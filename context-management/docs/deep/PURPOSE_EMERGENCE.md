# Purpose Emergence: How Connections Define Meaning

> "Purpose emerges from structure" - if we know WHO calls/uses a node, we can infer WHAT that node is.

## Core Insight

The fundamental insight behind purpose emergence is that **an entity's purpose is revealed by its relationships**, not just its internal structure. This is analogous to:

- **Physics**: A particle's properties emerge from its interactions
- **Biology**: A cell's function emerges from its position in tissue
- **Society**: A person's role emerges from their relationships

In code: **You are what you connect to.**

## Implementation in Collider

The Standard Model of Code implements purpose emergence through three complementary systems:

| Module | Purpose | Output Fields |
|--------|---------|---------------|
| `graph_type_inference.py` | Infer type from caller/callee patterns | `discovery_method`, `role` |
| `purpose_emergence.py` | Compute emergent purpose at 4 levels | `pi1_purpose` - `pi4_purpose` |
| `topology_reasoning.py` | Classify graph shape and health | `topology_role`, shape classification |

## The Purpose Hierarchy (pi Levels)

Purpose emerges hierarchically, with each level building on the one below:

```
pi4 (System)    = f(file's pi3 distribution)    -> "DataAccess", "TestSuite"
     |
pi3 (Organelle) = f(class's pi2 distribution)   -> "Repository", "Processor"
     |
pi2 (Molecular) = f(effect, boundary, topology) -> "Compute", "Retrieve", "Transform"
     |
pi1 (Atomic)    = Role from classifier          -> "Service", "Repository", "Controller"
```

### pi1: Atomic Purpose (= Role)

The base level - what the node *is* structurally.

**Source**: Role classifier (name patterns, decorators, inheritance)

**Example values**: `Service`, `Repository`, `Controller`, `Validator`, `Factory`

### pi2: Molecular Purpose

Emergent from the combination of:
- **Effect**: Pure, Read, Write, ReadWrite
- **Boundary**: Internal, Input, Output, I-O
- **Atom Family**: DAT (Data), LOG (Logic), ORG (Organization), EXE (Execution)
- **Topology Role**: Hub, Leaf, Root, Bridge, Orphan

**Emergence Rules** (from `purpose_emergence.py`):

| Effect | Boundary | Family | pi2 Purpose |
|--------|----------|--------|-------------|
| Pure | internal | LOG | Compute |
| Read | internal | DAT | Retrieve |
| Write | internal | DAT | Persist |
| ReadWrite | input | LOG | Process |
| ReadWrite | output | LOG | Generate |
| ReadWrite | io | LOG | Gateway |

**Topology Modifiers**:
- Hub nodes -> `Coordinate`
- Root nodes -> `Initiate`
- Bridge nodes -> `Connect`
- Orphan nodes -> `{Purpose}(Orphan)`

### pi3: Organelle Purpose

Emergent from the distribution of child pi2 purposes.

**Rules**:
- All children same purpose -> `{Purpose}Container`
- Dominant purpose (>70%) -> inherit dominant
- Mix of Retrieve+Persist -> `Repository`
- Mix of Transform+Compute -> `Processor`
- Mix of Intake+Emit -> `Gateway`
- Many different purposes -> `Scattered` (potential God class)

### pi4: System Purpose

File-level purpose, emergent from pi3 distribution.

**Special patterns detected first**:
- Test files -> `TestSuite`
- Config files -> `Configuration`
- `__init__.py` -> `ModuleExport`

**Fallback rules**:
- Single purpose file -> `{Purpose}System`
- Retrieve+Persist mix -> `DataAccess`
- Transform+Process mix -> `Processing`
- Many purposes -> `Utility`

## Graph-Based Type Inference

When a node's role is `Unknown`, we can infer it from graph structure:

### Inference Rules

| Rule Name | Condition | Inferred Type | Confidence |
|-----------|-----------|---------------|------------|
| `calls_repository` | Calls a Repository | Service | 90% |
| `called_only_by_tests` | Only callers are Tests | Internal | 85% |
| `called_by_controller` | Called by Controller | Service | 80% |
| `leaf_called_by_service` | Called by Service, no out-edges | Query | 75% |
| `high_in_degree_utility` | 10+ callers | Utility | 70% |
| `calls_factory` | Calls Factory/Builder | Service | 75% |

