# Collider Visualization — UI Refactor Brief

## Your Role

You are refactoring the Collider visualization UI. Collider is a code-as-physics analysis tool that produces a 3D force-directed graph of code atoms (functions, classes, modules) with 48 properties per node. The visualization is a single standalone HTML file with an embedded Vite-bundled JS/CSS application running THREE.js + 3d-force-graph.

The UI is currently broken — panels overlap, critical DOM elements are missing, and the layout uses conflicting absolute positioning from multiple eras of development. Your job is to audit the full codebase, understand every module's DOM expectations, and deliver a clean double-sidebar + dock layout.

---

## Architecture

**Build pipeline:**
```
Python Collider → JSON payload → visualize_graph_webgl.py → standalone.html
                                  ↓
                        Injects: Vite bundle (JS + CSS) + compressed payload
```

**Key paths (all relative to `particle/src/core/viz/`):**

| File | Role |
|------|------|
| `templates/standalone.html` | The DOM template. All HUD elements live here. |
| `build/src/styles.css` | 5500+ lines of CSS. Tokens, panels, zones, components. |
| `build/src/main.js` | Import chain — 20 phases, ~71 ESM modules bundled into single IIFE |
| `build/src/modules/` | All JS modules (see inventory below) |
| `build/vite.config.js` | Vite build config |

**Build command:** `cd particle/src/core/viz/build && npx vite build`
**Generate HTML:** `cd particle && .venv/bin/python tools/visualize_graph_webgl.py /tmp/test-output/ast_lod2_standard.json /tmp/collider-test.html`
**Run pipeline:** `cd particle && ./collider full ~/PROJECTS_all/PROJECT_ytpipe --output /tmp/test-output`

---

## Module Inventory — DOM Dependencies

Audit EVERY module. Each module expects certain DOM elements to exist. Many reference ghost elements that were never created. This is the root cause of silent failures.

### Critical modules to read first:

| Module | What it does | DOM elements it expects |
|--------|-------------|------------------------|
| `selection.js` | Node selection, selection panel, Node Intel Card | `#selection-panel`, `#selection-body`, `#selection-title`, `#selection-clear`, `#selection-box`, `#selection-modal-overlay` |
| `node-intel.js` | Rich 6-section intelligence card for single nodes | Renders INTO `#selection-body` container |
| `hover.js` | Node hover interaction, file panel | `#hover-panel`, `#hover-placeholder`, `#hover-name`, `#hover-type`, `#hover-file`, `#hover-tier`, `#hover-ring`, `#hover-family`, `#hover-complexity`, `#hover-loc`, `#hover-fanin`, `#hover-fanout`, `#hover-role`, `#hover-code`, `#file-panel`, `#file-name`, `#file-cohesion`, `#file-purpose`, `#file-atom-count`, `#file-lines`, `#file-classes`, `#file-functions`, `#file-code` |
| `sidebar.js` | Legacy sidebar controls, has DUPLICATE `updateSelectionPanel()` | `#hover-panel`, `#selection-panel`, `#selection-title`, `#selection-list`, `#selection-clear`, `#left-resize-handle`, `#right-resize-handle` |
| `layout.js` | Panel collision engine — FIGHTS with CSS grid | `#hover-panel`, `#selection-panel`, `#file-panel`, `#toast`, `#hud-toast`, `#left-sidebar`, `#right-sidebar` |
| `hud.js` | Stats bar, health gauge, incoherence breakdown | `#stat-nodes`, `#stat-edges`, `#stat-entropy`, `#stat-health`, `#stat-health-wrap` |
| `syndromes.js` | Syndrome dashboard (Dx button) | Dynamically creates panel, appends to `#zone-left-float` (recently changed from `#hud`) |
| `temporal.js` | Temporal overlay (Time button) | Same — appends to `#zone-left-float` |
| `encoding-view.js` | Color encoding views + size/opacity channels | `#dock-encoding-view`, encoding signature panel |
| `right-intel.js` | Right sidebar overview (recently created) | `#right-overview`, `#right-overview-body` |
| `main-module.js` | Init orchestrator — calls init() on all modules | N/A (calls other modules) |
| `holarchy.js` | Alternative holarchy tree view | Creates its own DOM, inserts into graph container |
| `panels.js` | Panel system foundation | Various panel IDs |
| `panel-handlers.js` | Button bindings, chip creation | Dock button IDs, filter containers |
| `tooltips.js` | Topology tooltip | `#topo-tooltip`, `#tooltip-icon`, `#tooltip-title`, `#tooltip-subtitle`, `#tooltip-body`, `#tooltip-theory`, `#tooltip-examples` |

