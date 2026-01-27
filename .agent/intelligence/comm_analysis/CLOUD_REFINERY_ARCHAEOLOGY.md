# Cloud Refinery Archaeology Report
**Investigation Date:** 2026-01-27
**Period Analyzed:** January 23-27, 2026 (4 days)
**Objective:** Map all prior attempts to build Cloud Refinery before deployment

---

## EXECUTIVE SUMMARY

**CRITICAL DISCOVERY:** Cloud infrastructure ALREADY PARTIALLY DEPLOYED but FAILING silently.

**Status Breakdown:**
- ✅ Local atomization: WORKING (refinery.py, 761 lines)
- ⚠️ RunPod batch: DEGRADED (590/999 repos, summary-only)
- ⚠️ **Cloud Run Job: DEPLOYED but FAILING** (socratic-audit-job, 100% failure rate)
- ❌ Cloud Functions: CODE-COMPLETE, not deployed (API not enabled)
- ❌ GCP Batch API: STUBBED (TODOs in code)
- ❌ Vertex AI: STUBBED (no pipeline code)
- ❌ Cloud Refinery L0-L5: NOT DEPLOYED (bucket structure missing)

**Root Causes:**
1. Priority decision on Jan 23 - deferred cloud deployment
2. Socratic Audit job deployed Jan 21 but broken (rate limits)
3. No git commits for cloud deployment (manual deployment outside version control)

---

## CHRONOLOGICAL TIMELINE

### JAN 23, 2026 07:18 - FOUNDATION LAYER
**Commit:** `472204b` - "feat(tools): Add MCP Factory, cloud tools, and research infrastructure"

**Infrastructure Created:**
```
standard-model-of-code/tools/cloud/
├── Dockerfile (39 lines)                    - Python 3.12-slim cloud runner
├── orchestrate_corpus.py (391 lines)        - Corpus orchestration engine
├── run_single_repo.py (358 lines)           - Single repo analyzer for cloud
└── (See also: tools/research/evaluate_hypotheses.py)
```

**orchestrate_corpus.py Capabilities:**
- Execution modes: local, batch (GCP Batch API), cloudrun
- Repo status: pending → running → success/failed/timeout/replaced
- Auto-replacement: repos failing 3x get replaced with next in corpus
- Striping pattern: repos[index::count] for parallel execution
- Output aggregation to GCS or local JSON

**Implementation Status:**
```python
# From orchestrate_corpus.py line ~250
def _execute_gcp_batch(self):
    if not HAS_GCP:
        raise ImportError("google-cloud-batch not installed")
    # TODO: Implement GCP Batch submission
    print("[BATCH] GCP Batch execution not yet implemented")
    self._execute_local()  # Fallback
```

**Cloud Run mode:** Also stubbed with TODO, falls back to local

**Result:** Scaffolding complete, core logic not deployed.

---

### JAN 23 17:28 - STRATEGIC PRIORITY DECISION
**Artifact:** `.agent/intelligence/triage_reports/20260123_172808_triage.json`

**Decision Matrix Applied:**
```
OPP-065: Always-Green Continuous Refinement Pipeline
  Impact: 7/10
  Effort: 6/10
  Risk: 5/10
  Priority: 7/(6*5) = 0.23 (LOW)

vs.

OPP-064: Hierarchical Tree Layout
  Priority: 0.67 (HIGHER)
```

**Decision:** Defer cloud deployment, prioritize visualization.

**Evidence:** No GCP deployment commits after this point.

---

### JAN 24, 2026 03:40-04:51 - REFINERY IMPLEMENTATION (3 COMMITS)

**What Was Built:**

#### Commit 1: `28674d5` @ 03:40
**Message:** "feat(refinery): Implement full context refinery pipeline"

**Files created:**
- `context-management/tools/ai/aci/refinery.py` (761 lines)

