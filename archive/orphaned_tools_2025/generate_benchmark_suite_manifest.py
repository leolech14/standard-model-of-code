#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_RE = re.compile(r"`([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)`")


HUGE_BY_DEFAULT = {
    "torvalds/linux",
    "tensorflow/tensorflow",
    "pytorch/pytorch",
    "kubernetes/kubernetes",
    "golang/go",
    "postgres/postgres",
    "mongodb/mongo",
    "docker/docker",
    "angular/angular",
    "facebook/react",
    "microsoft/TypeScript",
    "godotengine/godot",
    "gitlabhq/gitlabhq",
    "odoo/odoo",
    "elastic/elasticsearch",
    "jenkinsci/jenkins",
    "rails/rails",
    "FFmpeg/FFmpeg",
}


AUTO_PYTHON_DDD = {
    # Real repos already referenced in this workspace.
    "pgorecki/python-ddd",
    "ledmonster/ddd-python-inject",
}


@dataclass(frozen=True)
class RepoEntry:
    repo: str
    repo_dir: str
    enabled: bool
    suite: str
    spec_strategy: str
    specs: list[str]
    clone_url: str | None = None
    local_path: str | None = None
    notes: str | None = None


def _posix(path: Path) -> str:
    return path.as_posix()


def _repo_dir(owner_repo: str) -> str:
    owner, name = owner_repo.split("/", 1)
    return f"{owner}__{name}"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_repos(md_text: str) -> list[str]:
    return sorted({m.group(1) for m in REPO_RE.finditer(md_text)})


def _override(repo: str) -> RepoEntry | None:
    if repo == "iktakahiro/dddpy":
        return RepoEntry(
            repo=repo,
            repo_dir="dddpy_real",
            enabled=True,
            suite="golden",
            spec_strategy="manual",
            specs=[
                "spectrometer_v12_minimal/validation/benchmarks/specs/dddpy_real_onion_v1.bench.json",
            ],
            clone_url="https://github.com/iktakahiro/dddpy.git",
            local_path="spectrometer_v12_minimal/validation/dddpy_real",
            notes="Vendored fixture already present in workspace.",
        )
    return None


def build_manifest(repos: list[str]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    for repo in repos:
        ov = _override(repo)
        if ov is not None:
            entries.append(ov.__dict__)
            continue

        repo_dir = _repo_dir(repo)
        clone_url = f"https://github.com/{repo}.git"
        enabled = repo in AUTO_PYTHON_DDD or repo not in HUGE_BY_DEFAULT
        suite = "golden" if repo in AUTO_PYTHON_DDD else "discovery"
        spec_strategy = "auto_python_ddd_paths" if repo in AUTO_PYTHON_DDD else "none"
        entries.append(
            RepoEntry(
                repo=repo,
                repo_dir=repo_dir,
                enabled=enabled,
                suite=suite,
                spec_strategy=spec_strategy,
                specs=[],
                clone_url=clone_url,
                local_path=None,
                notes=None,
            ).__dict__
        )

    entries.sort(key=lambda e: (e["suite"], e["repo"].lower()))

    return {
        "version": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "spectrometer_v12_minimal/validation/iteration_test_repos.md",
        "suites": {"golden": "repos with golden specs", "discovery": "real repos without golden truth (yet)"},
        "entries": entries,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate benchmark suite manifest from iteration repo list.")
    parser.add_argument(
        "--in-md",
        default="spectrometer_v12_minimal/validation/iteration_test_repos.md",
        help="Input Markdown file containing referenced GitHub repos.",
    )
    parser.add_argument(
        "--out",
        default="spectrometer_v12_minimal/validation/benchmarks/suite_manifest.json",
        help="Output manifest JSON path.",
    )
    args = parser.parse_args(argv)

    repo_root = Path.cwd().resolve()
    in_path = (repo_root / args.in_md).resolve() if not Path(args.in_md).is_absolute() else Path(args.in_md).resolve()
    out_path = (repo_root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()

    md = _read_text(in_path)
    repos = _extract_repos(md)
    manifest = build_manifest(repos)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote: {out_path.relative_to(repo_root)} ({len(repos)} repos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(list(__import__("sys").argv[1:])))

