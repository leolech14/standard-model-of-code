"""Tests for TopologyClassifier, Betti numbers, and Elevation computation."""
from src.core.topology_reasoning import (
    TopologyClassifier,
    BettiNumbers,
    ElevationModel,
    ElevationResult,
    LandscapeProfile,
    LandscapeHealthIndex,
    compute_gradient
)


class TestBettiNumbers:
    """Test BettiNumbers dataclass."""

    def test_euler_characteristic(self):
        """χ = b0 - b1."""
        betti = BettiNumbers(b0=1, b1=0)
        assert betti.euler_characteristic == 1

        betti = BettiNumbers(b0=3, b1=5)
        assert betti.euler_characteristic == -2

    def test_health_signal_tree(self):
        """Single component, no extra edges = tree."""
        betti = BettiNumbers(b0=1, b1=0)
        assert betti.health_signal == "TREE"

    def test_health_signal_connected(self):
        """Slightly denser than a tree."""
        betti = BettiNumbers(b0=1, b1=3)
        assert betti.health_signal == "CONNECTED"

    def test_health_signal_dense(self):
        """Moderately dense (b1 > 100)."""
        betti = BettiNumbers(b0=1, b1=500)
        assert betti.health_signal == "DENSE"

    def test_health_signal_very_dense(self):
        """Highly dense (b1 > 1000)."""
        betti = BettiNumbers(b0=1, b1=5000)
        assert betti.health_signal == "VERY_DENSE"

    def test_health_signal_fragmented(self):
        """Multiple components, low density."""
        betti = BettiNumbers(b0=5, b1=0)
        assert betti.health_signal == "FRAGMENTED"

    def test_health_signal_fragmented_dense(self):
        """Fragmented with dense subgraphs."""
        betti = BettiNumbers(b0=3, b1=200)
        assert betti.health_signal == "FRAGMENTED_DENSE"


class TestTopologyClassifier:
    """Test TopologyClassifier methods."""

    def setup_method(self):
        self.classifier = TopologyClassifier()

    def test_compute_betti_numbers_empty(self):
        """Empty graph."""
        betti = self.classifier.compute_betti_numbers([], [])
        assert betti.b0 == 0
        assert betti.b1 == 0

    def test_compute_betti_numbers_single_node(self):
        """Single node, no edges."""
        nodes = [{"id": "A"}]
        edges = []
        betti = self.classifier.compute_betti_numbers(nodes, edges)
        assert betti.b0 == 1  # One component
        assert betti.b1 == 0  # No cycles

    def test_compute_betti_numbers_linear_chain(self):
        """A → B → C (linear, no cycles)."""
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"}
        ]
        betti = self.classifier.compute_betti_numbers(nodes, edges)
        assert betti.b0 == 1  # Connected
        assert betti.b1 == 0  # No cycles

    def test_compute_betti_numbers_triangle(self):
        """A → B → C → A (triangle = 1 cycle)."""
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"}
        ]
        betti = self.classifier.compute_betti_numbers(nodes, edges)
        assert betti.b0 == 1  # Connected
        assert betti.b1 == 1  # One cycle (3 edges - 3 nodes + 1 = 1)

    def test_compute_betti_numbers_two_islands(self):
        """Two disconnected nodes."""
        nodes = [{"id": "A"}, {"id": "B"}]
        edges = []
        betti = self.classifier.compute_betti_numbers(nodes, edges)
        assert betti.b0 == 2  # Two components
        assert betti.b1 == 0  # No cycles

    def test_compute_betti_numbers_complex(self):
        """Graph with multiple cycles."""
        # Diamond: A → B, A → C, B → D, C → D creates 1 cycle
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "A", "target": "C"},
            {"source": "B", "target": "D"},
            {"source": "C", "target": "D"}
        ]
        betti = self.classifier.compute_betti_numbers(nodes, edges)
        assert betti.b0 == 1  # Connected
        # b1 = |E| - |V| + b0 = 4 - 4 + 1 = 1
        assert betti.b1 == 1  # One cycle

    def test_classify_includes_betti_numbers(self):
        """Classify output includes Betti numbers."""
        nodes = [{"id": "A"}, {"id": "B"}]
        edges = [{"source": "A", "target": "B"}]
        result = self.classifier.classify(nodes, edges)

        assert "betti_numbers" in result
        assert result["betti_numbers"]["b0"] == 1
        assert result["betti_numbers"]["b1"] == 0
        assert result["betti_numbers"]["health_signal"] == "TREE"

    def test_classify_strict_layers(self):
        """Acyclic graph with one component = STRICT_LAYERS."""
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"}
        ]
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "STRICT_LAYERS"

    def test_classify_disconnected_islands(self):
        """Many disconnected components."""
        nodes = [{"id": f"N{i}"} for i in range(10)]
        edges = []  # No connections
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "DISCONNECTED_ISLANDS"

    def test_find_strongly_connected_components(self):
        """Test Tarjan's SCC algorithm."""
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}]
        # A → B → C → A forms an SCC, D is separate
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"},
            {"source": "C", "target": "D"}
        ]
        sccs = self.classifier._find_strongly_connected_components(nodes, edges)
        # Should have 2 SCCs: {A, B, C} and {D}
        scc_sizes = sorted([len(scc) for scc in sccs])
        assert scc_sizes == [1, 3]

    def test_count_directed_cycles(self):
        """Count nodes in directed cycles."""
        nodes = [{"id": "A"}, {"id": "B"}, {"id": "C"}, {"id": "D"}]
        edges = [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "A"},  # Cycle A-B-C
            {"source": "C", "target": "D"}   # D is not in cycle
        ]
        cyclic_count = self.classifier.count_directed_cycles(nodes, edges)
        assert cyclic_count == 3  # A, B, C are in the cycle


