# TOPOLOGY MAP - Navigation Through PROJECT_elements

> **Status:** ACTIVE
> **Created:** 2026-01-25
> **Purpose:** Complete spatial model for navigating this repository

## The Universe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PROJECTOME                                      │
│                         (all project contents)                               │
│                                                                              │
│    ┌──────────────────────────────┐    ┌──────────────────────────────┐     │
│    │           CODOME             │    │         CONTEXTOME           │     │
│    │      (all executable)        │    │     (all non-executable)     │     │
│    │                              │    │                              │     │
│    │  .py .js .ts .go .rs .css   │    │  .md .yaml .json (config)    │     │
│    │  .html .scm .sql .sh        │    │  research/ registry/         │     │
│    │                              │    │                              │     │
│    │  Analyzed by: COLLIDER      │    │  Analyzed by: ACI            │     │
│    └──────────────────────────────┘    └──────────────────────────────┘     │
│                                                                              │
│    ═══════════════ CONCORDANCES (purpose-aligned regions) ═══════════════   │
│                                                                              │
│    Pipeline ──────┼─── src/core/*.py ──────┼─── docs/specs/PIPELINE*.md     │
│    Visualization ─┼─── viz/assets/*.js ────┼─── docs/specs/UI*.md           │
│    Governance ────┼─── .agent/tools/*.py ──┼─── .agent/registry/*.yaml      │
│    AI Tools ──────┼─── tools/ai/*.py ──────┼─── config/*.yaml               │
│    Theory ────────┼─── (none) ─────────────┼─── docs/MODEL.md               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Topology (Plain English)

**Three main directories. That's it.**

| Directory | What's Inside | When to Use |
|-----------|---------------|-------------|
| `particle/` | Collider engine, analysis pipeline, theory docs | Analyzing code |
| `wave/` | AI tools, research, this documentation | Querying context |
| `.agent/` | Task registry, automation, agent state | Managing work |

## Directory Topology (With Metaphors)

*The physics metaphor (Particle/Wave/Observer) is optional context. Skip if not useful.*

```
PROJECT_elements/
│
├── particle/     ← "Particle" - measurement, determinism
│   ├── src/core/               ← Pipeline engine (CODOME)
│   ├── src/patterns/           ← Atom definitions (CODOME)
│   ├── docs/                   ← Theory & specs (CONTEXTOME)
│   └── tools/                  ← Utilities (CODOME)
│
├── wave/         ← "Wave" - potential, AI reasoning
│   ├── tools/ai/               ← AI engines (CODOME)
│   ├── config/                 ← Configurations (CONTEXTOME)
│   └── docs/                   ← This topology (CONTEXTOME)
│       ├── CODOME.md
│       ├── CONTEXTOME.md
│       ├── PROJECTOME.md
│       ├── CONCORDANCES.md
│       └── TOPOLOGY_MAP.md     ← YOU ARE HERE
│
└── .agent/                     ← "Observer" - decides what to do next
    ├── registry/               ← Task state (CONTEXTOME)
    ├── specs/                  ← Governance specs (CONTEXTOME)
    ├── tools/                  ← Automation (CODOME)
    └── intelligence/           ← AI outputs (CONTEXTOME)
```

## Navigation Quick Reference

| I want to... | Go to |
|--------------|-------|
| Understand the CODOME | `CODOME.md` |
| Understand the CONTEXTOME | `CONTEXTOME.md` |
| See all project contents | `PROJECTOME.md` |
| Navigate by concordance | `CONCORDANCES.md` |
| See system connections | `.agent/SUBSYSTEM_INTEGRATION.md` |
| Find all registries | `../../particle/docs/specs/REGISTRY_OF_REGISTRIES.md` |
| Start AI analysis | `AI_USER_GUIDE.md` |
| Run the Collider | `particle/CLAUDE.md` |

## The Four Documents

| Doc | Defines | Key Insight |
|-----|---------|-------------|
| `CODOME.md` | Executable code | What runs |
| `CONTEXTOME.md` | Non-executable content | What informs |
| `PROJECTOME.md` | Complete contents | The union |
| `CONCORDANCES.md` | Cross-cuts | Purpose-aligned regions |

## Realm Physics

| Realm | Path | Metaphor | Purpose |
|-------|------|----------|---------|
| **Particle** | `particle/` | Measurement | Collapse code to knowledge |
| **Wave** | `wave/` | Potential | AI reasoning, strategy |
| **Observer** | `.agent/` | Decision | What to measure next |

## The Algebra

```
P = C ⊔ X        PROJECTOME = CODOME ⊔ CONTEXTOME (disjoint union)
X = P \ C        CONTEXTOME = PROJECTOME \ CODOME  (set difference)
C = P \ X        CODOME = PROJECTOME \ CONTEXTOME  (set difference)
C ∩ X = ∅        No overlap (mutually exclusive)
```

**Partition:** CODOME and CONTEXTOME partition PROJECTOME (MECE).

## Classification Rule

```
For any file F in PROJECTOME:

IF F is executable (parseable, runnable):
   F ∈ CODOME

IF F is non-executable (docs, config, data):
   F ∈ CONTEXTOME

Every file belongs to exactly one. No exceptions.
```

## Concordance States

```
SYMMETRIC   Code ←→ Context    Healthy
ORPHAN      Code ←→ ∅          Undocumented
PHANTOM     ∅    ←→ Context    Unimplemented
DRIFT       Code ←/→ Context   Out of sync
```

## Tools by Universe

| Universe | Primary Tool | Command |
|----------|--------------|---------|
| CODOME | Collider | `./collider full <path>` |
| CONTEXTOME | ACI (analyze.py) | `python analyze.py "query"` |
| PROJECTOME | Registry of Registries | Manual inspection |
| CONCORDANCES | HSL | `python analyze.py --verify` |

## Theory Layer

The mathematical formalization lives in `CODESPACE_ALGEBRA.md`:

```
CODESPACE TUPLE:
  𝕮 = (P, G, σ, ρ, λ, 𝒫, H, ε)

PURPOSE FIELD (𝒫):
  - Dynamic in humans (flows, adapts)
  - Crystallized in code (frozen at commit)
  - Shape: Focusing Funnel (diffuse at L0, sharp at L12)
  - Drift: Δ𝒫 = 𝒫_human - 𝒫_code

EMERGENCE:
  "Whole > parts" = New layer born

CONSTRUCTAL LAW:
  Code evolves to optimize flow
```

| Theory Doc | Contents |
|------------|----------|
| `CODESPACE_ALGEBRA.md` | Full mathematical model |
| `GLOSSARY.md` | Term definitions (Purpose Field section) |
| `particle/docs/MODEL.md` | Standard Model theory |

---

*Created: 2026-01-25*
*Navigation is topology. Know your space.*
