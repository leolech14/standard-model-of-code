"""
Semantic Dimensions
===================

Detectors for D7 (LIFECYCLE), D8 (TRUST).
These dimensions define the semantic meaning and confidence of classification.
"""

from typing import Dict, Any


class SemanticDimensionDetector:
    """Detects semantic dimensions D7, D8."""

    # Lifecycle phase patterns
    CREATE_PATTERNS = ["create", "new", "make", "build", "initialize", "init", "setup", "construct", "factory"]
    DESTROY_PATTERNS = ["delete", "remove", "destroy", "cleanup", "teardown", "close", "dispose", "finalize"]

    # Special Python lifecycle methods
    CREATE_METHODS = ["__init__", "__new__", "__enter__"]
    DESTROY_METHODS = ["__del__", "__exit__", "__close__"]

    def detect_d7_lifecycle(self, node: Dict[str, Any]) -> str:
        """
        D7: LIFECYCLE - What lifecycle phase is this node in?

        Values:
        - Create: Creates new entities/resources
        - Use: Uses/operates on existing entities
        - Destroy: Destroys/releases entities/resources
        """
        name = node.get("name", "").lower()
        role = node.get("role", "")

        # Create phase
        if any(p in name for p in self.CREATE_PATTERNS):
            return "Create"

        if role in ["Factory", "Builder", "Creator"]:
            return "Create"

        # Special Python methods
        if name in self.CREATE_METHODS:
            return "Create"

        # Destroy phase
        if any(p in name for p in self.DESTROY_PATTERNS):
            return "Destroy"

        if role in ["Destroyer"]:
            return "Destroy"

        # Special Python methods
        if name in self.DESTROY_METHODS:
            return "Destroy"

        # Default: Use phase
        return "Use"

    def detect_d8_trust(self, node: Dict[str, Any]) -> float:
        """
        D8: TRUST - How confident are we in this classification?

        Values: 0-100%

        This is already computed by particle_classifier.py.
        Extract role_confidence from node.
        """
        return node.get("role_confidence", 0.0)

    def calculate_overall_trust(self, node: Dict[str, Any]) -> float:
        """
        Calculate overall trust score considering multiple factors.

        Factors:
        - Role confidence (primary)
        - Classification method (pattern vs inference)
        - Context availability
        """
        base_confidence = node.get("role_confidence", 0.0)

        # Boost if pattern-matched
        if node.get("discovery_method") == "pattern":
            base_confidence = min(100.0, base_confidence * 1.1)

        # Reduce if fallback inference was used
        if node.get("role") == "Unknown":
            base_confidence = min(50.0, base_confidence)

        return round(base_confidence, 2)
