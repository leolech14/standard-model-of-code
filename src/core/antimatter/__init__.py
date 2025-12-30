"""
Antimatter Package
==================

Machine-executable constraint checker for the 11 canonical antimatter laws.

The package is organized into:
- Models: Violation and EvaluationResult data classes
- ParticleAccessor: Consistent access to particle data
- PatternMatcher: Pattern matching against law definitions
- AntimatterEvaluator: Main facade orchestrating evaluation

Usage:
    from src.core.antimatter import AntimatterEvaluator, Violation, EvaluationResult

    evaluator = AntimatterEvaluator()
    result = evaluator.evaluate(particles)
    for v in result.violations:
        print(f"{v.law_id}: {v.particle_name}")
"""

from .models import Violation, EvaluationResult
from .particle_accessor import ParticleAccessor
from .pattern_matcher import PatternMatcher
from .evaluator import (
    AntimatterEvaluator,
    LAWS_PATH,
    check_purity_violation,
    check_command_returns,
    check_query_mutation,
)

__all__ = [
    # Models
    'Violation',
    'EvaluationResult',
    # Components
    'ParticleAccessor',
    'PatternMatcher',
    # Main class
    'AntimatterEvaluator',
    'LAWS_PATH',
    # Helper functions
    'check_purity_violation',
    'check_command_returns',
    'check_query_mutation',
]
