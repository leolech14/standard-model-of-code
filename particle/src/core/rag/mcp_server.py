"""
Collider MCP Tool Server
========================
Exposes GraphRAG search, neighborhood, and architectural insights
as native MCP tools for AI agents.

Usage:
    # Start the server (stdio transport for IDE/agent integration)
    uv run python -m src.core.rag.mcp_server

    # Or via the CLI
    collider serve
"""
import json
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(
    "Collider",
    instructions="Standard Model of Code — Semantic search and graph traversal for any codebase. Use collider_search for natural language queries and collider_neighborhood for call graph exploration."
)

# Global retriever instance (loaded once, reused across tool calls)
_retriever = None
_db_dir = None

def _get_retriever(db_dir: str = None):
    """Lazily initialize the GraphRAGRetriever, loading the model only once."""
    global _retriever, _db_dir

    if db_dir:
        target = Path(db_dir)
    else:
        # Default: look for .collider directory relative to cwd
        target = Path.cwd() / ".collider"
        if not target.exists():
            target = Path.cwd() / "src" / ".collider"

    # Reuse if same directory
    if _retriever and str(_db_dir) == str(target):
        return _retriever

    from src.core.rag.retriever import GraphRAGRetriever
    _retriever = GraphRAGRetriever(target)
    _db_dir = target
    return _retriever


@mcp.tool()
def collider_search(query: str, limit: int = 5, db_dir: str = "") -> str:
    """
    Semantic search across the entire codebase AST.

    Finds the most relevant functions, methods, and classes matching a natural language query.
    Returns deduplicated results with source code snippets, file paths, and line ranges.

    Args:
        query: Natural language description of what you're looking for (e.g. "authentication middleware", "database connection handling")
        limit: Maximum number of results to return (default: 5)
        db_dir: Path to the .collider directory. Leave empty to auto-detect.

    Returns:
        JSON array of matching code nodes with source snippets
    """
    retriever = _get_retriever(db_dir if db_dir else None)
    results = retriever.search(query, limit=limit)

    # Clean results for JSON serialization (remove numpy vectors)
    clean = []
    for r in results:
        clean.append({
            "name": r.get("name", ""),
            "type": r.get("type", r.get("kind", "")),
            "file_path": r.get("file_path", ""),
            "start_line": r.get("start_line"),
            "end_line": r.get("end_line"),
            "distance": r.get("_distance"),
            "code_snippet": r.get("code_snippet", ""),
        })

    return json.dumps(clean, indent=2)


@mcp.tool()
def collider_neighborhood(node_id: str, depth: int = 1, db_dir: str = "") -> str:
    """
    Graph traversal to find all callers and dependencies of a specific code node.

    Given a node ID (returned from collider_search), returns the neighborhood:
    - Callers: functions/methods that call this node
    - Dependencies: functions/methods this node calls

    Args:
        node_id: The node identifier (format: "filepath:function_name", e.g. "/path/to/file.py:my_function")
        depth: How many hops to traverse (default: 1, currently only depth=1 is supported)
        db_dir: Path to the .collider directory. Leave empty to auto-detect.

    Returns:
        JSON object with focal_node, callers, dependencies, and hydrated node details
    """
    retriever = _get_retriever(db_dir if db_dir else None)
    data = retriever.neighborhood(node_id, depth=depth)
    return json.dumps(data, indent=2)


@mcp.tool()
def collider_inspect_node(node_id: str, db_dir: str = "") -> str:
    """
    The "Getter" for the Node-Level AI Playground.

    Extracts the exact code snippet for a specific AST node. Use this to inspect
    a single function or class before executing a surgical mutation via collider_mutate.

    Args:
        node_id: The node identifier (returned from collider_search or collider_insights)
        db_dir: Path to the .collider directory. Leave empty to auto-detect.

    Returns:
        JSON payload containing the exact source code snippet, line ranges, and a mutation template.
    """
    import sqlite3

    retriever = _get_retriever(db_dir if db_dir else None)
    db_path = retriever.sql_db_path

    if not db_path.exists():
        return json.dumps({"error": "No collider.db found. Run `collider full <path>` first."})

    run_id = retriever._get_latest_run_id()
    conn = sqlite3.connect(db_path)

    query = "SELECT name, kind, file_path, start_line, end_line FROM nodes WHERE id = ?"
    params = [node_id]
    if run_id:
        query += " AND run_id = ?"
        params.append(run_id)
    query += " LIMIT 1"

    row = conn.execute(query, params).fetchone()
    conn.close()

    if not row:
        return json.dumps({"error": f"Node '{node_id}' not found in the graph database."})

    name, kind, file_path, start_line, end_line = row

    if not start_line or not end_line:
         return json.dumps({"error": f"Node '{node_id}' does not have line-level boundaries recorded."})

    # Read the exact snippet from disk
    snippet = retriever._read_source_snippet(file_path, start_line, end_line)

    payload = {
        "node_id": node_id,
        "name": name,
        "kind": kind,
        "file_path": file_path,
        "line_range": [start_line, end_line],
        "source_code_snippet": snippet,
        "playground_instructions": {
            "target_file": file_path,
            "mutation_template": {
                "action": "replace_function_body" if kind in ('function', 'method') else "replace_class_body",
                "target_node": name,
                "new_body": "Write the complete new Python definition here. Do NOT use markdown code blocks."
            }
        }
    }

    return json.dumps(payload, indent=2)


