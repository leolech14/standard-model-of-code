# Palace Dashboard - Layout & Functionality Specification

> **Status:** Backend 100% complete (21 endpoints), Frontend 30% complete (skeleton)
> **Date:** 2026-01-27
> **Deployment:** Ready for Cloud Run

---

## DASHBOARD LAYOUT

### Main Screen (6 Tabs)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🏰 PALACE DASHBOARD          Last Update: 2s ago    [●LIVE]    ┃
┠─────────────────────────────────────────────────────────────────┨
┃ [Butlers] [Knowledge] [Cloud] [Health] [Files] [Auto]         ┃
┠─────────────────────────────────────────────────────────────────┨
┃                                                                 ┃
┃  SYSTEM OVERVIEW                                               ┃
┃  ┌────────────────┬────────────────┬────────────────┐          ┃
┃  │ Health: BRONZE │ Automation: 92%│ Cloud Jobs: 3  │          ┃
┃  │ Margin: +0.70  │ Watchers: ✅   │ Running: 0     │          ┃
┃  └────────────────┴────────────────┴────────────────┘          ┃
┃                                                                 ┃
┃  BUTLER STATUS (26 total) - 24 healthy, 2 warnings             ┃
┃  ┌─────────────────────────────────────────────────────┐       ┃
┃  │ ✅ Communication Fabric    BRONZE, +0.70    3m ago  │       ┃
┃  │ ✅ Refinery                2,673 chunks     5m ago  │       ┃
┃  │ ✅ Autopilot               All GREEN        1h ago  │       ┃
┃  │ ✅ LOL                     2,469 entities   3m ago  │       ┃
┃  │ ✅ TDJ                     2,899 files      3m ago  │       ┃
┃  │ ⚠️ Socratic Audit         64% success      12m ago │       ┃
┃  │ ✅ Decision Deck           83 cards         1d ago  │       ┃
┃  │ ✅ Reference Library       9/65 analyzed    now     │ ◄ NEW ┃
┃  │ ... 18 more                                         │       ┃
┃  └─────────────────────────────────────────────────────┘       ┃
┃                                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## TAB 1: BUTLERS (Real-Time Status)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ BUTLERS - 26 Systems                    Healthy: 24/26 ✅     ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ Filter: [All] [AI] [Orchestrator] [Data]    Sort: [Health ▼]┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ COMMUNICATION FABRIC                          3min ago │┃
┃ │    Type: AI Butler                                        │┃
┃ │    Status: BRONZE tier, +0.70 margin, STABLE              │┃
┃ │    Metrics: F=9.81, MI=0.73, N=0.69, SNR=0.93             │┃
┃ │    [View Details] [View History]                          │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ REFINERY                                      5min ago │┃
┃ │    Type: AI Butler                                        │┃
┃ │    Status: 2,673 chunks, 539K tokens, all fresh           │┃
┃ │    Recent: Processed 4,615 files → 295 atoms              │┃
┃ │    [View Details] [Query Chunks]                          │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ REFERENCE LIBRARY                             now      │┃ ◄ NEW
┃ │    Type: Knowledge Butler                                 │┃
┃ │    Status: 9/65 analyzed (13.8%), 280 terms indexed       │┃
┃ │    Cloud: 2.17 GiB backed up                              │┃
┃ │    [View Library] [Search Refs] [Analysis Progress]       │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ⚠️ SOCRATIC AUDIT                                12min ago│┃
┃ │    Type: Orchestrator                                     │┃
┃ │    Status: 64% success rate (improving from 0%)           │┃
┃ │    Last: SUCCESS (762s), Next: 12:00 UTC                  │┃
┃ │    [Run Now] [View Logs] [Disable Schedule]               │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ... 22 more butlers                                           ┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Auto-Refresh:** 10 seconds
**Data Source:** `GET /api/butlers`

**Interactions:**
- Click butler card → Details modal
- Click [View Details] → `GET /api/butlers/{id}`
- Click [View History] → `GET /api/butlers/{id}/history` → Chart modal
- Click [Run Now] → `POST /api/cloud/jobs/{id}/execute`

**Health Indicators:**
- ✅ Green: healthy, last update < 15 min
- ⚠️ Yellow: warnings present or 15-60 min stale
- ❌ Red: unhealthy or > 60 min stale
- ⚪ Gray: no recent data

---

