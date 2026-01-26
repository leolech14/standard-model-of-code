#!/usr/bin/env python3
"""
Play Card - Execute a certified move from the Decision Deck

This is the execution engine that:
1. Loads a card by ID
2. Verifies preconditions
3. Executes steps (with checkpoints)
4. Validates outcomes
5. Updates meters
6. Handles rollback if needed

Usage:
    ./pe deck play CARD-ANA-001
    python play_card.py CARD-ANA-001 --dry-run
    python play_card.py CARD-ANA-001 --auto  # No prompts
"""

import sys
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Get paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent
METERS_FILE = PROJECT_ROOT / ".agent" / "state" / "meters.yaml"
PLAY_LOG = PROJECT_ROOT / ".agent" / "state" / "play_log.yaml"


def load_meters() -> Dict[str, int]:
    """Load current meter values."""
    if METERS_FILE.exists():
        with open(METERS_FILE) as f:
            return yaml.safe_load(f) or {}
    return {
        "focus": 0,
        "reliability": 0,
        "discovery": 0,
        "debt": 0,
        "readiness": 0,
    }


def save_meters(meters: Dict[str, int]):
    """Save meter values."""
    METERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METERS_FILE, 'w') as f:
        yaml.dump(meters, f, default_flow_style=False)


def log_play(card_id: str, outcome: str, details: Dict[str, Any]):
    """Log card play to history."""
    PLAY_LOG.parent.mkdir(parents=True, exist_ok=True)

    history = []
    if PLAY_LOG.exists():
        with open(PLAY_LOG) as f:
            history = yaml.safe_load(f) or []

    history.append({
        "timestamp": datetime.now().isoformat(),
        "card_id": card_id,
        "outcome": outcome,
        **details
    })

    # Keep last 100 plays
    history = history[-100:]

    with open(PLAY_LOG, 'w') as f:
        yaml.dump(history, f, default_flow_style=False)


def update_meters(meters: Dict[str, int], changes: Dict[str, int]) -> Dict[str, int]:
    """Apply meter changes."""
    for key, delta in changes.items():
        if key in meters:
            meters[key] = meters.get(key, 0) + delta
    return meters


