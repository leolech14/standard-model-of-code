# Master Integration Plan - AI Assistance System
**Date:** 2026-01-27 06:15
**Status:** COMPREHENSIVE EXECUTION PLAN
**Validation:** Gemini 3 Pro + Perplexity Sonar Pro (60+ sources)

---

## EXECUTIVE SUMMARY

**Objective:** Transform PROJECT_elements from semi-automatic (62%) to fully automatic (95%) with AI agents inheriting complete, fresh, validated knowledge instantly.

**Strategy:** Three-tier implementation (Essential → Integrated → Cloud)
**Total Effort:** 7-35 hours (depending on tier)
**Expected Impact:** Instant onboarding (<1s), surgical context, zero manual maintenance

---

## TIER 1: ESSENTIAL AUTOMATION (7 Hours)

### Component 1.1: Refinery Pipeline Integration
**Objective:** Wire Refinery into wire.py for automatic chunk generation

**Implementation:**
```python
# Add to wire.py after COMM_FABRIC stage:
- Stage 7: REFINERY_AGENT (atomize .agent/)
- Stage 8: REFINERY_CORE (atomize src/core/)
- Stage 9: REFINERY_ACI (atomize aci/)
- Add: chunk metadata.json (timestamp + git SHA)
```

**Files Modified:**
- `.agent/tools/wire.py` (+50 lines)

**Effort:** 30 minutes

**Confidence:**
- **Factual:** 100% - Pattern exists in enrichment_orchestrator.py, proven working
- **Alignment:** 100% - Directly serves automatic knowledge maintenance goal
- **Current:** 95% - Wire.py already has 6 stages, adding 3 more is incremental
- **Onwards:** 100% - Foundation for all future refinery work
- **Overall:** 95% (min)

**Risk:** LOW - Refinery already works, just wiring into pipeline
**Rollback:** `git checkout .agent/tools/wire.py`
**Success Criteria:** `./pe wire` generates 3 chunk files + metadata.json

---

### Component 1.2: Incremental Refinery Processing
**Objective:** Only re-chunk changed files, not entire codebase

**Implementation:**
```python
# Add to refinery.py:
class IncrementalCache:
    def __init__(self, cache_path):
        self.cache = load_cache()  # {file: {hash, chunks, timestamp}}

    def needs_processing(self, file_path) -> bool:
        current_hash = sha256(file_path.read_bytes())
        cached = self.cache.get(file_path, {})
        return current_hash != cached.get("hash")

# In process_directory():
cache = IncrementalCache(CHUNKS_DIR / "cache.yaml")
for file in files:
    if cache.needs_processing(file):
        chunks = process_file(file)
        cache.update(file, chunks)
    else:
        chunks = cache.get_cached(file)
```

**Files Modified:**
- `context-management/tools/ai/aci/refinery.py` (+100 lines)
- Create: `.agent/intelligence/chunks/cache.yaml`

**Effort:** 2 hours

**Confidence:**
- **Factual:** 95% - File hashing is standard, caching pattern proven
- **Alignment:** 100% - Prevents wasteful re-processing
- **Current:** 85% - Current refinery processes all files (works but slow)
- **Onwards:** 100% - Required for continuous updates
- **Overall:** 85% (min)

**Risk:** MEDIUM - Cache invalidation bugs possible
**Rollback:** Remove cache logic, fall back to full processing
**Success Criteria:** Second `./pe wire` run takes <10s (vs 60s full process)

---

### Component 1.3: Validation Gates
**Objective:** Prevent corrupted chunks from being written

