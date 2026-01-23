# UPB Implementation Plan (RAG-Validated)

> Validated via analyze.py queries against viz_core and body analysis sets

## Executive Summary

This plan extracts and consolidates binding logic from the sprawl identified in `UPB_LEGACY_SPRAWL.md` into a modular, testable architecture.

---

## RAG Validation Results

### Query 1: Binding Logic Sprawl
**Set:** `viz_core` | **Confidence:** HIGH

| File | Contains | Action |
|------|----------|--------|
| `control-bar.js` | `DATA_SOURCES`, `VISUAL_TARGETS`, `SCALES` | **EXTRACT** |
| `file-viz.js` | `VISUAL_MAPPINGS`, `applyVisualMapping()` | **REPLACE** |
| `node-helpers.js` | `getNodeColorByMode`, tier/ring accessors | **INTEGRATE** |
| `edge-system.js` | Edge color interpolation, width mapping | **EXTEND** |
| `color-engine.js` | OKLCH implementation, gradients | **USE AS-IS** |
| `data-manager.js` | Data broker (getNodes, getLinks) | **USE AS-IS** |

### Query 2: Dependency Matrix
**Set:** `viz_core` | **Confidence:** HIGH

```
                     Depends On →
                   control-bar  file-viz  node-helpers  edge-system  color-engine  data-manager
 control-bar.js        -           -           -             -            ✓            ✓
 file-viz.js           -           -           ✓            -            ✓            ✓
 node-helpers.js       -           -           -             -            -             -
 edge-system.js        -           -           ✓            -            ✓            -
 color-engine.js       -           -           -             -            -             -
 data-manager.js       -           -           ✓            -            ✓            -
```

**Key Finding:** `color-engine.js` and `node-helpers.js` are foundational (zero dependencies).

### Query 3: Python Server-Side
**Set:** `body` | **Confidence:** MEDIUM

| File | Binding Logic | UPB Integration |
|------|---------------|-----------------|
| `appearance_engine.py` | `apply_to_nodes()`, color modes, size | Token resolver pattern |
| `controls_engine.py` | Slider/button config, UI generation | Config injection |

**Key Finding:** Python uses `token_resolver.py` pattern - UPB can follow same pattern.

---

## Implementation Order (Dependency-Safe)

### Phase 0: Preparation (No Code Changes)
- [x] RAG validation complete
- [x] Dependency matrix mapped
- [ ] Create test harness for visual regression

### Phase 1: Extract Foundations
**Goal:** Extract definitions without breaking existing code

**CRITICAL:** Codebase uses IIFE pattern, NOT ES6 modules. All UPB modules must follow this pattern:
```javascript
const UPB_SCALES = (function() {
    'use strict';
    // Private scope
    return { /* Public API */ };
})();
if (typeof window !== 'undefined') window.UPB_SCALES = UPB_SCALES;
```

#### 1.1 Create `upb/scales.js` (~120 lines)
Extract from `control-bar.js` lines 93-108:
```javascript
// CURRENT (control-bar.js)
const SCALES = {
    linear: (v, min, max) => ...,
    log: (v, min, max) => ...,
    sqrt: (v, min, max) => ...,
    inverse: (v, min, max) => ...
};

// NEW (upb/scales.js) - IIFE PATTERN
const UPB_SCALES = (function() {
    'use strict';

    const SCALES = { linear: ..., log: ..., sqrt: ..., inverse: ..., exp: ..., discrete: ... };
    const SCALE_NAMES = ['linear', 'log', 'sqrt', 'inverse', 'exp', 'discrete', 'percentile'];

    function applyScale(name, value, min, max) { ... }

    return { SCALES, SCALE_NAMES, applyScale };
})();
if (typeof window !== 'undefined') window.UPB_SCALES = UPB_SCALES;
```

