#!/usr/bin/env python3
"""
repo_mapper.py

Generate:
- FILE_INDEX.csv
- DIRECTORY_STATS.csv
- DOCS_INDEX.csv
- BROKEN_LINKS.csv
- DOC_GRAPH.json

Optionally:
- THEORY_SECTION_REGISTRY.csv
- THEORY_SECTION_GRAPH.json
- THEORY_SECTION_INDEX.md

Usage:
  python repo_mapper.py /path/to/PROJECT_elements --out ./_repo_map

This script is intentionally dependency-light (only standard library + pandas optional).
If pandas is missing, it still writes CSVs via the csv module (less convenient formatting).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
TILDE_FENCE_RE = re.compile(r"~~~.*?~~~", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
REF_DEF_RE = re.compile(r"^\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
TITLE_RE = re.compile(r"^\s*#\s+(.+)", re.MULTILINE)
MARKER_RE = re.compile(r"<!--\s*@([A-Z_]+)\s*:\s*([^>]+?)\s*-->")

def strip_code(md: str) -> str:
    md = FENCE_RE.sub("", md)
    md = TILDE_FENCE_RE.sub("", md)
    md = INLINE_CODE_RE.sub("", md)
    return md

def extract_title(md: str, fallback: str) -> str:
    m = TITLE_RE.search(md)
    return m.group(1).strip() if m else fallback

def extract_md_links(md: str) -> List[str]:
    links = []
    for m in LINK_RE.finditer(md):
        links.append(m.group(2).strip())
    for m in REF_DEF_RE.finditer(md):
        links.append(m.group(2).strip())
    return links

def normalize_link(link: str) -> Optional[str]:
    link = link.strip()
    if link.startswith("<") and link.endswith(">"):
        link = link[1:-1].strip()
    if not link:
        return None
    # ignore schemes
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link):
        return None
    link = link.split("#", 1)[0].split("?", 1)[0].strip()
    return link or None

def resolve_path(src_path: str, link: str) -> str:
    # src_path is POSIX-ish relative path from repo root
    if link.startswith("/"):
        p = link.lstrip("/")
    else:
        src_dir = os.path.dirname(src_path)
        p = os.path.normpath(os.path.join(src_dir, link))
    p = p.lstrip("./")
    return p

def walk_files(root: Path) -> List[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        # ignore typical noise
        if any(part in (".git", ".venv", "node_modules") for part in p.parts):
            continue
        files.append(p)
    return files

def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

def build_indexes(repo_root: Path, out_dir: Path, theory_path: Optional[Path] = None) -> None:
    files = walk_files(repo_root)
    rel_paths = [p.relative_to(repo_root).as_posix() for p in files]
    rel_set = set(rel_paths)

    # FILE_INDEX
    file_rows = []
    for p, rel in zip(files, rel_paths):
        ext = p.suffix.lower()
        top = rel.split("/", 1)[0] if "/" in rel else "<root>"
        file_rows.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "ext": ext,
            "top": top,
        })
    write_csv(out_dir / "FILE_INDEX.csv", file_rows, ["path", "bytes", "ext", "top"])

    # DIRECTORY_STATS
    dir_stats: Dict[str, Dict[str, object]] = defaultdict(lambda: {"files": 0, "bytes": 0, "md": 0, "json": 0, "yaml": 0})
    for row in file_rows:
        d = os.path.dirname(row["path"]) or "<root>"
        dir_stats[d]["files"] += 1
        dir_stats[d]["bytes"] += int(row["bytes"])
        ext = row["ext"]
        if ext == ".md":
            dir_stats[d]["md"] += 1
        elif ext == ".json":
            dir_stats[d]["json"] += 1
        elif ext in (".yaml", ".yml"):
            dir_stats[d]["yaml"] += 1
    dir_rows = [{"dir": d, **v} for d, v in dir_stats.items()]
    write_csv(out_dir / "DIRECTORY_STATS.csv", dir_rows, ["dir", "files", "bytes", "md", "json", "yaml"])

    # DOCS_INDEX + DOC_GRAPH + BROKEN_LINKS
    md_paths = [rel for rel in rel_paths if rel.lower().endswith(".md")]
    out_links: Dict[str, List[str]] = defaultdict(list)
    in_links: Dict[str, List[str]] = defaultdict(list)
    broken_rows = []

    for rel in md_paths:
        abs_path = repo_root / rel
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        cleaned = strip_code(text)
        for raw in extract_md_links(cleaned):
            nl = normalize_link(raw)
            if not nl or nl.startswith("#"):
                continue
            resolved = resolve_path(rel, nl)
            exists = resolved in rel_set
            if not exists and "." not in os.path.basename(resolved):
                if (resolved + ".md") in rel_set:
                    resolved = resolved + ".md"
                    exists = True
            if not exists:
                broken_rows.append({"src": rel, "link": raw, "resolved": resolved})
            # doc graph only for existing md links
            if resolved.lower().endswith(".md") and exists:
                out_links[rel].append(resolved)
                in_links[resolved].append(rel)

    doc_rows = []
    for rel in md_paths:
        abs_path = repo_root / rel
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        title = extract_title(strip_code(text), os.path.basename(rel))
        doc_rows.append({
            "path": rel,
            "title": title,
            "bytes": abs_path.stat().st_size,
            "out_md_links": len(out_links.get(rel, [])),
            "in_md_links": len(in_links.get(rel, [])),
        })
    write_csv(out_dir / "DOCS_INDEX.csv", doc_rows, ["path", "title", "bytes", "out_md_links", "in_md_links"])
    write_csv(out_dir / "BROKEN_LINKS.csv", broken_rows, ["src", "link", "resolved"])

    graph = {"nodes": [{"path": r["path"], "title": r["title"]} for r in doc_rows], "edges": []}
    for src, tgts in out_links.items():
        for tgt in tgts:
            graph["edges"].append({"from": src, "to": tgt, "type": "md_link"})
    (out_dir / "DOC_GRAPH.json").write_text(json.dumps(graph, indent=2), encoding="utf-8")

    # THEORY section parsing (optional)
    if theory_path:
        theory_abs = (repo_root / theory_path).resolve() if not theory_path.is_absolute() else theory_path
        if theory_abs.exists():
            t = theory_abs.read_text(encoding="utf-8", errors="replace")
            sections = []
            current = None
            for line in t.splitlines():
                m = MARKER_RE.search(line)
                if not m:
                    continue
                key, val = m.group(1).strip(), m.group(2).strip()
                if key == "SECTION":
                    current = {"id": val, "meta": {}}
                    sections.append(current)
                elif key == "END_SECTION":
                    current = None
                else:
                    if current is not None:
                        current["meta"][key] = val

            dep_edges = []
            for s in sections:
                deps = [d.strip() for d in s["meta"].get("DEPENDS_ON", "").split(",") if d.strip() and d.strip().lower() != "none"]
                for d in deps:
                    dep_edges.append({"from": d, "to": s["id"], "type": "depends_on"})

            # csv registry
            reg_rows = []
            for s in sections:
                meta = s["meta"]
                reg_rows.append({
                    "section_id": s["id"],
                    "order": meta.get("ORDER", ""),
                    "topic": meta.get("TOPIC", ""),
                    "depends_on": meta.get("DEPENDS_ON", ""),
                    "provides": meta.get("PROVIDES", ""),
                    "status": meta.get("STATUS", ""),
                    "version": meta.get("VERSION", ""),
                })
            write_csv(out_dir / "THEORY_SECTION_REGISTRY.csv", reg_rows, ["section_id", "order", "topic", "depends_on", "provides", "status", "version"])
            (out_dir / "THEORY_SECTION_GRAPH.json").write_text(json.dumps({"nodes": reg_rows, "edges": dep_edges}, indent=2), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root", type=str, help="Path to repo root")
    ap.add_argument("--out", type=str, default="_repo_map", help="Output directory")
    ap.add_argument("--theory", type=str, default="", help="Optional path to THEORY.md for marker extraction")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    theory = Path(args.theory) if args.theory else None

    build_indexes(repo_root, out_dir, theory_path=theory)
    print(f"Wrote indexes to: {out_dir}")

if __name__ == "__main__":
    main()
