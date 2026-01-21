#!/usr/bin/env python3
"""
Present Architect
=================
Analyze the CURRENT state of the codebase using Collider + Gemini.

This tool:
1. Runs Collider analysis on the active codebase
2. Uses File Search stores for semantic context
3. Generates a comprehensive "State of the Codebase" report
4. Identifies health metrics, hot spots, and recommendations

Usage:
  # Full present-state analysis
  python present_architect.py --output architecture_report/

  # Quick health check
  python present_architect.py --quick

  # Focus on specific area
  python present_architect.py --focus "visualization"
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import subprocess

# Auto-detect venv
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
TOOLS_VENV = PROJECT_ROOT / ".tools_venv"
VENV_PYTHON = TOOLS_VENV / "bin" / "python"

if TOOLS_VENV.as_posix() not in sys.prefix:
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)
    else:
        print("ERROR: .tools_venv not found.")
        sys.exit(1)

import argparse
from google import genai
from typing import Dict, Any, Optional


# =============================================================================
# COLLIDER INTEGRATION
# =============================================================================

def run_collider_analysis(target_dir: Path, output_dir: Path) -> Optional[Dict]:
    """Run Collider analysis on the target directory."""
    collider_path = PROJECT_ROOT / "standard-model-of-code"
    collider_script = collider_path / "collider"

    if not collider_script.exists():
        print(f"  Warning: Collider not found at {collider_script}")
        return None

    print(f"  Running Collider on {target_dir}...")

    try:
        result = subprocess.run(
            [str(collider_script), "full", str(target_dir), "--output", str(output_dir)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(collider_path)
        )

        if result.returncode != 0:
            print(f"  Collider error: {result.stderr[:500]}")
            return None

        # Load the unified analysis
        analysis_file = output_dir / "unified_analysis.json"
        if analysis_file.exists():
            return json.loads(analysis_file.read_text())

    except subprocess.TimeoutExpired:
        print("  Collider timed out")
    except Exception as e:
        print(f"  Collider failed: {e}")

    return None


# =============================================================================
# FILE SEARCH INTEGRATION
# =============================================================================

def create_gemini_client():
    """Create Gemini client using API key."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set")
        return None
    return genai.Client(api_key=api_key)


def query_file_search(client, store_name: str, query: str) -> Optional[str]:
    """Query a File Search store and return the response."""
    from google.genai import types

    try:
        # First get the store resource name
        stores = list(client.file_search_stores.list())
        store_resource = None
        for store in stores:
            if store.display_name == store_name:
                store_resource = store.name
                break

        if not store_resource:
            return None

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_resource]
                    )
                )]
            )
        )
        return response.text

    except Exception as e:
        print(f"  File Search error: {e}")
        return None


# =============================================================================
# HEALTH METRICS
# =============================================================================

def calculate_health_metrics(collider_data: Dict) -> Dict:
    """Calculate health metrics from Collider analysis."""
    nodes = collider_data.get('nodes', [])
    edges = collider_data.get('edges', [])
    stats = collider_data.get('statistics', {})

    # Basic metrics
    node_count = len(nodes)
    edge_count = len(edges)

    # Role distribution
    role_counts = {}
    for node in nodes:
        role = node.get('role', 'unknown')
        role_counts[role] = role_counts.get(role, 0) + 1

    # Layer distribution
    layer_counts = {}
    for node in nodes:
        layer = node.get('layer', 'unknown')
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    # Calculate complexity score
    avg_edges_per_node = edge_count / node_count if node_count > 0 else 0

    # Dead code percentage
    dead_code_pct = stats.get('dead_code_percentage', 0)

    # Find hot spots (nodes with many incoming edges)
    incoming_edges = {}
    for edge in edges:
        target = edge.get('target', '')
        incoming_edges[target] = incoming_edges.get(target, 0) + 1

    hot_spots = sorted(
        [(k, v) for k, v in incoming_edges.items()],
        key=lambda x: -x[1]
    )[:10]

    return {
        'node_count': node_count,
        'edge_count': edge_count,
        'avg_edges_per_node': round(avg_edges_per_node, 2),
        'dead_code_percentage': dead_code_pct,
        'role_distribution': role_counts,
        'layer_distribution': layer_counts,
        'hot_spots': hot_spots,
        'health_score': calculate_health_score(
            node_count, edge_count, dead_code_pct, avg_edges_per_node
        )
    }


