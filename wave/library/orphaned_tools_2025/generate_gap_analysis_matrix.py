#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CanonRoleRow:
    number: int
    continent: str
    fundamental: str
    hadron: str
    example: str
    detection_rule: str


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _strip_md(text: str) -> str:
    # Minimal markdown cleanup for table cells: remove surrounding backticks and collapse whitespace.
    t = (text or "").strip()
    if t.startswith("`") and t.endswith("`") and len(t) >= 2:
        t = t[1:-1]
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _parse_int(text: str) -> int:
    try:
        return int(text.strip())
    except Exception:
        return -1


def _parse_hadrons_96_table(md_path: Path) -> list[CanonRoleRow]:
    lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    rows: list[CanonRoleRow] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        # Skip header separator
        if re.match(r"^\|\s*-+\s*\|", line):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue
        if parts[0].lower().startswith("#"):
            continue
        number = _parse_int(parts[0])
        if number <= 0:
            continue
        rows.append(
            CanonRoleRow(
                number=number,
                continent=_strip_md(parts[1]),
                fundamental=_strip_md(parts[2]),
                hadron=_strip_md(parts[3]),
                example=_strip_md(parts[4]),
                detection_rule=_strip_md(parts[5]),
            )
        )
    rows.sort(key=lambda r: r.number)
    return rows


def _load_engine_types(particle_defs_path: Path) -> set[str]:
    obj = _read_json(particle_defs_path)
    return {str(p.get("id") or "").strip() for p in (obj.get("particle_types") or []) if p.get("id")}


def _load_canvas_types(subhadrons_csv: Path) -> Counter[str]:
    rows = _read_csv_dicts(subhadrons_csv)
    return Counter((r.get("base_type") or "").strip() for r in rows if (r.get("base_type") or "").strip())


def _load_rpbl_hadrons(rpbl_csv: Path) -> set[str]:
    rows = _read_csv_dicts(rpbl_csv)
    return {str(r.get("hadron_subtipo") or "").strip() for r in rows if (r.get("hadron_subtipo") or "").strip()}


