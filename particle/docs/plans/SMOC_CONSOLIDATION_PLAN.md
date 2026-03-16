# SMoC Documentation Consolidation Plan

**Date:** 2026-03-16
**Goal:** Transform SMoC from a scattered knowledge base into a shareable source of truth accessible to 4 audiences: AI agents, developers, academic reviewers, and curious outsiders.
**Companion:** `particle/docs/research/20260315_smoc_docs_audit_report.md` (full diagnostic)
**Guiding principle:** No new content creation — consolidate, deduplicate, and surface what already exists.

---

## Phase 0: The front door (1 session, ~30 min)

**Problem:** README.md is a developer setup guide. A visitor to `github.com/leolech14/standard-model-of-code` has zero orientation on what SMoC is.

**Action 0.1 — Create `WHAT_IS_SMOC.md` at repo root.**

This is the single most impactful missing file. It should be ~200 lines, no more, covering:

```
Section 1: What is the Standard Model of Code? (3 paragraphs max)
  - The core thesis: software projects are measurable systems with formal health properties
  - The three-plane ontology: Projectome = Codome ⊔ Contextome (MECE partition)
  - The implementation: Collider engine analyzes real codebases using this framework

Section 2: Why does this matter? (bullet list)
  - No existing tool treats the totality of project contents as a single system
  - Cyclomatic complexity, coupling metrics, linters — all operate on fragments
  - SMoC provides the missing layer: purpose-aware structural comprehension

Section 3: Quick map (table)
  | If you want...                     | Start here                              |
  | To understand the theory           | particle/docs/theory/INDEX.md           |
  | To see the vocabulary              | particle/docs/GLOSSARY.yaml             |
  | To read the scientific predictions | particle/docs/theory/PREDICTIONS.md     |
  | To run the Collider                | README.md (setup guide)                 |
  | To understand the architecture     | docs/essentials/ARCHITECTURE.md         |
  | To see the vision                  | docs/essentials/VISION.md               |

Section 4: Convergence evidence (2 paragraphs)
  - Five independent frameworks (Popper, Turner, COPS, Stamper, Naur) arrive at the same structure
  - β₁ = McCabe cyclomatic complexity — proven theorem since 1976, validated bridge

Section 5: Status and maturity
  - Honest table: what's implemented, what's theoretical, what's novel
```

**Action 0.2 — Update README.md opening.**

Add a 3-line block above the "Getting Started" section:

```markdown
> **New here?** See [What is the Standard Model of Code?](WHAT_IS_SMOC.md) for a conceptual introduction.
> For the full theory: [Theory Index](particle/docs/theory/INDEX.md) | [Glossary](particle/docs/GLOSSARY.yaml) | [Predictions](particle/docs/theory/PREDICTIONS.md)
```

**Deliverables:** `WHAT_IS_SMOC.md` (new), `README.md` (2-line edit)

---

## Phase 1: Kill the monoliths (1 session, ~15 min)

**Problem:** 4 files all claim to be "the complete theory." A newcomer, a reviewer, or even an AI agent can't tell which is canonical. Combined: 11,564 lines of duplicated, drifting content.

| File | Lines | Claims | Reality |
|------|-------|--------|---------|
| `particle/docs/theory/STANDARD_MODEL_COMPLETE.md` | 435 | "CANONICAL" | Abbreviated, stale |
| `particle/docs/theory/THEORY_COMPLETE_ALL.md` | 3,430 | "GROUNDED" | Jan 28, pre-frameworks |
| `particle/docs/theory/STANDARD_MODEL_THEORY_COMPLETE.md` | 3,331 | "CANONICAL" | Jan 27, pre-frameworks |
| `wave/docs/theory/THEORY.md` | 4,368 | v3.0.0 | Dec 2025, narrative style |

**The canonical source is and always was: L0–L3 + 9 frameworks + INDEX.md.** The monoliths are snapshots from before the modular tree existed.

