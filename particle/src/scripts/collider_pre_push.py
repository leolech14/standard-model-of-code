#!/usr/bin/env python3
"""
Collider Pre-Push Git Hook
Enforces architectural health standards before permitting code to be pushed to remote.
"""

import sys
import subprocess
import json
from pathlib import Path
import os

# Ensure we can import particle modules
script_path = Path(__file__).resolve()
# script_path = PROJECT_elements/particle/src/scripts/collider_pre_push.py
particle_dir = script_path.parent.parent.parent

# Add particle/ to sys.path so we can import src.core...
sys.path.append(str(particle_dir))

def main():
    print("🛡️  Collider CI/CD Gate: Auditing Codebase Architecture...")

    # Run the `grade` command which executes the full analysis pipeline
    # without HTML generation and writes standard JSONs including insights.
    try:
        result = subprocess.run(
            ["uv", "run", "python", "cli.py", "grade"],
            cwd=str(particle_dir),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print("❌ Collider execution failed:")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Failed to run Collider: {e}")
        sys.exit(1)

    # Read the generated insights
    insights_path = particle_dir / ".collider" / "collider_insights.json"
    if not insights_path.exists():
        print("❌ Collider Intelligence Digest not generated.")
        sys.exit(1)

    try:
        with open(insights_path, "r") as f:
            insights = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse Intelligence Digest: {e}")
        sys.exit(1)

    health_score = insights.get("health_score", 0.0)
    findings = insights.get("findings", [])

    block_push = False

    if health_score < 8.0:
        print(f"❌ Architectural Health Score ({health_score}/10) is below the required 8.0 threshold.")
        block_push = True

    criticals = [f for f in findings if f.get("severity", "").lower() == "critical"]
    highs = [f for f in findings if f.get("severity", "").lower() == "high"]

    if criticals or highs:
        print(f"❌ Found {len(criticals)} Critical and {len(highs)} High severity architectural issues.")
        block_push = True

    if block_push:
        print("\n" + "="*80)
        print("🚨 PUSH REJECTED: Architectural Degradation Detected 🚨")
        print("="*80 + "\n")

        # Format the markdown strictly using the MCP tool logic we wrote earlier
        try:
            from src.core.rag.mcp_server import _format_insights_markdown
            md_output = _format_insights_markdown(insights)
            print(md_output)
        except Exception as e:
            print(f"[Fallback - Formatting failed: {e}]\n")
            for f in criticals + highs:
                print(f"- [{f.get('severity', 'UNKNOWN').upper()}] {f.get('title', 'Unknown')}: {f.get('description', '')}")

        print("\n" + "="*80)
        print("Use the 'Node Playground' AI tool (collider_inspect_node) to resolve these structural issues before pushing.")
        print("="*80 + "\n")
        sys.exit(1)

    print(f"✅ Architecture Valid (Health: {health_score}/10). Push permitted.")
    sys.exit(0)

if __name__ == "__main__":
    main()
