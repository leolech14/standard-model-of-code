# DataManager Refactoring Map
## visualize_graph_webgl.py Analysis

**File Stats:**
- 5559 lines
- 153 data access points
- 85+ functions
- 24 FULL_GRAPH accesses
- 26 Graph.graphData() accesses

---

## 1. DATA SOURCES (Entry Points)

| Source | Line | Description |
|--------|------|-------------|
| `graph_data` (Python) | 280-334 | Built from analysis JSON - nodes, links with markov_weight |
| `FULL_GRAPH = e.data.result` | 1721 | Worker thread delivers parsed data |
| `data.get("markov", {})` | 264 | Markov matrix from analysis |
| `data.get("file_boundaries")` | varies | File boundary data |

---

## 2. DATA STORES (Global State)

| Variable | Line | Purpose | Mutation Points |
|----------|------|---------|-----------------|
| `FULL_GRAPH` | 1256 | **PRIMARY** - all raw analysis data | Set once at 1721 |
| `Graph.graphData()` | ForceGraph | **ACTIVE** - current visible subset | 1786, 2561, 2575, 2592, 2607 |
| `FILE_GRAPH` | 2558 | Cached file-mode graph | buildFileGraph() |
| `SELECTED_NODE_IDS` | ~4488 | Current selection | setSelection(), clearSelection() |
| `SAVED_GROUPS` | ~4347 | Persisted groups | loadGroups(), saveGroups() |
| `VIS_FILTERS` | ~1270 | Filter state | setupSidebar callbacks |
| `ACTIVE_DATAMAPS` | ~1290 | Active datamap prefixes | setDatamap() |
| `NODE_COLOR_MODE` | 1333 | tier/ring/family/file | setNodeColorMode() |
| `EDGE_MODE` | ~1334 | type/resolution/weight/confidence | setEdgeMode() |
| `originalNodeColors` | 4250 | Saved for restore | applyFlowVisualization() |

---

## 3. DATA TRANSFORMERS (Pure-ish Functions)

### Core Transformers
| Function | Line | Input | Output | Accesses |
|----------|------|-------|--------|----------|
| `filterGraph()` | 2179 | data, minVal, datamapSet, filters | {nodes[], links[]} | data.nodes, data.links |
| `buildFileGraph()` | 2360 | data | {nodes[], links[]} | data.file_boundaries |
| `buildHybridGraph()` | 2430 | data | {nodes[], links[]} | data.file_boundaries, data.nodes |

### Node Property Extractors
| Function | Line | Input | Output |
|----------|------|-------|--------|
| `getNodeTier()` | 2071 | node | 'T0'/'T1'/'T2'/'UNKNOWN' |
| `getNodeAtomFamily()` | 2094 | node | 'LOG'/'DAT'/'ORG'/'EXE'/'EXT' |
| `getNodeRing()` | 2108 | node | ring string |
| `getNodeColorByMode()` | 2113 | node | color value |
| `getLinkEndpointId()` | 2328 | link, side | node id |
| `getLinkFileIdx()` | 3873 | link, side | file index |

### Aggregators
| Function | Line | Input | Output |
|----------|------|-------|--------|
| `collectCounts()` | 2619 | items, keyFn | Map<key, count> |
| `updateEdgeRanges()` | 3837 | (reads Graph) | updates EDGE_RANGES |
| `refreshNodeFileIndex()` | 3863 | (reads Graph) | updates node.fileIdx |

---

## 4. DATA CONSUMERS (Read-Only Access)

