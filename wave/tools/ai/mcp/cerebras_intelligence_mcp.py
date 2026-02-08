"""
Cerebras Intelligence MCP Server

Wraps the Cerebras-powered tools + Perplexity research + token utilities
as MCP tools for seamless AI agent access.

Server 1 of 3 in the intelligence MCP hybrid architecture.

Tools exposed:
  - cerebras_query: Direct LLM query at 3000 t/s
  - cerebras_analyze_file: Analyze a single file for purpose/deps/gaps
  - cerebras_tag_file: Classify file into D1-D8 dimensions
  - cerebras_sweep_directory: Generate context for an entire directory
  - cerebras_detect_gaps: Find architectural gaps from cached intel
  - perplexity_research: Web research with citations
  - estimate_tokens: Smart token estimation for files
  - check_token_budget: Validate files against token budget
  - get_project_health: System health and alerts
  - get_project_context: Formatted context for AI injection
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

# Resolve project root and add tools to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
TOOLS_DIR = PROJECT_ROOT / "wave" / "tools" / "ai"
sys.path.insert(0, str(TOOLS_DIR))

# Ensure Doppler secrets are available (fallback to env vars)
def _get_api_key(name: str) -> Optional[str]:
    """Get API key from environment or Doppler."""
    key = os.getenv(name)
    if key:
        return key
    try:
        import subprocess
        result = subprocess.run(
            ["doppler", "secrets", "get", name, "--plain"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


# --- Server ---

mcp = FastMCP(
    "CerebrasIntelligence",
    version="1.0.0",
    instructions=(
        "Fast intelligence tools powered by Cerebras (3000 t/s), "
        "Perplexity (web research), and local utilities. "
        "All tools operate on the PROJECT_elements codebase at "
        f"{PROJECT_ROOT}. Use cerebras_query for fast semantic questions, "
        "perplexity_research for web-sourced answers, and estimate_tokens "
        "before loading large context windows."
    ),
)


# ─────────────────────────────────────────────
# CEREBRAS TOOLS
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def cerebras_query(prompt: str, system_prompt: str = "", max_tokens: int = 1000) -> str:
    """Send a query to Cerebras LLM at 3000 tokens/sec.

    Fast semantic analysis for quick questions about code, architecture,
    or any text. Uses llama-3.3-70b by default.

    Args:
        prompt: The question or analysis prompt
        system_prompt: Optional system context
        max_tokens: Maximum response length (default 1000)

    Returns:
        Model response text
    """
    from cerebras_rapid_intel import cerebras_query as _query
    return _query(prompt, system_prompt, max_tokens)


@mcp.tool(annotations={"readOnlyHint": True})
def cerebras_analyze_file(file_path: str) -> str:
    """Analyze a single file with Cerebras to extract intelligence.

    Returns purpose, summary, key concepts, dependencies, exports,
    gaps, and quality score for the file.

    Args:
        file_path: Path to file (absolute or relative to project root)

    Returns:
        JSON string with file intelligence
    """
    from cerebras_rapid_intel import analyze_file as _analyze
    import dataclasses

    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        return json.dumps({"error": f"File not found: {path}"})

    result = _analyze(path)
    if result is None:
        return json.dumps({"error": f"Analysis failed for {path}"})

    return json.dumps(dataclasses.asdict(result), default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def cerebras_tag_file(file_path: str) -> str:
    """Classify a file into D1-D8 Standard Model dimensions.

    Tags a file with its architectural role (SCRIPT, SERVICE, CONTROLLER, etc.)
    and layer (APPLICATION, INFRASTRUCTURE, DOMAIN, etc.) using Cerebras.

    Args:
        file_path: Path to file to classify

    Returns:
        JSON string with dimensional classification and confidence
    """
    from cerebras_tagger import classify_file_cerebras as _classify
    import dataclasses

    api_key = _get_api_key("CEREBRAS_API_KEY")
    if not api_key:
        return json.dumps({"error": "CEREBRAS_API_KEY not available"})

    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        return json.dumps({"error": f"File not found: {path}"})

    result = _classify(path, api_key)
    if result is None:
        return json.dumps({"error": f"Classification failed for {path}"})

    return json.dumps(dataclasses.asdict(result), default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def cerebras_sweep_directory(directory: str = "wave/tools/ai/") -> str:
    """Generate rich context for all files in a directory using Cerebras.

    Scans all files, analyzes each with Cerebras, and produces a
    structured context document. Results are cached by file hash.

    Args:
        directory: Directory to sweep (relative to project root)

    Returns:
        Summary with file count, cache stats, and output path
    """
    import subprocess

    dir_path = Path(directory)
    if not dir_path.is_absolute():
        dir_path = PROJECT_ROOT / directory

    if not dir_path.is_dir():
        return json.dumps({"error": f"Not a directory: {dir_path}"})

    result = subprocess.run(
        ["python3", str(TOOLS_DIR / "cerebras_rapid_intel.py"), "context", str(dir_path)],
        capture_output=True, text=True, timeout=600,
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "CEREBRAS_API_KEY": _get_api_key("CEREBRAS_API_KEY") or ""}
    )

    if result.returncode != 0:
        return json.dumps({"error": result.stderr[-500:] if result.stderr else "Unknown error"})

    # Extract key info from output
    lines = result.stdout.strip().split("\n")
    output_path = ""
    for line in lines:
        if "Saved to:" in line:
            output_path = line.split("Saved to:")[-1].strip()

    return json.dumps({
        "status": "complete",
        "directory": str(dir_path),
        "output": output_path,
        "summary": "\n".join(lines[-5:])
    }, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def cerebras_detect_gaps() -> str:
    """Detect architectural gaps from cached intelligence data.

    Uses the rapid intel cache to find missing docs, broken links,
    incomplete implementations, and other issues.

    Returns:
        JSON with gap count, severity distribution, and top gaps
    """
    from cerebras_rapid_intel import detect_gaps as _gaps
    import dataclasses

    cache_path = PROJECT_ROOT / "wave" / "data" / "intel" / "file_intel_cache.json"
    if not cache_path.exists():
        return json.dumps({"error": "No intel cache. Run cerebras_sweep_directory first."})

    with open(cache_path) as f:
        cache = json.load(f)

    # Reconstruct FileIntel objects from cache
    from cerebras_rapid_intel import FileIntel
    intel_map = {}
    for rel_path, data in cache.items():
        try:
            intel_map[rel_path] = FileIntel(**data)
        except Exception:
            continue

    gaps = _gaps(intel_map)
    gap_dicts = [dataclasses.asdict(g) for g in gaps[:50]]  # Top 50

    severity_dist = {}
    for g in gaps:
        severity_dist[g.severity] = severity_dist.get(g.severity, 0) + 1

    return json.dumps({
        "total_gaps": len(gaps),
        "severity_distribution": severity_dist,
        "top_gaps": gap_dicts
    }, default=str, indent=2)


# ─────────────────────────────────────────────
# PERPLEXITY RESEARCH
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def perplexity_research(
    query: str,
    model: str = "sonar-pro",
    save: bool = True
) -> str:
    """Research a topic using Perplexity with web citations.

    Models: sonar (fast), sonar-pro (detailed), sonar-reasoning (analytical),
    sonar-deep-research (comprehensive multi-step).

    Args:
        query: The research question
        model: Perplexity model (default: sonar-pro)
        save: Auto-save result to research directory (default: True)

    Returns:
        JSON with content, citations, and usage stats
    """
    from perplexity_research import research as _research

    try:
        result = _research(query, model=model)
    except Exception as e:
        return json.dumps({"error": str(e)})

    if save and result.get("content"):
        try:
            from perplexity_research import auto_save_research
            saved = auto_save_research(query, result, model)
            result["saved_to"] = str(saved)
        except Exception:
            pass

    return json.dumps(result, default=str, indent=2)


# ─────────────────────────────────────────────
# TOKEN UTILITIES
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def estimate_tokens(file_paths: list[str], method: str = "smart") -> str:
    """Estimate token count for a list of files.

    Methods: fast (±50%, file size), medium (±20%, char count),
    accurate (±5%, tiktoken), smart (auto-select).

    Args:
        file_paths: List of file paths (absolute or relative to project root)
        method: Estimation method (default: smart)

    Returns:
        JSON with token count, method used, and per-file breakdown
    """
    from token_estimator import (
        estimate_tokens_fast,
        estimate_tokens_medium,
        estimate_tokens_accurate,
        estimate_tokens_smart,
        get_file_token_breakdown,
    )

    paths = []
    for fp in file_paths:
        p = Path(fp)
        if not p.is_absolute():
            p = PROJECT_ROOT / fp
        if p.exists():
            paths.append(p)

    if not paths:
        return json.dumps({"error": "No valid files found"})

    if method == "fast":
        tokens = estimate_tokens_fast(paths)
        result = {"tokens": tokens, "method": "fast", "accuracy": "±50%"}
    elif method == "medium":
        tokens = estimate_tokens_medium(paths)
        result = {"tokens": tokens, "method": "medium", "accuracy": "±20%"}
    elif method == "accurate":
        tokens = estimate_tokens_accurate(paths)
        result = {"tokens": tokens, "method": "accurate", "accuracy": "±5%"}
    else:
        result = estimate_tokens_smart(paths)

    # Add breakdown for top files
    breakdown = get_file_token_breakdown(paths, top_n=10)
    result["top_files"] = breakdown
    result["file_count"] = len(paths)

    return json.dumps(result, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def check_token_budget(
    file_paths: list[str],
    max_budget: int = 200000,
    force: bool = False
) -> str:
    """Check if files fit within a token budget.

    Args:
        file_paths: List of file paths
        max_budget: Maximum token budget (default: 200000)
        force: Allow exceeding budget with warning (default: False)

    Returns:
        JSON with allowed status, token count, ratio, and formatted report
    """
    from token_estimator import check_budget, format_budget_report

    paths = []
    for fp in file_paths:
        p = Path(fp)
        if not p.is_absolute():
            p = PROJECT_ROOT / fp
        if p.exists():
            paths.append(p)

    if not paths:
        return json.dumps({"error": "No valid files found"})

    result = check_budget(paths, max_budget, force=force)
    result["report"] = format_budget_report(result)

    return json.dumps(result, default=str, indent=2)


# ─────────────────────────────────────────────
# PROJECT INTELLIGENCE
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def get_project_health() -> str:
    """Get project health status, meter readings, and active alerts.

    Returns system health (HEALTHY/DEGRADED/CRITICAL), alert list,
    and meter values (focus, reliability, discovery, debt, readiness).

    Returns:
        JSON with health status, alerts, and meters
    """
    from intel import get_health, get_alerts, get_deck

    health = get_health()
    alerts = get_alerts()
    deck_ctx = get_deck()

    return json.dumps({
        "health": health,
        "alerts": alerts,
        "meters": deck_ctx.get("meters", {}),
        "available_cards": deck_ctx.get("available_cards", 0),
        "recent_plays": deck_ctx.get("recent_plays", [])
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def get_project_context(
    context_set: str = "minimal",
    output_format: str = "yaml"
) -> str:
    """Get formatted project context for AI injection.

    Context sets: minimal (cheapest), deck (cards+meters),
    session (current work), truths (repo facts), full (everything).

    Args:
        context_set: Which context to load (default: minimal)
        output_format: Output format - yaml, json, or oneline

    Returns:
        Formatted context string ready for AI prompt injection
    """
    from intel import get_context

    return get_context(set_name=context_set, format=output_format)


# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

@mcp.resource("intelligence://architecture-map")
def architecture_map() -> str:
    """The unified architecture map of the AI toolkit."""
    map_path = TOOLS_DIR / ".research" / "ARCHITECTURE_MAP.md"
    if map_path.exists():
        return map_path.read_text()
    return "Architecture map not found. Run self-discovery first."


@mcp.resource("intelligence://analysis-sets")
def analysis_sets() -> str:
    """Available analysis sets for context loading."""
    sets_path = PROJECT_ROOT / "wave" / "config" / "analysis_sets.yaml"
    if sets_path.exists():
        return sets_path.read_text()
    return "Analysis sets config not found."


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
