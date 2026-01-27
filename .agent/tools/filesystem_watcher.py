#!/usr/bin/env python3
"""
Filesystem Watcher - Smart Update Trigger
==========================================

Watches PROJECT_elements/ for file changes.
Only triggers wire.py after 5-minute quiet period.

This prevents wasteful polling - refinery only runs when files actually change.

Usage:
    python filesystem_watcher.py
    # Or in background:
    screen -dmS watcher python filesystem_watcher.py
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.parent
WATCH_PATHS = [
    REPO_ROOT / ".agent",
    REPO_ROOT / "context-management",
    REPO_ROOT / "standard-model-of-code/src",
]

# Ignore patterns (don't trigger on butler writes)
IGNORE_PATHS = [
    ".agent/intelligence/chunks",
    ".agent/intelligence/comms/state_history.jsonl",
    "context-management/intelligence/state",
    ".git",
    "__pycache__",
    ".venv",
    ".tools_venv",
]

# Timing
QUIET_PERIOD_SECONDS = 300  # 5 minutes quiet before triggering
CHECK_INTERVAL_SECONDS = 60  # Check every minute

# Logging
LOG_FILE = REPO_ROOT / ".agent" / "intelligence" / "filesystem_watcher.log"


class SmartWatcher:
    """File watcher with debouncing."""

    def __init__(self):
        self.last_change_time = 0
        self.pending = False
        self.last_mtime = self._get_max_mtime()
        # Ensure log file exists
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOG_FILE.touch(exist_ok=True)

    def _log(self, message: str):
        """Append to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        with open(LOG_FILE, 'a') as f:
            f.write(log_line)
        print(log_line.strip())  # Also print to stdout

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)
        return any(ignored in path_str for ignored in IGNORE_PATHS)

    def _get_max_mtime(self) -> float:
        """Get most recent modification time across watched paths."""
        max_mtime = 0
        for watch_path in WATCH_PATHS:
            if not watch_path.exists():
                continue

            for root, dirs, files in os.walk(watch_path):
                # Filter dirs to skip ignored paths
                dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]

                for filename in files:
                    filepath = Path(root) / filename

                    if self._should_ignore(filepath):
                        continue

                    try:
                        mtime = filepath.stat().st_mtime
                        if mtime > max_mtime:
                            max_mtime = mtime
                    except (OSError, PermissionError):
                        continue

        return max_mtime

    def check_for_changes(self):
        """Check if files changed since last check."""
        current_mtime = self._get_max_mtime()

        if current_mtime > self.last_mtime:
            # Files changed!
            self.last_change_time = time.time()
            self.last_mtime = current_mtime
            self.pending = True
            self._log("File changes detected, starting quiet period...")

    def check_and_trigger(self):
        """Trigger wire if quiet period elapsed."""
        if not self.pending:
            return

        quiet_time = time.time() - self.last_change_time

        if quiet_time >= QUIET_PERIOD_SECONDS:
            self._log(f"Quiet for {QUIET_PERIOD_SECONDS}s, running wire...")

            # Run wire --quick
            try:
                result = subprocess.run(
                    [sys.executable, str(REPO_ROOT / ".agent" / "tools" / "wire.py"), "--quick"],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                if result.returncode == 0:
                    self._log("Wire completed successfully")
                else:
                    self._log(f"Wire failed: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                self._log("Wire timed out")
            except Exception as e:
                self._log(f"Wire error: {e}")

            self.pending = False
            # Reset mtime to avoid re-triggering immediately
            self.last_mtime = self._get_max_mtime()

    def run(self):
        """Main watch loop."""
        self._log("Filesystem watcher started")
        self._log(f"Watching: {', '.join(str(p.name) for p in WATCH_PATHS)}")
        self._log(f"Quiet period: {QUIET_PERIOD_SECONDS}s")
        self._log(f"Check interval: {CHECK_INTERVAL_SECONDS}s")
        self._log(f"Log file: {LOG_FILE}")
        print()

        try:
            while True:
                self.check_for_changes()
                self.check_and_trigger()
                time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            self._log("Watcher stopped by user")


if __name__ == "__main__":
    watcher = SmartWatcher()
    watcher.run()
