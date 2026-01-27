"""
Search Package - File Search (RAG) Implementation
=================================================

Standard Model Classification:
-----------------------------
D1_KIND:     ORG.PKG.O (Organizational Package)
D2_LAYER:    Infrastructure (external API integration)
D3_ROLE:     Repository (stores/retrieves indexed files)
D4_BOUNDARY: I-O (API calls to Gemini File Search)
D5_STATE:    Stateful (stores persist across calls)
D6_EFFECT:   Impure (network I/O, store mutations)
D7_LIFECYCLE: Create/Use/Destroy (full store lifecycle)
D8_TRUST:    80 (depends on external service)

ACI Tier: 1 (RAG)
    This package implements Tier 1 - Retrieval Augmented Generation.
    Files are indexed into stores, then queried with semantic search.

Purpose Emergence: pi3 Organelle
    The search subsystem is a complete, self-contained RAG pipeline.
    It can function independently of other analysis modes.

Communication Theory:
    Source:   Project files
    Channel:  Gemini File Search API
    Message:  Indexed chunks with embeddings
    Receiver: Query engine with citation extraction
    Redundancy: Stores persist for reuse

Tool Theory:
    Universe: STONE_TOOLS (AI-native indexing)
    Role:     S-Graph (semantic index of codebase)
    Stone Tool Test: FAIL (requires API, not human-usable)
    Consumer: S-AIConsumer (RAG pipeline)

Usage:
    from analyze.search import create_store, index_files, search_store

    # Create or get existing store
    store_name = create_store(client, "my-store")

    # Index files
    stats = index_files(client, store_name, files, base_dir)

    # Search with citations
    results = search_store(client, store_name, "how does X work?")
"""

# Package exports will be added when store.py, indexer.py, query.py are created

__all__ = []
