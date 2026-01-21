# app.js Professional Modularization Plan

> **Generated:** 2026-01-20
> **Source:** `src/core/viz/assets/app.js` (8,826 lines)
> **Target:** Reduce to ~1,500 lines (core orchestration only)

---

## Executive Summary

| Metric | Current | Target | Change |
|--------|---------|--------|--------|
| app.js lines | 8,826 | ~1,500 | -83% |
| Functions in app.js | 148 | ~15 | -90% |
| Existing modules | 17 | 25+ | +47% |
| Module total lines | 8,054 | 15,000+ | +86% |

---

## FACTS: Current State

### app.js Analysis (8,826 lines)

| Category | Count | Lines | % |
|----------|-------|-------|---|
| Top-level functions | 148 | 8,795 | 99.6% |
| Top-level variables | 103 | ~200 | 2.3% |
| Comments/whitespace | - | ~300 | 3.4% |

### Existing Modules (17 files, 8,054 lines)

| Module | Lines | Exports | Status |
|--------|-------|---------|--------|
| color-engine.js | 1,035 | 4 | Complete |
| file-viz.js | 994 | 2 | Complete |
| control-bar.js | 946 | 1 | Complete |
| sidebar.js | 853 | 1 | Complete |
| data-manager.js | 715 | 2 | Complete |
| animation.js | 689 | 7 | Partial - needs layout funcs |
| edge-system.js | 562 | 1 | Partial - needs helpers |
| selection.js | 489 | 1 | Partial - needs visuals |
| panels.js | 243 | 1 | Complete |
| legend-manager.js | 237 | 1 | Complete |
| main.js | 199 | 0 | Entry point |
| refresh-throttle.js | 190 | 3 | Complete |
| tooltips.js | 176 | 1 | Complete |
| theme.js | 155 | 1 | Complete |
| node-accessors.js | 149 | 1 | Complete |
| core.js | 130 | 1 | Complete |
| utils.js | 292 | 4 | Complete |

---

## CONFIDENCE TABLE

Extraction confidence based on coupling analysis (Graph refs, DM refs, global state, THREE.js).

| Domain | Funcs | Lines | Avg Conf | Risk | Module Target |
|--------|-------|-------|----------|------|---------------|
| color-helpers | 6 | 280 | 100% | LOW | color-helpers.js |
| node-helpers | 11 | 237 | 97% | LOW | node-helpers.js |
| physics | 4 | 138 | 96% | LOW | physics.js |
| datamap | 7 | 167 | 96% | LOW | datamap.js |
| hud | 7 | 397 | 95% | LOW | hud.js |
| hover-interaction | 3 | 119 | 95% | LOW | interaction.js |
| selection | 21 | 677 | 94% | LOW | selection.js (extend) |
| layout | 9 | 316 | 93% | LOW | animation.js (extend) |
| groups | 8 | 135 | 92% | LOW | groups.js |
| controls-ui | 16 | 1,538 | 91% | LOW | controls.js |
| flow-mode | 6 | 309 | 90% | LOW | flow.js |
| edge-helpers | 7 | 430 | 89% | LOW | edge-system.js (extend) |
| file-boundaries | 27 | 1,223 | 88% | LOW | boundaries.js |
| dimension | 5 | 546 | 73% | MED | dimension.js |
| graph-core | 6 | 1,209 | 63% | HIGH | graph.js |

---

## HIGH-COUPLING FUNCTIONS

These functions require careful extraction due to heavy dependencies:

| Function | Lines | Graph | DM | Globals | THREE | Conf |
|----------|-------|-------|----|---------| ------|------|
| initGraph | 492 | 13 | 2 | 8 | 11 | 0% |
| animateDimensionChange | 201 | 30 | 0 | 3 | 0 | 0% |
| drawFileBoundaries | 311 | 1 | 2 | 2 | 57 | 0% |
| decompressPayload | 665 | 0 | 0 | 19 | 2 | 1% |
| refreshGraph | 282 | 19 | 0 | 5 | 0 | 18% |
| applyEdgeStyle | 316 | 13 | 0 | 2 | 0 | 51% |
| renderAllLegends | 454 | 3 | 0 | 6 | 1 | 59% |
| setupConfigControls | 184 | 11 | 0 | 1 | 0 | 62% |

