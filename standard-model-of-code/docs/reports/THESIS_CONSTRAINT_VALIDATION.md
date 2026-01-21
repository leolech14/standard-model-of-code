# Thesis: The Constraint Field

> Completing the Standard Model v5 with a formal validity layer.

**Date:** 2026-01-20
**Version:** 3.0 (revised after second critique)
**Status:** PROPOSAL
**Authors:** Claude Opus 4.5, Gemini 2.5 Pro
**Critiques:** Gemini 2.5 Pro (model upgrade), ChatGPT (profile + antimatter precision)

---

## Executive Summary

The Standard Model of Code v5 has two pillars:
- **Structure** (200 Atoms) - what code IS
- **Purpose** (33 Roles) - what code DOES

This thesis proposes a third pillar:
- **Validity** (Constraint Field) - what combinations are POSSIBLE

**Central Claim:** v4 contained a constraint corpus; v5 needs a formal Constraint Field. The 1440 grid is seed evidence, not the final form.

**Key v3.0 Changes:**
- Profiles (architecture + dimension semantics) as first-class concept
- Antimatter = Tier A only (precise definition)
- Stratified validity (axioms vs invariants vs signals)
- Governance policy for rule sprawl prevention

---

## Part 1: The Theory Change

### 1.1 The Missing Pillar

v5 achieved orthogonality by separating Atoms from Roles. But it lacks a formal notion of **forbidden states**.

| Pillar | v5 Current | Purpose |
|--------|------------|---------|
| Structure | 200 Atoms (D1) | What it IS |
| Purpose | 33 Roles (D3) | What it DOES |
| **Validity** | **Missing** | What is POSSIBLE |

Without validity, the model can classify code into states that are semantically impossible.

### 1.2 Formal Definition: The Constraint Field

Let a node have semantic coordinates:
```
x(node) = (atom, role, d1..d8, layer, ...context)
```

Let constraints be predicates:
```
c_i(x) → {pass | violate}
```

**Stratified validity:**
```
valid_axioms(node)     = ∀i ∈ TierA, ¬c_i(x(node))
valid_invariants(node) = ∀i ∈ TierB, ¬c_i(x(node))
valid(node)            = valid_axioms(node) ∧ valid_invariants(node)
```

**The π₁ equation becomes:**
```
π₁(node) = role(node)                         # Purpose assignment
π₁*(node) = role(node) | valid_axioms(node)   # Meaningful purpose
```

A node's purpose is only meaningful if it does not violate model axioms.

### 1.3 Antimatter: Precise Definition

**Antimatter = Tier A violations only.**

```
antimatter(node) = ∃i ∈ TierA, c_i(x(node)) = violate
```

Do NOT dilute this term. Tier B violations are "policy violations." Tier C outputs are "signals."

**Derived metrics:**
```
ρ_antimatter = |{n : antimatter(n)}| / |N|           # Tier A only
ρ_policy     = |{n : ∃ TierB violation}| / |N|       # Tier B
ρ_signal     = Σ(confidence_weighted Tier C) / |N|   # Tier C, weighted
```

---

## Part 2: Profiles (New in v3.0)

### 2.1 Why Profiles Are Required

Without profiles, the strongest invariants become ideological arguments instead of engineering outcomes.

Two profile types are required:
1. **Architecture Profile** - layer direction, dependency rules
2. **Dimension Semantics Profile** - what purity/effect/lifecycle mean

### 2.2 Architecture Profiles

| Profile | Layer Order | Dependency Direction | Use Case |
|---------|-------------|---------------------|----------|
| `classic_layered` | Presentation → Application → Domain → Infrastructure | Higher layers depend on lower | Traditional N-tier |
| `clean_onion` | Infrastructure → Application → Presentation → Domain (core) | Outer depends on inner, Domain is innermost | Clean Architecture, Hexagonal |
| `custom` | User-defined | User-defined | Framework-specific |

