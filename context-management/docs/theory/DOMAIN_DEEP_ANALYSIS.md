# DOMAIN: Deep Analysis & Complete Definition

> **Status:** SUPERSEDED → See `CONCORDANCES.md`
> **Date:** 2026-01-25
> **Method:** AI-assisted decomposition (Gemini 2.5 Flash) + algebraic verification
> **Outcome:** This analysis led to renaming "Domain" → "Concordance" for ontological precision.
> The term "Concordance" better captures PURPOSE ALIGNMENT measurement.

---

## 1. CANONICAL DEFINITION

**Domain** (n.) — A **vertical slice through both CODOME and CONTEXTOME** that defines a functional area. Every domain has code AND context. A domain is defined by the **relationship** between its code and its documentation.

```
Domain ≠ Container
Domain = Cross-Cut
Domain = Relationship(Code, Docs)
```

---

## 2. DOMAIN ALGEBRA

### 2.1 Set-Theoretic Definition

```
D = {D₁, D₂, ..., Dₘ}           Set of all domains

⋃ᵢ Dᵢ = P                       Coverage (all files covered)
Dᵢ ∩ Dⱼ ≠ ∅ (allowed)          Overlap permitted

∀Dᵢ:
  Dᵢ.code ⊂ C                   Code portion (executable)
  Dᵢ.context ⊂ X                Context portion (non-executable)
  Dᵢ = Dᵢ.code ∪ Dᵢ.context    Domain spans both universes
```

### 2.2 Domain Membership Function

```
μ: P → 𝒫(D)                     File → set of domains it belongs to

|μ(f)| ≥ 1                      Every file in at least one domain
|μ(f)| > 1 possible             File can be in multiple domains
```

### 2.3 Domain vs Partition

| Structure | Formula | Meaning |
|-----------|---------|---------|
| **Partition** | `D₁ ⊔ D₂ ⊔ ... ⊔ Dₘ = P` | Disjoint, no overlap |
| **Cover** | `⋃ Dᵢ = P` | May overlap |

**Domain is a COVER, not a partition.**

Why cover, not partition?
- A file can serve multiple functional concerns
- A utility used by Pipeline AND Research belongs to both
- Partition would force artificial categorization

---

## 3. PROPERTIES OF A DOMAIN

| Property | Type | Description |
|----------|------|-------------|
| **Name** | `string` | Human-readable identifier (e.g., "Pipeline") |
| **D.code** | `Set<File>` | Subset of CODOME |
| **D.context** | `Set<File>` | Subset of CONTEXTOME |
| **Owner** | `Realm \| Subsystem \| Agent` | Responsible entity |
| **Codome Paths** | `List<Glob>` | File patterns for code |
| **Contextome Paths** | `List<Glob>` | File patterns for docs |
| **Symmetry** | `State` | Health of code↔docs relationship |

### 3.1 Symmetry States

```
SYMMETRIC(D) ⟺ |D.code| > 0 ∧ |D.context| > 0 ∧ matches(D.code, D.context)
ORPHAN(D)    ⟺ |D.code| > 0 ∧ |D.context| = 0
PHANTOM(D)   ⟺ |D.code| = 0 ∧ |D.context| > 0
DRIFT(D)     ⟺ |D.code| > 0 ∧ |D.context| > 0 ∧ ¬matches(D.code, D.context)
```

### 3.2 Domain Health Score

```
health(D) = |SYMMETRIC| / (|SYMMETRIC| + |ORPHAN| + |PHANTOM| + |DRIFT|)

Target: health(D) > 0.9 for healthy domain
```

---

## 4. RELATIONSHIP WITH OTHER CONCEPTS

### 4.1 Domain ↔ Realm

| Aspect | Domain | Realm |
|--------|--------|-------|
| **Definition** | Semantic/functional | Physical/directory |
| **Structure** | Cover (overlap OK) | Partition (disjoint) |
| **Basis** | Content (what) | Location (where) |
| **Cross-cut** | Vertical | Horizontal |

```
ALGEBRAIC RELATIONSHIP:

Realms partition P:     P = R_Particle ⊔ R_Wave ⊔ R_Observer
Domains cover P:        P = ⋃ Dᵢ

For domain Dᵢ:
  Dᵢ = (Dᵢ ∩ R_Particle) ∪ (Dᵢ ∩ R_Wave) ∪ (Dᵢ ∩ R_Observer)

Domain can span realms. Realm cannot span domains.
```

### 4.2 Domain ↔ CODOME/CONTEXTOME

