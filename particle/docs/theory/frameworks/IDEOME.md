# THE IDEOME SPECIFICATION

## Collider's Third Epistemic Layer and the Rosetta Stone Computation

**Status:** Foundational Specification
**Version:** 1.0.0
**Date:** 2026-03-02
**Authors:** Leo (Architect), Claude (Formalization)
**Depends on:** Incoherence Lagrangian, Contextome Intelligence (Stage 0.8), Purpose Field Integration Spec, Projectome Omniscience Module Spec
**Supersedes:** Two-partition Projectome model (Codome + Contextome)

---

## 0. Abstract

This document formalizes the **Ideome** — the third and final epistemic layer of the Projectome — and establishes the **Three-Layer Epistemic Stack** as Collider's core macro architecture. Where the Codome captures *what IS* (executable reality) and the Contextome captures *what is SAID* (declared intent), the Ideome captures *what SHOULD BE* (the ontological specification, the Platonic Form of the system).

The Ideome is not a third partition of files on disk. It is a **computed surface** — the translation layer between Codome and Contextome that enables **drift attribution**: the ability to answer not just "is there incoherence?" but "who drifted, and from what?"

We call this the **Rosetta Stone Computation** because, like the historical artifact, the Ideome provides the reference frame that makes two otherwise opaque systems mutually interpretable.

---

## 1. Motivation: The Attribution Problem

### 1.1 The Current Limitation

Collider's Incoherence Lagrangian I(C) measures five terms:

    I(C) = I_struct + I_telic + I_sym + I_bound + I_flow

The I_sym (symmetry) term currently measures **delta_CX** — the gap between Codome and Contextome. When I_sym is high, we know code and documentation disagree. But we cannot answer the critical follow-up question:

> **Who drifted?**

Did the code evolve past what the documentation describes? Or did the documentation describe an architecture that was never implemented? Or did both drift independently from the original intent?

Without a reference frame, all drift looks the same.

### 1.2 The Platonic Insight

The resolution comes from Platonic epistemology. In Plato's theory of Forms:

- The **Form** (εἶδος) is the ideal, eternal, immutable specification
- The **Particular** (individual) is the imperfect instantiation
- The **Narrative** (λόγος) is what is said about the particular

Mapped to software systems:

| Platonic Layer | Projectome Layer | Query | Nature |
|---|---|---|---|
| Form (εἶδος) | **Ideome** | "What SHOULD be?" | Ontological specification |
| Particular | **Codome** | "What IS?" | Executable implementation |
| Narrative (λόγος) | **Contextome** | "What is SAID?" | Declared intent, documentation |

The Form is the arbiter. When the Particular and the Narrative disagree, you consult the Form.

### 1.3 The Rosetta Stone Analogy

The Rosetta Stone bore three scripts encoding the same decree:

| Script | Projectome Equivalent | Property |
|---|---|---|
| Egyptian hieroglyphs | Codome | Structural, formal, opaque to non-experts |
| Demotic script | Contextome | Natural language, readable, imprecise |
| Greek | Ideome | The known reference, the standard you trust |

The Greek wasn't "better" than the hieroglyphs. It was **already understood**. It provided the mapping. The Ideome provides Collider the mapping between "what the code does structurally" and "what the docs claim it does" by anchoring both to "what it's supposed to do."

Like the Rosetta Stone, the Ideome has a specific property: **it's the one you don't argue with.** It's the specification. When code and docs disagree, you check the spec. The spec is the arbiter.

---

## 2. Formal Definition

### 2.1 The Three-Layer Epistemic Stack

**Definition (Projectome, revised).** A Projectome P is a triple:

    P = (C, X, I)

where:

- **C** (Codome) is the set of all executable entities and their structural relationships
- **X** (Contextome) is the set of all non-executable artifacts and their declared intent signals
- **I** (Ideome) is the computed specification surface derived from ontological rules, project declarations, and meta-inference

The original MECE partition P = C ∪ X (where C ∩ X = ∅) still holds for **files on disk**. The Ideome does not partition files. It is a **derived layer** — computed from C, X, and the ontological rule set Ω.

