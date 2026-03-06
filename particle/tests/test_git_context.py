"""Tests for the Git Context module (repo identity + worktree topology)."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from git_context import (
    GitContextResult,
    WorktreeEntry,
    _build_worktree_entry,
    _get_remote,
    _get_repo_identity,
    _get_worktree_topology,
    _parse_worktrees,
    compute_git_context,
)


# ── Worktree porcelain parsing ──────────────────────────────────────────


PORCELAIN_MAIN_ONLY = """\
worktree /home/user/repo
HEAD abc1234567890abcdef1234567890abcdef12345678
branch refs/heads/main

"""

PORCELAIN_MAIN_PLUS_LINKED = """\
worktree /home/user/repo
HEAD abc1234567890abcdef1234567890abcdef12345678
branch refs/heads/main

worktree /home/user/repo/.claude/worktrees/feature-x
HEAD def4567890abcdef1234567890abcdef1234567890ab
branch refs/heads/feature-x
gitdir /home/user/repo/.git/worktrees/feature-x

"""

PORCELAIN_BARE = """\
worktree /home/user/repo.git
HEAD abc1234567890abcdef1234567890abcdef12345678
bare

"""

PORCELAIN_DETACHED = """\
worktree /home/user/repo
HEAD abc1234567890abcdef1234567890abcdef12345678
detached

"""

PORCELAIN_LOCKED = """\
worktree /home/user/repo
HEAD abc1234567890abcdef1234567890abcdef12345678
branch refs/heads/main

worktree /tmp/locked-tree
HEAD def4567890abcdef1234567890abcdef1234567890ab
branch refs/heads/locked-branch
locked
gitdir /home/user/repo/.git/worktrees/locked-tree

