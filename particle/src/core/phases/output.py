"""Phase 7: Output — Insights Compilation, Output Generation, Pipeline Report, Summary."""

from __future__ import annotations
import hashlib
import json
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    if not quiet:
        print(msg)


def run_output(ctx: PipelineContext) -> None:
    """Execute output generation stages.

    Covers:
    - Stage 21: Insights Compilation
    - Stage 21.5: Meta-Envelope (identity for cross-run analysis)
    - Stage 22: Output Generation (tiered: raw + briefing + report)
    - Pipeline report generation
    - Enhanced final summary
    - Cleanup (database disconnection)
    """
    _run_insights(ctx)        # Stage 21
    _build_meta_envelope(ctx) # Stage 21.5: Identity envelope
    _run_output_gen(ctx)      # Stage 22
    _write_report(ctx)        # Pipeline report
    _print_summary(ctx)       # Final summary with stage timing
    _cleanup(ctx)             # DB disconnect, summary print


def _run_insights(ctx: PipelineContext) -> None:
    """Stage 21: Insights Compilation."""
    from observability import StageTimer

    print("\n🔬 Stage 21: Insights Compilation...")
    with StageTimer(ctx.perf_manager, "Stage 21: Insights Compilation") as timer:
        try:
            from src.core.insights_compiler import compile_insights, compile_insights_report
            compiled_dict = compile_insights(ctx.full_output, repo_root=ctx.target)
            ctx.full_output['compiled_insights'] = compiled_dict
            # Generate markdown for file output
            report_obj = compile_insights_report(ctx.full_output, repo_root=ctx.target)
            ctx.full_output['_insights_markdown'] = report_obj.to_markdown()
            grade = compiled_dict.get('grade', '?')
            finding_count = compiled_dict.get('findings_count', 0)
            timer.set_output(grade=grade, findings=finding_count)
            _log(f"   → Grade: {grade} ({compiled_dict.get('health_score', 0)}/10)", ctx.quiet)
            _log(f"   → {finding_count} findings compiled", ctx.quiet)

            ctx.data_ledger.publish("insights", "Stage 21: Insights Compilation",
                summary=f"grade={compiled_dict.get('grade', '?')}, {finding_count} findings")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Insights compilation failed: {e}")
            ctx.data_ledger.publish("insights", "Stage 21: Insights Compilation", status="failed", summary=str(e))


def _build_meta_envelope(ctx: PipelineContext) -> None:
    """Stage 21.5: Build meta-envelope for cross-run identity and analysis."""
    try:
        from src.core.meta_envelope import build_meta_envelope
        ctx.meta_envelope = build_meta_envelope(
            ctx.full_output, ctx.target, ctx.options
        )
        _log(f"   → Meta-envelope: repo={ctx.meta_envelope.get('repo_id', '?')}, "
             f"run={ctx.meta_envelope.get('run_id', '?')[:8]}", ctx.quiet)
    except Exception as e:
        print(f"   ⚠️ Meta-envelope build failed (non-fatal): {e}")
        ctx.meta_envelope = None


def _run_output_gen(ctx: PipelineContext) -> None:
    """Stage 22: Write consolidated outputs with waybill attachment."""
    from observability import StageTimer

    print("\n📦 Stage 22: Generating Consolidated Outputs...")

    with StageTimer(ctx.perf_manager, "Stage 22: Output Generation") as timer:
        try:
            # Update performance data INSIDE timer (captures stages 1-11 timing)
            ctx.full_output['pipeline_performance'] = ctx.perf_manager.to_dict()

            from src.core.output_generator import generate_outputs
            skip_html = ctx.options.get("skip_html", False)

            # Attach Waybills to individual nodes (Phase 28)
            if not ctx.quiet:
                print(f"   → Attaching waybills to {len(ctx.nodes)} particles...")
            for node in ctx.nodes:
                node_id = node.get('id', node.get('name', 'unknown'))

                # Baseline waybill
                waybill = {
                    "parcel_id": f"pcl_{hashlib.sha256(f'{node_id}-{ctx.batch_id}'.encode()).hexdigest()[:12]}",
                    "parent_id": f"pcl_{hashlib.sha256(ctx.merkle_root.encode()).hexdigest()[:12]}",
                    "batch_id": ctx.batch_id,
                    "merkle_root": ctx.merkle_root,
                    "refinery_signature": ctx.refinery_signature,
                }

                # Padding bloat for non AI modes
                if not skip_html:
                    waybill["context_vector"] = [0.0] * 32
                    waybill["route"] = [
                        {
                            "event": "refined",
                            "timestamp": time.time(),
                            "agent": "full_analysis.py",
                            "context": {"batch": ctx.batch_id}
                        }
                    ]

                node['waybill'] = waybill

            verbose_output = ctx.options.get("verbose_output", False)
            webgl = ctx.options.get("webgl", False)
            outputs = generate_outputs(
                ctx.full_output,
                ctx.output_dir,
                target_name=ctx.target.name,
                skip_html=skip_html,
                verbose_output=verbose_output,
                meta_envelope=ctx.meta_envelope,
                webgl=webgl,
            )
            ctx.unified_json = outputs["llm"]
            ctx.viz_file = outputs.get("html")
            timer.set_output(json=1, html=1 if ctx.viz_file else 0)
            _log(f"   → Tier 1 (raw):     {ctx.unified_json}", ctx.quiet)
            if outputs.get("briefing"):
                _log(f"   → Tier 2 (briefing): {outputs['briefing']}", ctx.quiet)
            if outputs.get("report_html"):
                _log(f"   → Tier 3 (report):   {outputs['report_html']}", ctx.quiet)
            if "tokens" in outputs:
                for k, v in outputs["tokens"].items():
                    if isinstance(v, dict):
                        print(f"      - {k}:")
                        for sub_k, sub_v in sorted(v.items(), key=lambda x: str(x[0])):
                            print(f"         * {sub_k}: {sub_v:,} tokens")
                    else:
                        print(f"      - {k}: {v:,} tokens")
            if ctx.viz_file:
                _log(f"   → WebGL: {ctx.viz_file}", ctx.quiet)
            elif webgl:
                _log(f"   → WebGL: SKIPPED (--no-html)", ctx.quiet)
            ctx.data_ledger.publish("output_gen", "Stage 22: Output Generation")
        except Exception as e:
            timer.set_status("FAIL", str(e))
            print(f"   ⚠️ Output generation failed: {e}")
            ctx.data_ledger.publish("output_gen", "Stage 22: Output Generation", status="failed", summary=str(e))


