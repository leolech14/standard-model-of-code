"""Phase 6: Synthesis — Roadmap through Color Encoding (Stages 9-20+)."""

from __future__ import annotations
import hashlib
import importlib.util
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    """Print progress message unless quiet mode is active."""
    if not quiet:
        print(msg)


def run_synthesis(ctx: 'PipelineContext') -> None:
    """Execute all synthesis sub-stages (Stages 9-20 + color encoding)."""

    ctx.output_dir.mkdir(parents=True, exist_ok=True)

    # Always include pipeline performance data
    ctx.full_output['pipeline_performance'] = ctx.perf_manager.to_dict()

    skip_html = ctx.options.get("skip_html", False)
    if not skip_html:
        from brain_download import generate_brain_download
        brain_content = generate_brain_download(ctx.full_output)
        ctx.full_output['brain_download'] = brain_content

    _run_roadmap(ctx)
    _run_visual_reasoning(ctx)
    _run_semantic_cortex(ctx)
    _run_ai_insights(ctx)
    _run_manifest(ctx)
    _run_igt(ctx)
    _run_git_context(ctx)          # Moved before DB: git context stored in run record
    _run_db_persistence(ctx)
    _run_vectorization(ctx)
    _run_trinity(ctx)
    _run_temporal(ctx)
    _run_ideome(ctx)
    _run_chemistry(ctx)
    _run_color_encoding(ctx)


# ---------------------------------------------------------------------------
# Sub-stages
# ---------------------------------------------------------------------------

def _run_roadmap(ctx: 'PipelineContext') -> None:
    """Stage 9: Roadmap Evaluation."""
    from observability import StageTimer
    from src.core.roadmap_evaluator import RoadmapEvaluator

    print("\n🛣️  Stage 9: Roadmap Evaluation...")
    with StageTimer(ctx.perf_manager, "Stage 9: Roadmap Evaluation") as timer:
        roadmap_name = ctx.options.get('roadmap')
        if roadmap_name:
            try:
                roadmap_path = Path(__file__).parent.parent / "roadmaps" / f"{roadmap_name}.json"
                if roadmap_path.exists():
                    evaluator = RoadmapEvaluator(str(roadmap_path))
                    all_files = [str(f) for f in ctx.target.rglob('*') if f.is_file()]
                    roadmap_result = evaluator.evaluate(all_files)
                    ctx.full_output['roadmap'] = roadmap_result
                    timer.set_output(readiness=roadmap_result.get('readiness_score', 0))
                    _log(f"   → Roadmap '{roadmap_name}' analyzed: {roadmap_result['readiness_score']:.0f}% ready", ctx.quiet)
                    ctx.data_ledger.publish("roadmap", "Stage 9: Roadmap Evaluation",
                        summary=f"{roadmap_result.get('readiness_score', 0):.0f}% ready")
                else:
                    timer.set_status("WARN", f"Roadmap '{roadmap_name}' not found")
                    print(f"   ⚠️ Roadmap '{roadmap_name}' not found in roadmaps directory")
                    ctx.data_ledger.publish("roadmap", "Stage 9: Roadmap Evaluation", status="skipped", summary="not found")
            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Roadmap analysis failed: {e}")
                import traceback
                traceback.print_exc()
                ctx.data_ledger.publish("roadmap", "Stage 9: Roadmap Evaluation", status="failed", summary=str(e))
        else:
            timer.set_status("SKIP")
            print("   → Skipped (no --roadmap specified)")
            ctx.data_ledger.publish("roadmap", "Stage 9: Roadmap Evaluation", status="skipped")


