"""
Layer Revealer (Backward Compatibility Module)
==============================================

This module re-exports from the refactored layer_revealer package.
New code should import from src.analytics.layer_revealer directly.

Old:
    from layer_revealer import LayerRevealer, LAYERS

New:
    from src.analytics.layer_revealer import LayerRevealer, LAYERS
"""

import sys

# Re-export everything from the new package for backward compatibility
from src.analytics.layer_revealer import (
    LayerRevealer,
    LayerInfo,
    LAYERS,
    LayerStatistics,
    get_layer,
    get_all_layer_ids,
    get_layer_by_level,
)

__all__ = [
    'LayerRevealer',
    'LayerInfo',
    'LAYERS',
    'LayerStatistics',
    'get_layer',
    'get_all_layer_ids',
    'get_layer_by_level',
]


# CLI for backward compatibility
def main():
    """Command-line interface for LayerRevealer."""
    if len(sys.argv) < 2:
        print("Usage: python layer_revealer.py <analysis.json> [command]")
        print("\nCommands:")
        print("  summary           Show layer summary")
        print("  reveal <layer>    Reveal specific layer (L0-L7)")
        print("  atom <name>       Progressive revelation for atom")
        print("  roles             Show role distribution")
        print("  matrix <d1> <d2>  Cross-layer matrix")
        return

    revealer = LayerRevealer(sys.argv[1])

    if len(sys.argv) == 2:
        revealer.show_layer_summary()
        return

    command = sys.argv[2]

    if command == "summary":
        revealer.show_layer_summary()

    elif command == "reveal" and len(sys.argv) > 3:
        revealer.reveal_layer(sys.argv[3])

    elif command == "atom" and len(sys.argv) > 3:
        revealer.reveal_progressive(sys.argv[3])

    elif command == "roles":
        revealer.reveal_layer("L2_CLASSIFICATION")

    elif command == "matrix" and len(sys.argv) > 4:
        matrix = revealer.cross_layer_matrix(sys.argv[3], sys.argv[4])
        revealer.print_matrix(matrix, f"{sys.argv[3]} x {sys.argv[4]}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
