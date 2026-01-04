# SMOC Specification v0.1
**Standard Model of Code - Implementation Specification**

> This document is the single source of truth for what the self-proof system
> measures, how it classifies entities, and what the output schema looks like.
> Both human developers and AI agents must adhere to this spec.

---

## 1. Scope

### In Scope
- Python source files (`.py`)
- Directories specified as `target_path`

### Out of Scope (v0.1)
- `__init__.py` files (excluded via `shim_policy`)
- Non-Python files
- Generated code, vendored dependencies
- Test files (included in fixtures mode only)

---

## 2. Node Types (Components)

| Type | Key Format | Scale Level |
|------|------------|-------------|
| Function | `rel_path::function_name` | L3 |
| Method | `rel_path::Class.method_name` | L3 |
| Class | `rel_path::ClassName` | L4 |
| Module (file node) | `rel_path::module_name` | L2 |

File nodes are emitted for every scanned `.py` file. The module name is
derived from the filename (`foo.py` → `foo`, `pkg/__init__.py` → `pkg`).
If a collision exists, a stable suffix like `.__file__` is applied to the
file-node name to keep ids unique.

### Component Fields
```python
{
    "key": str,           # Unique identifier
    "name": str,          # Short name
    "rel_path": str,      # Relative file path
    "line": int,          # Line number
    "type": str,          # "function" | "method" | "class" | "module"
    "calls": List[str],   # Called names (AST-extracted)
    "decorators": List[str],  # Decorator strings
    "is_main_entry": bool # True if called in __main__ block
}
```

---

## 3. Edge Types

### Proof Edges (strict)
- **Edge type**: `calls` only
- **Source**: Component making the call
- **Target**: Called name resolved to internal component keys
- **Direction**: Caller -> Callee
- **Guardrail**: Proof graph uses `edge_type=="calls" AND resolution=="resolved_internal"` only

### Structural Edges (diagnostic)
- **Imports**: `edge_type=="imports"` is now emitted in `unified_analysis.json`
- **Purpose**: Structural/topology diagnostics only; does not affect self-proof
- **Resolution**: Module→file→node resolution when deterministic

---

## 4. Resolution Buckets

Resolution is determined by `_classify_call_target()` for calls and by
module→file resolution for imports.

| Bucket | Condition | Strict? |
|--------|-----------|---------|
| `resolved_internal` | Target exists in `name_to_keys` | N/A |
| `external` (strict) | Builtin name (print, len, etc.) | Yes |
| `external` (strict) | Qualified stdlib call (os.path.join) | Yes |
| `external` (not strict) | Bare stdlib symbol (Path, Counter) | No |
| `unresolved` | None of the above | N/A |

### Guardrail: Internal Always Wins
If a name exists in `name_to_keys`, it is **always** `resolved_internal`,
even if it shadows a builtin or stdlib name.

### Strict vs Non-Strict External
- **Strict**: Definitively external (builtins, qualified stdlib)
- **Non-strict**: Could be shadowed by internal definition (bare symbols like `Path`)

### Third-Party Calls
Third-party qualified calls (`requests.get`, `numpy.array`) are **unresolved**
unless import-based evidence exists. No curated allowlist is maintained.

### Import Resolution (module→file→node)
- Resolution attempts for `edge_type=="imports"`:
  1) `<target_root>/<module_path>.py`
  2) `<target_root>/<module_path>/__init__.py`
- Ambiguous match (both exist) → unresolved (`metadata.import_resolution="ambiguous"`)
- Relative imports (`.foo`, `..bar`) → unresolved (`metadata.import_resolution="relative_import"`)
- Deterministic internal hit:
  - `resolution="resolved_internal"`
  - `target` rewritten to canonical file-node id
  - `confidence=1.0`

Import resolution is **structural only** and never changes proof rules.

---

## 5. Entrypoint Rules (Ordered)

Entrypoints are detected by `_is_entry_point()` in this order:

| Priority | Rule | Detection Method | Mode |
|----------|------|------------------|------|
| 1 | `__main__` block calls | AST: direct `Name()` calls only | All |
| 2 | CLI decorators | Pattern: `click.command`, `typer.command`, etc. | All |
| 3 | Web route decorators | Pattern: `app.get`, `router.post`, etc. | All |
| 4 | Test functions | Name pattern: `test_*` in test files | **Fixture only** |
| 5 | Main function | Name pattern: `main` | All |

### __main__ Block Policy
- **Detected**: Direct function calls like `main()`, `cli()`
- **NOT Detected**: Attribute calls like `app.run()`, `uvicorn.run(app)`
- **Rationale**: Prevents false positives where `run()` becomes entrypoint

