# UI Architecture Session Summary

> Compact reference for continuing UI layout work.
> Updated: 2026-01-20

---

## Completed Tasks (5/5)

| # | Task | Confidence | Status |
|---|------|------------|--------|
| 1 | Remove star field | 98% | DONE |
| 2 | De-glamorize colors | 95% | DONE |
| 3 | Floating control bar | 92% | DONE |
| 4 | Vertical section resize | 85% | DONE |
| 5 | Horizontal sidebar resize | 80% | DONE |

**Files modified:**
- `modules/stars.js` → archived to `archive/removed_features/`
- `theme.tokens.json` → muted accents, shadows, edge colors
- `control-bar.js` → floating centered, muted inline styles
- `template.html` → resize handles, CSS variables, de-glamorized vars
- `sidebar.js` → `initSectionResize()`, `initSidebarResize()`
- `visualize_graph_webgl.py` → removed stars from MODULE_ORDER

---

## Next Phase: Layout Engine (Not Started)

**Goal:** Foundational spatial intelligence - every component registered, constraint-based, collision-aware.

### Core Concept

```
Current (implicit):     CSS vars → implicit cascade → hope it works
Target (explicit):      Register → Constrain → Measure → Solve → Apply
```

### Phase 1 Tasks

| Task | Description |
|------|-------------|
| Create `modules/layout.js` | Registration, pipeline, cached bounds |
| Register all components | header, sidebars, graph, control-bar, toast |
| Add ResizeObserver | Track size changes without reflow |
| Implement collision | Toast stacks above control bar |
| Add min-width validator | Graph never < 320px |
| Debug overlay | `Ctrl+Shift+L` shows bounding boxes |

### Component Registry Model

```javascript
Layout.register({
  id: 'left-sidebar',
  kind: 'dock',           // dock | overlay | floating | tooltip
  layer: 100,             // z-index intention
  size: { width: { min: 200, preferred: 280, max: 400 } },
  affects: ['3d-graph'],  // explicit dependencies
  persist: 'localStorage:viz_sidebar_widths'
});
```

### Constraint Model

```javascript
Layout.constrain([
  { subject: '3d-graph.left', equals: 'left-sidebar.right' },
  { subject: '3d-graph.right', equals: 'right-sidebar.left' },
  { subject: '3d-graph.width', greaterThan: 320, priority: 'required' }
]);
```

---

## Key Architecture Decisions

1. **No Cassowary in Phase 1** - Simple greedy solver, add complexity later if needed
2. **Vanilla JS only** - No React/Vue, follows existing module pattern
3. **CSS variables remain** - Layout engine sets them, not replaces them
4. **localStorage integration** - Persistence is built-in, not bolt-on
5. **Token-based spacing** - All values from semantic tokens

---

## Reference Files

| Purpose | Path |
|---------|------|
| Full architecture spec | `docs/specs/UI_LAYOUT_ARCHITECTURE.md` |
| UI refactor vision | `docs/specs/UI_REFACTOR_VISION.md` |
| ChatGPT implementation prompt | `~/.gemini/.../chatgpt-ui-tips.md` |
| Current sidebar logic | `modules/sidebar.js` |
| Current control bar | `modules/control-bar.js` |
| Template + inline CSS | `template.html` |
| Theme tokens | `schema/viz/tokens/theme.tokens.json` |

---

## Acceptance Criteria (Phase 1)

- [ ] No overlap between toast and control bar
- [ ] Graph width never < 320px
- [ ] No jank during resize (batched DOM writes)
- [ ] Sidebar/section persistence still works
- [ ] All relationships in Layout registry, not just CSS cascade
