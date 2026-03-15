# Atlas Discoverability Report — Wave 0 Quality Gate
## Date: 2026-03-15 | Executor: Claude Code (Opus 4.6)

---

## Factual Queries (answered from atlas/ files ONLY)

### Q1: Components (8)
| ID | Name | Purpose |
|----|------|---------|
| CMP-001 | cerebras-rapid-intel | Fast AI research using Cerebras inference |
| CMP-002 | collider | Deep code analysis using algebraic topology |
| CMP-003 | briefing-generator | Compresses Collider output into actionable briefings |
| CMP-010 | notion-sync | Automated Notion database sync via n8n |
| CMP-052 | ai-analyze | Smart-routed AI queries via Gemini |
| CMP-056 | cerebras-spiral-intel | Multi-pass iterative codebase understanding |
| CMP-060 | reh-mcp-server | Git archaeology + session mining, 11 MCP tools |
| CMP-061 | cerebras-intelligence-mcp | Fast LLM queries + Perplexity research, 10 MCP tools |

### Q2: Agents (4)
| ID | Name | Type |
|----|------|------|
| AGT-001 | claude-web | llm_conversational |
| AGT-002 | claude-code (Rainmaker) | llm_agentic |
| AGT-003 | n8n-orchestrator | workflow_runner |
| AGT-004 | chatgpt-agents | llm_conversational |

### Q3: Connections (7)
| ID | Source → Target | Protocol | Relationship |
|----|-----------------|----------|-------------|
| CON-001 | AGT-002 → EXT-001 (Cerebras) | http_rest | depends_on |
| CON-002 | AGT-002 → EXT-002 (Anthropic) | http_rest | depends_on |
| CON-003 | AGT-002 → RES-001 (VPS) | ssh | depends_on |
| CON-004 | RES-002 (Mac) → RES-001 (VPS) | sync_bidirectional | replicates |
| CON-005 | ecosystem → EXT-003 (Doppler) | http_rest | depends_on |
| CON-006 | AGT-002 → EXT-005 (GitHub) | http_rest | depends_on |
| CON-010 | AGT-003 → EXT-004 (Notion) | http_rest | orchestrates |

### Q4: Collider
- **ID:** CMP-002
- **Produces:** analysis_report (file:json), brain_download (file:md)
- **Connections:** requires_connections: [] (none — Collider is a local tool, no API dependency)
- **Fed by:** CMP-001 (cerebras-rapid-intel)
- **Feeds into:** CMP-003 (briefing-generator)

### Q5: What breaks if Cerebras goes down?
- **Connection:** CON-001 (cerebras-inference)
- **Direct blast_radius:** CMP-001, CMP-056, CMP-061
- **Cascade via feeds_into:**
  - CMP-001 → CMP-002 (Collider loses rapid intel enrichment)
  - CMP-002 → CMP-003 (Briefing generator gets degraded input)
- **Agent impact:** AGT-002 lists CON-001 in connections_usable
- **human_impact:** "Fast code gen and rapid intel unavailable. Falls back to Anthropic (slower, pricier)."
- **recovery_action:** "Check Cerebras status. If credential, rotate in Doppler. If provider, use Anthropic fallback."

### Q6: Entities by stage
| Stage | Count |
|-------|-------|
| P0 | 1 (CON-005 Doppler — bootstrap) |
| P1 | 6 (most connections) |
| P2 | 14 (most components and agents) |
| P3 | 1 (CMP-002 Collider) |

### Q7: Graph size
- **Nodes:** 27 (8 CMP + 4 AGT + 3 RES + 12 EXT)
- **Edges:** 7 connections
- **Graph equation:** G = (Components ∪ Agents ∪ Resources ∪ Externals, Connections)

---

## Navigation Queries

