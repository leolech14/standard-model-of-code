"""
Registry Exporter
=================

Export and reporting functions for the atom registry.
"""

import json
from datetime import datetime
from typing import Dict

from .registry import AtomRegistry


class RegistryExporter:
    """Exports and reports on the atom registry."""

    def __init__(self, registry: AtomRegistry):
        self.registry = registry

    def get_stats(self) -> Dict:
        """Get registry statistics."""
        by_continent = {}
        by_fundamental = {}
        by_level = {}
        by_source = {"original": 0, "discovered": 0}

        for atom in self.registry.atoms.values():
            by_continent[atom.continent] = by_continent.get(atom.continent, 0) + 1
            by_fundamental[atom.fundamental] = by_fundamental.get(atom.fundamental, 0) + 1
            by_level[atom.level] = by_level.get(atom.level, 0) + 1
            if atom.source == "original":
                by_source["original"] += 1
            else:
                by_source["discovered"] += 1

        return {
            "total_atoms": len(self.registry.atoms),
            "ast_types_mapped": len(self.registry.ast_type_map),
            "by_continent": by_continent,
            "by_fundamental": by_fundamental,
            "by_level": by_level,
            "by_source": by_source,
            "next_id": self.registry.next_id,
        }

    def export_json(self, path: str):
        """Export the canonical registry to JSON."""
        data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "atoms": {
                str(id): {
                    "id": atom.id,
                    "name": atom.name,
                    "ast_types": atom.ast_types,
                    "continent": atom.continent,
                    "fundamental": atom.fundamental,
                    "level": atom.level,
                    "description": atom.description,
                    "detection_rule": atom.detection_rule,
                    "source": atom.source,
                    "discovered_at": atom.discovered_at,
                } for id, atom in self.registry.atoms.items()
            }
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def print_summary(self):
        """Print a summary of the registry."""
        stats = self.get_stats()

        print("=" * 70)
        print("ATOM REGISTRY - Canonical Taxonomy")
        print("=" * 70)
        print()
        print(f"Total Atoms: {stats['total_atoms']}")
        print(f"AST Types Mapped: {stats['ast_types_mapped']}")
        print(f"Original (96 base): {stats['by_source']['original']}")
        print(f"Discovered: {stats['by_source']['discovered']}")
        print()

        print("By Continent:")
        for continent, count in sorted(stats['by_continent'].items(), key=lambda x: -x[1]):
            bar = "#" * min(count // 2, 30)
            print(f"  {continent:20} {count:3} {bar}")
        print()

        print("By Fundamental:")
        for fund, count in sorted(stats['by_fundamental'].items(), key=lambda x: -x[1]):
            bar = "#" * min(count, 30)
            print(f"  {fund:20} {count:3} {bar}")
        print()

        print("By Level:")
        for level, count in sorted(stats['by_level'].items(), key=lambda x: -x[1]):
            bar = "#" * min(count, 30)
            print(f"  {level:12} {count:3} {bar}")
