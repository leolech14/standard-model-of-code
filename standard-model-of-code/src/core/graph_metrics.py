"""Advanced graph metrics for semantic purpose detection.

Based on Perplexity research (60 citations):
- Betweenness: Critical infrastructure (bridges between components)
- Closeness: Coordination points (can reach many quickly)
- Eigenvector: Important neighbors matter
- PageRank: Influence propagation in directed graphs

These metrics quantify architectural PURPOSE through RELATIONSHIPS,
implementing the core insight: PURPOSE = f(edges).
"""
import networkx as nx
from typing import Dict, List, Any, Set, Optional


def compute_centrality_metrics(
    G: nx.DiGraph,
    timeout_seconds: int = 30
) -> Dict[str, Dict[str, float]]:
    """Compute multiple centrality measures for architectural analysis.

    Each metric reveals different aspects of purpose:
    - betweenness: How much traffic flows through this node (bridge)
    - closeness: How quickly can this node reach others (coordinator)
    - pagerank: How much influence flows to this node (importance)

    Args:
        G: Directed code graph
        timeout_seconds: Max time for expensive computations

    Returns:
        Dict mapping node_id to centrality scores
    """
    metrics: Dict[str, Dict[str, float]] = {
        node: {'betweenness': 0.0, 'closeness': 0.0, 'pagerank': 0.0}
        for node in G.nodes
    }

    if len(G.nodes) == 0:
        return metrics

    # Betweenness centrality: bridges between components
    # High betweenness = critical infrastructure
    try:
        betweenness = nx.betweenness_centrality(G, normalized=True)
        for node, score in betweenness.items():
            metrics[node]['betweenness'] = score
    except Exception:
        pass

    # Closeness centrality: ability to reach others quickly
    # High closeness = good coordinator position
    try:
        # For directed graphs, use "in" or "out" closeness
        closeness = nx.closeness_centrality(G)
        for node, score in closeness.items():
            metrics[node]['closeness'] = score
    except Exception:
        pass

    # PageRank: influence propagation
    # High pagerank = important in information flow
    try:
        pagerank = nx.pagerank(G, alpha=0.85, max_iter=100)
        for node, score in pagerank.items():
            metrics[node]['pagerank'] = score
    except Exception:
        # Fallback: uniform distribution
        uniform = 1.0 / len(G.nodes) if len(G.nodes) > 0 else 0.0
        for node in G.nodes:
            metrics[node]['pagerank'] = uniform

    return metrics


def identify_critical_nodes(
    G: nx.DiGraph,
    metrics: Dict[str, Dict[str, float]],
    top_n: int = 10
) -> Dict[str, List[str]]:
    """Identify architecturally significant nodes by metric.

    Categories:
    - bridges: High betweenness - removing them fragments the system
    - influential: High pagerank - important in information flow
    - coordinators: High closeness - can reach many nodes quickly

    Args:
        G: Code graph
        metrics: Pre-computed centrality metrics
        top_n: Number of top nodes per category

    Returns:
        Dict with node lists for each category
    """
    if not metrics:
        return {'bridges': [], 'influential': [], 'coordinators': []}

    # Sort by each metric
    by_betweenness = sorted(
        metrics.items(),
        key=lambda x: x[1].get('betweenness', 0),
        reverse=True
    )[:top_n]

    by_pagerank = sorted(
        metrics.items(),
        key=lambda x: x[1].get('pagerank', 0),
        reverse=True
    )[:top_n]

    by_closeness = sorted(
        metrics.items(),
        key=lambda x: x[1].get('closeness', 0),
        reverse=True
    )[:top_n]

    return {
        'bridges': [n[0] for n in by_betweenness],
        'influential': [n[0] for n in by_pagerank],
        'coordinators': [n[0] for n in by_closeness]
    }


