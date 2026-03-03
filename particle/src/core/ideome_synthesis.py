"""
Ideome Synthesis -- The Rosetta Stone of Collider Macro Structures

The Ideome is a computed translation surface between Codome (what IS) and
Contextome (what is SAID).  It synthesizes the ideal reference frame from
three deterministic pillars:

    1. Constraint Pillar  -- CONSTRAINT_RULES + decomposition completeness
    2. Declaration Pillar -- contextome purpose_priors + symmetry seeds
    3. Decomposition Pillar -- gap_report gap density per node

This enables triangulated drift detection:
    drift_C  = |Ideome - Codome|      (code diverged from ideal)
    drift_X  = |Ideome - Contextome|  (docs diverged from ideal)
    delta_CX = |Codome - Contextome|  (code-docs divergence)

The Ideome is NOT a third file partition.  Axiom A1 (P = C ⊔ X) holds.
The Ideome lives in the analysis output, not on disk.

Theory: docs/essentials/AXIOMS_FORMAL.md (Axiom A1)
        particle/docs/THEORY_EXPANSION_2026.md section 14 (Ideome)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNKNOWN = 0.5          # Convention: missing data yields midpoint, not penalty
DRIFT_THRESHOLD = 0.15 # Below this, code and docs are considered aligned
BOTH_DRIFTED_FLOOR = 0.4  # Both scores below this = both_drifted
DOMAIN_PREFIX_DEPTH = 2    # Path components for domain grouping
WORST_NODES_LIMIT = 5      # Top-N most drifted nodes per domain


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class IdeomeNode:
    """Per-node ideal reference with drift vectors."""
    node_id: str
    role: str                        # from codome
    expected_role: Optional[str]     # from contextome declarations (if any)

    # Three pillars of the ideal
    constraint_score: float          # [0,1] How well node meets CONSTRAINT_RULES
    declaration_score: float         # [0,1] How well docs describe this node
    decomposition_score: float       # [0,1] Completeness from purpose decomposition

    # Drift vectors (all [0,1], lower = better alignment)
    alignment_C: float               # How well CODE matches the ideal
    alignment_X: float               # How well DOCS match the ideal
    delta_CX: float                  # Direct code<->docs divergence
    drift_direction: str             # classification string

    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "role": self.role,
            "expected_role": self.expected_role,
            "constraint_score": round(self.constraint_score, 4),
            "declaration_score": round(self.declaration_score, 4),
            "decomposition_score": round(self.decomposition_score, 4),
            "alignment_C": round(self.alignment_C, 4),
            "alignment_X": round(self.alignment_X, 4),
            "delta_CX": round(self.delta_CX, 4),
            "drift_direction": self.drift_direction,
            "details": self.details,
        }


@dataclass
class DomainAlignment:
    """Aggregated alignment for a domain (directory cluster)."""
    domain: str                  # path prefix or domain name
    node_count: int
    avg_alignment_C: float
    avg_alignment_X: float
    avg_delta_CX: float
    drift_direction: str         # majority vote
    worst_nodes: List[str]       # top-N most drifted node_ids

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "node_count": self.node_count,
            "avg_alignment_C": round(self.avg_alignment_C, 4),
            "avg_alignment_X": round(self.avg_alignment_X, 4),
            "avg_delta_CX": round(self.avg_delta_CX, 4),
            "drift_direction": self.drift_direction,
            "worst_nodes": self.worst_nodes,
        }


@dataclass
class IdeomeResult:
    """Complete Ideome synthesis output."""
    nodes: List[IdeomeNode]
    domains: List[DomainAlignment]
    global_coherence: float      # [0,1] overall alignment (1 = perfect)
    global_drift_C: float        # avg code drift
    global_drift_X: float        # avg docs drift
    global_delta_CX: float       # avg code<->docs divergence
    coverage: float              # fraction of nodes with ideome data
    node_count: int

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "domains": [d.to_dict() for d in self.domains],
            "global_coherence": round(self.global_coherence, 4),
            "global_drift_C": round(self.global_drift_C, 4),
            "global_drift_X": round(self.global_drift_X, 4),
            "global_delta_CX": round(self.global_delta_CX, 4),
            "coverage": round(self.coverage, 4),
            "node_count": self.node_count,
            "summary": {
                "by_drift_direction": _count_drift_directions(self.nodes),
                "domain_count": len(self.domains),
            },
        }


def _count_drift_directions(nodes: List[IdeomeNode]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for n in nodes:
        counts[n.drift_direction] = counts.get(n.drift_direction, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Pillar 1: Constraint Score
# ---------------------------------------------------------------------------

def _build_constraint_index(full_output: dict) -> Dict[str, float]:
    """Map node_id -> constraint score from purpose_decomposition results.

    Uses completeness from DecompositionResult.  Nodes that were decomposed
    get their actual completeness; others get UNKNOWN.
    """
    decomp_list = full_output.get("purpose_decomposition", [])
    index: Dict[str, float] = {}
    for dr in decomp_list:
        node_id = dr.get("node_id", "")
        completeness = dr.get("completeness")
        if node_id and completeness is not None:
            index[node_id] = max(0.0, min(1.0, completeness))
    return index


# ---------------------------------------------------------------------------
# Pillar 2: Declaration Score
# ---------------------------------------------------------------------------

def _build_declaration_index(full_output: dict) -> Dict[str, float]:
    """Map node_id -> declaration score from contextome purpose_priors.

    purpose_priors maps glob patterns to {purpose, confidence, source}.
    We match node paths against these patterns and use the confidence.
    """
    ctx = full_output.get("contextome", {})
    priors = ctx.get("purpose_priors", {})
    if not priors:
        return {}

    # Build a flat lookup: normalize patterns to simple path prefixes
    index: Dict[str, float] = {}
    nodes = full_output.get("nodes", [])
    node_by_id = {n.get("id", ""): n for n in nodes}

    for pattern, prior_data in priors.items():
        if not isinstance(prior_data, dict):
            continue
        confidence = prior_data.get("confidence", UNKNOWN)

        # Match pattern against node IDs/paths
        # Patterns are typically glob-like (e.g., "src/services/*")
        # We do prefix matching against node ids
        prefix = pattern.rstrip("*").rstrip("/")
        for node_id, node in node_by_id.items():
            if not node_id:
                continue
            # Match: node_id starts with the pattern prefix
            if node_id.startswith(prefix) or prefix in node_id:
                # Check purpose match
                node_role = node.get("role", "").lower()
                prior_purpose = prior_data.get("purpose", "").lower()
                if prior_purpose and node_role:
                    if prior_purpose in node_role or node_role in prior_purpose:
                        # Matching purpose: use full confidence
                        index[node_id] = max(
                            index.get(node_id, 0.0),
                            max(0.0, min(1.0, confidence)),
                        )
                    else:
                        # Mismatching purpose: low score (declared but wrong)
                        index.setdefault(node_id, 0.2)
                else:
                    # Purpose data exists but no role to compare
                    index[node_id] = max(
                        index.get(node_id, 0.0),
                        max(0.0, min(1.0, confidence)),
                    )

    return index


# ---------------------------------------------------------------------------
# Pillar 3: Decomposition Score (from gap_report)
# ---------------------------------------------------------------------------

def _build_decomposition_index(full_output: dict) -> Dict[str, float]:
    """Map node_id -> decomposition score from gap_report gaps.

    Score = 1.0 - (gaps_for_node / max_expected) where max_expected is a
    reasonable upper bound on gaps per node.
    """
    gap_report = full_output.get("gap_report", {})
    gaps = gap_report.get("gaps", [])
    if not gaps:
        return {}

    # Count gaps per node location
    gap_counts: Dict[str, int] = {}
    for g in gaps:
        loc = g.get("location", "")
        if loc:
            gap_counts[loc] = gap_counts.get(loc, 0) + 1

    if not gap_counts:
        return {}

    # max_expected: use observed maximum * 1.5, floor of 3
    max_gaps = max(gap_counts.values())
    max_expected = max(max_gaps * 1.5, 3.0)

    index: Dict[str, float] = {}
    for node_id, count in gap_counts.items():
        score = 1.0 - min(count / max_expected, 1.0)
        index[node_id] = round(score, 4)

    return index


# ---------------------------------------------------------------------------
# Drift Direction Classification
# ---------------------------------------------------------------------------

def classify_drift(alignment_C: float, alignment_X: float) -> str:
    """Classify drift direction from alignment scores.

    Args:
        alignment_C: code alignment score [0, 1] (1 = perfect)
        alignment_X: docs alignment score [0, 1] (1 = perfect)

    Returns:
        One of: "aligned", "code_drifted", "docs_drifted",
                "both_drifted", "unknown"
    """
    delta = abs(alignment_C - alignment_X)

    # Both very poor -> both drifted (regardless of direction)
    if alignment_C < BOTH_DRIFTED_FLOOR and alignment_X < BOTH_DRIFTED_FLOOR:
        return "both_drifted"

    # Scores close enough -> aligned
    if delta <= DRIFT_THRESHOLD:
        return "aligned"

    # Clear directional drift (at least one score is decent)
    if alignment_C < alignment_X - DRIFT_THRESHOLD:
        return "code_drifted"
    if alignment_X < alignment_C - DRIFT_THRESHOLD:
        return "docs_drifted"

    return "unknown"


# ---------------------------------------------------------------------------
# Per-Node Synthesis
# ---------------------------------------------------------------------------

def _synthesize_node(
    node: dict,
    constraint_index: Dict[str, float],
    declaration_index: Dict[str, float],
    decomposition_index: Dict[str, float],
) -> IdeomeNode:
    """Synthesize an IdeomeNode for a single codome node."""
    node_id = node.get("id", "")
    role = node.get("role", "Unknown")

    # Pillar 1: Constraint
    constraint_score = constraint_index.get(node_id, UNKNOWN)

    # Pillar 2: Declaration
    declaration_score = declaration_index.get(node_id, UNKNOWN)

    # Pillar 3: Decomposition
    decomposition_score = decomposition_index.get(node_id, UNKNOWN)

    # Ideal score: equal-weight average of three pillars
    ideal = (constraint_score + declaration_score + decomposition_score) / 3.0

    # Drift vectors
    alignment_C = ideal            # code alignment = how well it meets the ideal
    alignment_X = declaration_score  # docs alignment = doc coverage of this node
    delta_CX = abs(alignment_C - alignment_X)

    # Direction
    drift_direction = classify_drift(alignment_C, alignment_X)

    # Expected role from contextome (if declaration index had a match)
    expected_role = None
    if node_id in declaration_index and declaration_index[node_id] != UNKNOWN:
        expected_role = role  # confirmed by docs

    details = {
        "constraint_source": (
            "decomposition" if node_id in constraint_index else "unknown"
        ),
        "declaration_source": (
            "contextome" if node_id in declaration_index else "unknown"
        ),
        "decomposition_source": (
            "gap_report" if node_id in decomposition_index else "unknown"
        ),
        "ideal_score": round(ideal, 4),
    }

    return IdeomeNode(
        node_id=node_id,
        role=role,
        expected_role=expected_role,
        constraint_score=constraint_score,
        declaration_score=declaration_score,
        decomposition_score=decomposition_score,
        alignment_C=alignment_C,
        alignment_X=alignment_X,
        delta_CX=delta_CX,
        drift_direction=drift_direction,
        details=details,
    )


# ---------------------------------------------------------------------------
# Domain Rollup
# ---------------------------------------------------------------------------

def _extract_domain(node_id: str) -> str:
    """Extract domain from node_id using first N path components."""
    parts = node_id.replace("\\", "/").split("/")
    # Use first DOMAIN_PREFIX_DEPTH components as domain
    if len(parts) >= DOMAIN_PREFIX_DEPTH:
        return "/".join(parts[:DOMAIN_PREFIX_DEPTH])
    return parts[0] if parts else "root"


def _rollup_domains(nodes: List[IdeomeNode]) -> List[DomainAlignment]:
    """Group nodes by domain and compute aggregate alignment."""
    if not nodes:
        return []

    # Group by domain
    domain_nodes: Dict[str, List[IdeomeNode]] = {}
    for n in nodes:
        domain = _extract_domain(n.node_id)
        domain_nodes.setdefault(domain, []).append(n)

    domains: List[DomainAlignment] = []
    for domain, dnodes in sorted(domain_nodes.items()):
        if not dnodes:
            continue

        count = len(dnodes)
        avg_C = sum(n.alignment_C for n in dnodes) / count
        avg_X = sum(n.alignment_X for n in dnodes) / count
        avg_delta = sum(n.delta_CX for n in dnodes) / count

        # Majority vote on drift direction
        direction_counts: Dict[str, int] = {}
        for n in dnodes:
            direction_counts[n.drift_direction] = (
                direction_counts.get(n.drift_direction, 0) + 1
            )
        majority_direction = max(direction_counts, key=direction_counts.get)

        # Worst nodes by delta_CX
        sorted_by_delta = sorted(dnodes, key=lambda n: n.delta_CX, reverse=True)
        worst = [n.node_id for n in sorted_by_delta[:WORST_NODES_LIMIT]]

        domains.append(DomainAlignment(
            domain=domain,
            node_count=count,
            avg_alignment_C=avg_C,
            avg_alignment_X=avg_X,
            avg_delta_CX=avg_delta,
            drift_direction=majority_direction,
            worst_nodes=worst,
        ))

    # Sort domains by avg_delta_CX descending (worst first)
    domains.sort(key=lambda d: d.avg_delta_CX, reverse=True)
    return domains


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def synthesize_ideome(full_output: dict) -> IdeomeResult:
    """Synthesize the Ideome -- the ideal reference frame for drift detection.

    Combines three deterministic pillars:
    1. Constraint (from CONSTRAINT_RULES + decomposition completeness)
    2. Declaration (from contextome purpose_priors)
    3. Decomposition (from gap_report gap density)

    Produces per-node alignment scores and drift direction, then rolls up
    to domain-level aggregates.

    Args:
        full_output: The unified analysis dict from Collider.

    Returns:
        IdeomeResult with per-node and per-domain alignment data.
    """
    nodes = full_output.get("nodes", [])
    if not nodes:
        return IdeomeResult(
            nodes=[],
            domains=[],
            global_coherence=UNKNOWN,
            global_drift_C=UNKNOWN,
            global_drift_X=UNKNOWN,
            global_delta_CX=0.0,
            coverage=0.0,
            node_count=0,
        )

    # Build pillar indexes
    constraint_index = _build_constraint_index(full_output)
    declaration_index = _build_declaration_index(full_output)
    decomposition_index = _build_decomposition_index(full_output)

    # Synthesize per-node
    ideome_nodes: List[IdeomeNode] = []
    for node in nodes:
        node_id = node.get("id", "")
        if not node_id:
            continue
        ideome_nodes.append(_synthesize_node(
            node, constraint_index, declaration_index, decomposition_index,
        ))

    # Domain rollup
    domains = _rollup_domains(ideome_nodes)

    # Global metrics
    total = len(ideome_nodes)
    if total > 0:
        global_C = sum(n.alignment_C for n in ideome_nodes) / total
        global_X = sum(n.alignment_X for n in ideome_nodes) / total
        global_delta = sum(n.delta_CX for n in ideome_nodes) / total
        # Coherence = 1 - avg_delta_CX (high coherence = low divergence)
        global_coherence = max(0.0, min(1.0, 1.0 - global_delta))
    else:
        global_C = UNKNOWN
        global_X = UNKNOWN
        global_delta = 0.0
        global_coherence = UNKNOWN

    # Coverage: fraction of nodes with at least one non-UNKNOWN pillar
    nodes_with_data = sum(
        1 for n in ideome_nodes
        if (n.constraint_score != UNKNOWN
            or n.declaration_score != UNKNOWN
            or n.decomposition_score != UNKNOWN)
    )
    coverage = nodes_with_data / max(total, 1)

    return IdeomeResult(
        nodes=ideome_nodes,
        domains=domains,
        global_coherence=global_coherence,
        global_drift_C=global_C,
        global_drift_X=global_X,
        global_delta_CX=global_delta,
        coverage=coverage,
        node_count=total,
    )
