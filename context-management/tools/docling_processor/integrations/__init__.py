"""
Docling Processor Integrations

Framework integrations for LangChain, LlamaIndex, vector databases, and enterprise patterns.
"""

# Core integrations (lazy imports - dependencies are optional)
def __getattr__(name):
    if name == "DoclingRAGLoader":
        from .langchain_loader import DoclingRAGLoader
        return DoclingRAGLoader
    elif name == "DoclingQAChain":
        from .langchain_loader import DoclingQAChain
        return DoclingQAChain
    elif name == "DoclingIndexReader":
        from .llamaindex_reader import DoclingIndexReader
        return DoclingIndexReader
    elif name == "DoclingQueryEngine":
        from .llamaindex_reader import DoclingQueryEngine
        return DoclingQueryEngine
    elif name == "VectorStoreFactory":
        from .vector_stores import VectorStoreFactory
        return VectorStoreFactory
    elif name in ("CircuitBreaker", "RetryHandler", "ProcessingMetrics",
                  "ProgressTracker", "BatchOrchestrator"):
        from . import enterprise
        return getattr(enterprise, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    # LangChain
    "DoclingRAGLoader",
    "DoclingQAChain",
    # LlamaIndex
    "DoclingIndexReader",
    "DoclingQueryEngine",
    # Vector Stores
    "VectorStoreFactory",
    # Enterprise Patterns
    "CircuitBreaker",
    "RetryHandler",
    "ProcessingMetrics",
    "ProgressTracker",
    "BatchOrchestrator",
]
