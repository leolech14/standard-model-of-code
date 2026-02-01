# app.js Modularization - Actionable Tasks

> **Status:** Ready to Execute
> **Source:** `src/core/viz/assets/app.js`
> **Pattern:** IIFE modules (see `modules/utils.js` for template)

---

## PHASE 1: Pure Functions (6 modules, 1,076 lines)

---

### TASK 1.1: Create `modules/node-helpers.js`

**Lines to extract:** 237
**Confidence:** 97%
**Dependencies:** None (pure functions)

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/node-helpers.js
```

#### Step 2: Copy this template
```javascript
/**
 * NODE-HELPERS MODULE - Node classification and color functions
 * @module NODE_HELPERS
 */
window.NODE_HELPERS = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE (from Step 3) ===

    return {
        getColorByMode: getNodeColorByMode,
        getSubsystem: getSubsystem,
        getPhase: getPhase,
        getFileType: getFileType,
        getRoleCategory: getRoleCategory,
        applyColors: applyNodeColors,
        applySizeMode: applyNodeSizeMode,
        getTierValue: getNodeTierValue,
        getDepth: getNodeDepth,
        getSemanticSimilarity: getSemanticSimilarity,
        groupByTier: groupNodesByTier
    };
})();

// Backward compatibility
window.getNodeColorByMode = NODE_HELPERS.getColorByMode;
window.getSubsystem = NODE_HELPERS.getSubsystem;
window.getPhase = NODE_HELPERS.getPhase;
window.getFileType = NODE_HELPERS.getFileType;
window.getRoleCategory = NODE_HELPERS.getRoleCategory;
window.applyNodeColors = NODE_HELPERS.applyColors;
window.applyNodeSizeMode = NODE_HELPERS.applySizeMode;
window.getNodeTierValue = NODE_HELPERS.getTierValue;
window.getNodeDepth = NODE_HELPERS.getDepth;
window.getSemanticSimilarity = NODE_HELPERS.getSemanticSimilarity;
window.groupNodesByTier = NODE_HELPERS.groupByTier;

console.log('[Module] NODE_HELPERS loaded - 11 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `getNodeColorByMode` | L2292-2360 | Copy to module |
| `getSubsystem` | L2361-2371 | Copy to module |
| `getPhase` | L2372-2381 | Copy to module |
| `getFileType` | L2382-2387 | Copy to module |
| `getRoleCategory` | L2388-2399 | Copy to module |
| `applyNodeColors` | L2400-2418 | Copy to module |
| `applyNodeSizeMode` | L3002-3025 | Copy to module |
| `getNodeTierValue` | L5538-5547 | Copy to module |
| `getNodeDepth` | L5548-5556 | Copy to module |
| `getSemanticSimilarity` | L5557-5578 | Copy to module |
| `groupNodesByTier` | L3825-3869 | Copy to module |

#### Step 4: Replace in app.js with markers
```javascript
// getNodeColorByMode, getSubsystem, getPhase, getFileType, getRoleCategory, applyNodeColors - MOVED TO modules/node-helpers.js
// applyNodeSizeMode - MOVED TO modules/node-helpers.js
// getNodeTierValue, getNodeDepth, getSemanticSimilarity - MOVED TO modules/node-helpers.js
// groupNodesByTier - MOVED TO modules/node-helpers.js
```

#### Step 5: Update visualize_graph_webgl.py
Add to MODULE_ORDER after `"modules/utils.js"`:
```python
"modules/node-helpers.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: No console errors, node colors work
```

---

### TASK 1.2: Create `modules/color-helpers.js`

**Lines to extract:** 280
**Confidence:** 100%
**Dependencies:** None

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/color-helpers.js
```

#### Step 2: Copy this template
```javascript
/**
 * COLOR-HELPERS MODULE - Color utilities and conversions
 * @module COLOR_HELPERS
 */
window.COLOR_HELPERS = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE ===

    return {
        getTopoColor: getTopoColor,
        normalizeInput: normalizeColorInput,
        toNumber: toColorNumber,
        dim: dimColor,
        getFileHue: getFileHue,
        getFileColor: getFileColor
    };
})();

