#!/usr/bin/env python3
"""
Sprint Manager CLI - Manages sprint lifecycle transitions.

Usage:
    ./sprint.py status                    # Show current sprint status
    ./sprint.py list                      # List all sprints
    ./sprint.py start <sprint-id>         # Move sprint to EXECUTING
    ./sprint.py validate <sprint-id>      # Move sprint to VALIDATING
    ./sprint.py complete <sprint-id>      # Move sprint to COMPLETE
    ./sprint.py dod <sprint-id>           # Check Definition of Done

Part of the Agent System Foundation.
See: .agent/OPEN_CONCERNS.md
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone

SPRINTS_DIR = Path(__file__).parent.parent / "sprints"
ARCHIVE_DIR = SPRINTS_DIR / "archive"


def load_sprint(sprint_id: str) -> tuple[Path, dict]:
    """Load a sprint file by ID."""
    # Check active sprints
    sprint_file = SPRINTS_DIR / f"{sprint_id}.yaml"
    if sprint_file.exists():
        with open(sprint_file) as f:
            return sprint_file, yaml.safe_load(f)

    # Check archive
    archive_file = ARCHIVE_DIR / f"{sprint_id}.yaml"
    if archive_file.exists():
        with open(archive_file) as f:
            return archive_file, yaml.safe_load(f)

    raise FileNotFoundError(f"Sprint {sprint_id} not found")


def save_sprint(path: Path, data: dict):
    """Save sprint data back to file."""
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def transition_sprint(sprint_id: str, new_status: str):
    """Transition a sprint to a new status."""
    valid_transitions = {
        "DESIGNING": ["EXECUTING"],
        "EXECUTING": ["VALIDATING"],
        "VALIDATING": ["COMPLETE", "EXECUTING"],  # Can go back if validation fails
        "COMPLETE": [],  # Terminal state
    }

    path, sprint = load_sprint(sprint_id)
    current_status = sprint.get("status", "DESIGNING")

    if new_status not in valid_transitions.get(current_status, []):
        print(f"ERROR: Cannot transition from {current_status} to {new_status}")
        print(f"Valid transitions from {current_status}: {valid_transitions.get(current_status, [])}")
        return False

    sprint["status"] = new_status
    sprint[f"{new_status.lower()}_at"] = datetime.now(timezone.utc).isoformat()

    save_sprint(path, sprint)
    print(f"Sprint {sprint_id}: {current_status} -> {new_status}")
    return True


def check_dod(sprint_id: str):
    """Check Definition of Done for a sprint."""
    _, sprint = load_sprint(sprint_id)

    dod_items = sprint.get("definition_of_done", [])
    if not dod_items:
        print(f"No Definition of Done for {sprint_id}")
        return

    print(f"\n{'='*60}")
    print(f"Definition of Done: {sprint_id}")
    print(f"{'='*60}\n")

    done_count = 0
    total_count = len(dod_items)

    for item in dod_items:
        item_id = item.get("id", "?")
        desc = item.get("description", "No description")
        status = item.get("status", "PENDING")
        evidence = item.get("evidence", "")

        symbol = "✅" if status == "DONE" else "⬜"
        if status == "DONE":
            done_count += 1

        print(f"  {symbol} [{item_id}] {desc}")
        if evidence:
            print(f"      Evidence: {evidence}")

    print(f"\n{'─'*60}")
    print(f"Progress: {done_count}/{total_count} ({100*done_count//total_count}%)")

    if done_count == total_count:
        print("🎉 All DOD items complete! Sprint can be marked COMPLETE.")
    else:
        print(f"⚠️  {total_count - done_count} items remaining before completion.")


def show_status():
    """Show status of all active sprints."""
    print(f"\n{'='*60}")
    print("SPRINT STATUS")
    print(f"{'='*60}\n")

    sprints = list(SPRINTS_DIR.glob("SPRINT-*.yaml"))

    if not sprints:
        print("No active sprints found.")
        return

    for sprint_file in sorted(sprints):
        with open(sprint_file) as f:
            sprint = yaml.safe_load(f)

        sprint_id = sprint.get("id", sprint_file.stem)
        name = sprint.get("name", "Unnamed")
        status = sprint.get("status", "UNKNOWN")
        target = sprint.get("target_completion", "No target")

        status_emoji = {
            "DESIGNING": "📝",
            "EXECUTING": "🚀",
            "VALIDATING": "🔍",
            "COMPLETE": "✅",
        }.get(status, "❓")

        print(f"  {status_emoji} {sprint_id}: {name}")
        print(f"      Status: {status} | Target: {target}")
        print()


def list_sprints():
    """List all sprints including archived."""
    print(f"\n{'='*60}")
    print("ALL SPRINTS")
    print(f"{'='*60}\n")

    # Active
    print("Active:")
    active = list(SPRINTS_DIR.glob("SPRINT-*.yaml"))
    for f in sorted(active):
        print(f"  - {f.stem}")

    if not active:
        print("  (none)")

    # Archived
    print("\nArchived:")
    archived = list(ARCHIVE_DIR.glob("SPRINT-*.yaml")) if ARCHIVE_DIR.exists() else []
    for f in sorted(archived):
        print(f"  - {f.stem}")

    if not archived:
        print("  (none)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1]

    if command == "status":
        show_status()
    elif command == "list":
        list_sprints()
    elif command == "dod" and len(sys.argv) >= 3:
        check_dod(sys.argv[2])
    elif command == "start" and len(sys.argv) >= 3:
        transition_sprint(sys.argv[2], "EXECUTING")
    elif command == "validate" and len(sys.argv) >= 3:
        transition_sprint(sys.argv[2], "VALIDATING")
    elif command == "complete" and len(sys.argv) >= 3:
        transition_sprint(sys.argv[2], "COMPLETE")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
