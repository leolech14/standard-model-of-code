"""
Context Module - File Collection and Context Building
======================================================

Standard Model Classification:
-----------------------------
D1_KIND:     LOG.FNC.M (Logic Function Module)
D2_LAYER:    Application (orchestrates file operations)
D3_ROLE:     Builder (constructs context from parts)
D4_BOUNDARY: I-O (reads files, produces string output)
D5_STATE:    Stateless (pure functions)
D6_EFFECT:   Impure (file system reads)
D7_LIFECYCLE: Use (called during analysis)
D8_TRUST:    90 (well-tested, some edge cases)

RPBL: (3, 4, 4, 1)
    R=3: Three responsibilities (list, filter, build) - could split
    P=4: File I/O but no mutations
    B=4: File system boundary
    L=1: Ephemeral - no persistent state

Communication Theory:
    Source:   File system
    Channel:  File I/O
    Message:  Context string (bundled file contents)
    Receiver: LLM models
    Noise:    Binary files, encoding errors (filtered)
    Redundancy: Critical files front-loaded

Tool Theory:
    Universe: TOOLOME (shapes what model sees)
    Role:     T-Transformer (transforms files to prompt)
    Stone Tool Test: FAIL (output is AI-native prompt format)
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple, Set


def list_local_files(
    base_dir: Path,
    patterns: Optional[List[str]] = None,
    user_excludes: Optional[List[str]] = None
) -> List[Path]:
    """
    List files from local filesystem matching patterns.

    Includes security-sensitive exclusions by default to prevent secret leakage.
    This is a critical security boundary.

    Args:
        base_dir: Base directory to search
        patterns: Glob patterns to include (None = all files)
        user_excludes: Additional patterns to exclude

    Returns:
        List of file paths, sorted for deterministic output
    """
    base_path = Path(base_dir)
    all_files = []

    # SECURITY: Default excludes - prevents secret leakage
    # This is the noise filter in Communication Theory terms
    default_excludes = [
        # Secrets and credentials
        ".env", ".env.*", "*.env", ".envrc",
        "*.key", "*.pem", "*.p12", "*.pfx", "*.crt",
        "credentials*", "secrets*", "*secret*",
        ".gcloud", ".aws", ".ssh",
        "service-account*.json", "*-credentials.json",

        # Build artifacts and caches
        "*.DS_Store", "__pycache__", "*.pyc", "*.pyo",
        ".git", "node_modules", ".npm", ".yarn",
        "*.zip", "*.tar", "*.gz", "*.rar",
        "*.lock", "package-lock.json", "yarn.lock",
        ".tools_venv", ".venv", "venv", "*.egg-info",

        # Binary files
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.webp",
        "*.mp3", "*.mp4", "*.wav", "*.avi",
        "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx",
        "*.so", "*.dylib", "*.dll", "*.exe",

        # IDE and editor
        ".idea", ".vscode", "*.swp", "*.swo",
    ]
    excludes = default_excludes + (user_excludes or [])

    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded."""
        name = path.name
        try:
            rel_path = str(path.relative_to(base_path))
        except ValueError:
            rel_path = str(path)

        for pattern in excludes:
            # Match against filename
            if fnmatch.fnmatch(name, pattern):
                return True
            # Match against relative path
            if fnmatch.fnmatch(rel_path, pattern):
                return True
            # Match against path components
            if pattern in rel_path.split(os.sep):
                return True
        return False

    # Walk the directory (sorted for deterministic output)
    for root, dirs, files in os.walk(base_path):
        # Filter out excluded directories (modifies in-place)
        dirs[:] = sorted([d for d in dirs if not should_exclude(Path(root) / d)])

        for file in sorted(files):
            file_path = Path(root) / file
            if should_exclude(file_path):
                continue
            all_files.append(file_path)

    # Filter by patterns if provided
    if patterns:
        filtered = []
        for f in all_files:
            rel_path = str(f.relative_to(base_path))
            for pat in patterns:
                if fnmatch.fnmatch(rel_path, pat):
                    filtered.append(f)
                    break
        return filtered

    return all_files


