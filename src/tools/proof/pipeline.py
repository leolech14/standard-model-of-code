"""
Proof Pipeline
==============

Orchestrates all stages of the Standard Model proof.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .stages import (
    StageResult,
    stage_classification,
    stage_role_distribution,
    stage_antimatter,
    stage_predictions,
    stage_insights,
    stage_purpose_field,
    stage_execution_flow,
    stage_performance,
)
from .document import ProofDocumentBuilder, ProofDocument
from .visualization import VisualizationGenerator, enrich_state_with_results


class ProofPipeline:
    """
    Orchestrates the 10-stage proof pipeline.

    Usage:
        pipeline = ProofPipeline(target_path)
        result = pipeline.run()
    """

    def __init__(self, target_path: str, verbose: bool = True):
        self.target_path = Path(target_path).resolve()
        self.verbose = verbose
        self.stage_results: Dict[str, StageResult] = {}

        # Will be set during initialization
        self._analyze_func = None
        self._evaluator_class = None
        self._generate_insights_func = None
        self._detect_purpose_func = None
        self._detect_flow_func = None
        self._predict_perf_func = None
        self._state_class = None

    def _log(self, message: str):
        """Log message if verbose mode is on."""
        if self.verbose:
            print(message)

    def _log_stage_header(self, stage_num: int, name: str):
        """Print stage header."""
        if self.verbose:
            print(f"{'':─<69}┐")
            print(f"│ STAGE {stage_num}: {name:56} │")
            print(f"└{'':─<69}")

    def _initialize_dependencies(self):
        """Import all required dependencies."""
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'core'))

        from unified_analysis import analyze
        from antimatter_evaluator import AntimatterEvaluator
        from insights_engine import generate_insights
        from purpose_field import detect_purpose_field
        from execution_flow import detect_execution_flow
        from performance_predictor import predict_performance
        from data_management import CodebaseState

        self._analyze_func = analyze
        self._evaluator_class = AntimatterEvaluator
        self._generate_insights_func = generate_insights
        self._detect_purpose_func = detect_purpose_field
        self._detect_flow_func = detect_execution_flow
        self._predict_perf_func = predict_performance
        self._state_class = CodebaseState

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the complete proof pipeline.

        Returns:
            Proof document as dictionary
        """
        self._initialize_dependencies()

        if not self.target_path.exists():
            self._log(f" Path not found: {self.target_path}")
            return {"error": "Path not found"}

        self._log_header()

        # Stage 1: Classification
        self._log_stage_header(1, "CLASSIFICATION")
        classification = stage_classification(
            str(self.target_path),
            self._analyze_func,
            **kwargs
        )
        self.stage_results['classification'] = classification

        if not classification.success:
            self._log(f" Analysis failed: {classification.error}")
            return {"error": classification.error}

        nodes = classification.data['nodes']
        edges = classification.data['edges']
        classification_time = classification.data['classification_time']

        self._log(f"   Nodes extracted: {len(nodes)}")
        self._log(f"   Edges extracted: {len(edges)}")
        self._log(f"   Time: {classification_time:.2f}s")

        # Initialize state
        state = self._state_class(str(self.target_path))
        state.load_initial_graph(nodes, edges)
        self._log(f"   State initialized with {len(nodes)} nodes\n")

        # Stage 2: Role Distribution
        self._log_stage_header(2, "ROLE DISTRIBUTION")
        role_result = stage_role_distribution(nodes)
        self.stage_results['role_distribution'] = role_result
        self._log_role_distribution(role_result.data, len(nodes))

        # Stage 3: Antimatter
        self._log_stage_header(3, "ANTIMATTER VIOLATIONS")
        antimatter = stage_antimatter(nodes, self._evaluator_class)
        self.stage_results['antimatter'] = antimatter
        self._log_antimatter(antimatter)

        # Stage 4: Predictions
        self._log_stage_header(4, "PREDICTIONS (Missing Components)")
        predictions = stage_predictions(role_result.data)
        self.stage_results['predictions'] = predictions
        self._log_predictions(predictions.data['predictions'])

        # Stage 5: Insights
        self._log_stage_header(5, "ACTIONABLE INSIGHTS")
        insights = stage_insights(nodes, edges, self._generate_insights_func)
        self.stage_results['insights'] = insights
        self._log_insights(insights)

        # Stage 6: Purpose Field
        self._log_stage_header(6, "PURPOSE FIELD")
        purpose = stage_purpose_field(nodes, edges, self._detect_purpose_func)
        self.stage_results['purpose_field'] = purpose
        self._log_purpose_field(purpose, len(nodes))

        # Stage 7: Execution Flow
        self._log_stage_header(7, "EXECUTION FLOW")
        purpose_field_obj = purpose.data.get('purpose_field')
        flow = stage_execution_flow(nodes, edges, purpose_field_obj, self._detect_flow_func)
        self.stage_results['execution_flow'] = flow
        self._log_execution_flow(flow)

        # Stage 8: Performance
        self._log_stage_header(8, "PERFORMANCE PREDICTION")
        exec_flow_obj = flow.data.get('exec_flow')
        perf = stage_performance(nodes, exec_flow_obj, self._predict_perf_func)
        self.stage_results['performance'] = perf
        self._log_performance(perf)

        # Stage 9: Build Document
        self._log_stage_header(9, "SUMMARY")
        doc = self._build_document(
            nodes, edges,
            role_result.data,
            classification_time,
            antimatter.data,
            predictions.data['predictions'],
            insights.data,
            purpose.data,
            flow.data,
            perf.data
        )
        self._log_summary(doc, len(nodes), classification_time)

        # Stage 10: Visualization
        self._log_stage_header(10, "VISUALIZATION GENERATION")
        output_dir = Path(kwargs.get('output_dir', '.'))
        self._generate_visualization(
            state, doc, output_dir,
            purpose_field_obj, exec_flow_obj, perf.data.get('perf_profile')
        )

        # Save proof document
        self._save_document(doc, output_dir)

        self._log_footer()

        return doc.to_dict()

    def _log_header(self):
        """Print pipeline header."""
        self._log("=" * 70)
        self._log(" COLLIDER - Standard Model of Code")
        self._log("=" * 70)
        self._log(f"\nTarget: {self.target_path}")
        self._log(f"Time:   {datetime.now().isoformat()}\n")

    def _log_footer(self):
        """Print pipeline footer."""
        self._log("\n" + "=" * 70)
        self._log(" PROOF COMPLETE")
        self._log("=" * 70)
        self._log("\nThis analysis is REPRODUCIBLE. Run again to verify.\n")

    def _log_role_distribution(self, role_data: Dict, total_nodes: int):
        """Log role distribution results."""
        role_counts = role_data['role_counts']
        self._log("  Roles detected:")
        for role, count in sorted(role_counts.items(), key=lambda x: -x[1])[:10]:
            pct = count / total_nodes * 100 if total_nodes else 0
            self._log(f"    {role:25} {count:6} ({pct:5.1f}%)")
        if len(role_counts) > 10:
            self._log(f"    ... and {len(role_counts) - 10} more roles")
        self._log(f"\n   Coverage: {role_data['coverage']:.1f}% (non-Unknown)")
        self._log(f"   Average confidence: {role_data['average_confidence']:.1f}%\n")

    def _log_antimatter(self, result: StageResult):
        """Log antimatter results."""
        if result.error:
            self._log(f"   Antimatter evaluation skipped: {result.error}")
        elif result.data['violation_count'] > 0:
            violations = result.data['violations']
            self._log(f"   Found {len(violations)} violations:")
            for v in violations[:5]:
                self._log(f"    - [{v.severity.upper()}] {v.law_name}: {v.particle_name}")
            if len(violations) > 5:
                self._log(f"    ... and {len(violations) - 5} more")
        else:
            self._log("   No antimatter violations detected")
        self._log("")

    def _log_predictions(self, predictions: list):
        """Log prediction results."""
        if predictions:
            self._log("   Predictions:")
            for p in predictions:
                self._log(f"     {p}")
        else:
            self._log("   Architecture appears complete")
        self._log("")

    def _log_insights(self, result: StageResult):
        """Log insights results."""
        if result.error:
            self._log(f"   Insights generation skipped: {result.error}")
        elif result.data['insights']:
            insights = result.data['insights']
            self._log(f"  Found {len(insights)} actionable insights:")
            priority_icon = {"critical": "", "high": "", "medium": "", "low": ""}
            for insight in insights[:5]:
                icon = priority_icon.get(insight.priority.value, "")
                self._log(f"    {icon} [{insight.priority.value.upper()}] {insight.title}")
            if len(insights) > 5:
                self._log(f"    ... and {len(insights) - 5} more")
        else:
            self._log("   No significant issues detected")
        self._log("")

    def _log_purpose_field(self, result: StageResult, total_nodes: int):
        """Log purpose field results."""
        if result.error:
            self._log(f"   Purpose field detection skipped: {result.error}")
        else:
            summary = result.data['summary']
            self._log("  Layer distribution:")
            for layer, count in summary.get('layers', {}).items():
                if layer != 'unknown':
                    pct = count / total_nodes * 100 if total_nodes else 0
                    self._log(f"    {layer.capitalize():20} {count:5} ({pct:5.1f}%)")

            violations = result.data['violations']
            if violations:
                self._log(f"\n   Purpose flow violations: {len(violations)}")
                for v in violations[:3]:
                    self._log(f"    - {v}")
                if len(violations) > 3:
                    self._log(f"    ... and {len(violations) - 3} more")
            else:
                self._log("\n   No purpose flow violations")
        self._log("")

    def _log_execution_flow(self, result: StageResult):
        """Log execution flow results."""
        if result.error:
            self._log(f"   Execution flow analysis skipped: {result.error}")
        else:
            summary = result.data['summary']
            self._log(f"  Entry points:     {summary.get('entry_points', 0)}")
            self._log(f"  Reachable nodes:  {summary.get('reachable_nodes', 0)}")
            self._log(f"  Orphans:          {summary.get('orphan_count', 0)}")
            self._log(f"  Dead code:        {summary.get('dead_code_percent', 0):.1f}%")
            self._log(f"  Causality chains: {summary.get('chains_count', 0)}")

            orphans = result.data['orphans']
            if orphans:
                self._log(f"\n   Orphan functions (unreachable):")
                for orphan in orphans[:5]:
                    self._log(f"    - {orphan}")
                if len(orphans) > 5:
                    self._log(f"    ... and {len(orphans) - 5} more")
            else:
                self._log("\n   No dead code detected")
        self._log("")

    def _log_performance(self, result: StageResult):
        """Log performance results."""
        if result.error:
            self._log(f"   Performance prediction skipped: {result.error}")
        else:
            summary = result.data['summary']
            self._log("  Time types:")
            total_cost = summary.get('total_estimated_cost', 0)
            for ttype, cost in sorted(summary.get('time_by_type', {}).items(), key=lambda x: -x[1]):
                pct = cost / total_cost * 100 if total_cost else 0
                self._log(f"    {ttype:15} {cost:10.0f} ({pct:5.1f}%)")

            self._log(f"\n  Critical path: {summary.get('critical_path_length', 0)} nodes, cost={summary.get('critical_path_cost', 0):.0f}")
            self._log(f"  Hotspots: {summary.get('hotspot_count', 0)}")

            perf_profile = result.data.get('perf_profile')
            if perf_profile and perf_profile.hotspots:
                self._log(f"\n  Top hotspots:")
                for hs in perf_profile.hotspots[:3]:
                    if hs in perf_profile.nodes:
                        hn = perf_profile.nodes[hs]
                        self._log(f"    - {hn.name} ({hn.time_type.value}, score={hn.hotspot_score:.0f})")
        self._log("")

    def _build_document(
        self,
        nodes, edges,
        role_data: Dict,
        classification_time: float,
        antimatter_data: Dict,
        predictions: list,
        insights_data: Dict,
        purpose_data: Dict,
        flow_data: Dict,
        perf_data: Dict
    ) -> ProofDocument:
        """Build the proof document from all stage results."""
        builder = ProofDocumentBuilder(str(self.target_path))

        return (
            builder
            .with_classification(
                nodes, edges,
                role_data['role_counts'],
                role_data['coverage'],
                role_data['average_confidence'],
                classification_time
            )
            .with_antimatter(
                antimatter_data.get('violations', []),
                antimatter_data.get('violation_count', 0)
            )
            .with_predictions(predictions)
            .with_insights(
                len(insights_data.get('insights', [])),
                insights_data.get('insights_summary', [])
            )
            .with_purpose_field(
                purpose_data.get('summary', {}),
                purpose_data.get('violations', [])
            )
            .with_execution_flow(
                flow_data.get('summary', {}),
                flow_data.get('orphans', [])
            )
            .with_performance(
                perf_data.get('summary', {}),
                perf_data.get('hotspots', [])
            )
            .with_metrics(
                role_data['entities'],
                role_data['repositories'],
                role_data['services'],
                role_data['controllers'],
                role_data['tests']
            )
            .build()
        )

    def _log_summary(self, doc: ProofDocument, total_nodes: int, classification_time: float):
        """Log summary statistics."""
        self._log(f"  Total nodes:      {total_nodes}")
        self._log(f"  Coverage:         {doc.classification.get('coverage_percent', 0):.1f}%")
        self._log(f"  Avg confidence:   {doc.classification.get('average_confidence', 0):.1f}%")
        self._log(f"  Violations:       {doc.antimatter.get('violations_count', 0)}")
        self._log(f"  Predictions:      {len(doc.predictions)}")
        if classification_time > 0:
            self._log(f"  Speed:            {total_nodes/classification_time:.0f} nodes/sec")
        self._log("")

    def _generate_visualization(
        self,
        state,
        doc: ProofDocument,
        output_dir: Path,
        purpose_field=None,
        exec_flow=None,
        perf_profile=None
    ):
        """Generate HTML visualization."""
        try:
            # Enrich state with analysis results
            enrich_state_with_results(state, purpose_field, exec_flow, perf_profile)

            # Generate visualization
            viz_gen = VisualizationGenerator()
            report_path = viz_gen.generate(state, doc.classification, output_dir)

            if report_path:
                self._log(f"   Report generated: {report_path.resolve()}")
            else:
                self._log("   Visualization generation skipped")
        except Exception as e:
            self._log(f"   Visualization generation failed: {e}")

    def _save_document(self, doc: ProofDocument, output_dir: Path):
        """Save proof document to JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "proof_output.json"

        with open(output_file, 'w') as f:
            json.dump(doc.to_dict(), f, indent=2, default=str)

        self._log(f"   Proof saved to: {output_file}")
