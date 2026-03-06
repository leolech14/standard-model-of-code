"""Phase 4: Analysis — Purpose, Execution Flow, Markov, Knots, Graph, Semantic, Codome."""

from __future__ import annotations
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._context import PipelineContext


def _log(msg: str, quiet: bool = False):
    """Log message if not quiet."""
    if not quiet:
        print(msg)


def run_analysis(ctx: PipelineContext) -> None:
    """Execute all analysis sub-stages.

    Stages:
    - 3: Purpose Field detection
    - 3.5: π₃ (Organelle Purpose) for containers
    - 3.6: π₄ (System Purpose) for files
    - 3.7: Purpose Coherence metrics
    - 4: Execution Flow detection
    - 5: Markov Transition Matrix
    - 6: Knot/Cycle Detection
    - 6.5: Graph Analytics (degrees, centrality, topology roles)
    - 6.6: Statistical Metrics (entropy, complexity, Halstead)
    - 6.7: Semantic Purpose Analysis (entry points, context propagation, critical nodes)
    - 6.8: Codome Boundary Generation
    """
    _run_purpose_field(ctx)      # Stage 3
    _run_organelle_purpose(ctx)  # Stage 3.5
    _run_system_purpose(ctx)     # Stage 3.6
    _run_coherence(ctx)          # Stage 3.7
    _run_execution_flow(ctx)     # Stage 4
    _run_markov(ctx)             # Stage 5
    _run_knots(ctx)              # Stage 6
    _run_graph_analytics(ctx)    # Stage 6.5
    _run_statistical(ctx)        # Stage 6.6
    _run_semantic(ctx)           # Stage 6.7
    _run_codome(ctx)             # Stage 6.8
    _run_api_drift(ctx)          # Stage 6.9
    ctx.flow_tracker.snapshot("After Phase 4: Analysis", ctx.nodes, ctx.edges)


def _run_purpose_field(ctx: PipelineContext) -> None:
    """Stage 3: Purpose Field detection."""
    from src.core.purpose_field import detect_purpose_field
    from observability import StageTimer

    print("\n🎯 Stage 3: Purpose Field...")
    with StageTimer(ctx.perf_manager, "Stage 3: Purpose Field") as timer:
        ctx.purpose_field = detect_purpose_field(ctx.nodes, ctx.edges)
        timer.set_output(nodes=len(ctx.purpose_field.nodes), violations=len(ctx.purpose_field.violations))
    _log(f"   → {len(ctx.purpose_field.nodes)} purpose nodes", ctx.quiet)
    _log(f"   → {len(ctx.purpose_field.violations)} violations", ctx.quiet)
    ctx.data_ledger.publish("purpose_field", "Stage 3: Purpose Field",
        summary=f"{len(ctx.purpose_field.nodes)} nodes, {len(ctx.purpose_field.violations)} violations")


def _run_organelle_purpose(ctx: PipelineContext) -> None:
    """Stage 3.5: π₃ (Organelle Purpose) for containers."""
    from src.core.purpose_emergence import compute_pi3

    print("\n🧬 Stage 3.5: Organelle Purpose (π₃)...")
    pi3_count = 0
    # Build parent-child index from names (Class.method pattern).
    # Key by (file_path, parent_name) to prevent bare-name collisions
    # (e.g., 46 different main() functions across files).
    children_by_parent = {}
    for node in ctx.nodes:
        name = node.get('name', '')
        if '.' in name:
            parent_name = name.rsplit('.', 1)[0]
            file_path = node.get('file_path', '')
            key = (file_path, parent_name)
            if key not in children_by_parent:
                children_by_parent[key] = []
            children_by_parent[key].append(node)

    # Compute π₃ for containers
    for node in ctx.nodes:
        name = node.get('name', '')
        file_path = node.get('file_path', '')
        key = (file_path, name)
        if key in children_by_parent and len(children_by_parent[key]) > 0:
            children = children_by_parent[key]
            pi3 = compute_pi3(node, children)
            node['pi3_purpose'] = pi3.purpose
            node['pi3_confidence'] = round(pi3.confidence, 2)
            node['pi3_child_count'] = len(children)
            pi3_count += 1
    _log(f"   → {pi3_count} containers with π₃ purpose", ctx.quiet)
    ctx.data_ledger.publish("organelle_purpose", "Stage 3.5: Organelle Purpose",
        summary=f"{pi3_count} containers")


