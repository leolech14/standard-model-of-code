import os
import logging
import time
from typing import List, Dict, Any
from neo4j import GraphDatabase
from ai.aci.schema import RefineryNode

# Configure logging
logger = logging.getLogger(__name__)

class Neo4jPublisher:
    """
    Publishes Refinery Atoms (RefineryNodes) to a Neo4j Graph Store.
    Implements the 'Unification' stage of the Waybill Architecture.
    """

    def __init__(self, uri: str = "bolt://localhost:7687", auth: tuple = None):
        """
        Initialize the connection to Neo4j.
        Defaults to localhost/no-auth if not specified, but checks env vars.
        """
        self.uri = os.getenv("NEO4J_URI", uri)
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password") # Default dev password

        self.auth = auth if auth else (user, password)
        self.driver = None

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
            self._verify_connectivity()
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            self.driver = None

    def _verify_connectivity(self):
        """Check if we can actually talk to the database."""
        if self.driver:
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")

    def close(self):
        if self.driver:
            self.driver.close()

    def publish_atoms(self, atoms: List[RefineryNode], parcel_id: str, batch_id: str):
        """
        Transacts a list of atoms into the graph.

        Graph Schema:
        - (:Atom {id, type, content, ...})
        - (:Parcel {id})
        - (:Batch {id})

        Edges:
        - (Atom)-[:BELONGS_TO]->(Parcel)
        - (Atom)-[:GENERATED_IN]->(Batch)
        """
        if not self.driver:
            logger.warning("Neo4j driver not active. Skipping publication.")
            return

        if not atoms:
            return

        start_time = time.time()
        with self.driver.session() as session:
            try:
                session.execute_write(self._create_audit_nodes, parcel_id, batch_id)
                session.execute_write(self._ingest_atoms, atoms, parcel_id, batch_id)
                elapsed = time.time() - start_time
                logger.info(f"Published {len(atoms)} atoms to Neo4j (Batch: {batch_id})")

                # S16: Telemetry Node
                self.publish_telemetry(batch_id, len(atoms), elapsed)
            except Exception as e:
                logger.error(f"Failed to publish atoms: {e}")

    def publish_telemetry(self, batch_id: str, atoms_count: int, duration_seconds: float):
        """
        Publishes telemetry data for feedback loop (S16).
        Creates a :TelemetryEvent node linked to the :Batch.
        """
        if not self.driver:
            return

        with self.driver.session() as session:
            try:
                session.execute_write(
                    self._create_telemetry_node,
                    batch_id,
                    atoms_count,
                    duration_seconds
                )
                logger.info(f"Telemetry recorded: Batch {batch_id}, {atoms_count} atoms, {duration_seconds:.2f}s")
            except Exception as e:
                logger.warning(f"Failed to publish telemetry: {e}")

    @staticmethod
    def _create_telemetry_node(tx, batch_id: str, atoms_count: int, duration_seconds: float):
        """Creates a TelemetryEvent node and links it to the Batch."""
        tx.run("""
            MATCH (b:Batch {id: $batch_id})
            CREATE (t:TelemetryEvent {
                timestamp: timestamp(),
                atoms_count: $atoms_count,
                duration_seconds: $duration_seconds,
                event_type: 'publication_complete'
            })
            CREATE (t)-[:RECORDED_IN]->(b)
        """, batch_id=batch_id, atoms_count=atoms_count, duration_seconds=duration_seconds)

    @staticmethod
    def _create_audit_nodes(tx, parcel_id: str, batch_id: str):
        """Ensure the Parcel and Batch nodes exist."""
        # Merge Batch (The "Room")
        tx.run("""
            MERGE (b:Batch {id: $batch_id})
            ON CREATE SET b.created_at = timestamp()
        """, batch_id=batch_id)

        # Merge Parcel (The Identity)
        tx.run("""
            MERGE (p:Parcel {id: $parcel_id})
            ON CREATE SET p.created_at = timestamp()
        """, parcel_id=parcel_id)

    @staticmethod
    def _ingest_atoms(tx, atoms: List[RefineryNode], parcel_id: str, batch_id: str):
        """Batch ingest atoms and link them."""
        # Convert objects to dicts for Cypher UNWIND
        atom_dicts = [
            {
                "id": a.chunk_id,
                "type": a.chunk_type,
                "content": a.content,
                "start_line": a.start_line,
                "end_line": a.end_line,
                "relevance": a.relevance_score,
                "embedding": a.embedding if a.embedding else []
            }
            for a in atoms
        ]

        # The Query
        query = """
        UNWIND $atoms AS atom_data
        MERGE (a:Atom {id: atom_data.id})
        SET a.type = atom_data.type,
            a.content = atom_data.content,
            a.start_line = atom_data.start_line,
            a.end_line = atom_data.end_line,
            a.relevance = atom_data.relevance,
            a.embedding = atom_data.embedding,
            a.updated_at = timestamp()

        WITH a
        MATCH (p:Parcel {id: $parcel_id})
        MATCH (b:Batch {id: $batch_id})

        MERGE (a)-[:BELONGS_TO]->(p)
        MERGE (a)-[:GENERATED_IN]->(b)
        """

        tx.run(query, atoms=atom_dicts, parcel_id=parcel_id, batch_id=batch_id)