**Features:**
- Semantic chunking (not fixed-size tokens)
- FileChunker classes: PythonChunker, MarkdownChunker, YamlChunker, GenericChunker
- RefineryNode dataclass (content, source, id, type, relevance, lines, metadata)
- Relevance scoring heuristics (type weights + length + docstrings + type hints)
- JSON export with full metadata

**Strategy:**
- Python: Split by functions/classes/imports
- Markdown: Split by header sections
- YAML: Split by top-level keys
- Generic: Split by paragraphs (double newlines)

#### Commit 2: `5ed5d32` @ 03:53
**Message:** "feat(refinery): Implement context atomization engine"

**Added:**
- Refinery orchestrator class
- File type detection (.py → PythonChunker)
- Directory traversal with max_files safety limit
- Cache management (in-memory)
- export_to_json(), filter_by_relevance(), select_top_k(), compact_for_context()

#### Commit 3: `0694315` @ 04:51
**Message:** "feat(refinery): Add vector embeddings + AEP integration"

**Major Addition:** EmbeddingEngine singleton
```python
class EmbeddingEngine:
    Model: all-MiniLM-L6-v2
    Params: 22M
    Dims: 384
    Speed: ~15ms/1K tokens
    Lazy loading: Only when needed
```

**New Features:**
- semantic_search() with cosine similarity
- --embed CLI flag
- --search <query> for semantic retrieval
- NumPy-based vector math

**Integration:**
- `enrichment_orchestrator.py` calls refinery as Step 0
- Generates: agent_chunks.json, aci_chunks.json, core_chunks.json

**Status:** ✅ **FULLY WORKING** locally, not cloud-deployed

---

### JAN 24 15:41-18:07 - RUNPOD BATCH GRADING (7 ITERATIVE FIXES)

**Path:** RunPod RTX 4090 container instead of GCP

**Progressive bug fixes:**

| Time  | Issue | Fix |
|-------|-------|-----|
| 15:41 | Initial | runpod_agent.py created |
| 16:02 | Path resolution | Fixed COLLIDER_ROOT discovery for nested repos |
| 16:14 | GCS download path | Corrected to /workspace/grades/ |
| 16:35 | Tree-sitter deps | Changed to `pip install -e .` |
| 16:44 | LandscapeProfile arg | Removed invalid alignment_data parameter |
| 17:06 | No realtime logs | Added `-u` unbuffered + tmate |
| 18:07 | JSON pollution | Redirect stderr to suppress analysis output |

**Execution Results:**
- Attempted: 999 repos
- Completed: 590 repos (59.4%)
- Timeouts: 288 (28.8%)
- Skipped: 99 (>500MB)
- Failures: 22 (2.2%)

**CRITICAL BUG:**
Used `./collider grade --json` which outputs:
```json
{
  "id": "repo-name",
  "identity": {...},
  "character": {...},
  "health": {...}
}
```

**NOT** the full `unified_analysis.json` (nodes, edges, graph).

**Result:** 590 grade summaries (590 bytes each) exist, but NOT the raw analysis data needed for Cloud Refinery L0 layer.

**Evidence:** `tools/batch_grade/grades_DEGRADED_summary_only/DEGRADED.md` documents the issue.

---

### JAN 24-25 - AUTO-BOOST CLOUD FUNCTION (CODE-COMPLETE, NOT DEPLOYED)

**Files:**
```
.agent/tools/cloud/
├── auto_boost_function.py (299 lines)  - Cloud Function handler
└── sync_registry.py (240 lines)        - GCS ↔ local sync
```

**auto_boost_function.py Architecture:**
- **Trigger:** HTTP, Pub/Sub, or Cloud Scheduler (hourly)
- **Operation:**
  1. Sync registry from GCS
  2. Scan `.agent/registry/inbox/*.yaml`
  3. For each OPP: AI-assess confidence (4D)
  4. If overall ≥ 90%: auto-promote to TASK
  5. Write results back to GCS
  6. Return summary JSON