**Strategy for 0% confidence functions:**
1. `initGraph` - Keep in app.js as core orchestrator
2. `animateDimensionChange` - Extract with Graph accessor pattern
3. `drawFileBoundaries` - Extract THREE.js code to boundaries.js
4. `decompressPayload` - Keep in app.js (bootstrap)

---

## EXTRACTION PHASES

### Phase 1: Pure Functions (LOW RISK)

**Target: 8 new modules, ~1,500 lines extracted**

| Module | Functions | Lines | Confidence |
|--------|-----------|-------|------------|
| node-helpers.js | 11 | 237 | 97% |
| color-helpers.js | 6 | 280 | 100% |
| physics.js | 4 | 138 | 96% |
| datamap.js | 7 | 167 | 96% |
| groups.js | 8 | 135 | 92% |
| hover.js | 3 | 119 | 95% |

**Phase 1 Functions:**
```
node-helpers.js:
  getNodeColorByMode, getSubsystem, getPhase, getFileType, getRoleCategory,
  applyNodeColors, applyNodeSizeMode, getNodeTierValue, getNodeDepth,
  getSemanticSimilarity, groupNodesByTier

color-helpers.js:
  getTopoColor, normalizeColorInput, toColorNumber, dimColor,
  getFileHue, getFileColor

physics.js:
  applyPhysicsState, applyPhysicsPreset, updatePhysicsSliders,
  buildPhysicsControls

datamap.js:
  normalizeDatamapConfig, resolveDatamapConfigs, datamapMatches,
  setDatamap, setNodeColorMode, applyDatamap, updateDatamapControls

groups.js:
  loadGroups, saveGroups, getNextGroupColor, getGroupById,
  getPrimaryGroupForNode, renderGroupList, updateGroupButtonState,
  createGroupFromSelection

hover.js:
  handleNodeHover, handleNodeClick, updateHoverPanel
```

### Phase 2: UI & Controls (LOW-MEDIUM RISK)

**Target: 4 modules, ~2,500 lines extracted**

| Module | Functions | Lines | Confidence |
|--------|-----------|-------|------------|
| controls.js | 16 | 1,538 | 91% |
| hud.js | 7 | 397 | 95% |
| flow.js | 6 | 309 | 90% |
| layout.js → animation.js | 9 | 316 | 93% |

**Phase 2 Functions:**
```
controls.js:
  setupControls, setupConfigControls, buildChipGroup, populateFilterChips,
  renderLegendSection, renderAllLegends, buildCheckboxRow, buildFilterGroup,
  buildDatamapToggle, buildExclusiveOptions, buildMetadataControls,
  buildAppearanceSliders, setupCollapsibleSections, clearAllFilters,
  collectCounts, initCommandBar

hud.js:
  setupReport, setupAIInsights, setupMetrics, setupHudFade,
  updateHudStats, updateBackgroundBrightness, applyMetadataVisibility

flow.js:
  getFlowPresetColor, getFlowPresetValue, toggleFlowMode,
  disableFlowMode, applyFlowVisualization, clearFlowVisualization

animation.js (extend):
  saveNodePositions, restoreNodePositions, freezeLayout, unfreezeLayout,
  resetLayout, applyLayoutPreset, cycleStaggerPattern, startLayoutMotion,
  startFlockSimulation
```

### Phase 3: Complex Systems (MEDIUM-HIGH RISK)

**Target: 3 modules, ~2,500 lines extracted**

| Module | Functions | Lines | Confidence |
|--------|-----------|-------|------------|
| selection.js (extend) | 21 | 677 | 94% |
| boundaries.js | 27 | 1,223 | 88% |
| dimension.js | 5 | 546 | 73% |

