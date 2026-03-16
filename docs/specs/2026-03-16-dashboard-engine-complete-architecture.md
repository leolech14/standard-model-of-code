# Dashboard Engine: Complete End-to-End Architecture

> The system that reads semantic files, resolves constraints, and produces a fully parametric, anti-fragile, dual-audience (human + AI) control panel in real-time.
>
> Born: 2026-03-16. Living system. Will evolve.

---

## Core Principle

**Semantic files are the code.** They are not documentation. They are not configuration. They ARE the application — context providers that the Dashboard Engine reads, interprets, and renders in real-time. Change a semantic file → the UI changes. An agent edits a parameter → the human sees it immediately.

Nothing is a fixed point. Everything is becoming. The purpose field captures WHAT something is striving to become, not just what it is now.

---

## End-to-End Data Flow

```
SEMANTIC FILES (on disk, the source of truth)
    │
    │  read by
    ▼
DASHBOARD ENGINE (the central coordinator)
    │
    ├── PURPOSE INTERPRETER
    │   Reads: why each file exists, what it's striving to become
    │   Produces: relevance scores, narrative roles, attention costs
    │
    ├── TOKEN RESOLVER
    │   Reads: seeds + coefficients (Algebra-UI)
    │   Produces: all derived visual values via calc()
    │
    ├── CONSTRAINT VALIDATOR
    │   Reads: resolved tokens + purpose + framework params
    │   Produces: validated values (or auto-corrections)
    │   Enforces: beauty regions, contrast, coherence
    │
    ├── LAYOUT COMPOSER
    │   Reads: validated values + narrative roles + adjacency rules
    │   Produces: spatial allocation (what goes where, how big)
    │
    ├── CONTROL BINDER
    │   Reads: mutations + parameters from semantic files
    │   Produces: two-way bindings (display + controls)
    │
    └── RENDERER
        Reads: composed layout + resolved styles + bound controls
        Produces: pixels on screen (React, Vanilla, Svelte — interchangeable)
            │
            ▼
        USER sees + interacts
        AI reads + modifies parameters
```

### Performance Flow

```
Semantic files read         ~5ms   (filesystem, cached after first read)
Purpose interpretation      ~1ms   (pure computation from fields)
Token resolution           ~2ms   (CSS calc(), browser-native)
Constraint validation      ~3ms   (linear constraint check, no solver needed for V1)
Layout composition         ~2ms   (sort + group + allocate)
Control binding            ~1ms   (map mutations to handlers)
Render                    ~10ms   (React reconciliation / DOM update)
                         ─────
TOTAL BUDGET              <25ms   (40fps capable, no jank)
```

If any stage exceeds its budget, it **freezes its last good output** and continues with stale-but-coherent values. The cascade doesn't break — it degrades gracefully.

---

## Component Map

### 1. SEMANTIC FILES (Source of Truth)

Files on disk. Read by the engine. Written by humans or AI agents.

```yaml
# Example: a semantic file for the journal domain
# Location: ~/.devjournal/semantic/journal.yaml (or .json, or .ts)

page:
  id: journal
  mission: "Track development activity to identify patterns and focus effort"
  audience: developer-owner
  cadence: daily-review
  success_criteria:
    - "Identify which projects got most effort"
    - "Spot breakthroughs"
    - "Detect concerns"
    - "See the shape of the day"

nodes:
  - id: journal.velocity
    purpose:
      answers: "How productive was this day?"
      becoming: "A real-time development intensity gauge with trend prediction"
      relevance: 0.95
      attention_cost: glance
      narrative_role: anchor
    sense:
      source: local
      endpoint: journal
      field_path: data.velocity
      interval_ms: 0
    controls:
      - id: rerun-pipeline
        label: "Refresh"
        action: "POST /api/v1/journal/rerun"
        confirm: false
    context:
      requires_nearby: [journal.timeline]
      enables: [journal.highlights]
    tags: [velocity, anchor, core-metric]
```

**Key fields:**
- `purpose.answers` — the question this resolves for the user
- `purpose.becoming` — what it's evolving toward (developmental direction)
- `controls` — two-way: not just display, but actions the user can take
- `context` — adjacency requirements (what needs to be nearby to make sense)
- Everything tagged for AI discoverability

