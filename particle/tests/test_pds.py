"""
Tests for PDS (Progressive Discovery System) — the pre-push gate.

Covers:
- get_changed_files(): subprocess mocking, extension filtering, fallback
- _fallback_changed_files(): porcelain parsing
- compute_blast_radius(): graph topology (ancestors + descendants)
- _node_in_changed_files(): path boundary matching, suffix collision prevention
- evaluate_gate(): blocking vs warning classification, downgrade logic,
  catch-all branch, changed_nodes parameter
- GateResult: dataclass serialization
"""
import subprocess
import sys
import os
from unittest.mock import patch, MagicMock

import networkx as nx
import pytest

# Add src/core to path for imports (same pattern as other tests)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from pds import (
    ANALYZABLE_EXTENSIONS,
    BLOCKING_CATEGORIES,
    BLOCKING_SEVERITIES,
    WARN_CATEGORIES,
    GateResult,
    get_changed_files,
    _fallback_changed_files,
    compute_blast_radius,
    _node_in_changed_files,
    evaluate_gate,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def simple_graph():
    """A -> B -> C -> D linear dependency chain."""
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("B", "C"), ("C", "D")])
    return G


@pytest.fixture
def diamond_graph():
    """
    Diamond: A -> B, A -> C, B -> D, C -> D
    Changing D affects all; changing A affects none upstream.
    """
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")])
    return G


@pytest.fixture
def disconnected_graph():
    """Two disconnected components: A->B and X->Y."""
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("X", "Y")])
    return G


@pytest.fixture
def blocking_finding_in_changed():
    """A critical topology finding whose nodes are in changed files."""
    return {
        "id": "F1",
        "category": "topology",
        "severity": "critical",
        "related_nodes": ["/repo/src/core/pds.py:evaluate_gate"],
        "description": "Cycle detected",
    }


@pytest.fixture
def blocking_finding_in_blast_only():
    """A critical topology finding only reachable via blast radius."""
    return {
        "id": "F2",
        "category": "entanglement",
        "severity": "high",
        "related_nodes": ["/repo/src/core/other.py:helper"],
        "description": "High coupling",
    }


@pytest.fixture
def warn_finding():
    """A medium-severity informational finding."""
    return {
        "id": "F3",
        "category": "bus_factor",
        "severity": "medium",
        "related_nodes": ["/repo/src/core/pds.py:compute_blast_radius"],
        "description": "Single contributor",
    }


# =============================================================================
# GateResult TESTS
# =============================================================================

class TestGateResult:
    def test_to_dict_passed(self):
        result = GateResult(passed=True, summary="all clear")
        d = result.to_dict()
        assert d["passed"] is True
        assert d["blocking_findings"] == []
        assert d["warnings"] == []
        assert d["summary"] == "all clear"

    def test_to_dict_failed(self):
        finding = {"id": "F1", "category": "topology"}
        result = GateResult(
            passed=False,
            blocking_findings=[finding],
            warnings=[{"id": "W1"}],
            summary="blocked",
        )
        d = result.to_dict()
        assert d["passed"] is False
        assert len(d["blocking_findings"]) == 1
        assert d["blocking_findings"][0]["id"] == "F1"
        assert len(d["warnings"]) == 1

    def test_default_values(self):
        result = GateResult(passed=True)
        assert result.blocking_findings == []
        assert result.warnings == []
        assert result.summary == ""


# =============================================================================
# get_changed_files TESTS
# =============================================================================

