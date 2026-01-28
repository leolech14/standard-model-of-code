# Refinery Infrastructure - Complete Subsystem Map
**Date:** 2026-01-27
**Status:** CURRENT ARCHITECTURE + EXPANSION OPPORTUNITIES
**Purpose:** Catalog what exists, identify what to build next

---

## TOP-LEVEL ARCHITECTURE

```
REFINERY (Knowledge Consolidation Infrastructure)
│
├── CONTEXT REFINERY (Corpus Processing)
│   └── context-management/tools/refinery/
│
├── ACI REFINERY (Semantic Chunking)
│   └── context-management/tools/ai/aci/refinery.py
│
├── QUERY SYSTEM (Search & Retrieval) ← BUILT THIS SESSION
│   └── context-management/tools/refinery/query_chunks.py
│
├── REPORTING SYSTEM (Activity & Library) ← BUILT THIS SESSION
│   └── context-management/tools/refinery/refinery_report.py
│
└── OUTPUT STORAGE (Intelligence Layer)
    └── context-management/intelligence/ + .agent/intelligence/chunks/
```

---

## SUBSYSTEM 1: CONTEXT REFINERY (5 Modules)

### Location
`context-management/tools/refinery/`

### Modules

#### 1.1 **Corpus Inventory** (corpus_inventory.py - 9,150 bytes)
**Purpose:** Scan and categorize ALL project files

**What it does:**
- Walks entire repository
- Classifies files by: language, category, size
- Tracks: total files, total bytes, total lines
- Generates: corpus_inventory.json

**Output:**
```json
{
  "summary": {
    "total_files": 2899,
    "total_bytes": 3136852407,
    "total_lines": 1661741
  },
  "by_language": {...},
  "by_category": {...}
}
```

**Status:** ✅ WORKING (last run: Jan 24)

---

#### 1.2 **Boundary Mapper** (boundary_mapper.py - 7,237 bytes)
**Purpose:** Map analysis_sets.yaml to boundary nodes

**What it does:**
- Loads analysis_sets.yaml (38 boundaries)
- Expands glob patterns to file lists
- Applies exclusions
- Creates BoundaryNode for each set

**Output:**
```json
{
  "boundaries": [
    {
      "name": "brain",
      "include_patterns": ["context-management/**"],
      "matched_files": [...],
      "file_count": 523
    }
    // ... 37 more
  ],
  "summary": {
    "boundaries": 38,
    "total_files_mapped": 10043
  }
}
```

**Status:** ✅ WORKING (overlap factor: 17.47 - files appear in multiple boundaries)

---

#### 1.3 **Delta Detector** (delta_detector.py - 7,229 bytes)
**Purpose:** Detect file changes since last run

**What it does:**
- Compares current files vs baseline
- Identifies: added, modified, deleted
- Tracks content hashes
- Generates: delta_report.json

**Output:**
```json
{
  "summary": {
    "has_changes": true,
    "added": 14,
    "modified": 0,
    "deleted": 0
  },
  "added_files": [...]
}
```

**Status:** ✅ WORKING (last run: Jan 24)

---

#### 1.4 **Atom Generator** (atom_generator.py - 11,696 bytes)
**Purpose:** Create RefineryNode entries for boundaries

**What it does:**
- Takes boundary definitions
- Generates atomic "knowledge atoms"
- Assigns 8D coordinates (what, layer, role, boundary, etc.)
- Creates: atoms_brain.json, atoms_body.json

**Output:**
```json
{
  "summary": {
    "atoms_generated": 165,
    "boundary": "brain"
  },
  "atoms": [
    {
      "id": "ATOM-brain-001",
      "type": "knowledge_atom",
      "content": "...",
      "dimensions": {...}
    }
  ]
}
```

**Status:** ✅ WORKING (295 atoms total: 130 body + 165 brain)

---

#### 1.5 **State Synthesizer** (state_synthesizer.py - 8,930 bytes)
**Purpose:** Produce global state/live.yaml

**What it does:**
- Loads: corpus_inventory, boundaries, delta_report, atoms
- Synthesizes into single coherent state
- Tracks: health indicators, overlap metrics
- Generates: live.yaml

**Output:**
```yaml
version: 1.0.0
corpus:
  total_files: 2899
  total_bytes: 3.1GB
boundaries:
  count: 38
  unique_files: None  # Honest about truncated data
  overlap_factor: None
atoms:
  total: 295
delta:
  has_changes: true
  added: 14
```

