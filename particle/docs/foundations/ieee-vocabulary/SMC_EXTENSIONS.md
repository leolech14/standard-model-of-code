# SMC Extensions to IEEE Vocabulary

> **Principle:** SMC extends IEEE SEVOCAB. It does not replace it.
> **Rule:** If IEEE has a term, USE IT. Only create new terms when IEEE lacks the concept.

---

## Extension Categories

### 1. UNIVERSE PARTITIONING (3 terms)

IEEE lacks formal partition of project contents.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **PROJECTOME** | Complete set of all files in project | IEEE has "project" but not the -ome partition concept |
| **CODOME** | All executable code (P ∩ executable) | IEEE has "source code" but not as formal set |
| **CONTEXTOME** | All non-executable content (P \ CODOME) | IEEE has "documentation" but not as complement to code |

**IEEE foundation:** Uses IEEE "project", "source code", "documentation"

---

### 2. COORDINATE SYSTEM (5 terms)

IEEE lacks formal location system for code entities.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **LOCUS** | 5-tuple coordinate ⟨λ, Ω, τ, α, R⟩ | No IEEE equivalent - novel formalization |
| **Ring (Ω)** | Dependency depth (R0-R4) | IEEE has "layer" but not formalized rings |
| **Tier (τ)** | Abstraction level | IEEE has "tier" but different meaning |
| **RPBL** | Character metrics tuple | No IEEE equivalent |
| **Level (λ)** | Scale from L-3 to L12 | IEEE has "level" but not 16-tier scale |

**IEEE foundation:** Builds on IEEE "layer", "level", "architecture"

---

### 3. QUANTUM METAPHOR (4 terms)

IEEE uses industrial metaphor. SMC uses physics metaphor.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **PARTICLE** | Implementation realm (collapsed state) | Novel framing - IEEE is paradigm-neutral |
| **WAVE** | Planning realm (superposition) | Novel framing |
| **OBSERVER** | Decision layer | IEEE has "stakeholder" but not quantum framing |
| **Holon** | Janus-faced entity (whole AND part) | From Koestler - not in IEEE |

**IEEE foundation:** Relates to IEEE "stakeholder", "implementation"

---

### 4. ROLES (33 terms → 17 SMC-specific)

IEEE has patterns and roles. SMC formalizes 33 canonical roles.

**IEEE-aligned (16):** Query, Command, Factory, Repository, Service, Controller, Manager, Handler, Utility, Parser, Loader, Store, Cache, Transformer, Builder, Emitter

**SMC-specific (17):**
| SMC Role | Definition | Why Not IEEE |
|----------|------------|--------------|
| **Validator** | Input/output validation | IEEE has "validation" (noun) not "Validator" (role) |
| **Guard** | Access control enforcer | IEEE has "access control" not "Guard" role |
| **Orchestrator** | Multi-service coordinator | IEEE has "orchestration" not as role |
| **Mapper** | Object-to-object transformation | IEEE lacks this specific role |
| **Serializer** | Data encoding | IEEE has "serialization" not role |
| **Finder** | Search/lookup function | Not in IEEE |
| **Getter** | Property accessor | Not in IEEE |
| **Mutator** | State modifier | Not in IEEE |
| **Creator** | Object instantiation | IEEE has "creation" not role |
| **Destroyer** | Cleanup/disposal | Not in IEEE |
| **Listener** | Event receiver | Not in IEEE as role |
| **Subscriber** | Pub/sub subscriber | Not in IEEE as role |
| **Helper** | Support function | Not in IEEE |
| **Formatter** | Output formatting | Not in IEEE as role |
| **Asserter** | Condition assertion | Not in IEEE |
| **Lifecycle** | Init/cleanup phase | IEEE has "lifecycle" (noun) not role |
| **Internal** | Private implementation | Not in IEEE as role |

**IEEE foundation:** Extends IEEE "design pattern", "role"

---

### 5. SYMMETRY STATES (5 terms)

