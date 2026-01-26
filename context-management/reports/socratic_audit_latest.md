# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-26 03:58:12\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

- **Entity**: `src/core/full_analysis.py` (File Content)
- **Status**: **No Compliant Entities Found**
- **Evidence**: The file consists entirely of function definitions (`classify_disconnection`, `detect_js_imports`, `run_full_analysis`, etc.) and lacks any class definitions.
- **Deviation**: The Semantic Definition for **Concept: Stage** requires a class structure inheriting from `BaseStage` with specific methods (`execute`, `name`). This file implements analysis logic using procedural functions and a monolithic orchestration function (`run_full_analysis`), which conceptually groups logic into "Stages" (via `StageTimer`) but strictly violates the object-oriented invariants of the Stage concept. The file acts as a consumer/orchestrator rather than a definition provider for Stages. `run_pipeline_analysis` correctly consumes compliant stages defined elsewhere (`src.core.pipeline`), but `run_full_analysis` represents a legacy/procedural implementation that does not adhere to the Stage architecture.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: The module 'full_analysis.py' (Analysis Layer) violates layer boundaries by performing direct File I/O and raw source code parsing in functions 'detect_js_imports' and 'detect_class_instantiation'. Extraction logic belongs in the ingestion/enrichment layer (e.g., 'FileEnricher' or 'IntentExtractor'), not intertwined with graph topology analysis. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia: The code implements ad-hoc, brittle regex patterns for detecting JS imports, Python class instantiations, and framework roles (e.g., hardcoded lists in 'classify_disconnection'). This likely ignores or duplicates more robust parsing logic available in 'src.core.intent_extractor' or the broader project infrastructure. (Severity: MEDIUM)\n- 🔴 **[AM004]**: Orphan/Incomplete Code: The file is truncated at line 578 inside 'compute_data_flow', resulting in a syntax error and incomplete functionality. Additionally, private utilities like '_open_file' likely duplicate existing project-level OS helpers. (Severity: LOW)\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings

- **Entity**: `PipelineManager` (class)
- **Status**: **Compliant**
- **Evidence**:
    1.  **Accepts List of Stages**: The `__init__` method accepts `stages: List[BaseStage]` (Line 29).
    2.  **Sequential Execution via run(state)**: The `run` method iterates through `self.stages` and calls `state = stage.execute(state)` sequentially (Lines 47, 57, 68).
    3.  **Tracks Timing**: The `run` method measures execution time using `time.perf_counter()` before and after execution to calculate `elapsed_ms` (Lines 67-69).
    4.  **Callbacks**: The class accepts `on_stage_start` and `on_stage_complete` in `__init__` and invokes them within the execution loop (Lines 59-60, 76-77).
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift detected in `run_stage`: This method executes a stage directly (`stage.execute(state)`), bypassing the critical lifecycle safeguards established in the main `run` loop (input/output validation, timing metrics, and observability callbacks). This undermines the Manager's role as a consistent orchestrator. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia detected regarding observability. The code relies on raw `print()` statements for warnings (`[Pipeline] WARN...`) within a core framework component. In a project with a dedicated `observability` module and `PerformanceManager`, this ignores established logging patterns and structural context. (Severity: MEDIUM)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (class)
- **Status**: **Compliant**
- **Evidence**:
    - **Nodes/Edges Collections**: The class initializes `self.nodes` and `self.edges` in `__init__` and populates them in `load_initial_graph`.
    - **O(1) Indexed Lookups**: The class maintains internal hash maps (`_by_file`, `_by_ring`, `_by_kind`, `_by_role`) and exposes corresponding accessor methods (`get_by_file`, `get_by_ring`, etc.) that utilize these maps for O(1) retrieval.
    - **Metadata Tracking**: The `__init__` method initializes `self.metadata` with `"layers_activated": []`.
    - **Enrichment**: The method `enrich_node(self, node_id, layer_name, **attributes)` is present, merges attributes into the node, and updates `self.metadata["layers_activated"]`.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift / Layer Violation: The Core Data Layer (`CodebaseState`) imports logic (`is_confidence_key`) from `normalize_output`. This creates an inverted dependency where the foundational data model depends on an output/formatting utility to define its schema validation logic. (Severity: HIGH)\n- 🔴 **[AM004]**: Orphan Code (Unused Imports): The symbols `UnifiedNode`, `UnifiedEdge`, and `UnifiedAnalysisOutput` are imported from `unified_analysis` but never referenced in the class or functions. This creates unnecessary coupling to the analysis layer. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia (Brittle Imports): The `try-except` block for importing `normalize_output` attempts to handle execution context manually (script vs. module), ignoring standard project structure and environment configuration. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings

- **Entity**: `EdgeExtractionStrategy` (and subclasses `PythonEdgeStrategy`, `JavascriptEdgeStrategy`, `TreeSitterEdgeStrategy`, etc.)
  - **Status**: Compliant
  - **Evidence**: The strategies operate directly on `body_source` (raw string) or parse it into an AST (using Tree-sitter) to identify patterns like function calls or attribute access.
  - **Reasoning**: This adheres to the invariant of operating on raw file content/AST. The strategies extract syntactic relationships without attempting to re-classify the nature of the particles themselves (preserving the Classifier separation).

- **Entity**: `JSModuleResolver`
  - **Status**: Compliant
  - **Evidence**: The resolver ingests `raw_content` from files or AST results (`analyze_file`) to map `window` exports, `require` statements, and imports.
  - **Reasoning**: It performs raw data ingestion to determine module structure and aliases, strictly for resolution purposes, avoiding higher-level semantic classification.

- **Entity**: `extract_call_edges`
  - **Status**: Compliant
  - **Evidence**: This orchestrator combines raw import data (`results`) with raw body analysis (via strategies) to generate edges.
  - **Reasoning**: While it consumes `particles` (output of a Classifier), it treats them as nodes and returns to their raw `body_source` to extract the edges, ensuring the extraction logic remains grounded in raw content analysis rather than derived metadata.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n\n
