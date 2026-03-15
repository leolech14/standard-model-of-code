"""Smoke tests for the REH MCP Server (mcp_history_server.py).

Verifies:
1. Shared constants match reh_core (import identity)
2. Tool functions are callable with mocked git
3. Error handling for invalid inputs
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
# Add MCP server path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "wave" / "tools" / "mcp"))

# Mock the mcp package if not installed (MCP server depends on fastmcp)
if "mcp" not in sys.modules:
    _mock_mcp = types.ModuleType("mcp")
    _mock_server = types.ModuleType("mcp.server")
    _mock_fastmcp = types.ModuleType("mcp.server.fastmcp")

    class _MockFastMCP:
        def __init__(self, *a, **kw):
            pass
        def tool(self):
            def decorator(fn):
                return fn
            return decorator
        def run(self, **kw):
            pass

    _mock_fastmcp.FastMCP = _MockFastMCP
    _mock_mcp.server = _mock_server
    _mock_server.fastmcp = _mock_fastmcp
    sys.modules["mcp"] = _mock_mcp
    sys.modules["mcp.server"] = _mock_server
    sys.modules["mcp.server.fastmcp"] = _mock_fastmcp

from reh_core import (
    NOISE_DIRS as CORE_NOISE_DIRS,
    CODE_EXTENSIONS as CORE_CODE_EXTENSIONS,
    CAPABILITY_PATTERNS as CORE_CAPABILITY_PATTERNS,
    LANG_BY_EXT as CORE_LANG_BY_EXT,
)
from mcp_history_server import (
    NOISE_DIRS,
    CODE_EXTENSIONS,
    CAPABILITY_PATTERNS,
    LANG_BY_EXT,
    get_repo_history,
    search_code_changes,
    get_file_history,
    detect_capability_changes,
    get_directory_activity,
    _validate_repo,
)


# ── Import identity tests ──────────────────────────────────────────────────

class TestSharedConstants:
    """Verify MCP server constants match reh_core values (D9)."""

    def test_noise_dirs_equal(self):
        assert NOISE_DIRS == CORE_NOISE_DIRS

    def test_code_extensions_equal(self):
        assert CODE_EXTENSIONS == CORE_CODE_EXTENSIONS

    def test_capability_patterns_keys_equal(self):
        assert set(CAPABILITY_PATTERNS.keys()) == set(CORE_CAPABILITY_PATTERNS.keys())

    def test_lang_by_ext_equal(self):
        assert LANG_BY_EXT == CORE_LANG_BY_EXT


# ── Validation tests ───────────────────────────────────────────────────────

class TestValidateRepo:
    def test_nonexistent_dir(self):
        ok, msg = _validate_repo("/nonexistent/path/xyz")
        assert not ok
        assert "not found" in msg.lower()

    def test_not_a_git_repo(self, tmp_path):
        ok, msg = _validate_repo(str(tmp_path))
        assert not ok
        assert "not a git" in msg.lower()

    def test_valid_repo(self, tmp_path):
        (tmp_path / ".git").mkdir()
        ok, msg = _validate_repo(str(tmp_path))
        assert ok
        assert msg == ""


# ── Tool invocation tests ─────────────────────────────────────────────────

class TestGetRepoHistory:
    @patch("mcp_history_server._run_git")
    @patch("mcp_history_server._validate_repo")
    def test_basic_call(self, mock_validate, mock_git):
        mock_validate.return_value = (True, "")
        mock_git.return_value = (True, "2026-03-14 abc1234 feat: add thing\n")
        result = json.loads(get_repo_history("/fake/repo", limit=5))
        assert "days" in result
        assert result["repo"] == "/fake/repo"

    @patch("mcp_history_server._validate_repo")
    def test_invalid_repo(self, mock_validate):
        mock_validate.return_value = (False, "not found")
        result = json.loads(get_repo_history("/bad/path"))
        assert "error" in result


class TestDetectCapabilityChanges:
    @patch("mcp_history_server._run_git")
    @patch("mcp_history_server._validate_repo")
    def test_basic_call(self, mock_validate, mock_git):
        mock_validate.return_value = (True, "")
        # First call: diff --name-status, second+: show file contents
        mock_git.side_effect = [
            (True, "M\tsrc/main.py\n"),  # diff --name-status
            (True, "def old_func():\n    pass\n"),  # show before
            (True, "def new_func():\n    pass\n"),  # show after
        ]
        result = json.loads(detect_capability_changes("/fake/repo"))
        assert "capabilities_added" in result
        assert "capabilities_removed" in result

    @patch("mcp_history_server._validate_repo")
    def test_invalid_repo(self, mock_validate):
        mock_validate.return_value = (False, "not found")
        result = json.loads(detect_capability_changes("/bad/path"))
        assert "error" in result


class TestSearchCodeChanges:
    @patch("mcp_history_server._validate_repo")
    def test_invalid_repo(self, mock_validate):
        mock_validate.return_value = (False, "not found")
        result = json.loads(search_code_changes("/bad/path", "def foo"))
        assert "error" in result


class TestGetFileHistory:
    @patch("mcp_history_server._validate_repo")
    def test_invalid_repo(self, mock_validate):
        mock_validate.return_value = (False, "not found")
        result = json.loads(get_file_history("/bad/path", "main.py"))
        assert "error" in result


class TestGetDirectoryActivity:
    @patch("mcp_history_server._validate_repo")
    def test_invalid_repo(self, mock_validate):
        mock_validate.return_value = (False, "not found")
        result = json.loads(get_directory_activity("/bad/path", "src/"))
        assert "error" in result
