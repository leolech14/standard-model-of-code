"""
Stage 2.11: Data Flow Analysis (D6:EFFECT)

Classifies D6:EFFECT dimension (PURE/READ/WRITE/MUTATE) and calculates purity scores.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class DataFlowAnalysisStage(BaseStage):
    """
    Stage 2.11: Data Flow Analysis.

    Input: CodebaseState with nodes containing body_source
    Output: CodebaseState with d6_effect and purity_score

    Classifies:
    - PURE: No side effects
    - READ: Reads external state
    - WRITE: Writes external state
    - MUTATE: Modifies parameters
    """

    @property
    def name(self) -> str:
        return "data_flow_analysis"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.11 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with body_source."""
        return any(n.get('body_source') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Analyze data flow and classify effects.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from data_flow_analyzer import analyze_data_flow

            nodes_list = list(state.nodes.values())
            df_results = analyze_data_flow(nodes_list)

            effect_counts = {'PURE': 0, 'READ': 0, 'WRITE': 0, 'MUTATE': 0}

            for node_id, df_info in df_results.items():
                if node_id in state.nodes:
                    effect = df_info.get('d6_effect', 'PURE')
                    purity = df_info.get('purity_score', 1.0)

                    state.nodes[node_id]['d6_effect'] = effect
                    state.nodes[node_id]['purity_score'] = purity

                    effect_counts[effect] = effect_counts.get(effect, 0) + 1

            state.metadata['data_flow'] = {
                'effect_distribution': effect_counts,
                'pure_count': effect_counts.get('PURE', 0),
            }

            print(f"   → Effect distribution: {effect_counts}")

        except ImportError as e:
            print(f"   → Data flow analysis skipped: {e}")

        return state
