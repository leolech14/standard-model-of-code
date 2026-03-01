"""
Tests for the Architectural Diff Engine (Feature 2).

Validates:
- Grade and score diffing
- Node addition/removal/modification detection
- Edge diffing
- Cycle resolution and detection
- Coupling change detection
- Level distribution changes
- Boundary compliance diffing
- Summary generation
- Edge cases (empty snapshots, identical snapshots)
"""

import pytest
import sys
from pathlib import Path

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from arch_diff import (
    compute_arch_diff,
    format_diff_markdown,
    _diff_grade,
    _diff_score,
    _diff_health_components,
    _diff_nodes,
    _diff_edges,
    _diff_coupling,
    _diff_cycles,
    _diff_levels,
    _diff_boundaries,
    _diff_kpis,
    _generate_summary,
)


# =============================================================================
# FIXTURES: Minimal valid analysis snapshots
# =============================================================================

def _make_snapshot(
    nodes=None,
    edges=None,
    grade="C",
    health_score=5.5,
    health_components=None,
    levels=None,
    kpis=None,
    knots=None,
    boundary_validation=None,
    target="test_project",
    timestamp="2026-01-01T00:00:00",
):
    """Create a minimal analysis snapshot for testing."""
    if health_components is None:
        health_components = {
            "topology": 6.0,
            "constraints": 8.0,
            "purpose": 5.0,
            "test_coverage": 5.0,
            "dead_code": 7.0,
            "entanglement": 6.0,
            "rpbl_balance": 6.0,
        }
    if levels is None:
        levels = {"L3": 100, "L4": 20, "L5": 15}
    if kpis is None:
        kpis = {
            "nodes_total": sum(levels.values()),
            "edges_total": len(edges) if edges else 0,
            "dead_code_percent": 5.0,
            "knot_score": 0,
            "cycles_detected": 0,
        }
    if knots is None:
        knots = {"cycles_detected": 0, "knot_score": 0, "cycles": []}

    snap = {
        "meta": {
            "target": target,
            "timestamp": timestamp,
            "version": "4.0.0",
        },
        "nodes": nodes or [],
        "edges": edges or [],
        "compiled_insights": {
            "grade": grade,
            "health_score": health_score,
            "health_components": health_components,
        },
        "distributions": {
            "levels": levels,
        },
        "kpis": kpis,
        "knots": knots,
    }

    if boundary_validation is not None:
        snap["boundary_validation"] = boundary_validation

    return snap


# =============================================================================
# IDENTICAL SNAPSHOTS
# =============================================================================

class TestIdenticalSnapshots:
    """When before == after, all deltas should be zero."""

    def test_identical_produces_zero_deltas(self):
        nodes = [
            {"id": "a:func:foo", "name": "foo", "kind": "function", "level": "L3"},
            {"id": "b:class:Bar", "name": "Bar", "kind": "class", "level": "L4"},
        ]
        edges = [
            {"source": "b:class:Bar", "target": "a:func:foo", "edge_type": "contains"},
        ]
        snap = _make_snapshot(nodes=nodes, edges=edges, grade="B", health_score=7.5)

        diff = compute_arch_diff(snap, snap)

        assert diff["grade_delta"]["direction"] == "unchanged"
        assert diff["score_delta"]["delta"] == 0
        assert diff["node_changes"]["added_count"] == 0
        assert diff["node_changes"]["removed_count"] == 0
        assert diff["node_changes"]["modified_count"] == 0
        assert diff["edge_changes"]["net_change"] == 0
        assert diff["cycle_changes"]["delta"] == 0


# =============================================================================
# GRADE DIFFING
# =============================================================================

class TestGradeDiffing:
    """Test grade comparison logic."""

    def test_grade_improvement(self):
        before = _make_snapshot(grade="C", health_score=5.5)
        after = _make_snapshot(grade="A", health_score=8.8)

        diff = compute_arch_diff(before, after)

        assert diff["grade_delta"]["before"] == "C"
        assert diff["grade_delta"]["after"] == "A"
        assert diff["grade_delta"]["direction"] == "improved"
        assert diff["grade_delta"]["steps"] == 2  # C(3) -> A(5) = +2

    def test_grade_regression(self):
        before = _make_snapshot(grade="A", health_score=9.0)
        after = _make_snapshot(grade="D", health_score=4.2)

        diff = compute_arch_diff(before, after)

        assert diff["grade_delta"]["direction"] == "regressed"
        assert diff["grade_delta"]["steps"] == -3  # A(5) -> D(2) = -3

    def test_grade_unchanged(self):
        before = _make_snapshot(grade="B", health_score=7.0)
        after = _make_snapshot(grade="B", health_score=7.5)

        diff = compute_arch_diff(before, after)

        assert diff["grade_delta"]["direction"] == "unchanged"
        assert diff["grade_delta"]["steps"] == 0


