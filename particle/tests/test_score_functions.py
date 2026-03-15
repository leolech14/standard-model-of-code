"""
Wave 1 / C3: Direct unit tests for all 9 _score_*() functions in InsightsCompiler.

These tests exercise the private scoring methods directly by constructing minimal
InsightsCompiler instances with synthetic full_output dicts.  Each function is
tested at representative input points (low, boundary, mid, high) to establish
a regression baseline before any behavioral changes.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, compile_insights


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compiler(**kpi_overrides) -> InsightsCompiler:
    """Build an InsightsCompiler with minimal data and targeted KPI overrides."""
    base = {
        'kpis': {
            'nodes_total': 100,
            'edges_total': 200,
            'dead_code_percent': 2.0,
            'orphan_count': 0,
            'orphan_percent': 0.0,
            'knot_score': 0.5,
            'cycles_detected': 0,
            'rho_antimatter': 0.0,
            'rho_policy': 0.0,
            'antimatter_count': 0,
            'policy_violation_count': 0,
            'signal_count': 0,
            'codebase_intelligence': 0.85,
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
        'topology': {'shape': 'STRICT_LAYERS', 'description': '', 'visual_metrics': {}},
        'distributions': {
            'types': {'Service': 10, 'Command': 5, 'Test': 12},
        },
        'nodes': [],
        'edges': [],
    }
    base['kpis'].update(kpi_overrides)
    return InsightsCompiler(base)


def _compiler_full(full_output: dict) -> InsightsCompiler:
    """Build an InsightsCompiler from a complete full_output dict."""
    return InsightsCompiler(full_output)


# =============================================================================
# 1. _score_topology
# =============================================================================

class TestScoreTopology:

    def test_strict_layers_is_10(self):
        c = _compiler(topology_shape='STRICT_LAYERS')
        assert c._score_topology() == 10.0

    def test_mesh_is_7(self):
        c = _compiler(topology_shape='MESH')
        assert c._score_topology() == 7.0

    def test_disconnected_islands_is_5(self):
        c = _compiler(topology_shape='DISCONNECTED_ISLANDS')
        assert c._score_topology() == 5.0

    def test_star_hub_is_4(self):
        c = _compiler(topology_shape='STAR_HUB')
        assert c._score_topology() == 4.0

    def test_big_ball_of_mud_is_2(self):
        c = _compiler(topology_shape='BIG_BALL_OF_MUD')
        assert c._score_topology() == 2.0

    def test_unknown_shape_gets_default(self):
        """Unknown shapes should fall back to _default (6.0)."""
        c = _compiler(topology_shape='NEVER_SEEN_BEFORE')
        assert c._score_topology() == 6.0

    def test_cyclic_network_is_7(self):
        """CYCLIC_NETWORK explicitly mapped to 7.0 (provisional/unvalidated).
        Rationale: cycles exist but limited; sits between DENSE_MESH and
        DISCONNECTED_ISLANDS.
        """
        c = _compiler(topology_shape='CYCLIC_NETWORK')
        assert c._score_topology() == 7.0

    def test_balanced_network_is_8(self):
        c = _compiler(topology_shape='BALANCED_NETWORK')
        assert c._score_topology() == 8.0

    def test_dense_mesh_is_7_5(self):
        c = _compiler(topology_shape='DENSE_MESH')
        assert c._score_topology() == 7.5

    def test_empty_shape_gets_default(self):
        c = _compiler(topology_shape='')
        assert c._score_topology() == 6.0

    def test_none_shape_gets_default(self):
        """When topology_shape is missing from kpis."""
        base = {'kpis': {}, 'nodes': [], 'edges': []}
        c = _compiler_full(base)
        assert c._score_topology() == 6.0


# =============================================================================
# 2. _score_constraints
# =============================================================================

class TestScoreConstraints:
    """Tests constraint scoring based on combined rho_antimatter + rho_policy.

    Default thresholds from YAML:
      perfect: < 0.01 → 10.0
      good:    < 0.03 → 8.0
      moderate:< 0.06 → 6.0
      poor:    < 0.10 → 4.0
      else:    → 2.0
    """

    def test_zero_violations_is_perfect(self):
        c = _compiler(rho_antimatter=0.0, rho_policy=0.0)
        assert c._score_constraints() == 10.0

    def test_just_below_perfect_threshold(self):
        c = _compiler(rho_antimatter=0.005, rho_policy=0.004)  # 0.009 < 0.01
        assert c._score_constraints() == 10.0

    def test_at_perfect_boundary(self):
        c = _compiler(rho_antimatter=0.01, rho_policy=0.0)  # 0.01 not < 0.01
        assert c._score_constraints() == 8.0

    def test_just_above_perfect_boundary(self):
        c = _compiler(rho_antimatter=0.011, rho_policy=0.0)  # 0.011 > 0.01
        assert c._score_constraints() == 8.0

    def test_good_range(self):
        c = _compiler(rho_antimatter=0.02, rho_policy=0.0)  # 0.02 < 0.03
        assert c._score_constraints() == 8.0

    def test_at_good_boundary(self):
        c = _compiler(rho_antimatter=0.03, rho_policy=0.0)  # 0.03 not < 0.03
        assert c._score_constraints() == 6.0

    def test_moderate_range(self):
        c = _compiler(rho_antimatter=0.04, rho_policy=0.01)  # 0.05 < 0.06
        assert c._score_constraints() == 6.0

    def test_at_moderate_boundary(self):
        c = _compiler(rho_antimatter=0.06, rho_policy=0.0)  # 0.06 not < 0.06
        assert c._score_constraints() == 4.0

    def test_poor_range(self):
        c = _compiler(rho_antimatter=0.08, rho_policy=0.0)  # 0.08 < 0.10
        assert c._score_constraints() == 4.0

    def test_at_poor_boundary(self):
        c = _compiler(rho_antimatter=0.10, rho_policy=0.0)  # 0.10 not < 0.10
        assert c._score_constraints() == 2.0

    def test_extreme_violations(self):
        c = _compiler(rho_antimatter=0.20, rho_policy=0.10)
        assert c._score_constraints() == 2.0

    def test_none_values_treated_as_zero(self):
        """None rho values should default to 0 (treated as clean)."""
        base = {
            'kpis': {'rho_antimatter': None, 'rho_policy': None},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(base)
        assert c._score_constraints() == 10.0


# =============================================================================
# 3. _score_purpose
# =============================================================================

class TestScorePurpose:
    """Tests the blended purpose score.

    Default sub-weights: ci=0.45, clarity=0.25, alignment=0.20, structural=0.10
    Inputs: codebase_intelligence, purpose_clarity, alignment_health,
            uncertain_ratio, god_class_count/ratio.
    """

    def test_high_ci_no_purpose_field(self):
        """When purpose_field data is absent, score is based on CI alone."""
        c = _compiler(codebase_intelligence=0.90)
        score = c._score_purpose()
        assert 8.0 <= score <= 10.0

    def test_low_ci_score(self):
        c = _compiler(codebase_intelligence=0.30)
        score = c._score_purpose()
        assert score < 5.0

    def test_zero_ci_score(self):
        c = _compiler(codebase_intelligence=0.0)
        score = c._score_purpose()
        assert score == 0.0

    def test_purpose_field_with_good_alignment(self):
        full = {
            'kpis': {'codebase_intelligence': 0.90, 'topology_shape': 'STRICT_LAYERS'},
            'purpose_field': {
                'total_nodes': 100,
                'uncertain_count': 5,
                'god_class_count': 0,
                'alignment_health': 'GOOD',
                'purpose_clarity': 0.95,
            },
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        score = c._score_purpose()
        assert score >= 8.5

    def test_purpose_field_with_critical_alignment_poor_locals(self):
        full = {
            'kpis': {'codebase_intelligence': 0.95, 'topology_shape': 'STRICT_LAYERS'},
            'purpose_field': {
                'total_nodes': 100,
                'uncertain_count': 45,
                'god_class_count': 35,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.55,
            },
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        score = c._score_purpose()
        # CRITICAL alignment with poor locals → low alignment_score (2.0)
        assert score < 8.0

    def test_guard_clause_triggers_on_critical_with_good_locals(self):
        """The guard clause (lines 1678-1685) overrides CRITICAL alignment to 8.5
        when local signals are strong (clarity >= 0.95, uncertain <= 0.05, god_ratio <= 0.03).
        This documents current behavior explicitly.
        """
        full = {
            'kpis': {'codebase_intelligence': 0.98, 'topology_shape': 'STRICT_LAYERS'},
            'purpose_field': {
                'total_nodes': 1000,
                'uncertain_count': 40,   # 4% < 5%
                'god_class_count': 20,   # 2% < 3%
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.96,  # > 0.95
            },
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        score = c._score_purpose()
        # Guard clause: alignment_score becomes 8.5 instead of 2.0
        # Score should be significantly higher than without guard clause
        assert score >= 8.0

    def test_guard_clause_does_NOT_trigger_when_clarity_below_threshold(self):
        """Guard clause requires clarity >= 0.95. At 0.94, CRITICAL maps to 2.0.
        Without the guard clause, alignment_score = 2.0, which drags the blended
        score lower than when the guard fires (alignment_score = 8.5).
        """
        full_with_guard = {
            'kpis': {'codebase_intelligence': 0.98, 'topology_shape': 'STRICT_LAYERS'},
            'purpose_field': {
                'total_nodes': 1000,
                'uncertain_count': 40,
                'god_class_count': 20,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.96,  # >= 0.95 — guard FIRES
            },
            'nodes': [], 'edges': [],
        }
        full_without_guard = {
            'kpis': {'codebase_intelligence': 0.98, 'topology_shape': 'STRICT_LAYERS'},
            'purpose_field': {
                'total_nodes': 1000,
                'uncertain_count': 40,
                'god_class_count': 20,
                'alignment_health': 'CRITICAL',
                'purpose_clarity': 0.94,  # < 0.95 — guard does NOT fire
            },
            'nodes': [], 'edges': [],
        }
        score_guarded = _compiler_full(full_with_guard)._score_purpose()
        score_unguarded = _compiler_full(full_without_guard)._score_purpose()
        # The unguarded path should produce a lower score because alignment maps
        # to 2.0 instead of 8.5.  The delta is alignment_weight * (8.5 - 2.0) = 0.20 * 6.5 = 1.3
        assert score_unguarded < score_guarded

    def test_purpose_bounded_0_to_10(self):
        c = _compiler(codebase_intelligence=1.0)
        score = c._score_purpose()
        assert 0.0 <= score <= 10.0


# =============================================================================
# 4. _score_test_coverage (test density)
# =============================================================================

class TestScoreTestCoverage:
    """Tests test atom density scoring.

    Counts atom types in distributions.types:
      test_atoms: [Asserter, Test, test]
      logic_atoms: [Service, Command, UseCase, ApplicationService, Controller, Handler]
    ratio = tests / logic

    Thresholds: ideal >= 1.0 → 10.0, good >= 0.5 → 7.0, low >= 0.2 → 5.0, else → 3.0
    """

    def _compiler_with_types(self, types_dict: dict) -> InsightsCompiler:
        full = {
            'kpis': {'topology_shape': 'STRICT_LAYERS'},
            'distributions': {'types': types_dict},
            'nodes': [], 'edges': [],
        }
        return _compiler_full(full)

    def test_ideal_ratio(self):
        """tests >= logic → 10.0"""
        c = self._compiler_with_types({'Test': 20, 'Service': 10, 'Command': 5})
        assert c._score_test_coverage() == 10.0

    def test_good_ratio(self):
        """0.5 <= ratio < 1.0 → 7.0"""
        c = self._compiler_with_types({'Test': 8, 'Service': 10, 'Command': 5})
        # ratio = 8/15 ≈ 0.53
        assert c._score_test_coverage() == 7.0

    def test_low_ratio(self):
        """0.2 <= ratio < 0.5 → 5.0"""
        c = self._compiler_with_types({'Test': 4, 'Service': 10, 'Command': 5})
        # ratio = 4/15 ≈ 0.27
        assert c._score_test_coverage() == 5.0

    def test_minimal_ratio(self):
        """ratio < 0.2 → 3.0"""
        c = self._compiler_with_types({'Test': 1, 'Service': 10, 'Command': 5})
        # ratio = 1/15 ≈ 0.07
        assert c._score_test_coverage() == 3.0

    def test_no_logic_atoms(self):
        """No logic atoms → 7.0 (no logic to test)."""
        c = self._compiler_with_types({'Test': 5, 'Utility': 10})
        assert c._score_test_coverage() == 7.0

    def test_no_test_atoms(self):
        """No test atoms → 3.0 (zero ratio)."""
        c = self._compiler_with_types({'Service': 10, 'Command': 5})
        assert c._score_test_coverage() == 3.0

    def test_empty_types(self):
        """Empty distributions → 7.0 (no logic to test)."""
        c = self._compiler_with_types({})
        assert c._score_test_coverage() == 7.0

    def test_asserter_counted_as_test(self):
        """Asserter atoms should count as test artifacts."""
        c = self._compiler_with_types({'Asserter': 20, 'Service': 10})
        # ratio = 20/10 = 2.0 → 10.0
        assert c._score_test_coverage() == 10.0

    def test_at_exact_good_boundary(self):
        """ratio = exactly 0.5 → 7.0 (>= 0.5)."""
        c = self._compiler_with_types({'Test': 5, 'Service': 10})
        # ratio = 5/10 = 0.5
        assert c._score_test_coverage() == 7.0

    def test_just_below_good_boundary(self):
        """ratio just below 0.5 → 5.0."""
        c = self._compiler_with_types({'Test': 49, 'Service': 100})
        # ratio = 0.49
        assert c._score_test_coverage() == 5.0


# =============================================================================
# 5. _score_dead_code
# =============================================================================

class TestScoreDeadCode:
    """Tests dead code scoring based on dead_code_percent.

    Note: dead_code_percent is 0-100 in KPIs, converted to ratio 0.0-1.0 internally.
    Thresholds (as ratios): low=0.03, moderate=0.08, high=0.15, severe=0.25
    Which means percent thresholds: 3%, 8%, 15%, 25%
    """

    def test_zero_dead_code(self):
        c = _compiler(dead_code_percent=0.0)
        assert c._score_dead_code() == 10.0

    def test_just_below_low_threshold(self):
        c = _compiler(dead_code_percent=2.9)  # 2.9% → ratio 0.029 < 0.03
        assert c._score_dead_code() == 10.0

    def test_at_low_threshold(self):
        c = _compiler(dead_code_percent=3.0)  # 3.0% → ratio 0.03 not < 0.03
        assert c._score_dead_code() == 8.0

    def test_just_above_low_threshold(self):
        c = _compiler(dead_code_percent=3.1)  # ratio 0.031
        assert c._score_dead_code() == 8.0

    def test_just_below_moderate_threshold(self):
        c = _compiler(dead_code_percent=7.9)  # ratio 0.079 < 0.08
        assert c._score_dead_code() == 8.0

    def test_at_moderate_threshold(self):
        c = _compiler(dead_code_percent=8.0)  # ratio 0.08 not < 0.08
        assert c._score_dead_code() == 6.0

    def test_just_below_high_threshold(self):
        c = _compiler(dead_code_percent=14.9)  # ratio 0.149 < 0.15
        assert c._score_dead_code() == 6.0

    def test_at_high_threshold(self):
        c = _compiler(dead_code_percent=15.0)  # ratio 0.15 not < 0.15
        assert c._score_dead_code() == 4.0

    def test_just_below_severe_threshold(self):
        c = _compiler(dead_code_percent=24.9)  # ratio 0.249 < 0.25
        assert c._score_dead_code() == 4.0

    def test_at_severe_threshold(self):
        c = _compiler(dead_code_percent=25.0)  # ratio 0.25 not < 0.25
        assert c._score_dead_code() == 2.0

    def test_extreme_dead_code(self):
        c = _compiler(dead_code_percent=80.0)
        assert c._score_dead_code() == 2.0

    def test_none_treated_as_zero(self):
        c = _compiler(dead_code_percent=None)
        assert c._score_dead_code() == 10.0


# =============================================================================
# 6. _score_entanglement
# =============================================================================

class TestScoreEntanglement:
    """Tests entanglement scoring based on knot_score.

    Thresholds: clean=1, low=3, moderate=5, severe=8
    """

    def test_zero_knot(self):
        c = _compiler(knot_score=0)
        assert c._score_entanglement() == 10.0

    def test_just_below_clean_threshold(self):
        c = _compiler(knot_score=0.9)
        assert c._score_entanglement() == 10.0

    def test_at_clean_threshold(self):
        c = _compiler(knot_score=1)  # 1 not < 1
        assert c._score_entanglement() == 8.0

    def test_just_above_clean_threshold(self):
        c = _compiler(knot_score=1.1)
        assert c._score_entanglement() == 8.0

    def test_just_below_low_threshold(self):
        c = _compiler(knot_score=2.9)
        assert c._score_entanglement() == 8.0

    def test_at_low_threshold(self):
        c = _compiler(knot_score=3)  # 3 not < 3
        assert c._score_entanglement() == 6.0

    def test_moderate_range(self):
        c = _compiler(knot_score=4)
        assert c._score_entanglement() == 6.0

    def test_at_moderate_threshold(self):
        c = _compiler(knot_score=5)  # 5 not < 5
        assert c._score_entanglement() == 4.0

    def test_at_severe_threshold(self):
        c = _compiler(knot_score=8)  # 8 not < 8
        assert c._score_entanglement() == 2.0

    def test_extreme_knot(self):
        c = _compiler(knot_score=20)
        assert c._score_entanglement() == 2.0

    def test_none_treated_as_zero(self):
        c = _compiler(knot_score=None)
        assert c._score_entanglement() == 10.0


# =============================================================================
# 7. _score_rpbl_balance
# =============================================================================

class TestScoreRPBLBalance:
    """Tests RPBL balance scoring.

    Penalties applied from 10.0 baseline:
      responsibility > 6 → -2
      purity < 4 → -2
      boundary > 6 → -1.5
      lifecycle > 6 → -1.5
    Floor = 2.0
    """

    def test_balanced_profile(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 10.0

    def test_heavy_responsibility_only(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 7, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 8.0  # 10 - 2

    def test_light_purity_only(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 4, 'purity': 3, 'boundary': 3, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 8.0  # 10 - 2

    def test_heavy_boundary_only(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 7, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 8.5  # 10 - 1.5

    def test_heavy_lifecycle_only(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 4, 'purity': 7, 'boundary': 3, 'lifecycle': 7},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 8.5  # 10 - 1.5

    def test_all_penalties_applied(self):
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 8, 'purity': 2, 'boundary': 8, 'lifecycle': 8},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        # 10 - 2 - 2 - 1.5 - 1.5 = 3.0
        assert c._score_rpbl_balance() == 3.0

    def test_floor_at_2(self):
        """Even with massive penalties, floor is 2.0."""
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 9, 'purity': 1, 'boundary': 9, 'lifecycle': 9},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        # 10 - 2 - 2 - 1.5 - 1.5 = 3.0 (still above floor)
        assert c._score_rpbl_balance() >= 2.0

    def test_at_responsibility_boundary(self):
        """responsibility = 6 (not > 6) → no penalty."""
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 6, 'purity': 7, 'boundary': 3, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 10.0

    def test_at_purity_boundary(self):
        """purity = 4 (not < 4) → no penalty."""
        full = {
            'kpis': {},
            'rpbl_profile': {'responsibility': 4, 'purity': 4, 'boundary': 3, 'lifecycle': 3},
            'nodes': [], 'edges': [],
        }
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 10.0

    def test_missing_rpbl_profile(self):
        """Missing rpbl_profile → 6.0 fallback."""
        full = {'kpis': {}, 'nodes': [], 'edges': []}
        c = _compiler_full(full)
        assert c._score_rpbl_balance() == 6.0


# =============================================================================
# 8. _compute_health_score
# =============================================================================

class TestComputeHealthScore:
    """Tests weighted health score computation.

    Default weights:
      topology=0.20, constraints=0.20, purpose=0.15,
      test_coverage=0.15, dead_code=0.10, entanglement=0.10, rpbl_balance=0.10
    Sum = 1.0
    """

    def test_all_perfect(self):
        components = {
            'topology': 10.0, 'constraints': 10.0, 'purpose': 10.0,
            'test_coverage': 10.0, 'dead_code': 10.0, 'entanglement': 10.0,
            'rpbl_balance': 10.0,
        }
        c = _compiler()
        score = c._compute_health_score(components)
        assert score == 10.0

    def test_all_minimum(self):
        components = {
            'topology': 0.0, 'constraints': 0.0, 'purpose': 0.0,
            'test_coverage': 0.0, 'dead_code': 0.0, 'entanglement': 0.0,
            'rpbl_balance': 0.0,
        }
        c = _compiler()
        score = c._compute_health_score(components)
        assert score == 0.0

    def test_topology_weight_dominance(self):
        """Topology has 20% weight — changing it by 5 should shift score by 1.0."""
        base = {
            'topology': 5.0, 'constraints': 5.0, 'purpose': 5.0,
            'test_coverage': 5.0, 'dead_code': 5.0, 'entanglement': 5.0,
            'rpbl_balance': 5.0,
        }
        high = dict(base, topology=10.0)
        c = _compiler()
        base_score = c._compute_health_score(base)
        high_score = c._compute_health_score(high)
        assert abs(base_score - 5.0) < 0.01
        assert abs(high_score - 6.0) < 0.01  # 5 * 0.2 bump = 1.0

    def test_clamped_at_10(self):
        """Even if components somehow exceed 10, health score capped at 10."""
        components = {
            'topology': 15.0, 'constraints': 15.0, 'purpose': 15.0,
            'test_coverage': 15.0, 'dead_code': 15.0, 'entanglement': 15.0,
            'rpbl_balance': 15.0,
        }
        c = _compiler()
        score = c._compute_health_score(components)
        assert score == 10.0

    def test_missing_component_defaults_to_5(self):
        """Missing component keys default to 5.0 in the computation."""
        components = {'topology': 10.0}  # All others missing
        c = _compiler()
        score = c._compute_health_score(components)
        # 10*0.20 + 5*0.20 + 5*0.15 + 5*0.15 + 5*0.10 + 5*0.10 + 5*0.10
        # = 2.0 + 1.0 + 0.75 + 0.75 + 0.50 + 0.50 + 0.50 = 6.0
        assert abs(score - 6.0) < 0.01


# =============================================================================
# 9. _score_to_grade
# =============================================================================

class TestScoreToGrade:
    """Tests grade assignment from health score.

    Boundaries: A >= 8.5, B >= 7.0, C >= 5.5, D >= 4.0, F < 4.0
    """

    def test_perfect_is_A(self):
        c = _compiler()
        assert c._score_to_grade(10.0) == 'A'

    def test_at_A_boundary(self):
        c = _compiler()
        assert c._score_to_grade(8.5) == 'A'

    def test_just_below_A(self):
        c = _compiler()
        assert c._score_to_grade(8.49) == 'B'

    def test_at_B_boundary(self):
        c = _compiler()
        assert c._score_to_grade(7.0) == 'B'

    def test_just_below_B(self):
        c = _compiler()
        assert c._score_to_grade(6.99) == 'C'

    def test_at_C_boundary(self):
        c = _compiler()
        assert c._score_to_grade(5.5) == 'C'

    def test_just_below_C(self):
        c = _compiler()
        assert c._score_to_grade(5.49) == 'D'

    def test_at_D_boundary(self):
        c = _compiler()
        assert c._score_to_grade(4.0) == 'D'

    def test_just_below_D(self):
        c = _compiler()
        assert c._score_to_grade(3.99) == 'F'

    def test_zero_is_F(self):
        c = _compiler()
        assert c._score_to_grade(0.0) == 'F'
