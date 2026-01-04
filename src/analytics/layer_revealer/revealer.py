"""
Layer Revealer
==============

Progressive analytics tool for revealing layers of code analysis.

This is the main orchestrator that composes LayerRegistry and LayerStatistics.
"""

import json
from typing import Dict, List, Any, Optional

from .layer_registry import LAYERS, LayerInfo, get_layer
from .layer_statistics import LayerStatistics


class LayerRevealer:
    """
    Progressive layer revelation analytics tool.

    Loads unified analysis output and allows drilling down
    through layers of increasing detail.

    Usage:
        revealer = LayerRevealer("path/to/unified_analysis.json")
        revealer.show_layer_summary()
        revealer.reveal_layer("L3_DIMENSION")
        revealer.filter_by("role", "Repository").reveal_layer("L6_MATH")
    """

    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the revealer.

        Args:
            data_path: Path to unified_analysis.json or proof_output.json
        """
        self.data: Dict[str, Any] = {}
        self.atoms: List[Dict] = []
        self.edges: List[Dict] = []
        self._filters: List[tuple] = []
        self._statistics = LayerStatistics()

        if data_path:
            self.load(data_path)

    def load(self, path: str) -> "LayerRevealer":
        """Load analysis data from JSON file."""
        with open(path) as f:
            self.data = json.load(f)

        # Extract atoms (particles/nodes)
        self.atoms = (
            self.data.get("nodes", []) or
            self.data.get("particles", []) or
            self.data.get("atoms", []) or
            []
        )

        # Extract edges
        self.edges = self.data.get("edges", [])

        print(f"Loaded {len(self.atoms)} atoms, {len(self.edges)} edges")
        return self

    # =========================================================================
    # FILTERING
    # =========================================================================

    def filter_by(self, field: str, value: Any) -> "LayerRevealer":
        """Add a filter. Chainable."""
        self._filters.append((field, value))
        return self

    def clear_filters(self) -> "LayerRevealer":
        """Clear all filters."""
        self._filters = []
        return self

    def _apply_filters(self, atoms: List[Dict]) -> List[Dict]:
        """Apply all current filters to atom list."""
        result = atoms
        for field, value in self._filters:
            result = [a for a in result if self._get_nested(a, field) == value]
        return result

    def _get_nested(self, obj: Dict, path: str) -> Any:
        """Get nested field value using dot notation."""
        parts = path.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    # =========================================================================
    # LAYER SUMMARY
    # =========================================================================

    def show_layer_summary(self) -> None:
        """Show summary of what each layer contains."""
        print("\n" + "=" * 70)
        print("PROGRESSIVE LAYER SYSTEM - The Standard Model of Code")
        print("=" * 70)

        for layer_id, info in LAYERS.items():
            print(f"\n{'_' * 68}")
            print(f"| L{info.level}: {info.name:<20} {info.description:>40} |")
            print(f"|{'-' * 68}|")
            print(f"| Key Fields: {', '.join(info.key_fields[:4]):<54} |")
            if info.requires:
                print(f"| Requires: {info.requires:<56} |")
            print(f"| Reveals: {info.reveals:<57} |")
            print(f"|{'_' * 68}|")

        print("\n" + "=" * 70)
        print("Each layer builds on the previous. You cannot compute L3 without L2.")
        print("=" * 70)

    # =========================================================================
    # LAYER REVELATION
    # =========================================================================

    def reveal_layer(self, layer_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Reveal statistics and sample data for a specific layer.

        Args:
            layer_id: One of L0_RAW through L7_SEMANTIC
            limit: Max atoms to show in detail

        Returns:
            Dict with layer statistics
        """
        info = get_layer(layer_id)
        if not info:
            print(f"Unknown layer: {layer_id}")
            print(f"Valid layers: {list(LAYERS.keys())}")
            return {}

        atoms = self._apply_filters(self.atoms)

        print(f"\n{'=' * 70}")
        print(f"REVEALING LAYER {info.level}: {info.name}")
        print(f"{'=' * 70}")
        print(f"Description: {info.description}")
        print(f"Total atoms: {len(atoms)}")

        # Compute statistics using LayerStatistics
        stats = self._statistics.compute(layer_id, atoms, self.data)
        stats["filtered"] = len(self._filters) > 0

        # Print stats
        print(f"\n{'-' * 50}")
        print("STATISTICS")
        print(f"{'-' * 50}")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in sorted(value.items(), key=lambda x: -x[1] if isinstance(x[1], (int, float)) else 0)[:10]:
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")

        # Show sample atoms
        print(f"\n{'-' * 50}")
        print(f"SAMPLE ATOMS (first {min(limit, len(atoms))})")
        print(f"{'-' * 50}")

        for atom in atoms[:limit]:
            self._print_atom_at_layer(atom, layer_id, info)

        return stats

    def _print_atom_at_layer(self, atom: Dict, layer_id: str, info: LayerInfo) -> None:
        """Print a single atom's data at the specified layer."""
        name = atom.get("name", "?")
        kind = atom.get("kind", "?")

        print(f"\n  * {name} ({kind})")

        # Print relevant fields for this layer
        for field in info.key_fields[:6]:
            value = self._get_nested(atom, field)
            if value is not None:
                if isinstance(value, dict):
                    print(f"    {field}: {{...}}")
                elif isinstance(value, list):
                    print(f"    {field}: [{len(value)} items]")
                else:
                    # Truncate long strings
                    s = str(value)
                    if len(s) > 60:
                        s = s[:57] + "..."
                    print(f"    {field}: {s}")

    # =========================================================================
    # PROGRESSIVE REVELATION
    # =========================================================================

    def reveal_progressive(self, atom_id: str) -> None:
        """
        Progressively reveal all layers for a specific atom.

        Shows how each layer builds on the previous.
        """
        # Find the atom
        atom = None
        for a in self.atoms:
            if a.get("id") == atom_id or a.get("name") == atom_id:
                atom = a
                break

        if not atom:
            print(f"Atom not found: {atom_id}")
            return

        name = atom.get("name", atom_id)
        print(f"\n{'=' * 70}")
        print(f"PROGRESSIVE REVELATION: {name}")
        print(f"{'=' * 70}")

        # Go through each layer
        for layer_id, info in LAYERS.items():
            print(f"\n{'_' * 68}")
            print(f"| L{info.level}: {info.name:<58} |")
            print(f"|{'-' * 68}|")

            # Check what data exists at this layer
            has_data = self._print_layer_data(atom, layer_id)

            if not has_data:
                print(f"| {'(no data at this layer)':<66} |")

            print(f"| -> {info.reveals:<64} |")
            print(f"|{'_' * 68}|")

    def _print_layer_data(self, atom: Dict, layer_id: str) -> bool:
        """Print atom data for a specific layer. Returns True if data exists."""
        has_data = False

        if layer_id == "L1_STRUCTURAL":
            if atom.get("name"):
                print(f"| name: {atom.get('name'):<59} |")
                print(f"| kind: {atom.get('kind'):<59} |")
                print(f"| file: {str(atom.get('file_path', ''))[:59]:<59} |")
                print(f"| line: {str(atom.get('start_line', '')):<59} |")
                has_data = True

        elif layer_id == "L2_CLASSIFICATION":
            role = atom.get("role") or atom.get("type") or atom.get("purpose")
            if role:
                conf = atom.get("role_confidence") or atom.get("confidence", 0)
                print(f"| role: {role:<59} |")
                print(f"| confidence: {conf:<54} |")
                print(f"| layer: {str(atom.get('layer', '')):<58} |")
                has_data = True

        elif layer_id == "L3_DIMENSION":
            dims = atom.get("dimensions", {})
            if dims:
                for d in ["D1_WHAT", "D2_LAYER", "D3_ROLE", "D4_BOUNDARY"]:
                    val = dims.get(d, "")
                    print(f"| {d}: {str(val):<58} |")
                has_data = True

        elif layer_id == "L4_LENS":
            lenses = atom.get("lenses", {})
            if lenses:
                for r in ["R1_IDENTITY", "R3_CLASSIFICATION", "R5_RELATIONSHIPS"]:
                    if r in lenses:
                        print(f"| {r}: {{...}}{'':54} |")
                has_data = True

        elif layer_id == "L5_GRAPH":
            lenses = atom.get("lenses", {})
            rels = lenses.get("R5_RELATIONSHIPS", {})
            if rels:
                print(f"| in_degree: {rels.get('in_degree', 0):<55} |")
                print(f"| out_degree: {rels.get('out_degree', 0):<54} |")
                print(f"| is_hub: {rels.get('is_hub', False):<57} |")
                has_data = True

        return has_data

    # =========================================================================
    # DRILL DOWN QUERIES
    # =========================================================================

    def find_by_role(self, role: str) -> List[Dict]:
        """Find all atoms with a specific role."""
        return [a for a in self.atoms if
                a.get("role") == role or
                a.get("type") == role or
                a.get("purpose") == role]

    def find_by_layer(self, arch_layer: str) -> List[Dict]:
        """Find all atoms in a specific architectural layer."""
        return [a for a in self.atoms if
                a.get("layer") == arch_layer or
                a.get("dimensions", {}).get("D2_LAYER") == arch_layer]

    def find_hubs(self) -> List[Dict]:
        """Find all hub nodes (high out-degree)."""
        return [a for a in self.atoms if
                a.get("lenses", {}).get("R5_RELATIONSHIPS", {}).get("is_hub")]

    def find_orphans(self) -> List[Dict]:
        """Find all orphan nodes (no connections)."""
        return [a for a in self.atoms if
                a.get("lenses", {}).get("R5_RELATIONSHIPS", {}).get("is_isolated")]

    def find_high_complexity(self, threshold: int = 10) -> List[Dict]:
        """Find atoms with high complexity."""
        return [a for a in self.atoms if
                a.get("complexity", 0) >= threshold]

    # =========================================================================
    # CROSS-LAYER ANALYSIS
    # =========================================================================

    def cross_layer_matrix(self, dim1: str, dim2: str) -> Dict[str, Dict[str, int]]:
        """
        Create a cross-tabulation of two dimensions.

        Example:
            matrix = revealer.cross_layer_matrix("role", "layer")
        """
        return self._statistics.cross_tabulate(self.atoms, dim1, dim2)

    def print_matrix(self, matrix: Dict[str, Dict[str, int]], title: str = "Cross-Layer Matrix") -> None:
        """Pretty-print a cross-tabulation matrix."""
        print(f"\n{title}")
        print("=" * 70)

        # Get all column keys
        all_cols = set()
        for row_data in matrix.values():
            all_cols.update(row_data.keys())
        cols = sorted(all_cols)

        # Header
        print(f"{'':20}", end="")
        for col in cols:
            print(f"{col[:10]:>12}", end="")
        print()

        # Rows
        for row, row_data in sorted(matrix.items()):
            print(f"{row[:20]:20}", end="")
            for col in cols:
                count = row_data.get(col, 0)
                print(f"{count:>12}", end="")
            print()
