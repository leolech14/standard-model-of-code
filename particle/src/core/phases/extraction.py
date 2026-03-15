"""Phase 2: Extraction — Base Analysis, Standard Model, Ecosystem, Levels, Dimensions."""

from __future__ import annotations
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    if not quiet:
        print(msg)


def run_extraction(ctx: PipelineContext) -> None:
    """Execute all extraction sub-stages:

    1. Base Analysis (unified_analysis.analyze)
    2. Standard Model Enrichment (with RPBL scores)
    3. Ecosystem Discovery (hybrid T2 approach)
    4. Holarchy Level Classification (L-3..L12)
    5. Octahedral Dimension Classification (D4, D5, D7)
    """
    from src.core.unified_analysis import analyze
    from src.core.standard_model_enricher import enrich_with_standard_model
    from observability import StageTimer

    # Stage 1: Base analysis
    print("\n🔬 Stage 1: Base Analysis...")
    with StageTimer(ctx.perf_manager, "Stage 1: Base Analysis") as timer:
        analysis_options = dict(ctx.options)
        analysis_options.pop("roadmap", None)
        # Pass survey exclusions to unified analysis (Phase 10 integration)
        if ctx.exclude_paths:
            analysis_options['exclude_paths'] = ctx.exclude_paths
        result = analyze(str(ctx.target), output_dir=str(ctx.output_dir), write_output=False, **analysis_options)
        ctx.nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        ctx.edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
        ctx.unified_stats = getattr(result, 'stats', {}) if hasattr(result, 'stats') else result.get('stats', {})
        ctx.unified_classification = getattr(result, 'classification', {}) if hasattr(result, 'classification') else result.get('classification', {})
        ctx.unified_auto_discovery = getattr(result, 'auto_discovery', {}) if hasattr(result, 'auto_discovery') else result.get('auto_discovery', {})
        ctx.unified_dependencies = getattr(result, 'dependencies', {}) if hasattr(result, 'dependencies') else result.get('dependencies', {})
        ctx.unified_architecture = getattr(result, 'architecture', {}) if hasattr(result, 'architecture') else result.get('architecture', {})
        ctx.unified_llm_enrichment = getattr(result, 'llm_enrichment', {}) if hasattr(result, 'llm_enrichment') else result.get('llm_enrichment', {})
        ctx.unified_warnings = getattr(result, 'warnings', []) if hasattr(result, 'warnings') else result.get('warnings', [])
        ctx.unified_recommendations = getattr(result, 'recommendations', []) if hasattr(result, 'recommendations') else result.get('recommendations', [])
        # Parse manifest from actual parser outcomes (Phase 1 C1)
        ctx.parse_manifest = getattr(result, 'parse_manifest', None) or (
            result.get('parse_manifest') if hasattr(result, '__getitem__') else None
        )
        timer.set_output(nodes=len(ctx.nodes), edges=len(ctx.edges))
    ctx.guard.nodes = ctx.nodes
    ctx.guard.edges = ctx.edges
    _log(f"   → {len(ctx.nodes)} nodes, {len(ctx.edges)} edges", ctx.quiet)
    ctx.data_ledger.publish("nodes", "Stage 1: Base Analysis", summary=f"{len(ctx.nodes)} nodes")
    ctx.data_ledger.publish("edges", "Stage 1: Base Analysis", summary=f"{len(ctx.edges)} edges")
    ctx.flow_tracker.snapshot("After Stage 1: Base Analysis", ctx.nodes, ctx.edges)

    # Stage 2: Standard Model enrichment
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    with StageTimer(ctx.perf_manager, "Stage 2: Standard Model Enrichment") as timer:
        ctx.nodes = enrich_with_standard_model(ctx.nodes)
        rpbl_count = sum(1 for n in ctx.nodes if n.get('rpbl'))

        # Flatten RPBL scores for UPB binding (P4-05/07/08)
        for node in ctx.nodes:
            rpbl = node.get('rpbl', {})
            node['rpbl_responsibility'] = rpbl.get('responsibility', 0)
            node['rpbl_purity'] = rpbl.get('purity', 0)
            node['rpbl_boundary'] = rpbl.get('boundary', 0)
            node['rpbl_lifecycle'] = rpbl.get('lifecycle', 0)

        timer.set_output(nodes=len(ctx.nodes), rpbl_enriched=rpbl_count)
    _log(f"   → {rpbl_count} nodes with RPBL scores", ctx.quiet)
    ctx.data_ledger.publish("standard_model", "Stage 2: Standard Model Enrichment",
        summary=f"{rpbl_count} RPBL-enriched")

    # Pipeline Assertion: Validate canonical roles
    try:
        from registry.role_registry import get_role_registry
        _registry = get_role_registry()
        _invalid = {n.get('role') for n in ctx.nodes if n.get('role') and not _registry.validate(n['role'])}
        if _invalid:
            if os.environ.get('COLLIDER_STRICT_ROLES', '').lower() == 'true':
                raise ValueError(f"Non-canonical roles detected: {_invalid}")
            else:
                print(f"   ⚠️ WARNING: Non-canonical roles: {_invalid}")
    except ImportError:
        pass  # Registry not available, skip validation

    # Stage 2.1: Post-enrichment graph inference pass
    # Graph inference inside unified_analysis (Stage 5) runs BEFORE enrichment,
    # so its 10 graph-topology rules (calls_repository, called_by_controller, etc.)
    # see raw/Unknown neighbor roles and fire 0 times.  This second pass runs
    # AFTER canonical roles are assigned, letting the rules match properly.
    print("\n🧠 Stage 2.1: Post-Enrichment Graph Inference...")
    with StageTimer(ctx.perf_manager, "Stage 2.1: Post-Enrichment Graph Inference") as timer:
        try:
            from graph_type_inference import apply_graph_inference
            ctx.nodes, gi_report = apply_graph_inference(ctx.nodes, ctx.edges)
            inferred = gi_report.get('total_inferred', 0)
            rules = gi_report.get('rules_applied', 0)
            timer.set_output(total_inferred=inferred, rules_applied=rules)
            _log(f"   → {inferred} types inferred ({rules} graph rules applied)", ctx.quiet)
        except ImportError as e:
            timer.set_status("WARN", str(e))
            _log(f"   ⚠️ Graph inference not available: {e}", ctx.quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            _log(f"   ⚠️ Graph inference failed: {e}", ctx.quiet)

    # Stage 2.5: Ecosystem discovery (hybrid T2 approach)
    ctx.ecosystem_discovery = {}
    ctx.ecosystem_discovery_status = "not_run"
    ctx.ecosystem_discovery_error = ""
    print("\n🧭 Stage 2.5: Ecosystem Discovery...")
    with StageTimer(ctx.perf_manager, "Stage 2.5: Ecosystem Discovery") as timer:
        try:
            from discovery_engine import discover_ecosystem_unknowns
            ctx.ecosystem_discovery = discover_ecosystem_unknowns(ctx.nodes)
            ctx.ecosystem_discovery_status = "ok"
            timer.set_output(unknowns=ctx.ecosystem_discovery.get('total_unknowns', 0))
            _log(f"   → {ctx.ecosystem_discovery.get('total_unknowns', 0)} unknown ecosystem patterns", ctx.quiet)
            ctx.data_ledger.publish("ecosystem", "Stage 2.5: Ecosystem Discovery",
                summary=f"{ctx.ecosystem_discovery.get('total_unknowns', 0)} unknowns")
        except Exception as e:
            ctx.ecosystem_discovery_status = "skipped"
            ctx.ecosystem_discovery_error = str(e)
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Ecosystem discovery skipped: {e}")
            ctx.data_ledger.publish("ecosystem", "Stage 2.5: Ecosystem Discovery", status="skipped", summary=str(e))

    # Stage 2.6: Holarchy Level Classification (L-3..L12)
    print("\n📊 Stage 2.6: Holarchy Level Classification...")
    with StageTimer(ctx.perf_manager, "Stage 2.6: Level Classification") as timer:
        try:
            from level_classifier import classify_level_batch, compute_level_statistics, infer_package_levels
            level_count = classify_level_batch(ctx.nodes)
            pkg_count = infer_package_levels(ctx.nodes)
            level_stats = compute_level_statistics(ctx.nodes)
            timer.set_output(nodes_classified=level_count, packages_detected=pkg_count, distribution=level_stats)
            # Show distribution summary
            dist_str = ", ".join(f"{k}:{v}" for k, v in level_stats.items() if v > 0)
            _log(f"   → {level_count} nodes assigned holarchy levels ({dist_str})", ctx.quiet)
            if pkg_count > 0:
                _log(f"   → {pkg_count} implicit L6 packages detected", ctx.quiet)
            ctx.data_ledger.publish("levels", "Stage 2.6: Level Classification",
                summary=f"{level_count} classified")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Level classification skipped: {e}")
            ctx.data_ledger.publish("levels", "Stage 2.6: Level Classification", status="skipped", summary=str(e))

    # Stage 2.7: Octahedral Dimension Classification (D4, D5, D7)
    print("\n📐 Stage 2.7: Octahedral Dimension Classification...")
    with StageTimer(ctx.perf_manager, "Stage 2.7: Dimension Classification") as timer:
        try:
            from dimension_classifier import classify_all_dimensions
            dim_count = classify_all_dimensions(ctx.nodes)
            timer.set_output(nodes_classified=dim_count)
            _log(f"   → {dim_count} nodes with full 8-dimension coordinates", ctx.quiet)
            ctx.data_ledger.publish("dimensions", "Stage 2.7: Dimension Classification",
                summary=f"{dim_count} classified")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Dimension classification skipped: {e}")
            ctx.data_ledger.publish("dimensions", "Stage 2.7: Dimension Classification", status="skipped", summary=str(e))
