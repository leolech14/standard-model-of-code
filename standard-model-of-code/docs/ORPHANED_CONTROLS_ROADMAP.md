# Orphaned Controls Implementation Roadmap

**Status:** Analysis Complete - 46 orphaned controls identified
**Date:** 2026-01-25
**Effort:** 8-12 hours total to implement all orphaned handlers

---

## Overview

46 HTML controls were added to the visualization template but lack JavaScript handlers. This roadmap prioritizes their implementation in phases of increasing effort.

**Quick metrics:**
- 26.1% of template controls are orphaned
- All in 8 functional categories
- 3 new modules needed
- 4 existing modules need enhancement

---

## Phase 1: Quick Wins (30 minutes)

**Goal:** Maximum visual impact with minimal effort
**Target:** Ship numeric display synchronization

### Task 1.1: Numeric Display Sync in circuit-breaker.js

**File:** `src/core/viz/assets/modules/circuit-breaker.js`

**What to do:**
Add numeric display updates to 7 existing slider handlers.

**Current pattern:**
```javascript
{
  id: 'cfg-edge-opacity',
  execute: () => {
    const el = document.getElementById('cfg-edge-opacity');
    el.addEventListener('input', (e) => {
      APPEARANCE_STATE.edgeOpacity = parseFloat(e.target.value);
      updateVisualization();
    });
  }
}
```

**Fixed pattern:**
```javascript
{
  id: 'cfg-edge-opacity',
  execute: () => {
    const el = document.getElementById('cfg-edge-opacity');
    el.addEventListener('input', (e) => {
      APPEARANCE_STATE.edgeOpacity = parseFloat(e.target.value);
      // ADD THIS LINE:
      document.getElementById('cfg-edge-opacity-num').value = e.target.value;
      updateVisualization();
    });
  }
}
```

**Controls to sync:**
1. `cfg-edge-opacity` → `cfg-edge-opacity-num`
2. `cfg-edge-width` → `cfg-edge-width-num`
3. `cfg-edge-curve` → `cfg-edge-curve-num`
4. `cfg-node-opacity` → `cfg-node-opacity-num`
5. `cfg-node-size` → `cfg-node-size-num`
6. `cfg-particle-count` → `cfg-particle-count-num`
7. `cfg-particle-speed` → `cfg-particle-speed-num`

**Estimated time:** 10 minutes
**Verification:** Drag each slider, verify numeric display updates

**Commits:**
```bash
git add src/core/viz/assets/modules/circuit-breaker.js
git commit -m "feat(circuit-breaker): Sync numeric displays with appearance sliders"
```

---

## Phase 2: Filter System (2-3 hours)

**Goal:** Complete the filter UI implementation
**Target:** Make filters fully functional end-to-end

### Task 2.1: Wire Range Slider Value Displays

**File:** `src/core/viz/assets/modules/filter-state.js` or `ui-manager.js`

**New handlers:**
```javascript
{
  id: 'filter-min-degree',
  execute: () => {
    const slider = document.getElementById('filter-min-degree');
    const display = document.getElementById('filter-min-degree-val');

    slider.addEventListener('input', (e) => {
      const value = parseInt(e.target.value);
      filterState.minDegree = value;
      display.textContent = value;
      applyFilters();
    });
  }
}
```

**Controls to implement:**
1. `filter-min-degree` → `filter-min-degree-val`
2. `filter-max-degree` → `filter-max-degree-val`

**Also wire existing toggles:**
3. `filter-hide-dead` - checkbox to toggle dead code filtering
4. `filter-hide-orphans` - checkbox to toggle orphan filtering

**Estimated time:** 20 minutes

### Task 2.2: Implement Chip Selector Handlers

**File:** `src/core/viz/assets/modules/filter-state.js` or new `filter-ui.js`

**Pattern:**
```javascript
{
  id: 'filter-role-chips',
  execute: () => {
    const container = document.getElementById('filter-role-chips');

    container.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;

      const role = chip.dataset.role;
      filterState.toggleRole(role);
      chip.classList.toggle('active', filterState.roles.has(role));
      applyFilters();
    });
  }
}
```