### Test Entrypoint Policy
- **Production mode** (`include_tests_as_entrypoints=False`): Tests are NOT entrypoints
- **Fixture mode** (`include_tests_as_entrypoints=True`): Tests ARE entrypoints
- **Rationale**: Production proof measures architecture intent; tests inflate reachability

---

## 6. Reachability Definition

Reachability is computed from entrypoints via **resolved_internal call edges only**.

### What Counts
- `resolved_internal` call edges (component A calls component B, B exists)

### What Does NOT Count
- Import edges (loading a module ≠ executing it)
- Containment edges (class contains method - implicit in key format)
- External or unresolved edges

### Policy
This is **non-negotiable for proof soundness**. Reachability measures what code
can actually be executed from entrypoints, not what code is imported.

---

## 7. Scoring Formula

```python
SCORE_WEIGHTS = {
    "registry_accuracy": 0.2,
    "connection_coverage": 0.3,
    "edge_accuracy": 0.3,
    "reachability": 0.2
}

proof_score = sum(metric * weight for metric, weight in SCORE_WEIGHTS.items())
```

### Thresholds
- `is_self_proving = True` when `proof_score >= 80.0`

---

## 8. Output Schema (proof_metrics)

```json
{
    "proof_metrics_version": "1.0",

    "calls_total": 6630,
    "calls_resolved_internal": 935,
    "calls_external": 1693,
    "calls_external_strict": 1693,
    "calls_unresolved": 4002,

    "total_edges": 946,
    "verified_edges": 946,
    "edge_accuracy": 100.0,

    "connected_components": 852,
    "isolated_components": 308,
    "connection_coverage": 73.4,

    "entry_points": 45,
    "reachable_from_entry": 199,
    "reachability": 17.2,

    "definitions": {
        "edge_set": "calls",
        "resolution": "resolved_internal",
        "entrypoint_policy": "rule-based only",
        "test_entrypoint_policy": "exclude",
        "shim_policy": "exclude __init__.py",
        "external_policy": "builtins+stdlib_roots (strict)",
        "reachability_edges": "resolved_internal only"
    }
}
```

### Output Schema (import diagnostics)
```json
{
  "stats": {
    "import_resolution": {
      "attempted": 1268,
      "resolved_internal": 212,
      "external": 770,
      "unresolved": 286,
      "resolved_to_file_no_node": 0,
      "ambiguous": 13
    },
    "top_unresolved_import_roots": [
      "models", "types", "constants", "import_extractor", "refactoring_strategy"
    ]
  }
}
```

### Schema Stability
- Fields in `proof_metrics` are **append-only** (new fields may be added)
- Existing field names and semantics must not change without version bump
- The `definitions` dict documents current policies

---

## 9. Fixtures as Executable Spec

Each fixture in `tests/fixtures/` locks a specific behavior:

| Fixture | Tests |
|---------|-------|
| `toy_linear` | Basic call chain resolution |
| `toy_cycle` | Cycle handling without infinite loop |
| `toy_external` | External (stdlib) classification |
| `toy_unresolved` | Dynamic/unknown calls |
| `toy_entry_main` | main() entrypoint detection |
| `toy_entry_click` | CLI decorator detection |
| `toy_entry_fastapi` | Web decorator detection |
| `toy_entry_pytest` | Test function detection |
| `toy_self_resolution` | self.method() resolution |
| `toy_main_name_only` | __main__ Name-only policy |
| `toy_import_internal` | Import resolves to internal module |
| `toy_import_ambiguous` | Ambiguous import remains unresolved |
| `toy_import_file_node` | Import resolves to file-node with no symbols |

---

## 10. Known Limitations (v0.1)

1. **Limited import resolution**: Absolute module→file only; relative imports remain unresolved
2. **No containment edges**: Class doesn't "contain" methods in graph
3. **No third-party detection**: Only stdlib/builtins, not installed packages
4. **No alias resolution**: `import x as y` not tracked
5. **No `from x import *`**: Star imports ignored
6. **No framework launchers**: `app.run()` in __main__ not detected as entrypoint

---

## 11. Changelog

### v0.1.2 (2025-01-03)
- Emit file-level module nodes for all `.py` files
- Import resolution targets file-node ids (resolved_to_file_no_node → 0)
- Added `toy_import_file_node` fixture

### v0.1.1 (2025-01-03)
- Added `proof_metrics_version: "1.0"` to schema
- Added `include_tests_as_entrypoints` flag (default: False)
- Added `test_entrypoint_policy` to definitions
- Added `reachability_edges` to definitions
- Fixed `__main__` detection to only use direct `Name()` calls
- Added `toy_main_name_only` fixture

### v0.1 (2025-01-03)
- Initial frozen specification
- Node types: function, method, class
- Edge type: calls only
- Resolution: internal, external, unresolved with strict distinction
- Entrypoints: rule-based with __main__, decorators, test patterns
- Scoring: 4-factor weighted formula
