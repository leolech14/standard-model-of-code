"""
Stage 8.6: Purpose Intelligence (Q-Scores)

Calculates quality scores and purpose clarity metrics.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class PurposeIntelligenceStage(BaseStage):
    """
    Stage 8.6: Purpose Intelligence.

    Input: CodebaseState with purpose assignments
    Output: CodebaseState with Q-scores and intelligence metrics

    Calculates:
    - Q-score (quality metric per node)
    - Purpose clarity
    - Naming coherence
    - Responsibility alignment
    """

    @property
    def name(self) -> str:
        return "purpose_intelligence"

    @property
    def stage_number(self) -> Optional[int]:
        return 8  # 8.6 maps to phase 8

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with purpose."""
        return any(n.get('purpose') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Calculate purpose intelligence metrics.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from purpose_intelligence import enrich_nodes_with_intelligence

            nodes_list = list(state.nodes.values())
            enriched = enrich_nodes_with_intelligence(nodes_list)

            q_scores = []
            for node in enriched:
                node_id = node.get('id')
                if node_id and node_id in state.nodes:
                    q_score = node.get('q_score', 0)
                    state.nodes[node_id]['q_score'] = q_score
                    state.nodes[node_id]['purpose_clarity'] = node.get('purpose_clarity', 0)
                    q_scores.append(q_score)

            avg_q = sum(q_scores) / len(q_scores) if q_scores else 0
            state.metadata['intelligence'] = {
                'avg_q_score': avg_q,
                'total_scored': len(q_scores),
            }

            print(f"   → Average Q-score: {avg_q:.2f} across {len(q_scores)} nodes")

        except Exception as e:
            print(f"   → Purpose intelligence skipped: {e}")

        return state
