"""Communication tools: web search, email, calendar, WhatsApp, memory, OpenClaw."""

from tool_registry import ToolSpec, registry

TOOLS = [
    ToolSpec(
        name="search_web",
        description="Search the web for current information using Perplexity Sonar. Use for real-time data: news, prices, weather, facts, documentation. Fast (~3-5s). Returns answer with sources.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "model": {
                    "type": "string",
                    "enum": ["sonar", "sonar-pro"],
                    "description": "Perplexity model",
                },
            },
            "required": ["query"],
        },
        method="POST",
        path="/api/voice/search-web",
        timeout=30,
        max_chars=4000,
        tags=["comms", "research"],
    ),
    ToolSpec(
        name="deep_research",
        description="Launch deep multi-step research using Perplexity Deep Research. Use for complex questions needing thorough analysis: market research, technical comparisons, in-depth investigation. Takes 30-120 seconds. Warn Leo it will take a moment before calling.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Research query"},
            },
            "required": ["query"],
        },
        method="POST",
        path="/api/voice/deep-research",
        timeout=180,
        max_chars=8000,
        tags=["comms", "research"],
    ),
    ToolSpec(
        name="recall_memory",
        description="Search long-term memories and recent conversation notes.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Memory search query"},
            },
            "required": ["query"],
        },
        method="GET",
        path="/api/voice/memory",
        arg_transform=lambda a: {"q": a.get("query", "")},
        tags=["comms"],
    ),
    ToolSpec(
        name="send_whatsapp",
        description="Send a WhatsApp message to Leonardo (default) or another number. Use when the user asks you to send a message, reminder, or note via WhatsApp.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message text to send"},
            },
            "required": ["message"],
        },
        method="POST",
        path="/api/voice/whatsapp",
        source="elevenlabs",
        tags=["comms"],
    ),
    ToolSpec(
        name="openclaw_agent",
        description="Run a full OpenClaw agent turn. This is the POWER tool - it gives access to ALL OpenClaw capabilities: 21 skills, 8 plugins, 4 MCP servers, memory, and 7 LLM providers. Send any message and OpenClaw will process it with its full stack. Use this for complex tasks, research, multi-step operations, or anything the other tools can't handle.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message for the agent"},
            },
            "required": ["message"],
        },
        method="POST",
        path="/api/voice/openclaw",
        source="elevenlabs",
        timeout=30,
        tags=["comms"],
    ),
    # --- Gmail ---
    ToolSpec(
        name="read_email",
        description="Read a single email by ID. Returns subject, from, date, body text, and attachments.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/email/read",
        source="elevenlabs",
        max_chars=4000,
        tags=["comms", "google"],
    ),
    ToolSpec(
        name="search_emails",
        description="Search Gmail with standard query syntax. Returns list of email summaries.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/email/search",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
    ToolSpec(
        name="send_email",
        description="Send an email from leonardo.lech@gmail.com.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/google/email/send",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
    ToolSpec(
        name="list_labels",
        description="List all Gmail labels and folders.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/email/labels",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
    # --- Calendar ---
    ToolSpec(
        name="list_events",
        description="List upcoming Google Calendar events for the next N days.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/calendar/list",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
    ToolSpec(
        name="create_event",
        description="Create a Google Calendar event. Natural language dates supported.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/google/calendar/create",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
    ToolSpec(
        name="search_calendar",
        description="Search Google Calendar events by text query.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/calendar/search",
        source="elevenlabs",
        tags=["comms", "google"],
    ),
]

registry.register_many(TOOLS)
