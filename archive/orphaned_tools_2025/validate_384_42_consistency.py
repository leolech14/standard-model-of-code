#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CanvasSubhadron:
    canvas_node_id: str
    sub_index: int
    subhadron_name: str
    base_type: str
    is_antimatter: bool
    reason: str


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _to_bool(text: str) -> bool:
    return text.strip().lower() in {"true", "1", "yes", "y"}


def _to_int(text: str) -> int:
    try:
        return int(text)
    except Exception:
        return -1


def _load_canvas_subhadrons(path: Path) -> list[CanvasSubhadron]:
    rows: list[CanvasSubhadron] = []
    for r in _read_csv_rows(path):
        rows.append(
            CanvasSubhadron(
                canvas_node_id=r.get("canvas_node_id") or "",
                sub_index=_to_int(r.get("sub_index") or ""),
                subhadron_name=r.get("subhadron_name") or "",
                base_type=r.get("base_type") or "",
                is_antimatter=_to_bool(r.get("is_antimatter") or "false"),
                reason=r.get("reason") or "",
            )
        )
    rows.sort(key=lambda x: (x.sub_index if x.sub_index >= 0 else 10**9, x.canvas_node_id))
    return rows


def _tokenize(s: str) -> list[str]:
    parts = re.split(r"[^A-Za-z0-9]+", s)
    tokens: list[str] = []
    for part in parts:
        if not part:
            continue
        tokens.extend(
            t
            for t in re.findall(
                r"[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+",
                part,
            )
            if t
        )
    return tokens


CANONICAL_MATCH_HINTS: dict[str, list[str]] = {
    "CommandHandler::FindById": ["CommandHandler_FindById"],
    "QueryHandler::Save": ["QueryHandler_Save"],
    "Entity::Stateless": ["Entity_Stateless"],
    "ValueObject::HasIdentity": ["ValueObject_WithIdentity", "ValueObject_HasIdentity"],
    "RepositoryImpl::PureFunction": ["Repository_PureFunction", "RepositoryImpl_PureFunction"],
    "PureFunction::ExternalIO": ["PureFunction_ExternalIO"],
    "EventHandler::ReturnsValue": ["EventHandler_ReturnsValue"],
    "TestFunction::ModifiesProductionData": ["TestFunction_TouchesProduction", "TestFunction_ModifiesProductionData"],
    "APIHandler::InternalOnly": ["APIHandler_InternalOnly"],
    "Service::GlobalState": ["Service_GlobalState"],
    "AggregateRoot::NoInvariants": ["AggregateRoot_NoInvariants"],
    "Validator::AcceptsInvalid": ["Validator_AcceptsInvalid"],
    "Middleware::SkipsNext": ["Middleware_SkipsNext"],
    "HealthCheck::Returns500WhenHealthy": ["HealthCheck_Returns500WhenHealthy"],
    "GracefulShutdown::HardKill": ["GracefulShutdown_HardKill"],
    "ChaosMonkey::ImprovesStability": ["ChaosMonkey_ImprovesStability"],
}


def _best_canvas_match(
    *,
    canvas: list[CanvasSubhadron],
    base_type: str,
    canonical_name: str,
) -> CanvasSubhadron | None:
    candidates = [c for c in canvas if c.base_type == base_type]
    if not candidates:
        return None

    # If there is only one, accept it.
    if len(candidates) == 1:
        return candidates[0]

    hints = CANONICAL_MATCH_HINTS.get(canonical_name) or []
    if hints:
        lowered = {c.subhadron_name.lower(): c for c in candidates}
        for hint in hints:
            hit = lowered.get(hint.lower())
            if hit:
                return hit
        return None

    normalized = canonical_name.replace("::", "_")
    parts = canonical_name.split("::", 1)
    suffix = parts[1] if len(parts) == 2 else canonical_name

    needles: list[str] = []
    needles.extend(_tokenize(normalized))
    needles.extend(_tokenize(suffix))

    # Prefer exact substring matches (case-insensitive).
    lowered = [(c, c.subhadron_name.lower()) for c in candidates]
    for needle in [normalized, suffix]:
        nl = needle.lower()
        if not nl:
            continue
        hits = [c for c, n in lowered if nl in n]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            candidates = hits
            lowered = [(c, c.subhadron_name.lower()) for c in candidates]

    # Score by overlapping tokens.
    needle_set = {n.lower() for n in needles}
    scored: list[tuple[int, int, CanvasSubhadron]] = []
    for c in candidates:
        toks = {t.lower() for t in _tokenize(c.subhadron_name)}
        overlap = len(needle_set & toks)
        # Prefer antimatter matches when canonical is impossible.
        anti_bonus = 1 if c.is_antimatter else 0
        scored.append((overlap, anti_bonus, c))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not scored:
        return None
    if scored[0][0] <= 0:
        return None
    return scored[0][2]


