"""
DevJournal Compiler — merges collector outputs into the unified ledger.

Runs all collectors for a target date, deduplicates by oid,
appends to devjournal.jsonl (idempotent).
"""

import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, RunEnvelope,
    LEDGER_PATH, META_INDEX_PATH,
    append_to_ledger, ensure_dirs,
)
from collectors.git_collector import collect as git_collect
from collectors.cli_collector import collect as cli_collect
from collectors.fs_collector import collect as fs_collect


def _load_existing_oids(date_str: str) -> Set[str]:
    """Load oids already in the ledger for the target date to avoid duplicates."""
    existing = set()
    if not LEDGER_PATH.exists():
        return existing
    with open(LEDGER_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Quick check: does this line contain the target date?
            if date_str not in line:
                continue
            try:
                evt = DevJournalEvent.from_jsonl(line)
                if evt.ts.strftime("%Y-%m-%d") == date_str:
                    existing.add(evt.oid)
            except Exception:
                continue
    return existing


def compile_day(date_str: str, verbose: bool = False) -> Dict:
    """Run all collectors and merge into the ledger.

    Args:
        date_str: Target date in YYYY-MM-DD format.
        verbose: Print progress to stdout.

    Returns:
        Summary dict with stats.
    """
    start_ms = time.time()
    ensure_dirs()

    # Load existing oids for idempotency
    existing_oids = _load_existing_oids(date_str)
    if verbose and existing_oids:
        print(f"  Found {len(existing_oids)} existing events for {date_str}")

    # Run collectors
    results: List[CollectorResult] = []

    if verbose:
        print("  Running git collector...")
    results.append(git_collect(date_str))

    if verbose:
        print("  Running CLI collector...")
    results.append(cli_collect(date_str))

    if verbose:
        print("  Running FS collector...")
    results.append(fs_collect(date_str))

    # Merge and deduplicate
    all_events: List[DevJournalEvent] = []
    events_by_source: Dict[str, int] = {}
    new_count = 0

    for result in results:
        source_name = result.source.value
        source_events = [e for e in result.events if e.oid not in existing_oids]
        events_by_source[source_name] = len(source_events)
        all_events.extend(source_events)
        new_count += len(source_events)

        if verbose:
            total = len(result.events)
            skipped = total - len(source_events)
            print(f"    {source_name}: {len(source_events)} new ({skipped} duplicates skipped)")

    # Sort chronologically
    all_events.sort(key=lambda e: e.ts)

    # Append to ledger
    if all_events:
        append_to_ledger(all_events)

    elapsed_ms = int((time.time() - start_ms) * 1000)

    # Write run envelope to meta_index
    import socket
    envelope = RunEnvelope(
        run_id=str(uuid.uuid4()),
        run_ts=datetime.now(timezone.utc),
        target_date=date_str,
        sources_run=[r.source.value for r in results],
        total_events=new_count,
        events_by_source=events_by_source,
        duration_ms=elapsed_ms,
        hostname=socket.gethostname(),
    )
    with open(META_INDEX_PATH, "a") as f:
        import json
        f.write(json.dumps(envelope.model_dump(mode="json"), default=str, separators=(",", ":")) + "\n")

    return {
        "date": date_str,
        "new_events": new_count,
        "events_by_source": events_by_source,
        "duration_ms": elapsed_ms,
        "collector_stats": {r.source.value: r.stats for r in results},
    }
