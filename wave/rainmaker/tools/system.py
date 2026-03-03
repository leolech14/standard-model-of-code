"""System tools: VPS status, services, files, shell, config."""

from tool_registry import ToolSpec, registry

TOOLS = [
    ToolSpec(
        name="get_system_status",
        description="Get VPS system metrics: CPU, memory, disk, uptime, and service states.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/system/current",
        tags=["system"],
    ),
    ToolSpec(
        name="check_services",
        description="Check status of managed systemd services.",
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Specific service to check"},
            },
        },
        method="GET",
        path="/api/voice/ops/services",
        arg_transform=lambda a: {"service": a["service"]} if a.get("service") else {},
        tags=["system"],
    ),
    ToolSpec(
        name="restart_service",
        description="Restart a managed systemd service by name.",
        parameters={
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "Service name to restart"},
            },
            "required": ["service"],
        },
        method="POST",
        path="/api/voice/ops/services/restart",
        arg_transform=lambda a: {"service": a.get("service", "")},
        tags=["system"],
    ),
    ToolSpec(
        name="deploy_rainmaker",
        description="Deploy latest code from repo to production with backup and validation.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/ops/deploy",
        timeout=60,
        tags=["system"],
    ),
    ToolSpec(
        name="check_ecosystem",
        description="Scan the ecosystem: Tailscale mesh, VPS storage, file index.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/ops/ecosystem",
        tags=["system"],
    ),
    ToolSpec(
        name="shell_exec",
        description="Execute a shell command on the VPS. Returns stdout, stderr, and exit code. Use for: git operations, systemctl, package management, process inspection, deployment commands, or any system operation. Commands run as root. Timeout default 30s, max 300s.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
                "timeout": {"type": "integer", "description": "Timeout in seconds (default 30, max 300)"},
                "background": {"type": "boolean", "description": "Run in background"},
            },
            "required": ["command"],
        },
        method="POST",
        path="/api/voice/shell/exec",
        arg_transform=lambda a: {
            "command": a["command"],
            "timeout": min(a.get("timeout", 30), 300),
            "background": a.get("background", False),
        },
        timeout=305,
        max_chars=4000,
        tags=["system"],
    ),
    ToolSpec(
        name="read_vps_file",
        description="Read a file or list a directory on the VPS. Use for reading code, configs, workspace files, logs, or browsing directories. Returns file content with line numbers, or directory listing.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read"},
                "max_lines": {"type": "integer", "description": "Max lines to return (default 200)"},
            },
            "required": ["path"],
        },
        method="GET",
        path="/api/voice/read",
        max_chars=4000,
        tags=["system"],
    ),
    ToolSpec(
        name="write_vps_file",
        description="Write or append content to a file on the VPS. Creates parent directories if needed. Use for creating new files, overwriting existing files, or appending content. Use mode='append' to add to end of file without replacing existing content.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"},
                "mode": {"type": "string", "enum": ["overwrite", "append"], "description": "Write mode"},
            },
            "required": ["path", "content"],
        },
        method="POST",
        path="/api/voice/write",
        tags=["system"],
    ),
    ToolSpec(
        name="edit_file",
        description="Find and replace text in a file. The old_text must be unique in the file. Use for surgical edits: changing a config value, fixing a bug, updating a line. Returns a diff preview of the change.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "old_text": {"type": "string", "description": "Text to find (must be unique)"},
                "new_text": {"type": "string", "description": "Replacement text"},
            },
            "required": ["path", "old_text", "new_text"],
        },
        method="POST",
        path="/api/voice/fs/edit",
        tags=["system"],
    ),
    ToolSpec(
        name="configure",
        description="Change system configuration. Routes to the correct backend automatically. Domains: trading (thresholds, triggers, scoring, preferences, trade-mode), llm (mode eco/full), voice (force tier), system (restart services).",
        parameters={
            "type": "object",
            "properties": {
                "domain": {"type": "string", "enum": ["trading", "llm", "voice", "system"]},
                "key": {"type": "string", "description": "Config key"},
                "value": {"type": "string", "description": "Config value"},
            },
            "required": ["domain", "key", "value"],
        },
        method="POST",
        path="/api/voice/config/set",
        max_chars=4000,
        tags=["system"],
    ),
    ToolSpec(
        name="get_config",
        description="Read current system configuration for a domain. Returns all settings for the domain or a specific key.",
        parameters={
            "type": "object",
            "properties": {
                "domain": {"type": "string", "enum": ["trading", "llm", "voice", "system"]},
                "key": {"type": "string", "description": "Specific config key (optional)"},
            },
            "required": ["domain"],
        },
        method="GET",
        path="/api/voice/config/get",
        max_chars=4000,
        tags=["system"],
    ),
    ToolSpec(
        name="run_vps_command",
        description="Execute a whitelisted shell command on the VPS. Allowed commands: openclaw health, openclaw gateway status, openclaw skills list, systemctl --user status, tail, df -h, free -h, uptime, ps aux, journalctl --user. Timeout: 15 seconds.",
        parameters={
            "type": "object",
            "properties": {
                "cmd": {"type": "string", "description": "Command to run"},
            },
            "required": ["cmd"],
        },
        method="POST",
        path="/api/voice/shell",
        source="elevenlabs",
        max_chars=4000,
        tags=["system"],
    ),
]

registry.register_many(TOOLS)
