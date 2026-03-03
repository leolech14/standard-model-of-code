# Rainmaker Tool Registry -- Pre-Maintenance Report

> **Date:** 2026-02-28 07:30 UTC
> **Author:** Claude Opus 4.6
> **VPS:** rainmaker (srv1325721, Tailscale 100.119.234.42)
> **Service:** rainmaker-dash (active, uptime 235s post-deploy)

---

## What Changed

A read-only tool registry was deployed alongside the existing execution system. No existing tool execution was modified.

### New Files (11 files, 1,788 LOC)

| File | LOC | Purpose |
|------|-----|---------|
| `tool_registry.py` | 362 | ToolSpec dataclass + ToolRegistry singleton |
| `tools/__init__.py` | 14 | Auto-imports all domain modules |
| `tools/trading.py` | 122 | 8 tools: positions, auto-trading, market state, cashout |
| `tools/voice.py` | 189 | 14 tools: providers, calls, LLM modes, self-knowledge |
| `tools/finance.py` | 193 | 17 tools: Pluggy, invoices, bank flows |
| `tools/system.py` | 182 | 12 tools: VPS status, services, files, shell, config |
| `tools/comms.py` | 157 | 12 tools: web search, email, calendar, WhatsApp, OpenClaw |
| `tools/media.py` | 198 | 16 tools: YouTube, Drive, tags, factory |
| `tools/meta.py` | 140 | 8 tools: generic API, UI state, self-editing, tool management |
| `tools/ops.py` | 125 | 9 tools: MCP, transfers, activity, TDJ, reverse sync |
| `tools_http_api.py` | 106 | Rewritten: reads from live registry instead of nonexistent YAML |

### Modified Files (1 file, 1 line)

| File | Change |
|------|--------|
| `app.py` | Added `path.startswith("/api/tools")` to auth whitelist (line ~275) |

### Untouched Files (verified by timestamp)

| File | Size | Last Modified | Status |
|------|------|---------------|--------|
| `voice_tools.py` | 32,765 | Feb 27 16:48 | Unchanged -- still source of truth for execution |
| `voice_tool_exec.py` | 19,447 | Feb 28 01:26 | Unchanged -- still handles all tool dispatch |
| `voice_tools_elevenlabs.py` | 35,011 | Feb 27 16:40 | Unchanged |

---

## Deployment Architecture (Critical Knowledge)

### File flow

```
Mac (this repo)
  wave/rainmaker/tool_registry.py
  wave/rainmaker/tools/*.py
  wave/rainmaker/tools_http_api.py
        |
        | scp (manual)
        v
VPS Repo: /root/PROJECTS_all/PROJECT_openclaw/dashboard/
        |
        | rainmaker-deploy (rsync, backup, validate)
        v
VPS Deployed: /opt/rainmaker-dash/
        |
        | systemctl restart rainmaker-dash
        v
Live at :8100
```

### Rules learned the hard way

