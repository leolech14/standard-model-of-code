"""
Registry Models
===============

Data classes for the atom registry.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AtomDefinition:
    """A canonical atom in the taxonomy."""
    id: int                          # Unique ID (1-96 original, 97+ discoveries)
    name: str                        # PascalCase name (e.g., "PureFunction")
    ast_types: List[str]             # Tree-sitter node types that map to this
    continent: str                   # Data Foundations, Logic & Flow, Organization, Execution
    fundamental: str                 # Bits, Variables, Functions, etc.
    level: str                       # atom, molecule, organelle
    description: str                 # What this atom represents
    detection_rule: str              # How to detect it

    # Discovery metadata
    source: str = "original"         # "original" or repo name where discovered
    discovered_at: str = ""          # ISO timestamp
    occurrence_count: int = 0        # Total times seen across all repos