```
∀D ∈ Domains:
  D.code ⊂ CODOME
  D.context ⊂ CONTEXTOME
  D ⊄ CODOME              (Domain is NOT only code)
  D ⊄ CONTEXTOME          (Domain is NOT only docs)

A Domain MUST span both universes (except Theory which is CONTEXTOME_ONLY).
```

### 4.3 Can a Domain Cross Realm Boundaries?

**YES.** A domain is semantic, not physical.

Example: "Core Protocol Integration" Domain (hypothetical):
- From Particle: `standard-model-of-code/src/core/full_analysis.py`
- From Wave: `context-management/tools/ai/aci/tier_orchestrator.py`
- From Observer: `.agent/KERNEL.md`

Current domains happen to be realm-local, but the definition allows cross-realm.

---

## 5. CONTENT vs LOCATION

| Question | Answer | Evidence |
|----------|--------|----------|
| What defines a domain? | **Content** (semantic purpose) | "Pipeline", "Governance" are functional names |
| How is membership determined? | **Location** (file paths) | Glob patterns in DOMAINS.md |

**Domain is CONTENT-DEFINED but LOCATION-IDENTIFIED.**

The semantic purpose (WHAT) dictates existence.
The file paths (WHERE) specify physical manifestation.

---

## 6. COMPARISON WITH SIMILAR CONCEPTS

### 6.1 vs DDD Bounded Context

| Aspect | PROJECT_elements Domain | DDD Bounded Context |
|--------|------------------------|---------------------|
| **Overlap** | Allowed (cover) | Forbidden (partition) |
| **Content** | Code + Docs explicitly | Primarily code/model |
| **Symmetry** | Measured (health score) | Implicit |
| **Translation** | Not formalized | Context Maps required |

### 6.2 vs Software Module

| Aspect | Domain | Module |
|--------|--------|--------|
| **Level** | Higher abstraction | Lower abstraction |
| **Span** | Multiple modules | Single unit |
| **Context** | Includes docs | Code-centric |

### 6.3 vs Feature

| Aspect | Domain | Feature |
|--------|--------|---------|
| **Definition** | Knowledge area | Capability |
| **Health** | Measured symmetry | User satisfaction |
| **Permanence** | Stable | May be removed |

---

## 7. PROPOSED SUB-TYPES

### 7.1 By Function

| Sub-Type | Purpose | Examples | Characteristics |
|----------|---------|----------|-----------------|
| **Foundational** | Core theory, infrastructure | Theory, Schema | High stability, strict invariants |
| **Operational** | Features, business logic | Pipeline, Visualization | Moderate change, correctness focus |
| **Meta-Management** | Self-refinement, intelligence | AI Tools, Governance | High change, 4D confidence |

### 7.2 By Symmetry Requirement

| Sub-Type | Symmetry Target | Validation |
|----------|-----------------|------------|
| **Code-Heavy** | 70%+ | Some undocumented internals OK |
| **Doc-Heavy** | 90%+ | Theory, specs need full alignment |
| **Balanced** | 80%+ | Standard operational domains |

### 7.3 By Realm Distribution

| Sub-Type | Realm Span | Example |
|----------|------------|---------|
| **Realm-Local** | Single realm | Pipeline (Particle only) |
| **Cross-Realm** | Multiple realms | Core Integration (all three) |
| **Realm-Agnostic** | No realm preference | Archive, Research |

---

## 8. CURRENT DOMAIN REGISTRY

| Domain | Owner | Codome Path | Contextome Path | State |
|--------|-------|-------------|-----------------|-------|
| Pipeline | Collider | `smc/src/core/` | `smc/docs/specs/` | SYMMETRIC |
| Visualization | Collider | `smc/src/core/viz/` | `smc/docs/specs/UI*.md` | SYMMETRIC |
| Governance | Observer | `.agent/tools/` | `.agent/registry/`, `.agent/specs/` | SYMMETRIC |
| AI Tools | Wave | `cm/tools/ai/` | `cm/config/` | SYMMETRIC |
| Theory | Human | — | `smc/docs/MODEL.md` | CONTEXTOME_ONLY |
| Archive | Wave | `cm/tools/archive/` | `cm/tools/archive/config.yaml` | SYMMETRIC |
| Research | Wave | `cm/tools/mcp/` | `docs/research/` | SYMMETRIC |

---

## 9. VISUALIZATIONS

### 9.1 Domain as Vertical Slice