class CardPlayer:
    """Execute certified moves from the Decision Deck."""

    def __init__(self, card_id: str, dry_run: bool = False, auto: bool = False):
        self.card_id = card_id.upper()
        self.dry_run = dry_run
        self.auto = auto
        self.card = None
        self.completed_steps = []

    def load_card(self) -> bool:
        """Load card definition."""
        card_path = SCRIPT_DIR / f"{self.card_id}.yaml"
        if not card_path.exists():
            print(f"Error: Card not found: {self.card_id}")
            return False

        with open(card_path) as f:
            self.card = yaml.safe_load(f)
        return True

    def check_preconditions(self) -> tuple[bool, List[str]]:
        """Check if all preconditions are satisfied."""
        failures = []

        for pre in self.card.get("preconditions", []):
            # Check file existence
            if "files_must_exist" in pre:
                for file_path in pre["files_must_exist"]:
                    full_path = PROJECT_ROOT / file_path
                    if not full_path.exists():
                        failures.append(f"Missing file: {file_path}")

            # Simple check evaluation (extend as needed)
            check = pre.get("check", "")
            if check == "session_not_active()":
                session_file = PROJECT_ROOT / ".agent" / "state" / "session.yaml"
                if session_file.exists():
                    failures.append("Session already active")

        return len(failures) == 0, failures

    def prompt_continue(self, message: str) -> bool:
        """Ask user to continue (unless auto mode)."""
        if self.auto:
            return True
        response = input(f"{message} [Y/n]: ").strip().lower()
        return response in ("", "y", "yes")

    def execute_step(self, step: Dict[str, Any], step_num: int) -> bool:
        """Execute a single step."""
        action = step.get("action", "")
        description = step.get("description", "")
        is_checkpoint = step.get("checkpoint", False)

        print(f"\n  Step {step_num}: {action}")
        print(f"  → {description}")

        if self.dry_run:
            print("  [DRY RUN - not executed]")
            return True

        # Handle different action types
        if action.startswith("./") or action.startswith("python") or action.startswith("cd "):
            # Shell command
            if is_checkpoint and not self.prompt_continue("Execute this step?"):
                return False

            try:
                result = subprocess.run(
                    action,
                    shell=True,
                    cwd=PROJECT_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 min timeout
                )
                if result.returncode != 0:
                    print(f"  ⚠️  Command failed: {result.stderr[:200]}")
                    return False
                print(f"  ✓ Done")
                return True
            except subprocess.TimeoutExpired:
                print("  ⚠️  Command timed out")
                return False
            except Exception as e:
                print(f"  ⚠️  Error: {e}")
                return False

        elif action.startswith("Load ") or action.startswith("Read ") or action.startswith("Review "):
            # Context loading actions - just acknowledge
            context_file = step.get("context_file")
            if context_file:
                full_path = PROJECT_ROOT / context_file
                if full_path.exists():
                    print(f"  ✓ Context available: {context_file}")
                else:
                    print(f"  ⚠️  Context not found: {context_file}")
            else:
                print(f"  ✓ Acknowledged")
            return True

        elif action.startswith("Check ") or action.startswith("Scan "):
            # Scanning actions
            scan_dir = step.get("scan_directory")
            pattern = step.get("pattern", "*")
            if scan_dir:
                full_path = PROJECT_ROOT / scan_dir
                if full_path.exists():
                    count = len(list(full_path.glob(pattern)))
                    print(f"  ✓ Found {count} items matching {pattern}")
                else:
                    print(f"  ⚠️  Directory not found: {scan_dir}")
            return True

        elif action.startswith("Initialize ") or action.startswith("Create "):
            # File creation
            creates_file = step.get("creates_file")
            if creates_file and not self.dry_run:
                full_path = PROJECT_ROOT / creates_file
                full_path.parent.mkdir(parents=True, exist_ok=True)
                # Create minimal file
                with open(full_path, 'w') as f:
                    yaml.dump({
                        "created": datetime.now().isoformat(),
                        "card": self.card_id,
                        "status": "ACTIVE"
                    }, f)
                print(f"  ✓ Created: {creates_file}")
            return True

        elif action.startswith("Display "):
            # Display actions
            read_file = step.get("read_file")
            if read_file:
                full_path = PROJECT_ROOT / read_file
                if full_path.exists():
                    print(f"  ✓ {read_file} available")
                else:
                    print(f"  ⚠️  {read_file} not found")
            return True

        else:
            # Manual action - prompt user
            if not self.prompt_continue("Complete this action manually and confirm?"):
                return False
            print(f"  ✓ Confirmed by user")
            return True

    def apply_outcome(self, outcome_type: str):
        """Apply success or failure outcome."""
        outcomes = self.card.get("outcomes", {})
        outcome = outcomes.get(outcome_type, {})

        # Update meters
        meter_changes = outcome.get("meters", {})
        if meter_changes:
            meters = load_meters()
            meters = update_meters(meters, meter_changes)
            save_meters(meters)
            print(f"\n  Meters updated: {meter_changes}")

        # Log the play
        log_play(self.card_id, outcome_type, {
            "steps_completed": len(self.completed_steps),
            "meter_changes": meter_changes
        })

    def rollback(self):
        """Execute rollback if available."""
        rollback = self.card.get("rollback", {})
        if not rollback.get("possible", False):
            print("\n  ⚠️  Rollback not available for this card")
            return

        warning = rollback.get("warning", "")
        if warning:
            print(f"\n  ⚠️  Warning: {warning}")

        if not self.prompt_continue("Execute rollback?"):
            return

        for step in rollback.get("steps", []):
            print(f"  Rollback: {step}")
            if not self.dry_run:
                subprocess.run(step, shell=True, cwd=PROJECT_ROOT)

    def play(self) -> bool:
        """Execute the card."""
        # Load card
        if not self.load_card():
            return False

        print(f"\n{'='*60}")
        print(f"PLAYING: {self.card.get('title', self.card_id)}")
        print(f"{'='*60}")
        print(f"\n{self.card.get('description', '')}")

        if self.dry_run:
            print("\n[DRY RUN MODE - No changes will be made]")

        # Check preconditions
        print("\n--- Preconditions ---")
        ok, failures = self.check_preconditions()
        if not ok:
            print("  ❌ Preconditions not met:")
            for f in failures:
                print(f"     - {f}")
            self.apply_outcome("failure")
            return False
        print("  ✓ All preconditions satisfied")

        # Execute steps
        print("\n--- Steps ---")
        steps = self.card.get("steps", [])

        for i, step in enumerate(steps, 1):
            if not self.execute_step(step, i):
                print(f"\n  ❌ Step {i} failed")
                if self.prompt_continue("Attempt rollback?"):
                    self.rollback()
                self.apply_outcome("failure")
                return False
            self.completed_steps.append(step)

        # Success
        print("\n--- Complete ---")
        print(f"  ✓ All {len(steps)} steps completed")
        self.apply_outcome("success")

        # Show unlocked cards
        unlocks = self.card.get("outcomes", {}).get("success", {}).get("unlocks", [])
        if unlocks:
            print(f"\n  🔓 Unlocked: {', '.join(unlocks)}")

        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Play a certified move from the Decision Deck")
    parser.add_argument("card_id", help="Card ID (e.g., CARD-ANA-001)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without executing")
    parser.add_argument("--auto", action="store_true", help="No prompts, auto-confirm all steps")

    args = parser.parse_args()

    player = CardPlayer(args.card_id, dry_run=args.dry_run, auto=args.auto)
    success = player.play()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
