# OpenClaw AI Operations Architecture

## 3-Tier Hybrid Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   TIER 1: LOCAL (MacBook)          TIER 2: EDGE (Hostinger)      TIER 3: BASE  │
│   ═══════════════════════          ════════════════════════      ══════════════ │
│                                                                   (Google Cloud)│
│   ┌─────────────────────┐         ┌─────────────────────┐       ┌────────────┐ │
│   │    Development      │         │   Always-On Agent   │       │  Archive   │ │
│   │    Workstation      │         │      Server         │       │  + Scale   │ │
│   ├─────────────────────┤         ├─────────────────────┤       ├────────────┤ │
│   │                     │         │                     │       │            │ │
│   │ • Claude Code CLI   │◀───────▶│ • OpenClaw Gateway  │◀─────▶│ • Cloud    │ │
│   │ • Cursor IDE        │   SSH   │ • n8n Automations   │ gsutil│   Storage  │ │
│   │ • Local dev/test    │   MCP   │ • Ollama Models     │  API  │ • BigQuery │ │
│   │ • Git repos         │         │ • WhatsApp Bridge   │       │ • Vertex   │ │
│   │ • Hot files         │         │ • 24/7 uptime       │       │ • Archive  │ │
│   │                     │         │                     │       │            │ │
│   ├─────────────────────┤         ├─────────────────────┤       ├────────────┤ │
│   │ Storage: 1TB SSD    │         │ Storage: 400GB NVMe │       │ Storage: ∞ │ │
│   │ RAM: 64GB           │         │ RAM: 32GB           │       │ Compute: ∞ │ │
│   │ Uptime: When awake  │         │ Uptime: 24/7        │       │ Cost: $/GB │ │
│   │ Cost: $0 (owned)    │         │ Cost: ~$30/mo       │       │            │ │
│   └─────────────────────┘         └─────────────────────┘       └────────────┘ │
│            │                               │                           │        │
│            │                               │                           │        │
│            └───────────────┬───────────────┴───────────────────────────┘        │
│                            │                                                    │
│                            ▼                                                    │
│              ┌─────────────────────────────┐                                    │
│              │      SYNC BRIDGE            │                                    │
│              │                             │                                    │
│              │  • Hot files ↔ Local        │                                    │
│              │  • Active data ↔ Hostinger  │                                    │
│              │  • Archive ↔ GCS            │                                    │
│              │  • Auto-tiering by age/use  │                                    │
│              └─────────────────────────────┘                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Tier Responsibilities

| Tier | Name | Purpose | Best For |
|------|------|---------|----------|
| **T1** | Local (Mac) | Development, IDE, testing | Active coding, Claude Code sessions |
| **T2** | Edge (Hostinger) | Always-on agents, bots, APIs | WhatsApp bot, n8n, 24/7 services |
| **T3** | Base (GCP) | Archive, scale, heavy compute | Backups, BigQuery, ML training |

## Data Flow Between Tiers

```
                    WRITE PATH                          READ PATH
                    ══════════                          ═════════

    Local creates    T1 ───────────▶ T2 ───────────▶ T3
    code/docs             sync           archive
                         (rsync)        (gsutil)


    Need old data    T1 ◀─────────── T2 ◀─────────── T3
                          fetch           restore
                         (rsync)        (gsutil)
```

## Sync Bridge Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     SYNC BRIDGE DAEMON                          │
│                   (runs on Hostinger VPS)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│   │  LOCAL SYNC     │  │  GCS SYNC       │  │  SMART TIER   │  │
│   │                 │  │                 │  │               │  │
│   │  rsync daemon   │  │  gsutil rsync   │  │  Age-based:   │  │
│   │  inotify watch  │  │  lifecycle      │  │  <7d = T1/T2  │  │
│   │  delta transfer │  │  policies       │  │  7-30d = T2   │  │
│   │                 │  │                 │  │  >30d = T3    │  │
│   └─────────────────┘  └─────────────────┘  └───────────────┘  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    MANIFEST                              │  │
│   │                                                          │  │
│   │  tracks: file locations, versions, last access           │  │
│   │  stored: /root/.sync-bridge/manifest.db (SQLite)         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Storage Allocation Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│   LOCAL (MacBook) - 1TB SSD                                    │
│   ├── ~/PROJECTS_all/        Active development (hot)         │
│   ├── ~/vault/               Credentials (never sync)         │
│   └── ~/.claude/             Session data (sync to T2)        │
│                                                                │
│   HOSTINGER (VPS) - 400GB NVMe                                 │
│   ├── /root/openclaw/        Bot runtime                       │
│   ├── /data/sessions/        User sessions (warm)              │
│   ├── /data/models/          Ollama models                     │
│   ├── /data/n8n/             Workflow data                     │
│   └── /data/sync/            Bridge staging area               │
│                                                                │
│   GCP (Cloud Storage) - Unlimited                              │
│   ├── gs://elements-archive-2026/backups/     Daily snapshots  │
│   ├── gs://elements-archive-2026/sessions/    Old sessions     │
│   ├── gs://elements-archive-2026/logs/        Historical logs  │
│   └── gs://elements-archive-2026/models/      Model checkpoints│
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## GCP Services Integration

