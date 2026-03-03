"""
Incoherence Functional -- The Lagrangian of Code

Computes I(C) = I_struct + I_telic + I_sym + I_bound + I_flow
from Collider full_output. Each I-term in [0,1]. Total normalized to [0,1].

Health_10 = 10 * (1 - I_total)

Theory: docs/essentials/LAGRANGIAN.md
Axiom: D7 -- d P/dt = -grad I(C)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNKNOWN = 0.5  # Missing data => midpoint, NOT falsely perfect 0.0

DEFAULT_WEIGHTS = {
    "struct": 0.25,
    "telic": 0.20,
    "sym": 0.15,
    "bound": 0.20,
    "flow": 0.20,
}

# Topology shape -> incoherence mapping
_SHAPE_INCOHERENCE = {
    "STAR": 0.7,              # hub-spoke = high coupling
    "CHAIN": 0.4,             # linear = moderate
    "CYCLIC_NETWORK": 0.5,    # cycles = moderate-high
    "HIERARCHICAL": 0.15,     # ideal tree-ish
    "MESH": 0.6,              # dense = high coupling
    "LAYERED": 0.1,           # ideal layered
    "MODULAR": 0.1,           # ideal modular
    "DISCONNECTED": 0.8,      # fragmented = very high
}

# Alignment health enum -> incoherence
_ALIGNMENT_INCOHERENCE = {
    "EXCELLENT": 0.05,
    "GOOD": 0.15,
    "MODERATE": 0.35,
    "POOR": 0.65,
    "CRITICAL": 0.85,
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class IncoherenceResult:
    """Result of computing the Incoherence Functional I(C)."""

    i_struct: float    # structural (antimatter, cycles, entanglement)
    i_telic: float     # teleological (purpose clarity, orphans, alignment)
    i_sym: float       # symmetry (code-doc divergence, dead code)
    i_bound: float     # boundary (layer violations, compliance)
    i_flow: float      # flow (complexity, fan-out, topology)
    i_total: float     # weighted sum in [0,1]
    health_10: float   # 10 * (1 - i_total)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Transfer functions
# ---------------------------------------------------------------------------

def _sigmoid(x: float, midpoint: float, steepness: float = 10.0) -> float:
    """Sigmoid transfer: maps x to [0,1] with configurable midpoint.

    At x=midpoint, output=0.5. Steepness controls slope.
    Higher x -> higher incoherence (closer to 1.0).
    """
    z = steepness * (x - midpoint)
    z = max(-500.0, min(500.0, z))  # clamp to avoid overflow
    return 1.0 / (1.0 + math.exp(-z))


def _inv_sigmoid(x: float, midpoint: float, steepness: float = 10.0) -> float:
    """Inverse sigmoid: higher x -> LOWER incoherence.

    Used for metrics where high values are GOOD (e.g., compliance_score).
    """
    return 1.0 - _sigmoid(x, midpoint, steepness)


def _piecewise(x: float, breakpoints: list, values: list) -> float:
    """Piecewise linear interpolation.

    breakpoints and values must be same length, sorted ascending on breakpoints.
    Returns linearly interpolated value. Clamps outside range.
    """
    if x <= breakpoints[0]:
        return values[0]
    if x >= breakpoints[-1]:
        return values[-1]
    for i in range(len(breakpoints) - 1):
        if breakpoints[i] <= x <= breakpoints[i + 1]:
            t = (x - breakpoints[i]) / (breakpoints[i + 1] - breakpoints[i])
            return values[i] + t * (values[i + 1] - values[i])
    return values[-1]


def _safe_get(data: dict, *keys, default=None):
    """Safely traverse nested dicts. Returns default if any key missing."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current


def _chem_mod(full_output: dict, target: str) -> float:
    """Get chemistry modulation for a target from serialized output. Returns 1.0 if none."""
    chem = full_output.get("chemistry", {})
    mods = chem.get("modulations", [])
    coeff = 1.0
    for m in mods:
        if m.get("target") == target:
            coeff *= m.get("coefficient", 1.0)
    return coeff


# ---------------------------------------------------------------------------
# I-term computations
# ---------------------------------------------------------------------------

