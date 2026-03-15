# SMoC Documentation Pre-Audit Snapshot
# Date: 2026-03-15 | Executor: Claude Code (Opus 4.6)

## File inventory: 277 files across 15 directories
## Proposed structure (March 5 DOCS_STRUCTURE_AUDIT): PARTIALLY IMPLEMENTED
## — foundations/ (4 files): implemented. frameworks/ (9 files): implemented.
## — synthesis/: MISSING (empty). whitepapers/: MISSING (empty).

## Files with identity blocks (frontmatter): 3 of 40 theory files (L0, PURPOSE_SPACE, STANDARD_MODEL_COMPLETE)
## Files with TODO/placeholder content: ~10 estimated (synthesis/, whitepapers/ dirs empty; several specs stale)
## Files that are compiled artifacts (load every session): INDEX.md, GLOSSARY.yaml, STANDARD_MODEL_COMPLETE.md
## Files that are source reasoning (load on demand): remaining 37 theory files, 45 specs, 121 core docs

## Glossary: PRESENT | Format: YAML | Term count: ~3646 lines (~500+ terms)
## Prior Perplexity research: PRESENT | 21 files | Topics: ML code analysis, semantic analysis, knowledge graphs, UI abstraction, music theory, consonance, cymatics, Claude Code, git sanitization, color schemas
## Estimated token cost of all theory docs: 170,281 tokens (17% of 1M context — TOO LARGE to always-load)

## Scaffold compliance assessment:
## - Identity protocol: NONE (no files use atlas entity_identity format; 3 have ad-hoc frontmatter)
## - Sparse encoding: PARTIAL (foundations are focused; monoliths like STANDARD_MODEL_COMPLETE are 10K+ lines)
## - Progressive disclosure: PARTIAL (INDEX.md is excellent; individual files lack L0 orientation headers)
## - Dependency graph: PARTIALLY EXPLICIT (INDEX.md has DAG; cross-references use relative paths, not IDs)

## Top 3 gaps the audit should focus on:
## 1. Two competing health models: incoherence.py (5-term) vs L3_APPLICATIONS.md (4-term) — which is canonical?
## 2. Three monolith docs claiming canonical status (STANDARD_MODEL_COMPLETE, THEORY_COMPLETE_ALL, THEORY_AXIOMS) — consolidate or deprecate
## 3. Zero atlas-style identity blocks — theory docs are invisible to the scaffold (no CMP-IDs, no stage, no purpose field)
