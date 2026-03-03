"""Tests for the Data Chemistry Layer -- cross-signal correlation engine.

Tests cover:
  - Signal extraction helpers
  - Syndrome detectors (flying_blind, hollow_architecture, etc.)
  - Contradiction detection
  - Modulation generation
  - ChemistryResult (to_dict, get_modulation)
  - ChemistryLab stateful service (feed/ingest/query lifecycle)
  - Graceful degradation (missing signals)
  - compute_chemistry() functional API
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from data_chemistry import (
    NEUTRAL,
    UNKNOWN,
    SYNDROME_THRESHOLD,
    EXPECTED_SIGNAL_COUNT,
    Modulation,
    Syndrome,
    Contradiction,
    NodeConvergence,
    ConvergenceResult,
    ChemistryResult,
    ChemistryLab,
    compute_chemistry,
    _extract_noise_ratio,
    _extract_classification_coverage,
    _extract_edge_diversity,
    _extract_boundary_ratio,
    _extract_dependency_count,
    _extract_ecosystem_unknowns,
    _extract_roadmap_readiness,
    _extract_advisory_counts,
    _extract_file_concentration,
    _extract_domain_clarity,
    _extract_ideome_coherence,
    _extract_dead_code_pct,
    _extract_knot_score,
    _extract_ci,
    _detect_flying_blind,
    _detect_hollow_architecture,
    _detect_dependency_sprawl,
    _detect_purpose_vacuum,
    _detect_advisory_storm,
    _detect_contradictions,
    _generate_modulations,
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_full_output(**overrides) -> dict:
    """Build a minimal full_output dict with sensible defaults."""
    base = {
        'smart_ignore': {'noise_ratio': 0.1, 'total_files': 100, 'ignored_count': 10},
        'classification': {'classified': 90, 'unclassified': 10},
        'edge_types': {'import': 60, 'call': 30, 'inherit': 10},
        'codome_boundaries': {'total_boundaries': 5},
        'kpis': {
            'nodes_total': 100,
            'dead_code_percent': 3,
            'knot_score': 1.5,
            'codebase_intelligence': 0.75,
        },
        'dependencies': {'dependencies': [f'dep-{i}' for i in range(10)]},
        'ecosystem_discovery': {'total_unknowns': 2},
        'roadmap': {'readiness_score': 70},
        'warnings': ['w1', 'w2'],
        'recommendations': ['r1'],
        'files': {
            'a.py': {'atom_count': 10},
            'b.py': {'atom_count': 12},
            'c.py': {'atom_count': 8},
        },
        'semantics': {'domain_inference': 'web-backend'},
        'ideome': {'global_coherence': 0.82},
        'nodes': [{'id': f'n{i}'} for i in range(100)],
    }
    base.update(overrides)
    return base


def _make_distressed_output() -> dict:
    """Build a full_output that triggers multiple syndromes."""
    return _make_full_output(
        smart_ignore={'noise_ratio': 0.55, 'total_files': 200, 'ignored_count': 110},
        classification={'classified': 30, 'unclassified': 70},
        codome_boundaries={'total_boundaries': 50},
        kpis={
            'nodes_total': 100,
            'dead_code_percent': 25,
            'knot_score': 7.0,
            'codebase_intelligence': 0.35,
        },
        dependencies={'dependencies': [f'd{i}' for i in range(120)]},
        ecosystem_discovery={'total_unknowns': 40},
        roadmap={'readiness_score': 25},
        warnings=[f'w{i}' for i in range(12)],
        recommendations=[f'r{i}' for i in range(10)],
        semantics={'domain_inference': None},
        ideome={'global_coherence': 0.25},
    )


# ── Signal extraction tests ─────────────────────────────────────────────


class TestExtractNoiseRatio:
    def test_direct_ratio(self):
        out = {'smart_ignore': {'noise_ratio': 0.42}}
        assert _extract_noise_ratio(out) == pytest.approx(0.42)

    def test_computed_ratio(self):
        out = {'smart_ignore': {'total_files': 200, 'ignored_count': 60}}
        assert _extract_noise_ratio(out) == pytest.approx(0.30)

    def test_from_ignored_paths(self):
        out = {'smart_ignore': {'total_files': 100, 'ignored_paths': ['a', 'b', 'c']}}
        assert _extract_noise_ratio(out) == pytest.approx(0.03)

    def test_empty_returns_none(self):
        assert _extract_noise_ratio({}) is None
        assert _extract_noise_ratio({'smart_ignore': {}}) is None


class TestExtractClassificationCoverage:
    def test_normal(self):
        out = {'classification': {'classified': 80, 'unclassified': 20}}
        assert _extract_classification_coverage(out) == pytest.approx(0.80)

    def test_perfect(self):
        out = {'classification': {'classified': 50, 'unclassified': 0}}
        assert _extract_classification_coverage(out) == pytest.approx(1.0)

    def test_zero_total_returns_none(self):
        out = {'classification': {'classified': 0, 'unclassified': 0}}
        assert _extract_classification_coverage(out) is None

    def test_missing_returns_none(self):
        assert _extract_classification_coverage({}) is None


class TestExtractEdgeDiversity:
    def test_normal(self):
        out = {'edge_types': {'import': 60, 'call': 30, 'inherit': 10}}
        result = _extract_edge_diversity(out)
        assert result is not None
        type_count, dominant_pct = result
        assert type_count == 3
        assert dominant_pct == pytest.approx(0.60)

    def test_single_type(self):
        out = {'edge_types': {'import': 100}}
        result = _extract_edge_diversity(out)
        assert result[0] == 1
        assert result[1] == pytest.approx(1.0)

    def test_empty_returns_none(self):
        assert _extract_edge_diversity({}) is None
        assert _extract_edge_diversity({'edge_types': {}}) is None


class TestExtractBoundaryRatio:
    def test_from_total_boundaries(self):
        out = {
            'codome_boundaries': {'total_boundaries': 20},
            'kpis': {'nodes_total': 100},
        }
        assert _extract_boundary_ratio(out) == pytest.approx(0.20)

    def test_from_boundary_nodes(self):
        out = {
            'codome_boundaries': {'boundary_nodes': ['a', 'b', 'c']},
            'kpis': {'nodes_total': 50},
        }
        assert _extract_boundary_ratio(out) == pytest.approx(0.06)

    def test_missing_returns_none(self):
        assert _extract_boundary_ratio({}) is None


class TestExtractDependencyCount:
    def test_list_format(self):
        out = {'dependencies': ['a', 'b', 'c']}
        assert _extract_dependency_count(out) == 3

    def test_dict_with_items(self):
        out = {'dependencies': {'dependencies': ['x', 'y']}}
        assert _extract_dependency_count(out) == 2

    def test_missing_returns_none(self):
        assert _extract_dependency_count({}) is None


class TestExtractAdvisoryCounts:
    def test_normal(self):
        out = {'warnings': ['a', 'b'], 'recommendations': ['c']}
        assert _extract_advisory_counts(out) == (2, 1)

    def test_missing(self):
        assert _extract_advisory_counts({}) == (0, 0)


class TestExtractDeadCodePct:
    def test_present(self):
        out = {'kpis': {'dead_code_percent': 12.5}}
        assert _extract_dead_code_pct(out) == pytest.approx(12.5)

    def test_missing_returns_zero(self):
        assert _extract_dead_code_pct({}) == 0.0
        assert _extract_dead_code_pct({'kpis': {}}) == 0.0


class TestExtractCI:
    def test_present(self):
        out = {'kpis': {'codebase_intelligence': 0.88}}
        assert _extract_ci(out) == pytest.approx(0.88)

    def test_missing_returns_zero(self):
        assert _extract_ci({}) == 0.0


# ── Syndrome detector tests ─────────────────────────────────────────────


class TestDetectFlyingBlind:
    def test_all_three_triggers(self):
        signals = {
            'noise_ratio': 0.5,
            'classification_coverage': 0.4,
            'boundary_ratio': 0.5,
        }
        syn = _detect_flying_blind(signals)
        assert syn is not None
        assert syn.name == 'flying_blind'
        assert syn.severity > 0.3

    def test_two_triggers_sufficient(self):
        signals = {'noise_ratio': 0.6, 'classification_coverage': 0.3}
        syn = _detect_flying_blind(signals)
        assert syn is not None

    def test_one_trigger_not_enough(self):
        signals = {'noise_ratio': 0.8}
        assert _detect_flying_blind(signals) is None

    def test_all_healthy_returns_none(self):
        signals = {
            'noise_ratio': 0.05,
            'classification_coverage': 0.95,
            'boundary_ratio': 0.05,
        }
        assert _detect_flying_blind(signals) is None

    def test_empty_returns_none(self):
        assert _detect_flying_blind({}) is None


class TestDetectHollowArchitecture:
    def test_classic_hollow(self):
        signals = {
            'dead_code_pct': 30,
            'knot_score': 6,
            'codebase_intelligence': 0.3,
        }
        syn = _detect_hollow_architecture(signals)
        assert syn is not None
        assert syn.name == 'hollow_architecture'

    def test_low_dead_code_no_syndrome(self):
        signals = {'dead_code_pct': 5, 'knot_score': 6, 'codebase_intelligence': 0.3}
        assert _detect_hollow_architecture(signals) is None

    def test_high_ci_no_syndrome(self):
        signals = {'dead_code_pct': 30, 'knot_score': 6, 'codebase_intelligence': 0.85}
        assert _detect_hollow_architecture(signals) is None


class TestDetectDependencySprawl:
    def test_heavy_deps_with_unknowns(self):
        signals = {
            'dependency_count': 120,
            'ecosystem_unknowns': 30,
            'edge_diversity': (2, 0.9),
        }
        syn = _detect_dependency_sprawl(signals)
        assert syn is not None
        assert syn.name == 'dependency_sprawl'

    def test_few_deps_no_syndrome(self):
        signals = {'dependency_count': 10, 'ecosystem_unknowns': 0}
        assert _detect_dependency_sprawl(signals) is None

    def test_threshold_30_deps(self):
        signals = {'dependency_count': 29}
        assert _detect_dependency_sprawl(signals) is None


class TestDetectPurposeVacuum:
    def test_classic_vacuum(self):
        signals = {
            'codebase_intelligence': 0.2,
            'domain_clarity': None,
            'roadmap_readiness': 20,
            'classification_coverage': 0.3,
        }
        syn = _detect_purpose_vacuum(signals)
        assert syn is not None
        assert syn.name == 'purpose_vacuum'

    def test_high_ci_blocks(self):
        signals = {
            'codebase_intelligence': 0.85,
            'domain_clarity': None,
            'roadmap_readiness': 20,
        }
        assert _detect_purpose_vacuum(signals) is None

    def test_unknown_domain_contributes(self):
        signals = {
            'codebase_intelligence': 0.4,
            'domain_clarity': 'Unknown',
        }
        syn = _detect_purpose_vacuum(signals)
        assert syn is not None


class TestDetectAdvisoryStorm:
    def test_storm_threshold(self):
        signals = {'advisory_counts': (10, 8)}
        syn = _detect_advisory_storm(signals)
        assert syn is not None
        assert syn.name == 'advisory_storm'

    def test_below_threshold(self):
        signals = {'advisory_counts': (5, 5)}
        assert _detect_advisory_storm(signals) is None

    def test_severity_scales(self):
        signals_low = {'advisory_counts': (8, 8)}
        signals_high = {'advisory_counts': (30, 30)}
        low = _detect_advisory_storm(signals_low)
        high = _detect_advisory_storm(signals_high)
        assert low.severity < high.severity


# ── Contradiction tests ──────────────────────────────────────────────────


class TestDetectContradictions:
    def test_high_ci_low_classification(self):
        signals = {'codebase_intelligence': 0.9, 'classification_coverage': 0.3}
        result = _detect_contradictions(signals)
        assert len(result) == 1
        assert result[0].signal_a == 'codebase_intelligence'
        assert result[0].tension > 0

    def test_good_ideome_high_noise(self):
        signals = {'ideome_coherence': 0.85, 'noise_ratio': 0.5}
        result = _detect_contradictions(signals)
        assert len(result) == 1
        assert result[0].signal_a == 'ideome_coherence'

    def test_low_dead_high_knot(self):
        signals = {'dead_code_pct': 2, 'knot_score': 8}
        result = _detect_contradictions(signals)
        assert len(result) == 1
        assert result[0].signal_b == 'knot_score'

    def test_many_deps_few_edge_types(self):
        signals = {'dependency_count': 80, 'edge_diversity': (1, 1.0)}
        result = _detect_contradictions(signals)
        assert len(result) == 1
        assert result[0].signal_b == 'edge_type_count'

    def test_no_contradictions_healthy(self):
        signals = {
            'codebase_intelligence': 0.5,
            'classification_coverage': 0.8,
            'noise_ratio': 0.1,
            'dead_code_pct': 10,
            'knot_score': 2,
        }
        result = _detect_contradictions(signals)
        assert result == []


# ── Modulation generation tests ──────────────────────────────────────────


class TestGenerateModulations:
    def test_high_noise_penalises_topology(self):
        signals = {'noise_ratio': 0.6}
        mods = _generate_modulations(signals, [])
        targets = [m.target for m in mods]
        assert 'topology' in targets
        topo_mod = next(m for m in mods if m.target == 'topology')
        assert topo_mod.coefficient < 1.0

    def test_low_classification_penalises_purpose(self):
        signals = {'classification_coverage': 0.4}
        mods = _generate_modulations(signals, [])
        targets = [m.target for m in mods]
        assert 'purpose' in targets

    def test_unknown_domain_adds_purpose_and_i_telic(self):
        signals = {'domain_clarity': None}
        mods = _generate_modulations(signals, [])
        targets = [m.target for m in mods]
        assert 'purpose' in targets
        assert 'i_telic' in targets

    def test_flying_blind_syndrome_modulates_three_targets(self):
        syn = Syndrome(name='flying_blind', severity=0.6, signals={})
        mods = _generate_modulations({}, [syn])
        targets = [m.target for m in mods]
        assert 'topology' in targets
        assert 'purpose' in targets
        assert 'constraints' in targets

    def test_coefficients_clamped(self):
        """All coefficients must stay above minimum floor."""
        signals = {
            'noise_ratio': 0.99,
            'classification_coverage': 0.01,
            'boundary_ratio': 0.95,
            'domain_clarity': None,
        }
        mods = _generate_modulations(signals, [])
        for m in mods:
            assert m.coefficient >= 0.70, f'{m.target} coefficient too low: {m.coefficient}'
            assert m.coefficient <= 1.5, f'{m.target} coefficient too high: {m.coefficient}'

    def test_no_signals_produces_domain_modulations(self):
        """Empty signals still trigger domain_clarity/roadmap modulations (None = unknown)."""
        mods = _generate_modulations({}, [])
        # Domain clarity None → purpose penalty; roadmap None → purpose_fulfillment penalty
        targets = {m.target for m in mods}
        assert 'purpose' in targets or 'purpose_fulfillment' in targets


# ── ChemistryResult tests ───────────────────────────────────────────────


class TestChemistryResult:
    def test_get_modulation_neutral(self):
        result = ChemistryResult()
        assert result.get_modulation('anything') == NEUTRAL

    def test_get_modulation_single(self):
        m = Modulation(target='topology', coefficient=0.85, reason='test')
        result = ChemistryResult(modulations=[m])
        assert result.get_modulation('topology') == pytest.approx(0.85)
        assert result.get_modulation('other') == NEUTRAL

    def test_get_modulation_multiple_multiply(self):
        m1 = Modulation(target='topology', coefficient=0.9, reason='a')
        m2 = Modulation(target='topology', coefficient=0.8, reason='b')
        result = ChemistryResult(modulations=[m1, m2])
        assert result.get_modulation('topology') == pytest.approx(0.72)

    def test_to_dict_structure(self):
        m = Modulation(target='topology', coefficient=0.9, reason='test')
        s = Syndrome(name='flying_blind', severity=0.5)
        c = Contradiction(signal_a='a', signal_b='b', tension=0.3)
        result = ChemistryResult(
            modulations=[m],
            syndromes=[s],
            contradictions=[c],
            compound_severity=0.5,
            signal_coverage=0.8,
        )
        d = result.to_dict()
        assert 'modulations' in d
        assert 'syndromes' in d
        assert 'contradictions' in d
        assert 'modulations_by_target' in d
        assert d['modulations_by_target']['topology'] == pytest.approx(0.9)

    def test_to_dict_merges_same_target(self):
        m1 = Modulation(target='t', coefficient=0.9, reason='a')
        m2 = Modulation(target='t', coefficient=0.8, reason='b')
        result = ChemistryResult(modulations=[m1, m2])
        d = result.to_dict()
        assert d['modulations_by_target']['t'] == pytest.approx(0.72)


# ── ChemistryLab tests ──────────────────────────────────────────────────


class TestChemistryLabFeedQuery:
    """Test the feed/query lifecycle and lazy evaluation."""

    def test_empty_lab_returns_neutral_for_topology(self):
        """Empty lab: no noise signal → topology unaffected, but purpose_vacuum fires."""
        lab = ChemistryLab()
        assert lab.get_modulation('topology') == NEUTRAL
        # Empty state triggers purpose_vacuum (CI=0, domain=None, roadmap=None)
        assert any(s.name == 'purpose_vacuum' for s in lab.syndromes)
        assert lab.compound_severity > 0.0

    def test_feed_single_signal(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.6)
        coeff = lab.get_modulation('topology')
        assert coeff < 1.0  # high noise penalises topology

    def test_feed_many(self):
        lab = ChemistryLab()
        lab.feed_many({'noise_ratio': 0.5, 'classification_coverage': 0.3})
        # Should detect flying_blind (2 of 3 triggers)
        assert len(lab.syndromes) > 0

    def test_feed_overwrites_signal(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.8)
        coeff_high_noise = lab.get_modulation('topology')
        lab.feed('noise_ratio', 0.05)
        coeff_low_noise = lab.get_modulation('topology')
        assert coeff_low_noise > coeff_high_noise

    def test_lazy_evaluation_caches(self):
        """Second query without new feed should not recompute."""
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.6)
        r1 = lab.get_result()
        r2 = lab.get_result()
        # Same object (no recomputation)
        assert r1 is r2

    def test_feed_invalidates_cache(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.6)
        r1 = lab.get_result()
        lab.feed('classification_coverage', 0.3)
        r2 = lab.get_result()
        assert r1 is not r2  # new result after feed

    def test_signals_property(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.42)
        lab.feed('knot_score', 3.0)
        s = lab.signals
        assert s['noise_ratio'] == 0.42
        assert s['knot_score'] == 3.0
        # Should be a copy
        s['extra'] = True
        assert 'extra' not in lab.signals


class TestChemistryLabIngest:
    """Test bulk ingestion from full_output."""

    def test_ingest_healthy(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        # Healthy codebase -- no harsh penalties
        assert lab.compound_severity < 0.3
        assert lab.signal_coverage > 0.5

    def test_ingest_distressed(self):
        lab = ChemistryLab()
        lab.ingest(_make_distressed_output())
        # Distressed codebase -- syndromes expected
        assert lab.compound_severity > 0.0
        assert len(lab.syndromes) >= 2

    def test_ingest_extracts_all_known_signals(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        s = lab.signals
        # Should have all INGEST_EXTRACTORS + ALWAYS_EXTRACTORS + advisory_counts
        assert 'noise_ratio' in s
        assert 'classification_coverage' in s
        assert 'dead_code_pct' in s
        assert 'codebase_intelligence' in s
        assert 'advisory_counts' in s
        assert 'ideome_coherence' in s
        assert 'domain_clarity' in s

    def test_ingest_then_feed_overwrites(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        original_noise = lab.signals.get('noise_ratio')
        lab.feed('noise_ratio', 0.99)
        assert lab.signals['noise_ratio'] == 0.99

    def test_ingest_empty_output(self):
        lab = ChemistryLab()
        lab.ingest({})
        # Should not crash; sparse signals trigger purpose_vacuum (CI=0, domain=None)
        assert lab.compound_severity > 0.0
        assert lab.signal_coverage >= 0.0

    def test_get_result_to_dict(self):
        lab = ChemistryLab()
        lab.ingest(_make_full_output())
        d = lab.get_result().to_dict()
        assert 'modulations' in d
        assert 'syndromes' in d
        assert 'contradictions' in d
        assert 'modulations_by_target' in d


class TestChemistryLabModulationTargets:
    """Test that specific targets get proper modulations."""

    def test_topology_modulated_by_noise(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.5)
        assert lab.get_modulation('topology') < 1.0

    def test_purpose_modulated_by_classification(self):
        lab = ChemistryLab()
        lab.feed('classification_coverage', 0.3)
        assert lab.get_modulation('purpose') < 1.0

    def test_constraints_modulated_by_boundary(self):
        lab = ChemistryLab()
        lab.feed('boundary_ratio', 0.5)
        assert lab.get_modulation('constraints') < 1.0

    def test_i_sym_modulated_by_ideome(self):
        lab = ChemistryLab()
        lab.feed('ideome_coherence', 0.2)
        assert lab.get_modulation('i_sym') < 1.0

    def test_i_telic_modulated_by_domain(self):
        lab = ChemistryLab()
        lab.feed('domain_clarity', None)
        assert lab.get_modulation('i_telic') < 1.0

    def test_unknown_target_neutral(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.8)
        assert lab.get_modulation('totally_made_up') == NEUTRAL


class TestChemistryLabSyndromes:
    """Test that syndromes are detected through the lab interface."""

    def test_flying_blind_via_lab(self):
        lab = ChemistryLab()
        lab.feed_many({
            'noise_ratio': 0.55,
            'classification_coverage': 0.3,
            'boundary_ratio': 0.5,
        })
        names = [s.name for s in lab.syndromes]
        assert 'flying_blind' in names

    def test_advisory_storm_via_lab(self):
        lab = ChemistryLab()
        lab.feed('advisory_counts', (12, 10))
        names = [s.name for s in lab.syndromes]
        assert 'advisory_storm' in names

    def test_compound_severity_increases_with_syndromes(self):
        lab = ChemistryLab()
        lab.feed_many({
            'noise_ratio': 0.6,
            'classification_coverage': 0.2,
            'boundary_ratio': 0.5,
            'advisory_counts': (15, 10),
        })
        # Should have flying_blind + advisory_storm
        assert lab.compound_severity > 0.0
        assert len(lab.syndromes) >= 2


# ── compute_chemistry() functional API tests ─────────────────────────────


class TestComputeChemistry:
    """Test the standalone compute_chemistry() function."""

    def test_healthy_codebase(self):
        result = compute_chemistry(_make_full_output())
        assert isinstance(result, ChemistryResult)
        assert result.compound_severity < 0.3
        assert result.signal_coverage > 0.5

    def test_distressed_codebase(self):
        result = compute_chemistry(_make_distressed_output())
        assert result.compound_severity > 0.0
        assert len(result.syndromes) >= 2
        assert len(result.modulations) > 0

    def test_empty_output(self):
        result = compute_chemistry({})
        assert isinstance(result, ChemistryResult)
        assert result.modulations == [] or all(m.coefficient <= 1.0 for m in result.modulations)

    def test_to_dict_round_trip(self):
        result = compute_chemistry(_make_full_output())
        d = result.to_dict()
        assert isinstance(d, dict)
        assert isinstance(d['modulations_by_target'], dict)

    def test_coverage_reflects_signals(self):
        full = _make_full_output()
        result = compute_chemistry(full)
        assert result.signal_coverage > 0.7  # most signals present

        sparse = {'kpis': {}}
        result_sparse = compute_chemistry(sparse)
        assert result_sparse.signal_coverage < result.signal_coverage


# ── Graceful degradation tests ───────────────────────────────────────────


class TestGracefulDegradation:
    """Verify the system handles missing/partial data gracefully."""

    def test_no_smart_ignore(self):
        out = _make_full_output(smart_ignore={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_no_classification(self):
        out = _make_full_output(classification={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_no_edge_types(self):
        out = _make_full_output(edge_types={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_no_dependencies(self):
        out = _make_full_output(dependencies={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_no_ideome(self):
        out = _make_full_output(ideome={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_no_kpis(self):
        out = _make_full_output(kpis={})
        result = compute_chemistry(out)
        assert isinstance(result, ChemistryResult)

    def test_lab_ingest_partial(self):
        lab = ChemistryLab()
        lab.ingest({'kpis': {'codebase_intelligence': 0.5}})
        # Should work fine with minimal data
        assert lab.get_modulation('topology') >= 0.0
        assert isinstance(lab.get_result(), ChemistryResult)


# ── Repr test ────────────────────────────────────────────────────────────


class TestRepr:
    def test_lab_repr_dirty(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.5)
        r = repr(lab)
        assert 'ChemistryLab' in r
        assert 'dirty' in r

    def test_lab_repr_computed(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.5)
        _ = lab.get_result()
        r = repr(lab)
        assert 'computed' in r


# ── Node-Level Convergence Tests ────────────────────────────────────────


def _make_rich_nodes(specs):
    """Create node dicts with convergence-relevant fields.

    Each spec is a dict with any of: confidence, docstring, intent,
    layer, is_god_class, Q_total, coherence_score, cyclomatic_complexity,
    out_degree.  Missing fields default to healthy values.
    """
    nodes = []
    for i, spec in enumerate(specs):
        node = {
            'id': spec.get('id', f'test::Node{i}'),
            'name': spec.get('name', f'Node{i}'),
            'file_path': spec.get('file_path', f'src/mod{i}.py'),
            'confidence': spec.get('confidence', 0.9),
            'docstring': spec.get('docstring', 'A docstring.'),
            'intent': spec.get('intent', 'Explicit'),
            'intent_profile': {'has_docstring': bool(spec.get('docstring', True))},
            'layer': spec.get('layer', 'Domain'),
            'is_god_class': spec.get('is_god_class', False),
            'purpose_intelligence': {'Q_total': spec.get('Q_total', 0.8)},
            'coherence_score': spec.get('coherence_score', 0.9),
            'cyclomatic_complexity': spec.get('cyclomatic_complexity', 5),
            'out_degree': spec.get('out_degree', 3),
        }
        nodes.append(node)
    return nodes


class TestNodeConvergence:
    """Tests for analyze_node_convergence()."""

    def test_no_nodes(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.1)
        result = lab.analyze_node_convergence()
        assert result.total_nodes == 0
        assert result.convergent_count == 0

    def test_healthy_nodes_no_convergence(self):
        nodes = _make_rich_nodes([{}, {}, {}])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.total_nodes == 3
        assert conv.convergent_count == 0
        assert conv.critical_count == 0

    def test_moderate_severity_3_signals(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.3, 'docstring': None, 'layer': 'Unknown'},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.convergent_count == 1
        assert conv.convergent_nodes[0].severity == 'moderate'
        assert conv.convergent_nodes[0].signal_count == 3
        signals = conv.convergent_nodes[0].signals
        assert 'low_confidence' in signals
        assert 'no_docstring' in signals
        assert 'unknown_layer' in signals

    def test_high_severity_4_signals(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.2, 'docstring': None, 'layer': 'Unknown',
             'is_god_class': True},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.convergent_nodes[0].severity == 'high'
        assert conv.convergent_nodes[0].signal_count == 4

    def test_critical_severity_5_plus_signals(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.2, 'docstring': None, 'intent': 'Implicit',
             'layer': 'Unknown', 'is_god_class': True, 'Q_total': 0.1,
             'coherence_score': 0.1, 'cyclomatic_complexity': 20},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.convergent_nodes[0].severity == 'critical'
        assert conv.convergent_nodes[0].signal_count == 8  # all 8 fire
        assert conv.critical_count == 1

    def test_sorted_by_signal_count(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.3, 'docstring': None, 'layer': 'Unknown'},  # 3
            {'confidence': 0.2, 'docstring': None, 'layer': 'Unknown',
             'is_god_class': True, 'Q_total': 0.1},                      # 5
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.convergent_count == 2
        assert conv.convergent_nodes[0].signal_count >= conv.convergent_nodes[1].signal_count

    def test_signal_distribution(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.3, 'docstring': None, 'layer': 'Unknown'},
            {'confidence': 0.2, 'docstring': None, 'layer': 'Unknown'},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        conv = lab.analyze_node_convergence()
        assert conv.signal_distribution.get('low_confidence', 0) == 2
        assert conv.signal_distribution.get('no_docstring', 0) == 2
        assert conv.signal_distribution.get('unknown_layer', 0) == 2

    def test_convergence_in_result(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.3, 'docstring': None, 'layer': 'Unknown'},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        r = lab.get_result()
        assert r.convergence is not None
        assert r.convergence.convergent_count == 1

    def test_convergence_to_dict(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.3, 'docstring': None, 'layer': 'Unknown'},
        ])
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        d = lab.get_result().to_dict()
        assert 'convergence' in d
        assert d['convergence']['convergent_count'] == 1
        assert len(d['convergence']['convergent_nodes']) == 1


# ── AI Consumer Summary Tests ───────────────────────────────────────────


class TestAIConsumerSummary:
    """Tests for build_ai_consumer_summary()."""

    def test_summary_structure(self):
        out = _make_full_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        assert 'headline' in s
        assert 'data_utility_grade' in s
        assert 'key_contradictions' in s
        assert 'convergent_concerns' in s
        assert 'blind_spots' in s
        assert 'actionable_next' in s
        assert 'meta' in s
        assert s['meta']['chemistry_version'] == '1.1.0'

    def test_grade_a_for_clean_system(self):
        out = _make_full_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        # Healthy defaults: few/no syndromes, low severity
        assert s['data_utility_grade'] in ('A', 'B')

    def test_grade_degrades_with_syndromes(self):
        out = _make_distressed_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        # Distressed system triggers syndromes => worse grade
        assert s['data_utility_grade'] in ('C', 'D', 'F')

    def test_headline_mentions_syndromes(self):
        out = _make_distressed_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        assert 'syndrome' in s['headline'].lower() or 'detected' in s['headline'].lower()

    def test_headline_clean_system(self):
        out = _make_full_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        # May or may not have anomalies depending on defaults
        assert isinstance(s['headline'], str)
        assert len(s['headline']) > 10

    def test_blind_spots_from_missing_signals(self):
        lab = ChemistryLab()
        lab.feed('noise_ratio', 0.1)  # only one signal
        s = lab.build_ai_consumer_summary()
        # Most expected signals are missing => blind spots populated
        assert len(s['blind_spots']) > 5

    def test_actionable_next_capped_at_5(self):
        out = _make_distressed_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        assert len(s['actionable_next']) <= 5

    def test_convergent_concerns_with_rich_nodes(self):
        nodes = _make_rich_nodes([
            {'confidence': 0.2, 'docstring': None, 'intent': 'Implicit',
             'layer': 'Unknown', 'is_god_class': True},  # 5 signals = critical
        ] * 3)
        out = _make_full_output(nodes=nodes)
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        cc = s['convergent_concerns']
        assert cc['critical_nodes'] == 3
        assert len(cc['top_entities']) == 3
        assert cc['signal_heatmap'].get('low_confidence', 0) == 3

    def test_meta_counts(self):
        out = _make_distressed_output()
        lab = ChemistryLab()
        lab.ingest(out)
        s = lab.build_ai_consumer_summary()
        m = s['meta']
        assert m['signals_extracted'] > 0
        assert m['syndromes_active'] >= 0
        assert m['contradictions_found'] >= 0


# ── Entity Paths Tests ──────────────────────────────────────────────────


class TestEntityPaths:
    """Tests for _enrich_with_entity_paths()."""

    def test_flying_blind_entities(self):
        nodes = _make_rich_nodes([
            {'id': 'a', 'confidence': 0.3, 'docstring': None},   # qualifies
            {'id': 'b', 'confidence': 0.3, 'docstring': 'OK'},   # low conf only
            {'id': 'c', 'confidence': 0.9, 'docstring': None},   # no doc only
        ])
        out = _make_full_output(
            nodes=nodes,
            smart_ignore={'noise_ratio': 0.55, 'total_files': 100, 'ignored_count': 55},
            classification={'classified': 30, 'unclassified': 70},
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.35,
                  'dead_code_percent': 3, 'knot_score': 1.5},
        )
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        flying = [s for s in result.syndromes if s.name == 'flying_blind']
        if flying:
            # Only 'a' has BOTH low confidence AND no docstring
            assert 'a' in flying[0].affected_entities
            assert 'b' not in flying[0].affected_entities
            assert 'c' not in flying[0].affected_entities

    def test_hollow_architecture_entities(self):
        nodes = _make_rich_nodes([
            {'id': 'x', 'layer': 'Unknown'},
            {'id': 'y', 'is_god_class': True},
            {'id': 'z', 'layer': 'Domain'},
        ])
        out = _make_full_output(
            nodes=nodes,
            classification={'classified': 30, 'unclassified': 70},
        )
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        hollow = [s for s in result.syndromes if s.name == 'hollow_architecture']
        if hollow:
            ents = hollow[0].affected_entities
            assert 'x' in ents
            assert 'y' in ents
            assert 'z' not in ents

    def test_purpose_vacuum_entities(self):
        nodes = _make_rich_nodes([
            {'id': 'p1', 'Q_total': 0.1},
            {'id': 'p2', 'Q_total': 0.8},
        ])
        out = _make_full_output(
            nodes=nodes,
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.35,
                  'dead_code_percent': 3, 'knot_score': 1.5},
            semantics={'domain_inference': None},
            ideome={'global_coherence': 0.2},
        )
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        vacuum = [s for s in result.syndromes if s.name == 'purpose_vacuum']
        if vacuum:
            assert 'p1' in vacuum[0].affected_entities
            assert 'p2' not in vacuum[0].affected_entities

    def test_entity_cap_at_20(self):
        # 50 nodes all qualifying for flying_blind
        nodes = _make_rich_nodes([
            {'id': f'n{i}', 'confidence': 0.1, 'docstring': None}
            for i in range(50)
        ])
        out = _make_full_output(
            nodes=nodes,
            smart_ignore={'noise_ratio': 0.6, 'total_files': 100, 'ignored_count': 60},
            classification={'classified': 30, 'unclassified': 70},
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.35,
                  'dead_code_percent': 3, 'knot_score': 1.5},
        )
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        flying = [s for s in result.syndromes if s.name == 'flying_blind']
        if flying:
            assert len(flying[0].affected_entities) <= 20

    def test_no_entities_without_nodes(self):
        out = _make_full_output(nodes=[])
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        for syn in result.syndromes:
            assert syn.affected_entities == []
        for cont in result.contradictions:
            assert cont.affected_entities == []

    def test_contradiction_entities(self):
        # High CI + unknown layer => contradiction entity linking
        nodes = _make_rich_nodes([
            {'id': 'hc1', 'confidence': 0.95, 'layer': 'Unknown'},
            {'id': 'hc2', 'confidence': 0.95, 'layer': 'Domain'},
        ])
        out = _make_full_output(
            nodes=nodes,
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.85,
                  'dead_code_percent': 3, 'knot_score': 1.5},
            classification={'classified': 30, 'unclassified': 70},
        )
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        ci_class = [c for c in result.contradictions
                    if c.signal_a == 'codebase_intelligence'
                    and c.signal_b == 'classification_coverage']
        if ci_class:
            assert 'hc1' in ci_class[0].affected_entities
            assert 'hc2' not in ci_class[0].affected_entities


# ── Resolution Hints Tests ──────────────────────────────────────────────


class TestResolutionHints:
    """Tests for contradiction resolution_hint strings."""

    def _get_contradictions(self, **kw):
        out = _make_full_output(**kw)
        lab = ChemistryLab()
        lab.ingest(out)
        return lab.get_result().contradictions

    def test_ci_vs_classification_hint(self):
        contras = self._get_contradictions(
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.9,
                  'dead_code_percent': 3, 'knot_score': 1.5},
            classification={'classified': 30, 'unclassified': 70},
        )
        ci_class = [c for c in contras
                    if c.signal_a == 'codebase_intelligence'
                    and c.signal_b == 'classification_coverage']
        if ci_class:
            assert 'Layer classification' in ci_class[0].resolution_hint

    def test_ideome_vs_noise_hint(self):
        contras = self._get_contradictions(
            ideome={'global_coherence': 0.85},
            smart_ignore={'noise_ratio': 0.55, 'total_files': 200, 'ignored_count': 110},
        )
        ide_noise = [c for c in contras
                     if c.signal_a == 'ideome_coherence'
                     and c.signal_b == 'noise_ratio']
        if ide_noise:
            assert 'tooling config' in ide_noise[0].resolution_hint.lower() or \
                   'Advisory noise' in ide_noise[0].resolution_hint

    def test_dead_code_vs_knot_hint(self):
        contras = self._get_contradictions(
            kpis={'nodes_total': 100, 'codebase_intelligence': 0.75,
                  'dead_code_percent': 1, 'knot_score': 7.0},
        )
        dc_knot = [c for c in contras
                   if c.signal_a == 'dead_code_pct'
                   and c.signal_b == 'knot_score']
        if dc_knot:
            assert 'shared interfaces' in dc_knot[0].resolution_hint.lower() or \
                   'brittle' in dc_knot[0].resolution_hint.lower()

    def test_deps_vs_edge_types_hint(self):
        contras = self._get_contradictions(
            dependencies={'dependencies': [f'd{i}' for i in range(100)]},
            edge_types={'import': 95, 'call': 3, 'inherit': 2},
        )
        dep_edge = [c for c in contras
                    if c.signal_a == 'dependency_count'
                    and c.signal_b == 'edge_type_count']
        if dep_edge:
            assert 'semantic edges' in dep_edge[0].resolution_hint.lower() or \
                   'variety is low' in dep_edge[0].resolution_hint.lower()

    def test_all_contradictions_have_hints(self):
        out = _make_distressed_output()
        lab = ChemistryLab()
        lab.ingest(out)
        result = lab.get_result()
        for c in result.contradictions:
            assert isinstance(c.resolution_hint, str)
