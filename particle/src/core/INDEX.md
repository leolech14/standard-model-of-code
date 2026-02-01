# src/core/ - Core Analysis Engine

[Back to Project Root](../../README.md)

## Overview

This directory contains the core analysis engine for Collider - the implementation of the Standard Model of Code theory.

## Module Index

### Primary Pipeline

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `full_analysis.py` | Main orchestrator | `run_full_analysis()` |
| `unified_analysis.py` | Analysis data structure | `UnifiedAnalysisOutput` class |
| `brain_download.py` | Output.md generation | `generate_brain_download()` |
| `cli.py` (root) | CLI entry point | `main()` |

### Extraction

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `tree_sitter_engine.py` | AST parsing | `TreeSitterUniversalEngine` |
| `complete_extractor.py` | Node extraction | `extract_complete()` |
| `edge_extractor.py` | Edge/relationship extraction | `extract_call_edges()` |

### Classification

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `atom_classifier.py` | Atom type classification | `classify_atoms()` |
| `atom_registry.py` | Atom definitions | `AtomRegistry` |
| `semantic_ids.py` | Semantic ID generation | `SemanticIDGenerator` |

### Intelligence

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `topology_reasoning.py` | Graph shape analysis | `classify_topology()` |
| `semantic_cortex.py` | Domain inference | `infer_domain()` |
| `insights_engine.py` | Improvement suggestions | `generate_insights()` |

### Support

| Module | Purpose |
|--------|---------|
| `config.py` | Configuration management |
| `data_management.py` | File I/O utilities |
| `output_generator.py` | JSON output generation |
| `stats_generator.py` | Statistics calculation |

## Data Flow

```
Input (codebase path)
    |
tree_sitter_engine.py (parse files)
    |
complete_extractor.py (extract nodes)
    |
edge_extractor.py (extract edges)
    |
atom_classifier.py (classify atoms)
    |
semantic_ids.py (assign IDs)
    |
unified_analysis.py (aggregate)
    |
brain_download.py (generate output.md)
```

## Adding New Functionality

1. **New atom type**: Add to `atom_registry.py`, update `schema/`
2. **New language**: Add grammar to `tree_sitter_engine.py`
3. **New insight**: Add to `insights_engine.py`
4. **New output format**: Add to `output_generator.py`
