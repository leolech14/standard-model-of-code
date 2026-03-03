# Rainmaker Ecosystem -- Deep Architectural Audit

> Generated: 2026-02-27 by Claude Opus 4.6 (ongoing -- raw findings, no conclusions)
> Last updated: 2026-02-27 22:15 UTC (second deep-dive pass)
> Scope: Full inventory, coupling analysis, mismatch catalog, SMOC classification
> Server: Hostinger srv1325721 (82.25.77.221 / Tailscale 100.119.234.42)
> Stats: 15 processes, 17 ports, 96 dashboard modules (35.7K LOC), 28 timers, 95 sync conflicts, 21 mismatch findings

---

## 1. AS-IS: Complete Inventory

### 1.1 Active Processes (by memory footprint)

| Process | PID | RSS | Service | Port | Role |
|---------|-----|-----|---------|------|------|
| OpenClaw Gateway | 591965 | 400MB | `openclaw-gateway.service` | 18789 (WS), 18792, 3334 | Message gateway + AI agent |
| Rainmaker Dashboard | 545721 | 230MB | `rainmaker-dash.service` | 8100 (HTTP) | Console UI + trading station + voice |
| Futures Monitor | 2368824 | 42MB | `futures-monitor.service` | -- | Trading bot + risk engine |
| Syncthing | 199354 | 232MB | `syncthing.service` | 22000, 8384 | File sync (Mac <-> VPS) |
| Caddy | 367044 | 54MB | `caddy.service` | 80, 443 | Reverse proxy + TLS |
| Cloudflared | 3488429 | 42MB | `cloudflared.service` | 20241 | Cloudflare tunnel |
| Tailscale | 839 | 71MB | `tailscaled.service` | 41641 | Mesh VPN |
| Grafana | 2409 | 128MB | Docker | 3000 | Log visualization |
| Loki | 2419 | 91MB | Docker | 3100 | Log aggregation |
| Promtail | 2421 | 55MB | Docker | -- | Log shipping |
| Authelia | 2444 | 35MB | Docker | 9091 | Auth proxy (SSO) |
| Portainer | -- | -- | Docker | 9000, 9443 | Container management |
| OpenClaw Sandbox | -- | -- | Docker | -- | Agent sandbox container |
| Netdata | 2926947 | 177MB | `netdata.service` | 19999 | System monitoring |
| Fail2Ban | 3242738 | 99MB | `fail2ban.service` | -- | Intrusion prevention |

### 1.2 External Domains (Caddy + Cloudflare Tunnel)

| Domain | Backend | Auth |
|--------|---------|------|
| `console.centralmcp.ai` | Dashboard :8100 | Direct (dashboard auth) |
| `dashboard.centralmcp.ai` | Redirects to Tailscale hostname | -- |
| `auth.centralmcp.ai` | Authelia :9091 | Authelia SSO |
| `docker.centralmcp.ai` | Portainer :9000 | Authelia forward-auth |
| `code.centralmcp.ai` | VS Code :8080 | Authelia forward-auth |
| `monitor.centralmcp.ai` | Netdata :19999 | Direct (Caddy) |
| `logs.centralmcp.ai` | Grafana :3000 | Authelia forward-auth |
| `agent.centralmcp.ai` | :8000 (dead) | -- |

### 1.3 Communication Channels

| Channel | Protocol | Target | State |
|---------|----------|--------|-------|
| WhatsApp | Baileys Web via OpenClaw | +555496816430 (self) -> +555499628402 (Leo) | Active |
| Telegram | Bot API via OpenClaw | @Rainmaker3bot -> chat 1124215633 | Broken (404 on bot token) |
| Voice (Twilio) | WebRTC/SIP | +18142507176 -> ElevenLabs / LLM | Active |
| Voice (Direct) | WebSocket | Dashboard -> ElevenLabs ConvAI | Active |

### 1.4 Secrets Management

All secrets in **Doppler** (`ai-tools/prd`, 99 secrets). Injected via `doppler run` in systemd override files. No `.env` files relied upon.

### 1.5 Scheduled Jobs

| Schedule | Source | Action |
|----------|--------|--------|
| 8:00 AM BRT daily | OpenClaw cron | Daily briefing via agent -> WhatsApp |
| Every 6 hours | OpenClaw cron | Health monitor via agent -> WhatsApp |
| 3:00 AM UTC daily | System crontab | Git backup of workspace |
| 4:00 AM UTC daily | System crontab | Full GCS backup |
| Every 6 hours | System crontab | Comprehensive system tests |

---

## 2. AS-IS: Data Flow Map

```
                          INTERNET
                             |
                    [Caddy + Cloudflare]
                    /    |    |    \
               :8100  :3000 :9000 :19999
                 |      |     |      |
            Dashboard Grafana Portainer Netdata
                 |
    +------------+------------+
    |            |            |
[WS Bridge]  [REST API]  [SSE Events]
    |            |            |
    +-----+------+            |
          |                   |
    [OpenClaw Gateway :18789] |
     /    |     |     \       |
    /     |     |      \      |
WhatsApp  TG  Voice   [Agent] |
    |     |     |        |    |
    |     |     |     [Gemini |
    |     |     |      2.5    |
    |     |     |      Flash] |
    |     |     |             |
    +--+--+--+--+----------+--+
       |                   |
   [fm_notify.py]    [collectors/]
       |                   |
   [Futures Monitor]  [trading_station.py]
       |                   |
       +--------+----------+
                |
        [Binance Futures API]
                |
    +-----------+-----------+
    |           |           |
[thresholds] [trade_mode] [indicators]
  .json        .json        .json
    |           |           |
    +-----------+-----------+
    (Hot-reload every 1 second)
```

---

## 3. COUPLING ANALYSIS: What's Broken

### 3.1 The WhatsApp Contention Problem (Critical)

**Three independent systems compete for the same WhatsApp pipe:**

| Consumer | Mechanism | Volume | Priority |
|----------|-----------|--------|----------|
| Futures Monitor (`fm_notify.py`) | Direct WS to gateway | Up to 240 msgs/hour in `full` mode | Highest (financial risk) |
| OpenClaw Agent (Gemini) | Internal agent -> channel | On-demand (user messages + auto-reply) | Medium (conversational) |
| OpenClaw Cron Jobs | Agent turn -> channel | 2x/day (briefing + health) | Low (scheduled) |

**Root cause:** No message bus, no priority queue, no channel multiplexing. All three hammer `ws://127.0.0.1:18789` with `method: "send"` and hope for the best. The futures monitor has its own rate limiter (240/hour) but the gateway has no concept of message priority or sender identity.

### 3.2 Shared State on Disk (Fragile)

| File | Writers | Readers | Risk |
|------|---------|---------|------|
| `thresholds.json` | Dashboard API, OpenClaw `trading-thresholds` skill | Futures Monitor (poll 1s), Dashboard, `trading_constants.py` | Race condition on concurrent write |
| `trade_mode.json` | Dashboard config panel | Futures Monitor (poll), Dashboard | Stale reads if monitor doesn't poll |
| `openclaw.json` | `openclaw config set`, manual editing | Gateway (startup), CLI (every call) | Token desync (already burned us) |
| `finance.db` | Dashboard (multiple writers) | Dashboard (multiple readers) | SQLite WAL should handle it, but no schema migrations |

### 3.3 Token Architecture (Fragile)

Three-layer token problem (documented in OPENCLAW_RAINMAKER_DOCS.md):
- **Doppler** injects `OPENCLAW_GATEWAY_TOKEN` at runtime
- **openclaw.json** has `gateway.auth.token` (must match manually)
- **`.gateway-token`** file is stale legacy (never updated)
- **Futures Monitor** reads `GATEWAY_TOKEN` from Doppler env (via `doppler run`)
- **Dashboard** reads `GATEWAY_TOKEN` from Doppler env (via `doppler run`)

All three must agree or you get `token_mismatch` flood.

### 3.4 Module Boundary Violations

