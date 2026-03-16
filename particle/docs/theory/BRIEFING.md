# Collider Briefing: PROJECT_lechworld

> Generated 2026-03-04T09:42:29 | Collider 4.0.0 | 32613ms | Merkle `9a2890513e7b...`
> Project type: **ACTIVE_SPRINT** -- High velocity, expect churn. Orphan warnings are noise. Focus on integration quality.

## Identity
| Metric | Value |
|--------|-------|
| Domain | Finance/FinTech |
| Scale | 810 nodes, 5740 edges, 651 files, 169,166 lines |
| Languages | yaml, typescript, javascript, python |
| Age | 2025-08-12 -> 2026-03-04 (11 active days) |
| Commits | 216 total, 19.64/day |
| Contributors | bus factor 2: Lech(171), leolech14(45) |
| Grade | **C** (health **6.42**/10) |
| Intelligence | 0.968 (Sharp) |
| Theory coverage | 72.8% |

> Chemistry: *System shows no cross-signal anomalies.*

## Architecture

**STAR_HUB** topology -- Dominated by central hub 'cross_language' (Star Topology).

| Metric | Value | Meaning |
|--------|-------|---------|
| Components (b0) | 24 | Disconnected subgraphs |
| Cycle complexity (b1) | 4728 | Circular dependency paths |
| Euler characteristic | -4704 | Topological signature |
| Health signal | FRAGMENTED_DENSE | |
| Largest cluster | 96.2% | Monolith indicator |
| Centralization | 0.59 | 0=distributed, 1=single hub |
| Graph density | 0.0088 | Edge/node ratio |
| Knot score | 1.0 | 1.0=clean, 0=tangled |
| Bidirectional edges | 18 | Mutual dependencies |
| Communities | 405 | Detected clusters |

**Layer distribution:**
  infrastructure: 761 (94%)
  application: 20 (2%)
  domain: 15 (2%)
  unknown: 10 (1%)

**Edge composition:** imports: 3169 (55%) | exposes: 1530 (27%) | invokes: 518 (9%) | calls: 507 (9%) | instantiates: 16 (0%)

## Incoherence Decomposition (5D)

| Dimension | Score | Weight | Reading | What it measures |
|-----------|-------|--------|---------|-----------------|
| Structural | 0.187 | 0.25 | Excellent | Graph shape vs ideal |
| Teleological | 0.720 | 0.2 | High | Purpose alignment |
| Symmetry | 0.281 | 0.15 | Good | Doc-code balance |
| Boundary | 0.500 | 0.2 | Moderate | Layer separation |
| Flow | 0.496 | 0.2 | Moderate | Dependency direction |
| **TOTAL** | **0.432** | | **Health: 5.68/10** | |

**Entropy analysis** (information distribution):
  boundary: 0.211
  layer: 0.383
  lifecycle: 0.127
  role: 0.197
  state: 0.181

**Purpose clarity:** 0.133 | Alignment: WARNING | Uncertain nodes: 699 | Violations: 8
**RPBL profile:** R=5.0 P=5.0 B=5.0 L=5.0

## Evolution Timeline
- **2025-08-12**: Refinement (0 files, 5 commits, 1d)
- **2025-08-20 to 2025-08-24**: Refinement (0 files, 2 commits, 2d)
- **2025-10-12**: Refinement (0 files, 38 commits, 1d)
- **2025-10-21 to 2025-10-26**: Major build (1240 files, 169 commits, 6d)
- **2026-03-04**: Refinement (0 files, 2 commits, 1d)

**File age distribution:**
  90-180 days: 1240 files

## Mission Matrix
| Dimension | Score |
|-----------|-------|
| all_targets_met | 0.0  |
| overall | 87.5 ======== |
| target | 95.0 ========= |

