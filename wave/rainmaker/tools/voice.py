"""Voice tools: providers, calls, LLM modes, self-knowledge."""

from tool_registry import ToolSpec, registry

TOOLS = [
    ToolSpec(
        name="switch_voice_provider",
        description="Switch the voice provider and call Leo back on the new provider. After switching, the current call ends and a new call is placed using the chosen provider. Use 'auto' to let the system pick the best available. Providers: elevenlabs (best quality, Ali G voice), openai (great quality, sage voice), grok (fast, xAI), gemini (free), selfhosted (free, runs locally), twilio (always-on fallback).",
        parameters={
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["elevenlabs", "openai", "grok", "gemini", "selfhosted", "twilio", "auto"],
                    "description": "Voice provider to switch to",
                },
            },
            "required": ["provider"],
        },
        method="POST",
        path="/api/voice/provider/switch-full",
        timeout=20,
        tags=["voice"],
    ),
    ToolSpec(
        name="check_voice_providers",
        description="Check status, balance, and quota of ALL voice providers in parallel. Returns: ElevenLabs chars remaining, OpenAI key status, Grok/Gemini availability, Twilio balance, self-hosted engine status, and which tier is currently active.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/providers",
        timeout=15,
        tags=["voice"],
    ),
    ToolSpec(
        name="make_voice_call",
        description="Place an outbound voice call to Leo (or a specified number). The call routes through the current voice provider tier system. Optionally include context that will be spoken as the greeting.",
        parameters={
            "type": "object",
            "properties": {
                "context": {"type": "string", "description": "Context for the call"},
                "to_number": {"type": "string", "description": "Phone number to call"},
            },
        },
        method="POST",
        path="/api/voice/call",
        timeout=30,
        tags=["voice"],
    ),
    ToolSpec(
        name="end_call",
        description="Gracefully end the current voice call. Use when Leo says goodbye, 'desliga', 'tchau', 'encerra', 'finaliza a ligacao', or asks to hang up. This truly terminates the call -- no fallback to another provider. Say goodbye BEFORE calling this tool.",
        parameters={
            "type": "object",
            "properties": {
                "call_sid": {"type": "string", "description": "Call SID to end"},
            },
        },
        method="POST",
        path="/api/voice/call/hangup",
        tags=["voice"],
    ),
    ToolSpec(
        name="check_llm_voice_mode",
        description="Check current custom LLM mode and chain definitions. Shows active mode (eco/full), configured chain, loaded chain, and preset definitions.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/llm/mode",
        tags=["voice"],
    ),
    ToolSpec(
        name="set_llm_voice_mode",
        description="Hot-edit the custom LLM chain mode for this runtime. Use voice_mode='eco' for cheaper default path or voice_mode='full' for stronger/faster path.",
        parameters={
            "type": "object",
            "properties": {
                "voice_mode": {
                    "type": "string",
                    "enum": ["eco", "full"],
                    "description": "LLM chain mode",
                },
                "mode": {
                    "type": "string",
                    "enum": ["eco", "full"],
                    "description": "Alias for voice_mode",
                },
            },
        },
        method="POST",
        path="/api/llm/mode",
        arg_transform=lambda a: {"mode": a.get("voice_mode") or a.get("mode", "eco")},
        tags=["voice"],
    ),
    ToolSpec(
        name="check_llm_mode",
        description="Legacy alias for check_llm_voice_mode. Checks current custom LLM mode and chain definitions.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/llm/mode",
        enabled=False,  # Legacy alias -- hidden from LLM to avoid token waste
        tags=["voice"],
    ),
    ToolSpec(
        name="set_llm_mode",
        description="Legacy alias for set_llm_voice_mode. Hot-edit the custom LLM chain mode for this runtime.",
        parameters={
            "type": "object",
            "properties": {
                "voice_mode": {"type": "string", "enum": ["eco", "full"]},
                "mode": {"type": "string", "enum": ["eco", "full"]},
            },
        },
        method="POST",
        path="/api/llm/mode",
        arg_transform=lambda a: {"mode": a.get("voice_mode") or a.get("mode", "eco")},
        enabled=False,  # Legacy alias -- hidden from LLM to avoid token waste
        tags=["voice"],
    ),
    ToolSpec(
        name="check_self_knowledge",
        description="Return the authoritative live self-map of the system: voice tiers, LLM voice mode, context injection layers, active collectors, and current warnings.",
        parameters={
            "type": "object",
            "properties": {
                "deep": {"type": "boolean", "description": "Deep introspection mode"},
            },
        },
        method="GET",
        path="/api/voice/self-knowledge",
        arg_transform=lambda a: {"deep": "1"} if a.get("deep") else {},
        timeout=20,
        max_chars=4000,
        tags=["voice"],
    ),
    ToolSpec(
        name="check_self",
        description="Check your own current configuration. Shows how many tools you have, which workspace files are loaded, your sound profile, and when you last synced. Use when asked about your own status or capabilities.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/omniscience",
        source="elevenlabs",
        tags=["voice"],
    ),
    ToolSpec(
        name="sync_self",
        description="Re-sync your system prompt and tool sounds from workspace files. Updates your personality, tools list, and sound profile. Use after workspace files change, after new tools are added, or when asked to refresh your configuration.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/sync-self",
        source="elevenlabs",
        tags=["voice"],
    ),
    ToolSpec(
        name="get_full_context",
        description="Get a complete context summary of the VPS: trading status, system health, gateway status, thresholds, and uptime. Use this first to get an overview before diving deeper.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/context",
        source="elevenlabs",
        max_chars=4000,
        tags=["voice"],
    ),
    ToolSpec(
        name="call_status",
        description="Check if there is an active phone call or Google Meet session. Returns call status, duration, and connection details.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/meet/status",
        source="elevenlabs",
        tags=["voice"],
    ),
    ToolSpec(
        name="join_meeting",
        description="Join a Google Meet call by dialing in with a phone number and PIN code. Bridges the call through Twilio to ElevenLabs voice.",
        parameters={
            "type": "object",
            "properties": {
                "dial_in": {"type": "string", "description": "Dial-in number"},
                "pin": {"type": "string", "description": "Meeting PIN"},
            },
            "required": ["dial_in", "pin"],
        },
        method="POST",
        path="/api/meet/join",
        source="elevenlabs",
        tags=["voice"],
    ),
]

registry.register_many(TOOLS)
