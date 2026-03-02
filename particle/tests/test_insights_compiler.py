"""
Tests for InsightsCompiler - unified interpretation of Collider output.
"""
import pytest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import (
    InsightsCompiler, compile_insights, compile_insights_report,
    CompiledInsight, InsightsReport,
)


# =============================================================================
# FIXTURES: Synthetic full_output dicts
# =============================================================================

def _base_output(**overrides):
    """Minimal full_output dict with sensible defaults."""
    out = {
        'kpis': {
            'nodes_total': 100,
            'edges_total': 200,
            'dead_code_percent': 3.0,
            'orphan_count': 5,
            'orphan_percent': 5.0,
            'knot_score': 1.0,
            'cycles_detected': 0,
            'rho_antimatter': 0.0,
            'rho_policy': 0.0,
            'antimatter_count': 0,
            'policy_violation_count': 0,
            'signal_count': 0,
            'codebase_intelligence': 0.75,
            'codebase_interpretation': 'Good',
            'q_distribution': {},
            'topology_shape': 'STRICT_LAYERS',
        },
        'rpbl_profile': {
            'responsibility': 4.0,
            'purity': 7.0,
            'boundary': 3.0,
            'lifecycle': 3.0,
        },
        'topology': {
            'shape': 'STRICT_LAYERS',
            'description': 'Clean layered architecture.',
            'visual_metrics': {},
        },
        'constraint_field': {
            'antimatter': {'count': 0, 'rho_antimatter': 0},
            'policy_violations': {'count': 0, 'rho_policy': 0},
            'signals': {'count': 5},
            'valid': True,
        },
        'performance': {
            'hotspot_count': 2,
            'critical_path_length': 5,
            'critical_path_cost': 10.0,
            'time_by_type': {'compute': 5, 'io': 3, 'setup': 2},
        },
        'distributions': {
            'types': {'Service': 10, 'Command': 5, 'Query': 8, 'Test': 12},
        },
        'execution_flow': {
            'entry_points': ['main', 'cli'],
            'orphans': [],
        },
        'top_hubs': [
            {'name': 'CoreService', 'in_degree': 15},
            {'name': 'Utils', 'in_degree': 10},
        ],
        'orphans_list': [],
        'nodes': [],
        'edges': [],
    }
    # Apply overrides (supports nested dict merge for kpis)
    for k, v in overrides.items():
        if k == 'kpis' and isinstance(v, dict):
            out['kpis'].update(v)
        else:
            out[k] = v
    return out


# =============================================================================
# BASIC COMPILATION
# =============================================================================

class TestInsightsCompiler:

    def test_compile_returns_dict(self):
        data = _base_output()
        result = compile_insights(data)
        assert isinstance(result, dict)
        assert result['grade'] in ('A', 'B', 'C', 'D', 'F')
        assert 0 <= result['health_score'] <= 10

    def test_compile_report_returns_object(self):
        data = _base_output()
        report = compile_insights_report(data)
        assert isinstance(report, InsightsReport)
        assert report.grade in ('A', 'B', 'C', 'D', 'F')

    def test_healthy_codebase_gets_good_grade(self):
        data = _base_output()
        result = compile_insights(data)
        assert result['grade'] in ('A', 'B'), f"Expected A or B, got {result['grade']}"
        assert result['health_score'] >= 7.0

    def test_to_dict_has_required_keys(self):
        data = _base_output()
        d = compile_insights(data)
        assert 'grade' in d
        assert 'health_score' in d
        assert 'health_components' in d
        assert 'mission_matrix' in d
        assert 'findings' in d
        assert 'findings_count' in d
        assert 'findings_by_severity' in d
        assert 'executive_summary' in d
        assert 'navigation' in d
        assert 'theory_glossary' in d

    def test_to_markdown_is_string(self):
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        assert isinstance(md, str)
        assert '# Collider Insights Report' in md
        assert report.grade in md


# =============================================================================
# DEAD CODE INTERPRETATION
# =============================================================================