"""


class TestParseWorktrees:
    def test_single_main_worktree(self):
        entries = _parse_worktrees(PORCELAIN_MAIN_ONLY)
        assert len(entries) == 1
        wt = entries[0]
        assert wt.path == "/home/user/repo"
        assert wt.branch == "refs/heads/main"
        assert wt.branch_short == "main"
        assert wt.is_main is True
        assert wt.is_bare is False
        assert wt.is_detached is False

    def test_main_plus_linked(self):
        entries = _parse_worktrees(PORCELAIN_MAIN_PLUS_LINKED)
        assert len(entries) == 2
        main = entries[0]
        linked = entries[1]
        assert main.is_main is True
        assert linked.is_main is False
        assert linked.branch_short == "feature-x"
        assert linked.gitdir == "/home/user/repo/.git/worktrees/feature-x"

    def test_bare_worktree(self):
        entries = _parse_worktrees(PORCELAIN_BARE)
        assert len(entries) == 1
        assert entries[0].is_bare is True
        assert entries[0].branch == ""
        assert entries[0].branch_short == ""

    def test_detached_head(self):
        entries = _parse_worktrees(PORCELAIN_DETACHED)
        assert len(entries) == 1
        assert entries[0].is_detached is True

    def test_locked_worktree(self):
        entries = _parse_worktrees(PORCELAIN_LOCKED)
        assert len(entries) == 2
        locked = entries[1]
        assert locked.is_locked is True
        assert locked.branch_short == "locked-branch"

    def test_empty_output(self):
        assert _parse_worktrees("") == []
        assert _parse_worktrees("   ") == []
        assert _parse_worktrees("\n\n") == []


# ── Worktree topology ──────────────────────────────────────────────────


class TestGetWorktreeTopology:
    @patch("git_context._run_git")
    def test_git_fails_returns_not_worktree(self, mock_git):
        mock_git.return_value = (False, "error")
        is_linked, main_path, worktrees = _get_worktree_topology("/repo")
        assert is_linked is False
        assert worktrees == []

    @patch("git_context._run_git")
    def test_main_is_not_linked(self, mock_git):
        mock_git.return_value = (True, PORCELAIN_MAIN_ONLY)
        is_linked, main_path, worktrees = _get_worktree_topology("/home/user/repo")
        assert is_linked is False
        assert len(worktrees) == 1

    @patch("git_context._run_git")
    def test_linked_worktree_detected(self, mock_git):
        mock_git.return_value = (True, PORCELAIN_MAIN_PLUS_LINKED)
        # Scanning from the linked worktree path
        is_linked, main_path, worktrees = _get_worktree_topology(
            "/home/user/repo/.claude/worktrees/feature-x"
        )
        assert is_linked is True
        assert main_path == "/home/user/repo"
        assert len(worktrees) == 2


# ── Full compute_git_context ───────────────────────────────────────────


class TestComputeGitContext:
    def test_no_path_returns_unavailable(self):
        result = compute_git_context(repo_path=None, full_output=None)
        assert result.available is False
        assert result.error == "no repo path available"

    def test_empty_path_returns_unavailable(self):
        result = compute_git_context(repo_path="")
        assert result.available is False
        assert result.error == "no repo path available"

    @patch("git_context._is_git_repo", return_value=False)
    def test_non_repo_returns_unavailable(self, mock_is_repo):
        result = compute_git_context(repo_path="/tmp/not-a-repo")
        assert result.available is False
        assert result.error == "not a git repository"

    @patch("git_context._run_git")
    @patch("git_context._is_git_repo", return_value=True)
    def test_clean_repo(self, mock_is_repo, mock_git):
        def side_effect(repo_path, args, **kwargs):
            cmd = " ".join(args)
            if cmd == "rev-parse HEAD":
                return True, "abc1234567890abcdef1234567890abcdef12345678\n"
            if cmd == "rev-parse --abbrev-ref HEAD":
                return True, "main\n"
            if cmd == "rev-parse --symbolic-full-name HEAD":
                return True, "refs/heads/main\n"
            if cmd == "status --porcelain":
                return True, "\n"
            if cmd == "remote -v":
                return True, "origin\tgit@github.com:org/repo.git (fetch)\norigin\tgit@github.com:org/repo.git (push)\n"
            if "worktree" in cmd:
                return True, PORCELAIN_MAIN_ONLY
            return False, ""

        mock_git.side_effect = side_effect
        result = compute_git_context(repo_path="/home/user/repo")

        assert result.available is True
        assert result.commit == "abc1234"
        assert result.branch == "main"
        assert result.dirty is False
        assert result.dirty_file_count == 0
        assert result.remote_url == "git@github.com:org/repo.git"
        assert result.is_worktree is False
        assert "clean" in result.summary
        assert "origin:github.com/org/repo" in result.summary

    @patch("git_context._run_git")
    @patch("git_context._is_git_repo", return_value=True)
    def test_dirty_linked_worktree(self, mock_is_repo, mock_git):
        def side_effect(repo_path, args, **kwargs):
            cmd = " ".join(args)
            if cmd == "rev-parse HEAD":
                return True, "def4567890abcdef1234567890abcdef1234567890ab\n"
            if cmd == "rev-parse --abbrev-ref HEAD":
                return True, "feature-x\n"
            if cmd == "rev-parse --symbolic-full-name HEAD":
                return True, "refs/heads/feature-x\n"
            if cmd == "status --porcelain":
                return True, " M src/foo.py\n M src/bar.py\n"
            if cmd == "remote -v":
                return True, "origin\tgit@github.com:org/repo.git (fetch)\n"
            if "worktree" in cmd:
                return True, PORCELAIN_MAIN_PLUS_LINKED
            return False, ""

        mock_git.side_effect = side_effect
        result = compute_git_context(
            repo_path="/home/user/repo/.claude/worktrees/feature-x"
        )

        assert result.available is True
        assert result.branch == "feature-x"
        assert result.dirty is True
        assert result.dirty_file_count == 2
        assert result.is_worktree is True
        assert result.worktree_count == 2
        assert "[linked-worktree off main]" in result.summary
        assert "dirty, 2 files" in result.summary
        assert "origin:github.com/org/repo" in result.summary

    @patch("git_context._run_git")
    @patch("git_context._is_git_repo", return_value=True)
    def test_detached_head(self, mock_is_repo, mock_git):
        def side_effect(repo_path, args, **kwargs):
            cmd = " ".join(args)
            if cmd == "rev-parse HEAD":
                return True, "abc1234567890abcdef1234567890abcdef12345678\n"
            if cmd == "rev-parse --abbrev-ref HEAD":
                return True, "HEAD\n"
            if cmd == "rev-parse --symbolic-full-name HEAD":
                return True, "HEAD\n"
            if cmd == "status --porcelain":
                return True, "\n"
            if cmd == "remote -v":
                return True, ""
            if "worktree" in cmd:
                return True, PORCELAIN_DETACHED
            return False, ""

        mock_git.side_effect = side_effect
        result = compute_git_context(repo_path="/home/user/repo")

        assert result.is_detached is True
        assert result.summary.startswith("DETACHED@abc1234")
        assert "detached" in result.summary
        # No remote — summary should not contain "origin:"
        assert "origin:" not in result.summary

    def test_json_serializable(self):
        result = GitContextResult(
            available=True,
            commit="abc1234",
            branch="main",
            worktrees=[
                WorktreeEntry(path="/repo", head="abc123", is_main=True),
            ],
        )
        d = result.to_dict()
        serialized = json.dumps(d)
        assert '"abc1234"' in serialized
        roundtrip = json.loads(serialized)
        assert roundtrip["commit"] == "abc1234"
        assert len(roundtrip["worktrees"]) == 1

    @patch("git_context._is_git_repo", return_value=True)
    @patch("git_context._run_git", return_value=(False, "error"))
    def test_git_commands_fail_gracefully(self, mock_git, mock_is_repo):
        """All git calls fail but no exception — returns available with empty fields."""
        result = compute_git_context(repo_path="/repo")
        assert result.available is True
        assert result.commit == ""
        assert result.branch == ""
        assert result.dirty is False
