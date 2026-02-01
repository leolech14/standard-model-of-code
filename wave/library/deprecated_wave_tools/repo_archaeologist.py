#!/usr/bin/env python3
"""
Repository Archaeologist
========================
Analyze the temporal evolution of a codebase with semantic understanding.

This tool:
1. Extracts file timestamps and groups files into time epochs
2. Runs incremental analysis on each epoch
3. Uses Gemini to understand semantic changes
4. Generates a timeline visualization of repository evolution

Usage:
  # Full analysis (can take hours for large archives)
  python repo_archaeologist.py --target archive/ --output evolution_report/

  # Resume from checkpoint
  python repo_archaeologist.py --target archive/ --resume

  # Quick preview (first 3 epochs only)
  python repo_archaeologist.py --target archive/ --preview

  # Specific time range
  python repo_archaeologist.py --target archive/ --from 2025-01-01 --to 2025-06-01
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json
import hashlib

# Auto-detect venv
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
TOOLS_VENV = PROJECT_ROOT / ".tools_venv"
VENV_PYTHON = TOOLS_VENV / "bin" / "python"

if TOOLS_VENV.as_posix() not in sys.prefix:
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    else:
        print("ERROR: .tools_venv not found. Run setup first.")
        sys.exit(1)

import argparse
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from google import genai


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FileRecord:
    """A file with its temporal metadata."""
    path: str
    created: datetime
    modified: datetime
    size: int
    extension: str

    def to_dict(self):
        return {
            'path': self.path,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'size': self.size,
            'extension': self.extension
        }


@dataclass
class Epoch:
    """A time period containing related files."""
    id: str
    start: datetime
    end: datetime
    files: List[FileRecord]
    summary: Optional[str] = None
    semantic_analysis: Optional[Dict] = None

    def to_dict(self):
        return {
            'id': self.id,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'file_count': len(self.files),
            'files': [f.to_dict() for f in self.files],
            'summary': self.summary,
            'semantic_analysis': self.semantic_analysis
        }


@dataclass
class Checkpoint:
    """Progress checkpoint for resumable analysis."""
    target_dir: str
    started_at: str
    last_epoch_completed: Optional[str]
    epochs_total: int
    epochs_completed: int

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# =============================================================================
# PHASE 1: TEMPORAL MAPPING
# =============================================================================

def extract_file_timestamps(target_dir: Path, exclude_patterns: List[str] = None) -> List[FileRecord]:
    """Extract timestamps from all files in directory."""
    exclude_patterns = exclude_patterns or [
        '__pycache__', '.git', 'node_modules', '.venv',
        '.DS_Store', '*.pyc', '*.pyo'
    ]

    records = []

    for root, dirs, files in os.walk(target_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if not any(
            d == pat or d.startswith(pat.rstrip('*'))
            for pat in exclude_patterns if not pat.startswith('*')
        )]

        for file in files:
            # Skip excluded files
            if any(file.endswith(pat.lstrip('*')) for pat in exclude_patterns if pat.startswith('*')):
                continue
            if file in exclude_patterns:
                continue

            file_path = Path(root) / file
            try:
                stat = file_path.stat()
                records.append(FileRecord(
                    path=str(file_path.relative_to(target_dir)),
                    created=datetime.fromtimestamp(stat.st_birthtime) if hasattr(stat, 'st_birthtime') else datetime.fromtimestamp(stat.st_mtime),
                    modified=datetime.fromtimestamp(stat.st_mtime),
                    size=stat.st_size,
                    extension=file_path.suffix.lower()
                ))
            except (OSError, ValueError) as e:
                print(f"  Warning: Could not read {file_path}: {e}")

    return records


def group_into_epochs(records: List[FileRecord], epoch_days: int = 7) -> List[Epoch]:
    """Group files into time-based epochs."""
    if not records:
        return []

    # Sort by modification time
    sorted_records = sorted(records, key=lambda r: r.modified)

    # Find time range
    earliest = sorted_records[0].modified
    latest = sorted_records[-1].modified

    # Create epochs
    epochs = []
    current_start = earliest
    epoch_num = 1

    while current_start < latest:
        current_end = current_start + timedelta(days=epoch_days)

        # Get files in this epoch
        epoch_files = [
            r for r in sorted_records
            if current_start <= r.modified < current_end
        ]

        if epoch_files:
            epochs.append(Epoch(
                id=f"epoch_{epoch_num:03d}",
                start=current_start,
                end=current_end,
                files=epoch_files
            ))
            epoch_num += 1

        current_start = current_end

    return epochs


# =============================================================================
# PHASE 2: SEMANTIC ANALYSIS
# =============================================================================

def create_gemini_client():
    """Create Gemini client using API key."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        print("Get key from: https://aistudio.google.com/apikey")
        return None
    return genai.Client(api_key=api_key)


