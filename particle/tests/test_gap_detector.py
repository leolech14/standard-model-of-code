"""Tests for Gap Detection (Module 3 of the Collider Trinity)."""

import sys
from pathlib import Path

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from purpose_decomposition import (
    DecompositionResult,
    PurposeManifest,
    SubCompartment,
    decompose_node,
)
from gap_detector import (
    Gap,
    GapReport,
    GAP_TYPES,
    _gaps_from_decomposition,
    _detect_disconnections,
    _detect_orphan_clusters,
    _detect_purpose_vacuums,
    _prepare_query_targets,
    _compute_coverage,
    detect_gaps,
)


# ── Helper factories ──────────────────────────────────────────────────────


def _make_node(nid, role="Internal", parent="", compartment="core", **extra):
    """Build a minimal node dict."""
    node = {"id": nid, "role": role, "parent": parent, "compartment": compartment}
    node.update(extra)
    return node


def _make_decomposition(
    node_id="svc",
    purpose="Service",
    present=None,
    missing=None,
    gaps=None,
    violations=None,
    completeness=0.5,
):
    """Build a DecompositionResult with controlled fields."""
    return DecompositionResult(
        node_id=node_id,
        purpose=purpose,
        pi3_purpose="",
        compartment="core",
        child_count=0,
        manifest=PurposeManifest(purpose=purpose),
        present=present or [],
        missing=missing or [],
        gaps=gaps or [],
        violations=violations or [],
        completeness=completeness,
    )


# ── GAP_TYPES tests ──────────────────────────────────────────────────────


class TestGapTypes:
    def test_all_expected_types_present(self):
        expected = {
            "missing_required", "missing_expected", "forbidden_present",
            "orphan_cluster", "purpose_vacuum", "disconnection",
        }
        assert GAP_TYPES == expected

    def test_gap_types_is_set(self):
        assert isinstance(GAP_TYPES, set)


# ── Gap dataclass tests ──────────────────────────────────────────────────


class TestGapDataclass:
    def test_to_dict(self):
        g = Gap(
            location="svc",
            gap_type="missing_required",
            description="test",
            severity="critical",
            circumscribed=True,
            llm_query_hint="check this",
            context={"key": "val"},
        )
        d = g.to_dict()
        assert d["location"] == "svc"
        assert d["gap_type"] == "missing_required"
        assert d["severity"] == "critical"
        assert d["circumscribed"] is True
        assert d["context"] == {"key": "val"}

    def test_default_context(self):
        g = Gap(
            location="x", gap_type="disconnection",
            description="d", severity="low",
            circumscribed=True, llm_query_hint="",
        )
        assert g.context == {}


# ── _gaps_from_decomposition tests ────────────────────────────────────────


class TestGapsFromDecomposition:
    def test_no_decomposition_results(self):
        assert _gaps_from_decomposition([]) == []

    def test_perfect_decomposition_no_gaps(self):
        """Decomposition with no missing/gaps/violations -> no gaps."""
        dr = _make_decomposition(
            present=["Command", "Query"],
            missing=[],
            gaps=[],
            violations=[],
            completeness=1.0,
        )
        result = _gaps_from_decomposition([dr])
        assert result == []

    def test_missing_required_creates_critical_gap(self):
        dr = _make_decomposition(missing=["Command"])
        result = _gaps_from_decomposition([dr])
        assert len(result) == 1
        assert result[0].gap_type == "missing_required"
        assert result[0].severity == "critical"
        assert result[0].circumscribed is True
        assert "Command" in result[0].description
        assert "Command" in result[0].llm_query_hint.lower() or "command" in result[0].llm_query_hint.lower()

    def test_missing_expected_creates_medium_gap(self):
        dr = _make_decomposition(gaps=["Validator"])
        result = _gaps_from_decomposition([dr])
        assert len(result) == 1
        assert result[0].gap_type == "missing_expected"
        assert result[0].severity == "medium"
        assert result[0].circumscribed is True

    def test_forbidden_present_creates_high_gap(self):
        dr = _make_decomposition(violations=["Controller"])
        result = _gaps_from_decomposition([dr])
        assert len(result) == 1
        assert result[0].gap_type == "forbidden_present"
        assert result[0].severity == "high"
        assert result[0].circumscribed is True
        assert "Controller" in result[0].description

    def test_multiple_issues_in_single_node(self):
        dr = _make_decomposition(
            missing=["Command", "Query"],
            gaps=["Validator"],
            violations=["Controller"],
        )
        result = _gaps_from_decomposition([dr])
        # 2 missing_required + 1 missing_expected + 1 forbidden_present = 4
        assert len(result) == 4
        types = [g.gap_type for g in result]
        assert types.count("missing_required") == 2
        assert types.count("missing_expected") == 1
        assert types.count("forbidden_present") == 1

    def test_multiple_decomposition_results(self):
        dr1 = _make_decomposition(node_id="svc1", missing=["Command"])
        dr2 = _make_decomposition(node_id="svc2", violations=["View"])
        result = _gaps_from_decomposition([dr1, dr2])
        assert len(result) == 2
        locations = {g.location for g in result}
        assert locations == {"svc1", "svc2"}

    def test_context_includes_parent_purpose(self):
        dr = _make_decomposition(
            purpose="Repository",
            missing=["Query"],
            completeness=0.5,
        )
        result = _gaps_from_decomposition([dr])
        assert result[0].context["parent_purpose"] == "Repository"
        assert "completeness" in result[0].context