**Profile schema:**
```yaml
# schema/profiles/architecture/classic_layered.yaml
id: classic_layered
name: "Classic Layered Architecture"
layer_order:
  - { name: Presentation, order: 0, position: outer }
  - { name: Application, order: 1, position: middle }
  - { name: Domain, order: 2, position: middle }
  - { name: Infrastructure, order: 3, position: inner }
dependency_rule: "outer_depends_on_inner"
# Allowed: Presentation → Application → Domain → Infrastructure
# Forbidden: Infrastructure → Domain (inner cannot depend on outer)
```

```yaml
# schema/profiles/architecture/clean_onion.yaml
id: clean_onion
name: "Clean/Onion Architecture"
layer_order:
  - { name: Infrastructure, order: 0, position: outer }
  - { name: Presentation, order: 1, position: outer }
  - { name: Application, order: 2, position: middle }
  - { name: Domain, order: 3, position: inner_core }
dependency_rule: "outer_depends_on_inner"
# Allowed: Infrastructure → Domain (via interfaces), Presentation → Application → Domain
# Forbidden: Domain → Infrastructure (core cannot depend on outer)
```

### 2.3 Dimension Semantics Profiles

Tier A axioms are only portable if dimension semantics are canonical.

| Profile | Purity Definition | Effect Definition |
|---------|-------------------|-------------------|
| `fp_strict` | No I/O + deterministic + no mutation | Any observable state change |
| `oop_conventional` | No observable side effects (logging may be OK) | State change visible to callers |
| `effect_typed` | Expressed via effect types; classification maps to them | Type-system enforced |

**Profile schema:**
```yaml
# schema/profiles/dimensions/fp_strict.yaml
id: fp_strict
name: "Functional Programming Strict"
dimensions:
  purity:
    pure: "No I/O, deterministic, no mutation, no exceptions"
    impure: "Any of the above present"
  effect:
    none: "No observable state change"
    local: "Mutates only local/owned state"
    external: "Mutates shared/external state"
    io: "Performs I/O operations"
axiom_applicability:
  AXIOM-001: true  # Pure cannot I/O
  AXIOM-002: true  # Immutable cannot mutate
```

### 2.4 Profile Selection

```yaml
# .collider/config.yaml
profiles:
  architecture: clean_onion
  dimensions: fp_strict
```

**Invariants become profile-dependent:**
```yaml
- id: INVARIANT-001
  tier: B
  scope: edge
  description: "Layer dependency violation"
  match:
    violates_profile_dependency_rule: true
  applies_to_profiles: [classic_layered, clean_onion]
  # The actual check depends on active profile
```

---

## Part 3: Constraint Taxonomy

### 3.1 Three Tiers (Stratified)

| Tier | Name | Nature | Default Behavior | Affects Validity |
|------|------|--------|------------------|------------------|
| **A** | Axioms | Model-defining impossibles | Error, requires explicit override | `valid_axioms` |
| **B** | Invariants | Architecture style policies | High severity, profile-configurable | `valid_invariants` |
| **C** | Heuristics | Signals / smells | Warning + confidence score | Does NOT affect validity |

### 3.2 Tier A: Axioms (Antimatter Sources)

Violations mean "your classification OR your code contradicts the model itself."

| Axiom ID | Dimension Conflict | Why Impossible | Profile Dependency |
|----------|-------------------|----------------|-------------------|
| AXIOM-001 | `purity=Pure` + does I/O | Pure functions cannot have side effects | Requires `fp_strict` or `oop_conventional` |
| AXIOM-002 | `lifecycle=Immutable` + mutates | Immutable state cannot change | Universal |
| AXIOM-003 | `role=Getter` + writes data | Getters retrieve, they don't mutate | Universal |

**Tier A must remain small and stable.** Adding to Tier A requires:
- Version bump
- Migration note
- Proof that it's truly axiomatic (not style preference)

### 3.3 Tier B: Invariants (Policy Violations)

Profile-dependent architecture rules.

