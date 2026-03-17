"""
ETS Compiler — merges trace collector outputs into the unified ledger.

Runs all active collectors (from trace registry or defaults),
deduplicates by oid, appends to the ledger (idempotent).
"""

import importlib
import importlib.util
import json
import socket
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, RunEnvelope,
    LEDGER_PATH, META_INDEX_PATH,
    append_to_ledger, ensure_dirs,
)

# Default collectors (v1 behavior when no registry is provided)
_DEFAULT_COLLECTORS = ["git_collector", "cli_collector", "fs_collector"]


def _load_registry(registry_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load trace registry YAML and return list of active trace entries."""
    if registry_path is None or not registry_path.exists():
        return []
    try:
        import yaml
        with open(registry_path) as f:
            data = yaml.safe_load(f)
        traces = data.get("traces", [])
        return [t for t in traces if t.get("status") == "active"]
    except Exception:
        return []


def _discover_collectors(registry_path: Optional[Path] = None) -> List[tuple]:
    """Discover collector functions from registry or defaults.

    Each collector must be a module in collectors/ with a collect(date_str) function.
    Returns list of (name, collect_fn) tuples.
    """
    collectors_dir = _devjournal / "collectors"
    collect_fns = []

    # Try registry first
    active_traces = _load_registry(registry_path)
    if active_traces:
        # Sort by priority
        active_traces.sort(key=lambda t: t.get("priority", 99))
        collector_names = [t["collector"] for t in active_traces]
    else:
        # Fall back to hardcoded defaults
        collector_names = _DEFAULT_COLLECTORS

    for name in collector_names:
        module_path = collectors_dir / f"{name}.py"
        if not module_path.exists():
            continue
        try:
            spec = importlib.util.spec_from_file_location(name, module_path)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "collect"):
                collect_fns.append((name, mod.collect))
        except Exception:
            continue

    return collect_fns


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


def compile_day(
    date_str: str,
    verbose: bool = False,
    registry_path: Optional[Path] = None,
) -> Dict:
    """Run all collectors and merge into the ledger.

    Args:
        date_str: Target date in YYYY-MM-DD format.
        verbose: Print progress to stdout.
        registry_path: Path to trace_registry.yaml (None = use defaults).

    Returns:
        Summary dict with stats.
    """
    start_ms = time.time()
    ensure_dirs()

    # Load existing oids for idempotency
    existing_oids = _load_existing_oids(date_str)
    if verbose and existing_oids:
        print(f"  Found {len(existing_oids)} existing events for {date_str}")

    # Discover and run collectors
    collector_fns = _discover_collectors(registry_path)
    results: List[CollectorResult] = []

    for name, collect_fn in collector_fns:
        if verbose:
            print(f"  Running {name}...")
        try:
            result = collect_fn(date_str)
            results.append(result)
        except Exception as e:
            if verbose:
                print(f"    {name} failed: {e}")

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
        f.write(json.dumps(envelope.model_dump(mode="json"), default=str, separators=(",", ":")) + "\n")

    return {
        "date": date_str,
        "new_events": new_count,
        "events_by_source": events_by_source,
        "duration_ms": elapsed_ms,
        "collector_stats": {r.source.value: r.stats for r in results},
    }
