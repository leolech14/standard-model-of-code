"""
Database Backends for Collider.

Available backends:
    - SQLiteBackend: Default, file-based, no setup required
    - PostgresBackend: For team/production use (requires psycopg2)
    - DuckDBBackend: For analytics queries (requires duckdb)
"""

from .base import DatabaseBackend

__all__ = ["DatabaseBackend"]
