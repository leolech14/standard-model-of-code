"""
Tests for compartment_inferrer.py — auto-inferred architectural compartments.

Tests each of the 5 inference strategies individually, the synthesis voting
mechanism, dependency inference, and full pipeline integration.
"""

import pytest
import networkx as nx

from src.core.compartment_inferrer import (
    infer_compartments,
    _strategy_directory_clustering,
    _strategy_layer_agreement,
    _strategy_community_detection,
    _strategy_naming_convention,
    _strategy_rpbl_boundary,
    _synthesize_votes,
    _infer_allowed_deps,
    _extract_directory_prefix,
    _sanitize_compartment_name,
    _merge_tiny_groups,
    _match_naming_pattern,
    _build_compartment_globs,
    MIN_COMPARTMENT_SIZE,
)


# =============================================================================
# HELPER: Build test nodes
# =============================================================================

def _make_node(name, file_path, d2_layer="", rpbl=0.0, **kwargs):
    """Create a minimal test node."""
    node = {
        "id": name,
        "name": name,
        "file_path": file_path,
        "dimensions": {"D2_LAYER": d2_layer} if d2_layer else {},
        "rpbl_boundary": rpbl,
    }
    node.update(kwargs)
    return node


def _make_edge(source, target, edge_type="imports"):
    """Create a minimal test edge."""
    return {"source": source, "target": target, "edge_type": edge_type}


# =============================================================================
# STRATEGY 1: DIRECTORY CLUSTERING
# =============================================================================

class TestDirectoryClustering:
    def test_basic_three_directories(self):
        nodes = [
            _make_node("a1", "src/api/routes.py"),
            _make_node("a2", "src/api/auth.py"),
            _make_node("a3", "src/api/middleware.py"),
            _make_node("c1", "src/core/engine.py"),
            _make_node("c2", "src/core/parser.py"),
            _make_node("c3", "src/core/analyzer.py"),
            _make_node("m1", "src/models/user.py"),
            _make_node("m2", "src/models/order.py"),
            _make_node("m3", "src/models/product.py"),
        ]
        result = _strategy_directory_clustering(nodes)
        # Should get 3 compartments: api, core, models
        labels = set(result.values())
        assert len(labels) == 3
        assert result["a1"] == result["a2"] == result["a3"]
        assert result["c1"] == result["c2"] == result["c3"]
        assert result["m1"] == result["m2"] == result["m3"]
        # Labels should be clean
        assert result["a1"] in ("api", "core", "models")
        assert result["c1"] in ("api", "core", "models")

    def test_merge_tiny_groups(self):
        nodes = [
            _make_node("a1", "src/api/routes.py"),
            _make_node("a2", "src/api/auth.py"),
            _make_node("a3", "src/api/users.py"),
            _make_node("x1", "src/misc/helper.py"),  # Only 1 node -- tiny
        ]
        result = _strategy_directory_clustering(nodes)
        # x1 should be merged into the largest group (api)
        assert result["x1"] == result["a1"]

    def test_single_directory(self):
        nodes = [
            _make_node("a", "src/api/a.py"),
            _make_node("b", "src/api/b.py"),
            _make_node("c", "src/api/c.py"),
        ]
        result = _strategy_directory_clustering(nodes)
        assert len(set(result.values())) == 1

    def test_root_level_files(self):
        nodes = [
            _make_node("s", "setup.py"),
            _make_node("r", "README.md"),
            _make_node("c", "conftest.py"),
        ]
        result = _strategy_directory_clustering(nodes)
        # All root-level -> same compartment
        assert len(set(result.values())) == 1

    def test_skips_synthetic_nodes(self):
        nodes = [
            _make_node("real", "src/core/x.py"),
            _make_node("real2", "src/core/y.py"),
            _make_node("real3", "src/core/z.py"),
            _make_node("codome", "__codome__"),  # synthetic
        ]
        result = _strategy_directory_clustering(nodes)
        assert "codome" not in result

    def test_empty_nodes(self):
        assert _strategy_directory_clustering([]) == {}


