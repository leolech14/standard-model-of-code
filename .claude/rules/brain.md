---
paths:
  - "context-management/**"
---

# Brain (AI/Context) Rules

## AI Analysis Tool
- Location: `tools/ai/analyze.py`
- Requires: `gcloud auth application-default login`
- Model: `gemini-2.5-pro` (default, best quality)

## Analysis Sets
- Defined in: `config/analysis_sets.yaml`
- Use `--set brain_core` for AI tools analysis
- Use `--set body` for Collider code analysis

## Cloud Mirror
- Tool: `tools/archive/archive.py`
- Bucket: `gs://elements-archive-2026/`
- Large outputs stored in GCS, not git

## Analysis Modes
- `--mode standard`: General analysis
- `--mode forensic`: Line-level citations required
- `--mode architect`: Theory-aware analysis

## Retry Logic
- Built-in exponential backoff for rate limits
- Max 5 retries with jitter
