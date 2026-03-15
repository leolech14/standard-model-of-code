"""
Wave 4 / H5 + M3: Purpose guard clause finding + confidence disclaimer.

H5: When the purpose guard clause fires, a provisional info finding is emitted.
M3: Markdown output includes a confidence disclaimer footer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, compile_insights, compile_insights_report


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
            'codebase_intelligence': 0.98,
            'codebase_interpretation': 'Excellent',
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


# =========================================================================
# H5: Purpose guard clause surfaced as finding
# =========================================================================

class TestPurposeGuardFinding:

    @staticmethod
    def _purpose_field_dict(alignment='CRITICAL', clarity=0.97,
                            uncertain_count=1, god_class_count=1,
                            total_nodes=100):
        """Build a purpose_field dict as it appears in full_output
        (serialized via .summary(), not a live object)."""
        return {
            'purpose_clarity': clarity,
            'alignment_health': alignment,
            'uncertain_count': uncertain_count,
            'god_class_count': god_class_count,
            'total_nodes': total_nodes,
        }

    def test_guard_fires_emits_finding(self):
        """When guard clause fires, an info finding with 'provisional' label appears."""
        pf = self._purpose_field_dict(
            alignment='CRITICAL', clarity=0.97,
            uncertain_count=1, god_class_count=1, total_nodes=100,
        )
        data = _base_output(purpose_field=pf)
        result = compile_insights(data)
        guard_findings = [
            f for f in result['findings']
            if 'guard clause' in f.get('title', '').lower()
        ]
        assert len(guard_findings) == 1
        gf = guard_findings[0]
        assert gf['severity'] == 'info'
        assert gf['category'] == 'purpose'
        assert 'provisional' in gf['title'].lower()
        assert gf['evidence']['override_from'] == 2.0
        assert gf['evidence']['override_to'] == 8.5
        assert gf['evidence']['alignment_health'] == 'CRITICAL'
        assert gf['evidence']['behavior_status'] == 'provisional_compatibility'
        assert gf['evidence']['purpose_clarity'] is not None
        assert gf['evidence']['uncertain_ratio'] is not None
        assert gf['evidence']['god_class_ratio'] is not None

    def test_guard_does_not_fire_no_finding(self):
        """When alignment is GOOD, no guard clause finding appears."""
        pf = self._purpose_field_dict(alignment='GOOD')
        data = _base_output(purpose_field=pf)
        result = compile_insights(data)
        guard_findings = [
            f for f in result['findings']
            if 'guard clause' in f.get('title', '').lower()
        ]
        assert len(guard_findings) == 0

    def test_guard_not_fired_when_no_purpose_field(self):
        """Without purpose_field, no guard clause finding."""
        data = _base_output()
        result = compile_insights(data)
        guard_findings = [
            f for f in result['findings']
            if 'guard clause' in f.get('title', '').lower()
        ]
        assert len(guard_findings) == 0

    def test_guard_not_fired_high_uncertainty(self):
        """CRITICAL alignment but high uncertainty: guard should NOT fire."""
        pf = self._purpose_field_dict(
            alignment='CRITICAL', clarity=0.97,
            uncertain_count=20, god_class_count=1, total_nodes=100,
        )
        data = _base_output(purpose_field=pf)
        result = compile_insights(data)
        guard_findings = [
            f for f in result['findings']
            if 'guard clause' in f.get('title', '').lower()
        ]
        assert len(guard_findings) == 0


# =========================================================================
# M3: Confidence disclaimer in markdown
# =========================================================================

class TestConfidenceDisclaimer:

    def test_disclaimer_in_markdown(self):
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        assert 'Confidence expresses' in md

    def test_disclaimer_mentions_reliability(self):
        """Disclaimer must explain confidence = reliability of method, not severity."""
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        assert 'reliability of the analysis method' in md.lower()

    def test_disclaimer_mentions_provisional(self):
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        assert 'provisional' in md.lower()

    def test_disclaimer_at_end(self):
        """Disclaimer should be near the end of the markdown output."""
        data = _base_output()
        report = compile_insights_report(data)
        md = report.to_markdown()
        lines = [l for l in md.strip().split('\n') if l.strip()]
        # The disclaimer should be in the last 5 non-empty lines
        last_lines = '\n'.join(lines[-5:]).lower()
        assert 'confidence expresses' in last_lines
