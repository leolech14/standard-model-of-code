#!/usr/bin/env python3
"""
Refinery Report - Activity Summary & Knowledge Library
=======================================================

Shows:
1. What Refinery did while you were away
2. Organized library view of consolidated knowledge
3. Recent changes to chunks
4. Health metrics for knowledge base

Usage:
    python refinery_report.py              # Full report
    python refinery_report.py --summary    # Quick summary
    python refinery_report.py --library    # Knowledge library view
    python refinery_report.py --changes    # Recent changes only
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CHUNKS_DIR = PROJECT_ROOT / ".agent" / "intelligence" / "chunks"
WATCHER_LOG = PROJECT_ROOT / ".agent" / "intelligence" / "filesystem_watcher.log"


def load_metadata() -> Dict[str, Any]:
    """Load chunk generation metadata."""
    metadata_file = CHUNKS_DIR / "metadata.json"
    if not metadata_file.exists():
        return {}

    with open(metadata_file) as f:
        return json.load(f)


def load_chunks(chunk_file: str) -> List[Dict[str, Any]]:
    """Load chunks from JSON file."""
    path = CHUNKS_DIR / chunk_file
    if not path.exists():
        return []

    with open(path) as f:
        data = json.load(f)
        return data.get("nodes", [])


def get_watcher_activity() -> List[str]:
    """Parse watcher log for recent activity."""
    if not WATCHER_LOG.exists():
        return []

    try:
        with open(WATCHER_LOG) as f:
            lines = f.readlines()
            # Get last 50 lines
            return lines[-50:] if len(lines) > 50 else lines
    except Exception:
        return []


def format_time_ago(iso_str: str) -> str:
    """Format ISO timestamp as 'X hours ago'."""
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now()
        delta = now - dt

        if delta.total_seconds() < 60:
            return f"{int(delta.total_seconds())}s ago"
        elif delta.total_seconds() < 3600:
            return f"{int(delta.total_seconds() / 60)}min ago"
        elif delta.total_seconds() < 86400:
            return f"{int(delta.total_seconds() / 3600)}h ago"
        else:
            return f"{int(delta.total_seconds() / 86400)}d ago"
    except Exception:
        return iso_str


def print_summary_report():
    """Print quick summary of current state."""
    metadata = load_metadata()

    if not metadata:
        print("No refinery metadata found. Run: ./pe wire")
        return

    print("=" * 70)
    print("REFINERY STATUS")
    print("=" * 70)
    print()

    # Freshness
    timestamp = metadata.get("timestamp", "unknown")
    age = format_time_ago(timestamp) if timestamp != "unknown" else "unknown"
    git_sha = metadata.get("git_sha", "unknown")[:8]

    print(f"  Last Updated: {age}")
    print(f"  Git SHA: {git_sha}")
    print()

    # Chunk stats
    chunks = metadata.get("chunks", {})
    total_chunks = metadata.get("total_chunks", 0)
    total_tokens = metadata.get("total_tokens", 0)

    print(f"  Total Chunks: {total_chunks:,}")
    print(f"  Total Tokens: {total_tokens:,}")
    print()

    print("  Breakdown:")
    for name, stats in chunks.items():
        chunk_count = stats.get("chunks", 0)
        token_count = stats.get("tokens", 0)
        pct = (chunk_count / total_chunks * 100) if total_chunks > 0 else 0
        bar = "█" * int(pct / 3)
        print(f"    {name:8} {chunk_count:>5} chunks ({pct:>5.1f}%) {bar}")
        print(f"             {token_count:>7,} tokens")

    print()
    print("=" * 70)


def print_library_view():
    """Print organized library view of all knowledge."""
    print("=" * 70)
    print("REFINERY KNOWLEDGE LIBRARY")
    print("=" * 70)
    print()

    # Load all chunks
    all_chunks = []
    for chunk_file in ["agent_chunks.json", "core_chunks.json", "aci_chunks.json"]:
        chunks = load_chunks(chunk_file)
        for chunk in chunks:
            chunk["source_module"] = chunk_file.replace("_chunks.json", "")
            all_chunks.append(chunk)

    if not all_chunks:
        print("No chunks found. Run: ./pe wire")
        return

    # Organize by source file
    by_file = defaultdict(list)
    for chunk in all_chunks:
        source = Path(chunk.get("source_file", "unknown"))
        # Get relative path
        try:
            rel_path = str(source.relative_to(PROJECT_ROOT))
        except ValueError:
            rel_path = str(source)

        by_file[rel_path].append(chunk)

    # Sort files by chunk count
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)

    # Show top 20 files
    print(f"Top 20 Files by Chunk Count (of {len(sorted_files)} total):")
    print()

    for i, (filepath, chunks) in enumerate(sorted_files[:20], 1):
        chunk_count = len(chunks)
        total_tokens = sum(c.get("metadata", {}).get("token_estimate", 0) or
                          len(c.get("content", "")) // 4 for c in chunks)

        # Get chunk types
        types = defaultdict(int)
        for c in chunks:
            types[c.get("chunk_type", "unknown")] += 1

        type_summary = ", ".join(f"{count} {t}" for t, count in sorted(types.items())[:3])

        print(f"  {i:2}. {filepath}")
        print(f"      Chunks: {chunk_count} | Tokens: ~{total_tokens:,}")
        print(f"      Types: {type_summary}")
        print()

    print()
    print(f"Total: {len(all_chunks):,} chunks across {len(sorted_files)} files")
    print()
    print("To search: ./pe refinery search <query>")
    print("=" * 70)


def print_changes_report():
    """Show what changed recently."""
    print("=" * 70)
    print("REFINERY RECENT ACTIVITY")
    print("=" * 70)
    print()

    # Get watcher activity
    activity = get_watcher_activity()

    if not activity:
        print("No watcher activity logged.")
        print()
        print("Watcher may not be running. Start with:")
        print("  screen -dmS watcher python3 .agent/tools/filesystem_watcher.py")
        return

    print("Last 10 events from filesystem watcher:")
    print()

    # Parse and display
    for line in activity[-10:]:
        line = line.strip()
        if line:
            print(f"  {line}")

    print()

    # Check metadata age
    metadata = load_metadata()
    if metadata:
        timestamp = metadata.get("timestamp")
        if timestamp:
            age = format_time_ago(timestamp)
            print(f"Last chunk regeneration: {age}")
            print(f"Git SHA: {metadata.get('git_sha', 'unknown')[:8]}")

    print()
    print("=" * 70)


def print_full_report():
    """Print complete refinery report."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "REFINERY ACTIVITY REPORT" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # Section 1: Current Status
    metadata = load_metadata()

    if metadata:
        timestamp = metadata.get("timestamp", "unknown")
        age = format_time_ago(timestamp)
        git_sha = metadata.get("git_sha", "unknown")[:8]

        print("## CURRENT STATUS")
        print(f"  Last Updated: {age} (Git SHA: {git_sha})")
        print(f"  Total Chunks: {metadata.get('total_chunks', 0):,}")
        print(f"  Total Tokens: {metadata.get('total_tokens', 0):,}")
        print()

    # Section 2: What Happened While You Were Away
    print("## ACTIVITY LOG (Recent)")
    activity = get_watcher_activity()

    if activity:
        # Count wire runs
        wire_runs = [l for l in activity if "running wire" in l.lower() or "wire completed" in l.lower()]
        file_changes = [l for l in activity if "changes detected" in l.lower()]

        print(f"  File changes detected: {len(file_changes)}")
        print(f"  Wire pipeline runs: {len(wire_runs)}")
        print()

        if wire_runs:
            print("  Last 3 wire runs:")
            for line in wire_runs[-3:]:
                print(f"    {line.strip()}")
            print()
    else:
        print("  No activity logged (watcher may not be running)")
        print()

    # Section 3: Knowledge Library Summary
    print("## KNOWLEDGE LIBRARY")

    all_chunks = []
    for chunk_file in ["agent_chunks.json", "core_chunks.json", "aci_chunks.json"]:
        chunks = load_chunks(chunk_file)
        all_chunks.extend(chunks)

    if all_chunks:
        # Count by type
        by_type = defaultdict(int)
        for chunk in all_chunks:
            by_type[chunk.get("chunk_type", "unknown")] += 1

        print(f"  Total entries: {len(all_chunks):,}")
        print()
        print("  By chunk type:")
        for chunk_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]:
            pct = count / len(all_chunks) * 100
            print(f"    {chunk_type:20} {count:>5} ({pct:>5.1f}%)")

    print()
    print("## COMMANDS")
    print("  ./pe refinery search <query>   # Search knowledge")
    print("  ./pe refinery stats            # Corpus statistics")
    print("  ./pe refinery chunks           # Chunk metadata")
    print("  ./pe refinery library          # Full library view")
    print()
    print("╚" + "═" * 68 + "╝")
    print()


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Refinery Activity Report & Knowledge Library")
    parser.add_argument("--summary", action="store_true", help="Quick summary only")
    parser.add_argument("--library", action="store_true", help="Knowledge library view")
    parser.add_argument("--changes", action="store_true", help="Recent changes only")

    args = parser.parse_args()

    if args.summary:
        print_summary_report()
    elif args.library:
        print_library_view()
    elif args.changes:
        print_changes_report()
    else:
        print_full_report()


if __name__ == "__main__":
    main()