def _write_md(
    out_path: Path,
    *,
    canon_rows: list[CanonRoleRow],
    rpbl_hadrons: set[str],
    engine_types: set[str],
    canvas_types: Counter[str],
) -> None:
    canon_hadrons = {r.hadron for r in canon_rows}
    canvas_type_set = set(canvas_types.keys())

    overlap_engine_canon = sorted(engine_types & canon_hadrons)
    engine_only = sorted(engine_types - canon_hadrons)
    canon_missing_in_engine = sorted(canon_hadrons - engine_types)

    overlap_canvas_canon = sorted(canvas_type_set & canon_hadrons)
    canvas_only = sorted(canvas_type_set - canon_hadrons)
    canon_missing_in_canvas = sorted(canon_hadrons - canvas_type_set)

    canon_missing_in_rpbl = sorted(canon_hadrons - rpbl_hadrons)
    rpbl_missing_in_canon = sorted(rpbl_hadrons - canon_hadrons)

    lines: list[str] = []
    lines.append("# Gap Analysis Matrix — Canon Roles vs Current Implementations")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Canon roles: `{len(canon_rows)}` (source: `HADRONS_96_FULL.md`)")
    lines.append(f"- Engine types: `{len(engine_types)}` (source: `spectrometer_v12_minimal/patterns/particle_defs.json`)")
    lines.append(
        f"- Archetype snapshot types: `{len(canvas_type_set)}` (source: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`)"
    )
    lines.append(f"- RPBL roles present: `{len(rpbl_hadrons)}` (source: `1440_csv.csv`)")
    lines.append("")

    lines.append("## Quick Findings")
    lines.append(
        f"- Engine ∩ Canon: {len(overlap_engine_canon)}; Engine-only: {len(engine_only)}; Canon missing in engine: {len(canon_missing_in_engine)}"
    )
    lines.append(
        f"- CanvasTypes ∩ Canon: {len(overlap_canvas_canon)}; Canvas-only: {len(canvas_only)}; Canon missing in canvas types: {len(canon_missing_in_canvas)}"
    )
    if canon_missing_in_rpbl or rpbl_missing_in_canon:
        lines.append(
            f"- Canon↔RPBL mismatch: canon_missing_in_rpbl={len(canon_missing_in_rpbl)} rpbl_missing_in_canon={len(rpbl_missing_in_canon)} (naming drift likely)"
        )
    else:
        lines.append("- Canon↔RPBL mismatch: none detected (names align).")
    lines.append("")

    lines.append("## Engine Types Not In Canon (Candidates to Add or Map)")
    if engine_only:
        lines.append("| engine type | suggested disposition |")
        lines.append("|---|---|")
        for t in engine_only:
            suggestion = "candidate role addition"
            if t == "Controller":
                suggestion = "map to `APIHandler` (or add `Controller` as separate presentation role)"
            elif t == "Repository":
                suggestion = "map to `DomainPort` (or add `Repository` explicitly)"
            elif t in {"ApplicationService", "DomainService", "Service", "UseCase"}:
                suggestion = "candidate role addition (organelle-level orchestration)"
            elif t in {"Command", "Query"}:
                suggestion = "candidate role addition (CQRS artifacts) or map into `DTO`"
            lines.append(f"| `{t}` | {suggestion} |")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Canvas Types Not In Canon (Archetype-only Vocabulary)")
    if canvas_only:
        lines.append("| canvas type | count | suggested disposition |")
        lines.append("|---|---:|---|")
        for t in sorted(canvas_only, key=lambda x: (-canvas_types[x], x)):
            count = canvas_types[t]
            suggestion = "candidate role addition or smell-only type"
            if t in {"Retry", "Timeout", "Bulkhead"}:
                suggestion = "resilience pattern (likely smell/ops catalog, not core role)"
            if t in {"SharedKernel", "ContextMap"}:
                suggestion = "strategic DDD concept (candidate role addition)"
            if t in {"Outbox"}:
                suggestion = "integration pattern (candidate archetype; probably not a base role)"
            lines.append(f"| `{t}` | {count} | {suggestion} |")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Canon Role Matrix (96)")
    lines.append("| # | continent | family | hadron | in RPBL | in engine | in canvas types | notes |")
    lines.append("|---:|---|---|---|:---:|:---:|:---:|---|")

    for r in canon_rows:
        in_rpbl = "✅" if r.hadron in rpbl_hadrons else "❌"
        in_engine = "✅" if r.hadron in engine_types else "❌"
        in_canvas = "✅" if r.hadron in canvas_type_set else "❌"

        notes: list[str] = []
        if in_engine == "✅":
            notes.append("direct engine type")
        elif r.hadron == "APIHandler" and "Controller" in engine_types:
            notes.append("engine has `Controller` (possible mapping)")
        elif r.hadron == "InfrastructureAdapter" and "RepositoryImpl" in engine_types:
            notes.append("engine has `RepositoryImpl` (possible mapping)")
        elif r.hadron == "DomainPort" and "Repository" in engine_types:
            notes.append("engine has `Repository` (possible mapping)")
        elif r.hadron in {"CommandHandler", "QueryHandler"} and "Command" in engine_types and "Query" in engine_types:
            notes.append("engine has `Command`/`Query` but not handlers (taxonomy gap)")

        if in_canvas == "✅" and in_engine == "❌":
            notes.append("present in archetype snapshot; engine taxonomy missing")
        if in_canvas == "❌" and in_engine == "❌":
            notes.append("missing in both (no current support)")

        # Keep notes compact
        note_text = "; ".join(notes) if notes else "—"
        lines.append(
            f"| {r.number} | {r.continent} | {r.fundamental} | `{r.hadron}` | {in_rpbl} | {in_engine} | {in_canvas} | {note_text} |"
        )

    lines.append("")

    lines.append("## Prioritized Gaps (High ROI)")
    lines.append("- Add artifact-level extraction (config/infra/runtime) to cover many Execution roles.")
    lines.append("- Add atom-level extraction (statements/expressions/variables) to support “physics” signals (complexity/flow).")
    lines.append("- Unify vocab: either (a) expand the Role Catalog beyond 96, or (b) map engine/canvas extras into existing roles explicitly.")
    lines.append("- Split violations into `forbidden` (hard) vs `smells` (soft) to stabilize the model.")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a canon vs implementation gap analysis matrix.")
    parser.add_argument("--canon", default="HADRONS_96_FULL.md", help="Path to the canonical 96-role markdown table.")
    parser.add_argument(
        "--rpbl",
        default="1440_csv.csv",
        help="Path to RPBL dataset (used to cross-check role names).",
    )
    parser.add_argument(
        "--engine",
        default="spectrometer_v12_minimal/patterns/particle_defs.json",
        help="Path to engine particle type definitions JSON.",
    )
    parser.add_argument(
        "--archetypes",
        default="spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv",
        help="Path to archetype snapshot CSV (canvas extraction).",
    )
    parser.add_argument("--out", default="GAP_ANALYSIS_MATRIX.md", help="Output markdown file path.")
    args = parser.parse_args(argv)

    canon_rows = _parse_hadrons_96_table(Path(args.canon))
    rpbl_hadrons = _load_rpbl_hadrons(Path(args.rpbl))
    engine_types = _load_engine_types(Path(args.engine))
    canvas_types = _load_canvas_types(Path(args.archetypes))

    _write_md(
        Path(args.out),
        canon_rows=canon_rows,
        rpbl_hadrons=rpbl_hadrons,
        engine_types=engine_types,
        canvas_types=canvas_types,
    )
    print(f"Wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