class TestDirectoryHelpers:
    def test_extract_prefix_deep_path(self):
        assert _extract_directory_prefix("src/api/routes/users.py") == "src/api"

    def test_extract_prefix_two_components(self):
        assert _extract_directory_prefix("tests/test_api.py") == "tests"

    def test_extract_prefix_root(self):
        assert _extract_directory_prefix("setup.py") == "_root"

    def test_sanitize_src_prefix(self):
        assert _sanitize_compartment_name("src/api") == "api"
        assert _sanitize_compartment_name("src/core") == "core"

    def test_sanitize_lib_prefix(self):
        assert _sanitize_compartment_name("lib/utils") == "utils"

    def test_sanitize_no_prefix(self):
        assert _sanitize_compartment_name("tests") == "tests"

    def test_sanitize_root(self):
        assert _sanitize_compartment_name("_root") == "root"

    def test_merge_tiny_groups_basic(self):
        groups = {
            "big": ["a", "b", "c", "d"],
            "tiny": ["x"],
        }
        _merge_tiny_groups(groups, min_size=3)
        assert "tiny" not in groups
        assert "x" in groups["big"]

    def test_merge_tiny_groups_no_merge_needed(self):
        groups = {
            "big": ["a", "b", "c"],
            "also_big": ["x", "y", "z"],
        }
        _merge_tiny_groups(groups, min_size=3)
        assert len(groups) == 2


# =============================================================================
# STRATEGY 2: D2_LAYER AGREEMENT
# =============================================================================

class TestLayerAgreement:
    def test_pure_directory_no_split(self):
        nodes = [
            _make_node("a1", "src/api/a.py", d2_layer="Interface"),
            _make_node("a2", "src/api/b.py", d2_layer="Interface"),
            _make_node("a3", "src/api/c.py", d2_layer="Interface"),
        ]
        dir_assignments = {"a1": "api", "a2": "api", "a3": "api"}
        result = _strategy_layer_agreement(nodes, dir_assignments)
        # All same layer -> no split
        assert len(set(result.values())) == 1
        assert result["a1"] == "api"

    def test_mixed_directory_split(self):
        nodes = [
            _make_node("a1", "src/mixed/handler.py", d2_layer="Interface"),
            _make_node("a2", "src/mixed/service.py", d2_layer="Application"),
            _make_node("a3", "src/mixed/model.py", d2_layer="Core"),
        ]
        dir_assignments = {"a1": "mixed", "a2": "mixed", "a3": "mixed"}
        result = _strategy_layer_agreement(nodes, dir_assignments)
        # Three different layers -> should split
        labels = set(result.values())
        assert len(labels) == 3

    def test_dominant_layer_no_split(self):
        """If >80% of nodes share a layer, don't split."""
        nodes = [
            _make_node("a1", "src/api/a.py", d2_layer="Interface"),
            _make_node("a2", "src/api/b.py", d2_layer="Interface"),
            _make_node("a3", "src/api/c.py", d2_layer="Interface"),
            _make_node("a4", "src/api/d.py", d2_layer="Interface"),
            _make_node("a5", "src/api/e.py", d2_layer="Core"),  # 1/5 = 20%
        ]
        dir_assignments = {f"a{i}": "api" for i in range(1, 6)}
        result = _strategy_layer_agreement(nodes, dir_assignments)
        # 80% Interface -> no split
        assert len(set(result.values())) == 1

    def test_empty_dir_assignments(self):
        result = _strategy_layer_agreement([], {})
        assert result == {}


# =============================================================================
# STRATEGY 3: COMMUNITY DETECTION
# =============================================================================

