#!/usr/bin/env python3
"""
Corpus Summarizer for Phase 2 Research

Aggregates coverage metrics from a corpus run into summary statistics
suitable for claims ladder promotion (L1 → L2).

Usage:
    python tools/research/summarize_corpus.py artifacts/atom-research/2026-01-22/
    python tools/research/summarize_corpus.py run_dir/ --output summary.md
"""

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any


def load_coverage_files(run_dir: Path) -> list[dict]:
    """Load all coverage.json files from a corpus run."""
    repos_dir = run_dir / "repos"
    if not repos_dir.exists():
        return []

    coverages = []
    for repo_dir in repos_dir.iterdir():
        if not repo_dir.is_dir():
            continue

        # Find the SHA subdirectory
        for sha_dir in repo_dir.iterdir():
            if not sha_dir.is_dir():
                continue

            coverage_file = sha_dir / "coverage.json"
            metadata_file = sha_dir / "run_metadata.json"

            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage = json.load(f)

                # Add repo info
                coverage["_repo_name"] = repo_dir.name
                coverage["_sha"] = sha_dir.name

                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                    coverage["_metadata"] = metadata

                coverages.append(coverage)

    return coverages


def compute_statistics(values: list[float]) -> dict[str, float]:
    """Compute summary statistics for a list of values."""
    if not values:
        return {"n": 0}

    sorted_values = sorted(values)
    n = len(sorted_values)

    # Quartiles
    q1_idx = n // 4
    q3_idx = (3 * n) // 4

    return {
        "n": n,
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "std": round(statistics.stdev(values), 2) if n > 1 else 0,
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "q1": round(sorted_values[q1_idx], 2),
        "q3": round(sorted_values[q3_idx], 2),
        "iqr": round(sorted_values[q3_idx] - sorted_values[q1_idx], 2),
    }


def aggregate_metrics(coverages: list[dict]) -> dict[str, Any]:
    """Aggregate metrics across all repos."""
    # Extract metric arrays
    top_1_masses = []
    top_2_masses = []
    top_4_masses = []
    unknown_rates = []
    t2_rates = []
    n_nodes_list = []

    per_language = {}
    per_domain = {}

    for cov in coverages:
        metrics = cov.get("metrics", {})
        metadata = cov.get("_metadata", {})
        repo_info = metadata.get("repo", {})

        # Core metrics
        top_1_masses.append(metrics.get("top_1_mass", 0))
        top_2_masses.append(metrics.get("top_2_mass", 0))
        top_4_masses.append(metrics.get("top_4_mass", 0))
        unknown_rates.append(metrics.get("unknown_rate", 0))
        t2_rates.append(metrics.get("t2_enrichment_rate", 0))
        n_nodes_list.append(metrics.get("n_nodes", 0))

        # By language
        lang = repo_info.get("language", "unknown")
        if lang not in per_language:
            per_language[lang] = {"top_4": [], "unknown": [], "n_nodes": []}
        per_language[lang]["top_4"].append(metrics.get("top_4_mass", 0))
        per_language[lang]["unknown"].append(metrics.get("unknown_rate", 0))
        per_language[lang]["n_nodes"].append(metrics.get("n_nodes", 0))

        # By domain
        domain = repo_info.get("domain", "unknown")
        if domain not in per_domain:
            per_domain[domain] = {"top_4": [], "unknown": []}
        per_domain[domain]["top_4"].append(metrics.get("top_4_mass", 0))
        per_domain[domain]["unknown"].append(metrics.get("unknown_rate", 0))

    return {
        "overview": {
            "n_repos": len(coverages),
            "total_nodes": sum(n_nodes_list),
        },
        "top_4_mass": compute_statistics(top_4_masses),
        "top_2_mass": compute_statistics(top_2_masses),
        "top_1_mass": compute_statistics(top_1_masses),
        "unknown_rate": compute_statistics(unknown_rates),
        "t2_enrichment_rate": compute_statistics(t2_rates),
        "n_nodes": compute_statistics(n_nodes_list),
        "by_language": {
            lang: {
                "n": len(data["top_4"]),
                "top_4_median": round(statistics.median(data["top_4"]), 2) if data["top_4"] else 0,
                "unknown_median": round(statistics.median(data["unknown"]), 2) if data["unknown"] else 0,
                "total_nodes": sum(data["n_nodes"]),
            }
            for lang, data in per_language.items()
        },
        "by_domain": {
            domain: {
                "n": len(data["top_4"]),
                "top_4_median": round(statistics.median(data["top_4"]), 2) if data["top_4"] else 0,
                "unknown_median": round(statistics.median(data["unknown"]), 2) if data["unknown"] else 0,
            }
            for domain, data in per_domain.items()
        },
    }