| Violation | Description |
|-----------|-------------|
| `fm_config.py` imports from `/opt/rainmaker-dash/trading_constants.py` | Monitor depends on deployed dashboard code at a hard-coded path |
| Dashboard `collectors/binance.py` re-exports from `trading_station.py` | Backward-compat shim masking a merge |
| Monitor sends messages directly via gateway WS | Bypasses OpenClaw agent entirely, no audit trail in agent sessions |
| Health Guardian writes to `/var/lib/health-guardian/` | OpenClaw cron reads it, but no formal contract |
| Dashboard `ecosystem.py` SSHs to Mac | Cross-machine dependency with no health check |

### 3.5 Naming Confusion

| Old Name (Monitor) | New Name (Dashboard) | Used Where |
|--------------------|---------------------|------------|
| GREEN | ALLOCATED | `fm_config.py` has `_ZONE_NAME_MAP` to translate |
| YELLOW | ELEVATED | `trading_constants.py` uses new names |
| RED | TRIM | `thresholds.json` uses new names |
| EMERGENCY | FLATTEN | Monitor normalizes on load |
| CRITICAL | CAP | Monitor synthesizes NUCLEAR from CAP |
| NUCLEAR | (none) | Only exists in monitor-side logic |

---

## 4. SMOC CLASSIFICATION

Using Standard Model of Code principles to classify the Rainmaker ecosystem:

### 4.1 Scale Classification (S-Level)

| Component | Scale | Rationale |
|-----------|-------|-----------|
| `thresholds.json` | S3 (File) | Single config file, hot-reloaded |
| `fm_notify.py` | S6 (Module) | Single-purpose notification module |
| `futures_monitor.py` + `fm_*.py` | S8 (Service) | Standalone daemon, 2631 LOC, 7 modules |
| OpenClaw Gateway | S9 (Platform) | Multi-channel message platform, plugins, agent runtime |
| Rainmaker Dashboard | S9 (Platform) | 35,698 LOC, 100+ modules, REST + WS + SSE + Voice |
| Rainmaker Ecosystem (total) | S11 (Organization) | Multi-service, multi-protocol, cross-machine mesh |

### 4.2 Layer Classification

| Component | Layer | Should Be |
|-----------|-------|-----------|
| `trading_constants.py` | L2 (Data) | L2 -- correct |
| `thresholds.json`, `trade_mode.json` | L2 (Data) | L2 -- correct |
| `fm_binance.py`, `fm_config.py` | L3 (Logic) | L3 -- correct |
| `fm_notify.py` | L4 (Integration) | L5 (Gateway) -- it's acting as a gateway client |
| `fm_risk.py`, `fm_triggers.py` | L3 (Logic) | L3 -- correct |
| `futures_monitor.py` (main loop) | L5 (Orchestration) | L6 (Service) -- it orchestrates all fm_* modules |
| OpenClaw Gateway | L6 (Service) | L7 (Platform) -- multi-tenant, multi-channel |
| Rainmaker Dashboard | L6 (Service) | L7 (Platform) -- same reasoning |
| Caddy + Cloudflare | L7 (Infrastructure) | L7 -- correct |

### 4.3 Dimension Analysis

| Dimension | Current State | Problem |
|-----------|---------------|---------|
| **Structural** | 3 services, loosely defined boundaries | No service contracts |
| **Behavioral** | Event-driven (WS) + polling (files) + cron | Hybrid makes debugging hard |
| **Temporal** | Mix of real-time (1s) and batch (6h) | No temporal isolation |
| **Relational** | Hard-coded paths, shared JSONs, direct WS | Tight coupling everywhere |
| **Contextual** | All run as root, all share Doppler secrets | No privilege separation |
| **Qualitative** | No tests, no contracts, no health checks | Fragile |
| **Quantitative** | ~38K LOC total (dashboard + monitor) | Manageable |
| **Identity** | centralmcp.ai domain, but it's really "Rainmaker" | Naming confusion |

---

## 5. TO-BE: Clean Architecture

### 5.1 Design Principles

1. **Single Responsibility**: Each service does ONE thing
2. **Channel Isolation**: Trading and personal assistant use separate channels
3. **Contract-First**: Services communicate through defined interfaces, not shared files
4. **Observable**: Every service emits structured events to a central bus
5. **Fail-Safe**: Financial alerts always get through, even if everything else breaks

### 5.2 Service Decomposition

```
RAINMAKER ECOSYSTEM (S11)
|
+-- LAYER 7: INFRASTRUCTURE
|   |
|   +-- [Caddy]           Reverse proxy + TLS termination
|   +-- [Cloudflare]      Tunnel for external access
|   +-- [Tailscale]       Mesh VPN (Mac <-> VPS)
|   +-- [Docker]          Container runtime
|   +-- [Doppler]         Secrets management (external SaaS)
|
+-- LAYER 6: OBSERVABILITY
|   |
|   +-- [Loki]            Log aggregation
|   +-- [Grafana]         Dashboards + alerting
|   +-- [Promtail]        Log shipping
|   +-- [Netdata]         System metrics
|   +-- [Fail2Ban]        Intrusion detection
|
+-- LAYER 5: PLATFORM SERVICES
|   |
|   +-- [OpenClaw Gateway]        MESSAGE BUS (sole owner of WhatsApp/TG/Voice)
|   |   |-- Channels: WhatsApp, Telegram, Voice
|   |   |-- Agent Runtime: Gemini 2.5 Flash
|   |   |-- Skills: 20+ (bird, github, trading-thresholds, etc.)
|   |   |-- Plugins: WhatsApp, Telegram, Voice-Call, LLM-Task
|   |   |-- Cron: Daily Briefing, Health Monitor
|   |   '-- Port: 18789 (WS, loopback only)
|   |
|   +-- [Rainmaker Console]       CONTROL PLANE (observe + configure)
|       |-- Trading Station: Binance read + threshold config
|       |-- Voice Gateway: Twilio + ElevenLabs + LLM bridge
|       |-- Finance: Pluggy integration, Gmail scanning
|       |-- Ecosystem: Tailscale mesh, GCS transfers
|       |-- Activity Bus: Event ingest + SSE broadcast
|       '-- Port: 8100 (HTTP)
|
+-- LAYER 4: DOMAIN SERVICES
|   |
|   +-- [Futures Monitor]         TRADING ENGINE (Binance-specific)
|   |   |-- Risk State Machine: 6 zones
|   |   |-- Order Management: trailing profit, auto-entry
|   |   |-- Trigger Evaluation: thesis, momentum, sniper, mean-reversion
|   |   '-- Notification: via Gateway WS (not direct WhatsApp)
|   |
|   +-- [Health Guardian]         HEALTH ENGINE
|       |-- Circuit Breaker: auto-restart on failure
|       |-- Model Monitoring: provider health
|       '-- State: /var/lib/health-guardian/
|
+-- LAYER 3: SHARED DATA
|   |
|   +-- [trading_constants.py]    Zone definitions (SSOT)
|   +-- [thresholds.json]         Risk zone thresholds
|   +-- [trade_mode.json]         Notification preferences
|   +-- [openclaw.json]           Gateway + agent config
|   +-- [finance.db]              Financial data (SQLite)
|   +-- [LanceDB + SQLite]        Agent memory
|
+-- LAYER 2: EXTERNAL INTEGRATIONS
    |
    +-- [Binance Futures API]     Trading data + order execution
    +-- [Pluggy API]              Open finance (bank data)
    +-- [ElevenLabs]              Voice synthesis + STT
    +-- [Twilio]                  Phone calls + webhook
    +-- [Google Workspace]        Gmail, Calendar, Drive
    +-- [LLM Providers]           Gemini, Claude, xAI, Cerebras, OpenRouter
    +-- [Syncthing]               File sync (Mac <-> VPS)
```

### 5.3 Key Architecture Changes

#### Change 1: Channel Ownership (Critical)

**Current:** Three systems fight over WhatsApp.
**Proposed:** OpenClaw Gateway is the SOLE channel owner. All others go through it.