**Action 1.1 — Create `particle/docs/theory/DEPRECATED/` directory.**

**Action 1.2 — Move the three particle monoliths into DEPRECATED/:**

```bash
mkdir -p particle/docs/theory/DEPRECATED
git mv particle/docs/theory/STANDARD_MODEL_COMPLETE.md particle/docs/theory/DEPRECATED/
git mv particle/docs/theory/THEORY_COMPLETE_ALL.md particle/docs/theory/DEPRECATED/
git mv particle/docs/theory/STANDARD_MODEL_THEORY_COMPLETE.md particle/docs/theory/DEPRECATED/
```

**Action 1.3 — Add deprecation header to each moved file:**

```markdown
> ⚠️ **DEPRECATED** — This monolith snapshot is retained for historical reference only.
> The canonical theory source is the modular L0–L3 stack + 9 frameworks.
> Entry point: [particle/docs/theory/INDEX.md](../INDEX.md)
> Last meaningful update: 2026-01-28
```

**Action 1.4 — Decide on `wave/docs/theory/THEORY.md` (4,368 lines).**

This is the oldest and largest monolith (v3.0.0, Dec 2025). Two options:
- **Option A (recommended):** Move to `wave/docs/theory/DEPRECATED_THEORY_v3.md` with the same header.
- **Option B:** Keep as "narrative reading" version with a clear note that L0–L3 supersedes it for precision.

**Action 1.5 — Consolidate the two competing THEORY_INDEX files.**

- `particle/docs/theory/INDEX.md` (Mar 6, best structured) — **KEEP as canonical.**
- `particle/docs/theory/THEORY_INDEX.md` (older) — **DELETE or redirect to INDEX.md.**
- `wave/docs/theory/THEORY_INDEX.md` (different) — **Add redirect header pointing to particle's INDEX.md.**

**Deliverables:** 3 files moved to DEPRECATED/, 2 index files resolved, ~11K lines of confusion eliminated.

---

## Phase 2: Get best artifacts INTO the repo (1 session, ~45 min)

**Problem:** The most polished, audience-ready SMoC documents exist only as .docx artifacts in Claude.ai conversations or on the local filesystem — outside version control, invisible to anyone visiting GitHub.

### Artifacts to ingest

| Artifact | Source | Target in repo | Format |
|----------|--------|----------------|--------|
| SMoC Whitepaper (~7k words, instrumental framing) | Claude.ai chat (Mar 2) | `particle/docs/theory/whitepapers/SMoC_WHITEPAPER.md` | Convert docx → md |
| Canonical Glossary (137 terms, 4 categories) | Claude.ai chat (Mar 4) | Already have `GLOSSARY.yaml` — verify parity | Cross-check |
| Textbook Chapter (L0–L2, SVG diagrams) | Claude.ai chat (Mar 4) | `particle/docs/theory/whitepapers/SMOC_TEXTBOOK_CH3.md` | Convert docx → md |
| Ideome Specification | Claude.ai chat | `particle/docs/theory/frameworks/IDEOME.md` | Extract key content |
| Convergence Analysis (5 frameworks) | Claude.ai chat (Mar 4) | `particle/docs/theory/CONVERGENCE_ANALYSIS.md` | Extract from whitepaper |
| March 15 Audit Report | `particle/docs/research/` (gitignored!) | `particle/docs/theory/audits/20260315_docs_audit.md` | Copy + un-gitignore |

**Action 2.1 — Create missing directories:**

```bash
mkdir -p particle/docs/theory/whitepapers
mkdir -p particle/docs/theory/synthesis
mkdir -p particle/docs/theory/audits
```

**Action 2.2 — Convert and commit the whitepaper.**

The whitepaper exists in at least 3 versions across Claude.ai conversations:
1. First draft (~288 paragraphs, 12 sections, Mar 2)
2. Instrumental reframing version (renamed sections, "Models Not Laws", Mar 2)
3. Complete version (~7k words, 9 chapters, 5 parts, Mar 4)

