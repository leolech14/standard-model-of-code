#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    "coverage",
    "vendor",
    "third_party",
    "Pods",
}


ARCH_DOC_NAMES = {
    "architecture.md",
    "arch.md",
    "design.md",
    "system_design.md",
    "overview.md",
    "components.md",
    "component.md",
    "module.md",
    "modules.md",
}


ARCH_DOC_DIR_HINTS = {
    "docs/architecture",
    "docs/arch",
    "docs/design",
    "docs/adr",
    "adr",
    "doc/architecture",
    "doc/design",
    "architecture",
    "design",
}


ARCH_AS_CODE_GLOBS = [
    "**/structurizr.dsl",
    "**/*.workspace",
    "**/*.c4",
    "**/*c4*.puml",
    "**/*C4*.puml",
]


DIAGRAM_GLOBS = [
    "**/*.mmd",
    "**/*.mermaid",
    "**/*.puml",
    "**/*.plantuml",
    "**/*.drawio",
    "**/*.graphml",
    "**/*.dot",
]


CONFIG_CANDIDATES = [
    # Java/Gradle/Maven
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    # Node/TS
    "package.json",
    "eslint.config.js",
    ".eslintrc",
    ".eslintrc.json",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.yaml",
    ".eslintrc.yml",
    # Python
    "pyproject.toml",
    "requirements.txt",
    "setup.cfg",
    # Go
    "go.mod",
    # Rust
    "Cargo.toml",
]


BOUNDARY_KEYWORDS = {
    # Java
    "archunit": "archunit",
    "com.tngtech.archunit": "archunit",
    # Node/TS boundaries
    "eslint-plugin-boundaries": "eslint_boundaries",
    "\"boundaries\"": "eslint_boundaries",
    # dependency-cruiser
    "dependency-cruiser": "dependency_cruiser",
    "depcruise": "dependency_cruiser",
    # Python import-linter
    "import-linter": "import_linter",
}


@dataclass(frozen=True)
class RepoTruthSources:
    repo: str
    root: str
    languages_top: list[tuple[str, int]]
    architecture_docs: list[str]
    architecture_as_code: list[str]
    diagrams: list[str]
    boundary_configs: list[str]


def _posix(path: Path) -> str:
    return path.as_posix()


def _iter_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, names in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for name in names:
            files.append(Path(root) / name)
    return files


def _ext_language_counts(files: list[Path]) -> list[tuple[str, int]]:
    c: Counter[str] = Counter()
    for p in files:
        suffix = p.suffix.lower()
        if not suffix:
            continue
        c[suffix] += 1
    return c.most_common(12)


def _glob_rel(repo_root: Path, pattern: str) -> list[str]:
    matches: list[str] = []
    for p in repo_root.glob(pattern):
        if p.is_file():
            try:
                matches.append(_posix(p.relative_to(repo_root)))
            except ValueError:
                matches.append(_posix(p))
    return sorted(set(matches))


def _find_arch_docs(repo_root: Path, files: list[Path]) -> list[str]:
    docs: set[str] = set()
    for p in files:
        if not p.is_file():
            continue
        name = p.name.lower()
        if name in ARCH_DOC_NAMES or name in {"readme.md"}:
            rel = _posix(p.relative_to(repo_root))
            rel_lower = rel.lower()
            # Count top-level README.md as a weak-but-useful architecture hint.
            if name == "readme.md" and "/" not in rel_lower:
                docs.add(rel)
                continue
            # Also count README in likely docs/arch folders.
            if name != "readme.md" or any(hint in rel_lower for hint in ARCH_DOC_DIR_HINTS):
                docs.add(rel)

    # Also capture any file in a known arch/doc folder even if named differently.
    for p in files:
        if not p.is_file():
            continue
        rel = _posix(p.relative_to(repo_root))
        rel_lower = rel.lower()
        if any(rel_lower.startswith(hint + "/") or ("/" + hint + "/") in ("/" + rel_lower) for hint in ARCH_DOC_DIR_HINTS):
            if p.suffix.lower() in {".md", ".txt", ".rst"}:
                docs.add(rel)

    return sorted(docs)


def _scan_boundary_configs(repo_root: Path) -> tuple[list[str], set[str]]:
    hits: list[str] = []
    kinds: set[str] = set()
    for rel in CONFIG_CANDIDATES:
        p = repo_root / rel
        if not p.exists() or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        matched = False
        for needle, kind in BOUNDARY_KEYWORDS.items():
            if needle.lower() in text.lower():
                kinds.add(kind)
                matched = True
        if matched:
            hits.append(rel)
    return sorted(set(hits)), kinds


def scan_repo(repo_root: Path) -> RepoTruthSources:
    files = _iter_files(repo_root)
    languages_top = _ext_language_counts(files)

    architecture_as_code: set[str] = set()
    for pattern in ARCH_AS_CODE_GLOBS:
        architecture_as_code.update(_glob_rel(repo_root, pattern))

    diagrams: set[str] = set()
    for pattern in DIAGRAM_GLOBS:
        diagrams.update(_glob_rel(repo_root, pattern))

    architecture_docs = _find_arch_docs(repo_root, files)
    boundary_configs, _ = _scan_boundary_configs(repo_root)

    return RepoTruthSources(
        repo=repo_root.name,
        root=str(repo_root),
        languages_top=languages_top,
        architecture_docs=architecture_docs,
        architecture_as_code=sorted(architecture_as_code),
        diagrams=sorted(diagrams),
        boundary_configs=boundary_configs,
    )


def _to_jsonable(obj: RepoTruthSources) -> dict[str, Any]:
    return {
        "repo": obj.repo,
        "root": obj.root,
        "languages_top": obj.languages_top,
        "architecture_docs": obj.architecture_docs,
        "architecture_as_code": obj.architecture_as_code,
        "diagrams": obj.diagrams,
        "boundary_configs": obj.boundary_configs,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Scan local repos for architecture truth sources.")
    parser.add_argument(
        "--repos-dir",
        default="spectrometer_v12_minimal/validation/benchmarks/repos",
        help="Directory containing repo folders to scan.",
    )
    parser.add_argument(
        "--out",
        default="spectrometer_v12_minimal/validation/benchmarks/runs/truth_sources.json",
        help="Output JSON report path.",
    )
    args = parser.parse_args(argv)

    repos_dir = Path(args.repos_dir).resolve()
    if not repos_dir.exists():
        raise FileNotFoundError(str(repos_dir))

    rows: list[RepoTruthSources] = []
    for child in sorted(repos_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        rows.append(scan_repo(child))

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps([_to_jsonable(r) for r in rows], indent=2), encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv[1:]))
