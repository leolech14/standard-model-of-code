#!/usr/bin/env python3
"""
CODOME Manifest Validator
=========================
Validates that CODOME_MANIFEST.yaml accurately reflects the actual codebase.

Usage:
    python .agent/tools/validate_manifest.py
    python .agent/tools/validate_manifest.py --fix  # Auto-fix missing entries
"""

import sys
from pathlib import Path
import yaml

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
MANIFEST_PATH = PROJECT_ROOT / ".agent/CODOME_MANIFEST.yaml"


def load_manifest():
    """Load the CODOME manifest."""
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def validate_paths(manifest: dict) -> tuple[list, list]:
    """Validate all paths in manifest exist."""
    missing = []
    valid = []

    def check_path(path_str: str, context: str):
        full_path = PROJECT_ROOT / path_str
        if full_path.exists():
            valid.append((path_str, context))
        else:
            missing.append((path_str, context))

    # Check realms
    for realm_name, realm in manifest.get('realms', {}).items():
        if 'path' in realm:
            check_path(realm['path'], f"realm.{realm_name}")
        if 'entry_point' in realm and realm['entry_point']:
            check_path(realm['entry_point'], f"realm.{realm_name}.entry_point")
        if 'claude_md' in realm and realm['claude_md']:
            check_path(realm['claude_md'], f"realm.{realm_name}.claude_md")

    # Check canonical docs
    for doc_name, doc in manifest.get('canonical_docs', {}).items():
        if 'path' in doc:
            check_path(doc['path'], f"canonical_docs.{doc_name}")

    # Check tools
    for tool_name, tool in manifest.get('tools', {}).items():
        if 'path' in tool:
            check_path(tool['path'], f"tools.{tool_name}")

    # Check configs
    for config_name, config in manifest.get('configs', {}).items():
        if 'path' in config:
            check_path(config['path'], f"configs.{config_name}")

    # Check schemas
    for schema_name, schema in manifest.get('schemas', {}).items():
        if 'path' in schema:
            check_path(schema['path'], f"schemas.{schema_name}")

    # Check specs
    for spec_name, spec in manifest.get('specs', {}).items():
        if 'path' in spec:
            check_path(spec['path'], f"specs.{spec_name}")

    # Check visualization
    viz = manifest.get('visualization', {})
    if 'template' in viz:
        check_path(viz['template'], "visualization.template")
    if 'styles' in viz:
        check_path(viz['styles'], "visualization.styles")
    if 'modules_dir' in viz:
        check_path(viz['modules_dir'], "visualization.modules_dir")

    # Check research paths
    for research_name, research in manifest.get('research', {}).items():
        if 'path' in research:
            check_path(research['path'], f"research.{research_name}")

    return valid, missing


def find_orphans(manifest: dict) -> list:
    """Find important files not tracked in manifest."""
    orphans = []

    # Key directories to check
    check_dirs = [
        ("standard-model-of-code/docs/specs", "*.md"),
        ("standard-model-of-code/src/core", "*.py"),
        ("context-management/tools/ai", "*.py"),
        ("context-management/config", "*.yaml"),
    ]

    # Collect all tracked paths from manifest
    tracked = set()

    def collect_paths(obj, prefix=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == 'path' and isinstance(v, str):
                    tracked.add(v)
                elif k == 'paths' and isinstance(v, list):
                    tracked.update(v)
                else:
                    collect_paths(v, f"{prefix}.{k}")
        elif isinstance(obj, list):
            for item in obj:
                collect_paths(item, prefix)

    collect_paths(manifest)

    # Check for untracked files
    # Ignore common boilerplate files
    ignore_names = {"__init__.py", "__pycache__", ".DS_Store"}

    for dir_path, pattern in check_dirs:
        full_dir = PROJECT_ROOT / dir_path
        if full_dir.exists():
            for file_path in full_dir.glob(pattern):
                if file_path.name in ignore_names:
                    continue
                rel_path = str(file_path.relative_to(PROJECT_ROOT))
                if rel_path not in tracked:
                    orphans.append((rel_path, dir_path))

    return orphans


def print_report(valid: list, missing: list, orphans: list):
    """Print validation report."""
    print("=" * 60)
    print("CODOME MANIFEST VALIDATION REPORT")
    print("=" * 60)
    print()

    # Summary
    total_paths = len(valid) + len(missing)
    print(f"SUMMARY:")
    print(f"  Valid paths:   {len(valid)}/{total_paths}")
    print(f"  Missing paths: {len(missing)}/{total_paths}")
    print(f"  Orphan files:  {len(orphans)}")
    print()

    # Missing paths (critical)
    if missing:
        print("-" * 60)
        print("MISSING PATHS (manifest references non-existent files):")
        print("-" * 60)
        for path, context in missing:
            print(f"  [MISSING] {path}")
            print(f"            Context: {context}")
        print()

    # Orphans (warning)
    if orphans:
        print("-" * 60)
        print("ORPHAN FILES (exist but not tracked in manifest):")
        print("-" * 60)
        for path, dir_path in orphans[:20]:  # Limit to 20
            print(f"  [ORPHAN] {path}")
        if len(orphans) > 20:
            print(f"  ... and {len(orphans) - 20} more")
        print()

    # Health score
    if total_paths > 0:
        health = len(valid) / total_paths * 100
        print("-" * 60)
        print(f"MANIFEST HEALTH: {health:.1f}%")
        if health == 100 and not orphans:
            print("STATUS: FULLY COHERENT")
        elif health >= 90:
            print("STATUS: MOSTLY COHERENT (minor gaps)")
        elif health >= 70:
            print("STATUS: PARTIAL COHERENCE (needs attention)")
        else:
            print("STATUS: DISINTEGRATED (critical)")
        print("-" * 60)

    # Only missing paths are critical failures
    # Orphans are warnings (especially __init__.py which is boilerplate)
    return len(missing) == 0


def main():
    print(f"Loading manifest from: {MANIFEST_PATH}")
    manifest = load_manifest()

    print(f"Validating paths against: {PROJECT_ROOT}")
    valid, missing = validate_paths(manifest)

    print(f"Scanning for orphan files...")
    orphans = find_orphans(manifest)

    is_healthy = print_report(valid, missing, orphans)

    sys.exit(0 if is_healthy else 1)


if __name__ == "__main__":
    main()
