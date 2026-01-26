# Orphaned UI Controls Audit Report

**Date:** 2026-01-25
**Analysis:** Deep handler coverage analysis across all JavaScript modules
**Tool:** Python regex analysis + manual validation

---

## Executive Summary

Found **46 truly orphaned controls** in the visualization template with ZERO handler bindings in any JavaScript module, plus app.js.

These controls exist in HTML but have no:
- `getElementById()` references
- `querySelector()` references
- Inline event handlers (`onclick`, `onchange`, etc.)
- Event listener bindings
- Any programmatic access

The orphaned controls fall into 8 functional categories representing incomplete feature implementations.

---

## Methodology

### Handler Coverage Analysis

1. **Template Analysis:** Extracted 176 total IDs from `template.html`
2. **Module Scan:** Searched 69 JavaScript modules for handler bindings
3. **Pattern Matching:** Checked for:
   - `document.getElementById("control-id")`
   - `document.querySelector("#control-id")`
   - `document.querySelector(".control-id")`
   - String literals matching control IDs
4. **Validation:** Confirmed orphans have NO references in any JS file
5. **app.js Check:** Only 1 orphan (`toggle-labels`) referenced in legacy app.js

**Result:** 46 controls with zero handlers

---

## Orphaned Controls by Category

### 1. Accessibility Controls (5 orphaned)

These controls were planned for a11y features but never implemented.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `a11y-focus-indicators` | `<input>` | Show focus indicators | Dead |
| `a11y-font-size` | `<input range>` min=12 max=24 | Font size slider | Dead |
| `a11y-font-size-val` | Display element | Show current font size | Dead |
| `a11y-large-text` | `<input>` | Toggle large text mode | Dead |
| `a11y-screen-reader` | `<input>` | Screen reader support toggle | Dead |

**Impact:** No accessibility features implemented in the visualization

**Recommendation:** Either:
- Remove from template (clean up)
- Implement handlers in new a11y module
- Mark as "future feature" in docs

---

### 2. Camera Controls (9 orphaned)

Navigation/camera manipulation features that were designed but not implemented.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `camera-auto-rotate` | `<input>` | Toggle auto rotation | Dead |
| `camera-bookmarks` | `<select>` | Save/restore camera positions | Dead |
| `camera-reset` | Button | Reset to default view | Dead |
| `camera-rotate-speed` | Range slider | Control rotation speed | Dead |
| `camera-rotate-speed-val` | Display | Show current speed | Dead |
| `camera-save-bookmark` | Button | Save current camera angle | Dead |
| `camera-zoom-fit` | Button | Zoom to fit graph | Dead |
| `camera-zoom-in` | Button | Zoom in | Dead |
| `camera-zoom-out` | Button | Zoom out | Dead |

**Impact:** Limited camera control (only pan/zoom work via mouse)

**Architecture Gap:** No camera state management module
- No persistent bookmark system
- No preset angles/views
- No auto-rotation engine

**Recommendation:**
- Implement `camera-manager.js` module with full bookmark/preset system
- Integrate with `InteractionManager.js`
- Or remove if not planned for MVP

---

### 3. Config Display Numeric Inputs (14 orphaned)

These are read-only numeric displays that show current configuration values. They are "display mirrors" for sliders.

| Control ID | Associated Slider | Purpose | Status |
|------------|------------------|---------|--------|
| `cfg-edge-curve-num` | `cfg-edge-curve` | Show edge curve value | Dead |
| `cfg-edge-opacity-num` | `cfg-edge-opacity` | Show edge opacity value | Dead |
| `cfg-edge-width-num` | `cfg-edge-width` | Show edge width value | Dead |
| `cfg-label-size-num` | (no main slider?) | Show label size value | Dead |
| `cfg-node-opacity-num` | `cfg-node-opacity` | Show node opacity value | Dead |
| `cfg-node-res-num` | (no main slider?) | Show node resolution value | Dead |
| `cfg-node-size-num` | `cfg-node-size` | Show node size value | Dead |
| `cfg-particle-count-num` | `cfg-particle-count` | Show particle count | Dead |
| `cfg-particle-speed-num` | `cfg-particle-speed` | Show particle speed | Dead |
| `edge-opacity-num` | `edge-opacity` | Show edge opacity (duplicate?) | Dead |
| `node-size-num` | `node-size` | Show node size (duplicate?) | Dead |
| `physics-center-num` | (no main slider?) | Show physics center value | Dead |
| `physics-charge-num` | `physics-charge` | Show physics charge value | Dead |
| `physics-link-num` | `physics-link-distance` | Show physics link value | Dead |

**Architecture Pattern:** In `circuit-breaker.js`, config handlers sync bidirectionally:
```javascript
const el = document.getElementById('cfg-edge-opacity');
el.addEventListener('input', (e) => {
  APPEARANCE_STATE.edgeOpacity = parseFloat(e.target.value);
  updateVisualization();
});
```

These `*-num` controls should ALSO update when the slider changes:
```javascript
// Currently missing:
document.getElementById('cfg-edge-opacity-num').textContent = e.target.value;
```