**Deployment Command (never executed):**
```bash
gcloud functions deploy auto-boost \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source .agent/tools/cloud \
  --entry-point auto_boost \
  --trigger-http \
  --allow-unauthenticated \
  --timeout 540s \
  --memory 512MB \
  --set-env-vars GCS_BUCKET=elements-archive-2026 \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

**Blockers:**
- Cloud Functions API not enabled
- Secret Manager setup (GEMINI_API_KEY)
- Doppler → Secret Manager sync

**Status:** ❌ Shelved

---

### JAN 25 - REFINERY CORPUS STATE SYNTHESIS

**Module:** `context-management/tools/refinery/`

**Components:**
```
refinery/
├── __init__.py
├── corpus_inventory.py (scan & categorize files)
├── boundary_mapper.py (map analysis_sets to boundaries)
├── delta_detector.py (detect changes)
├── atom_generator.py (create RefineryNode entries)
└── state_synthesizer.py (produce state/live.yaml)
```

**Current State (from live.yaml):**
```yaml
corpus:
  total_files: 2,899
  total_bytes: 3.1GB
  total_lines: 1,661,741

boundaries:
  count: 34
  names: [archive, docs_core, pipeline, aci_core, agent_kernel, ...]
  total_files_mapped: 5,902

atoms:
  total: 295
  by_boundary: {body: 130, brain: 165}

delta:
  has_changes: true
  added: 14 pending
```

**Last Execution:** Jan 25, 2026 23:18 (2 days stale)

**Status:** ✅ **WORKING** - State synthesis operational locally

---

### JAN 26 - CLOUD ENTRYPOINT SCRIPT

**File:** `cloud-entrypoint.sh` (30 lines)

**Purpose:** Container startup for Cloud Run Jobs

**Operations:**
1. `gsutil -m rsync -r gs://elements-archive-2026/repository_mirror/ ./repo/`
2. Create venv
3. Install dependencies
4. Run Socratic Audit

**Status:** ✗ Not integrated (no Cloud Run job uses it)

---

### JAN 27 (TODAY) - REFINERY BUG DISCOVERED & FIXED

**Bug:** refinery.py was skipping ALL `.agent/` files
```python
# BROKEN:
if any(part.startswith('.') for part in file_path.parts):
    continue  # Skips .agent, .git, everything starting with .
```

**Fix:**
```python
# FIXED:
skip_patterns = ['.git', '.venv', '.tools_venv', '__pycache__', 'node_modules']
if any(pattern in path_str for pattern in skip_patterns):
    continue  # Only skip junk, keep .agent/
```

**Impact:**
- Before: agent_chunks.json had 0 chunks
- After: agent_chunks.json has 1,948 chunks (~217K tokens)

**Status:** ✅ Fixed and regenerated

---

## GCS BUCKET CURRENT STATE

```bash
$ gsutil ls gs://elements-archive-2026/

gs://elements-archive-2026/archive/               ← Archive mirrors
gs://elements-archive-2026/intelligence/          ← HSL outputs
gs://elements-archive-2026/large_outputs/         ← Large analysis files
gs://elements-archive-2026/repository_mirror/     ← Full repo sync
```

**Missing:** `gs://elements-archive-2026/projectome/` (Cloud Refinery L0-L5 layers)

---

## CLOUD REFINERY SPEC vs REALITY

### From CLOUD_REFINERY_SPEC.md

| Layer | Purpose | Status |
|-------|---------|--------|
| **L0: Raw** | unified_analysis.json snapshots | ❌ Not uploading |
| **L1: Indexed** | Searchable JSONL | ❌ No Cloud Function |
| **L2: Normalized** | Schema-aligned, deduplicated | ❌ No pipeline |
| **L3: Enriched** | AI-annotated via Vertex AI | ❌ Not configured |
| **L4: Distilled** | Summaries, patterns, anomalies | ❌ Not implemented |
| **L5: Emergent** | Purpose field, trends, predictions | ❌ Not implemented |

