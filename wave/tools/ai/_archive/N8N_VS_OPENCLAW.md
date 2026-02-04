# n8n vs OpenClaw: Roles and Integration

**TL;DR:** They're complementary, not competing. OpenClaw = conversational AI brain. n8n = automation & scheduling hands.

---

## The Confusion

```
❓ User asks: "Where does n8n fit? What does it replace?"

Common misconception:
"Aren't they both automation tools?"

Reality:
They solve DIFFERENT problems and work TOGETHER
```

---

## Side-by-Side Comparison

| Aspect | OpenClaw | n8n |
|--------|----------|-----|
| **Type** | AI Agent Framework | Workflow Automation Platform |
| **Primary Job** | Manage AI conversations | Execute automated tasks |
| **Interface** | Chat (WhatsApp, API, Dashboard) | Visual workflow builder |
| **Best For** | Real-time Q&A, context-aware responses | Scheduled jobs, multi-step processes |
| **AI Integration** | Built-in (Claude, custom backends) | Via API calls (any service) |
| **State** | Session-based conversation memory | Stateless execution (unless configured) |
| **Trigger** | User messages | Time, webhooks, events |
| **Response** | Natural language | Structured data/actions |

---

## What Each One Does

### OpenClaw's Job

```
┌─────────────────────────────────────────────────────────────┐
│                     OPENCLAW GATEWAY                         │
│                  "The AI Conversation Manager"               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INPUT:  WhatsApp message, API call, dashboard query        │
│           ↓                                                 │
│  PROCESS:                                                   │
│  1. Identify user                                           │
│  2. Load conversation history                               │
│  3. Check permissions (allowlist)                           │
│  4. Route to appropriate AI backend                         │
│  5. Maintain context across messages                        │
│  6. Format response                                         │
│           ↓                                                 │
│  OUTPUT: Natural language AI response                       │
│                                                             │
│  EXAMPLES:                                                  │
│  • "What's the weather?" → Ask AI → Reply                   │
│  • "Remind me at 3pm" → Store → Reply confirmation          │
│  • "Summarize this PDF" → Process → Reply summary           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**OpenClaw is for:**
- ✅ Conversational AI (back-and-forth chat)
- ✅ Context-aware responses (remembers conversation)
- ✅ Real-time interactions (instant replies)
- ✅ User-initiated queries ("Hey AI, help me...")

**OpenClaw is NOT for:**
- ❌ Scheduled tasks ("Run at 6 AM daily")
- ❌ Multi-service workflows ("Pull GitHub → Analyze → Post Slack")
- ❌ Complex data transformations
- ❌ Automated monitoring/alerts

---

### n8n's Job

```
┌─────────────────────────────────────────────────────────────┐
│                         N8N                                  │
│                 "The Automation Workflow Engine"             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  TRIGGER: Time, webhook, file change, API event             │
│           ↓                                                 │
│  WORKFLOW:                                                  │
│  [Node 1] Fetch data from API A                            │
│       ↓                                                     │
│  [Node 2] Transform data (filter, map, format)             │
│       ↓                                                     │
│  [Node 3] Call AI API for analysis                         │
│       ↓                                                     │
│  [Node 4] Post result to Service B                         │
│       ↓                                                     │
│  [Node 5] Send notification                                │
│           ↓                                                 │
│  COMPLETE: Log execution, handle errors                     │
│                                                             │
│  EXAMPLES:                                                  │
│  • Daily 6 AM: Pull GitHub commits → AI summary → WhatsApp  │
│  • On webhook: New file → Analyze → Archive to GCS          │
│  • Hourly: Check VPS health → Alert if down                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**n8n is for:**
- ✅ Scheduled tasks ("Every day at 6 AM...")
- ✅ Multi-step workflows (fetch → transform → send)
- ✅ Service integrations (GitHub, Slack, GCS, etc.)
- ✅ Event-driven automation (webhook → action)
- ✅ Data pipelines (ETL processes)

