#!/usr/bin/env python3
"""
DevJournal CLI — run the full ingestion pipeline.

Usage:
    python run.py                    # Today
    python run.py 2026-03-16         # Specific date
    python run.py --range 3          # Last 3 days
    python run.py --materialize-only # Re-materialize from existing ledger
"""

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))

from compiler import compile_day
from materializer import materialize_day
from schema import DEVJOURNAL_DIR, DAYS_DIR, LEDGER_PATH


def main():
    parser = argparse.ArgumentParser(description="DevJournal — Refinery ingestion pipeline")
    parser.add_argument("date", nargs="?", default=None, help="Target date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--range", type=int, default=1, help="Number of days to process (backwards from date).")
    parser.add_argument("--materialize-only", action="store_true", help="Skip collectors, re-materialize from ledger.")
    parser.add_argument("--quiet", action="store_true", help="Suppress output.")
    args = parser.parse_args()

    verbose = not args.quiet
    target = args.date or date.today().isoformat()

    # Validate date format
    try:
        base_date = datetime.strptime(target, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: Invalid date format '{target}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    dates = [(base_date - timedelta(days=i)).isoformat() for i in range(args.range)]
    dates.reverse()  # Process chronologically

    if verbose:
        print(f"DevJournal Pipeline")
        print(f"  Output: {DEVJOURNAL_DIR}")
        print(f"  Dates: {dates}")
        print()

    for date_str in dates:
        if verbose:
            print(f"=== {date_str} ===")

        if not args.materialize_only:
            summary = compile_day(date_str, verbose=verbose)
            if verbose:
                print(f"  Compiled: {summary['new_events']} new events in {summary['duration_ms']}ms")
                print()

        digest = materialize_day(date_str, verbose=verbose)
        if verbose:
            print(f"  Digest: {digest.total_events} events, {len(digest.projects_active)} projects")
            print()

    # Print final summary
    if verbose:
        ledger_size = LEDGER_PATH.stat().st_size if LEDGER_PATH.exists() else 0
        day_files = list(DAYS_DIR.glob("*.json")) if DAYS_DIR.exists() else []
        print(f"--- Done ---")
        print(f"  Ledger: {LEDGER_PATH} ({ledger_size:,} bytes)")
        print(f"  Daily files: {len(day_files)} in {DAYS_DIR}")


if __name__ == "__main__":
    main()
