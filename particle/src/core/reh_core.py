"""
REH Core — Repository Evolution History shared library.
========================================================
Single canonical source for constants and git utilities used by both
the Collider temporal analysis module (``temporal_analysis.py``) and
the REH MCP Server (``wave/tools/mcp/mcp_history_server.py``).

Governed by D9 (DECISIONS.md): REH has one shared core with two
access interfaces — batch analytics and interactive MCP tools.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Tuple

# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

NOISE_DIRS = {
    ".git", "node_modules", ".venv", ".tools_venv", "__pycache__",
    "dist", "build", ".repos_cache", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".next", ".cache", ".egg-info", "venv",
}

NOISE_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".png", ".jpg", ".zip", ".DS_Store",
}

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java",
    ".rb", ".sh", ".yaml", ".yml", ".toml", ".json", ".md",
}

CAPABILITY_PATTERNS = {
    "python": re.compile(
        r"^\s*(async\s+)?def\s+(\w+)|^\s*class\s+(\w+)"
    ),
    "javascript": re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)"
        r"|^\s*(?:export\s+)?class\s+(\w+)"
        r"|^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\("
    ),
    "go": re.compile(
        r"^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)"
        r"|^\s*type\s+(\w+)\s+struct"
    ),
}

LANG_BY_EXT = {
    ".py": "python", ".js": "javascript", ".ts": "javascript",
    ".tsx": "javascript", ".jsx": "javascript", ".go": "go",
}

# ────────────────────────────────────────────────
# Git helpers
# ────────────────────────────────────────────────

def _run_git(
    repo_path: str,
    args: list[str],
    max_output: int = 500_000,
    timeout: int = 30,
) -> Tuple[bool, str]:
    """Run a git command safely with output capping and timeout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout[:max_output]
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except FileNotFoundError:
        return False, "git not found on PATH"
    except Exception as e:
        return False, str(e)


def _is_git_repo(path: str) -> bool:
    """Check whether *path* is inside a git working tree."""
    if os.path.isdir(os.path.join(path, ".git")):
        return True
    # Could be a worktree or subdirectory
    ok, _ = _run_git(path, ["rev-parse", "--git-dir"])
    return ok


def _is_noise(path: str) -> bool:
    """Check if a file path should be excluded from analysis."""
    parts = path.split("/")
    if any(p in NOISE_DIRS for p in parts):
        return True
    _, ext = os.path.splitext(path)
    return ext in NOISE_EXTENSIONS


def _is_code_file(path: str) -> bool:
    """Check if a file path is a recognized code file."""
    _, ext = os.path.splitext(path)
    return ext in CODE_EXTENSIONS