# ── _detect_disconnections tests ──────────────────────────────────────────


class TestDetectDisconnections:
    def test_empty_output(self):
        assert _detect_disconnections({}) == []

    def test_no_nodes(self):
        assert _detect_disconnections({"nodes": [], "edges": []}) == []

    def test_all_connected(self):
        """No isolated nodes -> no disconnections."""
        nodes = [_make_node("a"), _make_node("b"), _make_node("c")]
        edges = [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "c"},
        ]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        assert result == []

    def test_isolated_node_detected(self):
        """Node with no edges at all -> disconnection."""
        nodes = [_make_node("a"), _make_node("b"), _make_node("isolated")]
        edges = [{"source": "a", "target": "b"}]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        assert len(result) == 1
        assert result[0].location == "isolated"
        assert result[0].gap_type == "disconnection"
        assert result[0].severity == "low"
        assert result[0].circumscribed is True

    def test_incoming_only_not_isolated(self):
        """Node with only incoming edges is NOT isolated."""
        nodes = [_make_node("a"), _make_node("b")]
        edges = [{"source": "a", "target": "b"}]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        # 'a' is a source, 'b' is a target -- neither is truly isolated
        assert result == []

    def test_outgoing_only_not_isolated(self):
        """Node with only outgoing edges is NOT isolated."""
        nodes = [_make_node("a"), _make_node("b")]
        edges = [{"source": "a", "target": "b"}]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        assert result == []

    def test_multiple_isolated(self):
        nodes = [
            _make_node("a"), _make_node("b"),
            _make_node("iso1"), _make_node("iso2"),
        ]
        edges = [{"source": "a", "target": "b"}]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        assert len(result) == 2
        isolated_ids = {g.location for g in result}
        assert isolated_ids == {"iso1", "iso2"}

    def test_context_includes_role(self):
        nodes = [_make_node("iso", role="Utility")]
        edges = [{"source": "other", "target": "other2"}]  # iso not in edges
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        assert len(result) == 1
        assert result[0].context["role"] == "Utility"

    def test_empty_id_nodes_skipped(self):
        """Nodes with empty IDs should not generate gaps."""
        nodes = [{"id": "", "role": "Internal"}, _make_node("a")]
        edges = [{"source": "a", "target": "a"}]
        result = _detect_disconnections({"nodes": nodes, "edges": edges})
        # Empty ID node is technically isolated but should be skipped
        assert all(g.location != "" for g in result)


# ── _detect_orphan_clusters tests ─────────────────────────────────────────


