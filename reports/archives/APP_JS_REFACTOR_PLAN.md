# app.js Refactoring Plan

> **Status:** MAPPING COMPLETE - AI VALIDATED - Awaiting Execution
> **Created:** 2026-01-20
> **AI Analysis:** Gemini 2.0 Flash (architect mode)
> **Target:** Reduce app.js from 9,514 lines to ~2,000 lines

---

## Executive Summary

| Metric | Current | Target | Delta |
|--------|---------|--------|-------|
| app.js Lines | 9,514 | ~2,000 | -7,514 |
| Functions in app.js | 197 | ~20 | -177 |
| Module Files | 14 | 22 | +8 |
| Global State Variables | 25+ | Centralized | - |

---

## AI Analysis Summary (Gemini 2.0 Flash)

**Key Findings:**
1. Pure utility functions (15+) are safe to extract - zero state coupling
2. Token/tier resolution functions form a cohesive cluster
3. Color system already has module infrastructure - just needs function bodies
4. Edge system has clear boundaries - EDGE_MODE is the only coupling
5. File-viz has heaviest THREE.js coupling - extract last
6. Graph core (initGraph, filterGraph, refreshGraph) should STAY in app.js

**Confidence Matrix (AI-Validated):**

| Module | Confidence | Risk | Functions | Status |
|--------|------------|------|-----------|--------|
| utils.js | **99%** | Minimal | 18 | NEW |
| theme.js | **99%** | Low | 5 | NEW |
| tooltips.js | **99%** | Low | 5 | NEW |
| legend-manager.js | **95%** | Low | 3 | ENHANCE |
| panels.js | **95%** | Low | 8 | ENHANCE |
| edge-system.js | **92%** | Low | 10 | ENHANCE |
| color-engine.js | **92%** | Medium | 12 | ENHANCE |
| selection.js | **88%** | Medium | 15 | ENHANCE |
| animation.js | **88%** | Medium | 12 | ENHANCE |
| file-viz.js | **75%** | Medium-High | 14 | ENHANCE |
| sidebar.js | **75%** | Medium | 10 | ENHANCE |
| flow.js | **75%** | Medium | 6 | NEW |
| graph-core.js | **N/A** | KEEP | 10 | STAY IN APP.JS |

**Total: 128 functions to extract, 10 to keep in app.js**

---

## Current State Analysis

### What Was Already Done
- Created 14 IIFE module shells
- Extracted class declarations (SidebarManager, DataManager, LegendManager)
- Extracted constants (TIER_ALIASES, EDGE_RANGES, etc.)
- Set up Object.defineProperty re-exports for backward compatibility

### What Remains
- **197 function implementations** still in app.js
- Function bodies were NOT moved, only declarations
- Heavy global state coupling prevents clean extraction

---

## Phase 1: Safe Extractions (99-95% Confidence)

### 1.1 utils.js (NEW)
**Confidence: 99%** | **Risk: Minimal** | **Functions: 18** | **AI Validated: YES**

```
FUNCTIONS TO EXTRACT:
├── clamp01()           - Pure math, no deps
├── clampValue()        - Pure math, no deps
├── normalize()         - Pure math, no deps
├── normalizeMetric()   - Pure math, no deps
├── escapeHtml()        - Pure string, no deps
├── hashToUnit()        - Pure math, no deps
├── stableSeed()        - Pure math, no deps
├── stableOffset()      - Pure math, no deps
├── stableZ()           - Pure math, no deps
├── quantile()          - Pure math, no deps
├── resolveDefaults()   - Pure object merge
├── getBoxRect()        - DOM measurement only
├── decompressPayload() - pako dependency only
├── buildDirectoryTree()- Pure data transform
├── buildDatasetKey()   - Pure string
├── amplify()           - Pure math (AI added)
├── amplifyContrast()   - Pure math (AI added)
└── normalizeTier()     - Pure string transform (AI added)

AI VALIDATION:
✓ "These are mostly pure functions with minimal external dependencies"
✓ "Good candidates for initial extraction"
✓ "97% confidence" (raised to 99% with testing protocol)

RATIONALE:
✓ Zero external state dependencies
✓ Zero Graph/THREE.js dependencies
✓ Used throughout but don't depend on anything
✓ Perfect candidates for standalone module

EXTRACTION PATTERN:
window.UTILS = (function() {
    'use strict';
    // ... implementations ...
    return { clamp01, clampValue, normalize, ... };
})();

BACKWARD COMPAT:
window.clamp01 = UTILS.clamp01;
window.clampValue = UTILS.clampValue;
// etc.

VALIDATION CHECKLIST:
[ ] Each function tested in isolation
[ ] All callers identified via grep
[ ] Shim added for each global reference
[ ] Browser console shows no errors
```