**Phase 3 Functions:**
```
selection.js (extend):
  getSelectedNodes, setSelection, updateSelectionPanel, showSelectionModal,
  hideSelectionModal, initSelectionModal, updateSelectionVisuals,
  animateSelectionColors, startSelectionAnimation, stopSelectionAnimation,
  syncSelectionAfterGraphUpdate, updateSelectionBox, getNodeScreenPosition,
  selectNodesInBox, setupSelectionInteractions, initSelectionState,
  getSelectionColor, getNodeSpatialPhase, updateOverlayScale,
  ensureNodeOverlays, updatePendulums

boundaries.js:
  drawFileBoundaries, buildHull2D, computeCentroid, sampleFileNodes,
  buildSpatialGrid, getNeighborCells, applySoftCollisions, buildDirectoryTree,
  computeFileActivity, drawContainmentSpheres, startContainmentAnimation,
  stopContainmentAnimation, popBoundaries, restoreBoundaries, scheduleHullRedraw,
  clearFileBoundaries, applyClusterForce, applyFileCohesion, clearFileCohesion,
  toggleFileExpand, setFileModeState, updateExpandButtons, setFileVizMode,
  applyFileVizMode, applyFileColors, clearAllFileModes, handleCmdFiles

dimension.js:
  toggleDimensions, setupDimensionToggle, animateDimensionChange,
  setStarsVisible, handleCmd3d
```

### Phase 4: Graph Core (HIGH RISK)

**Target: Minimal extraction, heavy refactoring**

| Module | Functions | Lines | Confidence |
|--------|-----------|-------|------------|
| graph.js | 4 | ~600 | 63% |
| edge-helpers.js | 7 | 430 | 89% |

**Keep in app.js (~1,500 lines):**
- `initGraph` - Core orchestrator
- `refreshGraph` - Core refresh logic
- `filterGraph` - Core filtering
- `decompressPayload` - Bootstrap
- Global state declarations
- Event bindings
- Initialization sequence

**Extract to graph.js:**
- `runSelfTest`
- `buildFileGraph`
- `buildHybridGraph`

**Extract to edge-system.js (extend):**
- `applyEdgeStyle`
- `getLinkEndpointId`
- `getFileTarget`
- `captureFileNodePositions`
- `updateEdgeRanges`
- `refreshNodeFileIndex`
- `getLinkFileIdx`

---

## MODULE DEPENDENCY GRAPH

```
                    ┌─────────────┐
                    │   app.js    │
                    │  (1,500 L)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│   graph.js    │  │  controls.js  │  │  dimension.js │
│   (600 L)     │  │  (1,538 L)    │  │   (546 L)     │
└───────┬───────┘  └───────┬───────┘  └───────────────┘
        │                  │
        ▼                  ▼
┌───────────────┐  ┌───────────────┐
│ edge-system.js│  │    hud.js     │
│   (992 L)     │  │   (397 L)     │
└───────────────┘  └───────────────┘

        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  selection.js │  │ boundaries.js │  │   flow.js     │
│  (1,166 L)    │  │  (1,223 L)    │  │   (309 L)     │
└───────────────┘  └───────────────┘  └───────────────┘

        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│node-helpers.js│  │color-helpers.js│ │  datamap.js   │
│   (237 L)     │  │   (280 L)     │  │   (167 L)     │
└───────────────┘  └───────────────┘  └───────────────┘

        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  physics.js   │  │   groups.js   │  │   hover.js    │
│   (138 L)     │  │   (135 L)     │  │   (119 L)     │
└───────────────┘  └───────────────┘  └───────────────┘

                    ┌─────────────┐
                    │   core.js   │◄── Foundation
                    │   utils.js  │    (no deps)
                    └─────────────┘
```

---

## GLOBAL STATE MANAGEMENT

### Current Globals (103 declarations)

