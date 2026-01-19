# Spectrometer System Audit (local run)

Generated: 2025-12-14T14:53:13

## 1) What this system is trying to accomplish

Spectrometer is an architecture-aware codebase analyzer. It aims to:
- **Scan one or many repositories** (polyglot).
- **Extract structural elements** (“particles / atoms / hadrons”) such as Entities, ValueObjects, Repositories, UseCases, Controllers, etc.
- **Assign semantic identifiers** and build **dependency/call graphs**.
- **Score components** with an RPBL rubric (Responsibility, Purity, Boundary, Lifecycle).
- **Detect architectural risk** (e.g., “God Classes”) and generate recommendations.
- **Generate outputs** for humans (Markdown + Mermaid diagrams) and for LLM consumption (JSON/CSV).


## 2) What I actually tested (executed)

I tested the code in the uploaded bundle by executing the available entrypoints in this environment:

- **Attempted primary pipeline**: `learning_engine.py --single-repo <repo>`  
  - Result: **blocked** here because the environment is missing `tree_sitter` + `tree_sitter_python` bindings (hard requirement in `core/system_health.py`), and `learning_engine.py` also had a missing `Tuple` import (runtime error) before patching.

- **Executed minimal pipeline** (works without tree-sitter): `legacy_main.py <repo>` which uses `core/universal_detector.py`.
  - Repos analyzed:
    - `validation/test_repos/dddpy_real`
    - `validation/test_repos/fastapi`
    - `test_polyglot_god_classes`
    - `core/` (Spectrometer core itself)

- **Executed truth discovery**: `truth_extractor.py <repo> --output <file.json>` on `dddpy_real`.

- **Executed God Class detector (lite)**: `core/god_class_detector_lite.py` via import.
  - Note: had to patch **Path.walk()** → `os.walk()` + fix path-join; otherwise it crashes on Python 3.11.


## 3) Analytics from real runs

### 3.1 Repo-level metrics (universal detector)

| repo              |   files |   particles |   file_coverage_pct |   recognized_pct |   recognized |   unknown |   unique_types |   avg_confidence |   avg_rpbl |   lines |   chars |   runtime_s |
|:------------------|--------:|------------:|--------------------:|-----------------:|-------------:|----------:|---------------:|-----------------:|-----------:|--------:|--------:|------------:|
| dddpy_real        |      65 |         114 |               64.62 |            28.07 |           32 |        82 |              9 |            36.05 |      5.206 |    2637 |   77102 |       0.675 |
| fastapi_fixture   |      52 |         261 |               61.54 |            23.75 |           62 |       199 |              9 |            34.85 |      5.124 |   20362 |  727485 |       1.141 |
| polyglot_example  |       2 |           9 |              100    |            11.11 |            1 |         8 |              2 |            35    |      5.056 |    1014 |   34288 |     nan     |
| spectrometer_core |      17 |          56 |               94.12 |             3.57 |            2 |        54 |              3 |            31.16 |      5.045 |    6247 |  253536 |     nan     |


Notes:
- `file_coverage_pct` = % of files in the repo where at least one particle was detected.
- `recognized_pct` = % of particles classified as a non-`Unknown` type.


### 3.2 dddpy_real truth-based scoring (vs Truth Extractor)

Truth Extractor expected components: **8**

- **Name recall** (expected names found anywhere in detected particles): **100%**
- **Type accuracy (strict)**: **88%**
- **Type accuracy (lenient, RepositoryImpl→Repository)**: **100%**

Strict set scoring (exact type match):
- Precision: **21.9%** (matches / all detected typed components)
- Recall: **87.5%** (matches / all expected)
- F1: **0.35**

Lenient set scoring (RepositoryImpl treated as Repository):
- Precision: **25.0%**
- Recall: **100.0%**
- F1: **0.40**


### 3.3 dddpy_real layering compliance (based on internal import edges)

- Layer-edge compliance (simple Clean Architecture rule-set): **99.2%**

Violations:

| from_layer   | to_layer       |   count |
|:-------------|:---------------|--------:|
| presentation | infrastructure |       1 |

### 3.4 God Class (Antimatter) detector results

**dddpy_real**: 0 god-classes flagged out of 35 classes; avg risk 17.8%