```
BEFORE:
  Futures Monitor --[direct WS]--> Gateway --> WhatsApp
  Agent           --[internal]---> Gateway --> WhatsApp
  Cron            --[internal]---> Gateway --> WhatsApp

AFTER:
  Futures Monitor --[WS: method=send, priority=critical]--> Gateway
  Agent           --[internal, priority=normal]-----------> Gateway
  Cron            --[internal, priority=low]--------------> Gateway
                                                               |
                                        [Priority Queue + Rate Limiter]
                                               |         |
                                           WhatsApp   Telegram
```

**Implementation:**
- Gateway already receives messages from all three via WS `method: "send"`
- Add `priority` field to send params: `critical` (trading alerts), `normal` (agent), `low` (cron)
- Gateway rate-limits per-priority: critical always passes, normal gets 60/hour, low gets 10/hour
- Telegram becomes the OVERFLOW channel, not a fallback

#### Change 2: Eliminate Shared File Coupling

**Current:** Monitor reads `thresholds.json` every 1 second. Dashboard writes it. Race conditions possible.

**Proposed:** Dashboard exposes thresholds via HTTP API. Monitor polls HTTP instead of file.

```
BEFORE:
  Dashboard --[write]--> thresholds.json <--[poll 1s]-- Monitor

AFTER:
  Dashboard --[write]--> thresholds.json
  Dashboard --[serve]--> GET /api/thresholds (HTTP, cached 1s)
  Monitor   --[poll]---> GET /api/thresholds (1s interval)
```

This is a minimal change: `fm_config.py` replaces `open(THRESHOLDS_FILE)` with `requests.get("http://127.0.0.1:8100/api/thresholds")`. Dashboard already has the API endpoint.

#### Change 3: Unified Token Management

**Current:** Three separate token sources that must be manually synced.

**Proposed:** Single source of truth: Doppler. Everything reads from env.

```
BEFORE:
  Doppler --> OPENCLAW_GATEWAY_TOKEN (env at runtime)
  openclaw.json --> gateway.auth.token (config file, manual)
  .gateway-token --> legacy file (stale)

AFTER:
  Doppler --> OPENCLAW_GATEWAY_TOKEN (env at runtime)
  openclaw.json --> REMOVED (gateway reads env, not config)
  .gateway-token --> DELETED

  If config override needed: openclaw config set reads from Doppler
```

Until OpenClaw upstream supports env-only token, workaround: add a systemd ExecStartPre script that syncs Doppler token to openclaw.json before gateway starts.

#### Change 4: Unified Zone Naming

**Current:** Two naming systems with a translation layer.

**Proposed:** Standardize on the NEW names everywhere.

| Standard Name | Emoji | Max MR | Action |
|---------------|-------|--------|--------|
| ALLOCATED | Green | 33% | Normal |
| ELEVATED | Yellow | 50% | Warning |
| TRIM | Scissors | 60% | Microtrim |
| FLATTEN | Swords | 66% | Flatten worst 3 |
| CAP | Stop | 75% | Flatten + trim heavy |
| NUCLEAR | Skull | 100% | Kill all |

Monitor code gets refactored: replace all `GREEN`/`YELLOW`/`RED`/`EMERGENCY`/`CRITICAL` references with new names. Remove `_ZONE_NAME_MAP` translation layer.

#### Change 5: Notification Contract

Define a formal notification contract between Futures Monitor and Gateway:

```python
# Notification message schema (JSON over WS)
{
    "type": "req",
    "method": "send",
    "params": {
        "channel": "whatsapp",           # Primary channel
        "to": "+555499628402",
        "message": "...",
        "metadata": {
            "source": "futures-monitor",  # NEW: identify sender
            "priority": "critical",       # NEW: critical|normal|low
            "category": "trading",        # NEW: trading|system|personal
            "zone": "FLATTEN",            # NEW: current risk zone
            "dedup_key": "...",           # Existing
            "dedup_window": 60            # Existing
        }
    }
}
```

This doesn't require OpenClaw changes -- `metadata` fields are passed through. The Dashboard activity bus can use them for routing, filtering, and audit.

#### Change 6: Dashboard as Control Plane, Not Data Plane

**Current:** Dashboard runs voice calls, bridges WebSockets, manages finance, AND serves the UI.

**Proposed (future):** Split concerns:

| Concern | Service | Scale |
|---------|---------|-------|
| Console UI + API | `rainmaker-console` | S8 (Service) |
| Voice Gateway | `rainmaker-voice` | S8 (Service) |
| Finance Engine | `rainmaker-finance` | S7 (Module) within console |
| Trading Station | Keep in console | L5 (read-only view of Binance) |

**NOT recommended for now.** The Dashboard is 35K LOC but works. Splitting it would be a major refactor with no immediate user value. Instead: formalize the internal module boundaries with clear imports and add health checks.

---

## 6. SMOC CLASSIFICATION: TO-BE

### 6.1 Atom Classification

| Component | SMOC Atom | Type | Layer |
|-----------|-----------|------|-------|
| OpenClaw Gateway | Platform.MessageBroker | T1 | L7 |
| Rainmaker Console | Platform.ControlPlane | T1 | L7 |
| Futures Monitor | Service.TradingEngine | T1 | L6 |
| Health Guardian | Service.HealthMonitor | T1 | L5 |
| Caddy | Infrastructure.ReverseProxy | T0 | L8 |
| Cloudflare Tunnel | Infrastructure.Tunnel | T0 | L8 |
| Tailscale | Infrastructure.VPN | T0 | L8 |
| Doppler | Infrastructure.SecretsManager | T0 | L8 |
| Grafana+Loki | Observability.LogPlatform | T0 | L7 |
| Netdata | Observability.MetricsCollector | T0 | L7 |
| Binance API | ExternalService.Exchange | T0 | L1 |
| Pluggy API | ExternalService.OpenFinance | T0 | L1 |
| ElevenLabs | ExternalService.VoiceAI | T0 | L1 |
| LLM Providers | ExternalService.InferenceAPI | T0 | L1 |

### 6.2 Relationship Map (Directed)

```
Gateway ---[authenticates]--> Doppler
Gateway ---[routes_to]------> WhatsApp, Telegram, Voice
Gateway ---[runs]-----------> Agent (Gemini 2.5 Flash)
Gateway ---[schedules]------> Cron Jobs

Console ---[reads_from]-----> Binance API (read-only)
Console ---[bridges]--------> ElevenLabs, Twilio, LLMs
Console ---[sends_via]------> Gateway WS (notifications)
Console ---[stores_in]------> SQLite (finance.db, commlogs.db)
Console ---[syncs_with]-----> Mac (via Tailscale SSH)
Console ---[exposes]--------> HTTP API (:8100)

Monitor ---[sends_via]------> Gateway WS (trading alerts)
Monitor ---[reads_from]-----> Binance API (account, positions, orders)
Monitor ---[reads_config]---> thresholds.json, trade_mode.json
Monitor ---[imports]--------> trading_constants.py (from /opt/rainmaker-dash/)
Monitor ---[executes]-------> Binance API (orders: trim, flatten, kill)

Health  ---[reads]----------> Gateway health endpoint
Health  ---[reads]----------> System metrics
Health  ---[writes]---------> /var/lib/health-guardian/state.json
```

---

## 7. MISMATCH CATALOG (Raw Findings)

### 7.1 Phone Number Format Inconsistency

Two different phone numbers for the SAME person are used interchangeably:

| Format | Where Used |
|--------|-----------|
| `+555499628402` (12 digits) | `openclaw.json` allowFrom[0], `trade_mode.json` wa_target |
| `+5554999628402` (13 digits, extra `9`) | `openclaw.json` allowFrom[1], `fm_config.py` default, `voice_gateway.py`, `voice_core_api.py`, `invoice_api.py`, `voice_tools_elevenlabs.py`, Doppler `NOTIFICATION_WA_TARGET` |

Both are in the WhatsApp allowlist, suggesting someone noticed messages were failing and added the second format rather than fixing the root cause. Brazilian mobile numbers transitioned to 9-digit format (+55 DDD 9XXXX-XXXX) so `+5554999628402` is the correct E.164 format. The shorter `+555499628402` may still work via WhatsApp's number normalization but is technically wrong.

