# Research Directory

Consolidated research outputs from AI assistants.

## Structure

```
research/
├── gemini/          # Gemini 2.0 Flash research (348 files)
├── perplexity/      # Perplexity research (293 files)
├── claude/          # Claude research (TBD)
├── *.md             # Cross-cutting research from context-management
└── INDEX.md         # This file
```

## Agent-Specific Notes

### Gemini
- **Format:** Timestamped markdown files `YYYYMMDD_HHMMSS_query.md`
- **Source:** Originally in `standard-model-of-code/docs/research/gemini/docs/`
- **Use case:** Deep architectural validation, theory validation, multi-turn research

### Perplexity
- **Format:** Timestamped markdown files `YYYYMMDD_HHMMSS_query.md` + README
- **Source:** Originally in `standard-model-of-code/docs/research/perplexity/`
- **Use case:** Quick fact-checking, best practices, external ecosystem research

### Claude
- **Status:** Placeholder for future Claude Code research outputs
- **Potential use:** Implementation research, code analysis findings

## Cross-Cutting Files (root level)

Files from `context-management/docs/research/` covering multi-system concerns:
- ACI_DIAGNOSIS_AND_FIXES.md
- MULTI_DATASET_ANALYSIS_RESEARCH_SCOPE.md
- perplexity_topology_query.md

## Usage

**Find by topic:**
```bash
grep -r "keyword" research/
```

**Find by date:**
```bash
ls research/gemini/20260130_*
```

**Most recent:**
```bash
ls -lt research/gemini/ | head -10
```

## Migration Notes

- **Date:** 2026-01-31
- **Task:** TASK-104 consolidation
- **Files moved:** 641 markdown files
- **Old locations:** Removed after verification
- **Raw/sessions subdirs:** Remain in original locations (gitignored)

## Related Directories

- `/governance/` - Strategic decisions and architecture docs
- `/docs/research/` - Old location (deprecated)
- `/standard-model-of-code/docs/theory/` - Theory development
