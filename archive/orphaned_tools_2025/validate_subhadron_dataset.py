#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any


@dataclass(frozen=True)
class CanonHadron:
    continent: str
    fundamental: str


def _strip_parenthetical(text: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*", "", text).strip()


def _load_hadrons_96_md(path: Path) -> dict[str, CanonHadron]:
    """Load the canonical hadron→(continent,fundamental) map from the MD table."""
    mapping: dict[str, CanonHadron] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if line.startswith("| #") or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 4:
            continue
        continent = _strip_parenthetical(parts[1])
        fundamental = parts[2].strip()
        hadron = parts[3].strip()
        if hadron:
            mapping[hadron] = CanonHadron(continent=continent, fundamental=fundamental)
    return mapping


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _axis_values(rows: list[dict[str, str]], key: str) -> list[str]:
    return sorted({row.get(key, "").strip() for row in rows if row.get(key, "").strip()})


def _product(values: list[int]) -> int:
    out = 1
    for v in values:
        out *= v
    return out


def _build_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    axes = {
        "responsibility": _axis_values(rows, "responsibility"),
        "purity": _axis_values(rows, "purity"),
        "boundary": _axis_values(rows, "boundary"),
        "lifecycle": _axis_values(rows, "lifecycle"),
    }
    rpbl_unique = len(
        {
            (
                row.get("responsibility", ""),
                row.get("purity", ""),
                row.get("boundary", ""),
                row.get("lifecycle", ""),
            )
            for row in rows
        }
    )

    def count(col: str) -> Counter[str]:
        return Counter(row.get(col, "") for row in rows)

    continents = count("continente_cor")
    fundamentals = count("particula_fundamental")
    hadrons = count("hadron_subtipo")
    base_hadrons = count("base_hadron")

    rows_per_hadron: Counter[str] = Counter()
    impossible_per_hadron: Counter[str] = Counter()
    impossible_rows: list[dict[str, str]] = []
    for row in rows:
        h = row.get("hadron_subtipo", "")
        rows_per_hadron[h] += 1
        if row.get("is_impossible", "").lower() == "true":
            impossible_rows.append(row)
            impossible_per_hadron[h] += 1

    hist = Counter(rows_per_hadron.values())
    reasons = Counter(row.get("impossible_reason", "") for row in impossible_rows)
    mismatch_count = sum(
        1 for row in rows if row.get("base_hadron", "") and row.get("base_hadron") != row.get("hadron_subtipo", "")
    )

    return {
        "rows": len(rows),
        "axes": {k: {"count": len(v), "values": v} for k, v in axes.items()},
        "rpbl_grid_size": _product([len(axes["responsibility"]), len(axes["purity"]), len(axes["boundary"]), len(axes["lifecycle"])]),
        "rpbl_unique_in_rows": rpbl_unique,
        "continents": {
            "unique_count": len(continents),
            "unique": sorted(k for k in continents.keys() if k),
            "counts": dict(continents.most_common()),
        },
        "fundamentals": {
            "unique_count": len(fundamentals),
            "unique": sorted(k for k in fundamentals.keys() if k),
            "counts": dict(fundamentals.most_common()),
        },
        "hadrons": {
            "unique_count": len(hadrons),
            "top10_by_rows": [[k, v] for k, v in hadrons.most_common(10)],
            "rows_per_hadron": {
                "min": min(rows_per_hadron.values()) if rows_per_hadron else 0,
                "max": max(rows_per_hadron.values()) if rows_per_hadron else 0,
                "histogram": {str(k): v for k, v in sorted(hist.items())},
            },
        },
        "base_hadrons": {
            "unique_count": len(base_hadrons),
            "mismatch_count": mismatch_count,
            "top10_by_rows": [[k, v] for k, v in base_hadrons.most_common(10)],
        },
        "impossible": {
            "row_count": len(impossible_rows),
            "hadron_unique_count": len(impossible_per_hadron),
            "reasons": dict(reasons.most_common()),
            "continents": dict(Counter(row.get("continente_cor", "") for row in impossible_rows).most_common()),
            "top10_hadrons": [[k, v] for k, v in impossible_per_hadron.most_common(10)],
        },
    }


def _build_issues(
    rows: list[dict[str, str]],
    *,
    canon_hadrons: dict[str, CanonHadron],
    hadron_aliases: dict[str, str],
) -> list[str]:
    issues: list[str] = []

    required_cols = {
        "responsibility",
        "purity",
        "boundary",
        "lifecycle",
        "base_hadron",
        "hadron_subtipo",
        "continente_cor",
        "particula_fundamental",
        "is_impossible",
        "impossible_reason",
    }
    if not rows:
        issues.append("Dataset is empty.")
        return issues

    missing_cols = required_cols - set(rows[0].keys())
    if missing_cols:
        issues.append(f"Missing required columns: {sorted(missing_cols)}")

    mismatches = 0
    for row in rows:
        if row.get("base_hadron") and row.get("hadron_subtipo") and row["base_hadron"] != row["hadron_subtipo"]:
            mismatches += 1
    if mismatches:
        issues.append(f"base_hadron != hadron_subtipo for {mismatches} rows (expected 0).")

    # Canonical consistency: per hadron_subtipo, continent/fundamental should match HADRONS_96_FULL.md
    dataset_hadrons: dict[str, CanonHadron] = {}
    for row in rows:
        h = row.get("hadron_subtipo", "")
        if not h or h in dataset_hadrons:
            continue
        dataset_hadrons[h] = CanonHadron(
            continent=row.get("continente_cor", ""),
            fundamental=row.get("particula_fundamental", ""),
        )

    canon_mismatches: list[str] = []
    canon_missing: list[str] = []
    for hadron, info in sorted(dataset_hadrons.items()):
        canon_name = hadron_aliases.get(hadron, hadron)
        canon = canon_hadrons.get(canon_name)
        if not canon:
            canon_missing.append(hadron)
            continue
        if info.continent != canon.continent or info.fundamental != canon.fundamental:
            canon_mismatches.append(
                f"{hadron}: dataset={info.continent}/{info.fundamental} canon={canon.continent}/{canon.fundamental}"
            )

    if canon_missing:
        issues.append(f"{len(canon_missing)} hadrons missing in canon MD mapping: {canon_missing[:10]}...")
    if canon_mismatches:
        issues.append(f"{len(canon_mismatches)} hadrons mismatch canon mapping: {canon_mismatches[:10]}...")

    return issues


def _write_report(
    *,
    csv_path: Path,
    canon_md_path: Path,
    summary: dict[str, Any],
    issues: list[str],
    report_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    axes = summary.get("axes", {})
    impossible = summary.get("impossible", {})
    hadrons = summary.get("hadrons", {})

    lines: list[str] = []
    lines.append("# 1440 Dataset Validation Report")
    lines.append("")
    lines.append(f"- Dataset: `{csv_path}`")
    lines.append(f"- Canon: `{canon_md_path}`")
    lines.append("")
    lines.append("## What “1440” Means")
    lines.append(
        "- 1,440 is the size of the RPBL grid: "
        f"{axes.get('responsibility', {}).get('count', 0)}×"
        f"{axes.get('purity', {}).get('count', 0)}×"
        f"{axes.get('boundary', {}).get('count', 0)}×"
        f"{axes.get('lifecycle', {}).get('count', 0)} = {summary.get('rpbl_grid_size', 0)}."
    )
    lines.append(f"- The CSV currently contains `{summary.get('rows', 0)}` rows (hadron-specific allowed RPBL combos).")
    lines.append("")
    lines.append("## Axes (Observed Values)")
    for k in ("responsibility", "purity", "boundary", "lifecycle"):
        v = axes.get(k, {})
        lines.append(f"- {k}: {v.get('count', 0)} → {', '.join(v.get('values', []))}")
    lines.append("")
    lines.append("## Coverage")
    lines.append(f"- Hadrons present: {hadrons.get('unique_count', 0)} (target: 96)")
    rph = hadrons.get("rows_per_hadron", {})
    lines.append(
        f"- Rows per hadron: min={rph.get('min', 0)} max={rph.get('max', 0)} histogram={rph.get('histogram', {})}"
    )
    lines.append("")
    lines.append("## Impossible Rows")
    lines.append(f"- Impossible row count: {impossible.get('row_count', 0)}")
    lines.append(f"- Unique reasons: {len((impossible.get('reasons') or {}).keys())}")
    for reason, count in (impossible.get("reasons") or {}).items():
        if reason:
            lines.append(f"- {count}: {reason}")
    lines.append("")
    lines.append("## Issues / Mismatches")
    if not issues:
        lines.append("- None detected by this validator.")
    else:
        for issue in issues:
            lines.append(f"- {issue}")
    lines.append("")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate the RPBL/hadron dataset (1440_csv.csv).")
    parser.add_argument("--csv", default="1440_csv.csv", help="Path to 1440_csv.csv")
    parser.add_argument("--canon-md", default="HADRONS_96_FULL.md", help="Path to canonical HADRONS_96_FULL.md")
    parser.add_argument(
        "--summary-out",
        default="spectrometer_v12_minimal/1440_summary.json",
        help="Where to write the computed summary JSON",
    )
    parser.add_argument(
        "--report-out",
        default="spectrometer_v12_minimal/validation/1440_dataset_report.md",
        help="Where to write the Markdown report",
    )
    parser.add_argument("--no-write", action="store_true", help="Do not write files; print summary only")
    args = parser.parse_args(argv)

    csv_path = Path(args.csv).resolve() if not Path(args.csv).is_absolute() else Path(args.csv).resolve()
    canon_md_path = (
        Path(args.canon_md).resolve() if not Path(args.canon_md).is_absolute() else Path(args.canon_md).resolve()
    )
    summary_out = Path(args.summary_out)
    report_out = Path(args.report_out)

    rows = _load_rows(csv_path)
    summary = _build_summary(rows)

    canon = _load_hadrons_96_md(canon_md_path) if canon_md_path.exists() else {}
    hadron_aliases = {"ABTestRouter": "A/B Test Router"}
    issues = _build_issues(rows, canon_hadrons=canon, hadron_aliases=hadron_aliases)

    if args.no_write:
        print(json.dumps({"csv": str(csv_path), "summary": summary, "issues": issues}, indent=2))
        return 0

    summary_payload = {"source": str(Path(args.csv)), **summary}
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _write_report(
        csv_path=Path(args.csv),
        canon_md_path=Path(args.canon_md),
        summary=summary,
        issues=issues,
        report_path=report_out,
    )

    print(f"Wrote summary: {summary_out}")
    print(f"Wrote report: {report_out}")
    if issues:
        print(f"Issues detected: {len(issues)} (see report)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
