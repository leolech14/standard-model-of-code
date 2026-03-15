# Refinery Platform -- Common Knowledge

Shared SSOT for all AI agents (Claude, Gemini, Codex). Agent-specific files are thin wrappers that import this document plus their own deltas.

---

## Identity

**Refinery Platform** is the full-scope ecosystem dashboard for OpenClaw. It surfaces 200+ API endpoints across 12 domains as a unified, accessible, readable, editable frontend.

```
Stack:      Next.js 15 / React 19 / Tailwind 4 / TypeScript
Port:       3001 (dev + prod)
API Proxy:  /api/openclaw/:path*  ->  localhost:8100/api/:path*
Local API:  /api/v1/:path*        ->  Next.js API routes (mock/provisional)
Deploy:     dashboard.centralmcp.ai (behind Authelia)
Origin:     Wave hemisphere of PROJECT_elements
Future:     Standalone product (L7 -> L8)
```

---

## Algebra-UI Design System

**Algebra-UI** (also: vector-ui lineage, soft-token architecture) is the parametric design engine powering every visual property. The core distinction:

### Hard Tokens (Seeds / Anchors)

Explicit values that ground the system. These are chosen, not computed:

```css
--bg-l: 0.145;                /* background lightness seed */
--emerald-l: 0.696;           /* accent hue lightness */
--emerald-c: 0.170;           /* accent chroma */
--emerald-h: 162;             /* accent hue angle */
--space-unit: 0.25rem;        /* spatial atom */
--radius-seed: 0.5rem;        /* corner atom */
--motion-unit: 50ms;          /* temporal atom */
```

These are the **genotype** -- the DNA of the design.

### Soft Tokens (Computed / Derived)

Every other visual value is a mathematical function of hard tokens + coefficients:

```css
/* color: seed L + coefficient -> computed L */
--color-surface: oklch(calc(var(--bg-l) + var(--coeff-surface-l)) 0 0);
--emerald-light: oklch(calc(var(--emerald-l) + var(--coeff-hover-l)) var(--emerald-c) var(--emerald-h));

/* spacing: atom * multiplier * density */
--gap-sm: calc(var(--space-2) * var(--density));

/* shadow: geometry * strength coefficient */
--shadow-sm: 0 2px 8px oklch(0 0 0 / calc(0.12 * var(--shadow-strength)));
```

These are the **phenotype** -- the expression of the DNA under environmental conditions (theme, density, viewport).

### Coefficients (The Knobs)

Transform constants that shape soft tokens from hard tokens:

| Coefficient | Dark | Light | Purpose |
|------------|------|-------|---------|
| `--coeff-hover-l` | +0.05 | -0.05 | Hover brightness shift |
| `--coeff-surface-l` | +0.033 | +0.028 | Surface offset from bg |
| `--coeff-border-l` | +0.086 | -0.096 | Border offset from bg |
| `--coeff-dim-l` | -0.10 | -0.10 | Muted variant dimming |
| `--coeff-dim-c` | 0.7 | 0.7 | Muted chroma reduction |
| `--coeff-glow-alpha` | 0.25 | 0.15 | Glow/shadow alpha |
| `--shadow-strength` | 1.0 | 0.5 | Shadow intensity multiplier |
| `--glass-alpha` | 0.5 | 0.7 | Glass surface opacity |
| `--density` | 1.0 | 1.0 | Spacing density multiplier |

### Theme = Seed Override

Light theme is ~25 lines of seed + coefficient overrides in `[data-theme="light"]`. Every soft token recomputes automatically via CSS calc(). No component-level theme logic anywhere.

### Intellectual Lineage

```
PROJECT_vector-ui (2025)          Research: OKLCH analysis of 513K Android UIs
  -> 5 universal laws of UI beauty   -> basis vector extraction (UI Algebra)
  -> parametric design system concept  -> design-tokens-compact.json (OKLCH)

Refinery Platform (2026)          Production: full parametric OKLCH engine
  -> 4-layer token architecture      -> seeds + coefficients + calc() = all properties
  -> 7 parametric domains            -> theme = seed override (25 lines)
```

The research discovered the math. The platform ships it.

### Single Source of Truth

`app/globals.css` (644 lines) contains the entire engine. No other file defines visual properties. Components reference tokens via Tailwind utilities (`bg-surface`, `text-accent`, `border-border`) mapped through the `@theme` block, never raw color values.

---

## OpenClaw API Surface

12 domains, 200+ endpoints. All proxied through `/api/openclaw/:path*`.

