"""
Database Models for Collider.

Provides schema definitions and mappers between Python objects and DB rows.
"""
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_schema_sql() -> str:
    """Load the SQL schema file."""
    return SCHEMA_PATH.read_text()


__all__ = ["get_schema_sql", "SCHEMA_PATH"]
