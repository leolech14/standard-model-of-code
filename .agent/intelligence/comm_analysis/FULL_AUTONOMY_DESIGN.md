# PROJECT_elements - Full Autonomy Design
**Date:** 2026-01-27 05:35
**Vision:** EVERYTHING AUTOMATIC
**Principle:** "We cannot keep processing until data gets broken"

---

## THE VISION WORKFLOW

```
Developer opens Antigravity on PROJECT_*
    ↓
Developer opens terminal
    ↓
Developer opens Claude Code CLI
    ↓
Developer: "Onboard me"
    ↓
Claude reads ALREADY UPDATED, ENRICHED, VALIDATED knowledge
    ↓
Claude: "Here's the current state" (INSTANT - no analysis needed)
    ↓
Work begins from COMPLETE understanding
```

**Key Insight:** Knowledge must be ALWAYS READY, not generated on-demand.

---

## WHAT "EVERYTHING AUTOMATIC" MEANS

### The Contextome Infrastructure Must:

1. **Update automatically** - No manual ./pe wire needed
2. **Enrich automatically** - Meaning extraction happens in background
3. **Validate automatically** - Broken data rejected before written
4. **Structure automatically** - Optimal for LLM consumption
5. **Consolidate automatically** - Single coherent view, not scattered files
6. **Refresh recursively** - New knowledge generates new analysis
7. **Degrade gracefully** - Never break from over-processing

---

## THE RECURSIVE PROCESSING CHALLENGE

**The Problem:**
```
Analyze code → Generate insights → Write docs → Code changed → Re-analyze →
Generate new insights → Update docs → Docs changed → Re-analyze → ...
```

**Without protection:** Infinite loop, data corruption, semantic drift

**With proper configuration:**
```
Change detected → Validate change → Process incrementally → Update only affected →
Validate output → Write atomically → Mark complete → Sleep until next change
```

---

## CORE DESIGN PRINCIPLES

### 1. Idempotent Processing
**Requirement:** Running refinery 10x produces IDENTICAL output

**Implementation:**
- Content-based IDs (SHA256 of source)
- Atomic writes (temp file → rename)
- Schema validation before write
- Timestamp-based freshness checks

### 2. Incremental Updates
**Requirement:** Only re-process what CHANGED

**Implementation:**
- Git SHA tracking (know what code version)
- File hash tracking (know what files changed)
- Delta detection (compare current vs last)
- Selective re-chunking (only changed files)

### 3. Schema Stability
**Requirement:** Data format NEVER breaks consumers

**Implementation:**
- Versioned schemas (chunk_schema_v1.json)
- Backward compatibility (readers handle old formats)
- Migration scripts (v1 → v2)
- Validation gates (reject malformed data)

### 4. Validation Gates
**Requirement:** Broken data NEVER written

**Implementation:**
- Pre-write schema validation
- Sanity checks (chunk count reasonable?)
- Rollback on failure (temp file cleanup)
- Circuit breakers (stop after N failures)

### 5. Resource Bounds
**Requirement:** System never runs out of memory/disk/quota

**Implementation:**
- Max files per refinery run (100 default)
- Token budgets (max 1M tokens per chunk set)
- GCS lifecycle policies (auto-delete old R0 snapshots)
- Rate limit awareness (backoff on 429)

---

## AUTOMATION ARCHITECTURE

### LOCAL LAYER (Mac)

```
File System Monitor (fswatch or LaunchAgent)
    ↓
[DEBOUNCER] - 5min quiet period after last change
    ↓
Incremental Update Pipeline
    ├─ Delta Detector (what changed since last run?)
    ├─ Refinery (re-chunk only changed files)
    ├─ State Synthesizer (merge into live.yaml)
    ├─ Communication Fabric (record new state)
    └─ Metadata Writer (timestamp + SHA)
    ↓
[VALIDATION GATE] - Schema check, sanity check
    ↓
Atomic Write (temp → rename)
    ↓
Ready for Query
```

**Trigger:** File changes (automatic)
**Frequency:** Continuous (with 5min debounce)
**Safety:** Circuit breakers, schema validation

---

### CLOUD LAYER (GCP)

