# DevJournal Ingestion System + Semantic Page Architecture

> Design spec from brainstorm session 2026-03-16.
> Covers: ingestion pipeline (built), semantic page theory (designed), purpose-driven UI composition (researched).

---

## Part 1: DevJournal Ingestion System (BUILT)

### What It Is

The first automated data pipeline in the Refinery ecosystem. Collects development activity from multiple sources, normalizes into a unified event ledger, and materializes daily views for the dashboard.

### Architecture

```
Collectors (git, cli, fs) → Compiler → devjournal.jsonl (ledger) → Materializer → days/YYYY-MM-DD.json → Refinery API → /journal page
```

Two-stage design:
- **Stage 1 (Ingest)**: Deterministic collectors gather raw events. Each event gets a tracked `oid` (deterministic, time-sortable: `dj-{YYYYMMDDHHMMSS}{hash8}`).
- **Stage 2 (Triage)**: Classify, link, score, summarize. Designed but not yet built. Processors are optional and composable.

### Unified Event Schema

```json
{
  "oid": "dj-2026031614320a7f",
  "ts": "2026-03-16T14:32:00Z",
  "source": "git|cli|fs|session|collider|atlas|system",
  "kind": "commit|prompt|file_created|milestone|session_start|...",
  "project": "PROJECT_elements",
  "data": { ... },
  "tags": ["breakthrough", "bugfix"]
}
```

### Data Sources (13 identified, 3 implemented)

| ID | Source | Status | Format | Size | Value |
|----|--------|--------|--------|------|-------|
| S1 | Session Transcripts | Future | JSONL | 53.8 GB | Highest (full conversations) |
| S2 | REH Evolution | Integrated via git collector | JSON | ~27 KB/project | High (temporal backbone) |
| S3 | CLI History | **Implemented** | JSONL | 9.3 MB | High (user prompts) |
| S4 | Collider Analysis | Future | JSON | 128 MB | Medium (code health) |
| S5 | Feedback Ledger | Future | JSONL | 2.5 KB | Medium (quality trends) |
| S6 | Atlas Registry | Future | YAML | 55 KB | Medium (ecosystem topology) |
| S7 | Autopilot Logs | Future | JSONL | 27 files | Low (system events) |
| S8 | Memory System | Future | MD+YAML | ~10 KB | Low (decision tracking) |
| S9 | Governance | Future | MD+YAML | small | Low (architectural decisions) |
| S10 | System Logs | Future | Text | 406K lines | Low (infrastructure health) |
| S11 | Registries | Future | YAML | small | Low (structural context) |
| S12 | Git (raw) | **Implemented** | native | 121 repos | Highest (code changes) |
| S13 | Confidence Reports | Future | JSON | 33 files | Low (quality signal) |

### Output Location

```
~/.devjournal/
  devjournal.jsonl          # Append-only ledger (Stage 1)
  processed/                # Enriched objects (Stage 2, future)
  days/YYYY-MM-DD.json      # Materialized daily views
  weeks/YYYY-Www.json       # Weekly rollups (future)
  projects/PROJECT_name.json # Per-project views (future)
  meta_index.jsonl          # Run tracking
```

### Code Location

```
wave/tools/devjournal/
  schema.py                 # Pydantic models, oid generation
  collectors/
    git_collector.py        # Scans 121 repos
    cli_collector.py        # Parses ~/.claude/history.jsonl
    fs_collector.py         # Scans 5 dirs by mtime/ctime
  compiler.py               # Merges collectors → ledger (idempotent)
  materializer.py           # Ledger → daily JSON
  run.py                    # CLI: python run.py [date] [--range N]
  triage/                   # Future: classifier, linker, scorer
```

### Results (First Run)

- 3 days captured (March 14-16, 2026)
- 1,178 total events
- Ledger: 328 KB
- Idempotency verified: re-runs correctly deduplicate by oid

### Known Issues

1. Git collector needed date format fix (`--since` requires explicit `T00:00:00`)
2. REH tier2 briefing had list/dict mismatch (fixed)
3. FS collector takes ~23s due to scanning large directory trees (acceptable for daily batch)

---

## Part 2: Semantic Page Architecture (DESIGNED)

### The Problem

Current Refinery NodeDefinition has 3 layers: sense (WHERE data) → interpret (HOW to format) → represent (WHAT view). These answer *what* to show and *how*, but not *why*. Pages are composed by hardcoding layout, not by declaring purpose.

### The Insight

A semantically generated page needs a PURPOSE layer that sits above data fetching. The semantic file must declare:
- **WHY** each node exists (what question it answers)
- **HOW** it serves the page's mission (relevance ranking)
- **WHAT** context it needs nearby (strategic adjacency)

Without purpose, the renderer is just placing widgets. With purpose, the renderer can compose meaningful pages that fulfill the user's information needs.

### Research Validation

| Source | Key Finding |
|--------|-------------|
| CAMELEON Framework (W3C) | UI must start from Task & Concepts (purpose), not widgets. 4-layer model: Task → Abstract UI → Concrete UI → Final UI. |
| SpecifyUI (arxiv 2025) | Structured specifications with explicit intent alignment outperform prompt-based generation. Controllable parameters tied to designer intent. |
| Task-Oriented Design | User intent drives composition, not data structure. "Data structures don't capture intent." |
| Schema Relevance (2025) | Entities must be aligned with user's task goals and contribute meaningfully to task completion. |