class TestDeadCodeInterpretation:

    def test_no_finding_when_low(self):
        data = _base_output(kpis={'dead_code_percent': 2.0})
        result = compile_insights(data)
        dead_findings = [f for f in result['findings'] if f['category'] == 'dead_code' and 'Dead code' in f['title']]
        assert len(dead_findings) == 0

    def test_medium_when_moderate(self):
        data = _base_output(kpis={'dead_code_percent': 8.0})
        result = compile_insights(data)
        dead_findings = [f for f in result['findings'] if 'Dead code' in f['title']]
        assert len(dead_findings) == 1
        assert dead_findings[0]['severity'] == 'medium'

    def test_high_when_elevated(self):
        data = _base_output(kpis={'dead_code_percent': 15.0})
        result = compile_insights(data)
        dead_findings = [f for f in result['findings'] if 'Dead code' in f['title']]
        assert len(dead_findings) == 1
        assert dead_findings[0]['severity'] == 'high'

    def test_critical_when_extreme(self):
        data = _base_output(kpis={'dead_code_percent': 25.0})
        result = compile_insights(data)
        dead_findings = [f for f in result['findings'] if 'Dead code' in f['title']]
        assert len(dead_findings) == 1
        assert dead_findings[0]['severity'] == 'critical'


# =============================================================================
# ORPHAN INTERPRETATION
# =============================================================================

class TestOrphanInterpretation:

    def test_no_finding_when_low(self):
        data = _base_output(kpis={'orphan_percent': 5.0, 'orphan_count': 5})
        result = compile_insights(data)
        orphan_findings = [f for f in result['findings'] if 'Orphan' in f['title']]
        assert len(orphan_findings) == 0

    def test_high_when_elevated(self):
        data = _base_output(kpis={'orphan_percent': 12.0, 'orphan_count': 12})
        result = compile_insights(data)
        orphan_findings = [f for f in result['findings'] if 'Orphan' in f['title']]
        assert len(orphan_findings) == 1
        assert orphan_findings[0]['severity'] == 'high'

    def test_critical_when_extreme(self):
        data = _base_output(kpis={'orphan_percent': 20.0, 'orphan_count': 20})
        result = compile_insights(data)
        orphan_findings = [f for f in result['findings'] if 'Orphan' in f['title']]
        assert len(orphan_findings) == 1
        assert orphan_findings[0]['severity'] == 'critical'


# =============================================================================
# ENTANGLEMENT INTERPRETATION
# =============================================================================

class TestEntanglementInterpretation:

    def test_no_finding_when_low(self):
        data = _base_output(kpis={'knot_score': 1.0, 'cycles_detected': 0})
        result = compile_insights(data)
        knot_findings = [f for f in result['findings'] if 'entanglement' in f['title'].lower()]
        assert len(knot_findings) == 0

    def test_medium_when_moderate(self):
        data = _base_output(kpis={'knot_score': 3.0, 'cycles_detected': 2})
        result = compile_insights(data)
        knot_findings = [f for f in result['findings'] if 'entanglement' in f['title'].lower()]
        assert len(knot_findings) == 1
        assert knot_findings[0]['severity'] == 'medium'

    def test_critical_when_extreme(self):
        data = _base_output(kpis={'knot_score': 9.0, 'cycles_detected': 15})
        result = compile_insights(data)
        knot_findings = [f for f in result['findings'] if 'entanglement' in f['title'].lower()]
        assert len(knot_findings) == 1
        assert knot_findings[0]['severity'] == 'critical'


# =============================================================================
# ANTIMATTER INTERPRETATION
# =============================================================================

class TestAntimatterInterpretation:

    def test_no_finding_when_clean(self):
        data = _base_output(kpis={'rho_antimatter': 0.0, 'antimatter_count': 0})
        result = compile_insights(data)
        am_findings = [f for f in result['findings'] if 'Antimatter' in f['title']]
        assert len(am_findings) == 0

    def test_high_when_elevated(self):
        data = _base_output(kpis={'rho_antimatter': 0.03, 'antimatter_count': 3})
        result = compile_insights(data)
        am_findings = [f for f in result['findings'] if 'Antimatter' in f['title']]
        assert len(am_findings) == 1
        assert am_findings[0]['severity'] == 'high'

    def test_critical_when_extreme(self):
        data = _base_output(kpis={'rho_antimatter': 0.08, 'antimatter_count': 8})
        result = compile_insights(data)
        am_findings = [f for f in result['findings'] if 'Antimatter' in f['title']]
        assert len(am_findings) == 1
        assert am_findings[0]['severity'] == 'critical'


