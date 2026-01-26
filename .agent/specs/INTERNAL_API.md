# INTERNAL API SPECIFICATION
# Standard Interfaces for Subsystem Interoperability

> **Status:** DRAFT (2026-01-26)
> **Purpose:** Define the official internal APIs that subsystems use to communicate
> **Related:** SUBSYSTEM_CITIZENSHIP.md, TOOLS_REGISTRY.yaml

---

## 1. OVERVIEW

Every subsystem on the Scaffold MUST communicate through **official interfaces**.
No direct imports, no magic globals, no undeclared dependencies.

```
PRINCIPLE: If it's not in the API, it doesn't exist.

A subsystem S1 can only know about S2 if:
  1. S2 is declared in S1's citizenship.integrations
  2. The connection uses an official API
  3. The data format is schema-validated
```

---

## 2. API CATEGORIES

### 2.1 FILE API (Most Common)

Subsystems communicate via files in canonical locations.

```yaml
FILE_API:
  producer:
    writes: "{canonical_path}/{artifact_name}"
    format: json | yaml | html | md
    schema: "{schema_path}"  # REQUIRED for json/yaml

  consumer:
    reads: "{canonical_path}/{artifact_name}"
    expects: "{schema_path}"
    on_missing: error | warn | skip

  canonical_paths:
    collider_output: ".collider/"
    pom_output: ".pom/"
    analysis_output: "context-management/analysis/"
    research_output: "standard-model-of-code/docs/research/"
```

**Example: S1 (Collider) → S14 (POM)**

```
S1 writes: .collider/unified_analysis.json
S14 reads: .collider/unified_analysis.json

Schema: standard-model-of-code/schema/unified_analysis.schema.json
```

### 2.2 CLI API

Subsystems can invoke each other via command line.

```yaml
CLI_API:
  invoker:
    calls: "{command} {args}"
    cwd: "${PROJECT_ROOT}"
    captures: stdout | file

  invoked:
    entrypoint: "{path_to_script}"
    accepts:
      - positional_args
      - named_flags
      - stdin
    returns:
      - exit_code (0 = success)
      - stdout (optional)
      - file (if --output specified)
```

**Example: S3 (analyze.py) → S9 (Laboratory)**

```bash
# S3 invokes S9
python laboratory.py experiment --name "test" --output results.json
```

### 2.3 PYTHON API (Same-Realm Only)

Direct Python imports allowed ONLY within same realm.

```yaml
PYTHON_API:
  allowed:
    - Particle ↔ Particle (standard-model-of-code internal)
    - Wave ↔ Wave (context-management internal)
    - Observer ↔ Observer (.agent internal)

  forbidden:
    - Particle → Wave (cross-realm)
    - Wave → Observer (cross-realm)

  pattern:
    from {module} import {function}
    result = function(**kwargs)
```

**Example: Within S1 (Collider)**

```python
# OK: Same realm
from src.core.purpose_field import detect_purpose_field

# FORBIDDEN: Cross realm
from context_management.tools.ai import analyze  # NO!
```

### 2.4 HOOK API

Subsystems can register hooks into lifecycle events.

```yaml
HOOK_API:
  events:
    - pre_commit
    - post_commit
    - pre_analysis
    - post_analysis
    - on_file_change
    - on_task_complete

  registration:
    location: ".agent/hooks/{event}.d/"
    format: executable script

  execution:
    order: alphabetical by filename
    failure: "continue" | "abort"
```

**Example: S8 (Hygiene) hooks into pre_commit**

```
.agent/hooks/pre_commit.d/
  01_hygiene.sh → runs pre-commit checks
  02_validate.sh → runs validation
```

---

## 3. DATA FORMATS (The Lingua Franca)

### 3.1 Universal Schema Requirements

All inter-subsystem data MUST have:

```yaml
metadata:
  schema_version: "1.0"
  generator: "S1/Collider"
  generated_at: "2026-01-26T12:00:00Z"
  project_root: "/path/to/project"

data:
  # Actual payload
```

### 3.2 Standard Formats

| Format | Use Case | Schema Location |
|--------|----------|-----------------|
| `unified_analysis.json` | Collider output | `schema/unified_analysis.schema.json` |
| `pom_manifest.yaml` | POM output | `tools/pom/manifest.schema.yaml` |
| `task.yaml` | Task Registry | `.agent/schema/task.schema.yaml` |
| `opportunity.yaml` | Opportunities | `.agent/schema/opportunity.schema.yaml` |
| `research_result.md` | Analysis output | N/A (markdown) |

### 3.3 Entity Reference Format

When one subsystem references another's entities:

```yaml
# Standard entity reference
entity_ref:
  source: "S1"  # Which subsystem owns this
  type: "node"  # Entity type
  id: "cli.py::main"  # Unique identifier within source
```

---

## 4. DEPENDENCY DECLARATION

### 4.1 In Citizenship Application

```yaml
# POM.citizenship.yaml
integrations:
  depends_on:
    - seat: S1
      api: FILE_API
      artifact: unified_analysis.json
      required: false  # Can run without it

    - seat: S3
      api: CLI_API
      command: "analyze.py --query {query}"
      required: false
```

### 4.2 Runtime Discovery

```python
# Future: Dependency injection via registry
from tools_registry import get_dependency

collider_output = get_dependency("S1", "unified_analysis.json")
if collider_output.exists():
    data = collider_output.read()
```

---

## 5. VERSIONING

### 5.1 API Versioning

Each API has a version. Breaking changes require major version bump.

```yaml
api_versions:
  FILE_API: "1.0"
  CLI_API: "1.0"
  PYTHON_API: "1.0"
  HOOK_API: "1.0"
```

### 5.2 Schema Versioning

Data schemas are versioned independently.

```yaml
schema_versions:
  unified_analysis: "2.0"  # Current
  pom_manifest: "1.0"
  task: "1.0"
```

### 5.3 Compatibility Matrix

```
Producer Schema v2.0 + Consumer expects v1.0 → WARN (may work)
Producer Schema v1.0 + Consumer expects v2.0 → ERROR (missing fields)
```

---

## 6. ERROR HANDLING

### 6.1 Standard Error Format

```yaml
error:
  source: "S14/POM"
  code: "MISSING_DEPENDENCY"
  message: "unified_analysis.json not found"
  severity: "warning"  # error | warning | info
  suggestion: "Run './pe collider full .' first"
  timestamp: "2026-01-26T12:00:00Z"
```

### 6.2 Error Propagation

```
S1 fails → S14 receives error → S14 continues with partial data
S1 fails → S14 receives error → S14 aborts (if required=true)
```

---

## 7. INTERNAL API REGISTRY

All official APIs are registered in `TOOLS_REGISTRY.yaml`:

```yaml
apis:
  FILE_API:
    version: "1.0"
    artifacts:
      - name: unified_analysis.json
        producer: S1
        consumers: [S14, S3]
        schema: "..."

      - name: pom_manifest.yaml
        producer: S14
        consumers: [S15, S3]
        schema: "..."

  CLI_API:
    version: "1.0"
    commands:
      - name: "collider full"
        provider: S1
        callers: [S3, S10]

      - name: "pom scan"
        provider: S14
        callers: [S3]
```

---

## 8. THE GOLDEN RULES

```
1. DECLARE before you use
   - All dependencies in citizenship application

2. SCHEMA before you serialize
   - All data formats have schemas

3. VERSION before you change
   - Breaking changes = major version bump

4. FAIL gracefully
   - Return standard error format
   - Don't crash the caller

5. LOG for observability
   - All API calls logged
   - Enable tracing across subsystems
```

---

*"An API is a promise. A schema is a contract. A version is a commitment."*