def check_promotion_criteria(agg: dict) -> dict[str, Any]:
    """Check if corpus meets L2 promotion criteria."""
    criteria = {}

    # Corpus size
    n_repos = agg["overview"]["n_repos"]
    criteria["corpus_size"] = {
        "value": n_repos,
        "threshold": 100,
        "passed": n_repos >= 100,
    }

    # Median top-4 mass
    top_4 = agg["top_4_mass"]
    criteria["median_top_4"] = {
        "value": top_4.get("median", 0),
        "threshold": 70,
        "passed": top_4.get("median", 0) >= 70,
    }

    # Top-4 mass lower bound (approximate 95% CI: median - 1.96 * IQR/1.35)
    if top_4.get("iqr", 0) > 0 and top_4.get("n", 0) > 10:
        ci_lower = top_4["median"] - 1.96 * top_4["iqr"] / 1.35
    else:
        ci_lower = top_4.get("min", 0)

    criteria["top_4_ci_lower"] = {
        "value": round(ci_lower, 2),
        "threshold": 65,
        "passed": ci_lower >= 65,
    }

    # Median unknown rate
    unknown = agg["unknown_rate"]
    criteria["median_unknown"] = {
        "value": unknown.get("median", 100),
        "threshold": 10,
        "passed": unknown.get("median", 100) <= 10,
    }

    # Overall promotion
    criteria["l2_eligible"] = all(c["passed"] for c in criteria.values() if "passed" in c)

    return criteria


def generate_csv(coverages: list[dict], output_file: Path):
    """Generate CSV summary of all repos."""
    rows = []
    for cov in coverages:
        metrics = cov.get("metrics", {})
        metadata = cov.get("_metadata", {})
        repo_info = metadata.get("repo", {})
        tooling = metadata.get("tooling", {})

        rows.append({
            "repo": cov.get("_repo_name", "unknown"),
            "sha": cov.get("_sha", "unknown"),
            "language": repo_info.get("language", "unknown"),
            "domain": repo_info.get("domain", "unknown"),
            "size": repo_info.get("size", "unknown"),
            "n_nodes": metrics.get("n_nodes", 0),
            "top_1_mass": metrics.get("top_1_mass", 0),
            "top_2_mass": metrics.get("top_2_mass", 0),
            "top_4_mass": metrics.get("top_4_mass", 0),
            "unknown_rate": metrics.get("unknown_rate", 0),
            "t2_rate": metrics.get("t2_enrichment_rate", 0),
            "collider_sha": tooling.get("collider_commit", "unknown"),
        })

    with open(output_file, "w", newline="") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)


