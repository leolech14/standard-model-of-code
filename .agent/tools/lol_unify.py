#!/usr/bin/env python3
"""
LOL (List of Lists) Unify - Complete Self-Description Integration
==================================================================
SMoC Role: Integration/Orchestrator/D | static | orchestrator

Merges ALL self-description sources into a unified LOL (List of Lists) inventory:
1. LOL.csv - Base inventory (domain, category, intel_model)
2. Collider SMoC - Atom, role, layer, dimensions
3. TDJ - Temporal dynamics (mtime, ctime, age)
4. Symmetry - Wave-particle balance state
5. Purpose Field - Coherence, alignment

Output: LOL_UNIFIED.csv - The complete self-describing inventory

Usage:
  python lol_unify.py              # Full unification
  python lol_unify.py --stats      # Show integration statistics
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
LOL_CSV = REPO_ROOT / ".agent" / "intelligence" / "LOL.csv"
LOL_SMOC_CSV = REPO_ROOT / ".agent" / "intelligence" / "LOL_SMOC.csv"
LOL_UNIFIED_CSV = REPO_ROOT / ".agent" / "intelligence" / "LOL_UNIFIED.csv"
TDJ_PATH = REPO_ROOT / ".agent" / "intelligence" / "tdj.jsonl"
COLLIDER_DIR = REPO_ROOT / ".collider-full"

# New unified columns
TEMPORAL_COLUMNS = [
    "mtime",           # Last modified timestamp
    "ctime",           # Created timestamp
    "age_days",        # Days since creation
    "freshness",       # FRESH (<7d), RECENT (<30d), STABLE (<90d), AGED (>90d)
]

SYMMETRY_COLUMNS = [
    "symmetry_state",  # SYMMETRIC, ORPHAN (code no doc), PHANTOM (doc no code), DRIFT
]

PURPOSE_COLUMNS = [
    "purpose_clarity", # HIGH, MEDIUM, LOW based on coherence
    "is_god_class",    # True if class has multiple conflicting purposes
]


def load_base_inventory() -> dict:
    """Load LOL_SMOC.csv as base."""
    if LOL_SMOC_CSV.exists():
        source = LOL_SMOC_CSV
    elif LOL_CSV.exists():
        source = LOL_CSV
    else:
        print("ERROR: No LOL (List of Lists) inventory found")
        sys.exit(1)

    entities = {}
    with open(source, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entities[row['path']] = dict(row)

    print(f"Loaded {len(entities)} entities from {source.name}")
    return entities


def load_tdj() -> dict:
    """Load Temporal Daily Journal data."""
    if not TDJ_PATH.exists():
        print("Warning: TDJ not found, skipping temporal data")
        return {}

    temporal = {}
    now = datetime.now().timestamp()

    with open(TDJ_PATH) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("_meta"):
                continue

            path = entry.get("path", "")
            mtime = entry.get("mtime", 0)
            ctime = entry.get("ctime", 0)

            # Calculate age and freshness
            age_days = (now - ctime) / 86400 if ctime else 0

            if age_days < 7:
                freshness = "FRESH"
            elif age_days < 30:
                freshness = "RECENT"
            elif age_days < 90:
                freshness = "STABLE"
            else:
                freshness = "AGED"

            temporal[path] = {
                "mtime": datetime.fromtimestamp(mtime).isoformat() if mtime else "N/A",
                "ctime": datetime.fromtimestamp(ctime).isoformat() if ctime else "N/A",
                "age_days": round(age_days, 1),
                "freshness": freshness,
            }

    print(f"Loaded temporal data for {len(temporal)} files")
    return temporal


def load_symmetry() -> dict:
    """
    Determine symmetry state for each file.

    States:
    - SYMMETRIC: Code has matching documentation
    - ORPHAN: Code exists without documentation
    - PHANTOM: Documentation exists without code
    - DRIFT: Code and docs exist but are misaligned
    """
    # For now, use a heuristic based on file type and location
    # TODO: Integrate actual symmetry_check.py output
    return {}


def load_purpose_field() -> dict:
    """Load purpose field data from Collider output."""
    collider_files = list(COLLIDER_DIR.glob("output_llm-oriented_*.json")) if COLLIDER_DIR.exists() else []

    if not collider_files:
        print("Warning: No Collider output found, skipping purpose field")
        return {}

    # Use most recent
    collider_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    collider_path = collider_files[0]

    with open(collider_path) as f:
        data = json.load(f)

    purpose_data = data.get("purpose_field", {})
    god_classes = {g["name"] for g in purpose_data.get("god_classes", [])}

    # Build per-node purpose info
    purpose_map = {}
    nodes = data.get("nodes", [])

    for node in nodes:
        file_path = node.get("file_path", "")
        if not file_path or file_path.startswith("__"):
            continue

        # Get purpose coherence from node dimensions
        dims = node.get("dimensions", {})
        confidence = node.get("confidence", 0.5)

        # Determine clarity
        if confidence >= 0.8:
            clarity = "HIGH"
        elif confidence >= 0.5:
            clarity = "MEDIUM"
        else:
            clarity = "LOW"

        # Check if it's a god class
        node_name = node.get("name", "")
        is_god = node_name in god_classes

        # Aggregate per file (use worst clarity)
        if file_path not in purpose_map:
            purpose_map[file_path] = {
                "purpose_clarity": clarity,
                "is_god_class": is_god,
            }
        else:
            # Keep worst clarity
            existing = purpose_map[file_path]
            if clarity == "LOW" or (clarity == "MEDIUM" and existing["purpose_clarity"] == "HIGH"):
                existing["purpose_clarity"] = clarity
            if is_god:
                existing["is_god_class"] = True

    print(f"Loaded purpose data for {len(purpose_map)} files")
    return purpose_map


def classify_symmetry(entity: dict, has_doc_pair: bool) -> str:
    """Classify symmetry state based on file characteristics."""
    category = entity.get("category", "")
    domain = entity.get("domain", "")
    path = entity.get("path", "")

    # Documentation files
    if category == "doc":
        # Check if there's corresponding code
        # For now, use heuristic: docs in docs/ folders are likely symmetric
        if "/docs/" in path:
            return "SYMMETRIC"
        return "PHANTOM"  # Doc without clear code reference

    # Code files
    if category in ("source", "tool"):
        smoc_atom = entity.get("smoc_atom", "N/A")
        if smoc_atom == "N/A":
            return "ORPHAN"  # Code not analyzed
        # If code is analyzed, assume it has some documentation
        return "SYMMETRIC"

    # Config, data, schema - don't need symmetry
    return "N/A"


def unify_all(entities: dict, temporal: dict, purpose: dict) -> dict:
    """Merge all data sources into unified entities."""

    all_columns = set()

    for path, entity in entities.items():
        # Add temporal data
        if path in temporal:
            entity.update(temporal[path])
        else:
            for col in TEMPORAL_COLUMNS:
                entity[col] = "N/A"

        # Add purpose data
        # Try different path variations for matching
        purpose_match = None
        for try_path in [path, path.replace("standard-model-of-code/", ""), f"src/{path}"]:
            if try_path in purpose:
                purpose_match = purpose[try_path]
                break

        if purpose_match:
            entity.update(purpose_match)
        else:
            entity["purpose_clarity"] = "N/A"
            entity["is_god_class"] = "N/A"

        # Add symmetry state
        entity["symmetry_state"] = classify_symmetry(entity, False)

        all_columns.update(entity.keys())

    return entities, sorted(all_columns)


def save_unified(entities: dict, columns: list, path: Path):
    """Save unified inventory to CSV."""
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for entity in sorted(entities.values(), key=lambda e: e.get('path', '')):
            writer.writerow(entity)

    print(f"Saved unified inventory to {path}")


def print_stats(entities: dict):
    """Print unification statistics."""
    print("\n" + "=" * 60)
    print("LOL (List of Lists) UNIFIED STATISTICS")
    print("=" * 60)

    # Temporal distribution
    freshness = Counter(e.get("freshness", "N/A") for e in entities.values())
    print("\n## Temporal (Freshness)")
    for f, count in freshness.most_common():
        print(f"  {f:<12} {count}")

    # Symmetry distribution
    symmetry = Counter(e.get("symmetry_state", "N/A") for e in entities.values())
    print("\n## Symmetry State")
    for s, count in symmetry.most_common():
        print(f"  {s:<12} {count}")

    # Purpose clarity
    clarity = Counter(e.get("purpose_clarity", "N/A") for e in entities.values())
    print("\n## Purpose Clarity")
    for c, count in clarity.most_common():
        print(f"  {c:<12} {count}")

    # God classes
    god_count = sum(1 for e in entities.values() if e.get("is_god_class") == True)
    print(f"\n## God Classes (multiple purposes)")
    print(f"  Total: {god_count}")

    # Integration coverage
    print("\n## Integration Coverage")
    has_temporal = sum(1 for e in entities.values() if e.get("freshness") != "N/A")
    has_smoc = sum(1 for e in entities.values() if e.get("smoc_atom") not in ("N/A", None, ""))
    has_purpose = sum(1 for e in entities.values() if e.get("purpose_clarity") != "N/A")
    total = len(entities)

    print(f"  Temporal:  {has_temporal}/{total} ({has_temporal/total*100:.1f}%)")
    print(f"  SMoC:      {has_smoc}/{total} ({has_smoc/total*100:.1f}%)")
    print(f"  Purpose:   {has_purpose}/{total} ({has_purpose/total*100:.1f}%)")

    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unify all LOL (List of Lists) data sources")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    args = parser.parse_args()

    print("LOL (List of Lists) Unify - Creating complete self-description\n")

    # Load all sources
    entities = load_base_inventory()
    temporal = load_tdj()
    purpose = load_purpose_field()

    # Merge everything
    print("\nUnifying data sources...")
    unified, columns = unify_all(entities, temporal, purpose)

    # Save
    save_unified(unified, columns, LOL_UNIFIED_CSV)

    # Stats
    print_stats(unified)


if __name__ == "__main__":
    main()
