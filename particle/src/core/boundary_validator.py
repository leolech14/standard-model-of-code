"""
Boundary Validator — Declare architectural compartments, validate code against them.

Consumer agents declare compartment boundaries via a YAML file:

    compartments:
      api:
        globs: ["src/api/**", "src/routes/**"]
        allowed_deps: [core, models]
      core:
        globs: ["src/core/**", "src/engine/**"]
        allowed_deps: [models]
      models:
        globs: ["src/models/**"]
        allowed_deps: []  # leaf — no outbound deps

The validator:
1. Assigns every node to a compartment (or flags it as unmapped)
2. Cross-validates edges against allowed_deps
3. Produces a compliance report with violation details
4. Converts compliance rate to a 0-10 health score component

This lets AI consumers declare their architectural intent and have Collider
mechanically verify whether the code actually respects it.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
from fnmatch import fnmatch
from pathlib import Path

import yaml


# =============================================================================
# BOUNDARY LOADING
# =============================================================================

def load_boundaries(path: str) -> Dict[str, Any]:
    """
    Parse and validate a compartments YAML file.

    Expected format:
        compartments:
          <name>:
            globs: [<glob>, ...]
            allowed_deps: [<name>, ...]

    Args:
        path: Path to the YAML boundary file

    Returns:
        Dict with compartment definitions:
        {
            "compartments": {
                "api": {"globs": [...], "allowed_deps": [...]},
                ...
            }
        }

    Raises:
        FileNotFoundError: If the boundary file doesn't exist
        ValueError: If the YAML structure is invalid
    """
    boundary_path = Path(path)
    if not boundary_path.exists():
        raise FileNotFoundError(f"Boundary file not found: {path}")

    with open(boundary_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict) or "compartments" not in raw:
        raise ValueError(
            f"Boundary file must contain a 'compartments' key: {path}"
        )

    compartments = raw["compartments"]
    if not isinstance(compartments, dict):
        raise ValueError(
            f"'compartments' must be a mapping: {path}"
        )

    # Validate structure
    all_names = set(compartments.keys())
    for name, defn in compartments.items():
        if not isinstance(defn, dict):
            raise ValueError(
                f"Compartment '{name}' must be a mapping with 'globs' and 'allowed_deps'"
            )

        # Validate globs
        globs = defn.get("globs")
        if not globs or not isinstance(globs, list):
            raise ValueError(
                f"Compartment '{name}' must have a non-empty 'globs' list"
            )
        for g in globs:
            if not isinstance(g, str):
                raise ValueError(
                    f"Compartment '{name}' glob must be a string, got: {type(g).__name__}"
                )

        # Validate allowed_deps
        allowed = defn.get("allowed_deps", [])
        if not isinstance(allowed, list):
            raise ValueError(
                f"Compartment '{name}' 'allowed_deps' must be a list"
            )
        for dep in allowed:
            if dep not in all_names:
                raise ValueError(
                    f"Compartment '{name}' references unknown dependency '{dep}'. "
                    f"Valid compartments: {', '.join(sorted(all_names))}"
                )

    return {"compartments": compartments}


# =============================================================================
# COMPARTMENT ASSIGNMENT
# =============================================================================

def assign_compartments(
    nodes: List[Dict[str, Any]],
    boundaries: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Assign each node to a compartment based on file_path glob matching.

    Each node's file_path is matched against each compartment's globs.
    First match wins (compartment definition order).

    Mutates nodes in-place: adds 'compartment' field.

    Args:
        nodes: List of node dicts (must have 'file_path' and 'id')
        boundaries: Output of load_boundaries()

    Returns:
        {
            "assignments": {node_id: compartment_name, ...},
            "mapped_count": int,
            "unmapped_nodes": [node_ids...],
            "multi_mapped": [node_ids...],
        }
    """
    compartments = boundaries["compartments"]
    assignments: Dict[str, str] = {}
    unmapped: List[str] = []
    multi_mapped: List[str] = []

    for node in nodes:
        node_id = node.get("id", "")
        file_path = node.get("file_path", "")

        if not file_path:
            unmapped.append(node_id)
            continue

        matches: List[str] = []
        for comp_name, defn in compartments.items():
            for glob_pattern in defn.get("globs", []):
                if fnmatch(file_path, glob_pattern):
                    matches.append(comp_name)
                    break  # One match per compartment is enough

        if len(matches) == 0:
            unmapped.append(node_id)
        elif len(matches) == 1:
            assignments[node_id] = matches[0]
            node["compartment"] = matches[0]
        else:
            # Multiple compartments match — assign first, flag overlap
            multi_mapped.append(node_id)
            assignments[node_id] = matches[0]
            node["compartment"] = matches[0]

    return {
        "assignments": assignments,
        "mapped_count": len(assignments),
        "unmapped_nodes": unmapped,
        "multi_mapped": multi_mapped,
    }


# =============================================================================
# BOUNDARY VALIDATION
# =============================================================================

