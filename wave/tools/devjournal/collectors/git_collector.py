"""
Git Collector — scans PROJECTS_all for repos with activity on target date.

Uses REH EvolutionCompiler for per-project temporal analysis,
then emits individual events (commit, file_born, milestone) to the ledger.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import sys
_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Source,
    PROJECTS_ROOT, generate_oid,
)


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


def _is_git_repo(path: Path) -> bool:
    return (path / ".git").is_dir()


def _find_active_repos(date_str: str) -> List[Path]:
    """Find all PROJECT_* repos that have commits on the target date."""
    active = []
    if not PROJECTS_ROOT.is_dir():
        return active
    for d in sorted(PROJECTS_ROOT.iterdir()):
        if not d.name.startswith("PROJECT_") or not d.is_dir():
            continue
        if not _is_git_repo(d):
            continue
        # Check if repo has commits on target date
        out = _run_git(str(d), [
            "log", "--oneline",
            f"--since={date_str}T00:00:00",
            f"--until={date_str}T23:59:59",
            "--max-count=1",
        ])
        if out:
            active.append(d)
    return active


def _collect_commits(repo: Path, date_str: str) -> List[DevJournalEvent]:
    """Collect commit events from a repo for the target date."""
    events = []
    project_name = repo.name

    # Get commits with full detail
    out = _run_git(str(repo), [
        "log",
        f"--since={date_str}T00:00:00",
        f"--until={date_str}T23:59:59",
        "--format=%H|%aI|%s",
        "--no-merges",
    ])
    if not out:
        return events

    for line in out.split("\n"):
        if "|" not in line:
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, ts_str, message = parts

        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError:
            ts = datetime.now(timezone.utc)

        # Get changed file count
        stat = _run_git(str(repo), ["diff", "--shortstat", f"{sha}^..{sha}"])
        files_changed = 0
        insertions = 0
        deletions = 0
        if stat:
            for part in stat.split(","):
                part = part.strip()
                if "file" in part:
                    files_changed = int(part.split()[0])
                elif "insertion" in part:
                    insertions = int(part.split()[0])
                elif "deletion" in part:
                    deletions = int(part.split()[0])

        oid = generate_oid(ts, "git", "commit", sha[:12])
        events.append(DevJournalEvent(
            oid=oid,
            ts=ts,
            source=Source.GIT,
            kind=EventKind.COMMIT,
            project=project_name,
            data={
                "sha": sha[:12],
                "message": message,
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
            },
        ))

    return events


def _collect_file_births(repo: Path, date_str: str) -> List[DevJournalEvent]:
    """Collect file birth events (new files added in commits)."""
    events = []
    project_name = repo.name

    out = _run_git(str(repo), [
        "log",
        "--diff-filter=A",
        f"--since={date_str}T00:00:00",
        f"--until={date_str}T23:59:59",
        "--format=%aI",
        "--name-only",
        "--no-merges",
    ])
    if not out:
        return events

    current_ts = None
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Try to parse as ISO timestamp
        try:
            current_ts = datetime.fromisoformat(line)
            continue
        except ValueError:
            pass
        # It's a filename
        if current_ts and not any(noise in line for noise in [
            "node_modules/", ".git/", "__pycache__/", ".next/",
            ".venv/", "dist/", "build/",
        ]):
            oid = generate_oid(current_ts, "git", "file_born", f"{project_name}:{line}")
            events.append(DevJournalEvent(
                oid=oid,
                ts=current_ts,
                source=Source.GIT,
                kind=EventKind.FILE_BORN,
                project=project_name,
                data={
                    "file": line,
                    "exists": (repo / line).exists(),
                },
            ))

    return events


def _detect_milestones(commits: List[DevJournalEvent], project_name: str) -> List[DevJournalEvent]:
    """Detect milestone events from commit patterns."""
    if len(commits) < 5:
        return []

    milestones = []
    total_files = sum(c.data.get("files_changed", 0) for c in commits)
    total_insertions = sum(c.data.get("insertions", 0) for c in commits)

    # High-activity day = milestone
    msgs = " ".join(c.data.get("message", "") for c in commits).lower()
    if "feat" in msgs or "add" in msgs:
        milestone_type = "capability_added"
    elif "refactor" in msgs or "rename" in msgs:
        milestone_type = "refactor"
    elif "fix" in msgs:
        milestone_type = "bugfix_wave"
    else:
        milestone_type = "major_change"

    ts = commits[-1].ts  # Use last commit timestamp
    oid = generate_oid(ts, "git", "milestone", f"{project_name}:{ts.strftime('%Y%m%d')}")
    milestones.append(DevJournalEvent(
        oid=oid,
        ts=ts,
        source=Source.GIT,
        kind=EventKind.MILESTONE,
        project=project_name,
        data={
            "type": milestone_type,
            "commit_count": len(commits),
            "files_changed": total_files,
            "insertions": total_insertions,
            "title": commits[0].data.get("message", ""),
        },
        tags=[milestone_type],
    ))
    return milestones


def collect(date_str: str) -> CollectorResult:
    """Run the git collector for a target date.

    Args:
        date_str: Target date in YYYY-MM-DD format.

    Returns:
        CollectorResult with all git events for the day.
    """
    all_events: List[DevJournalEvent] = []
    repos = _find_active_repos(date_str)
    projects_found = []

    for repo in repos:
        commits = _collect_commits(repo, date_str)
        file_births = _collect_file_births(repo, date_str)
        milestones = _detect_milestones(commits, repo.name)
        all_events.extend(commits)
        all_events.extend(file_births)
        all_events.extend(milestones)
        if commits:
            projects_found.append(repo.name)

    # Sort by timestamp
    all_events.sort(key=lambda e: e.ts)

    return CollectorResult(
        source=Source.GIT,
        target_date=date_str,
        events=all_events,
        stats={
            "repos_scanned": len(repos),
            "projects_active": projects_found,
            "total_commits": sum(1 for e in all_events if e.kind == EventKind.COMMIT),
            "total_file_births": sum(1 for e in all_events if e.kind == EventKind.FILE_BORN),
            "total_milestones": sum(1 for e in all_events if e.kind == EventKind.MILESTONE),
        },
    )


if __name__ == "__main__":
    import json
    from datetime import date
    target = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    result = collect(target)
    print(f"Git collector: {len(result.events)} events from {result.stats.get('repos_scanned', 0)} repos")
    print(f"  Active: {result.stats.get('projects_active', [])}")
    print(f"  Commits: {result.stats.get('total_commits', 0)}")
    print(f"  File births: {result.stats.get('total_file_births', 0)}")
    print(f"  Milestones: {result.stats.get('total_milestones', 0)}")
