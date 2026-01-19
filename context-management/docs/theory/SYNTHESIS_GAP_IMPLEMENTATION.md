# Synthesis Gap Implementation

> **Purpose**: Implement missing components from foundational theories to complete the Standard Model
> **Created**: 2026-01-07
> **Status**: Implementation Roadmap

---

## Gap Summary from Foundational Theories

### Critical Gaps (High Priority) 🔴

| # | Gap | Source Theory | Current Status | Implementation |
|---|-----|---------------|----------------|----------------|
| 1 | **World 2 (Mental/Intent)** | Popper | Not modeled | Add D9_INTENT dimension |
| 2 | **Entropy/Complexity** | Shannon | No metric | Add complexity metrics to metadata |
| 3 | **Layer Violation Detection** | Clean Arch + Dijkstra | Not enforced | Add to Antimatter laws |
| 4 | **Bounded Context** | DDD | Not explicit | Add CONTEXT_BOUNDARY property at L6-L7 |

### Medium Gaps ⚠️

| # | Gap | Source Theory | Implementation |
|---|-----|---------------|----------------|
| 5 | **Coupling Tension** | Koestler | Add cohesion/coupling balance metric |
| 6 | **Matter Facet (Language)** | Ranganathan | Add D10_LANGUAGE dimension or metadata |
| 7 | **Tau Notation** | Ranganathan | Define canonical τ() format |
| 8 | **Aggregate Root** | DDD | Add `is_aggregate_root` property |
| 9 | **Noise/Error Propagation** | Shannon | Enhance TRUST calculation with error paths |

### Low Priority 🔵

| # | Gap | Source Theory | Implementation |
|---|-----|---------------|----------------|
| 10 | **Emergent Properties** | Koestler + Popper | Add `emergent_behavior` detection |
| 11 | **Pathological Holons** | Koestler | Detect God Classes/Anemic Models |
| 12 | **Screaming Architecture** | Clean Arch | Domain alignment score |

---

## Implementation Plan

### Phase 1: Extend Dimensions (D9, D10)

#### D9: INTENT (From Popper's World 2)
```yaml
D9_INTENT:
  description: "The programmer's mental intent - what the code is SUPPOSED to do"
  values:
    - "Documented"      # Clear docstring/comments explaining intent
    - "Implicit"        # Intent inferred from naming/patterns
    - "Ambiguous"       # Intent unclear
    - "Contradictory"   # Code behavior contradicts documentation
  detection:
    - Check for docstrings/comments
    - Compare docstring semantics to code behavior
    - Flag naming vs behavior mismatches
```

#### D10: LANGUAGE (From Ranganathan's Matter facet)
```yaml
D10_LANGUAGE:
  description: "The programming language/platform - the 'matter' of the code"
  values:
    - "Python"
    - "TypeScript" 
    - "JavaScript"
    - "Java"
    - "Go"
    - "Rust"
    - "C"
    - "C++"
    - "Other"
  note: "This is already in metadata, could be promoted to dimension"
```

### Phase 2: Add Metrics (Complexity, Coupling)

#### Complexity Metric (From Shannon's Entropy)
```yaml
metrics:
  complexity:
    cyclomatic: 5           # McCabe cyclomatic complexity
    cognitive: 8            # Cognitive complexity (SonarQube style)
    halstead_volume: 245.3  # Halstead metrics
    entropy: 3.2            # Shannon entropy of token distribution
  
  coupling:
    afferent: 5             # Incoming dependencies (Ca)
    efferent: 3             # Outgoing dependencies (Ce)
    instability: 0.375      # Ce / (Ca + Ce)
    abstractness: 0.2       # Abstract types / Total types
    distance: 0.425         # |A + I - 1| - distance from main sequence
  
  cohesion:
    lcom: 0.3               # Lack of Cohesion of Methods
    coupling_tension: 0.6   # Balance between self-assertive and integrative
```

### Phase 3: Add Antimatter Laws (Layer Violations)

