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
        self._run_insights_engine()

        # Sort by severity
        sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        self.findings.sort(key=lambda f: sev_order.get(f.severity, 5))

        health_components = self._compute_health_components()
        health_score = self._compute_health_score(health_components)
        grade = self._score_to_grade(health_score)
        navigation = self._build_navigation()
        summary = self._build_executive_summary(grade, health_score, health_components)
        glossary = self._build_glossary()

        return InsightsReport(
            grade=grade,
            health_score=health_score,
            health_components=health_components,
            findings=self.findings,
            executive_summary=summary,
            navigation=navigation,
            theory_glossary=glossary,
            meta={
                'compiler_version': '1.0.0',
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

        if hotspots > 5:
            self._add(
                category='performance',
                severity='high' if hotspots > 10 else 'medium',
                title='Performance hotspots',
                description=f'{hotspots} performance hotspots detected.',
                evidence={
                    'hotspot_count': hotspots,
                    'critical_path_length': critical_path_len,
                    'critical_path_cost': critical_path_cost,
                },
                interpretation=f'{hotspots} nodes are predicted performance bottlenecks based on complexity and call frequency.',
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
        return min(10.0, ci * 12)  # 0.85 -> 10.2 capped at 10

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