### FULL_GRAPH Readers (24 access points)
```
Line   Function/Context              Field Accessed
----   ----------------              --------------
2119   getNodeColorByMode()          file_boundaries
2120   getNodeColorByMode()          file_boundaries[idx]
2165   applyNodeColors()             file_boundaries
2166   applyNodeColors()             file_boundaries[idx]
2551   refreshGraph()                existence check
2558   refreshGraph()                → buildFileGraph(FULL_GRAPH)
2573   refreshGraph()                → buildHybridGraph(FULL_GRAPH)
2586   refreshGraph()                → filterGraph(FULL_GRAPH, ...)
2590   refreshGraph()                → filterGraph(FULL_GRAPH, ...)
3089   sidebar callback              → drawFileBoundaries(FULL_GRAPH)
3112   sidebar callback              → drawFileBoundaries(FULL_GRAPH)
3135   sidebar callback              → applyClusterForce(FULL_GRAPH)
3492   updateDatamapControls()       existence check
3494   updateDatamapControls()       → filterGraph(FULL_GRAPH, ...)
4095   applyFlowVisualization()      markov
4096   applyFlowVisualization()      markov.high_entropy_nodes
4217   setDatamap()                  existence check
4223   setDatamap()                  → filterGraph(FULL_GRAPH, ...)
4931   toggleFileExpand()            file_boundaries[idx]
5403   applyFileVizMode()            (alias: data = FULL_GRAPH)
5442   scheduleHullRedraw()          → drawFileBoundaries(FULL_GRAPH)
5454   applyFileColors()             file_boundaries
```

### Graph.graphData() Readers (26 access points)
```
Line   Function/Context              Purpose
----   ----------------              -------
2235   saveNodePositions()           iterate nodes
2270   freezeLayout()                iterate nodes
2284   unfreezeLayout()              iterate nodes
2418   captureFileNodePositions()    iterate nodes
3451   selectNodesInBox()            iterate nodes
3560   animateDimensionChange()      iterate nodes
3838   updateEdgeRanges()            iterate links
3865   refreshNodeFileIndex()        iterate nodes
4111   applyFlowVisualization()      nodes + links
4112   applyFlowVisualization()      links
4179   clearFlowVisualization()      nodes
4483   getSelectedNodes()            filter nodes
4676   updateSelectionVisuals()      iterate nodes
4699   syncSelectionAfterGraphUpdate() node ids
4751   selectNodesInBox()            iterate nodes
5023   drawFileBoundaries()          nodes for positioning
5404   applyFileVizMode()            nodes
5507   applyFileColors()             nodes
```

---

## 5. DATA FLOW DIAGRAM

```
                    ┌─────────────────────────────────────────────────────┐
                    │              PYTHON BACKEND                         │
                    │  full_analysis.py → compute_markov_matrix()         │
                    │  → edges get markov_weight                          │
                    │  → output JSON                                      │
                    └─────────────────────┬───────────────────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────────────┐
                    │         EMBEDDED DATA (graph_data dict)             │
                    │  nodes[], links[], markov{}, file_boundaries[]      │
                    └─────────────────────┬───────────────────────────────┘
                                          │
                         Worker.postMessage(compressed)
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           FULL_GRAPH (raw truth)                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐   │
│  │ nodes[]    │  │ links[]    │  │ markov{}   │  │ file_boundaries[]    │   │
│  │ (729)      │  │ (2923)     │  │ transitions│  │ (64 files)           │   │
│  │ +fileIdx   │  │ +markov_wt │  │ high_entropy│ │ atom_ids[], etc      │   │
│  └─────┬──────┘  └─────┬──────┘  └──────┬─────┘  └───────────┬──────────┘   │
└────────┼───────────────┼────────────────┼────────────────────┼──────────────┘
         │               │                │                    │
         └───────────────┴────────────────┴────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌────────────────────┐       ┌────────────────────┐
         │   filterGraph()    │       │  buildFileGraph()  │
         │   buildHybridGraph │       │  (file mode)       │
         └─────────┬──────────┘       └─────────┬──────────┘
                   │                            │
                   └──────────┬─────────────────┘
                              ▼
         ┌─────────────────────────────────────────────────────┐
         │           Graph.graphData() (active view)           │
         │  Subset of nodes/links currently visible            │
         │  - Filtered by density slider                       │
         │  - Filtered by datamaps                             │
         │  - Filtered by tier/ring/role/edge filters         │
         └─────────────────────┬───────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │ RENDERING    │     │ SELECTION    │     │ FLOW MODE    │
   │ nodeColor()  │     │ SELECTED_IDS │     │ markov_weight│
   │ linkColor()  │     │ overlays     │     │ particles    │
   │ linkWidth()  │     │ groups       │     │ high_entropy │
   └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 6. PAIN POINTS (Why We Need DataManager)

### Problem 1: Scattered Lookups
```javascript
// CURRENT: Repeated O(n) scans
const nodes = Graph.graphData().nodes || [];  // 26 occurrences!
nodes.forEach(n => { ... });
```

### Problem 2: No Indexed Access
```javascript
// WANTED: O(1) lookup
const node = DataManager.getNodeById(id);
const edges = DataManager.getEdgesFrom(nodeId);
```

### Problem 3: Recomputed Aggregations
```javascript
// CURRENT: Recomputes every call
const tierCounts = collectCounts(data.nodes, n => getNodeTier(n));