**Notation:**

    I = Φ(C, X, Ω)

where Φ is the **Ideome synthesis function** and Ω is the ontological rule set (Standard Model axioms, CONSTRAINT_RULES, project-specific declarations).

### 2.2 The Ideome Is Not a File Set

This distinction is critical and must not be confused:

| Property | Codome | Contextome | Ideome |
|---|---|---|---|
| Contains files on disk | Yes (.py, .js, .go, ...) | Yes (.md, .rst, .yaml, ...) | **No** |
| Is directly observable | Yes (AST, imports, graph) | Yes (headings, keywords, refs) | **No** — it is computed |
| Persistence | On-disk, version-controlled | On-disk, version-controlled | **Ephemeral** — recomputed per analysis run |
| Source of truth | Implementation truth | Declared truth | **Specified truth** |
| Mutability | Changes with every commit | Changes with every doc update | **Changes with ontological rule updates + project evolution** |

The Ideome is what a physicist would call a "derived quantity" — not measured directly, but computed from observables.

### 2.3 Three Sources of the Ideome

The Ideome is synthesized from three distinct sources, ordered by generality:

**Source 1: Universal Ontology (Ω_universal)**

The Standard Model axioms and CONSTRAINT_RULES that apply to ALL software systems, everywhere. These are pre-loaded, not project-specific.

Examples:
- "A Repository MUST have at least one Query and one Command child" (from CONSTRAINT_RULES)
- Axiom D2: "An entity IS what it IS FOR" — teleological identity
- Atom taxonomy: every code entity maps to one of {Repository, Domain, Subdomain, Module, Component, Atom}
- Emergence rules: composite purpose derives from child purposes

These constitute the "Greek" of the Rosetta Stone — the reference that is already known and does not need to be decoded.

**Source 2: Project-Specific Declarations (Ω_project)**

The project's own declared architecture, found in:
- SUBSYSTEMS.yaml or equivalent structural declarations
- Architecture Decision Records (ADRs)
- CI/CD configuration (what the build system expects to exist)
- Test directory structure (what the test suite assumes about the system)
- Package manifests (what dependencies are declared)

These are authored by humans and represent "the spec as written."

Examples for a hypothetical project:
- "The system SHALL have a Parser hemisphere and an Analysis hemisphere"
- "Authentication MUST be handled by the auth/ module"
- "All API endpoints MUST have corresponding OpenAPI definitions"

**Source 3: Meta-Inferred Synthesis (Φ_meta)**

The computed intersection — the act of triangulation itself. When Codome evidence and Contextome declarations are processed through Ω_universal and Ω_project, contradictions, gaps, and alignments emerge. The synthesis resolves them:

- Codome shows 8 subsystems. Contextome declares 6. Ω_project lists 8. **Resolution:** 8 is correct, Contextome is stale (documentation drift).
- Contextome describes an "event bus" architecture. Codome shows direct function calls. Ω_universal says either is valid. **Resolution:** DRIFT state — the architecture evolved but docs didn't update.
- Codome has a module with zero tests. Contextome says "fully tested." Ω_project requires test coverage. **Resolution:** Both Codome (missing tests) and Contextome (false claim) have drifted.

This third source is what makes the Ideome a **Stone** — the act of reading two scripts against a known reference to produce understanding.

---

## 3. The Drift Geometry

### 3.1 Triangulation

With three layers, Incoherence becomes a **triangulation** — not a comparison. The geometry is:

```
            Ideome (what SHOULD be)
           /         \
          / drift_C    \ drift_X
         /               \
    Codome ----------- Contextome
     (what IS)  Δ_CX   (what is SAID)
```

Three vectors span the space:

| Vector | Definition | Interpretation |
|---|---|---|
| **drift_C** | \|Ideome − Codome\| | **Implementation drift** — code doesn't match the specification |
| **drift_X** | \|Ideome − Contextome\| | **Documentation drift** — docs don't match the specification |
| **Δ_CX** | \|Codome − Contextome\| | **Symmetry gap** — code and docs disagree with each other |

### 3.2 The Triangle Inequality

These three vectors satisfy a constraint:

    Δ_CX ≤ drift_C + drift_X