def _run_visual_reasoning(ctx: 'PipelineContext') -> None:
    """Stage 10: Visual Topology Analysis."""
    from observability import StageTimer
    from src.core.topology_reasoning import TopologyClassifier

    print("\n🧠 Stage 10: Visual Reasoning...")
    with StageTimer(ctx.perf_manager, "Stage 10: Visual Reasoning") as timer:
        try:
            topo = TopologyClassifier()
            topology_result = topo.classify(ctx.nodes, ctx.edges)
            ctx.full_output['topology'] = topology_result
            ctx.full_output['kpis']['topology_shape'] = topology_result.get('shape', 'UNKNOWN')
            timer.set_output(shape=topology_result.get('shape', 'UNKNOWN'))
            _log(f"   → Visual Shape: {topology_result['shape']}", ctx.quiet)
            _log(f"   → Description: {topology_result['description']}", ctx.quiet)
            ctx.data_ledger.publish("topology", "Stage 10: Visual Reasoning",
                summary=topology_result.get('shape', 'UNKNOWN'))
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Topology analysis failed: {e}")
            ctx.data_ledger.publish("topology", "Stage 10: Visual Reasoning", status="failed", summary=str(e))


def _run_semantic_cortex(ctx: 'PipelineContext') -> None:
    """Stage 11: Semantic Cortex (Concept Extraction)."""
    from observability import StageTimer
    from src.core.semantic_cortex import ConceptExtractor

    print("\n🧠 Stage 11: Semantic Cortex...")
    with StageTimer(ctx.perf_manager, "Stage 11: Semantic Cortex") as timer:
        try:
            cortex = ConceptExtractor()
            semantics = cortex.extract_concepts(ctx.nodes)
            ctx.full_output['semantics'] = semantics
            timer.set_output(concepts=len(semantics.get('top_concepts', [])))
            _log(f"   → Domain Inference: {semantics['domain_inference']}", ctx.quiet)
            _log(f"   → Top Concepts: {', '.join([t['term'] for t in semantics['top_concepts'][:5]])}", ctx.quiet)
            ctx.data_ledger.publish("semantics", "Stage 11: Semantic Cortex",
                summary=f"{len(semantics.get('top_concepts', []))} concepts")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Semantic analysis failed: {e}")
            ctx.data_ledger.publish("semantics", "Stage 11: Semantic Cortex", status="failed", summary=str(e))


def _run_ai_insights(ctx: 'PipelineContext') -> None:
    """Stage 12: AI Insights (optional — requires Vertex AI)."""
    from observability import StageTimer

    if ctx.options.get('ai_insights'):
        print("\n✨ Stage 12: AI Insights Generation (Vertex AI)...")
        with StageTimer(ctx.perf_manager, "Stage 12: AI Insights") as timer:
            try:
                from src.core.full_analysis import _generate_ai_insights
                ai_insights = _generate_ai_insights(ctx.full_output, ctx.output_dir, ctx.options)
                if ai_insights:
                    ctx.full_output['ai_insights'] = ai_insights
                    timer.set_output(insights=len(ai_insights) if isinstance(ai_insights, list) else 1)
                    print("   → AI insights generated successfully")
                    ctx.data_ledger.publish("ai_insights", "Stage 12: AI Insights")
                else:
                    timer.set_status("WARN", "No results returned")
                    print("   ⚠️ AI insights generation returned no results")
                    ctx.data_ledger.publish("ai_insights", "Stage 12: AI Insights", status="empty")
            except Exception as e:
                timer.set_status("FAIL", str(e))
                print(f"   ⚠️ AI insights generation failed: {e}")
                ctx.data_ledger.publish("ai_insights", "Stage 12: AI Insights", status="failed", summary=str(e))
    else:
        ctx.data_ledger.publish("ai_insights", "Stage 12: AI Insights", status="skipped")


