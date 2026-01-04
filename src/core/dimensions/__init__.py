"""
Dimensions Package
==================

The 8-Dimensional Code Classification System.

The 8 Dimensions (Octahedral Atom Model):
  D1: WHAT      - Atom type (200+ atoms, open world)
  D2: LAYER     - Architectural layer (Interface/App/Core/Infra/Test)
  D3: ROLE      - Semantic purpose (33 roles)
  D4: BOUNDARY  - I/O crossing (Internal/Input/Output/I-O)
  D5: STATE     - Statefulness (Stateful/Stateless)
  D6: EFFECT    - Side effects (Pure/Read/Write/ReadModify)
  D7: LIFECYCLE - Phase (Create/Use/Destroy)
  D8: TRUST     - Confidence (0-100%)

Organized into 3 detector groups:
  - StructuralDimensionDetector (D1, D2, D3): Type, layer, role
  - BehavioralDimensionDetector (D4, D5, D6): Boundary, state, effect
  - SemanticDimensionDetector (D7, D8): Lifecycle, trust

Usage:
    from dimensions import DimensionEnricher

    enricher = DimensionEnricher()
    dimensions = enricher.enrich(node)
    print(dimensions.to_dict())
"""

from .models import DimensionVector, LAYERS, BOUNDARIES, STATES, EFFECTS, LIFECYCLES
from .structural import StructuralDimensionDetector
from .behavioral import BehavioralDimensionDetector
from .semantic import SemanticDimensionDetector
from .enricher import DimensionEnricher


__all__ = [
    # Main entry point
    'DimensionEnricher',

    # Data model
    'DimensionVector',

    # Detector components
    'StructuralDimensionDetector',
    'BehavioralDimensionDetector',
    'SemanticDimensionDetector',

    # Constants
    'LAYERS',
    'BOUNDARIES',
    'STATES',
    'EFFECTS',
    'LIFECYCLES',
]
