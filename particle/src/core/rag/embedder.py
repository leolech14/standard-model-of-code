import os
import json
from pathlib import Path
import sqlite3
import lancedb
from rich.console import Console

console = Console()

class GraphRAGEmbedder:
    """Stage 14: Semantic Vector Indexing for the Standard Model of Code."""

    def __init__(self, db_path: Path):
        self.sql_db_path = db_path

        # LanceDB lives locally next to the SQLite DB
        self.vector_dir = db_path.parent / "vectors"
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(str(self.vector_dir))

        self.table_name = "collider_nodes"

        console.print("   [dim]Loading local embedding model (BAAI/bge-small-en-v1.5)...[/dim]")
        try:
            from sentence_transformers import SentenceTransformer
            # BGE is fast, small (130MB), and top-tier for retrieval tasks
            self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        except ImportError:
            console.print("[red]⚠️ sentence-transformers not installed. Run `uv add sentence-transformers`[/red]")
            self.model = None

    def _get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            if not self.model: return []
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            console.print(f"      [red]⚠️ Embedding failed:[/red] {e}")
            return []

    def embed_graph(self):
        """Pulls nodes from SQLite, vectorizes them locally, and saves to LanceDB."""
        if not self.model: return

        if not self.sql_db_path.exists():
            console.print(f"      [red]⚠️ No SQLite DB found at {self.sql_db_path}[/red]")
            return

        console.print(f"\n[cyan]🧠 Stage 14: Semantic Vectorization (GraphRAG)[/cyan]...")

        try:
            conn = sqlite3.connect(self.sql_db_path)
            cursor = conn.cursor()

            # Get latest run_id to avoid embedding duplicates across runs
            latest_run = cursor.execute("SELECT run_id FROM nodes ORDER BY rowid DESC LIMIT 1").fetchone()
            run_id = latest_run[0] if latest_run else None

            if run_id:
                console.print(f"   → Scoping to latest run: {run_id}")
                cursor.execute("""
                    SELECT id, name, kind, role, file_path, metadata_json
                    FROM nodes
                    WHERE run_id = ?
                      AND (kind IN ('function', 'method', 'class')
                        OR role IN ('function', 'method', 'class'))
                """, (run_id,))
            else:
                cursor.execute("""
                    SELECT id, name, kind, role, file_path, metadata_json
                    FROM nodes
                    WHERE kind IN ('function', 'method', 'class')
                       OR role IN ('function', 'method', 'class')
                """)

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                console.print(f"   → No indexable nodes found.")
                return

            console.print(f"   → Vectorizing {len(rows)} structural nodes locally...")

            # 1. Define LanceDB Schema via PyArrow
            import pyarrow as pa
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("name", pa.string()),
                pa.field("type", pa.string()),
                pa.field("file_path", pa.string()),
                pa.field("semantic_payload", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), 384)) # bge-small output dimension
            ])

            # 2. Open or Create the table
            if self.table_name in self.db.table_names():
                tbl = self.db.open_table(self.table_name)
                # For simplicity in this iteration, we recreate the table to avoid stale vectors
                self.db.drop_table(self.table_name)

            tbl = self.db.create_table(self.table_name, schema=schema)

            # 3. Vectorize and Insert
            batch_payloads = []
            batch_metadata = []
            total_embedded = 0

            for row in rows:
                node_id, name, type_val, role, filepath, meta_json = row

                # Reconstruct semantic string for the embedder
                try:
                    import json
                    meta = json.loads(meta_json) if meta_json else {}
                    waybill = meta.get("waybill", meta)
                    purpose = waybill.get("purpose_intelligence", meta.get("purpose_intelligence", meta.get("purpose", "")))
                    sig = waybill.get("signature", meta.get("signature", ""))

                    payload = f"Node [{type_val}] {name} in {filepath}\nSignature: {sig}\nPurpose: {purpose}"
                except Exception:
                    payload = f"Node [{type_val}] {name} in {filepath}"

                batch_payloads.append(payload)
                batch_metadata.append({
                    "id": node_id,
                    "name": name,
                    "type": type_val,
                    "file_path": filepath,
                    "semantic_payload": payload
                })

                # Process in batches of 250 for speed
                if len(batch_payloads) >= 250:
                    vectors = self._get_embeddings_batch(batch_payloads)
                    if vectors:
                        for metadata, vec in zip(batch_metadata, vectors):
                            metadata["vector"] = vec
                        tbl.add(batch_metadata)
                        total_embedded += len(vectors)
                        console.print(f"   → Embedded {total_embedded}/{len(rows)} nodes...")

                    batch_payloads = []
                    batch_metadata = []

            if batch_payloads:
                vectors = self._get_embeddings_batch(batch_payloads)
                if vectors:
                    for metadata, vec in zip(batch_metadata, vectors):
                        metadata["vector"] = vec
                    tbl.add(batch_metadata)
                    total_embedded += len(vectors)
                    console.print(f"   → Embedded {total_embedded}/{len(rows)} nodes...")

            console.print(f"   [green]✅ GraphRAG Vectorization Complete.[/green]")

        except Exception as e:
             console.print(f"      [red]⚠️ Vectorization failed:[/red] {e}")
