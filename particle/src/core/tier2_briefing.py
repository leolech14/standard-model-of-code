#!/usr/bin/env python3
"""
Tier 2: AI Briefing generator for Collider.

Distills the full compiled_insights dict into a compact JSON payload
targeted at <4,000 tokens for direct LLM consumption.

Design constraints:
    - Max 5 findings (sorted by severity DESC, confidence DESC)
    - Text truncation: title 80, description 200, recommendation 200
    - KPI subset only (no per-node detail)
    - Token budget: soft-warn at 4K, no crash
"""

from __future__ import annotations

import json
import warnings
from typing import Any, Dict, List, Optional

# Severity sort order (higher = more urgent)
_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
_MAX_FINDINGS = 5
_TOKEN_BUDGET = 4000

# Text field truncation limits
_TRUNC_TITLE = 80
_TRUNC_DESC = 200
_TRUNC_RECOMMENDATION = 200
_TRUNC_SUMMARY = 500


def build_briefing(
    compiled_insights: Dict[str, Any],
    full_output: Dict[str, Any],
    meta_envelope: Dict[str, Any],
) -> Dict[str, Any]:
    """Distill compiled insights into a <4K token AI briefing.

    Args:
        compiled_insights: Dict from InsightsReport.to_dict() (Stage 21 output).
        full_output: Full pipeline output dict (for stats/counts extraction).
        meta_envelope: Standard identity envelope (embedded as-is).

    Returns:
        Compact briefing dict ready for JSON serialization.
    """
    # Extract and truncate executive summary
    exec_summary = _truncate(
        compiled_insights.get("executive_summary", ""), _TRUNC_SUMMARY
    )

    # Distill top findings
    raw_findings = compiled_insights.get("findings", [])
    top_findings = _distill_findings(raw_findings, limit=_MAX_FINDINGS)

    # Extract KPI summary from full_output
    stats_summary = _extract_stats_summary(full_output)

    # Navigation (pass through, already compact)
    navigation = compiled_insights.get("navigation", {})
    # Truncate navigation lists to top 3 each
    for key in ("start_here", "critical_path", "top_risks"):
        items = navigation.get(key, [])
        if isinstance(items, list) and len(items) > 3:
            navigation[key] = items[:3]

    briefing = {
        "meta_envelope": meta_envelope,
        "executive_summary": exec_summary,
        "grade": compiled_insights.get("grade", "?"),
        "health_score": round(compiled_insights.get("health_score", 0.0), 2),
        "health_components": _round_dict(
            compiled_insights.get("health_components", {}), 2
        ),
        "mission_matrix": compiled_insights.get("mission_matrix", {}),
        "top_findings": top_findings,
        "stats_summary": stats_summary,
        "navigation": navigation,
    }

    # Token budget gate (soft warn)
    _check_token_budget(briefing)

    return briefing


def _distill_findings(
    findings: List[Dict[str, Any]], limit: int = _MAX_FINDINGS
) -> List[Dict[str, Any]]:
    """Select top N findings, sorted by severity then confidence, with truncation."""
    if not findings:
        return []

    # Sort: severity ascending (critical first), then confidence descending
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            _SEVERITY_ORDER.get(str(f.get("severity", "info")).lower(), 99),
            -(f.get("confidence", 0.0)),
        ),
    )

    distilled = []
    for f in sorted_findings[:limit]:
        distilled.append({
            "severity": f.get("severity", "info"),
            "category": f.get("category", "unknown"),
            "title": _truncate(f.get("title", ""), _TRUNC_TITLE),
            "description": _truncate(f.get("description", ""), _TRUNC_DESC),
            "recommendation": _truncate(f.get("recommendation", ""), _TRUNC_RECOMMENDATION),
            "confidence": round(f.get("confidence", 0.0), 2),
            "related_node_count": len(f.get("related_nodes", [])),
        })

    return distilled


def _extract_stats_summary(full_output: Dict[str, Any]) -> Dict[str, Any]:
    """Pull key KPIs from the full output for the briefing."""
    counts = full_output.get("counts", {}) if isinstance(full_output, dict) else {}
    stats = full_output.get("stats", {}) if isinstance(full_output, dict) else {}
    kpis = full_output.get("kpis", {}) if isinstance(full_output, dict) else {}

    return {
        "files": counts.get("files", 0),
        "nodes": counts.get("nodes", 0),
        "edges": counts.get("edges", 0),
        "avg_complexity": round(kpis.get("avg_complexity", 0.0), 2),
        "test_coverage_ratio": round(kpis.get("test_coverage_ratio", 0.0), 2),
        "entry_points": counts.get("entry_points", 0),
        "orphan_ratio": round(
            counts.get("orphans", 0) / max(counts.get("nodes", 1), 1), 3
        ),
        "cycle_count": counts.get("cycles", 0),
    }


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len, appending ellipsis if truncated."""
    if not text or len(text) <= max_len:
        return text or ""
    return text[: max_len - 3].rstrip() + "..."


def _round_dict(d: Dict[str, Any], decimals: int) -> Dict[str, Any]:
    """Round all numeric values in a flat dict."""
    result = {}
    for k, v in d.items():
        try:
            result[k] = round(float(v), decimals)
        except (TypeError, ValueError):
            result[k] = v
    return result


def _check_token_budget(briefing: Dict[str, Any]) -> None:
    """Soft-warn if briefing exceeds token budget. Does not crash."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        json_str = json.dumps(briefing, default=str)
        token_count = len(enc.encode(json_str))
        if token_count > _TOKEN_BUDGET:
            warnings.warn(
                f"Tier 2 briefing is {token_count:,} tokens "
                f"(budget: {_TOKEN_BUDGET:,}). Consider reducing content.",
                stacklevel=2,
            )
    except ImportError:
        # tiktoken not available — skip budget check
        pass
