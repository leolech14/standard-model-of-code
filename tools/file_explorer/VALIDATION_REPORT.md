# File Explorer Validation Report

## Sources
- **Gemini 2.5 Flash** (Architect Mode) - SMC theoretical alignment
- **Gemini 2.5 Pro** (Architect Mode) - Package structure validation
- **Perplexity** - Industry best practices research

---

## Validation Summary

| Question | Verdict | Confidence |
|----------|---------|------------|
| Is monolithic embedded UI appropriate? | **NO** | 100% |
| Should split frontend/backend? | **YES** | 100% |
| REST vs RPC for local tools? | **REST** | 95% |
| Proposed package structure correct? | **YES** (with refinements) | 90% |

---

## 1. Monolithic Embedded UI Pattern

### Verdict: NOT APPROPRIATE

**Gemini Flash (SMC Alignment):**
> "This pattern creates a tightly coupled **Knot** within our architectural graph. The Presentation Tier and Application Tier are inextricably intertwined. This anti-pattern violates the principle of distinct Rings and Tiers."

**Gemini Pro (RPBL Classification):**
> "The existing file_explorer.py is unequivocally **P-Tier (Prototype)**. Its monolithic structure... makes it brittle and unsuitable for extension."

**Perplexity (Industry Practice):**
> "Embedding works best when using a framework that handles abstraction properly (NiceGUI). If manually embedding HTML/CSS/JS strings, you lose tooling, type safety, and maintainability."

### Conclusion
The 7630-line monolithic file with embedded UI is a **topological knot** that must be untangled.

---

## 2. Frontend/Backend Separation

### Verdict: MANDATORY

**Gemini Flash:**
> "This split will establish clear Boundaries for the Presentation Tier (frontend) and Application Tier (backend)... A clear separation is not merely a best practice; it is a mandatory architectural evolution."

**Gemini Pro:**
> "The refactoring plan correctly guides evolution into a layered, spec-driven B-Tier system, separating the interface Ring from the pure logic Ring."

**Perplexity:**
> "Most professional local web UIs follow: Backend (Python/FastAPI) + Frontend (Vue/React/vanilla) + WebSocket/REST communication."

### Recommended Stack
- **Backend:** FastAPI (not http.server)
- **Frontend:** Vanilla JS or Lit (lightweight)
- **Communication:** REST API with OpenAPI spec

---

## 3. REST vs RPC for Local Tools

### Verdict: REST

**Gemini Flash:**
> "REST provides a widely understood, semantic framework. file_explorer deals inherently with 'resources' - files and folders. Operations map directly to CRUD on Resource Atoms."

**Gemini Pro:**
> "The API must be defined with an OpenAPI specification... proper HTTP status codes formalize a stable API contract."

**Perplexity:**
> "For localhost tools, many use hybrid: REST-style where appropriate (GET /files/{path}) and RPC-style where clearer (POST /actions/rename). This matches FastAPI's natural expression."

### API Design Mandate
- Use proper HTTP status codes (not always 200)
- OpenAPI 3.1 specification required
- Resource-oriented endpoints

---

## 4. Validated Package Structure

### Approved Structure (Gemini Pro)

```
tools/file_explorer/
├── __main__.py          # Entrypoint (./pe file-explorer start)
├── TOOL_SPEC.yaml       # Tool specification
├── api/                 # Ring 2: Interface Layer
│   ├── __init__.py
│   ├── routes.py        # API endpoints
│   ├── schemas.py       # Pydantic models
│   └── openapi.yaml     # API specification
├── service/             # Ring 1: Business Logic
│   ├── __init__.py
│   └── file_operations.py
├── core/                # Ring 0: Pure Domain Logic
│   ├── __init__.py
│   └── filesystem.py    # Low-level operations
├── ui/                  # Frontend (build artifacts gitignored)
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── tests/
    ├── test_api.py
    └── test_core.py
```

### Ring Architecture
| Ring | Layer | Responsibility |
|------|-------|----------------|
| Ring 0 | Core | Pure filesystem operations |
| Ring 1 | Service | Business logic orchestration |
| Ring 2 | API | HTTP interface, validation |
| Ring 3 | UI | Presentation (separate repo possible) |

---

## 5. Collider Integration

### Three Integration Modes

1. **Data Consumer** - Read `unified_analysis.json` to display file metadata
2. **Trigger** - Button to run `./pe collider full <path>`
3. **Meta-Analysis Target** - Collider analyzes the tool itself

### Implementation
```yaml
dependencies:
  subsystems:
    - name: "PARTICLE"
      type: "reads"
      description: "Reads unified_analysis.json for metadata display"
    - name: "OBSERVER"
      type: "triggers"
      description: "Can trigger Collider analysis"
```

---

## 6. Security Best Practices (Perplexity)

### Essential Protections
- Explicit path whitelisting
- Canonicalization (resolve symlinks, `..`)
- Bind to `127.0.0.1` only
- Input validation on all parameters
- Content-length limits

### Current Issues to Fix
- JSON parse exception (unhandled)
- Content-length DoS
- Zip-slip vulnerability
- Thread-unsafe globals

---

## 7. RPBL Classification

| State | Tier | Description |
|-------|------|-------------|
| Current | P-Tier | Prototype - monolithic, brittle |
| Target | B-Tier | Business Logic - layered, spec-driven |

---

## Action Items

### Phase 1: Restructure (Priority: HIGH)
- [ ] Create `tools/file_explorer/` package
- [ ] Extract core logic to `core/filesystem.py`
- [ ] Extract service layer to `service/file_operations.py`
- [ ] Extract API routes to `api/routes.py`

### Phase 2: API Standardization (Priority: HIGH)
- [ ] Implement proper HTTP status codes
- [ ] Create Pydantic schemas for validation
- [ ] Generate OpenAPI specification

### Phase 3: Frontend Separation (Priority: MEDIUM)
- [ ] Extract UI to `ui/` directory
- [ ] Add to `.gitignore`: `ui/node_modules/`, `ui/dist/`
- [ ] Consider separate frontend repo for future

### Phase 4: Integration (Priority: MEDIUM)
- [ ] Add to `pe` CLI entrypoint
- [ ] Implement Collider data consumption
- [ ] Add "Analyze with Collider" action

### Phase 5: Testing (Priority: HIGH)
- [ ] Unit tests for core layer
- [ ] Integration tests for API
- [ ] Security tests for path validation

---

## Validation Signatures

| Validator | Model | Date | Status |
|-----------|-------|------|--------|
| Gemini Flash | gemini-2.5-flash | 2026-01-31 | APPROVED |
| Gemini Pro | gemini-2.5-pro | 2026-01-31 | APPROVED |
| Perplexity | sonar | 2026-01-31 | CONFIRMED |

---

## References

- `particle/docs/research/gemini/docs/20260131_071816_*.md`
- `particle/docs/research/gemini/docs/20260131_071940_*.md`
- `particle/docs/research/perplexity/docs/20260131_071714_*.md`
- `API_REFACTORING_PLAN.md`
- `API_AUDIT_file_explorer.md`