def _run_system_purpose(ctx: PipelineContext) -> None:
    """Stage 3.6: π₄ (System Purpose) for files."""
    from src.core.purpose_emergence import compute_pi4

    print("\n📦 Stage 3.6: System Purpose (π₄)...")
    # Group nodes by file
    nodes_by_file = {}
    for node in ctx.nodes:
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

    ctx.file_purposes = file_purposes
    _log(f"   → {len(file_purposes)} files with π₄ purpose", ctx.quiet)
    ctx.data_ledger.publish("system_purpose", "Stage 3.6: System Purpose",
        summary=f"{len(file_purposes)} files")


def _run_coherence(ctx: PipelineContext) -> None:
    """Stage 3.7: Purpose Coherence metrics from PurposeField."""
    print("\n🎯 Stage 3.7: Purpose Coherence Metrics...")
    coherence_enriched = 0
    # Build lookup: ID-first (reliable), name-fallback (for legacy compat)
    pf_by_id = {pn.id: pn for pn in ctx.purpose_field.nodes.values()}
    pf_by_name = {pn.name: pn for pn in ctx.purpose_field.nodes.values()}
    for node in ctx.nodes:
        node_id = node.get('id', '')
        name = node.get('name', '')
        pf_node = pf_by_id.get(node_id) or pf_by_name.get(name)
        if pf_node:
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
    _log(f"   → {coherence_enriched} nodes enriched with coherence metrics", ctx.quiet)
    # Count god classes
    god_class_count = sum(1 for n in ctx.nodes if n.get('is_god_class', False))
    if god_class_count > 0:
        print(f"   ⚠️  {god_class_count} god classes detected")
    ctx.data_ledger.publish("coherence", "Stage 3.7: Purpose Coherence",
        summary=f"{coherence_enriched} enriched, {god_class_count} god classes")


def _run_execution_flow(ctx: PipelineContext) -> None:
    """Stage 4: Execution Flow detection."""
    from src.core.execution_flow import detect_execution_flow
    from observability import StageTimer

    print("\n⚡ Stage 4: Execution Flow...")
    with StageTimer(ctx.perf_manager, "Stage 4: Execution Flow") as timer:
        ctx.exec_flow = detect_execution_flow(ctx.nodes, ctx.edges, ctx.purpose_field)
        timer.set_output(entry_points=len(ctx.exec_flow.entry_points), orphans=len(ctx.exec_flow.orphans))
    _log(f"   → {len(ctx.exec_flow.entry_points)} entry points", ctx.quiet)
    _log(f"   → {len(ctx.exec_flow.orphans)} orphans ({ctx.exec_flow.dead_code_percent}% dead code)", ctx.quiet)

    ctx.data_ledger.publish("execution_flow", "Stage 4: Execution Flow",
        summary=f"{len(ctx.exec_flow.entry_points)} entries, {len(ctx.exec_flow.orphans)} orphans")

    # Stage 4.5: Orphan Integration Analysis (REMOVED - Module Deleted)
    # orphan_integration was removed in remediation pass.
    ctx.orphan_analysis = []


def _run_markov(ctx: PipelineContext) -> None:
    """Stage 5: Markov Transition Matrix."""
    from src.core.topology_analysis import compute_markov_matrix
    from observability import StageTimer

    print("\n📊 Stage 5: Markov Transition Matrix...")
    with StageTimer(ctx.perf_manager, "Stage 5: Markov Transition Matrix") as timer:
        ctx.markov = compute_markov_matrix(ctx.nodes, ctx.edges)
        timer.set_output(transitions=ctx.markov['total_transitions'], edges_weighted=ctx.markov['edges_with_weight'])
    _log(f"   → {ctx.markov['total_transitions']} nodes with transitions", ctx.quiet)
    _log(f"   → {ctx.markov['edges_with_weight']} edges with markov_weight", ctx.quiet)
    _log(f"   → {ctx.markov['avg_fanout']:.1f} avg fanout", ctx.quiet)
    ctx.data_ledger.publish("markov", "Stage 5: Markov Transition Matrix",
        summary=f"{ctx.markov['total_transitions']} transitions")


