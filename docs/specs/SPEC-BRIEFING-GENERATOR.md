# SPEC: Collider Briefing Generator (AI Delivery Layer)

**Status:** Engineering spec, ready for implementation
**Origin:** First real AI consumer test of Collider on a foreign codebase (PROJECT_lechworld, 810 nodes)
**Date:** 2026-03-04
**Author:** Claude Code (Opus 4.6) -- acting as Collider consumer, not builder
**Revision:** v2.1 -- hardened with honest performance metrics, scope limitations, and primary value proposition reframe

---

## Primary Value Proposition

Reduces AI agent orientation from 12+ tool calls to 1, with calibrated safety warnings that prevent catastrophic actions. Validated by the LechWorld incident where an agent nearly deleted founding infrastructure based on orphan metrics alone.

## Problem Statement

Collider's `unified_analysis.json` contains 42 top-level keys, ~10MB of data, and extraordinary analytical depth. An AI agent consuming this output spent 12+ tool calls excavating data, missed critical sections (temporal analysis, file boundaries, ai_consumer_summary), and nearly deleted founding infrastructure because the orphan classifier flagged 65% of a development codebase as CRITICAL dead code.

The analysis engine is complete. The delivery layer doesn't exist.

### The Numbers

| Metric | Value | Problem |
|--------|-------|---------|
| Total output size | ~10MB | AI reads the whole file |
| Top-level keys | 42 | No reading order |
| `nodes` array | 2.7MB, 57 fields/node | Dominated by raw data |
| `edges` array | 2.6MB | Dominated by raw data |
| `contextome` | 989KB, 393 purpose_priors | Massive but redundant for orientation |
| `ai_consumer_summary` | 4KB (0.04% of output) | The one AI-targeted section, buried |
| Schema documentation | 0 | Agent crashes on type mismatches |

**62% of the file is raw graph data (nodes + edges) that an AI agent should never read directly.**

## Core Requirement

When `collider full` runs, it should produce a **BRIEFING.md** file alongside the existing outputs. This file is the primary AI interface to Collider's analysis. It must be:

- Under 3,000 tokens (fits in one context window read)
- Self-contained (no need to read any other file to orient)
- Actionable (tells the agent what to do, not just what is)
- Safe (explicitly warns against destructive actions based on incomplete metrics)

## Output Structure (Post-Implementation)

```
collider_output/
├── BRIEFING.md              # NEW: 2-3K tokens. Read this first. Always.
├── collider_insights.json   # Existing: findings, grade, health
├── unified_analysis.json    # Existing: full 10MB dump
├── pipeline_report.json     # Existing: performance timing
└── collider_report.html     # Existing: visual report
```

---

## Complete Schema Reference

### All 42 Top-Level Keys

Grouped by AI consumer utility (HIGH = read in briefing, MEDIUM = drill-down, LOW = raw data/internal):

#### HIGH UTILITY -- Sources for BRIEFING.md

| Key | Type | Size | Contains |
|-----|------|------|----------|
| `compiled_insights` | dict | 89KB | `grade`, `health_score`, `health_components`, `findings[]`, `executive_summary`, `mission_matrix`, `navigation`, `theory_glossary` |
| `temporal_analysis` | dict | 3KB | `active_days`, `bus_factor`, `growth_timeline[]`, `hotspots[]`, `first_commit_date`, `last_commit_date`, `top_contributors[]`, `total_commits`, `age_quartiles` |
| `incoherence` | dict | 1.5KB | `i_struct`, `i_telic`, `i_sym`, `i_bound`, `i_flow`, `i_total`, `health_10`, `details.weights`, `details.terms` |
| `topology` | dict | 396B | `shape`, `betti_numbers.{b0,b1,euler_characteristic,health_signal}`, `description`, `visual_metrics.{centralization_score,largest_cluster_percent,density_score}` |
| `semantics` | dict | 717B | `domain_inference`, `top_concepts[].{term,count}` |
| `kpis` | dict | 996B | 30+ KPIs: `codebase_intelligence`, `orphan_count/percent`, `dead_code_percent`, `topology_shape`, `graph_density`, `knot_score`, `igt_stability_index` |
| `igt` | dict | 159KB | `classified_orphans[].{id,label,path,score,is_problem}`, `directory_stability{dir:{stability_index,status,branching_factor}}`, `avg_stability`, `critical_orphans_count` |
| `semantic_analysis` | dict | 142KB | `critical_nodes.{bridges[],coordinators[],influential[]}`, `centrality.{distribution,top_10_closeness[]}`, `role_distribution`, `entry_points[]` |
| `graph_analytics` | dict | 13KB | `bottlenecks[].{betweenness,pagerank,in_degree,out_degree,file,name}`, `pagerank_top[]`, `communities`, `communities_count` |
| `file_boundaries` | list | 255KB | Per-file: `{file,age_days,created_ts,modified_ts,code_ratio,cohesion,complexity_count,complexity_density,line_count,token_estimate,purpose,is_test,is_config,is_recent,is_stale}` |
| `api_drift` | dict | 31KB | Frontend-backend mismatches with `drift_items` |
| `stats` | dict | 351B | `total_files`, `total_lines`, `total_nodes`, `total_edges`, `languages[]` |
| `counts` | dict | 118B | `nodes`, `edges`, `files`, `orphans`, `entry_points`, `cycles` |
| `ai_consumer_summary` | dict | 4KB | `headline`, `data_utility_grade`, `heatmap`, `quick_assessment`, `recommendations` |

