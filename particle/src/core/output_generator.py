#!/usr/bin/env python3
"""
Unified output generator for Collider.

Emits the LLM-oriented JSON output and the human-facing HTML report.
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

_FINE_GRAINED_ROLES = {"function", "method", "variable", "property", "parameter"}


def create_lod_payloads(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    import copy

    # LOD 1: Verbose (Raw stripped payload)
    lod1 = payload

    # LOD 2: Standard -- structural analyst view
    # Keep: node identity, graph metrics, classifications, edges, summaries
    # Drop: raw source text, heavy per-node analytics, heavy root sections
    lod2 = copy.deepcopy(payload)
    lod2 = _aggressively_strip_keys(lod2, {
        # Raw text (~9 MB)
        "code", "body_source", "body_preview",
        # Heavy per-node analytics (~18 MB combined)
        "waybill", "purpose_intelligence", "purpose_coherence",
        "control_flow", "data_flow", "intent_profile", "disconnection",
        "scope_analysis", "detected_atoms",
        # Heavy root sections (~12 MB combined)
        "markov", "ideome", "codome_boundaries",
    })

    # LOD 3: Compact (Remove fine-grained particles, keep files/classes/edges)
    lod3 = copy.deepcopy(payload)
    if "nodes" in lod3 and isinstance(lod3["nodes"], list):
        lod3["nodes"] = [
            node for node in lod3["nodes"]
            if isinstance(node, dict) and node.get("role") not in _FINE_GRAINED_ROLES
        ]

    # Strip all large string fields and heavy analytical objects
    lod3 = _aggressively_strip_keys(lod3, {
        # Raw text
        "code", "body_source", "body_preview", "docstring",
        "file_content", "source_code",
        # Heavy node metrics
        "dimensions", "waybill", "purpose_intelligence", "purpose_coherence",
        "control_flow", "data_flow", "rpbl", "intent_profile",
        # Heavy root arrays
        "markov", "execution_flow", "file_boundaries", "files", "igt",
        "semantic_analysis", "codome_boundaries",
    })

    return {"lod1": lod1, "lod2": lod2, "lod3": lod3}

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
    skip_html: bool = True,
    verbose_output: bool = False,
) -> Dict[str, Path]:
    if isinstance(data, dict):
        data = normalize_output(data)
        data = _strip_dead_output(data)

    if not json_filename or not html_filename:
        resolved_target = target_name or _resolve_target_name(data)
        json_filename, html_filename = _default_filenames(resolved_target, timestamp=timestamp)

    # Strip heavy fields before LOD creation
    payload = data.copy() if isinstance(data, dict) else data
    if isinstance(payload, dict):
        payload = _strip_heavy_waybill_fields(payload)

    # Create Multi-LOD outputs
    lods = create_lod_payloads(payload)
    output_dir = Path(output_dir)

    ans = {}
    tokens_info = {}
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
    except ImportError:
        enc = None

    _LOD_FILENAMES = {
        "lod1": "ast_lod1_verbose.json",
        "lod2": "ast_lod2_standard.json",
        "lod3": "ast_lod3_compact.json",
    }

    for level, data_lod in lods.items():
        # Skip LOD1 unless --verbose-output (saves ~60% disk + tokens)
        if level == "lod1" and not verbose_output:
            continue

        fname = _LOD_FILENAMES[level]
        out_path = output_dir / fname
        json_str = json.dumps(data_lod, indent=2, default=str, sort_keys=True)
        with open(out_path, "w") as f:
            f.write(json_str)
        ans[level] = out_path

        if enc:
            tokens_info[level] = len(enc.encode(json_str))

            if level == "lod3":
                breakdown = {}
                for k, v in data_lod.items():
                    try:
                        cat_str = json.dumps(v, default=str)
                        breakdown[k] = len(enc.encode(cat_str))
                    except Exception:
                        pass
                tokens_info["lod3_breakdown"] = breakdown

    if tokens_info:
        ans["tokens"] = tokens_info

    # Default output = LOD2 (standard); LOD1 only when --verbose-output
    default_lod = "lod1" if verbose_output else "lod2"
    default_path = ans[default_lod]

    # Maintain legacy aliases as symlinks (not copies)
    legacy_path = output_dir / json_filename
    stable_json = output_dir / "unified_analysis.json"
    for alias in [legacy_path, stable_json]:
        if alias.exists() or alias.is_symlink():
            alias.unlink()
        alias.symlink_to(default_path.name)  # relative symlink

    ans["llm"] = ans[default_lod]
    ans["stable_json"] = stable_json

    if not skip_html:
        html_path = write_html_report(data, output_dir, filename=html_filename, normalize=False)
        stable_html = output_dir / "collider_report.html"
        if stable_html.exists() or stable_html.is_symlink():
            stable_html.unlink()
        stable_html.symlink_to(html_path.name)
        ans["html"] = html_path
        ans["stable_html"] = stable_html

    # Emit Insights files if compiled_insights exists
    compiled = data.get("compiled_insights") if isinstance(data, dict) else None
    if compiled:
        # JSON
        insights_json_path = output_dir / "collider_insights.json"
        with open(insights_json_path, "w") as f:
            json.dump(compiled, f, indent=2, default=str)
        ans["insights_json"] = insights_json_path

        # Markdown (pre-generated by full_analysis.py)
        insights_md = data.get("_insights_markdown", "") if isinstance(data, dict) else ""
        if insights_md:
            insights_md_path = output_dir / "collider_insights.md"
            with open(insights_md_path, "w") as f:
                f.write(insights_md)
            ans["insights_md"] = insights_md_path

    return ans
