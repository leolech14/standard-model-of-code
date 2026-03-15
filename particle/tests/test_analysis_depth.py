"""
Phase 1 C1+C2: Tests for parser_coverage and analysis_depth fingerprint.

C1: parser_coverage — files_discovered, files_attempted,
    files_successfully_parsed, files_failed, files_skipped,
    coverage_ratio, coverage_by_language.
C2: analysis_depth — node_count, edge_count, nodes_per_discovered_file,
    nodes_per_attempted_file, nodes_per_parsed_file, edges_per_node,
    stages_completed, stages_total, nested parser_coverage.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import compile_insights


def _base_output(**overrides):
    out = {
        'kpis': {
            'nodes_total': 50, 'edges_total': 80,
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
        'counts': {'files': 10, 'nodes': 50, 'edges': 80},
        'nodes': [], 'edges': [],
    }
    for k, v in overrides.items():
        if k == 'kpis' and isinstance(v, dict):
            out['kpis'].update(v)
        else:
            out[k] = v
    return out


def _pc(**overrides):
    """Default parser_coverage dict."""
    pc = {
        'files_discovered': 100,
        'files_attempted': 80,
        'files_successfully_parsed': 75,
        'files_failed': 5,
        'files_skipped': 20,
        'coverage_ratio': 0.75,
        'coverage_by_language': {
            'python': {'attempted': 60, 'parsed': 58, 'failed': 2, 'coverage': 0.9667},
            'javascript': {'attempted': 20, 'parsed': 17, 'failed': 3, 'coverage': 0.85},
        },
    }
    pc.update(overrides)
    return pc


# =========================================================================
# C2: analysis_depth fingerprint
# =========================================================================

class TestAnalysisDepthPresent:

    def test_analysis_depth_in_meta(self):
        result = compile_insights(_base_output())
        assert 'analysis_depth' in result['meta']

    def test_analysis_depth_keys(self):
        result = compile_insights(_base_output(parser_coverage=_pc()))
        ad = result['meta']['analysis_depth']
        for key in ('node_count', 'edge_count', 'nodes_per_discovered_file',
                     'nodes_per_attempted_file', 'nodes_per_parsed_file',
                     'edges_per_node', 'stages_completed', 'stages_total'):
            assert key in ad, f'Missing key: {key}'

    def test_node_count_matches_kpis(self):
        result = compile_insights(_base_output())
        assert result['meta']['analysis_depth']['node_count'] == 50

    def test_edge_count_matches_kpis(self):
        result = compile_insights(_base_output())
        assert result['meta']['analysis_depth']['edge_count'] == 80


class TestAnalysisDepthDenominators:

    def test_nodes_per_discovered_file(self):
        """50 nodes / 100 discovered files = 0.5"""
        data = _base_output(parser_coverage=_pc(files_discovered=100))
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['nodes_per_discovered_file'] == 0.5

    def test_nodes_per_attempted_file(self):
        """50 nodes / 80 attempted files = 0.625"""
        data = _base_output(parser_coverage=_pc(files_attempted=80))
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['nodes_per_attempted_file'] == 0.62  # rounded to 2dp

    def test_nodes_per_parsed_file(self):
        """50 nodes / 75 parsed files = 0.67"""
        data = _base_output(parser_coverage=_pc(files_successfully_parsed=75))
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['nodes_per_parsed_file'] == 0.67

    def test_all_denominators_zero_safe(self):
        """All three per-file ratios should be 0.0 when denominators are 0."""
        pc = _pc(files_discovered=0, files_attempted=0, files_successfully_parsed=0)
        data = _base_output(parser_coverage=pc)
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['nodes_per_discovered_file'] == 0.0
        assert ad['nodes_per_attempted_file'] == 0.0
        assert ad['nodes_per_parsed_file'] == 0.0

    def test_denominators_without_parser_coverage(self):
        """Without parser_coverage, per-file ratios are null (not 0.0)
        and availability map marks them as 'unavailable'."""
        data = _base_output()
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['nodes_per_discovered_file'] is None
        assert ad['nodes_per_attempted_file'] is None
        assert ad['nodes_per_parsed_file'] is None
        assert ad['availability']['nodes_per_discovered_file'] == 'unavailable'
        assert ad['availability']['nodes_per_attempted_file'] == 'unavailable'
        assert ad['availability']['nodes_per_parsed_file'] == 'unavailable'

    def test_availability_absent_when_coverage_present(self):
        """When parser_coverage IS present, no availability map is needed."""
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert 'availability' not in ad

    def test_edges_per_node_zero_safe(self):
        data = _base_output(kpis={'nodes_total': 0, 'edges_total': 0})
        result = compile_insights(data)
        assert result['meta']['analysis_depth']['edges_per_node'] == 0.0

    def test_edges_per_node_computed(self):
        """80 edges / 50 nodes = 1.6"""
        result = compile_insights(_base_output())
        assert result['meta']['analysis_depth']['edges_per_node'] == 1.6


class TestAnalysisDepthStages:

    def test_stages_from_pipeline_performance(self):
        data = _base_output(pipeline_performance={
            'summary': {'total_stages': 12, 'ok_count': 10, 'fail_count': 1, 'warn_count': 1},
            'stages': [],
        })
        result = compile_insights(data)
        ad = result['meta']['analysis_depth']
        assert ad['stages_completed'] == 10
        assert ad['stages_total'] == 12

    def test_stages_default_when_no_perf(self):
        result = compile_insights(_base_output())
        ad = result['meta']['analysis_depth']
        assert ad['stages_completed'] == 0
        assert ad['stages_total'] == 0


# =========================================================================
# C1: parser_coverage pass-through
# =========================================================================

class TestParserCoveragePassThrough:

    def test_present_when_provided(self):
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        assert 'parser_coverage' in result['meta']['analysis_depth']

    def test_absent_for_legacy(self):
        data = _base_output()
        assert 'parser_coverage' not in data
        result = compile_insights(data)
        assert 'parser_coverage' not in result['meta']['analysis_depth']

    def test_coverage_ratio_preserved(self):
        data = _base_output(parser_coverage=_pc(coverage_ratio=0.85))
        result = compile_insights(data)
        assert result['meta']['analysis_depth']['parser_coverage']['coverage_ratio'] == 0.85

    def test_coverage_by_language_preserved(self):
        lang = {'Go': {'attempted': 30, 'parsed': 28, 'failed': 2, 'coverage': 0.9333}}
        data = _base_output(parser_coverage=_pc(coverage_by_language=lang))
        result = compile_insights(data)
        out_lang = result['meta']['analysis_depth']['parser_coverage']['coverage_by_language']
        assert 'Go' in out_lang
        assert out_lang['Go']['attempted'] == 30
        assert out_lang['Go']['parsed'] == 28
        assert out_lang['Go']['failed'] == 2

    def test_per_language_has_required_fields(self):
        """Each language entry must have attempted, parsed, failed, coverage."""
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        langs = result['meta']['analysis_depth']['parser_coverage']['coverage_by_language']
        for lang_name, entry in langs.items():
            for field in ('attempted', 'parsed', 'failed', 'coverage'):
                assert field in entry, f'{lang_name} missing field: {field}'


class TestParserCoverageInvariants:

    def test_files_discovered_ge_attempted(self):
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        ppc = result['meta']['analysis_depth']['parser_coverage']
        assert ppc['files_discovered'] >= ppc['files_attempted']

    def test_attempted_equals_success_plus_failed(self):
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        ppc = result['meta']['analysis_depth']['parser_coverage']
        assert ppc['files_attempted'] == ppc['files_successfully_parsed'] + ppc['files_failed']

    def test_skipped_equals_discovered_minus_attempted(self):
        data = _base_output(parser_coverage=_pc())
        result = compile_insights(data)
        ppc = result['meta']['analysis_depth']['parser_coverage']
        assert ppc['files_skipped'] == ppc['files_discovered'] - ppc['files_attempted']

    def test_coverage_ratio_bounded_0_1(self):
        data = _base_output(parser_coverage=_pc(
            files_discovered=100, files_successfully_parsed=100, coverage_ratio=1.0
        ))
        result = compile_insights(data)
        ratio = result['meta']['analysis_depth']['parser_coverage']['coverage_ratio']
        assert 0.0 <= ratio <= 1.0


class TestBackwardCompatibility:

    def test_nodes_analyzed_still_in_meta(self):
        result = compile_insights(_base_output())
        assert result['meta']['nodes_analyzed'] == 50
        assert result['meta']['edges_analyzed'] == 80

    def test_compiler_version_still_in_meta(self):
        result = compile_insights(_base_output())
        assert 'compiler_version' in result['meta']