#### MEDIUM UTILITY -- Drill-Down Data

| Key | Type | Size | Contains |
|-----|------|------|----------|
| `chemistry` | dict | 219KB | Signal convergence analysis, convergence zones, compound scoring |
| `purpose_field` | dict | 3.2KB | `purpose_clarity` (float), `alignment_health`, `layer_purposes`, `god_classes`, `uncertain_mortals[]`, `violations` |
| `constraint_field` | dict | 3.5KB | Architecture detection, constraint validation |
| `gap_report` | dict | 7KB | `gaps[].{severity,gap_type,description,llm_query_hint}`, `query_targets[].{query,context}` |
| `contextome` | dict | 989KB | `doc_inventory`, `purpose_priors{}` (393 file→purpose maps), `symmetry_seeds[]`, `purpose_coverage` |
| `knots` | dict | 582B | `knot_score`, `bidirectional_edges`, `cycles_detected`, `sample_tangles[]` |
| `statistical_metrics` | dict | 960B | `complexity.{avg,max}`, `entropy.{boundary,layer,lifecycle,role,state}`, `halstead.{difficulty,bugs,effort}` |
| `coverage` | dict | 110B | `dead_code_percent`, `rpbl_coverage`, `type_coverage` |
| `rpbl_profile` | dict | 73B | `responsibility`, `purity`, `boundary`, `lifecycle` (each 0-10) |
| `performance` | dict | 401B | `critical_path_cost`, `critical_path_length`, `time_by_layer`, `hotspot_count` |
| `smart_ignore` | dict | 38KB | Directory classification decisions (explore/shallow/skip) |
| `view_registry` | dict | 7.7KB | 28 visualization views, each with `question` and `reading` |
| `classification` | dict | 443B | `by_intent`, `by_layer`, `by_role`, `by_state` |
| `distributions` | dict | 647B | Atom type, level, level_zone, ring, type distributions |

#### LOW UTILITY -- Raw Data / Internal

| Key | Type | Size | Contains |
|-----|------|------|----------|
| `nodes` | list | 2.7MB | 810 nodes, 57 fields each (atom, centrality, dimensions, layer, purpose, etc.) |
| `edges` | list | 2.6MB | 5,740 edges with confidence, type, weight, markov_weight |
| `files` | dict | 114KB | Per-file atom inventory (atom_count, functions, classes, imports) |
| `execution_flow` | dict | 76KB | Entry points, orphan lists, layer distribution (overlaps with kpis) |
| `orphans_list` | list | 2KB | Simple string list (use igt.classified_orphans instead) |
| `pipeline_performance` | dict | 7KB | Stage-by-stage timing and memory |
| `manifest` | dict | 1.4KB | `batch_id`, `merkle_root`, `pipeline.stages_executed[]`, `schema_version` |
| `meta` | dict | 265B | `analysis_time_ms`, `version`, `timestamp`, `deterministic` |
| `top_hubs` | list | 377B | Hub nodes with in_degree |
| `edge_types` | dict | 84B | calls/exposes/imports/instantiates/invokes counts |
| `encoding_report` | dict | 131B | Convergent tagging stats |
| `ranked_views` | list | 350B | View ranking by domain |
| `theory_completeness` | dict | 153B | Standard Model coverage percentages |
| `llm_enrichment` | dict | 94B | LLM enrichment status (usually not_applied) |
| `dependencies` | dict | 80B | External dependency analysis status |
| `auto_discovery` | dict | 119B | Auto-discovery metadata |
| `purpose_decomposition` | list | 2B | Usually empty |
| `warnings` | list | 2B | Usually empty |

### Critical Type Information

**Types that crashed the AI agent (and will crash others):**

