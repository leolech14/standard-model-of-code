#!/usr/bin/env python3
"""
Collider Coverage Analyzer - Field-level data quality metrics.

Compares actual Collider output against particle.schema.json
to measure coverage at individual field level.

Usage:
    python collider_coverage.py                  # Analyze latest output
    python collider_coverage.py --csv            # Export as CSV
"""

import json
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent.parent
COLLIDER_OUTPUT = REPO_ROOT / ".collider-full"
SCHEMA_PATH = REPO_ROOT / "standard-model-of-code" / "schema" / "particle.schema.json"
OUTPUT_CSV = REPO_ROOT / ".agent" / "intelligence" / "COLLIDER_COVERAGE.csv"


def load_schema():
    """Load and flatten the particle schema."""
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    # Extract all expected fields
    fields = {}

    def extract_fields(obj, prefix=""):
        if "properties" in obj:
            for name, prop in obj["properties"].items():
                full_name = f"{prefix}{name}" if prefix else name
                fields[full_name] = {
                    "type": prop.get("type", prop.get("enum", "ref")),
                    "description": prop.get("description", ""),
                    "required": name in obj.get("required", [])
                }
                # Recurse into nested objects
                if prop.get("type") == "object" or "$ref" in prop:
                    if "properties" in prop:
                        extract_fields(prop, f"{full_name}.")

    extract_fields(schema)

    # Also extract from $defs
    for def_name, def_obj in schema.get("$defs", {}).items():
        extract_fields(def_obj, f"{def_name}.")

    return fields


def load_collider_output():
    """Load latest Collider output."""
    outputs = list(COLLIDER_OUTPUT.glob("output_llm-oriented_*.json"))
    if not outputs:
        print("No Collider output found")
        return None

    latest = max(outputs, key=lambda p: p.stat().st_mtime)
    print(f"Loading: {latest.name}")

    with open(latest) as f:
        return json.load(f)


def analyze_coverage(data, schema_fields):
    """Analyze field coverage across all nodes."""
    nodes = data.get("nodes", [])
    total = len(nodes)
    print(f"Analyzing {total} nodes...")

    # Count occurrences of each field
    field_counts = defaultdict(int)
    field_values = defaultdict(lambda: defaultdict(int))

    def count_fields(obj, prefix=""):
        if not isinstance(obj, dict):
            return
        for key, value in obj.items():
            full_key = f"{prefix}{key}" if prefix else key
            if value is not None and value != "" and value != []:
                field_counts[full_key] += 1
                # Track value distribution for enums
                if isinstance(value, (str, int, float, bool)):
                    field_values[full_key][str(value)] += 1
            if isinstance(value, dict):
                count_fields(value, f"{full_key}.")

    for node in nodes:
        count_fields(node)

    return field_counts, field_values, total


def print_report(field_counts, field_values, total, schema_fields):
    """Print coverage report."""
    print(f"\n{'='*80}")
    print("COLLIDER FIELD COVERAGE REPORT")
    print(f"{'='*80}")
    print(f"Total nodes: {total}")
    print(f"Fields in schema: {len(schema_fields)}")
    print(f"Fields in output: {len(field_counts)}")

    # Core dimension fields
    core_dims = [
        "dimensions.D1_WHAT", "dimensions.D2_LAYER", "dimensions.D3_ROLE",
        "dimensions.D4_BOUNDARY", "dimensions.D5_STATE", "dimensions.D6_EFFECT",
        "dimensions.D7_LIFECYCLE", "dimensions.D8_TRUST"
    ]

    print(f"\n{'─'*80}")
    print("CORE DIMENSIONS (8D Classification)")
    print(f"{'─'*80}")
    for dim in core_dims:
        count = field_counts.get(dim, 0)
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        grade = "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D" if pct >= 30 else "F"
        print(f"  {dim:<30} {bar} {pct:>5.1f}% [{grade}]")

    # Purpose fields
    purpose_fields = [
        "pi2_purpose", "pi2_confidence", "pi4_purpose", "pi4_confidence",
        "purpose_coherence", "purpose_entropy"
    ]

    print(f"\n{'─'*80}")
    print("PURPOSE INTELLIGENCE")
    print(f"{'─'*80}")
    for f in purpose_fields:
        count = field_counts.get(f, 0)
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        grade = "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D" if pct >= 30 else "F"
        print(f"  {f:<30} {bar} {pct:>5.1f}% [{grade}]")

    # Graph properties
    graph_fields = [
        "in_degree", "out_degree", "pagerank", "betweenness_centrality",
        "topology_role", "semantic_role"
    ]

    print(f"\n{'─'*80}")
    print("GRAPH PROPERTIES")
    print(f"{'─'*80}")
    for f in graph_fields:
        count = field_counts.get(f, 0)
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        grade = "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D" if pct >= 30 else "F"
        print(f"  {f:<30} {bar} {pct:>5.1f}% [{grade}]")

    # Top value distributions for key fields
    print(f"\n{'─'*80}")
    print("VALUE DISTRIBUTIONS (Top Fields)")
    print(f"{'─'*80}")

    for f in ["role", "layer", "effect", "boundary", "atom_family"]:
        if f in field_values and field_values[f]:
            print(f"\n  {f}:")
            sorted_vals = sorted(field_values[f].items(), key=lambda x: -x[1])[:8]
            for val, cnt in sorted_vals:
                pct = cnt / total * 100
                print(f"    {val:<20} {cnt:>5} ({pct:>5.1f}%)")

    # Calculate overall grade
    core_coverage = sum(field_counts.get(d, 0) for d in core_dims) / (len(core_dims) * total) * 100 if total else 0
    purpose_coverage = sum(field_counts.get(f, 0) for f in purpose_fields) / (len(purpose_fields) * total) * 100 if total else 0
    graph_coverage = sum(field_counts.get(f, 0) for f in graph_fields) / (len(graph_fields) * total) * 100 if total else 0

    overall = (core_coverage + purpose_coverage + graph_coverage) / 3

    print(f"\n{'='*80}")
    print("OVERALL GRADES")
    print(f"{'='*80}")
    print(f"  Core Dimensions:    {core_coverage:>5.1f}%")
    print(f"  Purpose Fields:     {purpose_coverage:>5.1f}%")
    print(f"  Graph Properties:   {graph_coverage:>5.1f}%")
    print(f"  ─────────────────────────────")
    print(f"  OVERALL:            {overall:>5.1f}%")

    return field_counts


def export_csv(field_counts, total):
    """Export full coverage to CSV."""
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for field, count in sorted(field_counts.items()):
        pct = count / total * 100 if total else 0
        rows.append({
            "field": field,
            "count": count,
            "total": total,
            "coverage_pct": round(pct, 2),
            "grade": "A" if pct >= 90 else "B" if pct >= 70 else "C" if pct >= 50 else "D" if pct >= 30 else "F"
        })

    with open(OUTPUT_CSV, "w") as f:
        f.write("field,count,total,coverage_pct,grade\n")
        for r in rows:
            f.write(f"{r['field']},{r['count']},{r['total']},{r['coverage_pct']},{r['grade']}\n")

    print(f"\nExported: {OUTPUT_CSV}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Collider Coverage Analyzer")
    parser.add_argument("--csv", action="store_true", help="Export as CSV")
    args = parser.parse_args()

    schema_fields = load_schema()
    data = load_collider_output()
    if not data:
        return 1

    field_counts, field_values, total = analyze_coverage(data, schema_fields)
    print_report(field_counts, field_values, total, schema_fields)

    if args.csv:
        export_csv(field_counts, total)

    return 0


if __name__ == "__main__":
    exit(main())