The symmetry gap between code and docs **cannot exceed** the sum of their individual drifts from the ideal. When Δ_CX ≈ drift_C + drift_X, code and docs drifted in **opposite directions** from the spec. When Δ_CX << drift_C + drift_X, they drifted in the **same direction** (both wrong, but in agreement).

### 3.3 Four Drift Regimes

The drift vectors partition the space into four diagnostic regimes:

| Regime | drift_C | drift_X | Δ_CX | Diagnosis |
|---|---|---|---|---|
| **ALIGNED** | Low | Low | Low | System is healthy. Code, docs, and spec agree. |
| **CODE_DRIFT** | High | Low | High | Code evolved past the spec. Docs are correct. Refactor code or update spec. |
| **DOC_DRIFT** | Low | High | High | Docs describe an outdated or fictional architecture. Code is correct. Update docs. |
| **DUAL_DRIFT** | High | High | Variable | Both drifted. The spec itself may need revision. Architectural review required. |

A fifth edge case exists:

| **SPEC_STALE** | Low | Low | Moderate | Code and docs agree with each other but the spec is outdated. Update Ω_project. |

### 3.4 Drift Attribution Formula

For any node n in the analysis graph, the **attributed incoherence** decomposes as:

    I_sym(n) = α · drift_C(n) + β · drift_X(n) + γ · Δ_CX(n)

where α + β + γ = 1 and the weights are determined by the confidence of each layer's signal:

- **α** scales with Codome analysis confidence (high — deterministic, always available)
- **β** scales with Contextome signal quality (variable — depends on doc structure and LLM enrichment)
- **γ** scales inversely with the other two — the residual when direct drift measurement is weak

When Contextome Intelligence (Stage 0.8) is not available, β → 0 and the formula degrades to the current proxy-based I_sym computation. **Backward compatibility is preserved.**

---

## 4. Ideome Synthesis: The Φ Function

### 4.1 Pipeline Position

The Ideome synthesis runs at **Stage 0.9** — after Contextome Intelligence (Stage 0.8) and before Base Analysis (Stage 1). This positioning is deliberate:

```
Stage 0    Survey (Codome Definition)
Stage 0.8  Contextome Intelligence (Contextome Definition)
Stage 0.9  Ideome Synthesis (Rosetta Stone Computation)  ← NEW
Stage 1    Base Analysis (Graph Construction)
  ...
Stage 12   Final Compilation
```

The Ideome must be computed before the analysis graph is built because it produces **purpose priors** and **drift expectations** that orient every downstream stage.

### 4.2 Synthesis Layers

The Φ function operates in three deterministic passes, with an optional fourth LLM-amplified pass:

**Pass 1: Universal Rule Loading (Ω_universal)**

Load the Standard Model ontology:
- CONSTRAINT_RULES matrix (what each purpose role REQUIRES, EXPECTS, FORBIDS)
- Atom taxonomy and hierarchy rules
- Emergence rules (how child purposes compose into parent purposes)
- Structural invariants (every Repository must have children, every Module must have atoms)

This pass is **static** — the rules are embedded in Collider's theory layer and do not depend on any project input.

**Pass 2: Project Declaration Extraction (Ω_project)**

Extract project-specific specifications from:
- Explicit spec files (SUBSYSTEMS.yaml, architecture docs flagged by Contextome Intelligence)
- CI/CD configuration (what the build system validates)
- Test structure (what the test suite expects to exist)
- Package manifest (declared modules, entry points)
- Contextome-declared constraints (RFC 2119 language extracted in Stage 0.8)

This pass consumes the **Contextome Intelligence output** as its primary input. It transforms raw doc signals into project-specific ontological rules.

**Pass 3: Triangulation (Φ_meta)**

For each entity in the Codome graph:
1. Query Ω_universal: "What does the Standard Model expect for an entity of this type and purpose?"
2. Query Ω_project: "What does the project specification declare about this entity?"
3. Query Contextome: "What do the docs say about this entity?" (via symmetry seeds from Stage 0.8)
4. Compute drift vectors: drift_C, drift_X, Δ_CX
5. Assign drift regime: ALIGNED, CODE_DRIFT, DOC_DRIFT, DUAL_DRIFT, or SPEC_STALE

