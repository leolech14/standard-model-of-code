#!/usr/bin/env python3
"""
Unified output generator for Collider.

Emits three purpose-driven tiers:
    Tier 1: Raw verification  (collider_raw.json)   — complete machine-readable data
    Tier 2: AI briefing        (collider_briefing.json) — <4K token compact intelligence
    Tier 3: Human report       (collider_report.html)   — self-contained narrative HTML
"""

from __future__ import annotations

import json
import importlib.util
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from src.core.normalize_output import normalize_output

def _load_webgl_generator():
    viz_path = Path(__file__).parent.parent.parent / "tools" / "visualize_graph_webgl.py"
    if not viz_path.exists():
        raise FileNotFoundError(f"WebGL generator not found at {viz_path}")

    spec = importlib.util.spec_from_file_location("visualize_graph_webgl", viz_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError("Unable to load WebGL generator module")
    spec.loader.exec_module(module)
    return module


def _slugify(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower())
    safe = safe.strip("-")
    return safe or "unknown"


def _resolve_target_name(data: Dict[str, Any]) -> str:
    meta = data.get("meta", {}) if isinstance(data, dict) else {}
    target = meta.get("target") or data.get("target_path") or data.get("target_name")
    if target:
        return Path(str(target)).name
    return "unknown"


def _default_filenames(target_name: str, timestamp: Optional[str] = None) -> Tuple[str, str]:
    ts = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(target_name)
    return (
        f"output_llm-oriented_{slug}_{ts}.json",
        f"output_human-readable_{slug}_{ts}.html",
    )


def _strip_heavy_waybill_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Strip context_vector and route from waybill at all levels."""
    payload.pop("brain_download", None)

    if "manifest" in payload and isinstance(payload["manifest"], dict):
        wb = payload["manifest"].get("waybill")
        if isinstance(wb, dict):
            wb.pop("context_vector", None)
            wb.pop("route", None)

    # Strip from nodes (may be top-level or nested under data)
    nodes = payload.get("nodes", [])
    if not nodes and isinstance(payload.get("data"), dict):
        nodes = payload["data"].get("nodes", [])
    for node in nodes:
        if isinstance(node, dict) and "waybill" in node:
            node["waybill"].pop("context_vector", None)
            node["waybill"].pop("route", None)

    return payload


def write_llm_output(
    data: Dict[str, Any],
    output_dir: Union[str, Path],
    filename: str = "output_llm-oriented.json",
    normalize: bool = True,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if normalize and isinstance(data, dict):
        data = normalize_output(data)

    payload = data.copy() if isinstance(data, dict) else data
    if isinstance(payload, dict):
        payload = _strip_heavy_waybill_fields(payload)

    output_path = output_dir / filename
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2, default=str, sort_keys=True)
    return output_path


def write_html_report(
    data_or_path: Union[Dict[str, Any], str, Path],
    output_dir: Union[str, Path],
    filename: str = "output_human-readable.html",
    normalize: bool = True,
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if normalize and isinstance(data_or_path, dict):
        data_or_path = normalize_output(data_or_path)

    output_path = output_dir / filename
    webgl = _load_webgl_generator()
    webgl.generate_webgl_html(data_or_path, output_path)
    return output_path


def _aggressively_strip_keys(obj: Any, keys_to_remove: set) -> Any:
    """Recursively strip specified keys from any dict or list, regardless of depth."""
    if isinstance(obj, dict):
        return {k: _aggressively_strip_keys(v, keys_to_remove)
                for k, v in obj.items() if k not in keys_to_remove}
    elif isinstance(obj, list):
        return [_aggressively_strip_keys(item, keys_to_remove) for item in obj]
    return obj


def _strip_dead_output(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove empty/stub sections and redundant node fields from output.

    Targets three categories:
    1. Root sections that are always empty (dead features)
    2. Per-node fields that are always None/empty
    3. Per-node fields that duplicate other fields (verified 99.95%+ identical)
    """
    # --- Ephemeral / internal keys ---
    data.pop("_chemistry_lab", None)
    data.pop("_insights_markdown", None)

    # --- Dead root sections (#8-10) ---
    for key in ("ecosystem_discovery", "orphan_integration", "recommendations"):
        val = data.get(key)
        if not val or val == {} or val == []:
            data.pop(key, None)

    # --- Per-node cleanup (#14-15) ---
    for node in data.get("nodes", []):
        if not isinstance(node, dict):
            continue

        # Always-empty fields
        if node.get("ring") is None:
            node.pop("ring", None)
        if node.get("metadata") == {}:
            node.pop("metadata", None)

        # Redundant confidence aliases:
        #   confidence == role_confidence (99.95%), confidence_raw == role_confidence_raw (100%)
        # Keep: role_confidence (canonical, used by DB mapper + scripts).
        # Drop: confidence, confidence_raw (aliases added by unified_analysis.py)
        node.pop("confidence", None)
        node.pop("confidence_raw", None)

        # Redundant RPBL scalars: rpbl_boundary/purity/lifecycle/responsibility
        # duplicate rpbl dict values (99.95%)
        # Keep: rpbl dict. Drop: rpbl_* scalars
        for dim in ("rpbl_responsibility", "rpbl_purity", "rpbl_boundary", "rpbl_lifecycle"):
            node.pop(dim, None)

    return data


def generate_outputs(
    data: Dict[str, Any],
    output_dir: Union[str, Path],
    json_filename: Optional[str] = None,
    html_filename: Optional[str] = None,
    target_name: Optional[str] = None,
    timestamp: Optional[str] = None,
    skip_html: bool = False,
    verbose_output: bool = False,
    meta_envelope: Optional[Dict[str, Any]] = None,
    webgl: bool = False,
) -> Dict[str, Path]:
    """Generate three-tier output suite.

    Tier 1: collider_raw.json       — complete data for verification + CI
    Tier 2: collider_briefing.json  — <4K token AI briefing
    Tier 3: collider_report.html    — self-contained narrative HTML report

    Plus: backward-compat symlinks, insights files, optional WebGL, meta-index.
    """
    if isinstance(data, dict):
        data = normalize_output(data)
        data = _strip_dead_output(data)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ans: Dict[str, Any] = {}
    tokens_info: Dict[str, Any] = {}

    # Tokenizer (optional, for budget reporting)
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        enc = None

    # ── Tier 1: Raw Verification (collider_raw.json) ──────────────────
    payload = data.copy() if isinstance(data, dict) else data
    if isinstance(payload, dict):
        payload = _strip_heavy_waybill_fields(payload)
        if meta_envelope:
            payload["meta_envelope"] = meta_envelope

    raw_path = output_dir / "collider_raw.json"
    raw_json_str = json.dumps(payload, indent=2, default=str, sort_keys=True)
    with open(raw_path, "w") as f:
        f.write(raw_json_str)
    ans["raw"] = raw_path
    ans["llm"] = raw_path  # backward-compat key

    if enc:
        tokens_info["tier1_raw"] = len(enc.encode(raw_json_str))

    # Backward-compat symlinks: collider_output.json → collider_raw.json
    for symlink_name in ("collider_output.json", "unified_analysis.json"):
        sym = output_dir / symlink_name
        if sym.exists() or sym.is_symlink():
            sym.unlink()
        sym.symlink_to("collider_raw.json")
    ans["stable_json"] = output_dir / "unified_analysis.json"

    # ── Tier 2: AI Briefing (collider_briefing.json) ──────────────────
    compiled = data.get("compiled_insights") if isinstance(data, dict) else None
    if compiled and meta_envelope:
        try:
            from src.core.tier2_briefing import build_briefing
            briefing = build_briefing(compiled, data, meta_envelope)
            briefing_path = output_dir / "collider_briefing.json"
            briefing_json_str = json.dumps(briefing, indent=2, default=str, sort_keys=True)
            with open(briefing_path, "w") as f:
                f.write(briefing_json_str)
            ans["briefing"] = briefing_path

            if enc:
                tokens_info["tier2_briefing"] = len(enc.encode(briefing_json_str))
        except Exception as e:
            print(f"   ⚠️ Tier 2 briefing generation failed: {e}")

    # ── Tier 3: Human Report (collider_report.html) ───────────────────
    if compiled and meta_envelope and not skip_html:
        try:
            from src.core.tier3_html_report import build_html_report
            report_html = build_html_report(compiled, data, meta_envelope)
            report_path = output_dir / "collider_report.html"
            with open(report_path, "w") as f:
                f.write(report_html)
            ans["report_html"] = report_path
        except Exception as e:
            print(f"   ⚠️ Tier 3 report generation failed: {e}")

    # ── WebGL visualization (opt-in via --webgl) ──────────────────────
    if webgl and not skip_html:
        try:
            if not html_filename:
                resolved_target = target_name or _resolve_target_name(data)
                _, html_filename = _default_filenames(resolved_target, timestamp=timestamp)
            html_path = write_html_report(data, output_dir, filename=html_filename, normalize=False)
            ans["html"] = html_path
        except Exception as e:
            print(f"   ⚠️ WebGL visualization failed: {e}")

    # ── Token report ──────────────────────────────────────────────────
    if tokens_info:
        ans["tokens"] = tokens_info

    # ── Insights files (keep existing output for backward compat) ─────
    if compiled:
        # JSON
        insights_json_path = output_dir / "collider_insights.json"
        with open(insights_json_path, "w") as f:
            json.dump(compiled, f, indent=2, default=str)
        ans["insights_json"] = insights_json_path

        # Markdown (pre-generated in Stage 21)
        insights_md = data.get("_insights_markdown", "") if isinstance(data, dict) else ""
        if insights_md:
            insights_md_path = output_dir / "collider_insights.md"
            with open(insights_md_path, "w") as f:
                f.write(insights_md)
            ans["insights_md"] = insights_md_path

    # ── Meta-index (append-only JSONL for cross-run analysis) ─────────
    if meta_envelope:
        try:
            from src.core.meta_envelope import append_to_meta_index
            index_path = append_to_meta_index(meta_envelope, output_dir)
            ans["meta_index"] = index_path
        except Exception as e:
            print(f"   ⚠️ Meta-index append failed: {e}")

    return ans
