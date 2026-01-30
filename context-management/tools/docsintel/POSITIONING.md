# DocsIntel: Ontological Positioning

**Date:** 2026-01-29
**Status:** VALIDATED
**Depends on:** L0_AXIOMS.md, L1_DEFINITIONS.md, level_classifier.py

---

## Executive Summary

DocsIntel is a **documentation intelligence system** that provides access to external provider documentation (Anthropic, GCP, AWS, etc.). This document explains why DocsIntel **cannot be positioned on the L-scale (L-3 to L12)** and where it properly belongs in the Standard Model architecture.

**Key Finding:** The L-scale applies exclusively to CODOME. DocsIntel operates on external CONTEXTOME, making it orthogonal to the level hierarchy.

---

## Part 1: The L-Scale is Code-Specific

### 1.1 Formal Definition (from L0_AXIOMS.md)

The primitive notions define:

```
| Symbol | Name  | Definition                                              |
|--------|-------|---------------------------------------------------------|
| N      | Nodes | Discrete CODE entities (functions, classes, methods)    |
| L      | Levels| Scale hierarchy (16 levels from Bit to Universe)        |
```

The level assignment function:

```
λ: Entity → L          Level assignment function
```

Where `Entity` refers to **code entities** - elements with tree-sitter kinds.

### 1.2 Implementation Evidence (from level_classifier.py)

```python
# KIND_TO_LEVEL maps tree-sitter kinds to holarchy levels
KIND_TO_LEVEL = {
    "function":     "L3",   # Code construct
    "method":       "L3",   # Code construct
    "class":        "L4",   # Code construct
    "module":       "L5",   # Code construct
    "package":      "L6",   # Code construct
    "api":          "L8",   # External boundary (still code)
    ...
}
```

Every level mapping requires a **tree-sitter kind**. Markdown files, YAML configs, and documentation have no such kinds.

### 1.3 The Containment Axiom (C2)

```
contains(e₁, e₂) ⟹ λ(e₁) > λ(e₂)

Examples:
  File (L5) contains Class (L4) contains Method (L3)
  Package (L6) contains Files (L5)
  System (L7) contains Packages (L6)
```

This containment relationship is **syntactic** - it comes from code structure (AST nesting). Documentation files don't have this containment hierarchy.

### 1.4 Conclusion

| Aspect | Codome | Contextome |
|--------|--------|------------|
| Has tree-sitter kinds? | Yes | No |
| Has λ assignment? | Yes | No |
| Has containment hierarchy? | Yes (AST) | No |
| L-scale applies? | **YES** | **NO** |

**The L-scale (L-3 to L12) is a Codome-only coordinate system.**

---

## Part 2: The MECE Partition

### 2.1 Axiom A1 (from L0_AXIOMS.md)

```
P = C ⊔ X                    (Projectome is disjoint union)
C ∩ X = ∅                    (Codome and Contextome are disjoint)
C ∪ X = P                    (Together they cover everything)

WHERE:
  C = {f ∈ P | executable(f)}      Codome (executable artifacts)
  X = {f ∈ P | ¬executable(f)}     Contextome (non-executable artifacts)
```

### 2.2 What Belongs Where

| Universe | Contains | Examples |
|----------|----------|----------|
| **CODOME** | Executable artifacts | .py, .js, .ts, .go, .css, .html, .sql |
| **CONTEXTOME** | Non-executable artifacts | .md, .yaml, .json configs, research |

### 2.3 DocsIntel's Subject Matter

DocsIntel deals with:
- Anthropic documentation (external .md, web pages)
- GCP documentation (external)
- AWS documentation (external)
- Provider API references (external)

This is **external Contextome** - not even part of the current project's Projectome.

---

## Part 3: The Three Realms

### 3.1 The Trinity (from L1_DEFINITIONS.md)

```
| Realm      | Directory              | Purpose              | Nature        |
|------------|------------------------|----------------------|---------------|
| PARTICLE   | standard-model-of-code/| Analyze structure    | Deterministic |
| WAVE       | context-management/    | Understand semantics | Probabilistic |
| OBSERVER   | .agent/                | Coordinate actions   | Reactive      |
```

### 3.2 What Each Realm Does

