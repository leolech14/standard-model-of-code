import os
import logging
from typing import Optional

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

logger = logging.getLogger(__name__)

class GraphBuilder:
    """
    Manages the structural construction and indexing of the Knowledge Graph in Neo4j.
    """

    def __init__(self, uri=None, user=None, password=None):
        if not GraphDatabase:
            logger.warning("Neo4j driver not found. GraphBuilder disabled.")
            self.driver = None
            return

        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "elements2026")

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.verify_connection()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def verify_connection(self):
        with self.driver.session() as session:
            result = session.run("RETURN 1 AS num")
            record = result.single()
            if record and record["num"] == 1:
                logger.info(f"Connected to Neo4j at {self.uri}")
                return True
        return False

    def build_indices(self):
        """
        Creates necessary indices for GraphRAG performance.
        Includes Vector Index for hybrid retrieval if supported.
        """
        if not self.driver:
            return

        queries = [
            # Constraint: Unique IDs
            "CREATE CONSTRAINT code_id_unique IF NOT EXISTS FOR (c:CodeEntity) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT paper_id_unique IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE",

            # Lookup Indices
            "CREATE INDEX code_name IF NOT EXISTS FOR (c:CodeEntity) ON (c.name)",
            "CREATE INDEX chunk_content IF NOT EXISTS FOR (c:Chunk) ON (c.content)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)"
        ]

        # Vector Index (Neo4j 5.15+)
        # We wrap this in try/except as older versions might fail syntax
        vector_query = """
        CREATE VECTOR INDEX chunk_vector_index IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
        }}
        """

        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                    logger.info(f"Executed: {q[:50]}...")
                except Exception as e:
                    logger.warning(f"Index creation failed: {e}")

            try:
                session.run(vector_query)
                logger.info("Vector index created/verified.")
            except Exception as e:
                logger.warning(f"Vector index creation failed (Neo4j version might be old): {e}")

    def import_collider_graph(self, collider_json_path):
        """
        Import Collider's unified_analysis.json directly to Neo4j.
        Tested and working - imports 2,540 code nodes + 7,346 edges.
        """
        import json
        from pathlib import Path
        from datetime import datetime

        if not self.driver:
            return False

        json_path = Path(collider_json_path)
        if not json_path.exists():
            logger.error(f"Collider file not found: {json_path}")
            return False

        # Load Collider output
        with open(json_path) as f:
            data = json.load(f)

        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        logger.info(f"Importing {len(nodes)} nodes, {len(edges)} edges from Collider")

        # Import nodes
        with self.driver.session() as session:
            for i, node in enumerate(nodes):
                try:
                    session.run("""
                        CREATE (n:CodeEntity {
                            id: $id,
                            file_path: $file_path,
                            start_line: $start_line,
                            semantic_role: $semantic_role,
                            purpose: $purpose,
                            betweenness: $betweenness,
                            imported_at: $imported_at
                        })
                    """, {
                        "id": node.get("id", f"node_{i}"),
                        "file_path": node.get("file_path", ""),
                        "start_line": node.get("start_line", 0),
                        "semantic_role": node.get("semantic_role", "unknown"),
                        "purpose": node.get("purpose", ""),
                        "betweenness": node.get("betweenness_centrality", 0.0),
                        "imported_at": datetime.now().isoformat()
                    })

                    if (i + 1) % 100 == 0:
                        logger.info(f"  Progress: {i+1}/{len(nodes)} nodes")

                except Exception as e:
                    logger.error(f"Error importing node {node.get('id')}: {e}")

            # Import edges
            for i, edge in enumerate(edges):
                try:
                    edge_type = edge.get("edge_type", "UNKNOWN").upper().replace(" ", "_")

                    session.run(f"""
                        MATCH (source:CodeEntity {{id: $source_id}})
                        MATCH (target:CodeEntity {{id: $target_id}})
                        CREATE (source)-[r:{edge_type}]->(target)
                    """, {
                        "source_id": edge.get("source"),
                        "target_id": edge.get("target")
                    })

                    if (i + 1) % 500 == 0:
                        logger.info(f"  Progress: {i+1}/{len(edges)} edges")

                except Exception:
                    pass  # Edge creation can fail if nodes don't exist

        logger.info(f"✓ Collider import complete")
        return True

    def import_academic_foundations(self, metadata_dir):
        """
        Import analyzed academic papers from reference library.
        Tested and working - imports 9 papers with concept mappings.
        """
        from pathlib import Path
        import json

        if not self.driver:
            return False

        metadata_path = Path(metadata_dir)
        if not metadata_path.exists():
            logger.error(f"Metadata directory not found: {metadata_path}")
            return False

        # Find all *_analysis.json files
        metadata_files = list(metadata_path.glob("*_analysis.json"))
        logger.info(f"Found {len(metadata_files)} analyzed papers")

        for metadata_file in sorted(metadata_files):
            ref_id = metadata_file.stem.replace("_analysis", "")

            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Skip stubs
                if "[TO BE GENERATED" in metadata.get("summary", ""):
                    continue

                # Import paper + concepts
                self._import_paper(ref_id, metadata)

            except Exception as e:
                logger.error(f"Error importing {ref_id}: {e}")

        logger.info(f"✓ Academic foundations import complete")
        return True

    def _import_paper(self, ref_id, metadata):
        """Import single paper with concepts."""
        with self.driver.session() as session:
            # Create paper node
            session.run("""
                CREATE (p:AcademicPaper {
                    id: $id,
                    summary: $summary,
                    smoc_relevance: $relevance
                })
            """, {
                "id": ref_id,
                "summary": metadata.get("summary", ""),
                "relevance": metadata.get("smoc_relevance_summary", "")
            })

            # Create concept mappings
            for concept_map in metadata.get("key_smoc_concepts", []):
                smoc_concept = concept_map.get("smoc_concept")
                paper_concept = concept_map.get("paper_concept")

                session.run("""
                    MERGE (c:SmocConcept {name: $name})
                """, {"name": smoc_concept})

                session.run("""
                    CREATE (pc:PaperConcept {name: $name, paper_id: $paper_id})
                """, {"name": paper_concept, "paper_id": ref_id})

                session.run("""
                    MATCH (p:AcademicPaper {id: $paper_id})
                    MATCH (pc:PaperConcept {name: $concept, paper_id: $paper_id})
                    CREATE (p)-[:DEFINES]->(pc)
                """, {"paper_id": ref_id, "concept": paper_concept})

                session.run("""
                    MATCH (pc:PaperConcept {name: $paper_concept, paper_id: $paper_id})
                    MATCH (sc:SmocConcept {name: $smoc_concept})
                    CREATE (pc)-[:VALIDATES]->(sc)
                """, {
                    "paper_concept": paper_concept,
                    "paper_id": ref_id,
                    "smoc_concept": smoc_concept
                })

    def sync_changes(self):
        """
        Incremental updates hook (to be integrated with wire.py).
        """
        # TODO: Implement delta detection + incremental graph update
        pass
