# Configuration Files Index

> **Purpose:** Central index of all configuration files in context-management/config/

## Core Configs

| File | Purpose | Used By |
|------|---------|---------|
| `aci_config.yaml` | ACI tier routing and thresholds | `aci/*.py` |
| `analysis_sets.yaml` | File groupings for analyze.py queries | `ai/analyze.py` |
| `prompts.yaml` | AI prompt templates | `ai/*.py` |
| `refinery_config.yaml` | Refinery pipeline settings | `refinery/pipeline.py` |

## Document Processing

| File | Purpose | Used By |
|------|---------|---------|
| `docling_config.yaml` | Docling processor settings | `docling_processor/` |
| `docling_gpu_profiles.yaml` | GPU acceleration profiles | `docling_processor/` |
| `docling_kubernetes.yaml` | K8s deployment config | Ops (future) |
| `documentation_map.yaml` | Doc structure mapping | Refinery |

## Schema Files

| File | Purpose | Used By |
|------|---------|---------|
| `research_schemas.yaml` | Research output schemas | `ai/analyze.py` |
| `semantic_models.yaml` | Semantic model definitions | ACI |
| `query_manifest_schema.yaml` | Query manifest validation | Analyze |
| `insights_schema.json` | Insights output schema | Refinery |

## Registries

| File | Purpose | Used By |
|------|---------|---------|
| `registries/DOMAINS.yaml` | Domain boundary definitions | Global |

## Notes

- **Canonical theory:** See `standard-model-of-code/docs/theory/`
- **Tool registry:** See `.agent/intelligence/TOOLS_REGISTRY.yaml`
- **Add new configs here** with clear naming: `<subsystem>_config.yaml`
