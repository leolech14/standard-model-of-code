# AST Node Type Extraction Report

> **Generated**: 2026-01-07
> **Purpose**: Phase 0.1 of C1 Atom Enumeration - Extract all AST node types

---

## Summary

| Language | Named Node Types | Source |
|----------|------------------|--------|
| Python | 127 | tree-sitter-python |
| TypeScript | 183 | tree-sitter-typescript |
| Java | 147 | tree-sitter-java |
| Go | 107 | tree-sitter-go |
| Rust | 163 | tree-sitter-rust |
| **Total Unique** | **576** | Combined after dedup |

---

## Key Insight

576 unique AST nodes will be consolidated into ~200 canonical atoms through:
1. **Merging synonyms**: `function_definition` (Python) ≈ `function_declaration` (TS/Java/Go) ≈ `function_item` (Rust)
2. **Abstracting variants**: `binary_integer_literal`, `octal_integer_literal`, `hex_integer_literal` → `IntegerLiteral`
3. **Language-specific exclusions**: Some nodes are grammar artifacts, not semantic entities

---

## Phase Categorization (Preview)

### DATA Phase (~28 atoms expected)
| Family | Sample AST Nodes |
|--------|------------------|
| CONSTANTS | `integer_literal`, `float_literal`, `string_literal`, `boolean_literal`, `none`, `null_literal` |
| VARIABLES | `identifier`, `assignment`, `augmented_assignment`, `variable_declaration` |
| TYPES | `type_annotation`, `generic_type`, `union_type`, `array_type`, `type_alias` |
| COLLECTIONS | `list`, `dictionary`, `array`, `tuple`, `set`, `map_literal` |
| PATTERNS | `pattern`, `case_clause`, `match_pattern`, `as_pattern` |

### LOGIC Phase (~58 atoms expected)
| Family | Sample AST Nodes |
|--------|------------------|
| FUNCTIONS | `function_definition`, `arrow_function`, `lambda`, `method_definition`, `generator_function` |
| OPERATIONS | `binary_expression`, `unary_expression`, `comparison_expression`, `ternary_expression` |
| CONTROL_FLOW | `if_statement`, `for_statement`, `while_statement`, `try_statement`, `match_statement` |
| EXPRESSIONS | `call_expression`, `member_expression`, `subscript_expression`, `await_expression` |

### ORGANIZATION Phase (~52 atoms expected)
| Family | Sample AST Nodes |
|--------|------------------|
| CONTAINERS | `class_definition`, `interface_declaration`, `enum_declaration`, `struct_item`, `trait_item` |
| MODULES | `module`, `program`, `namespace_definition` |
| IMPORTS | `import_statement`, `import_from_statement`, `export_statement`, `use_declaration` |
| DECORATORS | `decorator`, `attribute_item`, `annotation` |

### EXECUTION Phase (~62 atoms expected)
| Family | Sample AST Nodes |
|--------|------------------|
| ENTRY_POINTS | `if_name_main` (detected pattern), `main_function` (detected pattern) |
| ASSERTIONS | `assert_statement`, `static_assert` |
| ASYNC | `async_block`, `await_expression`, `spawn_expression` |
| ERRORS | `try_statement`, `catch_clause`, `throw_statement`, `finally_clause` |
| METADATA | `comment`, `doc_comment`, `line_comment`, `block_comment` |

---

## Files Generated

| File | Description |
|------|-------------|
| `python_nodes.json` | Raw Tree-sitter Python grammar |
| `typescript_nodes.json` | Raw Tree-sitter TypeScript grammar |
| `java_nodes.json` | Raw Tree-sitter Java grammar |
| `go_nodes.json` | Raw Tree-sitter Go grammar |
| `rust_nodes.json` | Raw Tree-sitter Rust grammar |
| `python_types.txt` | Extracted Python node types (127) |
| `typescript_types.txt` | Extracted TypeScript node types (183) |
| `java_types.txt` | Extracted Java node types (147) |
| `go_types.txt` | Extracted Go node types (107) |
| `rust_types.txt` | Extracted Rust node types (163) |
| `all_unique_types.txt` | Combined unique types (576) |

---

## Next Steps

1. **Phase 0.2**: Cross-reference with existing `ATOMS_REFERENCE.md` (if exists)
2. **Phase 0.3**: Define canonical atom structure with YAML schema
3. **Phase 1.1-1.4**: Complete enumeration of 4 phases (DATA, LOGIC, ORGANIZATION, EXECUTION)
4. **Phase 2**: Create per-language mappings back to AST node types

---

## Notes

- Types starting with `_` (underscore) are internal grammar nodes, excluded from count
- Some nodes appear in multiple languages with different names (synonyms)
- Comments, whitespace, and punctuation nodes are included but may be filtered for the atom table
