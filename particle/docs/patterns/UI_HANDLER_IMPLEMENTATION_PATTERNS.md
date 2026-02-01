# UI Handler Implementation Patterns

Reference guide for implementing handlers for orphaned controls.

---

## Standard Control Handler Pattern (Circuit Breaker)

All control handlers in the visualization follow this pattern defined in `circuit-breaker.js`:

```javascript
{
  id: 'control-name',

  // Validate element exists
  validate: () => document.getElementById('control-name') !== null,

  // Initialize the handler
  execute: () => {
    const el = document.getElementById('control-name');

    // Bind event listener
    el.addEventListener('change', (e) => {
      // Update state
      STATE_OBJECT.property = e.target.value;

      // Trigger visualization update
      updateVisualization();
    });
  },

  // Optional: Cleanup on shutdown
  cleanup: () => {
    const el = document.getElementById('control-name');
    el?.removeEventListener('change', handler);
  }
}
```

---

## Pattern 1: Numeric Input Sync (QUICK WIN)

**Use case:** Slider + numeric display that shows the slider's value

**Problem:** User moves slider, but numeric display doesn't update

**Solution:** Sync the numeric display when slider changes

### Example: Edge Opacity

**Template HTML:**
```html
<input id="cfg-edge-opacity" type="range" min="0" max="1" step="0.05" value="0.8">
<input id="cfg-edge-opacity-num" type="number" min="0" max="1" step="0.05" value="0.8" readonly>
```

**Current handler (in circuit-breaker.js):**
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

**Fixed handler:**
```javascript
{
  id: 'cfg-edge-opacity',
  execute: () => {
    const el = document.getElementById('cfg-edge-opacity');
    const numEl = document.getElementById('cfg-edge-opacity-num'); // ADD THIS

    el.addEventListener('input', (e) => {
      APPEARANCE_STATE.edgeOpacity = parseFloat(e.target.value);

      // ADD THIS: Sync numeric display
      numEl.value = e.target.value;

      updateVisualization();
    });
  }
}
```

**How to apply to all 14 orphaned `-num` controls:**

For each pair:
1. Find main slider in `circuit-breaker.js` (e.g., `cfg-edge-opacity`)
2. Inside the `input` event listener
3. Add 1 line to sync the numeric display:
   ```javascript
   document.getElementById('cfg-edge-opacity-num').value = e.target.value;
   ```

**Affected controls:**
```
cfg-edge-curve          → cfg-edge-curve-num
cfg-edge-opacity        → cfg-edge-opacity-num
cfg-edge-width          → cfg-edge-width-num
cfg-node-opacity        → cfg-node-opacity-num
cfg-node-size           → cfg-node-size-num
cfg-particle-count      → cfg-particle-count-num
cfg-particle-speed      → cfg-particle-speed-num
physics-charge          → physics-charge-num
physics-link-distance   → physics-link-num
```

Plus derived ones:
- `edge-opacity` → `edge-opacity-num`
- `node-size` → `node-size-num`
- `physics-gravity` → `physics-center-num`

**Effort:** 10 minutes
**Files to modify:** `circuit-breaker.js` (1 file)
**Tests:** Verify numeric display updates when you move each slider

---

## Pattern 2: Range Slider with Value Display

**Use case:** Range slider with a separate display showing current value

**Problem:** Value display exists but isn't updated

**Solution:** Create handler that updates display on slider change

### Example: Filter Minimum Degree

**Template HTML:**
```html
<label>Min Degree</label>
<input id="filter-min-degree" type="range" min="0" max="50" value="0">
<span id="filter-min-degree-val">0</span>
```

**Handler pattern:**
```javascript
{
  id: 'filter-min-degree',
  execute: () => {
    const slider = document.getElementById('filter-min-degree');
    const display = document.getElementById('filter-min-degree-val');

    slider.addEventListener('input', (e) => {
      const value = parseInt(e.target.value);

      // Update state (in filter-state.js pattern)
      filterState.minDegree = value;

      // Update display
      display.textContent = value;

      // Apply filter
      applyFilters();
    });
  }
}
```

**Affected controls:**
- `filter-min-degree` ↔ `filter-min-degree-val`
- `filter-max-degree` ↔ `filter-max-degree-val`
- `camera-rotate-speed` ↔ `camera-rotate-speed-val`
- `a11y-font-size` ↔ `a11y-font-size-val`

---

## Pattern 3: Toggle/Checkbox Handler

**Use case:** Simple checkbox that enables/disables a feature

**Problem:** Checkbox exists but has no event handler

**Solution:** Add change listener that updates state

### Example: Hide Dead Code

**Template HTML:**
```html
<input id="filter-hide-dead" type="checkbox">
<label for="filter-hide-dead">Hide Dead Code</label>
```

