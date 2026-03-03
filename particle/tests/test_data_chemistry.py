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