```python
# These are NOT what you'd expect:
graph_analytics['communities']   # dict{str: int}, NOT list[dict]
semantic_analysis['centrality']  # dict{distribution: dict, top_10_closeness: list}, NOT dict{node_id: float}
incoherence['details']['terms']  # dict with sub-dicts, NOT flat scores
topology['visual_metrics']       # dict with 7 numeric keys, NOT nested
compiled_insights['findings']    # list[dict] with keys: category, description, severity, title
nodes[0]                         # dict with 57 keys (see full list below)

# Node field list (57 fields):
# atom, atom_family, base_classes, betweenness_centrality, boundary,
# call_chain_length, closeness_centrality, coherence_score, complexity,
# decorators, depth_from_entry, dimensions, discovery_method, docstring,
# effect, encoded_colors, end_line, file_path, id, in_degree, intent,
# is_bridge, is_coordinator, is_influential, kind, language_dim, layer,
# level, level_name, level_zone, lifecycle, lines_of_code, metadata,
# name, out_degree, pagerank, params, parent, pi2_confidence, pi2_purpose,
# pi4_confidence, pi4_purpose, purpose_entropy, reachable_from_entry,
# return_type, role, role_confidence, role_confidence_raw, rpbl,
# semantic_role, signature, start_line, state, symbol_kind, tier,
# topology_role, type

# Edge field list (12 fields):
# confidence, edge_type, encoded_colors, family, file_path, line,
# markov_weight, metadata, resolution, source, target, weight

# File boundary field list (31 fields):
# age_days, atom_count, atom_indices, blank_lines, char_count, classes,
# code_lines, code_ratio, cohesion, comment_lines, complexity_count,
# complexity_density, created_ts, extension, file, file_name,
# format_category, functions, is_config, is_empty, is_recent, is_stale,
# is_test, line_count, line_range, modified_date, modified_ts, purpose,
# size_bytes, size_kb, token_estimate
```

---

## BRIEFING.md Template

```markdown
# Collider Briefing: {project_name}

Generated: {meta.timestamp} | Collider {meta.version} | {meta.analysis_time_ms}ms

## Identity
- **Domain:** {semantics.domain_inference}
- **Scale:** {counts.nodes} nodes, {counts.edges} edges, {stats.total_files} files, {stats.total_lines} lines
- **Languages:** {stats.languages}
- **Age:** {temporal_analysis.first_commit_date} → {temporal_analysis.last_commit_date} ({temporal_analysis.active_days} active days, {temporal_analysis.total_commits} commits)
- **Contributors:** {temporal_analysis.bus_factor} bus factor ({temporal_analysis.top_contributors})
- **Grade:** {compiled_insights.grade} (health {compiled_insights.health_score}/10)
- **Intelligence:** {kpis.codebase_intelligence} ({kpis.codebase_interpretation})

## Architecture Shape
{topology.shape} topology. {topology.betti_numbers.b0} disconnected components,
{topology.betti_numbers.b1} cycle complexity. Largest cluster: {topology.visual_metrics.largest_cluster_percent}%.
Centralization: {topology.visual_metrics.centralization_score}. Health signal: {topology.betti_numbers.health_signal}.

## Incoherence Profile (5D)
| Dimension | Score | Weight | Reading |
|-----------|-------|--------|---------|
| Structural | {incoherence.i_struct} | {incoherence.details.weights.struct} | {interpretation_from_score} |
| Teleological | {incoherence.i_telic} | {incoherence.details.weights.telic} | {interpretation_from_score} |
| Symmetry | {incoherence.i_sym} | {incoherence.details.weights.sym} | {interpretation_from_score} |
| Boundary | {incoherence.i_bound} | {incoherence.details.weights.bound} | {interpretation_from_score} |
| Flow | {incoherence.i_flow} | {incoherence.details.weights.flow} | {interpretation_from_score} |
| **Total** | **{incoherence.i_total}** | | **Health: {incoherence.health_10}/10** |

Purpose clarity: {purpose_field.purpose_clarity}. Alignment: {purpose_field.alignment_health}.
Knot score: {knots.knot_score} ({knots.bidirectional_edges} bidirectional edges).

## Evolution Timeline
{grouped from temporal_analysis.growth_timeline, see epoch_grouping algorithm}
- **{date_range}**: {label} ({files_born} files, {commits} commits)

## Top 5 Things to Know
{from compiled_insights.findings, filtered: severity in [critical, high], deduplicated by category}
{additionally informed by gap_report.gaps if severity >= medium}
1. [{severity}] {title}: {description}
2. ...

## Start Reading Here
{composite ranking from graph_analytics.pagerank_top + temporal_analysis.hotspots + semantic_analysis.critical_nodes + file_boundaries.complexity_count}
1. **{file}** -- {why_it_matters} (PageRank: {pr}, changes: {n})
2. ...
(Top 10 files. See composite ranking algorithm below.)

## Do Not Touch (Graph Bridges)
{from semantic_analysis.critical_nodes.bridges}
- **{bridge_node}** -- removing this disconnects {n} components
{from semantic_analysis.critical_nodes.coordinators}
- **{coordinator_node}** -- coordinates {n} dependencies

## Volatile Directories (Active Churn)
{from igt.directory_stability, filtered to status == "VOLATILE"}
- `{dir}`: stability {stability_index} (branching factor {branching_factor})

## Stable Directories (Settled)
{from igt.directory_stability, filtered to status == "STABLE"}
- `{dir}`: stability {stability_index}

## Safety Warnings
- **Orphan count** ({kpis.orphan_count}, {kpis.orphan_percent}%) reflects static reachability only.
  IGT classified {igt.critical_orphans_count} as critical. Labels include CODE_STRUCTURAL_ORPHAN,
  STANDALONE_DOC, GOVERNANCE_DRIFT.
  DO NOT delete files based on orphan status alone.
  Cross-reference with file_boundaries[].created_ts and igt.directory_stability.
- **API drift** ({api_drift.drift_items} items) may reflect planned integrations, not bugs.
  Check for service stubs before treating as errors.
- **Purpose clarity** is {purpose_field.purpose_clarity} ({purpose_field.alignment_health}).
  {purpose_field.uncertain_count} nodes have uncertain purpose assignment.

## Semantic Concepts
{from semantics.top_concepts, top 10}
{term}: {count} | ...

## Health Breakdown
| Component | Score |
|-----------|-------|
{from compiled_insights.health_components as key-value table}

## Drill-Down Guide
To go deeper, read these keys from unified_analysis.json:
- **Chemistry signals**: `chemistry` (219KB) -- signal convergence analysis
- **File details**: `file_boundaries` (255KB) -- per-file age, complexity, cohesion
- **Graph structure**: `graph_analytics` (13KB) -- bottlenecks, PageRank, communities
- **Knowledge gaps**: `gap_report.query_targets` -- pre-written queries for LLM exploration
- **Contextome**: `contextome.purpose_priors` -- 393 file→purpose mappings
```

