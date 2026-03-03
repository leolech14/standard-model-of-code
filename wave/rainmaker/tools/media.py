"""Media tools: YouTube, Google Drive, tags, factory/specbuilder."""

from tool_registry import ToolSpec, registry

TOOLS = [
    # --- YouTube ---
    ToolSpec(
        name="list_youtube",
        description="List all YouTube videos that have been processed. Shows titles, channels, and whether transcripts are available.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/youtube/list",
        source="elevenlabs",
        tags=["media", "youtube"],
    ),
    ToolSpec(
        name="process_youtube",
        description="Process a YouTube video: extract title, description, chapters, transcript. Give it any YouTube URL and get back a full breakdown. Use this when someone shares a video link or asks about a YouTube video.",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "YouTube video URL"},
            },
            "required": ["url"],
        },
        method="POST",
        path="/api/voice/youtube/process",
        source="elevenlabs",
        timeout=120,
        tags=["media", "youtube"],
    ),
    ToolSpec(
        name="search_youtube",
        description="Search within a previously processed YouTube video transcript. Find specific topics, quotes, or moments mentioned in the video.",
        parameters={
            "type": "object",
            "properties": {
                "video_id": {"type": "string", "description": "Video ID to search in"},
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["video_id", "query"],
        },
        method="GET",
        path="/api/voice/youtube/search",
        source="elevenlabs",
        tags=["media", "youtube"],
    ),
    # --- Google Drive ---
    ToolSpec(
        name="list_drive_files",
        description="List Google Drive files optionally by folder.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/drive/list",
        source="elevenlabs",
        tags=["media", "google"],
    ),
    ToolSpec(
        name="search_drive",
        description="Search Google Drive files by name or content.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/google/drive/search",
        source="elevenlabs",
        tags=["media", "google"],
    ),
    ToolSpec(
        name="upload_to_drive",
        description="Upload a VPS file to Google Drive.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/google/drive/upload",
        source="elevenlabs",
        tags=["media", "google"],
    ),
    # --- Tags ---
    ToolSpec(
        name="list_tags",
        description="List all available tags in the registry. Optionally filter by facet: operational financial semantic temporal priority.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/tags/list",
        source="elevenlabs",
        tags=["media", "tags"],
    ),
    ToolSpec(
        name="search_tags",
        description="Find all entities tagged with a specific tag. Returns entity list and voice summary. Use to answer: What is tagged as essential? Show me recurring items.",
        parameters={
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Tag to search for"},
            },
            "required": ["tag"],
        },
        method="GET",
        path="/api/voice/tags/search",
        source="elevenlabs",
        tags=["media", "tags"],
    ),
    ToolSpec(
        name="tag_entity",
        description="Tag an entity with a semantic label. Tags must be from the registry. Facets: operational financial semantic temporal priority. Entity types: invoice email event file activity spec task video memory.",
        parameters={
            "type": "object",
            "properties": {
                "entity_type": {"type": "string", "description": "Entity type"},
                "entity_id": {"type": "string", "description": "Entity ID"},
                "tag": {"type": "string", "description": "Tag to add"},
            },
            "required": ["entity_type", "entity_id", "tag"],
        },
        method="POST",
        path="/api/voice/tags/add",
        source="elevenlabs",
        tags=["media", "tags"],
    ),
    ToolSpec(
        name="get_entity_tags",
        description="Get all tags assigned to a specific entity. Returns tag names with facets and descriptions.",
        parameters={
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "Entity type"},
                "id": {"type": "string", "description": "Entity ID"},
            },
            "required": ["type", "id"],
        },
        method="GET",
        path="/api/voice/tags/entity",
        source="elevenlabs",
        tags=["media", "tags"],
    ),
    # --- Factory / SpecBuilder ---
    ToolSpec(
        name="factory_run",
        description="Process all ready tasks in the factory queue. Currently runs in dry-run mode: shows what workers would be assigned and estimated costs without actually dispatching to LLMs. Use when asked to run the factory, process tasks, or start production.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/factory/run",
        source="elevenlabs",
        timeout=60,
        tags=["media", "factory"],
    ),
    ToolSpec(
        name="factory_specs",
        description="List all specs in the SpecDriven Factory with their transcription status. Shows which specs have been decomposed into tasks and which are pending. Use when the user asks about available specs or what can be transcribed.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/factory/specs",
        source="elevenlabs",
        tags=["media", "factory"],
    ),
    ToolSpec(
        name="factory_status",
        description="Get the full factory status: task queue (total, pending, ready), worker pool (6 LLM workers with health and tiers), token budget remaining, and a preview of ready tasks. Use when asked about factory health, task backlog, worker utilization, or budget.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/factory/status",
        source="elevenlabs",
        tags=["media", "factory"],
    ),
    ToolSpec(
        name="factory_tasks",
        description="List tasks in the factory registry. Filter by status (pending, assigned, executing, completed, failed) or by spec name. Shows task ID, action, component, target file, tier, worker assignment, and step count. Use when asked to see the task queue, pending tasks, completed tasks, or tasks for a specific spec.",
        parameters={"type": "object", "properties": {}},
        method="GET",
        path="/api/voice/factory/tasks",
        source="elevenlabs",
        tags=["media", "factory"],
    ),
    ToolSpec(
        name="factory_task_detail",
        description="Get full task detail -- the mRNA. Shows every step, input files, output schema, and acceptance test. This is everything a worker needs to execute the task. Pass the task_id to inspect.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID"},
            },
            "required": ["task_id"],
        },
        method="GET",
        path="/api/voice/factory/task",
        source="elevenlabs",
        tags=["media", "factory"],
    ),
    ToolSpec(
        name="factory_transcribe",
        description="Decompose a spec into deterministic tasks (mRNA). Provide the spec name like CIRCADIAN, WATERSHED, TOKEN_BUDGET, etc. If no spec is provided, lists all available specs with their transcription status.",
        parameters={"type": "object", "properties": {}},
        method="POST",
        path="/api/voice/factory/transcribe",
        source="elevenlabs",
        tags=["media", "factory"],
    ),
]

registry.register_many(TOOLS)