class TestGetChangedFiles:
    @patch("pds.subprocess.run")
    def test_basic_diff(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="src/core/pds.py\nsrc/utils/helper.js\nREADME.md\n",
        )
        files = get_changed_files("/repo")
        assert "src/core/pds.py" in files
        assert "src/utils/helper.js" in files
        assert "README.md" not in files  # .md not analyzable

    @patch("pds.subprocess.run")
    def test_extension_filtering(self, mock_run):
        """Only analyzable extensions should be returned."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="a.py\nb.txt\nc.json\nd.ts\ne.go\nf.md\ng.yaml\n",
        )
        files = get_changed_files("/repo")
        assert files == {"a.py", "d.ts", "e.go"}

    @patch("pds.subprocess.run")
    def test_empty_diff(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        files = get_changed_files("/repo")
        assert files == set()

    @patch("pds.subprocess.run")
    def test_nonzero_returncode_triggers_fallback(self, mock_run):
        """When git diff fails, should fall back to git status."""
        # First call (git diff) fails
        mock_run.side_effect = [
            MagicMock(returncode=128, stdout="", stderr="fatal: bad ref"),
            MagicMock(returncode=0, stdout=" M src/core/pds.py\n"),
        ]
        files = get_changed_files("/repo")
        assert "src/core/pds.py" in files

    @patch("pds.subprocess.run")
    def test_timeout_triggers_fallback(self, mock_run):
        """Timeout on git diff should trigger fallback."""
        mock_run.side_effect = [
            subprocess.TimeoutExpired(cmd="git", timeout=30),
            MagicMock(returncode=0, stdout=" M app.ts\n"),
        ]
        files = get_changed_files("/repo")
        assert "app.ts" in files

    @patch("pds.subprocess.run")
    def test_custom_base_ref(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="file.py\n")
        get_changed_files("/repo", base_ref="main")
        args = mock_run.call_args[0][0]
        assert "main" in args

    @patch("pds.subprocess.run")
    def test_whitespace_handling(self, mock_run):
        """Lines with extra whitespace should be stripped."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  src/core/pds.py  \n\n  src/other.ts\n",
        )
        files = get_changed_files("/repo")
        assert "src/core/pds.py" in files
        assert "src/other.ts" in files


# =============================================================================
# _fallback_changed_files TESTS
# =============================================================================

