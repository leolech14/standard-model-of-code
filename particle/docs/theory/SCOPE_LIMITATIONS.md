# Scope and Limitations of the Standard Model of Code

**Status:** Academic Draft
**Version:** 1.0.0
**Date:** 2026-02-01

---

## Abstract

This document explicitly defines the scope and limitations of the Standard Model of Code (SMC). We specify what SMC covers, what it explicitly excludes, the assumptions it makes, and known limitations. This transparency is essential for proper application of the framework and for identifying areas requiring future work.

---

## 1. What SMC Covers

### 1.1 Artifact Types

| Artifact | Coverage | Notes |
|----------|----------|-------|
| Source code files | Full | All syntactically valid code |
| Configuration files | Full (Contextome) | YAML, JSON, TOML, etc. |
| Documentation | Full (Contextome) | Markdown, RST, etc. |
| Build files | Full | Makefile, package.json, etc. |
| Test files | Full | Classified as code |
| Schemas | Full | JSON Schema, OpenAPI, etc. |

### 1.2 Programming Languages

SMC is language-agnostic in theory. Current implementation (Collider) supports:

| Language | Status | Notes |
|----------|--------|-------|
| Python | Full | Primary development language |
| JavaScript | Full | Via Tree-sitter |
| TypeScript | Full | Via Tree-sitter |
| Go | Full | Via Tree-sitter |
| Rust | Full | Via Tree-sitter |
| Java | Full | Via Tree-sitter |
| C/C++ | Full | Via Tree-sitter |
| Ruby | Full | Via Tree-sitter |
| PHP | Full | Via Tree-sitter |
| C# | Full | Via Tree-sitter |
| Swift | Partial | Basic support |
| Kotlin | Partial | Basic support |
| Scala | Partial | Basic support |
| HTML/CSS | Full | Via Tree-sitter |
| SQL | Full | Via Tree-sitter |

### 1.3 Programming Paradigms

| Paradigm | Coverage | Notes |
|----------|----------|-------|
| Object-oriented | Full | Primary focus |
| Functional | Full | Pure/impure dimension captures |
| Procedural | Full | Supported |
| Declarative | Partial | DSLs may need extension |
| Logic | Minimal | Not primary focus |

### 1.4 Analysis Scope

| Aspect | Coverage | Notes |
|--------|----------|-------|
| Static structure | Full | AST-level analysis |
| Dependencies | Full | Imports, calls, contains |
| Containment hierarchy | Full | Files > classes > methods > blocks |
| Type relationships | Partial | Inheritance, implementation |
| Control flow | Planned | Future extension |
| Data flow | Planned | Future extension |

---

## 2. What SMC Does NOT Cover

### 2.1 Explicit Exclusions

| Exclusion | Reason |
|-----------|--------|
| **Runtime behavior** | SMC analyzes static structure, not execution traces |
| **Dynamic typing** | Cannot infer all types without execution |
| **Generated code** | Stubs, transpiled output are not human-authored |
| **Binary code** | Requires disassembly, out of scope |
| **Obfuscated code** | Intentionally obscured, defeats analysis |

### 2.2 Boundaries with Other Domains

| Domain | SMC Boundary |
|--------|--------------|
| **Program correctness** | SMC classifies structure; Hoare logic proves correctness |
| **Performance** | SMC doesn't predict runtime performance |
| **Security** | SMC identifies structure, not vulnerabilities |
| **Human factors** | SMC doesn't model developer experience |
| **Project management** | Outside scope (covered by SEMAT) |

### 2.3 Temporal Limitations

| Aspect | Current State | Future |
|--------|---------------|--------|
| Single snapshot | SMC analyzes one version at a time | Temporal layer planned |
| No git history | Change history not incorporated | PyDriller integration planned |
| No runtime data | No profiling data used | OpenTelemetry bridge planned |

---

## 3. Assumptions

### 3.1 Input Assumptions

| Assumption | Implication |
|------------|-------------|
| **Code is syntactically valid** | Unparseable code cannot be analyzed |
| **Files are readable** | Binary, encrypted files excluded |
| **Character encoding is valid** | UTF-8 or declared encoding |
| **Project structure exists** | Some directory organization assumed |

### 3.2 Theoretical Assumptions

| Assumption | Justification |
|------------|---------------|
| **Discrete entities exist** | Nodes are fundamental; continuous structures must be discretized |
| **Containment is hierarchical** | No cyclic containment (file contains function contains statement) |
| **Levels form a total order** | All entities are comparable by level |
| **Dimensions are orthogonal** | Independence assumed, to be empirically validated |
| **Atoms are MECE** | Every entity fits exactly one atom |

### 3.3 Practical Assumptions

| Assumption | Mitigation if Violated |
|------------|----------------------|
| Code follows conventions | Lower classification confidence |
| Names are meaningful | Fall back to structural analysis |
| Structure reflects intent | Crystallization axiom acknowledges drift |

