"""
Stage 5: Markov Transition Matrix

Computes probability of transitioning between nodes in the call graph.
Used for predicting execution flow and identifying critical paths.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class MarkovMatrixStage(BaseStage):
    """
    Stage 5: Markov Transition Matrix.

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with markov transition probabilities

    Computes:
    - Transition probabilities between nodes
    - Stationary distribution
    - Critical paths
    """

    @property
    def name(self) -> str:
        return "markov_matrix"

    @property
    def stage_number(self) -> Optional[int]:
        return 5

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes and edges."""
        return len(state.nodes) > 0 and len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute Markov transition matrix.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        # Use the compute_markov_matrix from full_analysis
        try:
            from full_analysis import compute_markov_matrix

            nodes_list = list(state.nodes.values())
            markov = compute_markov_matrix(nodes_list, state.edges)

            state.metadata['markov'] = markov

            # Extract key metrics
            high_prob_transitions = sum(1 for v in markov.values() if v.get('max_prob', 0) > 0.5)
            print(f"   → {len(markov)} transition probabilities, {high_prob_transitions} high-probability paths")

        except Exception as e:
            print(f"   → Markov matrix computation skipped: {e}")

        return state
