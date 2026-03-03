"""Ops tools: MCP, transfers, activity, ecosystem scanning, reverse sync."""

from tool_registry import ToolSpec, registry

TOOLS = [
    # --- MCP ---
    ToolSpec(
        name="call_mcp_tool",
        description="Call a safe MCP tool via mcporter. selector format: server.tool. args can be JSON object string.",
        parameters={
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "MCP tool selector (server:tool_name)"},
            },
            "required": ["selector"],
        },
        method="POST",
        path="/api/voice/mcp/call",
        source="elevenlabs",
        timeout=30,
        tags=["ops", "mcp"],
    ),
    ToolSpec(
        name="get_mcp_schema",
        description="Get MCP tool schema for one server (hostinger, huggingface, perplexity, cerebras).",
        parameters={
            "type": "object",
            "properties": {
                "server": {"type": "string", "description": "MCP server name"},
            },
            "required": ["server"],
        },
        method="GET",
        path="/api/voice/mcp/schema",
        source="elevenlabs",
        tags=["ops", "mcp"],
    ),
    ToolSpec(
        name="list_mcp_servers",
        description="List available MCP servers and health status from local mcporter.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/mcp/servers",
        source="elevenlabs",
        tags=["ops", "mcp"],
    ),
    # --- Data Transfer ---
    ToolSpec(
        name="transfer_data",
        description="Move files between any two ecosystem tenants: VPS, Mac, and Google Cloud Storage. Use /path for VPS, gs://bucket/path for GCS, mac:/path for Mac. All 6 directions supported. Always does a dry run first unless told otherwise.",
        parameters={
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Data source"},
                "destination": {"type": "string", "description": "Data destination"},
            },
            "required": ["source", "destination"],
        },
        method="POST",
        path="/api/voice/transfer",
        source="elevenlabs",
        timeout=60,
        tags=["ops"],
    ),
    ToolSpec(
        name="transfer_status",
        description="Check the status of active or last data transfer between VPS and GCS cold storage. Returns progress, source, destination, and completion status.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/transfer/status",
        source="elevenlabs",
        tags=["ops"],
    ),
    # --- Activity / Scanning ---
    ToolSpec(
        name="check_activity",
        description="Get recent activity events, alerts, and system summary.",
        parameters={
            "type": "object",
            "properties": {
                "hours": {"type": "number", "description": "Hours of history to check"},
            },
        },
        method="GET",
        path="/api/voice/activities",
        arg_transform=lambda a: {"hours": str(a.get("hours", 24))},
        tags=["ops"],
    ),
    ToolSpec(
        name="search_vps_files",
        description="Search for files by content on the VPS. Searches .md, .json, and .py files. Returns matching file paths (max 20). Use this to find specific configs, docs, or code.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/search",
        source="elevenlabs",
        tags=["ops"],
    ),
    ToolSpec(
        name="scan_ecosystem_tdj",
        description="Run a TDJ (Temporal Daily Journal) command on the ecosystem. Commands: summary (overview), hotspots (active dirs), drift (changes since last scan), modified (recently changed files), recent (newest files), stale (old files), pattern (search by filename pattern). Always runs ecosystem-wide.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "TDJ command (recent, stale, summary)"},
            },
            "required": ["command"],
        },
        method="POST",
        path="/api/voice/ops/tdj",
        source="elevenlabs",
        tags=["ops"],
    ),
    ToolSpec(
        name="run_reverse_sync",
        description="Sync VPS deployed state back to the repository. Copies configs (openclaw.json, thresholds, triggers) and systemd units to the repo with secrets masked. Syncthing then carries changes to Mac. Use after making VPS changes to ensure ground and cloud stay in sync.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/ops/reverse-sync",
        source="elevenlabs",
        timeout=60,
        tags=["ops"],
    ),
]

registry.register_many(TOOLS)