---

## 4. Known Limitations

### 4.1 Classification Limitations

| Limitation | Severity | Mitigation |
|------------|----------|------------|
| **Role inference is heuristic** | Medium | Confidence scores provided |
| **Some atoms may overlap** | Low | Refinement in progress |
| **New patterns may not fit** | Medium | Extensibility mechanism planned |
| **Context-dependent classification** | Medium | Multiple classifications possible |

### 4.2 Implementation Limitations

| Limitation | Severity | Status |
|------------|----------|--------|
| **Tree-sitter parser limits** | Low | Grammar extensions possible |
| **Large codebase performance** | Medium | Incremental analysis planned |
| **Cross-file analysis** | Medium | Import resolution implemented |
| **Semantic analysis** | High | Type inference not yet integrated |

### 4.3 Theoretical Limitations

| Limitation | Discussion |
|------------|------------|
| **167 atoms may be too many** | Hierarchical grouping available |
| **167 atoms may be too few** | Extensibility mechanism allows additions |
| **8 dimensions may be too few** | Additional dimensions could be added |
| **8 dimensions may be too many** | Some may be derivable from others |
| **16 levels may be arbitrary** | Zone boundaries are principled |

---

## 5. Scope vs. SEMAT, SWEBOK, SEVOCAB

### 5.1 Complementary Scopes

| Framework | Scope | SMC Relationship |
|-----------|-------|------------------|
| **SWEBOK** | Knowledge organization | SMC provides formal structure |
| **SEMAT** | Method composition | SMC provides entity-level detail |
| **SEVOCAB** | Terminology | SMC provides coordinates |

### 5.2 Non-Overlapping Concerns

| Concern | Covered By | Not SMC |
|---------|------------|---------|
| Project management | SEMAT/SWEBOK | - |
| Team dynamics | SEMAT | - |
| Process definition | SEMAT | - |
| Economic analysis | SWEBOK | - |
| Legal compliance | Outside all | - |

---

## 6. Version Scope

### 6.1 SMC Version 1.0

This document describes SMC Version 1.0, which:

**Includes:**
- Static structural analysis
- 167 atom taxonomy
- 8 classification dimensions
- 16 hierarchical levels
- 5 zone boundaries
- 4 ring partitions

**Excludes (planned for future versions):**
- Runtime flow analysis (v1.1)
- Temporal/change analysis (v1.2)
- Social/authorship graph (v1.3)
- Operational/deployment mapping (v1.4)

### 6.2 Versioning Policy

| Change Type | Version Bump |
|-------------|--------------|
| New atoms | Minor (1.x) |
| New dimensions | Major (x.0) |
| New levels | Major (x.0) |
| Axiom changes | Major (x.0) |
| Implementation improvements | Patch (1.0.x) |

---

## 7. Applicability Guidelines

### 7.1 When to Use SMC

| Scenario | Recommendation |
|----------|----------------|
| Codebase exploration | Recommended |
| Architecture documentation | Recommended |
| Onboarding new developers | Recommended |
| Code review support | Recommended |
| Dependency analysis | Recommended |
| Technical debt assessment | Recommended |

### 7.2 When NOT to Use SMC

| Scenario | Recommendation |
|----------|----------------|
| Runtime performance optimization | Use profilers |
| Security vulnerability detection | Use security scanners |
| Correctness verification | Use formal methods |
| Dynamic language metaprogramming | Limited applicability |
| Generated code analysis | Not meaningful |

---

## 8. Future Scope Extensions

### 8.1 Planned Extensions

| Extension | Priority | Timeline |
|-----------|----------|----------|
| Runtime metrics layer | High | v1.1 |
| Git history integration | High | v1.2 |
| Author/ownership graph | Medium | v1.3 |
| Deployment mapping | Medium | v1.4 |
| Natural language analysis | Low | v2.0 |

### 8.2 Research Directions

| Direction | Status |
|-----------|--------|
| ML-based classification | Explored |
| Cross-repository analysis | Conceptual |
| Real-time analysis | Conceptual |
| IDE integration | Planned |

---

## 9. Summary

The Standard Model of Code is a framework for **static structural classification** of source code artifacts. It provides:

**Scope:**
- 15+ programming languages
- All major paradigms (OOP, FP, procedural)
- Static AST-level analysis
- Dependency and containment relationships

**Limitations:**
- No runtime behavior analysis (yet)
- No temporal/change analysis (yet)
- Role inference is heuristic
- Assumes syntactically valid code

**Assumptions:**
- Discrete entities exist
- Containment is hierarchical
- Levels form a total order
- Dimensions are orthogonal
- Atoms are MECE

These boundaries are explicit by design. SMC does one thing well (structural classification) rather than attempting comprehensive coverage of all software engineering concerns.

---

*This document addresses Gap 5 (Scope and Limitations) from the SMC Academic Gap Analysis.*
