# Refinery Platform Architecture

**Level:** L7 System (evolving to L8 Ecosystem)
**Type:** Multi-tenant context processing platform
**Status:** Spinoff from PROJECT_elements

---

## The Core Insight

**Refinery processes CONTEXT for code projects.**

Like Elasticsearch processes search, or Neo4j processes graphs:
- **Refinery processes CONTEXT**
- Any project can use it
- Platform-level infrastructure

---

## Multi-Tenant Architecture

### Project Isolation

```
Each project = separate tenant:

refinery-data/
├── elements/
│   ├── chunks.json       (2,673 chunks, 539K tokens)
│   ├── metadata.json     (last processed, health)
│   └── index/            (search indexes)
│
├── atman/
│   ├── chunks.json
│   ├── metadata.json
│   └── index/
│
└── sentinel/
    ├── chunks.json
    ├── metadata.json
    └── index/
```

**Or Cloud Storage:**
```
gs://refinery-context/
├── tenants/
│   ├── elements/...
│   ├── atman/...
│   └── sentinel/...
```

---

## API Design (L7 Boundary)

### Core APIs

```typescript
// Projects (Tenant Management)
GET    /api/v1/projects                    List all tenants
POST   /api/v1/projects                    Register new project
GET    /api/v1/projects/:id                Project metadata
DELETE /api/v1/projects/:id                Remove project

// Context Processing
POST   /api/v1/projects/:id/process        Trigger processing
GET    /api/v1/projects/:id/status         Processing status
GET    /api/v1/projects/:id/health         Health metrics

// Chunks (The Core Product)
GET    /api/v1/projects/:id/chunks         List chunks (paginated)
GET    /api/v1/projects/:id/chunks/:chunk  Single chunk
POST   /api/v1/chunks/search               Search across projects
POST   /api/v1/chunks/semantic-search      Semantic/embedding search

// Analytics
GET    /api/v1/metrics                     Platform-wide metrics
GET    /api/v1/projects/:id/metrics        Project-specific metrics
GET    /api/v1/activity                    Recent activity

// Graph (Integration with Neo4j/GraphRAG when available)
GET    /api/v1/projects/:id/graph          GraphRAG access
POST   /api/v1/projects/:id/graph/query    Semantic queries
```

**Versioned (`/v1/`)** - because platform APIs need stability (78% validated)

---

## Data Model

### Core Entities

```typescript
// Project (Tenant)
interface Project {
  id: string;                    // "elements", "atman", etc.
  name: string;                  // Display name
  path: string;                  // Local path or git URL
  status: 'active' | 'archived';
  created_at: string;
  last_processed: string;
  health: {
    chunk_count: number;
    token_count: number;
    coverage: number;            // 0.0-1.0
    freshness: number;           // hours since last update
  };
}

// Chunk (Universal Format)
interface Chunk {
  chunk_id: string;              // Unique across platform
  project_id: string;            // Which tenant
  file: string;                  // Relative path
  content: string;               // The text
  tokens: number;                // Token count
  semantic_hash: string;         // For dedup
  embedding?: number[];          // Vector (if computed)
  metadata: {
    created: string;
    updated: string;
    category: string;            // "code", "docs", "config"
    language?: string;           // Programming language
  };
}

// SearchResult
interface SearchResult {
  chunk: Chunk;
  score: number;                 // Relevance 0.0-1.0
  highlights: string[];          // Matched snippets
  project: Project;              // Parent project
}

// PlatformMetrics
interface PlatformMetrics {
  total_projects: number;
  total_chunks: number;
  total_tokens: number;
  active_tenants: number;
  storage_used: string;          // "1.2 GB"
  last_24h: {
    queries: number;
    processing_jobs: number;
    errors: number;
  };
}
```

---

## Component Structure (L7 → L6 → L5)

### Backend (API Routes)

