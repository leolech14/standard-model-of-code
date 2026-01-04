"""
Visualization Generator
=======================

Generates HTML visualization from proof results.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class VisualizationGenerator:
    """Generates HTML visualization with embedded data."""

    def __init__(self, template_path: Optional[Path] = None):
        if template_path:
            self.template_path = template_path
        else:
            # Default: look in src/collider_viz.html
            repo_root = Path(__file__).resolve().parent.parent.parent
            self.template_path = repo_root / "collider_viz.html"

    def generate(
        self,
        state,
        classification_stats: Dict[str, Any],
        output_dir: Path
    ) -> Optional[Path]:
        """
        Generate HTML visualization report.

        Args:
            state: CodebaseState with enriched nodes/edges
            classification_stats: Stats from classification stage
            output_dir: Directory to write the report

        Returns:
            Path to generated report, or None on failure
        """
        if not self.template_path.exists():
            print(f"  Template not found at {self.template_path}")
            return None

        # Export data from state
        export_data = state.export()
        viz_data = {
            "particles": export_data['nodes'],
            "connections": export_data['edges'],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "stats": classification_stats
            }
        }

        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Inject data
        injected_html = self._inject_data(html_content, viz_data)
        if not injected_html:
            return None

        # Write output
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "collider_report.html"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(injected_html)

        return report_path

    def _inject_data(self, html_content: str, viz_data: Dict) -> Optional[str]:
        """Inject visualization data into HTML template."""
        start_marker = "/* <!-- DATA_INJECTION_START --> */"
        end_marker = "/* <!-- DATA_INJECTION_END --> */"

        if start_marker not in html_content or end_marker not in html_content:
            print("  Injection markers not found in template")
            return None

        # Safe JSON serialization for HTML embedding
        def safe_json_dumps(obj):
            return json.dumps(obj).replace('<', '\\u003c').replace('>', '\\u003e').replace('/', '\\u002f')

        # Construct injection block
        injection_block = f"""
    const particles = {safe_json_dumps(viz_data['particles'])};
    const connections = {safe_json_dumps(viz_data['connections'])};
    const vizMetadata = {safe_json_dumps(viz_data['metadata'])};
        """

        # Replace marker content
        parts_before = html_content.split(start_marker)[0]
        parts_after = html_content.split(end_marker)[1]
        return parts_before + start_marker + injection_block + end_marker + parts_after


def enrich_state_with_results(
    state,
    purpose_field=None,
    exec_flow=None,
    perf_profile=None
):
    """
    Enrich CodebaseState with analysis results.

    Args:
        state: CodebaseState instance
        purpose_field: Purpose field detection result
        exec_flow: Execution flow detection result
        perf_profile: Performance prediction result
    """
    # Enrich with purpose field data
    if purpose_field and hasattr(purpose_field, 'nodes'):
        for node in purpose_field.nodes.values():
            layer_val = node.layer.value if hasattr(node.layer, 'value') else str(node.layer)
            state.enrich_node(
                node.id,
                "purpose",
                layer=layer_val,
                composite_purpose=getattr(node, 'composite_purpose', None)
            )

    # Enrich with execution flow data
    if exec_flow and hasattr(exec_flow, 'orphans'):
        for orphan_id in exec_flow.orphans:
            state.enrich_node(orphan_id, "flow", is_orphan=True)

    # Enrich with performance data
    if perf_profile and hasattr(perf_profile, 'nodes'):
        for nid, pnode in perf_profile.nodes.items():
            is_hotspot = pnode.hotspot_score > 50
            state.enrich_node(
                nid,
                "performance",
                hotspot_score=pnode.hotspot_score,
                is_hotspot=is_hotspot
            )

    # Final polish (labels, defaults)
    for nid, node in state.nodes.items():
        if 'layer' not in node:
            state.enrich_node(nid, "default", layer="unknown")

        label = node.get('name', '').split('.')[-1]
        state.enrich_node(nid, "ui", label=label)
