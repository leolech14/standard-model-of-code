# TREE-SITTER INTEGRATION SPECIFICATION

> Comprehensive guide for leveraging Tree-sitter's full capabilities in Collider.
>
> **Status:** Living Document
> **Created:** 2026-01-21
> **Last Updated:** 2026-01-21
> **Confidence Level:** Research Complete, Implementation Pending
>
> **IMPORTANT:** See `TREE_SITTER_VALIDATION_REPORT.md` for evidence-based validation.
> That document contains verified test results and supersedes any assumptions here.

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Tree-sitter Architecture](#2-tree-sitter-architecture)
3. [Capability Inventory](#3-capability-inventory)
4. [Theory Compatibility Matrix](#4-theory-compatibility-matrix)
5. [Tool Compatibility Matrix](#5-tool-compatibility-matrix)
6. [Integration Surface](#6-integration-surface)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Appendices](#8-appendices)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Current State

| Metric | Value | Confidence |
|--------|-------|------------|
| Tree-sitter utilization | 5-10% | HIGH (code audit) |
| Node types extracted | ~15 per language | HIGH (code audit) |
| Query predicates used | 1 of 10+ | HIGH (code audit) |
| Scope tracking | 0% | FACT |
| Incremental parsing | 0% | FACT |
| Error recovery | 0% | FACT |

### 1.2 Opportunity Size

| Dimension | Current | Potential | Gap |
|-----------|---------|-----------|-----|
| WHAT (Atom classification) | Name heuristics | Full AST patterns | LARGE |
| LAYER (Architecture) | Path + imports | Dependency analysis | MEDIUM |
| ROLE (Purpose) | 29 roles, name-based | Call patterns, returns | LARGE |
| BOUNDARY (Internal/External) | Import classification | Full module resolution | MEDIUM |
| STATE (Stateful/Stateless) | Not detected | Assignment tracking | LARGE |
| EFFECT (Pure/Impure) | Not detected | Side effect analysis | LARGE |
| LIFECYCLE (Init/Active/Dispose) | Not detected | Pattern detection | MEDIUM |
| TRUST (Confidence) | Low baseline | Evidence-based | MEDIUM |

### 1.3 Key Finding

> **Tree-sitter is not a parser. It's a complete code intelligence platform.**
>
> We built a regex engine on top of a compiler frontend.

---

## 2. TREE-SITTER ARCHITECTURE

### 2.1 Component Stack

```
+------------------------------------------------------------------+
|                        TREE-SITTER STACK                          |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+   +-------------------+   +---------------+|
|  |   QUERY ENGINE    |   |   LOCALS SYSTEM   |   |  HIGHLIGHTS   ||
|  |-------------------|   |-------------------|   |---------------||
|  | S-expressions     |   | @local.scope      |   | Semantic      ||
|  | Captures (@name)  |   | @local.definition |   | tokens for    ||
|  | Predicates        |   | @local.reference  |   | every node    ||
|  | Directives        |   | Variable lifetime |   | type          ||
|  +-------------------+   +-------------------+   +---------------+|
|           |                       |                     |         |
|           +-----------------------+---------------------+         |
|                                   |                               |
|  +-------------------+   +--------v--------+   +-----------------+|
|  |    INJECTIONS     |   |     PARSER      |   |   TREE CURSOR   ||
|  |-------------------|   |-----------------|   |-----------------||
|  | Embedded langs    |   | GLR algorithm   |   | Memory-efficient||
|  | SQL in strings    |   | Error recovery  |   | traversal       ||
|  | GraphQL in JS     |   | Incremental     |   | No object alloc ||
|  | HTML in templates |   | Concrete tree   |   | goto_* methods  ||
|  +-------------------+   +-----------------+   +-----------------+|
|                                   |                               |
+-----------------------------------|-------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |    CONCRETE SYNTAX TREE       |
                    |-------------------------------|
                    | Named nodes (grammar symbols) |
                    | Anonymous nodes (literals)    |
                    | ERROR nodes (parse failures)  |
                    | MISSING nodes (recovery)      |
                    | Byte ranges, points, fields   |
                    +-------------------------------+
```

### 2.2 Data Flow

```
Source Code (bytes)
       |
       v
+-------------+
|   Parser    | -----> Tree (CST)
+-------------+            |
       ^                   v
       |          +----------------+
       |          | Query Engine   | -----> Captures (Dict[str, List[Node]])
       |          +----------------+
       |                   |
+-------------+            v
| Tree.edit() |   +----------------+
| (optional)  |   | Locals System  | -----> Scope Graph
+-------------+   +----------------+
                           |
                           v
                  +----------------+
                  |  Injections    | -----> Embedded Language Trees
                  +----------------+
```

### 2.3 Key Data Structures

#### 2.3.1 Node

```python
class Node:
    # Identity
    type: str              # "function_definition", "identifier", etc.
    is_named: bool         # Named (grammar) vs anonymous (literal)
    is_missing: bool       # Inserted by error recovery
    is_extra: bool         # Comments, whitespace

    # Position
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]  # (row, column)
    end_point: tuple[int, int]

    # Content
    text: bytes            # Raw source bytes

    # Structure
    parent: Node | None
    children: list[Node]
    child_count: int
    named_children: list[Node]
    named_child_count: int

    # Fields (named children)
    def child_by_field_name(name: str) -> Node | None
    def children_by_field_name(name: str) -> list[Node]
```

**Confidence:** FACT (from py-tree-sitter 0.25.2 documentation)

#### 2.3.2 Query

```python
class Query:
    # Properties
    pattern_count: int
    capture_count: int
    string_count: int

    # Methods
    def capture_name(index: int) -> str
    def capture_quantifier(pattern_index, capture_index) -> int
    def disable_capture(name: str)           # Irreversible
    def disable_pattern(index: int)          # Irreversible
    def pattern_settings(index: int) -> dict # From #set! directives
    def pattern_assertions(index: int) -> dict  # From #is? predicates
    def start_byte_for_pattern(index: int) -> int
    def end_byte_for_pattern(index: int) -> int
```

**Confidence:** FACT (from py-tree-sitter documentation)

#### 2.3.3 QueryCursor

```python
class QueryCursor:
    # Properties
    match_limit: int
    did_exceed_match_limit: bool

    # Methods
    def captures(node: Node, predicate=None) -> dict[str, list[Node]]
    def matches(node: Node, predicate=None) -> list[tuple[int, dict]]
    def set_byte_range(start: int, end: int)
    def set_point_range(start: tuple, end: tuple)
    def set_containing_byte_range(start: int, end: int)  # v0.26.0+
    def set_containing_point_range(start: tuple, end: tuple)  # v0.26.0+
    def set_max_start_depth(depth: int)
```

**Confidence:** FACT (from py-tree-sitter documentation)

#### 2.3.4 TreeCursor

```python
class TreeCursor:
    # Current position
    node: Node
    field_name: str | None
    field_id: int

    # Navigation (return bool for success)
    def goto_parent() -> bool
    def goto_first_child() -> bool
    def goto_last_child() -> bool
    def goto_next_sibling() -> bool
    def goto_previous_sibling() -> bool
    def goto_first_child_for_byte(byte: int) -> int
    def goto_first_child_for_point(point: tuple) -> int

    # Reset
    def reset(node: Node)
    def reset_to(cursor: TreeCursor)

    # Copy
    def copy() -> TreeCursor
```

**Confidence:** FACT (from py-tree-sitter documentation)

---

## 3. CAPABILITY INVENTORY

### 3.1 Legend

| Symbol | Meaning |
|--------|---------|
| IMPLEMENTED | Capability exists in codebase |
| PARTIAL | Capability partially implemented |
| NOT_IMPLEMENTED | Capability not yet built |
| N/A | Not applicable to our use case |

| Confidence | Meaning |
|------------|---------|
| FACT | Verified in documentation or code |
| HIGH | Strong evidence, minimal assumptions |
| MEDIUM | Some assumptions, reasonable confidence |
| LOW | Significant assumptions, needs validation |

### 3.2 Core Parsing Capabilities

| ID | Capability | Status | Confidence | Location | Notes |
|----|------------|--------|------------|----------|-------|
| CP-01 | Basic parsing (Parser.parse) | IMPLEMENTED | FACT | tree_sitter_engine.py:365-370 | Works |
| CP-02 | Multi-language support | IMPLEMENTED | FACT | tree_sitter_engine.py:344-357 | 9 languages configured |
| CP-03 | Timeout protection | IMPLEMENTED | FACT | tree_sitter_engine.py:50-76 | Threading-based |
| CP-04 | Incremental parsing (Tree.edit) | NOT_IMPLEMENTED | FACT | - | Requires edit tracking |
| CP-05 | Changed range detection | NOT_IMPLEMENTED | FACT | - | old_tree.changed_ranges(new_tree) |
| CP-06 | Error recovery (ERROR nodes) | NOT_IMPLEMENTED | FACT | - | parse() works on broken code |
| CP-07 | MISSING node detection | NOT_IMPLEMENTED | FACT | - | node.is_missing |
| CP-08 | TreeCursor traversal | NOT_IMPLEMENTED | FACT | - | Memory-efficient, no alloc |

### 3.3 Query System Capabilities

| ID | Capability | Status | Confidence | Location | Notes |
|----|------------|--------|------------|----------|-------|
| QS-01 | Basic queries (patterns) | IMPLEMENTED | FACT | tree_sitter_engine.py:382-424 | Inline strings |
| QS-02 | Captures (@name) | IMPLEMENTED | FACT | tree_sitter_engine.py:443-444 | Works |
| QS-03 | Field specifications | IMPLEMENTED | FACT | tree_sitter_engine.py:469-507 | child_by_field_name |
| QS-04 | #match? predicate | IMPLEMENTED | FACT | tree_sitter_engine.py:402,408 | Used for React |
| QS-05 | #eq? predicate | NOT_IMPLEMENTED | FACT | - | Equality checks |
| QS-06 | #not-eq? predicate | NOT_IMPLEMENTED | FACT | - | Negative equality |
| QS-07 | #any-of? predicate | NOT_IMPLEMENTED | FACT | - | Multi-string match |
| QS-08 | #is? predicate | NOT_IMPLEMENTED | FACT | - | Property assertion |
| QS-09 | #is-not? predicate | NOT_IMPLEMENTED | FACT | - | Negative assertion |
| QS-10 | #set! directive | NOT_IMPLEMENTED | FACT | - | Metadata attachment |
| QS-11 | Wildcard (_) | NOT_IMPLEMENTED | FACT | - | Match any node |
| QS-12 | Supertype queries | NOT_IMPLEMENTED | FACT | - | (expression) |
| QS-13 | Negated fields (!field) | NOT_IMPLEMENTED | FACT | - | Exclude patterns |
| QS-14 | Quantifiers (+, *, ?) | NOT_IMPLEMENTED | FACT | - | Repetition |
| QS-15 | Alternation | NOT_IMPLEMENTED | FACT | - | Choice patterns |
| QS-16 | Anonymous nodes ("literal") | PARTIAL | FACT | - | Used in some queries |
| QS-17 | Custom predicates (callable) | NOT_IMPLEMENTED | FACT | - | Python functions |
| QS-18 | QueryCursor.set_byte_range | NOT_IMPLEMENTED | FACT | - | Scoped queries |
| QS-19 | QueryCursor.set_max_start_depth | NOT_IMPLEMENTED | FACT | - | Depth limiting |
| QS-20 | Query.disable_capture | NOT_IMPLEMENTED | FACT | - | Performance tuning |

### 3.4 Scope Tracking Capabilities (locals.scm)

| ID | Capability | Status | Confidence | Location | Notes |
|----|------------|--------|------------|----------|-------|
| ST-01 | @local.scope | NOT_IMPLEMENTED | FACT | - | Scope boundaries |
| ST-02 | @local.definition | NOT_IMPLEMENTED | FACT | - | Variable definitions |
| ST-03 | @local.reference | NOT_IMPLEMENTED | FACT | - | Variable references |
| ST-04 | Definition-reference linking | NOT_IMPLEMENTED | FACT | - | Same-name matching |
| ST-05 | Unused variable detection | NOT_IMPLEMENTED | HIGH | - | Def without ref |
| ST-06 | Unused parameter detection | NOT_IMPLEMENTED | HIGH | - | Param without ref |
| ST-07 | Shadowing detection | NOT_IMPLEMENTED | HIGH | - | Inner redefines outer |
| ST-08 | Data flow tracking | NOT_IMPLEMENTED | MEDIUM | - | Value propagation |

### 3.5 Semantic Highlighting Capabilities (highlights.scm)

| ID | Capability | Status | Confidence | Location | Notes |
|----|------------|--------|------------|----------|-------|
| SH-01 | Token classification | NOT_IMPLEMENTED | FACT | - | @keyword, @function, etc. |
| SH-02 | Context-aware highlighting | NOT_IMPLEMENTED | FACT | - | Function call vs definition |
| SH-03 | Custom highlight groups | NOT_IMPLEMENTED | MEDIUM | - | @atom.repository, etc. |
| SH-04 | Scope-aware highlighting | NOT_IMPLEMENTED | FACT | - | Combined with locals |

### 3.6 Language Injection Capabilities (injections.scm)

| ID | Capability | Status | Confidence | Location | Notes |
|----|------------|--------|------------|----------|-------|
| LI-01 | @injection.content | NOT_IMPLEMENTED | FACT | - | Content to re-parse |
| LI-02 | @injection.language | NOT_IMPLEMENTED | FACT | - | Target language |
| LI-03 | injection.combined | NOT_IMPLEMENTED | FACT | - | Merge multiple |
| LI-04 | SQL in Python strings | NOT_IMPLEMENTED | MEDIUM | - | Detect and parse |
| LI-05 | GraphQL in JS strings | NOT_IMPLEMENTED | MEDIUM | - | Detect and parse |
| LI-06 | HTML in template literals | NOT_IMPLEMENTED | MEDIUM | - | Detect and parse |
| LI-07 | Regex pattern parsing | NOT_IMPLEMENTED | LOW | - | Complex patterns |

### 3.7 Node Type Coverage by Language

#### Python (tree-sitter-python)

| Category | Node Types | Status | Notes |
|----------|-----------|--------|-------|
| **Definitions** | function_definition, class_definition | IMPLEMENTED | Core extraction |
| | async_function_definition | NOT_IMPLEMENTED | Lifecycle detection |
| | decorated_definition | PARTIAL | Decorator names only |
| | lambda | NOT_IMPLEMENTED | Anonymous functions |
| **Control Flow** | if_statement, elif_clause, else_clause | NOT_IMPLEMENTED | Complexity metrics |
| | for_statement, while_statement | NOT_IMPLEMENTED | Loop detection |
| | try_statement, except_clause, finally_clause | NOT_IMPLEMENTED | Exception flow |
| | with_statement | NOT_IMPLEMENTED | Context managers |
| | match_statement, case_clause | NOT_IMPLEMENTED | Python 3.10+ |
| **Expressions** | call | IMPLEMENTED | Edge extraction |
| | assignment, augmented_assignment | NOT_IMPLEMENTED | Data flow |
| | attribute | PARTIAL | Method calls |
| | subscript | NOT_IMPLEMENTED | Index access |
| | comprehension types | NOT_IMPLEMENTED | List/dict/set/gen |
| | await | NOT_IMPLEMENTED | Async detection |
| | yield, yield_from | NOT_IMPLEMENTED | Generator detection |
| **Statements** | return_statement | NOT_IMPLEMENTED | Return analysis |
| | raise_statement | NOT_IMPLEMENTED | Exception sources |
| | assert_statement | NOT_IMPLEMENTED | Validation patterns |
| | import_statement, import_from_statement | IMPLEMENTED | Dependency extraction |
| **Literals** | string, integer, float, true, false, none | NOT_IMPLEMENTED | Constant analysis |
| **Types** | type annotation nodes | NOT_IMPLEMENTED | Type extraction |

**Total Python nodes:** ~100
**Implemented:** ~10
**Coverage:** ~10%

#### JavaScript/TypeScript (tree-sitter-javascript, tree-sitter-typescript)

| Category | Node Types | Status | Notes |
|----------|-----------|--------|-------|
| **Definitions** | function_declaration, function_expression | IMPLEMENTED | Core extraction |
| | arrow_function | IMPLEMENTED | Via variable_declarator |
| | class_declaration, class_expression | IMPLEMENTED | Core extraction |
| | method_definition | PARTIAL | Inside classes |
| | generator_function, generator_function_declaration | NOT_IMPLEMENTED | Generator detection |
| **JSX** | jsx_element, jsx_self_closing_element | NOT_IMPLEMENTED | React components |
| | jsx_attribute, jsx_expression | NOT_IMPLEMENTED | Prop analysis |
| **Control Flow** | if_statement, else_clause | NOT_IMPLEMENTED | Complexity |
| | switch_statement, switch_case | NOT_IMPLEMENTED | Case analysis |
| | for_statement, for_in_statement, for_of_statement | NOT_IMPLEMENTED | Loop types |
| | while_statement, do_statement | NOT_IMPLEMENTED | Loop detection |
| | try_statement, catch_clause, finally_clause | NOT_IMPLEMENTED | Exception flow |
| **Expressions** | call_expression | IMPLEMENTED | Edge extraction |
| | member_expression | IMPLEMENTED | Method calls |
| | new_expression | IMPLEMENTED | Constructor calls |
| | assignment_expression | NOT_IMPLEMENTED | Data flow |
| | await_expression | NOT_IMPLEMENTED | Async detection |
| | ternary_expression | NOT_IMPLEMENTED | Conditional logic |
| | template_literal, template_substitution | NOT_IMPLEMENTED | String interpolation |
| **Modules** | import_statement, export_statement | PARTIAL | Via regex fallback |
| | named_imports, namespace_import | PARTIAL | Import analysis |
| **TypeScript-specific** | type_annotation | NOT_IMPLEMENTED | Type extraction |
| | interface_declaration | PARTIAL | Name only |
| | type_alias_declaration | PARTIAL | Name only |
| | enum_declaration | NOT_IMPLEMENTED | Enum analysis |

**Total JS/TS nodes:** ~150
**Implemented:** ~15
**Coverage:** ~10%

#### Go (tree-sitter-go)

| Category | Node Types | Status | Notes |
|----------|-----------|--------|-------|
| **Definitions** | function_declaration | IMPLEMENTED | Core extraction |
| | method_declaration | IMPLEMENTED | With receiver |
| | type_declaration (struct_type) | IMPLEMENTED | Struct extraction |
| | type_declaration (interface_type) | IMPLEMENTED | Interface extraction |
| **Concurrency** | go_statement | NOT_IMPLEMENTED | Goroutine detection |
| | select_statement | NOT_IMPLEMENTED | Channel select |
| | channel_type, send_statement, receive_expression | NOT_IMPLEMENTED | Channel analysis |
| **Control Flow** | if_statement, else_clause | NOT_IMPLEMENTED | Complexity |
| | for_statement, range_clause | NOT_IMPLEMENTED | Loop types |
| | switch_statement, type_switch_statement | NOT_IMPLEMENTED | Case analysis |
| | defer_statement | NOT_IMPLEMENTED | Lifecycle detection |
| **Expressions** | call_expression | PARTIAL | Via regex |
| | selector_expression | NOT_IMPLEMENTED | Method calls |
| | composite_literal | NOT_IMPLEMENTED | Struct instantiation |
| **Error Handling** | assignment with error | NOT_IMPLEMENTED | Go error pattern |

**Total Go nodes:** ~80
**Implemented:** ~8
**Coverage:** ~10%

#### Rust (tree-sitter-rust)

| Category | Node Types | Status | Notes |
|----------|-----------|--------|-------|
| **Definitions** | function_item | IMPLEMENTED | Core extraction |
| | struct_item | IMPLEMENTED | Struct extraction |
| | enum_item | IMPLEMENTED | Enum extraction |
| | trait_item | IMPLEMENTED | Trait extraction |
| | impl_item | IMPLEMENTED | Implementation blocks |
| **Patterns** | match_expression, match_arm | NOT_IMPLEMENTED | Pattern matching |
| | if_expression, if_let_expression | NOT_IMPLEMENTED | Conditional |
| **Ownership** | reference_expression, borrow_expression | NOT_IMPLEMENTED | Borrow analysis |
| | lifetime | NOT_IMPLEMENTED | Lifetime tracking |
| **Async** | async_block | NOT_IMPLEMENTED | Async detection |
| **Macros** | macro_invocation, macro_definition | NOT_IMPLEMENTED | Macro analysis |
| **Unsafe** | unsafe_block | NOT_IMPLEMENTED | Unsafe detection |

**Total Rust nodes:** ~100
**Implemented:** ~8
**Coverage:** ~8%

---

## 4. THEORY COMPATIBILITY MATRIX

### 4.1 Three Planes Mapping

| Plane | Tree-sitter Component | Compatibility | Confidence |
|-------|----------------------|---------------|------------|
| **Physical** | Byte ranges, raw text | DIRECT | FACT |
| **Virtual** | CST nodes, named/anonymous | DIRECT | FACT |
| **Semantic** | Query captures, highlights | REQUIRES_MAPPING | HIGH |

**Analysis:** Tree-sitter operates at Virtual plane, producing data that maps to all three planes. Physical data (bytes, positions) is directly available. Semantic meaning requires our classification layer.

### 4.2 16-Level Scale Mapping

| Level | Tree-sitter Detection | Status | Confidence |
|-------|----------------------|--------|------------|
| L12-L8 (Cosmological) | N/A | OUT_OF_SCOPE | FACT |
| L7 SYSTEM | Module graph | POSSIBLE | MEDIUM |
| L6 PACKAGE | package/module nodes | POSSIBLE | HIGH |
| L5 FILE | Root node per file | IMPLEMENTED | FACT |
| L4 CONTAINER | class_definition, struct_item | IMPLEMENTED | FACT |
| L3 NODE | function_definition, method | IMPLEMENTED | FACT |
| L2 BLOCK | block, compound_statement | NOT_IMPLEMENTED | FACT |
| L1 STATEMENT | expression_statement, etc. | NOT_IMPLEMENTED | FACT |
| L0 TOKEN | identifier, operator | NOT_IMPLEMENTED | FACT |
| L-1 to L-3 (Physical) | byte positions | AVAILABLE | FACT |

**Gap:** We stop at L3 (NODE). Tree-sitter provides L2, L1, L0 data that we don't extract.

### 4.3 Eight Dimensions Mapping

| Dimension | Tree-sitter Data Source | Extraction Method | Status | Confidence |
|-----------|------------------------|-------------------|--------|------------|
| **D1: WHAT** | Node type + patterns | Query + classification | PARTIAL | HIGH |
| **D2: LAYER** | Import paths + file paths | Pattern matching | PARTIAL | HIGH |
| **D3: ROLE** | Call patterns, returns | Query analysis | MINIMAL | MEDIUM |
| **D4: BOUNDARY** | Import targets | Module resolution | PARTIAL | HIGH |
| **D5: STATE** | Assignment patterns | Locals tracking | NOT_IMPLEMENTED | HIGH |
| **D6: EFFECT** | I/O calls, mutations | Call + assignment | NOT_IMPLEMENTED | MEDIUM |
| **D7: LIFECYCLE** | Constructor patterns | Query patterns | NOT_IMPLEMENTED | HIGH |
| **D8: TRUST** | Multiple evidence sources | Aggregation | MINIMAL | MEDIUM |

### 4.4 Atom Detection Enhancement

| Atom Category | Current Detection | Tree-sitter Enhancement | Confidence |
|---------------|------------------|------------------------|------------|
| **Entity** | Name pattern | Field definitions + methods | HIGH |
| **Repository** | Name pattern | CRUD method signatures | HIGH |
| **Service** | Name pattern | Dependency injection patterns | MEDIUM |
| **Controller** | Decorator/path | Route patterns + HTTP methods | HIGH |
| **Factory** | Name pattern | Return `new X` or `X()` | HIGH |
| **Builder** | Name pattern | Return `self`/`this` pattern | HIGH |
| **Validator** | Name pattern | Return bool + raises | MEDIUM |
| **Transformer** | Name pattern | Input/output type difference | LOW |
| **Handler** | Name pattern | Event parameter pattern | MEDIUM |

### 4.5 RPBL Extraction

| RPBL | Tree-sitter Evidence | Query Pattern | Confidence |
|------|---------------------|---------------|------------|
| **Responsibility** | Method count, call fan-out | Count children, count calls | HIGH |
| **Purity** | No external assignment | Track assignment targets | MEDIUM |
| **Boundary** | External module calls | Import + call correlation | HIGH |
| **Lifecycle** | Constructor/dispose patterns | Named method patterns | HIGH |

---

## 5. TOOL COMPATIBILITY MATRIX

### 5.1 Collider Pipeline Stages

| Stage | Current Implementation | Tree-sitter Enhancement | Integration Point |
|-------|----------------------|------------------------|-------------------|
| **1. File Discovery** | os.walk + patterns | N/A | N/A |
| **2. Parsing** | Tree-sitter (partial) | FULL TREE ACCESS | tree_sitter_engine.py |
| **3. Particle Extraction** | Basic node types | ALL NODE TYPES | tree_sitter_engine.py |
| **4. Import Resolution** | Regex + AST | QUERY-BASED | edge_extractor.py |
| **5. Classification** | Name heuristics | AST PATTERNS | universal_classifier.py |
| **6. Edge Extraction** | Regex + basic TS | FULL SCOPE GRAPH | edge_extractor.py |
| **7. Topology Reasoning** | Graph analysis | ENHANCED METRICS | topology_reasoning.py |
| **8. Health Scoring** | Heuristics | ERROR NODE COUNT | health_calculator.py |
| **9. Visualization** | JSON export | SEMANTIC TOKENS | visualize_graph_webgl.py |

### 5.2 Current Files Using Tree-sitter

| File | Lines | Tree-sitter Usage | Enhancement Potential |
|------|-------|------------------|----------------------|
| tree_sitter_engine.py | 848 | Core parsing, basic queries | HIGH |
| edge_extractor.py | 1722 | Call extraction | HIGH |
| universal_detector.py | ~50 | Orchestration | LOW |

### 5.3 New Files Needed

| File | Purpose | Priority |
|------|---------|----------|
| queries/python/*.scm | Python query files | HIGH |
| queries/javascript/*.scm | JavaScript query files | HIGH |
| queries/typescript/*.scm | TypeScript query files | HIGH |
| queries/go/*.scm | Go query files | MEDIUM |
| queries/rust/*.scm | Rust query files | MEDIUM |
| src/core/scope_analyzer.py | Locals-based scope tracking | HIGH |
| src/core/control_flow.py | Control flow graph | MEDIUM |
| src/core/data_flow.py | Data flow analysis | MEDIUM |
| src/core/semantic_tokens.py | Token classification | LOW |

### 5.4 Schema Compatibility

#### Current Node Schema

```json
{
  "id": "user.py:UserRepository",
  "name": "UserRepository",
  "kind": "class",
  "file_path": "user.py",
  "start_line": 10,
  "end_line": 50,
  "body_source": "...",
  "role": "Repository",
  "layer": "Infrastructure",
  "dimensions": {
    "D1_WHAT": "TIER1.STDLIB.002",
    "D2_LAYER": "Infrastructure"
  }
}
```

#### Enhanced Node Schema (Proposed)

```json
{
  "id": "user.py:UserRepository",
  "name": "UserRepository",
  "kind": "class",
  "file_path": "user.py",
  "start_line": 10,
  "end_line": 50,
  "start_byte": 245,
  "end_byte": 1890,
  "body_source": "...",
  "role": "Repository",
  "layer": "Infrastructure",
  "dimensions": {
    "D1_WHAT": "TIER1.STDLIB.002",
    "D2_LAYER": "Infrastructure",
    "D5_STATE": "Stateless",
    "D6_EFFECT": "Impure",
    "D7_LIFECYCLE": "Singleton"
  },
  "rpbl": {
    "responsibility": 3,
    "purity": 7,
    "boundary": 5,
    "lifecycle": 8
  },
  "metrics": {
    "cyclomatic_complexity": 12,
    "nesting_depth": 3,
    "method_count": 8,
    "call_fan_out": 15,
    "call_fan_in": 7
  },
  "scope": {
    "definitions": ["user", "data", "result"],
    "references": ["self.db", "User", "validate"],
    "unused": ["temp"]
  },
  "errors": [],
  "confidence": 0.92
}
```

**New Fields Explanation:**

| Field | Source | Purpose |
|-------|--------|---------|
| start_byte, end_byte | Node | Incremental parsing, injections |
| D5_STATE | Scope analysis | State tracking |
| D6_EFFECT | Call + assignment analysis | Purity detection |
| D7_LIFECYCLE | Pattern detection | Lifecycle phase |
| rpbl | Multiple analyses | RPBL scoring |
| metrics | Control flow | Complexity metrics |
| scope | Locals analysis | Variable tracking |
| errors | ERROR nodes | Syntax issues |

---

## 6. INTEGRATION SURFACE

### 6.1 Directory Structure (Proposed)

```
standard-model-of-code/
├── src/
│   ├── core/
│   │   ├── tree_sitter_engine.py      # EXISTING - Refactor
│   │   ├── edge_extractor.py          # EXISTING - Refactor
│   │   ├── scope_analyzer.py          # NEW - Locals-based
│   │   ├── control_flow.py            # NEW - CFG
│   │   ├── data_flow.py               # NEW - DFG
│   │   └── semantic_tokens.py         # NEW - Highlights
│   └── queries/
│       ├── __init__.py                # Query loader
│       ├── python/
│       │   ├── definitions.scm        # Function/class extraction
│       │   ├── locals.scm             # Scope tracking
│       │   ├── highlights.scm         # Token classification
│       │   ├── injections.scm         # Embedded SQL, etc.
│       │   └── patterns.scm           # Atom detection patterns
│       ├── javascript/
│       │   ├── definitions.scm
│       │   ├── locals.scm
│       │   ├── highlights.scm
│       │   ├── injections.scm
│       │   └── patterns.scm
│       ├── typescript/
│       │   └── ... (same structure)
│       ├── go/
│       │   └── ... (same structure)
│       └── rust/
│           └── ... (same structure)
```

### 6.2 API Design (Proposed)

#### 6.2.1 Query Loader

```python
# src/queries/__init__.py

from pathlib import Path
from typing import Dict, Optional
import tree_sitter

class QueryLoader:
    """Load and cache .scm query files."""

    QUERY_DIR = Path(__file__).parent

    QUERY_TYPES = ['definitions', 'locals', 'highlights', 'injections', 'patterns']

    def __init__(self):
        self._cache: Dict[tuple, tree_sitter.Query] = {}

    def load_query(
        self,
        language: str,
        query_type: str,
        ts_language: tree_sitter.Language
    ) -> Optional[tree_sitter.Query]:
        """
        Load a query file for a language.

        Args:
            language: 'python', 'javascript', etc.
            query_type: 'definitions', 'locals', 'highlights', etc.
            ts_language: Tree-sitter Language object

        Returns:
            Compiled Query object, or None if file doesn't exist
        """
        cache_key = (language, query_type)
        if cache_key in self._cache:
            return self._cache[cache_key]

        query_file = self.QUERY_DIR / language / f"{query_type}.scm"
        if not query_file.exists():
            return None

        query_text = query_file.read_text()
        query = tree_sitter.Query(ts_language, query_text)
        self._cache[cache_key] = query
        return query

    def load_all_queries(
        self,
        language: str,
        ts_language: tree_sitter.Language
    ) -> Dict[str, tree_sitter.Query]:
        """Load all query types for a language."""
        queries = {}
        for query_type in self.QUERY_TYPES:
            query = self.load_query(language, query_type, ts_language)
            if query:
                queries[query_type] = query
        return queries


# Singleton instance
_query_loader: Optional[QueryLoader] = None

def get_query_loader() -> QueryLoader:
    global _query_loader
    if _query_loader is None:
        _query_loader = QueryLoader()
    return _query_loader
```

#### 6.2.2 Scope Analyzer

```python
# src/core/scope_analyzer.py

from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import tree_sitter

@dataclass
class ScopeInfo:
    """Information about a scope (function, class, block)."""
    node: tree_sitter.Node
    definitions: Dict[str, List[tree_sitter.Node]]  # name -> def nodes
    references: Dict[str, List[tree_sitter.Node]]   # name -> ref nodes
    parent: Optional['ScopeInfo'] = None
    children: List['ScopeInfo'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class ScopeAnalysisResult:
    """Result of scope analysis for a file."""
    scopes: List[ScopeInfo]
    unused_definitions: List[tuple]  # (name, node)
    undefined_references: List[tuple]  # (name, node)
    shadowed_definitions: List[tuple]  # (name, outer_node, inner_node)

class ScopeAnalyzer:
    """
    Analyze variable scopes using locals.scm queries.

    Detects:
    - Variable definitions and references
    - Unused variables
    - Undefined references (within scope)
    - Shadowing
    """

    def __init__(self, query_loader):
        self.query_loader = query_loader

    def analyze(
        self,
        tree: tree_sitter.Tree,
        language: str,
        ts_language: tree_sitter.Language
    ) -> ScopeAnalysisResult:
        """
        Analyze scopes in a parsed tree.

        Args:
            tree: Parsed Tree-sitter tree
            language: Language name
            ts_language: Tree-sitter Language object

        Returns:
            ScopeAnalysisResult with all scope information
        """
        locals_query = self.query_loader.load_query(language, 'locals', ts_language)
        if not locals_query:
            return ScopeAnalysisResult([], [], [], [])

        cursor = tree_sitter.QueryCursor(locals_query)
        captures = cursor.captures(tree.root_node)

        # Build scope tree
        scopes = self._build_scope_tree(captures)

        # Analyze for issues
        unused = self._find_unused(scopes)
        undefined = self._find_undefined(scopes)
        shadowed = self._find_shadowed(scopes)

        return ScopeAnalysisResult(scopes, unused, undefined, shadowed)

    def _build_scope_tree(self, captures: Dict) -> List[ScopeInfo]:
        # Implementation details...
        pass

    def _find_unused(self, scopes: List[ScopeInfo]) -> List[tuple]:
        # Find definitions without references
        pass

    def _find_undefined(self, scopes: List[ScopeInfo]) -> List[tuple]:
        # Find references without definitions (in scope)
        pass

    def _find_shadowed(self, scopes: List[ScopeInfo]) -> List[tuple]:
        # Find inner definitions that shadow outer
        pass
```

#### 6.2.3 Control Flow Analyzer

```python
# src/core/control_flow.py

from typing import Dict, List, Set
from dataclasses import dataclass
import tree_sitter

@dataclass
class ControlFlowMetrics:
    """Metrics derived from control flow analysis."""
    cyclomatic_complexity: int      # Decision points + 1
    nesting_depth: int              # Maximum nesting
    branch_count: int               # if/else/switch branches
    loop_count: int                 # for/while loops
    exception_handlers: int         # try/except blocks
    early_returns: int              # return statements before end
    has_recursion: bool             # Self-calls detected

class ControlFlowAnalyzer:
    """
    Analyze control flow structures using Tree-sitter.

    Calculates complexity metrics from control flow nodes.
    """

    # Node types that add to cyclomatic complexity
    DECISION_NODES = {
        'python': {'if_statement', 'elif_clause', 'for_statement',
                   'while_statement', 'except_clause', 'with_statement',
                   'match_statement', 'case_clause', 'and', 'or'},
        'javascript': {'if_statement', 'switch_case', 'for_statement',
                       'for_in_statement', 'for_of_statement', 'while_statement',
                       'do_statement', 'catch_clause', 'ternary_expression',
                       'binary_expression'},  # && and ||
        # ... other languages
    }

    def analyze_function(
        self,
        function_node: tree_sitter.Node,
        language: str
    ) -> ControlFlowMetrics:
        """
        Analyze control flow for a single function.

        Args:
            function_node: The function/method node
            language: Language name

        Returns:
            ControlFlowMetrics for the function
        """
        decision_types = self.DECISION_NODES.get(language, set())

        complexity = 1  # Base complexity
        max_depth = 0
        current_depth = 0
        branches = 0
        loops = 0
        handlers = 0
        returns = 0

        # ... traverse and count

        return ControlFlowMetrics(
            cyclomatic_complexity=complexity,
            nesting_depth=max_depth,
            branch_count=branches,
            loop_count=loops,
            exception_handlers=handlers,
            early_returns=returns,
            has_recursion=False  # Detected separately
        )
```

### 6.3 Query File Examples

#### 6.3.1 Python Definitions (definitions.scm)

```scheme
; queries/python/definitions.scm
; Extract all significant definitions from Python code

; Functions (sync and async)
(function_definition
  name: (identifier) @function.name
  parameters: (parameters) @function.params
  return_type: (type)? @function.return_type
  body: (block) @function.body) @function

(async_function_definition
  name: (identifier) @async_function.name
  parameters: (parameters) @async_function.params
  return_type: (type)? @async_function.return_type
  body: (block) @async_function.body) @async_function

; Classes
(class_definition
  name: (identifier) @class.name
  superclasses: (argument_list)? @class.bases
  body: (block) @class.body) @class

; Methods (functions inside classes)
(class_definition
  body: (block
    (function_definition
      name: (identifier) @method.name
      parameters: (parameters) @method.params) @method))

; Decorated definitions
(decorated_definition
  (decorator
    (identifier) @decorator.name)
  definition: (_) @decorated.definition) @decorated

(decorated_definition
  (decorator
    (call
      function: (attribute
        object: (identifier) @decorator.module
        attribute: (identifier) @decorator.attr)))
  definition: (_) @decorated.definition) @decorated_call

; Module-level assignments (potential constants/configs)
(module
  (expression_statement
    (assignment
      left: (identifier) @module_var.name
      right: (_) @module_var.value))) @module_var
```

#### 6.3.2 Python Locals (locals.scm)

```scheme
; queries/python/locals.scm
; Track variable scopes, definitions, and references

; Scope boundaries
(function_definition) @local.scope
(async_function_definition) @local.scope
(class_definition) @local.scope
(for_statement) @local.scope
(while_statement) @local.scope
(with_statement) @local.scope
(try_statement) @local.scope
(match_statement) @local.scope
(lambda) @local.scope
(list_comprehension) @local.scope
(dictionary_comprehension) @local.scope
(set_comprehension) @local.scope
(generator_expression) @local.scope

; Definitions - function parameters
(function_definition
  parameters: (parameters
    (identifier) @local.definition))

(function_definition
  parameters: (parameters
    (default_parameter
      name: (identifier) @local.definition)))

(function_definition
  parameters: (parameters
    (typed_parameter
      (identifier) @local.definition)))

; Definitions - assignments
(assignment
  left: (identifier) @local.definition)

(assignment
  left: (pattern_list
    (identifier) @local.definition))

(assignment
  left: (tuple_pattern
    (identifier) @local.definition))

; Definitions - for loop variables
(for_statement
  left: (identifier) @local.definition)

(for_statement
  left: (pattern_list
    (identifier) @local.definition))

; Definitions - except clause
(except_clause
  (as_pattern
    (identifier) @local.definition))

; Definitions - with statement
(with_statement
  (with_clause
    (with_item
      value: (as_pattern
        (identifier) @local.definition))))

; Definitions - import aliases
(import_statement
  name: (aliased_import
    alias: (identifier) @local.definition))

(import_from_statement
  name: (aliased_import
    alias: (identifier) @local.definition))

; References
(identifier) @local.reference
```

#### 6.3.3 Python Patterns (patterns.scm)

```scheme
; queries/python/patterns.scm
; Detect architectural patterns for atom classification

; === REPOSITORY PATTERN ===
; Class with CRUD-like methods
(class_definition
  name: (identifier) @class.name
  body: (block
    (function_definition
      name: (identifier) @method.name
      (#any-of? @method.name
        "find" "find_by_id" "find_all" "find_one"
        "get" "get_by_id" "get_all" "get_one"
        "save" "create" "insert" "add"
        "update" "modify" "patch"
        "delete" "remove" "destroy"
        "exists" "count" "list")))) @repository.candidate

; === FACTORY PATTERN ===
; Function/method that returns new instance
(function_definition
  name: (identifier) @factory.name
  (#match? @factory.name "^(create|make|build|new_|get_)")
  body: (block
    (return_statement
      (call
        function: (identifier) @factory.product)))) @factory.candidate

; Class method returning same class
(class_definition
  name: (identifier) @class.name
  body: (block
    (decorated_definition
      (decorator
        (identifier) @dec
        (#any-of? @dec "classmethod" "staticmethod"))
      definition: (function_definition
        body: (block
          (return_statement
            (call
              function: (identifier) @return.type))))))) @factory.classmethod

; === BUILDER PATTERN ===
; Methods that return self/cls
(class_definition
  body: (block
    (function_definition
      name: (identifier) @method.name
      (#not-match? @method.name "^__")
      body: (block
        (return_statement
          (identifier) @return.value
          (#eq? @return.value "self")))))) @builder.method

; === VALIDATOR PATTERN ===
; Function with bool return or raises
(function_definition
  name: (identifier) @validator.name
  (#match? @validator.name "^(validate|is_|has_|can_|check_|verify_|ensure_)")
  return_type: (type
    (identifier) @return.type
    (#eq? @return.type "bool"))?) @validator.candidate

; Function that raises ValidationError
(function_definition
  name: (identifier) @validator.name
  body: (block
    (raise_statement
      (call
        function: (identifier) @error.type
        (#any-of? @error.type "ValidationError" "ValueError" "AssertionError"))))) @validator.raises

; === HANDLER PATTERN ===
; Functions matching on_* or handle_*
(function_definition
  name: (identifier) @handler.name
  (#match? @handler.name "^(on_|handle_|process_)")) @handler.candidate

; Decorated handlers (event systems)
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @dec.method
        (#any-of? @dec.method "on" "handler" "subscribe" "listen"))))
  definition: (function_definition
    name: (identifier) @handler.name)) @handler.decorated

; === SERVICE PATTERN ===
; Class with injected dependencies in __init__
(class_definition
  name: (identifier) @service.name
  (#match? @service.name "(Service|Manager|Provider)$")
  body: (block
    (function_definition
      name: (identifier) @init
      (#eq? @init "__init__")
      parameters: (parameters
        (identifier) @param
        (#not-eq? @param "self"))))) @service.candidate

; === CONTROLLER PATTERN ===
; Flask/FastAPI route decorators
(decorated_definition
  (decorator
    (call
      function: (attribute
        attribute: (identifier) @route.method
        (#any-of? @route.method "route" "get" "post" "put" "delete" "patch"))))
  definition: (function_definition
    name: (identifier) @controller.name)) @controller.flask

; Django view classes
(class_definition
  name: (identifier) @view.name
  superclasses: (argument_list
    (identifier) @base
    (#any-of? @base "View" "APIView" "ViewSet" "ModelViewSet"))) @controller.django

; === SINGLETON PATTERN ===
; Class with _instance pattern
(class_definition
  name: (identifier) @singleton.name
  body: (block
    (expression_statement
      (assignment
        left: (identifier) @attr
        (#eq? @attr "_instance"))))) @singleton.candidate

; === ASYNC PATTERNS ===
; Async context managers
(async_function_definition
  name: (identifier) @async.name
  (#any-of? @async.name "__aenter__" "__aexit__")) @async.context_manager

; Async generators
(async_function_definition
  body: (block
    (expression_statement
      (yield)))) @async.generator
```

---

## 7. IMPLEMENTATION ROADMAP

### 7.1 Phase Overview

```
PHASE 1: Foundation (Weeks 1-2)
├── Extract queries to .scm files
├── Implement QueryLoader
├── Add ERROR node detection
└── Milestone: Query-driven extraction working

PHASE 2: Scope Analysis (Weeks 3-4)
├── Implement locals.scm for Python
├── Build ScopeAnalyzer
├── Detect unused variables
└── Milestone: Scope data in output

PHASE 3: Control Flow (Weeks 5-6)
├── Extract control flow nodes
├── Calculate cyclomatic complexity
├── Detect nesting depth
└── Milestone: Complexity metrics working

PHASE 4: Pattern Detection (Weeks 7-8)
├── Implement patterns.scm
├── Enhance atom classification
├── Add RPBL extraction
└── Milestone: Pattern-based classification

PHASE 5: Advanced Features (Weeks 9-12)
├── Incremental parsing
├── Language injections
├── Data flow analysis
└── Milestone: Full Tree-sitter utilization
```

### 7.2 Detailed Task Registry

#### Phase 1: Foundation

| ID | Task | Priority | Effort | Dependencies | Confidence |
|----|------|----------|--------|--------------|------------|
| P1-01 | Create queries/ directory structure | HIGH | 1h | None | FACT |
| P1-02 | Implement QueryLoader class | HIGH | 4h | P1-01 | HIGH |
| P1-03 | Extract Python queries to definitions.scm | HIGH | 2h | P1-02 | HIGH |
| P1-04 | Extract JS/TS queries to definitions.scm | HIGH | 2h | P1-02 | HIGH |
| P1-05 | Extract Go queries to definitions.scm | MEDIUM | 2h | P1-02 | HIGH |
| P1-06 | Extract Rust queries to definitions.scm | MEDIUM | 2h | P1-02 | HIGH |
| P1-07 | Refactor tree_sitter_engine.py to use QueryLoader | HIGH | 4h | P1-02 | HIGH |
| P1-08 | Add ERROR node detection | HIGH | 2h | P1-07 | FACT |
| P1-09 | Add error count to node schema | MEDIUM | 1h | P1-08 | HIGH |
| P1-10 | Add tests for query loading | HIGH | 2h | P1-07 | HIGH |
| P1-11 | Document query file format | MEDIUM | 1h | P1-03 | HIGH |

**Phase 1 Total:** ~23 hours

#### Phase 2: Scope Analysis

| ID | Task | Priority | Effort | Dependencies | Confidence |
|----|------|----------|--------|--------------|------------|
| P2-01 | Write Python locals.scm | HIGH | 4h | P1-03 | HIGH |
| P2-02 | Write JS/TS locals.scm | HIGH | 4h | P1-04 | HIGH |
| P2-03 | Implement ScopeAnalyzer class | HIGH | 8h | P2-01 | MEDIUM |
| P2-04 | Build scope tree from captures | HIGH | 4h | P2-03 | MEDIUM |
| P2-05 | Implement unused variable detection | HIGH | 4h | P2-04 | HIGH |
| P2-06 | Implement shadowing detection | MEDIUM | 2h | P2-04 | HIGH |
| P2-07 | Add scope data to node schema | HIGH | 2h | P2-03 | HIGH |
| P2-08 | Integrate with edge_extractor.py | HIGH | 4h | P2-03 | MEDIUM |
| P2-09 | Add D5_STATE dimension extraction | HIGH | 4h | P2-03 | MEDIUM |
| P2-10 | Add tests for scope analysis | HIGH | 4h | P2-03 | HIGH |

**Phase 2 Total:** ~44 hours

#### Phase 3: Control Flow

| ID | Task | Priority | Effort | Dependencies | Confidence |
|----|------|----------|--------|--------------|------------|
| P3-01 | Implement ControlFlowAnalyzer | HIGH | 8h | P1-07 | HIGH |
| P3-02 | Calculate cyclomatic complexity | HIGH | 4h | P3-01 | FACT |
| P3-03 | Calculate nesting depth | HIGH | 2h | P3-01 | FACT |
| P3-04 | Detect early returns | MEDIUM | 2h | P3-01 | HIGH |
| P3-05 | Detect recursion | MEDIUM | 4h | P3-01, P2-03 | MEDIUM |
| P3-06 | Add metrics to node schema | HIGH | 2h | P3-01 | HIGH |
| P3-07 | Update health scoring with complexity | MEDIUM | 4h | P3-06 | MEDIUM |
| P3-08 | Add tests for control flow | HIGH | 4h | P3-01 | HIGH |

**Phase 3 Total:** ~30 hours

#### Phase 4: Pattern Detection

| ID | Task | Priority | Effort | Dependencies | Confidence |
|----|------|----------|--------|--------------|------------|
| P4-01 | Write Python patterns.scm | HIGH | 8h | P1-03 | MEDIUM |
| P4-02 | Write JS/TS patterns.scm | HIGH | 8h | P1-04 | MEDIUM |
| P4-03 | Integrate patterns with UniversalClassifier | HIGH | 8h | P4-01, P4-02 | MEDIUM |
| P4-04 | Implement RPBL extraction | HIGH | 8h | P2-03, P3-01 | MEDIUM |
| P4-05 | Add D6_EFFECT dimension (purity) | HIGH | 4h | P2-03 | MEDIUM |
| P4-06 | Add D7_LIFECYCLE dimension | MEDIUM | 4h | P4-01 | HIGH |
| P4-07 | Update atom confidence scoring | HIGH | 4h | P4-03 | MEDIUM |
| P4-08 | Add tests for pattern detection | HIGH | 4h | P4-03 | HIGH |

**Phase 4 Total:** ~48 hours

#### Phase 5: Advanced Features

| ID | Task | Priority | Effort | Dependencies | Confidence |
|----|------|----------|--------|--------------|------------|
| P5-01 | Implement incremental parsing | MEDIUM | 16h | P1-07 | MEDIUM |
| P5-02 | Add file watcher integration | LOW | 8h | P5-01 | MEDIUM |
| P5-03 | Write Python injections.scm (SQL) | LOW | 4h | P1-03 | LOW |
| P5-04 | Write JS injections.scm (GraphQL) | LOW | 4h | P1-04 | LOW |
| P5-05 | Implement injection parsing | LOW | 8h | P5-03, P5-04 | LOW |
| P5-06 | Implement data flow graph | MEDIUM | 16h | P2-03 | LOW |
| P5-07 | Add cross-function data tracking | LOW | 8h | P5-06 | LOW |
| P5-08 | Write highlights.scm files | LOW | 8h | P1-03 | HIGH |
| P5-09 | Integrate highlights with visualizer | LOW | 8h | P5-08 | MEDIUM |

**Phase 5 Total:** ~80 hours

### 7.3 Visualization Integration

| Feature | Data Source | Viz Representation | Priority |
|---------|-------------|-------------------|----------|
| **Error nodes** | ERROR count | Red badge on node | HIGH |
| **Complexity** | cyclomatic_complexity | Node size/color intensity | HIGH |
| **Scope issues** | unused, shadowed | Warning icons | MEDIUM |
| **Purity** | D6_EFFECT | Color coding (green=pure) | MEDIUM |
| **Lifecycle** | D7_LIFECYCLE | Node shape variant | LOW |
| **Semantic tokens** | highlights.scm | Syntax coloring in detail view | LOW |

### 7.4 Success Metrics

| Metric | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|--------|---------|---------|---------|---------|---------|---------|
| Node types used | ~15 | ~20 | ~35 | ~50 | ~70 | ~100 |
| Query predicates | 1 | 3 | 5 | 5 | 8 | 10 |
| Dimensions populated | 2-3 | 3 | 5 | 6 | 7 | 8 |
| RPBL accuracy | N/A | N/A | N/A | N/A | ~70% | ~85% |
| Atom confidence avg | ~60% | ~65% | ~70% | ~75% | ~85% | ~90% |

---

## 8. APPENDICES

### 8.1 Tree-sitter Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| tree-sitter (core) | 0.20.0+ | Required for Query API |
| py-tree-sitter | 0.25.2 | Current recommended |
| tree-sitter-python | 0.20.0+ | Stable |
| tree-sitter-javascript | 0.20.0+ | Stable |
| tree-sitter-typescript | 0.20.0+ | Includes TSX |
| tree-sitter-go | 0.20.0+ | Stable |
| tree-sitter-rust | 0.20.0+ | Stable |

### 8.2 Reference Implementations

| Project | Tree-sitter Usage | Relevance |
|---------|------------------|-----------|
| [Neovim Treesitter](https://github.com/nvim-treesitter/nvim-treesitter) | Full query system | Query file structure |
| [GitHub Semantic](https://github.com/github/semantic) | Code analysis | Pattern detection |
| [Zed Editor](https://github.com/zed-industries/zed) | All features | Performance patterns |
| [tree-sitter-highlight](https://github.com/AstroNvim/tree-sitter-highlight) | Highlights | Token classification |

### 8.3 Node Type Reference

Full node type lists are available from the grammar files:

- Python: [tree-sitter-python/grammar.js](https://github.com/tree-sitter/tree-sitter-python/blob/master/grammar.js)
- JavaScript: [tree-sitter-javascript/grammar.js](https://github.com/tree-sitter/tree-sitter-javascript/blob/master/grammar.js)
- TypeScript: [tree-sitter-typescript/grammar.js](https://github.com/tree-sitter/tree-sitter-typescript/blob/master/grammar.js)
- Go: [tree-sitter-go/grammar.js](https://github.com/tree-sitter/tree-sitter-go/blob/master/grammar.js)
- Rust: [tree-sitter-rust/grammar.js](https://github.com/tree-sitter/tree-sitter-rust/blob/master/grammar.js)

### 8.4 Glossary

| Term | Definition |
|------|------------|
| **CST** | Concrete Syntax Tree - full parse tree including all tokens |
| **AST** | Abstract Syntax Tree - simplified tree (TS produces CST) |
| **Capture** | Named node from a query match (@name) |
| **Predicate** | Query condition (#match?, #eq?, etc.) |
| **Directive** | Query metadata setting (#set!) |
| **Locals** | Scope tracking system for variables |
| **Injection** | Embedded language parsing |
| **GLR** | Generalized LR parsing algorithm |

### 8.5 Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-21 | 1.0 | Initial comprehensive specification |

---

## DOCUMENT STATUS

- [x] Executive Summary
- [x] Tree-sitter Architecture
- [x] Capability Inventory
- [x] Theory Compatibility Matrix
- [x] Tool Compatibility Matrix
- [x] Integration Surface
- [x] Implementation Roadmap
- [x] Appendices

**Next Actions:**
1. Review with stakeholder
2. Prioritize Phase 1 tasks
3. Begin P1-01: Create queries/ directory structure

---

*This document serves as the authoritative reference for Tree-sitter integration in Collider.*
