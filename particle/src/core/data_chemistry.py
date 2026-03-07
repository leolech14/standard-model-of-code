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
    affected_entities: List[str] = field(default_factory=list)


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
    affected_entities: List[str] = field(default_factory=list)
    resolution_hint: str = ''


@dataclass
class NodeConvergence:
    """Per-node record of converging negative signals."""
    node_id: str          # e.g. "particle/src/core/foo.py::BarClass"
    name: str
    file_path: str
    signal_count: int     # how many negative signals converge
    signals: List[str]    # which signal names fired
    severity: str         # "critical" (5+), "high" (4), "moderate" (3)


@dataclass
class ConvergenceResult:
    """Aggregate result of per-node convergence analysis."""
    convergent_nodes: List[NodeConvergence] = field(default_factory=list)
    total_nodes: int = 0
    convergent_count: int = 0       # nodes with 3+ signals
    critical_count: int = 0         # nodes with 5+ signals
    signal_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'convergent_nodes': [asdict(n) for n in self.convergent_nodes],
            'total_nodes': self.total_nodes,
            'convergent_count': self.convergent_count,
            'critical_count': self.critical_count,
            'signal_distribution': self.signal_distribution,
        }


@dataclass
class ChemistryResult:
    """Complete output of the data chemistry layer."""
    modulations: List[Modulation] = field(default_factory=list)
    syndromes: List[Syndrome] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)
    compound_severity: float = 0.0   # aggregate syndrome severity [0,1]
    signal_coverage: float = 0.0     # fraction of expected signals present
    convergence: Optional[ConvergenceResult] = None

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
        # Serialize convergence with its own to_dict
        if self.convergence is not None:
            d['convergence'] = self.convergence.to_dict()
        else:
            d['convergence'] = None
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
    # Primary: nested estimates.skip_ratio (actual SmartIgnore output structure)
    estimates = si.get('estimates', {})
    if isinstance(estimates, dict):
        ratio = estimates.get('skip_ratio')
        if ratio is not None:
            return float(ratio)
        skipped = estimates.get('files_skipped', 0)
        total = estimates.get('files_to_analyze', 0) + skipped
        if total > 0:
            return skipped / total
    # Legacy fallback: flat keys
    ratio = si.get('noise_ratio')
    if ratio is not None:
        return float(ratio)
    return None


def _extract_classification_coverage(full_output: dict) -> Optional[float]:
    """Extract classification coverage as fraction [0,1].

    Classification output uses {by_role: {Service: 45, Unknown: 12, ...}}.
    Coverage = nodes with known role / total nodes.
    """
    cls = full_output.get('classification', {})
    if not cls or not isinstance(cls, dict):
        return None
    by_role = cls.get('by_role', {})
    if not by_role or not isinstance(by_role, dict):
        return None
    total = sum(v for v in by_role.values() if isinstance(v, (int, float)))
    if total == 0:
        return None
    unknown = sum(v for k, v in by_role.items()
                  if isinstance(v, (int, float)) and k in ('Unknown', 'unknown', 'Internal'))
    return (total - unknown) / total


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


