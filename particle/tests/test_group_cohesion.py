"""
Tests for group cohesion metrics (Feature 4).

Validates:
- Single group perfect/zero cohesion
- Multi-group balanced coupling
- Martin's instability metric
- Coupling matrix correctness
- Overall modularity computation
- Edge cases (empty groups, unmapped nodes)
- Summary formatting
"""

import pytest
import sys
from pathlib import Path

# Add src/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))

from group_cohesion import compute_group_cohesion, format_cohesion_summary


# =============================================================================
# FIXTURES
# =============================================================================

def make_nodes(*ids):
    """Create minimal node dicts from IDs."""
    return [{"id": nid} for nid in ids]


def make_edges(*triples):
    """Create edge dicts from (source, target, type) tuples."""
    return [
        {"source": s, "target": t, "edge_type": typ}
        for s, t, typ in triples
    ]


# =============================================================================
# SINGLE GROUP COHESION
# =============================================================================

class TestSingleGroupPerfectCohesion:
    """All edges internal -> cohesion 1.0."""

    def test_all_internal(self):
        nodes = make_nodes("a", "b", "c")
        edges = make_edges(
            ("a", "b", "calls"),
            ("b", "c", "calls"),
            ("a", "c", "imports"),
        )
        assignments = {"a": "core", "b": "core", "c": "core"}

        result = compute_group_cohesion(nodes, edges, assignments)
        group = result["per_group"]["core"]

        assert group["internal_edges"] == 3
        assert group["external_in"] == 0
        assert group["external_out"] == 0
        assert group["cohesion_ratio"] == 1.0

    def test_instability_zero_when_all_internal(self):
        """No external edges -> instability 0.0."""
        nodes = make_nodes("a", "b")
        edges = make_edges(("a", "b", "calls"))
        assignments = {"a": "core", "b": "core"}

        result = compute_group_cohesion(nodes, edges, assignments)
        assert result["per_group"]["core"]["instability"] == 0.0


class TestSingleGroupZeroCohesion:
    """All edges external -> cohesion 0.0."""

    def test_all_external(self):
        nodes = make_nodes("a", "b")
        edges = make_edges(
            ("a", "b", "calls"),
            ("b", "a", "calls"),
        )
        # a in 'api', b in 'core' — all edges cross boundaries
        assignments = {"a": "api", "b": "core"}

        result = compute_group_cohesion(nodes, edges, assignments)

        api = result["per_group"]["api"]
        assert api["internal_edges"] == 0
        assert api["external_out"] == 1
        assert api["external_in"] == 1
        assert api["cohesion_ratio"] == 0.0

        core = result["per_group"]["core"]
        assert core["cohesion_ratio"] == 0.0


# =============================================================================
# TWO GROUPS — BALANCED COUPLING
# =============================================================================

class TestTwoGroupsBalanced:
    """Symmetric coupling between two compartments."""

    def setup_method(self):
        self.nodes = make_nodes("a1", "a2", "b1", "b2")
        self.edges = make_edges(
            # Internal to api
            ("a1", "a2", "calls"),
            # Internal to core
            ("b1", "b2", "calls"),
            # Cross: api -> core
            ("a1", "b1", "imports"),
            # Cross: core -> api
            ("b2", "a2", "calls"),
        )
        self.assignments = {
            "a1": "api", "a2": "api",
            "b1": "core", "b2": "core",
        }
        self.result = compute_group_cohesion(
            self.nodes, self.edges, self.assignments
        )

    def test_internal_counts(self):
        assert self.result["per_group"]["api"]["internal_edges"] == 1
        assert self.result["per_group"]["core"]["internal_edges"] == 1

    def test_external_counts(self):
        api = self.result["per_group"]["api"]
        assert api["external_out"] == 1
        assert api["external_in"] == 1

        core = self.result["per_group"]["core"]
        assert core["external_out"] == 1
        assert core["external_in"] == 1

    def test_cohesion_is_one_third(self):
        """1 internal / (1 internal + 1 in + 1 out) = 1/3."""
        api = self.result["per_group"]["api"]
        assert abs(api["cohesion_ratio"] - 1/3) < 0.001

    def test_instability_is_half(self):
        """1 out / (1 out + 1 in) = 0.5."""
        api = self.result["per_group"]["api"]
        assert api["instability"] == 0.5

    def test_coupling_matrix_symmetric(self):
        matrix = self.result["coupling_matrix"]
        assert matrix["api->core"] == 1
        assert matrix["core->api"] == 1