**Impact:** UI is visually incomplete (missing value displays)

**Recommendation:**
- Implement numeric sync handlers
- Or remove `-num` elements from template
- Pattern: Each slider should update its `-num` counterpart

---

### 4. Filter Controls (10 orphaned)

Filter UI that was designed but not wired to the filter state management.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `filter-family-chips` | Container | Show/select code families | Dead |
| `filter-hide-dead` | Checkbox | Hide dead code nodes | Dead |
| `filter-hide-orphans` | Checkbox | Hide orphan nodes | Dead |
| `filter-max-degree` | Range slider | Maximum node degree filter | Dead |
| `filter-max-degree-val` | Display | Show current max degree | Dead |
| `filter-min-degree` | Range slider | Minimum node degree filter | Dead |
| `filter-min-degree-val` | Display | Show current min degree | Dead |
| `filter-role-chips` | Container | Show/select semantic roles | Dead |
| `filter-tier-chips` | Container | Show/select atom tiers | Dead |
| `panel-filter-chips` | Container | Show active filter chips | Dead |

**Partial Implementation:**
- `filter-state.js` exists and manages filter logic
- `ui-manager.js` has SOME filter handlers
- But many filter UI elements are not wired

**Gap Analysis:**
- Degree range filters (`min`/`max`) - no handlers
- Chip selector UI - no click handlers to toggle filters
- Active filter display (`panel-filter-chips`) - not updated when filters change

**Recommendation:**
- Wire missing handlers in `ui-manager.js` or new `filter-ui.js`
- Implement chip click handlers
- Sync `panel-filter-chips` on filter state changes

---

### 5. Physics Simulation Controls (3 orphaned)

Physics parameters that lack numeric displays or handlers.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `physics-center-num` | Display | Show physics center value | Dead |
| `physics-charge-num` | Display | Show charge repulsion value | Dead |
| `physics-link-num` | Display | Show link distance value | Dead |

**Note:** The main sliders exist and ARE handled in `circuit-breaker.js`:
- `physics-charge` → synced
- `physics-link-distance` → synced
- `physics-gravity` → synced
- `physics-collision` → synced

**Gap:** Numeric display mirrors not synced

**Recommendation:** Wire numeric displays (same pattern as config controls)

---

### 6. Statistics/Metrics Display (2 orphaned)

Stat panels that should show live metrics.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `stats-density` | Display | Show graph density metric | Dead |
| `stats-files` | Display | Show file count stat | Dead |

**Context:** Other stat displays ARE implemented:
- `stat-nodes` → handled
- `stat-entropy` → handled
- `stat-edges` → handled

**Gap:** These two specific stat displays are missing handlers

**Recommendation:** Add handlers in `hud.js` or stats module to update on data changes

---

### 7. Selection/Panel Actions (3 orphaned)

Action buttons for node/edge selection state management.

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `panel-select-clear` | Button | Clear all selections | Dead |
| `panel-select-invert` | Button | Invert selection | Dead |
| `selection-actions` | Container | Wrap for selection action buttons | Dead |

**Context:** Related selection controls ARE implemented:
- `selection-title` → handled
- `selection-panel` → handled
- `selection-modal-overlay` → handled

**Gap:** These specific action buttons have no click handlers

**Recommendation:** Implement in `selection.js` module

---

### 8. Miscellaneous Controls (3 orphaned)

| Control ID | HTML Element | Purpose | Status |
|------------|--------------|---------|--------|
| `perf-frame` | Display | Show current FPS/frame metrics | Dead |
| `section-appearance` | Container | Section header/toggle | Dead |
| `toggle-labels` | Checkbox | Toggle node labels | PARTIAL |

**`toggle-labels` Status:**
- Referenced in legacy `app.js` (1 match found)
- NOT referenced in any module JS
- Likely dead code from old implementation

**Recommendation:**
- Implement label toggle handler in `ui-manager.js` or `InteractionManager.js`
- Or remove if using different approach

---

## Handler Implementation Patterns

### How Circuit Breaker Implements Controls

File: `src/core/viz/assets/modules/circuit-breaker.js`

**Pattern A: Toggle with state sync**
```javascript
{
  id: 'panel-toggle-arrows',
  execute: () => {
    const el = document.getElementById('panel-toggle-arrows');
    el.addEventListener('change', (e) => {
      APPEARANCE_STATE.showArrows = e.target.checked;
      updateVisualization();
    });
  }
}
```

**Pattern B: Range slider with state sync**
```javascript
{
  id: 'cfg-edge-opacity',
  execute: () => {
    const el = document.getElementById('cfg-edge-opacity');
    el.addEventListener('input', (e) => {
      APPEARANCE_STATE.edgeOpacity = parseFloat(e.target.value);
      // Missing: update numeric display
      // document.getElementById('cfg-edge-opacity-num').textContent = e.target.value;
      updateVisualization();
    });
  }
}
```

### What's Missing

1. **Numeric Display Sync:** Sliders don't update their `-num` counterparts
2. **Filter UI:** No handlers to toggle filter chips
3. **Camera:** No camera state or bookmark system
4. **Selection Actions:** No clear/invert handlers
5. **Accessibility:** No a11y module at all