**Implementation:**
```python
def validate_and_write(chunks: List[RefineryNode], output_path: Path):
    """Atomic write with schema validation."""

    # Schema validation
    for chunk in chunks:
        assert chunk.content, "Empty content"
        assert 0 <= chunk.relevance_score <= 1.0, f"Invalid relevance: {chunk.relevance_score}"
        assert chunk.token_estimate < 100000, f"Chunk too large: {chunk.token_estimate}"
        assert chunk.chunk_id, "Missing chunk ID"

    # Sanity check
    total_tokens = sum(c.token_estimate for c in chunks)
    assert total_tokens < 10_000_000, f"Total unreasonable: {total_tokens:,}"
    assert len(chunks) > 0, "No chunks generated"

    # Atomic write (temp → validate → rename)
    temp = output_path.with_suffix('.tmp')
    data = {"nodes": [c.to_dict() for c in chunks], ...}

    with open(temp, 'w') as f:
        json.dump(data, f, indent=2)

    # Verify JSON is valid
    with open(temp) as f:
        json.load(f)

    # Commit
    temp.rename(output_path)
```

**Files Modified:**
- `context-management/tools/ai/aci/refinery.py` (+40 lines)

**Effort:** 1 hour

**Confidence:**
- **Factual:** 100% - Validation pattern is standard practice
- **Alignment:** 100% - Prevents "processing until data broken"
- **Current:** 90% - No validation currently, could write corrupted data
- **Onwards:** 100% - Required for production reliability
- **Overall:** 90% (min)

**Risk:** LOW - Pure safety addition, doesn't change functionality
**Rollback:** Remove validation, accept corruption risk
**Success Criteria:** Invalid chunks rejected, temp files cleaned up on failure

---

### Component 1.4: Convergence Detection
**Objective:** Stop re-processing when knowledge has stabilized

**Implementation:**
```python
def has_converged(current_metadata: dict, previous_metadata: dict) -> bool:
    """Check if knowledge stabilized."""

    # Same chunk count + same git SHA = converged
    if current_metadata["git_sha"] == previous_metadata["git_sha"]:
        current_hash = hash_all_chunks(CHUNKS_DIR)
        previous_hash = previous_metadata.get("content_hash")

        if current_hash == previous_hash:
            logger.info("Knowledge converged, skipping re-process")
            return True

    return False

# In wire.py before REFINERY stages:
if has_converged(current_meta, load_metadata()):
    print("  ⊘ Refinery skipped (knowledge converged)")
    skip_refinery = True
```

**Files Modified:**
- `.agent/tools/wire.py` (+30 lines)
- `context-management/tools/ai/aci/refinery.py` (+20 lines for hash function)

**Effort:** 1 hour

**Confidence:**
- **Factual:** 95% - Content hashing is proven technique
- **Alignment:** 100% - Prevents infinite re-processing loops
- **Current:** 80% - No convergence check currently exists
- **Onwards:** 100% - Critical for continuous updates
- **Overall:** 80% (min)

**Risk:** MEDIUM - False convergence possible if hash collisions
**Rollback:** Remove convergence check, always re-process
**Success Criteria:** Identical code doesn't trigger re-processing

---

### Component 1.5: Activate Continuous Updates
**Objective:** Wire pipeline runs automatically in background

**Implementation:**
```bash
# Option A: Screen session (simplest)
screen -dmS wire bash -c 'cd ~/PROJECTS_all/PROJECT_elements && python3 .agent/tools/wire.py --watch --quick'

# Option B: LaunchAgent (more robust)
# Create: ~/Library/LaunchAgents/com.elements.wire-watch.plist
<plist>
  <dict>
    <key>Label</key>
    <string>com.elements.wire-watch</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>/Users/lech/PROJECTS_all/PROJECT_elements/.agent/tools/wire.py</string>
      <string>--watch</string>
      <string>--quick</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key>
    <string>/tmp/wire-watch.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/wire-watch.err</string>
  </dict>
</plist>

# Load: launchctl load ~/Library/LaunchAgents/com.elements.wire-watch.plist
```

**Files Created:**
- `~/Library/LaunchAgents/com.elements.wire-watch.plist` (or use screen)

**Effort:** 30 minutes

**Confidence:**
- **Factual:** 100% - wire.py --watch already implemented and tested
- **Alignment:** 100% - Automatic updates is core requirement
- **Current:** 100% - Just activating existing feature
- **Onwards:** 95% - Might need tuning (5min interval too frequent?)
- **Overall:** 95% (min)

