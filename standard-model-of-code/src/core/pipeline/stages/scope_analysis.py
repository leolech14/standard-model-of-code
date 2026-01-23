"""
Stage 2.8: Scope Analysis

Builds lexical scope graph and detects:
- Unused definitions
- Shadowed definitions
- Scope violations
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ScopeAnalysisStage(BaseStage):
    """
    Stage 2.8: Scope Analysis.

    Input: CodebaseState with nodes containing body_source
    Output: CodebaseState with scope_analysis per node

    Detects:
    - Unused variables/functions
    - Shadowed names in nested scopes
    - Closure captures
    """

    @property
    def name(self) -> str:
        return "scope_analysis"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.8 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with body_source."""
        return any(n.get('body_source') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Analyze lexical scopes.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from scope_analyzer import analyze_scopes, find_unused_definitions

            nodes_list = list(state.nodes.values())

            # Analyze scopes
            scope_results = analyze_scopes(nodes_list)

            # Find unused definitions
            unused = find_unused_definitions(nodes_list)

            # Update nodes
            scope_count = 0
            unused_count = 0

            for node_id, scope_info in scope_results.items():
                if node_id in state.nodes:
                    state.nodes[node_id]['scope_analysis'] = scope_info
                    scope_count += 1

            for node_id in unused:
                if node_id in state.nodes:
                    state.nodes[node_id]['is_unused'] = True
                    unused_count += 1

            state.metadata['scope_analysis'] = {
                'analyzed_nodes': scope_count,
                'unused_definitions': unused_count,
            }

            print(f"   → {scope_count} scopes analyzed, {unused_count} unused definitions")

        except ImportError as e:
            print(f"   → Scope analysis skipped: {e}")

        return state