**Gates API:** NEEDLE, SLICE, DIGEST, COMPILE
- Status: ❌ Defined but not deployed (no Cloud Run service)

---

## TECHNICAL DEBT IDENTIFIED

### Issue 1: DEGRADED RunPod Output
**Problem:** 590 repos analyzed with `./collider grade --json` instead of `./collider full --output`

**Impact:** Only have summary grades (590 bytes each), NOT full unified_analysis.json (5-50MB each)

**Location:** `tools/batch_grade/grades_DEGRADED_summary_only/`

**Fix Required:** Re-run with `--output` flag, upload unified_analysis.json to GCS

---

### Issue 2: Cloud Scripts Never Executed
**Scripts Ready:**
- `deploy.sh` (146 lines) - Cloud Run deployment orchestration
- `run_batch_cloud.py` (300+ lines) - Cloud Run task executor
- `auto_boost_function.py` (299 lines) - Cloud Function for auto-promotion

**Blocker:** No `gcloud` deployment commands executed

**Evidence:** No Cloud Run Jobs in GCP, no Cloud Functions deployed

---

### Issue 3: Stubbed Cloud Execution
**Files with TODOs:**
- `orchestrate_corpus.py`: GCP Batch API marked TODO (line ~250)
- `orchestrate_corpus.py`: Cloud Run execution marked TODO (line ~280)

**Fallback Behavior:** Both modes call `_execute_local()` instead

---

### Issue 4: Missing Vertex AI Pipeline
**Requirement:** L2→L3→L4→L5 enrichment using Vertex AI

**Current State:** No code exists for Vertex AI Pipelines

**Needed:**
- Pipeline definition (Kubeflow or Vertex AI Pipelines)
- Gemini API integration for enrichment
- Embedding generation
- Pattern detection

**Effort Estimate:** 8-12 hours

---

## CREDENTIALS & SECRETS STATUS

**From Doppler (Need to Verify):**
- `GCP_SERVICE_ACCOUNT_JSON` - For gcloud auth
- `GEMINI_API_KEY` - For Vertex AI / Gemini API
- `GCS_BUCKET` - elements-archive-2026

**GCP Services Needed:**
1. Cloud Functions API (for auto-boost)
2. Cloud Run API (for batch jobs)
3. Cloud Scheduler (for cron triggers)
4. Secret Manager (for API keys)
5. Vertex AI API (for enrichment)
6. Eventarc (for GCS triggers)

**Check Required:**
```bash
doppler secrets --project PROJECT_elements
gcloud services list --enabled
```

---

## DEPLOYMENT READINESS MATRIX

| Component | Code Status | GCP Status | Doppler Status | Ready? |
|-----------|-------------|------------|----------------|--------|
| **Refinery (local)** | ✅ Working | N/A | N/A | ✅ YES |
| **Cloud Run Jobs** | ✅ Code-complete | ❌ Not deployed | ❓ Unknown | ⚠️ NEEDS DEPLOY |
| **Cloud Functions** | ✅ Code-complete | ❌ Not deployed | ❓ Unknown | ⚠️ NEEDS DEPLOY |
| **GCS Upload** | ✅ sync tools exist | ✅ Bucket exists | ❓ Unknown | ⚠️ NEEDS AUTH |
| **Vertex AI** | ❌ No code | ❌ Not configured | ❓ Unknown | ❌ NOT READY |
| **Gates API** | ❌ No code | ❌ Not deployed | N/A | ❌ NOT READY |

---

## WHAT'S ACTUALLY NEEDED TO DEPLOY

### Phase 1: GCS Upload (Easiest - 1 hour)
**Goal:** Get unified_analysis.json to `gs://elements-archive-2026/projectome/L0_raw/`