```
Local writes unified_analysis.json
    ↓
[EVENT TRIGGER] - GCS object finalize (Eventarc)
    ↓
Cloud Function: R0→R1 (Indexing)
    ├─ Validate JSON schema
    ├─ Extract to JSONL
    ├─ Build search index
    └─ Write to R1_indexed/
    ↓
[DAILY TRIGGER] - Cloud Scheduler
    ↓
Cloud Function: R1→R2 (Normalization)
    ├─ Deduplicate across snapshots
    ├─ Canonical ID assignment
    ├─ Cross-reference linking
    └─ Write to R2_normalized/
    ↓
[DAILY TRIGGER] - Cloud Scheduler
    ↓
Vertex AI Pipeline: R2→R3→R4→R5
    ├─ R3: Gemini enrichment (relationships, annotations)
    ├─ R4: Pattern detection, anomalies
    ├─ R5: Purpose field computation, predictions
    └─ Write to R3/, R4/, R5/
    ↓
Always-Ready Knowledge Corpus
```

**Trigger:** Automatic (events + schedules)
**Frequency:** Continuous (R0→R1), daily (R1→R5)
**Safety:** Schema validation, quota limits, monitoring

---

## THE SAFETY MECHANISMS

### 1. Delta Detection (Prevent Re-Processing)
```python
def should_process(file_path: str, last_run_sha: str) -> bool:
    """Only process if file changed since last run."""
    current_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()

    # Check cache
    if file_path in chunk_cache:
        cached_hash = chunk_cache[file_path]["hash"]
        if cached_hash == current_hash:
            return False  # Skip - unchanged

    return True  # Process - changed or new
```

### 2. Schema Validation (Prevent Broken Data)
```python
def validate_chunks(chunks: List[RefineryNode]) -> bool:
    """Validate before writing."""
    for chunk in chunks:
        # Required fields
        if not all([chunk.content, chunk.source_file, chunk.chunk_id]):
            return False

        # Reasonable bounds
        if chunk.token_estimate > 100000:  # Sanity check
            return False

        # Relevance in range
        if not (0 <= chunk.relevance_score <= 1.0):
            return False

    return True
```

### 3. Atomic Writes (Prevent Partial Corruption)
```python
def atomic_write(data: dict, path: Path):
    """Write atomically (all-or-nothing)."""
    temp_path = path.with_suffix('.tmp')

    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Validate before committing
        with open(temp_path) as f:
            json.load(f)  # Ensure valid JSON

        # Commit (atomic on POSIX)
        temp_path.rename(path)

    except Exception as e:
        # Cleanup on failure
        if temp_path.exists():
            temp_path.unlink()
        raise
```

### 4. Circuit Breakers (Prevent Cascade Failures)
**Already implemented** in autopilot.py:
- 3 failures → circuit trips
- 5 minute cooldown
- Auto-recovery when cooldown expires

### 5. Resource Limits (Prevent Runaway)
```python
# In refinery.py
max_files: int = 100           # Safety limit per directory
max_tokens: int = 1000000      # Max context per chunk set

# In wire.py
COLLIDER_CACHE_THRESHOLD = 30  # Minutes (skip if cached)
THROTTLE_SECONDS = 60          # Min time between runs
```

---

## FULL AUTONOMY IMPLEMENTATION

### LOCAL AUTOMATION (Mac)

**Goal:** Knowledge always fresh, updated automatically on file changes

**Components:**

#### A. File System Monitor (NEW)
**Create:** `.agent/tools/filesystem_monitor.py`

```python
#!/usr/bin/env python3
"""
Filesystem Monitor - Automatic Knowledge Update
================================================

Watches PROJECT_elements/ for changes.
On sustained activity (5min quiet period):
  1. Run incremental wire pipeline
  2. Update chunks (only changed files)
  3. Record new state
  4. Validate output

Prevents infinite loops with:
  - Debouncing (5min quiet)
  - Ignore self-writes (chunks/, state/)
  - Circuit breakers
  - Resource limits
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SmartHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_change = time.time()
        self.pending = False

    def on_modified(self, event):
        # Ignore our own writes
        if any(p in event.src_path for p in ['chunks/', 'state/', '.git/']):
            return

        self.last_change = time.time()
        self.pending = True

    def check_and_process(self):
        """Process if 5min quiet period elapsed."""
        if not self.pending:
            return

        quiet_time = time.time() - self.last_change
        if quiet_time > 300:  # 5 minutes
            print(f"[Monitor] Quiet for 5min, running incremental update...")
            # Run wire.py --quick (skip Collider, update everything else)
            subprocess.run(["python", "wire.py", "--quick"])
            self.pending = False
```

**LaunchAgent:** `com.elements.filesystem-monitor.plist`
- Runs filesystem_monitor.py on login
- Watches entire PROJECT_elements/
- Triggers incremental updates automatically

**Status:** NEW - needs creation

---

#### B. Wire Pipeline Auto-Mode (ACTIVATE EXISTING)

