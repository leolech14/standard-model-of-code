"""
Data Chemistry Layer -- Cross-Signal Correlation Engine

A parallel sibling component to the Collider pipeline.  The pipeline
continuously feeds signals to the lab and retrieves modulation
coefficients, syndromes, and contradiction reports on demand.

Architecture:
    ChemistryLab is a stateful service (not a pipeline stage).  It is
    instantiated once, lives alongside the pipeline, and serves any
    subsystem that needs cross-signal intelligence:

        lab = ChemistryLab()
        lab.ingest(full_output)          # bulk feed
        lab.feed('noise_ratio', 0.42)    # incremental feed

        coeff = lab.get_modulation('topology')   # query
        result = lab.get_result()                # full report

Theory: Individual measurements are solo instruments.  Chemistry
detects when COMBINATIONS of signals indicate a state that no
single signal can express.  Example: high noise + low classification
+ weak boundaries = "flying blind" syndrome, which is worse than
the sum of individual deficiencies.

Output: full_output['chemistry'] = lab.get_result().to_dict()
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NEUTRAL = 1.0        # No modulation
UNKNOWN = 0.5        # Missing data => midpoint
SYNDROME_THRESHOLD = 0.6  # Compound severity above this = active syndrome


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Modulation:
    """A named multiplier applied to a scoring component.

    coefficient: float in (0, +inf). 1.0 = no change. <1 = penalty. >1 = boost.
    reason: human-readable explanation of why this modulation exists.
    signals: dict of raw signal values that contributed.
    """
    target: str          # e.g. 'topology', 'constraints', 'i_struct'
    coefficient: float   # multiplier
    reason: str
    signals: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Syndrome:
    """A compound pattern detected from multiple co-occurring signals.

    name: identifier (e.g. 'flying_blind', 'hollow_architecture')
    severity: float [0,1] -- 0=benign, 1=critical
    signals: dict of contributing signal values
    description: what this syndrome means
    """
    name: str
    severity: float
    signals: Dict[str, Any] = field(default_factory=dict)
    description: str = ''


@dataclass
class Contradiction:
    """Two signals that shouldn't coexist but do.

    signal_a, signal_b: names of conflicting signals
    tension: float [0,1] -- how contradictory they are
    """
    signal_a: str
    signal_b: str
    tension: float
    description: str = ''


@dataclass
class ChemistryResult:
    """Complete output of the data chemistry layer."""
    modulations: List[Modulation] = field(default_factory=list)
    syndromes: List[Syndrome] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)
    compound_severity: float = 0.0   # aggregate syndrome severity [0,1]
    signal_coverage: float = 0.0     # fraction of expected signals present

    def to_dict(self) -> dict:
        d = asdict(self)
        # Index modulations by target for easy lookup
        d['modulations_by_target'] = {}
        for m in self.modulations:
            t = m.target
            if t not in d['modulations_by_target']:
                d['modulations_by_target'][t] = m.coefficient
            else:
                # Multiply if multiple modulations hit same target
                d['modulations_by_target'][t] *= m.coefficient
        return d

    def get_modulation(self, target: str) -> float:
        """Get combined modulation coefficient for a target. 1.0 = neutral."""
        coeff = NEUTRAL
        for m in self.modulations:
            if m.target == target:
                coeff *= m.coefficient
        return coeff


# ---------------------------------------------------------------------------
# Signal extraction helpers
# ---------------------------------------------------------------------------

def _extract_noise_ratio(full_output: dict) -> Optional[float]:
    """Extract noise ratio from smart_ignore."""
    si = full_output.get('smart_ignore', {})
    if not si:
        return None
    ratio = si.get('noise_ratio')
    if ratio is not None:
        return float(ratio)
    total = si.get('total_files', 0)
    ignored = si.get('ignored_count', 0) or len(si.get('ignored_paths', []))
    if total and total > 0:
        return ignored / total
    return None


def _extract_classification_coverage(full_output: dict) -> Optional[float]:
    """Extract classification coverage as fraction [0,1]."""
    cls = full_output.get('classification', {})
    if not cls or not isinstance(cls, dict):
        return None
    classified = cls.get('classified', 0) or 0
    unclassified = cls.get('unclassified', 0) or 0
    total = classified + unclassified
    if total == 0:
        return None
    return classified / total


def _extract_edge_diversity(full_output: dict) -> Optional[Tuple[int, float]]:
    """Extract edge type count and dominant percentage."""
    et = full_output.get('edge_types', {})
    if not et or not isinstance(et, dict):
        return None
    total = sum(v for v in et.values() if isinstance(v, (int, float)))
    if total == 0:
        return None
    type_count = len(et)
    dominant = max(v for v in et.values() if isinstance(v, (int, float)))
    return (type_count, dominant / total)


def _extract_boundary_ratio(full_output: dict) -> Optional[float]:
    """Extract codome boundary ratio (boundary nodes / total nodes)."""
    cb = full_output.get('codome_boundaries', {})
    if not cb:
        return None
    total_boundaries = cb.get('total_boundaries', 0) or len(cb.get('boundary_nodes', []))
    nodes_total = full_output.get('kpis', {}).get('nodes_total', 0) or len(full_output.get('nodes', []))
    if nodes_total == 0:
        return None
    return total_boundaries / nodes_total


def _extract_dependency_count(full_output: dict) -> Optional[int]:
    """Extract project dependency count."""
    deps = full_output.get('dependencies', {})
    if not deps:
        return None
    if isinstance(deps, list):
        return len(deps)
    if isinstance(deps, dict):
        items = deps.get('dependencies', deps.get('items', deps))
        if isinstance(items, (list, dict)):
            return len(items)
    return None


def _extract_ecosystem_unknowns(full_output: dict) -> Optional[int]:
    """Extract unknown ecosystem pattern count."""
    eco = full_output.get('ecosystem_discovery', {})
    if not eco:
        return None
    return eco.get('total_unknowns', 0)


def _extract_roadmap_readiness(full_output: dict) -> Optional[float]:
    """Extract roadmap readiness score [0,100]."""
    rm = full_output.get('roadmap', {})
    if not rm:
        return None
    return rm.get('readiness_score')


def _extract_advisory_counts(full_output: dict) -> Tuple[int, int]:
    """Extract warning and recommendation counts."""
    warnings = full_output.get('warnings', [])
    recs = full_output.get('recommendations', [])
    w = len(warnings) if isinstance(warnings, list) else 0
    r = len(recs) if isinstance(recs, list) else 0
    return (w, r)


def _extract_file_concentration(full_output: dict) -> Optional[float]:
    """Extract file concentration -- ratio of atoms in largest file vs average."""
    files = full_output.get('files', {})
    if not files or not isinstance(files, dict):
        return None
    counts = []
    for fdata in files.values():
        if isinstance(fdata, list):
            counts.append(len(fdata))
        elif isinstance(fdata, dict):
            counts.append(fdata.get('atom_count', 0))
    if not counts:
        return None
    avg = sum(counts) / len(counts)
    if avg == 0:
        return None
    return max(counts) / avg


def _extract_domain_clarity(full_output: dict) -> Optional[str]:
    """Extract semantic domain inference result."""
    sem = full_output.get('semantics', {})
    if not sem or not isinstance(sem, dict):
        return None
    return sem.get('domain_inference')


def _extract_ideome_coherence(full_output: dict) -> Optional[float]:
    """Extract ideome global coherence [0,1]."""
    ideome = full_output.get('ideome', {})
    if not ideome:
        return None
    return ideome.get('global_coherence')


def _extract_dead_code_pct(full_output: dict) -> float:
    """Extract dead code percentage."""
    return float(full_output.get('kpis', {}).get('dead_code_percent', 0) or 0)


def _extract_knot_score(full_output: dict) -> float:
    """Extract entanglement knot score."""
    return float(full_output.get('kpis', {}).get('knot_score', 0) or 0)


def _extract_ci(full_output: dict) -> float:
    """Extract codebase intelligence [0,1]."""
    return float(full_output.get('kpis', {}).get('codebase_intelligence', 0) or 0)


# ---------------------------------------------------------------------------
# Syndrome detectors
# ---------------------------------------------------------------------------

def _detect_flying_blind(signals: dict) -> Optional[Syndrome]:
    """High noise + low classification + weak boundaries = flying blind.

    The analysis is based on incomplete data AND can't classify what it sees
    AND doesn't know where modules begin/end. Each alone is manageable;
    together they mean the analysis is largely guessing.
    """
    noise = signals.get('noise_ratio')
    class_cov = signals.get('classification_coverage')
    boundary = signals.get('boundary_ratio')

    active = 0
    severity_sum = 0.0

    if noise is not None and noise > 0.3:
        active += 1
        severity_sum += min(1.0, noise)

    if class_cov is not None and class_cov < 0.7:
        active += 1
        severity_sum += (1.0 - class_cov)

    if boundary is not None and boundary > 0.3:
        active += 1
        severity_sum += min(1.0, boundary)

    if active < 2:
        return None

    severity = min(1.0, severity_sum / active)
    if severity < 0.3:
        return None

    return Syndrome(
        name='flying_blind',
        severity=round(severity, 4),
        signals={
            'noise_ratio': noise,
            'classification_coverage': class_cov,
            'boundary_ratio': boundary,
        },
        description=(
            'Analysis operating on incomplete data with weak classification '
            'and unclear module boundaries. Scores may be unreliable.'
        ),
    )


def _detect_hollow_architecture(signals: dict) -> Optional[Syndrome]:
    """Good topology shape but high dead code + low test coverage.

    The structure looks organized but the flesh is rotten -- dead code
    accumulates and tests don't cover the living code.
    """
    dead_code = signals.get('dead_code_pct', 0)
    knot = signals.get('knot_score', 0)
    ci = signals.get('codebase_intelligence', 0)

    if dead_code < 10 or ci > 0.8:
        return None

    # Hollowness = dead weight + coupling pressure + low intelligence
    hollowness = 0.0
    if dead_code > 15:
        hollowness += min(0.4, (dead_code - 15) / 50)
    if knot > 3:
        hollowness += min(0.3, (knot - 3) / 10)
    hollowness += max(0.0, 0.3 * (1.0 - ci))

    if hollowness < 0.3:
        return None

    return Syndrome(
        name='hollow_architecture',
        severity=round(min(1.0, hollowness), 4),
        signals={
            'dead_code_pct': dead_code,
            'knot_score': knot,
            'codebase_intelligence': ci,
        },
        description=(
            'Architecture appears structured but contains significant dead code '
            'and entanglement. Surface-level metrics mask underlying decay.'
        ),
    )


def _detect_dependency_sprawl(signals: dict) -> Optional[Syndrome]:
    """High dependencies + high ecosystem unknowns + low edge diversity.

    The project depends on many things it doesn't understand, and the
    connectivity graph doesn't reflect the actual dependency complexity.
    """
    dep_count = signals.get('dependency_count')
    eco_unknowns = signals.get('ecosystem_unknowns')
    edge_div = signals.get('edge_diversity')  # (type_count, dominant_pct)

    if dep_count is None or dep_count < 30:
        return None

    severity = 0.0

    # Heavy dependencies
    if dep_count > 100:
        severity += 0.3
    elif dep_count > 50:
        severity += 0.15

    # Unknown ecosystem patterns
    if eco_unknowns is not None and eco_unknowns > 20:
        severity += min(0.3, eco_unknowns / 100)

    # Low edge diversity (graph doesn't reflect dependency richness)
    if edge_div is not None:
        type_count, dominant_pct = edge_div
        if type_count <= 2 or dominant_pct > 0.85:
            severity += 0.2

    if severity < 0.3:
        return None

    return Syndrome(
        name='dependency_sprawl',
        severity=round(min(1.0, severity), 4),
        signals={
            'dependency_count': dep_count,
            'ecosystem_unknowns': eco_unknowns,
            'edge_diversity': edge_div,
        },
        description=(
            'Large dependency footprint with many unrecognized ecosystem '
            'patterns. Supply-chain risk is elevated.'
        ),
    )


def _detect_purpose_vacuum(signals: dict) -> Optional[Syndrome]:
    """Low CI + no semantic domain + low roadmap readiness.

    The codebase doesn't know what it is. No clear purpose, weak semantics,
    and the roadmap (if any) is unfulfilled.
    """
    ci = signals.get('codebase_intelligence', 0)
    domain = signals.get('domain_clarity')
    readiness = signals.get('roadmap_readiness')
    class_cov = signals.get('classification_coverage')

    if ci > 0.7:
        return None

    severity = 0.0
    severity += max(0.0, 0.3 * (1.0 - ci))

    if domain is None or domain == 'Unknown':
        severity += 0.2

    if readiness is not None and readiness < 50:
        severity += min(0.2, (50 - readiness) / 100)

    if class_cov is not None and class_cov < 0.5:
        severity += 0.15

    if severity < 0.3:
        return None

    return Syndrome(
        name='purpose_vacuum',
        severity=round(min(1.0, severity), 4),
        signals={
            'codebase_intelligence': ci,
            'domain_clarity': domain,
            'roadmap_readiness': readiness,
            'classification_coverage': class_cov,
        },
        description=(
            'Codebase lacks clear identity. Low intelligence, unclear domain, '
            'and incomplete roadmap suggest the project needs architectural direction.'
        ),
    )


def _detect_advisory_storm(signals: dict) -> Optional[Syndrome]:
    """Many warnings + recommendations across multiple features = systemic issues.

    A few advisories are normal. A storm indicates the pipeline is finding
    problems everywhere, which often means a deeper structural issue.
    """
    warn_count, rec_count = signals.get('advisory_counts', (0, 0))
    total = warn_count + rec_count

    if total < 15:
        return None

    severity = min(1.0, total / 60)

    return Syndrome(
        name='advisory_storm',
        severity=round(severity, 4),
        signals={
            'warning_count': warn_count,
            'recommendation_count': rec_count,
            'total_advisories': total,
        },
        description=(
            f'{total} advisories ({warn_count} warnings, {rec_count} recommendations) '
            'indicate systemic issues across multiple analysis dimensions.'
        ),
    )


# ---------------------------------------------------------------------------
# Contradiction detectors
# ---------------------------------------------------------------------------

def _detect_contradictions(signals: dict) -> List[Contradiction]:
    """Detect pairs of signals that shouldn't coexist."""
    contradictions = []

    # 1. High CI but low classification coverage
    ci = signals.get('codebase_intelligence', 0)
    class_cov = signals.get('classification_coverage')
    if ci > 0.8 and class_cov is not None and class_cov < 0.5:
        contradictions.append(Contradiction(
            signal_a='codebase_intelligence',
            signal_b='classification_coverage',
            tension=round(ci - class_cov, 4),
            description=(
                'High codebase intelligence but low classification coverage. '
                'Either CI is inflated or classification is overly strict.'
            ),
        ))

    # 2. Good ideome coherence but high noise
    ideome_coh = signals.get('ideome_coherence')
    noise = signals.get('noise_ratio')
    if ideome_coh is not None and ideome_coh > 0.7 and noise is not None and noise > 0.4:
        contradictions.append(Contradiction(
            signal_a='ideome_coherence',
            signal_b='noise_ratio',
            tension=round(ideome_coh * noise, 4),
            description=(
                'Ideome shows good code-doc alignment but analysis filtered >40% of files. '
                'Coherence may be based on incomplete picture.'
            ),
        ))

    # 3. Low dead code but high entanglement
    dead = signals.get('dead_code_pct', 0)
    knot = signals.get('knot_score', 0)
    if dead < 5 and knot > 5:
        contradictions.append(Contradiction(
            signal_a='dead_code_pct',
            signal_b='knot_score',
            tension=round(min(1.0, knot / 10), 4),
            description=(
                'Almost no dead code but high entanglement. Code is tightly coupled '
                'but fully used -- refactoring will be high-impact.'
            ),
        ))

    # 4. Many dependencies but few edge types
    dep_count = signals.get('dependency_count')
    edge_div = signals.get('edge_diversity')
    if dep_count is not None and dep_count > 50 and edge_div is not None:
        type_count, _ = edge_div
        if type_count <= 2:
            contradictions.append(Contradiction(
                signal_a='dependency_count',
                signal_b='edge_type_count',
                tension=round(min(1.0, dep_count / 100), 4),
                description=(
                    f'{dep_count} dependencies but only {type_count} edge types. '
                    'Dependency graph lacks resolution -- most relationships are invisible.'
                ),
            ))

    return contradictions


