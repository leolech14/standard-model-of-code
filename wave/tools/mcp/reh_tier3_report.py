"""
REH Tier 3 — Interactive HTML Report

Self-contained dark-theme HTML with inline SVG charts.
Mirrors Collider's tier3_html_report.py pattern.

Sections:
1. Header (repo name, date range, trajectory badge)
2. Executive Summary
3. Velocity Dashboard (SVG bar chart)
4. Timeline (SVG milestone markers)
5. Activity Heatmap (SVG grid)
6. Capability Changes (table)
7. Footer (metadata)
"""

import html as html_lib
from typing import Any, Dict, List


# --- Color palette (matches Collider) ---
_BG = "#0f172a"
_TEXT = "#e2e8f0"
_TEXT_DIM = "#94a3b8"
_CARD_BG = "#1e293b"
_BORDER = "#334155"
_GREEN = "#22c55e"
_BLUE = "#3b82f6"
_ORANGE = "#f97316"
_RED = "#ef4444"
_YELLOW = "#eab308"
_GRAY = "#6b7280"

_TRAJECTORY_COLORS = {
    "growing": _GREEN,
    "stable": _BLUE,
    "stabilizing": _BLUE,
    "declining": _ORANGE,
    "dormant": _GRAY,
    "restructuring": _YELLOW,
    "unknown": _GRAY,
}


def _esc(text: str) -> str:
    return html_lib.escape(str(text)) if text else ""


def build_reh_html_report(
    evolution_data: Dict[str, Any],
    briefing: Dict[str, Any],
) -> str:
    """Build self-contained HTML report from evolution + briefing data."""
    envelope = evolution_data.get("meta_envelope", {})
    velocity = evolution_data.get("velocity", {})
    milestones = evolution_data.get("milestones", [])
    activity = evolution_data.get("activity_heatmap", {})
    capability = evolution_data.get("capability_changes", {})
    trajectory = evolution_data.get("trajectory", "unknown")

    target = _esc(envelope.get("target", "Repository"))
    date_range = evolution_data.get("date_range", {})
    since = _esc(date_range.get("since", ""))
    until = _esc(date_range.get("until", ""))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>REH Report: {target}</title>
<style>{_build_css()}</style>
</head>
<body>
<div class="container">
{_build_header(target, trajectory, since, until, envelope)}
{_build_executive_summary(briefing.get("executive_summary", ""))}
{_build_velocity_dashboard(velocity)}
{_build_timeline(milestones)}
{_build_activity_heatmap(activity)}
{_build_capability_changes(capability)}
{_build_footer(envelope)}
</div>
</body>
</html>"""


def _build_css() -> str:
    return f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:{_BG};color:{_TEXT};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.6;padding:2rem}}
.container{{max-width:960px;margin:0 auto}}
.section{{background:{_CARD_BG};border:1px solid {_BORDER};border-radius:12px;padding:1.5rem;margin-bottom:1.5rem}}
.section-title{{font-size:1.1rem;font-weight:700;margin-bottom:1rem;color:{_TEXT}}}
header{{text-align:center;margin-bottom:2rem}}
header h1{{font-size:1.8rem;margin-bottom:0.5rem}}
header .date-range{{color:{_TEXT_DIM};font-size:0.9rem}}
.trajectory-badge{{display:inline-block;padding:4px 16px;border-radius:20px;font-size:0.85rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em}}
.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;margin-bottom:1rem}}
.metric{{background:{_BG};border-radius:8px;padding:1rem;text-align:center}}
.metric .value{{font-size:1.5rem;font-weight:700}}
.metric .label{{font-size:0.75rem;color:{_TEXT_DIM};text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;font-size:0.85rem}}
th,td{{padding:8px 12px;text-align:left;border-bottom:1px solid {_BORDER}}}
th{{color:{_TEXT_DIM};font-weight:600;font-size:0.75rem;text-transform:uppercase}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:600}}
.badge-high{{background:{_RED}33;color:{_RED}}}
.badge-medium{{background:{_ORANGE}33;color:{_ORANGE}}}
.badge-low{{background:{_BLUE}33;color:{_BLUE}}}
.badge-added{{background:{_GREEN}33;color:{_GREEN}}}
.badge-removed{{background:{_RED}33;color:{_RED}}}
.badge-modified{{background:{_YELLOW}33;color:{_YELLOW}}}
footer{{text-align:center;color:{_TEXT_DIM};font-size:0.75rem;padding:1rem 0}}
svg text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
@media print{{body{{background:#fff;color:#000}} .section{{border:1px solid #ccc;background:#f9f9f9}}}}
@media(max-width:640px){{.metric-grid{{grid-template-columns:1fr 1fr}}}}
"""


