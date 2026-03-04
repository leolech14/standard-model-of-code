"""Phase 1: Discovery — SmartIgnore, Survey, Contextome, Incremental Detection."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    if not quiet:
        print(msg)


def _run_smartignore(ctx: PipelineContext) -> None:
    """Stage -1: SmartIgnore directory exclusion."""
    ctx.smartignore_manifest = None
    smartignore_skip_paths = []

    run_smartignore = ctx.options.get("smart_ignore", True)
    if run_smartignore and not ctx.options.get("no_survey", False) and ctx.target.is_dir():
        print("\n🧭 Stage -1: SmartIgnore (Sequential Discovery)...")
        from src.core.observability import StageTimer

        with StageTimer(ctx.perf_manager, "Stage -1: SmartIgnore") as timer:
            try:
                from src.core.smart_ignore import SmartIgnore
                si = SmartIgnore(str(ctx.target))
                ctx.smartignore_manifest = si.discover()

                smartignore_skip_paths = list(ctx.smartignore_manifest.skip_paths)

                timer.set_output(
                    dirs_scanned=ctx.smartignore_manifest.total_dirs_scanned,
                    explore=len(ctx.smartignore_manifest.explore_paths),
                    skip=len(ctx.smartignore_manifest.skip_paths),
                    shallow=len(ctx.smartignore_manifest.shallow_paths),
                )

                _log(f"   → Scanned {ctx.smartignore_manifest.total_dirs_scanned} directories in {ctx.smartignore_manifest.discovery_time_ms:.0f}ms", ctx.quiet)
                _log(f"   → Phase 1 (name): {ctx.smartignore_manifest.phase1_dirs} classified", ctx.quiet)
                _log(f"   → Phase 2 (signal): {ctx.smartignore_manifest.phase2_dirs} explored", ctx.quiet)
                _log(f"   → Decision: EXPLORE {len(ctx.smartignore_manifest.explore_paths)}, "
                      f"SHALLOW {len(ctx.smartignore_manifest.shallow_paths)}, "
                      f"SKIP {len(ctx.smartignore_manifest.skip_paths)}", ctx.quiet)
                _log(f"   → Skip ratio: {ctx.smartignore_manifest.skip_ratio:.0%} "
                      f"(~{ctx.smartignore_manifest.estimated_files_skipped} files excluded)", ctx.quiet)

                # Write .smartignore file for caching/review
                si.write_smartignore(ctx.smartignore_manifest,
                                     str(ctx.output_dir / ".smartignore"))
                ctx.data_ledger.publish("smartignore", "Stage -1: SmartIgnore",
                    summary=f"skip={len(ctx.smartignore_manifest.skip_paths)}, ratio={ctx.smartignore_manifest.skip_ratio:.0%}")

            except ImportError as e:
                print(f"   ⚠️  SmartIgnore module not available: {e}")
                ctx.data_ledger.publish("smartignore", "Stage -1: SmartIgnore", status="failed", summary=str(e))
            except Exception as e:
                print(f"   ⚠️  SmartIgnore failed (continuing without): {e}")
                import traceback
                traceback.print_exc()
                ctx.data_ledger.publish("smartignore", "Stage -1: SmartIgnore", status="failed", summary=str(e))
    else:
        ctx.data_ledger.publish("smartignore", "Stage -1: SmartIgnore", status="skipped")

    # Seed exclude_paths with SmartIgnore decisions (Stage -1 → Stage 0 bridge)
    ctx.exclude_paths = list(smartignore_skip_paths)


def _run_survey(ctx: PipelineContext) -> None:
    """Stage 0: Pre-analysis survey."""
    ctx.survey_result = None

    # Check if survey is requested (default: enabled)
    run_survey_enabled = ctx.options.get("survey", True)
    skip_survey = ctx.options.get("no_survey", False)

    if run_survey_enabled and not skip_survey and ctx.target.is_dir():
        print("\n🔍 Stage 0: Survey (Pre-Analysis Intelligence)...")
        from src.core.observability import StageTimer

        with StageTimer(ctx.perf_manager, "Stage 0: Survey") as timer:
            try:
                from src.core.survey import run_survey, print_survey_report
                ctx.survey_result = run_survey(str(ctx.target))

                # Merge survey exclusions with SmartIgnore exclusions
                ctx.exclude_paths.extend(ctx.survey_result.recommended_excludes)

                timer.set_output(
                    total_files=ctx.survey_result.total_files,
                    exclusions=len(ctx.exclude_paths),
                    estimated_nodes=ctx.survey_result.estimated_nodes
                )

                _log(f"   → Scanned {ctx.survey_result.total_files:,} files in {ctx.survey_result.scan_time_ms:.0f}ms", ctx.quiet)
                _log(f"   → Found {len(ctx.survey_result.directory_exclusions)} vendor directories", ctx.quiet)
                _log(f"   → Found {len(ctx.survey_result.minified_files)} minified files", ctx.quiet)
                _log(f"   → Excluding {len(ctx.exclude_paths)} paths", ctx.quiet)
                _log(f"   → Estimated {ctx.survey_result.estimated_nodes:,} nodes after exclusions", ctx.quiet)

                # Print warnings
                for warning in ctx.survey_result.warnings:
                    print(f"   ⚠️  {warning}")
                ctx.data_ledger.publish("survey", "Stage 0: Survey",
                    summary=f"{ctx.survey_result.total_files} files, {len(ctx.exclude_paths)} exclusions")

            except ImportError as e:
                print(f"   ⚠️  Survey module not available: {e}")
                ctx.data_ledger.publish("survey", "Stage 0: Survey", status="failed", summary=str(e))
            except Exception as e:
                print(f"   ⚠️  Survey failed (continuing without exclusions): {e}")
                ctx.data_ledger.publish("survey", "Stage 0: Survey", status="failed", summary=str(e))
    else:
        ctx.data_ledger.publish("survey", "Stage 0: Survey", status="skipped")
        if skip_survey:
            print("\n🔍 Stage 0: Survey... SKIPPED (--no-survey)")
        elif not ctx.target.is_dir():
            print("\n🔍 Stage 0: Survey... SKIPPED (single file)")

    # Add any extra exclusions from --exclude flag
    extra_excludes = ctx.options.get("extra_excludes", [])
    if extra_excludes:
        ctx.exclude_paths.extend(extra_excludes)
        _log(f"   → Added {len(extra_excludes)} extra exclusions from --exclude flag", ctx.quiet)


def _run_contextome(ctx: PipelineContext) -> None:
    """Stage 0.8: Contextome Intelligence."""
    ctx.contextome_result = None

    if ctx.target.is_dir():
        print("\n📚 Stage 0.8: Contextome Intelligence...")
        from src.core.observability import StageTimer

        with StageTimer(ctx.perf_manager, "Stage 0.8: Contextome Intelligence") as timer:
            try:
                from src.core.contextome_intel import run_contextome_intelligence
                ctx.contextome_result = run_contextome_intelligence(
                    root_path=str(ctx.target),
                    exclude_paths=ctx.exclude_paths,
                )
                timer.set_output(
                    docs=ctx.contextome_result.doc_count,
                    deterministic_signals=ctx.contextome_result.deterministic_signals,
                    enriched_signals=ctx.contextome_result.enriched_signals,
                )
                _log(f"   → Discovered {ctx.contextome_result.doc_count} docs", ctx.quiet)
                _log(f"   → Extracted {ctx.contextome_result.deterministic_signals} deterministic signals", ctx.quiet)
                _log(f"   → Purpose coverage: {ctx.contextome_result.purpose_coverage:.0%}", ctx.quiet)
                _log(f"   → Symmetry seeds: {len(ctx.contextome_result.symmetry_seeds)}", ctx.quiet)
                if ctx.contextome_result.llm_used:
                    _log(f"   → LLM enrichment: +{ctx.contextome_result.enriched_signals} signals", ctx.quiet)
                ctx.data_ledger.publish("contextome", "Stage 0.8: Contextome Intelligence",
                    summary=f"{ctx.contextome_result.doc_count} docs")
            except Exception as e:
                print(f"   ⚠️  Contextome intelligence failed: {e}")
                import traceback
                traceback.print_exc()
                ctx.data_ledger.publish("contextome", "Stage 0.8: Contextome Intelligence", status="failed", summary=str(e))
    else:
        print("\n📚 Stage 0.8: Contextome Intelligence... SKIPPED (single file)")
        ctx.data_ledger.publish("contextome", "Stage 0.8: Contextome Intelligence", status="skipped")


def _run_incremental(ctx: PipelineContext) -> None:
    """Stage 0.5: Incremental Detection."""
    ctx.delta_result = None
    ctx.skip_files = set()

    if ctx.delta_tracker and ctx.target.is_dir():
        print("\n⚡ Stage 0.5: Incremental Detection...")
        from src.core.observability import StageTimer

        with StageTimer(ctx.perf_manager, "Stage 0.5: Incremental Detection") as timer:
            try:
                ctx.delta_result = ctx.delta_tracker.detect_changes(str(ctx.target), exclude=ctx.exclude_paths)
                ctx.skip_files = set(ctx.delta_result.unchanged_files)

                timer.set_output(
                    changed=len(ctx.delta_result.changed_files),
                    new=len(ctx.delta_result.new_files),
                    unchanged=len(ctx.delta_result.unchanged_files),
                    deleted=len(ctx.delta_result.deleted_files),
                )

                total = len(ctx.delta_result.changed_files) + len(ctx.delta_result.new_files) + len(ctx.delta_result.unchanged_files)
                skip_pct = (len(ctx.skip_files) / total * 100) if total > 0 else 0

                _log(f"   → Changed: {len(ctx.delta_result.changed_files)}, New: {len(ctx.delta_result.new_files)}", ctx.quiet)
                _log(f"   → Unchanged: {len(ctx.delta_result.unchanged_files)} ({skip_pct:.0f}% skipped)", ctx.quiet)
                if ctx.delta_result.deleted_files:
                    _log(f"   → Deleted: {len(ctx.delta_result.deleted_files)}", ctx.quiet)
                ctx.data_ledger.publish("incremental", "Stage 0.5: Incremental Detection",
                    summary=f"{len(ctx.delta_result.changed_files)} changed, {len(ctx.delta_result.new_files)} new")
            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Incremental detection failed: {e}")
                ctx.data_ledger.publish("incremental", "Stage 0.5: Incremental Detection", status="failed", summary=str(e))
    else:
        ctx.data_ledger.publish("incremental", "Stage 0.5: Incremental Detection", status="skipped")


def run_discovery(ctx: PipelineContext) -> None:
    """Execute all discovery sub-stages in order."""
    _run_smartignore(ctx)
    _run_survey(ctx)
    _run_contextome(ctx)
    _run_incremental(ctx)