def analyze_epoch_semantically(client, epoch: Epoch, previous_summary: str = None) -> Dict:
    """Use Gemini to understand what happened in this epoch."""

    # Build file inventory
    files_by_type = defaultdict(list)
    for f in epoch.files:
        files_by_type[f.extension].append(f.path)

    inventory = "\n".join([
        f"  {ext or '(no ext)'}: {len(files)} files"
        for ext, files in sorted(files_by_type.items(), key=lambda x: -len(x[1]))
    ])

    file_list = "\n".join([f"  - {f.path}" for f in epoch.files[:50]])
    if len(epoch.files) > 50:
        file_list += f"\n  ... and {len(epoch.files) - 50} more files"

    context = f"""
EPOCH: {epoch.id}
TIME PERIOD: {epoch.start.strftime('%Y-%m-%d')} to {epoch.end.strftime('%Y-%m-%d')}
FILE COUNT: {len(epoch.files)}

FILE TYPES:
{inventory}

FILES IN THIS EPOCH:
{file_list}
"""

    if previous_summary:
        context += f"\n\nPREVIOUS EPOCH SUMMARY:\n{previous_summary}"

    prompt = f"""Analyze this epoch from a repository's evolution. Based on the file names, types, and timing, determine:

1. ACTIVITY TYPE: What kind of work was happening? (e.g., "Initial setup", "Feature development", "Refactoring", "Documentation", "Bug fixes", "Archival/cleanup")

2. SEMANTIC THEME: What was the main focus? Give it a descriptive name.

3. KEY CHANGES: What significant files or patterns do you notice?

4. EVOLUTION NARRATIVE: One paragraph describing what was happening in this time period.

{context}

Respond in JSON format:
{{
  "activity_type": "...",
  "semantic_theme": "...",
  "key_changes": ["...", "..."],
  "narrative": "..."
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e), "activity_type": "unknown", "narrative": "Analysis failed"}


# =============================================================================
# PHASE 3: EVOLUTION SYNTHESIS
# =============================================================================

def generate_evolution_timeline(epochs: List[Epoch], output_dir: Path):
    """Generate HTML visualization of repository evolution."""

    html = """<!DOCTYPE html>