def _extract_drift_score(full_output: dict) -> Optional[float]:
    """Extract API drift score [0,1]. 0 = fully aligned, 1 = total mismatch."""
    drift = full_output.get('api_drift', {})
    if not drift:
        return None
    score = drift.get('drift_score')
    return float(score) if score is not None else None


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
            resolution_hint=(
                'Layer classification depends on convention files. Add __init__.py '
                'markers or review naming patterns to improve coverage.'
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
            resolution_hint=(
                'Advisory noise suggests style/linting gaps. The code\'s conceptual '
                'model is sound -- focus on tooling config to reduce filtered files.'
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
            resolution_hint=(
                'Tight coupling without dead code suggests active but brittle '
                'dependencies. Extract shared interfaces to reduce knot score.'
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
                resolution_hint=(
                    'Dependency variety is low -- most relationships are simple imports. '
                    'Consider whether semantic edges (inheritance, composition) are detected.'
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
    'drift_score': _extract_drift_score,
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
        self._nodes: List[dict] = []  # per-node data for convergence analysis
        self._ledger = None           # DataLedger for signal availability reporting

    def set_ledger(self, ledger) -> None:
        """Attach a DataLedger for signal availability reporting."""
        self._ledger = ledger

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

        # Store nodes for per-node convergence analysis
        self._nodes = full_output.get('nodes', [])

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

    # --- Node-level convergence --------------------------------------------

    def analyze_node_convergence(self) -> ConvergenceResult:
        """Count converging negative signals per node.

        Iterates full_output['nodes'] and checks each node against 8
        negative-signal thresholds.  Nodes with 3+ converging signals
        are flagged with severity grading:
            5+ signals = "critical"
            4  signals = "high"
            3  signals = "moderate"
        """
        if not self._nodes:
            return ConvergenceResult()

        signal_dist: Dict[str, int] = {}
        convergent: List[NodeConvergence] = []

        for node in self._nodes:
            fired: List[str] = []

            # 1. Low confidence
            conf = node.get('confidence', 1.0)
            if isinstance(conf, (int, float)) and conf < 0.5:
                fired.append('low_confidence')

            # 2. No docstring
            ds = node.get('docstring')
            ip = node.get('intent_profile') or {}
            if not ds and not ip.get('has_docstring', True):
                fired.append('no_docstring')

            # 3. Implicit / Ambiguous intent
            intent = node.get('intent', '')
            if intent in ('Implicit', 'Ambiguous'):
                fired.append('implicit_intent')

            # 4. Unknown layer
            if node.get('layer') == 'Unknown':
                fired.append('unknown_layer')

            # 5. God class
            if node.get('is_god_class'):
                fired.append('god_class')

            # 6. Low Q_total
            pi = node.get('purpose_intelligence') or {}
            q = pi.get('Q_total')
            if isinstance(q, (int, float)) and q < 0.4:
                fired.append('low_q_total')

            # 7. Low coherence
            coh = node.get('coherence_score')
            if isinstance(coh, (int, float)) and coh < 0.4:
                fired.append('low_coherence')

            # 8. High complexity
            cc = node.get('cyclomatic_complexity')
            if isinstance(cc, (int, float)) and cc > 15:
                fired.append('high_complexity')

            # Track distribution
            for s in fired:
                signal_dist[s] = signal_dist.get(s, 0) + 1

            if len(fired) >= 3:
                if len(fired) >= 5:
                    sev = 'critical'
                elif len(fired) >= 4:
                    sev = 'high'
                else:
                    sev = 'moderate'

                nid = node.get('id', node.get('name', '?'))
                convergent.append(NodeConvergence(
                    node_id=nid,
                    name=node.get('name', ''),
                    file_path=node.get('file_path', ''),
                    signal_count=len(fired),
                    signals=fired,
                    severity=sev,
                ))

        convergent.sort(key=lambda n: n.signal_count, reverse=True)

        return ConvergenceResult(
            convergent_nodes=convergent,
            total_nodes=len(self._nodes),
            convergent_count=len(convergent),
            critical_count=sum(1 for n in convergent if n.severity == 'critical'),
            signal_distribution=signal_dist,
        )

    # --- AI Consumer Summary -----------------------------------------------

    def build_ai_consumer_summary(self) -> dict:
        """Build a structured summary block optimized for AI consumers.

        Returns a JSON-serializable dict with headline, grade,
        contradictions, convergent concerns, blind spots, and
        prioritized next actions.  Designed to be the single entry
        point an AI agent reads to understand system health.
        """
        self._ensure_computed()
        assert self._result is not None
        r = self._result

        # --- Headline ---
        n_syn = len(r.syndromes)
        n_cont = len(r.contradictions)
        conv = r.convergence
        n_crit = conv.critical_count if conv else 0

        parts = []
        if n_syn:
            parts.append(f'{n_syn} syndrome{"s" if n_syn != 1 else ""}')
        if n_cont:
            parts.append(f'{n_cont} contradiction{"s" if n_cont != 1 else ""}')
        if n_crit:
            parts.append(f'{n_crit} critical convergence node{"s" if n_crit != 1 else ""}')

        if not parts:
            headline = 'System shows no cross-signal anomalies.'
        else:
            headline = f'Cross-signal analysis detected {", ".join(parts)}.'

        # --- Grade ---
        score = 10.0
        score -= n_syn * 1.5
        score -= n_cont * 1.0
        score -= min(3.0, n_crit * 0.5)
        score -= r.compound_severity * 2.0
        score = max(0.0, min(10.0, score))

        if score >= 8.5:
            grade = 'A'
        elif score >= 7.0:
            grade = 'B'
        elif score >= 5.0:
            grade = 'C'
        elif score >= 3.0:
            grade = 'D'
        else:
            grade = 'F'

        # --- Key contradictions ---
        key_contradictions = []
        for c in r.contradictions:
            entry = {
                'signal_a': c.signal_a,
                'signal_b': c.signal_b,
                'tension': c.tension,
                'description': c.description,
            }
            # P1-B: resolution_hint (populated by Step 4)
            if hasattr(c, 'resolution_hint'):
                entry['resolution_hint'] = c.resolution_hint
            # P1-A: affected_entities (populated by Step 3)
            if hasattr(c, 'affected_entities'):
                entry['affected_entities'] = c.affected_entities
            key_contradictions.append(entry)

        # --- Convergent concerns ---
        convergent_concerns = {'critical_nodes': 0, 'top_entities': [], 'signal_heatmap': {}}
        if conv and conv.convergent_count > 0:
            top = conv.convergent_nodes[:10]
            convergent_concerns = {
                'critical_nodes': conv.critical_count,
                'top_entities': [
                    {
                        'id': n.node_id,
                        'name': n.name,
                        'file': n.file_path,
                        'signals': n.signals,
                        'count': n.signal_count,
                    }
                    for n in top
                ],
                'signal_heatmap': conv.signal_distribution,
            }

        # --- Blind spots ---
        expected = {
            'codebase_intelligence', 'classification_coverage',
            'noise_ratio', 'purpose_entropy', 'knot_score',
            'dead_code_pct', 'dependency_count', 'ideome_coherence',
            'domain_clarity', 'roadmap_readiness', 'advisory_counts',
            'boundary_coverage', 'edge_diversity', 'node_metrics',
        }
        present = set(self._signals.keys())
        blind_spots = sorted(expected - present)

        # --- Actionable next ---
        actions = []
        # Prioritize by syndrome severity
        for syn in sorted(r.syndromes, key=lambda s: s.severity, reverse=True):
            a: Dict[str, Any] = {
                'action': f'Address "{syn.name}" syndrome',
                'impact': 'high' if syn.severity > 0.6 else 'medium',
                'effort': 'medium',
            }
            if hasattr(syn, 'affected_entities') and syn.affected_entities:
                a['targets'] = syn.affected_entities[:5]
            actions.append(a)
        # Add convergence action
        if n_crit > 0 and conv:
            actions.insert(0, {
                'action': f'Remediate {n_crit} critically convergent modules',
                'impact': 'high',
                'effort': 'high',
                'targets': [n.node_id for n in conv.convergent_nodes[:5]
                            if n.severity == 'critical'],
            })
        # Add blind spot action
        if blind_spots:
            actions.append({
                'action': f'Investigate {len(blind_spots)} missing signal(s): {", ".join(blind_spots[:3])}',
                'impact': 'medium',
                'effort': 'low',
            })
        actions = actions[:5]  # cap at 5

        # --- Signal availability from DataLedger ---
        signal_availability = None
        if self._ledger is not None:
            # Map chemistry signal keys to ledger data keys for availability check
            _SIGNAL_TO_LEDGER = {
                'noise_ratio': 'smartignore',
                'classification_coverage': 'nodes',
                'edge_diversity': 'edges',
                'boundary_ratio': 'codome',
                'dependency_count': 'nodes',
                'ecosystem_unknowns': 'ecosystem',
                'roadmap_readiness': 'roadmap',
                'file_concentration': 'full_output',
                'domain_clarity': 'semantics',
                'ideome_coherence': 'ideome',
                'drift_score': 'api_drift',
                'dead_code_pct': 'execution_flow',
                'knot_score': 'knots',
                'codebase_intelligence': 'purpose_intelligence',
            }
            signal_availability = {}
            for sig_key, ledger_key in _SIGNAL_TO_LEDGER.items():
                extracted = sig_key in self._signals
                ledger_status = self._ledger.get_status(ledger_key)
                signal_availability[sig_key] = {
                    'extracted': extracted,
                    'ledger_status': ledger_status,
                }

        result = {
            'headline': headline,
            'data_utility_grade': grade,
            'key_contradictions': key_contradictions,
            'convergent_concerns': convergent_concerns,
            'blind_spots': blind_spots,
            'actionable_next': actions,
            'meta': {
                'chemistry_version': '1.1.0',
                'signals_extracted': len(self._signals),
                'syndromes_active': n_syn,
                'contradictions_found': n_cont,
                'convergent_nodes': conv.convergent_count if conv else 0,
                'critical_nodes': n_crit,
            },
        }
        if signal_availability is not None:
            result['signal_availability'] = signal_availability
        return result

    # --- Internal ----------------------------------------------------------

    def _ensure_computed(self) -> None:
        """Lazily recompute if signals have changed since last query."""
        if self._dirty or self._result is None:
            self._recompute()
            self._dirty = False

    def _enrich_with_entity_paths(
        self,
        syndromes: List[Syndrome],
        contradictions: List[Contradiction],
    ) -> None:
        """Attach affected_entities to syndromes and contradictions.

        Scans self._nodes to find entities that match each syndrome's or
        contradiction's criteria. Mutates the objects in-place.
        """
        if not self._nodes:
            return

        # Build quick-lookup sets from nodes
        low_conf_nodes = []         # confidence < 0.5
        no_doc_nodes = []           # missing docstring
        unknown_layer_nodes = []    # layer == 'Unknown'
        god_class_nodes = []        # is_god_class
        low_q_nodes = []            # Q_total < 0.3
        high_outdegree_nodes = []   # out_degree > median*2

        out_degrees = [n.get('out_degree', 0) for n in self._nodes if isinstance(n, dict)]
        median_od = sorted(out_degrees)[len(out_degrees) // 2] if out_degrees else 0

        for node in self._nodes:
            if not isinstance(node, dict):
                continue
            nid = node.get('id', node.get('name', ''))

            conf = node.get('confidence')
            if conf is not None and conf < 0.5:
                low_conf_nodes.append(nid)

            doc = node.get('docstring')
            ip = node.get('intent_profile', {}) or {}
            has_doc = bool(doc) or ip.get('has_docstring', False)
            if not has_doc:
                no_doc_nodes.append(nid)

            layer = node.get('layer', '')
            if layer == 'Unknown':
                unknown_layer_nodes.append(nid)

            if node.get('is_god_class', False):
                god_class_nodes.append(nid)

            pi = node.get('purpose_intelligence', {}) or {}
            qt = pi.get('Q_total')
            if qt is not None and qt < 0.3:
                low_q_nodes.append(nid)

            od = node.get('out_degree', 0)
            if median_od > 0 and od > median_od * 2:
                high_outdegree_nodes.append(nid)

        # --- Enrich syndromes ---
        for syn in syndromes:
            if syn.name == 'flying_blind':
                # low confidence AND no docstring
                syn.affected_entities = sorted(
                    set(low_conf_nodes) & set(no_doc_nodes)
                )[:20]
            elif syn.name == 'hollow_architecture':
                # unknown layer AND/OR god class
                syn.affected_entities = sorted(
                    set(unknown_layer_nodes) | set(god_class_nodes)
                )[:20]
            elif syn.name == 'dependency_sprawl':
                # high out-degree
                syn.affected_entities = sorted(high_outdegree_nodes)[:20]
            elif syn.name == 'purpose_vacuum':
                # low Q_total
                syn.affected_entities = sorted(low_q_nodes)[:20]
            # advisory_storm has no direct node mapping (system-wide)

        # --- Enrich contradictions ---
        for cont in contradictions:
            if cont.signal_a == 'codebase_intelligence' and \
               cont.signal_b == 'classification_coverage':
                # Nodes with high confidence but unknown layer
                high_conf = {n.get('id', n.get('name', ''))
                             for n in self._nodes if isinstance(n, dict)
                             and (n.get('confidence') or 0) > 0.8}
                cont.affected_entities = sorted(
                    high_conf & set(unknown_layer_nodes)
                )[:20]
            elif cont.signal_a == 'dead_code_pct' and \
                 cont.signal_b == 'knot_score':
                # High out-degree nodes (the knots)
                cont.affected_entities = sorted(high_outdegree_nodes)[:20]
            elif cont.signal_a == 'dependency_count' and \
                 cont.signal_b == 'edge_type_count':
                # Nodes with many outgoing edges
                cont.affected_entities = sorted(high_outdegree_nodes)[:20]

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

        # Enrich with entity paths (P1-A: attach affected nodes)
        self._enrich_with_entity_paths(syndromes, contradictions)

        # Generate modulations
        modulations = _generate_modulations(signals, syndromes)

        # Compound severity
        if syndromes:
            compound = sum(s.severity for s in syndromes) / len(syndromes)
            if len(syndromes) >= 2:
                compound = min(1.0, compound * (1.0 + 0.1 * (len(syndromes) - 1)))
        else:
            compound = 0.0

        # Node-level convergence (runs after system-wide analysis)
        convergence = self.analyze_node_convergence()

        self._result = ChemistryResult(
            modulations=modulations,
            syndromes=syndromes,
            contradictions=contradictions,
            compound_severity=round(compound, 4),
            signal_coverage=round(coverage, 4),
            convergence=convergence,
        )

    # --- Diagnostics --------------------------------------------------------

    def build_diagnostics(self) -> dict:
        """Build diagnostic report: signal values vs detector thresholds.

        Answers "why is compound_severity 0.0?" without reading source code.
        Returns a dict suitable for inclusion in the chemistry output.
        """
        self._ensure_computed()
        signals = dict(self._signals)

        # Signal values and coverage
        signal_values: dict = {}
        signal_coverage: dict = {}
        all_signal_keys = (
            list(_INGEST_EXTRACTORS.keys())
            + list(_ALWAYS_EXTRACTORS.keys())
            + ['advisory_counts']
        )
        for key in all_signal_keys:
            val = signals.get(key)
            signal_values[key] = val
            if val is None:
                signal_coverage[key] = "missing"
            elif val == 0 or val == (0, 0):
                signal_coverage[key] = "zero"
            else:
                signal_coverage[key] = "present"

        # Detector traces
        detector_traces = [
            self._trace_flying_blind(signals),
            self._trace_hollow_architecture(signals),
            self._trace_dependency_sprawl(signals),
            self._trace_purpose_vacuum(signals),
            self._trace_advisory_storm(signals),
        ]

        return {
            "signal_values": signal_values,
            "signal_coverage": signal_coverage,
            "detector_traces": detector_traces,
        }

    @staticmethod
    def _trace_flying_blind(signals: dict) -> dict:
        noise = signals.get('noise_ratio')
        class_cov = signals.get('classification_coverage')
        boundary = signals.get('boundary_ratio')

        conditions = [
            {"check": "noise_ratio > 0.3", "threshold": 0.3,
             "actual": noise, "passed": noise is not None and noise > 0.3},
            {"check": "classification_coverage < 0.7", "threshold": 0.7,
             "actual": class_cov, "passed": class_cov is not None and class_cov < 0.7},
            {"check": "boundary_ratio > 0.3", "threshold": 0.3,
             "actual": boundary, "passed": boundary is not None and boundary > 0.3},
        ]
        active = sum(1 for c in conditions if c["passed"])

        return {
            "detector": "flying_blind",
            "gate": "2+ conditions active AND severity >= 0.3",
            "conditions": conditions,
            "active_conditions": active,
            "fired": active >= 2,
            "reason": f"{active}/3 conditions met (need 2+)",
        }

    @staticmethod
    def _trace_hollow_architecture(signals: dict) -> dict:
        dead_code = signals.get('dead_code_pct', 0)
        knot = signals.get('knot_score', 0)
        ci = signals.get('codebase_intelligence', 0)

        gate_dead = dead_code >= 10
        gate_ci = ci <= 0.8
        gate_passed = gate_dead and gate_ci

        conditions = [
            {"check": "dead_code_pct >= 10", "threshold": 10,
             "actual": dead_code, "passed": gate_dead},
            {"check": "codebase_intelligence <= 0.8", "threshold": 0.8,
             "actual": ci, "passed": gate_ci},
            {"check": "knot_score > 3 (severity boost)", "threshold": 3,
             "actual": knot, "passed": knot > 3},
        ]

        reason = (
            f"Gate passed: dead_code={dead_code}, ci={ci}"
            if gate_passed
            else f"Gate failed: dead_code_pct={dead_code} {'>=10' if gate_dead else '<10'} "
                 f"AND ci={ci} {'<=0.8' if gate_ci else '>0.8'}"
        )

        return {
            "detector": "hollow_architecture",
            "gate": "dead_code_pct >= 10 AND codebase_intelligence <= 0.8",
            "conditions": conditions,
            "active_conditions": sum(1 for c in conditions if c["passed"]),
            "fired": gate_passed,
            "reason": reason,
        }

    @staticmethod
    def _trace_dependency_sprawl(signals: dict) -> dict:
        dep_count = signals.get('dependency_count')
        eco_unknowns = signals.get('ecosystem_unknowns')
        edge_div = signals.get('edge_diversity')

        gate_passed = dep_count is not None and dep_count >= 30
        conditions = [
            {"check": "dependency_count >= 30", "threshold": 30,
             "actual": dep_count, "passed": gate_passed},
            {"check": "dependency_count > 100 (high severity)", "threshold": 100,
             "actual": dep_count, "passed": dep_count is not None and dep_count > 100},
            {"check": "ecosystem_unknowns > 20", "threshold": 20,
             "actual": eco_unknowns,
             "passed": eco_unknowns is not None and eco_unknowns > 20},
        ]

        reason = (
            f"dep_count={dep_count} >= 30"
            if gate_passed
            else f"Gate failed: dependency_count={dep_count} (need >= 30)"
        )

        return {
            "detector": "dependency_sprawl",
            "gate": "dependency_count >= 30",
            "conditions": conditions,
            "active_conditions": sum(1 for c in conditions if c["passed"]),
            "fired": gate_passed,
            "reason": reason,
        }

    @staticmethod
    def _trace_purpose_vacuum(signals: dict) -> dict:
        ci = signals.get('codebase_intelligence', 0)
        domain = signals.get('domain_clarity')
        readiness = signals.get('roadmap_readiness')
        class_cov = signals.get('classification_coverage')

        gate_passed = ci <= 0.7
        conditions = [
            {"check": "codebase_intelligence <= 0.7", "threshold": 0.7,
             "actual": ci, "passed": gate_passed},
            {"check": "domain_clarity is Unknown/None", "threshold": "known domain",
             "actual": domain,
             "passed": domain is None or domain == 'Unknown'},
            {"check": "roadmap_readiness < 50", "threshold": 50,
             "actual": readiness,
             "passed": readiness is not None and readiness < 50},
            {"check": "classification_coverage < 0.5", "threshold": 0.5,
             "actual": class_cov,
             "passed": class_cov is not None and class_cov < 0.5},
        ]

        reason = (
            f"ci={ci} <= 0.7, computing severity"
            if gate_passed
            else f"Gate failed: codebase_intelligence={ci} > 0.7"
        )

        return {
            "detector": "purpose_vacuum",
            "gate": "codebase_intelligence <= 0.7",
            "conditions": conditions,
            "active_conditions": sum(1 for c in conditions if c["passed"]),
            "fired": gate_passed,
            "reason": reason,
        }

    @staticmethod
    def _trace_advisory_storm(signals: dict) -> dict:
        warn_count, rec_count = signals.get('advisory_counts', (0, 0))
        total = warn_count + rec_count

        gate_passed = total >= 15
        conditions = [
            {"check": "total_advisories >= 15", "threshold": 15,
             "actual": total, "passed": gate_passed},
        ]

        return {
            "detector": "advisory_storm",
            "gate": "total_advisories >= 15",
            "conditions": conditions,
            "active_conditions": 1 if gate_passed else 0,
            "fired": gate_passed,
            "reason": f"total={total} ({'>=15 -> fires' if gate_passed else '<15 -> silent'})",
        }

    def __repr__(self) -> str:
        status = 'dirty' if self._dirty else 'computed'
        n_signals = len(self._signals)
        n_syn = len(self._result.syndromes) if self._result else '?'
        return f'<ChemistryLab signals={n_signals} syndromes={n_syn} [{status}]>'