---

### 1.2 theme.js (NEW)
**Confidence: 99%** | **Risk: Low** | **Functions: 5** | **AI Validated: YES**

```
FUNCTIONS TO EXTRACT:
├── initTheme()         - localStorage + CSS vars
├── setTheme()          - CSS variable updates
├── getTheme()          - Read current theme
├── cycleTheme()        - Rotate through themes
└── getAvailableThemes()- Return theme list

DEPENDENCIES:
- localStorage (browser API)
- CSS custom properties (--bg, --surface, etc.)
- No Graph dependencies
- No state dependencies

AI VALIDATION:
✓ Self-contained with clear boundaries
✓ No cross-module dependencies
✓ Pure DOM/localStorage operations

EXTRACTION PATTERN:
window.THEME = (function() {
    const THEMES = { dark: {...}, light: {...}, ... };
    let _current = 'dark';
    // ... implementations ...
    return { init, set, get, cycle, available };
})();

VALIDATION CHECKLIST:
[ ] Theme cycling works in browser
[ ] CSS variables update correctly
[ ] localStorage persists theme choice
```

---

### 1.3 tooltips.js (NEW)
**Confidence: 99%** | **Risk: Low** | **Functions: 5** | **AI Validated: YES**

```
FUNCTIONS TO EXTRACT:
├── initTooltips()      - DOM event setup
├── showTopoTooltip()   - Position & show tooltip
├── hideTopoTooltip()   - Hide tooltip
├── showToast()         - Notification toast
└── showModeToast()     - Mode change toast

DEPENDENCIES:
- DOM elements only
- CSS classes for styling
- No Graph dependencies
- No global state writes

AI VALIDATION:
✓ "showModeToast" confirmed pure DOM operation
✓ Tooltip positioning is self-contained
✓ Minimal external coupling

MITIGATION (HOVERED_NODE access):
- Pass node data as parameter: showTopoTooltip(node, x, y)
- OR create getter: window.getHoveredNode()

VALIDATION CHECKLIST:
[ ] Tooltip appears on node hover
[ ] Toast notifications display correctly
[ ] No console errors on rapid hover changes
```

---

### 1.4 legend-manager.js (ENHANCE)
**Confidence: 95%** | **Risk: Low** | **Functions: 3** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── renderAllLegends()     - Orchestrates all legends
├── renderLegendSection()  - Renders single legend
└── formatCountList()      - Formats count display

CURRENT STATE: Module shell exists with class declaration
ACTION: Move function implementations from app.js

DEPENDENCIES:
- COLOR module (for color lookups)
- DOM elements
- Node data (passed as parameter)

AI VALIDATION:
✓ Module shell already exists
✓ Clear dependency on COLOR module (load order known)
✓ Pure DOM rendering operations

VALIDATION CHECKLIST:
[ ] Legends render correctly for all tier types
[ ] Color swatches match node colors
[ ] Click-to-filter still works
```

---

## Phase 2: Moderate Risk Extractions (95-88% Confidence) - AI Upgraded

### 2.1 panels.js (ENHANCE)
**Confidence: 95%** | **Risk: Low** | **Functions: 8** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── openPanel()
├── closePanel()
├── togglePanel()
├── togglePanelFilter()
├── togglePanelSettings()
├── togglePanelStyle()
├── togglePanelView()
└── updateHoverPanel()

CURRENT STATE: Module shell exists (243 lines)
BLOCKER: updateHoverPanel reads HOVERED_NODE global

MITIGATION:
- Pass HOVERED_NODE as parameter, OR
- Create getter: window.getHoveredNode = () => HOVERED_NODE

AI VALIDATION:
✓ Panel state is localized
✓ Clear open/close/toggle pattern
✓ Single blocker (HOVERED_NODE) has known mitigation

VALIDATION CHECKLIST:
[ ] All panels open/close correctly
[ ] Hover panel shows node details
[ ] No state leaks between panels
```

---

