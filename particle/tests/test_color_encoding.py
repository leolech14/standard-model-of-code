"""
Tests for the color encoding layer.

Covers:
    - modulate_oklch preserves hue, gamut-maps result
    - ChannelMapping / ViewSpec dataclass construction
    - tag_convergence with both object and dict chemistry results
    - encode_nodes skips encoding for VIEW_DEFAULT (no L/C → appearance_engine handles)
    - encode_nodes with VIEW_ARCHITECTURE (L + C variation)
    - encode_edges maps confidence to hue gradient
    - Per-group normalization produces different colors for same metric in different groups
    - Normalization edge cases (single-node group, all-same-value)
    - Missing metric falls back to neutral defaults, no crash
    - encode_all orchestrator wires everything together
    - encode_all idempotency (safe to call twice)
    - EncodingReport tracks what was done
    - VIEW_DEFAULT preserves appearance_engine color_mode (file/ring/tier)
"""

import re

import pytest

from src.core.viz.color_science import (
    gamut_map_oklch,
    hex_to_oklch,
    in_srgb_gamut,
    modulate_oklch,
    oklch_to_hex,
)


def _ec_oklch(node_or_edge):
    """Extract OKLCH triple from encoded_color (now a tuple, not hex)."""
    ec = node_or_edge['encoded_color']
    assert isinstance(ec, (tuple, list)), f"encoded_color should be OKLCH tuple, got {type(ec)}: {ec}"
    assert len(ec) == 3, f"encoded_color should be [L, C, H], got {ec}"
    return ec
from src.core.viz.color_encoding import (
    NEUTRAL_C,
    NEUTRAL_L,
    ChannelMapping,
    EncodingReport,
    PRESET_VIEWS,
    VIEW_ARCHITECTURE,
    VIEW_DEFAULT,
    VIEW_FILES,
    VIEW_HEALTH,
    VIEW_TOPOLOGY,
    ViewSpec,
    encode_all,
    encode_edges,
    encode_nodes,
    tag_convergence,
)


HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')

# A view with explicit edge_mapping for testing edge encoding via encode_all
_VIEW_WITH_EDGES = ViewSpec(
    name='test_edges',
    hue_source='tier',
    lightness=ChannelMapping(
        metric='coherence_score',
        channel='lightness',
        output_range=(0.35, 0.85),
    ),
    edge_mapping=ChannelMapping(
        metric='confidence',
        channel='hue',
        output_range=(30.0, 145.0),
    ),
)


# =============================================================================
# modulate_oklch (color_science primitive)
# =============================================================================

class TestModulateOklch:
    """Test the modulate_oklch primitive added to color_science."""

    def test_preserves_hue(self):
        """Changing L and C should not change H."""
        L, C, H = 0.7, 0.15, 180.0
        rL, rC, rH = modulate_oklch(L, C, H, l_target=0.4, c_target=0.05)
        assert rH == pytest.approx(H, abs=0.1)

    def test_replaces_lightness(self):
        """l_target should replace L."""
        L, C, H = 0.7, 0.10, 90.0
        rL, rC, rH = modulate_oklch(L, C, H, l_target=0.3)
        assert rL == pytest.approx(0.3, abs=0.05)

    def test_replaces_chroma(self):
        """c_target should replace C."""
        L, C, H = 0.7, 0.10, 90.0
        rL, rC, rH = modulate_oklch(L, C, H, c_target=0.20)
        # May be gamut-reduced but should be close
        assert rC <= 0.20 + 0.01

    def test_none_keeps_original(self):
        """None targets should keep original values (post gamut-map)."""
        L, C, H = 0.6, 0.08, 120.0
        rL, rC, rH = modulate_oklch(L, C, H)
        # Should be essentially same as gamut_map_oklch(L, C, H)
        gL, gC, gH = gamut_map_oklch(L, C, H)
        assert rL == pytest.approx(gL, abs=0.001)
        assert rC == pytest.approx(gC, abs=0.001)

    def test_result_in_gamut(self):
        """Result must be in sRGB gamut even for extreme inputs."""
        rL, rC, rH = modulate_oklch(0.9, 0.4, 30.0, l_target=0.95, c_target=0.35)
        assert in_srgb_gamut(rL, rC, rH)

    def test_returns_tuple_of_three(self):
        """Should return a 3-tuple of floats."""
        result = modulate_oklch(0.5, 0.1, 200.0)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)