# ---------------------------------------------------------------------------
# Modulation generators
# ---------------------------------------------------------------------------

def _generate_modulations(signals: dict, syndromes: List[Syndrome]) -> List[Modulation]:
    """Generate score modulation coefficients from signals and syndromes."""
    modulations = []

    # --- Signal-based modulations ---

    # Noise ratio affects topology (graph built from partial data)
    noise = signals.get('noise_ratio')
    if noise is not None and noise > 0.3:
        penalty = max(0.75, 1.0 - (noise - 0.3) * 0.5)
        modulations.append(Modulation(
            target='topology',
            coefficient=round(penalty, 4),
            reason=f'High noise ratio ({noise:.0%}) -- topology based on {1-noise:.0%} of codebase',
            signals={'noise_ratio': noise},
        ))

    # Low classification coverage affects purpose scoring
    class_cov = signals.get('classification_coverage')
    if class_cov is not None and class_cov < 0.7:
        penalty = max(0.75, class_cov + 0.15)
        modulations.append(Modulation(
            target='purpose',
            coefficient=round(penalty, 4),
            reason=f'Classification coverage {class_cov:.0%} -- purpose metrics partially blind',
            signals={'classification_coverage': class_cov},
        ))

    # Weak boundaries affect constraints scoring
    boundary = signals.get('boundary_ratio')
    if boundary is not None and boundary > 0.3:
        penalty = max(0.80, 1.0 - (boundary - 0.3) * 0.4)
        modulations.append(Modulation(
            target='constraints',
            coefficient=round(penalty, 4),
            reason=f'High boundary ratio ({boundary:.0%}) -- constraint enforcement suspect',
            signals={'boundary_ratio': boundary},
        ))

    # Heavy dependencies affect entanglement
    dep_count = signals.get('dependency_count')
    if dep_count is not None and dep_count > 50:
        penalty = max(0.80, 1.0 - min(0.2, (dep_count - 50) / 500))
        modulations.append(Modulation(
            target='entanglement',
            coefficient=round(penalty, 4),
            reason=f'{dep_count} dependencies -- coupling pressure beyond internal graph',
            signals={'dependency_count': dep_count},
        ))

    # Low edge diversity affects topology and i_struct
    edge_div = signals.get('edge_diversity')
    if edge_div is not None:
        type_count, dominant_pct = edge_div
        if type_count <= 2 or dominant_pct > 0.85:
            penalty = max(0.80, 1.0 - (dominant_pct - 0.8) * 1.0) if dominant_pct > 0.8 else 0.85
            modulations.append(Modulation(
                target='topology',
                coefficient=round(penalty, 4),
                reason=f'Low edge diversity ({type_count} types, {dominant_pct:.0%} dominant)',
                signals={'edge_type_count': type_count, 'dominant_pct': dominant_pct},
            ))
            modulations.append(Modulation(
                target='i_struct',
                coefficient=round(penalty, 4),
                reason=f'Monomorphic graph -- structural incoherence may be underestimated',
                signals={'edge_type_count': type_count, 'dominant_pct': dominant_pct},
            ))

    # File concentration affects topology (extreme = structural risk)
    concentration = signals.get('file_concentration')
    if concentration is not None and concentration > 10:
        penalty = max(0.80, 1.0 - min(0.2, (concentration - 10) / 50))
        modulations.append(Modulation(
            target='topology',
            coefficient=round(penalty, 4),
            reason=f'Extreme file concentration ({concentration:.1f}x average)',
            signals={'file_concentration': concentration},
        ))

    # Weak domain clarity affects purpose and i_telic
    domain = signals.get('domain_clarity')
    if domain is None or domain == 'Unknown':
        modulations.append(Modulation(
            target='purpose',
            coefficient=0.92,
            reason='No semantic domain inferred -- naming may not convey intent',
            signals={'domain_clarity': domain},
        ))
        modulations.append(Modulation(
            target='i_telic',
            coefficient=0.92,
            reason='Unknown domain -- teleological assessment less grounded',
            signals={'domain_clarity': domain},
        ))

    # Low roadmap readiness affects purpose_fulfillment mission matrix
    readiness = signals.get('roadmap_readiness')
    if readiness is not None and readiness < 60:
        penalty = max(0.80, readiness / 75)
        modulations.append(Modulation(
            target='purpose_fulfillment',
            coefficient=round(penalty, 4),
            reason=f'Roadmap readiness {readiness:.0f}% -- planned architecture incomplete',
            signals={'roadmap_readiness': readiness},
        ))

    # Low ideome coherence affects i_sym (symmetry)
    ideome = signals.get('ideome_coherence')
    if ideome is not None and ideome < 0.5:
        penalty = max(0.75, 0.5 + ideome)
        modulations.append(Modulation(
            target='i_sym',
            coefficient=round(penalty, 4),
            reason=f'Low ideome coherence ({ideome:.3f}) -- code/docs divergence amplified',
            signals={'ideome_coherence': ideome},
        ))

    # --- Syndrome-based modulations ---

    for syn in syndromes:
        if syn.name == 'flying_blind' and syn.severity > 0.4:
            # Flying blind degrades ALL scores
            global_penalty = max(0.80, 1.0 - syn.severity * 0.25)
            for target in ('topology', 'purpose', 'constraints'):
                modulations.append(Modulation(
                    target=target,
                    coefficient=round(global_penalty, 4),
                    reason=f'Syndrome: flying_blind (severity={syn.severity:.2f})',
                    signals=syn.signals,
                ))

        elif syn.name == 'hollow_architecture' and syn.severity > 0.3:
            # Hollow architecture inflates apparent health
            penalty = max(0.85, 1.0 - syn.severity * 0.2)
            modulations.append(Modulation(
                target='dead_code',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: hollow_architecture (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))
            modulations.append(Modulation(
                target='entanglement',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: hollow_architecture (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))

        elif syn.name == 'dependency_sprawl' and syn.severity > 0.3:
            penalty = max(0.85, 1.0 - syn.severity * 0.2)
            modulations.append(Modulation(
                target='execution',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: dependency_sprawl (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))

        elif syn.name == 'purpose_vacuum' and syn.severity > 0.3:
            penalty = max(0.80, 1.0 - syn.severity * 0.25)
            modulations.append(Modulation(
                target='purpose',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: purpose_vacuum (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))
            modulations.append(Modulation(
                target='i_telic',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: purpose_vacuum (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))

        elif syn.name == 'advisory_storm' and syn.severity > 0.3:
            penalty = max(0.90, 1.0 - syn.severity * 0.1)
            modulations.append(Modulation(
                target='logic',
                coefficient=round(penalty, 4),
                reason=f'Syndrome: advisory_storm (severity={syn.severity:.2f})',
                signals=syn.signals,
            ))

    return modulations


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_chemistry(full_output: dict) -> ChemistryResult:
    """Run the data chemistry layer on full Collider output.

    Extracts cross-cutting signals, detects syndromes and contradictions,
    and produces modulation coefficients for the scoring pipeline.

    Args:
        full_output: The unified analysis dict from Collider.

    Returns:
        ChemistryResult with modulations, syndromes, contradictions.
    """
    # --- Extract all signals ---
    signals: Dict[str, Any] = {}
    expected_signals = 0

    noise = _extract_noise_ratio(full_output)
    if noise is not None:
        signals['noise_ratio'] = noise
    expected_signals += 1

    class_cov = _extract_classification_coverage(full_output)
    if class_cov is not None:
        signals['classification_coverage'] = class_cov
    expected_signals += 1

    edge_div = _extract_edge_diversity(full_output)
    if edge_div is not None:
        signals['edge_diversity'] = edge_div
    expected_signals += 1

    boundary = _extract_boundary_ratio(full_output)
    if boundary is not None:
        signals['boundary_ratio'] = boundary
    expected_signals += 1

    dep_count = _extract_dependency_count(full_output)
    if dep_count is not None:
        signals['dependency_count'] = dep_count
    expected_signals += 1

    eco_unknowns = _extract_ecosystem_unknowns(full_output)
    if eco_unknowns is not None:
        signals['ecosystem_unknowns'] = eco_unknowns
    expected_signals += 1

    readiness = _extract_roadmap_readiness(full_output)
    if readiness is not None:
        signals['roadmap_readiness'] = readiness
    expected_signals += 1

    w, r = _extract_advisory_counts(full_output)
    signals['advisory_counts'] = (w, r)
    expected_signals += 1

    concentration = _extract_file_concentration(full_output)
    if concentration is not None:
        signals['file_concentration'] = concentration
    expected_signals += 1

    domain = _extract_domain_clarity(full_output)
    if domain is not None:
        signals['domain_clarity'] = domain
    expected_signals += 1

    ideome = _extract_ideome_coherence(full_output)
    if ideome is not None:
        signals['ideome_coherence'] = ideome
    expected_signals += 1

    signals['dead_code_pct'] = _extract_dead_code_pct(full_output)
    signals['knot_score'] = _extract_knot_score(full_output)
    signals['codebase_intelligence'] = _extract_ci(full_output)
    expected_signals += 3

    # --- Signal coverage ---
    present = sum(1 for k, v in signals.items()
                  if v is not None and v != 0 and v != (0, 0))
    coverage = present / max(1, expected_signals)

    # --- Detect syndromes ---
    syndromes = []
    for detector in (
        _detect_flying_blind,
        _detect_hollow_architecture,
        _detect_dependency_sprawl,
        _detect_purpose_vacuum,
        _detect_advisory_storm,
    ):
        result = detector(signals)
        if result is not None:
            syndromes.append(result)

    # --- Detect contradictions ---
    contradictions = _detect_contradictions(signals)

    # --- Generate modulations ---
    modulations = _generate_modulations(signals, syndromes)

    # --- Compound severity ---
    if syndromes:
        compound = sum(s.severity for s in syndromes) / len(syndromes)
        # Boost if multiple syndromes are active (compounding effect)
        if len(syndromes) >= 2:
            compound = min(1.0, compound * (1.0 + 0.1 * (len(syndromes) - 1)))
    else:
        compound = 0.0

    return ChemistryResult(
        modulations=modulations,
        syndromes=syndromes,
        contradictions=contradictions,
        compound_severity=round(compound, 4),
        signal_coverage=round(coverage, 4),
    )


# ---------------------------------------------------------------------------
# ChemistryLab -- stateful parallel sibling to the pipeline
# ---------------------------------------------------------------------------

# All signal keys the lab knows how to extract from full_output
_INGEST_EXTRACTORS: Dict[str, Any] = {
    'noise_ratio': _extract_noise_ratio,
    'classification_coverage': _extract_classification_coverage,
    'edge_diversity': _extract_edge_diversity,
    'boundary_ratio': _extract_boundary_ratio,
    'dependency_count': _extract_dependency_count,
    'ecosystem_unknowns': _extract_ecosystem_unknowns,
    'roadmap_readiness': _extract_roadmap_readiness,
    'file_concentration': _extract_file_concentration,
    'domain_clarity': _extract_domain_clarity,
    'ideome_coherence': _extract_ideome_coherence,
}

# Extractors that always return a value (never None)
_ALWAYS_EXTRACTORS: Dict[str, Any] = {
    'dead_code_pct': _extract_dead_code_pct,
    'knot_score': _extract_knot_score,
    'codebase_intelligence': _extract_ci,
}

EXPECTED_SIGNAL_COUNT = len(_INGEST_EXTRACTORS) + len(_ALWAYS_EXTRACTORS) + 1  # +1 for advisory_counts


class ChemistryLab:
    """Stateful cross-signal correlation service.

    Lives alongside the pipeline as a parallel sibling.  The pipeline
    feeds signals to the lab (individually or in bulk), and any
    subsystem can query for modulation coefficients at any time.

    Lazy evaluation: internal analysis is deferred until a query
    arrives, then cached until new data invalidates it.

    Usage::

        lab = ChemistryLab()

        # Bulk feed from the assembled full_output dict
        lab.ingest(full_output)

        # Or feed signals incrementally as pipeline stages complete
        lab.feed('noise_ratio', 0.42)
        lab.feed('classification_coverage', 0.85)

        # Query from any scoring method
        topology_coeff = lab.get_modulation('topology')     # float
        purpose_coeff  = lab.get_modulation('purpose')      # float
        i_struct_coeff = lab.get_modulation('i_struct')      # float

        # Full result for serialisation into full_output
        result = lab.get_result()                           # ChemistryResult
        full_output['chemistry'] = result.to_dict()
    """

    def __init__(self) -> None:
        self._signals: Dict[str, Any] = {}
        self._dirty: bool = True
        self._result: Optional[ChemistryResult] = None

    # --- Feeding interface -------------------------------------------------

    def feed(self, key: str, value: Any) -> None:
        """Feed a single signal to the lab.

        The lab marks itself dirty so the next query triggers recomputation.
        Feeding the same key again overwrites the previous value.
        """
        self._signals[key] = value
        self._dirty = True

    def feed_many(self, signals: Dict[str, Any]) -> None:
        """Feed multiple signals at once."""
        self._signals.update(signals)
        self._dirty = True

    def ingest(self, full_output: dict) -> None:
        """Bulk-extract all known signals from a full_output dict.

        This is the most common usage: call once after full_output is
        assembled, and the lab will extract every signal it knows about.
        """
        for key, extractor in _INGEST_EXTRACTORS.items():
            val = extractor(full_output)
            if val is not None:
                self._signals[key] = val

        for key, extractor in _ALWAYS_EXTRACTORS.items():
            self._signals[key] = extractor(full_output)

        w, r = _extract_advisory_counts(full_output)
        self._signals['advisory_counts'] = (w, r)

        self._dirty = True

    # --- Query interface ---------------------------------------------------

    def get_modulation(self, target: str) -> float:
        """Get the combined modulation coefficient for a scoring target.

        Returns 1.0 (neutral) if no modulations apply or the lab has
        no data yet.  Multiple modulations on the same target are
        multiplied together.
        """
        self._ensure_computed()
        assert self._result is not None
        return self._result.get_modulation(target)

    def get_result(self) -> ChemistryResult:
        """Get the full ChemistryResult (syndromes, contradictions, etc.)."""
        self._ensure_computed()
        assert self._result is not None
        return self._result

    @property
    def syndromes(self) -> List[Syndrome]:
        """Active syndromes (empty list if none detected)."""
        self._ensure_computed()
        assert self._result is not None
        return self._result.syndromes

    @property
    def contradictions(self) -> List[Contradiction]:
        """Detected contradictions (empty list if none)."""
        self._ensure_computed()
        assert self._result is not None
        return self._result.contradictions

    @property
    def compound_severity(self) -> float:
        """Aggregate syndrome severity [0,1]."""
        self._ensure_computed()
        assert self._result is not None
        return self._result.compound_severity

    @property
    def signal_coverage(self) -> float:
        """Fraction of expected signals that are present."""
        self._ensure_computed()
        assert self._result is not None
        return self._result.signal_coverage

    @property
    def signals(self) -> Dict[str, Any]:
        """Read-only view of current signal state (for debugging)."""
        return dict(self._signals)

    # --- Internal ----------------------------------------------------------

    def _ensure_computed(self) -> None:
        """Lazily recompute if signals have changed since last query."""
        if self._dirty or self._result is None:
            self._recompute()
            self._dirty = False

    def _recompute(self) -> None:
        """Run syndrome detection, contradiction detection, and modulation
        generation on the current signal set."""
        signals = dict(self._signals)

        # Signal coverage
        present = sum(1 for v in signals.values()
                      if v is not None and v != 0 and v != (0, 0))
        coverage = present / max(1, EXPECTED_SIGNAL_COUNT)

        # Detect syndromes
        syndromes: List[Syndrome] = []
        for detector in (
            _detect_flying_blind,
            _detect_hollow_architecture,
            _detect_dependency_sprawl,
            _detect_purpose_vacuum,
            _detect_advisory_storm,
        ):
            result = detector(signals)
            if result is not None:
                syndromes.append(result)

        # Detect contradictions
        contradictions = _detect_contradictions(signals)

        # Generate modulations
        modulations = _generate_modulations(signals, syndromes)

        # Compound severity
        if syndromes:
            compound = sum(s.severity for s in syndromes) / len(syndromes)
            if len(syndromes) >= 2:
                compound = min(1.0, compound * (1.0 + 0.1 * (len(syndromes) - 1)))
        else:
            compound = 0.0

        self._result = ChemistryResult(
            modulations=modulations,
            syndromes=syndromes,
            contradictions=contradictions,
            compound_severity=round(compound, 4),
            signal_coverage=round(coverage, 4),
        )

    def __repr__(self) -> str:
        status = 'dirty' if self._dirty else 'computed'
        n_signals = len(self._signals)
        n_syn = len(self._result.syndromes) if self._result else '?'
        return f'<ChemistryLab signals={n_signals} syndromes={n_syn} [{status}]>'
