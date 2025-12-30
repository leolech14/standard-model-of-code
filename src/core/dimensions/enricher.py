"""
Dimension Enricher
==================

Orchestrates all dimension detectors to enrich code nodes.
"""

from typing import Dict, List, Any

from .models import DimensionVector
from .structural import StructuralDimensionDetector
from .behavioral import BehavioralDimensionDetector
from .semantic import SemanticDimensionDetector


class DimensionEnricher:
    """
    Enriches nodes with all 8 dimensions.

    Composes three specialized detector groups:
    - StructuralDimensionDetector: D1, D2, D3
    - BehavioralDimensionDetector: D4, D5, D6
    - SemanticDimensionDetector: D7, D8

    Usage:
        enricher = DimensionEnricher()
        dimensions = enricher.enrich(node)
        print(dimensions.to_dict())
    """

    def __init__(self):
        self.structural = StructuralDimensionDetector()
        self.behavioral = BehavioralDimensionDetector()
        self.semantic = SemanticDimensionDetector()

    def enrich(self, node: Dict[str, Any]) -> DimensionVector:
        """
        Enrich a node with all 8 dimensions.

        Args:
            node: UnifiedNode dictionary

        Returns:
            DimensionVector with all 8 dimensions populated
        """
        return DimensionVector(
            d1_what=self.structural.detect_d1_what(node),
            d2_layer=self.structural.detect_d2_layer(node),
            d3_role=self.structural.detect_d3_role(node),
            d4_boundary=self.behavioral.detect_d4_boundary(node),
            d5_state=self.behavioral.detect_d5_state(node),
            d6_effect=self.behavioral.detect_d6_effect(node),
            d7_lifecycle=self.semantic.detect_d7_lifecycle(node),
            d8_trust=self.semantic.detect_d8_trust(node),
        )

    def enrich_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich a list of nodes with dimensions.

        Modifies nodes in-place, adding 'dimensions' field.
        """
        enriched = []

        for node in nodes:
            dimensions = self.enrich(node)
            node["dimensions"] = dimensions.to_dict()
            enriched.append(node)

        return enriched

    def load_boundary_results(self, boundary_map: Dict[str, str]):
        """Load results from boundary_detector.py"""
        self.behavioral.load_boundary_results(boundary_map)

    def load_purity_results(self, purity_map: Dict[str, str]):
        """Load results from purity_detector.py"""
        self.behavioral.load_purity_results(purity_map)