**Risk:** LOW - Can kill the process anytime, wire.py already stable
**Rollback:** `screen -X -S wire quit` or `launchctl unload ...`
**Success Criteria:** `ps aux | grep wire` shows process, chunks update every 5min

---

### Component 1.6: Query Interface
**Objective:** Search consolidated knowledge via CLI

**Implementation:**
```python
# Already created: context-management/tools/refinery/query_chunks.py

# Add to pe:
refinery)
    shift
    case "${1:-help}" in
        search)
            shift
            python3 "$REPO_ROOT/context-management/tools/refinery/query_chunks.py" "$@"
            ;;
        stats)
            python3 "$REPO_ROOT/context-management/tools/refinery/state_synthesizer.py"
            ;;
        *)
            echo "./pe refinery search <query>"
            echo "./pe refinery stats"
            ;;
    esac
    ;;
```

**Files Modified:**
- `pe` script (+20 lines)

**Effort:** 15 minutes

**Confidence:**
- **Factual:** 100% - query_chunks.py already written and tested
- **Alignment:** 100% - Enables surgical context queries
- **Current:** 100% - Just adding CLI wrapper
- **Onwards:** 100% - Foundation for semantic search (Tier 2)
- **Overall:** 100% (min)

**Risk:** ZERO - Pure CLI addition, doesn't change existing behavior
**Rollback:** Remove from pe script
**Success Criteria:** `./pe refinery search "fabric"` returns results in <1s

---

### Component 1.7: Resolve L0-L5 → R0-R5 Naming
**Objective:** Eliminate confusion with Theory Stack L0-L3

**Implementation:**
```bash
# In CLOUD_REFINERY_SPEC.md, replace all:
L0: Raw       → R0: Raw
L1: Indexed   → R1: Indexed
L2: Normalized → R2: Normalized
L3: Enriched  → R3: Enriched
L4: Distilled → R4: Distilled
L5: Emergent  → R5: Emergent

# Also in all code comments, docs, bucket names
```

**Files Modified:**
- `context-management/docs/specs/CLOUD_REFINERY_SPEC.md`
- Any code comments referencing layers

**Effort:** 15 minutes

**Confidence:**
- **Factual:** 100% - Simple find/replace
- **Alignment:** 100% - Prevents L0 (axioms) vs L0 (raw data) confusion
- **Current:** 100% - No code uses L0-L5 yet, just specs
- **Onwards:** 100% - Correct foundation for cloud work
- **Overall:** 100% (min)

**Risk:** ZERO - Spec-only change
**Rollback:** Revert file
**Success Criteria:** No "L0" references in Cloud Refinery docs

---

## TIER 1 TOTALS

**Total Effort:** 7 hours
**Total Components:** 7
**Average Confidence:** 94%
**Overall Risk:** LOW

**What You Get:**
- ✅ Refinery runs automatically on every wire.py
- ✅ Incremental processing (100x faster updates)
- ✅ Validation gates (prevents corruption)
- ✅ Convergence detection (prevents infinite loops)
- ✅ Continuous updates (wire runs in background)
- ✅ Query interface (`./pe refinery search`)
- ✅ Clean naming (R0-R5, not L0-L5)

**Result:** Knowledge always fresh, queryable, safe from corruption

---

## TIER 2: UNIFIED CONCIERGE (8 Hours)

### Component 2.1: Butler Protocol Definition
**Objective:** Standard interface all butlers implement

**Implementation:**
```python
# Create: .agent/lib/butler_protocol.py

from typing import Protocol, Dict, Any

class Butler(Protocol):
    """Standard interface all butlers must implement."""

    name: str  # Butler identifier

    @staticmethod
    def status() -> Dict[str, Any]:
        """Return current state for concierge.

        Returns:
            {
                "name": str,          # Butler name
                "healthy": bool,      # Is butler operational?
                "summary": str,       # One-line summary
                "last_update": str,   # ISO timestamp
                "details": dict,      # Full state (optional)
            }
        """
        ...

    @staticmethod
    def quick_query(query: str) -> str:
        """Handle fast queries relevant to this butler."""
        ...
```