**Status:** ✅ WORKING (updated this session with overlap metrics)

---

## SUBSYSTEM 2: ACI REFINERY (1 Large Module)

### Location
`context-management/tools/ai/aci/refinery.py` (761 lines)

### Components

#### 2.1 **EmbeddingEngine** (Singleton)
**Purpose:** Generate vector embeddings for semantic search

**Features:**
- Model: all-MiniLM-L6-v2 (384 dimensions, 22M params)
- Speed: ~15ms per 1K tokens
- Lazy loading (only when needed)
- Batch processing

**Status:** ✅ WORKING (optional, requires sentence-transformers)

---

#### 2.2 **FileChunkers** (4 Strategy Classes)
**Purpose:** Semantic chunking by file type

**Strategies:**
- **PythonChunker:** Splits by functions, classes, imports
- **MarkdownChunker:** Splits by header sections (h1, h2, h3)
- **YamlChunker:** Splits by top-level keys
- **GenericChunker:** Splits by paragraphs (blank lines)

**Status:** ✅ WORKING (produces 2,673 chunks)

---

#### 2.3 **RefineryNode** (DataClass)
**Purpose:** Atomic chunk with metadata

**Schema:**
```python
@dataclass
class RefineryNode:
    content: str            # The chunk text
    source_file: str        # Origin file
    chunk_id: str           # SHA256-based ID
    chunk_type: str         # function, class, h1, h2, etc.
    relevance_score: float  # 0.0-1.0
    start_line: int
    end_line: int
    metadata: dict
    created_at: float
    embedding: List[float]  # 384-dim vector (optional)
```

**Status:** ✅ WORKING

---

#### 2.4 **Refinery Class** (Main Engine)
**Purpose:** Orchestrate chunking, scoring, export

**Features:**
- File type detection
- Chunking strategy selection
- Relevance scoring
- Vector embedding generation
- JSON export with validation ← ADDED THIS SESSION
- Incremental processing (cache) ← READY TO IMPLEMENT

**Status:** ✅ WORKING (just enhanced with validation gates)

---

## SUBSYSTEM 3: QUERY SYSTEM (Built This Session)

### Location
`context-management/tools/refinery/query_chunks.py` (165 lines)

### Features
- Text search over 2,673 chunks
- Relevance ranking (match score = base_relevance + match_count × 0.1)
- Preview extraction (100 chars around match)
- File path + line numbers
- `--limit N` flag
- `--context` flag for full content
- `--json` output

**Status:** ✅ WORKING (tested, integrated into ./pe refinery search)

---

## SUBSYSTEM 4: REPORTING SYSTEM (Built This Session)

### Location
`context-management/tools/refinery/refinery_report.py` (230 lines)

### Reports

#### 4.1 **Activity Report**
**Command:** `./pe refinery report`

**Shows:**
- Last update timestamp
- Total chunks/tokens
- Activity log (file changes, wire runs)
- Knowledge library summary
- Available commands

---

#### 4.2 **Library View**
**Command:** `./pe refinery library`

**Shows:**
- Top 20 files by chunk count
- Chunks + tokens per file
- Chunk type distribution
- Total: 2,673 chunks across 207 files

---

#### 4.3 **Changes Log**
**Command:** `./pe refinery changes`

**Shows:**
- Filesystem watcher activity
- Wire run history
- Last regeneration time

**Status:** ✅ WORKING (reads from filesystem_watcher.log)

---

## SUBSYSTEM 5: OUTPUT STORAGE

### Location 1: Context Intelligence
`context-management/intelligence/`

```
intelligence/
├── corpus_inventory.json    901 KB  # All files categorized
├── boundaries.json          106 KB  # 38 boundaries mapped
├── delta_state.json         302 KB  # Change tracking
├── atoms/
│   ├── atoms_brain.json     213 KB  # 165 atoms
│   └── atoms_body.json      165 KB  # 130 atoms
└── state/
    └── live.yaml            1.6 KB  # Current state
```

---

### Location 2: Agent Intelligence
`.agent/intelligence/chunks/`

```
chunks/
├── agent_chunks.json        1.9 MB  # 1,967 chunks
├── core_chunks.json         1.4 MB  # 598 chunks
├── aci_chunks.json          170 KB  # 108 chunks
├── metadata.json            367 B   # Generation metadata
├── cache.yaml               ← READY TO USE (incremental processing)
└── .gitignore               ← ADDED THIS SESSION
```

