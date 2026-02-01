# UI Layout Architecture Specification

> Foundational principles for component positioning, sizing, and spatial intelligence.
>
> Status: DRAFT - Architectural Specification
> Created: 2026-01-20

---

## Design Philosophy

**The layout system is not a feature. It is the foundation.**

Every UI component must inherently understand:
1. Where it is (position)
2. How big it is (size)
3. What constrains it (boundaries)
4. What depends on it (relationships)

This is not optional. This is not an add-on. This is how we think about UI.

---

## Core Principles

### Principle 1: Explicit Hierarchy Over Implicit Cascade

**Problem with current approach:**
```css
/* Scattered CSS - implicit relationships */
#left-sidebar { width: 280px; }
#3d-graph { left: var(--sidebar-width); }  /* Implicit dependency */
```

**Required approach:**
```javascript
// Explicit hierarchy - clear relationships
Layout.define('main', {
  type: 'HBox',
  children: [
    { id: 'left-sidebar', width: { min: 200, default: 280, max: 400 } },
    { id: '3d-graph', flex: 1 },  // Takes remaining space
    { id: 'right-sidebar', width: { min: 200, default: 260, max: 400 } }
  ]
});
```

**Why:** When relationships are explicit, the system can reason about them. Changes propagate correctly. Debugging is possible.

---

### Principle 2: Three-Phase Layout Pipeline

Every layout operation follows this universal pattern:

```
PHASE 1: MEASURE
├── Each component reports its size requirements
├── { min, preferred, max } for width and height
├── Bottom-up: leaves to root
└── Cached until invalidated

PHASE 2: SOLVE
├── Given available space, resolve constraints
├── Distribute space according to flex/stretch factors
├── Handle conflicts via priority (REQUIRED > PREFERRED > WEAK)
└── Output: concrete positions and sizes for all components

PHASE 3: APPLY
├── Update DOM/CSS with solved values
├── Batch all changes (single reflow)
├── Trigger dependent systems (e.g., 3D graph resize)
└── Mark as clean
```

**Implementation requirement:** All layout changes MUST go through this pipeline. No direct `element.style.width = ...` outside the system.

---

### Principle 3: Component Identity and Registration

Every UI component must be registered with the layout system:

```javascript
// Component registration (conceptual)
const component = Layout.register({
  id: 'left-sidebar',
  element: document.getElementById('left-sidebar'),

  // Size constraints
  size: {
    width: { min: 200, preferred: 280, max: 400 },
    height: { mode: 'fill-parent' }  // Stretch to container
  },

  // Position constraints
  position: {
    anchor: 'left',       // Attached to left edge of parent
    offset: { x: 0, y: 0 }
  },

  // Relationships
  affects: ['3d-graph'],  // When I resize, these need recalculation
  affectedBy: ['header'], // When header changes, I may need adjustment

  // Behaviors
  resizable: { horizontal: true, vertical: false },
  collapsible: true
});
```

**Why:** Registration creates a manifest of all components. The system knows what exists, what depends on what, and can make intelligent decisions.

---

### Principle 4: Constraint-Based Relationships

Relationships between components are expressed as constraints, not hardcoded values:

```javascript
// Instead of: #3d-graph { left: 280px; }
// Express as constraints:

Layout.constrain([
  // Graph starts where left sidebar ends
  { subject: '3d-graph.left', equals: 'left-sidebar.right' },

  // Graph ends where right sidebar starts
  { subject: '3d-graph.right', equals: 'right-sidebar.left' },

  // Graph fills vertical space below header
  { subject: '3d-graph.top', equals: 'header.bottom' },
  { subject: '3d-graph.bottom', equals: 'viewport.bottom' },

  // Minimum graph size (REQUIRED - cannot be violated)
  { subject: '3d-graph.width', greaterThan: 200, priority: 'required' },
  { subject: '3d-graph.height', greaterThan: 200, priority: 'required' }
]);
```

**Priority levels:**
- `required` - Must be satisfied. Violation is an error.
- `strong` - Strongly preferred. Only violated to satisfy `required`.
- `medium` - Preferred. Default priority.
- `weak` - Nice to have. First to be relaxed.

---

### Principle 5: Dirty Tracking and Incremental Updates

The system tracks which components need recalculation:

