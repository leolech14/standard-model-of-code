# Evolution & Mapping: Previous Attempts → Current Solutions

**Document Type:** Historical Context + System Mapping
**Created:** 2026-02-03
**Purpose:** Map previous architectural attempts to current OpenClaw implementation, documenting failures, learnings, and reusable components

---

## Timeline of Attempts

```
2025-07 → PROJECT_central-mcp (PHOTON)
          Goal: App generation from minimal input
          Status: ABANDONED (259K files, incoherent)
          Learning: AI can't generate infrastructure at scale

2025-10 → PROJECT_central-mcp refinement
          Goal: 9 auto-proactive loops, self-healing
          Status: 98% complete but unsustainable
          Learning: Complexity explosion, meta-problems

2026-01 → PROJECT_sentinel creation
          Goal: Local automation manager
          Status: ACTIVE, WORKING
          Learning: Centralization works, simple works

2026-02 → OpenClaw + Hostinger (CURRENT)
          Goal: AI operations layer, 3-tier hybrid
          Status: 30% complete
          Learning: TBD - applying all previous lessons
```

---

## Component Mapping: Old → New

### 1. Local Automation Layer

| Central-MCP/Sentinel | OpenClaw Current | Status | Notes |
|----------------------|------------------|--------|-------|
| **Sentinel CLI** | Keep as-is | ✅ REUSE | Already working, manages LaunchAgents |
| LaunchAgents (14) | Audit + migrate | 🔄 EVALUATE | Some can move to cloud (n8n) |
| Cron jobs (3) | Migrate to n8n | 📋 PLANNED | Cloud = 24/7, better monitoring |
| Shell hooks | Keep local | ✅ REUSE | Mac-specific, low complexity |
| `backup-irreplaceable` | Enhance with GCS | 🔄 UPGRADE | Add cloud backup destination |

**Sentinel Agents to Migrate:**

| Agent | Current Schedule | Migrate to Cloud? | Reason |
|-------|------------------|-------------------|--------|
| claude-backup | Daily 2AM | ✅ YES | 24/7 VPS more reliable |
| projectmonitor | Hourly | ✅ YES | Always-on scanning |
| vm-sync | Hourly | ✅ YES | VPS-to-VPS makes more sense |
| daily-report | Daily 6:30AM | ✅ YES | n8n workflow better |
| security-scan | Hourly | ✅ YES | Cloud = consistent uptime |
| downloads-sync | Hourly | ❌ NO | Mac-specific, needs local access |
| screenshot-cleanup | Daily 2AM | ❌ NO | Local filesystem only |

**Migration Strategy:**
```bash
# Phase 5: For each cloud candidate:
1. Create n8n workflow equivalent
2. Test in parallel with LaunchAgent
3. Disable LaunchAgent after 7 days success
4. Archive LaunchAgent config to sentinel/disabled/
```

---

### 2. Cloud Execution Layer

| Central-MCP | OpenClaw Current | Status | Notes |
|-------------|------------------|--------|-------|
| **GCP VM** (e2-micro) | Hostinger VPS (KVM 8) | ✅ UPGRADED | 32GB RAM vs limited free tier |
| VM IP: 34.41.115.199 | VPS IP: 82.25.77.221 | ✅ REPLACED | New infrastructure |
| Dashboard port 3002 | Gateway port 18789 | ✅ REPLACED | OpenClaw standard port |
| Custom app platform | OpenClaw (open-source) | ✅ REPLACED | Battle-tested framework |
| 9 auto-proactive loops | Simple agent + n8n | ✅ SIMPLIFIED | Avoid complexity explosion |
| PostgreSQL (34 tables) | SQLite + OpenClaw DB | ✅ SIMPLIFIED | Right-sized for workload |
| PM2 process manager | systemd + screen | ✅ STANDARD | Native Linux tools |

**Why Hostinger over GCP e2-micro:**
- 32GB RAM (vs 1GB) = can run Ollama with 70B models
- 400GB NVMe (vs 10GB) = substantial local storage
- Fixed $30/mo (vs variable) = predictable costs
- Better for always-on bot (vs burst compute)

---

### 3. AI Worker Coordination

| Central-MCP | OpenClaw Current | Status | Notes |
|-------------|------------------|--------|-------|
| **Agent A** (GLM-4.6, UI) | Cerebras Llama3:70B | 🔄 DIFFERENT | Speed over specialization |
| **Agent B** (Sonnet-4.5, arch) | Claude Opus 4.5 | ✅ SAME | Best for reasoning |
| **Agent C** (GLM-4.6, backend) | Ollama CodeLlama | 🔄 DIFFERENT | Self-hosted code tasks |
| **Agent D** (Sonnet-4.5, integration) | n8n workflows | 🔄 DIFFERENT | Visual vs agent-based |
| Agent Auto-Discovery Loop | Manual configuration | ✅ SIMPLIFIED | Avoid meta-complexity |
| Task Auto-Assignment Loop | Human routing decision | ✅ SIMPLIFIED | No autonomous task assignment |

