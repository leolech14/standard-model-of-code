"""
Stage 3.6: System Purpose (π₄)

Infers file-level purpose from contained organelles.
File purpose emerges from class/function purposes.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class SystemPurposeStage(BaseStage):
    """
    Stage 3.6: System Purpose (π₄).

    Input: CodebaseState with organelle purposes (π₃)
    Output: CodebaseState with file purposes (π₄)

    Purpose emergence: π₃ (organelles) → π₄ (files/systems)
    """

    @property
    def name(self) -> str:
        return "system_purpose"

    @property
    def stage_number(self) -> Optional[int]:
        return 3  # 3.6 maps to phase 3

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes with organelle purpose."""
        return any(n.get('organelle_purpose') or n.get('purpose') for n in state.nodes.values())

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Compute system-level purpose from organelle purposes.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from purpose_emergence import compute_pi4

            nodes_list = list(state.nodes.values())
            pi4_results = compute_pi4(nodes_list)

            file_count = 0
            for file_path, pi4_info in pi4_results.items():
                # Store in metadata since files aren't nodes
                state.metadata.setdefault('file_purposes', {})[file_path] = pi4_info
                file_count += 1

            print(f"   → {file_count} files with emergent purpose (π₄)")

        except ImportError as e:
            # Fallback: aggregate by file_path
            file_purposes = {}
            for node in state.nodes.values():
                fp = node.get('file_path')
                if not fp:
                    continue

                purpose = node.get('organelle_purpose') or node.get('purpose')
                if purpose:
                    if fp not in file_purposes:
                        file_purposes[fp] = {}
                    file_purposes[fp][purpose] = file_purposes[fp].get(purpose, 0) + 1

            # Assign dominant purpose per file
            for fp, purposes in file_purposes.items():
                dominant = max(purposes.items(), key=lambda x: x[1])
                file_purposes[fp] = {
                    'purpose': dominant[0],
                    'confidence': dominant[1] / sum(purposes.values()),
                }

            state.metadata['file_purposes'] = file_purposes
            print(f"   → {len(file_purposes)} files with purpose (fallback)")

        return state
