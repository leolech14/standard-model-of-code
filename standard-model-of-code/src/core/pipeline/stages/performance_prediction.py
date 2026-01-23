"""
Stage 8: Performance Prediction

Predicts performance characteristics from static analysis.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class PerformancePredictionStage(BaseStage):
    """
    Stage 8: Performance Prediction.

    Input: CodebaseState with execution flow
    Output: CodebaseState with performance predictions

    Predicts:
    - Hot spots (frequently called functions)
    - Bottlenecks (high complexity on critical path)
    - Memory pressure points
    """

    @property
    def name(self) -> str:
        return "performance_prediction"

    @property
    def stage_number(self) -> Optional[int]:
        return 8

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have execution flow or at least edges."""
        return len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Predict performance characteristics.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from performance_predictor import predict_performance

            nodes_list = list(state.nodes.values())
            execution_flow = state.metadata.get('execution_flow')

            perf = predict_performance(nodes_list, execution_flow)

            state.metadata['performance'] = perf

            # Update nodes with hotspot info
            hotspots = perf.get('hotspots', [])
            for hs in hotspots:
                node_id = hs.get('node_id')
                if node_id and node_id in state.nodes:
                    state.nodes[node_id]['is_hotspot'] = True
                    state.nodes[node_id]['hotspot_score'] = hs.get('score', 0)

            print(f"   → {len(hotspots)} predicted hotspots")

        except Exception as e:
            print(f"   → Performance prediction skipped: {e}")

        return state