---

## COMPLETE REFINERY STACK

```
┌─────────────────────────────────────────────────────────┐
│                    REFINERY INFRASTRUCTURE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  INPUT LAYER (File System)                              │
│  ├─ Corpus Inventory: Scan all files                    │
│  ├─ Boundary Mapper: Map to analysis sets               │
│  └─ Delta Detector: Track changes                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PROCESSING LAYER (Atomization)                         │
│  ├─ Atom Generator: Create knowledge atoms              │
│  ├─ ACI Refinery: Semantic chunking                     │
│  │  ├─ PythonChunker                                    │
│  │  ├─ MarkdownChunker                                  │
│  │  ├─ YamlChunker                                      │
│  │  └─ GenericChunker                                   │
│  ├─ Embedding Engine: Vector generation (optional)      │
│  └─ Validation Gates: Prevent corruption ← NEW          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SYNTHESIS LAYER (Consolidation)                        │
│  ├─ State Synthesizer: Produce live.yaml                │
│  ├─ Convergence Detector: Prevent re-processing ← NEW   │
│  └─ Metadata Tracker: Git SHA + timestamp ← NEW         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  QUERY LAYER (Retrieval) ← NEW                          │
│  ├─ Text Search: query_chunks.py                        │
│  ├─ Semantic Search: embeddings (ready, not active)     │
│  └─ Library Browser: File organization                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  REPORTING LAYER (Observability) ← NEW                  │
│  ├─ Activity Report: What happened                      │
│  ├─ Library View: Organized catalog                     │
│  └─ Changes Log: Recent updates                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## WHAT'S MISSING (Expansion Opportunities)

### MISSING LAYER 1: Incremental Processing
**Gap:** Re-processes all 2,673 chunks even if only 1 file changed
**Need:** File-level hash cache (cache.yaml exists but not used)
**Effort:** 2 hours
**Impact:** 100x faster updates

---

### MISSING LAYER 2: Semantic Search
**Gap:** Only text search works, embeddings generated but not indexed
**Need:** Vector index (FAISS or numpy cosine similarity)
**Effort:** 2 hours
**Impact:** Better retrieval quality ("purpose field" finds relevant chunks even without exact match)

---

### MISSING LAYER 3: Research Depth Tracking
**Gap:** 1,068 research files saved but not organized by depth
**Need:** Depth metadata + index (D0 → D5)
**Effort:** 4 hours
**Impact:** See research progression, trace code to theory

---

### MISSING LAYER 4: Cloud Sync
**Gap:** Chunks only local, not in GCS
**Need:** Upload chunks/ to gs://elements-archive-2026/refinery/
**Effort:** 30 minutes
**Impact:** Dashboard can read chunks when Mac is off

---

### MISSING LAYER 5: Historical Snapshots
**Gap:** Only current chunks, no history
**Need:** Timestamped snapshots (chunks_YYYYMMDD_HHMMSS/)
**Effort:** 1 hour
**Impact:** Time-travel queries, see knowledge evolution

---

### MISSING LAYER 6: Cross-Boundary Analysis
**Gap:** Boundaries tracked but not analyzed for relationships
**Need:** Boundary dependency graph, overlap heat map
**Effort:** 2 hours
**Impact:** Understand knowledge distribution, find gaps

---

### MISSING LAYER 7: Knowledge Health Metrics
**Gap:** No metrics on knowledge quality
**Need:** Coverage %, staleness detection, duplication analysis
**Effort:** 2 hours
**Impact:** Know when knowledge degrades, needs refresh

---

### MISSING LAYER 8: Auto-Cleanup
**Gap:** Chunks accumulate, no pruning
**Need:** GCS lifecycle policies, local cleanup scripts
**Effort:** 1 hour
**Impact:** Prevent storage bloat

---

## CURRENT SUBSYSTEMS (What Exists)

| Subsystem | Lines | Status | Purpose |
|-----------|-------|--------|---------|
| **corpus_inventory** | ~300 | ✅ Working | Scan all files |
| **boundary_mapper** | ~230 | ✅ Working | Map analysis sets |
| **delta_detector** | ~240 | ✅ Working | Track changes |
| **atom_generator** | ~390 | ✅ Working | Create knowledge atoms |
| **state_synthesizer** | ~300 | ✅ Enhanced | Produce live.yaml |
| **aci/refinery** | ~761 | ✅ Enhanced | Semantic chunking |
| **query_chunks** | ~165 | ✅ NEW | Text search |
| **refinery_report** | ~230 | ✅ NEW | Activity/library reports |

**Total:** 8 subsystems, ~2,800 lines of code

---

## DATA FLOW

```
File System
    ↓