**n8n is NOT for:**
- ❌ Real-time chat conversations
- ❌ Context-aware AI responses
- ❌ Session management
- ❌ Natural language understanding (it calls AI APIs, doesn't have AI built-in)

---

## How They Work Together

### Example 1: Daily Brief

```
6:00 AM - n8n TRIGGERS
    ↓
n8n: Fetch GitHub activity (API call)
    ↓
n8n: Fetch calendar events (Google API)
    ↓
n8n: Send combined data to OpenClaw API
    ↓
OpenClaw: Receives data → Routes to Claude Opus
    ↓
Claude Opus: Analyzes + Summarizes
    ↓
OpenClaw: Returns formatted summary
    ↓
n8n: Receives summary
    ↓
n8n: Sends via WhatsApp to user
```

**Who does what:**
- n8n: Orchestration (when, what data, from where, to whom)
- OpenClaw: AI intelligence (analysis, summarization, reasoning)

---

### Example 2: User Asks Question

```
User WhatsApp: "What did I commit to GitHub today?"
    ↓
Meta Cloud API: Webhook to OpenClaw
    ↓
OpenClaw: Receives message
    ↓
OpenClaw: Loads user session (knows who you are)
    ↓
OpenClaw: Determines query needs GitHub data
    ↓
OpenClaw: OPTION A - Calls GitHub API directly
         OPTION B - Triggers n8n workflow to fetch + format
    ↓
n8n (if used): Fetches commits → Formats nicely
    ↓
n8n: Returns data to OpenClaw
    ↓
OpenClaw: Routes to AI (Claude) with context
    ↓
Claude: Generates natural language summary
    ↓
OpenClaw: Sends back to WhatsApp
    ↓
User receives: "You made 3 commits today: [summary]"
```

**Who does what:**
- OpenClaw: Conversation management, context, AI routing
- n8n: Optional helper for complex data fetching
- Claude: Natural language generation

---

## What n8n Replaces from Previous Systems

### Replaces: Sentinel's Cron Jobs

```
OLD (Sentinel):
────────────────
Cron job: */15 * * * * /usr/local/bin/memory-alert.sh
          → Runs every 15 min
          → Mac-only, no visibility
          → Shell script (hard to debug)


NEW (n8n):
──────────
n8n workflow: "Memory Monitor"
    [Schedule: Every 15 min]
        ↓
    [HTTP Request: Check VPS memory]
        ↓
    [If > 80%: Alert]
        ↓
    [Send WhatsApp notification]

Benefits:
✅ Visual editor (see the flow)
✅ Runs on VPS (24/7, not Mac-dependent)
✅ Error handling built-in
✅ Can notify anywhere (WhatsApp, email, Slack)
✅ Execution history visible
```

---

### Replaces: Central-MCP's Auto-Proactive Loops

```
OLD (Central-MCP):
──────────────────
Loop 5: Status Auto-Analysis (300s)
    → Scan all projects
    → Find blockers
    → Generate tasks
    → Assign to agents
    → Result: Complexity explosion, conflicts


NEW (n8n):
──────────
n8n workflow: "Weekly Project Health Check"
    [Trigger: Monday 9 AM]
        ↓
    [Run Collider analysis on PROJECT_elements]
        ↓
    [Send results to OpenClaw]
        ↓
    [OpenClaw → Claude: "Summarize issues"]
        ↓
    [n8n: Post summary to WhatsApp]

Benefits:
✅ Simple, scheduled (not constant polling)
✅ Human receives report (not auto-assignment)
✅ One workflow, not 9 interacting loops
✅ Manual review before action
```

---

### Replaces: Central-MCP's Agent Coordination

```
OLD (Central-MCP):
──────────────────
Agent A discovers task
    ↓
Agent B auto-assigned
    ↓
Agent C starts working
    ↓
Agent D realizes conflict
    ↓
All agents confused, duplicate work


NEW (n8n + OpenClaw):
─────────────────────
Human: "Analyze PROJECT_elements architecture"
    ↓
n8n workflow: "Codebase Analysis"
    [Trigger: Manual or scheduled]
        ↓
    [Run Collider scan]
        ↓
    [Send to OpenClaw]
        ↓
    [OpenClaw → Claude: Analyze]
        ↓
    [Save results to GCS]
        ↓
    [Notify human via WhatsApp]

Benefits:
✅ Human triggers (no auto-discovery chaos)
✅ Single AI backend (no agent conflicts)
✅ Results stored (not lost in agent memory)
✅ Human reviews before next step
```

---

## What OpenClaw Replaces

### Replaces: Multiple AI Chat Interfaces

```
OLD:
────
- claude.ai (browser, manual)
- Cursor (IDE-only)
- ChatGPT (separate account)
- Terminal scripts (no memory)


NEW (OpenClaw):
───────────────
One gateway for ALL AI interactions:
✅ WhatsApp (anywhere, anytime)
✅ API (programmatic access)
✅ Dashboard (web UI)
✅ Claude Code MCP (terminal)

ALL share:
- Same conversation history
- Same user context
- Same AI backends
- Same allowlist/permissions
```

---

### Replaces: Manual AI Backend Selection

```
OLD:
────
User: "I need to analyze this code"
    → Manually decide: Claude? GPT? Gemini?
    → Open appropriate interface
    → Copy-paste code
    → Wait for response


NEW (OpenClaw):
───────────────
User: "Analyze this code" (via WhatsApp)
    ↓
OpenClaw: Auto-routes to best backend
    - Code task? → Ollama CodeLlama (free, local)
    - Complex? → Claude Opus (best quality)
    - Fast? → Cerebras (2000 tokens/sec)
    ↓
Returns response in same chat
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR WORKFLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   USER (You)                                                │
│     ↓                                                       │
│   WhatsApp Message: "Daily brief?"                          │
│     ↓                                                       │
│   ┌─────────────────────────────┐                          │
│   │       OPENCLAW               │                          │
│   │   (Conversation Manager)     │                          │
│   │                              │                          │
│   │  "Brief" keyword detected    │                          │
│   │  → Trigger n8n workflow      │←─────┐                   │
│   └─────────────────────────────┘      │                   │
│     ↓                                   │                   │
│   ┌─────────────────────────────┐      │                   │
│   │         N8N                  │      │                   │
│   │   (Workflow Engine)          │      │                   │
│   │                              │      │                   │
│   │  [1] Fetch GitHub activity   │      │                   │
│   │  [2] Fetch calendar          │      │                   │
│   │  [3] Call OpenClaw API ──────┼──────┘                   │
│   │      with combined data      │                          │
│   └─────────────────────────────┘                           │
│     ↓                                                       │
│   ┌─────────────────────────────┐                          │
│   │       OPENCLAW               │                          │
│   │  (receives structured data)  │                          │
│   │  → Routes to Claude Opus     │                          │
│   └─────────────────────────────┘                           │
│     ↓                                                       │
│   ┌─────────────────────────────┐                          │
│   │      CLAUDE OPUS             │                          │
│   │  (AI Backend)                │                          │
│   │                              │                          │
│   │  Analyzes → Summarizes       │                          │
│   └─────────────────────────────┘                           │
│     ↓                                                       │
│   ┌─────────────────────────────┐                          │
│   │       OPENCLAW               │                          │
│   │  (formats response)          │                          │
│   └─────────────────────────────┘                           │
│     ↓                                                       │
│   WhatsApp: "Here's your brief: [summary]"                  │
│     ↓                                                       │
│   USER (You) receives formatted brief                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use Which

### Use OpenClaw Alone:

```
✅ "What's the weather?"
✅ "Explain this code snippet"
✅ "Remind me to call João at 3pm"
✅ "Summarize this article"
✅ Any conversational, context-aware query
```

**Why:** OpenClaw handles these natively. No workflow needed.

---

### Use n8n Alone:

```
✅ Backup files to GCS every night at 2 AM
✅ Check if VPS is down, restart if needed
✅ Pull RSS feeds → Save to database
✅ Any scheduled, deterministic task
```

**Why:** No AI needed, just automation.

---

### Use OpenClaw + n8n Together:

```
✅ Daily brief (n8n fetches data → OpenClaw AI analyzes)
✅ Research pipeline (n8n Perplexity search → OpenClaw Claude summary)
✅ Alert + diagnosis (n8n detects issue → OpenClaw AI troubleshoots)
✅ Scheduled reports (n8n schedules → OpenClaw generates content)
```

**Why:** n8n orchestrates complex data flows, OpenClaw adds intelligence.

---

## Cost Comparison

| Task | OpenClaw Only | n8n Only | OpenClaw + n8n |
|------|---------------|----------|----------------|
| **Daily Brief** | ❌ Can't schedule | ❌ No AI intelligence | ✅ Best (n8n schedules, OpenClaw analyzes) |
| **Chat Q&A** | ✅ Best (conversational) | ❌ Not designed for chat | ⚠️ Overkill (n8n not needed) |
| **Backup Files** | ⚠️ Could, but awkward | ✅ Best (no AI needed) | ⚠️ Overkill (OpenClaw not needed) |
| **Research Report** | ⚠️ Manual trigger | ❌ Can't reason deeply | ✅ Best (n8n fetches, OpenClaw reasons) |

---

## Deployment Together

### On Hostinger VPS:

```
/root/
├── openclaw/                    ← OpenClaw installation
│   ├── dist/                    ← Compiled code
│   ├── config.json              ← OpenClaw config
│   └── gateway (port 18789)     ← AI conversation gateway
│
├── n8n/                         ← n8n installation
│   ├── .n8n/                    ← Workflow storage
│   ├── workflows/               ← Your automation workflows
│   └── n8n (port 5678)          ← Workflow editor
│
└── sync-bridge/                 ← Data sync daemon
    ├── sync-bridge.py
    └── manifest.db              ← File location tracking
```

### Process Management:

```bash
# OpenClaw (systemd or screen)
systemctl status openclaw-gateway
  OR
screen -r openclaw-gw

# n8n (systemd or PM2)
systemctl status n8n
  OR
pm2 status n8n
```

---

## Summary Table

| Question | Answer |
|----------|--------|
| **Can I use OpenClaw without n8n?** | ✅ Yes! Chat, Q&A, real-time AI works fine |
| **Can I use n8n without OpenClaw?** | ✅ Yes! Scheduled tasks, workflows work fine |
| **Do they compete?** | ❌ No, they're complementary |
| **Which do I install first?** | OpenClaw (Phase 1), then n8n (Phase 4) |
| **Which is more important?** | Depends on use case - chat = OpenClaw, automation = n8n |
| **Can they call each other?** | ✅ Yes! n8n → OpenClaw API, OpenClaw → trigger n8n workflows |
| **Which costs more?** | Both are FREE (self-hosted), only AI API calls cost money |

---

## Real-World Usage Scenarios

### Scenario 1: Morning Routine

```
6:00 AM - n8n runs "Morning Brief" workflow
    ├─ Fetches: GitHub commits, calendar, weather
    ├─ Sends to OpenClaw
    ├─ OpenClaw → Claude: "Create morning brief"
    └─ n8n: Sends brief to WhatsApp

Result: You wake up to AI-generated daily brief
```

---

### Scenario 2: On-Demand Question

```
You (WhatsApp): "Explain this error message: [paste]"
    ↓
OpenClaw: Receives → Routes to Claude
    ↓
Claude: Analyzes error → Suggests fix
    ↓
OpenClaw: Formats response
    ↓
You receive: Explanation + solution

Result: Real-time AI help, no n8n needed
```

---

### Scenario 3: Weekly Code Review

```
Monday 9 AM - n8n runs "Weekly Code Review" workflow
    ├─ Runs: git diff --stat origin/main...HEAD
    ├─ Sends diff to OpenClaw
    ├─ OpenClaw → Claude: "Review changes, suggest improvements"
    ├─ Claude: Analyzes → Generates report
    ├─ OpenClaw: Returns report to n8n
    └─ n8n: Posts to Slack + saves to Notion

Result: Automated code quality monitoring
```

---

## Bottom Line

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   OPENCLAW = Your AI brain (conversation, reasoning)        │
│   N8N = Your AI hands (automation, orchestration)           │
│                                                             │
│   Together = Complete AI operations layer                   │
│                                                             │
│   You talk to OpenClaw                                      │
│   OpenClaw talks to AI backends                             │
│   n8n runs scheduled/triggered tasks                        │
│   They call each other when needed                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**They don't replace each other - they multiply each other's value.**

---

**Last Updated:** 2026-02-03
**Related Docs:**
- OPENCLAW_ARCHITECTURE.md
- IMPLEMENTATION_MAP.md (Phase 4 = n8n)
