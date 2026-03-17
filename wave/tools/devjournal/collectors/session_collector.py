"""
Session Transcript Collector — parses Claude Code session transcripts.

Reads ~/.claude/projects/*/*.jsonl for the target date.
Extracts model, session start/end, tool calls, files touched, token usage.
Auto-populates Signature from session data (model field in assistant messages).

This is the richest trace source — contains the WHY behind every action.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Signature, Source,
    generate_oid,
)

# All project transcript directories
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Types we extract from transcript lines
INTERESTING_TYPES = {"user", "assistant"}


def _extract_project_name(dir_name: str) -> Optional[str]:
    """Extract PROJECT_name from a Claude projects directory name.

    Directory names look like: -Users-lech-PROJECTS-all-PROJECT-elements
    """
    parts = dir_name.split("-")
    # Find PROJECT_ segments
    for i, part in enumerate(parts):
        if part == "PROJECT" and i + 1 < len(parts):
            # Reconstruct: PROJECT_nextpart
            return f"PROJECT_{parts[i + 1]}"
    # Check for home dir sessions (e.g., -Users-lech)
    if dir_name.endswith("-Users-lech") or dir_name == "-Users-lech":
        return None  # Ecosystem-wide session
    return None


def _parse_session_file(
    file_path: Path,
    date_str: str,
) -> Dict[str, Any]:
    """Parse a single session .jsonl file, returning session metadata.

    Returns dict with: session_id, model, version, cwd, git_branch,
    project, messages (list), tool_uses, input_tokens, output_tokens,
    first_ts, last_ts.
    """
    session_data = {
        "session_id": file_path.stem,
        "file_path": str(file_path),
        "model": None,
        "version": None,
        "cwd": None,
        "git_branch": None,
        "project": None,
        "user_messages": 0,
        "assistant_messages": 0,
        "tool_uses": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "first_ts": None,
        "last_ts": None,
        "has_activity_on_date": False,
    }

    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts_str = entry.get("timestamp")
                if not ts_str:
                    continue

                # Check if this entry falls on our target date
                if not ts_str.startswith(date_str):
                    continue

                session_data["has_activity_on_date"] = True

                # Extract metadata from any message
                if entry.get("sessionId") and not session_data["cwd"]:
                    session_data["cwd"] = entry.get("cwd")
                    session_data["git_branch"] = entry.get("gitBranch")
                    session_data["version"] = entry.get("version")

                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

                if session_data["first_ts"] is None or ts < session_data["first_ts"]:
                    session_data["first_ts"] = ts
                if session_data["last_ts"] is None or ts > session_data["last_ts"]:
                    session_data["last_ts"] = ts

                entry_type = entry.get("type")

                if entry_type == "user":
                    session_data["user_messages"] += 1

                elif entry_type == "assistant":
                    session_data["assistant_messages"] += 1
                    msg = entry.get("message", {})

                    # Model attribution
                    model = msg.get("model")
                    if model and not session_data["model"]:
                        session_data["model"] = model

                    # Token usage
                    usage = msg.get("usage", {})
                    session_data["input_tokens"] += usage.get("input_tokens", 0)
                    session_data["input_tokens"] += usage.get("cache_creation_input_tokens", 0)
                    session_data["input_tokens"] += usage.get("cache_read_input_tokens", 0)
                    session_data["output_tokens"] += usage.get("output_tokens", 0)

                    # Tool uses
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                session_data["tool_uses"].append(block.get("name", "unknown"))

    except (OSError, PermissionError):
        pass

    return session_data


def _session_to_events(
    session_data: Dict[str, Any],
    dir_name: str,
) -> List[DevJournalEvent]:
    """Convert parsed session data into DevJournalEvent objects."""
    events = []

    if not session_data["has_activity_on_date"]:
        return events

    session_id = session_data["session_id"]
    project = _extract_project_name(dir_name) or session_data.get("project")
    first_ts = session_data["first_ts"]
    last_ts = session_data["last_ts"]
    model = session_data["model"]

    if not first_ts:
        return events

    # Build Signature from session data
    signature = None
    if model:
        signature = Signature(
            model=model,
            access_point="cli",
            orchestration="direct",
            session_id=session_id,
            hostname="mac",
        )

    # Emit SESSION_START
    oid = generate_oid(first_ts, "session", "session_start", session_id[:16])
    events.append(DevJournalEvent(
        oid=oid,
        ts=first_ts,
        source=Source.SESSION,
        kind=EventKind.SESSION_START,
        project=project,
        data={
            "session_id": session_id,
            "model": model,
            "version": session_data["version"],
            "cwd": session_data["cwd"],
            "git_branch": session_data["git_branch"],
        },
        tags=["session", model or "unknown-model"],
        signature=signature,
    ))

    # Emit CONVERSATION summary event
    tool_counts: Dict[str, int] = defaultdict(int)
    for tool in session_data["tool_uses"]:
        tool_counts[tool] += 1
    top_tools = dict(sorted(tool_counts.items(), key=lambda x: -x[1])[:5])

    total_messages = session_data["user_messages"] + session_data["assistant_messages"]
    if total_messages > 0:
        conv_oid = generate_oid(
            last_ts or first_ts, "session", "conversation",
            f"{session_id[:12]}:{total_messages}",
        )
        events.append(DevJournalEvent(
            oid=conv_oid,
            ts=last_ts or first_ts,
            source=Source.SESSION,
            kind=EventKind.CONVERSATION,
            project=project,
            data={
                "session_id": session_id,
                "model": model,
                "user_messages": session_data["user_messages"],
                "assistant_messages": session_data["assistant_messages"],
                "total_messages": total_messages,
                "tool_uses": len(session_data["tool_uses"]),
                "top_tools": top_tools,
                "input_tokens": session_data["input_tokens"],
                "output_tokens": session_data["output_tokens"],
                "total_tokens": session_data["input_tokens"] + session_data["output_tokens"],
                "duration_minutes": (
                    int((last_ts - first_ts).total_seconds() / 60)
                    if last_ts and first_ts and last_ts > first_ts
                    else 0
                ),
            },
            tags=["conversation", model or "unknown-model"],
            signature=signature,
        ))

    return events


def collect(date_str: str) -> CollectorResult:
    """Run the session transcript collector for a target date.

    Scans all ~/.claude/projects/*/*.jsonl files, parses those with
    activity on the target date, and emits SESSION_START + CONVERSATION events.
    """
    all_events: List[DevJournalEvent] = []
    sessions_found = 0
    total_tokens = 0
    models_seen: Set[str] = set()

    if not CLAUDE_PROJECTS_DIR.is_dir():
        return CollectorResult(
            source=Source.SESSION,
            target_date=date_str,
            events=[],
            stats={"error": "Claude projects directory not found"},
        )

    for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue

        dir_name = project_dir.name

        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            # Quick pre-filter: check file mtime is recent enough
            try:
                stat = jsonl_file.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                # Skip files not modified within +-2 days of target
                target = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if abs((file_date - target).days) > 2:
                    continue
            except OSError:
                continue

            session_data = _parse_session_file(jsonl_file, date_str)

            if not session_data["has_activity_on_date"]:
                continue

            events = _session_to_events(session_data, dir_name)
            all_events.extend(events)

            if events:
                sessions_found += 1
                total_tokens += session_data["input_tokens"] + session_data["output_tokens"]
                if session_data["model"]:
                    models_seen.add(session_data["model"])

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.SESSION,
        target_date=date_str,
        events=all_events,
        stats={
            "sessions_found": sessions_found,
            "total_events": len(all_events),
            "total_tokens": total_tokens,
            "models_seen": sorted(models_seen),
            "session_starts": sum(1 for e in all_events if e.kind == EventKind.SESSION_START),
            "conversations": sum(1 for e in all_events if e.kind == EventKind.CONVERSATION),
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"Session collector: {len(result.events)} events from {result.stats.get('sessions_found', 0)} sessions")
    print(f"  Session starts: {result.stats.get('session_starts', 0)}")
    print(f"  Conversations: {result.stats.get('conversations', 0)}")
    print(f"  Total tokens: {result.stats.get('total_tokens', 0):,}")
    print(f"  Models: {result.stats.get('models_seen', [])}")
