# Research Depth Layers - Recursive Investigation Architecture
**Date:** 2026-01-27
**Principle:** Each research round goes deeper - track the depth
**Status:** SPECIFICATION → IMPLEMENTATION NEEDED

---

## THE CONCEPT

**Current:** Flat research archive (1,068 files, no depth organization)
**Target:** Layered research depth (D0 → D1 → D2 → D3...)

```
D0 (Surface)     "What is Communication Theory?"
    ↓
D1 (Validation)  "Validate Shannon's framework for software"
    ↓
D2 (Deep Dive)   "How do control systems apply to code?"
    ↓
D3 (Cross-Val)   "Compare Friston's FEP to our stability model"
    ↓
D4 (Synthesis)   "Integrate all findings into coherent theory"
```

**Each layer builds on the previous. Each goes deeper.**

---

## DEPTH LAYER DEFINITIONS

### D0: Initial Query (Surface)
**Trigger:** First question on a topic
**Scope:** Broad overview, establish baseline
**Sources:** 1-5 citations
**Output:** General answer, identify gaps

**Example:**
- Query: "What is Communication Theory?"
- Result: Shannon's M-I-P-O model, basic concepts
- Identifies: Need to validate for software context

**Marker:** No parent query, depth_level = 0

---

### D1: Validation (Verify)
**Trigger:** Validate D0 findings
**Scope:** Confirm claims, find academic grounding
**Sources:** 10-20 citations
**Output:** Validated claims, identify assumptions

**Example:**
- Query: "Validate Shannon's framework for software engineering"
- Parent: D0 "What is Communication Theory?"
- Result: Confirmed applicable, found 15 papers
- Identifies: Need stability analysis

**Marker:** parent_query_id = D0 query, depth_level = 1

---

### D2: Deep Dive (Explore)
**Trigger:** Explore specific aspect from D1
**Scope:** Narrow focus, deep investigation
**Sources:** 20-40 citations
**Output:** Detailed analysis, mathematical foundations

**Example:**
- Query: "Control theory stability analysis for software systems"
- Parent: D1 validation
- Result: Lyapunov functions, bifurcation theory
- Identifies: Need to compare with existing models

**Marker:** parent_query_id = D1 query, depth_level = 2

---

### D3: Cross-Validation (Compare)
**Trigger:** Validate D2 findings against alternatives
**Scope:** Compare approaches, find best fit
**Sources:** 40-60 citations
**Output:** Comparative analysis, trade-offs

**Example:**
- Query: "Compare Friston's Free Energy Principle to our stability model"
- Parent: D2 control theory
- Result: FEP aligns with our model, provides neurobiological grounding
- Identifies: Need synthesis

**Marker:** parent_query_id = D2 query, depth_level = 3

---

### D4: Synthesis (Integrate)
**Trigger:** Combine all findings into coherent theory
**Scope:** Multi-source integration, resolve conflicts
**Sources:** All previous layers
**Output:** Final theory, implementation plan

**Example:**
- Query: "Synthesize Communication Theory + Control Theory + FEP for software"
- Parents: D0, D1, D2, D3
- Result: Integrated Communication Fabric theory
- Output: COMMUNICATION_FABRIC_RESEARCH_SYNTHESIS.md

**Marker:** parent_query_ids = [D0, D1, D2, D3], depth_level = 4

---

### D5: Application (Implement)
**Trigger:** Build system based on D4 synthesis
**Scope:** Code implementation, validation
**Sources:** D4 synthesis + implementation research
**Output:** Working system (fabric.py)

**Example:**
- Action: Build fabric.py implementing Communication Fabric
- Parents: D4 synthesis
- Result: 400+ lines of working code
- Validation: Live metrics match theory predictions

**Marker:** parent_query_id = D4 synthesis, depth_level = 5, type = "implementation"

---

## METADATA SCHEMA