# =============================================================================
# Dataclass construction
# =============================================================================

class TestDataclasses:
    """Test ChannelMapping, ViewSpec, EncodingReport construction."""

    def test_channel_mapping_defaults(self):
        cm = ChannelMapping(metric='x', channel='lightness', output_range=(0.3, 0.8))
        assert cm.normalize == 'global'
        assert cm.group_by is None
        assert cm.invert is False

    def test_channel_mapping_frozen(self):
        cm = ChannelMapping(metric='x', channel='lightness', output_range=(0.3, 0.8))
        with pytest.raises(AttributeError):
            cm.metric = 'y'

    def test_view_spec_defaults(self):
        vs = ViewSpec(name='test', hue_source='tier')
        assert vs.lightness is None
        assert vs.chroma is None
        assert vs.edge_mapping is None

    def test_view_spec_frozen(self):
        with pytest.raises(AttributeError):
            VIEW_DEFAULT.name = 'mutated'

    def test_preset_views_exist(self):
        assert len(PRESET_VIEWS) == 5
        for name in ('default', 'architecture', 'health', 'topology', 'files'):
            assert name in PRESET_VIEWS

    def test_encoding_report_defaults(self):
        r = EncodingReport(view_name='test')
        assert r.nodes_encoded == 0
        assert r.edges_encoded == 0
        assert r.convergent_tagged == 0
        assert r.channels_used == []
        assert r.missing_data == {}


# =============================================================================
# tag_convergence
# =============================================================================

class TestTagConvergence:
    """Test convergence tagging from chemistry results."""

    def _make_nodes(self, ids):
        return [{'id': nid, 'name': nid.split('::')[-1]} for nid in ids]

    def test_tags_matching_nodes_from_object(self):
        """Tag nodes using a mock ChemistryResult-like object."""
        class MockNodeConv:
            def __init__(self, nid, sev, sigs):
                self.node_id = nid
                self.severity = sev
                self.signals = sigs
                self.signal_count = len(sigs)

        class MockConvergence:
            convergent_nodes = [
                MockNodeConv('a::Foo', 'critical', ['low_confidence', 'no_docstring', 'god_class', 'high_complexity', 'low_coherence']),
                MockNodeConv('b::Bar', 'moderate', ['low_confidence', 'no_docstring', 'implicit_intent']),
            ]

        class MockChemResult:
            convergence = MockConvergence()

        nodes = self._make_nodes(['a::Foo', 'b::Bar', 'c::Baz'])
        tagged = tag_convergence(nodes, MockChemResult())

        assert tagged == 2
        assert nodes[0]['convergence_severity'] == 'critical'
        assert nodes[0]['convergence_count'] == 5
        assert 'god_class' in nodes[0]['convergence_signals']
        assert nodes[1]['convergence_severity'] == 'moderate'
        assert 'convergence_severity' not in nodes[2]

    def test_tags_matching_nodes_from_dict(self):
        """Tag nodes using a dict chemistry result (from JSON)."""
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'node_id': 'x::Alpha', 'severity': 'high',
                     'signals': ['low_confidence', 'no_docstring', 'implicit_intent', 'unknown_layer'],
                     'signal_count': 4},
                ]
            }
        }
        nodes = self._make_nodes(['x::Alpha', 'y::Beta'])
        tagged = tag_convergence(nodes, chemistry)

        assert tagged == 1
        assert nodes[0]['convergence_severity'] == 'high'
        assert nodes[0]['convergence_count'] == 4

    def test_no_convergence_data(self):
        """No convergence -> 0 tagged, no crash."""
        nodes = self._make_nodes(['a::X'])

        assert tag_convergence(nodes, None) == 0
        assert tag_convergence(nodes, {}) == 0
        assert tag_convergence(nodes, {'convergence': None}) == 0

    def test_no_matching_nodes(self):
        """Convergent nodes that don't match any node -> 0 tagged."""
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'node_id': 'missing::NotHere', 'severity': 'critical',
                     'signals': ['a', 'b', 'c', 'd', 'e'], 'signal_count': 5},
                ]
            }
        }
        nodes = self._make_nodes(['a::Foo'])
        assert tag_convergence(nodes, chemistry) == 0

    def test_empty_node_id_not_matched(self):
        """Convergent node with empty node_id should not match nodes with empty id."""
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'node_id': '', 'severity': 'critical',
                     'signals': ['a', 'b', 'c', 'd', 'e'], 'signal_count': 5},
                ]
            }
        }
        nodes = [{'id': '', 'name': 'empty'}]
        assert tag_convergence(nodes, chemistry) == 0

    def test_missing_node_id_in_dict_skipped(self):
        """Dict convergent node without node_id key is skipped entirely."""
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'severity': 'critical', 'signals': ['a'], 'signal_count': 1},
                ]
            }
        }
        nodes = [{'id': '', 'name': 'x'}]
        assert tag_convergence(nodes, chemistry) == 0


