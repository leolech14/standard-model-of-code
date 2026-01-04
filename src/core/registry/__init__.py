"""
Registry Package
================

Centralized repositories for code analysis data:

- models.py: AtomDefinition dataclass
- definitions.py: Canonical atom definitions (96 atoms)
- registry.py: AtomRegistry class
- exporter.py: RegistryExporter for stats/export
- pattern_repository.py: Role detection patterns (prefix, suffix, dunder, etc.)
- schema_repository.py: Optimization schemas (13 patterns with instructions)
"""

from .models import AtomDefinition
from .definitions import ALL_DEFINITIONS
from .registry import AtomRegistry
from .exporter import RegistryExporter

from .pattern_repository import (
    PatternRepository,
    RolePattern,
    get_pattern_repository,
)

from .schema_repository import (
    SchemaRepository,
    OptimizationSchema,
    SchemaCategory,
    Effort,
    get_schema_repository,
)

__all__ = [
    # Atom registry
    'AtomDefinition',
    'ALL_DEFINITIONS',
    'AtomRegistry',
    'RegistryExporter',

    # Pattern repository
    'PatternRepository',
    'RolePattern',
    'get_pattern_repository',

    # Schema repository
    'SchemaRepository',
    'OptimizationSchema',
    'SchemaCategory',
    'Effort',
    'get_schema_repository',
]
