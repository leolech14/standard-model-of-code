"""
Context Filters - Phase 1 Implementation
=========================================

Intelligent file filtering to prevent token quota disasters.

Filters:
- exclude_patterns: Exclude archive/, experiments/, legacy/
- max_age_days: Only include files modified in last N days
- max_file_size_kb: Skip files larger than N kilobytes
- limit: Hard cap on number of files
- sort_by: Order files by mtime, size, or path

Usage:
    from context_filters import apply_filters

    files = glob.glob("**/*.py")
    filters = {
        'exclude_patterns': ['**/archive/**'],
        'max_age_days': 90,
        'max_file_size_kb': 500,
        'limit': 100
    }
    filtered_files = apply_filters(files, filters, base_dir="/path/to/repo")
"""

import os
import time
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional


def filter_by_exclude_patterns(
    files: List[Path],
    exclude_patterns: List[str],
    base_dir: Optional[Path] = None
) -> List[Path]:
    """
    Exclude files matching any of the exclude patterns.

    Args:
        files: List of file paths
        exclude_patterns: List of glob patterns to exclude (e.g., "**/archive/**")
        base_dir: Base directory for relative path matching

    Returns:
        Filtered list of files
    """
    if not exclude_patterns:
        return files

    filtered = []
    for file_path in files:
        excluded = False

        # Get relative path for pattern matching
        if base_dir:
            try:
                rel_path = str(file_path.relative_to(base_dir))
            except ValueError:
                rel_path = str(file_path)
        else:
            rel_path = str(file_path)

        # Check against each exclude pattern
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                excluded = True
                break

            # Also check if pattern matches any parent directory
            # e.g., "**/archive/**" should match "foo/archive/bar.py"
            parts = rel_path.split(os.sep)
            for i in range(len(parts)):
                partial = os.sep.join(parts[:i+1])
                if fnmatch.fnmatch(partial, pattern):
                    excluded = True
                    break

            if excluded:
                break

        if not excluded:
            filtered.append(file_path)

    return filtered


def filter_by_age(files: List[Path], max_age_days: int) -> List[Path]:
    """
    Only include files modified in the last N days.

    Args:
        files: List of file paths
        max_age_days: Maximum file age in days

    Returns:
        Filtered list of files
    """
    cutoff_time = time.time() - (max_age_days * 86400)  # 86400 seconds = 1 day
    filtered = []

    for file_path in files:
        try:
            mtime = os.path.getmtime(file_path)
            if mtime >= cutoff_time:
                filtered.append(file_path)
        except OSError:
            # If we can't get mtime, skip the file
            continue

    return filtered


def filter_by_size(files: List[Path], max_kb: int) -> List[Path]:
    """
    Exclude files larger than N kilobytes.

    Args:
        files: List of file paths
        max_kb: Maximum file size in kilobytes

    Returns:
        Filtered list of files
    """
    max_bytes = max_kb * 1024
    filtered = []

    for file_path in files:
        try:
            size = os.path.getsize(file_path)
            if size <= max_bytes:
                filtered.append(file_path)
        except OSError:
            # If we can't get size, skip the file
            continue

    return filtered


def sort_files(files: List[Path], sort_by: str = "mtime") -> List[Path]:
    """
    Sort files by specified criterion.

    Args:
        files: List of file paths
        sort_by: Sort criterion - "mtime", "size", or "path"

    Returns:
        Sorted list of files
    """
    if sort_by == "mtime":
        # Most recent first
        return sorted(
            files,
            key=lambda f: os.path.getmtime(f) if os.path.exists(f) else 0,
            reverse=True
        )
    elif sort_by == "size":
        # Smallest first
        return sorted(
            files,
            key=lambda f: os.path.getsize(f) if os.path.exists(f) else 0
        )
    elif sort_by == "path":
        # Alphabetical
        return sorted(files, key=lambda f: str(f))
    else:
        return files


def estimate_tokens_fast(files: List[Path]) -> int:
    """
    Quick token estimation based on file size.

    Rough heuristic: 1 token ≈ 4 characters

    Args:
        files: List of file paths

    Returns:
        Estimated token count
    """
    total_size = 0
    for file_path in files:
        try:
            total_size += os.path.getsize(file_path)
        except OSError:
            continue

    # 1 token ≈ 4 chars
    return total_size // 4


def apply_filters(
    files: List[Path],
    filters: Dict[str, Any],
    base_dir: Optional[Path] = None,
    verbose: bool = False
) -> List[Path]:
    """
    Apply all configured filters to a list of files.

    Args:
        files: List of file paths
        filters: Dictionary of filter configurations
        base_dir: Base directory for relative path matching
        verbose: Print filter statistics

    Returns:
        Filtered and sorted list of files

    Filter options:
        - exclude_patterns: List of glob patterns to exclude
        - max_age_days: Maximum file age in days
        - max_file_size_kb: Maximum file size in KB
        - sort_by: "mtime", "size", or "path"
        - limit: Maximum number of files to return
    """
    if not filters:
        return files

    if verbose:
        print(f"  [Filters] Starting with {len(files)} files")

    # Step 1: Exclude patterns
    if 'exclude_patterns' in filters:
        files = filter_by_exclude_patterns(
            files,
            filters['exclude_patterns'],
            base_dir
        )
        if verbose:
            print(f"  [Filters] After exclude_patterns: {len(files)} files")

    # Step 2: Age filter
    if 'max_age_days' in filters:
        files = filter_by_age(files, filters['max_age_days'])
        if verbose:
            print(f"  [Filters] After max_age_days: {len(files)} files")

    # Step 3: Size filter
    if 'max_file_size_kb' in filters:
        files = filter_by_size(files, filters['max_file_size_kb'])
        if verbose:
            print(f"  [Filters] After max_file_size_kb: {len(files)} files")

    # Step 4: Sort (if requested)
    if 'sort_by' in filters:
        files = sort_files(files, filters['sort_by'])
        if verbose:
            print(f"  [Filters] Sorted by {filters['sort_by']}")

    # Step 5: Limit count
    if 'limit' in filters and filters['limit'] > 0:
        files = files[:filters['limit']]
        if verbose:
            print(f"  [Filters] After limit: {len(files)} files")

    if verbose:
        print(f"  [Filters] Final count: {len(files)} files")

    return files


def validate_filters(filters: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate filter configuration and return any errors.

    Args:
        filters: Dictionary of filter configurations

    Returns:
        Dictionary of {field: error_message} for any invalid filters
    """
    errors = {}

    if 'max_age_days' in filters:
        if not isinstance(filters['max_age_days'], int) or filters['max_age_days'] <= 0:
            errors['max_age_days'] = "Must be a positive integer"

    if 'max_file_size_kb' in filters:
        if not isinstance(filters['max_file_size_kb'], int) or filters['max_file_size_kb'] <= 0:
            errors['max_file_size_kb'] = "Must be a positive integer"

    if 'limit' in filters:
        if not isinstance(filters['limit'], int) or filters['limit'] <= 0:
            errors['limit'] = "Must be a positive integer"

    if 'sort_by' in filters:
        if filters['sort_by'] not in ['mtime', 'size', 'path']:
            errors['sort_by'] = "Must be 'mtime', 'size', or 'path'"

    if 'exclude_patterns' in filters:
        if not isinstance(filters['exclude_patterns'], list):
            errors['exclude_patterns'] = "Must be a list of patterns"

    return errors
