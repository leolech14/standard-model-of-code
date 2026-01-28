# PROJECT_elements - Theory Audit Manifest

> **Created:** 2026-01-26
> **Purpose:** Curated list of documents for external audit (ChatGPT 5.2 Pro)
> **Status:** DRAFT - needs review before packaging

---

## EXECUTIVE SUMMARY

PROJECT_elements is building a **"Standard Model of Code"** - a physics-inspired framework for understanding what computer programs are made of.

**The Core Question:** What are the fundamental constituents of software?

**The Answer:** Atoms (semantic units), Roles (responsibilities), Levels (scale), and Purpose (teleology).

---

## DOCUMENT HIERARCHY (Fundamentals → Derived)

### LAYER 0: AXIOMS (Mathematical Foundation)
> Start here. These are the irreducible primitives.

| Priority | File | Size | Content |
|----------|------|------|---------|
| **1** | `standard-model-of-code/docs/theory/THEORY_AXIOMS.md` | 14KB | Formal axioms A1-H5, validation status |

**Key axiom groups:**
- A: Set Structure (P = C ⊔ X partition)
- B: Graph Structure (nodes, edges)
- C: Level Structure (16-level hierarchy)
- D: Purpose Field (teleology)
- E: Constructal Law (flow optimization)
- F: Emergence (whole > parts)
- G: Observability (Peircean triad)
- H: Consumer Classes (AI-native design)

---

### LAYER 1: FOUNDATIONS (Core Theory)
> The canonical definitions. Read these after axioms.

| Priority | File | Size | Content |
|----------|------|------|---------|
| **2** | `standard-model-of-code/docs/MODEL.md` | 13KB | THE theory document |
| **3** | `context-management/docs/GLOSSARY.md` | 17KB | Definitive terminology (400+ terms) |
| **4** | `context-management/docs/PROJECTOME.md` | 6KB | Universe definition: P = C ⊔ X |
| **5** | `context-management/docs/CODOME.md` | 3KB | Executable code definition |
| **6** | `context-management/docs/CONTEXTOME.md` | 5KB | Non-executable content definition |

---

### LAYER 2: EXTENDED THEORY (Formal Mathematics)
> Deep formalization. Optional for initial audit.

| Priority | File | Size | Content |
|----------|------|------|---------|
| **7** | `context-management/docs/CODESPACE_ALGEBRA.md` | 55KB | Full mathematical formalization |
| **8** | `standard-model-of-code/docs/THEORY_EXPANSION_2026.md` | 27KB | Holon theory, purpose field depth |
| **9** | `standard-model-of-code/docs/PURPOSE_INTELLIGENCE.md` | 8KB | Q-scores, quality metrics |
| **10** | `standard-model-of-code/docs/theory/PROJECTOME_THEORY.md` | ~10KB | Projectome algebra details |

---

### LAYER 3: IMPLEMENTATION SPECS (How It Works)
> Technical specifications for the Collider tool.

| Priority | File | Size | Content |
|----------|------|------|---------|
| **11** | `standard-model-of-code/docs/COLLIDER.md` | 15KB | Tool reference, commands, pipeline |
| **12** | `standard-model-of-code/CLAUDE.md` | 12KB | Collider developer guide |
| **13** | `standard-model-of-code/docs/GLOSSARY.yaml` | ~30KB | 122 canonical terms (machine-readable) |
| — | `standard-model-of-code/docs/specs/PIPELINE_STAGES.md` | — | 28-stage analysis pipeline |
| — | `standard-model-of-code/docs/specs/CODOME_LANDSCAPE.md` | — | Topology, elevation, gradients |

---

### LAYER 4: OPERATIONAL CONTEXT (AI/Governance)
> How AI agents interact with the theory.