def validate_boundaries(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    assignments: Dict[str, str],
    boundaries: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Cross-validate edges against allowed_deps declarations.

    An edge from node A (compartment X) to node B (compartment Y) is a
    violation if Y is not in X's allowed_deps AND X != Y (intra-compartment
    edges are always allowed).

    Args:
        nodes: List of node dicts
        edges: List of edge dicts (must have 'source', 'target', 'edge_type')
        assignments: Node-to-compartment map from assign_compartments()
        boundaries: Output of load_boundaries()

    Returns:
        {
            "violations": [{source_node, target_node, source_compartment,
                           target_compartment, edge_type}, ...],
            "violation_count": int,
            "compliant_edges": int,
            "total_cross_compartment_edges": int,
            "compliance_rate": float,  # 0.0-1.0
            "per_compartment": {
                "api": {"violations": N, "compliant": N, "compliance_rate": float},
                ...
            }
        }
    """
    compartments = boundaries["compartments"]
    violations: List[Dict[str, Any]] = []
    compliant_edges = 0
    total_cross = 0

    # Build allowed_deps lookup as sets for O(1) membership
    allowed_deps: Dict[str, Set[str]] = {}
    for comp_name, defn in compartments.items():
        allowed_deps[comp_name] = set(defn.get("allowed_deps", []))

    # Per-compartment tracking
    per_comp: Dict[str, Dict[str, int]] = {
        name: {"violations": 0, "compliant": 0}
        for name in compartments
    }

    for edge in edges:
        source_id = edge.get("source", "")
        target_id = edge.get("target", "")
        edge_type = edge.get("edge_type", edge.get("type", "unknown"))

        source_comp = assignments.get(source_id)
        target_comp = assignments.get(target_id)

        # Skip edges where either node is unmapped
        if source_comp is None or target_comp is None:
            continue

        # Intra-compartment edges are always allowed
        if source_comp == target_comp:
            continue

        # This is a cross-compartment edge
        total_cross += 1

        if target_comp in allowed_deps.get(source_comp, set()):
            # Compliant cross-compartment edge
            compliant_edges += 1
            if source_comp in per_comp:
                per_comp[source_comp]["compliant"] += 1
        else:
            # VIOLATION
            violations.append({
                "source_node": source_id,
                "target_node": target_id,
                "source_compartment": source_comp,
                "target_compartment": target_comp,
                "edge_type": edge_type,
            })
            if source_comp in per_comp:
                per_comp[source_comp]["violations"] += 1

    # Compliance rate
    compliance_rate = 1.0
    if total_cross > 0:
        compliance_rate = compliant_edges / total_cross

    # Per-compartment compliance rates
    per_compartment: Dict[str, Dict[str, Any]] = {}
    for comp_name, counts in per_comp.items():
        comp_total = counts["violations"] + counts["compliant"]
        per_compartment[comp_name] = {
            "violations": counts["violations"],
            "compliant": counts["compliant"],
            "compliance_rate": (
                counts["compliant"] / comp_total if comp_total > 0 else 1.0
            ),
        }

    return {
        "violations": violations,
        "violation_count": len(violations),
        "compliant_edges": compliant_edges,
        "total_cross_compartment_edges": total_cross,
        "compliance_rate": round(compliance_rate, 4),
        "per_compartment": per_compartment,
    }


# =============================================================================
# HEALTH SCORE INTEGRATION
# =============================================================================

def compute_boundary_compliance_score(validation_result: Dict[str, Any]) -> float:
    """
    Convert boundary compliance rate to a 0-10 health score component.

    Scoring:
        100% compliance -> 10.0
          0% compliance ->  0.0
        Linear interpolation between.

    If there are no cross-compartment edges (nothing to validate),
    returns 10.0 (perfect — no violations possible).

    Args:
        validation_result: Output of validate_boundaries()

    Returns:
        Score from 0.0 to 10.0
    """
    total_cross = validation_result.get("total_cross_compartment_edges", 0)

    if total_cross == 0:
        return 10.0  # Nothing to violate

    compliance_rate = validation_result.get("compliance_rate", 1.0)
    return round(compliance_rate * 10.0, 2)


# =============================================================================
# SUMMARY
# =============================================================================

def format_boundary_summary(
    assignment_result: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> str:
    """Format a human-readable boundary validation summary."""
    lines = ["Boundary Validation Report", "=" * 40, ""]

    # Assignment stats
    mapped = assignment_result.get("mapped_count", 0)
    unmapped = len(assignment_result.get("unmapped_nodes", []))
    multi = len(assignment_result.get("multi_mapped", []))
    total = mapped + unmapped
    lines.append(f"Nodes mapped: {mapped}/{total}")
    if unmapped > 0:
        lines.append(f"Unmapped nodes: {unmapped}")
    if multi > 0:
        lines.append(f"Multi-mapped nodes (first match used): {multi}")
    lines.append("")

    # Compliance
    vcount = validation_result.get("violation_count", 0)
    cross = validation_result.get("total_cross_compartment_edges", 0)
    rate = validation_result.get("compliance_rate", 1.0)
    lines.append(f"Cross-compartment edges: {cross}")
    lines.append(f"Violations: {vcount}")
    lines.append(f"Compliance rate: {rate:.1%}")
    lines.append("")

    # Per-compartment
    per_comp = validation_result.get("per_compartment", {})
    if per_comp:
        lines.append("Per-compartment compliance:")
        for comp_name, stats in sorted(per_comp.items()):
            v = stats.get("violations", 0)
            c = stats.get("compliant", 0)
            cr = stats.get("compliance_rate", 1.0)
            lines.append(f"  {comp_name}: {cr:.1%} ({v} violations, {c} compliant)")
        lines.append("")

    # Top violations
    violations = validation_result.get("violations", [])
    if violations:
        lines.append(f"Top violations (showing first {min(10, len(violations))}):")
        for v in violations[:10]:
            lines.append(
                f"  {v['source_compartment']} -> {v['target_compartment']}: "
                f"{v['source_node']} -> {v['target_node']} ({v['edge_type']})"
            )

    return "\n".join(lines)
