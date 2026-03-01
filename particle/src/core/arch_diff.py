"""
Architectural Diff Engine — Compare two Collider analysis snapshots.

Computes semantic architectural deltas between two unified_analysis.json
snapshots, preserving all structural meaning that raw JSON diffing loses.

Consumer agents no longer need to manually diff snapshots — every cross-reference
(grade changes, cycle resolution, coupling shifts, level distribution changes)
is pre-computed deterministically.

Usage:
    from src.core.arch_diff import compute_arch_diff
    diff = compute_arch_diff(before_json, after_json)
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, defaultdict


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def compute_arch_diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two unified_analysis.json snapshots architecturally.

    Produces a complete architectural delta covering grade, health,
    node/edge changes, coupling shifts, cycle evolution, and level
    distribution changes.

    Args:
        before: First (older) analysis output dict
        after: Second (newer) analysis output dict

    Returns:
        Complete diff dict with all architectural deltas
    """
    grade_delta = _diff_grade(before, after)
    score_delta = _diff_score(before, after)
    health_delta = _diff_health_components(before, after)
    node_changes = _diff_nodes(before, after)
    edge_changes = _diff_edges(before, after)
    coupling_changes = _diff_coupling(before, after)
    cycle_changes = _diff_cycles(before, after)
    level_changes = _diff_levels(before, after)
    boundary_changes = _diff_boundaries(before, after)
    kpi_changes = _diff_kpis(before, after)

    summary = _generate_summary(
        grade_delta=grade_delta,
        score_delta=score_delta,
        node_changes=node_changes,
        edge_changes=edge_changes,
        coupling_changes=coupling_changes,
        cycle_changes=cycle_changes,
        level_changes=level_changes,
        boundary_changes=boundary_changes,
    )

    return {
        "meta": {
            "before_target": _safe_get(before, "meta", "target", default="unknown"),
            "after_target": _safe_get(after, "meta", "target", default="unknown"),
            "before_timestamp": _safe_get(before, "meta", "timestamp", default="unknown"),
            "after_timestamp": _safe_get(after, "meta", "timestamp", default="unknown"),
            "before_version": _safe_get(before, "meta", "version", default="unknown"),
            "after_version": _safe_get(after, "meta", "version", default="unknown"),
        },
        "grade_delta": grade_delta,
        "score_delta": score_delta,
        "health_components_delta": health_delta,
        "node_changes": node_changes,
        "edge_changes": edge_changes,
        "coupling_changes": coupling_changes,
        "cycle_changes": cycle_changes,
        "level_distribution_changes": level_changes,
        "boundary_changes": boundary_changes,
        "kpi_changes": kpi_changes,
        "summary": summary,
    }


# =============================================================================
# GRADE & SCORE DIFFING
# =============================================================================

def _diff_grade(before: Dict, after: Dict) -> Dict[str, Any]:
    """Compare architectural grades (A-F)."""
    b_grade = _get_grade(before)
    a_grade = _get_grade(after)

    grade_order = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
    b_val = grade_order.get(b_grade, 0)
    a_val = grade_order.get(a_grade, 0)

    if a_val > b_val:
        direction = "improved"
    elif a_val < b_val:
        direction = "regressed"
    else:
        direction = "unchanged"

    return {
        "before": b_grade,
        "after": a_grade,
        "direction": direction,
        "steps": a_val - b_val,
    }


def _diff_score(before: Dict, after: Dict) -> Dict[str, Any]:
    """Compare health scores (0-10)."""
    b_score = _get_health_score(before)
    a_score = _get_health_score(after)
    delta = round(a_score - b_score, 2)

    return {
        "before": b_score,
        "after": a_score,
        "delta": delta,
        "direction": "improved" if delta > 0 else "regressed" if delta < 0 else "unchanged",
        "percent_change": round((delta / b_score * 100) if b_score else 0, 1),
    }


def _diff_health_components(before: Dict, after: Dict) -> Dict[str, Any]:
    """Compare per-component health scores."""
    b_comps = _get_health_components(before)
    a_comps = _get_health_components(after)

    all_keys = sorted(set(list(b_comps.keys()) + list(a_comps.keys())))
    deltas = {}
    for key in all_keys:
        b_val = b_comps.get(key, 0.0)
        a_val = a_comps.get(key, 0.0)
        delta = round(a_val - b_val, 2)
        deltas[key] = {
            "before": b_val,
            "after": a_val,
            "delta": delta,
        }

    return {
        "components": deltas,
        "improved": [k for k, v in deltas.items() if v["delta"] > 0],
        "regressed": [k for k, v in deltas.items() if v["delta"] < 0],
        "unchanged": [k for k, v in deltas.items() if v["delta"] == 0],
    }


