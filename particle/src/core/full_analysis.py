#!/usr/bin/env python3
# Theory: L3_APPLICATIONS.md (Collider Pipeline — Full Analysis)
# Theory: L0-L3 Integration (All theory layers converge here)
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
from src.core.intent_extractor import build_node_intent_profiles_batch
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
    'run_full_analysis',
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
    perf_manager, out_path, target, total_time, nodes, edges, pipeline_error=None,
    data_ledger=None,
):
    """Write pipeline_report.json -- best-effort, returns path or None."""
    try:
        report_path = out_path / "pipeline_report.json"
        report = perf_manager.to_dict()
        if data_ledger is not None:
            report["data_availability"] = data_ledger.to_dict()
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
            "tier1_raw": str(out_path / "collider_raw.json"),
            "tier2_briefing": str(out_path / "collider_briefing.json"),
            "tier3_report": str(out_path / "collider_report.html"),
            "collider_output": str(out_path / "collider_output.json"),
            "unified_analysis": str(out_path / "unified_analysis.json"),
            "database": str(out_path / "collider.db"),
            "insights_md": str(out_path / "collider_insights.md"),
            "insights_json": str(out_path / "collider_insights.json"),
            "meta_index": str(out_path / "meta_index.jsonl"),
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


# =============================================================================
# INTERNAL ORCHESTRATOR — delegates to phase modules in src.core.phases
# =============================================================================