| Service | Purpose | Connection |
|---------|---------|------------|
| **Cloud Storage** | Archive, backups | gsutil from Hostinger |
| **BigQuery** | Analytics, logs | Direct API |
| **Vertex AI** | Heavy ML tasks | API when needed |
| **Cloud Functions** | Serverless triggers | Webhook endpoints |
| **Secret Manager** | API keys backup | gcloud CLI |

## Sync Commands (Hostinger VPS)

```bash
# Sync local → Hostinger (push)
sync-bridge push /local/path /remote/path

# Sync Hostinger → GCS (archive)
sync-bridge archive /data/old-sessions

# Restore from GCS → Hostinger (restore)
sync-bridge restore gs://bucket/path /local/path

# Full backup to GCS
sync-bridge backup-all

# Status
sync-bridge status
```

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              YOUR DEVICES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│   │   iPhone     │         │   MacBook    │         │  Any Browser │       │
│   │  WhatsApp    │         │ Claude Code  │         │  Dashboard   │       │
│   └──────┬───────┘         └──────┬───────┘         └──────┬───────┘       │
│          │                        │                        │               │
└──────────┼────────────────────────┼────────────────────────┼───────────────┘
           │                        │                        │
           ▼                        ▼                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD LAYER                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐              ┌─────────────────────────────────┐   │
│  │   META CLOUD API    │              │     HOSTINGER VPS               │   │
│  │   (via 360dialog)   │   webhook    │     82.25.77.221                │   │
│  │                     │─────────────▶│                                 │   │
│  │  ┌───────────────┐  │              │  ┌───────────────────────────┐  │   │
│  │  │ Virtual Number│  │              │  │      OPENCLAW GATEWAY     │  │   │
│  │  │ +55 XX XXXXX  │  │◀─────────────│  │      :18789               │  │   │
│  │  └───────────────┘  │   Graph API  │  │                           │  │   │
│  │                     │              │  │  ┌─────────────────────┐  │  │   │
│  │  360dialog BSP      │              │  │  │   Agent Manager     │  │  │   │
│  │  - No hosting fee   │              │  │  │   - Sessions        │  │  │   │
│  │  - Direct Meta      │              │  │  │   - Context         │  │  │   │
│  │  - Brazil ready     │              │  │  │   - Memory          │  │  │   │
│  └─────────────────────┘              │  │  └─────────────────────┘  │  │   │
│                                       │  │                           │  │   │
│                                       │  │  ┌─────────────────────┐  │  │   │
│                                       │  │  │   Channel Router    │  │  │   │
│                                       │  │  │   - WhatsApp Cloud  │  │  │   │
│                                       │  │  │   - Dashboard       │  │  │   │
│                                       │  │  │   - API             │  │  │   │
│                                       │  │  └─────────────────────┘  │  │   │
│                                       │  └───────────────────────────┘  │   │
│                                       │                                 │   │
│                                       │  ┌───────────────────────────┐  │   │
│                                       │  │         n8n               │  │   │
│                                       │  │   (Automation Layer)      │  │   │
│                                       │  │                           │  │   │
│                                       │  │  - Scheduled tasks        │  │   │
│                                       │  │  - Webhook triggers       │  │   │
│                                       │  │  - Multi-service flows    │  │   │
│                                       │  │  - Data transformations   │  │   │
│                                       │  └─────────────┬─────────────┘  │   │
│                                       │                │                │   │
│                                       │  ┌─────────────▼─────────────┐  │   │
│                                       │  │       OLLAMA              │  │   │
│                                       │  │   (Local Models)          │  │   │
│                                       │  │                           │  │   │
│                                       │  │  - llama3:70b             │  │   │
│                                       │  │  - codellama              │  │   │
│                                       │  │  - mistral                │  │   │
│                                       │  │  (32GB RAM = big models)  │  │   │
│                                       │  └───────────────────────────┘  │   │
│                                       └─────────────────────────────────┘   │
│                                                      │                      │
│                                                      │ API calls            │
│                                                      ▼                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      AI BACKENDS (External APIs)                      │  │
│  │                                                                       │  │
│  │   ┌────────────┐    ┌────────────┐    ┌────────────┐                 │  │
│  │   │  ANTHROPIC │    │  CEREBRAS  │    │ PERPLEXITY │                 │  │
│  │   │            │    │            │    │            │                 │  │
│  │   │ Claude     │    │ Llama 70B  │    │ Sonar Pro  │                 │  │
│  │   │ Opus 4.5   │    │ @2000 t/s  │    │ (Research) │                 │  │
│  │   │            │    │            │    │            │                 │  │
│  │   │ Best       │    │ Fastest    │    │ Web Search │                 │  │
│  │   │ reasoning  │    │ inference  │    │ + Citations│                 │  │
│  │   └────────────┘    └────────────┘    └────────────┘                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow: WhatsApp Message → AI Response