# =============================================================================
# SCORE DIFFING
# =============================================================================

class TestScoreDiffing:
    """Test health score comparison."""

    def test_score_improvement(self):
        before = _make_snapshot(health_score=6.0)
        after = _make_snapshot(health_score=8.0)

        diff = compute_arch_diff(before, after)

        assert diff["score_delta"]["before"] == 6.0
        assert diff["score_delta"]["after"] == 8.0
        assert diff["score_delta"]["delta"] == 2.0
        assert diff["score_delta"]["direction"] == "improved"

    def test_score_regression(self):
        before = _make_snapshot(health_score=8.0)
        after = _make_snapshot(health_score=5.0)

        diff = compute_arch_diff(before, after)

        assert diff["score_delta"]["delta"] == -3.0
        assert diff["score_delta"]["direction"] == "regressed"


# =============================================================================
# NODE DIFFING
# =============================================================================

class TestNodeDiffing:
    """Test node addition, removal, and modification detection."""

    def test_node_additions(self):
        before = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L3"},
        ])
        after = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L3"},
            {"id": "b", "name": "b", "kind": "class", "level": "L4"},
            {"id": "c", "name": "c", "kind": "module", "level": "L5"},
        ])

        diff = compute_arch_diff(before, after)
        nc = diff["node_changes"]

        assert nc["added_count"] == 2
        assert nc["removed_count"] == 0
        assert nc["unchanged_count"] == 1
        assert "b" in nc["added_ids"]
        assert "c" in nc["added_ids"]
        assert nc["added_by_level"]["L4"] == 1
        assert nc["added_by_level"]["L5"] == 1

    def test_node_removals(self):
        before = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L3"},
            {"id": "b", "name": "b", "kind": "class", "level": "L4"},
        ])
        after = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L3"},
        ])

        diff = compute_arch_diff(before, after)
        nc = diff["node_changes"]

        assert nc["removed_count"] == 1
        assert nc["added_count"] == 0
        assert "b" in nc["removed_ids"]
        assert nc["removed_by_level"]["L4"] == 1

    def test_node_modification(self):
        before = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L3", "tier": "T1"},
        ])
        after = _make_snapshot(nodes=[
            {"id": "a", "name": "a", "kind": "function", "level": "L4", "tier": "T2"},
        ])

        diff = compute_arch_diff(before, after)
        nc = diff["node_changes"]

        assert nc["modified_count"] == 1
        assert nc["modified"][0]["id"] == "a"
        assert nc["modified"][0]["changes"]["level"]["before"] == "L3"
        assert nc["modified"][0]["changes"]["level"]["after"] == "L4"
        assert nc["modified"][0]["changes"]["tier"]["before"] == "T1"
        assert nc["modified"][0]["changes"]["tier"]["after"] == "T2"


# =============================================================================
# EDGE DIFFING
# =============================================================================

class TestEdgeDiffing:
    """Test edge change detection."""

    def test_new_edges(self):
        before = _make_snapshot(edges=[
            {"source": "a", "target": "b", "edge_type": "calls"},
        ])
        after = _make_snapshot(edges=[
            {"source": "a", "target": "b", "edge_type": "calls"},
            {"source": "a", "target": "c", "edge_type": "calls"},
            {"source": "b", "target": "c", "edge_type": "imports"},
        ])

        diff = compute_arch_diff(before, after)
        ec = diff["edge_changes"]

        assert ec["added_count"] == 2
        assert ec["removed_count"] == 0
        assert ec["net_change"] == 2
        assert ec["added_by_type"]["calls"] == 1
        assert ec["added_by_type"]["imports"] == 1

    def test_removed_edges(self):
        before = _make_snapshot(edges=[
            {"source": "a", "target": "b", "edge_type": "calls"},
            {"source": "a", "target": "c", "edge_type": "calls"},
        ])
        after = _make_snapshot(edges=[
            {"source": "a", "target": "b", "edge_type": "calls"},
        ])

        diff = compute_arch_diff(before, after)
        ec = diff["edge_changes"]

        assert ec["removed_count"] == 1
        assert ec["net_change"] == -1


# =============================================================================
# CYCLE DIFFING
# =============================================================================