@mcp.tool()
def collider_overview(db_dir: str = "") -> str:
    """
    Get a high-level overview of the indexed codebase.

    Returns the total number of indexed nodes, the latest analysis run ID,
    and summary statistics about the codebase structure.

    Args:
        db_dir: Path to the .collider directory. Leave empty to auto-detect.

    Returns:
        JSON object with codebase statistics
    """
    import sqlite3

    retriever = _get_retriever(db_dir if db_dir else None)
    db_path = retriever.sql_db_path

    if not db_path.exists():
        return json.dumps({"error": "No collider.db found. Run `collider full <path>` first."})

    conn = sqlite3.connect(db_path)

    run_id = retriever._get_latest_run_id()

    total_nodes = conn.execute("SELECT COUNT(*) FROM nodes WHERE run_id = ?", (run_id,)).fetchone()[0]
    total_edges = conn.execute("SELECT COUNT(*) FROM edges WHERE run_id = ?", (run_id,)).fetchone()[0]

    # Get kind distribution
    kinds = conn.execute(
        "SELECT kind, COUNT(*) FROM nodes WHERE run_id = ? GROUP BY kind ORDER BY COUNT(*) DESC",
        (run_id,)
    ).fetchall()

    # Get top-level files
    files = conn.execute(
        "SELECT DISTINCT file_path FROM nodes WHERE run_id = ? AND kind IN ('module', 'file')",
        (run_id,)
    ).fetchall()

    conn.close()

    return json.dumps({
        "run_id": run_id,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "node_kinds": {k: c for k, c in kinds},
        "indexed_files": len(files),
    }, indent=2)


@mcp.tool()
def collider_mutate(target_file: str, mutations_json: str) -> str:
    """
    Applies JSON-formatted AST mutations to a target file and writes the result back to disk.

    Args:
        target_file: Absolute path to the file to mutate.
        mutations_json: JSON string representing the mutations array, e.g.,
                        [{"action": "replace_function_body", "target_node": "my_func", "new_body": "def my_func():..."}]

    Returns:
        JSON string confirming success or describing the error.
    """
    from src.core.synthesis.compiler import ColliderCompiler

    path = Path(target_file)
    if not path.exists():
        return json.dumps({"error": f"File not found: {target_file}"})

    try:
        source_code = path.read_text(encoding="utf-8")

        # Parse mutations_json if it's a string
        import json
        mutations_list = json.loads(mutations_json) if isinstance(mutations_json, str) else mutations_json

        # Build the proper payload expected by apply_mutations
        request_obj = {
            "target_file": target_file,
            "mutations": mutations_list
        }

        modified_code = ColliderCompiler.apply_mutations(source_code, request_obj)

        # Write back to disk
        path.write_text(modified_code, encoding="utf-8")

        return json.dumps({"success": True, "message": f"Successfully mutated {target_file}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─────────────────────────────────────────────
# INSIGHTS (Architectural Health)
# ─────────────────────────────────────────────

def _find_insights_json(db_dir: str = "") -> Path | None:
    """Find the collider_insights.json file."""
    if db_dir:
        candidate = Path(db_dir) / "collider_insights.json"
        if candidate.exists():
            return candidate

    # Default: .collider in cwd
    candidate = Path.cwd() / ".collider" / "collider_insights.json"
    if candidate.exists():
        return candidate

    # Fallback: /tmp outputs
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


def _format_insights_markdown(data: dict) -> str:
    """Formats raw Collider insights JSON into an actionable Markdown digest."""
    grade = data.get("grade", "?")
    score = data.get("health_score", 0.0)

    findings = data.get("findings", [])
    q_score_str = "Unknown"
    for f in findings:
        if f.get("category") == "purpose" and "codebase_intelligence" in f.get("evidence", {}):
            q = f["evidence"]["codebase_intelligence"]
            interp = f["evidence"].get("interpretation", "")
            q_score_str = f"{q} {f'({interp})' if interp else ''}"
            break

    meta = data.get("meta", {})
    nodes = meta.get("nodes_analyzed", "Unknown")
    edges = meta.get("edges_analyzed", "Unknown")

    lines = [
        "# Collider Intelligence Digest",
        "",
        "This document provides a highly structured, immediate visualization of the repository's semantic and topological state.",
        "",
        "## 1. System State & Numbers",
        "",
        f"**Overall Grade:** {grade}",
        f"**Codebase Health:** {score} / 10",
        f"**Codebase Intelligence (Q-Score):** {q_score_str}",
        "",
        "| Metric | Count |",
        "| :--- | :--- |",
        f"| **Total Nodes** | {nodes} |",
        f"| **Total Edges** | {edges} |",
        ""
    ]

    components = data.get("health_components", {})
    if components:
        lines.append("### Health Components Breakdown")
        for k, v in sorted(components.items()):
            name = k.replace("_", " ").title()
            lines.append(f"- {name}: {v} / 10")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 2. Actionable Insights & The \"Why\"")
    lines.append("")

    counts = data.get("findings_by_severity", {})
    total_findings = sum(counts.values()) if counts else len(findings)
    counts_str = ", ".join(f"{v} {k.title()}" for k, v in counts.items() if v > 0)
    lines.append(f"The Collider identified **{total_findings} total findings** ({counts_str}). Below are the specific actions to be taken, prioritized by severity.")
    lines.append("")

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.get("severity", "info").lower(), 5))

    severity_map = {
        "critical": "> [!CAUTION]",
        "high": "> [!WARNING]",
        "medium": "> [!IMPORTANT]",
        "low": "> [!TIP]",
        "info": "> [!NOTE]"
    }

    for f in sorted_findings:
        sev = f.get("severity", "info").upper()
        title = f.get("title", "Unknown Finding")
        alert = severity_map.get(sev.lower(), "> [!NOTE]")
        lines.append(f"### {alert} [{sev}] {title}")

        desc = f.get("description", "")
        if desc:
            lines.append(f"*   **What it is:** {desc}")

        evidence = f.get("evidence", {})
        if evidence:
            ev_str = ", ".join(f"{k}=" + (str(v) if not isinstance(v, list) else str(len(v)) + " items") for k, v in evidence.items())
            if "affected_components" in evidence and isinstance(evidence["affected_components"], list):
                comps = evidence["affected_components"]
                if len(comps) > 5:
                    ev_str = f"Affected components include {', '.join(comps[:5])} and {len(comps)-5} more."
                else:
                    ev_str = f"Affected components include {', '.join(comps)}."
            lines.append(f"*   **Evidence:** {ev_str}")

        action = f.get("recommendation", "")
        if action:
            lines.append(f"*   **Action to Take:** {action}")

        why = f.get("interpretation", "")
        if why and why != desc:
            lines.append(f"*   **Why:** {why}")

        lines.append("")

    nav = data.get("navigation", {})
    starts = nav.get("start_here", [])
    if starts:
        lines.append("---")
        lines.append("")
        lines.append("## 3. Navigation Guidance")
        lines.append("")
        lines.append("Highest-priority topological entry points:")
        lines.append("")
        for i, start in enumerate(starts[:5], 1):
            lines.append(f"{i}. `{start}`")
        lines.append("")

    if "_warning" in data:
        lines.append("---")
        lines.append(f"> [!WARNING]\n> {data['_warning']}")

    return "\n".join(lines)


