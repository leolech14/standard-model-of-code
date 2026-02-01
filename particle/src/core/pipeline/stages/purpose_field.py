"""
Stage 3: Purpose Field

Assigns architectural purpose to each node based on its characteristics.
The Purpose Field is a core SMOC concept representing the "why" of code.
"""

from typing import TYPE_CHECKING

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class PurposeFieldStage(BaseStage):
    """
    Stage 3: Purpose Field Assignment.

    Input: CodebaseState with Standard Model enrichment
    Output: CodebaseState with purpose classifications

    Adds:
    - purpose: Primary architectural purpose
    - purpose_score: Confidence in purpose assignment
    - architectural_role: How node fits in overall architecture
    """

    @property
    def name(self) -> str:
        return "purpose_field"

    @property
    def stage_number(self) -> int:
        return 3

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have enriched nodes."""
        # Need at least some nodes with role/atom
        has_enrichment = any(
            n.get('role') or n.get('atom')
            for n in state.nodes.values()
        )
        return has_enrichment

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Assign purpose field to nodes.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))
        from purpose_field import detect_purpose_field

        # Get nodes as list
        nodes_list = list(state.nodes.values())
        edges_list = state.edges

        # Detect purpose field
        purpose_field = detect_purpose_field(nodes_list, edges_list)

        # Store purpose field summary in state metadata
        summary = purpose_field.summary()
        state.metadata['purpose_field'] = summary

        # Update nodes with purpose information from the field
        purpose_count = 0
        for node_id in state.nodes:
            if node_id in purpose_field.nodes:
                pf_node = purpose_field.nodes[node_id]
                state.nodes[node_id]['purpose'] = pf_node.atomic_purpose
                state.nodes[node_id]['purpose_confidence'] = pf_node.atomic_confidence
                state.nodes[node_id]['coherence_score'] = pf_node.coherence_score
                purpose_count += 1

        print(f"   → {purpose_count} nodes with purpose, {summary.get('god_class_count', 0)} god classes")

        return state