def _write_report(
    path: Path,
    *,
    canvas_csv: Path,
    canvas_rows: list[CanvasSubhadron],
    impossible_42_csv: Path,
    laws_json: Path,
) -> None:
    total = len(canvas_rows)
    antimatter = sum(1 for r in canvas_rows if r.is_antimatter)
    possible = total - antimatter

    expected_total = 384
    expected_impossible = 42
    expected_possible = 342

    types = Counter(r.base_type for r in canvas_rows)
    anti_types = Counter(r.base_type for r in canvas_rows if r.is_antimatter)
    reasons = Counter(r.reason for r in canvas_rows if r.is_antimatter and r.reason)

    # Canonical 42 skeleton coverage
    canon_rows = _read_csv_rows(impossible_42_csv)
    confirmed = [r for r in canon_rows if (r.get("status") or "").strip().lower() == "confirmed"]
    placeholders = [r for r in canon_rows if (r.get("status") or "").strip().lower() == "placeholder"]

    matches: dict[str, CanvasSubhadron | None] = {}
    for r in confirmed:
        base = (r.get("base_hadron") or "").strip()
        name = (r.get("name") or "").strip()
        if not base or not name:
            continue
        matches[name] = _best_canvas_match(canvas=canvas_rows, base_type=base, canonical_name=name)

    matched = {k: v for k, v in matches.items() if v is not None}
    missing = {k: v for k, v in matches.items() if v is None}

    # Law scope coverage
    laws = _read_json(laws_json)
    scope_to_law: dict[str, str] = {}
    for law in laws:
        law_id = str(law.get("id") or "")
        for scope in law.get("scope") or []:
            scope_to_law[str(scope)] = law_id

    anti_in_law_scope = [r for r in canvas_rows if r.is_antimatter and r.base_type in scope_to_law]
    anti_outside_law_scope = [r for r in canvas_rows if r.is_antimatter and r.base_type not in scope_to_law]
    anti_by_law = Counter(scope_to_law.get(r.base_type, "—") for r in anti_in_law_scope)

    lines: list[str] = []
    lines.append("# 384/42 Consistency Report")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Canvas snapshot CSV: `{canvas_csv}`")
    lines.append(f"- Canonical impossible skeleton: `{impossible_42_csv}`")
    lines.append(f"- Canonical laws: `{laws_json}`")
    lines.append("")

    lines.append("## Expected vs Observed")
    lines.append("| metric | expected | observed |")
    lines.append("|---|---:|---:|")
    lines.append(f"| total subhadrons | {expected_total} | {total} |")
    lines.append(f"| impossible (theory target) | {expected_impossible} | {antimatter} |")
    lines.append(f"| possible (theory target) | {expected_possible} | {possible} |")
    lines.append("")

    lines.append("## Canvas Antimatter Distribution")
    lines.append("| type | total | antimatter |")
    lines.append("|---|---:|---:|")
    for t, count in types.most_common(30):
        lines.append(f"| `{t}` | {count} | {anti_types.get(t, 0)} |")
    lines.append("")

    lines.append("## Top Antimatter Reasons (Canvas)")
    lines.append("| reason | count |")
    lines.append("|---|---:|")
    for reason, count in reasons.most_common(30):
        safe = reason.replace("|", "\\|")
        lines.append(f"| {safe} | {count} |")
    lines.append("")

    lines.append("## Canonical 42 Skeleton Coverage (Confirmed Items)")
    lines.append(f"- Confirmed in skeleton: {len(confirmed)}")
    lines.append(f"- Placeholders in skeleton: {len(placeholders)}")
    lines.append(f"- Matched in canvas snapshot (heuristic): {len(matched)}/{len(matches)}")
    lines.append("")
    lines.append("| canonical | base_hadron | matched canvas subhadron | canvas type | canvas antimatter |")
    lines.append("|---|---|---|---|---|")
    for r in confirmed:
        cname = (r.get("name") or "").strip()
        base = (r.get("base_hadron") or "").strip() or "—"
        hit = matched.get(cname)
        if hit:
            lines.append(
                f"| `{cname}` | `{base}` | `{hit.subhadron_name}` | `{hit.base_type}` | {str(hit.is_antimatter)} |"
            )
        else:
            lines.append(f"| `{cname}` | `{base}` | — | — | — |")
    lines.append("")

    if missing:
        lines.append("### Missing (Likely Taxonomy Drift)")
        for cname in sorted(missing.keys()):
            base = next((r.get("base_hadron") for r in confirmed if (r.get("name") or "").strip() == cname), "") or ""
            lines.append(f"- `{cname}` (base: `{base or '—'}`)")
        lines.append("")

    lines.append("## Law Scope Coverage (L1–L11)")
    lines.append(f"- Antimatter inside L1–L11 scopes: {len(anti_in_law_scope)}")
    lines.append(f"- Antimatter outside L1–L11 scopes: {len(anti_outside_law_scope)}")
    lines.append("")
    lines.append("| law | antimatter count |")
    lines.append("|---|---:|")
    for law_id, count in sorted(anti_by_law.items(), key=lambda kv: kv[0]):
        lines.append(f"| `{law_id}` | {count} |")
    lines.append("")

    lines.append("## Interpretation")
    lines.append(
        "- The canvas contains a full 384-node subhadron set, but the current antimatter marking (239) does not match the theory target of 42; this implies the canvas is encoding additional “bad smells” as antimatter, or the 42 definition is being applied differently."
    )
    lines.append(
        "- The canonical 11-law list (L1–L11) only scopes a subset of types; a large portion of canvas antimatter is outside those scopes, which prevents deriving a stable 42 without deciding what is a hard-impossible law vs a soft smell."
    )
    lines.append("")

    lines.append("## Next Steps (To Canonicalize 42)")
    lines.append(
        "- Decide the semantics of `impossible`: strict logical impossibility (42) vs strong architecture smell (additional canvas antimatter)."
    )
    lines.append(
        "- If the target is strict-42: extend the extraction to map each antimatter pattern to a single law (or add new laws), then reclassify the remaining antimatter patterns as smells with severity (not impossible)."
    )
    lines.append(
        "- Once canonicalized: generate `subhadrons_384.csv` and `impossible_42.csv` from a single ruleset and keep them machine-readable next to the detector."
    )
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate consistency between 384 subhadrons, 42 impossibles, and laws.")
    parser.add_argument(
        "--canvas-csv",
        default="spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv",
        help="CSV produced by tools/extract_subhadrons_from_canvas.py",
    )
    parser.add_argument(
        "--impossible-42-csv",
        default="spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv",
        help="Canonical skeleton CSV",
    )
    parser.add_argument(
        "--laws-json",
        default="spectrometer_v12_minimal/LAW_11_CANONICAL.json",
        help="Canonical laws JSON",
    )
    parser.add_argument(
        "--out",
        default="spectrometer_v12_minimal/validation/384_42_consistency_report.md",
        help="Output Markdown report path",
    )
    args = parser.parse_args(argv)

    canvas_csv = Path(args.canvas_csv)
    impossible_42_csv = Path(args.impossible_42_csv)
    laws_json = Path(args.laws_json)
    out = Path(args.out)

    canvas_rows = _load_canvas_subhadrons(canvas_csv)
    _write_report(
        out,
        canvas_csv=canvas_csv,
        canvas_rows=canvas_rows,
        impossible_42_csv=impossible_42_csv,
        laws_json=laws_json,
    )
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
