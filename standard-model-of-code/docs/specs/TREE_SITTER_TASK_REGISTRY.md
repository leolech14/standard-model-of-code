# TREE-SITTER TASK REGISTRY

> Master task registry with dual-dimension confidence scoring.
>
> **Created:** 2026-01-21
> **Last Updated:** 2026-01-21 (RAG verified, 6 tasks READY)
> **Validation Source:** `TREE_SITTER_VALIDATION_REPORT.md`
> **Status:** RAG VERIFIED - ALIGNMENT CONFIRMED

---

## CONFIDENCE METHODOLOGY

**Confidence = min(Factual, Alignment)**

| Dimension | Question | Verification Method |
|-----------|----------|---------------------|
| **Factual (F)** | "Will this technically work?" | Live testing, API verification, code grep |
| **Alignment (A)** | "Does this fit the Single Ideal Truth?" | Codebase pattern analysis, theory compatibility |

### Confidence Thresholds

| Level | Meaning | Action |
|-------|---------|--------|
| **95%+** | Verified factual + verified aligned | **READY - Execute** |
| **90-94%** | High confidence, minor verification needed | Almost ready |
| **85-89%** | Good confidence but gaps remain | **NOT READY** - needs work |
| **70-84%** | Moderate confidence | Needs more verification |
| **<70%** | Low confidence | DO NOT EXECUTE - needs research |

**The bar is 95%. Below that = NOT READY.**

---

## EVIDENCE GATHERED (2026-01-21)

### Evidence 1: External Config Pattern IS Established

**Grep Results:** Collider uses 30+ external config files

| File Type | Examples | Purpose |
|-----------|----------|---------|
| `.yaml` | `ATOMS_TIER0_CORE.yaml`, `ATOMS_TIER1_STDLIB.yaml`, `rules.yaml` | Atom definitions, validation rules |
| `.json` | `atoms.json`, `roles.json`, `patterns.json`, `appearance.tokens.json` | Configs, tokens, registries |

**Source:** `grep -r "\.yaml\|\.json" src/ --include="*.py"`

**Conclusion:** External configuration files ARE an established pattern in Collider.

---

### Evidence 2: atom_loader.py Pattern

**File:** `src/core/atom_loader.py`

```python
# Pattern: Functions that load from external files
def load_yaml_atoms(yaml_path: Path) -> List[Dict]
def load_json_atoms(json_path: Path) -> Dict
def build_unified_taxonomy(patterns_dir: Path) -> Dict

# Loads from patterns/ directory:
# - src/patterns/atoms.json
# - src/patterns/ATOMS_TIER0_CORE.yaml
# - src/patterns/ATOMS_TIER1_STDLIB.yaml
# - src/patterns/ATOMS_TIER2_ECOSYSTEM.yaml
```

**Conclusion:** External files in `patterns/` directory with loader functions is proven pattern.

---

### Evidence 3: Mixed Loader Pattern

**Grep Results:** Both class and function loaders exist

| Loader | Type | File |
|--------|------|------|
| `ProfileLoader` | CLASS | `profile_loader.py` |
| `atom_loader` | FUNCTIONS | `atom_loader.py` |
| `role_registry` | CLASS + FUNCTIONS | `role_registry.py` |

**Conclusion:** Both patterns are acceptable. Choose based on complexity.

---

### Evidence 4: CURRENT Query Pattern is Inline

**File:** `src/core/tree_sitter_engine.py:382-441`

```python
# CURRENT pattern: Inline triple-quoted strings
if parser_name == "rust":
    query_scm = """
    (function_item name: (identifier) @func.name) @func
    (struct_item name: (type_identifier) @struct.name) @struct
    """
elif parser_name == "go":
    query_scm = """
    (function_declaration name: (identifier) @func.name) @func
    """
# ... etc

query = tree_sitter.Query(tree_sitter.Language(lang_obj), query_scm)
```

**Conclusion:** Current implementation uses inline strings, NOT external files.

---

### Evidence 5: RAG AI Architect Ruling (2026-01-21)

**Query:** `analyze.py --set theory --mode architect`

**Ruling:** External .scm files in `src/queries/` is **ALLOWED**