### 2. DASHBOARD ENGINE (Central Coordinator)

The single component that reads all semantic files and coordinates the entire rendering pipeline.

```
DashboardEngine {
  // State
  semanticFiles: Map<string, SemanticFile>     // loaded from disk
  resolvedTokens: Map<string, ResolvedValue>   // from Algebra-UI
  constraints: Constraint[]                     // coherence rules
  frameworkParams: FrameworkAdapter             // Tailwind | Vanilla | etc.
  performanceBudget: BudgetConfig              // ms + RAM limits per stage

  // Pipeline (runs on semantic file change OR parameter change)
  run(trigger: 'file-change' | 'param-change' | 'resize' | 'theme-switch') {
    1. readSemanticFiles()         // FS read, cached, diff-based
    2. interpretPurpose()          // extract relevance, roles, costs
    3. resolveTokens()             // seeds + coefficients → values
    4. validateConstraints()       // check beauty regions, auto-correct
    5. composeLayout()             // purpose → spatial allocation
    6. bindControls()              // mutations → UI handlers
    7. render()                    // framework adapter → pixels
  }

  // Anti-fragility
  onStageFailure(stage: string, error: Error) {
    freezeStageOutput(stage)       // keep last good values
    logDegradation(stage, error)   // visible in engine status
    continueWithFrozen()           // other stages proceed normally
  }
}
```

### 3. PURPOSE INTERPRETER

Reads the `purpose` field from every node and produces rendering instructions.

```
INPUT:  purpose.relevance = 0.95, narrative_role = 'anchor', attention_cost = 'glance'

OUTPUT:
  - area_allocation: 0.30 of viewport (derived from relevance)
  - position: top of page (derived from narrative_role = anchor)
  - view_size: compact (derived from attention_cost = glance)
  - salience: high (derived from relevance > 0.8)
  - order: 1 (derived from relevance rank among siblings)
```

The mapping is deterministic:

| Relevance | Area | Salience |
|-----------|------|----------|
| 0.9-1.0   | 25-35% | high |
| 0.7-0.9   | 15-25% | high |
| 0.5-0.7   | 10-15% | normal |
| 0.3-0.5   | 5-10% | normal |
| 0.0-0.3   | 2-5% | low |

| Role | Position |
|------|----------|
| anchor | top, always visible, prominent |
| detail | below anchors, grid or full-width |
| evidence | scrollable zone, collapsible |
| action | contextual (near target) or footer |

| Attention Cost | View Size | Interaction Depth |
|---------------|-----------|-------------------|
| glance | stat card, badge, gauge | instant (0s) |
| scan | table, bar chart, small list | quick (2-5s) |
| study | feed, timeline, detailed view | deliberate (10-30s) |
| analyze | full page, modal, drill-down | deep (1-5min) |

### 4. TOKEN RESOLVER

Algebra-UI extended. Currently in `globals.css`, will also resolve in JS for the constraint engine.

```
INPUTS:
  seeds:        { bg-l: 0.145, emerald-h: 162, space-unit: 0.25rem, ... }
  coefficients: { coeff-hover-l: 0.05, density: 1, shadow-strength: 1, ... }

PROCESS:
  For each derived token:
    value = calc(seed, coefficient, formula)

  color-surface    = oklch(bg-l + coeff-surface-l, 0, 0)
  color-hover      = oklch(bg-l + coeff-hover-l, 0, 0)
  gap-sm           = space-unit * 2 * density
  shadow-sm        = 0 2px 8px oklch(0 0 0 / 0.12 * shadow-strength)

OUTPUT:
  Map<token-name, resolved-value>
  (every token is now a concrete CSS value)
```

### 5. CONSTRAINT VALIDATOR

The rules engine that prevents incoherent UI. Operates on resolved tokens.