corpus_inventory.py → corpus_inventory.json (2,899 files cataloged)
    ↓
boundary_mapper.py → boundaries.json (38 boundaries, 10,043 mappings)
    ↓
delta_detector.py → delta_report.json (14 changes detected)
    ↓
atom_generator.py → atoms_*.json (295 atoms generated)
    ↓
aci/refinery.py → *_chunks.json (2,673 chunks, 539K tokens)
    ↓
state_synthesizer.py → live.yaml (consolidated state)
    ↓
query_chunks.py → Search results (instant retrieval)
    ↓
refinery_report.py → Activity reports (what happened)
```

---

## EXPANSION ROADMAP

### TIER 1: Performance (4 hours)
1. ✅ Validation gates (DONE)
2. ✅ Convergence detection (DONE)
3. ⬜ Incremental processing (2h)
4. ⬜ Semantic search (2h)

**Result:** 100x faster, better retrieval

---

### TIER 2: Cloud Integration (2 hours)
1. ⬜ Upload chunks to GCS (30min)
2. ⬜ Historical snapshots (1h)
3. ⬜ GCS lifecycle policies (30min)

**Result:** 24/7 availability, time-travel

---

### TIER 3: Knowledge Analytics (6 hours)
1. ⬜ Research depth tracking (4h)
2. ⬜ Cross-boundary analysis (2h)
3. ⬜ Knowledge health metrics (2h - can overlap with #2)

**Result:** Understand knowledge quality, see research progression

---

### TIER 4: Advanced Features (8 hours)
1. ⬜ Auto-cleanup policies (1h)
2. ⬜ Knowledge graph (3h - link chunks via references)
3. ⬜ Concept extraction (2h - identify key concepts)
4. ⬜ Duplicate detection (2h - find redundant chunks)

**Result:** Self-maintaining, self-optimizing knowledge base

---

## INNER TOP-LEVEL SUBSYSTEMS (What You Asked For)

### 1. **Inventory** (corpus_inventory.py)
Scans entire file system, categorizes everything

### 2. **Boundaries** (boundary_mapper.py)
Maps semantic regions (brain, body, pipeline, etc.)

### 3. **Delta** (delta_detector.py)
Tracks what changed since last run

### 4. **Atoms** (atom_generator.py)
Creates knowledge atoms with 8D coordinates

### 5. **Chunks** (aci/refinery.py)
Semantic chunking into queryable pieces

### 6. **Synthesis** (state_synthesizer.py)
Consolidates all into single state (live.yaml)

### 7. **Query** (query_chunks.py) ← NEW
Search and retrieve knowledge

### 8. **Reports** (refinery_report.py) ← NEW
Activity logs and library views

---

## WHAT TO EXPAND NEXT

**Highest Value:**
1. **Incremental Processing** (2h) - 100x faster updates
2. **Semantic Search** (2h) - Better retrieval quality
3. **Cloud Sync** (30min) - 24/7 availability

**High Value:**
4. **Research Depth** (4h) - Organize 1,068 research files by depth
5. **Knowledge Health** (2h) - Metrics on quality

**Medium Value:**
6. **Historical Snapshots** (1h) - Time-travel queries
7. **Cross-Boundary** (2h) - Understand relationships

**Low Priority:**
8. **Auto-Cleanup** (1h) - Prevent bloat
9. **Knowledge Graph** (3h) - Link chunks
10. **Deduplication** (2h) - Find redundancies

---

## RECOMMENDATION

**Expand in this order:**

**Phase 1 (4.5h):** Performance + Core Features
- Incremental processing (2h)
- Semantic search (2h)
- Cloud sync (30min)

**Phase 2 (6h):** Intelligence
- Research depth tracking (4h)
- Knowledge health metrics (2h)

**Phase 3 (6h):** Advanced
- Historical snapshots (1h)
- Cross-boundary analysis (2h)
- Knowledge graph (3h)

**Total: 16.5 hours to complete Refinery infrastructure**

---

**WHICH SUBSYSTEMS SHALL WE BUILD NEXT?**

The top-level architecture has 8 subsystems. We can expand any of them or add new ones.