def _build_header(
    target: str, trajectory: str, since: str, until: str, envelope: Dict
) -> str:
    color = _TRAJECTORY_COLORS.get(trajectory, _GRAY)
    commits = envelope.get("commit_count", 0)
    cpw = envelope.get("velocity_commits_per_week", 0)
    return f"""
<header>
  <h1>Repository Evolution: {target}</h1>
  <div class="date-range">{since} to {until} &middot; {commits} commits &middot; {cpw:.0f} commits/week</div>
  <div style="margin-top:0.75rem">
    <span class="trajectory-badge" style="background:{color}22;color:{color};border:1px solid {color}">{_esc(trajectory)}</span>
  </div>
</header>"""


def _build_executive_summary(summary: str) -> str:
    return f"""
<section class="section">
  <div class="section-title">Executive Summary</div>
  <p>{_esc(summary)}</p>
</section>"""


def _build_velocity_dashboard(velocity: Dict) -> str:
    weekly = velocity.get("weekly_commits", [])
    avg = velocity.get("commits_per_week_avg", 0)
    trend = velocity.get("trend", "unknown")
    active_dirs = velocity.get("most_active_dirs", [])

    # SVG bar chart
    if weekly:
        max_val = max(w["commits"] for w in weekly) or 1
        bar_width = 60
        chart_width = len(weekly) * (bar_width + 10) + 40
        chart_height = 160
        bars = ""
        for i, w in enumerate(weekly):
            h = (w["commits"] / max_val) * 120
            x = 30 + i * (bar_width + 10)
            y = chart_height - 30 - h
            color = _GREEN if w["commits"] >= avg else _GRAY
            label = w["week"].split("-W")[1] if "-W" in w["week"] else w["week"]
            bars += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{h}" fill="{color}" rx="4" opacity="0.8"/>'
            bars += f'<text x="{x + bar_width/2}" y="{chart_height - 12}" text-anchor="middle" fill="{_TEXT_DIM}" font-size="10">W{label}</text>'
            bars += f'<text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" fill="{_TEXT}" font-size="11" font-weight="600">{w["commits"]}</text>'

        # Average line
        avg_y = chart_height - 30 - (avg / max_val) * 120
        bars += f'<line x1="25" y1="{avg_y}" x2="{chart_width - 10}" y2="{avg_y}" stroke="{_ORANGE}" stroke-dasharray="5,5" opacity="0.6"/>'
        bars += f'<text x="{chart_width - 8}" y="{avg_y - 4}" fill="{_ORANGE}" font-size="10" text-anchor="end">avg {avg:.0f}</text>'

        chart = f'<svg viewBox="0 0 {chart_width} {chart_height}" width="100%" style="max-height:180px">{bars}</svg>'
    else:
        chart = '<p style="color:#94a3b8">No weekly data available</p>'

    dirs_html = "".join(f"<li>{_esc(d)}</li>" for d in active_dirs[:5])

    return f"""
<section class="section">
  <div class="section-title">Velocity Dashboard</div>
  <div class="metric-grid">
    <div class="metric"><div class="value">{avg:.0f}</div><div class="label">Commits / Week</div></div>
    <div class="metric"><div class="value">{_esc(trend)}</div><div class="label">Trend</div></div>
  </div>
  {chart}
  {"<div style='margin-top:1rem'><strong>Most Active Areas:</strong><ul style=\"margin-top:0.5rem;padding-left:1.5rem;color:" + _TEXT_DIM + "\">" + dirs_html + "</ul></div>" if dirs_html else ""}
</section>"""


def _build_timeline(milestones: List[Dict]) -> str:
    if not milestones:
        return """
<section class="section">
  <div class="section-title">Milestones</div>
  <p style="color:#94a3b8">No significant milestones detected in this period.</p>
</section>"""

    # SVG timeline
    width = 800
    height = 60 + len(milestones) * 50
    line_x = 80
    items = ""

    type_colors = {
        "capability_added": _GREEN,
        "refactor": _BLUE,
        "bugfix_wave": _ORANGE,
        "major_change": _YELLOW,
    }

    for i, m in enumerate(milestones):
        y = 40 + i * 50
        color = type_colors.get(m.get("type", ""), _GRAY)
        r = 8 if m.get("impact") == "high" else 6
        title = _esc(m.get("title", "")[:60])
        date = _esc(m.get("date", ""))
        desc = _esc(m.get("description", "")[:80])

        items += f'<circle cx="{line_x}" cy="{y}" r="{r}" fill="{color}"/>'
        items += f'<text x="{line_x - 45}" y="{y + 4}" fill="{_TEXT_DIM}" font-size="10" text-anchor="end">{date}</text>'
        items += f'<text x="{line_x + 20}" y="{y - 2}" fill="{_TEXT}" font-size="12" font-weight="600">{title}</text>'
        items += f'<text x="{line_x + 20}" y="{y + 14}" fill="{_TEXT_DIM}" font-size="10">{desc}</text>'

    # Vertical line
    line_svg = f'<line x1="{line_x}" y1="30" x2="{line_x}" y2="{height - 10}" stroke="{_BORDER}" stroke-width="2"/>'

    return f"""
<section class="section">
  <div class="section-title">Milestones</div>
  <svg viewBox="0 0 {width} {height}" width="100%">{line_svg}{items}</svg>
</section>"""


