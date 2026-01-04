"""
Particle Accessor
=================

Extracts data from particle dictionaries in a consistent way.
"""

from typing import Any, Dict, List, Set


class ParticleAccessor:
    """
    Provides consistent access to particle data.

    Handles multiple field naming conventions that may exist
    in different particle sources.
    """

    def get_edge_types(self, particle: Dict[str, Any]) -> Set[str]:
        """
        Get edge types from particle.

        Handles both 'edges' and 'outgoing_edges' fields.
        """
        edges = particle.get("edges", []) or particle.get("outgoing_edges", [])
        return {e.get("type", e) if isinstance(e, dict) else str(e) for e in edges}

    def get_imports(self, particle: Dict[str, Any]) -> List[str]:
        """Get imports from particle."""
        return particle.get("imports", []) or []

    def get_calls(self, particle: Dict[str, Any]) -> List[str]:
        """
        Get function calls from particle.

        Handles both 'calls' and 'called_functions' fields.
        """
        return particle.get("calls", []) or particle.get("called_functions", []) or []

    def get_methods(self, particle: Dict[str, Any]) -> List[str]:
        """
        Get method names from particle.

        Handles both 'methods' and 'method_names' fields.
        """
        return particle.get("methods", []) or particle.get("method_names", []) or []

    def get_fields(self, particle: Dict[str, Any]) -> Set[str]:
        """
        Get field/attribute names from particle.

        Handles both 'fields' and 'attributes' fields.
        """
        fields = particle.get("fields", []) or particle.get("attributes", []) or []
        return set(fields)

    def get_code(self, particle: Dict[str, Any]) -> str:
        """
        Get code excerpt from particle.

        Handles both 'code_excerpt' and 'evidence' fields.
        """
        return particle.get("code_excerpt", "") or particle.get("evidence", "") or ""

    def get_type(self, particle: Dict[str, Any]) -> str:
        """Get particle type with default."""
        return particle.get("type", "Unknown")

    def get_confidence(self, particle: Dict[str, Any]) -> float:
        """Get particle confidence with default."""
        return particle.get("confidence", 0.5)

    def get_id(self, particle: Dict[str, Any]) -> str:
        """Get particle ID with default."""
        return particle.get("id", "unknown")

    def get_name(self, particle: Dict[str, Any]) -> str:
        """Get particle name with default."""
        return particle.get("name", "unknown")

    def get_file_path(self, particle: Dict[str, Any]) -> str:
        """Get file path with default."""
        return particle.get("file_path", "")

    def get_line(self, particle: Dict[str, Any]) -> int:
        """Get line number with default."""
        return particle.get("line", 0)
