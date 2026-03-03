"""Tests for Purpose Decomposition (Module 2 of the Collider Trinity)."""

import sys
from pathlib import Path

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from purpose_decomposition import (
    CONSTRAINT_RULES,
    SubCompartment,
    PurposeManifest,
    DecompositionResult,
    decompose_node,
    decompose_purposes,
    summarize_decomposition,
    _build_parent_child_map,
    _get_child_roles,
)


# ── CONSTRAINT_RULES structure tests ─────────────────────────────────────


class TestConstraintRules:
    def test_all_rules_have_three_keys(self):
        for role, rules in CONSTRAINT_RULES.items():
            assert "required" in rules, f"{role} missing 'required'"
            assert "expected" in rules, f"{role} missing 'expected'"
            assert "forbidden" in rules, f"{role} missing 'forbidden'"

    def test_all_values_are_lists(self):
        for role, rules in CONSTRAINT_RULES.items():
            for key in ("required", "expected", "forbidden"):
                assert isinstance(rules[key], list), f"{role}.{key} is not a list"

    def test_no_overlap_between_categories(self):
        """A sub-purpose can't be both required and forbidden."""
        for role, rules in CONSTRAINT_RULES.items():
            req = set(rules["required"])
            exp = set(rules["expected"])
            forb = set(rules["forbidden"])
            assert req.isdisjoint(forb), f"{role}: required overlaps forbidden: {req & forb}"
            assert exp.isdisjoint(forb), f"{role}: expected overlaps forbidden: {exp & forb}"

    def test_known_roles_present(self):
        """Key architectural roles should have rules."""
        expected_roles = [
            "Repository", "Service", "Controller", "Entity",
            "Orchestrator", "UseCase", "Gateway", "Utility",
        ]
        for role in expected_roles:
            assert role in CONSTRAINT_RULES, f"Missing rules for {role}"

    def test_at_least_one_required(self):
        """Each role should require at least one sub-purpose."""
        for role, rules in CONSTRAINT_RULES.items():
            assert len(rules["required"]) >= 1, f"{role} has no required sub-purposes"


# ── Helper function tests ────────────────────────────────────────────────


def _make_node(nid, role="Internal", parent="", **extra):
    """Build a minimal node dict."""
    node = {"id": nid, "role": role, "parent": parent, "compartment": "core"}
    node.update(extra)
    return node


class TestBuildParentChildMap:
    def test_empty_nodes(self):
        result = _build_parent_child_map([])
        assert result == {}

    def test_flat_structure(self):
        """Nodes without parents have no children mapped."""
        nodes = [_make_node("a"), _make_node("b")]
        result = _build_parent_child_map(nodes)
        assert result == {}

    def test_parent_child_relationship(self):
        nodes = [
            _make_node("parent", role="Service"),
            _make_node("child1", role="Command", parent="parent"),
            _make_node("child2", role="Query", parent="parent"),
        ]
        result = _build_parent_child_map(nodes)
        assert "parent" in result
        assert len(result["parent"]) == 2
        child_ids = {c["id"] for c in result["parent"]}
        assert child_ids == {"child1", "child2"}

    def test_multiple_parents(self):
        nodes = [
            _make_node("p1", role="Service"),
            _make_node("p2", role="Repository"),
            _make_node("c1", role="Command", parent="p1"),
            _make_node("c2", role="Query", parent="p2"),
        ]
        result = _build_parent_child_map(nodes)
        assert len(result["p1"]) == 1
        assert len(result["p2"]) == 1


class TestGetChildRoles:
    def test_empty_children(self):
        assert _get_child_roles([]) == {}

    def test_role_mapping(self):
        children = [
            _make_node("a", role="Command"),
            _make_node("b", role="Query"),
            _make_node("c", role="Command"),
        ]
        result = _get_child_roles(children)
        assert len(result["Command"]) == 2
        assert len(result["Query"]) == 1

    def test_unknown_role_default(self):
        children = [{"id": "x"}]  # no 'role' key
        result = _get_child_roles(children)
        assert "Unknown" in result


# ── decompose_node tests ─────────────────────────────────────────────────


