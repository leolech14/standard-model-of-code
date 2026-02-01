"""
Stage 12: Output Generation

Generates final artifacts (JSON, HTML, Markdown).
"""

from typing import TYPE_CHECKING, Optional
from pathlib import Path

from ..base_stage import BaseStage

if TYPE_CHECKING:
    from ...data_management import CodebaseState


class OutputGenerationStage(BaseStage):
    """
    Stage 12: Output Generation.

    Input: CodebaseState with all analysis results
    Output: CodebaseState (unchanged) + generated files

    Generates:
    - unified_analysis.json (structured data)
    - collider_report.html (interactive visualization)
    - output.md (Brain Download markdown report)
    """

    def __init__(self, output_dir: Optional[str] = None, skip_html: bool = False):
        """
        Initialize output generation stage.

        Args:
            output_dir: Directory for output files
            skip_html: Skip HTML generation
        """
        self._output_dir = output_dir
        self._skip_html = skip_html

    @property
    def name(self) -> str:
        return "output_generation"

    @property
    def stage_number(self) -> Optional[int]:
        return 12

    def validate_input(self, state: "CodebaseState") -> bool:
        """Validate we have analysis results."""
        return len(state.nodes) > 0

    def execute(self, state: "CodebaseState") -> "CodebaseState":
        """
        Generate output artifacts.
        """
        import sys
        import json
        from datetime import datetime
        core_path = Path(__file__).parent.parent.parent
        if str(core_path) not in sys.path:
            sys.path.insert(0, str(core_path))

        # Determine output directory
        if self._output_dir:
            output_dir = Path(self._output_dir)
        else:
            output_dir = Path(state.target_path) / '.collider'

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate unified_analysis.json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = Path(state.target_path).name

        json_output = {
            'project': project_name,
            'timestamp': timestamp,
            'nodes': list(state.nodes.values()),
            'edges': state.edges,
            'metadata': state.metadata,
        }

        json_path = output_dir / 'unified_analysis.json'
        with open(json_path, 'w') as f:
            json.dump(json_output, f, indent=2, default=str)

        print(f"   → JSON: {json_path}")

        # Generate Brain Download markdown
        try:
            from brain_download import generate_brain_download

            md_content = generate_brain_download(json_output)
            md_path = output_dir / 'output.md'
            with open(md_path, 'w') as f:
                f.write(md_content)

            print(f"   → Markdown: {md_path}")

        except Exception as e:
            print(f"   → Markdown generation skipped: {e}")

        # Generate HTML visualization
        if not self._skip_html:
            try:
                # Use visualize_graph_webgl
                tools_path = core_path.parent.parent / 'tools'
                if str(tools_path) not in sys.path:
                    sys.path.insert(0, str(tools_path))

                from visualize_graph_webgl import generate_visualization

                html_path = output_dir / 'collider_report.html'
                generate_visualization(
                    json_path,
                    str(html_path),
                    project_name=project_name,
                )

                print(f"   → HTML: {html_path}")

            except Exception as e:
                print(f"   → HTML generation skipped: {e}")

        # Store output paths in metadata
        state.metadata['output_paths'] = {
            'json': str(json_path),
            'output_dir': str(output_dir),
        }

        return state
