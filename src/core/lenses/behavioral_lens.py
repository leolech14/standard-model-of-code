"""
Behavioral Lens
===============

Interrogates code atoms for behavioral properties:
- R5: RELATIONSHIPS - How is it connected?
- R6: TRANSFORMATION - What does it do?
"""

from typing import Dict, Any, List


class BehavioralLens:
    """
    Reveals behavioral properties of code atoms.

    Handles relationship and transformation questions.
    """

    # ==================== R5: RELATIONSHIPS ====================

    def lens_r5_relationships(
        self,
        node: Dict[str, Any],
        edges: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        R5: RELATIONSHIPS - How is it connected?

        Reveals: Calls, imports, inheritance, dependencies
        """
        edges = edges or []
        node_id = node.get("id", "")

        outgoing = [e for e in edges if e.get("source") == node_id]
        incoming = [e for e in edges if e.get("target") == node_id]

        calls_out = [e for e in outgoing if e.get("edge_type") == "calls"]
        called_by = [e for e in incoming if e.get("edge_type") == "calls"]
        imports = [e for e in outgoing if e.get("edge_type") == "imports"]
        inherits_from = [e for e in outgoing if e.get("edge_type") == "inherits"]

        in_degree = len(incoming)
        out_degree = len(outgoing)
        fan_in = len(called_by)
        fan_out = len(calls_out)

        is_hub = out_degree > 5
        is_authority = in_degree > 5

        return {
            "in_degree": in_degree,
            "out_degree": out_degree,
            "fan_in": fan_in,
            "fan_out": fan_out,
            "calls": [e.get("target") for e in calls_out],
            "called_by": [e.get("source") for e in called_by],
            "imports": [e.get("target") for e in imports],
            "inherits_from": [e.get("target") for e in inherits_from],
            "is_hub": is_hub,
            "is_authority": is_authority,
            "is_isolated": in_degree == 0 and out_degree == 0,
        }

    # ==================== R6: TRANSFORMATION ====================

    def lens_r6_transformation(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        R6: TRANSFORMATION - What does it do?

        Reveals: Input → Output transformation
        """
        params = node.get("params", [])
        return_type = node.get("return_type", "")
        dimensions = node.get("dimensions", {})

        effect = dimensions.get("D6_EFFECT", "Unknown")
        is_pure = effect == "Pure"

        transform_type = self._infer_transformation_type(
            node.get("name", ""),
            params,
            return_type
        )

        input_types = [p.get("type", "Any") for p in params]
        output_type = return_type or "Any"

        return {
            "input_count": len(params),
            "input_types": input_types,
            "output_type": output_type,
            "transformation_type": transform_type,
            "is_pure": is_pure,
            "is_deterministic": is_pure,
            "effect_type": effect,
            "signature": self._build_signature(params, return_type),
        }

    def _infer_transformation_type(
        self,
        name: str,
        params: List,
        return_type: str
    ) -> str:
        """Infer what kind of transformation this performs."""
        name_lower = name.lower()

        if any(p in name_lower for p in ["convert", "transform", "map", "parse", "format"]):
            return "converter"
        elif any(p in name_lower for p in ["filter", "select", "find", "search"]):
            return "filter"
        elif any(p in name_lower for p in ["reduce", "aggregate", "sum", "count"]):
            return "aggregator"
        elif any(p in name_lower for p in ["validate", "check", "is", "has"]):
            return "predicate"
        elif len(params) > 0 and return_type:
            return "mapper"
        else:
            return "procedure"

    def _build_signature(self, params: List, return_type: str) -> str:
        """Build function signature string."""
        param_str = ", ".join([
            f"{p.get('name', 'arg')}: {p.get('type', 'Any')}"
            for p in params
        ])
        return f"({param_str}) -> {return_type or 'Any'}"

    # ==================== COMBINED ====================

    def interrogate(
        self,
        node: Dict[str, Any],
        edges: List[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Interrogate a node through all behavioral lenses.

        Returns dict with R5, R6 results.
        """
        return {
            "R5_RELATIONSHIPS": self.lens_r5_relationships(node, edges),
            "R6_TRANSFORMATION": self.lens_r6_transformation(node),
        }