**Controls to implement:**
1. `filter-role-chips` - Semantic role filters
2. `filter-family-chips` - Code family filters
3. `filter-tier-chips` - Atom tier filters

**Estimated time:** 45 minutes

### Task 2.3: Update Active Filter Display

**File:** `src/core/viz/assets/modules/filter-state.js`

**What to do:**
When filters change, update `panel-filter-chips` to show active filters as chips.

**Pattern:**
```javascript
function updateActiveFilterDisplay() {
  const container = document.getElementById('panel-filter-chips');
  if (!container) return;

  container.innerHTML = '';

  // Add chips for each active filter
  filterState.roles.forEach(role => {
    const chip = document.createElement('div');
    chip.className = 'filter-chip';
    chip.textContent = role;
    chip.dataset.type = 'role';
    container.appendChild(chip);
  });

  // Similar for families, tiers, degree ranges, etc.
}
```

**Call this function:**
- After `applyFilters()`
- When filter state changes

**Estimated time:** 30 minutes

**Subtotal Phase 2:** 95 minutes (1.5-2 hours)

**Commits:**
```bash
git add src/core/viz/assets/modules/filter-state.js
git commit -m "feat(filters): Wire UI controls to filter state management"

git add src/core/viz/assets/modules/filter-state.js
git commit -m "feat(filters): Implement chip selector handlers"

git add src/core/viz/assets/modules/filter-state.js
git commit -m "feat(filters): Update active filter display panel"
```

---

## Phase 3: Selection & Stats (1-2 hours)

**Goal:** Complete selection workflow and metric displays
**Target:** Finalize working UI for selection actions and statistics

### Task 3.1: Implement Selection Action Handlers

**File:** `src/core/viz/assets/modules/selection.js`

**New handlers:**
```javascript
{
  id: 'panel-select-clear',
  execute: () => {
    const btn = document.getElementById('panel-select-clear');
    btn.addEventListener('click', () => {
      selectionState.clear();
      updateSelectionPanel();
      updateVisualization();
    });
  }
},
{
  id: 'panel-select-invert',
  execute: () => {
    const btn = document.getElementById('panel-select-invert');
    btn.addEventListener('click', () => {
      selectionState.invert();
      updateSelectionPanel();
      updateVisualization();
    });
  }
}
```

**Controls to implement:**
1. `panel-select-clear` - Clear all selections
2. `panel-select-invert` - Invert current selection
3. `selection-actions` - Container (just needs visibility management)

**Estimated time:** 15 minutes

### Task 3.2: Implement Stats Display Updates

**File:** `src/core/viz/assets/modules/hud.js`

**Pattern:**
```javascript
function updateStatisticsDisplay() {
  const fileCount = graph.nodes.filter(n => n.file_path).length;
  const density = calculateGraphDensity(graph);

  const filesDisplay = document.getElementById('stats-files');
  if (filesDisplay) {
    filesDisplay.querySelector('.value').textContent = fileCount;
  }

  const densityDisplay = document.getElementById('stats-density');
  if (densityDisplay) {
    densityDisplay.querySelector('.value').textContent = density.toFixed(2);
  }
}
```

**Call after:**
- Graph data loads
- Filters applied
- Selection changes

**Controls to implement:**
1. `stats-files` - File count display
2. `stats-density` - Graph density metric

**Estimated time:** 20 minutes

**Subtotal Phase 3:** 35 minutes

**Commits:**
```bash
git add src/core/viz/assets/modules/selection.js
git commit -m "feat(selection): Add clear and invert action handlers"

git add src/core/viz/assets/modules/hud.js
git commit -m "feat(hud): Update statistics displays on data changes"
```

---

## Phase 4: Camera Control System (4-6 hours)

**Goal:** Implement full camera navigation system
**Target:** Complete camera manager with bookmarks and presets

