"""
GitHub Collector — tracks GitHub activity via the gh CLI.

Reads push events, PR activity, and issue events for the target date
across all repos owned by the authenticated user. Uses `gh api` for
efficient querying without requiring a separate API token.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    generate_oid,
)

GH_USER = "leolech14"


def _run_gh(args: list) -> Optional[str]:
    """Run a gh CLI command, return stdout or None on failure."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def _fetch_events(date_str: str) -> List[Dict[str, Any]]:
    """Fetch GitHub events for the user on the target date.

    Uses the GitHub Events API via gh. Returns up to 100 events
    (API page limit), filtered to the target date.
    """
    out = _run_gh([
        "api", f"/users/{GH_USER}/events",
        "--paginate", "--jq", ".",
        "-H", "Accept: application/vnd.github+json",
    ])
    if not out:
        return []

    try:
        events = json.loads(out)
    except json.JSONDecodeError:
        # gh --paginate outputs multiple JSON arrays, try line-by-line
        events = []
        for line in out.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
                if isinstance(parsed, list):
                    events.extend(parsed)
                elif isinstance(parsed, dict):
                    events.append(parsed)
            except json.JSONDecodeError:
                continue

    # Filter to target date
    filtered = []
    for event in events:
        created_at = event.get("created_at", "")
        if created_at.startswith(date_str):
            filtered.append(event)

    return filtered


def _event_to_trace(event: Dict[str, Any]) -> Optional[DevJournalEvent]:
    """Convert a GitHub event to a DevJournalEvent."""
    event_type = event.get("type", "")
    created_at = event.get("created_at", "")
    repo_name = event.get("repo", {}).get("name", "")
    payload = event.get("payload", {})

    try:
        ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

    # Map to project name
    project = None
    short_repo = repo_name.split("/")[-1] if "/" in repo_name else repo_name
    if short_repo.startswith("PROJECT_") or short_repo.lower().startswith("project_"):
        project = short_repo

    data: Dict[str, Any] = {
        "event_type": event_type,
        "repo": repo_name,
    }

    kind = EventKind.COMMIT  # Default, will be refined below

    if event_type == "PushEvent":
        commits = payload.get("commits", [])
        data["commits"] = len(commits)
        data["ref"] = payload.get("ref", "")
        if commits:
            data["head_message"] = commits[-1].get("message", "")[:100]
        kind = EventKind.COMMIT

    elif event_type == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        data["action"] = payload.get("action", "")
        data["pr_number"] = pr.get("number")
        data["title"] = pr.get("title", "")[:100]
        data["state"] = pr.get("state", "")
        kind = EventKind.MILESTONE if payload.get("action") == "closed" and pr.get("merged") else EventKind.COMMIT

    elif event_type == "IssuesEvent":
        issue = payload.get("issue", {})
        data["action"] = payload.get("action", "")
        data["issue_number"] = issue.get("number")
        data["title"] = issue.get("title", "")[:100]
        kind = EventKind.COMMIT

    elif event_type == "CreateEvent":
        data["ref_type"] = payload.get("ref_type", "")
        data["ref"] = payload.get("ref", "")
        kind = EventKind.FILE_BORN

    elif event_type == "ReleaseEvent":
        release = payload.get("release", {})
        data["action"] = payload.get("action", "")
        data["tag_name"] = release.get("tag_name", "")
        data["name"] = release.get("name", "")[:100]
        kind = EventKind.MILESTONE

    elif event_type == "IssueCommentEvent":
        data["action"] = payload.get("action", "")
        data["issue_number"] = payload.get("issue", {}).get("number")
        data["comment_body"] = payload.get("comment", {}).get("body", "")[:200]
        kind = EventKind.PROMPT  # Closest match: a written message

    else:
        data["raw_type"] = event_type
        kind = EventKind.COMMIT

    oid = generate_oid(ts, "github", event_type.lower(), f"{repo_name}:{event.get('id', '')}")

    return DevJournalEvent(
        oid=oid,
        ts=ts,
        source=Source.GITHUB,
        kind=kind,
        project=project,
        data=data,
        tags=["github", event_type.lower(), short_repo],
    )


def collect(date_str: str) -> CollectorResult:
    """Run the GitHub collector for a target date."""
    raw_events = _fetch_events(date_str)
    all_events: List[DevJournalEvent] = []
    event_types: Dict[str, int] = {}
    repos_seen: set = set()

    for raw in raw_events:
        trace = _event_to_trace(raw)
        if trace:
            all_events.append(trace)
            etype = raw.get("type", "unknown")
            event_types[etype] = event_types.get(etype, 0) + 1
            repos_seen.add(raw.get("repo", {}).get("name", ""))

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.GITHUB,
        target_date=date_str,
        events=all_events,
        stats={
            "raw_events": len(raw_events),
            "trace_events": len(all_events),
            "event_types": event_types,
            "repos": sorted(repos_seen),
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"GitHub collector: {len(result.events)} events")
    print(f"  Event types: {result.stats.get('event_types', {})}")
    print(f"  Repos: {result.stats.get('repos', [])}")
