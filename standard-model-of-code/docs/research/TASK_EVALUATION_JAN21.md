# Task Evaluation: Jan 21, 2026 Research Session

> **Evaluator:** Based on research findings, theory alignment, and implementation feasibility
> **Context:** 21 tasks emerged from orphan taxonomy discovery and centrality research
> **Validation:** External research confirms priorities (see §Confidence Validation below)

---

## Evaluation Matrix

| # | Task | Useful | Align | Priority | Risk | Rationale |
|---|------|--------|-------|----------|------|-----------|
| **IMMEDIATE** |
| 1 | Disconnection taxonomy | **10** | **10** | **P0** | Low | Core theory fix. "Orphan" is demonstrably wrong (9% true dead code). |
| 2 | Add betweenness_centrality | 8 | 9 | P1 | Low | Research-backed (Zimmermann/Nagappan). 2 lines of code. |
| 3 | Add PageRank | 8 | 9 | P1 | Low | Research-backed. Identifies influential nodes. 2 lines. |
| 4 | Delete 11 dead code nodes | 6 | 7 | P2 | Med | Requires manual review. Small impact. |
| 5 | Fix test/config false positives | 9 | 9 | **P0** | Low | 16 nodes misclassified. 5 lines of code. |
| **MEDIUM TERM** |
| 6 | JS→JS edge detection | 9 | 8 | P1 | Med | Eliminates 68 false orphans (59%). Needs JS parser. |
| 7 | Class instantiation tracking | 8 | 8 | P1 | Med | Eliminates 15 false orphans. Tree-sitter query. |
| 8 | Tree-sitter scope analysis | 9 | **10** | P1 | Med | Direct theory implementation (Interface Surface §8). |
| 9 | Evolvability formula | 7 | 9 | P2 | High | No validated formula yet. Research-first. |
| 10 | Interface surface detection | 8 | **10** | P2 | Med | Depends on #8. Theory-aligned. |
| **RESEARCH** |
| 11 | Hubs vs bugs correlation | 8 | 8 | P2 | Low | Validation study. Git + graph analysis. |
| 12 | Topology predicts change | 9 | 9 | P2 | Low | Validates core thesis. High theory value. |
| 13 | Neutral network size | 6 | 7 | P3 | High | Highly speculative. No clear method. |
| 14 | NST-SMC mapping | 7 | 8 | P3 | Low | Documentation task. Cross-reference. |
| **VISUALIZATION** |
| 15 | Disconnection panel | 9 | 9 | P1 | Low | Makes #1 visible. High user value. |
| 16 | Color by disconnection type | 8 | 8 | P1 | Low | Standard viz encoding. |
| 17 | WHY tooltip | 9 | 9 | P1 | Low | Key UX improvement. Shows "why" not "that". |
| 18 | Centrality heatmap | 7 | 7 | P2 | Med | Nice-to-have. Depends on #2-3. |
| **DOCUMENTATION** |
| 19 | Update MODEL.md | 8 | **10** | P1 | Low | Theory must match implementation. |
| 20 | Update schema JSON | 8 | 9 | P1 | Low | Schema must match implementation. |
| 21 | Update COLLIDER.md | 7 | 8 | P2 | Low | User-facing docs. |

---

## Priority Summary

### P0 - URGENT (Do Now)
| # | Task | Why Urgent |
|---|------|------------|
| 1 | Disconnection taxonomy | **Core theory is wrong**. Every analysis produces misleading "orphan" labels. |
| 5 | Fix test/config false positives | Quick win. 5 lines eliminates 16 false positives. |

### P1 - HIGH (Do This Week)
| # | Task | Dependency |
|---|------|------------|
| 2 | Betweenness centrality | None |
| 3 | PageRank | None |
| 6 | JS edge detection | None |
| 7 | Class instantiation | None |
| 8 | Tree-sitter scope | None |
| 15 | Disconnection panel | After #1 |
| 16 | Color by type | After #1 |
| 17 | WHY tooltip | After #1 |
| 19 | Update MODEL.md | After #1 |
| 20 | Update schema JSON | After #1 |

### P2 - MEDIUM (This Month)
| # | Task | Blocker |
|---|------|---------|
| 4 | Delete dead code | Manual review needed |
| 9 | Evolvability formula | No validated formula |
| 10 | Interface surface | Depends on #8 |
| 11 | Hubs vs bugs | Git analysis setup |
| 12 | Topology predicts change | Historical data needed |
| 18 | Centrality heatmap | After #2-3 |
| 21 | Update COLLIDER.md | After implementation |