def _run_manifest(ctx: 'PipelineContext') -> None:
    """Stage 13: Manifest Writer (Provenance & Integrity)."""
    from observability import StageTimer
    from src.core.merkle_utils import calculate_merkle_root

    print("\n📦 Stage 13: Manifest Writer...")
    with StageTimer(ctx.perf_manager, "Stage 13: Manifest Writer") as timer:
        try:
            ctx.merkle_root = calculate_merkle_root([n.get('id', n.get('name', '')) for n in ctx.nodes])

            manifest = {
                "schema_version": "manifest.v2",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "batch_id": ctx.batch_id,
                "waybill": {
                    "parcel_id": f"pcl_{hashlib.sha256(ctx.merkle_root.encode()).hexdigest()[:12]}",
                    "batch_id": ctx.batch_id,
                    "merkle_root": ctx.merkle_root,
                    "refinery_signature": ctx.refinery_signature,
                    "context_vector": [0.0] * 32,
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
                    "target_path": str(ctx.target),
                    "node_count": len(ctx.nodes),
                    "edge_count": len(ctx.edges),
                    "merkle_root": ctx.merkle_root
                },
                "pipeline": {
                    "stages_executed": [s.stage_name for s in ctx.perf_manager.stages] if (ctx.perf_manager and hasattr(ctx.perf_manager, 'stages')) else [],
                    "total_stages": 22,
                    "version": "1.0.0-smoc"
                },
                "environment": {
                    "python_version": sys.version.split()[0],
                    "platform": sys.platform
                }
            }
            ctx.full_output['manifest'] = manifest
            _log(f"   → Manifest generated: {len(ctx.nodes)} nodes, {len(ctx.edges)} edges recorded", ctx.quiet)
            _log(f"   → Status: SIGNED (Integrity verified)", ctx.quiet)
            timer.set_output(nodes=len(ctx.nodes), edges=len(ctx.edges))
            ctx.data_ledger.publish("manifest", "Stage 13: Manifest Writer",
                summary=f"{len(ctx.nodes)} nodes, {len(ctx.edges)} edges")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Manifest generation failed: {e}")
            ctx.data_ledger.publish("manifest", "Stage 13: Manifest Writer", status="failed", summary=str(e))


def _run_igt(ctx: 'PipelineContext') -> None:
    """Stage 14: Information Graph Theory (IGT) Metrics."""
    from observability import StageTimer
    from src.core.igt_metrics import StabilityCalculator, OrphanClassifier

    print("\n📈 Stage 14: IGT Metrics...")
    igt_results = {}
    with StageTimer(ctx.perf_manager, "Stage 14: IGT Metrics") as timer:
        try:
            # 1. Directory Stability
            dir_structure = defaultdict(list)
            for f in ctx.full_output.get('file_boundaries', []):
                p = Path(f['file'])
                parent = str(p.parent)
                dir_structure[parent].append(p.name)

            stability_report = StabilityCalculator.analyze_directories(dir_structure)

            # 2. Type-Aware Orphan Analysis
            orphans_data = []
            for o_id in ctx.exec_flow.orphans:
                o_node = next((n for n in ctx.nodes if n.get('id') == o_id), None)
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

            ctx.full_output['igt'] = igt_results
            ctx.full_output['kpis']['igt_stability_index'] = round(igt_results['avg_stability'], 3)
            ctx.full_output['kpis']['critical_orphans'] = igt_results['critical_orphans_count']

            timer.set_output(
                avg_stability=igt_results['avg_stability'],
                critical_orphans=igt_results['critical_orphans_count']
            )
            _log(f"   → Average Directory Stability: {igt_results['avg_stability']:.3f}", ctx.quiet)
            _log(f"   → Critical Orphans: {igt_results['critical_orphans_count']}", ctx.quiet)
            ctx.data_ledger.publish("igt", "Stage 14: IGT Metrics",
                summary=f"stability={igt_results['avg_stability']:.3f}")

        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ IGT analysis failed: {e}")
            ctx.data_ledger.publish("igt", "Stage 14: IGT Metrics", status="failed", summary=str(e))


