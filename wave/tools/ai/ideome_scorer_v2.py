#!/usr/bin/env python3
"""
Ideome Scorer v2 — Component Alignment Engine (Layer 2)

Reads Collider's unified_analysis.json (with Stage 25 principle_evidence)
and ATLAS.yaml to score components against IDEOME.yaml principles.

Usage:
    python ideome_scorer_v2.py --component CMP-052
    python ideome_scorer_v2.py --all
    python ideome_scorer_v2.py --compare-v0  # Show v0 vs v2 scores
"""

import argparse
import json
import subprocess
import sys
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
COLLIDER_OUTPUT = PROJECT_ROOT / ".collider" / "unified_analysis.json"
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
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": sha,
    }


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_collider_output() -> dict:
    """Load unified_analysis.json from last Collider run."""
    if not COLLIDER_OUTPUT.exists():
        print(f"Warning: No Collider output at {COLLIDER_OUTPUT}")
        print("Run: collider-hub full --repo . to generate it")
        return {}
    with open(COLLIDER_OUTPUT) as f:
        return json.load(f)


def find_component(atlas: dict, component_id: str) -> Optional[dict]:
    for item in atlas.get("components", []):
        if item.get("id") == component_id:
            return item
    return None


def get_component_source_path(component: dict) -> Optional[str]:
    """Extract source file path from Atlas invoke.method."""
    invoke = component.get("invoke", {})
    method = invoke.get("method", "")
    # Extract Python file path from invocation string
    for token in method.split():
        if token.endswith(".py") or ".py " in token:
            clean = token.strip("\"'")
            if clean.endswith(".py"):
                return clean
    return None


def get_node_evidence(collider: dict, source_path: str) -> Dict[str, dict]:
    """Get principle evidence for nodes matching a source path."""
    evidence = collider.get("principle_evidence", {})
    matching = {}
    for node_id, ev in evidence.items():
        if source_path in ev.get("file_path", ""):
            matching[node_id] = ev
    return matching


def aggregate_evidence(node_evidence: Dict[str, dict], principle_key: str) -> tuple:
    """Aggregate per-node evidence for a principle across all component nodes.

    Returns (score, best_evidence_dict).
    """
    best_score = 0.0
    best_ev = {}
    for node_id, ev in node_evidence.items():
        p_ev = ev.get(principle_key, {})
        if p_ev.get("found", False):
            conf = p_ev.get("confidence", 0.5)
            if conf > best_score:
                best_score = conf
                best_ev = {
                    "node_id": node_id,
                    "file": p_ev.get("file", ""),
                    "line": p_ev.get("line", 0),
                    "snippet": p_ev.get("snippet", ""),
                    "source": "collider_stage_25",
                }
    return best_score, best_ev


def check_output_directory(component: dict) -> Dict[str, Any]:
    """Inspect component's output directory for Tier 1/2/3 files."""
    outputs = component.get("outputs", [])
    tiers_found = {"tier1": False, "tier2": False, "tier3": False}

    for out in outputs:
        if not isinstance(out, dict):
            continue
        name = out.get("name", "").lower()
        typ = out.get("type", "").lower()
        desc = out.get("description", "").lower()

        if "json" in typ and "briefing" not in name:
            tiers_found["tier1"] = True
        if "briefing" in name or "briefing" in desc:
            tiers_found["tier2"] = True
        if "html" in typ or "md" in typ or "markdown" in typ:
            tiers_found["tier3"] = True

    return tiers_found


# ============================================================================
# SCORING ENGINE v2
# ============================================================================

