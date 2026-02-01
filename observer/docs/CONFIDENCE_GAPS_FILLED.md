# Control Room - Confidence Gaps Filled

> **Date:** 2026-02-01
> **Source:** Cerebras llama-3.3-70b
> **Status:** GAPS RESOLVED

---

## Gap 1: Auth Bridge (CR-003)

**Previous Confidence:** 70%
**New Confidence:** 85%

### FastAPI Endpoints
```yaml
endpoints:
  - POST /auth/biometric  # Trigger Touch ID
  - GET /auth/verify      # Validate session
  - POST /auth/logout     # Clear session
```

### Session Token Storage
- **Recommended:** httpOnly cookie (XSS-resistant)
- **Alternative:** localStorage (for SPA compatibility)

### React AuthContext Shape
```typescript
interface AuthContext {
  isAuthenticated: boolean;
  token: string | null;
  error: string | null;
  login: () => Promise<void>;
  logout: () => void;
}
```

### SecureGate Component Pattern
```tsx
const SecureGate: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <LoginPrompt />;
  return <>{children}</>;
};
```

### Failure Modes & Fallbacks
| Scenario | Fallback |
|----------|----------|
| Non-macOS | Display message, offer password auth |
| Biometric error | Retry prompt, password fallback |
| Token invalid | Redirect to login |

---

## Gap 2: Testing Strategy (CR-008)

**Previous Confidence:** 70%
**New Confidence:** 85%

### Backend Tests (Pytest)
```
tests/
├── test_main.py           # App startup
├── test_routes.py         # Route registration
├── test_auth.py           # Authentication
├── test_validation.py     # Path validation
├── test_preview.py        # Preview system
└── endpoints/
    ├── test_files.py
    ├── test_operations.py
    ├── test_history.py
    └── test_search.py
```

### Frontend Tests (Vitest)
```
src/__tests__/
├── components/
│   ├── PipelineInspector.test.tsx
│   ├── Inventory.test.tsx
│   ├── FileSystem.test.tsx
│   └── Timeline.test.tsx
├── hooks/
│   ├── useAuth.test.ts
│   ├── useFiles.test.ts
│   └── usePreview.test.ts
└── App.test.tsx
```

### E2E Tests (Playwright)
```
e2e/
├── auth.spec.ts           # Login flow, Touch ID
├── file-operations.spec.ts # Upload, delete, rename
├── navigation.spec.ts     # View switching
└── pipeline.spec.ts       # Pipeline inspection
```

### Coverage Target: 80%

### Critical Paths
1. User authentication and authorization
2. Pipeline Inspector data visualization
3. Inventory management and updates
4. File System navigation and access
5. Touch ID authentication flow

---

## Gap 3: API Endpoints (CR-005)

**Previous Confidence:** 75%
**New Confidence:** 88%

### Router Organization
```python
# 4 routers for 23 endpoints

files_router = APIRouter(prefix="/api", tags=["files"])
# GET /api/list, /api/folder-preview, /api/preview
# GET /api/content, /api/open, /api/metadata

operations_router = APIRouter(prefix="/api", tags=["operations"])
# POST /api/upload, /api/paste, /api/delete
# POST /api/create-folder, /api/rename, /api/duplicate
# POST /api/compress, /api/extract, /api/trash, /api/restore

history_router = APIRouter(prefix="/api", tags=["history"])
# POST /api/undo, /api/redo

search_router = APIRouter(prefix="/api", tags=["search"])
# GET /api/search, /api/recent
```

### Pydantic Models
```python
class FileItem(BaseModel):
    path: str
    name: str
    size: int
    type: str
    modified: datetime

class PasteRequest(BaseModel):
    files: list[str]
    destination: str
    operation: Literal["copy", "move"] = "copy"

class CreateFolderRequest(BaseModel):
    path: str
    name: str

class RenameRequest(BaseModel):
    path: str
    new_name: str
```

### Auth Requirements
- **Protected:** 21/23 endpoints require auth middleware
- **Public:** GET /, GET /index.html (HTML shell only)

### Path Validation Middleware
```python
async def validate_path(path: str) -> str:
    """Ensure path is within sandbox, no traversal."""
    resolved = Path(path).resolve()
    if not resolved.is_relative_to(SANDBOX_ROOT):
        raise HTTPException(403, "Access denied")
    return str(resolved)
```

