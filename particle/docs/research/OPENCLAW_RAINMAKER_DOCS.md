# OpenClaw on Rainmaker -- Operations Reference

> Generated: 2026-02-27 by Claude Opus 4.6 from live system exploration
> Server: Hostinger srv1325721 (82.25.77.221 / Tailscale 100.119.234.42)

## What is OpenClaw

Open-source personal AI assistant. Runs on your own devices, answers on WhatsApp, Telegram, Slack, Discord, Signal, iMessage, etc. The gateway is the control plane; the product is the assistant.

- **Repo:** github.com/openclaw/openclaw
- **Docs:** docs.openclaw.ai
- **DeepWiki:** deepwiki.com/openclaw/openclaw
- **License:** MIT
- **Runtime:** Node >= 22

## Installation on Rainmaker

```
Binary:   /usr/bin/openclaw
Package:  /usr/lib/node_modules/openclaw/ (npm global)
Version:  2026.2.3-1
```

## Directory Map

```
/root/.openclaw/                    # Main config + state directory
├── openclaw.json                   # PRIMARY config (models, channels, skills, gateway auth)
├── .env                            # Stub -- secrets via Doppler, not this file
├── .gateway-token                  # STALE/UNUSED -- do NOT rely on this file
├── agents/
│   ├── main/                       # Primary agent
│   │   ├── agent/                  # Agent workspace
│   │   ├── sessions/               # Chat sessions
│   │   ├── auth-profiles.json      # Model auth (OAuth, API keys)
│   │   └── models.json             # Model config overrides
│   └── rainmaker/                  # Secondary agent
│       └── agent/
├── workspace/                      # Agent workspace (instructions, skills, tools)
│   ├── IDENTITY.md                 # "I am Rainmaker"
│   ├── SOUL.md                     # Personality, channel adaptation
│   ├── SYSTEM.md                   # VPS stack map
│   ├── USER.md                     # About Leo
│   ├── TOOLS.md                    # Available tools reference
│   ├── MEMORY.md                   # Agent memory
│   ├── skills/                     # Custom skills
│   │   ├── cloudpoint-finance/     # Finance data
│   │   ├── daily-summary/          # Morning briefing
│   │   ├── health-monitor/         # System health checks
│   │   ├── trading-thresholds/     # Binance alerts
│   │   ├── inbox-outbox/           # Message queue
│   │   ├── rainmaker-bridge/       # Bridge to server
│   │   ├── elevenlabs-stt/         # Speech-to-text
│   │   └── elevenlabs-voice/       # TTS
│   ├── binance/                    # Trading workspace
│   ├── youtube/                    # YouTube processing
│   └── tools_registry.json         # Registered tools
├── credentials/
│   ├── whatsapp/default/           # WhatsApp Web auth (Baileys)
│   ├── whatsapp-allowFrom.json     # Allowed phone numbers
│   └── whatsapp-pairing.json       # Pairing state
├── cron/
│   └── jobs.json                   # Scheduled tasks (Daily Briefing, Health Monitor)
├── extensions/
│   └── whatsapp/                   # WhatsApp channel plugin (TypeScript)
├── plugins/
│   └── shell-operator/             # Shell operator plugin
├── media/inbound/                  # Received media files
├── memory/                         # Agent memory (LanceDB + SQLite)
│   ├── lancedb/
│   ├── main.sqlite
│   └── rainmaker.sqlite
├── state/                          # Runtime state (empty files)
├── devices/                        # Paired devices
│   ├── paired.json                 # Paired CLI devices
│   └── pending.json                # Pending pairings
├── scripts/
│   └── google-oauth-setup.py       # OAuth token generator
├── private/                        # Private data
│   ├── exports/
│   ├── gmail_finance_snapshots/
│   ├── pluggy_snapshots/
│   ├── quarantine/
│   └── reports/
├── canvas/                         # Canvas rendering files
├── sandbox/                        # Sandbox configs
├── sandboxes/                      # Sandbox instances
├── subagents/                      # Subagent configs
├── telegram/                       # Telegram state
└── voice-calls/                    # Voice call recordings

/root/openclaw-custom/              # FULL SOURCE CODE (dev checkout)
├── src/                            # TypeScript source
│   └── whatsapp/                   # WhatsApp integration source
├── extensions/
│   └── whatsapp/                   # WhatsApp extension source
├── dist/                           # Built JS output
├── skills/                         # Built-in skills
├── packages/                       # Monorepo packages
├── apps/                           # Frontend apps
├── ui/                             # UI components
├── docs/                           # Documentation
├── test/                           # Tests
└── package.json                    # Monorepo root

/root/PROJECTS_all/PROJECT_openclaw/ # Leo's project workspace
├── openclaw-hooks/                 # Custom hooks
├── skills-security/                # Security-related skills
├── scripts/                        # Utility scripts
├── dashboard/                      # Custom dashboard
├── config/                         # Config backups
├── docs/                           # Project docs
└── vps/                            # VPS setup scripts
```