def calculate_health_score(nodes: int, edges: int, dead_code: float, avg_edges: float) -> str:
    """Calculate overall health score (A-F)."""
    score = 100

    # Penalize high dead code
    if dead_code > 20:
        score -= 30
    elif dead_code > 10:
        score -= 15
    elif dead_code > 5:
        score -= 5

    # Penalize high complexity
    if avg_edges > 10:
        score -= 20
    elif avg_edges > 5:
        score -= 10

    # Grade
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'


# =============================================================================
# SEMANTIC ANALYSIS
# =============================================================================

def analyze_architecture_semantically(client, metrics: Dict, focus: str = None) -> Dict:
    """Use Gemini to analyze the architecture semantically."""

    # Query File Search for known issues
    known_debt = query_file_search(
        client,
        "collider-docs",
        "What architecture debt and technical issues are documented?"
    )

    # Build analysis prompt
    focus_clause = f" Focus especially on: {focus}" if focus else ""

    prompt = f"""Analyze this codebase's current architecture.{focus_clause}

METRICS:
- Nodes: {metrics['node_count']}
- Edges: {metrics['edge_count']}
- Avg edges per node: {metrics['avg_edges_per_node']}
- Dead code: {metrics['dead_code_percentage']}%
- Health Score: {metrics['health_score']}

ROLE DISTRIBUTION:
{json.dumps(metrics['role_distribution'], indent=2)}

LAYER DISTRIBUTION:
{json.dumps(metrics['layer_distribution'], indent=2)}

HOT SPOTS (most connected nodes):
{json.dumps(metrics['hot_spots'][:5], indent=2)}

KNOWN DOCUMENTED ISSUES:
{known_debt or 'None available'}

Provide a comprehensive analysis in JSON format:
{{
  "overall_assessment": "...",
  "strengths": ["...", "..."],
  "concerns": ["...", "..."],
  "recommendations": [
    {{"priority": "high/medium/low", "action": "...", "rationale": "..."}}
  ],
  "architecture_pattern": "...",
  "technical_debt_estimate": "low/medium/high/critical"
}}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# REPORT GENERATION
# =============================================================================

def generate_architecture_report(
    metrics: Dict,
    semantic_analysis: Dict,
    output_dir: Path
):
    """Generate comprehensive architecture report."""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Architecture Report - Present State</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            padding: 40px;
        }}
        h1 {{ color: #00d4ff; margin-bottom: 10px; }}
        .subtitle {{ color: #888; margin-bottom: 40px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
        }}
        .card h3 {{ color: #00d4ff; margin-bottom: 15px; font-size: 0.9em; text-transform: uppercase; }}
        .metric {{ font-size: 3em; font-weight: 700; color: #fff; }}
        .metric-label {{ color: #888; font-size: 0.9em; }}
        .health-score {{
            font-size: 5em;
            font-weight: 700;
            text-align: center;
            padding: 20px;
        }}
        .health-A {{ color: #00ff88; }}
        .health-B {{ color: #88ff00; }}
        .health-C {{ color: #ffff00; }}
        .health-D {{ color: #ff8800; }}
        .health-F {{ color: #ff0044; }}
        .list {{ list-style: none; }}
        .list li {{ padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
        .list li:last-child {{ border: none; }}
        .tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 8px;
        }}
        .tag-high {{ background: rgba(255,0,68,0.2); color: #ff4488; }}
        .tag-medium {{ background: rgba(255,136,0,0.2); color: #ff8800; }}
        .tag-low {{ background: rgba(0,212,255,0.2); color: #00d4ff; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #fff; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .assessment {{ font-size: 1.2em; line-height: 1.6; color: #ccc; }}
    </style>
</head>
<body>
    <h1>Architecture Report</h1>
    <p class="subtitle">Present state analysis - Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

    <div class="grid">
        <div class="card">
            <h3>Health Score</h3>
            <div class="health-score health-{metrics['health_score']}">{metrics['health_score']}</div>
        </div>
        <div class="card">
            <h3>Nodes</h3>
            <div class="metric">{metrics['node_count']:,}</div>
            <div class="metric-label">code elements</div>
        </div>
        <div class="card">
            <h3>Edges</h3>
            <div class="metric">{metrics['edge_count']:,}</div>
            <div class="metric-label">relationships</div>
        </div>
        <div class="card">
            <h3>Dead Code</h3>
            <div class="metric">{metrics['dead_code_percentage']}%</div>
            <div class="metric-label">unreachable</div>
        </div>
    </div>

    <div class="section">
        <h2>Assessment</h2>
        <p class="assessment">{semantic_analysis.get('overall_assessment', 'No assessment available')}</p>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Strengths</h3>
            <ul class="list">
"""

    for strength in semantic_analysis.get('strengths', []):
        html += f"                <li>{strength}</li>\n"

    html += """
            </ul>
        </div>
        <div class="card">
            <h3>Concerns</h3>
            <ul class="list">
"""

    for concern in semantic_analysis.get('concerns', []):
        html += f"                <li>{concern}</li>\n"

    html += """
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ul class="list">
"""

    for rec in semantic_analysis.get('recommendations', []):
        priority = rec.get('priority', 'medium')
        html += f"""            <li>
                <span class="tag tag-{priority}">{priority.upper()}</span>
                <strong>{rec.get('action', '')}</strong>
                <br><small style="color: #888;">{rec.get('rationale', '')}</small>
            </li>
"""

    html += f"""
        </ul>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Hot Spots</h3>
            <ul class="list">
"""

    for name, count in metrics['hot_spots'][:7]:
        html += f"                <li><code>{name}</code> - {count} connections</li>\n"

    html += """
            </ul>
        </div>
        <div class="card">
            <h3>Architecture Pattern</h3>
            <div class="metric" style="font-size: 1.5em;">"""

    html += semantic_analysis.get('architecture_pattern', 'Unknown')

    html += f"""</div>
            <div class="metric-label">Technical Debt: {semantic_analysis.get('technical_debt_estimate', 'unknown')}</div>
        </div>
    </div>

</body>
</html>
"""

    report_file = output_dir / "architecture_report.html"
    report_file.write_text(html)
    return report_file