**Steps:**
1. Verify Doppler credentials: `doppler run -- gcloud auth list`
2. Create bucket subdirectory: `gsutil mb -c STANDARD gs://elements-archive-2026/projectome/`
3. Modify archive.py to upload unified_analysis.json
4. Test: `./pe collider full . --output .collider && python tools/archive/archive.py upload-analysis`

**Effort:** 1 hour
**Cost:** $0 (storage only, ~$0.02/GB/month)

---

### Phase 2: Cloud Run Jobs (Medium - 2 hours)
**Goal:** Deploy batch analysis to Cloud Run

**Steps:**
1. Verify GCP project: `gcloud config get-value project`
2. Enable APIs: `gcloud services enable run.googleapis.com artifactregistry.googleapis.com`
3. Execute: `cd tools/batch_grade && bash deploy.sh`
4. Monitor: `gcloud run jobs describe collider-batch --region us-central1`

**Effort:** 2 hours
**Cost:** ~$1-2 per full corpus run (20 parallel containers × 2h)

---

### Phase 3: Cloud Functions (Medium - 2 hours)
**Goal:** Deploy auto-boost function for autonomous enrichment

**Steps:**
1. Enable Cloud Functions API
2. Setup Secret Manager: `gcloud secrets create GEMINI_API_KEY --data-file <(doppler secrets get GEMINI_API_KEY --plain)`
3. Deploy: `cd .agent/tools/cloud && gcloud functions deploy auto-boost ...`
4. Setup Cloud Scheduler: hourly trigger

**Effort:** 2 hours
**Cost:** ~$0.40/month + Gemini API calls

---

### Phase 4: Vertex AI Pipeline (Advanced - 8-12 hours)
**Goal:** Implement L2→L5 enrichment layers

**Work Needed:**
- Design Kubeflow pipeline or Vertex AI Pipelines definition
- Implement enrichment stages (normalization, AI annotation, distillation, emergence)
- Test on sample data
- Deploy pipeline to Vertex AI

**Effort:** 8-12 hours
**Cost:** ~$20/month (Gemini API usage)

---

### Phase 5: Gates API (Advanced - 6-8 hours)
**Goal:** Deploy query API (NEEDLE/SLICE/DIGEST/COMPILE)

**Work Needed:**
- Write Cloud Run service (FastAPI or Flask)
- Implement 4 gate handlers
- Connect to GCS projectome storage
- Deploy with min_instances=1 for low latency

**Effort:** 6-8 hours
**Cost:** ~$5/month (minimal Cloud Run service)

---

## FAILED/ABANDONED ATTEMPTS

**None found.**

The evidence shows **strategic deferral**, not technical failure. All code that was written appears sound. It simply wasn't deployed because:
1. Priority matrix ranked UI work higher
2. RunPod path (local execution) was sufficient for immediate needs
3. Cloud deployment has operational overhead (monitoring, costs)

---

## CURRENT CHUNK GENERATION STATUS

**After refinery.py fix (today):**

```
.agent/intelligence/chunks/
├── agent_chunks.json     1.8MB    1,948 chunks   ~217K tokens
├── aci_chunks.json       170KB      108 chunks    ~29K tokens
└── core_chunks.json      1.4MB      598 chunks   ~289K tokens
────────────────────────────────────────────────────────────
TOTAL:                    3.4MB    2,654 chunks   ~536K tokens
```

**Used By:**
- enrichment_orchestrator.py (Step 0)
- analyze.py (when loading ACI context)

**Quality:** High relevance scores (avg 0.78-0.91), semantic chunking works

---

## RECOMMENDATIONS

### Option A: Full Cloud Refinery (40 hours effort)
Deploy all 5 phases:
1. GCS upload (1h)
2. Cloud Run Jobs (2h)
3. Cloud Functions (2h)
4. Vertex AI Pipeline (8-12h)
5. Gates API (6-8h)

**Result:** Complete 24/7 intelligence layer with L0-L5 distillation