def generate_markdown(agg: dict, criteria: dict, coverages: list[dict], output_file: Path):
    """Generate markdown summary report."""
    lines = []
    lines.append("# Corpus Summary Report")
    lines.append("")
    lines.append(f"**Generated:** {output_file.parent.name}")
    lines.append(f"**Repos analyzed:** {agg['overview']['n_repos']}")
    lines.append(f"**Total nodes:** {agg['overview']['total_nodes']:,}")
    lines.append("")

    # L2 Promotion Check
    lines.append("## L2 Promotion Criteria")
    lines.append("")
    lines.append("| Criterion | Value | Threshold | Status |")
    lines.append("|-----------|-------|-----------|--------|")
    for name, c in criteria.items():
        if name == "l2_eligible":
            continue
        status = "PASS" if c.get("passed") else "FAIL"
        lines.append(f"| {name} | {c.get('value', '-')} | {c.get('threshold', '-')} | {status} |")
    lines.append("")

    eligible = "YES" if criteria.get("l2_eligible") else "NO"
    lines.append(f"**L2 Eligible:** {eligible}")
    lines.append("")

    # Key Metrics
    lines.append("## Key Metrics")
    lines.append("")
    lines.append("### Top-4 Mass Distribution")
    t4 = agg["top_4_mass"]
    lines.append(f"- Median: **{t4.get('median', 0)}%**")
    lines.append(f"- Mean: {t4.get('mean', 0)}%")
    lines.append(f"- Std: {t4.get('std', 0)}%")
    lines.append(f"- IQR: [{t4.get('q1', 0)}%, {t4.get('q3', 0)}%]")
    lines.append(f"- Range: [{t4.get('min', 0)}%, {t4.get('max', 0)}%]")
    lines.append("")

    lines.append("### Unknown Rate Distribution")
    unk = agg["unknown_rate"]
    lines.append(f"- Median: **{unk.get('median', 0)}%**")
    lines.append(f"- Mean: {unk.get('mean', 0)}%")
    lines.append(f"- Range: [{unk.get('min', 0)}%, {unk.get('max', 0)}%]")
    lines.append("")

    # By Language
    lines.append("## By Language")
    lines.append("")
    lines.append("| Language | Repos | Nodes | Top-4 Median | Unknown Median |")
    lines.append("|----------|-------|-------|--------------|----------------|")
    for lang, data in sorted(agg["by_language"].items(), key=lambda x: -x[1]["n"]):
        lines.append(f"| {lang} | {data['n']} | {data['total_nodes']:,} | {data['top_4_median']}% | {data['unknown_median']}% |")
    lines.append("")

    # By Domain
    lines.append("## By Domain")
    lines.append("")
    lines.append("| Domain | Repos | Top-4 Median | Unknown Median |")
    lines.append("|--------|-------|--------------|----------------|")
    for domain, data in sorted(agg["by_domain"].items(), key=lambda x: -x[1]["n"]):
        lines.append(f"| {domain} | {data['n']} | {data['top_4_median']}% | {data['unknown_median']}% |")
    lines.append("")

    # Per-Repo Table
    lines.append("## Per-Repo Results")
    lines.append("")
    lines.append("| Repo | Lang | Nodes | Top-4 | Unknown | T2 |")
    lines.append("|------|------|-------|-------|---------|-----|")
    for cov in sorted(coverages, key=lambda x: x.get("_repo_name", "")):
        m = cov.get("metrics", {})
        md = cov.get("_metadata", {}).get("repo", {})
        lines.append(
            f"| {cov.get('_repo_name', '?')} | {md.get('language', '?')} | "
            f"{m.get('n_nodes', 0)} | {m.get('top_4_mass', 0)}% | "
            f"{m.get('unknown_rate', 0)}% | {m.get('t2_enrichment_rate', 0)}% |"
        )
    lines.append("")

    with open(output_file, "w") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Summarize corpus run results")
    parser.add_argument("run_dir", type=Path, help="Path to corpus run directory")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: run_dir/summary.md)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")

    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Error: Run directory not found: {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    # Load coverage data
    coverages = load_coverage_files(args.run_dir)
    if not coverages:
        print(f"Error: No coverage files found in {args.run_dir}", file=sys.stderr)
        sys.exit(1)

    # Aggregate
    agg = aggregate_metrics(coverages)
    criteria = check_promotion_criteria(agg)

    if args.json:
        output = {
            "aggregated": agg,
            "promotion_criteria": criteria,
        }
        print(json.dumps(output, indent=2))
    else:
        # Generate outputs
        csv_file = args.run_dir / "summary.csv"
        md_file = args.output or (args.run_dir / "summary.md")

        generate_csv(coverages, csv_file)
        generate_markdown(agg, criteria, coverages, md_file)

        print(f"Summary CSV: {csv_file}")
        print(f"Summary MD:  {md_file}")
        print()

        # Print key results
        print("=" * 60)
        print("CORPUS SUMMARY")
        print("=" * 60)
        print(f"Repos: {agg['overview']['n_repos']}")
        print(f"Total nodes: {agg['overview']['total_nodes']:,}")
        print()
        print(f"Top-4 mass median: {agg['top_4_mass'].get('median', 0)}%")
        print(f"Unknown rate median: {agg['unknown_rate'].get('median', 0)}%")
        print()
        print(f"L2 Eligible: {'YES' if criteria.get('l2_eligible') else 'NO'}")


if __name__ == "__main__":
    main()