---

### Performance Metrics

| Metric | Value | Context |
|--------|-------|---------|
| Raw byte ratio | ~1,000:1 | Compares uncompressed JSON to dense Markdown. Inflated by JSON syntax overhead. |
| Gzip-adjusted ratio | ~140:1 | Fairer baseline: compressed JSON to Markdown. Still strong. |
| Categories covered | 24/24 (100% breadth) | Every analytical category mentioned. HIGH-utility categories retain ~50% of synthesized values. MEDIUM/LOW categories are pointer-only. |
| Token budget | ~2,000 tokens | Fits in a single LLM context read. |
| Orientation tool calls | 1 (vs. 12+ without) | **The real metric.** Validated by the LechWorld incident. |
| Catastrophic risk reduction | HIGH to LOW | Safety warnings prevent orphan-deletion disasters. |
| Information scope | Orientation only | NOT sufficient for targeted investigation, novel analysis, or validation. The Drill-Down Guide provides pointers for deeper work. |

**Scope: Orientation only.** The briefing provides sufficient information for an AI agent to orient itself and avoid catastrophic actions. It is NOT sufficient for: (a) targeted investigation of specific nodes or files; (b) novel analytical queries not anticipated by the generator; (c) validation of the briefing's own synthesized scores. For these tasks, the agent must read specific keys from unified_analysis.json as directed by the Drill-Down Guide. The briefing is the entry point, not the endpoint.

---

## Implementation

### Location

**File:** `particle/src/core/briefing_generator.py` (new module)
**Called from:** `particle/src/core/phases/output.py` (after unified_analysis.json is written)

The generator reads the completed `full_output` dict (same data that becomes `unified_analysis.json`) and renders the BRIEFING.md template. No new analysis needed -- all data already exists.

### Key Data Paths (Complete)