# =============================================================================
# Tier hue ordering
# =============================================================================

class TestTierHueOrdering:
    """Test that EXT.DISCOVERED is distinguished from EXT regardless of iteration order."""

    def test_ext_discovered_gets_different_hue_from_ext(self):
        """EXT.DISCOVERED atoms must not be confused with plain EXT atoms."""
        nodes = [
            {'id': 'a', 'atom': 'EXT.DISCOVERED.001', 'coherence_score': 0.5, 'D6_pure_score': 0.3},
            {'id': 'b', 'atom': 'EXT.005', 'coherence_score': 0.5, 'D6_pure_score': 0.3},
        ]
        # Use ARCHITECTURE view (has L/C mappings) so encoded_color is written
        encode_nodes(nodes, VIEW_ARCHITECTURE)

        hue_discovered = _ec_oklch(nodes[0])[2]
        hue_ext = _ec_oklch(nodes[1])[2]

        # They should be meaningfully different (EXT.DISCOVERED=60deg, EXT=145deg)
        diff = abs(hue_discovered - hue_ext)
        if diff > 180:
            diff = 360 - diff
        assert diff > 30, f"EXT.DISCOVERED and EXT hues too close: {diff:.1f}deg"


# =============================================================================
# encode_nodes
# =============================================================================