def detect_clusters(G: nx.DiGraph) -> List[Set[str]]:
    """Detect cohesive modules via community detection.

    Clusters = groups with dense internal connections,
    sparse external connections. These represent cohesive
    modules with shared purpose.

    Uses Louvain algorithm when available, falls back to
    connected components.
    """
    if len(G.nodes) == 0:
        return []

    # Convert to undirected for community detection
    G_undirected = G.to_undirected()

    try:
        # Louvain community detection (best quality)
        from networkx.algorithms.community import louvain_communities
        communities = louvain_communities(G_undirected, seed=42)
        return [set(c) for c in communities]
    except ImportError:
        pass

    try:
        # Fallback: greedy modularity
        from networkx.algorithms.community import greedy_modularity_communities
        communities = greedy_modularity_communities(G_undirected)
        return [set(c) for c in communities]
    except Exception:
        pass

    # Last resort: weakly connected components
    try:
        components = nx.weakly_connected_components(G)
        return [set(c) for c in components]
    except Exception:
        return [set(G.nodes)]


def compute_cluster_metrics(
    G: nx.DiGraph,
    clusters: List[Set[str]]
) -> List[Dict[str, Any]]:
    """Compute metrics for each detected cluster.

    Helps understand what each cluster does:
    - Size and density
    - External vs internal edges
    - Key nodes within cluster
    """
    cluster_metrics = []

    for i, cluster in enumerate(clusters):
        # Subgraph for this cluster
        subgraph = G.subgraph(cluster)

        # Count internal vs external edges
        internal_edges = len(subgraph.edges)
        external_out = sum(
            1 for u, v in G.edges
            if u in cluster and v not in cluster
        )
        external_in = sum(
            1 for u, v in G.edges
            if u not in cluster and v in cluster
        )

        # Find most connected node in cluster
        max_degree_node = None
        max_degree = -1
        for node in cluster:
            degree = G.degree(node)
            if degree > max_degree:
                max_degree = degree
                max_degree_node = node

        cluster_metrics.append({
            'cluster_id': i,
            'size': len(cluster),
            'internal_edges': internal_edges,
            'external_edges_out': external_out,
            'external_edges_in': external_in,
            'cohesion': internal_edges / max(1, internal_edges + external_out + external_in),
            'hub_node': max_degree_node,
            'nodes': list(cluster)[:20]  # Sample for large clusters
        })

    return cluster_metrics


def find_architectural_layers(
    G: nx.DiGraph,
    entry_points: List[str]
) -> Dict[int, List[str]]:
    """Identify architectural layers based on distance from entry.

    Layer 0: Entry points (API, CLI, main)
    Layer 1: Direct handlers
    Layer 2: Business logic
    Layer N: Infrastructure/utilities

    This implements the "Map before Terrain" principle:
    understand high-level structure before diving into details.
    """
    layers: Dict[int, List[str]] = {}
    visited: Set[str] = set()
    current_layer = set(entry_points)
    layer_num = 0

    while current_layer:
        # Filter to unvisited nodes
        current_layer = current_layer - visited
        if not current_layer:
            break

        layers[layer_num] = list(current_layer)
        visited.update(current_layer)

        # Find next layer (all successors of current layer)
        next_layer: Set[str] = set()
        for node in current_layer:
            if node in G.nodes:
                next_layer.update(G.successors(node))

        current_layer = next_layer
        layer_num += 1

    return layers


def analyze_all_metrics(
    G: nx.DiGraph,
    entry_points: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Complete Phase 3 analysis pipeline.

    Convenience function that runs all advanced metrics.
    """
    # Centrality metrics
    centrality = compute_centrality_metrics(G)

    # Critical nodes
    critical = identify_critical_nodes(G, centrality)

    # Clusters
    clusters = detect_clusters(G)
    cluster_metrics = compute_cluster_metrics(G, clusters)

    # Layers (if entry points provided)
    layers = {}
    if entry_points:
        layers = find_architectural_layers(G, entry_points)

    return {
        'centrality_metrics': centrality,
        'critical_nodes': critical,
        'clusters': cluster_metrics,
        'layers': layers,
        'summary': {
            'cluster_count': len(clusters),
            'layer_count': len(layers),
            'bridge_count': len(critical['bridges']),
            'influential_count': len(critical['influential'])
        }
    }
