# Refinery Natural Subsystems - Optimal Decomposition
**Date:** 2026-01-27
**Question:** What is the SIMPLEST, MOST STABLE subsystem structure?
**Method:** Find natural boundaries by analyzing essential functions

---

## THE CORE QUESTION

**Not:** "What could we build?"
**But:** "What MUST exist for Refinery to work?"

**Finding:** The minimal, most direct, most aligned decomposition

---

## FUNCTIONAL ANALYSIS

### What Does Refinery Actually Do?

**Input:** Repository files (2,899 files, 3.1 GB)
**Output:** Queryable knowledge (2,673 chunks, 539K tokens)

**Core Functions:**
1. **SCAN** - Find all files
2. **CHUNK** - Break into semantic pieces
3. **INDEX** - Make searchable
4. **QUERY** - Retrieve relevant pieces
5. **SYNTHESIZE** - Consolidate state

**That's it. 5 functions. Everything else is support.**

---

## NATURAL SUBSYSTEM BOUNDARIES (The Stable Configuration)

### By Analyzing Essential Functions:

```
REFINERY
│
├─ SCANNER          (Find what exists)
├─ CHUNKER          (Break into pieces)
├─ INDEXER          (Make searchable)
├─ QUERIER          (Retrieve pieces)
└─ SYNTHESIZER      (Consolidate state)
```

**These are the NATURAL boundaries** - they can't be decomposed further without losing coherence.

---

## SUBSYSTEM 1: SCANNER

**Purpose:** Find all files in repository
**Input:** File system
**Output:** File manifest (paths, sizes, mtimes, types)

**Core Responsibility:**
- Walk directory tree
- Classify file types
- Detect changes (delta)
- Exclude junk (.git, .venv, etc.)

**Current Implementation:**
- corpus_inventory.py (scan + classify)
- delta_detector.py (detect changes)

**Optimal Structure:**
```
scanner/
├── walk.py          # Directory traversal
├── classify.py      # File type detection
├── delta.py         # Change detection
└── exclude.py       # Skip patterns
```

**Or simpler (RECOMMENDED):**
```
scanner.py           # All scanning logic in one module
```

**Lines:** ~400 (combined corpus_inventory + delta_detector)
**Status:** Currently split across 2 files, could be 1

---

## SUBSYSTEM 2: CHUNKER

**Purpose:** Break files into semantic pieces
**Input:** File content
**Output:** RefineryNode chunks

**Core Responsibility:**
- Detect file type (Python, Markdown, YAML, etc.)
- Apply appropriate chunking strategy
- Generate chunk IDs
- Score relevance
- Optionally: Generate embeddings

**Current Implementation:**
- aci/refinery.py (all chunking logic)

**Optimal Structure:**
```
chunker/
├── strategies/
│   ├── python.py        # PythonChunker
│   ├── markdown.py      # MarkdownChunker
│   ├── yaml.py          # YamlChunker
│   └── generic.py       # GenericChunker
├── embeddings.py        # EmbeddingEngine
├── scoring.py           # Relevance scoring
└── __init__.py          # Refinery class (orchestrator)
```

**Or simpler (CURRENT is actually GOOD):**
```
chunker.py               # All in one file (current: aci/refinery.py)
```

**Lines:** ~761 (current aci/refinery.py)
**Status:** Already well-structured, no split needed

---

## SUBSYSTEM 3: INDEXER

**Purpose:** Make chunks searchable
**Input:** RefineryNode chunks
**Output:** Search index

**Core Responsibility:**
- Build text index (for fast search)
- Build vector index (for semantic search)
- Build metadata index (by file, type, etc.)
- Update incrementally

**Current Implementation:**
- ❌ NOT IMPLEMENTED (search is brute-force over JSON)

**Optimal Structure:**
```
indexer.py
├── build_text_index()      # For keyword search
├── build_vector_index()    # For semantic search
├── build_metadata_index()  # For filtering
└── update_incremental()    # Only index changed chunks
```

