# GraphRAG Unlocks Repository Untangling
**Insight:** Semantic graph reveals natural organization
**When:** After tasks #4, #7, #8 complete
**Result:** Restructure repo by semantic clusters, not folders

---

## THE PROBLEM (Current State)

**Repository organized by:**
- File type (.md, .py, .yaml)
- Module ownership (collider/, wave/, .agent/)
- Historical accidents (where someone put it first)

**Not organized by:**
- Semantic relationships (which theories connect?)
- Conceptual clusters (which papers validate which code?)
- Natural boundaries (what belongs together?)

**Result:**
- 281 theories scattered across 689 files
- Related concepts in different directories
- Hard to find "everything about X"

---

## WHAT GRAPHRAG UNLOCKS

### Task #4: Community Detection (Leiden)

**When run:**
```python
communities = leiden_algorithm(graph)
# Returns: 15-30 semantic clusters
```

**Reveals:**
```
Community 1: Constructal Law cluster
├─ Theory: Lei Construtal (Bejan)
├─ Theory: Ω minimization
├─ Theory: E(S|Φ) energy function
├─ Code: refinery.py (convergence detection)
├─ Research: Flask 13-year study
└─ Papers: Bejan's publications

Community 2: Purpose Field cluster
├─ Theory: Purpose Field π
├─ Theory: dπ/dt dynamics
├─ Code: Collider purpose computation
├─ Research: Novelty validation (60+ sources)
└─ Papers: Friston FEP (validates)

Community 3: Communication Theory cluster
├─ Theory: Shannon entropy (MI)
├─ Theory: Control theory (F, N)
├─ Code: fabric.py
├─ Research: Google SRE, cascading failures
└─ Papers: Shannon, Ashby
```

**Each community = natural conceptual unit!**

---

### Task #7: Research Integration (1,068 files)

**When integrated:**
```
Graph adds:
- 1,068 ResearchDoc nodes
- ~5,000 concept mentions
- ~2,000 citations
```

**Enables:**
```cypher
// Find ALL material about Constructal Law
MATCH (cluster:Community {name: 'Constructal'})
MATCH (cluster)<-[:MEMBER_OF]-(item)
RETURN item
// Returns: theories, code, papers, research - everything!
```

**Result:** One query retrieves COMPLETE context on any topic

---

### Task #8: Accuracy Validation

**When measured:**
```
Baseline (text search): Find by keyword
GraphRAG (semantic): Find by meaning + relationships

Expected: 3.4× better recall
```

**Proves:** Semantic organization > folder organization

---

## THE UNTANGLING (After GraphRAG Complete)

### Phase 1: Discover Natural Clusters

```python
# Run community detection
communities = detect_communities(graph)

# Analyze each community
for community in communities:
    members = get_community_members(community)

    # What's in this cluster?
    theories = [m for m in members if type == 'Theory']
    code = [m for m in members if type == 'CodeEntity']
    papers = [m for m in members if type == 'AcademicPaper']

    print(f"Community: {len(theories)} theories, {len(code)} code, {len(papers)} papers")

    # Natural name emerges from most central concept
    central_concept = get_highest_betweenness(community)
    print(f"  Theme: {central_concept.name}")
```

**Output:**
```
Community 1: 8 theories, 12 code files, 5 papers
  Theme: flow_optimization

Community 2: 15 theories, 23 code files, 8 papers
  Theme: purpose_emergence

Community 3: 6 theories, 8 code files, 3 papers
  Theme: graph_structure
```

**These are NATURAL clusters** (not invented by us)

---

### Phase 2: Restructure by Semantics

**Instead of:**
```
particle/docs/theory/
├─ THEORY_AXIOMS.md (all mixed)
├─ L0_AXIOMS.md (all mixed)
└─ PROJECTOME_THEORY.md (all mixed)
```

**Reorganize to:**
```
knowledge/
├─ flow_systems/ (Community 1)
│   ├─ theories/
│   │   ├─ constructal_law.md
│   │   ├─ omega_minimization.md
│   │   └─ energy_function.md
│   ├─ implementations/
│   │   └─ refinery_convergence.py
│   └─ research/
│       └─ bejan_papers.md
│
├─ purpose_field/ (Community 2)
│   ├─ theories/
│   │   ├─ purpose_field_pi.md
│   │   └─ dynamics.md
│   ├─ implementations/
│   │   └─ collider_purpose.py
│   └─ research/
│       └─ novelty_validation.md
│
└─ graph_structure/ (Community 3)
    └─ [similar organization]
```