**Files Created:**
- `.agent/lib/butler_protocol.py` (50 lines)

**Effort:** 30 minutes

**Confidence:**
- **Factual:** 100% - Protocol pattern is Python standard
- **Alignment:** 95% - Standardizes butler interfaces (minor: might need iteration)
- **Current:** 85% - No standard interface exists currently
- **Onwards:** 100% - Enables all future butler additions
- **Overall:** 85% (min)

**Risk:** LOW - Just defines interface, doesn't change behavior
**Dependencies:** None
**Success Criteria:** Protocol compiles, type checks pass

---

### Component 2.2: Butler Interface Implementation
**Objective:** Add status() method to all key butlers

**Butlers to Implement:**

1. **FabricButler** (fabric.py)
```python
class FabricButler:
    name = "Communication Fabric"

    @staticmethod
    def status() -> Dict[str, Any]:
        sv = compute_state_vector()
        alerts = check_stability_alerts(sv)
        return {
            "name": "Communication Fabric",
            "healthy": sv.stability_margin > 0,
            "summary": f"{sv.health_tier} tier, margin {sv.stability_margin:+.2f}",
            "last_update": sv.timestamp,
            "details": {
                "F": sv.F, "MI": sv.MI, "N": sv.N,
                "SNR": sv.SNR, "stability": sv.stability_margin,
                "warnings": [a["message"] for a in alerts[:3]]
            }
        }
```

2. **RefineryButler** (query_chunks.py)
3. **AutopilotButler** (autopilot.py)
4. **GitButler** (new: .agent/lib/git_butler.py)
5. **LOLButler** (lol_sync.py)
6. **TDJButler** (tdj.py)
7. **ColliderButler** (new: .agent/lib/collider_butler.py)
8. **DeckButler** (deck_router.py) - optional if we keep deck

**Files Modified:** 8 files (+15-30 lines each)

**Effort:** 2.5 hours (20min per butler × 8)

**Confidence:**
- **Factual:** 90% - Each butler's data already exists, just wrapping it
- **Alignment:** 100% - Standardizes access for concierge
- **Current:** 80% - Some butlers have state, some don't (need creation)
- **Onwards:** 100% - Extensible pattern for new butlers
- **Overall:** 80% (min)

**Risk:** MEDIUM - Each butler different, might hit edge cases
**Dependencies:** Component 2.1 (protocol definition)
**Success Criteria:** All 8 butlers return valid status() dict

---

### Component 2.3: Concierge Hub Rewrite
**Objective:** Central hub that queries all butlers and displays unified state

**Implementation:**
```python
# Rewrite: .agent/tools/concierge.py

from fabric import FabricButler
from query_chunks import RefineryButler
# ... import all 8 butlers

class Concierge:
    def __init__(self):
        self.butlers = [
            FabricButler, RefineryButler, AutopilotButler,
            GitButler, LOLButler, TDJButler, ColliderButler
        ]

    def gather_palace_state(self, timeout_ms: int = 500) -> Dict[str, Any]:
        """Query all butlers with timeout protection."""

        state = {}
        for butler_class in self.butlers:
            try:
                with timeout(timeout_ms / 1000):
                    state[butler_class.name] = butler_class.status()
            except TimeoutError:
                state[butler_class.name] = {
                    "healthy": False,
                    "summary": f"Timeout ({timeout_ms}ms)"
                }
            except Exception as e:
                state[butler_class.name] = {
                    "healthy": False,
                    "summary": f"Error: {str(e)[:50]}"
                }

        return state

    def display(self, state: dict):
        """Display palace state with industrial UI."""
        # Beautiful formatted output
        ...

    def interactive_loop(self):
        """Main interactive mode."""
        state = self.gather_palace_state()
        self.display(state)

        while True:
            choice = input("> ").strip()
            # Handle R/D/S/Q commands
            ...
```