### Research Query Metadata
```yaml
query_id: "gemini_20260127_060333"
timestamp: "2026-01-27T06:03:33"
depth_level: 2
parent_query_id: "gemini_20260126_181710"  # D1 query
topic: "AI assistance architecture"
source: "gemini"  # gemini | perplexity
model: "gemini-2.0-flash-exp"

query: "We're designing an AI assistance system..."
status: "complete"
outcome: "Recommended direct imports over message queues"

children: ["gemini_20260127_070656", "gemini_20260127_070953"]  # Spawned D3 queries

citations: 15
tokens: 9290
cost: 0.0387

tags: ["integration", "architecture", "butler_protocol"]
```

---

## FILE NAMING CONVENTION

### Current (Flat):
```
20260127_060333_we_re_designing_an_ai_assistance_system_.json
```

### Proposed (Depth-Aware):
```
D2_20260127_060333_ai_assistance_system_integration.json
│  │               │                                 │
│  │               │                                 └─ Topic slug
│  │               └─ Timestamp
│  └─ Depth level (D0, D1, D2, D3, D4, D5)
└─ Prefix for sorting
```

**Benefit:** Files sort by depth automatically

---

## DIRECTORY STRUCTURE

### Current:
```
research/
├── gemini/
│   ├── sessions/  (all mixed together)
│   └── docs/      (all mixed together)
└── perplexity/
    └── docs/      (all mixed together)
```

### Proposed (Depth Layers):
```
research/
├── gemini/
│   ├── D0_surface/
│   │   ├── sessions/
│   │   └── docs/
│   ├── D1_validation/
│   │   ├── sessions/
│   │   └── docs/
│   ├── D2_deep/
│   │   ├── sessions/
│   │   └── docs/
│   ├── D3_cross_val/
│   ├── D4_synthesis/
│   └── D5_implementation/
│
└── perplexity/
    ├── D0_surface/
    ├── D1_validation/
    ├── D2_deep/
    ├── D3_cross_val/
    ├── D4_synthesis/
    └── D5_implementation/
```

**Benefit:** Browse by depth, see research progression

---

## DEPTH TRACKING METADATA FILE

### Create: `research/depth_index.yaml`

```yaml
version: 1
last_updated: "2026-01-27T08:50:00"
total_queries: 1068

depth_distribution:
  D0: 245  # Initial queries
  D1: 312  # Validation queries
  D2: 287  # Deep dives
  D3: 156  # Cross-validations
  D4: 52   # Syntheses
  D5: 16   # Implementations

topics:
  communication_theory:
    query_count: 23
    max_depth: 5
    root_query: "gemini_20260126_181710"
    synthesis_query: "gemini_20260126_200000"
    implementation: "fabric.py"

  decision_deck:
    query_count: 12
    max_depth: 3
    root_query: "perplexity_20260123_150543"
    outcome: "ABANDONED (theater)"

  butler_integration:
    query_count: 8
    max_depth: 3
    root_query: "gemini_20260127_055635"
    synthesis_query: "gemini_20260127_060333"
    status: "IN_PROGRESS"

queries:
  gemini_20260127_060333:
    depth_level: 2
    parent: "gemini_20260126_181710"
    children: ["gemini_20260127_070656", "gemini_20260127_070953"]
    topic: "butler_integration"
    timestamp: "2026-01-27T06:03:33"
    outcome: "Direct imports recommended"
    led_to_code: ["fabric_bridge.py", "butler_protocol.py (spec)"]
```

---

## RESEARCH PROGRESSION EXAMPLE (THIS SESSION)

### Topic: Communication Fabric

**D0:** "What is Communication Theory?" (Jan 26 18:00)
- Source: Perplexity
- Result: Shannon, control theory, FEP
- Citations: 30+

**D1:** "Validate Communication Theory for software" (Jan 26 18:30)
- Source: Gemini + Perplexity
- Result: Confirmed applicable
- Citations: 15 (Gemini), 30 (Perplexity)

**D2:** "Stability analysis using control theory" (Jan 26 19:00)
- Source: Gemini analysis
- Result: Lyapunov function, R_auto² > threshold
- Math: Derived stability condition

