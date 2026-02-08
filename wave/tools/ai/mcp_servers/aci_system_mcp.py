"""
Adaptive Context Intelligence (ACI) MCP Server

Wraps the ACI query routing, context building, and refinery systems
as MCP tools for seamless AI agent access.

Server 2 of 3 in the intelligence MCP hybrid architecture.

Tools exposed:
  - aci_analyze_query: Parse query intent, complexity, and scope
  - aci_route_query: Route query to optimal execution tier
  - aci_analyze_and_route: Combined intent + routing in one call
  - aci_build_context: Build optimized context window for a query
  - aci_refine_files: Atomize files into RefineryNodes
  - aci_semantic_match: Map query to Standard Model semantic space
  - aci_list_analysis_sets: List available analysis sets
  - aci_run_analysis: Full analysis pipeline (route + build + execute)
"""

import sys
import os
import json
import dataclasses
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

# Resolve paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
TOOLS_DIR = PROJECT_ROOT / "wave" / "tools" / "ai"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(PROJECT_ROOT / "wave" / "tools"))


# --- Server ---

mcp = FastMCP(
    "AdaptiveContextIntelligence",
    version="1.0.0",
    instructions=(
        "Adaptive Context Intelligence (ACI) - the 'Curriculum Compiler'. "
        "Routes queries to optimal AI execution tiers, builds optimized context "
        "windows, and atomizes code into searchable RefineryNodes. "
        f"Operates on PROJECT_elements at {PROJECT_ROOT}."
    ),
)


# Helper to serialize dataclasses/enums
def _serialize(obj):
    """JSON-safe serialization for dataclasses and enums."""
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if hasattr(obj, "name"):  # Enum
        return obj.name
    if hasattr(obj, "value"):
        return obj.value
    return str(obj)


