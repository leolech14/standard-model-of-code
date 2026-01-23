"""
Stage 1: Base Analysis

Performs the initial AST extraction and graph construction.
This is the foundation stage that all other stages build upon.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class BaseAnalysisStage(BaseStage):
    """
    Stage 1: Base Analysis - AST extraction and initial graph.

    Input: Empty CodebaseState with target_path set
    Output: CodebaseState with nodes and edges populated

    Uses unified_analyzer.analyze() internally.
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize with analysis options.

        Args:
            options: Options to pass to analyze() (exclude paths, etc.)
        """
        self._options = options or {}

    @property
    def name(self) -> str:
        return "base_analysis"

    @property
    def stage_number(self) -> int:
        return 1

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have a target path."""
        return bool(state.target_path)

    def validate_output(self, state: "CodebaseState") -> bool:
        """Validate we produced nodes."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Execute base analysis on the target path.

        Extracts AST, builds initial node/edge graph.
        """
        # Import from parent package
        import sys
        from pathlib import Path
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))
        from unified_analysis import analyze

        # Prepare options
        analysis_options = dict(self._options)
        analysis_options.pop("roadmap", None)

        # Run analysis
        result = analyze(
            state.target_path,
            output_dir=None,
            write_output=False,
            **analysis_options
        )

        # Extract results (handle both object and dict returns)
        nodes = result.nodes if hasattr(result, 'nodes') else result.get('nodes', [])
        edges = result.edges if hasattr(result, 'edges') else result.get('edges', [])

        # Load into state
        state.load_initial_graph(nodes, edges)

        # Store additional metadata
        state.metadata["stats"] = (
            getattr(result, 'stats', {})
            if hasattr(result, 'stats')
            else result.get('stats', {})
        )
        state.metadata["classification"] = (
            getattr(result, 'classification', {})
            if hasattr(result, 'classification')
            else result.get('classification', {})
        )
        state.metadata["auto_discovery"] = (
            getattr(result, 'auto_discovery', {})
            if hasattr(result, 'auto_discovery')
            else result.get('auto_discovery', {})
        )
        state.metadata["dependencies"] = (
            getattr(result, 'dependencies', {})
            if hasattr(result, 'dependencies')
            else result.get('dependencies', {})
        )
        state.metadata["architecture"] = (
            getattr(result, 'architecture', {})
            if hasattr(result, 'architecture')
            else result.get('architecture', {})
        )

        print(f"   → {len(state.nodes)} nodes, {len(state.edges)} edges")

        return state
