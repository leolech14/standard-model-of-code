"""Meta tools: tool management, generic API, UI state, self-editing."""

from tool_registry import ToolSpec, registry

TOOLS = [
    ToolSpec(
        name="rainmaker_api",
        description="Call any Rainmaker dashboard API endpoint. Use for operations not covered by other tools.",
        parameters={
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST"], "description": "HTTP method"},
                "path": {"type": "string", "description": "API path (e.g. /api/...)"},
                "body": {"type": "object", "description": "Request body for POST"},
            },
            "required": ["method", "path"],
        },
        method="GET",    # Ignored -- executor reads method/path from arguments
        path="__dynamic__",  # Sentinel: executor reads method/path from arguments
        max_chars=4000,
        tags=["meta"],
    ),
    ToolSpec(
        name="manage_ui_state",
        description="Change the frontend user interface state in real-time. Use this to switch themes (light/dark mode) for Leo dynamically while chatting. It broadcasts an SSE event to all his open dashboard tabs.",
        parameters={
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "UI action"},
                "theme": {"type": "string", "enum": ["dark", "light"], "description": "Theme"},
            },
            "required": ["action", "theme"],
        },
        method="POST",
        path="/api/voice/ui_control",
        tags=["meta"],
    ),
    ToolSpec(
        name="edit_self",
        description="Edit your own identity, rules, or knowledge files and immediately propagate to ALL tiers. Use for SOUL.md, AGENTS.md, TOOLS.md, MEMORY.md, etc. Changes take effect on every voice tier within seconds. Actions: replace_section, append_to_section, add_section, remove_section.",
        parameters={
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "enum": ["SOUL.md", "AGENTS.md", "TOOLS.md", "MEMORY.md",
                             "USER.md", "IDENTITY.md", "SYSTEM.md", "HEARTBEAT.md"],
                    "description": "File to edit",
                },
                "section": {"type": "string", "description": "Section name"},
                "action": {
                    "type": "string",
                    "enum": ["replace_section", "append_to_section", "add_section", "remove_section"],
                    "description": "Edit action",
                },
                "content": {"type": "string", "description": "Content for the section"},
            },
            "required": ["file", "section", "action"],
        },
        method="POST",
        path="/api/voice/self/edit",
        timeout=30,
        tags=["meta"],
    ),
    ToolSpec(
        name="edit_frontend",
        description="Edit the Rainmaker dashboard UI (CSS, JS, HTML templates) and deploy live. The browser auto-reloads within 5 seconds. Use when Leo asks to change colors, fonts, layout, or any visual element. Find-and-replace: old_text must be unique.",
        parameters={
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "Frontend file to edit"},
                "old_text": {"type": "string", "description": "Text to find"},
                "new_text": {"type": "string", "description": "Replacement text"},
            },
            "required": ["file", "old_text", "new_text"],
        },
        method="POST",
        path="/api/voice/frontend/edit",
        timeout=90,
        tags=["meta"],
    ),
    # --- Runtime tool management (Python-native, no HTTP call) ---
    # Executor dispatches these via _execute_native() using the __native__: sentinel.
    ToolSpec(
        name="register_tool",
        description="Register a new tool capability at runtime. Takes effect immediately on all tiers. The tool routes to an API endpoint on the Rainmaker Console. Use handler_path to specify the endpoint (e.g., '/api/health').",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tool name"},
                "description": {"type": "string", "description": "Tool description"},
                "parameters": {"type": "object", "description": "JSON Schema for params"},
                "handler_path": {"type": "string", "description": "API endpoint path"},
                "method": {"type": "string", "enum": ["GET", "POST"], "description": "HTTP method"},
            },
            "required": ["name", "description", "handler_path"],
        },
        method="POST",
        path="__native__:register",
        tags=["meta"],
    ),
    ToolSpec(
        name="disable_tool",
        description="Disable a runtime-registered tool (built-in tools cannot be disabled).",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tool name to disable"},
            },
            "required": ["name"],
        },
        method="POST",
        path="__native__:disable",
        tags=["meta"],
    ),
    ToolSpec(
        name="enable_tool",
        description="Re-enable a previously disabled runtime tool.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tool name to enable"},
            },
            "required": ["name"],
        },
        method="POST",
        path="__native__:enable",
        tags=["meta"],
    ),
    ToolSpec(
        name="list_tools",
        description="List all registered tools (built-in + runtime) with their status.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="__native__:list",
        tags=["meta"],
    ),
]

registry.register_many(TOOLS)
