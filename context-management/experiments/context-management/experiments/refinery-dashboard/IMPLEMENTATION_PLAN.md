# Cloud Context Refinery - Next.js Implementation Plan

**Date:** 2026-01-28
**Target:** Build from scratch using reference design as visual seed
**Stack:** Next.js 15 + TypeScript + Tailwind + Next.js API routes
**Scope:** Multi-project context refinery (not coupled to PROJECT_elements)

---

## Phase 1: Project Setup ✅ IN PROGRESS

```bash
# Creating: context-management/experiments/refinery-web-app/
npx create-next-app@latest refinery-web-app \
  --typescript --tailwind --app --use-npm

# Install dependencies
cd refinery-web-app
npm install lucide-react framer-motion
npm install @types/node --save-dev
```

**Status:** Running in background (task b42bead)

---

## Phase 2: Port Reference UI Components (2-3h)

### Components to Port

**From:** `reference_design/components/`
**To:** `refinery-web-app/components/`

```
1. Common.tsx → shared/
   - UiLink, UiRow, Badge, SectionHeader, EmptyState
   - Pure UI primitives

2. Inspectors.tsx → refinery/
   - ArtifactInspector, RunInspector, AlertInspector
   - Detail views for data

3. Inventory.tsx → refinery/
   - InventoryGrid, StackInspector
   - Chunk browser, file browser

4. PipelineInspector.tsx → refinery/
   - Pipeline stage visualization
   - Status tracking

5. Timeline.tsx → refinery/
   - Activity timeline
   - Run history
```

### Layout Components (New)

```typescript
// components/layout/
├── RootLayout.tsx      // Sidebar + main content wrapper
├── Sidebar.tsx         // Left nav (7 views)
├── SuperSidebar.tsx    // Right expandable panel
└── Header.tsx          // Top bar (status, search, settings)
```

---

## Phase 3: Create Data Models (30min)

### Types for Refinery

```typescript
// types/refinery.ts

export interface Chunk {
  chunk_id: string;
  file: string;
  content: string;
  tokens: number;
  semantic_hash: string;
  created: string;
  project: string;  // NEW: Which project this belongs to
}

export interface Project {
  name: string;
  path: string;
  last_processed: string;
  chunk_count: number;
  total_tokens: number;
  health_score: number;
}

export interface RefineryMetrics {
  total_chunks: number;
  total_tokens: number;
  total_projects: number;
  coverage: number;
  last_update: string;
}

export interface Activity {
  timestamp: string;
  action: string;  // "processed", "indexed", "queried"
  project: string;
  details: Record<string, any>;
}

export interface SearchResult {
  chunk: Chunk;
  score: number;
  highlights: string[];
}
```

---

## Phase 4: Implement API Routes (2-3h)

### File Structure

```
app/api/
├── projects/
│   ├── route.ts              // GET /api/projects (list all)
│   └── [name]/
│       ├── route.ts           // GET /api/projects/:name
│       └── chunks/route.ts    // GET /api/projects/:name/chunks
├── chunks/
│   ├── route.ts              // GET /api/chunks (all, paginated)
│   └── search/route.ts       // POST /api/chunks/search
├── metrics/
│   └── route.ts              // GET /api/metrics
└── activity/
    └── route.ts              // GET /api/activity (timeline)
```

### API Implementation Examples

```typescript
// app/api/projects/route.ts
import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET() {
  // Scan for projects with chunks
  const baseDir = process.env.REFINERY_DATA_DIR || '/data/refinery';

  const projects = await scanProjects(baseDir);

  return NextResponse.json({ projects });
}

async function scanProjects(baseDir: string) {
  // Read directories, find chunk files
  // Return project metadata
}
```

```typescript
// app/api/chunks/search/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { query, project } = await request.json();

  // Load chunks for project
  const chunks = await loadChunks(project);

  // Simple text search (upgrade to semantic later)
  const results = chunks.filter(c =>
    c.content.toLowerCase().includes(query.toLowerCase())
  );

  return NextResponse.json({ results, count: results.length });
}
```

---

## Phase 5: Build Views (3-4h)

### View Structure

```
app/
├── page.tsx                // Overview/Dashboard
├── projects/
│   ├── page.tsx            // Projects list
│   └── [name]/
│       └── page.tsx        // Project detail
├── chunks/
│   └── page.tsx            // Chunk browser
├── search/
│   └── page.tsx            // Search interface
├── pipelines/
│   └── page.tsx            // Pipeline monitoring
└── settings/
    └── page.tsx            // Configuration
```

### Example View

```typescript
// app/projects/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { ProjectCard } from '@/components/refinery/ProjectCard';

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/projects')
      .then(res => res.json())
      .then(data => {
        setProjects(data.projects);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Projects</h1>
      <div className="grid grid-cols-3 gap-4">
        {projects.map(p => (
          <ProjectCard key={p.name} project={p} />
        ))}
      </div>
    </div>
  );
}
```

