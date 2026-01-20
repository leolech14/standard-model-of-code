# Architecture Debt Registry

> Critical architectural issues identified for future remediation.
>
> **Created:** 2026-01-19
> **Source:** Session forensics from "cryptic-percolating-beaver"

---

## CRITICAL: No Clear Internal Call Structure

### The Core Problem

**app.js is a 10,000+ line monolith with no clear call hierarchy.**

The codebase exhibits "random web" architecture - functions call each other without clear layers, boundaries, or dependency direction. This makes:

- Debugging extremely difficult (no clear entry points)
- Refactoring risky (unknown downstream effects)
- Performance optimization guesswork (no hot path visibility)
- Testing nearly impossible (no isolation)

### Evidence

| Symptom | Observation |
|---------|-------------|
| File size | 10,000+ lines in single file |
| forEach count | 154 forEach loops (many nested) |
| Global state | Multiple global variables modified from anywhere |
| Animation systems | 3+ separate requestAnimationFrame loops that can conflict |
| No module boundaries | Everything in global scope or single IIFE |

### Desired State

```
┌─────────────────────────────────────────────────────────────┐
│                      ENTRY POINTS                           │
│  initializeApp() → setupGraph() → bindEvents()              │
├─────────────────────────────────────────────────────────────┤
│                      SUBSYSTEMS                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Layout  │  │ Render  │  │ Filter  │  │ Physics │        │
│  │ Manager │  │ Engine  │  │ System  │  │ Engine  │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
├───────┴────────────┴────────────┴────────────┴──────────────┤
│                      DATA LAYER                             │
│  DataManager (single source of truth for graph state)       │
└─────────────────────────────────────────────────────────────┘
```

### Remediation Plan

| Phase | Action | Effort |
|-------|--------|--------|
| 1 | Map all function call relationships | MEDIUM |
| 2 | Identify natural subsystem boundaries | MEDIUM |
| 3 | Extract Physics subsystem (flock, forces) | HIGH |
| 4 | Extract Layout subsystem (presets, animations) | HIGH |
| 5 | Extract Render subsystem (colors, materials) | HIGH |
| 6 | Create clear DataManager interface | HIGH |

---

## HIGH: O(n²) Flock Simulation

### Location

`src/core/viz/assets/app.js:5238-5258`

### The Problem

```javascript
// NESTED O(n²) LOOP
nodes.forEach(n => {           // O(n)
    nodes.forEach(other => {   // × O(n) = O(n²)
        if (other === n) return;
        const dx = (other.x || 0) - (n.x || 0);
        const dy = (other.y || 0) - (n.y || 0);
        const dz = (other.z || 0) - (n.z || 0);
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);
        // ... separation, alignment, cohesion calculations
    });
});
```

### Impact

| Nodes | Iterations/Frame | At 60fps | User Experience |
|-------|------------------|----------|-----------------|
| 100 | 10,000 | 600K/sec | Smooth |
| 300 | 90,000 | 5.4M/sec | Acceptable |
| 500 | 250,000 | 15M/sec | Laggy |
| 1000 | 1,000,000 | 60M/sec | Unusable |
| 2000 | 4,000,000 | 240M/sec | Browser freeze |

### Current Mitigation

Guard added at line 5228:
```javascript
const FLOCK_MAX_NODES = 500;
if (nodes.length > FLOCK_MAX_NODES) {
    console.warn(`[Performance] Flock disabled: ${nodes.length} nodes exceeds limit`);
    return;
}
```

### Proper Fix

Replace O(n²) with spatial partitioning:

```javascript
// O(n) spatial grid approach
const grid = new Map();  // cellKey -> [nodes in cell]
const cellSize = separation * 2;

// Build grid: O(n)
nodes.forEach(n => {
    const key = `${Math.floor(n.x/cellSize)},${Math.floor(n.y/cellSize)}`;
    if (!grid.has(key)) grid.set(key, []);
    grid.get(key).push(n);
});

// Query neighbors: O(n) average case
nodes.forEach(n => {
    const nearbyNodes = getNeighborCells(n, grid);  // Only ~9-27 cells
    nearbyNodes.forEach(other => { /* physics */ });
});
```

**Note:** File cohesion (lines 9310-9350) already uses this pattern correctly.

---

## HIGH: Unthrottled Graph.refresh()

### Location

`src/core/viz/assets/app.js:5259` (and lines 4428, 4450, 4481)

### The Problem

```javascript
function flockStep() {
    nodes.forEach(n => { /* physics calculations */ });
    Graph.refresh();  // <-- EXPENSIVE: Full WebGL scene rebuild
    LAYOUT_ANIMATION_ID = requestAnimationFrame(flockStep);  // 60fps
}
```

`Graph.refresh()` triggers:
- Full geometry buffer update
- Material recompilation (if needed)
- Draw call submission
- GPU sync

At 60fps with no throttling, GPU is constantly rebuilding the scene.

### Fix

```javascript
let frameCount = 0;
const REFRESH_INTERVAL = 2;  // Refresh every 2nd frame

function flockStep() {
    nodes.forEach(n => { /* physics calculations */ });

    frameCount++;
    if (frameCount % REFRESH_INTERVAL === 0) {
        Graph.refresh();  // Only 30fps refresh, physics still 60fps
    }

    LAYOUT_ANIMATION_ID = requestAnimationFrame(flockStep);
}
```

---

## MEDIUM: Multiple Animation Systems

### Location

Lines 4420, 4447, 4459 (three separate requestAnimationFrame loops)

### The Problem

Three different animation systems can run simultaneously:
1. `animateTransition()` - Layout preset transitions
2. `startLayoutMotion()` - Continuous motion effects
3. `startFlockSimulation()` - Boid flocking

They share `LAYOUT_ANIMATION_ID` but cancellation is inconsistent.

### Evidence

```javascript
// Line 4409 - cancels previous
if (LAYOUT_ANIMATION_ID) cancelAnimationFrame(LAYOUT_ANIMATION_ID);

// But startLayoutMotion() doesn't always cancel first
// And physics forces can conflict with layout animations
```

### Fix

Unified animation manager:

```javascript
const AnimationManager = {
    activeSystem: null,
    frameId: null,

    start(system, stepFn) {
        this.stop();  // Always cancel previous
        this.activeSystem = system;
        const loop = () => {
            stepFn();
            this.frameId = requestAnimationFrame(loop);
        };
        this.frameId = requestAnimationFrame(loop);
    },

    stop() {
        if (this.frameId) {
            cancelAnimationFrame(this.frameId);
            this.frameId = null;
        }
        this.activeSystem = null;
    }
};
```

---

## Summary: Priority Matrix

| ID | Issue | Severity | Effort | Impact |
|----|-------|----------|--------|--------|
| ARCH-001 | No clear call structure | CRITICAL | HIGH | Blocks all other improvements |
| ARCH-002 | O(n²) flock simulation | HIGH | MEDIUM | Performance cliff at 500+ nodes |
| ARCH-003 | Unthrottled Graph.refresh() | HIGH | LOW | Easy win, significant perf gain |
| ARCH-004 | Multiple animation systems | MEDIUM | MEDIUM | Race conditions, conflicts |

---

## Appendix: Call Graph Audit Needed

To fix ARCH-001, we need to run Collider on itself and analyze:

```bash
./collider full src/core/viz/assets --output /tmp/app_analysis
```

Then examine:
- Which functions have highest in-degree (most callers)?
- Which functions have highest out-degree (call most things)?
- Are there clear clusters that could become modules?
- What are the entry points from HTML event handlers?

This is **meta-ironic**: using Collider to diagnose Collider's own architecture problems.