# =============================================================================
# MAIN
# =============================================================================

def run_present_analysis(
    target_dir: Path,
    output_dir: Path,
    quick: bool = False,
    focus: str = None
):
    """Run the full present-state analysis."""

    print("=" * 60)
    print("PRESENT ARCHITECT")
    print("=" * 60)
    print(f"Target: {target_dir}")
    print(f"Output: {output_dir}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)
    collider_output = output_dir / "collider_analysis"

    # Step 1: Run Collider
    print("STEP 1: Collider Analysis")
    print("-" * 40)

    collider_data = run_collider_analysis(target_dir, collider_output)

    if not collider_data:
        # Try to load existing analysis
        existing = output_dir / "collider_analysis" / "unified_analysis.json"
        if existing.exists():
            print("  Using existing Collider analysis")
            collider_data = json.loads(existing.read_text())
        else:
            print("  ERROR: No Collider data available")
            sys.exit(1)

    print(f"  Found {len(collider_data.get('nodes', []))} nodes")
    print()

    # Step 2: Calculate Metrics
    print("STEP 2: Health Metrics")
    print("-" * 40)

    metrics = calculate_health_metrics(collider_data)
    print(f"  Health Score: {metrics['health_score']}")
    print(f"  Dead Code: {metrics['dead_code_percentage']}%")
    print(f"  Avg Complexity: {metrics['avg_edges_per_node']} edges/node")
    print()

    # Step 3: Semantic Analysis (skip in quick mode)
    semantic_analysis = {}
    if not quick:
        print("STEP 3: Semantic Analysis")
        print("-" * 40)

        client = create_gemini_client()
        if client:
            semantic_analysis = analyze_architecture_semantically(client, metrics, focus)
            print(f"  Pattern: {semantic_analysis.get('architecture_pattern', 'unknown')}")
            print(f"  Debt Level: {semantic_analysis.get('technical_debt_estimate', 'unknown')}")
        else:
            print("  Skipped (no API key)")
        print()

    # Step 4: Generate Report
    print("STEP 4: Generate Report")
    print("-" * 40)

    report_file = generate_architecture_report(metrics, semantic_analysis, output_dir)
    print(f"  Created: {report_file}")

    # Save JSON data
    data_file = output_dir / "architecture_data.json"
    data_file.write_text(json.dumps({
        'generated_at': datetime.now().isoformat(),
        'metrics': metrics,
        'semantic_analysis': semantic_analysis
    }, indent=2, default=str))
    print(f"  Created: {data_file}")

    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

    return metrics, semantic_analysis


def main():
    parser = argparse.ArgumentParser(description="Analyze current codebase architecture")
    parser.add_argument("--target", "-t", default="standard-model-of-code", help="Directory to analyze")
    parser.add_argument("--output", "-o", default="architecture_report", help="Output directory")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode (skip semantic analysis)")
    parser.add_argument("--focus", "-f", help="Focus area (e.g., 'visualization', 'pipeline')")

    args = parser.parse_args()

    target = Path(args.target)
    if not target.is_absolute():
        target = PROJECT_ROOT / target

    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / output

    run_present_analysis(
        target_dir=target,
        output_dir=output,
        quick=args.quick,
        focus=args.focus
    )


if __name__ == "__main__":
    main()
