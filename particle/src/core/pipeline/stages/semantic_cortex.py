"""
Stage 11: Semantic Cortex

Extracts semantic concepts and business domain themes.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class SemanticCortexStage(BaseStage):
    """
    Stage 11: Semantic Cortex.

    Input: CodebaseState with nodes
    Output: CodebaseState with semantic concepts

    Extracts:
    - Business domain concepts
    - Technical themes
    - Naming patterns
    - Semantic clusters
    """

    @property
    def name(self) -> str:
        return "semantic_cortex"

    @property
    def stage_number(self) -> Optional[int]:
        return 11

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Extract semantic concepts.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from semantic_cortex import ConceptExtractor

            extractor = ConceptExtractor()
            nodes_list = list(state.nodes.values())

            semantic = extractor.extract(nodes_list)

            state.metadata['semantic'] = semantic

            concepts = semantic.get('concepts', [])
            themes = semantic.get('themes', [])
            print(f"   → {len(concepts)} concepts, {len(themes)} themes extracted")

        except Exception as e:
            print(f"   → Semantic cortex skipped: {e}")

        return state
