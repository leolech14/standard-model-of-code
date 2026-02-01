"""
Schema Migrator for Collider Database.

Handles database schema versioning and migrations.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from ..backends.base import DatabaseBackend


class Migration:
    """A single migration."""

    def __init__(self, version: int, description: str,
                 up: Callable[[DatabaseBackend], bool],
                 down: Optional[Callable[[DatabaseBackend], bool]] = None):
        """
        Initialize migration.

        Args:
            version: Migration version number
            description: Human-readable description
            up: Function to apply migration
            down: Optional function to roll back
        """
        self.version = version
        self.description = description
        self.up = up
        self.down = down


class Migrator:
    """
    Database schema migrator.

    Manages schema versions and applies migrations.
    """

    def __init__(self, backend: DatabaseBackend):
        """
        Initialize migrator.

        Args:
            backend: Database backend
        """
        self.backend = backend
        self._migrations: List[Migration] = []

        # Register built-in migrations
        self._register_migrations()

    def _register_migrations(self):
        """Register all migrations."""
        # v1: Initial schema (handled by schema.sql)
        self._migrations.append(Migration(
            version=1,
            description="Initial schema with runs, nodes, edges, and file tracking",
            up=lambda b: True,  # Already applied by initialize_schema
        ))

        # Future migrations would be added here
        # self._migrations.append(Migration(
        #     version=2,
        #     description="Add full-text search tables",
        #     up=self._migrate_v2_up,
        #     down=self._migrate_v2_down,
        # ))

    def get_current_version(self) -> int:
        """Get current schema version."""
        return self.backend.get_schema_version()

    def get_latest_version(self) -> int:
        """Get latest available migration version."""
        if not self._migrations:
            return 0
        return max(m.version for m in self._migrations)

    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied."""
        current = self.get_current_version()
        return [m for m in self._migrations if m.version > current]

    def migrate(self, target_version: Optional[int] = None) -> Dict[str, Any]:
        """
        Run migrations up to target version.

        Args:
            target_version: Target version (defaults to latest)

        Returns:
            Dict with migration results
        """
        if target_version is None:
            target_version = self.get_latest_version()

        current = self.get_current_version()
        applied = []
        errors = []

        if current >= target_version:
            return {
                "status": "up_to_date",
                "current_version": current,
                "target_version": target_version,
                "applied": [],
            }

        # Apply pending migrations in order
        pending = [m for m in self._migrations
                   if current < m.version <= target_version]
        pending.sort(key=lambda m: m.version)

        for migration in pending:
            try:
                success = migration.up(self.backend)
                if success:
                    self.backend.migrate_to(migration.version)
                    applied.append({
                        "version": migration.version,
                        "description": migration.description,
                        "applied_at": datetime.now().isoformat(),
                    })
                else:
                    errors.append({
                        "version": migration.version,
                        "error": "Migration returned False",
                    })
                    break
            except Exception as e:
                errors.append({
                    "version": migration.version,
                    "error": str(e),
                })
                break

        return {
            "status": "completed" if not errors else "error",
            "current_version": self.get_current_version(),
            "target_version": target_version,
            "applied": applied,
            "errors": errors,
        }

    def rollback(self, target_version: int) -> Dict[str, Any]:
        """
        Roll back to target version.

        Args:
            target_version: Version to roll back to

        Returns:
            Dict with rollback results
        """
        current = self.get_current_version()

        if current <= target_version:
            return {
                "status": "already_at_version",
                "current_version": current,
                "target_version": target_version,
            }

        # Get migrations to rollback (in reverse order)
        to_rollback = [m for m in self._migrations
                       if target_version < m.version <= current]
        to_rollback.sort(key=lambda m: m.version, reverse=True)

        rolled_back = []
        errors = []

        for migration in to_rollback:
            if migration.down is None:
                errors.append({
                    "version": migration.version,
                    "error": "Migration has no rollback",
                })
                break

            try:
                success = migration.down(self.backend)
                if success:
                    self.backend.migrate_to(migration.version - 1)
                    rolled_back.append({
                        "version": migration.version,
                        "description": migration.description,
                    })
                else:
                    errors.append({
                        "version": migration.version,
                        "error": "Rollback returned False",
                    })
                    break
            except Exception as e:
                errors.append({
                    "version": migration.version,
                    "error": str(e),
                })
                break

        return {
            "status": "completed" if not errors else "error",
            "current_version": self.get_current_version(),
            "target_version": target_version,
            "rolled_back": rolled_back,
            "errors": errors,
        }

    def status(self) -> Dict[str, Any]:
        """
        Get migration status.

        Returns:
            Dict with current version, pending migrations, etc.
        """
        current = self.get_current_version()
        pending = self.get_pending_migrations()

        return {
            "current_version": current,
            "latest_version": self.get_latest_version(),
            "pending_count": len(pending),
            "pending": [
                {"version": m.version, "description": m.description}
                for m in pending
            ],
        }