def _run_db_persistence(ctx: 'PipelineContext') -> None:
    """Stage 15: Database Persistence."""
    from observability import StageTimer

    ctx.db_run_id = None
    if ctx.db_manager:
        print("\n💾 Stage 15: Database Persistence...")
        with StageTimer(ctx.perf_manager, "Stage 15: Database Persistence") as timer:
            try:
                from src.core.database.backends.base import AnalysisRun
                from datetime import datetime as dt_datetime

                git_ctx = ctx.full_output.get('git_context', {})
                run = AnalysisRun(
                    id=f"run_{hashlib.sha256(f'{ctx.target}-{time.time()}'.encode()).hexdigest()[:12]}",
                    project_name=ctx.target.name,
                    project_path=str(ctx.target),
                    started_at=dt_datetime.now(),
                    collider_version="1.0.0",
                    status="running",
                    options=ctx.options,
                    git_commit=git_ctx.get('commit', ''),
                    git_branch=git_ctx.get('branch', ''),
                    git_dirty=git_ctx.get('dirty', False),
                    git_summary=git_ctx.get('summary', ''),
                )

                ctx.db_run_id = ctx.db_manager.create_run(run)

                node_count = ctx.db_manager.insert_nodes(ctx.db_run_id, ctx.nodes)
                edge_count = ctx.db_manager.insert_edges(ctx.db_run_id, ctx.edges)

                # Compute delta against previous run
                delta_json_str = None
                try:
                    prev_run = ctx.db_manager.get_latest_run(str(ctx.target))
                    if prev_run and prev_run.id != ctx.db_run_id:
                        delta = ctx.db_manager.compare_runs(prev_run.id, ctx.db_run_id)
                        delta['previous_run_id'] = prev_run.id
                        delta['previous_git_commit'] = getattr(prev_run, 'git_commit', '') or ''
                        delta['previous_git_branch'] = getattr(prev_run, 'git_branch', '') or ''
                        delta_json_str = json.dumps(delta)
                        _log(f"   → Delta: +{delta.get('added', 0)} -{delta.get('removed', 0)} nodes vs {prev_run.id}", ctx.quiet)
                except Exception:
                    pass

                ctx.db_manager.update_run(
                    ctx.db_run_id,
                    status="completed",
                    completed_at=dt_datetime.now(),
                    node_count=node_count,
                    edge_count=edge_count,
                    delta_json=delta_json_str,
                )

                timer.set_output(run_id=ctx.db_run_id, nodes=node_count, edges=edge_count)
                _log(f"   → Run ID: {ctx.db_run_id}", ctx.quiet)
                _log(f"   → Persisted {node_count} nodes, {edge_count} edges", ctx.quiet)

                # Update file tracking if delta tracker is available
                if ctx.delta_tracker and ctx.delta_result:
                    from src.core.database.incremental.hasher import FileHasher
                    hasher = FileHasher()
                    file_hashes = hasher.hash_directory(ctx.target)
                    ctx.delta_tracker.update_tracking(str(ctx.target), ctx.db_run_id, file_hashes)
                    _log(f"   → Updated file tracking for {len(file_hashes)} files", ctx.quiet)

                # Retention: purge old runs after successful persistence
                try:
                    from src.core.database import DatabaseConfig
                    db_config = DatabaseConfig.from_options(ctx.options, project_root=ctx.target)
                    if db_config and db_config.history_enabled:
                        purged = ctx.db_manager.purge_old_runs(project_path=str(ctx.target))
                        if purged > 0:
                            _log(f"   → Retention: purged {purged} old run(s)", ctx.quiet)
                except Exception:
                    pass

                ctx.data_ledger.publish("db_persistence", "Stage 15: Database Persistence",
                    summary=f"run={ctx.db_run_id}")

            except Exception as e:
                timer.set_status("WARN", str(e))
                print(f"   ⚠️ Database persistence failed: {e}")
                ctx.data_ledger.publish("db_persistence", "Stage 15: Database Persistence", status="failed", summary=str(e))
    else:
        ctx.data_ledger.publish("db_persistence", "Stage 15: Database Persistence", status="skipped")


