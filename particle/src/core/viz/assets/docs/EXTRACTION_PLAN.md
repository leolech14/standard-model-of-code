# app.js Extraction Plan

> **⚠️ HISTORICAL DOCUMENT** - This plan was created when app.js was 5,337 lines.
> As of 2026-01-21, app.js is now **3,109 lines** (42% reduction).
> Many items marked "TODO" have been completed. Line numbers are outdated.
> This document is kept for reference only.

**Source:** `app.js` (5,337 → 3,109 lines)
**Goal:** Extract everything possible into dedicated modules
**Date:** 2026-01-21 (original), updated 2026-01-21

---

## Current State Analysis

| Metric | Value |
|--------|-------|
| Total Lines | 5,337 |
| Functions | ~50 |
| Global Variables | ~100 |
| Classes | 3 (RuntimeRegistry, UIManager, PanelManager) |

---

## Extraction Matrix

### Phase 1: Self-Contained Classes (No Dependencies)

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `RuntimeRegistry` class | 311-374 | NEW `registry.js` | TODO |
| `PERF_MONITOR` object | 83-174 | NEW `perf-monitor.js` | TODO |
| `UIManager` object | 2290-2550 | NEW `ui-manager.js` | TODO |
| `PanelManager` object | 5080-5300 | EXISTING `panels.js` | TODO |

### Phase 2: Config/State Objects

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `THEME_CONFIG` | 189-199 | NEW `config.js` | TODO |
| `EDGE_MODE_CONFIG` | 204-211 | `edge-system.js` | TODO |
| `NODE_COLOR_CONFIG` | 215 | `color-engine.js` | TODO |
| `APPEARANCE_STATE` | 270-295 | NEW `state.js` or `vis-state.js` | TODO |
| `SIDEBAR_STATE` | 266-269 | `sidebar.js` | TODO |
| `VIS_FILTERS` | 249-265 | `vis-state.js` | TODO |
| `COLOR_TWEAKS` | 244-248 | `color-engine.js` | TODO |

### Phase 3: Theory Constants

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `SCALE_16_LEVELS` | 2658-2681 | NEW `theory.js` | TODO |
| `THREE_LAYERS` | 2683-2692 | `theory.js` | TODO |
| `SMC_THEORY` | 2694-2823 | `theory.js` | TODO |
| `LEVEL_ZONES` | 2830-2843 | `theory.js` | TODO |
| `VIS_PRESETS` | 2845-3330 | `theme.js` or NEW `presets.js` | TODO |

### Phase 4: Physics/Animation

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `PHYSICS_STATE` | 3332-3337 | `physics.js` | TODO |
| `PHYSICS_PRESETS` | 3339-3356 | `physics.js` | TODO |
| Preset grid setup | 3358-3413 | `physics.js` | TODO |
| Layout grid setup | 3415-3480 | `layout.js` | TODO |

### Phase 5: Edge System

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `EDGE_MODE_ORDER` | 3483-3491 | `edge-system.js` | TODO |
| `EDGE_MODE_LABELS` | 3493-3501 | `edge-system.js` | TODO |
| `EDGE_MODE_HINTS` | 3503-3513 | `edge-system.js` | TODO |
| `GRADIENT_PALETTES` | 3515-3568 | `edge-system.js` | TODO |
| `applyEdgeStyle()` | 2250-2288 | `edge-system.js` | TODO |

### Phase 6: Selection System

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `formatCountList()` | 3653-3655 | `selection.js` | TODO |
| `appendSelectionRow()` | 3657-3668 | `selection.js` | TODO |
| `updateSelectionPanel()` | 3670-3762 | `selection.js` | TODO |
| `showSelectionModal()` | 3764-3880 | `selection.js` | TODO |
| `hideSelectionModal()` | 3882-3885 | `selection.js` | TODO |
| `initSelectionModal()` | 3887-3929 | `selection.js` | TODO |
| `updateOverlayScale()` | 3931-3941 | `selection.js` | TODO |
| `ensureNodeOverlays()` | 3943-4000 | `selection.js` | TODO |
| `updateSelectionVisuals()` | 4002-4087 | `selection.js` | TODO |
| `syncSelectionAfterGraphUpdate()` | 4089-4107 | `selection.js` | TODO |
| `updateSelectionBox()` | 4109-4118 | `selection.js` | TODO |
| `getNodeScreenPosition()` | 4120-4129 | `selection.js` | TODO |
| `selectNodesInBox()` | 4131-4146 | `selection.js` | TODO |
| `setupSelectionInteractions()` | 4148-4208 | `selection.js` | TODO |
| `initSelectionState()` | 4210-4217 | `selection.js` | TODO |

