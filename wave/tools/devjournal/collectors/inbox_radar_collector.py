"""
Inbox Radar Collector — tracks email financial intelligence scan runs.

Reads scan metadata from ~/.ets/inbox-radar/ and emits:
  - ANALYSIS_RUN events for each scan run (from meta_index.jsonl)
  - FINANCE_EVENT events for unregistered financial domains (from tier1_raw.json)

Data source: Inbox Radar tool (~/_tools/scripts/inbox_radar.py)
Output: TraceEvents appended to the ETS ledger

Integration pattern: Inbox Radar writes its own meta_index.jsonl and tier1 output.
This collector reads those outputs and converts them to TraceEvents, making
inbox-radar a first-class intelligence source in the ETS pipeline.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    generate_oid,
)

INBOX_RADAR_DIR = Path.home() / ".ets" / "inbox-radar"
META_INDEX_PATH = INBOX_RADAR_DIR / "meta_index.jsonl"
TIER1_PATH = INBOX_RADAR_DIR / "tier1_raw.json"


def _parse_meta_index(date_str: str) -> list[dict]:
    """Read scan run entries from meta_index.jsonl matching target date."""
    if not META_INDEX_PATH.exists():
        return []

    runs = []
    try:
        for line in META_INDEX_PATH.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                run_ts = entry.get("run_ts", "")
                if run_ts.startswith(date_str):
                    runs.append(entry)
            except json.JSONDecodeError:
                continue
    except OSError:
        pass

    return runs


def _parse_tier1_unregistered(date_str: str) -> list[dict]:
    """Read unregistered financial domains from tier1_raw.json.

    Only returns data if the tier1 was generated on the target date.
    """
    if not TIER1_PATH.exists():
        return []

    try:
        data = json.loads(TIER1_PATH.read_text())
        envelope = data.get("meta_envelope", {})
        run_ts = envelope.get("run_ts", "")
        if not run_ts.startswith(date_str):
            return []

        return data.get("unregistered", [])
    except (OSError, json.JSONDecodeError):
        return []


def collect(date_str: str) -> CollectorResult:
    """Collect inbox-radar events for the target date.

    Emits:
      - ANALYSIS_RUN for each scan run
      - FINANCE_EVENT for each unregistered financial domain
    """
    events: List[DevJournalEvent] = []

    # 1. Scan run events from meta_index.jsonl
    runs = _parse_meta_index(date_str)
    for run in runs:
        run_id = run.get("run_id", "unknown")
        run_ts_str = run.get("run_ts", "")
        try:
            ts = datetime.fromisoformat(run_ts_str).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        oid = generate_oid(ts, "email", "analysis_run", f"inbox-radar-{run_id}")

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.EMAIL,
            kind=EventKind.ANALYSIS_RUN,
            project=None,  # ecosystem-wide
            data={
                "tool": "inbox-radar",
                "run_id": run_id,
                "mode": run.get("mode", "turbulent"),
                "accounts_scanned": run.get("accounts_scanned", 0),
                "total_messages": run.get("total_messages_processed", 0),
                "total_senders": run.get("total_senders_found", 0),
                "domains_classified": run.get("total_domains_classified", 0),
                "unregistered_count": run.get("unregistered_count", 0),
                "duplicate_count": run.get("duplicate_count", 0),
                "duration_seconds": run.get("scan_duration_seconds", 0),
            },
            tags=["inbox-radar", "financial-intelligence", "email-scan"],
        ))

    # 2. Finance events from unregistered domains
    unregistered = _parse_tier1_unregistered(date_str)
    for domain_entry in unregistered:
        domain = domain_entry.get("domain", "")
        if not domain:
            continue

        # Use the last_seen date as timestamp, falling back to date_str
        last_seen = domain_entry.get("last_seen", date_str)
        try:
            ts = datetime.strptime(last_seen, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            ts = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # Only emit if the event falls on target date
        if ts.strftime("%Y-%m-%d") != date_str:
            # Use scan date instead
            ts = datetime.strptime(date_str, "%Y-%m-%d").replace(
                hour=12, tzinfo=timezone.utc
            )

        oid = generate_oid(ts, "email", "finance_event", f"unregistered-{domain}")

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.EMAIL,
            kind=EventKind.FINANCE_EVENT,
            project=None,
            data={
                "tool": "inbox-radar",
                "domain": domain,
                "intent": domain_entry.get("intent", "unknown"),
                "confidence": domain_entry.get("confidence", 0),
                "financial_risk": domain_entry.get("financial_risk", "none"),
                "action_needed": domain_entry.get("action_needed", "none"),
                "accounts": domain_entry.get("accounts", []),
                "message_count": domain_entry.get("message_count", 0),
            },
            tags=["inbox-radar", "unregistered-financial", f"risk:{domain_entry.get('financial_risk', 'none')}"],
        ))

    return CollectorResult(
        source=Source.EMAIL,
        target_date=date_str,
        events=events,
        stats={
            "scan_runs": len(runs),
            "unregistered_domains": len(unregistered),
            "total_events": len(events),
        },
    )
