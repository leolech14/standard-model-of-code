# Palace Dashboard API Specification
**Date:** 2026-01-27 06:50
**Purpose:** 24/7 real-time monitoring and control dashboard
**Deployment:** Google Cloud (App Engine, Cloud Run, or AI Studio)
**Access:** Web browser, always-on, no local dependencies

---

## OVERVIEW

**The Dashboard provides:**
1. Real-time view of all 26 butlers (status, health, last run)
2. Knowledge library browser (2,673 chunks, searchable)
3. System health metrics (Communication Fabric state)
4. Cloud job controls (start/stop/configure schedulers)
5. GCS file browser (projectome snapshots, intelligence outputs)
6. Automation controls (enable/disable watchers, adjust thresholds)

**Architecture:**
```
Browser
    ↓
HTTPS (Google Cloud)
    ↓
Dashboard API (Python/FastAPI)
    ↓
├─ READ: Query butler status, chunks, metrics (GET endpoints)
├─ WRITE: Control cloud jobs, automation (POST endpoints)
└─ FILES: Browse/download GCS files (GET /files/*)

    ↓
Backend Connections:
├─ GCS (cloud files)
├─ Secret Manager (API keys)
├─ Cloud Scheduler (job controls)
├─ Cloud Run Jobs (execution triggers)
└─ Local State (via GCS mirror)
```

---

## API ENDPOINTS SCHEMA

### GROUP 1: BUTLER STATUS (Real-Time Monitoring)

#### GET /api/butlers
**Purpose:** List all butlers with current status

**Response:**
```json
{
  "timestamp": "2026-01-27T06:50:00Z",
  "total_butlers": 26,
  "healthy_count": 24,
  "unhealthy_count": 2,
  "butlers": [
    {
      "name": "Communication Fabric",
      "type": "ai",
      "healthy": true,
      "last_update": "2026-01-27T06:45:00Z",
      "summary": "BRONZE tier, +0.70 margin, STABLE",
      "details_endpoint": "/api/butlers/comm_fabric"
    },
    {
      "name": "Refinery",
      "type": "ai",
      "healthy": true,
      "last_update": "2026-01-27T06:26:00Z",
      "summary": "2,673 chunks, 539K tokens",
      "details_endpoint": "/api/butlers/refinery"
    },
    {
      "name": "Autopilot",
      "type": "orchestrator",
      "healthy": true,
      "last_update": "2026-01-27T06:00:00Z",
      "summary": "All systems GREEN, 100% success rate",
      "details_endpoint": "/api/butlers/autopilot"
    }
    // ... 23 more butlers
  ]
}
```

**Refresh Rate:** Every 10 seconds
**Caching:** 5 seconds

---

#### GET /api/butlers/{butler_id}
**Purpose:** Detailed status for specific butler

**Example:** `/api/butlers/comm_fabric`

**Response:**
```json
{
  "name": "Communication Fabric",
  "type": "ai",
  "healthy": true,
  "last_update": "2026-01-27T06:45:00Z",
  "metrics": {
    "F": 9.81,
    "MI": 0.7277,
    "N": 0.6850,
    "SNR": 0.9270,
    "R_auto": 1.0,
    "R_manual": 0.5477,
    "delta_H": 1.0,
    "stability_margin": 0.70,
    "health_tier": "BRONZE"
  },
  "warnings": [
    "High noise level (0.6850 > 0.5)"
  ],
  "recommendations": [
    "Be prepared for context to shift"
  ],
  "history_endpoint": "/api/butlers/comm_fabric/history"
}
```

**Refresh Rate:** Every 10 seconds

---

#### GET /api/butlers/{butler_id}/history
**Purpose:** Time-series data for butler

**Example:** `/api/butlers/comm_fabric/history?hours=24`

