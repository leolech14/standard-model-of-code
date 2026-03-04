"""Phase 5: Intelligence — Data Flow, Performance, Constraints, Purpose Intelligence."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    """Print progress message unless quiet mode is active."""
    if not quiet:
        print(msg)


def run_intelligence(ctx: 'PipelineContext') -> None:
    """Execute all intelligence sub-stages.

    Stages 7, 8, 8.5, 8.6 + color scale application.
    """
    from observability import StageTimer

    # Stage 7: Data Flow
    print("\n🌊 Stage 7: Data Flow Analysis...")
    with StageTimer(ctx.perf_manager, "Stage 7: Data Flow Analysis") as timer:
        from src.core.topology_analysis import compute_data_flow
        ctx.data_flow = compute_data_flow(ctx.nodes, ctx.edges)
        timer.set_output(sources=len(ctx.data_flow['data_sources']), sinks=len(ctx.data_flow['data_sinks']))
    _log(f"   → {len(ctx.data_flow['data_sources'])} data sources", ctx.quiet)
    _log(f"   → {len(ctx.data_flow['data_sinks'])} data sinks", ctx.quiet)
    ctx.data_ledger.publish("data_flow", "Stage 7: Data Flow Analysis",
        summary=f"{len(ctx.data_flow['data_sources'])} sources, {len(ctx.data_flow['data_sinks'])} sinks")

    # Stage 8: Performance Prediction
    print("\n⏱️  Stage 8: Performance Prediction...")
    with StageTimer(ctx.perf_manager, "Stage 8: Performance Prediction") as timer:
        try:
            from src.core.performance_predictor import predict_performance
            perf = predict_performance(ctx.nodes, ctx.exec_flow)
            ctx.perf_summary = perf.summary() if hasattr(perf, 'summary') else {}
            ctx.data_ledger.publish("performance", "Stage 8: Performance Prediction")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️  Performance prediction skipped: {e}")
            ctx.perf_summary = {}
            ctx.data_ledger.publish("performance", "Stage 8: Performance Prediction", status="skipped", summary=str(e))

    # Stage 8.5: Constraint Field Validation
    print("\n🚧 Stage 8.5: Constraint Field Validation...")
    ctx.constraint_report = {}
    with StageTimer(ctx.perf_manager, "Stage 8.5: Constraint Validation") as timer:
        try:
            from constraint_engine import ConstraintEngine
            engine = ConstraintEngine()
            ctx.constraint_report = engine.validate_graph(ctx.nodes, ctx.edges)
            timer.set_output(
                antimatter=ctx.constraint_report['antimatter']['count'],
                policy=ctx.constraint_report['policy_violations']['count'],
                signals=ctx.constraint_report['signals']['count']
            )
            # Show architecture detection
            arch_detect = ctx.constraint_report.get('architecture_detection', {})
            if arch_detect:
                is_layered = arch_detect.get('is_layered', False)
                arch_type = "Layered" if is_layered else "Non-layered"
                _log(f"   → Architecture: {arch_type} (confidence: {arch_detect.get('confidence', 0):.0%})", ctx.quiet)
                if ctx.constraint_report.get('layer_validation_skipped'):
                    _log(f"   → Layer constraints: SKIPPED (non-layered codebase)", ctx.quiet)
            _log(f"   → Antimatter (Tier A): {ctx.constraint_report['antimatter']['count']}", ctx.quiet)
            _log(f"   → Policy (Tier B): {ctx.constraint_report['policy_violations']['count']}", ctx.quiet)
            _log(f"   → Signals (Tier C): {ctx.constraint_report['signals']['count']}", ctx.quiet)
            _log(f"   → Valid: {ctx.constraint_report['valid']}", ctx.quiet)
            ctx.data_ledger.publish("constraints", "Stage 8.5: Constraint Validation",
                summary=f"antimatter={ctx.constraint_report['antimatter']['count']}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Constraint validation skipped: {e}")
            ctx.data_ledger.publish("constraints", "Stage 8.5: Constraint Validation", status="skipped", summary=str(e))

    # Stage 8.6: Purpose Intelligence (Q-Scores)
    print("\n🧠 Stage 8.6: Purpose Intelligence...")
    ctx.codebase_intelligence = {}
    with StageTimer(ctx.perf_manager, "Stage 8.6: Purpose Intelligence") as timer:
        try:
            from purpose_intelligence import enrich_nodes_with_intelligence
            ctx.nodes, ctx.codebase_intelligence = enrich_nodes_with_intelligence(ctx.nodes, ctx.edges)
            timer.set_output(
                codebase_q=ctx.codebase_intelligence.get('codebase_intelligence', 0),
                interpretation=ctx.codebase_intelligence.get('interpretation', 'Unknown'),
            )
            _log(f"   → Codebase Intelligence: {ctx.codebase_intelligence.get('codebase_intelligence', 0):.3f}", ctx.quiet)
            _log(f"   → Interpretation: {ctx.codebase_intelligence.get('interpretation', 'Unknown')}", ctx.quiet)
            dist = ctx.codebase_intelligence.get('distribution', {})
            _log(f"   → Distribution: {dist.get('excellent', 0)} excellent, {dist.get('good', 0)} good, {dist.get('moderate', 0)} moderate, {dist.get('poor', 0)} poor", ctx.quiet)
            ctx.data_ledger.publish("purpose_intelligence", "Stage 8.6: Purpose Intelligence",
                summary=f"Q={ctx.codebase_intelligence.get('codebase_intelligence', 0):.3f}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Purpose Intelligence skipped: {e}")
            ctx.data_ledger.publish("purpose_intelligence", "Stage 8.6: Purpose Intelligence", status="skipped", summary=str(e))

    # Apply data-driven color scales to nodes (metric_color field)
    try:
        from src.core.viz.color_science import (
            SCALE_COMPLEXITY, apply_scale_to_nodes,
        )
        apply_scale_to_nodes(ctx.nodes, 'cyclomatic_complexity', SCALE_COMPLEXITY, 'complexity_color')
        _log("   → Color scales applied to nodes", ctx.quiet)
    except Exception as e:
        _log(f"   ⚠️ Color scale application skipped: {e}", ctx.quiet)

    # NOTE: Multi-channel OKLCH encoding is applied after Stage 20 (Data Chemistry)
    # so that convergence data is available for tagging. See synthesis phase.
