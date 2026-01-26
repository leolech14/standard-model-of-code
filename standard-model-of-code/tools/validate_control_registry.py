#!/usr/bin/env python3
"""
UI Control Registry Validator

Enforces: No control in template.html without registry authorization.

Usage:
  # Check if a control is authorized BEFORE implementing
  python validate_control_registry.py --check "new-control-id"

  # Validate template.html against registry (post-implementation)
  python validate_control_registry.py --audit

  # List all authorized controls
  python validate_control_registry.py --list
"""

import argparse
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml")
    sys.exit(1)

REGISTRY_PATH = Path(__file__).parent.parent / "schema/viz/controls/CONTROL_REGISTRY.yaml"
TEMPLATE_PATH = Path(__file__).parent.parent / "src/core/viz/assets/template.html"

# Structural IDs to exclude from control validation
# These are container/panel IDs, not interactive controls
STRUCTURAL_IDS = {
    '3d-graph', 'header', 'loader', 'toast', 'control-bar-container',
    'filtering', 'selection', 'camera', 'accessibility', 'export',
    'analysis', 'layout-phys', 'view-modes', 'panel-settings',
    'node-appear', 'edge-appear'
}


def load_registry():
    """Load the control registry."""
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found at {REGISTRY_PATH}")
        sys.exit(1)

    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def get_registered_ids(registry):
    """Extract all control IDs from registry."""
    ids = set()
    for _, panel_data in registry.get("panels", {}).items():
        for control in panel_data.get("controls", []):
            ids.add(control["id"])
    return ids


def get_authorized_ids(registry):
    """Extract only AUTHORIZED or IMPLEMENTED control IDs."""
    ids = set()
    for _, panel_data in registry.get("panels", {}).items():
        for control in panel_data.get("controls", []):
            if control.get("status") in ("AUTHORIZED", "IMPLEMENTED"):
                ids.add(control["id"])
    return ids


def get_template_ids():
    """Extract control IDs from template.html."""
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Template not found at {TEMPLATE_PATH}")
        sys.exit(1)

    content = TEMPLATE_PATH.read_text()

    # Match id="..." patterns
    ids = set()
    pattern = r'id="([^"]+)"'
    matches = re.findall(pattern, content)
    ids.update(matches)

    return ids


def check_control(control_id):
    """Check if a control ID is authorized."""
    registry = load_registry()
    authorized = get_authorized_ids(registry)

    if control_id in authorized:
        print(f"✅ AUTHORIZED: '{control_id}' is in registry")
        return 0
    else:
        print(f"❌ DENIED: '{control_id}' is NOT in registry")
        print(f"\nTo authorize, add to CONTROL_REGISTRY.yaml with status: AUTHORIZED")
        return 1


def audit_template():
    """Audit template.html against registry."""
    registry = load_registry()
    authorized = get_authorized_ids(registry)
    template_ids = get_template_ids()

    # Find unauthorized controls in template
    unauthorized = template_ids - authorized - STRUCTURAL_IDS
    # Find authorized but not implemented
    missing = authorized - template_ids

    print("=" * 60)
    print("UI CONTROL REGISTRY AUDIT")
    print("=" * 60)
    print(f"Registry controls: {len(authorized)}")
    print(f"Template controls: {len(template_ids)}")
    print(f"Structural (filtered): {len(template_ids & STRUCTURAL_IDS)}")
    print()

    if unauthorized:
        print(f"❌ UNAUTHORIZED ({len(unauthorized)}):")
        for uid in sorted(unauthorized):
            print(f"   - {uid}")
        print()

    if missing:
        print(f"⚠️  AUTHORIZED BUT NOT IMPLEMENTED ({len(missing)}):")
        for uid in sorted(missing):
            print(f"   - {uid}")
        print()

    if not unauthorized and not missing:
        print("✅ PERFECT: All controls authorized and implemented")

    return 1 if unauthorized else 0


def list_controls():
    """List all registered controls."""
    registry = load_registry()

    print("=" * 60)
    print("UI CONTROL REGISTRY")
    print("=" * 60)
    print(f"Version: {registry.get('version', 'unknown')}")
    print(f"Total: {registry.get('total_authorized', 'unknown')}")
    print()

    for panel_name, panel_data in registry.get("panels", {}).items():
        controls = panel_data.get("controls", [])
        print(f"\n{panel_name.upper()} ({len(controls)} controls)")
        print("-" * 40)
        for control in controls:
            status_icon = "✅" if control.get("status") == "IMPLEMENTED" else "⏳"
            print(f"  {status_icon} {control['id']} [{control.get('type', '?')}]")


def main():
    parser = argparse.ArgumentParser(description="UI Control Registry Validator")
    parser.add_argument("--check", metavar="ID", help="Check if control ID is authorized")
    parser.add_argument("--audit", action="store_true", help="Audit template against registry")
    parser.add_argument("--list", action="store_true", help="List all registered controls")

    args = parser.parse_args()

    if args.check:
        sys.exit(check_control(args.check))
    elif args.audit:
        sys.exit(audit_template())
    elif args.list:
        list_controls()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
