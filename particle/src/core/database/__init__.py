"""
Collider Database Layer.

Provides persistence, incremental analysis, and search capabilities.

Quick Start:
    from src.core.database import create_database_manager, DatabaseConfig

    config = DatabaseConfig.from_options(options)
    db = create_database_manager(config, target_path)

    # Detect changes
    delta = db.detect_changes(target_path)

    # Persist results
    run_id = db.persist(nodes, edges, metadata)

Features (see --list-features):
    - database: Core persistence (default ON)
    - incremental: Skip unchanged files (default ON)
    - sqlite: SQLite backend (default ON)
    - search: Tantivy full-text search (default OFF)
"""

from .config import DatabaseConfig
from .registry import FeatureRegistry, Feature

# Lazy imports for backends to avoid import errors when deps not installed
_manager_instance = None


def create_database_manager(config: DatabaseConfig, project_path=None):
    """
    Factory function to create the appropriate database manager.

    Args:
        config: DatabaseConfig instance
        project_path: Path to the project being analyzed

    Returns:
        DatabaseManager instance (SQLite, PostgreSQL, or DuckDB based)
    """
    if not config.enabled:
        return None

    from pathlib import Path
    if project_path:
        config._project_root = Path(project_path).resolve()

    if config.backend == "sqlite":
        from .backends.sqlite import SQLiteBackend
        return SQLiteBackend(config)
    else:
        raise ValueError(f"Unknown database backend: {config.backend}. Only 'sqlite' is supported.")


def list_features():
    """Print all available database features."""
    FeatureRegistry.print_features()


__all__ = [
    "DatabaseConfig",
    "FeatureRegistry",
    "Feature",
    "create_database_manager",
    "list_features",
]
