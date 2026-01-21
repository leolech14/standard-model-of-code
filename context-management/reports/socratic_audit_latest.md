# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-21 14:52:34\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings
- **Entity**: `compute_markov_matrix`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class. It modifies one of its inputs (`edges`) in place, violating the statelessness principle.
    ```python
    def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:
        # ...
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if source in transitions and target in transitions[source]:
                edge['markov_weight'] = transitions[source][target] # Modifies input
    ```
- **Deviation**: The entity does not inherit from a `BaseStage` class. While it is called like a processing unit, its implementation as a function that mutates its arguments violates the 'stateless' invariant, which is critical for predictable pipeline behavior.

---
- **Entity**: `detect_knots`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class.
    ```python
    def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:
        """
        Detect dependency knots (cycles) and tangles in the graph.
        ...
        """
    ```
- **Deviation**: The entity does not inherit from a `BaseStage` class as required. Although it behaves like a stateless processing unit and returns a structured dictionary, it fails to meet the structural requirement of being an instantiable Stage class.

---
- **Entity**: `compute_data_flow`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class.
    ```python
    def compute_data_flow(nodes: List[Dict], edges: List[Dict]) -> Dict:
        """
        Analyze data flow patterns across the codebase.
        """
    ```
- **Deviation**: The entity does not inherit from a `BaseStage` class. It correctly functions as a stateless processing unit but does not adhere to the required object-oriented structure defined by the `Stage` concept.

---
- **Entity**: `create_codome_boundaries`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class.
    ```python
    def create_codome_boundaries(nodes: List[Dict], edges: List[Dict]) -> Dict[str, Any]:
        """
        Create synthetic codome boundary nodes and inferred edges.
        ...
        """
    ```
- **Deviation**: The entity does not inherit from a `BaseStage` class. While it serves as a distinct processing step in the analysis pipeline, it is implemented procedurally rather than adhering to the class-based structure required by the invariants.

---
- **Entity**: Inline Graph Analytics (Stage 6.5)
- **Status**: Non-Compliant
- **Evidence**: The logic for "Stage 6.5: Graph Analytics" is implemented as a large, inline block of code within the `run_full_analysis` function, rather than being encapsulated in a separate class or even a function.
    ```python
    # Stage 6.5: Graph Analytics (Nerd Layer)
    print("\n🧮 Stage 6.5: Graph Analytics...")
    with StageTimer(perf_manager, "Stage 6.5: Graph Analytics") as timer:
        # Degree computation (always runs - needed for Control Bar mappings)
        try:
            import networkx as nx
            # ... extensive logic follows ...
    ```
- **Deviation**: This is a significant deviation. The processing logic is not encapsulated in any reusable unit, violating all invariants. It is not a class, has no `run`/`execute` method, and is tightly coupled to the orchestrator function. It represents a "stage" in concept only, not in structure.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The primary execution function `run_full_analysis` is an incomplete stub that fails to call any of the major analysis functions defined within the same file. As a result, critical functions like `classify_disconnection`, `create_codome_boundaries`, `build_file_index`, `compute_markov_matrix`, `detect_knots`, `compute_data_flow`, and `_generate_ai_insights` are orphaned. The file defines a complex analysis pipeline but provides no mechanism to execute it, rendering over 80% of the code inert and disconnected from its intended entry point. (Severity: HIGH)\n- 🔴 **[AM002]**: The code violates its designated 'Stage' role, which implies a stateless, deterministic transformation. The implementation includes numerous side effects, such as filesystem manipulation (`_resolve_output_dir`), modifying global interpreter state (`sys.path.insert`), and launching external processes with network access (`_generate_ai_insights`). These actions are characteristic of an Orchestrator or CLI Handler, not a pure processing Stage, representing significant architectural drift. (Severity: HIGH)\n- 🔴 **[AM001]**: The module exhibits context myopia by manipulating `sys.path` with `sys.path.insert(0, ...)` to resolve a local import. This is a fragile anti-pattern that ignores standard Python packaging and module resolution, creating a tight dependency on the file's location within the filesystem. This approach makes the code less portable and harder to maintain. (Severity: MEDIUM)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings
- **Entity**: `EdgeExtractionStrategy` (and its concrete subclasses: `PythonEdgeStrategy`, `JavascriptEdgeStrategy`, `PythonTreeSitterStrategy`, etc.)
- **Status**: Compliant
- **Evidence**: The responsibility of these strategy classes is to extract potential relationships from a single particle's `body_source`. They operate either on the raw string content using regular expressions (e.g., `PythonEdgeStrategy`) or by parsing the body into a local AST and querying it (e.g., `PythonTreeSitterStrategy`). For example, `PythonEdgeStrategy` uses `re.findall(r'(?:self\.)?(\w+)\s*\(', body)` to find call-like patterns. This fits the definition of operating on raw file content or AST. The logic within is confined to identifying syntactic constructs, not interpreting their cross-module meaning.
- **Deviation**: None.

---
- **Entity**: `JSModuleResolver`
- **Status**: Non-Compliant
- **Evidence**: This class is designed to resolve JavaScript module references across files. It analyzes file content to build up a stateful model of `window_exports` and `import_aliases`. The method `resolve_member_call` then uses this cross-file knowledge to link a call site (e.g., `COLOR.subscribe()`) to a particle in a different file.
- **Deviation**: This functionality constitutes "complex semantic reasoning". Instead of simply ingesting raw data (finding the text `COLOR.subscribe`), it interprets the semantics of JavaScript's module system to resolve the meaning of the `COLOR` identifier in a global context. This requires building a cross-file symbol table, a task that goes beyond raw data ingestion and into semantic analysis, which is explicitly designated as the role of other components (like a `Classifier` or a dedicated `Resolver`).

---
- **Entity**: `extract_call_edges`
- **Status**: Non-Compliant
- **Evidence**: This function serves as the main orchestrator. It is responsible for initializing and populating the `JSModuleResolver`: `reset_js_module_resolver()`, `resolver = get_js_module_resolver()`, `resolver.analyze_file(file_path, content)`. The results of this analysis are then used by the `JavaScriptTreeSitterStrategy` to perform cross-file call resolution.
- **Deviation**: By orchestrating the `JSModuleResolver` and incorporating its results into the edge extraction process, this function violates the invariant against performing complex semantic reasoning. It is not merely extracting raw relationships but is actively resolving them using a semantic model of the codebase's module structure, which is outside the scope of a simple "Extractor".\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: The code defines a constant `STDLIB_MODULES` (line 321) and a function `_collect_file_node_ids` (line 428) which are never used or referenced within the provided file. This constitutes orphan code that adds clutter and potential confusion for future maintenance without providing any current functionality. (Severity: LOW)\n\n