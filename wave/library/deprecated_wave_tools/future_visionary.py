#!/usr/bin/env python3
"""
Future Visionary
================
Project the FUTURE of the codebase based on past evolution and present state.

This tool:
1. Loads archaeological data (past evolution)
2. Loads architectural data (present state)
3. Queries documented roadmaps and debt
4. Synthesizes a future projection with actionable roadmap

Usage:
  # Generate future projection
  python future_visionary.py --output roadmap_report/

  # With specific time horizon
  python future_visionary.py --horizon 90  # 90 days

  # Focus on specific goal
  python future_visionary.py --goal "eliminate app.js monolith"
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

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
from typing import Dict, List, Optional


# =============================================================================
# DATA LOADING
# =============================================================================

def load_evolution_data(evolution_dir: Path) -> Optional[Dict]:
    """Load archaeological evolution data."""
    data_file = evolution_dir / "evolution_data.json"
    if data_file.exists():
        return json.loads(data_file.read_text())
    return None


def load_architecture_data(arch_dir: Path) -> Optional[Dict]:
    """Load present architecture data."""
    data_file = arch_dir / "architecture_data.json"
    if data_file.exists():
        return json.loads(data_file.read_text())
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
    """Query a File Search store."""
    from google.genai import types

    try:
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
        return None


# =============================================================================
# FUTURE PROJECTION
# =============================================================================

def synthesize_future_vision(
    client,
    evolution_data: Optional[Dict],
    architecture_data: Optional[Dict],
    horizon_days: int,
    goal: Optional[str]
) -> Dict:
    """Synthesize future projection from all available data."""

    # Query File Search for documented roadmaps and debt
    debt_info = query_file_search(
        client,
        "collider-docs",
        "What technical debt exists? What is the recommended refactoring approach?"
    )

    vision_info = query_file_search(
        client,
        "collider-docs",
        "What is the long-term vision for this project? What are the goals?"
    )

    # Build context
    evolution_summary = "No historical data available."
    if evolution_data:
        epochs = evolution_data.get('epochs', [])
        if epochs:
            recent = epochs[-3:] if len(epochs) >= 3 else epochs
            evolution_summary = "Recent evolution:\n" + "\n".join([
                f"- {e.get('semantic_analysis', {}).get('semantic_theme', 'Unknown')}: {e.get('semantic_analysis', {}).get('activity_type', 'unknown')}"
                for e in recent
            ])

    arch_summary = "No architecture data available."
    if architecture_data:
        metrics = architecture_data.get('metrics', {})
        analysis = architecture_data.get('semantic_analysis', {})
        arch_summary = f"""Current state:
- Health Score: {metrics.get('health_score', 'unknown')}
- Nodes: {metrics.get('node_count', 0)}
- Dead Code: {metrics.get('dead_code_percentage', 0)}%
- Pattern: {analysis.get('architecture_pattern', 'unknown')}
- Debt Level: {analysis.get('technical_debt_estimate', 'unknown')}
- Top Concerns: {', '.join(analysis.get('concerns', [])[:3])}"""

    goal_clause = f"\n\nSPECIFIC GOAL TO ACHIEVE: {goal}" if goal else ""

    prompt = f"""You are a software architect projecting the future of a codebase.

PAST EVOLUTION:
{evolution_summary}

PRESENT STATE:
{arch_summary}

DOCUMENTED TECHNICAL DEBT:
{debt_info or 'Not available'}

DOCUMENTED VISION:
{vision_info or 'Not available'}

TIME HORIZON: {horizon_days} days{goal_clause}

Based on all this information, create a detailed future projection and roadmap.

