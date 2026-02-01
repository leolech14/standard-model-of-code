#!/usr/bin/env python3
"""
HSL Daemon (Headless Semantic Loader)
======================================
Backwards-compatible wrapper for drift_guard.py.

This was renamed during SMoC-native naming consolidation:
- hsl_daemon.py → drift_guard.py (Jan 2026)

This wrapper exists to support existing LaunchAgents and scripts that
reference the old name. It delegates to drift_guard.py and logs to the
expected HSL log locations.

Usage:
    python hsl_daemon.py --once       # Single run (for LaunchAgent)
    python hsl_daemon.py              # Continuous mode

Logs to: wave/intelligence/logs/hsl_daemon.log
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Determine paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DRIFT_GUARD = SCRIPT_DIR / "drift_guard.py"
LOG_DIR = REPO_ROOT / "wave" / "intelligence" / "logs"
LOG_FILE = LOG_DIR / "hsl_daemon.log"


def log(message: str):
    """Write timestamped message to HSL log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    line = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a") as f:
        f.write(line)

    # Also print to stdout for LaunchAgent capture
    print(line.strip())


def main():
    """Run drift_guard.py with HSL logging wrapper."""
    log("HSL Daemon starting")

    # Check drift_guard exists
    if not DRIFT_GUARD.exists():
        log(f"ERROR: drift_guard.py not found at {DRIFT_GUARD}")
        sys.exit(1)

    # Pass through all arguments to drift_guard
    args = [sys.executable, str(DRIFT_GUARD)] + sys.argv[1:]

    try:
        log(f"Delegating to drift_guard.py with args: {sys.argv[1:]}")

        # Run drift_guard
        result = subprocess.run(
            args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout for --once mode
        )

        # Log output
        if result.stdout:
            for line in result.stdout.strip().split('\n')[:20]:  # Limit output
                log(f"drift_guard: {line}")

        if result.stderr:
            for line in result.stderr.strip().split('\n')[:10]:
                log(f"drift_guard STDERR: {line}")

        if result.returncode == 0:
            log("HSL Daemon completed successfully")
        else:
            log(f"HSL Daemon exited with code {result.returncode}")

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        log("ERROR: drift_guard.py timed out after 5 minutes")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
