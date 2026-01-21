# app.js Final Refactor Plan

> **Goal**: Reduce app.js from 4,666 lines to ~1,500 lines (core orchestration only)
> **Date**: 2026-01-21
> **Status**: IN PROGRESS

## Current State

| Metric | Value |
|--------|-------|
| app.js lines | 4,666 |
| app.js functions | 45 |
| Existing modules | 37 |
| Module total lines | 14,611 |

## Target State

| Metric | Target |
|--------|--------|
| app.js lines | ~1,500 |
| app.js functions | ~12 (core only) |
| Modules | 37 (enhanced) |

## Function Inventory (45 total)

### MOVE 1: Selection Functions → selection.js (~565 lines)

| Function | Lines | Status |
|----------|-------|--------|
| `formatCountList` | 3218-3220 | To move |
| `appendSelectionRow` | 3222-3233 | To move |
| `updateSelectionPanel` | 3235-3324 | To move |
| `showSelectionModal` | 3329-3445 | To move |
| `hideSelectionModal` | 3447-3450 | To move |
| `initSelectionModal` | 3452-3494 | To move |
| `updateOverlayScale` | 3496-3506 | DUPLICATE - delete |
| `ensureNodeOverlays` | 3508-3541 | DUPLICATE - delete |
| `updateSelectionVisuals` | 3567-3652 | To move |
| `syncSelectionAfterGraphUpdate` | 3654-3672 | To move |
| `updateSelectionBox` | 3674-3681 | To move |
| `getNodeScreenPosition` | 3685-3694 | To move |
| `selectNodesInBox` | 3696-3711 | To move |
| `setupSelectionInteractions` | 3713-3773 | To move |
| `initSelectionState` | 3775-3782 | To move |

**Dependencies**: getNodeAtomFamily, getNodeRing, getNodeTier, collectCounts, showToast, HudLayoutManager, createGroupFromSelection, buildDatasetKey, loadGroups, renderGroupList, getBoxRect, SPACE_PRESSED, HOVERED_NODE, Graph, THREE

### MOVE 2: File Boundary Functions → file-viz.js (~900 lines)

| Function | Lines | Status |
|----------|-------|--------|
| `toggleFileExpand` | 3854-3872 | To move |
| `drawFileBoundaries` | 3874-4182 | To move |
| `buildDirectoryTree` | 4184-4214 | To move |
| `computeFileActivity` | 4216-4237 | To move |
| `drawContainmentSpheres` | 4239-4335 | To move |
| `startContainmentAnimation` | 4337-4417 | To move |
| `stopContainmentAnimation` | 4419-4428 | To move |
| `popBoundaries` | 4430-4490 | To move |
| `restoreBoundaries` | 4492-4530 | To move |
| `updateExpandButtons` | 4532-4560 | To move |
| `handleCmdFiles` | ~4600 | To move |

**Dependencies**: FILE_BOUNDARIES, FILE_SPHERES_GROUP, Graph, THREE, TWEEN, getFileColorByExtension, VIS_FILTERS

### MOVE 3: UI Control Functions → ui-builders.js (~600 lines)

| Function | Lines | Status |
|----------|-------|--------|
| `initCommandBar` | 537-736 | To move |
| `buildChipGroup` | 738-782 | To move |
| `populateFilterChips` | 784-852 | To move |
| `setupControls` | 1870-1898 | To move |
| `setupConfigControls` | 1900-2086 | To move |
| `buildMetadataControls` | 2548-2567 | To move |
| `buildAppearanceSliders` | 2569-3216 | To move |

**Dependencies**: VIS_FILTERS, APPEARANCE_STATE, Graph, refreshGraph, applyEdgeStyle

### MOVE 4: Remaining Functions

| Function | Lines | Target Module |
|----------|-------|---------------|
| `handleNodeHover` | 3784-3852 | hover.js |
| `handleNodeClick` | 3839-3852 | hover.js |
| `applyEdgeStyle` | 2088-2123 | edge-system.js |
| `handleCmdFlow` | ~4650 | flow.js |
| `handleCmd3d` | ~4700 | layout.js |

### KEEP: Core Orchestration (~12 functions)

| Function | Lines | Purpose |
|----------|-------|---------|
| `decompressPayload` | 33-535 | Bootstrap, data parsing |
| `initFallback2D` | 854-1003 | 2D fallback init |
| `initGraph` | 1005-1483 | Main graph initialization |
| `runSelfTest` | 1485-1669 | Diagnostics |
| `filterGraph` | 1671-1792 | Core filtering |
| `buildHybridGraph` | 1794-1868 | Graph building |
| `refreshGraph` | 2125-2546 | Core refresh |

## Extraction Protocol

For each move:

1. **Add functions to target module** inside IIFE
2. **Expose via public API** in return statement
3. **Add backward-compat shims** at bottom of module
4. **Remove from app.js**
5. **Test immediately** with `./collider full . --output .collider_test`

## Shim Pattern

```javascript
// At bottom of module, OUTSIDE the IIFE:
function functionName(...args) { return MODULE.functionName(...args); }
window.functionName = functionName;  // For HTML onclick handlers
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing functionality | Backward-compat shims |
| Module load order issues | Explicit dependency comments |
| Missing dependencies | Check each function's external calls |
| Performance regression | Run self-test after each move |

## Validation Checkpoints

After each MOVE:
- [ ] `./collider full . --output .collider_test` succeeds
- [ ] Self-test passes (no red failures)
- [ ] Selection, file boundaries, UI controls still work
- [ ] No console errors

## Progress Tracking

| Move | Functions | Lines | Status |
|------|-----------|-------|--------|
| Move 1 | 15 | ~565 | **IN PROGRESS** |
| Move 2 | 11 | ~900 | Pending |
| Move 3 | 7 | ~600 | Pending |
| Move 4 | 5 | ~200 | Pending |

## Expected Final State

```
app.js: ~1,500 lines (core orchestration)
├── decompressPayload()
├── initFallback2D()
├── initGraph()
├── runSelfTest()
├── filterGraph()
├── buildHybridGraph()
└── refreshGraph()

selection.js: ~1,100 lines (was 513 + 565)
file-viz.js: ~1,600 lines (enhanced)
ui-builders.js: ~1,000 lines (enhanced)
```

## Commit Strategy

One commit per MOVE:
1. `refactor(viz): Move selection UI to selection.js`
2. `refactor(viz): Move file boundaries to file-viz.js`
3. `refactor(viz): Move UI controls to ui-builders.js`
4. `refactor(viz): Move remaining functions to respective modules`
5. `refactor(viz): Complete app.js modularization (-3,166 lines)`
