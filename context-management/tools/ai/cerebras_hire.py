#!/usr/bin/env python3
"""
Cerebras Hire Mechanism
=======================
EXCLUSIVE access control for Cerebras API.

PROBLEM:
- Multiple agents hitting Cerebras = rate limit chaos
- No coordination = everyone fails

SOLUTION:
- Global lock file that grants EXCLUSIVE access
- Agents must "hire" Cerebras before using it
- Only one consumer at a time
- Auto-expire after timeout

Usage:
    # Check if available
    python cerebras_hire.py status

    # Hire Cerebras (blocks until available)
    python cerebras_hire.py hire --consumer "sweep-agent" --duration 600

    # Release when done
    python cerebras_hire.py release

    # Force release (emergency)
    python cerebras_hire.py force-release

    # In Python code:
    from cerebras_hire import hire_cerebras, release_cerebras
    with hire_cerebras("my-agent", duration=300):
        # Exclusive Cerebras access here
        pass
"""

import os
import sys
import json
import time
import fcntl
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
from contextlib import contextmanager

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
HIRE_DIR = PROJECT_ROOT / "context-management" / "data" / "cerebras_hire"
HIRE_DIR.mkdir(parents=True, exist_ok=True)

LOCK_FILE = HIRE_DIR / "cerebras.lock"
STATE_FILE = HIRE_DIR / "hire_state.json"

DEFAULT_DURATION = 300  # 5 minutes default
MAX_DURATION = 3600     # 1 hour max


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class HireState:
    """Current hire state."""
    hired: bool = False
    consumer: str = ""
    hired_at: str = ""
    expires_at: str = ""
    duration: int = 0
    pid: int = 0


def load_state() -> HireState:
    """Load current hire state."""
    if not STATE_FILE.exists():
        return HireState()
    try:
        data = json.loads(STATE_FILE.read_text())
        return HireState(**data)
    except Exception:
        return HireState()


def save_state(state: HireState):
    """Save hire state."""
    STATE_FILE.write_text(json.dumps(asdict(state), indent=2))


def is_expired(state: HireState) -> bool:
    """Check if current hire has expired."""
    if not state.hired:
        return True
    if not state.expires_at:
        return True
    try:
        expires = datetime.fromisoformat(state.expires_at)
        return datetime.now() > expires
    except Exception:
        return True


