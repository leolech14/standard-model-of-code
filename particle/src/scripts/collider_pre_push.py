#!/usr/bin/env python3
"""
Collider Pre-Push Git Hook
Enforces architectural health standards before permitting code to be pushed.

HOW IT WORKS:
  1. Runs `uv run python cli.py grade --json` to get a health score
  2. Blocks push if health score < MINIMUM_HEALTH (default 8.0)
  3. If grade fails entirely, allows push with a warning (CI will catch it)

CONFIGURATION (for AI agents editing this):
  - MINIMUM_HEALTH: float, threshold score out of 10
  - TIMEOUT_SECONDS: int, max seconds before we let the push through
  - ALLOW_ON_ERROR: bool, if True push is allowed when grade crashes

This script is called by .agent/hooks/pre-push (the shell wrapper).
"""

import sys
import subprocess
import json
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
# AI AGENTS: edit these values to adjust gate strictness
MINIMUM_HEALTH = 8.0       # Score out of 10. Below this = push blocked.
TIMEOUT_SECONDS = 120      # Max time for grade command. 0 = no timeout.
ALLOW_ON_ERROR = True      # If grade crashes, allow push? (CI is the backup)
# ───────────────────────────────────────────────────────────────

script_path = Path(__file__).resolve()
particle_dir = script_path.parent.parent.parent  # particle/src/scripts/ -> particle/


def main():
    print("Collider CI/CD Gate: Auditing Codebase Architecture...")

    # ── Step 1: Run grade --json and capture output ────────────
    try:
        result = subprocess.run(
            ["uv", "run", "python", "cli.py", "grade", "--json"],
            cwd=str(particle_dir),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS or None,
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: Collider grade timed out ({TIMEOUT_SECONDS}s). Allowing push -- CI will validate.")
        sys.exit(0)
    except FileNotFoundError:
        print("WARNING: 'uv' not found. Allowing push -- install uv and re-run.")
        sys.exit(0 if ALLOW_ON_ERROR else 1)
    except Exception as e:
        print(f"WARNING: Failed to run Collider: {e}")
        sys.exit(0 if ALLOW_ON_ERROR else 1)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        print(f"WARNING: Collider grade exited with code {result.returncode}")
        if stderr:
            # Show last 5 lines of stderr to help debugging
            lines = stderr.splitlines()[-5:]
            for line in lines:
                print(f"  {line}")
        if ALLOW_ON_ERROR:
            print("Allowing push -- CI will validate.")
            sys.exit(0)
        sys.exit(1)

    # ── Step 2: Parse JSON output ──────────────────────────────
    stdout = result.stdout.strip()
    grade_data = None

    # grade --json may emit progress lines before the JSON object
    # Find the JSON by looking for the first { ... } block
    json_start = stdout.find("{")
    if json_start >= 0:
        try:
            grade_data = json.loads(stdout[json_start:])
        except json.JSONDecodeError:
            pass

    if grade_data is None:
        print("WARNING: Could not parse grade output as JSON.")
        print(f"Raw output (last 200 chars): ...{stdout[-200:]}")
        if ALLOW_ON_ERROR:
            print("Allowing push -- CI will validate.")
            sys.exit(0)
        sys.exit(1)

    # ── Step 3: Enforce health threshold ───────────────────────
    health_index = grade_data.get("health_index", 0.0)
    grade_letter = grade_data.get("grade", "?")

    print(f"Health: {health_index:.1f}/10 ({grade_letter})")

    if health_index >= MINIMUM_HEALTH:
        print(f"PASS: Architecture healthy (>= {MINIMUM_HEALTH}). Push permitted.")
        sys.exit(0)

    # ── Step 4: Push blocked -- show useful diagnostics ────────
    print(f"\nFAIL: Health {health_index:.1f}/10 is below minimum {MINIMUM_HEALTH}")
    print("=" * 60)

    # Show component scores if available
    components = grade_data.get("component_scores", {})
    if components:
        print("Component scores:")
        for name, score in components.items():
            marker = "  <<" if score < MINIMUM_HEALTH else ""
            print(f"  {name}: {score:.1f}/10{marker}")

    # Also check .collider/collider_insights.json for findings (if it exists from a prior full run)
    insights_path = particle_dir / ".collider" / "collider_insights.json"
    if insights_path.exists():
        try:
            insights = json.load(open(insights_path))
            findings = insights.get("findings", [])
            severe = [f for f in findings if f.get("severity", "").lower() in ("critical", "high")]
            if severe:
                print(f"\n{len(severe)} critical/high findings (from last full analysis):")
                for f in severe[:5]:
                    print(f"  [{f.get('severity', '?').upper()}] {f.get('title', '?')}")
                if len(severe) > 5:
                    print(f"  ... and {len(severe) - 5} more")
        except Exception:
            pass  # Stale/missing insights file is non-fatal

    print("=" * 60)
    print("Fix the issues above, then retry push.")
    print("To skip this check once: git push --no-verify")
    sys.exit(1)


if __name__ == "__main__":
    main()
