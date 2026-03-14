#!/usr/bin/env python3
"""Collider Scorecard -- canonical quick-look at Collider health.

Usage:
    python3 collider_scorecard.py [--collider-dir DIR] [--json] [--history N]

Reads Zone 3 artifacts (.collider/) and system_status.json to produce a
compact health dashboard.

Schema aligns with meta_envelope.py (repo_id, run_id, schema_version)
so scorecard JSON records can be aggregated:
  - Longitudinally: same repo over time via meta_index.jsonl
  - Horizontally:   across repos via repo_id joins
  - In parallel:    each record is self-contained, no shared state

No API calls, no side effects.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]  # particle/
PROJECT_ROOT = REPO_ROOT.parent                   # PROJECT_elements/
DEFAULT_COLLIDER_DIR = PROJECT_ROOT / ".collider"
SYSTEM_STATUS = REPO_ROOT / "data" / "system_status.json"
FEEDBACK_DIR = PROJECT_ROOT / "collider_feedback"

SCORECARD_SCHEMA_VERSION = "1.0.0"
W = 48  # inner width between box borders


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _coerce_severity(val: Any) -> int:
    """Normalize severity count: could be int or list of finding dicts."""
    if isinstance(val, list):
        return len(val)
    if isinstance(val, int):
        return val
    return 0


def bar(val: float, width: int = 10) -> str:
    filled = int(round(val / 10 * width))
    return "\u2588" * filled + "\u2591" * (width - filled)


def age_str(ts: str) -> str:
    """Human-readable age from ISO timestamp."""
    try:
        then = datetime.fromisoformat(ts)
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - then
        days = delta.days
        if days == 0:
            hours = delta.seconds // 3600
            return f"{hours}h ago" if hours else "just now"
        return f"{days}d ago"
    except (ValueError, TypeError):
        return "unknown"


def _get_test_count() -> int | None:
    """Quick pytest --collect-only count. Returns None if unavailable."""
    venv_python = REPO_ROOT / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        return None
    try:
        r = subprocess.run(
            [str(venv_python), "-m", "pytest", "tests/", "-q", "--collect-only"],
            capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
        )
        for line in r.stdout.splitlines():
            if "test" in line and ("selected" in line or "collected" in line):
                parts = line.split()
                if parts and parts[0].isdigit():
                    return int(parts[0])
    except (subprocess.TimeoutExpired, OSError):
        pass
    return None


def row(text: str) -> str:
    """Pad text to fixed width inside box borders."""
    return f"\u2551 {text:<{W}} \u2551"


def sep() -> str:
    return "\u2560" + "\u2550" * (W + 2) + "\u2563"


# ---------------------------------------------------------------------------
# Canonical scorecard record (JSON schema)
# ---------------------------------------------------------------------------
def build_scorecard_record(collider_dir: Path) -> dict | None:
    """Build a self-contained scorecard record aligned with meta_envelope.

    The record is designed for:
      - Parallel aggregation: each record has repo_id + run_id, no shared state
      - Longitudinal tracking: append to JSONL, query by repo_id + run_ts
      - Cross-repo comparison: join on shared field names
    """
    insights = load_json(collider_dir / "collider_insights.json")
    pipeline = load_json(collider_dir / "pipeline_report.json")
    status = load_json(SYSTEM_STATUS)

    if not insights:
        return None

    meta = insights.get("meta", {})
    mm = insights.get("mission_matrix", {})
    fbs = insights.get("findings_by_severity", {})
    hc = insights.get("health_components", {})
    p_meta = pipeline.get("meta", {}) if pipeline else {}
    p_summary = pipeline.get("summary", {}) if pipeline else {}

    # Pull envelope fields from pipeline meta (written by meta_envelope.py)
    # or synthesize them if meta_index.jsonl wasn't populated
    record: dict[str, Any] = {
        # --- Identity (meta_envelope compatible) ---
        "schema_version": SCORECARD_SCHEMA_VERSION,
        "repo_id": p_meta.get("repo_id", _hash_path(p_meta.get("target", ""))),
        "target": p_meta.get("target", "unknown"),
        "run_ts": p_meta.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "collider_version": p_meta.get("collider_version", meta.get("compiler_version", "?")),

        # --- Health ---
        "grade": insights.get("grade"),
        "health_score": insights.get("health_score"),
        "health_components": {k: round(float(v), 2) for k, v in hc.items()},

        # --- Mission Matrix ---
        "mission_matrix": {
            "overall": mm.get("overall"),
            "target": mm.get("target"),
            "all_targets_met": mm.get("all_targets_met"),
            "execution": _extract_mm_score(mm.get("execution")),
            "performance": _extract_mm_score(mm.get("performance")),
            "logic": _extract_mm_score(mm.get("logic")),
            "purpose_fulfillment": _extract_mm_score(mm.get("purpose_fulfillment")),
        },

        # --- Findings ---
        "findings": {
            "total": insights.get("findings_count", 0),
            "critical": _coerce_severity(fbs.get("critical", 0)),
            "high": _coerce_severity(fbs.get("high", 0)),
            "medium": _coerce_severity(fbs.get("medium", 0)),
            "low": _coerce_severity(fbs.get("low", 0)),
            "info": _coerce_severity(fbs.get("info", 0)),
        },

        # --- Scale ---
        "scale": {
            "nodes": meta.get("nodes_analyzed", 0),
            "edges": meta.get("edges_analyzed", 0),
        },

        # --- Pipeline ---
        "pipeline": {
            "stages": p_summary.get("total_stages"),
            "ok": p_summary.get("ok_count"),
            "fail": p_summary.get("fail_count"),
            "warn": p_summary.get("warn_count"),
            "success_rate": p_summary.get("success_rate"),
            "total_time_s": p_meta.get("total_time_s"),
            "peak_memory_mb": round(p_summary.get("peak_memory_kb", 0) / 1024, 1) or None,
            "slowest_stage": _extract_slowest(p_summary.get("slowest_stage")),
        } if pipeline else None,

        # --- Taxonomy (static reference data) ---
        "taxonomy": {
            "atoms": status.get("canonical", {}).get("atoms"),
            "roles": status.get("canonical", {}).get("roles"),
            "patterns": status.get("learnable", {}).get("total"),
            "accuracy": status.get("accuracy"),
        } if status else None,

        # --- Tests (dynamic, optional) ---
        "tests": {
            "particle_collected": _get_test_count(),
        },
    }

    return record


def _hash_path(path_str: str) -> str:
    """Fallback repo_id from target path."""
    import hashlib
    return hashlib.sha256(path_str.encode()).hexdigest()[:12] if path_str else "unknown"


def _extract_mm_score(entry: Any) -> dict | None:
    """Normalize mission matrix entry to {score, status}."""
    if isinstance(entry, dict):
        return {"score": entry.get("score"), "status": entry.get("status")}
    return None


def _extract_slowest(entry: Any) -> str | None:
    if isinstance(entry, dict):
        return entry.get("name")
    if isinstance(entry, str):
        return entry
    return None


# ---------------------------------------------------------------------------
# History (longitudinal)
# ---------------------------------------------------------------------------
def load_history(n: int = 10) -> list[dict]:
    """Load recent run_index.jsonl entries for longitudinal view."""
    index_path = FEEDBACK_DIR / "run_index.jsonl"
    if not index_path.exists():
        return []
    entries = []
    for line in index_path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    # Sort by timestamp descending, return last N
    entries.sort(key=lambda x: x.get("ts", ""), reverse=True)
    return entries[:n]


# ---------------------------------------------------------------------------
# Text rendering
# ---------------------------------------------------------------------------
def render_text(collider_dir: Path, history_count: int = 0) -> str:
    rec = build_scorecard_record(collider_dir)
    if not rec:
        return "No collider_insights.json found.  Run: ./collider full . --output .collider"

    lines: list[str] = []

    # --- Header ---
    lines.append("\u2554" + "\u2550" * (W + 2) + "\u2557")
    lines.append(row(f"COLLIDER SCORECARD              v{rec['collider_version']}"))
    lines.append(sep())
    lines.append(row(f"Grade: {rec['grade']}   Score: {rec['health_score']}/10   {bar(rec['health_score'])}"))
    lines.append(row(f"Nodes: {rec['scale']['nodes']:,}   Edges: {rec['scale']['edges']:,}"))
    lines.append(row(f"Last run: {age_str(rec['run_ts'])}"))
    lines.append(sep())

    # --- Health Components ---
    lines.append(row("HEALTH COMPONENTS"))
    for name, val in rec["health_components"].items():
        flag = " !" if val < 4 else ""
        lines.append(row(f"  {name:20s} {bar(val)} {val:>5.1f}{flag}"))
    lines.append(sep())

    # --- Mission Matrix ---
    mm = rec["mission_matrix"]
    lines.append(row(f"MISSION MATRIX   overall: {mm['overall']}  target: {mm['target']}"))
    for k in ["execution", "performance", "logic", "purpose_fulfillment"]:
        entry = mm.get(k)
        if entry:
            lines.append(row(f"  {k:22s} {entry['score']:>5}  [{entry['status']}]"))
    met_str = "ALL MET" if mm["all_targets_met"] else "NOT MET"
    lines.append(row(f"  targets: {met_str}"))
    lines.append(sep())

    # --- Findings ---
    f = rec["findings"]
    lines.append(row(f"FINDINGS ({f['total']} total)"))
    lines.append(row(f"  critical: {f['critical']}   high: {f['high']}   medium: {f['medium']}"))
    lines.append(row(f"  low: {f['low']}   info: {f['info']}"))
    lines.append(sep())

    # --- Pipeline ---
    p = rec.get("pipeline")
    if p and p.get("stages"):
        lines.append(row(f"PIPELINE ({p['stages']} stages)"))
        lines.append(row(f"  OK: {p['ok']}  Fail: {p['fail']}  Warn: {p['warn']}  Rate: {p['success_rate']:.0%}"))
        lines.append(row(f"  Time: {p['total_time_s']:.0f}s   Peak mem: {p['peak_memory_mb']:.0f}MB"))
        if p.get("slowest_stage"):
            lines.append(row(f"  Slowest: {p['slowest_stage'][:36]}"))
        lines.append(sep())

    # --- Taxonomy ---
    t = rec.get("taxonomy")
    if t:
        lines.append(row("TAXONOMY"))
        lines.append(row(f"  Atoms: {t['atoms']}  Roles: {t['roles']}  Patterns: {t['patterns']}"))
        lines.append(row(f"  Accuracy: {t['accuracy']}%"))
        lines.append(sep())

    # --- Tests ---
    tc = rec.get("tests", {}).get("particle_collected")
    if tc is not None:
        lines.append(row("TESTS"))
        lines.append(row(f"  Particle: {tc} collected"))
        lines.append(sep())

    # --- History (longitudinal) ---
    if history_count > 0:
        history = load_history(history_count)
        if history:
            lines.append(row("RECENT RUNS (longitudinal)"))
            lines.append(row(f"  {'date':12s} {'repo':20s} {'grade':5s} {'score':>5s}"))
            lines.append(row(f"  {'----':12s} {'----':20s} {'-----':5s} {'-----':>5s}"))
            for h in history:
                ts = h.get("ts", "")[:10]
                repo = h.get("repo", "?")[:20]
                grade = str(h.get("grade", "?"))
                score = h.get("health_score")
                score_s = f"{score:.1f}" if score is not None else "?"
                lines.append(row(f"  {ts:12s} {repo:20s} {grade:5s} {score_s:>5s}"))
            lines.append(sep())

    # Close box (replace last sep with bottom border)
    if lines and lines[-1] == sep():
        lines[-1] = "\u255a" + "\u2550" * (W + 2) + "\u255d"
    else:
        lines.append("\u255a" + "\u2550" * (W + 2) + "\u255d")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON rendering
# ---------------------------------------------------------------------------
def render_json(collider_dir: Path, history_count: int = 0) -> str:
    rec = build_scorecard_record(collider_dir)
    if not rec:
        return json.dumps({"error": "no collider_insights.json"})

    if history_count > 0:
        rec["history"] = load_history(history_count)

    return json.dumps(rec, indent=2, default=str)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Collider Scorecard")
    parser.add_argument("--collider-dir", type=Path, default=DEFAULT_COLLIDER_DIR,
                        help="Path to .collider/ directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--history", type=int, default=0, metavar="N",
                        help="Include N most recent runs from run_index.jsonl")
    args = parser.parse_args()

    if args.json:
        print(render_json(args.collider_dir, args.history))
    else:
        print(render_text(args.collider_dir, args.history))


if __name__ == "__main__":
    main()