**D3:** "Compare our model to Google SRE, Friston" (Jan 26 19:15)
- Source: Internal synthesis
- Result: Aligns with both frameworks
- Validation: Theory sound

**D4:** "Synthesize complete Communication Fabric theory" (Jan 26 19:30)
- Source: Gemini synthesis
- Result: COMMUNICATION_FABRIC_RESEARCH_SYNTHESIS.md
- Output: Complete theory document

**D5:** "Implement Communication Fabric" (Jan 26 19:45)
- Source: Code implementation
- Result: fabric.py (400+ lines)
- Validation: Live metrics match theory

**Depth progression: D0 → D1 → D2 → D3 → D4 → D5 in 2 hours**

---

## IMPLEMENTATION PLAN

### Component 1: Add Depth Metadata to Existing Files (2 hours)

**Scan all 1,068 files, add metadata:**
```python
# For each research file
metadata = {
    "query_id": generate_id(timestamp, source),
    "depth_level": infer_depth(filename, content),
    "parent_query_id": extract_parent(content),
    "topic": classify_topic(content),
    "citations": count_citations(content)
}

# Write sidecar file
# gemini/sessions/20260127_060333.json
# gemini/sessions/20260127_060333.meta.yaml  ← NEW
```

---

### Component 2: Build Depth Index (1 hour)

**Create `research/depth_index.yaml`:**
- Scan all metadata files
- Build topic → query chains
- Calculate depth distribution
- Link parents → children

---

### Component 3: Reorganize by Depth (Optional - 3 hours)

**Move files into depth directories:**
```bash
# Move D0 queries
mv gemini/sessions/D0_*.json gemini/D0_surface/sessions/

# Move D1 queries
mv gemini/sessions/D1_*.json gemini/D1_validation/sessions/

# etc.
```

**Or:** Keep flat, use metadata for virtual organization

---

### Component 4: Depth-Aware Auto-Save (1 hour)

**Modify analyze.py:**
```python
def auto_save_with_depth(query, response, parent_query_id=None):
    # Infer depth
    if parent_query_id:
        parent_depth = load_metadata(parent_query_id)["depth_level"]
        depth = parent_depth + 1
    else:
        depth = 0  # New topic

    # Save with depth prefix
    filename = f"D{depth}_{timestamp}_{slug}.json"

    # Write metadata
    metadata = {
        "depth_level": depth,
        "parent_query_id": parent_query_id,
        ...
    }
```

---

## VISUALIZATION

### Depth Tree View:
```
Communication Theory (23 queries)
├─ D0: "What is Communication Theory?" (Jan 26 18:00)
│  └─ D1: "Validate for software" (Jan 26 18:30)
│     ├─ D2: "Stability analysis" (Jan 26 19:00)
│     │  └─ D3: "Compare to FEP" (Jan 26 19:15)
│     │     └─ D4: "Synthesize theory" (Jan 26 19:30)
│     │        └─ D5: "Implement fabric.py" (Jan 26 19:45)
│     │
│     └─ D2: "Metric definitions" (Jan 26 18:45)
│        └─ D3: "F/MI/N/SNR formulas" (Jan 26 19:00)
│
└─ D1: "Internal metrics analysis" (Jan 26 19:00)
   └─ D2: "Live metric computation" (Jan 26 19:20)
```

---

## DASHBOARD INTEGRATION