**Lines:** ~200 (estimated)
**Status:** MISSING - Currently just loads all JSON and searches

---

## SUBSYSTEM 4: QUERIER

**Purpose:** Retrieve relevant chunks
**Input:** Query string
**Output:** Ranked results

**Core Responsibility:**
- Text search (current)
- Semantic search (embeddings)
- Filter by metadata
- Rank by relevance
- Format results

**Current Implementation:**
- query_chunks.py (text search only)

**Optimal Structure:**
```
querier.py
├── text_search()       # Keyword matching
├── semantic_search()   # Vector similarity
├── filter_by()         # Metadata filtering
├── rank_results()      # Relevance scoring
└── format_output()     # Result formatting
```

**Lines:** ~165 (current query_chunks.py)
**Status:** Basic implementation, needs semantic search

---

## SUBSYSTEM 5: SYNTHESIZER

**Purpose:** Consolidate all data into coherent state
**Input:** All refinery outputs
**Output:** Single source of truth (live.yaml)

**Core Responsibility:**
- Load all outputs (corpus, boundaries, atoms, chunks)
- Merge into unified view
- Calculate aggregate metrics
- Detect health issues
- Generate summary

**Current Implementation:**
- state_synthesizer.py
- boundary_mapper.py (partial - creates boundaries.json)

**Optimal Structure:**
```
synthesizer.py
├── load_all_sources()      # Import all data
├── merge_state()           # Consolidate
├── calculate_metrics()     # Aggregate stats
├── detect_issues()         # Health checks
└── write_live_yaml()       # Output
```

**Lines:** ~300 (current state_synthesizer.py)
**Status:** Good, but boundary_mapper should be part of Scanner, not Synthesizer

---

## THE NATURAL ARCHITECTURE (Most Stable)

```
REFINERY
│
├── scanner.py              # File discovery + classification + delta
│   ├── walk_directory()
│   ├── classify_file()
│   ├── detect_changes()
│   └── map_boundaries()    ← Move from boundary_mapper
│
├── chunker.py              # Semantic atomization
│   ├── Refinery class (orchestrator)
│   ├── FileChunker strategies (Python, MD, YAML)
│   ├── EmbeddingEngine (optional)
│   └── Validation gates
│
├── indexer.py              # Make searchable ← NEW SUBSYSTEM
│   ├── build_indexes()
│   ├── update_incremental()
│   └── persist_to_disk()
│
├── querier.py              # Retrieve knowledge
│   ├── text_search()
│   ├── semantic_search()
│   └── rank_results()
│
├── synthesizer.py          # Consolidate state
│   ├── merge_all_sources()
│   ├── calculate_health()
│   └── write_live_yaml()
│
└── reporter.py             # Observability
    ├── activity_report()
    ├── library_view()
    └── changes_log()
```

**6 subsystems. Each does ONE thing. Minimal, direct, effective.**

---

## COMPARISON: CURRENT vs OPTIMAL

| Current | Lines | Optimal | Lines | Change |
|---------|-------|---------|-------|--------|
| corpus_inventory.py | 300 | scanner.py | 400 | Merge with delta |
| delta_detector.py | 240 | ↑ (merged) | ↑ | Consolidate |
| boundary_mapper.py | 230 | ↑ (merged) | ↑ | Part of scanning |
| atom_generator.py | 390 | **REMOVE** | 0 | Redundant with chunker |
| aci/refinery.py | 761 | chunker.py | 800 | Add validation |
| state_synthesizer.py | 300 | synthesizer.py | 300 | Keep as-is |
| query_chunks.py | 165 | querier.py | 250 | Add semantic |
| refinery_report.py | 230 | reporter.py | 230 | Keep as-is |
| **(none)** | 0 | **indexer.py** | 200 | ADD |

