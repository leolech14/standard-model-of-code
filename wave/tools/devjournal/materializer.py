"""
DevJournal Materializer — produces daily/weekly/project views from the ledger.

Reads devjournal.jsonl, groups events, computes metrics,
writes materialized JSON files for the Refinery dashboard.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))
from schema import (
    DailyDigest, DevJournalEvent,
    DAYS_DIR, LEDGER_PATH, ensure_dirs, read_ledger_for_date,
)


def _bucket_by_hour(events: List[DevJournalEvent]) -> List[Dict[str, Any]]:
    """Group events into hourly buckets for timeline charts."""
    hourly: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for e in events:
        hour = e.ts.hour
        hourly[hour][e.source.value] += 1
        hourly[hour]["_total"] += 1

    timeline = []
    for h in range(24):
        bucket = hourly.get(h, {})
        total = bucket.pop("_total", 0)
        timeline.append({
            "hour": h,
            "label": f"{h:02d}:00",
            "total": total,
            "by_source": dict(bucket),
        })
    return timeline


def _extract_highlights(events: List[DevJournalEvent], max_items: int = 15) -> List[Dict[str, Any]]:
    """Extract the most notable events for the highlights section."""
    highlights = []

    # Milestones first
    for e in events:
        if e.kind.value == "milestone":
            highlights.append({
                "oid": e.oid,
                "ts": e.ts.isoformat(),
                "kind": e.kind.value,
                "project": e.project,
                "title": e.data.get("title", ""),
                "detail": f"{e.data.get('commit_count', 0)} commits, {e.data.get('files_changed', 0)} files",
                "tags": e.tags,
            })

    # Session starts (show what projects were worked on)
    for e in events:
        if e.kind.value == "session_start":
            highlights.append({
                "oid": e.oid,
                "ts": e.ts.isoformat(),
                "kind": "session",
                "project": e.project,
                "title": f"Session started in {e.project}",
                "detail": "",
                "tags": [],
            })

    # Notable file creations (large files, interesting extensions)
    notable_extensions = {".py", ".ts", ".tsx", ".rs", ".go", ".yaml", ".json", ".md"}
    for e in events:
        if e.kind.value == "file_created":
            ext = e.data.get("extension", "")
            size = e.data.get("size_bytes", 0)
            if ext in notable_extensions and size > 500:
                scan_root = e.data.get("scan_root", "")
                if "Downloads" in scan_root or "_inbox" in scan_root:
                    highlights.append({
                        "oid": e.oid,
                        "ts": e.ts.isoformat(),
                        "kind": "inbox_arrival",
                        "project": e.project,
                        "title": f"New file in {scan_root}: {e.data.get('path', '')}",
                        "detail": f"{size:,} bytes",
                        "tags": ["inbox"],
                    })

    # Session conversations (AI activity summary)
    for e in events:
        if e.kind.value == "conversation":
            model = e.data.get("model", "unknown")
            msgs = e.data.get("total_messages", 0)
            tokens = e.data.get("total_tokens", 0)
            highlights.append({
                "oid": e.oid,
                "ts": e.ts.isoformat(),
                "kind": "ai_session",
                "project": e.project,
                "title": f"AI session ({model}): {msgs} messages",
                "detail": f"{tokens:,} tokens",
                "tags": ["session", model],
            })

    # Memory events
    for e in events:
        if e.kind.value in ("memory_written", "memory_updated"):
            action = "New memory" if e.kind.value == "memory_written" else "Updated memory"
            highlights.append({
                "oid": e.oid,
                "ts": e.ts.isoformat(),
                "kind": e.kind.value,
                "project": e.project,
                "title": f"{action}: {e.data.get('name', 'unknown')}",
                "detail": e.data.get("description", "")[:100],
                "tags": e.tags,
            })

    # Corroborated clusters
    for e in events:
        if e.kind.value == "corroborated":
            ctype = e.data.get("correlation_type", "")
            event_count = e.data.get("event_count", 0)
            sources = e.data.get("sources", [])
            if ctype == "session_cluster":
                dur = e.data.get("duration_minutes", 0)
                highlights.append({
                    "oid": e.oid,
                    "ts": e.ts.isoformat(),
                    "kind": "work_session",
                    "project": e.project,
                    "title": f"Work session: {event_count} events across {', '.join(sources)}",
                    "detail": f"{dur} minutes",
                    "tags": ["corroborated"] + sources,
                })

    # Sort by timestamp, cap at max
    highlights.sort(key=lambda h: h["ts"])
    return highlights[:max_items]


def _compute_velocity(events: List[DevJournalEvent]) -> Dict[str, Any]:
    """Compute velocity metrics from the day's events."""
    commits = [e for e in events if e.kind.value == "commit"]
    prompts = [e for e in events if e.kind.value == "prompt"]
    files_created = [e for e in events if e.kind.value == "file_created"]
    files_born = [e for e in events if e.kind.value == "file_born"]

    total_insertions = sum(e.data.get("insertions", 0) for e in commits)
    total_deletions = sum(e.data.get("deletions", 0) for e in commits)

    # Active hours (hours with any events)
    active_hours = len({e.ts.hour for e in events})

    return {
        "commits": len(commits),
        "prompts": len(prompts),
        "files_created": len(files_created),
        "files_born_in_git": len(files_born),
        "lines_added": total_insertions,
        "lines_removed": total_deletions,
        "net_lines": total_insertions - total_deletions,
        "active_hours": active_hours,
    }


def materialize_day(date_str: str, verbose: bool = False) -> DailyDigest:
    """Read ledger events for a date and produce a materialized daily digest.

    Args:
        date_str: Target date in YYYY-MM-DD format.
        verbose: Print progress.

    Returns:
        DailyDigest written to days/YYYY-MM-DD.json.
    """
    ensure_dirs()
    events = read_ledger_for_date(date_str)

    if verbose:
        print(f"  Materializing {len(events)} events for {date_str}")

    # Group by source
    by_source: Dict[str, int] = defaultdict(int)
    for e in events:
        by_source[e.source.value] += 1

    # Group by kind
    by_kind: Dict[str, int] = defaultdict(int)
    for e in events:
        by_kind[e.kind.value] += 1

    # Group by project
    by_project: Dict[str, int] = defaultdict(int)
    for e in events:
        proj = e.project or "_ecosystem"
        by_project[proj] += 1

    # Active projects (sorted by activity)
    projects_active = sorted(by_project.keys(), key=lambda p: -by_project[p])
    projects_active = [p for p in projects_active if p != "_ecosystem"]

    # Build digest
    digest = DailyDigest(
        date=date_str,
        generated_at=datetime.now(timezone.utc),
        total_events=len(events),
        events_by_source=dict(by_source),
        events_by_kind=dict(by_kind),
        events_by_project=dict(by_project),
        timeline=_bucket_by_hour(events),
        projects_active=projects_active,
        milestones=[
            {
                "oid": e.oid,
                "project": e.project,
                "type": e.data.get("type"),
                "title": e.data.get("title"),
                "commit_count": e.data.get("commit_count"),
            }
            for e in events if e.kind.value == "milestone"
        ],
        velocity=_compute_velocity(events),
        highlights=_extract_highlights(events),
    )

    # Write to disk
    output_path = DAYS_DIR / f"{date_str}.json"
    with open(output_path, "w") as f:
        json.dump(digest.model_dump(mode="json"), f, indent=2, default=str)

    if verbose:
        print(f"  Written to {output_path}")
        print(f"  Projects: {projects_active}")
        print(f"  Velocity: {digest.velocity}")

    return digest