### P3 - LOW (Backlog)
| # | Task | Reason |
|---|------|--------|
| 13 | Neutral network size | Speculative, no method |
| 14 | NST-SMC mapping | Pure documentation |

---

## Recommended Execution Order

```
PHASE 1: Fix the Theory (Day 1)
├── #1 Disconnection taxonomy implementation
├── #5 Test/config false positive fix
├── #19 Update MODEL.md
└── #20 Update schema JSON

PHASE 2: Add Centrality (Day 2)
├── #2 Betweenness centrality
├── #3 PageRank
└── Tests + validation

PHASE 3: Visualization (Day 3)
├── #15 Disconnection panel
├── #16 Color by type
└── #17 WHY tooltip

PHASE 4: Edge Detection (Week 2)
├── #6 JS→JS edges
├── #7 Class instantiation
└── Re-run analysis, validate orphan reduction

PHASE 5: Tree-sitter (Week 3)
├── #8 Scope analysis
└── #10 Interface surface (if #8 succeeds)

PHASE 6: Validation Research (Ongoing)
├── #11 Hubs vs bugs
├── #12 Topology predicts change
└── Document findings

PHASE 7: Cleanup (As Needed)
├── #4 Delete dead code
├── #18 Centrality heatmap
├── #21 COLLIDER.md update
└── #9 Evolvability (if research supports)
```

---

## Risk Analysis

### High Risk Tasks
| Task | Risk | Mitigation |
|------|------|------------|
| #9 Evolvability formula | No validated formula exists | Research-first, don't implement prematurely |
| #13 Neutral network size | Highly speculative | Keep as research question, not task |
| #6 JS edge detection | Complexity of JS import variants | Start with simple `import` regex, iterate |

### Dependencies
```
#1 ──┬── #15, #16, #17 (viz depends on taxonomy)
     └── #19, #20 (docs depend on taxonomy)

#2, #3 ── #18 (heatmap needs centrality data)

#8 ── #10 (interface detection needs scope analysis)
```

### What Could Block Progress
1. **Tree-sitter locals.scm availability** - Python grammar doesn't ship with it (use Helix's)
2. **JS parser choice** - May need tree-sitter-javascript or regex fallback
3. **Schema migration** - Adding `disconnection` property may break consumers

---

## Conclusion

