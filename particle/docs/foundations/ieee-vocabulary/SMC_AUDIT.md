# SMC Extension Audit

> **Question:** Is each SMC term truly novel, or does IEEE already have this concept?
> **Method:** Direct lookup in IEEE SEVOCAB (5,401 terms)

---

## Classification

| Category | Description | Action |
|----------|-------------|--------|
| **TRULY NOVEL** | IEEE has no equivalent concept | Keep as SMC extension |
| **ROLE FROM NOUN** | IEEE has noun, SMC adds role | Keep - roles are valid extensions |
| **REDUNDANT** | IEEE has same concept | REMOVE from SMC, use IEEE term |
| **EXTENDED** | IEEE has basic, SMC formalizes | Keep with citation |

---

## Audit Results

### TRULY NOVEL (IEEE has nothing similar)

These concepts do not exist in IEEE SEVOCAB:

| SMC Term | SMC Definition | IEEE Check | Status |
|----------|----------------|------------|--------|
| **PROJECTOME** | Complete file set partition | No "projectome" or partition concept | NOVEL |
| **CODOME** | Executable code partition | No formal code/non-code partition | NOVEL |
| **CONTEXTOME** | Non-executable partition | No formal complement to code | NOVEL |
| **LOCUS** | 5-tuple coordinate ⟨λ,Ω,τ,α,R⟩ | No location coordinate system | NOVEL |
| **RPBL** | Responsibility/Purity/Boundary/Lifecycle | No such 4-axis metric | NOVEL |
| **Ring (Ω)** | R0-R4 dependency depth | IEEE has "layer" but not formalized rings | NOVEL |
| **PARTICLE** | Implementation realm (physics metaphor) | No quantum metaphor | NOVEL |
| **WAVE** | Planning realm (physics metaphor) | No quantum metaphor | NOVEL |
| **OBSERVER** | Decision layer (quantum framing) | IEEE has "stakeholder" but different | NOVEL |
| **Holon** | Janus-faced entity | Not in IEEE | NOVEL |
| **SYMMETRIC** | Code-docs-memory aligned state | No alignment state concept | NOVEL |
| **PHANTOM** | Docs without implementation | Not in IEEE | NOVEL |
| **AMNESIAC** | AI-assisted memory loss | Not in IEEE (too new) | NOVEL |
| **Purpose Field** | Vector field 𝒫 over nodes | No teleological formalization | NOVEL |
| **Purpose Drift** | Δ𝒫 gap measure | IEEE "drift" = ML model drift (different) | NOVEL |
| **CONCORDANCE** | Purpose-aligned region | Not in IEEE | NOVEL |
| **4D Confidence** | Factual×Alignment×Current×Onwards | IEEE has no "confidence" term | NOVEL |
| **Stone Tool** | AI-native tool humans can't use | Not in IEEE | NOVEL |
| **TOOLOME** | Tool taxonomy (-ome) | Not in IEEE | NOVEL |
| **AI_AGENT** | AI as consumer class | IEEE "agent" = delegated object (different) | NOVEL |

**Count: 20 truly novel concepts**

---

### ROLE FROM NOUN (Valid SMC extensions)

IEEE has the **process/concept as noun**. SMC adds the **role** (entity that performs it).

| SMC Role | IEEE Noun | IEEE Definition | SMC Adds |
|----------|-----------|-----------------|----------|
| **Validator** | validation | "confirmation through objective evidence..." | Role that performs validation |
| **Mapper** | mapping | "assigned correspondence between two things..." | Role that performs mapping |
| **Factory** | factory | "object that creates other objects..." | ✓ IEEE has as object, SMC has as role |
| **Utility** | utility | "software tool for frequent tasks..." | ✓ IEEE has as tool, SMC has as role |

**These are VALID extensions** - IEEE defines the concept, SMC defines the role.

