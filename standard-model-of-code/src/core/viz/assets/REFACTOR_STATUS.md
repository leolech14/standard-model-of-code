# REFACTOR STATUS REPORT
**Generated:** 2026-01-20 00:35

## EXECUTIVE SUMMARY

| Metric | Count |
|--------|-------|
| Total Modules | 14 |
| GOOD Re-exports | 26 |
| BROKEN Re-exports | 14 |
| Completion | ~65% |

## MODULE STATUS

| Module | Lines | Status | Issues |
|--------|-------|--------|--------|
| core.js | 118 | **GOOD** | All 4 re-exports properly linked |
| node-accessors.js | 149 | **GOOD** | All 8 re-exports properly linked |
| edge-system.js | 550 | **GOOD** | All 8 re-exports properly linked |
| color-engine.js | 325 | **GOOD** | 2 re-exports (simple alias) |
| refresh-throttle.js | 190 | **GOOD** | No re-exports needed |
| control-bar.js | 946 | **GOOD** | No re-exports needed |
| main.js | 199 | **GOOD** | Wiring only, no re-exports |
| animation.js | 692 | **PARTIAL** | 2 good, 4 broken |
| selection.js | 488 | **PARTIAL** | 3 good, 4 broken |
| file-viz.js | 968 | **PARTIAL** | 3 good, 2 broken |
| panels.js | 244 | **PARTIAL** | 1 good, 1 broken |
| data-manager.js | 715 | **BROKEN** | 1 broken (DM) |
| legend-manager.js | 237 | **BROKEN** | 1 broken (Legend) |
| sidebar.js | 593 | **CHECK** | No re-exports (uses class) |

## BROKEN RE-EXPORTS (MUST FIX)

### animation.js
```js
// CURRENT (broken):
let CURRENT_LAYOUT = 'force';
let LAYOUT_ANIMATION_ID = null;
let LAYOUT_TIME = 0;
let CURRENT_STAGGER_PATTERN = 'tier';

// SHOULD BE:
let CURRENT_LAYOUT = ANIM.currentLayout;
let LAYOUT_ANIMATION_ID = ANIM.animationId;
let LAYOUT_TIME = ANIM.layoutTime;
let CURRENT_STAGGER_PATTERN = ANIM.currentStaggerPattern;
```

### selection.js
```js
// CURRENT (broken):
let MARQUEE_ACTIVE = false;
let MARQUEE_START = null;
let MARQUEE_ADDITIVE = false;
let LAST_MARQUEE_END_TS = 0;

// SHOULD BE:
let MARQUEE_ACTIVE = SELECT.marqueeActive;
let MARQUEE_START = SELECT.marqueeStart;
let MARQUEE_ADDITIVE = SELECT.marqueeAdditive;
let LAST_MARQUEE_END_TS = SELECT.lastMarqueeEndTs;
```

### file-viz.js
```js
// CURRENT (broken):
let FILE_GRAPH = null;
let FILE_NODE_POSITIONS = new Map();

// SHOULD BE:
let FILE_GRAPH = FILE_VIZ.graph;
let FILE_NODE_POSITIONS = FILE_VIZ.nodePositions;
```

### panels.js
```js
// CURRENT (broken):
let _activePanelId = null;

// SHOULD BE:
let _activePanelId = PANELS.activePanelId;
```

### data-manager.js
```js
// CURRENT (broken):
let DM = null;

// SHOULD BE:
let DM = DATA.manager;  // Or expose DATA itself
```

### legend-manager.js
```js
// CURRENT (broken):
let Legend = null;

// SHOULD BE:
let Legend = LEGEND.instance;  // Or expose LEGEND itself
```

## ACTION PLAN

### Phase 1: Fix Module Internals
For each broken re-export, verify the module exposes the value:
1. Check if module has getter/property for the value
2. If not, ADD the getter to the module
3. Update re-export to use the getter

### Phase 2: Remove app.js Duplicates
Once re-exports are fixed:
1. Remove duplicate declarations from app.js
2. Keep only app.js-specific state that modules don't manage

### Phase 3: Test
1. Regenerate HTML: `./collider full . --output .collider`
2. Open in browser
3. Verify no console errors
4. Test all functionality

## GOOD RE-EXPORTS (Already Working)

These can be safely removed from app.js:
- `SELECTED_NODE_IDS` (selection.js)
- `EDGE_MODE`, `EDGE_RANGES`, `NODE_FILE_INDEX`, `FILE_HUE_MAP` (edge-system.js)
- `EDGE_MODE_ORDER`, `EDGE_MODE_LABELS`, `EDGE_MODE_HINTS`, `GRADIENT_PALETTES` (edge-system.js)
- `SELECTION_SIZE_MULT`, `PENDULUM`, `amplify`, `amplifyContrast` (core.js)
- `getNodeTier`, `getNodeAtomFamily`, `getNodeRing`, etc. (node-accessors.js)
- `LAYOUT_PRESETS`, `STAGGER_PATTERNS` (animation.js)
- `FILE_NODE_IDS`, `EXPANDED_FILES`, `FILE_EXPAND_MODE` (file-viz.js)
- `selectionOriginals`, `originalColorsForDim` (selection.js)
- `HudLayoutManager` (panels.js)
- `ColorOrchestrator`, `Color` (color-engine.js)
- `TIER_ALIASES` (node-accessors.js)
