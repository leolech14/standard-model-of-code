# Cloud Context Refinery Platform

**Status:** L7 → L8 Evolution (Module → Holon → Platform)
**Vision:** Independent context processing platform serving multiple projects
**Origin:** Spun off from PROJECT_elements (birthplace, not home)

---

## What Is This?

**Cloud Context Refinery** is an independent L7 system (evolving to L8+) that:
- Processes context for MULTIPLE projects (multi-tenant)
- Chunks, indexes, and semantically organizes codebases + documentation
- Provides universal context API for AI agents and developers
- Born from PROJECT_elements but serves ANY project

**NOT:** A feature of Elements
**IS:** A platform Elements happens to use

---

## The Vision: Module → Holon → Platform

### Phase 1: Module (L6) ✅ DONE
```
Refinery as package within PROJECT_elements
Serves: One project (Elements)
Location: elements/context-management/tools/refinery/
```

### Phase 2: Holon (L7) 🔄 IN PROGRESS
```
Refinery as independent system
Serves: Multiple projects (Elements + Atman + Sentinel + ...)
Location: Separate deployment, Elements consumes via API
```

### Phase 3: Platform (L8+) 🎯 TARGET
```
Refinery as universal context processor
Serves: Any codebase (open source, Enterprise, etc.)
Location: Cloud platform, SDK/clients for all languages
Like: Elasticsearch, Neo4j, Datadog - infrastructure
```

---

## Architecture Principles

### 1. Multi-Tenant from Day 1
- Every API accepts `project` parameter
- Data isolated per project
- No hardcoded Elements paths

### 2. API-First
- All functionality via REST API
- Elements = just another client
- Clean contract boundaries (POINT framework - 78% validated)

### 3. Cloud-Native
- Designed for Cloud Run/Kubernetes
- Stateless where possible
- Scalable horizontally

### 4. Theory-Grounded
- Implements SMoC principles
- Compositional alignment (95% validated)
- L6→L5→L3 proper composition

---

## Current Status

**Development:** In `context-management/experiments/refinery-platform/`
**Production:** Will deploy to Cloud Run
**Origin Data:** PROJECT_elements chunks (first tenant)

---

## Quick Start

```bash
# Install
npm install

# Run locally
npm run dev  # http://localhost:3001

# Deploy
npm run build
gcloud run deploy refinery-platform --source .
```

---

## Future

**This will become:**
- Separate GitHub repo
- Independent product
- Larger than Elements
- Universal context platform

**Elements will:**
- Use Refinery SDK
- Just one tenant
- Consume via API

---

**Spinoff in progress.** 🚀
