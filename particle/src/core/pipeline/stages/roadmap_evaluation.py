"""
Stage 9: Roadmap Evaluation (Optional)

Evaluates codebase against a defined roadmap.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class RoadmapEvaluationStage(BaseStage):
    """
    Stage 9: Roadmap Evaluation.

    Input: CodebaseState with full analysis
    Output: CodebaseState with roadmap evaluation results

    Evaluates:
    - Feature completeness
    - Technical debt
    - Architecture alignment
    """

    def __init__(self, roadmap_name: Optional[str] = None):
        """
        Initialize with optional roadmap name.

        Args:
            roadmap_name: Name of roadmap to evaluate against
        """
        self._roadmap_name = roadmap_name

    @property
    def name(self) -> str:
        return "roadmap_evaluation"

    @property
    def stage_number(self) -> Optional[int]:
        return 9

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have analysis results."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Evaluate against roadmap.
        """
        if not self._roadmap_name:
            print("   → Roadmap evaluation skipped (no roadmap specified)")
            return state

        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from roadmap_evaluator import RoadmapEvaluator

            evaluator = RoadmapEvaluator(self._roadmap_name)

            # Build full output for evaluator
            full_output = {
                'nodes': list(state.nodes.values()),
                'edges': state.edges,
                'metadata': state.metadata,
            }

            roadmap_result = evaluator.evaluate(full_output)

            state.metadata['roadmap'] = roadmap_result

            score = roadmap_result.get('score', 0)
            print(f"   → Roadmap score: {score:.1f}%")

        except Exception as e:
            print(f"   → Roadmap evaluation skipped: {e}")

        return state