# ─────────────────────────────────────────────
# QUERY UNDERSTANDING
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def aci_analyze_query(query: str) -> str:
    """Parse a query into structured intent, complexity, and scope.

    Classifies the query intent (ARCHITECTURE, DEBUG, RESEARCH, etc.),
    complexity (SIMPLE, MODERATE, COMPLEX), and scope (INTERNAL, EXTERNAL, HYBRID).
    Also extracts keywords and suggests analysis sets.

    Args:
        query: The natural language query to analyze

    Returns:
        JSON with intent, complexity, scope, keywords, and suggested_sets
    """
    from aci.intent_parser import analyze_query

    profile = analyze_query(query)
    return json.dumps({
        "intent": profile.intent.name,
        "complexity": profile.complexity.name,
        "scope": profile.scope.name,
        "keywords": profile.keywords,
        "suggested_sets": getattr(profile, "suggested_sets", []),
        "is_agent_query": getattr(profile, "is_agent", False),
        "is_external": getattr(profile, "is_external", False),
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def aci_route_query(query: str, force_tier: str = "") -> str:
    """Route a query to the optimal execution tier.

    Determines which AI backend and context strategy to use:
    INSTANT (cached), CEREBRAS (fast), RAG (file search),
    LONG_CONTEXT (full reasoning), PERPLEXITY (web), FLASH_DEEP, HYBRID.

    Args:
        query: The query to route
        force_tier: Force a specific tier (optional)

    Returns:
        JSON with tier, primary_sets, fallback_tier, reasoning, context_flow
    """
    from aci.tier_orchestrator import route_query

    force = force_tier if force_tier else None
    route = route_query(query, force_tier=force)

    return json.dumps({
        "tier": route.tier.name,
        "primary_sets": route.primary_sets,
        "fallback_tier": route.fallback_tier.name if route.fallback_tier else None,
        "use_truths": route.use_truths,
        "inject_agent": route.inject_agent,
        "reasoning": route.reasoning,
        "context_flow": route.context_flow,
        "traversal_direction": str(route.traversal_direction) if route.traversal_direction else None,
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def aci_analyze_and_route(query: str) -> str:
    """Combined query analysis + routing in one call.

    Parses intent/complexity/scope, routes to tier, and returns
    the full decision context. Use this for complete query understanding.

    Args:
        query: The query to analyze and route

    Returns:
        JSON with intent analysis and routing decision
    """
    from aci.intent_parser import analyze_query
    from aci.tier_orchestrator import route_query

    profile = analyze_query(query)
    route = route_query(query)

    return json.dumps({
        "query": query,
        "intent": {
            "type": profile.intent.name,
            "complexity": profile.complexity.name,
            "scope": profile.scope.name,
            "keywords": profile.keywords,
        },
        "routing": {
            "tier": route.tier.name,
            "primary_sets": route.primary_sets,
            "fallback_tier": route.fallback_tier.name if route.fallback_tier else None,
            "reasoning": route.reasoning,
            "context_flow": route.context_flow,
        },
    }, default=str, indent=2)


# ─────────────────────────────────────────────
# SEMANTIC MATCHING
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def aci_semantic_match(query: str) -> str:
    """Map a query to the Standard Model of Code semantic space.

    Identifies the PURPOSE level (PI1-PI4), architectural LAYER,
    relevant ROLES, traversal DIRECTION, and suggested files/sets
    based on the Standard Model dimensions (D1-D8).

    Args:
        query: The query to map semantically

    Returns:
        JSON with semantic targets, suggested files, traversal strategy
    """
    from aci.semantic_finder import semantic_match

    match = semantic_match(query)
    return json.dumps(_serialize(match), default=str, indent=2)


# ─────────────────────────────────────────────
# CONTEXT BUILDING
# ─────────────────────────────────────────────

@mcp.tool(annotations={"readOnlyHint": True})
def aci_list_analysis_sets() -> str:
    """List all available analysis sets with their descriptions and token budgets.

    Analysis sets are named groups of files for AI context injection.
    Examples: 'brain' (AI tools), 'body' (Collider), 'theory' (Standard Model).

    Returns:
        JSON with set names, descriptions, file counts, and token budgets
    """
    import yaml

    sets_path = PROJECT_ROOT / "wave" / "config" / "analysis_sets.yaml"
    if not sets_path.exists():
        return json.dumps({"error": "analysis_sets.yaml not found"})

    with open(sets_path) as f:
        config = yaml.safe_load(f)

    sets_info = {}
    for name, spec in config.get("analysis_sets", config.get("sets", {})).items():
        sets_info[name] = {
            "description": spec.get("description", ""),
            "max_tokens": spec.get("max_tokens", "unlimited"),
            "includes": spec.get("includes", [])[:3],
            "positional_strategy": spec.get("positional_strategy", "default"),
        }

    return json.dumps({
        "total_sets": len(sets_info),
        "sets": sets_info,
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": True})
def aci_refine_files(file_paths: list[str], chunk_type: str = "auto") -> str:
    """Atomize files into RefineryNodes (semantic chunks).

    Breaks files into atomic, searchable chunks using language-aware
    chunking (Python: functions/classes, Markdown: headings, YAML: keys).
    Each chunk gets a SHA256 ID, relevance score, and metadata.

    Args:
        file_paths: List of files to refine (absolute or relative to project)
        chunk_type: Chunking strategy - auto, function, class, heading (default: auto)

    Returns:
        JSON with chunks (content, type, relevance, source location)
    """
    from aci.refinery import Refinery

    paths = []
    for fp in file_paths:
        p = Path(fp)
        if not p.is_absolute():
            p = PROJECT_ROOT / fp
        if p.exists():
            paths.append(p)

    if not paths:
        return json.dumps({"error": "No valid files found"})

    refinery = Refinery()
    all_nodes = []

    for path in paths[:10]:  # Cap at 10 files to stay under response limit
        try:
            nodes = refinery.process_file(path)
            for node in nodes:
                all_nodes.append({
                    "chunk_id": node.chunk_id,
                    "chunk_type": node.chunk_type,
                    "source_file": str(node.source_file),
                    "start_line": node.start_line,
                    "end_line": node.end_line,
                    "relevance_score": node.relevance_score,
                    "content_preview": node.content[:200] + "..." if len(node.content) > 200 else node.content,
                    "token_estimate": len(node.content) // 4,
                })
        except Exception as e:
            all_nodes.append({"error": str(e), "file": str(path)})

    return json.dumps({
        "total_chunks": len(all_nodes),
        "files_processed": len(paths),
        "chunks": all_nodes,
    }, default=str, indent=2)


@mcp.tool(annotations={"readOnlyHint": False})
def aci_run_analysis(
    query: str,
    analysis_set: str = "",
    max_files: int = 50,
    force: bool = False
) -> str:
    """Run the full ACI analysis pipeline on a query.

    Routes the query, builds context, and executes via the appropriate
    AI backend (Gemini, Cerebras, or Perplexity). This is the main
    entry point for intelligent codebase analysis.

    Args:
        query: The analysis question
        analysis_set: Force a specific analysis set (optional, ACI auto-selects)
        max_files: Maximum files to include in context (default: 50)
        force: Force execution even if over token budget

    Returns:
        JSON with analysis result, routing info, and token usage
    """
    import subprocess

    cmd = [
        "python3", str(TOOLS_DIR / "analyze.py"),
        "--aci" if not analysis_set else f"--set", analysis_set or "__skip__",
        "--max-files", str(max_files),
    ]

    # Clean up command
    if analysis_set:
        cmd = ["python3", str(TOOLS_DIR / "analyze.py"), "--set", analysis_set, "--max-files", str(max_files)]
    else:
        cmd = ["python3", str(TOOLS_DIR / "analyze.py"), "--aci", "--max-files", str(max_files)]

    if force:
        cmd.append("--force")
    cmd.append(query)

    result = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=300,
        cwd=str(PROJECT_ROOT),
        env={**os.environ}
    )

    output = result.stdout
    if result.returncode != 0 and result.stderr:
        output += "\n\nSTDERR:\n" + result.stderr[-500:]

    # Truncate if too large for MCP response
    if len(output) > 9000:
        output = output[:4000] + "\n\n... [truncated] ...\n\n" + output[-4000:]

    return json.dumps({
        "status": "complete" if result.returncode == 0 else "error",
        "output": output,
    }, indent=2)


# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

@mcp.resource("aci://config")
def aci_config() -> str:
    """The ACI configuration (tiers, token budgets, intent keywords)."""
    config_path = PROJECT_ROOT / "wave" / "config" / "aci_config.yaml"
    if config_path.exists():
        return config_path.read_text()
    return "ACI config not found."


@mcp.resource("aci://tiers")
def tier_info() -> str:
    """Execution tier descriptions and routing rules."""
    from aci.tier_orchestrator import Tier
    tiers = {t.name: t.value for t in Tier}
    return json.dumps(tiers, indent=2)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
