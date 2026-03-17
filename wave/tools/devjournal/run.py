#!/usr/bin/env python3
"""
ETS CLI — run the Ecosystem Trace & Signature ingestion pipeline.

Usage:
    python run.py                        # Today
    python run.py 2026-03-16             # Specific date
    python run.py --range 3              # Last 3 days
    python run.py --materialize-only     # Re-materialize from existing ledger
    python run.py --registry ~/.ets/trace_registry.yaml  # Use trace registry
"""

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))

from compiler import compile_day
from correlator import correlate_day, write_correlation_report
from materializer import materialize_day
from schema import (
    DEVJOURNAL_DIR, DAYS_DIR, LEDGER_PATH, ETS_REGISTRY_PATH,
    append_to_ledger,
)


def main():
    parser = argparse.ArgumentParser(description="ETS — Ecosystem Trace & Signature pipeline")
    parser.add_argument("date", nargs="?", default=None, help="Target date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--range", type=int, default=1, help="Number of days to process (backwards from date).")
    parser.add_argument("--materialize-only", action="store_true", help="Skip collectors, re-materialize from ledger.")
    parser.add_argument("--no-correlate", action="store_true", help="Skip trace correlation.")
    parser.add_argument("--quiet", action="store_true", help="Suppress output.")
    parser.add_argument("--registry", type=str, default=None,
                        help="Path to trace_registry.yaml. Default: ~/.ets/trace_registry.yaml if exists.")
    args = parser.parse_args()

    verbose = not args.quiet
    target = args.date or date.today().isoformat()

    # Resolve registry path
    registry_path = None
    if args.registry:
        registry_path = Path(args.registry).expanduser()
    elif ETS_REGISTRY_PATH.exists():
        registry_path = ETS_REGISTRY_PATH

    # Validate date format
    try:
        base_date = datetime.strptime(target, "%Y-%m-%d").date()
    except ValueError:
        print(f"Error: Invalid date format '{target}'. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    dates = [(base_date - timedelta(days=i)).isoformat() for i in range(args.range)]
    dates.reverse()  # Process chronologically

    if verbose:
        mode = "ETS" if registry_path else "DevJournal (legacy)"
        print(f"Ecosystem Trace & Signature Pipeline")
        print(f"  Mode: {mode}")
        print(f"  Output: {DEVJOURNAL_DIR}")
        if registry_path:
            print(f"  Registry: {registry_path}")
        print(f"  Dates: {dates}")
        print()

    for date_str in dates:
        if verbose:
            print(f"=== {date_str} ===")

        if not args.materialize_only:
            summary = compile_day(date_str, verbose=verbose, registry_path=registry_path)
            if verbose:
                print(f"  Compiled: {summary['new_events']} new events in {summary['duration_ms']}ms")
                print()

        # Run correlation (after compilation, before materialization)
        if not args.no_correlate:
            if verbose:
                print(f"  Correlating...")
            corroborated = correlate_day(date_str, verbose=verbose)
            if corroborated:
                append_to_ledger(corroborated)
                report_path = write_correlation_report(date_str, corroborated)
                if verbose:
                    print(f"  Correlated: {len(corroborated)} meta-events → {report_path}")
            elif verbose:
                print(f"  No correlations found")
            if verbose:
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
