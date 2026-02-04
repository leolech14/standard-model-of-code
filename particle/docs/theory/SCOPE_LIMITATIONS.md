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

## 10. Known Critiques and Responses

This section addresses critiques extracted from an AI-assisted debate analysis (2026-02-01). This is critique synthesis, not empirical validation.

### 10.1 "L2 Principles Are Analogies, Not Proofs"

**Critique:** The L2 layer uses phrases like "inspired by Friston" and "analogous to Tononi's IIT". If these are analogies, not derivations, then metrics derived from them measure fit-to-metaphor, not objective reality.

**Response:**
| Point | Counter |
|-------|---------|
| "Inspired by" language | Honest about theoretical heritage; physics also builds on prior frameworks |
| Analogies can be rigorous | CDPS scores analogies reproducibly under explicit rubric (not truth detection) |
| Consilience (weak) | Similar math in both domains motivates hypothesis of shared structure; requires empirical test |
| Practical utility | Even if analogical, the diagnostics provide actionable insights |

**Status:** Acknowledged. SMC is transparent that L2 laws are *inspired by* external theories, not derived purely from L0 axioms. This is a feature (cross-domain inspiration and consilience seeking), not a bug.

### 10.2 "Thresholds Are Arbitrary"

**Critique:** The God Class threshold (e.g., >20 methods) is not universal. It varies by language, project size, and team conventions. Calling these "laws" implies false universality.

**Response:**
| Point | Counter |
|-------|---------|
| Thresholds are configurable | Implementation allows per-project calibration |
| Physics has constants too | Gravitational constant G was empirically measured |
| Context-aware defaults | Different defaults for microservice vs monolith |
| The structure is universal | Even if numbers vary, the *concept* of God Class is universal |

**Recommendation:** Rename "Antimatter Laws" to "Antimatter Patterns" or "Antimatter Heuristics" to avoid implying universal constants.

### 10.3 "Lawvere Fixed-Point Theorem Over-Interpretation"

**Critique:** The application of Lawvere's fixed-point theorem assumes code is a pure formal system. Modern code with rich types, naming, and annotations is already a partial meta-language for itself.

**Response:**
| Point | Counter |
|-------|---------|
| Code does self-document partially | Agreed; the gap is reduced but not eliminated |
| Business intent remains external | `calculateTax()` doesn't explain tax law |
| Practical experience confirms | Every developer has faced syntactically valid but semantically opaque code |
| The gap is empirical | Not just theoretical; measurable as semantic incompleteness |

**Status:** The theorem application is acknowledged as *philosophical* rather than strictly mathematical. The practical point remains valid: code alone cannot fully specify its purpose.

### 10.4 "Science vs Heuristic"

**Critique:** Is SMC a science (predictive, falsifiable) or a heuristic (useful rules of thumb)?

**Response:**

**SMC is BOTH:**

| Aspect | Classification |
|--------|----------------|
| L0 Axioms | Formal/Axiomatic |
| L1 Definitions (Atoms, Dimensions) | Taxonomic/Deterministic |
| L2 Principles (Purpose Field, Antimatter) | Heuristic/Inspired |
| L3 Applications (Q-Score, Health) | Diagnostic/Practical |

**Position Statement:**
> SMC is a *structured heuristic framework* with an axiomatic foundation. It does not claim to be a physical science with universal constants. It claims to provide a *rigorous vocabulary* and *measurable diagnostics* for software architecture. Treating its outputs as "indicators" rather than "absolute truths" is the correct interpretation.

### 10.5 The Discovery vs Invention Question

**Critique:** Is SMC discovering pre-existing truths about software, or inventing useful frameworks?

**Response:** See dedicated document: `EPISTEMOLOGICAL_STATUS.md`

**Summary Position: CONSTRAINED INVENTION**

| Aspect | Status |
|--------|--------|
| Code has mathematical structure | DISCOVERED (objective) |
| Graph metrics describe it | DISCOVERED (math works) |
| 187 atoms taxonomy | INVENTED (could differ) |
| Threshold values | INVENTED (configurable) |
| CDPS validates analogies | BRIDGE (tests if discovery or projection) |

> "We are CARTOGRAPHERS, not EXPLORERS. The territory is real. The map is our invention. But not any map works—only those that respect the territory."

### 10.6 Summary of Critique Integration

| Critique | Validity | Action Taken |
|----------|----------|--------------|
| L2 is analogical | Valid | Documented in L1_DEFINITIONS.md |
| Thresholds are arbitrary | Valid | Made configurable; renamed "laws" to "patterns" |
| Lawvere over-interpretation | Partially valid | Clarified as "philosophical" application |
| Science vs heuristic | Valid distinction | Positioned as "axiomatic heuristics" |

**Source:** AI-generated debate analysis (NotebookLM, 2026-02-01). Transcripts archived at `particle/docs/research/notebooklm/`.

---

*This document addresses Gap 5 (Scope and Limitations) from the SMC Academic Gap Analysis.*
