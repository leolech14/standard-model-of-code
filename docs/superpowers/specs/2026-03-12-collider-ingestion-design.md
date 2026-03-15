# Collider Ingestion System — Design Spec

> Auto-generate dashboard pages from backend code analysis.
> Point Collider at a repo → NodeDefinitions appear in Refinery → pages render automatically.

---

## State of the World: 4 Persistence Classes

### Class 1: Live Sensed Data

**What**: Ephemeral runtime values — CPU usage, trading PnL, gateway status, voice providers.

**Source**: OpenClaw backend at `localhost:8100`, proxied through Next.js rewrite (`/api/openclaw/:path*` → `localhost:8100/api/:path*`).

**Transport**: `lib/api.ts` → `apiGet<T>(path)` with 10s timeout + AbortController.

**Polling**: Two hooks:
- `usePolling(path, { interval })` — single endpoint, React `useState` storage
- `useMultiPolling(endpoints[])` — N endpoints, mutable `slotsRef` Map + tick counter

**Memory**: React component state only. `slotsRef` is a mutable Map keyed by endpoint path. Each slot holds `{ data, loading, error }`.

**Stored?**: **No.** Zero persistence. No localStorage, no IndexedDB, no SWR cache. Page refresh = refetch everything from OpenClaw. Tab hidden = polling pauses. Tab visible = immediate refetch.

**Polling tiers**: 10s (health, system, trading), 15s (voice, llm), 30s (automations, settings, finance).

**Source of truth**: OpenClaw backend. Refinery is a pure read-through window.

---

### Class 2: NodeDefinitions

**What**: Semantic contracts that tell Refinery WHAT to poll, HOW to interpret data, and WHERE to render it. Each defines: endpoint, polling interval, field extraction path, formatting rules, thresholds, view type, salience, grouping, ordering.

**Where they live today**: Static TypeScript files in `lib/nodes/registry/`:
- `system.ts` — 11 nodes (health, cpu, memory, disk, uptime, version, platform, processes, services, events, anomalies)
- `voice.ts` — 5 nodes
- `trading.ts` — 12 nodes (with filterParams + 2 tabs)
- `comms.ts`, `memory.ts` — additional domains
- `index.ts` — aggregator: `ALL_NODES[]` array + `NODE_MAP` Map + selector functions

**Who writes them**: Human developer, by hand, in TypeScript. Each node is ~20-40 lines.

**Who reads them**:
- `SemanticPage.tsx` calls `getNodesByDomain(domain)` → gets nodes → `getUniqueEndpoints(nodes)` → polls → groups by `representation.group` → sorts by `representation.order` → dispatches to `NodeRenderer`
- `NodeRenderer.tsx` reads `sense.fieldPath` (extraction), `interpret.*` (formatting), `representation.preferredView` (view dispatch)

**Where they SHOULD live (after ingestion)**:
- Hand-crafted nodes: stay in static TypeScript (source of truth, type-safe, git-tracked)
- Auto-generated nodes: SQLite (`data/dashboard.db`) via `better-sqlite3` — atomic writes, zero infrastructure, single file
- At runtime: both merge into one unified list. Static wins on ID collision (SQLite nodes whose `id` matches a static node are excluded before merge — static array is authoritative).

**Source of truth**: Static TS files for hand-crafted. SQLite for auto-generated. Code is canonical; database is derived.

---

### Class 3: Curation State

**What**: Vote counts, promotion status, archive/reject flags, confidence scores. Metadata ABOUT a NodeDefinition, not the definition itself.

**Where it lives today**: **Nowhere.** No curation mechanism exists. All nodes are either in the static registry (always visible) or not.

**Where it SHOULD live**: Same SQLite table as dynamic NodeDefinitions. Curation state is columns on the row, not a separate store:

```sql
CREATE TABLE node_definitions (
  id TEXT PRIMARY KEY,          -- 'auto.openclaw.health'
  definition JSON NOT NULL,     -- full NodeDefinition as JSON
  domain TEXT NOT NULL,         -- denormalized from definition.domain at insert time for query efficiency
  confidence REAL NOT NULL,     -- 0.0-1.0, from pipeline
  status TEXT DEFAULT 'generated',  -- generated | promoted | archived
  upvotes INTEGER DEFAULT 0,
  downvotes INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
```