| Briefing Section | Source Key(s) | Type Info |
|-----------------|---------------|-----------|
| Identity - domain | `semantics['domain_inference']` | `str` |
| Identity - scale | `counts['nodes']`, `counts['edges']`, `stats['total_files']`, `stats['total_lines']` | `int` |
| Identity - languages | `stats['languages']` | `list[str]` |
| Identity - age | `temporal_analysis['first_commit_date']`, `temporal_analysis['last_commit_date']`, `temporal_analysis['active_days']` | `str`, `str`, `int` |
| Identity - contributors | `temporal_analysis['bus_factor']`, `temporal_analysis['top_contributors']` | `int`, `list[dict{name,commits}]` |
| Identity - grade | `compiled_insights['grade']`, `compiled_insights['health_score']` | `str`, `float` |
| Identity - intelligence | `kpis['codebase_intelligence']`, `kpis['codebase_interpretation']` | `float`, `str` |
| Architecture | `topology['shape']`, `topology['betti_numbers']`, `topology['visual_metrics']`, `topology['description']` | `str`, `dict`, `dict`, `str` |
| Incoherence | `incoherence['i_struct']` thru `incoherence['i_flow']`, `incoherence['i_total']`, `incoherence['health_10']`, `incoherence['details']['weights']` | all `float` |
| Purpose | `purpose_field['purpose_clarity']`, `purpose_field['alignment_health']`, `purpose_field['uncertain_count']` | `float`, `str`, `int` |
| Knots | `knots['knot_score']`, `knots['bidirectional_edges']` | `float`, `int` |
| Evolution | `temporal_analysis['growth_timeline']` | `list[dict{date,files_born,commits}]` |
| Top 5 | `compiled_insights['findings']` | `list[dict{category,description,severity,title}]` |
| Top 5 (supplement) | `gap_report['gaps']` | `list[dict{severity,gap_type,description,llm_query_hint}]` |
| Start Here | `graph_analytics['pagerank_top']` | `list[dict{betweenness,pagerank,file,name,in_degree,out_degree}]` |
| Start Here | `graph_analytics['bottlenecks']` | `list[dict]` (same schema as pagerank_top) |
| Start Here | `temporal_analysis['hotspots']` | `list[dict{change_count,last_changed,path}]` |
| Start Here | `semantic_analysis['critical_nodes']` | `dict{bridges:list[str], coordinators:list[str], influential:list[str]}` |
| Start Here | `file_boundaries` | `list[dict]` -- filter by `complexity_count`, `cohesion` |
| Do Not Touch | `semantic_analysis['critical_nodes']['bridges']` | `list[str]` (node IDs, format: "file:symbol") |
| Do Not Touch | `semantic_analysis['critical_nodes']['coordinators']` | `list[str]` |
| Volatile/Stable | `igt['directory_stability']` | `dict{dir_path: {stability_index:float, status:str, branching_factor:int}}` |
| Safety - orphans | `kpis['orphan_count']`, `kpis['orphan_percent']`, `igt['critical_orphans_count']` | `int`, `float`, `int` |
| Safety - API drift | `api_drift` | `dict` with drift item count |
| Safety - purpose | `purpose_field['purpose_clarity']`, `purpose_field['alignment_health']`, `purpose_field['uncertain_count']` | `float`, `str`, `int` |
| Concepts | `semantics['top_concepts']` | `list[dict{term:str, count:int}]` |
| Health | `compiled_insights['health_components']` | `dict{component:float}` |
| Meta | `meta['timestamp']`, `meta['version']`, `meta['analysis_time_ms']` | `str`, `str`, `int` |

### Composite "Start Here" Ranking

```python
def rank_start_here(full_output: dict) -> list[tuple[str, float, str]]:
    """Produce ordered list of files an AI should read first.

    Returns: [(file_path, score, reason), ...]
    """
    # Source 1: PageRank (graph importance)
    pagerank = {}
    for node in full_output.get('graph_analytics', {}).get('pagerank_top', []):
        file_path = node.get('file', '')
        if file_path:
            pagerank[file_path] = max(pagerank.get(file_path, 0), node.get('pagerank', 0))

    # Source 2: Hotspots (change frequency)
    hotspots = {}
    for h in full_output.get('temporal_analysis', {}).get('hotspots', []):
        hotspots[h['path']] = h['change_count']

    # Source 3: Bridges (structural importance)
    bridges = set()
    critical = full_output.get('semantic_analysis', {}).get('critical_nodes', {})
    for b in critical.get('bridges', []):
        # Bridge format is "file:symbol" -- extract file
        parts = b.rsplit(':', 1)
        if parts:
            bridges.add(parts[0] if len(parts) > 1 else b)

    # Source 4: Complexity (cognitive load)
    complexity = {}
    for fb in full_output.get('file_boundaries', []):
        complexity[fb['file']] = fb.get('complexity_count', 0)

    # Normalize each source to 0-1
    def normalize(d: dict) -> dict:
        if not d:
            return {}
        max_val = max(d.values())
        if max_val == 0:
            return {k: 0 for k in d}
        return {k: v / max_val for k, v in d.items()}

    pr_norm = normalize(pagerank)
    hs_norm = normalize(hotspots)
    cx_norm = normalize(complexity)

    # Composite score: pagerank(0.35) + hotspot(0.30) + bridge(0.20) + complexity(0.15)
    all_files = set(pr_norm) | set(hs_norm) | bridges | set(cx_norm)
    scores = {}
    reasons = {}
    for f in all_files:
        pr = pr_norm.get(f, 0)
        hs = hs_norm.get(f, 0)
        br = 1.0 if f in bridges else 0.0
        cx = cx_norm.get(f, 0)

        score = pr * 0.35 + hs * 0.30 + br * 0.20 + cx * 0.15
        scores[f] = score

        # Build reason string
        tags = []
        if pr > 0.5: tags.append("high PageRank")
        if hs > 0.5: tags.append("change hotspot")
        if br: tags.append("graph bridge")
        if cx > 0.5: tags.append("complex")
        reasons[f] = ", ".join(tags) if tags else "structural node"

    ranked = sorted(scores.items(), key=lambda x: -x[1])[:10]
    return [(f, s, reasons[f]) for f, s in ranked]
```

