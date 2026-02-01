"""
Stage 4: Execution Flow

Analyzes code execution flow as a parallel semantic layer to Purpose Field:
- Causality chain detection (entry → calls → exit)
- Orphan detection (dead code, unused functions)
- Integration error detection (broken references)
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ExecutionFlowStage(BaseStage):
    """
    Stage 4: Execution Flow Analysis.

    Input: CodebaseState with nodes, edges, and purpose field
    Output: CodebaseState with execution flow analysis

    Adds:
    - Causality chains from entry points
    - Orphan detection (dead code)
    - Integration error detection
    - Reachability paths
    """

    @property
    def name(self) -> str:
        return "execution_flow"

    @property
    def stage_number(self) -> Optional[int]:
        return 4

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes and edges."""
        return len(state.nodes) > 0 and len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Detect execution flow patterns.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from execution_flow import detect_execution_flow

            # Get nodes and edges
            nodes_list = list(state.nodes.values())
            edges_list = state.edges

            # Get purpose field if available
            purpose_field = state.metadata.get('purpose_field')

            # Detect execution flow
            exec_flow = detect_execution_flow(nodes_list, edges_list, purpose_field)

            # Store results in state metadata
            state.metadata['execution_flow'] = exec_flow.summary()

            # Update nodes with flow information
            orphan_count = 0
            for node_id, flow_node in exec_flow.nodes.items():
                if node_id in state.nodes:
                    state.nodes[node_id]['is_orphan'] = flow_node.is_orphan
                    state.nodes[node_id]['is_entry_point'] = flow_node.is_entry_point
                    state.nodes[node_id]['in_degree'] = flow_node.in_degree
                    state.nodes[node_id]['out_degree'] = flow_node.out_degree
                    if flow_node.is_orphan:
                        orphan_count += 1

            # Store summary stats
            state.metadata['execution_flow']['orphan_count'] = orphan_count
            state.metadata['execution_flow']['entry_points'] = exec_flow.entry_points
            state.metadata['execution_flow']['dead_code_percent'] = exec_flow.dead_code_percent

            print(f"   → Execution flow: {len(exec_flow.entry_points)} entry points, "
                  f"{orphan_count} orphans ({exec_flow.dead_code_percent:.1f}% dead code)")

        except Exception as e:
            print(f"   → Execution flow skipped: {e}")
            state.metadata['execution_flow'] = {'error': str(e)}

        return state
