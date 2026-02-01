"""
Context Management Services
============================

Shared infrastructure services that can be consumed by multiple tools.

Architecture:
- tools/     = Executables (you invoke them directly)
- services/  = Infrastructure (you query/import them)

Available Services:
- graph_rag: S14 GraphRAG semantic query service (Neo4j backend)

Future Services:
- vector_search: FAISS/Chroma vector similarity search
- embedding: Shared embedding generation (Gemini, OpenAI, etc.)
- cache: Redis/memory cache layer
"""

__all__ = ["graph_rag"]
