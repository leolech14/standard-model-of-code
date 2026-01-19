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
class SubhadronRow:
    canvas_node_id: str
    sub_index: int
    badge: str
    subhadron_name: str
    base_type: str
    is_antimatter: bool
    reason: str
    rarity: str
    visual: str
    x: int
    y: int
    color: str


HEADER_RE = re.compile(
    r"^###\s*(?:(?P<badge>[^\w\s])\s*)?(?P<name>[A-Za-z0-9][A-Za-z0-9_]+)\b",
    re.M,
)
TYPE_RE = re.compile(r"\bType:\s*([A-Za-z0-9_]+)")
RARITY_RE = re.compile(r"\bRarity:\s*([0-9.]+%)")
VISUAL_RE = re.compile(r"\bVisual:\s*([A-Za-z0-9_+\-]+)")
REASON_RE = re.compile(r"\bReason:\s*(.+)")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_sub_index(node_id: str) -> int:
    m = re.match(r"^sub_(\d+)$", node_id)
    if not m:
        return -1
    try:
        return int(m.group(1))
    except Exception:
        return -1


def _parse_subhadron_node(node: dict[str, Any]) -> SubhadronRow | None:
    node_id = str(node.get("id") or "")
    if not node_id.startswith("sub_"):
        return None

    text = str(node.get("text") or "")
    m = HEADER_RE.search(text.strip())
    if not m:
        raise ValueError(f"Could not parse header for node {node_id}")

    badge = (m.group("badge") or "").strip()
    name = (m.group("name") or "").strip()

    mt = TYPE_RE.search(text)
    if not mt:
        raise ValueError(f"Could not parse Type: for node {node_id}")
    base_type = mt.group(1).strip()

    is_antimatter = "ANTIMATTER DETECTED" in text

    rarity = ""
    mr = RARITY_RE.search(text)
    if mr:
        rarity = mr.group(1).strip()

    visual = ""
    mv = VISUAL_RE.search(text)
    if mv:
        visual = mv.group(1).strip()

    reason = ""
    if is_antimatter:
        mreason = REASON_RE.search(text)
        if mreason:
            reason = mreason.group(1).strip()

    return SubhadronRow(
        canvas_node_id=node_id,
        sub_index=_parse_sub_index(node_id),
        badge=badge,
        subhadron_name=name,
        base_type=base_type,
        is_antimatter=is_antimatter,
        reason=reason,
        rarity=rarity,
        visual=visual,
        x=int(node.get("x") or 0),
        y=int(node.get("y") or 0),
        color=str(node.get("color") or ""),
    )


def _write_csv(path: Path, rows: list[SubhadronRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "canvas_node_id",
                "sub_index",
                "badge",
                "subhadron_name",
                "base_type",
                "is_antimatter",
                "reason",
                "rarity",
                "visual",
                "x",
                "y",
                "color",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "canvas_node_id": r.canvas_node_id,
                    "sub_index": r.sub_index,
                    "badge": r.badge,
                    "subhadron_name": r.subhadron_name,
                    "base_type": r.base_type,
                    "is_antimatter": str(bool(r.is_antimatter)),
                    "reason": r.reason,
                    "rarity": r.rarity,
                    "visual": r.visual,
                    "x": r.x,
                    "y": r.y,
                    "color": r.color,
                }
            )


def _write_md(path: Path, *, canvas_path: Path, rows: list[SubhadronRow], csv_path: Path) -> None:
    total = len(rows)
    antimatter = sum(1 for r in rows if r.is_antimatter)
    possible = total - antimatter
    types = Counter(r.base_type for r in rows)
    reasons = Counter(r.reason for r in rows if r.is_antimatter and r.reason)

    lines: list[str] = []
    lines.append("# Subhadrons 384 — Extracted From Canvas")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"- Source: `{canvas_path}`")
    lines.append(f"- CSV: `{csv_path}`")
    lines.append("")
    lines.append("## Snapshot")
    lines.append(f"- Total subhadrons found: {total}")
    lines.append(f"- Marked antimatter in canvas: {antimatter}")
    lines.append(f"- Marked non-antimatter in canvas: {possible}")
    lines.append(f"- Unique `Type:` values: {len(types)}")
    lines.append("")
    lines.append("## Top Types")
    lines.append("| type | count | antimatter |")
    lines.append("|---|---:|---:|")
    for t, count in types.most_common(20):
        anti = sum(1 for r in rows if r.base_type == t and r.is_antimatter)
        lines.append(f"| `{t}` | {count} | {anti} |")
    lines.append("")
    lines.append("## Antimatter Reasons (Top)")
    lines.append("| reason | count |")
    lines.append("|---|---:|")
    for reason, count in reasons.most_common(20):
        safe = reason.replace("|", "\\|")
        lines.append(f"| {safe} | {count} |")
    lines.append("")
    lines.append("## Note")
    lines.append(
        "This is a faithful snapshot of what the canvas currently marks as antimatter; it is not asserting that the true canonical impossible set is 42."
    )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract 384 subhadron nodes from an Obsidian canvas file.")
    parser.add_argument(
        "--canvas",
        default="THEORY_COMPLETE.canvas",
        help="Path to the .canvas JSON file",
    )
    parser.add_argument(
        "--out-csv",
        default="spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv",
        help="Output CSV path",
    )
    parser.add_argument(
        "--out-md",
        default="spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.md",
        help="Output Markdown summary path",
    )
    args = parser.parse_args(argv)

    canvas_path = Path(args.canvas)
    data = _read_json(canvas_path)

    rows: list[SubhadronRow] = []
    for node in data.get("nodes") or []:
        row = _parse_subhadron_node(node)
        if row:
            rows.append(row)

    rows.sort(key=lambda r: (r.sub_index if r.sub_index >= 0 else 10**9, r.canvas_node_id))

    csv_path = Path(args.out_csv)
    md_path = Path(args.out_md)

    _write_csv(csv_path, rows)
    _write_md(md_path, canvas_path=canvas_path, rows=rows, csv_path=csv_path)

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {md_path}")
    print(f"Subhadrons: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))

