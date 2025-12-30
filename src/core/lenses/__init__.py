"""
Lenses Package
==============

The 8 Epistemic Lenses - How we ASK about code atoms.

The 8 Lenses interrogate atoms from different perspectives:
  R1: IDENTITY      - What is it called? (name, path, signature)
  R2: ONTOLOGY      - What exists here? (entity type, properties)
  R3: CLASSIFICATION - What kind is it? (role, category, atom)
  R4: COMPOSITION   - How is it structured? (parts, container, nesting)
  R5: RELATIONSHIPS - How is it connected? (calls, imports, inherits)
  R6: TRANSFORMATION - What does it do? (input → output)
  R7: SEMANTICS     - What does it mean? (purpose, intent)
  R8: EPISTEMOLOGY  - How certain are we? (confidence, evidence)

Organized into 3 lens groups:
  - StructuralLens (R1, R2, R4): Identity, ontology, composition
  - BehavioralLens (R5, R6): Relationships, transformation
  - SemanticLens (R3, R7, R8): Classification, semantics, epistemology

Usage:
    from src.core.lenses import LensInterrogator

    interrogator = LensInterrogator()
    inquiry = interrogator.interrogate(node, edges)
    print(inquiry.r1_identity)
"""

from .structural_lens import StructuralLens
from .behavioral_lens import BehavioralLens
from .semantic_lens import SemanticLens
from .interrogator import LensInterrogator, LensInquiry

__all__ = [
    'StructuralLens',
    'BehavioralLens',
    'SemanticLens',
    'LensInterrogator',
    'LensInquiry',
]
