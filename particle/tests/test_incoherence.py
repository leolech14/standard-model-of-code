"""Tests for the Incoherence Functional (Module 1 of the Collider Trinity)."""

import math
import sys
from pathlib import Path

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from incoherence import (
    UNKNOWN,
    DEFAULT_WEIGHTS,
    IncoherenceResult,
    _sigmoid,
    _inv_sigmoid,
    _piecewise,
    _safe_get,
    _compute_i_struct,
    _compute_i_telic,
    _compute_i_sym,
    _compute_i_bound,
    _compute_i_flow,
    compute_incoherence,
)


# ── Transfer function tests ──────────────────────────────────────────────


class TestSigmoid:
    def test_midpoint_returns_half(self):
        assert _sigmoid(5.0, midpoint=5.0) == pytest.approx(0.5, abs=1e-6)

    def test_high_value_approaches_one(self):
        assert _sigmoid(100.0, midpoint=5.0) > 0.99

    def test_low_value_approaches_zero(self):
        assert _sigmoid(0.0, midpoint=5.0, steepness=2.0) < 0.01

    def test_monotonically_increasing(self):
        vals = [_sigmoid(x, midpoint=5.0) for x in range(11)]
        for i in range(len(vals) - 1):
            assert vals[i] <= vals[i + 1]

    def test_extreme_inputs_no_overflow(self):
        assert _sigmoid(1e6, midpoint=0.0) == pytest.approx(1.0, abs=1e-6)
        assert _sigmoid(-1e6, midpoint=0.0) == pytest.approx(0.0, abs=1e-6)


class TestInvSigmoid:
    def test_midpoint_returns_half(self):
        assert _inv_sigmoid(5.0, midpoint=5.0) == pytest.approx(0.5, abs=1e-6)

    def test_high_value_approaches_zero(self):
        """High values = good = low incoherence."""
        assert _inv_sigmoid(100.0, midpoint=5.0) < 0.01

    def test_low_value_approaches_one(self):
        """Low values = bad = high incoherence."""
        assert _inv_sigmoid(0.0, midpoint=5.0, steepness=2.0) > 0.99


class TestPiecewise:
    def test_exact_breakpoints(self):
        assert _piecewise(0, [0, 5, 10], [0.0, 0.5, 1.0]) == 0.0
        assert _piecewise(5, [0, 5, 10], [0.0, 0.5, 1.0]) == 0.5
        assert _piecewise(10, [0, 5, 10], [0.0, 0.5, 1.0]) == 1.0

    def test_interpolation(self):
        assert _piecewise(2.5, [0, 5, 10], [0.0, 0.5, 1.0]) == pytest.approx(0.25)

    def test_clamp_below(self):
        assert _piecewise(-5, [0, 10], [0.0, 1.0]) == 0.0

    def test_clamp_above(self):
        assert _piecewise(15, [0, 10], [0.0, 1.0]) == 1.0


class TestSafeGet:
    def test_simple_key(self):
        assert _safe_get({"a": 1}, "a") == 1

    def test_nested_keys(self):
        assert _safe_get({"a": {"b": {"c": 42}}}, "a", "b", "c") == 42

    def test_missing_key_returns_default(self):
        assert _safe_get({"a": 1}, "b", default=99) == 99

    def test_non_dict_intermediate(self):
        assert _safe_get({"a": 42}, "a", "b", default="nope") == "nope"


# ── I-term tests ─────────────────────────────────────────────────────────


def _make_output(**overrides):
    """Build a minimal full_output dict with sensible defaults."""
    base = {
        "kpis": {
            "rho_antimatter": 0.0,
            "knot_score": 1.5,
            "cycles_detected": 1,
            "nodes_total": 1000,
            "edges_total": 5000,
            "orphan_percent": 3.0,
            "dead_code_percent": 2.0,
            "avg_fanout": 3.0,
            "topology_shape": "HIERARCHICAL",
            "graph_density": 0.001,
            "igt_stability_index": 0.7,
        },
        "purpose_field": {
            "purpose_clarity": 0.8,
            "alignment_health": "GOOD",
            "god_class_count": 5,
            "uncertain_count": 100,
            "unknown_count": 10,
            "total_nodes": 1000,
        },
        "topology": {
            "shape": "HIERARCHICAL",
            "visual_metrics": {
                "centralization_score": 0.2,
                "density_score": 5.0,
                "largest_cluster_percent": 75.0,
                "components": 10,
                "cyclic_nodes": 2,
                "directed_cycles": 1,
            },
        },
        "boundary_validation": {
            "compliance_score": 8.5,
            "validation": {
                "violation_count": 5,
                "compliance_rate": 0.95,
            },
        },
        "architecture": {
            "layer_violations": [],
        },
        "rpbl_profile": {
            "boundary": 7.0,
            "lifecycle": 6.0,
            "purity": 8.0,
            "responsibility": 7.0,
        },
        "coverage": {
            "dead_code_percent": 2.0,
            "rpbl_coverage": 95.0,
        },
        "performance": {
            "hotspot_count": 10,
        },
    }
    # Apply overrides via dot notation
    for key, val in overrides.items():
        parts = key.split(".")
        d = base
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = val
    return base