Top risk classes (by score):
| class_name              |   antimatter_risk_score |   lines_of_code |   method_count |   touchpoint_overload | file_path                                                                                                                           |
|:------------------------|------------------------:|----------------:|---------------:|----------------------:|:------------------------------------------------------------------------------------------------------------------------------------|
| TodoApiRouteHandler     |                   41.95 |             239 |              0 |                    70 | /mnt/data/spectrometer_system_audit/validation/test_repos/dddpy_real/dddpy/presentation/api/todo/handlers/todo_api_route_handler.py |
| UpdateTodoUseCaseImpl   |                   32.05 |              41 |              0 |                    90 | /mnt/data/spectrometer_system_audit/validation/test_repos/dddpy_real/dddpy/usecase/todo/update_todo_usecase.py                      |
| StartTodoUseCaseImpl    |                   31.85 |              37 |              0 |                    80 | /mnt/data/spectrometer_system_audit/validation/test_repos/dddpy_real/dddpy/usecase/todo/start_todo_usecase.py                       |
| CompleteTodoUseCaseImpl |                   31.85 |              37 |              0 |                    80 | /mnt/data/spectrometer_system_audit/validation/test_repos/dddpy_real/dddpy/usecase/todo/complete_todo_usecase.py                    |
| FindTodoByIdUseCaseImpl |                   31.45 |              29 |              0 |                    50 | /mnt/data/spectrometer_system_audit/validation/test_repos/dddpy_real/dddpy/usecase/todo/find_todo_by_id_usecase.py                  |


**fastapi_fixture**: 0 god-classes flagged out of 118 classes; avg risk 14.7%

Top risk classes (by score):
| class_name   |   antimatter_risk_score |   lines_of_code |   method_count |   touchpoint_overload | file_path                                                                         |
|:-------------|------------------------:|----------------:|---------------:|----------------------:|:----------------------------------------------------------------------------------|
| APIRouter    |                   75    |            1278 |              0 |                   100 | /mnt/data/spectrometer_system_audit/validation/test_repos/fastapi/routing.py      |
| FastAPI      |                   69.45 |             589 |              0 |                   100 | /mnt/data/spectrometer_system_audit/validation/test_repos/fastapi/applications.py |
| Item         |                   65    |            1256 |              0 |                   100 | /mnt/data/spectrometer_system_audit/validation/test_repos/fastapi/applications.py |
| Item         |                   65    |             952 |              0 |                   100 | /mnt/data/spectrometer_system_audit/validation/test_repos/fastapi/routing.py      |
| Item         |                   65    |            1209 |              0 |                   100 | /mnt/data/spectrometer_system_audit/validation/test_repos/fastapi/applications.py |


**spectrometer_core**: 0 god-classes flagged out of 39 classes; avg risk 26.4%

Top risk classes (by score):
| class_name                |   antimatter_risk_score |   lines_of_code |   method_count |   touchpoint_overload | file_path                                                           |
|:--------------------------|------------------------:|----------------:|---------------:|----------------------:|:--------------------------------------------------------------------|
| DiscoveryEngine           |                   68.25 |             465 |              0 |                   100 | /mnt/data/spectrometer_system_audit/core/discovery_engine.py        |
| TreeSitterUniversalEngine |                   67.25 |             445 |              0 |                   100 | /mnt/data/spectrometer_system_audit/core/tree_sitter_engine.py      |
| GodClassDetector          |                   62.9  |             358 |              0 |                   100 | /mnt/data/spectrometer_system_audit/core/god_class_detector.py      |
| AtomExtractor             |                   60    |             300 |              0 |                   100 | /mnt/data/spectrometer_system_audit/core/atom_extractor.py          |
| GodClassDetectorLite      |                   59.8  |             296 |              0 |                   100 | /mnt/data/spectrometer_system_audit/core/god_class_detector_lite.py |

## 4) Evaluation (what’s working vs what’s not)

### What works today (in this environment)
- ✅ **Minimal analyzer runs end-to-end** (`legacy_main.py` → `core/universal_detector.py`), producing:
  - `results.json` (structured output)
  - `particles.csv` / `components.csv`
  - `report.md` with a Mermaid dependency summary
- ✅ **Truth extractor runs** and successfully finds developer-declared structure (at least via type hints + docs).
- ✅ Dependency extraction works well enough to compute high-level **layer-edge flow**.