def _build_activity_heatmap(activity: Dict) -> str:
    matrix = activity.get("matrix", [])
    weeks = activity.get("weeks", [])

    if not matrix or not weeks:
        return """
<section class="section">
  <div class="section-title">Activity Heatmap</div>
  <p style="color:#94a3b8">No activity data available.</p>
</section>"""

    # SVG heatmap grid
    cell_w = 50
    cell_h = 30
    label_w = 140
    header_h = 30
    width = label_w + len(weeks) * (cell_w + 4) + 20
    height = header_h + len(matrix) * (cell_h + 4) + 10

    # Find max for color scaling
    all_vals = [v for row in matrix for v in row.get("weekly", [])]
    max_val = max(all_vals) if all_vals else 1

    svg = ""

    # Week headers
    for j, w in enumerate(weeks):
        x = label_w + j * (cell_w + 4)
        label = w.split("-W")[1] if "-W" in w else w[-2:]
        svg += f'<text x="{x + cell_w/2}" y="{header_h - 8}" fill="{_TEXT_DIM}" font-size="10" text-anchor="middle">W{label}</text>'

    # Rows
    for i, row in enumerate(matrix):
        y = header_h + i * (cell_h + 4)
        dir_name = _esc(row.get("directory", "")[:16])
        svg += f'<text x="{label_w - 8}" y="{y + cell_h/2 + 4}" fill="{_TEXT_DIM}" font-size="11" text-anchor="end">{dir_name}</text>'

        for j, val in enumerate(row.get("weekly", [])):
            x = label_w + j * (cell_w + 4)
            intensity = val / max_val if max_val > 0 else 0
            # Color: transparent → green
            opacity = 0.1 + intensity * 0.8
            color = _GREEN if intensity > 0.5 else _BLUE if intensity > 0.2 else _GRAY
            svg += f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{color}" opacity="{opacity:.2f}" rx="4"/>'
            if val > 0:
                svg += f'<text x="{x + cell_w/2}" y="{y + cell_h/2 + 4}" fill="{_TEXT}" font-size="10" text-anchor="middle" opacity="0.9">{val}</text>'

    return f"""
<section class="section">
  <div class="section-title">Activity Heatmap (directories x weeks)</div>
  <div style="overflow-x:auto">
    <svg viewBox="0 0 {width} {height}" width="100%" style="min-width:{width}px">{svg}</svg>
  </div>
</section>"""


def _build_capability_changes(capability: Dict) -> str:
    changes = capability.get("recently_changed", [])
    total = capability.get("total_current", 0)

    if not changes:
        return f"""
<section class="section">
  <div class="section-title">Capabilities ({total} tracked)</div>
  <p style="color:#94a3b8">No recent capability changes detected.</p>
</section>"""

    rows = ""
    for c in changes[:15]:
        name = _esc(c.get("name", ""))
        file = _esc(c.get("file", ""))
        ctype = _esc(c.get("type", "function"))
        rows += f'<tr><td><code>{name}</code></td><td>{ctype}</td><td style="color:{_TEXT_DIM}">{file}</td></tr>'

    return f"""
<section class="section">
  <div class="section-title">Recently Changed Capabilities ({len(changes)} of {total})</div>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>File</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def _build_footer(envelope: Dict) -> str:
    run_ts = _esc(envelope.get("run_ts", ""))
    run_id = _esc(envelope.get("run_id", "")[:8])
    version = _esc(envelope.get("reh_version", "1.0.0"))
    hostname = _esc(envelope.get("hostname", ""))
    analysis_ms = envelope.get("analysis_time_ms", 0)

    return f"""
<footer>
  REH v{version} &middot; Run {run_id} &middot; {run_ts} &middot; {hostname} &middot; {analysis_ms}ms
</footer>"""
