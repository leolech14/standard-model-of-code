"""
REH Tier 2 — AI Briefing (<4K tokens)

Distills full evolution data into a compact JSON for LLM context injection.
Mirrors Collider's tier2_briefing.py pattern.
"""

import json
import warnings
from typing import Any, Dict, List


_MAX_MILESTONES = 5
_TOKEN_BUDGET = 4000
_TRUNC_TITLE = 80
_TRUNC_DESC = 200
_TRUNC_SUMMARY = 500


def _truncate(text: str, max_len: int) -> str:
    if not text or len(text) <= max_len:
        return text or ""
    content_max = max_len - 3
    truncated = text[:content_max]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        return truncated[:last_space] + "..."
    return truncated + "..."


def _round_val(v: Any, decimals: int = 2) -> Any:
    if isinstance(v, float):
        return round(v, decimals)
    if isinstance(v, dict):
        return {k: _round_val(val, decimals) for k, val in v.items()}
    if isinstance(v, list):
        return [_round_val(item, decimals) for item in v]
    return v


def build_reh_briefing(
    evolution_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Build <4K token AI briefing from full evolution compilation.

    Args:
        evolution_data: Output of EvolutionCompiler.compile()

    Returns:
        Compact JSON dict suitable for LLM context injection.
    """
    velocity = evolution_data.get("velocity", {})
    milestones = evolution_data.get("milestones", [])
    capability = evolution_data.get("capability_changes", {})
    activity = evolution_data.get("activity_heatmap", {})
    envelope = evolution_data.get("meta_envelope", {})
    trajectory = evolution_data.get("trajectory", "unknown")

    # Build executive summary
    target = envelope.get("target", "repo")
    cpw = velocity.get("commits_per_week_avg", 0)
    trend = velocity.get("trend", "unknown")
    total_commits = envelope.get("commit_count", 0)
    n_milestones = len(milestones)
    cap_changed = capability.get("recently_changed_count", 0)

    # Commit count transparency (merge filter may reduce count)
    raw_commits = envelope.get("commit_count_raw", total_commits)
    commit_note = (
        f"{total_commits} commits" if raw_commits == total_commits
        else f"{total_commits} dev commits ({raw_commits} total)"
    )

    summary = (
        f"{target} is {trajectory} with {cpw:.0f} commits/week ({trend}). "
        f"{commit_note} analyzed, {n_milestones} milestones detected, "
        f"{cap_changed} capabilities recently changed."
    )

    # Distill milestones (top 5, sorted by impact)
    impact_order = {"high": 0, "medium": 1, "low": 2}
    sorted_milestones = sorted(
        milestones,
        key=lambda m: (impact_order.get(m.get("impact", "low"), 2), m.get("date", "")),
    )[:_MAX_MILESTONES]

    top_milestones = [
        {
            "date": m["date"],
            "type": m.get("type", "change"),
            "title": _truncate(m.get("title", ""), _TRUNC_TITLE),
            "description": _truncate(m.get("description", ""), _TRUNC_DESC),
            "impact": m.get("impact", "medium"),
            "files_changed": m.get("files_born_count", 0),
        }
        for m in sorted_milestones
    ]

    # Hot and cold zones
    matrix = activity.get("matrix", [])
    hot_zones = [f"{row['directory']} ({row['total']} changes)" for row in matrix[:3]]
    cold_zones = [
        f"{row['directory']} ({row['total']} changes)"
        for row in sorted(matrix, key=lambda r: r.get("total", 0))[:2]
    ] if len(matrix) > 3 else []

    # Volatility zones (for AI agents: high stddev = unstable, worth watching)
    volatility_zones: list = []
    for row in matrix:
        weeks = row.get("weeks", {})
        vals = list(weeks.values())
        if len(vals) >= 2:
            mean = sum(vals) / len(vals)
            stddev = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
            if stddev > 0 and mean > 0:
                volatility_zones.append((row["directory"], round(stddev, 1), row["total"]))
    volatility_zones.sort(key=lambda x: -x[1])

    # Capability summary
    cap_summary = {
        "total_capabilities": capability.get("total_current", 0),
        "recently_changed": cap_changed,
    }

    # Navigation hints
    navigation = {
        "start_here": [
            m["date"] + ": " + _truncate(m.get("title", ""), 50)
            for m in sorted_milestones[:3]
        ],
        "watch_list": cold_zones[:2],
        "watch_list_agent": [
            f"{d} (volatility: {s}, total: {t})"
            for d, s, t in volatility_zones[:2]
        ],
        "growth_areas": hot_zones[:2],
    }

    briefing = {
        "meta_envelope": envelope,
        "executive_summary": _truncate(summary, _TRUNC_SUMMARY),
        "trajectory": trajectory,
        "velocity": _round_val({
            "commits_per_week_avg": cpw,
            "trend": trend,
            "most_active_dirs": velocity.get("most_active_dirs", [])[:3],
        }),
        "top_milestones": top_milestones,
        "capability_summary": cap_summary,
        "hot_zones": hot_zones,
        "cold_zones": cold_zones,
        "navigation": navigation,
    }

    _check_token_budget(briefing)
    return briefing


def _check_token_budget(briefing: Dict) -> None:
    """Warn if briefing exceeds token budget."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        text = json.dumps(briefing, default=str)
        tokens = len(enc.encode(text))
        if tokens > _TOKEN_BUDGET:
            warnings.warn(
                f"REH briefing is {tokens} tokens (budget: {_TOKEN_BUDGET})",
                stacklevel=2,
            )
    except ImportError:
        pass  # tiktoken optional
