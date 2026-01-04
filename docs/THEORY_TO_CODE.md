# Theory-to-Code Mapping

> This document shows exactly which theoretical concepts are implemented,
> where they live in code, and what outputs they produce.

---

## Implementation Status Overview

| Theory Concept | Status | Scale Level | Code Location |
|----------------|--------|-------------|---------------|
| Three Layers | Partial | - | Operates on Layer 2 (symbols) |
| Scale Axis | Planned | L3-L4 | Not yet explicit in output |
| Bosons/Fermions | Not Implemented | L3 | - |
| Constructor Principle | Not Implemented | L3-L4 | - |
| Markov Dynamics | Not Implemented | L3 | Static graph only |
| Self-Proof | **Implemented** | L3-L4 | `validation/self_proof.py` |

---

## What's Implemented (v0.1)

### Components (Nodes)

**Theory**: Software entities at various scale levels.

**Implementation**:
```
File: src/core/validation/self_proof.py
Function: add_component()
```

| Component Type | Scale Level | Detection |
|----------------|-------------|-----------|
| Function | L3 | AST: `ast.FunctionDef` |
| Method | L3 | AST: `ast.FunctionDef` inside `ast.ClassDef` |
| Class | L4 | AST: `ast.ClassDef` |

**Output Fields**:
```python
{
    "key": "path/to/file.py::ComponentName",
    "name": "ComponentName",
    "type": "function" | "method" | "class",
    "calls": ["called_name1", "called_name2"],
    "decorators": ["@decorator.name"],
    "is_main_entry": True | False
}
```

---

### Edges (Connections)

**Theory**: Relationships between components (calls, imports, containment).

**Implementation**:
```
Proof (call edges only):
```
File: src/core/validation/self_proof.py
Function: _build_real_call_graph()
```
```

| Edge Type | Status | Detection |
|-----------|--------|-----------|
| Call edges | **Implemented (proof)** | AST: `ast.Call` nodes |
| Import edges | **Implemented (structural)** | Module→file→node resolution |
| Containment | Implicit only | Key format includes class name |

**Outputs**:
```python
proof_edges = [
    {"source": "file.py::caller", "target": "file.py::callee", "verified": True}
]

unified_analysis.edges = [
    {"edge_type": "calls", "resolution": "resolved_internal"},
    {"edge_type": "imports", "resolution": "resolved_internal|external|unresolved"}
]
```

Structural import resolver:
```
File: src/core/edge_extractor.py
Functions: resolve_import_target_to_file(), resolve_edges()
```

---

### Resolution Buckets

**Theory**: Classify call targets by what we know about them.

**Implementation**:
```
Calls (proof):
  File: src/core/validation/self_proof.py
  Function: _classify_call_target()
  Constants: BUILTINS, STDLIB_MODULE_ROOTS, STDLIB_SYMBOLS

Imports (structural):
  File: src/core/edge_extractor.py
  Function: resolve_import_target_to_file()
```

| Bucket | Theory Concept | Detection Logic |
|--------|----------------|-----------------|
| `resolved_internal` | Internal code | Name exists in `name_to_keys` |
| `external` (strict) | Known external | Builtins OR qualified stdlib |
| `external` (not strict) | Possibly external | Bare stdlib symbols |
| `unresolved` | Unknown | Everything else |

**Output Metrics**:
```json
{
    "calls_total": 6630,
    "calls_resolved_internal": 935,
    "calls_external": 1693,
    "calls_external_strict": 1693,
    "calls_unresolved": 4002
}
```

**Import Diagnostics (unified_analysis.stats)**:
```json
{
  "import_resolution": {
    "attempted": 1268,
    "resolved_internal": 212,
    "external": 770,
    "unresolved": 286,
    "resolved_to_file_no_node": 0,
    "ambiguous": 13
  },
  "top_unresolved_import_roots": ["models", "types", "constants"]
}
```

File nodes are emitted for every scanned `.py` file to allow import targets
to resolve to a canonical file-node id even when the file has no symbols.