**Pass 4 (Optional, LLM-Amplified): Semantic Reconciliation**

When an LLM adapter is available:
- Feed Codome structure + Contextome declarations + Ω_project rules to the LLM
- Ask: "Given this specification, this code structure, and this documentation, identify conflicts and suggest which drifted"
- Merge LLM attribution into the deterministic drift vectors as confidence-weighted enrichment

This pass follows the same dual-layer principle established in Contextome Intelligence: **deterministic core always runs, LLM amplifies but never gates.**

### 4.3 The Lawvere Fixed-Point

From the POM Specification: "POM inventories itself since POM ∈ PROJECTOME."

The Ideome inherits this self-referential property. The Ideome specification (this document) is itself part of the Contextome of the PROJECT_elements repository. When Collider runs on itself:

- The Codome contains the Ideome synthesis code
- The Contextome contains this specification document
- The Ideome is computed from both

This creates a fixed-point: the Ideome of Collider includes a specification of how the Ideome should work. If the implementation drifts from this spec, Collider's own Ideome synthesis will detect the drift.

This is not a paradox. It is a **consistency check** — the system's ability to audit its own specification compliance is a feature, not a bug.

---

## 5. Data Contract

### 5.1 IdeomeResult

```
IdeomeResult:
    # Universal ontology loaded
    universal_rules_count: int
    universal_rules_version: str

    # Project-specific declarations extracted
    project_declarations: list[ProjectDeclaration]
    project_declaration_sources: list[str]  # file paths where specs were found

    # Drift analysis per entity
    drift_map: dict[str, DriftAnalysis]  # keyed by entity path

    # Aggregate metrics
    regime_distribution: dict[str, int]  # ALIGNED/CODE_DRIFT/DOC_DRIFT/DUAL_DRIFT/SPEC_STALE → count
    mean_drift_c: float   # average implementation drift
    mean_drift_x: float   # average documentation drift
    mean_delta_cx: float   # average symmetry gap

    # Meta
    ideome_confidence: float  # 0-1, scales with input quality
    llm_used: bool
    synthesis_time_ms: int
```

### 5.2 ProjectDeclaration

```
ProjectDeclaration:
    source: str          # file path or rule system
    declaration_type: str  # 'structural' | 'behavioral' | 'constraint' | 'dependency' | 'architectural'
    target_pattern: str  # glob pattern or entity path
    expected_property: str  # what SHOULD be true
    confidence: float    # 0-1, how certain we are of this declaration
    origin: str          # 'universal' | 'project_explicit' | 'project_inferred' | 'contextome'
```

### 5.3 DriftAnalysis

```
DriftAnalysis:
    entity_path: str
    entity_type: str     # atom taxonomy type

    # Three drift vectors
    drift_c: float       # |Ideome - Codome|, 0-1
    drift_x: float       # |Ideome - Contextome|, 0-1
    delta_cx: float      # |Codome - Contextome|, 0-1

    # Regime classification
    regime: str          # ALIGNED | CODE_DRIFT | DOC_DRIFT | DUAL_DRIFT | SPEC_STALE

    # Attribution
    attribution: dict    # which rules contributed to each drift score

    # Contextome link
    related_docs: list[str]       # doc paths from symmetry seeds
    related_declarations: list[str]  # which ProjectDeclarations apply
```

---

## 6. Integration Points

### 6.1 Feeds Into

| Consumer | What It Receives | How It Changes |
|---|---|---|
| **Incoherence Lagrangian (I_sym)** | drift_c, drift_x, delta_cx per node | I_sym decomposes into attributed incoherence instead of a single proxy score |
| **Purpose Field (Stage 3.7)** | Project declarations as purpose priors | Purpose field seeds from spec-declared intent, not just bottom-up emergence |
| **Gap Detector** | Expected compartments from Ω_project | Gap detection checks against spec, not just Standard Model defaults |
| **Purpose Decomposition** | CONSTRAINT_RULES enriched with project-specific constraints | Decomposition matrix is project-aware, not just generic |
| **Insights Compiler** | Regime distribution, drift attribution | Insights can say "code drifted from spec" not just "code has high incoherence" |