**Step:** Export the latest .docx from Claude.ai → convert with `pandoc whitepaper.docx -o SMoC_WHITEPAPER.md` → review → commit.

**Critical:** The whitepaper should use "Semiotic Model of Code" as academic title, "Standard Model of Code" as the product/commercial title. This dual naming was established in the March 4 "Popper's Worlds" conversation.

**Action 2.3 — Formalize the Ideome as a framework document.**

`ideome_synthesis.py` (501 lines) implements the Ideome but it has no theory file. Create `particle/docs/theory/frameworks/IDEOME.md` with:
- YAML frontmatter matching the other frameworks
- Core thesis: Ideome = triangulated drift surface between Codome, Contextome, and ideal reference
- Three-layer stack: Codome (what IS) / Contextome (what is SAID) / Ideome (what SHOULD BE)
- Formulas from `ideome_synthesis.py` with line-number references
- Status: `IMPLEMENTED`
- Update `INDEX.md` framework DAG to include IDEOME

**Action 2.4 — Un-gitignore the audit report.**

The March 15 audit (`particle/docs/research/20260315_smoc_docs_audit_report.md`) is the best single diagnostic of SMoC's documentation state. It's currently gitignored because `particle/docs/research/` is in Zone 3. Either:
- Add an exception: `!particle/docs/research/20260315_smoc_docs_audit_report.md`
- Or move it to `particle/docs/theory/audits/` (tracked)

**Action 2.5 — Verify glossary parity.**

`particle/docs/GLOSSARY.yaml` (185 terms, v2.1.0) is the SSOT. But `wave/docs/GLOSSARY.md` (516 lines) and `wave/docs/GLOSSARY_QUICK.md` (44 lines) also exist. Verify:
- Are all 185 YAML terms represented in the .md version?
- If not, the .md is stale → add deprecation header pointing to GLOSSARY.yaml
- The audited .docx version from Claude.ai had 137 terms — reconcile the 48-term gap

**Deliverables:** `whitepapers/` directory with whitepaper + textbook, `frameworks/IDEOME.md`, audit report tracked, glossary parity verified.

---

## Phase 3: Resolve the concordance bugs (1 session, ~30 min)

**Problem:** The March 15 audit found two critical concordance failures that would embarrass SMoC under scrutiny — a framework that defines concordance has concordance problems of its own.

**Action 3.1 — Resolve the health model discordance.**

Two competing health formulas:

```
L3_APPLICATIONS.md §2.1:
  H(G) = 10 * (0.25*T + 0.25*E + 0.25*Gd + 0.25*A)

incoherence.py (implementation):
  I = I_struct + I_telic + I_sym + I_bound + I_flow
  Health_10 = 10 * (1 - I_total)
```

The incoherence.py model is more sophisticated and is what actually runs. **Update L3_APPLICATIONS.md** to:
1. Document both models
2. Mark the 4-term model as "simplified pedagogical form"
3. Mark the 5-term incoherence functional as "canonical implementation"
4. Add implementation reference: `incoherence.py:L42-L87` (verify line numbers)

**Action 3.2 — Ground topology_reasoning.py in TOPOLOGY.md.**

`topology_reasoning.py` classifies topology shapes (Star, Mesh, Islands, Tree, Chain) and maps them to incoherence scores via `_SHAPE_INCOHERENCE`. This is used by the health model but has zero theory documentation.

Add a section to `TOPOLOGY.md`:
```markdown
## 7. Topology Shape Classification (Implemented)

**Implementation:** `particle/src/core/topology_reasoning.py`

The Collider classifies project graph topology into five canonical shapes:
| Shape    | Definition                          | Incoherence contribution |
|----------|-------------------------------------|--------------------------|
| Star     | Single hub, all others peripheral   | Low (centralized)        |
| Mesh     | Dense cross-connections             | Low (redundant paths)    |
| Islands  | Disconnected clusters               | High (fragmentation)     |
| Tree     | Hierarchical, no cycles             | Medium (brittle)         |
| Chain    | Linear sequential dependencies      | Medium-High (bottleneck) |
```