// WANTED: Cached
const tierCounts = DataManager.getTierCounts(); // cached
```

### Problem 4: No Derived Data Coordination
```javascript
// CURRENT: Markov weights on edges, but no quick lookup
// To find high-probability edges from node X:
const edgesFromX = links.filter(l => getSource(l) === X.id)
                        .sort((a,b) => b.markov_weight - a.markov_weight);

// WANTED: Pre-indexed
const topEdges = DataManager.getTopMarkovEdges(nodeId, k=3);
```

### Problem 5: No Reactive Updates
```javascript
// CURRENT: Manual refresh calls everywhere
VIS_FILTERS.tiers.add('T0');
refreshGraph();  // Must remember to call!
updateSelectionVisuals();  // And this!
updateDatamapControls();  // And this!

// WANTED: Reactive
DataManager.filters.tiers.add('T0');  // Automatically triggers dependents
```

---

## 7. PROPOSED DataManager API

```javascript
class DataManager {
    // ═══════════════════════════════════════════════════════════
    // RAW DATA (immutable after load)
    // ═══════════════════════════════════════════════════════════
    raw: {
        nodes: Node[],
        links: Link[],
        markov: MarkovData,
        fileBoundaries: FileBoundary[],
        kpis: KPIs,
        brainDownload: string
    }

    // ═══════════════════════════════════════════════════════════
    // INDEXES (built once, O(1) lookup)
    // ═══════════════════════════════════════════════════════════
    index: {
        nodeById: Map<string, Node>,
        nodesByTier: Map<string, Node[]>,
        nodesByFamily: Map<string, Node[]>,
        nodesByFile: Map<number, Node[]>,

        edgesBySource: Map<string, Link[]>,
        edgesByTarget: Map<string, Link[]>,
        edgeBetween: Map<string, Link>,  // "src|tgt" → link

        markovFromNode: Map<string, {target: string, weight: number}[]>,
        highEntropyNodes: Set<string>
    }

    // ═══════════════════════════════════════════════════════════
    // DERIVED DATA (cached, invalidated on filter change)
    // ═══════════════════════════════════════════════════════════
    derived: {
        filteredNodes: Node[],       // Current visible subset
        filteredLinks: Link[],
        tierCounts: Map<string, number>,
        familyCounts: Map<string, number>,
        ringCounts: Map<string, number>,
        edgeTypeCounts: Map<string, number>,
        edgeRanges: { weight: {min, max}, confidence: {min, max} }
    }

    // ═══════════════════════════════════════════════════════════
    // STATE (mutable, triggers reactive updates)
    // ═══════════════════════════════════════════════════════════
    state: {
        filters: FilterState,
        colorMode: 'tier' | 'ring' | 'family' | 'file',
        edgeMode: 'type' | 'resolution' | 'weight' | 'confidence',
        density: number,
        datamaps: Set<string>,
        selection: Set<string>,
        groups: Group[]
    }