```javascript
// Internal state
const dirtyComponents = new Set();

// When something changes
function markDirty(componentId) {
  dirtyComponents.add(componentId);

  // Also mark dependents
  const component = Layout.get(componentId);
  component.affects.forEach(id => dirtyComponents.add(id));
}

// On next frame
function resolveDirty() {
  if (dirtyComponents.size === 0) return;

  // Sort by dependency order (topological sort)
  const ordered = topologicalSort(dirtyComponents);

  // Measure only dirty components
  ordered.forEach(id => measure(id));

  // Solve constraints
  solve();

  // Apply in batch
  applyAll();

  dirtyComponents.clear();
}
```

**Why:** Avoid recalculating the entire layout when one component changes. Only update what's necessary.

---

### Principle 6: Semantic Spacing Tokens

All spacing values come from a token system, never hardcoded:

```javascript
// Token definitions
const SPACING = {
  '0': 0,
  '1': 4,
  '2': 8,
  '3': 12,
  '4': 16,
  '5': 20,
  '6': 24,
  '8': 32,
  '10': 40,
  '12': 48
};

// Usage
Layout.register({
  id: 'control-bar',
  position: {
    bottom: SPACING['4'],  // 16px from bottom
    // NOT: bottom: 16
  }
});
```

**Why:** Consistency. Scalability. A single change propagates everywhere.

---

## Component Categories

### Category A: Fixed Chrome (Header, Footers)

Components that don't resize but affect available space.

```javascript
Layout.register({
  id: 'header',
  category: 'chrome',
  size: {
    width: { mode: 'fill-parent' },
    height: { fixed: 48 }  // Always 48px
  },
  position: { anchor: 'top' },
  zIndex: 200
});
```

### Category B: Resizable Panels (Sidebars)

Components the user can resize within constraints.

```javascript
Layout.register({
  id: 'left-sidebar',
  category: 'panel',
  size: {
    width: { min: 200, preferred: 280, max: 400 },
    height: { mode: 'fill-available' }
  },
  position: { anchor: 'left', below: 'header' },
  resizable: { horizontal: true },
  persist: 'localStorage:sidebar-widths'  // Remember user preference
});
```

### Category C: Flexible Content (Graph Area)

Components that fill remaining space.

```javascript
Layout.register({
  id: '3d-graph',
  category: 'content',
  size: {
    width: { mode: 'fill-available', min: 200 },
    height: { mode: 'fill-available', min: 200 }
  },
  position: {
    leftOf: 'right-sidebar',
    rightOf: 'left-sidebar',
    below: 'header'
  }
});
```

### Category D: Floating Overlays (Tooltips, Control Bar)

Components that float above others and need positioning intelligence.

```javascript
Layout.register({
  id: 'control-bar',
  category: 'overlay',
  size: {
    width: { preferred: 900, max: 'calc(100% - 48px)' },
    height: { mode: 'content' }
  },
  position: {
    anchor: 'bottom-center',
    offset: { y: -16 }
  },
  zIndex: 9999,
  avoidOverlap: ['toast']  // Don't overlap with toast notifications
});
```

---

## Spatial Intelligence Features

### Feature 1: Bounds Awareness

Every component knows its bounds at all times:

```javascript
const bounds = Layout.getBounds('left-sidebar');
// Returns: { x: 0, y: 48, width: 280, height: 552, right: 280, bottom: 600 }
```

### Feature 2: Collision Detection (Opt-In)

For floating components that need to avoid overlap:

```javascript
Layout.register({
  id: 'tooltip',
  category: 'overlay',
  collision: {
    enabled: true,
    avoidOverlap: ['control-bar', 'header', 'toast'],
    strategy: 'flip-shift'  // Flip direction, then shift to fit
  }
});
```

### Feature 3: Viewport Awareness

Components can respond to viewport constraints:

```javascript
Layout.register({
  id: 'right-sidebar',
  responsive: {
    // Below 768px viewport width, collapse to icon-only
    breakpoints: [
      { maxWidth: 768, size: { width: { fixed: 48 } } },
      { minWidth: 769, size: { width: { min: 200, preferred: 260, max: 400 } } }
    ]
  }
});
```

### Feature 4: Relationship Queries

Ask questions about layout relationships:

```javascript
Layout.query.isOverlapping('tooltip', 'control-bar');  // boolean
Layout.query.distanceBetween('header', '3d-graph');    // { x: 0, y: 0 }
Layout.query.wouldFit('new-panel', { width: 300, height: 200 });  // boolean
Layout.query.availableSpace('3d-graph');  // { width: 760, height: 552 }
```