**Benefit:** Everything about X in ONE place (semantic locality)

---

### Phase 3: Auto-Generate Organization

**GraphRAG can GENERATE reorganization plan:**

```python
def propose_restructuring(graph):
    """
    Analyze communities and propose file reorganization.
    """
    communities = detect_communities(graph)

    plan = {}
    for community in communities:
        # Get all files in this community
        files = get_file_paths(community.members)

        # Propose new directory
        theme = get_central_theme(community)
        new_dir = f"knowledge/{theme}/"

        # Generate move commands
        plan[theme] = {
            "current_files": files,
            "proposed_location": new_dir,
            "rationale": f"Semantic cluster around {theme}",
            "members": len(community.members)
        }

    return plan

# Execute
plan = propose_restructuring(graph)

# Output: Automated reorganization plan
for theme, details in plan.items():
    print(f"\nCluster: {theme}")
    print(f"  Files to move: {len(details['current_files'])}")
    print(f"  New location: {details['proposed_location']}")
    print(f"  Rationale: {details['rationale']}")
```

**GraphRAG TELLS US how to organize the repo!**

---

## THE VISION

**Current:** 689 theory files, organizados por acidente
**After GraphRAG:** Semantic clusters discovered automatically
**Then:** Restructure repo to match semantic reality
**Result:** "Natural" organization (emerges from connections, not imposed)

---

## SPECIFIC UNTANGLING EXAMPLES

### Example 1: Purpose Field Scattered

**Current locations:**
- Theory: `particle/docs/theory/THEORY_AXIOMS.md` (D1-D7)
- Research: `docs/research/perplexity/` (novelty validation)
- Code: `src/core/purpose_field.py`
- Papers: `wave/archive/references/` (REF-040 Friston)
- Discussion: `.agent/intelligence/comm_analysis/` (our notes)

**After GraphRAG clustering:**
```
Move all to: knowledge/purpose_field/
├─ theory.md (D1-D7 axioms)
├─ implementation.py (from Collider)
├─ validation.md (novelty research)
├─ foundations.md (REF-040 Friston)
└─ evolution.md (our session notes)
```

**One directory, complete context!**

---

### Example 2: Communication Theory Scattered

**Current:**
- Theory: `.agent/intelligence/comm_analysis/` (15 files!)
- Code: `.agent/intelligence/comms/fabric.py`
- Research: `docs/research/perplexity/` (60+ sources)
- Papers: Shannon, Ashby (in references/)

**After clustering:**
```
knowledge/communication_systems/
├─ shannon_theory.md
├─ control_theory.md
├─ fabric_implementation.py
├─ research_synthesis.md
└─ academic_foundations.md (Shannon, Ashby)
```

**GraphRAG shows what belongs together!**

---

## WHEN UNLOCKED (Tasks #4, #7, #8)

**We can:**

1. **Discover natural clusters** (Leiden detection)
2. **Validate organization** (modularity Q >0.7 = good)
3. **Generate restructuring plan** (automated)
4. **Preview new structure** (before moving files)
5. **Execute reorganization** (git mv commands)
6. **Verify improvement** (easier to find related concepts?)

**Timeline:**
- Task #4: 1 hour (Leiden)
- Task #7: 4 hours (research integration)
- Task #8: 2 hours (validation)
- **Total:** 7 hours → Unlocks untangling capability

---

## THE POWER

**GraphRAG doesn't just answer queries.**

**GraphRAG reveals STRUCTURE:**
- What belongs together (communities)
- What's central (PageRank)
- What connects domains (bridges)
- What's isolated (needs integration)

**This structure IS the natural organization of knowledge!**

**Restructure repo to match → Untangled automatically**

---

## RECOMMENDATION

**Complete tasks #4, #7, #8 (7 hours)**

**Then:**
- Run community detection
- Analyze clusters
- Propose reorganization
- Preview changes
- Execute restructuring

**Result:** Repository organized by MEANING, not by ACCIDENT

**This is the ultimate untangling - let the graph tell us how to organize!**

---

**WANT TO COMPLETE THESE 3 TASKS NEXT SESSION?**

7 hours → Full semantic organization discovered