| Invariant ID | Description | Profile |
|--------------|-------------|---------|
| INVARIANT-001 | Layer dependency violation | All (interpreted per profile) |
| INVARIANT-002 | Repository must be Singleton/Scoped | DI-aware profiles |
| INVARIANT-003 | Controller should not contain business logic | MVC profiles |

### 3.4 Tier C: Heuristics (Signals)

Informative, probabilistic. **Does not affect validity.**

| Heuristic ID | Description | Confidence |
|--------------|-------------|------------|
| HEURISTIC-001 | Getter with side effects | 0.7 |
| HEURISTIC-002 | Ephemeral repository | 0.5 |
| HEURISTIC-003 | God class (R-score > 7) | 0.85 |

---

## Part 4: Constraint Scope

### 4.1 Three Scopes

| Scope | What It Validates | Example |
|-------|-------------------|---------|
| **Node** | Single node's dimensions | Immutable + Mutator role |
| **Edge** | Relationship between two nodes | Domain imports Infrastructure |
| **Path** | Transitive closure | A → B → C violates layer flow |

### 4.2 Edge Semantics

**What does "depends on" mean?**

| Edge Type | Meaning | Detection |
|-----------|---------|-----------|
| `import` | Static reference at compile time | Import analysis |
| `implements` | Interface implementation | Type hierarchy |
| `calls` | Runtime invocation | Call graph |
| `instantiates` | Creates instance of | Constructor calls |

Constraints should specify which edge types they apply to:
```yaml
- id: INVARIANT-001
  scope: edge
  edge_types: [import, instantiates]  # Not just "calls"
  match:
    violates_profile_dependency_rule: true
```

### 4.3 Path Constraints (Bounded)

Path constraints can explode computationally. Bound them:
```yaml
- id: PATH-001
  scope: path
  max_depth: 3  # Limit traversal
  description: "Transitive layer violation"
```

---

## Part 5: Output Schema (Stratified)

### 5.1 Node-Level Output

```json
{
  "id": "UserService.updateEmail",
  "atom": "LOG.FNC.M",
  "role": "Mutator",
  "dimensions": {
    "purity": "Impure",
    "boundary": "Domain",
    "lifecycle": "Scoped"
  },
  "layer": "Domain",
  "constraint_field": {
    "valid_axioms": true,
    "valid_invariants": false,
    "antimatter": false,
    "violations": [
      {
        "rule_id": "INVARIANT-001",
        "tier": "B",
        "severity": "High",
        "message": "Domain layer depends on Infrastructure (profile: clean_onion)",
        "fix": ["Inject via port/adapter pattern"]
      }
    ],
    "signals": [
      {
        "rule_id": "HEURISTIC-003",
        "tier": "C",
        "confidence": 0.85,
        "message": "High responsibility score (R=8)"
      }
    ]
  }
}
```

### 5.2 Aggregate Metrics

```json
{
  "constraint_field_summary": {
    "profile": {
      "architecture": "clean_onion",
      "dimensions": "fp_strict"
    },
    "total_nodes": 1463,
    "antimatter_nodes": 3,
    "antimatter_density": 0.002,
    "policy_violation_nodes": 44,
    "policy_density": 0.030,
    "signal_density_weighted": 0.15,
    "by_tier": {
      "A": 3,
      "B": 44,
      "C": 127
    },
    "by_scope": {
      "node": 28,
      "edge": 15,
      "path": 4
    }
  }
}
```

---

## Part 6: Reconciliation Loop (Constrained)

### 6.1 Principles

1. **Constraints produce hypotheses, not auto-corrections**
2. **The classifier remains the source of truth**
3. **No automatic relabeling unless explicitly enabled**
4. **No iterative loops by default**

Reconciliation = "what to inspect next," not "self-modifying truth."

### 6.2 Hypothesis Output