**Key Points from AI Architect:**
1. **RPBL Analysis:** Separating queries increases PURITY (no side effects in code)
2. **Atom Isolation:** NOT violated - queries define atoms, tighter linkage is better
3. **Pattern Match:** Mirrors `atom_loader.py` and `token_resolver.py` patterns
4. **Constraints:**
   - Mirror loading pattern (centralized directory + dedicated loader)
   - Maintain Atom Isolation
   - Avoid Dependency Cycles
   - DO NOT add to `COLLIDER_ARCHITECTURE.md` structural registry

**Verdict:** MINOR change, minimal risk to architectural patterns.

---

### Evidence 6: Loader Pattern (RAG Forensic)

**Query:** `analyze.py --set body --mode forensic`

**Findings:**
| Aspect | Evidence | Citation |
|--------|----------|----------|
| Class vs Functions | **Functions preferred** | `atom_loader.py:L20` |
| Location | `src/core/` adjacent to modules they augment | `atom_loader.py:L3` |
| Integration | Provides resources for classification, not direct TS engine integration | Workflow phases |

**Pattern Template:**
```python
from pathlib import Path
from typing import Dict, List

def load_scm_queries(queries_path: Path) -> Dict[str, str]:
    """Load .scm queries from directory."""
    ...
```

---

### Evidence 7: Schema Flexibility

**File:** `src/core/unified_analysis.schema.json`

**Finding:** Schema uses `additionalProperties: true`

```json
{
  "nodes": {"items": {"additionalProperties": true}},
  "edges": {"items": {"additionalProperties": true}},
  "additionalProperties": true
}
```

**Conclusion:** Schema is intentionally flexible. Adding `error_count`, `scope_info`, or other fields requires NO schema changes.

---

## ARCHITECTURE DECISION: MADE + RAG VERIFIED

**Decision:** External `.scm` files in `src/queries/` directory

**Principle Applied:** Most comprehensive, most persistent, most aligned, least workaround.

### Why External .scm Files

| Criterion | External .scm | Inline Strings | Python Constants |
|-----------|---------------|----------------|------------------|
| **Comprehensive** | Industry standard (nvim-treesitter, Zed) | Limited to this project | Compromise |
| **Persistent** | Ecosystem compatible, won't change | Tied to Python code | Python-only |
| **Aligned** | Matches atom_loader pattern | Matches current (not ideal) | Middle ground |
| **Workaround?** | NO - proper solution | YES - avoids file mgmt | YES - avoids .scm |

### Implementation Pattern (Matches atom_loader.py)

```
src/
├── patterns/                    # EXISTING - atoms, roles
│   ├── atoms.json
│   ├── ATOMS_TIER0_CORE.yaml
│   └── ...
└── queries/                     # NEW - tree-sitter queries
    ├── __init__.py              # Query loader functions
    ├── python/
    │   ├── definitions.scm      # Function/class extraction
    │   ├── locals.scm           # Scope tracking
    │   └── patterns.scm         # Atom detection
    ├── javascript/
    │   └── ...
    └── ...
```

### Revised Alignment Score: 95% (RAG VERIFIED)

| Factor | Score | Evidence |
|--------|-------|----------|
| Matches atom pattern | +30% | `atom_loader.py` loads from `patterns/` |
| Matches tokens pattern | +20% | `token_resolver.py` loads from tokens dir |
| Industry standard | +15% | nvim-treesitter, Zed, GitHub Semantic |
| Proper solution, not workaround | +15% | Full ecosystem compatibility |
| **RAG Architect Approval** | +10% | Evidence 5: "ALLOWED", "MINOR change" |
| **Schema Flexibility** | +5% | Evidence 7: `additionalProperties: true` |

**Final Alignment: 95%** (RAG verified via analyze.py)

---

## REVISED CONFIDENCE SCORES

Based on evidence gathered:

### Phase 1: Foundation (RAG VERIFIED)

| Task | Factual | Alignment | Overall | Status |
|------|---------|-----------|---------|--------|
| P1-01: Create queries/ directory | 99% | **95%** | **95%** | ✅ READY |
| P1-02: Query loader functions | 95% | **95%** | **95%** | ✅ READY |
| P1-03: Python definitions.scm | 90% | **95%** | **90%** | NOT READY |
| P1-04: JS/TS definitions.scm | 90% | **95%** | **90%** | NOT READY |
| P1-05: Go definitions.scm | 85% | **95%** | **85%** | NOT READY |
| P1-06: Rust definitions.scm | 85% | **95%** | **85%** | NOT READY |
| P1-07: Refactor engine to use loader | 80% | **95%** | **80%** | NOT READY |
| P1-08: ERROR node detection | 99% | **95%** | **95%** | ✅ READY |
| P1-09: Error count in schema | 95% | **95%** | **95%** | ✅ READY |
| P1-10: Tests | 99% | **95%** | **95%** | ✅ READY |
| P1-11: Documentation | 99% | **95%** | **95%** | ✅ READY |