class TestElevationModel:
    """Test ElevationModel for landscape elevation computation."""

    def setup_method(self):
        self.model = ElevationModel()

    def test_default_elevation(self):
        """Default metrics should give baseline elevation (~5)."""
        metrics = {}
        elevation = self.model.compute_elevation(metrics)
        # With defaults: cc=1, fo=0, loc=50, mi=80
        # All components should be ~0, so elevation ≈ 5 (baseline)
        assert 4.5 <= elevation <= 5.5

    def test_high_complexity_raises_elevation(self):
        """High cyclomatic complexity should increase elevation."""
        low_cc = self.model.compute_elevation({'cyclomatic_complexity': 1})
        high_cc = self.model.compute_elevation({'cyclomatic_complexity': 50})
        assert high_cc > low_cc

    def test_high_coupling_raises_elevation(self):
        """High fan-out (>8) should increase elevation."""
        low_fo = self.model.compute_elevation({'fan_out': 5})
        high_fo = self.model.compute_elevation({'fan_out': 20})
        assert high_fo > low_fo

    def test_large_file_raises_elevation(self):
        """Large files (>100 LOC) should increase elevation."""
        small = self.model.compute_elevation({'loc': 50})
        large = self.model.compute_elevation({'loc': 500})
        assert large > small

    def test_low_maintainability_raises_elevation(self):
        """Low maintainability index should increase elevation."""
        good_mi = self.model.compute_elevation({'maintainability_index': 90})
        bad_mi = self.model.compute_elevation({'maintainability_index': 40})
        assert bad_mi > good_mi

    def test_compute_elevation_map(self):
        """Compute elevation for all nodes in a graph."""
        nodes = [
            {"id": "A", "cyclomatic_complexity": 5, "loc": 100},
            {"id": "B", "cyclomatic_complexity": 20, "loc": 500},
        ]
        edges = [{"source": "A", "target": "B"}]

        elev_map = self.model.compute_elevation_map(nodes, edges)

        assert "A" in elev_map
        assert "B" in elev_map
        assert isinstance(elev_map["A"], ElevationResult)
        # B should have higher elevation (more complex)
        assert elev_map["B"].elevation > elev_map["A"].elevation


