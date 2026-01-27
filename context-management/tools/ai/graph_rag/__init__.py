"""
GraphRAG (S14) - Graph-Structured Reasoning Subsystem
======================================================

SMoC Role: Intelligence/Query/E | service | graph_reasoner

Enhanced knowledge retrieval via semantic proximity graphs.

Usage:
    from graph_rag import GraphRAGService
    
    service = GraphRAGService()
    answer = service.query("What validates Purpose Field?")

Integration:
    - analyze.py: GRAPH_RAG tier (ACI Tier 5)
    - wire.py: Incremental updates
    - Collider: Enriched purpose validation
"""

__version__ = "1.0.0"
__subsystem__ = "S14"

from .graph_rag_service import GraphRAGService

__all__ = ["GraphRAGService"]
