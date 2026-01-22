#!/usr/bin/env python3
"""
Perplexity MCP Server with Deterministic Auto-Save Pipeline

A local MCP server that wraps Perplexity API and automatically persists
ALL research outputs to a structured directory.

Pipeline:
    1. Receive query via JSON-RPC
    2. Call Perplexity API
    3. DETERMINISTIC SAVE:
       - raw/{timestamp}_{slug}.json  (full API response)
       - docs/{timestamp}_{slug}.md   (human-readable markdown)
    4. Return response with save confirmation

This ensures ZERO information loss from research queries.

Usage:
    # Add to ~/.claude/settings.json mcpServers:
    "perplexity-local": {
        "command": "python3",
        "args": ["/path/to/perplexity_mcp_server.py"]
    }
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# === Configuration ===
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
RESEARCH_BASE = PROJECT_ROOT / "standard-model-of-code" / "docs" / "research" / "perplexity"
RAW_DIR = RESEARCH_BASE / "raw"       # Full JSON responses
DOCS_DIR = RESEARCH_BASE / "docs"     # Human-readable markdown

# === API Key Management ===
def get_api_key() -> str:
    """Get Perplexity API key from Doppler or environment."""
    # Try Doppler first
    try:
        result = subprocess.run(
            ["doppler", "secrets", "get", "PERPLEXITY_API_KEY", "--plain",
             "--project", "ai-tools", "--config", "dev"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to environment
    key = os.environ.get("PERPLEXITY_API_KEY")
    if key:
        return key

    raise ValueError("No PERPLEXITY_API_KEY found in Doppler or environment")


# === Deterministic Auto-Save Pipeline ===
def generate_filename(query: str) -> str:
    """Generate deterministic filename from timestamp and query."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() else "_" for c in query[:50]).strip("_").lower()
    return f"{timestamp}_{slug}"


def save_raw_json(filename: str, query: str, api_response: dict, model: str) -> Path:
    """
    Save COMPLETE API response as JSON.
    This preserves ALL information from Perplexity.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Structure: full API response + our metadata
    raw_data = {
        "_meta": {
            "saved_at": datetime.now().isoformat(),
            "model": model,
            "query": query,
            "query_length": len(query),
            "source": "perplexity-local-mcp"
        },
        "api_response": api_response  # COMPLETE response from Perplexity
    }

    filepath = RAW_DIR / f"{filename}.json"
    filepath.write_text(json.dumps(raw_data, indent=2, ensure_ascii=False))
    return filepath


def save_markdown_doc(filename: str, query: str, api_response: dict, model: str) -> Path:
    """
    Save human-readable markdown summary.
    """
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Extract content from API response
    content = api_response.get("choices", [{}])[0].get("message", {}).get("content", "")
    citations = api_response.get("citations", [])
    usage = api_response.get("usage", {})

    md_content = f"""# Perplexity Research: {query[:100]}{'...' if len(query) > 100 else ''}

> **Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Model:** {model}
> **Source:** MCP Server (auto-saved)
> **Raw JSON:** `raw/{filename}.json`

---

## Query

{query}

---

## Response

{content}

---

## Citations

"""
    if citations:
        for i, citation in enumerate(citations, 1):
            md_content += f"{i}. {citation}\n"
    else:
        md_content += "_No citations provided_\n"

    # Add usage stats if available
    if usage:
        md_content += f"""
---

## Usage Stats