**Response:**
```json
{
  "butler": "Communication Fabric",
  "period_hours": 24,
  "data_points": 48,
  "series": [
    {
      "timestamp": "2026-01-27T05:00:00Z",
      "F": 9.81,
      "MI": 0.73,
      "stability_margin": 0.70
    },
    {
      "timestamp": "2026-01-27T06:00:00Z",
      "F": 9.75,
      "MI": 0.73,
      "stability_margin": 0.71
    }
    // ... 46 more points
  ],
  "trends": {
    "F": {"direction": "down", "delta": -0.06},
    "stability_margin": {"direction": "up", "delta": +0.01}
  }
}
```

**Use:** Chart trends, detect degradation
**Refresh Rate:** Every 30 seconds

---

### GROUP 2: KNOWLEDGE LIBRARY (Searchable Content)

#### GET /api/knowledge/search
**Purpose:** Search consolidated knowledge chunks

**Query Params:**
- `q` (required): Search query
- `limit` (optional): Max results (default 10)
- `type` (optional): Filter by chunk type (function, class, h1, etc.)

**Example:** `/api/knowledge/search?q=Communication+Fabric&limit=5`

**Response:**
```json
{
  "query": "Communication Fabric",
  "total_matches": 23,
  "returned": 5,
  "results": [
    {
      "chunk_id": "abc123...",
      "source_file": ".agent/tools/autopilot.py",
      "chunk_type": "function",
      "start_line": 445,
      "relevance": 0.98,
      "match_count": 6,
      "preview": "...Step 3: Communication Fabric - Recording state vector...",
      "full_content_endpoint": "/api/knowledge/chunks/abc123"
    }
    // ... 4 more
  ]
}
```

**Refresh Rate:** No caching (search is fast, <100ms)

---

#### GET /api/knowledge/library
**Purpose:** Organized library view (files ranked by chunk count)

**Query Params:**
- `limit` (optional): Max files (default 50)
- `sort` (optional): `chunks|tokens|name` (default chunks)

**Response:**
```json
{
  "total_files": 207,
  "total_chunks": 2673,
  "total_tokens": 539176,
  "files": [
    {
      "path": ".agent/intelligence/session_summary_20260123.md",
      "chunks": 77,
      "tokens": 4798,
      "types": {"h1": 14, "h2": 15, "h3": 48},
      "last_modified": "2026-01-23T12:00:00Z",
      "chunks_endpoint": "/api/knowledge/files/.agent/intelligence/session_summary_20260123.md"
    }
    // ... 49 more
  ]
}
```