// Backward compatibility
window.getTopoColor = COLOR_HELPERS.getTopoColor;
window.normalizeColorInput = COLOR_HELPERS.normalizeInput;
window.toColorNumber = COLOR_HELPERS.toNumber;
window.dimColor = COLOR_HELPERS.dim;
window.getFileHue = COLOR_HELPERS.getFileHue;
window.getFileColor = COLOR_HELPERS.getFileColor;

console.log('[Module] COLOR_HELPERS loaded - 6 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `getTopoColor` | L3624-3824 | Copy to module |
| `normalizeColorInput` | L5579-5592 | Copy to module |
| `toColorNumber` | L5593-5617 | Copy to module |
| `dimColor` | L6765-6773 | Copy to module |
| `getFileHue` | L6115-6128 | Copy to module |
| `getFileColor` | L6129-6145 | Copy to module |

#### Step 4: Replace in app.js
```javascript
// getTopoColor - MOVED TO modules/color-helpers.js
// normalizeColorInput, toColorNumber - MOVED TO modules/color-helpers.js
// dimColor - MOVED TO modules/color-helpers.js
// getFileHue, getFileColor - MOVED TO modules/color-helpers.js
```

#### Step 5: Update MODULE_ORDER
```python
"modules/color-helpers.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: Topology colors work, file colors work
```

---

### TASK 1.3: Create `modules/physics.js`

**Lines to extract:** 138
**Confidence:** 96%
**Dependencies:** Graph (via window.Graph)

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/physics.js
```

#### Step 2: Copy this template
```javascript
/**
 * PHYSICS MODULE - Force simulation controls
 * @module PHYSICS
 */
window.PHYSICS = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE ===
    // Replace direct Graph. references with window.Graph.

    return {
        applyState: applyPhysicsState,
        applyPreset: applyPhysicsPreset,
        updateSliders: updatePhysicsSliders,
        buildControls: buildPhysicsControls
    };
})();

// Backward compatibility
window.applyPhysicsState = PHYSICS.applyState;
window.applyPhysicsPreset = PHYSICS.applyPreset;
window.updatePhysicsSliders = PHYSICS.updateSliders;
window.buildPhysicsControls = PHYSICS.buildControls;

console.log('[Module] PHYSICS loaded - 4 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `applyPhysicsState` | L4711-4723 | Copy, change `Graph.` → `window.Graph.` |
| `applyPhysicsPreset` | L4724-4737 | Copy to module |
| `updatePhysicsSliders` | L4738-4752 | Copy to module |
| `buildPhysicsControls` | L4753-4848 | Copy to module |

#### Step 4: Replace in app.js
```javascript
// applyPhysicsState, applyPhysicsPreset, updatePhysicsSliders, buildPhysicsControls - MOVED TO modules/physics.js
```

#### Step 5: Update MODULE_ORDER
```python
"modules/physics.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: Physics sliders work, presets apply
```

---

### TASK 1.4: Create `modules/datamap.js`

**Lines to extract:** 167
**Confidence:** 96%
**Dependencies:** DM (via window.DM)

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/datamap.js
```

#### Step 2: Copy this template
```javascript
/**
 * DATAMAP MODULE - Data mapping and filtering
 * @module DATAMAP
 */
window.DATAMAP = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE ===
    // Replace DM. with window.DM.

    return {
        normalizeConfig: normalizeDatamapConfig,
        resolveConfigs: resolveDatamapConfigs,
        matches: datamapMatches,
        set: setDatamap,
        setColorMode: setNodeColorMode,
        apply: applyDatamap,
        updateControls: updateDatamapControls
    };
})();

// Backward compatibility
window.normalizeDatamapConfig = DATAMAP.normalizeConfig;
window.resolveDatamapConfigs = DATAMAP.resolveConfigs;
window.datamapMatches = DATAMAP.matches;
window.setDatamap = DATAMAP.set;
window.setNodeColorMode = DATAMAP.setColorMode;
window.applyDatamap = DATAMAP.apply;
window.updateDatamapControls = DATAMAP.updateControls;