class TestCommunityDetection:
    def test_two_clusters(self):
        """Graph with two clear communities should yield two compartments."""
        G = nx.DiGraph()
        # Cluster 1: tightly connected
        G.add_edges_from([("a1", "a2"), ("a2", "a3"), ("a3", "a1")])
        # Cluster 2: tightly connected
        G.add_edges_from([("b1", "b2"), ("b2", "b3"), ("b3", "b1")])
        # Weak link between clusters
        G.add_edge("a1", "b1")

        nodes = [
            _make_node("a1", "src/api/x.py"),
            _make_node("a2", "src/api/y.py"),
            _make_node("a3", "src/api/z.py"),
            _make_node("b1", "src/core/x.py"),
            _make_node("b2", "src/core/y.py"),
            _make_node("b3", "src/core/z.py"),
        ]
        result = _strategy_community_detection(nodes, G)
        # Should detect communities (at least 1 assignment)
        assert len(result) > 0

    def test_no_graph_returns_empty(self):
        nodes = [_make_node("a", "src/api/x.py")]
        result = _strategy_community_detection(nodes, None)
        assert result == {}

    def test_empty_graph(self):
        G = nx.DiGraph()
        result = _strategy_community_detection([], G)
        assert result == {}


# =============================================================================
# STRATEGY 4: NAMING CONVENTION
# =============================================================================

class TestNamingConvention:
    def test_django_patterns(self):
        nodes = [
            _make_node("v", "myapp/views/user_view.py"),
            _make_node("m", "myapp/models/user.py"),
            _make_node("s", "myapp/services/auth.py"),
        ]
        result = _strategy_naming_convention(nodes, None)
        assert result.get("v") == "interface"
        assert result.get("m") == "domain"
        assert result.get("s") == "application"

    def test_controller_suffix(self):
        nodes = [
            _make_node("uc", "src/user_controller.py"),
        ]
        result = _strategy_naming_convention(nodes, None)
        assert result.get("uc") == "interface"

    def test_unknown_pattern(self):
        nodes = [
            _make_node("x", "src/foo/bar.py"),
        ]
        result = _strategy_naming_convention(nodes, None)
        assert "x" not in result

    def test_test_directory(self):
        nodes = [
            _make_node("t", "tests/test_thing.py"),
        ]
        result = _strategy_naming_convention(nodes, None)
        assert result.get("t") == "test"

    def test_match_naming_pattern_directories(self):
        assert _match_naming_pattern("src/controllers/main.py") == "interface"
        assert _match_naming_pattern("app/models/user.py") == "domain"
        assert _match_naming_pattern("lib/utils/helpers.py") == "utility"

    def test_match_naming_pattern_no_match(self):
        assert _match_naming_pattern("src/foo/bar.py") is None


# =============================================================================
# STRATEGY 5: RPBL BOUNDARY
# =============================================================================

class TestRPBLBoundary:
    def test_high_boundary_reinforces(self):
        nodes = [
            _make_node("a1", "src/api/x.py", rpbl=0.9),
            _make_node("a2", "src/api/y.py", rpbl=0.3),
        ]
        dir_assignments = {"a1": "api", "a2": "api"}
        result = _strategy_rpbl_boundary(nodes, dir_assignments)
        # Only a1 has high RPBL
        assert "a1" in result
        assert "a2" not in result
        assert result["a1"] == "api"

    def test_no_dir_assignments(self):
        result = _strategy_rpbl_boundary([], {})
        assert result == {}


# =============================================================================
# SYNTHESIS: WEIGHTED VOTING
# =============================================================================

