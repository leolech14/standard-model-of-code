"""
Git Context Module
==================
Repo identity + worktree topology for Collider output.

Adds ``git_context`` as a first-class data section following the exact
``temporal_analysis`` pattern: dataclass result, ``available: bool``,
graceful degradation, zero-crash guarantee.

AI tools consuming Collider output can now tell:
- Which branch / commit produced the analysis
- Whether the working tree is dirty
- Whether the scan ran from a linked worktree vs the main checkout
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


# ────────────────────────────────────────────────
# Git helpers (from REH shared core)
# ────────────────────────────────────────────────
# Local wrappers so tests can @patch("src.core.git_context._run_git")
# without touching reh_core or temporal_analysis.

def _run_git(
    repo_path: str,
    args: list[str],
    max_output: int = 500_000,
    timeout: int = 30,
) -> Tuple[bool, str]:
    """Run a git command safely with output capping and timeout."""
    from src.core.reh_core import _run_git as _reh_run_git
    return _reh_run_git(repo_path, args, max_output=max_output, timeout=timeout)


def _is_git_repo(path: str) -> bool:
    """Check whether *path* is inside a git working tree."""
    from src.core.reh_core import _is_git_repo as _reh_is_git_repo
    return _reh_is_git_repo(path)


# ────────────────────────────────────────────────
# Result dataclasses
# ────────────────────────────────────────────────

@dataclass
class WorktreeEntry:
    """One record from ``git worktree list --porcelain``."""
    path: str = ""
    head: str = ""
    branch: str = ""          # refs/heads/main
    branch_short: str = ""    # main
    is_main: bool = False
    is_bare: bool = False
    is_detached: bool = False
    is_locked: bool = False
    gitdir: str = ""


@dataclass
class GitContextResult:
    """Full git context for the Collider pipeline."""
    available: bool = False
    error: Optional[str] = None

    # Repo identity
    commit: str = ""
    commit_full: str = ""
    branch: str = ""
    branch_full: str = ""     # refs/heads/main
    is_detached: bool = False
    dirty: bool = False
    dirty_file_count: int = 0

    # Remote
    remote_url: str = ""
    remote_name: str = ""

    # Worktree topology
    is_worktree: bool = False
    main_worktree_path: str = ""
    worktrees: List[WorktreeEntry] = field(default_factory=list)
    worktree_count: int = 0

    # Summary
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ────────────────────────────────────────────────
# Private helpers
# ────────────────────────────────────────────────

def _get_repo_identity(repo_path: str) -> dict:
    """Collect commit, branch, dirty state via four git calls."""
    identity: dict = {
        "commit": "",
        "commit_full": "",
        "branch": "",
        "branch_full": "",
        "is_detached": False,
        "dirty": False,
        "dirty_file_count": 0,
    }

    # Full commit SHA
    ok, out = _run_git(repo_path, ["rev-parse", "HEAD"])
    if ok:
        identity["commit_full"] = out.strip()
        identity["commit"] = out.strip()[:7]

    # Short branch name
    ok, out = _run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
    if ok:
        branch = out.strip()
        identity["branch"] = branch
        identity["is_detached"] = branch == "HEAD"

    # Full symbolic ref
    ok, out = _run_git(repo_path, ["rev-parse", "--symbolic-full-name", "HEAD"])
    if ok:
        identity["branch_full"] = out.strip()

    # Dirty state
    ok, out = _run_git(repo_path, ["status", "--porcelain"])
    if ok:
        dirty_lines = [l for l in out.strip().split("\n") if l.strip()]
        identity["dirty"] = len(dirty_lines) > 0
        identity["dirty_file_count"] = len(dirty_lines)

    return identity


def _get_remote(repo_path: str) -> dict:
    """Get primary remote name and URL."""
    remote: dict = {"remote_name": "", "remote_url": ""}

    ok, out = _run_git(repo_path, ["remote", "-v"])
    if not ok or not out.strip():
        return remote

    # Parse first fetch line: "origin\tgit@github.com:org/repo.git (fetch)"
    for line in out.strip().split("\n"):
        if "(fetch)" in line:
            parts = line.split()
            if len(parts) >= 2:
                remote["remote_name"] = parts[0]
                remote["remote_url"] = parts[1]
            break

    return remote


def _parse_worktrees(output: str) -> List[WorktreeEntry]:
    """Parse ``git worktree list --porcelain`` output.

    Porcelain format: blocks separated by blank lines.
    Each block has lines like ``worktree /path``, ``HEAD abc123``,
    ``branch refs/heads/main``, optionally ``bare``, ``detached``,
    ``locked``.  The main worktree has no ``gitdir`` line.
    """
    if not output or not output.strip():
        return []

    entries: List[WorktreeEntry] = []
    current: dict = {}

    for line in output.split("\n"):
        line = line.rstrip()

        if not line:
            # Block separator — flush current entry
            if current:
                entries.append(_build_worktree_entry(current))
                current = {}
            continue

        if line.startswith("worktree "):
            current["path"] = line[len("worktree "):]
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):]
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True
        elif line.startswith("locked"):
            current["locked"] = True
        elif line.startswith("gitdir "):
            current["gitdir"] = line[len("gitdir "):]

    # Flush last block
    if current:
        entries.append(_build_worktree_entry(current))

    return entries


def _build_worktree_entry(raw: dict) -> WorktreeEntry:
    """Convert a raw parsed dict into a WorktreeEntry."""
    branch = raw.get("branch", "")
    branch_short = branch.rsplit("/", 1)[-1] if branch else ""

    return WorktreeEntry(
        path=raw.get("path", ""),
        head=raw.get("head", ""),
        branch=branch,
        branch_short=branch_short,
        is_main="gitdir" not in raw,
        is_bare=raw.get("bare", False),
        is_detached=raw.get("detached", False),
        is_locked=raw.get("locked", False),
        gitdir=raw.get("gitdir", ""),
    )


def _get_worktree_topology(repo_path: str) -> Tuple[bool, str, List[WorktreeEntry]]:
    """Determine worktree topology.

    Returns (is_worktree, main_worktree_path, worktree_list).
    """
    ok, out = _run_git(repo_path, ["worktree", "list", "--porcelain"])
    if not ok:
        return False, repo_path, []

    worktrees = _parse_worktrees(out)
    if not worktrees:
        return False, repo_path, []

    # Find the main worktree (the one without a gitdir field)
    main_path = ""
    for wt in worktrees:
        if wt.is_main:
            main_path = wt.path
            break

    if not main_path and worktrees:
        main_path = worktrees[0].path

    # Am I a linked worktree? Compare resolved paths.
    resolved_repo = str(Path(repo_path).resolve())
    resolved_main = str(Path(main_path).resolve()) if main_path else ""
    is_linked = resolved_repo != resolved_main and len(worktrees) > 1

    return is_linked, main_path, worktrees


# ────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────

def compute_git_context(
    repo_path: Optional[str] = None,
    full_output: Optional[dict] = None,
) -> GitContextResult:
    """Compute full git context for the Collider pipeline.

    Follows the ``compute_temporal_analysis`` pattern exactly:
    1. Resolve repo_path (from arg or full_output metadata)
    2. If no path -> ``available=False``
    3. If not git repo -> ``available=False``
    4. Collect identity, remote, worktree topology
    5. Build summary string
    6. Return populated result
    """
    result = GitContextResult()

    # Resolve repo path
    if repo_path is None and full_output is not None:
        metadata = full_output.get("metadata", {})
        repo_path = metadata.get("target_path", "")
    if not repo_path:
        result.error = "no repo path available"
        return result

    repo_path = str(Path(repo_path).resolve())

    if not _is_git_repo(repo_path):
        result.error = "not a git repository"
        return result

    result.available = True

    # Repo identity
    identity = _get_repo_identity(repo_path)
    result.commit = identity["commit"]
    result.commit_full = identity["commit_full"]
    result.branch = identity["branch"]
    result.branch_full = identity["branch_full"]
    result.is_detached = identity["is_detached"]
    result.dirty = identity["dirty"]
    result.dirty_file_count = identity["dirty_file_count"]

    # Remote
    remote = _get_remote(repo_path)
    result.remote_name = remote["remote_name"]
    result.remote_url = remote["remote_url"]

    # Worktree topology
    is_linked, main_path, worktrees = _get_worktree_topology(repo_path)
    result.is_worktree = is_linked
    result.main_worktree_path = main_path
    result.worktrees = worktrees
    result.worktree_count = len(worktrees)

    # Build summary — must answer at a glance:
    #   What branch? What commit? Dirty? Detached? Worktree? Where from?
    # Examples:
    #   "main@40b2227 (clean) origin:github.com/org/repo"
    #   "feature-x@def4567 (dirty, 17 files) [linked-worktree off main] origin:github.com/org/repo"
    #   "DETACHED@abc1234 (clean)"
    parts = []

    # Branch + commit
    branch_label = "DETACHED" if result.is_detached else result.branch
    parts.append(f"{branch_label}@{result.commit}")

    # Status parenthetical
    extras = []
    if result.is_detached:
        extras.append("detached")
    if result.dirty:
        extras.append(f"dirty, {result.dirty_file_count} file{'s' if result.dirty_file_count != 1 else ''}")
    else:
        extras.append("clean")
    if result.worktree_count > 1:
        extras.append(f"{result.worktree_count} worktrees")
    parts.append(f"({', '.join(extras)})")

    # Worktree context — which branch is main?
    if result.is_worktree:
        main_branch = ""
        for wt in result.worktrees:
            if wt.is_main and wt.branch_short:
                main_branch = wt.branch_short
                break
        if main_branch:
            parts.append(f"[linked-worktree off {main_branch}]")
        else:
            parts.append("[linked-worktree]")

    # Remote origin — strip protocol noise, keep host+path
    if result.remote_url:
        url = result.remote_url
        # Normalize to host:path form
        for prefix in ("https://", "http://", "git@", "ssh://git@", "ssh://"):
            if url.startswith(prefix):
                url = url[len(prefix):]
                break
        url = url.rstrip("/")
        if url.endswith(".git"):
            url = url[:-4]
        # git@github.com:org/repo → github.com/org/repo
        url = url.replace(":", "/", 1) if ":" in url and "/" not in url.split(":")[0] else url
        parts.append(f"{result.remote_name}:{url}")

    result.summary = " ".join(parts)

    return result