    // ═══════════════════════════════════════════════════════════
    // METHODS
    // ═══════════════════════════════════════════════════════════

    // Lookups (O(1))
    getNode(id: string): Node | null
    getEdgesFrom(nodeId: string): Link[]
    getEdgesTo(nodeId: string): Link[]
    getNodesInFile(fileIdx: number): Node[]

    // Markov-specific
    getTopMarkovEdges(nodeId: string, k?: number): Link[]
    getMarkovWeight(sourceId: string, targetId: string): number
    isHighEntropyNode(nodeId: string): boolean

    // Aggregations (cached)
    getCounts(dimension: 'tier' | 'family' | 'ring' | 'edgeType'): Map

    // Filtered view
    getFilteredGraph(): { nodes: Node[], links: Link[] }

    // State mutations (trigger reactive updates)
    setFilter(dimension: string, values: Set<string>): void
    setColorMode(mode: string): void
    setSelection(ids: Set<string>): void

    // Subscriptions
    subscribe(event: string, callback: Function): Unsubscribe
    // Events: 'filter-change', 'selection-change', 'graph-update'
}
```

---

## 8. REFACTORING IMPACT ZONES

### HIGH IMPACT (Core data flow)
- `initGraph()` - Initialize DataManager here
- `refreshGraph()` - Replace with DataManager.getFilteredGraph()
- `filterGraph()` - Move logic into DataManager
- `applyFlowVisualization()` - Use DataManager.markov indexes

### MEDIUM IMPACT (Read from DataManager instead of FULL_GRAPH)
- `getNodeColorByMode()` - DataManager.index.nodesByFile
- `buildFileGraph()` - DataManager.raw.fileBoundaries
- `buildHybridGraph()` - DataManager.raw.*
- `collectCounts()` - Replace with DataManager.getCounts()
- `updateEdgeRanges()` - Replace with DataManager.derived.edgeRanges

### LOW IMPACT (Just change variable reference)
- All `Graph.graphData().nodes` reads
- All `FULL_GRAPH.field` reads
- Selection functions

### UI CALLBACKS (Wire to DataManager.subscribe)
- Sidebar filter checkboxes
- Datamap toggles
- Color mode selectors
- Density slider

---

## 9. IMPLEMENTATION PHASES

### Phase 1: Core DataManager (Foundation)
- [ ] Create DataManager class with raw data storage
- [ ] Build indexes on initialization
- [ ] getNode(), getEdgesFrom(), getEdgesTo()

### Phase 2: Derived Data & Caching
- [ ] Implement filtered graph computation
- [ ] Cache tier/family/ring counts
- [ ] Cache edge ranges

### Phase 3: Markov Integration
- [ ] Index markov transitions by source node
- [ ] getTopMarkovEdges() for flow mode
- [ ] High entropy node lookup

### Phase 4: Reactive State
- [ ] Subscribe/publish system
- [ ] Wire filter changes to graph updates
- [ ] Wire selection to visual updates

### Phase 5: Migration
- [ ] Replace FULL_GRAPH accesses one by one
- [ ] Replace Graph.graphData() reads with DataManager
- [ ] Remove redundant global state

---

## 10. LINES OF CODE AFFECTED

| Category | Estimated Lines | Functions |
|----------|-----------------|-----------|
| New DataManager class | ~300 | 20+ methods |
| initGraph() rewrite | ~50 | 1 |
| refreshGraph() rewrite | ~30 | 1 |
| Filter functions | ~100 | 5 |
| Flow mode refactor | ~50 | 2 |
| Selection refactor | ~80 | 8 |
| UI callback wiring | ~100 | 15+ |
| **TOTAL NEW/MODIFIED** | **~710** | **50+** |

This represents ~13% of the file, but touches the most critical paths.
