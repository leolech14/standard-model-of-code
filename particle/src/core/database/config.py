"""
Database Configuration for Collider.

Provides DatabaseConfig dataclass with environment variable overrides.
Default: SQLite backend with incremental analysis enabled.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List


@dataclass
class DatabaseConfig:
    """Configuration for Collider database layer."""

    # Core settings
    enabled: bool = True
    backend: str = "sqlite"

    # Paths (env var overrides)
    sqlite_path: str = ".collider/collider.db"  # COLLIDER_SQLITE_PATH
    tantivy_path: str = ".collider/search"       # COLLIDER_TANTIVY_PATH

    # Feature toggles
    incremental_enabled: bool = True   # --incremental/--no-incremental
    search_enabled: bool = False       # --search
    history_enabled: bool = True       # --keep-history

    # Performance tuning
    batch_size: int = 500
    hash_algorithm: str = "blake3"

    # Internal
    _project_root: Optional[Path] = field(default=None, repr=False)

    def __post_init__(self):
        """Apply environment variable overrides."""
        if os.environ.get("COLLIDER_SQLITE_PATH"):
            self.sqlite_path = os.environ["COLLIDER_SQLITE_PATH"]
        if os.environ.get("COLLIDER_TANTIVY_PATH"):
            self.tantivy_path = os.environ["COLLIDER_TANTIVY_PATH"]
        if os.environ.get("COLLIDER_DB_DISABLED", "").lower() in ("1", "true", "yes"):
            self.enabled = False

    @classmethod
    def from_options(cls, options: Dict[str, Any], project_root: Optional[Path] = None) -> "DatabaseConfig":
        """
        Create config from CLI options dict.

        Args:
            options: Dict with CLI flags like db, no_db, db_backend, incremental, etc.
            project_root: Project root path for resolving relative paths.

        Returns:
            Configured DatabaseConfig instance.
        """
        config = cls()

        # Handle explicit disable
        if options.get("no_db"):
            config.enabled = False
            return config

        # Backend selection
        if options.get("db_backend"):
            config.backend = options["db_backend"]

        # Path overrides
        if options.get("db"):
            config.sqlite_path = options["db"]

        # Feature toggles
        if "incremental" in options:
            config.incremental_enabled = options["incremental"]
        if options.get("no_incremental"):
            config.incremental_enabled = False
        if options.get("search"):
            config.search_enabled = True
        if options.get("no_history"):
            config.history_enabled = False

        # Performance
        if options.get("batch_size"):
            config.batch_size = options["batch_size"]

        config._project_root = project_root
        return config

    def resolve_path(self, path: str) -> Path:
        """Resolve a path relative to project root."""
        p = Path(path)
        if p.is_absolute():
            return p
        if self._project_root:
            return self._project_root / p
        return Path.cwd() / p

    def get_sqlite_path(self) -> Path:
        """Get resolved SQLite database path."""
        return self.resolve_path(self.sqlite_path)

    def get_tantivy_path(self) -> Path:
        """Get resolved Tantivy index path."""
        return self.resolve_path(self.tantivy_path)

    @staticmethod
    def list_features() -> List[Dict[str, Any]]:
        """
        List all database features for discoverability.

        Returns:
            List of feature dicts with id, default, cli, status.
        """
        from .registry import FeatureRegistry
        return FeatureRegistry.list_features()

    def to_dict(self) -> Dict[str, Any]:
        """Export config as dict (for serialization)."""
        return {
            "enabled": self.enabled,
            "backend": self.backend,
            "sqlite_path": self.sqlite_path,
            "tantivy_path": self.tantivy_path,
            "incremental_enabled": self.incremental_enabled,
            "search_enabled": self.search_enabled,
            "history_enabled": self.history_enabled,
            "batch_size": self.batch_size,
            "hash_algorithm": self.hash_algorithm,
        }
