# Codome Edge Discovery

> **Date:** January 21, 2026
> **Status:** IMPLEMENTED - Boundary nodes and inferred edges live in pipeline
> **Metaphor:** Cartographers reading Braille in the dark - now with torches

---

## The Discovery

While classifying "orphan" nodes, we found the edge of our map. 120 nodes appeared disconnected:
- 10 are truly dead (orphans)
- 110 are alive but their callers are invisible to us

We called this a "fundamental limit of static analysis." **That was wrong.**

It's not a limit. It's **unmapped territory**.

---

## The Codome

**Codome** (n.): The totality of code that can interact with a system.

```
CODOME
├── Analyzed repo        ← We map this
├── Installed packages   ← pytest, lodash call into us
├── Runtime environment  ← Browser, Node invoke handlers
├── Build artifacts      ← HTML references JS
└── External consumers   ← Other repos import us
```

"Codebase" implies a single repo. "Codome" implies the full interaction space.

Our current map only shows edges WITHIN the analyzed repo. The 110 "invisible" nodes have edges from elsewhere in the codome.

### Clarification: CODOME vs Systems of Systems

| Concept | What It Is | Purpose |
|---------|------------|---------|
| **CODOME** | The full set of files/code under analysis (input scope) | Defines WHAT we analyze |
| **Systems of Systems** | Recursive composition theory (holons) | Explains HOW to think about structure |

**CODOME** is about analysis boundaries - the edges we can and cannot see.
**SoS** is about recursive composition - every level is a system made of systems.

These concepts are **orthogonal**:
- CODOME answers: "What is in our field of view?"
- SoS answers: "How is what we see organized internally?"

See `THEORY_EXPANSION_2026.md` Section 5 for Systems of Systems theory.

---

## The Unmapped Edges

| Edge Type | Source | Target | Count | Detector Status |
|-----------|--------|--------|-------|-----------------|
| JS import | `import {x}` | JS function | ~72 | **TODO: Task #6** |
| Class instantiation | `MyClass()` | Class definition | ~19 | **TODO: Task #7** |
| Test framework | pytest | test function | ~16 | **DONE: test_entry** |
| HTML reference | onclick, src | JS function | ? | Not started |
| Dynamic dispatch | getattr, eval | target | ? | Research needed |

---

## Edge Detector Specifications

### Detector #1: JS Import Edges (Task #6)

**Input patterns:**
```javascript
import { foo, bar } from './module'
import * as utils from '../utils'
const x = require('./helper')
```

**Output:** Edge from importing file → imported function/module

**Expected impact:** Eliminate ~72 cross_language orphans (60% of total)

---

### Detector #2: Class Instantiation Edges (Task #7)

**Input patterns:**
```python
obj = MyClass()
obj = MyClass(arg1, arg2)
result = SomeFactory.create()
```

**Output:** Edge from call site → class definition

**Expected impact:** Eliminate ~19 framework_managed orphans (16% of total)

---

### Detector #3: HTML → JS Edges (Future)

**Input patterns:**
```html
<button onclick="handleClick()">
<script src="app.js">
<div data-handler="processForm">
```

**Output:** Edge from HTML element → JS function

**Expected impact:** Unknown, requires HTML parsing capability

---

## The Cartographer's Creed

We don't accept blind spots. We don't say "fundamental limit."

When we find the edge of the map, we extend the map.

The codome is vast. Our job is to illuminate it.

---

## Visualization: The Parallel Edge System

**Key Insight:** A node might be connected to SOME things but disconnected from OTHERS. An "orphan" isn't necessarily isolated - it might have edges we can see AND edges we can't see.

### Two Edge Layers

```
LAYER 1: VISIBLE EDGES (current)
├── Structural: contains, inherits
├── Dependency: imports, calls
└── Semantic: decorates, triggers

LAYER 2: CODOME EDGES (new)
├── HTML → JS: onclick, src attributes
├── Test → Code: pytest/jest invocations
├── Framework → Instance: DI, decorators
├── External → Export: npm consumers
└── Dynamic → Target: eval, getattr
```

### Visual Representation

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Dashed edges** | Show invisible edges as dashed lines | Clear "missing link" indication | Where do they connect TO? |
| **Boundary nodes** | Virtual nodes for HTML, TestFramework, etc. | Shows codome sources | Adds visual noise |
| **Color coding** | Nodes colored by disconnection type | Simple, non-intrusive | Doesn't show relationships |
| **Toggle layer** | User can show/hide codome edges | Full picture available | Complexity in UI |

### Recommended Approach: Boundary Nodes + Toggle

Create synthetic "codome boundary" nodes that represent external sources:

