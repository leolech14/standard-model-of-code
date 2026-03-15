# Code-to-Spec Architecture Reference

Deep technical specification for the ingestion pipeline that converts external code artifacts into structured AppSpec documents compatible with the Semantic Node Architecture.

---

## Pipeline Overview

```
External Code Artifact
    │
    ▼
┌─────────────────────────────────┐
│  1. INTAKE                      │
│  File upload / git clone / npm  │
│  → staging area                 │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  2. STATIC ANALYSIS             │
│  Package.json → StackSignature  │
│  AST parse → ComponentNode[]    │
│  Import graph → Dependencies    │
│  File scan → DirectoryRole[]    │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  3. SEMANTIC EXTRACTION         │
│  API calls → AppSense.apis[]   │
│  Browser APIs → browserApis[]  │
│  Types → TypeDef[]             │
│  Transforms → DataTransform[]  │
│  Algorithms → Algorithm[]      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  4. EXPOSURE ANALYSIS           │
│  Data sources → ExposableNode[] │
│  Confidence scoring             │
│  Risk assessment                │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  5. SPEC ASSEMBLY               │
│  → AppSpec v1.0 document        │
│  → Stored in inbox registry     │
│  → Available in Apps Inbox UI   │
└─────────────────────────────────┘
```

**Current state:** Steps 1-5 are performed manually (hand-crafted specs). Automation targets steps 2-4.

---

## Type Topology

The AppSpec type system consists of 15 interfaces organized in a strict hierarchy. Each interface maps to a specific analysis concern.

### Root Document

```
AppSpec
├── specVersion: '1.0'              (format version, always '1.0')
├── meta: AppSpecMeta               (identity + status)
├── architecture: AppArchitecture   (structural analysis)
├── sense: AppSense                 (data ingestion patterns)
├── interpret: AppInterpret         (transformation logic)
├── represent: AppRepresent         (rendering output)
├── dependencies: AppDependencies   (package graph)
├── exposable: ExposableNode[]      (NodeDefinition candidates)
└── risks: AppRisk[]                (hazard inventory)
```

### Interface Map (15 total)

```
AppSpec ─┬─ AppSpecMeta ──── StackSignature
         │
         ├─ AppArchitecture ─┬─ StateManagement
         │                   ├─ ComponentNode
         │                   └─ DirectoryRole
         │
         ├─ AppSense ────────┬─ ApiConsumption
         │                   ├─ BrowserApiUsage
         │                   └─ LocalSource
         │
         ├─ AppInterpret ────┬─ TypeDef
         │                   ├─ DataTransform
         │                   └─ Algorithm
         │
         ├─ AppRepresent ────┬─ AppView
         │                   └─ ThemingInfo
         │
         ├─ AppDependencies ── Dependency
         │
         ├─ ExposableNode (bridge to NodeDefinition)
         │
         └─ AppRisk
```

### Sense/Interpret/Represent Parallel

AppSpec deliberately mirrors NodeDefinition's three-phase model, but at app-level granularity:

| Phase | NodeDefinition (data node) | AppSpec (code artifact) |
|-------|---------------------------|------------------------|
| **Sense** | Single API endpoint + polling interval | All API endpoints + browser APIs + local sources + lifecycle strategy |
| **Interpret** | Thresholds + formatting + badges | Full type system + transform functions + algorithms |
| **Represent** | Single view kind + salience + columns | Layout system + multiple views + theming + render tech |

The mapping is **1:N** — one AppSpec can yield multiple NodeDefinitions through the ExposableNode bridge.

---

## ExposableNode: The Bridge Protocol

ExposableNode is the critical interface that connects the Code-to-Spec pipeline to the live dashboard. Each ExposableNode represents a data source within the ingested app that could become a first-class Refinery widget.

### Promotion Flow

```
ExposableNode (in AppSpec)
    │
    │  confidence >= threshold (0.75)
    │
    ▼
NodeDefinition (in Registry)
    │
    ├─ id: exposable.suggestedId
    ├─ kind: exposable.nodeKind
    ├─ sense: derived from exposable.senseStrategy
    │         (needs adapter: proxy, iframe, postMessage, etc.)
    ├─ interpret: inferred from source app's type system
    ├─ representation.preferredView: exposable.viewKind
    │
    ▼
NodeRenderer → Live Widget on Dashboard
```

