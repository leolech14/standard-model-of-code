"""
Stage 6.6: Statistical Metrics

Calculates information-theoretic and Halstead complexity metrics.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class StatisticalMetricsStage(BaseStage):
    """
    Stage 6.6: Statistical Metrics.

    Input: CodebaseState with nodes
    Output: CodebaseState with statistical metrics

    Calculates:
    - Entropy (information density)
    - Halstead metrics (volume, difficulty, effort)
    - Maintainability index
    """

    @property
    def name(self) -> str:
        return "statistical_metrics"

    @property
    def stage_number(self) -> Optional[int]:
        return 6  # 6.6 maps to phase 6

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute statistical metrics.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from analytics_engine import compute_all_metrics

            nodes_list = list(state.nodes.values())
            stats = compute_all_metrics(nodes_list)

            state.metadata['stats'] = stats

            # Update nodes with per-node metrics if available
            if 'node_metrics' in stats:
                for node_id, metrics in stats['node_metrics'].items():
                    if node_id in state.nodes:
                        state.nodes[node_id].update(metrics)

            print(f"   → Entropy: {stats.get('entropy', 0):.2f}, "
                  f"Halstead difficulty: {stats.get('halstead_difficulty', 0):.2f}")

        except ImportError as e:
            print(f"   → Statistical metrics skipped: {e}")

        return state
