#!/usr/bin/env python3
"""
Collider Hub: canonical wrapper for reliable, repeatable Collider runs.

Goals:
- One stable entrypoint for agents and humans.
- Always write analysis outputs to <repo>/.collider.
- Institutionalize feedback by writing a post-run package to <repo>/.collider/feedback.
- Keep Collider output and feedback directories locally git-ignored.
- Apply ecosystem noise exclusions by default (overrideable).
- Make MCP checks use explicit db_dir to avoid auto-detection drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

_THIS = Path(__file__).resolve()
_PARTICLE_ROOT = _THIS.parents[2]
_ELEMENTS_ROOT = _THIS.parents[3]
_CENTRAL_FEEDBACK_ROOT = Path(
    os.environ.get("COLLIDER_CENTRAL_FEEDBACK_DIR", str(_ELEMENTS_ROOT / "collider_feedback"))
).expanduser()

DEFAULT_CANDIDATES = [
    str(_PARTICLE_ROOT / "collider"),
    str(_ELEMENTS_ROOT / "collider"),
    "collider",
]

_PERF_SIGNAL_TOKENS = ("cost", "time", "latency", "duration", "tau", "\u03c4", "throughput")

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
        ".collider",
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
        ".collider",
        "collider_output",
        "docs/standard-model",
        "docs/standard-model-registry.json",
        ".claude/worktrees",
        "workspace/.openclaw/extensions",
        "docs/ECOSYSTEM_DIAGRAM_files",
    ],
}


def _repo_root(path: Path) -> Path:
    return path.resolve()


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _slug(value: str) -> str:
    safe = []
    for ch in value.lower():
        safe.append(ch if ch.isalnum() else "-")
    text = "".join(safe).strip("-")
    while "--" in text:
        text = text.replace("--", "-")
    return text or "unknown"


def _resolve_output_dir(repo: Path, output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()
    return (repo / ".collider").resolve()


def _resolve_feedback_dir(
    repo: Path,
    output_dir: Path,
    feedback_dir: str | None,
    legacy_reh_dir: str | None = None,
) -> Path:
    # Backward compatibility for existing wrappers using --reh-dir.
    candidate = feedback_dir or legacy_reh_dir
    if candidate:
        return Path(candidate).expanduser().resolve()
    return (output_dir / "feedback").resolve()


def _ignore_pattern(repo: Path, hidden_dir: Path) -> str | None:
    try:
        rel = hidden_dir.resolve().relative_to(repo.resolve())
    except ValueError:
        return None
    rel_text = rel.as_posix().strip("/")
    if not rel_text:
        return None
    return f"{rel_text}/"


def _ensure_local_ignore(repo: Path, hidden_dir: Path) -> None:
    hidden_dir.mkdir(parents=True, exist_ok=True)
    gitignore = hidden_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n", encoding="utf-8")

    pattern = _ignore_pattern(repo, hidden_dir)
    if not pattern:
        return

    git_dir = repo / ".git"
    if not git_dir.exists():
        return

    exclude = git_dir / "info" / "exclude"
    try:
        if exclude.parent.exists():
            current = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
            lines = {line.strip() for line in current.splitlines()}
            if pattern not in lines:
                prefix = "" if (not current or current.endswith("\n")) else "\n"
                exclude.write_text(f"{current}{prefix}{pattern}\n", encoding="utf-8")
            return
    except OSError:
        pass

    # Fallback for constrained environments where .git/info/exclude is not writable.
    root_gitignore = repo / ".gitignore"
    try:
        current = root_gitignore.read_text(encoding="utf-8") if root_gitignore.exists() else ""
        lines = {line.strip() for line in current.splitlines()}
        if pattern not in lines:
            prefix = "" if (not current or current.endswith("\n")) else "\n"
            root_gitignore.write_text(f"{current}{prefix}{pattern}\n", encoding="utf-8")
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


def _run_capture(cmd: Sequence[str], timeout_sec: int = 90) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"


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


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _read_insights(output_dir: Path) -> dict[str, Any]:
    return _read_json(output_dir / "collider_insights.json")


def _read_unified(output_dir: Path) -> dict[str, Any]:
    return _read_json(output_dir / "unified_analysis.json")


def _path_is_perf_signal(path: str) -> bool:
    lower = path.lower()
    return any(token in lower for token in _PERF_SIGNAL_TOKENS)


def _collect_negative_perf_values(obj: Any, path: str = "", limit: int = 20) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    def visit(value: Any, value_path: str) -> None:
        if len(findings) >= limit:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{value_path}.{key}" if value_path else str(key)
                visit(child, child_path)
            return
        if isinstance(value, list):
            for idx, child in enumerate(value):
                child_path = f"{value_path}[{idx}]"
                visit(child, child_path)
            return
        if isinstance(value, (int, float)) and value < 0 and _path_is_perf_signal(value_path):
            findings.append({"path": value_path, "value": value})

    visit(obj, path)
    return findings


def _extract_counts(unified: dict[str, Any]) -> tuple[int, int]:
    nodes = unified.get("nodes")
    edges = unified.get("edges")
    node_count = len(nodes) if isinstance(nodes, list) else 0
    edge_count = len(edges) if isinstance(edges, list) else 0

    counts = unified.get("counts")
    if isinstance(counts, dict):
        if node_count == 0:
            node_count = int(counts.get("nodes") or counts.get("total_nodes") or 0)
        if edge_count == 0:
            edge_count = int(counts.get("edges") or counts.get("total_edges") or 0)
    return node_count, edge_count


def _extract_top_findings(insights: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    findings = insights.get("findings")
    if not isinstance(findings, list):
        return []
    top: list[dict[str, Any]] = []
    for item in findings:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("finding") or item.get("message") or "untitled_finding"
        severity = item.get("severity", "unknown")
        evidence = item.get("evidence") or item.get("source") or item.get("path") or ""
        confidence = item.get("confidence")
        entry: dict[str, Any] = {
            "severity": str(severity).lower(),
            "title": str(title),
            "evidence": str(evidence),
        }
        if confidence is not None:
            entry["confidence"] = confidence
        top.append(entry)
        if len(top) >= limit:
            break
    return top


def _legacy_artifact_signals(repo: Path, output_dir: Path) -> list[str]:
    candidates = [
        repo / "collider_output" / "proof_output.json",
        repo / "docs" / "standard-model" / "repo" / "proof_output.json",
        repo / "docs" / "standard-model-registry.json",
    ]
    found = [str(p) for p in candidates if p.exists()]
    if not found:
        return []
    output_dir_s = str(output_dir.resolve())
    return [p for p in found if not p.startswith(output_dir_s)]


def _build_auto_feedback(repo: Path, output_dir: Path, run_mode: str) -> dict[str, Any]:
    insights = _read_insights(output_dir)
    unified = _read_unified(output_dir)

    checks: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    ok, missing = _validate_artifacts(output_dir)
    checks.append(
        {
            "id": "required_artifacts",
            "status": "pass" if ok else "fail",
            "details": "required Collider artifacts present" if ok else "missing required Collider artifacts",
            "evidence": missing,
            "action": "re-run collider-hub full and verify output contract",
        }
    )
    if missing:
        issues.append(
            {
                "severity": "critical",
                "title": "Missing required output artifacts",
                "evidence": missing,
                "action": "re-run full analysis and fix output generation failures",
            }
        )

    node_count, edge_count = _extract_counts(unified)
    edge_ok = not (node_count > 0 and edge_count == 0)
    checks.append(
        {
            "id": "edge_extraction",
            "status": "pass" if edge_ok else "warn",
            "details": f"nodes={node_count}, edges={edge_count}",
            "action": "improve language/runtime edge extraction when nodes > 0 and edges == 0",
        }
    )
    if not edge_ok:
        issues.append(
            {
                "severity": "high",
                "title": "Node extraction succeeded but edge extraction returned zero",
                "evidence": [f"nodes={node_count}", f"edges={edge_count}"],
                "action": "prioritize call/import edge extraction for this repository pattern",
            }
        )

    negative_signals = _collect_negative_perf_values(unified)
    checks.append(
        {
            "id": "performance_sign",
            "status": "pass" if not negative_signals else "fail",
            "details": "no negative performance values detected" if not negative_signals else "negative performance values detected",
            "evidence": negative_signals[:10],
            "action": "clamp/validate cost and timing aggregations to non-negative outputs",
        }
    )
    if negative_signals:
        issues.append(
            {
                "severity": "critical",
                "title": "Negative performance values found in analysis output",
                "evidence": negative_signals[:10],
                "action": "fix aggregation/sign logic before trusting performance metrics",
            }
        )

    legacy_signals = _legacy_artifact_signals(repo, output_dir)
    checks.append(
        {
            "id": "artifact_governance",
            "status": "pass" if not legacy_signals else "warn",
            "details": "single canonical output root" if not legacy_signals else "legacy/canonical artifact drift detected",
            "evidence": legacy_signals[:10],
            "action": "archive/deprecate legacy outputs and keep one canonical active output root",
        }
    )
    if legacy_signals:
        issues.append(
            {
                "severity": "medium",
                "title": "Parallel legacy outputs can confuse consumers",
                "evidence": legacy_signals[:10],
                "action": "enforce canonical output pointer and treat legacy outputs as read-only",
            }
        )

    mission = insights.get("mission_matrix")
    if isinstance(mission, dict):
        for key in ("execution", "performance", "logic", "purpose_fulfillment"):
            section = mission.get(key)
            if not isinstance(section, dict):
                continue
            status = str(section.get("status", "")).lower()
            if status in {"fail", "critical"}:
                issues.append(
                    {
                        "severity": "high",
                        "title": f"Mission matrix failure: {key}",
                        "evidence": section.get("notes", []),
                        "action": f"treat {key} as blocking until status returns to pass",
                    }
                )

    findings_by_severity = insights.get("findings_by_severity")
    if not isinstance(findings_by_severity, dict):
        findings_by_severity = {}
    critical_count = int(findings_by_severity.get("critical") or 0)
    if critical_count > 0:
        issues.append(
            {
                "severity": "high",
                "title": "Critical findings reported by insights compiler",
                "evidence": [f"critical={critical_count}"],
                "action": "address critical findings before publishing trust claims",
            }
        )

    grade = insights.get("grade", "unknown")
    health_score = insights.get("health_score", None)
    top_findings = _extract_top_findings(insights)

    payload = {
        "schema_version": "collider.feedback.auto.v1",
        "ts": _utc_iso(),
        "repo": str(repo),
        "run_mode": run_mode,
        "grade": grade,
        "health_score": health_score,
        "findings_by_severity": findings_by_severity,
        "top_findings": top_findings,
        "collider_output_dir": str(output_dir),
        "counts": {"nodes": node_count, "edges": edge_count},
        "checks": checks,
        "issues": issues,
        "issue_count": len(issues),
        "negative_performance_signals": negative_signals[:10],
        "legacy_artifact_signals": legacy_signals[:10],
    }
    return payload


def _build_audit_prompt(auto_feedback: dict[str, Any]) -> str:
    excerpt = {
        "repo": auto_feedback.get("repo"),
        "grade": auto_feedback.get("grade"),
        "health_score": auto_feedback.get("health_score"),
        "findings_by_severity": auto_feedback.get("findings_by_severity"),
        "counts": auto_feedback.get("counts"),
        "issues": auto_feedback.get("issues", [])[:8],
        "top_findings": auto_feedback.get("top_findings", [])[:8],
        "checks": auto_feedback.get("checks", []),
    }
    return (
        "You are a strict software quality auditor.\n"
        "Write an actionable audit in markdown with sections:\n"
        "1) Critical defects\n"
        "2) Root causes\n"
        "3) First fixes (ordered)\n"
        "4) Noise policy updates\n"
        "5) Confidence\n\n"
        "Rules:\n"
        "- Focus on exact problems, not generic praise.\n"
        "- Use direct language.\n"
        "- Keep it concise.\n\n"
        f"Input data:\n{json.dumps(excerpt, indent=2, ensure_ascii=False)}\n"
    )


def _render_deterministic_audit(auto_feedback: dict[str, Any], reason: str) -> str:
    lines = [
        "# AI User Audit Report",
        "",
        f"- ts: {auto_feedback.get('ts')}",
        f"- repo: {auto_feedback.get('repo')}",
        f"- grade: {auto_feedback.get('grade')}",
        f"- health_score: {auto_feedback.get('health_score')}",
        f"- mode: deterministic_fallback ({reason})",
        "",
        "## Critical Defects",
    ]
    issues = auto_feedback.get("issues", [])
    if isinstance(issues, list) and issues:
        for item in issues[:10]:
            if not isinstance(item, dict):
                continue
            sev = item.get("severity", "unknown")
            title = item.get("title", "untitled_issue")
            lines.append(f"- [{sev}] {title}")
    else:
        lines.append("- No critical defects detected by deterministic checks.")

    lines.extend(
        [
            "",
            "## Root Causes",
            "- Artifact drift, extraction gaps, and invalid metric semantics are the main observed causes.",
            "",
            "## First Fixes",
            "1. Fix any fail-level checks first (required artifacts, negative performance values).",
            "2. Remove/archive parallel legacy outputs and keep one canonical output root.",
            "3. Improve language-specific edge extraction for repositories with node-only output.",
            "",
            "## Noise Policy Updates",
            "- Keep generated paths (`.collider`, `.collider/feedback`, `collider_output`, docs/standard-model artifacts) excluded by default.",
            "- Promote repeated benign warnings into explicit ignore rules only after repeated confirmation.",
            "",
            "## Confidence",
            "- Medium: deterministic checks are reliable for structural/output defects and metric sanity.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _assess_llm_quality(text: str, prompt: str, latency_ms: float, timeout_ms: float) -> dict[str, Any]:
    """Assess LLM response quality with structured signals.

    Returns a quality_signals dict that downstream consumers can use
    to decide how much to trust the LLM-augmented audit.
    """
    has_sections = text.count("#") >= 2  # markdown headers present
    prompt_len = max(len(prompt), 1)
    response_ratio = round(len(text) / prompt_len, 3)
    near_timeout = latency_ms > (timeout_ms * 0.80)
    suspiciously_short = len(text) < 100

    return {
        "has_sections": has_sections,
        "response_ratio": response_ratio,
        "response_chars": len(text),
        "near_timeout": near_timeout,
        "suspiciously_short": suspiciously_short,
    }


def _compute_degradation_level(provider: str, quality_signals: dict[str, Any] | None) -> str:
    """Classify audit reliability into none/partial/full.

    - none:    LLM responded with reasonable quality
    - partial: LLM responded but quality is questionable
    - full:    fell back to deterministic (LLM unavailable/failed/disabled)
    """
    if provider == "deterministic":
        return "full"
    if quality_signals is None:
        return "partial"
    # Partial if any red flag is present
    if (quality_signals.get("near_timeout")
            or quality_signals.get("suspiciously_short")
            or not quality_signals.get("has_sections")):
        return "partial"
    return "none"


def _generate_ai_user_audit(
    auto_feedback: dict[str, Any],
    llm_model: str,
    timeout_sec: int,
    skip_llm: bool,
) -> tuple[str, dict[str, Any]]:
    timeout_ms = timeout_sec * 1000

    if skip_llm:
        reason = "llm_audit_disabled"
        meta = {
            "provider": "deterministic",
            "reason": reason,
            "degradation_level": "full",
            "latency_ms": 0,
            "quality_signals": None,
        }
        return _render_deterministic_audit(auto_feedback, reason), meta

    prompt = _build_audit_prompt(auto_feedback)
    ollama = shutil.which("ollama")
    if not ollama:
        reason = "ollama_not_found"
        meta = {
            "provider": "deterministic",
            "reason": reason,
            "degradation_level": "full",
            "latency_ms": 0,
            "quality_signals": None,
        }
        return _render_deterministic_audit(auto_feedback, reason), meta

    t0 = time.monotonic()
    rc, stdout, stderr = _run_capture([ollama, "run", llm_model, prompt], timeout_sec=timeout_sec)
    latency_ms = round((time.monotonic() - t0) * 1000, 1)

    text = stdout.strip()
    if rc != 0 or not text:
        reason = f"ollama_failed_rc_{rc}"
        if stderr.strip():
            reason = f"{reason}:{stderr.strip()[:140]}"
        meta = {
            "provider": "deterministic",
            "reason": reason,
            "degradation_level": "full",
            "latency_ms": latency_ms,
            "quality_signals": None,
        }
        return _render_deterministic_audit(auto_feedback, reason), meta

    # LLM succeeded -- assess quality
    quality = _assess_llm_quality(text, prompt, latency_ms, timeout_ms)
    degradation = _compute_degradation_level("ollama", quality)
    meta = {
        "provider": "ollama",
        "model": llm_model,
        "reason": "ok",
        "degradation_level": degradation,
        "latency_ms": latency_ms,
        "quality_signals": quality,
    }
    return text + ("\n" if not text.endswith("\n") else ""), meta


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_to_sinks(src: Path, targets: list[Path]) -> list[str]:
    copied: list[str] = []
    for target in targets:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            copied.append(str(target))
        except OSError:
            continue
    return copied


def _sync_feedback_to_research_sinks(
    repo: Path,
    auto_json_path: Path,
    audit_md_path: Path,
    feedback_report_path: Path,
) -> dict[str, list[str]]:
    """Persist all ingested feedback artifacts to one central PROJECT_elements folder."""
    slug = _slug(repo.name)
    stamp = _utc_stamp()
    central_root = _CENTRAL_FEEDBACK_ROOT.resolve()
    copied = {"central": []}

    targets = [
        central_root / f"{slug}_auto_feedback_{stamp}.json",
        central_root / f"{slug}_ai_user_audit_{stamp}.md",
        central_root / f"{slug}_feedback_report_{stamp}.json",
    ]
    copied["central"].extend(_copy_to_sinks(auto_json_path, [targets[0]]))
    copied["central"].extend(_copy_to_sinks(audit_md_path, [targets[1]]))
    copied["central"].extend(_copy_to_sinks(feedback_report_path, [targets[2]]))
    return copied


def _generate_feedback_bundle(
    repo: Path,
    output_dir: Path,
    feedback_dir: Path,
    run_mode: str,
    llm_model: str,
    llm_timeout_sec: int,
    skip_llm: bool,
) -> dict[str, Any]:
    _ensure_local_ignore(repo, feedback_dir)
    auto_feedback = _build_auto_feedback(repo, output_dir, run_mode=run_mode)
    audit_md, llm_meta = _generate_ai_user_audit(
        auto_feedback=auto_feedback,
        llm_model=llm_model,
        timeout_sec=llm_timeout_sec,
        skip_llm=skip_llm,
    )

    # Attach degradation signal to auto_feedback for primary artifact consumers
    auto_feedback["llm_degradation"] = {
        "level": llm_meta.get("degradation_level", "full"),
        "provider": llm_meta.get("provider", "deterministic"),
        "reason": llm_meta.get("reason", "unknown"),
        "latency_ms": llm_meta.get("latency_ms", 0),
    }

    stamp = _utc_stamp()
    auto_json_path = feedback_dir / f"collider_feedback_auto_{stamp}.json"
    latest_auto_json = feedback_dir / "latest_auto_feedback.json"
    audit_md_path = feedback_dir / f"ai-user-audit_{stamp}.md"
    latest_audit_md = feedback_dir / "latest_ai_user_audit.md"
    feedback_report_path = feedback_dir / f"collider_feedback_report_{stamp}.json"
    latest_feedback_report_path = feedback_dir / "collider_feedback_report_latest.json"

    _write_json(auto_json_path, auto_feedback)
    shutil.copy2(auto_json_path, latest_auto_json)

    audit_md_path.parent.mkdir(parents=True, exist_ok=True)
    audit_md_path.write_text(audit_md, encoding="utf-8")
    shutil.copy2(audit_md_path, latest_audit_md)

    # Build top-level degradation summary for quick downstream consumption
    degradation_level = llm_meta.get("degradation_level", "full")
    llm_degradation = {
        "level": degradation_level,
        "provider": llm_meta.get("provider", "deterministic"),
        "reason": llm_meta.get("reason", "unknown"),
        "audit_reliability": "llm_augmented" if degradation_level == "none" else (
            "llm_partial" if degradation_level == "partial" else "deterministic_only"
        ),
        "latency_ms": llm_meta.get("latency_ms", 0),
    }

    feedback_report = {
        "schema_version": "collider.feedback.report.v2",
        "generated_at_utc": _utc_iso(),
        "repo": str(repo),
        "run_mode": run_mode,
        "grade": auto_feedback.get("grade"),
        "health_score": auto_feedback.get("health_score"),
        "issue_count": auto_feedback.get("issue_count", 0),
        "llm_degradation": llm_degradation,
        "llm_meta": llm_meta,
        "canonical_output_root": str(output_dir),
        "feedback_package_root": str(feedback_dir),
        "artifacts": {
            "auto_feedback_json": str(auto_json_path),
            "latest_auto_feedback_json": str(latest_auto_json),
            "ai_user_audit_md": str(audit_md_path),
            "latest_ai_user_audit_md": str(latest_audit_md),
            "feedback_report_json": str(feedback_report_path),
            "latest_feedback_report_json": str(latest_feedback_report_path),
        },
        "checksums": {
            "auto_feedback_json": _sha256(auto_json_path),
            "ai_user_audit_md": _sha256(audit_md_path),
        },
    }
    _write_json(feedback_report_path, feedback_report)
    shutil.copy2(feedback_report_path, latest_feedback_report_path)

    copied = _sync_feedback_to_research_sinks(
        repo=repo,
        auto_json_path=auto_json_path,
        audit_md_path=audit_md_path,
        feedback_report_path=feedback_report_path,
    )

    return {
        "auto_feedback_json": str(auto_json_path),
        "latest_auto_feedback_json": str(latest_auto_json),
        "ai_user_audit_md": str(audit_md_path),
        "latest_ai_user_audit_md": str(latest_audit_md),
        "feedback_report_json": str(feedback_report_path),
        "latest_feedback_report_json": str(latest_feedback_report_path),
        "llm_meta": llm_meta,
        "synced": copied,
    }


def _write_manual_feedback(
    repo: Path,
    feedback_dir: Path,
    author: str,
    problem: str,
    evidence: str,
    expected: str,
    proposed_fix: str,
) -> dict[str, str]:
    _ensure_local_ignore(repo, feedback_dir)
    payload = {
        "schema_version": "collider.feedback.manual.v1",
        "ts": _utc_iso(),
        "author": author,
        "repo": str(repo),
        "problem": problem,
        "evidence": evidence,
        "expected": expected,
        "proposed_fix": proposed_fix,
    }
    stamp = _utc_stamp()
    manual_path = feedback_dir / f"manual_feedback_{stamp}.json"
    latest_manual = feedback_dir / "latest_manual_feedback.json"
    _write_json(manual_path, payload)
    shutil.copy2(manual_path, latest_manual)

    slug = _slug(repo.name)
    central_root = _CENTRAL_FEEDBACK_ROOT.resolve()
    targets = [central_root / f"{slug}_manual_feedback_{stamp}.json"]
    _copy_to_sinks(manual_path, targets)
    return {"manual_feedback_json": str(manual_path), "latest_manual_feedback_json": str(latest_manual)}


def _run_feedback_pipeline(args: argparse.Namespace, repo: Path, output_dir: Path, run_mode: str) -> int:
    if args.no_feedback:
        print("  feedback: skipped (--no-feedback)")
        return 0

    feedback_dir = _resolve_feedback_dir(
        repo=repo,
        output_dir=output_dir,
        feedback_dir=getattr(args, "feedback_dir", None),
        legacy_reh_dir=getattr(args, "legacy_reh_dir", None),
    )
    result = _generate_feedback_bundle(
        repo=repo,
        output_dir=output_dir,
        feedback_dir=feedback_dir,
        run_mode=run_mode,
        llm_model=args.llm_audit_model,
        llm_timeout_sec=args.llm_timeout_sec,
        skip_llm=args.no_llm_audit,
    )
    print("  feedback bundle:")
    print(f"   - auto: {result['latest_auto_feedback_json']}")
    print(f"   - audit: {result['latest_ai_user_audit_md']}")
    print(f"   - report: {result['latest_feedback_report_json']}")
    llm_meta = result.get("llm_meta", {})
    provider = llm_meta.get("provider", "unknown")
    reason = llm_meta.get("reason", "")
    print(f"   - llm: provider={provider} reason={reason}")
    return 0


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

    rc = _run(cmd)
    if rc != 0:
        return rc
    return _run_feedback_pipeline(args, repo=repo, output_dir=output_dir, run_mode="full")


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
    print("  step 1/4: full run")
    rc = _run(full_cmd)
    if rc != 0:
        return rc

    print("  step 2/4: artifact validation")
    ok, missing = _validate_artifacts(output_dir)
    if not ok:
        print("  missing artifacts:")
        for m in missing:
            print(f"   - {m}")
        return 2

    print("  step 3/4: summary")
    insights = _read_insights(output_dir)
    if insights:
        sev = insights.get("findings_by_severity", {})
        print("  findings_by_severity:", sev)
    if args.with_grade:
        print("  step 4/5: grade")
        grade_cmd = [collider_bin, "grade", str(repo), "--json"]
        rc = _run(grade_cmd)
        if rc != 0:
            return rc
    else:
        print("  step 4/4: grade skipped")

    return _run_feedback_pipeline(args, repo=repo, output_dir=output_dir, run_mode="smoke")


def cmd_feedback(args: argparse.Namespace) -> int:
    repo = _repo_root(Path(args.repo))
    output_dir = _resolve_output_dir(repo, args.output_dir)
    _ensure_local_ignore(repo, output_dir)
    print("Collider Hub Feedback")
    print(f"  repo: {repo}")
    print(f"  output: {output_dir}")
    return _run_feedback_pipeline(args, repo=repo, output_dir=output_dir, run_mode="feedback-only")


def cmd_manual_feedback(args: argparse.Namespace) -> int:
    repo = _repo_root(Path(args.repo))
    output_dir = _resolve_output_dir(repo, None)
    feedback_dir = _resolve_feedback_dir(
        repo=repo,
        output_dir=output_dir,
        feedback_dir=getattr(args, "feedback_dir", None),
        legacy_reh_dir=getattr(args, "legacy_reh_dir", None),
    )
    result = _write_manual_feedback(
        repo=repo,
        feedback_dir=feedback_dir,
        author=args.author,
        problem=args.problem,
        evidence=args.evidence,
        expected=args.expected,
        proposed_fix=args.proposed_fix,
    )
    print("Collider Hub Manual Feedback")
    print(f"  repo: {repo}")
    print(f"  manual: {result['latest_manual_feedback_json']}")
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


def cmd_audit_doc(args: argparse.Namespace) -> int:
    """Thin wrapper: delegate to wave/tools/ai/adversarial_auditor.py."""
    auditor = _ELEMENTS_ROOT / "wave" / "tools" / "ai" / "adversarial_auditor.py"
    if not auditor.exists():
        print(f"adversarial_auditor.py not found at {auditor}")
        return 1

    cmd: list[str] = [
        sys.executable, str(auditor), "audit", args.document,
        "--domain", args.domain,
    ]
    if args.layers:
        for layer in args.layers:
            cmd.extend(["--layer", str(layer)])
    if args.dry_run:
        cmd.append("--dry-run")

    print("Collider Hub Audit-Doc")
    print(f"  delegating to: {auditor.name}")
    return _run(cmd)


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
            "--feedback-dir",
            default=None,
            help="Feedback directory (default: <repo>/.collider/feedback)",
        )
        sp.add_argument(
            "--reh-dir",
            dest="legacy_reh_dir",
            default=None,
            help=argparse.SUPPRESS,
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
        sp.add_argument(
            "--no-feedback",
            action="store_true",
            help="Disable automatic feedback package generation",
        )
        sp.add_argument(
            "--no-llm-audit",
            action="store_true",
            help="Use deterministic audit report only (skip LLM attempt)",
        )
        sp.add_argument(
            "--llm-audit-model",
            default=os.environ.get("COLLIDER_AUDIT_MODEL", "qwen2.5:7b-instruct"),
            help="Model for ai-user-audit via ollama",
        )
        sp.add_argument(
            "--llm-timeout-sec",
            type=int,
            default=90,
            help="Timeout for ai-user-audit model call",
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

    feedback = sub.add_parser(
        "feedback",
        help="Generate Collider feedback package from existing Collider artifacts",
    )
    add_common(feedback)
    feedback.set_defaults(func=cmd_feedback)

    manual = sub.add_parser(
        "manual-feedback",
        help="Write manual feedback and ingest into Collider research sinks",
    )
    manual.add_argument("--repo", default=".", help="Target repository path")
    manual.add_argument("--feedback-dir", default=None, help="Feedback directory (default: <repo>/.collider/feedback)")
    manual.add_argument("--reh-dir", dest="legacy_reh_dir", default=None, help=argparse.SUPPRESS)
    manual.add_argument("--author", default=os.environ.get("USER", "unknown"), help="Feedback author")
    manual.add_argument("--problem", required=True, help="Problem statement")
    manual.add_argument("--evidence", required=True, help="Concrete evidence")
    manual.add_argument("--expected", default="", help="Expected behavior")
    manual.add_argument("--proposed-fix", default="", help="Proposed fix")
    manual.set_defaults(func=cmd_manual_feedback)

    mcp = sub.add_parser(
        "mcp-check",
        help="Verify MCP collider service with explicit db_dir",
    )
    add_common(mcp)
    mcp.set_defaults(func=cmd_mcp_check)

    audit_doc = sub.add_parser(
        "audit-doc",
        help="Run three-layer adversarial audit on a document",
    )
    audit_doc.add_argument("document", help="Path to document (md, txt)")
    audit_doc.add_argument(
        "--domain", "-d", default="general",
        help="Domain profile: smoc, general (default: general)",
    )
    audit_doc.add_argument(
        "--layer", "-l", type=int, action="append", dest="layers",
        choices=[1, 2, 3],
        help="Run specific layer(s) only (repeatable)",
    )
    audit_doc.add_argument("--dry-run", action="store_true", help="No API calls")
    audit_doc.set_defaults(func=cmd_audit_doc)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