class TestCycleDiffing:
    """Test cycle resolution and detection."""

    def test_cycle_resolution(self):
        """Cycle in before, gone in after."""
        before = _make_snapshot(knots={
            "cycles_detected": 1,
            "knot_score": 3,
            "cycles": [["a", "b", "c"]],
        })
        after = _make_snapshot(knots={
            "cycles_detected": 0,
            "knot_score": 0,
            "cycles": [],
        })

        diff = compute_arch_diff(before, after)
        cc = diff["cycle_changes"]

        assert cc["before_count"] == 1
        assert cc["after_count"] == 0
        assert cc["resolved_count"] == 1
        assert cc["new_count"] == 0
        assert cc["knot_score_delta"] == -3

    def test_new_cycle_detection(self):
        """No cycle before, cycle after."""
        before = _make_snapshot(knots={
            "cycles_detected": 0,
            "knot_score": 0,
            "cycles": [],
        })
        after = _make_snapshot(knots={
            "cycles_detected": 2,
            "knot_score": 5,
            "cycles": [["x", "y"], ["p", "q", "r"]],
        })

        diff = compute_arch_diff(before, after)
        cc = diff["cycle_changes"]

        assert cc["new_count"] == 2
        assert cc["resolved_count"] == 0
        assert cc["delta"] == 2

    def test_persistent_cycles(self):
        """Same cycle in both snapshots."""
        knots = {
            "cycles_detected": 1,
            "knot_score": 2,
            "cycles": [["a", "b"]],
        }
        before = _make_snapshot(knots=knots)
        after = _make_snapshot(knots=knots)

        diff = compute_arch_diff(before, after)
        cc = diff["cycle_changes"]

        assert cc["persistent_count"] == 1
        assert cc["new_count"] == 0
        assert cc["resolved_count"] == 0


# =============================================================================
# COUPLING DIFFING
# =============================================================================

class TestCouplingDiffing:
    """Test coupling change detection."""

    def test_coupling_increase(self):
        """Fan-in increase should be detected."""
        before = _make_snapshot(edges=[
            {"source": "a", "target": "hub", "edge_type": "calls"},
        ])
        after = _make_snapshot(edges=[
            {"source": "a", "target": "hub", "edge_type": "calls"},
            {"source": "b", "target": "hub", "edge_type": "calls"},
            {"source": "c", "target": "hub", "edge_type": "calls"},
        ])

        diff = compute_arch_diff(before, after)
        cp = diff["coupling_changes"]

        assert cp["nodes_with_coupling_changes"] > 0
        # Find 'hub' in the top changes
        hub_change = next((c for c in cp["top_changes"] if c["id"] == "hub"), None)
        assert hub_change is not None
        assert hub_change["fan_in"]["delta"] == 2  # 1 -> 3


# =============================================================================
# LEVEL DISTRIBUTION DIFFING
# =============================================================================

class TestLevelDiffing:
    """Test level distribution comparison."""

    def test_level_changes(self):
        before = _make_snapshot(levels={"L3": 100, "L4": 20, "L5": 15})
        after = _make_snapshot(levels={"L3": 120, "L4": 20, "L5": 18, "L6": 3})

        diff = compute_arch_diff(before, after)
        lc = diff["level_distribution_changes"]

        assert lc["per_level"]["L3"]["delta"] == 20
        assert lc["per_level"]["L4"]["delta"] == 0
        assert lc["per_level"]["L5"]["delta"] == 3
        assert lc["per_level"]["L6"]["delta"] == 3
        assert lc["total_delta"] == 26


# =============================================================================
# BOUNDARY DIFFING
# =============================================================================

class TestBoundaryDiffing:
    """Test boundary compliance comparison."""

    def test_no_boundaries_returns_none(self):
        before = _make_snapshot()
        after = _make_snapshot()

        diff = compute_arch_diff(before, after)
        assert diff["boundary_changes"] is None

    def test_boundary_compliance_change(self):
        before = _make_snapshot(boundary_validation={
            "compliance_rate": 0.85,
            "violation_count": 15,
        })
        after = _make_snapshot(boundary_validation={
            "compliance_rate": 0.95,
            "violation_count": 5,
        })

        diff = compute_arch_diff(before, after)
        bc = diff["boundary_changes"]

        assert bc is not None
        assert bc["compliance_rate"]["delta"] == pytest.approx(0.10, abs=0.001)
        assert bc["violations"]["delta"] == -10

    def test_boundary_added_in_after(self):
        before = _make_snapshot()
        after = _make_snapshot(boundary_validation={
            "compliance_rate": 0.90,
            "violation_count": 10,
        })

        diff = compute_arch_diff(before, after)
        bc = diff["boundary_changes"]

        assert bc is not None
        assert bc["before_present"] is False
        assert bc["after_present"] is True


# =============================================================================
# EMPTY / INITIAL ANALYSIS
# =============================================================================

