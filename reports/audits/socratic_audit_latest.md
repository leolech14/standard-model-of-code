# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-31 20:18:12\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

- **Entity**: `src/core/full_analysis.py` (File/Module)
- **Status**: **Non-Compliant**
- **Evidence**: The file acts as a procedural orchestrator and contains no class definitions.
- **Deviation**: No classes inheriting from `BaseStage` are defined in this file. The concept of "Stage" is implemented procedurally within `run_full_analysis` rather than as object-oriented units, violating the invariant "Must inherit from BaseStage".

- **Entity**: "Stage 0: Survey" (Logic block in `run_full_analysis`)
- **Status**: **Non-Compliant**
- **Evidence**: `print("\n🔍 Stage 0: Survey (Pre-Analysis Intelligence)...")` (Line 926)
- **Deviation**: Implemented as a procedural code block using `StageTimer`. Fails to inherit from `BaseStage`. Does not implement `execute(state: CodebaseState)`. Manipulates local variables rather than a unified `CodebaseState`.

- **Entity**: "Stage 0.5: Incremental Detection" (Logic block in `run_full_analysis`)
- **Status**: **Non-Compliant**
- **Evidence**: `print("\n⚡ Stage 0.5: Incremental Detection...")` (Line 956)
- **Deviation**: Implemented as a procedural code block. Fails invariants: Not a class, no `BaseStage` inheritance, no `execute` method.

- **Entity**: "Stage 1: Base Analysis" (Logic block in `run_full_analysis`)
- **Status**: **Non-Compliant**
- **Evidence**: `print("\n🔬 Stage 1: Base Analysis...")` (Line 985)
- **Deviation**: Implemented as a procedural code block calling `unified_analysis.analyze`. Fails invariants: Not a class, no `BaseStage` inheritance. Uses loose variables (`nodes`, `edges`) instead of `CodebaseState`.

- **Entity**: "Stage 2: Standard Model Enrichment" (Logic block in `run_full_analysis`)
- **Status**: **Non-Compliant**
- **Evidence**: `print("\n🧬 Stage 2: Standard Model Enrichment...")` (Line 1003)
- **Deviation**: Implemented as a procedural code block. Fails invariants: Not a class, no `BaseStage` inheritance.

- **Entity**: `run_pipeline_analysis` (Function)
- **Status**: **Compliant Usage**
- **Evidence**: `def run_pipeline_analysis... state = pipeline.run(state)`
- **Deviation**: None. This function correctly orchestrates the concept by delegating to `pipeline` and `CodebaseState`, although it does not define a Stage itself. It represents the correct architectural direction compared to `run_full_analysis`.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: The module 'src/core/full_analysis.py' violates the boundary between Core Domain logic and Presentation/System Interface. Functions `_open_file` and `_manual_open_command` invoke OS-specific UI commands (`open`, `xdg-open`, `start`) to launch web browsers. Core analysis logic must remain headless and platform-agnostic; report visualization concerns belong in the CLI wrapper, not the analysis kernel. (Severity: HIGH)\n- 🔴 **[AM001]**: Context Myopia (Redundancy): The function `detect_js_imports` performs local imports (`import re`, `from pathlib import Path`) that are either standard or already imported at the top level (`Path`). This suggests code was copy-pasted from another context without integration into the current module's scope, creating unnecessary local coupling and noise. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia (Hardcoded Taxonomy): The `classify_disconnection` function hardcodes extensive lists of framework-specific strings (e.g., '@injectable', 'spec.js', '.vue'). This taxonomy logic is tightly coupled to the orchestration script. This knowledge constitutes a domain rule set that should be encapsulated in `src.core.intent_extractor` or an external configuration, rather than creating a 'God Method' inside the analysis runner. (Severity: MEDIUM)\n- 🔴 **[AM004]**: Orphan/Incomplete Code: The file terminates abruptly at `def find_cycle(no`, rendering the code syntactically invalid and the logic for `detect_knots` incomplete. This renders the analysis engine incapable of execution. (Severity: HIGH)\n\n## Concept: PipelineManager\n> Orchestrator that executes stages in sequence with timing.\n\n### Findings

- **Entity**: `PipelineManager`
- **Status**: **Compliant**
- **Evidence**:
  - **Invariants Check**:
    - **Must accept a list of BaseStage instances**: The `__init__` method defines `stages: List[BaseStage]`.
    - **Must execute stages in order via run(state) method**: The `run` method iterates `for stage in self.stages:` and updates the state sequentially (`state = stage.execute(state)`).
    - **Must track timing per stage**: The `run` method captures `start_time = time.perf_counter()` before execution and calculates `elapsed_ms` immediately after execution.
    - **May provide stage-start and stage-complete callbacks**: The class accepts `on_stage_start` and `on_stage_complete` in `__init__` and invokes them inside `run` if they exist (`self._on_stage_start(stage)`, `self._on_stage_complete(stage, elapsed_ms)`).\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: The code uses raw 'print' statements for warnings (lines 104, 119) instead of utilizing a project-level logging infrastructure or the provided 'hub' reference, ignoring the broader observability context. (Severity: MEDIUM)\n- 🔴 **[AM004]**: The 'perf_manager' dependency is injected in __init__ and stored in 'self._perf_manager', but it is never utilized in the 'run' method or anywhere else; the code instead re-implements manual timing logic. (Severity: HIGH)\n- 🔴 **[AM002]**: The 'run_stage' method allows execution of a stage while bypassing the validation, event emission, and timing logic established in the 'run' method, drifting from the Manager's responsibility to enforce pipeline consistency. (Severity: LOW)\n\n## Concept: CodebaseState\n> Central state container passed between pipeline stages.\n\n### Findings