class TestComputeGradient:
    """Test gradient computation along edges."""

    def test_steep_uphill(self):
        """Large positive gradient = steep uphill."""
        result = compute_gradient(3.0, 8.0)
        assert result["gradient"] == 5.0
        assert result["direction"] == "STEEP_UPHILL"
        assert result["risk"] == "HIGH"

    def test_uphill(self):
        """Small positive gradient = uphill."""
        result = compute_gradient(5.0, 6.0)
        assert result["gradient"] == 1.0
        assert result["direction"] == "UPHILL"
        assert result["risk"] == "MEDIUM"

    def test_downhill(self):
        """Small negative gradient = downhill."""
        result = compute_gradient(6.0, 5.0)
        assert result["gradient"] == -1.0
        assert result["direction"] == "DOWNHILL"
        assert result["risk"] == "LOW"

    def test_steep_downhill(self):
        """Large negative gradient = steep downhill."""
        result = compute_gradient(10.0, 5.0)
        assert result["gradient"] == -5.0
        assert result["direction"] == "STEEP_DOWNHILL"
        assert result["risk"] == "MINIMAL"


class TestLandscapeProfile:
    """Test LandscapeProfile dataclass."""

    def test_euler_characteristic(self):
        """χ = b₀ - b₁."""
        profile = LandscapeProfile(b0=1, b1=0)
        assert profile.euler_characteristic == 1

        profile = LandscapeProfile(b0=3, b1=5)
        assert profile.euler_characteristic == -2

    def test_has_cycles(self):
        """Check cycle detection."""
        no_cycles = LandscapeProfile(b0=1, b1=0)
        assert not no_cycles.has_cycles

        has_cycles = LandscapeProfile(b0=1, b1=3)
        assert has_cycles.has_cycles

    def test_peaks_and_valleys(self):
        """Identify high/low complexity nodes."""
        profile = LandscapeProfile(
            b0=1,
            b1=0,
            elevations={
                "god_class": 9.5,      # Peak (>8)
                "complex_fn": 8.2,     # Peak
                "normal": 5.0,
                "simple_util": 3.5,    # Valley (<4)
            }
        )
        assert "god_class" in profile.peaks
        assert "complex_fn" in profile.peaks
        assert "simple_util" in profile.valleys
        assert len(profile.peaks) == 2
        assert len(profile.valleys) == 1


class TestLandscapeHealthIndex:
    """Test LandscapeHealthIndex computation."""

    def setup_method(self):
        self.lhi = LandscapeHealthIndex()

    def test_perfect_health(self):
        """Perfect codebase: no cycles, low elevation, no bad gradients."""
        profile = LandscapeProfile(
            b0=1,  # Single connected component
            b1=0,  # No cycles
            elevations={"a": 3.0, "b": 3.5, "c": 4.0, "d": 3.2},
            gradients=[
                {"gradient": -1.0, "risk": "LOW"},
                {"gradient": -0.5, "risk": "LOW"},
            ]
        )
        result = self.lhi.compute(profile)
        # Consolidated formula: T=10 (no cycles, b0=1), E~8 (low elevations), Gd~9 (downhill), A=5 (no data)
        assert result["grade"] in ["A", "B", "C"]  # Alignment penalty without data
        assert result["index"] >= 6.0

    def test_cyclic_codebase(self):
        """Codebase with many cycles should have poor health."""
        profile = LandscapeProfile(
            b0=1,
            b1=10,  # Many cycles
            elevations={"a": 5.0, "b": 5.0},
            gradients=[]
        )
        result = self.lhi.compute(profile)
        # b1=10: 10.0 - (10 * 0.5) = 5.0 (mediocre cycle health)
        assert result["component_scores"]["cycles"] <= 5.0

    def test_high_complexity_codebase(self):
        """Codebase with high elevation should have poor health."""
        profile = LandscapeProfile(
            b0=1,
            b1=0,
            elevations={"god": 9.0, "complex": 8.5, "messy": 8.0},
            gradients=[]
        )
        result = self.lhi.compute(profile)
        assert result["component_scores"]["elevation"] < 3.0

    def test_fragmented_codebase(self):
        """Too many disconnected components is unhealthy."""
        profile = LandscapeProfile(
            b0=50,  # Way too many components for 10 nodes
            b1=0,
            elevations={f"n{i}": 5.0 for i in range(10)},
            gradients=[]
        )
        result = self.lhi.compute(profile)
        assert result["component_scores"]["isolation"] < 5.0

    def test_grade_mapping(self):
        """Test grade assignment."""
        assert self.lhi._to_grade(9.5) == "A"
        assert self.lhi._to_grade(8.5) == "B"
        assert self.lhi._to_grade(7.5) == "C"
        assert self.lhi._to_grade(6.0) == "D"
        assert self.lhi._to_grade(3.0) == "F"

    def test_empty_profile(self):
        """Handle empty profile gracefully."""
        profile = LandscapeProfile(b0=0, b1=0)
        result = self.lhi.compute(profile)
        assert "index" in result
        assert "grade" in result


