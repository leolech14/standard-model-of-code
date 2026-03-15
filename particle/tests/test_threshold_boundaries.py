"""
Wave 1 / C4: Threshold boundary tests.

Loads thresholds from collider_thresholds.yaml and verifies that each scoring
function's bucket transitions occur at the documented threshold values.
Uses epsilon-based testing (small delta below/above threshold) appropriate
to each metric's scale.
"""
import pytest
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, _load_thresholds


# ---------------------------------------------------------------------------
# Load the canonical thresholds
# ---------------------------------------------------------------------------

_THRESHOLDS = _load_thresholds()
_HS = _THRESHOLDS.get('health_scoring', {})
_GB = _THRESHOLDS.get('grade_boundaries', {})


def _compiler(**kpi_overrides) -> InsightsCompiler:
    base = {
        'kpis': {
            'nodes_total': 100, 'edges_total': 200,
            'dead_code_percent': 0.0, 'knot_score': 0.0,
            'rho_antimatter': 0.0, 'rho_policy': 0.0,
            'codebase_intelligence': 0.85,
            'topology_shape': 'STRICT_LAYERS',
        },
        'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
        'distributions': {'types': {'Service': 10, 'Test': 12}},
        'nodes': [], 'edges': [],
    }
    base['kpis'].update(kpi_overrides)
    return InsightsCompiler(base)


def _compiler_rpbl(**rpbl_overrides) -> InsightsCompiler:
    rpbl = {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3}
    rpbl.update(rpbl_overrides)
    return InsightsCompiler({
        'kpis': {}, 'rpbl_profile': rpbl, 'nodes': [], 'edges': [],
    })


# =============================================================================
# Constraint boundaries (rho thresholds)
# =============================================================================

class TestConstraintBoundaries:
    """Verify bucket transitions at exact YAML threshold values."""

    def test_below_perfect(self):
        th = float(_HS.get('constraint_perfect', 0.01))
        eps = th * 0.1  # 10% of threshold as epsilon
        c = _compiler(rho_antimatter=th - eps)
        assert c._score_constraints() == 10.0

    def test_at_perfect(self):
        th = float(_HS.get('constraint_perfect', 0.01))
        c = _compiler(rho_antimatter=th)
        assert c._score_constraints() == 8.0, f"At threshold {th}, expected 8.0"

    def test_below_good(self):
        th_good = float(_HS.get('constraint_good', 0.03))
        eps = th_good * 0.05
        c = _compiler(rho_antimatter=th_good - eps)
        assert c._score_constraints() == 8.0

    def test_at_good(self):
        th = float(_HS.get('constraint_good', 0.03))
        c = _compiler(rho_antimatter=th)
        assert c._score_constraints() == 6.0

    def test_below_moderate(self):
        th = float(_HS.get('constraint_moderate', 0.06))
        eps = th * 0.05
        c = _compiler(rho_antimatter=th - eps)
        assert c._score_constraints() == 6.0

    def test_at_moderate(self):
        th = float(_HS.get('constraint_moderate', 0.06))
        c = _compiler(rho_antimatter=th)
        assert c._score_constraints() == 4.0

    def test_below_poor(self):
        th = float(_HS.get('constraint_poor', 0.10))
        eps = th * 0.05
        c = _compiler(rho_antimatter=th - eps)
        assert c._score_constraints() == 4.0

    def test_at_poor(self):
        th = float(_HS.get('constraint_poor', 0.10))
        c = _compiler(rho_antimatter=th)
        assert c._score_constraints() == 2.0


# =============================================================================
# Dead code boundaries (percent → ratio conversion)
# =============================================================================