**Result:** 8 files → 6 subsystems
**Total Lines:** 2,616 → 2,180 (simpler!)

---

## WHY THIS IS THE STABLE CONFIGURATION

### 1. Scanner (Unified Discovery)
**Why one subsystem:**
- Scanning, delta detection, boundary mapping are ALL discovery
- They operate on the same input (file system)
- They produce related outputs (what files, what changed, what boundaries)
- Splitting them creates artificial boundaries

**Evidence:** corpus_inventory and delta_detector BOTH walk the file tree

---

### 2. Chunker (Semantic Atomization)
**Why one subsystem:**
- File type detection → chunking strategy → validation are ONE pipeline
- They operate on file content
- They produce uniform output (RefineryNode)
- Splitting breaks the flow

**Evidence:** Current aci/refinery.py already does this correctly

---

### 3. Indexer (NEW - Currently Missing)
**Why separate subsystem:**
- Indexing is DISTINCT from chunking
- Operates on chunks, not files
- Can be rebuilt from chunks alone
- Different update cycle (incremental)

**Evidence:** Text search currently brute-forces through JSON (no index)

---

### 4. Querier (Retrieval)
**Why separate from Indexer:**
- Querying uses indexes but has different logic
- Ranking, filtering, formatting are query-specific
- Can swap index implementations without changing querier

**Evidence:** query_chunks.py doesn't know about index structure

---

### 5. Synthesizer (State Consolidation)
**Why separate:**
- Operates on ALL subsystem outputs
- Different update cycle (after all others complete)
- Single responsibility: merge into coherent state

**Evidence:** Reads corpus, boundaries, atoms, chunks - doesn't generate them

---