class TestWeightedVoting:
    def test_unanimous(self):
        """All strategies agree -> high confidence."""
        strat1 = ({"a": "api", "b": "core"}, 0.35)
        strat2 = ({"a": "api", "b": "core"}, 0.25)
        strat3 = ({"a": "api", "b": "core"}, 0.20)
        nodes = [_make_node("a", "x"), _make_node("b", "y")]
        assignments, confidence = _synthesize_votes([strat1, strat2, strat3], nodes)
        assert assignments["a"] == "api"
        assert assignments["b"] == "core"
        assert confidence["a"] == 1.0
        assert confidence["b"] == 1.0

    def test_highest_weight_wins(self):
        """Strategies disagree -> highest weight wins."""
        strat1 = ({"a": "api"}, 0.35)  # votes api
        strat2 = ({"a": "core"}, 0.25)  # votes core
        nodes = [_make_node("a", "x")]
        assignments, confidence = _synthesize_votes([strat1, strat2], nodes)
        assert assignments["a"] == "api"  # 0.35 > 0.25

    def test_single_strategy(self):
        """Only one strategy has opinion -> uses it."""
        strat1 = ({"a": "api"}, 0.35)
        nodes = [_make_node("a", "x")]
        assignments, confidence = _synthesize_votes([strat1], nodes)
        assert assignments["a"] == "api"
        assert confidence["a"] == 1.0

    def test_empty_strategies(self):
        assignments, confidence = _synthesize_votes([], [])
        assert assignments == {}
        assert confidence == {}

    def test_partial_coverage(self):
        """Strategies cover different nodes."""
        strat1 = ({"a": "api"}, 0.35)
        strat2 = ({"b": "core"}, 0.25)
        nodes = [_make_node("a", "x"), _make_node("b", "y")]
        assignments, confidence = _synthesize_votes([strat1, strat2], nodes)
        assert assignments["a"] == "api"
        assert assignments["b"] == "core"


# =============================================================================
# DEPENDENCY INFERENCE
# =============================================================================

class TestDependencyInference:
    def test_infer_deps_from_edges(self):
        assignments = {"a1": "api", "a2": "api", "c1": "core", "c2": "core"}
        edges = [
            _make_edge("a1", "c1"),
            _make_edge("a2", "c2"),  # 2 edges api->core
        ]
        deps = _infer_allowed_deps(assignments, edges)
        assert "core" in deps["api"]

    def test_no_cross_edges(self):
        assignments = {"a1": "api", "a2": "api"}
        edges = [_make_edge("a1", "a2")]  # intra-compartment
        deps = _infer_allowed_deps(assignments, edges)
        assert deps["api"] == []

    def test_threshold_not_met(self):
        """Single edge doesn't create dependency (noise filter)."""
        assignments = {"a1": "api", "c1": "core"}
        edges = [_make_edge("a1", "c1")]  # Only 1 edge
        deps = _infer_allowed_deps(assignments, edges)
        assert "core" not in deps.get("api", [])


# =============================================================================
# GLOB GENERATION
# =============================================================================

class TestGlobGeneration:
    def test_basic_globs(self):
        assignments = {"a1": "api", "a2": "api", "c1": "core"}
        node_by_id = {
            "a1": {"file_path": "src/api/routes.py"},
            "a2": {"file_path": "src/api/auth.py"},
            "c1": {"file_path": "src/core/engine.py"},
        }
        globs = _build_compartment_globs(assignments, node_by_id)
        assert "api" in globs
        assert "core" in globs
        assert any("src/api" in g for g in globs["api"])


# =============================================================================
# INTEGRATION: FULL PIPELINE
# =============================================================================

