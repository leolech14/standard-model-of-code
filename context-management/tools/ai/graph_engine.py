import os
from neo4j import GraphDatabase
from google import genai
from google.genai.types import Part

class GraphEngine:
    def __init__(self, uri=None, auth=None, client=None, model="gemini-2.0-flash-001"):
        uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        if not auth:
            user = os.environ.get("NEO4J_USER", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "password")
            auth = (user, password)
            
        self.driver = GraphDatabase.driver(uri, auth=auth)
        self.model = model
        # Use provided client or create one
        self.client = client or genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def close(self):
        self.driver.close()

    def _get_schema_summary(self):
        return """
        Nodes: (:CodeNode {id: string, type: string, ...})
        Edges: (:CodeNode)-[:DEPENDS_ON {type: string}]->(:CodeNode)
        Properties on CodeNode: id (filepath or signature), file_path, start_line, end_line.
        """

    def nl_to_cypher(self, user_query):
        schema = self._get_schema_summary()
        prompt = f"""
        You are a Cypher expert. Convert the following natural language query into a READ-ONLY Cypher query for Neo4j.
        
        Schema:
        {schema}
        
        User Query: "{user_query}"
        
        Rules:
        1. Return ONLY the Cypher query. No markdown, no explanations.
        2. Use MATCH, RETURN, ORDER BY, LIMIT.
        3. Do NOT use CREATE, MERGE, DELETE, SET.
        4. If asking for specific files/functions, use CONTAINS or exact match on 'id' property.
        
        Cypher:
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=[Part.from_text(text=prompt)]
        )
        return response.text.strip().replace("```cypher", "").replace("```", "").strip()

    def query(self, user_query):
        cypher = self.nl_to_cypher(user_query)
        print(f"\n[Generated Cypher]: {cypher}\n")
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher)
                records = [r.data() for r in result]
                return records, cypher
        except Exception as e:
            return f"Error executing Cypher: {e}", cypher