---

## Implementation Phases

### Phase 1: Foundation (Required First)

1. Create `Layout` module with registration system
2. Define component categories and size constraint model
3. Implement 3-phase pipeline (measure → solve → apply)
4. Add dirty tracking with topological sort
5. Migrate existing components to registration model

### Phase 2: Constraint System

1. Implement constraint expression language
2. Add priority levels (required, strong, medium, weak)
3. Build simple constraint solver (greedy, not full Cassowary)
4. Support basic relationships (equals, greaterThan, lessThan)

### Phase 3: Spatial Intelligence

1. Add bounds caching and efficient updates
2. Implement collision detection for overlays
3. Add relationship queries
4. Build viewport awareness and responsive breakpoints

### Phase 4: Persistence and Tooling

1. localStorage integration for user preferences
2. Debug visualization (show bounds, constraints)
3. Performance monitoring (measure times, solve times)
4. Developer console commands for inspection

---

## Migration Strategy

### Step 1: Coexistence

New system runs alongside existing CSS. Components can be migrated incrementally.

```javascript
// Existing CSS still works
#left-sidebar { width: var(--sidebar-width); }

// But registered component can override
Layout.register({ id: 'left-sidebar', ... });
// System applies width via JS, CSS variable is updated for compatibility
```

### Step 2: Gradual Migration

Migrate components in order of dependency (leaves first, containers last):
1. Header (fixed, no dependencies)
2. Sidebars (simple constraints)
3. Graph area (depends on sidebars)
4. Overlays (depends on all)

### Step 3: CSS Reduction

Once all components are migrated, CSS becomes minimal:
- Base styles (fonts, colors)
- Component-internal styles (not layout)
- No more positional CSS (`position`, `top`, `left`, `width`, `height`)

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Direct Style Manipulation

```javascript
// BAD - bypasses layout system
element.style.width = '300px';

// GOOD - goes through layout system
Layout.resize('left-sidebar', { width: 300 });
```

### Anti-Pattern 2: Implicit Dependencies

```css
/* BAD - implicit dependency via CSS variable */
#3d-graph { left: var(--sidebar-width); }

/* GOOD - explicit constraint */
Layout.constrain({ subject: '3d-graph.left', equals: 'left-sidebar.right' });
```

### Anti-Pattern 3: Hardcoded Values

```javascript
// BAD - magic number
position: { bottom: 16 }

// GOOD - semantic token
position: { bottom: SPACING['4'] }
```

### Anti-Pattern 4: Global Queries

```javascript
// BAD - reads layout property, forces browser reflow
const width = element.offsetWidth;

// GOOD - reads from cache
const width = Layout.getBounds('left-sidebar').width;
```

---

## Success Criteria

The layout system is successful when:

1. **No component uses `position: fixed/absolute` directly in CSS** - All positioning through the system
2. **Every component is registered** - Complete manifest exists
3. **All constraints are explicit** - No hidden dependencies
4. **Dirty tracking works** - Only affected components recalculate
5. **User preferences persist** - Resize a sidebar, reload, it's remembered
6. **Collisions are impossible** - System prevents overlapping overlays
7. **Responsive behavior is declarative** - Breakpoints defined, not coded

---

## Open Questions

1. **Cassowary vs. simpler solver?** Full constraint satisfaction is powerful but complex. A greedy solver handles 90% of cases with less overhead.

2. **How to handle 3D graph integration?** The graph has its own coordinate system. Need clear boundary between 2D UI layout and 3D canvas.

3. **Animation integration?** How do layout changes animate? CSS transitions? JS animation? Layout system's responsibility?

4. **Performance budget?** What's acceptable time for full layout solve? 1ms? 5ms? 16ms (one frame)?

---

## References

- Cassowary Algorithm (Apple Auto Layout foundation)
- Qt Layout Management (explicit hierarchy model)
- GTK4 ConstraintLayout (Cassowary in GTK)
- SwiftUI Layout System (declarative + escape hatches)
- Unity UGUI RectTransform (anchor-based)
- CSS Layout Algorithms (reflow/repaint model)
- Design Tokens (spacing systems)

---

## Next Steps

1. Review and approve this specification
2. Create `modules/layout.js` with registration API
3. Define spacing tokens in `schema/viz/tokens/`
4. Migrate one simple component (header) as proof of concept
5. Iterate based on learnings