class TestInferCompartmentsFull:
    def test_end_to_end(self):
        """Full inference with realistic node set."""
        nodes = [
            _make_node("a1", "src/api/routes.py", d2_layer="Interface"),
            _make_node("a2", "src/api/auth.py", d2_layer="Interface"),
            _make_node("a3", "src/api/middleware.py", d2_layer="Interface"),
            _make_node("c1", "src/core/engine.py", d2_layer="Core"),
            _make_node("c2", "src/core/parser.py", d2_layer="Core"),
            _make_node("c3", "src/core/analyzer.py", d2_layer="Core"),
            _make_node("m1", "src/models/user.py", d2_layer="Core"),
            _make_node("m2", "src/models/order.py", d2_layer="Core"),
            _make_node("m3", "src/models/product.py", d2_layer="Core"),
        ]
        edges = [
            _make_edge("a1", "c1"),
            _make_edge("a2", "c2"),
            _make_edge("c1", "m1"),
            _make_edge("c2", "m2"),
        ]
        result = infer_compartments(nodes, edges)

        # Must have compartments key
        assert "compartments" in result
        assert len(result["compartments"]) >= 2  # At least api + core or similar

        # Each compartment has required keys
        for comp_name, comp_def in result["compartments"].items():
            assert "globs" in comp_def
            assert "allowed_deps" in comp_def
            assert isinstance(comp_def["globs"], list)
            assert isinstance(comp_def["allowed_deps"], list)

        # Metadata present
        meta = result["inference_metadata"]
        assert meta["total_nodes_assigned"] > 0
        assert meta["source"] == "inferred"

    def test_output_structure_matches_load_boundaries(self):
        """Output must be structurally compatible with boundary_validator.load_boundaries()."""
        nodes = [
            _make_node("a", "src/api/x.py", d2_layer="Interface"),
            _make_node("b", "src/api/y.py", d2_layer="Interface"),
            _make_node("c", "src/api/z.py", d2_layer="Interface"),
            _make_node("d", "src/core/a.py", d2_layer="Core"),
            _make_node("e", "src/core/b.py", d2_layer="Core"),
            _make_node("f", "src/core/c.py", d2_layer="Core"),
        ]
        edges = [_make_edge("a", "d"), _make_edge("b", "e")]
        result = infer_compartments(nodes, edges)

        # Structure validation: same shape as load_boundaries()
        assert "compartments" in result
        compartments = result["compartments"]
        assert isinstance(compartments, dict)
        for comp_name, comp_def in compartments.items():
            assert isinstance(comp_name, str)
            assert isinstance(comp_def, dict)
            assert "globs" in comp_def
            assert "allowed_deps" in comp_def
            assert isinstance(comp_def["globs"], list)
            assert isinstance(comp_def["allowed_deps"], list)
            for g in comp_def["globs"]:
                assert isinstance(g, str)
            for d in comp_def["allowed_deps"]:
                assert isinstance(d, str)

    def test_pipeline_flow(self):
        """Inferred boundaries pass through assign_compartments -> validate_boundaries."""
        from src.core.boundary_validator import assign_compartments, validate_boundaries

        nodes = [
            _make_node("a", "src/api/x.py", d2_layer="Interface"),
            _make_node("b", "src/api/y.py", d2_layer="Interface"),
            _make_node("c", "src/api/z.py", d2_layer="Interface"),
            _make_node("d", "src/core/a.py", d2_layer="Core"),
            _make_node("e", "src/core/b.py", d2_layer="Core"),
            _make_node("f", "src/core/c.py", d2_layer="Core"),
        ]
        edges = [_make_edge("a", "d"), _make_edge("b", "e")]

        # Infer
        inferred = infer_compartments(nodes, edges)
        assert inferred["compartments"]

        # Assign (uses same interface as declared boundaries)
        assignment_result = assign_compartments(nodes, inferred)
        assert assignment_result["mapped_count"] >= 0

        # Validate
        validation = validate_boundaries(
            nodes, edges,
            assignment_result["assignments"],
            inferred,
        )
        assert "compliance_rate" in validation
        assert 0.0 <= validation["compliance_rate"] <= 1.0

    def test_empty_nodes(self):
        result = infer_compartments([], [])
        assert result["compartments"] == {}
        assert result["inference_metadata"]["total_nodes_assigned"] == 0

    def test_with_networkx_graph(self):
        """Test with G_full provided for community detection."""
        G = nx.DiGraph()
        G.add_edges_from([("a1", "a2"), ("a2", "a3"), ("b1", "b2"), ("b2", "b3")])

        nodes = [
            _make_node("a1", "src/api/x.py"),
            _make_node("a2", "src/api/y.py"),
            _make_node("a3", "src/api/z.py"),
            _make_node("b1", "src/core/x.py"),
            _make_node("b2", "src/core/y.py"),
            _make_node("b3", "src/core/z.py"),
        ]
        edges = [
            _make_edge("a1", "a2"), _make_edge("a2", "a3"),
            _make_edge("b1", "b2"), _make_edge("b2", "b3"),
        ]
        result = infer_compartments(nodes, edges, G_full=G)
        assert result["compartments"]
        meta = result["inference_metadata"]
        # Community detection should have contributed
        assert "community" in meta.get("strategy_contributions", {})
