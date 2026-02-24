"""
Collider Bridge
===============
Shared utility for loading Collider insights across MCP, ACI, and boot.

Searches for collider_insights.json in:
1. .collider/collider_insights.json (default output dir)
2. Any --output dir that contains collider_insights.json
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional


def _find_insights_file(project_root: Path) -> Optional[Path]:
    """Find the most recent collider_insights.json.

    Search order:
    1. .collider/collider_insights.json
    2. /tmp/**/collider_insights.json (common --output target)
    """
    # Primary location
    primary = project_root / ".collider" / "collider_insights.json"
    if primary.exists():
        return primary

    # Check /tmp for recent outputs
    tmp = Path("/tmp")
    if tmp.exists():
        candidates = sorted(
            tmp.glob("**/collider_insights.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0]

    return None


def load_insights(project_root: Path) -> Optional[Dict]:
    """Load the latest collider_insights.json.

    Returns:
        Parsed insights dict, or None if no insights file exists.
    """
    path = _find_insights_file(project_root)
    if path is None:
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def insights_age_days(project_root: Path) -> Optional[float]:
    """Return the age of the insights file in days, or None if missing."""
    path = _find_insights_file(project_root)
    if path is None:
        return None

    mtime = path.stat().st_mtime
    age_seconds = time.time() - mtime
    return age_seconds / 86400


def insights_summary(insights: Dict) -> str:
    """One-line summary for logs/headers.

    Example: "Grade A (8.8/10) | 6 findings | CYCLIC_NETWORK"
    """
    grade = insights.get("grade", "?")
    score = insights.get("health_score", 0)
    count = insights.get("findings_count", 0)

    # Extract topology shape from navigation or findings
    topo = "unknown"
    for f in insights.get("findings", []):
        if f.get("category") == "topology":
            evidence = f.get("evidence", {})
            topo = evidence.get("shape", topo)
            break

    return f"Grade {grade} ({score}/10) | {count} findings | {topo}"


def insights_path(project_root: Path) -> Optional[Path]:
    """Return the path to the insights file, or None."""
    return _find_insights_file(project_root)


def load_insights_markdown(project_root: Path) -> Optional[str]:
    """Load the collider_insights.md markdown report.

    Searches same locations as JSON but for .md extension.
    """
    # Primary location
    primary = project_root / ".collider" / "collider_insights.md"
    if primary.exists():
        return primary.read_text()

    # Check /tmp
    tmp = Path("/tmp")
    if tmp.exists():
        candidates = sorted(
            tmp.glob("**/collider_insights.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0].read_text()

    return None
