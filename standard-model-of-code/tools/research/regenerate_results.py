#!/usr/bin/env python3
"""
Deterministic Results Regenerator

Regenerates results.json from coverage.json files in repos/.
This ensures results.json is always derived, never hand-edited.

Usage:
    python tools/research/regenerate_results.py artifacts/atom-research/2026-01-22/
    python tools/research/regenerate_results.py artifacts/atom-research/2026-01-22/ --verify
"""

import argparse
import json
import sys
from pathlib import Path


def regenerate_results(pack_dir: Path) -> list[dict]:
    """
    Scan repos/**/coverage.json and regenerate results.json deterministically.
    """
    repos_dir = pack_dir / "repos"
    if not repos_dir.exists():
        print(f"Error: repos directory not found: {repos_dir}", file=sys.stderr)
        sys.exit(1)

    results = []

    # Scan each repo directory
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue

        repo_name = repo_dir.name

        # Find commit SHA directory
        commit_dirs = [d for d in repo_dir.iterdir() if d.is_dir()]
        if not commit_dirs:
            print(f"Warning: No commit directory in {repo_dir}", file=sys.stderr)
            continue

        # Use the first (should be only) commit directory
        commit_dir = commit_dirs[0]
        commit_sha = commit_dir.name

        # Load coverage.json
        coverage_file = commit_dir / "coverage.json"
        if not coverage_file.exists():
            print(f"Warning: No coverage.json in {commit_dir}", file=sys.stderr)
            continue

        try:
            with open(coverage_file) as f:
                coverage = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {coverage_file}: {e}", file=sys.stderr)
            continue

        metrics = coverage.get("metrics", {})

        # Build result entry
        result = {
            "name": repo_name,
            "status": "success",
            "sha": commit_sha,
            "n_nodes": metrics.get("n_nodes", 0),
            "top_4_mass": metrics.get("top_4_mass", 0.0),
            "unknown_rate": metrics.get("unknown_rate", 0.0),
            "t2_rate": metrics.get("t2_enrichment_rate", 0.0),
        }
        results.append(result)

    # Sort by name for determinism
    results.sort(key=lambda x: x["name"])

    return results


def verify_results(pack_dir: Path, regenerated: list[dict]) -> tuple[bool, list[str]]:
    """
    Compare regenerated results with existing results.json.
    Returns (match, differences).
    """
    results_file = pack_dir / "results.json"
    differences = []

    if not results_file.exists():
        return False, ["results.json does not exist"]

    try:
        with open(results_file) as f:
            existing = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in results.json: {e}"]

    # Sort existing for comparison
    existing_sorted = sorted(existing, key=lambda x: x.get("name", ""))

    # Compare counts
    if len(regenerated) != len(existing_sorted):
        differences.append(
            f"Repo count mismatch: regenerated={len(regenerated)}, existing={len(existing_sorted)}"
        )

    # Build lookup
    existing_by_name = {r.get("name"): r for r in existing_sorted}

    for regen in regenerated:
        name = regen["name"]
        if name not in existing_by_name:
            differences.append(f"Missing repo in existing: {name}")
            continue

        exist = existing_by_name[name]

        # Compare key fields
        for field in ["n_nodes", "top_4_mass", "unknown_rate"]:
            regen_val = regen.get(field)
            exist_val = exist.get(field)

            # Allow small float tolerance
            if isinstance(regen_val, float) and isinstance(exist_val, float):
                if abs(regen_val - exist_val) > 0.01:
                    differences.append(
                        f"{name}.{field}: regenerated={regen_val}, existing={exist_val}"
                    )
            elif regen_val != exist_val:
                differences.append(
                    f"{name}.{field}: regenerated={regen_val}, existing={exist_val}"
                )

    return len(differences) == 0, differences


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate results.json from coverage.json files"
    )
    parser.add_argument(
        "pack_dir",
        type=Path,
        help="Path to audit pack directory",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing results.json matches regenerated (don't overwrite)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file (default: pack_dir/results.json)",
    )

    args = parser.parse_args()

    # Regenerate
    regenerated = regenerate_results(args.pack_dir)

    if not regenerated:
        print("Error: No repos found", file=sys.stderr)
        sys.exit(1)

    print(f"Regenerated results for {len(regenerated)} repos:")
    for r in regenerated:
        print(f"  - {r['name']}: n_nodes={r['n_nodes']}, top_4_mass={r['top_4_mass']}%")

    if args.verify:
        match, differences = verify_results(args.pack_dir, regenerated)
        if match:
            print("\n[PASS] Existing results.json matches regenerated")
            sys.exit(0)
        else:
            print("\n[FAIL] Differences found:")
            for diff in differences:
                print(f"  - {diff}")
            sys.exit(1)
    else:
        # Write output
        output_file = args.output or (args.pack_dir / "results.json")
        with open(output_file, "w") as f:
            json.dump(regenerated, f, indent=2)
        print(f"\nWrote: {output_file}")


if __name__ == "__main__":
    main()
