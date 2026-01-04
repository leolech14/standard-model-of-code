"""
Antimatter Evaluator (Backward Compatibility Module)
====================================================

This module re-exports from the refactored antimatter package.
New code should import from src.core.antimatter directly.

Old:
    from antimatter_evaluator import AntimatterEvaluator, Violation

New:
    from src.core.antimatter import AntimatterEvaluator, Violation
"""

# Re-export everything from the new package for backward compatibility
from src.core.antimatter import (
    Violation,
    EvaluationResult,
    ParticleAccessor,
    PatternMatcher,
    AntimatterEvaluator,
    LAWS_PATH,
    check_purity_violation,
    check_command_returns,
    check_query_mutation,
)

__all__ = [
    'Violation',
    'EvaluationResult',
    'ParticleAccessor',
    'PatternMatcher',
    'AntimatterEvaluator',
    'LAWS_PATH',
    'check_purity_violation',
    'check_command_returns',
    'check_query_mutation',
]


# CLI for backward compatibility
if __name__ == "__main__":
    print("=" * 70)
    print("ANTIMATTER EVALUATOR - Constraint Checker")
    print("=" * 70)

    evaluator = AntimatterEvaluator()
    print(f"Loaded {len(evaluator.laws)} laws")

    # Demo with sample particles
    sample_particles = [
        {
            "id": "p1",
            "name": "get_user",
            "type": "PureFunction",
            "confidence": 0.8,
            "imports": ["requests"],
            "file_path": "utils.py",
            "line": 10,
        },
        {
            "id": "p2",
            "name": "UserEntity",
            "type": "Entity",
            "confidence": 0.9,
            "fields": ["name", "email"],  # Missing id!
            "file_path": "domain/user.py",
            "line": 5,
        },
        {
            "id": "p3",
            "name": "CreateUserCommand",
            "type": "Command",
            "confidence": 0.85,
            "file_path": "commands/user.py",
            "line": 1,
        },
    ]

    print(f"\nEvaluating {len(sample_particles)} sample particles...")
    result = evaluator.evaluate(sample_particles)

    print(f"\nResults:")
    print(f"   Violations: {len(result.violations)}")
    print(f"   By severity: {result.by_severity}")
    print(f"   By law: {result.by_law}")

    if result.violations:
        print("\nViolations found:")
        for v in result.violations:
            print(f"   [{v.severity.upper()}] {v.law_id}: {v.particle_name} ({v.particle_type})")
            for e in v.evidence:
                print(f"      - {e}")
