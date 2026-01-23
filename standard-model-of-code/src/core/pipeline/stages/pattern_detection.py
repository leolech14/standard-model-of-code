"""
Stage 2.10: Pattern Detection

Detects T2 patterns (decorators, constructors, framework idioms).
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class PatternDetectionStage(BaseStage):
    """
    Stage 2.10: Pattern Detection.

    Input: CodebaseState with nodes
    Output: CodebaseState with pattern matches

    Detects:
    - Decorator patterns (@app.route, @pytest.fixture)
    - Constructor patterns (__init__, constructor)
    - Factory patterns
    - Singleton patterns
    - Observer patterns
    """

    @property
    def name(self) -> str:
        return "pattern_detection"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.10 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Detect code patterns.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from pattern_matcher import PatternMatcher

            matcher = PatternMatcher()
            nodes_list = list(state.nodes.values())

            pattern_counts = {}
            for node in nodes_list:
                patterns = matcher.match(node)
                if patterns:
                    node_id = node.get('id')
                    if node_id and node_id in state.nodes:
                        state.nodes[node_id]['patterns'] = patterns
                        for p in patterns:
                            pattern_counts[p] = pattern_counts.get(p, 0) + 1

            state.metadata['patterns'] = {
                'counts': pattern_counts,
                'total': sum(pattern_counts.values()),
            }

            top_patterns = sorted(pattern_counts.items(), key=lambda x: -x[1])[:3]
            top_str = ', '.join(f"{p}:{c}" for p, c in top_patterns)
            print(f"   → {sum(pattern_counts.values())} patterns detected: {top_str}")

        except ImportError as e:
            print(f"   → Pattern detection skipped: {e}")

        return state
