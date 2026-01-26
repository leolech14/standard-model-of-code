# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-25 23:58:18\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

- **Entity**: `BaseStage` (src/core/pipeline/base_stage.py)
  - **Status**: **Compliant**
  - **Evidence**:
    - **Inheritance**: Defined as `class BaseStage(ABC)`, serving as the base class required by the invariants.
    - **Method Implementation**: Defines `@abstractmethod def execute(self, state: "CodebaseState") -> "CodebaseState"` matching the signature requirement.
    - **Name Property**: Defines `@property @abstractmethod def name(self) -> str` matching the requirement.
    - **Validation**: Includes `validate_input` and `validate_output` methods with default implementations (`return True`), matching the optional invariant.

- **Entity**: `PipelineManager` (src/core/pipeline/manager.py)
  - **Status**: **Compliant**
  - **Evidence**:
    - **Usage of Concept**: Constructor accepts `stages: List[BaseStage]`, enforcing that all managed stages inherit from `BaseStage`.
    - **Execution Loop**: In `run()`, it calls `stage.validate_input(state)`, `stage.execute(state)`, and `stage.validate_output(state)` in the correct order, respecting the Stage interface.
    - **Identity**: Utilizes `stage.name` for logging and lookup (`run_stage`), respecting the unique identifier invariant.

- **Entity**: `run_full_analysis` (src/core/full_analysis.py)
  - **Status**: **Deviating / Legacy**
  - **Evidence**: The function implements analysis steps procedurally using comments (e.g., `# Stage 1: Base Analysis`) and `StageTimer` context managers, rather than instantiating classes inheriting from `BaseStage`.
  - **Deviation**: While logically performing "stages", this implementation does not use the `Stage` Concept defined in the invariants. It represents a legacy or alternative execution path compared to the compliant `run_pipeline_analysis` function found in the same file.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: 'full_analysis.py' contains significant core domain logic (e.g., 'detect_js_imports', 'classify_disconnection', 'create_codome_boundaries') that belongs in the 'src.core' library (likely as Pipeline Stages or Strategies). The entry point script should merely orchestrate these components, not define them, violating separation of concerns. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia: The function 'detect_js_imports' directly accesses the file system ('open(full_path, ...)') to read content. This ignores the existing 'FileEnricher' abstraction and the 'CodebaseState' context (which likely already holds file content/AST), leading to redundant I/O and bypassing architectural data governance. (Severity: MEDIUM)\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings

- **Entity**: `PipelineManager` (Class)
- **Status**: **Compliant**
- **Evidence**:
    - **Accepts BaseStage list**: The `__init__` method signature defines `stages: List[BaseStage]` and assigns it to `self.stages`.
    - **Executes in order via run(state)**: The `run` method iterates specifically through the list (`for stage in self.stages:`) and updates the state sequentially (`state = stage.execute(state)`).
    - **Tracks timing**: The `run` method captures `start_time = time.perf_counter()` before execution and calculates `elapsed_ms` immediately after.
    - **Callbacks**: The class accepts `on_stage_start` and `on_stage_complete` in `__init__` and invokes them at the appropriate times within the execution loop.
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: The 'PipelineManager' (Core/Orchestration layer) uses raw 'print()' statements for warning logs. This violates layer boundaries by coupling core logic directly to standard output (CLI/Presentation layer) instead of using an abstract logging facility. (Severity: HIGH)\n- 🔴 **[AM004]**: Orphan Code: The 'perf_manager' dependency is injected via '__init__' and stored in 'self._perf_manager', but it is never utilized within the 'run' method or anywhere else in the class. The code manually implements timing logic that likely duplicates or ignores the intended functionality of the unused 'PerformanceManager'. (Severity: MEDIUM)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (class)
- **Status**: **Compliant**
- **Evidence**:
    - **Collections**: The class initializes `self.nodes` (Dict) and `self.edges` (List) in `__init__`.
    - **O(1) Indexed Lookups**:
        - Internal indices `_by_file`, `_by_ring`, `_by_kind`, and `_by_role` are initialized as `defaultdict(set)`.
        - Public methods `get_by_file`, `get_by_ring`, `get_by_kind`, and `get_by_role` provide O(1) access via these indices.
    - **Metadata Tracking**: `self.metadata` is initialized with `"layers_activated": []`.
    - **Enrichment**: The method `enrich_node(self, node_id: str, layer_name: str, **attributes)` is present. It merges attributes into the node dictionary and updates the `layers_activated` list in metadata.