| SMC Role | IEEE Has? | Status |
|----------|-----------|--------|
| Validator | validation (noun) | VALID ROLE |
| Guard | — | NOVEL ROLE |
| Orchestrator | — | NOVEL ROLE |
| Mapper | mapping (noun) | VALID ROLE |
| Serializer | — | NOVEL ROLE |
| Finder | — | NOVEL ROLE |
| Getter | — | NOVEL ROLE |
| Mutator | — | NOVEL ROLE |
| Creator | — | NOVEL ROLE |
| Destroyer | — | NOVEL ROLE |
| Listener | — | NOVEL ROLE |
| Subscriber | — | NOVEL ROLE |
| Helper | — | NOVEL ROLE |
| Formatter | — | NOVEL ROLE |
| Asserter | assertion (noun) | VALID ROLE |
| Lifecycle | — | NOVEL ROLE |
| Internal | — | NOVEL ROLE |

**Count: 17 roles (4 from IEEE nouns, 13 novel)**

---

### EXTENDED (IEEE has basic, SMC formalizes)

| SMC Term | IEEE Term | Relationship |
|----------|-----------|--------------|
| Level (λ) | level | IEEE: "degree of complexity"; SMC: 16-tier scale |
| Tier (τ) | tier | IEEE: no definition; SMC: abstraction layer |
| DRIFT | drift | IEEE: "ML model behavior change"; SMC: code-docs divergence |

**Count: 3 extended concepts**

---

### POTENTIALLY REDUNDANT (Review needed)

| SMC Term | IEEE Term | Question |
|----------|-----------|----------|
| END_USER | end user | Same concept? IEEE: "individual who uses system" |
| DEVELOPER | developer | Same concept? IEEE: "organization performing development" |

**Action:** These might be redundant. Consider using IEEE terms directly.

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| **TRULY NOVEL** | 20 | Keep - unique SMC contributions |
| **NOVEL ROLES** | 13 | Keep - IEEE lacks role concept |
| **ROLE FROM NOUN** | 4 | Keep - valid extension pattern |
| **EXTENDED** | 3 | Keep with IEEE citation |
| **POTENTIALLY REDUNDANT** | 2 | Review - maybe use IEEE |
| **TOTAL SMC EXTENSIONS** | **42** | (not 49 as previously thought) |

---

## Conclusions

### 1. SMC is VALID as an extension layer

- 20 truly novel concepts (LOCUS, CODOME, Purpose Field, etc.)
- 17 role definitions (IEEE has concepts but not roles)
- Only 2 potentially redundant terms

### 2. SMC's unique contribution is ROLES

IEEE defines concepts as nouns (validation, mapping, factory).
SMC defines **entities that perform those concepts** (Validator, Mapper, Factory).

This is a valid extension pattern:
```
IEEE:  "validation" = the process of confirming...
SMC:   "Validator"  = the code entity that performs validation
```

### 3. SMC's truly novel concepts

These don't exist in IEEE at all:
- **Universe partition**: PROJECTOME, CODOME, CONTEXTOME
- **Coordinate system**: LOCUS, RPBL, Ring
- **Quantum metaphor**: PARTICLE, WAVE, OBSERVER
- **Symmetry states**: SYMMETRIC, PHANTOM, AMNESIAC
- **Purpose formalization**: Purpose Field, Purpose Drift
- **AI-native concepts**: Stone Tool, AI_AGENT, TOOLOME

### 4. Recommendations

1. **Use IEEE terms** where exact match exists (end user, developer)
2. **Cite IEEE** when extending (Validator extends "validation")
3. **Keep novel concepts** - they are SMC's unique contribution
4. **Document the relationship** - SMC extends IEEE, doesn't replace it

---

## IEEE Terms SMC Should USE (not redefine)

These IEEE terms should be used directly in SMC:

| IEEE Term | Definition |
|-----------|------------|
| module | program unit that is discrete and identifiable |
| component | entity with discrete structure |
| system | combination of interacting elements |
| architecture | fundamental concepts or properties |
| validation | confirmation through objective evidence |
| verification | confirmation that requirements are fulfilled |
| traceability | discernible association among entities |
| factory | object that creates other objects |
| utility | software tool for frequent tasks |
| agent | active object with delegated responsibility |
| tool | software product for support |

**Rule:** Use these IEEE terms. Don't create SMC synonyms.

---

*Audit completed: 2026-01-31*
*Method: Direct lookup in IEEE SEVOCAB 5,401 terms*