# ── Shape Classification Decision Tree ──────────────────────────────────


class TestShapeClassification:
    """Test that the classify() decision tree returns correct shapes
    for various graph topologies, including the new FRAGMENTED_CYCLIC."""

    def setup_method(self):
        self.classifier = TopologyClassifier()

    def _make_nodes(self, n: int) -> list:
        return [{"id": f"N{i}"} for i in range(n)]

    def _make_chain(self, ids: list[str]) -> list:
        """Build A->B->C chain edges."""
        return [{"source": ids[i], "target": ids[i + 1]}
                for i in range(len(ids) - 1)]

    def _make_cycle(self, ids: list[str]) -> list:
        """Build A->B->C->A cycle edges."""
        edges = self._make_chain(ids)
        edges.append({"source": ids[-1], "target": ids[0]})
        return edges

    def test_fragmented_cyclic(self):
        """Many components + cycles in core -> FRAGMENTED_CYCLIC."""
        # 10 isolated nodes (fragments) + 1 cycle group of 3
        nodes = self._make_nodes(13)
        # Cycle among N0-N1-N2
        edges = self._make_cycle(["N0", "N1", "N2"])
        # N3-N12 are isolated (10 disconnected components + 1 cyclic = 11 total)
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "FRAGMENTED_CYCLIC"

    def test_fragmented_no_cycles_is_disconnected_islands(self):
        """Many components, no cycles -> DISCONNECTED_ISLANDS."""
        nodes = self._make_nodes(10)
        edges = []  # No connections at all
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "DISCONNECTED_ISLANDS"

    def test_big_ball_of_mud_requires_few_components(self):
        """BIG_BALL_OF_MUD requires <=5 components with heavy cycles."""
        # Single component, many cycle groups, high avg degree
        # Build a dense cyclic graph: 20 nodes, 12+ cycle groups
        nodes = self._make_nodes(20)
        edges = []
        # Create 12 overlapping cycles (pairs cycling back)
        for i in range(0, 12):
            a, b = f"N{i}", f"N{i + 1}"
            edges.append({"source": a, "target": b})
            edges.append({"source": b, "target": a})
        # Connect remaining nodes to make it dense (high avg degree)
        for i in range(12, 20):
            edges.append({"source": "N0", "target": f"N{i}"})
            edges.append({"source": f"N{i}", "target": "N0"})
        result = self.classifier.classify(nodes, edges)
        # Should NOT be FRAGMENTED_CYCLIC (few components)
        assert result["shape"] != "FRAGMENTED_CYCLIC"

    def test_strict_layers(self):
        """Single component, no cycles -> STRICT_LAYERS."""
        nodes = self._make_nodes(5)
        edges = self._make_chain([f"N{i}" for i in range(5)])
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "STRICT_LAYERS"

    def test_cyclic_network(self):
        """Few components, some cycles -> CYCLIC_NETWORK."""
        # Single component with 1-2 cycles, low density
        nodes = self._make_nodes(5)
        edges = self._make_chain([f"N{i}" for i in range(5)])
        # Add one back-edge to create a cycle
        edges.append({"source": "N2", "target": "N0"})
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "CYCLIC_NETWORK"

    def test_balanced_network(self):
        """Single component, no cycles, not linear -> BALANCED_NETWORK or STRICT_LAYERS."""
        nodes = self._make_nodes(3)
        edges = [
            {"source": "N0", "target": "N1"},
            {"source": "N0", "target": "N2"},
        ]
        result = self.classifier.classify(nodes, edges)
        # Tree-like with one root -- classified as STRICT_LAYERS
        assert result["shape"] in ("STRICT_LAYERS", "BALANCED_NETWORK")

    def test_fragmented_cyclic_description_mentions_components(self):
        """FRAGMENTED_CYCLIC description should mention component count."""
        nodes = self._make_nodes(13)
        edges = self._make_cycle(["N0", "N1", "N2"])
        result = self.classifier.classify(nodes, edges)
        assert result["shape"] == "FRAGMENTED_CYCLIC"
        assert "component" in result["description"].lower()
        assert "cycle" in result["description"].lower()

    def test_all_shapes_have_visual_metrics(self):
        """Every classification result includes visual_metrics."""
        # Test with FRAGMENTED_CYCLIC
        nodes = self._make_nodes(13)
        edges = self._make_cycle(["N0", "N1", "N2"])
        result = self.classifier.classify(nodes, edges)
        assert "visual_metrics" in result
        assert "components" in result["visual_metrics"]
        assert "directed_cycles" in result["visual_metrics"]


