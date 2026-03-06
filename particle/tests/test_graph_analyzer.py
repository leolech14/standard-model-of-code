"""
Tests for graph_analyzer.py — the NetworkX-based graph analysis module.

Covers:
- NodeStats / GraphAnalysisResult dataclasses
- get_filtered_degree(): dependency vs structural edge filtering
- load_graph(): JSON → DiGraph construction with multiple edge key formats
- find_bottlenecks(): betweenness centrality ranking
- find_pagerank(): importance ranking
- find_communities(): Louvain/connected-components fallback
- find_bridges(): bridge edge detection
- shortest_path(): path resolution with partial name matching
- suggest_refactoring_cuts(): edge betweenness recommendations
"""
import json
import os
import sys
import tempfile

import networkx as nx
import pytest

# Add src/core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from graph_analyzer import (
    DEPENDENCY_EDGE_TYPES,
    STRUCTURAL_EDGE_TYPES,
    NodeStats,
    GraphAnalysisResult,
    get_filtered_degree,
    load_graph,
    find_bottlenecks,
    find_pagerank,
    find_communities,
    find_bridges,
    shortest_path,
    suggest_refactoring_cuts,
)


# =============================================================================
# FIXTURES
# =============================================================================

def _build_star_graph() -> nx.DiGraph:
    """Star topology: hub → {spoke_0, spoke_1, spoke_2, spoke_3}."""
    G = nx.DiGraph()
    G.add_node("hub", name="hub_func", kind="function", file="hub.py")
    for i in range(4):
        G.add_node(f"spoke_{i}", name=f"spoke_{i}", kind="function", file=f"spoke_{i}.py")
        G.add_edge("hub", f"spoke_{i}", kind="calls", family="Dependency")
    return G


def _build_chain_graph() -> nx.DiGraph:
    """Chain topology: A → B → C → D."""
    G = nx.DiGraph()
    for label in "ABCD":
        G.add_node(label, name=f"func_{label}", kind="function", file=f"{label.lower()}.py")
    for src, tgt in [("A", "B"), ("B", "C"), ("C", "D")]:
        G.add_edge(src, tgt, kind="calls", family="Dependency")
    return G


def _build_mixed_edge_graph() -> nx.DiGraph:
    """Graph with both dependency and structural edges for filtered degree testing."""
    G = nx.DiGraph()
    G.add_node("A", name="A", kind="class", file="a.py")
    G.add_node("B", name="B", kind="function", file="b.py")
    G.add_node("C", name="C", kind="function", file="c.py")
    G.add_node("D", name="D", kind="class", file="d.py")

    # Dependency edges (should count for call degree)
    G.add_edge("A", "B", kind="calls")
    G.add_edge("A", "C", kind="imports")
    G.add_edge("B", "C", kind="uses")

    # Structural edges (should NOT count for call degree)
    G.add_edge("A", "D", kind="contains")
    G.add_edge("D", "A", kind="inherits")

    return G


