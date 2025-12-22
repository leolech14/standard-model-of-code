"""Oracle extractors for architecture ground truth."""

from .base import OracleExtractor, OracleResult, ComponentMembership, DependencyConstraints
from .canonical_paths import CanonicalPathsOracle

__all__ = [
    "OracleExtractor",
    "OracleResult", 
    "ComponentMembership",
    "DependencyConstraints",
    "CanonicalPathsOracle",
]