**Old: Specialized Agents**
```
Central-MCP had 4 specialized AI agents (A/B/C/D) with:
- Automatic task discovery
- Self-assignment
- Progress tracking
- Inter-agent communication

Problems:
- Coordination overhead
- Duplicate work
- Conflicting implementations
- No human oversight
```

**New: Router Pattern**
```python
# Single point of control
def route_query(query, context):
    """Human-controlled routing logic"""
    if is_code_task(query):
        return ollama_codellama()  # Free, local
    elif is_fast_qa(query):
        return cerebras_llama3()   # Fast, cheap
    elif is_complex(query):
        return claude_opus()       # Best quality
    elif needs_research(query):
        return perplexity_sonar()  # Web search
    else:
        return claude_opus()       # Default to best
```

---

### 4. Data Persistence & Storage

| Central-MCP | OpenClaw Current | Status | Notes |
|-------------|------------------|--------|-------|
| **PostgreSQL** (34 tables) | SQLite + manifest.db | ✅ SIMPLIFIED | Lighter for workload |
| VM-only storage | 3-tier (Local/VPS/GCS) | ✅ UPGRADED | Redundancy + flexibility |
| No backup strategy | Auto-tiering by age | ✅ NEW | Intelligent archival |
| File tracking in DB | sync-bridge manifest | ✅ PLANNED | Explicit file location tracking |
| Git-based versioning | Git + GCS snapshots | ✅ ENHANCED | Multiple backup layers |

**Old Storage Model (Central-MCP):**
```
VM Filesystem
    └── PostgreSQL metadata
    └── No backup strategy
    └── Lost when VM dies
```

**New Storage Model (OpenClaw):**
```
T1: MacBook (1TB)
    ├── Active development
    ├── Hot files (<7 days)
    └── Vault (never sync)

T2: Hostinger VPS (400GB)
    ├── OpenClaw runtime
    ├── Warm files (7-30 days)
    ├── Ollama models
    └── Staging for GCS

T3: GCP Cloud Storage (∞)
    ├── Cold archive (>30 days)
    ├── Daily snapshots
    └── Disaster recovery

sync-bridge manifest.db tracks locations
```

---

### 5. Monitoring & Observability

| Central-MCP | OpenClaw Current | Status | Notes |
|-------------|------------------|--------|-------|
| **Loop 0**: System Status | systemd health checks | ✅ SIMPLIFIED | Native Linux monitoring |
| **Loop 1**: Agent Discovery | Manual agent config | ✅ SIMPLIFIED | No auto-discovery needed |
| **Loop 2**: Project Discovery | Not needed | ❌ REMOVED | Different scope |
| **Loop 3**: Context Learning | Not implemented | ❌ REMOVED | Too complex |
| **Loop 4**: Progress Monitoring | n8n execution logs | ✅ REPLACED | Built-in monitoring |
| **Loop 5**: Status Analysis | n8n alerts + webhooks | ✅ REPLACED | Event-driven |
| **Loop 6**: Opportunity Scanning | Not needed | ❌ REMOVED | Human-driven planning |
| **Loop 7**: Spec Generation | Not needed | ❌ REMOVED | No app generation |
| **Loop 8**: Task Assignment | Human assigns | ✅ SIMPLIFIED | Manual control |
| **Loop 9**: Git Monitor | git hooks (if needed) | 🔄 OPTIONAL | Can add later |
| Grafana dashboards | Simple logs + status | ✅ SIMPLIFIED | Avoid over-engineering |

**Monitoring Philosophy Change:**
```
OLD: 9 self-monitoring loops running constantly
     → Complexity explosion
     → Hard to debug
     → Meta-problems (who monitors the monitors?)

NEW: Simple, explicit monitoring
     → systemd for process health
     → n8n logs for workflows
     → Manual review for complex issues
     → Human is the ultimate monitor
```

---

## Failure Documentation

### Failure 1: VIVO Business Number Recycling

**Date:** 2026-02-03
**Component:** WhatsApp number provisioning
**What Happened:**
- Acquired VIVO Business number (+55 54 99653-9322)
- Number was recycled from previous owner
- Had old WhatsApp contacts messaging bot
- Created noise and confusion
- Couldn't properly test bot behavior

