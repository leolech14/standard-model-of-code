# Research Inventory - Auto-Saved Queries
**Date:** 2026-01-27
**Status:** FULLY AUTOMATIC - Every query saved
**Total:** 681 research files across all time

---

## YES - AUTO-SAVE IS ENABLED ✅

### Location
```
standard-model-of-code/docs/research/
├── gemini/                      # Gemini API queries
│   ├── sessions/                # Full conversation JSON (243 files)
│   ├── docs/                    # Markdown summaries (246 files)
│   └── raw/                     # Raw API responses (243 files)
│
└── perplexity/                  # Perplexity Sonar queries
    ├── docs/                    # Markdown reports (148 files)
    ├── raw/                     # Raw JSON responses (144 files)
    └── *.md                     # Root level reports (44 files)
```

**Total Storage:** 14 MB (5.7 MB Gemini + 8.3 MB Perplexity)

---

## BREAKDOWN BY SOURCE

### Gemini Research (732 total files)
```
Sessions (JSON):     243 files  # Full conversation context
Docs (Markdown):     246 files  # Human-readable summaries
Raw (JSON):          243 files  # API responses

Format: gemini/sessions/YYYYMMDD_HHMMSS_query_preview.json
Example: 20260127_060333_we_re_designing_an_ai_assistance_system_.json
```

**Storage:** 5.7 MB

### Perplexity Research (336 total files)
```
Docs (Markdown):     148 files  # Formatted reports
Raw (JSON):          144 files  # API responses
Root Level (MD):      44 files  # Standalone queries

Format: perplexity/docs/YYYYMMDD_HHMMSS_query_preview.md
Example: 20260127_060622_research_question__what_are_the_minimal_essential.md
```

**Storage:** 8.3 MB

---

## THIS SESSION CONTRIBUTION

### From Jan 26-27 (Communication Fabric + Refinery + Dashboard):

**Gemini Queries:** 58 new sessions
- Architectural discussions
- Integration patterns
- Butler protocol design
- AI assistance systems

**Perplexity Queries:** 42 new research files
- Multi-service integration (60+ sources)
- AI agent assistance patterns
- Context engineering
- Recursive processing safety

**Total This Session:** 100 research files (~2 MB)

---

## MOST RECENT QUERIES (Last 10)

### Gemini:
1. `08:22` - Performance collapse fix (visualization)
2. `08:19` - Data flow in visualization system
3. `08:15` - Graph pause/animation investigation
4. `07:39` - Quality criteria for validation
5. `06:18` - Collider visualization redesign
6. `06:03` - **AI assistance system design** ← Integration architecture
7. `05:56` - **Butler integration protocol** ← This session
8. `05:54` - Integration spine design
9. `05:22` - Decision Deck architecture
10. `04:55` - MCP server duplication

### Perplexity:
1. `08:42` - Interface contracts & schema design
2. `08:40` - Zero-friction module distribution
3. `08:38` - Central hub / service locator patterns
4. `08:10` - 3D force graph performance
5. `08:09` - Multi-layer graph visualization
6. `07:09` - **AI-agent friendly module design** ← This session
7. `07:06` - **Plugin architecture patterns** ← This session
8. `06:39` - Deterministic figure caption extraction
9. `06:19` - 3D code visualization with Three.js
10. `06:06` - **Minimal essential features for AI agents** ← This session

---

## AUTO-SAVE MECHANISM

### Code Location
`context-management/tools/ai/analyze.py`

```python
# Line 383
AUTO_SAVE_ENABLED = True  # Set to False to disable

# Line 391
def auto_save_gemini_response(query, response_text, model, mode):
    """
    Saves to 3 locations:
    - sessions/TIMESTAMP_query.json (full conversation)
    - docs/TIMESTAMP_query.md (formatted markdown)
    - raw/TIMESTAMP_query.json (raw API response)
    """

# Line 2505
saved_path = auto_save_research(args.prompt, result, "sonar-pro")
print(f"[Auto-saved to: {saved_path}]")
```

**Trigger:** Every analyze.py query + every Perplexity MCP call

---

## WHAT GETS SAVED

### Gemini Queries:
- ✅ Full prompt + system message
- ✅ Complete response
- ✅ Model used (gemini-3-pro-preview, gemini-2.0-flash, etc.)
- ✅ Token counts (input/output)
- ✅ Cost estimate
- ✅ Timestamp
- ✅ Query summary (from first 50 chars)

