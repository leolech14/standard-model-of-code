"""Bridge: OpenClaw compartments → Collider Incoherence per-compartment.

Maps operational boundaries (compartments.yaml) to code structure metrics
(Collider output), computing per-compartment Incoherence Functional I-terms.

Usage:
    python -m particle.src.core.compartment_bridge \
        --compartments /path/to/compartments.yaml \
        --modules /path/to/dashboard_modules.yaml \
        --collider /path/to/collider_output.json \
        --output /tmp/compartment_health.json

Theory:
    The Incoherence Functional I(C) = I_struct + I_telic + I_sym + I_bound + I_flow
    is normally computed over the entire codebase. This bridge computes it per-compartment
    by extracting subgraphs — effectively a "local Lagrangian" per operational boundary.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_compartments(yaml_path: str) -> list[dict]:
    """Load compartments.yaml and return the list of compartment dicts."""
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict):
        return data.get("compartments", [])
    if isinstance(data, list):
        return data
    return []


def load_dashboard_modules(yaml_path: str) -> dict[str, list[str]]:
    """Load dashboard_modules.yaml. Returns {capability: [file_paths]}.

    The YAML structure is:
        schema_version: "2.0.0"
        files:
            dashboard/foo.py: {capability: X, layer: Y}
            ...

    We invert it to get capability → list of file paths.
    """
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return {}

    # The file mappings live under the "files" key
    files_section = data.get("files", {})
    if not isinstance(files_section, dict):
        files_section = {}

    result: dict[str, list[str]] = {}
    for file_path, meta in files_section.items():
        if isinstance(meta, dict):
            cap = meta.get("capability", "")
            if cap:
                result.setdefault(cap, []).append(file_path)
    return result


# ---------------------------------------------------------------------------
# Capability → Compartment name resolution
# ---------------------------------------------------------------------------

# Alias map: compartment ID → alternative capability names.
# Kept empty after renaming dashboard_modules.yaml to match compartments.yaml.
# Preserved as extension point if future naming divergence occurs.
_COMPARTMENT_TO_CAPABILITY: dict[str, str] = {}

# Compartments that map to code through dashboard_domains, not capabilities.
# Maps compartment ID → list of capabilities that serve that domain.
# NOTE: console-* compartments NO LONGER inherit all core files —
# the 'core' compartment now owns those 19 files directly.
_DOMAIN_COMPARTMENT_CAPABILITIES: dict[str, list[str]] = {
    "context-injection": ["intelligence-pipeline"],
    "telemetry": ["monitoring"],
}


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------

def map_compartment_to_files(
    compartment: dict,
    capability_files: dict[str, list[str]],
) -> set[str]:
    """Map compartment → file paths via dashboard_modules capability field.

    Resolution order:
    1. Direct match: compartment ID == capability name
    2. Alias match: compartment ID maps to different capability name
    3. Domain match: compartment has known domain→capability mapping
    4. config_files fallback: .py paths from compartment definition
    """
    comp_id = compartment.get("id", "")
    files: set[str] = set()

    # 1. Direct match
    files.update(capability_files.get(comp_id, []))

    # 2. Alias match (e.g., financial-intelligence → fin-intelligence)
    alias = _COMPARTMENT_TO_CAPABILITY.get(comp_id)
    if alias:
        files.update(capability_files.get(alias, []))

    # 3. Domain-based match (e.g., console-runtime → core files)
    domain_caps = _DOMAIN_COMPARTMENT_CAPABILITIES.get(comp_id, [])
    for cap in domain_caps:
        files.update(capability_files.get(cap, []))

    # 4. config_files fallback: .py paths from compartment definition
    for cf in compartment.get("config_files", []):
        if cf.startswith("dashboard/") and cf.endswith(".py"):
            files.add(cf)

    return files


def _filter_nodes_by_files(
    nodes: list[dict],
    file_paths: set[str],
) -> list[dict]:
    """Filter Collider nodes to those belonging to the given file paths."""
    return [n for n in nodes if n.get("file_path", "") in file_paths]


# ---------------------------------------------------------------------------
# Subgraph KPI extraction
# ---------------------------------------------------------------------------

def _sigmoid(x: float, midpoint: float, steepness: float = 10.0) -> float:
    """Sigmoid transfer (mirrored from incoherence.py)."""
    z = steepness * (x - midpoint)
    z = max(-500.0, min(500.0, z))
    return 1.0 / (1.0 + math.exp(-z))


def extract_subgraph_kpis(
    file_paths: set[str],
    full_output: dict,
) -> dict[str, Any]:
    """Extract and recompute KPIs for the subgraph defined by file_paths.

    Returns a dict of KPIs scoped to the subgraph: node count,
    orphan_percent, avg_fanout, purpose metrics, dead code estimate,
    cross-boundary ratio, coherence scores, and complexity metrics.
    """
    all_nodes = full_output.get("nodes", [])
    sub_nodes = _filter_nodes_by_files(all_nodes, file_paths)

    if not sub_nodes:
        return {"nodes": 0, "status": "no_nodes"}

    total = len(sub_nodes)
    kpis: dict[str, Any] = {"nodes_total": total, "files": len(file_paths)}

    # --- Orphan percent (nodes with 0 in_degree and 0 out_degree) ---
    orphans = sum(
        1 for n in sub_nodes
        if n.get("in_degree", 0) == 0 and n.get("out_degree", 0) == 0
    )
    kpis["orphan_percent"] = round(100.0 * orphans / total, 2) if total else 0

    # --- Average fan-out ---
    fanouts = [n.get("out_degree", 0) for n in sub_nodes]
    kpis["avg_fanout"] = round(sum(fanouts) / len(fanouts), 2) if fanouts else 0

    # --- Max fan-out (identifies god-class-like hubs within compartment) ---
    kpis["max_fanout"] = max(fanouts) if fanouts else 0

    # --- Average complexity ---
    # Collider stores this as "cyclomatic_complexity", not "complexity"
    # (the bare "complexity" field is always 0 — a naming artifact)
    complexities = [
        n.get("cyclomatic_complexity", 0) for n in sub_nodes
        if n.get("cyclomatic_complexity") is not None
        and n.get("cyclomatic_complexity", 0) > 0
    ]
    if complexities:
        kpis["avg_complexity"] = round(sum(complexities) / len(complexities), 2)

    # --- Purpose clarity (avg of pi2_confidence across subgraph) ---
    confidences = [
        n.get("pi2_confidence", 0) for n in sub_nodes
        if n.get("pi2_confidence") is not None
    ]
    if confidences:
        kpis["purpose_clarity"] = round(sum(confidences) / len(confidences), 4)

    # --- Alignment: count pi2_purpose categories ---
    purposes = [n.get("pi2_purpose", "UNKNOWN") for n in sub_nodes]
    unknown_count = sum(1 for p in purposes if p in ("UNKNOWN", None, ""))
    kpis["unknown_count"] = unknown_count
    kpis["total_nodes"] = total

    # --- Coherence score (per-node average, from Purpose Field analysis) ---
    # IMPORTANT: 98.9% of nodes have the default coherence_score=1.0 (uncomputed).
    # Only nodes matched by name in the Purpose Field get real values (0.0-0.56).
    # We EXCLUDE default 1.0 to avoid drowning real signals in noise.
    coherence_scores = [
        n.get("coherence_score") for n in sub_nodes
        if n.get("coherence_score") is not None
        and n.get("coherence_score") != 1.0  # skip uncomputed defaults
    ]
    if coherence_scores:
        kpis["avg_coherence"] = round(sum(coherence_scores) / len(coherence_scores), 4)
        kpis["coherence_computed_pct"] = round(
            100.0 * len(coherence_scores) / total, 1
        )

    # --- Dead code: orphaned nodes (in=0 AND out=0) as % of subgraph ---
    # More reliable than reachable_from_entry at subgraph level since
    # entry-reachability is a whole-graph property
    kpis["dead_code_percent"] = kpis["orphan_percent"]

    # --- Edge analysis: cross-boundary ratio ---
    edges = full_output.get("edges", [])
    sub_node_ids = {n.get("id", "") for n in sub_nodes}
    sub_edges = [
        e for e in edges
        if e.get("source", "") in sub_node_ids or e.get("target", "") in sub_node_ids
    ]
    total_sub_edges = len(sub_edges)
    kpis["edges_total"] = total_sub_edges

    if total_sub_edges > 0:
        # Internal edges: both endpoints inside compartment
        internal = sum(
            1 for e in sub_edges
            if e.get("source", "") in sub_node_ids and e.get("target", "") in sub_node_ids
        )
        cross_boundary = total_sub_edges - internal
        kpis["cross_boundary_ratio"] = round(cross_boundary / total_sub_edges, 4)
        kpis["internal_edges"] = internal
        kpis["cross_boundary_edges"] = cross_boundary
    else:
        kpis["cross_boundary_ratio"] = 0.0
        kpis["internal_edges"] = 0
        kpis["cross_boundary_edges"] = 0

    # --- Purpose entropy (diversity of purpose types within compartment) ---
    purpose_counts: dict[str, int] = {}
    for p in purposes:
        key = p if p else "UNKNOWN"
        purpose_counts[key] = purpose_counts.get(key, 0) + 1
    if len(purpose_counts) > 1:
        # Shannon entropy normalized to [0,1]
        max_entropy = math.log(len(purpose_counts))
        entropy = -sum(
            (c / total) * math.log(c / total)
            for c in purpose_counts.values()
            if c > 0
        )
        kpis["purpose_entropy"] = round(entropy / max_entropy if max_entropy > 0 else 0, 4)
    else:
        kpis["purpose_entropy"] = 0.0

    return kpis


# ---------------------------------------------------------------------------
# Per-compartment incoherence
# ---------------------------------------------------------------------------

def _compute_subgraph_i_struct(kpis: dict) -> float:
    """I_struct from subgraph KPIs.

    Uses orphan density and coherence scores.
    High orphan % and low coherence → high structural incoherence.
    """
    scores = []

    # Orphan density: structural fragmentation signal
    orphan_pct = kpis.get("orphan_percent")
    if orphan_pct is not None:
        scores.append(_sigmoid(orphan_pct, midpoint=10.0, steepness=0.2))

    # Coherence score (inverted): low coherence = high incoherence
    coherence = kpis.get("avg_coherence")
    if coherence is not None:
        scores.append(1.0 - max(0.0, min(1.0, coherence)))

    # Max fan-out as entanglement proxy: a node with 20+ outgoing edges
    # is a structural hub/god-class risk
    max_fan = kpis.get("max_fanout", 0)
    if max_fan > 0:
        scores.append(_sigmoid(max_fan, midpoint=10.0, steepness=0.3))

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def _compute_subgraph_i_telic(kpis: dict) -> float:
    """I_telic from subgraph KPIs.

    Uses purpose clarity, unknown ratio, and purpose entropy.
    """
    scores = []

    # Purpose clarity (inverted): low clarity → high incoherence
    clarity = kpis.get("purpose_clarity")
    if clarity is not None:
        scores.append(1.0 - max(0.0, min(1.0, clarity)))

    # Unknown purpose ratio
    unknown = kpis.get("unknown_count")
    total = kpis.get("total_nodes")
    if unknown is not None and total:
        ratio = unknown / max(total, 1)
        scores.append(_sigmoid(ratio, midpoint=0.15, steepness=8.0))

    # Purpose entropy: high entropy = many different purposes in one compartment
    # Some diversity is fine, but very high entropy means the compartment
    # lacks a coherent role
    entropy = kpis.get("purpose_entropy")
    if entropy is not None:
        # Moderate weight — some diversity is expected
        scores.append(_sigmoid(entropy, midpoint=0.7, steepness=5.0))

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def _compute_subgraph_i_sym(kpis: dict) -> float:
    """I_sym from subgraph KPIs.

    Uses orphan/dead code percentage and unknown purpose ratio
    as code-doc divergence proxies.
    """
    scores = []

    # Dead code (orphans)
    dead = kpis.get("dead_code_percent")
    if dead is not None:
        if dead <= 2:
            s = 0.15 * dead / 2
        elif dead <= 5:
            s = 0.15 + (0.25 * (dead - 2) / 3)
        elif dead <= 15:
            s = 0.4 + (0.35 * (dead - 5) / 10)
        else:
            s = min(0.95, 0.75 + (0.2 * (dead - 15) / 15))
        scores.append(s)

    # Unknown purpose as symmetry signal:
    # nodes that Collider can't classify suggest doc-code divergence
    unknown = kpis.get("unknown_count")
    total = kpis.get("total_nodes")
    if unknown is not None and total:
        ratio = unknown / max(total, 1)
        scores.append(_sigmoid(ratio, midpoint=0.1, steepness=15.0))

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def _compute_subgraph_i_bound(kpis: dict) -> float:
    """I_bound from subgraph KPIs.

    Uses cross-boundary ratio: the fraction of edges that connect
    this compartment to outside nodes. High ratio → high coupling
    to external systems → higher boundary incoherence.
    """
    scores = []

    # Cross-boundary ratio: THE key signal for boundary health
    # A well-encapsulated compartment has mostly internal edges
    cbr = kpis.get("cross_boundary_ratio")
    if cbr is not None:
        # midpoint=0.5 (50% cross-boundary is the inflection)
        scores.append(_sigmoid(cbr, midpoint=0.5, steepness=5.0))

    # Also penalize compartments with very few internal edges
    # (suggests the compartment is more of a pass-through than a cohesive unit)
    internal = kpis.get("internal_edges", 0)
    total_edges = kpis.get("edges_total", 0)
    if total_edges > 0 and internal == 0:
        scores.append(0.9)  # No internal edges at all = very porous boundary

    return round(sum(scores) / len(scores), 4) if scores else 0.5


def _compute_subgraph_i_flow(kpis: dict) -> float:
    """I_flow from subgraph KPIs.

    Uses average fan-out and average complexity.
    """
    scores = []

    # Average fan-out: high fan-out = high flow complexity
    fanout = kpis.get("avg_fanout")
    if fanout is not None:
        scores.append(_sigmoid(fanout, midpoint=5.0, steepness=0.5))

    # Average complexity: high cyclomatic complexity = convoluted flow
    complexity = kpis.get("avg_complexity")
    if complexity is not None:
        scores.append(_sigmoid(complexity, midpoint=8.0, steepness=0.3))

    return round(sum(scores) / len(scores), 4) if scores else 0.5


# Weights (same as incoherence.py DEFAULT_WEIGHTS)
_WEIGHTS = {"struct": 0.25, "telic": 0.20, "sym": 0.15, "bound": 0.20, "flow": 0.20}


def compute_compartment_incoherence(
    compartment: dict,
    capability_files: dict[str, list[str]],
    full_output: dict,
) -> dict[str, Any]:
    """Full pipeline: compartment → files → subgraph → I-terms.

    Returns dict with file count, node count, 5 I-terms, I-total, and health_10.
    """
    file_paths = map_compartment_to_files(compartment, capability_files)
    if not file_paths:
        return {
            "id": compartment.get("id", ""),
            "files": 0,
            "nodes": 0,
            "status": "no_code_files",
        }

    kpis = extract_subgraph_kpis(file_paths, full_output)
    if kpis.get("status") == "no_nodes":
        return {
            "id": compartment.get("id", ""),
            "files": len(file_paths),
            "nodes": 0,
            "status": "no_nodes_in_collider",
        }

    i_struct = _compute_subgraph_i_struct(kpis)
    i_telic = _compute_subgraph_i_telic(kpis)
    i_sym = _compute_subgraph_i_sym(kpis)
    i_bound = _compute_subgraph_i_bound(kpis)
    i_flow = _compute_subgraph_i_flow(kpis)

    w = _WEIGHTS
    i_total = (
        w["struct"] * i_struct
        + w["telic"] * i_telic
        + w["sym"] * i_sym
        + w["bound"] * i_bound
        + w["flow"] * i_flow
    )
    i_total = round(max(0.0, min(1.0, i_total)), 4)
    health_10 = round(10.0 * (1.0 - i_total), 2)

    return {
        "id": compartment.get("id", ""),
        "files": len(file_paths),
        "nodes": kpis.get("nodes_total", 0),
        "i_struct": i_struct,
        "i_telic": i_telic,
        "i_sym": i_sym,
        "i_bound": i_bound,
        "i_flow": i_flow,
        "i_total": i_total,
        "health_10": health_10,
    }


# ---------------------------------------------------------------------------
# Batch: all compartments
# ---------------------------------------------------------------------------

def compute_all_compartments(
    yaml_path: str,
    modules_yaml_path: str,
    collider_output_path: str,
) -> dict[str, Any]:
    """Compute I-terms for every compartment that has code files.

    Returns structured dict with compartment results and umbrella summaries.
    """
    compartments = load_compartments(yaml_path)
    capability_files = load_dashboard_modules(modules_yaml_path)

    with open(collider_output_path, "r") as f:
        full_output = json.load(f)

    results: dict[str, Any] = {}
    umbrellas: dict[str, dict] = {}

    # Index compartments by id for umbrella lookup
    comp_by_id = {c["id"]: c for c in compartments}

    for comp in compartments:
        comp_id = comp.get("id", "")
        if comp.get("kind") == "umbrella":
            # Umbrellas are computed after children
            umbrellas[comp_id] = comp
            continue

        result = compute_compartment_incoherence(comp, capability_files, full_output)
        results[comp_id] = result

    # Compute umbrella health as worst-of children
    umbrella_results: dict[str, Any] = {}
    for umb_id, umb in umbrellas.items():
        children = umb.get("sub_compartments", [])
        child_healths = []
        for child_id in children:
            child = results.get(child_id, {})
            h = child.get("health_10")
            if h is not None:
                child_healths.append(h)

        if child_healths:
            worst = min(child_healths)
            umbrella_results[umb_id] = {
                "health_10": worst,
                "derivation": "worst-of-children",
                "children": children,
                "child_healths": {
                    cid: results.get(cid, {}).get("health_10")
                    for cid in children
                },
            }
        else:
            umbrella_results[umb_id] = {
                "health_10": None,
                "derivation": "no-children-with-code",
                "children": children,
            }

    # --- Coverage metrics: what fraction of Collider is mapped? ---
    all_nodes = full_output.get("nodes", [])
    all_collider_files = {n.get("file_path", "") for n in all_nodes}
    all_collider_files.discard("")

    # All files claimed by any compartment
    mapped_files: set[str] = set()
    for comp in compartments:
        if comp.get("kind") == "umbrella":
            continue
        mapped_files.update(map_compartment_to_files(comp, capability_files))

    # All files in dashboard_modules (regardless of compartment match)
    all_module_files: set[str] = set()
    for cap_files_list in capability_files.values():
        all_module_files.update(cap_files_list)

    unmapped_files = sorted(all_collider_files - mapped_files)
    mapped_nodes = sum(1 for n in all_nodes if n.get("file_path", "") in mapped_files)
    unmapped_nodes = len(all_nodes) - mapped_nodes

    # Group unmapped files by top-level directory
    unmapped_by_dir: dict[str, int] = {}
    for f in unmapped_files:
        parts = f.split("/")
        top = parts[0] if parts else "root"
        unmapped_by_dir[top] = unmapped_by_dir.get(top, 0) + 1

    coverage = {
        "collider_total_nodes": len(all_nodes),
        "collider_total_files": len(all_collider_files),
        "dashboard_modules_files": len(all_module_files),
        "mapped_to_compartments": {
            "files": len(mapped_files),
            "nodes": mapped_nodes,
        },
        "unmapped": {
            "files": len(unmapped_files),
            "nodes": unmapped_nodes,
            "by_directory": dict(sorted(unmapped_by_dir.items(), key=lambda x: -x[1])),
        },
        "coverage_pct": round(100.0 * mapped_nodes / len(all_nodes), 1) if all_nodes else 0,
    }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {
            "compartments_yaml": yaml_path,
            "dashboard_modules_yaml": modules_yaml_path,
            "collider_output": collider_output_path,
        },
        "coverage": coverage,
        "compartments": results,
        "umbrellas": umbrella_results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute per-compartment Incoherence Functional from Collider output.",
    )
    parser.add_argument("--compartments", required=True, help="Path to compartments.yaml")
    parser.add_argument("--modules", required=True, help="Path to dashboard_modules.yaml")
    parser.add_argument("--collider", required=True, help="Path to collider_output.json")
    parser.add_argument("--output", default=None, help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    result = compute_all_compartments(args.compartments, args.modules, args.collider)

    output_json = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Written to {args.output}")

        # Coverage summary
        cov = result.get("coverage", {})
        mapped = cov.get("mapped_to_compartments", {})
        unmapped = cov.get("unmapped", {})
        print(f"\n  Coverage: {cov.get('coverage_pct', 0)}% of Collider nodes mapped")
        print(f"  {mapped.get('nodes', 0)}/{cov.get('collider_total_nodes', 0)} nodes, "
              f"{mapped.get('files', 0)}/{cov.get('collider_total_files', 0)} files")
        if unmapped.get("by_directory"):
            print(f"  Unmapped ({unmapped.get('files', 0)} files):")
            for d, c in list(unmapped["by_directory"].items())[:5]:
                print(f"    {d}/: {c} files")

        # Compartment summary
        comps = result.get("compartments", {})
        active = {k: v for k, v in comps.items() if v.get("health_10") is not None}
        print(f"\n  {len(active)} compartments with code / {len(comps)} total")
        for cid, data in sorted(active.items(), key=lambda x: x[1].get("health_10", 0)):
            print(f"  {cid:25s}  health={data['health_10']:5.2f}  nodes={data.get('nodes', 0)}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