**Root Cause:**
- Didn't explicitly request "número novo" (new number)
- Carrier default = recycle old numbers
- No verification of number history

**Impact:**
- Wasted 2 hours on setup
- Couldn't test cleanly
- Had to unlink and start over

**Learning:**
- **Always request "número novo" explicitly**
- Test number first (call it, check WhatsApp)
- Virtual numbers from BSP better (guaranteed clean)
- Physical SIM = legacy baggage risk

**Applied to Current Plan:**
- Using 360dialog virtual number provisioning
- Meta Cloud API guarantees clean number
- No recycling risk
- Skip physical SIM entirely

**Status:** ✅ LEARNED, DOCUMENTED, PLAN ADJUSTED

---

### Failure 2: Central-MCP Complexity Explosion

**Date:** 2025-10 (peak), abandoned by 2026-01
**Component:** Entire central-mcp platform
**What Happened:**
- Started with simple goal: "minimal input → full app"
- Added 9 auto-proactive loops for intelligence
- Each loop generated metadata, tasks, specs
- Loops started interacting in unexpected ways
- Generated 259K files, 6GB of code/docs
- Multiple versions of truth
- Contradicting implementations
- Became impossible to debug or maintain

**Root Cause:**
- **Generative AI cannot maintain coherence at scale**
- No single source of truth
- AI generating infrastructure (meta-problem)
- Autonomous systems with no oversight
- Scope creep (app generation is HARD)

**Impact:**
- Months of work abandoned
- $0 revenue despite "98% complete"
- Valuable patterns buried in chaos
- Lost time and motivation

**Learning:**
- **AI should assist, not generate infrastructure**
- **Human-in-loop for all major decisions**
- **Narrow scope, simple tools**
- **Manual deployment, not autonomous**
- **Incremental complexity only**

**Applied to Current Plan:**
- OpenClaw = proven open-source, not AI-generated
- n8n = visual workflows, human-designed
- No auto-proactive loops
- Explicit routing logic (human-written)
- Phase gates prevent scope creep

**Status:** ✅ LEARNED, CORE PRINCIPLE CHANGED

---

### Failure 3: Local SSH Tunnel Issues

**Date:** 2026-02-03
**Component:** Dashboard access via localhost tunnel
**What Happened:**
- Created SSH tunnel: `ssh -L 18789:127.0.0.1:18789 hostinger`
- Tunnel worked initially
- Browser access localhost:18789
- Got WebSocket error: "secure context required"
- Tunnel kept dropping/disconnecting
- ERR_CONNECTION_REFUSED repeatedly

**Root Cause:**
- SSH tunnel not persistent (no `-f` flag)
- Browser security requires HTTPS for WebSockets
- Dashboard token auth separate from network auth

**Impact:**
- 20 minutes debugging
- Multiple tunnel restarts
- Confusion about auth vs network

**Learning:**
- Use `-f -N` flags for persistent background tunnel
- Token auth still required even via localhost
- Document the full URL with token: `localhost:18789/?token=...`

**Applied to Current Plan:**
- Document correct SSH tunnel command
- Include token in all dashboard URLs
- Consider HTTPS setup for production

**Status:** ✅ FIXED, DOCUMENTED

---

### Failure 4: Perplexity MCP API Key 401

**Date:** 2026-02-03
**Component:** Perplexity MCP integration in ~/.claude.json
**What Happened:**
- Perplexity MCP tool returned 401 Unauthorized
- API key configured: `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`
- Key either expired or invalid

**Root Cause:**
- API keys expire or get rotated
- No validation on initial setup
- Hard-coded in config (not Doppler)

**Impact:**
- Research tool unavailable
- Had to fall back to local script

**Learning:**
- Test API keys immediately after setup
- Store keys in Doppler, not config files
- Have fallback research methods
- Local perplexity_research.py worked (Doppler-backed)

**Applied to Current Plan:**
- Use local scripts with Doppler
- Validate all API keys before depending on them
- Build redundancy (multiple research paths)

**Status:** ⏳ TODO - Fix MCP key or remove from config

---

### Near-Miss: WhatsApp Personal Number Link

**Date:** 2026-02-03
**Component:** WhatsApp integration initial attempt
**What Almost Happened:**
- Almost linked personal number (+555499628402) to OpenClaw
- Would have intercepted ALL personal messages
- Bot would have responded to family/friends
- Privacy nightmare, social embarrassment

**Prevented By:**
- User sent message to father
- OpenClaw sent pairing request to father
- User realized: "This affects everyone I message"
- Immediately unlinked personal number