- **Entity**: `CodebaseState` (class in `src/core/data_management.py`)
- **Status**: **Compliant**
- **Evidence**:
    - **Invariants 1 (Collections)**: The class initializes storage for the graph structure in `__init__`: `self.nodes: Dict[str, Dict[str, Any]] = {}` and `self.edges: List[Dict[str, Any]] = []`.
    - **Invariants 2 (O(1) Lookups)**: The class maintains hash map indexes (`_by_file`, `_by_ring`, `_by_kind`, `_by_role`) populated in `load_initial_graph` and provides specific accessor methods (`get_by_file`, `get_by_ring`, etc.) that utilize these dictionaries for O(1) access complexity.
    - **Invariants 3 (Metadata)**: The `metadata` dictionary is initialized with `"layers_activated": []` in `__init__`.
    - **Invariants 4 (Enrichment)**: The method `enrich_node(self, node_id: str, layer_name: str, **attributes)` is implemented to merge attributes into existing nodes and update the `layers_activated` metadata.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: Architectural Drift: The docstring explicitly defines the class as a 'Singleton-like container' intended to be a 'single source of truth', yet the implementation is a standard instantiable class with no mechanism (e.g., `__new__` override or module-level instance) to enforce this constraint. This allows multiple conflicting state objects to exist. (Severity: HIGH)\n- 🔴 **[AM004]**: Orphan Code/Imports: The symbols `UnifiedNode`, `UnifiedEdge`, and `UnifiedAnalysisOutput` are imported from `unified_analysis` but never referenced in the code, which instead relies on generic `Dict` and `Any` typing or dynamic attribute checks. (Severity: MEDIUM)\n- 🔴 **[AM001]**: Context Myopia: The code uses a fragile `try-except` block to import `is_confidence_key`, indicating a lack of awareness regarding the canonical project structure or execution context (root vs module), rather than relying on a standardized configuration or import path. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings

- **Entity**: `IntentExtractor` (defined in `src/core/intent_extractor.py`)
- **Status**: **Non-Compliant**
- **Evidence**: The function `classify_commit_intent(message: str) -> str` explicitly performs classification of raw text into semantic categories (e.g., `'fix'`, `'feature'`, `'refactor'`).
- **Deviation**: The component violates the invariant "**Must not perform complex semantic reasoning (role of Classifier)**".
  - The definition of an **Extractor** is limited to "**raw data ingestion**".
  - Converting raw commit messages into semantic "Intent Types" via keyword analysis is a classification task, which belongs to a **Classifier** component.
  - The `extract_commit_intents` function calls this classifier, meaning the extraction process returns interpreted data rather than raw data.
  - Additionally, `build_node_intent_profile` computes a derived "richness" score, which is a form of analysis beyond ingestion.

- **Entity**: `EdgeExtractor` (defined in `src/core/edge_extractor.py`)
- **Status**: **Compliant**
- **Evidence**: The component extracts structural relationships (edges) using AST (Tree-sitter) or raw content (Regex).
- **Reasoning**: While the component employs `JSModuleResolver` and `ScopeAnalyzer`—which involve logic like fuzzy matching and scope resolution—these mechanisms are used to identify the endpoints of the edges (i.e., resolving the target of a function call). This is considered a necessary part of ingesting the "Call Graph" structure from the code, rather than "complex semantic reasoning" or "classification" of the entities themselves. The output remains a representation of the structural links found in the raw code.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM001]**: In `edge_extractor.py`, the code commits a severe Context Myopia violation by conditionally importing and initializing `tree_sitter` (a high-fidelity parser), yet the `PythonEdgeStrategy` and `JavascriptEdgeStrategy` classes completely ignore this capability. They instead rely on brittle, manual Regex (`re.findall`) to extract function calls and attributes, which is error-prone and ignores the tools already made available in the file context. (Severity: HIGH)\n- 🔴 **[AM001]**: In `intent_extractor.py`, the function `extract_docstring_intent` re-implements Python docstring extraction using regex. This ignores the standard library's `ast` module (`ast.parse` and `ast.get_docstring`) which provides robust, built-in functionality for this exact purpose without the fragility of string matching. (Severity: MEDIUM)\n- 🔴 **[AM002]**: In `edge_extractor.py`, the `JSModuleResolver` pattern relies on a global singleton (`_js_module_resolver`) to maintain state across file analyses. This violates the stateless nature expected of an 'Extractor' role (Architectural Drift), creating hidden coupling where the output depends on the order in which files are processed. (Severity: MEDIUM)\n\n
