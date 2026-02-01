"""
Stage 6.8: Codome Boundaries

Generates synthetic nodes for external callers (test frameworks, CLI, etc.)
that we can't see in the analyzed codebase.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class CodomeBoundaryStage(BaseStage):
    """
    Stage 6.8: Codome Boundaries.

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with codome boundary nodes and inferred edges

    Creates synthetic boundary nodes:
    - __codome__::test_entry (pytest/jest)
    - __codome__::entry_point (__main__, CLI)
    - __codome__::framework_managed (decorators, DI)
    - __codome__::cross_language (JS from HTML)
    - __codome__::external_boundary (public API)
    - __codome__::dynamic_target (reflection)
    """

    @property
    def name(self) -> str:
        return "codome_boundary"

    @property
    def stage_number(self) -> Optional[int]:
        return 6  # 6.8 maps to phase 6

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Create codome boundary nodes.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from full_analysis import create_codome_boundaries

            nodes_list = list(state.nodes.values())
            codome_result = create_codome_boundaries(nodes_list, state.edges)

            # Add boundary nodes to state
            boundary_nodes = codome_result.get('boundary_nodes', [])
            for bn in boundary_nodes:
                bn_id = bn.get('id')
                if bn_id:
                    state.nodes[bn_id] = bn

            # Add inferred edges
            inferred_edges = codome_result.get('inferred_edges', [])
            for edge in inferred_edges:
                state.edges.append(edge)

            state.metadata['codome'] = {
                'boundary_nodes': len(boundary_nodes),
                'inferred_edges': len(inferred_edges),
                'categories': codome_result.get('categories', {}),
            }

            print(f"   → {len(boundary_nodes)} boundary nodes, {len(inferred_edges)} inferred edges")

        except Exception as e:
            print(f"   → Codome boundaries skipped: {e}")

        return state