### Sense Strategy Patterns

How external app data becomes pollable by Refinery:

| Strategy | Description | Example |
|----------|-------------|---------|
| **Local API Proxy** | App exposes data via `/api/` route, Refinery proxies it | `cloud-refinery-console` pipelines |
| **localStorage Proxy** | App persists to localStorage, local API route reads it | `cloud-refinery-console` artifacts |
| **postMessage Embed** | App runs in iframe, exposes data via `window.postMessage` | `audio-analyzer-pro` LUFS reading |
| **Custom View Embed** | App's canvas/WebGL output embedded as custom NodeRenderer view | `audio-analyzer-pro` spectrum |
| **File Parse** | App generates output files, Refinery reads them periodically | Static generators, CLI tools |
| **WebSocket Bridge** | App streams data, Refinery connects to the stream | Real-time services |

### Confidence Scoring

Confidence reflects how cleanly an app's data source maps to a NodeDefinition:

| Range | Meaning | Action |
|-------|---------|--------|
| 0.90-1.00 | Direct mapping, minimal adapter needed | Auto-promote |
| 0.75-0.89 | Good mapping, simple adapter | Suggest with one-click promote |
| 0.50-0.74 | Partial mapping, significant adapter work | Show in inspector, manual review |
| 0.00-0.49 | Speculative, requires custom integration | Display as "potential" only |

---

## AppSpec Sections: Deep Reference

### Meta

Identity and ingestion status. The `StackSignature` sub-interface captures the technology fingerprint used for compatibility analysis.

```typescript
StackSignature {
  framework: string;   // 'react' | 'vue' | 'svelte' | 'vanilla' | ...
  bundler: string;     // 'vite' | 'webpack' | 'next' | 'esbuild' | ...
  language: string;    // 'typescript' | 'javascript' | 'python' | ...
  styling: string;     // 'tailwind' | 'css-modules' | 'styled-components' | ...
  target: 'browser' | 'node' | 'edge' | 'hybrid';
}
```

**Why this matters:** StackSignature determines compatibility with Refinery's ecosystem. A React/TS/Tailwind app has near-zero integration friction. A Python CLI app needs a different adapter strategy entirely.

### Architecture

Structural analysis of the codebase. The `ComponentNode` tree is the most information-dense sub-structure:

```typescript
ComponentNode {
  name: string;              // 'App', 'Spectrogram', 'DataTable'
  path: string;              // Relative file path
  loc: number;               // Lines of code (complexity signal)
  props: Record<string, string>;  // Props interface
  children: string[];        // Child component names
  role: string;              // One-line purpose
  complexity: 'leaf' | 'branch' | 'root';
}
```

**Complexity classification:**
- `root`: Entry/layout component, composes the entire app
- `branch`: Intermediate component, composes children but has own logic
- `leaf`: Terminal component, renders UI without composing others

### Sense (Data In)

Catalogs every data source the app consumes. Three categories:

1. **APIs** (`ApiConsumption[]`): External HTTP endpoints with method, return type, and consuming components
2. **Browser APIs** (`BrowserApiUsage[]`): Web platform APIs with complexity rating
3. **Local Sources** (`LocalSource[]`): localStorage, indexedDB, file inputs, hardcoded data, generated data

The `lifecycle` field describes the overall data refresh pattern:
- `polling`: Regular interval fetches
- `event-driven`: Fetches triggered by user actions or events
- `raf`: `requestAnimationFrame` loop (real-time rendering)
- `manual`: User-triggered only
- `static`: Data loaded once, never refreshed
- `mixed`: Combination of patterns

### Interpret (Transforms)

Three sub-analyses:

1. **TypeDef[]**: Every interface/type in the codebase with field count and purpose
2. **DataTransform[]**: Input → output transformations (data flows)
3. **Algorithm[]**: Non-trivial computations with complexity classification

