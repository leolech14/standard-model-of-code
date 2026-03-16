#!/usr/bin/env python3
"""
Ideome Scorer — Component Alignment Measurement Engine

Scores ecosystem components against IDEOME.yaml principles.
Pure YAML + filesystem checks. No LLM, no API keys, no heavy imports.

Usage:
    python ideome_scorer.py --component CMP-052
    python ideome_scorer.py --component CMP-052 --auto
    python ideome_scorer.py --all --auto
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# --- Paths ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
ECOROOT = PROJECT_ROOT.parent / ".ecoroot"
ATLAS_PATH = PROJECT_ROOT / "atlas" / "ATLAS.yaml"
IDEOME_PATH = ECOROOT / "IDEOME.yaml"
TOOLS_REGISTRY_PATH = ECOROOT / "TOOLS_REGISTRY.yaml"
PROGRESSIVE_REQ_PATH = PROJECT_ROOT / "atlas" / "schemas" / "PROGRESSIVE_REQUIREMENTS.yaml"
ALIGNMENT_DIR = ECOROOT / "alignment"


def _d6_header() -> Dict[str, Any]:
    sha = "unknown"
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_ROOT), stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        pass
    return {
        "source": "ideome",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": sha,
    }


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def find_component_in_atlas(atlas: dict, component_id: str) -> Optional[dict]:
    """Find a component entry in ATLAS.yaml by CMP-xxx ID."""
    for item in atlas.get("components", []):
        if item.get("id") == component_id:
            return item
    return None


def find_component_in_registry(registry: dict, component_name: str) -> Optional[dict]:
    """Find a component in TOOLS_REGISTRY.yaml by name or ECO-ID."""
    # Registry is a flat dict of tool entries
    for key, entry in registry.items():
        if isinstance(entry, dict):
            if entry.get("id", "").startswith("ECO-") or entry.get("name", "") == component_name:
                if component_name in (entry.get("name", ""), key):
                    return entry
    return None


# ============================================================================
# PRINCIPLE CHECKS
# ============================================================================

def check_A1_d6_header(component: dict, **kw) -> float:
    """Check if component produces D6 _generated header."""
    outputs = component.get("outputs", [])
    for out in outputs:
        if isinstance(out, dict) and "json" in out.get("type", "").lower():
            return 1.0
    # Check if source code has _generated or d6_header
    source = component.get("invoke", {}).get("method", "")
    if "_generated" in str(component) or "d6_header" in str(component):
        return 1.0
    return 0.0


def check_A2_three_tier(component: dict, **kw) -> float:
    """Check for three-tier output pattern."""
    outputs = component.get("outputs", [])
    types = set()
    for out in outputs:
        if isinstance(out, dict):
            t = out.get("type", "").lower()
            if "json" in t:
                types.add("tier1")
            if "md" in t or "markdown" in t:
                types.add("tier3")
            if "html" in t:
                types.add("tier3")
            if "briefing" in out.get("name", "").lower():
                types.add("tier2")
            if "jsonl" in t:
                types.add("tracking")
    score = len(types.intersection({"tier1", "tier2", "tier3"})) / 3.0
    return round(score, 2)


def check_A3_longitudinal(component: dict, **kw) -> float:
    """Check for longitudinal tracking (run_index.jsonl or equivalent)."""
    outputs = component.get("outputs", [])
    for out in outputs:
        if isinstance(out, dict):
            name = out.get("name", "").lower()
            typ = out.get("type", "").lower()
            if "index" in name or "jsonl" in typ or "tracking" in name:
                return 1.0
    return 0.0


def check_A4_meta_envelope(component: dict, **kw) -> float:
    """Check for meta envelope with provenance fields."""
    # If component has D6 header AND outputs JSON, likely has envelope
    has_d6 = check_A1_d6_header(component) > 0
    has_json_output = any(
        "json" in (out.get("type", "") if isinstance(out, dict) else "").lower()
        for out in component.get("outputs", [])
    )
    return 1.0 if (has_d6 and has_json_output) else 0.0


def check_A5_cost_awareness(component: dict, **kw) -> float:
    """Check for cost/token tracking."""
    metrics = component.get("metrics", {})
    if metrics.get("cost_metric"):
        return 1.0
    return 0.0


def check_B1_deterministic_fallback(component: dict, **kw) -> float:
    """Heuristic: does the component mention fallback/deterministic in its description?"""
    desc = str(component.get("agent", {}).get("explanation", ""))
    desc += str(component.get("description", ""))
    keywords = ["deterministic", "fallback", "offline", "without llm", "no api", "pure git"]
    matches = sum(1 for k in keywords if k in desc.lower())
    return min(1.0, matches / 2.0)


def check_B2_degradation_signal(component: dict, **kw) -> float:
    """Check for LLM degradation signal in output schema."""
    full_text = json.dumps(component, default=str).lower()
    if "degradation" in full_text or "llm_failed" in full_text:
        return 1.0
    return 0.0


def check_B3_auto_feedback(component: dict, **kw) -> float:
    """Check for self-evaluation / auto-feedback."""
    outputs = component.get("outputs", [])
    for out in outputs:
        if isinstance(out, dict):
            name = out.get("name", "").lower()
            if "feedback" in name or "quality" in name or "audit" in name:
                return 1.0
    desc = str(component.get("agent", {}).get("explanation", "")).lower()
    if "self-evaluation" in desc or "auto-feedback" in desc or "quality check" in desc:
        return 1.0
    return 0.0


def check_B4_observable_failure(component: dict, **kw) -> float:
    """Heuristic: does the component mention error handling/logging?"""
    desc = str(component.get("agent", {}).get("explanation", ""))
    if "error" in desc.lower() or "logging" in desc.lower() or "observable" in desc.lower():
        return 1.0
    return 0.5  # Assume partial by default


def check_B5_config_ssot(component: dict, **kw) -> float:
    """Manual check placeholder. In --auto mode, return 0.5 (unknown)."""
    return 0.5  # Requires manual assessment


def check_C1_atlas_registered(component: dict, **kw) -> float:
    """Check Atlas registration at P2+."""
    stage = component.get("stage", "P0")
    stage_num = int(stage[1]) if len(stage) == 2 and stage[1].isdigit() else 0
    return 1.0 if stage_num >= 2 else 0.0


def check_C2_registry_entry(component: dict, atlas: dict = None, **kw) -> float:
    """Check TOOLS_REGISTRY for ECO-xxx entry."""
    registry = load_yaml(TOOLS_REGISTRY_PATH)
    name = component.get("name", "")
    for key, entry in registry.items():
        if isinstance(entry, dict) and entry.get("id", "").startswith("ECO-"):
            if name in (entry.get("name", ""), key):
                return 1.0
    return 0.0


def check_C3_progressive_compliance(component: dict, **kw) -> float:
    """Check Progressive Requirements compliance for declared stage."""
    stage = component.get("stage", "P0")
    stage_num = int(stage[1]) if len(stage) == 2 and stage[1].isdigit() else 0

    # Basic checks per stage
    checks = []
    if stage_num >= 0:
        checks.extend([bool(component.get("id")), bool(component.get("name")),
                       bool(component.get("purpose")), bool(component.get("owner"))])
    if stage_num >= 1:
        checks.append(bool(component.get("tags")))
    if stage_num >= 2:
        agent = component.get("agent", {})
        checks.extend([bool(agent.get("explanation")), bool(agent.get("context_priority")),
                       bool(component.get("version"))])
    if stage_num >= 3:
        checks.extend([bool(component.get("metrics", {}).get("cost_metric")),
                       bool(component.get("invoke", {}).get("prerequisites"))])

    if not checks:
        return 1.0
    return round(sum(1 for c in checks if c) / len(checks), 2)


def check_C4_feeds_documented(component: dict, **kw) -> float:
    """Check feeds_into and fed_by are populated."""
    has_into = bool(component.get("feeds_into"))
    has_by = bool(component.get("fed_by"))
    if has_into and has_by:
        return 1.0
    elif has_into or has_by:
        return 0.5
    return 0.0


def check_C5_affordances(component: dict, **kw) -> float:
    """Check agent.affordances with can_read/can_write/cannot."""
    affordances = component.get("agent", {}).get("affordances", {})
    fields = ["can_read", "can_write", "cannot"]
    present = sum(1 for f in fields if f in affordances)
    return round(present / 3.0, 2)


# ============================================================================
# SCORING ENGINE
# ============================================================================

CHECKS = {
    "A1": check_A1_d6_header,
    "A2": check_A2_three_tier,
    "A3": check_A3_longitudinal,
    "A4": check_A4_meta_envelope,
    "A5": check_A5_cost_awareness,
    "B1": check_B1_deterministic_fallback,
    "B2": check_B2_degradation_signal,
    "B3": check_B3_auto_feedback,
    "B4": check_B4_observable_failure,
    "B5": check_B5_config_ssot,
    "C1": check_C1_atlas_registered,
    "C2": check_C2_registry_entry,
    "C3": check_C3_progressive_compliance,
    "C4": check_C4_feeds_documented,
    "C5": check_C5_affordances,
}

DOMAIN_WEIGHTS = {
    "output_contract": 0.40,
    "operational_resilience": 0.35,
    "ecosystem_integration": 0.25,
}

DOMAIN_PRINCIPLES = {
    "output_contract": ["A1", "A2", "A3", "A4", "A5"],
    "operational_resilience": ["B1", "B2", "B3", "B4", "B5"],
    "ecosystem_integration": ["C1", "C2", "C3", "C4", "C5"],
}

GRADE_BOUNDARIES = {"A": 0.85, "B": 0.70, "C": 0.55, "D": 0.40}


def compute_grade(score: float) -> str:
    for grade, threshold in GRADE_BOUNDARIES.items():
        if score >= threshold:
            return grade
    return "F"


def score_component(component: dict) -> dict:
    """Score a single component against all ideome principles."""
    principle_scores = {}
    for pid, check_fn in CHECKS.items():
        principle_scores[pid] = check_fn(component)

    domain_scores = {}
    for domain, principles in DOMAIN_PRINCIPLES.items():
        scores = [principle_scores[p] for p in principles]
        domain_scores[domain] = {
            "score": round(sum(scores) / len(scores), 2),
            "principles": {p: principle_scores[p] for p in principles},
        }

    alignment = sum(
        DOMAIN_WEIGHTS[d] * domain_scores[d]["score"]
        for d in DOMAIN_WEIGHTS
    )
    alignment = round(alignment, 2)

    # Recommendations (principles scoring 0)
    recommendations = []
    ideome = load_yaml(IDEOME_PATH)
    for domain_key, domain_def in ideome.get("domains", {}).items():
        for pid, pdef in domain_def.get("principles", {}).items():
            if principle_scores.get(pid, 0) == 0:
                recommendations.append(f"Add {pdef.get('name', pid)} ({pid})")

    return {
        "_generated": _d6_header(),
        "component_id": component.get("id", "unknown"),
        "component_name": component.get("name", "unknown"),
        "display_name": component.get("display_name", ""),
        "stage": component.get("stage", "P0"),
        "alignment_score": alignment,
        "grade": compute_grade(alignment),
        "domains": domain_scores,
        "recommendations": recommendations[:5],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def generate_markdown(report: dict) -> str:
    """Generate Tier 3 markdown report from scoring result."""
    md = f"# Alignment Report: {report['display_name'] or report['component_name']}\n\n"
    md += f"**Component:** {report['component_id']} | **Stage:** {report['stage']}\n"
    md += f"**Alignment:** {report['alignment_score']} ({report['grade']})\n"
    md += f"**Scored:** {report['timestamp'][:10]}\n\n"

    for domain, data in report["domains"].items():
        md += f"## {domain.replace('_', ' ').title()} ({data['score']:.0%})\n\n"
        for pid, score in data["principles"].items():
            icon = "pass" if score >= 0.8 else ("partial" if score > 0 else "FAIL")
            md += f"- [{icon}] {pid}: {score}\n"
        md += "\n"

    if report["recommendations"]:
        md += "## Recommendations\n\n"
        for r in report["recommendations"]:
            md += f"- {r}\n"

    return md


def append_to_index(report: dict) -> None:
    """Append compact record to alignment_index.jsonl."""
    ALIGNMENT_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "component_id": report["component_id"],
        "alignment_score": report["alignment_score"],
        "grade": report["grade"],
        "timestamp": report["timestamp"],
    }
    with open(ALIGNMENT_DIR / "alignment_index.jsonl", "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def save_report(report: dict) -> None:
    """Save Tier 1 (JSON) and Tier 3 (markdown) reports."""
    ALIGNMENT_DIR.mkdir(parents=True, exist_ok=True)
    cid = report["component_id"]

    # Tier 1
    json_path = ALIGNMENT_DIR / f"{cid}.json"
    json_path.write_text(json.dumps(report, indent=2, default=str))

    # Tier 3
    md_path = ALIGNMENT_DIR / f"{cid}.md"
    md_path.write_text(generate_markdown(report))

    # Index
    append_to_index(report)

    print(f"  Tier 1: {json_path}")
    print(f"  Tier 3: {md_path}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Ideome Scorer — Component Alignment Engine")
    parser.add_argument("--component", help="Component ID (CMP-xxx) to score")
    parser.add_argument("--all", action="store_true", help="Score all P2+ components")
    parser.add_argument("--auto", action="store_true", help="Skip manual checks (deterministic only)")
    args = parser.parse_args()

    atlas = load_yaml(ATLAS_PATH)

    if args.component:
        component = find_component_in_atlas(atlas, args.component)
        if not component:
            print(f"Component {args.component} not found in ATLAS.yaml")
            sys.exit(1)

        print(f"\nScoring {args.component} ({component.get('display_name', component.get('name'))})...")
        report = score_component(component)
        save_report(report)
        print(f"\n  Alignment: {report['alignment_score']} ({report['grade']})")
        print(f"  Output Contract: {report['domains']['output_contract']['score']:.0%}")
        print(f"  Operational Resilience: {report['domains']['operational_resilience']['score']:.0%}")
        print(f"  Ecosystem Integration: {report['domains']['ecosystem_integration']['score']:.0%}")
        if report["recommendations"]:
            print(f"\n  Top recommendations:")
            for r in report["recommendations"][:3]:
                print(f"    - {r}")

    elif args.all:
        components = [
            c for c in atlas.get("components", [])
            if c.get("stage", "P0") >= "P2"
        ]
        print(f"\nScoring {len(components)} P2+ components...\n")
        results = []
        for comp in components:
            report = score_component(comp)
            save_report(report)
            results.append(report)
            print(f"  {report['component_id']:10s} {report['display_name'] or report['component_name']:40s} {report['grade']}  ({report['alignment_score']})")

        print(f"\n  Total: {len(results)} components scored")
        avg = sum(r["alignment_score"] for r in results) / len(results) if results else 0
        print(f"  Average alignment: {avg:.2f} ({compute_grade(avg)})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
