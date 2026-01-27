# Refinery - Minimal Viable Path
**Created:** 2026-01-27 04:45
**Objective:** MINIMAL work to start consolidating repo knowledge
**Principle:** Start local, prove value, then scale to cloud

---

## CURRENT STATE ASSESSMENT

### What Works RIGHT NOW
✅ **refinery.py** - Atomizes files into semantic chunks
✅ **State synthesizer** - Creates live.yaml corpus state
✅ **Enrichment orchestrator** - Runs refinery as Step 0
✅ **GCS bucket** - exists, accessible
✅ **Chunk storage** - .agent/intelligence/chunks/*.json

### What's Generated Today
```
Chunks: 2,654 total (~536K tokens)
├── agent_chunks.json:  1,948 chunks  ~217K tokens
├── core_chunks.json:     598 chunks  ~289K tokens
└── aci_chunks.json:      108 chunks   ~29K tokens

State: live.yaml
├── 2,899 files tracked
├── 34 boundaries mapped
├── 295 atoms generated
└── 14 pending changes detected
```

### What's Missing
❌ **Systematic execution** - Refinery runs on-demand, not continuously
❌ **Search capability** - Chunks exist but can't query them
❌ **Integration** - Not wired into analyze.py or Decision Deck
❌ **Time-series** - No historical tracking (only current state)

---

## THE MINIMAL PATH (3 Implementation Tiers)

### TIER 1: LOCAL CONSOLIDATION (1-2 hours)
**Goal:** Refinery runs systematically and accumulates knowledge locally

**What to build:**
1. Add refinery to wire.py pipeline (after COMM_FABRIC)
2. Store chunks with timestamps
3. Create simple query interface

**Files to modify:**
- `.agent/tools/wire.py` - Add REFINERY stage
- `.agent/intelligence/chunks/` - Add timestamped subdirs
- Create `query_chunks.py` - Simple grep-like search

**Result:**
- Every `./pe wire` run updates chunk index
- Can query: `./pe refinery search "pipeline stages"`
- Historical snapshots preserved

**Effort:** 1-2 hours
**Cost:** $0 (all local)

---

### TIER 2: SMART SEARCH (2-3 hours)
**Goal:** Semantic search over consolidated knowledge

**What to build:**
1. Generate embeddings for all chunks (if not exists)
2. Build vector index (FAISS or simple numpy)
3. Expose via CLI

**Files to create:**
- `context-management/tools/refinery/search_index.py`
- `.agent/intelligence/chunks/embeddings.npy` (vector index)

**Usage:**
```bash
./pe refinery search "How does purpose emerge?"
→ Returns top 5 relevant chunks with similarity scores

./pe refinery ask "What are all the atoms?"
→ Searches chunks + synthesizes answer
```

**Effort:** 2-3 hours (embeddings already supported in refinery.py)
**Cost:** $0 (all local)

---

### TIER 3: CLOUD BACKUP (30 minutes)
**Goal:** Mirror consolidated knowledge to GCS

**What to build:**
1. Create `gs://elements-archive-2026/refinery/chunks/`
2. Add upload to wire.py after REFINERY stage
3. Optional: Download on startup for multi-machine sync

**Files to modify:**
- `.agent/tools/wire.py` - Add GCS upload after chunk generation
- Or: `sync_to_cloud.sh` - Include chunks/ directory

**Result:**
- Chunks backed up to cloud
- Can query from any machine
- Foundation for future cloud processing

**Effort:** 30 minutes
**Cost:** ~$0.01/month (storage only)

---

## TIER 1 DETAILED IMPLEMENTATION

### Step 1: Add Refinery to wire.py

**Add after Communication Fabric stage:**

```python
# Stage 7: Refinery (Knowledge Consolidation)
REFINERY_SCRIPT = REPO_ROOT / "context-management" / "tools" / "ai" / "aci" / "refinery.py"
CHUNKS_DIR = INTELLIGENCE_DIR / "chunks"

stages.append(PipelineStage(
    "REFINERY",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / ".agent"),
     "--export", str(CHUNKS_DIR / "agent_chunks.json")],
    "Atomize .agent/ into semantic chunks"
))

stages.append(PipelineStage(
    "REFINERY_CORE",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "standard-model-of-code" / "src" / "core"),
     "--export", str(CHUNKS_DIR / "core_chunks.json")],
    "Atomize collider core into semantic chunks"
))

stages.append(PipelineStage(
    "REFINERY_ACI",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "context-management" / "tools" / "ai" / "aci"),
     "--export", str(CHUNKS_DIR / "aci_chunks.json")],
    "Atomize ACI tools into semantic chunks"
))
```

**Verification:**
```bash
./pe wire --quick
# Should show REFINERY stages running
# Should update .agent/intelligence/chunks/*.json
```

**Effort:** 15 minutes

---

### Step 2: Add Timestamp Tracking

**Create chunk metadata file:**

```python
# In wire.py after refinery stages
import json
from datetime import datetime

chunk_metadata = {
    "generated_at": datetime.now().isoformat(),
    "chunks": {
        "agent": len(json.load(open(CHUNKS_DIR / "agent_chunks.json"))["nodes"]),
        "core": len(json.load(open(CHUNKS_DIR / "core_chunks.json"))["nodes"]),
        "aci": len(json.load(open(CHUNKS_DIR / "aci_chunks.json"))["nodes"]),
    },
    "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
}

with open(CHUNKS_DIR / "metadata.json", 'w') as f:
    json.dump(chunk_metadata, f, indent=2)
```

**Effort:** 10 minutes

---

### Step 3: Simple Query Interface

**Create:** `context-management/tools/refinery/query_chunks.py`

```python
#!/usr/bin/env python3
"""
Simple chunk query interface.
Usage: python query_chunks.py "search term"
"""

import json
import sys
from pathlib import Path

CHUNKS_DIR = Path(__file__).parents[4] / ".agent" / "intelligence" / "chunks"

def search_chunks(query: str, top_k: int = 10):
    """Search chunks by text match."""
    results = []

    for chunk_file in CHUNKS_DIR.glob("*_chunks.json"):
        with open(chunk_file) as f:
            data = json.load(f)

        for node in data["nodes"]:
            content = node["content"].lower()
            if query.lower() in content:
                results.append({
                    "file": chunk_file.stem,
                    "type": node["chunk_type"],
                    "source": node["source_file"].split("/")[-1],
                    "line": node["start_line"],
                    "relevance": node["relevance_score"],
                    "preview": content[:200],
                })

    # Sort by relevance
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_chunks.py 'search term'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    results = search_chunks(query)

    print(f"\n=== Found {len(results)} matches for '{query}' ===\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. [{r['source']}:{r['line']}] {r['type']} (rel: {r['relevance']:.2f})")
        print(f"   {r['preview'][:100]}...\n")
```

**Add to ./pe:**

```bash
cmd_refinery() {
    case "${1:-help}" in
        search)
            shift
            python3 "$TOOLS/refinery/query_chunks.py" "$@"
            ;;
        stats)
            python3 "$TOOLS/refinery/state_synthesizer.py"
            ;;
        *)
            echo "Usage: ./pe refinery <command>"
            echo ""
            echo "Commands:"
            echo "  search <query>   Search consolidated knowledge"
            echo "  stats            Show corpus statistics"
            ;;
    esac
}
```

**Effort:** 20 minutes

---

## TIER 1 COMPLETE CAPABILITIES

After Tier 1 (1-2 hours), you can:

```bash
# Update consolidated knowledge
./pe wire
→ Generates 2,654 chunks from .agent/, core/, aci/
→ Updates metadata with timestamp and git SHA

# Search consolidated knowledge
./pe refinery search "purpose emergence"
→ Returns: 5 relevant chunks from across codebase

./pe refinery search "cloud deployment"
→ Returns: All chunks mentioning cloud/GCP

# View corpus state
./pe refinery stats
→ Shows: 2,899 files, 34 boundaries, 295 atoms
```

**What this enables:**
- Agents can query consolidated knowledge before decisions
- Historical tracking (metadata.json per run)
- Foundation for semantic search (Tier 2)
- Foundation for cloud sync (Tier 3)

---

## TIER 2: SEMANTIC SEARCH (If Needed)

**Only do this if text search isn't enough.**

```bash
# One-time: Generate embeddings for all chunks
./pe refinery embed

# Semantic search
./pe refinery ask "How does the Standard Model classify code?"
→ Returns chunks semantically similar to query
```

**Requirements:**
- sentence-transformers installed
- ~384 dimensional vectors per chunk
- FAISS or numpy for similarity search

**Effort:** 2-3 hours
**Benefit:** Better retrieval than text match

---

## TIER 3: CLOUD BACKUP (If Multi-Machine)

**Only do this if you need cross-machine sync.**

```bash
# Auto-backup after wire run
./pe wire
→ Uploads chunks/ to gs://elements-archive-2026/refinery/

# Pull latest on another machine
./pe refinery pull
→ Downloads latest chunks from GCS
```

**Effort:** 30 minutes
**Cost:** ~$0.01/month

---

## THE MINIMAL ANSWER

**To start consolidating repo knowledge with proper configuration:**

### Absolute Minimum (45 min):
1. ✅ Fix refinery.py bug (DONE TODAY - was skipping .agent/)
2. Add 3 refinery stages to wire.py (~15 min)
3. Add timestamped metadata tracking (~10 min)
4. Add `./pe refinery search` command (~20 min)

**Result:**
- Every `./pe wire` run updates consolidated knowledge
- Can search via `./pe refinery search "query"`
- Chunks backed by git (in .agent/intelligence/chunks/)

**No cloud, no embeddings, no complex infrastructure.**

---

## PROPOSED IMMEDIATE STEPS

### 1. Resolve L0-L3 naming collision (5 min)
Update CLOUD_REFINERY_SPEC.md: L0-L5 → R0-R5

### 2. Wire refinery into pipeline (15 min)
Add 3 stages to wire.py

### 3. Add query interface (20 min)
Create query_chunks.py + ./pe refinery command

### 4. Test end-to-end (10 min)
```bash
./pe wire          # Generate chunks
./pe refinery search "Communication Fabric"  # Query
```

**Total: 50 minutes to working knowledge consolidation**

---

**Want me to execute this minimal path?** Or do you prefer a different configuration?
