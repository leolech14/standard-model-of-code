# Rainmaker Tool Registry -- Architectural Spec

> **Status:** DRAFT | **Version:** 1.0.0 | **Created:** 2026-02-27
> **Author:** Claude Opus 4.6 + Leonardo Lech
> **Subsystem:** Rainmaker Console (external, VPS)
> **Macro:** MACRO-003 (deploy/sync)

---

## Problem

Tools are defined in 3 Python lists, routed via 2 route tables, dispatched through a 70+ case if/elif chain, and format-converted by 4 separate functions. Adding a tool requires touching 4 files. No single place defines "what tools exist."

### Current State

```
voice_tools.py              38 tools (TOOLS list + TOOL_ROUTES dict)
voice_tools_elevenlabs.py   59 tools (ELEVENLABS_TOOLS + ELEVENLABS_TOOL_ROUTES)
voice_tool_exec.py          70+ if/elif chain (execute_tool)
tools_http_api.py           reads nonexistent TOOLS_REGISTRY.yaml
omniscience.py              pushes tool list to ElevenLabs T1
llm_proxy.py                injects tools into text channels
```

Adding one tool: define in TOOLS/ELEVENLABS_TOOLS, add route in TOOL_ROUTES/ELEVENLABS_TOOL_ROUTES, add elif in voice_tool_exec.py, run omniscience.sync(). Four files, no validation.

### Target State

```
tool_registry.py            ToolSpec + ToolRegistry (~250 LOC)
tools/                      Domain-grouped registrations (~400 LOC)
  trading.py, voice.py, finance.py, system.py, comms.py, media.py
voice_tools.py              Thin shim → registry
voice_tool_exec.py          Thin shim → registry.execute()
```

Adding one tool: add ToolSpec in the appropriate `tools/*.py` domain file. Done.

---

## Core Abstraction: ToolSpec

Every Rainmaker tool does one thing: call `http://127.0.0.1:{PORT}/api/...` with arguments.

```python
@dataclass
class ToolSpec:
    # Identity
    name: str                           # "get_trading_status"
    description: str                    # Human-readable, LLM-visible
    parameters: dict                    # JSON Schema for arguments

    # Execution
    method: str                         # "GET" | "POST"
    path: str                           # "/api/trading/current"
    arg_transform: Callable | None      # Reshape args before HTTP call
    timeout: int = 15                   # Seconds
    max_chars: int = 2000               # Response truncation

    # Lifecycle
    enabled: bool = True
    source: str = "builtin"             # "builtin" | "elevenlabs" | "runtime"
    tags: list[str] = field(default_factory=list)  # ["trading", "finance"]

    # Format converters
    def to_openai(self) -> dict: ...         # T2/T3/T5/T6
    def to_chat_completions(self) -> dict:   # WhatsApp/Telegram (gateway)
    def to_gemini(self) -> dict: ...         # T4
```

### What ToolSpec is NOT

- Not an abstract class with an execute() method (tools are data, not behavior)
- Not backed by YAML/JSON (Python dataclasses ARE the registry)
- Not extensible via plugins/middleware (single-user VPS, arg_transform covers edge cases)
- Not unified with OpenClaw skills (different paradigm entirely)

---

## ToolRegistry

Singleton that holds all ToolSpecs.

```python
class ToolRegistry:
    _tools: dict[str, ToolSpec]     # name → spec
    _runtime_path: Path             # JSON persistence for runtime-registered tools

    def register(self, spec: ToolSpec) -> None
    def get(self, name: str) -> ToolSpec | None
    def all(self) -> list[ToolSpec]
    def by_tag(self, tag: str) -> list[ToolSpec]
    def enable(self, name: str) -> None
    def disable(self, name: str) -> None

    # Batch format converters
    def for_openai(self) -> list[dict]
    def for_chat_completions(self) -> list[dict]
    def for_gemini(self) -> list[dict]

    # Generic executor (replaces the entire if/elif chain)
    async def execute(self, name: str, arguments: dict) -> str

registry = ToolRegistry()  # Module-level singleton
```

### Execution Model

