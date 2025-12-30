"""
Antimatter Evaluator
====================

Main facade for evaluating particles against antimatter laws.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Violation, EvaluationResult
from .pattern_matcher import PatternMatcher
from .particle_accessor import ParticleAccessor

# Path to canonical laws
LAWS_PATH = Path(__file__).parent.parent.parent / "data" / "LAW_11_CANONICAL.json"


class AntimatterEvaluator:
    """
    Evaluates particles against the 11 canonical antimatter laws.

    Each law is evaluated using pattern matching defined in data/LAW_11_CANONICAL.json.

    Usage:
        evaluator = AntimatterEvaluator()
        result = evaluator.evaluate(particles)
        print(result.to_dict())
    """

    def __init__(self, laws_path: Path = LAWS_PATH):
        """
        Initialize the evaluator.

        Args:
            laws_path: Path to JSON file containing law definitions
        """
        self.laws = self._load_laws(laws_path)
        self.pattern_matcher = PatternMatcher()
        self.accessor = ParticleAccessor()

    def _load_laws(self, path: Path) -> List[Dict[str, Any]]:
        """Load laws from JSON file."""
        if not path.exists():
            print(f"Warning: Laws file not found: {path}")
            return []
        return json.loads(path.read_text())

    def evaluate(
        self,
        particles: List[Dict[str, Any]],
        threshold: float = 0.55,
    ) -> EvaluationResult:
        """
        Evaluate all laws against all particles.

        Args:
            particles: List of particle dicts with type, edges, etc.
            threshold: Minimum confidence to report violations

        Returns:
            EvaluationResult with all violations
        """
        result = EvaluationResult(
            total_particles=len(particles),
            laws_checked=len(self.laws),
        )

        for law in self.laws:
            law_violations = self._evaluate_law(law, particles, threshold)
            result.violations.extend(law_violations)
            result.by_law[law["id"]] = len(law_violations)

        # Count by severity
        for v in result.violations:
            result.by_severity[v.severity] = result.by_severity.get(v.severity, 0) + 1

        return result

    def _evaluate_law(
        self,
        law: Dict[str, Any],
        particles: List[Dict[str, Any]],
        threshold: float,
    ) -> List[Violation]:
        """Evaluate a single law against all particles."""
        violations = []
        pattern = law.get("pattern", {})
        particle_types = pattern.get("particle_types", law.get("scope", []))
        law_threshold = law.get("threshold", threshold)

        for particle in particles:
            p_type = self.accessor.get_type(particle)
            p_conf = self.accessor.get_confidence(particle)

            # Skip if particle type doesn't match law scope
            if p_type not in particle_types:
                continue

            # Skip if confidence too low
            if p_conf < law_threshold:
                continue

            # Check for violations using PatternMatcher
            violation = self.pattern_matcher.check_particle(law, pattern, particle)
            if violation:
                violations.append(violation)

        return violations

    def check_single(
        self,
        particle: Dict[str, Any],
        law_id: Optional[str] = None
    ) -> List[Violation]:
        """
        Check a single particle against one or all laws.

        Args:
            particle: Particle to check
            law_id: Optional specific law to check (None = all laws)

        Returns:
            List of violations found
        """
        violations = []
        laws_to_check = self.laws

        if law_id:
            laws_to_check = [l for l in self.laws if l["id"] == law_id]

        for law in laws_to_check:
            pattern = law.get("pattern", {})
            particle_types = pattern.get("particle_types", law.get("scope", []))
            p_type = self.accessor.get_type(particle)

            if p_type in particle_types:
                violation = self.pattern_matcher.check_particle(law, pattern, particle)
                if violation:
                    violations.append(violation)

        return violations


# =============================================================================
# INDIVIDUAL LAW CHECKERS (for use as detector functions)
# =============================================================================

def check_purity_violation(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L3: Check if a pure function has side effects."""
    matcher = PatternMatcher()
    return matcher.check_particle(law, law.get("pattern", {}), particle)


def check_command_returns(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L1: Check if CommandHandler returns domain data."""
    matcher = PatternMatcher()
    return matcher.check_particle(law, law.get("pattern", {}), particle)


def check_query_mutation(particle: Dict[str, Any], law: Dict[str, Any]) -> Optional[Violation]:
    """L2: Check if QueryHandler mutates state."""
    matcher = PatternMatcher()
    return matcher.check_particle(law, law.get("pattern", {}), particle)
