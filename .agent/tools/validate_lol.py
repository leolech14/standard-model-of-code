#!/usr/bin/env python3
"""
LOL Validator
=============
SMoC Role: Validation/Completeness/D | static | validator

Tests the TOTALITY AXIOM:
  ∀x. (x under PROJECT_elements/) → (∃L ∈ LOL. x ∈ L)
  "Everything under the hood is in some list."

Usage:
  python validate_lol.py              # Full validation
  python validate_lol.py --quick      # Just counts
  python validate_lol.py --gaps       # Show what's missing
"""

import sys
from pathlib import Path
from collections import defaultdict

import yaml

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
LOL_PATH = REPO_ROOT / ".agent" / "intelligence" / "LOL.yaml"

# Exclusions (not inventoried by design)
EXCLUDED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", ".tools_venv",
    "archive", ".archive", ".collider", "dist", "build", "artifacts",
    ".mypy_cache", ".pytest_cache", "benchmarks", ".DS_Store",
    "llm-threads", "_archive",  # Vendor libs and archived code
}

EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dylib", ".egg-info", ".whl",
    ".log", ".tmp", ".bak", ".swp", ".swo"
}


def load_lol() -> dict:
    """Load LOL.yaml."""
    with open(LOL_PATH) as f:
        return yaml.safe_load(f)


def extract_all_paths_from_lol(data: dict, prefix: str = "") -> set:
    """Recursively extract all file paths mentioned in LOL."""
    paths = set()

    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                # It's a path
                paths.add(item)
            elif isinstance(item, dict):
                paths.update(extract_all_paths_from_lol(item, prefix))
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in ("path", "data", "config", "source"):
                if isinstance(value, str):
                    paths.add(value)
            elif isinstance(value, (dict, list)):
                paths.update(extract_all_paths_from_lol(value, prefix))

    return paths


def get_actual_files(extensions: set = None) -> set:
    """Get all actual files under PROJECT_elements."""
    files = set()

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue

        # Skip excluded directories
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        # Skip excluded extensions
        if path.suffix in EXCLUDED_EXTENSIONS:
            continue

        # Filter by extension if specified
        if extensions and path.suffix not in extensions:
            continue

        # Get relative path
        rel_path = str(path.relative_to(REPO_ROOT))
        files.add(rel_path)

    return files


def validate_file_inventory(lol: dict) -> dict:
    """Validate file inventory completeness."""
    results = {
        "python": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
        "javascript": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
        "yaml": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
    }

    # Get LOL paths from files section
    files_section = lol.get("files", {})

    # Python files
    python_in_lol = extract_all_paths_from_lol(files_section.get("python", {}))
    python_actual = get_actual_files({".py"})

    results["python"]["in_lol"] = len(python_in_lol)
    results["python"]["expected"] = len(python_actual)
    results["python"]["missing"] = sorted(python_actual - python_in_lol)[:20]  # First 20
    results["python"]["extra"] = sorted(python_in_lol - python_actual)[:20]

    # JavaScript files
    js_in_lol = extract_all_paths_from_lol(files_section.get("javascript", {}))
    js_actual = get_actual_files({".js"})

    results["javascript"]["in_lol"] = len(js_in_lol)
    results["javascript"]["expected"] = len(js_actual)
    results["javascript"]["missing"] = sorted(js_actual - js_in_lol)[:20]
    results["javascript"]["extra"] = sorted(js_in_lol - js_actual)[:20]

    # YAML files
    yaml_in_lol = extract_all_paths_from_lol(files_section.get("yaml", {}))
    yaml_actual = get_actual_files({".yaml", ".yml"})

    results["yaml"]["in_lol"] = len(yaml_in_lol)
    results["yaml"]["expected"] = len(yaml_actual)
    results["yaml"]["missing"] = sorted(yaml_actual - yaml_in_lol)[:20]
    results["yaml"]["extra"] = sorted(yaml_in_lol - yaml_actual)[:20]

    return results


def validate_counts(lol: dict) -> dict:
    """Validate declared counts against actual."""
    results = {}

    summary = lol.get("summary", {})
    file_totals = summary.get("file_totals", {})

    # Python count
    python_declared = file_totals.get("python", 0)
    python_actual = len(get_actual_files({".py"}))
    results["python"] = {
        "declared": python_declared,
        "actual": python_actual,
        "match": python_declared == python_actual,
        "delta": python_actual - python_declared
    }

    # JavaScript count
    js_declared = file_totals.get("javascript", 0)
    js_actual = len(get_actual_files({".js"}))
    results["javascript"] = {
        "declared": js_declared,
        "actual": js_actual,
        "match": js_declared == js_actual,
        "delta": js_actual - js_declared
    }

    # YAML count
    yaml_declared = file_totals.get("yaml", 0)
    yaml_actual = len(get_actual_files({".yaml", ".yml"}))
    results["yaml"] = {
        "declared": yaml_declared,
        "actual": yaml_actual,
        "match": yaml_declared == yaml_actual,
        "delta": yaml_actual - yaml_declared
    }

    return results