# =============================================================================
# NODE DIFFING
# =============================================================================

def _diff_nodes(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Compare nodes between snapshots.

    Matches nodes by 'id' field. Classifies each as:
    - added: present in after but not before
    - removed: present in before but not after
    - modified: present in both but key fields changed (kind, level, tier)
    - unchanged: identical in both
    """
    b_nodes = {n["id"]: n for n in before.get("nodes", []) if "id" in n}
    a_nodes = {n["id"]: n for n in after.get("nodes", []) if "id" in n}

    b_ids = set(b_nodes.keys())
    a_ids = set(a_nodes.keys())

    added_ids = a_ids - b_ids
    removed_ids = b_ids - a_ids
    common_ids = b_ids & a_ids

    modified = []
    unchanged_count = 0

    tracked_fields = ("kind", "level", "tier", "level_zone", "topology_role")

    for nid in common_ids:
        changes = {}
        for field in tracked_fields:
            b_val = b_nodes[nid].get(field)
            a_val = a_nodes[nid].get(field)
            if b_val != a_val:
                changes[field] = {"before": b_val, "after": a_val}
        if changes:
            modified.append({"id": nid, "name": a_nodes[nid].get("name", ""), "changes": changes})
        else:
            unchanged_count += 1

    # Aggregate per-level changes
    added_by_level = Counter(a_nodes[nid].get("level", "?") for nid in added_ids)
    removed_by_level = Counter(b_nodes[nid].get("level", "?") for nid in removed_ids)

    return {
        "added_count": len(added_ids),
        "removed_count": len(removed_ids),
        "modified_count": len(modified),
        "unchanged_count": unchanged_count,
        "added_ids": sorted(added_ids)[:50],  # Cap for readability
        "removed_ids": sorted(removed_ids)[:50],
        "modified": modified[:50],
        "added_by_level": dict(added_by_level),
        "removed_by_level": dict(removed_by_level),
    }


# =============================================================================
# EDGE DIFFING
# =============================================================================

def _edge_key(edge: Dict) -> Tuple[str, str, str]:
    """Create a stable key for edge matching."""
    return (
        edge.get("source", ""),
        edge.get("target", ""),
        edge.get("edge_type", edge.get("type", "")),
    )


def _diff_edges(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Compare edges between snapshots.

    Matches edges by (source, target, edge_type) composite key.
    """
    b_edges = before.get("edges", [])
    a_edges = after.get("edges", [])

    b_keys = {_edge_key(e) for e in b_edges}
    a_keys = {_edge_key(e) for e in a_edges}

    added = a_keys - b_keys
    removed = b_keys - a_keys

    # Aggregate by edge type
    added_by_type = Counter(k[2] for k in added)
    removed_by_type = Counter(k[2] for k in removed)

    return {
        "before_count": len(b_edges),
        "after_count": len(a_edges),
        "added_count": len(added),
        "removed_count": len(removed),
        "net_change": len(a_edges) - len(b_edges),
        "added_by_type": dict(added_by_type),
        "removed_by_type": dict(removed_by_type),
    }


# =============================================================================
# COUPLING DIFFING
# =============================================================================

def _diff_coupling(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Compare fan-in/fan-out for high-impact nodes.

    Reports the top nodes by degree change (absolute delta),
    useful for detecting new hubs or decoupled components.
    """
    b_in, b_out = _compute_degree_maps(before.get("edges", []))
    a_in, a_out = _compute_degree_maps(after.get("edges", []))

    all_nodes = set(list(b_in.keys()) + list(b_out.keys()) +
                    list(a_in.keys()) + list(a_out.keys()))

    changes = []
    for nid in all_nodes:
        b_fan_in = b_in.get(nid, 0)
        a_fan_in = a_in.get(nid, 0)
        b_fan_out = b_out.get(nid, 0)
        a_fan_out = a_out.get(nid, 0)

        delta_in = a_fan_in - b_fan_in
        delta_out = a_fan_out - b_fan_out

        if delta_in != 0 or delta_out != 0:
            changes.append({
                "id": nid,
                "fan_in": {"before": b_fan_in, "after": a_fan_in, "delta": delta_in},
                "fan_out": {"before": b_fan_out, "after": a_fan_out, "delta": delta_out},
                "total_delta": abs(delta_in) + abs(delta_out),
            })

    # Sort by total impact, return top 20
    changes.sort(key=lambda x: x["total_delta"], reverse=True)
    top_changes = changes[:20]

    return {
        "nodes_with_coupling_changes": len(changes),
        "top_changes": top_changes,
    }


def _compute_degree_maps(edges: List[Dict]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Compute in-degree and out-degree maps from edge list."""
    in_deg: Dict[str, int] = Counter()
    out_deg: Dict[str, int] = Counter()
    for e in edges:
        src = e.get("source", "")
        tgt = e.get("target", "")
        if src:
            out_deg[src] += 1
        if tgt:
            in_deg[tgt] += 1
    return dict(in_deg), dict(out_deg)


# =============================================================================
# CYCLE DIFFING
# =============================================================================

def _diff_cycles(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Compare cycle detection between snapshots.

    Reports new cycles, resolved cycles, and persistent cycles.
    Uses knot data from the Collider output.
    """
    b_knots = before.get("knots", {})
    a_knots = after.get("knots", {})

    b_cycles = b_knots.get("cycles_detected", 0)
    a_cycles = a_knots.get("cycles_detected", 0)
    b_score = b_knots.get("knot_score", 0)
    a_score = a_knots.get("knot_score", 0)

    # Extract cycle member sets for comparison
    b_cycle_sets = _extract_cycle_sets(b_knots)
    a_cycle_sets = _extract_cycle_sets(a_knots)

    resolved = b_cycle_sets - a_cycle_sets
    new_cycles = a_cycle_sets - b_cycle_sets
    persistent = b_cycle_sets & a_cycle_sets

    return {
        "before_count": b_cycles,
        "after_count": a_cycles,
        "delta": a_cycles - b_cycles,
        "knot_score_before": b_score,
        "knot_score_after": a_score,
        "knot_score_delta": round(a_score - b_score, 2),
        "resolved_count": len(resolved),
        "new_count": len(new_cycles),
        "persistent_count": len(persistent),
        "resolved": [list(s) for s in resolved],
        "new_cycles": [list(s) for s in new_cycles],
    }


def _extract_cycle_sets(knots: Dict) -> Set[frozenset]:
    """Extract cycle member sets as frozensets for comparison."""
    cycles = set()
    for cycle in knots.get("cycles", []):
        if isinstance(cycle, list):
            cycles.add(frozenset(cycle))
        elif isinstance(cycle, dict):
            members = cycle.get("members", cycle.get("nodes", []))
            cycles.add(frozenset(members))
    return cycles


# =============================================================================
# LEVEL DISTRIBUTION DIFFING
# =============================================================================

def _diff_levels(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Compare holarchy level distributions.

    Shows how the codebase composition shifted across levels
    (e.g., more L3 atoms added, fewer L5 files).
    """
    b_dist = _get_level_distribution(before)
    a_dist = _get_level_distribution(after)

    all_levels = sorted(
        set(list(b_dist.keys()) + list(a_dist.keys())),
        key=lambda x: _level_sort_key(x)
    )

    changes = {}
    for level in all_levels:
        b_count = b_dist.get(level, 0)
        a_count = a_dist.get(level, 0)
        delta = a_count - b_count
        changes[level] = {
            "before": b_count,
            "after": a_count,
            "delta": delta,
        }

    return {
        "per_level": changes,
        "total_before": sum(b_dist.values()),
        "total_after": sum(a_dist.values()),
        "total_delta": sum(a_dist.values()) - sum(b_dist.values()),
    }


def _level_sort_key(level: str) -> int:
    """Sort key for holarchy levels (L-3 to L12)."""
    try:
        return int(level.replace("L", ""))
    except ValueError:
        return 999


# =============================================================================
# BOUNDARY DIFFING
# =============================================================================

def _diff_boundaries(before: Dict, after: Dict) -> Optional[Dict[str, Any]]:
    """
    Compare boundary validation results (if both snapshots have them).

    Returns None if neither snapshot has boundary data.
    """
    b_boundary = before.get("boundary_validation")
    a_boundary = after.get("boundary_validation")

    if not b_boundary and not a_boundary:
        return None

    result = {
        "before_present": b_boundary is not None,
        "after_present": a_boundary is not None,
    }

    if b_boundary and a_boundary:
        b_rate = b_boundary.get("compliance_rate", 0)
        a_rate = a_boundary.get("compliance_rate", 0)
        b_violations = b_boundary.get("violation_count", 0)
        a_violations = a_boundary.get("violation_count", 0)

        result.update({
            "compliance_rate": {
                "before": b_rate,
                "after": a_rate,
                "delta": round(a_rate - b_rate, 4),
            },
            "violations": {
                "before": b_violations,
                "after": a_violations,
                "delta": a_violations - b_violations,
            },
        })

    return result


# =============================================================================
# KPI DIFFING
# =============================================================================

def _diff_kpis(before: Dict, after: Dict) -> Dict[str, Any]:
    """Compare key performance indicators."""
    b_kpis = before.get("kpis", {})
    a_kpis = after.get("kpis", {})

    all_keys = sorted(set(list(b_kpis.keys()) + list(a_kpis.keys())))
    deltas = {}

    for key in all_keys:
        b_val = b_kpis.get(key)
        a_val = a_kpis.get(key)

        # Only diff numeric KPIs
        if isinstance(b_val, (int, float)) and isinstance(a_val, (int, float)):
            delta = round(a_val - b_val, 4) if isinstance(a_val, float) else a_val - b_val
            deltas[key] = {
                "before": b_val,
                "after": a_val,
                "delta": delta,
            }
        elif b_val != a_val:
            deltas[key] = {
                "before": b_val,
                "after": a_val,
                "changed": True,
            }

    return deltas


# =============================================================================
# SUMMARY GENERATION
# =============================================================================

def _generate_summary(
    grade_delta: Dict,
    score_delta: Dict,
    node_changes: Dict,
    edge_changes: Dict,
    coupling_changes: Dict,
    cycle_changes: Dict,
    level_changes: Dict,
    boundary_changes: Optional[Dict],
) -> str:
    """
    Generate a natural language summary of architectural changes.

    Designed for AI consumption — dense, factual, no fluff.
    """
    lines = []

    # Grade change
    gd = grade_delta
    if gd["direction"] == "improved":
        lines.append(f"Grade improved from {gd['before']} to {gd['after']} (+{gd['steps']} steps).")
    elif gd["direction"] == "regressed":
        lines.append(f"Grade REGRESSED from {gd['before']} to {gd['after']} ({gd['steps']} steps).")
    else:
        lines.append(f"Grade unchanged at {gd['before']}.")

    # Score change
    sd = score_delta
    if sd["delta"] != 0:
        sign = "+" if sd["delta"] > 0 else ""
        lines.append(f"Health score: {sd['before']} -> {sd['after']} ({sign}{sd['delta']}).")

    # Node changes
    nc = node_changes
    parts = []
    if nc["added_count"]:
        parts.append(f"+{nc['added_count']} added")
    if nc["removed_count"]:
        parts.append(f"-{nc['removed_count']} removed")
    if nc["modified_count"]:
        parts.append(f"~{nc['modified_count']} modified")
    if parts:
        lines.append(f"Nodes: {', '.join(parts)}.")

    # Edge changes
    ec = edge_changes
    if ec["net_change"] != 0:
        sign = "+" if ec["net_change"] > 0 else ""
        lines.append(f"Edges: {ec['before_count']} -> {ec['after_count']} ({sign}{ec['net_change']}).")

    # Cycle changes
    cc = cycle_changes
    if cc["resolved_count"] > 0:
        lines.append(f"Cycles resolved: {cc['resolved_count']}.")
    if cc["new_count"] > 0:
        lines.append(f"NEW CYCLES DETECTED: {cc['new_count']}.")
    if cc["delta"] == 0 and cc["before_count"] > 0:
        lines.append(f"Cycles unchanged: {cc['before_count']} persistent.")

    # Coupling hotspots
    cp = coupling_changes
    if cp["top_changes"]:
        hottest = cp["top_changes"][0]
        lines.append(
            f"Coupling hotspot: {hottest['id']} "
            f"(fan-in {hottest['fan_in']['delta']:+d}, "
            f"fan-out {hottest['fan_out']['delta']:+d})."
        )

    # Level distribution
    lc = level_changes
    if lc["total_delta"] != 0:
        sign = "+" if lc["total_delta"] > 0 else ""
        lines.append(f"Total nodes: {lc['total_before']} -> {lc['total_after']} ({sign}{lc['total_delta']}).")

    # Boundary compliance
    if boundary_changes and boundary_changes.get("compliance_rate"):
        bc = boundary_changes["compliance_rate"]
        if bc["delta"] != 0:
            sign = "+" if bc["delta"] > 0 else ""
            lines.append(f"Boundary compliance: {bc['before']:.1%} -> {bc['after']:.1%} ({sign}{bc['delta']:.1%}).")

    return " ".join(lines)


# =============================================================================
# FORMAT HELPERS
# =============================================================================

def format_diff_markdown(diff: Dict[str, Any]) -> str:
    """Format the diff as a Markdown report."""
    lines = []
    lines.append("# Architectural Diff Report")
    lines.append("")

    # Meta
    meta = diff.get("meta", {})
    lines.append(f"**Before:** {meta.get('before_target', '?')} ({meta.get('before_timestamp', '?')})")
    lines.append(f"**After:** {meta.get('after_target', '?')} ({meta.get('after_timestamp', '?')})")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(diff.get("summary", "No changes detected."))
    lines.append("")

    # Grade & Score
    gd = diff["grade_delta"]
    sd = diff["score_delta"]
    lines.append("## Grade & Health")
    lines.append("")
    lines.append(f"| Metric | Before | After | Delta |")
    lines.append(f"|--------|--------|-------|-------|")
    lines.append(f"| Grade | {gd['before']} | {gd['after']} | {gd['direction']} |")
    lines.append(f"| Health Score | {sd['before']} | {sd['after']} | {sd['delta']:+.2f} |")
    lines.append("")

    # Health components
    hd = diff["health_components_delta"]
    if hd.get("components"):
        lines.append("## Health Components")
        lines.append("")
        lines.append("| Component | Before | After | Delta |")
        lines.append("|-----------|--------|-------|-------|")
        for comp, vals in hd["components"].items():
            lines.append(f"| {comp} | {vals['before']:.1f} | {vals['after']:.1f} | {vals['delta']:+.1f} |")
        lines.append("")

    # Node changes
    nc = diff["node_changes"]
    lines.append("## Node Changes")
    lines.append("")
    lines.append(f"- Added: {nc['added_count']}")
    lines.append(f"- Removed: {nc['removed_count']}")
    lines.append(f"- Modified: {nc['modified_count']}")
    lines.append(f"- Unchanged: {nc['unchanged_count']}")
    lines.append("")

    # Edge changes
    ec = diff["edge_changes"]
    lines.append("## Edge Changes")
    lines.append("")
    lines.append(f"- Before: {ec['before_count']} edges")
    lines.append(f"- After: {ec['after_count']} edges")
    lines.append(f"- Net change: {ec['net_change']:+d}")
    lines.append("")

    # Cycles
    cc = diff["cycle_changes"]
    if cc["before_count"] > 0 or cc["after_count"] > 0:
        lines.append("## Cycle Evolution")
        lines.append("")
        lines.append(f"- Before: {cc['before_count']} cycles (knot score: {cc['knot_score_before']})")
        lines.append(f"- After: {cc['after_count']} cycles (knot score: {cc['knot_score_after']})")
        if cc["resolved_count"]:
            lines.append(f"- Resolved: {cc['resolved_count']}")
        if cc["new_count"]:
            lines.append(f"- **New cycles: {cc['new_count']}**")
        lines.append("")

    # Level distribution
    lc = diff["level_distribution_changes"]
    levels_with_changes = {k: v for k, v in lc["per_level"].items() if v["delta"] != 0}
    if levels_with_changes:
        lines.append("## Level Distribution Changes")
        lines.append("")
        lines.append("| Level | Before | After | Delta |")
        lines.append("|-------|--------|-------|-------|")
        for level, vals in levels_with_changes.items():
            lines.append(f"| {level} | {vals['before']} | {vals['after']} | {vals['delta']:+d} |")
        lines.append("")

    return "\n".join(lines)


# =============================================================================
# SAFE ACCESSOR HELPERS
# =============================================================================

def _safe_get(d: Dict, *keys, default=None):
    """Safely traverse nested dicts."""
    current = d
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


def _get_grade(data: Dict) -> str:
    """Extract grade from analysis output (multiple possible locations)."""
    # Try compiled_insights first (canonical location)
    grade = _safe_get(data, "compiled_insights", "grade")
    if grade:
        return grade
    # Fallback to top-level
    return data.get("grade", "?")


def _get_health_score(data: Dict) -> float:
    """Extract health score from analysis output."""
    score = _safe_get(data, "compiled_insights", "health_score")
    if score is not None:
        return float(score)
    return float(data.get("health_score", 0.0))


def _get_health_components(data: Dict) -> Dict[str, float]:
    """Extract health component scores from analysis output."""
    comps = _safe_get(data, "compiled_insights", "health_components")
    if comps:
        return {k: float(v) for k, v in comps.items()}
    return {}


def _get_level_distribution(data: Dict) -> Dict[str, int]:
    """Extract level distribution from analysis output."""
    dist = _safe_get(data, "distributions", "levels")
    if dist:
        return {k: int(v) for k, v in dist.items()}
    return {}
