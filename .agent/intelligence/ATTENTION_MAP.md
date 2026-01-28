# Attention Map (Generated)

**Generated:** 2026-01-27  
**Scope:** `full_contextome.zip`

This file answers: **what deserves attention first** vs **what can be safely separated/archived**.

---

## 1) What’s actually here (by category)

| category | files | MB |
|---|---|---|
| generated_output | 383 | 1063.39 |
| doc | 1207 | 14.12 |
| archive | 301 | 11.03 |
| other | 208 | 3.69 |
| registry | 156 | 1.66 |
| spec | 64 | 0.95 |
| report_doc | 41 | 0.49 |
| research_output | 5 | 0.03 |
| cache | 2 | 0.00 |

Interpretation:
- The pack is **dominated by generated JSON outputs (~1063 MB)**.
- Human-readable docs are comparatively small (~14 MB).
- This is good news: **you can ship a coherent v1 without dragging the artifact bulk along**.

---

## 2) The “coherence” bottleneck (why it feels like a chain)

Among active markdown docs:
- Total active docs: **788**
- Internal doc links: **64**
- Isolated docs: **733**  

This means “knowledge traversal” is currently **mostly impossible** without search — you can’t *browse* the system.

---

## 3) Separation plan (what to split into Core vs Artifacts)

### Keep in Core (v1)
These are the things that create *truth* (canon) or define how truth is validated:

- **Theory + specs**
  - `standard-model-of-code/docs/**`
  - `context-management/docs/theory/**`
  - `.agent/specs/**`
- **Registries (canonical datasets)**
  - `.agent/registry/**`
  - `context-management/registry/**`
  - any `**/registry/**.yaml` or canonical JSON registries
- **Operating manuals**
  - `ARCHITECTURE_MAP.md`, `PROJECT_MAP.md`, `QUICK_START.md`, `CLAUDE.md`, `AGENTS.md`

### Split out of Core (v1) into “Artifacts”
These are valuable, but they should not block shipping:

- `standard-model-of-code/artifacts/**` (dominant size)
- `.collider-full/**`, `collider_output_small/**`, `architecture_report/**`
- `context-management/intelligence/**`
- `standard-model-of-code/docs/research/**` (Gemini/Perplexity traces)
- `archive/**` and `standard-model-of-code/.archive/**`

---

## 4) The next step that unlocks everything: build navigation

If we do only one coherence upgrade next, it should be this:

### ✅ Create a browseable index layer

**Goal:** every doc is reachable in ≤2 clicks.

Minimum implementation:
1. Root `INDEX.md` linking to the 6–10 major hubs.
2. Folder-level `README.md` / `INDEX.md` pages linking to every child doc.
3. A standard footer/header for docs:
   - Home / Up / Related / Glossary

This alone turns “chain” → “mesh”, even before we rewrite any theory.

---

## 5) Fix trust-breakers (small list, high leverage)

### A) Fix active broken links (14)
See: `BROKEN_LINKS.csv` (filter `is_archive = False`).

### B) Ensure the maps are clickable
`PROJECT_MAP.md` and `ARCHITECTURE_MAP.md` currently read like maps, but they don’t fully function like maps unless they contain **real markdown links**.

### C) Decide what is canonical (and enforce it)
Pick canonical sources for:
- pipeline stages
- atom IDs + registry
- dimension list
Then **generate** everything else.

---

## 6) If you want “theory interlinked to itself” specifically

You already have the machinery: `@SECTION`, `@DEPENDS_ON`, `@PROVIDES`.

Next:
- Generate a *Theory Section Registry* (already provided: `THEORY_SECTION_INDEX.md`, `THEORY_SECTION_REGISTRY.csv`)
- Generate a *Concept Atlas* page (concept → sections)
- Add backlinks: section → “used by” sections
- Optional: split `THEORY.md` into per-section docs (auto-generated) while keeping the narrative master doc.

---

## Where to look next
- `REPO_INDEX.md` (overview)
- `DOCS_INDEX.csv` (every markdown doc + title + link degrees)
- `DIRECTORY_STATS.csv` (what’s big / dense)
