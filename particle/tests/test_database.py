"""
Tests for the Collider Database Layer.

Tests cover:
- DatabaseConfig creation and defaults
- SQLite backend operations
- Incremental analysis (file hashing, delta tracking)
- Mappers (node/edge conversion)
"""
import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.core.database import DatabaseConfig, FeatureRegistry, create_database_manager
from src.core.database.backends.base import AnalysisRun, TrackedFile, DeltaResult
from src.core.database.backends.sqlite import SQLiteBackend
from src.core.database.models.mappers import (
    node_to_row, row_to_node, edge_to_row, row_to_edge,
    batch_nodes_to_rows, batch_edges_to_rows
)
from src.core.database.incremental import FileHasher


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_default_config(self):
        """Default config should enable SQLite with incremental."""
        config = DatabaseConfig()
        assert config.enabled is True
        assert config.backend == "sqlite"
        assert config.incremental_enabled is True
        assert config.history_enabled is True

    def test_from_options_no_db(self):
        """--no-db should disable database."""
        config = DatabaseConfig.from_options({"no_db": True})
        assert config.enabled is False

    def test_from_options_backend(self):
        """--db-backend should set backend."""
        config = DatabaseConfig.from_options({"db_backend": "postgres"})
        assert config.backend == "postgres"

    def test_from_options_incremental_off(self):
        """--no-incremental should disable incremental."""
        config = DatabaseConfig.from_options({"no_incremental": True})
        assert config.incremental_enabled is False

    def test_to_dict(self):
        """Config should serialize to dict."""
        config = DatabaseConfig()
        d = config.to_dict()
        assert d["enabled"] is True
        assert d["backend"] == "sqlite"


class TestFeatureRegistry:
    """Tests for FeatureRegistry."""

    def test_list_features(self):
        """Should list all features."""
        features = FeatureRegistry.list_features()
        assert len(features) >= 5
        assert any(f["id"] == "database" for f in features)
        assert any(f["id"] == "incremental" for f in features)

    def test_get_feature(self):
        """Should get feature by ID."""
        feature = FeatureRegistry.get_feature("sqlite")
        assert feature is not None
        assert feature.default is True

    def test_default_on(self):
        """Should return features that are on by default."""
        defaults = FeatureRegistry.get_default_on()
        assert len(defaults) >= 3
        assert all(f.default for f in defaults)


