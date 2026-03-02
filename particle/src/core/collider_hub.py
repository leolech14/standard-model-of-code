#!/usr/bin/env python3
"""
Collider Hub: canonical wrapper for reliable, repeatable Collider runs.

Goals:
- One stable entrypoint for agents and humans.
- Always write outputs to <repo>/.collider.
- Keep .collider locally git-ignored.
- Apply ecosystem noise exclusions by default (overrideable).
- Make MCP checks use explicit db_dir to avoid auto-detection drift.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

_THIS = Path(__file__).resolve()
_PARTICLE_ROOT = _THIS.parents[1]
_ELEMENTS_ROOT = _PARTICLE_ROOT.parent

DEFAULT_CANDIDATES = [
    str(_PARTICLE_ROOT / "collider"),
    str(_ELEMENTS_ROOT / "collider"),
    "collider",
]

PROFILE_EXCLUDES = {
    "strict": [],
    # Safe defaults for most repos.
    "balanced": [
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        "tmp",
        "temp",
        ".next",
    ],
    # Ecosystem profile: balanced + known high-noise paths seen here.
    "ecosystem": [
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        "tmp",
        "temp",
        ".next",
        ".claude/worktrees",
        "workspace/.openclaw/extensions",
        "docs/ECOSYSTEM_DIAGRAM_files",
    ],
}


def _repo_root(path: Path) -> Path:
    return path.resolve()


def _resolve_output_dir(repo: Path, output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()
    return (repo / ".collider").resolve()


def _ensure_local_ignore(repo: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    gitignore = output_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")

    git_dir = repo / ".git"
    if not git_dir.exists():
        return

    exclude = git_dir / "info" / "exclude"
    try:
        if exclude.parent.exists():
            current = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
            lines = {line.strip() for line in current.splitlines()}
            if ".collider/" not in lines:
                prefix = "" if (not current or current.endswith("\n")) else "\n"
                exclude.write_text(f"{current}{prefix}.collider/\n", encoding="utf-8")
            return
    except OSError:
        pass

    # Fallback for constrained environments where .git/info/exclude is not writable.
    root_gitignore = repo / ".gitignore"
    try:
        current = root_gitignore.read_text(encoding="utf-8") if root_gitignore.exists() else ""
        lines = {line.strip() for line in current.splitlines()}
        if ".collider/" not in lines:
            prefix = "" if (not current or current.endswith("\n")) else "\n"
            root_gitignore.write_text(f"{current}{prefix}.collider/\n", encoding="utf-8")
    except OSError:
        pass


def _resolve_collider_bin(explicit: str | None) -> str:
    candidates: list[str] = []
    if explicit:
        candidates.append(explicit)
    env_bin = os.environ.get("COLLIDER_BIN", "").strip()
    if env_bin:
        candidates.append(env_bin)
    candidates.extend(DEFAULT_CANDIDATES)

    seen: set[str] = set()
    for cand in candidates:
        cand = cand.strip()
        if not cand or cand in seen:
            continue
        seen.add(cand)
        p = Path(cand).expanduser()
        if "/" in cand:
            if p.exists():
                return str(p.resolve())
            continue
        found = shutil.which(cand)
        if found:
            return found
    raise FileNotFoundError(
        "Could not find Collider CLI. Set COLLIDER_BIN or pass --collider-bin."
    )


def _run(cmd: Sequence[str], cwd: Path | None = None) -> int:
    proc = subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, check=False)
    return proc.returncode


def _build_full_cmd(
    collider_bin: str,
    repo: Path,
    output_dir: Path,
    profile: str,
    no_default_excludes: bool,
    extra_excludes: Sequence[str],
    passthrough: Sequence[str],
    html: bool,
    no_timing: bool,
) -> list[str]:
    cmd = [
        collider_bin,
        "full",
        str(repo),
        "--output",
        str(output_dir),
        "--db",
        str(output_dir / "collider.db"),
        "--no-open",
    ]
    if not no_timing:
        cmd.append("--timing")
    if html:
        cmd.append("--html")

    excludes: list[str] = []
    if not no_default_excludes:
        excludes.extend(PROFILE_EXCLUDES.get(profile, PROFILE_EXCLUDES["ecosystem"]))
    excludes.extend(extra_excludes)
    for ex in excludes:
        cmd.extend(["--exclude", ex])
    cmd.extend(passthrough)
    return cmd


def _validate_artifacts(output_dir: Path) -> tuple[bool, list[str]]:
    required = [
        output_dir / "unified_analysis.json",
        output_dir / "collider_insights.json",
        output_dir / "collider.db",
    ]
    missing = [str(p) for p in required if not p.exists()]
    return (len(missing) == 0, missing)


def _read_insights(output_dir: Path) -> dict:
    path = output_dir / "collider_insights.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def cmd_full(args: argparse.Namespace) -> int:
    repo = _repo_root(Path(args.repo))
    output_dir = _resolve_output_dir(repo, args.output_dir)
    _ensure_local_ignore(repo, output_dir)
    collider_bin = _resolve_collider_bin(args.collider_bin)

    cmd = _build_full_cmd(
        collider_bin=collider_bin,
        repo=repo,
        output_dir=output_dir,
        profile=args.profile,
        no_default_excludes=args.no_default_excludes,
        extra_excludes=args.exclude or [],
        passthrough=args.passthrough or [],
        html=args.html,
        no_timing=args.no_timing,
    )

    print("Collider Hub")
    print(f"  repo: {repo}")
    print(f"  output: {output_dir}")
    print(f"  collider: {collider_bin}")
    print("  command:")
    print("   " + " ".join(cmd))
    if args.dry_run:
        return 0
    return _run(cmd)


def cmd_smoke(args: argparse.Namespace) -> int:
    repo = _repo_root(Path(args.repo))
    output_dir = _resolve_output_dir(repo, args.output_dir)
    _ensure_local_ignore(repo, output_dir)
    collider_bin = _resolve_collider_bin(args.collider_bin)

    full_cmd = _build_full_cmd(
        collider_bin=collider_bin,
        repo=repo,
        output_dir=output_dir,
        profile=args.profile,
        no_default_excludes=args.no_default_excludes,
        extra_excludes=args.exclude or [],
        passthrough=args.passthrough or [],
        html=False,
        no_timing=False,
    )

    print("Collider Hub Smoke")
    print("  step 1/3: full run")
    rc = _run(full_cmd)
    if rc != 0:
        return rc

    print("  step 2/3: artifact validation")
    ok, missing = _validate_artifacts(output_dir)
    if not ok:
        print("  missing artifacts:")
        for m in missing:
            print(f"   - {m}")
        return 2

    print("  step 3/3: summary")
    insights = _read_insights(output_dir)
    if insights:
        sev = insights.get("findings_by_severity", {})
        print("  findings_by_severity:", sev)
    if args.with_grade:
        print("  step 4/4: grade")
        grade_cmd = [collider_bin, "grade", str(repo), "--json"]
        rc = _run(grade_cmd)
        if rc != 0:
            return rc
    return 0


def cmd_mcp_check(args: argparse.Namespace) -> int:
    repo = _repo_root(Path(args.repo))
    output_dir = _resolve_output_dir(repo, args.output_dir)
    _ensure_local_ignore(repo, output_dir)

    mcporter = shutil.which("mcporter")
    if not mcporter:
        print("mcporter not found in PATH")
        return 3

    print("Collider Hub MCP Check")
    list_cmd = [mcporter, "list", "--json"]
    rc = _run(list_cmd)
    if rc != 0:
        return rc

    overview_cmd = [
        mcporter,
        "call",
        "collider.collider_overview",
        f"db_dir={output_dir}",
        "--output",
        "json",
    ]
    return _run(overview_cmd)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Canonical Collider wrapper for cross-agent ecosystem usage."
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--repo", default=".", help="Target repository path")
        sp.add_argument(
            "--output-dir",
            default=None,
            help="Output directory (default: <repo>/.collider)",
        )
        sp.add_argument(
            "--collider-bin",
            default=None,
            help="Explicit collider CLI path (overrides auto-detection)",
        )
        sp.add_argument(
            "--profile",
            choices=sorted(PROFILE_EXCLUDES.keys()),
            default="ecosystem",
            help="Default exclusion profile",
        )
        sp.add_argument(
            "--no-default-excludes",
            action="store_true",
            help="Disable profile excludes",
        )
        sp.add_argument(
            "--exclude",
            action="append",
            default=[],
            help="Extra exclude path (repeatable)",
        )

    full = sub.add_parser("full", help="Run full Collider analysis with canonical defaults")
    add_common(full)
    full.add_argument("--html", action="store_true", help="Generate HTML output")
    full.add_argument("--no-timing", action="store_true", help="Disable --timing flag")
    full.add_argument("--dry-run", action="store_true", help="Print command without running")
    full.add_argument(
        "passthrough",
        nargs=argparse.REMAINDER,
        help="Extra args passed to collider full (prefix with --)",
    )
    full.set_defaults(func=cmd_full)

    smoke = sub.add_parser(
        "smoke",
        help="Run full + artifact validation as a reliability test (optional grade)",
    )
    add_common(smoke)
    smoke.add_argument(
        "--with-grade",
        action="store_true",
        help="Also run collider grade (slower; runs another full analysis internally)",
    )
    smoke.add_argument(
        "passthrough",
        nargs=argparse.REMAINDER,
        help="Extra args passed to collider full (prefix with --)",
    )
    smoke.set_defaults(func=cmd_smoke)

    mcp = sub.add_parser(
        "mcp-check",
        help="Verify MCP collider service with explicit db_dir",
    )
    add_common(mcp)
    mcp.set_defaults(func=cmd_mcp_check)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
