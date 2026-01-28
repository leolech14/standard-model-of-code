import os
from neo4j import GraphDatabase
import json

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class GraphAnalytics:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.driver.verify_connectivity()

    def close(self):
        self.driver.close()

    def run_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def get_sprawl_stats(self):
        """
        Analyze 'sprawl' by looking for:
        1. Orphans (nodes with 0 edges)
        2. Disconnected components (weakly connected components)
        3. High complexity nodes (high degree centrality)
        """
        print("\n--- GRAPH ANALYTICS: SPRAWL DETECTION ---")
        
        # 1. Total Counts
        counts = self.run_query("""
        MATCH (n:CodeNode)
        RETURN count(n) as node_count
        """)
        edge_counts = self.run_query("""
        MATCH ()-[r]->()
        RETURN count(r) as edge_count
        """)
        print(f"Total Nodes: {counts[0]['node_count']}")
        print(f"Total Connections: {edge_counts[0]['edge_count']}")

        # 2. Orphans
        orphans = self.run_query("""
        MATCH (n:CodeNode)
        WHERE NOT (n)--()
        RETURN count(n) as orphans, collect(n.id)[0..5] as examples
        """)
        print(f"Orphaned Nodes (Disconnected): {orphans[0]['orphans']}")
        if orphans[0]['orphans'] > 0:
            print(f"  Examples: {orphans[0]['examples']}")

        # 3. God Objects (High fan-out/fan-in)
        god_objects = self.run_query("""
        MATCH (n:CodeNode)
        WITH n, 
             size([(n)-->() | 1]) as out_degree,
             size([()-->(n) | 1]) as in_degree
        WHERE out_degree > 20 OR in_degree > 20
        RETURN n.id, out_degree, in_degree
        ORDER BY (out_degree + in_degree) DESC
        LIMIT 10
        """)
        print("\nTop 10 'God Objects' (High Coupling):")
        for obj in god_objects:
            print(f"  - {obj['n.id']}: In={obj['in_degree']}, Out={obj['out_degree']}")

        # 4. Community Detection (Label Propagation - Basic Simulation/Heuristic if GDS not installed)
        # Note: GDS (Graph Data Science) library might not be available. 
        # We can simulate basic clustering by looking for dense connections or just listing node types.
        
        # Let's check for 'islands' - small components
        # This is hard without GDS or complex traversal, but we can check nodes with low connectivity
        
        print("\nAnalysis Complete.")

def main():
    analytics = None
    try:
        analytics = GraphAnalytics(NEO4J_URI, (NEO4J_USER, NEO4J_PASSWORD))
        analytics.get_sprawl_stats()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if analytics:
            analytics.close()

if __name__ == "__main__":
    main()
