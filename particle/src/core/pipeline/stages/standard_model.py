"""
Stage 2: Standard Model Enrichment

Enriches nodes with Standard Model classification (atoms, roles, dimensions).
This is the core semantic enrichment that makes SMOC unique.
"""

from typing import TYPE_CHECKING

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class StandardModelStage(BaseStage):
    """
    Stage 2: Standard Model Enrichment.

    Input: CodebaseState with raw nodes from Stage 1
    Output: CodebaseState with atom, role, dimension classifications

    Adds:
    - atom: Semantic atom (e.g., LOG.FNC.M, DAT.VAR.A)
    - role: Canonical role (e.g., ServiceEntry, DataHolder)
    - rpbl: Responsibility, Purity, Boundary, Lifecycle scores
    """

    @property
    def name(self) -> str:
        return "standard_model"

    @property
    def stage_number(self) -> int:
        return 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes to enrich."""
        return len(state.nodes) > 0

    def validate_output(self, state: "CodebaseState") -> bool:
        """Validate we enriched at least some nodes."""
        rpbl_count = sum(1 for n in state.nodes.values() if n.get('rpbl'))
        return rpbl_count > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Enrich nodes with Standard Model classification.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))
        from standard_model_enricher import enrich_with_standard_model

        # Get nodes as list for enricher
        nodes_list = list(state.nodes.values())

        # Enrich
        enriched_nodes = enrich_with_standard_model(nodes_list)

        # Update state with enriched data
        rpbl_count = 0
        for node in enriched_nodes:
            node_id = node.get('id')
            if node_id and node_id in state.nodes:
                # Update node in state
                state.nodes[node_id].update(node)

                # Flatten RPBL scores for UPB binding
                rpbl = node.get('rpbl', {})
                state.nodes[node_id]['rpbl_responsibility'] = rpbl.get('responsibility', 0)
                state.nodes[node_id]['rpbl_purity'] = rpbl.get('purity', 0)
                state.nodes[node_id]['rpbl_boundary'] = rpbl.get('boundary', 0)
                state.nodes[node_id]['rpbl_lifecycle'] = rpbl.get('lifecycle', 0)

                if rpbl:
                    rpbl_count += 1

        print(f"   → {rpbl_count} nodes with RPBL classification")

        return state
