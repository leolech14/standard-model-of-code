#!/usr/bin/env python3
"""
Service Health Check Script
============================
Reads SERVICE_REGISTRY.yaml and performs health checks on all services.
Outputs JSON status for consumption by dashboards/APIs.

Usage:
    python3 wave/tools/ops/health_check.py
    python3 wave/tools/ops/health_check.py --json
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def check_env_var_present(env_vars: list) -> Dict[str, Any]:
    """Check if required environment variables are set (presence only, no values)."""
    missing = []
    present = []

    for var in env_vars:
        # Check environment
        if os.environ.get(var):
            present.append(var)
        else:
            # Try Doppler
            try:
                result = subprocess.run(
                    ["doppler", "secrets", "get", var, "--plain"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    present.append(f"{var} (doppler)")
                else:
                    missing.append(var)
            except Exception:
                missing.append(var)

    return {
        "status": "OK" if not missing else "DEGRADED" if present else "DOWN",
        "present": present,
        "missing": missing
    }


def check_socket_reachable(host: str, port: int, timeout: float = 2.0) -> Dict[str, Any]:
    """Check if a TCP socket is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return {"status": "OK", "message": f"Connected to {host}:{port}"}
        else:
            return {"status": "DOWN", "message": f"Cannot connect to {host}:{port}"}
    except Exception as e:
        return {"status": "DOWN", "message": str(e)}


def check_process_running(process_name: str) -> Dict[str, Any]:
    """Check if a process is running by name."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            return {"status": "OK", "pids": pids}
        else:
            return {"status": "DOWN", "message": "Process not running"}
    except Exception as e:
        return {"status": "UNKNOWN", "message": str(e)}


def check_log_for_errors(log_path: Path) -> Dict[str, Any]:
    """Check a log file for recent errors."""
    if not log_path.exists():
        return {"status": "UNKNOWN", "message": "Log file not found"}

    try:
        content = log_path.read_text()
        lines = content.strip().split('\n') if content.strip() else []

        if not lines:
            return {"status": "OK", "message": "Log empty (no errors)"}

        # Get last few lines
        last_lines = lines[-5:]
        has_error = any('error' in line.lower() or 'fail' in line.lower() for line in last_lines)

        return {
            "status": "ERROR" if has_error else "OK",
            "last_entry": lines[-1] if lines else None,
            "line_count": len(lines)
        }
    except Exception as e:
        return {"status": "UNKNOWN", "message": str(e)}


def check_config_valid(tool_path: Path) -> Dict[str, Any]:
    """Check if a tool's config/path exists."""
    full_path = PROJECT_ROOT / tool_path
    if full_path.exists():
        return {"status": "OK", "path": str(tool_path)}
    else:
        return {"status": "DOWN", "message": f"Tool not found: {tool_path}"}


def run_all_checks() -> Dict[str, Any]:
    """Run all health checks and return consolidated status."""
    timestamp = datetime.utcnow().isoformat() + "Z"

    results = {
        "timestamp": timestamp,
        "overall_status": "OK",
        "services": {}
    }

    # HSL Daemon
    hsl_stderr = PROJECT_ROOT / "wave/intelligence/logs/hsl_daemon_stderr.log"
    hsl_process = check_process_running("activity_watcher")
    hsl_logs = check_log_for_errors(hsl_stderr)

    results["services"]["hsl_daemon"] = {
        "name": "Headless Semantic Loader",
        "process": hsl_process,
        "logs": hsl_logs,
        "status": hsl_process["status"]
    }

    # GCS Archive
    gcs_tool = PROJECT_ROOT / "wave/tools/archive/archive.py"
    results["services"]["gcs_archive"] = {
        "name": "GCS Archive",
        "bucket": "gs://elements-archive-2026",
        "tool_exists": check_config_valid(Path("wave/tools/archive/archive.py")),
        "status": "OK" if gcs_tool.exists() else "DOWN"
    }

    # Neo4j
    neo4j_check = check_socket_reachable("localhost", 7687)
    results["services"]["neo4j"] = {
        "name": "Neo4j Graph Database",
        "uri": "bolt://localhost:7687",
        "connection": neo4j_check,
        "status": neo4j_check["status"]
    }

    # API Providers
    results["services"]["gemini"] = {
        "name": "Google Gemini",
        **check_env_var_present(["GEMINI_API_KEY", "GOOGLE_API_KEY"])
    }

    results["services"]["cerebras"] = {
        "name": "Cerebras Inference",
        **check_env_var_present(["CEREBRAS_API_KEY"])
    }

    results["services"]["perplexity"] = {
        "name": "Perplexity AI",
        **check_env_var_present(["PERPLEXITY_API_KEY"])
    }

    results["services"]["huggingface"] = {
        "name": "HuggingFace",
        **check_env_var_present(["HF_TOKEN"])
    }

    # Refinery Pipeline
    refinery_tool = PROJECT_ROOT / "wave/tools/refinery/pipeline.py"
    results["services"]["refinery"] = {
        "name": "Refinery Pipeline",
        "tool_exists": check_config_valid(Path("wave/tools/refinery/pipeline.py")),
        "status": "OK" if refinery_tool.exists() else "DOWN"
    }

    # Calculate overall status
    statuses = [s.get("status", "UNKNOWN") for s in results["services"].values()]
    if "DOWN" in statuses:
        results["overall_status"] = "DEGRADED"
    elif "ERROR" in statuses:
        results["overall_status"] = "WARNING"
    elif all(s == "OK" for s in statuses):
        results["overall_status"] = "OK"
    else:
        results["overall_status"] = "UNKNOWN"

    return results


def main():
    results = run_all_checks()

    if "--json" in sys.argv or len(sys.argv) == 1:
        print(json.dumps(results, indent=2))
    else:
        # Pretty print
        print(f"\n{'='*60}")
        print(f"SERVICE HEALTH CHECK - {results['timestamp']}")
        print(f"{'='*60}")
        print(f"Overall Status: {results['overall_status']}")
        print(f"{'='*60}\n")

        for svc_id, svc_data in results["services"].items():
            status = svc_data.get("status", "UNKNOWN")
            icon = {"OK": "[OK]", "DOWN": "[!!]", "DEGRADED": "[~~]", "ERROR": "[XX]", "UNKNOWN": "[??]"}.get(status, "[??]")
            print(f"{icon} {svc_data.get('name', svc_id)}: {status}")

        print()


if __name__ == "__main__":
    main()