---

## Updated Confidence Scores

| Task | Before | After | Delta |
|------|--------|-------|-------|
| CR-001 | 90% | 90% | - |
| CR-002 | 80% | 80% | - |
| CR-003 | 70% | 85% | +15% |
| CR-004 | 80% | 80% | - |
| CR-005 | 75% | 88% | +13% |
| CR-006 | 85% | 85% | - |
| CR-007 | 80% | 80% | - |
| CR-008 | 70% | 85% | +15% |

**Average:** 79% → **84%** (+5%)

---

## Ready to Proceed

All gaps filled. Confidence scores raised from 79% to 84% average.
Lowest remaining confidence: CR-002 (80%), CR-004 (80%), CR-007 (80%)

---

## Gap 4: Shared Types (CR-002) - Round 2

**Previous Confidence:** 80%
**New Confidence:** 92%

### UnifiedFile Type (bridges Artifact + File)
```typescript
// TypeScript
interface UnifiedFile extends Artifact {
  path: string;
  modified: Date;
}

// Pydantic
class UnifiedFileModel(ArtifactModel, FileModel):
    pass
```

### Enum Mapping Pattern
```python
# Python enums inherit from str for JSON serialization
class CanonicalStage(str, Enum):
    Capture = 'Capture'
    Separate = 'Separate'
    Clean = 'Clean'
    Enrich = 'Enrich'
    Mix = 'Mix'
    Distill = 'Distill'
    Publish = 'Publish'
```

### Zod Runtime Validation
```typescript
const ArtifactSchema = z.object({
  id: z.string(),
  name: z.string(),
  pipelineId: z.enum(['Refinery', 'Factory']),
  stage: z.enum(['Capture', 'Separate', 'Clean', 'Enrich', 'Mix', 'Distill', 'Publish']),
  truthStatus: z.enum(['VERIFIED', 'SUPPORTED', 'CONFLICTING', 'STALE', 'UNVERIFIED']),
  // ... other fields
});
```

---

## Gap 5: WebSocket Integration (CR-007) - Round 2

**Previous Confidence:** 80%
**New Confidence:** 90%

### Message Schema
```yaml
event_types:
  - file_change: { type, file_path, file_name }
  - observer_status: { status, observer_id }
  - pipeline_progress: { pipeline_id, stage, status }
  - alert_broadcast: { alert_id, message, severity }
```

### FastAPI WebSocket Manager
```python
class WebSocketManager:
    def __init__(self):
        self.connections = {}
        self.rooms = {}

    async def register(self, websocket: WebSocket, room: str):
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)

    async def broadcast(self, room: str, message: dict):
        for conn in self.rooms.get(room, []):
            await conn.send_json(message)
```

### React useWebSocket Hook
```typescript
const useWebSocket = (url: string) => {
  const [messages, setMessages] = useState<WSMessage[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (e) => setMessages(prev => [...prev, JSON.parse(e.data)]);
    ws.onclose = () => reconnect();
    return () => ws.close();
  }, [url]);

  return { messages };
};
```

### Reconnection Strategy
- Exponential backoff: 1s, 2s, 4s, 8s... max 30s
- Heartbeat ping every 10s
- Room-based channels for multi-tenant

---

## Final Updated Confidence Scores

| Task | Before | After Round 1 | After Round 2 | Delta |
|------|--------|---------------|---------------|-------|
| CR-001 | 90% | 90% | 90% | - |
| CR-002 | 80% | 80% | 92% | +12% |
| CR-003 | 70% | 85% | 85% | +15% |
| CR-004 | 80% | 80% | 80% | - |
| CR-005 | 75% | 88% | 88% | +13% |
| CR-006 | 85% | 85% | 85% | - |
| CR-007 | 80% | 80% | 90% | +10% |
| CR-008 | 70% | 85% | 85% | +15% |

**Average:** 79% → 84% → **87%** (+8% total)

---

## Status: READY TO BUILD

All confidence gaps filled. 4 Cerebras rounds completed.
- Lowest confidence: CR-004 (80%) - FastAPI setup (well-documented patterns)
- Highest confidence: CR-002 (92%) - Types fully mapped

Next: Continue CR-001 (Project Setup)
