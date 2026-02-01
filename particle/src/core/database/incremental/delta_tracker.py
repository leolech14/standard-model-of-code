"""
Delta Tracker for Incremental Analysis.

Compares current file state with previously tracked state
to determine which files need re-analysis.
"""
import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .hasher import FileHasher
from ..backends.base import DatabaseBackend, TrackedFile, DeltaResult


@dataclass
class DeltaStats:
    """Statistics from delta detection."""
    total_files: int = 0
    changed_files: int = 0
    new_files: int = 0
    unchanged_files: int = 0
    deleted_files: int = 0
    scan_time_ms: float = 0
    hash_time_ms: float = 0


class DeltaTracker:
    """
    Tracks file changes for incremental analysis.

    Usage:
        tracker = DeltaTracker(db_backend)
        delta = tracker.detect_changes(project_path)

        # Only analyze changed/new files
        files_to_analyze = delta.needs_analysis

        # After analysis, update tracking
        tracker.update_tracking(project_path, run_id, file_hashes)
    """

    def __init__(self, backend: DatabaseBackend, hasher: Optional[FileHasher] = None):
        """
        Initialize delta tracker.

        Args:
            backend: Database backend for persistence
            hasher: Optional custom hasher (defaults to BLAKE3)
        """
        self.backend = backend
        self.hasher = hasher or FileHasher()
        self._last_stats: Optional[DeltaStats] = None

    def detect_changes(self, project_path: str,
                       patterns: Optional[List[str]] = None,
                       exclude: Optional[List[str]] = None) -> DeltaResult:
        """
        Detect which files have changed since last analysis.

        Args:
            project_path: Project root directory
            patterns: Glob patterns to include
            exclude: Paths to exclude

        Returns:
            DeltaResult with changed, new, unchanged, deleted files
        """
        project_path = str(Path(project_path).resolve())
        stats = DeltaStats()

        # 1. Get current file hashes
        start_scan = time.time()
        current_files = self.hasher.hash_directory(
            Path(project_path),
            patterns=patterns,
            exclude=exclude
        )
        stats.scan_time_ms = (time.time() - start_scan) * 1000
        stats.total_files = len(current_files)

        # 2. Get tracked files from database
        start_hash = time.time()
        tracked = self.backend.get_tracked_files(project_path)
        stats.hash_time_ms = (time.time() - start_hash) * 1000

        # 3. Compare
        tracked_paths = set(tracked.keys())
        current_paths = set(current_files.keys())

        changed = []
        new = []
        unchanged = []
        deleted = list(tracked_paths - current_paths)

        for path in current_paths:
            current_hash, current_mtime = current_files[path]
            if path in tracked:
                if tracked[path].blake3_hash != current_hash:
                    changed.append(path)
                else:
                    unchanged.append(path)
            else:
                new.append(path)

        # Update stats
        stats.changed_files = len(changed)
        stats.new_files = len(new)
        stats.unchanged_files = len(unchanged)
        stats.deleted_files = len(deleted)
        self._last_stats = stats

        return DeltaResult(
            changed_files=changed,
            new_files=new,
            unchanged_files=unchanged,
            deleted_files=deleted,
        )

    def update_tracking(self, project_path: str, run_id: str,
                        file_hashes: Dict[str, Tuple[str, int]]) -> int:
        """
        Update file tracking after analysis.

        Args:
            project_path: Project root directory
            run_id: Analysis run ID
            file_hashes: Dict mapping relative_path -> (hash, mtime)

        Returns:
            Number of files updated
        """
        project_path = str(Path(project_path).resolve())

        # Build TrackedFile objects
        tracked_files = []
        for rel_path, (hash_value, mtime) in file_hashes.items():
            file_id = self._make_file_id(project_path, rel_path)
            tracked_files.append(TrackedFile(
                id=file_id,
                project_path=project_path,
                relative_path=rel_path,
                blake3_hash=hash_value,
                modified_ts=mtime,
                last_analyzed_run=run_id,
            ))

        # Update database
        return self.backend.update_tracked_files(project_path, tracked_files)

    def cleanup_deleted(self, project_path: str, deleted_paths: List[str]) -> int:
        """
        Remove tracking for deleted files.

        Args:
            project_path: Project root directory
            deleted_paths: Relative paths of deleted files

        Returns:
            Number of files removed
        """
        if not deleted_paths:
            return 0

        project_path = str(Path(project_path).resolve())
        return self.backend.delete_tracked_files(project_path, deleted_paths)

    def get_stats(self) -> Optional[DeltaStats]:
        """Get statistics from last detect_changes call."""
        return self._last_stats

    def print_summary(self) -> None:
        """Print summary of last delta detection."""
        if not self._last_stats:
            print("  [Delta] No detection performed yet")
            return

        s = self._last_stats
        print(f"  [Delta] Scanned {s.total_files} files in {s.scan_time_ms:.0f}ms")
        print(f"  [Delta] Changed: {s.changed_files}, New: {s.new_files}, Unchanged: {s.unchanged_files}")
        if s.deleted_files:
            print(f"  [Delta] Deleted: {s.deleted_files}")

        skip_pct = (s.unchanged_files / s.total_files * 100) if s.total_files > 0 else 0
        print(f"  [Delta] Skipping {skip_pct:.0f}% of files (unchanged)")

    def _make_file_id(self, project_path: str, relative_path: str) -> str:
        """Generate unique file ID."""
        combined = f"{project_path}::{relative_path}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


def create_delta_tracker(backend: DatabaseBackend, algorithm: str = "blake3",
                         workers: int = 4) -> DeltaTracker:
    """
    Factory function to create DeltaTracker.

    Args:
        backend: Database backend
        algorithm: Hash algorithm
        workers: Parallel workers for hashing

    Returns:
        Configured DeltaTracker
    """
    hasher = FileHasher(algorithm=algorithm, workers=workers)
    return DeltaTracker(backend, hasher)
