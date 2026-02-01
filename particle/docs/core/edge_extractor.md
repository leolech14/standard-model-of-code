# Edge Extractor

> **Mirror**: [`edge_extractor.py`](../../../src/core/edge_extractor.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`JSModuleResolver`**: No docstring
- **`EdgeExtractionStrategy`**: No docstring
- **`PythonEdgeStrategy`**: No docstring
- **`JavascriptEdgeStrategy`**: No docstring
- **`TypeScriptEdgeStrategy`**: No docstring
- **`GoEdgeStrategy`**: No docstring
- **`RustEdgeStrategy`**: No docstring
- **`DefaultEdgeStrategy`**: No docstring
- **`TreeSitterEdgeStrategy`**: No docstring
- **`PythonTreeSitterStrategy`**: No docstring
- **`JavaScriptTreeSitterStrategy`**: No docstring
- **`TypeScriptTreeSitterStrategy`**: No docstring

### Functions
- **`get_js_module_resolver`**: Get or create the global JS module resolver.
- **`reset_js_module_resolver`**: Reset the global resolver (for testing or fresh analysis).
- **`_normalize_file_path`**: Normalize file path to a resolved absolute string.
- **`module_name_from_path`**: Derive a module name from a file path.
- **`file_node_name`**: Compute a unique file-node name derived from the file path.
- **`file_node_id`**: Build a canonical file-node id for a file path.
- **`_make_node_id`**: Create a node ID in the canonical format: {full_path}:{name}
- **`_get_particle_id`**: Get the canonical ID for a particle.
- **`_collect_file_node_ids`**: Collect file-node ids keyed by normalized file path.
- **`_find_target_particle`**: Find target particle for a call, preferring same-file matches.
- **`get_strategy_for_file`**: Factory to get the correct strategy based on file extension.
- **`extract_call_edges`**: No docstring
- **`extract_decorator_edges`**: Extract decorator relationships.
- **`_extract_exposure_edges_from_body`**: Extract module.exports, export statements from source code.
- **`extract_exposure_edges`**: Extract exposure relationships (module.exports, export statements).
- **`deduplicate_edges`**: Remove duplicate edges based on source, target, and type.
- **`_is_canonical_id`**: Check if target looks like a canonical ID (path:name format).
- **`_extract_node_path`**: Extract the file path portion from a canonical node id.
- **`_build_file_to_node_ids`**: Build a mapping from absolute file path to node ids for that file.
- **`resolve_import_target_to_file`**: Resolve a module name to a file path inside target_root.
- **`_get_module_root`**: Extract root module name from a dotted path.
- **`_is_stdlib_or_external`**: Check if target appears to be stdlib or third-party.
- **`resolve_edges`**: Post-process edges to add resolution status.
- **`get_proof_edges`**: Filter edges for proof metrics calculation.
- **`get_edge_resolution_summary`**: Summarize edge resolution status by edge type.
- **`get_import_resolution_diagnostics`**: Summarize import resolution diagnostics.

## Waybill
- **ID**: `PARCEL-EDGE_EXTRACTOR.PY`
- **Source**: `Codome://edge_extractor.py`
- **Refinery**: `SelfAnalysis-v1.0`
- **Generated**: `2026-01-28T19:17:39.162111Z`
- **Status**: REFINED
