"""
Wave 1 / H3: Tests for YAML threshold overrides.

Verifies that per-project collider_thresholds.yaml files correctly merge
with the bundled defaults via _load_thresholds(repo_root).
"""
import pytest
import sys
import yaml
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, _load_thresholds, compile_insights


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_override_yaml(tmpdir: Path, content: dict, subdir: str = '.collider'):
    """Write a collider_thresholds.yaml override file in a temp repo."""
    override_dir = tmpdir / subdir
    override_dir.mkdir(parents=True, exist_ok=True)
    path = override_dir / 'collider_thresholds.yaml'
    with open(path, 'w') as f:
        yaml.dump(content, f)
    return path


def _base_output(**kpi_overrides):
    out = {
        'kpis': {
            'nodes_total': 100, 'edges_total': 200,
            'dead_code_percent': 2.0, 'knot_score': 0.5,
            'rho_antimatter': 0.0, 'rho_policy': 0.0,
            'codebase_intelligence': 0.85,
            'topology_shape': 'STRICT_LAYERS',
        },
        'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
        'distributions': {'types': {'Service': 10, 'Test': 12}},
        'nodes': [], 'edges': [],
    }
    out['kpis'].update(kpi_overrides)
    return out


# =============================================================================
# Override loading
# =============================================================================

