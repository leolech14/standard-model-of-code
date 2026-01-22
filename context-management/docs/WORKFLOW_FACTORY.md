# Workflow Factory

> A systematic approach to AI-powered codebase exploration using the hybrid Tier 1/Tier 2 system.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        WORKFLOW FACTORY             │
                    │   "Right tool for the right job"   │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
        ┌───────────────────┐           ┌───────────────────┐
        │   TIER 1: LONG    │           │  TIER 2: FILE     │
        │     CONTEXT       │           │     SEARCH        │
        │                   │           │                   │
        │ • Holistic view   │           │ • Needle queries  │
        │ • Architecture    │           │ • Citations       │
        │ • Cross-file      │           │ • Repeated Q&A    │
        │ • 1M tokens max   │           │ • Index once      │
        └───────────────────┘           └───────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                    ┌───────────────────┐
                    │  COMBINED POWER   │
                    │                   │
                    │ File Search finds │
                    │ → Long Context    │
                    │   reasons deeply  │
                    └───────────────────┘
```

## Available File Search Stores

| Store | Files | Best For |
|-------|-------|----------|
| `collider-brain` | 14 | "How does local_analyze.py work?" |
| `collider-docs` | 96 | "What is the theory?" "What debt exists?" |
| `collider-pipeline` | 7 | "How does analysis flow?" "What stages exist?" |
| `collider-schema` | 19 | "What atoms exist?" "What are the roles?" |
| `collider-classifiers` | 10 | "How are nodes classified?" "What heuristics?" |

## Workflow Recipes

### Recipe 1: Understanding a Feature

```bash
# Step 1: Quick discovery with File Search
python local_analyze.py --search "How does role classification work?" \
  --store-name collider-classifiers

# Step 2: Deep dive with Long Context (if needed)
python local_analyze.py --set classifiers --interactive \
  "Explain the role_registry module in detail"
```

### Recipe 2: Debugging an Issue

```bash
# Step 1: Find relevant files
python local_analyze.py --search "Where is RPBL score calculated?" \
  --store-name collider-pipeline

# Citations tell you exactly which files matter

# Step 2: Read those specific files with Long Context
python local_analyze.py --file "src/core/standard_model_enricher.py" \
  "Why might RPBL scores be incorrect for utility functions?"
```

### Recipe 3: Architecture Review

```bash
# Step 1: Query docs for known issues
python local_analyze.py --search "What architecture debt exists?" \
  --store-name collider-docs

# Step 2: Full architecture review with composed set
python local_analyze.py --set architecture_review --interactive
```

### Recipe 4: Theory Exploration

```bash
# Step 1: Quick answer from indexed docs
python local_analyze.py --search "What are the 16 scale levels?" \
  --store-name collider-docs

# Step 2: Full theory deep dive
python local_analyze.py --set theory --interactive
```

### Recipe 5: Adding a New Feature

```bash
# Step 1: Find similar patterns
python local_analyze.py --search "How are new classifiers added?" \
  --store-name collider-classifiers

# Step 2: Understand the pipeline integration
python local_analyze.py --search "How do stages get added to full_analysis?" \
  --store-name collider-pipeline

# Step 3: Full context for implementation
python local_analyze.py --set pipeline "I want to add a new Stage 9 for X"
```

## Decision Matrix

| Question Type | Use | Why |
|---------------|-----|-----|
| "What is X?" | File Search | Quick answer with citations |
| "How does X work?" | File Search → Long Context | Find files, then deep dive |
| "Why does X happen?" | Long Context | Needs cross-file reasoning |
| "Fix bug in X" | File Search → Long Context | Find location, then analyze |
| "Review architecture of X" | Long Context (composed set) | Holistic view needed |
| "What are the patterns for X?" | File Search | Quick discovery |

## Cost Comparison

| Mode | Typical Cost | Best For |
|------|--------------|----------|
| File Search query | ~$0.003 | Repeated questions, discovery |
| Long Context one-shot (50K) | ~$0.02 | Quick analysis |
| Long Context interactive (100K) | ~$0.05/turn | Deep exploration |
| Full architecture review (250K) | ~$0.10/turn | Comprehensive review |

## Store Maintenance

### List stores
```bash
python local_analyze.py --list-stores
```

### Re-index after code changes
```bash
python local_analyze.py --delete-store collider-pipeline
python local_analyze.py --index --set pipeline --store-name collider-pipeline --yes
```

### Add new store for specific area
```bash
python local_analyze.py --index --file "path/to/files/*.py" \
  --store-name my-new-store --yes
```

## Environment Setup

```bash
# Doppler (recommended)
eval $(doppler secrets download --project ai-tools --config dev --no-file --format env-no-quotes)

# Or direct export
export GEMINI_API_KEY='your-key'
```

## Integration with Analysis Sets

The `analysis_sets.yaml` defines file patterns for Long Context analysis.
File Search stores are indexed separately but should mirror these patterns:

| Analysis Set | Corresponding Store |
|--------------|---------------------|
| `brain` | `collider-brain` |
| `pipeline` | `collider-pipeline` |
| `classifiers` | `collider-classifiers` |
| `theory` | `collider-docs` |
| `schema` | `collider-schema` |

Keep them in sync: when you update an analysis set, re-index the corresponding store.
