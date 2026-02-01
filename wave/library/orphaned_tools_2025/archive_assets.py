#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Candidate:
    source: Path
    rule: str


def _load_plan(plan_path: Path) -> dict[str, Any]:
    with plan_path.open("r", encoding="utf-8") as f:
        plan = json.load(f)
    if not isinstance(plan, dict) or plan.get("version") != 1:
        raise ValueError(f"Unsupported plan format: {plan_path}")
    return plan


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _resolve_repo_root(start: Path) -> Path:
    return start.resolve()


def _iter_matches_by_rule(repo_root: Path, rule: dict[str, Any]) -> Iterable[Path]:
    kind = rule.get("kind")
    if kind == "path":
        for p in rule.get("paths", []):
            yield repo_root / p
        return

    if kind == "glob":
        include = rule.get("include", [])
        exclude = set(rule.get("exclude", []))
        for pattern in include:
            for match in repo_root.glob(pattern):
                rel = match.relative_to(repo_root)
                if _as_posix(rel) in exclude:
                    continue
                yield match
        return

    if kind == "dir_name":
        names = rule.get("names", [])
        for name in names:
            for match in repo_root.rglob(name):
                if match.is_dir():
                    yield match
        return

    raise ValueError(f"Unknown rule kind: {kind!r}")


def _iter_protected_paths(repo_root: Path, protected: list[str]) -> list[Path]:
    return [(repo_root / p).resolve() for p in protected]


def _is_protected(path: Path, protected_paths: list[Path]) -> bool:
    resolved = path.resolve()
    for protected in protected_paths:
        if resolved == protected or _is_within(resolved, protected):
            return True
    return False


def _dedupe_top_level(paths: list[Candidate]) -> list[Candidate]:
    sorted_candidates = sorted(paths, key=lambda c: (len(c.source.parts), _as_posix(c.source)))
    kept: list[Candidate] = []
    kept_sources: list[Path] = []
    for c in sorted_candidates:
        if any(_is_within(c.source, k) for k in kept_sources if k.is_dir()):
            continue
        kept.append(c)
        kept_sources.append(c.source)
    return kept


def _dir_size_bytes(path: Path) -> int:
    total = 0
    if path.is_file():
        return path.stat().st_size
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                continue
    return total


def _dir_file_count(path: Path) -> int:
    if path.is_file():
        return 1
    return sum(1 for p in path.rglob("*") if p.is_file())


def _safe_move(src: Path, dst: Path) -> Path:
    if not src.exists():
        raise FileNotFoundError(str(src))

    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.move(str(src), str(dst))
        return dst

    suffix = 1
    while True:
        alt = dst.with_name(f"{dst.name}.dup{suffix}")
        if not alt.exists():
            shutil.move(str(src), str(alt))
            return alt
        suffix += 1


def _archive_subdir(mode: str) -> str:
    now = datetime.now()
    if mode == "date":
        return now.strftime("%Y-%m-%d")
    if mode == "datetime":
        return now.strftime("%Y-%m-%d_%H%M%S")
    raise ValueError(f"Unknown archive_subdir_mode: {mode!r}")


def _print_summary(candidates: list[Candidate], repo_root: Path) -> None:
    by_rule: dict[str, list[Path]] = {}
    for c in candidates:
        by_rule.setdefault(c.rule, []).append(c.source)

    total_bytes = sum(_dir_size_bytes(c.source) for c in candidates if c.source.exists())
    total_files = sum(_dir_file_count(c.source) for c in candidates if c.source.exists())
    print(f"Selected: {len(candidates)} items, {total_files} files, {total_bytes/1e6:.1f} MB")
    for rule, paths in sorted(by_rule.items(), key=lambda kv: kv[0]):
        bytes_rule = sum(_dir_size_bytes(p) for p in paths if p.exists())
        print(f"- {rule}: {len(paths)} items, {bytes_rule/1e6:.1f} MB")

    if candidates:
        biggest = sorted(
            [(c.source, _dir_size_bytes(c.source)) for c in candidates if c.source.exists()],
            key=lambda kv: kv[1],
            reverse=True,
        )[:15]
        print("Biggest items:")
        for p, sz in biggest:
            rel = p.relative_to(repo_root)
            print(f"  - {rel} ({sz/1e6:.1f} MB)")


def build_candidates(repo_root: Path, plan: dict[str, Any]) -> list[Candidate]:
    return build_candidates_filtered(repo_root, plan, only_rules=None, skip_rules=None)