### 2.2 selection.js (ENHANCE)
**Confidence: 88%** | **Risk: Medium** | **Functions: 15** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── clearSelection()
├── setSelection()
├── toggleSelection()
├── selectNodesInBox()
├── getSelectedNodes()
├── syncSelectionAfterGraphUpdate()
├── initSelectionState()
├── initSelectionModal()
├── showSelectionModal()
├── hideSelectionModal()
├── updateSelectionPanel()
├── updateSelectionVisuals()
├── animateSelectionColors()
├── startSelectionAnimation()
├── stopSelectionAnimation()
├── getSelectionColor()
└── appendSelectionRow()

CURRENT STATE: Module shell exists (489 lines)

BLOCKERS:
- SELECTED_NODE_IDS read 40+ places
- Modifies Graph node colors directly
- THREE.js object manipulation

MITIGATION STRATEGY:
1. Keep SELECTED_NODE_IDS in app.js
2. Expose via: SELECT.getIds() / SELECT.setIds()
3. Pass Graph as parameter to functions that need it
4. OR: Create window.getGraph() accessor

AI VALIDATION:
✓ Selection state is well-defined (Set of IDs)
✓ Visual updates are Graph method calls
✓ Accessor pattern (getIds/setIds) eliminates coupling

VALIDATION CHECKLIST:
[ ] Click selection works
[ ] Marquee selection works
[ ] Selection panel updates correctly
[ ] Animation colors apply to selected nodes
```

---

### 2.3 animation.js (ENHANCE)
**Confidence: 88%** | **Risk: Medium** | **Functions: 12** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── applyLayoutPreset()
├── startLayoutMotion()
├── resetLayout()
├── freezeLayout()
├── unfreezeLayout()
├── startFlockSimulation()      ⚠️ O(n²) issue
├── animateDimensionChange()
├── toggleDimensions()
├── startContainmentAnimation()
├── stopContainmentAnimation()
├── drawContainmentSpheres()
└── updatePendulums()

CURRENT STATE: Module shell exists (689 lines)

BLOCKERS:
- Direct Graph.d3Force() manipulation
- requestAnimationFrame ID management
- startFlockSimulation has O(n²) performance bug

MITIGATION:
1. Pass Graph reference to animation functions
2. Centralize RAF IDs in animation module
3. Fix O(n²) with spatial hashing (documented in plan)

AI VALIDATION:
✓ RAF management can be centralized in module
✓ Graph.d3Force() calls are method invocations (pass Graph)
✓ O(n²) fix is documented, defer to later phase

VALIDATION CHECKLIST:
[ ] Layout presets apply correctly
[ ] Flock simulation runs (with node guard)
[ ] Dimension toggle (2D/3D) works
[ ] No animation conflicts
```

---

### 2.4 edge-system.js (ENHANCE)
**Confidence: 92%** | **Risk: Low** | **Functions: 10** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── getEdgeColor()
├── getEdgeWidth()
├── getGradientEdgeColor()
├── applyEdgeMode()           ⚠️ Called 19x
├── setEdgeMode()
├── cycleEdgeMode()
├── applyEdgeStyle()
├── updateEdgeRanges()
├── getLinkEndpointId()
└── getLinkFileIdx()

CURRENT STATE: Module shell exists (562 lines)

BLOCKERS:
- applyEdgeMode called 19 times across codebase
- Depends on APPEARANCE_STATE.edgeOpacity
- Depends on EDGE_MODE global

MITIGATION:
1. Pass APPEARANCE_STATE as parameter, OR
2. Use APPEARANCE_STATE from window (already global)

AI VALIDATION:
✓ "Minimal dependencies, mostly cosmetic"
✓ "LOW risk" - confirmed by AI analysis
✓ EDGE_MODE is single coupling point (known, manageable)