# =============================================================================
# INSTABILITY METRIC
# =============================================================================

class TestInstabilityMetric:
    """Validate Martin's instability I = Ce / (Ca + Ce)."""

    def test_stable_leaf(self):
        """Leaf module: many incoming, no outgoing -> I = 0.0."""
        nodes = make_nodes("a", "b", "leaf")
        edges = make_edges(
            ("a", "leaf", "imports"),
            ("b", "leaf", "imports"),
        )
        assignments = {"a": "api", "b": "core", "leaf": "models"}

        result = compute_group_cohesion(nodes, edges, assignments)
        models = result["per_group"]["models"]

        assert models["external_in"] == 2
        assert models["external_out"] == 0
        assert models["instability"] == 0.0

    def test_unstable_hub(self):
        """Hub module: no incoming, many outgoing -> I = 1.0."""
        nodes = make_nodes("hub", "x", "y")
        edges = make_edges(
            ("hub", "x", "imports"),
            ("hub", "y", "imports"),
        )
        assignments = {"hub": "api", "x": "core", "y": "models"}

        result = compute_group_cohesion(nodes, edges, assignments)
        api = result["per_group"]["api"]

        assert api["external_in"] == 0
        assert api["external_out"] == 2
        assert api["instability"] == 1.0

    def test_mixed_stability(self):
        """3 out, 1 in -> I = 3/4 = 0.75."""
        nodes = make_nodes("h", "a", "b", "c", "d")
        edges = make_edges(
            ("h", "a", "calls"),
            ("h", "b", "calls"),
            ("h", "c", "calls"),
            ("d", "h", "calls"),
        )
        assignments = {
            "h": "hub", "a": "x", "b": "y", "c": "z", "d": "w",
        }

        result = compute_group_cohesion(nodes, edges, assignments)
        hub = result["per_group"]["hub"]
        assert hub["instability"] == 0.75


# =============================================================================
# COUPLING MATRIX
# =============================================================================

class TestCouplingMatrix:
    """Verify cross-compartment edge count matrix."""

    def test_directed_counts(self):
        nodes = make_nodes("a1", "a2", "b1", "c1")
        edges = make_edges(
            ("a1", "b1", "calls"),
            ("a2", "b1", "calls"),
            ("a1", "c1", "imports"),
            ("b1", "c1", "imports"),
        )
        assignments = {
            "a1": "api", "a2": "api",
            "b1": "core",
            "c1": "models",
        }

        result = compute_group_cohesion(nodes, edges, assignments)
        matrix = result["coupling_matrix"]

        assert matrix["api->core"] == 2
        assert matrix["api->models"] == 1
        assert matrix["core->models"] == 1
        assert "models->api" not in matrix  # No reverse edge

    def test_coupling_partners_track(self):
        """per_group should track who each compartment talks to."""
        nodes = make_nodes("a", "b", "c")
        edges = make_edges(
            ("a", "b", "calls"),
            ("a", "c", "calls"),
            ("a", "c", "imports"),
        )
        assignments = {"a": "api", "b": "core", "c": "models"}

        result = compute_group_cohesion(nodes, edges, assignments)
        partners = result["per_group"]["api"]["coupling_partners"]

        assert partners["core"] == 1
        assert partners["models"] == 2


# =============================================================================
# OVERALL MODULARITY
# =============================================================================

