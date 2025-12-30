"""
Dimension Models
================

Data structures for 8-dimensional code classification.

The 8 Dimensions (Octahedral Atom Model):
  D1: WHAT      - Atom type (200+ atoms, open world)
  D2: LAYER     - Architectural layer (Interface/App/Core/Infra/Test)
  D3: ROLE      - Semantic purpose (33 roles)
  D4: BOUNDARY  - I/O crossing (Internal/Input/Output/I-O)
  D5: STATE     - Statefulness (Stateful/Stateless)
  D6: EFFECT    - Side effects (Pure/Read/Write/ReadModify)
  D7: LIFECYCLE - Phase (Create/Use/Destroy)
  D8: TRUST     - Confidence (0-100%)
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DimensionVector:
    """Complete 8-dimensional classification of a code atom."""
    d1_what: str        # Atom type (AST node kind)
    d2_layer: str       # Architectural layer
    d3_role: str        # Semantic purpose
    d4_boundary: str    # I/O crossing type
    d5_state: str       # Statefulness
    d6_effect: str      # Side effect type
    d7_lifecycle: str   # Lifecycle phase
    d8_trust: float     # Confidence %

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "D1_WHAT": self.d1_what,
            "D2_LAYER": self.d2_layer,
            "D3_ROLE": self.d3_role,
            "D4_BOUNDARY": self.d4_boundary,
            "D5_STATE": self.d5_state,
            "D6_EFFECT": self.d6_effect,
            "D7_LIFECYCLE": self.d7_lifecycle,
            "D8_TRUST": self.d8_trust,
        }


# Standard dimension values

LAYERS = ["Interface", "Application", "Core", "Infrastructure", "Test", "Unknown"]
BOUNDARIES = ["Internal", "Input", "Output", "I-O"]
STATES = ["Stateful", "Stateless", "Unknown"]
EFFECTS = ["Pure", "Read", "Write", "ReadModify", "Unknown"]
LIFECYCLES = ["Create", "Use", "Destroy"]
