"""
Stage 4: Execution Flow / Edge Extraction

Extracts call relationships and builds the execution flow graph.
This stage enriches edges with call semantics.
"""

from typing import TYPE_CHECKING

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class EdgeExtractionStage(BaseStage):
    """
    Stage 4: Edge Extraction / Execution Flow.

    Input: CodebaseState with enriched nodes
    Output: CodebaseState with semantic edge classifications

    Enriches edges with:
    - family: Edge type family (calls, defines, imports, etc.)
    - weight: Edge importance weight
    - semantic_type: Detailed edge classification
    """

    @property
    def name(self) -> str:
        return "edge_extraction"

    @property
    def stage_number(self) -> int:
        return 4

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have edges to classify."""
        return len(state.edges) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Extract and classify execution flow edges.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))
        from edge_extractor import extract_call_edges

        # Extract additional call edges
        nodes_list = list(state.nodes.values())
        existing_edges = state.edges

        # Use tree-sitter based extraction if available
        try:
            new_edges = extract_call_edges(nodes_list, existing_edges)
            if new_edges:
                for edge in new_edges:
                    if edge not in state.edges:
                        state.edges.append(edge)
                print(f"   → Extracted {len(new_edges)} additional call edges")
        except Exception as e:
            print(f"   → Edge extraction skipped: {e}")

        # Classify edge families
        family_counts = {}
        for edge in state.edges:
            family = edge.get('family', 'unknown')
            family_counts[family] = family_counts.get(family, 0) + 1

        print(f"   → Edge families: {family_counts}")

        return state
