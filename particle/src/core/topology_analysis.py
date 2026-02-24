"""
Topology analysis: Markov matrices, knot detection, and data flow.

Graph-level analysis that operates on the complete node/edge graph
to detect cycles, compute transition probabilities, and trace data flow.

Extracted from full_analysis.py during audit refactoring (2026-02-24).
"""
import sys
from collections import defaultdict
from typing import Dict, List


def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Compute Markov transition matrix from call graph.
    P(A -> B) = calls from A to B / total calls from A

    Also enriches edges with markov_weight for visualization.
    """
    # Build adjacency counts
    out_counts = defaultdict(lambda: defaultdict(int))
    out_totals = defaultdict(int)

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            out_counts[source][target] += 1
            out_totals[source] += 1

    # Compute probabilities
    transitions = {}
    for source, targets in out_counts.items():
        total = out_totals[source]
        transitions[source] = {
            target: count / total
            for target, count in targets.items()
        }

    # Enrich edges with markov_weight for flow visualization
    edges_with_weight = 0
    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source in transitions and target in transitions[source]:
            edge['markov_weight'] = transitions[source][target]
            edges_with_weight += 1
        else:
            edge['markov_weight'] = 0.0

    # Summary stats
    high_entropy_nodes = []
    for source, probs in transitions.items():
        if len(probs) > 5:
            high_entropy_nodes.append({
                'node': source.split(':')[-1] if ':' in source else source,
                'fanout': len(probs),
                'max_prob': max(probs.values()) if probs else 0
            })

    return {
        'total_transitions': len(transitions),
        'edges_with_weight': edges_with_weight,
        'avg_fanout': sum(len(t) for t in transitions.values()) / len(transitions) if transitions else 0,
        'high_entropy_nodes': sorted(high_entropy_nodes, key=lambda x: -x['fanout'])[:10],
        'transitions': transitions
    }


def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Detect dependency knots (cycles) and tangles in the graph.
    Uses Tarjan's SCC algorithm (O(V+E)) to find all directed cycles.
    - Cycles: Strongly connected components with >1 node
    - Tangles: Bidirectional edges (A imports B and B imports A)
    """
    # Build adjacency -- exclude structural edges (contains, member_of)
    STRUCTURAL_EDGE_TYPES = {'contains', 'member_of', 'defines', 'parent'}
    graph = defaultdict(set)
    adj_list = defaultdict(list)

    for edge in edges:
        if edge.get('edge_type', '') in STRUCTURAL_EDGE_TYPES:
            continue
        source = edge.get('source', '')
        target = edge.get('target', '')
        if source and target:
            graph[source].add(target)
            adj_list[source].append(target)

    # Tarjan's SCC algorithm
    node_ids = list(graph.keys())
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(node_ids) + 500))

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True

        for w in adj_list[v]:
            if w not in index:
                strongconnect(w)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif on_stack.get(w, False):
                lowlinks[v] = min(lowlinks[v], index[w])

        if lowlinks[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:
                sccs.append(scc)

    try:
        for v in node_ids:
            if v not in index:
                strongconnect(v)
    except RecursionError:
        pass
    finally:
        sys.setrecursionlimit(old_limit)

    # Extract cycle info
    cycle_groups = len(sccs)
    cyclic_nodes = sum(len(scc) for scc in sccs)

    # Find bidirectional edges (tangles)
    seen_pairs = set()
    bidirectional = []
    for source, targets in graph.items():
        for target in targets:
            if source in graph.get(target, set()):
                pair = tuple(sorted([source, target]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    bidirectional.append({
                        'a': source.split(':')[-1] if ':' in source else source,
                        'b': target.split(':')[-1] if ':' in target else target
                    })

    # Compute knot score: 0 = no knots, 10 = severely tangled
    total_nodes = len(set(n.get('id', '') for n in nodes)) or 1

    # Identify the size of the largest isolated cycle
    max_scc_size = max([len(scc) for scc in sccs]) if sccs else 0
    cyclic_pct = (cyclic_nodes / total_nodes) * 100

    # Score 1: Base percentage of cyclic nodes (50% of codebase = max 5 points)
    pct_score = min(5.0, (cyclic_pct / 50.0) * 5.0)

    # Score 2: Penalize massive single monolithic loops (20+ nodes = max 3 points)
    scc_score = min(3.0, (max_scc_size / 20.0) * 3.0)

    # Score 3: Raw group complexity (multiple cycles = max 1 point)
    groups_score = min(1.0, cycle_groups * 0.25)

    # Score 4: Tight bidirectional coupling (4 pairs = max 1 point)
    bidir_score = min(1.0, len(bidirectional) * 0.25)

    knot_score = min(10.0, pct_score + scc_score + groups_score + bidir_score)

    return {
        'cycles_detected': cycle_groups,
        'cyclic_nodes': cyclic_nodes,
        'bidirectional_edges': len(bidirectional),
        'knot_score': round(knot_score, 1),
        'sample_cycles': [scc[:5] for scc in sccs[:5]],
        'sample_tangles': bidirectional[:10]
    }


def compute_data_flow(nodes: List[Dict], edges: List[Dict]) -> Dict:
    """
    Analyze data flow patterns across the codebase.
    """
    # Track flow by type
    flow_by_type = defaultdict(lambda: {'in': 0, 'out': 0})

    for edge in edges:
        source = edge.get('source', '')
        target = edge.get('target', '')

        source_type = None
        target_type = None
        for n in nodes:
            if n.get('id') == source:
                source_type = n.get('type', 'Unknown')
            if n.get('id') == target:
                target_type = n.get('type', 'Unknown')

        if source_type:
            flow_by_type[source_type]['out'] += 1
        if target_type:
            flow_by_type[target_type]['in'] += 1

    # Identify data sources and sinks
    sources = []
    sinks = []

    for type_name, flow in flow_by_type.items():
        ratio = flow['out'] / flow['in'] if flow['in'] > 0 else flow['out']
        if ratio > 2 and flow['out'] > 10:
            sources.append({'type': type_name, 'ratio': round(ratio, 1), 'out': flow['out']})
        elif ratio < 0.5 and flow['in'] > 10:
            sinks.append({'type': type_name, 'ratio': round(ratio, 1), 'in': flow['in']})

    return {
        'flow_by_type': dict(flow_by_type),
        'data_sources': sorted(sources, key=lambda x: -x['out'])[:5],
        'data_sinks': sorted(sinks, key=lambda x: -x['in'])[:5],
        'total_flow_edges': len(edges)
    }
