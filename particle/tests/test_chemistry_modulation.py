"""
Wave 1 / H4: Tests for chemistry modulation of health components.

Verifies that ChemistryLab.get_modulation() coefficients are correctly applied
to health component scores in _compute_health_components().
"""
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from insights_compiler import InsightsCompiler, compile_insights


# ---------------------------------------------------------------------------
# Mock ChemistryLab
# ---------------------------------------------------------------------------

@dataclass
class MockModulation:
    target: str
    coefficient: float


class MockChemistryLab:
    """Minimal mock of data_chemistry.ChemistryLab with known modulations."""

    def __init__(self, modulations: dict[str, float] | None = None):
        """
        Args:
            modulations: mapping of target → coefficient.
                         e.g. {'topology': 0.8, 'purpose': 1.2}
        """
        self._mods = modulations or {}
        # Build the modulations list (used by get_modulation)
        self.modulations = [MockModulation(t, c) for t, c in self._mods.items()]

    def get_modulation(self, target: str) -> float:
        """Get combined modulation coefficient for a target. 1.0 = neutral."""
        coeff = 1.0
        for m in self.modulations:
            if m.target == target:
                coeff *= m.coefficient
        return coeff

    def get_result(self):
        return {'modulations_by_target': self._mods, 'syndromes': []}


def _base_output(**extras) -> dict:
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
    out.update(extras)
    return out


# =============================================================================
# Neutral modulation (no change)
# =============================================================================

class TestNeutralModulation:

    def test_no_lab_means_no_modulation(self):
        """Without a chemistry lab, scores are unmodulated."""
        data = _base_output()
        c = InsightsCompiler(data)
        assert c._lab is None
        components = c._compute_health_components()
        # All components should be their natural values
        assert components['topology'] == 10.0  # STRICT_LAYERS

    def test_all_neutral_modulations(self):
        """All modulations at 1.0 should produce identical scores."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({
            'topology': 1.0,
            'constraints': 1.0,
            'purpose': 1.0,
            'test_coverage': 1.0,
            'dead_code': 1.0,
            'entanglement': 1.0,
            'rpbl_balance': 1.0,
        })
        c_neutral = InsightsCompiler(data)
        assert c_neutral._lab is not None

        c_none = InsightsCompiler(_base_output())
        comp_neutral = c_neutral._compute_health_components()
        comp_none = c_none._compute_health_components()

        for key in comp_none:
            assert abs(comp_neutral[key] - comp_none[key]) < 0.01, \
                f"{key}: neutral={comp_neutral[key]}, none={comp_none[key]}"


# =============================================================================
# Penalty modulation (coefficient < 1.0)
# =============================================================================

class TestPenaltyModulation:

    def test_topology_penalty(self):
        """0.8 coefficient on topology should reduce score by 20%."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({'topology': 0.8})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # STRICT_LAYERS = 10.0 * 0.8 = 8.0
        assert abs(components['topology'] - 8.0) < 0.01

    def test_constraints_penalty(self):
        """0.7 coefficient on constraints."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({'constraints': 0.7})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # rho=0 → 10.0 * 0.7 = 7.0
        assert abs(components['constraints'] - 7.0) < 0.01

    def test_multiple_penalties(self):
        """Multiple targets modulated simultaneously."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({
            'topology': 0.8,
            'constraints': 0.9,
        })
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        assert abs(components['topology'] - 8.0) < 0.01
        assert abs(components['constraints'] - 9.0) < 0.01
        # Unmodulated components should be unchanged
        assert components['dead_code'] == 10.0  # 2% dead code → 10.0


# =============================================================================
# Boost modulation (coefficient > 1.0)
# =============================================================================

class TestBoostModulation:

    def test_topology_boost(self):
        """1.2 coefficient on topology with MESH shape (7.0 base)."""
        data = _base_output()
        data['kpis']['topology_shape'] = 'MESH'  # MESH = 7.0
        data['_chemistry_lab'] = MockChemistryLab({'topology': 1.2})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # 7.0 * 1.2 = 8.4
        assert abs(components['topology'] - 8.4) < 0.01


# =============================================================================
# Clamping (0.0-10.0)
# =============================================================================

class TestModulationClamping:

    def test_clamp_at_10(self):
        """Boost beyond 10.0 should be clamped."""
        data = _base_output()  # topology = STRICT_LAYERS = 10.0
        data['_chemistry_lab'] = MockChemistryLab({'topology': 1.5})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # 10.0 * 1.5 = 15.0 → clamped to 10.0
        assert components['topology'] == 10.0

    def test_clamp_at_0(self):
        """Zero coefficient should clamp at 0.0."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({'topology': 0.0})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        assert components['topology'] == 0.0

    def test_negative_coefficient_clamps_at_0(self):
        """Negative coefficient (should never happen, but defensive)."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({'topology': -0.5})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # 10.0 * -0.5 = -5.0 → clamped to 0.0
        assert components['topology'] == 0.0

    def test_extreme_boost(self):
        """2.0 coefficient should still clamp at 10.0."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({'topology': 2.0})
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        assert components['topology'] == 10.0


# =============================================================================
# Lab detection
# =============================================================================

class TestLabDetection:

    def test_none_lab_is_ignored(self):
        """_chemistry_lab = None → no modulation."""
        data = _base_output()
        data['_chemistry_lab'] = None
        c = InsightsCompiler(data)
        assert c._lab is None

    def test_string_lab_is_ignored(self):
        """A serialized string should not be treated as a live lab."""
        data = _base_output()
        data['_chemistry_lab'] = 'ChemistryLab(signals=5)'
        c = InsightsCompiler(data)
        assert c._lab is None

    def test_dict_lab_is_ignored(self):
        """A dict (serialized result) is not a live lab object."""
        data = _base_output()
        data['_chemistry_lab'] = {'modulations': [], 'syndromes': []}
        c = InsightsCompiler(data)
        assert c._lab is None

    def test_mock_lab_is_accepted(self):
        """Our mock with get_modulation() should be recognized."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({})
        c = InsightsCompiler(data)
        assert c._lab is not None


# =============================================================================
# Multiple modulations on same target
# =============================================================================

class TestMultipleModulations:

    def test_two_modulations_on_same_target_multiply(self):
        """Two modulations on topology should multiply: 0.8 * 0.9 = 0.72."""
        lab = MockChemistryLab({})
        # Manually add two modulations for same target
        lab.modulations = [
            MockModulation('topology', 0.8),
            MockModulation('topology', 0.9),
        ]
        data = _base_output()
        data['_chemistry_lab'] = lab
        c = InsightsCompiler(data)
        components = c._compute_health_components()
        # 10.0 * 0.8 * 0.9 = 7.2
        assert abs(components['topology'] - 7.2) < 0.01


# =============================================================================
# End-to-end: modulation affects grade
# =============================================================================

class TestModulationAffectsGrade:

    def test_severe_penalty_drops_grade(self):
        """Heavy penalties on high-weight components should drop grade."""
        data = _base_output()
        data['_chemistry_lab'] = MockChemistryLab({
            'topology': 0.5,     # 20% weight: 10 → 5.0
            'constraints': 0.5,  # 20% weight: 10 → 5.0
        })
        c = InsightsCompiler(data)
        report = c.compile()
        # Without modulation: ~9.0+ (A)
        # With modulation: ~7.0-7.5 (B)
        assert report.grade in ('B', 'C'), f"Expected B or C, got {report.grade}"

    def test_no_modulation_stays_high(self):
        """Baseline without modulation should be A."""
        data = _base_output()
        c = InsightsCompiler(data)
        report = c.compile()
        assert report.grade == 'A'