### Task 4.1: Create Camera Manager Module

**File:** `src/core/viz/assets/modules/camera-manager.js` (new)

**Implementation:**
```javascript
export class CameraManager {
  constructor(camera, graph) {
    this.camera = camera;
    this.graph = graph;
    this.bookmarks = this.loadBookmarks();
    this.autoRotateEnabled = false;
    this.autoRotateSpeed = 1;
  }

  // Navigation methods
  zoomIn(factor = 1.2) {
    this.camera.position.multiplyScalar(1 / factor);
  }

  zoomOut(factor = 1.2) {
    this.camera.position.multiplyScalar(factor);
  }

  fitGraph() {
    // Calculate bounding sphere of all nodes
    const bounds = this.calculateGraphBounds();
    this.camera.position.copy(bounds.center);
    this.camera.position.z = bounds.radius * 2;
  }

  reset() {
    this.camera.position.set(0, 0, 150);
    this.camera.lookAt(0, 0, 0);
  }

  // Bookmark management
  saveBookmark(name) {
    const bookmark = {
      position: this.camera.position.clone(),
      rotation: this.camera.quaternion.clone(),
      timestamp: Date.now()
    };
    this.bookmarks[name] = bookmark;
    this.persistBookmarks();
    return true;
  }

  loadBookmark(name) {
    const bookmark = this.bookmarks[name];
    if (!bookmark) return false;

    this.camera.position.copy(bookmark.position);
    this.camera.quaternion.copy(bookmark.rotation);
    return true;
  }

  deleteBookmark(name) {
    delete this.bookmarks[name];
    this.persistBookmarks();
  }

  getBookmarks() {
    return Object.keys(this.bookmarks);
  }

  // Auto-rotation
  enableAutoRotate(speed = 1) {
    this.autoRotateEnabled = true;
    this.autoRotateSpeed = speed;
  }

  disableAutoRotate() {
    this.autoRotateEnabled = false;
  }

  update(deltaTime) {
    if (this.autoRotateEnabled) {
      this.rotateAroundCenter(this.autoRotateSpeed * deltaTime);
    }
  }

  // Persistence
  persistBookmarks() {
    try {
      const data = Object.entries(this.bookmarks).map(([name, bm]) => ({
        name,
        position: bm.position,
        rotation: bm.rotation
      }));
      localStorage.setItem('camera-bookmarks', JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save camera bookmarks:', e);
    }
  }

  loadBookmarks() {
    try {
      const data = JSON.parse(localStorage.getItem('camera-bookmarks')) || [];
      const bookmarks = {};
      data.forEach(item => {
        bookmarks[item.name] = {
          position: new THREE.Vector3(...item.position),
          rotation: new THREE.Quaternion(...item.rotation)
        };
      });
      return bookmarks;
    } catch {
      return {};
    }
  }

  // Helper methods
  calculateGraphBounds() {
    // ... calculate bounding sphere
  }

  rotateAroundCenter(angle) {
    // ... rotate camera around center point
  }
}
```

**Estimated time:** 2-3 hours

### Task 4.2: Wire Camera Control UI

**File:** `src/core/viz/assets/modules/camera-manager.js` (continuation)