```
[TestFramework] ----dashed----> test_user_login()
[HTMLTemplate]  ----dashed----> handleFormSubmit()
[BrowserRuntime] ---dashed----> window_onload()
```

These edges are:
- **Inferred** (not detected from code)
- **Confidence-scored** (based on patterns like test_ prefix, exports)
- **Toggleable** (user can hide codome layer)

### Schema Addition

```json
{
  "edge_type": "invokes",
  "family": "Codome",
  "source": "__codome__::pytest",
  "target": "tests/test_user.py::test_login",
  "inferred": true,
  "confidence": 0.95
}
```

---

## Implementation (January 21, 2026)

### What's Implemented

**Stage 6.8: Codome Boundary Generation** in `full_analysis.py`:

1. **Boundary Nodes Created:**
   - `__codome__::test_entry` (TestFramework) - pytest/jest invoke test functions
   - `__codome__::entry_point` (RuntimeEntry) - __main__, CLI scripts
   - `__codome__::framework_managed` (FrameworkDI) - decorators, dataclasses
   - `__codome__::cross_language` (HTMLTemplate) - JS called from HTML
   - `__codome__::external_boundary` (ExternalAPI) - npm consumers, public API
   - `__codome__::dynamic_target` (DynamicDispatch) - getattr, eval, reflection

2. **Inferred Edges:**
   - `edge_type: "invokes"`, `family: "Codome"`, `inferred: true`
   - `confidence` score from disconnection classification
   - Connect boundary nodes → disconnected functions

3. **Output Structure:**
   ```json
   {
     "codome_boundaries": {
       "boundary_nodes": [...],
       "inferred_edges": [...],
       "summary": {"test_entry": 100, "cross_language": 540, ...}
     },
     "kpis": {
       "codome_boundary_count": 6,
       "codome_inferred_edges": 619
     }
   }
   ```

### What's NOT Linked

Nodes with `reachability_source: "unreachable"` are deliberately NOT connected to boundary nodes. These are true dead code candidates that should be reviewed.

---

## Known Issues (January 21, 2026)

### BUG: Degree Calculation Includes ALL Edges

**Location:** `full_analysis.py:968-972`

**Problem:** When calculating `in_degree` and `out_degree` for topology classification, ALL edges are counted - including structural edges like `contains`. This means a function inside a file always has `in_degree >= 1` from its container, making "orphan" detection misleading.

```python
# Current (buggy):
for edge in edges:
    G.add_edge(src, tgt)  # ALL edges, no filter

# Should be:
for edge in edges:
    if edge.get('family') in ['Dependency', 'Semantic', 'Inheritance']:
        G.add_edge(src, tgt)  # Only call-graph edges
```

**Impact:** The `disconnection` classification currently works around this by looking at naming patterns, but the topology_role (orphan/root/leaf/hub) is computed from incorrect degree values.

**Fix Required:** Separate degree calculations:
- `call_in_deg` / `call_out_deg` - for disconnection analysis
- `total_in_deg` / `total_out_deg` - for structural analysis

### Rendering Stack Clarification

The visualization uses **Three.js + 3d-force-graph**, NOT raw WebGL:

```html
<!-- template.html -->
<script src="https://unpkg.com/three@0.149.0/build/three.min.js"></script>
<script src="https://unpkg.com/3d-force-graph@1.73.3/dist/3d-force-graph.min.js"></script>
```

Any claims about "migrating to WebGL puro" are incorrect. The stack is:
- `3d-force-graph` - high-level force-directed graph library
- `Three.js` - underlying 3D rendering engine
- `WebGL` - browser API (abstracted by Three.js)

---

## Next Steps

### Pipeline Fixes
1. **Fix edge filtering bug** - separate call_in_deg from total_in_deg
2. Build JS import edge detector (#6)
3. Build class instantiation edge detector (#7)

### UI Implementation
4. **Render boundary nodes** in visualization (they exist in data, not shown in UI)
5. **Add toggle** for codome layer (show/hide inferred edges)
6. **Edge styling** - dashed lines for inferred edges

### Validation
7. Re-run analysis after fixes
8. Count remaining true orphans
9. Repeat until the map is complete

---

## Progress Tracker

| Date | Orphans | After Detector | Remaining |
|------|---------|----------------|-----------|
| Jan 21, 2026 | 684 | (baseline) | 684 |
| Jan 21, 2026 | 684 | **Codome Boundaries** | 65 unreachable |
| | | JS imports (#6) | ~48 (est.) |
| | | Class inst. (#7) | ~29 (est.) |
| **Target** | | All detectors | **~10 true orphans** |

### Latest Run (src/ directory):
- Total disconnected: 684
- Linked via codome boundaries: 619
- Remaining unreachable: 65 (9.5% - true dead code candidates)
