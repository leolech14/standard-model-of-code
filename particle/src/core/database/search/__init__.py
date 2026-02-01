"""
Search Module for Collider Database.

Provides full-text search using Tantivy (Rust-based).
"""

# Lazy import to avoid error when tantivy not installed
def get_tantivy_index():
    """Get TantivyIndex class (lazy import)."""
    from .tantivy_index import TantivyIndex
    return TantivyIndex


__all__ = ["get_tantivy_index"]