def _write_graph_json(data: dict) -> str:
    """Write graph data to a temp JSON file, return path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return path


# =============================================================================
# NodeStats dataclass
# =============================================================================

class TestNodeStats:

    def test_defaults(self):
        ns = NodeStats(id="n1", name="func", kind="function", file="f.py")
        assert ns.in_degree == 0
        assert ns.out_degree == 0
        assert ns.call_in_degree == 0
        assert ns.call_out_degree == 0
        assert ns.betweenness == 0.0
        assert ns.pagerank == 0.0
        assert ns.community == -1

    def test_custom_values(self):
        ns = NodeStats(id="n1", name="func", kind="function", file="f.py",
                       in_degree=5, betweenness=0.42)
        assert ns.in_degree == 5
        assert ns.betweenness == 0.42


# =============================================================================
# get_filtered_degree
# =============================================================================

class TestGetFilteredDegree:
    """Tests for dependency-only degree calculation."""

    def test_in_degree_dependency_only(self):
        G = _build_mixed_edge_graph()
        # C has incoming: A→C (imports), B→C (uses) = 2 dependency edges
        assert get_filtered_degree(G, "C", "in") == 2

    def test_in_degree_excludes_structural(self):
        G = _build_mixed_edge_graph()
        # A has incoming: D→A (inherits) = structural, should be 0 dep edges in
        assert get_filtered_degree(G, "A", "in") == 0

    def test_out_degree_dependency_only(self):
        G = _build_mixed_edge_graph()
        # A has outgoing: A→B (calls), A→C (imports) = 2 dep, A→D (contains) = structural
        assert get_filtered_degree(G, "A", "out") == 2

    def test_both_direction(self):
        G = _build_mixed_edge_graph()
        # B: in=A→B(calls)=1, out=B→C(uses)=1 → total=2
        assert get_filtered_degree(G, "B", "both") == 2

    def test_isolated_node(self):
        G = nx.DiGraph()
        G.add_node("lonely", name="lonely", kind="function", file="l.py")
        assert get_filtered_degree(G, "lonely", "in") == 0
        assert get_filtered_degree(G, "lonely", "out") == 0

    def test_custom_edge_types(self):
        G = _build_mixed_edge_graph()
        # Count only structural edges for A outgoing: A→D(contains) = 1
        assert get_filtered_degree(G, "A", "out", STRUCTURAL_EDGE_TYPES) == 1


# =============================================================================
# load_graph
# =============================================================================

class TestLoadGraph:

    def test_load_components_and_edges(self):
        data = {
            "components": {
                "n1": {"name": "func_a", "kind": "function", "file": "a.py"},
                "n2": {"name": "func_b", "kind": "function", "file": "b.py"},
            },
            "edges": [
                {"source": "n1", "target": "n2", "kind": "calls"},
            ],
        }
        path = _write_graph_json(data)
        try:
            G = load_graph(path)
            assert len(G.nodes) == 2
            assert len(G.edges) == 1
            assert G.nodes["n1"]["name"] == "func_a"
        finally:
            os.unlink(path)

    def test_load_relationships_key(self):
        """load_graph supports 'relationships' as fallback for 'edges'."""
        data = {
            "components": {"x": {"name": "x", "kind": "class", "file": "x.py"}},
            "relationships": [
                {"from": "x", "to": "y", "kind": "calls"},
            ],
        }
        path = _write_graph_json(data)
        try:
            G = load_graph(path)
            # 'y' should be auto-created from edge
            assert "y" in G.nodes
            assert len(G.edges) == 1
        finally:
            os.unlink(path)

    def test_load_edge_first_auto_creates_nodes(self):
        """Nodes referenced in edges but not in components are auto-created."""
        data = {
            "components": {},
            "edges": [
                {"src": "a", "dst": "b", "kind": "calls"},
            ],
        }
        path = _write_graph_json(data)
        try:
            G = load_graph(path)
            assert "a" in G.nodes
            assert "b" in G.nodes
        finally:
            os.unlink(path)

    def test_load_empty_graph(self):
        data = {"components": {}, "edges": []}
        path = _write_graph_json(data)
        try:
            G = load_graph(path)
            assert len(G.nodes) == 0
            assert len(G.edges) == 0
        finally:
            os.unlink(path)


# =============================================================================
# find_bottlenecks
# =============================================================================

class TestFindBottlenecks:

    def test_chain_center_is_bottleneck(self):
        """In A → B → C → D, B and C have highest betweenness."""
        G = _build_chain_graph()
        bns = find_bottlenecks(G, top_n=4)
        assert len(bns) == 4
        # B and C should have higher betweenness than A and D
        names_by_centrality = [ns.name for ns in bns]
        # B is on paths A→C, A→D; C is on paths A→D, B→D
        assert names_by_centrality[0] in ("func_B", "func_C")

    def test_star_hub_is_bottleneck(self):
        """In star graph, hub has highest betweenness."""
        G = _build_star_graph()
        bns = find_bottlenecks(G, top_n=1)
        assert len(bns) == 1
        assert bns[0].name == "hub_func"

    def test_top_n_limits(self):
        G = _build_chain_graph()
        bns = find_bottlenecks(G, top_n=2)
        assert len(bns) == 2

    def test_populates_node_stats(self):
        G = _build_star_graph()
        bns = find_bottlenecks(G, top_n=1)
        hub = bns[0]
        assert hub.id == "hub"
        assert hub.out_degree == 4
        assert hub.call_out_degree == 4  # all edges are 'calls'
        assert hub.betweenness >= 0


# =============================================================================
# find_pagerank
# =============================================================================

class TestFindPagerank:

    def test_chain_end_has_rank(self):
        """In A → B → C → D, nodes with incoming edges accumulate rank."""
        G = _build_chain_graph()
        pr = find_pagerank(G, top_n=4)
        assert len(pr) == 4
        # All nodes should have non-zero pagerank
        for ns in pr:
            assert ns.pagerank > 0

    def test_star_spokes_have_rank(self):
        """In star graph, spokes receive PageRank from hub."""
        G = _build_star_graph()
        pr = find_pagerank(G, top_n=5)
        assert len(pr) == 5

    def test_top_n_limits(self):
        G = _build_star_graph()
        pr = find_pagerank(G, top_n=2)
        assert len(pr) == 2

    def test_populates_filtered_degrees(self):
        G = _build_mixed_edge_graph()
        pr = find_pagerank(G, top_n=4)
        # At least one node should have call_in_degree or call_out_degree
        assert any(ns.call_in_degree > 0 or ns.call_out_degree > 0 for ns in pr)


# =============================================================================
# find_communities
# =============================================================================

class TestFindCommunities:

    def test_disconnected_components(self):
        """Two disconnected clusters should be separate communities."""
        G = nx.DiGraph()
        # Cluster 1
        G.add_edge("a1", "a2")
        G.add_edge("a2", "a3")
        # Cluster 2
        G.add_edge("b1", "b2")
        G.add_edge("b2", "b3")

        comms = find_communities(G)
        assert len(comms) >= 2
        # Total nodes across all communities should be 6
        all_nodes = []
        for members in comms.values():
            all_nodes.extend(members)
        assert len(all_nodes) == 6

    def test_single_component(self):
        """Fully connected graph should have 1 community."""
        G = _build_chain_graph()
        comms = find_communities(G)
        assert len(comms) >= 1
        # All 4 nodes should appear somewhere
        all_nodes = []
        for members in comms.values():
            all_nodes.extend(members)
        assert len(all_nodes) == 4

    def test_empty_graph(self):
        G = nx.DiGraph()
        comms = find_communities(G)
        assert isinstance(comms, dict)


# =============================================================================
# find_bridges
# =============================================================================

class TestFindBridges:

    def test_chain_all_bridges(self):
        """In chain A → B → C → D, all edges are bridges."""
        G = _build_chain_graph()
        bridges = find_bridges(G)
        # In undirected chain, there should be 3 bridges
        assert len(bridges) == 3

    def test_cycle_no_bridges(self):
        """In a cycle, no edges are bridges."""
        G = nx.DiGraph()
        G.add_edge("A", "B")
        G.add_edge("B", "C")
        G.add_edge("C", "A")
        bridges = find_bridges(G)
        assert len(bridges) == 0

    def test_limit_parameter(self):
        G = _build_chain_graph()
        bridges = find_bridges(G, limit=1)
        assert len(bridges) == 1


# =============================================================================
# shortest_path
# =============================================================================

class TestShortestPath:

    def test_direct_path(self):
        G = _build_chain_graph()
        path = shortest_path(G, "A", "D")
        assert path == ["A", "B", "C", "D"]

    def test_adjacent_nodes(self):
        G = _build_chain_graph()
        path = shortest_path(G, "A", "B")
        assert path == ["A", "B"]

    def test_no_path(self):
        G = _build_chain_graph()
        # D → A has no path in directed graph
        path = shortest_path(G, "D", "A")
        assert path == []

    def test_partial_name_resolution(self):
        """shortest_path resolves partial names via name attribute."""
        G = _build_chain_graph()
        # Nodes have name="func_A", etc. — resolve by name attribute
        path = shortest_path(G, "func_A", "func_D")
        assert len(path) == 4

    def test_nonexistent_node(self):
        G = _build_chain_graph()
        path = shortest_path(G, "MISSING", "A")
        assert path == []

    def test_pipe_delimited_ids(self):
        """Collider uses pipe-delimited IDs: file|name|kind."""
        G = nx.DiGraph()
        G.add_node("a.py|setup|function", name="setup", kind="function", file="a.py")
        G.add_node("b.py|teardown|function", name="teardown", kind="function", file="b.py")
        G.add_edge("a.py|setup|function", "b.py|teardown|function", kind="calls")
        path = shortest_path(G, "setup", "teardown")
        assert len(path) == 2


# =============================================================================
# suggest_refactoring_cuts
# =============================================================================

class TestSuggestRefactoringCuts:

    def test_returns_recommendations(self):
        G = _build_chain_graph()
        cuts = suggest_refactoring_cuts(G, top_n=3)
        assert len(cuts) == 3
        for cut in cuts:
            assert 'source' in cut
            assert 'target' in cut
            assert 'centrality' in cut
            assert 'recommendation' in cut

    def test_top_n_limits(self):
        G = _build_star_graph()
        cuts = suggest_refactoring_cuts(G, top_n=2)
        assert len(cuts) == 2

    def test_centrality_is_positive(self):
        G = _build_chain_graph()
        cuts = suggest_refactoring_cuts(G, top_n=3)
        for cut in cuts:
            assert cut['centrality'] > 0


# =============================================================================
# GraphAnalysisResult dataclass
# =============================================================================

class TestGraphAnalysisResult:

    def test_defaults(self):
        r = GraphAnalysisResult()
        assert r.node_count == 0
        assert r.edge_count == 0
        assert r.bottlenecks == []
        assert r.top_pagerank == []
        assert r.communities == {}
        assert r.bridges == []

    def test_mutable_defaults_independent(self):
        """Verify dataclass default_factory produces independent lists."""
        r1 = GraphAnalysisResult()
        r2 = GraphAnalysisResult()
        r1.bottlenecks.append("test")
        assert len(r2.bottlenecks) == 0
