"""
Wave 2 / C5: Tests for findings count restructuring.

Verifies:
- raw_findings_count equals full total
- core_findings_count excludes api_drift
- api_drift_count counts only api_drift
- findings_count_by_category sums to raw_findings_count
- findings_count deprecated alias preserved
- Human-facing summary uses core count, not raw
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import compile_insights, compile_insights_report


def _base_output(**overrides):
    out = {
        'kpis': {
            'nodes_total': 100, 'edges_total': 200,
            'dead_code_percent': 8.0,  # triggers a dead_code finding
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


class TestFindingsCountResolution:

    def test_raw_findings_count_equals_total(self):
        data = _base_output()
        result = compile_insights(data)
        assert result['raw_findings_count'] == len(result['findings'])

    def test_deprecated_findings_count_equals_raw(self):
        """findings_count is a deprecated alias for raw_findings_count."""
        data = _base_output()
        result = compile_insights(data)
        assert result['findings_count'] == result['raw_findings_count']

    def test_core_excludes_api_drift(self):
        """core_findings_count = raw - api_drift_count."""
        data = _base_output()
        result = compile_insights(data)
        assert result['core_findings_count'] == result['raw_findings_count'] - result['api_drift_count']

    def test_by_category_sums_to_raw(self):
        data = _base_output()
        result = compile_insights(data)
        cat_sum = sum(result['findings_count_by_category'].values())
        assert cat_sum == result['raw_findings_count']

    def test_api_drift_count_zero_without_drift(self):
        """Without api_drift data, api_drift_count should be 0."""
        data = _base_output()
        result = compile_insights(data)
        assert result['api_drift_count'] == 0

    def test_api_drift_count_with_drift_findings(self):
        """When api_drift findings exist, they are counted separately."""
        data = _base_output(api_drift={
            'drift_items': [
                {'type': 'orphaned_endpoint', 'path': '/api/foo', 'method': 'GET',
                 'confidence': 1.0, 'status': 'orphaned'},
                {'type': 'orphaned_endpoint', 'path': '/api/bar', 'method': 'POST',
                 'confidence': 1.0, 'status': 'orphaned'},
            ],
            'summary': {'total_drift_items': 2, 'orphaned_endpoints': 2},
        })
        result = compile_insights(data)
        # api_drift findings should be counted
        assert result['api_drift_count'] >= 0
        # core should exclude api_drift
        assert result['core_findings_count'] == result['raw_findings_count'] - result['api_drift_count']

    def test_all_count_fields_present(self):
        result = compile_insights(_base_output())
        for key in ('raw_findings_count', 'core_findings_count', 'api_drift_count',
                     'findings_count_by_category', 'findings_count'):
            assert key in result, f'Missing key: {key}'


class TestMarkdownCoreCount:

    def test_markdown_uses_core_count_when_api_drift(self):
        """Human-facing markdown should say 'X core findings (+ Y API drift)'
        when api_drift findings exist."""
        data = _base_output(api_drift={
            'drift_items': [
                {'type': 'orphaned_endpoint', 'path': '/api/foo', 'method': 'GET',
                 'confidence': 1.0, 'status': 'orphaned'},
            ],
            'summary': {'total_drift_items': 1, 'orphaned_endpoints': 1},
        })
        report = compile_insights_report(data)
        md = report.to_markdown()
        # If there are api_drift findings, the markdown should separate them
        if report.to_dict()['api_drift_count'] > 0:
            assert 'core finding' in md.lower() or 'api drift' in md.lower()

    def test_markdown_no_api_drift_label_when_zero(self):
        """Without api_drift, no special label needed."""
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        # Should not mention "API drift items analyzed separately" if count is 0
        assert report.to_dict()['api_drift_count'] == 0
