"""
ETS Trace Correlator — links events across sources into corroborated clusters.

Two algorithms:
1. Session Clustering: Groups events with <4h gaps into work sessions.
   A work session can span multiple sources (git + cli + fs + session).
2. Bucket Correlation: Events within 5-minute windows in the same project
   are linked as "caused by the same action."

Output: CORROBORATED meta-events that reference their constituent event oids.
These can then be materialized into the daily digest for richer narratives.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_devjournal = Path(__file__).resolve().parent
sys.path.insert(0, str(_devjournal))
from schema import (
    DevJournalEvent, EventKind, Source,
    LEDGER_PATH, ETS_DIR, generate_oid, read_ledger_for_date,
)

# Correlation parameters
SESSION_GAP_HOURS = 4       # Max gap between events in same work session
BUCKET_MINUTES = 5          # Time window for fine-grained correlation
MIN_CLUSTER_SIZE = 2        # Minimum events to form a corroborated cluster
MIN_SESSION_EVENTS = 3      # Minimum events for a meaningful work session


def _cluster_into_sessions(
    events: List[DevJournalEvent],
) -> List[List[DevJournalEvent]]:
    """Group events into work sessions using gap-splitting.

    Events are sorted by timestamp. A new session starts when the gap
    between consecutive events exceeds SESSION_GAP_HOURS.
    """
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: e.ts)
    sessions: List[List[DevJournalEvent]] = [[sorted_events[0]]]

    for event in sorted_events[1:]:
        last_ts = sessions[-1][-1].ts
        gap = (event.ts - last_ts).total_seconds() / 3600

        if gap > SESSION_GAP_HOURS:
            sessions.append([event])
        else:
            sessions[-1].append(event)

    return sessions


def _bucket_correlate(
    events: List[DevJournalEvent],
) -> List[List[DevJournalEvent]]:
    """Find correlated event clusters within BUCKET_MINUTES windows.

    Groups events by project, then finds clusters where multiple sources
    contribute events within a tight time window. This detects patterns
    like: prompt → commit → file births (all within 5 minutes).
    """
    # Group by project
    by_project: Dict[Optional[str], List[DevJournalEvent]] = defaultdict(list)
    for e in events:
        by_project[e.project].append(e)

    clusters: List[List[DevJournalEvent]] = []

    for project, proj_events in by_project.items():
        sorted_evts = sorted(proj_events, key=lambda e: e.ts)

        # Sliding window
        i = 0
        while i < len(sorted_evts):
            window: List[DevJournalEvent] = [sorted_evts[i]]
            j = i + 1

            while j < len(sorted_evts):
                gap = (sorted_evts[j].ts - sorted_evts[i].ts).total_seconds() / 60
                if gap > BUCKET_MINUTES:
                    break
                window.append(sorted_evts[j])
                j += 1

            # Only keep clusters with multiple sources
            sources_in_window = {e.source for e in window}
            if len(window) >= MIN_CLUSTER_SIZE and len(sources_in_window) >= 2:
                clusters.append(window)
                i = j  # Skip past this cluster
            else:
                i += 1

    return clusters


def _describe_session(session: List[DevJournalEvent]) -> Dict[str, Any]:
    """Build a descriptive summary of a work session."""
    sources = sorted({e.source.value for e in session})
    projects = sorted({e.project for e in session if e.project})
    kinds = sorted({e.kind.value for e in session})

    first = session[0]
    last = session[-1]
    duration_min = int((last.ts - first.ts).total_seconds() / 60)

    # Count by source
    source_counts: Dict[str, int] = defaultdict(int)
    for e in session:
        source_counts[e.source.value] += 1

    # Find commits for narrative
    commits = [e for e in session if e.kind == EventKind.COMMIT]
    commit_msgs = [e.data.get("message", "")[:80] for e in commits[:3]]

    # Check for signatures
    signed = [e for e in session if e.signature is not None]
    models = sorted({e.signature.model for e in signed if e.signature})

    return {
        "sources": sources,
        "projects": projects,
        "kinds": kinds,
        "event_count": len(session),
        "duration_minutes": duration_min,
        "source_counts": dict(source_counts),
        "commit_messages": commit_msgs,
        "models": models,
        "has_signatures": len(signed) > 0,
        "start_ts": first.ts.isoformat(),
        "end_ts": last.ts.isoformat(),
    }


def _describe_cluster(cluster: List[DevJournalEvent]) -> Dict[str, Any]:
    """Build a descriptive summary of a correlated cluster."""
    sources = sorted({e.source.value for e in cluster})
    kinds = sorted({e.kind.value for e in cluster})

    return {
        "sources": sources,
        "kinds": kinds,
        "event_count": len(cluster),
        "window_seconds": int((cluster[-1].ts - cluster[0].ts).total_seconds()),
        "oids": [e.oid for e in cluster],
        "project": cluster[0].project,
    }


def correlate_day(
    date_str: str,
    verbose: bool = False,
) -> List[DevJournalEvent]:
    """Run correlation on all events for a target date.

    Returns a list of CORROBORATED meta-events to be appended to the ledger.
    """
    events = read_ledger_for_date(date_str)

    if verbose:
        print(f"  Correlator: {len(events)} events for {date_str}")

    if len(events) < MIN_CLUSTER_SIZE:
        return []

    corroborated_events: List[DevJournalEvent] = []

    # 1. Session clustering
    sessions = _cluster_into_sessions(events)
    meaningful_sessions = [s for s in sessions if len(s) >= MIN_SESSION_EVENTS]

    if verbose:
        print(f"  Sessions: {len(sessions)} total, {len(meaningful_sessions)} meaningful (>={MIN_SESSION_EVENTS} events)")

    for i, session in enumerate(meaningful_sessions):
        desc = _describe_session(session)
        ts = session[-1].ts  # Use end time of session

        oid = generate_oid(
            ts, "system", "corroborated",
            f"session:{date_str}:{i}:{desc['event_count']}",
        )

        corroborated_events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.SYSTEM,
            kind=EventKind.CORROBORATED,
            project=desc["projects"][0] if len(desc["projects"]) == 1 else None,
            data={
                "correlation_type": "session_cluster",
                "session_index": i,
                **desc,
            },
            tags=["corroborated", "session"] + desc["sources"],
        ))

    # 2. Bucket correlation
    clusters = _bucket_correlate(events)

    if verbose:
        print(f"  Clusters: {len(clusters)} cross-source clusters found")

    for i, cluster in enumerate(clusters):
        desc = _describe_cluster(cluster)
        ts = cluster[-1].ts

        oid = generate_oid(
            ts, "system", "corroborated",
            f"bucket:{date_str}:{i}:{desc['event_count']}",
        )

        corroborated_events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.SYSTEM,
            kind=EventKind.CORROBORATED,
            project=desc["project"],
            data={
                "correlation_type": "bucket_cluster",
                "cluster_index": i,
                **desc,
            },
            tags=["corroborated", "bucket"] + desc["sources"],
        ))

    if verbose:
        print(f"  Total corroborated events: {len(corroborated_events)}")

    return corroborated_events


def write_correlation_report(
    date_str: str,
    corroborated: List[DevJournalEvent],
) -> Path:
    """Write a correlation report to the ETS maps directory."""
    output_dir = ETS_DIR / "maps" / "correlations"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"{date_str}.json"

    sessions = [e for e in corroborated if e.data.get("correlation_type") == "session_cluster"]
    buckets = [e for e in corroborated if e.data.get("correlation_type") == "bucket_cluster"]

    report = {
        "date": date_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_corroborated": len(corroborated),
            "session_clusters": len(sessions),
            "bucket_clusters": len(buckets),
        },
        "sessions": [
            {
                "oid": e.oid,
                "duration_minutes": e.data.get("duration_minutes", 0),
                "event_count": e.data.get("event_count", 0),
                "sources": e.data.get("sources", []),
                "projects": e.data.get("projects", []),
                "models": e.data.get("models", []),
                "commit_messages": e.data.get("commit_messages", []),
            }
            for e in sessions
        ],
        "clusters": [
            {
                "oid": e.oid,
                "project": e.project,
                "sources": e.data.get("sources", []),
                "event_count": e.data.get("event_count", 0),
                "window_seconds": e.data.get("window_seconds", 0),
            }
            for e in buckets
        ],
    }

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return report_path


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()

    corroborated = correlate_day(target, verbose=True)

    if corroborated:
        report_path = write_correlation_report(target, corroborated)
        print(f"\n  Report: {report_path}")

        # Optionally append to ledger
        if "--append" in sys.argv:
            from schema import append_to_ledger
            append_to_ledger(corroborated)
            print(f"  Appended {len(corroborated)} corroborated events to ledger")