```yaml
antimatter_laws:
  - id: "AM001"
    name: "Layer Skip Violation"
    description: "Direct dependency from higher layer to lower non-adjacent layer"
    detection: "If L(source) - L(target) > 1 for same subsystem"
    severity: "ERROR"
    examples:
      - "Controller calling Repository directly (skipping Service)"
      - "Interface layer calling Infrastructure directly"
  
  - id: "AM002"  
    name: "Reverse Layer Dependency"
    description: "Lower layer depending on higher layer"
    detection: "If L(source) < L(target) for 'imports' edge"
    severity: "ERROR"
    examples:
      - "Core domain importing Controller"
      - "Repository importing Service"
  
  - id: "AM003"
    name: "God Class (Pathological Holon)"
    description: "Class with too many responsibilities, too autonomous"
    detection: "methods > 20 OR afferent_coupling > 10 OR files_referring > 15"
    severity: "WARNING"
    
  - id: "AM004"
    name: "Anemic Model"
    description: "Entity with only getters/setters, no behavior"
    detection: "All methods are getters/setters AND no business logic"
    severity: "WARNING"
    
  - id: "AM005"
    name: "Bounded Context Violation"
    description: "Cross-boundary dependency without explicit interface"
    detection: "Import across L6 boundary without using defined contract"
    severity: "ERROR"
```

### Phase 4: Add DDD Properties

```yaml
ddd_properties:
  is_aggregate_root: boolean    # Is this the root of an aggregate?
  aggregate_id: string          # Which aggregate does it belong to?
  bounded_context: string       # Which bounded context?
  invariants:                   # Business rules this entity enforces
    - "user_id must be positive"
    - "email must be valid format"
  domain_events:                # Events this entity can produce
    - "UserCreated"
    - "UserUpdated"
```

### Phase 5: Define Tau Notation (Canonical ID)

```
τ(Type:Role:Layer:Boundary:State:Effect:Lifecycle:Trust)

Examples:
- τ(Method:Query:App:IO:SL:R:U:92)
  = Method, Query role, Application layer, I-O boundary, Stateless, Read effect, Use phase, 92% confidence

- τ(Class:Repository:Infra:IO:SF:RW:C:85)
  = Class, Repository role, Infrastructure layer, I-O boundary, Stateful, ReadWrite, Create phase, 85%

Abbreviations:
  Boundary: Int=Internal, In=Input, Out=Output, IO=I-O
  State: SF=Stateful, SL=Stateless
  Effect: P=Pure, R=Read, W=Write, RW=ReadWrite
  Lifecycle: C=Create, U=Use, D=Destroy
```

---

## Schema Updates Required

### particle.schema.json additions

```json
{
  "dimensions": {
    "properties": {
      "D9_INTENT": {
        "enum": ["Documented", "Implicit", "Ambiguous", "Contradictory"],
        "description": "Popper World 2 - programmer intent clarity"
      },
      "D10_LANGUAGE": {
        "type": "string",
        "description": "Ranganathan Matter facet - programming language"
      }
    }
  },
  "metrics": {
    "type": "object",
    "properties": {
      "complexity": {
        "type": "object",
        "properties": {
          "cyclomatic": { "type": "number" },
          "cognitive": { "type": "number" },
          "entropy": { "type": "number" }
        }
      },
      "coupling": {
        "type": "object", 
        "properties": {
          "afferent": { "type": "integer" },
          "efferent": { "type": "integer" },
          "instability": { "type": "number" },
          "tension": { "type": "number" }
        }
      }
    }
  },
  "ddd": {
    "type": "object",
    "properties": {
      "is_aggregate_root": { "type": "boolean" },
      "aggregate_id": { "type": "string" },
      "bounded_context": { "type": "string" },
      "invariants": { "type": "array", "items": { "type": "string" } }
    }
  },
  "violations": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "law_id": { "type": "string" },
        "severity": { "enum": ["ERROR", "WARNING", "INFO"] },
        "message": { "type": "string" }
      }
    }
  }
}
```

---

## Files to Update

| File | Changes |
|------|---------|
| `schema/particle.schema.json` | Add D9, D10, metrics, ddd, violations |
| `schema/types.ts` | Add new TypeScript types |
| `schema/types.py` | Add new Python dataclasses |
| `schema/antimatter_laws.yaml` | New file with all law definitions |
| `docs/FOUNDATIONAL_THEORIES.md` | Mark gaps as "Implemented" |
| `core/collider.py` | Add detection logic for new properties |

---

## Validation Criteria

After implementation, verify:

- [ ] D9_INTENT works on samples with/without docstrings
- [ ] Complexity metrics match external tools (radon, lizard)
- [ ] Layer violations detected in known bad codebases
- [ ] Aggregate roots identified in DDD sample projects
- [ ] Tau notation generates correctly from all dimension values
- [ ] God Class detection triggers on known examples
- [ ] Bounded context violations detected across module boundaries