**ID format**: Auto-generated nodes use `auto.{target}.{handler_name}` (e.g., `auto.openclaw.health`, `auto.openclaw.system_current`). The `auto.` prefix guarantees no collision with static node IDs (which use `{domain}.{name}` format like `system.cpu`).

**Denormalization note**: `domain` column is extracted from `definition.domain` at insert time. The `definition` JSON field is canonical — `domain` column exists solely for indexed queries.

**Promotion threshold**: `PROMOTION_THRESHOLD = 0.75` — defined once in `lib/store.ts`, imported by API route and inbox UI. Single constant, not magic numbers.

**How it changes**:
- `generated`: pipeline output, not yet visible on dashboard
- `promoted`: confidence >= PROMOTION_THRESHOLD auto-promotes OR user upvotes → visible on dashboard
- `archived`: user downvotes or explicitly rejects → hidden

**How it affects visibility**:
- `getAllNodes()` returns `[...staticNodes, ...sqliteNodes.filter(n => n.status === 'promoted')]`
- Inbox page shows `sqliteNodes.filter(n => n.status === 'generated')` for review
- Archived nodes invisible everywhere except admin view

**Merge strategy**: `getAllNodes()` remains **synchronous**. SQLite nodes are eagerly loaded at module initialization into a module-level cache (same pattern as `ALL_NODES[]` today). Cache invalidated on write operations (insert/vote/archive). No async cascade to consumers — `SemanticPage.tsx` and `getNodesByDomain()` keep their current synchronous signatures.

**Inbox coexistence**: The existing AppSpec-based inbox (rendering full application specs with inspector sections) is a separate view from the new NodeDefinition inbox. The AppSpec pipeline is a higher-level concept — one AppSpec describes an entire application; NodeDefinitions describe individual data points. Both coexist as tabs on the Inbox page: "Specs" (existing AppSpec view) and "Nodes" (new generated NodeDefinition review with vote buttons).

**Source of truth**: SQLite. Curation is user intent — not derivable from code.

---

### Class 4: UI / Page / Layout Composition

**What**: Which pages exist, which nodes appear on each page, grouping, ordering, tabs, layout rules.

**Where it lives today**: Distributed across 3 layers, ALL static:

1. **Sidebar** (`components/layout/Sidebar.tsx`): hardcoded `NAV_GROUPS[]` array. 15 items in 5 groups. Adding a page = editing this array.

2. **Domain config** (`lib/nodes/domainConfig.ts`): `DOMAIN_CONFIGS` record. Per-domain: icon, title, description, tabs (optional), polling footer. Adding a domain = adding an entry here.

3. **NodeDefinition itself**: `domain` field assigns node to page. `representation.group` controls grouping within page. `representation.order` controls sort. `representation.salience` controls layout prominence (high=grid, normal=full-width, low=compact).

**Layout is NOT stored — it's computed**:
- `SemanticPage` groups nodes by `representation.group`
- Sorts within group by `representation.order`
- High-salience metrics → responsive grid (1-4 cols)
- High-salience non-metrics → full-width
- Normal salience → full-width
- Low salience → compact 2x4 grid
- Tabs (if configured in domainConfig) split groups across tab panels

**What's static vs dynamic**:
- Pages/routes: STATIC (filesystem-based Next.js routing)
- Sidebar nav: STATIC (hardcoded array)
- Domain config: STATIC (hardcoded record)
- Node→page assignment: DERIVED from `node.domain`
- Node grouping/ordering: DERIVED from `node.representation.*`
- Layout rules: DERIVED from salience + kind

**Only persistent layout state**:
- Sidebar collapse: `localStorage('refinery-sidebar-collapsed')`
- Theme mode: `localStorage('theme-mode')`

**Source of truth**: Code. Layout is an emergent property of NodeDefinitions + SemanticPage algorithm. Not stored separately.

---

## What the Persistence Layer Actually Needs to Store