### Epoch Grouping for Evolution Timeline

```python
from datetime import datetime, timedelta

def group_timeline_epochs(growth_timeline: list[dict]) -> list[dict]:
    """Group daily entries into narrative epochs.

    Input:  [{'date': '2025-10-22', 'files_born': 300, 'commits': 50}, ...]
    Output: [{'date_range': 'Oct 22-26 2025', 'label': 'Foundation Sprint',
              'files_born': 1200, 'commits': 200}, ...]
    """
    if not growth_timeline:
        return []

    # Sort by date
    entries = sorted(growth_timeline, key=lambda x: x['date'])

    # Cluster by gaps > 7 days
    epochs = []
    current = [entries[0]]

    for entry in entries[1:]:
        prev_date = datetime.strptime(current[-1]['date'], '%Y-%m-%d')
        curr_date = datetime.strptime(entry['date'], '%Y-%m-%d')

        if (curr_date - prev_date).days > 7:
            epochs.append(current)
            current = [entry]
        else:
            current.append(entry)
    epochs.append(current)

    # Label each epoch
    result = []
    for i, epoch in enumerate(epochs):
        total_files = sum(e.get('files_born', 0) for e in epoch)
        total_commits = sum(e.get('commits', 0) for e in epoch)

        start = epoch[0]['date']
        end = epoch[-1]['date']
        date_range = start if start == end else f"{start} to {end}"

        # Determine label
        if i == 0 and total_files > 100:
            label = "Foundation"
        elif total_files > 100:
            label = "Major build"
        elif total_files > 30:
            label = "Feature expansion"
        elif total_files > 10:
            label = "Sprint"
        elif total_commits > total_files * 3:
            label = "Refinement"
        else:
            label = "Maintenance"

        result.append({
            'date_range': date_range,
            'label': label,
            'files_born': total_files,
            'commits': total_commits,
            'days': len(epoch)
        })

    return result
```

### Incoherence Interpretation

```python
def interpret_incoherence(score: float) -> str:
    """Convert incoherence score to human-readable interpretation."""
    if score < 0.2:
        return "Excellent -- well-coherent"
    elif score < 0.4:
        return "Good -- minor drift"
    elif score < 0.6:
        return "Moderate -- needs attention"
    elif score < 0.8:
        return "High -- significant incoherence"
    else:
        return "Critical -- fundamental misalignment"
```

### Safety Warning Generator

```python
def generate_safety_warnings(full_output: dict) -> list[str]:
    """Generate context-aware safety warnings."""
    warnings = []

    kpis = full_output.get('kpis', {})
    igt = full_output.get('igt', {})
    temporal = full_output.get('temporal_analysis', {})
    purpose = full_output.get('purpose_field', {})

    # Orphan warning (always include if > 20%)
    orphan_pct = kpis.get('orphan_percent', 0)
    if orphan_pct > 20:
        # Determine project type for calibrated warning
        active_days = temporal.get('active_days', 0)
        last_commit = temporal.get('last_commit_date', '')

        labels = {}
        for o in igt.get('classified_orphans', []):
            label = o.get('label', 'UNKNOWN')
            labels[label] = labels.get(label, 0) + 1

        label_str = ", ".join(f"{v} {k}" for k, v in sorted(labels.items(), key=lambda x: -x[1])[:3])

        warnings.append(
            f"Orphan count ({kpis.get('orphan_count', '?')}, {orphan_pct}%) reflects STATIC "
            f"reachability only. IGT labels: {label_str}. "
            f"DO NOT delete files based on orphan status alone. "
            f"Cross-reference with file_boundaries[].created_ts and igt.directory_stability."
        )

    # API drift warning
    api_drift = full_output.get('api_drift', {})
    drift_count = len(api_drift.get('drift_items', api_drift.get('items', [])))
    if drift_count > 10:
        warnings.append(
            f"API drift ({drift_count} items) may reflect planned integrations, "
            f"not bugs. Check for service stubs before treating as errors."
        )

    # Purpose clarity warning
    clarity = purpose.get('purpose_clarity', 1.0)
    if clarity < 0.5:
        warnings.append(
            f"Purpose clarity is {clarity:.3f} ({purpose.get('alignment_health', '?')}). "
            f"{purpose.get('uncertain_count', '?')} nodes have uncertain purpose. "
            f"Layer assignment may be unreliable for architecture decisions."
        )

    return warnings
```