| Category | Count | Strategy |
|----------|-------|----------|
| Graph instances | 3 | Keep in app.js, expose via window |
| UI state | 15 | Move to STATE object |
| Config objects | 12 | Move to CONFIG object |
| Geometry/THREE | 8 | Keep in app.js |
| Animation state | 6 | Move to ANIM module |
| Selection state | 5 | Move to SELECT module |
| File viz state | 4 | Move to FILEVIZ module |

### Proposed State Consolidation

```javascript
// app.js - Core state (keep)
let Graph = null;
let DM = null;
let FULL_GRAPH = null;

// STATE module - UI state
window.STATE = {
  selectedNodeIds: new Set(),
  hoveredNode: null,
  flowMode: false,
  graphMode: 'atoms',
  is3d: true,
  layoutFrozen: false,
  hintsEnabled: true,
  currentDensity: 1
};

// CONFIG module - Configuration
window.CONFIG = {
  theme: {...},
  edgeMode: {...},
  nodeColor: {...},
  flow: {...},
  appearance: {...}
};
```

---

## EXTRACTION CHECKLIST

### Per-Function Extraction

- [ ] Read function body completely
- [ ] Identify all dependencies (Graph, DM, globals, DOM, THREE)
- [ ] Create IIFE wrapper with proper namespace
- [ ] Add window.* accessors for external deps
- [ ] Add backward-compat shims if needed
- [ ] Update MODULE_ORDER in visualize_graph_webgl.py
- [ ] Replace function in app.js with "MOVED TO" comment
- [ ] Regenerate: `./collider full . --output .collider`
- [ ] Browser test: no console errors, feature works

### Per-Phase Verification

```bash
# After each phase
./collider full . --output .collider
open .collider/*.html

# Verify checklist:
# [ ] Graph renders
# [ ] Controls work
# [ ] No JS console errors
# [ ] All features functional
```

---

## TIMELINE ESTIMATE

| Phase | Modules | Lines | Sessions |
|-------|---------|-------|----------|
| Phase 1 | 6 new | 1,076 | 1 |
| Phase 2 | 4 new/ext | 2,560 | 2 |
| Phase 3 | 3 ext | 2,446 | 2 |
| Phase 4 | 2 ext | 1,030 | 1 |
| **Total** | **15** | **7,112** | **6** |

---

## SUCCESS CRITERIA

1. **app.js < 2,000 lines** - Core orchestration only
2. **All modules < 1,200 lines** - Manageable size
3. **Zero console errors** - Clean runtime
4. **All features work** - No regression
5. **Clear module boundaries** - Single responsibility
6. **Documented dependencies** - Each module header states deps

---

## APPENDIX: Function-to-Module Mapping

### node-helpers.js (NEW)
```
L2292: getNodeColorByMode
L2361: getSubsystem
L2372: getPhase
L2382: getFileType
L2388: getRoleCategory
L2400: applyNodeColors
L3002: applyNodeSizeMode
L5778: getNodeTierValue
L5788: getNodeDepth
L5797: getSemanticSimilarity
L3964: groupNodesByTier
```

### color-helpers.js (NEW)
```
L3624: getTopoColor
L5819: normalizeColorInput
L5833: toColorNumber
L7005: dimColor
L6355: getFileHue
L6369: getFileColor
```

### physics.js (NEW)
```
L4850: applyPhysicsState
L4863: applyPhysicsPreset
L4877: updatePhysicsSliders
L4892: buildPhysicsControls
```

### datamap.js (NEW)
```
L4349: normalizeDatamapConfig
L4377: resolveDatamapConfigs
L4396: datamapMatches
L6303: setDatamap
L6331: setNodeColorMode
L6344: applyDatamap
L5518: updateDatamapControls
```

### groups.js (NEW)
```
L6435: loadGroups
L6454: saveGroups
L6462: getNextGroupColor
L6467: getGroupById
L6471: getPrimaryGroupForNode
L6483: renderGroupList
L6542: updateGroupButtonState
L6550: createGroupFromSelection
```

### hover.js (NEW)
```
L7273: handleNodeHover
L7328: handleNodeClick
L6386: updateHoverPanel
```