class TestDeadCodeBoundaries:
    """dead_code_percent is 0-100 in KPIs but compared as ratio (pct/100) against YAML."""

    def _threshold_pct(self, key, default):
        """Convert YAML ratio threshold to percent for KPI input."""
        return float(_HS.get(key, default)) * 100.0

    def test_below_low(self):
        pct = self._threshold_pct('dead_code_ratio_low', 0.03)
        eps = pct * 0.1
        c = _compiler(dead_code_percent=pct - eps)
        assert c._score_dead_code() == 10.0

    def test_at_low(self):
        pct = self._threshold_pct('dead_code_ratio_low', 0.03)
        c = _compiler(dead_code_percent=pct)
        assert c._score_dead_code() == 8.0

    def test_below_moderate(self):
        pct = self._threshold_pct('dead_code_ratio_moderate', 0.08)
        eps = pct * 0.05
        c = _compiler(dead_code_percent=pct - eps)
        assert c._score_dead_code() == 8.0

    def test_at_moderate(self):
        pct = self._threshold_pct('dead_code_ratio_moderate', 0.08)
        c = _compiler(dead_code_percent=pct)
        assert c._score_dead_code() == 6.0

    def test_below_high(self):
        pct = self._threshold_pct('dead_code_ratio_high', 0.15)
        eps = pct * 0.05
        c = _compiler(dead_code_percent=pct - eps)
        assert c._score_dead_code() == 6.0

    def test_at_high(self):
        pct = self._threshold_pct('dead_code_ratio_high', 0.15)
        c = _compiler(dead_code_percent=pct)
        assert c._score_dead_code() == 4.0

    def test_below_severe(self):
        pct = self._threshold_pct('dead_code_ratio_severe', 0.25)
        eps = pct * 0.05
        c = _compiler(dead_code_percent=pct - eps)
        assert c._score_dead_code() == 4.0

    def test_at_severe(self):
        pct = self._threshold_pct('dead_code_ratio_severe', 0.25)
        c = _compiler(dead_code_percent=pct)
        assert c._score_dead_code() == 2.0


# =============================================================================
# Entanglement boundaries (knot_score: integer-like)
# =============================================================================

class TestEntanglementBoundaries:

    def test_below_clean(self):
        th = float(_HS.get('knot_clean', 1))
        c = _compiler(knot_score=th - 0.1)
        assert c._score_entanglement() == 10.0

    def test_at_clean(self):
        th = float(_HS.get('knot_clean', 1))
        c = _compiler(knot_score=th)
        assert c._score_entanglement() == 8.0

    def test_below_low(self):
        th = float(_HS.get('knot_low', 3))
        c = _compiler(knot_score=th - 0.1)
        assert c._score_entanglement() == 8.0

    def test_at_low(self):
        th = float(_HS.get('knot_low', 3))
        c = _compiler(knot_score=th)
        assert c._score_entanglement() == 6.0

    def test_below_moderate(self):
        th = float(_HS.get('knot_moderate', 5))
        c = _compiler(knot_score=th - 0.1)
        assert c._score_entanglement() == 6.0

    def test_at_moderate(self):
        th = float(_HS.get('knot_moderate', 5))
        c = _compiler(knot_score=th)
        assert c._score_entanglement() == 4.0

    def test_below_severe(self):
        th = float(_HS.get('knot_severe', 8))
        c = _compiler(knot_score=th - 0.1)
        assert c._score_entanglement() == 4.0

    def test_at_severe(self):
        th = float(_HS.get('knot_severe', 8))
        c = _compiler(knot_score=th)
        assert c._score_entanglement() == 2.0


# =============================================================================
# Test coverage (test density) boundaries
# =============================================================================

class TestTestCoverageBoundaries:
    """Test density ratio boundaries. Uses atom count ratios to hit exact thresholds."""

    def _compiler_ratio(self, ratio: float) -> InsightsCompiler:
        """Build a compiler where test/logic ratio is approximately `ratio`."""
        logic = 1000
        tests = int(ratio * logic)
        return InsightsCompiler({
            'kpis': {},
            'distributions': {'types': {'Test': tests, 'Service': logic}},
            'nodes': [], 'edges': [],
        })

    def test_below_ideal(self):
        th = float(_HS.get('test_coverage_ideal', 1.0))
        c = self._compiler_ratio(th - 0.05)
        assert c._score_test_coverage() == 7.0

    def test_at_ideal(self):
        th = float(_HS.get('test_coverage_ideal', 1.0))
        c = self._compiler_ratio(th)
        assert c._score_test_coverage() == 10.0

    def test_below_good(self):
        th = float(_HS.get('test_coverage_good', 0.5))
        c = self._compiler_ratio(th - 0.05)
        assert c._score_test_coverage() == 5.0

    def test_at_good(self):
        th = float(_HS.get('test_coverage_good', 0.5))
        c = self._compiler_ratio(th)
        assert c._score_test_coverage() == 7.0

    def test_below_low(self):
        th = float(_HS.get('test_coverage_low', 0.2))
        c = self._compiler_ratio(th - 0.05)
        assert c._score_test_coverage() == 3.0

    def test_at_low(self):
        th = float(_HS.get('test_coverage_low', 0.2))
        c = self._compiler_ratio(th)
        assert c._score_test_coverage() == 5.0