**Root Cause:**
- Misunderstanding of WhatsApp Business API
- Thought it was a "bot on my number"
- Actually intercepts ALL activity

**Impact:**
- No actual damage (caught early)
- Learning happened before harm

**Learning:**
- **Never link personal number to bot**
- **Always use dedicated bot number**
- **Test understanding before deployment**

**Applied to Current Plan:**
- Using separate virtual number via 360dialog
- Personal number stays personal
- Clear separation of concerns

**Status:** ✅ AVOIDED, PRINCIPLE ESTABLISHED

---

## Reusable Components from Previous Attempts

### From Central-MCP (Mine for Patterns)

```bash
~/PROJECTS_all/PROJECT_central-mcp/
├── src/tools/              ← MCP integration patterns
├── src/eco-agents/         ← Multi-agent coordination (study, don't copy)
├── src/confidence/         ← Quality scoring system
├── 02_SPECBASES/           ← Specification frameworks
└── *.md files              ← Architecture documentation
```

**What to Extract:**
- MCP tool patterns (how to structure)
- Confidence/quality scoring logic
- Specification templates
- Error handling patterns
- Logging structures

**What NOT to Copy:**
- Auto-proactive loops
- Agent auto-discovery
- Self-modifying code
- Complex orchestration

---

### From Sentinel (Keep & Enhance)

```bash
~/PROJECTS_all/PROJECT_sentinel/
├── agents/                 ← LaunchAgent configs (evaluate each)
├── cron/crontab            ← Migrate useful jobs to n8n
├── hooks/master.sh         ← Keep local hooks
├── bin/sentinel            ← Keep CLI tool, enhance with cloud awareness
└── backups/                ← Integrate with GCS archival
```

**Enhancements Planned:**
```bash
sentinel cloud              # Show cloud-migrated agents
sentinel migrate AGENT      # Move agent to n8n workflow
sentinel sync               # Trigger GCS backup
sentinel status --full      # Include cloud + local
```

---

## Decision Log

### Decision 1: Hostinger over GCP Free Tier
**Date:** 2026-02-03
**Options:**
- A) Continue with GCP e2-micro (free tier)
- B) Upgrade to Hostinger VPS KVM 8 ($30/mo)

**Chosen:** B (Hostinger)

**Rationale:**
- Need 32GB RAM for Ollama 70B models
- e2-micro (1GB) can't run local models
- $30/mo << Claude API costs if we offload 60% queries
- 400GB storage >> 10GB (headroom for growth)
- Fixed cost = predictable budget

**Result:** ✅ Working well, Ollama ready to install

---

### Decision 2: 360dialog over Chakra Chat
**Date:** 2026-02-03
**Options:**
- A) Chakra Chat ($12.49/mo, n8n integration, Brazil-focused)
- B) 360dialog (FREE hosting, official Meta BSP, better docs)
- C) Direct Meta Cloud API (no BSP, DIY)

**Chosen:** B (360dialog)

**Rationale:**
- Cheapest long-term (no markup on Meta fees)
- Best documentation (developer-focused)
- Official Meta partnership = less ban risk
- Can switch to Chakra later if needed
- Perplexity research strongly recommended it

**Result:** ⏳ PENDING - Account creation next

---

### Decision 3: No Auto-Proactive Loops
**Date:** 2026-02-03
**Options:**
- A) Recreate central-mcp's 9 loops in OpenClaw
- B) Simple agent + manual monitoring
- C) Hybrid (1-2 simple loops only)

**Chosen:** B (Simple)

**Rationale:**
- Central-MCP failed BECAUSE of loop complexity
- OpenClaw has built-in session management
- n8n provides needed automation
- Human oversight prevents runaway behavior
- Can add loops later if genuinely needed

**Result:** ✅ Architecture designed without loops

---

### Decision 4: SQLite over PostgreSQL
**Date:** 2026-02-03
**Options:**
- A) PostgreSQL (like central-mcp)
- B) SQLite (lightweight)
- C) No DB (filesystem only)

**Chosen:** B (SQLite)

**Rationale:**
- Workload = single bot, <1000 sessions
- PostgreSQL = overkill for this scale
- SQLite = easier backup (just copy file)
- Less moving parts = fewer failure modes
- Can upgrade to Postgres if growth demands

**Result:** ✅ OpenClaw uses SQLite by default

---

### Decision 5: Manual Deployment vs CI/CD
**Date:** 2026-02-03
**Options:**
- A) Auto-deploy on git push (CI/CD)
- B) Manual `./scripts/deploy.sh` review → deploy
- C) Full GitOps with rollback

**Chosen:** B (Manual with review)