### Perplexity Queries:
- ✅ Research question
- ✅ Full response with citations
- ✅ Source URLs (60+ for deep research)
- ✅ Model (sonar-pro)
- ✅ Timestamp
- ✅ Formatted markdown

**Format:** Timestamped filename with query preview

---

## HISTORICAL GROWTH

### Timeline:
- **Jan 22:** First queries (MCP factory, architecture)
- **Jan 23:** Decision Deck research (57KB flagship doc)
- **Jan 24:** Cloud deployment, health metrics
- **Jan 25:** Epistemology, semiotics, active inference
- **Jan 26:** Communication theory, control systems
- **Jan 27:** Integration architecture, AI assistance (THIS SESSION)

**Growth Rate:** ~40-60 queries per day (when active)

---

## ACCESSING THE RESEARCH

### By Date:
```bash
# Today's Gemini queries
ls -lt standard-model-of-code/docs/research/gemini/sessions/20260127_*.json

# Today's Perplexity queries
ls -lt standard-model-of-code/docs/research/perplexity/docs/20260127_*.md
```

### By Topic:
```bash
# Search Gemini research
./pe refinery search "integration architecture"

# Search Perplexity research
grep -r "multi-service" standard-model-of-code/docs/research/perplexity/docs/
```

### Via Refinery:
```bash
# Gemini/Perplexity docs ARE in chunks
./pe refinery search "butler protocol"
./pe refinery search "AI assistance"
./pe refinery search "Communication Fabric"

# Returns: Relevant research chunks
```

---

## STORAGE BREAKDOWN

**Current Size:** 14 MB total
- Gemini: 5.7 MB
- Perplexity: 8.3 MB

**Files:**
- Gemini: 732 files (sessions + docs + raw)
- Perplexity: 336 files (docs + raw)
- **Total: 1,068 research files**

**Growth:** ~2 MB per active session day

---

## AUTO-SAVE FORMAT

### Gemini Session File:
```json
{
  "query": "What is the right architectural abstraction...",
  "model": "gemini-2.0-flash-exp",
  "mode": "STANDARD",
  "context_size": 6365,
  "response": "Okay, this is an interesting...",
  "timestamp": "2026-01-27T05:56:35",
  "cost_estimate": 0.0387,
  "tokens": {"input": 7277, "output": 2013}
}
```

### Perplexity Doc File:
```markdown
# Multi-Service AI Agent Architecture Design

[Full research report with 60+ citations]

Sources:
- [Source 1](url)
- [Source 2](url)
...

---
_Auto-saved: perplexity/docs/YYYYMMDD_HHMMSS_query.md_
```

---

## QUERIES FROM THIS SESSION (Examples)

### Key Research Validated:

**1. Butler Integration Architecture**
- File: `gemini/sessions/20260127_055635_what_is_the_right_architectural_abstract.json`
- Result: "Direct imports with Protocol interfaces, NOT message queues"
- Sources: 1 Gemini analysis

**2. Minimal AI Assistance Features**
- File: `perplexity/docs/20260127_060622_research_question__what_are_the_minimal_essential.md`
- Result: "Surgical context, fast intent classification, graceful degradation"
- Sources: 60+ academic papers

**3. Multi-Service Integration**
- File: `perplexity/docs/20260127_055951_i_m_designing_an_integration_architecture_for_an_a.md`
- Result: "Synchronous for local, async for distributed"
- Sources: 60+ production examples

---

## ANSWER

### ✅ YES - AUTO-SAVE IS WORKING

**What:**
- Every Gemini query → 3 files (session.json, docs.md, raw.json)
- Every Perplexity query → 2 files (docs.md, raw.json)

**Where:**
- `standard-model-of-code/docs/research/gemini/` (732 files, 5.7 MB)
- `standard-model-of-code/docs/research/perplexity/` (336 files, 8.3 MB)

**How Many:**
- **Total:** 1,068 research files
- **This Session:** 100 files (~2 MB)
- **All Time:** Since Jan 22, 2026 (6 days)

**Growth:** ~40-60 queries/day when actively researching

**Searchable:** YES - via `./pe refinery search` (research docs are in chunks)

---

**The research archive is HUGE and AUTOMATIC. Every question you ask gets saved forever.**