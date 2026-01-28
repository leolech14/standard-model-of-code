# Data Flow Analyzer

> **Mirror**: [`data_flow_analyzer.py`](../../../src/core/data_flow_analyzer.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`Assignment`**: No docstring
- **`SideEffect`**: No docstring
- **`DataFlowGraph`**: No docstring

### Functions
- **`_get_tree_sitter`**: Lazy load tree-sitter module.
- **`_get_language`**: Lazy load language module.
- **`analyze_data_flow`**: Analyze data flow in a parsed tree.
- **`_analyze_python_data_flow`**: Analyze Python data flow using AST traversal.
- **`_analyze_python_data_flow.visit_node`**: No docstring
- **`_analyze_js_data_flow`**: Analyze JavaScript/TypeScript data flow.
- **`_analyze_js_data_flow.visit_node`**: No docstring
- **`_process_python_assignment`**: Process Python assignment: target = value.
- **`_process_python_augmented_assignment`**: Process Python augmented assignment: target += value (always a mutation).
- **`_process_global_statement`**: Process global/nonlocal statement and track declared globals.
- **`_process_delete_statement`**: Process delete statement as mutation.
- **`_get_python_target_name`**: Get target name and whether it's an attribute write.
- **`_process_js_declarator`**: Process JS variable declarator: const x = value.
- **`_process_js_assignment`**: Process JS assignment expression: target = value.
- **`_process_js_augmented_assignment`**: Process JS augmented assignment: target += value.
- **`_process_js_update`**: Process JS update expression: i++ or ++i (mutation).
- **`_is_attribute_target`**: Check if assignment target is an attribute access.
- **`_extract_referenced_names`**: Extract all identifier names referenced in a node.
- **`_extract_referenced_names.collect_names`**: No docstring
- **`_check_side_effect_call`**: Check if a function call has side effects.
- **`_check_mutating_method_call`**: Check if a method call mutates its receiver object.
- **`calculate_purity`**: Calculate purity score for a data flow graph.
- **`get_purity_factors`**: Get detailed breakdown of purity factors.
- **`_count_mutation_types`**: Count mutations by type.
- **`_count_side_effect_types`**: Count side effects by type.
- **`analyze_function_purity`**: Analyze purity of a single function.
- **`analyze_function_purity.visit`**: No docstring
- **`analyze_function_purity.visit`**: No docstring
- **`get_data_flow_summary`**: Get summary statistics for a data flow graph.
