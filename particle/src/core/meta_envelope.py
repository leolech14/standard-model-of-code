#!/usr/bin/env python3
"""
Meta-envelope builder for Collider output tiers.

Produces a standard identity + provenance block that is embedded in every
output tier, enabling cross-run joins for longitudinal (same repo over time)
and horizontal (cross-repo) meta-analysis.
"""

from __future__ import annotations

import hashlib
import json
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


SCHEMA_VERSION = "1.0.0"


def build_meta_envelope(
    full_output: Dict[str, Any],
    target: Path,
    options: Dict[str, Any],
) -> Dict[str, Any]:
    """Build standard identity envelope from pipeline output.

    Sources (all drawn from existing pipeline data):
        full_output["meta"]               → target, collider_version, analysis_time_ms
        full_output["counts"]             → node_count, edge_count, file_count
        full_output["stats"]              → language_distribution
        full_output["compiled_insights"]  → grade, health_score
        target (Path)                     → repo_id, target_path
        options (dict)                    → config_hash
    """
    meta = full_output.get("meta", {}) if isinstance(full_output, dict) else {}
    counts = full_output.get("counts", {}) if isinstance(full_output, dict) else {}
    stats = full_output.get("stats", {}) if isinstance(full_output, dict) else {}
    insights = full_output.get("compiled_insights", {}) if isinstance(full_output, dict) else {}

    # Stable repo identifier: hash of resolved target path
    target_str = str(target.resolve()) if target else "unknown"
    repo_id = hashlib.sha256(target_str.encode()).hexdigest()[:12]

    # Reproducibility marker: hash of sorted options dict
    config_hash = _hash_options(options)

    # Language mix from stats
    lang_dist = stats.get("language_distribution", {})
    if isinstance(lang_dist, dict):
        language_mix = {k: round(v, 4) if isinstance(v, float) else v
                        for k, v in lang_dist.items()}
    else:
        language_mix = {}

    return {
        "repo_id": repo_id,
        "run_id": str(uuid.uuid4()),
        "run_ts": datetime.now(timezone.utc).isoformat(),
        "collider_version": meta.get("version", "unknown"),
        "schema_version": SCHEMA_VERSION,
        "target": target.name if target else meta.get("target", "unknown"),
        "target_path": target_str,
        "node_count": counts.get("nodes", 0),
        "edge_count": counts.get("edges", 0),
        "file_count": counts.get("files", 0),
        "language_mix": language_mix,
        "analysis_time_ms": meta.get("analysis_time_ms", 0),
        "config_hash": config_hash,
        "hostname": socket.gethostname(),
        "grade": insights.get("grade", "?"),
        "health_score": round(insights.get("health_score", 0.0), 2),
    }


def _hash_options(options: Optional[Dict[str, Any]]) -> str:
    """Hash sorted options dict for reproducibility tracking."""
    if not options:
        return "00000000"
    try:
        canonical = json.dumps(options, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()[:8]
    except (TypeError, ValueError):
        return "00000000"


def append_to_meta_index(
    meta_envelope: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Append meta_envelope as one JSON line to the per-repo meta index.

    File: <output_dir>/meta_index.jsonl
    Each line is a self-contained JSON object (one per Collider run).
    """
    index_path = output_dir / "meta_index.jsonl"
    line = json.dumps(meta_envelope, default=str, sort_keys=True)
    with open(index_path, "a") as f:
        f.write(line + "\n")
    return index_path