**Handler pattern:**
```javascript
{
  id: 'filter-hide-dead',
  execute: () => {
    const el = document.getElementById('filter-hide-dead');

    el.addEventListener('change', (e) => {
      // Update filter state
      filterState.hideDead = e.target.checked;

      // Apply changes
      applyFilters();
    });
  }
}
```

**Affected controls:**
- `filter-hide-dead`
- `filter-hide-orphans`
- `camera-auto-rotate`
- `a11y-focus-indicators`
- `a11y-large-text`
- `a11y-screen-reader`
- `toggle-labels`

---

## Pattern 4: Button Click Handler

**Use case:** Button that triggers an action

**Problem:** Button exists but click handler not implemented

**Solution:** Add click listener with action handler

### Example: Clear Selection

**Template HTML:**
```html
<button id="panel-select-clear">Clear</button>
<button id="panel-select-invert">Invert</button>
```

**Handler pattern:**
```javascript
{
  id: 'panel-select-clear',
  execute: () => {
    const btn = document.getElementById('panel-select-clear');

    btn.addEventListener('click', () => {
      // Get current selection state
      const selected = selectionState.getSelected();

      // Clear it
      selectionState.clear();

      // Update UI
      updateSelectionPanel();
      updateVisualization();
    });
  }
}
```

**Affected controls:**
- `panel-select-clear` - Action: clear all selections
- `panel-select-invert` - Action: invert current selection
- `camera-reset` - Action: reset to default view
- `camera-zoom-fit` - Action: zoom to fit graph
- `camera-zoom-in` - Action: zoom in by 20%
- `camera-zoom-out` - Action: zoom out by 20%
- `camera-save-bookmark` - Action: save current camera angle
- `stats-density` - Not a button, display only

---

## Pattern 5: Chip/Chip Container Handler

**Use case:** Multiple clickable chips to toggle filters

**Problem:** Chip container exists but chips have no click handlers

**Solution:** Implement delegation handler on container

### Example: Filter Role Chips

**Template HTML:**
```html
<div id="filter-role-chips" class="chip-container">
  <div class="chip" data-role="utility">Utility</div>
  <div class="chip" data-role="orchestrator">Orchestrator</div>
  <div class="chip" data-role="hub">Hub</div>
  <div class="chip" data-role="leaf">Leaf</div>
</div>
```

**Handler pattern:**
```javascript
{
  id: 'filter-role-chips',
  execute: () => {
    const container = document.getElementById('filter-role-chips');

    // Delegation: listen on container, identify chips by click
    container.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;

      const role = chip.dataset.role;

      // Toggle this role in filter
      filterState.toggleRole(role);

      // Update visual state (active/inactive)
      chip.classList.toggle('active', filterState.roles.has(role));

      // Apply filters
      applyFilters();
    });
  }
}
```

**Affected controls:**
- `filter-role-chips` - Toggle semantic role filters
- `filter-family-chips` - Toggle code family filters
- `filter-tier-chips` - Toggle atom tier filters
- `panel-filter-chips` - Display active filters (read-only, update pattern below)

---

## Pattern 6: Display Element Update Handler

**Use case:** Read-only display that shows computed/live metrics

**Problem:** Display element exists but never updated

**Solution:** Add update handler called from state change events

### Example: File Count Stats

**Template HTML:**
```html
<div id="stats-files">
  <span class="label">Files:</span>
  <span class="value">0</span>
</div>
```

**Handler pattern (called from data refresh):**
```javascript
// In hud.js or wherever stats are computed:

function updateStatsDisplay() {
  // Compute metrics
  const fileCount = graph.nodes.filter(n => n.file_path).length;
  const density = calculateDensity(graph);

  // Update displays
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

**Call this function:**
- When graph data loads
- When filters are applied
- When selection changes
- When zooming/navigating

**Affected controls (display-only):**
- `stats-files`
- `stats-density`
- `perf-frame` (FPS counter)
- All `-num` numeric displays (use Pattern 1 instead)

---

## Pattern 7: Dropdown/Select Handler

**Use case:** Select dropdown to choose from options

**Problem:** Dropdown exists but change handler not wired

**Solution:** Add change listener that applies selection

### Example: Camera Bookmarks

**Template HTML:**
```html
<select id="camera-bookmarks" class="select-input">
  <option value="">-- Save/Load Camera --</option>
  <option value="front">Front View</option>
  <option value="top">Top View</option>
  <option value="iso">Isometric</option>
  <option value="custom1">Custom 1</option>
