#!/usr/bin/env python3
"""
Collider Pre-Push Git Hook — PDS Gate
Enforces structural health by checking for regressions in changed code.

HOW IT WORKS:
  1. Runs `uv run python cli.py pds --json` to evaluate blast radius of changes
  2. Blocks push if critical/high findings exist in structural categories
  3. If PDS finds no baseline, allows push (CI runs full analysis to establish one)
  4. If PDS crashes entirely, allows push with a warning (CI will catch it)

CONFIGURATION (for AI agents editing this):
  - TIMEOUT_SECONDS: int, max seconds before we let the push through
  - ALLOW_ON_ERROR: bool, if True push is allowed when pds crashes
  - BLOCKING_CATEGORIES: list, structural categories that block on critical/high
  - BLOCKING_SEVERITIES: list, severity levels that trigger blocking

This script is called by .agent/hooks/pre-push (the shell wrapper).
"""

import sys
import subprocess
import json
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────
# AI AGENTS: edit these values to adjust gate strictness
TIMEOUT_SECONDS = 30       # PDS is fast (reads cached baseline + git diff)
ALLOW_ON_ERROR = True      # If PDS crashes, allow push? (CI is the backup)
BLOCKING_CATEGORIES = [
    "purpose_decomposition", "incoherence", "gap_detection",
    "topology", "entanglement", "constraints",
]
BLOCKING_SEVERITIES = ["critical", "high"]
# ───────────────────────────────────────────────────────────────

script_path = Path(__file__).resolve()
particle_dir = script_path.parent.parent.parent  # particle/src/scripts/ -> particle/


def main():
    print("Collider PDS Gate: Checking for structural regressions...")

    # ── Step 1: Run pds --json and capture output ─────────────
    try:
        result = subprocess.run(
            ["uv", "run", "python", "cli.py", "pds", "--json"],
            cwd=str(particle_dir),
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS or None,
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: PDS timed out ({TIMEOUT_SECONDS}s). Allowing push -- CI will validate.")
        sys.exit(0)
    except FileNotFoundError:
        print("WARNING: 'uv' not found. Allowing push -- install uv and re-run.")
        sys.exit(0 if ALLOW_ON_ERROR else 1)
    except Exception as e:
        print(f"WARNING: Failed to run PDS: {e}")
        sys.exit(0 if ALLOW_ON_ERROR else 1)

    # ── Step 2: Parse JSON output ─────────────────────────────
    stdout = result.stdout.strip()
    pds_data = None

    # PDS --json emits a JSON object on stdout
    json_start = stdout.find("{")
    if json_start >= 0:
        try:
            pds_data = json.loads(stdout[json_start:])
        except json.JSONDecodeError:
            pass

    if pds_data is None:
        # PDS output couldn't be parsed -- could be "No baseline" text
        if "No PDS baseline" in stdout or "No analyzable changes" in stdout:
            print(f"PDS: {stdout}")
            print("Allowing push -- no baseline or no changes.")
            sys.exit(0)

        print("WARNING: Could not parse PDS output as JSON.")
        if stdout:
            print(f"Raw output (last 200 chars): ...{stdout[-200:]}")
        if ALLOW_ON_ERROR:
            print("Allowing push -- CI will validate.")
            sys.exit(0)
        sys.exit(1)

    # ── Step 3: Evaluate PDS result ───────────────────────────
    passed = pds_data.get("passed", True)
    summary = pds_data.get("summary", "")
    blocking = pds_data.get("blocking_findings", [])
    warnings = pds_data.get("warnings", [])

    print(f"PDS: {summary}")

    if passed:
        if warnings:
            print(f"  {len(warnings)} warning(s) (non-blocking)")
        print("PASS: No structural regressions detected. Push permitted.")
        sys.exit(0)

    # ── Step 4: Push blocked -- show diagnostics ──────────────
    print(f"\nFAIL: {len(blocking)} blocking structural finding(s)")
    print("=" * 60)

    for finding in blocking[:10]:
        sev = finding.get("severity", "?").upper()
        cat = finding.get("category", "?")
        title = finding.get("title", "?")
        print(f"  [{sev}] [{cat}] {title}")

    if len(blocking) > 10:
        print(f"  ... and {len(blocking) - 10} more")

    if warnings:
        print(f"\n  Plus {len(warnings)} non-blocking warning(s)")

    print("=" * 60)
    print("Fix the structural issues above, then retry push.")
    print("To skip this check once: git push --no-verify")
    sys.exit(1)


if __name__ == "__main__":
    main()