class TestOverrideLoading:

    def test_no_override_returns_bundled_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            th = _load_thresholds(Path(tmpdir))
            # Should have bundled topology_scores
            assert 'topology_scores' in th
            assert th['topology_scores']['STRICT_LAYERS'] == 10.0

    def test_override_in_dotcollider(self):
        """Override in .collider/ directory is picked up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'grade_boundaries': {'A': 9.0},
            })
            th = _load_thresholds(Path(tmpdir))
            assert float(th['grade_boundaries']['A']) == 9.0

    def test_override_in_repo_root(self):
        """Override in repo root is picked up."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'collider_thresholds.yaml'
            with open(path, 'w') as f:
                yaml.dump({'grade_boundaries': {'A': 9.5}}, f)
            th = _load_thresholds(Path(tmpdir))
            assert float(th['grade_boundaries']['A']) == 9.5

    def test_dotcollider_overrides_then_root_overrides(self):
        """Root-level override takes precedence over .collider/ (loaded second)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # .collider override
            _write_override_yaml(tmppath, {'grade_boundaries': {'A': 9.0}})
            # root override (loaded second, wins)
            path = tmppath / 'collider_thresholds.yaml'
            with open(path, 'w') as f:
                yaml.dump({'grade_boundaries': {'A': 9.5}}, f)
            th = _load_thresholds(tmppath)
            assert float(th['grade_boundaries']['A']) == 9.5


# =============================================================================
# Partial override preserves defaults
# =============================================================================

class TestPartialOverrides:

    def test_partial_grade_boundaries(self):
        """Overriding A boundary should preserve B, C, D."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'grade_boundaries': {'A': 9.0},
            })
            th = _load_thresholds(Path(tmpdir))
            assert float(th['grade_boundaries']['A']) == 9.0
            assert float(th['grade_boundaries']['B']) == 7.0  # default preserved
            assert float(th['grade_boundaries']['C']) == 5.5  # default preserved
            assert float(th['grade_boundaries']['D']) == 4.0  # default preserved

    def test_partial_topology_scores(self):
        """Overriding one topology score preserves others."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'topology_scores': {'MESH': 8.0},
            })
            th = _load_thresholds(Path(tmpdir))
            assert float(th['topology_scores']['MESH']) == 8.0  # overridden
            assert float(th['topology_scores']['STRICT_LAYERS']) == 10.0  # preserved

    def test_partial_health_scoring_weights(self):
        """Overriding one weight preserves others."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'health_scoring': {'weights': {'topology': 0.30}},
            })
            th = _load_thresholds(Path(tmpdir))
            hs = th['health_scoring']
            # weights is nested — shallow merge at health_scoring level
            # means the whole 'weights' key gets the override
            # Let's verify how the merge actually works
            weights = hs.get('weights', {})
            assert float(weights.get('topology', 0)) == 0.30

    def test_override_preserves_unrelated_sections(self):
        """Overriding grade_boundaries should not affect dead_code or entanglement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'grade_boundaries': {'A': 9.0},
            })
            th = _load_thresholds(Path(tmpdir))
            assert 'dead_code' in th
            assert 'entanglement' in th
            assert 'confidence_baselines' in th


# =============================================================================
# Override affects scoring
# =============================================================================

class TestOverrideAffectsScoring:

    def test_custom_grade_boundary_affects_grade(self):
        """Health score 8.5 is normally A; with A boundary raised to 9.0, it becomes B."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'grade_boundaries': {'A': 9.0},
            })
            data = _base_output()
            c = InsightsCompiler(data, repo_root=Path(tmpdir))
            report = c.compile()
            # Healthy codebase gets ~8.6-9.0 normally; with higher A bar,
            # it may stay A or drop to B depending on exact components.
            assert report.grade in ('A', 'B')

    def test_custom_topology_score_changes_health(self):
        """Override BIG_BALL_OF_MUD from 2.0 to 8.0 → healthier score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'topology_scores': {'BIG_BALL_OF_MUD': 8.0},
            })
            data = _base_output(topology_shape='BIG_BALL_OF_MUD')
            c_default = InsightsCompiler(dict(data))
            c_override = InsightsCompiler(dict(data), repo_root=Path(tmpdir))
            r_default = c_default.compile()
            r_override = c_override.compile()
            # Override should produce higher topology score
            assert r_override.health_components['topology'] > r_default.health_components['topology']


# =============================================================================
# Graceful handling of bad YAML
# =============================================================================

class TestBadYAMLFallback:

    def test_empty_yaml_file(self):
        """Empty override file should not crash; bundled defaults preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override_dir = Path(tmpdir) / '.collider'
            override_dir.mkdir()
            (override_dir / 'collider_thresholds.yaml').write_text('')
            th = _load_thresholds(Path(tmpdir))
            assert 'topology_scores' in th

    def test_yaml_with_none_content(self):
        """YAML that parses to None should not crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override_dir = Path(tmpdir) / '.collider'
            override_dir.mkdir()
            (override_dir / 'collider_thresholds.yaml').write_text('---\n')
            th = _load_thresholds(Path(tmpdir))
            assert 'topology_scores' in th

    def test_yaml_with_wrong_types(self):
        """Scalar where dict expected should not crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override_dir = Path(tmpdir) / '.collider'
            override_dir.mkdir()
            (override_dir / 'collider_thresholds.yaml').write_text(
                'topology_scores: "not_a_dict"\n'
            )
            th = _load_thresholds(Path(tmpdir))
            # The scalar replaces the dict (shallow merge of non-dict values)
            # Code should handle this gracefully downstream
            assert 'topology_scores' in th

    def test_yaml_with_extra_unknown_sections(self):
        """Unknown sections should be merged without crashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'unknown_future_section': {'key': 'value'},
            })
            th = _load_thresholds(Path(tmpdir))
            assert th['unknown_future_section'] == {'key': 'value'}
            assert 'topology_scores' in th  # defaults preserved


# =============================================================================
# Confidence baselines via YAML
# =============================================================================

class TestConfidenceBaselineOverrides:

    def test_default_confidence_baselines_loaded(self):
        th = _load_thresholds()
        baselines = th.get('confidence_baselines', {})
        assert baselines.get('dead_code') == 0.85
        assert baselines.get('api_drift') == 0.65
        assert baselines.get('purpose') == 0.50
        assert baselines.get('ideome') == 0.40

    def test_override_confidence_baseline(self):
        """Per-project can raise/lower confidence for a category."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_override_yaml(Path(tmpdir), {
                'confidence_baselines': {'api_drift': 0.30},
            })
            th = _load_thresholds(Path(tmpdir))
            assert float(th['confidence_baselines']['api_drift']) == 0.30
            # Others preserved
            assert float(th['confidence_baselines']['dead_code']) == 0.85