```python
async def execute(self, name: str, arguments: dict) -> str:
    spec = self.get(name)
    if not spec:
        return json.dumps({"error": f"Unknown tool: {name}"})
    if not spec.enabled:
        return json.dumps({"error": f"Tool disabled: {name}"})

    args = spec.arg_transform(arguments) if spec.arg_transform else arguments

    if spec.method == "GET":
        resp = await client.get(spec.path, params=stringify(args), timeout=spec.timeout)
    else:
        resp = await client.post(spec.path, json=args, timeout=spec.timeout)

    return resp.text[:spec.max_chars]
```

---

## Tool Catalog

96 tools total across 8 domains (94 enabled, 2 legacy aliases disabled).

### Domain: Trading (8 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `get_trading_status` | GET | `/api/trading/current` | builtin |
| `manage_thresholds` | GET | `/api/thresholds` | builtin |
| `best_trades` | GET | `/api/trading/ranking` | builtin |
| `toggle_auto_trading` | GET/POST | `/api/trading/auto-entry` | builtin |
| `check_auto_trading` | GET | `/api/trading/auto-entry` | elevenlabs |
| `market_state` | GET | `/api/trading/market-state` | builtin |
| `cashout_brl` | POST | `/api/voice/finance/binance/cashout-brl` | builtin |
| `binance_withdraw` | POST | `/api/voice/finance/binance/withdraw` | elevenlabs |

### Domain: Voice (12 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `switch_voice_provider` | POST | `/api/voice/provider/switch-full` | builtin |
| `check_voice_providers` | GET | `/api/voice/providers` | builtin |
| `make_voice_call` | POST | `/api/voice/call` | builtin |
| `end_call` | POST | `/api/voice/call/hangup` | builtin |
| `check_llm_voice_mode` | GET | `/api/llm/mode` | builtin |
| `set_llm_voice_mode` | POST | `/api/llm/mode` | builtin |
| `check_self_knowledge` | GET | `/api/voice/self-knowledge` | builtin |
| `check_self` | GET | `/api/voice/omniscience` | elevenlabs |
| `sync_self` | POST | `/api/voice/sync-self` | elevenlabs |
| `get_full_context` | GET | `/api/voice/context` | elevenlabs |
| `call_status` | GET | `/api/meet/status` | elevenlabs |
| `join_meeting` | POST | `/api/meet/join` | elevenlabs |

### Domain: Finance (15 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `finance_status` | GET | `/api/voice/finance/status` | elevenlabs |
| `finance_snapshot` | GET | `/api/voice/finance/snapshot` | elevenlabs |
| `finance_pending_actions` | GET | `/api/voice/finance/pending` | elevenlabs |
| `finance_confirm_action` | POST | `/api/voice/finance/confirm` | elevenlabs |
| `finance_cancel_action` | POST | `/api/voice/finance/cancel` | elevenlabs |
| `bank_to_binance_flow` | POST | `/api/voice/finance/flow/bank-to-binance` | elevenlabs |
| `binance_to_bank_flow` | POST | `/api/voice/finance/flow/binance-to-bank` | elevenlabs |
| `check_invoices` | GET | `/api/voice/invoices/check` | elevenlabs |
| `invoice_summary` | GET | `/api/voice/invoices/summary` | elevenlabs |
| `pluggy_connect_start` | POST | `/api/voice/finance/pluggy/connect/start` | elevenlabs |
| `pluggy_known_items` | GET | `/api/voice/finance/pluggy/items/known` | elevenlabs |
| `pluggy_operations` | GET | `/api/voice/finance/pluggy/operations` | elevenlabs |
| `pluggy_probe_items` | POST | `/api/voice/finance/pluggy/items/probe` | elevenlabs |
| `pluggy_refresh_items` | POST | `/api/voice/finance/pluggy/items/refresh` | elevenlabs |
| `pluggy_run_operation` | POST | `/api/voice/finance/pluggy/run` | elevenlabs |

### Domain: System (12 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `get_system_status` | GET | `/api/system/current` | builtin |
| `check_services` | GET | `/api/voice/ops/services` | builtin |
| `restart_service` | POST | `/api/voice/ops/services/restart` | builtin |
| `deploy_rainmaker` | POST | `/api/voice/ops/deploy` | builtin |
| `check_ecosystem` | GET | `/api/voice/ops/ecosystem` | builtin |
| `shell_exec` | POST | `/api/voice/shell/exec` | builtin |
| `read_vps_file` | GET | `/api/voice/read` | builtin |
| `write_vps_file` | POST | `/api/voice/write` | builtin |
| `edit_file` | POST | `/api/voice/fs/edit` | builtin |
| `configure` | POST | `/api/voice/config/set` | builtin |
| `get_config` | GET | `/api/voice/config/get` | builtin |
| `run_vps_command` | POST | `/api/voice/shell` | elevenlabs |