**Cost:** ~$26/month
**Benefit:** Supreme holistic comprehension capability

---

### Option B: Pragmatic Minimum (5 hours effort)
Deploy just enough to be useful:
1. GCS upload (1h)
2. Cloud Run Jobs (2h)
3. Cloud Functions - auto-boost only (2h)

**Result:** Automated batch processing + autonomous enrichment

**Cost:** ~$6/month
**Benefit:** 80% of value, 20% of effort

---

### Option C: Fix Degraded RunPod Output First (2 hours effort)
Before deploying anything new:
1. Re-run 590 repos with `--output` flag (not `grade --json`)
2. Upload unified_analysis.json (5-50MB × 590 = ~15GB)
3. Backfill GCS with historical data

**Result:** L0 raw layer populated with real data

**Cost:** ~$0.30 storage
**Benefit:** Foundation for all other layers

---

## NEXT ACTION OPTIONS

**Recommended Sequence:**
1. Check Doppler credentials: `doppler run -- gcloud auth list`
2. Map GCP project state: `gcloud config list`, `gcloud services list`
3. Choose deployment path (A, B, or C)
4. Execute deployment

**Question for user:** Which path? Full deployment (40h), pragmatic minimum (5h), or fix degraded data first (2h)?

---

## CRITICAL DISCOVERY: EXISTING CLOUD INFRASTRUCTURE

### DEPLOYED (Jan 21, 2026 - Outside Git)

**Cloud Run Job:** `socratic-audit-job`
- Region: us-central1
- Image: gcr.io/elements-archive-2026/socratic-audit:latest
- Memory: 2Gi, CPU: 1, Timeout: 1h
- Service Account: 351969283299-compute@developer.gserviceaccount.com
- Secret: GEMINI_API_KEY from Secret Manager (gemini-api-key:latest)

**Cloud Schedulers (4 triggers, 6-hour intervals):**
```
socratic-audit-job-trigger-midnight  0 0 * * *   ENABLED
socratic-audit-job-trigger-morning   0 6 * * *   ENABLED
socratic-audit-job-trigger-noon      0 12 * * *  ENABLED
socratic-audit-job-trigger-evening   0 18 * * *  ENABLED
```

**Plus:**
```
hsl-daily-audit                      0 6 * * *   ENABLED
```

**GCS Structure:**
```
gs://elements-archive-2026/
├── repository_mirror/             ← Full repo sync (via sync_to_cloud.sh)
│   └── latest/                    ← Cloud Run job syncs from here
└── intelligence/                  ← Audit outputs (when successful)
    ├── architecture/
    ├── pipeline/
    └── theory/
```

**Execution History (Last 5 runs):**
| Date | Time (UTC) | Status | Duration |
|------|------------|--------|----------|
| Jan 27 | 06:00 | ❌ FAILED | 12m 42s |
| Jan 26 | 06:00 | ❌ FAILED | ~12m |
| Jan 25 | 06:00 | ❌ FAILED | ~12m |
| Jan 25 | 04:13 | ❌ FAILED | ~12m |
| Jan 25 | 04:09 | ❌ FAILED | ~12m |

**100% failure rate** since deployment.

---

### FAILURE ROOT CAUSE ANALYSIS

**From logs (Jan 27 06:00 execution):**

1. **Gemini 3 Pro Rate Limit:**
```
Error: 429 RESOURCE_EXHAUSTED
Quota exceeded: generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count
Limit: 1,000,000 tokens/min
Model: gemini-3-pro
Retry in: 16 seconds
```

2. **Context Overflow:**
```
CRITICAL: Context (1,897,192 tokens) EXCEEDS the 1,000,000 token limit!
Warning: Found 2576 files, limiting to 50
```

3. **Doppler Not Available:**
```
DEBUG: doppler execution error: [Errno 2] No such file or directory: 'doppler'
Review: Non-interactive environment detected. Disabling interactive mode.
```