def _compute_i_struct(full_output: dict) -> tuple[float, dict]:
    """Structural Incoherence: antimatter, knots, cycles.

    Sources:
    - kpis.rho_antimatter: fraction of antimatter edges [0, ~0.1]
    - kpis.knot_score: entanglement metric [0, ~10]
    - kpis.cycles_detected: number of cycles [0, N]
    - kpis.igt_stability_index: IGT stability [0, 1] (high=stable=good)
    """
    kpis = full_output.get("kpis", {})

    rho_am = kpis.get("rho_antimatter")
    knot = kpis.get("knot_score")
    cycles = kpis.get("cycles_detected")
    igt = kpis.get("igt_stability_index")

    components = {}
    scores = []

    if rho_am is not None:
        s = _sigmoid(rho_am, midpoint=0.03, steepness=80.0)
        components["antimatter"] = {"raw": rho_am, "score": round(s, 4)}
        scores.append(s)
    if knot is not None:
        s = _sigmoid(knot, midpoint=3.0, steepness=1.0)
        components["entanglement"] = {"raw": knot, "score": round(s, 4)}
        scores.append(s)
    if cycles is not None:
        # Normalize by total nodes to get cycle density
        total = kpis.get("nodes_total", 1000)
        cycle_density = cycles / max(total, 1)
        s = _sigmoid(cycle_density, midpoint=0.01, steepness=200.0)
        components["cycles"] = {"raw": cycles, "density": round(cycle_density, 6), "score": round(s, 4)}
        scores.append(s)
    if igt is not None:
        # High stability = low incoherence
        s = 1.0 - max(0.0, min(1.0, igt))
        components["igt_stability"] = {"raw": igt, "score": round(s, 4)}
        scores.append(s)

    if not scores:
        return UNKNOWN, {"status": "no_data", "components": {}}

    i_struct = sum(scores) / len(scores)
    # Apply chemistry modulation (mod < 1.0 → divide to raise incoherence)
    mod = _chem_mod(full_output, "i_struct")
    if mod != 1.0:
        i_struct = min(1.0, i_struct / mod)
    return round(i_struct, 4), {"components": components}


def _compute_i_telic(full_output: dict) -> tuple[float, dict]:
    """Teleological Incoherence: purpose clarity, alignment, orphans, god classes.

    Sources:
    - purpose_field.purpose_clarity: [0, 1] (high=clear=good)
    - purpose_field.alignment_health: enum string
    - kpis.orphan_percent: percentage [0, 100]
    - purpose_field.god_class_count: count
    - purpose_field.uncertain_count / total_nodes: ratio
    """
    pf = full_output.get("purpose_field", {})
    kpis = full_output.get("kpis", {})

    clarity = pf.get("purpose_clarity")
    alignment = pf.get("alignment_health")
    orphan_pct = kpis.get("orphan_percent")
    god_count = pf.get("god_class_count")
    uncertain = pf.get("uncertain_count")
    total = pf.get("total_nodes")

    components = {}
    scores = []

    if clarity is not None:
        # High clarity = low incoherence
        s = 1.0 - max(0.0, min(1.0, clarity))
        components["purpose_clarity"] = {"raw": clarity, "score": round(s, 4)}
        scores.append(s)
    if alignment is not None:
        s = _ALIGNMENT_INCOHERENCE.get(str(alignment).upper(), UNKNOWN)
        components["alignment_health"] = {"raw": alignment, "score": round(s, 4)}
        scores.append(s)
    if orphan_pct is not None:
        # orphan_percent is 0-100
        s = _sigmoid(orphan_pct, midpoint=5.0, steepness=0.3)
        components["orphan_density"] = {"raw": orphan_pct, "score": round(s, 4)}
        scores.append(s)
    if god_count is not None and total:
        god_ratio = god_count / max(total, 1)
        s = _sigmoid(god_ratio, midpoint=0.02, steepness=50.0)
        components["god_class_ratio"] = {"raw": god_count, "ratio": round(god_ratio, 4), "score": round(s, 4)}
        scores.append(s)
    if uncertain is not None and total:
        uncertain_ratio = uncertain / max(total, 1)
        s = _sigmoid(uncertain_ratio, midpoint=0.2, steepness=5.0)
        components["uncertain_ratio"] = {"raw": uncertain, "ratio": round(uncertain_ratio, 4), "score": round(s, 4)}
        scores.append(s)

    if not scores:
        return UNKNOWN, {"status": "no_data", "components": {}}

    i_telic = sum(scores) / len(scores)
    # Apply chemistry modulation
    mod = _chem_mod(full_output, "i_telic")
    if mod != 1.0:
        i_telic = min(1.0, i_telic / mod)
    return round(i_telic, 4), {"components": components}