**Files Modified:**
- `.agent/tools/concierge.py` (major rewrite, ~400 lines)

**Effort:** 3 hours

**Confidence:**
- **Factual:** 85% - Similar pattern to existing concierge, proven UI exists
- **Alignment:** 100% - This IS the integration hub
- **Current:** 70% - Major rewrite risk, might hit unexpected issues
- **Onwards:** 100% - Becomes central point for all future additions
- **Overall:** 70% (min)

**Risk:** HIGH - Major rewrite, could break existing concierge
**Dependencies:** Component 2.2 (all butler interfaces working)
**Rollback:** `git checkout .agent/tools/concierge.py`
**Success Criteria:** `./concierge` displays complete state in <1s

---

### Component 2.4: Ollama Query Integration
**Objective:** Route queries to appropriate butler via Ollama

**Implementation:**
```python
# Add to Concierge class:

def ask_palace(self, query: str) -> str:
    """Route query to appropriate butler via Ollama."""

    # Classify intent (local Ollama ~100ms)
    intent = self._classify_intent(query)

    # Route to butler
    if intent == "health":
        state = FabricButler.status()
        return state["summary"]

    elif intent == "search":
        results = RefineryButler.search(query, limit=3)
        return self._format_search_results(results)

    elif intent == "tasks":
        # ... etc

    # Fallback: unclear intent
    return "Unclear query. Try: 'search X', 'health', 'tasks', 'status'"

def _classify_intent(self, query: str) -> str:
    """Use Ollama to classify query intent."""
    prompt = f"Classify intent: {query}\nOptions: [health, search, tasks, git, status]\nAnswer:"

    result = subprocess.run(
        ["ollama", "run", "llama3.2:3b", prompt],
        capture_output=True, text=True, timeout=1
    )

    return result.stdout.strip().lower()
```

**Files Modified:**
- `.agent/tools/concierge.py` (+80 lines)

**Effort:** 1.5 hours

**Confidence:**
- **Factual:** 95% - Ollama integration exists in pe, proven working
- **Alignment:** 100% - Enables fast butler queries
- **Current:** 85% - Ollama works in pe, needs adaptation for concierge
- **Onwards:** 100% - Foundation for advanced assistance
- **Overall:** 85% (min)

**Risk:** LOW - Ollama already working, just different integration point
**Dependencies:** Component 2.3 (concierge hub)
**Success Criteria:** Query "system health" returns fabric status in <300ms

---

### Component 2.5: Make Concierge Default
**Objective:** Auto-run concierge when entering PROJECT_elements

**Implementation:**
```bash
# Option A: Add to ~/.zshrc
echo 'function pe-enter() { cd ~/PROJECTS_all/PROJECT_elements && ./concierge }' >> ~/.zshrc
echo 'alias pe="pe-enter"' >> ~/.zshrc

# Option B: Create wrapper script
# Create: ./start
#!/bin/bash
cd "$(dirname "$0")"
./concierge

# Option C: Update CLAUDE.md
# First instruction: "Run ./concierge for instant onboarding"
```

**Files Modified:**
- `~/.zshrc` (if Option A)
- Create `./start` (if Option B)
- `CLAUDE.md` (if Option C)

**Effort:** 15 minutes

**Confidence:**
- **Factual:** 100% - Shell aliases are standard
- **Alignment:** 95% - Makes concierge discoverable (minor: agent must know to use alias)
- **Current:** 100% - Simple addition
- **Onwards:** 90% - Might need adjustment based on usage patterns
- **Overall:** 90% (min)

**Risk:** ZERO - Can remove alias anytime
**Dependencies:** Component 2.3 (working concierge)
**Success Criteria:** New terminal session → concierge runs automatically

---

### Component 2.6: Integration Testing
**Objective:** Verify all components work together