### 6.2 Receives From

| Producer | What It Provides |
|---|---|
| **Survey (Stage 0)** | File inventory, exclusion patterns, framework detection |
| **Contextome Intelligence (Stage 0.8)** | Declared purposes, symmetry seeds, purpose priors, constraint declarations |
| **CONSTRAINT_RULES** | Universal role specifications |
| **Standard Model Axioms** | Ontological hierarchy rules |
| **Project config files** | CI/CD expectations, package manifests, test structure |

### 6.3 Constructal 4-Flow Resistance Completion

The Constructal theory posits four resistance channels:

    R_total = R_static + R_runtime + R_change + R_human

| Channel | Data Source | Status |
|---|---|---|
| R_static | Codome structural analysis (complexity, coupling) | Built (22 dimensions) |
| R_runtime | Runtime data integration | Planned |
| R_change | Temporal analysis (REH, git history) | Built (Stage 11.97) |
| R_human | Contextome + Ideome (documentation quality, spec clarity, drift) | **Now available** |

With the Ideome providing R_human measurement, three of four resistance channels are operational. The Composition Layer — the cross-correlation engine — becomes feasible for the first time.

---

## 7. Relationship to Existing Modules

### 7.1 What Changes

| Module | Before Ideome | After Ideome |
|---|---|---|
| `incoherence.py` I_sym | Proxy: dead_code + unknown_purpose + rpbl_coverage + contextome signals | Full: drift_C + drift_X + Δ_CX with attribution |
| `purpose_field.py` | Pure bottom-up emergence from code structure | Top-down priors from Ideome seed the field before emergence runs |
| `purpose_decomposition.py` | Generic CONSTRAINT_RULES for all projects | Project-specific constraints layered on top of universal rules |
| `gap_detector.py` | Checks against Standard Model defaults | Checks against project specification (missing what the spec says SHOULD exist) |
| `insights_compiler.py` | "High incoherence detected" | "Code drifted from spec in auth module; docs are accurate" |
| `contextome_intel.py` | Standalone Contextome discovery | Feeds directly into Ideome synthesis as primary input |

### 7.2 What Doesn't Change

The deterministic analysis pipeline (Stages 1-11) remains unchanged. The Ideome operates as a **pre-analysis enrichment** (Stage 0.9) and a **post-analysis attribution layer** (wired into Insights at Stage 12). The core graph construction, complexity metrics, coupling analysis, and purpose inference are untouched.

This preserves the fundamental architectural principle: **the deterministic layer IS the product.** The Ideome adds attribution capability without modifying the measurement apparatus.

---

## 8. Design Principles

### 8.1 Deterministic Core, LLM Amplifier

Consistent with Contextome Intelligence and the broader Collider philosophy:

- **Layer 1 (Deterministic, Always Runs):** Universal rule loading, project declaration extraction from structured sources (YAML, JSON, config files), structural drift computation via entity matching
- **Layer 2 (LLM Enrichment, Optional):** Semantic reconciliation, natural-language spec interpretation, conflict attribution in ambiguous cases

Without LLM: Ideome synthesis produces drift vectors from rule matching and structural comparison. Drift attribution is heuristic-based.

With LLM: Drift attribution is enriched with semantic understanding. "The auth module's structure suggests session-based auth, but the spec says token-based" — this level of semantic reconciliation requires language understanding.

### 8.2 Product FOR AI, Not AI Product

The Ideome output is structured data — drift vectors, regime classifications, declaration lists — designed to be consumed by AI agents (the primary user). The human (final user) sees the Insights Compiler's interpretation. The raw Ideome data feeds the AI partner's understanding of the codebase.

### 8.3 Backward Compatibility

Every integration point degrades gracefully:
- No Contextome Intelligence → Ideome has only universal rules → drift_X is unmeasurable → regime defaults to inference from drift_C alone
- No project spec files → Ω_project is empty → only Ω_universal applies → generic but still functional
- No LLM → deterministic synthesis only → slightly less nuanced attribution → still fully operational

