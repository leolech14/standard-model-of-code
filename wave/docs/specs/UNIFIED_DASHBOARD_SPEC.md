# Unified Dashboard Specification - Collider + Refinery Parallel View

**Date:** 2026-01-28
**Status:** SPECIFICATION (Pre-Implementation)
**Approach:** Build from scratch applying compositional alignment principles
**Purpose:** Single interface showing both Collider (code graph) and Refinery (knowledge) simultaneously

---

## Executive Summary

**Vision:** One dashboard with parallel views of:
- **LEFT:** Collider 3D graph visualization (existing)
- **RIGHT:** Refinery data, metrics, knowledge search

**Principle:** Natural configuration applying our validated theories:
- Compositional alignment (95% validated)
- API at L7 boundaries (78% validated)
- Dual navigation spaces (75% validated)

**Tech Stack:** TBD (Next.js vs pure HTML)

**Timeline:** TBD (spec first, estimate after)

---

## Design Principles

### 1. Compositional Alignment [95% Validated]

```
L7 (SYSTEM): Unified Dashboard
  ├─ API Layer (REST endpoints at L7 boundary)
  │
  ├─ L6 (PACKAGE): Collider UI Module
  │   ├─ L5: graph-view.tsx
  │   ├─ L5: controls.tsx
  │   └─ L5: metrics-display.tsx
  │
  └─ L6 (PACKAGE): Refinery UI Module
      ├─ L5: chunk-browser.tsx
      ├─ L5: search-interface.tsx
      └─ L5: activity-log.tsx

Each level properly composes from below ✅
No level skipping ✅
Clear boundaries ✅
```

### 2. Dual Navigation [75% Validated]

**Graph Navigation (Discrete):**
- Click node → see details
- Follow edges → traverse dependencies
- Filter by type → explore structure

**Semantic Navigation (Continuous):**
- Search by concept → find similar code
- Cluster view → see communities
- Similarity ranking → conceptual proximity

**Both available simultaneously** ✅

### 3. API Boundaries [78% Validated]

```
Dashboard Frontend (L7)
    ↓ crosses meaningful boundary
Backend API (L7)
    ↓ internal composition
Data Layer (L6)
    ↓
Collider/Refinery Services (L5-L6)
```

