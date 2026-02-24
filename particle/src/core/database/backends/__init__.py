"""
Database Backends for Collider.

Available backends:
    - SQLiteBackend: Default, file-based, no setup required
"""

from .base import DatabaseBackend

__all__ = ["DatabaseBackend"]
