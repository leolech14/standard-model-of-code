# Research: Count the EXACT number of pipeline stages defined in this file. List each stage name. This is to res...

> **Date:** 2026-01-27 23:31:09
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:7ddebdf9b2005eaa22bde65bc5de56e220c33bbeaa8ec8057ab2ec50b7dc0dc7`
> **Raw JSON:** `raw/20260127_233109_count_the_exact_number_of_pipeline_stages_defined.json`

---

## Query

Count the EXACT number of pipeline stages defined in this file. List each stage name. This is to resolve count drift: PIPELINE_STAGES.md claims 28 stages, REGISTRY_OF_REGISTRIES.md claims 18 stages. The code is the canonical source of truth. What is the REAL count?

---

## Response

Based on the provided codebase context, specifically the `particle/src/core/pipeline/stages/__init__.py` file, the REAL, exact number of pipeline stages defined is **28**.

This count is consistently supported by:
1.  The introductory comment: "28 stages organized into 5 phases".
2.  The number of unique stage classes imported.
3.  The number of class names listed in the `__all__` variable.
4.  The number of stage identifiers listed in the `STAGE_ORDER` list (which contains 28 entries, despite its own comment claiming 27).

Here is the list of each stage name, derived from the `__all__` list and the import statements, which correspond to the defined stage classes:

**Pipeline Stages (28 total):**

**Phase 1: Extraction**
1.  SurveyStage
2.  BaseAnalysisStage
3.  StandardModelStage

**Phase 2: Enrichment**
4.  EcosystemDiscoveryStage
5.  DimensionClassificationStage
6.  ScopeAnalysisStage
7.  ControlFlowStage
8.  PatternDetectionStage
9.  DataFlowAnalysisStage

**Phase 3: Analysis**
10. PurposeFieldStage
11. OrganellePurposeStage
12. SystemPurposeStage
13. EdgeExtractionStage
14. MarkovMatrixStage
15. KnotDetectionStage
16. GraphAnalyticsStage
17. StatisticalMetricsStage
18. CodomeBoundaryStage

**Phase 4: Intelligence**
19. DataFlowMacroStage
20. PerformancePredictionStage
21. ConstraintValidationStage
22. PurposeIntelligenceStage

**Phase 5: Output**
23. RoadmapEvaluationStage
24. TopologyReasoningStage
25. SemanticCortexStage
26. AIInsightsStage
27. ManifestWriterStage
28. OutputGenerationStage

---

## Citations

_No citations provided_
