# Orphan Taxonomy: Why Nodes Appear Disconnected

> **Date:** January 21, 2026
> **Status:** RESEARCH FINDING - Proposes replacing `topology_role=orphan` with richer taxonomy
> **Key Insight:** "Orphan" is a misclassification bucket, not a real category

---

## The Problem

Current Collider classifies nodes with `in_degree=0 AND out_degree=0` as `orphan`. This is **wrong** because it conflates 7+ distinct phenomena under one label:

| What We Call It | What It Actually Is | Correct Treatment |
|-----------------|---------------------|-------------------|
| Orphan | Dead code | DELETE |
| Orphan | Entry point | Mark as ROOT |
| Orphan | External interface | Mark as BOUNDARY |
| Orphan | Test fixture | Mark as TEST_ROOT |
| Orphan | Dynamic dispatch target | Mark as POLYMORPHIC |
| Orphan | Reflection target | Mark as DYNAMIC |
| Orphan | Framework-managed | Mark as FRAMEWORK_ROOT |

**Result:** 116 "orphans" in Collider are actually 7 different things requiring 7 different actions.

---

## Proposed Taxonomy: `disconnection_reason`

Replace single `orphan` classification with multi-dimensional analysis:

### Primary Dimension: Reachability Source

| `reachability_source` | Definition | Detection Method |
|-----------------------|------------|------------------|
| `unreachable` | No path from any entry point | True dead code |
| `entry_point` | IS an entry point | `__main__`, CLI, event handler |
| `external_boundary` | Called from outside system | Public API, exported function |
| `test_entry` | Called by test framework | In `test_*` file or `conftest` |
| `framework_managed` | Instantiated by DI/framework | Decorators like `@Component` |
| `dynamic_target` | Called via reflection/eval | String-based invocation patterns |
| `cross_language` | Called from different language | JS↔Python, etc. |

### Secondary Dimension: Connection Direction

| `connection_gap` | Definition |
|------------------|------------|
| `no_incoming` | Nothing calls this (but it calls others) |
| `no_outgoing` | Calls nothing (terminal) |
| `isolated` | Neither incoming nor outgoing |

### Tertiary Dimension: Confidence

| `isolation_confidence` | Meaning |
|------------------------|---------|
| `high` | Static analysis confident this is truly isolated |
| `medium` | Possible dynamic/reflection paths |
| `low` | Likely false positive (framework, cross-language) |

---

## Visualization Specification

### Current (Wrong)
```
All orphans → Gray color → "Dead code?" tooltip
```

### Proposed (Right)

| Category | Visual Encoding | Interaction |
|----------|-----------------|-------------|
| `unreachable` (true dead) | Red, smallest, dashed border | "Safe to delete" tooltip |
| `entry_point` | Green, ROOT icon, solid border | "Entry point" tooltip |
| `test_entry` | Blue, test tube icon | "Test fixture" tooltip |
| `framework_managed` | Purple, gear icon | "Framework creates this" tooltip |
| `dynamic_target` | Orange, lightning icon | "Called dynamically" tooltip |
| `cross_language` | Yellow, bridge icon | "Cross-language boundary" tooltip |
| `external_boundary` | Cyan, arrow-out icon | "Public API" tooltip |

### Layout Strategy

1. **Don't hide orphans** - they're important signals
2. **Group by reason** - cluster same-reason orphans together
3. **Position at boundaries** - entry points at top, dead code at bottom
4. **Show WHY** - tooltip explains the classification reason

---

## Detection Algorithm