```
1. USER sends WhatsApp message
         │
         ▼
2. META receives on virtual number
         │
         ▼
3. META → 360dialog → WEBHOOK to Hostinger VPS
         │
         ▼
4. OPENCLAW GATEWAY receives webhook
         │
         ├──▶ Parse message
         ├──▶ Load user session/context
         ├──▶ Check permissions (allowlist)
         │
         ▼
5. AGENT MANAGER routes to AI backend
         │
         ├──▶ Simple query? → Cerebras (fast)
         ├──▶ Complex reasoning? → Claude Opus
         ├──▶ Need web search? → Perplexity
         ├──▶ Code generation? → Ollama local
         │
         ▼
6. AI RESPONSE generated
         │
         ▼
7. OPENCLAW → Graph API → META → WhatsApp
         │
         ▼
8. USER receives reply
```

## Component Responsibilities

| Component | Role | Location |
|-----------|------|----------|
| **360dialog** | BSP, number hosting, Meta bridge | Cloud (their infra) |
| **OpenClaw Gateway** | Message routing, session management | Hostinger VPS |
| **n8n** | Automation, scheduled tasks, integrations | Hostinger VPS |
| **Ollama** | Local LLM inference (free, private) | Hostinger VPS |
| **Claude Opus** | Complex reasoning, main AI brain | Anthropic API |
| **Cerebras** | Fast inference for simple queries | Cerebras API |
| **Perplexity** | Web search, research, citations | Perplexity API |

## Port Allocation (Hostinger VPS)

| Port | Service | Access |
|------|---------|--------|
| 22 | SSH | Public (key-only) |
| 18789 | OpenClaw Gateway | Public (token auth) |
| 5678 | n8n | Localhost / tunnel |
| 11434 | Ollama | Localhost only |

## Security Layers

```
┌─────────────────────────────────────────┐
│ Layer 1: Network                        │
│ - SSH key-only access                   │
│ - Firewall (ufw)                        │
│ - Fail2ban                              │
├─────────────────────────────────────────┤
│ Layer 2: Application                    │
│ - Gateway auth token                    │
│ - WhatsApp allowlist                    │
│ - Rate limiting                         │
├─────────────────────────────────────────┤
│ Layer 3: Data                           │
│ - API keys in env vars                  │
│ - Session data encrypted                │
│ - No PII logging                        │
└─────────────────────────────────────────┘
```

## Integration Points

### Claude Code (Mac) ↔ Hostinger VPS
```
Method: MCP (Model Context Protocol)
Config: ~/.claude.json → hostinger server
Tools: 118 Hostinger API tools available
```

### OpenClaw ↔ 360dialog (WhatsApp Cloud API)
```
Method: Webhooks + Graph API
Inbound: POST /webhook (messages, status)
Outbound: POST graph.facebook.com/v20.0/{phone_id}/messages
Auth: Bearer token (permanent access token)
```

### OpenClaw ↔ n8n
```
Method: HTTP webhooks + REST API
Trigger: n8n webhook nodes
Action: n8n HTTP Request nodes
Use: Scheduled tasks, multi-step workflows
```

### OpenClaw ↔ Ollama
```
Method: HTTP API (localhost:11434)
Endpoint: POST /api/generate
Models: llama3:70b, codellama, mistral
Use: Free local inference, code tasks
```

## Cost Structure (Monthly)

| Item | Cost | Notes |
|------|------|-------|
| Hostinger VPS KVM 8 | ~$30 | 32GB RAM, 8 vCPU |
| 360dialog | FREE | No hosting fee |
| WhatsApp conversations | ~R$50-100 | Usage-based |
| Claude API | ~$20-50 | Per token |
| Cerebras API | ~$5-10 | Very cheap |
| Perplexity API | ~$5 | Research only |
| Ollama | FREE | Self-hosted |
| **TOTAL** | ~$70-100/mo | |

## Future Expansions

```
Phase 2: Multi-channel
├── Telegram bot
├── Discord bot
├── Email gateway
└── SMS fallback

Phase 3: Knowledge base
├── RAG with local embeddings
├── Project documentation indexed
├── Code context awareness
└── Memory persistence

Phase 4: Proactive AI
├── Scheduled check-ins
├── Anomaly detection alerts
├── Automated reports
└── Smart reminders
```

---

*Architecture designed for Leonardo Lech's AI Operations Layer*
*Last updated: 2026-02-03*