@mcp.tool()
def get_collider_insights(db_dir: str = "") -> str:
    """
    Get Collider architectural insights: grade, health score, findings, and navigation.

    Returns the full insights analysis formatted as an actionable Markdown digest, including:
    - Overall grade (A-F) and health score (0-10)
    - Health components (topology, constraints, purpose, test coverage, etc.)
    - Findings with severity, interpretation, and recommendations
    - Navigation guidance (entry points, critical path, top risks)

    Args:
        db_dir: Path to the .collider directory. Leave empty to auto-detect.

    Returns:
        Structured Markdown string containing grade, health_score, actionable findings, and navigation.
        If no insights exist, returns an error string with instructions to run the Collider.
    """
    path = _find_insights_json(db_dir)
    if path is None:
        return json.dumps({
            "error": "No collider_insights.json found.",
            "action": "Run `./pe collider full .` or `collider full <path> --output .collider` first.",
            "hint": "The insights compiler runs as stage 11.95 of the full analysis pipeline."
        })

    try:
        with open(path, "r") as f:
            insights = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        return json.dumps({"error": f"Failed to read insights: {e}"})

    # Add staleness warning
    import time
    age_days = (time.time() - path.stat().st_mtime) / 86400
    if age_days > 7:
        insights["_warning"] = f"Insights are {age_days:.0f} days old. Re-run Collider for fresh data."

    insights["_source"] = str(path)
    return _format_insights_markdown(insights)


@mcp.resource("collider://insights")
def collider_insights_resource() -> str:
    """Collider architectural insights in markdown format."""
    # Try markdown version first
    md_path = Path.cwd() / ".collider" / "collider_insights.md"
    if md_path.exists():
        return md_path.read_text()

    # Fall back to JSON summary
    path = _find_insights_json()
    if path is None:
        return "No Collider insights available. Run `./pe collider full .` first."

    try:
        with open(path, "r") as f:
            insights = json.load(f)
        grade = insights.get("grade", "?")
        score = insights.get("health_score", 0)
        summary = insights.get("executive_summary", "No summary available.")
        return f"# Collider Insights\n\n**Grade: {grade}** | Health Score: {score}/10\n\n{summary}"
    except Exception:
        return "Error reading Collider insights."


if __name__ == "__main__":
    mcp.run(transport="stdio")
