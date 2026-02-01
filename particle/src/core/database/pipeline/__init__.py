"""
Pipeline Integration for Collider Database.

Provides pipeline stages for incremental analysis and persistence.
"""

from .stages import IncrementalStage, PersistenceStage

__all__ = ["IncrementalStage", "PersistenceStage"]