Respond in JSON:
{{
  "vision_statement": "One paragraph describing where this codebase should be in {horizon_days} days",
  "key_milestones": [
    {{"day": 30, "title": "...", "description": "..."}},
    {{"day": 60, "title": "...", "description": "..."}},
    {{"day": 90, "title": "...", "description": "..."}}
  ],
  "immediate_priorities": [
    {{"priority": 1, "action": "...", "impact": "high/medium/low", "effort": "high/medium/low"}}
  ],
  "risk_factors": ["...", "..."],
  "success_metrics": ["...", "..."],
  "resource_recommendations": "..."
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

def generate_roadmap_report(
    vision: Dict,
    evolution_data: Optional[Dict],
    architecture_data: Optional[Dict],
    horizon_days: int,
    output_dir: Path
):
    """Generate visual roadmap report."""

    today = datetime.now()

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Future Roadmap</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 100%);
            color: #e0e0e0;
            padding: 40px;
            min-height: 100vh;
        }}
        h1 {{ color: #ff00aa; margin-bottom: 10px; font-size: 2.5em; }}
        .subtitle {{ color: #888; margin-bottom: 40px; }}
        .vision {{
            background: linear-gradient(135deg, rgba(255,0,170,0.1), rgba(0,212,255,0.1));
            border: 1px solid rgba(255,0,170,0.3);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            font-size: 1.2em;
            line-height: 1.8;
        }}
        .timeline {{
            position: relative;
            padding-left: 60px;
            margin-bottom: 40px;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 25px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, #ff00aa, #00d4ff);
        }}
        .milestone {{
            position: relative;
            margin-bottom: 40px;
            padding: 25px;
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .milestone::before {{
            content: '';
            position: absolute;
            left: -43px;
            top: 30px;
            width: 16px;
            height: 16px;
            background: #ff00aa;
            border-radius: 50%;
            border: 4px solid #0a0a0f;
        }}
        .milestone-day {{
            position: absolute;
            left: -100px;
            top: 25px;
            width: 50px;
            text-align: right;
            color: #ff00aa;
            font-weight: 700;
            font-size: 1.2em;
        }}
        .milestone-title {{
            font-size: 1.3em;
            color: #fff;
            margin-bottom: 10px;
        }}
        .milestone-desc {{
            color: #aaa;
            line-height: 1.6;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .card {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
        }}
        .card h3 {{ color: #00d4ff; margin-bottom: 15px; font-size: 0.9em; text-transform: uppercase; }}
        .priority {{
            display: flex;
            align-items: flex-start;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .priority:last-child {{ border: none; }}
        .priority-num {{
            background: linear-gradient(135deg, #ff00aa, #00d4ff);
            color: #fff;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            flex-shrink: 0;
        }}
        .priority-content {{ flex: 1; }}
        .priority-action {{ color: #fff; margin-bottom: 5px; }}
        .tags {{ display: flex; gap: 8px; }}
        .tag {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75em;
        }}
        .impact-high {{ background: rgba(255,0,68,0.2); color: #ff4488; }}
        .impact-medium {{ background: rgba(255,136,0,0.2); color: #ff8800; }}
        .impact-low {{ background: rgba(0,212,255,0.2); color: #00d4ff; }}
        .effort-high {{ background: rgba(255,0,68,0.1); color: #ff4488; border: 1px solid rgba(255,0,68,0.3); }}
        .effort-medium {{ background: rgba(255,136,0,0.1); color: #ff8800; border: 1px solid rgba(255,136,0,0.3); }}
        .effort-low {{ background: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }}
        .list {{ list-style: none; }}
        .list li {{ padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); color: #aaa; }}
        .list li:last-child {{ border: none; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #fff; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Future Roadmap</h1>
    <p class="subtitle">{horizon_days}-day projection - Generated {today.strftime('%Y-%m-%d')}</p>

    <div class="vision">
        {vision.get('vision_statement', 'No vision statement available.')}
    </div>

    <div class="section">
        <h2>Milestones</h2>
        <div class="timeline">
"""

    for milestone in vision.get('key_milestones', []):
        day = milestone.get('day', 0)
        target_date = today + timedelta(days=day)
        html += f"""
            <div class="milestone">
                <div class="milestone-day">Day {day}</div>
                <div class="milestone-title">{milestone.get('title', 'Milestone')}</div>
                <div class="milestone-desc">{milestone.get('description', '')}</div>
                <small style="color: #666;">Target: {target_date.strftime('%b %d, %Y')}</small>
            </div>
"""

    html += """
        </div>
    </div>

    <div class="section">
        <h2>Immediate Priorities</h2>
        <div class="card">
"""

    for priority in vision.get('immediate_priorities', []):
        num = priority.get('priority', 0)
        impact = priority.get('impact', 'medium')
        effort = priority.get('effort', 'medium')
        html += f"""
            <div class="priority">
                <div class="priority-num">{num}</div>
                <div class="priority-content">
                    <div class="priority-action">{priority.get('action', '')}</div>
                    <div class="tags">
                        <span class="tag impact-{impact}">Impact: {impact}</span>
                        <span class="tag effort-{effort}">Effort: {effort}</span>
                    </div>
                </div>
            </div>
"""

    html += """
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Risk Factors</h3>
            <ul class="list">
"""

    for risk in vision.get('risk_factors', []):
        html += f"                <li>{risk}</li>\n"

    html += """
            </ul>
        </div>
        <div class="card">
            <h3>Success Metrics</h3>
            <ul class="list">
"""

    for metric in vision.get('success_metrics', []):
        html += f"                <li>{metric}</li>\n"

    html += f"""
            </ul>
        </div>
    </div>

    <div class="card" style="margin-top: 40px;">
        <h3>Resource Recommendations</h3>
        <p style="color: #aaa; line-height: 1.6;">{vision.get('resource_recommendations', 'No recommendations available.')}</p>
    </div>

</body>
</html>
"""

    report_file = output_dir / "roadmap.html"
    report_file.write_text(html)
    return report_file


# =============================================================================
# MAIN
# =============================================================================

def run_future_projection(
    output_dir: Path,
    evolution_dir: Path,
    architecture_dir: Path,
    horizon_days: int,
    goal: Optional[str]
):
    """Run future projection analysis."""

    print("=" * 60)
    print("FUTURE VISIONARY")
    print("=" * 60)
    print(f"Horizon: {horizon_days} days")
    print(f"Output: {output_dir}")
    if goal:
        print(f"Goal: {goal}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Load past data
    print("Loading historical data...")
    evolution_data = load_evolution_data(evolution_dir)
    if evolution_data:
        print(f"  Found {evolution_data.get('total_epochs', 0)} epochs")
    else:
        print("  No evolution data found")

    # Load present data
    print("Loading architecture data...")
    architecture_data = load_architecture_data(architecture_dir)
    if architecture_data:
        print(f"  Found metrics with health score: {architecture_data.get('metrics', {}).get('health_score', 'unknown')}")
    else:
        print("  No architecture data found")

    print()

    # Create future projection
    print("Synthesizing future vision...")
    client = create_gemini_client()
    if not client:
        print("  ERROR: No API key")
        sys.exit(1)

    vision = synthesize_future_vision(
        client, evolution_data, architecture_data, horizon_days, goal
    )

    if 'error' in vision:
        print(f"  Error: {vision['error']}")
    else:
        print(f"  Vision created with {len(vision.get('key_milestones', []))} milestones")

    print()

    # Generate report
    print("Generating roadmap report...")
    report_file = generate_roadmap_report(
        vision, evolution_data, architecture_data, horizon_days, output_dir
    )
    print(f"  Created: {report_file}")

    # Save JSON
    data_file = output_dir / "roadmap_data.json"
    data_file.write_text(json.dumps({
        'generated_at': datetime.now().isoformat(),
        'horizon_days': horizon_days,
        'goal': goal,
        'vision': vision
    }, indent=2))
    print(f"  Created: {data_file}")

    print()
    print("=" * 60)
    print("PROJECTION COMPLETE")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Project future codebase roadmap")
    parser.add_argument("--output", "-o", default="roadmap_report", help="Output directory")
    parser.add_argument("--evolution-dir", default="evolution_report", help="Evolution data directory")
    parser.add_argument("--arch-dir", default="architecture_report", help="Architecture data directory")
    parser.add_argument("--horizon", type=int, default=90, help="Days to project (default: 90)")
    parser.add_argument("--goal", "-g", help="Specific goal to achieve")

    args = parser.parse_args()

    output = Path(args.output)
    evolution = Path(args.evolution_dir)
    arch = Path(args.arch_dir)

    if not output.is_absolute():
        output = PROJECT_ROOT / output
    if not evolution.is_absolute():
        evolution = PROJECT_ROOT / evolution
    if not arch.is_absolute():
        arch = PROJECT_ROOT / arch

    run_future_projection(
        output_dir=output,
        evolution_dir=evolution,
        architecture_dir=arch,
        horizon_days=args.horizon,
        goal=args.goal
    )


if __name__ == "__main__":
    main()