class TestDecomposeNode:
    def test_unknown_role_returns_none(self):
        """Roles not in CONSTRAINT_RULES return None."""
        node = _make_node("x", role="SomeUnknownRole")
        result = decompose_node(node, [])
        assert result is None

    def test_service_with_all_required(self):
        """Service with Command + Query children -> fully present."""
        node = _make_node("svc", role="Service")
        children = [
            _make_node("c1", role="Command", parent="svc"),
            _make_node("c2", role="Query", parent="svc"),
        ]
        result = decompose_node(node, children)
        assert result is not None
        assert result.purpose == "Service"
        assert "Command" in result.present
        assert "Query" in result.present
        assert result.missing == []
        assert result.completeness > 0.0

    def test_service_missing_required(self):
        """Service without Command -> missing."""
        node = _make_node("svc", role="Service")
        children = [
            _make_node("c1", role="Query", parent="svc"),
        ]
        result = decompose_node(node, children)
        assert "Command" in result.missing
        assert result.completeness < 1.0

    def test_repository_with_forbidden(self):
        """Repository with Controller child -> violation."""
        node = _make_node("repo", role="Repository")
        children = [
            _make_node("c1", role="Query", parent="repo"),
            _make_node("c2", role="Command", parent="repo"),
            _make_node("c3", role="Controller", parent="repo"),
        ]
        result = decompose_node(node, children)
        assert "Controller" in result.violations
        assert "Query" in result.present
        assert "Command" in result.present

    def test_completeness_calculation(self):
        """Completeness = present(required+expected) / total(required+expected)."""
        node = _make_node("svc", role="Service")
        # Service requires: Command, Query. Expects: Validator, Transformer
        # Total = 4. If we provide Command + Query + Validator = 3/4 = 0.75
        children = [
            _make_node("c1", role="Command", parent="svc"),
            _make_node("c2", role="Query", parent="svc"),
            _make_node("c3", role="Validator", parent="svc"),
        ]
        result = decompose_node(node, children)
        assert result.completeness == pytest.approx(0.75, abs=0.01)

    def test_full_completeness(self):
        """All required + expected present -> completeness = 1.0."""
        node = _make_node("svc", role="Service")
        children = [
            _make_node("c1", role="Command", parent="svc"),
            _make_node("c2", role="Query", parent="svc"),
            _make_node("c3", role="Validator", parent="svc"),
            _make_node("c4", role="Transformer", parent="svc"),
        ]
        result = decompose_node(node, children)
        assert result.completeness == pytest.approx(1.0, abs=0.01)

    def test_gaps_vs_missing(self):
        """Missing = absent required. Gaps = absent expected."""
        node = _make_node("svc", role="Service")
        # Provide nothing -- required: Command, Query -> missing
        # expected: Validator, Transformer -> gaps
        result = decompose_node(node, [])
        assert "Command" in result.missing
        assert "Query" in result.missing
        assert "Validator" in result.gaps
        assert "Transformer" in result.gaps

    def test_to_dict(self):
        node = _make_node("svc", role="Service")
        result = decompose_node(node, [])
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["node_id"] == "svc"
        assert d["purpose"] == "Service"
        assert "manifest" in d
        assert "missing" in d
        assert "completeness" in d

    def test_child_count(self):
        node = _make_node("svc", role="Service")
        children = [_make_node(f"c{i}", role="Internal") for i in range(5)]
        result = decompose_node(node, children)
        assert result.child_count == 5

    def test_test_suite_decomposition(self):
        """TestSuite requires Asserter, expects Factory, forbids nothing."""
        node = _make_node("ts", role="TestSuite")
        children = [
            _make_node("a1", role="Asserter", parent="ts"),
            _make_node("a2", role="Factory", parent="ts"),
        ]
        result = decompose_node(node, children)
        assert result.missing == []
        assert result.gaps == []
        assert result.violations == []
        assert result.completeness == pytest.approx(1.0, abs=0.01)


# ── decompose_purposes integration tests ─────────────────────────────────