class TestEdgeCases:
    """Test edge cases: empty snapshots, initial analysis."""

    def test_empty_before(self):
        """First analysis — everything is 'added'."""
        before = _make_snapshot(nodes=[], edges=[], grade="?", health_score=0.0, levels={})
        after = _make_snapshot(
            nodes=[
                {"id": "a", "name": "a", "kind": "function", "level": "L3"},
                {"id": "b", "name": "b", "kind": "class", "level": "L4"},
            ],
            edges=[{"source": "a", "target": "b", "edge_type": "calls"}],
            grade="B",
            health_score=7.0,
            levels={"L3": 1, "L4": 1},
        )

        diff = compute_arch_diff(before, after)

        assert diff["node_changes"]["added_count"] == 2
        assert diff["node_changes"]["removed_count"] == 0
        assert diff["edge_changes"]["added_count"] == 1

    def test_empty_after(self):
        """Project deleted — everything is 'removed'."""
        before = _make_snapshot(
            nodes=[{"id": "a", "name": "a", "kind": "function", "level": "L3"}],
            edges=[],
            levels={"L3": 1},
        )
        after = _make_snapshot(nodes=[], edges=[], grade="?", health_score=0.0, levels={})

        diff = compute_arch_diff(before, after)

        assert diff["node_changes"]["removed_count"] == 1
        assert diff["node_changes"]["added_count"] == 0


# =============================================================================
# SUMMARY GENERATION
# =============================================================================

class TestSummaryGeneration:
    """Test natural language summary output."""

    def test_summary_includes_grade_change(self):
        before = _make_snapshot(grade="C", health_score=5.5)
        after = _make_snapshot(grade="A", health_score=8.8)

        diff = compute_arch_diff(before, after)
        summary = diff["summary"]

        assert "improved" in summary.lower()
        assert "C" in summary
        assert "A" in summary

    def test_summary_includes_new_cycles_warning(self):
        before = _make_snapshot(knots={"cycles_detected": 0, "knot_score": 0, "cycles": []})
        after = _make_snapshot(knots={"cycles_detected": 2, "knot_score": 4, "cycles": [["a", "b"], ["c", "d"]]})

        diff = compute_arch_diff(before, after)
        summary = diff["summary"]

        assert "NEW CYCLES" in summary


# =============================================================================
# MARKDOWN FORMAT
# =============================================================================

class TestMarkdownFormat:
    """Test Markdown report generation."""

    def test_markdown_output_is_string(self):
        before = _make_snapshot(grade="B", health_score=7.0)
        after = _make_snapshot(grade="A", health_score=8.5)
        diff = compute_arch_diff(before, after)

        md = format_diff_markdown(diff)

        assert isinstance(md, str)
        assert "# Architectural Diff Report" in md
        assert "## Summary" in md
        assert "## Grade & Health" in md


# =============================================================================
# KPI DIFFING
# =============================================================================

class TestKpiDiffing:
    """Test KPI comparison."""

    def test_numeric_kpi_delta(self):
        before = _make_snapshot(kpis={"nodes_total": 100, "dead_code_percent": 5.0})
        after = _make_snapshot(kpis={"nodes_total": 120, "dead_code_percent": 3.0})

        diff = compute_arch_diff(before, after)
        kd = diff["kpi_changes"]

        assert kd["nodes_total"]["delta"] == 20
        assert kd["dead_code_percent"]["delta"] == pytest.approx(-2.0)

    def test_non_numeric_kpi_change(self):
        before = _make_snapshot(kpis={"topology_shape": "MESH"})
        after = _make_snapshot(kpis={"topology_shape": "STRICT_LAYERS"})

        diff = compute_arch_diff(before, after)
        kd = diff["kpi_changes"]

        assert kd["topology_shape"]["before"] == "MESH"
        assert kd["topology_shape"]["after"] == "STRICT_LAYERS"
        assert kd["topology_shape"]["changed"] is True


# =============================================================================
# HEALTH COMPONENT DIFFING
# =============================================================================

class TestHealthComponentDiffing:
    """Test per-component health score comparison."""

    def test_component_improvement(self):
        before_comps = {"topology": 4.0, "constraints": 6.0, "purpose": 5.0}
        after_comps = {"topology": 8.0, "constraints": 6.0, "purpose": 7.0}

        before = _make_snapshot(health_components=before_comps)
        after = _make_snapshot(health_components=after_comps)

        diff = compute_arch_diff(before, after)
        hd = diff["health_components_delta"]

        assert "topology" in hd["improved"]
        assert "purpose" in hd["improved"]
        assert "constraints" in hd["unchanged"]
        assert hd["components"]["topology"]["delta"] == 4.0
