#!/usr/bin/env python3
"""
Architectural Symmetry Validator (Holonic Edition)
==================================================
Part of Phase 8: Systematic Architectural Enforcement

Checks for symmetry between Codome (Code) and Contextome (Docs)
based on existing meta-registries:
- .agent/META_REGISTRY.yaml
- context-management/config/documentation_map.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
CONFIG_DIR = PROJECT_ROOT / "context-management" / "config"
META_REGISTRY = PROJECT_ROOT / ".agent" / "META_REGISTRY.yaml"
DOC_MAP = CONFIG_DIR / "documentation_map.yaml"

def load_yaml(path: Path) -> Dict:
    if not path.exists():
        print(f"Warning: {path} not found.")
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def check_path(rel_path: str) -> bool:
    # Handle globs if present
    if "*" in rel_path:
        # PROJECT_ROOT.glob returns generators, we check if any exist
        return any(PROJECT_ROOT.glob(rel_path))
    full_path = PROJECT_ROOT / rel_path
    return full_path.exists()

def validate_meta_registry():
    print("\n--- [ Meta-Registry Symmetry Check ] ---")
    data = load_yaml(META_REGISTRY)
    if not data: return

    # Check Body/Brain/Archive roots
    categories = ["body", "brain", "archive"]
    for cat in categories:
        if cat in data:
            # Handle different keys in meta-registry
            root = data[cat].get("root") or data[cat].get("local")
            if root:
                status = "OK" if check_path(root) else "FAIL"
                print(f"[{status}] Universe: {cat:7} | Root: {root}")

            entry = data[cat].get("entry") or data[cat].get("pipeline")
            if entry:
                status = "OK" if check_path(entry) else "FAIL"
                print(f"[{status}] Entry:    {cat:7} | File: {entry}")

    # Check High-Order Registries (Meta)
    if "meta" in data:
        print("\n--- [ High-Order (ROR/LOL/SOS) Symmetry ] ---")
        for key, path in data["meta"].items():
            status = "OK" if check_path(path) else "FAIL"
            print(f"[{status}] Meta: {key.upper():7} | Path: {path}")

def validate_holarchy_symmetry():
    print("\n--- [ High-Order Holarchy Consistency (ROR/LOL/SOS) ] ---")
    data = load_yaml(META_REGISTRY)
    if not data or "meta" not in data: return

    meta = data["meta"]
    lol_path = PROJECT_ROOT / meta["lol"]
    ror_path = PROJECT_ROOT / meta["ror"]
    sos_path = PROJECT_ROOT / meta["sos"]

    # Check if SOS references S1 (Collider) consistent with LOL
    if check_path(meta["lol"]) and check_path(meta["sos"]):
        with open(sos_path, 'r') as f:
            sos_content = f.read()
            if "S1 (Collider)" in sos_content:
                print("[OK] SOS correctly references S1 (Collider) via LOL.")
            else:
                print("[FAIL] SOS reference to LOL Subsystem S1 for S1 is missing or incorrect.")

    # Check if ROR contains the High-Order Holarchy table
    if check_path(meta["ror"]):
        with open(ror_path, 'r') as f:
            ror_content = f.read()
            if "The High-Order Holarchy (ROR, LOL, SOS)" in ror_content:
                print("[OK] ROR correctly defines the High-Order Holarchy specialized roles.")
            else:
                print("[FAIL] ROR is missing the High-Order Holarchy definition.")

def validate_doc_map_symmetry():
    print("\n--- [ Holonic Symmetry Score (Doc Map) ] ---")
    data = load_yaml(DOC_MAP)
    docs = data.get("documentation", {})

    total_checks = 0
    passed_checks = 0

    for doc_path, meta in docs.items():
        doc_exists = check_path(doc_path)
        validates = meta.get("validates_against", [])

        status = "OK  " if doc_exists else "FAIL"
        print(f"[{status}] Doc: {doc_path}")

        if doc_exists:
            passed_checks += 1
        total_checks += 1

        for v_path in validates:
            v_exists = check_path(v_path)
            v_status = "✓" if v_exists else "✗"
            print(f"  {v_status} Validates against: {v_path}")
            if v_exists:
                passed_checks += 1
            total_checks += 1

    score = passed_checks / total_checks if total_checks > 0 else 0
    print(f"\nOverall Symmetry Score: {score:.2f}")

def validate_subsystems_symmetry():
    print("\n--- [ Subsystem Symmetry Check (SUBSYSTEMS.yaml) ] ---")
    data = load_yaml(META_REGISTRY)
    if not data or "meta" not in data or "subsystems" not in data["meta"]:
        return

    sub_path = PROJECT_ROOT / data["meta"]["subsystems"]
    sub_registry = load_yaml(sub_path)
    if not sub_registry: return

    subsystems = sub_registry.get("subsystems", [])

    for sub in subsystems:
        name = sub.get("name")
        root_dirs = sub.get("root_dirs", {})
        code_root = root_dirs.get("code")
        context_root = root_dirs.get("context")

        status = "OK  "
        code_exists = check_path(code_root) if code_root else False
        context_exists = check_path(context_root) if context_root else False

        if not code_exists or not context_exists:
            status = "FAIL"

        print(f"[{status}] Subsystem: {name:15}")
        print(f"  {'✓' if code_exists else '✗'} Code:    {code_root}")
        print(f"  {'✓' if context_exists else '✗'} Context: {context_root}")

def main():
    if not META_REGISTRY.exists() or not DOC_MAP.exists():
        print("Error: Canonical registries missing.")
        print(f"Checked: {META_REGISTRY}")
        print(f"Checked: {DOC_MAP}")
        return

    validate_meta_registry()
    validate_holarchy_symmetry()
    validate_subsystems_symmetry()
    validate_doc_map_symmetry()
    print("\nValidation complete.")

if __name__ == "__main__":
    main()
