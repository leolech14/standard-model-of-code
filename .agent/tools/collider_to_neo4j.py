#!/usr/bin/env python3
"""
Collider to Neo4j Importer - Phase 1 GraphRAG
==============================================

Imports Collider's unified_analysis.json directly into Neo4j.
No entity extraction needed - structure already in graph format!

Usage:
    python collider_to_neo4j.py <unified_analysis.json>
    python collider_to_neo4j.py .collider-full/output_llm*.json
"""

import json
import sys
from pathlib import Path
from neo4j import GraphDatabase
from datetime import datetime

# Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "elements2026"


class ColliderImporter:
    """Import Collider output to Neo4j."""

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "chunks_linked": 0,
            "errors": 0
        }

    def close(self):
        self.driver.close()

    def clear_database(self):
        """Clear all nodes and relationships."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared")

    def import_nodes(self, nodes):
        """Import code nodes from Collider."""
        print(f"Importing {len(nodes)} nodes...")

        with self.driver.session() as session:
            for i, node in enumerate(nodes):
                try:
                    # Create code entity node
                    session.run("""
                        CREATE (n:CodeEntity {
                            id: $id,
                            file_path: $file_path,
                            start_line: $start_line,
                            end_line: $end_line,
                            semantic_role: $semantic_role,
                            purpose: $purpose,
                            kind: $kind,
                            betweenness: $betweenness,
                            has_docstring: $has_docstring,
                            imported_at: $imported_at
                        })
                    """, {
                        "id": node.get("id", f"node_{i}"),
                        "file_path": node.get("file_path", ""),
                        "start_line": node.get("start_line", 0),
                        "end_line": node.get("end_line", 0),
                        "semantic_role": node.get("semantic_role", "unknown"),
                        "purpose": node.get("purpose", ""),
                        "kind": node.get("kind", ""),
                        "betweenness": node.get("betweenness_centrality", 0.0),
                        "has_docstring": node.get("has_docstring", False),
                        "imported_at": datetime.now().isoformat()
                    })

                    self.stats["nodes_created"] += 1

                    if (i + 1) % 100 == 0:
                        print(f"  Progress: {i+1}/{len(nodes)} nodes")

                except Exception as e:
                    print(f"  Error importing node {node.get('id')}: {e}")
                    self.stats["errors"] += 1

        print(f"✓ Imported {self.stats['nodes_created']} nodes")

    def import_edges(self, edges):
        """Import edges from Collider."""
        print(f"Importing {len(edges)} edges...")

        with self.driver.session() as session:
            for i, edge in enumerate(edges):
                try:
                    # Create relationship
                    edge_type = edge.get("edge_type", "UNKNOWN").upper().replace(" ", "_")

                    session.run(f"""
                        MATCH (source:CodeEntity {{id: $source_id}})
                        MATCH (target:CodeEntity {{id: $target_id}})
                        CREATE (source)-[r:{edge_type} {{
                            family: $family,
                            resolution: $resolution,
                            imported_at: $imported_at
                        }}]->(target)
                    """, {
                        "source_id": edge.get("source"),
                        "target_id": edge.get("target"),
                        "family": edge.get("family", ""),
                        "resolution": edge.get("resolution", ""),
                        "imported_at": datetime.now().isoformat()
                    })

                    self.stats["edges_created"] += 1

                    if (i + 1) % 500 == 0:
                        print(f"  Progress: {i+1}/{len(edges)} edges")

                except Exception as e:
                    # Edge creation can fail if nodes don't exist
                    self.stats["errors"] += 1

        print(f"✓ Imported {self.stats['edges_created']} edges ({self.stats['errors']} failed)")

    def link_chunks(self, chunks_dir):
        """Link semantic chunks to code nodes."""
        chunks_dir = Path(chunks_dir)
        total_linked = 0

        # Load all chunk files
        for chunk_file in chunks_dir.glob("*_chunks.json"):
            try:
                with open(chunk_file) as f:
                    data = json.load(f)

                chunks = data.get("nodes", [])
                print(f"Linking {len(chunks)} chunks from {chunk_file.name}...")

                with self.driver.session() as session:
                    for chunk in chunks:
                        try:
                            # Create chunk node
                            session.run("""
                                CREATE (c:Chunk {
                                    chunk_id: $chunk_id,
                                    content: $content,
                                    source_file: $source_file,
                                    chunk_type: $chunk_type,
                                    start_line: $start_line,
                                    relevance: $relevance
                                })
                            """, {
                                "chunk_id": chunk.get("chunk_id"),
                                "content": chunk.get("content", "")[:1000],  # Truncate for storage
                                "source_file": chunk.get("source_file"),
                                "chunk_type": chunk.get("chunk_type"),
                                "start_line": chunk.get("start_line", 0),
                                "relevance": chunk.get("relevance_score", 0.0)
                            })

                            # Link to code entity (if exists)
                            session.run("""
                                MATCH (chunk:Chunk {chunk_id: $chunk_id})
                                MATCH (code:CodeEntity)
                                WHERE code.file_path = $file_path
                                  AND code.start_line <= $start_line
                                  AND code.end_line >= $start_line
                                CREATE (code)-[:HAS_CHUNK]->(chunk)
                            """, {
                                "chunk_id": chunk.get("chunk_id"),
                                "file_path": chunk.get("source_file"),
                                "start_line": chunk.get("start_line", 0)
                            })

                            total_linked += 1

                        except Exception as e:
                            pass  # Chunk linking is best-effort

                print(f"  ✓ Linked {total_linked} chunks from {chunk_file.name}")

            except Exception as e:
                print(f"  Error processing {chunk_file}: {e}")

        self.stats["chunks_linked"] = total_linked

    def print_stats(self):
        """Print import statistics."""
        print("\n" + "=" * 60)
        print("IMPORT COMPLETE")
        print("=" * 60)
        print(f"Nodes created: {self.stats['nodes_created']}")
        print(f"Edges created: {self.stats['edges_created']}")
        print(f"Chunks linked: {self.stats['chunks_linked']}")
        print(f"Errors: {self.stats['errors']}")
        print("=" * 60)


def validate_file(file_path: Path) -> tuple[bool, str]:
    """Validate unified_analysis.json before import."""
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if len(nodes) == 0:
        return False, "No nodes found - file may be corrupted or wrong format"

    # Check node structure
    if nodes and "id" not in nodes[0]:
        return False, "Nodes missing 'id' field - incompatible format"

    return True, f"Valid: {len(nodes)} nodes, {len(edges)} edges"


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python collider_to_neo4j.py <unified_analysis.json>")
        print("       python collider_to_neo4j.py --validate <file>")
        print("\nCanonical path: .collider/unified_analysis.json")
        print("\nExample:")
        print("  python collider_to_neo4j.py .collider/unified_analysis.json")
        return 1

    # Handle --validate flag
    if sys.argv[1] == "--validate":
        if len(sys.argv) < 3:
            print("Usage: python collider_to_neo4j.py --validate <file>")
            return 1
        valid, msg = validate_file(Path(sys.argv[2]))
        print(f"Validation: {msg}")
        return 0 if valid else 1

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        return 1

    # Load Collider output
    print(f"Loading {input_file}...")
    with open(input_file) as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    print(f"Loaded: {len(nodes)} nodes, {len(edges)} edges")

    # Import to Neo4j
    importer = ColliderImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # Clear existing data (optional - comment out to preserve)
        # importer.clear_database()

        # Import nodes
        importer.import_nodes(nodes)

        # Import edges
        importer.import_edges(edges)

        # Link chunks (if they exist)
        chunks_dir = Path(".agent/intelligence/chunks")
        if chunks_dir.exists():
            importer.link_chunks(chunks_dir)

        # Print summary
        importer.print_stats()

    finally:
        importer.close()

    print("\n✓ Import complete. Access Neo4j at http://localhost:7474")
    print("  Query example: MATCH (n:CodeEntity) RETURN n LIMIT 25")

    return 0


if __name__ == "__main__":
    sys.exit(main())
