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
    category: str          # topology, constraints, purpose, dead_code, entanglement, rpbl, performance, data_flow, execution, incoherence, purpose_decomposition, gap_detection, temporal, contextome, ideome
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
        self._lab = full_output.get('_chemistry_lab')  # ChemistryLab or None

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

        # --- Extended insight generators (v2.0) ---
        self._interpret_markov()
        self._interpret_topology_deep()
        self._interpret_data_flow()
        self._interpret_graph_analytics()
        self._interpret_theory_completeness()
        self._interpret_igt_stability()
        self._interpret_semantic_roles()

        # --- Collider Trinity (v2.1) ---
        self._interpret_incoherence()
        self._interpret_purpose_decomposition()
        self._interpret_gaps()

        # --- Temporal Analysis (REH integration) ---
        self._interpret_temporal()

        # --- Contextome Intelligence (Stage 0.8) ---
        self._interpret_contextome()

        # --- Ideome Synthesis (Rosetta Stone) ---
        self._interpret_ideome()

        # --- Dark-matter feature interpreters (Collider Potential expansion) ---
        self._interpret_smart_ignore()
        self._interpret_roadmap_eval()
        self._interpret_semantics_cortex()
        self._interpret_ecosystem()
        self._interpret_dependencies_graph()
        self._interpret_advisories()
        self._interpret_file_landscape()
        self._interpret_classification_coverage()
        self._interpret_edge_diversity()
        self._interpret_codome_boundary()

        # --- Data Chemistry (cross-signal correlation) ---
        self._interpret_chemistry()

        # Sort by severity
        sev_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        self.findings.sort(key=lambda f: sev_order.get(f.severity, 5))

        # Promote high/critical findings to issues list
        issues = self._promote_findings_to_issues()

        health_components = self._compute_health_components()
        mission_matrix = self._compute_mission_matrix(health_components)
        health_score = self._compute_health_score(health_components)
        grade = self._score_to_grade(health_score)
        navigation = self._build_navigation()
        summary = self._build_executive_summary(grade, health_score, health_components)
        glossary = self._build_glossary()

        # Collect capability status (built by _interpret_execution_capability)
        cap_status = getattr(self, '_capability_status', {})

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
                'compiler_version': '2.1.0',
                'nodes_analyzed': self.kpis.get('nodes_total', 0),
                'edges_analyzed': self.kpis.get('edges_total', 0),
                'capability_status': cap_status,
                'issues': issues,
                'issue_count': len(issues),
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
        """Report degraded optional capabilities that affect Collider's practical utility.

        This is the pipeline health gate.  It checks five dimensions:
        1. LLM / AI audit status  (ollama or provider failure → warning)
        2. Vectorization status   (failed → medium, not just low)
        3. Ecosystem discovery    (skipped → medium)
        4. Freshness guard        (feedback timestamp >> analysis timestamp → stale)
        5. Publishability gate    (feedback-only without smoke/full in session)

        It also builds a ``capability_status`` summary block that downstream
        consumers (reports, dashboards, CI) can read at a glance.
        """

        cap_status: Dict[str, Any] = {}

        # --- 1. LLM / AI audit --------------------------------------------------
        llm = self.data.get('llm_enrichment') or {}
        llm_enabled = llm.get('enabled', False)
        llm_model = str(llm.get('model', 'none') or 'none').lower()
        llm_analysis = str(llm.get('analysis_status', 'not_applied') or 'not_applied').lower()
        llm_enhanced = int(llm.get('particles_enhanced', 0) or 0)

        if llm_enabled and llm_analysis != 'applied':
            # LLM was expected but didn't deliver
            cap_status['llm_audit'] = 'degraded'
            self._add(
                category='execution',
                severity='medium',
                title='LLM audit did not complete',
                description=(
                    f'LLM enrichment was enabled (model={llm_model}) but '
                    f'analysis_status={llm_analysis}, particles_enhanced={llm_enhanced}.'
                ),
                evidence={
                    'llm_enabled': llm_enabled,
                    'llm_model': llm_model,
                    'llm_analysis_status': llm_analysis,
                    'particles_enhanced': llm_enhanced,
                },
                interpretation=(
                    'The AI-powered audit stage failed or was skipped.  '
                    'Purpose classifications, code smell detection, and '
                    'architecture inference rely on this stage.  '
                    'The deterministic fallback was used, which provides '
                    'boilerplate rather than genuine analysis.'
                ),
                recommendation=(
                    'Ensure the configured LLM provider is reachable '
                    '(check ollama/vertex status).  Re-run with --llm to '
                    'restore AI-powered enrichment.'
                ),
                effort='low',
                drill_down={'key': 'llm_enrichment'},
            )
        elif not llm_enabled:
            cap_status['llm_audit'] = 'off'
        else:
            cap_status['llm_audit'] = 'ok'

        # --- 2. Vectorization ----------------------------------------------------
        vector_status = (self.kpis.get('vectorization_status') or '').lower()
        if vector_status == 'failed':
            cap_status['vectorization'] = 'failed'
            self._add(
                category='execution',
                severity='medium',
                title='Vectorization unavailable',
                description='Stage 14 vectorization failed; semantic search index was not refreshed.',
                evidence={
                    'vectorization_status': self.kpis.get('vectorization_status'),
                    'vectorization_error': self.kpis.get('vectorization_error'),
                },
                interpretation=(
                    'GraphRAG/semantic retrieval is degraded.  '
                    'Code search, similarity queries, and RAG-powered '
                    'exploration will fall back to keyword matching.'
                ),
                recommendation='Install optional vector dependencies (lancedb) and rerun full analysis.',
                effort='low',
                drill_down={'key': 'kpis.vectorization_status'},
            )
        elif vector_status in ('skipped', 'not_run'):
            cap_status['vectorization'] = 'skipped'
        else:
            cap_status['vectorization'] = 'ok'

        # --- 3. Ecosystem discovery ----------------------------------------------
        ecosystem_status = (self.kpis.get('ecosystem_discovery_status') or '').lower()
        if ecosystem_status in ('failed', 'skipped'):
            cap_status['ecosystem_discovery'] = ecosystem_status
            self._add(
                category='execution',
                severity='medium',
                title='Ecosystem discovery unavailable',
                description=f'Stage 2.5 ecosystem discovery status: {ecosystem_status}.',
                evidence={
                    'ecosystem_discovery_status': self.kpis.get('ecosystem_discovery_status'),
                    'ecosystem_discovery_error': self.kpis.get('ecosystem_discovery_error'),
                },
                interpretation=(
                    'Tier-2 ecosystem enrichment is incomplete.  '
                    'Unknown frameworks, runtime libraries, and '
                    'platform conventions were not auto-detected.'
                ),
                recommendation='Install discovery_engine dependencies and rerun when framework detection is needed.',
                effort='low',
                drill_down={'key': 'kpis.ecosystem_discovery_status'},
            )
        else:
            cap_status['ecosystem_discovery'] = 'ok'

        # --- 4. AI insights stage ------------------------------------------------
        ai_insights = self.data.get('ai_insights')
        if ai_insights:
            cap_status['ai_insights'] = 'ok'
        else:
            cap_status['ai_insights'] = 'off'

        # --- 5. HTML report stage ------------------------------------------------
        brain_download = self.data.get('brain_download')
        cap_status['html_report'] = 'ok' if brain_download else 'off'

        # --- 6. Freshness guard --------------------------------------------------
        self._check_freshness(cap_status)

        # --- 7. Publishability gate ----------------------------------------------
        self._check_publishability(cap_status)

        # --- Store capability status on self for inclusion in report meta ---------
        self._capability_status = cap_status

    def _check_freshness(self, cap_status: Dict[str, Any]):
        """Warn if compiled insights are based on stale analysis data.

        Staleness is detected by comparing the manifest timestamp (when
        full analysis ran) to the current compilation time.  If the gap
        exceeds the threshold the insights are flagged as potentially stale.
        """
        manifest = self.data.get('manifest') or {}
        generated_at = manifest.get('generated_at_utc', '')
        if not generated_at:
            # No manifest → likely feedback-only run; freshness unknown
            cap_status['freshness'] = 'unknown'
            return

        try:
            from datetime import datetime, timezone, timedelta
            if generated_at.endswith('Z'):
                generated_at = generated_at[:-1] + '+00:00'
            analysis_time = datetime.fromisoformat(generated_at)
            now = datetime.now(timezone.utc)
            age = now - analysis_time

            # Threshold: 24h for warning, 7d for stale
            if age > timedelta(days=7):
                cap_status['freshness'] = 'stale'
                self._add(
                    category='execution',
                    severity='high',
                    title='Analysis data is stale',
                    description=f'Analysis was generated {age.days}d ago ({generated_at}).',
                    evidence={'analysis_timestamp': generated_at, 'age_days': age.days},
                    interpretation=(
                        'Insights are based on analysis data older than 7 days.  '
                        'The codebase may have changed significantly since then.'
                    ),
                    recommendation='Re-run `collider full` to refresh analysis before publishing.',
                    effort='low',
                    drill_down={'key': 'manifest.generated_at_utc'},
                )
            elif age > timedelta(hours=24):
                cap_status['freshness'] = 'warn'
                self._add(
                    category='execution',
                    severity='low',
                    title='Analysis data aging',
                    description=f'Analysis was generated {age.total_seconds()/3600:.0f}h ago.',
                    evidence={'analysis_timestamp': generated_at, 'age_hours': round(age.total_seconds()/3600, 1)},
                    interpretation='Insights may not reflect recent changes.',
                    recommendation='Consider re-running analysis if significant changes were made.',
                    effort='low',
                    drill_down={'key': 'manifest.generated_at_utc'},
                )
            else:
                cap_status['freshness'] = 'fresh'
        except Exception:
            cap_status['freshness'] = 'unknown'

    def _check_publishability(self, cap_status: Dict[str, Any]):
        """Gate: a report is only 'publishable' if a smoke or full run occurred
        in the same session that produced the compiled insights.

        A feedback-only run (no Stage 1 analysis) should never be marked
        publishable because it reuses cached data without validating it.
        """
        perf = self.data.get('pipeline_performance') or {}
        stages = perf.get('stages', [])
        if isinstance(stages, list):
            stage_names = [s.get('stage_name', '') if isinstance(s, dict) else str(s) for s in stages]
        else:
            stage_names = []

        has_analysis = any('Stage 1' in s or 'Base Analysis' in s for s in stage_names)
        has_nodes = int(self.kpis.get('nodes_total', 0) or 0) > 0

        if has_analysis and has_nodes:
            cap_status['publishable'] = True
        else:
            cap_status['publishable'] = False
            if not has_analysis:
                self._add(
                    category='execution',
                    severity='medium',
                    title='Not publishable: no fresh analysis in session',
                    description='Insights were compiled without a smoke or full analysis run in this session.',
                    evidence={
                        'stages_executed': stage_names[:10],
                        'has_analysis_stage': has_analysis,
                        'nodes_total': self.kpis.get('nodes_total', 0),
                    },
                    interpretation=(
                        'A feedback-only compilation reuses cached data '
                        'without re-validating the codebase.  '
                        'This is useful for iteration but should not be '
                        'treated as a publishable quality gate.'
                    ),
                    recommendation='Run `collider full` or `collider smoke` before publishing results.',
                    effort='low',
                    drill_down={'key': 'pipeline_performance.stages'},
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
    # Extended interpretation passes (v2.0)
    # -------------------------------------------------------------------------

    def _interpret_markov(self):
        """Interpret Markov transitions -- developer navigation complexity."""
        markov = self.data.get('markov', {})
        if not markov:
            return

        avg_fanout = markov.get('avg_fanout', 0) or 0
        high_entropy = markov.get('high_entropy_nodes', [])
        total_trans = markov.get('total_transitions', 0) or 0

        if not high_entropy and avg_fanout < 4:
            return

        if high_entropy:
            top_nodes = high_entropy[:5]
            node_names = [n.get('node', '?') for n in top_nodes]
            max_fanout = max((n.get('fanout', 0) for n in top_nodes), default=0)
            sev = 'high' if max_fanout > 15 or len(high_entropy) > 10 else (
                'medium' if max_fanout > 8 else 'low'
            )

            self._add(
                category='topology',
                severity=sev,
                title='Navigation complexity hotspots',
                description=(
                    f'{len(high_entropy)} high-entropy nodes in the developer navigation model '
                    f'(avg fanout: {avg_fanout:.1f}, {total_trans} transitions).'
                ),
                evidence={
                    'high_entropy_count': len(high_entropy),
                    'avg_fanout': round(avg_fanout, 2),
                    'total_transitions': total_trans,
                    'top_nodes': [
                        {'node': n.get('node', '?'), 'fanout': n.get('fanout', 0),
                         'max_prob': round(n.get('max_prob', 0), 3)}
                        for n in top_nodes
                    ],
                },
                interpretation=(
                    'These files are navigation crossroads -- developers touching them face many '
                    'equally-likely next files to edit. High entropy means changes propagate '
                    'unpredictably. Consider decomposing into more focused modules.'
                ),
                recommendation=(
                    f'Review top entropy nodes: {", ".join(node_names[:3])}. '
                    'Break them into smaller, single-purpose modules to reduce change propagation.'
                ),
                effort='medium',
                related_nodes=node_names,
                theory_refs=['topology_shapes'],
                drill_down={'key': 'markov.high_entropy_nodes'},
            )

    def _interpret_topology_deep(self):
        """Interpret Betti numbers -- algebraic topology beyond shape classification."""
        topo = self.data.get('topology', {})
        betti = topo.get('betti_numbers', {})
        if not betti:
            return

        b0 = betti.get('b0', 1)
        b1 = betti.get('b1', 0)
        euler = betti.get('euler_characteristic', 0)
        health = betti.get('health_signal', '')
        vis = topo.get('visual_metrics', {})

        findings_added = False

        if b0 > 3:
            sev = 'high' if b0 > 10 else 'medium'
            self._add(
                category='topology',
                severity=sev,
                title=f'Disconnected components (b0={b0})',
                description=f'{b0} connected components -- the codebase has {b0} independent clusters.',
                evidence={
                    'b0': b0, 'b1': b1, 'euler': euler,
                    'largest_cluster_pct': vis.get('largest_cluster_percent', 0),
                },
                interpretation=(
                    f'Betti number b0={b0} means the dependency graph has {b0} disconnected pieces. '
                    f'Largest cluster covers {vis.get("largest_cluster_percent", "?")}% of nodes. '
                    'Remaining fragments may be dead modules or independently deployable services.'
                ),
                recommendation='Check if disconnected clusters are intentional (microservices) or accidental (missing imports).',
                effort='medium',
                theory_refs=['betti_numbers'],
                drill_down={'key': 'topology.betti_numbers'},
            )
            findings_added = True

        if b1 > 5:
            sev = 'high' if b1 > 20 else ('medium' if b1 > 10 else 'low')
            cyclic_count = vis.get('cyclic_nodes', 0)
            self._add(
                category='topology',
                severity=sev,
                title=f'Cycle complexity (b1={b1})',
                description=f'{b1} independent cycles in the dependency graph ({cyclic_count} cyclic nodes).',
                evidence={
                    'b1': b1, 'cyclic_nodes': cyclic_count,
                    'directed_cycles': vis.get('directed_cycles', 0),
                },
                interpretation=(
                    f'Betti number b1={b1} measures independent loops. Each cycle means a set of '
                    'mutual dependencies that must be understood as a unit. High b1 makes the '
                    'codebase harder to reason about and test in isolation.'
                ),
                recommendation='Break the largest cycles first using dependency inversion or interface extraction.',
                effort='high' if b1 > 20 else 'medium',
                theory_refs=['betti_numbers'],
                drill_down={'key': 'topology.visual_metrics'},
            )
            findings_added = True

        # Betti health contradicts shape?
        if health and not findings_added:
            shape = topo.get('shape', '')
            if health in ('warning', 'critical') and shape in ('MESH', 'STRICT_LAYERS'):
                self._add(
                    category='topology',
                    severity='low',
                    title='Betti health contradicts topology shape',
                    description=f'Shape is {shape} but Betti health signal is "{health}" (b0={b0}, b1={b1}).',
                    evidence={'shape': shape, 'health_signal': health, 'b0': b0, 'b1': b1, 'euler': euler},
                    interpretation='Topology shape looks healthy, but algebraic invariants detect hidden structural issues.',
                    recommendation='Investigate Betti numbers for latent cycle or fragmentation problems.',
                    effort='low',
                    theory_refs=['betti_numbers'],
                    drill_down={'key': 'topology.betti_numbers'},
                )

    def _interpret_data_flow(self):
        """Interpret data flow -- sources, sinks, and security surface area."""
        df = self.data.get('data_flow', {})
        if not df:
            return

        sources = df.get('data_sources', [])
        sinks = df.get('data_sinks', [])
        total_edges = df.get('total_flow_edges', 0)
        flow_by_type = df.get('flow_by_type', {})

        if not sources and not sinks:
            return

        if sources:
            top_sources = sources[:5]
            source_types = [s.get('type', '?') for s in top_sources]

            self._add(
                category='data_flow',
                severity='info',
                title=f'Data entry surface ({len(sources)} sources)',
                description=(
                    f'{len(sources)} data source components feed the system '
                    f'across {total_edges} flow edges.'
                ),
                evidence={
                    'source_count': len(sources),
                    'sink_count': len(sinks),
                    'total_flow_edges': total_edges,
                    'top_sources': [
                        {'type': s.get('type', '?'), 'out': s.get('out', 0),
                         'ratio': round(s.get('ratio', 0), 3)}
                        for s in top_sources
                    ],
                    'dominant_types': list(flow_by_type.keys())[:8],
                },
                interpretation=(
                    f'The system receives data through {len(sources)} source components '
                    f'(top types: {", ".join(source_types[:3])}). '
                    'Each source is a potential validation boundary and security checkpoint.'
                ),
                recommendation=(
                    'Verify all data sources have input validation. '
                    'Sources with high out-ratio are critical -- a bug there propagates everywhere.'
                ),
                effort='medium',
                theory_refs=['dimensions.D5_space'],
                drill_down={'key': 'data_flow.data_sources'},
            )

        # High-concentration sinks
        if sinks:
            high_in_sinks = [s for s in sinks if s.get('ratio', 0) > 0.3]

            if high_in_sinks:
                sev = 'medium' if len(high_in_sinks) > 3 else 'low'
                self._add(
                    category='data_flow',
                    severity=sev,
                    title=f'Data concentration sinks ({len(high_in_sinks)} high-ratio)',
                    description=f'{len(high_in_sinks)} sinks receive >30% of incoming data flow.',
                    evidence={
                        'high_ratio_sinks': [
                            {'type': s.get('type', '?'), 'in': s.get('in', 0),
                             'ratio': round(s.get('ratio', 0), 3)}
                            for s in high_in_sinks[:5]
                        ],
                    },
                    interpretation=(
                        'These components are data funnels -- many paths converge here. '
                        'They are critical for output correctness, logging, and security.'
                    ),
                    recommendation='Audit high-ratio sinks for proper error handling and output sanitization.',
                    effort='low',
                    theory_refs=['dimensions.D5_space'],
                    drill_down={'key': 'data_flow.data_sinks'},
                )

    def _interpret_graph_analytics(self):
        """Interpret graph analytics -- PageRank keystones, bottlenecks, communities."""
        ga = self.data.get('graph_analytics', {})
        if not ga:
            return

        pagerank_top = ga.get('pagerank_top', [])
        bottlenecks = ga.get('bottlenecks', [])
        communities = ga.get('communities_count', 0)

        # PageRank: architectural keystones
        if pagerank_top:
            top5 = pagerank_top[:5]
            names = [n.get('name', '?') for n in top5]

            self._add(
                category='topology',
                severity='info',
                title=f'Architectural keystones (top {len(top5)} by PageRank)',
                description=f'PageRank identifies {len(pagerank_top)} high-influence nodes. Top: {", ".join(names[:3])}.',
                evidence={
                    'keystones': [{
                        'name': n.get('name', '?'),
                        'kind': n.get('kind', '?'),
                        'pagerank': round(n.get('pagerank', 0), 4),
                        'betweenness': round(n.get('betweenness', 0), 4),
                        'in_degree': n.get('in_degree', 0),
                        'out_degree': n.get('out_degree', 0),
                        'community': n.get('community', None),
                    } for n in top5],
                },
                interpretation=(
                    'These nodes have the most structural influence. Changes to them '
                    'ripple through the most paths in the dependency graph. '
                    'They are the "load-bearing walls" of the architecture.'
                ),
                recommendation='Protect keystones with comprehensive tests. Refactoring here needs extra care.',
                effort='low',
                related_nodes=names,
                theory_refs=['graph_theory.pagerank'],
                drill_down={'key': 'graph_analytics.pagerank_top'},
            )

        # Bottlenecks: single points of failure
        if bottlenecks:
            top_bn = bottlenecks[:5]
            bn_names = [n.get('name', '?') for n in top_bn]
            max_betweenness = max((n.get('betweenness', 0) for n in top_bn), default=0)

            sev = 'high' if max_betweenness > 0.3 else ('medium' if max_betweenness > 0.1 else 'low')
            self._add(
                category='topology',
                severity=sev,
                title=f'Bottleneck nodes ({len(bottlenecks)} detected)',
                description=(
                    f'{len(bottlenecks)} nodes with high betweenness centrality. '
                    f'Top: {", ".join(bn_names[:3])}.'
                ),
                evidence={
                    'bottlenecks': [{
                        'name': n.get('name', '?'),
                        'kind': n.get('kind', '?'),
                        'betweenness': round(n.get('betweenness', 0), 4),
                        'in_degree': n.get('in_degree', 0),
                        'out_degree': n.get('out_degree', 0),
                    } for n in top_bn],
                },
                interpretation=(
                    'Bottleneck nodes sit on many shortest paths between other nodes. '
                    'If one fails or becomes complex, it blocks multiple workflows. '
                    'They are single points of failure in the architecture.'
                ),
                recommendation=f'Consider decomposing top bottleneck: {bn_names[0]}. Add redundant paths or facades.',
                effort='medium',
                related_nodes=bn_names,
                theory_refs=['graph_theory.betweenness'],
                drill_down={'key': 'graph_analytics.bottlenecks'},
            )

        # Community structure
        if communities > 1:
            self._add(
                category='topology',
                severity='info',
                title=f'Community structure ({communities} clusters)',
                description=f'Graph community detection found {communities} natural module clusters.',
                evidence={'communities_count': communities},
                interpretation=(
                    f'The codebase naturally groups into {communities} communities. '
                    'This suggests either good modular design or emerging domain boundaries.'
                ),
                recommendation='Compare detected communities against intended module boundaries. Mismatches reveal implicit coupling.',
                effort='low',
                theory_refs=['graph_theory.communities'],
                drill_down={'key': 'graph_analytics.communities'},
            )

    def _interpret_theory_completeness(self):
        """Interpret theory completeness -- SMoC dimension coverage gaps."""
        tc = self.data.get('theory_completeness', {})
        if not tc:
            return

        overall = tc.get('overall_score', 0)
        if not overall:
            return

        dims = {}
        for key, val in tc.items():
            if key.endswith('_percentage') and isinstance(val, (int, float)):
                dims[key.replace('_percentage', '')] = val

        if not dims:
            return

        weak_dims = {k: v for k, v in dims.items() if v < 50}
        if overall >= 80 and not weak_dims:
            return  # Healthy

        sev = 'medium' if overall < 50 else ('low' if overall < 80 else 'info')

        self._add(
            category='purpose',
            severity=sev,
            title=f'Theory coverage: {overall:.0f}%',
            description=(
                f'SMoC dimension coverage is {overall:.0f}%. '
                f'{len(weak_dims)} dimensions below 50%.'
            ),
            evidence={
                'overall_score': overall,
                'dimension_scores': {k: round(v, 1) for k, v in dims.items()},
                'weak_dimensions': list(weak_dims.keys()),
            },
            interpretation=(
                'Theory completeness measures how much of the Standard Model of Code\'s '
                'dimensional analysis the codebase supports. Weak dimensions are blind spots '
                'where the analysis has limited visibility.'
            ),
            recommendation=(
                f'Improve coverage for: {", ".join(weak_dims.keys())}. '
                'Add metadata, improve naming, or enrich configuration to fill gaps.'
                if weak_dims else 'Coverage is reasonable. Maintain it as the codebase grows.'
            ),
            effort='low',
            theory_refs=['dimensions'],
            drill_down={'key': 'theory_completeness'},
        )

    def _interpret_igt_stability(self):
        """Interpret IGT -- intergenerational transfer and critical orphans."""
        igt = self.data.get('igt', {})
        if not igt:
            return

        avg_stability = igt.get('avg_stability', 0)
        critical_count = igt.get('critical_orphans_count', 0)
        classified = igt.get('classified_orphans', [])

        if critical_count == 0 and avg_stability >= 0.8:
            return

        if critical_count > 0:
            problem_orphans = [o for o in classified if o.get('is_problem', False)]
            top_orphans = problem_orphans[:5] if problem_orphans else classified[:5]
            labels: Dict[str, int] = {}
            for o in classified:
                lbl = o.get('label', 'UNKNOWN')
                labels[lbl] = labels.get(lbl, 0) + 1

            sev = 'high' if critical_count > 20 else ('medium' if critical_count > 5 else 'low')
            label_summary = ', '.join(f'{k}={v}' for k, v in sorted(labels.items(), key=lambda x: -x[1])[:5])

            self._add(
                category='dead_code',
                severity=sev,
                title=f'Critical orphans ({critical_count} classified)',
                description=(
                    f'{critical_count} orphans classified by IGT. '
                    f'Labels: {label_summary}.'
                ),
                evidence={
                    'critical_orphans_count': critical_count,
                    'avg_stability': round(avg_stability, 3),
                    'label_distribution': labels,
                    'top_orphans': [{
                        'path': o.get('path', '?'),
                        'label': o.get('label', '?'),
                        'score': round(o.get('score', 0), 3),
                        'is_problem': o.get('is_problem', False),
                    } for o in top_orphans],
                },
                interpretation=(
                    'IGT classifies orphans with contextual labels (STANDALONE_DOC, DEAD_CODE, '
                    'FRAMEWORK_ENTRY, etc). Problem orphans are genuinely disconnected code that '
                    'adds maintenance cost without contributing to the dependency graph.'
                ),
                recommendation=(
                    'Review problem orphans first. STANDALONE_DOC may be fine; '
                    'DEAD_CODE should be removed; FRAMEWORK_ENTRY needs import verification.'
                ),
                effort='medium',
                related_nodes=[o.get('path', '?') for o in top_orphans],
                theory_refs=['igt', 'constraint_tiers.A_antimatter'],
                drill_down={'key': 'igt.classified_orphans'},
            )

        if avg_stability < 0.5 and critical_count == 0:
            self._add(
                category='dead_code',
                severity='low',
                title=f'Low IGT stability ({avg_stability:.2f})',
                description=f'Average intergenerational stability is {avg_stability:.2f} (below 0.5 threshold).',
                evidence={'avg_stability': round(avg_stability, 3)},
                interpretation=(
                    'Low stability means the codebase\'s directory structure has weak '
                    'parent-child relationships. Files may be misplaced.'
                ),
                recommendation='Review directory organization. Files may not reflect actual dependencies.',
                effort='low',
                theory_refs=['igt'],
                drill_down={'key': 'igt.directory_stability'},
            )

    def _interpret_semantic_roles(self):
        """Interpret semantic analysis -- role distribution and critical nodes."""
        sa = self.data.get('semantic_analysis', {})
        if not sa:
            return

        roles = sa.get('role_distribution', {})
        critical = sa.get('critical_nodes', {})
        intent = sa.get('intent_summary', {})

        # Role distribution skew
        if roles:
            total = sum(roles.values()) or 1
            dominant_role = max(roles.items(), key=lambda x: x[1], default=(None, 0))

            if dominant_role[0] and dominant_role[1] / total > 0.6:
                self._add(
                    category='topology',
                    severity='low',
                    title=f'Role skew: {dominant_role[1]/total:.0%} {dominant_role[0]}',
                    description=(
                        f'Node role distribution is skewed: {dominant_role[0]} nodes '
                        f'dominate at {dominant_role[1]/total:.0%}.'
                    ),
                    evidence={
                        'role_distribution': roles,
                        'dominant_role': dominant_role[0],
                        'dominant_pct': round(dominant_role[1] / total, 3),
                    },
                    interpretation=(
                        f'Most nodes are "{dominant_role[0]}" type. A healthy codebase '
                        'typically has a mix of hubs, leaves, orchestrators, and utilities.'
                    ),
                    recommendation=(
                        'If mostly leaves, the architecture may be overly flat. '
                        'If mostly hubs, it may be too centralized.'
                    ),
                    effort='low',
                    theory_refs=['dimensions.D1_what'],
                    drill_down={'key': 'semantic_analysis.role_distribution'},
                )

        # Bridges: single points of failure from semantic analysis
        bridges = critical.get('bridges', [])
        if bridges:
            bridge_names = (
                bridges[:5] if isinstance(bridges[0], str)
                else [b.get('name', '?') for b in bridges[:5]]
            ) if bridges else []
            sev = 'medium' if len(bridges) > 10 else 'low'

            self._add(
                category='topology',
                severity=sev,
                title=f'Bridge nodes ({len(bridges)} detected)',
                description=f'{len(bridges)} bridge nodes -- removing any one disconnects part of the graph.',
                evidence={
                    'bridge_count': len(bridges),
                    'top_bridges': bridge_names,
                },
                interpretation=(
                    'Bridge nodes are the only connection between graph regions. '
                    'If one fails, parts of the codebase become unreachable -- '
                    'they represent architectural fragility.'
                ),
                recommendation='Add redundant paths around critical bridges. Consider extracting shared interfaces.',
                effort='medium',
                related_nodes=bridge_names,
                theory_refs=['graph_theory.bridges'],
                drill_down={'key': 'semantic_analysis.critical_nodes.bridges'},
            )

        # Docstring coverage from intent summary
        if intent:
            total_processed = intent.get('total_processed', 0)
            with_docstring = intent.get('with_docstring', 0)
            if total_processed > 0:
                doc_ratio = with_docstring / total_processed
                if doc_ratio < 0.3:
                    self._add(
                        category='purpose',
                        severity='low',
                        title=f'Low documentation coverage ({doc_ratio:.0%})',
                        description=(
                            f'Only {with_docstring}/{total_processed} ({doc_ratio:.0%}) '
                            'nodes have docstrings.'
                        ),
                        evidence={
                            'total_processed': total_processed,
                            'with_docstring': with_docstring,
                            'doc_ratio': round(doc_ratio, 3),
                            'empty_profiles': intent.get('empty_profiles', 0),
                        },
                        interpretation=(
                            'Low docstring coverage means purpose-field analysis relies more on '
                            'naming and structure than explicit documentation.'
                        ),
                        recommendation='Add docstrings to high-traffic nodes first (keystones, bottlenecks, entry points).',
                        effort='medium',
                        theory_refs=['dimensions.D7_intent'],
                        drill_down={'key': 'semantic_analysis.intent_summary'},
                    )

    # -------------------------------------------------------------------------
    # Health score computation
    # -------------------------------------------------------------------------

    def _compute_health_components(self) -> Dict[str, float]:
        """Compute individual health component scores (each 0-10)."""
        components = {
            'topology': self._score_topology(),
            'constraints': self._score_constraints(),
            'purpose': self._score_purpose(),
            'test_coverage': self._score_test_coverage(),
            'dead_code': self._score_dead_code(),
            'entanglement': self._score_entanglement(),
            'rpbl_balance': self._score_rpbl_balance(),
        }
        # Apply chemistry modulations (coefficients < 1.0 penalise overconfident scores)
        if self._lab is not None:
            for key in components:
                mod = self._lab.get_modulation(key)
                if mod != 1.0:
                    components[key] = round(max(0.0, min(10.0, components[key] * mod)), 2)
        return components

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

        # Apply chemistry modulations to mission dimensions
        if self._lab is not None:
            execution_score = round(max(0.0, min(100.0, execution_score * self._lab.get_modulation('execution'))), 1)
            performance_score = round(max(0.0, min(100.0, performance_score * self._lab.get_modulation('performance'))), 1)
            logic_score = round(max(0.0, min(100.0, logic_score * self._lab.get_modulation('logic'))), 1)
            purpose_score = round(max(0.0, min(100.0, purpose_score * self._lab.get_modulation('purpose_fulfillment'))), 1)

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

        # Reference AI consumer summary if available
        ai_summary = self.data.get('ai_consumer_summary', {})
        if ai_summary:
            headline = ai_summary.get('headline', '')
            if headline:
                parts.append(f'AI assessment: {headline}')
            du_grade = ai_summary.get('data_utility_grade', '')
            if du_grade:
                parts.append(f'Data utility grade: **{du_grade}**.')

        # Reference convergence if significant
        chem = self.data.get('chemistry', {})
        conv = chem.get('convergence', {}) if chem else {}
        n_crit = conv.get('critical_count', 0)
        if n_crit > 0:
            parts.append(
                f'**{n_crit}** nodes have 5+ converging negative signals (critical convergence).'
            )

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
    # Collider Trinity interpreters (v2.1)
    # -------------------------------------------------------------------------

    def _interpret_incoherence(self):
        """Interpret incoherence functional results (Module 1 of Trinity)."""
        inc = self.data.get('incoherence', {})
        if not inc:
            return

        i_total = inc.get('i_total', 0.5)
        health_10 = inc.get('health_10', 5.0)

        # Summary finding -- always emit
        if i_total > 0.6:
            sev = 'critical'
        elif i_total > 0.4:
            sev = 'high'
        elif i_total > 0.25:
            sev = 'medium'
        else:
            sev = 'low'

        self._add(
            category='incoherence',
            severity=sev,
            title='Incoherence Functional',
            description=(
                f'Aggregate incoherence I(C) = {i_total:.3f} '
                f'(health {health_10:.1f}/10). '
                f'Measures structural, teleological, symmetry, boundary, '
                f'and flow coherence.'
            ),
            evidence={
                'i_total': i_total,
                'health_10': health_10,
                'i_struct': inc.get('i_struct'),
                'i_telic': inc.get('i_telic'),
                'i_sym': inc.get('i_sym'),
                'i_bound': inc.get('i_bound'),
                'i_flow': inc.get('i_flow'),
            },
            interpretation=(
                'The Incoherence Functional quantifies how far the codebase '
                'deviates from architectural coherence across five dimensions. '
                'Lower is better (0 = perfectly coherent).'
            ),
            recommendation=(
                'Focus on the highest I-term first. '
                'I_struct: reduce cycles/antimatter. '
                'I_telic: clarify node purposes. '
                'I_bound: fix layer violations.'
            ) if sev in ('critical', 'high') else '',
            effort='high' if sev == 'critical' else 'medium',
            theory_refs=['LAGRANGIAN.md'],
            drill_down={'key': 'incoherence', 'kpi': 'i_total'},
        )

        # Per-term findings for terms above threshold
        terms = inc.get('details', {}).get('terms', {})
        term_labels = {
            'struct': ('Structural', 'Cycles, antimatter density, entanglement'),
            'telic': ('Teleological', 'Purpose clarity, orphans, god classes'),
            'sym': ('Symmetry', 'Dead code, unknown nodes, coverage gaps'),
            'bound': ('Boundary', 'Layer violations, RPBL coupling'),
            'flow': ('Flow', 'Fan-out, topology shape, centralization'),
        }
        for key, (label, desc) in term_labels.items():
            term_val = inc.get(f'i_{key}')
            if term_val is not None and term_val > 0.4:
                self._add(
                    category='incoherence',
                    severity='high' if term_val > 0.6 else 'medium',
                    title=f'High {label} Incoherence (I_{key}={term_val:.2f})',
                    description=f'{label} incoherence is elevated. Measures: {desc}.',
                    evidence={'term': key, 'value': term_val, 'details': terms.get(key, {})},
                    interpretation=f'I_{key} > 0.4 indicates significant {label.lower()} degradation.',
                    recommendation=f'Investigate {label.lower()} drivers in the details breakdown.',
                    effort='medium',
                    theory_refs=['LAGRANGIAN.md'],
                    drill_down={'key': f'incoherence.i_{key}'},
                )

    def _interpret_purpose_decomposition(self):
        """Interpret purpose decomposition results (Module 2 of Trinity)."""
        decomp = self.data.get('purpose_decomposition', [])
        if not decomp:
            return

        # Find containers with missing required sub-purposes (critical gaps)
        for dr in decomp:
            missing = dr.get('missing', [])
            violations = dr.get('violations', [])
            completeness = dr.get('completeness', 1.0)
            node_id = dr.get('node_id', '?')
            purpose = dr.get('purpose', '?')

            if missing:
                self._add(
                    category='purpose_decomposition',
                    severity='high' if len(missing) > 1 else 'medium',
                    title=f'{purpose} missing required sub-purposes',
                    description=(
                        f"Container '{node_id}' ({purpose}) is missing "
                        f"required sub-purposes: {', '.join(missing)}. "
                        f"Completeness: {completeness:.0%}."
                    ),
                    evidence={
                        'node_id': node_id,
                        'purpose': purpose,
                        'missing': missing,
                        'completeness': completeness,
                    },
                    interpretation=(
                        f'CONSTRAINT_RULES require a {purpose} to have '
                        f'{", ".join(missing)} children. Their absence '
                        f'indicates incomplete architectural implementation.'
                    ),
                    recommendation=(
                        f'Add {", ".join(missing)} sub-components to '
                        f'{node_id}, or verify they exist under different names.'
                    ),
                    effort='high',
                    related_nodes=[node_id],
                    theory_refs=['PURPOSE_FIELD_INTEGRATION_SPEC.md'],
                    drill_down={'key': 'purpose_decomposition', 'node': node_id},
                )

            if violations:
                self._add(
                    category='purpose_decomposition',
                    severity='high',
                    title=f'{purpose} contains forbidden sub-purposes',
                    description=(
                        f"Container '{node_id}' ({purpose}) contains "
                        f"forbidden sub-purposes: {', '.join(violations)}. "
                        f"This violates architectural constraints."
                    ),
                    evidence={
                        'node_id': node_id,
                        'purpose': purpose,
                        'violations': violations,
                    },
                    interpretation=(
                        f'A {purpose} should not contain '
                        f'{", ".join(violations)} children. This indicates '
                        f'responsibility leakage or misclassification.'
                    ),
                    recommendation=(
                        f'Extract {", ".join(violations)} logic from '
                        f'{node_id} into appropriate containers.'
                    ),
                    effort='medium',
                    related_nodes=[node_id],
                    theory_refs=['PURPOSE_FIELD_INTEGRATION_SPEC.md'],
                    drill_down={'key': 'purpose_decomposition', 'node': node_id},
                )

    def _interpret_gaps(self):
        """Interpret gap detection results (Module 3 of Trinity)."""
        report = self.data.get('gap_report', {})
        if not report:
            return

        gaps = report.get('gaps', [])
        coverage = report.get('coverage', 1.0)
        query_targets = report.get('query_targets', [])

        if not gaps:
            return

        # Summary finding
        critical_count = sum(1 for g in gaps if g.get('severity') == 'critical')
        high_count = sum(1 for g in gaps if g.get('severity') == 'high')

        if critical_count > 0:
            sev = 'critical'
        elif high_count > 0:
            sev = 'high'
        elif len(gaps) > 10:
            sev = 'medium'
        else:
            sev = 'low'

        by_type = {}
        for g in gaps:
            gt = g.get('gap_type', 'unknown')
            by_type[gt] = by_type.get(gt, 0) + 1

        type_summary = ', '.join(f'{t}({c})' for t, c in sorted(by_type.items(), key=lambda x: -x[1]))

        self._add(
            category='gap_detection',
            severity=sev,
            title=f'{len(gaps)} architectural gaps detected',
            description=(
                f'Gap analysis found {len(gaps)} gaps across the codebase. '
                f'Coverage: {coverage:.0%}. Types: {type_summary}. '
                f'{len(query_targets)} gaps are well-circumscribed for LLM analysis.'
            ),
            evidence={
                'total_gaps': len(gaps),
                'coverage': coverage,
                'by_type': by_type,
                'critical_count': critical_count,
                'high_count': high_count,
                'query_targets_count': len(query_targets),
            },
            interpretation=(
                'Gaps represent missing, forbidden, or disconnected '
                'architectural elements. Critical gaps (missing required '
                'sub-purposes) indicate incomplete implementations.'
            ),
            recommendation=(
                'Address critical gaps first (missing required sub-purposes). '
                'Use LLM query targets for deeper semantic analysis.'
            ) if sev in ('critical', 'high') else '',
            effort='high' if critical_count > 5 else 'medium',
            theory_refs=['THEORY_EXPANSION_2026.md'],
            drill_down={'key': 'gap_report'},
        )

        # Individual critical gaps as separate findings
        for g in gaps:
            if g.get('severity') != 'critical':
                continue
            self._add(
                category='gap_detection',
                severity='critical',
                title=f"Critical gap: {g.get('gap_type', '?')} at {g.get('location', '?')}",
                description=g.get('description', ''),
                evidence={
                    'location': g.get('location'),
                    'gap_type': g.get('gap_type'),
                    'context': g.get('context', {}),
                    'llm_query_hint': g.get('llm_query_hint', ''),
                },
                interpretation=(
                    'This is a critical architectural gap -- a required '
                    'sub-purpose is absent from its container.'
                ),
                recommendation=g.get('llm_query_hint', 'Investigate this gap.'),
                effort='medium',
                related_nodes=[g.get('location', '')],
                theory_refs=['THEORY_EXPANSION_2026.md'],
                drill_down={'key': 'gap_report.gaps', 'location': g.get('location')},
            )

    def _interpret_temporal(self):
        """Interpret temporal analysis results (REH integration)."""
        ta = self.data.get('temporal_analysis', {})
        if not ta or not ta.get('available'):
            return

        # --- Hotspot concentration ---
        hotspots = ta.get('hotspots', [])
        if hotspots:
            top = hotspots[0]
            top_count = top.get('change_count', 0)
            sev = 'high' if top_count > 50 else ('medium' if top_count > 20 else 'low')
            self._add(
                category='temporal',
                severity=sev,
                title='Change Hotspots',
                description=(
                    f'Top hotspot: {top.get("path", "?")} changed {top_count} times. '
                    f'{len(hotspots)} hotspots identified.'
                ),
                evidence={
                    'top_hotspot': top.get('path'),
                    'top_change_count': top_count,
                    'hotspot_count': len(hotspots),
                },
                interpretation=(
                    'Files with high change frequency are maintenance magnets. '
                    'They either concentrate too much responsibility (God class) '
                    'or sit at an unstable architectural boundary.'
                ),
                recommendation=(
                    f'Consider decomposing {top.get("path", "?")} if it '
                    f'mixes multiple concerns.'
                ) if sev in ('high', 'medium') else '',
                effort='medium' if sev == 'high' else 'low',
                related_nodes=[h.get('path', '') for h in hotspots[:5]],
                theory_refs=['FLOW.md'],
                drill_down={'key': 'temporal_analysis.hotspots'},
            )

        # --- Change coupling ---
        coupling = ta.get('change_coupling', [])
        if coupling:
            top_pair = coupling[0]
            co_count = top_pair.get('co_change_count', 0)
            sev = 'medium' if co_count > 10 else 'low'
            self._add(
                category='temporal',
                severity=sev,
                title='Temporal Coupling',
                description=(
                    f'{len(coupling)} file pairs change together frequently. '
                    f'Strongest: {top_pair.get("file_a", "?")} ↔ '
                    f'{top_pair.get("file_b", "?")} ({co_count} co-changes).'
                ),
                evidence={
                    'coupling_pairs': len(coupling),
                    'strongest_pair': [
                        top_pair.get('file_a'),
                        top_pair.get('file_b'),
                    ],
                    'strongest_co_changes': co_count,
                },
                interpretation=(
                    'Files that always change together may be tightly coupled. '
                    'If they are in different modules, the module boundary may '
                    'be misdrawn. If same module, consider merging or extracting '
                    'a shared abstraction.'
                ),
                recommendation='Review coupling pairs for hidden dependencies.',
                effort='low',
                theory_refs=['FLOW.md'],
                drill_down={'key': 'temporal_analysis.change_coupling'},
            )

        # --- Capability drift ---
        removed = ta.get('capabilities_removed', [])
        if removed:
            self._add(
                category='temporal',
                severity='high' if len(removed) > 5 else 'medium',
                title='Capability Regression Risk',
                description=(
                    f'{len(removed)} functions/classes removed in recent commits. '
                    f'{ta.get("capabilities_modified", 0)} modified.'
                ),
                evidence={
                    'removed_count': len(removed),
                    'modified_count': ta.get('capabilities_modified', 0),
                    'added_count': len(ta.get('capabilities_added', [])),
                    'removed_names': [r.get('name', '') for r in removed[:10]],
                },
                interpretation=(
                    'Recently removed capabilities may indicate intentional '
                    'cleanup or accidental regression. Cross-reference with '
                    'test results to verify no capability loss.'
                ),
                recommendation='Verify removed capabilities are covered by tests.',
                effort='medium',
                theory_refs=['THEORY_EXPANSION_2026.md'],
                drill_down={'key': 'temporal_analysis.capabilities_removed'},
            )

        # --- Bus factor ---
        bus_factor = ta.get('bus_factor', 0)
        if bus_factor == 1:
            self._add(
                category='temporal',
                severity='high',
                title='Single Contributor (Bus Factor = 1)',
                description='Only one author has contributed to this repository.',
                evidence={'bus_factor': 1},
                interpretation=(
                    'All institutional knowledge resides with a single person. '
                    'If they become unavailable, the project has no fallback.'
                ),
                recommendation='Document critical decisions and onboard a second contributor.',
                effort='high',
                theory_refs=[],
            )

        # --- Growth summary (always emit as info) ---
        self._add(
            category='temporal',
            severity='info',
            title='Repository Timeline',
            description=(
                f'{ta.get("total_commits", 0)} commits over '
                f'{ta.get("active_days", 0)} active days '
                f'({ta.get("first_commit_date", "?")} → '
                f'{ta.get("last_commit_date", "?")}). '
                f'Median file age: {ta.get("median_age_days", 0):.0f} days.'
            ),
            evidence={
                'total_commits': ta.get('total_commits'),
                'active_days': ta.get('active_days'),
                'commits_per_day': ta.get('commits_per_day'),
                'median_age_days': ta.get('median_age_days'),
                'bus_factor': bus_factor,
            },
            interpretation='Temporal fingerprint of the repository.',
            recommendation='',
            effort='low',
            drill_down={'key': 'temporal_analysis'},
        )

    # -------------------------------------------------------------------------
    # Contextome Intelligence (Stage 0.8)
    # -------------------------------------------------------------------------

    def _interpret_contextome(self):
        """Interpret Contextome Intelligence results (Stage 0.8)."""
        ctx = self.data.get('contextome', {})
        if not ctx:
            return

        doc_count = ctx.get('doc_count', 0)
        purpose_coverage = ctx.get('purpose_coverage', 0.0)
        deterministic_signals = ctx.get('deterministic_signals', 0)
        enriched_signals = ctx.get('enriched_signals', 0)
        llm_used = ctx.get('llm_used', False)
        declared_purposes = ctx.get('declared_purposes', [])
        symmetry_seeds = ctx.get('symmetry_seeds', [])
        purpose_priors = ctx.get('purpose_priors', {})

        # --- Purpose coverage ---
        if doc_count > 0:
            sev = 'info'
            if purpose_coverage < 0.3:
                sev = 'high'
            elif purpose_coverage < 0.6:
                sev = 'medium'
            elif purpose_coverage < 0.8:
                sev = 'low'

            self._add(
                category='contextome',
                severity=sev,
                title='Documentation Purpose Coverage',
                description=(
                    f'{doc_count} documentation files found. '
                    f'{purpose_coverage:.0%} have extractable purpose signals. '
                    f'{deterministic_signals} deterministic signals extracted'
                    + (f', {enriched_signals} LLM-enriched.' if llm_used else '.')
                ),
                evidence={
                    'doc_count': doc_count,
                    'purpose_coverage': purpose_coverage,
                    'deterministic_signals': deterministic_signals,
                    'enriched_signals': enriched_signals,
                    'llm_used': llm_used,
                },
                interpretation=(
                    'Purpose coverage measures how many docs contain '
                    'extractable purpose signals (headings, keywords, code refs). '
                    'Low coverage means the Contextome is opaque -- '
                    'documentation exists but does not communicate intent.'
                ) if sev in ('high', 'medium') else (
                    'Contextome fingerprint of the repository.'
                ),
                recommendation=(
                    'Add purpose-oriented headings (H1) to documentation files. '
                    'Reference code paths explicitly to improve symmetry detection.'
                ) if sev in ('high', 'medium') else '',
                effort='low',
                theory_refs=['FRONTIER_REFRAMING_2026-03-02.md'],
                drill_down={'key': 'contextome'},
            )
        else:
            # No docs at all
            self._add(
                category='contextome',
                severity='medium',
                title='No Documentation Found',
                description='No documentation files (.md, .rst, .txt, .adoc, .org) detected.',
                evidence={'doc_count': 0},
                interpretation=(
                    'A repository without documentation has zero Contextome. '
                    'Purpose can only be inferred from code structure.'
                ),
                recommendation='Create a README.md with project purpose and architecture.',
                effort='low',
                theory_refs=['FRONTIER_REFRAMING_2026-03-02.md'],
            )
            return  # No more contextome findings possible

        # --- Symmetry seeds ---
        if symmetry_seeds:
            high_conf = [s for s in symmetry_seeds if s.get('confidence', 0) >= 0.7]
            low_conf = [s for s in symmetry_seeds if s.get('confidence', 0) < 0.4]
            self._add(
                category='contextome',
                severity='info',
                title='Doc-Code Symmetry Seeds',
                description=(
                    f'{len(symmetry_seeds)} doc-code relationships detected. '
                    f'{len(high_conf)} high-confidence, {len(low_conf)} low-confidence.'
                ),
                evidence={
                    'total_seeds': len(symmetry_seeds),
                    'high_confidence': len(high_conf),
                    'low_confidence': len(low_conf),
                    'top_seeds': symmetry_seeds[:5],
                },
                interpretation=(
                    'Symmetry seeds map documentation to the code it describes. '
                    'High confidence means clear name matching or explicit code refs. '
                    'Low confidence means only indirect signals (sibling directory).'
                ),
                recommendation='',
                effort='low',
                theory_refs=['LAGRANGIAN.md'],
                drill_down={'key': 'contextome.symmetry_seeds'},
            )

        # --- Constraint declarations ---
        docs_with_constraints = [
            dp for dp in declared_purposes
            if dp.get('constraints') and len(dp.get('constraints', [])) > 0
        ]
        if docs_with_constraints:
            total_constraints = sum(
                len(dp.get('constraints', [])) for dp in docs_with_constraints
            )
            sev = 'info' if total_constraints < 20 else 'low'
            self._add(
                category='contextome',
                severity=sev,
                title='Documented Constraints',
                description=(
                    f'{total_constraints} MUST/SHALL constraint statements found '
                    f'across {len(docs_with_constraints)} documents.'
                ),
                evidence={
                    'total_constraints': total_constraints,
                    'docs_with_constraints': len(docs_with_constraints),
                    'sample_files': [dp.get('file', '') for dp in docs_with_constraints[:5]],
                },
                interpretation=(
                    'RFC 2119 constraint language (MUST, SHALL, REQUIRED) in documentation '
                    'represents testable requirements. These can seed gap detection and '
                    'inform purpose decomposition.'
                ),
                recommendation='',
                effort='low',
                theory_refs=['FRONTIER_REFRAMING_2026-03-02.md'],
                drill_down={'key': 'contextome.declared_purposes'},
            )

        # --- Framework signals ---
        all_frameworks = set()
        for dp in declared_purposes:
            all_frameworks.update(dp.get('framework_signals', []))
        if all_frameworks:
            self._add(
                category='contextome',
                severity='info',
                title='Framework Signals from Documentation',
                description=(
                    f'{len(all_frameworks)} framework/technology signals extracted: '
                    f'{", ".join(sorted(all_frameworks)[:10])}'
                    + (f' (+{len(all_frameworks) - 10} more)' if len(all_frameworks) > 10 else '')
                    + '.'
                ),
                evidence={
                    'frameworks': sorted(all_frameworks),
                    'framework_count': len(all_frameworks),
                },
                interpretation=(
                    'Framework signals from documentation provide purpose priors -- '
                    'if docs mention React, code should contain React patterns.'
                ),
                recommendation='',
                effort='low',
                drill_down={'key': 'contextome.declared_purposes'},
            )

        # --- Purpose priors ---
        if purpose_priors:
            self._add(
                category='contextome',
                severity='info',
                title='Purpose Priors',
                description=(
                    f'{len(purpose_priors)} purpose priors generated from documentation. '
                    f'These seed the purpose field with top-down expectations.'
                ),
                evidence={
                    'prior_count': len(purpose_priors),
                    'sample_priors': dict(list(purpose_priors.items())[:5]),
                },
                interpretation=(
                    'Purpose priors are glob-pattern-to-purpose mappings derived '
                    'from documentation headings and keywords. They guide the '
                    'purpose field computation by setting expectations before '
                    'bottom-up emergence runs.'
                ),
                recommendation='',
                effort='low',
                theory_refs=['PURPOSE_FIELD_INTEGRATION_SPEC.md'],
                drill_down={'key': 'contextome.purpose_priors'},
            )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _promote_findings_to_issues(self) -> list:
        """Promote high/critical findings into a structured issues list.

        Issues are the CI/dashboard-consumable signal: they represent
        findings that warrant immediate attention or should block
        a "publishable" quality gate.
        """
        issues: list = []
        for f in self.findings:
            if f.severity in ('critical', 'high'):
                issues.append({
                    'id': f.id,
                    'title': f.title,
                    'severity': f.severity,
                    'category': f.category,
                    'recommendation': f.recommendation,
                    'effort': f.effort,
                })
        return issues

    # -----------------------------------------------------------------
    # Ideome Synthesis (Rosetta Stone)
    # -----------------------------------------------------------------
    def _interpret_ideome(self):
        """Interpret Ideome synthesis results: triangulated drift attribution."""
        ideome = self.data.get('ideome', {})
        if not ideome:
            return

        # --- Global summary (always emitted) ---
        coherence = ideome.get('global_coherence', 0.0)
        drift_C = ideome.get('global_drift_C', 0.0)
        drift_X = ideome.get('global_drift_X', 0.0)
        delta_CX = ideome.get('global_delta_CX', 0.0)
        coverage = ideome.get('coverage', 0.0)
        node_count = ideome.get('node_count', 0)

        if coherence >= 0.8:
            sev = 'info'
        elif coherence >= 0.6:
            sev = 'low'
        elif coherence >= 0.4:
            sev = 'medium'
        else:
            sev = 'high'

        # Determine dominant drift direction
        if delta_CX < 0.15:
            drift_summary = 'Code and documentation are well-aligned.'
        elif drift_C > drift_X:
            drift_summary = 'Code has drifted further from the ideal than documentation.'
        else:
            drift_summary = 'Documentation has drifted further from the ideal than code.'

        self._add(
            category='ideome',
            severity=sev,
            title='Ideome Coherence (Rosetta Stone)',
            description=(
                f'Global coherence: {coherence:.3f} '
                f'(code drift={drift_C:.3f}, docs drift={drift_X:.3f}, '
                f'delta={delta_CX:.3f}). '
                f'Coverage: {coverage:.1%} of {node_count} nodes.'
            ),
            evidence={
                'global_coherence': coherence,
                'global_drift_C': drift_C,
                'global_drift_X': drift_X,
                'global_delta_CX': delta_CX,
                'coverage': coverage,
                'node_count': node_count,
            },
            interpretation=(
                f'{drift_summary} '
                f'The Ideome triangulates between code reality (Codome), '
                f'documentation claims (Contextome), and the ideal reference frame '
                f'to attribute drift direction.'
            ),
            recommendation=(
                'Focus on the side with higher drift score. '
                'Code drift means implementation deviated from architectural intent. '
                'Docs drift means documentation no longer describes the actual system.'
                if delta_CX >= 0.15 else ''
            ),
            effort='medium' if delta_CX >= 0.3 else 'low',
            theory_refs=['FRONTIER_REFRAMING_2026-03-02.md'],
            drill_down={'key': 'ideome'},
        )

        # --- Per-domain findings (only for significant drift) ---
        domains = ideome.get('domains', [])
        for dom in domains:
            dom_delta = dom.get('avg_delta_CX', 0.0)
            if dom_delta < 0.3:
                continue

            dom_name = dom.get('domain', '?')
            dom_direction = dom.get('drift_direction', 'unknown')
            dom_drift_C = dom.get('avg_alignment_C', 0.0)
            dom_drift_X = dom.get('avg_alignment_X', 0.0)
            dom_count = dom.get('node_count', 0)
            worst = dom.get('worst_nodes', [])

            if dom_delta >= 0.5:
                dom_sev = 'high'
            elif dom_delta >= 0.3:
                dom_sev = 'medium'
            else:
                dom_sev = 'low'

            direction_label = {
                'code_drifted': 'Code has drifted from documentation',
                'docs_drifted': 'Documentation has drifted from code',
                'both_drifted': 'Both code and docs have drifted from the ideal',
                'aligned': 'Aligned',
            }.get(dom_direction, 'Drift direction unclear')

            self._add(
                category='ideome',
                severity=dom_sev,
                title=f'Domain Drift: {dom_name}',
                description=(
                    f'{direction_label} in {dom_name} '
                    f'({dom_count} nodes, delta={dom_delta:.3f}). '
                    f'Code alignment={dom_drift_C:.3f}, '
                    f'docs alignment={dom_drift_X:.3f}.'
                ),
                evidence={
                    'domain': dom_name,
                    'drift_direction': dom_direction,
                    'avg_alignment_C': dom_drift_C,
                    'avg_alignment_X': dom_drift_X,
                    'avg_delta_CX': dom_delta,
                    'node_count': dom_count,
                    'worst_nodes': worst,
                },
                interpretation=(
                    f'The domain {dom_name} shows significant divergence between '
                    f'code and documentation. {direction_label}.'
                ),
                recommendation=(
                    f'Review the {len(worst)} most drifted nodes in {dom_name}: '
                    f'{", ".join(worst[:3])}'
                    + (f' (+{len(worst) - 3} more)' if len(worst) > 3 else '')
                    + '.'
                    if worst else f'Investigate drift in {dom_name}.'
                ),
                effort='medium',
                related_nodes=worst[:5],
                drill_down={'key': 'ideome.domains', 'domain': dom_name},
            )

    # ------------------------------------------------------------------
    # Dark-matter feature interpreters (Collider Potential expansion)
    # ------------------------------------------------------------------

    def _interpret_smart_ignore(self):
        """Interpret SmartIgnore manifest -- noise ratio and filtering impact."""
        si = self.data.get('smart_ignore', {})
        if not si:
            return

        ignored_count = si.get('ignored_count', 0) or len(si.get('ignored_paths', []))
        total_files = si.get('total_files', 0)
        noise_ratio = si.get('noise_ratio', 0.0)
        patterns = si.get('patterns', [])

        if total_files and not noise_ratio:
            noise_ratio = ignored_count / total_files if total_files else 0

        if ignored_count == 0:
            return

        sev = 'info'
        if noise_ratio > 0.5:
            sev = 'medium'
        elif noise_ratio > 0.3:
            sev = 'low'

        self._add(
            category='noise',
            severity=sev,
            title=f'SmartIgnore filtered {ignored_count} paths ({noise_ratio:.0%} noise ratio)',
            description=(
                f'{ignored_count} files/directories ignored out of {total_files or "?"} total. '
                f'Noise ratio: {noise_ratio:.1%}.'
                + (f' Top patterns: {", ".join(str(p) for p in patterns[:3])}.' if patterns else '')
            ),
            evidence={
                'ignored_count': ignored_count,
                'total_files': total_files,
                'noise_ratio': round(noise_ratio, 4),
                'patterns': patterns[:5] if patterns else [],
            },
            interpretation=(
                'High noise ratios (>50%) indicate heavy dependency or build artifacts. '
                'SmartIgnore keeps the analysis focused on production code.'
            ),
            recommendation='Review ignored patterns if key source files are missing from analysis.',
            effort='low',
            drill_down={'key': 'smart_ignore'},
        )

    def _interpret_roadmap_eval(self):
        """Interpret roadmap evaluation -- readiness and milestone coverage."""
        rm = self.data.get('roadmap', {})
        if not rm:
            return

        readiness = rm.get('readiness_score', 0)
        milestones = rm.get('milestones', [])
        missing = rm.get('missing', [])
        covered = rm.get('covered', [])
        total_ms = len(milestones) or (len(covered) + len(missing)) or 1

        sev = 'info'
        if readiness < 30:
            sev = 'high'
        elif readiness < 60:
            sev = 'medium'
        elif readiness < 80:
            sev = 'low'

        self._add(
            category='roadmap',
            severity=sev,
            title=f'Roadmap readiness: {readiness:.0f}%',
            description=(
                f'{len(covered)} of {total_ms} milestones covered. '
                + (f'Missing: {", ".join(str(m) for m in missing[:3])}.' if missing else 'All milestones met.')
            ),
            evidence={
                'readiness_score': readiness,
                'milestones_total': total_ms,
                'covered_count': len(covered),
                'missing_count': len(missing),
                'missing_sample': missing[:5],
            },
            interpretation='Roadmap readiness measures how much of a planned architecture is actually implemented.',
            recommendation='Focus on missing milestones to close readiness gaps.' if missing else 'Roadmap fully covered.',
            effort='high' if len(missing) > 3 else 'medium',
            drill_down={'key': 'roadmap'},
        )

    def _interpret_semantics_cortex(self):
        """Interpret semantic cortex -- domain inference and concept clusters."""
        sem = self.data.get('semantics', {})
        if not sem:
            return

        domain = sem.get('domain_inference', 'Unknown')
        top_concepts = sem.get('top_concepts', [])
        concept_clusters = sem.get('concept_clusters', [])
        naming_patterns = sem.get('naming_patterns', {})

        if domain == 'Unknown' and not top_concepts:
            return

        concept_names = [c.get('term', c) if isinstance(c, dict) else str(c) for c in top_concepts[:5]]

        self._add(
            category='purpose',
            severity='info',
            title=f'Semantic domain: {domain}',
            description=(
                f'Inferred domain: {domain}. '
                f'Top concepts: {", ".join(concept_names)}.'
                + (f' {len(concept_clusters)} concept clusters detected.' if concept_clusters else '')
            ),
            evidence={
                'domain_inference': domain,
                'top_concepts': top_concepts[:5],
                'cluster_count': len(concept_clusters),
                'naming_patterns': naming_patterns,
            },
            interpretation=(
                'Semantic cortex extracts domain vocabulary from identifiers and structure. '
                'Strong domain coherence indicates clear naming conventions.'
            ),
            recommendation='Review naming conventions if domain inference seems wrong.',
            effort='low',
            drill_down={'key': 'semantics'},
        )

    def _interpret_ecosystem(self):
        """Interpret ecosystem discovery -- unknown patterns and library detection."""
        eco = self.data.get('ecosystem_discovery', {})
        if not eco:
            return

        total_unknowns = eco.get('total_unknowns', 0)
        categories = eco.get('categories', {})
        discoveries = eco.get('discoveries', [])

        if total_unknowns == 0 and not categories:
            return

        sev = 'info'
        if total_unknowns > 50:
            sev = 'medium'
        elif total_unknowns > 20:
            sev = 'low'

        cat_summary = ', '.join(f'{k}={v}' for k, v in sorted(
            categories.items(), key=lambda x: -x[1] if isinstance(x[1], (int, float)) else 0
        )[:5]) if categories else 'none'

        self._add(
            category='ecosystem',
            severity=sev,
            title=f'Ecosystem: {total_unknowns} unknown patterns',
            description=(
                f'{total_unknowns} ecosystem patterns not in the Standard Model taxonomy. '
                f'Categories: {cat_summary}.'
            ),
            evidence={
                'total_unknowns': total_unknowns,
                'categories': categories,
                'sample_discoveries': discoveries[:5] if discoveries else [],
            },
            interpretation=(
                'Unknown ecosystem patterns are libraries, frameworks, or conventions '
                'not yet mapped to Standard Model atoms. High counts may indicate '
                'a specialized tech stack.'
            ),
            recommendation='Consider extending atom taxonomy if unknowns represent recurring patterns.',
            effort='medium',
            drill_down={'key': 'ecosystem_discovery'},
        )

    def _interpret_dependencies_graph(self):
        """Interpret project dependencies -- complexity and depth."""
        deps = self.data.get('dependencies', {})
        if not deps:
            return

        dep_list = deps if isinstance(deps, list) else deps.get('dependencies', deps.get('items', []))
        if isinstance(dep_list, dict):
            dep_count = len(dep_list)
            dep_types = dep_list
        elif isinstance(dep_list, list):
            dep_count = len(dep_list)
            dep_types = {}
        else:
            return

        if dep_count == 0:
            return

        sev = 'info'
        if dep_count > 100:
            sev = 'medium'
        elif dep_count > 50:
            sev = 'low'

        self._add(
            category='topology',
            severity=sev,
            title=f'Dependency landscape: {dep_count} dependencies',
            description=f'{dep_count} project dependencies detected.',
            evidence={
                'dependency_count': dep_count,
                'dependency_types': dep_types if isinstance(dep_types, dict) else {},
            },
            interpretation=(
                'Large dependency counts increase supply-chain risk and build complexity. '
                'Transitive dependencies can introduce unexpected vulnerabilities.'
            ),
            recommendation='Audit dependencies periodically. Remove unused packages.' if dep_count > 50 else 'Dependency count is manageable.',
            effort='medium' if dep_count > 50 else 'low',
            drill_down={'key': 'dependencies'},
        )

    def _interpret_advisories(self):
        """Interpret warnings and recommendations -- advisory landscape."""
        warnings = self.data.get('warnings', [])
        recommendations = self.data.get('recommendations', [])

        if not warnings and not recommendations:
            return

        warn_count = len(warnings) if isinstance(warnings, list) else 0
        rec_count = len(recommendations) if isinstance(recommendations, list) else 0
        total = warn_count + rec_count

        if total == 0:
            return

        sev = 'info'
        if warn_count > 20:
            sev = 'medium'
        elif warn_count > 10:
            sev = 'low'

        sample_warnings = []
        if isinstance(warnings, list):
            sample_warnings = [str(w)[:80] for w in warnings[:3]]

        self._add(
            category='advisories',
            severity=sev,
            title=f'{warn_count} warnings, {rec_count} recommendations',
            description=(
                f'Pipeline generated {warn_count} warnings and {rec_count} recommendations. '
                + (f'Sample: {"; ".join(sample_warnings)}.' if sample_warnings else '')
            ),
            evidence={
                'warning_count': warn_count,
                'recommendation_count': rec_count,
                'total_advisories': total,
                'sample_warnings': sample_warnings,
            },
            interpretation='Advisories surface issues found during structural analysis that may need attention.',
            recommendation='Review warnings first -- they indicate potential problems.',
            effort='low',
            drill_down={'key': 'warnings'},
        )

    def _interpret_file_landscape(self):
        """Interpret file index and boundaries -- file distribution health."""
        files = self.data.get('files', {})
        boundaries = self.data.get('file_boundaries', {})

        if not files and not boundaries:
            return

        file_count = len(files) if isinstance(files, dict) else 0
        boundary_count = len(boundaries) if isinstance(boundaries, (dict, list)) else 0

        if file_count == 0 and boundary_count == 0:
            return

        # Compute atoms per file distribution if available
        atoms_per_file = {}
        if isinstance(files, dict):
            for fpath, fdata in files.items():
                count = len(fdata) if isinstance(fdata, list) else (fdata.get('atom_count', 0) if isinstance(fdata, dict) else 0)
                atoms_per_file[fpath] = count

        large_files = {f: c for f, c in atoms_per_file.items() if c > 50}
        avg_atoms = sum(atoms_per_file.values()) / max(len(atoms_per_file), 1) if atoms_per_file else 0

        sev = 'info'
        if len(large_files) > 10:
            sev = 'medium'
        elif len(large_files) > 3:
            sev = 'low'

        self._add(
            category='files',
            severity=sev,
            title=f'File landscape: {file_count} files, {boundary_count} boundaries',
            description=(
                f'{file_count} files indexed with {boundary_count} boundaries. '
                f'Avg atoms/file: {avg_atoms:.1f}.'
                + (f' {len(large_files)} large files (>50 atoms).' if large_files else '')
            ),
            evidence={
                'file_count': file_count,
                'boundary_count': boundary_count,
                'avg_atoms_per_file': round(avg_atoms, 1),
                'large_file_count': len(large_files),
                'large_files_sample': list(large_files.keys())[:5],
            },
            interpretation='File landscape shows how atoms distribute across files. Large files may need decomposition.',
            recommendation='Consider splitting files with >50 atoms into focused modules.' if large_files else 'File sizes are healthy.',
            effort='medium' if large_files else 'low',
            drill_down={'key': 'files'},
        )

    def _interpret_classification_coverage(self):
        """Interpret classification and auto-discovery -- type system coverage."""
        cls = self.data.get('classification', {})
        auto = self.data.get('auto_discovery', {})

        if not cls and not auto:
            return

        classified_count = cls.get('classified', 0) if isinstance(cls, dict) else 0
        unclassified_count = cls.get('unclassified', 0) if isinstance(cls, dict) else 0
        total = classified_count + unclassified_count

        auto_discoveries = auto.get('discoveries', []) if isinstance(auto, dict) else (auto if isinstance(auto, list) else [])
        auto_count = len(auto_discoveries)

        if total == 0 and auto_count == 0:
            return

        coverage_pct = (classified_count / total * 100) if total else 0

        sev = 'info'
        if coverage_pct < 50 and total > 0:
            sev = 'medium'
        elif coverage_pct < 80 and total > 0:
            sev = 'low'

        self._add(
            category='purpose',
            severity=sev,
            title=f'Classification: {coverage_pct:.0f}% coverage' + (f' (+{auto_count} auto-discovered)' if auto_count else ''),
            description=(
                f'{classified_count} of {total} nodes classified.'
                + (f' {auto_count} patterns auto-discovered.' if auto_count else '')
            ),
            evidence={
                'classified': classified_count,
                'unclassified': unclassified_count,
                'total': total,
                'coverage_percent': round(coverage_pct, 1),
                'auto_discovery_count': auto_count,
            },
            interpretation='Classification coverage measures how well the Standard Model taxonomy maps to the codebase.',
            recommendation='Review unclassified nodes -- they may represent new atom types.' if unclassified_count > 0 else 'Full classification coverage.',
            effort='medium' if unclassified_count > 10 else 'low',
            drill_down={'key': 'classification'},
        )

    def _interpret_edge_diversity(self):
        """Interpret edge type distribution -- connectivity diversity."""
        et = self.data.get('edge_types', {})
        if not et or not isinstance(et, dict):
            return

        total_typed = sum(et.values())
        if total_typed == 0:
            return

        type_count = len(et)
        dominant_type = max(et.items(), key=lambda x: x[1]) if et else ('?', 0)
        dominant_pct = dominant_type[1] / total_typed * 100 if total_typed else 0

        sev = 'info'
        if type_count == 1 and total_typed > 10:
            sev = 'low'  # Monomorphic connectivity
        elif dominant_pct > 90:
            sev = 'low'

        self._add(
            category='topology',
            severity=sev,
            title=f'Edge diversity: {type_count} types across {total_typed} edges',
            description=(
                f'{type_count} edge types detected. '
                f'Dominant: {dominant_type[0]} ({dominant_pct:.0f}%). '
                f'Distribution: {", ".join(f"{k}={v}" for k, v in sorted(et.items(), key=lambda x: -x[1])[:5])}.'
            ),
            evidence={
                'type_count': type_count,
                'total_typed_edges': total_typed,
                'dominant_type': dominant_type[0],
                'dominant_percent': round(dominant_pct, 1),
                'distribution': dict(sorted(et.items(), key=lambda x: -x[1])[:10]),
            },
            interpretation=(
                'Edge diversity reflects how nodes connect. Healthy codebases have '
                'import and call edges in balance. Monomorphic graphs (>90% one type) '
                'may indicate shallow analysis resolution.'
            ),
            recommendation='Investigate if import-only graphs lack call resolution.' if dominant_pct > 90 else 'Edge diversity is healthy.',
            effort='low',
            drill_down={'key': 'edge_types'},
        )

    def _interpret_codome_boundary(self):
        """Interpret codome boundaries -- boundary layer health."""
        cb = self.data.get('codome_boundaries', {})
        if not cb:
            return

        boundary_nodes = cb.get('boundary_nodes', [])
        inferred_edges = cb.get('inferred_edges', [])
        total_boundaries = cb.get('total_boundaries', 0) or len(boundary_nodes)
        total_inferred = cb.get('total_inferred_edges', 0) or len(inferred_edges)

        if total_boundaries == 0 and total_inferred == 0:
            return

        nodes_total = self.kpis.get('nodes_total', 1) or 1
        boundary_ratio = total_boundaries / nodes_total

        sev = 'info'
        if boundary_ratio > 0.3:
            sev = 'low'  # Many boundary nodes = high surface area

        self._add(
            category='constraints',
            severity=sev,
            title=f'Codome boundaries: {total_boundaries} boundary nodes, {total_inferred} inferred edges',
            description=(
                f'{total_boundaries} codome boundary nodes ({boundary_ratio:.0%} of all nodes). '
                f'{total_inferred} cross-boundary edges inferred.'
            ),
            evidence={
                'total_boundaries': total_boundaries,
                'total_inferred_edges': total_inferred,
                'boundary_ratio': round(boundary_ratio, 4),
                'nodes_total': nodes_total,
            },
            interpretation=(
                'Codome boundaries mark where code modules interface with each other. '
                'High boundary ratios (>30%) suggest a highly interconnected or fragmented architecture.'
            ),
            recommendation='Review boundary nodes to identify tightly-coupled modules.' if boundary_ratio > 0.3 else 'Boundary surface area is reasonable.',
            effort='medium' if boundary_ratio > 0.3 else 'low',
            drill_down={'key': 'codome_boundaries'},
        )

    def _interpret_chemistry(self):
        """Interpret cross-signal chemistry: syndromes, contradictions, modulations."""
        chem = self.data.get('chemistry', {})
        if not chem:
            return

        syndromes = chem.get('syndromes', [])
        contradictions = chem.get('contradictions', [])
        modulations = chem.get('modulations', [])
        compound = chem.get('compound_severity', 0.0)
        coverage = chem.get('signal_coverage', 0.0)

        # --- Summary finding (always emitted when chemistry data exists) ---
        syn_names = [s['name'] for s in syndromes] if syndromes else []
        if compound > 0.6:
            sev = 'critical'
        elif compound > 0.3:
            sev = 'high'
        elif syndromes:
            sev = 'medium'
        else:
            sev = 'info'

        self._add(
            category='chemistry',
            severity=sev,
            title='Cross-Signal Chemistry Summary',
            description=(
                f'Compound severity {compound:.2f}, {len(syndromes)} syndromes active, '
                f'{len(contradictions)} contradictions, signal coverage {coverage:.0%}.'
            ),
            evidence={'syndromes': syn_names, 'compound_severity': compound, 'coverage': coverage},
            interpretation=(
                'Data chemistry detects compound syndromes and contradictions across '
                'otherwise-independent quality signals. High compound severity indicates '
                'correlated failures that amplify each other.'
            ),
            recommendation='Review active syndromes for compounding quality issues.' if syndromes else None,
        )

        # --- Per-syndrome findings ---
        for syn in syndromes:
            name = syn.get('name', 'unknown')
            severity = syn.get('severity', 0.0)
            sev = 'critical' if severity > 0.7 else ('high' if severity > 0.4 else 'medium')
            entities = syn.get('affected_entities', [])
            desc = syn.get('description', f'Compound syndrome {name} detected (severity={severity:.2f}).')
            if entities:
                desc += f' Affects {len(entities)} entities.'
            evidence = dict(syn.get('signals', {}))
            if entities:
                evidence['affected_entities'] = entities[:10]
            self._add(
                category='chemistry',
                severity=sev,
                title=f'Syndrome: {name}',
                description=desc,
                evidence=evidence,
                interpretation=f'This syndrome emerges from correlated signals that together indicate a systemic pattern.',
                recommendation=f'Address contributing signals to resolve {name} syndrome.',
            )

        # --- Per-contradiction findings ---
        for contra in contradictions:
            hint = contra.get('resolution_hint', '')
            entities = contra.get('affected_entities', [])
            evidence = dict(contra.get('signals', {}))
            if entities:
                evidence['affected_entities'] = entities[:10]
            rec = hint if hint else (
                'Investigate data quality -- contradictory signals may indicate '
                'measurement error or genuine architectural tension.'
            )
            self._add(
                category='chemistry',
                severity='medium',
                title=f'Signal Contradiction: {contra.get("signal_a", "?")} vs {contra.get("signal_b", "?")}',
                description=contra.get('description', 'Contradictory signals detected.'),
                evidence=evidence,
                interpretation=(
                    'Contradictory signals may indicate measurement error, genuine architectural '
                    'tension, or a codebase in active transition.'
                ),
                recommendation=rec,
            )

        # --- Significant modulations (|1 - coeff| > 0.05) ---
        sig_mods = [m for m in modulations if abs(1.0 - m.get('coefficient', 1.0)) > 0.05]
        if sig_mods:
            targets = sorted({m['target'] for m in sig_mods})
            self._add(
                category='chemistry',
                severity='info',
                title='Score Modulations Applied',
                description=f'{len(sig_mods)} modulations affecting: {", ".join(targets)}.',
                evidence={'modulation_count': len(sig_mods), 'targets': targets},
                interpretation=(
                    'Chemistry modulations adjust health, incoherence, and mission matrix scores '
                    'based on cross-signal correlations detected by the lab.'
                ),
            )

        # --- Convergence finding (nodes with 3+ negative signals) ---
        conv = chem.get('convergence', {})
        if conv and conv.get('convergent_count', 0) > 0:
            n_conv = conv['convergent_count']
            n_crit = conv.get('critical_count', 0)
            total = conv.get('total_nodes', 0)
            top_nodes = conv.get('convergent_nodes', [])[:5]
            top_names = [
                f"{n.get('name', '?')} ({n.get('signal_count', 0)} signals)"
                for n in top_nodes
            ]
            sev = 'critical' if n_crit > 10 else ('high' if n_crit > 0 else 'medium')
            self._add(
                category='chemistry',
                severity=sev,
                title='Node-Level Signal Convergence',
                description=(
                    f'{n_conv} of {total} nodes have 3+ converging negative signals '
                    f'({n_crit} critical with 5+).'
                ),
                evidence={
                    'convergent_count': n_conv,
                    'critical_count': n_crit,
                    'total_nodes': total,
                    'top_entities': top_names,
                    'signal_distribution': conv.get('signal_distribution', {}),
                },
                interpretation=(
                    'Nodes where multiple negative signals converge are high-priority '
                    'improvement targets. Critical nodes (5+ signals) represent the '
                    'most structurally deficient parts of the codebase.'
                ),
                recommendation=(
                    'Prioritize critical-convergence nodes for docstrings, type annotations, '
                    'and architectural clarification. Each fix removes multiple signals at once.'
                ),
            )

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