| What | Store | Why |
|------|-------|-----|
| Live API data | Nothing | Ephemeral. OpenClaw is source of truth. |
| Hand-crafted NodeDefinitions | Static TS files | Already works. Type-safe, git-tracked. |
| Auto-generated NodeDefinitions | SQLite `definition` column | Needs CRUD, voting, confidence tracking. |
| Curation state (votes, status) | SQLite columns on same row | Inseparable from the node it describes. |
| Page/layout composition | Nothing | Derived from NodeDefinitions. No separate storage. |
| Sidebar navigation | Code (for now) | Static array. Future: derive from registered domains. |
| Domain config | Code (for now) | Static record. Future: derive from node domains. |

**Minimum new persistence**: ONE SQLite table. Everything else is either already stored (static TS), ephemeral (polling), or derived (layout).

---

## Static vs Dynamic vs Derived

| Thing | Static | Dynamic | Derived |
|-------|--------|---------|---------|
| Hand-crafted NodeDefinitions | Yes (TS files) | | |
| Auto-generated NodeDefinitions | | Yes (SQLite) | |
| Curation state | | Yes (SQLite) | |
| Live sensed data | | | Yes (from OpenClaw) |
| Page existence | Yes (filesystem routes) | | |
| Sidebar items | Yes (hardcoded array) | | |
| Domain config | Yes (hardcoded record) | | |
| Node→page assignment | | | Yes (from node.domain) |
| Layout/grouping/ordering | | | Yes (from representation.*) |
| Theme | | Yes (localStorage) | |

---

## Source of Truth vs Cache

| Thing | Source of Truth | Cache |
|-------|---------------|-------|
| API data | OpenClaw backend | React state (usePolling) |
| Hand-crafted nodes | `lib/nodes/registry/*.ts` | `ALL_NODES[]` array |
| Auto-generated nodes | SQLite `node_definitions` table | Merged into `ALL_NODES[]` at runtime |
| Curation | SQLite columns | None |
| Layout | SemanticPage algorithm | None |
| Backend code structure | Repo source files | Collider analysis output |

---

## MVP User Flow

```
1. USER: Triggers ingestion
   └─ "Ingest OpenClaw" button in Refinery Inbox page
   └─ Calls: POST /api/v1/ingest { repoPath: '/root/projects/PROJECT_openclaw' }

2. REFINERY API ROUTE: Invokes Collider MCP
   └─ Calls: collider-ingestion-mcp.generate_node_definitions(repo_path)
   └─ Waits for response (may take 30-60s for large repos)

3. COLLIDER MCP: Deterministic extraction
   └─ api_route_extractor → 200+ endpoints with routes, methods, params
   └─ intent_extractor → docstrings, commit intents per handler
   └─ universal_classifier → domain classification per endpoint
   └─ purpose_decomposition → NodeKind inference
   └─ graph_framework → salience ranking (hub vs leaf)
   └─ Per endpoint: map deterministic fields (endpoint, title, mutations, filterParams, description, salience, domain)
   └─ Score gaps: which of the 5 inference fields are still empty?

4. COLLIDER MCP: Thin LLM layer (only for gaps)
   └─ Batch endpoints with gaps → Cerebras gpt-oss-120b
   └─ "Given endpoint GET /system/current returning {cpu, memory, disk}, infer: intervalMs, fieldPath, format, thresholds, preferredView"
   └─ Endpoints with zero gaps (e.g., /health) skip LLM entirely

5. COLLIDER MCP: Confidence scoring
   └─ data_chemistry → modulate confidence per node
   └─ Output: NodeDefinition[] as JSON with confidence scores

6. REFINERY API ROUTE: Stores results
   └─ INSERT INTO node_definitions (id, definition, domain, confidence, status, ...)
   └─ Nodes with confidence >= 0.75 → status = 'promoted' (auto)
   └─ Nodes with confidence < 0.75 → status = 'generated' (inbox)

7. REFINERY: Dashboard updates
   └─ getAllNodes() now returns static + promoted dynamic nodes
   └─ New domains may appear → new pages renderable via SemanticPage
   └─ Inbox page shows 'generated' nodes for review

8. USER: Curates
   └─ Reviews inbox → upvotes good nodes (→ promoted) or downvotes bad (→ archived)
   └─ Reviews dashboard → downvotes noisy nodes (→ archived)
   └─ SQLite updates in-place via server actions
```

