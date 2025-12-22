
import sys
import os
from pathlib import Path

# Add CWD to path
sys.path.insert(0, os.getcwd())

from core.intelligence import IntelligenceEvaluator, ComplianceScorer, StandardModelPhysics
from dataclasses import dataclass

@dataclass
class MockParticle:
    id: str
    name: str
    module_path: str
    continent: str
    architectural_layer: str
    is_pure: bool = True
    node_count: int = 10

def run_verification():
    print("🧪 Verifying Best Practices Intelligence Layer...")
    
    # 1. create Mock Particles
    
    # Healthy Particle
    p_healthy = MockParticle(
        id="P1", name="StringUtil", module_path="utils/string_util.py",
        continent="Data Foundations", architectural_layer="infrastructure"
    )
    
    # Violating Particle: Data Foundation (Impure)
    p_impure = MockParticle(
        id="P2", name="BadData", module_path="models/bad_data.py",
        continent="Data Foundations", architectural_layer="domain",
        is_pure=False
    )
    
    # Violating Particle: God Class (implied by future check, currently mocked check usually passes unless we mock detailed sizing)
    
    particles = [p_healthy, p_impure]
    
    # 2. Evaluate
    evaluator = IntelligenceEvaluator()
    violations = evaluator.evaluate_codebase(particles)
    
    print(f"📊 Evaluated {len(particles)} particles, found {len(violations)} violations.")
    
    for v in violations:
        print(f"  ❌ Violation: {v.rule_name} - {v.details}")
        print(f"     💡 Solution: {v.solution}")
        
    # 3. Score
    scorer = ComplianceScorer()
    result = scorer.calculate_score(violations, len(particles))
    
    print(f"\n🏆 Score: {result['score']}/100 Grade: {result['grade']}")
    print(f"   Breakdown: {result['breakdown']}")
    
    if len(violations) >= 1 and result['score'] < 100:
        print("\n✅ VERIFICATION PASSED: Intelligence Layer detected violations and reduced score.")
    else:
        print("\n❌ VERIFICATION FAILED: Did not detect expected violations.")

if __name__ == "__main__":
    run_verification()
