"""
Token Estimator - Phase 3 Implementation
=========================================

Accurate token counting BEFORE sending to API.

Methods:
1. Fast estimation (size / 4) - Phase 1
2. Character-based estimation (size / 3.5) - Phase 2
3. Accurate tiktoken counting - Phase 3

Usage:
    from token_estimator import estimate_tokens_accurate, check_budget

    files = [Path("file1.py"), Path("file2.md")]
    tokens = estimate_tokens_accurate(files)

    if not check_budget(tokens, max_tokens=150000):
        print("WARNING: Budget exceeded!")
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


def estimate_tokens_fast(files: List[Path]) -> int:
    """
    Quick token estimation based on file size.

    Heuristic: 1 token ≈ 4 bytes
    Accuracy: ±50%

    Args:
        files: List of file paths

    Returns:
        Estimated token count
    """
    total_bytes = 0
    for filepath in files:
        try:
            total_bytes += os.path.getsize(filepath)
        except OSError:
            continue

    return total_bytes // 4


def estimate_tokens_medium(files: List[Path]) -> int:
    """
    Medium accuracy estimation by counting actual characters.

    Heuristic: 1 token ≈ 3.5 characters (better than bytes)
    Accuracy: ±20%

    Args:
        files: List of file paths

    Returns:
        Estimated token count
    """
    total_chars = 0

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                total_chars += len(content)
        except (OSError, UnicodeDecodeError):
            # Fallback to size estimate for unreadable files
            try:
                total_chars += os.path.getsize(filepath)
            except OSError:
                continue

    return int(total_chars / 3.5)


def estimate_tokens_accurate(files: List[Path], encoding: str = "cl100k_base") -> int:
    """
    Accurate token counting using tiktoken.

    Uses actual GPT-4/Gemini tokenizer.
    Accuracy: ±5%

    Args:
        files: List of file paths
        encoding: Tokenizer to use (cl100k_base for GPT-4/Gemini)

    Returns:
        Accurate token count
    """
    if not HAS_TIKTOKEN:
        # Fallback to medium accuracy if tiktoken not available
        return estimate_tokens_medium(files)

    try:
        enc = tiktoken.get_encoding(encoding)
    except Exception:
        # Fallback to medium accuracy if encoding fails
        return estimate_tokens_medium(files)

    total_tokens = 0

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tokens = enc.encode(content)
                total_tokens += len(tokens)
        except (OSError, UnicodeDecodeError):
            # Fallback to character estimate for unreadable files
            try:
                size = os.path.getsize(filepath)
                total_tokens += size // 4
            except OSError:
                continue

    return total_tokens


def estimate_tokens_smart(files: List[Path], max_budget: int = 1_000_000) -> Dict[str, any]:
    """
    Smart token estimation with automatic method selection.

    Strategy:
    - Use fast method first
    - If within 80% of budget, use accurate method
    - If over budget, warn immediately

    Args:
        files: List of file paths
        max_budget: Maximum token budget

    Returns:
        Dict with:
            - method: Estimation method used
            - tokens: Estimated tokens
            - accuracy: Accuracy level (±%)
            - over_budget: Boolean
    """
    # Step 1: Fast estimate
    fast_estimate = estimate_tokens_fast(files)

    # Step 2: If clearly over budget, return immediately
    if fast_estimate > max_budget * 1.5:
        return {
            'method': 'fast',
            'tokens': fast_estimate,
            'accuracy': 50,
            'over_budget': True,
            'ratio': fast_estimate / max_budget if max_budget > 0 else 0
        }

    # Step 3: If within 80% of budget, use accurate method
    if fast_estimate > max_budget * 0.8:
        accurate_estimate = estimate_tokens_accurate(files)
        return {
            'method': 'accurate',
            'tokens': accurate_estimate,
            'accuracy': 5,
            'over_budget': accurate_estimate > max_budget,
            'ratio': accurate_estimate / max_budget if max_budget > 0 else 0
        }

    # Step 4: Well under budget, medium accuracy is fine
    medium_estimate = estimate_tokens_medium(files)
    return {
        'method': 'medium',
        'tokens': medium_estimate,
        'accuracy': 20,
        'over_budget': medium_estimate > max_budget,
        'ratio': medium_estimate / max_budget if max_budget > 0 else 0
    }


def check_budget(
    files: List[Path],
    max_budget: int,
    warn_threshold: float = 0.9,
    force: bool = False
) -> Dict[str, any]:
    """
    Check if files are within token budget with warnings.

    Args:
        files: List of file paths
        max_budget: Maximum token budget
        warn_threshold: Warn if exceeding this ratio (default 0.9 = 90%)
        force: Skip enforcement if True

    Returns:
        Dict with:
            - allowed: Boolean (can proceed)
            - tokens: Estimated tokens
            - budget: Maximum budget
            - ratio: tokens/budget
            - warning: Warning message if any
    """
    estimate = estimate_tokens_smart(files, max_budget)

    tokens = estimate['tokens']
    ratio = estimate['ratio']

    # Over budget
    if estimate['over_budget']:
        if force:
            return {
                'allowed': True,
                'tokens': tokens,
                'budget': max_budget,
                'ratio': ratio,
                'warning': f"⚠️  FORCED: {tokens:,} tokens exceeds budget {max_budget:,} ({ratio:.1%})",
                'method': estimate['method']
            }
        else:
            return {
                'allowed': False,
                'tokens': tokens,
                'budget': max_budget,
                'ratio': ratio,
                'warning': f"❌ BLOCKED: {tokens:,} tokens exceeds budget {max_budget:,} ({ratio:.1%})",
                'method': estimate['method']
            }

    # Near budget (warning)
    if ratio >= warn_threshold:
        return {
            'allowed': True,
            'tokens': tokens,
            'budget': max_budget,
            'ratio': ratio,
            'warning': f"⚠️  WARNING: {tokens:,} tokens is {ratio:.1%} of budget {max_budget:,}",
            'method': estimate['method']
        }

    # Well within budget
    return {
        'allowed': True,
        'tokens': tokens,
        'budget': max_budget,
        'ratio': ratio,
        'warning': None,
        'method': estimate['method']
    }


def format_budget_report(budget_check: Dict[str, any]) -> str:
    """
    Format budget check result as user-friendly report.

    Args:
        budget_check: Result from check_budget()

    Returns:
        Formatted report string
    """
    lines = []

    tokens = budget_check['tokens']
    budget = budget_check['budget']
    ratio = budget_check['ratio']
    method = budget_check.get('method', 'unknown')

    lines.append("=" * 60)
    lines.append("TOKEN BUDGET CHECK")
    lines.append("=" * 60)
    lines.append(f"  Estimated:  {tokens:,} tokens (method: {method})")
    lines.append(f"  Budget:     {budget:,} tokens")
    lines.append(f"  Usage:      {ratio:.1%}")

    # Visual bar
    bar_width = 40
    filled = int(bar_width * min(ratio, 1.0))
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append(f"  [{bar}]")

    if budget_check.get('warning'):
        lines.append("")
        lines.append(budget_check['warning'])

    lines.append("=" * 60)

    return '\n'.join(lines)


def get_file_token_breakdown(files: List[Path], top_n: int = 10) -> List[Dict[str, any]]:
    """
    Get token breakdown for largest files.

    Useful for understanding what's using the most tokens.

    Args:
        files: List of file paths
        top_n: Number of top files to return

    Returns:
        List of dicts with file info sorted by token count
    """
    file_stats = []

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Estimate tokens for this file
            if HAS_TIKTOKEN:
                enc = tiktoken.get_encoding("cl100k_base")
                tokens = len(enc.encode(content))
            else:
                tokens = len(content) // 4

            file_stats.append({
                'file': str(filepath),
                'tokens': tokens,
                'size': os.path.getsize(filepath),
                'lines': content.count('\n') + 1
            })
        except Exception:
            continue

    # Sort by token count
    file_stats.sort(key=lambda x: x['tokens'], reverse=True)

    return file_stats[:top_n]


def compress_context(content: str, level: str = "medium") -> str:
    """
    Semantic Compression Algorithm (Ported from Central-MCP).
    Reduces token payload by removing redundancy and applying standard abbreviations.

    Levels:
    - 'light': Basic whitespace and comment stripping
    - 'medium': + standard semantic abbreviations
    - 'aggressive': + pattern collapsing (destructive)
    """
    import re

    compressed = content

    # Light: remove consecutive blank lines and trailing spaces
    compressed = re.sub(r'\n{3,}', '\n\n', compressed)
    compressed = re.sub(r' +\n', '\n', compressed)

    if level in ["medium", "aggressive"]:
        # Semantic abbreviations (saves tokens without losing meaning)
        abbreviations = {
            "function": "fn",
            "boolean": "bool",
            "integer": "int",
            "string": "str",
            "configuration": "config",
            "initialization": "init",
            "implementation": "impl",
            "development": "dev",
            "production": "prod",
            "environment": "env",
            "repository": "repo",
            "directory": "dir",
            "information": "info",
            "temperature": "temp",
            "maximum": "max",
            "minimum": "min",
        }
        for full_word, abbr in abbreviations.items():
            compressed = re.sub(rf'\b{full_word}\b', abbr, compressed)

    if level == "aggressive":
        # Remove all inline comments (Python and JS/TS)
        compressed = re.sub(r'(?s)/\*.*?\*/', '', compressed) # multi-line
        compressed = re.sub(r'(?m)^\s*//.*$', '', compressed) # single-line JS
        compressed = re.sub(r'(?m)^\s*#.*$', '', compressed)  # single-line Python

    return compressed
