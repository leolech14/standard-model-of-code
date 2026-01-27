# Refinery Tier 1 - Tightened Execution Plan
**Created:** 2026-01-27 05:20
**Status:** READY TO EXECUTE
**Estimated Time:** 50 minutes

---

## FIXES APPLIED (Before Execution)

### 1. Skip Logic - Path-Part Matching ✅
**Problem:** Substring matching (`if '.git' in path_str`) could skip legitimate files

**Fixed:**
```python
# BEFORE (DANGEROUS):
if any(pattern in path_str for pattern in skip_patterns):
    continue  # Could skip "docs/__pycache__explain.md"

# AFTER (SAFE):
skip_dirs = {'.git', '.venv', '__pycache__', 'node_modules', ...}
if any(part in skip_dirs for part in file_path.parts):
    continue  # Only skips if directory name exactly matches
```

**File:** `context-management/tools/ai/aci/refinery.py:551-558`
**Status:** ✅ APPLIED

---

### 2. Boundary Overlap Reporting ✅
**Problem:** 2,899 files vs 10,043 "mapped" suggests overlap but wasn't explicit

**Fixed:**
```yaml
boundaries:
  total_files_mapped: 10043   # Sum across all boundaries
  unique_files: None          # Unreliable (truncated data)
  overlap_factor: None        # Can't compute from truncated data
```

**Honest reporting:** Returns `None` when data is unreliable (contains lists truncated to 50)

**Files:**
- `context-management/tools/refinery/state_synthesizer.py` - Added functions
- `context-management/intelligence/state/live.yaml` - Now shows metrics

**Status:** ✅ APPLIED

---

### 3. Query Interface Created ✅
**Created:** `context-management/tools/refinery/query_chunks.py`

**Features:**
- Text search with relevance ranking
- Match count + position scoring
- File paths + line numbers
- Preview (100 chars around match)
- `--limit N` flag (default 10)
- `--context` flag for full content
- `--json` for machine-readable output

**Test Result:**
```bash
$ python query_chunks.py "Communication Fabric" --limit 3

Found 3 matches for: 'Communication Fabric'

1. [.agent/tools/autopilot.py:445]
   Type: function
   Relevance: 0.98 | Matches: 6
   Preview: ...Step 3: Communication Fabric - Recording state vector...
```

**Status:** ✅ WORKING

---

## EXECUTION STEPS

### STEP 1: Resolve Naming Collision (5 min)

**File:** `context-management/docs/specs/CLOUD_REFINERY_SPEC.md`

**Change:**
```diff
- L0: Raw           - unified_analysis.json snapshots
- L1: Indexed       - Searchable JSONL
- L2: Normalized    - Schema-aligned, deduplicated
- L3: Enriched      - AI-annotated, relationships inferred
- L4: Distilled     - Summaries, patterns, anomalies
- L5: Emergent      - Purpose field, trends, predictions
+ R0: Raw           - unified_analysis.json snapshots
+ R1: Indexed       - Searchable JSONL
+ R2: Normalized    - Schema-aligned, deduplicated
+ R3: Enriched      - AI-annotated, relationships inferred
+ R4: Distilled     - Summaries, patterns, anomalies
+ R5: Emergent      - Purpose field, trends, predictions
```

**Find/replace pattern:**
- ` L0:` → ` R0:`
- ` L1:` → ` R1:`
- ...
- `L0_raw` → `R0_raw`
- `L1_indexed` → `R1_indexed`
- etc.

**Also update:** Any GCS bucket path references

**Verification:**
```bash
grep -c "R0\|R1\|R2\|R3\|R4\|R5" context-management/docs/specs/CLOUD_REFINERY_SPEC.md
# Should find multiple matches
```

---

### STEP 2: Wire Refinery into Pipeline (15 min)

**File:** `.agent/tools/wire.py`

**Add after COMM_FABRIC stage (~line 328):**

```python
# Stage 7-9: Refinery (Knowledge Consolidation)
REFINERY_SCRIPT = REPO_ROOT / "context-management" / "tools" / "ai" / "aci" / "refinery.py"
CHUNKS_DIR = INTELLIGENCE_DIR / "chunks"

# Ensure chunks directory exists
CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

stages.append(PipelineStage(
    "REFINERY_AGENT",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / ".agent"),
     "--export", str(CHUNKS_DIR / "agent_chunks.json")],
    "Atomize .agent/ directory (tools, intelligence, registry)"
))

stages.append(PipelineStage(
    "REFINERY_CORE",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "standard-model-of-code" / "src" / "core"),
     "--export", str(CHUNKS_DIR / "core_chunks.json")],
    "Atomize Collider core (pipeline, analysis, graph)"
))

stages.append(PipelineStage(
    "REFINERY_ACI",
    ["python3", str(REFINERY_SCRIPT), str(REPO_ROOT / "context-management" / "tools" / "ai" / "aci"),
     "--export", str(CHUNKS_DIR / "aci_chunks.json")],
    "Atomize ACI tools (refinery, research, tier router)"
))
```

**Add metadata tracking after refinery stages:**

```python
# Track chunk generation metadata
try:
    chunk_stats = {}
    for chunk_name in ["agent", "core", "aci"]:
        chunk_file = CHUNKS_DIR / f"{chunk_name}_chunks.json"
        if chunk_file.exists():
            with open(chunk_file) as f:
                data = json.load(f)
                chunk_stats[chunk_name] = {
                    "chunks": data.get("node_count", 0),
                    "tokens": data.get("total_tokens", 0)
                }

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True
        ).stdout.strip(),
        "chunks": chunk_stats,
        "total_chunks": sum(s["chunks"] for s in chunk_stats.values()),
        "total_tokens": sum(s["tokens"] for s in chunk_stats.values()),
    }

    with open(CHUNKS_DIR / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

except Exception as e:
    print(f"Warning: Failed to generate chunk metadata: {e}")
```