class TestSQLiteBackend:
    """Tests for SQLite backend."""

    @pytest.fixture
    def db(self):
        """Create a temp SQLite database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig()
            config.sqlite_path = str(Path(tmpdir) / "test.db")
            backend = SQLiteBackend(config)
            backend.connect()
            backend.initialize_schema()
            yield backend
            backend.disconnect()

    def test_connect(self, db):
        """Should connect successfully."""
        assert db.is_connected()

    def test_health_check(self, db):
        """Health check should return healthy status."""
        health = db.health_check()
        assert health["status"] == "healthy"
        assert health["backend"] == "sqlite"

    def test_create_and_get_run(self, db):
        """Should create and retrieve a run."""
        run = AnalysisRun(
            id="test_run_001",
            project_name="test",
            project_path="/tmp/test",
            started_at=datetime.now(),
        )
        run_id = db.create_run(run)
        assert run_id == "test_run_001"

        retrieved = db.get_run(run_id)
        assert retrieved is not None
        assert retrieved.project_name == "test"

    def test_insert_and_get_nodes(self, db):
        """Should insert and retrieve nodes."""
        # Create run first
        run = AnalysisRun(
            id="test_run",
            project_name="test",
            project_path="/tmp/test",
        )
        db.create_run(run)

        nodes = [
            {"id": "node1", "name": "TestClass", "kind": "class", "role": "Service"},
            {"id": "node2", "name": "helper", "kind": "function", "role": "Utility"},
        ]
        count = db.insert_nodes("test_run", nodes)
        assert count == 2

        retrieved = db.get_nodes("test_run")
        assert len(retrieved) == 2

    def test_insert_and_get_edges(self, db):
        """Should insert and retrieve edges."""
        run = AnalysisRun(
            id="test_run",
            project_name="test",
            project_path="/tmp/test",
        )
        db.create_run(run)

        edges = [
            {"source": "node1", "target": "node2", "type": "calls"},
        ]
        count = db.insert_edges("test_run", edges)
        assert count == 1

        retrieved = db.get_edges("test_run")
        assert len(retrieved) == 1
        assert retrieved[0]["source"] == "node1"

    def test_search_nodes(self, db):
        """Should search nodes by name."""
        run = AnalysisRun(id="test_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        nodes = [
            {"id": "node1", "name": "UserService", "kind": "class"},
            {"id": "node2", "name": "OrderService", "kind": "class"},
            {"id": "node3", "name": "helper", "kind": "function"},
        ]
        db.insert_nodes("test_run", nodes)

        results = db.search_nodes("Service", run_id="test_run")
        assert len(results) == 2

    def test_compare_runs(self, db):
        """Should compare two runs."""
        # Create two runs
        run1 = AnalysisRun(id="run1", project_name="test", project_path="/tmp/test")
        run2 = AnalysisRun(id="run2", project_name="test", project_path="/tmp/test")
        db.create_run(run1)
        db.create_run(run2)

        # Run 1 has nodes A, B
        db.insert_nodes("run1", [
            {"id": "nodeA", "name": "A", "kind": "class"},
            {"id": "nodeB", "name": "B", "kind": "class"},
        ])

        # Run 2 has nodes B, C
        db.insert_nodes("run2", [
            {"id": "nodeB", "name": "B", "kind": "class"},
            {"id": "nodeC", "name": "C", "kind": "class"},
        ])

        comparison = db.compare_runs("run1", "run2")
        assert comparison["added"] == 1  # C
        assert comparison["removed"] == 1  # A
        assert comparison["common"] == 1  # B

    def test_transaction_rollback(self, db):
        """Transaction should rollback on error, leaving no partial data."""
        # Verify empty state
        runs = db.get_runs()
        initial_run_count = len(runs)

        # Create a run with valid nodes but try to cause an edge insert failure
        # by mocking the insert_edges method to raise an exception
        original_insert_edges = db.insert_edges

        def failing_insert_edges(*args, **kwargs):
            raise sqlite3.Error("Simulated edge insert failure")

        db.insert_edges = failing_insert_edges

        # Try to persist - should fail and rollback
        metadata = {"project_name": "test", "target_path": "/tmp/test"}
        nodes = [{"id": "node1", "name": "Test", "kind": "class"}]
        edges = [{"source": "node1", "target": "node2", "type": "calls"}]

        with pytest.raises(sqlite3.Error):
            db.persist(nodes, edges, metadata)

        # Restore original method
        db.insert_edges = original_insert_edges

        # Verify no partial data was committed
        runs = db.get_runs()
        # After rollback, should have same number of runs (or one failed run)
        # The key is that nodes should NOT be committed without edges
        for run in runs[initial_run_count:]:
            if run.status == "failed":
                # Run was marked as failed - this is acceptable
                node_count = len(db.get_nodes(run.id))
                assert node_count == 0, "Failed run should have no nodes after rollback"

    def test_persist_transaction_success(self, db):
        """Persist should commit all data atomically on success."""
        metadata = {"project_name": "test", "target_path": "/tmp/test"}
        nodes = [
            {"id": "node1", "name": "ClassA", "kind": "class"},
            {"id": "node2", "name": "ClassB", "kind": "class"},
        ]
        edges = [{"source": "node1", "target": "node2", "type": "uses"}]

        run_id = db.persist(nodes, edges, metadata)

        # Verify all data was committed
        run = db.get_run(run_id)
        assert run is not None
        assert run.status == "completed"
        assert run.node_count == 2
        assert run.edge_count == 1

        retrieved_nodes = db.get_nodes(run_id)
        assert len(retrieved_nodes) == 2

        retrieved_edges = db.get_edges(run_id)
        assert len(retrieved_edges) == 1


class TestMappers:
    """Tests for node/edge mappers."""

    def test_node_to_row(self):
        """Should convert node dict to row format."""
        node = {
            "id": "test::node",
            "name": "TestClass",
            "kind": "class",
            "file_path": "src/test.py",
            "start_line": 10,
            "role": "Service",
            "role_confidence": 0.85,
            "custom_field": "value",
        }
        row = node_to_row(node)
        assert row["id"] == "test::node"
        assert row["name"] == "TestClass"
        assert row["role"] == "Service"
        assert "custom_field" not in row  # Should be in metadata_json
        assert row["metadata_json"] is not None
        metadata = json.loads(row["metadata_json"])
        assert metadata["custom_field"] == "value"

    def test_row_to_node(self):
        """Should convert row back to node dict."""
        row = {
            "id": "test::node",
            "name": "TestClass",
            "kind": "class",
            "role": "Service",
            "metadata_json": '{"custom_field": "value"}',
        }
        node = row_to_node(row)
        assert node["id"] == "test::node"
        assert node["custom_field"] == "value"

    def test_edge_to_row(self):
        """Should convert edge dict to row format."""
        edge = {
            "source": "node1",
            "target": "node2",
            "type": "calls",
            "weight": 1.5,
        }
        row = edge_to_row(edge)
        assert row["source_id"] == "node1"
        assert row["target_id"] == "node2"
        assert row["edge_type"] == "calls"
        assert row["weight"] == 1.5


class TestFileHasher:
    """Tests for file hasher."""

    def test_hash_file(self):
        """Should hash a single file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('hello')")
            f.flush()
            path = Path(f.name)

        hasher = FileHasher()
        hash_value = hasher.hash_file(path)
        assert hash_value is not None
        assert len(hash_value) == 64  # SHA-256 hex length

        path.unlink()

    def test_hash_directory(self):
        """Should hash all matching files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            (Path(tmpdir) / "test1.py").write_text("print(1)")
            (Path(tmpdir) / "test2.py").write_text("print(2)")
            (Path(tmpdir) / "test.txt").write_text("text")

            hasher = FileHasher()
            result = hasher.hash_directory(
                Path(tmpdir),
                patterns=["*.py"],
            )

            assert len(result) == 2
            assert "test1.py" in result
            assert "test2.py" in result


class TestDeltaResult:
    """Tests for DeltaResult."""

    def test_needs_analysis(self):
        """Should compute files needing analysis."""
        delta = DeltaResult(
            changed_files=["a.py", "b.py"],
            new_files=["c.py"],
            unchanged_files=["d.py", "e.py"],
            deleted_files=["f.py"],
        )
        needs = delta.needs_analysis
        assert len(needs) == 3
        assert "a.py" in needs
        assert "b.py" in needs
        assert "c.py" in needs
        assert "d.py" not in needs

    def test_total_changes(self):
        """Should count total changes."""
        delta = DeltaResult(
            changed_files=["a.py"],
            new_files=["b.py", "c.py"],
            unchanged_files=["d.py"],
            deleted_files=["e.py"],
        )
        assert delta.total_changes == 4  # 1 changed + 2 new + 1 deleted


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    @pytest.fixture
    def db(self):
        """Create a temp SQLite database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig()
            config.sqlite_path = str(Path(tmpdir) / "test.db")
            backend = SQLiteBackend(config)
            backend.connect()
            backend.initialize_schema()
            yield backend
            backend.disconnect()

    def test_unicode_in_node_names(self, db):
        """Should handle Unicode characters in node names."""
        run = AnalysisRun(id="unicode_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        nodes = [
            {"id": "node1", "name": "日本語クラス", "kind": "class"},
            {"id": "node2", "name": "Émoji™ Handler 🎉", "kind": "function"},
            {"id": "node3", "name": "Ελληνικά", "kind": "method"},
        ]
        count = db.insert_nodes("unicode_run", nodes)
        assert count == 3

        retrieved = db.get_nodes("unicode_run")
        assert len(retrieved) == 3
        names = {n["name"] for n in retrieved}
        assert "日本語クラス" in names
        assert "Émoji™ Handler 🎉" in names

    def test_large_batch_insertion(self, db):
        """Should handle large batch insertions efficiently."""
        run = AnalysisRun(id="large_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        # Create 1000 nodes
        nodes = [
            {"id": f"node_{i}", "name": f"Class{i}", "kind": "class", "role": "Service"}
            for i in range(1000)
        ]
        count = db.insert_nodes("large_run", nodes)
        assert count == 1000

        # Create 2000 edges
        edges = [
            {"source": f"node_{i}", "target": f"node_{i+1}", "type": "calls"}
            for i in range(999)
        ]
        edge_count = db.insert_edges("large_run", edges)
        assert edge_count == 999

    def test_context_manager(self):
        """Should work correctly as context manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig()
            config.sqlite_path = str(Path(tmpdir) / "test.db")

            with SQLiteBackend(config) as db:
                db.initialize_schema()
                assert db.is_connected()
                run = AnalysisRun(id="ctx_run", project_name="test", project_path="/tmp")
                db.create_run(run)

            # After exiting context, should be disconnected
            assert not db.is_connected()

    def test_empty_nodes_and_edges(self, db):
        """Should handle empty node/edge lists gracefully."""
        run = AnalysisRun(id="empty_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        assert db.insert_nodes("empty_run", []) == 0
        assert db.insert_edges("empty_run", []) == 0

    def test_special_characters_in_metadata(self, db):
        """Should handle special characters in metadata JSON."""
        run = AnalysisRun(id="special_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        nodes = [
            {
                "id": "node1",
                "name": "Test",
                "kind": "class",
                "description": 'Contains "quotes" and\nnewlines and\ttabs',
                "path": "C:\\Windows\\Path",
            },
        ]
        count = db.insert_nodes("special_run", nodes)
        assert count == 1

        retrieved = db.get_node("special_run", "node1")
        assert retrieved is not None
        assert "description" in retrieved
        assert "quotes" in retrieved["description"]

    def test_schema_version(self, db):
        """Should track schema version."""
        version = db.get_schema_version()
        assert version >= 1

    def test_migrate_to_same_version(self, db):
        """Migration to current version should succeed."""
        current = db.get_schema_version()
        result = db.migrate_to(current)
        assert result is True

    def test_get_nonexistent_run(self, db):
        """Should return None for nonexistent run."""
        run = db.get_run("nonexistent_run_12345")
        assert run is None

    def test_get_nonexistent_node(self, db):
        """Should return None for nonexistent node."""
        run = AnalysisRun(id="test_run", project_name="test", project_path="/tmp/test")
        db.create_run(run)

        node = db.get_node("test_run", "nonexistent_node")
        assert node is None

    def test_duplicate_run_id(self, db):
        """Should handle duplicate run IDs gracefully."""
        run1 = AnalysisRun(id="dup_run", project_name="test1", project_path="/tmp/test")
        run2 = AnalysisRun(id="dup_run", project_name="test2", project_path="/tmp/test")

        db.create_run(run1)
        # SQLite INSERT will fail or replace for duplicate primary key
        # The behavior depends on implementation
        run_id = db.create_run(run2)
        assert run_id == "dup_run"


class TestRetentionPolicy:
    """Tests for retention-based purging of old runs."""

    @pytest.fixture
    def db(self):
        """Create a temp SQLite database with retention enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig(
                retention_max_runs=3,
                retention_max_days=0,  # Disable age-based for count tests
            )
            config.sqlite_path = str(Path(tmpdir) / "test.db")
            backend = SQLiteBackend(config)
            backend.connect()
            backend.initialize_schema()
            yield backend
            backend.disconnect()

    def _create_run(self, db, run_id, project_path="/tmp/test", age_seconds=0):
        """Helper to create a run with a specific age."""
        from datetime import timedelta
        started = datetime.now() - timedelta(seconds=age_seconds)
        run = AnalysisRun(
            id=run_id,
            project_name="test",
            project_path=project_path,
            started_at=started,
            status="completed",
        )
        db.create_run(run)
        return run_id

    def test_purge_excess_runs_by_count(self, db):
        """Should purge runs beyond retention_max_runs per project."""
        # Create 5 runs (max is 3)
        for i in range(5):
            self._create_run(db, f"run_{i}", age_seconds=(4 - i) * 100)

        purged = db.purge_old_runs(project_path="/tmp/test")
        assert purged == 2  # 5 - 3 = 2 purged

        remaining = db.get_runs(project_path="/tmp/test", limit=100)
        assert len(remaining) == 3

    def test_purge_respects_project_scope(self, db):
        """Purge should scope retention per-project."""
        # Project A: 4 runs
        for i in range(4):
            self._create_run(db, f"a_{i}", project_path="/tmp/projA", age_seconds=(3 - i) * 100)
        # Project B: 2 runs
        for i in range(2):
            self._create_run(db, f"b_{i}", project_path="/tmp/projB", age_seconds=(1 - i) * 100)

        # Purge only project A
        purged = db.purge_old_runs(project_path="/tmp/projA")
        assert purged == 1  # 4 - 3 = 1

        # Project B untouched
        remaining_b = db.get_runs(project_path="/tmp/projB", limit=100)
        assert len(remaining_b) == 2

    def test_purge_all_projects(self, db):
        """Purge without project_path should purge across all projects."""
        for i in range(5):
            self._create_run(db, f"a_{i}", project_path="/tmp/projA", age_seconds=(4 - i) * 100)
        for i in range(4):
            self._create_run(db, f"b_{i}", project_path="/tmp/projB", age_seconds=(3 - i) * 100)

        purged = db.purge_old_runs()  # No project_path
        assert purged == 3  # A: 5-3=2, B: 4-3=1

    def test_purge_cascades_nodes_and_edges(self, db):
        """Purged runs should cascade-delete their nodes and edges."""
        # Create 4 runs with nodes
        for i in range(4):
            rid = self._create_run(db, f"run_{i}", age_seconds=(3 - i) * 100)
            db.insert_nodes(rid, [{"id": f"n_{i}", "name": f"Class{i}", "kind": "class"}])
            db.insert_edges(rid, [{"source": f"n_{i}", "target": f"n_{i}", "type": "self"}])

        # Before purge: 4 runs worth of nodes
        all_before = sum(len(db.get_nodes(f"run_{i}")) for i in range(4))
        assert all_before == 4

        purged = db.purge_old_runs(project_path="/tmp/test")
        assert purged == 1  # 4 - 3 = 1

        # Oldest run's nodes should be gone (cascaded)
        assert db.get_nodes("run_0") == []
        # Newest runs' nodes should remain
        assert len(db.get_nodes("run_3")) == 1

    def test_purge_by_age(self):
        """Should purge runs older than retention_max_days."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig(
                retention_max_runs=0,  # Disable count-based
                retention_max_days=7,  # 7-day retention
            )
            config.sqlite_path = str(Path(tmpdir) / "test.db")
            db = SQLiteBackend(config)
            db.connect()
            db.initialize_schema()

            # Create runs at various ages
            self._create_run(db, "recent", age_seconds=3600)           # 1 hour ago
            self._create_run(db, "week_old", age_seconds=8 * 86400)    # 8 days ago
            self._create_run(db, "month_old", age_seconds=30 * 86400)  # 30 days ago

            purged = db.purge_old_runs()
            assert purged == 2  # week_old + month_old

            remaining = db.get_runs(limit=100)
            assert len(remaining) == 1
            assert remaining[0].id == "recent"

            db.disconnect()

    def test_purge_both_axes(self):
        """Both count and age should apply together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DatabaseConfig(
                retention_max_runs=5,
                retention_max_days=3,
            )
            config.sqlite_path = str(Path(tmpdir) / "test.db")
            db = SQLiteBackend(config)
            db.connect()
            db.initialize_schema()

            # 2 old runs (>3 days) + 3 recent runs
            self._create_run(db, "old_1", age_seconds=5 * 86400)
            self._create_run(db, "old_2", age_seconds=4 * 86400)
            self._create_run(db, "new_1", age_seconds=7200)
            self._create_run(db, "new_2", age_seconds=3600)
            self._create_run(db, "new_3", age_seconds=1800)

            purged = db.purge_old_runs()
            # Age removes old_1, old_2 (>3 days)
            # Count: 3 remaining <= 5, so no further purge
            assert purged == 2

            remaining = db.get_runs(limit=100)
            assert len(remaining) == 3

            db.disconnect()

    def test_purge_disabled(self, db):
        """Should be a no-op when both retention values are 0."""
        db.config.retention_max_runs = 0
        db.config.retention_max_days = 0

        for i in range(10):
            self._create_run(db, f"run_{i}")

        purged = db.purge_old_runs()
        assert purged == 0

        remaining = db.get_runs(limit=100)
        assert len(remaining) == 10

    def test_purge_no_excess(self, db):
        """Should purge nothing when under the limit."""
        self._create_run(db, "run_1")
        self._create_run(db, "run_2")

        purged = db.purge_old_runs(project_path="/tmp/test")
        assert purged == 0
