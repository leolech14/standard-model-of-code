"""
Stage 6: Knot/Cycle Detection

Finds circular dependencies and tangled code structures.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class KnotDetectionStage(BaseStage):
    """
    Stage 6: Knot/Cycle Detection.

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with knot information

    Detects:
    - Circular dependencies (A → B → C → A)
    - Bidirectional edges (A ↔ B)
    - Tangled clusters
    """

    @property
    def name(self) -> str:
        return "knot_detection"

    @property
    def stage_number(self) -> Optional[int]:
        return 6

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have edges."""
        return len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Detect knots and cycles.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from full_analysis import detect_knots

            nodes_list = list(state.nodes.values())
            knots = detect_knots(nodes_list, state.edges)

            state.metadata['knots'] = knots

            cycle_count = len(knots.get('cycles', []))
            bidir_count = len(knots.get('bidirectional', []))
            print(f"   → {cycle_count} cycles, {bidir_count} bidirectional edges")

        except Exception as e:
            print(f"   → Knot detection skipped: {e}")

        return state