### Q8: File reads from CLAUDE.md to "what connections does the Collider use?"
1. Read CLAUDE.md → find "Load atlas/ATLAS.yaml"
2. Read atlas/ATLAS.yaml → find CMP-002 (Collider) → requires_connections: []
**Answer in 2 reads.** (Collider has no external connections — it's a local tool.)

### Q9: Machine-parseable?
YES. `python3 -c "import yaml; yaml.safe_load(open('atlas/ATLAS.yaml'))"` succeeds. Full graph extractable.

### Q10: Adjacency list (10-line script, run, output)
```python
import yaml
data = yaml.safe_load(open('atlas/ATLAS.yaml'))
adj = {}
for c in data.get('connections', []):
    s, t = c.get('source','?'), c.get('target','?')
    r = c.get('relationship',{})
    rel = r.get('canonical', r) if isinstance(r, dict) else r
    adj.setdefault(s, []).append((t, rel, c['id']))
for s, edges in sorted(adj.items()):
    for t, rel, cid in edges:
        print(f'{s} --[{rel}]--> {t}  ({cid})')
```
**Output:**
```
agent:AGT-002 --[depends_on]--> external:EXT-001  (CON-001)
agent:AGT-002 --[depends_on]--> external:EXT-002  (CON-002)
agent:AGT-002 --[depends_on]--> resource:RES-001  (CON-003)
agent:AGT-002 --[depends_on]--> external:EXT-005  (CON-006)
agent:AGT-003 --[orchestrates]--> external:EXT-004  (CON-010)
resource:RES-002 --[replicates]--> resource:RES-001  (CON-004)
system:ecosystem --[depends_on]--> external:EXT-003  (CON-005)
```

---

## Gap Queries

### Q11: Priority or next-action signal?
NO. The atlas has no "current priority" or "next action" field. This would need either a separate file (atlas/PRIORITIES.md) or a `priority` field on entities. Currently, stage and status are the closest signals (P0 = needs work, status: draft = incomplete).

### Q12: Unregistered source files
**29 Python tools in wave/tools/ai/ have no atlas entry.** Top 10 candidates for registration:
1. cerebras_tagger.py (batch D1-D8 classification — high usage)
2. cerebras_enricher.py (node enrichment — high usage)
3. adversarial_auditor.py (threat analysis — active)
4. perplexity_research.py (web research — daily use)
5. sonar_deep.py (deep research — weekly use)
6. cerebras_queue.py (job queuing — infrastructure)
7. cerebras_doc_validator.py (documentation validation)
8. cerebras_zoo_compare.py (model comparison)
9. collider_bridge.py (Collider integration)
10. boundary_analyzer.py (scope analysis)

### Q13: Token cost
- **ATLAS.yaml:** ~4,076 tokens (0.41% of 1M context)
- **All schemas:** ~9,481 tokens
- **Total (data + grammar):** ~13,557 tokens (1.36% of 1M context)
- **Under 1% for data alone:** YES
- **Under 2% for data + grammar:** YES

---

## Verdict

### Discoverability Score: 4 / 5

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Findability** | 5/5 | CLAUDE.md boot pointer works. 2 reads to any answer. |
| **Completeness** | 3/5 | 8 of 37 active components registered (22%). 29 unregistered tools. |
| **Machine parseability** | 5/5 | Standard YAML. Adjacency list extractable in 10 lines. |
| **Cross-reference accuracy** | 4/5 | 34/34 refs resolve. feeds_into/fed_by chains are accurate. |
| **Agent autonomy** | 4/5 | Full blast radius traversal works. No priority signal. |

### Top 3 improvements to raise score by 1 point:
1. **Register the 10 highest-priority tools** (especially cerebras_tagger, perplexity_research, sonar_deep) — raises completeness from 22% to ~50%
2. **Add a `priority` or `next_action` field** to entities — enables agents to self-direct maintenance work
3. **Add Perplexity/Gemini connections** (CON-007, CON-008) — these are Ring 1 services with daily usage but no connection entries

### Scaffold hypothesis impact on score:
YES — the scaffold validation (CONFIRMED WITH BOUNDARIES) means the atlas is not just a partial index but the COMPLETE architectural awareness layer for identity and connectivity. Runtime telemetry is the one gap, and it's scaffold-compatible. This raises confidence that the 4/5 score reflects a fundamentally sound architecture, not a lucky subset.
