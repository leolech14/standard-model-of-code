"""
Stage 7: Data Flow (Macro)

Identifies data sources (inputs) and sinks (outputs) at system level.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class DataFlowMacroStage(BaseStage):
    """
    Stage 7: Data Flow (Macro).

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with data flow analysis

    Identifies:
    - Data sources (user input, file reads, API calls)
    - Data sinks (database writes, file writes, API responses)
    - Data transformation chains
    """

    @property
    def name(self) -> str:
        return "data_flow_macro"

    @property
    def stage_number(self) -> Optional[int]:
        return 7

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes and edges."""
        return len(state.nodes) > 0 and len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute macro-level data flow.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from full_analysis import compute_data_flow

            nodes_list = list(state.nodes.values())
            data_flow = compute_data_flow(nodes_list, state.edges)

            state.metadata['macro_data_flow'] = data_flow

            sources = len(data_flow.get('sources', []))
            sinks = len(data_flow.get('sinks', []))
            print(f"   → {sources} data sources, {sinks} data sinks")

        except Exception as e:
            print(f"   → Macro data flow skipped: {e}")

        return state