---

## MCP Response Contract

The `generate_node_definitions` tool returns a structured JSON response. This is the cross-language boundary — Python produces it, TypeScript consumes it.

### Request

```json
{
  "repo_path": "/root/projects/PROJECT_openclaw"
}
```

### Response (success)

```json
{
  "status": "ok",
  "nodes": [
    {
      "definition": { /* full NodeDefinition object */ },
      "confidence": 0.87,
      "domain": "system",
      "gaps_filled_by_llm": ["intervalMs", "fieldPath"]
    }
  ],
  "stats": {
    "total_endpoints": 213,
    "nodes_generated": 45,
    "llm_calls": 12,
    "skipped_endpoints": 168,
    "duration_ms": 34200
  },
  "errors": []
}
```

### Response (partial failure)

```json
{
  "status": "partial",
  "nodes": [ /* successfully generated nodes */ ],
  "stats": { /* ... */ },
  "errors": [
    "LLM timeout for endpoints: /api/v1/complex-handler, /api/v1/multi-step",
    "Could not classify domain for: /api/v1/internal/debug"
  ]
}
```

### Response (error)

```json
{
  "status": "error",
  "nodes": [],
  "stats": null,
  "errors": ["Repository not found at /root/projects/NONEXISTENT"]
}
```

**Validation**: The API route (Deliverable 4) validates each `definition` against a Zod schema mirroring the TypeScript `NodeDefinition` interface BEFORE SQLite insertion. Malformed definitions are logged to `errors[]` in the ingestion response and skipped — not stored.

**Fields validated (required only)**: `id` (string, non-empty), `domain` (string), `title` (string), `kind` (NodeKind enum), `sense.source` (string), `sense.endpoint` (string), `sense.intervalMs` (number > 0), `representation.preferredView` (ViewType enum), `representation.salience` (SalienceLevel enum). Optional fields (`interpret.format`, `sense.fieldPath`, `representation.group`, `representation.order`, etc.) are passed through if present but do not fail validation if absent.

---

## Error Handling

| Failure | Behavior | User sees |
|---------|----------|-----------|
| Invalid/inaccessible `repoPath` | MCP returns `{ status: "error", message: "..." }` immediately | Toast: "Repository not found at path" |
| Collider extraction crash (steps 3) | MCP catches exception, returns `{ status: "error" }` with traceback in `message` | Toast: "Ingestion failed — analysis error" |
| Cerebras API down/rate-limited (step 4) | MCP skips LLM gap-filling, produces nodes with lower confidence. Logs to `errors[]` | Nodes appear in inbox (lower confidence = not auto-promoted). Warning in ingestion summary. |
| Cerebras timeout per endpoint | That endpoint's LLM fields left empty → lower confidence. Other endpoints unaffected. | Affected nodes have gaps noted in inbox detail view |
| MCP stdio transport crash | API route catches `EPIPE`/`SIGTERM`, returns 500 | Toast: "Ingestion service unavailable" |
| SQLite write failure (disk full, locked) | API route catches, returns 500 with message | Toast: "Failed to save results" |
| Zod validation failure on a node | That node skipped, added to response `errors[]`. Other valid nodes still stored. | Ingestion summary shows "N nodes generated, M skipped (validation)" |

**Principle**: Partial success is better than total failure. If 45 nodes are generated and 3 fail validation, store the 42 valid ones. Report errors but don't block the batch.

**Timeout**: `POST /api/v1/ingest` has a 120s server-side timeout. The endpoint is synchronous — holds the connection until the MCP completes. If this proves too slow for very large repos, a future iteration can switch to async with job polling.

### Ingestion API Contract

**Request**: `POST /api/v1/ingest`
```json
{
  "repoPath": "/root/projects/PROJECT_openclaw"
}
```

**Response** (200):
```json
{
  "success": true,
  "generated": 12,
  "promoted": 8,
  "skipped": 3,
  "errors": ["validation failed for /api/v1/debug: missing sense.endpoint"]
}
```

