"""Information Graph Theory (IGT) Metrics.

This module implements the mathematical foundations for topological stability 
and type-aware orphan semantics in codebases.

IGT Axioms:
1. Stability (σ) is a function of Branching Factor (Bf) relative to cognitive thresholds.
2. Orphan Severity is ontologically dependent on the entity type (Code vs Context).
"""

import math
import os
from typing import List, Dict, Any, Set, Optional

class StabilityCalculator:
    """Computes structural stability for directory/module containers.
    
    Reference: TOPOLOGICAL_BOUNDARIES.md
    Theory: Miller's Law (7 ± 2) applied to filesystem branching.
    """
    
    @staticmethod
    def calculate_stability(branching_factor: int) -> float:
        """Computes the Stability Index (σ) on a 0.0 - 1.0 scale.
        
        Perfect stability (1.0) is achieved at Bf = 7.
        Degradation occurs as Bf moves away from the 5-9 range.
        """
        if branching_factor == 0:
            return 0.0
            
        # Distance from the optimal center (7)
        dist = abs(branching_factor - 7)
        
        # Sigmoid-like penalty curve
        # σ = 1 / (1 + e^(0.3 * (dist - 4)))  - adjusted to hit ~0.8 at 10 and ~0.8 at 4
        # Simplified linear-exponential drop for transparency:
        if dist <= 2: # Bf ∈ [5, 9]
            return 1.0 - (dist * 0.05)
        else:
            return max(0.0, 0.9 * math.exp(-0.15 * (dist - 2)))

    @classmethod
    def analyze_directories(cls, directory_structure: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Analyzes all directories in a structure.
        
        Args:
            directory_structure: Dict mapping dir_path to list of child names.
            
        Returns:
            Dict mapping dir_path to its stability metrics.
        """
        metrics = {}
        for path, children in directory_structure.items():
            bf = len(children)
            sigma = cls.calculate_stability(bf)
            
            status = "STABLE"
            if sigma < 0.4:
                status = "VOLATILE" if bf > 15 else "FRAGMENTED"
            elif sigma < 0.8:
                status = "UNBALANCED"
                
            metrics[path] = {
                "branching_factor": bf,
                "stability_index": round(sigma, 3),
                "status": status
            }
        return metrics

class OrphanClassifier:
    """Applies type-aware severity to isolated nodes (orphans).
    
    Reference: ORPHAN_SEMANTICS.md
    Theory: Orphan severity = f(Ontological Type).
    """
    
    # Severity Levels
    CRITICAL = 1.0   # Must be fixed/removed
    PROBLEM = 0.7    # Should be linked/integrated
    SUBOPTIMAL = 0.4 # Prefer links, but functional
    ACCEPTABLE = 0.1 # Fine as standalone
    NEUTRAL = 0.0    # No problem (e.g. artifacts)

    @classmethod
    def classify_severity(cls, node_id: str, node_type: str, file_path: str) -> Dict[str, Any]:
        """Classifies orphan severity based on type and path.
        
        Args:
            node_id: ID of the orphan node.
            node_type: 'file', 'atom', 'dir', etc.
            file_path: Physical location of the node.
            
        Returns:
            Dict with score and semantic label.
        """
        # 1. Code Orphans (Always Critical)
        if node_type == 'atom':
            return {"score": cls.CRITICAL, "label": "CRITICAL_CODE_ISOLATION", "is_problem": True}
            
        # 2. File Orphans (Branch by Path)
        ext = os.path.splitext(file_path)[1].lower()
        
        # Narrative Docs / Theory (Critical)
        if '/docs/theory/' in file_path or 'THEORY.md' in file_path:
            return {"score": cls.CRITICAL, "label": "NARRATIVE_DISCONTINUITY", "is_problem": True}
            
        # Governance (Problem)
        if '/governance/' in file_path or file_path.endswith('.yaml'):
            return {"score": cls.PROBLEM, "label": "GOVERNANCE_DRIFT", "is_problem": True}
            
        # Specs (Suboptimal)
        if '/specs/' in file_path:
            return {"score": cls.SUBOPTIMAL, "label": "SPEC_DETACHMENT", "is_problem": False}
            
        # Artifacts / Logs / Research dumps (Neutral)
        if '/archive/' in file_path or '/research/' in file_path or '/evals/' in file_path:
            return {"score": cls.NEUTRAL, "label": "DATA_POINT", "is_problem": False}
            
        # Default for unknown files
        if ext in ['.py', '.js', '.ts', '.html']:
            return {"score": cls.CRITICAL, "label": "CODE_STRUCTURAL_ORPHAN", "is_problem": True}
            
        return {"score": cls.ACCEPTABLE, "label": "STANDALONE_DOC", "is_problem": False}

    @classmethod
    def filter_true_orphans(cls, raw_orphans: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Filters a raw list of orphans into 'True Problems' vs 'Isolated Artifacts'."""
        classified = []
        for o in raw_orphans:
            analysis = cls.classify_severity(o['id'], o.get('type', 'file'), o['path'])
            classified.append({
                "id": o['id'],
                "path": o['path'],
                **analysis
            })
        return classified

def compute_igt_summary(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
    """Helper to compute overall IGT scores for a graph."""
    # This will be used in full_analysis.py
    pass

if __name__ == "__main__":
    # 1. Test Stability Calculator
    print("Testing StabilityCalculator...")
    for bf in [1, 4, 7, 10, 15, 25]:
        sigma = StabilityCalculator.calculate_stability(bf)
        print(f"  Bf: {bf:2} => σ: {sigma:.3f}")
    
    # 2. Test Orphan Classifier
    print("\nTesting OrphanClassifier...")
    test_orphans = [
        {"id": "atom_1", "type": "atom", "path": "src/core/logic.py"},
        {"id": "theory_doc", "type": "file", "path": "docs/theory/THEORY.md"},
        {"id": "research_dump", "type": "file", "path": "archive/research/old_data.json"},
        {"id": "standalone_py", "type": "file", "path": "scripts/tools.py"}
    ]
    classified = OrphanClassifier.filter_true_orphans(test_orphans)
    for c in classified:
        print(f"  ID: {c['id']:12} | Severity: {c['score']:.1} | Label: {c['label']}")
