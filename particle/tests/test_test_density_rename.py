"""
Wave 4 / H2: Tests for test_coverage → test_density dual-emit deprecation.

Verifies:
- Both keys emitted in health_components
- Values are identical
- Only test_density participates in health_score (no double-counting)
- Backward compat: _compute_health_score honors old test_coverage key
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, compile_insights


def _base_output(**overrides):
    out = {
        'kpis': {
            'nodes_total': 100, 'edges_total': 200,
            'dead_code_percent': 2.0,
            'orphan_count': 0, 'orphan_percent': 0.0,
            'knot_score': 0.5, 'cycles_detected': 0,
            'rho_antimatter': 0.0, 'rho_policy': 0.0,
            'antimatter_count': 0, 'policy_violation_count': 0,
            'signal_count': 0,
            'codebase_intelligence': 0.85,
            'codebase_interpretation': 'Good',
            'q_distribution': {},
            'topology_shape': 'STRICT_LAYERS',
        },
        'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
        'topology': {'shape': 'STRICT_LAYERS', 'description': '', 'visual_metrics': {}},
        'distributions': {'types': {'Service': 10, 'Test': 12}},
        'performance': {'hotspot_count': 0, 'time_by_type': {}},
        'nodes': [], 'edges': [],
    }
    for k, v in overrides.items():
        if k == 'kpis' and isinstance(v, dict):
            out['kpis'].update(v)
        else:
            out[k] = v
    return out


def _compiler(**kw):
    return InsightsCompiler(_base_output(**kw))


class TestDualEmit:

    def test_both_keys_present(self):
        result = compile_insights(_base_output())
        hc = result['health_components']
        assert 'test_density' in hc
        assert 'test_coverage' in hc

    def test_values_identical(self):
        result = compile_insights(_base_output())
        hc = result['health_components']
        assert hc['test_density'] == hc['test_coverage']

    def test_test_density_is_canonical(self):
        """test_density is the canonical key; test_coverage is the alias."""
        result = compile_insights(_base_output())
        hc = result['health_components']
        # Both present but test_density is the one that matters for scoring
        assert 'test_density' in hc


class TestNoDoubleCounting:

    def test_health_score_unchanged(self):
        """Having both keys should NOT double-count in the health score.
        The deprecated test_coverage key is NOT in the weights dict."""
        c = _compiler()
        components = c._compute_health_components()
        score = c._compute_health_score(components)
        # If double-counting occurred, score would be inflated.
        # The score should equal: sum of 7 canonical weights * component values.
        # With both test_density and test_coverage at the same value,
        # only test_density is weighted.
        expected_weights = {
            'topology': 0.20, 'constraints': 0.20, 'purpose': 0.15,
            'test_density': 0.15, 'dead_code': 0.10, 'entanglement': 0.10,
            'rpbl_balance': 0.10,
        }
        manual = sum(components.get(k, 5.0) * w for k, w in expected_weights.items())
        assert abs(score - round(min(10.0, max(0.0, manual)), 2)) < 0.01


class TestBackwardCompat:

    def test_old_format_components_still_work(self):
        """If someone passes only test_coverage (old format), _compute_health_score
        should still work correctly via the fallback."""
        c = _compiler()
        old_components = {
            'topology': 10.0, 'constraints': 10.0, 'purpose': 10.0,
            'test_coverage': 10.0, 'dead_code': 10.0, 'entanglement': 10.0,
            'rpbl_balance': 10.0,
        }
        score = c._compute_health_score(old_components)
        assert score == 10.0

    def test_new_format_preferred_over_old(self):
        """If both test_density and test_coverage are present,
        test_density value is used (it's the weight key)."""
        c = _compiler()
        components = {
            'topology': 5.0, 'constraints': 5.0, 'purpose': 5.0,
            'test_density': 10.0,
            'test_coverage': 0.0,  # deprecated, should be ignored
            'dead_code': 5.0, 'entanglement': 5.0, 'rpbl_balance': 5.0,
        }
        score = c._compute_health_score(components)
        # test_density=10 * 0.15 = 1.5, rest = 5*0.85 = 4.25 → 5.75
        assert abs(score - 5.75) < 0.01


class TestYAMLOverrideNormalization:
    """Old YAML overrides using test_coverage should be normalized to test_density."""

    def test_old_yaml_weight_key_normalized(self):
        """YAML with weights: {test_coverage: 0.20} should be treated as test_density: 0.20."""
        from unittest.mock import patch
        c = _compiler()
        old_yaml = {'health_scoring': {'weights': {'test_coverage': 0.20}}}
        with patch.object(c, '_thresholds', old_yaml):
            components = c._compute_health_components()
            score = c._compute_health_score(components)
        # If normalization works, test_density uses 0.20 weight, not the default 0.15.
        # Re-compute with explicit 0.20 weight to verify.
        expected_weights = {
            'topology': 0.20, 'constraints': 0.20, 'purpose': 0.15,
            'test_density': 0.20, 'dead_code': 0.10, 'entanglement': 0.10,
            'rpbl_balance': 0.10,
        }
        manual = sum(components.get(k, 5.0) * w for k, w in expected_weights.items())
        assert abs(score - round(min(10.0, max(0.0, manual)), 2)) < 0.01

    def test_new_yaml_key_takes_precedence(self):
        """If YAML has both test_coverage and test_density, test_density wins."""
        from unittest.mock import patch
        c = _compiler()
        yaml_with_both = {'health_scoring': {'weights': {
            'test_coverage': 0.05,
            'test_density': 0.20,
        }}}
        with patch.object(c, '_thresholds', yaml_with_both):
            components = c._compute_health_components()
            score = c._compute_health_score(components)
        expected_weights = {
            'topology': 0.20, 'constraints': 0.20, 'purpose': 0.15,
            'test_density': 0.20, 'dead_code': 0.10, 'entanglement': 0.10,
            'rpbl_balance': 0.10,
        }
        manual = sum(components.get(k, 5.0) * w for k, w in expected_weights.items())
        assert abs(score - round(min(10.0, max(0.0, manual)), 2)) < 0.01
