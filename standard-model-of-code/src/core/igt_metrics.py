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

def compute_igt_summary(nodes: List[Dict], edges: List[Dict], files: List[Dict] = None) -> Dict[str, Any]:
    """Computes overall Information Graph Theory (IGT) status for the graph.
    
    This function consolidates directory stability and orphan severity into a 
    single structural health report.
    """
    from collections import defaultdict
    
    # 1. Directory Stability Analysis
    dir_structure = defaultdict(list)
    file_list = files or []
    
    # If no explicit files list, try to find file-type nodes
    if not file_list:
        file_list = [n for n in nodes if n.get('type') == 'file' or n.get('kind') == 'file']
        
    for f in file_list:
        p = f.get('file') or f.get('file_path') or f.get('path')
        if not p: continue
        
        path_obj = os.path.normpath(p)
        parent = os.path.dirname(path_obj) or "."
        name = os.path.basename(path_obj)
        dir_structure[parent].append(name)
        
    stability_report = StabilityCalculator.analyze_directories(dir_structure)
    
    # 2. Orphan Severity Analysis
    # We assume 'orphans' identification happens externally (e.g. via ExecutionFlow)
    # but here we can identify nodes with 0 in-degree.
    node_ids = {n.get('id') for n in nodes if n.get('id')}
    targets = {e.get('target') for e in edges if e.get('target')}
    orphan_ids = node_ids - targets
    
    orphans_data = []
    for o_id in orphan_ids:
        o_node = next((n for n in nodes if n.get('id') == o_id), None)
        if o_node:
            orphans_data.append({
                'id': o_id,
                'type': o_node.get('type') or o_node.get('kind', 'file'),
                'path': o_node.get('file_path') or o_node.get('path', '')
            })
            
    classified_orphans = OrphanClassifier.filter_true_orphans(orphans_data)
    
    # 3. Aggregate Metrics
    avg_stability = sum(s['stability_index'] for s in stability_report.values()) / len(stability_report) if stability_report else 1.0
    critical_orphans = [o for o in classified_orphans if o['is_problem']]
    
    return {
        "directory_stability": stability_report,
        "classified_orphans": classified_orphans,
        "metrics": {
            "avg_stability": round(avg_stability, 3),
            "critical_orphan_count": len(critical_orphans),
            "total_orphan_count": len(classified_orphans),
            "igt_health": round(avg_stability * (1.0 - (len(critical_orphans) / max(1, len(nodes)) * 10)), 3) # Heuristic health
        }
    }

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