| File | Size | Content |
|------|------|---------|
| `context-management/docs/BACKGROUND_AI_LAYER_MAP.md` | 33KB | BARE, AEP, HSL engines |
| `context-management/docs/AI_USER_GUIDE.md` | 5KB | Three AI roles (Librarian, Surgeon, Architect) |
| `context-management/docs/HOLOGRAPHIC_SOCRATIC_LAYER.md` | 4KB | 24/7 validation system |
| `.agent/specs/GOVERNANCE_SCHEMA.yaml` | — | Task registry, confidence scoring |

---

### LAYER 5: RESEARCH EVIDENCE
> AI-generated research validating the theory.

| Location | Count | Content |
|----------|-------|---------|
| `standard-model-of-code/docs/research/gemini/` | ~50 | Gemini 3 Pro validations |
| `standard-model-of-code/docs/research/perplexity/` | ~30 | Perplexity research outputs |
| `standard-model-of-code/docs/research/claude/` | ~20 | Claude analysis results |

---

## RECOMMENDED AUDIT PACKAGE

### Tier 1: Minimal (5 files, ~50KB)
For quick theory understanding:

1. `THEORY_AXIOMS.md` - Axioms
2. `MODEL.md` - Theory
3. `GLOSSARY.md` - Terms
4. `PROJECTOME.md` - Universes
5. `COLLIDER.md` - Tool

### Tier 2: Complete (15 files, ~200KB)
For thorough audit:

Add from Layers 2-3:
- `CODESPACE_ALGEBRA.md`
- `THEORY_EXPANSION_2026.md`
- `PURPOSE_INTELLIGENCE.md`
- `BACKGROUND_AI_LAYER_MAP.md`
- `AI_USER_GUIDE.md`
- + specs directory

### Tier 3: Full (ALL active docs, ~67MB)
For comprehensive audit:

- All 675 active documentation files
- Excludes archive (1.3GB of historical versions)

---

## KNOWN ISSUES

### Duplication
- Multiple THEORY_*.md files in archive (consolidated into THEORY_AXIOMS.md)
- GLOSSARY exists in two forms: `.md` (human) and `.yaml` (machine)
- Some concepts repeated across MODEL.md and THEORY_EXPANSION.md

### Sprawl
- 675 active docs, 253 archived docs
- 1.3GB in archive directory (historical versions)
- Research outputs scattered across 3 AI engines

### Gaps
- `GLOSSARY_GAP_MAP.md` lists missing terms
- Some axioms marked "HEURISTIC" (not formally proven)
- Consumer class theory (H-axioms) is newer, less tested

---

## FILE LOCATIONS SUMMARY

```
PROJECT_elements/
├── standard-model-of-code/
│   ├── docs/
│   │   ├── MODEL.md              ← CANONICAL THEORY
│   │   ├── COLLIDER.md           ← Tool reference
│   │   ├── theory/
│   │   │   ├── THEORY_AXIOMS.md  ← FORMAL AXIOMS
│   │   │   └── PROJECTOME_THEORY.md
│   │   ├── specs/                ← Technical specs (24 files)
│   │   └── research/             ← AI research outputs
│   └── CLAUDE.md                 ← Developer guide
│
├── context-management/
│   ├── docs/
│   │   ├── GLOSSARY.md           ← TERMINOLOGY
│   │   ├── PROJECTOME.md         ← Universe definitions
│   │   ├── CODOME.md
│   │   ├── CONTEXTOME.md
│   │   ├── CODESPACE_ALGEBRA.md  ← Full math (55KB)
│   │   └── BACKGROUND_AI_LAYER_MAP.md
│   └── config/                   ← Semantic models
│
└── .agent/
    ├── registry/                 ← Task tracking
    └── specs/                    ← Governance schemas
```

---

## NEXT STEPS

1. **Review this manifest** - Is the hierarchy correct?
2. **Choose tier** - Minimal (5 files) or Complete (15 files)?
3. **Generate zip** - Run packaging script
4. **Send to ChatGPT** - For external audit

---

*Generated: 2026-01-26*