def _run_knots(ctx: PipelineContext) -> None:
    """Stage 6: Knot/Cycle Detection."""
    from src.core.topology_analysis import detect_knots
    from observability import StageTimer

    print("\n🔗 Stage 6: Knot/Cycle Detection...")
    with StageTimer(ctx.perf_manager, "Stage 6: Knot/Cycle Detection") as timer:
        ctx.knots = detect_knots(ctx.nodes, ctx.edges)
        timer.set_output(cycles=ctx.knots['cycles_detected'], bidirectional=ctx.knots['bidirectional_edges'])
    _log(f"   → {ctx.knots['cycles_detected']} cycles detected", ctx.quiet)
    _log(f"   → {ctx.knots['bidirectional_edges']} bidirectional edges", ctx.quiet)
    _log(f"   → Knot score: {ctx.knots['knot_score']}/10", ctx.quiet)
    ctx.data_ledger.publish("knots", "Stage 6: Knot/Cycle Detection",
        summary=f"{ctx.knots['cycles_detected']} cycles, score={ctx.knots['knot_score']}")


def _run_graph_analytics(ctx: PipelineContext) -> None:
    """Stage 6.5: Graph Analytics (degrees, centrality, topology roles, π₂)."""
    from src.core.graph_framework import build_nx_graph, classify_node_role
    from src.core.disconnection_classifier import classify_disconnection
    from src.core.purpose_emergence import compute_pi2
    from observability import StageTimer

    # _G_full carries ALL edge types for Stage 6.7 (entry points, context propagation,
    # closeness centrality). Building it here avoids a second build_nx_graph() call.
    ctx.nx_graph_full = None  # Will be set inside try block; used by Stage 6.7

    print("\n🧮 Stage 6.5: Graph Analytics...")
    with StageTimer(ctx.perf_manager, "Stage 6.5: Graph Analytics") as timer:
        # Degree computation (always runs - needed for Control Bar mappings)
        try:
            import networkx as nx
            G = nx.DiGraph()
            for node in ctx.nodes:
                G.add_node(node.get('id', ''), **{k: v for k, v in node.items() if k != 'body_source'})
            # Only count behavioral edges (calls, invokes) for topology classification
            # Structural edges (contains, inherits) would give false in_degree to all nested nodes
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in ctx.edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src and tgt:
                        G.add_edge(src, tgt)

            # Also build full graph (all edge types) for Stage 6.7 re-use.
            # This is built once here so Stage 6.7 does not have to rebuild it.
            ctx.nx_graph_full = build_nx_graph(ctx.nodes, ctx.edges)

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
            _closeness = nx.closeness_centrality(ctx.nx_graph_full) if len(ctx.nx_graph_full) > 0 else {}

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_degree_map.get(n.get('id', ''), 0) + out_degree_map.get(n.get('id', ''), 0) for n in ctx.nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            for node in ctx.nodes:
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
            for node in ctx.nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            _log(f"   → {degree_enriched} nodes enriched with degree metrics", ctx.quiet)
            _log(f"   → Topology roles: {role_counts}", ctx.quiet)
            if disconnection_counts:
                _log(f"   → Disconnection taxonomy: {disconnection_counts}", ctx.quiet)
            # Report top centrality nodes
            if betweenness:
                top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_betweenness:
                    _log(f"   → Top betweenness: {[(n.split('::')[-1], round(v, 4)) for n, v in top_betweenness]}", ctx.quiet)
            if pagerank:
                top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_pagerank:
                    _log(f"   → Top PageRank: {[(n.split('::')[-1], round(v, 4)) for n, v in top_pagerank]}", ctx.quiet)
        except Exception as e:
            # Fallback: compute degrees without networkx
            print(f"   ⚠️ Graph analytics fallback: {type(e).__name__}: {e}")
            in_counts = defaultdict(int)
            out_counts = defaultdict(int)
            # Only count behavioral edges (calls, invokes) for topology classification
            behavioral_edge_types = {'calls', 'invokes'}
            for edge in ctx.edges:
                if edge.get('edge_type') in behavioral_edge_types:
                    src = edge.get('source', edge.get('from', ''))
                    tgt = edge.get('target', edge.get('to', ''))
                    if src:
                        out_counts[src] += 1
                    if tgt:
                        in_counts[tgt] += 1

            # Threshold for hub classification (top 5% or min 10 connections)
            all_degrees = [in_counts.get(n.get('id', ''), 0) + out_counts.get(n.get('id', ''), 0) for n in ctx.nodes]
            hub_threshold = max(10, sorted(all_degrees, reverse=True)[len(all_degrees) // 20] if len(all_degrees) > 20 else 10)

            degree_enriched = 0
            for node in ctx.nodes:
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
            for node in ctx.nodes:
                role = node.get('topology_role', 'unknown')
                role_counts[role] = role_counts.get(role, 0) + 1
                if 'disconnection' in node:
                    source = node['disconnection'].get('reachability_source', 'unknown')
                    disconnection_counts[source] = disconnection_counts.get(source, 0) + 1
            _log(f"   → {degree_enriched} nodes enriched with degree metrics (fallback)", ctx.quiet)
            _log(f"   → Topology roles: {role_counts}", ctx.quiet)
            if disconnection_counts:
                _log(f"   → Disconnection taxonomy: {disconnection_counts}", ctx.quiet)
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

                # Write community_id back to individual nodes so downstream
                # consumers (Chemistry node convergence, color encoding) can read it.
                if communities:
                    node_by_id = {n.get('id', ''): n for n in ctx.nodes}
                    for comm_id, members in communities.items():
                        for member_id in members:
                            if member_id in node_by_id:
                                node_by_id[member_id]['community_id'] = int(comm_id) if isinstance(comm_id, (int, str)) else comm_id

                ctx.graph_analytics = {
                    'bottlenecks': bottlenecks,
                    'pagerank_top': pagerank_top,
                    'communities_count': len(communities),
                    'communities': {str(k): len(v) for k, v in list(communities.items())[:10]} if communities else {},
                }
                timer.set_output(bottlenecks=len(bottlenecks), pagerank=len(pagerank_top), communities=len(communities))
                _log(f"   → {len(bottlenecks)} bottlenecks identified", ctx.quiet)
                _log(f"   → {len(pagerank_top)} PageRank leaders", ctx.quiet)
                _log(f"   → {len(communities)} communities detected", ctx.quiet)
            else:
                ctx.graph_analytics = {}
        except Exception as e:
            ctx.graph_analytics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Advanced graph analytics skipped: {e}")
    ctx.data_ledger.publish("graph_analytics", "Stage 6.5: Graph Analytics",
        summary=f"{len(ctx.nodes)} nodes enriched")


def _run_statistical(ctx: PipelineContext) -> None:
    """Stage 6.6: Statistical Metrics (Entropy, Complexity, Halstead)."""
    from observability import StageTimer

    print("\n📊 Stage 6.6: Statistical Metrics...")
    with StageTimer(ctx.perf_manager, "Stage 6.6: Statistical Metrics") as timer:
        try:
            from analytics_engine import compute_all_metrics
            ctx.statistical_metrics = compute_all_metrics(ctx.nodes)
            timer.set_output(
                avg_cyclomatic=ctx.statistical_metrics['complexity']['avg'],
                total_volume=ctx.statistical_metrics['halstead']['total_volume'],
                estimated_bugs=ctx.statistical_metrics['halstead']['estimated_bugs']
            )
            _log(f"   → Avg cyclomatic: {ctx.statistical_metrics['complexity']['avg']}", ctx.quiet)
            _log(f"   → High complexity nodes: {ctx.statistical_metrics['complexity']['high_complexity_count']}", ctx.quiet)
            _log(f"   → Est. bugs: {ctx.statistical_metrics['halstead']['estimated_bugs']}", ctx.quiet)
            ctx.data_ledger.publish("statistical_metrics", "Stage 6.6: Statistical Metrics",
                summary=f"avg_cc={ctx.statistical_metrics['complexity']['avg']}")
        except Exception as e:
            ctx.statistical_metrics = {}
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Statistical metrics skipped: {e}")
            ctx.data_ledger.publish("statistical_metrics", "Stage 6.6: Statistical Metrics", status="skipped", summary=str(e))


def _run_semantic(ctx: PipelineContext) -> None:
    """Stage 6.7: Semantic Purpose Analysis (PURPOSE = f(edges))."""
    from src.core.graph_framework import (
        build_nx_graph,
        find_entry_points,
        propagate_context,
        classify_node_role,
    )
    from src.core.graph_metrics import identify_critical_nodes
    from src.core.intent_extractor import build_node_intent_profiles_batch
    from observability import StageTimer

    print("\n🎯 Stage 6.7: Semantic Purpose Analysis...")
    ctx.semantic_analysis = {
        'entry_points': [],
        'node_context': {},
        'centrality': {},
        'role_distribution': {},
        'critical_nodes': {},
        'intent_summary': {}
    }
    with StageTimer(ctx.perf_manager, "Stage 6.7: Semantic Purpose") as timer:
        try:
            # Re-use the full graph built in Stage 6.5 (all edge types: calls, imports,
            # contains, inherits …).  Avoids a second build_nx_graph() call.
            # Falls back to building a new graph when Stage 6.5 failed (NetworkX absent).
            if ctx.nx_graph_full is not None:
                G = ctx.nx_graph_full
            else:
                G = build_nx_graph(ctx.nodes, ctx.edges)

            # Find entry points (main, CLI, routes, handlers)
            entry_points = find_entry_points(G)
            ctx.semantic_analysis['entry_points'] = entry_points

            # Propagate context from entry points downstream (top-down comprehension)
            node_context = propagate_context(G, entry_points, max_depth=15)
            ctx.semantic_analysis['node_context'] = {
                'reachable_count': len(node_context),
                'max_depth': max((ctx_item.get('depth_from_entry', 0) for ctx_item in node_context.values()), default=0)
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
                for node in ctx.nodes
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
                ctx.semantic_analysis['centrality'] = {
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
                for node in ctx.nodes
                for node_id in [node.get('id')]
                if node_id
            }
            critical_nodes = identify_critical_nodes(G, centrality_full, top_n=10)
            ctx.semantic_analysis['critical_nodes'] = critical_nodes

            # Enrich nodes with semantic roles, context, and critical flags
            role_counts = {'utility': 0, 'orchestrator': 0, 'hub': 0, 'leaf': 0}
            intent_stats = {'with_docstring': 0, 'with_commits': 0, 'empty': 0}

            # Pre-fetch all git history in one pass: one subprocess per unique
            # file path instead of one per node (~300s savings)
            intent_profiles = build_node_intent_profiles_batch(
                ctx.nodes, repo_path=ctx.target, num_commits=5
            )

            for node in ctx.nodes:
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
                    ctx_item = node_context[node_id]
                    node['depth_from_entry'] = ctx_item.get('depth_from_entry', -1)
                    node['reachable_from_entry'] = True
                    if ctx_item.get('call_chain'):
                        node['call_chain_length'] = len(ctx_item['call_chain'])
                else:
                    node['reachable_from_entry'] = False
                    node['depth_from_entry'] = -1

                # Apply pre-fetched intent profile (no subprocess here)
                intent_profile = intent_profiles.get(node_id)
                if intent_profile:
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

            ctx.semantic_analysis['role_distribution'] = role_counts
            ctx.semantic_analysis['intent_summary'] = {
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
            _log(f"   → {len(entry_points)} entry points detected", ctx.quiet)
            _log(f"   → {len(node_context)} nodes reachable from entry", ctx.quiet)
            _log(f"   → Roles: {role_counts['utility']} utility, {role_counts['orchestrator']} orchestrator, {role_counts['hub']} hub, {role_counts['leaf']} leaf", ctx.quiet)
            _log(f"   → Intent: {intent_stats['with_docstring']} with docstring, {intent_stats['with_commits']} with commits", ctx.quiet)
            ctx.data_ledger.publish("semantic_analysis", "Stage 6.7: Semantic Purpose Analysis",
                summary=f"{len(entry_points)} entries, {len(node_context)} reachable")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Semantic purpose analysis skipped: {e}")
            ctx.data_ledger.publish("semantic_analysis", "Stage 6.7: Semantic Purpose Analysis", status="skipped", summary=str(e))


def _run_codome(ctx: PipelineContext) -> None:
    """Stage 6.8: Codome Boundary Generation."""
    from src.core.codome_boundary import create_codome_boundaries
    from observability import StageTimer

    print("\n🌐 Stage 6.8: Codome Boundary Generation...")
    ctx.codome_result = {'boundary_nodes': [], 'inferred_edges': [], 'summary': {}}
    with StageTimer(ctx.perf_manager, "Stage 6.8: Codome Boundaries") as timer:
        try:
            ctx.codome_result = create_codome_boundaries(ctx.nodes, ctx.edges)
            timer.set_output(
                boundaries=ctx.codome_result['total_boundaries'],
                inferred_edges=ctx.codome_result['total_inferred_edges']
            )
            if ctx.codome_result['boundary_nodes']:
                _log(f"   → {ctx.codome_result['total_boundaries']} codome boundary nodes created", ctx.quiet)
                _log(f"   → {ctx.codome_result['total_inferred_edges']} inferred edges generated", ctx.quiet)
                _log(f"   → Sources: {ctx.codome_result['summary']}", ctx.quiet)
                # Add boundary nodes and inferred edges to main lists for visualization
                # Mark with _fromCodome flag for UI filtering
                for bn in ctx.codome_result['boundary_nodes']:
                    bn['_fromCodome'] = True
                for ie in ctx.codome_result['inferred_edges']:
                    ie['_fromCodome'] = True
                ctx.nodes.extend(ctx.codome_result['boundary_nodes'])
                ctx.edges.extend(ctx.codome_result['inferred_edges'])
            else:
                print("   → No disconnected nodes to link")
            ctx.data_ledger.publish("codome", "Stage 6.8: Codome Boundaries",
                summary=f"{ctx.codome_result.get('total_boundaries', 0)} boundaries")
        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ Codome boundary generation skipped: {e}")
            ctx.data_ledger.publish("codome", "Stage 6.8: Codome Boundaries", status="skipped", summary=str(e))


def _run_api_drift(ctx: PipelineContext) -> None:
    """Stage 6.9: API Backend/Frontend Drift Detection."""
    from observability import StageTimer

    print("\n🔗 Stage 6.9: API Drift Detection...")
    with StageTimer(ctx.perf_manager, "Stage 6.9: API Drift Detection") as timer:
        try:
            from src.core.api_route_extractor import extract_api_routes
            from src.core.frontend_api_detector import detect_frontend_api_calls
            from src.core.api_drift_analyzer import analyze_api_drift, generate_api_edges

            # Step 1: Extract backend API routes
            ctx.endpoint_catalog = extract_api_routes(
                ctx.nodes, ctx.edges, source_root=str(ctx.target),
            )
            _log(f"   → {ctx.endpoint_catalog.total_routes} backend routes "
                 f"({ctx.endpoint_catalog.framework_detected})", ctx.quiet)

            # Step 2: Detect frontend API calls
            ctx.consumer_report = detect_frontend_api_calls(ctx.nodes, ctx.edges)
            _log(f"   → {ctx.consumer_report.total_calls} frontend API calls "
                 f"({ctx.consumer_report.unique_endpoints_called} unique)", ctx.quiet)

            # Step 3: Compare and detect drift
            ctx.api_drift_report = analyze_api_drift(
                ctx.endpoint_catalog, ctx.consumer_report,
            )

            # Step 4: Inject api_call/api_drift edges into the graph
            drift_edges = generate_api_edges(ctx.api_drift_report)
            if drift_edges:
                # Normalize edge IDs: strip frontend::/backend:: prefix and
                # convert absolute paths to relative (matching node ID format).
                repo_prefix = str(ctx.target).rstrip("/") + "/"
                for edge in drift_edges:
                    for key in ("source", "target"):
                        val = edge.get(key, "")
                        # Strip domain prefix
                        for prefix in ("frontend::", "backend::"):
                            if val.startswith(prefix):
                                val = val[len(prefix):]
                                break
                        # Convert absolute path to relative
                        if val.startswith(repo_prefix):
                            val = val[len(repo_prefix):]
                        edge[key] = val
                ctx.edges.extend(drift_edges)

            summary = ctx.api_drift_report.summary()
            timer.set_output(
                backend_routes=ctx.endpoint_catalog.total_routes,
                frontend_calls=ctx.consumer_report.total_calls,
                matched=ctx.api_drift_report.matched_endpoints,
                drift_items=len(ctx.api_drift_report.drift_items),
                drift_score=round(ctx.api_drift_report.drift_score, 4),
            )
            _log(f"   → Matched: {ctx.api_drift_report.matched_endpoints}, "
                 f"Drift items: {len(ctx.api_drift_report.drift_items)}, "
                 f"Score: {ctx.api_drift_report.drift_score:.2%}", ctx.quiet)

            # Log drift items by severity
            by_sev = summary.get('by_severity', {})
            if any(v > 0 for v in by_sev.values()):
                parts = [f"{k}={v}" for k, v in by_sev.items() if v > 0]
                _log(f"   → Severity: {', '.join(parts)}", ctx.quiet)
            ctx.data_ledger.publish("api_drift", "Stage 6.9: API Drift Detection",
                summary=f"{len(ctx.api_drift_report.drift_items)} items, score={ctx.api_drift_report.drift_score:.2%}")

        except Exception as e:
            timer.set_status("WARN", str(e))
            print(f"   ⚠️ API drift detection skipped: {e}")
            ctx.data_ledger.publish("api_drift", "Stage 6.9: API Drift Detection", status="skipped", summary=str(e))