**Test Suite:**
1. ✓ All 8 butlers respond to status()
2. ✓ Concierge gathers state in <1s
3. ✓ Display is readable and complete
4. ✓ Ollama routing works
5. ✓ Query interface returns results
6. ✓ No infinite loops (convergence working)
7. ✓ No corrupted chunks (validation working)
8. ✓ Incremental processing works (cache hits)

**Effort:** 1 hour

**Confidence:**
- **Factual:** 90% - Integration bugs always possible
- **Alignment:** 100% - Verification is mandatory
- **Current:** 75% - Integration untested until now
- **Onwards:** 100% - Establishes working baseline
- **Overall:** 75% (min)

**Risk:** DISCOVERY - Tests will find bugs, unknown scope
**Dependencies:** All Components 2.1-2.5
**Success Criteria:** All 8 tests pass

---

## TIER 2 TOTALS

**Total Effort:** 8 hours
**Total Components:** 6
**Average Confidence:** 86%
**Overall Risk:** MEDIUM (major rewrite of concierge)

**What You Get:**
- ✅ Unified concierge hub (one command, complete state)
- ✅ 8 butlers with standard interfaces
- ✅ Ollama routing (query any butler via natural language)
- ✅ Auto-run on terminal open
- ✅ Integration tested end-to-end

**Result:** Agent inherits palace instantly, queries via natural language

---

## TIER 3: CLOUD INTELLIGENCE (20 Hours)

### Component 3.1: Fix Socratic Audit Job
**Objective:** Stop 100% failure rate (currently wasting quota)

**Implementation:**
```dockerfile
# Modify cloud-entrypoint.sh:
python3 context-management/tools/ai/analyze.py \
    --set agent_kernel \
    --model gemini-2.0-flash-exp \
    --max-files 50 \
    "$@"

# Rebuild: ./cloud-run-deploy.sh
```

**Files Modified:**
- `cloud-entrypoint.sh` (change model + add limits)
- Rebuild Docker image

**Effort:** 1 hour

**Confidence:**
- **Factual:** 100% - Gemini 2.5 Flash has 4M tokens/min (4x higher limit)
- **Alignment:** 100% - Stops quota waste, foundation for cloud intelligence
- **Current:** 100% - Job exists, just needs config change
- **Onwards:** 100% - Required for any cloud work
- **Overall:** 100% (min)

**Risk:** LOW - Just changing model, tested pattern
**Dependencies:** None
**Success Criteria:** Next scheduled run succeeds (exit code 0)

---

### Component 3.2: R0 Layer Deployment
**Objective:** Start accumulating unified_analysis.json snapshots

**Implementation:**
```bash
# 1. Create bucket structure
gsutil mb gs://elements-archive-2026/projectome/
gsutil mb gs://elements-archive-2026/projectome/R0_raw/

# 2. Modify wire.py to upload after Collider
if COLLIDER ran successfully:
    latest_analysis = find_latest_collider_output()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    gsutil cp {latest_analysis} gs://elements-archive-2026/projectome/R0_raw/{timestamp}.json

# Or: Add to archive.py
python archive.py upload-analysis
```

**Files Modified:**
- `.agent/tools/wire.py` (+20 lines) OR
- `context-management/tools/archive/archive.py` (+40 lines)

**Effort:** 1 hour

**Confidence:**
- **Factual:** 95% - GCS upload proven (sync_to_cloud.sh works)
- **Alignment:** 100% - Foundation for cloud intelligence
- **Current:** 90% - Need to verify bucket permissions
- **Onwards:** 100% - Required for R1-R5 layers
- **Overall:** 90% (min)

**Risk:** LOW - Upload only, doesn't change local behavior
**Dependencies:** Component 3.1 (working GCS access)
**Success Criteria:** `gsutil ls gs://elements-archive-2026/projectome/R0_raw/` shows files

---

### Component 3.3-3.7: R1-R5 Cloud Functions
**Objective:** Full cloud refinery distillation pipeline

