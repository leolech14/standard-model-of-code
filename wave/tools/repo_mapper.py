#!/usr/bin/env python3
"""
Repository Mapper - Complete tree analysis before AI processing.

Phase 1: Map (FREE - no API calls)
  - Full directory tree
  - File metadata (size, mtime, extension)
  - Pattern detection from paths/names

Phase 2: Plan (FREE - local analysis)
  - Group files by type/purpose
  - Estimate processing costs
  - Prioritize by value

Phase 3: Execute (PAID - Cerebras batch)
  - Process groups in order
  - Rate-limit aware
  - Checkpoint progress

Usage:
    python repo_mapper.py map                    # Generate tree + metadata
    python repo_mapper.py analyze                # Analyze patterns
    python repo_mapper.py plan                   # Create processing plan
    python repo_mapper.py plan --execute         # Run the plan with Cerebras
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Optional
import hashlib

PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "wave" / "data" / "repo_map"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Skip patterns
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tools_venv", "dist", "build", ".egg-info", ".collider",
    ".next", ".cache", ".pytest_cache", ".mypy_cache",
    # Skip large output/artifact directories
    "artifacts", "archive", "large_outputs", "runs",
    ".archive", "legacy_experiments", "orphaned_tools_2025"
}

SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".dll",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".ttf", ".woff", ".woff2", ".eot",
    ".lock", ".DS_Store"
}

# File type categories
FILE_CATEGORIES = {
    "code_python": {".py"},
    "code_js": {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"},
    "code_other": {".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".rb", ".php"},
    "config": {".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".cfg"},
    "docs": {".md", ".rst", ".txt", ".adoc"},
    "web": {".html", ".htm", ".css", ".scss", ".sass", ".less"},
    "data": {".csv", ".tsv", ".xml", ".sql"},
    "shell": {".sh", ".bash", ".zsh", ".fish"},
    "other": set()
}


@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    size_bytes: int
    modified: str
    depth: int
    category: str
    parent_dir: str


def get_category(ext: str) -> str:
    """Determine file category from extension."""
    ext = ext.lower()
    for cat, exts in FILE_CATEGORIES.items():
        if ext in exts:
            return cat
    return "other"


def scan_repository() -> list[FileInfo]:
    """Scan entire repository and collect file metadata."""
    files = []

    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        rel_root = Path(root).relative_to(PROJECT_ROOT)
        depth = len(rel_root.parts)

        for filename in filenames:
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()

            # Skip binary/media files
            if ext in SKIP_EXTENSIONS:
                continue

            # Skip hidden files (except important ones)
            if filename.startswith(".") and filename not in {".env.example", ".gitignore", ".prettierrc"}:
                continue

            # Skip files > 100KB (likely generated/data, not source)
            try:
                if filepath.stat().st_size > 100 * 1024:
                    continue
            except OSError:
                continue

            try:
                stat = filepath.stat()
                files.append(FileInfo(
                    path=str(filepath.relative_to(PROJECT_ROOT)),
                    name=filename,
                    extension=ext,
                    size_bytes=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    depth=depth,
                    category=get_category(ext),
                    parent_dir=str(rel_root)
                ))
            except (OSError, PermissionError):
                continue

    return files


def analyze_patterns(files: list[FileInfo]) -> dict:
    """Analyze patterns in the file tree."""

    # Group by category
    by_category = defaultdict(list)
    for f in files:
        by_category[f.category].append(f)

    # Group by top-level directory
    by_toplevel = defaultdict(list)
    for f in files:
        parts = f.path.split("/")
        toplevel = parts[0] if len(parts) > 1 else "root"
        by_toplevel[toplevel].append(f)

    # Group by depth
    by_depth = defaultdict(list)
    for f in files:
        by_depth[f.depth].append(f)

    # Size distribution
    total_size = sum(f.size_bytes for f in files)
    size_by_category = {
        cat: sum(f.size_bytes for f in fs)
        for cat, fs in by_category.items()
    }

    # Extension frequency
    ext_counts = defaultdict(int)
    for f in files:
        ext_counts[f.extension] += 1

    # Directory patterns (look for common structures)
    dir_patterns = defaultdict(int)
    for f in files:
        parts = f.parent_dir.split("/")
        for part in parts:
            if part:
                dir_patterns[part] += 1

    return {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "by_category": {k: len(v) for k, v in by_category.items()},
        "by_toplevel": {k: len(v) for k, v in sorted(by_toplevel.items(), key=lambda x: -len(x[1]))[:20]},
        "by_depth": {k: len(v) for k, v in sorted(by_depth.items())},
        "size_by_category_mb": {k: round(v/1024/1024, 2) for k, v in size_by_category.items()},
        "top_extensions": dict(sorted(ext_counts.items(), key=lambda x: -x[1])[:20]),
        "common_dirs": dict(sorted(dir_patterns.items(), key=lambda x: -x[1])[:30])
    }


def create_processing_plan(files: list[FileInfo], analysis: dict) -> dict:
    """Create a prioritized processing plan for Cerebras."""

    # Estimate tokens per file (rough: 1 token per 4 chars, avg file ~500 lines ~10KB)
    def estimate_tokens(f: FileInfo) -> int:
        return max(100, f.size_bytes // 4)

    # Group files into processing batches
    batches = []

    # Priority 1: Python code (most valuable for Standard Model)
    python_files = [f for f in files if f.category == "code_python"]
    if python_files:
        tokens = sum(estimate_tokens(f) for f in python_files)
        batches.append({
            "name": "python_code",
            "priority": 1,
            "files": len(python_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),  # $0.60/M
            "estimated_time_min": round(len(python_files) * 2.5 / 60, 1),  # ~2.5s per file with rate limits
            "task": "D1-D8 classification + docstring extraction"
        })

    # Priority 2: Config files (understand project structure)
    config_files = [f for f in files if f.category == "config"]
    if config_files:
        tokens = sum(estimate_tokens(f) for f in config_files)
        batches.append({
            "name": "config_files",
            "priority": 2,
            "files": len(config_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),
            "estimated_time_min": round(len(config_files) * 2.5 / 60, 1),
            "task": "Purpose extraction + dependency mapping"
        })

    # Priority 3: Documentation (already human-readable, lower value)
    doc_files = [f for f in files if f.category == "docs"]
    if doc_files:
        tokens = sum(estimate_tokens(f) for f in doc_files)
        batches.append({
            "name": "documentation",
            "priority": 3,
            "files": len(doc_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),
            "estimated_time_min": round(len(doc_files) * 2.5 / 60, 1),
            "task": "Summary extraction + topic tagging"
        })

    # Priority 4: JavaScript/TypeScript
    js_files = [f for f in files if f.category == "code_js"]
    if js_files:
        tokens = sum(estimate_tokens(f) for f in js_files)
        batches.append({
            "name": "javascript_code",
            "priority": 4,
            "files": len(js_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),
            "estimated_time_min": round(len(js_files) * 2.5 / 60, 1),
            "task": "Component classification + export mapping"
        })

    # Priority 5: Shell scripts
    shell_files = [f for f in files if f.category == "shell"]
    if shell_files:
        tokens = sum(estimate_tokens(f) for f in shell_files)
        batches.append({
            "name": "shell_scripts",
            "priority": 5,
            "files": len(shell_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),
            "estimated_time_min": round(len(shell_files) * 2.5 / 60, 1),
            "task": "Purpose + command extraction"
        })

    # Priority 6: Web files
    web_files = [f for f in files if f.category == "web"]
    if web_files:
        tokens = sum(estimate_tokens(f) for f in web_files)
        batches.append({
            "name": "web_files",
            "priority": 6,
            "files": len(web_files),
            "estimated_tokens": tokens,
            "estimated_cost_usd": round(tokens * 0.6 / 1_000_000, 2),
            "estimated_time_min": round(len(web_files) * 2.5 / 60, 1),
            "task": "Component identification"
        })

    # Totals
    total_files = sum(b["files"] for b in batches)
    total_tokens = sum(b["estimated_tokens"] for b in batches)
    total_cost = sum(b["estimated_cost_usd"] for b in batches)
    total_time = sum(b["estimated_time_min"] for b in batches)

    return {
        "created_at": datetime.now().isoformat(),
        "summary": {
            "total_files": total_files,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 2),
            "total_time_min": round(total_time, 1),
            "rate_limit_note": "Cerebras: 3000 req/min, but burst limited to ~30/sec"
        },
        "batches": batches,
        "execution_order": [b["name"] for b in batches]
    }


def cmd_map(args):
    """Generate complete repository map."""
    print("Scanning repository...")
    files = scan_repository()

    # Save raw file list
    output = {
        "created_at": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "total_files": len(files),
        "files": [asdict(f) for f in files]
    }

    output_file = OUTPUT_DIR / f"repo_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    latest_file = OUTPUT_DIR / "repo_map_latest.json"

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    with open(latest_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Mapped {len(files)} files")
    print(f"Output: {output_file}")

    # Quick summary
    by_cat = defaultdict(int)
    for f in files:
        by_cat[f.category] += 1

    print("\nBy category:")
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat:15} {count:5}")


def cmd_analyze(args):
    """Analyze patterns in the repository."""
    # Load latest map
    latest_file = OUTPUT_DIR / "repo_map_latest.json"
    if not latest_file.exists():
        print("No map found. Run 'map' first.")
        return

    with open(latest_file) as f:
        data = json.load(f)

    files = [FileInfo(**f) for f in data["files"]]
    analysis = analyze_patterns(files)

    # Save analysis
    output_file = OUTPUT_DIR / "analysis_latest.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)

    # Print summary
    print(f"Repository Analysis")
    print(f"==================")
    print(f"Total files: {analysis['total_files']}")
    print(f"Total size: {analysis['total_size_mb']} MB")
    print()

    print("By Category:")
    for cat, count in sorted(analysis["by_category"].items(), key=lambda x: -x[1]):
        size = analysis["size_by_category_mb"].get(cat, 0)
        print(f"  {cat:15} {count:5} files  ({size:.1f} MB)")
    print()

    print("Top-Level Directories:")
    for dir_name, count in list(analysis["by_toplevel"].items())[:10]:
        print(f"  {dir_name:30} {count:5} files")
    print()

    print("Top Extensions:")
    for ext, count in list(analysis["top_extensions"].items())[:10]:
        ext_display = ext if ext else "(no ext)"
        print(f"  {ext_display:10} {count:5}")


def cmd_plan(args):
    """Create processing plan for Cerebras."""
    # Load latest map
    latest_file = OUTPUT_DIR / "repo_map_latest.json"
    if not latest_file.exists():
        print("No map found. Run 'map' first.")
        return

    with open(latest_file) as f:
        data = json.load(f)

    files = [FileInfo(**f) for f in data["files"]]
    analysis = analyze_patterns(files)
    plan = create_processing_plan(files, analysis)

    # Save plan
    output_file = OUTPUT_DIR / "processing_plan.json"
    with open(output_file, 'w') as f:
        json.dump(plan, f, indent=2)

    # Print plan
    print("Cerebras Processing Plan")
    print("========================")
    print()
    print(f"Total: {plan['summary']['total_files']} files")
    print(f"Tokens: ~{plan['summary']['total_tokens']:,}")
    print(f"Cost: ${plan['summary']['total_cost_usd']:.2f}")
    print(f"Time: ~{plan['summary']['total_time_min']:.0f} minutes")
    print()

    print("Execution Order:")
    print("-" * 70)
    for batch in plan["batches"]:
        print(f"[{batch['priority']}] {batch['name']:20} | {batch['files']:4} files | ${batch['estimated_cost_usd']:.2f} | {batch['estimated_time_min']:.0f}min")
        print(f"    Task: {batch['task']}")
    print("-" * 70)

    print(f"\nPlan saved: {output_file}")

    if args.execute:
        print("\n--execute flag detected. Starting batch processing...")
        # TODO: Integrate with cerebras_tagger.py
        print("(Execution not yet implemented - use cerebras_tagger.py directly)")


def main():
    parser = argparse.ArgumentParser(description="Repository Mapper")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Map command
    subparsers.add_parser("map", help="Scan and map repository")

    # Analyze command
    subparsers.add_parser("analyze", help="Analyze patterns")

    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Create processing plan")
    plan_parser.add_argument("--execute", action="store_true", help="Execute the plan")

    args = parser.parse_args()

    if args.command == "map":
        cmd_map(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "plan":
        cmd_plan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