**Refresh Rate:** Every 60 seconds (chunks don't change that often)

---

#### GET /api/knowledge/chunks/{chunk_id}
**Purpose:** Full content of specific chunk

**Response:**
```json
{
  "chunk_id": "abc123...",
  "source_file": ".agent/tools/autopilot.py",
  "chunk_type": "function",
  "start_line": 445,
  "end_line": 467,
  "relevance_score": 0.98,
  "content": "def run_comm_fabric(circuit_breaker):\n    ...",
  "metadata": {
    "file_type": ".py",
    "created_at": "2026-01-27T06:26:00Z"
  }
}
```

**Refresh Rate:** No caching (immutable chunks)

---

#### GET /api/knowledge/stats
**Purpose:** Knowledge library statistics

**Response:**
```json
{
  "last_generated": "2026-01-27T06:26:55Z",
  "git_sha": "c913e631",
  "total_chunks": 2673,
  "total_tokens": 539176,
  "by_module": {
    "agent": {"chunks": 1967, "tokens": 220101},
    "core": {"chunks": 598, "tokens": 289702},
    "aci": {"chunks": 108, "tokens": 29373}
  },
  "by_type": {
    "function": 699,
    "h3": 680,
    "h2": 522,
    "h1": 318,
    "class": 253
  },
  "freshness": "current"  // "current" | "stale" | "unknown"
}
```

**Refresh Rate:** Every 30 seconds

---

### GROUP 3: CLOUD JOBS (Control & Monitor)

#### GET /api/cloud/jobs
**Purpose:** List all Cloud Run Jobs

**Response:**
```json
{
  "jobs": [
    {
      "name": "socratic-audit-job",
      "region": "us-central1",
      "last_run": "2026-01-27T10:17:46Z",
      "status": "success",  // success|failed|running
      "duration_seconds": 762,
      "exit_code": 0,
      "next_scheduled": "2026-01-27T12:00:00Z",
      "execution_history_endpoint": "/api/cloud/jobs/socratic-audit-job/history"
    }
  ]
}
```

**Refresh Rate:** Every 30 seconds

---

#### GET /api/cloud/jobs/{job_name}/history
**Purpose:** Execution history for job

**Query Params:**
- `limit` (optional): Max executions (default 20)

**Response:**
```json
{
  "job_name": "socratic-audit-job",
  "total_executions": 156,
  "returned": 20,
  "executions": [
    {
      "execution_id": "socratic-audit-job-4rjb8",
      "start_time": "2026-01-27T10:00:00Z",
      "end_time": "2026-01-27T10:12:42Z",
      "status": "success",
      "exit_code": 0,
      "duration_seconds": 762,
      "logs_endpoint": "/api/cloud/jobs/socratic-audit-job/logs/socratic-audit-job-4rjb8"
    }
    // ... 19 more
  ],
  "success_rate": 0.64,  // 64% success (was 0%, now improving)
  "avg_duration_seconds": 785
}
```

**Refresh Rate:** Every 60 seconds

---

#### POST /api/cloud/jobs/{job_name}/execute
**Purpose:** Trigger job execution manually

**Request Body:**
```json
{
  "wait": false  // true = wait for completion, false = async
}
```

**Response:**
```json
{
  "job_name": "socratic-audit-job",
  "execution_id": "socratic-audit-job-xyz123",
  "status": "running",
  "started_at": "2026-01-27T06:50:00Z",
  "logs_url": "https://console.cloud.google.com/run/jobs/...",
  "poll_endpoint": "/api/cloud/jobs/socratic-audit-job/status/socratic-audit-job-xyz123"
}
```

**Use:** Manual job trigger from dashboard
**Auth:** Requires admin role

---

#### GET /api/cloud/jobs/{job_name}/status/{execution_id}
**Purpose:** Poll execution status

**Response:**
```json
{
  "execution_id": "socratic-audit-job-xyz123",
  "status": "running",  // pending|running|success|failed
  "progress": "Step 2/5: Processing...",
  "elapsed_seconds": 45,
  "estimated_remaining_seconds": 120
}
```

**Refresh Rate:** Real-time (poll every 2 seconds when watching)

---

### GROUP 4: CLOUD SCHEDULERS (Schedule Management)

#### GET /api/cloud/schedulers
**Purpose:** List all Cloud Scheduler jobs

**Response:**
```json
{
  "schedulers": [
    {
      "name": "socratic-audit-job-trigger-midnight",
      "schedule": "0 0 * * *",  // Cron format
      "timezone": "UTC",
      "target": "socratic-audit-job",
      "enabled": true,
      "last_run": "2026-01-27T00:00:00Z",
      "next_run": "2026-01-28T00:00:00Z",
      "success_rate": 0.64
    }
    // ... 4 more schedulers
  ]
}
```

**Refresh Rate:** Every 60 seconds

---

#### POST /api/cloud/schedulers/{scheduler_name}/toggle
**Purpose:** Enable/disable scheduler

**Request Body:**
```json
{
  "enabled": false  // true = enable, false = disable
}
```

**Response:**
```json
{
  "scheduler_name": "socratic-audit-job-trigger-midnight",
  "enabled": false,
  "message": "Scheduler disabled"
}
```

**Use:** Pause failing jobs, enable fixed jobs
**Auth:** Requires admin role

---

### GROUP 5: GCS FILES (Cloud Storage Browser)

#### GET /api/files/list
**Purpose:** Browse GCS bucket contents

**Query Params:**
- `path` (optional): Subdirectory (default: root)
- `limit` (optional): Max files (default 100)

**Example:** `/api/files/list?path=projectome/R0_raw/&limit=50`

**Response:**
```json
{
  "bucket": "elements-archive-2026",
  "path": "projectome/R0_raw/",
  "files": [
    {
      "name": "20260127_063000.json",
      "path": "projectome/R0_raw/20260127_063000.json",
      "size_bytes": 5242880,
      "size_human": "5.0 MB",
      "created": "2026-01-27T06:30:00Z",
      "updated": "2026-01-27T06:30:00Z",
      "download_url": "/api/files/download?file=projectome/R0_raw/20260127_063000.json"
    }
    // ... more files
  ],
  "total_count": 127,
  "total_size_bytes": 671088640,
  "total_size_human": "640 MB"
}
```

**Refresh Rate:** Every 60 seconds

---

#### GET /api/files/download
**Purpose:** Download file from GCS

**Query Params:**
- `file` (required): Full path in bucket

**Example:** `/api/files/download?file=projectome/R0_raw/20260127_063000.json`

**Response:** File content (binary or JSON)
**Content-Type:** Auto-detected from file extension

**Use:** Download snapshots, view intelligence outputs

---

#### POST /api/files/upload
**Purpose:** Upload file to GCS (manual snapshot)

**Request:** Multipart form with file
**Query Params:**
- `path` (required): Destination path in bucket

**Response:**
```json
{
  "uploaded": true,
  "path": "projectome/R0_raw/manual_20260127.json",
  "size_bytes": 5242880,
  "url": "gs://elements-archive-2026/projectome/R0_raw/manual_20260127.json"
}
```

**Use:** Manual snapshot upload
**Auth:** Requires admin role

---

### GROUP 6: AUTOMATION CONTROL

#### GET /api/automation/status
**Purpose:** Overall automation health

**Response:**
```json
{
  "timestamp": "2026-01-27T06:50:00Z",
  "automation_level": "92%",
  "local_watchers": {
    "filesystem_watcher": {
      "running": true,
      "pid": 57794,
      "last_trigger": "2026-01-27T06:32:00Z",
      "triggers_today": 4
    },
    "socratic_audit_watcher": {
      "running": true,
      "last_trigger": "2026-01-27T05:00:00Z"
    },
    "hsl_daemon": {
      "running": true,
      "last_trigger": "2026-01-27T06:00:00Z"
    }
  },
  "autopilot": {
    "enabled": true,
    "level": "FULL",
    "last_run": "2026-01-26T22:57:39Z",
    "success_rate": 1.0
  },
  "circuit_breakers": {
    "open_count": 0,
    "systems_status": {
      "tdj": "GREEN",
      "trigger_engine": "GREEN",
      "enrichment": "GREEN",
      "comm_fabric": "GREEN"
    }
  }
}
```

**Refresh Rate:** Every 30 seconds

---

#### POST /api/automation/wire/trigger
**Purpose:** Manually trigger wire pipeline

**Request Body:**
```json
{
  "mode": "quick",  // "quick" | "full"
  "wait": false
}
```

**Response:**
```json
{
  "triggered": true,
  "mode": "quick",
  "started_at": "2026-01-27T06:50:00Z",
  "estimated_duration_seconds": 30,
  "poll_endpoint": "/api/automation/wire/status"
}
```

**Use:** Force update from dashboard
**Auth:** Requires user role

---

#### GET /api/automation/wire/status
**Purpose:** Check if wire is currently running

**Response:**
```json
{
  "running": true,
  "current_stage": "REFINERY_CORE",
  "progress": "7/9 stages complete",
  "elapsed_seconds": 12,
  "estimated_remaining_seconds": 5
}
```

**Refresh Rate:** Real-time (poll every 2s when watching)

---

#### POST /api/automation/autopilot/toggle
**Purpose:** Enable/disable autopilot

**Request Body:**
```json
{
  "enabled": true,
  "level": "FULL"  // FULL|PARTIAL|MANUAL|EMERGENCY
}
```

**Response:**
```json
{
  "autopilot_enabled": true,
  "level": "FULL",
  "message": "Autopilot enabled at FULL level"
}
```

**Use:** Emergency stop, level adjustment
**Auth:** Requires admin role

---

### GROUP 7: SYSTEM HEALTH (Communication Fabric)

#### GET /api/health/current
**Purpose:** Current system health snapshot

**Response:**
```json
{
  "timestamp": "2026-01-27T06:50:00Z",
  "health_tier": "BRONZE",
  "stability_margin": 0.70,
  "status": "STABLE",
  "metrics": {
    "F": 9.81,
    "MI": 0.7277,
    "N": 0.6850,
    "SNR": 0.9270,
    "R_auto": 1.0,
    "R_manual": 0.5477,
    "delta_H": 1.0
  },
  "alerts": [
    {
      "severity": "WARNING",
      "type": "noise_high",
      "message": "Noise level high (0.6850 > 0.5)",
      "timestamp": "2026-01-27T06:45:00Z"
    }
  ],
  "recommendations": [
    "Be prepared for context to shift"
  ]
}
```

**Refresh Rate:** Every 10 seconds

---

#### GET /api/health/trends
**Purpose:** Health metrics over time

**Query Params:**
- `hours` (optional): Time window (default 24)

**Response:**
```json
{
  "period_hours": 24,
  "data_points": 48,
  "current": {
    "F": 9.81,
    "MI": 0.73,
    "stability_margin": 0.70
  },
  "deltas": {
    "F": -0.12,
    "MI": +0.02,
    "stability_margin": +0.05
  },
  "trend_alerts": [
    "Stability margin improving (+0.05 over 24h)"
  ]
}
```

**Refresh Rate:** Every 60 seconds

---

### GROUP 8: DASHBOARD METADATA

#### GET /api/meta/info
**Purpose:** Dashboard itself status

**Response:**
```json
{
  "dashboard_version": "1.0.0",
  "api_version": "1.0",
  "uptime_seconds": 86400,
  "repo_root": "/app/repo_mirror",
  "git_sha": "c913e631",
  "last_sync": "2026-01-27T06:30:00Z",
  "endpoints": {
    "total": 20,
    "categories": ["butlers", "knowledge", "cloud", "automation", "health", "files"]
  }
}
```

**Refresh Rate:** Static (cached forever)

---

## WEBAPP STRUCTURE (Google Cloud Deployment)

### Option A: Cloud Run (Recommended)
**File:** `dashboard/main.py` (FastAPI app)

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from google.cloud import storage, run_v2, scheduler_v1
import json

app = FastAPI(title="Palace Dashboard API")

# Serve static frontend
@app.get("/")
def dashboard_ui():
    return FileResponse("static/index.html")

# API endpoints
@app.get("/api/butlers")
def list_butlers():
    # Query all butler status files from GCS or local
    ...

@app.get("/api/knowledge/search")
def search_knowledge(q: str, limit: int = 10):
    # Query chunks via refinery
    ...

@app.post("/api/cloud/jobs/{job_name}/execute")
def trigger_job(job_name: str):
    # Use Cloud Run Jobs API
    client = run_v2.JobsClient()
    ...

# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}
```

**Deploy:**
```bash
# Build
cd dashboard
gcloud builds submit --tag gcr.io/elements-archive-2026/palace-dashboard

# Deploy
gcloud run deploy palace-dashboard \
    --image gcr.io/elements-archive-2026/palace-dashboard \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars GCS_BUCKET=elements-archive-2026 \
    --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```

**Result:** `https://palace-dashboard-HASH-uc.a.run.app`

---

### Option B: App Engine (Zero Config)
**File:** `dashboard/app.yaml`

```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT main:app

env_variables:
  GCS_BUCKET: "elements-archive-2026"

automatic_scaling:
  min_instances: 1
  max_instances: 5
```

**Deploy:**
```bash
cd dashboard
gcloud app deploy
```

**Result:** `https://elements-archive-2026.uc.r.appspot.com`

---

## FRONTEND (No-Code AI Studio Deployment)

### Static HTML Dashboard
**File:** `dashboard/static/index.html`

**Features:**
- Auto-refreshing cards for each butler (10s refresh)
- Knowledge search box (instant results)
- Library browser (paginated file list)
- Cloud job controls (start/stop buttons)
- Health metrics charts (Fabric time-series)
- GCS file browser (download snapshots)

**Technology:**
- Vanilla JS (no build step)
- Fetch API (calls backend endpoints)
- Chart.js (health metrics visualization)
- Tailwind CSS (styling)

**Deploy to AI Studio:**
1. Open Google AI Studio
2. Create new "Web App" project
3. Upload index.html
4. Point to API endpoint (Cloud Run URL)
5. Publish

**Result:** 24/7 dashboard, no code, GUI deployment

---

## DASHBOARD UI MOCKUP

```
┌─────────────────────────────────────────────────────────────┐
│ 🏰 PALACE DASHBOARD                              [LIVE]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ System Health: BRONZE ● Stability: +0.70 (STABLE)          │
│ Knowledge: 2,673 chunks | Last updated: 3min ago           │
│ Automation: 92% ● All systems GREEN                        │
│                                                             │
├───────── BUTLERS (26) ──────────────────────────────────────┤
│                                                             │
│ ✅ Communication Fabric     BRONZE, +0.70      [Details]   │
│ ✅ Refinery                 2,673 chunks       [Details]   │
│ ✅ Autopilot                All GREEN          [Details]   │
│ ✅ LOL                      2,469 entities     [Details]   │
│ ✅ TDJ                      2,899 files        [Details]   │
│ ✅ Collider                 Cached (15min)     [Details]   │
│ ... 20 more                                                 │
│                                                             │
├───────── CLOUD JOBS ────────────────────────────────────────┤
│                                                             │
│ socratic-audit-job          SUCCESS (12min ago)  [▶ Run]  │
│   Next: 12:00 UTC (5h 10m)  Success: 64%        [⏸ Pause]  │
│                                                             │
│ Schedulers:                                                 │
│   ✅ Midnight (00:00)  ⏸ Morning (06:00)  ✅ Noon  ✅ Evening│
│                                                             │
├───────── KNOWLEDGE LIBRARY ──────────────────────────────────┤
│                                                             │
│ [Search: ___________________________] [🔍 Search]          │
│                                                             │
│ Top Files:                                                  │
│  1. session_summary.md         77 chunks  [View]           │
│  2. autopilot.py               23 chunks  [View]           │
│  3. edge_extractor.py          39 chunks  [View]           │
│                                            [Browse All →]  │
│                                                             │
├───────── HEALTH TRENDS ──────────────────────────────────────┤
│                                                             │
│ [Chart: Stability Margin (24h)]                            │
│   ▲ 1.0                                                    │
│   │     ╱──────────────                                    │
│   │ ╱──╱                                                   │
│   │╱                                                       │
│   └─────────────────────────────▶                         │
│   0.0                          24h                         │
│                                                             │
│ Current: +0.70 (STABLE) ● Trend: +0.05 (improving)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## IMPLEMENTATION FILES

### Backend API
```
dashboard/
├── main.py                 # FastAPI app (400 lines)
├── requirements.txt        # Dependencies
├── Dockerfile              # Container build
└── routers/
    ├── butlers.py          # Butler endpoints
    ├── knowledge.py        # Search/library endpoints
    ├── cloud.py            # Job control endpoints
    ├── health.py           # Fabric metrics endpoints
    └── files.py            # GCS browser endpoints
```

### Frontend
```
dashboard/static/
├── index.html              # Main dashboard (500 lines)
├── styles.css              # Tailwind/custom CSS
└── app.js                  # Fetch API + charts (300 lines)
```

### Deployment
```
dashboard/
├── app.yaml                # App Engine config (if using App Engine)
├── cloudbuild.yaml         # Build config (if using Cloud Run)
└── deploy.sh               # One-click deployment
```

---

## DATA FLOW

### Read Operations (Monitoring):
```
Browser → GET /api/butlers
    ↓
Dashboard API → Reads from GCS mirror
    ↓
gs://elements-archive-2026/intelligence/state/live.yaml
gs://elements-archive-2026/intelligence/chunks/metadata.json
gs://elements-archive-2026/intelligence/comms/state_history.jsonl
    ↓
Returns: Real-time butler status
```

### Write Operations (Control):
```
Browser → POST /api/cloud/jobs/socratic-audit-job/execute
    ↓
Dashboard API → Cloud Run Jobs API
    ↓
gcloud run jobs execute socratic-audit-job
    ↓
Returns: Execution ID, status endpoint
```

### Sync Pattern:
```
Local Mac (every wire run)
    ↓
Uploads state files to GCS
    ↓
gs://elements-archive-2026/intelligence/state/*

Dashboard API (every 30s)
    ↓
Downloads state files from GCS
    ↓
Caches locally (5-60s depending on endpoint)
    ↓
Serves to browser
```

**Result:** Dashboard shows real-time state even when Mac is off (reads from GCS)

---

## DEPLOYMENT STRATEGY

### Phase 1: Backend API (4 hours)
1. Create dashboard/ directory structure
2. Implement FastAPI app with all endpoints
3. Test locally (uvicorn main:app)
4. Dockerize

### Phase 2: Frontend UI (3 hours)
1. Create index.html with all sections
2. Add auto-refresh logic (Fetch API)
3. Add Chart.js for trends
4. Test with backend

### Phase 3: Deploy to Cloud (1 hour)
1. Build container: `gcloud builds submit`
2. Deploy to Cloud Run: `gcloud run deploy`
3. Configure IAM (allow-unauthenticated for dashboard)
4. Test live URL

### Phase 4: Integrate (1 hour)
1. Add GCS sync to wire.py (upload state files)
2. Add dashboard URL to CLAUDE.md
3. Test end-to-end

**Total:** 9 hours for complete 24/7 dashboard

---

## SECURITY

### Public Endpoints (No Auth):
- GET /api/butlers (status)
- GET /api/knowledge/search (search)
- GET /api/health/current (metrics)

### Authenticated Endpoints (Requires API Key):
- POST /api/cloud/jobs/{name}/execute (trigger jobs)
- POST /api/automation/* (control automation)
- POST /api/cloud/schedulers/*/toggle (modify schedules)
- POST /api/files/upload (upload files)

### Secret Storage:
- API keys in Secret Manager
- Dashboard uses service account
- Frontend sends bearer token

---

## COST ESTIMATE

**Cloud Run:**
- Min instances: 1 (always-on)
- Memory: 512MB
- CPU: 1

**Monthly Cost:**
- Cloud Run: ~$5-10/month
- Storage: ~$0.50/month (state files)
- Bandwidth: ~$1/month (API calls)

**Total:** ~$7-12/month for 24/7 dashboard

---

## SUCCESS CRITERIA

### Dashboard Working When:
- ✅ Can view all 26 butlers in real-time
- ✅ Can search 2,673 chunks instantly
- ✅ Can browse knowledge library
- ✅ Can trigger cloud jobs manually
- ✅ Can see health trends (charts)
- ✅ Can enable/disable automation
- ✅ Works when Mac is off (reads from GCS)

### Expected Performance:
- Initial load: <2 seconds
- Butler status refresh: 10 seconds
- Search query: <500ms
- Job trigger: <1 second
- Health metrics: 30 seconds

---

**SHALL I BUILD THE DASHBOARD (9 hours)?**

Or document the spec and defer implementation?