#### 1.2 Create `upb/endpoints.js` (~180 lines)
Extract from `control-bar.js` lines 25-87:
```javascript
// CURRENT (control-bar.js)
const DATA_SOURCES = { size_bytes: {...}, token_estimate: {...}, ... };
const VISUAL_TARGETS = { nodeSize: {...}, hue: {...}, ... };

// NEW (upb/endpoints.js) - IIFE PATTERN
const UPB_ENDPOINTS = (function() {
    'use strict';

    const SOURCES = { ... };  // Enhanced with validation
    const TARGETS = { ... };  // Enhanced with units, constraints

    function getSource(name) { ... }
    function getTarget(name) { ... }
    function listSources(type) { ... }  // type='continuous'|'discrete'|'boolean'
    function listTargets(category) { ... }  // category='appearance'|'physics'|'animation'

    return { SOURCES, TARGETS, getSource, getTarget, listSources, listTargets };
})();
if (typeof window !== 'undefined') window.UPB_ENDPOINTS = UPB_ENDPOINTS;
```

### Phase 2: Create Binding Graph
**Goal:** Implement the core UPB abstraction

#### 2.1 Create `upb/bindings.js` (~250 lines)
```javascript
// NEW - The UPB Core (IIFE PATTERN)
const UPB_BINDINGS = (function() {
    'use strict';

    // Access other UPB modules via window
    const SCALES = window.UPB_SCALES;
    const ENDPOINTS = window.UPB_ENDPOINTS;

    function Binding(source, target, options) {
        options = options || {};
        this.source = source;      // String: key into SOURCES
        this.target = target;      // String: key into TARGETS
        this.scale = options.scale || 'linear';
        this.weight = options.weight || 1.0;
        this.range = options.range || null;  // Override target default range
    }

    Binding.prototype.apply = function(node, sourceValue, dataMin, dataMax) { ... };

    function BindingGraph() {
        this._bindings = new Map();  // target -> [Binding, ...]
    }

    BindingGraph.prototype.bind = function(source, target, options) { ... };
    BindingGraph.prototype.unbind = function(source, target) { ... };
    BindingGraph.prototype.getBindingsFor = function(target) { ... };
    BindingGraph.prototype.hasConflict = function(target) { ... };
    BindingGraph.prototype.evaluate = function(node, dataRanges) { ... };
    BindingGraph.prototype.serialize = function() { ... };
    BindingGraph.deserialize = function(config) { ... };

    var defaultGraph = new BindingGraph();

    return { Binding, BindingGraph, defaultGraph };
})();
if (typeof window !== 'undefined') window.UPB_BINDINGS = UPB_BINDINGS;
```

### Phase 3: Blend Modes
**Goal:** Enable many-to-one binding

#### 3.1 Create `upb/blenders.js` (~150 lines)
```javascript
// Blend multiple source values into single target value (IIFE PATTERN)
const UPB_BLENDERS = (function() {
    'use strict';

    var BLENDERS = {
        add: function(values, weights) {
            return values.reduce(function(a, v, i) { return a + v * weights[i]; }, 0);
        },
        multiply: function(values, weights) {
            return values.reduce(function(a, v, i) { return a * Math.pow(v, weights[i]); }, 1);
        },
        average: function(values, weights) {
            var totalWeight = weights.reduce(function(a, w) { return a + w; }, 0);
            return values.reduce(function(a, v, i) { return a + v * weights[i]; }, 0) / totalWeight;
        },
        max: function(values) { return Math.max.apply(null, values); },
        min: function(values) { return Math.min.apply(null, values); },
        modulate: function(values) {
            return values.reduce(function(a, v) { return a * v; }, 1);
        }
    };

    function blend(blendMode, values, weights) {
        var fn = BLENDERS[blendMode] || BLENDERS.average;
        return fn(values, weights);
    }

    return { BLENDERS: BLENDERS, blend: blend };
})();
if (typeof window !== 'undefined') window.UPB_BLENDERS = UPB_BLENDERS;
```