---

### Entrypoints

**Theory**: Roots for reachability traversal.

**Implementation**:
```
File: src/core/validation/self_proof.py
Functions:
  - _is_entry_point()
  - _find_main_block_calls()
  - _get_decorator_names()
```

| Entrypoint Type | Detection | Fixture |
|-----------------|-----------|---------|
| `__main__` calls | AST: Name() in if-block | `toy_main_name_only` |
| CLI decorators | Pattern match on decorators | `toy_entry_click` |
| Web decorators | Pattern match on decorators | `toy_entry_fastapi` |
| Test functions | Name starts with `test_` | `toy_entry_pytest` |
| main() function | Name equals `main` | `toy_entry_main` |

**Output Metrics**:
```json
{
    "entry_points": 45,
    "reachable_from_entry": 199,
    "reachability": 17.2
}
```

---

### Self-Proof Score

**Theory**: Measure of structural coherence.

**Implementation**:
```
File: src/core/validation/self_proof.py
Function: _calculate_proof_score()
```

**Formula**:
```python
weights = {
    "registry_accuracy": 0.2,
    "connection_coverage": 0.3,
    "edge_accuracy": 0.3,
    "reachability": 0.2
}
proof_score = sum(metric * weight for metric, weight in weights.items())
is_self_proving = proof_score >= 80.0
```

---

## What's NOT Implemented Yet

### Scale Level Field (v0.2 planned)

**Theory**: Every component has an explicit scale level.

**Planned Implementation**:
```python
# Add to component dict
"scale_level": 3  # function/method
"scale_level": 4  # class
"scale_level": 5  # module (future)
```

---

### Statefulness Classification (v0.2 planned)

**Theory**: Bosons (stateless) vs Fermions (stateful).

**Planned Implementation**:
```python
# Add to component dict
"statefulness": "stateless" | "stateful" | "unknown"
"statefulness_signals": ["self_mutation", "io_call", "global_write"]
```

**Detection Signals**:
- `stateful`: `self.x = ...`, global assignment, I/O calls
- `stateless`: Pure computation, no mutation detected
- `unknown`: Can't determine

---

### Constructor Tagging (v0.3 planned)

**Theory**: Structure-introducing operations.

**Planned Implementation**:
```python
# Add to component dict
"constructor_kind": "init" | "factory" | "builder" | "none"
```

**Detection**:
- `init`: Method named `__init__`
- `factory`: Function named `from_*`, `create_*`
- `builder`: Function named `build_*`
- `none`: Default

---

### Markov Importance (v0.4+ planned)

**Theory**: Transition probabilities and stationary distribution.

**Planned Implementation**:
```python
# Add to proof_metrics
"component_importance": {
    "file.py::main": 0.15,
    "file.py::helper": 0.02
}
```

**Options**:
- PageRank on call graph (static approximation)
- Edge weights from call frequency
- Runtime trace integration (future)

---

## File Map

| File | Theory Concepts | Status |
|------|-----------------|--------|
| `src/core/validation/self_proof.py` | Components, Edges, Resolution, Entrypoints, Proof Score | Implemented |
| `tests/fixtures/*` | Behavior locks for all rules | Implemented |
| `docs/SPEC.md` | Frozen specification | Implemented |
| `docs/THEORY_QUICK_START.md` | Concise conceptual intro | Implemented |
| `THEORY.md` (root) | Full conceptual framework | Implemented |
| `STANDARD_CODE.md` | Canonical theory reference | Implemented |
| `docs/THEORY_TO_CODE.md` | This file | Implemented |

---

## How to Extend

When adding a new theory concept:

1. **Document in STANDARD_CODE.md or THEORY.md** (conceptual description)
2. **Add to this file** (implementation mapping)
3. **Implement in self_proof.py** (actual code)
4. **Add to SPEC.md** (output schema)
5. **Create fixture** (behavior lock)
6. **Add test** (regression prevention)

The order matters: theory -> mapping -> code -> spec -> fixture -> test.