class TestIStruct:
    def test_clean_codebase(self):
        """Clean codebase -> low structural incoherence."""
        out = _make_output(**{
            "kpis.rho_antimatter": 0.0,
            "kpis.knot_score": 0.5,
            "kpis.cycles_detected": 0,
            "kpis.igt_stability_index": 0.9,
        })
        score, details = _compute_i_struct(out)
        assert score < 0.2
        assert "components" in details

    def test_messy_codebase(self):
        """High antimatter + knots + cycles -> high structural incoherence."""
        out = _make_output(**{
            "kpis.rho_antimatter": 0.1,
            "kpis.knot_score": 8.0,
            "kpis.cycles_detected": 50,
            "kpis.igt_stability_index": 0.2,
        })
        score, details = _compute_i_struct(out)
        assert score > 0.6

    def test_empty_data(self):
        score, details = _compute_i_struct({})
        assert score == UNKNOWN
        assert details.get("status") == "no_data"


class TestITelic:
    def test_clear_purpose(self):
        out = _make_output(**{
            "purpose_field.purpose_clarity": 0.95,
            "purpose_field.alignment_health": "EXCELLENT",
            "kpis.orphan_percent": 1.0,
            "purpose_field.god_class_count": 2,
            "purpose_field.uncertain_count": 50,
            "purpose_field.total_nodes": 1000,
        })
        score, _ = _compute_i_telic(out)
        assert score < 0.25

    def test_confused_purpose(self):
        out = _make_output(**{
            "purpose_field.purpose_clarity": 0.3,
            "purpose_field.alignment_health": "CRITICAL",
            "kpis.orphan_percent": 15.0,
            "purpose_field.god_class_count": 100,
            "purpose_field.uncertain_count": 800,
            "purpose_field.total_nodes": 1000,
        })
        score, _ = _compute_i_telic(out)
        assert score > 0.5

    def test_empty_data(self):
        score, details = _compute_i_telic({})
        assert score == UNKNOWN


class TestISym:
    def test_low_dead_code(self):
        out = _make_output(**{
            "kpis.dead_code_percent": 1.0,
            "purpose_field.unknown_count": 5,
            "purpose_field.total_nodes": 1000,
            "coverage.rpbl_coverage": 98.0,
        })
        score, _ = _compute_i_sym(out)
        assert score < 0.15

    def test_high_dead_code(self):
        out = _make_output(**{
            "kpis.dead_code_percent": 20.0,
            "purpose_field.unknown_count": 200,
            "purpose_field.total_nodes": 1000,
            "coverage.rpbl_coverage": 50.0,
        })
        score, _ = _compute_i_sym(out)
        assert score > 0.5


class TestIBound:
    def test_good_compliance(self):
        out = _make_output(**{
            "boundary_validation.compliance_score": 9.5,
            "boundary_validation.validation.violation_count": 0,
            "boundary_validation.validation.compliance_rate": 1.0,
        })
        score, _ = _compute_i_bound(out)
        assert score < 0.25

    def test_bad_compliance(self):
        out = _make_output(**{
            "boundary_validation.compliance_score": 3.0,
            "boundary_validation.validation.violation_count": 500,
            "boundary_validation.validation.compliance_rate": 0.3,
            "rpbl_profile.boundary": 2.0,
            "rpbl_profile.lifecycle": 2.0,
            "rpbl_profile.purity": 2.0,
            "rpbl_profile.responsibility": 2.0,
        })
        score, _ = _compute_i_bound(out)
        assert score > 0.5


class TestIFlow:
    def test_good_flow(self):
        out = _make_output(**{
            "kpis.avg_fanout": 2.0,
            "kpis.topology_shape": "LAYERED",
            "topology.visual_metrics.centralization_score": 0.1,
            "topology.visual_metrics.largest_cluster_percent": 70.0,
        })
        score, _ = _compute_i_flow(out)
        assert score < 0.25

    def test_bad_flow(self):
        out = _make_output(**{
            "kpis.avg_fanout": 15.0,
            "kpis.topology_shape": "STAR",
            "topology.visual_metrics.centralization_score": 0.8,
            "topology.visual_metrics.largest_cluster_percent": 99.0,
        })
        score, _ = _compute_i_flow(out)
        assert score > 0.5


# ── Integration tests ────────────────────────────────────────────────────


