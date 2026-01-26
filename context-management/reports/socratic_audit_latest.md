# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-26 01:28:49\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\nBased on the provided codebase context and the Semantic Definition of the **Stage** concept, here is the audit report.

### Findings

- **Entity**: `BaseStage` (`src/core/pipeline/base_stage.py`)
  - **Status**: **Compliant**
  - **Evidence**:
    - **Inheritance**: Defined as `class BaseStage(ABC)`, serving as the root for the inheritance invariant.
    - **Execute Method**: Defines `@abstractmethod def execute(self, state: "CodebaseState") -> "CodebaseState":`, enforcing implementation in subclasses.
    - **Name Property**: Defines `@property @abstractmethod def name(self) -> str:`, enforcing unique identifiers.
    - **Validation**: Implements `validate_input` and `validate_output` with default returns of `True`, matching the invariant "May implement...".
    - **Statelessness**: The class definition contains no instance state storage mechanisms, encouraging stateless usage.

- **Entity**: `PipelineManager` (`src/core/pipeline/manager.py`)
  - **Status**: **Compliant** (as Orchestrator)
  - **Evidence**:
    - The manager correctly respects the Stage contract invariants during execution.
    - It calls `stage.validate_input(state)` before execution.
    - It calls `stage.execute(state)` to process the state.
    - It calls `stage.validate_output(state)` after execution.
    - It uses `stage.name` for logging and identification.

- **Entity**: `run_full_analysis` logic (`src/core/full_analysis.py`)
  - **Status**: **Non-Compliant** (Legacy Pattern)
  - **Deviation**: This function implements analysis steps (e.g., `Stage 0: Survey`, `Stage 1: Base Analysis`) procedurally using imperative function calls and `StageTimer`, rather than instantiating classes inheriting from `BaseStage`.
  - **Evidence**: Usage of `with StageTimer(perf_manager, "Stage 1: Base Analysis")` instead of `BaseStage` objects.
  - **Note**: The file also contains `run_pipeline_analysis`, which appears to be the modern entry point utilizing the compliant `BaseStage` architecture via `create_default_pipeline`. The legacy function represents a deviation from the defined Stage architecture but co-exists with the new implementation.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: 'full_analysis.py' acts as a 'God Script', implementing core domain logic (e.g., 'create_codome_boundaries', 'classify_disconnection') as procedural functions. This violates the explicit architectural contract defined in 'base_stage.py' and 'manager.py', which mandates that analysis logic be encapsulated in 'BaseStage' subclasses and orchestrated by the 'PipelineManager'. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia: The functions 'detect_js_imports' and 'detect_class_instantiation' implement ad-hoc regex-based parsing within the entry script. This duplicates and ignores the likely existence of robust AST-based extractors in the referenced 'src.core.graph_framework' or 'edge_extractor.py', creating fragile, redundant logic outside the established 'Standard Model' context. (Severity: MEDIUM)\n- 🔴 **[AM004]**: Orphan Code (Logical): 'classify_disconnection' is defined as a standalone utility but not integrated into the visible flow of 'create_codome_boundaries' (which expects 'disconnection' data to already exist on nodes). Without being part of a unified Stage execution, this logic is architecturally disconnected. (Severity: LOW)\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings
- **Entity**: `PipelineManager`
- **Status**: **Compliant**
- **Evidence**:
  - **Accepts BaseStage list**: The `__init__` method signature specifies `stages: List[BaseStage]`.
  - **Executes in order via run(state)**: The `run` method iterates through `self.stages` sequentially (`for stage in self.stages:`) and calls `stage.execute(state)`.
  - **Tracks timing**: Inside the `run` loop, the code captures `start_time = time.perf_counter()` before execution and calculates `elapsed_ms` immediately after.
  - **Callbacks**: The class accepts `on_stage_start` and `on_stage_complete` in `__init__` and invokes them at the appropriate times within the `run` loop.
