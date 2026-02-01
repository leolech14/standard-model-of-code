# UI Wiring - Next Steps

**Status:** All 46 orphaned controls now have handlers
**File:** `src/core/viz/assets/modules/panel-handlers.js` (601 → 981 lines)
**Date:** 2026-01-26

---

## Immediate Next Steps (Priority Order)

### 1. Test in Browser (15 minutes)
```bash
# Regenerate visualization
./collider full standard-model-of-code --output /tmp/test_wiring

# Open in browser
open /tmp/test_wiring/collider_report.html
```

**Test Checklist:**
- [ ] Open browser console - verify no JavaScript errors
- [ ] Click `a11y-large-text` toggle - UI should scale
- [ ] Drag `filter-min-degree` slider - nodes should filter
- [ ] Click `panel-select-clear` - selection should clear
- [ ] Click `camera-save-bookmark` - bookmark should save
- [ ] Verify numeric displays update when sliders move

---

### 2. Add Missing CSS Classes (10 minutes)

Add to `src/core/viz/assets/styles.css`:

```css
/* Accessibility enhancements */
body.large-text {
    --scale-factor: 1.2;
}

body.sr-mode .node-label {
    opacity: 1 !important;
    pointer-events: all;
}

body.show-focus-indicators *:focus {
    outline: var(--focus-ring, 2px solid var(--accent));
    outline-offset: 2px;
}

/* Filter chips */
.chip {
    display: inline-block;
    padding: 4px 12px;
    margin: 2px;
    background: var(--surface-hover);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
}

.chip:hover {
    background: var(--accent-dim);
    border-color: var(--accent);
}

.chip.active {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
}
```

---

### 3. Implement Missing FILTER_STATE Methods (20 minutes)

Check `src/core/viz/assets/modules/filter-state.js` for these methods:

```javascript
// If missing, add:
setMaxDegree(val) {
    this.maxDegree = val;
    this._applyFilters();
}

setFilter(type, values) {
    this.filters[type] = values;
    this._applyFilters();
}

removeFilter(type, value) {
    if (this.filters[type]) {
        this.filters[type] = this.filters[type].filter(v => v !== value);
        this._applyFilters();
    }
}

getActiveFilters() {
    return { ...this.filters };
}
```

---

### 4. Validate with Circuit Breaker (5 minutes)

In browser console after loading graph:
```javascript
CIRCUIT.runAll()  // Should show more passing tests
CIRCUIT.inventory()  // Print full control table
```

Expected: Previously failing tests should now pass.

---

### 5. Add TOAST Module (optional, 10 minutes)

If TOAST notifications desired, create `src/core/viz/assets/modules/toast.js`:

```javascript
window.TOAST = (function() {
    function show(message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    return { show };
})();
```

Add CSS:
```css
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--surface);
    border: 1px solid var(--border-accent);
    padding: 12px 20px;
    border-radius: var(--radius);
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s;
    z-index: 10000;
}

.toast.show {
    opacity: 1;
    transform: translateY(0);
}
```

---

## Low Priority Enhancements

### A. Camera Preset Views (30 minutes)
Add handler for `data-camera-preset` buttons:
```javascript
document.querySelectorAll('[data-camera-preset]').forEach(btn => {
    btn.addEventListener('click', () => {
        const preset = btn.dataset.cameraPreset;
        const positions = {
            top: { pos: {x: 0, y: 500, z: 0}, lookAt: {x: 0, y: 0, z: 0} },
            front: { pos: {x: 0, y: 0, z: 500}, lookAt: {x: 0, y: 0, z: 0} },
            side: { pos: {x: 500, y: 0, z: 0}, lookAt: {x: 0, y: 0, z: 0} }
        };
        if (typeof Graph !== 'undefined' && positions[preset]) {
            Graph.cameraPosition(positions[preset].pos, positions[preset].lookAt, 1000);
        }
    });
});
```