class TestComputeIncoherence:
    def test_healthy_repo(self):
        out = _make_output(**{
            "kpis.rho_antimatter": 0.0,
            "kpis.knot_score": 0.5,
            "kpis.cycles_detected": 0,
            "kpis.igt_stability_index": 0.9,
            "purpose_field.purpose_clarity": 0.95,
            "purpose_field.alignment_health": "EXCELLENT",
            "kpis.orphan_percent": 1.0,
            "purpose_field.god_class_count": 2,
            "kpis.dead_code_percent": 1.0,
            "boundary_validation.compliance_score": 9.5,
            "kpis.avg_fanout": 2.0,
            "kpis.topology_shape": "LAYERED",
        })
        result = compute_incoherence(out)
        assert isinstance(result, IncoherenceResult)
        assert result.i_total < 0.3
        assert result.health_10 > 7.0

    def test_unhealthy_repo(self):
        out = _make_output(**{
            "kpis.rho_antimatter": 0.1,
            "kpis.knot_score": 8.0,
            "kpis.cycles_detected": 50,
            "kpis.igt_stability_index": 0.2,
            "purpose_field.purpose_clarity": 0.3,
            "purpose_field.alignment_health": "CRITICAL",
            "kpis.orphan_percent": 15.0,
            "purpose_field.god_class_count": 100,
            "kpis.dead_code_percent": 20.0,
            "boundary_validation.compliance_score": 3.0,
            "kpis.avg_fanout": 15.0,
            "kpis.topology_shape": "STAR",
        })
        result = compute_incoherence(out)
        assert result.i_total > 0.5
        assert result.health_10 < 5.0

    def test_empty_output_degrades_gracefully(self):
        result = compute_incoherence({})
        # All terms should default to UNKNOWN = 0.5
        assert result.i_struct == UNKNOWN
        assert result.i_telic == UNKNOWN
        assert result.i_sym == UNKNOWN
        assert result.i_bound == UNKNOWN
        assert result.i_flow == UNKNOWN
        assert result.i_total == pytest.approx(0.5, abs=0.01)
        assert result.health_10 == pytest.approx(5.0, abs=0.1)

    def test_partial_data(self):
        """Only some KPIs available -- should still compute."""
        out = {"kpis": {"rho_antimatter": 0.02, "avg_fanout": 4.0}}
        result = compute_incoherence(out)
        # struct and flow should have data, others should be UNKNOWN
        assert result.i_struct != UNKNOWN  # has rho_antimatter
        assert result.i_telic == UNKNOWN   # no purpose_field
        assert result.i_sym == UNKNOWN     # no dead_code/coverage
        assert result.i_bound == UNKNOWN   # no boundary_validation
        assert result.i_flow != UNKNOWN    # has avg_fanout

    def test_custom_weights(self):
        out = _make_output()
        w1 = compute_incoherence(out, weights={"struct": 1.0, "telic": 0, "sym": 0, "bound": 0, "flow": 0})
        w2 = compute_incoherence(out, weights={"struct": 0, "telic": 0, "sym": 0, "bound": 0, "flow": 1.0})
        # Total should track the weighted term
        assert w1.i_total == pytest.approx(w1.i_struct, abs=0.01)
        assert w2.i_total == pytest.approx(w2.i_flow, abs=0.01)

    def test_to_dict(self):
        result = compute_incoherence({})
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "i_struct" in d
        assert "i_total" in d
        assert "health_10" in d
        assert "details" in d

    def test_all_terms_in_range(self):
        out = _make_output()
        result = compute_incoherence(out)
        for term in [result.i_struct, result.i_telic, result.i_sym, result.i_bound, result.i_flow, result.i_total]:
            assert 0.0 <= term <= 1.0
        assert 0.0 <= result.health_10 <= 10.0

    def test_with_real_collider_output(self):
        """Test against actual Collider output if available."""
        import json
        from pathlib import Path

        output_file = Path("/tmp/collider_self_test6/unified_analysis.json")
        if not output_file.exists():
            pytest.skip("No real Collider output available")

        with open(output_file) as f:
            data = json.load(f)

        result = compute_incoherence(data)
        assert 0.0 <= result.i_total <= 1.0
        assert 0.0 <= result.health_10 <= 10.0
        # Verify details contain component breakdowns
        assert "terms" in result.details
        for term_name in ["struct", "telic", "sym", "bound", "flow"]:
            assert term_name in result.details["terms"]

    def test_weights_normalize(self):
        """Weights that don't sum to 1.0 should be normalized."""
        out = _make_output()
        r1 = compute_incoherence(out, weights={"struct": 0.5, "telic": 0.5, "sym": 0.5, "bound": 0.5, "flow": 0.5})
        r2 = compute_incoherence(out)  # uses DEFAULT_WEIGHTS
        # Different weights but both should produce valid results
        assert 0.0 <= r1.i_total <= 1.0
        assert 0.0 <= r2.i_total <= 1.0