## Systemd Service

```
Unit:     openclaw-gateway.service (user scope)
ExecStart: doppler run --project ai-tools --config prd -- node openclaw gateway --port 18789
Restart:  always (5s delay)
Memory:   max 2G
Runtime:  max 7 days (auto-restart weekly)
```

### Override (`~/.config/systemd/user/openclaw-gateway.service.d/override.conf`)
- Clears default env vars
- Wraps ExecStart with `doppler run` for secret injection
- All secrets come from Doppler `ai-tools/prd` project

## Authentication Architecture

**CRITICAL: Three-layer token system (source of bugs)**

```
Layer 1: Doppler (ai-tools/prd)
  OPENCLAW_GATEWAY_TOKEN = "16977b..." (48 chars)
  → Injected at runtime via `doppler run`
  → This is what the GATEWAY PROCESS actually uses

Layer 2: openclaw.json → gateway.auth.token
  → What the CLI reads for API calls
  → MUST match Layer 1 or you get token_mismatch flood
  → Fixed 2026-02-27: synced to match Doppler value

Layer 3: .gateway-token file (STALE/LEGACY)
  → Written once on first setup, never updated
  → May be read by some internal processes
  → DO NOT rely on this file
```

**When token_mismatch happens:**
1. Check `doppler secrets get OPENCLAW_GATEWAY_TOKEN --project ai-tools --config prd --plain`
2. Compare with `openclaw config get gateway.auth.token`
3. If different: `openclaw config set gateway.auth.token '<doppler-value>'`
4. Then: `openclaw gateway restart`

## Channels

### WhatsApp (PRIMARY)
- DM policy: allowlist
- Allowed: +555499628402, +5554999628402
- Group policy: allowlist, require @mention
- Media max: 50 MB
- Auth: Baileys Web (QR pairing stored in credentials/whatsapp/default/)
- Self number: +555496816430

### Telegram (BROKEN)
- Bot: @Rainmaker3bot
- Error: `getMe` returns 404 -- bot token is invalid/expired
- Needs: new bot token from @BotFather

## Models

```
Primary:    google/gemini-2.5-flash (1024k ctx, text+image)
Fallback 1: anthropic/claude-haiku-4-5 (195k ctx, text+image)
Fallback 2: xai/grok-4-fast (1953k ctx, text+image)
Fallback 3: cerebras/qwen-3-235b-a22b-instruct-2507 (128k, text only)
Fallback 4: openrouter/google/gemini-2.5-flash-lite (1024k, text+image)
Extra:      minimax-portal/MiniMax-M2.1 (195k, text)
```

Auth providers with keys: Anthropic, Google, Google-Antigravity (OAuth), XAI, OpenRouter, MiniMax-Portal (OAuth)
Missing auth: Cerebras (needs API key)

Thinking level: high (default)

## Scheduled Jobs (cron/jobs.json)

### Daily Briefing
- Schedule: 8:00 AM BRT daily
- Agent: main
- Delivery: WhatsApp → +555499628402
- Action: Run daily-summary skill, check health-guardian alerts, send consolidated report

### Health Monitor
- Schedule: every 6 hours
- Agent: main
- Delivery: WhatsApp → +555499628402
- Action: Run health-check, read models_snapshot, check incidents
- Last run: 2026-02-13 (stale -- nextRunAtMs may need reset)

## System Crontab

```
0 3 * * *   backup-workspace.sh         # Git backup at 3 AM UTC
0 4 * * *   backup-openclaw.sh           # Full GCS backup at 4 AM UTC
0 */6 * * * comprehensive-test.sh        # System tests every 6h
```

## Skills (enabled)

