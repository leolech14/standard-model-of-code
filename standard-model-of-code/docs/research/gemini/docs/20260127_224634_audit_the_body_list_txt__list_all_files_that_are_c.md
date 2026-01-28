# Research: Audit the body_list.txt. List all files that are Contextome (non-executable info) but residing in th...

> **Date:** 2026-01-27 22:46:34
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:ca2c0842fdbc535dabcfe4cc931250e3e78915afe264661120828532fb54f3fc`
> **Raw JSON:** `raw/20260127_224634_audit_the_body_list_txt__list_all_files_that_are_c.json`

---

## Query

Audit the body_list.txt. List all files that are Contextome (non-executable info) but residing in the standard-model-of-code/ hemisphere. Identify the 'Purity Ratio'.

---

## Response

The `PROJECTOME_TOTALITY_REPORT.md` defines the Projectome as a disjoint union of the Codome (executable instructions) and the Contextome (non-executable information).

Based on the provided definitions:
*   **Codome (C) ["The Body"]**: All executable instructions (`.py`, `.js`, `.ts`). This category also implicitly includes build scripts (`.sh`, `Makefile`, `Dockerfile`), compiled artifacts (`.pyc`), and web interfaces (`.html`) which contain executable logic or are part of the execution environment.
*   **Contextome (X) ["The Brain"]**: All non-executable information (`.md`, `.yaml`, `.json`). This category represents the semantic information space, including theory, data definitions, governance rules, and documentation. I'll also include `.mmd` (Mermaid diagrams, visual documentation) and `.config.js` (configuration, not executable logic) as they fit the "non-executable information" criteria. I'll also include `CODEOWNERS` as a governance document.
*   **Not Contextome (other/ancillary)**: Files like `.txt`, `.ini`, `.lock`, `.toml`, `.csv`, `.in`, and packaging metadata (`.egg-info` contents) are primarily related to build systems, environment descriptions, or raw data, rather than the core "semantic information space" described for the Contextome.

The "standard-model-of-code/ hemisphere" refers to the entire repository structure provided in `body_list.txt`.

### Contextome Files in `standard-model-of-code/` Hemisphere:

Here is the list of files identified as Contextome:

1.  `standard-model-of-code/README_HANDLER_AUDIT.md`
2.  `standard-model-of-code/CHANGELOG.md`
3.  `standard-model-of-code/CODEOWNERS`
4.  `standard-model-of-code/AUDIT_INDEX.md`
5.  `standard-model-of-code/docs/MODEL.md`
6.  `standard-model-of-code/docs/RESEARCH_TO_IMPLEMENTATION_ROADMAP.md`
7.  `standard-model-of-code/docs/SPRAWL_CONSOLIDATION_PLAN.md`
8.  `standard-model-of-code/docs/COLLIDER.md`
9.  `standard-model-of-code/docs/GLOSSARY.yaml`
10. `standard-model-of-code/docs/POSSIBILITIES.md`
11. `standard-model-of-code/docs/OPEN_CONCERNS.md`
12. `standard-model-of-code/docs/validated_theory.md`
13. `standard-model-of-code/docs/validated_pipeline.md`
14. `standard-model-of-code/docs/KNOWLEDGE_TREE.md`
15. `standard-model-of-code/docs/COMPETITIVE_ANALYSIS.md`
16. `standard-model-of-code/docs/THEORY_EXPANSION_2026.md`
17. `standard-model-of-code/docs/README.md`
18. `standard-model-of-code/docs/PURPOSE_INTELLIGENCE.md`
19. `standard-model-of-code/docs/ORPHANED_CONTROLS_ROADMAP.md`
20. `standard-model-of-code/docs/ORPHANED_CONTROLS_INDEX.md`
21. `standard-model-of-code/docs/SESSION_CONCERNS_20260125.md`
22. `standard-model-of-code/docs/RESEARCH_DIRECTIONS.md`
23. `standard-model-of-code/CONTROL_HANDLER_MAPPING.md`
24. `standard-model-of-code/README.md`
25. `standard-model-of-code/schema/MARKERS.md`
26. `standard-model-of-code/schema/constants.yaml`
27. `standard-model-of-code/schema/graph.schema.json`
28. `standard-model-of-code/schema/antimatter_laws.yaml`
29. `standard-model-of-code/schema/README.md`
30. `standard-model-of-code/schema/particle.schema.json`
31. `standard-model-of-code/ROADMAP.md`
32. `standard-model-of-code/CONTRIBUTING.md`
33. `standard-model-of-code/graph TD4.mmd`
34. `standard-model-of-code/collider_pipeline.md`
35. `standard-model-of-code/commitlint.config.js`
36. `standard-model-of-code/data/LAW_11_CANONICAL.json`
37. `standard-model-of-code/data/OUTPUT_SCHEMA.json`
38. `standard-model-of-code/data/system_status.json`
39. `standard-model-of-code/data/1440_summary.json`
40. `standard-model-of-code/data/pattern_registry.json`
41. `standard-model-of-code/ARIADNES_THREAD.md`
42. `standard-model-of-code/CLAUDE.md`
43. `standard-model-of-code/collider_pipeline.mmd`
44. `standard-model-of-code/HANDLER_COVERAGE_CORRECTED.md`
45. `standard-model-of-code/HANDLER_WIRING_AUDIT.md`

**Total Contextome Files: 45**

### Purity Ratio Calculation:

1.  **Count of Contextome Files:** 45
2.  **Total Files (excluding directories):**
    By analyzing `body_list.txt` and filtering out entries ending with `/` (which denote directories), there are **120** files in total.

3.  **Purity Ratio:**
    Purity Ratio = (Number of Contextome Files) / (Total Files)
    Purity Ratio = 45 / 120 = 0.375

### Conclusion:

The audit reveals **45** Contextome files residing directly within the `standard-model-of-code/` hemisphere. The **Purity Ratio** of Contextome files to total files in this part of the codebase is **0.375** (or 37.5%). This indicates that approximately 37.5% of the codebase's file "particles" represent non-executable semantic information, aligning with the "Brain" component of the Projectome. The remaining files primarily constitute the "Body" (Codome) or ancillary configuration/build artifacts.

---

## Citations

_No citations provided_