### Research Depth View (New Tab):
```
┌─────────────────────────────────────────────────────────────┐
│ RESEARCH ARCHIVE - DEPTH VIEW                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Total Queries: 1,068                                        │
│                                                             │
│ By Depth:                                                   │
│   D0 (Surface):        245 queries  ████████░░  23%        │
│   D1 (Validation):     312 queries  ███████████  29%       │
│   D2 (Deep):           287 queries  ██████████  27%        │
│   D3 (Cross-Val):      156 queries  █████░░░░░  15%        │
│   D4 (Synthesis):       52 queries  ██░░░░░░░░   5%        │
│   D5 (Implementation):  16 queries  █░░░░░░░░░   1%        │
│                                                             │
│ Active Topics:                                              │
│  • Communication Fabric (23 queries, max depth: D5)        │
│  • Butler Integration (8 queries, max depth: D3)           │
│  • Cloud Refinery (15 queries, max depth: D2)              │
│                                                             │
│ [Browse by Topic] [Browse by Depth] [View Tree]            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API ENDPOINTS FOR RESEARCH DEPTH

### GET /api/research/topics
**Purpose:** List research topics with depth stats

**Response:**
```json
{
  "topics": [
    {
      "name": "communication_fabric",
      "query_count": 23,
      "max_depth": 5,
      "depth_distribution": {
        "D0": 1, "D1": 3, "D2": 8, "D3": 6, "D4": 4, "D5": 1
      },
      "root_query_id": "gemini_20260126_181710",
      "synthesis_query_id": "gemini_20260126_200000",
      "implementation_files": ["fabric.py", "fabric_bridge.py"],
      "status": "COMPLETE"
    }
  ]
}
```

---

### GET /api/research/topics/{topic}/tree
**Purpose:** Get research progression tree for topic

**Response:**
```json
{
  "topic": "communication_fabric",
  "tree": {
    "query_id": "gemini_20260126_181710",
    "depth": 0,
    "query": "What is Communication Theory?",
    "timestamp": "2026-01-26T18:17:10",
    "outcome": "Shannon model identified",
    "children": [
      {
        "query_id": "perplexity_20260126_181437",
        "depth": 1,
        "query": "Validate Shannon for software",
        "outcome": "Confirmed applicable",
        "children": [
          {
            "query_id": "gemini_20260126_190000",
            "depth": 2,
            "query": "Stability analysis",
            "children": [...]
          }
        ]
      }
    ]
  }
}
```

---

### GET /api/research/depth/{level}
**Purpose:** Browse all queries at specific depth

**Example:** `/api/research/depth/D2`

**Response:**
```json
{
  "depth_level": 2,
  "query_count": 287,
  "queries": [
    {
      "query_id": "gemini_20260126_190000",
      "topic": "communication_fabric",
      "query": "Stability analysis using control theory",
      "parent": "perplexity_20260126_181437",
      "children": ["gemini_20260126_191500"],
      "timestamp": "2026-01-26T19:00:00",
      "citations": 25
    }
    // ... 286 more
  ]
}
```

---

## RESEARCH QUERY WORKFLOW (NEW)

### When You Ask a Question:

**Step 1: Check Context**
```python
# Is this a new topic or follow-up?
topic = classify_topic(query)
parent = find_recent_query_on_topic(topic)

if parent:
    depth = parent.depth_level + 1
else:
    depth = 0  # New topic
```

**Step 2: Execute Query**
```python
response = gemini_or_perplexity(query)
```

**Step 3: Auto-Save with Depth**
```python
save_research({
    "query_id": generate_id(),
    "depth_level": depth,
    "parent_query_id": parent.id if parent else None,
    "topic": topic,
    ...
})
```

**Step 4: Update Index**
```python
update_depth_index(query_id, topic, depth)
```

---

## DEPTH INFERENCE (For Existing Files)

**Analyze content to infer depth:**

### D0 Indicators:
- Query starts with: "What is", "Explain", "Overview of"
- No references to prior queries
- Broad scope keywords

### D1 Indicators:
- Query contains: "Validate", "Verify", "Confirm"
- References external sources
- Cites D0 findings

### D2 Indicators:
- Query contains: "Deep dive", "Analyze", "How does X work"
- Mathematical formulas
- Narrow focus

### D3 Indicators:
- Query contains: "Compare", "Cross-validate", "Alternatives"
- Multiple frameworks mentioned
- Trade-off analysis

### D4 Indicators:
- Query contains: "Synthesize", "Integrate", "Combine"
- References multiple prior queries
- Creates new artifact (synthesis doc)

### D5 Indicators:
- Creates code (`fabric.py`, `butler_protocol.py`)
- Implements theory from D4
- Validation metrics

---

## EXAMPLE: COMMUNICATION FABRIC DEPTH CHAIN

```
D0: perplexity_20260126_181437
    "Research academic foundations for Communication Theory"
    → Result: Shannon, control theory, cascading failures
    → Citations: 60+
    ↓
