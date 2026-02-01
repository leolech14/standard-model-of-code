"""
Stage 2.5: Ecosystem Discovery

Detects ecosystem-specific atoms (React hooks, Django models, etc.)
that require T2 pattern recognition beyond the base Standard Model.
"""

from typing import TYPE_CHECKING, Optional

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class EcosystemDiscoveryStage(BaseStage):
    """
    Stage 2.5: Ecosystem Discovery.

    Input: CodebaseState with Standard Model enrichment
    Output: CodebaseState with ecosystem-specific atom classifications

    Detects T2 patterns:
    - React hooks (useState, useEffect, etc.)
    - Django models, views, serializers
    - FastAPI endpoints
    - pytest fixtures
    - And 250+ other ecosystem patterns
    """

    @property
    def name(self) -> str:
        return "ecosystem_discovery"

    @property
    def stage_number(self) -> Optional[int]:
        return 2  # 2.5 maps to phase 2

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have enriched nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Discover ecosystem-specific atoms.
        """
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        try:
            # Try to use discovery engine if available
            from discovery_engine import discover_ecosystem_unknowns

            nodes_list = list(state.nodes.values())
            enriched_nodes = discover_ecosystem_unknowns(nodes_list)

            t2_count = 0
            for node in enriched_nodes:
                node_id = node.get('id')
                if node_id and node_id in state.nodes:
                    # Check if ecosystem atom was added
                    if node.get('ecosystem_atom'):
                        state.nodes[node_id]['ecosystem_atom'] = node['ecosystem_atom']
                        t2_count += 1

            print(f"   → {t2_count} nodes with ecosystem-specific atoms")

        except ImportError:
            # Fallback: detect common patterns manually
            t2_count = 0
            for node_id, node in state.nodes.items():
                body = node.get('body_source', '')
                name = node.get('name', '')
                file_path = node.get('file_path', '')

                ecosystem_atom = None

                # React patterns
                if 'useState' in body or 'useEffect' in body:
                    ecosystem_atom = 'REACT.HOOK'
                elif name.startswith('use') and node.get('kind') == 'function':
                    ecosystem_atom = 'REACT.CUSTOM_HOOK'

                # Django patterns
                if 'models.Model' in body:
                    ecosystem_atom = 'DJANGO.MODEL'
                elif '@api_view' in body or 'APIView' in body:
                    ecosystem_atom = 'DJANGO.VIEW'

                # FastAPI patterns
                if '@app.get' in body or '@app.post' in body or '@router' in body:
                    ecosystem_atom = 'FASTAPI.ENDPOINT'

                # pytest patterns
                if '@pytest.fixture' in body or 'conftest' in file_path:
                    ecosystem_atom = 'PYTEST.FIXTURE'

                if ecosystem_atom:
                    state.nodes[node_id]['ecosystem_atom'] = ecosystem_atom
                    t2_count += 1

            print(f"   → {t2_count} nodes with ecosystem patterns (fallback detection)")

        return state
