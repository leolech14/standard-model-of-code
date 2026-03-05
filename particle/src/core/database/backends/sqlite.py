"""
SQLite Backend for Collider Database.

Default backend - file-based, zero setup required.
Optimized for single-user, local analysis with WAL mode.
"""
import hashlib
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from .base import DatabaseBackend, AnalysisRun, TrackedFile, DeltaResult
from ..models import get_schema_sql
from ..models.mappers import iter_nodes_to_rows, iter_edges_to_rows, row_to_node, row_to_edge


class SQLiteBackend(DatabaseBackend):
    """
    SQLite implementation of DatabaseBackend.

    Features:
    - WAL mode for better concurrency
    - Batch inserts for performance
    - Full-text search via FTS5 (optional)
    """

    def __init__(self, config):
        super().__init__(config)
        self._conn: Optional[sqlite3.Connection] = None
        self._db_path: Optional[Path] = None
        self._in_transaction: bool = False

    # =========================================================================
    # Connection Management
    # =========================================================================

    def connect(self) -> bool:
        """Connect to SQLite database, creating it if needed."""
        if self._conn is not None:
            return True

        self._db_path = self.config.get_sqlite_path()

        # Ensure parent directory exists
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._conn = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
                timeout=30.0
            )
            self._conn.row_factory = sqlite3.Row

            # Optimize for performance
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute("PRAGMA cache_size=10000")
            self._conn.execute("PRAGMA temp_store=MEMORY")
            self._conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            self._conn.execute("PRAGMA foreign_keys=ON")  # Enable FK enforcement

            self._connected = True
            return True

        except sqlite3.Error as e:
            print(f"SQLite connection error: {e}")
            # Close connection if it was opened but PRAGMA failed
            if self._conn:
                try:
                    self._conn.close()
                except sqlite3.Error:
                    pass
                self._conn = None
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close database connection."""
        if self._conn:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass
            self._conn = None
            self._connected = False

    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._conn is not None and self._connected

    def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        if not self.is_connected():
            return {"status": "disconnected"}

        start = time.time()
        try:
            self._conn.execute("SELECT 1")
            latency_ms = (time.time() - start) * 1000

            # Get counts
            cursor = self._conn.execute("SELECT COUNT(*) FROM analysis_runs")
            run_count = cursor.fetchone()[0]

            cursor = self._conn.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]

            return {
                "status": "healthy",
                "backend": "sqlite",
                "path": str(self._db_path),
                "latency_ms": round(latency_ms, 2),
                "runs": run_count,
                "nodes": node_count,
            }
        except sqlite3.Error as e:
            return {"status": "error", "error": str(e)}

    # =========================================================================
    # Transaction Management
    # =========================================================================

    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if not self.is_connected():
            return
        if not self._in_transaction:
            self._conn.execute("BEGIN TRANSACTION")
            self._in_transaction = True

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        if not self.is_connected():
            return
        if self._in_transaction:
            self._conn.commit()
            self._in_transaction = False

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if not self.is_connected():
            return
        if self._in_transaction:
            self._conn.rollback()
            self._in_transaction = False

    def _maybe_commit(self) -> None:
        """Commit only if not in an explicit transaction."""
        if not self._in_transaction and self._conn:
            self._conn.commit()

    # =========================================================================
    # Schema Management
    # =========================================================================

    def initialize_schema(self) -> bool:
        """Create tables if they don't exist."""
        if not self.is_connected():
            return False

        try:
            schema_sql = get_schema_sql()
            self._conn.executescript(schema_sql)
            self._maybe_commit()
            return True
        except sqlite3.Error as e:
            print(f"Schema initialization error: {e}")
            return False

    def get_schema_version(self) -> int:
        """Get current schema version."""
        if not self.is_connected():
            return 0

        try:
            cursor = self._conn.execute(
                "SELECT MAX(version) FROM schema_version"
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except sqlite3.Error:
            return 0

    def migrate_to(self, version: int) -> bool:
        """Migrate schema to target version."""
        current = self.get_schema_version()
        if current >= version:
            return True

        # Migrations would be applied here
        # For now, just update version
        try:
            self._conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, description) VALUES (?, ?)",
                (version, f"Migration to v{version}")
            )
            self._maybe_commit()
            return True
        except sqlite3.Error:
            return False

    # =========================================================================
    # Analysis Runs
    # =========================================================================

    def create_run(self, run: AnalysisRun) -> str:
        """Create a new analysis run record."""
        if not self.is_connected():
            self.connect()
            self.initialize_schema()

        try:
            self._conn.execute(
                """INSERT INTO analysis_runs
                   (id, project_name, project_path, started_at, collider_version,
                    status, options_json, metadata_json,
                    git_commit, git_branch, git_dirty, git_summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run.id,
                    run.project_name,
                    run.project_path,
                    run.started_at.isoformat() if run.started_at else None,
                    run.collider_version,
                    run.status,
                    json.dumps(run.options) if run.options else None,
                    json.dumps(run.metadata) if run.metadata else None,
                    run.git_commit,
                    run.git_branch,
                    1 if run.git_dirty else 0,
                    run.git_summary,
                )
            )
            self._maybe_commit()
            return run.id
        except sqlite3.Error as e:
            print(f"Error creating run: {e}")
            return run.id

    # Allowlist of columns that can be updated (SQL injection prevention)
    ALLOWED_RUN_COLUMNS = {
        "status", "completed_at", "node_count", "edge_count",
        "options", "metadata", "collider_version",
        "git_commit", "git_branch", "git_dirty", "git_summary", "delta_json",
    }

    def update_run(self, run_id: str, **updates) -> bool:
        """Update an existing run."""
        if not self.is_connected():
            return False

        # Validate column names against allowlist (SQL injection prevention)
        for key in updates.keys():
            base_key = key.replace("_json", "") if key.endswith("_json") else key
            if base_key not in self.ALLOWED_RUN_COLUMNS:
                print(f"Warning: Ignoring invalid column '{key}' in update_run")
                continue

        # Build SET clause dynamically
        set_parts = []
        values = []

        for key, value in updates.items():
            base_key = key.replace("_json", "") if key.endswith("_json") else key
            if base_key not in self.ALLOWED_RUN_COLUMNS:
                continue  # Skip invalid columns

            if key in ("options", "metadata"):
                set_parts.append(f"{key}_json = ?")
                values.append(json.dumps(value))
            elif key == "completed_at" and isinstance(value, datetime):
                set_parts.append(f"{key} = ?")
                values.append(value.isoformat())
            else:
                set_parts.append(f"{key} = ?")
                values.append(value)

        if not set_parts:
            return True

        values.append(run_id)

        try:
            self._conn.execute(
                f"UPDATE analysis_runs SET {', '.join(set_parts)} WHERE id = ?",
                values
            )
            self._maybe_commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating run: {e}")
            return False

    def get_run(self, run_id: str) -> Optional[AnalysisRun]:
        """Get a run by ID."""
        if not self.is_connected():
            return None

        try:
            cursor = self._conn.execute(
                "SELECT * FROM analysis_runs WHERE id = ?", (run_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            return self._row_to_run(dict(row))
        except sqlite3.Error:
            return None

    def get_runs(self, project_path: Optional[str] = None, limit: int = 10) -> List[AnalysisRun]:
        """Get recent runs, optionally filtered by project."""
        if not self.is_connected():
            return []

        try:
            if project_path:
                cursor = self._conn.execute(
                    """SELECT * FROM analysis_runs
                       WHERE project_path = ?
                       ORDER BY started_at DESC LIMIT ?""",
                    (project_path, limit)
                )
            else:
                cursor = self._conn.execute(
                    """SELECT * FROM analysis_runs
                       ORDER BY started_at DESC LIMIT ?""",
                    (limit,)
                )

            return [self._row_to_run(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_latest_run(self, project_path: str) -> Optional[AnalysisRun]:
        """Get the most recent completed run for a project."""
        if not self.is_connected():
            return None

        try:
            cursor = self._conn.execute(
                """SELECT * FROM analysis_runs
                   WHERE project_path = ? AND status = 'completed'
                   ORDER BY started_at DESC LIMIT 1""",
                (project_path,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_run(dict(row))
        except sqlite3.Error:
            return None

    def _row_to_run(self, row: Dict) -> AnalysisRun:
        """Convert DB row to AnalysisRun."""
        return AnalysisRun(
            id=row["id"],
            project_name=row["project_name"],
            project_path=row["project_path"],
            started_at=datetime.fromisoformat(row["started_at"]) if row.get("started_at") else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row.get("completed_at") else None,
            collider_version=row.get("collider_version", "1.0.0"),
            status=row.get("status", "unknown"),
            node_count=row.get("node_count", 0),
            edge_count=row.get("edge_count", 0),
            options=json.loads(row["options_json"]) if row.get("options_json") else None,
            metadata=json.loads(row["metadata_json"]) if row.get("metadata_json") else None,
            git_commit=row.get("git_commit"),
            git_branch=row.get("git_branch"),
            git_dirty=bool(row.get("git_dirty", 0)),
            git_summary=row.get("git_summary"),
            delta_json=row.get("delta_json"),
        )

    # =========================================================================
    # Nodes
    # =========================================================================

    def insert_nodes(self, run_id: str, nodes: List[Dict[str, Any]]) -> int:
        """Insert nodes in batch using memory-efficient generator."""
        if not nodes or not self.is_connected():
            return 0

        batch_size = self.config.batch_size
        inserted = 0
        batch = []

        try:
            # Use generator to avoid loading all rows into memory at once
            for row in iter_nodes_to_rows(nodes, run_id):
                batch.append(row)
                if len(batch) >= batch_size:
                    self._conn.executemany(
                        """INSERT OR REPLACE INTO nodes
                           (id, run_id, name, kind, file_path, start_line, end_line,
                            role, role_confidence, atom, ring, level,
                            in_degree, out_degree, pagerank, betweenness,
                            complexity, q_score, dimensions_json, metadata_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        batch
                    )
                    inserted += len(batch)
                    batch = []

            # Insert remaining rows
            if batch:
                self._conn.executemany(
                    """INSERT OR REPLACE INTO nodes
                       (id, run_id, name, kind, file_path, start_line, end_line,
                        role, role_confidence, atom, ring, level,
                        in_degree, out_degree, pagerank, betweenness,
                        complexity, q_score, dimensions_json, metadata_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    batch
                )
                inserted += len(batch)

            self._maybe_commit()
            return inserted
        except sqlite3.Error as e:
            print(f"Error inserting nodes: {e}")
            return inserted

    # Allowlist of node filter columns (SQL injection prevention)
    ALLOWED_NODE_FILTERS = {"role", "kind", "ring", "atom", "file_path", "level", "name"}

    def get_nodes(self, run_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get nodes for a run."""
        if not self.is_connected():
            return []

        query = "SELECT * FROM nodes WHERE run_id = ?"
        params = [run_id]

        if filters:
            for key, value in filters.items():
                # Validate against allowlist (SQL injection prevention)
                if key in self.ALLOWED_NODE_FILTERS:
                    query += f" AND {key} = ?"
                    params.append(value)

        try:
            cursor = self._conn.execute(query, params)
            return [row_to_node(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_node(self, run_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a single node by ID."""
        if not self.is_connected():
            return None

        try:
            cursor = self._conn.execute(
                "SELECT * FROM nodes WHERE run_id = ? AND id = ?",
                (run_id, node_id)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return row_to_node(dict(row))
        except sqlite3.Error:
            return None

    # =========================================================================
    # Edges
    # =========================================================================

    def insert_edges(self, run_id: str, edges: List[Dict[str, Any]]) -> int:
        """Insert edges in batch using memory-efficient generator."""
        if not edges or not self.is_connected():
            return 0

        batch_size = self.config.batch_size
        inserted = 0
        batch = []

        try:
            # Use generator to avoid loading all rows into memory at once
            for row in iter_edges_to_rows(edges, run_id):
                batch.append(row)
                if len(batch) >= batch_size:
                    self._conn.executemany(
                        """INSERT OR REPLACE INTO edges
                           (run_id, source_id, target_id, edge_type, weight, confidence, metadata_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        batch
                    )
                    inserted += len(batch)
                    batch = []

            # Insert remaining rows
            if batch:
                self._conn.executemany(
                    """INSERT OR REPLACE INTO edges
                       (run_id, source_id, target_id, edge_type, weight, confidence, metadata_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    batch
                )
                inserted += len(batch)

            self._maybe_commit()
            return inserted
        except sqlite3.Error as e:
            print(f"Error inserting edges: {e}")
            return inserted

    # Allowlist of edge filter columns (SQL injection prevention)
    ALLOWED_EDGE_FILTERS = {"edge_type", "source_id", "target_id"}

    def get_edges(self, run_id: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get edges for a run."""
        if not self.is_connected():
            return []

        query = "SELECT * FROM edges WHERE run_id = ?"
        params = [run_id]

        if filters:
            for key, value in filters.items():
                # Validate against allowlist (SQL injection prevention)
                if key in self.ALLOWED_EDGE_FILTERS:
                    query += f" AND {key} = ?"
                    params.append(value)

        try:
            cursor = self._conn.execute(query, params)
            return [row_to_edge(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    # =========================================================================
    # File Tracking (Incremental)
    # =========================================================================

    def get_tracked_files(self, project_path: str) -> Dict[str, TrackedFile]:
        """Get all tracked files for a project."""
        if not self.is_connected():
            return {}

        try:
            cursor = self._conn.execute(
                "SELECT * FROM tracked_files WHERE project_path = ?",
                (project_path,)
            )

            result = {}
            for row in cursor.fetchall():
                row_dict = dict(row)
                tf = TrackedFile(
                    id=row_dict["id"],
                    project_path=row_dict["project_path"],
                    relative_path=row_dict["relative_path"],
                    blake3_hash=row_dict["blake3_hash"],
                    modified_ts=row_dict["modified_ts"],
                    last_analyzed_run=row_dict.get("last_analyzed_run"),
                )
                result[tf.relative_path] = tf

            return result
        except sqlite3.Error:
            return {}

    def update_tracked_files(self, project_path: str, files: List[TrackedFile]) -> int:
        """Update tracked files (upsert)."""
        if not files or not self.is_connected():
            return 0

        try:
            rows = [
                (f.id, project_path, f.relative_path, f.blake3_hash,
                 f.modified_ts, f.last_analyzed_run)
                for f in files
            ]

            self._conn.executemany(
                """INSERT OR REPLACE INTO tracked_files
                   (id, project_path, relative_path, blake3_hash, modified_ts, last_analyzed_run)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                rows
            )
            self._maybe_commit()
            return len(files)
        except sqlite3.Error as e:
            print(f"Error updating tracked files: {e}")
            return 0

    def delete_tracked_files(self, project_path: str, relative_paths: List[str]) -> int:
        """Delete tracked files that no longer exist."""
        if not relative_paths or not self.is_connected():
            return 0

        try:
            placeholders = ",".join("?" * len(relative_paths))
            self._conn.execute(
                f"""DELETE FROM tracked_files
                    WHERE project_path = ? AND relative_path IN ({placeholders})""",
                [project_path] + relative_paths
            )
            self._maybe_commit()
            return len(relative_paths)
        except sqlite3.Error:
            return 0

    # =========================================================================
    # Query Operations
    # =========================================================================

    def search_nodes(self, query: str, run_id: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search nodes by name or file path.

        Args:
            query: Search string (matches name or file_path)
            run_id: Optional run to search in (defaults to latest)
            limit: Max results

        Returns:
            List of matching nodes
        """
        if not self.is_connected():
            return []

        try:
            if run_id:
                cursor = self._conn.execute(
                    """SELECT * FROM nodes
                       WHERE run_id = ? AND (name LIKE ? OR file_path LIKE ?)
                       LIMIT ?""",
                    (run_id, f"%{query}%", f"%{query}%", limit)
                )
            else:
                # Search across latest run per project
                cursor = self._conn.execute(
                    """SELECT n.* FROM nodes n
                       JOIN latest_runs lr ON n.run_id = lr.id
                       WHERE n.name LIKE ? OR n.file_path LIKE ?
                       LIMIT ?""",
                    (f"%{query}%", f"%{query}%", limit)
                )

            return [row_to_node(dict(row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    # =========================================================================
    # Retention / Purge
    # =========================================================================

    def purge_old_runs(self, project_path: Optional[str] = None) -> int:
        """
        Archive/purge old runs per retention policy in config.

        Two axes (0 = disabled):
        1. retention_max_runs  -- archive excess runs (keep metadata, drop nodes/edges)
        2. retention_max_days  -- hard-delete archived runs older than 2x max_days

        Archived runs retain git context and delta summaries for timeline queries.
        """
        if not self.is_connected():
            return 0

        max_runs = self.config.retention_max_runs
        max_days = self.config.retention_max_days

        if max_runs <= 0 and max_days <= 0:
            return 0  # Both disabled

        purged = 0

        try:
            # --- Hard-delete archived runs older than 2x max_days ---
            if max_days > 0:
                from datetime import timedelta
                hard_cutoff = (datetime.now() - timedelta(days=max_days * 2)).isoformat()

                if project_path:
                    cursor = self._conn.execute(
                        """DELETE FROM analysis_runs
                           WHERE project_path = ? AND status = 'archived'
                           AND started_at < ?""",
                        (project_path, hard_cutoff)
                    )
                else:
                    cursor = self._conn.execute(
                        """DELETE FROM analysis_runs
                           WHERE status = 'archived' AND started_at < ?""",
                        (hard_cutoff,)
                    )
                purged += cursor.rowcount

            # --- Count-based archive (per project) ---
            if max_runs > 0:
                if project_path:
                    projects = [project_path]
                else:
                    cursor = self._conn.execute(
                        "SELECT DISTINCT project_path FROM analysis_runs"
                    )
                    projects = [row[0] for row in cursor.fetchall()]

                for proj in projects:
                    # Find non-archived run IDs beyond the keep limit
                    cursor = self._conn.execute(
                        """SELECT id FROM analysis_runs
                           WHERE project_path = ? AND status != 'archived'
                           ORDER BY started_at DESC
                           LIMIT -1 OFFSET ?""",
                        (proj, max_runs)
                    )
                    excess_ids = [row[0] for row in cursor.fetchall()]

                    for run_id in excess_ids:
                        self._conn.execute("DELETE FROM nodes WHERE run_id = ?", (run_id,))
                        self._conn.execute("DELETE FROM edges WHERE run_id = ?", (run_id,))
                        self._conn.execute(
                            "UPDATE analysis_runs SET status = 'archived', node_count = 0, edge_count = 0 WHERE id = ?",
                            (run_id,)
                        )
                        purged += 1

            self._maybe_commit()
            return purged

        except sqlite3.Error as e:
            print(f"Error purging old runs: {e}")
            return purged

    def compare_runs(self, run_id_1: str, run_id_2: str) -> Dict[str, Any]:
        """
        Compare two analysis runs.

        Returns:
            Dict with added, removed, changed node counts
        """
        if not self.is_connected():
            return {}

        try:
            # Get node IDs from each run
            cursor1 = self._conn.execute(
                "SELECT id FROM nodes WHERE run_id = ?", (run_id_1,)
            )
            ids1 = {row[0] for row in cursor1.fetchall()}

            cursor2 = self._conn.execute(
                "SELECT id FROM nodes WHERE run_id = ?", (run_id_2,)
            )
            ids2 = {row[0] for row in cursor2.fetchall()}

            added = ids2 - ids1
            removed = ids1 - ids2
            common = ids1 & ids2

            return {
                "run_1": run_id_1,
                "run_2": run_id_2,
                "added": len(added),
                "removed": len(removed),
                "common": len(common),
                "added_ids": list(added)[:20],
                "removed_ids": list(removed)[:20],
            }
        except sqlite3.Error:
            return {}
