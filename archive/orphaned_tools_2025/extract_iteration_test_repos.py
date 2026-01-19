#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


GITHUB_URL_RE = re.compile(r"https?://github\.com/([^\s)\]\">]+)")
GITHUB_SSH_RE = re.compile(r"git@github\.com:([^\s)\]\">]+)")


@dataclass(frozen=True)
class RepoHit:
    repo: str
    full: str


def _clean_suffix(text: str) -> str:
    return text.rstrip("`'\".,;:)")


def _normalize_repo(path_part: str) -> RepoHit | None:
    s = _clean_suffix(path_part.strip())
    if s.endswith(".git"):
        s = s[:-4]
    if not s:
        return None

    parts = s.split("/")
    if len(parts) < 2:
        return None

    owner = parts[0].strip()
    repo = parts[1].split("?")[0].split("#")[0].strip()

    if not owner or not repo:
        return None
    if owner == "user-attachments":
        return None
    if owner in {"search", "topics", "marketplace", "settings", "features", "sponsors"}:
        return None

    return RepoHit(repo=f"{owner}/{repo}", full=s)


def _scan_text_for_repos(text: str) -> list[RepoHit]:
    hits: list[RepoHit] = []
    for m in GITHUB_URL_RE.finditer(text):
        hit = _normalize_repo(m.group(1))
        if hit:
            hits.append(RepoHit(repo=hit.repo, full="https://github.com/" + _clean_suffix(m.group(1))))
    for m in GITHUB_SSH_RE.finditer(text):
        hit = _normalize_repo(m.group(1))
        if hit:
            hits.append(RepoHit(repo=hit.repo, full="git@github.com:" + _clean_suffix(m.group(1))))
    return hits


def _unique_repos(hits: Iterable[RepoHit]) -> list[str]:
    return sorted({h.repo for h in hits})


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_batch_analysis_repos(path: Path) -> list[RepoHit]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    hits: list[RepoHit] = []
    for row in obj.get("repository_results") or []:
        url = str(row.get("url") or "").strip()
        if not url:
            continue
        m = GITHUB_URL_RE.search(url)
        if not m:
            continue
        hit = _normalize_repo(m.group(1))
        if hit:
            hits.append(RepoHit(repo=hit.repo, full=url))
    return hits


def _extract_git_origin_repo(config_path: Path) -> list[RepoHit]:
    hits: list[RepoHit] = []
    for line in _read_text(config_path).splitlines():
        if "url" not in line:
            continue
        m = GITHUB_URL_RE.search(line)
        if m:
            hit = _normalize_repo(m.group(1))
            if hit:
                hits.append(RepoHit(repo=hit.repo, full="https://github.com/" + _clean_suffix(m.group(1))))
        m = GITHUB_SSH_RE.search(line)
        if m:
            hit = _normalize_repo(m.group(1))
            if hit:
                hits.append(RepoHit(repo=hit.repo, full="git@github.com:" + _clean_suffix(m.group(1))))
    return hits


def _format_repo_list(repos: list[str]) -> list[str]:
    return [f"- `{r}`" for r in repos]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Extract GitHub repos referenced by iteration/testing context files.")
    parser.add_argument(
        "--out",
        default="spectrometer_v12_minimal/validation/iteration_test_repos.md",
        help="Output Markdown file path",
    )
    args = parser.parse_args(argv)

    repo_root = Path.cwd().resolve()

    sources: list[tuple[str, Path, str]] = [
        ("Local fixture origin", repo_root / "spectrometer_v12_minimal/validation/dddpy_real/.git/config", "git_origin"),
        ("Batch analysis (executed)", repo_root / "batch_analysis_results.json", "batch_json"),
        ("Curated validation dataset", repo_root / "validation_dataset.py", "text"),
        ("Controlled repos validator", repo_root / "controlled_repos_validator.py", "text"),
        ("V11 external validation", repo_root / "spectrometer_v11_external_validation.py", "text"),
        ("Code smell benchmarks", repo_root / "code_smell_validator.py", "text"),
        ("V13 phased plan (doc)", repo_root / "V13-GROK.md", "text"),
        ("V13 phase 1 script", repo_root / "phase1_test.py", "text"),
        ("V13 rigorous framework", repo_root / "rigorous_test_framework.py", "text"),
        ("Third-party validation (pgorecki)", repo_root / "THIRD_PARTY_VALIDATION_PGORECKI.md", "text"),
        ("Touchpoints source notes", repo_root / "TOUCHPOINTS", "text"),
    ]

    repos_by_source: dict[str, list[str]] = {}
    repo_to_sources: dict[str, set[str]] = defaultdict(set)

    for label, path, kind in sources:
        if not path.exists():
            continue
        if kind == "batch_json":
            hits = _extract_batch_analysis_repos(path)
        elif kind == "git_origin":
            hits = _extract_git_origin_repo(path)
        else:
            hits = _scan_text_for_repos(_read_text(path))

        repos = _unique_repos(hits)
        repos_by_source[label] = repos
        for r in repos:
            repo_to_sources[r].add(label)

    all_repos = sorted(repo_to_sources.keys())

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Iteration Test Repos (From Context Files)")
    lines.append("")
    lines.append("This list is extracted from the project’s context/testing assets (docs + scripts).")
    lines.append("It is intended to reconstruct which external GitHub repos were used or proposed during iterations.")
    lines.append("")
    lines.append(f"- Unique repos (all sources): {len(all_repos)}")
    lines.append("")

    lines.append("## Sources")
    for label in sources:
        name = label[0]
        if name in repos_by_source:
            lines.append(f"- {name}: {len(repos_by_source[name])} repos")
    lines.append("")

    lines.append("## Confirmed / Executed")
    if "Local fixture origin" in repos_by_source:
        lines.append("- Local fixture(s) present in this workspace:")
        lines.extend(_format_repo_list(repos_by_source["Local fixture origin"]))
    if "Batch analysis (executed)" in repos_by_source:
        lines.append("- Batch analysis sample (from `batch_analysis_results.json`):")
        lines.extend(_format_repo_list(repos_by_source["Batch analysis (executed)"]))
    lines.append("")

    lines.append("## Proposed / Mentioned Targets (By Source)")
    for label, repos in sorted(repos_by_source.items(), key=lambda kv: kv[0].lower()):
        if label in {"Local fixture origin", "Batch analysis (executed)"}:
            continue
        lines.append(f"### {label}")
        if repos:
            lines.extend(_format_repo_list(repos))
        else:
            lines.append("- (none)")
        lines.append("")

    lines.append("## Repo → Sources Map")
    for repo in all_repos:
        srcs = ", ".join(sorted(repo_to_sources[repo]))
        lines.append(f"- `{repo}` — {srcs}")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