<html>
<head>
    <title>Repository Evolution Timeline</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            padding: 40px;
        }
        h1 {
            color: #00d4ff;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            color: #888;
            margin-bottom: 40px;
        }
        .timeline {
            position: relative;
            padding-left: 40px;
        }
        .timeline::before {
            content: '';
            position: absolute;
            left: 15px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(to bottom, #00d4ff, #ff00aa);
        }
        .epoch {
            position: relative;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .epoch::before {
            content: '';
            position: absolute;
            left: -33px;
            top: 25px;
            width: 12px;
            height: 12px;
            background: #00d4ff;
            border-radius: 50%;
            border: 3px solid #0a0a0f;
        }
        .epoch-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .epoch-id {
            color: #00d4ff;
            font-weight: 600;
        }
        .epoch-date {
            color: #888;
            font-size: 0.9em;
        }
        .epoch-theme {
            font-size: 1.3em;
            color: #fff;
            margin-bottom: 10px;
        }
        .epoch-type {
            display: inline-block;
            padding: 4px 12px;
            background: rgba(0, 212, 255, 0.2);
            color: #00d4ff;
            border-radius: 20px;
            font-size: 0.8em;
            margin-bottom: 15px;
        }
        .epoch-narrative {
            color: #aaa;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .epoch-stats {
            display: flex;
            gap: 20px;
            font-size: 0.85em;
            color: #666;
        }
        .stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .stat-value {
            color: #00d4ff;
            font-weight: 600;
        }
        .key-changes {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .key-changes h4 {
            color: #888;
            font-size: 0.8em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .key-changes ul {
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .key-changes li {
            background: rgba(255,255,255,0.05);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.85em;
            color: #aaa;
        }
        .summary {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
        }
        .summary h2 {
            color: #00d4ff;
            margin-bottom: 20px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .summary-stat {
            text-align: center;
        }
        .summary-stat .value {
            font-size: 2.5em;
            color: #00d4ff;
            font-weight: 700;
        }
        .summary-stat .label {
            color: #888;
        }
    </style>
</head>
<body>
    <h1>Repository Evolution</h1>
    <p class="subtitle">Semantic analysis of how this codebase evolved over time</p>
"""

    # Summary stats
    total_files = sum(len(e.files) for e in epochs)
    time_span = (epochs[-1].end - epochs[0].start).days if epochs else 0

    html += f"""
    <div class="summary">
        <h2>Overview</h2>
        <div class="summary-grid">
            <div class="summary-stat">
                <div class="value">{len(epochs)}</div>
                <div class="label">Epochs</div>
            </div>
            <div class="summary-stat">
                <div class="value">{total_files:,}</div>
                <div class="label">Files Analyzed</div>
            </div>
            <div class="summary-stat">
                <div class="value">{time_span}</div>
                <div class="label">Days Span</div>
            </div>
        </div>
    </div>

    <div class="timeline">
"""

    for epoch in epochs:
        analysis = epoch.semantic_analysis or {}
        html += f"""
        <div class="epoch">
            <div class="epoch-header">
                <span class="epoch-id">{epoch.id}</span>
                <span class="epoch-date">{epoch.start.strftime('%b %d, %Y')} - {epoch.end.strftime('%b %d, %Y')}</span>
            </div>
            <div class="epoch-theme">{analysis.get('semantic_theme', 'Unknown')}</div>
            <span class="epoch-type">{analysis.get('activity_type', 'Unknown')}</span>
            <p class="epoch-narrative">{analysis.get('narrative', 'No analysis available.')}</p>
            <div class="epoch-stats">
                <span class="stat"><span class="stat-value">{len(epoch.files)}</span> files</span>
            </div>
"""

        key_changes = analysis.get('key_changes', [])
        if key_changes:
            html += """
            <div class="key-changes">
                <h4>Key Changes</h4>
                <ul>
"""
            for change in key_changes[:5]:
                html += f"                    <li>{change}</li>\n"
            html += """
                </ul>
            </div>
"""

        html += "        </div>\n"

    html += """
    </div>
</body>
</html>
"""

    output_file = output_dir / "evolution_timeline.html"
    output_file.write_text(html)
    return output_file


def generate_evolution_json(epochs: List[Epoch], output_dir: Path):
    """Generate JSON data of evolution analysis."""
    data = {
        'generated_at': datetime.now().isoformat(),
        'total_epochs': len(epochs),
        'total_files': sum(len(e.files) for e in epochs),
        'time_range': {
            'start': epochs[0].start.isoformat() if epochs else None,
            'end': epochs[-1].end.isoformat() if epochs else None
        },
        'epochs': [e.to_dict() for e in epochs]
    }

    output_file = output_dir / "evolution_data.json"
    output_file.write_text(json.dumps(data, indent=2))
    return output_file


# =============================================================================
# CHECKPOINT MANAGEMENT
# =============================================================================

def save_checkpoint(checkpoint: Checkpoint, output_dir: Path):
    """Save progress checkpoint."""
    checkpoint_file = output_dir / ".checkpoint.json"
    checkpoint_file.write_text(json.dumps(checkpoint.to_dict(), indent=2))


def load_checkpoint(output_dir: Path) -> Optional[Checkpoint]:
    """Load existing checkpoint if available."""
    checkpoint_file = output_dir / ".checkpoint.json"
    if checkpoint_file.exists():
        data = json.loads(checkpoint_file.read_text())
        return Checkpoint.from_dict(data)
    return None


# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

def run_archaeology(
    target_dir: Path,
    output_dir: Path,
    epoch_days: int = 7,
    preview_only: bool = False,
    resume: bool = False,
    date_from: datetime = None,
    date_to: datetime = None
):
    """Run the full archaeological analysis."""

    print("=" * 60)
    print("REPOSITORY ARCHAEOLOGIST")
    print("=" * 60)
    print(f"Target: {target_dir}")
    print(f"Output: {output_dir}")
    print(f"Epoch size: {epoch_days} days")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Check for resume
    checkpoint = None
    if resume:
        checkpoint = load_checkpoint(output_dir)
        if checkpoint:
            print(f"Resuming from checkpoint: {checkpoint.epochs_completed}/{checkpoint.epochs_total} epochs done")

    # Phase 1: Temporal Mapping
    print("PHASE 1: Temporal Mapping")
    print("-" * 40)

    print("  Extracting file timestamps...")
    records = extract_file_timestamps(target_dir)
    print(f"  Found {len(records)} files")

    # Apply date filters
    if date_from:
        records = [r for r in records if r.modified >= date_from]
    if date_to:
        records = [r for r in records if r.modified <= date_to]

    if date_from or date_to:
        print(f"  After date filter: {len(records)} files")

    print("  Grouping into epochs...")
    epochs = group_into_epochs(records, epoch_days)
    print(f"  Created {len(epochs)} epochs")

    if preview_only:
        epochs = epochs[:3]
        print(f"  Preview mode: analyzing first 3 epochs only")

    print()

    # Phase 2: Semantic Analysis
    print("PHASE 2: Semantic Analysis")
    print("-" * 40)

    client = create_gemini_client()
    if not client:
        print("  Skipping semantic analysis (no API key)")
    else:
        start_idx = 0
        if checkpoint and checkpoint.last_epoch_completed:
            # Find where to resume
            for i, e in enumerate(epochs):
                if e.id == checkpoint.last_epoch_completed:
                    start_idx = i + 1
                    break

        previous_summary = None
        for i, epoch in enumerate(epochs[start_idx:], start=start_idx):
            print(f"  Analyzing {epoch.id} ({epoch.start.strftime('%Y-%m-%d')})...", end=" ", flush=True)

            try:
                analysis = analyze_epoch_semantically(client, epoch, previous_summary)
                epoch.semantic_analysis = analysis
                epoch.summary = analysis.get('narrative', '')
                previous_summary = epoch.summary
                print(f"OK - {analysis.get('activity_type', 'unknown')}")
            except Exception as e:
                print(f"FAILED: {e}")

            # Save checkpoint after each epoch
            save_checkpoint(Checkpoint(
                target_dir=str(target_dir),
                started_at=datetime.now().isoformat(),
                last_epoch_completed=epoch.id,
                epochs_total=len(epochs),
                epochs_completed=i + 1
            ), output_dir)

    print()

    # Phase 3: Evolution Synthesis
    print("PHASE 3: Evolution Synthesis")
    print("-" * 40)

    print("  Generating timeline visualization...")
    html_file = generate_evolution_timeline(epochs, output_dir)
    print(f"  Created: {html_file}")

    print("  Generating JSON data...")
    json_file = generate_evolution_json(epochs, output_dir)
    print(f"  Created: {json_file}")

    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"  Epochs analyzed: {len(epochs)}")
    print(f"  Files processed: {sum(len(e.files) for e in epochs)}")
    print(f"  Timeline: {html_file}")
    print(f"  Data: {json_file}")
    print()

    return epochs


def main():
    parser = argparse.ArgumentParser(
        description="Analyze repository evolution over time",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--target", "-t", default="archive", help="Directory to analyze")
    parser.add_argument("--output", "-o", default="evolution_report", help="Output directory")
    parser.add_argument("--epoch-days", type=int, default=7, help="Days per epoch (default: 7)")
    parser.add_argument("--preview", action="store_true", help="Preview mode (first 3 epochs)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_absolute():
        target = PROJECT_ROOT / target

    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / output

    date_from = datetime.strptime(args.date_from, "%Y-%m-%d") if args.date_from else None
    date_to = datetime.strptime(args.date_to, "%Y-%m-%d") if args.date_to else None

    run_archaeology(
        target_dir=target,
        output_dir=output,
        epoch_days=args.epoch_days,
        preview_only=args.preview,
        resume=args.resume,
        date_from=date_from,
        date_to=date_to
    )


if __name__ == "__main__":
    main()
