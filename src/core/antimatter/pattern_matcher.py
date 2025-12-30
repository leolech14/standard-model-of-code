"""
Pattern Matcher
===============

Matches particles against antimatter law patterns.
"""

from typing import Any, Dict, List, Optional

from .models import Violation
from .particle_accessor import ParticleAccessor


class PatternMatcher:
    """
    Checks particles against antimatter law patterns.

    Supports:
    - Forbidden edges, imports, calls, methods, fields
    - Required fields and patterns
    - Inversion patterns (violation if required things are MISSING)
    """

    def __init__(self):
        self.accessor = ParticleAccessor()

    def check_particle(
        self,
        law: Dict[str, Any],
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
    ) -> Optional[Violation]:
        """
        Check if a particle violates a law pattern.

        Args:
            law: Law definition with id, name, statement, severity
            pattern: Pattern specification with forbidden/required items
            particle: Particle to check

        Returns:
            Violation if law is violated, None otherwise
        """
        evidence = []
        is_violation = False

        # Check forbidden edges
        if self._check_forbidden_edges(pattern, particle, evidence):
            is_violation = True

        # Check forbidden imports
        if self._check_forbidden_imports(pattern, particle, evidence):
            is_violation = True

        # Check forbidden calls
        if self._check_forbidden_calls(pattern, particle, evidence):
            is_violation = True

        # Check forbidden methods
        if self._check_forbidden_methods(pattern, particle, evidence):
            is_violation = True

        # Check forbidden fields
        if self._check_forbidden_fields(pattern, particle, evidence):
            is_violation = True

        # Check required fields (violation if MISSING)
        if self._check_required_fields(pattern, particle, evidence):
            is_violation = True

        # Check required patterns (violation if MISSING)
        if self._check_required_patterns(pattern, particle, evidence):
            is_violation = True

        # Check inversion patterns
        if self._check_inversion(pattern, particle, evidence):
            is_violation = True

        if not is_violation:
            return None

        return Violation(
            law_id=law["id"],
            law_name=law["name"],
            particle_id=self.accessor.get_id(particle),
            particle_name=self.accessor.get_name(particle),
            particle_type=self.accessor.get_type(particle),
            file_path=self.accessor.get_file_path(particle),
            line=self.accessor.get_line(particle),
            message=law["statement"],
            severity=law.get("severity", "warning"),
            confidence=self.accessor.get_confidence(particle),
            evidence=evidence,
        )

    def _check_forbidden_edges(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for forbidden edge types."""
        forbidden_edges = pattern.get("forbidden_edges", [])
        if not forbidden_edges:
            return False

        particle_edges = self.accessor.get_edge_types(particle)
        found = False
        for edge in forbidden_edges:
            if edge in particle_edges:
                found = True
                evidence.append(f"Has forbidden edge: {edge}")
        return found

    def _check_forbidden_imports(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for forbidden imports."""
        forbidden_imports = pattern.get("forbidden_imports", [])
        if not forbidden_imports:
            return False

        particle_imports = self.accessor.get_imports(particle)
        found = False
        for imp in forbidden_imports:
            if any(imp in i for i in particle_imports):
                found = True
                evidence.append(f"Has forbidden import: {imp}")
        return found

    def _check_forbidden_calls(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for forbidden function calls."""
        forbidden_calls = pattern.get("forbidden_calls", [])
        if not forbidden_calls:
            return False

        particle_calls = self.accessor.get_calls(particle)
        found = False
        for call in forbidden_calls:
            if any(call in c for c in particle_calls):
                found = True
                evidence.append(f"Has forbidden call: {call}")
        return found

    def _check_forbidden_methods(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for forbidden method patterns."""
        forbidden_methods = pattern.get("forbidden_methods", [])
        if not forbidden_methods:
            return False

        particle_methods = self.accessor.get_methods(particle)
        found = False
        for method in forbidden_methods:
            if any(method in m for m in particle_methods):
                found = True
                evidence.append(f"Has forbidden method pattern: {method}")
        return found

    def _check_forbidden_fields(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for forbidden fields."""
        forbidden_fields = pattern.get("forbidden_fields", [])
        if not forbidden_fields:
            return False

        particle_fields = self.accessor.get_fields(particle)
        found = False
        for f in forbidden_fields:
            if f in particle_fields:
                found = True
                evidence.append(f"Has forbidden field: {f}")
        return found

    def _check_required_fields(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for missing required fields (violation if MISSING)."""
        required_fields = pattern.get("required_fields", [])
        if not required_fields:
            return False

        particle_fields = self.accessor.get_fields(particle)
        has_any = any(f in particle_fields for f in required_fields)
        if not has_any:
            evidence.append(f"Missing required field (one of: {required_fields})")
            return True
        return False

    def _check_required_patterns(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check for missing required patterns (violation if MISSING)."""
        required_patterns = pattern.get("required_patterns", [])
        if not required_patterns:
            return False

        code = self.accessor.get_code(particle)
        has_any = any(p in code for p in required_patterns)
        if not has_any and not pattern.get("inversion"):
            evidence.append(f"Missing required pattern (one of: {required_patterns})")
            return True
        return False

    def _check_inversion(
        self,
        pattern: Dict[str, Any],
        particle: Dict[str, Any],
        evidence: List[str]
    ) -> bool:
        """Check inversion patterns (violation if required things are MISSING)."""
        if not pattern.get("inversion"):
            return False

        required_edges = pattern.get("required_edges", [])
        if not required_edges:
            return False

        particle_edges = self.accessor.get_edge_types(particle)
        has_any = any(e in particle_edges for e in required_edges)
        if not has_any:
            evidence.append(pattern.get("inversion_message", "Missing required edges"))
            return True
        return False