## TAB 2: KNOWLEDGE (Searchable Library)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ KNOWLEDGE LIBRARY - 2,673 chunks, 539K tokens                 ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ ┌─────────────────────────────────────────────────────────┐  ┃
┃ │ 🔍 Search: [________________________] [Search]         │  ┃
┃ └─────────────────────────────────────────────────────────┘  ┃
┃                                                               ┃
┃ SEARCH RESULTS (23 matches for "Communication Fabric")        ┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ 📄 .agent/tools/autopilot.py:445                          │┃
┃ │    Type: function | Relevance: 98% | 6 matches            │┃
┃ │    "...Step 3: Communication Fabric - Recording state..."  │┃
┃ │    [View Full] [View Context]                              │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ 📄 context-management/docs/specs/FABRIC_SPEC.md:12        │┃
┃ │    Type: h2 | Relevance: 92% | 4 matches                  │┃
┃ │    "## Communication Fabric State Vector..."               │┃
┃ │    [View Full] [View File]                                 │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ... 21 more results                                           ┃
┃                                                               ┃
┃ ──────────────────────────────────────────────────────────    ┃
┃                                                               ┃
┃ REFERENCE LIBRARY STATUS                           ◄ NEW     ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ 📚 Academic References: 65 works                          │┃
┃ │    Analyzed: 9 (13.8%) | Pending: 56 (86.2%)              │┃
┃ │    Indexes: ✓ Catalog  ✓ Concepts (50)  ✓ Search (280)   │┃
┃ │    Cloud: gs://...references/ (2.17 GiB backed up)        │┃
┃ │    [Browse Refs] [Search by Concept] [Analysis Queue]     │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ LIBRARY FILES (207 total, sorted by chunks)                   ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ session_summary.md          77 chunks    4,798 tokens     │┃
┃ │ autopilot.py                23 chunks    7,234 tokens     │┃
┃ │ edge_extractor.py           39 chunks    5,112 tokens     │┃
┃ │ ... 204 more files                                        │┃
┃ │ [View All →]                                               │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Search:**
- Data: `GET /api/knowledge/search?q={query}`
- Live search (debounced 300ms)
- Highlights matches
- Click result → Full chunk modal

**Reference Library Card (NEW):**
- Data: `GET /api/knowledge/references`
- Shows: total_refs, analyzed, pending, completion %
- Links: Browse catalog, search by concept
- Click [Browse Refs] → Reference browser modal

**Library Files:**
- Data: `GET /api/knowledge/library?sort=chunks`
- Paginated (50 per page)
- Click file → Chunk list modal
- Sort: chunks, tokens, name

---

## TAB 3: CLOUD JOBS (Control Panel)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CLOUD JOBS - Scheduled Tasks                                  ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ ACTIVE JOBS (3)                                               ┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ socratic-audit-job                        ⚪ IDLE          │┃
┃ │   Last: SUCCESS (12min ago, 762s)                          │┃
┃ │   Next: Today 12:00 UTC (5h 10m)                           │┃
┃ │   Success Rate: 64% (100/156 runs)                         │┃
┃ │   Schedule: Daily midnight + noon                          │┃
┃ │   [▶ Run Now] [⏸ Pause] [📊 History] [📋 Logs]             │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ refinery-chunking-job                     ✅ SUCCESS       │┃
┃ │   Last: SUCCESS (5min ago, 42s)                            │┃
┃ │   Next: On file change (watcher-triggered)                 │┃
┃ │   Success Rate: 100% (89/89 runs)                          │┃
┃ │   [▶ Run Now] [📊 History]                                 │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ SCHEDULERS (5)                                                ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ Midnight Audit     0 0 * * *    [Enabled]  [Disable]   │┃
┃ │ ⏸ Morning Check      0 6 * * *    [Disabled] [Enable]    │┃
┃ │ ✅ Noon Refresh       0 12 * * *   [Enabled]  [Disable]   │┃
┃ │ ✅ Evening Sync       0 18 * * *   [Enabled]  [Disable]   │┃
┃ │ ✅ File Watcher       On change    [Enabled]  [Disable]   │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Job Cards:**
- Data: `GET /api/cloud/jobs`
- Refresh: 30s
- Click [▶ Run Now] → `POST /api/cloud/jobs/{name}/execute`
- Click [⏸ Pause] → `POST /api/cloud/schedulers/{name}/toggle`
- Click [📊 History] → History modal with success rate chart
- Click [📋 Logs] → Cloud Console link

**Scheduler Controls:**
- Click [Enable]/[Disable] → `POST /api/cloud/schedulers/{name}/toggle`
- Visual: ✅ = enabled, ⏸ = disabled
- Shows next run time, cron schedule

**Running Job Indicator:**
- When job executing: Shows progress bar
- Poll: `GET /api/cloud/jobs/{name}/status/{exec_id}` every 2s
- Shows: elapsed time, ETA, current stage

---

