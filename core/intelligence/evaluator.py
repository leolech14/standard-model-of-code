"""
Intelligence Evaluator (The Judge)

This module implements the logic to verify Semantic Particles against the
Standard Model Physics defined in rules.py.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from .rules import StandardModelPhysics, ArchitecturalRule

@dataclass
class Violation:
    rule_id: str
    rule_name: str
    severity: str
    particle_id: str
    file_path: str
    details: str
    solution: str = "Refactor code to adhere to the architectural rule."

class IntelligenceEvaluator:
    def __init__(self):
        self.rules = StandardModelPhysics.ALL_RULES

    def evaluate_particle(self, particle: Any) -> List[Violation]:
        """
        Evaluate a single particle against all applicable rules.
        """
        violations = []
        
        # 1. Check Layering (Gravity)
        violations.extend(self._check_gravity(particle))

        # 2. Check Purity
        violations.extend(self._check_purity(particle))

        # 3. Check Sizing
        violations.extend(self._check_sizing(particle))

        return violations

    def _check_gravity(self, particle) -> List[Violation]:
        """Enforce dependencies flowing down."""
        violations = []
        
        # Skip if no boundary data
        if not hasattr(particle, 'architectural_layer'):
            return []
            
        current_layer = particle.architectural_layer
        
        # Simplified layer hierarchy map (lower index = lower layer / more foundational)
        # 0: Interface/App -> 1: Logic -> 2: Data
        # Wait, usually Data is at bottom (0) and Interface at top.
        # Let's map strict Standard Model continents:
        # Data Foundations (0) -> Logic & Flow (1) -> Organization (2) ? 
        # Actually, "Dependency Rule": High level policy should not depend on low level detail?
        # Standard Model "Gravity":
        # Data Foundations (Primitives) should NOT depend on Logic or UI.
        
        # Let's use the explicit 'continent' if available
        continent = getattr(particle, 'continent', 'Unknown')
        
        # Simple rule: Data Foundations cannot import Logic & Flow
        if continent == "Data Foundations":
            # Check dependencies (this requires graph edges, which might not be on the particle object directly
            # depending on how SemanticID is structured. Assuming internal_dependencies list of strings).
            pass 

        # Placeholder for complex dependency graph check
        # (Requires access to full graph, which we might inject later)
        
        return violations

    def _check_purity(self, particle) -> List[Violation]:
        """Enforce atomic purity."""
        violations = []
        
        # Rule: Data Atoms must be pure
        if getattr(particle, 'continent', '') == "Data Foundations":
            if getattr(particle, 'is_pure', True) is False: # Explicitly False
                 violations.append(Violation(
                    rule_id=StandardModelPhysics.LAW_OF_ATOMIC_PURITY.id,
                    rule_name=StandardModelPhysics.LAW_OF_ATOMIC_PURITY.name,
                    severity=StandardModelPhysics.LAW_OF_ATOMIC_PURITY.severity,
                    particle_id=particle.id,
                    file_path=particle.module_path,
                    details=f"Data Atom '{particle.name}' is marked as impure/mutating.",
                    solution="Remove side effects from this Data Atom. Move logic to a Logic/Flow Atom or mark this as a Service."
                ))
        
        return violations

    def _check_sizing(self, particle) -> List[Violation]:
        """Check for God Classes."""
        violations = []
        
        # Check method count if available (assuming metadata)
        # This relies on the 'god_class_detector' having run and populated metadata
        # or we check raw children count
        
        # Placeholder logic
        node_count = getattr(particle, 'node_count', 0) 
        # A crude proxy if we don't have method count
        
        return violations

    def evaluate_codebase(self, semantic_ids: List[Any]) -> List[Violation]:
        """Evaluate all particles in the codebase."""
        all_violations = []
        for p in semantic_ids:
            all_violations.extend(self.evaluate_particle(p))
        return all_violations