```json
{
  "rule_id": "AXIOM-001",
  "violation_kind": "code_smell",
  "alternative_hypotheses": [
    {
      "type": "misclassification",
      "field": "purity",
      "suggested": "Impure",
      "confidence": 0.7,
      "reason": "Detected I/O call may indicate impurity"
    },
    {
      "type": "incomplete_analysis",
      "reason": "Call graph may be incomplete"
    }
  ],
  "action": "inspect"  # NOT "auto_relabel"
}
```

---

## Part 7: Suppression and Adoption

### 7.1 Suppression Mechanisms

| Mechanism | Purpose | Example |
|-----------|---------|---------|
| `allow_if` conditions | Contextual exceptions | "OK in test code" |
| Project suppression file | Team policy | `.collider/suppressions.yaml` |
| Inline suppressions | Developer override | `# collider:ignore AXIOM-001` |
| Baseline | Grandfather existing | "Only fail on new violations" |

### 7.2 Suppression Schema

```yaml
# .collider/suppressions.yaml
version: "1.0.0"
suppressions:
  - rule_id: INVARIANT-003
    scope: file
    pattern: "**/tests/**"
    reason: "Test files are allowed to violate layer rules"

  - rule_id: AXIOM-001
    scope: node
    node_pattern: "LegacyService.*"
    reason: "Legacy code, scheduled for refactor Q2"
    expires: "2026-06-01"
```

### 7.3 Suppression Debt Metric

Track suppression health:
```json
{
  "suppression_debt": {
    "total_suppressions": 23,
    "expired": 2,
    "expiring_soon": 5,
    "tier_a_suppressions": 1,  # Red flag
    "permanent_suppressions": 8
  }
}
```

---

## Part 8: Governance (New in v3.0)

### 8.1 Rule Addition Requirements

| Requirement | Purpose |
|-------------|---------|
| Rationale | Why this rule exists |
| Examples | At least 2 real-world cases |
| False-positive risk | Expected noise level |
| Tier justification | Why A vs B vs C |
| Profile applicability | Which profiles it applies to |

### 8.2 Tier A Changes

Tier A is the model's axiomatic core. Changes require:
- **Version bump** (e.g., v5.1 → v5.2)
- **Migration note** for existing users
- **Proof** that it's truly axiomatic (not style preference)
- **Review** by model maintainers

### 8.3 Deprecation Policy

```yaml
- id: RULE-XXX
  status: deprecated
  deprecated_since: "2026-03-01"
  removal_date: "2026-09-01"
  replacement: RULE-YYY
  migration_guide: "docs/migrations/XXX-to-YYY.md"
```

### 8.4 Rule Sprawl Prevention

**Hard limits:**
- Tier A: Maximum 20 rules (axiomatic core must stay small)
- Tier B: No hard limit, but requires profile association
- Tier C: No hard limit, but requires confidence score

**Review triggers:**
- Adding 5th+ rule in a category requires architecture review
- Any rule with >30% suppression rate requires re-evaluation

---

## Part 9: Pipeline Integration

### 9.1 Stage 8.5: Constraint Field

```
Stage 7:   Standard Model Enrichment (Atoms + Dimensions)
Stage 8:   Purpose Field (Roles + Layer dynamics)
Stage 8.5: Constraint Field (Validity + Antimatter)  ← NEW
Stage 9:   Execution Flow
Stage 10:  Markov + Knots
Stage 11:  Topology + Semantics
Stage 12:  Output Generation
```

### 9.2 Implementation Components

| Component | Path | Purpose |
|-----------|------|---------|
| Profile Loader | `src/core/profile_loader.py` | Load architecture + dimension profiles |
| Rule Schema | `schema/constraints/rules.yaml` | Declarative constraint definitions |
| Constraint Engine | `src/core/constraint_field.py` | Rule engine + reconciliation |
| Suppression Loader | `src/core/constraint_suppressions.py` | Load project overrides |

---

## Part 10: Implementation Checklist

