"""
Gap Detection -- Module 3 of the Collider Trinity

Compares what SHOULD exist (from Purpose Decomposition) against what DOES
exist (from Collider analysis).  Maps unknown unknowns.  For well-circumscribed
gaps, prepares LLM query targets (but does NOT execute them -- Phase 2).

Theory: docs/essentials/LAGRANGIAN.md (I_telic term)
        particle/docs/THEORY_EXPANSION_2026.md section 13 (Disconnection Taxonomy)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from purpose_decomposition import DecompositionResult


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Gap:
    """A single detected gap in the codebase architecture."""
    location: str           # node_id or path where gap was found
    gap_type: str           # see GAP_TYPES below
    description: str        # human-readable
    severity: str           # "critical" | "high" | "medium" | "low"
    circumscribed: bool     # True if well-defined enough for LLM query
    llm_query_hint: str     # suggested semantic query for LLM analysis
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


GAP_TYPES = {
    "missing_required",     # from decomposition: required sub-compartment absent
    "missing_expected",     # from decomposition: expected sub-compartment absent
    "forbidden_present",    # from decomposition: forbidden sub-compartment present
    "orphan_cluster",       # group of nodes with no parent purpose
    "purpose_vacuum",       # container exists but no coherent sub-purpose pattern
    "disconnection",        # nodes unreachable, no incoming, no outgoing
}

# Severity assignment for gap types
_TYPE_SEVERITY = {
    "missing_required": "critical",
    "forbidden_present": "high",
    "missing_expected": "medium",
    "purpose_vacuum": "medium",
    "orphan_cluster": "medium",
    "disconnection": "low",
}


@dataclass
class GapReport:
    """Full gap detection report."""
    gaps: List[Gap]
    coverage: float          # % of expected compartments that exist
    unknown_count: int       # number of well-circumscribed unknowns
    query_targets: List[dict]  # ready-to-use LLM query specs

    def to_dict(self) -> dict:
        return {
            "gaps": [g.to_dict() for g in self.gaps],
            "coverage": self.coverage,
            "unknown_count": self.unknown_count,
            "query_targets": self.query_targets,
            "summary": {
                "total_gaps": len(self.gaps),
                "by_type": _count_by_type(self.gaps),
                "by_severity": _count_by_severity(self.gaps),
            },
        }


def _count_by_type(gaps: List[Gap]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for g in gaps:
        counts[g.gap_type] = counts.get(g.gap_type, 0) + 1
    return counts


def _count_by_severity(gaps: List[Gap]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for g in gaps:
        counts[g.severity] = counts.get(g.severity, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Gap detection from decomposition results
# ---------------------------------------------------------------------------

def _gaps_from_decomposition(
    decomposition_results: List[DecompositionResult],
) -> List[Gap]:
    """Extract gaps from purpose decomposition results.

    Three sub-types:
    - missing_required: required sub-purpose absent (critical)
    - missing_expected: expected sub-purpose absent (medium)
    - forbidden_present: forbidden sub-purpose present (high)
    """
    gaps: List[Gap] = []

    for dr in decomposition_results:
        node_path = dr.node_id

        # Missing required sub-compartments
        for missing in dr.missing:
            gaps.append(Gap(
                location=node_path,
                gap_type="missing_required",
                description=(
                    f"{dr.purpose} '{node_path}' is missing required "
                    f"sub-purpose '{missing}'"
                ),
                severity="critical",
                circumscribed=True,
                llm_query_hint=(
                    f"Does '{node_path}' contain {missing.lower()} logic "
                    f"that isn't classified as a '{missing}' sub-purpose? "
                    f"Look for hidden or inlined {missing.lower()} behavior."
                ),
                context={
                    "parent_purpose": dr.purpose,
                    "expected_sub_purpose": missing,
                    "completeness": dr.completeness,
                    "compartment": dr.compartment,
                },
            ))

        # Missing expected sub-compartments
        for gap_name in dr.gaps:
            gaps.append(Gap(
                location=node_path,
                gap_type="missing_expected",
                description=(
                    f"{dr.purpose} '{node_path}' is missing expected "
                    f"sub-purpose '{gap_name}'"
                ),
                severity="medium",
                circumscribed=True,
                llm_query_hint=(
                    f"Should '{node_path}' ({dr.purpose}) include "
                    f"{gap_name.lower()} functionality? Is there a design "
                    f"reason for its absence?"
                ),
                context={
                    "parent_purpose": dr.purpose,
                    "expected_sub_purpose": gap_name,
                    "completeness": dr.completeness,
                },
            ))

        # Forbidden sub-compartments present
        for violation in dr.violations:
            gaps.append(Gap(
                location=node_path,
                gap_type="forbidden_present",
                description=(
                    f"{dr.purpose} '{node_path}' contains forbidden "
                    f"sub-purpose '{violation}'"
                ),
                severity="high",
                circumscribed=True,
                llm_query_hint=(
                    f"Why does '{node_path}' ({dr.purpose}) contain "
                    f"{violation.lower()} logic? This violates architectural "
                    f"constraints. Should it be extracted or moved?"
                ),
                context={
                    "parent_purpose": dr.purpose,
                    "forbidden_sub_purpose": violation,
                },
            ))

    return gaps


# ---------------------------------------------------------------------------
# Disconnection detection from graph
# ---------------------------------------------------------------------------

def _detect_disconnections(full_output: dict) -> List[Gap]:
    """Find truly isolated nodes -- no incoming AND no outgoing edges.

    These are nodes that exist in the codebase but participate in no
    dependency relationships at all. They represent potential dead code
    or miscategorized components.
    """
    nodes = full_output.get("nodes", [])
    edges = full_output.get("edges", [])

    if not nodes or not edges:
        return []

    # Build adjacency sets
    sources = set()
    targets = set()
    for e in edges:
        sources.add(e.get("source", ""))
        targets.add(e.get("target", ""))

    node_ids = {n.get("id", "") for n in nodes}
    node_by_id = {n.get("id", ""): n for n in nodes}

    # Truly isolated = no incoming AND no outgoing
    isolated = node_ids - (sources | targets)

    gaps: List[Gap] = []
    for nid in sorted(isolated):
        if not nid:
            continue
        node = node_by_id.get(nid, {})
        role = node.get("role", "Unknown")
        kind = node.get("kind", "")

        gaps.append(Gap(
            location=nid,
            gap_type="disconnection",
            description=(
                f"Node '{nid}' ({role}) has no incoming or outgoing "
                f"edges -- completely disconnected from the dependency graph"
            ),
            severity="low",
            circumscribed=True,
            llm_query_hint=(
                f"Is '{nid}' ({role}) truly unused, or is it invoked "
                f"through a mechanism not captured by static analysis "
                f"(reflection, dynamic import, plugin system)?"
            ),
            context={
                "role": role,
                "kind": kind,
                "compartment": node.get("compartment", ""),
            },
        ))

    return gaps


# ---------------------------------------------------------------------------
# Orphan cluster detection
# ---------------------------------------------------------------------------

def _detect_orphan_clusters(full_output: dict) -> List[Gap]:
    """Find clusters of nodes with no parent that share a purpose vacuum.

    An orphan cluster is a group of top-level nodes (no parent field)
    that are co-located (same compartment) but have no container node
    organizing them. This indicates a missing architectural abstraction.
    """
    nodes = full_output.get("nodes", [])
    if not nodes:
        return []

    # Find top-level nodes (no parent)
    orphans_by_compartment: Dict[str, List[dict]] = {}
    for n in nodes:
        parent = n.get("parent", "")
        if not parent:
            comp = n.get("compartment", "unknown")
            orphans_by_compartment.setdefault(comp, []).append(n)

    gaps: List[Gap] = []
    for comp, orphan_nodes in sorted(orphans_by_compartment.items()):
        # Only flag clusters of 5+ orphans as meaningful
        if len(orphan_nodes) < 5:
            continue

        # Check role diversity -- if they're all the same role, less concerning
        roles = {n.get("role", "Unknown") for n in orphan_nodes}

        gaps.append(Gap(
            location=comp,
            gap_type="orphan_cluster",
            description=(
                f"Compartment '{comp}' has {len(orphan_nodes)} top-level "
                f"nodes with no parent container. Roles: {', '.join(sorted(roles)[:5])}"
            ),
            severity="medium",
            circumscribed=len(orphan_nodes) <= 50,
            llm_query_hint=(
                f"The '{comp}' compartment has {len(orphan_nodes)} "
                f"unorganized nodes. What higher-level abstraction could "
                f"group these into a coherent container hierarchy?"
            ),
            context={
                "compartment": comp,
                "orphan_count": len(orphan_nodes),
                "roles": sorted(roles),
                "sample_ids": [n.get("id", "") for n in orphan_nodes[:10]],
            },
        ))

    return gaps


# ---------------------------------------------------------------------------
# Purpose vacuum detection
# ---------------------------------------------------------------------------

def _detect_purpose_vacuums(full_output: dict) -> List[Gap]:
    """Find container nodes with children but no coherent purpose pattern.

    A purpose vacuum is a node that has children (it's a container) but
    its children's purposes are so scattered that no dominant sub-purpose
    pattern emerges. This indicates the container is doing too many things
    or has unclear responsibility.
    """
    nodes = full_output.get("nodes", [])
    if not nodes:
        return []

    # Build parent -> children map
    children_of: Dict[str, List[dict]] = {}
    for n in nodes:
        parent = n.get("parent", "")
        if parent:
            children_of.setdefault(parent, []).append(n)

    node_by_id = {n.get("id", ""): n for n in nodes}

    gaps: List[Gap] = []
    for parent_id, children in children_of.items():
        if len(children) < 3:
            continue

        parent_node = node_by_id.get(parent_id, {})

        # Count child role distribution
        role_counts: Dict[str, int] = {}
        for c in children:
            role = c.get("role", "Unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        # Compute entropy-like scatter: if no role has >30% share, it's a vacuum
        total = len(children)
        max_share = max(role_counts.values()) / total if total else 0

        if max_share < 0.3 and len(role_counts) >= 4:
            top_roles = sorted(role_counts.items(), key=lambda x: -x[1])[:5]
            role_summary = ", ".join(f"{r}({c})" for r, c in top_roles)

            gaps.append(Gap(
                location=parent_id,
                gap_type="purpose_vacuum",
                description=(
                    f"Container '{parent_id}' has {total} children with "
                    f"no dominant purpose pattern. Top roles: {role_summary}"
                ),
                severity="medium",
                circumscribed=True,
                llm_query_hint=(
                    f"Container '{parent_id}' has scattered child purposes "
                    f"({role_summary}). Is this a god class that should be "
                    f"split? What coherent sub-containers could organize "
                    f"its children?"
                ),
                context={
                    "parent_role": parent_node.get("role", "Unknown"),
                    "child_count": total,
                    "unique_roles": len(role_counts),
                    "max_share": round(max_share, 4),
                    "role_distribution": dict(top_roles),
                },
            ))

    return gaps


# ---------------------------------------------------------------------------
# LLM query target preparation
# ---------------------------------------------------------------------------

def _prepare_query_targets(gaps: List[Gap]) -> List[dict]:
    """Prepare structured LLM query specs from circumscribed gaps.

    Phase 1: Only PREPARES queries. Phase 2 will optionally EXECUTE them
    via cerebras_rapid_intel.py or analyze.py --aci.
    """
    targets = []
    for g in gaps:
        if not g.circumscribed:
            continue

        targets.append({
            "location": g.location,
            "gap_type": g.gap_type,
            "severity": g.severity,
            "query": g.llm_query_hint,
            "context": g.context,
        })

    # Sort by severity (critical first)
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    targets.sort(key=lambda t: severity_order.get(t["severity"], 9))

    return targets


# ---------------------------------------------------------------------------
# Coverage computation
# ---------------------------------------------------------------------------

def _compute_coverage(decomposition_results: List[DecompositionResult]) -> float:
    """Compute what fraction of expected compartments actually exist.

    Coverage = total present / total (required + expected) across all containers.
    """
    total_expected = 0
    total_present = 0

    for dr in decomposition_results:
        total_expected += len(dr.missing) + len(dr.gaps) + len(dr.present)
        total_present += len(dr.present)

    return total_present / max(total_expected, 1)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def detect_gaps(
    full_output: dict,
    decomposition_results: List[DecompositionResult],
) -> GapReport:
    """Detect all gaps in the codebase.

    Combines four gap detection strategies:
    1. Decomposition gaps (missing_required, missing_expected, forbidden_present)
    2. Disconnection detection (isolated nodes)
    3. Orphan cluster detection (unorganized top-level nodes)
    4. Purpose vacuum detection (containers with scattered children)

    Args:
        full_output: The unified analysis dict from Collider.
        decomposition_results: Results from decompose_purposes().

    Returns:
        GapReport with all detected gaps and LLM query targets.
    """
    all_gaps: List[Gap] = []

    # Strategy 1: From decomposition
    all_gaps.extend(_gaps_from_decomposition(decomposition_results))

    # Strategy 2: Disconnections
    all_gaps.extend(_detect_disconnections(full_output))

    # Strategy 3: Orphan clusters
    all_gaps.extend(_detect_orphan_clusters(full_output))

    # Strategy 4: Purpose vacuums
    all_gaps.extend(_detect_purpose_vacuums(full_output))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_gaps.sort(key=lambda g: severity_order.get(g.severity, 9))

    # Prepare LLM query targets
    query_targets = _prepare_query_targets(all_gaps)

    # Compute coverage
    coverage = _compute_coverage(decomposition_results)

    # Count circumscribed unknowns
    unknown_count = sum(1 for g in all_gaps if g.circumscribed)

    return GapReport(
        gaps=all_gaps,
        coverage=round(coverage, 4),
        unknown_count=unknown_count,
        query_targets=query_targets,
    )
