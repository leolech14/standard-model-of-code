#!/usr/bin/env python3
"""
Collider Full Analysis
Single command for complete deterministic analysis with all theoretical frameworks.

Usage:
    ./collider full <path> [--output <dir>]

Outputs:
    - output_llm-oriented_<project>_<timestamp>.json (LLM knowledge bundle)
    - output_human-readable_<project>_<timestamp>.html (human report + graph)
"""
import hashlib
import importlib.util
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional

from src.core.file_enricher import FileEnricher
from src.core.graph_framework import (
    build_nx_graph, find_entry_points, propagate_context, classify_node_role
)
from src.core.graph_metrics import compute_centrality_metrics, identify_critical_nodes
from src.core.intent_extractor import build_node_intent_profile
from src.core.igt_metrics import StabilityCalculator, OrphanClassifier

# Extracted modules (audit refactoring 2026-02-24)
from src.core.disconnection_classifier import classify_disconnection
from src.core.merkle_utils import calculate_merkle_root, generate_refinery_signature
from src.core.js_edge_detection import detect_js_imports, detect_class_instantiation
from src.core.codome_boundary import create_codome_boundaries, CODOME_BOUNDARIES
from src.core.file_index_builder import (
    build_file_index as _build_file_index,
    build_file_boundaries as _build_file_boundaries,
    calculate_theory_completeness as _calculate_theory_completeness,
)
from src.core.topology_analysis import compute_markov_matrix, detect_knots, compute_data_flow
from src.core.pipeline_snapshot import build_pipeline_snapshot


# Re-export extracted functions for backwards compatibility
# (other modules may import directly from full_analysis)
__all__ = [
    'classify_disconnection', 'calculate_merkle_root', 'generate_refinery_signature',
    'detect_js_imports', 'detect_class_instantiation', 'create_codome_boundaries',
    'build_file_index', 'build_file_boundaries', 'compute_markov_matrix',
    'detect_knots', 'compute_data_flow', 'build_pipeline_snapshot',
    'run_full_analysis', 'run_pipeline_analysis',
]


# =============================================================================
# LOGGING HELPERS
# =============================================================================

import contextlib

def _log(msg: str, quiet: bool = False):
    """Print progress message unless quiet mode is active."""
    if not quiet:
        print(msg)


def _write_pipeline_report(
    perf_manager, out_path, target, total_time, nodes, edges, pipeline_error=None
):
    """Write pipeline_report.json -- best-effort, returns path or None."""
    try:
        report_path = out_path / "pipeline_report.json"
        report = perf_manager.to_dict()
        report["meta"] = {
            "report_version": "1.0",
            "target": str(target),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "collider_version": "4.0.0",
            "total_time_s": round(total_time, 1),
            "node_count": len(nodes) if nodes else 0,
            "edge_count": len(edges) if edges else 0,
        }
        if pipeline_error:
            report["meta"]["pipeline_error"] = str(pipeline_error)
            report["meta"]["status"] = "FAILED"
        else:
            report["meta"]["status"] = "OK"
        report["output_files"] = {
            "unified_analysis": str(out_path / "unified_analysis.json"),
            "lod1": str(out_path / "ast_lod1_verbose.json"),
            "lod2": str(out_path / "ast_lod2_standard.json"),
            "lod3": str(out_path / "ast_lod3_compact.json"),
            "database": str(out_path / "collider.db"),
        }
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        return report_path
    except Exception:
        return None


class _PipelineCrashGuard:
    """Accumulates state during pipeline execution for crash-safe report writing."""

    def __init__(self):
        self.perf_manager = None
        self.out_path = None
        self.target = None
        self.start_time = None
        self.nodes = []
        self.edges = []

    def write_crash_report(self, exc):
        """Best-effort: write pipeline_report.json with error metadata."""
        if not (self.perf_manager and self.out_path and self.target and self.start_time):
            return
        elapsed = time.time() - self.start_time
        rp = _write_pipeline_report(
            self.perf_manager, self.out_path, self.target, elapsed,
            self.nodes, self.edges, pipeline_error=exc,
        )
        print(f"\n{'=' * 60}")
        print(f"COLLIDER PIPELINE FAILED: {exc}")
        if rp:
            print(f"   Partial report: {rp}")
        print(f"{'=' * 60}")


@contextlib.contextmanager
def suppress_fd_stderr():
    """Suppress C-library warnings written directly to fd 2 (e.g. tree-sitter)."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)


# =============================================================================
# FILE-CENTRIC VIEW: Thin wrappers for backwards compatibility
# =============================================================================

def _resolve_output_dir(target: Path, output_dir: Optional[str]) -> Path:
    """Resolve the canonical output directory."""
    if output_dir:
        return Path(output_dir)
    if target.is_dir():
        return target / ".collider"
    return target.parent / ".collider"


def _find_latest_html(output_dir: Path) -> Optional[Path]:
    """Return newest output_human-readable_*.html in output_dir, if any."""
    try:
        candidates = sorted(
            output_dir.glob("output_human-readable_*.html"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    except FileNotFoundError:
        return None
    return candidates[0] if candidates else None


def _open_file(path: Path) -> bool:
    """Open a file path with the OS default handler."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except Exception:  # noqa: utility function, caller doesn't need error detail
        return False
    return True


def _manual_open_command(path: Path) -> str:
    """Return a manual open command for the current OS."""
    if sys.platform == "darwin":
        return f'open "{path}"'
    if os.name == "nt":
        return f'start \"\" \"{path}\"'
    return f'xdg-open "{path}"'


# Backwards-compatible wrappers for extracted functions
build_file_index = _build_file_index
build_file_boundaries = _build_file_boundaries


def _generate_ai_insights(full_output: Dict, output_dir: Path, options: Dict) -> Optional[Dict]:
    """Generate AI insights using Vertex AI Gemini.

    This calls the wave analyze.py tool with --mode insights.
    Returns the parsed JSON insights or None on failure.
    """
    import subprocess
    import tempfile

    # Find the analyze.py script (relative to project structure)
    project_root = Path(__file__).parent.parent.parent.parent  # particle -> PROJECT_elements
    analyze_script = project_root / "wave" / "tools" / "ai" / "analyze.py"

    if not analyze_script.exists():
        print(f"   ⚠️ AI analyze script not found: {analyze_script}")
        return None

    # Write full_output to a temp file for the insights generator
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(full_output, f)
        temp_input = f.name

    try:
        model = options.get('ai_insights_model', 'gemini-2.0-flash-001')

        # Run the insights generator
        cmd = [
            sys.executable,
            str(analyze_script),
            "--mode", "insights",
            "--collider-json", temp_input,
            "--model", model,
            "--yes"  # Skip confirmation
        ]

        # Capture output to parse JSON result
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"   ⚠️ AI insights command failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            return None

        # The analyze.py script writes to ai_insights.json in the same dir as input
        insights_file = Path(temp_input).parent / "ai_insights.json"
        if not insights_file.exists():
            # Try the default output location
            insights_file = output_dir / "ai_insights.json"

        if insights_file.exists():
            with open(insights_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Try to parse from stdout if script printed JSON
        try:
            # Look for JSON in output (between first { and last })
            stdout = result.stdout
            json_start = stdout.find('{')
            json_end = stdout.rfind('}')
            if json_start >= 0 and json_end > json_start:
                return json.loads(stdout[json_start:json_end+1])
        except (json.JSONDecodeError, ValueError):
            pass

        return None

    except subprocess.TimeoutExpired:
        print("   ⚠️ AI insights generation timed out")
        return None
    except Exception as e:
        print(f"   ⚠️ AI insights generation error: {e}")
        return None
    finally:
        # Clean up temp file
        try:
            Path(temp_input).unlink()
        except Exception:  # noqa: best-effort cleanup
            pass


def run_pipeline_analysis(target_path: str, options: Dict[str, Any] = None) -> "CodebaseState":
    """
    Run analysis using the new Pipeline architecture.

    This is the refactored entry point that uses BaseStage classes
    and PipelineManager for orchestration.

    Args:
        target_path: Path to codebase to analyze
        options: Analysis options

    Returns:
        CodebaseState with all analysis results
    """
    from .pipeline import create_default_pipeline
    from .data_management import CodebaseState

    options = options or {}
    KNOWN_OPTIONS = {
        "roadmap", "open_latest", "ai_insights", "quiet", "output_dir",
        "output_format", "skip_ai", "max_files", "include_tests", "verbose",
        "db_backend", "db_path", "json_log", "dry_run", "no_color",
        "parallel", "cache", "skip_survey", "summary_format",
    }
    unknown = set(options.keys()) - KNOWN_OPTIONS
    if unknown:
        print(f"[WARN] Unknown options ignored: {unknown}")

    if options.get("dry_run"):
        stages = ["Discovery", "SmartIgnore", "Survey", "Analysis", "Data Chemistry", "AI Insights", "Report"]
        print("[DRY RUN] Pipeline stages that would execute:")
        for i, s in enumerate(stages, 1):
            print(f"  {i}. {s}")
        print(f"[DRY RUN] Target: {target_path}")
        return None

    print("\n" + "=" * 60)
    print("🚀 COLLIDER PIPELINE ANALYSIS")
    print("=" * 60)

    # Initialize state
    state = CodebaseState(target_path)

    # Create pipeline
    pipeline = create_default_pipeline(options)

    print(f"\n📋 Pipeline: {len(pipeline.stages)} stages")
    for i, stage in enumerate(pipeline.stages, 1):
        print(f"   {i}. {stage.name}")

    # Execute pipeline
    print("\n" + "-" * 40)
    state = pipeline.run(state)
    print("-" * 40)

    print(f"\n✅ Analysis complete: {len(state.nodes)} nodes, {len(state.edges)} edges")

    return state


def run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None) -> Dict:
    """Run complete analysis with all theoretical frameworks.

    Wraps _run_full_analysis to ensure pipeline_report.json is written
    even if an unhandled exception escapes the stage guards.
    """
    guard = _PipelineCrashGuard()
    try:
        return _run_full_analysis(target_path, output_dir, options, _guard=guard)
    except Exception as exc:
        guard.write_crash_report(exc)
        raise