class TestDecomposePurposes:
    def test_empty_output(self):
        result = decompose_purposes({})
        assert result == []

    def test_no_nodes(self):
        result = decompose_purposes({"nodes": []})
        assert result == []

    def test_flat_nodes_no_containers(self):
        """Nodes without children or pi3 containers -> no results."""
        nodes = [
            _make_node("a", role="Internal"),
            _make_node("b", role="Command"),
        ]
        result = decompose_purposes({"nodes": nodes})
        assert result == []

    def test_container_with_children(self):
        """A Service with children should be decomposed."""
        nodes = [
            _make_node("svc", role="Service"),
            _make_node("c1", role="Command", parent="svc"),
            _make_node("c2", role="Query", parent="svc"),
        ]
        results = decompose_purposes({"nodes": nodes})
        assert len(results) == 1
        assert results[0].purpose == "Service"
        assert results[0].missing == []

    def test_pi3_container_without_parent_children(self):
        """Node with pi3_child_count but no parent-linked children."""
        nodes = [
            _make_node("container", role="Service", pi3_child_count=5),
        ]
        results = decompose_purposes({"nodes": nodes})
        # Should still be analyzed (it's a container)
        assert len(results) == 1
        # But children list is empty -> everything missing
        assert "Command" in results[0].missing
        assert "Query" in results[0].missing

    def test_unknown_role_skipped(self):
        """Nodes with roles not in CONSTRAINT_RULES are skipped."""
        nodes = [
            _make_node("unknown", role="SomeWeirdRole"),
            _make_node("c1", role="Internal", parent="unknown"),
        ]
        results = decompose_purposes({"nodes": nodes})
        assert results == []

    def test_sorted_by_completeness(self):
        """Results should be sorted ascending by completeness (worst first)."""
        nodes = [
            # Perfect service
            _make_node("svc1", role="Service"),
            _make_node("s1c1", role="Command", parent="svc1"),
            _make_node("s1c2", role="Query", parent="svc1"),
            _make_node("s1c3", role="Validator", parent="svc1"),
            _make_node("s1c4", role="Transformer", parent="svc1"),
            # Empty service (worst)
            _make_node("svc2", role="Service", pi3_child_count=1),
        ]
        results = decompose_purposes({"nodes": nodes})
        assert len(results) == 2
        # Worst first
        assert results[0].completeness <= results[1].completeness
        assert results[0].node_id == "svc2"

    def test_multiple_container_types(self):
        """Mixed container roles decompose independently."""
        nodes = [
            _make_node("svc", role="Service"),
            _make_node("sc1", role="Command", parent="svc"),
            _make_node("repo", role="Repository"),
            _make_node("rc1", role="Query", parent="repo"),
        ]
        results = decompose_purposes({"nodes": nodes})
        purposes = {r.purpose for r in results}
        assert "Service" in purposes
        assert "Repository" in purposes

    def test_with_real_collider_output(self):
        """Test against actual Collider output if available."""
        import json

        output_file = Path("/tmp/collider_self_test6/unified_analysis.json")
        if not output_file.exists():
            pytest.skip("No real Collider output available")

        with open(output_file) as f:
            data = json.load(f)

        results = decompose_purposes(data)
        # Should find some containers
        assert len(results) > 0

        # All results should have valid structure
        for r in results:
            assert 0.0 <= r.completeness <= 1.0
            assert isinstance(r.missing, list)
            assert isinstance(r.violations, list)
            assert isinstance(r.present, list)

        # Summary should work
        summary = summarize_decomposition(results)
        assert summary["total_containers"] == len(results)
        assert 0.0 <= summary["avg_completeness"] <= 1.0


# ── summarize_decomposition tests ────────────────────────────────────────


class TestSummarizeDecomposition:
    def test_empty_results(self):
        summary = summarize_decomposition([])
        assert summary["total_containers"] == 0
        assert summary["avg_completeness"] == 1.0
        assert summary["total_missing"] == 0
        assert summary["total_gaps"] == 0
        assert summary["total_violations"] == 0
        assert summary["worst_nodes"] == []

    def test_single_result(self):
        node = _make_node("svc", role="Service")
        result = decompose_node(node, [])
        summary = summarize_decomposition([result])
        assert summary["total_containers"] == 1
        assert summary["total_missing"] == 2  # Command + Query
        assert summary["total_gaps"] == 2  # Validator + Transformer
        assert summary["avg_completeness"] == 0.0

    def test_worst_nodes_limited_to_five(self):
        """Should only report top 5 worst nodes."""
        nodes_and_children = []
        for i in range(10):
            node = _make_node(f"svc{i}", role="Service", pi3_child_count=1)
            nodes_and_children.append(decompose_node(node, []))

        results = [r for r in nodes_and_children if r is not None]
        summary = summarize_decomposition(results)
        assert len(summary["worst_nodes"]) <= 5

    def test_summary_counts_violations(self):
        node = _make_node("repo", role="Repository")
        children = [
            _make_node("c1", role="Controller", parent="repo"),  # forbidden
            _make_node("c2", role="View", parent="repo"),  # forbidden
        ]
        result = decompose_node(node, children)
        summary = summarize_decomposition([result])
        assert summary["total_violations"] == 2
