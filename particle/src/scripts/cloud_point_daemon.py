#!/usr/bin/env python3
"""
Cloud Point Background Daemon
A background process managed by PROJECT_sentinel that autonomously monitors codebase architecture.
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Setup absolute paths
DAEMON_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DAEMON_DIR.parent.parent.parent
DB_DIR = PROJECT_ROOT / "particle" / ".collider"
INSIGHTS_JSON = DB_DIR / "collider_insights.json"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "cloud_point_daemon.log"

def log_event(message: str, level: str = "INFO"):
    """Writes to the daemon append log."""
    LOG_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    print(log_entry.strip())

def run_collider():
    """Executes the standard model analysis."""
    log_event("Starting background Collider analysis...")
    start_time = time.time()
    try:
        result = subprocess.run(
            ["uv", "run", "python", "particle/cli.py", "grade", "--json"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        duration = time.time() - start_time
        if result.returncode != 0:
            log_event(f"Collider execution failed (Code {result.returncode})", "ERROR")
            log_event(result.stderr, "ERROR")
            return False

        log_event(f"Collider analysis completed in {duration:.2f}s")
        return True
    except Exception as e:
        log_event(f"Failed to execute Collider process: {e}", "ERROR")
        return False

def analyze_insights():
    """Reads the JSON output and checks for degradation."""
    if not INSIGHTS_JSON.exists():
        log_event("No collider_insights.json found after run.", "ERROR")
        return

    try:
        with open(INSIGHTS_JSON, "r") as f:
            insights = json.load(f)
    except Exception as e:
        log_event(f"Failed to parse insights JSON: {e}", "ERROR")
        return

    health_score = insights.get("health_score", 0.0)
    findings = insights.get("findings", [])

    log_event(f"Current Health Score: {health_score}/10")

    # We look for ANY findings, focusing on [MEDIUM] and [LOW]
    # since [HIGH]/[CRITICAL] are caught by the pre-push hook.
    actionable_findings = [f for f in findings if f.get("severity", "").lower() in ["medium", "low"]]

    if actionable_findings:
        log_event(f"Detected {len(actionable_findings)} non-critical architectural issues.", "WARNING")
        for finding in actionable_findings:
            sev = finding.get("severity", "UNK").upper()
            title = finding.get("title", "Unknown Issue")
            log_event(f"  - [{sev}] {title}")

        # TODO: Future enhancement - Actually trigger an MCP Agent via a local LLM runner
        log_event("Action: Background AI Agent swarm trigger requested (Simulation Mode)", "INFO")
        log_event("The MCP Server 'collider_inspect_node' and 'collider_mutate' tools should be invoked.", "INFO")
    else:
        log_event("Codebase architecture is perfectly clean. No healing required.", "INFO")

def main():
    log_event("Cloud Point Daemon Waking Up...")
    if run_collider():
        analyze_insights()
    log_event("Cloud Point Daemon Sleeping.")

if __name__ == "__main__":
    main()