| Skill | Purpose |
|-------|---------|
| bird | Unknown |
| clawhub | Hub/marketplace |
| coding-agent | Code generation |
| github | GitHub integration |
| gog | Google search |
| healthcheck | System health |
| mcporter | MCP tool integration |
| nano-banana-pro | Unknown |
| openai-image-gen | DALL-E image generation |
| openai-whisper-api | Speech-to-text |
| oracle | Unknown |
| skill-creator | Create new skills |
| tmux | Terminal sessions |
| twilio | Phone calls |
| video-frames | Video frame extraction |
| voice-call | Twilio voice (from +18142507176) |
| weather | Weather info |
| elevenlabs-stt | ElevenLabs speech-to-text |
| elevenlabs-speech | ElevenLabs TTS |
| inbox-outbox | Message queue management |
| trading-thresholds | Binance trading alerts |
| cloudpoint-finance | Finance data |
| rainmaker-bridge | Server bridge |
| notion | Notion integration |
| daily-summary | DISABLED |
| health-monitor | DISABLED |

## Plugins

| Plugin | Status |
|--------|--------|
| whatsapp | enabled |
| telegram | enabled (but broken -- 404 on bot token) |
| minimax-portal-auth | enabled (OAuth) |
| google-antigravity-auth | enabled (OAuth, leonardolech3@gmail.com) |
| voice-call | enabled (Twilio, +18142507176) |
| lobster | enabled |
| llm-task | enabled |
| diagnostics-otel | DISABLED |

## Voice

- TTS: ElevenLabs (auto on inbound, voice ID: nPczCjzI2devNBz1zQrb)
- STT: Whisper + ElevenLabs
- Voice calls: Twilio (outbound from +18142507176)
- Webhook: https://dashboard.centralmcp.ai/voice/webhook

## Other Services on Rainmaker

| Service | Port | Description |
|---------|------|-------------|
| OpenClaw Gateway | 18789 | Main gateway (WS) |
| Rainmaker Dashboard | 8100 | Console UI |
| Code Server | 8080 | VS Code in browser |
| Syncthing | 22000/8384 | File sync |
| Cloudflared | - | Cloudflare tunnel |
| Futures Monitor | - | Binance trading bot |
| Health Guardian | - | Anomaly detection (5min timer) |

## Common Operations

```bash
# Status
openclaw gateway health
openclaw gateway status
openclaw models list
openclaw models status

# Send message
openclaw message send --channel whatsapp --target '+555499628402' --message 'text'
openclaw message send --channel whatsapp --target '+555499628402' --message 'caption' --media /path/to/file

# Read messages
openclaw message read --channel whatsapp --target '+555499628402' --limit 10

# Polls
openclaw message poll --channel whatsapp --target '+555499628402' --poll-question 'Q?' --poll-option A --poll-option B

# Reactions
openclaw message react --channel whatsapp --target '+555499628402' --message-id MSG_ID --emoji '✅'

# Agent turn
openclaw agent --to '+555499628402' --message 'do something' --deliver

# Logs
openclaw logs --follow
openclaw logs --limit 500

# Model management
openclaw models set 'model/name'
openclaw models fallbacks add 'model/name'
openclaw models fallbacks remove 'model/name'

# Config
openclaw config get <path>
openclaw config set <path> <value>

# Service
openclaw gateway restart
openclaw gateway stop
openclaw gateway start

# Doctor
openclaw doctor
```

## Known Issues (2026-02-27)

1. **Token mismatch (FIXED)**: openclaw.json had wrong gateway token. Synced with Doppler value.
2. **Telegram broken**: Bot token returns 404. Needs new token from @BotFather.
3. **gemini-3.1-pro was set as primary model**: Doesn't exist. Changed to gemini-2.5-flash.
4. **zai/glm-5 in fallbacks**: Dead model. Removed.
5. **Health Monitor cron stale**: Last ran Feb 13. nextRunAtMs may need reset.
6. **Cerebras missing auth**: No API key configured for cerebras fallback.
7. **.gateway-token file**: Legacy artifact from Feb 4. Not updated on restart. Ignore it.

## Secrets Management

All secrets in Doppler: `ai-tools/prd` (99 secrets)
Key secrets:
- `OPENCLAW_GATEWAY_TOKEN` -- gateway auth
- `OPENCLAW_GATEWAY_WS` -- ws://127.0.0.1:18789
- `GOOGLE_APPLICATION_CRED` -- GCP service account
- Various API keys (Anthropic, OpenAI, XAI, ElevenLabs, etc.)

Access: `doppler secrets --project ai-tools --config prd`
