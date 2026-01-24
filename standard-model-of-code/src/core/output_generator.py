#!/usr/bin/env python3
"""
Unified output generator for Collider.

Emits the LLM-oriented JSON output and the human-facing HTML report.
"""

from __future__ import annotations

import json
import importlib.util
import re
import shutil
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

    output_path = output_dir / filename
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, default=str, sort_keys=True)
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


def generate_outputs(
    data: Dict[str, Any],
    output_dir: Union[str, Path],
    json_filename: Optional[str] = None,
    html_filename: Optional[str] = None,
    target_name: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Path]:
    if isinstance(data, dict):
        data = normalize_output(data)

    if not json_filename or not html_filename:
        resolved_target = target_name or _resolve_target_name(data)
        json_filename, html_filename = _default_filenames(resolved_target, timestamp=timestamp)

    json_path = write_llm_output(data, output_dir, filename=json_filename, normalize=False)
    html_path = write_html_report(data, output_dir, filename=html_filename, normalize=False)

    # Create stable filenames for automation (always available, always current)
    output_dir = Path(output_dir)
    stable_json = output_dir / "unified_analysis.json"
    stable_html = output_dir / "collider_report.html"

    # Copy to stable filenames (not symlink - works across filesystems)
    shutil.copy2(json_path, stable_json)
    shutil.copy2(html_path, stable_html)

    return {"llm": json_path, "html": html_path, "stable_json": stable_json, "stable_html": stable_html}