**Complexity ratings for algorithms:**
- `trivial`: Simple branching, lookups, formatting
- `linear`: Single-pass array operations, mapping, filtering
- `nontrivial`: Multi-step computation, signal processing, tree operations

### Represent (Views)

The output side: what the app renders and how.

```typescript
AppView {
  name: string;
  renders: string;           // What it displays
  renderTech: 'dom' | 'canvas-2d' | 'webgl' | 'svg' | 'three.js';
  realtime: boolean;         // RAF loop or streaming
  component: string;         // Implementing component
}
```

**Render tech is critical** for Refinery integration:
- `dom`: Can be embedded as React component directly
- `canvas-2d` / `webgl` / `three.js`: Needs iframe or custom view embedding
- `svg`: Can be embedded as React component with minor adaptation

### Risks

Hazard inventory with four categories:

| Category | What it catches |
|----------|----------------|
| `security` | API keys in code, XSS vectors, unsafe eval |
| `compatibility` | Framework version conflicts, CSS clashes, heavy deps |
| `performance` | Monolithic components, excessive RAF loops, large bundles |
| `maintenance` | Missing tests, no types, abandoned dependencies |
| `missing` | Expected files/features not found (tests, docs, CI) |

---

## Integration with Algebra-UI

The `ThemingInfo` field in AppSpec's `represent` section identifies color system compatibility:

| App's colorModel | Algebra-UI Compatibility | Migration Path |
|-----------------|-------------------------|----------------|
| `oklch` | Native compatible | Direct token binding |
| `hsl` | Partially compatible | Convert to OKLCH coordinates |
| `hex` / `rgb` | Incompatible | Full color migration needed |
| `mixed` | Partial | Audit per-component |

Apps using OKLCH and CSS custom properties can bind directly to Algebra-UI's parametric engine with minimal work. Apps using hex/rgb require a color migration pass before their views can participate in the unified theme system.

---

## File Inventory

| File | Lines | Purpose |
|------|-------|---------|
| `types/appSpec.ts` | 287 | Complete type system (15 interfaces) |
| `services/inboxSpecs.ts` | 325 | Hand-crafted spec instances for 2 apps |
| `components/AppSpecInspector.tsx` | 340 | Spec viewer UI with 7 collapsible sections |

**Note:** These files currently live in `/tmp/refinery-console/` (the cloud-refinery-console standalone app). When the Code-to-Spec system is promoted to the main Refinery Platform, these types and components will move to `lib/ingestion/` and `components/ingestion/` respectively.

---

## Automation Roadmap

### Phase A: Static Analysis (deterministic)
- Parse `package.json` → auto-fill `StackSignature`
- Parse `tsconfig.json` → language/target detection
- File-system scan → `DirectoryRole[]` + `fileCount` + `sizeBytes`
- Import graph → `ComponentNode[]` with children relationships
- `grep` patterns → `ApiConsumption[]` (fetch/axios calls), `BrowserApiUsage[]`

### Phase B: Semantic Analysis (LLM-augmented)
- Component purpose inference → `ComponentNode.role`
- Algorithm detection and complexity rating → `Algorithm[]`
- ExposableNode candidate identification → `ExposableNode[]`
- Risk assessment → `AppRisk[]`

### Phase C: Interactive Refinement
- User confirms/adjusts auto-generated spec
- Confidence scores updated based on user feedback
- ExposableNode promotion to NodeDefinition registry

### Phase D: Continuous Ingestion
- Watch directories for new code drops
- Auto-generate AppSpec on arrival
- Notification when new ExposableNodes are available
- One-click promote to live dashboard

---

## References

| Document | Path |
|----------|------|
| AppSpec types | `types/appSpec.ts` (current: `/tmp/refinery-console/`) |
| NodeDefinition types | `lib/nodes/types.ts` |
| Unified vision | `~/.claude/plans/unified-spec-engine-vision.md` |
| Node architecture SSOT | `.ecoroot/common_knowledge.md` (Semantic Node Architecture section) |
| Algebra-UI engine | `app/globals.css` |