**Response** (500):
```json
{
  "success": false,
  "error": "MCP service unavailable"
}
```

---

## Decisions Log

### DECIDED: Architecture — Collider as MCP Service

**Decision**: Build `collider-ingestion-mcp` as a Python MCP server (FastMCP 3.1.0, stdio transport).
**Rationale**: Collider is Python, Refinery is TypeScript. Service = thin facade over existing modules. MCP pattern proven (cerebras-intelligence-mcp activated 2026-03-12).

### DECIDED: Target Backend — OpenClaw First

**Decision**: First ingestion target is OpenClaw (200+ endpoints). Then generalize.
**Rationale**: Hand-crafted NodeDefinitions exist as ground truth for comparison.

### DECIDED: Curation Model — Auto-Generate, Human-Promote

**Decision**: Confidence >= 0.75 auto-promotes. Below → Inbox. User votes up/down post-hoc.
**Rationale**: Matches existing ExposableNode.confidence pattern.

### DECIDED: Storage — SQLite via better-sqlite3

**Decision**: Single SQLite file (`data/dashboard.db`). Static TS registry untouched. Merge at runtime.
**Rationale**: Perplexity confirms SQLite is standard for single-user Next.js. Atomic writes, zero infrastructure.
**Migration**: Schema versioned via `PRAGMA user_version`. `lib/store.ts` checks version on init, runs `ALTER TABLE` migrations sequentially if needed. Single-user = no concurrent migration risk.

### DECIDED: Pipeline Strategy — Deterministic-First, Adaptive LLM

**Decision**: Deterministic extraction for all fields first. LLM only called for endpoints with remaining gaps. Zero LLM cost for fully-determinable endpoints.
**Rationale**: LLM only where highest-win. Budget scales with ambiguity, not endpoint count.

### DECIDED: Cerebras Model

**Decision**: `gpt-oss-120b` default (was `llama-3.3-70b`, retired). Response parser handles `content` or `reasoning` field.

### DECIDED: MCP Registration

**Decision**: `~/.claude.json` project entry, `doppler run` wrapper, stdio transport.

---

## Deliverables

| # | Component | Language | What it does |
|---|-----------|----------|-------------|
| 1 | **Collider Ingestion MCP** | Python | Analyzes repo, outputs NodeDefinition JSON |
| 2 | **SQLite Store** | TypeScript | `lib/store.ts` — CRUD for dynamic nodes + voting |
| 3 | **Registry Merge** | TypeScript | `getAllNodes()` returns static + promoted dynamic |
| 4 | **Ingestion API Route** | TypeScript | `POST /api/v1/ingest` — triggers MCP, stores results |
| 5 | **Inbox UI Update** | React | Show generated nodes, vote buttons, promote/archive |

---

## Key File Paths

| What | Where |
|------|-------|
| Collider modules | `particle/src/core/` (note: `universal_classifier` is at `core/classification/universal_classifier.py`) |
| Existing MCP servers | `wave/tools/ai/mcp_servers/` |
| Refinery types | `wave/experiments/refinery-platform/lib/nodes/types.ts` |
| Static registries | `wave/experiments/refinery-platform/lib/nodes/registry/` |
| SemanticPage | `wave/experiments/refinery-platform/lib/nodes/SemanticPage.tsx` |
| NodeRenderer | `wave/experiments/refinery-platform/lib/nodes/NodeRenderer.tsx` |
| Domain config | `wave/experiments/refinery-platform/lib/nodes/domainConfig.ts` |
| Sidebar | `wave/experiments/refinery-platform/components/layout/Sidebar.tsx` |
| Polling hooks | `wave/experiments/refinery-platform/lib/usePolling.ts`, `useMultiPolling.ts` |
| API layer | `wave/experiments/refinery-platform/lib/api.ts` |
| AppSpec types | `wave/experiments/refinery-platform/lib/ingestion/types.ts` |
| Inbox page | `wave/experiments/refinery-platform/app/inbox/page.tsx` |
| Cerebras rapid intel | `wave/tools/ai/cerebras_rapid_intel.py` |
| This spec | `docs/superpowers/specs/2026-03-12-collider-ingestion-design.md` |
