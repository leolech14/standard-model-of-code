from pathlib import Path
import json
import sqlite3
import lancedb
from rich.console import Console

console = Console()

class GraphRAGRetriever:
    """The Retrieval API for standard agents querying the Standard Model of Code."""

    def __init__(self, db_dir: Path):
        self.sql_db_path = db_dir / "collider.db"
        self.vector_dir = db_dir / "vectors"

        self.table_name = "collider_nodes"
        self._latest_run_id = None

        try:
            self.db = lancedb.connect(str(self.vector_dir))
        except Exception as e:
            self.db = None
            console.print(f"[red]⚠️ Could not connect to LanceDB at {self.vector_dir}:[/red] {e}")

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        except ImportError:
            console.print("[red]⚠️ sentence-transformers not installed. Vector search unavailable.[/red]")
            self.model = None

    def _get_latest_run_id(self) -> str | None:
        """Returns the most recent analysis run_id from the SQLite DB."""
        if self._latest_run_id:
            return self._latest_run_id
        if not self.sql_db_path.exists():
            return None
        conn = sqlite3.connect(self.sql_db_path)
        row = conn.execute("SELECT run_id FROM nodes ORDER BY rowid DESC LIMIT 1").fetchone()
        conn.close()
        self._latest_run_id = row[0] if row else None
        return self._latest_run_id

    def _get_embedding(self, text: str) -> list[float]:
        if not self.model: return []
        try:
            embeddings = self.model.encode([text], normalize_embeddings=True)
            return embeddings[0].tolist()
        except Exception as e:
            console.print(f"[red]⚠️ Query embedding failed:[/red] {e}")
            return []

    def _read_source_snippet(self, file_path: str, start_line: int, end_line: int, max_lines: int = 50) -> str:
        """Extract source code from disk using line range from the AST database."""
        try:
            p = Path(file_path)
            if not p.exists():
                return ""
            lines = p.read_text().splitlines()
            # Clamp to max_lines to keep token budget sane
            actual_end = min(end_line, start_line + max_lines)
            snippet = lines[max(0, start_line - 1):actual_end]
            return "\n".join(snippet)
        except Exception:
            return ""

    def _hydrate_with_source(self, results: list[dict]) -> list[dict]:
        """Look up start_line/end_line in SQLite and attach source code snippets."""
        if not self.sql_db_path.exists():
            return results

        run_id = self._get_latest_run_id()
        conn = sqlite3.connect(self.sql_db_path)

        for res in results:
            node_id = res.get("id", "")
            query = "SELECT start_line, end_line FROM nodes WHERE id = ?"
            params = [node_id]
            if run_id:
                query += " AND run_id = ?"
                params.append(run_id)
            query += " LIMIT 1"

            row = conn.execute(query, params).fetchone()
            if row and row[0] and row[1]:
                res["start_line"] = row[0]
                res["end_line"] = row[1]
                res["code_snippet"] = self._read_source_snippet(
                    res.get("file_path", ""), row[0], row[1]
                )
            else:
                res["start_line"] = None
                res["end_line"] = None
                res["code_snippet"] = ""

        conn.close()
        return results

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Semantic search against the vectorized codebase. Returns deduplicated results with source snippets."""
        if not self.db or self.table_name not in self.db.table_names():
            console.print(f"[red]⚠️ Vector index '{self.table_name}' not found. Run `collider full` first.[/red]")
            return []

        vec = self._get_embedding(query)
        if not vec:
            return []

        tbl = self.db.open_table(self.table_name)
        # Over-fetch to account for duplicates, then dedup
        raw_results = tbl.search(vec).limit(limit * 10).to_list()

        # Deduplicate by (name, file_path) — keeps the closest match
        seen = set()
        deduped = []
        for res in raw_results:
            key = (res.get("name", ""), res.get("file_path", ""))
            if key not in seen:
                seen.add(key)
                deduped.append(res)
            if len(deduped) >= limit:
                break

        # Hydrate with source code snippets
        return self._hydrate_with_source(deduped)

    def neighborhood(self, node_id: str, depth: int = 1) -> dict:
        """Relational search. Returns adjacent nodes (callers and dependencies) via SQLite graph. Scoped to latest run."""
        if not self.sql_db_path.exists():
            console.print(f"[red]⚠️ No SQLite DB found at {self.sql_db_path}[/red]")
            return {}

        run_id = self._get_latest_run_id()
        conn = sqlite3.connect(self.sql_db_path)
        cursor = conn.cursor()

        # Scope edges to latest run_id
        if run_id:
            cursor.execute("SELECT target_id FROM edges WHERE source_id = ? AND run_id = ?", (node_id, run_id))
            dependencies = list(set(row[0] for row in cursor.fetchall()))

            cursor.execute("SELECT source_id FROM edges WHERE target_id = ? AND run_id = ?", (node_id, run_id))
            dependents = list(set(row[0] for row in cursor.fetchall()))
        else:
            cursor.execute("SELECT DISTINCT target_id FROM edges WHERE source_id = ?", (node_id,))
            dependencies = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT DISTINCT source_id FROM edges WHERE target_id = ?", (node_id,))
            dependents = [row[0] for row in cursor.fetchall()]

        # Hydrate signatures for these neighbors
        neighbors = set(dependencies + dependents)
        if not neighbors:
             conn.close()
             return {"message": "No neighbors found."}

        placeholders = ",".join(["?"] * len(neighbors))
        run_filter = f" AND run_id = '{run_id}'" if run_id else ""
        cursor.execute(
            f"SELECT DISTINCT id, name, kind, file_path FROM nodes WHERE id IN ({placeholders}){run_filter}",
            tuple(neighbors)
        )
        hydrated_nodes = [{"id": r[0], "name": r[1], "kind": r[2], "file_path": r[3]} for r in cursor.fetchall()]

        conn.close()
        return {
            "focal_node": node_id,
            "dependencies": dependencies,
            "callers": dependents,
            "nodes": hydrated_nodes
        }