def _run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None, *, _guard: _PipelineCrashGuard = None) -> Dict:
    """Internal implementation of run_full_analysis."""

    if options is None:
        options = {}
    open_latest = options.get("open_latest")
    if open_latest is None:
        open_latest = False
    if options.get("no_open", False):
        open_latest = False
    quiet = options.get("quiet", False)

    start_time = time.time()
    target = Path(target_path).resolve()
    resolved_output_dir = _resolve_output_dir(target, output_dir)

    # Import analysis functions (must come before observability import)
    sys.path.insert(0, str(Path(__file__).parent))

    # Initialize observability
    timing_enabled = options.get("timing", False)
    verbose_timing = options.get("verbose_timing", False)
    from observability import PerformanceManager, StageTimer
    perf_manager = PerformanceManager(verbose=verbose_timing, json_log=options.get("json_log", False))
    perf_manager.start_pipeline()
    _guard.perf_manager = perf_manager

    # Update crash guard with resolved state
    if _guard is None:
        _guard = _PipelineCrashGuard()
    _guard.start_time = start_time
    _guard.out_path = resolved_output_dir
    _guard.target = target

    # Working vars (overwritten by stages)
    nodes = []
    edges = []
    out_path = resolved_output_dir
    report_path = None

    _log("=" * 60, quiet)
    _log("COLLIDER FULL ANALYSIS", quiet)
    _log(f"Target: {target}", quiet)
    if timing_enabled or verbose_timing:
        _log("Performance Tracking: ENABLED", quiet)
    _log("=" * 60, quiet)

    # =========================================================================
    # DATABASE INITIALIZATION (Phase 30)
    # =========================================================================
    db_manager = None
    delta_tracker = None
    delta_result = None
    skip_files = set()

    if not options.get("no_db", False):
        try:
            from src.core.database import create_database_manager, DatabaseConfig
            from src.core.database.incremental import DeltaTracker

            db_config = DatabaseConfig.from_options(options, project_root=target)
            db_manager = create_database_manager(db_config, str(target))

            if db_manager:
                db_manager.connect()
                db_manager.initialize_schema()
                print(f"Database: {db_config.backend} @ {db_config.get_sqlite_path()}")

                # Initialize delta tracker for incremental analysis
                if db_config.incremental_enabled:
                    delta_tracker = DeltaTracker(db_manager)
        except ImportError as e:
            print(f"   Database module not available: {e}")
        except Exception as e:
            print(f"   Database initialization failed: {e}")

    # Initialize Logistics (Phase 28)
    batch_id = f"batch_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    refinery_signature = generate_refinery_signature()
    merkle_root = "UNSET" # Will be calculated after nodes are finalized

    # =========================================================================
    # STAGE -1: SMART IGNORE - Sequential Discovery Protocol (Phase 11)
    # =========================================================================
    smartignore_manifest = None
    smartignore_skip_paths = []

    run_smartignore = options.get("smart_ignore", True)
    if run_smartignore and not options.get("no_survey", False) and target.is_dir():
        print("\n🧭 Stage -1: SmartIgnore (Sequential Discovery)...")
        with StageTimer(perf_manager, "Stage -1: SmartIgnore") as timer:
            try:
                from src.core.smart_ignore import SmartIgnore
                si = SmartIgnore(str(target))
                smartignore_manifest = si.discover()

                smartignore_skip_paths = list(smartignore_manifest.skip_paths)

                timer.set_output(
                    dirs_scanned=smartignore_manifest.total_dirs_scanned,
                    explore=len(smartignore_manifest.explore_paths),
                    skip=len(smartignore_manifest.skip_paths),
                    shallow=len(smartignore_manifest.shallow_paths),
                )

                _log(f"   → Scanned {smartignore_manifest.total_dirs_scanned} directories in {smartignore_manifest.discovery_time_ms:.0f}ms", quiet)
                _log(f"   → Phase 1 (name): {smartignore_manifest.phase1_dirs} classified", quiet)
                _log(f"   → Phase 2 (signal): {smartignore_manifest.phase2_dirs} explored", quiet)
                _log(f"   → Decision: EXPLORE {len(smartignore_manifest.explore_paths)}, "
                      f"SHALLOW {len(smartignore_manifest.shallow_paths)}, "
                      f"SKIP {len(smartignore_manifest.skip_paths)}", quiet)
                _log(f"   → Skip ratio: {smartignore_manifest.skip_ratio:.0%} "
                      f"(~{smartignore_manifest.estimated_files_skipped} files excluded)", quiet)

                # Write .smartignore file for caching/review
                si.write_smartignore(smartignore_manifest,
                                     str(resolved_output_dir / ".smartignore"))

            except ImportError as e:
                print(f"   ⚠️  SmartIgnore module not available: {e}")
            except Exception as e:
                print(f"   ⚠️  SmartIgnore failed (continuing without): {e}")
                import traceback
                traceback.print_exc()

    # Seed exclude_paths with SmartIgnore decisions (Stage -1 → Stage 0 bridge)
    exclude_paths = list(smartignore_skip_paths)

    # =========================================================================
    # STAGE 0: SURVEY - Pre-Analysis Intelligence (Phase 10)
    # =========================================================================
    survey_result = None

    # Check if survey is requested (default: enabled)
    run_survey_enabled = options.get("survey", True)
    skip_survey = options.get("no_survey", False)

    if run_survey_enabled and not skip_survey and target.is_dir():
        print("\n🔍 Stage 0: Survey (Pre-Analysis Intelligence)...")
        with StageTimer(perf_manager, "Stage 0: Survey") as timer:
            try:
                from src.core.survey import run_survey, print_survey_report
                survey_result = run_survey(str(target))

                # Merge survey exclusions with SmartIgnore exclusions
                exclude_paths.extend(survey_result.recommended_excludes)

                timer.set_output(
                    total_files=survey_result.total_files,
                    exclusions=len(exclude_paths),
                    estimated_nodes=survey_result.estimated_nodes
                )

                _log(f"   → Scanned {survey_result.total_files:,} files in {survey_result.scan_time_ms:.0f}ms", quiet)
                _log(f"   → Found {len(survey_result.directory_exclusions)} vendor directories", quiet)
                _log(f"   → Found {len(survey_result.minified_files)} minified files", quiet)
                _log(f"   → Excluding {len(exclude_paths)} paths", quiet)
                _log(f"   → Estimated {survey_result.estimated_nodes:,} nodes after exclusions", quiet)

                # Print warnings
                for warning in survey_result.warnings:
                    print(f"   ⚠️  {warning}")

            except ImportError as e:
                print(f"   ⚠️  Survey module not available: {e}")
            except Exception as e:
                print(f"   ⚠️  Survey failed (continuing without exclusions): {e}")
    else:
        if skip_survey:
            print("\n🔍 Stage 0: Survey... SKIPPED (--no-survey)")
        elif not target.is_dir():
            print("\n🔍 Stage 0: Survey... SKIPPED (single file)")

    # Add any extra exclusions from --exclude flag
    extra_excludes = options.get("extra_excludes", [])
    if extra_excludes:
        exclude_paths.extend(extra_excludes)
        _log(f"   → Added {len(extra_excludes)} extra exclusions from --exclude flag", quiet)

    # =========================================================================
    # STAGE 0.8: CONTEXTOME INTELLIGENCE (Phase 10)
    # =========================================================================
    contextome_result = None

    if target.is_dir():
        print("\n📚 Stage 0.8: Contextome Intelligence...")
        with StageTimer(perf_manager, "Stage 0.8: Contextome Intelligence") as timer:
            try:
                from src.core.contextome_intel import run_contextome_intelligence
                contextome_result = run_contextome_intelligence(
                    root_path=str(target),
                    exclude_paths=exclude_paths,
                )
                timer.set_output(
                    docs=contextome_result.doc_count,
                    deterministic_signals=contextome_result.deterministic_signals,
                    enriched_signals=contextome_result.enriched_signals,
                )
                _log(f"   → Discovered {contextome_result.doc_count} docs", quiet)
                _log(f"   → Extracted {contextome_result.deterministic_signals} deterministic signals", quiet)
                _log(f"   → Purpose coverage: {contextome_result.purpose_coverage:.0%}", quiet)
                _log(f"   → Symmetry seeds: {len(contextome_result.symmetry_seeds)}", quiet)
                if contextome_result.llm_used:
                    _log(f"   → LLM enrichment: +{contextome_result.enriched_signals} signals", quiet)
            except Exception as e:
                print(f"   ⚠️  Contextome intelligence failed: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("\n📚 Stage 0.8: Contextome Intelligence... SKIPPED (single file)")

    # =========================================================================
    # STAGE 0.5: INCREMENTAL DETECTION (Phase 30)
    # =========================================================================
    if delta_tracker and target.is_dir():
        print("\n⚡ Stage 0.5: Incremental Detection...")
        with StageTimer(perf_manager, "Stage 0.5: Incremental Detection") as timer:
            try:
                delta_result = delta_tracker.detect_changes(str(target), exclude=exclude_paths)
                skip_files = set(delta_result.unchanged_files)

                timer.set_output(
                    changed=len(delta_result.changed_files),
                    new=len(delta_result.new_files),
                    unchanged=len(delta_result.unchanged_files),
                    deleted=len(delta_result.deleted_files),
                )

                total = len(delta_result.changed_files) + len(delta_result.new_files) + len(delta_result.unchanged_files)
                skip_pct = (len(skip_files) / total * 100) if total > 0 else 0

                _log(f"   → Changed: {len(delta_result.changed_files)}, New: {len(delta_result.new_files)}", quiet)
                _log(f"   → Unchanged: {len(delta_result.unchanged_files)} ({skip_pct:.0f}% skipped)", quiet)
                if delta_result.deleted_files:
                    _log(f"   → Deleted: {len(delta_result.deleted_files)}", quiet)
            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Incremental detection failed: {e}")

    from src.core.unified_analysis import analyze
    from src.core.standard_model_enricher import enrich_with_standard_model
    from src.core.purpose_field import detect_purpose_field
    from src.core.purpose_emergence import compute_pi2, compute_pi3, compute_pi4
    from src.core.execution_flow import detect_execution_flow

    from src.core.performance_predictor import predict_performance
    from src.core.roadmap_evaluator import RoadmapEvaluator
    from src.core.topology_reasoning import TopologyClassifier
    from src.core.semantic_cortex import ConceptExtractor
    # NOTE: standard_output_generator removed - consolidated into unified outputs

    # Stage 1: Base analysis
    print("\n🔬 Stage 1: Base Analysis...")
    with StageTimer(perf_manager, "Stage 1: Base Analysis") as timer:
        analysis_options = dict(options)
        analysis_options.pop("roadmap", None)
        # Pass survey exclusions to unified analysis (Phase 10 integration)
        if exclude_paths:
            analysis_options['exclude_paths'] = exclude_paths
        result = analyze(str(target), output_dir=str(resolved_output_dir), write_output=False, **analysis_options)
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])
        unified_stats = getattr(result, 'stats', {}) if hasattr(result, 'stats') else result.get('stats', {})
        unified_classification = getattr(result, 'classification', {}) if hasattr(result, 'classification') else result.get('classification', {})
        unified_auto_discovery = getattr(result, 'auto_discovery', {}) if hasattr(result, 'auto_discovery') else result.get('auto_discovery', {})
        unified_dependencies = getattr(result, 'dependencies', {}) if hasattr(result, 'dependencies') else result.get('dependencies', {})
        unified_architecture = getattr(result, 'architecture', {}) if hasattr(result, 'architecture') else result.get('architecture', {})
        unified_llm_enrichment = getattr(result, 'llm_enrichment', {}) if hasattr(result, 'llm_enrichment') else result.get('llm_enrichment', {})
        unified_warnings = getattr(result, 'warnings', []) if hasattr(result, 'warnings') else result.get('warnings', [])
        unified_recommendations = getattr(result, 'recommendations', []) if hasattr(result, 'recommendations') else result.get('recommendations', [])
        timer.set_output(nodes=len(nodes), edges=len(edges))
    _guard.nodes = nodes
    _guard.edges = edges
    _log(f"   → {len(nodes)} nodes, {len(edges)} edges", quiet)

    # Stage 2: Standard Model enrichment
    print("\n🧬 Stage 2: Standard Model Enrichment...")
    with StageTimer(perf_manager, "Stage 2: Standard Model Enrichment") as timer:
        nodes = enrich_with_standard_model(nodes)
        rpbl_count = sum(1 for n in nodes if n.get('rpbl'))

        # Flatten RPBL scores for UPB binding (P4-05/07/08)
        for node in nodes:
            rpbl = node.get('rpbl', {})
            node['rpbl_responsibility'] = rpbl.get('responsibility', 0)
            node['rpbl_purity'] = rpbl.get('purity', 0)
            node['rpbl_boundary'] = rpbl.get('boundary', 0)
            node['rpbl_lifecycle'] = rpbl.get('lifecycle', 0)

        timer.set_output(nodes=len(nodes), rpbl_enriched=rpbl_count)
    _log(f"   → {rpbl_count} nodes with RPBL scores", quiet)

    # Pipeline Assertion: Validate canonical roles
    try:
        from registry.role_registry import get_role_registry
        _registry = get_role_registry()
        _invalid = {n.get('role') for n in nodes if n.get('role') and not _registry.validate(n['role'])}
        if _invalid:
            import os
            if os.environ.get('COLLIDER_STRICT_ROLES', '').lower() == 'true':
                raise ValueError(f"Non-canonical roles detected: {_invalid}")
            else:
                print(f"   ⚠️ WARNING: Non-canonical roles: {_invalid}")
    except ImportError:
        pass  # Registry not available, skip validation

    # Stage 2.5: Ecosystem discovery (hybrid T2 approach)
    ecosystem_discovery = {}
    ecosystem_discovery_status = "not_run"
    ecosystem_discovery_error = ""
    print("\n🧭 Stage 2.5: Ecosystem Discovery...")
    with StageTimer(perf_manager, "Stage 2.5: Ecosystem Discovery") as timer:
        try:
            from discovery_engine import discover_ecosystem_unknowns
            ecosystem_discovery = discover_ecosystem_unknowns(nodes)
            ecosystem_discovery_status = "ok"
            timer.set_output(unknowns=ecosystem_discovery.get('total_unknowns', 0))
            _log(f"   → {ecosystem_discovery.get('total_unknowns', 0)} unknown ecosystem patterns", quiet)
        except Exception as e:
            ecosystem_discovery_status = "skipped"
            ecosystem_discovery_error = str(e)
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Ecosystem discovery skipped: {e}")

    # Stage 2.6: Holarchy Level Classification (L-3..L12)
    print("\n📊 Stage 2.6: Holarchy Level Classification...")
    with StageTimer(perf_manager, "Stage 2.6: Level Classification") as timer:
        try:
            from level_classifier import classify_level_batch, compute_level_statistics, infer_package_levels
            level_count = classify_level_batch(nodes)
            pkg_count = infer_package_levels(nodes)
            level_stats = compute_level_statistics(nodes)
            timer.set_output(nodes_classified=level_count, packages_detected=pkg_count, distribution=level_stats)
            # Show distribution summary
            dist_str = ", ".join(f"{k}:{v}" for k, v in level_stats.items() if v > 0)
            _log(f"   → {level_count} nodes assigned holarchy levels ({dist_str})", quiet)
            if pkg_count > 0:
                _log(f"   → {pkg_count} implicit L6 packages detected", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Level classification skipped: {e}")

    # Stage 2.7: Octahedral Dimension Classification (D4, D5, D7)
    print("\n📐 Stage 2.7: Octahedral Dimension Classification...")
    with StageTimer(perf_manager, "Stage 2.7: Dimension Classification") as timer:
        try:
            from dimension_classifier import classify_all_dimensions
            dim_count = classify_all_dimensions(nodes)
            timer.set_output(nodes_classified=dim_count)
            _log(f"   → {dim_count} nodes with full 8-dimension coordinates", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Dimension classification skipped: {e}")

    # Shared tree-sitter cache for Stages 2.8 – 2.11 (avoids 4x re-parsing the same source)
    from src.core.tree_sitter_cache import TreeSitterCache as _TreeSitterCache
    _ts_cache = _TreeSitterCache(max_size=500)

    # Stage 2.8: Scope Analysis (definitions, references, unused, shadowing)
    print("\n🔬 Stage 2.8: Scope Analysis...")
    with StageTimer(perf_manager, "Stage 2.8: Scope Analysis") as timer:
        try:
            from scope_analyzer import analyze_scopes, find_unused_definitions, find_shadowed_definitions

            # Parsers obtained from shared cache (lazy-initialised once on first use)
            py_parser = _ts_cache.get_parser("python")
            js_parser = _ts_cache.get_parser("javascript")

            scope_stats = {'files_analyzed': 0, 'unused': 0, 'shadowed': 0}

            # Analyze scope per file
            _stage_warns = 0
            files_analyzed = set()
            for node in nodes:
                file_path = node.get('file_path', '')
                if file_path in files_analyzed:
                    continue
                files_analyzed.add(file_path)

                # Determine language
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                try:
                    with suppress_fd_stderr():
                        tree = _ts_cache.parse(body, lang)
                        graph = analyze_scopes(tree, bytes(body, 'utf8'), lang, file_path)
                    unused = find_unused_definitions(graph)
                    shadowed = find_shadowed_definitions(graph)

                    scope_stats['files_analyzed'] += 1
                    scope_stats['unused'] += len(unused)
                    scope_stats['shadowed'] += len(shadowed)

                    # Store in node metadata
                    node['scope_analysis'] = {
                        'definitions': len(graph.definitions),
                        'references': len(graph.references),
                        'unused_count': len(unused),
                        'shadowed_count': len(shadowed)
                    }
                except Exception:
                    _stage_warns += 1

            if _stage_warns:
                print(f"   ⚠️  {_stage_warns} items skipped due to parse errors")
            timer.set_output(**scope_stats)
            _log(f"   → {scope_stats['files_analyzed']} files analyzed", quiet)
            _log(f"   → {scope_stats['unused']} unused definitions detected", quiet)
            _log(f"   → {scope_stats['shadowed']} shadowing pairs found", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Scope analysis skipped: {e}")

    # Stage 2.9: Control Flow Metrics (cyclomatic complexity, nesting depth)
    print("\n📈 Stage 2.9: Control Flow Metrics...")
    with StageTimer(perf_manager, "Stage 2.9: Control Flow Metrics") as timer:
        try:
            from control_flow_analyzer import analyze_control_flow, get_complexity_rating, get_nesting_rating

            # Parsers from shared cache (already initialised by Stage 2.8 if it ran)
            py_parser = _ts_cache.get_parser("python")
            js_parser = _ts_cache.get_parser("javascript")

            cf_stats = {'nodes_analyzed': 0, 'avg_cc': 0, 'max_cc': 0, 'avg_depth': 0, 'max_depth': 0}
            cc_sum, depth_sum = 0, 0

            _stage_warns = 0
            for node in nodes:
                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                file_path = node.get('file_path', '')
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                try:
                    tree = _ts_cache.parse(body, lang)
                    metrics = analyze_control_flow(tree, bytes(body, 'utf8'), lang)

                    cc = metrics['cyclomatic_complexity']
                    depth = metrics['max_nesting_depth']

                    # Store in node (nested for full detail)
                    node['control_flow'] = {
                        'cyclomatic_complexity': cc,
                        'complexity_rating': get_complexity_rating(cc),
                        'max_nesting_depth': depth,
                        'nesting_rating': get_nesting_rating(depth),
                        'decision_points': metrics['decision_points'],
                        'branches': metrics['branches'],
                        'loops': metrics['loops'],
                        'early_returns': metrics['early_returns']
                    }

                    # P3-09: Flatten key metrics for UPB binding
                    node['cyclomatic_complexity'] = cc
                    node['complexity_rating'] = get_complexity_rating(cc)
                    node['max_nesting_depth'] = depth
                    node['nesting_rating'] = get_nesting_rating(depth)

                    cf_stats['nodes_analyzed'] += 1
                    cc_sum += cc
                    depth_sum += depth
                    cf_stats['max_cc'] = max(cf_stats['max_cc'], cc)
                    cf_stats['max_depth'] = max(cf_stats['max_depth'], depth)
                except Exception:
                    _stage_warns += 1

            if _stage_warns:
                print(f"   ⚠️  {_stage_warns} items skipped due to parse errors")
            if cf_stats['nodes_analyzed'] > 0:
                cf_stats['avg_cc'] = round(cc_sum / cf_stats['nodes_analyzed'], 2)
                cf_stats['avg_depth'] = round(depth_sum / cf_stats['nodes_analyzed'], 2)

            timer.set_output(**cf_stats)
            _log(f"   → {cf_stats['nodes_analyzed']} nodes analyzed", quiet)
            _log(f"   → Avg CC: {cf_stats['avg_cc']}, Max CC: {cf_stats['max_cc']}", quiet)
            _log(f"   → Avg Depth: {cf_stats['avg_depth']}, Max Depth: {cf_stats['max_depth']}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Control flow analysis skipped: {e}")

    # Stage 2.10: Pattern-Based Atom Detection
    print("\n🧬 Stage 2.10: Pattern-Based Atom Detection...")
    with StageTimer(perf_manager, "Stage 2.10: Pattern Detection") as timer:
        try:
            from pattern_matcher import PatternMatcher

            # Initialize pattern matcher
            pattern_matcher = PatternMatcher()

            # Parsers from shared cache
            py_parser = _ts_cache.get_parser("python")
            js_parser = _ts_cache.get_parser("javascript")

            pattern_stats = {'nodes_enriched': 0, 'atoms_detected': 0, 'by_type': {}}

            _stage_warns = 0
            for node in nodes:
                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                file_path = node.get('file_path', '')
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                try:
                    tree = _ts_cache.parse(body, lang)
                    atoms = pattern_matcher.detect_atoms(tree, bytes(body, 'utf8'), lang)

                    if atoms:
                        # Store detected atoms in node
                        node['detected_atoms'] = [
                            {
                                'type': a.type,
                                'name': a.name,
                                'confidence': a.confidence,
                                'evidence': a.evidence
                            }
                            for a in atoms
                        ]

                        # Update node's atom type if high confidence detection
                        best_atom = max(atoms, key=lambda a: a.confidence)
                        if best_atom.confidence >= 0.85:
                            node['atom_type'] = best_atom.type
                            node['atom_confidence'] = best_atom.confidence

                        pattern_stats['nodes_enriched'] += 1
                        pattern_stats['atoms_detected'] += len(atoms)

                        for a in atoms:
                            pattern_stats['by_type'][a.type] = pattern_stats['by_type'].get(a.type, 0) + 1
                except Exception:
                    _stage_warns += 1

            if _stage_warns:
                print(f"   ⚠️  {_stage_warns} items skipped due to parse errors")
            timer.set_output(**{k: v for k, v in pattern_stats.items() if k != 'by_type'})
            _log(f"   → {pattern_stats['nodes_enriched']} nodes enriched with atom patterns", quiet)
            _log(f"   → {pattern_stats['atoms_detected']} total atoms detected", quiet)
            if pattern_stats['by_type']:
                top_types = sorted(pattern_stats['by_type'].items(), key=lambda x: -x[1])[:5]
                _log(f"   → Top types: {', '.join(f'{t}:{c}' for t, c in top_types)}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Pattern detection skipped: {e}")

    # Stage 2.11: Data Flow Analysis (D6:EFFECT - Purity)
    print("\n🌊 Stage 2.11: Data Flow Analysis (D6:EFFECT)...")
    with StageTimer(perf_manager, "Stage 2.11: Data Flow Analysis") as timer:
        try:
            from data_flow_analyzer import analyze_data_flow, get_data_flow_summary

            # Parsers from shared cache
            py_parser = _ts_cache.get_parser("python")
            js_parser = _ts_cache.get_parser("javascript")

            flow_stats = {
                'nodes_analyzed': 0,
                'total_assignments': 0,
                'total_mutations': 0,
                'total_side_effects': 0,
                'purity_distribution': {'pure': 0, 'mostly_pure': 0, 'mixed': 0, 'mostly_impure': 0, 'impure': 0}
            }

            _stage_warns = 0
            for node in nodes:
                body = node.get('body_source', '')
                if not body or len(body) < 10:
                    continue

                file_path = node.get('file_path', '')
                if file_path.endswith('.py'):
                    lang, parser = 'python', py_parser
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    lang, parser = 'javascript', js_parser
                else:
                    continue

                try:
                    tree = _ts_cache.parse(body, lang)
                    flow_graph = analyze_data_flow(tree, bytes(body, 'utf8'), lang, file_path)
                    summary = get_data_flow_summary(flow_graph)

                    # Store data flow metrics in node
                    node['data_flow'] = {
                        'assignments': summary['total_assignments'],
                        'mutations': summary['mutations'],
                        'side_effects': summary['side_effects'],
                        'pure_score': summary['pure_score'],
                        'purity_rating': summary['purity_rating'],
                    }

                    # D6:EFFECT dimension
                    node['D6_EFFECT'] = summary['purity_rating']
                    node['D6_pure_score'] = summary['pure_score']

                    # Update stats
                    flow_stats['nodes_analyzed'] += 1
                    flow_stats['total_assignments'] += summary['total_assignments']
                    flow_stats['total_mutations'] += summary['mutations']
                    flow_stats['total_side_effects'] += summary['side_effects']
                    flow_stats['purity_distribution'][summary['purity_rating']] += 1
                except Exception:
                    _stage_warns += 1

            if _stage_warns:
                print(f"   ⚠️  {_stage_warns} items skipped due to parse errors")
            timer.set_output(
                nodes_analyzed=flow_stats['nodes_analyzed'],
                mutations=flow_stats['total_mutations'],
                side_effects=flow_stats['total_side_effects']
            )
            _log(f"   → {flow_stats['nodes_analyzed']} nodes analyzed for purity", quiet)
            _log(f"   → {flow_stats['total_mutations']} mutations, {flow_stats['total_side_effects']} side effects", quiet)
            purity_dist = flow_stats['purity_distribution']
            _log(f"   → Purity: pure={purity_dist['pure']}, mostly_pure={purity_dist['mostly_pure']}, mixed={purity_dist['mixed']}, impure={purity_dist['impure']}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Data flow analysis skipped: {e}")

    # Stage 3: Purpose Field
    print("\n🎯 Stage 3: Purpose Field...")
    with StageTimer(perf_manager, "Stage 3: Purpose Field") as timer:
        purpose_field = detect_purpose_field(nodes, edges)
        timer.set_output(nodes=len(purpose_field.nodes), violations=len(purpose_field.violations))
    _log(f"   → {len(purpose_field.nodes)} purpose nodes", quiet)
    _log(f"   → {len(purpose_field.violations)} violations", quiet)

    # Stage 3.5: π₃ (Organelle Purpose) for containers
    print("\n🧬 Stage 3.5: Organelle Purpose (π₃)...")
    pi3_count = 0
    # Build parent-child index from names (Class.method pattern)
    children_by_parent = {}
    node_by_name = {n.get('name', ''): n for n in nodes}
    for node in nodes:
        name = node.get('name', '')
        if '.' in name:
            parent_name = name.rsplit('.', 1)[0]
            if parent_name not in children_by_parent:
                children_by_parent[parent_name] = []
            children_by_parent[parent_name].append(node)

    # Compute π₃ for containers
    for node in nodes:
        name = node.get('name', '')
        if name in children_by_parent and len(children_by_parent[name]) > 0:
            children = children_by_parent[name]
            pi3 = compute_pi3(node, children)
            node['pi3_purpose'] = pi3.purpose
            node['pi3_confidence'] = round(pi3.confidence, 2)
            node['pi3_child_count'] = len(children)
            pi3_count += 1
    _log(f"   → {pi3_count} containers with π₃ purpose", quiet)

    # Stage 3.6: π₄ (System Purpose) for files
    print("\n📦 Stage 3.6: System Purpose (π₄)...")
    # Group nodes by file
    nodes_by_file = {}
    for node in nodes:
        fpath = node.get('file_path', 'unknown')
        if fpath not in nodes_by_file:
            nodes_by_file[fpath] = []
        nodes_by_file[fpath].append(node)

    # Compute π₄ for each file
    file_purposes = {}
    for fpath, file_nodes in nodes_by_file.items():
        pi4 = compute_pi4(fpath, file_nodes)
        file_purposes[fpath] = {
            'purpose': pi4.purpose,
            'confidence': round(pi4.confidence, 2),
            'node_count': len(file_nodes),
            'signals': pi4.signals
        }
        # Also tag each node with its file's π₄
        for node in file_nodes:
            node['pi4_purpose'] = pi4.purpose
            node['pi4_confidence'] = round(pi4.confidence, 2)

    _log(f"   → {len(file_purposes)} files with π₄ purpose", quiet)

    # Stage 3.7: Purpose Coherence (from PurposeField)
    print("\n🎯 Stage 3.7: Purpose Coherence Metrics...")
    coherence_enriched = 0
    # Build lookup from purpose_field.nodes by node name
    pf_by_name = {pn.name: pn for pn in purpose_field.nodes.values()}
    for node in nodes:
        name = node.get('name', '')
        if name in pf_by_name:
            pf_node = pf_by_name[name]
            # Transfer coherence metrics
            node['purpose_coherence'] = {
                'coherence_score': pf_node.coherence_score,
                'purpose_entropy': pf_node.purpose_entropy,
                'is_god_class': pf_node.is_god_class,
                'unique_child_purposes': pf_node.unique_purposes,
                'composite_purpose': pf_node.composite_purpose,
                'atomic_purpose': pf_node.atomic_purpose,
                'atomic_confidence': pf_node.atomic_confidence,
                'layer': pf_node.layer.value,
            }
            # Also add flat fields for easier access
            node['coherence_score'] = pf_node.coherence_score
            node['purpose_entropy'] = pf_node.purpose_entropy
            if pf_node.is_god_class:
                node['is_god_class'] = True
            coherence_enriched += 1
    _log(f"   → {coherence_enriched} nodes enriched with coherence metrics", quiet)
    # Count god classes
    god_class_count = sum(1 for n in nodes if n.get('is_god_class', False))
    if god_class_count > 0:
        print(f"   ⚠️  {god_class_count} god classes detected")

    # Stage 4: Execution Flow
    print("\n⚡ Stage 4: Execution Flow...")
    with StageTimer(perf_manager, "Stage 4: Execution Flow") as timer:
        exec_flow = detect_execution_flow(nodes, edges, purpose_field)
        timer.set_output(entry_points=len(exec_flow.entry_points), orphans=len(exec_flow.orphans))
    _log(f"   → {len(exec_flow.entry_points)} entry points", quiet)
    _log(f"   → {len(exec_flow.orphans)} orphans ({exec_flow.dead_code_percent}% dead code)", quiet)

    # Stage 4.5: Orphan Integration Analysis (REMOVED - Module Deleted)
    # orphan_integration was removed in remediation pass.
    orphan_analysis = []

    # Stage 5: Markov Matrix
    print("\n📊 Stage 5: Markov Transition Matrix...")
    with StageTimer(perf_manager, "Stage 5: Markov Transition Matrix") as timer:
        markov = compute_markov_matrix(nodes, edges)
        timer.set_output(transitions=markov['total_transitions'], edges_weighted=markov['edges_with_weight'])
    _log(f"   → {markov['total_transitions']} nodes with transitions", quiet)
    _log(f"   → {markov['edges_with_weight']} edges with markov_weight", quiet)
    _log(f"   → {markov['avg_fanout']:.1f} avg fanout", quiet)

    # Stage 6: Knot Detection
    print("\n🔗 Stage 6: Knot/Cycle Detection...")
    with StageTimer(perf_manager, "Stage 6: Knot/Cycle Detection") as timer:
        knots = detect_knots(nodes, edges)
        timer.set_output(cycles=knots['cycles_detected'], bidirectional=knots['bidirectional_edges'])
    _log(f"   → {knots['cycles_detected']} cycles detected", quiet)
    _log(f"   → {knots['bidirectional_edges']} bidirectional edges", quiet)
    _log(f"   → Knot score: {knots['knot_score']}/10", quiet)

    # Stage 6.5: Graph Analytics (Nerd Layer)
    # _G_full carries ALL edge types for Stage 6.7 (entry points, context propagation,
    # closeness centrality).  Building it here avoids a second build_nx_graph() call.
    _G_full = None  # Will be set inside try block; used by Stage 6.7
    print("\n🧮 Stage 6.5: Graph Analytics...")
    with StageTimer(perf_manager, "Stage 6.5: Graph Analytics") as timer:
        # Degree computation (always runs - needed for Control Bar mappings)
        try:
            import networkx as nx
            G = nx.DiGraph()
            for node in nodes:
                G.add_node(node.get('id', ''), **{k: v for k, v in node.items() if k != 'body_source'})
            # Only count behavioral edges (calls, invokes) for topology classification
            # Structural edges (contains, inherits) would give false in_degree to all nested nodes
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src and tgt:
                        G.add_edge(src, tgt)

            # Also build full graph (all edge types) for Stage 6.7 re-use.
            # This is built once here so Stage 6.7 does not have to rebuild it.
            _G_full = build_nx_graph(nodes, edges)

            # Compute in_degree and out_degree for each node
            in_degree_map = dict(G.in_degree())
            out_degree_map = dict(G.out_degree())
            degree_enriched = 0

            # Compute centrality metrics on behavioral graph (research-backed: Zimmermann/Nagappan)
            betweenness = nx.betweenness_centrality(G) if len(G) > 0 else {}
            pagerank = nx.pagerank(G) if len(G) > 0 and G.is_directed() else {}

            # Compute closeness centrality on the full graph (all edges) – same graph
            # that Stage 6.7 uses for entry-point propagation and semantic analysis.
            # Doing this here eliminates the duplicate compute_centrality_metrics(G)
            # call that Stage 6.7 previously made on a freshly-built full graph.
            _closeness = nx.closeness_centrality(_G_full) if len(_G_full) > 0 else {}

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_degree_map.get(n.get('id', ''), 0) + out_degree_map.get(n.get('id', ''), 0) for n in nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            for node in nodes:
                node_id = node.get('id', '')
                in_deg = in_degree_map.get(node_id, 0)
                out_deg = out_degree_map.get(node_id, 0)
                node['in_degree'] = in_deg
                node['out_degree'] = out_deg

                # Add centrality metrics (betweenness/pagerank on behavioral graph,
                # closeness on full graph to match Stage 6.7 semantics)
                node['betweenness_centrality'] = round(betweenness.get(node_id, 0), 6)
                node['pagerank'] = round(pagerank.get(node_id, 0), 6)
                node['closeness_centrality'] = round(_closeness.get(node_id, 0.0), 6)

                # Compute topology_role (relational property)
                if in_deg == 0 and out_deg == 0:
                    node['topology_role'] = 'orphan'
                elif in_deg == 0 and out_deg > 0:
                    node['topology_role'] = 'root'
                elif out_deg == 0 and in_deg > 0:
                    node['topology_role'] = 'leaf'
                elif (in_deg + out_deg) >= hub_threshold:
                    node['topology_role'] = 'hub'
                else:
                    node['topology_role'] = 'internal'

                # Compute π₂ (Molecular Purpose) - emergent from composition
                pi2 = compute_pi2(node)
                node['pi2_purpose'] = pi2.purpose
                node['pi2_confidence'] = round(pi2.confidence, 2)

                # Add disconnection taxonomy for nodes missing incoming edges
                # This includes orphans (no edges) AND roots (no incoming but have outgoing)
                # Roots are often: entry points, HTML event handlers, exported APIs
                if in_deg == 0:
                    disconnection = classify_disconnection(node, in_deg, out_deg)
                    if disconnection:
                        node['disconnection'] = disconnection

                if in_deg > 0 or out_deg > 0:
                    degree_enriched += 1

            # Count topology roles and disconnection sources for summary
            role_counts = {}
            disconnection_counts = {}
            for node in nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            _log(f"   → {degree_enriched} nodes enriched with degree metrics", quiet)
            _log(f"   → Topology roles: {role_counts}", quiet)
            if disconnection_counts:
                _log(f"   → Disconnection taxonomy: {disconnection_counts}", quiet)
            # Report top centrality nodes
            if betweenness:
                top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_betweenness:
                    _log(f"   → Top betweenness: {[(n.split('::')[-1], round(v, 4)) for n, v in top_betweenness]}", quiet)
            if pagerank:
                top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_pagerank:
                    _log(f"   → Top PageRank: {[(n.split('::')[-1], round(v, 4)) for n, v in top_pagerank]}", quiet)
        except Exception as e:
            # Fallback: compute degrees without networkx
            print(f"   ⚠️ Graph analytics fallback: {type(e).__name__}: {e}")
            in_counts = defaultdict(int)
            out_counts = defaultdict(int)
            # Only count behavioral edges (calls, invokes) for topology classification
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src:
                        out_counts[src] += 1
                    if tgt:
                        in_counts[tgt] += 1

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_counts.get(n.get('id', ''), 0) + out_counts.get(n.get('id', ''), 0) for n in nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            degree_enriched = 0
            for node in nodes:
                node_id = node.get('id', '')
                in_deg = in_counts.get(node_id, 0)
                out_deg = out_counts.get(node_id, 0)
                node['in_degree'] = in_deg
                node['out_degree'] = out_deg

                # Compute topology_role (relational property)
                if in_deg == 0 and out_deg == 0:
                    node['topology_role'] = 'orphan'
                elif in_deg == 0 and out_deg > 0:
                    node['topology_role'] = 'root'
                elif out_deg == 0 and in_deg > 0:
                    node['topology_role'] = 'leaf'
                elif (in_deg + out_deg) >= hub_threshold:
                    node['topology_role'] = 'hub'
                else:
                    node['topology_role'] = 'internal'

                # BUG FIX: Separate call degree from total degree for metrics
                # This ensures we report "behavioral" stats correctly in APIs
                node['call_in_degree'] = in_deg
                node['call_out_degree'] = out_deg

                # Add disconnection taxonomy for nodes missing incoming edges
                # This includes orphans (no edges) AND roots (no incoming but have outgoing)
                if in_deg == 0:
                    disconnection = classify_disconnection(node, in_deg, out_deg)
                    if disconnection:
                        node['disconnection'] = disconnection

                if in_deg > 0 or out_deg > 0:
                    degree_enriched += 1

            # Count topology roles and disconnection sources for summary
            role_counts = {}
            disconnection_counts = {}
            for node in nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            _log(f"   → {degree_enriched} nodes enriched with degree metrics (fallback)", quiet)
            _log(f"   → Topology roles: {role_counts}", quiet)
            if disconnection_counts:
                _log(f"   → Disconnection taxonomy: {disconnection_counts}", quiet)
            G = None  # No graph for analytics

        # Advanced analytics (optional - requires graph_analyzer)
        try:
            from graph_analyzer import find_bottlenecks, find_pagerank, find_communities
            if G is not None:
                # Run analytics
                bottlenecks_raw = find_bottlenecks(G, top_n=20) if len(G) > 0 else []
                pagerank_raw = find_pagerank(G, top_n=20) if len(G) > 0 else []
                communities = find_communities(G) if len(G) > 5 else {}

                # Convert dataclass objects to dicts for JSON serialization
                from dataclasses import asdict
                bottlenecks = [asdict(b) if hasattr(b, '__dataclass_fields__') else b for b in bottlenecks_raw]
                pagerank_top = [asdict(p) if hasattr(p, '__dataclass_fields__') else p for p in pagerank_raw]

                graph_analytics = {
                    'bottlenecks': bottlenecks,
                    'pagerank_top': pagerank_top,
                    'communities_count': len(communities),
                    'communities': {str(k): len(v) for k, v in list(communities.items())[:10]} if communities else {},
                }
                timer.set_output(bottlenecks=len(bottlenecks), pagerank=len(pagerank_top), communities=len(communities))
                _log(f"   → {len(bottlenecks)} bottlenecks identified", quiet)
                _log(f"   → {len(pagerank_top)} PageRank leaders", quiet)
                _log(f"   → {len(communities)} communities detected", quiet)
            else:
                graph_analytics = {}
        except Exception as e:
            graph_analytics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Advanced graph analytics skipped: {e}")

    # Stage 6.6: Statistical Metrics (Entropy, Complexity, Halstead)
    print("\n📊 Stage 6.6: Statistical Metrics...")
    with StageTimer(perf_manager, "Stage 6.6: Statistical Metrics") as timer:
        try:
            from analytics_engine import compute_all_metrics
            statistical_metrics = compute_all_metrics(nodes)
            timer.set_output(
                avg_cyclomatic=statistical_metrics['complexity']['avg'],
                total_volume=statistical_metrics['halstead']['total_volume'],
                estimated_bugs=statistical_metrics['halstead']['estimated_bugs']
            )
            _log(f"   → Avg cyclomatic: {statistical_metrics['complexity']['avg']}", quiet)
            _log(f"   → High complexity nodes: {statistical_metrics['complexity']['high_complexity_count']}", quiet)
            _log(f"   → Est. bugs: {statistical_metrics['halstead']['estimated_bugs']}", quiet)
        except Exception as e:
            statistical_metrics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Statistical metrics skipped: {e}")

    # Stage 6.7: Semantic Purpose Analysis (PURPOSE = f(edges))
    print("\n🎯 Stage 6.7: Semantic Purpose Analysis...")
    semantic_analysis = {
        'entry_points': [],
        'node_context': {},
        'centrality': {},
        'role_distribution': {},
        'critical_nodes': {},
        'intent_summary': {}
    }
    with StageTimer(perf_manager, "Stage 6.7: Semantic Purpose") as timer:
        try:
            # Re-use the full graph built in Stage 6.5 (all edge types: calls, imports,
            # contains, inherits …).  Avoids a second build_nx_graph() call.
            # Falls back to building a new graph when Stage 6.5 failed (NetworkX absent).
            if _G_full is not None:
                G = _G_full
            else:
                G = build_nx_graph(nodes, edges)

            # Find entry points (main, CLI, routes, handlers)
            entry_points = find_entry_points(G)
            semantic_analysis['entry_points'] = entry_points

            # Propagate context from entry points downstream (top-down comprehension)
            node_context = propagate_context(G, entry_points, max_depth=15)
            semantic_analysis['node_context'] = {
                'reachable_count': len(node_context),
                'max_depth': max((ctx.get('depth_from_entry', 0) for ctx in node_context.values()), default=0)
            }

            # Closeness centrality was already computed on the full graph in Stage 6.5
            # and stored on each node as 'closeness_centrality'.  Build the summary
            # dict expected by identify_critical_nodes without recomputing anything.
            centrality = {
                node_id: {
                    'betweenness': 0.0,  # already stored on node; not needed here
                    'closeness': node.get('closeness_centrality', 0.0),
                    'pagerank': 0.0,      # already stored on node; not needed here
                }
                for node in nodes
                for node_id in [node.get('id')]
                if node_id
            }

            # Build centrality summary (top 10 by closeness + distribution stats)
            closeness_values = [m.get('closeness', 0.0) for m in centrality.values()]
            if closeness_values:
                top_10_closeness = sorted(
                    [(nid, m.get('closeness', 0.0)) for nid, m in centrality.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
                semantic_analysis['centrality'] = {
                    'top_10_closeness': [{'id': nid, 'score': round(score, 4)} for nid, score in top_10_closeness],
                    'distribution': {
                        'min': round(min(closeness_values), 4),
                        'max': round(max(closeness_values), 4),
                        'mean': round(sum(closeness_values) / len(closeness_values), 4),
                        'computed_count': len(closeness_values)
                    }
                }

            # Identify critical nodes (bridges, influential, coordinators).
            # Uses per-node betweenness/pagerank stored in Stage 6.5 for 'bridges' /
            # 'influential'; closeness (full-graph) for 'coordinators'.
            # Build a richer per-node metric dict for identify_critical_nodes.
            centrality_full = {
                node_id: {
                    'betweenness': node.get('betweenness_centrality', 0.0),
                    'closeness': node.get('closeness_centrality', 0.0),
                    'pagerank': node.get('pagerank', 0.0),
                }
                for node in nodes
                for node_id in [node.get('id')]
                if node_id
            }
            critical_nodes = identify_critical_nodes(G, centrality_full, top_n=10)
            semantic_analysis['critical_nodes'] = critical_nodes

            # Enrich nodes with semantic roles, context, and critical flags
            role_counts = {'utility': 0, 'orchestrator': 0, 'hub': 0, 'leaf': 0}
            intent_stats = {'with_docstring': 0, 'with_commits': 0, 'empty': 0}

            for node in nodes:
                node_id = node.get('id')
                if not node_id:
                    continue

                # closeness_centrality already set on the node by Stage 6.5; no-op here.

                # Classify semantic role from degree metrics
                in_deg = node.get('in_degree', 0)
                out_deg = node.get('out_degree', 0)
                semantic_role = classify_node_role(in_deg, out_deg)
                node['semantic_role'] = semantic_role
                role_counts[semantic_role] += 1

                # Add critical node flags
                node['is_bridge'] = node_id in critical_nodes.get('bridges', [])
                node['is_influential'] = node_id in critical_nodes.get('influential', [])
                node['is_coordinator'] = node_id in critical_nodes.get('coordinators', [])

                # Add context propagation data
                if node_id in node_context:
                    ctx = node_context[node_id]
                    node['depth_from_entry'] = ctx.get('depth_from_entry', -1)
                    node['reachable_from_entry'] = True
                    if ctx.get('call_chain'):
                        node['call_chain_length'] = len(ctx['call_chain'])
                else:
                    node['reachable_from_entry'] = False
                    node['depth_from_entry'] = -1

                # Extract intent profile (docstring + commit history)
                file_path = node.get('file_path', '')
                source_code = node.get('body_source', '')
                if file_path and (source_code or node.get('kind') in ('function', 'method', 'class')):
                    intent_profile = build_node_intent_profile(
                        node_id=node_id,
                        file_path=file_path,
                        source_code=source_code or '',
                        repo_path=target
                    )
                    # Only store if we extracted something meaningful
                    has_docstring = bool(intent_profile.get('docstring'))
                    has_commits = bool(intent_profile.get('recent_commits'))
                    if has_docstring or has_commits:
                        node['intent_profile'] = {
                            'has_docstring': has_docstring,
                            'has_commits': has_commits,
                        }
                        if has_docstring:
                            node['intent_profile']['docstring'] = intent_profile['docstring'][:200]
                            intent_stats['with_docstring'] += 1
                        if has_commits:
                            node['intent_profile']['commit_intents'] = intent_profile.get('commit_intents', [])
                            intent_stats['with_commits'] += 1
                    else:
                        intent_stats['empty'] += 1

            semantic_analysis['role_distribution'] = role_counts
            semantic_analysis['intent_summary'] = {
                'with_docstring': intent_stats['with_docstring'],
                'with_commits': intent_stats['with_commits'],
                'empty_profiles': intent_stats['empty'],
                'total_processed': sum(intent_stats.values())
            }

            timer.set_output(
                entry_points=len(entry_points),
                reachable=len(node_context),
                roles=sum(role_counts.values()),
                intents=intent_stats['with_docstring'] + intent_stats['with_commits']
            )
            _log(f"   → {len(entry_points)} entry points detected", quiet)
            _log(f"   → {len(node_context)} nodes reachable from entry", quiet)
            _log(f"   → Roles: {role_counts['utility']} utility, {role_counts['orchestrator']} orchestrator, {role_counts['hub']} hub, {role_counts['leaf']} leaf", quiet)
            _log(f"   → Intent: {intent_stats['with_docstring']} with docstring, {intent_stats['with_commits']} with commits", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Semantic purpose analysis skipped: {e}")

    # Stage 6.8: Codome Boundary Generation
    print("\n🌐 Stage 6.8: Codome Boundary Generation...")
    codome_result = {'boundary_nodes': [], 'inferred_edges': [], 'summary': {}}
    with StageTimer(perf_manager, "Stage 6.8: Codome Boundaries") as timer:
        try:
            codome_result = create_codome_boundaries(nodes, edges)
            timer.set_output(
                boundaries=codome_result['total_boundaries'],
                inferred_edges=codome_result['total_inferred_edges']
            )
            if codome_result['boundary_nodes']:
                _log(f"   → {codome_result['total_boundaries']} codome boundary nodes created", quiet)
                _log(f"   → {codome_result['total_inferred_edges']} inferred edges generated", quiet)
                _log(f"   → Sources: {codome_result['summary']}", quiet)
                # Add boundary nodes and inferred edges to main lists for visualization
                # Mark with _fromCodome flag for UI filtering
                for bn in codome_result['boundary_nodes']:
                    bn['_fromCodome'] = True
                for ie in codome_result['inferred_edges']:
                    ie['_fromCodome'] = True
                nodes.extend(codome_result['boundary_nodes'])
                edges.extend(codome_result['inferred_edges'])
            else:
                print("   → No disconnected nodes to link")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Codome boundary generation skipped: {e}")

    # Stage 7: Data Flow
    print("\n🌊 Stage 7: Data Flow Analysis...")
    with StageTimer(perf_manager, "Stage 7: Data Flow Analysis") as timer:
        data_flow = compute_data_flow(nodes, edges)
        timer.set_output(sources=len(data_flow['data_sources']), sinks=len(data_flow['data_sinks']))
    _log(f"   → {len(data_flow['data_sources'])} data sources", quiet)
    _log(f"   → {len(data_flow['data_sinks'])} data sinks", quiet)

    # Stage 8: Performance Prediction
    print("\n⏱️  Stage 8: Performance Prediction...")
    with StageTimer(perf_manager, "Stage 8: Performance Prediction") as timer:
        try:
            perf = predict_performance(nodes, exec_flow)
            perf_summary = perf.summary() if hasattr(perf, 'summary') else {}
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️  Performance prediction skipped: {e}")
            perf_summary = {}

    # Stage 8.5: Constraint Field Validation
    print("\n🚧 Stage 8.5: Constraint Field Validation...")
    constraint_report = {}
    with StageTimer(perf_manager, "Stage 8.5: Constraint Validation") as timer:
        try:
            from constraint_engine import ConstraintEngine
            engine = ConstraintEngine()
            constraint_report = engine.validate_graph(nodes, edges)
            timer.set_output(
                antimatter=constraint_report['antimatter']['count'],
                policy=constraint_report['policy_violations']['count'],
                signals=constraint_report['signals']['count']
            )
            # Show architecture detection
            arch_detect = constraint_report.get('architecture_detection', {})
            if arch_detect:
                is_layered = arch_detect.get('is_layered', False)
                arch_type = "Layered" if is_layered else "Non-layered"
                _log(f"   → Architecture: {arch_type} (confidence: {arch_detect.get('confidence', 0):.0%})", quiet)
                if constraint_report.get('layer_validation_skipped'):
                    _log(f"   → Layer constraints: SKIPPED (non-layered codebase)", quiet)
            _log(f"   → Antimatter (Tier A): {constraint_report['antimatter']['count']}", quiet)
            _log(f"   → Policy (Tier B): {constraint_report['policy_violations']['count']}", quiet)
            _log(f"   → Signals (Tier C): {constraint_report['signals']['count']}", quiet)
            _log(f"   → Valid: {constraint_report['valid']}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Constraint validation skipped: {e}")

    # Stage 8.6: Purpose Intelligence (Q-Scores)
    print("\n🧠 Stage 8.6: Purpose Intelligence...")
    codebase_intelligence = {}
    with StageTimer(perf_manager, "Stage 8.6: Purpose Intelligence") as timer:
        try:
            from purpose_intelligence import enrich_nodes_with_intelligence
            nodes, codebase_intelligence = enrich_nodes_with_intelligence(nodes, edges)
            timer.set_output(
                codebase_q=codebase_intelligence.get('codebase_intelligence', 0),
                interpretation=codebase_intelligence.get('interpretation', 'Unknown'),
            )
            _log(f"   → Codebase Intelligence: {codebase_intelligence.get('codebase_intelligence', 0):.3f}", quiet)
            _log(f"   → Interpretation: {codebase_intelligence.get('interpretation', 'Unknown')}", quiet)
            dist = codebase_intelligence.get('distribution', {})
            _log(f"   → Distribution: {dist.get('excellent', 0)} excellent, {dist.get('good', 0)} good, {dist.get('moderate', 0)} moderate, {dist.get('poor', 0)} poor", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Purpose Intelligence skipped: {e}")

    # Compute aggregate metrics
    total_time = time.time() - start_time

    # Type distribution
    types = Counter(n.get('type', 'Unknown') for n in nodes)

    # Ring distribution (Clean Architecture)
    rings = Counter(n.get('ring', 'unknown') for n in nodes)

    # Edge breakdown + KPIs
    edge_types = Counter(e.get('edge_type', 'unknown') for e in edges)
    total_edges = len(edges)
    unresolved_edges = sum(1 for e in edges if e.get('resolution') == 'unresolved')
    resolved_edges = total_edges - unresolved_edges
    edge_resolution_percent = (resolved_edges / total_edges * 100) if total_edges else 0.0
    call_edges = edge_types.get('calls', 0)
    import_edges = edge_types.get('imports', 0)
    call_ratio_percent = (call_edges / total_edges * 100) if total_edges else 0.0
    orphan_count = len(exec_flow.orphans)
    orphan_percent = (orphan_count / len(nodes) * 100) if nodes else 0.0
    reachability_percent = max(0.0, 100.0 - exec_flow.dead_code_percent)
    graph_density = (total_edges / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0.0

    # RPBL averages
    rpbl_sums = {'responsibility': 0, 'purity': 0, 'boundary': 0, 'lifecycle': 0}
    for n in nodes:
        rpbl = n.get('rpbl', {})
        for k in rpbl_sums:
            rpbl_sums[k] += rpbl.get(k, 0)
    rpbl_avgs = {k: round(v / len(nodes), 1) if nodes else 0 for k, v in rpbl_sums.items()}

    # Build complete output
    full_output = {
        'nodes': list(nodes),  # Required for report generator
        'edges': list(edges),  # Required for report generator
        'meta': {
            'target': str(target),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'analysis_time_ms': int(total_time * 1000),
            'version': '4.0.0',
            'deterministic': True,
            'hostname': socket.gethostname(),
            'cwd': os.getcwd()
        },
        'counts': {
            'nodes': len(nodes),
            'edges': len(edges),
            'files': len(set(n.get('file_path', '') for n in nodes)),
            'entry_points': len(exec_flow.entry_points),
            'orphans': len(exec_flow.orphans),
            'cycles': knots['cycles_detected']
        },
        'stats': unified_stats,
        'coverage': {
            'type_coverage': 100.0,
            'ring_coverage': (len(nodes) - rings.get('unknown', 0)) / len(nodes) * 100 if nodes else 0,
            'rpbl_coverage': rpbl_count / len(nodes) * 100 if nodes else 0,
            'dead_code_percent': exec_flow.dead_code_percent
        },
        'classification': unified_classification,
        'auto_discovery': unified_auto_discovery,
        'ecosystem_discovery': ecosystem_discovery,
        'dependencies': unified_dependencies,
        'architecture': unified_architecture,
        'llm_enrichment': unified_llm_enrichment,
        'warnings': unified_warnings,
        'recommendations': unified_recommendations,
        'theory_completeness': _calculate_theory_completeness(nodes),
        'distributions': {
            'types': dict(types.most_common(15)),
            'rings': dict(rings),
            'atoms': dict(Counter(n.get('atom', '') for n in nodes)),
            'levels': dict(Counter(n.get('level', 'L3') for n in nodes)),
            'level_zones': dict(Counter(n.get('level_zone', 'SEMANTIC') for n in nodes)),
        },
        'analytics': statistical_metrics,
        'edge_types': dict(edge_types),
        'rpbl_profile': rpbl_avgs,
        'kpis': {
            'nodes_total': len(nodes),
            'edges_total': total_edges,
            'edge_resolution_percent': round(edge_resolution_percent, 1),
            'resolved_edges': resolved_edges,
            'unresolved_edges': unresolved_edges,
            'call_edges': call_edges,
            'import_edges': import_edges,
            'call_ratio_percent': round(call_ratio_percent, 1),
            'reachability_percent': round(reachability_percent, 1),
            'dead_code_percent': round(exec_flow.dead_code_percent, 1),
            'orphan_count': orphan_count,
            'orphan_percent': round(orphan_percent, 1),
            'knot_score': knots.get('knot_score', 0),
            'cycles_detected': knots.get('cycles_detected', 0),
            'avg_fanout': round(markov.get('avg_fanout', 0.0), 2),
            'graph_density': round(graph_density, 4),
            'top_hub_count': 0,
            'topology_shape': 'UNKNOWN',
            # Constraint Field metrics
            'antimatter_count': constraint_report.get('antimatter', {}).get('count', 0) if constraint_report else 0,
            'policy_violation_count': constraint_report.get('policy_violations', {}).get('count', 0) if constraint_report else 0,
            'signal_count': constraint_report.get('signals', {}).get('count', 0) if constraint_report else 0,
            # Purpose Intelligence metrics
            'codebase_intelligence': codebase_intelligence.get('codebase_intelligence', 0) if codebase_intelligence else 0,
            'codebase_interpretation': codebase_intelligence.get('interpretation', 'Unknown') if codebase_intelligence else 'Unknown',
            'q_distribution': codebase_intelligence.get('distribution', {}) if codebase_intelligence else {},
            'rho_antimatter': round(constraint_report.get('antimatter', {}).get('rho_antimatter', 0), 4) if constraint_report else 0,
            'rho_policy': round(constraint_report.get('policy_violations', {}).get('rho_policy', 0), 4) if constraint_report else 0,
            'constraint_valid': constraint_report.get('valid', True) if constraint_report else True,
            # Codome boundary KPIs
            'codome_boundary_count': codome_result.get('total_boundaries', 0),
            'codome_inferred_edges': codome_result.get('total_inferred_edges', 0),
            # Capability status KPIs (optional stages)
            'ecosystem_discovery_status': ecosystem_discovery_status,
            'ecosystem_discovery_error': ecosystem_discovery_error,
        },
        'purpose_field': purpose_field.summary(),
        'execution_flow': dict(exec_flow.summary(), **{
            'entry_points': exec_flow.entry_points,
            'orphans': exec_flow.orphans
        }),
        'markov': markov,
        'knots': knots,
        'graph_analytics': graph_analytics,
        'statistical_metrics': statistical_metrics,
        'semantic_analysis': semantic_analysis,
        'data_flow': data_flow,
        'performance': perf_summary,
        'constraint_field': constraint_report if constraint_report else {},
        'top_hubs': [],
        'orphans_list': exec_flow.orphans[:20],  # First 20
        'orphan_integration': [],
        # Codome boundary visualization layer
        'codome_boundaries': {
            'boundary_nodes': codome_result.get('boundary_nodes', []),
            'inferred_edges': codome_result.get('inferred_edges', []),
            'summary': codome_result.get('summary', {}),
            'total_boundaries': codome_result.get('total_boundaries', 0),
            'total_inferred_edges': codome_result.get('total_inferred_edges', 0)
        },
    }

    # Compute top hubs
    in_deg = Counter()
    for e in edges:
        in_deg[e.get('target', '')] += 1
    for node_id, deg in in_deg.most_common(10):
        name = node_id.split(':')[-1] if ':' in node_id else node_id.split('/')[-1]
        full_output['top_hubs'].append({'name': name, 'in_degree': deg})
    full_output['kpis']['top_hub_count'] = len(full_output['top_hubs'])

    # Include SmartIgnore discovery data in output
    if smartignore_manifest:
        from src.core.smart_ignore import SmartIgnore as _SI
        si_helper = _SI(str(target))
        full_output['smart_ignore'] = si_helper.manifest_to_dict(smartignore_manifest)

    # Include Contextome Intelligence in output (Stage 0.8)
    if contextome_result is not None:
        full_output['contextome'] = contextome_result.to_dict()

    # ==========================================================================
    # FILE-CENTRIC VIEW: Hybrid atom/file navigation
    # ==========================================================================
    print("\n📁 Building file index...")
    with StageTimer(perf_manager, "File Index Building") as timer:
        files_index = build_file_index(nodes, edges, str(target))
        file_boundaries = build_file_boundaries(files_index)

        # Enrich file boundaries with comprehensive metadata
        try:
            enricher = FileEnricher(root_path=str(target), enable_git=False)
            file_boundaries = enricher.enrich_boundaries(file_boundaries)
            _log(f"   → File metadata enriched for {len(file_boundaries)} files", quiet)
        except Exception as e:
            print(f"   ⚠️ File enrichment failed: {e}")

        full_output['files'] = files_index
        full_output['file_boundaries'] = file_boundaries
        full_output['counts']['files_with_atoms'] = len(files_index)
        timer.set_output(files=len(files_index), atoms_mapped=sum(f['atom_count'] for f in file_boundaries))

    _log(f"   → {len(files_index)} files indexed", quiet)
    _log(f"   → {sum(f['atom_count'] for f in file_boundaries)} atoms mapped to files", quiet)

    # Save output
    out_path = resolved_output_dir

    out_path.mkdir(parents=True, exist_ok=True)

    # NOTE: The LLM-oriented output JSON is the single source of truth for analysis results.

    # Stage 9: Roadmap Evaluation
    print("\n🛣️  Stage 9: Roadmap Evaluation...")
    with StageTimer(perf_manager, "Stage 9: Roadmap Evaluation") as timer:
        roadmap_name = options.get('roadmap')
        if roadmap_name:
            try:
                roadmap_path = Path(__file__).parent / "roadmaps" / f"{roadmap_name}.json"
                if roadmap_path.exists():
                    evaluator = RoadmapEvaluator(str(roadmap_path))
                    # Collect all file paths
                    all_files = [str(f) for f in Path(target_path).rglob('*') if f.is_file()]
                    roadmap_result = evaluator.evaluate(all_files)
                    full_output['roadmap'] = roadmap_result
                    timer.set_output(readiness=roadmap_result.get('readiness_score', 0))
                    _log(f"   → Roadmap '{roadmap_name}' analyzed: {roadmap_result['readiness_score']:.0f}% ready", quiet)
                else:
                    timer.set_status("WARN", f"Roadmap '{roadmap_name}' not found")
                    print(f"   ⚠️ Roadmap '{roadmap_name}' not found in roadmaps directory")
            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Roadmap analysis failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            timer.set_status("SKIP")
            print("   → Skipped (no --roadmap specified)")

    # Stage 10: Visual Topology Analysis
    print("\n🧠 Stage 10: Visual Reasoning...")
    with StageTimer(perf_manager, "Stage 10: Visual Reasoning") as timer:
        try:
            topo = TopologyClassifier()
            topology_result = topo.classify(nodes, edges)
            full_output['topology'] = topology_result
            full_output['kpis']['topology_shape'] = topology_result.get('shape', 'UNKNOWN')
            timer.set_output(shape=topology_result.get('shape', 'UNKNOWN'))
            _log(f"   → Visual Shape: {topology_result['shape']}", quiet)
            _log(f"   → Description: {topology_result['description']}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Topology analysis failed: {e}")

    # Stage 11: Semantic Cortex (Concept Extraction)
    print("\n🧠 Stage 11: Semantic Cortex...")
    with StageTimer(perf_manager, "Stage 11: Semantic Cortex") as timer:
        try:
            cortex = ConceptExtractor()
            semantics = cortex.extract_concepts(nodes)
            full_output['semantics'] = semantics
            timer.set_output(concepts=len(semantics.get('top_concepts', [])))
            _log(f"   → Domain Inference: {semantics['domain_inference']}", quiet)
            _log(f"   → Top Concepts: {', '.join([t['term'] for t in semantics['top_concepts'][:5]])}", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Semantic analysis failed: {e}")

    # ==========================================================================
    # OUTPUT CONSOLIDATION: 2 files only
    # 1. output_llm-oriented_<project>_<timestamp>.json - Structured knowledge bundle
    # 2. output_human-readable_<project>_<timestamp>.html - Visual report (embeds Brain Download)
    # ==========================================================================

    # Always include pipeline performance data (feeds pipeline_report.json and brain_download)
    full_output['pipeline_performance'] = perf_manager.to_dict()

    skip_html = options.get("skip_html", True)
    if not skip_html:
        # Generate Brain Download content (for embedding in HTML)
        from brain_download import generate_brain_download
        brain_content = generate_brain_download(full_output)
        full_output['brain_download'] = brain_content  # Embed in JSON for HTML access

    # Stage 12: AI Insights (optional - requires Vertex AI)
    if options.get('ai_insights'):
        print("\n✨ Stage 12: AI Insights Generation (Vertex AI)...")
        with StageTimer(perf_manager, "Stage 12: AI Insights") as timer:
            try:
                ai_insights = _generate_ai_insights(full_output, out_path, options)
                if ai_insights:
                    full_output['ai_insights'] = ai_insights
                    timer.set_output(insights=len(ai_insights) if isinstance(ai_insights, list) else 1)
                    print("   → AI insights generated successfully")
                else:
                    timer.set_status("WARN", "No results returned")
                    print("   ⚠️ AI insights generation returned no results")
            except Exception as e:
                timer.set_status("FAIL", str(e))
                print(f"   ⚠️ AI insights generation failed: {e}")


    # Stage 13: Manifest Writer (Provenance & Integrity)
    print("\n📦 Stage 13: Manifest Writer...")
    with StageTimer(perf_manager, "Stage 13: Manifest Writer") as timer:
        try:
            # Capturing provenance and integrity data for "Measured Codome"
            # Calculate Merkle Root once all nodes are finalized
            merkle_root = calculate_merkle_root([n.get('id', n.get('name', '')) for n in nodes])

            manifest = {
                "schema_version": "manifest.v2",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "batch_id": batch_id,
                "waybill": {
                    "parcel_id": f"pcl_{hashlib.sha256(merkle_root.encode()).hexdigest()[:12]}",
                    "batch_id": batch_id,
                    "merkle_root": merkle_root,
                    "refinery_signature": refinery_signature,
                    "context_vector": [0.0] * 32, # Placeholder for Phase 28 semantic vector
                    "route": [
                        {
                            "event": "manifest_signed",
                            "timestamp": time.time(),
                            "agent": "full_analysis.py",
                            "context": {"stage": "13"}
                        }
                    ]
                },
                "input": {
                    "target_path": str(Path(target_path).resolve()),
                    "node_count": len(nodes),
                    "edge_count": len(edges),
                    "merkle_root": merkle_root
                },
                "pipeline": {
                    "stages_executed": [s.stage_name for s in perf_manager.stages] if (perf_manager and hasattr(perf_manager, 'stages')) else [],
                    "total_stages": 22,
                    "version": "1.0.0-smoc"
                },
                "environment": {
                    "python_version": sys.version.split()[0],
                    "platform": sys.platform
                }
            }
            full_output['manifest'] = manifest
            _log(f"   → Manifest generated: {len(nodes)} nodes, {len(edges)} edges recorded", quiet)
            _log(f"   → Status: SIGNED (Integrity verified)", quiet)
            timer.set_output(nodes=len(nodes), edges=len(edges))
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Manifest generation failed: {e}")

    # Stage 14: Information Graph Theory (IGT) Metrics
    print("\n📈 Stage 14: IGT Metrics...")
    igt_results = {}
    with StageTimer(perf_manager, "Stage 14: IGT Metrics") as timer:
        try:
            # 1. Directory Stability
            dir_structure = defaultdict(list)
            for f in full_output.get('file_boundaries', []):
                p = Path(f['file'])
                parent = str(p.parent)
                dir_structure[parent].append(p.name)

            stability_report = StabilityCalculator.analyze_directories(dir_structure)

            # 2. Type-Aware Orphan Analysis
            orphans_data = []
            for o_id in exec_flow.orphans:
                # Find the node in the nodes list
                o_node = next((n for n in nodes if n.get('id') == o_id), None)
                if o_node:
                    orphans_data.append({
                        'id': o_id,
                        'type': o_node.get('type', 'file'),
                        'path': o_node.get('file_path', '')
                    })

            classified_orphans = OrphanClassifier.filter_true_orphans(orphans_data)

            igt_results = {
                'directory_stability': stability_report,
                'classified_orphans': classified_orphans,
                'avg_stability': sum(s['stability_index'] for s in stability_report.values()) / len(stability_report) if stability_report else 1.0,
                'critical_orphans_count': sum(1 for o in classified_orphans if o['is_problem'])
            }

            full_output['igt'] = igt_results
            full_output['kpis']['igt_stability_index'] = round(igt_results['avg_stability'], 3)
            full_output['kpis']['critical_orphans'] = igt_results['critical_orphans_count']

            timer.set_output(
                avg_stability=igt_results['avg_stability'],
                critical_orphans=igt_results['critical_orphans_count']
            )
            _log(f"   → Average Directory Stability: {igt_results['avg_stability']:.3f}", quiet)
            _log(f"   → Critical Orphans: {igt_results['critical_orphans_count']}", quiet)

        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ IGT analysis failed: {e}")

    # =========================================================================
    # STAGE 15: DATABASE PERSISTENCE (Phase 30)
    # =========================================================================
    db_run_id = None
    if db_manager:
        print("\n💾 Stage 15: Database Persistence...")
        with StageTimer(perf_manager, "Stage 15: Database Persistence") as timer:
            try:
                from src.core.database.backends.base import AnalysisRun
                from datetime import datetime as dt_datetime

                # Create run record
                run = AnalysisRun(
                    id=f"run_{hashlib.sha256(f'{target}-{time.time()}'.encode()).hexdigest()[:12]}",
                    project_name=target.name,
                    project_path=str(target),
                    started_at=dt_datetime.now(),
                    collider_version="1.0.0",
                    status="running",
                    options=options,
                )

                db_run_id = db_manager.create_run(run)

                # Persist nodes and edges
                node_count = db_manager.insert_nodes(db_run_id, nodes)
                edge_count = db_manager.insert_edges(db_run_id, edges)

                # Mark complete
                db_manager.update_run(
                    db_run_id,
                    status="completed",
                    completed_at=dt_datetime.now(),
                    node_count=node_count,
                    edge_count=edge_count,
                )

                timer.set_output(run_id=db_run_id, nodes=node_count, edges=edge_count)
                _log(f"   → Run ID: {db_run_id}", quiet)
                _log(f"   → Persisted {node_count} nodes, {edge_count} edges", quiet)
                _log(f"   → DB: {db_config.get_sqlite_path()}", quiet)

                # Update file tracking if delta tracker is available
                if delta_tracker and delta_result:
                    from src.core.database.incremental.hasher import FileHasher
                    hasher = FileHasher()
                    file_hashes = hasher.hash_directory(target)
                    delta_tracker.update_tracking(str(target), db_run_id, file_hashes)
                    _log(f"   → Updated file tracking for {len(file_hashes)} files", quiet)

                # Retention: purge old runs after successful persistence
                if db_config and db_config.history_enabled:
                    purged = db_manager.purge_old_runs(project_path=str(target))
                    if purged > 0:
                        _log(f"   → Retention: purged {purged} old run(s)", quiet)

            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Database persistence failed: {e}")

    # Stage 16: Semantic Vector Indexing (GraphRAG)
    # Only runs when optional deps (lancedb, sentence-transformers) are installed.
    vectorization_status = "skipped"
    vectorization_error = ""
    _has_graphrag_deps = importlib.util.find_spec("lancedb") and importlib.util.find_spec("sentence_transformers")
    if _has_graphrag_deps:
        try:
            from src.core.rag.embedder import GraphRAGEmbedder
            persistent_db = target / ".collider" / "collider.db"
            embedder = GraphRAGEmbedder(db_path=persistent_db)
            embedder.embed_graph()
            vectorization_status = "ok"
        except Exception as e:
            vectorization_status = "failed"
            vectorization_error = str(e)
            print(f"\n   ⚠️ Stage 16 Vectorization Failed: {e}")

    # Persist optional stage status for downstream scoring and diagnostics.
    full_output.setdefault('kpis', {})['vectorization_status'] = vectorization_status
    full_output['kpis']['vectorization_error'] = vectorization_error
    if vectorization_status == "failed":
        warnings_list = full_output.setdefault('warnings', [])
        if isinstance(warnings_list, list):
            warnings_list.append(f"stage16_vectorization_failed: {vectorization_error}")

    # Stage 17: Collider Trinity (Incoherence, Purpose Decomposition, Gap Detection)
    print("\n🔬 Stage 17: Collider Trinity...")
    try:
        from src.core.incoherence import compute_incoherence
        from src.core.purpose_decomposition import decompose_purposes
        from src.core.gap_detector import detect_gaps

        incoherence_result = compute_incoherence(full_output)
        full_output['incoherence'] = incoherence_result.to_dict()

        decomposition_results = decompose_purposes(full_output)
        full_output['purpose_decomposition'] = [r.to_dict() for r in decomposition_results]

        gap_report = detect_gaps(full_output, decomposition_results)
        full_output['gap_report'] = gap_report.to_dict()

        _log(f"   → Incoherence: I={incoherence_result.i_total:.3f}  Health={incoherence_result.health_10:.1f}/10", quiet)
        _log(f"   → Purpose Decomposition: {len(decomposition_results)} containers analyzed", quiet)
        gap_count = len(gap_report.gaps)
        crit_count = sum(1 for g in gap_report.gaps if g.severity == 'critical')
        _log(f"   → Gap Detection: {gap_count} gaps ({crit_count} critical), coverage={gap_report.coverage:.1%}", quiet)
    except Exception as e:
        print(f"   ⚠️ Trinity computation failed: {e}")
        import traceback
        traceback.print_exc()

    # Stage 18: Temporal Analysis (REH integration)
    print("\n🔬 Stage 18: Temporal Analysis...")
    try:
        from src.core.temporal_analysis import compute_temporal_analysis
        temporal_result = compute_temporal_analysis(full_output, repo_path=str(target))
        full_output['temporal_analysis'] = temporal_result.to_dict()
        if temporal_result.available:
            _log(f"   → {temporal_result.total_commits} commits, {temporal_result.active_days} active days", quiet)
            _log(f"   → {len(temporal_result.hotspots)} hotspots, {len(temporal_result.change_coupling)} coupling pairs", quiet)
            _log(f"   → Bus factor: {temporal_result.bus_factor}, median file age: {temporal_result.median_age_days:.0f} days", quiet)
        else:
            _log(f"   → Skipped: {temporal_result.error}", quiet)
    except Exception as e:
        print(f"   ⚠️ Temporal analysis failed: {e}")
        import traceback
        traceback.print_exc()

    # Stage 19: Ideome Synthesis (Rosetta Stone)
    print("\n🔬 Stage 19: Ideome Synthesis...")
    try:
        from src.core.ideome_synthesis import synthesize_ideome
        ideome_result = synthesize_ideome(full_output)
        full_output['ideome'] = ideome_result.to_dict()
        _log(f"   → Coherence: {ideome_result.global_coherence:.3f}", quiet)
        _log(f"   → Drift: code={ideome_result.global_drift_C:.3f} docs={ideome_result.global_drift_X:.3f}", quiet)
        _log(f"   → Coverage: {ideome_result.coverage:.1%} ({ideome_result.node_count} nodes)", quiet)
    except Exception as e:
        print(f"   ⚠️ Ideome synthesis failed: {e}")
        import traceback
        traceback.print_exc()

    # Stage 20: Data Chemistry (Cross-Signal Correlation)
    print("\n🧪 Stage 20: Data Chemistry...")
    try:
        from src.core.data_chemistry import ChemistryLab
        chem_lab = ChemistryLab()
        chem_lab.ingest(full_output)
        chem_result = chem_lab.get_result()
        full_output['chemistry'] = chem_result.to_dict()
        full_output['_chemistry_lab'] = chem_lab  # ephemeral live ref
        syn_names = [s.name for s in chem_result.syndromes]
        if not quiet:
            print(f"   → Syndromes: {syn_names or 'none'}")
            print(f"   → Contradictions: {len(chem_result.contradictions)}")
            print(f"   → Compound severity: {chem_result.compound_severity:.3f}")
            print(f"   → Signal coverage: {chem_result.signal_coverage:.0%}")
            if chem_result.convergence:
                print(f"   → Convergent nodes: {chem_result.convergence.convergent_count} "
                      f"({chem_result.convergence.critical_count} critical)")
        # AI Consumer Summary -- structured block for downstream AI consumers
        full_output['ai_consumer_summary'] = chem_lab.build_ai_consumer_summary()
        if not quiet:
            print(f"   → AI Consumer Summary: grade={full_output['ai_consumer_summary']['data_utility_grade']}")
    except Exception as e:
        print(f"   ⚠️ Data Chemistry failed: {e}")
        import traceback
        traceback.print_exc()

    # Stage 21: Insights Compilation
    print("\n🔬 Stage 21: Insights Compilation...")
    with StageTimer(perf_manager, "Stage 21: Insights Compilation") as timer:
        try:
            from src.core.insights_compiler import compile_insights, compile_insights_report
            compiled_dict = compile_insights(full_output)
            full_output['compiled_insights'] = compiled_dict
            # Generate markdown for file output
            report_obj = compile_insights_report(full_output)
            full_output['_insights_markdown'] = report_obj.to_markdown()
            grade = compiled_dict.get('grade', '?')
            finding_count = compiled_dict.get('findings_count', 0)
            timer.set_output(grade=grade, findings=finding_count)
            _log(f"   → Grade: {grade} ({compiled_dict.get('health_score', 0)}/10)", quiet)
            _log(f"   → {finding_count} findings compiled", quiet)
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Insights compilation failed: {e}")

    # Stage 22: Write consolidated outputs
    print("\n📦 Stage 22: Generating Consolidated Outputs...")

    unified_json = None
    viz_file = None
    with StageTimer(perf_manager, "Stage 22: Output Generation") as timer:
        try:
            # Update performance data INSIDE timer (captures stages 1-11 timing)
            full_output['pipeline_performance'] = perf_manager.to_dict()

            from src.core.output_generator import generate_outputs
            skip_html = options.get("skip_html", True)

            # Attach Waybills to individual nodes (Phase 28)
            if not quiet:
                print(f"   → Attaching waybills to {len(nodes)} particles...")
            for node in nodes:
                node_id = node.get('id', node.get('name', 'unknown'))

                # Baseline waybill
                waybill = {
                    "parcel_id": f"pcl_{hashlib.sha256(f'{node_id}-{batch_id}'.encode()).hexdigest()[:12]}",
                    "parent_id": f"pcl_{hashlib.sha256(merkle_root.encode()).hexdigest()[:12]}",
                    "batch_id": batch_id,
                    "merkle_root": merkle_root,
                    "refinery_signature": refinery_signature,
                }

                # Padding bloat for non AI modes
                if not skip_html:
                    waybill["context_vector"] = [0.0] * 32
                    waybill["route"] = [
                        {
                            "event": "refined",
                            "timestamp": time.time(),
                            "agent": "full_analysis.py",
                            "context": {"batch": batch_id}
                        }
                    ]

                node['waybill'] = waybill

            verbose_output = options.get("verbose_output", False)
            outputs = generate_outputs(full_output, out_path, target_name=target.name, skip_html=skip_html, verbose_output=verbose_output)
            unified_json = outputs["llm"]
            viz_file = outputs.get("html")
            timer.set_output(json=1, html=1 if viz_file else 0)
            _log(f"   → Data: {unified_json}", quiet)
            if "tokens" in outputs:
                for k, v in outputs["tokens"].items():
                    if isinstance(v, dict):
                        print(f"      - {k}:")
                        for sub_k, sub_v in sorted(v.items(), key=lambda x: str(x[0])):
                            print(f"         * {sub_k}: {sub_v:,} tokens")
                    else:
                        print(f"      - {k}: {v:,} tokens")
            if viz_file:
                _log(f"   → Visual: {viz_file}", quiet)
            else:
                _log(f"   → Visual: SKIPPED (AI-First Mode)", quiet)
        except Exception as e:
            timer.set_status("FAIL", str(e))
            print(f"   ⚠️ Output generation failed: {e}")

    # Final timing summary
    total_time = time.time() - start_time

    # =========================================================================
    # PIPELINE REPORT: Always write standalone JSON (cheap, enables automation)
    # Report is also written in the except block below for crash resilience.
    # =========================================================================
    report_path = _write_pipeline_report(
        perf_manager, out_path, target, total_time, nodes, edges
    )

    # =========================================================================
    # ENHANCED FINAL SUMMARY (always shown, even in quiet mode)
    # =========================================================================
    peak_mb = perf_manager._peak_memory_kb / 1024 if perf_manager._peak_memory_kb else 0

    print("\n" + "=" * 60)
    print("COLLIDER FULL ANALYSIS COMPLETE")
    print(f"   Target: {target.name}")
    print(f"   Time:   {total_time:.1f}s | Memory: {peak_mb:,.0f} MB peak")
    print(f"   Graph:  {len(nodes):,} nodes, {len(edges):,} edges")

    # Compact stage timing table
    if perf_manager.stages:
        print()
        print("   Stage Timing:")
        for stage in perf_manager.stages:
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
        slowest = perf_manager.get_slowest_stage()
        if slowest and total_time > 0:
            pct = (slowest['latency_ms'] / 1000 / total_time * 100)
            print(f"\n   Bottleneck: {slowest['name']} ({slowest['latency_ms'] / 1000:.1f}s, {pct:.0f}%)")

    print()
    if report_path:
        print(f"   Report: {report_path}")
    if unified_json:
        print(f"   Data:   {unified_json}")
    if viz_file:
        print(f"   Visual: {viz_file}")

    # Detailed timing if requested
    if timing_enabled and not verbose_timing:
        perf_manager.print_summary()

    if open_latest:
        latest_html = _find_latest_html(out_path)
        if latest_html:
            print(f"   Open:   {latest_html}")
            print(f"   Manual: {_manual_open_command(latest_html)}")
            if not _open_file(latest_html):
                print("   Open failed (see system logs for details).")
        else:
            print("   No HTML outputs found to open.")

    # Close database connection
    if db_manager:
        try:
            db_manager.disconnect()
        except Exception:  # noqa: best-effort cleanup
            pass

    print("=" * 60)
    summary = {
        "status": "complete",
        "nodes": full_output.get("counts", {}).get("nodes", 0),
        "edges": full_output.get("counts", {}).get("edges", 0),
        "stages": len(perf_manager.stages) if perf_manager and hasattr(perf_manager, "stages") else 0,
        "elapsed_s": round(total_time, 3),
    }
    print(f"PIPELINE_SUMMARY: {json.dumps(summary)}")

    return full_output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python full_analysis.py <path> [--output <dir>]")
        sys.exit(1)

    target = sys.argv[1]
    output_dir = None

    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    run_full_analysis(target, output_dir)
