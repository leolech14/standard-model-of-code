# Component C1: Full Atom Enumeration Roadmap

> **Goal**: Complete enumeration of all ~200 atoms organized into the periodic table structure
> **Priority**: ★★★★★ Critical Path
> **Estimated Duration**: Week 1-2

---

## Current State

| Metric | Current | Target |
|--------|---------|--------|
| Atoms documented | ~30% | 100% |
| Phases defined | 4/4 | 4/4 ✅ |
| Families defined | ~15/22 | 22/22 |
| Cross-language mappings | Partial | 5 languages |

---

## Phase 0: Pre-Development Research

### 0.1 Extract All AST Node Types (Day 1-2)

**Objective**: Get complete lists of AST node types from all target Tree-sitter grammars.

**Actions**:
```bash
# Clone Tree-sitter grammar repos
git clone https://github.com/tree-sitter/tree-sitter-python
git clone https://github.com/tree-sitter/tree-sitter-typescript
git clone https://github.com/tree-sitter/tree-sitter-java
git clone https://github.com/tree-sitter/tree-sitter-go
git clone https://github.com/tree-sitter/tree-sitter-rust

# Extract node types from each grammar
for lang in python typescript java go rust; do
  cat tree-sitter-$lang/src/node-types.json | jq '.[].type' > extracted_nodes_$lang.txt
done
```

**Expected Output**:
| Language | Estimated Node Types |
|----------|---------------------|
| Python | ~108 types |
| TypeScript | ~115 types |
| Java | ~95 types |
| Go | ~52 types |
| Rust | ~84 types |
| **Union** | ~150-200 unique atoms |

**Deliverable**: `/research/extracted_nodes/` directory with raw extraction

---

### 0.2 Analyze Existing Atom Documentation (Day 2)

**Objective**: Inventory what we already have documented.

**Actions**:
1. Review `docs/ATOMS_REFERENCE.md` (if exists)
2. Review `core/llm_classifier.py` for existing classifications
3. Extract atoms from `collider_output/` analysis results
4. Cross-reference with `schema/` if present

**Questions to Answer**:
- Which atoms are fully specified with all dimensions?
- Which atoms have cross-language mappings?
- Which atoms are missing entirely?

**Deliverable**: Gap analysis spreadsheet

---

### 0.3 Define Canonical Atom Structure (Day 3)

**Objective**: Finalize the schema for each atom entry.

**Proposed Structure**:
```yaml
atom:
  id: "Fn_FunctionDef"  # Unique ID: Family_AtomName
  symbol: "Fn"          # 2-letter symbol
  name: "Function Definition"
  phase: "LOGIC"
  family: "FUNCTIONS"
  description: "A named, callable code block with parameters and return value"
  
  # Semantic mappings (how to classify once detected)
  default_dimensions:
    D2_LAYER: "contextual"      # Depends on location
    D3_ROLE: "contextual"       # Depends on naming/behavior
    D4_BOUNDARY: "Internal"     # Default unless detected otherwise
    D5_STATE: "Stateless"       # Default for functions
    D6_EFFECT: "contextual"     # Requires analysis
    D7_LIFECYCLE: "Use"         # Default
    
  # AST mappings per language
  ast_mappings:
    python: 
      - node_type: "function_definition"
        indicators: ["def", "async def"]
    typescript:
      - node_type: "function_declaration"
        indicators: ["function"]
      - node_type: "arrow_function"
        indicators: ["=>"]
    java:
      - node_type: "method_declaration"
        indicators: ["void", "public", "private", "protected"]
    go:
      - node_type: "function_declaration"
        indicators: ["func"]
    rust:
      - node_type: "function_item"
        indicators: ["fn"]
  
  # Related atoms
  related_atoms:
    - "Fn_Method"       # Method is a function inside a class
    - "Fn_Lambda"       # Anonymous function
    - "Fn_Generator"    # Generator function
    - "Fn_Coroutine"    # Async function
  
  # Detection heuristics
  detection_notes: |
    - Functions with `self` parameter → Method
    - Functions with `async` → Coroutine
    - Functions with `yield` → Generator
```

**Deliverable**: `schema/atom_template.yaml` with full specification

---

## Phase 1: Initial Enumeration (Week 1)

### 1.1 Complete DATA Phase Atoms (Day 4-5)

**Families**:
| Family | Symbol | Expected Atoms |
|--------|--------|----------------|
| CONSTANTS | Cn | 8-10 (IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, NoneLiteral, ComplexLiteral, BytesLiteral, FormattedString) |
| VARIABLES | Vr | 6-8 (Identifier, Assignment, AugmentedAssignment, Declaration, Destructuring, GlobalDeclaration) |
| TYPES | Tp | 10-15 (Primitive, Generic, Union, Optional, Alias, Callable, Protocol, TypeVar, NewType) |
| COLLECTIONS | Cl | 8-12 (List, Dict, Set, Tuple, Array, Map, Queue, Stack, Deque, PriorityQueue) |
| PATTERNS | Pt | 5-8 (MatchCase, Pattern, Guard, Wildcard, SequencePattern, MappingPattern) |

**Deliverable**: `schema/atoms/DATA_PHASE.yaml`

---

### 1.2 Complete LOGIC Phase Atoms (Day 5-6)