## TAB 4: HEALTH (System Metrics)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ SYSTEM HEALTH - Communication Fabric                         ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ CURRENT STATUS                                                ┃
┃ ┌──────────────────────────────────────────────────────────┐ ┃
┃ │                                                          │ ┃
┃ │   Health Tier: BRONZE      Stability: +0.70  (STABLE)   │ ┃
┃ │                                                          │ ┃
┃ │   ┌────────────────────────────────────────────────┐    │ ┃
┃ │   │ F (Feedback Latency):      9.81 hours          │    │ ┃
┃ │   │ MI (Mutual Information):   0.7277 (GOOD)       │    │ ┃
┃ │   │ N (Noise):                 0.6850 (HIGH ⚠️)    │    │ ┃
┃ │   │ SNR (Signal/Noise):        0.9270 (GOOD)       │    │ ┃
┃ │   │ R_auto (Redundancy):       1.0 (FULL)          │    │ ┃
┃ │   │ R_manual:                  0.5477 (MODERATE)    │    │ ┃
┃ │   │ ΔH (Change Entropy):       1.0 (HIGH)          │    │ ┃
┃ │   └────────────────────────────────────────────────┘    │ ┃
┃ │                                                          │ ┃
┃ └──────────────────────────────────────────────────────────┘ ┃
┃                                                               ┃
┃ ALERTS & RECOMMENDATIONS                                      ┃
┃ ┌──────────────────────────────────────────────────────────┐ ┃
┃ │ ⚠️ WARNING: High noise level (0.6850 > 0.5)              │ ┃
┃ │    Recommendation: Be prepared for context to shift      │ ┃
┃ └──────────────────────────────────────────────────────────┘ ┃
┃                                                               ┃
┃ 24-HOUR TRENDS                                                ┃
┃ ┌──────────────────────────────────────────────────────────┐ ┃
┃ │ Stability Margin                                         │ ┃
┃ │  1.0 ┐                                                   │ ┃
┃ │      │    ╱────────────────                              │ ┃
┃ │  0.7 ├───╱                                               │ ┃
┃ │      │  ╱                                                │ ┃
┃ │  0.0 └─────────────────────────────────▶                │ ┃
┃ │      0h              12h              24h                │ ┃
┃ │                                                          │ ┃
┃ │ Trend: +0.05 (improving) ✅                              │ ┃
┃ └──────────────────────────────────────────────────────────┘ ┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Current Metrics:**
- Data: `GET /api/health/current`
- Refresh: 10s
- Color-coded: GREEN (healthy), YELLOW (warning), RED (critical)

**Trend Chart:**
- Data: `GET /api/health/trends?hours=24`
- Chart.js line chart
- Shows: stability_margin, F, MI over time
- Hover: Show exact values
- Refresh: 60s

**Alerts:**
- Real-time display of current alerts
- Severity: INFO, WARNING, CRITICAL
- Click alert → Dismiss or view details

---

## TAB 5: FILES (GCS Browser)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CLOUD FILES - gs://elements-archive-2026/                    ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ Path: / > projectome > R0_raw >                              ┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ 📁 projectome/              640 MB    127 files           │┃
┃ │ 📁 references/              2.17 GiB  13,947 files         │┃ ◄ NEW
┃ │ 📁 intelligence/            45 MB     89 files            │┃
┃ │ 📁 chunks/                  15 MB     12 files            │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ FILES IN: /projectome/R0_raw/                                 ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ 📄 20260127_063000.json     5.0 MB    10min ago  [⬇]     │┃
┃ │ 📄 20260127_000000.json     4.8 MB    6h ago     [⬇]     │┃
┃ │ 📄 20260126_183000.json     4.9 MB    18h ago    [⬇]     │┃
┃ │ ... 124 more files                                        │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ [⬆ Upload File] [🗑️ Cleanup Old] [📊 Storage Stats]          ┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Browse:**
- Data: `GET /api/files/list?path={path}`
- Click folder → Navigate into it
- Breadcrumb navigation
- Refresh: 60s

**Download:**
- Click [⬇] → `GET /api/files/download?file={path}`
- Browser downloads file
- Works for: JSON, YAML, MD, CSV, images

**Upload:**
- Click [⬆ Upload] → File picker
- `POST /api/files/upload` with multipart form
- Requires auth

**Reference Library Folder (NEW):**
- Shows references/ folder (2.17 GiB)
- Can browse: pdf/, txt/, images/, metadata/
- Download individual refs or metadata

---

## TAB 6: AUTOMATION (Control Panel)