**Action 3.3 — Fix L1_DEFINITIONS.md duplicate frontmatter.**

The YAML `---` block appears twice at the top. Mechanical fix: remove the duplicate.

**Deliverables:** Health model concordance resolved, topology shapes grounded, L1 frontmatter fixed.

---

## Phase 4: Audience-ready packaging (1–2 sessions, ~1 hour)

**Problem:** Even after Phases 0–3, the repo serves developers and AI agents well but doesn't package SMoC for academic reviewers or external audiences.

**Action 4.1 — Create audience routing table in WHAT_IS_SMOC.md.**

Different audiences need different entry points and different levels of detail:

| Audience | What they need | Entry point | Depth |
|----------|---------------|-------------|-------|
| **Curious outsider** (5 min) | "What is this?" | `WHAT_IS_SMOC.md` | Conceptual, no math |
| **Developer** (30 min) | "How do I use it?" | `README.md` → setup → `./pe collider --full` | Practical, CLI-focused |
| **AI agent** (immediate) | "What's the context?" | `CLAUDE.md` → `atlas/ATLAS.yaml` | Structured, navigable |
| **Academic reviewer** (2 hours) | "Is this rigorous?" | `whitepapers/SMoC_WHITEPAPER.md` → L0–L3 → PREDICTIONS.md | Formal, falsifiable |
| **Potential collaborator** (1 hour) | "What's novel?" | `CONVERGENCE_ANALYSIS.md` → `ACADEMIC_POSITIONING.md` → GLOSSARY.yaml | Comparative |

**Action 4.2 — Cross-reference supplementary files into INDEX.md.**

These files exist but are orphans (zero inbound links from the theory tree):
- `EPISTEMOLOGICAL_STATUS.md` → link from INDEX.md under "Methodology"
- `ACADEMIC_POSITIONING.md` → link from INDEX.md under "External Context"
- `EMPIRICAL_VALIDATION.md` → link from INDEX.md under "Validation"
- `PREDICTIONS.md` → already linked, but verify
- `docs/essentials/VISION.md` → link from WHAT_IS_SMOC.md
- `docs/essentials/ARCHITECTURE.md` → link from WHAT_IS_SMOC.md

**Action 4.3 — Create `particle/docs/theory/synthesis/THREE_PILLARS.md`.**

Brief document (~100 lines) explaining how SMoC (Pillar 1) connects to:
- Pillar 2 (Parametric UI / Semantic Algebra) — structural parallels
- Pillar 3 (Ecosystem Atlas) — data flow (Collider output → atlas component entries)
- Shared concepts: Concordance ≈ Connection, Purpose Field ≈ Semantic Graph

Source: `particle/docs/research/20260315_field_theory_three_pillars_synthesis.md` (already written, just not in the tracked theory tree).

**Action 4.4 — Update the docs/reader/ HTML site.**

The Quarto-generated reader site (last built Feb 4) is stale. It has an `index.html`, `search.json`, and rendered pages for governance docs, but NOT for theory docs. Options:
- **Quick fix:** Add the theory INDEX.md and WHAT_IS_SMOC.md to the Quarto build
- **Better fix:** Generate a GitHub Pages site from the theory tree directly
- **Best fix:** Enable GitHub Pages on the repo and auto-deploy on push

**Deliverables:** Audience routing table, orphan docs cross-referenced, Three Pillars synthesis tracked, reader site updated.

---

## Phase 5: Structural hygiene (ongoing, low priority)

These are lower-priority cleanups from the March 15 audit that improve consistency but don't block sharing.

**Action 5.1 — Add Atlas identity blocks to framework files.**

