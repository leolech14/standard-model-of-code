# Validated Semantic Map: PIPELINE\n\nDate: 2026-01-21 18:44:53\n\n## Concept: Stage\n> A processing unit in the analysis pipeline.\n\n### Findings

The codebase implements its analysis pipeline using a functional paradigm, where processing units are standalone functions called in sequence by the `run_full_analysis` orchestrator. This architectural pattern is fundamentally at odds with the object-oriented `Stage` concept defined.

---

- **Entity**: `compute_markov_matrix`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class. It is defined as `def compute_markov_matrix(nodes: List[Dict], edges: List[Dict]) -> Dict:`. It also modifies one of its input arguments (`edges`) in place, which violates the statelessness principle.
- **Deviation**:
    - **Inheritance**: As a function, it cannot inherit from a `BaseStage` class.
    - **Method**: It does not implement an `execute` or `run` method; it is invoked directly by its function name.
    - **Statelessness**: The function is stateful. It modifies the `edges` list passed to it by adding a `markov_weight` key to each edge dictionary.
    - **Return Format**: It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.

---

- **Entity**: `detect_knots`
- **Status**: Non-Compliant
- **Evidence**: The entity is a standalone function, not a class. It is defined as `def detect_knots(nodes: List[Dict], edges: List[Dict]) -> Dict:`.
- **Deviation**:
    - **Inheritance**: As a function, it cannot inherit from a `BaseStage` class.
    - **Method**: It does not implement an `execute` or `run` method; it is invoked directly.
    - **Return Format**: It returns a standard Python `Dict`, not a `ProcessingResult` or `AnalysisResult` object.
    - *(Note: This function does adhere to the statelessness principle, as it does not modify its inputs and returns a new dictionary. However, it fails on all other invariants.)*

---

- **Entity**: Graph Analytics processing block (within `run_full_analysis`)
- **Status**: Non-Compliant
- **Evidence**: This processing unit is not an encapsulated entity but rather an inline block of code within the `run_full_analysis` function, starting at the comment `"# Stage 6.5: Graph Analytics..."`. It directly iterates over and modifies the `nodes` list.
- **Deviation**:
    - **Inheritance**: It is a block of procedural code, not a class, and thus cannot inherit.
    - **Method**: It is not a method and cannot be executed independently; it is part of a larger function.
    - **Statelessness**: This block is highly stateful. It modifies the `nodes` list in-place, adding numerous keys (`in_degree`, `out_degree`, `topology_role`, `disconnection`, etc.) to the node dictionaries. This creates significant side effects for subsequent stages.
    - **Return Format**: It does not return any value; its entire purpose is to modify shared state.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM002]**: The code violates architectural layer separation by mixing core analysis logic with presentation and OS-interaction concerns. For instance, `create_codome_boundaries`, a core processing function, contains a `print` statement, which is presentation logic. More significantly, the file includes helper functions like `_open_file` and `_manual_open_command` that perform OS-level operations (opening files via shell commands), a responsibility that should reside in a dedicated CLI or UI layer, not in a `core` analysis module. This blending of concerns reduces the modularity and reusability of the core engine. (Severity: MEDIUM)\n- 🔴 **[AM001]**: The code exhibits minor context myopia by implementing custom, regex-based parsers in `detect_js_imports` and `detect_class_instantiation`. While a comment acknowledges that a full AST analysis would be more robust, this heuristic-based approach is prone to errors and duplicates the more complex function of dedicated language parsers. For a sophisticated analysis tool, relying on fragile regex for code parsing, instead of leveraging or building a more robust parsing component, represents a missed opportunity for greater accuracy and adherence to best practices. (Severity: LOW)\n\n## Concept: Extractor\n> Component responsible for raw data ingestion.\n\n### Findings
- **Entity**: `PythonEdgeStrategy`, `JavascriptEdgeStrategy`, `GoEdgeStrategy`, `RustEdgeStrategy`
- **Status**: Compliant
- **Evidence**: These classes operate on the `body_source` of a code particle (a raw string) and use regular expressions to find patterns that look like function calls. For example, `PythonEdgeStrategy` uses `re.findall(r'(?:self\.)?(\w+)\s*\(', body)`. This is a direct operation on raw content to extract potential relationships without understanding the code's deeper meaning.
- **Deviation**: N/A

---
- **Entity**: `TreeSitterEdgeStrategy`, `PythonTreeSitterStrategy`, `TypeScriptTreeSitterStrategy`
- **Status**: Compliant
- **Evidence**: These classes parse the raw `body_source` into an Abstract Syntax Tree (AST) using `tree-sitter`. They then traverse this tree to find structural nodes corresponding to calls (e.g., `node.type in {'call', 'call_expression'}`). This adheres to the invariant "Must operate on raw file content or AST" and avoids complex semantic reasoning by focusing on the structural syntax of the code.
- **Deviation**: N/A

---
- **Entity**: `JSModuleResolver`
- **Status**: Non-Compliant
- **Evidence**: The purpose of this class is to resolve JavaScript module references across files by tracking aliases, global exports, and various import/export patterns. The method `resolve_member_call` attempts to determine the concrete target of a call like `COLOR.subscribe()` by checking its internal maps (`self.window_exports`, `self.import_aliases`) and even employing heuristics like fuzzy filename matching.
- **Deviation**: This class performs cross-file symbol resolution, which is a form of "complex semantic reasoning". Instead of just extracting the text "COLOR.subscribe", it tries to understand what "COLOR" refers to in the context of the entire codebase. This reasoning step goes beyond raw data ingestion and violates the invariant that such tasks are the role of a Classifier.

---
- **Entity**: `JavaScriptTreeSitterStrategy`
- **Status**: Non-Compliant
- **Evidence**: This class directly integrates and uses `JSModuleResolver` to perform its extraction. In its `extract_edges` method, it calls `resolver.resolve_member_call(obj_name, method_name, caller_file, particle_by_name)` to find the target of a member call.
- **Deviation**: By using `JSModuleResolver`, this strategy incorporates cross-file semantic reasoning into the extraction process. It is not merely extracting call information from the local AST; it is actively resolving symbols, which is a task reserved for components other than the Extractor according to the provided definition.

---
- **Entity**: `extract_call_edges` (Orchestrator Function)
- **Status**: Non-Compliant
- **Evidence**: A significant portion of this function is dedicated to setting up and using the `JSModuleResolver`. It begins by calling `reset_js_module_resolver()`, then iterates through all JS files to populate the resolver with `resolver.analyze_file(file_path, content)`. The results of this semantic analysis are then used by strategies like `JavaScriptTreeSitterStrategy`.
- **Deviation**: This function orchestrates the violation by making cross-file semantic analysis a foundational step in the extraction process. It mixes the pure ingestion role of an Extractor with the analytical role of a more advanced component, thereby breaking the "Must not perform complex semantic reasoning" invariant.\n\n### Semantic Guardrails (Antimatter Check)\n**DETECTED LIABILITIES**:\n- 🔴 **[AM004]**: A significant feature for high-precision JavaScript analysis is implemented but not integrated, leaving it as orphan code. The `JavaScriptTreeSitterStrategy` class defines a method `extract_member_call` intended to parse object-method calls (e.g., `MyModule.myFunc()`). This method, and by extension the `JSModuleResolver.resolve_member_call` it is designed to feed, are never executed. The strategy inherits the generic `extract_edges` method from its parent `TreeSitterEdgeStrategy`, which does not use the specialized `extract_member_call` logic. As a result, the entire module resolution mechanism for member calls, a key feature advertised in the strategy's docstring, is non-functional. (Severity: HIGH)\n\n