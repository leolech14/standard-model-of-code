"""
Purpose Intelligence (Q-Scores)

Computes quality scores measuring how well code serves the holon at each level.
This is the quantitative measurement of purpose fulfillment.

Formula: Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)

Where I(H) = intrinsic quality from 6 metrics:
- Q_alignment:    Rule adherence (violations penalty)
- Q_coherence:    Focus via entropy of atom categories
- Q_density:      Signal-to-noise ratio
- Q_completeness: Expected children present
- Q_simplicity:   1 / log(complexity)
- Q_purity:       Behavior matches classified dimensions

Reference: docs/PURPOSE_INTELLIGENCE.md
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import math


# =============================================================================
# WEIGHTS (tunable)
# =============================================================================

# Holon propagation weights
W_PARTS = 0.5       # Weight for child quality
W_INTRINSIC = 0.5   # Weight for intrinsic quality

# Intrinsic quality metric weights (must sum to 1.0)
METRIC_WEIGHTS = {
    'alignment': 0.20,
    'coherence': 0.20,
    'density': 0.15,
    'completeness': 0.15,
    'simplicity': 0.15,
    'purity': 0.15,
}

# Violation severity weights
VIOLATION_WEIGHTS = {
    'antimatter': 0.5,   # Tier A - severe
    'policy': 0.2,       # Tier B - moderate
    'signal': 0.05,      # Tier C - minor
}

# Signal atom categories (high purpose value)
SIGNAL_ATOMS = {
    'LOG.FNC.Method', 'LOG.FNC.Function', 'LOG.FNC.Lambda',
    'LOG.CTL.Conditional', 'LOG.CTL.Loop', 'LOG.CTL.Return',
    'LOG.OPS.BinaryExpr', 'LOG.OPS.UnaryExpr', 'LOG.OPS.Call',
    'ORG.AGG.Class', 'ORG.AGG.Module',
    'DAT.ENT.Entity', 'DAT.ENT.ValueObject',
}

# Noise atom categories (low purpose value)
NOISE_ATOMS = {
    'DAT.VAR.Comment', 'DAT.VAR.Docstring',
    'ORG.STR.Import', 'ORG.STR.Pass',
    'DAT.TYP.TypeAnnotation',
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PurposeIntelligence:
    """Q-scores for a single holon."""
    Q_total: float = 0.0
    Q_alignment: float = 1.0
    Q_coherence: float = 1.0
    Q_density: float = 1.0
    Q_completeness: float = 1.0
    Q_simplicity: float = 1.0
    Q_purity: float = 1.0
    Q_intrinsic: float = 1.0

    # Debug info
    violations_count: int = 0
    children_count: int = 0
    avg_children_q: float = 0.0

    def to_dict(self) -> Dict:
        return {
            'Q_total': round(self.Q_total, 3),
            'Q_alignment': round(self.Q_alignment, 3),
            'Q_coherence': round(self.Q_coherence, 3),
            'Q_density': round(self.Q_density, 3),
            'Q_completeness': round(self.Q_completeness, 3),
            'Q_simplicity': round(self.Q_simplicity, 3),
            'Q_purity': round(self.Q_purity, 3),
            'Q_intrinsic': round(self.Q_intrinsic, 3),
        }


# =============================================================================
# METRIC COMPUTATIONS
# =============================================================================

def compute_Q_alignment(node: Dict, violations: List[Dict] = None) -> float:
    """
    Q_alignment: Rule adherence score.

    Formula: 1 - Σ(weight × violation_count)

    Consumes: violations from constraint_engine.py
    """
    if not violations:
        violations = node.get('violations', [])

    if not violations:
        return 1.0

    # Count violations by tier
    tier_counts = Counter(v.get('tier', 'signal') for v in violations)

    # Calculate penalty
    penalty = 0.0
    for tier, count in tier_counts.items():
        weight = VIOLATION_WEIGHTS.get(tier, 0.05)
        penalty += weight * count

    # Cap at 0
    return max(0.0, 1.0 - penalty)


def compute_Q_coherence(node: Dict, children: List[Dict] = None) -> float:
    """
    Q_coherence: Focus via entropy of atom categories.

    Low entropy = focused (good)
    High entropy = scattered (bad, god class)

    Formula: 1 / (1 + normalized_entropy)
    """
    # Get atom categories from node or children
    categories = []

    if children:
        for child in children:
            cat = child.get('atom_family') or child.get('category')
            if cat:
                categories.append(cat)
    else:
        # Single node - check its internal composition
        cat = node.get('atom_family') or node.get('category')
        if cat:
            categories.append(cat)

    if not categories:
        return 1.0  # No data = assume coherent

    # Calculate Shannon entropy
    counts = Counter(categories)
    total = len(categories)

    if total <= 1:
        return 1.0  # Single item = perfectly coherent

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize by max possible entropy (log2 of unique categories)
    max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    # Convert to score (inverse relationship)
    return 1.0 / (1.0 + normalized_entropy)


def compute_Q_density(node: Dict) -> float:
    """
    Q_density: Signal-to-noise ratio.

    High signal atoms / total atoms

    Consumes: atom classification, lines_of_code
    """
    atom = node.get('atom', '')

    # Check if this is a signal atom
    if atom in SIGNAL_ATOMS:
        base_density = 1.0
    elif atom in NOISE_ATOMS:
        base_density = 0.2
    else:
        base_density = 0.6  # Neutral

    # Factor in complexity vs size ratio
    complexity = node.get('complexity', 1)
    loc = node.get('lines_of_code', node.get('end_line', 1) - node.get('start_line', 0) + 1)

    if loc > 0:
        # Complexity density: lower is better (less complexity per line)
        complexity_density = complexity / loc
        # Invert: high complexity density = low Q_density
        complexity_factor = 1.0 / (1.0 + complexity_density)
    else:
        complexity_factor = 1.0

    return (base_density + complexity_factor) / 2


def compute_Q_completeness(node: Dict, children: List[Dict] = None, edges: List[Dict] = None) -> float:
    """
    Q_completeness: Expected children present.

    Orphans = 0
    Missing expected methods = reduced score

    Consumes: topology_role, edges, role expectations
    """
    # Orphans are incomplete by definition
    topology = node.get('topology_role', '')
    if topology == 'orphan':
        # Check disconnection reason
        disconnection = node.get('disconnection', {})
        source = disconnection.get('reachability_source', 'unreachable')
        if source == 'unreachable':
            return 0.0  # True dead code
        elif source in ('test_entry', 'entry_point', 'framework_managed'):
            return 0.9  # Known external caller
        else:
            return 0.5  # Uncertain

    # Check role-based expectations
    role = node.get('role', '')
    kind = node.get('kind', '')

    if kind == 'class' and children:
        # Classes should have methods
        method_count = sum(1 for c in children if c.get('kind') == 'function')

        # Role-specific expectations
        expected = {
            'Repository': 2,   # save, find minimum
            'Service': 1,      # at least one method
            'Controller': 1,   # at least one handler
            'Factory': 1,      # create method
            'Builder': 2,      # build + setters
        }.get(role, 1)

        if method_count >= expected:
            return 1.0
        elif method_count > 0:
            return method_count / expected
        else:
            return 0.3  # Empty class

    # Default: complete
    return 1.0


def compute_Q_simplicity(node: Dict) -> float:
    """
    Q_simplicity: Inverse of complexity.

    Formula: 1 / (1 + log(1 + complexity))

    Consumes: complexity field
    """
    complexity = node.get('complexity', 1)

    if complexity <= 1:
        return 1.0

    # Logarithmic scaling - complexity 10 should still be decent
    return 1.0 / (1.0 + math.log(1 + complexity))


def compute_Q_purity(node: Dict) -> float:
    """
    Q_purity: Behavior matches classified dimensions.

    If D6_EFFECT is Pure but node has I/O calls → low purity
    If role is Repository but has UI calls → low purity

    Consumes: dimensions, edge analysis
    """
    effect = node.get('effect', node.get('D6_EFFECT', ''))
    boundary = node.get('boundary', node.get('D4_BOUNDARY', ''))
    role = node.get('role', '')

    purity = 1.0

    # Check effect vs actual behavior
    if effect == 'Pure':
        # Pure functions shouldn't have I/O indicators
        has_io = node.get('has_io', False)
        external_calls = node.get('external_calls', 0)
        if has_io or external_calls > 0:
            purity -= 0.4  # Significant penalty

    # Check boundary consistency
    if boundary == 'Internal':
        # Internal nodes shouldn't cross system boundaries
        crosses_boundary = node.get('crosses_boundary', False)
        if crosses_boundary:
            purity -= 0.3

    # Check role consistency
    if role in ('Repository', 'Store', 'Cache'):
        # Data layer shouldn't have UI dependencies
        has_ui_deps = node.get('has_ui_deps', False)
        if has_ui_deps:
            purity -= 0.3

    return max(0.0, purity)


# =============================================================================
# INTRINSIC QUALITY
# =============================================================================

def compute_intrinsic_quality(node: Dict, children: List[Dict] = None) -> PurposeIntelligence:
    """
    Compute I(H) - the intrinsic quality of a holon.

    I(H) = weighted average of 6 metrics
    """
    pi = PurposeIntelligence()

    # Compute each metric
    pi.Q_alignment = compute_Q_alignment(node)
    pi.Q_coherence = compute_Q_coherence(node, children)
    pi.Q_density = compute_Q_density(node)
    pi.Q_completeness = compute_Q_completeness(node, children)
    pi.Q_simplicity = compute_Q_simplicity(node)
    pi.Q_purity = compute_Q_purity(node)

    # Weighted combination
    pi.Q_intrinsic = (
        METRIC_WEIGHTS['alignment'] * pi.Q_alignment +
        METRIC_WEIGHTS['coherence'] * pi.Q_coherence +
        METRIC_WEIGHTS['density'] * pi.Q_density +
        METRIC_WEIGHTS['completeness'] * pi.Q_completeness +
        METRIC_WEIGHTS['simplicity'] * pi.Q_simplicity +
        METRIC_WEIGHTS['purity'] * pi.Q_purity
    )

    pi.violations_count = len(node.get('violations', []))
    pi.children_count = len(children) if children else 0

    return pi


# =============================================================================
# HOLON PROPAGATION
# =============================================================================

def propagate_quality(node: Dict, children_q: List[float], intrinsic: PurposeIntelligence) -> float:
    """
    Q(H) = w_parts × Avg(Q_children) + w_intrinsic × I(H)

    This is the core holon formula - quality of the whole depends on
    both the quality of its parts AND its own structural quality.
    """
    if children_q:
        avg_children = sum(children_q) / len(children_q)
    else:
        avg_children = 1.0  # No children = assume they're fine

    intrinsic.avg_children_q = avg_children

    q_total = W_PARTS * avg_children + W_INTRINSIC * intrinsic.Q_intrinsic
    return q_total


# =============================================================================
# MAIN COMPUTATION
# =============================================================================

def compute_purpose_intelligence(
    node: Dict,
    children: List[Dict] = None,
    children_q_scores: List[float] = None,
) -> PurposeIntelligence:
    """
    Compute full Purpose Intelligence for a node.

    Args:
        node: The node dictionary with all metadata
        children: List of child nodes (for containers)
        children_q_scores: Pre-computed Q_total scores of children

    Returns:
        PurposeIntelligence with all Q-scores
    """
    # Compute intrinsic quality
    pi = compute_intrinsic_quality(node, children)

    # Apply holon propagation formula
    pi.Q_total = propagate_quality(node, children_q_scores or [], pi)

    return pi


def compute_codebase_intelligence(nodes: List[Dict], edges: List[Dict] = None) -> Dict:
    """
    Compute Purpose Intelligence for an entire codebase.

    Process bottom-up: leaves first, then propagate up.

    Returns:
        Dict with per-node Q-scores and codebase summary
    """
    # Build parent-child relationships
    children_by_parent = {}
    for node in nodes:
        name = node.get('name', '')
        if '.' in name:
            parent = name.rsplit('.', 1)[0]
            if parent not in children_by_parent:
                children_by_parent[parent] = []
            children_by_parent[parent].append(node)

    # Index nodes by name
    nodes_by_name = {n.get('name', ''): n for n in nodes}

    # Process in dependency order (leaves first)
    # For simplicity, process all leaf nodes first, then containers

    q_scores = {}  # name -> Q_total
    pi_results = {}  # name -> PurposeIntelligence

    # Pass 1: Leaf nodes (no children)
    for node in nodes:
        name = node.get('name', '')
        if name not in children_by_parent:
            pi = compute_purpose_intelligence(node)
            q_scores[name] = pi.Q_total
            pi_results[name] = pi

    # Pass 2: Container nodes (have children)
    for node in nodes:
        name = node.get('name', '')
        if name in children_by_parent:
            children = children_by_parent[name]
            children_q = [q_scores.get(c.get('name', ''), 0.5) for c in children]
            pi = compute_purpose_intelligence(node, children, children_q)
            q_scores[name] = pi.Q_total
            pi_results[name] = pi

    # Compute codebase summary
    all_q = list(q_scores.values())
    if all_q:
        avg_q = sum(all_q) / len(all_q)
        min_q = min(all_q)
        max_q = max(all_q)
    else:
        avg_q = min_q = max_q = 0.0

    # Quality distribution
    excellent = sum(1 for q in all_q if q >= 0.85)
    good = sum(1 for q in all_q if 0.70 <= q < 0.85)
    moderate = sum(1 for q in all_q if 0.50 <= q < 0.70)
    poor = sum(1 for q in all_q if q < 0.50)

    return {
        'per_node': {name: pi.to_dict() for name, pi in pi_results.items()},
        'summary': {
            'codebase_intelligence': round(avg_q, 3),
            'min_q': round(min_q, 3),
            'max_q': round(max_q, 3),
            'distribution': {
                'excellent': excellent,
                'good': good,
                'moderate': moderate,
                'poor': poor,
            },
            'interpretation': (
                'Sharp' if avg_q >= 0.85 else
                'Good' if avg_q >= 0.70 else
                'Muddy' if avg_q >= 0.50 else
                'Poor'
            ),
        }
    }


# =============================================================================
# PIPELINE INTEGRATION
# =============================================================================

def enrich_nodes_with_intelligence(nodes: List[Dict], edges: List[Dict] = None) -> Tuple[List[Dict], Dict]:
    """
    Add purpose_intelligence fields to nodes.

    Call this as Stage 8.6 in full_analysis.py pipeline.

    Returns:
        (enriched_nodes, codebase_summary)
    """
    result = compute_codebase_intelligence(nodes, edges)

    # Enrich each node
    for node in nodes:
        name = node.get('name', '')
        if name in result['per_node']:
            node['purpose_intelligence'] = result['per_node'][name]

    return nodes, result['summary']


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    # Test with sample nodes
    test_nodes = [
        {
            'name': 'UserRepository',
            'kind': 'class',
            'role': 'Repository',
            'complexity': 5,
            'violations': [],
            'topology_role': 'internal',
        },
        {
            'name': 'UserRepository.save',
            'kind': 'function',
            'role': 'Command',
            'complexity': 3,
            'violations': [{'tier': 'policy', 'rule_id': 'B001'}],
            'atom_family': 'LOG',
            'effect': 'Write',
        },
        {
            'name': 'UserRepository.find',
            'kind': 'function',
            'role': 'Query',
            'complexity': 2,
            'violations': [],
            'atom_family': 'LOG',
            'effect': 'Read',
        },
    ]

    nodes, summary = enrich_nodes_with_intelligence(test_nodes)

    print("=== PURPOSE INTELLIGENCE TEST ===\n")
    print(f"Codebase Intelligence: {summary['codebase_intelligence']}")
    print(f"Interpretation: {summary['interpretation']}")
    print(f"Distribution: {summary['distribution']}")
    print()

    for node in nodes:
        pi = node.get('purpose_intelligence', {})
        print(f"{node['name']}:")
        print(f"  Q_total: {pi.get('Q_total', 'N/A')}")
        print(f"  Q_alignment: {pi.get('Q_alignment')}")
        print(f"  Q_coherence: {pi.get('Q_coherence')}")
        print()