def _compute_i_sym(full_output: dict) -> tuple[float, dict]:
    """Symmetry Incoherence: code-doc divergence, dead code.

    Sources:
    - kpis.dead_code_percent: percentage [0, 100]
    - purpose_field.unknown_count: nodes with unknown purpose
    - purpose_field.total_nodes: total nodes
    - coverage.rpbl_coverage: RPBL coverage [0, 100] (high=good)
    - contextome.purpose_coverage: fraction of docs with purpose signals [0, 1]
    - contextome.symmetry_seeds: doc-code relationship seeds

    The contextome provides the first real code-doc symmetry signal.
    purpose_coverage measures how much the Contextome communicates intent.
    symmetry_seeds measure how well docs map to code they describe.
    """
    kpis = full_output.get("kpis", {})
    pf = full_output.get("purpose_field", {})
    coverage = full_output.get("coverage", {})
    ctx = full_output.get("contextome", {})

    dead_pct = kpis.get("dead_code_percent")
    unknown = pf.get("unknown_count")
    total = pf.get("total_nodes")
    rpbl_cov = coverage.get("rpbl_coverage")

    components = {}
    scores = []

    if dead_pct is not None:
        # dead_code_percent is 0-100
        s = _piecewise(dead_pct, [0, 2, 5, 15, 30], [0.0, 0.15, 0.4, 0.75, 0.95])
        components["dead_code"] = {"raw": dead_pct, "score": round(s, 4)}
        scores.append(s)
    if unknown is not None and total:
        unknown_ratio = unknown / max(total, 1)
        s = _sigmoid(unknown_ratio, midpoint=0.1, steepness=15.0)
        components["unknown_purpose"] = {"raw": unknown, "ratio": round(unknown_ratio, 4), "score": round(s, 4)}
        scores.append(s)
    if rpbl_cov is not None:
        # High coverage = low incoherence
        s = _piecewise(rpbl_cov, [0, 50, 80, 95, 100], [1.0, 0.7, 0.35, 0.1, 0.0])
        components["rpbl_coverage"] = {"raw": rpbl_cov, "score": round(s, 4)}
        scores.append(s)

    # --- Contextome symmetry signals ---
    if ctx:
        purpose_cov = ctx.get("purpose_coverage")
        sym_seeds = ctx.get("symmetry_seeds", [])
        doc_count = ctx.get("doc_count", 0)

        if purpose_cov is not None and doc_count > 0:
            # Low purpose_coverage = high symmetry incoherence
            # (docs exist but don't communicate purpose)
            s = _piecewise(
                purpose_cov * 100,  # convert to 0-100
                [0, 30, 60, 80, 100],
                [0.9, 0.6, 0.35, 0.15, 0.0],
            )
            components["contextome_purpose_coverage"] = {
                "raw": round(purpose_cov, 4),
                "doc_count": doc_count,
                "score": round(s, 4),
            }
            scores.append(s)

        if sym_seeds and doc_count > 0:
            # Average confidence of symmetry seeds
            avg_conf = sum(
                ss.get("confidence", 0) for ss in sym_seeds
            ) / max(len(sym_seeds), 1)
            # Low avg confidence = high symmetry incoherence
            s = _piecewise(
                avg_conf * 100,
                [0, 30, 50, 70, 100],
                [0.85, 0.55, 0.35, 0.15, 0.0],
            )
            components["contextome_symmetry_confidence"] = {
                "raw": round(avg_conf, 4),
                "seed_count": len(sym_seeds),
                "score": round(s, 4),
            }
            scores.append(s)

    # --- Ideome coherence signal ---
    ideome = full_output.get("ideome", {})
    if ideome:
        global_coherence = ideome.get("global_coherence")
        if global_coherence is not None:
            # Low coherence = high symmetry incoherence (double-weighted)
            s = 1.0 - max(0.0, min(1.0, global_coherence))
            components["ideome_coherence"] = {
                "raw": round(global_coherence, 4),
                "score": round(s, 4),
            }
            scores.append(s)
            scores.append(s)  # double-weight: ideome triangulates, strongest signal

    # --- Chemistry compound severity signal ---
    chem = full_output.get("chemistry", {})
    compound_sev = chem.get("compound_severity")
    if compound_sev is not None and compound_sev > 0:
        s = max(0.0, min(1.0, compound_sev))
        components["chemistry_severity"] = {
            "raw": round(compound_sev, 4),
            "score": round(s, 4),
        }
        scores.append(s)

    if not scores:
        return UNKNOWN, {"status": "no_data", "components": {}}

    i_sym = sum(scores) / len(scores)
    return round(i_sym, 4), {"components": components}