---

## Impact Assessment

### Severity: HIGH

**46 dead controls = incomplete feature implementations**

These aren't minor bugs—they represent:
- Unfinished UI/UX designs
- Missing state management modules
- Broken user workflows

### Risk Areas

1. **User Confusion:** Controls render but don't work
2. **Performance:** Some controls (filters, camera) could help optimize viewport
3. **Accessibility:** a11y controls missing entirely
4. **Maintenance:** Dead HTML clutters template

### Non-Critical Status

None of these are BLOCKING current visualization—the core 3D graph, basic controls, and file tree work. But these are table-stakes features for a production release.

---

## Recommended Actions (Priority Order)

### Phase 1: Quick Wins (1-2 hours)

1. **Numeric Display Sync**
   - Wire `-num` inputs to update when main sliders change
   - Affects 14 controls
   - Low risk, high polish

2. **Remove Dead A11y Controls**
   - Delete 5 a11y HTML elements from template
   - Or add `disabled` attribute + docs saying "future feature"
   - Reduces confusion

### Phase 2: Feature Completion (4-6 hours)

3. **Implement Filter UI**
   - Wire chip selectors in `ui-manager.js`
   - Sync `panel-filter-chips` on state changes
   - Affects 10 controls

4. **Implement Selection Actions**
   - Add `clear` and `invert` handlers in `selection.js`
   - Affects 3 controls

5. **Implement Stats Display**
   - Add handlers to update `stats-density` and `stats-files`
   - Affects 2 controls

### Phase 3: Advanced Features (8-12 hours)

6. **Implement Camera System**
   - Create `camera-manager.js` module
   - Bookmark/preset system
   - Auto-rotate engine
   - Affects 9 controls

7. **Implement Performance Monitor**
   - FPS counter in `perf-frame`
   - Integrate with existing perf tracking

### Phase 4: Polish

8. **Accessibility Module**
   - Implement a11y handlers
   - Or remove controls if not planned
   - Affects 5 controls

---

## Orphaned Controls Inventory

### Complete List (46 controls)

**Accessibility (5):**
- a11y-focus-indicators
- a11y-font-size
- a11y-font-size-val
- a11y-large-text
- a11y-screen-reader

**Camera (9):**
- camera-auto-rotate
- camera-bookmarks
- camera-reset
- camera-rotate-speed
- camera-rotate-speed-val
- camera-save-bookmark
- camera-zoom-fit
- camera-zoom-in
- camera-zoom-out

**Config Display (14):**
- cfg-edge-curve-num
- cfg-edge-opacity-num
- cfg-edge-width-num
- cfg-label-size-num
- cfg-node-opacity-num
- cfg-node-res-num
- cfg-node-size-num
- cfg-particle-count-num
- cfg-particle-speed-num
- edge-opacity-num
- node-size-num
- physics-center-num
- physics-charge-num
- physics-link-num

**Filters (10):**
- filter-family-chips
- filter-hide-dead
- filter-hide-orphans
- filter-max-degree
- filter-max-degree-val
- filter-min-degree
- filter-min-degree-val
- filter-role-chips
- filter-tier-chips
- panel-filter-chips

**Stats (2):**
- stats-density
- stats-files

**Selection (3):**
- panel-select-clear
- panel-select-invert
- selection-actions

**Other (3):**
- perf-frame
- section-appearance
- toggle-labels

---

## Implementation Notes for Developers

### When Adding Handlers

1. **Use circuit-breaker.js as template** for control registration
2. **Always create state binding** - don't just add event listeners
3. **Update numeric displays** - if slider exists, `-num` display should too
4. **Test in dev tools** - verify `getElementById` actually finds element
5. **Use synchronous pattern** - event → state → visualization

### Module Responsibility Map

| Category | Primary Module | Secondary |
|----------|----------------|-----------|
| Appearance sliders | `circuit-breaker.js` | `ui-manager.js` |
| Filters | `filter-state.js` | `ui-manager.js` |
| Selection | `selection.js` | `panel-handlers.js` |
| Camera | (needs new) `camera-manager.js` | - |
| Stats | `hud.js` | `report.js` |
| A11y | (needs new) `a11y-manager.js` | - |
| Performance | `perf-monitor.js` | `hud.js` |

---

## Conclusion

**46 orphaned controls represent incomplete implementations across 8 functional areas.**

This is not a "defect"—it's a design/implementation gap. These controls were added to the HTML template but the handlers were never written.

**Recommendation:** Treat as technical debt. Prioritize numeric display sync (quick win) and filter UI completion (user-facing feature).

---

## References

- **Template:** `/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/src/core/viz/assets/template.html`
- **Circuit Breaker:** `/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/src/core/viz/assets/modules/circuit-breaker.js`
- **Filter State:** `/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/src/core/viz/assets/modules/filter-state.js`
- **Modules Directory:** `/Users/lech/PROJECTS_all/PROJECT_elements/standard-model-of-code/src/core/viz/assets/modules/` (69 files)