### B. Performance Monitor Upgrade (20 minutes)
Replace `setInterval` with proper frame timing:
```javascript
let frameCount = 0;
let lastFpsUpdate = performance.now();

function updatePerf() {
    frameCount++;
    const now = performance.now();
    if (now - lastFpsUpdate > 100) {
        const fps = frameCount / ((now - lastFpsUpdate) / 1000);
        document.getElementById('perf-frame').textContent = fps.toFixed(1) + ' fps';
        frameCount = 0;
        lastFpsUpdate = now;
    }
    requestAnimationFrame(updatePerf);
}
requestAnimationFrame(updatePerf);
```

### C. Filter Persistence (15 minutes)
Save active filters to localStorage:
```javascript
// On filter change:
localStorage.setItem('activeFilters', JSON.stringify(FILTER_STATE.getActiveFilters()));

// On load:
const savedFilters = JSON.parse(localStorage.getItem('activeFilters') || '{}');
Object.entries(savedFilters).forEach(([type, values]) => {
    FILTER_STATE.setFilter(type, values);
});
```

---

## Known Issues to Watch For

1. **Timing:** If `_bindFilterChips()` runs before Graph data loaded, chips won't populate
   - **Fix:** Call after Graph.graphData() ready, or retry on data load event

2. **Event Bus:** If EVENT_BUS not defined, filter change events won't propagate
   - **Fix:** Graceful degradation already in place (`typeof EVENT_BUS !== 'undefined'`)

3. **Three.js dependency:** Camera zoom in/out uses `THREE.Vector3`
   - **Fix:** Already checks `window.THREE`, but ensure Three.js loaded before module

4. **FILTER_STATE methods:** Assumes methods exist that may not be implemented yet
   - **Fix:** See step 3 above

---

## Success Metrics

| Metric | Target | How to Verify |
|--------|--------|---------------|
| No console errors | 0 errors | Open dev tools, check console |
| Controls functional | 46/46 working | Manual test checklist |
| Numeric displays sync | 14/14 update | Drag sliders, watch displays |
| Filter chips populate | All tiers/families/roles | Check containers have content |
| Camera bookmarks save | Persist after reload | Save bookmark, refresh page, verify in dropdown |

---

## Files to Modify

| File | Action | Time |
|------|--------|------|
| `src/core/viz/assets/styles.css` | Add chip/accessibility styles | 10 min |
| `src/core/viz/assets/modules/filter-state.js` | Add missing methods if needed | 20 min |
| `src/core/viz/assets/modules/toast.js` | Create (optional) | 10 min |
| `src/core/viz/assets/template.html` | Add TOAST container (optional) | 2 min |

---

## Testing Commands

```bash
# Syntax check
node --check src/core/viz/assets/modules/panel-handlers.js

# Full analysis (regenerate HTML)
./collider full standard-model-of-code --output /tmp/test_ui

# Run tests (if available)
pytest tests/test_ui.py -v
```

---

## Rollback Plan

If handlers cause issues:
```bash
git checkout HEAD -- src/core/viz/assets/modules/panel-handlers.js
```

Original file: 601 lines
Modified file: 981 lines
Diff: +380 lines

---

## Documentation Updated

- [x] ORPHANED_UI_CONTROLS_WIRING_REPORT.md created
- [x] UI_WIRING_NEXT_STEPS.md created (this file)
- [ ] VISUALIZATION_UI_SPEC.md (update control inventory)
- [ ] CLAUDE.md (add wiring status note)

---

## Summary

**DONE:**
- All 46 orphaned controls wired with handlers
- Defensive coding (type checks, optional chaining)
- Following existing panel-handlers.js patterns
- No syntax errors

**TODO (before claiming complete):**
- Browser test (verify functionality)
- Add CSS for chips/accessibility
- Implement missing FILTER_STATE methods
- Run circuit-breaker validation

**Risk:** LOW - handlers use graceful degradation
**Complexity:** MEDIUM - some advanced features (camera bookmarks, chip population)
**Impact:** HIGH - completes UI control coverage