The 9 framework files already have YAML frontmatter. Extend each with:
```yaml
kind: theory_document
owner: leonardo.lech
stage: P2  # or P1 for THEORETICAL status
agent:
  explanation: "One-sentence plain-English summary for AI agents"
  context_priority: medium  # low/medium/high/critical
```

**Action 5.2 — Resolve the wave/docs/theory/ question.**

19 files (375 KB) live in `wave/docs/theory/`. Many overlap with or predate the canonical `particle/docs/theory/` tree. Decision needed:
- **Option A (clean):** Deprecate all of `wave/docs/theory/` with a redirect README. The canonical theory lives in `particle/docs/theory/`.
- **Option B (gradual):** Review each file for unique content not in the particle tree, migrate what's novel, deprecate the rest.

Unique-to-wave candidates worth reviewing:
- `ORPHAN_SEMANTICS.md` — already cross-referenced from particle's INDEX.md
- `CONTAINMENT_TOPOLOGY.md` — may contain content not in TOPOLOGY.md
- `OPTIMAL_SUBDIVISION_PRINCIPLE.md` — may contain unique constructal theory formalization

**Action 5.3 — Consolidate glossaries.**

- `particle/docs/GLOSSARY.yaml` (185 terms) — **SSOT, keep**
- `wave/docs/GLOSSARY.md` (516 lines) — stale? → add deprecation header or auto-generate from YAML
- `wave/docs/GLOSSARY_QUICK.md` (44 lines) — probably stale → deprecate
- The .docx glossary from Claude.ai (137 terms) — reconcile the 48-term difference with YAML

**Action 5.4 — Clean up `docs/essentials/` naming.**

These 5 files are good distilled summaries but their location (`docs/essentials/`) is disconnected from the theory tree. Consider symlinking or adding explicit cross-references from INDEX.md.

---

## Target structure after consolidation

```
PROJECT_elements/
├── WHAT_IS_SMOC.md                          ← NEW: front door for all audiences
├── README.md                                ← EDITED: link to WHAT_IS_SMOC.md
├── CLAUDE.md                                ← UNCHANGED: AI agent orientation
├── particle/docs/
│   ├── GLOSSARY.yaml                        ← SSOT: 185 terms, v2.1.0
│   └── theory/
│       ├── INDEX.md                         ← SSOT: master navigation (consolidated)
│       ├── foundations/
│       │   ├── L0_AXIOMS.md                ← canonical
│       │   ├── L1_DEFINITIONS.md           ← canonical (fix dup frontmatter)
│       │   ├── L2_PRINCIPLES.md            ← canonical
│       │   └── L3_APPLICATIONS.md          ← canonical (fix health model)
│       ├── frameworks/
│       │   ├── PURPOSE_SPACE.md            ← canonical
│       │   ├── GRAPH_THEORY.md ... (8 more)
│       │   └── IDEOME.md                   ← NEW: formalize the Ideome
│       ├── whitepapers/
│       │   ├── SMoC_WHITEPAPER.md          ← NEW: from Claude.ai docx
│       │   └── SMOC_TEXTBOOK_CH3.md        ← NEW: from Claude.ai docx
│       ├── synthesis/
│       │   └── THREE_PILLARS.md            ← NEW: cross-pillar integration
│       ├── audits/
│       │   └── 20260315_docs_audit.md      ← MOVED: from gitignored research/
│       ├── PREDICTIONS.md                   ← canonical, 5/5 quality
│       ├── CONVERGENCE_ANALYSIS.md          ← NEW: extracted from whitepaper
│       ├── EPISTEMOLOGICAL_STATUS.md        ← cross-referenced into INDEX
│       ├── ACADEMIC_POSITIONING.md          ← cross-referenced into INDEX
│       └── DEPRECATED/
│           ├── STANDARD_MODEL_COMPLETE.md
│           ├── THEORY_COMPLETE_ALL.md
│           └── STANDARD_MODEL_THEORY_COMPLETE.md
```

---

## Execution checklist

