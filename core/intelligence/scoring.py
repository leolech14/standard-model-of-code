"""
Intelligence Scoring (The Scorecard)

Calculates the Atomic Compliance Score (ACS) based on violations found.
"""

from typing import List, Dict
from .evaluator import Violation
from .rules import StandardModelPhysics

class ComplianceScorer:
    
    def calculate_score(self, violations: List[Violation], total_particles: int) -> Dict[str, Any]:
        """
        Calculate ACS on a 0-100 scale.
        
        Formula:
        Start with 100.
        Deduct points for violations based on severity.
        Normalize by codebase size to avoid punishing large codebases unfairly?
        Actually, usually score is per-particle average or density.
        
        Let's do: 100 - (ViolationPoints / TotalParticles * Factor)
        """
        
        if total_particles == 0:
            return {"score": 100, "grade": "A+", "breakdown": {}}
            
        # Deduct points
        penalty_points = 0
        breakdown = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
        
        for v in violations:
            breakdown[v.severity] += 1
            if v.severity == "CRITICAL":
                penalty_points += 10
            elif v.severity == "WARNING":
                penalty_points += 3
            elif v.severity == "INFO":
                penalty_points += 1
        
        # Calculate raw score per particle to normalize
        # e.g., Average Permission Points per Particle
        # If every particle has 1 critical error, score should be low.
        
        avg_penalty = penalty_points / total_particles
        
        # Scaling: How much penalty per particle reduces the score significantly?
        # If avg_penalty is 0.5 (1 warning every 6 particles), score might be 95.
        # If avg_penalty is 10 (1 critical every particle), score should be 0.
        
        # Linear drop: Score = 100 - (avg_penalty * 10)
        # If avg_penalty = 1 (1 warning every 3 particles), Score = 90.
        # If avg_penalty = 5 (1 warning every 0.6 particles), Score = 50.
        
        score = max(0, 100 - (avg_penalty * 5))
        
        # Grading
        grade = "F"
        if score >= 97: grade = "A+"
        elif score >= 93: grade = "A"
        elif score >= 90: grade = "A-"
        elif score >= 87: grade = "B+"
        elif score >= 83: grade = "B"
        elif score >= 80: grade = "B-"
        elif score >= 70: grade = "C"
        elif score >= 60: grade = "D"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "total_violations": len(violations),
            "breakdown": breakdown,
            "penalty_points": penalty_points
        }