# =============================================================================
# PURPOSE INTERPRETATION
# =============================================================================

class TestPurposeInterpretation:

    def test_excellent_gets_info(self):
        data = _base_output(kpis={'codebase_intelligence': 0.90, 'codebase_interpretation': 'Excellent'})
        result = compile_insights(data)
        purpose_findings = [f for f in result['findings'] if f['category'] == 'purpose']
        assert len(purpose_findings) == 1
        assert purpose_findings[0]['severity'] == 'info'

    def test_critical_when_opaque(self):
        data = _base_output(kpis={'codebase_intelligence': 0.30, 'codebase_interpretation': 'Opaque'})
        result = compile_insights(data)
        purpose_findings = [f for f in result['findings'] if f['category'] == 'purpose' and f['severity'] != 'info']
        assert len(purpose_findings) == 1
        assert purpose_findings[0]['severity'] == 'critical'

    def test_misalignment_overrides_high_qscore(self):
        data = _base_output(
            kpis={'codebase_intelligence': 0.95, 'codebase_interpretation': 'Sharp'},
            purpose_field={
                'total_nodes': 100,
                'uncertain_count': 45,
                'god_class_count': 35,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.55,
            },
        )
        result = compile_insights(data)
        purpose_findings = [f for f in result['findings'] if f['category'] == 'purpose']
        assert len(purpose_findings) == 1
        assert purpose_findings[0]['title'] == 'Purpose-field misalignment'
        assert purpose_findings[0]['severity'] in ('high', 'critical')


class TestExecutionCapabilityInterpretation:

    def test_vectorization_failure_emits_finding(self):
        data = _base_output(
            kpis={
                'vectorization_status': 'failed',
                'vectorization_error': "No module named 'lancedb'",
            },
        )
        result = compile_insights(data)
        findings = [f for f in result['findings'] if f['category'] == 'execution']
        assert len(findings) == 1
        assert findings[0]['title'] == 'Vectorization unavailable'

    def test_ecosystem_skip_emits_finding(self):
        data = _base_output(
            kpis={
                'ecosystem_discovery_status': 'skipped',
                'ecosystem_discovery_error': "No module named 'discovery_engine'",
            },
        )
        result = compile_insights(data)
        findings = [f for f in result['findings'] if f['category'] == 'execution']
        assert len(findings) == 1
        assert findings[0]['title'] == 'Ecosystem discovery skipped'


# =============================================================================
# RPBL INTERPRETATION
# =============================================================================