### Phase 0 — Front door
- [x] Write `WHAT_IS_SMOC.md` (~122 lines, conceptual intro, audience routing, maturity table)
- [x] Add intro block to README.md (also fixed SMC → SMoC)

### Phase 1 — Kill monoliths
- [x] Create `particle/docs/theory/DEPRECATED/`
- [x] Move 3 monoliths to DEPRECATED/ with deprecation headers (all content preserved)
- [x] `wave/docs/theory/THEORY.md` marked SUPERSEDED, kept as narrative reading companion
- [x] `particle/docs/theory/THEORY_INDEX.md` archived to DEPRECATED/ (not deleted)
- [x] `wave/docs/theory/THEORY_INDEX.md` link updated to point to canonical INDEX.md

### Phase 2 — Ingest best artifacts
- [x] Create `whitepapers/`, `synthesis/`, `audits/` directories
- [x] Convert whitepaper .docx → `whitepapers/SMoC_WHITEPAPER.md` (236 lines, placeholders fixed)
- [x] Convert textbook .docx → `whitepapers/SMOC_TEXTBOOK_CH3.md` (1,063 lines)
- [x] Convert evidence audit .docx → `whitepapers/SMOC_EVIDENCE_AUDIT.md` (343 lines)
- [x] Copy hardened glossary .md → `whitepapers/SMOC_GLOSSARY_HARDENED.md` (242 KB)
- [x] Copy audit report → tracked `audits/20260315_docs_audit.md`
- [x] Update INDEX.md with sections 10 (whitepapers) and 11 (methodology)
- [ ] Create `frameworks/IDEOME.md` from ideome_synthesis.py + specs
- [ ] Verify GLOSSARY.yaml ↔ GLOSSARY.md parity

### Phase 3 — Concordance bugs
- [ ] Update L3_APPLICATIONS.md: document both health models, mark canonical
- [ ] Add topology shape classification to TOPOLOGY.md
- [ ] Fix L1_DEFINITIONS.md duplicate frontmatter

### Phase 4 — Audience packaging
- [ ] Add audience routing table to WHAT_IS_SMOC.md
- [ ] Cross-reference orphan docs into INDEX.md
- [ ] Create `synthesis/THREE_PILLARS.md`
- [ ] Update or rebuild docs/reader/ site

### Phase 5 — Hygiene (ongoing)
- [ ] Atlas identity blocks on framework files
- [ ] Review and deprecate wave/docs/theory/ overlap
- [ ] Consolidate glossary variants
- [ ] Cross-reference docs/essentials/ into theory tree

---

## Sequencing guidance for Claude Code agents

Each phase is designed as a standalone Claude Code session prompt:

**Session 1 (Phases 0+1):** "Create WHAT_IS_SMOC.md at repo root and deprecate the monolith theory files. Follow SMOC_CONSOLIDATION_PLAN.md Phase 0 and Phase 1 exactly."

**Session 2 (Phase 2):** "Ingest the whitepaper and textbook artifacts into the theory tree. Create IDEOME.md framework. Follow Phase 2 of the consolidation plan." (Requires the .docx files as input)

**Session 3 (Phase 3):** "Fix the health model discordance and ground topology_reasoning.py. Follow Phase 3."

**Session 4 (Phase 4):** "Package the theory for external audiences. Cross-reference orphans, create THREE_PILLARS.md, update reader site. Follow Phase 4."

---

## Success criteria

After all phases, a visitor to `github.com/leolech14/standard-model-of-code` should be able to:

1. **In 2 minutes:** Understand what SMoC is (WHAT_IS_SMOC.md)
2. **In 10 minutes:** Navigate the full theory (INDEX.md → L0–L3 → frameworks)
3. **In 30 minutes:** Assess novelty and rigor (whitepaper + PREDICTIONS.md + convergence)
4. **In 1 hour:** Form an opinion on whether to collaborate, cite, or critique

No monoliths competing for canonical status. No glossary forks. No theory-implementation discordance. One front door, one theory tree, one vocabulary.