def build_candidates_filtered(
    repo_root: Path,
    plan: dict[str, Any],
    *,
    only_rules: set[str] | None,
    skip_rules: set[str] | None,
) -> list[Candidate]:
    protected_paths = _iter_protected_paths(repo_root, plan.get("protected_paths", []))
    candidates: list[Candidate] = []

    for rule in plan.get("rules", []):
        rule_name = rule.get("name", "unnamed")
        if only_rules and rule_name not in only_rules:
            continue
        if skip_rules and rule_name in skip_rules:
            continue
        skip_within = [(repo_root / p).resolve() for p in rule.get("skip_within_paths", [])]
        for match in _iter_matches_by_rule(repo_root, rule):
            if not match.exists():
                continue
            match_resolved = match.resolve()
            if any(_is_within(match_resolved, parent) for parent in skip_within):
                continue
            if _is_protected(match, protected_paths):
                continue
            candidates.append(Candidate(source=match, rule=rule_name))

    # Normalize: prefer moving directories/files at the top-most level only
    return _dedupe_top_level(candidates)


def apply_archive(repo_root: Path, plan: dict[str, Any], candidates: list[Candidate]) -> Path:
    archive_root = (repo_root / plan["archive_root"]).resolve()
    subdir = _archive_subdir(plan.get("archive_subdir_mode", "date"))
    archive_dest = (archive_root / subdir).resolve()
    archive_dest.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "version": 1,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "archive_dir": str(archive_dest),
        "items": [],
    }

    for c in candidates:
        src = c.source.resolve()
        rel = src.relative_to(repo_root)
        dst = archive_dest / rel

        moved_to = _safe_move(src, dst)
        size_bytes = _dir_size_bytes(moved_to)
        file_count = _dir_file_count(moved_to)

        manifest["items"].append(
            {
                "rule": c.rule,
                "source": _as_posix(rel),
                "archived_to": _as_posix(moved_to.relative_to(repo_root)),
                "is_dir": moved_to.is_dir(),
                "size_bytes": size_bytes,
                "file_count": file_count,
            }
        )

    manifest_path = archive_dest / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    summary_path = archive_dest / "manifest.md"
    total_bytes = sum(i["size_bytes"] for i in manifest["items"])
    total_files = sum(i["file_count"] for i in manifest["items"])
    by_rule: dict[str, dict[str, int]] = {}
    for i in manifest["items"]:
        agg = by_rule.setdefault(i["rule"], {"items": 0, "bytes": 0})
        agg["items"] += 1
        agg["bytes"] += i["size_bytes"]

    lines = [
        "# Archive Manifest",
        "",
        f"- Created: `{manifest['created_at']}`",
        f"- Archive dir: `{_as_posix(archive_dest.relative_to(repo_root))}`",
        f"- Items: {len(manifest['items'])}",
        f"- Files: {total_files}",
        f"- Size: {total_bytes/1e6:.1f} MB",
        "",
        "## By rule",
    ]
    for rule in sorted(by_rule):
        lines.append(f"- `{rule}`: {by_rule[rule]['items']} items, {by_rule[rule]['bytes']/1e6:.1f} MB")
    lines.append("")
    lines.append("## Items")
    for i in manifest["items"]:
        lines.append(f"- `{i['source']}` → `{i['archived_to']}`")
    lines.append("")
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    return manifest_path


def undo_archive(repo_root: Path, manifest_path: Path) -> None:
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ValueError("Unsupported manifest format")

    items = manifest.get("items", [])
    # Reverse: move deepest paths first
    items_sorted = sorted(items, key=lambda i: len(str(i.get("archived_to", "")).split("/")), reverse=True)
    for i in items_sorted:
        src = (repo_root / i["archived_to"]).resolve()
        dst = (repo_root / i["source"]).resolve()
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            raise FileExistsError(f"Refusing to overwrite existing path: {dst}")
        shutil.move(str(src), str(dst))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Safely archive assets into ARCHIVE/ (dry-run first).")
    parser.add_argument("--plan", default="tools/archive_plan.json", help="Path to archive plan JSON")
    parser.add_argument(
        "--only-rule",
        action="append",
        default=[],
        help="Archive only these rules (repeatable).",
    )
    parser.add_argument(
        "--skip-rule",
        action="append",
        default=[],
        help="Skip these rules (repeatable).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print what would be archived")
    mode.add_argument("--apply", action="store_true", help="Move items into ARCHIVE/ and write a manifest")
    mode.add_argument("--undo", metavar="MANIFEST", help="Undo an archive using the manifest.json path")
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(Path.cwd())

    if args.undo:
        undo_archive(repo_root, Path(args.undo).resolve())
        print("Undo complete.")
        return 0

    plan_path = (repo_root / args.plan).resolve() if not Path(args.plan).is_absolute() else Path(args.plan).resolve()
    plan = _load_plan(plan_path)

    only_rules = set(args.only_rule) or None
    skip_rules = set(args.skip_rule) or None
    candidates = build_candidates_filtered(repo_root, plan, only_rules=only_rules, skip_rules=skip_rules)
    _print_summary(candidates, repo_root)

    if args.dry_run:
        print("\nDry run only. To apply: python3 tools/archive_assets.py --apply")
        return 0

    manifest_path = apply_archive(repo_root, plan, candidates)
    rel_manifest = manifest_path.relative_to(repo_root)
    print(f"\nArchive applied. Manifest: {rel_manifest}")
    print(f"Undo: python3 tools/archive_assets.py --undo {rel_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
