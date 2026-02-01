"""Graph-based semantic analysis framework.

Implements PURPOSE = f(edges) by building NetworkX graphs from
Collider's unified_analysis.json and computing relationship metrics.

Based on PURPOSE_ONTOLOGY research (85% validated) and Perplexity
academic research (60 citations).

Key insight: A function's purpose is revealed by its RELATIONSHIPS
(who calls it, what it calls) not its CONTENT (implementation).
"""
import networkx as nx
from collections import deque
from typing import Dict, List, Any, Optional, Set


def build_nx_graph(nodes: List[Dict], edges: List[Dict]) -> nx.DiGraph:
    """Build NetworkX DiGraph from Collider analysis output.

    Args:
        nodes: List of node dicts with 'id' and attributes
        edges: List of edge dicts with 'source', 'target', and attributes

    Returns:
        Directed graph with all node/edge attributes preserved
    """
    G = nx.DiGraph()

    for node in nodes:
        node_id = node.get('id')
        if node_id:
            G.add_node(node_id, **node)

    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source and target:
            G.add_edge(source, target, **edge)

    return G


def compute_degree_metrics(G: nx.DiGraph) -> Dict[str, Dict[str, int]]:
    """Compute in-degree and out-degree for each node.

    Semantic interpretation:
    - High in-degree = utility (called by many) - "servant"
    - High out-degree = orchestrator (calls many) - "commander"
    - High both = hub (critical junction)
    - Low both = leaf (specialized/isolated)
    """
    return {
        node: {
            'in_degree': G.in_degree(node),
            'out_degree': G.out_degree(node)
        }
        for node in G.nodes
    }


def classify_node_role(
    in_degree: int,
    out_degree: int,
    in_threshold: int = 5,
    out_threshold: int = 5
) -> str:
    """Classify architectural role from degree metrics.

    Based on PURPOSE_ONTOLOGY research:
    - High in, low out = UTILITY (serves many)
    - Low in, high out = ORCHESTRATOR (coordinates many)
    - High both = HUB (critical junction)
    - Low both = LEAF (specialized)

    Args:
        in_degree: Number of incoming edges (callers)
        out_degree: Number of outgoing edges (callees)
        in_threshold: Threshold for "high" in-degree
        out_threshold: Threshold for "high" out-degree

    Returns:
        Role classification string
    """
    high_in = in_degree >= in_threshold
    high_out = out_degree >= out_threshold

    if high_in and not high_out:
        return "utility"
    elif high_out and not high_in:
        return "orchestrator"
    elif high_in and high_out:
        return "hub"
    else:
        return "leaf"


def find_entry_points(G: nx.DiGraph) -> List[str]:
    """Find likely entry points (nodes with 0 in-degree or special names).

    Entry points are where execution begins - important for
    top-down context propagation.
    """
    entry_points = set()

    # Nodes with zero in-degree (nothing calls them)
    for node in G.nodes:
        if G.in_degree(node) == 0:
            entry_points.add(node)

    # Common entry point patterns
    entry_patterns = [
        'main', 'cli', 'app', 'server', 'index', 'run',
        '__main__', 'entrypoint', 'handler', 'lambda_handler'
    ]

    for node in G.nodes:
        node_lower = node.lower()
        if any(p in node_lower for p in entry_patterns):
            entry_points.add(node)

    return list(entry_points)


def propagate_context(
    G: nx.DiGraph,
    root_nodes: List[str],
    max_depth: int = 10
) -> Dict[str, Dict]:
    """Propagate context via BFS from root nodes downstream.

    Implements cognitive research finding: experts understand code
    top-down, with parent context informing child interpretation.

    "You must read the map before you study the terrain."

    Args:
        G: Code graph
        root_nodes: Entry points (main, routes, CLI)
        max_depth: Maximum propagation depth

    Returns:
        Dict mapping node_id to enriched context including:
        - parent_context: Info from calling node
        - depth_from_entry: Distance from nearest entry point
        - call_chain: Path from entry to this node
    """
    node_context: Dict[str, Dict] = {}
    queue = deque()

    # Initialize queue with root nodes
    for node in root_nodes:
        if node in G.nodes:
            queue.append((node, 0, [], {}))

    visited: Set[str] = set()

    while queue:
        node_id, depth, call_chain, parent_context = queue.popleft()

        # Skip if visited or too deep
        if node_id in visited or depth > max_depth:
            continue
        visited.add(node_id)

        # Get node data from graph
        node_data = dict(G.nodes[node_id]) if node_id in G.nodes else {}

        # Build context for this node
        context = {
            **node_data,
            'depth_from_entry': depth,
            'call_chain': call_chain + [node_id],
            'parent_context': parent_context,
            'reachable_from_entry': True
        }
        node_context[node_id] = context

        # Propagate to callees (successors in call graph)
        for callee in G.successors(node_id):
            child_parent_context = {
                'parent_id': node_id,
                'parent_role': node_data.get('semantic_role', 'unknown'),
                'parent_atom': node_data.get('atom_type', 'unknown'),
            }
            queue.append((
                callee,
                depth + 1,
                call_chain + [node_id],
                child_parent_context
            ))

    return node_context


def get_node_neighborhood(
    G: nx.DiGraph,
    node_id: str,
    radius: int = 1
) -> Dict[str, Any]:
    """Get the local neighborhood of a node.

    Useful for understanding a node's immediate context without
    analyzing the entire graph.
    """
    if node_id not in G.nodes:
        return {}

    predecessors = list(G.predecessors(node_id))[:10]  # Limit
    successors = list(G.successors(node_id))[:10]

    return {
        'node_id': node_id,
        'callers': predecessors,
        'callees': successors,
        'caller_count': G.in_degree(node_id),
        'callee_count': G.out_degree(node_id),
    }


def analyze_graph(
    nodes: List[Dict],
    edges: List[Dict]
) -> Dict[str, Any]:
    """Complete graph analysis pipeline.

    Convenience function that runs all Phase 1 analysis.

    Returns:
        Dict with:
        - graph: NetworkX DiGraph
        - degree_metrics: In/out degree per node
        - entry_points: Detected entry points
        - node_context: Propagated context
        - summary: High-level statistics
    """
    # Build graph
    G = build_nx_graph(nodes, edges)

    # Compute metrics
    degree_metrics = compute_degree_metrics(G)

    # Find entry points
    entry_points = find_entry_points(G)

    # Propagate context
    node_context = propagate_context(G, entry_points)

    # Compute role distribution
    role_counts = {'utility': 0, 'orchestrator': 0, 'hub': 0, 'leaf': 0}
    for node_id, metrics in degree_metrics.items():
        role = classify_node_role(metrics['in_degree'], metrics['out_degree'])
        role_counts[role] += 1

    return {
        'graph': G,
        'degree_metrics': degree_metrics,
        'entry_points': entry_points,
        'node_context': node_context,
        'summary': {
            'node_count': len(G.nodes),
            'edge_count': len(G.edges),
            'entry_point_count': len(entry_points),
            'reachable_count': len(node_context),
            'role_distribution': role_counts
        }
    }