```
INPUTS:
  resolved_tokens: Map<string, value>
  purpose_instructions: { area_allocations, positions, sizes }
  framework_params: { valid_spacing_values, valid_radii, ... }

PROCESS:
  For each constraint in constraints[]:
    result = evaluate(constraint.rule, resolved_tokens)
    if result == VIOLATION:
      if constraint.type == 'must':   → REFUSE (log error, use fallback)
      if constraint.type == 'should': → AUTO-CORRECT (nudge to nearest legal)
      if constraint.type == 'prefer': → WARN (render but flag)

OUTPUT:
  validated_tokens: Map<string, value>  (safe to render)
  corrections: Correction[]            (what was auto-fixed)
  warnings: Warning[]                  (soft violations)
  errors: Error[]                      (hard violations)
```

**Beauty Regions** (from vector-ui research):

The constraint engine knows the "safe zones" where OKLCH values produce beautiful, accessible, coherent UI. These were discovered empirically from 513K Android UIs:
- Lightness corridors where contrast works
- Chroma ranges where colors aren't garish
- Hue relationships that harmonize
- Spacing ratios that feel balanced

Values inside beauty regions → render. Values outside → nudge back in.

### 6. LAYOUT COMPOSER

Turns purpose instructions + validated tokens into spatial allocation.

```
INPUTS:
  nodes: NodeDefinition[] (with purpose.narrativeRole + relevance)
  validated_tokens: Map<string, value>
  viewport: { width, height }
  context_rules: { requiresNearby, contrastsWith }

PROCESS:
  1. SORT nodes by relevance (descending)
  2. GROUP by narrative role:
       anchors[]   → allocate top zone
       details[]   → allocate middle zone
       evidence[]  → allocate bottom zone
       actions[]   → attach to their targets
  3. WITHIN groups, respect adjacency:
       if A.requiresNearby includes B → place adjacent
       if A.contrastsWith includes C → place side-by-side
  4. ALLOCATE area proportional to relevance
  5. SIZE views by attentionCost

OUTPUT:
  layout: LayoutInstruction[]
  Each: { nodeId, zone, x, y, width, height, viewType }
```

### 7. CONTROL BINDER

Makes the UI two-way: not just display, but interactive controls.

```
INPUTS:
  nodes: NodeDefinition[] (with mutations[] and controls[])

PROCESS:
  For each node with controls:
    Create handler binding:
      control.action → API endpoint
      control.confirm → show modal if true
      control.feedback → toast on success/failure

OUTPUT:
  bindings: Map<nodeId, ControlBinding[]>
  Each binding: { triggerId, handler, confirmText, feedbackType }
```

This is what makes it a CONTROL PANEL, not just a dashboard. Every semantic file can declare:
- What to SHOW (sense)
- What to DO (controls/mutations)
- WHY it matters (purpose)

### 8. RENDERER (Framework-Agnostic)

Consumes the composed layout + resolved styles + bound controls. Produces pixels.

```
INPUTS:
  layout: LayoutInstruction[]       (what goes where)
  styles: Map<string, value>        (how it looks)
  bindings: Map<nodeId, Control[]>  (what it does)
  data: Map<nodeId, unknown>        (current values from polling)

CONTRACT:
  interface RenderAdapter {
    mount(container: Element): void
    update(nodeId: string, data: unknown): void
    destroy(): void
  }

IMPLEMENTATIONS:
  ReactTailwindAdapter  → current (what exists)
  VanillaAdapter        → future (proves framework-agnosticism)
  TerminalAdapter       → future (CLI dashboard for SSH access)
```

---

## Anti-Fragility Design

### Failure Isolation

Each pipeline stage is independent. If one fails, others continue with frozen values:

```
Token resolver fails → use last resolved tokens (CSS variables persist)
Constraint check fails → render unchecked (warn in status bar)
Layout composer fails → use last layout (positions don't change)
Control binder fails → display-only mode (controls disabled, data still shows)
Renderer fails → show last frame (nothing worse than a freeze)
```

### Performance Budgets

```yaml
budgets:
  semantic_read:    5ms    # FS read (cached after first)
  purpose_interpret: 1ms   # Pure computation
  token_resolve:    2ms    # CSS calc native
  constraint_check: 3ms    # Linear scan
  layout_compose:   2ms    # Sort + allocate
  control_bind:     1ms    # Map handlers
  render:          10ms    # DOM update
  total:           25ms    # 40fps target

  ram:
    semantic_cache:  1MB   # All semantic files in memory
    token_cache:     50KB  # All resolved values
    layout_cache:    10KB  # Spatial instructions
    render_state:    5MB   # React/DOM state
    total:           7MB   # Budget for the engine
```