| Domain | Key Endpoints | Polling |
|--------|--------------|---------|
| System | `health`, `system/current`, `system/history` | 10s |
| Voice | `voice/gateway/status`, `voice/providers` | 15s |
| LLM | `llm/mode` (GET+POST confirmed); `llm/health`, `llm/providers/status` (planned, not yet in backend) | 15s |
| Comms | `commlog/recent`, `activity/recent`, `channels/config` | 10s |
| Automations | `automations`, `automations/{id}` | 30s |
| Trading | `trading/current`, `trading/market-state`, `trading/auto-entry`, `trading/ranking` (GET); `trading/auto-entry/toggle` (POST) | 10s/15s/30s |
| Finance | `voice/finance/status`, `voice/finance/snapshot`, `voice/finance/pending` (GET); `voice/invoices/check`, `voice/invoices/summary` (GET); `voice/finance/pluggy/items/known`, `voice/finance/pluggy/operations` (GET); `voice/finance/confirm`, `voice/finance/cancel`, `voice/finance/pluggy/item/refresh` (POST) | 30s |
| Memory | `voice/memory`, `voice/self-knowledge` | 30s |
| Tools | `tools`, `voice/mcp/servers` | 30s |
| Collider | `collider/*`, `refinery/*` | 30s |
| Google | `google/calendar`, `google/email`, `google/drive` | 30s |
| Settings | `voice/config/get?domain=*` (4 domains), `voice/config/set` (POST), `thresholds` | 30s |

Polling tiers: 10s (live ops), 15s (semi-live), 30s (stable).

---

## Component Library

### UI Primitives (`components/ui/`)

10 components: `Tabs`, `DataTable`, `Select`, `Toggle`, `Modal`, `Toast`, `Gauge`, `Skeleton`, `SearchInput`, `ActionButton` + barrel `index.ts`.

### Shared (`components/shared/Common.tsx`)

`UiLink`, `UiRow`, `Badge`, `SectionHeader`, `EmptyState`. All use parametric tokens exclusively.

### Layout (`components/layout/`)

`Sidebar.tsx` (5 groups, 14 items), `ThemeProvider.tsx` (context wrapper).

### Hooks (`lib/`)

- `api.ts` -- centralized fetch with `apiGet`, `apiPost`, `apiPut`, `apiDelete` (OpenClaw proxy) and `localGet` (local Next.js routes). All throw `ApiError` on non-2xx.
- `usePolling.ts` -- auto-refresh with tab visibility awareness. Uses `apiGet` internally (OpenClaw endpoints only). Three tiers: 10s/15s/30s.
- `useMutation.ts` -- POST + toast confirmation pattern.
- `useTheme.ts` -- mode/toggle/system theme switching.

---

## Route Inventory

### Implemented Pages

| Route | Data Source | Hooks | Mode |
|-------|------------|-------|------|
| `/` (Overview) | `localGet` (local) | `localGet` | sensory |
| `/projects` | `localGet` (local) | `localGet` | sensory |
| `/chunks` | `localGet` (local) | `localGet` | sensory |
| `/infra` | `localGet` (local) | `localGet` | sensory |
| `/rainmaker` | OpenClaw API | `usePolling` x3 | sensory |
| `/system` | OpenClaw API (node-driven) | `usePolling` x3, `useMutation` x1, `NodeRenderer` x11 | sensory-motor |
| `/voice` | OpenClaw API | `usePolling` x4, `useMutation` x2, `useToast` | sensory-motor |
| `/llm` | OpenClaw API | `usePolling` x1, `useMutation` x1, `useToast` | sensory-motor |
| `/settings` | OpenClaw API | `usePolling` x5, `useMutation` x1, `useToast` | sensory-motor |
| `/trading` | OpenClaw API | `usePolling` x4, `useMutation` x1, `useToast` | sensory-motor |
| `/finance` | OpenClaw API | `usePolling` x7, `useMutation` x3, `useToast` | sensory-motor |
| `/inbox` | Static (lib/ingestion/specs.ts) | none | sensory (drill-in) |

12 pages implemented. `/inbox` is a client-side listing page with drill-in to AppSpecInspector (no polling, static specs). `/system`, `/voice`, `/llm`, `/settings`, `/trading`, and `/finance` are sensory-motor pages (read + guarded mutations). `/trading` has 2 tabs (Status | Opportunities) with mixed polling tiers (10s/15s/30s) and dynamic query params for ranking filters. `/finance` has 3 tabs (Overview | Invoices | Pluggy) with 5 eager polls + 2 tab-gated polls. `/llm` is single-view (no tabs). `/settings` has 2 tabs polling 4 config domains independently.

### Missing Pages (sidebar-promised)

`/automations`, `/comms`, `/memory`, `/tools`, `/google` -- 5 routes, all placeholder/404.

---

## Navigation Architecture

15 sidebar items in 5 groups:

| Group | Routes |
|-------|--------|
| Operations | `/system`, `/voice`, `/llm`, `/automations` |
| Communications | `/comms` |
| Finance | `/trading`, `/finance` |
| Intelligence | `/inbox`, `/memory`, `/tools` |
| Platform | `/projects`, `/chunks`, `/infra`, `/google`, `/settings` |

Each page uses Tabs for sub-views. `/rainmaker` is accessed via a floating cloud widget, not the sidebar.

---

## Semantic Node Architecture

The platform is pivoting from page-first to **node-first** architecture. The same algebraic derivation principle used for style (seeds + coefficients → derived tokens) now applies to the entire UI surface: semantic definitions + owner preferences → derived interface.

### Core Concept

Every visual unit is a **NodeDefinition** — a sensory-motor unit. Sense (IN) = data polling endpoint + field extraction. Mutations (OUT) = user-triggered actions. Pages compose nodes; the rendering bridge translates semantic definitions into React components.

### Architecture Layers

```
SEMANTIC LAYER       lib/nodes/types.ts, registry/*.ts, defaultProfile.ts
RENDERING BRIDGE     lib/nodes/NodeRenderer.tsx, views/*.tsx
SUBSTRATE            lib/usePolling.ts, useMutation.ts, api.ts, components/ui/*
```

### Node Registry

| Domain | Nodes | Endpoints | Status |
|--------|-------|-----------|--------|
| System | 11 | health, system/current, system/history | ACTIVE — /system renders from nodes |
| Voice | 5 | voice/providers, llm/mode, voice/self-knowledge, voice/gateway/status, meet/status | DEFINED — not yet wired to page |

### Data Flow

Page calls `usePolling` per unique endpoint → passes raw data to `<NodeRenderer>` → NodeRenderer extracts sub-field via `fieldPath` → resolves view kind from profile/node hints → view component renders using existing UI primitives.

### Key Files

| File | Purpose |
|------|---------|
| `lib/nodes/types.ts` | NodeDefinition contract, all type definitions |
| `lib/nodes/helpers.ts` | extractField, interpolateTemplate, formatNodeValue, statusToBadge |
| `lib/nodes/defaultProfile.ts` | OwnerRepresentationProfile default |
| `lib/nodes/NodeRenderer.tsx` | View selector + renderer dispatch |
| `lib/nodes/views/*.tsx` | GaugeView, StatView, StatusView, TableView, FeedView, JsonView |
| `lib/nodes/registry/system.ts` | 11 system domain nodes |
| `lib/nodes/registry/voice.ts` | 5 voice domain nodes |
| `lib/nodes/registry/index.ts` | Aggregator + selectors |

### Future Direction

All remaining pages will be derived from node definitions. Every node.id can become a URL (`/node/system.cpu`), enabling infinite navigable surface. Owner preferences will control rendering: salience + order → screen real estate allocation.

---

## Code-to-Spec Ingestion System

The platform can ingest external code artifacts (zips, repos, packages) and reverse-engineer them into structured specifications compatible with the Semantic Node Architecture. This is the "Apps Inbox" pipeline.

### AppSpec Type System

`AppSpec` mirrors NodeDefinition's Sense/Interpret/Represent philosophy but applied to entire code artifacts rather than live data nodes:

```
AppSpec
├── meta          Identity, stack signature, ingestion status
├── architecture  Pattern, entry point, component tree, state management
├── sense         APIs consumed, browser APIs, data lifecycle
├── interpret     Type system, transforms, algorithms
├── represent     Layout system, views, theming, render tech
├── dependencies  Runtime + dev with weight classification
├── exposable[]   Bridge to NodeDefinition (auto-promotion candidates)
└── risks[]       Security, compatibility, performance, maintenance
```

### ExposableNode Bridge

Each `ExposableNode` in an AppSpec is a candidate for automatic promotion into the NodeDefinition registry:

```typescript
interface ExposableNode {
  suggestedId: string;     // 'inbox.app-name.data-source'
  title: string;           // Human-readable name for Refinery
  nodeKind: NodeKind;      // metric | status | table | feed | composite | control
  senseStrategy: string;   // How Refinery would poll this data
  viewKind: string;        // Suggested rendering approach
  confidence: number;      // 0-1, extraction confidence
}
```

When confidence is high enough (>0.75), an ExposableNode can be automatically converted to a full NodeDefinition and added to the registry -- making external app data available as first-class dashboard widgets.

### Apps Inbox UI

The Overview page includes an "Apps Inbox" card (sibling to pipeline cards) that surfaces pending ingested apps. Clicking an app opens the `AppSpecInspector` drawer with 7 collapsible sections (Architecture, Components, Sense, Interpret, Represent, Dependencies, Exposable Nodes, Risks).