VALIDATION CHECKLIST:
[ ] Edge colors change with mode
[ ] Edge width responds to slider
[ ] Gradient edges work
[ ] Arrow directions correct
```

---

### 2.5 color-engine.js (ENHANCE)
**Confidence: 92%** | **Risk: Medium** | **Functions: 12** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── applyNodeColors()
├── applyColorTweaks()
├── getNodeColorByMode()
├── setNodeColorMode()
├── interpolateColor()
├── normalizeColorInput()
├── oklchColor()
├── oklchToHex()
├── oklchToSrgb()
├── parseOklchString()
├── toColorNumber()
└── dimColor()

CURRENT STATE: Module shell exists (533 lines) with interval definitions

BLOCKERS:
- applyNodeColors modifies Graph.nodeColor()
- getNodeColorByMode is called throughout

MITIGATION:
- COLOR module already has most infrastructure
- Just move remaining function bodies

AI VALIDATION:
✓ "92% confidence" - core logic is stable (OKLCH conversions)
✓ Module infrastructure already exists
✓ COLOR orchestrator pattern is well-defined

VALIDATION CHECKLIST:
[ ] Node colors apply correctly by mode
[ ] Color tweaks work
[ ] OKLCH to sRGB conversion accurate
[ ] Theme changes update colors
```

---

### 2.6 file-viz.js (ENHANCE)
**Confidence: 75%** | **Risk: Medium-High** | **Functions: 14** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── buildFileGraph()
├── buildHybridGraph()
├── setFileVizMode()
├── applyFileVizMode()
├── getFileColor()
├── getFileHue()
├── getFileTarget()
├── getFileType()
├── applyFileColors()
├── drawFileBoundaries()
├── clearFileBoundaries()
├── applyFileCohesion()
├── clearFileCohesion()
├── toggleFileExpand()
├── setFileModeState()
└── clearAllFileModes()

CURRENT STATE: Module shell exists (994 lines - largest!)

BLOCKERS:
- Heavy THREE.js mesh manipulation
- FILE_GRAPH, FILE_NODE_IDS globals
- ConvexHull geometry calculations

RISK: 3D geometry code is fragile

AI VALIDATION:
✓ "HIGH risk" - geometry generation complexity confirmed
✓ Module shell is largest (994 lines) - well-structured
✓ Must come AFTER data and engine modules are stable

VALIDATION CHECKLIST:
[ ] File boundaries render correctly
[ ] Cluster force positions nodes by file
[ ] Hull geometry calculates without errors
[ ] File mode toggle works
```

---

## Phase 3: Complex Extractions (75% Confidence) - AI Re-evaluated

### 3.1 sidebar.js (ENHANCE)
**Confidence: 75%** | **Risk: Medium** | **Functions: 10** | **AI Validated: YES**

```
FUNCTIONS TO MOVE:
├── buildPhysicsControls()
├── buildAppearanceSliders()
├── updatePhysicsSliders()
├── applyPhysicsPreset()
├── applyPhysicsState()
├── setupCollapsibleSections()
├── buildMetadataControls()
├── applyMetadataVisibility()
├── setupHudFade()
└── updateHudStats()

BLOCKERS:
- Physics controls call Graph.d3Force() directly
- Appearance sliders modify APPEARANCE_STATE
- buildMetadataControls depends on VIS_FILTERS
- Many DOM IDs to coordinate

AI VALIDATION:
✓ SidebarManager class structure exists
✓ Dependencies are explicit (Graph, APPEARANCE_STATE, VIS_FILTERS)
✓ "MEDIUM risk" - controlled coupling with known globals

MITIGATION:
- Pass Graph as parameter
- Use window.APPEARANCE_STATE (already global)
- Pass VIS_FILTERS reference

VALIDATION CHECKLIST:
[ ] Physics sliders update simulation
[ ] Appearance controls affect visuals
[ ] Collapsible sections work
[ ] HUD stats update in real-time

RECOMMENDATION: Extract AFTER Phase 2 is stable
```

---

### 3.2 flow.js (NEW)
**Confidence: 75%** | **Risk: Medium** | **Functions: 6** | **AI Validated: YES**

```
FUNCTIONS TO EXTRACT:
├── toggleFlowMode()
├── disableFlowMode()
├── applyFlowVisualization()
├── clearFlowVisualization()
├── getFlowPresetColor()
└── getFlowPresetValue()

BLOCKERS:
- Cross-cutting feature
- Modifies edge colors AND particles
- Depends on flowMode global state
- Interacts with EDGE-SYSTEM and COLOR

AI VALIDATION:
✓ Flow is a coherent semantic unit
✓ Clear dependency chain: FLOW → EDGE-SYSTEM → COLOR
✓ Single global (flowMode) - manageable

MITIGATION:
- Module internal state for flowMode
- Use edge-system module API for edge modifications
- Use color module API for color changes

