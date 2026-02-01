# Control Room - Compatibility Matrix

> **Generated:** 2026-02-01
> **Source:** Cerebras llama-3.3-70b analysis
> **Status:** REFERENCE DOCUMENT

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Direct Reuse | 3 features | Ready |
| Needs Wrapper | 3 features | Planned |
| Conflicts | 3 issues | Must Resolve |
| New Glue Code | 4 components | Must Build |

---

## 1. DIRECT REUSE (Can use as-is)

| Source B Feature | Source A Component | Notes |
|------------------|-------------------|-------|
| API Endpoints (`/api/list`, `/api/folder-preview`) | FileSystem, Inventory | Just need auth header |
| Token Generation | AppSettings | Move to shared utility |
| Biometric Auth (Touch ID) | App.tsx (SecureGate) | Swift code works on macOS |

---

## 2. NEEDS WRAPPER

| Source B Function | Source A Component | Wrapper Type |
|-------------------|-------------------|--------------|
| File Operations (`create-folder`, `rename`, `duplicate`) | FileSystem, Inventory | React hooks → Python API |
| Authentication Mechanism | App.tsx | React context → Python session |
| Upload/Paste/Delete APIs | Inspectors, Inventory | React mutations → Python endpoints |

---

## 3. CONFLICTS (Must Resolve)

| Type | Source B | Source A | Resolution |
|------|----------|----------|------------|
| **Naming** | `File` object | `Artifact` interface | Map `Artifact.path` ↔ `File.path` |
| **State** | Session token (server) | AppState (client) | Hybrid: token in httpOnly cookie + AppState |
| **Data Format** | Python dict JSON | TypeScript interfaces | Shared JSON schema, Zod validation |

---

## 4. NEW GLUE CODE NEEDED

| Component | Purpose | Estimated Hours |
|-----------|---------|-----------------|
| **WebSocket Adapter** | Real-time file changes, observer status | 10h |
| **Auth Bridge** | Touch ID → session token → React context | 12h |
| **Data Transform Layer** | Python dict ↔ TypeScript interfaces | 6h |
| **API Gateway** | Unified endpoint routing, CORS | 4h |

---

## Component Mapping

### Source A → Control Room

| Source A Component | Control Room Location | Changes Needed |
|--------------------|----------------------|----------------|
| `App.tsx` | `src/App.tsx` | Add SecureGate, WebSocket |
| `PipelineInspector.tsx` | `src/components/` | No changes |
| `FileSystem.tsx` | `src/components/` | Replace mock with Python API |
| `Inventory.tsx` | `src/components/` | Add file operations |
| `Timeline.tsx` | `src/components/` | No changes |
| `Common.tsx` | `src/components/ui/` | Split into smaller files |
| `types.ts` | `src/types/` | Add File, Auth types |

### Source B → Control Room

| Source B Section | Control Room Location | Changes Needed |
|------------------|----------------------|----------------|
| Auth (lines 108-168) | `backend/auth.py` | Extract, add FastAPI wrapper |
| API endpoints | `backend/routes/` | Split by domain |
| Path validation | `backend/security.py` | Extract as middleware |
| Preview generation | `backend/preview.py` | Add WebSocket streaming |
| HTML template | REMOVE | React replaces this |

---

## Data Type Mapping

### Artifact (Source A) ↔ File (Source B)

```typescript
// Source A: Artifact
interface Artifact {
  id: string;
  name: string;
  projectId: string;
  pipelineId: PipelineId;
  stage: CanonicalStage;
  type: string;
  size: string;
  updatedAt: number;
  status: 'live' | 'archived' | 'failed';
}

// Source B: File (implicit)
// {
//   name: str,
//   path: str,
//   size: int,
//   modified: float,
//   is_dir: bool,
//   preview_type: str
// }

// Control Room: Unified
interface UnifiedFile {
  id: string;           // hash of path
  name: string;
  path: string;         // from Source B
  projectId?: string;   // from Source A context
  type: string;         // preview_type or artifact type
  size: number;         // bytes
  updatedAt: number;    // epoch ms
  isDirectory: boolean; // from Source B
  status?: ArtifactStatus; // if tracked by pipeline
}
```

---

## Security Model

```
┌─────────────────────────────────────────────────────────┐
│  BROWSER                                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  React App                                       │   │
│  │  - Auth context (token in memory)               │   │
│  │  - SecureGate (blocks until authenticated)      │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼ (httpOnly cookie + token)    │
├─────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI)                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  /auth/biometric → Touch ID → session token     │   │
│  │  /auth/verify → validate session                │   │
│  │  /api/* → requires valid session               │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼ (path validation)            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  File System (sandboxed to BROWSE_ROOT)         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Touch ID fails on non-macOS | HIGH | Fallback to password auth |
| WebSocket disconnects | MEDIUM | Reconnect logic + optimistic UI |
| Large file preview hangs | MEDIUM | Streaming + size limits |
| Session token leak | HIGH | httpOnly cookies, short expiry |

---

*This matrix guides the refactor. Update as implementation progresses.*