If a stage exceeds its budget:
1. First: optimize (memoize, skip unchanged)
2. Second: reduce scope (render fewer nodes)
3. Third: freeze and skip (stale but coherent)

### Token Independence

Each token domain is independent:

```
COLOR tokens fail  → spacing, typography, layout still work (render with fallback colors)
SPACING tokens fail → colors, typography still work (render with default spacing)
PURPOSE fails      → tokens still work (render with manual order, no auto-layout)
```

No single failure cascades to total failure. The UI degrades gracefully into less-parametric but still-functional rendering.

---

## Dual Audience: Human + AI

### For the Human (Primary)
- Visual: charts, colors, spatial hierarchy, interactive controls
- Purpose-driven: the most relevant information is most prominent
- Anti-fragile: never shows a blank screen, always shows something coherent

### For the AI (Secondary but Essential)
- Semantic files are machine-readable (YAML/JSON)
- Every node has `purpose.answers` — the AI knows WHAT each widget means
- Every control has `action` — the AI can trigger mutations programmatically
- The engine state is queryable — AI can ask "what is journal.velocity currently showing?"
- Parameters are writable — AI can change seeds, coefficients, or purpose.relevance in real-time

### Human-AI Collaboration Pattern

```
1. Human says: "The timeline feels too big"
2. AI reads: journal.timeline.purpose.relevance = 0.85
3. AI adjusts: journal.timeline.purpose.relevance = 0.65
4. Engine re-runs: timeline shrinks (lower relevance → less area)
5. Human sees: smaller timeline, more space for projects
6. No code changed. Just a parameter in a semantic file.
```

---

## What Exists vs What Needs Building

| Component | Status | Location |
|-----------|--------|----------|
| Semantic file format | PARTIAL — types exist, YAML format designed but not read from files | `lib/nodes/types.ts`, `lib/nodes/registry/*.ts` |
| Purpose interpreter | TYPES EXIST, logic NOT wired | `PurposeDefinition` in types.ts, SemanticPage doesn't read it |
| Token resolver | DONE (CSS) | `app/globals.css` (644 lines) |
| Token resolver (JS) | NOT BUILT | Need JS-side access to resolved values for constraint engine |
| Constraint validator | NOT BUILT | Need constraints schema + validation engine |
| Layout composer | NOT BUILT | SemanticPage uses hardcoded groups, not purpose-derived layout |
| Control binder | PARTIAL | useMutation exists, but not driven by semantic file controls |
| Renderer (React) | DONE | SemanticPage + NodeRenderer + views/ |
| Renderer (Vanilla) | NOT BUILT | Would prove framework-agnosticism |
| Anti-fragility | NOT BUILT | No freeze-on-failure, no budget monitoring |
| AI parameter API | NOT BUILT | No endpoint for AI to read/write parameters |
| Dashboard Engine coordinator | NOT BUILT | Pipeline stages exist independently, no orchestrator |

### Build Order

1. **Dashboard Engine shell** — the coordinator that runs the pipeline
2. **Semantic file reader** — read YAML/JSON from disk, not compiled TypeScript
3. **Purpose → layout wiring** — make SemanticPage derive layout from purpose
4. **Constraint schema** — define initial rules (color, spacing, composition)
5. **Constraint validator** — check rules, auto-correct violations
6. **Anti-fragility** — freeze-on-failure, budget monitoring
7. **AI parameter API** — endpoint for agents to read/write semantic parameters
8. **Second renderer** — vanilla HTML to prove framework-agnosticism

---

## The Vision in One Sentence

The Dashboard Engine reads semantic files that declare purpose + data + controls, resolves all visual values through constraints that guarantee coherence, and renders a fully parametric control panel that humans see and AI agents can modify in real-time — with no hardcoded UI, only hardcoded logic about what makes good UI.

---

*Architecture spec: 2026-03-16 | Converges: Algebra-UI + Semantic Nodes + Purpose-Driven + Constraint Engine + Framework-Agnostic Rendering*
*Lineage: PROJECT_vector-ui (research) → Refinery Platform (production) → Dashboard Engine (vision)*
