# Parametric UI Engine Architecture

> The system that hardcodes LOGIC (how to make good UI), not VALUES (what the UI looks like).
> Zero hardcoded UI. 100% variable-driven. Framework-agnostic. Constraint-validated.

---

## The Problem

Current UI systems conflate four concerns:
1. **What values exist** (design tokens) — solved by Algebra-UI
2. **What values are allowed** (constraints) — NOT solved anywhere
3. **Why a value was chosen** (purpose) — NOT solved anywhere
4. **How values are rendered** (framework) — hardcoded to React/Tailwind

Every UI framework (React, Vue, Svelte, Tailwind, vanilla CSS) hardcodes layout decisions as imperative code. You can theme colors, but you can't theme the logic that decides "this element goes here at this size because of its purpose."

## The Architecture: Four Layers

```
┌─────────────────────────────────────────────┐
│  LAYER 1: SEMANTIC DEFINITIONS              │  ← What exists and why
│  (NodeDefinition + PurposeDefinition)       │
│  Framework-agnostic. Pure data.             │
├─────────────────────────────────────────────┤
│  LAYER 2: TOKEN SYSTEM                      │  ← What values are possible
│  (Seeds + Coefficients + Computed Tokens)   │
│  Algebra-UI. CSS calc(). OKLCH.             │
├─────────────────────────────────────────────┤
│  LAYER 3: CONSTRAINT ENGINE                 │  ← What combinations are legal
│  (Restrictions + Coherence Rules)           │
│  Prevents impossible/ugly/inaccessible UI.  │
├─────────────────────────────────────────────┤
│  LAYER 4: RENDERER                          │  ← How to draw it
│  (React | Svelte | Vue | Vanilla | Terminal)│
│  Interchangeable. Consumes resolved values. │
└─────────────────────────────────────────────┘
```

**Data flows DOWN. Each layer produces input for the next.**

---

## Layer 1: Semantic Definitions (EXISTS — types.ts)

Pure data describing WHAT exists and WHY.

```typescript
// Already built:
PurposeDefinition {
  answers: string        // "How productive was this day?"
  relevance: number      // 0-1 (drives sizing, ordering)
  attentionCost: 'glance' | 'scan' | 'study' | 'analyze'
  narrativeRole: 'anchor' | 'detail' | 'evidence' | 'action'
}

PageDefinition {
  mission: string
  successCriteria: string[]
}

// These are the INPUTS to the constraint engine.
// They carry intent, not pixels.
```

## Layer 2: Token System (EXISTS — globals.css)

Seeds + coefficients → all visual values.

```
Seeds (genotype):
  --bg-l: 0.145          ← background lightness
  --emerald-h: 162       ← accent hue
  --space-unit: 0.25rem  ← spatial atom
  --radius-seed: 0.5rem  ← corner atom

Coefficients (transform constants):
  --coeff-hover-l: 0.05  ← hover brightness delta
  --coeff-surface-l: 0.033 ← surface elevation
  --density: 1           ← spacing multiplier

Computed (phenotype):
  --color-surface: oklch(calc(var(--bg-l) + var(--coeff-surface-l)) 0 0)
  --gap-sm: calc(var(--space-unit) * 2 * var(--density))
```

**What's missing:** The token system produces VALUES but doesn't know which values are LEGAL together.

## Layer 3: Constraint Engine (NOT YET BUILT)

This is the core innovation. Rules that prevent incoherent UI.

### Constraint Types