def validate_tools(lol: dict) -> dict:
    """Validate tool inventory."""
    results = {"listed": 0, "exist": 0, "missing_files": []}

    # Extract tool paths from tool_taxonomy section
    taxonomy = lol.get("tool_taxonomy", {})

    tool_names = set()
    for domain in ["particle_tools", "wave_tools", "observer_tools"]:
        tools = taxonomy.get(domain, [])
        for tool in tools:
            if isinstance(tool, dict) and "name" in tool:
                tool_names.add(tool["name"])

    results["listed"] = len(tool_names)

    # Check if they exist (search common locations)
    tool_dirs = [
        REPO_ROOT / ".agent" / "tools",
        REPO_ROOT / "context-management" / "tools",
        REPO_ROOT / "standard-model-of-code" / "tools",
        REPO_ROOT / "standard-model-of-code" / "src" / "core",
    ]

    for name in tool_names:
        found = False
        for d in tool_dirs:
            if (d / name).exists():
                found = True
                break
            # Search recursively
            matches = list(d.rglob(name)) if d.exists() else []
            if matches:
                found = True
                break

        if found:
            results["exist"] += 1
        else:
            results["missing_files"].append(name)

    return results


def calculate_completeness(file_results: dict) -> float:
    """Calculate overall completeness percentage."""
    total_expected = sum(r["expected"] for r in file_results.values())
    total_in_lol = sum(r["in_lol"] for r in file_results.values())

    if total_expected == 0:
        return 100.0

    return (total_in_lol / total_expected) * 100


def print_report(count_results: dict, file_results: dict, tool_results: dict, show_gaps: bool = False):
    """Print validation report."""
    print("=" * 70)
    print("LOL VALIDATION REPORT")
    print("=" * 70)
    print(f"Testing: {LOL_PATH}")
    print()

    # Count validation
    print("## COUNT VALIDATION")
    print("-" * 40)
    all_match = True
    for ftype, data in count_results.items():
        status = "✓" if data["match"] else "✗"
        delta_str = f" (Δ{data['delta']:+d})" if data["delta"] != 0 else ""
        print(f"  {status} {ftype:12} declared={data['declared']:4}  actual={data['actual']:4}{delta_str}")
        if not data["match"]:
            all_match = False
    print()

    # File inventory validation
    print("## FILE INVENTORY VALIDATION")
    print("-" * 40)
    completeness = calculate_completeness(file_results)
    for ftype, data in file_results.items():
        coverage = (data["in_lol"] / data["expected"] * 100) if data["expected"] > 0 else 100
        status = "✓" if coverage >= 95 else "△" if coverage >= 80 else "✗"
        print(f"  {status} {ftype:12} in_lol={data['in_lol']:4}  expected={data['expected']:4}  coverage={coverage:.1f}%")
    print()
    print(f"  OVERALL COMPLETENESS: {completeness:.1f}%")
    print()

    # Tool validation
    print("## TOOL VALIDATION")
    print("-" * 40)
    tool_coverage = (tool_results["exist"] / tool_results["listed"] * 100) if tool_results["listed"] > 0 else 100
    print(f"  Listed: {tool_results['listed']}")
    print(f"  Exist:  {tool_results['exist']}")
    print(f"  Coverage: {tool_coverage:.1f}%")
    if tool_results["missing_files"]:
        print(f"  Missing: {tool_results['missing_files'][:5]}")
    print()

    # Gaps (if requested)
    if show_gaps:
        print("## GAPS (Missing from LOL)")
        print("-" * 40)
        for ftype, data in file_results.items():
            if data["missing"]:
                print(f"\n  {ftype.upper()} ({len(data['missing'])} missing, showing first 10):")
                for path in data["missing"][:10]:
                    print(f"    - {path}")
        print()

    # Totality Axiom
    print("## TOTALITY AXIOM")
    print("-" * 40)
    if completeness >= 95 and all_match:
        print("  ✓ VALID: ∀x. (x ∈ PROJECT_elements) → (∃L ∈ LOL. x ∈ L)")
        print("    Everything under the hood is in some list.")
    elif completeness >= 80:
        print("  △ PARTIAL: Totality Axiom holds for ~{:.0f}% of entities".format(completeness))
        print("    Some entities are not yet inventoried.")
    else:
        print("  ✗ INVALID: Totality Axiom does not hold")
        print("    Many entities are missing from LOL.")
    print()

    print("=" * 70)

    return completeness >= 95 and all_match


def main():
    quick = "--quick" in sys.argv
    show_gaps = "--gaps" in sys.argv

    print("Loading LOL.yaml...")
    lol = load_lol()

    print("Validating counts...")
    count_results = validate_counts(lol)

    if not quick:
        print("Validating file inventory (this may take a moment)...")
        file_results = validate_file_inventory(lol)

        print("Validating tools...")
        tool_results = validate_tools(lol)
    else:
        file_results = {
            "python": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
            "javascript": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
            "yaml": {"expected": 0, "in_lol": 0, "missing": [], "extra": []},
        }
        tool_results = {"listed": 0, "exist": 0, "missing_files": []}

    print()
    valid = print_report(count_results, file_results, tool_results, show_gaps)

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