**API characteristics (POINT framework):**
- P: Purposeful (OpenAPI spec)
- O: Oriented (REST/JSON)
- I: Isolated (frontend doesn't know backend internals)
- N: Negotiated (versioned contract)
- T: Versioned (v1 API)

---

## Visual Layout

### Option A: Split View (50/50)

```
┌─────────────────────────────────────────────────────────┐
│ Header: Controls, Status, Settings                      │
├──────────────────────────┬──────────────────────────────┤
│                          │                              │
│   COLLIDER               │   REFINERY                   │
│   (3D Graph)             │   (Data & Metrics)           │
│                          │                              │
│   • WebGL visualization  │   • Chunk browser            │
│   • Node/edge controls   │   • Knowledge search         │
│   • Topology metrics     │   • Activity timeline        │
│   • Filter/zoom          │   • Health metrics           │
│                          │                              │
│   50% width              │   50% width                  │
│                          │                              │
└──────────────────────────┴──────────────────────────────┘
│ Footer: Status bar, notifications                       │
└─────────────────────────────────────────────────────────┘
```

### Option B: Tabbed Interface

```
┌─────────────────────────────────────────────────────────┐
│ [Collider] [Refinery] [Combined] [Settings]            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Currently showing: Collider 3D View                  │
│   (Click tabs to switch)                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Option C: Overlay/Toggle

```
┌─────────────────────────────────────────────────────────┐
│ 3D Graph with Data Overlays                            │
│                                                         │
│ Toggles:                                               │
│ [✓] Show graph                                         │
│ [✓] Show chunk data (overlay on nodes)                │
│ [ ] Show activity timeline                             │
│ [✓] Show health metrics (corner widget)               │
└─────────────────────────────────────────────────────────┘
```

**Recommendation:** Start with **Option A (Split View)** - clearest separation, easiest to implement.

---

## Data Sources & Integration

### Collider Data

**Source Files:**
```
.collider/unified_analysis.json  (graph structure)
.collider/collider_report.html   (visualization - extract logic)
```

**Data Structure:**
```json
{
  "nodes": [
    {
      "id": "scanner.py::scan_files",
      "file_path": "wave/tools/refinery/scanner.py",
      "start_line": 42,
      "atom_type": "FunctionDef",
      "role": "Worker",
      "level": 3,
      "purpose": {...},
      "metrics": {...}
    }
  ],
  "edges": [
    {
      "source": "scanner.py::scan_files",
      "target": "chunker.py::chunk_file",
      "type": "calls",
      "weight": 1.0
    }
  ],
  "metrics": {
    "node_count": 1179,
    "edge_count": 2341,
    "health_score": 0.85
  }
}
```

**API Endpoints Needed:**
```
GET /api/collider/graph       → full graph data
GET /api/collider/node/:id    → node details
GET /api/collider/metrics     → system metrics
POST /api/collider/query      → graph queries
```

---

### Refinery Data

**Source Files:**
```
.agent/intelligence/chunks/agent_chunks.json
.agent/intelligence/chunks/core_chunks.json
.agent/intelligence/chunks/aci_chunks.json
wave/intelligence/state/live.yaml
```

**Data Structure:**
```json
{
  "chunks": [
    {
      "chunk_id": "agent_001",
      "file": ".agent/KERNEL.md",
      "content": "...",
      "tokens": 847,
      "semantic_hash": "abc123",
      "created": "2026-01-27T..."
    }
  ],
  "metrics": {
    "total_chunks": 2673,
    "total_tokens": 539000,
    "coverage": 0.92
  },
  "activity": {
    "last_update": "2026-01-28T...",
    "files_changed": 12,
    "chunks_updated": 45
  }
}
```

**API Endpoints Needed:**
```
GET /api/refinery/chunks          → paginated chunks
GET /api/refinery/search?q=...    → search chunks
GET /api/refinery/metrics         → statistics
GET /api/refinery/activity        → recent changes
GET /api/refinery/health          → F, MI, SNR, etc.
```

---

### Integration Points (Collider ↔ Refinery)

**Cross-linking:**
```
User clicks Collider node "scanner.py::scan_files"
  ↓
Dashboard queries: GET /api/refinery/chunks?file=scanner.py
  ↓
Right panel shows: Chunks from that file
```

**Bi-directional:**
```
User searches Refinery: "file processing"
  ↓
Dashboard queries: POST /api/collider/query {semantic: "file processing"}
  ↓
Left panel highlights: Related nodes in graph
```

---

## Component Architecture

### Frontend Components (L6 Packages)

```typescript
// L6: Collider Module
src/components/collider/
├── GraphView.tsx           // L5: 3D visualization
├── GraphControls.tsx       // L5: Filters, zoom, settings
├── NodeDetails.tsx         // L5: Selected node info
├── MetricsPanel.tsx        // L5: Health, counts, topology
└── index.ts                // L6: Module exports

// L6: Refinery Module
src/components/refinery/
├── ChunkBrowser.tsx        // L5: Paginated chunk list
├── SearchInterface.tsx     // L5: Semantic search
├── ActivityTimeline.tsx    // L5: Recent changes
├── HealthDashboard.tsx     // L5: F, MI, SNR metrics
└── index.ts                // L6: Module exports

// L6: Shared/Layout
src/components/layout/
├── Header.tsx              // L5: Top nav, status
├── SplitView.tsx           // L5: 50/50 layout manager
└── Footer.tsx              // L5: Status bar
```

**Compositional alignment:** Each L6 package composes from L5 components ✅

---

### Backend API (L7 System)

```python
# FastAPI or Next.js API routes?

# Option 1: FastAPI Backend (Python)
api/
├── main.py                 // FastAPI app
├── routers/
│   ├── collider.py         // /api/collider/*
│   └── refinery.py         // /api/refinery/*
├── services/
│   ├── graph_service.py    // Load/query graph
│   └── chunk_service.py    // Load/query chunks
└── models/
    └── schemas.py          // Pydantic models

# Option 2: Next.js API Routes (TypeScript)
app/api/
├── collider/
│   ├── graph/route.ts
│   ├── node/[id]/route.ts
│   └── metrics/route.ts
└── refinery/
    ├── chunks/route.ts
    ├── search/route.ts
    └── health/route.ts
```

**Decision needed:** Python (FastAPI) or TypeScript (Next.js)?

---

## Tech Stack Decision

### Option 1: Pure HTML + Vanilla JS

**Pros:**
- ✅ Collider viz already uses this
- ✅ No build step
- ✅ Simple deployment
- ✅ Fast loading

**Cons:**
- ❌ Harder to maintain complex UI
- ❌ No component reusability
- ❌ Manual state management

---

### Option 2: Next.js + TypeScript

**Pros:**
- ✅ Modern, maintainable
- ✅ Component architecture
- ✅ Great DX (developer experience)
- ✅ API routes built-in

**Cons:**
- ❌ Build step required
- ❌ More complex deployment
- ❌ Larger bundle size

---

### Option 3: React (no Next.js)

**Pros:**
- ✅ Component reusability
- ✅ Simpler than Next.js
- ✅ Can embed in static HTML

**Cons:**
- ❌ Still needs build step
- ❌ No built-in routing
- ❌ Need separate backend

---

## 🎯 **DECISION NEEDED:**

**Before I continue spec'ing, which tech stack?**

1. **Pure HTML + JS** (like current Collider viz)
2. **Next.js** (like experimental dashboard)
3. **React** (middle ground)
4. **Something else?**

**Also: Backend preference?**
- **FastAPI** (Python - matches existing)
- **Next.js API routes** (if using Next.js frontend)
- **No backend** (pure static, read JSON files directly)

**What's your preference?**
## DECISIONS MADE ✅

**Q1: Tech Stack** → Next.js 15 + TypeScript
**Q2: Layout** → Reference design patterns from cloud-refinery-console
**Q3: Backend** → Next.js API routes (TypeScript)

**Reference Design:**
- Location: `experiments/refinery-dashboard/reference_design/`
- Stack: Vite + React (migrate to Next.js)
- Has: UI patterns, components, data models
- Missing: Real backend (uses mock data)

**Our Task:**
1. Create new Next.js app
2. Port reference UI patterns
3. Add real API routes (Collider + Refinery data)
4. Integrate Collider 3D visualization
5. Deploy

---

## Implementation Kickoff

**Status:** READY TO BUILD
**Timeline:** 9-12 hours estimated
**Next:** Create Next.js project and start porting
