"""
Stage 11b: AI Insights (Optional)

Generates LLM-powered insights about the codebase.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class AIInsightsStage(BaseStage):
    """
    Stage 11b: AI Insights.

    Input: CodebaseState with full analysis
    Output: CodebaseState with AI-generated insights

    Requires --ai-insights flag to run.
    Uses LLM to generate:
    - Architecture observations
    - Improvement suggestions
    - Risk analysis
    """

    def __init__(self, enabled: bool = False, model: Optional[str] = None):
        """
        Initialize AI insights stage.

        Args:
            enabled: Whether to run AI insights
            model: LLM model to use (default: configured model)
        """
        self._enabled = enabled
        self._model = model

    @property
    def name(self) -> str:
        return "ai_insights"

    @property
    def stage_number(self) -> Optional[int]:
        return 11  # 11b maps to phase 11

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have analysis results."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Generate AI insights.
        """
        if not self._enabled:
            print("   → AI insights skipped (use --ai-insights to enable)")
            return state

        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            # Build summary for LLM
            summary = {
                'nodes': len(state.nodes),
                'edges': len(state.edges),
                'topology': state.metadata.get('topology', {}),
                'purpose_field': state.metadata.get('purpose_field', {}),
                'constraints': state.metadata.get('constraints', {}),
            }

            # Try insights engine
            from insights_engine import generate_insights

            insights = generate_insights(summary, model=self._model)

            state.metadata['ai_insights'] = insights

            print(f"   → AI insights generated: {len(insights.get('observations', []))} observations")

        except Exception as e:
            print(f"   → AI insights skipped: {e}")

        return state
