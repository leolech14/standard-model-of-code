# Perplexity Sonar Pro Query: Spatial Relations & Topology Ontology Research

## API Endpoint
```
POST https://api.perplexity.ai/chat/completions
```

## Required Header
```
Authorization: Bearer $PPLX_API_KEY
Content-Type: application/json
```

---

## Full cURL Command

```bash
export PPLX_API_KEY="your-api-key-here"

curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PPLX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "sonar-pro",
  "temperature": 0.2,
  "messages": [
    {
      "role": "system",
      "content": "You are an expert in formal ontologies, spatial reasoning, GIS theory, and knowledge representation. Provide comprehensive, academically-grounded answers with citations (URLs when available). Structure your response with clear sections. Prioritize peer-reviewed sources, ISO/OGC standards, and authoritative databases like nLab, Stanford Encyclopedia of Philosophy, and official specification documents."
    },
    {
      "role": "user",
      "content": "I am building an ontology for CODE STRUCTURE ANALYSIS that models software repositories as typed multigraphs with spatial/topological relationships. I need to ground my inventory in established standards.\n\n## CURRENT INVENTORY\n\n### Node Types (Containers)\n- Directory, File, Atom (functions, classes, methods, variables)\n\n### Edge Types - Containment (E_contains)\n- Directory → Directory (subdirectory)\n- Directory → File\n- File → Atom\n\n### Edge Types - Dependencies (E_depends)\n- calls, imports, inherits, references\n\n### Spatial Concepts We Use\n- contains, within, crosses (boundary), adjacent, overlaps\n- visible vs hidden (viewport boundary)\n- interior vs boundary\n\n### Measurements\n- fan-out (branching factor)\n- cross-boundary coupling ratio\n- Betti numbers (b₀ connected components, b₁ cycles)\n- Euler characteristic\n\n## RESEARCH TASKS\n\n### Task 1: Identify Canonical Inventories\nWhat are the definitive, peer-reviewed taxonomies for:\n\na) **Spatial Relations** (topological, directional, metric)\n   - OGC Simple Features / DE-9IM matrix\n   - RCC-8 (Region Connection Calculus)\n   - GeoSPARQL ontology\n   - ISO 19107 (Spatial Schema)\n   - Allen's temporal intervals (for applicability to code regions)\n\nb) **Graph Relations** (for dependency graphs)\n   - Is there a canonical taxonomy of edge types in program analysis?\n   - Call graphs, data flow, control flow - any standard vocabulary?\n\nc) **Topological Invariants** (for code structure)\n   - Beyond Betti numbers: persistent homology, Euler characteristic\n   - What invariants are used in software complexity analysis?\n\nd) **Error/Anomaly Types** (geometric/topological)\n   - OGC geometry validation errors\n   - What's the canonical list? (self-intersection, polygon gaps, dangles, pseudo-nodes, spikes, etc.)\n\n### Task 2: Gap Analysis\nCompare my inventory to the canonical sources:\n- What spatial relation types am I MISSING?\n- What error types should I add?\n- What measurement invariants should I consider?\n\n### Task 3: Unknown Unknowns\nBeyond the obvious sources, search for:\n- Mereotopology (part-whole + topology combined)\n- Qualitative spatial reasoning (QSR) in AI\n- Graph grammar / graph transformation systems\n- Applied algebraic topology in software engineering\n- Network motifs and structural patterns\n\n### Task 4: Ontology Architecture\nHow should I structure an incremental ontology?\n- What are the minimum primitives (atomic relations)?\n- Which relations are derivable from primitives?\n- RCC-8 composition tables - how do they work?\n- Should I use OWL/SKOS, or something lighter?\n\n## DELIVERABLES REQUESTED\n\n1. **Canonical Inventory Table**: Map my terms to standard terms with citations\n2. **Gap List**: Relations/errors I'm missing with definitions\n3. **Unknown Unknowns List**: Concepts from adjacent fields I should investigate\n4. **Primitive Set**: Recommended minimal set of atomic relations\n5. **Architecture Recommendation**: OWL vs SKOS vs custom, with rationale\n6. **Key Papers**: 5-10 foundational papers I should read, with URLs\n\nProvide citations with URLs where possible. Prefer ISO/OGC specs, peer-reviewed papers, and authoritative sources like nLab or Stanford Encyclopedia."
    }
  ]
}'
```