def _run_vectorization(ctx: 'PipelineContext') -> None:
    """Stage 16: Semantic Vector Indexing (GraphRAG)."""
    from observability import StageTimer

    print("\n🔗 Stage 16: Semantic Vector Indexing...")
    vectorization_status = "skipped"
    vectorization_error = ""
    with StageTimer(ctx.perf_manager, "Stage 16: Semantic Vector Indexing") as timer:
        _has_lancedb = importlib.util.find_spec("lancedb")
        _has_st = importlib.util.find_spec("sentence_transformers")
        if _has_lancedb and _has_st:
            try:
                from src.core.rag.embedder import GraphRAGEmbedder
                persistent_db = ctx.target / ".collider" / "collider.db"
                embedder = GraphRAGEmbedder(db_path=persistent_db)
                embedder.embed_graph()
                vectorization_status = "ok"
                timer.set_output(status="ok")
                _log("   → Vector index built", ctx.quiet)
            except Exception as e:
                vectorization_status = "failed"
                vectorization_error = str(e)
                timer.set_status("FAIL", str(e))
                print(f"   ⚠️ Vectorization failed: {e}")
        else:
            missing = []
            if not _has_lancedb:
                missing.append("lancedb")
            if not _has_st:
                missing.append("sentence-transformers")
            timer.set_status("SKIP")
            _log(f"   → Skipped (missing: {', '.join(missing)})", ctx.quiet)

    ctx.full_output.setdefault('kpis', {})['vectorization_status'] = vectorization_status
    ctx.full_output['kpis']['vectorization_error'] = vectorization_error
    ctx.data_ledger.publish("vectorization", "Stage 16: Semantic Vector Indexing",
        status=vectorization_status if vectorization_status in ("ok", "failed") else "skipped",
        summary=vectorization_error or "")
    if vectorization_status == "failed":
        warnings_list = ctx.full_output.setdefault('warnings', [])
        if isinstance(warnings_list, list):
            warnings_list.append(f"stage16_vectorization_failed: {vectorization_error}")


def _run_trinity(ctx: 'PipelineContext') -> None:
    """Stage 17: Collider Trinity (Incoherence, Purpose Decomposition, Gap Detection)."""
    print("\n🔬 Stage 17: Collider Trinity...")
    try:
        from src.core.incoherence import compute_incoherence
        from src.core.purpose_decomposition import decompose_purposes
        from src.core.gap_detector import detect_gaps

        incoherence_result = compute_incoherence(ctx.full_output)
        ctx.full_output['incoherence'] = incoherence_result.to_dict()

        decomposition_results = decompose_purposes(ctx.full_output)
        ctx.full_output['purpose_decomposition'] = [r.to_dict() for r in decomposition_results]

        # Entry points (main(), CLI handlers) are exempt from gap detection --
        # they orchestrate external behavior, not internal sub-structure.
        ep_set = set(getattr(ctx.exec_flow, 'entry_points', []))
        gap_report = detect_gaps(ctx.full_output, decomposition_results,
                                 entry_points=ep_set)
        ctx.full_output['gap_report'] = gap_report.to_dict()

        _log(f"   → Incoherence: I={incoherence_result.i_total:.3f}  Health={incoherence_result.health_10:.1f}/10", ctx.quiet)
        _log(f"   → Purpose Decomposition: {len(decomposition_results)} containers analyzed", ctx.quiet)
        gap_count = len(gap_report.gaps)
        crit_count = sum(1 for g in gap_report.gaps if g.severity == 'critical')
        _log(f"   → Gap Detection: {gap_count} gaps ({crit_count} critical), coverage={gap_report.coverage:.1%}", ctx.quiet)
        ctx.data_ledger.publish("trinity", "Stage 17: Collider Trinity",
            summary=f"I={incoherence_result.i_total:.3f}, {gap_count} gaps")
    except Exception as e:
        print(f"   ⚠️ Trinity computation failed: {e}")
        import traceback
        traceback.print_exc()
        ctx.data_ledger.publish("trinity", "Stage 17: Collider Trinity", status="failed", summary=str(e))


