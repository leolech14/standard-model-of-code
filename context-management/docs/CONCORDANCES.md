# CONCORDANCES - Purpose Alignment Regions

> Vertical slices through CODOME and CONTEXTOME where code and documentation share concordant PURPOSE.

## Etymology & Lineage

**Concordance** (n.) — From Latin *concordare* ("agree together").

| Heritage | Meaning | Our Extension |
|----------|---------|---------------|
| **Latin** | Agreement, harmony | - |
| **NLP/Linguistics** | Measurable text alignment | - |
| **DDD "Domain"** | Purpose-driven region | We add MEASUREMENT |
| **PROJECT_elements** | Purpose region + alignment metric | **CONCORDANCE** |

Previously called "Domain" (borrowed from DDD), renamed to **Concordance** to emphasize:
1. The MEASUREMENT aspect (concordance score)
2. The PURPOSE alignment (not just grouping)
3. The code ↔ docs AGREEMENT (not just co-location)

## Definition

**Concordance** (n.) — A PURPOSE-defined region of the PROJECTOME where:
1. Code and docs share the **SAME PURPOSE**
2. That purpose is **MEASURABLY ALIGNED**
3. Health = how well they **AGREE** on purpose

```
Concordance = {
  purpose: "the shared WHY",
  codome_slice: "code that serves this purpose",
  contextome_slice: "docs that describe this purpose",
  score: "alignment between 𝒫_code and 𝒫_docs"
}
```

## Connection to Purpose Field

From CODESPACE_ALGEBRA.md §10:

```
𝒫(n) = Purpose vector over nodes
IDENTITY(n) ≡ 𝒫(n)    "You ARE what you're FOR"
```

**Concordance Score** measures:
```
Score = 𝒫_code · 𝒫_docs       Dot product (alignment)
        ─────────────────
        ‖𝒫_code‖ · ‖𝒫_docs‖

Score = 1.0  →  Perfect concordance
Score < 1.0  →  Purpose drift
Score = 0    →  Orthogonal purposes
```

## The Cross-Cut Model

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

## Concordance Registry

| Concordance | Codome Path | Contextome Path | Owner |
|-------------|-------------|-----------------|-------|
| **Pipeline** | `standard-model-of-code/src/core/` | `standard-model-of-code/docs/specs/` | Collider |
| **Visualization** | `standard-model-of-code/src/core/viz/` | `standard-model-of-code/docs/specs/UI*.md` | Collider |
| **Governance** | `.agent/tools/` | `.agent/registry/`, `.agent/specs/` | Observer |
| **AI Tools** | `context-management/tools/ai/` | `context-management/config/` | Wave |
| **Theory** | — | `standard-model-of-code/docs/MODEL.md` | Human |
| **Archive** | `context-management/tools/archive/` | `context-management/tools/archive/config.yaml` | Wave |
| **Research** | `context-management/tools/mcp/` | `docs/research/` | Wave |

## Concordance States

For any concordance C:
- `C.code` ⊂ CODOME (the executable implementation)
- `C.context` ⊂ CONTEXTOME (the specs, configs, docs)
- `C.score` = purpose alignment between C.code and C.context

| State | Old Name | Meaning | Formula |
|-------|----------|---------|---------|
| **CONCORDANT** | SYMMETRIC | Purposes agree | Code ↔ Docs match |
| **DISCORDANT** | DRIFT | Purposes disagree | Code ↔ Docs conflict |
| **UNVOICED** | ORPHAN | Code purpose not documented | Code ↔ ∅ |
| **UNREALIZED** | PHANTOM | Doc purpose not implemented | ∅ ↔ Docs |

**Concordance Health Score = Concordant / (Concordant + Discordant + Unvoiced + Unrealized)**

## Concordance Algebra

```
C = {C₁, C₂, ..., Cₘ}           Set of all concordances

⋃ᵢ Cᵢ = P                       Coverage (all files covered)
Cᵢ ∩ Cⱼ ≠ ∅ (allowed)          Overlap permitted (cover, not partition)

μ: P → 𝒫(C)                     File → set of concordances it belongs to
|μ(f)| ≥ 1                      Every file in at least one concordance
```

## Concordance Operations

| Operation | Tool | Purpose |
|-----------|------|---------|
| Measure concordance | `boundary_analyzer.py` | Compute alignment |
| Detect discordance | HSL --verify | Find purpose drift |
| List concordances | Registry of Registries | Discovery |
| Navigate concordance | CLAUDE.md entry points | Jump to code/docs |

## Why Concordances Matter

1. **Purpose Alignment** — Ensures code does what docs say
2. **Completeness** — Detect unvoiced code or unrealized specs
3. **Ownership** — Clear responsibility boundaries
4. **Health** — Measure documentation drift as PURPOSE drift

## The Topology

```
┌────────────────────────────────────────────────────────────────┐
│                         PROJECTOME                             │
│                                                                │
│  ┌─────────────────────┐       ┌─────────────────────┐         │
│  │       CODOME        │       │     CONTEXTOME      │         │
│  │    (executable)     │       │   (non-executable)  │         │
│  │                     │       │                     │         │
│  │  ┌───┐ ┌───┐ ┌───┐  │       │  ┌───┐ ┌───┐ ┌───┐  │         │
│  │  │ P │ │ V │ │ G │  │   ≡   │  │ P │ │ V │ │ G │  │         │
│  │  │ i │ │ i │ │ o │  │  ←→   │  │ i │ │ i │ │ o │  │         │
│  │  │ p │ │ z │ │ v │  │       │  │ p │ │ z │ │ v │  │         │
│  │  │ e │ │   │ │   │  │       │  │ e │ │   │ │   │  │         │
│  │  └───┘ └───┘ └───┘  │       │  └───┘ └───┘ └───┘  │         │
│  │                     │       │                     │         │
│  └─────────────────────┘       └─────────────────────┘         │
│                                                                │
│  Concordances are PURPOSE ALIGNMENT across both universes      │
│  The ≡ symbol = concordance (purpose agreement)                │
└────────────────────────────────────────────────────────────────┘
```

## See Also

- `CODOME.md` — Executable universe
- `CONTEXTOME.md` — Non-executable universe
- `PROJECTOME.md` — Complete contents
- `CODESPACE_ALGEBRA.md` — Purpose Field theory (§10)
- `TOPOLOGY_MAP.md` — Master navigation guide

---

*Created: 2026-01-25*
*Renamed: Domain → Concordance (ontological precision)*
*Concordances measure PURPOSE ALIGNMENT, not just co-location*