```
            │ CODOME              │ CONTEXTOME
            │ (executable)        │ (non-executable)
────────────┼─────────────────────┼──────────────────────────
Pipeline    │ full_analysis.py    │ PIPELINE_STAGES.md
            │ survey.py           │ specs/*.md
────────────┼─────────────────────┼──────────────────────────
Viz         │ modules/*.js        │ UI_SPEC.md
            │ styles.css          │ presets.yaml
────────────┼─────────────────────┼──────────────────────────
Governance  │ task_store.py       │ registry/*.yaml
            │ confidence.py       │ ROADMAP.yaml
────────────┼─────────────────────┼──────────────────────────
AI Tools    │ analyze.py          │ analysis_sets.yaml
            │ aci/*.py            │ prompts.yaml
────────────┼─────────────────────┼──────────────────────────
Theory      │ (N/A)               │ MODEL.md
            │                     │ docs/specs/*.md
```

### 9.2 Domain vs Realm Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                         PROJECTOME                               │
│                                                                  │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│   │   PARTICLE    │  │     WAVE      │  │   OBSERVER    │       │
│   │    Realm      │  │    Realm      │  │    Realm      │       │
│   │               │  │               │  │               │       │
│   │  ┌─────────┐  │  │  ┌─────────┐  │  │  ┌─────────┐  │       │
│   │  │Pipeline │  │  │  │AI Tools │  │  │  │Governan │  │       │
│   │  │ Domain  │  │  │  │ Domain  │  │  │  │ Domain  │  │       │
│   │  └─────────┘  │  │  └─────────┘  │  │  └─────────┘  │       │
│   │  ┌─────────┐  │  │  ┌─────────┐  │  │               │       │
│   │  │  Viz    │  │  │  │Archive  │  │  │               │       │
│   │  │ Domain  │  │  │  │ Domain  │  │  │               │       │
│   │  └─────────┘  │  │  └─────────┘  │  │               │       │
│   │               │  │               │  │               │       │
│   └───────────────┘  └───────────────┘  └───────────────┘       │
│                                                                  │
│   Realms = HORIZONTAL partitions (by location)                   │
│   Domains = VERTICAL slices (by function)                        │
│                                                                  │
│   A domain CAN cross realm boundaries (semantic, not physical)   │
└─────────────────────────────────────────────────────────────────┘
```

### 9.3 Domain Overlap Visualization

```
                    PROJECTOME
        ┌──────────────────────────────────┐
        │                                  │
        │    ┌───────────┐                 │
        │    │ Pipeline  │                 │
        │    │    ┌──────┴─────┐           │
        │    │    │  overlap   │           │
        │    └────┤            │           │
        │         │ Governance │           │
        │         │      ┌─────┴───┐       │
        │         │      │ overlap │       │
        │         └──────┤         │       │
        │                │AI Tools │       │
        │                └─────────┘       │
        │                                  │
        └──────────────────────────────────┘

        Domains MAY overlap (files serve multiple concerns)
```

---

## 10. OPEN QUESTIONS

1. **Should we formalize cross-realm domains?**
   - Current domains are realm-local
   - Definition allows cross-realm
   - Example: "Core Integration" domain

2. **Should domain hierarchy be introduced?**
   - Currently flat list of 7 domains
   - Could have sub-domains (AI Tools → ACI, RAG, Perplexity)
   - Aligns with 16-level scale

3. **Should inter-domain relationships be formalized?**
   - Types: `depends_on`, `integrates_with`, `subsumes`
   - Would create domain graph
   - Could enhance navigation

4. **Should domain maturity be tracked?**
   - Beyond symmetry score
   - Include: age, change frequency, issue count
   - Similar to topic maturity in mind_map_builder

---

## 11. TRACEABILITY

| Reference | Location |
|-----------|----------|
| Canonical definition | `context-management/docs/DOMAINS.md` |
| Algebraic foundation | `context-management/docs/CODESPACE_ALGEBRA.md` |
| Glossary entry | `standard-model-of-code/docs/GLOSSARY.yaml` |
| Boundary analyzer | `context-management/tools/ai/boundary_analyzer.py` |
| This document | `context-management/docs/theory/DOMAIN_DEEP_ANALYSIS.md` |

---

## 12. SUMMARY

**Domain** is:
- A **vertical slice** through CODOME and CONTEXTOME
- Defined by **semantic purpose** (content), identified by **file paths** (location)
- A **cover** (overlaps allowed), not a partition
- Measured by **symmetry** between code and docs
- **Orthogonal** to Realms (can cross realm boundaries)

**Domain is NOT:**
- A directory (that's a Realm)
- A module (that's smaller scope)
- A feature (that's user-facing capability)
- A partition (files can belong to multiple domains)

---

*Created: 2026-01-25*
*Method: AI-assisted analysis with algebraic verification*
*Confidence: HIGH (multiple Gemini queries, cross-referenced with CODESPACE_ALGEBRA.md)*