**Who wrote which?** The dashboard/monitor hardcode the 13-digit format. OpenClaw config panel and `trade_mode.json` have the 12-digit format. These were likely written by different agents/sessions.

### 7.2 Gateway WebSocket Protocol: 3 Different Implementations

Four independent WS clients connect to the OpenClaw gateway, using THREE different protocol dialects:

**Client A: Futures Monitor (`fm_notify.py`) -- Protocol v3 (correct)**
```json
// Step 1: Wait for connect.challenge
// Step 2: Send connect request
{"type": "req", "id": "uuid", "method": "connect", "params": {
    "minProtocol": 3, "maxProtocol": 3,
    "client": {"id": "cli", "version": "2026.2.3-1", "platform": "linux", "mode": "cli"},
    "auth": {"token": "..."}, "role": "operator", "scopes": ["operator.admin"]
}}
// Step 3: Wait for hello-ok
// Step 4: Send message
{"type": "req", "id": "uuid", "method": "send", "params": {"channel": "whatsapp", "to": "+...", "message": "..."}}
```

**Client B: Dashboard gateway collector (`collectors/gateway.py`) -- Protocol v3 (correct, matches A)**
Same protocol as A. Used only for health checks, never sends messages.

**Client C: Dashboard voice_gateway.py -- DIFFERENT protocol (simplified)**
```json
// Step 1: Wait for challenge
// Step 2: Send connect (FLAT, not nested in params)
{"type": "connect", "clientId": "cli", "token": "...", "minProtocol": 3, "maxProtocol": 3}
// Step 3: Send message (DIFFERENT method name)
{"type": "rpc", "method": "message.send", "params": {"target": "+...", "message": "..."}}
```

**Client D: Dashboard invoice_api.py -- REST API (completely different)**
```python
httpx.post("http://127.0.0.1:18789/v1/messages",
    json={"target": "+...", "message": "..."},
    headers={"Authorization": f"Bearer {token}"})
```

**Client E: Dashboard voice_core_api.py -- CLI subprocess (yet another approach)**
```python
subprocess.run(["doppler", "run", "--config", "prd", "--",
    "openclaw", "message", "send", "--channel", "whatsapp", "--target", target, "--message", message])
```

So there are **5 distinct paths** to send a WhatsApp message:
1. WS Protocol v3 (monitor) -- raw WS, correct protocol
2. WS Protocol v3 (collector) -- health check only
3. WS simplified protocol (voice_gateway) -- different wire format, unknown if it even works reliably
4. REST POST to /v1/messages (invoice_api) -- undocumented HTTP endpoint
5. CLI subprocess via doppler + openclaw CLI (voice_core_api) -- spawns a whole process per message

**Unknown:** Does the gateway actually support all 3 wire formats? Or are some of these silently failing?

### 7.3 Zone Naming: 5 Divergent Taxonomies

| Context | Zone 1 | Zone 2 | Zone 3 | Zone 4 | Zone 5 | Zone 6 |
|---------|--------|--------|--------|--------|--------|--------|
| `trading_constants.py` (SSOT) | ALLOCATED | ELEVATED | TRIM | FLATTEN | CAP | (none) |
| `thresholds.json` (on disk) | ALLOCATED | ELEVATED | TRIM | FLATTEN | CAP | (none) |
| `fm_config.py` fallback | GREEN | YELLOW | RED | EMERGENCY | CRITICAL | NUCLEAR |
| `fm_risk.py` runtime | GREEN | YELLOW | RED | EMERGENCY | CRITICAL | NUCLEAR |
| `fm_format.py` display | GREEN | YELLOW | RED | EMERGENCY | CRITICAL | NUCLEAR |
| `AGENTS.md` instructions | GREEN | YELLOW | RED | EMERGENCY | (none) | NUCLEAR |
| `trading-thresholds` skill | GREEN | YELLOW | RED | EMERGENCY | (none) | NUCLEAR |

**Key observations:**
- `trading_constants.py` has 5 zones (ALLOCATED through CAP). Monitor has 6 (GREEN through NUCLEAR). The translation layer in `fm_config._ensure_monitor_zone_names()` synthesizes NUCLEAR from CAP with a hardcoded `max=80`.
- `AGENTS.md` tells the AI agent that thresholds are "GREEN < 33%, YELLOW 33-66%, RED > 66%, EMERGENCY > 80%, NUCLEAR > 90%" -- but the actual `thresholds.json` on disk says ALLOCATED=33, ELEVATED=50, TRIM=60, FLATTEN=66, CAP=100. The documentation doesn't match reality.
- The `trading-thresholds` OpenClaw skill uses the OLD names and teaches the AI to write them to `thresholds.json` -- but the file now uses NEW names. If the AI follows the skill instructions, it would write `GREEN`/`YELLOW`/`RED` to a file that expects `ALLOCATED`/`ELEVATED`/`TRIM`, and the monitor's `_ensure_monitor_zone_names()` would skip translation (since `GREEN` is the old format) but with wrong thresholds.
- The thresholds in `AGENTS.md` (33/66/80/90) don't match the actual on-disk values (33/50/60/66/100).

### 7.4 Duplicate Binance API Clients

Two completely independent Binance API implementations exist:

| Module | Location | Functions | Usage |
|--------|----------|-----------|-------|
| `fm_binance.py` | Monitor (2631 LOC total) | `bget`, `bpost`, `bdelete`, `get_account`, `get_positions`, `place_market_open/close`, `partial_close`, `set_leverage` | Order execution, position monitoring |
| `trading_station.py` | Dashboard (35K LOC total) | `_bget`, `_sign`, `collect`, `get_account`, `get_positions`, `fetch_income_history`, `fetch_user_trades`, `SpotClient` class | Read-only data collection, spot/withdraw |

Both implement `get_account()` and `get_positions()` independently, with different response normalization. Both sign requests with HMAC-SHA256 using the same Binance API keys from Doppler. They're making parallel API calls to the same Binance endpoints for the same data.

**Additionally:** The monitor's `fm_trailing.py` lazy-loads `decision_engine.py` directly from `/opt/rainmaker-dash/`, creating a runtime import dependency from the monitor process INTO the dashboard's deployed code. If someone redeploys the dashboard and the `decision_engine.py` API changes, the monitor crashes.

### 7.5 Message Sender Inventory (Complete)

All systems that can send a WhatsApp/Telegram message:

| Sender | Mechanism | Has Rate Limit | Has Dedup | Logs to Activity | Logs to COMMLOG | Identifies Self |
|--------|-----------|----------------|-----------|-----------------|----------------|----------------|
| Futures Monitor | WS Protocol v3 | Yes (240/hr) | Yes (dedup_key) | Yes | No | No (shows as "cli") |
| OpenClaw Agent (Gemini) | Internal gateway | No | No | No | Via session JSONL | Yes (agent session) |
| OpenClaw Cron (Daily Briefing) | Agent turn -> channel | No | No | No | Via session JSONL | Yes (cron job id) |
| OpenClaw Cron (Health Monitor) | Agent turn -> channel | No | No | No | Via session JSONL | Yes (cron job id) |
| Dashboard voice tool | CLI subprocess | No | No | Yes | Yes | Yes ("rainmaker") |
| Dashboard invoice reminders | REST POST /v1/messages | No | No | Yes | No | No |
| Dashboard voice_gateway | WS simplified | No | No | Yes | No | No |
| OpenClaw `trading-thresholds` skill | Via agent | No | No | No | Via session | Yes (skill name) |
| OpenClaw `rainmaker-bridge` skill | Via dashboard API -> CLI | No | No | Yes (via dashboard) | Yes | Mixed |
| OpenClaw `daily-summary` skill | Via agent | No | No | No | Via session | Yes |

**10 distinct senders.** Only one (futures monitor) has any rate limiting. None of them identify themselves to the gateway in a way that would allow filtering or routing.

### 7.6 Dashboard Size and Scope