def _assemble_output(ctx) -> None:
    """Build ctx.full_output dict from phase intermediates.

    This is the bridge between the analysis phases (1-5) and
    the synthesis/output phases (6-7). It aggregates all intermediate
    results into the canonical full_output dict structure.
    """
    from observability import StageTimer

    nodes = ctx.nodes
    edges = ctx.edges

    # Compute aggregate metrics
    total_time = time.time() - ctx.start_time

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
    exec_flow = ctx.exec_flow
    orphan_count = len(exec_flow.orphans) if exec_flow else 0
    orphan_percent = (orphan_count / len(nodes) * 100) if nodes else 0.0
    reachability_percent = max(0.0, 100.0 - (exec_flow.dead_code_percent if exec_flow else 0.0))
    graph_density = (total_edges / (len(nodes) * (len(nodes) - 1))) if len(nodes) > 1 else 0.0

    # RPBL averages
    rpbl_count = sum(1 for n in nodes if n.get('rpbl'))
    rpbl_sums = {'responsibility': 0, 'purity': 0, 'boundary': 0, 'lifecycle': 0}
    for n in nodes:
        rpbl = n.get('rpbl', {})
        for k in rpbl_sums:
            rpbl_sums[k] += rpbl.get(k, 0)
    rpbl_avgs = {k: round(v / len(nodes), 1) if nodes else 0 for k, v in rpbl_sums.items()}

    # Convenience aliases for optional intermediates
    knots = ctx.knots or {}
    markov = ctx.markov or {}
    constraint_report = ctx.constraint_report
    codebase_intelligence = ctx.codebase_intelligence
    codome_result = ctx.codome_result or {}

    # Build complete output
    ctx.full_output = {
        'nodes': list(nodes),
        'edges': list(edges),
        'meta': {
            'target': str(ctx.target),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'analysis_time_ms': int(total_time * 1000),
            'version': '4.0.0',
            'schema_version': '1.0.0',
            'deterministic': True,
            'hostname': socket.gethostname(),
            'cwd': os.getcwd()
        },
        'counts': {
            'nodes': len(nodes),
            'edges': len(edges),
            'files': len(set(n.get('file_path', '') for n in nodes)),
            'entry_points': len(exec_flow.entry_points) if exec_flow else 0,
            'orphans': len(exec_flow.orphans) if exec_flow else 0,
            'cycles': knots.get('cycles_detected', 0)
        },
        'stats': ctx.unified_stats or {},
        'coverage': {
            'type_coverage': 100.0,
            'ring_coverage': (len(nodes) - rings.get('unknown', 0)) / len(nodes) * 100 if nodes else 0,
            'rpbl_coverage': rpbl_count / len(nodes) * 100 if nodes else 0,
            'dead_code_percent': exec_flow.dead_code_percent if exec_flow else 0.0
        },
        'classification': ctx.unified_classification or {},
        'auto_discovery': ctx.unified_auto_discovery or {},
        'ecosystem_discovery': ctx.ecosystem_discovery or {},
        'dependencies': ctx.unified_dependencies or {},
        'architecture': ctx.unified_architecture or {},
        'llm_enrichment': ctx.unified_llm_enrichment or {},
        'warnings': ctx.unified_warnings or [],
        'recommendations': ctx.unified_recommendations or [],
        'theory_completeness': _calculate_theory_completeness(nodes),
        'distributions': {
            'types': dict(types.most_common(15)),
            'rings': dict(rings),
            'atoms': dict(Counter(n.get('atom') or '' for n in nodes)),
            'levels': dict(Counter(n.get('level') or 'L3' for n in nodes)),
            'level_zones': dict(Counter(n.get('level_zone') or 'SEMANTIC' for n in nodes)),
            'layers': dict(Counter(n.get('layer') or 'unknown' for n in nodes)),
        },
        'analytics': ctx.statistical_metrics or {},
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
            'dead_code_percent': round(exec_flow.dead_code_percent if exec_flow else 0.0, 1),
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
            # Concordance KPIs (Stage 8.7)
            'concordance_alignment': ctx.concordance_result.get('alignment_score', 0) if ctx.concordance_result else 0,
            'concordance_health': ctx.concordance_result.get('overall_health', 0) if ctx.concordance_result else 0,
            'concordance_issues': len(ctx.concordance_result.get('issues', [])) if ctx.concordance_result else 0,
            # Capability status KPIs (optional stages)
            'ecosystem_discovery_status': ctx.ecosystem_discovery_status,
            'ecosystem_discovery_error': ctx.ecosystem_discovery_error,
        },
        'purpose_field': ctx.purpose_field.summary() if ctx.purpose_field else {},
        'execution_flow': dict(exec_flow.summary(), **{
            'entry_points': exec_flow.entry_points,
            'orphans': exec_flow.orphans,
            'chains': [
                {
                    'entry_point': c.entry_point,
                    'path': c.path,
                    'length': c.length,
                    'layers_crossed': c.layers_crossed,
                    'has_violation': c.has_violation,
                }
                for c in (exec_flow.chains or [])[:50]  # cap at 50 to limit output size
            ],
            'integration_errors': [
                {
                    'type': e.type,
                    'source': e.source,
                    'target': e.target,
                    'message': e.message,
                }
                for e in (exec_flow.integration_errors or [])[:100]
            ],
        }) if exec_flow else {},
        'markov': markov,
        'knots': knots,
        'graph_analytics': ctx.graph_analytics or {},
        'statistical_metrics': ctx.statistical_metrics or {},
        'semantic_analysis': ctx.semantic_analysis or {},
        'data_flow': ctx.data_flow or {},
        'performance': ctx.perf_summary or {},
        'constraint_field': constraint_report if constraint_report else {},
        'top_hubs': [],
        'orphans_list': exec_flow.orphans[:20] if exec_flow else [],
        'orphan_integration': [],
        # Codome boundary visualization layer
        'codome_boundaries': {
            'boundary_nodes': codome_result.get('boundary_nodes', []),
            'inferred_edges': codome_result.get('inferred_edges', []),
            'summary': codome_result.get('summary', {}),
            'total_boundaries': codome_result.get('total_boundaries', 0),
            'total_inferred_edges': codome_result.get('total_inferred_edges', 0)
        },
        # API Drift Detection
        'api_drift': _assemble_api_drift(ctx),
        # Concordance Analysis (Stage 8.7)
        'concordance': ctx.concordance_result or {},
    }

    # Compute top hubs
    in_deg = Counter()
    for e in edges:
        in_deg[e.get('target', '')] += 1
    for node_id, deg in in_deg.most_common(10):
        name = node_id.split(':')[-1] if ':' in node_id else node_id.split('/')[-1]
        ctx.full_output['top_hubs'].append({'name': name, 'in_degree': deg})
    ctx.full_output['kpis']['top_hub_count'] = len(ctx.full_output['top_hubs'])

    # Include SmartIgnore discovery data in output
    if ctx.smartignore_manifest:
        from src.core.smart_ignore import SmartIgnore as _SI
        si_helper = _SI(str(ctx.target))
        ctx.full_output['smart_ignore'] = si_helper.manifest_to_dict(ctx.smartignore_manifest)

    # Include Contextome Intelligence in output
    if ctx.contextome_result is not None:
        ctx.full_output['contextome'] = ctx.contextome_result.to_dict()

    # ==========================================================================
    # FILE-CENTRIC VIEW: Hybrid atom/file navigation
    # ==========================================================================
    print("\n📁 Building file index...")
    with StageTimer(ctx.perf_manager, "File Index Building") as timer:
        files_index = _build_file_index(nodes, edges, str(ctx.target))
        file_boundaries = _build_file_boundaries(files_index)

        # Enrich file boundaries with comprehensive metadata
        try:
            enricher = FileEnricher(root_path=str(ctx.target), enable_git=False)
            file_boundaries = enricher.enrich_boundaries(file_boundaries)
            _log(f"   → File metadata enriched for {len(file_boundaries)} files", ctx.quiet)
        except Exception as e:
            print(f"   ⚠️ File enrichment failed: {e}")

        ctx.full_output['files'] = files_index
        ctx.full_output['file_boundaries'] = file_boundaries
        ctx.full_output['counts']['files_with_atoms'] = len(files_index)
        timer.set_output(files=len(files_index), atoms_mapped=sum(f['atom_count'] for f in file_boundaries))

    _log(f"   → {len(files_index)} files indexed", ctx.quiet)
    _log(f"   → {sum(f['atom_count'] for f in file_boundaries)} atoms mapped to files", ctx.quiet)
    ctx.data_ledger.publish("full_output", "_assemble_output",
        summary=f"{len(nodes)} nodes, {len(edges)} edges assembled")