class TestRPBLInterpretation:

    def test_no_finding_when_balanced(self):
        data = _base_output(rpbl_profile={'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3})
        result = compile_insights(data)
        rpbl_findings = [f for f in result['findings'] if f['category'] == 'rpbl']
        assert len(rpbl_findings) == 0

    def test_finding_when_imbalanced(self):
        data = _base_output(rpbl_profile={'responsibility': 8, 'purity': 2, 'boundary': 7, 'lifecycle': 7})
        result = compile_insights(data)
        rpbl_findings = [f for f in result['findings'] if f['category'] == 'rpbl']
        assert len(rpbl_findings) == 1
        assert rpbl_findings[0]['severity'] in ('high', 'medium')


# =============================================================================
# TOPOLOGY INTERPRETATION
# =============================================================================

class TestTopologyInterpretation:

    def test_strict_layers_is_info(self):
        data = _base_output(
            kpis={'topology_shape': 'STRICT_LAYERS'},
            topology={'shape': 'STRICT_LAYERS', 'description': 'Clean layers.', 'visual_metrics': {}},
        )
        result = compile_insights(data)
        topo_findings = [f for f in result['findings'] if f['category'] == 'topology']
        assert len(topo_findings) == 1
        assert topo_findings[0]['severity'] == 'info'

    def test_big_ball_of_mud_is_critical(self):
        data = _base_output(
            kpis={'topology_shape': 'BIG_BALL_OF_MUD'},
            topology={'shape': 'BIG_BALL_OF_MUD', 'description': 'No structure.', 'visual_metrics': {}},
        )
        result = compile_insights(data)
        topo_findings = [f for f in result['findings'] if f['category'] == 'topology']
        assert len(topo_findings) == 1
        assert topo_findings[0]['severity'] == 'critical'


# =============================================================================
# HEALTH SCORE & GRADE
# =============================================================================

class TestHealthScore:

    def test_perfect_score(self):
        """All-green metrics should produce A grade."""
        data = _base_output(
            kpis={
                'dead_code_percent': 1.0,
                'orphan_percent': 2.0,
                'knot_score': 0.5,
                'rho_antimatter': 0.0,
                'rho_policy': 0.0,
                'codebase_intelligence': 0.90,
                'topology_shape': 'STRICT_LAYERS',
            },
            rpbl_profile={'responsibility': 3, 'purity': 8, 'boundary': 2, 'lifecycle': 2},
        )
        result = compile_insights(data)
        assert result['grade'] == 'A'
        assert result['health_score'] >= 8.5

    def test_terrible_score(self):
        """All-red metrics should produce F grade."""
        data = _base_output(
            kpis={
                'dead_code_percent': 40.0,
                'orphan_percent': 30.0,
                'knot_score': 10.0,
                'rho_antimatter': 0.15,
                'rho_policy': 0.10,
                'codebase_intelligence': 0.20,
                'topology_shape': 'BIG_BALL_OF_MUD',
            },
            rpbl_profile={'responsibility': 9, 'purity': 1, 'boundary': 9, 'lifecycle': 9},
        )
        result = compile_insights(data)
        assert result['grade'] == 'F'
        assert result['health_score'] < 4.0

    def test_health_components_present(self):
        """Health components should have the expected keys."""
        data = _base_output()
        result = compile_insights(data)
        expected_keys = {'topology', 'constraints', 'purpose', 'test_coverage', 'dead_code', 'entanglement', 'rpbl_balance'}
        assert set(result['health_components'].keys()) == expected_keys


# =============================================================================
# MISSION MATRIX (95% TARGETS)
# =============================================================================

class TestMissionMatrix:

    def test_matrix_has_expected_dimensions(self):
        data = _base_output()
        result = compile_insights(data)
        matrix = result['mission_matrix']
        assert set(matrix.keys()) >= {'target', 'execution', 'performance', 'logic', 'purpose_fulfillment', 'overall', 'all_targets_met'}

    def test_matrix_scores_are_bounded(self):
        data = _base_output()
        result = compile_insights(data)
        matrix = result['mission_matrix']
        for dim in ('execution', 'performance', 'logic', 'purpose_fulfillment'):
            score = matrix[dim]['score']
            assert 0.0 <= score <= 100.0

    def test_particle_like_profile_hits_95_targets(self):
        data = _base_output(
            kpis={
                'nodes_total': 3985,
                'edges_total': 12025,
                'dead_code_percent': 2.63,
                'knot_score': 4.1,
                'codebase_intelligence': 0.971,
                'q_distribution': {'excellent': 3739, 'good': 0, 'moderate': 0, 'poor': 0},
                'vectorization_status': 'failed',
                'vectorization_error': "No module named 'lancedb'",
                'ecosystem_discovery_status': 'skipped',
                'ecosystem_discovery_error': "No module named 'discovery_engine'",
                'topology_shape': 'CYCLIC_NETWORK',
            },
            purpose_field={
                'total_nodes': 3985,
                'uncertain_count': 1606,
                'god_class_count': 75,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.594,
            },
            performance={
                'hotspot_count': 10,
                'critical_path_length': 20,
                'critical_path_cost': 2808,
                'time_by_type': {'τ_compute': 139145.0, 'τ_instant': 6507.0, 'τ_io_local': 78500.0},
            },
            distributions={
                'types': {'Service': 12, 'Command': 8, 'UseCase': 4, 'Asserter': 40},
            },
        )
        result = compile_insights(data)
        matrix = result['mission_matrix']

        assert matrix['execution']['score'] >= 95.0
        assert matrix['performance']['score'] >= 95.0
        assert matrix['logic']['score'] >= 95.0
        assert matrix['purpose_fulfillment']['score'] >= 95.0
        assert matrix['all_targets_met'] is True

    def test_weak_profile_does_not_meet_targets(self):
        data = _base_output(
            kpis={
                'nodes_total': 100,
                'edges_total': 0,
                'dead_code_percent': 32.0,
                'knot_score': 9.0,
                'rho_antimatter': 0.12,
                'rho_policy': 0.06,
                'codebase_intelligence': 0.25,
                'vectorization_status': 'failed',
                'ecosystem_discovery_status': 'failed',
                'topology_shape': 'BIG_BALL_OF_MUD',
            },
            purpose_field={
                'total_nodes': 100,
                'uncertain_count': 60,
                'god_class_count': 40,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.35,
            },
            performance={
                'hotspot_count': 40,
                'critical_path_length': 120,
                'critical_path_cost': 1600,
                'time_by_type': {'compute': 95, 'io': 3, 'instant': 2},
            },
        )
        result = compile_insights(data)
        matrix = result['mission_matrix']
        assert matrix['all_targets_met'] is False
        assert matrix['purpose_fulfillment']['score'] < 95.0


# =============================================================================
# NAVIGATION
# =============================================================================

class TestNavigation:

    def test_navigation_has_sections(self):
        data = _base_output()
        result = compile_insights(data)
        nav = result['navigation']
        assert 'start_here' in nav
        assert 'critical_path' in nav
        assert 'top_risks' in nav

    def test_entry_points_in_start_here(self):
        data = _base_output(execution_flow={'entry_points': ['main', 'cli'], 'orphans': []})
        result = compile_insights(data)
        assert 'main' in result['navigation']['start_here']

    def test_hubs_in_start_here(self):
        data = _base_output(top_hubs=[{'name': 'BigService', 'in_degree': 20}])
        result = compile_insights(data)
        start = result['navigation']['start_here']
        assert any('BigService' in str(s) for s in start)


# =============================================================================
# EXECUTIVE SUMMARY
# =============================================================================

class TestExecutiveSummary:

    def test_summary_includes_grade(self):
        data = _base_output()
        result = compile_insights(data)
        assert result['grade'] in result['executive_summary']

    def test_summary_includes_node_count(self):
        data = _base_output(kpis={'nodes_total': 500})
        result = compile_insights(data)
        assert '500' in result['executive_summary']


# =============================================================================
# COMPILED INSIGHT DATACLASS
# =============================================================================

class TestCompiledInsight:

    def test_to_dict(self):
        insight = CompiledInsight(
            id='CI-001',
            category='test',
            severity='low',
            title='Test finding',
            description='A test.',
            evidence={'key': 'val'},
            interpretation='Means nothing.',
            recommendation='Do nothing.',
            effort='low',
        )
        d = insight.to_dict()
        assert d['id'] == 'CI-001'
        assert d['category'] == 'test'
        assert d['severity'] == 'low'


# =============================================================================
# FINDINGS SORTING
# =============================================================================

class TestFindingsSorting:

    def test_critical_first(self):
        """Findings should be sorted critical > high > medium > low > info."""
        data = _base_output(
            kpis={
                'dead_code_percent': 25.0,
                'knot_score': 1.0,
                'codebase_intelligence': 0.90,
                'topology_shape': 'STRICT_LAYERS',
            },
            topology={'shape': 'STRICT_LAYERS', 'description': 'Clean.', 'visual_metrics': {}},
        )
        result = compile_insights(data)
        findings = result['findings']
        if len(findings) >= 2:
            severities = [f['severity'] for f in findings]
            sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
            orders = [sev_order.get(s, 5) for s in severities]
            assert orders == sorted(orders), f"Not sorted: {severities}"


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:

    def test_empty_output(self):
        """Should handle empty/minimal output without crashing."""
        result = compile_insights({'kpis': {}, 'nodes': [], 'edges': []})
        assert isinstance(result, dict)
        assert result['grade'] in ('A', 'B', 'C', 'D', 'F')

    def test_missing_sections(self):
        """Should handle missing top-level keys gracefully."""
        result = compile_insights({})
        assert isinstance(result, dict)
        assert 'grade' in result

    def test_none_values_in_kpis(self):
        """Should handle None values in KPIs."""
        data = _base_output(kpis={'dead_code_percent': None, 'knot_score': None})
        # Should not raise
        result = compile_insights(data)
        assert isinstance(result, dict)