- **PARTICLE (Collider):** Analyzes CODE structure using the L-scale
- **WAVE (Refinery):** Understands CODE semantics via AI
- **OBSERVER (.agent/):** Coordinates actions, manages state, acquires knowledge

### 3.3 Where DocsIntel Fits

DocsIntel is a **knowledge acquisition tool** for the OBSERVER. It doesn't analyze code - it fetches external documentation to inform decision-making.

```
OBSERVER Realm (.agent/)
├── Autopilot     → Coordinates actions
├── Wire          → Routes information
├── Watcher       → Monitors state
└── DocsIntel      → Ingests external knowledge   ← NEW
```

---

## Part 4: Why DocsIntel Cannot Be on the L-Scale

### 4.1 The Containment Problem

The L-scale is a **containment hierarchy**:

```
L12 UNIVERSE contains L11 DOMAIN contains L10 ORGANIZATION contains ...
```

DocsIntel doesn't "contain" Anthropic or GCP. It **knows about** them. This is a fundamentally different relationship:

| Relationship | Example | L-Scale Applicable? |
|--------------|---------|---------------------|
| **Contains** | File contains Class | Yes |
| **Calls** | Function calls Function | Yes (edge type) |
| **Knows about** | DocsIntel knows about GCP | **No** |

### 4.2 The Kind Problem

Every L-scale position requires a tree-sitter kind:

```python
# From level_classifier.py
def classify_level(node: Dict[str, Any]) -> str:
    kind = node.get("kind", "").lower()  # Requires a kind!
    if kind in KIND_TO_LEVEL:
        return KIND_TO_LEVEL[kind]
```

DocsIntel has no tree-sitter kind. It's not a function, class, module, or any code construct.

### 4.3 The Universe Problem

Even if we tried to place DocsIntel at L8 (ECOSYSTEM) or higher:

```
L8  ECOSYSTEM   - External boundaries
L9  PLATFORM    - Monorepo/platform
L10 ORGANIZATION- Company/team repos
L11 DOMAIN      - Business domain
L12 UNIVERSE    - All software
```

These levels describe **code at scale**, not **knowledge about code**. L12 UNIVERSE means "all software that exists" - not "a tool that knows about software."

---

## Part 5: The Correct Positioning

### 5.1 Orthogonal to L-Scale

DocsIntel exists on a **different axis** than the L-scale:

```
                        WHAT IT OPERATES ON
                        │
        CODE            │           EXTERNAL KNOWLEDGE
        (Codome)        │           (External Contextome)
             │          │                │
             │          │                │
        L-3 to L12      │           DocsIntel
        (Holarchy)      │           (No L-level)
             │          │                │
    ─────────┼──────────┼────────────────┼───────
             │          │                │
        PARTICLE        │           OBSERVER
        (Collider)      │           (Knowledge Substrate)
                        │
                    WAVE
                    (Refinery)
```

### 5.2 Observer Realm Subsystem

Using Miller's 10 Universal Subsystems:

```
| Subsystem   | Software Analogue    | Examples                    |
|-------------|---------------------|-----------------------------|
| Ingestor    | Input handling      | Request parsers, validators |
```

DocsIntel is an **INGESTOR** for the OBSERVER realm - it brings external knowledge INTO the system.

### 5.3 Final Position

```
Position: OBSERVER.Ingestor
Realm: OBSERVER (.agent/)
Subsystem: Ingestor (Miller's taxonomy)
L-Scale: N/A (orthogonal)
Nature: Meta-tool (operates on external knowledge, not code)
```

---

## Part 6: Architecture Summary

### 6.1 DocsIntel's Place in the System

```
PROJECT_elements/
├── standard-model-of-code/     # PARTICLE realm
│   └── (L-scale applies here)
│
├── context-management/         # WAVE realm
│   ├── tools/
│   │   └── docsintel/           # DocsIntel lives here
│   │       ├── DOCINTEL.md     # Architecture
│   │       ├── POSITIONING.md  # This file
│   │       ├── providers.yaml  # Provider registry
│   │       └── install.sh      # Setup script
│   └── ...
│
└── .agent/                     # OBSERVER realm
    └── (DocsIntel serves this realm)
```

### 6.2 What DocsIntel Orchestrates