def _assemble_api_drift(ctx) -> dict:
    """Serialize API drift results for the output dict."""
    drift = ctx.api_drift_report
    if drift is None:
        return {}
    try:
        result = drift.to_dict()
        result['summary'] = drift.summary()
        # Include endpoint catalog stats
        cat = ctx.endpoint_catalog
        if cat:
            result['endpoint_catalog'] = {
                'framework_detected': cat.framework_detected,
                'total_routes': cat.total_routes,
                'by_method': cat.by_method,
            }
        # Include consumer report stats
        rep = ctx.consumer_report
        if rep:
            result['consumer_report'] = {
                'total_calls': rep.total_calls,
                'unique_endpoints_called': rep.unique_endpoints_called,
                'by_method': rep.by_method,
            }
        return result
    except Exception:
        return {}


def _run_full_analysis(target_path: str, output_dir: str = None, options: Dict[str, Any] = None, *, _guard: _PipelineCrashGuard = None) -> Dict:
    """Internal implementation of run_full_analysis.

    Thin orchestrator that delegates to phase modules in src.core.phases.
    Each phase reads/writes a shared PipelineContext object.
    """
    from src.core.phases import (
        PipelineContext, run_discovery, run_extraction, run_enrichment,
        run_analysis, run_intelligence, run_synthesis, run_output,
    )

    if options is None:
        options = {}
    quiet = options.get("quiet", False)
    start_time = time.time()
    target = Path(target_path).resolve()
    resolved_output_dir = _resolve_output_dir(target, output_dir)

    # Ensure src.core is on the path (required by phase modules for bare imports)
    sys.path.insert(0, str(Path(__file__).parent))

    # Initialize observability
    verbose_timing = options.get("verbose_timing", False)
    from observability import PerformanceManager
    perf_manager = PerformanceManager(
        verbose=verbose_timing, json_log=options.get("json_log", False)
    )
    perf_manager.start_pipeline()

    # Set up crash guard
    if _guard is None:
        _guard = _PipelineCrashGuard()
    _guard.perf_manager = perf_manager
    _guard.start_time = start_time
    _guard.out_path = resolved_output_dir
    _guard.target = target

    _log("=" * 60, quiet)
    _log("COLLIDER FULL ANALYSIS", quiet)
    _log(f"Target: {target}", quiet)
    if options.get("timing", False) or verbose_timing:
        _log("Performance Tracking: ENABLED", quiet)
    _log("=" * 60, quiet)

    # Database initialization (Phase 30)
    db_manager = None
    delta_tracker = None
    if not options.get("no_db", False):
        try:
            from src.core.database import create_database_manager, DatabaseConfig
            from src.core.database.incremental import DeltaTracker
            db_config = DatabaseConfig.from_options(options, project_root=target)
            db_manager = create_database_manager(db_config, str(target))
            if db_manager:
                db_manager.connect()
                db_manager.initialize_schema()
                # Run pending schema migrations (e.g. v2 git context columns)
                from src.core.database.migrations.migrator import Migrator
                migrator = Migrator(db_manager)
                migrator.migrate()
                print(f"Database: {db_config.backend} @ {db_config.get_sqlite_path()}")
                if db_config.incremental_enabled:
                    delta_tracker = DeltaTracker(db_manager)
        except ImportError as e:
            print(f"   Database module not available: {e}")
        except Exception as e:
            print(f"   Database initialization failed: {e}")

    # Create pipeline context (shared mutable state for all phases)
    ctx = PipelineContext(
        target=target,
        output_dir=resolved_output_dir,
        options=options,
        quiet=quiet,
        batch_id=f"batch_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}",
        start_time=start_time,
        perf_manager=perf_manager,
        guard=_guard,
        db_manager=db_manager,
        delta_tracker=delta_tracker,
        refinery_signature=generate_refinery_signature(),
    )

    # ── Phase 1: Discovery ────────────────────────────────────────────
    # SmartIgnore, Survey, Contextome, Incremental Detection
    run_discovery(ctx)

    # ── Phase 2: Extraction ───────────────────────────────────────────
    # Base Analysis, Standard Model Enrichment, Ecosystem, Level, Dimension
    run_extraction(ctx)

    # ── Phase 3: Enrichment ───────────────────────────────────────────
    # Scope Analysis, Control Flow, Pattern Detection, Data Flow
    run_enrichment(ctx)

    # ── Phase 4: Analysis ─────────────────────────────────────────────
    # Purpose, Execution Flow, Markov, Knots, Graph Analytics, Semantic, Codome
    run_analysis(ctx)

    # ── Phase 5: Intelligence ─────────────────────────────────────────
    # Data Flow, Performance, Constraints, Purpose Intelligence
    run_intelligence(ctx)

    # ── Assemble output dict ──────────────────────────────────────────
    # Bridge: aggregates phase intermediates into canonical full_output
    _assemble_output(ctx)
    ctx.full_output['pipeline_flow'] = ctx.flow_tracker.to_dict()

    # ── Phase 6: Synthesis ────────────────────────────────────────────
    # Roadmap, Topology, Cortex, AI, Manifest, IGT, DB, Vector, Trinity,
    # Temporal, Ideome, Chemistry, Color Encoding (Stages 9-20+)
    run_synthesis(ctx)

    # ── Phase 7: Output ───────────────────────────────────────────────
    # Insights, Output Generation, Pipeline Report, Summary, Cleanup
    run_output(ctx)

    return ctx.full_output


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