### controls.js (NEW)
```
L2788: setupControls
L2818: setupConfigControls
L899: buildChipGroup
L945: populateFilterChips
L961: renderLegendSection
L1016: renderAllLegends
L4291: buildCheckboxRow
L4314: buildFilterGroup
L4431: buildDatamapToggle
L4458: buildExclusiveOptions
L4487: buildMetadataControls
L4508: buildAppearanceSliders
L5231: setupCollapsibleSections
L4248: clearAllFilters
L4279: collectCounts
L698: initCommandBar
```

### hud.js (NEW)
```
L5263: setupReport
L5272: setupAIInsights
L5385: setupMetrics
L5458: setupHudFade
L5479: updateHudStats
L4988: updateBackgroundBrightness
L4996: applyMetadataVisibility
```

### flow.js (NEW)
```
L5994: getFlowPresetColor
L6002: getFlowPresetValue
L6101: toggleFlowMode
L6138: disableFlowMode
L6158: applyFlowVisualization
L6268: clearFlowVisualization
```

### boundaries.js (NEW)
```
L7343: toggleFileExpand
L7360: sampleFileNodes
L7366: buildHull2D
L7399: computeCentroid
L7407: drawFileBoundaries
L7718: buildSpatialGrid
L7736: getNeighborCells
L7749: applySoftCollisions
L7799: buildDirectoryTree
L7831: computeFileActivity
L7854: drawContainmentSpheres
L7954: startContainmentAnimation
L8036: stopContainmentAnimation
L8047: popBoundaries
L8103: restoreBoundaries
L8152: setFileModeState
L8246: updateExpandButtons
L8251: setFileVizMode
L8276: applyFileVizMode
L8334: scheduleHullRedraw
L8353: applyFileColors
L8367: clearFileBoundaries
L8373: clearAllFileModes
L8421: applyClusterForce
L8486: applyFileCohesion
L8542: clearFileCohesion
L8561: handleCmdFiles
```

### dimension.js (NEW)
```
L5551: toggleDimensions
L5566: setupDimensionToggle
L5577: animateDimensionChange
L5936: setStarsVisible
L8567: handleCmd3d
```

### selection.js (EXTEND)
```
L6570: getSelectedNodes
L6576: setSelection
L6591: formatCountList
L6595: appendSelectionRow
L6608: updateSelectionPanel
L6702: showSelectionModal
L6820: hideSelectionModal
L6825: initSelectionModal
L6869: updateOverlayScale
L6881: ensureNodeOverlays
L6937: updatePendulums
L6967: getSelectionColor
L6984: getNodeSpatialPhase
L7014: animateSelectionColors
L7044: startSelectionAnimation
L7055: stopSelectionAnimation
L7059: updateSelectionVisuals
L7146: syncSelectionAfterGraphUpdate
L7163: updateSelectionBox
L7174: getNodeScreenPosition
L7185: selectNodesInBox
L7202: setupSelectionInteractions
L7264: initSelectionState
```

### animation.js (EXTEND)
```
L2539: saveNodePositions
L2553: restoreNodePositions
L2573: freezeLayout
L2587: unfreezeLayout
L2598: resetLayout
L4009: applyLayoutPreset
L4105: cycleStaggerPattern
L4113: startLayoutMotion
L4138: startFlockSimulation
```

### edge-system.js (EXTEND)
```
L3026: applyEdgeStyle
L2616: getLinkEndpointId
L2624: getFileTarget
L2698: captureFileNodePositions
L5858: updateEdgeRanges
L5884: refreshNodeFileIndex
L5894: getLinkFileIdx
```

### graph.js (NEW)
```
L2113: runSelfTest
L2638: buildFileGraph
L2712: buildHybridGraph
```

### KEEP IN app.js
```
L33: decompressPayload
L1470: initFallback2D
L1621: initGraph
L2419: filterGraph
L3342: refreshGraph
+ All global state declarations
+ Event bindings
+ Initialization sequence
```
