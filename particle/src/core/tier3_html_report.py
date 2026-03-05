#!/usr/bin/env python3
"""
Tier 3: Self-contained HTML narrative report for Collider.

Generates a single HTML file with:
    - Inline CSS (dark theme, print-friendly)
    - Inline SVG charts (radar for health components, bars for mission matrix)
    - No external dependencies (fonts, scripts, stylesheets)
    - 7 sections: Header, Executive Summary, Health Dashboard, Top Findings,
      Architecture Overview, Navigation Guide, Footer

Design constraints:
    - Zero runtime dependencies (pure Python f-strings)
    - Opens correctly when double-clicked in any browser
    - Print-friendly via @media print
"""

from __future__ import annotations

import html
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# Grade badge color mapping
_GRADE_COLORS = {
    "A+": "#22c55e", "A": "#22c55e", "A-": "#4ade80",
    "B+": "#3b82f6", "B": "#3b82f6", "B-": "#60a5fa",
    "C+": "#eab308", "C": "#eab308", "C-": "#facc15",
    "D+": "#f97316", "D": "#f97316", "D-": "#fb923c",
    "F": "#ef4444",
}

_SEVERITY_COLORS = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#eab308",
    "low": "#3b82f6",
    "info": "#6b7280",
}


def build_html_report(
    compiled_insights: Dict[str, Any],
    full_output: Dict[str, Any],
    meta_envelope: Dict[str, Any],
) -> str:
    """Generate self-contained HTML narrative report.

    Args:
        compiled_insights: Dict from InsightsReport.to_dict() (Stage 21).
        full_output: Full pipeline output dict (for stats extraction).
        meta_envelope: Standard identity envelope.

    Returns:
        Complete HTML string ready to write to file.
    """
    grade = compiled_insights.get("grade", "?")
    health_score = compiled_insights.get("health_score", 0.0)
    health_components = compiled_insights.get("health_components", {})
    mission_matrix = compiled_insights.get("mission_matrix", {})
    exec_summary = compiled_insights.get("executive_summary", "")
    findings = compiled_insights.get("findings", [])
    navigation = compiled_insights.get("navigation", {})

    counts = full_output.get("counts", {}) if isinstance(full_output, dict) else {}
    stats = full_output.get("stats", {}) if isinstance(full_output, dict) else {}
    kpis = full_output.get("kpis", {}) if isinstance(full_output, dict) else {}

    target_name = meta_envelope.get("target", "Unknown")
    run_ts = meta_envelope.get("run_ts", datetime.now(timezone.utc).isoformat())
    collider_version = meta_envelope.get("collider_version", "unknown")
    run_id = meta_envelope.get("run_id", "unknown")

    # Build sections
    css = _build_css()
    header_html = _build_header(target_name, grade, health_score, run_ts)
    summary_html = _build_executive_summary(exec_summary)
    dashboard_html = _build_health_dashboard(health_components, mission_matrix)
    findings_html = _build_findings(findings)
    arch_html = _build_architecture_overview(counts, stats, kpis, meta_envelope)
    nav_html = _build_navigation(navigation)
    footer_html = _build_footer(collider_version, run_id, run_ts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Collider Report — {_esc(target_name)}</title>
<style>{css}</style>
</head>
<body>
<div class="container">
{header_html}
{summary_html}
{dashboard_html}
{findings_html}
{arch_html}
{nav_html}
{footer_html}
</div>
</body>
</html>"""


# ─── Section Builders ──────────────────────────────────────────────


def _build_header(target: str, grade: str, health_score: float, run_ts: str) -> str:
    color = _GRADE_COLORS.get(grade, "#6b7280")
    # Parse timestamp for display
    try:
        dt = datetime.fromisoformat(run_ts.replace("Z", "+00:00"))
        ts_display = dt.strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        ts_display = str(run_ts)

    score_pct = min(health_score / 10.0 * 100, 100)

    return f"""<header>
<div class="header-top">
    <h1>{_esc(target)}</h1>
    <div class="header-meta">{ts_display}</div>
</div>
<div class="grade-row">
    <div class="grade-badge" style="background:{color}">{_esc(grade)}</div>
    <div class="health-gauge">
        <div class="gauge-label">Health Score: {health_score:.1f}/10</div>
        <div class="gauge-track">
            <div class="gauge-fill" style="width:{score_pct:.0f}%;background:{color}"></div>
        </div>
    </div>
</div>
</header>"""


def _build_executive_summary(summary: str) -> str:
    if not summary:
        return ""
    # Convert newlines to paragraphs
    paragraphs = [p.strip() for p in summary.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [summary]
    p_html = "\n".join(f"<p>{_esc(p)}</p>" for p in paragraphs)
    return f"""<section class="section">
<h2>Executive Summary</h2>
{p_html}
</section>"""


def _build_health_dashboard(
    components: Dict[str, Any], mission: Dict[str, Any]
) -> str:
    radar_svg = _build_radar_chart(components) if components else ""
    bars_html = _build_mission_bars(mission) if mission else ""

    return f"""<section class="section">
<h2>Health Dashboard</h2>
<div class="dashboard-grid">
    <div class="chart-panel">
        <h3>Health Components</h3>
        {radar_svg}
    </div>
    <div class="chart-panel">
        <h3>Mission Matrix</h3>
        {bars_html}
    </div>
</div>
</section>"""


def _build_findings(findings: List[Dict[str, Any]]) -> str:
    if not findings:
        return ""

    # Sort by severity
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_f = sorted(
        findings,
        key=lambda f: (
            sev_order.get(str(f.get("severity", "info")).lower(), 99),
            -(f.get("confidence", 0.0)),
        ),
    )

    cards = []
    for f in sorted_f[:10]:  # Cap at 10 for readability
        sev = str(f.get("severity", "info")).lower()
        color = _SEVERITY_COLORS.get(sev, "#6b7280")
        confidence = f.get("confidence", 0.0)
        conf_pct = min(confidence * 100, 100)
        title = f.get("title", "Untitled")
        desc = f.get("description", "")
        rec = f.get("recommendation", "")
        category = f.get("category", "")
        nodes = f.get("related_nodes", [])
        node_count = len(nodes) if isinstance(nodes, list) else 0

        rec_html = f'<div class="finding-rec"><strong>Recommendation:</strong> {_esc(rec)}</div>' if rec else ""

        cards.append(f"""<div class="finding-card">
    <div class="finding-header">
        <span class="severity-badge" style="background:{color}">{_esc(sev.upper())}</span>
        <span class="finding-category">{_esc(category)}</span>
        <span class="finding-confidence">
            <span class="conf-bar"><span class="conf-fill" style="width:{conf_pct:.0f}%"></span></span>
            {confidence:.0%}
        </span>
    </div>
    <div class="finding-title">{_esc(title)}</div>
    <div class="finding-desc">{_esc(desc)}</div>
    {rec_html}
    <div class="finding-meta">{node_count} related node{"s" if node_count != 1 else ""}</div>
</div>""")

    return f"""<section class="section">
<h2>Top Findings</h2>
{"".join(cards)}
</section>"""


def _build_architecture_overview(
    counts: Dict, stats: Dict, kpis: Dict, envelope: Dict
) -> str:
    lang_mix = envelope.get("language_mix", {})
    lang_rows = ""
    if lang_mix:
        sorted_langs = sorted(lang_mix.items(), key=lambda x: -x[1] if isinstance(x[1], (int, float)) else 0)
        for lang, pct in sorted_langs[:8]:
            val = pct * 100 if isinstance(pct, float) and pct <= 1 else pct
            lang_rows += f"<tr><td>{_esc(str(lang))}</td><td>{val:.1f}%</td></tr>\n"

    return f"""<section class="section">
<h2>Architecture Overview</h2>
<div class="dashboard-grid">
    <div class="stats-panel">
        <h3>Structure</h3>
        <table class="stats-table">
            <tr><td>Files</td><td>{counts.get("files", 0):,}</td></tr>
            <tr><td>Nodes</td><td>{counts.get("nodes", 0):,}</td></tr>
            <tr><td>Edges</td><td>{counts.get("edges", 0):,}</td></tr>
            <tr><td>Entry Points</td><td>{counts.get("entry_points", 0):,}</td></tr>
            <tr><td>Orphans</td><td>{counts.get("orphans", 0):,}</td></tr>
            <tr><td>Cycles</td><td>{counts.get("cycles", 0):,}</td></tr>
        </table>
    </div>
    <div class="stats-panel">
        <h3>Quality Metrics</h3>
        <table class="stats-table">
            <tr><td>Avg Complexity</td><td>{kpis.get("avg_complexity", 0.0):.2f}</td></tr>
            <tr><td>Test Coverage</td><td>{kpis.get("test_coverage_ratio", 0.0):.0%}</td></tr>
            <tr><td>Analysis Time</td><td>{envelope.get("analysis_time_ms", 0):,}ms</td></tr>
        </table>
        {f'<h3>Languages</h3><table class="stats-table">{lang_rows}</table>' if lang_rows else ""}
    </div>
</div>
</section>"""


def _build_navigation(navigation: Dict[str, Any]) -> str:
    if not navigation:
        return ""

    sections = []
    labels = {
        "start_here": "Start Here",
        "critical_path": "Critical Path",
        "top_risks": "Top Risks",
    }
    for key, label in labels.items():
        items = navigation.get(key, [])
        if not items:
            continue
        if isinstance(items, list):
            li_html = "\n".join(f"<li>{_esc(str(item))}</li>" for item in items[:5])
        else:
            li_html = f"<li>{_esc(str(items))}</li>"
        sections.append(f"<div class='nav-section'><h3>{label}</h3><ol>{li_html}</ol></div>")

    if not sections:
        return ""

    return f"""<section class="section">
<h2>Navigation Guide</h2>
<div class="nav-grid">
{"".join(sections)}
</div>
</section>"""


def _build_footer(version: str, run_id: str, run_ts: str) -> str:
    return f"""<footer>
<div class="footer-content">
    <span>Generated by Collider v{_esc(version)}</span>
    <span class="footer-sep">|</span>
    <span>Run: {_esc(run_id[:8])}</span>
    <span class="footer-sep">|</span>
    <span>{_esc(run_ts)}</span>
</div>
</footer>"""


# ─── SVG Chart Builders ────────────────────────────────────────────


def _build_radar_chart(components: Dict[str, Any], size: int = 280) -> str:
    """Build inline SVG radar chart for health components."""
    if not components:
        return "<p>No health component data.</p>"

    labels = list(components.keys())
    values = []
    for k in labels:
        try:
            values.append(float(components[k]))
        except (TypeError, ValueError):
            values.append(0.0)

    n = len(labels)
    if n < 3:
        return "<p>Insufficient dimensions for radar chart.</p>"

    cx, cy = size / 2, size / 2
    max_r = size / 2 - 40  # Leave room for labels

    # Background grid rings (at 25%, 50%, 75%, 100%)
    grid_lines = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        r = max_r * frac
        points = " ".join(
            f"{cx + r * math.sin(2 * math.pi * i / n):.1f},"
            f"{cy - r * math.cos(2 * math.pi * i / n):.1f}"
            for i in range(n)
        )
        grid_lines.append(
            f'<polygon points="{points}" fill="none" stroke="#374151" stroke-width="1"/>'
        )

    # Axis lines
    axis_lines = []
    for i in range(n):
        x = cx + max_r * math.sin(2 * math.pi * i / n)
        y = cy - max_r * math.cos(2 * math.pi * i / n)
        axis_lines.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="#374151" stroke-width="1"/>'
        )

    # Data polygon
    data_points = []
    for i, v in enumerate(values):
        r = max_r * min(v / 10.0, 1.0)
        x = cx + r * math.sin(2 * math.pi * i / n)
        y = cy - r * math.cos(2 * math.pi * i / n)
        data_points.append(f"{x:.1f},{y:.1f}")

    data_polygon = (
        f'<polygon points="{" ".join(data_points)}" '
        f'fill="rgba(59,130,246,0.25)" stroke="#3b82f6" stroke-width="2"/>'
    )

    # Data points (dots)
    dots = []
    for i, v in enumerate(values):
        r = max_r * min(v / 10.0, 1.0)
        x = cx + r * math.sin(2 * math.pi * i / n)
        y = cy - r * math.cos(2 * math.pi * i / n)
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#3b82f6"/>'
        )

    # Labels
    label_elems = []
    for i, label in enumerate(labels):
        angle = 2 * math.pi * i / n
        lr = max_r + 24
        x = cx + lr * math.sin(angle)
        y = cy - lr * math.cos(angle)
        # Text anchor based on position
        if abs(math.sin(angle)) < 0.1:
            anchor = "middle"
        elif math.sin(angle) > 0:
            anchor = "start"
        else:
            anchor = "end"
        # Clean label: replace underscores, title case
        display = label.replace("_", " ").title()
        # Truncate long labels
        if len(display) > 14:
            display = display[:12] + ".."
        v = values[i]
        label_elems.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'fill="#9ca3af" font-size="11">{_esc(display)} ({v:.1f})</text>'
        )

    return f"""<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
{"".join(grid_lines)}
{"".join(axis_lines)}
{data_polygon}
{"".join(dots)}
{"".join(label_elems)}
</svg>"""


def _build_mission_bars(mission: Dict[str, Any]) -> str:
    """Build horizontal bar chart for mission matrix dimensions."""
    if not mission:
        return "<p>No mission matrix data.</p>"

    rows = []
    for dim, score in mission.items():
        try:
            val = float(score)
        except (TypeError, ValueError):
            val = 0.0
        pct = min(val, 100)
        display = dim.replace("_", " ").title()
        # Color gradient: red→yellow→green based on score
        if val >= 75:
            color = "#22c55e"
        elif val >= 50:
            color = "#eab308"
        elif val >= 25:
            color = "#f97316"
        else:
            color = "#ef4444"

        rows.append(f"""<div class="bar-row">
    <div class="bar-label">{_esc(display)}</div>
    <div class="bar-track">
        <div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
    </div>
    <div class="bar-value">{val:.0f}</div>
</div>""")

    return "\n".join(rows)


# ─── CSS ───────────────────────────────────────────────────────────


def _build_css() -> str:
    return """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
background:#0f172a;color:#e2e8f0;line-height:1.6;padding:2rem}
.container{max-width:900px;margin:0 auto}
header{margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid #1e293b}
.header-top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:1rem}
h1{font-size:1.8rem;font-weight:700;color:#f1f5f9}
.header-meta{color:#64748b;font-size:0.9rem}
.grade-row{display:flex;align-items:center;gap:1.5rem}
.grade-badge{display:inline-flex;align-items:center;justify-content:center;
width:56px;height:56px;border-radius:12px;font-size:1.5rem;font-weight:800;color:#fff}
.health-gauge{flex:1}
.gauge-label{font-size:0.85rem;color:#94a3b8;margin-bottom:4px}
.gauge-track{height:10px;background:#1e293b;border-radius:5px;overflow:hidden}
.gauge-fill{height:100%;border-radius:5px;transition:width 0.5s}
.section{margin-bottom:2rem;padding:1.5rem;background:#1e293b;border-radius:12px}
h2{font-size:1.3rem;color:#f1f5f9;margin-bottom:1rem;
padding-bottom:0.5rem;border-bottom:1px solid #334155}
h3{font-size:1rem;color:#cbd5e1;margin-bottom:0.75rem}
p{margin-bottom:0.75rem;color:#cbd5e1}
.dashboard-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
.chart-panel,.stats-panel{background:#0f172a;padding:1rem;border-radius:8px}
svg{display:block;margin:0 auto}
.bar-row{display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem}
.bar-label{width:100px;font-size:0.85rem;color:#94a3b8;text-align:right}
.bar-track{flex:1;height:18px;background:#334155;border-radius:4px;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;transition:width 0.5s}
.bar-value{width:36px;font-size:0.85rem;color:#e2e8f0;text-align:right}
.finding-card{background:#0f172a;border-radius:8px;padding:1rem;margin-bottom:0.75rem;
border-left:3px solid #334155}
.finding-header{display:flex;align-items:center;gap:0.75rem;margin-bottom:0.5rem}
.severity-badge{display:inline-block;padding:2px 8px;border-radius:4px;
font-size:0.7rem;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:0.05em}
.finding-category{font-size:0.8rem;color:#64748b}
.finding-confidence{margin-left:auto;display:flex;align-items:center;gap:6px;
font-size:0.8rem;color:#94a3b8}
.conf-bar{display:inline-block;width:48px;height:6px;background:#334155;
border-radius:3px;overflow:hidden}
.conf-fill{display:block;height:100%;background:#3b82f6;border-radius:3px}
.finding-title{font-weight:600;color:#f1f5f9;margin-bottom:4px}
.finding-desc{font-size:0.9rem;color:#94a3b8;margin-bottom:6px}
.finding-rec{font-size:0.85rem;color:#cbd5e1;padding:8px;
background:#1e293b;border-radius:4px;margin-bottom:6px}
.finding-meta{font-size:0.75rem;color:#475569}
.stats-table{width:100%;border-collapse:collapse}
.stats-table td{padding:6px 8px;border-bottom:1px solid #1e293b;font-size:0.9rem}
.stats-table td:first-child{color:#94a3b8}
.stats-table td:last-child{text-align:right;color:#e2e8f0;font-variant-numeric:tabular-nums}
.nav-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}
.nav-section{background:#0f172a;padding:1rem;border-radius:8px}
.nav-section ol{padding-left:1.25rem;color:#94a3b8;font-size:0.9rem}
.nav-section li{margin-bottom:4px}
footer{margin-top:2rem;padding-top:1rem;border-top:1px solid #1e293b;
text-align:center;color:#475569;font-size:0.8rem}
.footer-content{display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap}
.footer-sep{color:#334155}
@media print{
body{background:#fff;color:#1e293b;padding:1rem}
.section{background:#f8fafc;border:1px solid #e2e8f0}
.chart-panel,.stats-panel,.finding-card,.nav-section{background:#f1f5f9}
.grade-badge{print-color-adjust:exact;-webkit-print-color-adjust:exact}
.gauge-fill,.bar-fill,.conf-fill,.severity-badge{
print-color-adjust:exact;-webkit-print-color-adjust:exact}
h1,h2,.finding-title{color:#0f172a}
p,.finding-desc,.bar-label,.gauge-label{color:#334155}
}
@media(max-width:640px){
.dashboard-grid{grid-template-columns:1fr}
.grade-row{flex-direction:column;align-items:flex-start}
.header-top{flex-direction:column}
}
"""


# ─── Utilities ─────────────────────────────────────────────────────


def _esc(text: str) -> str:
    """HTML-escape text for safe embedding."""
    return html.escape(str(text)) if text else ""
