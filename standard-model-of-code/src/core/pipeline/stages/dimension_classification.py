"""
Stage 2.7: Dimension Classification

Assigns octahedral dimension coordinates to nodes:
- D4: BOUNDARY (internal/external/boundary)
- D5: STATE (stateless/stateful/transformative)
- D7: TIME (sync/async/scheduled)
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class DimensionClassificationStage(BaseStage):
    """
    Stage 2.7: Dimension Classification.

    Input: CodebaseState with Standard Model enrichment
    Output: CodebaseState with D4, D5, D7 dimension coordinates

    The 8-dimensional space is the core theoretical framework of SMOC.
    """

    @property
    def name(self) -> str:
        return "dimension_classification"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.7 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes to classify."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Classify nodes in 8D semantic space.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from dimension_classifier import classify_all_dimensions

            nodes_list = list(state.nodes.values())
            classified_nodes = classify_all_dimensions(nodes_list)

            dim_count = 0
            for node in classified_nodes:
                node_id = node.get('id')
                if node_id and node_id in state.nodes:
                    # Update dimensions
                    for dim in ['d4_boundary', 'd5_state', 'd7_time']:
                        if node.get(dim):
                            state.nodes[node_id][dim] = node[dim]
                            dim_count += 1

            print(f"   → {dim_count // 3} nodes with dimension coordinates")

        except ImportError:
            # Fallback classification
            dim_count = 0
            for node_id, node in state.nodes.items():
                body = node.get('body_source', '')
                name = node.get('name', '')

                # D4: BOUNDARY
                if any(p in name.lower() for p in ['api', 'endpoint', 'route', 'handler']):
                    state.nodes[node_id]['d4_boundary'] = 'EXTERNAL'
                elif name.startswith('_'):
                    state.nodes[node_id]['d4_boundary'] = 'INTERNAL'
                else:
                    state.nodes[node_id]['d4_boundary'] = 'BOUNDARY'

                # D5: STATE
                if 'self.' in body or 'this.' in body:
                    state.nodes[node_id]['d5_state'] = 'STATEFUL'
                elif '@staticmethod' in body or not ('self' in body or 'this' in body):
                    state.nodes[node_id]['d5_state'] = 'STATELESS'
                else:
                    state.nodes[node_id]['d5_state'] = 'TRANSFORMATIVE'

                # D7: TIME
                if 'async ' in body or 'await ' in body or 'Promise' in body:
                    state.nodes[node_id]['d7_time'] = 'ASYNC'
                elif '@scheduled' in body or 'cron' in body.lower():
                    state.nodes[node_id]['d7_time'] = 'SCHEDULED'
                else:
                    state.nodes[node_id]['d7_time'] = 'SYNC'

                dim_count += 1

            print(f"   → {dim_count} nodes with dimensions (fallback)")

        return state
