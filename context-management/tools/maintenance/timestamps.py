#!/usr/bin/env python3
"""
QUERY_TIMESTAMPS.PY
Utility for agents to query file timestamps intelligently.

Usage:
    python tools/query_timestamps.py recent 7           # Files created in last 7 days
    python tools/query_timestamps.py modified 1         # Files modified in last 1 day
    python tools/query_timestamps.py between 2026-01-15 2026-01-17  # Date range
    python tools/query_timestamps.py stale 30           # Not modified in 30+ days
    python tools/query_timestamps.py pattern "src/core" # Files matching path pattern
    python tools/query_timestamps.py summary            # Project timeline summary
    python tools/query_timestamps.py context            # LLM-ready context block

For AI agents: Use 'context' command to get a structured summary for your context window.
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
TIMESTAMPS_FILE = PROJECT_ROOT / "project_elements_file_timestamps.csv"


def load_timestamps():
    """Load and parse the timestamps CSV."""
    if not TIMESTAMPS_FILE.exists():
        print(f"Error: {TIMESTAMPS_FILE} not found. Run ./tools/update_timestamps.sh first.")
        sys.exit(1)

    files = []
    with open(TIMESTAMPS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['birth_dt'] = datetime.fromisoformat(row['birth_iso'])
            row['modified_dt'] = datetime.fromisoformat(row['modified_iso'])
            row['rel_path'] = row['path'].replace(str(PROJECT_ROOT) + '/', '')
            files.append(row)
    return files


def cmd_recent(days: int):
    """Files created in the last N days."""
    files = load_timestamps()
    cutoff = datetime.now() - timedelta(days=days)
    recent = [f for f in files if f['birth_dt'] > cutoff]
    recent.sort(key=lambda x: x['birth_dt'], reverse=True)

    print(f"# Files created in last {days} day(s): {len(recent)}\n")
    for f in recent[:50]:
        print(f"{f['birth_iso'][:10]}  {f['rel_path']}")
    if len(recent) > 50:
        print(f"\n... and {len(recent) - 50} more")


def cmd_modified(days: int):
    """Files modified in the last N days."""
    files = load_timestamps()
    cutoff = datetime.now() - timedelta(days=days)
    modified = [f for f in files if f['modified_dt'] > cutoff]
    modified.sort(key=lambda x: x['modified_dt'], reverse=True)

    print(f"# Files modified in last {days} day(s): {len(modified)}\n")
    for f in modified[:50]:
        print(f"{f['modified_iso'][:10]}  {f['rel_path']}")
    if len(modified) > 50:
        print(f"\n... and {len(modified) - 50} more")


def cmd_between(start_date: str, end_date: str):
    """Files created between two dates."""
    files = load_timestamps()
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date) + timedelta(days=1)  # Include end date

    between = [f for f in files if start <= f['birth_dt'] < end]
    between.sort(key=lambda x: x['birth_dt'])

    print(f"# Files created between {start_date} and {end_date}: {len(between)}\n")
    for f in between[:100]:
        print(f"{f['birth_iso'][:10]}  {f['rel_path']}")
    if len(between) > 100:
        print(f"\n... and {len(between) - 100} more")


def cmd_stale(days: int):
    """Files not modified in N+ days (excluding archives)."""
    files = load_timestamps()
    cutoff = datetime.now() - timedelta(days=days)

    stale = [f for f in files
             if f['modified_dt'] < cutoff
             and '/archive/' not in f['path']
             and '/.archive/' not in f['path']
             and '/node_modules/' not in f['path']
             and f['rel_path'].endswith(('.py', '.md', '.json', '.ts', '.js'))]
    stale.sort(key=lambda x: x['modified_dt'])

    print(f"# Files not modified in {days}+ days (excluding archives): {len(stale)}\n")
    for f in stale[:50]:
        print(f"{f['modified_iso'][:10]}  {f['rel_path']}")
    if len(stale) > 50:
        print(f"\n... and {len(stale) - 50} more")


def cmd_pattern(pattern: str):
    """Files matching a path pattern."""
    files = load_timestamps()
    matches = [f for f in files if pattern in f['path']]
    matches.sort(key=lambda x: x['birth_dt'], reverse=True)

    print(f"# Files matching '{pattern}': {len(matches)}\n")
    for f in matches[:50]:
        print(f"{f['birth_iso'][:10]}  {f['rel_path']}")
    if len(matches) > 50:
        print(f"\n... and {len(matches) - 50} more")


def cmd_summary():
    """Project timeline summary."""
    files = load_timestamps()

    # Exclude non-project files
    project_files = [f for f in files
                     if not any(x in f['path'] for x in ['/archive/', '/.archive/', '.DS_Store'])]

    # Group by date
    by_date = defaultdict(int)
    for f in files:
        by_date[f['birth_iso'][:10]] += 1

    # Find key dates
    sorted_dates = sorted(by_date.items())
    first_date = sorted_dates[0][0] if sorted_dates else "unknown"
    last_date = sorted_dates[-1][0] if sorted_dates else "unknown"
    peak_date = max(by_date.items(), key=lambda x: x[1]) if by_date else ("unknown", 0)

    # Recent activity
    week_ago = datetime.now() - timedelta(days=7)
    recent_count = len([f for f in files if f['birth_dt'] > week_ago])

    print("# PROJECT TIMELINE SUMMARY\n")
    print(f"Total files tracked: {len(files)}")
    print(f"Project files (excl. archives): {len(project_files)}")
    print(f"First file created: {first_date}")
    print(f"Most recent file: {last_date}")
    print(f"Peak activity day: {peak_date[0]} ({peak_date[1]} files)")
    print(f"Files created in last 7 days: {recent_count}")
    print(f"\n## Activity by Month:\n")

    by_month = defaultdict(int)
    for date, count in sorted_dates:
        by_month[date[:7]] += count
    for month, count in sorted(by_month.items()):
        bar = '█' * (count // 20)
        print(f"{month}: {bar} {count}")


def cmd_context():
    """Generate LLM-ready context block."""
    files = load_timestamps()

    week_ago = datetime.now() - timedelta(days=7)
    day_ago = datetime.now() - timedelta(days=1)

    recent_created = [f for f in files if f['birth_dt'] > week_ago]
    recent_modified = [f for f in files if f['modified_dt'] > day_ago]

    # Focus areas (most active directories in last 7 days)
    dir_activity = defaultdict(int)
    for f in recent_created:
        parts = f['rel_path'].split('/')
        if len(parts) > 1:
            dir_activity['/'.join(parts[:2])] += 1

    top_dirs = sorted(dir_activity.items(), key=lambda x: x[1], reverse=True)[:5]

    print("<!-- TIMESTAMP CONTEXT FOR AI AGENT -->")
    print("<project_timeline>")
    print(f"  <total_files>{len(files)}</total_files>")
    print(f"  <project_birth>2025-12-03</project_birth>")
    print(f"  <project_age_days>{(datetime.now() - datetime(2025, 12, 3)).days}</project_age_days>")
    print(f"  <files_created_last_7_days>{len(recent_created)}</files_created_last_7_days>")
    print(f"  <files_modified_last_24h>{len(recent_modified)}</files_modified_last_24h>")
    print("  <active_areas>")
    for dir_path, count in top_dirs:
        print(f"    <area path=\"{dir_path}\" recent_files=\"{count}\"/>")
    print("  </active_areas>")
    print("  <recent_files>")
    for f in sorted(recent_created, key=lambda x: x['birth_dt'], reverse=True)[:10]:
        print(f"    <file created=\"{f['birth_iso'][:10]}\">{f['rel_path']}</file>")
    print("  </recent_files>")
    print("</project_timeline>")
    print("<!-- END TIMESTAMP CONTEXT -->")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "recent":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cmd_recent(days)
    elif cmd == "modified":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        cmd_modified(days)
    elif cmd == "between":
        if len(sys.argv) < 4:
            print("Usage: query_timestamps.py between START_DATE END_DATE")
            sys.exit(1)
        cmd_between(sys.argv[2], sys.argv[3])
    elif cmd == "stale":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cmd_stale(days)
    elif cmd == "pattern":
        if len(sys.argv) < 3:
            print("Usage: query_timestamps.py pattern PATTERN")
            sys.exit(1)
        cmd_pattern(sys.argv[2])
    elif cmd == "summary":
        cmd_summary()
    elif cmd == "context":
        cmd_context()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