class TestEncodeNodes:
    """Test node encoding with various ViewSpecs."""

    def _make_tier_nodes(self, n=5):
        """Create test nodes with tier atoms and some metrics."""
        atoms = ['CORE.001', 'CORE.002', 'ARCH.010', 'EXT.005', 'EXT.DISCOVERED.001']
        nodes = []
        for i in range(n):
            nodes.append({
                'id': f'node_{i}',
                'atom': atoms[i % len(atoms)],
                'coherence_score': 0.2 * (i + 1),  # 0.2, 0.4, 0.6, 0.8, 1.0
                'D6_pure_score': 0.1 * (i + 1),    # 0.1, 0.2, 0.3, 0.4, 0.5
                'cyclomatic_complexity': i * 5,      # 0, 5, 10, 15, 20
            })
        return nodes

    def test_view_default_skips_encoding(self):
        """VIEW_DEFAULT has no L/C mappings, so encoded_color is NOT written."""
        nodes = self._make_tier_nodes()
        encoded, missing = encode_nodes(nodes, VIEW_DEFAULT)

        assert encoded == 0
        assert missing == {}
        for node in nodes:
            assert 'encoded_color' not in node

    def test_view_architecture_produces_oklch_tuples(self):
        """VIEW_ARCHITECTURE should assign encoded_color OKLCH tuples to every node."""
        nodes = self._make_tier_nodes()
        encoded, missing = encode_nodes(nodes, VIEW_ARCHITECTURE)

        assert encoded == 5
        for node in nodes:
            L, C, H = _ec_oklch(node)
            assert 0 <= L <= 1
            assert 0 <= C <= 0.4
            assert 0 <= H < 360

    def test_view_architecture_produces_lc_variation(self):
        """VIEW_ARCHITECTURE should produce varying L and C across nodes."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_ARCHITECTURE)

        lightnesses = [_ec_oklch(n)[0] for n in nodes]
        chromas = [_ec_oklch(n)[1] for n in nodes]

        # With varying coherence_score and D6_pure_score, L and C should vary
        assert max(lightnesses) - min(lightnesses) > 0.05
        assert max(chromas) - min(chromas) > 0.01

    def test_view_architecture_different_hues_for_different_tiers(self):
        """Different tiers should get different hues in ARCHITECTURE view."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_ARCHITECTURE)

        core_hue = _ec_oklch(nodes[0])[2]  # CORE
        arch_hue = _ec_oklch(nodes[2])[2]  # ARCH
        ext_hue = _ec_oklch(nodes[3])[2]   # EXT

        # Hues should be meaningfully different (at least 30 degrees apart)
        assert abs(core_hue - arch_hue) > 30 or abs(core_hue - arch_hue) > 330
        assert abs(arch_hue - ext_hue) > 30 or abs(arch_hue - ext_hue) > 330

    def test_view_health_inverts_complexity(self):
        """VIEW_HEALTH inverts complexity: highest complexity -> lowest lightness."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_HEALTH)

        # node_0 has complexity=0 (lowest), node_4 has complexity=20 (highest)
        L_low_complex = _ec_oklch(nodes[0])[0]
        L_high_complex = _ec_oklch(nodes[4])[0]

        # Inverted: low complexity -> high lightness, high complexity -> low lightness
        assert L_low_complex > L_high_complex

    def test_data_views_produce_valid_oklch(self):
        """Every data-driven view (non-default) should produce valid OKLCH tuples."""
        nodes = self._make_tier_nodes(20)
        data_views = {k: v for k, v in PRESET_VIEWS.items() if k != 'default'}
        for name, view in data_views.items():
            encode_nodes(nodes, view)
            for node in nodes:
                L, C, H = _ec_oklch(node)
                assert 0 <= L <= 1, f"L out of range in {name}: {L}"
                assert 0 <= C <= 0.4, f"C out of range in {name}: {C}"
                assert 0 <= H < 360, f"H out of range in {name}: {H}"

    def test_missing_metric_uses_neutral(self):
        """Nodes lacking the mapped metric should get neutral L/C."""
        nodes = [
            {'id': 'a', 'atom': 'CORE.001'},  # no coherence_score or D6_pure_score
            {'id': 'b', 'atom': 'CORE.002', 'coherence_score': 0.9, 'D6_pure_score': 0.5},
        ]
        encoded, missing = encode_nodes(nodes, VIEW_ARCHITECTURE)

        assert encoded == 2
        assert missing['coherence_score'] == 1  # node 'a' missing
        assert missing['D6_pure_score'] == 1

        # Node 'a' should have neutral-ish L/C
        La, Ca, Ha = _ec_oklch(nodes[0])
        assert La == pytest.approx(NEUTRAL_L, abs=0.05)
        assert Ca == pytest.approx(NEUTRAL_C, abs=0.03)

    def test_empty_nodes_no_crash(self):
        """Empty node list should not crash."""
        encoded, missing = encode_nodes([], VIEW_ARCHITECTURE)
        assert encoded == 0

    def test_file_hue_golden_angle(self):
        """VIEW_FILES uses golden-angle hue distribution by fileIdx."""
        nodes = [
            {'id': f'n{i}', 'atom': 'CORE.001', 'fileIdx': i,
             'coherence_score': 0.5, 'D6_pure_score': 0.3}
            for i in range(5)
        ]
        encode_nodes(nodes, VIEW_FILES)

        hues = [_ec_oklch(n)[2] for n in nodes]
        # Adjacent files should have different hues (golden angle ~ 137.5deg)
        for i in range(len(hues) - 1):
            diff = abs(hues[i + 1] - hues[i])
            if diff > 180:
                diff = 360 - diff
            # Should be roughly 137.5deg apart (allowing for gamut mapping variation)
            assert diff > 50, f"Files {i} and {i+1} too close: {diff:.1f}deg"


# =============================================================================
# Per-group normalization
# =============================================================================

class TestPerGroupNormalization:
    """Test per-group normalization edge cases and correctness."""

    def test_same_metric_different_groups(self):
        """Same absolute metric in two groups with different ranges -> different L values."""
        view = ViewSpec(
            name='test_pergroup',
            hue_source='tier',
            lightness=ChannelMapping(
                metric='complexity',
                channel='lightness',
                output_range=(0.35, 0.85),
                normalize='per_group',
                group_by='file_path',
            ),
        )

        nodes = [
            # Group A: complexity range [1, 10]
            {'id': 'a1', 'atom': 'CORE.001', 'file_path': 'fileA', 'complexity': 5},
            {'id': 'a2', 'atom': 'CORE.001', 'file_path': 'fileA', 'complexity': 1},
            {'id': 'a3', 'atom': 'CORE.001', 'file_path': 'fileA', 'complexity': 10},
            # Group B: complexity range [50, 100]
            {'id': 'b1', 'atom': 'CORE.001', 'file_path': 'fileB', 'complexity': 75},
            {'id': 'b2', 'atom': 'CORE.001', 'file_path': 'fileB', 'complexity': 50},
            {'id': 'b3', 'atom': 'CORE.001', 'file_path': 'fileB', 'complexity': 100},
        ]

        encode_nodes(nodes, view)

        # a1 (5 in range [1,10]) and b1 (75 in range [50,100]) have different absolute
        # values but similar relative positions (~midpoint). Their L should be similar.
        La1 = _ec_oklch(nodes[0])[0]
        Lb1 = _ec_oklch(nodes[3])[0]
        assert abs(La1 - Lb1) < 0.15  # relatively close

        # a2 (min of group A) and b3 (max of group B) should have very different L
        La2 = _ec_oklch(nodes[1])[0]
        Lb3 = _ec_oklch(nodes[5])[0]
        assert abs(La2 - Lb3) > 0.2

    def test_single_node_group_gets_midpoint(self):
        """A group with one node should get the midpoint of the output range."""
        view = ViewSpec(
            name='test_single',
            hue_source='tier',
            lightness=ChannelMapping(
                metric='score',
                channel='lightness',
                output_range=(0.35, 0.85),
                normalize='per_group',
                group_by='file_path',
            ),
        )
        nodes = [
            {'id': 'a', 'atom': 'CORE.001', 'file_path': 'lonely_file', 'score': 42.0},
        ]
        encode_nodes(nodes, view)

        L = _ec_oklch(nodes[0])[0]
        midpoint = (0.35 + 0.85) / 2.0  # 0.60
        assert L == pytest.approx(midpoint, abs=0.05)

    def test_all_same_value_group_gets_midpoint(self):
        """A group where all nodes have identical values should get the midpoint."""
        view = ViewSpec(
            name='test_uniform',
            hue_source='tier',
            lightness=ChannelMapping(
                metric='score',
                channel='lightness',
                output_range=(0.35, 0.85),
                normalize='global',  # global is fine too
            ),
        )
        nodes = [
            {'id': f'n{i}', 'atom': 'CORE.001', 'score': 7.0}
            for i in range(5)
        ]
        encode_nodes(nodes, view)

        midpoint = (0.35 + 0.85) / 2.0
        for node in nodes:
            L = _ec_oklch(node)[0]
            assert L == pytest.approx(midpoint, abs=0.05)


# =============================================================================
# encode_edges
# =============================================================================

class TestEncodeEdges:
    """Test edge encoding."""

    def test_encodes_confidence_gradient(self):
        """Edges with varying confidence should get different colors."""
        edges = [
            {'source': 'a', 'target': 'b', 'confidence': 0.6},
            {'source': 'a', 'target': 'c', 'confidence': 0.8},
            {'source': 'a', 'target': 'd', 'confidence': 1.0},
        ]
        encoded, missing = encode_edges(edges)

        assert encoded == 3
        assert missing == 0
        for edge in edges:
            L, C, H = _ec_oklch(edge)
            assert 0 <= L <= 1
            assert 0 <= H < 360

        # Different confidence -> different OKLCH values
        hues = [_ec_oklch(e)[2] for e in edges]
        assert max(hues) - min(hues) > 1  # at least some hue variation

    def test_missing_confidence_reports_count(self):
        """Edges without the metric are not encoded; missing count is tracked."""
        edges = [
            {'source': 'a', 'target': 'b'},  # no confidence
            {'source': 'a', 'target': 'c', 'confidence': 0.9},
        ]
        encoded, missing = encode_edges(edges)
        assert encoded <= 1
        assert missing >= 1

    def test_all_edges_missing_metric(self):
        """When no edges have the metric, returns (0, total_edges)."""
        edges = [
            {'source': 'a', 'target': 'b'},
            {'source': 'a', 'target': 'c'},
        ]
        encoded, missing = encode_edges(edges)
        assert encoded == 0
        assert missing == 2

    def test_uniform_confidence_still_encodes(self):
        """All same confidence -> all get same color, no crash."""
        edges = [
            {'source': 'a', 'target': 'b', 'confidence': 1.0},
            {'source': 'a', 'target': 'c', 'confidence': 1.0},
        ]
        encoded, missing = encode_edges(edges)
        assert encoded == 2
        assert missing == 0

    def test_empty_edges_no_crash(self):
        """Empty edge list should not crash."""
        encoded, missing = encode_edges([])
        assert encoded == 0
        assert missing == 0

    def test_custom_mapping(self):
        """Custom ChannelMapping for edges should work."""
        mapping = ChannelMapping(
            metric='weight',
            channel='lightness',
            output_range=(0.3, 0.8),
        )
        edges = [
            {'source': 'a', 'target': 'b', 'weight': 1.0},
            {'source': 'a', 'target': 'c', 'weight': 5.0},
        ]
        encoded, missing = encode_edges(edges, mapping)
        assert encoded == 2
        assert missing == 0

    def test_default_hue_range_is_warm_to_cool(self):
        """Default edge encoding should map low confidence to warm, high to cool."""
        edges = [
            {'source': 'a', 'target': 'b', 'confidence': 0.0},
            {'source': 'a', 'target': 'c', 'confidence': 1.0},
        ]
        encode_edges(edges)

        hue_low = _ec_oklch(edges[0])[2]
        hue_high = _ec_oklch(edges[1])[2]

        # Low confidence ~ 30deg (warm orange-red), high ~ 145deg (green)
        assert hue_low < 90, f"Low confidence hue too high: {hue_low:.1f}"
        assert hue_high > 90, f"High confidence hue too low: {hue_high:.1f}"


# =============================================================================
# encode_all orchestrator
# =============================================================================

class TestEncodeAll:
    """Test the encode_all orchestrator."""

    def _make_full_output(self):
        nodes = [
            {'id': f'node_{i}', 'atom': 'CORE.001',
             'coherence_score': 0.5, 'cyclomatic_complexity': i * 3}
            for i in range(10)
        ]
        edges = [
            {'source': f'node_{i}', 'target': f'node_{i+1}', 'confidence': 0.6 + i * 0.04}
            for i in range(9)
        ]
        return {'nodes': nodes, 'edges': edges}

    def test_default_view_skips_node_encoding(self):
        """encode_all with VIEW_DEFAULT should NOT encode nodes (preserves color_mode)."""
        full = self._make_full_output()
        report = encode_all(full, VIEW_DEFAULT)

        assert report.view_name == 'default'
        assert report.nodes_encoded == 0
        assert report.edges_encoded == 0  # no edge_mapping on VIEW_DEFAULT
        assert report.channels_used == []
        # No encoded_color on any node
        for node in full['nodes']:
            assert 'encoded_color' not in node

    def test_default_view_still_tags_convergence(self):
        """VIEW_DEFAULT should still tag convergence even though it skips encoding."""
        full = self._make_full_output()
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'node_id': 'node_0', 'severity': 'critical',
                     'signals': ['a', 'b', 'c', 'd', 'e'], 'signal_count': 5},
                ]
            }
        }
        report = encode_all(full, VIEW_DEFAULT, chemistry=chemistry)

        assert report.convergent_tagged == 1
        assert full['nodes'][0]['convergence_severity'] == 'critical'
        assert report.nodes_encoded == 0  # encoding skipped

    def test_architecture_view_encodes_nodes(self):
        """VIEW_ARCHITECTURE should encode all nodes with 3 channels."""
        full = self._make_full_output()
        for node in full['nodes']:
            node['D6_pure_score'] = 0.3

        report = encode_all(full, VIEW_ARCHITECTURE)

        assert report.nodes_encoded == 10
        assert 'hue' in report.channels_used
        assert 'lightness' in report.channels_used
        assert 'chroma' in report.channels_used
        for node in full['nodes']:
            assert 'encoded_color' in node

    def test_with_chemistry_tags_convergence(self):
        """encode_all with chemistry should tag convergent nodes."""
        full = self._make_full_output()
        chemistry = {
            'convergence': {
                'convergent_nodes': [
                    {'node_id': 'node_0', 'severity': 'critical',
                     'signals': ['a', 'b', 'c', 'd', 'e'], 'signal_count': 5},
                    {'node_id': 'node_1', 'severity': 'moderate',
                     'signals': ['x', 'y', 'z'], 'signal_count': 3},
                ]
            }
        }
        report = encode_all(full, VIEW_ARCHITECTURE, chemistry=chemistry)

        assert report.convergent_tagged == 2
        assert full['nodes'][0]['convergence_severity'] == 'critical'
        assert full['nodes'][1]['convergence_severity'] == 'moderate'

    def test_without_chemistry_no_crash(self):
        """encode_all without chemistry should still work."""
        full = self._make_full_output()
        report = encode_all(full)

        assert report.convergent_tagged == 0
        assert report.nodes_encoded == 0  # VIEW_DEFAULT

    def test_report_tracks_missing_data(self):
        """Nodes missing mapped metrics should be counted in missing_data."""
        nodes = [
            {'id': 'a', 'atom': 'CORE.001'},  # missing both metrics
            {'id': 'b', 'atom': 'CORE.002', 'coherence_score': 0.5},  # missing D6_pure_score
        ]
        full = {'nodes': nodes, 'edges': []}
        report = encode_all(full, VIEW_ARCHITECTURE)

        assert report.missing_data.get('coherence_score', 0) >= 1
        assert report.missing_data.get('D6_pure_score', 0) >= 1

    def test_empty_output_no_crash(self):
        """Empty full_output should not crash."""
        report = encode_all({})
        assert report.nodes_encoded == 0
        assert report.edges_encoded == 0

    def test_none_view_defaults(self):
        """None view should default to VIEW_DEFAULT."""
        full = self._make_full_output()
        report = encode_all(full, view=None)
        assert report.view_name == 'default'

    def test_edge_encoding_with_explicit_mapping(self):
        """View with edge_mapping should encode edges; missing data surfaced."""
        nodes = [{'id': 'n0', 'atom': 'CORE.001', 'coherence_score': 0.5}]
        edges = [
            {'source': 'n0', 'target': 'n0', 'confidence': 0.8},
            {'source': 'n0', 'target': 'n0'},  # missing confidence
        ]
        full = {'nodes': nodes, 'edges': edges}
        report = encode_all(full, _VIEW_WITH_EDGES)

        assert report.edges_encoded >= 1
        assert report.missing_data.get('edge:confidence', 0) >= 1

    def test_view_default_does_not_encode_edges(self):
        """VIEW_DEFAULT has no edge_mapping, so edges are not encoded."""
        full = self._make_full_output()
        report = encode_all(full, VIEW_DEFAULT)

        assert report.edges_encoded == 0
        for edge in full['edges']:
            assert 'encoded_color' not in edge

    def test_report_dict_conversion(self):
        """EncodingReport.__dict__ should produce a JSON-serializable dict."""
        full = self._make_full_output()
        report = encode_all(full, VIEW_DEFAULT)
        d = report.__dict__
        assert isinstance(d, dict)
        assert 'view_name' in d
        assert 'nodes_encoded' in d
        import json
        json.dumps(d)  # should not raise

    def test_idempotent_double_call(self):
        """Calling encode_all twice on the same data should produce identical results."""
        full = self._make_full_output()
        for node in full['nodes']:
            node['D6_pure_score'] = 0.3

        report1 = encode_all(full, VIEW_ARCHITECTURE)
        colors_after_first = [n.get('encoded_color') for n in full['nodes']]

        report2 = encode_all(full, VIEW_ARCHITECTURE)
        colors_after_second = [n.get('encoded_color') for n in full['nodes']]

        assert colors_after_first == colors_after_second
        assert report1.nodes_encoded == report2.nodes_encoded

    def test_color_mode_file_preserved_with_default_view(self):
        """VIEW_DEFAULT must not write encoded_color, so color_mode=file still works."""
        nodes = [
            {'id': f'n{i}', 'atom': 'CORE.001', 'fileIdx': i}
            for i in range(5)
        ]
        full = {'nodes': nodes, 'edges': []}
        encode_all(full, VIEW_DEFAULT)

        # No encoded_color should exist
        for node in nodes:
            assert 'encoded_color' not in node, \
                "VIEW_DEFAULT wrote encoded_color, which would shadow color_mode=file"
