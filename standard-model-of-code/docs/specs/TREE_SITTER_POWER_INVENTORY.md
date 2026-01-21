# TREE-SITTER POWER INVENTORY

> Living checklist of Tree-sitter capabilities - what we have vs. what we can unlock.
>
> **Status:** Active Tracking
> **Last Updated:** 2026-01-21

---

## QUICK STATUS

```
IMPLEMENTED     ████░░░░░░░░░░░░░░░░  12/100 capabilities (12%)
PARTIAL         ██░░░░░░░░░░░░░░░░░░   8/100 capabilities (8%)
NOT_IMPLEMENTED ████████████████████  80/100 capabilities (80%)

Overall Tree-sitter Utilization: ~15%
```

---

## LEGEND

| Symbol | Status | Meaning |
|--------|--------|---------|
| [x] | IMPLEMENTED | Working in production |
| [~] | PARTIAL | Partially implemented |
| [ ] | NOT_IMPLEMENTED | Available but not built |
| [-] | N/A | Not applicable to our use case |

---

## CORE POWERS

### Parsing Engine

| Status | Power | Unlocks | Notes |
|--------|-------|---------|-------|
| [x] | Basic Parsing | Parse source code to CST | `Parser.parse()` |
| [x] | Multi-language | Support 9+ languages | Via tree-sitter-* packages |
| [x] | Timeout Protection | Prevent hang on large files | Threading-based |
| [ ] | Incremental Parsing | Fast re-parse on edits | `Tree.edit()` |
| [ ] | Change Detection | Know what changed | `old_tree.changed_ranges(new_tree)` |
| [ ] | Error Recovery | Parse broken code | ERROR nodes |
| [ ] | Missing Detection | Find syntax gaps | MISSING nodes |
| [ ] | TreeCursor | Memory-efficient traversal | No object allocation |

### Query System