### Phase 1: Foundation (2 days)
- [ ] Create `schema/profiles/architecture/` with classic_layered.yaml, clean_onion.yaml
- [ ] Create `schema/profiles/dimensions/` with fp_strict.yaml, oop_conventional.yaml
- [ ] Create `schema/constraints/taxonomy.yaml` with Tier A/B/C definitions
- [ ] Create `schema/constraints/rules.yaml` with 5 seed rules

### Phase 2: Extraction (1 day)
- [ ] Parse `archive/data/1440_csv.csv`
- [ ] Cluster 81 impossibles by reason and dimension pattern
- [ ] Classify into Tier A (≤10), Tier B, Tier C
- [ ] Generate rules.yaml entries with evidence links

### Phase 3: Engine (2 days)
- [ ] Create `src/core/profile_loader.py`
- [ ] Create `src/core/constraint_field.py`
- [ ] Implement node, edge, path validators (path bounded to depth 3)
- [ ] Integrate as Stage 8.5 in full_analysis.py

### Phase 4: Adoption (1 day)
- [ ] Create suppression mechanism
- [ ] Add baseline support
- [ ] Add stratified output schema
- [ ] Add visualization in HTML report

### Phase 5: Documentation (1 day)
- [ ] Update MODEL.md with Constraint Field theory
- [ ] Add CONSTRAINT_FIELD.md detailed spec
- [ ] Add PROFILES.md explaining architecture + dimension profiles
- [ ] Add governance docs

---

## Part 11: Canonical Model Changes

### 11.1 Additions to MODEL.md

```markdown
## The Constraint Field

The third pillar of the Standard Model, defining semantic feasibility.

### Definition
- Constraints are predicates over semantic coordinates
- Validity is stratified:
  - valid_axioms: no Tier A violations
  - valid_invariants: no Tier B violations (under active profile)
- Antimatter: nodes with Tier A violations ONLY

### Profiles
- Architecture profiles define layer semantics and dependency direction
- Dimension profiles define what purity/effect/lifecycle mean
- Tier A axioms may be profile-dependent

### Constraint Taxonomy
- Tier A (Axioms): Model-defining impossibles → antimatter
- Tier B (Invariants): Architecture policies → policy violations
- Tier C (Heuristics): Signals with confidence → does not affect validity

### Governance
- Tier A maximum 20 rules
- Tier A changes require version bump + migration
- Rules require rationale, examples, false-positive risk
```

---

## Conclusion

The Constraint Field is the **third pillar** of the Standard Model:

| Pillar | Question | Answer |
|--------|----------|--------|
| Structure (Atoms) | What IS it? | Syntactic category |
| Purpose (Roles) | What DOES it? | Semantic intent |
| **Validity (Constraints)** | Is it POSSIBLE? | Dimensional consistency |

**v3.0 Key Decisions:**

| Decision | Rationale |
|----------|-----------|
| Profiles are first-class | Prevents ideological arguments about layer direction |
| Antimatter = Tier A only | Keeps the term meaningful |
| Tier C doesn't affect validity | Signals are informative, not judgmental |
| Governance limits Tier A to 20 | Prevents rule sprawl |
| Reconciliation = hypotheses only | Classifier remains source of truth |

**Recommendation:** Implement the Constraint Field with profiles and stratified validity as a first-class piece of Standard Model v5.

---

## References

| Document | Path | Relevance |
|----------|------|-----------|
| v4 1440 Grid | `archive/data/1440_csv.csv` | Seed evidence |
| v4 RPBL Docs | `archive/docs/STANDARD-MODEL-1440-RPBL.md` | Historical context |
| v5 Model | `standard-model-of-code/docs/MODEL.md` | Current theory |
| v5 Atoms | `schema/fixed/200_ATOMS.md` | Structure pillar |
| v5 Roles | `schema/fixed/roles.json` | Purpose pillar |
| Purpose Field | `src/core/purpose_field.py` | Current partial validation |

---

*Thesis v3.0: Revised after second critique (ChatGPT)*
*Key additions: Profiles, precise antimatter definition, stratified validity, governance*