def _write_report(ctx: PipelineContext) -> None:
    """Write standalone pipeline report JSON."""
    from src.core.full_analysis import _write_pipeline_report

    total_time = time.time() - ctx.start_time

    # =========================================================================
    # PIPELINE REPORT: Always write standalone JSON (cheap, enables automation)
    # Report is also written in the except block below for crash resilience.
    # =========================================================================
    ctx.report_path = _write_pipeline_report(
        ctx.perf_manager, ctx.output_dir, ctx.target, total_time, ctx.nodes, ctx.edges,
        data_ledger=ctx.data_ledger,
    )


def _print_summary(ctx: PipelineContext) -> None:
    """Print enhanced final summary with stage timing."""
    total_time = time.time() - ctx.start_time
    peak_mb = ctx.perf_manager._peak_memory_kb / 1024 if ctx.perf_manager._peak_memory_kb else 0
    open_latest = ctx.options.get("open_latest", False)
    if ctx.options.get("no_open", False):
        open_latest = False
    timing_enabled = ctx.options.get("timing", False)
    verbose_timing = ctx.options.get("verbose_timing", False)

    # =========================================================================
    # ENHANCED FINAL SUMMARY (always shown, even in quiet mode)
    # =========================================================================
    print("\n" + "=" * 60)
    print("COLLIDER FULL ANALYSIS COMPLETE")
    print(f"   Target: {ctx.target.name}")
    print(f"   Time:   {total_time:.1f}s | Memory: {peak_mb:,.0f} MB peak")
    print(f"   Graph:  {len(ctx.nodes):,} nodes, {len(ctx.edges):,} edges")
    print(f"   {ctx.data_ledger.summary_line()}")

    # Compact stage timing table
    if ctx.perf_manager.stages:
        print()
        print("   Stage Timing:")
        for stage in ctx.perf_manager.stages:
            # Clean stage name (remove "Stage X.Y: " prefix for display)
            name = stage.stage_name
            if ": " in name:
                name = name.split(": ", 1)[1]
            # Format timing
            if stage.latency_ms >= 1000:
                time_str = f"{stage.latency_ms / 1000:.1f}s"
            else:
                time_str = f"{stage.latency_ms:.0f}ms"
            # Dot-pad alignment
            pad = "." * max(1, 28 - len(name))
            print(f"   {name} {pad} {time_str:>8}   {stage.status}")

        # Identify bottleneck
        slowest = ctx.perf_manager.get_slowest_stage()
        if slowest and total_time > 0:
            pct = (slowest['latency_ms'] / 1000 / total_time * 100)
            print(f"\n   Bottleneck: {slowest['name']} ({slowest['latency_ms'] / 1000:.1f}s, {pct:.0f}%)")

    print()
    if ctx.report_path:
        print(f"   Report: {ctx.report_path}")
    if ctx.unified_json:
        print(f"   Data:   {ctx.unified_json}")
    if ctx.viz_file:
        print(f"   Visual: {ctx.viz_file}")

    # Detailed timing if requested
    if timing_enabled and not verbose_timing:
        ctx.perf_manager.print_summary()

    if open_latest:
        from src.core.full_analysis import _find_latest_html, _open_file, _manual_open_command
        latest_html = _find_latest_html(ctx.output_dir)
        if latest_html:
            print(f"   Open:   {latest_html}")
            print(f"   Manual: {_manual_open_command(latest_html)}")
            if not _open_file(latest_html):
                print("   Open failed (see system logs for details).")
        else:
            print("   No HTML outputs found to open.")

    print("=" * 60)


def _cleanup(ctx: PipelineContext) -> None:
    """Close database connection and print final summary."""
    total_time = time.time() - ctx.start_time

    # Close database connection
    if ctx.db_manager:
        try:
            ctx.db_manager.disconnect()
        except Exception:  # noqa: best-effort cleanup
            pass

    summary = {
        "status": "complete",
        "nodes": ctx.full_output.get("counts", {}).get("nodes", 0),
        "edges": ctx.full_output.get("counts", {}).get("edges", 0),
        "stages": len(ctx.perf_manager.stages) if ctx.perf_manager and hasattr(ctx.perf_manager, "stages") else 0,
        "elapsed_s": round(total_time, 3),
    }
    print(f"PIPELINE_SUMMARY: {json.dumps(summary)}")