console.log('[Module] DATAMAP loaded - 7 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `normalizeDatamapConfig` | L4210-4237 | Copy to module |
| `resolveDatamapConfigs` | L4238-4256 | Copy to module |
| `datamapMatches` | L4257-4291 | Copy to module |
| `setDatamap` | L6063-6090 | Copy to module |
| `setNodeColorMode` | L6091-6103 | Copy to module |
| `applyDatamap` | L6104-6114 | Copy to module |
| `updateDatamapControls` | L5278-5310 | Copy to module |

#### Step 4: Replace in app.js
```javascript
// normalizeDatamapConfig, resolveDatamapConfigs, datamapMatches - MOVED TO modules/datamap.js
// setDatamap, setNodeColorMode, applyDatamap - MOVED TO modules/datamap.js
// updateDatamapControls - MOVED TO modules/datamap.js
```

#### Step 5: Update MODULE_ORDER
```python
"modules/datamap.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: Datamap toggles work, color modes switch
```

---

### TASK 1.5: Create `modules/groups.js`

**Lines to extract:** 135
**Confidence:** 92%
**Dependencies:** SELECTED_NODE_IDS, GROUPS (via window.*)

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/groups.js
```

#### Step 2: Copy this template
```javascript
/**
 * GROUPS MODULE - Node grouping functionality
 * @module GROUPS
 */
window.GROUPS_MODULE = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE ===
    // Replace GROUPS with window.GROUPS
    // Replace SELECTED_NODE_IDS with window.SELECTED_NODE_IDS

    return {
        load: loadGroups,
        save: saveGroups,
        getNextColor: getNextGroupColor,
        getById: getGroupById,
        getPrimaryForNode: getPrimaryGroupForNode,
        renderList: renderGroupList,
        updateButtonState: updateGroupButtonState,
        createFromSelection: createGroupFromSelection
    };
})();

// Backward compatibility
window.loadGroups = GROUPS_MODULE.load;
window.saveGroups = GROUPS_MODULE.save;
window.getNextGroupColor = GROUPS_MODULE.getNextColor;
window.getGroupById = GROUPS_MODULE.getById;
window.getPrimaryGroupForNode = GROUPS_MODULE.getPrimaryForNode;
window.renderGroupList = GROUPS_MODULE.renderList;
window.updateGroupButtonState = GROUPS_MODULE.updateButtonState;
window.createGroupFromSelection = GROUPS_MODULE.createFromSelection;