### Layout

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ AUTOMATION - 92% Autonomous                                   ┃
┠───────────────────────────────────────────────────────────────┨
┃                                                               ┃
┃ LOCAL WATCHERS                                                ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ Filesystem Watcher         PID: 57794    4 triggers/day│┃
┃ │    Watching: context-management/, .agent/                  │┃
┃ │    Last: 28min ago → Triggered wire (SUCCESS)              │┃
┃ │    [Stop] [Restart] [View Log]                             │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ ✅ Socratic Audit Watcher     Daily 00:00 UTC              │┃
┃ │    Last: 5h ago → Ran audit (SUCCESS, 762s)                │┃
┃ │    [Configure] [Disable]                                   │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ AUTOPILOT                                                     ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ Status: ✅ ENABLED at FULL level                           │┃
┃ │ Last Run: 26 Jan 22:57 (11h ago)                           │┃
┃ │ Success Rate: 100% (23/23 runs)                            │┃
┃ │ Next: On trigger (file change or schedule)                 │┃
┃ │ [Toggle OFF] [Set to PARTIAL] [Emergency Stop]             │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ CIRCUIT BREAKERS                                              ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ All Systems: GREEN ✅                                       │┃
┃ │   TDJ: ✅ | Trigger Engine: ✅ | Enrichment: ✅ | Fabric: ✅│┃
┃ │ Open Breakers: 0                                           │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┃ MANUAL CONTROLS                                               ┃
┃ ┌────────────────────────────────────────────────────────────┐┃
┃ │ [▶ Run Wire Now]  [🔄 Sync to Cloud]  [🧹 Cleanup]         │┃
┃ └────────────────────────────────────────────────────────────┘┃
┃                                                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Functionality

**Watcher Control:**
- Data: `GET /api/automation/status`
- Shows: Running/stopped, PID, last trigger
- Click [Stop]/[Restart] → Kills/starts watcher process

**Autopilot Toggle:**
- Click [Toggle OFF] → `POST /api/automation/autopilot/toggle`
- Levels: FULL, PARTIAL, MANUAL, EMERGENCY
- Confirmation modal for safety

**Manual Wire:**
- Click [▶ Run Wire Now] → `POST /api/automation/wire/trigger`
- Shows progress modal while running
- Poll: `GET /api/automation/wire/status` every 2s

**Circuit Breakers:**
- Visual status for each system
- Click system → Details on why breaker state
- Auto-refresh: 30s

---

## REFERENCE LIBRARY INTEGRATION (NEW)

### Reference Browser Modal

**Triggered by:** Click [Browse Refs] in Knowledge tab

**Layout:**
```
┌──────────────────────────────────────────────────────────────┐
│ REFERENCE LIBRARY - 65 Academic Works                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Filter: [All] [Analyzed Only] [Pending]                     │
│ Search: [_________________] [By Concept ▼]                  │
│                                                              │
│ ANALYZED (9) - Tier 1 Complete                              │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ✓ REF-001  Lawvere (1969)  Diagonal Arguments          │  │
│ │    Category: I.1 Category Theory                       │  │
│ │    SMoC: Proves CODOME/CONTEXTOME partition            │  │
│ │    [View Analysis] [View PDF] [View TXT]               │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ✓ REF-040  Friston (2010)  Free Energy Principle       │  │
│ │    Category: II.3 Free Energy                          │  │
│ │    SMoC: Source of d𝒫/dt = -∇Incoherence               │  │
│ │    Concepts: 5 mapped (free_energy, markov_blankets...) │  │
│ │    [View Analysis] [View Equations]                    │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ... 7 more analyzed                                          │
│                                                              │
│ PENDING (56) - Awaiting Analysis                             │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ⏳ REF-002  Kan (1958)  Adjoint Functors               │  │
│ │    Priority: Tier 2                                    │  │
│ │    [Generate Analysis] [View TXT]                      │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ... 55 more pending                                          │
│                                                              │
│ [Close] [Export Catalog] [Analysis Queue →]                  │
└──────────────────────────────────────────────────────────────┘
```

**Data:**
- `GET /api/knowledge/references` - Overview stats
- `GET /archive/references/index/catalog.json` - Full catalog
- `GET /archive/references/metadata/{ref_id}.json` - Individual ref

**Interactions:**
- Click [View Analysis] → Shows full SMoC relevance in modal
- Click [View PDF] → Download PDF from GCS
- Click [View TXT] → Shows enhanced TXT with SMoC markers
- Click [Generate Analysis] → Triggers batch job for that ref
- Filter by [Analyzed Only] → Show 9/65
- Search by concept → Uses concept_index.json

---

## API ENDPOINTS SUMMARY

