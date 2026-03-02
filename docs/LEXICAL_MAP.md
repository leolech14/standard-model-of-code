# LEXICAL MAP - Standard Model of Code

> The atlas. Every core term, defined once. Start here.

---

## NAVIGATION MAP

```
PROJECT_elements/
│
├── .agent/ ──────────► OBSERVER (governance, tasks, decisions)
│
├── particle/ ────────► PARTICLE (Collider engine, deterministic analysis)
│   ├── src/core/        Pipeline stages
│   ├── data/atoms/      Atom taxonomy (3,610 atoms)
│   └── docs/            Theory (L0-L3), MODEL.md
│
└── wave/ ────────────► WAVE (AI tools, context, probabilistic)
    ├── tools/ai/        analyze.py, ACI, research
    ├── docs/            Glossaries, topology
    └── config/          Analysis sets, models
```

---

## THE ALGEBRA

```
PARTITIONS (disjoint, complete)
──────────────────────────────────────
P = C ⊔ X         Projectome = Codome ⊔ Contextome
C ∩ X = ∅         No file is both executable and non-executable

REALMS (disjoint, complete)
──────────────────────────────────────
P = Particle ⊔ Wave ⊔ Observer

CLASSIFICATION (total function)
──────────────────────────────────────
σ: Nodes → Atoms   Every node maps to exactly one atom

CONCORDANCES (cover, may overlap)
──────────────────────────────────────
⋃ Cᵢ = P           Concordances cover everything
κ(Cᵢ) → [0,1]      Each has an alignment score

SYMMETRY (relation)
──────────────────────────────────────
R: Code × Docs → {SYMMETRIC, ORPHAN, PHANTOM, DRIFT}
```

---

## UNIVERSES (The MECE Partition)

| Term | Definition |
|------|------------|
| **PROJECTOME** | All files in the project. The universe. P = C ⊔ X. |
| **CODOME** | All executable code (.py, .js, .ts, .go, .rs). What runs. |
| **CONTEXTOME** | All non-executable content (.md, .yaml, configs). What informs. |

---

## REALMS (The Trinity)

| Realm | Path | Nature | Purpose |
|-------|------|--------|---------|
| **PARTICLE** | `particle/` | Deterministic | Measure structure (Collider) |
| **WAVE** | `wave/` | Probabilistic | Understand semantics (AI tools) |
| **OBSERVER** | `.agent/` | Reactive | Coordinate actions (governance) |

---

## CLASSIFICATION

| Concept | Count | What It Answers |
|---------|-------|-----------------|
| **Atom** | 3,610 (94 core) | WHAT type of code element? |
| **Role** | 33 canonical | WHY does it exist? |
| **Dimension** | 8 | HOW is it characterized? |
| **Phase** | 4 | What CATEGORY of concern? |
| **Level** | 16 (L-3 to L12) | WHERE in the holarchy? |
| **RPBL** | 4 axes, 6,561 states | HOW does it behave? |

---

## CONCORDANCES & SYMMETRY

| State | Code | Docs | Meaning |
|-------|------|------|---------|
| **CONCORDANT** | exists | exists | Purposes align. Healthy. |
| **UNVOICED** | exists | missing | Code without docs. Tech debt. |
| **UNREALIZED** | missing | exists | Spec not implemented. |
| **DISCORDANT** | exists | exists | Purposes disagree. Dangerous. |

---

## PURPOSE FIELD

| Term | Definition |
|------|------------|
| **Purpose Field** | Vector field over nodes: what each entity is FOR |
| **Purpose = Identity** | You ARE what you're FOR |
| **Crystallization** | Code freezes intent at commit time |
| **Purpose Drift** | Gap between human intent and frozen code |
| **Technical Debt** | Accumulated drift since last commit |
| **Emergence** | Higher-level purpose exceeds sum of parts |

---

## TOPOLOGY

| Role | Condition | Meaning |
|------|-----------|---------|
| **orphan** | in=0, out=0 | Disconnected (but only ~9% are truly dead) |
| **root** | in=0, out>0 | Entry point |
| **leaf** | in>0, out=0 | Terminal node |
| **hub** | high degree | Central coordinator |
| **internal** | in>0, out>0 | Normal flow-through |

---

## SUBSYSTEMS

| ID | Name | Purpose |
|----|------|---------|
| S1 | **Collider** | Static analysis pipeline (28 stages) |
| S2 | **HSL** | Validation rules (drift detection) |
| S3 | **analyze.py** | AI query tool |
| S4 | **ACI** | 5-tier query routing |
| S5 | **BARE** | Auto-refinement engine |
| S6 | **Laboratory** | Research API bridge |
| S7 | **Registry** | Task tracking |

---

## THREE PLANES (Popper)

| Plane | What Lives Here | Example |
|-------|----------------|---------|
| **Physical** | Bits, bytes, files | `0x48 0x65 0x6C 0x6C 0x6F` |
| **Virtual** | AST nodes, runtime objects | `FunctionDeclaration` |
| **Semantic** | Meaning, intent | `Repository`, `Service` |

Every artifact exists in all three simultaneously.

---

## EDGE TYPES

| Type | Meaning | Example |
|------|---------|---------|
| CALLS | Invocation | `main() calls init()` |
| IMPORTS | Dependency | `app.py imports utils` |
| INHERITS | Extension | `Dog inherits Animal` |
| IMPLEMENTS | Realization | `UserRepo implements IRepo` |
| CONTAINS | Composition | `Class contains method` |
| USES | Reference | `handler uses logger` |

---

## CONSUMER CLASSES

| Consumer | Needs | Stone Tool Test |
|----------|-------|-----------------|
| **END_USER** | Usability | Can use directly |
| **DEVELOPER** | Clarity | Can use directly |
| **AI_AGENT** | Parseability | May need AI mediation |

**Stone Tool Principle:** Tools MAY be designed that humans cannot use directly. AI mediates.

---

## ETYMOLOGY

| Term | Origin |
|------|--------|
| **-ome** | Greek -ωμα: complete set (genome, proteome) |
| **Particle/Wave** | Quantum duality: measurement vs potential |
| **Collider** | Particle physics: smash to find constituents |
| **Holons** | Koestler: parts that are also wholes |

---

## DEEPER READING

| Need | File |
|------|------|
| The unifying equation | [essentials/LAGRANGIAN.md](essentials/LAGRANGIAN.md) |
| The 13 big ideas | [essentials/THEORY_WINS.md](essentials/THEORY_WINS.md) |
| Why "Standard Model" | [essentials/VISION.md](essentials/VISION.md) |
| Classification reference | [essentials/CLASSIFICATION.md](essentials/CLASSIFICATION.md) |
| Architecture overview | [essentials/ARCHITECTURE.md](essentials/ARCHITECTURE.md) |
| Quick topic lookup | [nav/](nav/) (10 single-topic files) |
| Full theory (L0-L3) | [../particle/docs/theory/THEORY_INDEX.md](../particle/docs/theory/THEORY_INDEX.md) |
| Machine-readable terms | [../particle/docs/GLOSSARY.yaml](../particle/docs/GLOSSARY.yaml) |
| Day-1 survival kit | [../wave/docs/GLOSSARY_QUICK.md](../wave/docs/GLOSSARY_QUICK.md) |

---

*Distilled from wave/docs/GLOSSARY.md (450 lines) and particle/docs/GLOSSARY.yaml (156 terms)*
*This file: ~180 lines, every core term defined once*