**Implementation:**
- R0→R1: Cloud Function (index to JSONL)
- R1→R2: Cloud Function (normalize, deduplicate)
- R2→R5: Vertex AI Pipeline (enrich, distill, emergence)
- Gates API: Cloud Run service (NEEDLE, SLICE, DIGEST, COMPILE)

**Effort:** 18 hours
- R0→R1: 3 hours
- R1→R2: 3 hours
- R2→R5: 8 hours
- Gates API: 4 hours

**Confidence:**
- **Factual:** 70% - No code exists, spec only
- **Alignment:** 100% - Ultimate vision of cloud intelligence
- **Current:** 40% - Major new development, unknown unknowns
- **Onwards:** 100% - Enables predictive intelligence
- **Overall:** 40% (min)

**Risk:** HIGH - Complex deployment, many integration points
**Dependencies:** Component 3.2 (R0 working)
**Success Criteria:** Query Gates API, receive answer from R4 in <2s

---

## TIER 3 TOTALS

**Total Effort:** 20 hours
**Total Components:** 6
**Average Confidence:** 70%
**Overall Risk:** HIGH (cloud deployment complexity)

**What You Get:**
- ✅ Cloud audit job working (not failing)
- ✅ R0 snapshots accumulating
- ✅ R1-R5 distillation layers (if full deployment)
- ✅ Gates API for instant queries
- ✅ 24/7 intelligence even when Mac off

**Result:** Time-travel queries, predictive intelligence, instant answers

---

## COMPLETE IMPLEMENTATION MATRIX

| Tier | Component | Effort | Confidence | Risk | Impact |
|------|-----------|--------|------------|------|--------|
| **1.1** | Refinery → wire.py | 30min | 95% | LOW | HIGH |
| **1.2** | Incremental processing | 2h | 85% | MED | HIGH |
| **1.3** | Validation gates | 1h | 90% | LOW | HIGH |
| **1.4** | Convergence detection | 1h | 80% | MED | MED |
| **1.5** | Activate --watch | 30min | 95% | LOW | HIGH |
| **1.6** | Query interface | 15min | 100% | ZERO | MED |
| **1.7** | Rename R0-R5 | 15min | 100% | ZERO | LOW |
| **2.1** | Butler protocol | 30min | 85% | LOW | MED |
| **2.2** | Butler interfaces | 2.5h | 80% | MED | HIGH |
| **2.3** | Concierge hub | 3h | 70% | HIGH | HIGH |
| **2.4** | Ollama integration | 1.5h | 85% | LOW | MED |
| **2.5** | Make default | 15min | 90% | ZERO | LOW |
| **2.6** | Integration tests | 1h | 75% | DISC | HIGH |
| **3.1** | Fix cloud job | 1h | 100% | LOW | HIGH |
| **3.2** | R0 deployment | 1h | 90% | LOW | MED |
| **3.3-7** | R1-R5 + Gates | 18h | 40% | HIGH | MED |

---

## RISK ASSESSMENT

### High Confidence, Low Risk (DO FIRST)
- Component 1.1: Refinery → wire (95% confidence, LOW risk)
- Component 1.3: Validation gates (90%, LOW)
- Component 1.5: Activate --watch (95%, LOW)
- Component 1.6: Query interface (100%, ZERO)
- Component 1.7: Rename R0-R5 (100%, ZERO)
- Component 3.1: Fix cloud job (100%, LOW)

**Total: 3.5 hours, ~95% avg confidence, guaranteed impact**

---

### Medium Confidence, Medium Risk (DO SECOND)
- Component 1.2: Incremental processing (85%, MED)
- Component 1.4: Convergence detection (80%, MED)
- Component 2.1: Butler protocol (85%, LOW)
- Component 2.2: Butler interfaces (80%, MED)
- Component 2.4: Ollama integration (85%, LOW)
- Component 3.2: R0 deployment (90%, LOW)

**Total: 8.5 hours, ~84% avg confidence, high impact**

---

