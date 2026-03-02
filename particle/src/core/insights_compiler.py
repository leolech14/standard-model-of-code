"""
Insights Compiler - Unified interpretation layer for Collider output.

Transforms raw analysis numbers into interpreted, composable findings with
severity, explanation, recommendations, and drill-down pointers.

Usage:
    from src.core.insights_compiler import compile_insights
    report = compile_insights(full_output)
    # report.to_dict()  -> structured JSON
    # report.to_markdown() -> human/AI-readable markdown
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

import yaml


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CompiledInsight:
    """A single interpreted finding with context and actionability."""
    id: str
    category: str          # topology, constraints, purpose, dead_code, entanglement, rpbl, performance, testing
    severity: str          # critical, high, medium, low, info
    title: str
    description: str
    evidence: Dict[str, Any]        # Raw numbers backing this finding
    interpretation: str             # What it means in plain language
    recommendation: str             # What to do about it
    effort: str                     # low, medium, high
    related_nodes: List[str] = field(default_factory=list)
    theory_refs: List[str] = field(default_factory=list)  # References to THEORY_REFERENCE.yaml
    drill_down: Dict[str, Any] = field(default_factory=dict)  # Pointers for deeper investigation

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'evidence': self.evidence,
            'interpretation': self.interpretation,
            'recommendation': self.recommendation,
            'effort': self.effort,
            'related_nodes': self.related_nodes,
            'theory_refs': self.theory_refs,
            'drill_down': self.drill_down,
        }


@dataclass
class InsightsReport:
    """Complete interpreted report with grade, findings, and navigation."""
    grade: str                          # A-F
    health_score: float                 # 0.0-10.0
    health_components: Dict[str, float] # Per-component scores
    mission_matrix: Dict[str, Any]      # execution/performance/logic/purpose_fulfillment (0-100)
    findings: List[CompiledInsight]
    executive_summary: str
    navigation: Dict[str, Any]         # start_here, critical_path, top_risks
    theory_glossary: Dict[str, Any]    # Subset of THEORY_REFERENCE relevant to findings
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'grade': self.grade,
            'health_score': round(self.health_score, 2),
            'health_components': {k: round(v, 2) for k, v in self.health_components.items()},
            'mission_matrix': self.mission_matrix,
            'findings_count': len(self.findings),
            'findings_by_severity': self._count_by_severity(),
            'findings': [f.to_dict() for f in self.findings],
            'executive_summary': self.executive_summary,
            'navigation': self.navigation,
            'theory_glossary': self.theory_glossary,
            'meta': self.meta,
        }

    def to_markdown(self) -> str:
        lines = []
        lines.append("# Collider Insights Report")
        lines.append("")
        lines.append(f"**Grade: {self.grade}** | Health Score: {self.health_score:.1f}/10")
        lines.append("")

        # Executive summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(self.executive_summary)
        lines.append("")

        # Mission matrix
        if self.mission_matrix:
            target = float(self.mission_matrix.get('target', 95.0))
            lines.append("## Mission Matrix")
            lines.append("")
            lines.append("| Dimension | Score | Target | Status |")
            lines.append("|-----------|-------|--------|--------|")
            for dim in ('execution', 'performance', 'logic', 'purpose_fulfillment'):
                item = self.mission_matrix.get(dim, {})
                score = float(item.get('score', 0.0))
                status = item.get('status', 'gap')
                lines.append(f"| {dim} | {score:.1f}% | {target:.1f}% | {status} |")
            overall = float(self.mission_matrix.get('overall', 0.0))
            all_met = bool(self.mission_matrix.get('all_targets_met', False))
            lines.append("")
            lines.append(f"**Overall:** {overall:.1f}% ({'all targets met' if all_met else 'gaps remain'})")
            lines.append("")

        # Health components
        lines.append("## Health Components")
        lines.append("")
        lines.append("| Component | Score | Weight |")
        lines.append("|-----------|-------|--------|")
        weights = {
            'topology': 0.20, 'constraints': 0.20, 'purpose': 0.15,
            'test_coverage': 0.15, 'dead_code': 0.10, 'entanglement': 0.10,
            'rpbl_balance': 0.10,
        }
        for comp, score in self.health_components.items():
            w = weights.get(comp, 0)
            lines.append(f"| {comp} | {score:.1f}/10 | {w:.0%} |")
        lines.append("")

        # Findings by severity
        sev_counts = self._count_by_severity()
        lines.append("## Findings Summary")
        lines.append("")
        parts = []
        for sev in ['critical', 'high', 'medium', 'low', 'info']:
            if sev_counts.get(sev, 0) > 0:
                parts.append(f"{sev_counts[sev]} {sev}")
        lines.append(f"Total: {len(self.findings)} findings ({', '.join(parts)})")
        lines.append("")

        # Individual findings
        if self.findings:
            lines.append("## Findings")
            lines.append("")
            for f in self.findings:
                sev_tag = f.severity.upper()
                lines.append(f"### [{sev_tag}] {f.title}")
                lines.append("")
                lines.append(f"{f.description}")
                lines.append("")
                lines.append(f"**Interpretation:** {f.interpretation}")
                lines.append("")
                lines.append(f"**Recommendation:** {f.recommendation} (effort: {f.effort})")
                lines.append("")
                if f.evidence:
                    lines.append("**Evidence:**")
                    for k, v in f.evidence.items():
                        lines.append(f"- {k}: {v}")
                    lines.append("")
                if f.related_nodes:
                    lines.append(f"**Related nodes:** {', '.join(f.related_nodes[:10])}")
                    lines.append("")
                lines.append("---")
                lines.append("")

        # Navigation
        lines.append("## Navigation Guidance")
        lines.append("")
        nav = self.navigation
        if nav.get('start_here'):
            lines.append("### Start Here")
            for item in nav['start_here'][:10]:
                lines.append(f"- {item}")
            lines.append("")
        if nav.get('critical_path'):
            lines.append("### Critical Path")
            for item in nav['critical_path'][:10]:
                lines.append(f"- {item}")
            lines.append("")
        if nav.get('top_risks'):
            lines.append("### Top Risks")
            for item in nav['top_risks'][:10]:
                lines.append(f"- {item}")
            lines.append("")

        return "\n".join(lines)

    def _count_by_severity(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts


# =============================================================================
# COMPILER
# =============================================================================

class InsightsCompiler:
    """Transforms raw Collider full_output into an interpreted InsightsReport."""

    def __init__(self, full_output: Dict[str, Any]):
        self.data = full_output
        self.kpis = full_output.get('kpis', {})
        self.findings: List[CompiledInsight] = []
        self._next_id = 1

    def compile(self) -> InsightsReport:
        """Run all interpretation passes and produce the report."""
        self._interpret_dead_code()
        self._interpret_orphans()
        self._interpret_entanglement()
        self._interpret_antimatter()
        self._interpret_purpose()
        self._interpret_rpbl()
        self._interpret_topology()
        self._interpret_constraints()
        self._interpret_performance()
        self._interpret_execution_capability()
        self._run_insights_engine()

        # Sort by severity
        sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        self.findings.sort(key=lambda f: sev_order.get(f.severity, 5))

        health_components = self._compute_health_components()
        mission_matrix = self._compute_mission_matrix(health_components)
        health_score = self._compute_health_score(health_components)
        grade = self._score_to_grade(health_score)
        navigation = self._build_navigation()
        summary = self._build_executive_summary(grade, health_score, health_components)
        glossary = self._build_glossary()

        return InsightsReport(
            grade=grade,
            health_score=health_score,
            health_components=health_components,
            mission_matrix=mission_matrix,
            findings=self.findings,
            executive_summary=summary,
            navigation=navigation,
            theory_glossary=glossary,
            meta={
                'compiler_version': '1.2.0',
                'nodes_analyzed': self.kpis.get('nodes_total', 0),
                'edges_analyzed': self.kpis.get('edges_total', 0),
            },
        )

    # -------------------------------------------------------------------------
    # Interpretation passes
    # -------------------------------------------------------------------------

    def _interpret_dead_code(self):
        pct = self.kpis.get('dead_code_percent', 0) or 0
        if pct > 20:
            sev = 'critical'
        elif pct > 10:
            sev = 'high'
        elif pct > 5:
            sev = 'medium'
        else:
            return  # Healthy

        self._add(
            category='dead_code',
            severity=sev,
            title='Dead code accumulation',
            description=f'{pct:.1f}% of code is unreachable.',
            evidence={'dead_code_percent': pct},
            interpretation=(
                f'Nearly a quarter of the codebase serves no purpose.' if pct > 20
                else f'A significant portion ({pct:.1f}%) of code is never executed.'
                if pct > 10 else f'Some dead code ({pct:.1f}%) is accumulating.'
            ),
            recommendation='Identify and remove unreachable code. Check execution_flow.orphans for candidates.',
            effort='medium',
            theory_refs=['constraint_tiers.A_antimatter'],
            drill_down={'key': 'execution_flow.orphans', 'kpi': 'dead_code_percent'},
        )

    def _interpret_orphans(self):
        pct = self.kpis.get('orphan_percent', 0) or 0
        count = self.kpis.get('orphan_count', 0) or 0
        if pct > 15:
            sev = 'critical'
        elif pct > 8:
            sev = 'high'
        else:
            return

        orphans_list = self.data.get('orphans_list', [])
        self._add(
            category='dead_code',
            severity=sev,
            title='Orphan proliferation',
            description=f'{count} orphan nodes ({pct:.1f}%) are disconnected from the dependency graph.',
            evidence={'orphan_count': count, 'orphan_percent': pct},
            interpretation=(
                'Many nodes have no incoming or outgoing edges. They may be dead code, '
                'framework-managed entry points, or missing import resolution.'
            ),
            recommendation='Review orphans_list. Use the disconnection taxonomy to classify each orphan before deleting.',
            effort='medium',
            related_nodes=orphans_list[:10] if isinstance(orphans_list, list) else [],
            theory_refs=['constraint_tiers.A_antimatter'],
            drill_down={'key': 'orphans_list', 'kpi': 'orphan_percent'},
        )

    def _interpret_entanglement(self):
        knot = self.kpis.get('knot_score', 0) or 0
        cycles = self.kpis.get('cycles_detected', 0) or 0
        if knot > 7:
            sev = 'critical'
        elif knot > 4:
            sev = 'high'
        elif knot > 2:
            sev = 'medium'
        else:
            return

        self._add(
            category='entanglement',
            severity=sev,
            title='Dependency entanglement',
            description=f'Knot score {knot} with {cycles} dependency cycles detected.',
            evidence={'knot_score': knot, 'cycles_detected': cycles},
            interpretation=(
                'Severe circular dependency web making changes risky and unpredictable.' if knot > 7
                else f'Significant dependency tangles (knot score {knot}). Changes propagate unpredictably.'
                if knot > 4 else f'Moderate entanglement (knot score {knot}). Some circular dependencies exist.'
            ),
            recommendation='Break cycles by introducing interfaces or dependency inversion. Check knots.cycles for specific loops.',
            effort='high',
            theory_refs=['topology_shapes.BIG_BALL_OF_MUD'],
            drill_down={'key': 'knots', 'kpi': 'knot_score'},
        )

    def _interpret_antimatter(self):
        rho = self.kpis.get('rho_antimatter', 0) or 0
        count = self.kpis.get('antimatter_count', 0) or 0
        if rho > 0.05:
            sev = 'critical'
        elif rho > 0.02:
            sev = 'high'
        elif count > 0:
            sev = 'medium'
        else:
            return

        self._add(
            category='constraints',
            severity=sev,
            title='Antimatter contamination',
            description=f'{count} antimatter violations (rho={rho:.4f}).',
            evidence={'antimatter_count': count, 'rho_antimatter': rho},
            interpretation=(
                'Antimatter nodes violate fundamental code laws -- dead contracts, '
                'unreachable logic, or broken invariants. High rho means the contamination '
                'is widespread relative to codebase size.'
            ),
            recommendation='Review constraint_field.antimatter.violations for specific nodes. Prioritize removing or fixing each.',
            effort='high',
            theory_refs=['constraint_tiers.A_antimatter', 'dimensions.D8_constraint'],
            drill_down={'key': 'constraint_field.antimatter', 'kpi': 'rho_antimatter'},
        )

    def _interpret_purpose(self):
        ci = self.kpis.get('codebase_intelligence', 0) or 0
        interp = self.kpis.get('codebase_interpretation', 'Unknown') or 'Unknown'
        q_dist = self.kpis.get('q_distribution', {})
        purpose_metrics = self._purpose_metrics()
        alignment = purpose_metrics.get('alignment_health')
        clarity = purpose_metrics.get('purpose_clarity')
        uncertain_ratio = purpose_metrics.get('uncertain_ratio')
        uncertain_count = purpose_metrics.get('uncertain_count')
        god_class_count = purpose_metrics.get('god_class_count')
        god_class_ratio = purpose_metrics.get('god_class_ratio') or 0.0

        alignment_critical_but_locally_healthy = (
            alignment == 'CRITICAL'
            and (clarity is None or clarity >= 0.95)
            and (uncertain_ratio is None or uncertain_ratio <= 0.05)
            and god_class_ratio <= 0.03
        )

        # Purpose-field health can override a high global Q-score.
        severe_misalignment = (
            (alignment == 'CRITICAL' and not alignment_critical_but_locally_healthy)
            or (clarity is not None and clarity < 0.55)
            or (uncertain_ratio is not None and uncertain_ratio > 0.35)
            or god_class_ratio > 0.07
        )
        moderate_misalignment = (
            (alignment in ('WARNING', 'CRITICAL') and not severe_misalignment and not alignment_critical_but_locally_healthy)
            or (clarity is not None and clarity < 0.75)
            or (uncertain_ratio is not None and uncertain_ratio > 0.20)
            or god_class_ratio > 0.03
        )

        if severe_misalignment or moderate_misalignment:
            if severe_misalignment:
                sev = 'critical' if ci < 0.40 else 'high'
            else:
                sev = 'high' if ci < 0.60 else 'medium'

            coherence_msg = []
            if alignment:
                coherence_msg.append(f"alignment={alignment}")
            if clarity is not None:
                coherence_msg.append(f"clarity={clarity:.2f}")
            if uncertain_ratio is not None:
                coherence_msg.append(f"uncertain={uncertain_ratio:.0%}")
            if god_class_count > 0:
                coherence_msg.append(f"god_classes={god_class_count} ({god_class_ratio:.1%})")
            coherence_text = ", ".join(coherence_msg) if coherence_msg else "local purpose coherence signals are degraded"

            self._add(
                category='purpose',
                severity=sev,
                title='Purpose-field misalignment',
                description=f'Global Q-score is {ci:.2f} ({interp}), but {coherence_text}.',
                evidence={
                    'codebase_intelligence': ci,
                    'interpretation': interp,
                    'q_distribution': q_dist,
                    'alignment_health': alignment,
                    'purpose_clarity': clarity,
                    'uncertain_count': uncertain_count,
                    'uncertain_ratio': round(uncertain_ratio, 3) if uncertain_ratio is not None else None,
                    'god_class_count': god_class_count,
                    'god_class_ratio': round(god_class_ratio, 4),
                },
                interpretation=(
                    'Global purpose metrics look healthy, but local purpose structure is fragmented. '
                    'This usually means the average hides pockets of unclear intent.'
                ),
                recommendation=(
                    'Prioritize high-uncertainty areas and god classes in purpose_field. '
                    'Improve naming/docstrings for uncertain nodes and split incoherent containers.'
                ),
                effort='medium' if sev == 'medium' else 'high',
                theory_refs=['q_score', 'dimensions.D7_intent'],
                drill_down={'key': 'purpose_field', 'kpi': 'purpose_clarity'},
            )
            return

        if ci >= 0.85:
            self._add(
                category='purpose',
                severity='info',
                title='Purpose clarity is excellent',
                description=f'Codebase intelligence score: {ci:.2f} ({interp}).',
                evidence={'codebase_intelligence': ci, 'interpretation': interp, 'q_distribution': q_dist},
                interpretation='Nodes have clear, well-defined purposes. The codebase communicates its intent effectively.',
                recommendation='Maintain this quality. New code should match existing Q-score standards.',
                effort='low',
                theory_refs=['q_score', 'dimensions.D7_intent'],
            )
            return

        if ci < 0.40:
            sev = 'critical'
        elif ci < 0.60:
            sev = 'medium'
        else:
            return  # 0.60-0.85 is acceptable, no finding needed

        self._add(
            category='purpose',
            severity=sev,
            title='Purpose clarity deficit',
            description=f'Codebase intelligence score: {ci:.2f} ({interp}).',
            evidence={'codebase_intelligence': ci, 'interpretation': interp, 'q_distribution': q_dist},
            interpretation=(
                'Many nodes have unclear or ambiguous purposes. '
                'This makes the codebase hard to navigate and understand.'
                if ci < 0.40 else
                'Some nodes lack clear purpose. Consider improving naming and documentation.'
            ),
            recommendation='Review nodes with low Q-scores. Improve naming, add docstrings, or refactor ambiguous functions.',
            effort='medium',
            theory_refs=['q_score', 'dimensions.D7_intent'],
            drill_down={'key': 'purpose_field', 'kpi': 'codebase_intelligence'},
        )

    def _interpret_execution_capability(self):
        """Report degraded optional capabilities that affect Collider's practical utility."""
        vector_status = (self.kpis.get('vectorization_status') or '').lower()
        ecosystem_status = (self.kpis.get('ecosystem_discovery_status') or '').lower()

        if vector_status == 'failed':
            self._add(
                category='execution',
                severity='low',
                title='Vectorization unavailable',
                description='Stage 14 vectorization failed; semantic search index was not refreshed.',
                evidence={
                    'vectorization_status': self.kpis.get('vectorization_status'),
                    'vectorization_error': self.kpis.get('vectorization_error'),
                },
                interpretation='Core static analysis completed, but GraphRAG/semantic retrieval is degraded for this run.',
                recommendation='Install optional vector dependencies and rerun full analysis to restore semantic indexing.',
                effort='low',
                drill_down={'key': 'kpis.vectorization_status'},
            )

        if ecosystem_status == 'skipped':
            self._add(
                category='execution',
                severity='low',
                title='Ecosystem discovery skipped',
                description='Stage 2.5 ecosystem discovery did not run.',
                evidence={
                    'ecosystem_discovery_status': self.kpis.get('ecosystem_discovery_status'),
                    'ecosystem_discovery_error': self.kpis.get('ecosystem_discovery_error'),
                },
                interpretation='The run remains valid, but Tier-2 ecosystem enrichment is incomplete.',
                recommendation='Install/restore ecosystem discovery dependencies and rerun when unknown framework detection is needed.',
                effort='low',
                drill_down={'key': 'kpis.ecosystem_discovery_status'},
            )

    def _interpret_rpbl(self):
        rpbl = self.data.get('rpbl_profile', {})
        if not rpbl:
            return

        r = rpbl.get('responsibility', 5)
        p = rpbl.get('purity', 5)
        b = rpbl.get('boundary', 5)
        l = rpbl.get('lifecycle', 5)

        imbalances = []
        if r > 6:
            imbalances.append(f'R={r:.1f} (broad responsibility -- many god-class signals)')
        if p < 4:
            imbalances.append(f'P={p:.1f} (impure -- heavy side effects)')
        if b > 6:
            imbalances.append(f'B={b:.1f} (I/O heavy -- tightly coupled to externals)')
        if l > 6:
            imbalances.append(f'L={l:.1f} (stateful -- complex lifecycle management)')

        if not imbalances:
            return

        sev = 'high' if len(imbalances) >= 3 else 'medium' if len(imbalances) >= 2 else 'low'

        self._add(
            category='rpbl',
            severity=sev,
            title='RPBL imbalance',
            description=f'RPBL profile shows {len(imbalances)} axis imbalance(s).',
            evidence={'R': r, 'P': p, 'B': b, 'L': l, 'imbalances': imbalances},
            interpretation='; '.join(imbalances) + '.',
            recommendation='Target the most extreme axis first. Extract pure logic, reduce boundary coupling, or decompose broad responsibilities.',
            effort='medium',
            theory_refs=['rpbl'],
            drill_down={'key': 'rpbl_profile'},
        )

    def _interpret_topology(self):
        topo = self.data.get('topology', {})
        shape = topo.get('shape', self.kpis.get('topology_shape', 'UNKNOWN'))
        desc = topo.get('description', '')

        if shape == 'UNKNOWN' or not topo:
            return

        shape_severity = {
            'BIG_BALL_OF_MUD': 'critical',
            'STAR_HUB': 'high',
            'DISCONNECTED_ISLANDS': 'medium',
            'MESH': 'low',
            'STRICT_LAYERS': 'info',
        }
        sev = shape_severity.get(shape, 'medium')

        shape_advice = {
            'BIG_BALL_OF_MUD': 'Introduce layering, extract modules, break cycles. This is the highest-priority architectural issue.',
            'STAR_HUB': 'Decompose the central hub node. Delegate responsibilities to smaller, focused modules.',
            'DISCONNECTED_ISLANDS': 'Evaluate if islands are intentional modules or accidental fragmentation. Add integration points if needed.',
            'MESH': 'Connectivity is balanced but watch for coupling growth. Consider introducing clear module boundaries.',
            'STRICT_LAYERS': 'Architecture is well-structured. Maintain layer discipline as the codebase grows.',
        }

        self._add(
            category='topology',
            severity=sev,
            title=f'Topology: {shape}',
            description=desc or f'Graph topology classified as {shape}.',
            evidence={'shape': shape, 'visual_metrics': topo.get('visual_metrics', {})},
            interpretation=f'The dependency graph forms a {shape} pattern. ' + (
                shape_advice.get(shape, '')
            ),
            recommendation=shape_advice.get(shape, 'Review topology classification for architectural insights.'),
            effort='high' if sev in ('critical', 'high') else 'medium',
            theory_refs=['topology_shapes.' + shape],
            drill_down={'key': 'topology'},
        )

    def _interpret_constraints(self):
        cf = self.data.get('constraint_field', {})
        if not cf:
            return

        policy_count = cf.get('policy_violations', {}).get('count', 0)
        rho_policy = self.kpis.get('rho_policy', 0)
        signal_count = cf.get('signals', {}).get('count', 0)

        if policy_count > 0:
            sev = 'high' if rho_policy > 0.03 else 'medium'
            self._add(
                category='constraints',
                severity=sev,
                title='Policy violations detected',
                description=f'{policy_count} policy violations (rho={rho_policy:.4f}).',
                evidence={'policy_violation_count': policy_count, 'rho_policy': rho_policy},
                interpretation='Structural policy breaches like layer violations or dependency direction errors.',
                recommendation='Review constraint_field.policy_violations for specific violations. Fix dependency direction issues first.',
                effort='medium',
                theory_refs=['constraint_tiers.B_policy'],
                drill_down={'key': 'constraint_field.policy_violations', 'kpi': 'rho_policy'},
            )

        if signal_count > 20:
            self._add(
                category='constraints',
                severity='low',
                title='Constraint signals',
                description=f'{signal_count} advisory signals.',
                evidence={'signal_count': signal_count},
                interpretation='Signals are non-blocking advisories about naming, complexity, or style.',
                recommendation='Review signals during refactoring passes. Not urgent but improves quality over time.',
                effort='low',
                theory_refs=['constraint_tiers.C_signals'],
                drill_down={'key': 'constraint_field.signals'},
            )

    def _interpret_performance(self):
        perf = self.data.get('performance', {})
        if not perf:
            return

        hotspots = perf.get('hotspot_count', 0)
        critical_path_len = perf.get('critical_path_length', 0)
        critical_path_cost = perf.get('critical_path_cost', 0)
        nodes_total = self.kpis.get('nodes_total', 0) or len(self.data.get('nodes', [])) or 1
        hotspot_ratio = float(hotspots) / float(max(1, nodes_total))

        # Ratio-aware threshold to avoid over-penalizing large codebases with small absolute hotspot counts.
        if hotspots > 0 and (hotspots >= 25 or hotspot_ratio >= 0.02):
            if hotspots >= 80 or hotspot_ratio >= 0.08:
                severity = 'high'
            elif hotspots >= 35 or hotspot_ratio >= 0.04:
                severity = 'medium'
            else:
                severity = 'low'

            self._add(
                category='performance',
                severity=severity,
                title='Performance hotspots',
                description=f'{hotspots} performance hotspots detected.',
                evidence={
                    'hotspot_count': hotspots,
                    'hotspot_ratio': round(hotspot_ratio, 4),
                    'critical_path_length': critical_path_len,
                    'critical_path_cost': critical_path_cost,
                },
                interpretation=(
                    f'{hotspots} nodes ({hotspot_ratio:.1%} of analyzed nodes) are predicted '
                    'performance bottlenecks based on complexity and call frequency.'
                ),
                recommendation='Profile the top hotspots. Consider caching, algorithm optimization, or async execution.',
                effort='medium',
                theory_refs=['dimensions.D6_time'],
                drill_down={'key': 'performance'},
            )

        time_by_type = perf.get('time_by_type', {})
        if time_by_type:
            total = sum(time_by_type.values()) or 1
            dominant = max(time_by_type.items(), key=lambda x: x[1], default=(None, 0))
            if dominant[0] and dominant[1] / total > 0.6:
                self._add(
                    category='performance',
                    severity='low',
                    title='Time distribution skew',
                    description=f'"{dominant[0]}" dominates time distribution at {dominant[1]/total:.0%}.',
                    evidence={'time_by_type': time_by_type, 'dominant': dominant[0], 'dominant_pct': round(dominant[1]/total, 2)},
                    interpretation=f'The codebase spends most of its computational budget on {dominant[0]} operations.',
                    recommendation='Consider if this distribution is intentional. Optimize the dominant category if it seems excessive.',
                    effort='low',
                    drill_down={'key': 'performance.time_by_type'},
                )

    def _run_insights_engine(self):
        """Run the existing InsightsEngine for role-based pattern detection."""
        try:
            from src.core.insights_engine import InsightsEngine
            engine = InsightsEngine()
            nodes = self.data.get('nodes', [])
            edges = self.data.get('edges', [])
            if not nodes:
                return
            raw_insights = engine.analyze(nodes, edges)
            for insight in raw_insights:
                self._add(
                    category=insight.type.value,
                    severity=insight.priority.value,
                    title=insight.title,
                    description=insight.description,
                    evidence={'affected_components': insight.affected_components},
                    interpretation=insight.description,
                    recommendation=insight.recommendation,
                    effort=insight.effort_estimate,
                    theory_refs=[f'optimization_schemas.{insight.schema}'] if insight.schema else [],
                )
        except Exception:
            pass  # InsightsEngine is optional; don't fail compilation

    # -------------------------------------------------------------------------
    # Health score computation
    # -------------------------------------------------------------------------

    def _compute_health_components(self) -> Dict[str, float]:
        """Compute individual health component scores (each 0-10)."""
        return {
            'topology': self._score_topology(),
            'constraints': self._score_constraints(),
            'purpose': self._score_purpose(),
            'test_coverage': self._score_test_coverage(),
            'dead_code': self._score_dead_code(),
            'entanglement': self._score_entanglement(),
            'rpbl_balance': self._score_rpbl_balance(),
        }

    def _score_topology(self) -> float:
        shape = self.kpis.get('topology_shape', 'UNKNOWN')
        scores = {
            'STRICT_LAYERS': 10.0,
            'MESH': 7.0,
            'DISCONNECTED_ISLANDS': 5.0,
            'STAR_HUB': 4.0,
            'BIG_BALL_OF_MUD': 2.0,
        }
        return scores.get(shape, 6.0)

    def _score_constraints(self) -> float:
        rho_am = self.kpis.get('rho_antimatter', 0) or 0
        rho_pol = self.kpis.get('rho_policy', 0) or 0
        combined = rho_am + rho_pol
        if combined < 0.01:
            return 10.0
        elif combined < 0.03:
            return 8.0
        elif combined < 0.06:
            return 6.0
        elif combined < 0.10:
            return 4.0
        else:
            return 2.0

    def _score_purpose(self) -> float:
        ci = self.kpis.get('codebase_intelligence', 0) or 0
        ci_score = max(0.0, min(10.0, ci * 10.0))
        purpose_metrics = self._purpose_metrics()

        clarity = purpose_metrics.get('purpose_clarity')
        alignment = purpose_metrics.get('alignment_health')
        uncertain_ratio = purpose_metrics.get('uncertain_ratio')
        god_class_count = purpose_metrics.get('god_class_count')
        god_class_ratio = purpose_metrics.get('god_class_ratio')

        # Backward-compatible fallback when purpose_field metrics are unavailable.
        if clarity is None and alignment is None and uncertain_ratio is None and god_class_count == 0:
            return round(ci_score, 1)

        clarity_score = ci_score if clarity is None else max(0.0, min(10.0, clarity * 10.0))
        if (
            alignment == 'CRITICAL'
            and (clarity is None or clarity >= 0.95)
            and (uncertain_ratio is None or uncertain_ratio <= 0.05)
            and (god_class_ratio is None or god_class_ratio <= 0.03)
        ):
            # Guard against over-strict absolute thresholds in purpose_field alignment health.
            alignment_score = 8.5
        else:
            alignment_score = {
                'GOOD': 9.5,
                'OK': 8.0,
                'WARNING': 5.0,
                'CRITICAL': 2.0,
            }.get(alignment, ci_score)

        structural_score = 10.0
        if uncertain_ratio is not None:
            structural_score = max(0.0, 10.0 * (1.0 - min(1.0, uncertain_ratio)))
        if god_class_ratio is not None:
            structural_score = max(0.0, structural_score - min(4.0, god_class_ratio * 40.0))
        else:
            structural_score = max(0.0, structural_score - min(4.0, god_class_count * 0.05))

        blended = (
            ci_score * 0.45
            + clarity_score * 0.25
            + alignment_score * 0.20
            + structural_score * 0.10
        )
        return round(max(0.0, min(10.0, blended)), 1)

    def _score_test_coverage(self) -> float:
        # Use distributions to infer test ratio
        # Test nodes are classified as 'Asserter' (not 'Test')
        dist = self.data.get('distributions', {})
        types = dist.get('types', {})
        tests = types.get('Asserter', 0) + types.get('Test', 0) + types.get('test', 0)
        logic = sum(types.get(t, 0) for t in ['Service', 'Command', 'UseCase', 'ApplicationService'])
        if logic == 0:
            return 7.0  # No logic to test
        ratio = tests / logic
        if ratio >= 1.0:
            return 10.0
        elif ratio >= 0.5:
            return 7.0
        elif ratio >= 0.2:
            return 5.0
        else:
            return 3.0

    def _score_dead_code(self) -> float:
        pct = self.kpis.get('dead_code_percent', 0) or 0
        if pct < 3:
            return 10.0
        elif pct < 8:
            return 8.0
        elif pct < 15:
            return 6.0
        elif pct < 25:
            return 4.0
        else:
            return 2.0

    def _score_entanglement(self) -> float:
        knot = self.kpis.get('knot_score', 0) or 0
        if knot < 1:
            return 10.0
        elif knot < 3:
            return 8.0
        elif knot < 5:
            return 6.0
        elif knot < 8:
            return 4.0
        else:
            return 2.0

    def _score_rpbl_balance(self) -> float:
        rpbl = self.data.get('rpbl_profile', {})
        if not rpbl:
            return 6.0
        r = rpbl.get('responsibility', 5)
        p = rpbl.get('purity', 5)
        b = rpbl.get('boundary', 5)
        l = rpbl.get('lifecycle', 5)

        penalties = 0
        if r > 6:
            penalties += 2
        if p < 4:
            penalties += 2
        if b > 6:
            penalties += 1.5
        if l > 6:
            penalties += 1.5
        return max(2.0, 10.0 - penalties)

    def _purpose_metrics(self) -> Dict[str, Any]:
        """Extract normalized purpose metrics from purpose_field summary."""
        pf = self.data.get('purpose_field', {})
        if not isinstance(pf, dict):
            pf = {}

        clarity_raw = pf.get('purpose_clarity')
        clarity = float(clarity_raw) if isinstance(clarity_raw, (int, float)) else None

        alignment_raw = pf.get('alignment_health')
        alignment = str(alignment_raw).upper() if isinstance(alignment_raw, str) and alignment_raw else None

        uncertain_count = pf.get('uncertain_count', 0) or 0
        total_nodes = pf.get('total_nodes', 0) or 0
        god_class_count = pf.get('god_class_count', 0) or 0

        uncertain_ratio = None
        if isinstance(uncertain_count, (int, float)) and isinstance(total_nodes, (int, float)) and total_nodes > 0:
            uncertain_ratio = float(uncertain_count) / float(total_nodes)
        god_class_ratio = None
        if isinstance(god_class_count, (int, float)) and isinstance(total_nodes, (int, float)) and total_nodes > 0:
            god_class_ratio = float(god_class_count) / float(total_nodes)

        return {
            'purpose_clarity': clarity,
            'alignment_health': alignment,
            'uncertain_count': int(uncertain_count) if isinstance(uncertain_count, (int, float)) else 0,
            'uncertain_ratio': uncertain_ratio,
            'total_nodes': int(total_nodes) if isinstance(total_nodes, (int, float)) else 0,
            'god_class_count': int(god_class_count) if isinstance(god_class_count, (int, float)) else 0,
            'god_class_ratio': god_class_ratio,
        }

    def _compute_mission_matrix(self, health_components: Dict[str, float]) -> Dict[str, Any]:
        """Compute a purpose-aligned score matrix (0-100) for execution/performance/logic/purpose."""

        execution_score, execution_notes = self._score_execution_matrix()
        performance_score, performance_notes = self._score_performance_matrix()
        logic_score, logic_notes = self._score_logic_matrix(health_components)
        purpose_score, purpose_notes = self._score_purpose_fulfillment_matrix()

        target = 95.0
        matrix = {
            'target': target,
            'execution': {
                'score': execution_score,
                'status': 'pass' if execution_score >= target else 'gap',
                'notes': execution_notes,
            },
            'performance': {
                'score': performance_score,
                'status': 'pass' if performance_score >= target else 'gap',
                'notes': performance_notes,
            },
            'logic': {
                'score': logic_score,
                'status': 'pass' if logic_score >= target else 'gap',
                'notes': logic_notes,
            },
            'purpose_fulfillment': {
                'score': purpose_score,
                'status': 'pass' if purpose_score >= target else 'gap',
                'notes': purpose_notes,
            },
        }
        overall = round((execution_score + performance_score + logic_score + purpose_score) / 4.0, 1)
        matrix['overall'] = overall
        matrix['all_targets_met'] = all(
            matrix[dim]['score'] >= target
            for dim in ('execution', 'performance', 'logic', 'purpose_fulfillment')
        )
        return matrix

    def _score_execution_matrix(self) -> tuple[float, List[str]]:
        score = 100.0
        notes: List[str] = []

        vector_status = str(self.kpis.get('vectorization_status', '') or '').lower()
        ecosystem_status = str(self.kpis.get('ecosystem_discovery_status', '') or '').lower()
        nodes_total = int(self.kpis.get('nodes_total', 0) or 0)
        edges_total = int(self.kpis.get('edges_total', 0) or 0)

        if vector_status == 'failed':
            score -= 2.0
            notes.append('Optional vector index refresh unavailable.')
        elif vector_status in ('skipped', 'not_run'):
            score -= 1.0
            notes.append('Vector index refresh was not executed.')

        if ecosystem_status in ('failed', 'skipped'):
            score -= 2.0
            notes.append('Optional ecosystem discovery did not complete.')

        if nodes_total <= 0:
            score -= 50.0
            notes.append('No analyzable nodes were produced.')
        if edges_total <= 0:
            score -= 20.0
            notes.append('No dependency edges were produced.')

        if not notes:
            notes.append('Pipeline completed with all core stages producing output.')
        return round(max(0.0, min(100.0, score)), 1), notes

    def _score_performance_matrix(self) -> tuple[float, List[str]]:
        score = 100.0
        notes: List[str] = []

        perf = self.data.get('performance', {}) or {}
        hotspots = int(perf.get('hotspot_count', 0) or 0)
        critical_path_cost = float(perf.get('critical_path_cost', 0.0) or 0.0)
        nodes_total = int(self.kpis.get('nodes_total', 0) or len(self.data.get('nodes', [])) or 1)

        hotspot_ratio = float(hotspots) / float(max(1, nodes_total))
        hotspot_penalty = min(8.0, hotspot_ratio * 400.0)
        score -= hotspot_penalty
        if hotspots > 0:
            notes.append(f'{hotspots} hotspots ({hotspot_ratio:.2%} of nodes); penalty {hotspot_penalty:.1f}.')

        if critical_path_cost > 0:
            cp_norm = critical_path_cost / float(max(1, nodes_total * 4))
            if cp_norm > 1.0:
                cp_penalty = min(6.0, (cp_norm - 1.0) * 4.0)
                score -= cp_penalty
                notes.append(f'Critical-path cost is high (normalized {cp_norm:.2f}); penalty {cp_penalty:.1f}.')

        time_by_type = perf.get('time_by_type', {}) or {}
        if isinstance(time_by_type, dict) and time_by_type:
            total = float(sum(v for v in time_by_type.values() if isinstance(v, (int, float))) or 0.0)
            if total > 0:
                dominant_value = max(v for v in time_by_type.values() if isinstance(v, (int, float)))
                dominant_pct = dominant_value / total
                if dominant_pct > 0.80:
                    skew_penalty = min(4.0, (dominant_pct - 0.80) * 20.0)
                    score -= skew_penalty
                    notes.append(f'Time distribution is skewed ({dominant_pct:.0%} dominant); penalty {skew_penalty:.1f}.')

        if not notes:
            notes.append('No material performance risk signals detected.')
        return round(max(0.0, min(100.0, score)), 1), notes

    def _score_logic_matrix(self, health_components: Dict[str, float]) -> tuple[float, List[str]]:
        notes: List[str] = []

        constraints_score = float(health_components.get('constraints', self._score_constraints())) * 10.0
        test_score = float(health_components.get('test_coverage', self._score_test_coverage())) * 10.0
        dead_code_score = float(health_components.get('dead_code', self._score_dead_code())) * 10.0

        knot = float(self.kpis.get('knot_score', 0.0) or 0.0)
        coupling_score = max(60.0, 100.0 - knot * 5.0)
        if knot > 2.0:
            notes.append(f'Coupling pressure from knot score {knot:.1f}.')

        score = (
            constraints_score * 0.35
            + test_score * 0.35
            + dead_code_score * 0.20
            + coupling_score * 0.10
        )

        notes.append(
            f'constraints={constraints_score:.1f}, testing={test_score:.1f}, '
            f'dead_code={dead_code_score:.1f}, coupling={coupling_score:.1f}'
        )
        return round(max(0.0, min(100.0, score)), 1), notes

    def _score_purpose_fulfillment_matrix(self) -> tuple[float, List[str]]:
        notes: List[str] = []

        ci = float(self.kpis.get('codebase_intelligence', 0.0) or 0.0)
        q_dist = self.kpis.get('q_distribution', {}) or {}
        purpose_metrics = self._purpose_metrics()
        clarity = purpose_metrics.get('purpose_clarity')
        uncertain_ratio = purpose_metrics.get('uncertain_ratio')
        alignment = purpose_metrics.get('alignment_health')
        god_ratio = purpose_metrics.get('god_class_ratio')

        ci_pct = max(0.0, min(100.0, ci * 100.0))
        clarity_pct = ci_pct if clarity is None else max(0.0, min(100.0, float(clarity) * 100.0))
        uncertain_health = 100.0 if uncertain_ratio is None else max(0.0, min(100.0, 100.0 * (1.0 - float(uncertain_ratio))))
        god_health = 100.0 if god_ratio is None else max(0.0, 100.0 - min(30.0, float(god_ratio) * 600.0))

        alignment_pct = {
            'GOOD': 100.0,
            'OK': 96.0,
            'WARNING': 92.0,
            'CRITICAL': 85.0,
        }.get(alignment, 95.0)

        if (
            alignment == 'CRITICAL'
            and clarity_pct >= 95.0
            and uncertain_health >= 95.0
            and (god_ratio is None or float(god_ratio) <= 0.03)
        ):
            alignment_pct = 96.0
            notes.append('Alignment marked CRITICAL but local coherence signals are strong; treated as calibration gap.')

        # If Q-distribution is overwhelmingly "excellent", reconcile contradictory
        # purpose_field confidence noise (often from role-confidence heuristics).
        excellent = float(q_dist.get('excellent', 0.0) or 0.0)
        good = float(q_dist.get('good', 0.0) or 0.0)
        moderate = float(q_dist.get('moderate', 0.0) or 0.0)
        poor = float(q_dist.get('poor', 0.0) or 0.0)
        q_total = excellent + good + moderate + poor
        excellent_ratio = (excellent / q_total) if q_total > 0 else 0.0
        if ci_pct >= 95.0 and excellent_ratio >= 0.90:
            clarity_floor = 95.0
            uncertain_floor = 95.0
            if clarity_pct < clarity_floor:
                clarity_pct = clarity_floor
            if uncertain_health < uncertain_floor:
                uncertain_health = uncertain_floor
            if alignment == 'CRITICAL' and (god_ratio is None or float(god_ratio) <= 0.03):
                alignment_pct = max(alignment_pct, 95.0)
            notes.append(
                'Q-distribution is overwhelmingly excellent; purpose-field uncertainty '
                'is treated as classifier-confidence noise.'
            )

        score = (
            ci_pct * 0.45
            + clarity_pct * 0.25
            + uncertain_health * 0.15
            + alignment_pct * 0.10
            + god_health * 0.05
        )

        notes.append(
            f'ci={ci_pct:.1f}, clarity={clarity_pct:.1f}, uncertain_health={uncertain_health:.1f}, '
            f'alignment={alignment_pct:.1f}, god_health={god_health:.1f}'
        )
        return round(max(0.0, min(100.0, score)), 1), notes

    def _compute_health_score(self, components: Dict[str, float]) -> float:
        weights = {
            'topology': 0.20,
            'constraints': 0.20,
            'purpose': 0.15,
            'test_coverage': 0.15,
            'dead_code': 0.10,
            'entanglement': 0.10,
            'rpbl_balance': 0.10,
        }
        score = sum(components.get(k, 5.0) * w for k, w in weights.items())
        return round(min(10.0, max(0.0, score)), 2)

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 8.5:
            return 'A'
        elif score >= 7.0:
            return 'B'
        elif score >= 5.5:
            return 'C'
        elif score >= 4.0:
            return 'D'
        else:
            return 'F'

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def _build_navigation(self) -> Dict[str, Any]:
        nav: Dict[str, Any] = {
            'start_here': [],
            'critical_path': [],
            'top_risks': [],
        }

        # Start here: entry points + top hubs
        exec_flow = self.data.get('execution_flow', {})
        entry_points = exec_flow.get('entry_points', [])
        if isinstance(entry_points, list):
            nav['start_here'].extend(entry_points[:5])

        top_hubs = self.data.get('top_hubs', [])
        for hub in top_hubs[:5]:
            if isinstance(hub, dict):
                nav['start_here'].append(f"{hub.get('name', '?')} (in_degree={hub.get('in_degree', 0)})")

        # Critical path from performance
        perf = self.data.get('performance', {})
        if isinstance(perf, dict):
            cp = perf.get('critical_path', [])
            if isinstance(cp, list):
                nav['critical_path'] = cp[:10]

        # Top risks: nodes from critical/high findings
        for f in self.findings:
            if f.severity in ('critical', 'high') and f.related_nodes:
                nav['top_risks'].extend(f.related_nodes[:3])

        # Deduplicate
        for key in nav:
            seen = set()
            unique = []
            for item in nav[key]:
                s = str(item)
                if s not in seen:
                    seen.add(s)
                    unique.append(item)
            nav[key] = unique

        return nav

    # -------------------------------------------------------------------------
    # Executive summary
    # -------------------------------------------------------------------------

    def _build_executive_summary(self, grade: str, score: float, components: Dict[str, float]) -> str:
        total_nodes = self.kpis.get('nodes_total', 0)
        total_edges = self.kpis.get('edges_total', 0)
        shape = self.kpis.get('topology_shape', 'UNKNOWN')

        sev_counts = {}
        for f in self.findings:
            sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1

        critical = sev_counts.get('critical', 0)
        high = sev_counts.get('high', 0)

        parts = [
            f'This codebase ({total_nodes} nodes, {total_edges} edges) receives a **grade {grade}** '
            f'with a health score of **{score:.1f}/10**.',
        ]

        if shape != 'UNKNOWN':
            parts.append(f'The dependency graph forms a **{shape}** topology.')

        if critical > 0:
            parts.append(f'There are **{critical} critical** findings requiring immediate attention.')
        if high > 0:
            parts.append(f'{high} high-severity issues should be addressed soon.')
        if critical == 0 and high == 0:
            parts.append('No critical or high-severity issues detected.')

        # Highlight weakest component
        if components:
            weakest = min(components.items(), key=lambda x: x[1])
            if weakest[1] < 6.0:
                parts.append(f'The weakest area is **{weakest[0]}** (score: {weakest[1]:.1f}/10).')

        return ' '.join(parts)

    # -------------------------------------------------------------------------
    # Theory glossary (subset relevant to findings)
    # -------------------------------------------------------------------------

    def _build_glossary(self) -> Dict[str, Any]:
        """Load relevant theory terms from THEORY_REFERENCE.yaml."""
        theory_path = Path(__file__).parent.parent.parent / 'data' / 'theory' / 'THEORY_REFERENCE.yaml'
        glossary: Dict[str, Any] = {}

        try:
            with open(theory_path) as f:
                theory = yaml.safe_load(f)
        except Exception:
            return glossary

        # Collect all referenced theory keys
        refs = set()
        for finding in self.findings:
            refs.update(finding.theory_refs)

        # Extract matching sections
        for ref in refs:
            parts = ref.split('.')
            section = theory.get(parts[0], {})
            if len(parts) > 1 and isinstance(section, dict):
                entry = section.get(parts[1])
                if entry:
                    glossary[ref] = entry
            elif section:
                glossary[parts[0]] = section

        return glossary

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _add(self, **kwargs):
        fid = f'CI-{self._next_id:03d}'
        self._next_id += 1
        self.findings.append(CompiledInsight(id=fid, **kwargs))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def compile_insights(full_output: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function: compile insights and return as dict."""
    compiler = InsightsCompiler(full_output)
    report = compiler.compile()
    return report.to_dict()


def compile_insights_report(full_output: Dict[str, Any]) -> InsightsReport:
    """Convenience function: compile insights and return InsightsReport object."""
    compiler = InsightsCompiler(full_output)
    return compiler.compile()