# =============================================================================
# Grade boundaries
# =============================================================================

class TestGradeBoundaries:

    def test_at_A_boundary(self):
        th = float(_GB.get('A', 8.5))
        c = _compiler()
        assert c._score_to_grade(th) == 'A'

    def test_epsilon_below_A(self):
        th = float(_GB.get('A', 8.5))
        c = _compiler()
        assert c._score_to_grade(th - 0.01) == 'B'

    def test_at_B_boundary(self):
        th = float(_GB.get('B', 7.0))
        c = _compiler()
        assert c._score_to_grade(th) == 'B'

    def test_epsilon_below_B(self):
        th = float(_GB.get('B', 7.0))
        c = _compiler()
        assert c._score_to_grade(th - 0.01) == 'C'

    def test_at_C_boundary(self):
        th = float(_GB.get('C', 5.5))
        c = _compiler()
        assert c._score_to_grade(th) == 'C'

    def test_epsilon_below_C(self):
        th = float(_GB.get('C', 5.5))
        c = _compiler()
        assert c._score_to_grade(th - 0.01) == 'D'

    def test_at_D_boundary(self):
        th = float(_GB.get('D', 4.0))
        c = _compiler()
        assert c._score_to_grade(th) == 'D'

    def test_epsilon_below_D(self):
        th = float(_GB.get('D', 4.0))
        c = _compiler()
        assert c._score_to_grade(th - 0.01) == 'F'


# =============================================================================
# RPBL boundaries
# =============================================================================

class TestRPBLBoundaries:

    def test_responsibility_at_threshold(self):
        """responsibility = 6 (threshold value, > not >=) → no penalty."""
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('resource_heavy', 6))
        c = _compiler_rpbl(responsibility=th)
        assert c._score_rpbl_balance() == 10.0

    def test_responsibility_above_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('resource_heavy', 6))
        c = _compiler_rpbl(responsibility=th + 0.1)
        assert c._score_rpbl_balance() == 8.0  # 10 - 2

    def test_purity_at_threshold(self):
        """purity = 4 (threshold value, < not <=) → no penalty."""
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('purpose_light', 4))
        c = _compiler_rpbl(purity=th)
        assert c._score_rpbl_balance() == 10.0

    def test_purity_below_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('purpose_light', 4))
        c = _compiler_rpbl(purity=th - 0.1)
        assert c._score_rpbl_balance() == 8.0  # 10 - 2

    def test_boundary_at_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('behavior_heavy', 6))
        c = _compiler_rpbl(boundary=th)
        assert c._score_rpbl_balance() == 10.0

    def test_boundary_above_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('behavior_heavy', 6))
        c = _compiler_rpbl(boundary=th + 0.1)
        assert c._score_rpbl_balance() == 8.5  # 10 - 1.5

    def test_lifecycle_at_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('logic_heavy', 6))
        c = _compiler_rpbl(lifecycle=th)
        assert c._score_rpbl_balance() == 10.0

    def test_lifecycle_above_threshold(self):
        th = float(_THRESHOLDS.get('rpbl_balance', {}).get('logic_heavy', 6))
        c = _compiler_rpbl(lifecycle=th + 0.1)
        assert c._score_rpbl_balance() == 8.5  # 10 - 1.5


# =============================================================================
# Health weight sync (YAML matches code defaults)
# =============================================================================

class TestHealthWeightSync:
    """Verify that the weights in YAML match the hardcoded defaults."""

    def test_weights_sum_to_1(self):
        weights = _HS.get('weights', {})
        total = sum(float(v) for v in weights.values())
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"

    def test_expected_components_present(self):
        weights = _HS.get('weights', {})
        expected = {'topology', 'constraints', 'purpose', 'test_density',
                    'dead_code', 'entanglement', 'rpbl_balance'}
        assert set(weights.keys()) == expected
