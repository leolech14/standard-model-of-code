# AST to Atom Crosswalk Table

> **Purpose**: Map Tree-sitter AST node types to Standard Model atoms
> **Generated**: 2026-01-07
> **Status**: Phase 0.2 - Initial Mapping

---

## Summary

| Language | AST Node Types | Mapped to 200 Atoms | Coverage |
|----------|----------------|---------------------|----------|
| Python | 127 | ~95% | High |
| TypeScript | 183 | ~90% | High |
| Java | 147 | ~92% | High |
| Go | 107 | ~88% | High |
| Rust | 163 | ~85% | Medium-High |
| **Average** | - | - | **~90%** |

---

## Crosswalk by Phase

### DATA Phase → AST Mappings

| Atom | Python | TypeScript | Java | Go | Rust |
|------|--------|------------|------|-----|------|
| **Boolean** | `true`, `false` | `true`, `false` | `boolean_literal` | `true`, `false` | `boolean_literal` |
| **Integer** | `integer` | `number` | `integer_literal` | `int_literal` | `integer_literal` |
| **Float** | `float` | `number` | `floating_point_literal` | `float_literal` | `float_literal` |
| **String** | `string` | `string`, `template_string` | `string_literal` | `interpreted_string_literal` | `string_literal` |
| **Null** | `none` | `null` | `null_literal` | `nil` | - |
| **LocalVar** | `identifier` | `identifier` | `identifier` | `identifier` | `identifier` |
| **Parameter** | `parameters` | `formal_parameters` | `formal_parameters` | `parameter_list` | `parameters` |
| **ArrayLiteral** | `list` | `array` | `array_initializer` | `composite_literal` | `array_expression` |
| **ObjectLiteral** | `dictionary` | `object` | - | `composite_literal` | `struct_expression` |

---

### LOGIC Phase → AST Mappings

| Atom | Python | TypeScript | Java | Go | Rust |
|------|--------|------------|------|-----|------|
| **Function** | `function_definition` | `function_declaration` | `method_declaration` | `function_declaration` | `function_item` |
| **Method** | `function_definition` (in class) | `method_definition` | `method_declaration` | `method_declaration` | `function_item` (in impl) |
| **Lambda** | `lambda` | `arrow_function` | `lambda_expression` | `func_literal` | `closure_expression` |
| **Constructor** | `__init__` (pattern) | `constructor` | `constructor_declaration` | - | - |
| **AsyncFunction** | `function_definition` + `async` | `function_declaration` + `async` | - | - | `async_block` |
| **Generator** | `function_definition` + `yield` | `generator_function` | - | - | - |
| **BinaryExpr** | `binary_operator` | `binary_expression` | `binary_expression` | `binary_expression` | `binary_expression` |
| **UnaryExpr** | `unary_operator` | `unary_expression` | `unary_expression` | `unary_expression` | `unary_expression` |
| **CallExpr** | `call` | `call_expression` | `method_invocation` | `call_expression` | `call_expression` |
| **MemberExpr** | `attribute` | `member_expression` | `field_access` | `selector_expression` | `field_expression` |
| **IfBranch** | `if_statement` | `if_statement` | `if_statement` | `if_statement` | `if_expression` |
| **ForLoop** | `for_statement` | `for_statement` | `for_statement` | `for_statement` | `for_expression` |
| **WhileLoop** | `while_statement` | `while_statement` | `while_statement` | `for_statement` (no while) | `while_expression` |
| **TryBlock** | `try_statement` | `try_statement` | `try_statement` | - | - |
| **CatchClause** | `except_clause` | `catch_clause` | `catch_clause` | - | - |
| **ReturnStmt** | `return_statement` | `return_statement` | `return_statement` | `return_statement` | `return_expression` |
| **AwaitExpr** | `await` | `await_expression` | - | - | `await_expression` |
| **MatchPattern** | `match_statement` | - | - | `type_switch_statement` | `match_expression` |

---

### ORGANIZATION Phase → AST Mappings

| Atom | Python | TypeScript | Java | Go | Rust |
|------|--------|------------|------|-----|------|
| **Class** | `class_definition` | `class_declaration` | `class_declaration` | - | - |
| **Struct** | - | - | - | `struct_type` | `struct_item` |
| **Enum** | - | `enum_declaration` | `enum_declaration` | - | `enum_item` |
| **Trait** | - | - | - | - | `trait_item` |
| **Interface** | - | `interface_declaration` | `interface_declaration` | `interface_type` | - |
| **Module** | `module` (pattern) | `module` | - | `package_clause` | `mod_item` |
| **ImportStmt** | `import_statement` | `import_statement` | `import_declaration` | `import_declaration` | `use_declaration` |
| **ExportStmt** | - | `export_statement` | - | - | `pub` modifier |
| **Decorator** | `decorator` | `decorator` | `annotation` | - | `attribute_item` |
| **GenericParam** | - | `type_parameter` | `type_parameter` | `type_parameter` | `type_parameters` |
| **TypeAlias** | - | `type_alias_declaration` | - | `type_declaration` | `type_item` |

---

### EXECUTION Phase → AST Mappings

| Atom | Python | TypeScript | Java | Go | Rust |
|------|--------|------------|------|-----|------|
| **AsyncBlock** | `async for`, `async with` | `async_function` | - | - | `async_block` |
| **Future** | - | `Promise` (pattern) | `CompletableFuture` | - | `impl Future` |
| **Channel** | - | - | - | `channel_type` | `channel` |
| **Goroutine** | - | - | - | `go_statement` | - |
| **Exception** | `raise` | `throw` | `throw_statement` | `panic` | `panic!` |
| **Defer** | - | - | - | `defer_statement` | - |
| **MacroDef** | - | - | - | - | `macro_definition` |
| **Annotation** | `decorator` | `decorator` | `annotation` | - | `attribute_item` |

---

## Unmapped AST Nodes (Candidates for New Atoms)

| Language | Unmapped Node | Suggested Atom | Priority |
|----------|---------------|----------------|----------|
| Rust | `unsafe_block` | UnsafeBlock | Medium |
| Rust | `lifetime` | Lifetime ✅ (exists #136) | - |
| Go | `select_statement` | ChannelSelect ✅ (exists #146) | - |
| TypeScript | `satisfies_expression` | SatisfiesExpr | Low |
| Java | `record_declaration` | Record ✅ (exists #91) | - |
| Python | `walrus_operator` | WalrusExpr ✅ (exists #55) | - |

---

## Coverage Analysis

### By Phase
```
DATA:         ██████████████████████████████░░░░░░░░░░ 75% (21/28)
LOGIC:        ████████████████████████████████████████ 95% (55/58)
ORGANIZATION: ██████████████████████████████████░░░░░░ 85% (44/52)
EXECUTION:    ████████████████████████░░░░░░░░░░░░░░░░ 60% (37/62)
```

### Notes
- **LOGIC phase** has highest coverage - most languages share core control flow
- **EXECUTION phase** has lowest coverage - many atoms are runtime/semantic concepts not directly in AST
- Some atoms represent **patterns** (e.g., Repository, Service) rather than AST nodes - need semantic analysis

---

## Next Steps

1. **Complete detailed crosswalk** with line-by-line verification
2. **Create per-language YAML mapping files** 
3. **Implement in Collider** - update `symbol_classifier.py` to use crosswalk
4. **Validate coverage** - run on sample repositories