---

## Alternative: Shorter Focused Query

If the above is too long, here's a focused version:

```bash
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PPLX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "model": "sonar-pro",
  "temperature": 0.2,
  "messages": [
    {
      "role": "system",
      "content": "Expert in spatial ontologies, GIS, and formal topology. Cite sources with URLs."
    },
    {
      "role": "user",
      "content": "I need canonical inventories for building a CODE TOPOLOGY ontology:\n\n1. What are ALL spatial relation types in OGC DE-9IM, RCC-8, and GeoSPARQL? Provide the complete taxonomy.\n\n2. What are ALL geometry validation error types defined by OGC? (self-intersection, gaps, dangles, etc.)\n\n3. What topological invariants beyond Betti numbers are used in software/network analysis?\n\n4. What is the minimal primitive set from which other relations can be derived? (e.g., RCC-8 composition)\n\n5. What concepts from mereotopology, qualitative spatial reasoning, or algebraic topology should I investigate?\n\nProvide a structured inventory with definitions and citations."
    }
  ]
}'
```

---

## Using the MCP Tool (if available)

If you have the Perplexity MCP server configured, you can use:

```
mcp__perplexity__perplexity_research
```

With the messages array above.

---

## Expected Output Structure

The response should include:

### 1. Canonical Spatial Relations Taxonomy
| Standard | Relation | Definition | Your Term |
|----------|----------|------------|-----------|
| DE-9IM | Equals | Same geometry | - |
| DE-9IM | Disjoint | No shared points | - |
| DE-9IM | Intersects | Shared points exist | overlaps? |
| DE-9IM | Touches | Boundaries touch, interiors don't | adjacent |
| DE-9IM | Contains | A contains B | contains |
| DE-9IM | Within | A within B | within |
| DE-9IM | Overlaps | Partial intersection | overlaps |
| DE-9IM | Crosses | Different dimensions intersect | crosses |
| DE-9IM | Covers | Contains + boundary | - |
| DE-9IM | CoveredBy | Within + boundary | - |
| RCC-8 | DC | Disconnected | - |
| RCC-8 | EC | Externally connected | adjacent |
| RCC-8 | PO | Partial overlap | overlaps |
| RCC-8 | TPP | Tangential proper part | - |
| RCC-8 | NTPP | Non-tangential proper part | within |
| RCC-8 | TPPi | Inverse TPP | - |
| RCC-8 | NTPPi | Inverse NTPP | contains |
| RCC-8 | EQ | Equal | - |

### 2. Geometry Validation Error Types
- Self-intersection
- Ring self-intersection
- Polygon holes outside shell
- Nested holes
- Disconnected interior
- Too few points
- Invalid coordinate
- Duplicate rings
- Self-touching rings
- Ring orientation
- Unclosed ring
- Dangles (line endpoints not connected)
- Pseudo-nodes (unnecessary vertices)
- Spikes (zero-area protrusions)
- Gaps (slivers between polygons)

### 3. Gap Analysis
- Missing: Equals, Disjoint, Touches, Covers, CoveredBy
- Missing: DC, EC, TPP, TPPi, NTPPi (RCC-8 completeness)
- Missing: directional relations (north, south, above, below)
- Missing: metric relations (near, far, distance-based)

### 4. Architecture Recommendation
- Primitive set: DC, PP, PPi, EQ (4 primitives)
- All RCC-8 derivable from these
- Use OWL for formal reasoning, SKOS for lightweight taxonomy

---

## Notes

1. **API Key**: Get from https://www.perplexity.ai/settings/api
2. **Model**: `sonar-pro` is their most capable research model
3. **Temperature**: 0.2 for factual/research queries
4. **Rate Limits**: Check your tier at https://docs.perplexity.ai/guides/rate-limits
