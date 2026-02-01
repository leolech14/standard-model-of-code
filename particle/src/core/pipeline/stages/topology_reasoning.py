"""
Stage 10: Visual Reasoning / Topology Classification

Classifies the overall graph topology shape.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class TopologyReasoningStage(BaseStage):
    """
    Stage 10: Topology Reasoning.

    Input: CodebaseState with nodes and edges
    Output: CodebaseState with topology classification

    Classifies topology as:
    - Star: Central hub with spokes
    - Mesh: Highly interconnected
    - Islands: Disconnected clusters
    - Tree: Hierarchical
    - Chain: Linear sequence
    """

    @property
    def name(self) -> str:
        return "topology_reasoning"

    @property
    def stage_number(self) -> Optional[int]:
        return 10

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have nodes and edges."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Classify graph topology.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            from topology_reasoning import TopologyClassifier

            classifier = TopologyClassifier()
            nodes_list = list(state.nodes.values())

            topology = classifier.classify(nodes_list, state.edges)

            state.metadata['topology'] = topology

            shape = topology.get('shape', 'unknown')
            confidence = topology.get('confidence', 0)
            print(f"   → Topology: {shape} (confidence: {confidence:.1%})")

        except Exception as e:
            print(f"   → Topology reasoning skipped: {e}")

        return state