### Domain: Comms (12 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `search_web` | POST | `/api/voice/search-web` | builtin |
| `deep_research` | POST | `/api/voice/deep-research` | builtin |
| `recall_memory` | GET | `/api/voice/memory` | builtin |
| `send_whatsapp` | POST | `/api/voice/whatsapp` | elevenlabs |
| `openclaw_agent` | POST | `/api/voice/openclaw` | elevenlabs |
| `read_email` | GET | `/api/voice/google/email/read` | elevenlabs |
| `search_emails` | GET | `/api/voice/google/email/search` | elevenlabs |
| `send_email` | POST | `/api/voice/google/email/send` | elevenlabs |
| `list_labels` | GET | `/api/voice/google/email/labels` | elevenlabs |
| `list_events` | GET | `/api/voice/google/calendar/list` | elevenlabs |
| `create_event` | POST | `/api/voice/google/calendar/create` | elevenlabs |
| `search_calendar` | GET | `/api/voice/google/calendar/search` | elevenlabs |

### Domain: Media (16 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `list_youtube` | GET | `/api/voice/youtube/list` | elevenlabs |
| `process_youtube` | POST | `/api/voice/youtube/process` | elevenlabs |
| `search_youtube` | GET | `/api/voice/youtube/search` | elevenlabs |
| `list_drive_files` | GET | `/api/voice/google/drive/list` | elevenlabs |
| `search_drive` | GET | `/api/voice/google/drive/search` | elevenlabs |
| `upload_to_drive` | POST | `/api/voice/google/drive/upload` | elevenlabs |
| `list_tags` | GET | `/api/voice/tags/list` | elevenlabs |
| `search_tags` | GET | `/api/voice/tags/search` | elevenlabs |
| `tag_entity` | POST | `/api/voice/tags/add` | elevenlabs |
| `get_entity_tags` | GET | `/api/voice/tags/entity` | elevenlabs |
| `factory_run` | POST | `/api/voice/factory/run` | elevenlabs |
| `factory_specs` | GET | `/api/voice/factory/specs` | elevenlabs |
| `factory_status` | GET | `/api/voice/factory/status` | elevenlabs |
| `factory_tasks` | GET | `/api/voice/factory/tasks` | elevenlabs |
| `factory_task_detail` | GET | `/api/voice/factory/task` | elevenlabs |
| `factory_transcribe` | POST | `/api/voice/factory/transcribe` | elevenlabs |

### Meta Tools (6 tools)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `register_tool` | -- | (python-native) | builtin |
| `disable_tool` | -- | (python-native) | builtin |
| `enable_tool` | -- | (python-native) | builtin |
| `list_tools` | -- | (python-native) | builtin |
| `rainmaker_api` | * | (user-specified) | builtin |
| `manage_ui_state` | POST | `/api/voice/ui_control` | builtin |

### Remaining (MCP, Transfer, etc.)

| Name | Method | Path | Source |
|------|--------|------|--------|
| `call_mcp_tool` | POST | `/api/voice/mcp/call` | elevenlabs |
| `get_mcp_schema` | GET | `/api/voice/mcp/schema` | elevenlabs |
| `list_mcp_servers` | GET | `/api/voice/mcp/servers` | elevenlabs |
| `transfer_data` | POST | `/api/voice/transfer` | elevenlabs |
| `transfer_status` | GET | `/api/voice/transfer/status` | elevenlabs |
| `search_vps_files` | GET | `/api/voice/search` | elevenlabs |
| `scan_ecosystem_tdj` | POST | `/api/voice/ops/tdj` | elevenlabs |
| `run_reverse_sync` | POST | `/api/voice/ops/reverse-sync` | elevenlabs |
| `check_activity` | GET | `/api/voice/activities` | builtin |
| `edit_self` | POST | `/api/voice/self/edit` | builtin |
| `edit_frontend` | POST | `/api/voice/frontend/edit` | builtin |
| `pluggy_refresh_item` | POST | `/api/voice/finance/pluggy/item/refresh` | elevenlabs |
| `pluggy_submit_mfa` | POST | `/api/voice/finance/pluggy/item/mfa` | elevenlabs |