### Five Semantic Layers

```
1. MISSION        — Why the page exists (PageDefinition)
2. CONTRIBUTION   — Why each node exists (PurposeDefinition)
3. CONTEXT        — What each node needs nearby (ContextDefinition)
4. SENSE+INTERPRET — Where data comes from and how to read it (existing)
5. REPRESENT      — How to render it (existing, now informed by 1-3)
```

### New Type Definitions

```typescript
interface PurposeDefinition {
  answers: string;           // The question this node resolves
  serves: string[];          // Which page success_criteria it fulfills
  relevance: number;         // 0-1, drives sort order
  attentionCost: 'glance' | 'scan' | 'study' | 'analyze';
  narrativeRole: 'anchor' | 'detail' | 'evidence' | 'action';
}

interface ContextDefinition {
  requiresNearby?: string[]; // Adjacency constraints
  enables?: string[];        // Downstream dependencies
  contrastsWith?: string[];  // Comparison pairs
}

interface PageDefinition {
  id: string;
  mission: string;           // Why this page exists
  audience: string;          // Who reads it
  cadence: string;           // When/how often
  successCriteria: string[]; // How you know it worked
}
```

### Narrative Roles

| Role | Position | Purpose | Examples |
|------|----------|---------|----------|
| **Anchor** | Top, prominent | The headline. First thing you see. | velocity stats, health grade |
| **Detail** | Below anchors | Breaks down the anchor. | project breakdown, source split |
| **Evidence** | Below details | Proves the claim. Raw data, excerpts. | highlights, commits, sessions |
| **Action** | Near its target | What to do about it. | re-run pipeline, drill-down |

### Rendering Algorithm

```
1. READ page mission + success criteria
2. SORT nodes by relevance (descending)
3. GROUP by narrative_role:
     anchors  → top, prominent, always visible
     details  → below anchors, grid layout
     evidence → scrollable feeds, collapsible
     actions  → contextual (near target) or footer
4. RESPECT requires_nearby (adjacency constraints)
5. SIZE by attention_cost:
     glance  → stat card, badge
     scan    → table, bar chart
     study   → feed, timeline
     analyze → full-page, drill-down
6. DERIVE salience from purpose.relevance (don't hardcode)
7. RENDER using existing views
```

### Journal Page Node Map (Proof of Concept)

| Node | Answers | Role | Relevance | View |
|------|---------|------|-----------|------|
| journal.velocity | "How productive was this day?" | anchor | 0.95 | composite (6 stats) |
| journal.timeline | "When did work happen?" | detail | 0.85 | custom (bar chart) |
| journal.projects | "Where did effort concentrate?" | detail | 0.80 | table (bar breakdown) |
| journal.highlights | "What actually happened?" | evidence | 0.75 | feed (chronological) |
| journal.milestones | "What breakthroughs occurred?" | evidence | 0.70 | feed (impact-sorted) |
| journal.rerun | "Is this data fresh?" | action | 0.40 | control (button) |

### Implementation Path

1. Extend `types.ts` with `PurposeDefinition`, `ContextDefinition`, `PageDefinition`
2. Extend `useMultiPolling` to support `source: 'local'` (route via `localGet`)
3. Create `registry/journal.ts` with purpose-annotated node definitions
4. Add `journal` to `domainConfig.ts`
5. Implement purpose-aware rendering in `SemanticPage` (sort by relevance, group by role)
6. Refactor `app/journal/page.tsx` to `<SemanticPage domain="journal" />`

### Blocker: useMultiPolling Source Routing

Current `useMultiPolling` hardcodes `apiGet()` (OpenClaw proxy). Journal needs `localGet()` (local API routes). The `DataSource` type already declares `'local'` but it's not wired through. Fix: extend `EndpointConfig` with `source: DataSource`, branch in `fetchOne()`.

---

## Part 3: Refinery Platform Audit Summary

### Current State (as of 2026-03-16)

- **Completion**: 70% MVP (build passes, 12/14 pages working)
- **Foundation**: Algebra-UI (644-line parametric OKLCH), 10 UI primitives, centralized API layer
- **Node Architecture**: System domain (11 nodes) done. Voice (5 nodes) defined. 10 domains empty.
- **Ingestion**: Framework exists (AppSpec, 15 interfaces). Zero automation. Manual specs only.

### Six Active Concerns

| ID | Concern | Severity |
|----|---------|----------|
| C1 | Dual architecture (page-first vs node-first coexist) | High |
| C2 | No ingestion pipeline → **DevJournal solves this** | High |
| C3 | Node registries empty (2/12 domains defined) | Medium |
| C4 | Backend gaps (missing POST endpoints in OpenClaw) | Medium |
| C5 | Three dashboard implementations not consolidated | Medium |
| C6 | Light theme saturation (coefficient doesn't shift chroma) | Low |

### How DevJournal Advances The Platform

- Solves C2 (first real ingestion pipeline)
- Adds `/journal` page under INTELLIGENCE group
- Uses proven filesystem-reading pattern (no new architecture risk)
- No OpenClaw dependency (pure filesystem)
- Collector → compiler → materializer pattern reusable for future ingestion (AppSpec, Collider, Atlas)
- Purpose-driven node definitions (if implemented) advance C1 resolution by proving node-first works for local data sources

---

*Spec compiled: 2026-03-16 | Session artifacts: 6 HTML brainstorm files + this document*
