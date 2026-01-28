# Normalize Output

> **Mirror**: [`normalize_output.py`](../../../src/core/normalize_output.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture

### Functions
- **`_get_schema`**: Lazy-load unified atom schema if available.
- **`normalize_meta`**: Ensure meta.target/timestamp/version exist and are populated.
- **`is_confidence_key`**: No docstring
- **`normalize_confidence_fields`**: Normalize confidence-like fields to 0..1, preserving raw values.
- **`_derive_atom_family`**: No docstring
- **`_derive_tier`**: No docstring
- **`_normalize_taxonomy`**: No docstring
- **`_iter_nodes`**: No docstring
- **`_iter_edges`**: No docstring
- **`_candidate_roots`**: No docstring
- **`_normalize_path_value`**: No docstring
- **`normalize_file_paths`**: Make node.file_path relative to meta.target when possible.
- **`normalize_file_boundaries`**: Make boundary.file relative to meta.target when possible.
- **`normalize_files_index`**: Normalize keys in files index to be relative to meta.target when possible.
- **`canonicalize_ids`**: Canonicalize node ids to file_path::qualified_name.
- **`normalize_output`**: Apply all output-normalization steps in-place.
- **`validate_contract`**: Validate output contract; returns (errors, warnings).
- **`validate_contract.check_confidence_fields`**: No docstring
