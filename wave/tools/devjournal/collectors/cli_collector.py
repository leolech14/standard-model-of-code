"""
CLI Collector — parses Claude Code history.jsonl for prompts on target date.

Reads ~/.claude/history.jsonl, filters to target date,
groups by project + session, emits prompt and session_start events.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    CLI_HISTORY_PATH, generate_oid,
)


def _parse_history(date_str: str) -> List[Dict[str, Any]]:
    """Parse history.jsonl, returning entries for the target date."""
    entries = []
    if not CLI_HISTORY_PATH.exists():
        return entries

    # Parse target date boundaries (in milliseconds)
    target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_start_ms = int(target_date.timestamp() * 1000)
    day_end_ms = day_start_ms + 86_400_000  # +24h

    with open(CLI_HISTORY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts_ms = entry.get("timestamp", 0)
                if day_start_ms <= ts_ms < day_end_ms:
                    entries.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue

    return entries


def _extract_project_name(project_path: str) -> str:
    """Extract PROJECT_name from a full path, or return the last dir component."""
    if not project_path:
        return "unknown"
    parts = project_path.rstrip("/").split("/")
    for part in reversed(parts):
        if part.startswith("PROJECT_"):
            return part
    # Fall back to last component
    return parts[-1] if parts else "unknown"


def collect(date_str: str) -> CollectorResult:
    """Run the CLI collector for a target date.

    Args:
        date_str: Target date in YYYY-MM-DD format.

    Returns:
        CollectorResult with prompt and session events for the day.
    """
    entries = _parse_history(date_str)
    events: List[DevJournalEvent] = []

    # Track sessions for session_start detection
    seen_sessions: Dict[str, datetime] = {}
    project_counts: Dict[str, int] = defaultdict(int)

    for entry in entries:
        ts_ms = entry.get("timestamp", 0)
        ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        display = entry.get("display", "")
        project_path = entry.get("project", "")
        session_id = entry.get("sessionId", "")
        project_name = _extract_project_name(project_path)

        if not display:
            continue

        # Emit session_start on first prompt per session
        if session_id and session_id not in seen_sessions:
            seen_sessions[session_id] = ts
            sess_oid = generate_oid(ts, "cli", "session_start", session_id[:16])
            events.append(DevJournalEvent(
                oid=sess_oid,
                ts=ts,
                source=Source.CLI,
                kind=EventKind.SESSION_START,
                project=project_name,
                data={
                    "session_id": session_id,
                    "project_path": project_path,
                },
            ))

        # Emit prompt event
        # Truncate display for storage (keep first 500 chars)
        display_truncated = display[:500] + ("..." if len(display) > 500 else "")
        data_key = f"{ts_ms}:{display[:50]}"
        oid = generate_oid(ts, "cli", "prompt", data_key)

        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.CLI,
            kind=EventKind.PROMPT,
            project=project_name,
            data={
                "display": display_truncated,
                "char_count": len(display),
                "session_id": session_id,
            },
        ))
        project_counts[project_name] += 1

    # Sort by timestamp
    events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.CLI,
        target_date=date_str,
        events=events,
        stats={
            "total_prompts": sum(1 for e in events if e.kind == EventKind.PROMPT),
            "total_sessions": len(seen_sessions),
            "prompts_by_project": dict(project_counts),
            "history_file": str(CLI_HISTORY_PATH),
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"CLI collector: {len(result.events)} events")
    print(f"  Prompts: {result.stats.get('total_prompts', 0)}")
    print(f"  Sessions: {result.stats.get('total_sessions', 0)}")
    print(f"  By project: {result.stats.get('prompts_by_project', {})}")
