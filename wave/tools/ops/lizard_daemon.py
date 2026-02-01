
#!/usr/bin/env python3
"""
🦎 THE LIZARD DAEMON
====================
"Like a lizard gets its tail back."

This daemon watches the Codome (src/core) for changes.
When a file is modified, created, or deleted, it triggers the
Entanglement Mechanism to update the Contextome (docs/core).

Concepts:
- Bit-Threads: The active link between Code and Doc.
- AdS/CFT: Code is the Boundary, Doc is the Bulk.
"""

import sys
import time
import os
import subprocess
from pathlib import Path
# from watchdog imports removed for pure stdlib polling



# Configuration
CODE_ROOT = Path("particle/src/core").resolve()
DOC_ROOT = Path("particle/docs/core").resolve()

def get_file_states(root: Path):
    """Snapshot current mtimes of all .py files."""
    state = {}
    for path in root.rglob("*.py"):
        try:
            state[path] = path.stat().st_mtime
        except OSError:
            pass
    return state

def start_lizard():
    print(f"🦎 Lizard Daemon Active (Polling Mode).")
    print(f"   Watching: {CODE_ROOT}")
    print(f"   Entangled with: {DOC_ROOT}")
    print(f"   Bit-threads are tensioned. Ctrl+C to sever.")

    # Initial State
    last_state = get_file_states(CODE_ROOT)

    try:
        while True:
            time.sleep(2)  # 2-second heartbeat
            current_state = get_file_states(CODE_ROOT)

            # Detect Changes
            modified = []
            for path, mtime in current_state.items():
                if path not in last_state:
                    print(f"\n🦎 [DETECTED] CREATED: {path.name}")
                    modified.append(path)
                elif mtime > last_state[path]:
                    print(f"\n🦎 [DETECTED] MODIFIED: {path.name}")
                    modified.append(path)

            # Detect Deletions
            for path in last_state:
                if path not in current_state:
                    print(f"\n🦎 [SEVERED] DELETED: {path.name}")
                    # In full protocol, we might regenerate or archive

            if modified:
                print(f"   → Vibrating bit-thread...")
                try:
                    # Run Self-Analysis
                    cmd = [sys.executable, "wave/tools/ops/self_analysis.py"]
                    subprocess.run(cmd, check=True)
                    print(f"   → ✨ Symmetry Restored.")
                except subprocess.CalledProcessError as e:
                    print(f"   → ❌ Regeneration Failed: {e}")

            last_state = current_state

    except KeyboardInterrupt:
        print("\n🦎 Lizard Daemon Severed.")

if __name__ == "__main__":
    start_lizard()