| Status | Power | Unlocks | Notes |
|--------|-------|---------|-------|
| [x] | Basic Queries | Pattern matching | Inline S-expressions |
| [x] | Captures | Extract matched nodes | `@name` syntax |
| [x] | Field Access | Named children | `child_by_field_name()` |
| [~] | #match? Predicate | Regex filtering | Used for React |
| [ ] | #eq? Predicate | Exact matching | String equality |
| [ ] | #not-eq? Predicate | Negative matching | Exclude patterns |
| [ ] | #any-of? Predicate | Multi-option matching | List of strings |
| [ ] | #is? Predicate | Property assertion | Scope checking |
| [ ] | #is-not? Predicate | Negative assertion | Non-local check |
| [ ] | #set! Directive | Metadata attachment | Custom properties |
| [ ] | Wildcard (_) | Match any node | Generic patterns |
| [ ] | Supertypes | Abstract node matching | (expression) |
| [ ] | Negated Fields | Exclude by field | `!type_parameters` |
| [ ] | Quantifiers | Repetition | `+`, `*`, `?` |
| [ ] | Alternation | Choice patterns | Multiple options |
| [ ] | Custom Predicates | Python callbacks | Programmable filters |
| [ ] | Byte Range Queries | Scoped extraction | `set_byte_range()` |
| [ ] | Depth Limiting | Performance tuning | `set_max_start_depth()` |
| [ ] | External .scm Files | Maintainable queries | queries/*.scm |

### Scope Tracking (locals.scm)

| Status | Power | Unlocks | Notes |
|--------|-------|---------|-------|
| [ ] | @local.scope | Scope boundaries | Function, class, block |
| [ ] | @local.definition | Variable definitions | Parameters, assignments |
| [ ] | @local.reference | Variable uses | Identifier references |
| [ ] | Def-Ref Linking | Connect uses to defs | Same-name matching |
| [ ] | Unused Detection | Dead code | Def without ref |
| [ ] | Shadowing Detection | Naming issues | Inner redefines outer |
| [ ] | Data Flow | Value propagation | Track through scopes |

### Semantic Highlighting (highlights.scm)

| Status | Power | Unlocks | Notes |
|--------|-------|---------|-------|
| [ ] | Token Classification | Semantic meaning | @keyword, @function |
| [ ] | Context-aware | Def vs call | @function vs @function.call |
| [ ] | Custom Groups | Domain tokens | @atom.repository |
| [ ] | Scope-aware | Combined tracking | With locals.scm |

### Language Injection (injections.scm)

| Status | Power | Unlocks | Notes |
|--------|-------|---------|-------|
| [ ] | @injection.content | Content to re-parse | String bodies |
| [ ] | @injection.language | Target language | SQL, GraphQL |
| [ ] | injection.combined | Merge fragments | Multiple strings |
| [ ] | SQL in Python | Database queries | Detect SQL patterns |
| [ ] | GraphQL in JS | API queries | GQL strings |
| [ ] | HTML in Templates | Template parsing | Template literals |

---

## LANGUAGE COVERAGE

### Python (tree-sitter-python)

| Status | Node Type | Category | Unlocks |
|--------|-----------|----------|---------|
| [x] | function_definition | Definition | Function extraction |
| [x] | class_definition | Definition | Class extraction |
| [ ] | async_function_definition | Definition | Async detection |
| [~] | decorated_definition | Definition | Decorator names |
| [ ] | lambda | Expression | Anonymous functions |
| [ ] | if_statement | Control Flow | Complexity metrics |
| [ ] | elif_clause | Control Flow | Branch counting |
| [ ] | else_clause | Control Flow | Branch counting |
| [ ] | for_statement | Control Flow | Loop detection |
| [ ] | while_statement | Control Flow | Loop detection |
| [ ] | try_statement | Control Flow | Exception flow |
| [ ] | except_clause | Control Flow | Handler counting |
| [ ] | finally_clause | Control Flow | Cleanup detection |
| [ ] | with_statement | Control Flow | Context managers |
| [ ] | match_statement | Control Flow | Pattern matching |
| [ ] | case_clause | Control Flow | Case counting |
| [x] | call | Expression | Call extraction |
| [ ] | assignment | Expression | Data flow |
| [ ] | augmented_assignment | Expression | Mutation tracking |
| [~] | attribute | Expression | Method calls |
| [ ] | subscript | Expression | Index access |
| [ ] | list_comprehension | Expression | Comprehension |
| [ ] | dict_comprehension | Expression | Comprehension |
| [ ] | set_comprehension | Expression | Comprehension |
| [ ] | generator_expression | Expression | Generator |
| [ ] | await | Expression | Async detection |
| [ ] | yield | Expression | Generator detection |
| [ ] | yield_from | Expression | Generator delegation |
| [ ] | return_statement | Statement | Return analysis |
| [ ] | raise_statement | Statement | Exception source |
| [ ] | assert_statement | Statement | Validation |
| [x] | import_statement | Statement | Dependencies |
| [x] | import_from_statement | Statement | Dependencies |
| [ ] | string | Literal | String analysis |
| [ ] | type annotation | Type | Type extraction |
| [ ] | comment | Other | Documentation |
| [ ] | ERROR | Other | Syntax errors |

**Python Coverage: ~10/35 = 29%**

### JavaScript/TypeScript

| Status | Node Type | Category | Unlocks |
|--------|-----------|----------|---------|
| [x] | function_declaration | Definition | Function extraction |
| [x] | function_expression | Definition | Anonymous functions |
| [x] | arrow_function | Definition | Arrow functions |
| [x] | class_declaration | Definition | Class extraction |
| [ ] | class_expression | Definition | Anonymous classes |
| [~] | method_definition | Definition | Class methods |
| [ ] | generator_function | Definition | Generator detection |
| [ ] | jsx_element | JSX | React components |
| [ ] | jsx_self_closing_element | JSX | Simple components |
| [ ] | jsx_attribute | JSX | Prop analysis |
| [ ] | jsx_expression | JSX | Embedded expressions |
| [ ] | if_statement | Control Flow | Complexity |
| [ ] | switch_statement | Control Flow | Case analysis |
| [ ] | switch_case | Control Flow | Branch counting |
| [ ] | for_statement | Control Flow | Loop detection |
| [ ] | for_in_statement | Control Flow | Object iteration |
| [ ] | for_of_statement | Control Flow | Array iteration |
| [ ] | while_statement | Control Flow | Loop detection |
| [ ] | do_statement | Control Flow | Loop detection |
| [ ] | try_statement | Control Flow | Exception flow |
| [ ] | catch_clause | Control Flow | Handler counting |
| [ ] | finally_clause | Control Flow | Cleanup detection |
| [x] | call_expression | Expression | Call extraction |
| [x] | member_expression | Expression | Method calls |
| [x] | new_expression | Expression | Constructor calls |
| [ ] | assignment_expression | Expression | Data flow |
| [ ] | await_expression | Expression | Async detection |
| [ ] | ternary_expression | Expression | Conditional |
| [ ] | template_literal | Literal | String templates |
| [ ] | template_substitution | Literal | Interpolation |
| [~] | import_statement | Module | Dependencies |
| [~] | export_statement | Module | Exports |
| [ ] | named_imports | Module | Import details |
| [ ] | type_annotation | TypeScript | Type info |
| [~] | interface_declaration | TypeScript | Interface names |
| [~] | type_alias_declaration | TypeScript | Type names |
| [ ] | enum_declaration | TypeScript | Enum analysis |
| [ ] | ERROR | Other | Syntax errors |

**JS/TS Coverage: ~12/37 = 32%**

### Go (tree-sitter-go)

| Status | Node Type | Category | Unlocks |
|--------|-----------|----------|---------|
| [x] | function_declaration | Definition | Function extraction |
| [x] | method_declaration | Definition | Method extraction |
| [x] | type_declaration (struct) | Definition | Struct extraction |
| [x] | type_declaration (interface) | Definition | Interface extraction |
| [ ] | go_statement | Concurrency | Goroutine detection |
| [ ] | select_statement | Concurrency | Channel select |
| [ ] | channel_type | Concurrency | Channel analysis |
| [ ] | send_statement | Concurrency | Channel send |
| [ ] | receive_expression | Concurrency | Channel receive |
| [ ] | if_statement | Control Flow | Complexity |
| [ ] | for_statement | Control Flow | Loop detection |
| [ ] | range_clause | Control Flow | Range iteration |
| [ ] | switch_statement | Control Flow | Case analysis |
| [ ] | type_switch_statement | Control Flow | Type assertion |
| [ ] | defer_statement | Control Flow | Lifecycle |
| [~] | call_expression | Expression | Call extraction |
| [ ] | selector_expression | Expression | Method calls |
| [ ] | composite_literal | Expression | Struct creation |
| [ ] | ERROR | Other | Syntax errors |

**Go Coverage: ~5/19 = 26%**

### Rust (tree-sitter-rust)

| Status | Node Type | Category | Unlocks |
|--------|-----------|----------|---------|
| [x] | function_item | Definition | Function extraction |
| [x] | struct_item | Definition | Struct extraction |
| [x] | enum_item | Definition | Enum extraction |
| [x] | trait_item | Definition | Trait extraction |
| [x] | impl_item | Definition | Impl blocks |
| [ ] | match_expression | Control Flow | Pattern matching |
| [ ] | match_arm | Control Flow | Match branches |
| [ ] | if_expression | Control Flow | Conditional |
| [ ] | if_let_expression | Control Flow | Pattern if |
| [ ] | loop_expression | Control Flow | Loops |
| [ ] | while_expression | Control Flow | While loops |
| [ ] | for_expression | Control Flow | For loops |
| [ ] | reference_expression | Ownership | Borrowing |
| [ ] | borrow_expression | Ownership | Mutable borrow |
| [ ] | lifetime | Ownership | Lifetime tracking |
| [ ] | async_block | Async | Async detection |
| [ ] | macro_invocation | Macro | Macro calls |
| [ ] | macro_definition | Macro | Macro defs |
| [ ] | unsafe_block | Safety | Unsafe detection |
| [~] | call_expression | Expression | Call extraction |
| [ ] | ERROR | Other | Syntax errors |

**Rust Coverage: ~6/21 = 29%**

---

## THEORY INTEGRATION

### 8 Dimensions Status

| Dimension | Power Source | Status | Confidence |
|-----------|-------------|--------|------------|
| D1: WHAT | Node types + patterns.scm | [~] | 60% |
| D2: LAYER | Import analysis | [~] | 70% |
| D3: ROLE | Call patterns | [~] | 50% |
| D4: BOUNDARY | Module resolution | [~] | 65% |
| D5: STATE | locals.scm | [ ] | 0% |
| D6: EFFECT | Assignment tracking | [ ] | 0% |
| D7: LIFECYCLE | Pattern detection | [ ] | 0% |
| D8: TRUST | Multi-source evidence | [~] | 40% |

### RPBL Extraction

| Metric | Power Source | Status | Confidence |
|--------|-------------|--------|------------|
| Responsibility | Method count, fan-out | [ ] | 0% |
| Purity | Assignment tracking | [ ] | 0% |
| Boundary | External calls | [~] | 50% |
| Lifecycle | Pattern detection | [ ] | 0% |

### Atom Detection Enhancement

| Atom | Current Method | Enhanced Method | Status |
|------|---------------|-----------------|--------|
| Entity | Name pattern | Field + method analysis | [ ] |
| Repository | Name pattern | CRUD signature detection | [ ] |
| Service | Name pattern | DI pattern detection | [ ] |
| Controller | Decorator | Route pattern analysis | [~] |
| Factory | Name pattern | Return `new X` pattern | [ ] |
| Builder | Name pattern | Return `self` pattern | [ ] |
| Validator | Name pattern | Bool return + raises | [ ] |
| Transformer | Name pattern | Type transformation | [ ] |
| Handler | Name pattern | Event parameter | [ ] |

---

## METRICS UNLOCKABLE

| Metric | Power Source | Status | Value |
|--------|-------------|--------|-------|
| Cyclomatic Complexity | Control flow nodes | [ ] | Code quality |
| Nesting Depth | AST depth | [ ] | Readability |
| Call Fan-out | Call extraction | [~] | Coupling |
| Call Fan-in | Reverse call graph | [ ] | Importance |
| Unused Variables | locals.scm | [ ] | Dead code |
| Shadowed Variables | locals.scm | [ ] | Bug risk |
| Error Node Count | ERROR nodes | [ ] | Syntax quality |
| Missing Node Count | MISSING nodes | [ ] | Incomplete code |
| Method Count per Class | Definition counting | [~] | Responsibility |
| Parameter Count | Parameter nodes | [ ] | Complexity |
| Return Points | return_statement | [ ] | Complexity |
| Exception Handlers | except_clause | [ ] | Error handling |

---

## VISUALIZATION INTEGRATION

| Feature | Data Source | Visual Representation | Status |
|---------|-------------|----------------------|--------|
| Syntax Errors | ERROR nodes | Red badge | [ ] |
| Complexity Heat | Cyclomatic | Node color intensity | [ ] |
| Unused Code | Scope analysis | Faded/grayed | [ ] |
| Purity Indicator | Effect tracking | Green/yellow/red | [ ] |
| Lifecycle Phase | Pattern detection | Node shape | [ ] |
| Scope Boundaries | locals.scm | Nesting visualization | [ ] |
| Data Flow | Assignment tracking | Animated edges | [ ] |
| Call Depth | Call graph | Distance coloring | [ ] |

---

## IMPLEMENTATION PROGRESS

### Phase 1: Foundation
- [ ] P1-01: Create queries/ directory
- [ ] P1-02: Implement QueryLoader
- [ ] P1-03: Python definitions.scm
- [ ] P1-04: JS/TS definitions.scm
- [ ] P1-05: Go definitions.scm
- [ ] P1-06: Rust definitions.scm
- [ ] P1-07: Refactor tree_sitter_engine.py
- [ ] P1-08: ERROR node detection
- [ ] P1-09: Error count in schema
- [ ] P1-10: Query loading tests
- [ ] P1-11: Documentation

### Phase 2: Scope Analysis
- [ ] P2-01: Python locals.scm
- [ ] P2-02: JS/TS locals.scm
- [ ] P2-03: ScopeAnalyzer class
- [ ] P2-04: Scope tree building
- [ ] P2-05: Unused variable detection
- [ ] P2-06: Shadowing detection
- [ ] P2-07: Scope data in schema
- [ ] P2-08: Edge extractor integration
- [ ] P2-09: D5_STATE extraction
- [ ] P2-10: Scope analysis tests

### Phase 3: Control Flow
- [ ] P3-01: ControlFlowAnalyzer
- [ ] P3-02: Cyclomatic complexity
- [ ] P3-03: Nesting depth
- [ ] P3-04: Early return detection
- [ ] P3-05: Recursion detection
- [ ] P3-06: Metrics in schema
- [ ] P3-07: Health scoring update
- [ ] P3-08: Control flow tests

### Phase 4: Pattern Detection
- [ ] P4-01: Python patterns.scm
- [ ] P4-02: JS/TS patterns.scm
- [ ] P4-03: Classifier integration
- [ ] P4-04: RPBL extraction
- [ ] P4-05: D6_EFFECT extraction
- [ ] P4-06: D7_LIFECYCLE extraction
- [ ] P4-07: Confidence scoring
- [ ] P4-08: Pattern detection tests

### Phase 5: Advanced
- [ ] P5-01: Incremental parsing
- [ ] P5-02: File watcher
- [ ] P5-03: Python injections.scm
- [ ] P5-04: JS injections.scm
- [ ] P5-05: Injection parsing
- [ ] P5-06: Data flow graph
- [ ] P5-07: Cross-function tracking
- [ ] P5-08: highlights.scm files
- [ ] P5-09: Visualizer integration

---

## CHANGELOG

| Date | Change |
|------|--------|
| 2026-01-21 | Initial inventory created |

---

*Update this document as capabilities are implemented.*
*Mark items [x] when complete, [~] when partial.*
