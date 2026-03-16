# The Oracle — Atlas-Aware Knowledge Retrieval System

**Date:** 2026-03-16
**Status:** Vision (not yet designed)
**Predecessor:** `wave/tools/ai/analyze.py` (CMP-052, ACI Router, P3)
**Depends on:** Atlas scaffold (confirmed), Collider emitter (Stage 23)

---

## The Problem

Files exist everywhere. Knowledge is scattered across:
- `particle/docs/theory/` (277 files, 170K tokens)
- `atlas/ATLAS.yaml` (64 entities, ecosystem map)
- `wave/tools/ai/` (40+ Python tools with embedded domain knowledge)
- `_inbox/` (2,941 SMoC-related artifacts, audited but not indexed)
- `PROJECT_openclaw/` (273 files, voice/channels/agents architecture)
- Claude memory, Notion, Google Drive, Doppler

An agent that needs to answer "what's the health model formula?" must KNOW the file path. If it doesn't, it guesses or asks. That's cognitive load the system should eliminate.

## The Vision

A single entry point for ALL knowledge retrieval. The Oracle:

1. **Reads ATLAS.yaml at boot** -- knows every component, connection, agent, resource
2. **Has pre-built indexes** for theory, code, specs, _inbox artifacts, cross-project
3. **Routes queries via ACI** -- instant (atlas), RAG (indexed search), long context (full file), web (Perplexity)
4. **Returns answers with atlas-aware citations** -- not just "file:line" but "CMP-002 (Collider), incoherence.py:42, stage P3"
5. **Speaks atlas vocabulary** -- query results reference entity IDs, relationship types, blast radius

## What analyze.py Already Has (inherit)

- ACI 5-tier routing (instant, RAG, long_context, perplexity, flash_deep)
- Analysis sets (`wave/config/analysis_sets.yaml`)
- File search with citations (RAG stores)
- Stone Tool Output Contract (AnalyzeResult with run_id, timing, cost, context manifest)
- Auto-save to `research/auto-saves/`
- Longitudinal tracking (`.analyze/run_index.jsonl`)
- 6 modes (standard, forensic, architect, insights, role_validation, plan_validation)

## What the Oracle Adds (new)

- **Atlas-aware indexing:** Each indexed chunk tagged with its atlas entity ID
- **Automatic store building:** Collider emitter output → component-aware RAG stores
- **Cross-project reach:** Index PROJECT_elements + PROJECT_openclaw + _inbox
- **Query-time atlas enrichment:** Search result includes component identity, blast_radius, health status
- **Semantic routing:** "What's the health model?" auto-routes to L3_APPLICATIONS.md + incoherence.py without `--set`
- **Progressive disclosure:** First answer from atlas (10 tokens), then from RAG (100 tokens), then from full file (1000 tokens)

## Architecture Sketch

```
Query → Oracle
    ↓
Atlas lookup (instant): Does an entity match the query?
    ├── Yes → Return entity.agent.explanation + entity.source_file
    ├── Partial → Use entity to scope the RAG search
    └── No → Full ACI routing
    ↓
ACI Router (existing, enhanced)
    ├── RAG: Search atlas-tagged stores → return with entity citations
    ├── Long Context: Load component's source files (atlas.invoke.method → file path)
    ├── Perplexity: Web research with atlas context injection
    └── GraphRAG: Traverse Neo4j with atlas relationship types
    ↓
AnalyzeResult (Stone Tool Output Contract)
    + atlas_entities_referenced: [CMP-002, CON-001]
    + atlas_context: {component stage, health, blast_radius}
```

## Why This Matters

"Ingestion" stops being about moving files. It becomes about INDEXING.

- A file in `_inbox/` that's indexed by the Oracle is as accessible as a file in `particle/docs/`
- A file in `particle/docs/` that's NOT indexed is invisible to agents
- The atlas is the map. The Oracle is the librarian. The Collider is the observer.

## Design Principles

1. **Atlas-first:** Every query starts with an atlas lookup. The atlas is the shortest path to knowledge.
2. **Index, don't move:** Files can live anywhere. What matters is that they're indexed and atlas-referenced.
3. **Progressive disclosure:** Answer at the cheapest tier first. Escalate only if needed.
4. **Citation-rich:** Every answer traces back to source file + line + atlas entity.
5. **Self-improving:** Each query that fails to find an answer identifies a gap in the index.

## Implementation Approach

This is NOT a rewrite of analyze.py. It's a **new wrapper** that:
1. Adds an atlas lookup layer BEFORE ACI routing
2. Enhances the RAG store builder to tag chunks with atlas entity IDs
3. Adds a cross-project indexing capability
4. Enriches AnalyzeResult with atlas context

analyze.py (CMP-052) remains the engine. The Oracle is the intelligence layer on top.

## Relationship to Other Components

- **Collider emitter (Stage 23):** Produces component candidates → Oracle indexes them
- **Atlas (ATLAS.yaml):** Oracle reads at boot → scopes all queries
- **REH (CMP-060):** Oracle can query git history via REH MCP tools
- **Cerebras Intelligence MCP (CMP-061):** Oracle can delegate fast queries
- **Perplexity (CON-007):** Oracle uses for web research tier

## Open Questions

1. Should the Oracle be a new component (CMP-100?) or an evolution of analyze.py (CMP-052 v4)?
2. Should atlas-tagged RAG stores be persistent (SQLite) or rebuilt per session?
3. Should the Oracle expose MCP tools (query_knowledge, index_directory, find_entity)?
4. How does the Oracle interact with the _inbox artifacts without moving them?
5. Token budget for atlas-enriched search results vs plain citations?

---

*This is a vision document, not a spec. The next session should design the implementation.*