---

## Follow-Up Specs (Separate Work Items)

### 1. Orphan-Temporal Cross-Reference
Join `igt.classified_orphans` with `file_boundaries[].created_ts` and `igt.directory_stability`.

The current labels from IGT are coarse:
- `CODE_STRUCTURAL_ORPHAN` (308 in LechWorld)
- `STANDALONE_DOC` (216)
- `GOVERNANCE_DRIFT` (4)

Produce fine-grained labels:
- `DEAD_LEGACY`: orphan + old (>180 days) + stable directory + never modified
- `WORK_IN_PROGRESS`: orphan + young (<30 days) + volatile directory
- `STANDALONE_SCRIPT`: orphan + is entry_point + has main/CLI pattern
- `DYNAMICALLY_LOADED`: orphan + React component + in routes/lazy patterns
- `TRULY_ORPHANED`: orphan + no temporal excuse + not a script

Data available:
```python
# For each orphan in igt['classified_orphans']:
orphan_path = orphan['path']

# Find its file_boundary entry:
fb = next(fb for fb in full_output['file_boundaries'] if fb['file'] == orphan_path)
age_days = fb['age_days']
is_recent = fb['is_recent']
is_stale = fb['is_stale']
created_ts = fb['created_ts']

# Find its directory stability:
dir_path = os.path.dirname(orphan_path)
dir_stability = igt['directory_stability'].get(dir_path, {})
stability_status = dir_stability.get('status', 'UNKNOWN')  # VOLATILE/UNBALANCED/STABLE

# Check if entry point:
is_entry = orphan_path in set(full_output.get('execution_flow', {}).get('entry_points', []))
```

### 2. SCHEMA.md Auto-Generation
Generate type documentation for every top-level key in unified_analysis.json.

Available now from the schema dump (this spec already contains the reference):
- 42 top-level keys with types, sizes
- Nested key structures
- Per-element schemas for lists (nodes: 57 fields, edges: 12 fields, file_boundaries: 31 fields)

Implementation: Walk the `full_output` dict recursively, output markdown table per key.
Add `# Used by BRIEFING.md` annotations for keys in the data paths table above.

### 3. Severity Calibration by Project Type

Infer project type from existing signals (no new analysis needed):

```python
def infer_project_type(full_output: dict) -> str:
    """Infer project lifecycle stage from Collider signals."""
    temporal = full_output.get('temporal_analysis', {})
    kpis = full_output.get('kpis', {})
    igt = full_output.get('igt', {})

    active_days = temporal.get('active_days', 0)
    commits_per_day = temporal.get('commits_per_day', 0)
    last_commit = temporal.get('last_commit_date', '')
    stability = igt.get('avg_stability', 0.5)
    orphan_pct = kpis.get('orphan_percent', 0)

    # Days since last commit
    from datetime import datetime
    try:
        days_since = (datetime.now() - datetime.strptime(last_commit, '%Y-%m-%d')).days
    except:
        days_since = 999

    if days_since < 30 and commits_per_day > 5:
        return "ACTIVE_SPRINT"
    elif days_since < 90 and active_days > 30:
        return "ACTIVE_DEVELOPMENT"
    elif stability > 0.7 and orphan_pct < 20:
        return "MATURE_PRODUCTION"
    elif days_since > 180:
        return "LEGACY"
    else:
        return "EVOLVING"
```

Calibration rules:
- `ACTIVE_SPRINT`: Downgrade orphan severity (code being wired), upgrade API drift severity
- `ACTIVE_DEVELOPMENT`: Treat orphans as MEDIUM not CRITICAL
- `MATURE_PRODUCTION`: Orphans are genuinely suspicious, API drift is a bug
- `LEGACY`: Everything is informational, focus on "what can be removed"

### 4. Diff Mode

`collider diff run1.json run2.json` → delta report.

