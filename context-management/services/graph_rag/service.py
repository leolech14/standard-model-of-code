import os
import logging
from typing import List, Dict, Any
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

class GraphRAGService:
    """
    Graph Retrieval-Augmented Generation Service (S14).
    
    Provides the intelligence layer for querying the Unified Graph (Refinery + Collider).
    """

    def __init__(self, uri: str = "bolt://localhost:7687", auth: tuple = None):
        self.uri = os.getenv("NEO4J_URI", uri)
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.auth = auth if auth else (user, password)
        self._driver = None
        
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=self.auth)
            self._driver.verify_connectivity()
            logger.info(f"GraphRAG connected to {self.uri}")
        except Exception as e:
            logger.warning(f"GraphRAG failed to connect: {e}")
            self._driver = None

    def query(self, question: str) -> str:
        """
        Main entry point for GraphRAG queries.
        
        1. Vector Search (if embeddings available)
        2. Graph Traversal (Expansion)
        3. Context Synthesis
        """
        if not self._driver:
            return "Graph Storage is unavailable."

        # TODO: Implement full embedding logic or call EmbeddingEngine
        # For now, we rely on text search via Cypher if no vector index
        
        context = self._naive_text_search(question)
        return context

    def _naive_text_search(self, term: str) -> str:
        """
        Simple text search if vectors aren't ready.
        Searches Atom content for the query term.
        """
        query = """
        MATCH (a:Atom)
        WHERE toLower(a.content) CONTAINS toLower($term)
        RETURN a.content as content, a.relevance as score
        ORDER BY a.relevance DESC
        LIMIT 5
        """
        
        results = []
        with self._driver.session() as session:
            result = session.run(query, term=term)
            results = [record["content"] for record in result]
            
        return "\n---\n".join(results) if results else "No graph context found."

    def close(self):
        if self._driver:
            self._driver.close()
