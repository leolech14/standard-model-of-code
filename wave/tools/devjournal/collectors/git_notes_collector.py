"""
Git Notes Collector — reads ETS signature metadata from git notes.

Scans PROJECTS_all repos for git notes in the refs/notes/ets-signatures
namespace. Notes contain JSON with Signature Protocol fields attached to
specific commits. Emits GIT_NOTE_ADDED events.

This is the READ side of the Signature Protocol's git notes integration.
The WRITE side is the post-commit hook (tools/ets-post-commit-hook.sh).
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Signature, Source,
    PROJECTS_ROOT, generate_oid,
)

NOTES_REF = "refs/notes/ets-signatures"


def _run_git(repo: str, args: list) -> Optional[str]:
    """Run a git command, return stdout or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _has_notes_ref(repo: str) -> bool:
    """Check if the repo has the ETS notes namespace."""
    result = _run_git(repo, ["notes", "--ref", NOTES_REF, "list"])
    return result is not None and len(result) > 0


def _get_commits_on_date(repo: str, date_str: str) -> List[str]:
    """Get commit SHAs for the target date."""
    out = _run_git(repo, [
        "log",
        f"--since={date_str}T00:00:00",
        f"--until={date_str}T23:59:59",
        "--format=%H",
        "--no-merges",
    ])
    if not out:
        return []
    return [sha.strip() for sha in out.split("\n") if sha.strip()]


def _read_note(repo: str, sha: str) -> Optional[Dict]:
    """Read a git note for a specific commit, return parsed JSON or None."""
    note_text = _run_git(repo, ["notes", "--ref", NOTES_REF, "show", sha])
    if not note_text:
        return None
    try:
        return json.loads(note_text)
    except json.JSONDecodeError:
        return None


def collect(date_str: str) -> CollectorResult:
    """Run the git notes collector for a target date.

    Scans all PROJECT_* repos for ETS signature notes on commits
    made on the target date.
    """
    all_events: List[DevJournalEvent] = []
    repos_checked = 0
    repos_with_notes = 0
    notes_found = 0

    if not PROJECTS_ROOT.is_dir():
        return CollectorResult(
            source=Source.GIT_NOTES,
            target_date=date_str,
            events=[],
            stats={"error": "PROJECTS_all not found"},
        )

    for d in sorted(PROJECTS_ROOT.iterdir()):
        if not d.name.startswith("PROJECT_") or not d.is_dir():
            continue
        if not (d / ".git").is_dir():
            continue

        repos_checked += 1

        if not _has_notes_ref(str(d)):
            continue

        repos_with_notes += 1
        commits = _get_commits_on_date(str(d), date_str)

        for sha in commits:
            note_data = _read_note(str(d), sha)
            if not note_data:
                continue

            notes_found += 1

            # Get commit timestamp
            ts_str = _run_git(str(d), ["log", "-1", "--format=%aI", sha])
            try:
                ts = datetime.fromisoformat(ts_str) if ts_str else datetime.now(timezone.utc)
            except ValueError:
                ts = datetime.now(timezone.utc)

            # Build Signature from note data
            signature = None
            if note_data.get("model"):
                signature = Signature(
                    model=note_data.get("model", "unknown"),
                    access_point=note_data.get("access_point", "unknown"),
                    orchestration=note_data.get("orchestration", "unknown"),
                    session_id=note_data.get("session_id"),
                    hostname=note_data.get("hostname", ""),
                )

            oid = generate_oid(ts, "git_notes", "git_note_added", f"{d.name}:{sha[:12]}")

            all_events.append(DevJournalEvent(
                oid=oid,
                ts=ts,
                source=Source.GIT_NOTES,
                kind=EventKind.GIT_NOTE_ADDED,
                project=d.name,
                data={
                    "sha": sha[:12],
                    "note_json": note_data,
                    "model": note_data.get("model"),
                    "access_point": note_data.get("access_point"),
                    "orchestration": note_data.get("orchestration"),
                },
                tags=["signature", note_data.get("model", "unknown")],
                signature=signature,
            ))

    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.GIT_NOTES,
        target_date=date_str,
        events=all_events,
        stats={
            "repos_checked": repos_checked,
            "repos_with_notes": repos_with_notes,
            "notes_found": notes_found,
        },
    )


if __name__ == "__main__":
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"Git notes collector: {len(result.events)} events")
    print(f"  Repos checked: {result.stats.get('repos_checked', 0)}")
    print(f"  Repos with notes: {result.stats.get('repos_with_notes', 0)}")
    print(f"  Notes found: {result.stats.get('notes_found', 0)}")
