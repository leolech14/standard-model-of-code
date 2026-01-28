# PIPELINES - Disambiguation

**📍 Governance:** [DECISIONS](./DECISIONS.md) | [ROADMAP](./ROADMAP.md) | [Quality Gates](./QUALITY_GATES.md)
**📊 Architecture:** [SUBSYSTEMS.yaml](./SUBSYSTEMS.yaml) | [DOMAINS.yaml](./DOMAINS.yaml)

**Critical:** PROJECT_elements has TWO major pipelines. Always specify which one.

---

## 1. COLLIDER PIPELINE (Codome Analysis)

**Location:** `standard-model-of-code/src/core/pipeline/`

**Purpose:** Analyze code → generate graph + metrics

**Stages:** 28 (verified 2026-01-27)

**Phases:**
1. **Extraction** (0-2): Survey, AST parsing, atom classification
2. **Enrichment** (2.5-2.11): Ecosystem, dimensions, scope, control flow, patterns, data flow
3. **Analysis** (3-6.8): Purpose hierarchy, edges, Markov, knots, graph analytics, codome boundaries
4. **Intelligence** (7-8.6): Data flow macro, performance, constraints, purpose intelligence
5. **Output** (9-12): Roadmap, topology, semantic cortex, AI insights, manifest, final output

**Entrypoint:** `./collider full <path>` or `./pe collider full <path>`

**Input:** Source code (.py, .js, .go, etc.)

**Output:** `unified_analysis.json` (22MB), `collider_report.html` (interactive viz)

**Canonical source:** `src/core/pipeline/stages/__init__.py` (code)

**Documentation:** `docs/specs/PIPELINE_STAGES.md` (REFERENCE, generated from code)

---

## 2. REFINERY PIPELINE (Contextome Atomization)

**Location:** `context-management/tools/ai/aci/refinery.py`

**Purpose:** Break docs/config into semantic chunks for AI consumption

**Stages:** 8 (verified 2026-01-27)

**Known phases:**
1. **Load** - Read file (Python, Markdown, YAML)
2. **Chunk** - Semantic splitting (functions, sections, keys)
3. **Enrich** - Add metadata (relevance score, embeddings)
4. **Index** - Build searchable registry
5. **Cache** - Store for reuse

**Entrypoint:** `python context-management/tools/ai/aci/refinery.py <path>`

**Input:** Documentation (.md), config (.yaml), code (.py)

**Output:** `*_chunks.json` (agent_chunks, core_chunks, aci_chunks)

**Canonical source:** `context-management/tools/ai/aci/refinery.py` (code)

**Documentation:** Missing - needs `REFINERY_PIPELINE_STAGES.md`

---

## 3. FILESYSTEM WATCHER PIPELINE (Background Automation)

**Location:** `.agent/tools/filesystem_watcher.py` + wire.py

**Purpose:** Watch files → auto-trigger refinement on changes

**Stages:**
1. **Detect** - Filesystem events (create, modify, delete)
2. **Quiet Period** - Wait 5 minutes for batch
3. **Wire** - Trigger refinery.py on changed files
4. **Validate** - Check chunk integrity
5. **Update State** - Record metrics, timestamps

**Entrypoint:** Auto-starts via LaunchAgent or `screen -dmS watcher`

**Input:** File change events

**Output:** Updated chunks in `.agent/intelligence/chunks/`

---

## TERMINOLOGY RULES

### ❌ DON'T SAY:
- "the pipeline" (ambiguous)
- "pipeline stages" (which one?)
- "28 stages" (missing context)

### ✅ DO SAY:
- "Collider pipeline" (28 stages)
- "Refinery pipeline" (N stages)
- "Watcher pipeline" (5 phases)
- "Collider stage 11.5" (ManifestWriter)
- "Refinery chunking phase"

---

## UPDATING DOCUMENTATION

All docs that say "pipeline" must be updated to specify:

| File | Current | Should Say |
|------|---------|------------|
| DOMAINS.yaml | "Pipeline" domain | "Collider Pipeline" |
| QUALITY_GATES.md | "Pipeline stage count" | "Collider pipeline stage count" |
| ROADMAP.md | "Pipeline stages" | "Collider pipeline stages" |
| Any analysis doc | "pipeline" | "Collider pipeline" |

---

## NEXT: Document Refinery Pipeline Stages

**Action needed:**
1. Read `refinery.py` code
2. Identify distinct phases/stages
3. Create `REFINERY_PIPELINE_STAGES.md`
4. Add to DOMAINS.yaml as separate domain
5. Update SUBSYSTEMS.yaml WAVE entry

---

**This disambiguation prevents future confusion as both pipelines grow.**