**Rationale:**
- Central-MCP taught us: AI + automation = chaos
- Manual step = human verification
- Prevents broken deploys at 3 AM
- Simple scripts >> complex CI pipelines
- Can automate later if needed

**Result:** ✅ Manual deployment protocol established

---

## Evolution of Architecture Thinking

### v1.0: Monolithic (2025-07)
```
Single codebase
    ↓
Everything in one place
    ↓
Simple but inflexible
```

**Problems:** Hard to scale, single point of failure

---

### v2.0: Microservices + Auto-Loops (2025-10)
```
Multiple services
    ↓
9 auto-proactive loops
    ↓
Agent specialization
```

**Problems:** Complexity explosion, coordination overhead, incoherence

---

### v3.0: Hybrid 3-Tier (2026-02) ← CURRENT
```
Local (Dev) + Cloud (Always-On) + Base (Archive)
    ↓
Simple agent + manual monitoring
    ↓
Human-in-loop for all major decisions
```

**Advantages:**
- Right-sized complexity
- Separation of concerns
- Redundancy without duplication
- Human oversight preserved
- Incremental growth path

---

## Principles Crystallized Through Failure

### 1. AI Assists, Doesn't Generate Infrastructure
```
❌ Let AI create automation systems
✅ Use proven tools, configure manually
```

### 2. Human-in-Loop for Major Decisions
```
❌ Auto-assignment, auto-discovery, auto-everything
✅ Explicit routing, manual approval, human oversight
```

### 3. Simple > Complex (Always)
```
❌ 9 monitoring loops "for intelligence"
✅ systemd + logs + human review
```

### 4. Narrow Scope > Broad Vision
```
❌ "Generate full-stack apps from idea"
✅ "AI assistant accessible via WhatsApp"
```

### 5. Incremental > Big Bang
```
❌ Deploy entire platform at once
✅ 5 phases, test each before next
```

### 6. Right-Size Everything
```
❌ PostgreSQL for <1000 sessions
✅ SQLite (can upgrade later)
```

### 7. Document Failures Explicitly
```
❌ Hide mistakes, start fresh each time
✅ Learn publicly, reference failures, improve
```

### 8. Cost-Optimize from Day 1
```
❌ "We'll optimize later"
✅ Ollama for 60% of queries = free
```

---

## Current State Summary

### What's Working ✅
- Hostinger VPS (fast, reliable, 32GB RAM)
- OpenClaw Gateway (running, accessible)
- Claude Code ↔ Hostinger MCP (118 tools)
- SSH access (key-based, secure)
- Architecture documented
- Lessons learned applied

### What's in Progress 🔄
- WhatsApp integration (30% complete)
- Number provisioning (researched, provider selected)
- Cloud API setup (scripted, pending account)

### What's Not Started ⏳
- Storage bridge (local ↔ VPS ↔ GCS)
- Ollama installation (models selected)
- n8n workflows (use cases defined)
- Sentinel integration (migration plan created)

### What's Blocked 🚫
- WhatsApp: Need new number + 360dialog account
- GCS sync: Need to authenticate VPS to GCP
- Sentinel migration: Depends on n8n setup

---

## Next Session Checklist

### Before Starting Implementation:
- [ ] Review OPENCLAW_ARCHITECTURE.md
- [ ] Review IMPLEMENTATION_MAP.md
- [ ] Review this doc (EVOLUTION_AND_MAPPING.md)
- [ ] Check Phase status in implementation map
- [ ] Verify no blockers for current phase

### During Implementation:
- [ ] Document new failures immediately
- [ ] Update decision log for choices made
- [ ] Screenshot successes
- [ ] Log time spent per task

### After Phase Completion:
- [ ] Update implementation map
- [ ] Write PHASE_N_COMPLETE.md
- [ ] Archive logs and configs
- [ ] Identify reusable patterns

---

## Reference Quick Links

| Document | Purpose |
|----------|---------|
| **OPENCLAW_ARCHITECTURE.md** | System design, 3-tier model, data flow |
| **IMPLEMENTATION_MAP.md** | 5-phase roadmap, tasks, timeline |
| **EVOLUTION_AND_MAPPING.md** | This doc - history, mapping, failures |
| **~/PROJECTS_all/PROJECT_sentinel/AGENT_KERNEL.md** | Sentinel documentation |
| **~/PROJECTS_all/PROJECT_central-mcp/README_START_HERE.md** | Central-MCP status |

---

**Status:** Living document - update after each major decision or failure
**Last Updated:** 2026-02-03
**Version:** 1.0
**Maintainer:** Leonardo Lech + Claude Code
