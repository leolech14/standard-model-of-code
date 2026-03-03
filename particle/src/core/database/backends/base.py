"""
Abstract Base Class for Database Backends.

All backends must implement this interface for:
- Connection management
- Schema initialization
- CRUD operations for analysis runs, nodes, edges
- File tracking for incremental analysis
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple


@dataclass
class AnalysisRun:
    """Represents a single analysis run."""
    id: str
    project_name: str
    project_path: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    collider_version: str = "1.0.0"
    status: str = "running"  # running, completed, failed
    node_count: int = 0
    edge_count: int = 0
    options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TrackedFile:
    """Represents a tracked file for incremental analysis."""
    id: str
    project_path: str
    relative_path: str
    blake3_hash: str
    modified_ts: int
    last_analyzed_run: Optional[str] = None


@dataclass
class DeltaResult:
    """Result of change detection."""
    changed_files: List[str]
    new_files: List[str]
    unchanged_files: List[str]
    deleted_files: List[str]

    @property
    def total_changes(self) -> int:
        return len(self.changed_files) + len(self.new_files) + len(self.deleted_files)

    @property
    def needs_analysis(self) -> Set[str]:
        """Files that need to be analyzed."""
        return set(self.changed_files) | set(self.new_files)


class DatabaseBackend(ABC):
    """
    Abstract base class for database backends.

    Backends provide:
    1. Connection management (connect, disconnect, health check)
    2. Schema initialization and migrations
    3. Analysis run management (create, update, query)
    4. Node/Edge persistence and retrieval
    5. File tracking for incremental analysis
    """

    def __init__(self, config):
        """
        Initialize backend with config.

        Args:
            config: DatabaseConfig instance
        """
        self.config = config
        self._connected = False

    # =========================================================================
    # Connection Management
    # =========================================================================

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish database connection.

        Returns:
            True if connection successful.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database is connected."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Dict with status, latency_ms, version, etc.
        """
        pass

    # =========================================================================
    # Schema Management
    # =========================================================================

    @abstractmethod
    def initialize_schema(self) -> bool:
        """
        Create tables if they don't exist.

        Returns:
            True if schema is ready.
        """
        pass

    @abstractmethod
    def get_schema_version(self) -> int:
        """Get current schema version."""
        pass

    @abstractmethod
    def migrate_to(self, version: int) -> bool:
        """
        Migrate schema to target version.

        Args:
            version: Target schema version.

        Returns:
            True if migration successful.
        """
        pass

    # =========================================================================
    # Analysis Runs
    # =========================================================================

    @abstractmethod
    def create_run(self, run: AnalysisRun) -> str:
        """
        Create a new analysis run record.

        Args:
            run: AnalysisRun instance.

        Returns:
            Run ID.
        """
        pass

    @abstractmethod
    def update_run(self, run_id: str, **updates) -> bool:
        """
        Update an existing run.

        Args:
            run_id: Run ID to update.
            **updates: Fields to update.

        Returns:
            True if update successful.
        """
        pass

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[AnalysisRun]:
        """Get a run by ID."""
        pass

    @abstractmethod
    def get_runs(self, project_path: Optional[str] = None, limit: int = 10) -> List[AnalysisRun]:
        """
        Get recent runs, optionally filtered by project.

        Args:
            project_path: Filter by project path.
            limit: Max runs to return.

        Returns:
            List of AnalysisRun instances.
        """
        pass

    @abstractmethod
    def get_latest_run(self, project_path: str) -> Optional[AnalysisRun]:
        """Get the most recent completed run for a project."""
        pass

    # =========================================================================
    # Nodes
    # =========================================================================

    @abstractmethod
    def insert_nodes(self, run_id: str, nodes: List[Dict[str, Any]]) -> int:
        """
        Insert nodes in batch.

        Args:
            run_id: Analysis run ID.
            nodes: List of node dicts.

        Returns:
            Number of nodes inserted.
        """
        pass

    @abstractmethod
    def get_nodes(self, run_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get nodes for a run.

        Args:
            run_id: Analysis run ID.
            filters: Optional filters (role, kind, file_path, etc.)

        Returns:
            List of node dicts.
        """
        pass

    @abstractmethod
    def get_node(self, run_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a single node by ID."""
        pass

    # =========================================================================
    # Edges
    # =========================================================================

    @abstractmethod
    def insert_edges(self, run_id: str, edges: List[Dict[str, Any]]) -> int:
        """
        Insert edges in batch.

        Args:
            run_id: Analysis run ID.
            edges: List of edge dicts.

        Returns:
            Number of edges inserted.
        """
        pass

    @abstractmethod
    def get_edges(self, run_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get edges for a run.

        Args:
            run_id: Analysis run ID.
            filters: Optional filters (edge_type, source_id, target_id)

        Returns:
            List of edge dicts.
        """
        pass

    # =========================================================================
    # File Tracking (Incremental)
    # =========================================================================

    @abstractmethod
    def get_tracked_files(self, project_path: str) -> Dict[str, TrackedFile]:
        """
        Get all tracked files for a project.

        Args:
            project_path: Project root path.

        Returns:
            Dict mapping relative_path -> TrackedFile
        """
        pass

    @abstractmethod
    def update_tracked_files(self, project_path: str, files: List[TrackedFile]) -> int:
        """
        Update tracked files (upsert).

        Args:
            project_path: Project root path.
            files: List of TrackedFile instances.

        Returns:
            Number of files updated.
        """
        pass

    @abstractmethod
    def delete_tracked_files(self, project_path: str, relative_paths: List[str]) -> int:
        """
        Delete tracked files that no longer exist.

        Args:
            project_path: Project root path.
            relative_paths: Paths to delete.

        Returns:
            Number of files deleted.
        """
        pass

    # =========================================================================
    # Transaction Management
    # =========================================================================

    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass

    # =========================================================================
    # High-Level Operations
    # =========================================================================

    def persist(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]],
                metadata: Dict[str, Any], run: Optional[AnalysisRun] = None) -> str:
        """
        Persist a complete analysis result atomically.

        All operations (create_run, insert_nodes, insert_edges, update_run)
        are wrapped in a transaction. If any operation fails, the entire
        transaction is rolled back to maintain database consistency.

        Args:
            nodes: List of node dicts.
            edges: List of edge dicts.
            metadata: Analysis metadata.
            run: Optional pre-created AnalysisRun.

        Returns:
            Run ID.

        Raises:
            Exception: Re-raises any exception after rollback.
        """
        if not self.is_connected():
            self.connect()
            self.initialize_schema()

        # Create run if not provided
        if run is None:
            import hashlib
            import time
            run = AnalysisRun(
                id=f"run_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}",
                project_name=metadata.get("project_name", "unknown"),
                project_path=metadata.get("target_path", ""),
                started_at=datetime.now(),
                options=metadata.get("options"),
            )
        elif run.started_at is None:
            # Ensure started_at is always set for consistency
            run.started_at = datetime.now()

        # Wrap all operations in a transaction for atomicity
        self.begin_transaction()
        try:
            run_id = self.create_run(run)

            # Insert nodes and edges
            node_count = self.insert_nodes(run_id, nodes)
            edge_count = self.insert_edges(run_id, edges)

            # Mark complete
            self.update_run(
                run_id,
                status="completed",
                completed_at=datetime.now(),
                node_count=node_count,
                edge_count=edge_count,
            )

            self.commit_transaction()
            return run_id

        except Exception as e:
            # Rollback on any error to maintain consistency
            self.rollback_transaction()
            # Mark run as failed if it was created
            if run:
                try:
                    self.begin_transaction()
                    self.update_run(run.id, status="failed")
                    self.commit_transaction()
                except Exception:
                    self.rollback_transaction()
            raise e

    def purge_old_runs(self, project_path: Optional[str] = None) -> int:
        """
        Purge old analysis runs based on retention policy.

        Applies two axes (both configurable, 0 = disabled):
        1. Count-based: keep only the N most recent runs per project
        2. Age-based: delete runs older than X days

        Relies on ON DELETE CASCADE for nodes/edges cleanup.

        Args:
            project_path: If given, only purge runs for this project.
                          If None, purge across all projects.

        Returns:
            Number of runs purged.
        """
        # Subclasses implement the actual SQL; default is no-op
        return 0

    def detect_changes(self, project_path: str, current_files: Dict[str, Tuple[str, int]]) -> DeltaResult:
        """
        Detect which files have changed since last analysis.

        Args:
            project_path: Project root path.
            current_files: Dict mapping relative_path -> (hash, mtime)

        Returns:
            DeltaResult with changed, new, unchanged, deleted files.
        """
        tracked = self.get_tracked_files(project_path)
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

        return DeltaResult(
            changed_files=changed,
            new_files=new,
            unchanged_files=unchanged,
            deleted_files=deleted,
        )

    def __enter__(self):
        """Context manager entry.

        Raises:
            ConnectionError: If database connection fails.
        """
        if not self.connect():
            raise ConnectionError(f"Failed to connect to database")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.

        Always attempts to disconnect, even if an exception occurred.
        Disconnect errors are suppressed to avoid masking the original exception.
        """
        try:
            self.disconnect()
        except Exception:
            # Suppress disconnect errors to avoid masking the original exception
            # The original exception (if any) is more important
            pass
        return False  # Don't suppress the original exception