**Zero dependencies gate the analysis.** The Ideome enriches everything, blocks nothing.

---

## 9. The Macro Architecture

### 9.1 Before: Two-Partition Model

```
PROJECTOME
├── CODOME (executable: .py, .js, .go, ...)
│   └── 22 analysis dimensions (Survey → Incoherence)
└── CONTEXTOME (documentation: .md, .rst, .yaml, ...)
    └── 0 analysis dimensions (counted but never read)
```

### 9.2 After: Three-Layer Epistemic Stack

```
PROJECTOME
├── CODOME (what IS)
│   ├── Survey (Stage 0) — filesystem definition
│   ├── Base Analysis (Stage 1) — graph construction
│   ├── Complexity, Coupling, Cohesion (Stages 2-5)
│   ├── Purpose Field (Stage 3.7) — bottom-up emergence
│   ├── Advanced Analysis (Stages 6-11)
│   └── Trinity + Temporal (Stages 11.96-11.97)
│
├── CONTEXTOME (what is SAID)
│   └── Contextome Intelligence (Stage 0.8)
│       ├── Doc Discovery (0.8.1)
│       ├── Structural Purpose Extraction (0.8.2)
│       ├── Symmetry Seeding (0.8.3)
│       ├── Purpose Priors (0.8.4)
│       └── LLM Enrichment (0.8.5-0.8.6, optional)
│
├── IDEOME (what SHOULD BE) ← THE ROSETTA STONE
│   └── Ideome Synthesis (Stage 0.9)
│       ├── Universal Rule Loading (Ω_universal)
│       ├── Project Declaration Extraction (Ω_project)
│       ├── Triangulation (Φ_meta)
│       └── Semantic Reconciliation (LLM, optional)
│
└── COMPOSITION LAYER (cross-correlation engine)
    └── Correlates all dimensions through Constructal resistance model
        ├── R_static  ← Codome structural analysis
        ├── R_change  ← Temporal analysis
        ├── R_human   ← Contextome + Ideome
        └── R_runtime ← (planned)
```

### 9.3 The Full Pipeline (Revised)

```
Stage 0      Survey (Codome Definition Layer)
Stage 0.8    Contextome Intelligence (Contextome Definition Layer)
Stage 0.9    Ideome Synthesis (Specification Layer / Rosetta Stone)
Stage 1      Base Analysis (Graph Construction)
Stage 2      Complexity Analysis
Stage 3      Coupling & Cohesion
Stage 3.7    Purpose Field (seeded by Ideome priors)
Stage 4-5    Dependency & Pattern Analysis
Stage 6-10   Advanced Analysis (Security, Performance, etc.)
Stage 11     Synthesis Pass
Stage 11.96  Trinity (Incoherence, Purpose Decomposition, Gap Detection)
Stage 11.97  Temporal Analysis (REH)
Stage 11.98  Drift Attribution (Ideome post-analysis)  ← NEW
Stage 11.95  Insights Compilation (with drift-attributed findings)
Stage 12     Final Report Generation
```

Note Stage 11.98 (Drift Attribution): this is the **post-analysis pass** where the Ideome's drift vectors are computed against the fully-built analysis graph. Stage 0.9 establishes the specification surface; Stage 11.98 measures actual drift against it.

---

## 10. Axioms

### Axiom I1: Tripartite Epistemic Completeness

> Every aspect of a software system is capturable by exactly one of: what it IS (Codome), what is SAID about it (Contextome), or what it SHOULD BE (Ideome). There is no fourth epistemic category.

### Axiom I2: Specification Primacy

> When Codome and Contextome disagree, the Ideome is the arbiter. The specification defines truth; implementation and documentation are measured against it.

### Axiom I3: Computed, Not Stored

> The Ideome is a derived quantity, not a stored artifact. It is recomputed on every analysis run from the current state of Codome, Contextome, and the ontological rule set.

### Axiom I4: Deterministic Foundation

> The Ideome synthesis function Φ produces identical outputs given identical inputs. LLM enrichment adds confidence but never changes the deterministic drift vectors — it only enriches attribution metadata.