### Phase 4: Wire to Existing System
**Goal:** Connect UPB to graph without breaking anything

#### 4.1 Create `upb/index.js` (~80 lines)
```javascript
// UPB Module Entry Point (IIFE PATTERN)
// NOTE: This file must be loaded AFTER scales, endpoints, bindings, blenders
const UPB = (function() {
    'use strict';

    // Aggregate all UPB sub-modules
    var SCALES = window.UPB_SCALES;
    var ENDPOINTS = window.UPB_ENDPOINTS;
    var BINDINGS = window.UPB_BINDINGS;
    var BLENDERS = window.UPB_BLENDERS;

    // Quick API shortcuts
    function bind(source, target, options) {
        return BINDINGS.defaultGraph.bind(source, target, options);
    }

    function apply(nodes, dataRanges) {
        return BINDINGS.defaultGraph.evaluateAll(nodes, dataRanges);
    }

    return {
        // Sub-modules
        SCALES: SCALES,
        ENDPOINTS: ENDPOINTS,
        BINDINGS: BINDINGS,
        BLENDERS: BLENDERS,

        // Quick API (delegates to default graph)
        bind: bind,
        apply: apply,

        // Backward compatibility aliases
        DATA_SOURCES: ENDPOINTS.SOURCES,
        VISUAL_TARGETS: ENDPOINTS.TARGETS,

        // Version
        VERSION: '0.1.0'
    };
})();
if (typeof window !== 'undefined') window.UPB = UPB;
```

#### 4.2 Update `control-bar.js` to use UPB
```javascript
// BEFORE (line 25-108 in control-bar.js)
const DATA_SOURCES = { ... };
const VISUAL_TARGETS = { ... };
const SCALES = { ... };

// AFTER - Delegate to UPB (loaded via window)
const DATA_SOURCES = window.UPB ? window.UPB.DATA_SOURCES : { /* fallback */ };
const VISUAL_TARGETS = window.UPB ? window.UPB.VISUAL_TARGETS : { /* fallback */ };
const SCALES = window.UPB ? window.UPB.SCALES.SCALES : { /* fallback */ };
```

#### 4.3 Script Loading Order (in template.html)
```html
<!-- UPB modules must load in dependency order -->
<script src="modules/upb/scales.js"></script>
<script src="modules/upb/endpoints.js"></script>
<script src="modules/upb/blenders.js"></script>
<script src="modules/upb/bindings.js"></script>
<script src="modules/upb/index.js"></script>
<!-- Then existing modules -->
<script src="modules/control-bar.js"></script>
```

### Phase 5: Integration Testing
**Goal:** Verify no visual regression

- [ ] Capture baseline screenshots
- [ ] Run visual diff after UPB integration
- [ ] Benchmark binding evaluation (<1ms per node)

---

## File Size Targets (Max 300 Lines)

| File | Target | Responsibility |
|------|--------|----------------|
| `upb/index.js` | ~80 | Entry point, exports |
| `upb/endpoints.js` | ~180 | Source/target definitions |
| `upb/scales.js` | ~120 | Scale functions |
| `upb/bindings.js` | ~250 | Binding graph logic |
| `upb/blenders.js` | ~150 | Blend mode functions |
| **Total** | **~780** | (vs control-bar.js 917 lines) |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing visualizations | Phase 4 uses delegation, not replacement |
| Performance regression | Benchmark before/after |
| Module loading order | UPB loads before control-bar |
| Type compatibility | Scale functions validate input types |

---

## Success Criteria

1. **Zero visual regression** - Existing mappings work identically
2. **Performance** - Binding evaluation <1ms per node
3. **Modularity** - Each file <300 lines, single responsibility
4. **Testable** - Unit tests for all scale/blend functions
5. **Documented** - JSDoc on all exports

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-21 | Claude + Leonardo | Initial RAG-validated plan |