def _compute_i_bound(full_output: dict) -> tuple[float, dict]:
    """Boundary Incoherence: layer violations, compartment compliance.

    Sources (active -- data provided by pipeline):
    - architecture.layer_violations: list of violations
    - rpbl_profile: RPBL dimension scores [0, 10]

    Sources (planned -- boundary_validation stage not yet implemented):
    - boundary_validation.compliance_score: [0, 10] (high=good)
    - boundary_validation.validation.violation_count: count
    - boundary_validation.validation.compliance_rate: [0, 1]
    NOTE: These 3 components gracefully degrade to UNKNOWN (0.5) until
    a dedicated boundary validation stage populates full_output['boundary_validation'].
    This is NOT the same as codome_boundary (Stage 6.8), which is graph visualization.
    """
    bv = full_output.get("boundary_validation", {})
    arch = full_output.get("architecture", {})
    kpis = full_output.get("kpis", {})
    rpbl = full_output.get("rpbl_profile", {})

    compliance = bv.get("compliance_score")
    validation = bv.get("validation", {})
    violation_count = validation.get("violation_count") if isinstance(validation, dict) else None
    compliance_rate = validation.get("compliance_rate") if isinstance(validation, dict) else None
    layer_violations = arch.get("layer_violations", [])
    rho_am = kpis.get("rho_antimatter")

    components = {}
    scores = []

    if compliance is not None:
        # compliance_score is 0-10, high=good
        s = _inv_sigmoid(compliance, midpoint=7.0, steepness=1.5)
        components["compliance_score"] = {"raw": compliance, "score": round(s, 4)}
        scores.append(s)
    if compliance_rate is not None:
        # 0-1, high=good
        s = 1.0 - max(0.0, min(1.0, compliance_rate))
        components["compliance_rate"] = {"raw": compliance_rate, "score": round(s, 4)}
        scores.append(s)
    if violation_count is not None:
        total_edges = kpis.get("edges_total", 1000)
        viol_density = violation_count / max(total_edges, 1)
        s = _sigmoid(viol_density, midpoint=0.02, steepness=100.0)
        components["violation_density"] = {"raw": violation_count, "density": round(viol_density, 6), "score": round(s, 4)}
        scores.append(s)
    if isinstance(layer_violations, list) and layer_violations:
        total_edges = kpis.get("edges_total", 1000)
        lv_density = len(layer_violations) / max(total_edges, 1)
        s = _sigmoid(lv_density, midpoint=0.01, steepness=150.0)
        components["layer_violations"] = {"count": len(layer_violations), "density": round(lv_density, 6), "score": round(s, 4)}
        scores.append(s)
    if rpbl and isinstance(rpbl, dict):
        # Average RPBL score, invert (high=good)
        rpbl_values = [v for v in rpbl.values() if isinstance(v, (int, float))]
        if rpbl_values:
            avg_rpbl = sum(rpbl_values) / len(rpbl_values)
            s = _inv_sigmoid(avg_rpbl, midpoint=5.0, steepness=0.8)
            components["rpbl_average"] = {"raw": round(avg_rpbl, 2), "score": round(s, 4)}
            scores.append(s)

    if not scores:
        return UNKNOWN, {"status": "no_data", "components": {}}

    i_bound = sum(scores) / len(scores)
    # Apply chemistry modulation
    mod = _chem_mod(full_output, "i_bound")
    if mod != 1.0:
        i_bound = min(1.0, i_bound / mod)
    return round(i_bound, 4), {"components": components}