---

## Phase 6: Apply Reference Design Styling (1-2h)

### Copy Exact Visual from Reference

```css
/* From reference_design → refinery-web-app */

Colors:
- bg-neutral-950 (main background)
- bg-neutral-900/50 backdrop-blur (cards)
- border-neutral-800 (borders)
- text-neutral-200 (text)
- emerald-500 (primary accent)
- purple-500, blue-500 (secondary)

Typography:
- font-sans (system)
- tracking-tight (headings)
- text-xs uppercase tracking-wider (section headers)

Components:
- Rounded corners (rounded-lg)
- Subtle shadows
- Glassmorphic cards (backdrop-blur)
- Smooth transitions
```

### Layout Pattern

```tsx
// Same as reference:
<div className="min-h-screen bg-neutral-950 text-neutral-200">
  <Sidebar />  {/* Left nav */}
  <main className="flex-1">
    {/* Content */}
  </main>
  <SuperSidebar />  {/* Right expandable */}
</div>
```

---

## Phase 7: Data Source Integration (1-2h)

### Connect to Real Data

```typescript
// services/refinery-data.ts

export async function loadProjectChunks(projectName: string) {
  // For PROJECT_elements:
  const elementsChunks = [
    '/Users/lech/PROJECTS_all/PROJECT_elements/.agent/intelligence/chunks/agent_chunks.json',
    '/Users/lech/PROJECTS_all/PROJECT_elements/.agent/intelligence/chunks/core_chunks.json',
    // etc.
  ];

  // For other projects:
  // Scan /data/refinery/{project_name}/chunks/

  // Or: Use Cloud Storage
  // gs://elements-archive-2026/refinery/{project_name}/
}

export async function searchChunks(query: string, project?: string) {
  // Text search across chunks
  // TODO: Upgrade to semantic search with embeddings
}

export async function getMetrics() {
  // Aggregate across all projects
  return {
    total_projects: await countProjects(),
    total_chunks: await countChunks(),
    total_tokens: await sumTokens(),
  };
}
```

---

## Phase 8: Deploy Configuration (30min)

### Local Development

```bash
# .env.local
REFINERY_DATA_DIR=/Users/lech/PROJECTS_all/refinery_data
GEMINI_API_KEY=<from Doppler>
NODE_ENV=development
```

### Cloud Run Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# deploy.sh
#!/bin/bash
gcloud run deploy refinery-web \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars REFINERY_DATA_DIR=/data
```

---

## Key Architectural Decisions

### 1. Multi-Project Support

**Storage Structure:**
```
/data/refinery/
├── PROJECT_elements/
│   ├── chunks/
│   │   ├── agent_chunks.json
│   │   ├── core_chunks.json
│   │   └── aci_chunks.json
│   └── metadata.json
├── PROJECT_atman/
│   ├── chunks/
│   └── metadata.json
└── PROJECT_sentinel/
    ├── chunks/
    └── metadata.json
```

**Or Cloud Storage:**
```
gs://elements-archive-2026/refinery/
├── PROJECT_elements/...
├── PROJECT_atman/...
└── PROJECT_sentinel/...
```

### 2. API Design

**RESTful structure:**
```
GET    /api/projects              List all projects
GET    /api/projects/:name        Project details
GET    /api/projects/:name/chunks Chunks for project
POST   /api/chunks/search         Search across all or specific project
GET    /api/metrics               Global metrics
GET    /api/activity              Recent activity timeline
```

### 3. State Management

**Client-side:**
- React useState for UI state
- API calls for data (no Redux needed initially)
- localStorage for user preferences

**Server-side:**
- File system or Cloud Storage for data
- No database yet (JSON files sufficient)

---

## Timeline

**Today (if continuing):**
- ✅ Project created
- ⏳ Port 2-3 key components
- ⏳ One API route working
- ⏳ Basic view rendering data

**Tomorrow:**
- Port remaining components
- All API routes implemented
- Full navigation working

**This Week:**
- Polish UI
- Deploy to Cloud Run
- Multi-project support
- Testing

**Estimated:** 9-12 hours total

---

## Success Criteria

### Must Have (P0)
- [ ] Next.js app runs locally
- [ ] At least 1 view works (Overview or Projects)
- [ ] At least 1 API route works (GET /api/projects)
- [ ] Visual matches reference design
- [ ] Can view PROJECT_elements chunks

### Should Have (P1)
- [ ] All 7 views implemented (Overview, Pipelines, Inventory, Vault, Runs, Alerts, Settings)
- [ ] All API routes working
- [ ] Search functionality
- [ ] Multi-project support

### Nice to Have (P2)
- [ ] Cloud Run deployment
- [ ] Semantic search (not just text)
- [ ] Real-time updates
- [ ] Grafana/metrics integration

---

**READY TO START BUILDING?**

Check task b42bead to see if Next.js created successfully, then we'll start porting components!
