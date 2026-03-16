# Dashboard Engine: Component Registry & Nicknames

> Every component involved in the parametric UI pipeline. Official name + internal nickname + feature list.
> Nicknames should make the function POP — when you hear the name, you know what it does.

---

## Pipeline Components (in execution order)

---

### 1. Semantic Files

**Official:** Semantic Definition Files
**Nickname suggestions:**
- **Scrolls** — ancient documents that carry the knowledge (purpose, data, controls)
- **Blueprints** — because they define what gets built without being the building
- **Genomes** — fits the Algebra-UI genotype/phenotype language — they ARE the DNA

**Features:**
- Declare page mission and success criteria
- Define each node's purpose (what question it answers, what it's becoming)
- Specify data sources (endpoint, polling interval, field extraction)
- Declare controls and mutations (two-way logic — not just display)
- Tag everything for AI discoverability
- Specify adjacency requirements (what needs to be near what)
- Provide the `becoming` field — developmental direction, not just current state
- Can be edited by humans OR AI agents in real-time
- Format: YAML/JSON on filesystem (not compiled TypeScript)

---

### 2. Semantic File Reader

**Official:** Filesystem Intake
**Nickname suggestions:**
- **Receptor** — biological: the cell surface that detects signals from the environment
- **Scanner** — it scans the filesystem for semantic files continuously
- **Intake** — fits the Refinery metaphor (raw material enters the refinery)

**Features:**
- Watch filesystem for semantic file changes (inotify/FSEvents)
- Parse YAML/JSON into typed structures
- Cache parsed files in memory (invalidate on change)
- Diff-based updates (only re-process what changed)
- Validate semantic file schema on read (reject malformed)
- Report which files are loaded, stale, or failed
- Handle missing files gracefully (freeze last good, warn)
- Provide file metadata (mtime, size, hash) for change detection

---

### 3. Purpose Interpreter

**Official:** Purpose-to-Layout Resolver
**Nickname suggestions:**
- **Compass** — points you to what matters most (relevance → direction)
- **Lens** — focuses attention where it belongs (attentionCost → sizing)
- **Diviner** — reads the purpose and divines the layout from it

**Features:**
- Read `purpose.relevance` (0-1) → compute area allocation percentage
- Read `purpose.narrativeRole` → assign zone (top/middle/bottom/contextual)
- Read `purpose.attentionCost` → determine view sizing (compact/medium/large/full)
- Rank nodes by relevance (descending) → produce ordering
- Derive `representation.salience` FROM relevance (not hardcoded)
- Derive `representation.order` FROM relevance rank (not hardcoded)
- Read `purpose.becoming` → flag developmental nodes for the user
- Map success_criteria → nodes that serve them (coverage check)
- Detect orphan nodes (purpose declared but no success criteria served)
- Output: LayoutInstructions[] (zone, area%, viewSize, order per node)

---

### 4. Token Resolver

**Official:** Algebra-UI Token Engine
**Nickname suggestions:**
- **Mint** — produces the currency (tokens) that everything else spends
- **Distillery** — fits Refinery perfectly: raw seeds distilled into refined values
- **Alchemist** — transforms base metals (seeds) into gold (visual properties)

**Features:**
- Resolve seeds + coefficients → all derived CSS values
- Support 7 parametric domains: color achromatic, color chromatic, spacing, radius, shadows, motion, glass
- OKLCH color space (perceptually uniform)
- Theme switching via seed overrides (~25 lines for light theme)
- CSS `calc()` native (browser-level performance)
- JS-side mirror for constraint engine access (not just CSS)
- Expose current resolved values as queryable map
- Support runtime coefficient changes (agent tuning)
- Coefficient bounds (min/max per coefficient — feeds into constraints)
- Output: Map<tokenName, resolvedValue> (every visual property as concrete value)

---

### 5. Constraint Validator

**Official:** Coherence & Restriction Engine
**Nickname suggestions:**
- **Arbiter** — the judge that decides if a combination is legal
- **Guardian** — protects the UI from incoherent states (but Sentinel is taken)
- **Censor** — blocks what shouldn't be shown (provocative, memorable)
- **Sieve** — fits Refinery: filters out impurities (incoherent combinations)

