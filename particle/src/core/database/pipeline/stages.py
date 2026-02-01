"""
Pipeline Stages for Database Integration.

IncrementalStage: Runs before analysis to detect changes
PersistenceStage: Runs after analysis to save results
"""
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...data_management import CodebaseState

from ..backends.base import DatabaseBackend, AnalysisRun
from ..incremental.delta_tracker import DeltaTracker, create_delta_tracker


class IncrementalStage:
    """
    Pipeline stage for incremental analysis.

    Runs BEFORE file parsing to determine which files can be skipped.
    """

    name = "incremental_detection"
    stage_number = 0.5  # Between Survey (0) and Base Analysis (1)

    def __init__(self, backend: DatabaseBackend, config: Optional[Dict[str, Any]] = None):
        """
        Initialize incremental stage.

        Args:
            backend: Database backend
            config: Optional configuration
        """
        self.backend = backend
        self.config = config or {}
        self.tracker = create_delta_tracker(
            backend,
            algorithm=self.config.get("hash_algorithm", "blake3"),
            workers=self.config.get("workers", 4),
        )
        self.delta = None
        self.skip_files = set()

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Detect changes and update state with files to skip.

        Args:
            state: Current pipeline state

        Returns:
            Modified state with skip_files set
        """
        project_path = state.target_path
        exclude = self.config.get("exclude_paths", [])

        # Detect changes
        self.delta = self.tracker.detect_changes(project_path, exclude=exclude)

        # Update state metadata
        if hasattr(state, "metadata"):
            state.metadata["incremental"] = {
                "changed": len(self.delta.changed_files),
                "new": len(self.delta.new_files),
                "unchanged": len(self.delta.unchanged_files),
                "deleted": len(self.delta.deleted_files),
            }

        # Set files to skip
        self.skip_files = set(self.delta.unchanged_files)

        return state

    def get_skip_files(self):
        """Get set of files to skip during analysis."""
        return self.skip_files

    def print_summary(self):
        """Print detection summary."""
        self.tracker.print_summary()


class PersistenceStage:
    """
    Pipeline stage for persisting analysis results.

    Runs AFTER all analysis to save nodes/edges to database.
    """

    name = "persistence"
    stage_number = 12  # After all analysis, before output generation

    def __init__(self, backend: DatabaseBackend, config: Optional[Dict[str, Any]] = None):
        """
        Initialize persistence stage.

        Args:
            backend: Database backend
            config: Optional configuration
        """
        self.backend = backend
        self.config = config or {}
        self.run_id = None
        self.node_count = 0
        self.edge_count = 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Persist analysis results to database.

        Args:
            state: Pipeline state with nodes and edges

        Returns:
            State with persistence metadata added
        """
        project_path = str(Path(state.target_path).resolve())
        project_name = Path(project_path).name

        # Create analysis run
        run = AnalysisRun(
            id=f"run_{hashlib.sha256(f'{project_path}-{time.time()}'.encode()).hexdigest()[:12]}",
            project_name=project_name,
            project_path=project_path,
            started_at=datetime.now(),
            collider_version=self.config.get("version", "1.0.0"),
            status="running",
            options=self.config.get("options"),
        )

        # Ensure connection
        if not self.backend.is_connected():
            self.backend.connect()
            self.backend.initialize_schema()

        # Create run
        self.run_id = self.backend.create_run(run)

        # Get nodes and edges from state
        nodes = list(state.nodes.values()) if hasattr(state.nodes, 'values') else state.nodes
        edges = state.edges

        # Insert
        self.node_count = self.backend.insert_nodes(self.run_id, nodes)
        self.edge_count = self.backend.insert_edges(self.run_id, edges)

        # Mark complete
        self.backend.update_run(
            self.run_id,
            status="completed",
            completed_at=datetime.now(),
            node_count=self.node_count,
            edge_count=self.edge_count,
        )

        # Update state metadata
        if hasattr(state, "metadata"):
            state.metadata["persistence"] = {
                "run_id": self.run_id,
                "nodes_persisted": self.node_count,
                "edges_persisted": self.edge_count,
            }

        return state

    def get_run_id(self) -> Optional[str]:
        """Get the created run ID."""
        return self.run_id

    def print_summary(self):
        """Print persistence summary."""
        print(f"  [Persistence] Run ID: {self.run_id}")
        print(f"  [Persistence] Persisted {self.node_count} nodes, {self.edge_count} edges")


def update_file_hashes(tracker: DeltaTracker, project_path: str,
                       run_id: str, delta) -> int:
    """
    Update file hashes after successful analysis.

    Args:
        tracker: DeltaTracker instance
        project_path: Project root
        run_id: Analysis run ID
        delta: DeltaResult from detection

    Returns:
        Number of files updated
    """
    # Get current hashes for changed/new files
    from ..incremental.hasher import FileHasher
    hasher = FileHasher()

    files_to_update = set(delta.changed_files) | set(delta.new_files)
    all_hashes = hasher.hash_directory(Path(project_path))

    # Filter to only include analyzed files
    file_hashes = {
        path: hash_mtime
        for path, hash_mtime in all_hashes.items()
        if path in files_to_update or path in set(delta.unchanged_files)
    }

    # Update tracking
    updated = tracker.update_tracking(project_path, run_id, file_hashes)

    # Cleanup deleted
    if delta.deleted_files:
        tracker.cleanup_deleted(project_path, delta.deleted_files)

    return updated
