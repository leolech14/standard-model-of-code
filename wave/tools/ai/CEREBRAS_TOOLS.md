# Cerebras Integration Tools

Fast semantic enrichment using Cerebras inference (3000 tokens/sec).

## Architecture

```
Collider (FREE)              Cerebras ($0.001/file)
─────────────────            ────────────────────────
Structure:                   Semantics:
- Atoms (167 types)          - Purpose (intent)
- Layers                     - Semantic tags
- Edges (dependencies)       - Complexity rating
- Metrics                    - Quality hints
         │                            │
         └──────────┬─────────────────┘
                    ▼
            ENRICHED OUTPUT
         (Structure + Meaning)
```

## Tools

### 1. repo_mapper.py - Repository Mapping (FREE)

Maps entire repository tree with metadata. No API calls.

```bash
# Map repository
python repo_mapper.py map

# Analyze patterns
python repo_mapper.py analyze

# Create processing plan
python repo_mapper.py plan
```

**Output:** `wave/data/repo_map/`

### 2. cerebras_enricher.py - Semantic Enrichment

Adds semantic layer on top of Collider output.

```bash
# Run Collider first
./collider full /path/to/repo --output .collider

# Then enrich with Cerebras
python cerebras_enricher.py enrich .collider/unified_analysis.json

# Use specific model
python cerebras_enricher.py enrich ... --model llama3.1-8b

# Quick single-file enrichment
python cerebras_enricher.py quick src/main.py
```

**Output:** `wave/data/enriched/enriched_latest.json`

**Fields extracted:**
- `purpose` - One-line intent (max 20 words)
- `semantic_tags` - 5 human-meaningful tags
- `key_exports` - Main functions/classes
- `dependencies` - What it needs
- `complexity` - LOW/MEDIUM/HIGH
- `quality_hints` - Potential issues
- `related_to` - Suggested related files

### 3. cerebras_tagger.py - Batch D1-D8 Classification

Fast dimension tagging for files.

```bash
# Tag all Python files
python cerebras_tagger.py tag --pattern "**/*.py"

# Tag specific directory
python cerebras_tagger.py tag --pattern "**/*.py" --path src/

# View statistics
python cerebras_tagger.py stats

# Validate with Claude
python cerebras_tagger.py validate --sample 0.1
```

**Output:** `wave/data/tags/tags_latest.json`

## Models

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| llama-3.3-70b | 2100 t/s | Best | Complex analysis |
| llama3.1-8b | 3000 t/s | Good | Bulk operations |
| qwen-3-32b | 2000 t/s | Good | Alternative |

## Rate Limits

Cerebras enforces per-second burst limits:
- 3000 RPM stated = ~50/sec max
- Actual burst limit is stricter (~7-10/sec safe)
- Tools use 150ms interval between requests

## Cost

| Operation | Files | Cost |
|-----------|-------|------|
| Enrich (8B) | 100 | ~$0.03 |
| Enrich (70B) | 100 | ~$0.06 |
| Tag (8B) | 500 | ~$0.36 |

## Validation

Cerebras output validated at **90% accuracy** by Perplexity:
- cli.py classification: 9/10
- mine_semgrep.py classification: 9/10

## Pipeline Integration

```yaml
# In TOOLS_REGISTRY.yaml
cerebras_enricher:
  id: T014
  connects_to: [collider]

cerebras_tagger:
  id: T015

repo_mapper:
  id: T016
```

## Environment

Requires `CEREBRAS_API_KEY` in environment or Doppler:
```bash
export CEREBRAS_API_KEY="csk-..."
# or
doppler secrets set CEREBRAS_API_KEY "csk-..."
```