```python
def classify_disconnection(node, edges, all_nodes):
    """
    Replace binary orphan detection with rich taxonomy.

    Returns: {
        'reachability_source': str,
        'connection_gap': str,
        'isolation_confidence': float,
        'suggested_action': str
    }
    """
    in_deg = compute_in_degree(node, edges)
    out_deg = compute_out_degree(node, edges)

    # Not disconnected at all
    if in_deg > 0 and out_deg > 0:
        return None

    file_path = node.get('file_path', '')
    name = node.get('name', '')
    kind = node.get('kind', '')
    decorators = node.get('decorators', [])

    # Determine connection gap
    if in_deg == 0 and out_deg == 0:
        connection_gap = 'isolated'
    elif in_deg == 0:
        connection_gap = 'no_incoming'
    else:
        connection_gap = 'no_outgoing'

    # Classify reachability source
    if is_test_file(file_path):
        source = 'test_entry'
        confidence = 0.95
        action = 'OK - test framework invokes'

    elif has_main_guard(node) or is_cli_entry(node):
        source = 'entry_point'
        confidence = 0.99
        action = 'OK - entry point'

    elif is_framework_managed(decorators):
        source = 'framework_managed'
        confidence = 0.90
        action = 'OK - framework instantiates'

    elif is_cross_language(file_path):
        source = 'cross_language'
        confidence = 0.70
        action = 'CHECK - may have cross-language callers'

    elif has_dynamic_patterns(node):
        source = 'dynamic_target'
        confidence = 0.60
        action = 'CHECK - may be called via reflection'

    elif is_public_api(node):
        source = 'external_boundary'
        confidence = 0.80
        action = 'OK - public interface'

    else:
        source = 'unreachable'
        confidence = 0.85
        action = 'REVIEW - likely dead code'

    return {
        'reachability_source': source,
        'connection_gap': connection_gap,
        'isolation_confidence': confidence,
        'suggested_action': action
    }
```

---

## Application to Collider's 116 Orphans

Re-analyzing with taxonomy:

| Reachability Source | Count | % | Action |
|---------------------|-------|---|--------|
| `cross_language` (JS) | 68 | 59% | Improve JS edge detection |
| `framework_managed` (dataclass) | 15 | 13% | Track instantiation |
| `test_entry` | 16 | 14% | Reclassify as test_root |
| `entry_point` (scripts) | 6 | 5% | Detect __main__ |
| `unreachable` (true dead) | 11 | 9% | DELETE these |

**Only 11 of 116 "orphans" are actually dead code (9%).**

---

## Visualization Mockup

```
┌─────────────────────────────────────────────────────────────┐
│  DISCONNECTED NODES PANEL                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ■ ENTRY POINTS (6)                    ┌─────┐              │
│    ○ cli.py::main                      │ ▶   │ Green        │
│    ○ run_benchmark.py::main            │     │ "Runs via    │
│    ○ clone_repos.py::main              └─────┘  __main__"   │
│                                                             │
│  ■ TEST FIXTURES (16)                  ┌─────┐              │
│    ○ conftest.py::sample_file          │ 🧪  │ Blue         │
│    ○ conftest.py::mock_tree_sitter     │     │ "pytest      │
│    ○ test_upb.js::assert               └─────┘  invokes"    │
│                                                             │
│  ■ CROSS-LANGUAGE (68)                 ┌─────┐              │
│    ○ layout.js::get                    │ 🌉  │ Yellow       │
│    ○ selection.js::set                 │     │ "Called from │
│    ○ registry.js::hasCommand           └─────┘  HTML/other" │
│                                                             │
│  ■ FRAMEWORK-MANAGED (15)              ┌─────┐              │
│    ○ types.py::Dimensions              │ ⚙️   │ Purple       │
│    ○ types.py::Edge                    │     │ "Dataclass   │
│    ○ types.py::Location                └─────┘  instantiated"│
│                                                             │
│  ■ DEAD CODE (11)                      ┌─────┐              │
│    ○ smart_extractor.py::format_card   │ 💀  │ Red          │
│    ○ graph_analyzer.py::generate_report│     │ "No callers  │
│    ○ types.py::parse_particle_id       └─────┘  DELETE?"    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration with SMC Theory

### New Property: `disconnection`

Add to node schema alongside `topology_role`:

```json
{
  "id": "conftest.py::sample_file",
  "topology_role": "orphan",           // DEPRECATED - keep for back-compat
  "disconnection": {
    "reachability_source": "test_entry",
    "connection_gap": "isolated",
    "isolation_confidence": 0.95,
    "suggested_action": "OK - test framework invokes"
  }
}
```

### Theory Connection

This connects to **Interface Surface** (THEORY_EXPANSION §8):

- Disconnected nodes are at the **boundary** of our analysis
- They reveal where our static analysis **cannot see**
- Each disconnection type is a different kind of boundary crossing

---

## Next Steps

1. **Implement `classify_disconnection()`** in full_analysis.py
2. **Add `disconnection` property** to node schema
3. **Update visualization** to show taxonomy, not just "orphan"
4. **Delete true dead code** (11 nodes) after manual review

---

## References

1. Perplexity Research (Jan 21, 2026): Orphan node taxonomy
2. Graph Theory: Isolated nodes, disconnected components
3. Static Analysis: False positive handling via reachability roots
4. Network Visualization: Encoding 'why' vs 'that' for disconnection