```typescript
interface Constraint {
  id: string;
  domain: 'color' | 'spacing' | 'typography' | 'layout' | 'composition';
  type: 'must' | 'should' | 'prefer';  // hard vs soft constraints
  rule: ConstraintRule;
  reason: string;  // WHY this constraint exists
}

// Color coherence
{ id: 'contrast-min', domain: 'color', type: 'must',
  rule: { fn: 'contrast_ratio', args: ['text-color', 'bg-color'], op: '>=', value: 4.5 },
  reason: 'WCAG AA accessibility' }

// Spacing coherence
{ id: 'density-bounds', domain: 'spacing', type: 'must',
  rule: { fn: 'range', args: ['--density'], min: 0.5, max: 2.0 },
  reason: 'Below 0.5 elements overlap, above 2.0 screen wastes space' }

// Layout coherence (from purpose)
{ id: 'anchor-prominence', domain: 'layout', type: 'should',
  rule: { fn: 'min_area_ratio', args: ['anchor-nodes', 'total-viewport'], value: 0.25 },
  reason: 'Anchors must be prominent — they answer the page mission' }

// Composition coherence
{ id: 'adjacent-contrast', domain: 'composition', type: 'prefer',
  rule: { fn: 'sibling_lightness_delta', args: ['adjacent-surfaces'], min: 0.02 },
  reason: 'Adjacent surfaces need distinguishable lightness to be perceived as separate' }

// Typography coherence
{ id: 'type-scale-ratio', domain: 'typography', type: 'must',
  rule: { fn: 'ratio', args: ['h1-size', 'body-size'], min: 1.5, max: 3.0 },
  reason: 'Headers must be noticeably larger than body but not comically so' }
```

### How Constraints Work

```
INPUT: seeds + coefficients + semantic definitions
  ↓
RESOLVE: compute all derived values via calc()
  ↓
VALIDATE: check every constraint
  ↓
IF violations:
  - 'must' constraints → REFUSE to render (show error)
  - 'should' constraints → AUTO-CORRECT (nudge value to nearest legal)
  - 'prefer' constraints → WARN (render but flag)
  ↓
OUTPUT: resolved, validated values → ready for any renderer
```

### What This Enables

**Instant theming:** Change `--bg-l: 0.145` to `--bg-l: 0.95` (light theme). The constraint engine automatically:
- Flips `--coeff-hover-l` sign (hover goes darker not lighter)
- Adjusts text colors to maintain contrast ratio ≥ 4.5
- Recalculates shadow strength (lighter bg = softer shadows)
- Validates all combinations are coherent BEFORE rendering

**Real-time feedback signals:** As any seed changes:
- Green: all constraints satisfied
- Yellow: soft constraints violated (auto-corrected)
- Red: hard constraints violated (blocked)

**Dynamic layout from purpose:** When a node's `relevance` changes:
- Constraint engine recalculates area allocation
- Anchors get more space, evidence gets less
- Layout reflows without touching any component code

## Layer 4: Renderer (EXISTS — React/Tailwind, but coupled)

Renderers are CONSUMERS of resolved values. They should NOT make design decisions.

### Framework Abstraction

```typescript
// The renderer contract — framework-agnostic
interface RenderPrimitive {
  type: 'stat' | 'gauge' | 'feed' | 'table' | 'chart' | 'control';
  resolvedStyles: Record<string, string>;  // all CSS values, pre-computed
  data: unknown;
  interactions: InteractionBinding[];
}

// React renderer (one implementation)
function ReactRenderer({ primitive }: { primitive: RenderPrimitive }) {
  return <div style={primitive.resolvedStyles}>{renderContent(primitive)}</div>;
}

// Vanilla renderer (another implementation)
function vanillaRenderer(primitive: RenderPrimitive): HTMLElement {
  const el = document.createElement('div');
  Object.assign(el.style, primitive.resolvedStyles);
  el.innerHTML = renderContent(primitive);
  return el;
}

// Svelte, Vue, etc. — same contract, different output
```

### How Frameworks Become Parameter Sources

Each framework defines its own set of available primitives:

```yaml
# Tailwind parameter source
tailwind:
  spacing: [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
  border-radius: [none, sm, md, lg, xl, 2xl, full]
  font-size: [xs, sm, base, lg, xl, 2xl, 3xl, 4xl]
  breakpoints: [sm:640, md:768, lg:1024, xl:1280, 2xl:1536]

# Material UI parameter source
material:
  spacing: [0, 4, 8, 12, 16, 24, 32, 48, 64]
  border-radius: [0, 4, 8, 16, 28]
  elevation: [0, 1, 2, 3, 4, 6, 8, 12, 16, 24]

# Vanilla CSS parameter source
vanilla:
  spacing: continuous  # any value allowed
  border-radius: continuous
  units: [px, rem, em, vw, vh, %]
```

