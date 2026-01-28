# Tree Sitter Engine

> **Mirror**: [`tree_sitter_engine.py`](../../../src/core/tree_sitter_engine.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`ParseTimeout`**: No docstring
- **`TreeSitterUniversalEngine`**: No docstring

### Functions
- **`normalize_type`**: No docstring
- **`get_query_loader`**: No docstring
- **`get_query_for_language`**: Get tree-sitter query for a language, with fallback to inline queries.
- **`count_parse_errors`**: Count ERROR and MISSING nodes in a parsed tree.
- **`_find_containing_class`**: Walk up the AST to find the containing class for a node.
- **`parse_with_timeout`**: Parse source with timeout protection.
- **`parse_with_timeout.target`**: No docstring
- **`load_colliderignore`**: Load .colliderignore patterns from a directory.
- **`should_ignore_path`**: Check if a path should be ignored based on patterns.