**Add initialization function:**
```javascript
export function initCameraControls(cameraManager) {
  // Zoom buttons
  document.getElementById('camera-zoom-in')?.addEventListener('click',
    () => cameraManager.zoomIn()
  );

  document.getElementById('camera-zoom-out')?.addEventListener('click',
    () => cameraManager.zoomOut()
  );

  document.getElementById('camera-zoom-fit')?.addEventListener('click',
    () => cameraManager.fitGraph()
  );

  // Reset
  document.getElementById('camera-reset')?.addEventListener('click',
    () => cameraManager.reset()
  );

  // Auto-rotate
  const autoRotate = document.getElementById('camera-auto-rotate');
  if (autoRotate) {
    autoRotate.addEventListener('change', (e) => {
      if (e.target.checked) {
        const speed = parseFloat(
          document.getElementById('camera-rotate-speed')?.value || 1
        );
        cameraManager.enableAutoRotate(speed);
      } else {
        cameraManager.disableAutoRotate();
      }
    });
  }

  // Rotation speed
  const rotateSpeed = document.getElementById('camera-rotate-speed');
  if (rotateSpeed) {
    rotateSpeed.addEventListener('input', (e) => {
      cameraManager.autoRotateSpeed = parseFloat(e.target.value);
      document.getElementById('camera-rotate-speed-val').textContent = e.target.value;
    });
  }

  // Bookmarks dropdown
  const bookmarkSelect = document.getElementById('camera-bookmarks');
  if (bookmarkSelect) {
    // Populate with saved bookmarks
    updateBookmarkDropdown(cameraManager);

    bookmarkSelect.addEventListener('change', (e) => {
      const name = e.target.value;
      if (name && cameraManager.loadBookmark(name)) {
        e.target.value = '';
      }
    });
  }

  // Save bookmark button
  document.getElementById('camera-save-bookmark')?.addEventListener('click', () => {
    const name = prompt('Save this view as:', `view_${new Date().toLocaleString()}`);
    if (name) {
      cameraManager.saveBookmark(name);
      updateBookmarkDropdown(cameraManager);
      showToast(`Saved view: ${name}`);
    }
  });
}

function updateBookmarkDropdown(cameraManager) {
  const select = document.getElementById('camera-bookmarks');
  if (!select) return;

  const currentValue = select.value;
  select.innerHTML = '<option value="">-- Load Camera View --</option>';

  cameraManager.getBookmarks().forEach(name => {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  });

  select.value = currentValue;
}
```

**Controls to wire:**
1. `camera-zoom-in`
2. `camera-zoom-out`
3. `camera-zoom-fit`
4. `camera-reset`
5. `camera-auto-rotate`
6. `camera-rotate-speed`
7. `camera-rotate-speed-val`
8. `camera-bookmarks`
9. `camera-save-bookmark`

**Estimated time:** 1.5-2 hours

### Task 4.3: Integrate with Main Visualization Loop

**File:** `src/core/viz/assets/modules/main.js`

**What to do:**
1. Create `cameraManager` instance
2. Call `initCameraControls(cameraManager)`
3. Call `cameraManager.update()` in animation loop

**Pattern:**
```javascript
import { CameraManager, initCameraControls } from './camera-manager.js';

function init() {
  // ... existing code ...

  const cameraManager = new CameraManager(camera, graph);
  initCameraControls(cameraManager);

  // Store for later access
  window.cameraManager = cameraManager;
}

function animate() {
  const deltaTime = clock.getDelta();
  cameraManager.update(deltaTime);

  // ... rest of animation loop
}
```

**Estimated time:** 30 minutes

**Subtotal Phase 4:** 4-6 hours

**Commits:**
```bash
git add src/core/viz/assets/modules/camera-manager.js
git commit -m "feat(camera): Add camera manager module with bookmarks and presets"

git add src/core/viz/assets/modules/main.js
git commit -m "feat(camera): Integrate camera manager into visualization loop"
```

---

## Phase 5: Accessibility Features (2-3 hours)

**Goal:** Implement accessibility controls
**Target:** Make visualization accessible to users with different needs

**Optional Phase** - Implement only if accessibility is required for release

### Task 5.1: Create A11y Manager Module

**File:** `src/core/viz/assets/modules/a11y-manager.js` (new)