### All 21 Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/butlers` | GET | List all butlers | ✅ |
| `/api/butlers/{id}` | GET | Butler details | ✅ |
| `/api/butlers/{id}/history` | GET | Time series | ✅ |
| `/api/knowledge/search` | GET | Search chunks | ✅ |
| `/api/knowledge/library` | GET | Browse files | ✅ |
| `/api/knowledge/chunks/{id}` | GET | Get chunk | ✅ |
| `/api/knowledge/stats` | GET | Library stats | ✅ |
| `/api/knowledge/references` | GET | Ref library status | ✅ NEW |
| `/api/cloud/jobs` | GET | List jobs | ✅ |
| `/api/cloud/jobs/{id}/history` | GET | Job history | ✅ |
| `/api/cloud/jobs/{id}/execute` | POST | Trigger job | ✅ |
| `/api/cloud/jobs/{id}/status/{exec}` | GET | Poll status | ✅ |
| `/api/health/current` | GET | Current health | ✅ |
| `/api/health/trends` | GET | Historical | ✅ |
| `/api/automation/status` | GET | Automation health | ✅ |
| `/api/automation/wire/status` | GET | Wire progress | ✅ |
| `/api/automation/wire/trigger` | POST | Manual wire | ✅ |
| `/api/automation/autopilot/toggle` | POST | Control autopilot | ✅ |
| `/api/files/list` | GET | Browse GCS | ✅ |
| `/api/files/download` | GET | Download file | ✅ |
| `/api/files/upload` | POST | Upload file | ✅ |

**Backend: 21/21 implemented ✅**

---

## CURRENT IMPLEMENTATION STATUS

### Backend (FastAPI): 100% ✅

- main.py: 95 lines
- 6 routers: 1,090 lines total
- All 21 endpoints functional
- Dependencies: fastapi, uvicorn, google-cloud-*

### Frontend (HTML/JS): 30% ⚠️

- index.html: ~300 lines (basic structure)
- app.js: ~400 lines (API integration)
- Works: Tab navigation, auto-refresh, search
- Missing: Styling, charts, modals, reference browser

### Deployment: Ready ⏳

- Dockerfile: ✅
- deploy.sh: ✅
- requirements.txt: ✅
- Not deployed yet

---

## TESTING PLAN

### Local Testing

```bash
# 1. Install dependencies
cd dashboard
pip3 install -r requirements.txt

# 2. Run server
uvicorn main:app --reload --port 8080

# 3. Test endpoints
curl http://localhost:8080/api/butlers
curl http://localhost:8080/api/knowledge/references
curl http://localhost:8080/api/health/current

# 4. Open browser
open http://localhost:8080
```

### Cloud Testing

```bash
# 1. Deploy
./deploy.sh

# 2. Get URL
gcloud run services describe palace-dashboard --region us-central1 --format="value(status.url)"

# 3. Test
curl {URL}/api/butlers
open {URL}
```

---

## WHAT'S WORKING VS NOT

### ✅ Fully Working

- All 21 API endpoints implemented
- Reference library endpoint returns correct data
- Refinery integration (via reference_analyzer)
- Cloud sync complete (2.17 GiB)
- Full-text search index (280 terms)

### ⚠️ Partially Working

- Frontend skeleton exists but basic
- No charts implemented (Chart.js imported but not used)
- No modals (would need JavaScript)
- No reference browser UI

### ❌ Not Built

- Styled UI (currently plain Tailwind)
- Interactive charts for trends
- Reference analysis modal
- Batch analysis UI
- Mobile responsive design

---

## TO MAKE IT PRODUCTION-READY

### Backend (Already Done) ✅

All endpoints work, ready to deploy

### Frontend (Needs Work) ⚠️

**Priority 1: Core Views**
1. Butler grid (6 cards per row)
2. Knowledge search results
3. Health metric cards
4. Reference library status card (NEW)

**Priority 2: Interactivity**
5. Job trigger buttons
6. Autopilot toggle
7. File download links
8. Wire manual trigger

**Priority 3: Polish**
9. Trend charts (Chart.js)
10. Modals for details
11. Reference browser
12. Responsive design

**Estimate:** 6-8 hours for production UI

---

## DEPLOY NOW OR WAIT?

### Can Deploy Now With:
- ✅ All API endpoints
- ⚠️ Basic functional UI
- ✅ Reference library integration
- ✅ Real data from Refinery

### Should Wait For:
- Better styling
- Charts implemented
- Reference browser modal
- Full testing

**Recommendation:** Deploy backend now (works), iterate UI after deployment

---

*This is the complete spec for what Palace Dashboard is and does.*
*Backend ready, frontend needs polish.*
*Reference library fully integrated via /api/knowledge/references.*