def is_process_alive(pid: int) -> bool:
    """Check if the hiring process is still alive."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)  # Signal 0 = check existence
        return True
    except OSError:
        return False


# =============================================================================
# HIRE OPERATIONS
# =============================================================================

def try_hire(consumer: str, duration: int = DEFAULT_DURATION) -> bool:
    """
    Try to hire Cerebras. Returns True if successful.
    Non-blocking - returns immediately if not available.
    """
    duration = min(duration, MAX_DURATION)

    # Check current state
    state = load_state()

    # If hired but expired or process dead, release it
    if state.hired:
        if is_expired(state) or not is_process_alive(state.pid):
            print(f"Previous hire expired/orphaned (was: {state.consumer})")
            state = HireState()
            save_state(state)
        else:
            return False  # Still actively hired

    # Try to acquire
    now = datetime.now()
    expires = now + timedelta(seconds=duration)

    new_state = HireState(
        hired=True,
        consumer=consumer,
        hired_at=now.isoformat(),
        expires_at=expires.isoformat(),
        duration=duration,
        pid=os.getpid()
    )
    save_state(new_state)

    return True


def do_hire(consumer: str, duration: int = DEFAULT_DURATION,
            timeout: int = 0, poll_interval: int = 5) -> bool:
    """
    Hire Cerebras, waiting if necessary.

    Args:
        consumer: Who is hiring
        duration: How long to hire for
        timeout: Max time to wait (0 = wait forever)
        poll_interval: Seconds between retry attempts

    Returns:
        True if hired, False if timeout
    """
    start = time.time()

    while True:
        if try_hire(consumer, duration):
            return True

        # Check timeout
        if timeout > 0 and (time.time() - start) > timeout:
            return False

        # Show who has it
        state = load_state()
        remaining = 0
        if state.expires_at:
            try:
                expires = datetime.fromisoformat(state.expires_at)
                remaining = max(0, (expires - datetime.now()).total_seconds())
            except Exception:
                pass

        print(f"Cerebras hired by '{state.consumer}' - {remaining:.0f}s remaining. Waiting...")
        time.sleep(poll_interval)


def do_release():
    """Release Cerebras hire."""
    state = load_state()

    # Only release if we own it
    if state.pid != os.getpid() and state.pid > 0:
        if is_process_alive(state.pid):
            print(f"Warning: Releasing hire owned by PID {state.pid}")

    save_state(HireState())
    print("Cerebras released")


def force_release():
    """Force release regardless of owner."""
    state = load_state()
    if state.hired:
        print(f"Force releasing from '{state.consumer}' (PID {state.pid})")
    save_state(HireState())
    print("Cerebras force released")


def get_status() -> dict:
    """Get current hire status."""
    state = load_state()

    if not state.hired:
        return {"available": True, "hired": False}

    # Check if actually valid
    if is_expired(state):
        return {"available": True, "hired": False, "note": "Previous hire expired"}

    if not is_process_alive(state.pid):
        return {"available": True, "hired": False, "note": "Previous hire orphaned"}

    # Calculate remaining time
    remaining = 0
    try:
        expires = datetime.fromisoformat(state.expires_at)
        remaining = max(0, (expires - datetime.now()).total_seconds())
    except Exception:
        pass

    return {
        "available": False,
        "hired": True,
        "consumer": state.consumer,
        "hired_at": state.hired_at,
        "expires_at": state.expires_at,
        "remaining_seconds": remaining,
        "pid": state.pid
    }


# =============================================================================
# CONTEXT MANAGER
# =============================================================================

@contextmanager
def hire_cerebras(consumer: str, duration: int = DEFAULT_DURATION,
                  timeout: int = 0):
    """
    Context manager for exclusive Cerebras access.

    Usage:
        from cerebras_hire import hire_cerebras

        with hire_cerebras("my-sweep", duration=600):
            # Exclusive access to Cerebras here
            run_sweep()
    """
    if not do_hire(consumer, duration, timeout):
        raise TimeoutError(f"Could not hire Cerebras within {timeout}s")

    try:
        yield
    finally:
        do_release()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Cerebras Hire Mechanism")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # status
    subparsers.add_parser("status", help="Check hire status")

    # hire
    hire_p = subparsers.add_parser("hire", help="Hire Cerebras")
    hire_p.add_argument("--consumer", required=True, help="Who is hiring")
    hire_p.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                        help=f"Duration in seconds (max {MAX_DURATION})")
    hire_p.add_argument("--timeout", type=int, default=0,
                        help="Max wait time (0 = forever)")

    # release
    subparsers.add_parser("release", help="Release hire")

    # force-release
    subparsers.add_parser("force-release", help="Force release (emergency)")

    args = parser.parse_args()

    if args.command == "status":
        status = get_status()
        print("=" * 50)
        print("CEREBRAS HIRE STATUS")
        print("=" * 50)
        if status["available"]:
            print("Status: AVAILABLE")
            if "note" in status:
                print(f"Note: {status['note']}")
        else:
            print("Status: HIRED")
            print(f"Consumer: {status['consumer']}")
            print(f"Hired at: {status['hired_at']}")
            print(f"Expires: {status['expires_at']}")
            print(f"Remaining: {status['remaining_seconds']:.0f}s")
            print(f"PID: {status['pid']}")

    elif args.command == "hire":
        print(f"Hiring Cerebras for '{args.consumer}' ({args.duration}s)...")
        if do_hire(args.consumer, args.duration, args.timeout):
            print(f"SUCCESS: Cerebras hired for {args.duration}s")
            print("Remember to release when done!")
        else:
            print("FAILED: Could not hire within timeout")
            sys.exit(1)

    elif args.command == "release":
        do_release()

    elif args.command == "force-release":
        force_release()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
