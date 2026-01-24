#!/usr/bin/env python3
"""
Delta Detector
===============
Compares current corpus state to previous inventory and detects changes.
Implements the "Delta-First" principle - only reprocess what changed.

Output: context-management/intelligence/delta_report.json

Usage:
    python delta_detector.py                      # Detect changes since last run
    python delta_detector.py --baseline FILE      # Compare against specific baseline
    python delta_detector.py --since "2026-01-20" # Changes since date
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INTELLIGENCE_DIR = PROJECT_ROOT / "context-management/intelligence"
CORPUS_INVENTORY_PATH = INTELLIGENCE_DIR / "corpus_inventory.json"
DELTA_STATE_PATH = INTELLIGENCE_DIR / "delta_state.json"

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

def load_state() -> Dict[str, Any]:
    """Load previous delta state (file hashes from last run)."""
    if DELTA_STATE_PATH.exists():
        with open(DELTA_STATE_PATH, 'r') as f:
            return json.load(f)
    return {"last_run": None, "file_hashes": {}}


def save_state(state: Dict[str, Any]):
    """Save current state for next comparison."""
    state["last_run"] = datetime.now().isoformat()
    with open(DELTA_STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


# ============================================================================
# DELTA DETECTION
# ============================================================================

def detect_deltas(
    current_inventory: Dict[str, Any],
    previous_hashes: Dict[str, str]
) -> Dict[str, Any]:
    """
    Compare current inventory to previous state.

    Returns:
        {
            "added": [...],      # New files
            "modified": [...],   # Changed files
            "deleted": [...],    # Removed files
            "unchanged": count   # Unchanged file count
        }
    """
    current_files = {f["path"]: f["content_hash"] for f in current_inventory.get("files", [])}
    current_paths: Set[str] = set(current_files.keys())
    previous_paths: Set[str] = set(previous_hashes.keys())

    # Detect changes
    added = current_paths - previous_paths
    deleted = previous_paths - current_paths
    common = current_paths & previous_paths

    modified = []
    unchanged = 0

    for path in common:
        if current_files[path] != previous_hashes.get(path):
            modified.append(path)
        else:
            unchanged += 1

    return {
        "added": sorted(added),
        "modified": sorted(modified),
        "deleted": sorted(deleted),
        "unchanged": unchanged
    }


def get_file_details(paths: List[str], inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get full details for a list of file paths."""
    file_map = {f["path"]: f for f in inventory.get("files", [])}
    return [file_map[p] for p in paths if p in file_map]


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Delta Detector - Detect changes since last run"
    )
    parser.add_argument("--baseline", type=str, default=None,
                        help="Path to baseline inventory to compare against")
    parser.add_argument("--output", type=str, default=None,
                        help="Custom output path")
    parser.add_argument("--update-state", action="store_true", default=True,
                        help="Update state file after detection (default: True)")
    parser.add_argument("--no-update-state", dest="update_state", action="store_false",
                        help="Don't update state file")

    args = parser.parse_args()

    output_path = Path(args.output) if args.output else INTELLIGENCE_DIR / "delta_report.json"

    # Load current inventory
    if not CORPUS_INVENTORY_PATH.exists():
        print("ERROR: No corpus inventory found. Run corpus_inventory.py first.")
        return 1

    with open(CORPUS_INVENTORY_PATH, 'r') as f:
        current_inventory = json.load(f)

    # Load baseline (previous state)
    if args.baseline:
        with open(args.baseline, 'r') as f:
            baseline = json.load(f)
        previous_hashes = {f["path"]: f["content_hash"] for f in baseline.get("files", [])}
        baseline_source = args.baseline
    else:
        state = load_state()
        previous_hashes = state.get("file_hashes", {})
        baseline_source = str(DELTA_STATE_PATH) if state.get("last_run") else "initial_run"

    # Detect deltas
    deltas = detect_deltas(current_inventory, previous_hashes)

    # Build report
    report = {
        "meta": {
            "tool": "delta_detector",
            "version": "1.0.0",
            "detected_at": datetime.now().isoformat(),
            "baseline_source": baseline_source,
            "current_inventory": str(CORPUS_INVENTORY_PATH)
        },
        "summary": {
            "added": len(deltas["added"]),
            "modified": len(deltas["modified"]),
            "deleted": len(deltas["deleted"]),
            "unchanged": deltas["unchanged"],
            "total_changes": len(deltas["added"]) + len(deltas["modified"]) + len(deltas["deleted"]),
            "has_changes": len(deltas["added"]) + len(deltas["modified"]) + len(deltas["deleted"]) > 0
        },
        "changes": {
            "added": get_file_details(deltas["added"], current_inventory),
            "modified": get_file_details(deltas["modified"], current_inventory),
            "deleted": [{"path": p} for p in deltas["deleted"]]  # No details for deleted
        }
    }

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    # Update state for next run
    if args.update_state:
        new_state = {
            "file_hashes": {f["path"]: f["content_hash"] for f in current_inventory.get("files", [])}
        }
        save_state(new_state)

    # Summary
    print(f"\nDelta Detection Complete:")
    print(f"  Added:     {report['summary']['added']}")
    print(f"  Modified:  {report['summary']['modified']}")
    print(f"  Deleted:   {report['summary']['deleted']}")
    print(f"  Unchanged: {report['summary']['unchanged']}")
    print(f"  Output:    {output_path}")

    if report['summary']['has_changes']:
        print(f"\n  Top changes:")
        for f in report['changes']['added'][:5]:
            print(f"    + {f['path']}")
        for f in report['changes']['modified'][:5]:
            print(f"    ~ {f['path']}")
        for f in report['changes']['deleted'][:5]:
            print(f"    - {f['path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