def score_component_v2(
    component: dict,
    collider: dict,
    ideome: dict,
) -> dict:
    """Score a component using Codome evidence (Layer 1) + Atlas (Domain C only)."""

    source_path = get_component_source_path(component) or ""
    node_evidence = get_node_evidence(collider, source_path) if source_path else {}
    has_collider = bool(node_evidence)

    scores = {}
    evidence_trail = {}

    # --- Domain A: Output Contract (from Codome evidence) ---

    # A1: D6 header (from Stage 25 grep)
    a1_score, a1_ev = aggregate_evidence(node_evidence, "a1_d6_header")
    scores["A1"] = a1_score
    evidence_trail["A1"] = a1_ev or {"source": "no_collider_evidence", "note": "Run collider full . to populate"}

    # A2: Three-tier output (output directory inspection)
    tiers = check_output_directory(component)
    tier_count = sum(1 for v in tiers.values() if v)
    scores["A2"] = round(tier_count / 3.0, 2)
    evidence_trail["A2"] = {"tiers": tiers, "source": "atlas_output_types"}

    # A3: Longitudinal tracking (from Stage 25 grep)
    a3_score, a3_ev = aggregate_evidence(node_evidence, "a3_longitudinal")
    scores["A3"] = a3_score
    evidence_trail["A3"] = a3_ev or {"source": "no_collider_evidence"}

    # A4: Meta envelope (= A1 + has JSON output)
    has_json_output = any(
        "json" in (out.get("type", "") if isinstance(out, dict) else "").lower()
        for out in component.get("outputs", [])
    )
    scores["A4"] = a1_score if has_json_output else 0.0
    evidence_trail["A4"] = {"derives_from": "A1 + json_output_check"}

    # A5: Cost tracking (from Stage 25 grep)
    a5_score, a5_ev = aggregate_evidence(node_evidence, "a5_cost_tracking")
    scores["A5"] = a5_score
    evidence_trail["A5"] = a5_ev or {"source": "no_collider_evidence"}

    # --- Domain B: Operational Resilience (from Codome evidence) ---

    # B1: Deterministic fallback (heuristic — hard to verify statically)
    b1_score = 0.0
    if has_collider:
        # If component has degradation handling, likely has fallback
        b2_score, _ = aggregate_evidence(node_evidence, "b2_degradation")
        b1_score = min(b2_score, 0.7)  # Cap at 0.7 (heuristic, not proven)
    scores["B1"] = b1_score
    evidence_trail["B1"] = {"source": "heuristic_from_b2", "confidence": "low"}

    # B2: LLM degradation signal (from Stage 25 grep)
    b2_score, b2_ev = aggregate_evidence(node_evidence, "b2_degradation")
    scores["B2"] = b2_score
    evidence_trail["B2"] = b2_ev or {"source": "no_collider_evidence"}

    # B3: Auto-feedback (from Stage 25 grep)
    b3_score, b3_ev = aggregate_evidence(node_evidence, "b3_auto_feedback")
    scores["B3"] = b3_score
    evidence_trail["B3"] = b3_ev or {"source": "no_collider_evidence"}

    # B4: Error observability (from Stage 25 except:pass ratio)
    b4_score, b4_ev = aggregate_evidence(node_evidence, "b4_error_observability")
    scores["B4"] = b4_score
    evidence_trail["B4"] = b4_ev or {"source": "no_collider_evidence"}

    # B5: Config SSOT (manual — return 0.5 with decay note)
    scores["B5"] = 0.5
    evidence_trail["B5"] = {"source": "manual_unverified", "confidence": "unknown"}

    # --- Domain C: Ecosystem Integration (Atlas checks — correct) ---

    stage = component.get("stage", "P0")
    stage_num = int(stage[1]) if len(stage) == 2 and stage[1].isdigit() else 0

    scores["C1"] = 1.0 if stage_num >= 2 else 0.0
    evidence_trail["C1"] = {"stage": stage, "source": "atlas"}

    # C2: Tools registry
    registry = load_yaml(ECOROOT / "TOOLS_REGISTRY.yaml")
    name = component.get("name", "")
    has_eco = any(
        isinstance(v, dict) and name in (v.get("name", ""), k)
        for k, v in registry.items() if isinstance(v, dict)
    )
    scores["C2"] = 1.0 if has_eco else 0.0
    evidence_trail["C2"] = {"source": "tools_registry"}

    # C3: Progressive compliance
    checks = [bool(component.get("id")), bool(component.get("name")),
              bool(component.get("purpose")), bool(component.get("owner"))]
    if stage_num >= 1:
        checks.append(bool(component.get("tags")))
    if stage_num >= 2:
        agent = component.get("agent", {})
        checks.extend([bool(agent.get("explanation")), bool(component.get("version"))])
    if stage_num >= 3:
        checks.append(bool(component.get("metrics", {}).get("cost_metric")))
    scores["C3"] = round(sum(1 for c in checks if c) / max(len(checks), 1), 2)
    evidence_trail["C3"] = {"source": "atlas_field_validation"}

    # C4: Feeds documented
    has_into = bool(component.get("feeds_into"))
    has_by = bool(component.get("fed_by"))
    scores["C4"] = 1.0 if (has_into and has_by) else (0.5 if (has_into or has_by) else 0.0)
    evidence_trail["C4"] = {"source": "atlas"}

    # C5: Agent affordances
    affordances = component.get("agent", {}).get("affordances", {})
    aff_count = sum(1 for f in ["can_read", "can_write", "cannot"] if f in affordances)
    scores["C5"] = round(aff_count / 3.0, 2)
    evidence_trail["C5"] = {"source": "atlas"}

    # --- Compute domain and overall scores ---
    domain_a = [scores[f"A{i}"] for i in range(1, 6)]
    domain_b = [scores[f"B{i}"] for i in range(1, 6)]
    domain_c = [scores[f"C{i}"] for i in range(1, 6)]

    domain_scores = {
        "output_contract": {"score": round(sum(domain_a) / 5, 2), "principles": {f"A{i}": scores[f"A{i}"] for i in range(1, 6)}},
        "operational_resilience": {"score": round(sum(domain_b) / 5, 2), "principles": {f"B{i}": scores[f"B{i}"] for i in range(1, 6)}},
        "ecosystem_integration": {"score": round(sum(domain_c) / 5, 2), "principles": {f"C{i}": scores[f"C{i}"] for i in range(1, 6)}},
    }

    alignment = round(
        0.40 * domain_scores["output_contract"]["score"] +
        0.35 * domain_scores["operational_resilience"]["score"] +
        0.25 * domain_scores["ecosystem_integration"]["score"],
        2
    )

    # Grade
    grade = "F"
    for g, threshold in [("A", 0.85), ("B", 0.70), ("C", 0.55), ("D", 0.40)]:
        if alignment >= threshold:
            grade = g
            break

    # Recommendations
    recs = []
    ideome_defs = load_yaml(IDEOME_PATH)
    for domain_key, domain_def in ideome_defs.get("domains", {}).items():
        for pid, pdef in domain_def.get("principles", {}).items():
            if scores.get(pid, 0) < 0.3:
                recs.append(f"Improve {pdef.get('name', pid)} ({pid}): score={scores.get(pid, 0)}")

    return {
        "_generated": _d6_header(),
        "component_id": component.get("id", "unknown"),
        "component_name": component.get("name", "unknown"),
        "display_name": component.get("display_name", ""),
        "stage": component.get("stage", "P0"),
        "alignment_score": alignment,
        "grade": grade,
        "domains": domain_scores,
        "evidence": evidence_trail,
        "has_collider_evidence": has_collider,
        "source_path": source_path,
        "nodes_matched": len(node_evidence),
        "recommendations": recs[:5],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def save_report(report: dict) -> None:
    ALIGNMENT_DIR.mkdir(parents=True, exist_ok=True)
    cid = report["component_id"]

    # Tier 1 JSON
    (ALIGNMENT_DIR / f"{cid}.v2.json").write_text(json.dumps(report, indent=2, default=str))

    # Tier 3 Markdown
    md = f"# Alignment Report v2: {report['display_name'] or report['component_name']}\n\n"
    md += f"**{report['component_id']}** | Stage: {report['stage']} | "
    md += f"Score: **{report['alignment_score']} ({report['grade']})** | "
    md += f"Collider evidence: {'Yes' if report['has_collider_evidence'] else 'No'}\n\n"

    for domain, data in report["domains"].items():
        md += f"## {domain.replace('_', ' ').title()} ({data['score']:.0%})\n\n"
        for pid, score in data["principles"].items():
            ev = report.get("evidence", {}).get(pid, {})
            source = ev.get("source", "unknown")
            snippet = ev.get("snippet", "")
            icon = "PASS" if score >= 0.7 else ("partial" if score > 0 else "FAIL")
            md += f"- [{icon}] **{pid}**: {score}"
            if snippet:
                md += f" — `{snippet[:60]}`"
            md += f" (source: {source})\n"
        md += "\n"

    if report["recommendations"]:
        md += "## Recommendations\n\n"
        for r in report["recommendations"]:
            md += f"- {r}\n"

    (ALIGNMENT_DIR / f"{cid}.v2.md").write_text(md)

    # Longitudinal index
    record = {
        "component_id": report["component_id"],
        "alignment_score": report["alignment_score"],
        "grade": report["grade"],
        "version": "2.0.0",
        "has_collider_evidence": report["has_collider_evidence"],
        "timestamp": report["timestamp"],
    }
    with open(ALIGNMENT_DIR / "alignment_index.jsonl", "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Ideome Scorer v2 — Evidence-Based Alignment")
    parser.add_argument("--component", help="Component ID (CMP-xxx)")
    parser.add_argument("--all", action="store_true", help="Score all P2+ components")
    args = parser.parse_args()

    atlas = load_yaml(ATLAS_PATH)
    collider = load_collider_output()
    ideome = load_yaml(IDEOME_PATH)

    has_evidence = bool(collider.get("principle_evidence"))
    if not has_evidence:
        print("Note: No Stage 25 evidence in unified_analysis.json.")
        print("Domain A/B scores will be lower. Run: collider-hub full --repo .\n")

    if args.component:
        comp = find_component(atlas, args.component)
        if not comp:
            print(f"Component {args.component} not found")
            sys.exit(1)
        report = score_component_v2(comp, collider, ideome)
        save_report(report)
        print(f"\n  {report['component_id']} ({report['display_name']})")
        print(f"  Alignment: {report['alignment_score']} ({report['grade']})")
        print(f"  Output Contract: {report['domains']['output_contract']['score']:.0%}")
        print(f"  Operational Resilience: {report['domains']['operational_resilience']['score']:.0%}")
        print(f"  Ecosystem Integration: {report['domains']['ecosystem_integration']['score']:.0%}")
        print(f"  Collider evidence: {'Yes' if report['has_collider_evidence'] else 'No'} ({report['nodes_matched']} nodes)")

    elif args.all:
        components = [c for c in atlas.get("components", []) if c.get("stage", "P0") >= "P2"]
        print(f"Scoring {len(components)} P2+ components (v2, evidence-based)...\n")
        results = []
        for comp in components:
            report = score_component_v2(comp, collider, ideome)
            save_report(report)
            results.append(report)
            ev_tag = "E" if report["has_collider_evidence"] else " "
            print(f"  [{ev_tag}] {report['component_id']:10s} {(report['display_name'] or report['component_name'])[:40]:40s} {report['grade']}  ({report['alignment_score']})")

        avg = sum(r["alignment_score"] for r in results) / len(results) if results else 0
        with_evidence = sum(1 for r in results if r["has_collider_evidence"])
        print(f"\n  Total: {len(results)} | Average: {avg:.2f} | With Collider evidence: {with_evidence}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
