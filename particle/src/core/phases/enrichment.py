"""Phase 3: Enrichment — Scope Analysis, Control Flow, Pattern Detection, Data Flow."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    """Print progress message unless quiet mode is active."""
    if not quiet:
        print(msg)


def _run_scope_analysis(ctx: 'PipelineContext') -> None:
    """Stage 2.8: Scope Analysis (definitions, references, unused, shadowing)."""
    from observability import StageTimer
    from src.core.full_analysis import suppress_fd_stderr

    print("\n🔬 Stage 2.8: Scope Analysis...")
    with StageTimer(ctx.perf_manager, "Stage 2.8: Scope Analysis") as timer:
        try:
            from scope_analyzer import analyze_scopes, find_unused_definitions, find_shadowed_definitions

            py_parser = ctx.ts_cache.get_parser("python")
            js_parser = ctx.ts_cache.get_parser("javascript")

            scope_stats = {'files_analyzed': 0, 'unused': 0, 'shadowed': 0}

            _stage_warns = 0
            files_analyzed = set()
            for node in ctx.nodes:
                file_path = node.get('file_path', '')
                if file_path in files_analyzed:
                    continue
                files_analyzed.add(file_path)

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
                        tree = ctx.ts_cache.parse(body, lang)
                        graph = analyze_scopes(tree, bytes(body, 'utf8'), lang, file_path)
                    unused = find_unused_definitions(graph)
                    shadowed = find_shadowed_definitions(graph)

                    scope_stats['files_analyzed'] += 1
                    scope_stats['unused'] += len(unused)
                    scope_stats['shadowed'] += len(shadowed)

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
            _log(f"   → {scope_stats['files_analyzed']} files analyzed", ctx.quiet)
            _log(f"   → {scope_stats['unused']} unused definitions detected", ctx.quiet)
            _log(f"   → {scope_stats['shadowed']} shadowing pairs found", ctx.quiet)
            ctx.data_ledger.publish("scope_analysis", "Stage 2.8: Scope Analysis",
                summary=f"{scope_stats['files_analyzed']} files")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Scope analysis skipped: {e}")
            ctx.data_ledger.publish("scope_analysis", "Stage 2.8: Scope Analysis", status="skipped", summary=str(e))


def _run_control_flow(ctx: 'PipelineContext') -> None:
    """Stage 2.9: Control Flow Metrics (cyclomatic complexity, nesting depth)."""
    from observability import StageTimer

    print("\n📈 Stage 2.9: Control Flow Metrics...")
    with StageTimer(ctx.perf_manager, "Stage 2.9: Control Flow Metrics") as timer:
        try:
            from control_flow_analyzer import analyze_control_flow, get_complexity_rating, get_nesting_rating

            py_parser = ctx.ts_cache.get_parser("python")
            js_parser = ctx.ts_cache.get_parser("javascript")

            cf_stats = {'nodes_analyzed': 0, 'avg_cc': 0, 'max_cc': 0, 'avg_depth': 0, 'max_depth': 0}
            cc_sum, depth_sum = 0, 0

            _stage_warns = 0
            for node in ctx.nodes:
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
                    tree = ctx.ts_cache.parse(body, lang)
                    metrics = analyze_control_flow(tree, bytes(body, 'utf8'), lang)

                    cc = metrics['cyclomatic_complexity']
                    depth = metrics['max_nesting_depth']

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
            _log(f"   → {cf_stats['nodes_analyzed']} nodes analyzed", ctx.quiet)
            _log(f"   → Avg CC: {cf_stats['avg_cc']}, Max CC: {cf_stats['max_cc']}", ctx.quiet)
            _log(f"   → Avg Depth: {cf_stats['avg_depth']}, Max Depth: {cf_stats['max_depth']}", ctx.quiet)
            ctx.data_ledger.publish("control_flow", "Stage 2.9: Control Flow Metrics",
                summary=f"{cf_stats['nodes_analyzed']} nodes, avg_cc={cf_stats['avg_cc']}")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Control flow analysis skipped: {e}")
            ctx.data_ledger.publish("control_flow", "Stage 2.9: Control Flow Metrics", status="skipped", summary=str(e))


def _run_pattern_detection(ctx: 'PipelineContext') -> None:
    """Stage 2.10: Pattern-Based Atom Detection."""
    from observability import StageTimer

    print("\n🧬 Stage 2.10: Pattern-Based Atom Detection...")
    with StageTimer(ctx.perf_manager, "Stage 2.10: Pattern Detection") as timer:
        try:
            from pattern_matcher import PatternMatcher

            pattern_matcher = PatternMatcher()

            py_parser = ctx.ts_cache.get_parser("python")
            js_parser = ctx.ts_cache.get_parser("javascript")

            pattern_stats = {'nodes_enriched': 0, 'atoms_detected': 0, 'by_type': {}}

            _stage_warns = 0
            for node in ctx.nodes:
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
                    tree = ctx.ts_cache.parse(body, lang)
                    atoms = pattern_matcher.detect_atoms(tree, bytes(body, 'utf8'), lang)

                    if atoms:
                        node['detected_atoms'] = [
                            {
                                'type': a.type,
                                'name': a.name,
                                'confidence': a.confidence,
                                'evidence': a.evidence
                            }
                            for a in atoms
                        ]

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
            _log(f"   → {pattern_stats['nodes_enriched']} nodes enriched with atom patterns", ctx.quiet)
            _log(f"   → {pattern_stats['atoms_detected']} total atoms detected", ctx.quiet)
            if pattern_stats['by_type']:
                top_types = sorted(pattern_stats['by_type'].items(), key=lambda x: -x[1])[:5]
                _log(f"   → Top types: {', '.join(f'{t}:{c}' for t, c in top_types)}", ctx.quiet)
            ctx.data_ledger.publish("pattern_detection", "Stage 2.10: Pattern Detection",
                summary=f"{pattern_stats['atoms_detected']} atoms")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Pattern detection skipped: {e}")
            ctx.data_ledger.publish("pattern_detection", "Stage 2.10: Pattern Detection", status="skipped", summary=str(e))


def _run_data_flow_analysis(ctx: 'PipelineContext') -> None:
    """Stage 2.11: Data Flow Analysis (D6:EFFECT - Purity)."""
    from observability import StageTimer

    print("\n🌊 Stage 2.11: Data Flow Analysis (D6:EFFECT)...")
    with StageTimer(ctx.perf_manager, "Stage 2.11: Data Flow Analysis") as timer:
        try:
            from data_flow_analyzer import analyze_data_flow, get_data_flow_summary

            py_parser = ctx.ts_cache.get_parser("python")
            js_parser = ctx.ts_cache.get_parser("javascript")

            flow_stats = {
                'nodes_analyzed': 0,
                'total_assignments': 0,
                'total_mutations': 0,
                'total_side_effects': 0,
                'purity_distribution': {'pure': 0, 'mostly_pure': 0, 'mixed': 0, 'mostly_impure': 0, 'impure': 0}
            }

            _stage_warns = 0
            for node in ctx.nodes:
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
                    tree = ctx.ts_cache.parse(body, lang)
                    flow_graph = analyze_data_flow(tree, bytes(body, 'utf8'), lang, file_path)
                    summary = get_data_flow_summary(flow_graph)

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
            _log(f"   → {flow_stats['nodes_analyzed']} nodes analyzed for purity", ctx.quiet)
            _log(f"   → {flow_stats['total_mutations']} mutations, {flow_stats['total_side_effects']} side effects", ctx.quiet)
            purity_dist = flow_stats['purity_distribution']
            _log(f"   → Purity: pure={purity_dist['pure']}, mostly_pure={purity_dist['mostly_pure']}, mixed={purity_dist['mixed']}, impure={purity_dist['impure']}", ctx.quiet)
            ctx.data_ledger.publish("data_flow_enrichment", "Stage 2.11: Data Flow Analysis",
                summary=f"{flow_stats['nodes_analyzed']} nodes")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Data flow analysis skipped: {e}")
            ctx.data_ledger.publish("data_flow_enrichment", "Stage 2.11: Data Flow Analysis", status="skipped", summary=str(e))


def run_enrichment(ctx: 'PipelineContext') -> None:
    """Execute all enrichment sub-stages using shared tree-sitter cache."""
    # Initialize shared tree-sitter cache (avoids 4x re-parsing the same source)
    from src.core.tree_sitter_cache import TreeSitterCache as _TreeSitterCache
    ctx.ts_cache = _TreeSitterCache(max_size=500)

    _run_scope_analysis(ctx)
    _run_control_flow(ctx)
    _run_pattern_detection(ctx)
    _run_data_flow_analysis(ctx)
    ctx.flow_tracker.snapshot("After Phase 3: Enrichment", ctx.nodes, ctx.edges)
