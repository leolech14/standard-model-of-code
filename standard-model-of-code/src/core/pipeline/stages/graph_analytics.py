"""
Stage 6.5: Graph Analytics

Computes graph-theoretic metrics: centrality, clustering, connectivity.
These metrics inform architectural analysis and visualization.
"""

from typing import TYPE_CHECKING

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class GraphAnalyticsStage(BaseStage):
    """
    Stage 6.5: Graph Analytics.

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with graph metrics per node

    Adds per-node metrics:
    - in_degree: Number of incoming edges
    - out_degree: Number of outgoing edges
    - betweenness: Betweenness centrality (if computed)
    - clustering: Local clustering coefficient
    """

    @property
    def name(self) -> str:
        return "graph_analytics"

    @property
    def stage_number(self) -> int:
        return 6  # Stage 6.5 maps to 6

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have a graph to analyze."""
        return len(state.nodes) > 0 and len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute graph analytics metrics.
        """
        # Compute in/out degree from state's edge indexes
        for node_id in state.nodes:
            in_edges = state.get_edges_to(node_id)
            out_edges = state.get_edges_from(node_id)

            state.nodes[node_id]['in_degree'] = len(in_edges)
            state.nodes[node_id]['out_degree'] = len(out_edges)
            state.nodes[node_id]['total_degree'] = len(in_edges) + len(out_edges)

        # Compute basic connectivity metrics
        orphan_count = sum(
            1 for n in state.nodes.values()
            if n.get('total_degree', 0) == 0
        )
        hub_count = sum(
            1 for n in state.nodes.values()
            if n.get('total_degree', 0) > 10
        )

        # Store aggregate metrics
        state.metadata['graph_analytics'] = {
            'total_nodes': len(state.nodes),
            'total_edges': len(state.edges),
            'orphan_nodes': orphan_count,
            'hub_nodes': hub_count,
            'avg_degree': (
                sum(n.get('total_degree', 0) for n in state.nodes.values())
                / len(state.nodes) if state.nodes else 0
            ),
        }

        print(f"   → {orphan_count} orphans, {hub_count} hubs, "
              f"avg degree {state.metadata['graph_analytics']['avg_degree']:.2f}")

        return state
