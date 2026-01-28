#!/usr/bin/env python3
"""
GraphRAG Query Interface - Semantic Reasoning Over Knowledge Graph
===================================================================

Query types:
- Theory validation: "What validates X?"
- Code traceability: "What code implements X?"
- Research lineage: "Papers about X?"
- Concept discovery: "How are X and Y related?"

Usage:
    python graphrag_query.py "What validates Purpose Field?"
    python graphrag_query.py "What code implements Constructal Law?"
"""

import sys
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "elements2026"


class GraphRAGQuery:
    """GraphRAG query interface."""

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def query(self, question: str):
        """Execute GraphRAG query based on question pattern."""

        question_lower = question.lower()

        # Pattern 1: Validation queries
        if "validate" in question_lower or "ground" in question_lower:
            return self._query_validation(question)

        # Pattern 2: Implementation queries
        elif "implement" in question_lower or "code" in question_lower:
            return self._query_implementation(question)

        # Pattern 3: Research queries
        elif "research" in question_lower or "paper" in question_lower:
            return self._query_research(question)

        # Pattern 4: Relationship queries
        elif "relate" in question_lower or "connect" in question_lower:
            return self._query_relationships(question)

        # Default: General search
        else:
            return self._query_general(question)

    def _query_validation(self, question):
        """Find theoretical validation for concepts."""

        # Extract key terms
        terms = [w for w in question.split() if len(w) > 4]
        search_term = " ".join(terms[:3])  # First few meaningful words

        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:SmocConcept)
                WHERE any(term in $terms WHERE c.name CONTAINS term)
                MATCH (pc)-[:VALIDATES]->(c)
                MATCH (p:AcademicPaper)-[:DEFINES]->(pc)
                RETURN DISTINCT
                    p.id as ref,
                    p.title as paper,
                    p.author as author,
                    pc.name as validates_via,
                    c.name as concept
                LIMIT 5
            """, terms=[t.lower() for t in terms])

            results = list(result)

            if not results:
                return f"No validation found for: {search_term}"

            output = []
            for record in results:
                output.append(f"  {record['ref']}: {record['paper']} ({record['author']})")
                output.append(f"    → Validates '{record['concept']}' via {record['validates_via']}")

            return "\n".join(output)

    def _query_implementation(self, question):
        """Find code implementing concepts."""

        terms = [w for w in question.split() if len(w) > 4]

        with self.driver.session() as session:
            result = session.run("""
                MATCH (code:CodeEntity)
                WHERE any(term in $terms WHERE
                    code.file_path CONTAINS term OR
                    code.id CONTAINS term OR
                    toString(code.purpose) CONTAINS term)
                RETURN code.id, code.file_path, code.semantic_role, code.purpose
                LIMIT 10
            """, terms=terms)

            results = list(result)

            if not results:
                return f"No code found implementing: {' '.join(terms)}"

            output = []
            for record in results:
                output.append(f"  {record['code.id']}")
                output.append(f"    File: {record['code.file_path']}")
                output.append(f"    Role: {record['code.semantic_role']}, Purpose: {record['code.purpose']}")

            return "\n".join(output)

    def _query_research(self, question):
        """Find research papers about topics."""

        terms = [w for w in question.split() if len(w) > 4]

        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:AcademicPaper)
                WHERE any(term in $terms WHERE p.summary CONTAINS term)
                RETURN p.id, p.title, p.author,
                       substring(p.summary, 0, 200) as summary_preview
                LIMIT 5
            """, terms=terms)

            results = list(result)

            if not results:
                return f"No research found about: {' '.join(terms)}"

            output = []
            for record in results:
                output.append(f"  {record['p.id']}: {record['p.title']} ({record['p.author']})")
                output.append(f"    {record['summary_preview']}...")
                output.append("")

            return "\n".join(output)

    def _query_relationships(self, question):
        """Find how concepts relate via shortest path."""

        terms = [w for w in question.split() if len(w) > 4]

        if len(terms) < 2:
            return "Need at least 2 concepts to find relationship"

        with self.driver.session() as session:
            result = session.run("""
                MATCH (c1:SmocConcept), (c2:SmocConcept)
                WHERE c1.name CONTAINS $term1 AND c2.name CONTAINS $term2
                MATCH path = shortestPath((c1)-[*..5]-(c2))
                RETURN [n in nodes(path) | coalesce(n.name, n.id)] as path_nodes,
                       [r in relationships(path) | type(r)] as path_rels
                LIMIT 3
            """, term1=terms[0].lower(), term2=terms[1].lower() if len(terms) > 1 else "")

            results = list(result)

            if not results:
                return f"No path found between concepts"

            output = []
            for record in results:
                nodes = record['path_nodes']
                rels = record['path_rels']

                path_str = nodes[0]
                for i, rel in enumerate(rels):
                    path_str += f" -[{rel}]-> {nodes[i+1]}"

                output.append(f"  Path: {path_str}")

            return "\n".join(output)

    def _query_general(self, question):
        """General semantic search."""

        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $query)
                RETURN labels(n)[0] as type,
                       coalesce(n.name, n.id, n.title) as name,
                       coalesce(n.summary, n.content, '') as preview
                LIMIT 10
            """, query=question.lower())

            results = list(result)

            if not results:
                return "No results found"

            output = []
            for record in results:
                preview = record['preview'][:100] if record['preview'] else ""
                output.append(f"  [{record['type']}] {record['name']}")
                if preview:
                    output.append(f"    {preview}...")

            return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python graphrag_query.py 'your question'")
        print("\nExamples:")
        print("  python graphrag_query.py 'What validates Purpose Field?'")
        print("  python graphrag_query.py 'What code implements fabric?'")
        print("  python graphrag_query.py 'Research about Constructal Law?'")
        return 1

    question = " ".join(sys.argv[1:])

    print(f"\nQuery: {question}\n")
    print("=" * 60)

    graphrag = GraphRAGQuery()
    try:
        answer = graphrag.query(question)
        print(answer)
    finally:
        graphrag.close()

    print("=" * 60)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
