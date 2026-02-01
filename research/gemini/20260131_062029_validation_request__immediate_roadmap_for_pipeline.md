# Research: VALIDATION REQUEST: Immediate Roadmap for Pipeline Activation

I've completed discovery and found th...

> **Date:** 2026-01-31 06:20:29
> **Source:** gemini
> **Model:** gemini-2.5-flash
> **Checksum:** `sha256:c923509e77f98e23cc42dcb900d58fccf0201cf0cd1936ba3813bb33f78f8ae1`
> **Raw JSON:** `raw/20260131_062029_validation_request__immediate_roadmap_for_pipeline.json`

---

## Query

VALIDATION REQUEST: Immediate Roadmap for Pipeline Activation

I've completed discovery and found these specific gaps:

CONFIRMED WORKING (27 stages exist):
- 28 BaseStage files in pipeline/stages/
- create_full_pipeline() instantiates 26 stages
- All stages are proper wrappers (delegate to core modules)
- PipelineManager with events, timing, validation exists

SPECIFIC GAPS FOUND:

1. ManifestWriterStage: EXISTS as file (manifest_writer.py) but NOT in 
   create_full_pipeline()'s all_stages dict. It's in STAGE_ORDER but not instantiated.

2. ExecutionFlowStage: Core module exists (execution_flow.py) but NO stage wrapper.
   Monolith has Stage 4: Execution Flow.

3. IGTMetricsStage: Core module exists (igt_metrics.py) but NO stage wrapper.
   Monolith has Stage 13: IGT Metrics.

QUESTION: What is the immediate roadmap to activate the pipeline?

Steps I propose:
1. Add ManifestWriterStage to create_full_pipeline() all_stages dict
2. Create ExecutionFlowStage wrapper (simple - just import and call)
3. Create IGTMetricsStage wrapper (simple - just import and call)
4. Update cli.py to call run_pipeline_analysis()
5. Run regression test comparing outputs

Is this correct? What am I missing?

---

## Response

This is an excellent analysis! You've clearly identified the existing components and the specific gaps that need to be addressed to transition from the "monolith" `run_full_analysis` function to the new `PipelineManager` architecture.

Your proposed steps are largely correct and hit the immediate requirements for activating the pipeline. However, there's one critical missing piece in your proposed roadmap that needs to be addressed for the actual transition.

Let's break down your assessment:

---

### Your Confirmed Working Points:

*   **"28 BaseStage files in pipeline/stages/"**: Great, this means the modularization work is well underway.
*   **"create_full_pipeline() instantiates 26 stages"**: Good, indicates the central pipeline configuration is mostly set.
*   **"All stages are proper wrappers (delegate to core modules)"**: Excellent, this confirms they're following the `BaseStage` pattern.
*   **"PipelineManager with events, timing, validation exists"**: This means the orchestration layer is ready to go.

These points indicate a solid foundation for the pipeline.

---

### Your Specific Gaps Found:

1.  **ManifestWriterStage:** Correct. If the file exists and is meant to be part of the pipeline, it needs to be included in the `create_default_pipeline()`'s `all_stages` dict and `STAGE_ORDER`.
2.  **ExecutionFlowStage:** Correct. The core logic `detect_execution_flow` exists, but needs a `BaseStage` wrapper to be callable by the `PipelineManager`.
3.  **IGTMetricsStage:** Correct. Similarly, the IGT metrics (likely from `StabilityCalculator`, `OrphanClassifier`) need a `BaseStage` wrapper.

---

### Validation of Your Proposed Roadmap:

1.  **"Add ManifestWriterStage to create_full_pipeline() all_stages dict"**: **Correct and essential.**
2.  **"Create ExecutionFlowStage wrapper (simple - just import and call)"**: **Correct and essential.**
3.  **"Create IGTMetricsStage wrapper (simple - just import and call)"**: **Correct and essential.**
4.  **"Update cli.py to call run_pipeline_analysis()"**: **Partially correct, but there's a more immediate and significant step within `full_analysis.py` itself.** `cli.py` would ideally call `full_analysis.py` (the existing entry point), which *then* needs to switch to calling `run_pipeline_analysis`.
5.  **"Run regression test comparing outputs"**: **Absolutely correct and critical.** This is the final verification step to ensure the pipeline produces identical (or improved) results compared to the monolithic approach.

---

### The Critical Missing Piece: Refactoring `run_full_analysis()`

The biggest missing piece is that the current `run_full_analysis` function in `full_analysis.py` (the file you provided) *does not* actually call `run_pipeline_analysis()`.

Instead, `run_full_analysis()` contains a *very long, sequential list* of direct calls to analysis modules (e.g., `enrich_with_standard_model`, `detect_purpose_field`, `compute_markov_matrix`, `detect_knots`, etc.). This is your "monolith".

The `run_pipeline_analysis()` function you noted is a *separate* function in `full_analysis.py` that *would* orchestrate the new pipeline, but `run_full_analysis()` isn't calling it.

**Therefore, the immediate roadmap must include:**

**0. Refactor `run_full_analysis()` to use the pipeline.**
    *   This means stripping out all the individual stage calls within `run_full_analysis()`.
    *   Replace them with a single call to `state = run_pipeline_analysis(target_path, options)`.
    *   Then, adapt the *post-pipeline processing* in `run_full_analysis` (like `build_file_index`, `generate_brain_download`, `_generate_ai_insights`, and `generate_outputs`) to work with the `CodebaseState` object returned by `run_pipeline_analysis`. You'll need to construct the `full_output` dictionary from the `CodebaseState` (e.g., `state.nodes`, `state.edges`, `state.metadata`, `state.kpis`, etc.).