**Implementation:**
```javascript
export function initA11yControls() {
  // Font size adjustment
  const fontSizeSlider = document.getElementById('a11y-font-size');
  const fontSizeVal = document.getElementById('a11y-font-size-val');

  if (fontSizeSlider) {
    fontSizeSlider.addEventListener('input', (e) => {
      const size = parseInt(e.target.value);
      fontSizeVal.textContent = `${size}px`;
      document.documentElement.style.fontSize = `${size}px`;
      localStorage.setItem('font-size', size);
    });

    // Load saved preference
    const saved = localStorage.getItem('font-size');
    if (saved) {
      fontSizeSlider.value = saved;
      fontSizeSlider.dispatchEvent(new Event('input'));
    }
  }

  // Large text toggle
  const largeText = document.getElementById('a11y-large-text');
  if (largeText) {
    largeText.addEventListener('change', (e) => {
      document.body.classList.toggle('large-text', e.target.checked);
      localStorage.setItem('large-text', e.target.checked);
    });

    const saved = localStorage.getItem('large-text') === 'true';
    if (saved) {
      largeText.checked = true;
      largeText.dispatchEvent(new Event('change'));
    }
  }

  // Focus indicators
  const focusIndicators = document.getElementById('a11y-focus-indicators');
  if (focusIndicators) {
    focusIndicators.addEventListener('change', (e) => {
      document.body.classList.toggle('show-focus', e.target.checked);
      localStorage.setItem('focus-indicators', e.target.checked);
    });

    const saved = localStorage.getItem('focus-indicators') !== 'false';
    if (saved) {
      focusIndicators.checked = true;
      focusIndicators.dispatchEvent(new Event('change'));
    }
  }

  // Screen reader support
  const screenReader = document.getElementById('a11y-screen-reader');
  if (screenReader) {
    screenReader.addEventListener('change', (e) => {
      const enabled = e.target.checked;
      document.body.setAttribute('aria-label',
        enabled ? 'Screen reader enabled' : 'Screen reader disabled'
      );
      localStorage.setItem('screen-reader', enabled);

      // Add aria-labels to interactive elements
      updateAriaLabels(enabled);
    });

    const saved = localStorage.getItem('screen-reader') !== 'false';
    if (saved) {
      screenReader.checked = true;
      screenReader.dispatchEvent(new Event('change'));
    }
  }
}

function updateAriaLabels(enabled) {
  if (!enabled) return;

  // Add aria-labels to all controls
  document.getElementById('cfg-edge-opacity')?.setAttribute('aria-label', 'Edge Opacity');
  // ... more controls
}
```

**Estimated time:** 1.5-2 hours

### Task 5.2: Add A11y Styles

**File:** `src/core/viz/assets/styles.css`

**What to add:**
```css
/* Accessibility mode styles */

body.large-text {
  font-size: 18px !important;
  letter-spacing: 0.05em;
}

body.show-focus {
  --focus-color: #ff00ff;
}

body.show-focus *:focus-visible {
  outline: 3px solid var(--focus-color);
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Estimated time:** 30 minutes

**Subtotal Phase 5:** 2-2.5 hours

**Commits:**
```bash
git add src/core/viz/assets/modules/a11y-manager.js
git commit -m "feat(a11y): Add accessibility controls manager"

git add src/core/viz/assets/styles.css
git commit -m "feat(a11y): Add accessibility mode styles"
```

---

## Phase 6: Polish & Testing (1 hour)

**Goal:** Comprehensive validation and documentation
**Target:** Ensure all handlers work correctly in generated reports

### Task 6.1: Test All Controls

**Procedure:**
1. Generate fresh report: `./collider full . --output .collider`
2. Open `collider_report.html` in browser
3. Test each orphaned control category:
   - [ ] Numeric displays update when sliders move
   - [ ] Filters apply correctly
   - [ ] Selection actions work
   - [ ] Stats display updates
   - [ ] Camera bookmarks save/load
   - [ ] A11y settings persist
4. Check browser console for errors
5. Verify keyboard navigation (Tab, Enter)

**Time:** 20 minutes

### Task 6.2: Update Documentation

**Files to update:**
- `docs/specs/VISUALIZATION_UI_SPEC.md` - Add new controls to spec
- `docs/COLLIDER.md` - Update shortcuts/controls list
- `README.md` - Update feature list if applicable

**Time:** 20 minutes

### Task 6.3: Final Validation

**Checklist:**
- [ ] All 46 orphaned controls now have handlers
- [ ] No JavaScript errors in console
- [ ] All handlers follow circuit-breaker pattern
- [ ] State objects properly updated
- [ ] Visualization updates on all control changes
- [ ] All changes committed to git

**Time:** 20 minutes

**Final commits:**
```bash
git add -A
git commit -m "docs: Update UI documentation and control references"

