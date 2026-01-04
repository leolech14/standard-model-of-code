"""
Layer Revealer Package
======================

Progressive analytics tool for revealing layers of code analysis.

The tool is organized into:
- LayerRegistry: Static layer definitions and metadata
- LayerStatistics: Statistical computation engine
- LayerRevealer: Main orchestrator/facade

Usage:
    from src.analytics.layer_revealer import LayerRevealer, LAYERS, LayerInfo

    revealer = LayerRevealer("path/to/unified_analysis.json")
    revealer.show_layer_summary()
    revealer.reveal_layer("L3_DIMENSION")
"""

from .layer_registry import LayerInfo, LAYERS, get_layer, get_all_layer_ids, get_layer_by_level
from .layer_statistics import LayerStatistics
from .revealer import LayerRevealer

__all__ = [
    'LayerInfo',
    'LAYERS',
    'get_layer',
    'get_all_layer_ids',
    'get_layer_by_level',
    'LayerStatistics',
    'LayerRevealer',
]
