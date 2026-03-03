"""
Tests for the color encoding layer.

Covers:
    - modulate_oklch preserves hue, gamut-maps result
    - ChannelMapping / ViewSpec dataclass construction
    - tag_convergence with both object and dict chemistry results
    - encode_nodes with VIEW_DEFAULT (backward-compatible, hue-only)
    - encode_nodes with VIEW_ARCHITECTURE (L + C variation)
    - encode_edges maps confidence to hue gradient
    - Per-group normalization produces different colors for same metric in different groups
    - Missing metric falls back to neutral defaults, no crash
    - encode_all orchestrator wires everything together
    - EncodingReport tracks what was done
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
        """No convergence → 0 tagged, no crash."""
        nodes = self._make_nodes(['a::X'])

        assert tag_convergence(nodes, None) == 0
        assert tag_convergence(nodes, {}) == 0
        assert tag_convergence(nodes, {'convergence': None}) == 0

    def test_no_matching_nodes(self):
        """Convergent nodes that don't match any node → 0 tagged."""
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

    def test_view_default_produces_hex_colors(self):
        """VIEW_DEFAULT should assign encoded_color to every node."""
        nodes = self._make_tier_nodes()
        encoded, missing = encode_nodes(nodes, VIEW_DEFAULT)

        assert encoded == 5
        for node in nodes:
            assert 'encoded_color' in node
            assert HEX_RE.match(node['encoded_color'])

    def test_view_default_no_lc_variation(self):
        """VIEW_DEFAULT has no L/C mapping → all nodes get neutral L/C."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_DEFAULT)

        # All nodes should use NEUTRAL_L and NEUTRAL_C (modulo gamut mapping)
        for node in nodes:
            L, C, H = hex_to_oklch(node['encoded_color'])
            assert L == pytest.approx(NEUTRAL_L, abs=0.05)
            assert C == pytest.approx(NEUTRAL_C, abs=0.03)

    def test_view_default_different_hues_for_different_tiers(self):
        """Different tiers should get different hues."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_DEFAULT)

        core_hue = hex_to_oklch(nodes[0]['encoded_color'])[2]  # CORE
        arch_hue = hex_to_oklch(nodes[2]['encoded_color'])[2]  # ARCH
        ext_hue = hex_to_oklch(nodes[3]['encoded_color'])[2]   # EXT

        # Hues should be meaningfully different (at least 30 degrees apart)
        assert abs(core_hue - arch_hue) > 30 or abs(core_hue - arch_hue) > 330
        assert abs(arch_hue - ext_hue) > 30 or abs(arch_hue - ext_hue) > 330

    def test_view_architecture_produces_lc_variation(self):
        """VIEW_ARCHITECTURE should produce varying L and C across nodes."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_ARCHITECTURE)

        lightnesses = [hex_to_oklch(n['encoded_color'])[0] for n in nodes]
        chromas = [hex_to_oklch(n['encoded_color'])[1] for n in nodes]

        # With varying coherence_score and D6_pure_score, L and C should vary
        assert max(lightnesses) - min(lightnesses) > 0.05
        assert max(chromas) - min(chromas) > 0.01

    def test_view_health_inverts_complexity(self):
        """VIEW_HEALTH inverts complexity: highest complexity → lowest lightness."""
        nodes = self._make_tier_nodes()
        encode_nodes(nodes, VIEW_HEALTH)

        # node_0 has complexity=0 (lowest), node_4 has complexity=20 (highest)
        L_low_complex = hex_to_oklch(nodes[0]['encoded_color'])[0]
        L_high_complex = hex_to_oklch(nodes[4]['encoded_color'])[0]

        # Inverted: low complexity → high lightness, high complexity → low lightness
        assert L_low_complex > L_high_complex

    def test_all_encoded_colors_are_valid_hex(self):
        """Every encoded_color should be a valid 6-digit hex."""
        nodes = self._make_tier_nodes(20)
        for view in PRESET_VIEWS.values():
            encode_nodes(nodes, view)
            for node in nodes:
                assert HEX_RE.match(node['encoded_color']), \
                    f"Invalid hex in {view.name}: {node['encoded_color']}"

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
        La, Ca, Ha = hex_to_oklch(nodes[0]['encoded_color'])
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

        hues = [hex_to_oklch(n['encoded_color'])[2] for n in nodes]
        # Adjacent files should have different hues (golden angle ≈ 137.5°)
        for i in range(len(hues) - 1):
            diff = abs(hues[i + 1] - hues[i])
            if diff > 180:
                diff = 360 - diff
            # Should be roughly 137.5° apart (allowing for gamut mapping variation)
            assert diff > 50, f"Files {i} and {i+1} too close: {diff:.1f}°"


# =============================================================================
# Per-group normalization
# =============================================================================

class TestPerGroupNormalization:
    """Test that per-group normalization produces different colors for same value in different groups."""

    def test_same_metric_different_groups(self):
        """Same absolute metric in two groups with different ranges → different L values."""
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
        La1 = hex_to_oklch(nodes[0]['encoded_color'])[0]
        Lb1 = hex_to_oklch(nodes[3]['encoded_color'])[0]
        assert abs(La1 - Lb1) < 0.15  # relatively close

        # a2 (min of group A) and b3 (max of group B) should have very different L
        La2 = hex_to_oklch(nodes[1]['encoded_color'])[0]
        Lb3 = hex_to_oklch(nodes[5]['encoded_color'])[0]
        assert abs(La2 - Lb3) > 0.2


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
        encoded = encode_edges(edges)

        assert encoded == 3
        for edge in edges:
            assert 'encoded_color' in edge
            assert HEX_RE.match(edge['encoded_color'])

        # Different confidence → different colors
        colors = [edge['encoded_color'] for edge in edges]
        assert len(set(colors)) >= 2  # at least 2 distinct colors

    def test_missing_confidence_skipped(self):
        """Edges without the metric are not encoded."""
        edges = [
            {'source': 'a', 'target': 'b'},  # no confidence
            {'source': 'a', 'target': 'c', 'confidence': 0.9},
        ]
        encoded = encode_edges(edges)
        # Only the one with confidence gets encoded
        assert encoded <= 1

    def test_uniform_confidence_still_encodes(self):
        """All same confidence → all get same color, no crash."""
        edges = [
            {'source': 'a', 'target': 'b', 'confidence': 1.0},
            {'source': 'a', 'target': 'c', 'confidence': 1.0},
        ]
        encoded = encode_edges(edges)
        assert encoded == 2

    def test_empty_edges_no_crash(self):
        """Empty edge list should not crash."""
        assert encode_edges([]) == 0

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
        encoded = encode_edges(edges, mapping)
        assert encoded == 2


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

    def test_default_view_encodes_nodes(self):
        """encode_all with VIEW_DEFAULT should encode all nodes."""
        full = self._make_full_output()
        report = encode_all(full, VIEW_DEFAULT)

        assert report.view_name == 'default'
        assert report.nodes_encoded == 10
        assert 'hue' in report.channels_used

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
        report = encode_all(full, VIEW_DEFAULT, chemistry=chemistry)

        assert report.convergent_tagged == 2
        assert full['nodes'][0]['convergence_severity'] == 'critical'
        assert full['nodes'][1]['convergence_severity'] == 'moderate'

    def test_without_chemistry_no_crash(self):
        """encode_all without chemistry should still work."""
        full = self._make_full_output()
        report = encode_all(full)

        assert report.convergent_tagged == 0
        assert report.nodes_encoded == 10

    def test_architecture_view_uses_three_channels(self):
        """VIEW_ARCHITECTURE should use hue + lightness + chroma."""
        full = self._make_full_output()
        # Add D6_pure_score to nodes
        for i, node in enumerate(full['nodes']):
            node['D6_pure_score'] = 0.1 * (i + 1)

        report = encode_all(full, VIEW_ARCHITECTURE)

        assert 'hue' in report.channels_used
        assert 'lightness' in report.channels_used
        assert 'chroma' in report.channels_used

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

    def test_report_dict_conversion(self):
        """EncodingReport.__dict__ should produce a JSON-serializable dict."""
        full = self._make_full_output()
        report = encode_all(full, VIEW_DEFAULT)
        d = report.__dict__
        assert isinstance(d, dict)
        assert 'view_name' in d
        assert 'nodes_encoded' in d
        # Verify JSON serializable
        import json
        json.dumps(d)  # should not raise
