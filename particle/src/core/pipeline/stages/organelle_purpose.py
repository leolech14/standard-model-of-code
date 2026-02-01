"""
Stage 3.5: Organelle Purpose (π₃)

Infers container-level purpose from contained particles.
Class purpose emerges from method purposes.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class OrganellePurposeStage(BaseStage):
    """
    Stage 3.5: Organelle Purpose (π₃).

    Input: CodebaseState with particle purposes (π₂)
    Output: CodebaseState with organelle purposes (π₃)

    Purpose emergence: π₂ (particles) → π₃ (organelles/classes)
    """

    @property
    def name(self) -> str:
        return "organelle_purpose"

    @property
    def stage_number(self) -> Optional[int]:
        return 3  # 3.5 maps to phase 3

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with purpose."""
        return any(n.get('purpose') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute organelle-level purpose from particle purposes.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from purpose_emergence import compute_pi3

            nodes_list = list(state.nodes.values())
            pi3_results = compute_pi3(nodes_list)

            organelle_count = 0
            for node_id, pi3_info in pi3_results.items():
                if node_id in state.nodes:
                    state.nodes[node_id]['organelle_purpose'] = pi3_info.get('purpose')
                    state.nodes[node_id]['organelle_confidence'] = pi3_info.get('confidence', 0)
                    organelle_count += 1

            print(f"   → {organelle_count} organelles with emergent purpose (π₃)")

        except ImportError as e:
            # Fallback: aggregate purposes for classes
            classes = [n for n in state.nodes.values() if n.get('kind') == 'class']
            organelle_count = 0

            for cls in classes:
                cls_id = cls.get('id')
                # Find methods belonging to this class
                methods = [n for n in state.nodes.values()
                          if n.get('parent') == cls_id and n.get('purpose')]

                if methods:
                    # Aggregate purposes
                    purpose_counts = {}
                    for m in methods:
                        p = m.get('purpose')
                        purpose_counts[p] = purpose_counts.get(p, 0) + 1

                    # Dominant purpose
                    dominant = max(purpose_counts.items(), key=lambda x: x[1])
                    state.nodes[cls_id]['organelle_purpose'] = dominant[0]
                    state.nodes[cls_id]['organelle_confidence'] = dominant[1] / len(methods)
                    organelle_count += 1

            print(f"   → {organelle_count} organelles with purpose (fallback)")

        return state
