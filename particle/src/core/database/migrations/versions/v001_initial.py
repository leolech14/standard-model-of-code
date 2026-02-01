"""
Migration v001: Initial Schema

This is a placeholder - the initial schema is applied via schema.sql.
"""

VERSION = 1
DESCRIPTION = "Initial schema with runs, nodes, edges, and file tracking"


def up(backend) -> bool:
    """Apply migration."""
    # Initial schema is created by initialize_schema()
    return True


def down(backend) -> bool:
    """Roll back migration (drops all tables)."""
    # This would drop all tables - use with caution!
    return False  # Not implemented for safety
