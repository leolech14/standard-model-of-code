"""
ANALYTICS PACKAGE - Progressive Layer Revelation System
========================================================

This package provides tools for analyzing code through the
8-layer progressive revelation system.

LAYERS:
    L0: Raw AST          - Pure syntax parse
    L1: Structural       - Identity, location, body
    L2: Classification   - Role, atom type, arch layer
    L3: Dimension        - 8D coordinates (D1-D8)
    L4: Lens             - 8L perspectives (R1-R8)
    L5: Graph            - Relationships, edges
    L6: Math             - 4 Pillars (Ω, π, S, Nash)
    L7: Semantic         - Meaning, intent, purpose

USAGE:
    # Layer Revealer - CLI/programmatic layer exploration
    from analytics import LayerRevealer

    revealer = LayerRevealer("unified_analysis.json")
    revealer.show_layer_summary()
    revealer.reveal_layer("L2_CLASSIFICATION")
    revealer.reveal_progressive("UserRepository")

    # Canonical Visualizer - Interactive HTML visualization
    from analytics import CanonicalVisualizer

    viz = CanonicalVisualizer()
    viz.generate("unified_analysis.json", "output.html")
    viz.print_report()
"""

from .layer_revealer import LayerRevealer, LAYERS, LayerInfo
from .canonical_visualizer import CanonicalVisualizer, DetectionResults, ArchitectureInsights

__all__ = [
    # Layer Revealer
    "LayerRevealer",
    "LAYERS",
    "LayerInfo",
    # Canonical Visualizer
    "CanonicalVisualizer",
    "DetectionResults",
    "ArchitectureInsights",
]

__version__ = "4.0.0"