D1: gemini_20260126_181710
    "Analyze Communication Theory through fabric lens"
    → Result: F, MI, N, SNR metrics defined
    → Parent: D0
    ↓
D2: gemini_20260126_190000
    "Control theory stability analysis"
    → Result: Lyapunov function, R_auto² > threshold
    → Parent: D1
    ↓
D3: internal_20260126_193000
    "Compare to Friston's Free Energy Principle"
    → Result: Our model aligns with FEP
    → Parent: D2
    ↓
D4: internal_20260126_195000
    "Synthesize Communication Fabric theory"
    → Result: COMMUNICATION_FABRIC_RESEARCH_SYNTHESIS.md
    → Parents: [D0, D1, D2, D3]
    ↓
D5: implementation_20260126_200000
    "Build fabric.py"
    → Result: 400+ lines, live metrics
    → Parent: D4
    → Validation: Stability margin = +0.70 (theory predicted stable)
```

**This is RECURSIVE RESEARCH - each layer builds on previous.**

---

## BENEFITS

### 1. See Research Progression
```bash
./pe research depth-tree communication_fabric
→ Shows: D0 → D1 → D2 → D3 → D4 → D5
→ Visualizes: How we got from question to working code
```

### 2. Resume at Any Depth
```bash
./pe research continue communication_fabric
→ Finds: Latest query (D5)
→ Suggests: "Topic complete. Start new topic or go deeper?"
```

### 3. Identify Shallow Topics
```bash
./pe research audit
→ Shows: Topics stuck at D0 or D1 (never validated)
→ Action: "These need deeper research"
```

### 4. Trace Implementation to Theory
```bash
# For any code file
./pe research trace fabric.py
→ Shows: D5 → D4 → D3 → D2 → D1 → D0
→ Complete lineage from implementation back to first question
```

---

## IMPLEMENTATION PRIORITY

### Phase 1: Metadata Generation (2 hours)
- Scan 1,068 existing files
- Infer depth levels
- Extract parent relationships
- Build depth_index.yaml

### Phase 2: Depth-Aware Auto-Save (1 hour)
- Modify analyze.py to track depth
- Add parent_query_id parameter
- Auto-increment depth on follow-ups

### Phase 3: API Endpoints (2 hours)
- `/api/research/topics` - Topic list with depth stats
- `/api/research/topics/{topic}/tree` - Depth progression
- `/api/research/depth/{level}` - Browse by depth

### Phase 4: Dashboard UI (2 hours)
- Research tab with depth visualization
- Tree view of query progression
- Depth distribution charts

**Total: 7 hours for complete depth system**

---

## CURRENT STATE

**Auto-Save:** ✅ WORKING (1,068 files saved)
**Depth Tracking:** ❌ NOT IMPLEMENTED (all files flat)
**Depth Inference:** ❌ NOT IMPLEMENTED (can't tell depth from filename)
**Depth Metadata:** ❌ NOT IMPLEMENTED (no depth_index.yaml)

**Gap:** Research is saved but NOT organized by depth

---

## RECOMMENDATION

**Build depth system in 2 phases:**

**Phase 1 (4 hours):** Metadata + Index
- Infer depth for existing 1,068 files
- Build depth_index.yaml
- Add depth to auto-save

**Phase 2 (3 hours):** Visualization
- API endpoints for depth queries
- Dashboard Research tab
- Tree view UI

**Result:** See research progression D0 → D5, trace any code back to its theoretical roots

---

**SHALL I BUILD THE RESEARCH DEPTH SYSTEM?**

This would make the research archive navigable by depth, showing how each topic evolves from surface questions to working implementations.

7 hours to transform flat archive into layered knowledge depth system.