**Phase 1: 6 tasks READY (95%+), 5 tasks need factual verification**

---

### Phase 2: Scope Analysis

| Task | Factual | Alignment | Overall | Evidence |
|------|---------|-----------|---------|----------|
| P2-01: Python locals.scm | 75% | **65%** | **65%** | D5:STATE is in MODEL.md |
| P2-02: JS/TS locals.scm | 75% | **65%** | **65%** | Same |
| P2-03: ScopeAnalyzer | 65% | **60%** | **60%** | Function pattern matches atom_loader |
| P2-04: Build scope tree | 60% | **55%** | **55%** | Algorithm needs validation |
| P2-05: Unused variables | 80% | **60%** | **60%** | Could serve health metrics |
| P2-06: Shadowing detection | 85% | **60%** | **60%** | Same |
| P2-07: Add scope to schema | 90% | **70%** | **70%** | Extends existing pattern |
| P2-08: Integrate with edge_extractor | 60% | **50%** | **50%** | Significant refactor risk |
| P2-09: D5_STATE extraction | 70% | **80%** | **70%** | D5 explicitly in MODEL.md |
| P2-10: Tests | 99% | **85%** | **85%** | Tests always aligned |

**Phase 2 Average: 64%** (was 45%)

---

### Phase 3: Control Flow

| Task | Factual | Alignment | Overall | Evidence |
|------|---------|-----------|---------|----------|
| P3-01: ControlFlowAnalyzer | 80% | **60%** | **60%** | Function pattern acceptable |
| P3-02: Cyclomatic complexity | 95% | **85%** | **85%** | Health metrics exist in Collider |
| P3-03: Nesting depth | 95% | **85%** | **85%** | Part of quality metrics |
| P3-04: Early returns | 85% | **65%** | **65%** | Useful but not in theory |
| P3-05: Recursion detection | 70% | **55%** | **55%** | Unclear priority |
| P3-06: Add metrics to schema | 90% | **80%** | **80%** | Extends existing pattern |
| P3-07: Update health scoring | 75% | **85%** | **75%** | Health scoring exists |
| P3-08: Tests | 99% | **85%** | **85%** | Tests always aligned |

**Phase 3 Average: 74%** (was 60%)

---

### Phase 4: Pattern Detection

| Task | Factual | Alignment | Overall | Evidence |
|------|---------|-----------|---------|----------|
| P4-01: Python patterns.scm | 70% | **80%** | **70%** | Atom detection is core mission |
| P4-02: JS/TS patterns.scm | 70% | **80%** | **70%** | Same |
| P4-03: Integrate with classifier | 65% | **80%** | **65%** | Improves existing classification |
| P4-04: RPBL extraction | 60% | **90%** | **60%** | RPBL explicitly in MODEL.md |
| P4-05: D6_EFFECT (purity) | 55% | **90%** | **55%** | D6 explicitly in MODEL.md |
| P4-06: D7_LIFECYCLE | 65% | **90%** | **65%** | D7 explicitly in MODEL.md |
| P4-07: Update confidence scoring | 70% | **85%** | **70%** | D8:TRUST in MODEL.md |
| P4-08: Tests | 99% | **85%** | **85%** | Tests always aligned |

**Phase 4 Average: 68%** (was 50%)

---

### Phase 5: Advanced Features

| Task | Factual | Alignment | Overall | Evidence |
|------|---------|-----------|---------|----------|
| P5-01: Incremental parsing | 90% | **45%** | **45%** | Optimization, not theory-serving |
| P5-02: File watcher | 70% | **35%** | **35%** | Not in current scope |
| P5-03: Python SQL injection | 50% | **40%** | **40%** | Unclear value |
| P5-04: JS GraphQL injection | 50% | **40%** | **40%** | Same |
| P5-05: Injection parsing | 40% | **35%** | **35%** | Architecture risk |
| P5-06: Data flow graph | 55% | **55%** | **55%** | Could serve D6:EFFECT |
| P5-07: Cross-function tracking | 40% | **45%** | **40%** | Complexity vs value |
| P5-08: highlights.scm | 80% | **30%** | **30%** | Not core mission |
| P5-09: Integrate highlights | 60% | **30%** | **30%** | Same |

