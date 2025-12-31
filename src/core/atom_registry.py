#!/usr/bin/env python3
"""
Atom Registry - Canonical list of all known atoms in the taxonomy.

REFACTORED: This module now re-exports from the registry/ package.
The monolithic implementation has been split into:
- registry/models.py: AtomDefinition dataclass
- registry/definitions.py: All 96 canonical atom definitions
- registry/registry.py: AtomRegistry class
- registry/exporter.py: RegistryExporter for stats/export

All original imports continue to work for backward compatibility.
"""

from pathlib import Path

# Re-export everything from the registry package
try:
    from .registry import (
        AtomDefinition,
        ALL_DEFINITIONS,
        AtomRegistry,
        RegistryExporter,
    )
except ImportError:
    from registry import (
        AtomDefinition,
        ALL_DEFINITIONS,
        AtomRegistry,
        RegistryExporter,
    )

__all__ = [
    'AtomDefinition',
    'ALL_DEFINITIONS',
    'AtomRegistry',
    'RegistryExporter',
]


# =============================================================================
# CLI (backward compatibility)
# =============================================================================

if __name__ == "__main__":
    registry = AtomRegistry()
    exporter = RegistryExporter(registry)
    exporter.print_summary()

    # Export canonical registry
    output_path = Path(__file__).parent.parent / "output" / "atom_registry_canon.json"
    output_path.parent.mkdir(exist_ok=True)
    exporter.export_json(str(output_path))
    print()
    print(f"Exported to: {output_path}")