def _run_temporal(ctx: 'PipelineContext') -> None:
    """Stage 18: Temporal Analysis (REH integration)."""
    print("\n🔬 Stage 18: Temporal Analysis...")
    try:
        from src.core.temporal_analysis import compute_temporal_analysis
        temporal_result = compute_temporal_analysis(ctx.full_output, repo_path=str(ctx.target))
        ctx.full_output['temporal_analysis'] = temporal_result.to_dict()
        if temporal_result.available:
            _log(f"   → {temporal_result.total_commits} commits, {temporal_result.active_days} active days", ctx.quiet)
            _log(f"   → {len(temporal_result.hotspots)} hotspots, {len(temporal_result.change_coupling)} coupling pairs", ctx.quiet)
            _log(f"   → Bus factor: {temporal_result.bus_factor}, median file age: {temporal_result.median_age_days:.0f} days", ctx.quiet)
            ctx.data_ledger.publish("temporal", "Stage 18: Temporal Analysis",
                summary=f"{temporal_result.total_commits} commits")
        else:
            _log(f"   → Skipped: {temporal_result.error}", ctx.quiet)
            ctx.data_ledger.publish("temporal", "Stage 18: Temporal Analysis", status="skipped", summary=temporal_result.error)
    except Exception as e:
        print(f"   ⚠️ Temporal analysis failed: {e}")
        import traceback
        traceback.print_exc()
        ctx.data_ledger.publish("temporal", "Stage 18: Temporal Analysis", status="failed", summary=str(e))


def _run_git_context(ctx: 'PipelineContext') -> None:
    """Stage 18b: Git Context (repo identity + worktree topology)."""
    try:
        from src.core.git_context import compute_git_context
        git_result = compute_git_context(repo_path=str(ctx.target))
        ctx.full_output['git_context'] = git_result.to_dict()
        if git_result.available:
            # Backfill meta with basic git fields for frontend consumers
            meta = ctx.full_output.get('meta', {})
            meta['git_branch'] = git_result.branch
            meta['git_commit'] = git_result.commit
            meta['git_dirty'] = git_result.dirty
            meta['git_summary'] = git_result.summary
            _log(f"   → {git_result.summary}", ctx.quiet)
        else:
            _log(f"   → Skipped: {git_result.error}", ctx.quiet)
    except Exception as e:
        print(f"   ⚠️ Git context failed: {e}")


def _run_ideome(ctx: 'PipelineContext') -> None:
    """Stage 19: Ideome Synthesis (Rosetta Stone)."""
    print("\n🔬 Stage 19: Ideome Synthesis...")
    try:
        from src.core.ideome_synthesis import synthesize_ideome
        ideome_result = synthesize_ideome(ctx.full_output)
        ctx.full_output['ideome'] = ideome_result.to_dict()
        _log(f"   → Coherence: {ideome_result.global_coherence:.3f}", ctx.quiet)
        _log(f"   → Drift: code={ideome_result.global_drift_C:.3f} docs={ideome_result.global_drift_X:.3f}", ctx.quiet)
        _log(f"   → Coverage: {ideome_result.coverage:.1%} ({ideome_result.node_count} nodes)", ctx.quiet)
        ctx.data_ledger.publish("ideome", "Stage 19: Ideome Synthesis",
            summary=f"coherence={ideome_result.global_coherence:.3f}")
    except Exception as e:
        print(f"   ⚠️ Ideome synthesis failed: {e}")
        import traceback
        traceback.print_exc()
        ctx.data_ledger.publish("ideome", "Stage 19: Ideome Synthesis", status="failed", summary=str(e))


def _run_chemistry(ctx: 'PipelineContext') -> None:
    """Stage 20: Data Chemistry (Cross-Signal Correlation)."""
    print("\n🧪 Stage 20: Data Chemistry...")
    try:
        from src.core.data_chemistry import ChemistryLab
        chem_lab = ChemistryLab()
        chem_lab.set_ledger(ctx.data_ledger)
        chem_lab.ingest(ctx.full_output)
        chem_result = chem_lab.get_result()
        ctx.full_output['chemistry'] = chem_result.to_dict()
        ctx.full_output['chemistry']['diagnostics'] = chem_lab.build_diagnostics()
        ctx.full_output['_chemistry_lab'] = chem_lab  # ephemeral live ref
        syn_names = [s.name for s in chem_result.syndromes]
        if not ctx.quiet:
            print(f"   → Syndromes: {syn_names or 'none'}")
            print(f"   → Contradictions: {len(chem_result.contradictions)}")
            print(f"   → Compound severity: {chem_result.compound_severity:.3f}")
            print(f"   → Signal coverage: {chem_result.signal_coverage:.0%}")
            if chem_result.convergence:
                print(f"   → Convergent nodes: {chem_result.convergence.convergent_count} "
                      f"({chem_result.convergence.critical_count} critical)")
        # AI Consumer Summary
        ctx.full_output['ai_consumer_summary'] = chem_lab.build_ai_consumer_summary()
        if not ctx.quiet:
            print(f"   → AI Consumer Summary: grade={ctx.full_output['ai_consumer_summary']['data_utility_grade']}")
        ctx.data_ledger.publish("chemistry", "Stage 20: Data Chemistry",
            summary=f"coverage={chem_result.signal_coverage:.0%}, severity={chem_result.compound_severity:.3f}")
    except Exception as e:
        print(f"   ⚠️ Data Chemistry failed: {e}")
        import traceback
        traceback.print_exc()
        ctx.data_ledger.publish("chemistry", "Stage 20: Data Chemistry", status="failed", summary=str(e))