The constraint engine uses these as **valid ranges**. When resolving a spacing value, it snaps to the nearest legal value in the active framework's parameter set. This is how the same semantic definition produces Tailwind classes in one renderer and raw CSS in another.

---

## The Resolution Pipeline

```
1. SEMANTIC LAYER produces:
   { node: 'journal.velocity', purpose: { relevance: 0.95, role: 'anchor', cost: 'glance' } }

2. TOKEN LAYER produces candidate values:
   { fontSize: calc(--text-lg), gap: calc(--space-4), bg: calc(--color-surface), ... }

3. CONSTRAINT ENGINE validates + resolves:
   ✓ contrast(text, bg) = 8.2 (≥ 4.5, PASS)
   ✓ anchor area = 0.30 (≥ 0.25, PASS)
   ~ hover delta = 0.03 (< 0.05 preferred, AUTO-CORRECT to 0.05)

4. FRAMEWORK ADAPTER snaps to target:
   Tailwind: "text-lg p-4 bg-surface" (snapped to Tailwind scale)
   Vanilla:  "font-size: 1.125rem; padding: 1rem; background: oklch(...)"

5. RENDERER draws:
   React: <div className="text-lg p-4 bg-surface">...</div>
   Vanilla: el.style = resolved; el.textContent = data;
```

---

## What Algebra-UI Already Provides (and What's Missing)

| Capability | Algebra-UI Status | Constraint Engine Status |
|-----------|-------------------|------------------------|
| Color derivation (OKLCH calc) | DONE | — |
| Theme switching (seed override) | DONE | — |
| Spacing scale (space-unit × N) | DONE | — |
| Shadow derivation | DONE | — |
| Contrast validation | — | NOT BUILT |
| Adjacent surface coherence | — | NOT BUILT |
| Purpose → size mapping | — | NOT BUILT |
| Relevance → order mapping | — | NOT BUILT |
| Framework parameter snapping | — | NOT BUILT |
| Soft constraint auto-correction | — | NOT BUILT |
| Real-time validation feedback | — | NOT BUILT |

**Algebra-UI is Layer 2. The constraint engine (Layer 3) is the missing piece that makes it fully parametric.**

---

## Implementation Path

### Phase 1: Constraint Schema (define the rules)
Create `constraints.yaml` (or `.ts`) with the constraint definitions. Start with color + spacing.

### Phase 2: Validation Engine (check the rules)
A function that takes resolved tokens + constraints → returns violations + auto-corrections.

### Phase 3: Purpose-to-Layout Resolver (use the rules)
SemanticPage reads `purpose.relevance` + `purpose.narrativeRole` → produces layout instructions via constraints.

### Phase 4: Framework Adapter (abstract the renderer)
Extract rendering primitives from React/Tailwind into a framework-agnostic contract. Second renderer (vanilla HTML) proves the abstraction.

---

## Research References

- [Martin Fowler: Design Token-Based UI Architecture](https://martinfowler.com/articles/design-token-based-ui-architecture.html) — token layers (option → decision → component)
- [Cassowary Constraint Solver](https://en.wikipedia.org/wiki/Cassowary_(software)) — incremental linear constraint solving for UI layout (powers Apple Auto Layout)
- [TokiForge](https://github.com/tokiforge/tokiforge) — framework-agnostic runtime token switching (~3KB)
- [GSS: Constraint CSS](https://gss.github.io/guides/ccss) — constraint-based CSS extensions
- [Theme UI](https://github.com/system-ui/theme-ui) — constraint-based design principles for React
- [Components.ai](https://components.ai/) — parametric generative design exploration
- [Style Dictionary](https://styledictionary.com/) — platform-agnostic design token compiler
- [Generative and Malleable UIs (CHI 2025)](https://dl.acm.org/doi/full/10.1145/3706598.3713285) — task-driven data model for UI generation
- [Normal Flow: Constraint-Based Design Systems](https://normalflow.pub/posts/2022-08-12-an-introduction-to-constraint-based-design-systems)
- [Figma Schema 2025: Design Systems for a New Era](https://www.figma.com/blog/schema-2025-design-systems-recap/)

---

*Spec created: 2026-03-16 | Part of the Algebra-UI + Semantic Node Architecture convergence*