- **Deviation**: None.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The code imports 'UnifiedNode', 'UnifiedEdge', and 'UnifiedAnalysisOutput' from 'unified_analysis' but never references them. The implementation relies entirely on generic 'Any' types and duck-typing (e.g., 'hasattr(n, ...)') rather than these imported type definitions. (Severity: MEDIUM)\n- 🔴 **[AM002]**: The import logic for 'normalize_output' utilizes a try-except fallback block ('from normalize_output' vs 'from src.core.normalize_output'). This implies an ambiguous architectural context (module vs. script execution) and violates strict module resolution standards. (Severity: MEDIUM)\n- 🔴 **[AM001]**: The 'load_initial_graph' method manually re-implements object-to-dict conversion logic using 'vars()' and attribute checks, ignoring the 'asdict' utility explicitly imported from 'dataclasses' which is designed for this standard library purpose. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings

- **Entity**: `SmartExtractor` (in `src/core/smart_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: The class explicitly defines its role as the "smart extraction layer that prepares data for the LLM classifier." It operates directly on file content (`file_path.read_text`) and AST (`ast.parse`), extracting structural elements like decorators, imports, and docstrings.
- **Reasoning**: It adheres strictly to the invariants by gathering raw data and deferring the actual classification (the "complex semantic reasoning") to an external LLM, as evidenced by the `format_card_for_llm` method and the `heuristic_type` field which acts as a placeholder or simple guess rather than a final determination.

- **Entity**: `intent_extractor.py` (Module functions: `extract_readme_intent`, `extract_commit_intents`, etc.)
- **Status**: **Compliant**
- **Evidence**: Functions operate on raw data sources: `extract_readme_intent` reads file text; `extract_commit_intents` parses raw `git log` subprocess output; `extract_docstring_intent` uses regex on source code.
- **Reasoning**: While `classify_commit_intent` performs a form of classification, it relies on simple keyword matching (e.g., `if 'fix' in message...`), which is a syntactic heuristic rather than "complex semantic reasoning." This fits the scope of extracting metadata signals from raw inputs.

- **Entity**: `EdgeExtractionStrategy` and subclasses (in `src/core/edge_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: The strategies (`PythonEdgeStrategy`, `TreeSitterEdgeStrategy`, etc.) use either regex patterns on `body_source` or `tree_sitter` AST parsing to identify relationships.
- **Reasoning**: The edge detection logic (`extract_edges`) is based on syntactic presence (calls, imports) and structural scope analysis. The resolution logic (`_find_target_particle`) uses name matching and file path heuristics, maintaining operation at the syntactic/structural level without deep semantic interpretation of the code's behavior.

- **Entity**: `JSModuleResolver` (in `src/core/edge_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: Uses `tree_sitter` to parse JavaScript/TypeScript content and traverses the AST to map imports and exports.
- **Reasoning**: It tracks variable assignments and import statements (`window.X = ...`, `require(...)`) to resolve module paths. This is a structural extraction task essential for accurate data ingestion, adhering to the requirement of operating on ASTs.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: Context Myopia Violation in `intent_extractor.py`. The function `extract_docstring_intent` uses brittle Regular Expressions to parse Python docstrings, ignoring the robust, standard `ast.get_docstring` approach already implemented and available in the sibling module `smart_extractor.py`. This unnecessarily duplicates logic and lowers reliability. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia / Structural Confusion in `edge_extractor.py`. The import block for `scope_analyzer` uses a 'shotgun' approach (nested try/except blocks attempting multiple paths), indicating the component is unaware of the project's canonical structure. It attempts to guess the location of internal dependencies rather than adhering to a defined architectural layout. (Severity: MEDIUM)\n- 🔴 **[AM004]**: Orphan/Incomplete Code in `edge_extractor.py`. The file terminates abruptly in the middle of a method signature (`resolve_member_call`), rendering the module syntax-invalid and unusable. It defines complex logic (`JSModuleResolver`) that is not fully integrated or closed. (Severity: MEDIUM)\n\n