1. **NEVER scp directly to /opt/rainmaker-dash/**. Files get overwritten on next deploy or restart. Always deploy to the repo directory first, then run `rainmaker-deploy`.
2. **Syncthing IS running** (process, not systemd unit). It syncs the repo directory from Mac.
3. **`rainmaker-deploy`** is at `/usr/local/bin/rainmaker-deploy`. It rsyncs from repo to /opt, with backup. Protected dirs: `venv/`, `models/`, `data/`, `logs/`.
4. **Ecosync lock** at `/tmp/ecosync.lock` -- if stale, `rm -f` it. Used by reverse-sync and deploy to prevent concurrent operations.
5. **`.pyc` cache** can serve stale code after file replacement. Delete `__pycache__/*.pyc` for changed files before restart.
6. **Auth middleware** in `app.py` blocks all `/api/*` routes by default. New public endpoints must be added to the whitelist.

---

## What's Live Now

### Endpoints

| Endpoint | Auth | Returns |
|----------|------|---------|
| `GET /api/tools` | Public | 94 enabled tools with full descriptions |
| `GET /api/tools?tag=trading` | Public | Filtered by tag (8 trading tools) |
| `GET /api/tools?include_disabled=true` | Public | All 96 including 2 legacy aliases |
| `GET /api/tools/{name}` | Public | Single tool detail with parameters |
| `GET /api/tools/tags/list` | Public | 15 tags with counts |

### Registry Numbers

| Metric | Value |
|--------|-------|
| Total tools | 96 |
| Enabled | 94 |
| Disabled | 2 (check_llm_mode, set_llm_mode -- legacy aliases) |
| Tags | 15 (trading, voice, finance, system, comms, media, meta, ops, pluggy, google, mcp, research, tags, youtube, factory) |
| Avg description | 137 chars (restored from 39 chars) |
| Total description chars | 12,874 (restored from 3,469) |

### Checksums (deployed = repo)

```
3d6bda1ca558f1a561efbd0a01c4ffc3  tool_registry.py
c32994a93091edcf826c76117e65dfa3  tools_http_api.py
```

---

## What the Registry Does NOT Do

- Does NOT replace `voice_tool_exec.py` for execution. All tool dispatch still goes through the existing if/elif chain.
- Does NOT replace `voice_tools.py` or `voice_tools_elevenlabs.py` for tool definitions used by the execution path. Those files remain the source of truth for runtime.
- Does NOT push to ElevenLabs (omniscience.sync is not wired).
- The `execute()` method exists in tool_registry.py but nothing calls it. It's inert.

---

## Verification Commands

Run these to confirm health:

```bash
# 1. Service status
ssh rainmaker 'systemctl is-active rainmaker-dash'
# Expected: active

# 2. Registry endpoint
ssh rainmaker 'curl -s http://127.0.0.1:8100/api/tools | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[\"summary\"])"'
# Expected: {"total": 96, "enabled": 94, "disabled": 2, "returned": 94}

# 3. Existing execution path (trading API)
ssh rainmaker 'curl -s http://127.0.0.1:8100/api/trading/current | python3 -c "import sys,json; print(\"OK\" if json.load(sys.stdin) else \"EMPTY\")"'
# Expected: OK

# 4. Health check
ssh rainmaker 'curl -s http://127.0.0.1:8100/api/health | python3 -c "import sys,json; print(json.load(sys.stdin)[\"status\"])"'
# Expected: ok

# 5. File integrity
ssh rainmaker 'md5sum /opt/rainmaker-dash/tool_registry.py /root/PROJECTS_all/PROJECT_openclaw/dashboard/tool_registry.py'
# Expected: same hash on both lines
```

---

## Rollback

If anything goes wrong:

```bash
# Remove new files from repo (source of truth)
ssh rainmaker 'rm -f /root/PROJECTS_all/PROJECT_openclaw/dashboard/tool_registry.py'
ssh rainmaker 'rm -rf /root/PROJECTS_all/PROJECT_openclaw/dashboard/tools/'

# Restore original tools_http_api.py from backup
ssh rainmaker 'ls /opt/rainmaker-dash-backups/ | tail -1'  # find latest backup
ssh rainmaker 'cd /opt/rainmaker-dash-backups && tar xzf <latest>.tar.gz tools_http_api.py -C /root/PROJECTS_all/PROJECT_openclaw/dashboard/'

# Revert app.py auth whitelist change
ssh rainmaker 'cd /root/PROJECTS_all/PROJECT_openclaw/dashboard && sed -i "/api\/tools/d" app.py'

# Deploy clean state
ssh rainmaker 'rainmaker-deploy'
ssh rainmaker 'systemctl restart rainmaker-dash'
```

---

## Next Steps (Not Started)

These are optional future moves. None are required for the registry to function as-is.

| Step | What | Risk | Effort |
|------|------|------|--------|
| Wire shims | Make `voice_tools.py` delegate to registry for definitions | Medium -- touches execution path | 2h |
| Wire executor | Make `voice_tool_exec.py` use `registry.execute()` | High -- replaces dispatch chain | 4h |
| Omniscience sync | Have `omniscience.sync()` read from registry | Low -- read-only | 30m |
| Runtime persistence | Set `runtime_path` on singleton for runtime tools | Low | 15m |
| Composite endpoints | Create `/api/trading/auto-entry/toggle` and `/api/voice/provider/switch-full` on VPS | Medium -- new server code | 2h |

---

## Local Files (Mac)

Canonical source in this repo:

```
wave/rainmaker/
  __init__.py              Package marker
  tool_registry.py         Core: ToolSpec + ToolRegistry (362 LOC)
  tools_http_api.py        API endpoint (106 LOC)
  tools/
    __init__.py            Auto-import all domain modules
    trading.py             8 tools
    voice.py               14 tools (2 disabled legacy aliases)
    finance.py             17 tools
    system.py              12 tools
    comms.py               12 tools
    media.py               16 tools
    meta.py                8 tools (includes __dynamic__ and __native__: sentinels)
    ops.py                 9 tools
```

Governance artifacts:

```
.agent/specs/RAINMAKER_TOOL_REGISTRY.md    Architectural spec
.agent/macros/library/MACRO-003-*.yaml     Deploy macro (DRAFT, not used -- deploy manually)
.agent/registry/REGISTRY_OF_REGISTRIES.yaml  REG-015 entry
.agent/macros/INDEX.md                     MACRO-003 listed
```