class TestFallbackChangedFiles:
    @patch("pds.subprocess.run")
    def test_porcelain_parsing(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M src/core/pds.py\n?? src/new_file.ts\nA  src/added.go\n",
        )
        files = _fallback_changed_files("/repo")
        assert "src/core/pds.py" in files
        assert "src/new_file.ts" in files
        assert "src/added.go" in files

    @patch("pds.subprocess.run")
    def test_skips_non_analyzable(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M README.md\n M config.yaml\n M app.py\n",
        )
        files = _fallback_changed_files("/repo")
        assert files == {"app.py"}

    @patch("pds.subprocess.run")
    def test_short_lines_skipped(self, mock_run):
        """Lines shorter than 4 chars are not valid porcelain."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="AB\n M app.py\n",
        )
        files = _fallback_changed_files("/repo")
        assert files == {"app.py"}

    @patch("pds.subprocess.run")
    def test_failure_returns_empty(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        files = _fallback_changed_files("/repo")
        assert files == set()

    @patch("pds.subprocess.run")
    def test_timeout_returns_empty(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=30)
        files = _fallback_changed_files("/repo")
        assert files == set()


# =============================================================================
# compute_blast_radius TESTS
# =============================================================================

class TestComputeBlastRadius:
    def test_linear_chain_middle(self, simple_graph):
        """Changing B in A->B->C->D should include all nodes."""
        blast = compute_blast_radius(simple_graph, {"B"})
        assert blast == {"A", "B", "C", "D"}

    def test_linear_chain_leaf(self, simple_graph):
        """Changing D (leaf) includes D and all ancestors."""
        blast = compute_blast_radius(simple_graph, {"D"})
        assert blast == {"A", "B", "C", "D"}

    def test_linear_chain_root(self, simple_graph):
        """Changing A (root) includes A and all descendants."""
        blast = compute_blast_radius(simple_graph, {"A"})
        assert blast == {"A", "B", "C", "D"}

    def test_diamond_graph(self, diamond_graph):
        """Changing D in diamond includes everything."""
        blast = compute_blast_radius(diamond_graph, {"D"})
        assert blast == {"A", "B", "C", "D"}

    def test_diamond_one_branch(self, diamond_graph):
        """Changing B in diamond: ancestors={A}, descendants={D}."""
        blast = compute_blast_radius(diamond_graph, {"B"})
        assert blast == {"A", "B", "D"}

    def test_disconnected_graph(self, disconnected_graph):
        """Changing A should NOT include X or Y."""
        blast = compute_blast_radius(disconnected_graph, {"A"})
        assert blast == {"A", "B"}
        assert "X" not in blast
        assert "Y" not in blast

    def test_multiple_changed_nodes(self, disconnected_graph):
        """Multiple changed nodes merge their blast radii."""
        blast = compute_blast_radius(disconnected_graph, {"A", "X"})
        assert blast == {"A", "B", "X", "Y"}

    def test_node_not_in_graph(self, simple_graph):
        """Nodes not in the graph are silently skipped."""
        blast = compute_blast_radius(simple_graph, {"NONEXISTENT"})
        assert blast == set()

    def test_empty_changed_set(self, simple_graph):
        """No changed nodes -> empty blast radius."""
        blast = compute_blast_radius(simple_graph, set())
        assert blast == set()

    def test_empty_graph(self):
        """Empty graph -> empty blast radius regardless of input."""
        G = nx.DiGraph()
        blast = compute_blast_radius(G, {"A", "B"})
        assert blast == set()

    def test_self_loop(self):
        """Node with self-loop still works."""
        G = nx.DiGraph()
        G.add_edge("A", "A")
        blast = compute_blast_radius(G, {"A"})
        assert blast == {"A"}


# =============================================================================
# _node_in_changed_files TESTS
# =============================================================================

class TestNodeInChangedFiles:
    def test_exact_match(self):
        """Full path node matches relative changed file."""
        assert _node_in_changed_files(
            "/repo/src/core/pds.py:evaluate_gate",
            {"src/core/pds.py"},
        )

    def test_no_function_suffix(self):
        """Node IDs without ':function' part still match."""
        assert _node_in_changed_files(
            "/repo/src/core/pds.py",
            {"src/core/pds.py"},
        )

    def test_suffix_collision_prevented(self):
        """Changed file 'pds.py' must NOT match '/other/core/xpds.py'."""
        assert not _node_in_changed_files(
            "/repo/src/core/xpds.py:func",
            {"pds.py"},
        )

    def test_exact_filename_match(self):
        """Changed file 'pds.py' SHOULD match '/repo/pds.py' (exact len)."""
        assert _node_in_changed_files("pds.py:func", {"pds.py"})

    def test_path_boundary_slash(self):
        """Match requires '/' before the suffix."""
        assert _node_in_changed_files(
            "/repo/src/core/pds.py:func",
            {"core/pds.py"},
        )

    def test_path_boundary_backslash(self):
        """Backslash path boundary (no drive letter — avoids ':' split issue)."""
        # Note: Windows drive-letter paths like "C:\repo\..." break the ':'
        # split in _node_in_changed_files. This tests backslash support
        # for relative-style paths only.
        assert _node_in_changed_files(
            "\\repo\\src\\core\\pds.py:func",
            {"core\\pds.py"},
        )

    def test_no_match_different_file(self):
        assert not _node_in_changed_files(
            "/repo/src/core/pds.py:func",
            {"src/core/other.py"},
        )

    def test_empty_changed_files(self):
        assert not _node_in_changed_files(
            "/repo/src/core/pds.py:func",
            set(),
        )

    def test_multiple_changed_files_any_match(self):
        """Should return True if ANY changed file matches."""
        assert _node_in_changed_files(
            "/repo/src/core/pds.py:func",
            {"other.py", "src/core/pds.py", "unrelated.ts"},
        )

    def test_partial_directory_no_match(self):
        """Changed file 'core/pds.py' must NOT match '/repo/src/notcore/pds.py'."""
        # 'notcore/pds.py' does not end with 'core/pds.py' — no collision.
        # But '/repo/src/score/pds.py' would incorrectly match if we only
        # check endswith without boundary. Let's verify:
        assert not _node_in_changed_files(
            "/repo/src/score/pds.py:func",
            {"core/pds.py"},
        )

    def test_same_filename_different_directory(self):
        """Two files named 'utils.py' in different dirs should not cross-match."""
        assert not _node_in_changed_files(
            "/repo/src/core/utils.py:func",
            {"src/other/utils.py"},
        )

    def test_changed_file_is_full_node_path(self):
        """Edge case: changed_file has exact same full path as node."""
        assert _node_in_changed_files(
            "/repo/src/core/pds.py",
            {"/repo/src/core/pds.py"},
        )


# =============================================================================
# evaluate_gate TESTS
# =============================================================================

class TestEvaluateGate:
    def test_no_findings(self):
        """No findings -> pass, empty lists."""
        result = evaluate_gate([], {"A"}, {"a.py"})
        assert result.passed is True
        assert result.blocking_findings == []
        assert result.warnings == []

    def test_finding_outside_blast_radius(self):
        """Findings whose nodes don't touch blast radius are ignored."""
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["Z"],  # Z not in blast radius
        }
        result = evaluate_gate([finding], {"A", "B"}, {"a.py"})
        assert result.passed is True
        assert result.blocking_findings == []
        assert result.warnings == []

    def test_blocking_finding_in_changed_files(
        self, blocking_finding_in_changed
    ):
        """Critical/high finding in blocking category + changed file -> block."""
        blast = {"/repo/src/core/pds.py:evaluate_gate", "/repo/other.py"}
        changed = {"src/core/pds.py"}
        result = evaluate_gate(
            [blocking_finding_in_changed], blast, changed
        )
        assert result.passed is False
        assert len(result.blocking_findings) == 1
        assert result.blocking_findings[0]["id"] == "F1"

    def test_blocking_finding_downgraded_when_not_in_changed(
        self, blocking_finding_in_blast_only
    ):
        """Critical/high finding NOT in changed files -> downgraded to warning."""
        blast = {"/repo/src/core/other.py:helper", "/repo/src/core/pds.py"}
        changed = {"src/core/pds.py"}  # other.py not in changed
        result = evaluate_gate(
            [blocking_finding_in_blast_only], blast, changed
        )
        assert result.passed is True
        assert len(result.blocking_findings) == 0
        assert len(result.warnings) == 1
        w = result.warnings[0]
        assert w["downgraded_from"] == "blocking"
        assert "blast radius" in w["downgrade_reason"]

    def test_warn_category_stays_warning(self, warn_finding):
        """Findings in WARN_CATEGORIES always go to warnings."""
        blast = {"/repo/src/core/pds.py:compute_blast_radius"}
        changed = {"src/core/pds.py"}
        result = evaluate_gate([warn_finding], blast, changed)
        assert result.passed is True
        assert len(result.warnings) == 1
        assert result.warnings[0]["id"] == "F3"

    def test_low_severity_blocking_category_is_warning(self):
        """Blocking category but low severity -> warning, not blocking."""
        finding = {
            "category": "topology",
            "severity": "medium",
            "related_nodes": ["A"],
        }
        result = evaluate_gate([finding], {"A"}, {"a.py"})
        assert result.passed is True
        assert len(result.warnings) == 1

    def test_catch_all_unknown_category(self):
        """Unknown category with blocking severity -> warning (catch-all)."""
        finding = {
            "category": "unknown_future_category",
            "severity": "critical",
            "related_nodes": ["A"],
        }
        result = evaluate_gate([finding], {"A"}, {"a.py"})
        assert result.passed is True
        assert len(result.warnings) == 1

    def test_changed_nodes_parameter_precise_matching(self):
        """When changed_nodes is provided, uses set intersection instead
        of file-path matching."""
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["node_A"],
        }
        blast = {"node_A", "node_B"}
        changed_files = {"a.py"}  # file-path match would NOT work for "node_A"
        changed_nodes = {"node_A"}  # precise match DOES work

        result = evaluate_gate(
            [finding], blast, changed_files, changed_nodes=changed_nodes
        )
        assert result.passed is False
        assert len(result.blocking_findings) == 1

    def test_changed_nodes_no_match_downgrades(self):
        """When changed_nodes is provided but doesn't contain the finding's
        nodes, the finding is downgraded."""
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["node_A"],
        }
        blast = {"node_A", "node_B"}
        changed_files = {"a.py"}
        changed_nodes = {"node_B"}  # node_A not in changed_nodes

        result = evaluate_gate(
            [finding], blast, changed_files, changed_nodes=changed_nodes
        )
        assert result.passed is True
        assert len(result.warnings) == 1
        assert result.warnings[0].get("downgraded_from") == "blocking"

    def test_multiple_findings_mixed(self):
        """Mix of blocking and warning findings."""
        findings = [
            {
                "category": "topology",
                "severity": "critical",
                "related_nodes": ["A"],
            },
            {
                "category": "bus_factor",
                "severity": "medium",
                "related_nodes": ["A"],
            },
            {
                "category": "entanglement",
                "severity": "high",
                "related_nodes": ["B"],  # B not in changed files
            },
        ]
        blast = {"A", "B"}
        changed = {"a.py"}

        # For file matching: "A" won't match "a.py" via _node_in_changed_files
        # because A doesn't have a path-like structure. Use changed_nodes.
        result = evaluate_gate(
            findings, blast, changed, changed_nodes={"A"}
        )
        assert result.passed is False  # First finding blocks
        assert len(result.blocking_findings) == 1
        # Bus_factor = warn category, entanglement downgraded
        assert len(result.warnings) == 2

    def test_summary_format(self):
        result = evaluate_gate([], set(), {"a.py", "b.py"})
        assert "2 file(s) changed" in result.summary
        assert "0 node(s) in blast radius" in result.summary
        assert "0 blocking finding(s)" in result.summary

    def test_summary_includes_downgraded_count(self):
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["A"],
        }
        blast = {"A"}
        changed = {"other.py"}  # A not in changed files -> downgrade
        changed_nodes = set()  # empty -> A not in changed

        result = evaluate_gate(
            [finding], blast, changed, changed_nodes=changed_nodes
        )
        assert "1 pre-existing downgraded" in result.summary

    def test_empty_related_nodes(self):
        """Finding with empty related_nodes never matches blast radius."""
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": [],
        }
        result = evaluate_gate([finding], {"A", "B"}, {"a.py"})
        assert result.passed is True
        assert result.blocking_findings == []
        assert result.warnings == []

    def test_finding_missing_fields_uses_defaults(self):
        """Missing category/severity should not crash."""
        finding = {
            "related_nodes": ["A"],
        }
        result = evaluate_gate([finding], {"A"}, {"a.py"})
        assert result.passed is True
        # empty category + empty severity -> goes to warn branch
        assert len(result.warnings) == 1

    def test_severity_case_insensitive(self):
        """Severity comparison should be case-insensitive."""
        finding = {
            "category": "topology",
            "severity": "CRITICAL",
            "related_nodes": ["A"],
        }
        result = evaluate_gate(
            [finding], {"A"}, {"a.py"}, changed_nodes={"A"}
        )
        assert result.passed is False

    def test_downgraded_finding_preserves_original_fields(self):
        """Downgraded findings should preserve all original fields."""
        finding = {
            "id": "F99",
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["A"],
            "description": "Test finding",
            "custom_field": "preserved",
        }
        result = evaluate_gate(
            [finding], {"A"}, {"other.py"}, changed_nodes=set()
        )
        w = result.warnings[0]
        assert w["id"] == "F99"
        assert w["description"] == "Test finding"
        assert w["custom_field"] == "preserved"
        assert w["downgraded_from"] == "blocking"

    def test_downgrade_does_not_mutate_original(self):
        """Downgrading should not mutate the original finding dict."""
        finding = {
            "category": "topology",
            "severity": "critical",
            "related_nodes": ["A"],
        }
        evaluate_gate(
            [finding], {"A"}, {"other.py"}, changed_nodes=set()
        )
        assert "downgraded_from" not in finding
        assert "downgrade_reason" not in finding


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPDSIntegration:
    """End-to-end tests simulating realistic Collider output."""

    def test_full_pipeline_pass(self):
        """Simulate a clean push: no blocking findings in changed files."""
        G = nx.DiGraph()
        G.add_edges_from([
            ("src/core/pds.py:get_changed_files", "src/core/pds.py:evaluate_gate"),
            ("src/core/pds.py:evaluate_gate", "src/core/pds.py:GateResult"),
            ("src/core/other.py:helper", "src/core/pds.py:evaluate_gate"),
        ])

        changed_files = {"src/core/pds.py"}
        changed_nodes = {
            "src/core/pds.py:get_changed_files",
            "src/core/pds.py:evaluate_gate",
            "src/core/pds.py:GateResult",
        }
        blast = compute_blast_radius(G, changed_nodes)

        findings = [
            {
                "id": "CI-001",
                "category": "topology",
                "severity": "critical",
                "related_nodes": ["src/core/other.py:helper"],
                "description": "Pre-existing cycle",
            },
            {
                "id": "CI-002",
                "category": "bus_factor",
                "severity": "medium",
                "related_nodes": ["src/core/pds.py:evaluate_gate"],
                "description": "Single contributor",
            },
        ]

        result = evaluate_gate(findings, blast, changed_files, changed_nodes)

        assert result.passed is True
        # CI-001 is in blast radius but not in changed files -> downgraded
        # CI-002 is in warn category -> warning
        assert len(result.blocking_findings) == 0
        assert len(result.warnings) == 2

        # Verify serialization round-trip
        d = result.to_dict()
        assert d["passed"] is True
        assert isinstance(d["summary"], str)

    def test_full_pipeline_block(self):
        """Simulate a blocked push: critical finding in changed file."""
        G = nx.DiGraph()
        G.add_edges_from([
            ("src/core/pds.py:func_a", "src/core/pds.py:func_b"),
        ])

        changed_files = {"src/core/pds.py"}
        changed_nodes = {
            "src/core/pds.py:func_a",
            "src/core/pds.py:func_b",
        }
        blast = compute_blast_radius(G, changed_nodes)

        findings = [
            {
                "id": "CI-100",
                "category": "purpose_decomposition",
                "severity": "critical",
                "related_nodes": ["src/core/pds.py:func_a"],
                "description": "God function",
            },
        ]

        result = evaluate_gate(findings, blast, changed_files, changed_nodes)

        assert result.passed is False
        assert len(result.blocking_findings) == 1
        assert result.blocking_findings[0]["id"] == "CI-100"
        assert "1 blocking finding(s)" in result.summary

    def test_summary_counts_accuracy(self):
        """Verify all counts in summary string are accurate."""
        G = nx.DiGraph()
        G.add_edges_from([("A", "B"), ("B", "C")])
        blast = compute_blast_radius(G, {"B"})

        findings = [
            {"category": "topology", "severity": "critical", "related_nodes": ["B"]},
            {"category": "topology", "severity": "high", "related_nodes": ["A"]},
            {"category": "bus_factor", "severity": "low", "related_nodes": ["C"]},
        ]

        changed_files = {"b.py"}
        result = evaluate_gate(
            findings, blast, changed_files, changed_nodes={"B"}
        )

        assert f"{len(changed_files)} file(s) changed" in result.summary
        assert f"{len(blast)} node(s) in blast radius" in result.summary


# =============================================================================
# CONSTANTS SANITY CHECKS
# =============================================================================

class TestConstants:
    def test_blocking_categories_are_disjoint_from_warn(self):
        """Blocking and warn categories must not overlap."""
        assert BLOCKING_CATEGORIES.isdisjoint(WARN_CATEGORIES)

    def test_analyzable_extensions_are_dotted(self):
        """All extensions should start with a dot."""
        for ext in ANALYZABLE_EXTENSIONS:
            assert ext.startswith("."), f"Extension {ext} missing leading dot"

    def test_blocking_severities_are_lowercase(self):
        for sev in BLOCKING_SEVERITIES:
            assert sev == sev.lower()
