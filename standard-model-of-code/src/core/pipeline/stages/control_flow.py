"""
Stage 2.9: Control Flow Metrics

Calculates cyclomatic complexity and nesting depth per function.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ControlFlowStage(BaseStage):
    """
    Stage 2.9: Control Flow Metrics.

    Input: CodebaseState with nodes containing body_source
    Output: CodebaseState with control_flow metrics per node

    Calculates:
    - Cyclomatic complexity
    - Maximum nesting depth
    - Branch count
    """

    @property
    def name(self) -> str:
        return "control_flow"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.9 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with body_source."""
        return any(n.get('body_source') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Calculate control flow metrics.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from control_flow_analyzer import analyze_control_flow

            nodes_list = list(state.nodes.values())
            cf_results = analyze_control_flow(nodes_list)

            high_complexity = 0
            deep_nesting = 0

            for node_id, cf_info in cf_results.items():
                if node_id in state.nodes:
                    state.nodes[node_id]['control_flow'] = cf_info
                    state.nodes[node_id]['cyclomatic_complexity'] = cf_info.get('cyclomatic', 1)
                    state.nodes[node_id]['nesting_depth'] = cf_info.get('max_nesting', 0)

                    if cf_info.get('cyclomatic', 1) > 10:
                        high_complexity += 1
                    if cf_info.get('max_nesting', 0) > 4:
                        deep_nesting += 1

            state.metadata['control_flow'] = {
                'high_complexity_count': high_complexity,
                'deep_nesting_count': deep_nesting,
            }

            print(f"   → {high_complexity} high-complexity functions, {deep_nesting} deeply nested")

        except ImportError as e:
            print(f"   → Control flow analysis skipped: {e}")

        return state