Key comparison points:
- `manifest.merkle_root` -- fast equality check (no diff needed if same)
- `counts.*` -- node/edge/orphan deltas
- `kpis.*` -- all KPI deltas
- `incoherence.*` -- 5D score changes
- `compiled_insights.grade` -- grade change
- `compiled_insights.health_score` -- health change
- `topology.shape` -- topology change
- `igt.directory_stability` -- per-directory stability changes
- New/removed files via `file_boundaries[].file` set difference
- New/resolved findings via `compiled_insights.findings[]` comparison

---

## Origin: The LechWorld Test

### What Happened

An AI agent (Claude Code, Opus 4.6) ran `collider full` on PROJECT_lechworld (810 nodes, TypeScript/React, Firebase backend). The agent:

1. Read only `kpis` and `execution_flow` initially (6 of 42 keys)
2. Took the orphan count (528, 65.2%) at face value as CRITICAL dead code
3. Started deleting files -- including founding infrastructure from Aug 2025
4. Was stopped by the user
5. Then discovered `temporal_analysis`, `file_boundaries`, `igt`, `ai_consumer_summary`, `compiled_insights`, `semantic_analysis`, `incoherence`, `chemistry` -- all of which contained the information needed to avoid the mistake
6. Produced a correct diagnosis once it found the data: "well-structured (I_struct=0.15) but purpose-scattered (I_telic=0.72)"

### What the Agent Got Right (Proving Collider Works)
- Identified the domain as Finance/FinTech from semantic concepts
- Traced the 5-day sprint (Oct 22-26, 2025) from temporal data
- Found the bridge nodes (lechito-tools, generate-perfect-ui, flight-price-monitor)
- Mapped directory stability correctly (scripts/ volatile, auth/ stable)
- Recognized the 55 API drift items as aspirational integrations, not bugs
- Used incoherence decomposition to make a precise diagnosis

### What the Agent Got Wrong (Proving the Delivery Layer is Missing)
- Nearly destroyed working code based on orphan metric alone
- Spent 12+ turns on data excavation instead of reading a briefing
- Never found the `ai_consumer_summary` until explicitly told to look
- Wrote Python one-liners that crashed on type mismatches (no schema)
- Had to be corrected by the user: "this is an ongoing development codebase"

### The Feedback (Verbatim Scoring)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Data richness | 10/10 | Nothing else comes close |
| Analytical depth | 9/10 | Incoherence, chemistry, IGT are unique |
| AI consumability | 3/10 | Brilliant data, terrible packaging |
| Actionability | 4/10 | Findings lack context, severity uncalibrated |
| Documentation | 2/10 | No schema, no reading guide, no type hints |
| Paradigm novelty | 10/10 | Standard Model of Code is genuinely new |

### What's Paradigm-Shifting (From AI Consumer Perspective)
1. **Incoherence decomposition** (5 independent dimensions) -- no other tool does this
2. **Chemistry / signal convergence** -- treating code signals as compounds
3. **File boundaries with temporal data** -- evolution history per file
4. **Directory stability index (IGT)** -- volatile vs stable at directory level
5. **Contextome** -- 2,674 deterministic signals, 99.5% purpose coverage
6. **Topology via Betti numbers** -- algebraic topology on dependency graphs
7. **Purpose field** -- per-node purpose inference (pi2_purpose, pi4_purpose) with confidence scores
8. **Gap report** -- AI-ready query targets with pre-written LLM hints

---

## Appendix: Response from Architecture Reviewer

The architecture reviewer (Claude Opus 4.6, different session) validated all findings and added:

- **Separate files, not layers:** BRIEFING.md should be its own file, not a section of the JSON. AI agents load the whole file to find one section -- separate files let them read the briefing first, then selectively load the full dump.
- **The "start here" data exists in the wrong keys:** `navigation.start_here` points to test files (execution entry points), but actual reading entry points are in hotspots + bridges + centrality. A composite ranking function (30 lines) would fix this.
- **Diff mode closes the loop:** Turns Collider from a snapshot tool into a development loop tool. Change code → run Collider → see delta → decide next change.
- **Project-type inference:** Collider already computes enough to distinguish active-development from mature-production from legacy. Severity should be `f(raw_signal, project_context)`.

The reviewer's conclusion: "Items 1-3 require no new analysis capabilities. They're packaging. That's the point."

---

## Appendix: Key Count Reconciliation

Early estimates said "60+ keys." The actual count is **42 top-level keys**. The confusion arose because:
- Sub-keys (e.g., `kpis` has 30+ fields) were being counted as separate keys
- The `igt.directory_stability` dict has 75 directory entries, each with 3 sub-keys
- `contextome.purpose_priors` has 393 entries
- `nodes` array has 810 items, each with 57 fields

The real problem isn't key count -- it's that **6.3MB of the 10MB output (nodes + edges + contextome) is raw data** that should be accessed selectively, not loaded whole.