IEEE lacks code-docs alignment tracking.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **SYMMETRIC** | Code, docs, memory aligned | Novel state |
| **ORPHAN** | Code without docs | IEEE has "orphan" (different meaning) |
| **PHANTOM** | Docs without implementation | Novel state |
| **DRIFT** | Code and docs disagree | IEEE has "drift" (different context) |
| **AMNESIAC** | AI-assisted memory loss | Novel (AI-era concept) |

**IEEE foundation:** Extends IEEE "traceability", "documentation"

---

### 6. PURPOSE FORMALIZATION (5 terms)

IEEE lacks teleological formalization.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **Purpose Field** | Vector field 𝒫: N → ℝᵏ | Novel mathematical formalization |
| **Purpose Drift** | Δ𝒫 = 𝒫_human - 𝒫_code | Novel metric |
| **Dynamic Purpose** | Human intent (flowing) | Novel concept |
| **Crystallized Purpose** | Code intent (frozen) | Novel concept |
| **Emergence Signal** | New layer detection | Novel concept |

**IEEE foundation:** Extends IEEE "requirement", "intent"

---

### 7. AI CONSUMER CLASS (4 terms)

IEEE lacks AI-as-consumer concepts (written pre-AI era).

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **AI_AGENT** | AI as first-class consumer | Not in IEEE (too new) |
| **Stone Tool** | AI-native tool | Novel concept |
| **TOOLOME** | Tool taxonomy | Novel -ome extension |
| **END_USER** | Final human consumer | IEEE has "end user" but different framing |

**IEEE foundation:** Extends IEEE "user", "tool"

---

### 8. CONCORDANCE (2 terms)

IEEE lacks purpose-region formalization.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **CONCORDANCE** | Purpose-aligned region | Novel concept |
| **Alignment Score (κ)** | Quantified purpose alignment [0,1] | Novel metric |

**IEEE foundation:** Relates to IEEE "traceability", "requirement"

---

### 9. CONFIDENCE FRAMEWORK (4 terms)

IEEE has "confidence" but SMC adds 4D model.

| SMC Term | Definition | Why Not IEEE |
|----------|------------|--------------|
| **4D Confidence** | min(Factual, Alignment, Current, Onwards) | Novel framework |
| **Factual** | Evidence-based truth | Novel dimension |
| **Current** | Temporal freshness | Novel dimension |
| **Onwards** | Future-enabling quality | Novel dimension |

**IEEE foundation:** Extends IEEE "confidence level", "quality"

---

## Summary

| Category | IEEE Terms Used | SMC Extensions |
|----------|-----------------|----------------|
| Universe | project, source code, documentation | 3 (PROJECTOME, CODOME, CONTEXTOME) |
| Coordinates | layer, level, architecture | 5 (LOCUS, Ring, Tier, RPBL, Level) |
| Metaphor | stakeholder, implementation | 4 (PARTICLE, WAVE, OBSERVER, Holon) |
| Roles | 16 pattern roles | 17 additional roles |
| Symmetry | traceability, documentation | 5 states |
| Purpose | requirement, intent | 5 formalizations |
| AI | user, tool | 4 AI concepts |
| Concordance | traceability | 2 concepts |
| Confidence | confidence level | 4 dimensions |

**Total SMC extensions: ~49 terms** built on IEEE foundation of 5,401 terms.

---

## The Relationship

```
IEEE SEVOCAB (5,401 terms)
    │
    ├── SMC USES directly (45 terms)
    │   module, service, repository, validation, architecture...
    │
    ├── SMC EXTENDS (13 terms)
    │   validation → Validator (role)
    │   layer → Ring (formalized)
    │   confidence → 4D Confidence
    │
    └── SMC ADDS (49 terms)
        LOCUS, CODOME, Purpose Field, AI_AGENT...
```

**Compliance rule:** Every SMC document must:
1. Use IEEE terms where available
2. Clearly mark extensions with CAPS or explicit note
3. Justify why IEEE term doesn't suffice

---

*SMC is an extension layer, not a replacement vocabulary.*
