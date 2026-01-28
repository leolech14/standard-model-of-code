# Contextome Mapping Pack

This folder contains machine-generated indexes for `full_contextome.zip`.

**Generated:** 2026-01-27

## Files

- `REPO_INDEX.md` — human-readable overview + hotspots + doc-graph snapshot
- `FILESYSTEM_TREE.md` — shallow tree summary (depth 2)
- `ATTENTION_MAP.md` — what to focus on vs what to separate
- `FILE_INDEX.csv` — every file with size + classification
- `DIRECTORY_STATS.csv` — counts + size per directory
- `DOCS_INDEX.csv` — every markdown doc with title + link degrees
- `DOC_GRAPH.json` — doc graph (active docs) for visualization
- `BROKEN_LINKS.csv` — broken local links from docs (code blocks ignored)
- `THEORY_SECTION_INDEX.md` — extracted `@SECTION` index from `context-management/docs/theory/THEORY.md`
- `THEORY_SECTION_REGISTRY.csv` — section registry (CSV)
- `THEORY_SECTION_GRAPH.json` — dependency graph for theory sections
- `repo_mapper.py` — script to regenerate these indexes on a real repo checkout

## Quick usage

Open:
1. `REPO_INDEX.md`
2. `ATTENTION_MAP.md`

Then use the CSVs to slice/filter:
- filter `FILE_INDEX.csv` to isolate “generated_output” and build a *Core-only* pack
- filter `DOCS_INDEX.csv` for docs with `in_md_links == 0` to see orphans