**Features:**
- Define constraints as typed rules (must / should / prefer)
- Color constraints: minimum contrast ratio (WCAG AA ≥ 4.5:1)
- Color constraints: adjacent surface lightness delta (≥ 0.02)
- Color constraints: chroma range per hue (beauty regions from vector-ui research)
- Spacing constraints: density bounds (0.5 ≤ density ≤ 2.0)
- Spacing constraints: minimum touch target (≥ 44px for accessibility)
- Typography constraints: heading/body ratio (1.5 ≤ ratio ≤ 3.0)
- Layout constraints: anchor area minimum (≥ 25% of viewport)
- Layout constraints: evidence zone scrollable (never exceeds viewport)
- Composition constraints: maximum nodes per visible page (cognitive load limit)
- Auto-correction for `should` violations (nudge to nearest legal value)
- Hard refusal for `must` violations (show fallback, log error)
- Warning for `prefer` violations (render but flag in engine status)
- Framework parameter snapping (values snap to framework's legal grid)
- Output: ValidatedTokens + Corrections[] + Warnings[] + Errors[]

---

### 6. Layout Composer

**Official:** Spatial Allocation Engine
**Nickname suggestions:**
- **Cartographer** — maps the territory (viewport) and decides what goes where
- **Typesetter** — like a newspaper typesetter: allocates space based on story importance
- **Mason** — builds the structure from the blueprint (semantic file)

**Features:**
- Sort nodes by relevance (purpose interpreter output)
- Group by narrative role → zone assignment (anchor/detail/evidence/action)
- Allocate area proportional to relevance within zones
- Respect adjacency constraints (requiresNearby → place adjacent)
- Respect contrast constraints (contrastsWith → place side-by-side)
- Determine grid vs stack vs inline layout per group
- Responsive breakpoints (viewport resize → re-compose)
- Handle overflow (too many nodes for viewport → paginate or collapse)
- Z-index assignment (modals, tooltips, floating controls)
- Output: LayoutInstruction[] (nodeId, zone, x, y, width, height, viewType)

---

### 7. Control Binder

**Official:** Two-Way Interaction Layer
**Nickname suggestions:**
- **Synapse** — the connection point between sensing and acting (neural metaphor)
- **Nerve** — carries signals both ways (sensory in, motor out)
- **Relay** — receives signal, triggers action, reports result

**Features:**
- Read `controls[]` from semantic files → create UI handlers
- Read `mutations[]` from node definitions → create action buttons
- Confirmation modals for dangerous actions
- Optimistic UI updates (show expected state before server confirms)
- Toast notifications on success/failure
- Debounce rapid interactions
- Keyboard shortcuts for common actions
- Real-time parameter editing (AI or human changes a seed → re-render)
- Undo/redo stack for parameter changes
- Control state persistence (remember toggle states across sessions)
- Output: Map<nodeId, ControlBinding[]> (trigger → handler → feedback)

---

### 8. Renderer

**Official:** Framework Adapter & Pixel Producer
**Nickname suggestions:**
- **Prism** — takes the unified light (resolved values) and splits it into visible spectrum (pixels)
- **Projector** — projects the abstract layout onto the physical screen
- **Canvas** — the surface where everything becomes visible

**Features:**
- Consume LayoutInstructions → produce DOM/components
- Consume ValidatedTokens → apply styles
- Consume ControlBindings → wire interactions
- React/Tailwind adapter (current implementation)
- Vanilla HTML adapter (future — proves framework-agnosticism)
- Terminal adapter (future — CLI dashboard over SSH)
- View primitive library: StatView, GaugeView, FeedView, TableView, ChartView, ControlView
- Custom view escape hatch (customViewId → user-provided component)
- Loading states (Skeleton components during data fetch)
- Error states (graceful degradation per node)
- Animation/transitions using motion tokens
- Output: Pixels on screen (or characters in terminal)

---

## Support Systems (always running, not in pipeline)

---

### 9. Anti-Fragility System

**Official:** Degradation & Recovery Manager
**Nickname suggestions:**
- **Immune** — the body's defense system: detects threats, isolates damage, heals
- **Cocoon** — wraps failing components in a safe shell while they recover
- **Buffer** — absorbs shocks without passing them through

**Features:**
- Monitor each pipeline stage independently
- Freeze-on-failure: keep last good output when a stage crashes
- Token domain independence (color fails → spacing still works)
- Graceful degradation cascade (parametric → semi-parametric → static fallback)
- Auto-recovery (retry failed stage on next trigger)
- Health status dashboard (which stages are healthy/frozen/failed)
- Circuit breaker (if a stage fails 3x, stop retrying, use frozen values)
- Recovery notification (stage healed → resume live values)

---

### 10. Performance Monitor

**Official:** Budget & Timing Tracker
**Nickname suggestions:**
- **Pulse** — the heartbeat monitor of the engine
- **Vitals** — life signs of every component
- **Chrono** — time is the critical resource it watches

**Features:**
- Track milliseconds per pipeline stage per run
- Track RAM usage per component
- Compare against budgets (warn if exceeding)
- Historical trending (is the engine getting slower?)
- Hot path identification (which stage bottlenecks?)
- Frame rate tracking (target: 40fps / 25ms total)
- Render count per second
- Node count impact analysis (how many nodes before budget breaks?)
- Auto-throttle (reduce scope if budget exceeded)

---

### 11. AI Parameter API

**Official:** Agent Interface for Real-Time Control
**Nickname suggestions:**
- **Dial** — agents turn the dials to adjust the system
- **Remote** — remote control for the dashboard
- **Tuner** — fine-tune parameters without touching code

**Features:**
- REST/MCP endpoint: GET current parameter values
- REST/MCP endpoint: SET seed, coefficient, or purpose values
- REST/MCP endpoint: GET current engine state (health, timings, frozen stages)
- REST/MCP endpoint: GET node data (what is journal.velocity showing right now?)
- Validate parameter changes against constraints before applying
- Emit change events (SSE/WebSocket) so dashboard updates in real-time
- Audit log (who changed what, when, previous value)
- Batch parameter changes (change 5 seeds atomically)
- Rollback to previous parameter set
- MCP tool exposure (agents can use via Claude Code / Gemini / Codex)

---

### 12. Theme Engine

**Official:** Seed Set Manager
**Nickname suggestions:**
- **Palette** — the set of colors/values active right now
- **Skin** — the current visual identity (swappable)
- **Mood** — because themes are moods: dark is serious, light is open

**Features:**
- Store named theme presets (dark, light, high-contrast, custom)
- Theme = seed overrides + coefficient adjustments (nothing else)
- Switch themes in <5ms (just change CSS variables)
- Auto-detect system preference (prefers-color-scheme)
- Schedule-based themes (dark at night, light during day)
- Theme preview (show before applying)
- Custom theme builder (adjust seeds via sliders)
- Export/import themes as JSON
- Per-page theme overrides (if needed)

---

### 13. Event Bus

**Official:** Change Propagation System
**Nickname suggestions:**
- **Ripple** — fits the Contextome Ripple Protocol: a change ripples through
- **Wave** — a signal that propagates (fits the Wave hemisphere naming)
- **Current** — electrical current flowing through the system

**Features:**
- Emit events on: semantic file change, parameter change, theme switch, resize, data refresh
- Subscribe to events per component (only process relevant changes)
- Debounce rapid changes (batch multiple edits into one pipeline run)
- Event types: `file-changed`, `param-set`, `theme-switch`, `viewport-resize`, `data-refresh`, `stage-failed`, `stage-recovered`
- Event log (for debugging: what triggered what)
- Priority handling (user interactions > agent changes > scheduled refreshes)

---

### 14. State Store

**Official:** Live Parameter Cache
**Nickname suggestions:**
- **Register** — like a CPU register: fast, always current, the working memory
- **Ledger** — the current state of all accounts (every parameter value)
- **Vault** — the secure store of all active values

**Features:**
- Hold current values of all seeds, coefficients, and derived tokens
- Hold current semantic file cache (parsed, typed)
- Hold current layout state (zone allocations, node positions)
- Hold current control state (toggle positions, filter selections)
- Snapshot/restore (save state → restore later)
- Diff capability (what changed between two states?)
- Serializable (can be saved to disk or sent to AI)
- Reactive (changes trigger pipeline re-run)

---

## Component Interaction Map

```
                    ┌─────────────┐
                    │   Scrolls   │ ← semantic files on disk
                    └──────┬──────┘
                           │ read by
                    ┌──────▼──────┐
                    │  Receptor   │ ← filesystem watcher + parser
                    └──────┬──────┘
                           │ parsed data
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼──────┐ ┌──▼───┐ ┌──────▼──────┐
       │   Compass   │ │ Mint │ │   Synapse   │
       │  (purpose)  │ │(token│ │  (controls) │
       └──────┬──────┘ └──┬───┘ └──────┬──────┘
              │            │            │
              └────────────┼────────────┘
                           │ all feed into
                    ┌──────▼──────┐
                    │    Sieve    │ ← constraint validation
                    └──────┬──────┘
                           │ validated
                    ┌──────▼──────┐
                    │ Cartographer│ ← layout composition
                    └──────┬──────┘
                           │ laid out
                    ┌──────▼──────┐
                    │    Prism    │ ← render to pixels
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   SCREEN    │
                    └─────────────┘

     Support systems (always running):
     ┌────────┐ ┌───────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐
     │ Immune │ │ Pulse │ │ Dial │ │  Mood  │ │ Ripple │ │Register│
     └────────┘ └───────┘ └──────┘ └────────┘ └────────┘ └────────┘
```

---

## Summary Table

| # | Official Name | Nickname | Type | Features | Status |
|---|--------------|----------|------|----------|--------|
| 1 | Semantic Definition Files | **Scrolls** | Source | Purpose, data, controls, becoming | PARTIAL (TS, not YAML) |
| 2 | Filesystem Intake | **Receptor** | Pipeline | Watch, parse, cache, validate | NOT BUILT |
| 3 | Purpose-to-Layout Resolver | **Compass** | Pipeline | Relevance→area, role→zone, cost→size | TYPES ONLY |
| 4 | Algebra-UI Token Engine | **Mint** | Pipeline | Seeds→tokens, 7 domains, OKLCH calc | DONE (CSS) |
| 5 | Coherence & Restriction Engine | **Sieve** | Pipeline | Must/should/prefer rules, beauty regions | NOT BUILT |
| 6 | Spatial Allocation Engine | **Cartographer** | Pipeline | Sort, group, allocate, adjacency | NOT BUILT |
| 7 | Two-Way Interaction Layer | **Synapse** | Pipeline | Controls, mutations, confirm, toast | PARTIAL |
| 8 | Framework Adapter | **Prism** | Pipeline | React adapter, view primitives | DONE (React only) |
| 9 | Degradation & Recovery | **Immune** | Support | Freeze-on-failure, domain isolation | NOT BUILT |
| 10 | Budget & Timing Tracker | **Pulse** | Support | ms/stage, RAM, auto-throttle | NOT BUILT |
| 11 | Agent Interface | **Dial** | Support | GET/SET params, MCP, audit log | NOT BUILT |
| 12 | Seed Set Manager | **Mood** | Support | Theme presets, auto-detect, <5ms switch | PARTIAL (CSS) |
| 13 | Change Propagation | **Ripple** | Support | Events, debounce, priority | NOT BUILT |
| 14 | Live Parameter Cache | **Register** | Support | State, snapshots, diffs, reactive | NOT BUILT |

**8 pipeline + 6 support = 14 components total.**
**4 built (Scrolls partial, Mint, Synapse partial, Prism). 10 to build.**

---

*Registry created: 2026-03-16 | Nickname convention: evocative single-word names that describe function*