</select>
```

**Handler pattern:**
```javascript
{
  id: 'camera-bookmarks',
  execute: () => {
    const select = document.getElementById('camera-bookmarks');

    select.addEventListener('change', (e) => {
      const bookmarkName = e.target.value;

      if (!bookmarkName) return; // User selected placeholder

      // Load camera position from storage
      const bookmark = cameraState.getBookmark(bookmarkName);
      if (!bookmark) return;

      // Apply camera position
      cameraState.set(bookmark.position, bookmark.rotation);

      // Animate camera transition
      animateCameraTransition(bookmark);

      // Reset dropdown
      e.target.value = '';
    });
  }
}
```

**Affected controls:**
- `camera-bookmarks`

---

## Pattern 8: Action Button with Modal/Input

**Use case:** Button that opens dialog or prompts for input

**Problem:** Button exists but click handler not implemented

**Solution:** Add click handler that opens dialog and processes result

### Example: Save Camera Bookmark

**Template HTML:**
```html
<button id="camera-save-bookmark">Save View</button>
```

**Handler pattern:**
```javascript
{
  id: 'camera-save-bookmark',
  execute: () => {
    const btn = document.getElementById('camera-save-bookmark');

    btn.addEventListener('click', () => {
      // Show prompt dialog
      const name = prompt('Save this camera view as:', `view_${Date.now()}`);
      if (!name) return; // User cancelled

      // Save bookmark
      const bookmark = {
        name: name,
        position: cameraState.getCurrentPosition(),
        rotation: cameraState.getCurrentRotation(),
        timestamp: Date.now()
      };

      cameraState.saveBookmark(name, bookmark);

      // Update dropdown with new option
      updateBookmarkDropdown();

      // Show confirmation
      showToast(`Saved view: ${name}`);
    });
  }
}
```

**Affected controls:**
- `camera-save-bookmark`

---

## Pattern 9: Accessible Control Group

**Use case:** A11y controls that affect UI appearance

**Problem:** Controls exist but no handlers

**Solution:** Create a11y manager module with integration to state

### Example: Font Size Accessibility

**Template HTML:**
```html
<div id="accessibility" class="settings-group">
  <label for="a11y-font-size">Font Size</label>
  <input id="a11y-font-size" type="range" min="12" max="24" value="14">
  <span id="a11y-font-size-val">14px</span>

  <label for="a11y-large-text">Large Text</label>
  <input id="a11y-large-text" type="checkbox">

  <label for="a11y-focus-indicators">Show Focus Indicators</label>
  <input id="a11y-focus-indicators" type="checkbox" checked>

  <label for="a11y-screen-reader">Screen Reader Support</label>
  <input id="a11y-screen-reader" type="checkbox" checked>
</div>
```

**New module: `src/core/viz/assets/modules/a11y-manager.js`**

```javascript
export function initA11yControls() {
  // Font size
  const fontSizeSlider = document.getElementById('a11y-font-size');
  const fontSizeVal = document.getElementById('a11y-font-size-val');

  fontSizeSlider.addEventListener('input', (e) => {
    const size = parseInt(e.target.value);
    fontSizeVal.textContent = `${size}px`;
    document.documentElement.style.fontSize = `${size}px`;
  });

  // Large text mode
  const largeText = document.getElementById('a11y-large-text');
  largeText.addEventListener('change', (e) => {
    document.body.classList.toggle('large-text', e.target.checked);
  });

  // Focus indicators
  const focusIndicators = document.getElementById('a11y-focus-indicators');
  focusIndicators.addEventListener('change', (e) => {
    document.body.classList.toggle('show-focus', e.target.checked);
  });

  // Screen reader support
  const screenReader = document.getElementById('a11y-screen-reader');
  screenReader.addEventListener('change', (e) => {
    document.body.setAttribute('aria-label',
      e.target.checked ? 'Screen reader enabled' : 'Screen reader disabled'
    );
  });
}
```

**Import in main.js:**
```javascript
import { initA11yControls } from './a11y-manager.js';

function init() {
  // ... other initialization
  initA11yControls();
}
```

**Affected controls (would move to a11y-manager):**
- `a11y-font-size`
- `a11y-font-size-val`
- `a11y-large-text`
- `a11y-focus-indicators`
- `a11y-screen-reader`

---

## Pattern 10: Camera Control Commands

**Use case:** Buttons to manipulate camera programmatically

**Problem:** Buttons exist but no camera control handlers

**Solution:** Create camera-manager module with camera state

### Example: Camera Zoom Controls

**Template HTML:**
```html
<button id="camera-zoom-in">+</button>
<button id="camera-zoom-out">−</button>
<button id="camera-zoom-fit">Fit</button>
<button id="camera-reset">Reset</button>
```

**New module: `src/core/viz/assets/modules/camera-manager.js`**

```javascript
export class CameraManager {
  constructor(camera, graph) {
    this.camera = camera;
    this.graph = graph;
    this.bookmarks = this.loadBookmarks();
  }

  zoomIn(factor = 1.2) {
    this.camera.position.multiplyScalar(1 / factor);
  }