---

### Other Considerations for a Smooth Transition:

Beyond the immediate activation, here are additional points to consider for a complete and robust migration:

1.  **Comprehensive Stage Coverage**: Go through `run_full_analysis()` line by line and ensure *every single analysis step* performed there is either:
    *   Wrapped in an existing or new `BaseStage` (e.g., `_calculate_theory_completeness`, `compute_markov_matrix`, `detect_knots`, `compute_data_flow`, `_calculate_theory_completeness` which is a post-processing calculation, `build_pipeline_snapshot`).
    *   Confirmed as a post-processing/reporting step that takes the `CodebaseState` or final `full_output` dictionary (e.g., `build_file_index`, `generate_brain_download`).
    *   The specialized `classify_disconnection` is a helper function that `CodomeBoundaryGeneration` (or similar stage) will use internally.
    *   The `calculate_merkle_root` and `generate_refinery_signature` are for provenance and are used within `ManifestWriterStage` and `_emit_waybills` (a post-pipeline loop).

2.  **`CodebaseState` Adaptation**: Each new `BaseStage` wrapper will need to correctly interact with the `CodebaseState` object:
    *   Reading inputs (e.g., `state.nodes`, `state.edges`).
    *   Performing transformations.
    *   Updating the `state` object (e.g., `state.nodes = new_nodes`, `state.edges.extend(new_edges)`, `state.kpis['new_metric'] = value`).

3.  **Performance Manager Integration**: `run_pipeline_analysis` already handles `PerformanceManager` orchestration. Ensure that any new `BaseStage`s correctly use the `self.start_timer()` and `self.stop_timer()` methods (or are structured so `PipelineManager` automatically times them). Remove the manual `StageTimer` blocks from `run_full_analysis` as it transitions.

4.  **`_emit_file_nodes` Handling**: This function from `unified_analysis.py` emits file-level nodes. If `unified_analysis.analyze()` is designed as a single pipeline stage, then `_emit_file_nodes` would be an internal part of that stage. If `unified_analysis` is broken down further, then `_emit_file_nodes` might become its own, very early `BaseStage`.

5.  **Output Aggregation (The `full_output` Dict)**: `run_pipeline_analysis` returns a `CodebaseState`. The current `full_analysis.py` then builds a large `full_output` dictionary which includes *all* the various metrics and results. This aggregation logic needs to be moved *after* `run_pipeline_analysis` completes, populating `full_output` from the `CodebaseState` attributes (e.g., `state.kpis`, `state.metadata['analytics']`, etc.).

6.  **Error Handling & Logging**: Ensure that error handling in the new stages is consistent and that logging provides clear visibility into pipeline execution, especially for debugging during the transition.

7.  **`--ai-insights` Integration**: The `_generate_ai_insights` call needs the `full_output` dictionary. This step should be called after the pipeline runs and the `full_output` dictionary is constructed from `CodebaseState`.

---

### Revised Immediate Roadmap for Pipeline Activation:

1.  **Refactor `run_full_analysis()` in `full_analysis.py`**:
    *   Remove all direct calls to individual analysis modules.
    *   Add `from .pipeline import run_pipeline_analysis` (if not already there).
    *   Replace the core analysis loop with `state = run_pipeline_analysis(target_path, options)`.
    *   Adapt all subsequent post-processing (e.g., `build_file_index`, `_generate_ai_insights`, `generate_outputs`) to consume data from the returned `CodebaseState` object and construct the final `full_output` dict.

2.  **Add `ManifestWriterStage`**:
    *   Ensure `manifest_writer.py` contains a `ManifestWriterStage` class inheriting from `BaseStage`.
    *   Add `ManifestWriterStage` to the `create_default_pipeline()`'s `all_stages` dict and `STAGE_ORDER` list.

3.  **Create `ExecutionFlowStage` Wrapper**:
    *   Create a new file (e.g., `pipeline/stages/execution_flow_stage.py`).
    *   Define `ExecutionFlowStage` inheriting `BaseStage`, importing `detect_execution_flow`, and calling it within its `run()` method, updating the `CodebaseState`.
    *   Add `ExecutionFlowStage` to the `create_default_pipeline()`'s `all_stages` dict and `STAGE_ORDER` list.

4.  **Create `IGTMetricsStage` Wrapper**:
    *   Create a new file (e.g., `pipeline/stages/igt_metrics_stage.py`).
    *   Define `IGTMetricsStage` inheriting `BaseStage`, importing `StabilityCalculator` and `OrphanClassifier`, and calling their relevant methods within `run()`, updating the `CodebaseState`.
    *   Add `IGTMetricsStage` to the `create_default_pipeline()`'s `all_stages` dict and `STAGE_ORDER` list.

5.  **Run Comprehensive Regression Tests**: Compare the `output_llm-oriented_<project>_<timestamp>.json` and `output_human-readable_<project>_<timestamp>.html` from the new pipeline-driven `full_analysis.py` against the outputs from the monolithic version (before step 1).

This revised roadmap ensures that `full_analysis.py` correctly uses the new pipeline architecture, rather than just having the pipeline available in parallel. Good luck!

---

## Citations

_No citations provided_