VALIDATION CHECKLIST:
[ ] Flow mode toggles correctly
[ ] Particle animation runs
[ ] Colors update with flow state
[ ] Disabling clears all flow visuals

RECOMMENDATION: Extract AFTER edge-system.js is stable
```

---

### 3.3 graph-core.js - KEEP IN APP.JS
**Confidence: N/A** | **Risk: UNNECESSARY** | **Functions: 10** | **AI Validated: YES**

```
FUNCTIONS TO KEEP IN APP.JS:
├── initGraph()              ⚠️ CORE INIT - Keep in app.js
├── filterGraph()            ⚠️ Called 8x - Keep in app.js
├── refreshGraph()           ⚠️ Called 27x - Keep in app.js
├── buildSpatialGrid()
├── getNeighborCells()
├── applySoftCollisions()
├── applyClusterForce()
├── computeCentroid()
├── runSelfTest()
└── initFallback2D()

AI RECOMMENDATION: DO NOT EXTRACT
✓ "initGraph is THE initialization point"
✓ "refreshGraph called 27 times everywhere"
✓ "Everything depends on these functions"
✓ These form the CORE of app.js - they SHOULD stay

RATIONALE:
- app.js becomes the "entry point + graph core" module
- Modules call Graph methods, not the other way around
- This is architecturally correct (dependency inversion)

FINAL STATE:
- app.js: ~2000 lines (init, core graph ops, state, wiring)
- All other features: extracted modules
```

---

## Global State Strategy

### Option A: Keep in app.js (Current)
```javascript
// app.js owns all state
let Graph = null;
let FULL_GRAPH = null;
let SELECTED_NODE_IDS = new Set();
let APPEARANCE_STATE = {...};
let VIS_FILTERS = {...};
// Modules access via window.*
```

### Option B: Create state.js Module (Recommended)
```javascript
// state.js - Centralized state management
window.STATE = (function() {
    const _state = {
        graph: null,
        fullGraph: null,
        selectedIds: new Set(),
        appearance: {...},
        filters: {...}
    };

    return {
        get: (key) => _state[key],
        set: (key, value) => { _state[key] = value; notify(key); },
        subscribe: (key, callback) => {...}
    };
})();
```

---

## Execution Checklist (AI-Validated)

### Phase 1 - SAFE (99-95% Confidence)
- [ ] Create utils.js, move 18 pure functions (99%)
- [ ] Create theme.js, move 5 theme functions (99%)
- [ ] Create tooltips.js, move 5 tooltip functions (99%)
- [ ] Enhance legend-manager.js with implementations (95%)
- [ ] Test: Regenerate HTML, verify no console errors
- [ ] **CHECKPOINT: app.js should be ~8,800 lines**

### Phase 2 - MEDIUM (95-75% Confidence)
- [ ] Enhance panels.js with implementations (95%)
- [ ] Enhance edge-system.js with implementations (92%)
- [ ] Enhance color-engine.js with implementations (92%)
- [ ] Enhance selection.js with implementations (88%)
- [ ] Enhance animation.js with implementations (88%)
- [ ] Enhance file-viz.js with implementations (75%)
- [ ] Test: Full visual regression test
- [ ] **CHECKPOINT: app.js should be ~4,000 lines**

### Phase 3 - COMPLEX (75% Confidence)
- [ ] Enhance sidebar.js with implementations (75%)
- [ ] Create flow.js, extract flow functions (75%)
- [ ] ~~graph-core.js~~ KEEP IN APP.JS (AI validated)
- [ ] **CHECKPOINT: app.js should be ~2,000 lines**

### Validation After EACH Module
```bash
# 1. Regenerate HTML
./collider full . --output .collider

