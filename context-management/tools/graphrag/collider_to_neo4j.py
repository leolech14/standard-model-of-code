import json
import os
import glob
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

def get_latest_collider_file():
    """Finds the latest Collider output JSON file."""
    files = glob.glob(".collider-full/output_llm-oriented_*.json")
    if not files:
        raise FileNotFoundError("No Collider output files found in .collider-full/")
    return max(files, key=os.path.getmtime)

def sanitize_properties(props):
    """Converts complex types (dict, list of dicts) to JSON strings for Neo4j."""
    sanitized = {}
    for k, v in props.items():
        if isinstance(v, dict) or (isinstance(v, list) and any(isinstance(i, dict) for i in v)):
            sanitized[k] = json.dumps(v)
        else:
            sanitized[k] = v
    return sanitized

def import_data(driver, file_path):
    print(f"Loading data from {file_path}...")
    with open(file_path, 'r') as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Sanitize data
    print("Sanitizing data for Neo4j compatibility...")
    nodes = [sanitize_properties(n) for n in nodes]
    edges = [sanitize_properties(e) for e in edges]

    print(f"Found {len(nodes)} nodes and {len(edges)} edges.")

    with driver.session() as session:
        # Create constraint for performance
        print("Creating constraints...")
        try:
            session.run("CREATE CONSTRAINT FOR (n:CodeNode) REQUIRE n.id IS UNIQUE")
        except Exception as e:
            # Check if constraint already exists
            if "Neo.ClientError.Schema.EquivalentSchemaRuleAlreadyExists" not in str(e):
                 print(f"Constraint creation note: {e}")

        # Import Nodes
        print("Importing nodes...")
        query_nodes = """
        UNWIND $batch AS node
        MERGE (n:CodeNode {id: node.id})
        SET n += node
        """
        batch_size = 1000
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            session.run(query_nodes, batch=batch)
            print(f"  Processed {min(i + batch_size, len(nodes))} / {len(nodes)} nodes")

        # Import Edges
        print("Importing edges...")
        query_edges = """
        UNWIND $batch AS edge
        MATCH (s:CodeNode {id: edge.source})
        MATCH (t:CodeNode {id: edge.target})
        MERGE (s)-[r:DEPENDS_ON {type: edge.edge_type}]->(t)
        SET r += edge
        """
        for i in range(0, len(edges), batch_size):
            batch = edges[i:i + batch_size]
            session.run(query_edges, batch=batch)
            print(f"  Processed {min(i + batch_size, len(edges))} / {len(edges)} edges")

    print("Import complete!")

def main():
    file_path = get_latest_collider_file()
    print(f"Connecting to Neo4j at {NEO4J_URI} as {NEO4J_USER}...")

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Connected successfully.")
        import_data(driver, file_path)
        driver.close()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Neo4j is running and credentials are correct.")

if __name__ == "__main__":
    main()