The Rainmaker Console is a **35,698 LOC** Python/FastAPI monolith with:

| Category | Modules | LOC | Scope |
|----------|---------|-----|-------|
| Voice system | 15 files (`voice_*.py`, `ws_bridge*.py`) | 5,809 | 6-tier voice gateway, Twilio/ElevenLabs/OpenAI/Grok/Gemini/self-hosted |
| Trading | 6 files | ~3,000 | Binance client, thresholds, trade mode, intelligence, scoring, decisions |
| Finance | 5 files | ~2,500 | Pluggy API, Gmail scanning, ledger, invoices, categorizer |
| Communication | 4 files | ~1,200 | COMMLOG, channels API, context router |
| Operations | 5 files | ~2,000 | Ecosystem scanner, workspace reader, file transfer, system health |
| Google | 2 files | ~500 | Gmail + Calendar + Drive |
| Activity | 2 files | ~800 | Event ingest + SSE broadcaster |
| AI/LLM | 4 files | ~1,500 | LLM proxy, omniscience, prompt assembler, signal pool |
| Auth | 3 files | ~600 | WebAuthn, core_auth, TOTP |
| UI | Templates + static | ~5,000+ | Jinja2 templates for 25+ pages |
| Infrastructure | Collectors, runtime_edges | ~800 | Background health polling |
| Backtest | 3 files | ~1,200 | Paper trading, historical analysis, strategy comparison |
| Other | Assorted | ~10,000+ | Compartments, automations, media, tags, factory, youtube, meet |

This is not a "dashboard" -- it's a full-stack platform operating as a single process.

### 7.7 Cross-Module Import Violations

| From | To | Path | Type |
|------|----|------|------|
| Monitor `fm_config.py` | Dashboard `trading_constants.py` | `sys.path.insert(0, "/opt/rainmaker-dash")` | Hard-coded path inject |
| Monitor `fm_trailing.py` | Dashboard `decision_engine.py` | `sys.path.insert(0, "/opt/rainmaker-dash")` | Lazy load, hard-coded |
| Dashboard `collectors/binance.py` | Dashboard `trading_station.py` | `from trading_station import get_account, get_positions, collect` | Backward-compat shim |

The monitor has zero dependency isolation from the dashboard. If dashboard deploys new code that changes `trading_constants.ZONE_ORDER` or `decision_engine` signatures, the monitor breaks silently or crashes.

### 7.8 Agent Configuration Drift

`AGENTS.md` (the instructions read by the OpenClaw AI agent on every session boot) contains:

1. **Stale threshold values:** States `GREEN < 33%, YELLOW 33-66%, RED > 66%, EMERGENCY > 80%, NUCLEAR > 90%` but actual on-disk config is `ALLOCATED=33, ELEVATED=50, TRIM=60, FLATTEN=66, CAP=100`
2. **References to nonexistent service:** "litellm.service" mentioned as "Do NOT re-enable" but no such service exists in systemd
3. **References to "health-guardian.timer":** `systemctl status health-guardian.timer` but actual unit names not verified
4. **83 voice tools listed** but the SKILL.md for `trading-thresholds` uses the old zone names
5. **The AGENTS.md doc itself is 650+ lines** -- this is the system prompt context injected into EVERY agent turn with Gemini 2.5 Flash. At ~1k tokens per turn overhead minimum.

### 7.9 Orphaned / Conflicting Configurations

| Item | Status |
|------|--------|
| `.gateway-token` file | Stale since Feb 4, never updated. Some OpenClaw internal code may still read it. |
| `openclaw.json` `channels.telegram.botToken` | Contains a token that returns 404 on `getMe`. Bot is dead. |
| `agent.centralmcp.ai` Cloudflare ingress | Points to `:8000` but nothing listens there. Dead route. |
| `code.centralmcp.ai` | Points to `:8080` (Code Server). Unknown if installed/running. No process found on port. |
| `daily-summary` skill | `enabled: false` in openclaw.json, but cron job `Daily Briefing` references its script |
| `health-monitor` skill | `enabled: false` in openclaw.json, but cron job `Health Monitor` references it |
| Health Monitor cron | `lastRunAtMs: 1770957954462` (Feb 13, 14 days stale). `nextRunAtMs: 1772248138573` (Feb 28) -- may or may not fire. |
| `ECOSYSTEM_GLOSSARY.yaml` on rainmaker | Exists at `/root/PROJECTS_all/ECOSYSTEM_GLOSSARY.yaml` but purpose/freshness unknown |

### 7.10 Secrets Exposure Surface

| Path | Issue |
|------|-------|
| `openclaw.json` gateway.auth.token | Plain text on disk. Readable by any process running as root. |
| `/root/.doppler/fallback/prd.env` | Encrypted fallback cache (PBKDF2) but key derivation source unknown |
| `openclaw.json` channels.telegram.botToken | Plain text. Bot is dead but token is still there. |
| `openclaw.json` talk.apiKey | Plain text. Purpose unknown ("talk" section). |
| All processes run as root | Zero privilege separation. Monitor, dashboard, gateway, all root. |

### 7.11 Observability Gaps

| What | Observed By | NOT Observed By |
|------|-------------|-----------------|
| Gateway WS connections | Gateway logs (stdout) | Grafana, Netdata, Activity bus |
| Monitor trading actions | Monitor stdout -> log file | Dashboard activity (partially, via HTTP ingest) |
| Agent sessions | OpenClaw session JSONLs | Dashboard COMMLOG (backfilled every 5min) |
| WhatsApp message volume | Gateway logs | No aggregated counter anywhere |
| Binance API rate usage | Nothing | Both monitor and dashboard call Binance independently with no coordination |
| Voice call quality | COMMLOG transcripts | No audio quality metrics |
| Token mismatch events | Gateway WARN log | No alert, no dashboard visibility |

### 7.12 OpenClaw Gateway Protocol: What It Actually Supports

Deep investigation of `/root/openclaw-custom/src/gateway/` reveals the gateway is a **mature, well-designed system** supporting THREE distinct protocol dialects -- all intentional:

| Dialect | Entry Point | Wire Format | Purpose |
|---------|-------------|-------------|---------|
| **Native WS** | `ws-connection.ts` -> `message-handler.ts` | JSON frames: `req`/`res`/`event` | Primary protocol. 82+ RPC methods. Challenge-response handshake. |
| **OpenAI-compatible HTTP** | `openai-http.ts` | `POST /v1/chat/completions` | Drop-in replacement for OpenAI API. Streaming + non-streaming. |
| **OpenResponses HTTP** | `openresponses-http.ts` | `POST /v1/responses` | Implements OpenResponses spec. Images, files, tools, streaming. |

**Native WS handshake (canonical):**
1. Server sends `connect.challenge` with nonce
2. Client sends `req` with `method: "connect"`, nested `params: { auth: {token}, client: {...}, role, scopes }`
3. Server validates auth (token/password/device-identity/tailscale), responds `hello-ok`
4. All further comms are `req`/`res`/`event` frames

**Key finding: The "simplified" protocol used by `voice_gateway.py` (`{"type": "connect", "clientId": "cli", "token": "..."}`) is NOT a supported dialect.** The gateway's `message-handler.ts` strictly expects:
- First message must have `type: "req"` and `method: "connect"`
- Auth must be nested inside `params.auth`
- There is no `type: "connect"` handler in the frame schema

This means `voice_gateway.py`'s WhatsApp sending path may be silently failing or the gateway has undocumented backward-compat handling.

**OpenClaw custom modifications (uncommitted):**
Only 3 files modified from upstream -- none affect the gateway protocol:
1. `src/auto-reply/reply/commands-core.ts` -- generic command hook system
2. `src/auto-reply/reply/commands.test.ts` -- test for above
3. `ui/src/ui/navigation.ts` -- adds "intelligence" tab to web UI

The gateway code is **unmodified upstream**.

### 7.13 Signal Pool + Context Router: The LLM Intelligence Layer

The dashboard has a sophisticated signal scoring and context injection system, previously unmapped:

```
Signal Producers          Signal Pool            Context Router           LLM Agent
┌─────────────┐      ┌──────────────┐      ┌──────────────────┐     ┌──────────┐
│ Trading     │──┐   │              │      │ Keyword triggers  │     │          │
│ Decisions   │──┤   │  Thread-safe │      │ (PT-BR + EN)     │     │ Gemini   │
│ Market      │──┤──>│  in-memory   │──────│ Salience scoring  │────>│ 2.5      │
│ Trailing    │──┤   │  store       │      │ Budget election   │     │ Flash    │
│ Auto-entry  │──┤   │  (max 200)   │      │ char budget=2000  │     │          │
│ Activity    │──┤   │              │      │ Crystal store     │     │          │
│ Health      │──┘   │  TTL expiry  │      │  (newer layer)    │     │          │
│ Memory(LTM) │──────│  Dedup by    │      │                  │     │          │
│ Comms       │──────│  domain:key  │      │ inject_context()  │     │          │
└─────────────┘      └──────────────┘      └──────────────────┘     └──────────┘
```

**Zone salience mapping in signal_pool.py USES OLD NAMES:**
```python
_ZONE_SALIENCE = {
    "GREEN": 15, "YELLOW": 40, "RED": 70,
    "EMERGENCY": 85, "CRITICAL": 92, "NUCLEAR": 100,
}
```

This is yet another location where the old zone names are embedded. Since `console_state["trading"]["zone"]` emits one format and signal_pool expects another, there could be a salience scoring mismatch -- critical trading zones getting LOW salience (default 25 instead of 85-100) because the zone name doesn't match the lookup table.

**Keyword trigger sets** in `context_router.py` include bilingual (PT-BR + EN) triggers for: TRADING, ACTIVITY, FINANCE, MEMORY, COMMS domains. This is well-designed but the trigger sets are hardcoded (not configurable).

**Two injection layers exist in parallel:**
1. `signal_pool` + `elect()` -- the older system (budget: 2000 chars)
2. `intelligence.crystal_store` + `injector.assemble_injection()` -- the newer system (budget: 850 chars)
3. `context_router.inject_context()` tries crystal store first, falls back to signal pool

### 7.14 The SpecBuilder / Factory System

The dashboard has a spec-driven task factory (`factory_api.py`, 304 LOC) that bridges to an external project at `/opt/specbuilder/`:

- **Purpose:** Transcribe markdown spec documents into deterministic, schedulable tasks for LLM workers
- **Import pattern:** `sys.path.insert(0, "/opt/specbuilder")` -- another hard-coded path inject
- **Components:** `Task`, `Registry` (SQLite), `Scheduler`, `WorkerPool`, `Transcriber`
- **Status:** Appears to be in "i1" (dry-run) mode -- actual LLM dispatch is marked as "i2: comes later"
- **Database:** `factory.db` (path from `config.FACTORY_DB_PATH`)
- **Spec directory:** `config.FACTORY_SPECS_DIR`

This is an ambitious code generation pipeline that hasn't been fully deployed. It represents a **fourth sys.path injection** into the dashboard process.

### 7.15 Backtest Engine

The dashboard includes a complete event-driven backtesting system (`backtest_engine.py`, 1276 LOC) that:

- Imports and calls the REAL production modules: `scoring_engine`, `reversal_intel`, `decision_engine`, `indicators_lib`
- Simulates portfolio state: equity, positions, margin ratio, zone transitions
- Applies realistic slippage (0.05%) and fees (0.04%)
- Applies Binance funding rates every 8 hours
- Uses `trading_constants.determine_zone()` for zone classification (NEW names)
- Has supporting modules: `backtest_data.py` (1215 LOC), `backtest_http_api.py` (447 LOC)
- Total backtest subsystem: ~2,938 LOC

**Coupling observation:** The backtest engine imports `decision_engine.py` (the same module that `fm_trailing.py` in the monitor lazy-loads via `sys.path`). Any change to `decision_engine.py` affects three consumers: dashboard UI, backtest engine, and monitor trailing logic.

### 7.16 Health Guardian: Independent Watchdog

The Health Guardian (`/opt/health-guardian/health_guardian.py`, 1084 LOC deployed) runs as a systemd timer every 5 minutes. Investigation reveals:

**Architecture:**
- **Timer:** `health-guardian.timer` (every 5 min, oneshot service)
- **State DB:** `/var/lib/health-guardian/incidents.db` (SQLite, 630KB)
- **State JSON:** `/var/lib/health-guardian/state.json` (live status snapshot)
- **Models snapshot:** `/var/lib/health-guardian/models_snapshot.json` (provider health, refreshed daily)

**Current alerts (live state.json):**
```
1. CRASH_LOOP: rainmaker-dash restarted 92x
2. CRASH_LOOP: finance-harvest is failed
3. CRASH_LOOP: finance-refresh is failed
4. SYNC_CONFLICT: 43 conflict file(s) in /root/PROJECTS_all
```

**Deployed vs repo drift:** The deployed version at `/opt/health-guardian/` has 1084 lines. The repo version at `/root/PROJECTS_all/PROJECT_openclaw/vps/health-guardian/` has 978 lines. The deployed version has 4 EXTRA failure classes not in the repo:
- `check_sync_conflicts()`
- `check_session_bloat()`
- `check_doc_freshness()`
- `check_config_code_coherence()`

This means the deployed health guardian is ahead of its own source repo. If someone deploys from the repo, they'll lose these checks.

**Insight cooldowns** show a rich incident history: SERVICE_DEAD, CRASH_LOOP, PROCESS_LEAK, CIRCUIT_BREAKER, AUTO_RESTART_FAILED, CHANNEL_DOWN, ERROR_FLOOD, CONFIG_DRIFT, SYNC_CONFLICT events spanning weeks. The system has been noisy.

**Quarantine:** One file quarantined: `finance_harvest.py.bak` (Feb 14) -- the guardian auto-quarantines crashing scripts.

### 7.17 Syncthing Sync Conflicts: 95 Orphaned Files

95 `.sync-conflict-*` files exist across the VPS, across 5 clusters:

| Cluster | Count | Date | Source Device | Path |
|---------|-------|------|---------------|------|
| Collider viz modules (in .openclaw workspace) | 26 | Feb 8 | MacBook (W6FO5FW) | `/root/.openclaw/workspace/.openclaw/extensions/collider/` |
| Collider viz modules (in openclaw dir) | 26 | Feb 8 | MacBook | `/root/openclaw/workspace/.openclaw/extensions/collider/` |
| PROJECT_elements files | 35 | Feb 8-9 | MacBook | `/root/PROJECTS_all/PROJECT_elements/` |
| PROJECT_openclaw control files | 6 | Feb 26 | **VPS itself (LQQBHVF)** | `/root/PROJECTS_all/PROJECT_openclaw/control/` |
| CLI history | 2 | Feb 9 | MacBook | `/root/PROJECTS_all/PROJECT_cli-history/` |
| Dashboard __pycache__ | 1 | Feb 26 | MacBook | `/opt/rainmaker-dash/` |

**Key observations:**
- The Feb 8 batch (87 files) was a mass conflict event, likely from simultaneous editing on Mac and VPS
- The Feb 26 conflicts in `PROJECT_openclaw/control/` are from device `LQQBHVF` which is **the VPS's own second Syncthing instance** -- the VPS is conflicting with itself
- Syncthing syncs 2 folders: `kitten-tts-outputs` (/opt/kitten-tts/outputs) and `projects-all` (/root/PROJECTS_all)
- Syncthing service is **disabled in systemd** but running directly (started at 12:04 UTC) -- unclear how it was launched
- Health Guardian has been reporting "43 conflict files" for weeks with no resolution

### 7.18 Timer/Cron Ecosystem: 28 Active Timers

Beyond the 3 crontab entries and 2 OpenClaw cron jobs, there are **28 systemd timers** running:

| Timer | Frequency | Purpose | Owner |
|-------|-----------|---------|-------|
| `voice-capture.timer` | Every 10 min | Voice capture/processing | Custom |
| `health-guardian.timer` | Every 5 min | Anomaly detection | Custom |
| `tailscale-watchdog.timer` | Every 5 min | VPN health check | Custom |
| `tdj-scan.timer` | Every 5 min | Unknown (tdj = ?) | Custom |
| `reverse-sync.timer` | Every 15 min | Reverse file sync | Custom |
| `models-fetch.timer` | Daily 12:05 | LLM provider model listing | Custom |
| `morning-digest.timer` | Daily 11:05 | Morning digest (BRT 8:05) | Custom |
| `finance-refresh.timer` | Weekly Mon 21:35 | Finance data refresh | Custom |
| `finance-harvest.timer` | Weekly Mon 21:45 | Finance data harvest | Custom |
| `doppler-sync-fallback.timer` | Every ~6h | Doppler offline cache | Custom |
| `cloudflared-update.timer` | Daily midnight | Cloudflare tunnel update | System |
| `sysstat-collect.timer` | Every 10 min | System statistics | System |
| 16 more system timers | Various | apt, logrotate, fstrim, etc. | System |

**Conflict with OpenClaw cron:** Both `morning-digest.timer` (11:05 UTC = 8:05 BRT) and OpenClaw's `Daily Briefing` cron job (8:00 AM BRT) fire within 5 minutes of each other. They may produce duplicate morning messages.

**Failed timers:** `finance-harvest` and `finance-refresh` are both in failed state. Health Guardian has been reporting these as CRASH_LOOP for weeks.

### 7.19 .env Secret Leak

`/root/.openclaw/.env` claims to be a "stub" but contains a **live XAI API key** in plaintext:

```
# Secrets managed by Doppler (ai-tools/prd)
# This file is kept as a stub because OpenClaw reads ~/.openclaw/.env at startup.
XAI_API_KEY=xai-13tWHJ...
```

The comment says "all secrets are injected via doppler run" but then hardcodes an API key directly below. Additionally, `state.json` exposes the gateway auth token in plaintext: `"gateway.auth.token": "16977b348d..."`.

### 7.20 Dashboard Crash Loop: 92 Restarts

Health Guardian reports `rainmaker-dash restarted 92x`. Combined with the `finance-harvest` and `finance-refresh` failures, this suggests the dashboard has stability issues. The one `__pycache__/*.sync-conflict-*` file in `/opt/rainmaker-dash/` could indicate Syncthing is interfering with the running dashboard's bytecode cache.

### 7.21 Complete Dashboard Module Map (96 Python Files, 35,744 LOC)

Sorted by category with LOC:

**Voice subsystem (16 files, ~6,100 LOC):**
`voice_gateway.py` (964), `voice_core_api.py` (1027), `voice_tools.py` (867), `voice_tools_elevenlabs.py` (747), `voice_gateway_twilio.py` (341), `voice_gateway_api.py` (200), `voice_self_api.py` (290), `selfhosted_voice.py` (249), `voice_bridge_base.py` (475), `voice_policy.py` (158), `voice_provider_breaker.py` (74), `voice_tool_exec.py` (465), `voice_brain.py` (35), `voice_transcript.py` (38), `voice_prompt.py` (42), `voice_audio.py` (86)

**WebSocket bridges (5 files, ~860 LOC):**
`ws_bridge.py` (229), `ws_bridge_openai.py` (64), `ws_bridge_grok.py` (91), `ws_bridge_gemini.py` (222), `ws_bridge_selfhosted.py` (439), `ws_bridge_http_api.py` (113)

**Trading (8 files, ~3,900 LOC):**
`trading_station.py` (536), `trading_http_api.py` (792), `decision_engine.py` (1287), `scoring_engine.py` (351), `reversal_intel.py` (358), `trade_intel.py` (688), `trading_constants.py` (76), `trade_mode.py` (166)

**Backtest (4 files, ~3,100 LOC):**
`backtest_engine.py` (1276), `backtest_data.py` (1215), `backtest_http_api.py` (447), `paper_trading.py` (1215), `paper_trading_http_api.py` (177)

**Finance (6 files, ~3,500 LOC):**
`finance_api.py` (1628), `pluggy_engine.py` (757), `finance_gmail.py` (631), `finance_ledger.py` (273), `finance_categorizer.py` (182), `finance_voice_api.py` (756)

**AI/LLM (5 files, ~2,200 LOC):**
`llm_proxy.py` (769), `omniscience.py` (760), `prompt_assembler.py` (364), `signal_pool.py` (440), `context_router.py` (280)

**Communication (3 files, ~930 LOC):**
`commlog.py` (646), `commlog_http_api.py` (148), `channels_api.py` (137)

**Activity/Events (3 files, ~920 LOC):**
`activity.py` (383), `activity_http_api.py` (485), `sse_broadcaster.py` (50)

**Operations (5 files, ~1,400 LOC):**
`ecosystem.py` (415), `ops_api.py` (310), `ops_voice_api.py` (108), `system_http_api.py` (81), `workspace_reader.py` (110)

**Google (3 files, ~1,500 LOC):**
`google_api.py` (716), `google_voice_api.py` (259), `meet.py` (159), `meet_http_api.py` (67)

**Invoice (2 files, ~660 LOC):**
`invoice_api.py` (589), `invoices_voice_api.py` (70)

**Auth (3 files, ~1,060 LOC):**
`core_auth.py` (433), `webauthn_api.py` (545), `webauthn_service.py` (78)

**Data/Search (4 files, ~1,200 LOC):**
`data_surface.py` (458), `memory_bridge.py` (274), `memory_capture.py` (179), `bulk_loader.py` (355)

**Config/State (5 files, ~530 LOC):**
`config.py` (340), `db.py` (255), `console_state.py` (26), `core_errors.py` (79), `core_log.py` (37)

**Other (13 files, ~2,800 LOC):**
`app.py` (926 -- main FastAPI app), `market_data.py` (271), `market_analyzer.py` (247), `compartments_api.py` (249), `compartments_http_api.py` (63), `automations_api.py` (315), `automations_http_api.py` (73), `factory_api.py` (304), `factory_voice_api.py` (85), `refinery_api.py` (147), `ytpipe_api.py` (288), `tags_api.py` (115), `files_api.py` (138), `media_http_api.py` (82), `history_http_api.py` (116), `indicators_lib.py` (123), `core_tags.py` (353), `mcp_voice_api.py` (140)

**Patches/Scripts (4 files, ~190 LOC):**
`patch_openclaw_config.py` (21), `patch_risk_zones_vps.py` (71), `enable_tsunami_vps.py` (63), `check_data.py` (33)

---

## 8. PREMATURE CONCLUSIONS AVOIDED

The following observations are noted WITHOUT recommending action. Each requires deeper investigation:

- The 35K LOC dashboard may be appropriately monolithic for a single-user system, or it may be a liability. Depends on deployment frequency and failure modes.
- The duplicate Binance clients may be intentional (separation of concerns: monitor writes orders, dashboard reads only) or accidental duplication.
- The 5 message-sending paths may all be necessary for different contexts (voice emergency, cron, interactive, invoice) or may indicate organic growth without design.
- Running everything as root on a single VPS may be acceptable for a personal system or may be a ticking time bomb.
- The zone naming divergence may be mid-migration (old->new) or may be a permanent state of confusion.
- The AGENTS.md being 650+ lines may be necessary for the AI to function well, or may be token waste that confuses the model.
- The gateway protocol is unmodified upstream -- the "simplified" protocol in voice_gateway.py may just be wrong (a bug), or the gateway may have undocumented backward-compat. Need to test whether voice_gateway.py WhatsApp messages actually get delivered.
- The signal_pool using OLD zone names may be intentional (monitor emits old names, pool scores them) or a bug (if console_state emits new names, pool won't score them correctly). Need to trace what `console_state["trading"]["zone"]` actually contains at runtime.
- The 92 dashboard restarts may be from code instability, OOM, or the Syncthing `__pycache__` conflict corrupting the running process. Need to check logs for root cause.
- The deployed health guardian being ahead of repo could be intentional rapid iteration or a deployment hygiene problem.
- `morning-digest.timer` and OpenClaw `Daily Briefing` may be the same system (one replaced the other) or duplicate competing systems.
- The specbuilder/factory system appears to be an unreleased code generation pipeline. Whether it should be removed, completed, or left dormant is unclear.
- Finance timers (`finance-harvest`, `finance-refresh`) have been failing for weeks. Whether these are abandoned features or should be fixed is unknown.

---

## 9. IMPLEMENTATION PRIORITY (TENTATIVE -- NEEDS REVIEW)

### Phase 1: Stop the Bleeding (1-2 hours)

1. **Fix Telegram bot token** -- get new token from @BotFather, update Doppler + openclaw.json
2. **Set trading to Telegram-primary** -- `trade_mode.json` channel: "telegram"
3. **Keep WhatsApp for personal assistant** -- agent + cron use WhatsApp, trading goes to Telegram
4. This is the FASTEST fix and immediately resolves channel contention

### Phase 2: Formalize Contracts (1 day)

1. **Add `source` and `priority` to monitor's WS send params** -- 10 lines in `fm_notify.py`
2. **Add token sync ExecStartPre** -- systemd one-liner that copies Doppler token to openclaw.json
3. **Standardize zone names** -- refactor fm_*.py to use new names (ALLOCATED/ELEVATED/TRIM/FLATTEN/CAP)
4. **Delete `.gateway-token`** -- remove legacy file

### Phase 3: Decouple Config (1 day)

1. **Monitor reads thresholds via HTTP** -- replace file poll with `GET /api/thresholds`
2. **Remove hard-coded `/opt/rainmaker-dash/` import** -- bundle `trading_constants.py` with monitor
3. **Add health endpoint to monitor** -- `GET /health` on a dedicated port for dashboard to probe
4. **Reset Health Monitor cron** -- fix stale `nextRunAtMs`

### Phase 4: Documentation & Observability (ongoing)

1. **Deploy this architecture doc to rainmaker** -- `/root/PROJECTS_all/PROJECT_openclaw/docs/`
2. **Add Grafana dashboard for trading alerts** -- track message volume per source
3. **Add structured logging** -- all three services log to Loki with consistent format
4. **SMOC classification in ECOSYSTEM_GLOSSARY.yaml** -- formal atom registry

---

## 10. APPENDIX: Full Port Map

| Port | Service | Protocol | Bound To | External |
|------|---------|----------|----------|----------|
| 22 | SSH | TCP | 0.0.0.0 | Yes (Fail2Ban) |
| 80 | Caddy | HTTP | * | Yes (redirect to 443) |
| 443 | Caddy | HTTPS | * | Yes |
| 3000 | Grafana | HTTP | Docker | Via Caddy |
| 3100 | Loki | HTTP | Docker | Via Promtail |
| 3334 | OpenClaw Voice Webhook | HTTP | 127.0.0.1 | No |
| 8080 | Code Server (dead?) | HTTP | -- | Via Caddy |
| 8100 | Rainmaker Dashboard | HTTP | 0.0.0.0 | Via Caddy + CF Tunnel |
| 8384 | Syncthing UI | HTTP | 127.0.0.1 | No |
| 9000 | Portainer | HTTP | Docker | Via Caddy |
| 9091 | Authelia | HTTP | Docker | Via Caddy |
| 9443 | Portainer HTTPS | HTTPS | Docker | Via Caddy |
| 18789 | OpenClaw Gateway | WS | 127.0.0.1 + ::1 | Via CF Tunnel |
| 18792 | OpenClaw (unknown) | ? | 127.0.0.1 | No |
| 19999 | Netdata | HTTP | 0.0.0.0 | Via Caddy |
| 20241 | Cloudflared Metrics | HTTP | 127.0.0.1 | No |
| 22000 | Syncthing Protocol | TCP | * | Yes |

## 11. APPENDIX: Config File Registry

| File | Owner | Consumers | Hot-Reload |
|------|-------|-----------|------------|
| `/root/.openclaw/openclaw.json` | OpenClaw CLI | Gateway (startup) | No (restart required) |
| `/root/.openclaw/workspace/binance/config/thresholds.json` | Dashboard API | Monitor (1s), Dashboard | Yes (1s) |
| `/root/.openclaw/workspace/binance/config/trade_mode.json` | Dashboard config panel | Monitor (poll), Dashboard | Yes |
| `/root/.openclaw/workspace/binance/config/indicators.json` | Dashboard | Monitor | Yes |
| `/root/.openclaw/workspace/binance/config/triggers.json` | Dashboard | Monitor | Yes |
| `/root/.openclaw/workspace/binance/config/preferences.json` | Dashboard | Monitor | Yes |
| `/root/.openclaw/cron/jobs.json` | OpenClaw | Gateway (startup) | No |
| `/opt/rainmaker-dash/finance.db` | Dashboard | Dashboard | N/A (SQLite) |
| `/opt/rainmaker-dash/data/backtest.db` | Dashboard | Dashboard | N/A |
| `/opt/rainmaker-dash/data/commlogs.db` | Dashboard | Dashboard | N/A |
| `/var/lib/health-guardian/state.json` | Health Guardian | OpenClaw cron | Yes |
| `/etc/caddy/Caddyfile` | Manual | Caddy | `caddy reload` |
| `/etc/cloudflared/config.yml` | Manual | Cloudflared | Restart required |
| `/var/lib/health-guardian/incidents.db` | Health Guardian | Health Guardian | N/A (SQLite) |
| `/var/lib/health-guardian/state.json` | Health Guardian | OpenClaw cron, Dashboard | Yes (5 min) |
| `/var/lib/health-guardian/models_snapshot.json` | Health Guardian | OpenClaw cron | Yes (daily) |
| `/root/.openclaw/.env` | Manual | OpenClaw startup | No (contains leaked XAI key) |
| `/root/.openclaw/workspace/binance/config/.env` | Unknown | Health Guardian (EnvironmentFile) | Unknown |
| `/root/.config/syncthing/config.xml` | Syncthing | Syncthing | Auto |
| Factory DB (`config.FACTORY_DB_PATH`) | Dashboard factory_api | Dashboard | N/A (SQLite) |

## 12. APPENDIX: Systemd Timer Map

| Timer | Interval | Service Type | Status |
|-------|----------|-------------|--------|
| `health-guardian.timer` | 5 min | oneshot | Active |
| `tailscale-watchdog.timer` | 5 min | oneshot | Active |
| `tdj-scan.timer` | 5 min | oneshot | Active (purpose unknown) |
| `voice-capture.timer` | 10 min | oneshot | Active |
| `reverse-sync.timer` | 15 min | oneshot | Active |
| `sysstat-collect.timer` | 10 min | oneshot | Active |
| `morning-digest.timer` | Daily 11:05 UTC | oneshot | Active (conflicts with OC Daily Briefing?) |
| `models-fetch.timer` | Daily 12:05 UTC | oneshot | Active |
| `doppler-sync-fallback.timer` | ~6h | oneshot | Active |
| `finance-refresh.timer` | Weekly Mon | oneshot | **FAILED** |
| `finance-harvest.timer` | Weekly Mon | oneshot | **FAILED** |
| `cloudflared-update.timer` | Daily | oneshot | Active |

## 13. APPENDIX: Sync Conflict Inventory (95 files)

| Cluster | Count | Source | Date | Impact |
|---------|-------|--------|------|--------|
| Collider viz in .openclaw/workspace | 26 | MacBook | Feb 8 | Dead weight, never cleaned |
| Collider viz in openclaw/ dir | 26 | MacBook | Feb 8 | Duplicate of above, different base path |
| PROJECT_elements | 35 | MacBook | Feb 8-9 | May cause git noise on VPS |
| PROJECT_openclaw/control | 6 | **VPS itself** | Feb 26 | Active conflict -- VPS fighting itself |
| PROJECT_cli-history | 2 | MacBook | Feb 9 | Minor |
| Dashboard __pycache__ | 1 | MacBook | Feb 26 | Could corrupt running process bytecode |