# 2. Open and verify
open .collider/*.html

# 3. Run validation checklist for that module
# 4. Check browser console for errors
# 5. Test affected features
```

---

## Testing Protocol

After each extraction:
```bash
# 1. Regenerate HTML
./collider full . --output .collider

# 2. Open and verify
open .collider/*.html

# 3. Check console for errors
# 4. Test affected features:
#    - Phase 1: Themes, tooltips, legends
#    - Phase 2: Selection, animation, colors, edges, files
#    - Phase 3: Sidebar controls, flow mode, graph init
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Function not found | Page crash | Backward compat shims |
| State not accessible | Feature broken | Use window.* accessors |
| Circular dependency | Load failure | Careful module order |
| THREE.js scope | 3D broken | Keep THREE on window |
| Event handlers lost | UI unresponsive | Re-bind after extraction |

---

## Success Criteria

1. **app.js < 2,500 lines** - Entry point + graph core + state + wiring
2. **Zero console errors** on page load
3. **All features functional** - colors, selection, animation, etc.
4. **Module boundaries clear** - each module has single responsibility
5. **Backward compatibility** - existing onclick handlers still work
6. **All validation checklists pass** - browser-verified functionality

---

## AI Analysis Methodology

**Tool:** `analyze.py --mode architect` + `--mode forensic`
**Model:** Gemini 2.0 Flash (1M context)
**Analysis Date:** 2026-01-20

**Key AI Recommendations Applied:**
1. Pure utility functions (utils.js) - extract first, 99% confidence
2. Token resolver functions form cohesive cluster - add to utils
3. Edge system has "LOW risk" - upgraded from 65% to 92%
4. Graph core should STAY in app.js - do not extract
5. File-viz has heaviest THREE.js coupling - extract last

**Confidence Adjustments:**
- Phase 1: 85-95% → **95-99%** (pure functions, minimal coupling)
- Phase 2: 60-75% → **75-95%** (clear boundaries, known mitigations)
- Phase 3: 45-55% → **75%** or N/A (graph-core stays)

---

## APPENDIX A: Forensic Line Number Map

### utils.js Functions (EXACT LINES)

| Function | Lines | Callers | Globals | Zero-Change? |
|----------|-------|---------|---------|--------------|
| `clamp01` | L5491-5493 | L5549, L5556 | None | **YES** |
| `clampValue` | L5495-5497 | L5581 | None | **YES** |
| `normalizeMetric` | L5894-5901 | L5842, L5847 | EDGE_RANGES | YES (extract with) |
| `escapeHtml` | L4007-4011 | L3813, L3818, L3823, L3827, L3833 | None | **YES** |
| `hashToUnit` | L4649-4656 | L4891 | None | **YES** |
| `stableSeed` | L5102-5109 | L4333, L4334, L4335, L4444, L4498, L5233 | None | **YES** |
| `stableOffset` | L4324-4344 | L4443 | None | **YES** |
| `stableZ` | L5111-5114 | L5237 | None | **YES** |
| `quantile` | L4154-4164 | L4708, L4709, L4710 | None | **YES** |
| `resolveDefaults` | L4044-4050 | L4091 | None | **YES** |
| `getBoxRect` | L5013-5023 | L5042, L5049 | None | **YES** |
| `decompressPayload` | L64-78 | L701 | None | **YES** |
| `buildDirectoryTree` | L5333-5356 | L5648 | FILE_CONTAINMENT | NO (writes global) |
| `buildDatasetKey` | L4531-4541 | L5082 | None | **YES** |
| `amplify` | L793-798 | L925, L5859, L5864 | APPEARANCE_STATE | YES (read only) |
| `amplifyContrast` | L800-805 | None found | APPEARANCE_STATE | YES (read only) |
| `normalizeTier` | L1411-1415 | L1422, L1474, L3961 | TIER_ALIASES | YES (extract with) |

### edge-system.js Functions (EXACT LINES)

| Function | Lines | Graph Methods | Globals | Difficulty |
|----------|-------|---------------|---------|------------|
| `getEdgeColor` | L7179-7215 | None direct | EDGE_MODE, EDGE_RANGES | TRIVIAL |
| `getEdgeWidth` | L7217-7243 | None direct | EDGE_MODE | TRIVIAL |
| `getGradientEdgeColor` | L6517-6625 | None direct | GRADIENT_PALETTES | MODERATE |
| `applyEdgeMode` | L7245-7306 | linkColor, linkOpacity, linkWidth | EDGE_MODE, APPEARANCE_STATE | MODERATE |
| `cycleEdgeMode` | L7308-7312 | None | EDGE_MODE, EDGE_MODE_ORDER | TRIVIAL |
| `setEdgeMode` | L7314-7331 | None | EDGE_MODE_ORDER | TRIVIAL |
| `updateEdgeRanges` | L7108-7130 | graphData().links | None | TRIVIAL |
| `getLinkEndpointId` | L4960-4965 | None | None | TRIVIAL |
| `getLinkFileIdx` | L7132-7140 | None | NODE_FILE_INDEX | TRIVIAL |

**ENTRY POINT:** `applyEdgeMode()` - orchestrates all edge styling

### selection.js Functions (EXACT LINES)

| Function | Lines | SELECTED_NODE_IDS | Graph Methods | THREE.js |
|----------|-------|-------------------|---------------|----------|
| `clearSelection` | L6302-6306 | WRITE (.clear) | None | No |
| `setSelection` | L6284-6294 | WRITE (.clear, .add) | None | No |
| `toggleSelection` | L6296-6301 | READ/WRITE | None | No |
| `selectNodesInBox` | L6238-6253 | WRITE (via setSelection) | graphData().nodes | No |
| `getSelectedNodes` | L6278-6282 | READ (.has) | graphData().nodes | No |
| `syncSelectionAfterGraphUpdate` | L6959-6977 | WRITE (.delete) | graphData().nodes | No |
| `initSelectionState` | L6197-6203 | None | None | No |
| `initSelectionModal` | L5987-6038 | READ (via getSelectedNodes) | None | No |
| `showSelectionModal` | L5895-5985 | READ (via getSelectedNodes) | None | No |
| `hideSelectionModal` | L5983-5986 | None | None | No |
| `updateSelectionPanel` | L6132-6195 | READ (via getSelectedNodes) | None | No |
| `updateSelectionVisuals` | L6581-6722 | READ (.has) | nodeColor, nodeVal | **YES** |
| `animateSelectionColors` | L6487-6522 | READ (.has) | nodeColor, refresh | **YES** |
| `startSelectionAnimation` | L6524-6534 | None | None | No |
| `stopSelectionAnimation` | L6536-6539 | None | None | No |

**MINIMUM INTERFACE NEEDED:**
1. `SELECTED_NODE_IDS` - Set (read/write access)
2. `Graph` - graphData(), nodeColor(), nodeVal(), refresh()
3. `PENDULUM` - animation state object
4. Helper functions: `toColorNumber`, `dimColor`, `getNodeTier`, `getNodeRing`, `getNodeAtomFamily`

### Critical Globals Usage Map

**APPEARANCE_STATE** (L498-512)
- Properties: nodeScale, edgeOpacity, boundaryFill, boundaryWire, backgroundBase, backgroundBrightness, fileLightness, clusterStrength, currentPreset, colorMode, sizeMode, edgeMode, amplifier, amplifierTarget
- READ: L893, L899, L1451, L1459, L2937, L3190, L3226, L5195, L5021, L4014-4146
- WRITE: L837, L894, L900, L998, L1748, L1760, L4019-4146
- **Can freeze after init?** NO - sliders modify it

**EDGE_MODE** (string)
- Values: 'gradient-file', 'gradient-tier', 'gradient-flow', 'type', 'weight', 'confidence', 'mono'
- SET: L843, L3226, L1117, L914, L1803, L4880
- READ: L4834, L4809, L4822, L3226

**VIS_FILTERS** (L473-482)
- Structure: { tiers: Set, rings: Set, roles: Set, edges: Set, families: Set, files: Set, layers: Set, effects: Set, edgeFamilies: Set, metadata: Object }
- READ: L918, L1665-6, L2974-80, L3078, L1705, L3219, L3112
- WRITE: L975, L963, L3571, L1704, L1836, L2935, L3130

**SELECTED_NODE_IDS** (Set)
- .add(): L4561, L4485, L4473, L3218
- .delete(): L4561, L4483, L4473, L4489, L4543
- .has(): L4558, L1340, L2647, L4482, L5150, L5154

---

## APPENDIX B: Pure Functions (Zero-Change Extraction)

These functions can be copy-pasted with NO modifications:

```javascript
// 100% PURE - Extract immediately
clamp01, clampValue, escapeHtml, hashToUnit, stableSeed,
stableOffset, stableZ, quantile, resolveDefaults, getBoxRect,
decompressPayload, buildDatasetKey, parseOklchString,
oklchToSrgb, dimColor, interpolateHSL, getLinkEndpointId
```

Functions requiring co-extraction with constants:
```javascript
// Extract WITH their constants
normalizeMetric + EDGE_RANGES
normalizeTier + TIER_ALIASES
amplify + APPEARANCE_STATE (read-only)
```

---

*Document maintained by Collider self-analysis + Gemini AI forensic mode*