def read_file_content(file_path: Path, with_line_numbers: bool = False) -> str:
    """
    Read file content, optionally with line numbers.

    Line numbers are added for forensic/interactive modes where
    precise code location matters.

    Args:
        file_path: Path to file
        with_line_numbers: If True, prefix each line with its number

    Returns:
        File content as string, or error message for binary files
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception:
            return f"[Binary or unreadable file: {file_path}]"
    except Exception as e:
        return f"[Error reading {file_path}: {e}]"

    if with_line_numbers:
        lines = content.split('\n')
        numbered = [f"{i+1:4d} | {line}" for i, line in enumerate(lines)]
        return '\n'.join(numbered)

    return content


def build_context_from_files(
    files: List[Path],
    base_dir: Path,
    with_line_numbers: bool = False,
    critical_files: Optional[List[str]] = None,
    positional_strategy: Optional[str] = None,
    max_chars: Optional[int] = None
) -> Tuple[str, int]:
    """
    Build context string from files with optional strategic positioning.

    Positional strategies implement the "sandwich" pattern from prompt
    engineering - critical files at beginning and end for better recall.

    Args:
        files: List of file paths to include
        base_dir: Base directory for relative paths
        with_line_numbers: Add line numbers to content
        critical_files: Files to position strategically
        positional_strategy: 'sandwich' (begin+end) or 'front-load' (begin only)
        max_chars: Maximum characters (truncates if exceeded)

    Returns:
        Tuple of (context string, total character count)
    """
    parts = []
    critical_set: Set[str] = set(critical_files or [])

    # Separate critical and regular files
    critical_file_paths = []
    regular_file_paths = []

    for f in files:
        try:
            rel_path = str(f.relative_to(base_dir))
        except ValueError:
            rel_path = str(f)

        if rel_path in critical_set or str(f) in critical_set:
            critical_file_paths.append(f)
        else:
            regular_file_paths.append(f)

    # Build file list based on strategy
    if positional_strategy == 'sandwich':
        # Critical files at beginning AND end
        ordered_files = critical_file_paths + regular_file_paths + critical_file_paths
    elif positional_strategy == 'front-load':
        # Critical files at beginning only
        ordered_files = critical_file_paths + regular_file_paths
    else:
        # No special positioning
        ordered_files = files

    # Build context
    total_chars = 0
    seen_files: Set[str] = set()  # Avoid duplicates from sandwich

    for f in ordered_files:
        file_key = str(f)
        if file_key in seen_files:
            continue
        seen_files.add(file_key)

        try:
            rel_path = str(f.relative_to(base_dir))
        except ValueError:
            rel_path = str(f)

        content = read_file_content(f, with_line_numbers=with_line_numbers)

        # Check max chars
        file_block = f"\n{'='*60}\nFILE: {rel_path}\n{'='*60}\n{content}\n"
        if max_chars and total_chars + len(file_block) > max_chars:
            # Truncate remaining files
            parts.append(f"\n[TRUNCATED: Remaining files omitted due to size limit]\n")
            break

        parts.append(file_block)
        total_chars += len(file_block)

    context = "\n".join(parts)
    return context, total_chars


def count_tokens_estimate(content: str) -> int:
    """
    Estimate token count using character heuristic.

    This is a fast approximation (~4 chars per token for English/code).
    For accurate counts, use the API's count_tokens method.

    Args:
        content: Text to count

    Returns:
        Estimated token count
    """
    return len(content) // 4


def validate_context_size(
    content: str,
    max_tokens: int,
    warn_threshold: float = 0.8
) -> Tuple[bool, int, Optional[str]]:
    """
    Validate context size before sending to API.

    Args:
        content: Context string
        max_tokens: Maximum allowed tokens
        warn_threshold: Fraction at which to warn (default 80%)

    Returns:
        Tuple of (is_valid, token_count, warning_message)
    """
    token_count = count_tokens_estimate(content)

    if token_count > max_tokens:
        return (
            False,
            token_count,
            f"Context ({token_count:,} tokens) EXCEEDS limit ({max_tokens:,})"
        )

    if token_count > max_tokens * warn_threshold:
        return (
            True,
            token_count,
            f"Context at {token_count / max_tokens * 100:.0f}% of limit"
        )

    return (True, token_count, None)