### Current Inventory

| App | Origin | Stack | ExposableNodes | Confidence |
|-----|--------|-------|----------------|------------|
| cloud-refinery-console | zip-upload | React/Vite/TS/Tailwind | 4 (pipelines, artifacts, runs, alerts) | 75-90% |
| audio-analyzer-pro | zip-upload | React/Vite/TS/Tailwind | 2 (LUFS meter, spectrum) | 45-60% |

### Key Files

| File | Purpose |
|------|---------|
| `lib/ingestion/types.ts` | AppSpec contract (15 interfaces) |
| `lib/ingestion/specs.ts` | Hand-crafted spec instances (format documentation) |
| `components/ingestion/AppSpecInspector.tsx` | Spec viewer UI (7 sections, Algebra-UI tokens) |
| `app/inbox/page.tsx` | Inbox listing page with drill-in inspector |

### Unified Vision

The three derivation engines (Algebra-UI for visuals, NodeDefinition for data, AppSpec for code) converge into a single paradigm: **Spec → Engine → Cache**. Source of truth is always the specification; rendered code is an ephemeral materialization. Full vision document: `~/.claude/plans/unified-spec-engine-vision.md`.

---

## Implementation Status

| Phase | Status | Scope |
|-------|--------|-------|
| 0A | DONE | Parametric OKLCH token engine (644-line globals.css) |
| 0B | DONE | 10 UI components, 4 hooks, sidebar, layout. All pages wired to token system and centralized API layer. |
| 1 | DONE | System, Voice, LLM -- all sensory-motor pages. |
| 2 | IN PROGRESS | Settings (DONE). Comms + Automations blocked (no backend polling endpoints). |
| 3 | DONE | Trading + Finance. |
| 5 | IN PROGRESS | Node-first architecture pivot. System domain (11 nodes) + Voice domain (5 nodes) defined. /system refactored to render from node definitions. |
| 6 | IN PROGRESS | Code-to-Spec ingestion. AppSpec type system (15 interfaces), 2 hand-crafted specs, AppSpecInspector UI, Apps Inbox card on Overview. |
| Next | PENDING | Registry expansion (trading, finance, llm, settings domains). Remaining pages built from registry. ExposableNode auto-promotion. Automated code analysis pipeline. |

Architecture plans:
- Node architecture: `~/.claude/plans/curried-humming-giraffe.md`
- Unified vision: `~/.claude/plans/unified-spec-engine-vision.md`
- Code-to-Spec deep ref: `docs/code-to-spec-architecture.md`

---

## Non-Negotiable Rules

1. **All color is OKLCH.** No hex, no rgb, no hsl in component code.
2. **Tokens are the contract.** Components use Tailwind utilities mapped to tokens (`bg-surface`, `text-accent`). Never hardcode visual values.
3. **Light theme = seed overrides only.** No component-level theme conditionals.
4. **Confirm all mutations.** ActionButton -> Modal -> API -> Toast.
5. **Centralized API layer.** All OpenClaw calls through `apiGet`/`apiPost`. All local calls through `localGet`. No raw `fetch`.
6. **Build must pass.** `npm run build` before deploy. Always.

---

## Key Paths

| Task | File |
|------|------|
| Parametric engine (ALL visual properties) | `app/globals.css` |
| Theme switching | `lib/useTheme.ts` + `components/layout/ThemeProvider.tsx` |
| API abstraction | `lib/api.ts` + `lib/usePolling.ts` + `lib/useMutation.ts` |
| Component library | `components/ui/` (10 primitives) |
| Node contract + types | `lib/nodes/types.ts` |
| Node registry (all domains) | `lib/nodes/registry/` |
| Rendering bridge | `lib/nodes/NodeRenderer.tsx` + `lib/nodes/views/` |
| Owner profile | `lib/nodes/defaultProfile.ts` |
| Navigation | `components/layout/Sidebar.tsx` |
| Root layout | `app/layout.tsx` |
| API proxy config | `next.config.ts` |
| AppSpec types | `lib/ingestion/types.ts` |
| AppSpec instances | `lib/ingestion/specs.ts` |
| AppSpec inspector | `components/ingestion/AppSpecInspector.tsx` |
| Inbox page | `app/inbox/page.tsx` |
| Code-to-Spec architecture | `docs/code-to-spec-architecture.md` |
| Unified vision document | `~/.claude/plans/unified-spec-engine-vision.md` |
| Agent shared SSOT | `.ecoroot/common_knowledge.md` (this file) |
| Claude-specific | `.claude/CLAUDE.md` |
| Gemini-specific | `GEMINI.md` |
| Codex-specific | `AGENTS.md` |