### 6. Reporter (Observability)
**Why separate:**
- Read-only (doesn't modify state)
- User-facing (not part of processing pipeline)
- Can be disabled without breaking refinery

**Evidence:** refinery_report.py is pure display logic

---

## WHAT ABOUT ATOM_GENERATOR?

**Current:** atom_generator.py creates 295 "knowledge atoms"
**Question:** Is this redundant with Chunker?

**Analysis:**
- Atoms: Large-grain boundaries (brain, body)
- Chunks: Fine-grain semantic pieces (functions, classes)

**Are they different?** Let's check:

```python
# Atom (from atom_generator)
{
  "id": "ATOM-brain-001",
  "type": "knowledge_atom",
  "boundary": "brain",
  "files": [list of files in boundary]
}

# Chunk (from chunker)
{
  "id": "abc123",
  "type": "function",
  "source_file": "specific file",
  "content": "actual code/text"
}
```

**They're different granularities:**
- Atoms = boundary-level aggregation
- Chunks = file-level atomization

**Verdict:** Atoms are BOUNDARY aggregations → should be in Synthesizer, not separate subsystem

---

## THE FINAL OPTIMAL STRUCTURE

```
refinery/
│
├── scanner.py              # Discovery (files + boundaries + deltas)
│   ├── scan_files()
│   ├── classify_files()
│   ├── detect_deltas()
│   └── map_boundaries()
│
├── chunker.py              # Atomization (semantic chunking)
│   ├── Refinery class
│   ├── FileChunker strategies
│   ├── Validation gates
│   └── Embeddings (optional)
│
├── indexer.py              # Indexing (make searchable) ← NEW
│   ├── build_text_index()
│   ├── build_vector_index()
│   └── update_incremental()
│
├── querier.py              # Retrieval (search + rank)
│   ├── search()
│   ├── rank()
│   └── format()
│
├── synthesizer.py          # Consolidation (state + atoms + health)
│   ├── merge_sources()
│   ├── generate_atoms()     ← Move from atom_generator
│   ├── calculate_health()
│   └── write_live_yaml()
│
└── reporter.py             # Observability (reports + views)
    ├── activity_report()
    ├── library_view()
    └── changes_log()
```

**6 subsystems. Clean separation. Natural boundaries.**

---

## WHY 6 (Not 8, Not 4)?

**Too Few (4):**
```
├── input.py     (scanner + chunker)    # Too much in one file
├── process.py   (indexer + synthesizer) # Unrelated functions
├── output.py    (querier + reporter)    # Mixed concerns
```
**Problem:** Violates single responsibility

**Too Many (Current 8):**
```
├── corpus_inventory.py     # All do discovery
├── boundary_mapper.py      # Should be together
├── delta_detector.py       # Artificial split
├── atom_generator.py       # Redundant with synthesizer
...
```
**Problem:** Artificial boundaries, harder to navigate

**Just Right (6):**
Each subsystem has ONE clear purpose, can't be split without losing coherence, can't be merged without mixing concerns.

---

## MIGRATION PATH (Current 8 → Optimal 6)

### Step 1: Merge Discovery Functions
```bash
# Create scanner.py merging:
- corpus_inventory.py (scan files)
- delta_detector.py (detect changes)
- boundary_mapper.py (map analysis sets)

Result: Single discovery subsystem
```

### Step 2: Rename & Clarify
```bash
# Rename for clarity:
aci/refinery.py → chunker.py (semantic atomization)
state_synthesizer.py → synthesizer.py (no rename needed)
query_chunks.py → querier.py (retrieval logic)
refinery_report.py → reporter.py (observability)
```

### Step 3: Create Missing Subsystem
```bash
# Add indexer.py (currently missing)
- Build text index from chunks
- Build vector index (optional)
- Enable fast search (not brute-force)
```

### Step 4: Move Atoms to Synthesizer
```bash
# Move atom_generator.py logic into synthesizer.py
# Atoms are aggregations of boundaries → part of synthesis
```

**Result:** 8 files → 6 subsystems (cleaner, more aligned)

---

## THE STABLE CONFIGURATION

### Why These 6 Are Stable:

**Scanner:**
- Natural boundary: Everything about discovering files
- Single input: File system
- Single output: File manifest + boundaries + deltas
- Can't split: All discovery functions need same file walk
- Can't merge: Discovery is distinct from processing

**Chunker:**
- Natural boundary: Everything about breaking content into pieces
- Single input: File content
- Single output: RefineryNode chunks
- Can't split: Type detection → strategy → validation is one pipeline
- Can't merge: Chunking logic is independent of scanning/indexing

**Indexer:**
- Natural boundary: Everything about making searchable
- Single input: Chunks
- Single output: Indexes (text, vector, metadata)
- Can't split: All indexes serve same purpose
- Can't merge: Indexing is separate from chunking and querying

**Querier:**
- Natural boundary: Everything about retrieval
- Single input: Query + indexes
- Single output: Ranked results
- Can't split: Search → rank → format is one operation
- Can't merge: Querying is separate from indexing

**Synthesizer:**
- Natural boundary: Everything about consolidating state
- Single input: All subsystem outputs
- Single output: live.yaml + atoms
- Can't split: State consolidation is atomic
- Can't merge: Synthesis depends on all others completing

**Reporter:**
- Natural boundary: Everything about observability
- Single input: Refinery state
- Single output: Human-readable reports
- Can't split: Reports are presentation layer
- Can't merge: Read-only, doesn't participate in processing

---

## SUBSYSTEM INTERFACES (How They Connect)

```python
# Scanner produces
{
  "files": [...],           # All files found
  "boundaries": {...},      # Semantic regions
  "deltas": {...}           # What changed
}

# Chunker consumes files, produces
{
  "chunks": [RefineryNode, ...]
}

# Indexer consumes chunks, produces
{
  "text_index": {...},      # For fast text search
  "vector_index": {...},    # For semantic search
  "metadata_index": {...}   # For filtering
}

# Querier consumes indexes + query, produces
{
  "results": [ranked chunks]
}

# Synthesizer consumes all outputs, produces
{
  "state": live.yaml,       # Consolidated state
  "atoms": [...],           # Boundary-level atoms
  "health": {...}           # Knowledge health
}

# Reporter consumes state, produces
{
  "reports": [activity, library, changes]
}
```

**Clean interfaces. Minimal coupling. Natural data flow.**

---

## WHAT'S REDUNDANT (Should Be Removed)

### Atom Generator as Separate Subsystem
**Current:** atom_generator.py (390 lines)
**Function:** Creates boundary-level aggregations
**Problem:** This is just BOUNDARY SUMMARIZATION → part of synthesis
**Recommendation:** Move into synthesizer.py

**Why redundant:**
- Atoms are derived from boundaries (which Scanner already maps)
- Atoms are aggregations (which Synthesizer already does)
- Atoms are stored in state (which Synthesizer produces)

**Evidence:**
```python
# atom_generator.py essentially does:
for boundary in boundaries:
    atom = summarize_boundary(boundary)
    atoms.append(atom)

# This IS synthesis, not a separate operation
```

---

## IMPLEMENTATION RECOMMENDATION

### Phase 1: Consolidate Scanner (2 hours)
```bash
# Create scanner.py merging:
- corpus_inventory.py (file walking)
- delta_detector.py (change detection)
- boundary_mapper.py (analysis set mapping)

# Delete originals, update imports
```

**Result:** 770 lines → 400 lines (simpler)

---

### Phase 2: Add Indexer (2 hours)
```bash
# Create indexer.py (NEW)
- Build text index for fast search
- Build vector index (if embeddings enabled)
- Persist indexes to disk
```

**Result:** Search goes from O(n) → O(log n), enables sub-100ms queries

---

### Phase 3: Enhance Querier (1 hour)
```bash
# Update querier.py to use indexes
- Remove brute-force search
- Use indexer.get_matches()
- Add semantic search option
```

**Result:** Fast queries, semantic understanding

---

### Phase 4: Move Atoms to Synthesizer (1 hour)
```bash
# Merge atom_generator.py into synthesizer.py
- Atoms are boundary aggregations
- Generated during synthesis
- No separate subsystem needed
```

**Result:** 390 lines removed, cleaner architecture

---

### Phase 5: Rename for Clarity (15 min)
```bash
# Clarify names:
aci/refinery.py → chunker.py (or keep current name)
query_chunks.py → querier.py
refinery_report.py → reporter.py
```

**Result:** Subsystem purpose obvious from name

**Total:** 6 hours to optimal structure

---

## THE ANSWER

### Current Inner Top-Level Subsystems:
1. corpus_inventory (scanner role)
2. boundary_mapper (scanner role)
3. delta_detector (scanner role)
4. atom_generator (synthesizer role - REDUNDANT)
5. aci/refinery (chunker role)
6. state_synthesizer (synthesizer role)
7. query_chunks (querier role)
8. refinery_report (reporter role)

**Total:** 8 files, some redundant, some split

---

### Optimal Natural Subsystems:
1. **Scanner** (discovery)
2. **Chunker** (atomization)
3. **Indexer** (searchability) ← MISSING
4. **Querier** (retrieval)
5. **Synthesizer** (consolidation)
6. **Reporter** (observability)

**Total:** 6 subsystems, clean boundaries, natural alignment

---

## STABILITY TEST

**Question:** Can we split any of these 6 further?
**Answer:** No - each is atomic

**Question:** Should we merge any of these 6?
**Answer:** No - each has distinct responsibility

**Question:** Are any missing?
**Answer:** No - covers full pipeline (discover → chunk → index → query → synthesize → report)

**Verdict:** **6 is the stable configuration** - the natural subsystem decomposition.

---

**SHALL I IMPLEMENT THE OPTIMAL 6-SUBSYSTEM ARCHITECTURE?**

6 hours to consolidate, add Indexer, and achieve the most stable, simple, direct, effective structure.