**Phase 5 Average: 39%** (was 35%)

---

## EXECUTIVE SUMMARY (RAG VERIFIED)

**Threshold: 95% = READY. Below 95% = NOT READY.**

| Phase | Ready Tasks | Status |
|-------|-------------|--------|
| Phase 1: Foundation | **6 of 11** | P1-01, P1-02, P1-08, P1-09, P1-10, P1-11 ✅ READY |
| Phase 2: Scope Analysis | 0 of 10 | Alignment raised, factual gaps remain |
| Phase 3: Control Flow | 0 of 8 | Alignment raised, factual gaps remain |
| Phase 4: Pattern Detection | 0 of 8 | Alignment raised, factual gaps remain |
| Phase 5: Advanced Features | 0 of 9 | DEFER - low alignment |

**Status: 6 TASKS READY TO EXECUTE**

| Task | Confidence | Description |
|------|------------|-------------|
| P1-01 | 95% | Create `src/queries/` directory structure |
| P1-02 | 95% | Implement query loader functions |
| P1-08 | 95% | ERROR node detection |
| P1-09 | 95% | Error count in schema |
| P1-10 | 95% | Tests for query loader |
| P1-11 | 95% | Documentation |

---

## PATH TO 95% CONFIDENCE

**6 tasks are READY. Here's how to raise the remaining 5 in Phase 1:**

### Remaining Phase 1 Tasks (Need Factual Verification)

| Task | Current | Gap | What's Needed |
|------|---------|-----|---------------|
| P1-03: Python definitions.scm | 90% | -5% | Write actual .scm, validate node extraction |
| P1-04: JS/TS definitions.scm | 90% | -5% | Same |
| P1-05: Go definitions.scm | 85% | -10% | Verify Go grammar node types |
| P1-06: Rust definitions.scm | 85% | -10% | Verify Rust grammar node types |
| P1-07: Refactor engine | 80% | -15% | Backward compat plan, prototype |

### Verified Questions (Answered by RAG)

| Question | Answer | Source |
|----------|--------|--------|
| Where should queries/ live? | `src/queries/` | Evidence 5: AI Architect |
| What's the loader function signature? | `load_scm_queries(path: Path) -> Dict[str, str]` | Evidence 6: Forensic |
| Class or functions? | **Functions** | Evidence 6: `atom_loader.py:L20` |
| Schema changes needed? | **NO** - `additionalProperties: true` | Evidence 7 |

### Open Questions (For Factual Verification)

| Question | Blocks | How to Answer |
|----------|--------|---------------|
| Exact Python node types for definitions? | P1-03 | Live test with py-tree-sitter |
| Exact JS/TS node types? | P1-04 | Live test |
| Exact Go node types? | P1-05 | Live test |
| Exact Rust node types? | P1-06 | Live test |
| Backward compat migration path? | P1-07 | Write migration plan |

---

## NEXT STEPS

**Goal:** Execute the 6 ready tasks, then raise remaining 5 to 95%.

### Execution Order (Dependencies)

```
P1-01 (queries/ dir) ─┬─► P1-02 (loader functions)
                      │
P1-10 (tests) ────────┘

P1-08 (ERROR detection) ─► P1-09 (error schema)

P1-11 (documentation) ─── Can run in parallel
```

### Recommended Order

1. **P1-01**: Create `src/queries/` directory structure
2. **P1-02**: Implement query loader functions
3. **P1-10**: Write tests (validates P1-01, P1-02)
4. **P1-08**: ERROR node detection
5. **P1-09**: Error count in schema
6. **P1-11**: Documentation

### After Phase 1 Foundation

1. **Live test** Python/JS/Go/Rust node types → raise P1-03 to P1-06 to 95%
2. **Write migration plan** for P1-07
3. **Execute P1-03 to P1-07** to complete Phase 1

---

## DOCUMENT STATUS

- [x] Confidence methodology defined (95% = READY)
- [x] Evidence gathered from codebase (grep, file reads)
- [x] Dual-dimension scoring applied
- [x] Architecture decision made (external .scm files)
- [x] **RAG verification completed** (analyze.py)
- [x] **6 tasks at 95%** ← ACHIEVED
- [ ] Execute 6 ready tasks
- [ ] Raise remaining 5 to 95%
- [ ] Complete Phase 1

**Status:** 6 TASKS READY. Execute P1-01 first.