def _compute_i_flow(full_output: dict) -> tuple[float, dict]:
    """Flow Incoherence: complexity, fan-out, topology shape, bottlenecks.

    Sources:
    - kpis.avg_fanout: average outgoing edges per node
    - topology.visual_metrics.centralization_score: [0, 1]
    - topology.visual_metrics.density_score: [0, ~20]
    - topology.visual_metrics.largest_cluster_percent: [0, 100]
    - kpis.topology_shape: enum string
    - kpis.graph_density: [0, 1]
    - performance.hotspot_count: count (if available)
    """
    kpis = full_output.get("kpis", {})
    topo = full_output.get("topology", {})
    vm = topo.get("visual_metrics", {}) if isinstance(topo, dict) else {}
    perf = full_output.get("performance", {})

    avg_fanout = kpis.get("avg_fanout")
    centralization = vm.get("centralization_score") if isinstance(vm, dict) else None
    density_score = vm.get("density_score") if isinstance(vm, dict) else None
    largest_cluster = vm.get("largest_cluster_percent") if isinstance(vm, dict) else None
    shape = kpis.get("topology_shape")
    hotspots = perf.get("hotspot_count") if isinstance(perf, dict) else None

    components = {}
    scores = []

    if avg_fanout is not None:
        s = _sigmoid(avg_fanout, midpoint=5.0, steepness=0.5)
        components["avg_fanout"] = {"raw": avg_fanout, "score": round(s, 4)}
        scores.append(s)
    if centralization is not None:
        # High centralization = bad (bottleneck risk)
        s = _sigmoid(centralization, midpoint=0.3, steepness=6.0)
        components["centralization"] = {"raw": centralization, "score": round(s, 4)}
        scores.append(s)
    if shape is not None:
        s = _SHAPE_INCOHERENCE.get(str(shape).upper(), UNKNOWN)
        components["topology_shape"] = {"raw": shape, "score": round(s, 4)}
        scores.append(s)
    if largest_cluster is not None:
        # Very high cluster % can indicate monolith (bad) but very low = fragmented (also bad)
        # Sweet spot around 60-80%
        s = _piecewise(largest_cluster, [0, 30, 60, 80, 95, 100], [0.8, 0.4, 0.1, 0.15, 0.5, 0.7])
        components["cluster_dominance"] = {"raw": largest_cluster, "score": round(s, 4)}
        scores.append(s)
    if hotspots is not None:
        total = kpis.get("nodes_total", 1000)
        hotspot_ratio = hotspots / max(total, 1)
        s = _sigmoid(hotspot_ratio, midpoint=0.05, steepness=30.0)
        components["hotspot_density"] = {"raw": hotspots, "ratio": round(hotspot_ratio, 4), "score": round(s, 4)}
        scores.append(s)

    if not scores:
        return UNKNOWN, {"status": "no_data", "components": {}}

    i_flow = sum(scores) / len(scores)
    # Apply chemistry modulation
    mod = _chem_mod(full_output, "i_flow")
    if mod != 1.0:
        i_flow = min(1.0, i_flow / mod)
    return round(i_flow, 4), {"components": components}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_incoherence(
    full_output: dict,
    weights: Optional[Dict[str, float]] = None,
) -> IncoherenceResult:
    """Compute the Incoherence Functional I(C) from Collider full_output.

    Args:
        full_output: The unified analysis dict from Collider.
        weights: Optional weight overrides. Keys: struct, telic, sym, bound, flow.
                 Must sum to 1.0.

    Returns:
        IncoherenceResult with all five I-terms, total, and health score.
    """
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)

    # Normalize weights to sum to 1.0
    total_w = sum(w.values())
    if total_w > 0:
        w = {k: v / total_w for k, v in w.items()}

    # Compute each I-term
    i_struct, d_struct = _compute_i_struct(full_output)
    i_telic, d_telic = _compute_i_telic(full_output)
    i_sym, d_sym = _compute_i_sym(full_output)
    i_bound, d_bound = _compute_i_bound(full_output)
    i_flow, d_flow = _compute_i_flow(full_output)

    # Weighted sum
    i_total = (
        w["struct"] * i_struct
        + w["telic"] * i_telic
        + w["sym"] * i_sym
        + w["bound"] * i_bound
        + w["flow"] * i_flow
    )
    i_total = round(max(0.0, min(1.0, i_total)), 4)

    health_10 = round(10.0 * (1.0 - i_total), 2)

    details = {
        "weights": {k: round(v, 4) for k, v in w.items()},
        "terms": {
            "struct": d_struct,
            "telic": d_telic,
            "sym": d_sym,
            "bound": d_bound,
            "flow": d_flow,
        },
    }

    return IncoherenceResult(
        i_struct=i_struct,
        i_telic=i_telic,
        i_sym=i_sym,
        i_bound=i_bound,
        i_flow=i_flow,
        i_total=i_total,
        health_10=health_10,
        details=details,
    )
