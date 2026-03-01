"""
Group Cohesion — Per-compartment cohesion and coupling metrics.

Given boundary assignments (from boundary_validator), computes for each
declared compartment:

- Internal cohesion (what fraction of edges stay inside)
- External coupling (in/out split)
- Instability metric (Martin's I = Ce / (Ca + Ce))
- Coupling partners (who they talk to most)

Plus a cross-compartment coupling matrix and overall modularity score.

Depends on Feature 1 (boundary_validator) for compartment assignments.
"""

from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict


# =============================================================================
# CORE COMPUTATION
# =============================================================================

def compute_group_cohesion(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    assignments: Dict[str, str],
) -> Dict[str, Any]:
    """
    Compute cohesion and coupling metrics for each declared compartment.

    For each compartment:
    - internal_edges: edges where BOTH source and target are in the compartment
    - external_in: edges entering from another compartment
    - external_out: edges leaving to another compartment
    - cohesion_ratio: internal / (internal + external_in + external_out)
    - instability: external_out / (external_out + external_in)  [Martin's I]

    Args:
        nodes: List of node dicts (with 'id' fields)
        edges: List of edge dicts (with 'source', 'target', 'edge_type')
        assignments: Node-to-compartment map from assign_compartments()

    Returns:
        {
            "per_group": {
                "api": {
                    "node_count": int,
                    "internal_edges": int,
                    "external_in": int,
                    "external_out": int,
                    "cohesion_ratio": float,    # 0.0-1.0 (higher = more cohesive)
                    "instability": float,        # 0.0-1.0 (0=stable, 1=unstable)
                    "coupling_partners": {"core": N, "models": N},
                },
                ...
            },
            "overall_modularity": float,  # weighted average cohesion
            "coupling_matrix": {          # Cross-compartment edge counts
                "api->core": N,
                "api->models": N,
                ...
            }
        }
    """
    # Build node-to-compartment quick lookup
    # (assignments dict already maps node_id -> compartment_name)

    # Count nodes per compartment
    node_counts: Dict[str, int] = defaultdict(int)
    for node_id, comp in assignments.items():
        node_counts[comp] += 1

    # Collect all known compartments (even if they have no edges)
    all_compartments: Set[str] = set(assignments.values())

    # Initialize per-group accumulators
    per_group: Dict[str, Dict[str, Any]] = {}
    for comp in all_compartments:
        per_group[comp] = {
            "node_count": node_counts[comp],
            "internal_edges": 0,
            "external_in": 0,
            "external_out": 0,
            "coupling_partners": defaultdict(int),
        }

    # Coupling matrix: directed counts between compartments
    coupling_matrix: Dict[str, int] = defaultdict(int)

    # Classify each edge
    for edge in edges:
        source_id = edge.get("source", "")
        target_id = edge.get("target", "")

        source_comp = assignments.get(source_id)
        target_comp = assignments.get(target_id)

        # Skip edges where either node is unmapped
        if source_comp is None or target_comp is None:
            continue

        if source_comp == target_comp:
            # Intra-compartment edge
            per_group[source_comp]["internal_edges"] += 1
        else:
            # Cross-compartment edge
            per_group[source_comp]["external_out"] += 1
            per_group[target_comp]["external_in"] += 1

            # Track coupling partners
            per_group[source_comp]["coupling_partners"][target_comp] += 1

            # Coupling matrix (directed)
            matrix_key = f"{source_comp}->{target_comp}"
            coupling_matrix[matrix_key] += 1

    # Compute derived metrics for each group
    for comp, stats in per_group.items():
        internal = stats["internal_edges"]
        ext_in = stats["external_in"]
        ext_out = stats["external_out"]
        total = internal + ext_in + ext_out

        # Cohesion ratio: fraction of edges that are internal
        stats["cohesion_ratio"] = round(
            internal / total if total > 0 else 1.0, 4
        )

        # Martin's Instability metric: I = Ce / (Ca + Ce)
        # Ce = efferent coupling (outgoing), Ca = afferent coupling (incoming)
        ext_total = ext_in + ext_out
        stats["instability"] = round(
            ext_out / ext_total if ext_total > 0 else 0.0, 4
        )

        # Convert defaultdict to regular dict for serialization
        stats["coupling_partners"] = dict(stats["coupling_partners"])

    # Overall modularity: weighted average cohesion (weighted by total edges)
    overall_modularity = _compute_overall_modularity(per_group)

    return {
        "per_group": per_group,
        "overall_modularity": overall_modularity,
        "coupling_matrix": dict(coupling_matrix),
    }


def _compute_overall_modularity(per_group: Dict[str, Dict[str, Any]]) -> float:
    """
    Compute weighted average cohesion across all compartments.

    Weight is proportional to total edge count (internal + external)
    for each compartment. Compartments with more edges have more influence.

    Returns 1.0 if there are no edges at all (vacuously cohesive).
    """
    total_weight = 0.0
    weighted_cohesion = 0.0

    for comp, stats in per_group.items():
        weight = (
            stats["internal_edges"]
            + stats["external_in"]
            + stats["external_out"]
        )
        weighted_cohesion += stats["cohesion_ratio"] * weight
        total_weight += weight

    if total_weight == 0:
        return 1.0  # No edges at all

    return round(weighted_cohesion / total_weight, 4)


# =============================================================================
# SUMMARY
# =============================================================================

def format_cohesion_summary(cohesion_data: Dict[str, Any]) -> str:
    """Format a human-readable cohesion report."""
    lines = ["Group Cohesion Report", "=" * 40, ""]

    per_group = cohesion_data.get("per_group", {})
    modularity = cohesion_data.get("overall_modularity", 0.0)

    lines.append(f"Overall modularity: {modularity:.1%}")
    lines.append("")

    # Per-group details
    for comp_name in sorted(per_group.keys()):
        stats = per_group[comp_name]
        lines.append(f"  {comp_name}:")
        lines.append(f"    Nodes: {stats['node_count']}")
        lines.append(f"    Internal edges: {stats['internal_edges']}")
        lines.append(f"    External in: {stats['external_in']}")
        lines.append(f"    External out: {stats['external_out']}")
        lines.append(f"    Cohesion: {stats['cohesion_ratio']:.1%}")
        lines.append(f"    Instability: {stats['instability']:.2f}")

        partners = stats.get("coupling_partners", {})
        if partners:
            partner_str = ", ".join(
                f"{p}: {c}" for p, c in sorted(
                    partners.items(), key=lambda x: -x[1]
                )
            )
            lines.append(f"    Coupling: {partner_str}")
        lines.append("")

    # Coupling matrix
    coupling = cohesion_data.get("coupling_matrix", {})
    if coupling:
        lines.append("Cross-compartment coupling matrix:")
        for key in sorted(coupling.keys()):
            lines.append(f"  {key}: {coupling[key]}")

    return "\n".join(lines)