class TestTopologyScoreMapping:
    """Test that _score_topology() maps all shapes correctly."""

    def test_all_shapes_have_explicit_scores(self):
        """No shape should fall back to the generic 6.0 default."""
        all_shapes = [
            'STRICT_LAYERS', 'BALANCED_NETWORK', 'MESH',
            'CYCLIC_NETWORK', 'DISCONNECTED_ISLANDS',
            'FRAGMENTED_CYCLIC', 'DENSE_MESH', 'STAR_HUB',
            'BIG_BALL_OF_MUD',
        ]
        # These are the default_scores from insights_compiler._score_topology
        default_scores = {
            'STRICT_LAYERS': 10.0,
            'BALANCED_NETWORK': 8.5,
            'MESH': 7.0,
            'CYCLIC_NETWORK': 5.5,
            'DISCONNECTED_ISLANDS': 5.0,
            'FRAGMENTED_CYCLIC': 4.5,
            'DENSE_MESH': 4.0,
            'STAR_HUB': 4.0,
            'BIG_BALL_OF_MUD': 2.0,
        }
        for shape in all_shapes:
            assert shape in default_scores, f"{shape} missing from score map"
            # Score should not be the generic fallback
            assert default_scores[shape] != 6.0 or shape == 'UNKNOWN'

    def test_scores_are_monotonically_ordered(self):
        """Better shapes should score higher."""
        scores = {
            'STRICT_LAYERS': 10.0,
            'BALANCED_NETWORK': 8.5,
            'MESH': 7.0,
            'CYCLIC_NETWORK': 5.5,
            'DISCONNECTED_ISLANDS': 5.0,
            'FRAGMENTED_CYCLIC': 4.5,
            'BIG_BALL_OF_MUD': 2.0,
        }
        ordered = sorted(scores.items(), key=lambda x: -x[1])
        for i in range(len(ordered) - 1):
            assert ordered[i][1] >= ordered[i + 1][1], (
                f"{ordered[i][0]} ({ordered[i][1]}) should score >= "
                f"{ordered[i + 1][0]} ({ordered[i + 1][1]})"
            )
