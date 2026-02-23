"""
Collider MCP Tool Server
========================
Exposes GraphRAG search and neighborhood as native MCP tools for AI agents.

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


if __name__ == "__main__":
    mcp.run(transport="stdio")