### Structural Inference

When graph context is insufficient, structural properties can suggest type:

| Property | Pattern | Inferred Type |
|----------|---------|---------------|
| Return type | Contains "create", "build" | Factory |
| Return type | `bool` | Specification |
| Parameters | `request`, `response` | Controller |
| Docstring | Contains "test", "verify" | Test |
| Docstring | Contains "validate", "check" | Validator |
| Complexity | > 20 | Service |
| Kind=class, out_degree=0 | Leaf class | DTO |

### Parent Inheritance

Nested functions inherit their parent's role with slightly lower confidence:

```
TestClass (role: Asserter, confidence: 90%)
  └── TestClass.test_method (role: Asserter, confidence: 81%)  # 90% * 0.9
```

## Topology Reasoning

Beyond individual nodes, the graph's overall shape reveals architectural health:

### Betti Numbers

Topological invariants that capture graph structure:

- **b0**: Number of connected components (islands)
- **b1**: Number of independent cycles (circular dependencies)
- **Euler characteristic**: chi = b0 - b1

### Health Signals

| b0 | b1 | Signal | Meaning |
|----|-----|--------|---------|
| 1 | 0 | ACYCLIC | Ideal: connected, no cycles |
| 1 | 1-5 | CYCLIC | Some circular dependencies |
| 1 | >5 | HIGHLY_CYCLIC | Many circular dependencies |
| >1 | 0 | FRAGMENTED | Disconnected components |
| >1 | >0 | FRAGMENTED_CYCLIC | Worst: islands + cycles |

### Shape Classification

| Shape | Pattern | Description |
|-------|---------|-------------|
| STRICT_LAYERS | b1=0, b0=1 | Acyclic layered architecture |
| BIG_BALL_OF_MUD | High cycles + degree | Tangled dependencies |
| STAR_HUB | High centralization | Dominated by one node |
| DISCONNECTED_ISLANDS | b0 > 5 | Fragmented clusters |
| MESH | High avg degree | Highly interconnected |

## Pipeline Integration

Purpose emergence happens across multiple pipeline stages:

```
Stage 2.7  -> Dimension Classification (D1-D8)
Stage 3.5  -> Organelle Purpose (pi3)    <- compute_pi3()
Stage 3.6  -> System Purpose (pi4)       <- compute_pi4()
Stage 5    -> Graph-Based Type Inference <- apply_graph_inference()
Stage 6.5  -> Graph Analytics + pi2      <- compute_pi2()
Stage 10   -> Topology Classification    <- TopologyClassifier.classify()
```

## Output Schema

Nodes in `unified_analysis.json` include:

```json
{
  "id": "UserService.validate",
  "role": "Service",
  "role_confidence": 90.0,
  "discovery_method": "graph_inference:calls_repository",

  "pi2_purpose": "Process",
  "pi2_confidence": 0.85,

  "pi3_purpose": "Repository",
  "pi3_confidence": 0.80,

  "pi4_purpose": "DataAccessSystem",
  "pi4_confidence": 0.90,

  "topology_role": "hub",
  "semantic_role": "orchestrator"
}
```

## Relationship to ConAff (Future Enhancement)

The current implementation uses **direct neighbors** for inference. A future enhancement based on the ConAff paper (NeurIPS 2023) could add:

1. **k-Reciprocal Encoding**: Two nodes are reciprocally related if each is in the other's top-k neighbors
2. **Contextual Affinity**: Nodes with similar relationship patterns are considered similar, even if not directly connected
3. **Progressive Boundary Filtering**: Nodes near cluster boundaries are filtered progressively to reduce noise

This would enable discovering semantic similarity between nodes that never directly interact but play analogous roles in different parts of the codebase.

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `src/core/graph_type_inference.py` | 463 | Graph-based role inference |
| `src/core/purpose_emergence.py` | 510 | pi1-pi4 computation |
| `src/core/topology_reasoning.py` | 623 | Betti numbers, elevation, shapes |

## References

- [Standard Model of Code - MODEL.md](../../standard-model-of-code/docs/MODEL.md)
- [Collider Documentation](../../standard-model-of-code/docs/COLLIDER.md)
- [ConAff Paper](https://github.com/cly234/DeepClustering-ConNR) - Contextually Affinitive Neighborhood Refinery for Deep Clustering (NeurIPS 2023)
