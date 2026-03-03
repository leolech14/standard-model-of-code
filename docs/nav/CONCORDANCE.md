# CONCORDANCE - Code-Doc Alignment

> A concordance is a purpose-aligned region spanning both code and documentation. Health = alignment.

---

## What's a Concordance?

A concordance is a **region of shared purpose** that crosses the Codome/Contextome boundary. It links the code that DOES something with the docs that DESCRIBE it.

Example: The "Pipeline" concordance includes:
- `full_analysis.py` (Codome -- the code)
- `PIPELINE_STAGES.md` (Contextome -- the docs)

Both exist to serve the same purpose: the analysis pipeline.

---

## The 4 Health States

| State | Code | Docs | Meaning |
|-------|------|------|---------|
| **CONCORDANT** | exists | exists | Purposes agree. Healthy. |
| **UNVOICED** | exists | missing | Code without matching docs. Traditional tech debt. |
| **UNREALIZED** | missing | exists | Spec not yet implemented. Roadmap item. |
| **DISCORDANT** | exists | exists | Both exist but state contradictory purposes. **Most dangerous.** |

---

## Why DISCORDANT Is Worst

- **UNVOICED** (no docs): You know something is undocumented. Obvious gap.
- **UNREALIZED** (no code): You know a spec isn't built yet. Expected state.
- **DISCORDANT** (both wrong): The docs say one thing, the code does another. **You don't know who's right.** Developers trust the docs and write code that contradicts the actual behavior. Users read the docs and expect behavior the code doesn't deliver.

---

## Measuring Drift

Drift between code and docs is measured as **cosine distance** between their purpose vectors:

```
drift(concordance) = 1 - cos(𝒫_code, 𝒫_docs)
```

| Drift | Interpretation |
|-------|---------------|
| 0.0 | Perfect alignment |
| 0.0-0.2 | Minor wording differences |
| 0.2-0.5 | Structural divergence |
| 0.5+ | Fundamental disagreement (DISCORDANT) |

---

## Symmetry Score

The overall health of a concordance uses the **harmonic mean** of two sub-scores:

```
Symmetry = harmonic_mean(Coverage, Realizability)

Coverage     = |code with matching docs| / |all code|
Realizability = |docs with matching code| / |all docs|
```

Harmonic mean penalizes imbalance. A project with great coverage but poor realizability (lots of unbuilt specs) still scores low.

---

## Concordance Examples

```
            │ CODOME              │ CONTEXTOME
────────────┼─────────────────────┼─────────────────
Pipeline    │ full_analysis.py    │ PIPELINE_STAGES.md
            │ survey.py           │ specs/*.md
────────────┼─────────────────────┼─────────────────
AI Tools    │ analyze.py          │ analysis_sets.yaml
            │ aci/*.py            │ prompts.yaml
────────────┼─────────────────────┼─────────────────
Governance  │ task_store.py       │ registry/*.yaml
            │ confidence.py       │ ROADMAP.yaml
```

---

## Key Insight

This extends the "orphan" concept from individual nodes to **entire regions**. A subsystem can be concordant even if individual functions lack docstrings. Conversely, every function can have docstrings while the subsystem is discordant (the docs collectively describe a different system than what the code implements).

---

*Source: L0_AXIOMS.md (Axioms A1), L2_PRINCIPLES.md (§4)*
*See also: [PURPOSE.md](PURPOSE.md) for drift mechanics, [../essentials/ARCHITECTURE.md](../essentials/ARCHITECTURE.md) for concordance health table*