console.log('[Module] GROUPS_MODULE loaded - 8 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `loadGroups` | L6195-6213 | Copy, use window.GROUPS |
| `saveGroups` | L6214-6221 | Copy, use window.GROUPS |
| `getNextGroupColor` | L6222-6226 | Copy to module |
| `getGroupById` | L6227-6230 | Copy, use window.GROUPS |
| `getPrimaryGroupForNode` | L6231-6242 | Copy, use window.GROUPS |
| `renderGroupList` | L6243-6301 | Copy, use window.GROUPS |
| `updateGroupButtonState` | L6302-6309 | Copy to module |
| `createGroupFromSelection` | L6310-6329 | Copy, use window.SELECTED_NODE_IDS |

#### Step 4: Replace in app.js
```javascript
// loadGroups, saveGroups, getNextGroupColor, getGroupById, getPrimaryGroupForNode - MOVED TO modules/groups.js
// renderGroupList, updateGroupButtonState, createGroupFromSelection - MOVED TO modules/groups.js
```

#### Step 5: Update MODULE_ORDER
```python
"modules/groups.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: Groups panel works, create/delete groups
```

---

### TASK 1.6: Create `modules/hover.js`

**Lines to extract:** 119
**Confidence:** 95%
**Dependencies:** HOVERED_NODE (via window.*)

#### Step 1: Create file
```bash
touch src/core/viz/assets/modules/hover.js
```

#### Step 2: Copy this template
```javascript
/**
 * HOVER MODULE - Node hover and click interactions
 * @module HOVER
 */
window.HOVER = (function() {
    'use strict';

    // === PASTE FUNCTIONS HERE ===
    // Replace HOVERED_NODE with window.HOVERED_NODE

    return {
        onNodeHover: handleNodeHover,
        onNodeClick: handleNodeClick,
        updatePanel: updateHoverPanel
    };
})();

// Backward compatibility
window.handleNodeHover = HOVER.onNodeHover;
window.handleNodeClick = HOVER.onNodeClick;
window.updateHoverPanel = HOVER.updatePanel;

console.log('[Module] HOVER loaded - 3 functions');
```

#### Step 3: Extract these functions from app.js

| Function | Lines | Action |
|----------|-------|--------|
| `handleNodeHover` | L7033-7087 | Copy, use window.HOVERED_NODE |
| `handleNodeClick` | L7088-7102 | Copy to module |
| `updateHoverPanel` | L6146-6194 | Copy to module |

#### Step 4: Replace in app.js
```javascript
// handleNodeHover, handleNodeClick - MOVED TO modules/hover.js
// updateHoverPanel - MOVED TO modules/hover.js
```

#### Step 5: Update MODULE_ORDER
```python
"modules/hover.js",
```

#### Step 6: Verify
```bash
./collider full . --output .collider && open .collider/*.html
# Check: Hover panel shows, click selects nodes
```

---

## PHASE 1 COMPLETION CHECKLIST

After all 6 tasks:

```bash
# Final verification
./collider full . --output .collider
open .collider/*.html
```

### Console check
- [ ] `[Module] NODE_HELPERS loaded - 11 functions`
- [ ] `[Module] COLOR_HELPERS loaded - 6 functions`
- [ ] `[Module] PHYSICS loaded - 4 functions`
- [ ] `[Module] DATAMAP loaded - 7 functions`
- [ ] `[Module] GROUPS_MODULE loaded - 8 functions`
- [ ] `[Module] HOVER loaded - 3 functions`

### Feature check
- [ ] Node colors render correctly
- [ ] Topology tooltip colors work
- [ ] Physics sliders adjust simulation
- [ ] Datamap toggles filter nodes
- [ ] Groups can be created/deleted
- [ ] Hover panel shows node info
- [ ] Click selects nodes

### Metrics after Phase 1
```
app.js: 8,826 → ~7,750 lines (-1,076 lines, -12%)
New modules: 6
Total modules: 23
```

---

## MODULE_ORDER after Phase 1

Update `tools/visualize_graph_webgl.py`:

```python
MODULE_ORDER = [
    "performance.js",
    "modules/utils.js",
    "modules/core.js",
    "modules/node-accessors.js",
    "modules/node-helpers.js",      # NEW
    "modules/color-helpers.js",     # NEW
    "modules/color-engine.js",
    "modules/refresh-throttle.js",
    "modules/legend-manager.js",
    "modules/data-manager.js",
    "modules/physics.js",           # NEW
    "modules/datamap.js",           # NEW
    "modules/groups.js",            # NEW
    "modules/hover.js",             # NEW
    "modules/animation.js",
    "modules/selection.js",
    "modules/panels.js",
    "modules/sidebar.js",
    "modules/edge-system.js",
    "modules/file-viz.js",
    "modules/tooltips.js",
    "modules/theme.js",
    "modules/control-bar.js",
    "modules/main.js",
]
```

---

## COMMIT after Phase 1

```bash
cd /Users/lech/PROJECTS_all/PROJECT_elements
git add standard-model-of-code/src/core/viz/assets/modules/*.js
git add standard-model-of-code/src/core/viz/assets/app.js
git add standard-model-of-code/tools/visualize_graph_webgl.py
git commit -m "Extract 6 modules from app.js (Phase 1): node-helpers, color-helpers, physics, datamap, groups, hover

- node-helpers.js: 11 functions (237 lines)
- color-helpers.js: 6 functions (280 lines)
- physics.js: 4 functions (138 lines)
- datamap.js: 7 functions (167 lines)
- groups.js: 8 functions (135 lines)
- hover.js: 3 functions (119 lines)

Total: 39 functions, 1,076 lines extracted
app.js: 8,826 → 7,750 lines (-12%)

Co-Authored-By: Claude <noreply@anthropic.com>"
```