- Prompt tokens: {usage.get('prompt_tokens', 'N/A')}
- Completion tokens: {usage.get('completion_tokens', 'N/A')}
- Total tokens: {usage.get('total_tokens', 'N/A')}
"""

    filepath = DOCS_DIR / f"{filename}.md"
    filepath.write_text(md_content)
    return filepath


def auto_save_research(query: str, api_response: dict, model: str) -> dict:
    """
    DETERMINISTIC PIPELINE: Save both raw JSON and markdown.

    Returns dict with paths to saved files.
    """
    filename = generate_filename(query)

    # Save both formats
    raw_path = save_raw_json(filename, query, api_response, model)
    doc_path = save_markdown_doc(filename, query, api_response, model)

    return {
        "raw": raw_path,
        "doc": doc_path,
        "filename": filename
    }


# === Perplexity API ===
def call_perplexity(messages: list, model: str = "sonar-pro") -> dict:
    """Call Perplexity API."""
    import httpx

    api_key = get_api_key()

    response = httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": messages,
            "return_citations": True
        },
        timeout=300.0
    )
    response.raise_for_status()
    return response.json()


# === MCP Protocol ===
def read_message() -> Optional[dict]:
    """Read a JSON-RPC message from stdin."""
    line = sys.stdin.readline()
    if not line:
        return None
    return json.loads(line)


def write_message(msg: dict):
    """Write a JSON-RPC message to stdout."""
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_initialize(_params: dict) -> dict:
    """Handle initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "perplexity-local",
            "version": "1.0.0"
        }
    }


def handle_tools_list() -> dict:
    """Return available tools."""
    return {
        "tools": [
            {
                "name": "perplexity_ask",
                "description": "Ask Perplexity a question. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Array of conversation messages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["role", "content"]
                            }
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "perplexity_research",
                "description": "Deep research using Perplexity. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Array of conversation messages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["role", "content"]
                            }
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "perplexity_search",
                "description": "Web search using Perplexity. Auto-saves response to docs/research/perplexity/",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }


def handle_tool_call(name: str, arguments: dict) -> dict:
    """Handle a tool call with deterministic auto-save pipeline."""
    try:
        if name == "perplexity_ask":
            messages = arguments.get("messages", [])
            model = "sonar-pro"
        elif name == "perplexity_research":
            messages = arguments.get("messages", [])
            model = "sonar-deep-research"
        elif name == "perplexity_search":
            query = arguments.get("query", "")
            messages = [{"role": "user", "content": query}]
            model = "sonar-pro"
        else:
            return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}

        # Extract query for saving
        query_text = messages[-1].get("content", "") if messages else ""

        # Call Perplexity API
        api_response = call_perplexity(messages, model)

        # DETERMINISTIC PIPELINE: Save full API response
        try:
            saved = auto_save_research(query_text, api_response, model)
            save_note = (
                f"\n\n---\n"
                f"_Auto-saved:_\n"
                f"- Raw: `{saved['raw'].relative_to(PROJECT_ROOT)}`\n"
                f"- Doc: `{saved['doc'].relative_to(PROJECT_ROOT)}`"
            )
        except Exception as e:
            save_note = f"\n\n---\n_Auto-save failed: {e}_"

        # Extract content for response
        content = api_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = api_response.get("citations", [])

        # Format response
        response_text = content
        if citations:
            response_text += "\n\n**Sources:**\n"
            for i, citation in enumerate(citations, 1):
                response_text += f"{i}. {citation}\n"
        response_text += save_note

        return {"content": [{"type": "text", "text": response_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}


def main():
    """Main MCP server loop."""
    # Log startup
    sys.stderr.write(f"[perplexity-local] Starting MCP server\n")
    sys.stderr.write(f"[perplexity-local] Research base: {RESEARCH_BASE}\n")
    sys.stderr.write(f"[perplexity-local] Raw JSON dir: {RAW_DIR}\n")
    sys.stderr.write(f"[perplexity-local] Markdown dir: {DOCS_DIR}\n")
    sys.stderr.flush()

    while True:
        msg_id = None
        try:
            msg = read_message()
            if msg is None:
                break

            method = msg.get("method", "")
            params = msg.get("params", {})
            msg_id = msg.get("id")

            if method == "initialize":
                result = handle_initialize(params)
            elif method == "initialized":
                continue  # Notification, no response needed
            elif method == "tools/list":
                result = handle_tools_list()
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}

            if msg_id is not None:
                write_message({"jsonrpc": "2.0", "id": msg_id, "result": result})

        except Exception as e:
            sys.stderr.write(f"[perplexity-local] Error: {e}\n")
            sys.stderr.flush()
            if msg_id is not None:
                write_message({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)}
                })


if __name__ == "__main__":
    main()