```
app/api/v1/
├── projects/
│   ├── route.ts               // L6: Project management
│   ├── [id]/
│   │   ├── route.ts           // L5: Single project
│   │   ├── chunks/route.ts    // L5: Chunks for project
│   │   ├── process/route.ts   // L5: Trigger processing
│   │   └── health/route.ts    // L5: Health metrics
├── chunks/
│   ├── search/route.ts        // L6: Cross-project search
│   └── semantic-search/route.ts
├── metrics/
│   └── route.ts               // L6: Platform metrics
└── activity/
    └── route.ts               // L6: Activity log

Compositional alignment: L6 packages compose from L5 routes ✅
```

### Frontend (Views)

```
app/
├── page.tsx                   // Platform overview
├── projects/
│   ├── page.tsx               // All projects
│   └── [id]/
│       ├── page.tsx           // Project dashboard
│       ├── chunks/page.tsx    // Chunk browser
│       └── search/page.tsx    // Project search
├── search/
│   └── page.tsx               // Global search
└── admin/
    ├── metrics/page.tsx       // Platform metrics
    └── tenants/page.tsx       // Tenant management
```

---

## Client SDK (For Elements to Consume)

### TypeScript SDK

```typescript
// @refinery-platform/client

export class RefineryClient {
  constructor(baseUrl: string, apiKey: string) {}

  // Projects
  async listProjects(): Promise<Project[]>
  async getProject(id: string): Promise<Project>
  async createProject(config: ProjectConfig): Promise<Project>

  // Chunks
  async getChunks(projectId: string, page?: number): Promise<Chunk[]>
  async searchChunks(query: string, projectId?: string): Promise<SearchResult[]>
  async semanticSearch(query: string, projectId?: string): Promise<SearchResult[]>

  // Metrics
  async getMetrics(): Promise<PlatformMetrics>
  async getProjectHealth(projectId: string): Promise<HealthMetrics>
}

// Usage in Elements:
import { RefineryClient } from '@refinery-platform/client';

const refinery = new RefineryClient('https://refinery.elements.cloud', API_KEY);
const chunks = await refinery.searchChunks('authentication logic', 'elements');
```

### Python SDK

```python
# refinery-client-py

from refinery_client import RefineryClient

client = RefineryClient(
    base_url='https://refinery.elements.cloud',
    api_key=os.getenv('REFINERY_API_KEY')
)

# Search across projects
results = client.search_chunks(
    query='authentication logic',
    project_id='elements'
)
```

---

## Deployment Architecture

### Local Development

```
localhost:3001
- Reads local project data
- Single tenant (Elements)
- Fast iteration
```

### Cloud Production

```
Cloud Run: refinery-platform
- Multi-tenant
- Auto-scaling
- Connects to:
  ├─ Cloud Storage (chunk data)
  ├─ Neo4j (GraphRAG - when ready)
  └─ Vertex AI (embeddings)
```

---

## Migration Path (L6 → L7 → L8)

### Current (L6 Package)
```
elements/context-management/tools/refinery/
- Python scripts
- Local processing
- Single project
```

### Phase 1 (L7 System)
```
refinery-platform/ (Next.js)
- Multi-tenant web app
- REST API
- Cloud deployment
- Elements = first tenant
```

### Phase 2 (L8 Platform)
```
Separate repo: github.com/refinery-platform/refinery
- Open source or SaaS
- SDKs for multiple languages
- Enterprise features
- Elements = reference implementation
```

---

## Next Steps (Right Now)

### 1. Install Dependencies (2min)
```bash
cd refinery-platform
npm install next react react-dom
npm install -D typescript @types/react @types/node
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react framer-motion
```

### 2. Create Basic Structure (10min)
```
app/
├── layout.tsx
├── page.tsx
└── api/v1/projects/route.ts

components/
└── shared/

lib/
└── refinery-client.ts
```

### 3. First API Route (15min)
```typescript
// GET /api/v1/projects
// Returns: [{ id: 'elements', name: 'PROJECT_elements', ... }]
```

### 4. First View (15min)
```tsx
// app/page.tsx
// Shows: Platform overview, project list
```

**Total: ~45min to working MVP**

---

**Ready to execute these steps?**