## Health Breakdown
| Component | Score | Status |
|-----------|-------|--------|
| constraints | 10.0/10 | [##########] OK |
| dead_code | 2.0/10 | [##........] CRITICAL |
| entanglement | 8.0/10 | [########..] OK |
| purpose | 5.8/10 | [#####.....] WARN |
| rpbl_balance | 10.0/10 | [##########] OK |
| test_coverage | 5.0/10 | [#####.....] WARN |
| topology | 4.0/10 | [####......] CRITICAL |

## Top Findings
1. !!! [CRITICAL] **Dead code accumulation**: 65.5% of code is unreachable.
2. !!! [CRITICAL] **Frontend calls non-existent endpoint**: Frontend calls GET /api/analytics/notification but no backend route handles it. Runtime 404 expected.
3. !! [HIGH] **Purpose-field misalignment**: Global Q-score is 0.97 (Sharp), but alignment=WARNING, clarity=0.13, uncertain=87%.
4. !! [HIGH] **Topology: STAR_HUB**: Dominated by central hub 'cross_language' (Star Topology).
5. !! [HIGH] **Incoherence Functional**: Aggregate incoherence I(C) = 0.432 (health 5.7/10). Measures structural, teleological, symmetry, boundary, and flow coherence.
6. ! [MEDIUM] **Ecosystem discovery unavailable**: Stage 2.5 ecosystem discovery status: skipped.
7. ! [MEDIUM] **Node-Level Signal Convergence**: 610 of 810 nodes have 3+ converging negative signals (0 critical with 5+).

**Knowledge gaps** (query targets for deeper analysis):
  - [medium] The 'unknown' compartment has 810 unorganized nodes. What higher-level abstraction could group these into a coherent container hierarchy?
  - [low] Is '/Users/lech/PROJECTS_all/PROJECT_lechworld/PRODUCT/src/store/fix_hybrid_store.py:fix_hybrid_store' (Internal) truly unused, or is it invoked through a mechanism not captured by static analysis (reflection, dynamic import, plugin system)?
  - [low] Is '/Users/lech/PROJECTS_all/PROJECT_lechworld/PRODUCT/src/store/fix_index_careful.py:fix_index_store' (Internal) truly unused, or is it invoked through a mechanism not captured by static analysis (reflection, dynamic import, plugin system)?

## Start Reading Here
*Composite rank: PageRank(35%) + change frequency(30%) + bridge status(20%) + complexity(15%)*

| # | File | Score | Why |
|---|------|-------|-----|
| 1 | `Dashboard.tsx` | 0.30 | hotspot |
| 2 | `firebase.json` | 0.22 | hotspot |
| 3 | `functions/lechito-tools.ts` | 0.20 | bridge |
| 4 | `functions/flight-search.ts` | 0.20 | bridge |
| 5 | `src/pages/api/prices/index.ts` | 0.20 | bridge |
| 6 | `src/ui-algebra/generate-perfect-ui.ts` | 0.20 | bridge |
| 7 | `functions/error-handler.ts` | 0.20 | bridge |
| 8 | `functions/flight-price-monitor.ts` | 0.20 | bridge |
| 9 | `App.tsx` | 0.18 | hotspot |
| 10 | `smart-ai-agent.ts` | 0.18 | hotspot |

## Critical Nodes (Do Not Touch)
**Bridges** -- removing any of these disconnects the dependency graph:
- `functions/lechito-tools.ts:executeTool`
- `src/ui-algebra/generate-perfect-ui.ts:generateColorPalette`
- `src/ui-algebra/generate-perfect-ui.ts:generatePerfectUI`
- `functions/flight-price-monitor.ts:confirmPriceMonitorForUser`
- `src/pages/api/prices/index.ts:handler`
- `functions/flight-search.ts:performFlightSearch`
- `src/ui-algebra/generate-perfect-ui.ts:adjustBackgroundForContrast`
- `functions/error-handler.ts:createHttpsError`

**Coordinators** -- highest dependency fan-out:
- `scripts/performance-test.js:log`
- `src/store/store-selector.ts:useAppStore`
- `src/pages/api/prices/index.ts:handler`
- `src/hooks/use-toast.ts:toast`
- `src/hooks/use-toast.ts:useToast`

**Most influential** -- highest PageRank:
- `scripts/performance-test.js:log`
- `src/store/store-selector.ts:useAppStore`
- `src/config/validators.ts:sanitizeValue`
- `src/api/integration-tracker-api.ts:getHealthHistory`
- `scripts/performance-test.js:walkDir`

## Directory Stability Map

**VOLATILE** (active churn, expect changes):
  `scripts` -- stability 0.007, branching factor 41
  `src/services` -- stability 0.029, branching factor 32
  `functions` -- stability 0.033, branching factor 31
  `src/hooks` -- stability 0.060, branching factor 27
  `src/components/ui` -- stability 0.315, branching factor 16
**FRAGMENTED** (needs consolidation):
  `src/components/family` -- stability 0.366, branching factor 15
**STABLE** (settled, high confidence):
  `src/components/auth` -- stability 0.950
  `src/components/dashboard` -- stability 0.950
  `src/components/layout/floating-components` -- stability 0.950
  `src/config` -- stability 0.950
  `src/ui-algebra` -- stability 0.950
  `src/components/agent` -- stability 0.900
  `src/components/agentic` -- stability 0.900
  `src/components/intelligence` -- stability 0.900

Average stability: **0.573**

## Orphan Analysis

**528 orphans (65.2%)** -- static reachability only, NOT a deletion list.

**By IGT label:**
  CODE_STRUCTURAL_ORPHAN: 308 (58%)
  STANDALONE_DOC: 216 (41%)
  GOVERNANCE_DRIFT: 4 (1%)

**By directory (top 8):**
  `/Users/lech`: 528

Critical orphans (IGT): 312

## Complexity Profile

| Metric | Value |
|--------|-------|
| Avg complexity | 1.03 |
| Max complexity | 7 |
| High-complexity nodes | 0 |
| Halstead difficulty | 0.07 |
| Halstead est. bugs | 1.47 |
| Halstead effort | 27307.63 |
| Critical path length | 4 |
| Critical path cost | 768.0 |
| Dead code | 65.51% |
| RPBL coverage | 99.5% |

**Estimated cost by layer:**
  infrastructure: 68,889
  unknown: 1,707
  domain: 1,492
  application: 640

## Safety Warnings

1. **ORPHAN METRIC IS NOT A DELETION LIST.** 528 nodes (65.2%) are unreachable in the static graph. React lazy loading, dynamic imports, standalone scripts, and WIP code inflate this. Cross-reference with `file_boundaries[].created_ts` and `igt.directory_stability` before ANY deletion.
2. **API drift (55 items)** may reflect aspirational integrations. In ACTIVE_SPRINT codebases, check for service stubs before treating as errors.
3. **Purpose clarity 0.133** -- layer assignments may be unreliable. 699 of 806 nodes have uncertain purpose.

## Semantic Landscape

**use**(88) | **Price**(35) | **Data**(20) | **Member**(20) | **Status**(20) | **generate**(19) | **User**(19) | **Rate**(17) | **validate**(16) | **Miles**(16) | **check**(16) | **Config**(15) | **Limit**(14) | **Component**(14) | **Account**(13) | **Card**(13) | **Notification**(12) | **Firebase**(12) | **Auth**(12) | **Monitor**(12)

**Roles:** Internal: 739 | Utility: 15 | Store: 13 | Orchestrator: 11 | Service: 8 | Factory: 7 | Query: 5 | Asserter: 3

**Top atoms:** LOG.FNC.M: 449 | EXT.REACT.001: 122 | ORG.AGG.M: 75 | EXT.REACT.005: 61 | EXT.REACT.019: 45 | ORG.MOD.O: 14

## Contextome

- **0** documents inventoried
- **393** file-to-purpose mappings
- **136** symmetry seeds (doc-code links)
- Purpose coverage: **1.0%**

## Pipeline
- 29 stages executed (1.0.0-smoc)
- Analysis time: 32613ms
- OK: 30 | Warn: 1 | Fail: 0
- Slowest: Stage 6.7: Semantic Purpose (14060ms)
- Peak memory: 342MB

## Drill-Down Guide

Navigate `unified_analysis.json` by need:

| Need | Key | Size |
|------|-----|------|
| Signal convergence | `chemistry` | ~220KB |
| Per-file metadata | `file_boundaries` | ~255KB |
| Graph bottlenecks | `graph_analytics` | ~13KB |
| AI query targets | `gap_report.query_targets` | ~7KB |
| File-to-purpose map | `contextome.purpose_priors` | ~989KB |
| Per-node detail (57 fields) | `nodes[]` | ~2.7MB |
| Per-edge detail (12 fields) | `edges[]` | ~2.6MB |
| 28 viz views | `view_registry` | ~8KB |
| Orphan classification | `igt.classified_orphans` | ~159KB |
| Raw findings list | `compiled_insights.findings` | ~89KB |

**Pre-built diagnostic views** (use with Collider visualizer):
  `behavior`: How do behavioral types compare in quality?
  `boundaries`: Are boundary components well-defined?
  `centrality`: Which nodes control information flow?
  `clarity`: Which atom families are most self-documenting?
  `complexity`: Where are the large, complex components?
  `confidence`: How confident are we in each component?
  `convergence`: Where do multiple problems converge?
  `coupling`: How tightly coupled are components by tier?
  `debt`: Where is technical debt accumulating?
  `file_quality`: Which files have the healthiest code?