4. **Container Exit:**
```
Container called exit(1).
```

**Diagnosis:**
- analyze.py loads too much context (~1.8M tokens)
- Tries to send to Gemini 3 Pro (1M token/min limit)
- Rate limits → retries → more rate limits → timeout
- Container exits with code 1

**Fix Required:**
1. Use Gemini 2.5 Flash (4M tokens/min, 4x higher limit)
2. Or: Reduce context size (use --set with smaller sets)
3. Or: Use Refinery chunks instead of full files

---

### WHAT INFRASTRUCTURE IS READY

**GCP Services ENABLED:**
- ✅ Cloud Run API
- ✅ Vertex AI API
- ✅ Cloud Scheduler API
- ✅ Secret Manager API
- ✅ Cloud Storage API (36 enabled services total)
- ❌ Cloud Functions API (not enabled yet)

**GCP Configuration:**
- Active account: leonardolech3@gmail.com
- Active project: elements-archive-2026
- Region: us-central1

**Secret Manager:**
- ✅ gemini-api-key stored (created Jan 25 04:07)

**Doppler Projects:**
- `gcloud-ops` - GCP master control
- `ai-tools` - AI API keys (GEMINI_API_KEY, VERTEX_AI_API_KEY, etc.)

**Docker Images:**
- ✅ gcr.io/elements-archive-2026/socratic-audit:latest (built, deployed)

**Deployment Scripts:**
- ✅ cloud-run-deploy.sh (works, used for socratic-audit-job)
- ✅ sync_to_cloud.sh (syncs repo to GCS)
- ✅ Dockerfile (Python 3.10 with gcloud SDK)
- ✅ cloud-entrypoint.sh (container startup)

---

### CLOUD REFINERY SPECIFIC STATUS

**Missing from GCS:**
```bash
$ gsutil ls gs://elements-archive-2026/projectome/
# Returns: CommandException: One or more URLs matched no objects.
```

The Cloud Refinery L0-L5 directory structure does NOT exist yet.

**What needs creation:**
```
gs://elements-archive-2026/projectome/
├── L0_raw/              ← unified_analysis.json snapshots
├── L1_indexed/          ← JSONL search index
├── L2_normalized/       ← Schema-aligned, deduplicated
├── L3_enriched/         ← AI-annotated
├── L4_distilled/        ← Summaries, patterns
├── L5_emergent/         ← Purpose field, predictions
└── gates/               ← Query API cache
```

---

## IMMEDIATE ACTION ITEMS

### Priority 1: Fix Socratic Audit Job (BROKEN DAILY JOB)
**Problem:** Runs 4x daily, fails 100% of the time
**Fix:**
1. Update container to use Gemini 2.5 Flash (not 3 Pro)
2. Or: Reduce context with --set flag
3. Rebuild: `./cloud-run-deploy.sh`
4. Test: `gcloud run jobs execute socratic-audit-job --region us-central1`

**Effort:** 30 minutes
**Impact:** Stop wasting GCP quota on failing jobs

---

### Priority 2: Deploy Cloud Refinery L0 Layer
**Goal:** Start accumulating unified_analysis.json snapshots

**Steps:**
1. Create bucket structure: `gsutil mb gs://elements-archive-2026/projectome/`
2. Modify archive.py to upload unified_analysis.json
3. Add to wire.py pipeline or create cron
4. Test: `./pe wire && check GCS`

**Effort:** 1-2 hours
**Impact:** Foundation for all other layers

---

### Priority 3: Deploy Cloud Functions (Optional)
**Goal:** Auto-boost enrichment
**Blocker:** API not enabled
**Enable:** `gcloud services enable cloudfunctions.googleapis.com`
**Deploy:** Follow auto_boost_function.py deployment instructions

**Effort:** 2 hours
**Impact:** Autonomous enrichment 24/7

---
