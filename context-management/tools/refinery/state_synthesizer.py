#!/usr/bin/env python3
"""
State Synthesizer
==================
Produces the global state/live.yaml map from all refinery outputs.
This is the "single source of truth" for the current corpus state.

Output: context-management/intelligence/state/live.yaml

Usage:
    python state_synthesizer.py                  # Generate live state
    python state_synthesizer.py --format json    # JSON output instead
"""
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INTELLIGENCE_DIR = PROJECT_ROOT / "context-management/intelligence"
STATE_DIR = INTELLIGENCE_DIR / "state"

# Input files
CORPUS_INVENTORY_PATH = INTELLIGENCE_DIR / "corpus_inventory.json"
BOUNDARIES_PATH = INTELLIGENCE_DIR / "boundaries.json"
DELTA_REPORT_PATH = INTELLIGENCE_DIR / "delta_report.json"
ATOMS_DIR = INTELLIGENCE_DIR / "atoms"

# ============================================================================
# STATE SYNTHESIS
# ============================================================================

def load_if_exists(path: Path) -> Dict[str, Any]:
    """Load JSON file if it exists, return empty dict otherwise."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def count_unique_files(boundaries_data: Dict[str, Any]) -> Optional[int]:
    """
    Count unique files across all boundaries (accounting for overlap).

    NOTE: This uses the "contains" relationship which may be truncated
    for large boundaries. For more accurate count, we'd need to expand
    all patterns again, but that's expensive. This gives a rough estimate.
    """
    all_files = set()
    for boundary in boundaries_data.get("boundaries", []):
        # Each boundary has a "contains" relationship list (may be truncated)
        files = boundary.get("relationships", {}).get("contains", [])
        all_files.update(files)

    # If we got very few unique files but high total_mapped, the contains
    # lists are likely truncated - return None to signal unreliable data
    if len(all_files) < 1000 and boundaries_data.get("summary", {}).get("total_files_mapped", 0) > 5000:
        return None

    return len(all_files)


def calculate_overlap_factor(boundaries_data: Dict[str, Any], corpus_data: Dict[str, Any]) -> Any:
    """
    Calculate overlap factor (average boundaries per file).

    overlap_factor = total_files_mapped / unique_files
    1.0 = no overlap (each file in exactly one boundary)
    2.0 = average file appears in 2 boundaries

    Returns None if data is unreliable (truncated contains lists).
    """
    total_mapped = boundaries_data.get("summary", {}).get("total_files_mapped", 0)
    unique = count_unique_files(boundaries_data)

    if unique is None:
        return None  # Unreliable data

    if unique == 0:
        return 0.0

    return round(total_mapped / unique, 2)


def synthesize_state() -> Dict[str, Any]:
    """
    Synthesize global state from all refinery outputs.

    Returns the complete state representation of the corpus.
    """
    now = datetime.now().isoformat()

    # Load all sources
    corpus = load_if_exists(CORPUS_INVENTORY_PATH)
    boundaries = load_if_exists(BOUNDARIES_PATH)
    delta = load_if_exists(DELTA_REPORT_PATH)

    # Load all atom files
    atoms_summary = {"total": 0, "by_boundary": {}, "files": []}
    if ATOMS_DIR.exists():
        for atom_file in ATOMS_DIR.glob("atoms_*.json"):
            with open(atom_file, 'r') as f:
                atom_data = json.load(f)
            count = atom_data.get("summary", {}).get("atoms_generated", 0)
            boundary = atom_data.get("meta", {}).get("boundary", "all")
            atoms_summary["total"] += count
            atoms_summary["by_boundary"][boundary or "all"] = count
            atoms_summary["files"].append(str(atom_file.name))

    # Build state
    state = {
        # Meta
        "version": "1.0.0",
        "synthesized_at": now,
        "project_root": str(PROJECT_ROOT),

        # Corpus summary
        "corpus": {
            "total_files": corpus.get("summary", {}).get("total_files", 0),
            "total_bytes": corpus.get("summary", {}).get("total_bytes", 0),
            "total_lines": corpus.get("summary", {}).get("total_lines", 0),
            "languages": list(corpus.get("by_language", {}).keys()),
            "categories": list(corpus.get("by_category", {}).keys()),
            "last_scan": corpus.get("meta", {}).get("scanned_at")
        },

        # Boundaries summary
        "boundaries": {
            "count": len(boundaries.get("boundaries", [])),
            "names": [b["region_name"] for b in boundaries.get("boundaries", [])],
            "total_files_mapped": boundaries.get("summary", {}).get("total_files_mapped", 0),
            "unique_files": count_unique_files(boundaries),
            "overlap_factor": calculate_overlap_factor(boundaries, corpus),
            "last_mapped": boundaries.get("meta", {}).get("mapped_at")
        },

        # Delta status
        "delta": {
            "has_changes": delta.get("summary", {}).get("has_changes", False),
            "added": delta.get("summary", {}).get("added", 0),
            "modified": delta.get("summary", {}).get("modified", 0),
            "deleted": delta.get("summary", {}).get("deleted", 0),
            "last_detected": delta.get("meta", {}).get("detected_at")
        },

        # Atoms summary
        "atoms": {
            "total": atoms_summary["total"],
            "by_boundary": atoms_summary["by_boundary"],
            "atom_files": atoms_summary["files"]
        },

        # Health indicators
        "health": {
            "corpus_fresh": is_recent(corpus.get("meta", {}).get("scanned_at")),
            "boundaries_fresh": is_recent(boundaries.get("meta", {}).get("mapped_at")),
            "delta_fresh": is_recent(delta.get("meta", {}).get("detected_at")),
            "all_tools_ran": all([
                corpus.get("summary", {}).get("total_files", 0) > 0,
                len(boundaries.get("boundaries", [])) > 0
            ])
        },

        # Quick stats for AI consumption
        "quick_stats": {
            "files": corpus.get("summary", {}).get("total_files", 0),
            "boundaries": len(boundaries.get("boundaries", [])),
            "atoms": atoms_summary["total"],
            "pending_changes": delta.get("summary", {}).get("added", 0) + delta.get("summary", {}).get("modified", 0)
        }
    }

    return state


def is_recent(timestamp_str: str, hours: int = 24) -> bool:
    """Check if a timestamp is within the last N hours."""
    if not timestamp_str:
        return False
    try:
        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(ts.tzinfo) if ts.tzinfo else datetime.now()
        delta = now - ts
        return delta.total_seconds() < (hours * 3600)
    except Exception:
        return False


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="State Synthesizer - Generate global state/live.yaml"
    )
    parser.add_argument("--format", choices=["yaml", "json"], default="yaml",
                        help="Output format (default: yaml)")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output path")

    args = parser.parse_args()

    # Synthesize
    print("Synthesizing global state...")
    state = synthesize_state()

    # Determine output
    if args.output:
        output_path = Path(args.output)
    else:
        ext = "yaml" if args.format == "yaml" else "json"
        output_path = STATE_DIR / f"live.{ext}"

    # Write
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "yaml":
        with open(output_path, 'w') as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=False)
    else:
        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)

    # Summary
    print(f"\nState Synthesis Complete:")
    print(f"  Files:       {state['quick_stats']['files']}")
    print(f"  Boundaries:  {state['quick_stats']['boundaries']}")
    print(f"  Atoms:       {state['quick_stats']['atoms']}")
    print(f"  Changes:     {state['quick_stats']['pending_changes']} pending")
    print(f"  Health:      {'All fresh' if state['health']['all_tools_ran'] else 'Needs refresh'}")
    print(f"  Output:      {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