class TestOverallModularity:
    """Weighted average cohesion computation."""

    def test_perfect_modularity(self):
        """All edges internal -> modularity 1.0."""
        nodes = make_nodes("a", "b", "c", "d")
        edges = make_edges(
            ("a", "b", "calls"),
            ("c", "d", "calls"),
        )
        assignments = {
            "a": "grp1", "b": "grp1",
            "c": "grp2", "d": "grp2",
        }

        result = compute_group_cohesion(nodes, edges, assignments)
        assert result["overall_modularity"] == 1.0

    def test_zero_modularity(self):
        """All edges cross boundaries -> modularity 0.0."""
        nodes = make_nodes("a", "b")
        edges = make_edges(("a", "b", "calls"))
        assignments = {"a": "x", "b": "y"}

        result = compute_group_cohesion(nodes, edges, assignments)
        assert result["overall_modularity"] == 0.0

    def test_mixed_modularity(self):
        """Known mix: 2 internal + 2 cross = some intermediate value."""
        nodes = make_nodes("a1", "a2", "b1", "b2")
        edges = make_edges(
            ("a1", "a2", "calls"),   # internal api
            ("b1", "b2", "calls"),   # internal core
            ("a1", "b1", "imports"), # cross
            ("b2", "a2", "calls"),   # cross
        )
        assignments = {
            "a1": "api", "a2": "api",
            "b1": "core", "b2": "core",
        }

        result = compute_group_cohesion(nodes, edges, assignments)
        # Each group: 1 internal, 1 in, 1 out -> cohesion = 1/3
        # All groups equal weight -> modularity = 1/3
        assert abs(result["overall_modularity"] - 1/3) < 0.001


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Graceful handling of degenerate inputs."""

    def test_empty_group(self):
        """Compartment with assigned nodes but no edges."""
        nodes = make_nodes("a")
        edges = []
        assignments = {"a": "lonely"}

        result = compute_group_cohesion(nodes, edges, assignments)
        group = result["per_group"]["lonely"]

        assert group["node_count"] == 1
        assert group["internal_edges"] == 0
        assert group["cohesion_ratio"] == 1.0  # vacuously cohesive
        assert group["instability"] == 0.0      # vacuously stable

    def test_no_assignments(self):
        """No nodes assigned -> empty result."""
        nodes = make_nodes("a", "b")
        edges = make_edges(("a", "b", "calls"))
        assignments = {}

        result = compute_group_cohesion(nodes, edges, assignments)

        assert result["per_group"] == {}
        assert result["overall_modularity"] == 1.0
        assert result["coupling_matrix"] == {}

    def test_unmapped_nodes_in_edges(self):
        """Edges referencing unmapped nodes should be skipped."""
        nodes = make_nodes("a", "b", "unmapped")
        edges = make_edges(
            ("a", "b", "calls"),
            ("a", "unmapped", "imports"),  # unmapped target
        )
        assignments = {"a": "api", "b": "api"}
        # "unmapped" is not in assignments

        result = compute_group_cohesion(nodes, edges, assignments)
        api = result["per_group"]["api"]

        # Only the a->b edge counted (both mapped), unmapped edge skipped
        assert api["internal_edges"] == 1
        assert api["external_out"] == 0

    def test_single_node_group(self):
        """Group with one node, self-loop edge."""
        nodes = make_nodes("a")
        edges = make_edges(("a", "a", "recursive"))
        assignments = {"a": "solo"}

        result = compute_group_cohesion(nodes, edges, assignments)
        solo = result["per_group"]["solo"]

        assert solo["internal_edges"] == 1
        assert solo["cohesion_ratio"] == 1.0


# =============================================================================
# SUMMARY FORMATTING
# =============================================================================

class TestFormatSummary:
    """Verify human-readable output."""

    def test_contains_key_sections(self):
        data = {
            "per_group": {
                "api": {
                    "node_count": 5,
                    "internal_edges": 10,
                    "external_in": 3,
                    "external_out": 2,
                    "cohesion_ratio": 0.6667,
                    "instability": 0.4,
                    "coupling_partners": {"core": 2},
                },
            },
            "overall_modularity": 0.75,
            "coupling_matrix": {"api->core": 2},
        }

        summary = format_cohesion_summary(data)
        assert "Group Cohesion Report" in summary
        assert "api:" in summary
        assert "75.0%" in summary  # modularity
        assert "Instability: 0.40" in summary
        assert "api->core: 2" in summary

    def test_empty_data(self):
        data = {
            "per_group": {},
            "overall_modularity": 1.0,
            "coupling_matrix": {},
        }
        summary = format_cohesion_summary(data)
        assert "Group Cohesion Report" in summary
        assert "100.0%" in summary