**The single most important task is #1 (Disconnection Taxonomy)** because:
1. It fixes a fundamental theory error
2. It's documented and specified (ORPHAN_TAXONOMY.md)
3. It unblocks 6 other tasks (#15-17, #19-20, and enables proper #4)
4. It demonstrates that SMC theory evolves through research

**Quick wins for immediate impact:**
- #5 (5 lines) + #2-3 (4 lines total) = 3 meaningful improvements in <1 hour

**Defer:**
- #9, #13 - Not ready for implementation
- #14 - Pure documentation, do when convenient

---

## Confidence Validation (External Research)

To validate our internal evaluation, we queried external research sources (Perplexity Sonar API) on three key questions.

### Research Query 1: Static Analysis Feature Priorities

**Question:** "Among these four static analysis features, which aligns most directly with best practices: (a) better dead code vs entry point classification, (b) network centrality metrics, (c) evolvability scoring, (d) interface surface detection?"

**Finding:**
> "Among your four options, **better classification of unreachable/dead code vs entry points vs test fixtures** aligns most directly with established best practices and is likely to have the highest initial impact for tool adoption."

**Relevance:** Confirms #1 (Disconnection Taxonomy) is industry priority. Other features are valid but less mature.

---

### Research Query 2: Network Centrality in Software

**Question:** "Does research support using betweenness centrality and PageRank in software dependency graphs?"

**Finding:**
> Research by Zimmermann, Nagappan et al. found "binaries with high dependency between them are more failure-prone." Betweenness centrality successfully identifies "bridge" components. However, "relatively limited penetration in commercial tools."

**Relevance:** Confirms #2-3 (centrality metrics) are research-backed but implementation is ahead of commercial practice. Valid P1 priority.

---

### Research Query 3: Dead Code False Positives

**Question:** "What are the main causes of false positives in dead code detection?"

**Finding:**
> Main causes match our 7-type taxonomy exactly:
> - **Reflection/dynamic invocation** → our `dynamic_target`
> - **Framework lifecycle methods** → our `framework_managed`
> - **Entry points** → our `entry_point`
> - **Test fixtures** → our `test_entry`
> - **Cross-language calls** → our `cross_language`
>
> Industry acknowledges the problem is "largely unsolved."
> **Meta's SCARF approach:** Accept false negatives to avoid false positives (same philosophy as our taxonomy).

**Relevance:** Our 7-type taxonomy matches documented false positive causes exactly. This is not novel theory - it's systematizing known problems.

---

### Final Verdict

**#1 (Disconnection Taxonomy) is CONFIRMED P0** because:

| Criterion | Evidence |
|-----------|----------|
| Reduces false positives | Industry's top priority for adoption |
| Addresses unsolved problem | Dead code false positives are "largely unsolved" |
| Matches production approach | Meta's SCARF uses similar philosophy |
| Taxonomy validated | Our 7 types match documented false positive causes |
| Implementation ready | ORPHAN_TAXONOMY.md has full spec |
| Unblocks other work | Enables #15-17 (viz), #19-20 (docs), proper #4 |

**Confidence Level:** HIGH (external research validates internal analysis)

---

## Step-by-Step Task Validation

### Task #1: Disconnection Taxonomy

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Read `ORPHAN_TAXONOMY.md` | Understand 7-type classification |
| 2 | Locate `full_analysis.py:705-735` | Find current orphan detection |
| 3 | Implement `classify_disconnection()` | Function returns `{reachability_source, connection_gap, isolation_confidence, suggested_action}` |
| 4 | Add `disconnection` property to node schema | Each orphan node has new property |
| 5 | Run on Collider itself | `./collider full . --output .collider` |
| 6 | Verify 116 orphans now classified | Check `output_llm-oriented.json` for `disconnection` field |
| 7 | Validate distribution matches research | ~68 cross_language, ~16 test_entry, ~15 framework_managed, ~11 unreachable |

**Done when:** `grep -c "reachability_source" output_llm-oriented.json` returns 116

---

### Task #2: Add betweenness_centrality

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Locate Stage 7 in `full_analysis.py` | Where topology_role is computed |
| 2 | Add `betweenness = nx.betweenness_centrality(G)` | NetworkX already imported |
| 3 | Add to node: `node['betweenness_centrality'] = betweenness.get(node_id, 0)` | |
| 4 | Run on Collider | |
| 5 | Verify top hub has high betweenness | `layout.js::get` should be near top |

**Done when:** `jq '.nodes[] | select(.betweenness_centrality > 0.1)' unified_analysis.json` returns results

---

### Task #3: Add PageRank

| Step | Action | Verification |
|------|--------|--------------|
| 1 | After #2, add `pagerank = nx.pagerank(G)` | Only for directed graphs |
| 2 | Add to node: `node['pagerank'] = pagerank.get(node_id, 0)` | |
| 3 | Run on Collider | |
| 4 | Verify influential nodes rank high | Entry points should have higher PageRank |

**Done when:** `jq '.nodes | sort_by(-.pagerank) | .[0:5]' unified_analysis.json` shows meaningful ranking

---

### Task #4: Delete 11 Dead Code Nodes

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need taxonomy to identify true dead code |
| 2 | Extract nodes where `reachability_source == "unreachable"` | Should be ~11 |
| 3 | Manual review each | Confirm no dynamic/reflection callers |
| 4 | Delete confirmed dead code | Git commit each removal |
| 5 | Re-run Collider | Orphan count should drop |

**Done when:** `disconnection.reachability_source == "unreachable"` returns 0 nodes

---

### Task #5: Fix Test/Config False Positives

| Step | Action | Verification |
|------|--------|--------------|
| 1 | In `classify_disconnection()`, add test file detection | `if 'test_' in file_path or 'conftest' in file_path` |
| 2 | Return `reachability_source = 'test_entry'` for matches | |
| 3 | Add config file detection | `if file_path.endswith('.yaml') or 'config' in file_path` |
| 4 | Run on Collider | |
| 5 | Verify 16 nodes now classified as test_entry | Not orphan |

**Done when:** `jq '[.nodes[] | select(.disconnection.reachability_source == "test_entry")] | length'` returns >= 16

---

### Task #6: JS→JS Edge Detection

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Locate `edge_extractor.py` | Current edge detection |
| 2 | Add JS import regex: `import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"]` | |
| 3 | Add JS require regex: `require\(['"]([^'"]+)['"]\)` | |
| 4 | Create edges from imports | Source file → target module |
| 5 | Run on Collider | |
| 6 | Check orphan reduction | Should drop from 68 to near 0 cross_language |

**Done when:** `jq '[.nodes[] | select(.disconnection.reachability_source == "cross_language")] | length'` < 10

---

### Task #7: Class Instantiation Tracking

| Step | Action | Verification |
|------|--------|--------------|
| 1 | In `edge_extractor.py`, add pattern for `ClassName()` | |
| 2 | Create edge: caller → class definition | |
| 3 | Specifically handle dataclasses | `@dataclass` decorated classes |
| 4 | Run on Collider | |
| 5 | Verify 15 framework_managed nodes now have incoming edges | |

**Done when:** Dataclass nodes in `types.py` have `in_degree > 0`

---

### Task #8: Tree-sitter Scope Analysis

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Download Python `locals.scm` from Helix | Official grammar lacks it |
| 2 | Create `scope_analyzer.py` | New module |
| 3 | Parse `@local.scope` captures | function, class, module boundaries |
| 4 | Parse `@local.definition` captures | What's defined in scope |
| 5 | Parse `@local.reference` captures | What crosses scope boundaries |
| 6 | Test on sample Python file | |
| 7 | Integrate with `tree_sitter_engine.py` | |

**Done when:** Can extract scope boundaries from any Python file

---

### Task #9: Evolvability Formula

| Step | Action | Verification |
|------|--------|--------------|
| 1 | **RESEARCH FIRST** - No implementation yet | |
| 2 | Review Wagner/Kirschner papers | Biological evolvability metrics |
| 3 | Correlate topology_role with git history | Do leaves change more easily? |
| 4 | Propose candidate formula | Document in research/ |
| 5 | Validate on multiple codebases | |
| 6 | Only implement if research supports | |

**Done when:** `docs/research/EVOLVABILITY_METRICS.md` has validated formula

---

### Task #10: Interface Surface Detection

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #8 first | Needs scope analysis |
| 2 | Define "interface" using scope data | What's visible outside scope |
| 3 | Compute interface_surface metric | Count of external-facing symbols |
| 4 | Add to node properties | |
| 5 | Validate against known APIs | Public functions should score higher |

**Done when:** `node.interface_surface` correlates with actual API surface

---

### Task #11: Hubs vs Bugs Correlation

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Extract git blame for all files | `git log --follow --oneline` |
| 2 | Identify bug-fix commits | Commits with "fix", "bug", "issue" |
| 3 | Map commits to nodes | Which nodes changed in bug fixes |
| 4 | Correlate with betweenness_centrality | |
| 5 | Document findings | `docs/research/HUBS_VS_BUGS.md` |

**Done when:** Statistical correlation (positive or negative) documented with p-value

---

### Task #12: Topology Predicts Change

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Track current topology_role for all nodes | Baseline |
| 2 | Make changes over time | Normal development |
| 3 | Record which changes succeed/fail | Build breaks, test failures |
| 4 | Correlate with topology_role | Do leaf changes succeed more? |
| 5 | Document findings | |

**Done when:** Can state "X topology_role has Y% change success rate" with evidence

---

### Task #13: Neutral Network Size

| Step | Action | Verification |
|------|--------|--------------|
| 1 | **DEFER** - Highly speculative | |
| 2 | Research what "equivalent implementations" means | |
| 3 | Define measurement method | |
| 4 | If method found, implement | |

**Done when:** Method exists OR task reclassified as "not measurable"

---

### Task #14: NST-SMC Mapping

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Read NST elements documentation | |
| 2 | Read SMC atoms documentation | |
| 3 | Create mapping table | NST element → SMC atom |
| 4 | Document in `docs/research/NST_SMC_MAPPING.md` | |

**Done when:** Mapping document exists with rationale for each pair

---

### Task #15: Disconnection Panel

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need taxonomy data |
| 2 | Locate visualization code | `src/core/viz/assets/` |
| 3 | Add panel HTML | Sidebar showing disconnection groups |
| 4 | Group nodes by `reachability_source` | 7 sections |
| 5 | Add counts per group | |
| 6 | Make clickable to highlight nodes | |

**Done when:** Panel visible in HTML output with correct groupings

---

### Task #16: Color by Disconnection Type

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need taxonomy data |
| 2 | Define color palette | Per ORPHAN_TAXONOMY.md spec |
| 3 | Add to visualization | `getNodeColor()` function |
| 4 | Test all 7 types have distinct colors | |

**Done when:** Visual inspection shows 7 distinct colors for disconnected nodes

---

### Task #17: WHY Tooltip

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need taxonomy data |
| 2 | Locate tooltip code | `src/core/viz/assets/` |
| 3 | Add `suggested_action` to tooltip | From disconnection property |
| 4 | Show `reachability_source` explanation | Human-readable reason |
| 5 | Test by hovering on disconnected nodes | |

**Done when:** Tooltip shows "Test fixture - pytest invokes" not just "orphan"

---

### Task #18: Centrality Heatmap

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #2-3 first | Need centrality data |
| 2 | Add color scale for betweenness | Low (blue) → High (red) |
| 3 | Add toggle in control bar | Switch between role color and centrality color |
| 4 | Test visualization | High-centrality nodes visually prominent |

**Done when:** Heatmap mode available in visualization controls

---

### Task #19: Update MODEL.md

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need final taxonomy |
| 2 | Locate `docs/MODEL.md` | Theory document |
| 3 | Add `disconnection` property specification | Under node properties section |
| 4 | Document 7 reachability_source types | |
| 5 | Update topology_role section | Note orphan is deprecated |

**Done when:** MODEL.md reflects implemented `disconnection` property

---

### Task #20: Update Schema JSON

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #1 first | Need final taxonomy |
| 2 | Locate `schema/` directory | Schema definitions |
| 3 | Add `disconnection` object to node schema | |
| 4 | Define all properties with types | |
| 5 | Validate existing outputs against new schema | |

**Done when:** `jsonschema validate output.json schema.json` passes

---

### Task #21: Update COLLIDER.md

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Complete #2-3 first | Need centrality implementation |
| 2 | Locate `docs/COLLIDER.md` | User-facing docs |
| 3 | Add centrality metrics to output documentation | |
| 4 | Add disconnection taxonomy explanation | |
| 5 | Update examples | |

**Done when:** User can understand new features from COLLIDER.md alone

---

## AI Validation (Gemini 2.5 Pro)

Validated via `analyze.py` on Jan 21, 2026:

### Executive Summary (AI)

> "This is an exceptionally well-crafted and thorough task evaluation document. The author has demonstrated a mature understanding of software project management, risk analysis, and technical planning. The priorities are logical, driven by a clear strategic goal: fixing a foundational flaw in the model's theory (Task #1) and then building upon that corrected foundation."
>
> "I would confidently approve this plan for execution."

### Validation Results

| # | Task | Priority | Steps | AC | Gaps |
|---|------|----------|-------|----|----|
| 1 | Disconnection taxonomy | **Justified** | Excellent | Excellent | Minor: add schema migration plan |
| 2 | Betweenness centrality | **Justified** | Excellent | Good | Minor: benchmark performance |
| 3 | PageRank | **Justified** | Excellent | Good | None |
| 4 | Delete dead code | **Justified** | Excellent | Excellent | None |
| 5 | Test/config fix | **Justified** | Good | Good | None |
| 6 | JS edge detection | **Justified** | Good | Excellent | None |
| 7 | Class instantiation | **Justified** | Good | Good | **Major: needs symbol resolution** |
| 8 | Tree-sitter scope | **Justified** | Excellent | Good | None |
| 9 | Evolvability formula | **Justified** | Excellent | Excellent | None |
| 10 | Interface surface | **Justified** | Excellent | Good | None |
| 11 | Hubs vs bugs | **Justified** | Good | Excellent | None |
| 12 | Topology predicts | **Justified** | Challenging | Ambitious | Gap: effort underestimated |
| 13 | Neutral network | **Justified** | Excellent | Excellent | None |
| 14 | NST-SMC mapping | **Justified** | Excellent | Excellent | None |
| 15 | Disconnection panel | **Justified** | Excellent | Excellent | None |
| 16 | Color by type | **Justified** | Excellent | Excellent | None |
| 17 | WHY tooltip | **Justified** | Excellent | Excellent | None |
| 18 | Centrality heatmap | **Justified** | Excellent | Good | None |
| 19 | Update MODEL.md | **Justified** | Excellent | Good | None |
| 20 | Update schema JSON | **Justified** | Excellent | Excellent | None |
| 21 | Update COLLIDER.md | **Justified** | Excellent | Excellent | None |

### Critical Findings

| Task | Issue | Severity | Resolution |
|------|-------|----------|------------|
| #7 | Implicitly depends on symbol resolution (ClassName → file) | **Major** | Add symbol resolver task or reduce scope to same-file only |
| #12 | More of a long-running research project than a task | Medium | Reframe as ongoing tracking, not single task |
| #1 | Schema migration not planned | Minor | Add migration substep for consumers |
| #2 | Performance not benchmarked | Minor | Add benchmark step for large graphs |

### Improved Acceptance Criteria (AI Suggestions)

| Task | Original AC | Improved AC |
|------|-------------|-------------|
| #8 | "Can extract scope boundaries from any Python file" | "Given test file with 3 nested functions, analyzer outputs JSON tree with 3 scopes" |
| #10 | "correlates with actual API surface" | "public functions have interface_surface > 0, private (`_`) functions have 0" |
| #19 | "MODEL.md reflects implementation" | "Peer review confirms MODEL.md aligns with Task #1 implementation" |

**Validation tokens:** 6,269 input, 2,909 output ($0.02)