### Axiom I5: Graceful Degradation

> The Ideome synthesis operates at maximum capability with all three inputs (Codome + Contextome + Ω_project). It degrades to universal-only rules when project-specific declarations are absent. It degrades to pure Codome analysis when Contextome Intelligence is unavailable. It never fails completely.

### Axiom I6: The Fixed-Point (Lawvere)

> The Ideome specification is part of the Contextome of any repository that contains it. When Collider analyzes itself, the Ideome synthesis computes drift between its own code and its own specification. This self-referential property is a consistency check, not a paradox.

### Axiom I7: Attribution Over Measurement

> The Ideome's primary contribution is not measuring incoherence (which existing modules already do) but **attributing** it. "Where" and "how much" are Codome questions. "Who drifted and from what" is an Ideome question.

---

## 11. Theoretical Grounding

### 11.1 Category Theory: The Adjunction

The relationship between the three layers can be modeled as an adjunction in category theory:

- **Codome → Ideome** (implementation → specification): the "specification extraction" functor. Given code, what spec does it satisfy?
- **Ideome → Codome** (specification → implementation): the "implementation check" functor. Given a spec, does the code satisfy it?
- **Contextome → Ideome** (documentation → specification): the "declaration extraction" functor. Given docs, what spec do they describe?

The adjunction F ⊣ G between these functors produces the natural transformation that IS the drift measurement.

### 11.2 Information Theory: Signal-to-Noise

The Ideome resolves a fundamental signal-to-noise problem:

- **Codome signals** are precise but numerous (every line of code is a signal). Low noise, high volume.
- **Contextome signals** are sparse but intentional (every heading is a deliberate declaration). Medium noise, low volume.
- **Ideome signals** are highest confidence because they triangulate. The intersection of two independent signal sources has lower noise than either alone.

The Ideome's purpose coverage metric (from Contextome Intelligence) directly measures signal availability. The drift vectors measure signal disagreement.

### 11.3 Constructal Law: Flow Optimization

The Ideome completes the Constructal 4-flow resistance model:

    R_total = R_static + R_runtime + R_change + R_human

Where R_human is the resistance to **human comprehension** — how hard is it for a human (or AI) to understand what the system does, why, and how it should evolve?

R_human decomposes into:
- **R_doc**: Documentation quality (from Contextome Intelligence)
- **R_spec**: Specification clarity (from Ideome synthesis — how well do the rules explain the system?)
- **R_drift**: Drift magnitude (from Ideome — high drift = high cognitive resistance)

    R_human = R_doc + R_spec + R_drift

The Constructal Law predicts that systems evolve toward configurations that minimize total flow resistance. Collider's job is to measure R_total accurately so that the consuming AI can recommend configurations that reduce it.

---

## 12. Implementation Roadmap

### Phase 1: Ideome Synthesis Core (~400 lines)

**File:** `particle/src/core/ideome_synthesis.py`

- Universal rule loader (reads CONSTRAINT_RULES, Standard Model axioms)
- Project declaration extractor (reads config files, spec files, CI config)
- Stub triangulation engine (entity matching by path and name)
- IdeomeResult, ProjectDeclaration, DriftAnalysis data contracts
- run_ideome_synthesis(codome_data, contextome_data, root_path, llm_adapter=None) → IdeomeResult
- Stage 0.9 integration into full_analysis.py

### Phase 2: Drift Attribution Engine (~300 lines)

**File:** Extension to `ideome_synthesis.py` or new `drift_attribution.py`

- Post-analysis drift computation (Stage 11.98)
- Per-node drift_C, drift_X, Δ_CX calculation
- Regime classification (ALIGNED, CODE_DRIFT, DOC_DRIFT, DUAL_DRIFT, SPEC_STALE)
- Integration with incoherence.py I_sym (replace proxy metrics with attributed drift)
- Insights Compiler pass: _interpret_ideome()

### Phase 3: LLM Semantic Reconciliation (~200 lines)

- Provider-agnostic adapter (reuses LLMAdapter Protocol from Contextome Intelligence)
- Semantic conflict detection prompt
- Attribution enrichment merge
- Confidence adjustment

