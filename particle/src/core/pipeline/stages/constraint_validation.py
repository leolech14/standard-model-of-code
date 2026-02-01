"""
Stage 8.5: Constraint Validation

Validates architectural constraints and detects violations.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class ConstraintValidationStage(BaseStage):
    """
    Stage 8.5: Constraint Validation.

    Input: CodebaseState with enriched nodes
    Output: CodebaseState with constraint violations

    Validates:
    - Layer boundary violations
    - Circular dependency constraints
    - Naming conventions
    - Architecture rules
    """

    @property
    def name(self) -> str:
        return "constraint_validation"

    @property
    def stage_number(self) -> Optional[int]:
        return 8  # 8.5 maps to phase 8

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes and edges."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Validate architectural constraints.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from constraint_engine import ConstraintEngine

            engine = ConstraintEngine()
            nodes_list = list(state.nodes.values())

            report = engine.validate(nodes_list, state.edges)

            state.metadata['constraints'] = report

            violations = report.get('violations', [])
            print(f"   → {len(violations)} constraint violations")

            # Mark violated nodes
            for v in violations:
                node_id = v.get('node_id')
                if node_id and node_id in state.nodes:
                    state.nodes[node_id].setdefault('violations', []).append(v)

        except Exception as e:
            print(f"   → Constraint validation skipped: {e}")

        return state
