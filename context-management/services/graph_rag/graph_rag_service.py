import os
import logging
from typing import List, Dict, Any

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

logger = logging.getLogger(__name__)

class GraphRAGService:
    """
    Service Tier 5: Graph-Structured Retrieval & Reasoning.
    Orchestrates queries against the Neo4j Knowledge Graph.
    """
    
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.environ.get("NEO4J_USER", "neo4j")
        self.password = os.environ.get("NEO4J_PASSWORD", "elements2026")
        
        if GraphDatabase:
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            except Exception as e:
                logger.warning(f"GraphRAG Service failed to connect: {e}")
                self.driver = None
        else:
            self.driver = None
            logger.warning("neo4j driver not installed.")

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, question: str, method: str = "auto") -> Dict[str, Any]:
        """
        Main entry point for GraphRAG queries.

        Methods:
            auto: Detect query type and route (validation, implementation, etc.)
            validation: "What validates X?" queries
            implementation: "What code implements X?" queries
            research: "Papers about X?" queries
            general: Keyword-based fallback

        Returns:
            {
                "answer": str,
                "context": Dict,
                "query_type": str,
                "nodes_retrieved": int
            }
        """
        if not self.driver:
            return {
                "answer": "GraphRAG unavailable: Neo4j not connected",
                "context": {},
                "query_type": "error",
                "nodes_retrieved": 0
            }

        # Auto-detect query type
        if method == "auto":
            method = self._classify_query(question)

        # Route to appropriate query method
        if method == "validation":
            return self._query_validation(question)
        elif method == "implementation":
            return self._query_implementation(question)
        elif method == "research":
            return self._query_research(question)
        else:
            context = self._retrieve_context(question)
            return {
                "answer": f"GRAPH CONTEXT:\n{context}" if context else "No results",
                "context": {},
                "query_type": "general",
                "nodes_retrieved": len(context.split('\n')) if context else 0
            }

    def _classify_query(self, question: str) -> str:
        """Classify query type from keywords."""
        q_lower = question.lower()

        if any(kw in q_lower for kw in ['validate', 'ground', 'theory', 'paper']):
            return "validation"
        elif any(kw in q_lower for kw in ['implement', 'code', 'function', 'class', 'module']):
            return "implementation"
        elif any(kw in q_lower for kw in ['research', 'study', 'paper', 'architecture', 'repository']):
            return "research"
        else:
            return "general"

    def _query_validation(self, question: str) -> Dict[str, Any]:
        """Find theoretical validation for concepts."""
        terms = [w for w in question.split() if len(w) > 4]

        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:SmocConcept)
                WHERE any(term in $terms WHERE toLower(c.name) CONTAINS term)
                MATCH (pc)-[:VALIDATES]->(c)
                MATCH (p:AcademicPaper)-[:DEFINES]->(pc)
                RETURN p.id, p.title, p.author, pc.name, c.name
                LIMIT 10
            """, terms=[t.lower() for t in terms])

            records = list(result)

            if not records:
                return {
                    "answer": f"No validation found for: {' '.join(terms)}",
                    "context": {},
                    "query_type": "validation",
                    "nodes_retrieved": 0
                }

            # Format answer
            lines = []
            for r in records:
                lines.append(f"{r['p.id']}: {r['p.title']} ({r['p.author']})")
                lines.append(f"  → Validates '{r['c.name']}' via {r['pc.name']}")

            return {
                "answer": "\n".join(lines),
                "context": {"papers": records},
                "query_type": "validation",
                "nodes_retrieved": len(records)
            }

    def _query_implementation(self, question: str) -> Dict[str, Any]:
        """Find code implementing concepts."""
        terms = [w for w in question.split() if len(w) > 4]

        with self.driver.session() as session:
            result = session.run("""
                MATCH (code:CodeEntity)
                WHERE any(term in $terms WHERE
                    toLower(code.file_path) CONTAINS term OR
                    toLower(code.id) CONTAINS term)
                RETURN code.id, code.file_path, code.semantic_role
                LIMIT 20
            """, terms=[t.lower() for t in terms])

            records = list(result)

            lines = []
            for r in records:
                lines.append(f"{r['code.id']}")
                lines.append(f"  File: {r['code.file_path']}")
                lines.append(f"  Role: {r['code.semantic_role']}")

            return {
                "answer": "\n".join(lines) if lines else "No code found",
                "context": {"code": records},
                "query_type": "implementation",
                "nodes_retrieved": len(records)
            }

    def _query_research(self, question: str) -> Dict[str, Any]:
        """Find research papers about topics."""
        terms = [w for w in question.split() if len(w) > 4]

        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:AcademicPaper)
                WHERE any(term in $terms WHERE toLower(p.summary) CONTAINS term OR toLower(p.title) CONTAINS term)
                RETURN p.id, p.title, p.author, p.summary
                LIMIT 10
            """, terms=[t.lower() for t in terms])

            records = list(result)

            lines = []
            for r in records:
                summary_preview = r['p.summary'][:200] if r['p.summary'] else ""
                lines.append(f"{r['p.id']}: {r['p.title']} ({r['p.author']})")
                lines.append(f"  {summary_preview}...")
                lines.append("")

            return {
                "answer": "\n".join(lines) if lines else "No research found",
                "context": {"papers": records},
                "query_type": "research",
                "nodes_retrieved": len(records)
            }

    def _retrieve_context(self, question: str) -> str:
        """
        Retrieves a subgraph relevant to the question using Cypher.
        """
        # Simple extraction of potential keywords (naive)
        keywords = [w for w in question.split() if len(w) > 4]
        
        # Cypher: Find concepts or papers matching keywords, expand 2 hops
        cypher = """
        MATCH (start)
        WHERE (start:Concept OR start:Paper OR start:CodeEntity)
          AND (toLower(start.name) CONTAINS toLower($keyword) 
               OR toLower(start.title) CONTAINS toLower($keyword))
        
        CALL apoc.path.subgraphAll(start, {
            maxLevel: 2,
            limit: 100
        })
        YIELD nodes, relationships
        
        RETURN nodes, relationships
        LIMIT 10
        """
        
        # Cypher: Find concepts or papers matching keywords, expand 2 hops
        fallback_cypher = """
        MATCH (start)-[r]-(neighbor)
        WHERE (start:SmocConcept OR start:AcademicPaper OR start:CodeEntity OR start:Chunk OR start:Atom)
          AND (toLower(start.name) CONTAINS toLower($keyword) 
               OR toLower(start.title) CONTAINS toLower($keyword)
               OR toLower(start.file_path) CONTAINS toLower($keyword)
               OR toLower(start.id) CONTAINS toLower($keyword))
        RETURN start, r, neighbor
        LIMIT 100
        """
        
        results = []
        with self.driver.session() as session:
            for kw in keywords:
                try:
                    # Try executing query for each keyword
                    res = session.run(fallback_cypher, keyword=kw)
                    for record in res:
                        start = record["start"]
                        neighbor = record["neighbor"]
                        rel = record["r"]
                        
                        # Format: [Paper] 'Title' --VALIDATES--> [Concept] 'Name'
                        s_label = list(start.labels)[0]
                        n_label = list(neighbor.labels)[0]
                        s_name = start.get("name") or start.get("title") or start.get("id")
                        n_name = neighbor.get("name") or neighbor.get("title") or start.get("id")
                        r_type = rel.type
                        
                        line = f"[{s_label}] '{s_name}' --{r_type}--> [{n_label}] '{n_name}'"
                        results.append(line)
                except Exception as e:
                    logger.error(f"Graph query error: {e}")
                    return f"Error executing graph query: {e}"

        return "\n".join(set(results)) # Deduplicate