class TestDetectOrphanClusters:
    def test_empty_output(self):
        assert _detect_orphan_clusters({}) == []

    def test_no_orphans(self):
        """All nodes have parents -> no orphan clusters."""
        nodes = [
            _make_node("p", role="Service"),
            _make_node("c1", parent="p"),
            _make_node("c2", parent="p"),
        ]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert result == []

    def test_below_threshold(self):
        """4 orphans in same compartment -> below threshold (5)."""
        nodes = [_make_node(f"n{i}", compartment="core") for i in range(4)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert result == []

    def test_at_threshold(self):
        """5 orphans in same compartment -> detected."""
        nodes = [_make_node(f"n{i}", compartment="core") for i in range(5)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert result[0].gap_type == "orphan_cluster"
        assert result[0].location == "core"
        assert result[0].severity == "medium"
        assert result[0].context["orphan_count"] == 5

    def test_above_threshold(self):
        """10 orphans -> detected with correct count."""
        nodes = [_make_node(f"n{i}", compartment="infra") for i in range(10)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert result[0].context["orphan_count"] == 10

    def test_multiple_compartments(self):
        """Orphan clusters in different compartments detected separately."""
        nodes = (
            [_make_node(f"a{i}", compartment="core") for i in range(6)]
            + [_make_node(f"b{i}", compartment="infra") for i in range(7)]
        )
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 2
        compartments = {g.location for g in result}
        assert compartments == {"core", "infra"}

    def test_mixed_orphans_and_parented(self):
        """Only parentless nodes count toward orphan clusters."""
        nodes = (
            [_make_node(f"orphan{i}", compartment="core") for i in range(6)]
            + [_make_node(f"child{i}", compartment="core", parent="parent") for i in range(10)]
        )
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert result[0].context["orphan_count"] == 6  # not 16

    def test_circumscribed_flag_large_cluster(self):
        """Clusters > 50 nodes are not circumscribed."""
        nodes = [_make_node(f"n{i}", compartment="big") for i in range(51)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert result[0].circumscribed is False

    def test_circumscribed_flag_small_cluster(self):
        """Clusters <= 50 nodes are circumscribed."""
        nodes = [_make_node(f"n{i}", compartment="small") for i in range(50)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert result[0].circumscribed is True

    def test_sample_ids_limited(self):
        """Sample IDs should be limited to 10."""
        nodes = [_make_node(f"n{i}", compartment="core") for i in range(20)]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result[0].context["sample_ids"]) == 10

    def test_roles_in_context(self):
        """Role diversity captured in context."""
        nodes = [
            _make_node("a", role="Service", compartment="core"),
            _make_node("b", role="Repository", compartment="core"),
            _make_node("c", role="Controller", compartment="core"),
            _make_node("d", role="Entity", compartment="core"),
            _make_node("e", role="Utility", compartment="core"),
        ]
        result = _detect_orphan_clusters({"nodes": nodes})
        assert len(result) == 1
        assert len(result[0].context["roles"]) == 5


# ── _detect_purpose_vacuums tests ─────────────────────────────────────────


class TestDetectPurposeVacuums:
    def test_empty_output(self):
        assert _detect_purpose_vacuums({}) == []

    def test_no_containers(self):
        """Nodes without children -> no vacuums."""
        nodes = [_make_node("a"), _make_node("b")]
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert result == []

    def test_focused_container_no_vacuum(self):
        """Container where one role dominates -> no vacuum."""
        nodes = [
            _make_node("parent", role="Service"),
            _make_node("c1", role="Command", parent="parent"),
            _make_node("c2", role="Command", parent="parent"),
            _make_node("c3", role="Command", parent="parent"),
            _make_node("c4", role="Query", parent="parent"),
        ]
        result = _detect_purpose_vacuums({"nodes": nodes})
        # Command = 3/4 = 75% > 30% threshold -> no vacuum
        assert result == []

    def test_scattered_container_is_vacuum(self):
        """Container where no role exceeds 30% with 4+ roles -> vacuum."""
        nodes = [
            _make_node("god", role="Service"),
            _make_node("c1", role="Command", parent="god"),
            _make_node("c2", role="Query", parent="god"),
            _make_node("c3", role="Validator", parent="god"),
            _make_node("c4", role="Transformer", parent="god"),
            _make_node("c5", role="Factory", parent="god"),
            _make_node("c6", role="Mapper", parent="god"),
            _make_node("c7", role="Controller", parent="god"),
        ]
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert len(result) == 1
        assert result[0].gap_type == "purpose_vacuum"
        assert result[0].severity == "medium"
        assert result[0].location == "god"

    def test_too_few_children_skipped(self):
        """Container with < 3 children -> not analyzed."""
        nodes = [
            _make_node("small", role="Service"),
            _make_node("c1", role="Command", parent="small"),
            _make_node("c2", role="Query", parent="small"),
        ]
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert result == []

    def test_few_roles_not_vacuum(self):
        """Container with scattered count but only 3 roles -> not vacuum (need 4+)."""
        nodes = [
            _make_node("mixed", role="Service"),
            _make_node("c1", role="Command", parent="mixed"),
            _make_node("c2", role="Query", parent="mixed"),
            _make_node("c3", role="Validator", parent="mixed"),
        ]
        # 3 roles, each ~33% -> max_share ~0.33 > 0.3 -> no vacuum
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert result == []

    def test_vacuum_context(self):
        """Vacuum context includes role distribution."""
        nodes = [
            _make_node("god"),
            _make_node("c1", role="A", parent="god"),
            _make_node("c2", role="B", parent="god"),
            _make_node("c3", role="C", parent="god"),
            _make_node("c4", role="D", parent="god"),
            _make_node("c5", role="E", parent="god"),
        ]
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert len(result) == 1
        ctx = result[0].context
        assert ctx["child_count"] == 5
        assert ctx["unique_roles"] == 5
        assert ctx["max_share"] < 0.3

    def test_circumscribed_always_true(self):
        """Purpose vacuums are always circumscribed."""
        nodes = [_make_node("god")] + [
            _make_node(f"c{i}", role=f"Role{i}", parent="god") for i in range(10)
        ]
        result = _detect_purpose_vacuums({"nodes": nodes})
        assert len(result) == 1
        assert result[0].circumscribed is True


# ── _prepare_query_targets tests ──────────────────────────────────────────


class TestPrepareQueryTargets:
    def test_empty_gaps(self):
        assert _prepare_query_targets([]) == []

    def test_circumscribed_gap_included(self):
        g = Gap(
            location="svc", gap_type="missing_required",
            description="d", severity="critical",
            circumscribed=True, llm_query_hint="check this",
            context={"key": "val"},
        )
        targets = _prepare_query_targets([g])
        assert len(targets) == 1
        assert targets[0]["location"] == "svc"
        assert targets[0]["query"] == "check this"
        assert targets[0]["severity"] == "critical"

    def test_non_circumscribed_excluded(self):
        g = Gap(
            location="big", gap_type="orphan_cluster",
            description="d", severity="medium",
            circumscribed=False, llm_query_hint="too broad",
        )
        targets = _prepare_query_targets([g])
        assert targets == []

    def test_sorted_by_severity(self):
        gaps = [
            Gap("a", "disconnection", "d", "low", True, "q"),
            Gap("b", "missing_required", "d", "critical", True, "q"),
            Gap("c", "forbidden_present", "d", "high", True, "q"),
            Gap("d", "missing_expected", "d", "medium", True, "q"),
        ]
        targets = _prepare_query_targets(gaps)
        severities = [t["severity"] for t in targets]
        assert severities == ["critical", "high", "medium", "low"]


# ── _compute_coverage tests ───────────────────────────────────────────────


class TestComputeCoverage:
    def test_empty_results(self):
        assert _compute_coverage([]) == 0.0

    def test_full_coverage(self):
        dr = _make_decomposition(
            present=["Command", "Query", "Validator", "Transformer"],
            missing=[],
            gaps=[],
        )
        coverage = _compute_coverage([dr])
        assert coverage == pytest.approx(1.0)

    def test_partial_coverage(self):
        dr = _make_decomposition(
            present=["Command"],
            missing=["Query"],
            gaps=["Validator"],
        )
        # present=1, missing=1, gaps=1 -> total_expected = 1+1+1 = 3, present=1
        coverage = _compute_coverage([dr])
        assert coverage == pytest.approx(1 / 3, abs=0.01)

    def test_zero_coverage(self):
        dr = _make_decomposition(
            present=[],
            missing=["Command", "Query"],
            gaps=["Validator"],
        )
        coverage = _compute_coverage([dr])
        assert coverage == pytest.approx(0.0)

    def test_multiple_results(self):
        dr1 = _make_decomposition(
            present=["Command", "Query"],
            missing=[],
            gaps=[],
        )
        dr2 = _make_decomposition(
            present=[],
            missing=["Command"],
            gaps=["Validator"],
        )
        # dr1: present=2, expected=2. dr2: present=0, expected=2.
        # Total present=2, total expected=4 -> 0.5
        coverage = _compute_coverage([dr1, dr2])
        assert coverage == pytest.approx(0.5)


# ── GapReport tests ──────────────────────────────────────────────────────


class TestGapReport:
    def test_to_dict(self):
        g = Gap("loc", "disconnection", "desc", "low", True, "hint")
        report = GapReport(
            gaps=[g],
            coverage=0.75,
            unknown_count=1,
            query_targets=[{"query": "test"}],
        )
        d = report.to_dict()
        assert d["coverage"] == 0.75
        assert d["unknown_count"] == 1
        assert len(d["gaps"]) == 1
        assert len(d["query_targets"]) == 1
        assert d["summary"]["total_gaps"] == 1
        assert "by_type" in d["summary"]
        assert "by_severity" in d["summary"]

    def test_empty_report(self):
        report = GapReport(gaps=[], coverage=1.0, unknown_count=0, query_targets=[])
        d = report.to_dict()
        assert d["summary"]["total_gaps"] == 0
        assert d["coverage"] == 1.0


# ── detect_gaps integration tests ─────────────────────────────────────────


class TestDetectGaps:
    def test_empty_everything(self):
        report = detect_gaps({}, [])
        assert report.gaps == []
        assert report.coverage == 0.0
        assert report.unknown_count == 0
        assert report.query_targets == []

    def test_only_decomposition_gaps(self):
        dr = _make_decomposition(
            missing=["Command"],
            gaps=["Validator"],
            violations=["Controller"],
        )
        report = detect_gaps({"nodes": [], "edges": []}, [dr])
        assert len(report.gaps) == 3
        types = {g.gap_type for g in report.gaps}
        assert types == {"missing_required", "missing_expected", "forbidden_present"}

    def test_only_graph_gaps(self):
        nodes = [_make_node("a"), _make_node("iso")]
        edges = [{"source": "a", "target": "a"}]
        report = detect_gaps({"nodes": nodes, "edges": edges}, [])
        # iso is disconnected
        assert len(report.gaps) >= 1
        assert any(g.gap_type == "disconnection" for g in report.gaps)

    def test_combined_strategies(self):
        """All four strategies produce gaps in one call."""
        # Setup: decomposition gap + isolated node + orphan cluster + purpose vacuum
        dr = _make_decomposition(missing=["Command"])

        nodes = (
            # Isolated node
            [_make_node("iso")]
            # Orphan cluster (6 orphans in 'orphan_comp')
            + [_make_node(f"o{i}", compartment="orphan_comp") for i in range(6)]
            # Purpose vacuum (container with 5 diverse children)
            + [_make_node("god")]
            + [_make_node(f"vc{i}", role=f"Role{i}", parent="god") for i in range(5)]
        )
        edges = [{"source": "god", "target": "vc0"}]  # god is connected, iso is not

        report = detect_gaps({"nodes": nodes, "edges": edges}, [dr])

        gap_types = {g.gap_type for g in report.gaps}
        assert "missing_required" in gap_types
        assert "disconnection" in gap_types
        assert "orphan_cluster" in gap_types
        assert "purpose_vacuum" in gap_types

    def test_gaps_sorted_by_severity(self):
        """Gaps should be sorted: critical, high, medium, low."""
        dr = _make_decomposition(
            missing=["Command"],       # critical
            violations=["Controller"],  # high
            gaps=["Validator"],         # medium
        )
        nodes = [_make_node("iso")]
        edges = [{"source": "other", "target": "other2"}]  # iso is disconnected (low)

        report = detect_gaps({"nodes": nodes, "edges": edges}, [dr])

        severities = [g.severity for g in report.gaps]
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for i in range(len(severities) - 1):
            assert severity_order[severities[i]] <= severity_order[severities[i + 1]]

    def test_query_targets_match_circumscribed(self):
        dr = _make_decomposition(missing=["Command", "Query"])
        report = detect_gaps({}, [dr])
        # Both gaps are circumscribed -> both should be in query_targets
        assert len(report.query_targets) == 2
        assert all(t["severity"] == "critical" for t in report.query_targets)

    def test_coverage_reflects_decomposition(self):
        dr = _make_decomposition(
            present=["Command"],
            missing=["Query"],
            gaps=[],
        )
        report = detect_gaps({}, [dr])
        # present=1, missing=1 -> coverage = 1/2 = 0.5
        assert report.coverage == pytest.approx(0.5)

    def test_unknown_count(self):
        dr = _make_decomposition(missing=["Command"])
        nodes = [_make_node("iso")]
        edges = [{"source": "x", "target": "y"}]
        report = detect_gaps({"nodes": nodes, "edges": edges}, [dr])
        # missing_required is circumscribed, disconnection is circumscribed
        circumscribed_count = sum(1 for g in report.gaps if g.circumscribed)
        assert report.unknown_count == circumscribed_count

    def test_entry_points_exempt_from_decomposition_gaps(self):
        """Entry points should be excluded from missing_required gaps."""
        dr = _make_decomposition(node_id="main_func", missing=["Command", "Query"])
        report = detect_gaps({}, [dr], entry_points={"main_func"})
        # Entry point gaps should be filtered out
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) == 0

    def test_non_entry_points_still_flagged(self):
        """Non-entry-point nodes should still produce gaps normally."""
        dr_entry = _make_decomposition(node_id="main_func", missing=["Command"])
        dr_normal = _make_decomposition(node_id="service", missing=["Query"])
        report = detect_gaps({}, [dr_entry, dr_normal], entry_points={"main_func"})
        # Only service should have a gap, not main_func
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) == 1
        assert missing_req[0].location == "service"

    def test_entry_points_none_backward_compat(self):
        """When entry_points is None (default), all gaps fire (backward compat)."""
        dr = _make_decomposition(node_id="main_func", missing=["Command"])
        report = detect_gaps({}, [dr])  # no entry_points arg
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) == 1

    def test_entry_points_empty_set(self):
        """Empty set of entry points = all gaps fire."""
        dr = _make_decomposition(node_id="main_func", missing=["Command"])
        report = detect_gaps({}, [dr], entry_points=set())
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) == 1

    def test_entry_points_dont_affect_other_strategies(self):
        """Entry point exemption only applies to decomposition, not disconnections."""
        dr = _make_decomposition(node_id="main_func", missing=["Command"])
        # main_func is also a disconnected node
        nodes = [_make_node("main_func"), _make_node("a")]
        edges = [{"source": "a", "target": "a"}]
        report = detect_gaps(
            {"nodes": nodes, "edges": edges}, [dr],
            entry_points={"main_func"},
        )
        # Decomposition gap should be filtered...
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) == 0
        # ...but disconnection should still fire
        disconnections = [g for g in report.gaps if g.gap_type == "disconnection"]
        assert any(g.location == "main_func" for g in disconnections)

    def test_with_real_collider_output(self):
        """Test against actual Collider output if available."""
        import json

        output_file = Path("/tmp/collider_self_test6/unified_analysis.json")
        if not output_file.exists():
            pytest.skip("No real Collider output available")

        with open(output_file) as f:
            data = json.load(f)

        # First decompose purposes
        from purpose_decomposition import decompose_purposes
        decomp_results = decompose_purposes(data)

        # Then detect gaps
        report = detect_gaps(data, decomp_results)

        # Should find gaps (real codebases aren't perfect)
        assert len(report.gaps) > 0
        assert 0.0 <= report.coverage <= 1.0

        # All gaps should have valid types
        for g in report.gaps:
            assert g.gap_type in GAP_TYPES
            assert g.severity in {"critical", "high", "medium", "low"}

        # Report should serialize
        d = report.to_dict()
        assert d["summary"]["total_gaps"] == len(report.gaps)

    def test_with_real_decomposition(self):
        """Integration: decompose_node -> detect_gaps pipeline."""
        node = _make_node("svc", role="Service")
        children = [
            _make_node("c1", role="Query", parent="svc"),
            # Missing Command (required)
        ]
        dr = decompose_node(node, children)
        assert dr is not None

        report = detect_gaps({"nodes": [node] + children, "edges": []}, [dr])
        # Should find missing_required for Command
        missing_req = [g for g in report.gaps if g.gap_type == "missing_required"]
        assert len(missing_req) >= 1
        assert any("Command" in g.description for g in missing_req)
