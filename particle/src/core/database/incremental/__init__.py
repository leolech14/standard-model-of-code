"""
Incremental Analysis Module for Collider.

Provides fast change detection using BLAKE3 hashing to skip
unchanged files on re-analysis.
"""

from .hasher import FileHasher, hash_file, hash_files_parallel
from .delta_tracker import DeltaTracker

__all__ = ["FileHasher", "hash_file", "hash_files_parallel", "DeltaTracker"]