**Current:** Wire has `--watch` mode but not activated

**Activation Options:**

**Option 1: LaunchAgent**
```xml
<!-- com.elements.wire-watch.plist -->
<plist>
  <dict>
    <key>Label</key>
    <string>com.elements.wire-watch</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/Users/lech/PROJECTS_all/PROJECT_elements/.agent/tools/wire.py</string>
      <string>--watch</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
  </dict>
</plist>
```

**Option 2: Screen/tmux session** (simpler)
```bash
# Start persistent session
screen -dmS wire-watch bash -c 'cd ~/PROJECTS_all/PROJECT_elements && python3 .agent/tools/wire.py --watch'

# Attach to monitor
screen -r wire-watch
```

**Resource Impact:** Collider runs every 5min if code changed (CPU-intensive)

**Better approach:** Hybrid
- Wire --quick runs every 5 min (skips Collider, fast)
- Collider runs only on demand OR when git SHA changes

---

#### C. Incremental Refinery (NEW)

**Problem:** Current refinery re-processes ALL files every run

**Solution:** Delta-aware refinery

```python
def process_file_incremental(self, file_path: str, cache: dict) -> List[RefineryNode]:
    """Only re-chunk if file changed."""

    # Compute file hash
    file_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()

    # Check cache
    cached_entry = cache.get(file_path)
    if cached_entry and cached_entry["hash"] == file_hash:
        # Unchanged - return cached chunks
        return cached_entry["chunks"]

    # Changed or new - process
    chunks = self.process_file(file_path)

    # Update cache
    cache[file_path] = {
        "hash": file_hash,
        "chunks": chunks,
        "processed_at": datetime.now().isoformat()
    }

    return chunks
```

**Benefit:** 100x faster on incremental runs (only processes changed files)

---

### CLOUD AUTOMATION (GCP)

**Goal:** 24/7 background intelligence, zero local resources

**Components:**

#### A. R0 Layer - Automatic Snapshot (EVENT-DRIVEN)

**Trigger:** GCS object finalize event

```
Local: git commit
    ↓
Post-commit: Upload unified_analysis.json to GCS
    ↓
GCS: gs://elements-archive-2026/projectome/R0_raw/YYYY-MM-DD_HHMMSS.json
    ↓
[EVENTARC TRIGGER] - Object finalize
    ↓
Cloud Function: index_snapshot()
    ↓
R1_indexed/ written
```

**Frequency:** Every commit that runs Collider
**Latency:** <1 minute (event-driven)

---

#### B. R1→R2 - Daily Normalization (SCHEDULED)

**Trigger:** Cloud Scheduler (daily at 02:00 UTC)

```
Cloud Scheduler fires
    ↓
Cloud Function: normalize_corpus()
    ├─ Read all R1 snapshots
    ├─ Deduplicate by content hash
    ├─ Assign canonical IDs
    ├─ Link cross-references
    └─ Write R2_normalized/canonical.json
```

**Frequency:** Daily
**Duration:** ~5-10 minutes

---

#### C. R2→R5 - Weekly Enrichment (SCHEDULED)

**Trigger:** Cloud Scheduler (Sunday 03:00 UTC)

```
Cloud Scheduler fires
    ↓
Vertex AI Pipeline: enrich_and_distill()
    ├─ R3: Gemini annotations (relationships, context)
    ├─ R4: Pattern detection, summaries
    ├─ R5: Purpose field computation, predictions
    └─ Write R3/, R4/, R5/
```

**Frequency:** Weekly
**Duration:** ~30-60 minutes

---

## SAFETY MECHANISMS (Prevent Data Degradation)

### 1. Versioned Schemas
```
chunks/
├── agent_chunks_v1.json  ← Old format (keep)
├── agent_chunks_v2.json  ← New format (readers handle both)
└── schema_version.txt    ← "2"
```

### 2. Validation Gates
```python
def write_chunks(chunks: List, output_path: Path):
    """Write with validation."""

    # Pre-write validation
    if not validate_schema(chunks):
        raise ValueError("Schema validation failed")

    if not validate_sanity(chunks):
        raise ValueError("Sanity check failed")

    # Atomic write
    atomic_write(chunks, output_path)

    # Post-write verification
    verify_readable(output_path)
```

### 3. Staleness Detection
```python
def is_stale(metadata: dict) -> bool:
    """Check if knowledge is stale."""
    last_update = datetime.fromisoformat(metadata["timestamp"])
    age_hours = (datetime.now() - last_update).total_seconds() / 3600

    # Stale if >1 hour old AND git SHA changed
    current_sha = get_git_sha()
    if age_hours > 1 and current_sha != metadata["git_sha"]:
        return True

    return False
```