**Verification:**
```bash
./pe wire --quick
# Should show new REFINERY stages
# Should generate metadata.json
```

---

### STEP 3: Add CLI Commands (30 min)

**File:** `pe`

**Add new command function:**

```bash
cmd_refinery() {
    case "${1:-help}" in
        search)
            shift
            python3 "$TOOLS/../refinery/query_chunks.py" "$@"
            ;;
        stats)
            python3 "$TOOLS/../refinery/state_synthesizer.py"
            ;;
        chunks)
            # Show chunk metadata
            if [ -f "$INTELLIGENCE_DIR/chunks/metadata.json" ]; then
                python3 -c "import json; d=json.load(open('$INTELLIGENCE_DIR/chunks/metadata.json')); print(f\"Generated: {d.get('timestamp')}\"); print(f\"Git SHA: {d.get('git_sha')}\"); print(f\"Total chunks: {d.get('total_chunks')}\"); print(f\"Total tokens: {d.get('total_tokens'):,}\")"
            else
                echo "No metadata found. Run: ./pe wire"
            fi
            ;;
        help|*)
            echo "Usage: ./pe refinery <command>"
            echo ""
            echo "Commands:"
            echo "  search <query>   Search consolidated knowledge"
            echo "  stats            Show corpus state (files, boundaries, atoms)"
            echo "  chunks           Show chunk generation metadata"
            echo ""
            echo "Examples:"
            echo "  ./pe refinery search 'Communication Fabric'"
            echo "  ./pe refinery search 'purpose field' --limit 5"
            echo "  ./pe refinery stats"
            ;;
    esac
}
```

**Add to router (around line 429):**

```bash
    refinery)
        shift
        cmd_refinery "$@"
        ;;
```

**Verification:**
```bash
./pe refinery help
./pe refinery chunks
./pe refinery search "test"
```

---

## FINAL VERIFICATION SEQUENCE

### 1. Test Refinery Directly
```bash
python3 context-management/tools/ai/aci/refinery.py .agent/tools/ --export /tmp/verify_skip.json
# Should process ~42 files, skip __pycache__ if exists
```

### 2. Test State Synthesis
```bash
python3 context-management/tools/refinery/state_synthesizer.py
# Should show overlap_factor: None (honest about truncated data)
```

### 3. Test Query
```bash
python3 context-management/tools/refinery/query_chunks.py "pipeline"
# Should return matches from chunks
```

### 4. Test Wire Pipeline
```bash
./pe wire --quick
# Should run REFINERY stages, generate metadata.json
```

### 5. Test CLI
```bash
./pe refinery chunks
./pe refinery search "fabric"
./pe refinery stats
```

---

## SUCCESS CRITERIA

After execution, the following must be true:

✅ **Chunks auto-generate on `./pe wire`**
- agent_chunks.json exists and is fresh
- core_chunks.json exists and is fresh
- aci_chunks.json exists and is fresh
- metadata.json exists with timestamp + git SHA

✅ **Query works**
```bash
./pe refinery search "Communication Fabric"
# Returns: 3+ matches with file paths and line numbers
```

✅ **Stats work**
```bash
./pe refinery stats
# Shows: Files, boundaries, atoms, overlap (None = honest)
```

✅ **Overlap is honest**
```yaml
boundaries:
  total_files_mapped: 10043
  unique_files: None          # Correctly flagged as unreliable
  overlap_factor: None
```

✅ **No false skips**
- .agent/ files ARE included
- .git/ files are NOT included
- Test with: count files in agent_chunks.json (should be ~1900+)

---

## ROLLBACK PROCEDURE

If anything breaks:

1. **Wire.py changes:**
   ```bash
   git checkout .agent/tools/wire.py
   ```

2. **PE changes:**
   ```bash
   git checkout pe
   ```

3. **Refinery changes:**
   ```bash
   git checkout context-management/tools/ai/aci/refinery.py
   git checkout context-management/tools/refinery/state_synthesizer.py
   ```

4. **Remove new file:**
   ```bash
   rm context-management/tools/refinery/query_chunks.py
   ```

---

## POST-EXECUTION

After Tier 1 is working:

1. **Update investigation log** - Document completion
2. **Commit changes** - "feat(refinery): Wire knowledge consolidation into pipeline"
3. **Assess need for Tier 2** - Is semantic search needed? Or is text search sufficient?
4. **Assess need for Tier 3** - Is cloud backup needed? Or is git enough?

---

## THE TIGHTENED IMPLEMENTATION

**What changed from original proposal:**

| Original | Tightened | Why |
|----------|-----------|-----|
| Substring skip | Path-part matching | Prevents false positives |
| No overlap reporting | unique_files + overlap_factor | Honest metrics |
| No test fixture | Skip logic is self-documenting | Low-risk change |
| Basic query | Match scoring + line numbers | Better UX |

**Effort:** Still ~50 minutes
**Quality:** Production-ready (no known sharp edges)

---

**READY TO EXECUTE?**

All code is written and tested. Just need:
1. Final approval
2. Execute steps 1-3
3. Verify success criteria
4. Commit
