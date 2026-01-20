# Modularization MVP Workflow

> Systematic, repeatable process for extracting functions from app.js

---

## THE RHYTHM: 5-Step Module Extraction

```
┌─────────────────────────────────────────────────────────────┐
│  SCAN → EXTRACT → CREATE → REMOVE → VERIFY                 │
│    1       2         3        4        5                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: SCAN (Identify Target Functions)

**Command:**
```bash
grep -n "^function FUNCNAME" src/core/viz/assets/app.js
```

**Checklist:**
- [ ] List all functions for this module
- [ ] Note line numbers (start-end)
- [ ] Identify dependencies (what globals/functions it calls)
- [ ] Identify dependents (what calls this function)

**Output:** Function inventory table

| Function | Lines | Depends On | Called By |
|----------|-------|------------|-----------|
| funcA    | 100-150 | DM, Graph | funcX |
| funcB    | 151-200 | funcA | onclick |

---

## Step 2: EXTRACT (Copy Code)

**Action:** Read function code from app.js

**Checklist:**
- [ ] Copy function body exactly
- [ ] Copy any associated constants/variables
- [ ] Note any inline comments that explain behavior

---

## Step 3: CREATE (Write Module File)

**Template:**
```javascript
/**
 * ═══════════════════════════════════════════════════════════════════════════
 * MODULE_NAME MODULE - Brief description
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Detailed description of what this module handles.
 * Depends on: LIST_GLOBALS_AND_MODULES
 *
 * @module MODULE_NAME
 * @version 1.0.0
 */

window.MODULE_NAME = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // SECTION NAME
    // ═══════════════════════════════════════════════════════════════════════

    function functionName() {
        // Implementation
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        publicName: functionName
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.functionName = MODULE_NAME.publicName;

console.log('[Module] MODULE_NAME loaded - N functions');
```

**Checklist:**
- [ ] Create file at `src/core/viz/assets/modules/name.js`
- [ ] Add IIFE wrapper
- [ ] Export all public functions
- [ ] Add backward compatibility shims
- [ ] Add console.log count

---

## Step 4: REMOVE (Clean app.js)

**Action:** Replace function definitions with MOVED TO markers

**Pattern:**
```javascript
// functionA, functionB, functionC - MOVED TO modules/name.js
```

**Checklist:**
- [ ] Remove function body (keep marker comment)
- [ ] Remove associated constants if moved
- [ ] Keep variable declarations that are still used

---

## Step 5: VERIFY (Test Build)

**Commands:**
```bash
# Update MODULE_ORDER (if new module)
# Edit: tools/visualize_graph_webgl.py

# Rebuild
./collider full . --output .collider

# Check line count
wc -l src/core/viz/assets/app.js

# Verify modules loaded
grep "\[Module\].*loaded" .collider/*.html | tail -20
```

**Checklist:**
- [ ] MODULE_ORDER updated (new modules only)
- [ ] Build succeeds
- [ ] All modules load (check console.log output)
- [ ] No JS errors in browser

---

## QUEUE SYSTEM

### Current Extraction Queue

| Priority | Module | Functions | Status |
|----------|--------|-----------|--------|
| P1 | file-boundaries.js | 15+ | NEXT |
| P2 | config-controls.js | 8 | PENDING |
| P3 | legend-render.js | 4 | PENDING |
| P4 | graph-init.js | 5 | PENDING |

### Completed Modules (Phase 1 + 2 + 3 + 4)

| Module | Functions | Description |
|--------|-----------|-------------|
| node-helpers.js | 11 | Node classification & colors |
| color-helpers.js | 6 | Color utilities |
| physics.js | 4 | Force simulation controls |
| datamap.js | 7 | Data mapping & filtering |
| groups.js | 8 | Node grouping |
| hover.js | 3 | Hover interactions |
| flow.js | 6 | Flow visualization presets |
| ui-builders.js | 5 | DOM element builders |
| layout-helpers.js | 7 | Layout stability |
| spatial.js | 6 | Spatial algorithms |
| stars.js | 3 | Starfield visibility |
| hud.js | 2 | HUD fade & stats |
| dimension.js | 3 | 2D/3D toggle animation |
| report.js | 3 | Report, AI insights, metrics |
| legend-manager.js | +2 | DOM rendering added |
| visibility.js | 4 | UI visibility controls |
| animation.js | 7 | Layout presets, flock, stagger (O(n) spatial hash) |
| file-viz.js | +4 | File clustering forces added |
| **TOTAL** | **91** | **New modules: 17** |

---

## PROGRESS TRACKER

```
app.js: 8,826 → 6,151 lines (-30.3%)
Functions: 148 → 65 (-56.1%)
Modules: 19 → 34 (+15)
Target: ~2,000 lines

████████████████████████░ 39% to target
```

---

## QUICK REFERENCE

### Add Module to Build Order

Edit `tools/visualize_graph_webgl.py`:
```python
MODULE_ORDER = [
    # ... existing modules ...
    "modules/new-module.js",  # ADD HERE (respect dependencies)
    # ... remaining modules ...
]
```

### Common Globals (safe to access via window.*)

| Global | Purpose |
|--------|---------|
| `Graph` | 3D Force Graph instance |
| `DM` | DataManager instance |
| `VIS_FILTERS` | Filter state |
| `SELECTED_NODE_IDS` | Selection Set |
| `THEME_CONFIG` | Theme tokens |
| `APPEARANCE_CONFIG` | Appearance tokens |

### Shim Pattern

```javascript
// Single function
window.funcName = MODULE.funcName;

// Multiple functions
window.funcA = MODULE.funcA;
window.funcB = MODULE.funcB;
```

---

## ABORT CONDITIONS

Stop extraction if:
1. Function has 10+ internal dependencies
2. Function modifies Graph internals directly
3. Function is called from template.html onclick
4. Build fails after removal

---

## NEXT ACTION

**Module:** `flow.js`
**Functions:** getFlowPresetColor, getFlowPresetValue, toggleFlowMode, disableFlowMode, applyFlowVisualization, clearFlowVisualization
**Constants:** FLOW_PRESETS, currentFlowPreset

**Step:** CREATE module file
