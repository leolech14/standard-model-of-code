"""
File Hasher for Incremental Analysis.

Uses BLAKE3 for fast, secure hashing with optional parallel processing.
Falls back to hashlib.sha256 if blake3 is not installed.
"""
import hashlib
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Pattern

# Try to import blake3, fall back to hashlib
try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False


class FileHasher:
    """
    Fast file hasher for incremental analysis.

    Uses BLAKE3 when available, falls back to SHA-256.
    Supports parallel hashing for large file sets.
    """

    # Default algorithm - fallback is allowed for this value
    DEFAULT_ALGORITHM = "blake3"

    def __init__(self, algorithm: str = "blake3", workers: int = 4,
                 allow_fallback: Optional[bool] = None):
        """
        Initialize hasher.

        Args:
            algorithm: Hash algorithm ("blake3" or "sha256")
            workers: Number of parallel workers for batch hashing
            allow_fallback: Whether to allow fallback to sha256 if blake3
                           is not available. If None (default), fallback is
                           only allowed when using the default algorithm.
                           Set to True to always allow, False to never allow.
        """
        self.workers = workers

        # Determine if fallback is allowed
        if allow_fallback is None:
            # Only fallback if using the default algorithm
            allow_fallback = (algorithm == self.DEFAULT_ALGORITHM)

        if algorithm == "blake3" and not HAS_BLAKE3:
            if allow_fallback:
                import warnings
                warnings.warn(
                    "blake3 not installed, falling back to sha256. "
                    "Install blake3 for faster hashing: pip install blake3",
                    category=UserWarning,
                    stacklevel=2
                )
                self.algorithm = "sha256"
            else:
                raise ImportError(
                    f"blake3 was explicitly requested but is not installed. "
                    f"Install it with: pip install blake3"
                )
        else:
            self.algorithm = algorithm

    def hash_file(self, file_path: Path) -> Optional[str]:
        """
        Hash a single file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest string or None if file can't be read
        """
        return hash_file(file_path, self.algorithm)

    def hash_files(self, file_paths: List[Path], parallel: bool = True) -> Dict[Path, str]:
        """
        Hash multiple files.

        Args:
            file_paths: List of file paths
            parallel: Whether to use parallel processing

        Returns:
            Dict mapping path -> hash
        """
        if parallel and len(file_paths) > 10:
            return hash_files_parallel(file_paths, self.algorithm, self.workers)

        result = {}
        for path in file_paths:
            h = self.hash_file(path)
            if h:
                result[path] = h
        return result

    def hash_directory(self, directory: Path, patterns: Optional[List[str]] = None,
                       exclude: Optional[List[str]] = None) -> Dict[str, Tuple[str, int]]:
        """
        Hash all matching files in a directory.

        Args:
            directory: Root directory
            patterns: Glob patterns to include (default: common code files)
            exclude: Paths to exclude

        Returns:
            Dict mapping relative_path -> (hash, mtime)
        """
        if patterns is None:
            patterns = [
                "**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.jsx",
                "**/*.go", "**/*.rs", "**/*.java", "**/*.kt",
                "**/*.c", "**/*.cpp", "**/*.h", "**/*.hpp",
                "**/*.rb", "**/*.php", "**/*.cs", "**/*.swift",
            ]

        if exclude is None:
            exclude = [
                "node_modules", "__pycache__", ".git", ".venv", "venv",
                "dist", "build", ".next", "target", "vendor",
            ]

        # Compile exclusions into a single regex for O(1) lookup
        # Escape special regex characters and join with OR
        exclude_pattern: Optional[Pattern] = None
        if exclude:
            escaped = [re.escape(e) for e in exclude]
            exclude_pattern = re.compile("|".join(escaped))

        # Collect files
        files = []
        directory = Path(directory).resolve()

        for pattern in patterns:
            for file_path in directory.glob(pattern):
                if not file_path.is_file():
                    continue

                # Check exclusions with O(1) regex match
                rel_path = str(file_path.relative_to(directory))
                if exclude_pattern and exclude_pattern.search(rel_path):
                    continue

                files.append(file_path)

        # Hash files in parallel
        hashes = self.hash_files(files, parallel=True)

        # Build result with relative paths and mtime
        result = {}
        for path, hash_value in hashes.items():
            rel_path = str(path.relative_to(directory))
            mtime = int(path.stat().st_mtime)
            result[rel_path] = (hash_value, mtime)

        return result


def hash_file(file_path: Path, algorithm: str = "blake3") -> Optional[str]:
    """
    Hash a single file.

    Args:
        file_path: Path to file
        algorithm: "blake3" or "sha256"

    Returns:
        Hex digest string or None if file can't be read
    """
    try:
        with open(file_path, "rb") as f:
            if algorithm == "blake3" and HAS_BLAKE3:
                hasher = blake3.blake3()
                while chunk := f.read(1024 * 1024):  # 1MB chunks
                    hasher.update(chunk)
                return hasher.hexdigest()
            else:
                hasher = hashlib.sha256()
                while chunk := f.read(1024 * 1024):
                    hasher.update(chunk)
                return hasher.hexdigest()
    except (IOError, OSError):
        return None


def hash_files_parallel(file_paths: List[Path], algorithm: str = "blake3",
                        workers: int = 4) -> Dict[Path, str]:
    """
    Hash multiple files in parallel.

    Args:
        file_paths: List of file paths
        algorithm: Hash algorithm
        workers: Number of parallel workers

    Returns:
        Dict mapping path -> hash
    """
    result = {}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(hash_file, path, algorithm): path
            for path in file_paths
        }

        for future in as_completed(futures):
            path = futures[future]
            try:
                h = future.result()
                if h:
                    result[path] = h
            except Exception:
                pass

    return result