### Ghost elements (referenced by JS but NEVER created in standalone.html):

- `#hover-panel` + all `#hover-*` children — **hover.js and sidebar.js reference these but they don't exist**
- `#file-panel` + all `#file-*` children — **hover.js references these but they don't exist**
- `#selection-modal-overlay` — **selection.js builds this dynamically, check if it works**
- `#selection-list` — **sidebar.js expects this, but selection-body is what exists**
- `#left-sidebar`, `#right-sidebar` — **layout.js validateGraphWidth() references these**
- `#left-resize-handle`, `#right-resize-handle` — **sidebar.js resize handlers**

---

## Current State & Problems

### What was recently done (partially working):
1. `standalone.html` was restructured with zone wrappers: `zone-top`, `zone-left`, `zone-right`, `zone-left-float`, `zone-bottom`
2. `#hud` now has `display: grid` with `grid-template-areas`
3. `#selection-panel` was created (was missing entirely — Node Intel Card was dead)
4. `#right-overview` was created with dataset intelligence summary
5. layout.js reflow() was modified to skip selection-panel repositioning
6. syndromes.js and temporal.js inject into `#zone-left-float` instead of `#hud`

### What's still broken:
1. **Visual quality is poor** — the sidebars don't look like proper product sidebars (VS Code, Blender, Grafana quality)
2. **The hover panel doesn't exist** — hovering over nodes shows nothing in the right rail
3. **The file panel doesn't exist** — no file context on hover
4. **The bottom dock buttons are cryptic** — "Tier", "Family", "Ring", "Dx", "Time" mean nothing without context
5. **layout.js reflow() still runs** for hover-panel and file-panel (dead code since elements don't exist)
6. **sidebar.js has duplicate functions** that conflict with selection.js
7. **The side-dock (left sidebar) handle/pin UI is vestigial** — if always-open, the handle row is useless
8. **No encoding legend** — when you pick a color mode, there's no legend showing what colors mean
9. **Glass/blur hierarchy is inconsistent** — no clear depth layering between zones

---

## Target Layout: Double Sidebar + Dock

```
┌──────────────────────────────────────────────────────────────┐
│                      TOP BAR                                 │
│  COLLIDER v2.3  ytpipe  2026-03-04    Nodes 597  Edges 1778 │
│                                       Entropy 3.21  H 7.4   │
├────────────┬─────────────────────────────┬───────────────────┤
│            │                             │                   │
│  LEFT      │                             │  RIGHT            │
│  SIDEBAR   │       3D CANVAS             │  SIDEBAR          │
│            │                             │                   │
│ Appearance │    (force graph fills       │ Default: overview │
│  - sliders │     all remaining space)    │  - architecture   │
│ Physics    │                             │  - health bars    │
│  - presets │                             │  - syndromes      │
│ Filters    │                             │  - incoherence    │
│  - search  │                             │                   │
│            │                             │ On click: intel   │
│ [legend]   │                             │  - identity       │
│            │                             │  - metrics        │
│            │                             │  - DNA bars       │
│            │                             │  - topology       │
│            │                             │                   │
├────────────┴─────────────────────────────┴───────────────────┤
│                      BOTTOM DOCK                             │
│  [Atoms|Files]  [Tier|Family|Layer|Ring|File|Flow]  [Dx|Time]│
│                     encoding signature                       │
└──────────────────────────────────────────────────────────────┘
```

**Zone rules:**
- Left sidebar: 220px, always visible, collapsible sections
- Right sidebar: 340px, always visible, shows overview or selection detail
- Canvas: fills remaining space (`1fr`)
- Bottom dock: centered, compact
- No panel uses `position: absolute` or `position: fixed` (CSS grid handles placement)
- Z-index: Canvas=0, HUD zones=100, Floats=200, Modal=9999

---

## What You Must Do

### Phase 1: Full Audit
1. Read EVERY file in `build/src/modules/` (there are ~30+ modules)
2. Map every `document.getElementById()` and `document.querySelector()` call
3. Identify which DOM elements exist vs don't exist
4. Identify duplicate functions (sidebar.js vs selection.js, etc.)
5. Map the event flow: what calls what, what triggers reflow

### Phase 2: DOM Reconciliation
1. Create ALL missing DOM elements that active JS code depends on
2. Decide which ghost elements should be created vs which JS code should be removed
3. For `#hover-panel` + children: CREATE them in the right sidebar (below selection panel, or as a hover tooltip)
4. For `#file-panel` + children: CREATE them or route file info into the right sidebar
5. Remove `#selection-list` references from sidebar.js (dead code, selection.js uses `#selection-body`)
6. Remove or disable layout.js reflow() for panels now in CSS grid zones

### Phase 3: Clean Layout
1. Make the CSS grid layout actually work visually as a double sidebar + dock
2. Both sidebars should have glassmorphic backgrounds with proper depth hierarchy
3. Left sidebar: always open, no hover-to-reveal, remove handle/pin row
4. Right sidebar: always shows content (overview or selection detail)
5. Bottom dock: properly centered in its grid zone
6. Clean up all absolute/fixed positioning remnants
7. Ensure `pointer-events: none` on the grid, `pointer-events: auto` on interactive zones

### Phase 4: Information Surfacing
1. The right sidebar overview should show: dataset stats, architecture breakdown (tier/family/ring distributions as bars), incoherence gauge (5 bars), top syndromes, health score
2. Clicking a node should switch the right sidebar to the Node Intel Card (48 properties in 6 collapsible sections)
3. The bottom dock buttons should have better UX — either tooltips with descriptions or an encoding legend in the left sidebar
4. Hovering a node should show a compact tooltip (not a full panel) near the cursor

### Phase 5: Cleanup
1. Remove dead CSS rules for elements that no longer exist
2. Remove duplicate function definitions
3. Remove layout.js panel collision code for grid-managed panels
4. Ensure no inline `style.left/top/right/bottom` is set on grid-managed panels

---

## Design Tokens

The CSS uses a token system. Key tokens:

```css
--color-bg-base       /* darkest background */
--color-bg-surface    /* panel backgrounds */
--color-bg-elevated   /* raised elements */
--color-border-strong /* visible borders */
--color-border-subtle /* subtle separators */
--color-text-primary  /* main text */
--color-text-secondary /* labels */
--color-text-muted    /* hints */
--surface-blur        /* backdrop blur amount */
--offset-panel-margin /* standard margin */
--spacing-1 through --spacing-10 /* spacing scale */
--radius-sm, --radius-lg /* border radii */
--z-index-docked, --z-index-sticky, --z-index-panel, --z-index-modal /* z layers */
```

Use these tokens. Do not hardcode colors or sizes.

---

## Glassmorphic Depth Hierarchy

| Zone | Blur | Opacity | Shadow | Purpose |
|------|------|---------|--------|---------|
| Canvas (Z5) | none | 100% | none | The background IS the 3D graph |
| Top bar (Z1) | blur(12px) | 85% | subtle | Scannable stats |
| Sidebars (Z2, Z3) | blur(16px) | 90% | medium | Persistent panels |
| Float panels (Z4) | blur(20px) | 95% | heavy | On-demand intelligence |
| Modal (Z9) | blur(24px) | 100% | heaviest | Full overlay |

---

## Verification Checklist

After refactoring, verify:

- [ ] `npx vite build` — clean (no errors, warnings OK for `#3d-graph`)
- [ ] `pytest tests/test_color_encoding.py -q` — 106 tests pass
- [ ] Left sidebar visible on load with all sections
- [ ] Right sidebar shows intelligence overview on load
- [ ] Click node → right sidebar shows Node Intel Card with all 6 sections
- [ ] Click "Clear" or empty space → right sidebar returns to overview
- [ ] Hover node → tooltip appears near cursor
- [ ] Bottom dock buttons all functional
- [ ] Dx button → syndrome panel in left-float zone
- [ ] Time button → temporal panel stacks in left-float zone
- [ ] No panels overlap at any viewport size
- [ ] Health stat clickable → incoherence breakdown expands
- [ ] Console has no errors (silent failures from missing DOM elements)
- [ ] Encoding views change node colors, sizes, opacity