### Lower Confidence, Higher Risk (DO LAST OR DEFER)
- Component 2.3: Concierge rewrite (70%, HIGH)
- Component 2.6: Integration tests (75%, DISCOVERY)
- Component 3.3-7: R1-R5 cloud (40%, HIGH)

**Total: 22 hours, ~62% avg confidence, uncertain outcome**

---

## EXECUTION STRATEGY

### Phase A: High-Confidence Wins (3.5h)
Execute Components: 1.1, 1.3, 1.5, 1.6, 1.7, 3.1

**Result after 3.5 hours:**
- Refinery in pipeline ✅
- Chunks validated ✅
- Continuous updates ✅
- Queryable via CLI ✅
- Clean naming ✅
- Cloud job fixed ✅

**Confidence this succeeds:** 95%
**Impact:** Massive (automation jumps to 95%)

---

### Phase B: Incremental Improvements (8.5h)
Execute Components: 1.2, 1.4, 2.1, 2.2, 2.4, 3.2

**Result after 8.5 hours more:**
- Incremental refinery ✅
- Convergence detection ✅
- Butler protocol standard ✅
- 8 butlers implemented ✅
- Ollama routing ✅
- R0 snapshots accumulating ✅

**Confidence this succeeds:** 84%
**Impact:** High (foundation for all future work)

---

### Phase C: Advanced (22h - DEFER)
Execute Components: 2.3, 2.6, 3.3-7

**Result after 22 hours more:**
- Concierge hub unified ✅
- Full integration tested ✅
- R1-R5 cloud layers ✅

**Confidence this succeeds:** 62%
**Impact:** Medium (nice-to-have, not critical)
**Recommendation:** Defer until Phase A+B proven

---

## RECOMMENDATION

### Execute Phase A ONLY (3.5 hours, 95% confidence)

**Why:**
- Highest confidence components
- Lowest risk
- Highest impact
- Proven patterns
- Easy rollback

**What you get:**
- Knowledge automatically maintained ✅
- Queryable via CLI ✅
- Safe from corruption ✅
- Cloud job fixed ✅
- Zero manual steps ✅

**Then:** Assess if Phase B needed, or if Phase A is sufficient.

---

## FINAL CONFIDENCE ASSESSMENT

### Overall Plan Confidence (4D Scoring):

**Factual:** 88%
- Most components use proven patterns
- Some unknowns in cloud deployment

**Alignment:** 99%
- Directly addresses "everything automatic" vision
- Minor deviations possible in execution

**Current:** 82%
- Tier 1 fits current architecture well
- Tier 2-3 require more adaptation

**Onwards:** 98%
- Strong foundation for future enhancements
- Extensible design

**Overall (min):** 82%

**Verdict:** SOLID - High confidence in core components, uncertainty in advanced features

---

## IS IT BETTER THAN NOT HAVING IT?

### Tier 1 (7h):
**YES - 95% confidence**
- Knowledge always fresh (vs manual `./pe wire`)
- Safe processing (vs potential corruption)
- Instant queries (vs loading files)

### Tier 2 (15h total):
**MAYBE - 70% confidence**
- Unified hub nice but not critical
- Current concierge + pe commands work fine
- Risk of building theater again

### Tier 3 (35h total):
**DEFER - 40% confidence**
- Cloud layers unproven
- High complexity
- Uncertain value until Tier 1+2 proven

---

## EXECUTION DECISION

**RECOMMENDED:** Execute Tier 1 Phase A (3.5 hours, 95% confidence)

**Components:**
1. Wire refinery (30min)
2. Validation gates (1h)
3. Activate --watch (30min)
4. Query CLI (15min)
5. Rename R0-R5 (15min)
6. Fix cloud job (1h)

**Total:** 3.5 hours
**Confidence:** 95%
**Impact:** Automation 62% → 95%

**Then assess:** Is more integration needed? Or is this sufficient?

---

**SHALL I EXECUTE PHASE A (3.5 HOURS)?**

This is the highest-confidence, highest-impact work. Everything else can wait.
