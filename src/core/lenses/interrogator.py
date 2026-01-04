"""
Lens Interrogator
=================

Facade that orchestrates all 8 epistemic lenses through 3 lens groups.

This is the main entry point for lens interrogation.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

from .structural_lens import StructuralLens
from .behavioral_lens import BehavioralLens
from .semantic_lens import SemanticLens


@dataclass
class LensInquiry:
    """Result of interrogating an atom through all 8 lenses."""
    r1_identity: Dict[str, Any]       # Name, path, signature
    r2_ontology: Dict[str, Any]       # Entity type, properties
    r3_classification: Dict[str, Any] # Role, category, atom
    r4_composition: Dict[str, Any]    # Parts, container, nesting
    r5_relationships: Dict[str, Any]  # Connections
    r6_transformation: Dict[str, Any] # Input → Output
    r7_semantics: Dict[str, Any]      # Purpose, intent
    r8_epistemology: Dict[str, Any]   # Confidence, evidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "R1_IDENTITY": self.r1_identity,
            "R2_ONTOLOGY": self.r2_ontology,
            "R3_CLASSIFICATION": self.r3_classification,
            "R4_COMPOSITION": self.r4_composition,
            "R5_RELATIONSHIPS": self.r5_relationships,
            "R6_TRANSFORMATION": self.r6_transformation,
            "R7_SEMANTICS": self.r7_semantics,
            "R8_EPISTEMOLOGY": self.r8_epistemology,
        }


class LensInterrogator:
    """
    Interrogates code atoms through 8 epistemic lenses.

    Composes three specialized lens groups:
    - StructuralLens: R1 Identity, R2 Ontology, R4 Composition
    - BehavioralLens: R5 Relationships, R6 Transformation
    - SemanticLens: R3 Classification, R7 Semantics, R8 Epistemology

    Usage:
        interrogator = LensInterrogator()
        inquiry = interrogator.interrogate(node, edges)
        print(inquiry.r1_identity)  # What is it called?
    """

    def __init__(self):
        self.structural = StructuralLens()
        self.behavioral = BehavioralLens()
        self.semantic = SemanticLens()

    def interrogate(
        self,
        node: Dict[str, Any],
        edges: List[Dict[str, Any]] = None,
        context: Dict = None
    ) -> LensInquiry:
        """
        Interrogate a node through all 8 lenses.

        Args:
            node: Node dictionary to interrogate
            edges: Optional list of edges for relationship analysis
            context: Optional additional context

        Returns:
            LensInquiry with results from all 8 lenses
        """
        edges = edges or []

        # Structural lenses (R1, R2, R4)
        structural = self.structural.interrogate(node)

        # Behavioral lenses (R5, R6)
        behavioral = self.behavioral.interrogate(node, edges)

        # Semantic lenses (R3, R7, R8)
        semantic = self.semantic.interrogate(node)

        return LensInquiry(
            r1_identity=structural["R1_IDENTITY"],
            r2_ontology=structural["R2_ONTOLOGY"],
            r3_classification=semantic["R3_CLASSIFICATION"],
            r4_composition=structural["R4_COMPOSITION"],
            r5_relationships=behavioral["R5_RELATIONSHIPS"],
            r6_transformation=behavioral["R6_TRANSFORMATION"],
            r7_semantics=semantic["R7_SEMANTICS"],
            r8_epistemology=semantic["R8_EPISTEMOLOGY"],
        )

    # Expose individual lenses for direct access

    def lens_r1_identity(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R1: IDENTITY - What is it called?"""
        return self.structural.lens_r1_identity(node)

    def lens_r2_ontology(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R2: ONTOLOGY - What exists here?"""
        return self.structural.lens_r2_ontology(node)

    def lens_r3_classification(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R3: CLASSIFICATION - What kind is it?"""
        return self.semantic.lens_r3_classification(node)

    def lens_r4_composition(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R4: COMPOSITION - How is it structured?"""
        return self.structural.lens_r4_composition(node)

    def lens_r5_relationships(
        self,
        node: Dict[str, Any],
        edges: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """R5: RELATIONSHIPS - How is it connected?"""
        return self.behavioral.lens_r5_relationships(node, edges)

    def lens_r6_transformation(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R6: TRANSFORMATION - What does it do?"""
        return self.behavioral.lens_r6_transformation(node)

    def lens_r7_semantics(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R7: SEMANTICS - What does it mean?"""
        return self.semantic.lens_r7_semantics(node)

    def lens_r8_epistemology(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """R8: EPISTEMOLOGY - How certain are we?"""
        return self.semantic.lens_r8_epistemology(node)
