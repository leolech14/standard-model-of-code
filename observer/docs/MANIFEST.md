# Control Room - Source Manifest

> **Purpose:** Document both source codebases before merge
> **Created:** 2026-02-01
> **Status:** MAPPING PHASE

---

## Workspace Structure

```
observer/
├── source-a/          # Refinery Dashboard (React/TypeScript)
├── source-b/          # File Explorer (Python)
├── docs/              # Documentation
│   ├── MANIFEST.md    # This file
│   └── ANALYSIS/      # Cerebras analysis outputs
├── analysis/          # Raw analysis data
└── merged/            # Future: merged codebase
```

---

## Source A: Refinery Dashboard

**Origin:** `refinery-dashboard.zip`
**Stack:** React 18 + TypeScript + Vite
**Size:** ~254KB compressed

### Files

| File | Size | Purpose |
|------|------|---------|
| `App.tsx` | 68KB | Main application, navigation, state |
| `types.ts` | 2KB | TypeScript interfaces |
| `index.tsx` | 0.5KB | Entry point |
| `index.html` | 2KB | HTML shell |
| `package.json` | 0.5KB | Dependencies |
| `vite.config.ts` | 0.5KB | Build config |
| `tsconfig.json` | 0.5KB | TS config |

### Components

| Component | Size | Purpose |
|-----------|------|---------|
| `PipelineInspector.tsx` | 21KB | Pipeline stage visualization |
| `Inventory.tsx` | 25KB | Artifact grid display |
| `Inspectors.tsx` | 17KB | Artifact/Run/Alert inspectors |
| `InfrastructureInspector.tsx` | 14KB | Buffer/Cluster/Network |
| `FileSystem.tsx` | 33KB | File tree explorer |
| `StorageAnalysis.tsx` | 7KB | Storage metrics |
| `Timeline.tsx` | 11KB | Run history timeline |
| `PipelineMetrics.tsx` | 10KB | Pipeline performance |
| `FloatingPanel.tsx` | 7KB | Overlay panel system |
| `Common.tsx` | 15KB | Shared UI components |

### Services

| Service | Purpose |
|---------|---------|
| `mockData.ts` | Mock data for development |

---

## Source B: File Explorer

**Origin:** `tools/file_explorer.py`
**Stack:** Python 3 + HTTP Server + Embedded HTML/JS
**Size:** ~307KB

### Key Sections (to be mapped by Cerebras)

| Section | Lines | Purpose |
|---------|-------|---------|
| Configuration | 1-80 | Constants, language maps |
| Authentication | 108-168 | Touch ID / biometric auth |
| Path Validation | 82-106 | Security sandboxing |
| File Operations | TBD | CRUD operations |
| HTTP Handler | TBD | Request routing |
| HTML Template | TBD | Embedded frontend |

### Security Features

- Touch ID / Face ID via Swift LocalAuthentication
- Secure token-based session auth
- Path validation (sandbox enforcement)
- Trash/undo system

---

## Analysis Plan

### Phase 1: Deep Mapping (Cerebras)

1. **Map Source A Components**
   - Inputs/outputs for each component
   - State management patterns
   - Event handlers
   - Props interfaces

2. **Map Source B Sections**
   - Extract security module
   - Extract file operations
   - Extract preview system
   - Map HTTP endpoints

### Phase 2: Compatibility Matrix

- Which Source A components can use Source B security?
- Which Source B features need React wrappers?
- Shared data structures?

### Phase 3: Refactor Registry

- Create task-by-task refactor plan
- Each task: input files, output files, test criteria
- Confidence score per task

---

## Questions for Cerebras

### Source A Questions
1. What are ALL the TypeScript interfaces in types.ts?
2. What state does App.tsx manage?
3. What props does each component accept?
4. What events does each component emit?
5. What external APIs are called?

### Source B Questions
1. What HTTP endpoints exist?
2. What is the complete authentication flow?
3. What file operations are supported?
4. What preview types are handled?
5. What is the HTML template structure?

---

---

## Analysis Complete (2026-02-01)

### Cerebras Deep Mapping Results

| Analysis | File | Key Findings |
|----------|------|--------------|
| Source A Types | `analysis/source_a_cerebras.json` | 8 interfaces, 3 enums, 19 state vars |
| Source A Components | `analysis/source_a_cerebras.json` | 10 components mapped |
| Source B Security | `analysis/source_b_cerebras.json` | Touch ID, token auth, path validation |
| Source B API | `analysis/source_b_cerebras.json` | 23 HTTP endpoints |
| Source B Preview | `analysis/source_b_cerebras.json` | 60+ languages, images, video, PDF |
| Compatibility | `analysis/compatibility_and_tasks.json` | 3 direct reuse, 3 conflicts, 4 glue needed |

### Generated Documentation

| Document | Purpose |
|----------|---------|
| `MANIFEST.md` | This file - project overview |
| `COMPATIBILITY_MATRIX.md` | What can be reused, what conflicts |
| `REFACTOR_REGISTRY.yaml` | 8 tasks, 89 hours, 5 phases |

### Confidence Scores

```
Phase 1 (Foundation):  90% avg
Phase 2 (Security):    70%     ← HIGH RISK
Phase 3 (Backend):     77% avg
Phase 4 (Frontend):    85%
Phase 5 (Integration): 75% avg

Overall: 79%
```

### Next Steps

1. **Gemini Validation** - Cross-validate Cerebras findings
2. **Phase 1 Execution** - Start with CR-001 (Project Setup)
3. **Incremental Progress** - One task at a time, update confidence

---

*Analysis complete. Ready for implementation.*
