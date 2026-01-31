# PARTICLE Tools Index

> **Realm:** PARTICLE (deterministic, structural)
> **Purpose:** Collider support and static analysis tools
> Updated: 2026-01-31

## Analysis Tools

| Tool | Purpose |
|------|---------|
| `mine_semgrep.py` | Extract Semgrep rules for pattern detection |
| `mine_eslint.py` | Extract ESLint rules |
| `extract_doc_nodes.py` | Extract documentation nodes from code |
| `export_graphrag.py` | Export to GraphRAG format |

## Validation Tools

| Tool | Purpose |
|------|---------|
| `validate_ui.py` | Validate UI component compliance |
| `validate_control_registry.py` | Validate control registry entries |
| `verify_animation.py` | Verify animation configurations |
| `check-arch-docs.sh` | Check architecture documentation |

## Pipeline Tools

| Tool | Purpose |
|------|---------|
| `pipeline_tracer.py` | Trace pipeline execution paths |
| `visualize_graph_webgl.py` | WebGL-based graph visualization |
| `clean_scm_headers.py` | Clean SCM headers from files |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `batch_grade/` | Batch grading system for code analysis |
| `cloud/` | Cloud deployment utilities |
| `research/` | Research and experimentation tools |

## Usage

```bash
# Mine Semgrep rules
python3 standard-model-of-code/tools/mine_semgrep.py

# Validate UI components
python3 standard-model-of-code/tools/validate_ui.py

# Trace pipeline
python3 standard-model-of-code/tools/pipeline_tracer.py
```

## Classification

These are **PARTICLE realm** tools:
- Deterministic output
- Structural analysis
- No AI/ML inference
- Static code examination

## See Also

- `context-management/tools/` - WAVE realm tools
- `tools/` - Cross-realm utilities
- `.agent/intelligence/TOOLS_REGISTRY.yaml` - Full tool registry