- **Deviation**: N/A\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift (Layer Violation): The code utilizes `print()` statements within `src/core`, violating the separation of concerns between Domain Logic and the Presentation/Logging layer. Core components should emit events or use a logger, not write to stdout. (Severity: HIGH)\n- 🔴 **[AM004]**: Orphan Code (Unused Dependency): The `perf_manager` instance is injected via `__init__` and stored in `self._perf_manager`, but it is never referenced or used in `run()` or `run_stage()`, rendering it dead state. (Severity: MEDIUM)\n- 🔴 **[AM002]**: Architectural Drift (Inconsistent Role): The `run_stage` method directly calls `stage.execute()`, bypassing the validation checks (`validate_input`/`validate_output`) and observability hooks (`on_stage_start`/`complete`) that define the Manager's primary role, leading to unsafe execution paths. (Severity: MEDIUM)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (class in `src/core/data_management.py`)
- **Status**: **Compliant**
- **Evidence**:
  - **Nodes/Edges Collections**: The class initializes `self.nodes` (Dict) and `self.edges` (List) in `__init__`.
  - **O(1) Indexed Lookups**: The class maintains internal indices (`self._by_file`, `self._by_ring`, `self._by_kind`, `self._by_role`) which are populated in `load_initial_graph`. It provides accessor methods (`get_by_file`, `get_by_ring`, etc.) performing direct dictionary lookups.
  - **Metadata Tracking**: `self.metadata` is initialized with `"layers_activated": []` in the constructor.
  - **Enrichment**: The method `enrich_node(self, node_id: str, layer_name: str, **attributes)` is implemented to merge attributes into nodes and update the `layers_activated` metadata.
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: The code imports 'asdict' from 'dataclasses' but ignores it in 'load_initial_graph', instead implementing a manual, fragile object-to-dict conversion strategy using 'hasattr' and 'vars'. This duplicates standard library functionality that was explicitly imported for this purpose. (Severity: MEDIUM)\n- 🔴 **[AM004]**: The classes 'UnifiedNode', 'UnifiedEdge', and 'UnifiedAnalysisOutput' are imported from 'unified_analysis' but never referenced in the code, creating orphan dependencies and suggesting a disconnect between the data management layer and the type definitions it is supposed to manage. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings
- **Entity**: `SmartExtractor` (in `src/core/smart_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: The class methods `_enrich_from_source` and `_enrich_from_ast` operate directly on file content using `pathlib.read_text` and the `ast` module. The docstring defines its role as the "smart extraction layer that prepares data for the LLM classifier."
- **Reasoning**: It adheres to the invariants by processing raw code/AST to package context (decorators, signatures, imports) without performing the classification itself. The `_infer_layer` method uses simple string matching against file paths, which counts as heuristic extraction rather than complex semantic reasoning.

- **Entity**: `IntentExtractor` (functions in `src/core/intent_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: Functions like `extract_readme_intent`, `extract_commit_intents`, and `extract_docstring_intent` ingest raw data via file I/O, `subprocess` (git), and Regex.
- **Reasoning**: Although it contains a function named `classify_commit_intent`, the implementation relies on simple keyword lookup (e.g., if 'fix' in message), which is a mechanical extraction of metadata, not complex semantic reasoning.

- **Entity**: `EdgeExtractor` (strategies in `src/core/edge_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: The strategies (`PythonEdgeStrategy`, `TreeSitterEdgeStrategy`, etc.) and `JSModuleResolver` utilize Regex and Tree-sitter parsers to identify syntactic relationships (imports, calls).
- **Reasoning**: The component focuses strictly on ingesting raw source to map structural dependencies. It resolves scopes and symbols based on syntax, avoiding any high-level semantic inference about the code's purpose.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: Context Myopia: The component implements a Python-exclusive extraction strategy (using the `ast` module) while the surrounding project context (`edge_extractor.py`) explicitly supports a polyglot environment (JavaScript/TypeScript via Tree-sitter). This extractor will silently fail to provide 'smart' features for any non-Python nodes in the graph, contradicting its generic role description. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia (Logic Duplication): The code re-implements docstring extraction logic (in `_enrich_from_ast`) which already exists in `intent_extractor.py`. It also hardcodes `LAYER_PATTERNS`, ignoring potential project-wide configuration or shared constants that would govern architectural layering definitions. (Severity: MEDIUM)\n\n
