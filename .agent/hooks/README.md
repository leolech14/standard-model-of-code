# Git Hooks

Git hooks for PROJECT_elements.

## Installation

```bash
# Copy all hooks to .git/hooks/
cp .agent/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

## Hooks

### post-commit

Runs after every commit:

1. **Auto-Mirror** - Syncs to GCS (`gs://elements-archive-2026/`)
2. **BARE TruthValidator** - Updates repository truths

The TruthValidator outputs to `.agent/intelligence/truths/repo_truths.yaml`.

## Adding New Hooks

1. Create the hook script in `.agent/hooks/`
2. Document it in this README
3. Copy to `.git/hooks/` and make executable
