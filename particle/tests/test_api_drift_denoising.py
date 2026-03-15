"""
Wave 2 / C5b: Tests for API drift de-noising.

Verifies:
- match_type tagging: exact / method_mismatch / fuzzy
- path_drift suppression below 0.70 threshold
- suppression count reporting
- exact/method_mismatch types not affected by threshold
- evidence fields correctly set
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import compile_insights


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


def _drift_data(items, drift_score=0.3, matched=5, total_be=10, total_fe=8):
    return {
        'drift_items': items,
        'drift_score': drift_score,
        'matched_endpoints': matched,
        'total_backend_routes': total_be,
        'total_frontend_calls': total_fe,
        'summary': {'total_drift_items': len(items)},
    }


class TestMatchTypeTagging:

    def test_orphaned_endpoint_tagged_exact(self):
        items = [{'drift_type': 'orphaned_endpoint', 'description': 'GET /api/foo',
                  'severity': 'medium', 'confidence': 1.0}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'orphaned_endpoint']
        assert len(drift_findings) == 1
        assert drift_findings[0]['evidence']['match_type'] == 'exact'

    def test_missing_endpoint_tagged_exact(self):
        items = [{'drift_type': 'missing_endpoint', 'description': 'POST /api/bar',
                  'severity': 'high', 'confidence': 1.0}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'missing_endpoint']
        assert drift_findings[0]['evidence']['match_type'] == 'exact'

    def test_method_mismatch_tagged(self):
        items = [{'drift_type': 'method_mismatch', 'description': 'GET vs POST /api/baz',
                  'severity': 'medium', 'confidence': 1.0}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'method_mismatch']
        assert drift_findings[0]['evidence']['match_type'] == 'method_mismatch'

    def test_path_drift_tagged_fuzzy(self):
        items = [{'drift_type': 'path_drift', 'description': '/api/user vs /api/users',
                  'severity': 'low', 'confidence': 0.85}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'path_drift']
        assert drift_findings[0]['evidence']['match_type'] == 'fuzzy'

    def test_fuzzy_has_similarity_score(self):
        items = [{'drift_type': 'path_drift', 'description': 'test',
                  'severity': 'low', 'confidence': 0.85}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'path_drift']
        assert drift_findings[0]['evidence']['similarity_score'] == 0.85

    def test_exact_has_no_similarity_score(self):
        items = [{'drift_type': 'orphaned_endpoint', 'description': 'test',
                  'severity': 'medium', 'confidence': 1.0}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [f for f in result['findings'] if f.get('evidence', {}).get('drift_type') == 'orphaned_endpoint']
        assert drift_findings[0]['evidence']['similarity_score'] is None


class TestPathDriftSuppression:

    def test_below_threshold_suppressed(self):
        """path_drift with confidence 0.50 (< 0.70) should be suppressed."""
        items = [{'drift_type': 'path_drift', 'description': 'low conf',
                  'severity': 'low', 'confidence': 0.50}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        path_findings = [f for f in result['findings']
                         if f.get('evidence', {}).get('drift_type') == 'path_drift']
        assert len(path_findings) == 0

    def test_above_threshold_not_suppressed(self):
        """path_drift with confidence 0.85 (>= 0.70) should NOT be suppressed."""
        items = [{'drift_type': 'path_drift', 'description': 'high conf',
                  'severity': 'low', 'confidence': 0.85}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        path_findings = [f for f in result['findings']
                         if f.get('evidence', {}).get('drift_type') == 'path_drift']
        assert len(path_findings) == 1

    def test_at_threshold_not_suppressed(self):
        """path_drift at exactly 0.70 should NOT be suppressed (>= check)."""
        items = [{'drift_type': 'path_drift', 'description': 'boundary',
                  'severity': 'low', 'confidence': 0.70}]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        path_findings = [f for f in result['findings']
                         if f.get('evidence', {}).get('drift_type') == 'path_drift']
        assert len(path_findings) == 1

    def test_suppression_count_reported(self):
        """Suppressed items should generate an info finding with the count."""
        items = [
            {'drift_type': 'path_drift', 'description': 'a', 'severity': 'low', 'confidence': 0.45},
            {'drift_type': 'path_drift', 'description': 'b', 'severity': 'low', 'confidence': 0.55},
            {'drift_type': 'path_drift', 'description': 'c', 'severity': 'low', 'confidence': 0.80},
        ]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        suppression_findings = [
            f for f in result['findings']
            if 'suppressed' in f.get('title', '').lower()
        ]
        assert len(suppression_findings) == 1
        assert suppression_findings[0]['evidence']['suppressed_count'] == 2

    def test_exact_types_not_affected_by_threshold(self):
        """Exact match types (orphaned, missing, shadow) should never be suppressed."""
        items = [
            {'drift_type': 'orphaned_endpoint', 'description': 'x', 'severity': 'medium', 'confidence': 0.30},
            {'drift_type': 'missing_endpoint', 'description': 'y', 'severity': 'high', 'confidence': 0.30},
        ]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        exact_findings = [
            f for f in result['findings']
            if f.get('evidence', {}).get('match_type') == 'exact'
        ]
        # Both should be present despite low confidence
        assert len(exact_findings) >= 2


class TestBeforeAfterEmission:

    def test_mixed_items_correct_surfaced_count(self):
        """3 items: 1 exact (always surfaced), 1 fuzzy above threshold, 1 fuzzy below.
        Should surface 2 drift findings + 1 suppression info."""
        items = [
            {'drift_type': 'orphaned_endpoint', 'description': 'exact', 'severity': 'medium', 'confidence': 1.0},
            {'drift_type': 'path_drift', 'description': 'good fuzzy', 'severity': 'low', 'confidence': 0.85},
            {'drift_type': 'path_drift', 'description': 'bad fuzzy', 'severity': 'low', 'confidence': 0.45},
        ]
        data = _base_output(api_drift=_drift_data(items))
        result = compile_insights(data)
        drift_findings = [
            f for f in result['findings']
            if f['category'] == 'api_drift' and 'suppressed' not in f.get('title', '').lower()
               and 'aligned' not in f.get('title', '').lower()
               and 'drift' not in f.get('title', '').lower() or f.get('evidence', {}).get('drift_type')
        ]
        # More precise: count findings with a drift_type in evidence
        typed_findings = [
            f for f in result['findings']
            if f.get('evidence', {}).get('drift_type') in ('orphaned_endpoint', 'path_drift')
        ]
        assert len(typed_findings) == 2  # exact + good fuzzy, bad fuzzy suppressed
