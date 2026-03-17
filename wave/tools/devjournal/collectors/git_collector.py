"""
Git Trace Collector — scans PROJECTS_all for repos with activity on target date.

Extracts commits, file births, and milestones. Parses ETS Signature Protocol
trailers (Agent-Model, Agent-Access, Agent-Orchestration, Agent-Session) from
commit messages to populate Signature provenance blocks.
"""

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import sys
_devjournal = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_devjournal))
from schema import (
    CollectorResult, DevJournalEvent, EventKind, Signature, Source,
    PROJECTS_ROOT, generate_oid,
)


# ── Signature Protocol trailer keys ─────────────────────

TRAILER_MAP = {
    "Agent-Model": "model",
    "Agent-Access": "access_point",
    "Agent-Orchestration": "orchestration",
    "Agent-Session": "session_id",
}

# ── Conventional commit prefix patterns for milestone detection ──

FEAT_PATTERNS = re.compile(r"^(feat|add|implement|create|build|launch|new)\b", re.IGNORECASE)
FIX_PATTERNS = re.compile(r"^(fix|bugfix|hotfix|patch|repair)\b", re.IGNORECASE)
REFACTOR_PATTERNS = re.compile(r"^(refactor|rename|restructure|reorganize|simplify|clean)\b", re.IGNORECASE)
DOCS_PATTERNS = re.compile(r"^(docs|doc|document|spec|plan)\b", re.IGNORECASE)
INFRA_PATTERNS = re.compile(r"^(ci|cd|deploy|infra|ops|build|chore)\b", re.IGNORECASE)

# Milestone threshold: any project meeting ONE of these qualifies
MILESTONE_THRESHOLDS = {
    "min_commits": 3,          # lowered from 5
    "min_insertions": 500,     # significant code volume
    "min_files": 10,           # broad change
    "min_feat_commits": 2,     # multiple features in a day
}


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


def _parse_trailers(repo: str, sha: str) -> Optional[Signature]:
    """Parse ETS Signature Protocol trailers from a commit message."""
    body = _run_git(repo, ["log", "-1", "--format=%b", sha])
    if not body:
        return None

    sig_fields: Dict[str, str] = {}
    for line in body.split("\n"):
        line = line.strip()
        for trailer_key, sig_key in TRAILER_MAP.items():
            if line.startswith(f"{trailer_key}:"):
                value = line[len(trailer_key) + 1:].strip()
                if value:
                    sig_fields[sig_key] = value

    if not sig_fields:
        return None

    # Also check Co-Authored-By for model hints
    for line in body.split("\n"):
        if "Co-Authored-By:" in line and "Claude" in line and "model" not in sig_fields:
            sig_fields["model"] = "claude"
            if "access_point" not in sig_fields:
                sig_fields["access_point"] = "cli"
            if "orchestration" not in sig_fields:
                sig_fields["orchestration"] = "direct"

    if not sig_fields.get("model"):
        return None

    return Signature(
        model=sig_fields.get("model", "unknown"),
        access_point=sig_fields.get("access_point", "unknown"),
        orchestration=sig_fields.get("orchestration", "unknown"),
        session_id=sig_fields.get("session_id"),
        hostname="",
    )


def _classify_commit(message: str) -> str:
    """Classify a commit message by conventional commit type."""
    # Strip scope: "feat(refinery):" -> "feat"
    clean = re.sub(r"^(\w+)\(.*?\):\s*", r"\1: ", message)

    if FEAT_PATTERNS.search(clean):
        return "feat"
    if FIX_PATTERNS.search(clean):
        return "fix"
    if REFACTOR_PATTERNS.search(clean):
        return "refactor"
    if DOCS_PATTERNS.search(clean):
        return "docs"
    if INFRA_PATTERNS.search(clean):
        return "infra"
    return "other"


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

        # Parse shortstat
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

        # Parse Signature Protocol trailers
        signature = _parse_trailers(str(repo), sha)

        # Classify commit type
        commit_type = _classify_commit(message)

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
                "commit_type": commit_type,
            },
            tags=[commit_type],
            signature=signature,
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
        try:
            current_ts = datetime.fromisoformat(line)
            continue
        except ValueError:
            pass
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
    """Detect milestones using semantic analysis of commit patterns.

    A milestone is detected when a project's daily activity meets any of:
    - 3+ commits (sustained work)
    - 500+ insertions (significant volume)
    - 10+ files changed (broad scope)
    - 2+ feat commits (multiple capabilities added)

    Milestones are classified by dominant commit type and tagged with
    all commit types present in the day's work.
    """
    if not commits:
        return []

    total_commits = len(commits)
    total_insertions = sum(c.data.get("insertions", 0) for c in commits)
    total_files = sum(c.data.get("files_changed", 0) for c in commits)

    # Count by type
    type_counts: Dict[str, int] = {}
    for c in commits:
        ct = c.data.get("commit_type", "other")
        type_counts[ct] = type_counts.get(ct, 0) + 1

    feat_count = type_counts.get("feat", 0)

    # Check if ANY threshold is met
    qualifies = (
        total_commits >= MILESTONE_THRESHOLDS["min_commits"]
        or total_insertions >= MILESTONE_THRESHOLDS["min_insertions"]
        or total_files >= MILESTONE_THRESHOLDS["min_files"]
        or feat_count >= MILESTONE_THRESHOLDS["min_feat_commits"]
    )

    if not qualifies:
        return []

    # Determine dominant type
    if feat_count > 0:
        milestone_type = "capability_added"
    elif type_counts.get("fix", 0) > type_counts.get("refactor", 0):
        milestone_type = "bugfix_wave"
    elif type_counts.get("refactor", 0) > 0:
        milestone_type = "refactor"
    elif type_counts.get("docs", 0) > 0:
        milestone_type = "documentation"
    elif type_counts.get("infra", 0) > 0:
        milestone_type = "infrastructure"
    else:
        milestone_type = "major_change"

    # Build descriptive title from feat commits, or first commit
    feat_msgs = [c.data.get("message", "") for c in commits if c.data.get("commit_type") == "feat"]
    if feat_msgs:
        title = feat_msgs[0]
        if len(feat_msgs) > 1:
            title += f" (+{len(feat_msgs) - 1} more features)"
    else:
        title = commits[0].data.get("message", "")

    # Tags: all commit types present + milestone type
    tags = list(set([milestone_type] + list(type_counts.keys())))

    ts = commits[-1].ts
    oid = generate_oid(ts, "git", "milestone", f"{project_name}:{ts.strftime('%Y%m%d')}")

    return [DevJournalEvent(
        oid=oid,
        ts=ts,
        source=Source.GIT,
        kind=EventKind.MILESTONE,
        project=project_name,
        data={
            "type": milestone_type,
            "commit_count": total_commits,
            "files_changed": total_files,
            "insertions": total_insertions,
            "deletions": sum(c.data.get("deletions", 0) for c in commits),
            "title": title,
            "commit_types": type_counts,
            "has_signature": any(c.signature is not None for c in commits),
        },
        tags=tags,
    )]


def collect(date_str: str) -> CollectorResult:
    """Run the git trace collector for a target date."""
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
            "signed_commits": sum(1 for e in all_events if e.kind == EventKind.COMMIT and e.signature),
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
    print(f"  Signed: {result.stats.get('signed_commits', 0)}")
    print(f"  File births: {result.stats.get('total_file_births', 0)}")
    print(f"  Milestones: {result.stats.get('total_milestones', 0)}")
