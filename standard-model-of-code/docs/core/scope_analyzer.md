# Scope Analyzer

> **Mirror**: [`scope_analyzer.py`](../../../src/core/scope_analyzer.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`Definition`**: No docstring
- **`Reference`**: No docstring
- **`Scope`**: No docstring
- **`ScopeGraph`**: No docstring
- **`QueryBasedScopeAnalyzer`**: No docstring

### Functions
- **`_find_containing_scope`**: Find the innermost scope containing a node.
- **`_infer_definition_kind`**: Infer the kind of definition from node context.
- **`_analyze_manual`**: Manual AST traversal fallback when queries unavailable.
- **`_analyze_manual.visit_node`**: No docstring
- **`_get_scope_types`**: Get scope-creating node types for a language.
- **`_extract_definitions_manual`**: Extract definitions manually (fallback).
- **`_extract_references_manual`**: Extract references manually (fallback).
- **`_resolve_all_references`**: Resolve all references to their definitions.
- **`resolve_reference`**: Resolve a reference to its definition.
- **`find_unused_definitions`**: Find definitions that are never referenced.
- **`find_shadowed_definitions`**: Find definitions that shadow outer scope definitions.
- **`_find_in_ancestors`**: Find a definition with given name in ancestor scopes.
- **`analyze_scopes`**: Analyze scopes in a parsed tree.
- **`get_scope_summary`**: Get summary statistics for a scope graph.

## Waybill
- **ID**: `PARCEL-SCOPE_ANALYZER.PY`
- **Source**: `Codome://scope_analyzer.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T17:50:51.687501Z`
- **Status**: REFINED
