"""
Stage 14: IGT Metrics (Information Graph Theory)

Computes Information Graph Theory metrics for codebase health:
- Stability calculations based on branching factors
- Directory structure analysis
- Orphan classification and severity
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class IGTMetricsStage(BaseStage):
    """
    Stage 14: IGT Metrics.

    Input: CodebaseState with complete analysis
    Output: CodebaseState with IGT metrics

    Adds:
    - Stability scores per directory
    - Branching factor analysis
    - Classified orphans with severity
    - IGT summary statistics
    """

    @property
    def name(self) -> str:
        return "igt_metrics"

    @property
    def stage_number(self) -> Optional[int]:
        return 13

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute IGT metrics.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from igt_metrics import compute_igt_summary, StabilityCalculator, OrphanClassifier

            # Get nodes and edges
            nodes_list = list(state.nodes.values())
            edges_list = state.edges

            # Compute IGT summary
            igt_results = compute_igt_summary(nodes_list, edges_list)

            # Store in state metadata
            state.metadata['igt_metrics'] = igt_results

            # Extract key stats for logging
            stability_count = len(igt_results.get('stability_analysis', {}))
            orphan_count = len(igt_results.get('classified_orphans', []))
            avg_stability = igt_results.get('average_stability', 0)

            print(f"   → IGT metrics: {stability_count} dirs analyzed, "
                  f"{orphan_count} orphans classified, avg stability: {avg_stability:.2f}")

        except Exception as e:
            print(f"   → IGT metrics skipped: {e}")
            state.metadata['igt_metrics'] = {'error': str(e)}

        return state