### Phase 7: File Visualization

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `toggleFileExpand()` | 4289-4307 | `file-viz.js` | TODO |
| `drawFileBoundaries()` | 4309-4617 | `file-viz.js` | TODO |
| `buildDirectoryTree()` | 4619-4649 | `file-viz.js` | TODO |
| `computeFileActivity()` | 4651-4672 | `file-viz.js` | TODO |
| `drawContainmentSpheres()` | 4674-4770 | `file-viz.js` | TODO |
| `startContainmentAnimation()` | 4772-4852 | `file-viz.js` | TODO |
| `stopContainmentAnimation()` | 4854-4863 | `file-viz.js` | TODO |
| `popBoundaries()` | 4865-4919 | `file-viz.js` | TODO |
| `restoreBoundaries()` | 4921-5033 | `file-viz.js` | TODO |
| `updateExpandButtons()` | 5035-5066 | `file-viz.js` | TODO |
| `handleCmdFiles()` | 5068-5071 | `file-viz.js` | TODO |
| `FILE_CONTAINMENT` object | 4602-4617 | `file-viz.js` | TODO |

### Phase 8: Hover/Interaction

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `handleNodeHover()` | 4219-4272 | `hover.js` | TODO |
| `handleNodeClick()` | 4274-4287 | `hover.js` | TODO |
| `TOOLTIP_STATE` | 2825-2828 | `tooltips.js` | TODO |

### Phase 9: UI Controls Setup

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `initCommandBar()` | 699-898 | `control-bar.js` | TODO |
| `buildChipGroup()` | 900-944 | `control-bar.js` | TODO |
| `populateFilterChips()` | 946-1014 | `control-bar.js` | TODO |
| `setupControls()` | 2032-2060 | `control-bar.js` | TODO |
| `setupConfigControls()` | 2062-2248 | `control-bar.js` | TODO |
| `buildMetadataControls()` | 2983-3002 | `control-bar.js` | TODO |
| `buildAppearanceSliders()` | 3004-3330 | `control-bar.js` | TODO |
| Button event wiring | 3570-3624 | `control-bar.js` | TODO |

### Phase 10: Flow/Dimension

| Extract | Lines | Target Module | Status |
|---------|-------|---------------|--------|
| `handleCmdFlow()` | 5073 | `flow.js` | TODO |
| `handleCmd3d()` | 5074 | `dimension.js` | TODO |
| `flowMode` variable | 306 | `flow.js` | TODO |

---

## What Stays in app.js (Integration Layer)

These functions ARE the integration layer and should remain:

| Function | Lines | Reason |
|----------|-------|--------|
| `decompressPayload()` | 33-50 | Bootstrap |
| Worker setup | 15-30 | Bootstrap |
| `initGraph()` | 1167-1645 | Core orchestration |
| `initFallback2D()` | 1016-1165 | Fallback mode |
| `runSelfTest()` | 1647-1831 | Diagnostics |
| `filterGraph()` | 1833-1954 | Core filtering |
| `buildHybridGraph()` | 1956-2030 | Graph construction |
| `refreshGraph()` | 2560-2656 | Core refresh |
| DOMContentLoaded handler | Various | Bootstrap |
| Global variable declarations | 52-78 | Module coordination |

---

## New Modules to Create

| Module | Content | Est. Lines |
|--------|---------|------------|
| `registry.js` | RuntimeRegistry class | ~70 |
| `perf-monitor.js` | PERF_MONITOR object | ~100 |
| `ui-manager.js` | UIManager object | ~300 |
| `config.js` | THEME_CONFIG, default configs | ~100 |
| `state.js` | APPEARANCE_STATE, global state | ~100 |
| `theory.js` | SMC_THEORY, SCALE_16_LEVELS, THREE_LAYERS | ~200 |
| `presets.js` | VIS_PRESETS | ~500 |

---

## Estimated Result

| Metric | Before | After |
|--------|--------|-------|
| app.js lines | 5,337 | ~1,500 |
| Total modules | 34 | 41 |
| Extractable code | - | ~3,800 lines |

---

## Execution Order

1. **Phase 1** - Self-contained classes (safest, no deps)
2. **Phase 2** - Config objects (state management)
3. **Phase 3** - Theory constants (pure data)
4. **Phase 4** - Physics/Animation (already have modules)
5. **Phase 5** - Edge system (extend existing module)
6. **Phase 6** - Selection system (extend existing module)
7. **Phase 7** - File visualization (extend existing module)
8. **Phase 8** - Hover/Interaction (extend existing module)
9. **Phase 9** - UI Controls (extend existing module)
10. **Phase 10** - Flow/Dimension (extend existing modules)

---

## Risk Mitigation

- **Test after each phase** - run `./collider full . --output .collider_test`
- **Preserve backward compatibility** - use `Object.defineProperty` for globals
- **Commit after each phase** - easy rollback