### 4. Incremental Limits
```python
MAX_FILES_PER_RUN = 100       # Don't process entire repo at once
MAX_TOKENS_PER_CHUNK = 10000  # Prevent mega-chunks
MAX_PROCESSING_TIME = 300     # 5 minutes max
```

### 5. Circuit Breakers (ALREADY IMPLEMENTED)
From autopilot.py:
- 3 failures → circuit opens
- 5 minute cooldown
- Auto-recovery

---

## THE COMPLETE AUTOMATION STACK

### Level 0: File Changes (Continuous)
```
Files change
    ↓
[DEBOUNCER] - 5min quiet period
    ↓
filesystem_monitor.py triggers
    ↓
Incremental wire --quick
```

### Level 1: Git Commits (Per-Commit)
```
git commit
    ↓
post-commit hook
    ↓
autopilot.py
    ├─ Trigger Engine
    ├─ Enrichment (if stale)
    └─ Comm Fabric
```

### Level 2: Scheduled Updates (Periodic)
```
[CRON/LaunchAgent]
    ├─ Every 1h: Full wire --quick (fast update)
    ├─ Every 6h: Full wire (with Collider)
    └─ Daily: State synthesis + cleanup
```

### Level 3: Cloud Processing (24/7)
```
[GCP Cloud Schedulers]
    ├─ Every commit: R0 upload (event-driven)
    ├─ Daily 02:00: R1→R2 normalization
    └─ Weekly Sunday: R2→R5 enrichment
```

### Level 4: On-Demand Gates (Instant)
```
Claude: "What changed this week?"
    ↓
Gates API: DIGEST query
    ↓
Returns from R4_distilled/ (pre-computed)
    ↓
Response in <200ms
```

---

## WHAT NEEDS TO BE BUILT

### Immediate (Local Autonomy)

| Component | Status | Effort | Impact |
|-----------|--------|--------|--------|
| **Incremental refinery** | NEW | 2h | 100x faster updates |
| **Validation gates** | NEW | 1h | Prevent data corruption |
| **Filesystem monitor** | NEW | 2h | Automatic on file change |
| **Wire scheduler** | ACTIVATE | 30min | Continuous updates |
| **Delta detector** | EXISTS | Test | Only process changes |

**Total: 5.5 hours to local full autonomy**

---

### Cloud Autonomy (24/7 Intelligence)

| Component | Status | Effort | Impact |
|-----------|--------|--------|--------|
| **Fix socratic-audit-job** | BROKEN | 1h | Stop quota waste |
| **R0 uploader** | NEW | 1h | Start accumulating history |
| **R0→R1 Cloud Function** | NEW | 3h | Indexed search |
| **R1→R2 Cloud Function** | NEW | 3h | Normalized corpus |
| **R2→R5 Vertex Pipeline** | NEW | 8h | Full enrichment |
| **Gates API** | NEW | 6h | Instant queries |

**Total: 22 hours to cloud full autonomy**

---

## CONFIGURATION FILES NEEDED

### 1. Filesystem Monitor Config
```yaml
# .agent/config/monitor.yaml
watch:
  directories:
    - .agent/
    - context-management/
    - standard-model-of-code/src/

  ignore:
    - .git/
    - chunks/
    - state/
    - __pycache__/
    - *.pyc

  debounce:
    quiet_period_seconds: 300  # 5 minutes
    max_wait_seconds: 1800     # 30 minutes max

  action:
    command: "python .agent/tools/wire.py --quick --incremental"
    timeout_seconds: 300
    circuit_breaker:
      max_failures: 3
      cooldown_seconds: 900  # 15 minutes
```

### 2. Refinery Cache Schema
```yaml
# .agent/intelligence/chunks/cache.yaml
version: 1
last_full_process: "2026-01-27T05:00:00"
git_sha: "abc123..."

files:
  "path/to/file.py":
    hash: "sha256:..."
    chunk_count: 15
    last_processed: "2026-01-27T05:00:00"
    chunks_written: true
```

### 3. Processing Limits
```yaml
# .agent/config/refinery_limits.yaml
processing:
  max_files_per_run: 100
  max_tokens_per_chunk: 10000
  max_processing_time_seconds: 300

incremental:
  enabled: true
  cache_path: ".agent/intelligence/chunks/cache.yaml"
  force_full_every_n_runs: 10  # Full reprocess every 10 runs

validation:
  schema_version: 2
  required_fields: [content, source_file, chunk_id, chunk_type]
  max_relevance: 1.0
  min_relevance: 0.0
```