### Critical blockers / defects surfaced by running the code
1) ❌ **Primary entrypoint (Learning Engine) is not runnable here**  
   - Hard dependency on `tree_sitter` + `tree_sitter_python` via `core/system_health.py`.
   - Plus a real runtime bug: missing `Tuple` import in `learning_engine.py` (NameError).

2) ❌ **God Class detector is currently unreliable as implemented**
   - It used `Path.walk()` (Python 3.12+), but the system health check only enforces Python 3.8+.  
   - Method counting regex uses `^` anchors without `re.MULTILINE`, so **method_count tends to be 0**, which cascades into incorrect risk scoring.

3) ⚠️ **Classification coverage is the main weakness in the minimal pipeline**
   - On `dddpy_real`: only **28.1%** particles get a non-Unknown type.
   - On `fastapi` fixture: only **23.8%** typed.
   - Most unknowns are functions (providers, tests, helpers) and common class types (exceptions, configs) that are not covered by patterns.

4) ⚠️ **Reported performance metrics are misleading**
   - Current `performance` block in `results.json` measures mainly stats generation time, not the full analysis runtime, resulting in unrealistic throughput numbers.


## 5) Implementation roadmap (next development steps)

### Phase 0 — Make the “definitive” pipeline runnable (non-negotiable)
- Fix runtime errors in `learning_engine.py` (e.g., missing imports).
- Provide a **clear dependency manifest**:
  - `pyproject.toml`/`requirements.txt` + optional extras for extra languages.
  - A one-command install path (or a Docker image).
- Add a **fallback mode**:
  - If `tree_sitter` is missing, do not abort; drop to the universal/regex engine with explicit “degraded mode” flag.

### Phase 1 — Unify the two worlds (tree-sitter engine + universal engine)
Right now you have two parallel pipelines. Standardize on one intermediate representation (IR):
- `Component` (id, name, type, confidence, layer, file span, RPBL, evidence)
- `Edge` (from_component, to_component, kind=import|call|inherit, weight)
- `RepoReport` (metrics, coverage, violations, artifacts)

Then:
- Make **tree-sitter-based extractor** produce the same IR.
- Make **universal detector** produce the same IR.
- Make diagrams/scoring consume ONLY the IR.

### Phase 2 — Raise classification coverage and reduce Unknowns
Concrete improvements that will move the needle immediately:
- Add first-class patterns for:
  - `Exception` / `DomainError`
  - `Provider` / `Dependency` (e.g., `get_*`, `provide_*`)
  - `Config` / `Settings`
  - `Test` / `Fixture` (or ignore test paths entirely)
- Expand function classification (currently very narrow: handle_/create_/validate_/execute_/process_).
- Use stronger signals beyond naming:
  - directory path conventions (`/domain/`, `/usecase/`, `/infra/`, `/presentation/`)
  - base classes / decorators
  - imports (e.g., fastapi router/depends, pydantic models)
- Make confidence non-constant by scoring evidence:
  - path match (strong)
  - name match (medium)
  - decorator/baseclass match (strong)
  - keyword/context match (weak)

### Phase 3 — Make scoring meaningful and reproducible
- Improve `truth_extractor.py` so the “golden truth” is richer than just type hints.
- Update scoring to support **equivalences** (e.g., RepositoryImpl counts as Repository) and **partial matches**.
- Ensure benchmark runners work **offline** on the included `validation/` repos (no cloning required).

### Phase 4 — Fix God Class detection so it can be trusted
- Replace regex-based class parsing with:
  - tree-sitter queries when available
  - a robust Python AST fallback for Python-only repos
- Fix method counting (re.MULTILINE) and dependency counting.
- Report both:
  - “size risk” (LOC, methods)
  - “responsibility spread” (touchpoints, imports)
  - “fan-in/out” (graph-based)

### Phase 5 — Productize
- Provide a single CLI:
  - `spectrometer analyze <path>`
  - `spectrometer truth <path>`
  - `spectrometer score <analysis.json> <truth.json>`
  - `spectrometer diagram <analysis.json>`
- Version the JSON schema and guarantee backward compatibility.
- Add CI:
  - run minimal mode tests without tree-sitter
  - run full mode tests in an image that has tree-sitter bindings installed
