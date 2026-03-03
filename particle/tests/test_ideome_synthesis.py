"""
Tests for Ideome Synthesis -- The Rosetta Stone of Collider Macro Structures

Five test classes:
    1. TestClassifyDrift       -- drift direction classification
    2. TestSynthesizeNode      -- per-node pillar computation + drift vectors
    3. TestDomainRollup        -- aggregation logic, worst_nodes ordering
    4. TestGracefulDegradation -- missing contextome, decomposition, gaps
    5. TestSynthesizeIdeome    -- full synthesis integration + to_dict round-trip
"""

import pytest
from src.core.ideome_synthesis import (
    IdeomeNode,
    DomainAlignment,
    IdeomeResult,
    classify_drift,
    synthesize_ideome,
    _build_constraint_index,
    _build_declaration_index,
    _build_decomposition_index,
    _synthesize_node,
    _rollup_domains,
    _extract_domain,
    UNKNOWN,
    DRIFT_THRESHOLD,
    BOTH_DRIFTED_FLOOR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_node(node_id: str, role: str = "Service", **extra) -> dict:
    """Create a minimal codome node dict."""
    n = {"id": node_id, "role": role}
    n.update(extra)
    return n


def _make_full_output(
    nodes=None,
    purpose_decomposition=None,
    contextome=None,
    gap_report=None,
) -> dict:
    """Build a minimal full_output dict for testing."""
    out = {}
    if nodes is not None:
        out["nodes"] = nodes
    if purpose_decomposition is not None:
        out["purpose_decomposition"] = purpose_decomposition
    if contextome is not None:
        out["contextome"] = contextome
    if gap_report is not None:
        out["gap_report"] = gap_report
    return out


# ===========================================================================
# 1. TestClassifyDrift
# ===========================================================================

class TestClassifyDrift:
    """Test drift direction classification logic."""

    def test_aligned_when_scores_close(self):
        """Scores within DRIFT_THRESHOLD -> aligned."""
        assert classify_drift(0.7, 0.7) == "aligned"
        assert classify_drift(0.7, 0.8) == "aligned"  # delta=0.1 < 0.15

    def test_code_drifted_when_code_worse(self):
        """Code significantly lower than docs -> code_drifted."""
        assert classify_drift(0.3, 0.7) == "code_drifted"

    def test_docs_drifted_when_docs_worse(self):
        """Docs significantly lower than code -> docs_drifted."""
        assert classify_drift(0.8, 0.4) == "docs_drifted"

    def test_both_drifted_when_both_low(self):
        """Both below BOTH_DRIFTED_FLOOR -> both_drifted."""
        assert classify_drift(0.2, 0.35) == "both_drifted"

    def test_unknown_when_ambiguous(self):
        """Large delta but neither pattern fits cleanly -> unknown."""
        # Both above floor, code > docs by >threshold but not by enough
        # for docs_drifted (docs still above floor)
        result = classify_drift(0.6, 0.42)
        assert result in ("docs_drifted", "unknown")

    def test_perfect_alignment(self):
        assert classify_drift(1.0, 1.0) == "aligned"

    def test_zero_alignment(self):
        assert classify_drift(0.0, 0.0) == "both_drifted"  # both at zero = maximally drifted


# ===========================================================================
# 2. TestSynthesizeNode
# ===========================================================================

class TestSynthesizeNode:
    """Test per-node synthesis with various pillar combinations."""

    def test_all_pillars_known(self):
        """Node with all three pillars populated."""
        node = _make_node("src/services/auth.py", "Service")
        c_idx = {"src/services/auth.py": 0.8}
        d_idx = {"src/services/auth.py": 0.9}
        x_idx = {"src/services/auth.py": 0.7}

        result = _synthesize_node(node, c_idx, d_idx, x_idx)

        assert result.node_id == "src/services/auth.py"
        assert result.role == "Service"
        assert result.constraint_score == 0.8
        assert result.declaration_score == 0.9
        assert result.decomposition_score == 0.7
        # ideal = (0.8 + 0.9 + 0.7) / 3 = 0.8
        assert abs(result.alignment_C - 0.8) < 0.01
        assert result.alignment_X == 0.9
        # delta = |0.8 - 0.9| = 0.1
        assert abs(result.delta_CX - 0.1) < 0.01
        assert result.drift_direction == "aligned"  # 0.1 < 0.15

    def test_no_pillars_defaults_to_unknown(self):
        """Node with no pillar data -> all UNKNOWN."""
        node = _make_node("orphan.py", "Unknown")
        result = _synthesize_node(node, {}, {}, {})

        assert result.constraint_score == UNKNOWN
        assert result.declaration_score == UNKNOWN
        assert result.decomposition_score == UNKNOWN
        # ideal = (0.5 + 0.5 + 0.5) / 3 = 0.5
        assert abs(result.alignment_C - 0.5) < 0.01
        assert result.alignment_X == UNKNOWN
        assert result.delta_CX < DRIFT_THRESHOLD  # 0.0
        assert result.drift_direction == "aligned"

    def test_code_drifted_scenario(self):
        """Low constraint + decomposition, high declaration -> code drifted."""
        node = _make_node("src/broken.py", "Service")
        c_idx = {"src/broken.py": 0.2}   # poorly constrained
        d_idx = {"src/broken.py": 0.9}   # well documented
        x_idx = {"src/broken.py": 0.3}   # many gaps

        result = _synthesize_node(node, c_idx, d_idx, x_idx)

        # ideal = (0.2 + 0.9 + 0.3) / 3 ≈ 0.467
        # alignment_C ≈ 0.467, alignment_X = 0.9
        # delta ≈ 0.433 -> code_drifted (C < X - threshold)
        assert result.drift_direction == "code_drifted"

    def test_docs_drifted_scenario(self):
        """High constraint + decomposition, low declaration -> docs drifted."""
        node = _make_node("src/undocumented.py", "Service")
        c_idx = {"src/undocumented.py": 0.9}
        d_idx = {"src/undocumented.py": 0.1}  # poorly documented
        x_idx = {"src/undocumented.py": 0.9}

        result = _synthesize_node(node, c_idx, d_idx, x_idx)

        # ideal = (0.9 + 0.1 + 0.9) / 3 ≈ 0.633
        # alignment_C ≈ 0.633, alignment_X = 0.1
        # delta ≈ 0.533 -> docs_drifted (X < C - threshold)
        assert result.drift_direction == "docs_drifted"

    def test_details_contain_sources(self):
        """Details dict tracks which pillar sources were available."""
        node = _make_node("known.py", "Service")
        c_idx = {"known.py": 0.8}

        result = _synthesize_node(node, c_idx, {}, {})

        assert result.details["constraint_source"] == "decomposition"
        assert result.details["declaration_source"] == "unknown"
        assert result.details["decomposition_source"] == "unknown"

    def test_to_dict_round_trip(self):
        """IdeomeNode.to_dict() produces valid dict."""
        node = _make_node("test.py", "Service")
        result = _synthesize_node(node, {}, {}, {})
        d = result.to_dict()

        assert d["node_id"] == "test.py"
        assert d["role"] == "Service"
        assert isinstance(d["constraint_score"], float)
        assert isinstance(d["drift_direction"], str)
        assert isinstance(d["details"], dict)


# ===========================================================================
# 3. TestDomainRollup
# ===========================================================================

class TestDomainRollup:
    """Test domain aggregation logic."""

    def test_extract_domain_two_components(self):
        assert _extract_domain("src/services/auth.py") == "src/services"
        assert _extract_domain("lib/core/engine.py") == "lib/core"

    def test_extract_domain_single_component(self):
        assert _extract_domain("setup.py") == "setup.py"

    def test_extract_domain_deep_path(self):
        assert _extract_domain("src/a/b/c/d.py") == "src/a"

    def test_extract_domain_backslash(self):
        assert _extract_domain("src\\services\\auth.py") == "src/services"

    def test_rollup_empty(self):
        assert _rollup_domains([]) == []

    def test_rollup_single_domain(self):
        """All nodes in same domain -> one DomainAlignment."""
        nodes = [
            IdeomeNode("src/a/f1.py", "Service", None,
                        0.8, 0.7, 0.9, 0.8, 0.7, 0.1, "aligned", {}),
            IdeomeNode("src/a/f2.py", "Service", None,
                        0.6, 0.5, 0.7, 0.6, 0.5, 0.1, "aligned", {}),
        ]
        domains = _rollup_domains(nodes)
        assert len(domains) == 1
        assert domains[0].domain == "src/a"
        assert domains[0].node_count == 2
        assert abs(domains[0].avg_alignment_C - 0.7) < 0.01
        assert abs(domains[0].avg_alignment_X - 0.6) < 0.01

    def test_rollup_multiple_domains_sorted_by_delta(self):
        """Domains sorted by avg_delta_CX descending (worst first)."""
        nodes = [
            IdeomeNode("good/svc/a.py", "S", None, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, "aligned", {}),
            IdeomeNode("bad/svc/b.py", "S", None, 0.3, 0.8, 0.3, 0.47, 0.8, 0.33, "code_drifted", {}),
        ]
        domains = _rollup_domains(nodes)
        assert len(domains) == 2
        assert domains[0].domain == "bad/svc"   # worst delta first
        assert domains[1].domain == "good/svc"

    def test_worst_nodes_ordering(self):
        """worst_nodes ordered by delta_CX descending."""
        nodes = [
            IdeomeNode("d/svc/low.py", "S", None, .5, .5, .5, .5, .5, 0.05, "aligned", {}),
            IdeomeNode("d/svc/high.py", "S", None, .3, .8, .3, .47, .8, 0.33, "code_drifted", {}),
            IdeomeNode("d/svc/mid.py", "S", None, .5, .6, .5, .53, .6, 0.07, "aligned", {}),
        ]
        domains = _rollup_domains(nodes)
        assert len(domains) == 1  # all same domain
        assert domains[0].worst_nodes[0] == "d/svc/high.py"

    def test_majority_drift_direction(self):
        """Drift direction uses majority vote."""
        nodes = [
            IdeomeNode("d/svc/a.py", "S", None, .5, .5, .5, .5, .5, 0, "aligned", {}),
            IdeomeNode("d/svc/b.py", "S", None, .5, .5, .5, .5, .5, 0, "aligned", {}),
            IdeomeNode("d/svc/c.py", "S", None, .3, .8, .3, .47, .8, .33, "code_drifted", {}),
        ]
        domains = _rollup_domains(nodes)
        assert len(domains) == 1  # all same domain d/svc
        assert domains[0].drift_direction == "aligned"  # 2 aligned vs 1 drifted

    def test_to_dict(self):
        d = DomainAlignment("src/core", 5, 0.7, 0.6, 0.1, "aligned", ["a", "b"])
        dd = d.to_dict()
        assert dd["domain"] == "src/core"
        assert dd["node_count"] == 5


# ===========================================================================
# 4. TestGracefulDegradation
# ===========================================================================

class TestGracefulDegradation:
    """Test that Ideome works with missing upstream data."""

    def test_empty_full_output(self):
        """Empty dict -> valid result with UNKNOWN defaults."""
        result = synthesize_ideome({})
        assert result.node_count == 0
        assert result.global_coherence == UNKNOWN
        assert result.coverage == 0.0

    def test_nodes_only_no_upstream(self):
        """Nodes exist but no contextome/decomposition/gaps."""
        nodes = [_make_node("a.py"), _make_node("b.py")]
        full = _make_full_output(nodes=nodes)
        result = synthesize_ideome(full)

        assert result.node_count == 2
        # All pillars UNKNOWN -> all scores 0.5
        for n in result.nodes:
            assert n.constraint_score == UNKNOWN
            assert n.declaration_score == UNKNOWN
            assert n.decomposition_score == UNKNOWN
            assert n.drift_direction == "aligned"  # delta = 0
        assert result.coverage == 0.0  # no node has non-UNKNOWN data

    def test_with_only_decomposition(self):
        """Only purpose_decomposition exists."""
        nodes = [_make_node("src/svc.py", "Service")]
        decomp = [{"node_id": "src/svc.py", "completeness": 0.8}]
        full = _make_full_output(nodes=nodes, purpose_decomposition=decomp)
        result = synthesize_ideome(full)

        assert result.nodes[0].constraint_score == 0.8
        assert result.nodes[0].declaration_score == UNKNOWN
        assert result.coverage == 1.0  # one pillar is non-UNKNOWN

    def test_with_only_contextome(self):
        """Only contextome exists."""
        nodes = [_make_node("src/auth.py", "Service")]
        ctx = {
            "purpose_priors": {
                "src/auth": {"purpose": "Service", "confidence": 0.85, "source": "doc"},
            },
            "purpose_coverage": 0.6,
            "doc_count": 3,
        }
        full = _make_full_output(nodes=nodes, contextome=ctx)
        result = synthesize_ideome(full)

        assert result.nodes[0].declaration_score == 0.85
        assert result.coverage == 1.0

    def test_with_only_gap_report(self):
        """Only gap_report exists."""
        nodes = [_make_node("src/x.py")]
        gaps = {"gaps": [{"location": "src/x.py", "gap_type": "missing_required"}]}
        full = _make_full_output(nodes=nodes, gap_report=gaps)
        result = synthesize_ideome(full)

        assert result.nodes[0].decomposition_score < 1.0
        assert result.coverage == 1.0


# ===========================================================================
# 5. TestSynthesizeIdeome
# ===========================================================================

class TestSynthesizeIdeome:
    """Full integration tests for synthesize_ideome()."""

    def _build_rich_output(self) -> dict:
        """Build a realistic full_output with all upstream data."""
        nodes = [
            _make_node("src/services/auth.py", "Service"),
            _make_node("src/services/user.py", "Service"),
            _make_node("src/models/entity.py", "Entity"),
            _make_node("src/utils/helper.py", "Utility"),
            _make_node("tests/test_auth.py", "Test"),
        ]
        decomp = [
            {"node_id": "src/services/auth.py", "completeness": 0.9},
            {"node_id": "src/services/user.py", "completeness": 0.6},
            {"node_id": "src/models/entity.py", "completeness": 0.7},
        ]
        ctx = {
            "purpose_priors": {
                "src/services/auth": {
                    "purpose": "Service", "confidence": 0.8, "source": "doc",
                },
                "src/models/entity": {
                    "purpose": "Entity", "confidence": 0.9, "source": "doc",
                },
            },
            "purpose_coverage": 0.5,
            "doc_count": 4,
        }
        gaps = {
            "gaps": [
                {"location": "src/services/user.py", "gap_type": "missing_required"},
                {"location": "src/services/user.py", "gap_type": "missing_expected"},
                {"location": "src/utils/helper.py", "gap_type": "orphan_cluster"},
            ],
        }
        return _make_full_output(
            nodes=nodes,
            purpose_decomposition=decomp,
            contextome=ctx,
            gap_report=gaps,
        )

    def test_full_synthesis_produces_nodes(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        assert result.node_count == 5
        assert len(result.nodes) == 5

    def test_coverage_reflects_data_availability(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        # 4 nodes have at least one non-UNKNOWN pillar
        # (auth, user, entity from decomp; helper from gaps; test has none)
        assert result.coverage > 0.5

    def test_domains_are_created(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        assert len(result.domains) >= 2  # src/services, src/models, etc.

    def test_global_coherence_bounded(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        assert 0.0 <= result.global_coherence <= 1.0

    def test_global_drift_bounded(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        assert 0.0 <= result.global_drift_C <= 1.0
        assert 0.0 <= result.global_drift_X <= 1.0
        assert 0.0 <= result.global_delta_CX <= 1.0

    def test_to_dict_complete(self):
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        d = result.to_dict()

        assert "nodes" in d
        assert "domains" in d
        assert "global_coherence" in d
        assert "global_drift_C" in d
        assert "global_drift_X" in d
        assert "global_delta_CX" in d
        assert "coverage" in d
        assert "node_count" in d
        assert "summary" in d
        assert "by_drift_direction" in d["summary"]
        assert "domain_count" in d["summary"]

    def test_to_dict_values_are_json_serializable(self):
        """Ensure to_dict() produces JSON-safe types."""
        import json
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        d = result.to_dict()
        # Should not raise
        json.dumps(d)

    def test_nodes_without_id_skipped(self):
        """Nodes with empty id are skipped."""
        nodes = [{"id": "", "role": "Service"}, _make_node("real.py")]
        full = _make_full_output(nodes=nodes)
        result = synthesize_ideome(full)
        assert result.node_count == 1

    def test_drift_directions_distributed(self):
        """With varied inputs, multiple drift directions appear."""
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        directions = {n.drift_direction for n in result.nodes}
        # At minimum aligned should appear (nodes with no data)
        assert "aligned" in directions

    def test_ideome_result_summary_counts(self):
        """Summary counts match actual node distributions."""
        full = self._build_rich_output()
        result = synthesize_ideome(full)
        d = result.to_dict()
        summary = d["summary"]["by_drift_direction"]
        total = sum(summary.values())
        assert total == result.node_count


# ===========================================================================
# Pillar Index Tests
# ===========================================================================

class TestPillarIndexes:
    """Test the three pillar index builders."""

    def test_constraint_index_from_decomposition(self):
        full = {"purpose_decomposition": [
            {"node_id": "a.py", "completeness": 0.8},
            {"node_id": "b.py", "completeness": 0.3},
        ]}
        idx = _build_constraint_index(full)
        assert idx["a.py"] == 0.8
        assert idx["b.py"] == 0.3

    def test_constraint_index_clamps_values(self):
        full = {"purpose_decomposition": [
            {"node_id": "over.py", "completeness": 1.5},
            {"node_id": "under.py", "completeness": -0.2},
        ]}
        idx = _build_constraint_index(full)
        assert idx["over.py"] == 1.0
        assert idx["under.py"] == 0.0

    def test_constraint_index_empty(self):
        assert _build_constraint_index({}) == {}

    def test_declaration_index_from_priors(self):
        full = {
            "nodes": [{"id": "src/auth.py", "role": "Service"}],
            "contextome": {
                "purpose_priors": {
                    "src/auth": {"purpose": "Service", "confidence": 0.85},
                },
            },
        }
        idx = _build_declaration_index(full)
        assert "src/auth.py" in idx
        assert idx["src/auth.py"] == 0.85

    def test_declaration_index_mismatch(self):
        full = {
            "nodes": [{"id": "src/auth.py", "role": "Controller"}],
            "contextome": {
                "purpose_priors": {
                    "src/auth": {"purpose": "Service", "confidence": 0.85},
                },
            },
        }
        idx = _build_declaration_index(full)
        assert "src/auth.py" in idx
        assert idx["src/auth.py"] == 0.2  # mismatch

    def test_declaration_index_empty(self):
        assert _build_declaration_index({}) == {}

    def test_decomposition_index_from_gaps(self):
        full = {"gap_report": {"gaps": [
            {"location": "x.py", "gap_type": "missing_required"},
            {"location": "x.py", "gap_type": "missing_expected"},
            {"location": "y.py", "gap_type": "disconnection"},
        ]}}
        idx = _build_decomposition_index(full)
        assert "x.py" in idx
        assert "y.py" in idx
        assert idx["x.py"] < idx["y.py"]  # more gaps = lower score

    def test_decomposition_index_empty(self):
        assert _build_decomposition_index({}) == {}
        assert _build_decomposition_index({"gap_report": {"gaps": []}}) == {}
