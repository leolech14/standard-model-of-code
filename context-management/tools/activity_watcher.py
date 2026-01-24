#!/usr/bin/env python3
"""
Activity Watcher - Smart trigger for analysis based on sustained activity.

Instead of running analysis on every file change (thundering herd),
this script watches for SUSTAINED activity before triggering.

Logic:
  1. File change detected (via launchd WatchPaths)
  2. Watcher starts, records timestamp
  3. Checks every POLL_INTERVAL for new changes
  4. If activity continues over WATCH_WINDOW → trigger analysis
  5. If isolated change (no follow-up) → exit silently

This prevents:
  - Wasting API calls on drive-by edits
  - Running analysis when user isn't actively working
  - Thundering herd from multiple watchers

Usage:
  python activity_watcher.py --watch-paths /path/to/dir1 /path/to/dir2
  python activity_watcher.py --watch-paths /path/to/dir --on-activity "python analyze.py --verify pipeline"
"""

import argparse
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
POLL_INTERVAL = 300  # 5 minutes between checks
WATCH_WINDOW = 1800  # 30 minutes total watch window
MIN_CHANGES_FOR_ACTIVITY = 2  # Need at least 2 changes to consider "active"
STATE_FILE = Path("/tmp/elements_activity_watcher.state")
LOG_FILE = Path("/tmp/elements_activity_watcher.log")


def log(msg: str):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def get_mtimes(paths: list[Path]) -> dict[str, float]:
    """Get modification times for all files in watched paths."""
    mtimes = {}
    for path in paths:
        if path.is_file():
            mtimes[str(path)] = path.stat().st_mtime
        elif path.is_dir():
            for f in path.rglob("*"):
                if f.is_file() and not any(p in str(f) for p in [".git", "__pycache__", ".pyc"]):
                    try:
                        mtimes[str(f)] = f.stat().st_mtime
                    except:
                        pass
    return mtimes


def count_changes(old_mtimes: dict, new_mtimes: dict) -> int:
    """Count files that changed between snapshots."""
    changes = 0
    for path, mtime in new_mtimes.items():
        if path not in old_mtimes or old_mtimes[path] != mtime:
            changes += 1
    # Also count new files
    for path in new_mtimes:
        if path not in old_mtimes:
            changes += 1
    return changes


def load_state() -> dict:
    """Load watcher state from file."""
    if STATE_FILE.exists():
        try:
            import json
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {}


def save_state(state: dict):
    """Save watcher state to file."""
    import json
    STATE_FILE.write_text(json.dumps(state, indent=2))


def clear_state():
    """Clear watcher state."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def main():
    parser = argparse.ArgumentParser(description="Activity watcher for smart analysis triggers")
    parser.add_argument("--watch-paths", nargs="+", required=True, help="Paths to watch for changes")
    parser.add_argument("--on-activity", default=None, help="Command to run when sustained activity detected")
    parser.add_argument("--poll-interval", type=int, default=POLL_INTERVAL, help=f"Seconds between checks (default: {POLL_INTERVAL})")
    parser.add_argument("--watch-window", type=int, default=WATCH_WINDOW, help=f"Total watch window in seconds (default: {WATCH_WINDOW})")
    parser.add_argument("--min-changes", type=int, default=MIN_CHANGES_FOR_ACTIVITY, help=f"Minimum changes to trigger (default: {MIN_CHANGES_FOR_ACTIVITY})")
    parser.add_argument("--daemon", type=str, help="Daemon name for logging")
    args = parser.parse_args()

    daemon_name = args.daemon or "activity_watcher"
    log(f"[{daemon_name}] Starting activity watch")

    # Convert paths
    watch_paths = [Path(p) for p in args.watch_paths]
    for p in watch_paths:
        if not p.exists():
            log(f"[{daemon_name}] Warning: watch path does not exist: {p}")

    # Load or initialize state
    state = load_state()
    now = time.time()

    # Check if we're already in a watch window
    if "watch_start" in state and "baseline_mtimes" in state:
        watch_start = state["watch_start"]
        elapsed = now - watch_start

        if elapsed > args.watch_window:
            # Watch window expired, check final tally
            baseline_mtimes = state["baseline_mtimes"]
            current_mtimes = get_mtimes(watch_paths)
            total_changes = state.get("total_changes", 0) + count_changes(baseline_mtimes, current_mtimes)

            log(f"[{daemon_name}] Watch window complete. Total changes: {total_changes}")

            if total_changes >= args.min_changes:
                log(f"[{daemon_name}] SUSTAINED ACTIVITY DETECTED ({total_changes} changes)")
                if args.on_activity:
                    log(f"[{daemon_name}] Running: {args.on_activity}")
                    try:
                        result = subprocess.run(
                            args.on_activity,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=600  # 10 min timeout
                        )
                        if result.returncode == 0:
                            log(f"[{daemon_name}] Analysis completed successfully")
                        else:
                            log(f"[{daemon_name}] Analysis failed: {result.stderr[:500]}")
                    except subprocess.TimeoutExpired:
                        log(f"[{daemon_name}] Analysis timed out")
                    except Exception as e:
                        log(f"[{daemon_name}] Analysis error: {e}")
            else:
                log(f"[{daemon_name}] Isolated change detected, skipping analysis")

            clear_state()
            return

        else:
            # Still in watch window, accumulate changes
            baseline_mtimes = state["baseline_mtimes"]
            current_mtimes = get_mtimes(watch_paths)
            new_changes = count_changes(baseline_mtimes, current_mtimes)
            total_changes = state.get("total_changes", 0) + new_changes

            log(f"[{daemon_name}] Watch in progress. Elapsed: {int(elapsed)}s, Changes this poll: {new_changes}, Total: {total_changes}")

            # Update state
            state["baseline_mtimes"] = current_mtimes
            state["total_changes"] = total_changes
            state["last_poll"] = now
            save_state(state)
            return

    else:
        # Start new watch window
        log(f"[{daemon_name}] Starting new watch window ({args.watch_window}s)")
        baseline_mtimes = get_mtimes(watch_paths)

        state = {
            "watch_start": now,
            "baseline_mtimes": baseline_mtimes,
            "total_changes": 0,
            "last_poll": now,
            "daemon": daemon_name
        }
        save_state(state)
        log(f"[{daemon_name}] Baseline captured: {len(baseline_mtimes)} files tracked")
        return


if __name__ == "__main__":
    main()