```
┌─────────────────────────────────────────────────────────────────┐
│                    DocsIntel (OBSERVER.Ingestor)                 │
│                    Orthogonal to L-scale                        │
├─────────────────────────────────────────────────────────────────┤
│  Purpose: Acquire external knowledge for the Observer           │
│  Subject: External provider documentation                       │
│  Method: MCP server orchestration                               │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PRE-INDEXED   │  │  SELF-INDEXED   │  │   CUSTOM RAG    │
│   MCP Servers   │  │   docs-mcp      │  │    (Future)     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Context7      │  │ Index on-demand │  │ • Vector DB     │
│ • anthropic-mcp │  │ • Any URL       │  │ • Cross-provider│
│ • AWS MCP       │  │ • GitHub        │  │   queries       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 6.3 Relationship to L-Scale Entities

When DocsIntel provides knowledge, it informs decisions about L-scale entities:

```
DocsIntel                    L-Scale Code
(External Knowledge)        (Codome)
        │                       │
        │   "Anthropic API      │
        │    requires Tier 4    │
        │    for 1M context"    │
        │          │            │
        │          ▼            │
        │   Decision: Modify    │
        │   API call code       │
        │          │            │
        │          ▼            │
        └──────────────────────►│  L3: api_client.py::call_anthropic()
                                │  L8: External API boundary
```

DocsIntel INFORMS decisions about code but doesn't EXIST on the code scale.

---

## Part 7: Implications

### 7.1 For the Standard Model

The Standard Model's L-scale is **domain-specific to code**. This is correct and should remain so. Extending L-levels to non-code artifacts would break:
- The containment axiom (C2)
- The kind-to-level mapping
- The tree-sitter foundation

### 7.2 For Future Tools

Other meta-tools that operate on external knowledge should also be positioned in OBSERVER, not forced onto the L-scale:

| Tool | Subject | Position |
|------|---------|----------|
| DocsIntel | External documentation | OBSERVER.Ingestor |
| Market Intel | Competitor analysis | OBSERVER.Ingestor |
| Compliance | Regulatory requirements | OBSERVER.Ingestor |
| Telemetry | Runtime metrics | OBSERVER.Sensor |

### 7.3 For Architectural Clarity

The separation is clean:

```
L-Scale (Codome)          OBSERVER (Meta)
├── Analyzes CODE         ├── Acquires KNOWLEDGE
├── Tree-sitter based     ├── MCP/RAG based
├── Deterministic         ├── Probabilistic
└── Containment hierarchy └── Service topology
```

---

## Appendix A: Research Origin

This positioning analysis emerged from attempting to solve:

> "Two Anthropic Max 20x accounts have different 1M context access - why?"

The attempt to find authoritative documentation led to:
1. Discovery of documentation intelligence MCP servers
2. Need to position DocsIntel in the Standard Model
3. Realization that L-scale doesn't apply to Contextome
4. Proper positioning in OBSERVER realm

See: `RESEARCH.md` for full investigation notes.

---

## Appendix B: Validation

### B.1 Theoretical Validation

| Claim | Source | Status |
|-------|--------|--------|
| N = code entities | L0_AXIOMS.md line 28 | VERIFIED |
| λ: Entity → L | L0_AXIOMS.md line 160 | VERIFIED |
| KIND_TO_LEVEL requires tree-sitter | level_classifier.py line 81 | VERIFIED |
| MECE partition C ⊔ X | L0_AXIOMS.md Axiom A1 | VERIFIED |
| Three Realms | L1_DEFINITIONS.md §0 | VERIFIED |

### B.2 Practical Validation

- DocsIntel has no tree-sitter kind: Cannot assign L-level
- DocsIntel doesn't contain providers: Violates containment axiom
- DocsIntel operates on external data: Outside Projectome entirely

---

## References

1. `standard-model-of-code/docs/theory/L0_AXIOMS.md` - Foundational axioms
2. `standard-model-of-code/docs/theory/L1_DEFINITIONS.md` - Definitions including Three Realms
3. `standard-model-of-code/src/core/level_classifier.py` - L-scale implementation
4. Miller, J. G. (1978). "Living Systems" - 10 Universal Subsystems
5. Koestler, A. (1967). "The Ghost in the Machine" - Holarchy concept

---

*DocsIntel is orthogonal to the L-scale. It belongs in OBSERVER as a knowledge ingestor.*
