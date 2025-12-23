# Roadmap 8: Polyglot Structural Extraction

## Status: Planned

## Problem
Currently, detailed structural data (return types, parameters, docstrings, complexity) is only extracted for **Python** via AST. Other languages get names and line numbers only.

| Language | Structural Data | Confidence Potential |
|----------|-----------------|---------------------|
| Python | ✅ Full | High (82%) |
| TypeScript | ❌ Names only | Medium (62%) |
| Go | ❌ Names only | Medium (62%) |
| Java | ❌ Names only | Medium |
| Rust | ❌ Names only | Medium |

## Solution
Enhance tree-sitter extractors to capture structural data for each language:

### Phase 1: TypeScript/JavaScript
- Extract function return types from TS annotations
- Extract parameter types
- Extract JSDoc comments as docstrings
- Calculate cyclomatic complexity

### Phase 2: Go
- Extract function signatures (`func X(a int) error`)
- Extract return types
- Extract Go doc comments
- Parse Go interfaces for inheritance patterns

### Phase 3: Other Languages
- Java, Rust, C#, Kotlin extractors

## Impact
With full structural data, the graph inference rules (return type analysis, parameter patterns, docstring patterns) will fire on all languages, boosting confidence from ~62% to estimated ~78%.

## Priority: Medium
This is a parser infrastructure improvement, not a core model change.
