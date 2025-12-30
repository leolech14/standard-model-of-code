"""
Layer Statistics
================

Statistical computation engine for layer-based analysis.
"""

from typing import Dict, List, Any
from collections import defaultdict


class LayerStatistics:
    """
    Computes statistics for different layers of analysis.

    Each layer has specific metrics that are computed from the atom data.
    """

    def compute(
        self,
        layer_id: str,
        atoms: List[Dict],
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Compute statistics for a specific layer.

        Args:
            layer_id: Layer identifier (L0_RAW through L7_SEMANTIC)
            atoms: List of atom dictionaries
            data: Optional full analysis data (for L6_MATH)

        Returns:
            Dictionary of computed statistics
        """
        stats = {
            "total_count": len(atoms),
            "filtered": False
        }

        if layer_id == "L1_STRUCTURAL":
            stats.update(self._compute_structural(atoms))
        elif layer_id == "L2_CLASSIFICATION":
            stats.update(self._compute_classification(atoms))
        elif layer_id == "L3_DIMENSION":
            stats.update(self._compute_dimension(atoms))
        elif layer_id == "L5_GRAPH":
            stats.update(self._compute_graph(atoms))
        elif layer_id == "L6_MATH":
            stats.update(self._compute_math(atoms, data or {}))

        return stats

    def _compute_structural(self, atoms: List[Dict]) -> Dict[str, Any]:
        """Compute L1 structural layer statistics."""
        kinds = defaultdict(int)
        complexities = []

        for a in atoms:
            kinds[a.get("kind", "unknown")] += 1
            if "complexity" in a:
                complexities.append(a["complexity"])

        result = {"kind_distribution": dict(kinds)}

        if complexities:
            result["avg_complexity"] = sum(complexities) / len(complexities)
            result["max_complexity"] = max(complexities)

        return result

    def _compute_classification(self, atoms: List[Dict]) -> Dict[str, Any]:
        """Compute L2 classification layer statistics."""
        roles = defaultdict(int)
        layers = defaultdict(int)
        methods = defaultdict(int)

        for a in atoms:
            role = a.get("role") or a.get("type") or a.get("purpose") or "Unknown"
            roles[role] += 1

            layer = a.get("layer") or a.get("arch_layer") or "Unknown"
            layers[layer] += 1

            method = a.get("discovery_method", "unknown")
            methods[method] += 1

        # Coverage calculation
        known = sum(1 for a in atoms if a.get("role") not in [None, "Unknown"])
        coverage = f"{known}/{len(atoms)} ({100*known/len(atoms):.1f}%)" if atoms else "0%"

        return {
            "role_distribution": dict(roles),
            "layer_distribution": dict(layers),
            "discovery_methods": dict(methods),
            "coverage": coverage
        }

    def _compute_dimension(self, atoms: List[Dict]) -> Dict[str, Any]:
        """Compute L3 8D dimension layer statistics."""
        d2_dist = defaultdict(int)
        d4_dist = defaultdict(int)
        d5_dist = defaultdict(int)
        d6_dist = defaultdict(int)

        for a in atoms:
            d = a.get("dimensions", {})
            d2_dist[d.get("D2_LAYER", "Unknown")] += 1
            d4_dist[d.get("D4_BOUNDARY", "Unknown")] += 1
            d5_dist[d.get("D5_STATE", "Unknown")] += 1
            d6_dist[d.get("D6_EFFECT", "Unknown")] += 1

        return {
            "D2_LAYER_distribution": dict(d2_dist),
            "D4_BOUNDARY_distribution": dict(d4_dist),
            "D5_STATE_distribution": dict(d5_dist),
            "D6_EFFECT_distribution": dict(d6_dist)
        }

    def _compute_graph(self, atoms: List[Dict]) -> Dict[str, Any]:
        """Compute L5 graph structure statistics."""
        in_degrees = []
        out_degrees = []
        hubs = 0
        authorities = 0
        orphans = 0

        for a in atoms:
            lenses = a.get("lenses", {})
            rels = lenses.get("R5_RELATIONSHIPS", {})

            in_deg = rels.get("in_degree", 0)
            out_deg = rels.get("out_degree", 0)
            in_degrees.append(in_deg)
            out_degrees.append(out_deg)

            if rels.get("is_hub"):
                hubs += 1
            if rels.get("is_authority"):
                authorities += 1
            if rels.get("is_isolated"):
                orphans += 1

        return {
            "avg_in_degree": sum(in_degrees) / len(in_degrees) if in_degrees else 0,
            "avg_out_degree": sum(out_degrees) / len(out_degrees) if out_degrees else 0,
            "hub_count": hubs,
            "authority_count": authorities,
            "orphan_count": orphans
        }

    def _compute_math(self, atoms: List[Dict], data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute L6 mathematical/4-pillars statistics."""
        math = data.get("math_coverage", {})
        result = {}

        if math:
            result["markov"] = math.get("markov", {})
            result["knot"] = math.get("knot", {})
            result["constructal"] = math.get("constructal", {})

        return result

    def cross_tabulate(
        self,
        atoms: List[Dict],
        dim1: str,
        dim2: str
    ) -> Dict[str, Dict[str, int]]:
        """
        Create a cross-tabulation of two dimensions.

        Args:
            atoms: List of atom dictionaries
            dim1: First dimension path (dot notation)
            dim2: Second dimension path (dot notation)

        Returns:
            Nested dict: matrix[dim1_value][dim2_value] = count
        """
        matrix = defaultdict(lambda: defaultdict(int))

        for atom in atoms:
            val1 = self._get_nested(atom, dim1) or "Unknown"
            val2 = self._get_nested(atom, dim2) or "Unknown"
            matrix[val1][val2] += 1

        return {k: dict(v) for k, v in matrix.items()}

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