**Families**:
| Family | Symbol | Expected Atoms |
|--------|--------|----------------|
| FUNCTIONS | Fn | 8-10 (FunctionDef, Method, Lambda, Generator, Coroutine, Constructor, Destructor, StaticMethod, ClassMethod) |
| OPERATIONS | Op | 15-20 (BinaryOp, UnaryOp, Comparison, Assignment, Augmented, LogicalOp, BitwiseOp, Ternary) |
| CONTROL_FLOW | Cf | 10-15 (If, Else, For, While, Try, Except, Finally, With, Match, Break, Continue, Return, Yield, Raise) |
| EXPRESSIONS | Ex | 10-12 (Call, Attribute, Subscript, Slice, Comprehension, Await, Lambda, Conditional) |

**Deliverable**: `schema/atoms/LOGIC_PHASE.yaml`

---

### 1.3 Complete ORGANIZATION Phase Atoms (Day 6-7)

**Families**:
| Family | Symbol | Expected Atoms |
|--------|--------|----------------|
| CONTAINERS | Ct | 6-8 (Class, Interface, Protocol, Struct, Enum, Abstract, Trait, Mixin) |
| MODULES | Md | 5-7 (Module, Package, Namespace, Import, Export, Re-export, Wildcard) |
| IMPORTS | Im | 5-6 (Import, ImportFrom, ImportAlias, ImportGroup, DynamicImport, ConditionalImport) |
| DECORATORS | Dc | 4-6 (Decorator, DecoratorFactory, PropertyDecorator, ClassDecorator) |

**Deliverable**: `schema/atoms/ORGANIZATION_PHASE.yaml`

---

### 1.4 Complete EXECUTION Phase Atoms (Day 7-8)

**Families**:
| Family | Symbol | Expected Atoms |
|--------|--------|----------------|
| ENTRY_POINTS | Ep | 4-6 (MainEntry, ScriptGuard, CLIEntry, PluginEntry, TestEntry, Endpoint) |
| ASSERTIONS | As | 4-5 (Assert, TypeGuard, Precondition, Postcondition, Invariant) |
| RESOURCES | Rs | 6-8 (File, Socket, Connection, Stream, Handle, Lock, Semaphore, Pool) |
| METADATA | Mt | 5-7 (Docstring, Comment, Annotation, TypeHint, Pragma, Magic) |

**Deliverable**: `schema/atoms/EXECUTION_PHASE.yaml`

---

## Phase 2: Cross-Language Mapping (Week 2)

### 2.1 Python Mappings (Day 8)

**Objective**: Map all atoms to Python's Tree-sitter node types.

**Source**: [tree-sitter-python/src/node-types.json](https://github.com/tree-sitter/tree-sitter-python)

**Sample Mappings**:
```yaml
# Python-specific mappings
python_mappings:
  Fn_FunctionDef: function_definition
  Fn_Lambda: lambda
  Fn_Generator: function_definition  # detected by presence of yield
  Ct_Class: class_definition
  Cf_If: if_statement
  Cf_For: for_statement
  Cf_While: while_statement
  Cf_Try: try_statement
  Im_Import: import_statement
  Im_ImportFrom: import_from_statement
```

---

### 2.2 TypeScript Mappings (Day 9)

**Objective**: Map all atoms to TypeScript's Tree-sitter node types.

**Source**: [tree-sitter-typescript/src/node-types.json](https://github.com/tree-sitter/tree-sitter-typescript)

**Notes**:
- TypeScript has both function_declaration and arrow_function
- Interface and type_alias are separate concepts
- Generic types need special handling

---

### 2.3 Java/Go/Rust Mappings (Day 10)

**Objective**: Complete mappings for remaining languages.

**Per-language notes**:
- **Java**: method_declaration includes both methods and constructors
- **Go**: Has both function_declaration and method_declaration (receiver-based)
- **Rust**: function_item, impl_item, trait_item are key containers

---

### 2.4 Validation & Gap Filling (Day 11-12)

**Objective**: Verify completeness and fill gaps.

**Actions**:
1. Run Collider on sample codebases, check for "unknown" atoms
2. Cross-check against all Tree-sitter node types
3. Add any missing atoms discovered
4. Document edge cases and ambiguities

---

## Deliverables

| Deliverable | Path | Description |
|-------------|------|-------------|
| Complete Atoms YAML | `/schema/ATOMS_COMPLETE.yaml` | Full periodic table |
| Per-Phase Files | `/schema/atoms/*.yaml` | Phase-organized atoms |
| Language Mappings | `/schema/mappings/*.yaml` | Per-language AST mappings |
| Gap Analysis | `/docs/ATOMS_GAP_ANALYSIS.md` | Known gaps and edge cases |
| Visualization | `/docs/assets/periodic_table.png` | Visual periodic table |

---

## Success Criteria

- [ ] All 22 families defined with symbols
- [ ] All ~200 atoms enumerated with unique IDs
- [ ] All atoms have at least Python + TypeScript mappings
- [ ] No "unknown" atoms when running Collider on test repos
- [ ] Visual periodic table generated
- [ ] Documentation complete and reviewed

---

## Dependencies

- **Blocks**: C2 (JSON Schema) - schema must match atom structure
- **Blocked by**: None - can start immediately
- **Parallel**: C3 (Training Corpus) - can generate training data as atoms are defined

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Some AST types don't fit atoms | Medium | Use "Unknown" with investigation queue |
| Language-specific features | Low | Add language-specific atoms as needed |
| Scope creep (500+ atoms) | Medium | Cap at 200, group edge cases |