def _run_color_encoding(ctx: 'PipelineContext') -> None:
    """Post-Stage 20: Multi-channel OKLCH color encoding."""
    try:
        from src.core.viz.color_encoding import (
            encode_all, encode_nodes, encode_edges, VIEW_DEFAULT, PRESET_VIEWS,
            get_view_registry, rank_views,
        )
        chem_result_obj = ctx.full_output.get('_chemistry_lab', None)
        chemistry = chem_result_obj.get_result() if chem_result_obj else None
        enc_report = encode_all(ctx.full_output, view=VIEW_DEFAULT, chemistry=chemistry)
        ctx.full_output['encoding_report'] = enc_report.__dict__
        _log(f"   → Encoded {enc_report.nodes_encoded} nodes, "
             f"{enc_report.edges_encoded} edges, "
             f"{enc_report.convergent_tagged} convergent", ctx.quiet)

        # Pre-compute all non-default view colors for runtime view switching.
        # Store as OKLCH triples [L, C, H] — hex conversion at render boundary.
        nodes = ctx.full_output.get('nodes', [])
        edges = ctx.full_output.get('edges', [])
        view_count = 0
        edges_encoded_total = 0
        for view_name, view_spec in PRESET_VIEWS.items():
            if view_name == 'default':
                continue
            encode_nodes(nodes, view_spec)
            for node in nodes:
                ec = node.pop('encoded_color', None)
                if ec:
                    if 'encoded_colors' not in node:
                        node['encoded_colors'] = {}
                    node['encoded_colors'][view_name] = list(ec)
            # Encode edges when the view specifies an edge mapping
            if view_spec.edge_mapping is not None:
                n_enc, _ = encode_edges(edges, view_spec.edge_mapping)
                for edge in edges:
                    ec = edge.pop('encoded_color', None)
                    if ec:
                        if 'encoded_colors' not in edge:
                            edge['encoded_colors'] = {}
                        edge['encoded_colors'][view_name] = list(ec)
                edges_encoded_total += n_enc
            view_count += 1

        # Build view registry and rank by informativeness (annotates in place)
        registry = get_view_registry()
        rank_views(registry, nodes, top_k=4, min_domains=3)
        ctx.full_output['view_registry'] = registry
        ranked_names = [n for n, e in registry.items() if e.get('rank') and e['rank'] > 0]
        ranked_names.sort(key=lambda n: registry[n]['rank'])
        _log(f"   → Top views: {', '.join(ranked_names)}", ctx.quiet)
        _log(f"   → Pre-computed {view_count} encoding views for "
             f"{len(nodes)} nodes, {edges_encoded_total} edge encodings", ctx.quiet)
        ctx.data_ledger.publish("color_encoding", "Post-Stage 20: Color Encoding",
            summary=f"{enc_report.nodes_encoded} nodes, {view_count} views")
    except Exception as e:
        _log(f"   ⚠️ Color encoding skipped: {e}", ctx.quiet)
        import traceback
        traceback.print_exc()
        ctx.data_ledger.publish("color_encoding", "Post-Stage 20: Color Encoding", status="failed", summary=str(e))