### Phase 4: Composition Layer Foundation

With Ideome providing R_human and temporal analysis providing R_change, the Composition Layer becomes feasible:
- Cross-correlation engine that overlays Markov chain, constructal resistance, purpose decomposition, and drift attribution
- "Show me where all dimensions agree something is wrong" — the convergence signal
- This is the ultimate frontier

---

## 13. Glossary

| Term | Definition |
|---|---|
| **Ideome** | The computed specification surface; the third epistemic layer of the Projectome; what SHOULD be |
| **Rosetta Stone Computation** | The triangulation of Codome, Contextome, and Ideome to produce drift attribution |
| **drift_C** | Implementation drift: the distance between what the code IS and what the spec says it SHOULD be |
| **drift_X** | Documentation drift: the distance between what the docs SAY and what the spec says it SHOULD be |
| **Δ_CX** | Symmetry gap: the distance between what the code IS and what the docs SAY |
| **Regime** | One of ALIGNED, CODE_DRIFT, DOC_DRIFT, DUAL_DRIFT, SPEC_STALE — the diagnostic classification of a drift pattern |
| **Ω_universal** | Universal ontological rules (Standard Model axioms, CONSTRAINT_RULES, atom taxonomy) |
| **Ω_project** | Project-specific declarations extracted from specs, config, CI, tests |
| **Φ** | The Ideome synthesis function: Φ(C, X, Ω) → I |
| **Φ_meta** | The meta-inference component of Φ — the triangulation computation itself |
| **R_human** | Human comprehension resistance in the Constructal 4-flow model; decomposed into R_doc + R_spec + R_drift |

---

## 14. Open Questions

1. **Ideome persistence:** Should IdeomeResult be cached between runs for temporal drift tracking? (Currently ephemeral per Axiom I3, but temporal comparison of drift vectors across commits would be valuable.)

2. **Spec conflict resolution:** When Ω_universal and Ω_project conflict (e.g., project spec says "no tests needed" but Ω_universal says "all modules MUST have tests"), which takes priority? Current proposal: Ω_project wins for project-specific structural declarations; Ω_universal wins for universal invariants.

3. **Confidence calibration:** How should drift_C, drift_X, and Δ_CX be scaled to the 0-1 range given that they are computed from heterogeneous signals (structural matching, keyword overlap, semantic similarity)?

4. **Multi-language Ideome:** For polyglot repositories, should the Ideome synthesize per-language sub-specifications, or one unified specification?

5. **Evolution tracking:** Should the Ideome capture the direction of drift (toward or away from the spec over time), not just the magnitude? This would require temporal Ideome comparisons.

---

## Appendix A: The Rosetta Stone — Extended Analogy

The Rosetta Stone was discovered in 1799 near the town of Rashid (Rosetta) in Egypt. It bore three scripts: hieroglyphic (priestly, formal), Demotic (common Egyptian, practical), and Greek (understood by scholars). The stone enabled Jean-François Champollion to decode hieroglyphics in 1822 by using the Greek as a reference frame.

Key properties of the analogy:

1. **The Greek wasn't better — it was known.** The Ideome isn't "better" than the Codome or Contextome. It's the layer we **trust** because it's derived from explicit specification.

2. **Decoding required all three scripts.** Understanding the code requires the Codome (structural analysis), the Contextome (declared intent), AND the Ideome (specification). Any two gives partial understanding. All three gives full comprehension.

3. **The stone was a single artifact.** The three scripts were inscribed on the same stone — they described the same decree. The Projectome is a single system — Codome, Contextome, and Ideome describe the same software from different epistemological vantage points.

4. **Translation, not replacement.** Champollion didn't replace hieroglyphics with Greek. He used Greek to understand hieroglyphics. The Ideome doesn't replace code analysis with specification checking. It uses specification to understand what code analysis reveals.

---

*This specification defines the theoretical foundation for the Ideome as Collider's core macro structure. Implementation follows the deterministic-first, LLM-amplified philosophy established in the Contextome Intelligence module. The Rosetta Stone Computation is the bridge that makes Collider's 25+ analysis dimensions mutually interpretable.*