git add -A
git commit -m "test: Validate all orphaned control handlers in generated report"
```

---

## Implementation Timeline

| Phase | Tasks | Effort | Total |
|-------|-------|--------|-------|
| 1 | Numeric sync | 30 min | 30 min |
| 2 | Filters | 95 min | 2h 5m |
| 3 | Selection/Stats | 35 min | 1h 40m |
| 4 | Camera system | 4-6h | 4-6h |
| 5 | A11y (optional) | 2-2.5h | 2-2.5h |
| 6 | Polish/Testing | 60 min | 1h |
| **Total** | **All phases** | **8-12h** | **8-12h** |

**Recommended approach:**
1. Do Phase 1 immediately (30 min, high impact)
2. Do Phase 2-3 together (3-4 hours, user-facing features)
3. Do Phase 4 if camera navigation is priority (4-6 hours)
4. Do Phase 5 only if accessibility required (2-2.5 hours)
5. Do Phase 6 always (1 hour, validation)

---

## Success Criteria

### Phase 1 Complete
- [ ] All 14 numeric displays update when sliders move
- [ ] No visual inconsistencies
- [ ] No console errors

### Phase 2 Complete
- [ ] Filter UI fully functional
- [ ] All chip selectors work
- [ ] Active filter display updates

### Phase 3 Complete
- [ ] Selection clear/invert buttons work
- [ ] Stats displays show correct values
- [ ] Updates trigger on relevant events

### Phase 4 Complete
- [ ] All 9 camera controls functional
- [ ] Camera bookmarks save to localStorage
- [ ] Auto-rotation works smoothly

### Phase 5 Complete
- [ ] A11y settings persist in localStorage
- [ ] Font size adjustable
- [ ] Focus indicators toggle works

### Phase 6 Complete
- [ ] All tests pass
- [ ] Documentation up-to-date
- [ ] All commits clean and well-documented

---

## Risk Mitigation

### Potential Issues

1. **State object conflicts**
   - Risk: Multiple handlers updating same state
   - Mitigation: Use existing state object patterns
   - Test: Verify state consistency in DevTools

2. **Performance degradation**
   - Risk: Too many event listeners
   - Mitigation: Use delegation where possible
   - Test: Monitor FPS with perf-frame

3. **Bookmark persistence**
   - Risk: localStorage quota exceeded
   - Mitigation: Limit bookmarks to 10, gzip if needed
   - Test: Save many bookmarks, verify limit enforced

4. **Camera animation conflicts**
   - Risk: Multiple camera updates collide
   - Mitigation: Single camera update queue
   - Test: Rapid camera changes don't break view

---

## References

1. **Audit Report:** `/docs/reports/ORPHANED_UI_CONTROLS_AUDIT.md`
2. **Quick Reference:** `/docs/reports/ORPHANED_CONTROLS_QUICK_REFERENCE.txt`
3. **Implementation Patterns:** `/docs/patterns/UI_HANDLER_IMPLEMENTATION_PATTERNS.md`
4. **Circuit Breaker Example:** `src/core/viz/assets/modules/circuit-breaker.js` (lines 77-1260)
5. **Filter State:** `src/core/viz/assets/modules/filter-state.js`
6. **Selection State:** `src/core/viz/assets/modules/selection.js`

---

## Notes

- All code should follow existing module patterns
- Use circuit-breaker.js as the primary reference
- Test in generated HTML reports, not source files
- Commit frequently (one feature per commit)
- Update CHANGELOG.md with major additions

This roadmap is executable as-is. Each phase is independent and can be tackled separately.