---

## Multi-Step Tools (Need Composite Endpoints)

3-4 tools in the current if/elif chain do multi-step HTTP calls. These need new composite dashboard endpoints so they become single-shot ToolSpec entries:

| Tool | Current Behavior | New Endpoint |
|------|-----------------|--------------|
| `switch_voice_provider` | POST switch + POST callback on new provider | `/api/voice/provider/switch-full` |
| `toggle_auto_trading` | GET status or POST preferences (branching on action) | `/api/trading/auto-entry/toggle` |

---

## File Layout on VPS

```
/opt/rainmaker-dash/
  tool_registry.py           # NEW ~250 LOC: ToolSpec, ToolRegistry, execute()
  tools/                     # NEW: domain-grouped tool definitions
    __init__.py              # imports all below to populate registry
    trading.py               # ~8 tools
    voice.py                 # ~12 tools
    finance.py               # ~15 tools
    system.py                # ~12 tools
    comms.py                 # ~12 tools
    media.py                 # ~16 tools
    meta.py                  # ~6 tools (register/disable/enable/list/rainmaker_api)
  voice_tools.py             # MODIFIED: thin shim → registry
  voice_tool_exec.py         # MODIFIED: thin shim → registry.execute()
  voice_tools_elevenlabs.py  # MODIFIED: thin shim (data moved to tools/*.py)
  tools_http_api.py          # MODIFIED: reads from live registry
```

## Consumer Impact

Zero breaking changes. Existing imports keep working via shims:

| Consumer | Current Import | Shim Target |
|----------|---------------|-------------|
| `llm_proxy.py` | `voice_tools.tools_for_chat_completions()` | `registry.for_chat_completions()` |
| `voice_brain.py` | `voice_tools.tools_for_openai()` | `registry.for_openai()` |
| `omniscience.py` | `voice_tools.get_all_tools()` | `registry.all()` |
| `voice_tool_exec.py` | 70+ if/elif chain | `registry.execute()` |

---

## Implementation Phases

| Phase | What | LOC | Risk |
|-------|------|-----|------|
| 1 | Create `tool_registry.py` (ToolSpec + ToolRegistry) | ~250 | Low |
| 2 | Migrate ELEVENLABS tools to `tools/*.py` | ~200 | Zero (mechanical) |
| 3 | Migrate TOOL_ROUTES tools to `tools/*.py` | ~50 | Zero (mechanical) |
| 4 | Migrate if/elif custom tools (may need new endpoints) | ~150 | Medium |
| 5 | Wire shims in voice_tools.py, voice_tool_exec.py | ~100 | Low |
| 6 | Omniscience sync + /api/tools introspection | ~50 | Low |

**Total: ~650 LOC new, ~450 LOC removed. Net +200 LOC.**

---

## Verification

```bash
# 1. Registry loads
python3 -c "from tool_registry import registry; print(len(registry.all()), 'tools')"

# 2. Introspection endpoint
curl http://127.0.0.1:8100/api/tools | python3 -m json.tool | head

# 3. WhatsApp tool call (via gateway)
# Send: "what are my positions" → should trigger get_trading_status

# 4. Voice call → tools work on all tiers

# 5. ElevenLabs sync
python3 -c "from omniscience import sync; sync()"
```

---

## Governance

| Artifact | Location |
|----------|----------|
| This spec | `.agent/specs/RAINMAKER_TOOL_REGISTRY.md` |
| Sync macro | `.agent/macros/library/MACRO-003-tool-registry-sync.yaml` |
| Implementation | `wave/rainmaker/tool_registry.py` + `wave/rainmaker/tools/` |
| Deploy target | `/opt/rainmaker-dash/` on rainmaker VPS |
| RoR entry | REG-015 in `.agent/registry/REGISTRY_OF_REGISTRIES.yaml` |

---

*Created: 2026-02-27*
*Spec follows Concepts/Objects duality from KERNEL.md*