---

## THE ONBOARDING EXPERIENCE

### Current (Manual)
```
User: "Onboard me"
Claude: "Let me analyze the codebase..."
[2-5 minutes of analysis]
Claude: "Here's what I found..."
```

**Problem:** Every onboarding re-analyzes from scratch.

---

### With Full Autonomy
```
User: "Onboard me"
Claude: [Reads from always-fresh consolidated knowledge]
Claude: "PROJECT_elements (last updated 3 minutes ago, git SHA abc123)

        Quick Stats:
        - 2,899 files, 1.6M lines
        - 2,654 knowledge chunks
        - 38 boundaries, 295 atoms
        - Health: BRONZE tier, STABLE margin +0.70
        - Recent: 14 files changed in last commit

        Top 3 areas:
        1. Collider (analysis engine) - 598 chunks
        2. Agent tools (orchestration) - 1,948 chunks
        3. ACI (AI context) - 108 chunks

        Communication state:
        - F (latency): 9.81h
        - MI (alignment): 0.73
        - System is STABLE

        What would you like to work on?"
```

**Duration:** <1 second (reads pre-computed state)
**Freshness:** Always current (updates automatically)

---

## RECURSIVE KNOWLEDGE GENERATION

**The Vision:**
```
Code → Analysis → Insights → Documentation → Code Changes → Re-Analysis → New Insights → ...
```

**How to make it safe:**

1. **Detect Recursion Depth**
```python
def check_recursion(metadata: dict) -> bool:
    """Prevent infinite analysis loops."""
    depth = metadata.get("analysis_depth", 0)

    if depth > 5:  # Max 5 levels of re-analysis
        logger.warning("Max recursion depth reached, skipping")
        return False

    return True
```

2. **Semantic Convergence Check**
```python
def has_converged(current_state: dict, previous_state: dict) -> bool:
    """Check if knowledge has stabilized."""

    # Compare chunk counts
    if abs(current_state["chunks"] - previous_state["chunks"]) < 10:
        # Compare content hashes
        if current_state["hash"] == previous_state["hash"]:
            return True  # Converged - stop processing

    return False
```

3. **Freshness Window**
```python
def should_reprocess(file_path: str, min_age_minutes: int = 60) -> bool:
    """Don't re-process too frequently."""

    last_processed = get_last_processed_time(file_path)
    age_minutes = (datetime.now() - last_processed).total_seconds() / 60

    return age_minutes >= min_age_minutes
```

---

## IMPLEMENTATION PRIORITY

### Phase 1: Local Full Autonomy (6 hours)
1. ✅ Tighten refinery skip logic (DONE)
2. ✅ Add overlap metrics (DONE)
3. ⬜ Implement incremental processing (2h)
4. ⬜ Add validation gates (1h)
5. ⬜ Create filesystem monitor (2h)
6. ⬜ Activate wire scheduler (30min)
7. ⬜ Test end-to-end (30min)

**Result:** Knowledge always fresh, updates automatically

---

### Phase 2: Cloud Autonomy (22 hours)
1. ⬜ Fix socratic-audit-job (1h)
2. ⬜ Deploy R0 uploader (1h)
3. ⬜ Deploy R0→R1 function (3h)
4. ⬜ Deploy R1→R2 function (3h)
5. ⬜ Deploy R2→R5 pipeline (8h)
6. ⬜ Deploy Gates API (6h)

**Result:** 24/7 cloud intelligence, instant queries

---

## THE ANSWER

**How automatic COULD it be?**

### With 6 hours work (Local):
- **95% automatic** - Everything updates on file changes
- Onboarding: instant (reads pre-computed state)
- Zero manual steps for daily work

### With 28 hours work (Local + Cloud):
- **99% automatic** - Cloud handles heavy processing
- Local just syncs and queries
- Mac can be off, intelligence continues

### Configuration Complexity:
- **Simple:** Just activate what exists (wire --watch) - 30 min, 70% automatic
- **Moderate:** Add incremental processing + monitoring - 6h, 95% automatic
- **Complete:** Full cloud deployment - 28h, 99% automatic

---

**WHICH LEVEL OF AUTONOMY DO YOU WANT?**

1. **Quick win** (30 min) - Activate wire --watch in screen session
2. **Local autonomy** (6h) - Filesystem monitor + incremental refinery
3. **Full autonomy** (28h) - Cloud Refinery R0-R5 + Gates API

All three prevent data degradation via validation gates + circuit breakers + incremental processing.