  zoomOut(factor = 1.2) {
    this.camera.position.multiplyScalar(factor);
  }

  fitGraph() {
    // Calculate bounding box of all nodes
    const bounds = this.calculateGraphBounds();
    this.camera.position.copy(bounds.center);
    this.camera.position.z = bounds.radius * 2;
  }

  reset() {
    // Restore default view
    this.camera.position.set(0, 0, 150);
    this.camera.lookAt(0, 0, 0);
  }

  saveBookmark(name) {
    const bookmark = {
      position: this.camera.position.clone(),
      rotation: this.camera.quaternion.clone()
    };
    this.bookmarks[name] = bookmark;
    this.persistBookmarks();
  }

  loadBookmark(name) {
    const bookmark = this.bookmarks[name];
    if (!bookmark) return false;
    this.camera.position.copy(bookmark.position);
    this.camera.quaternion.copy(bookmark.rotation);
    return true;
  }

  persistBookmarks() {
    localStorage.setItem('camera-bookmarks', JSON.stringify(this.bookmarks));
  }

  loadBookmarks() {
    try {
      return JSON.parse(localStorage.getItem('camera-bookmarks')) || {};
    } catch {
      return {};
    }
  }
}

// Wire to buttons
export function initCameraControls(cameraManager) {
  document.getElementById('camera-zoom-in')?.addEventListener('click',
    () => cameraManager.zoomIn()
  );

  document.getElementById('camera-zoom-out')?.addEventListener('click',
    () => cameraManager.zoomOut()
  );

  document.getElementById('camera-zoom-fit')?.addEventListener('click',
    () => cameraManager.fitGraph()
  );

  document.getElementById('camera-reset')?.addEventListener('click',
    () => cameraManager.reset()
  );
}
```

**Affected controls (would move to camera-manager):**
- `camera-zoom-in`
- `camera-zoom-out`
- `camera-zoom-fit`
- `camera-reset`
- `camera-auto-rotate`
- `camera-rotate-speed`
- `camera-rotate-speed-val`
- `camera-bookmarks`
- `camera-save-bookmark`

---

## Quick Implementation Checklist

### For each orphaned control:

1. **Identify the element**
   ```javascript
   const el = document.getElementById('control-id');
   ```

2. **Determine the handler pattern** (see patterns 1-10 above)

3. **Write the event listener**
   ```javascript
   el.addEventListener('event-type', (e) => {
     // Handle the event
   });
   ```

4. **Update state** (use existing state objects)
   ```javascript
   STATE.property = newValue;
   ```

5. **Trigger visualization update**
   ```javascript
   updateVisualization();
   applyFilters();
   // etc
   ```

6. **Test in browser**
   - Open DevTools Console
   - Verify no errors
   - Test the control works
   - Check state changes

7. **Verify in generated report**
   - Run `./collider full . --output .collider`
   - Open generated `collider_report.html`
   - Test control in actual report

---

## Common State Objects

| State Object | Location | Purpose |
|-------------|----------|---------|
| `APPEARANCE_STATE` | circuit-breaker.js | Visual config (opacity, size, curves) |
| `filterState` | filter-state.js | Filter settings |
| `selectionState` | selection.js | Selected nodes/edges |
| `cameraState` | (needs impl) | Camera position, bookmarks |
| `a11yState` | (needs impl) | Accessibility settings |

---

## Testing Handlers

### In browser DevTools:

```javascript
// Verify element exists
document.getElementById('cfg-edge-opacity')
// → <input id="cfg-edge-opacity" ...>

// Verify listener attached
document.getElementById('cfg-edge-opacity')
  .addEventListener('input', () => console.log('test'));

// Simulate slider change
const el = document.getElementById('cfg-edge-opacity');
el.value = 0.5;
el.dispatchEvent(new Event('input'));

// Check state updated
console.log(APPEARANCE_STATE.edgeOpacity)
// → 0.5
```

---

## Summary

**46 orphaned controls grouped by pattern:**

| Pattern | Controls | Effort | Files |
|---------|----------|--------|-------|
| 1. Numeric Sync | 14 | Easy | circuit-breaker.js |
| 2. Range Display | 4 | Easy | filter-state.js |
| 3. Toggle | 7 | Easy | various |
| 4. Button Click | 6 | Easy | various |
| 5. Chip Container | 3 | Medium | filter-state.js |
| 6. Display Update | 2 | Easy | hud.js |
| 7. Select Dropdown | 1 | Medium | (new module) |
| 8. Save Dialog | 1 | Medium | (new module) |
| 9. A11y Controls | 5 | Medium | a11y-manager.js |
| 10. Camera Controls | 9 | Hard | camera-manager.js |

**Total effort estimate:** 8-12 hours for full implementation

**Quick win (30 min):** Implement Pattern 1 (numeric sync) - biggest visual impact
