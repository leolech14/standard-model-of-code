# Component C2: Formal JSON Schema Roadmap

> **Goal**: Create machine-readable schemas that any AI/tool can consume to understand particles
> **Priority**: ★★★★★ Critical Path
> **Estimated Duration**: Week 2-3

---

## Current State

| Metric | Current | Target |
|--------|---------|--------|
| JSON Schema defined | 0% | 100% |
| TypeScript types | 0% | 100% |
| Python dataclasses | 0% | 100% |
| Validation tests | 0% | 100% |
| Documentation | 0% | 100% |

---

## Phase 0: Pre-Development Research

### 0.1 Study Industry Standards (Day 1)

**Objective**: Review existing code analysis schemas for inspiration.

**Sources to Review**:
| Source | What to Learn |
|--------|---------------|
| [LSP (Language Server Protocol)](https://microsoft.github.io/language-server-protocol/) | Symbol kinds, location representation |
| [Tree-sitter JSON output](https://tree-sitter.github.io/) | AST node structure |
| [CodeQL Schema](https://codeql.github.com/) | Query-friendly code representation |
| [SARIF (Static Analysis Results)](https://sarifweb.azurewebsites.net/) | Findings and location format |
| [OpenAPI Spec](https://spec.openapis.org/) | Schema design patterns |

**Deliverable**: Design notes documenting borrowed patterns

---

### 0.2 Define Schema Requirements (Day 1-2)

**Objective**: List all requirements the schema must satisfy.

**Functional Requirements**:
| # | Requirement | Rationale |
|---|-------------|-----------|
| F1 | Represent single particle | Core use case |
| F2 | Represent full graph (nodes + edges) | Codebase analysis |
| F3 | Extensible for new dimensions | Future-proofing |
| F4 | Queryable by any dimension | AI filtering |
| F5 | Include source location | Code navigation |
| F6 | Include confidence scores | Trust calculation |
| F7 | Support incremental updates | Live analysis |

**Non-Functional Requirements**:
| # | Requirement | Rationale |
|---|-------------|-----------|
| N1 | JSON Schema 2020-12 compliant | Industry standard |
| N2 | TypeScript/Python type generation | Developer experience |
| N3 | Under 10KB per particle (typical) | Performance |
| N4 | Self-documenting | AI parsing |

**Deliverable**: `docs/SCHEMA_REQUIREMENTS.md`

---

### 0.3 Design Schema Hierarchy (Day 2)

**Objective**: Define the file structure for schema files.

**Proposed Structure**:
```
schema/
├── particle.schema.json      # Core: Single code entity
├── edge.schema.json          # Core: Relationship between particles
├── graph.schema.json         # Core: Full codebase graph
├── atoms.schema.json         # Reference: Valid atom types
├── dimensions.schema.json    # Reference: Dimension enums
├── levels.schema.json        # Reference: L-3 to L12
├── roles.schema.json         # Reference: 33 roles
├── edges.schema.json         # Reference: 5 edge families
├── tau.schema.json           # Notation: τ string format
├── types.ts                  # TypeScript types (generated)
├── types.py                  # Python types (generated)
└── README.md                 # Schema documentation
```

**Deliverable**: Directory structure created

---

## Phase 1: Core Schema Definition (Week 2)

### 1.1 Particle Schema (Day 3-4)

**Objective**: Define the core particle schema.

**Schema Definition**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://standardmodelofcode.org/schemas/particle.json",
  "title": "Standard Model Particle",
  "description": "A single classified code entity with 8-dimensional semantic coordinates",
  "type": "object",
  "required": ["id", "atom", "dimensions", "level", "plane", "location"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique particle ID: file_path::qualified_name",
      "pattern": "^.+::[a-zA-Z_][a-zA-Z0-9_.]*$",
      "examples": ["src/auth/user.py::UserService.get_by_id"]
    },
    "atom": {
      "$ref": "atoms.schema.json",
      "description": "Atom type from the 200-atom periodic table"
    },
    "tau": {
      "type": "string",
      "description": "Canonical τ notation encoding all dimensions",
      "pattern": "^τ\\\\(.+\\\\)$",
      "examples": ["τ(Method:Query:App:IO:SL:R:U:92)"]
    },
    "dimensions": {
      "$ref": "#/$defs/dimensions",
      "description": "8-dimensional semantic classification"
    },
    "level": {
      "$ref": "levels.schema.json",
      "description": "Holarchy level (L-3 to L12)"
    },
    "plane": {
      "enum": ["Physical", "Virtual", "Semantic"],
      "description": "Popper's world mapping"
    },
    "location": {
      "$ref": "#/$defs/location",
      "description": "Source code location"
    },
    "metadata": {
      "$ref": "#/$defs/metadata",
      "description": "Additional extracted information"
    },
    "edges_out": {
      "type": "array",
      "items": { "$ref": "edge.schema.json" },
      "description": "Outgoing relationships from this particle"
    }
  },
  "$defs": {
    "dimensions": {
      "type": "object",
      "required": ["D1_WHAT", "D2_LAYER", "D3_ROLE"],
      "properties": {
        "D1_WHAT": {
          "type": "string",
          "description": "Atom type (same as top-level atom)"
        },
        "D2_LAYER": {
          "enum": ["Interface", "Application", "Core", "Infrastructure", "Test", "Unknown"],
          "description": "Clean Architecture layer"
        },
        "D3_ROLE": {
          "$ref": "roles.schema.json",
          "description": "DDD tactical role"
        },
        "D4_BOUNDARY": {
          "enum": ["Internal", "Input", "Output", "I-O"],
          "description": "Information flow boundary"
        },
        "D5_STATE": {
          "enum": ["Stateful", "Stateless"],
          "description": "State management characteristic"
        },
        "D6_EFFECT": {
          "enum": ["Pure", "Read", "Write", "ReadWrite"],
          "description": "Side effect classification"
        },
        "D7_LIFECYCLE": {
          "enum": ["Create", "Use", "Destroy"],
          "description": "Object lifecycle phase"
        },
        "D8_TRUST": {
          "type": "number",
          "minimum": 0,
          "maximum": 100,
          "description": "Classification confidence percentage"
        }
      }
    },
    "location": {
      "type": "object",
      "required": ["file", "line_start", "line_end"],
      "properties": {
        "file": { "type": "string" },
        "line_start": { "type": "integer", "minimum": 1 },
        "line_end": { "type": "integer", "minimum": 1 },
        "col_start": { "type": "integer", "minimum": 0 },
        "col_end": { "type": "integer", "minimum": 0 }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "qualified_name": { "type": "string" },
        "signature": { "type": "string" },
        "docstring": { "type": "string" },
        "decorators": { "type": "array", "items": { "type": "string" } },
        "parameters": { "type": "array", "items": { "type": "string" } },
        "return_type": { "type": "string" },
        "complexity": { "type": "number" },
        "lines_of_code": { "type": "integer" }
      }
    }
  }
}
```

**Deliverable**: `schema/particle.schema.json`

---

### 1.2 Edge Schema (Day 4)

**Objective**: Define relationship schema.

**Schema Definition**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://standardmodelofcode.org/schemas/edge.json",
  "title": "Standard Model Edge",
  "description": "A typed relationship between two particles",
  "type": "object",
  "required": ["target", "type", "family"],
  "properties": {
    "target": {
      "type": "string",
      "description": "Target particle ID"
    },
    "type": {
      "$ref": "#/$defs/edge_types",
      "description": "Specific edge type"
    },
    "family": {
      "enum": ["Structural", "Dependency", "Inheritance", "Semantic", "Temporal"],
      "description": "One of 5 edge families"
    },
    "weight": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Edge strength (0-1)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 100,
      "description": "Detection confidence"
    },
    "location": {
      "type": "object",
      "properties": {
        "file": { "type": "string" },
        "line": { "type": "integer" }
      },
      "description": "Where this relationship is established"
    }
  },
  "$defs": {
    "edge_types": {
      "enum": [
        "calls", "imports", "uses", "references",
        "inherits", "implements", "extends", "mixes",
        "contains", "is_part_of", "returns", "receives",
        "precedes", "follows", "triggers", "blocks",
        "similar_to", "coupled_with", "depends_on"
      ]
    }
  }
}
```

**Deliverable**: `schema/edge.schema.json`

---

### 1.3 Graph Schema (Day 5)

**Objective**: Define full codebase graph schema.

**Schema Definition**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://standardmodelofcode.org/schemas/graph.json",
  "title": "Standard Model Graph",
  "description": "Complete codebase represented as classified particles and typed edges",
  "type": "object",
  "required": ["version", "generated_at", "repository", "particles"],
  "properties": {
    "version": {
      "type": "string",
      "const": "1.0.0"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "repository": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "root": { "type": "string" },
        "languages": { "type": "array", "items": { "type": "string" } },
        "commit": { "type": "string" }
      }
    },
    "statistics": {
      "type": "object",
      "properties": {
        "total_particles": { "type": "integer" },
        "total_edges": { "type": "integer" },
        "per_level": { "type": "object" },
        "per_layer": { "type": "object" },
        "per_phase": { "type": "object" }
      }
    },
    "particles": {
      "type": "array",
      "items": { "$ref": "particle.schema.json" }
    }
  }
}
```

**Deliverable**: `schema/graph.schema.json`

---

### 1.4 Reference Schemas (Day 6)

**Objective**: Create enum/reference schemas.

Files to create:
- `atoms.schema.json` - All 200 atom types (from C1)
- `dimensions.schema.json` - D1-D8 definitions
- `levels.schema.json` - L-3 to L12 enum
- `roles.schema.json` - 33 roles with descriptions
- `edges.schema.json` - 5 edge families with types

**Deliverable**: All reference schema files

---

## Phase 2: Type Generation (Week 2-3)

### 2.1 TypeScript Types (Day 7)

**Objective**: Generate TypeScript types from JSON schemas.

**Using**: `json-schema-to-typescript`

**Generated Output** (`types.ts`):
```typescript
// Auto-generated from Standard Model JSON schemas

export type Level = 'L-3' | 'L-2' | 'L-1' | 'L0' | 'L1' | 'L2' | 'L3' | 'L4' 
  | 'L5' | 'L6' | 'L7' | 'L8' | 'L9' | 'L10' | 'L11' | 'L12';

export type Plane = 'Physical' | 'Virtual' | 'Semantic';

export type Layer = 'Interface' | 'Application' | 'Core' | 'Infrastructure' | 'Test';

export type Effect = 'Pure' | 'Read' | 'Write' | 'ReadWrite';

export interface Dimensions {
  D1_WHAT: string;
  D2_LAYER: Layer;
  D3_ROLE: Role;
  D4_BOUNDARY?: 'Internal' | 'Input' | 'Output' | 'I-O';
  D5_STATE?: 'Stateful' | 'Stateless';
  D6_EFFECT?: Effect;
  D7_LIFECYCLE?: 'Create' | 'Use' | 'Destroy';
  D8_TRUST?: number;
}

export interface Location {
  file: string;
  line_start: number;
  line_end: number;
  col_start?: number;
  col_end?: number;
}

export interface Particle {
  id: string;
  atom: Atom;
  tau?: string;
  dimensions: Dimensions;
  level: Level;
  plane: Plane;
  location: Location;
  metadata?: ParticleMetadata;
  edges_out?: Edge[];
}

export interface Edge {
  target: string;
  type: EdgeType;
  family: EdgeFamily;
  weight?: number;
  confidence?: number;
}

export interface Graph {
  version: '1.0.0';
  generated_at: string;
  repository: Repository;
  statistics?: GraphStatistics;
  particles: Particle[];
}
```

**Deliverable**: `schema/types.ts`

---

### 2.2 Python Types (Day 8)

**Objective**: Generate Python dataclasses/Pydantic models.

**Using**: `datamodel-code-generator`

**Generated Output** (`types.py`):
```python
"""Auto-generated from Standard Model JSON schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime

class Level(str, Enum):
    L_3 = "L-3"
    L_2 = "L-2"
    L_1 = "L-1"
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"
    L5 = "L5"
    L6 = "L6"
    L7 = "L7"
    L8 = "L8"
    L9 = "L9"
    L10 = "L10"
    L11 = "L11"
    L12 = "L12"

class Plane(str, Enum):
    PHYSICAL = "Physical"
    VIRTUAL = "Virtual"
    SEMANTIC = "Semantic"

class Layer(str, Enum):
    INTERFACE = "Interface"
    APPLICATION = "Application"
    CORE = "Core"
    INFRASTRUCTURE = "Infrastructure"
    TEST = "Test"

@dataclass
class Dimensions:
    D1_WHAT: str
    D2_LAYER: Layer
    D3_ROLE: str
    D4_BOUNDARY: Optional[str] = None
    D5_STATE: Optional[str] = None
    D6_EFFECT: Optional[str] = None
    D7_LIFECYCLE: Optional[str] = None
    D8_TRUST: Optional[float] = None

@dataclass
class Location:
    file: str
    line_start: int
    line_end: int
    col_start: Optional[int] = None
    col_end: Optional[int] = None

@dataclass
class Edge:
    target: str
    type: str
    family: str
    weight: Optional[float] = None
    confidence: Optional[float] = None

@dataclass
class Particle:
    id: str
    atom: str
    dimensions: Dimensions
    level: Level
    plane: Plane
    location: Location
    tau: Optional[str] = None
    metadata: Optional[dict] = None
    edges_out: List[Edge] = field(default_factory=list)

@dataclass
class Graph:
    version: str
    generated_at: datetime
    repository: dict
    particles: List[Particle]
    statistics: Optional[dict] = None
```

**Deliverable**: `schema/types.py`

---

## Phase 3: Validation & Documentation (Week 3)

### 3.1 Schema Validation Tests (Day 9-10)

**Objective**: Create tests that verify schema correctness.

**Tests to Create**:
```python
# tests/test_schema_validation.py

def test_particle_valid():
    """Valid particle should pass validation."""
    particle = {
        "id": "test.py::MyClass.my_method",
        "atom": "Fn_Method",
        "dimensions": {
            "D1_WHAT": "Fn_Method",
            "D2_LAYER": "Core",
            "D3_ROLE": "Query"
        },
        "level": "L3",
        "plane": "Semantic",
        "location": {"file": "test.py", "line_start": 10, "line_end": 20}
    }
    assert validate_particle(particle) is True

def test_particle_missing_required():
    """Missing required field should fail."""
    particle = {"id": "test.py::foo"}  # Missing atom, dimensions, etc.
    with pytest.raises(ValidationError):
        validate_particle(particle)

def test_edge_types_valid():
    """All edge types should be recognized."""
    for edge_type in ["calls", "imports", "inherits", "contains"]:
        edge = {"target": "x", "type": edge_type, "family": "Structural"}
        assert validate_edge(edge) is True

def test_graph_with_particles():
    """Full graph should validate."""
    graph = {...}  # Full example
    assert validate_graph(graph) is True
```

**Deliverable**: `tests/test_schema_validation.py`

---

### 3.2 Schema Documentation (Day 11)

**Objective**: Create comprehensive schema documentation.

**Documentation to Generate**:
1. **README.md** - Overview, quick start, examples
2. **API Reference** - Auto-generated from schemas
3. **Examples** - Sample particles for common patterns
4. **Migration Guide** - For future schema versions

**Deliverable**: `schema/README.md`, `schema/EXAMPLES.md`

---

### 3.3 Integration with Collider (Day 12)

**Objective**: Update Collider to use the formal schema.

**Changes**:
1. Import generated types in `core/`
2. Validate output against schema before writing
3. Add `--validate` flag to CLI
4. Update output format to match schema exactly

**Deliverable**: Updated Collider with schema integration

---

## Deliverables

| Deliverable | Path | Description |
|-------------|------|-------------|
| Particle Schema | `/schema/particle.schema.json` | Core entity definition |
| Edge Schema | `/schema/edge.schema.json` | Relationship definition |
| Graph Schema | `/schema/graph.schema.json` | Full codebase format |
| Reference Schemas | `/schema/*.schema.json` | Enums and references |
| TypeScript Types | `/schema/types.ts` | TS type definitions |
| Python Types | `/schema/types.py` | Python dataclasses |
| Validation Tests | `/tests/test_schema_validation.py` | Schema tests |
| Documentation | `/schema/README.md` | Usage guide |

---

## Success Criteria

- [ ] All schemas pass JSON Schema 2020-12 validation
- [ ] TypeScript types compile without errors
- [ ] Python types pass mypy type checking
- [ ] All 200 atoms defined in atoms.schema.json
- [ ] Collider output validates against graph.schema.json
- [ ] Documentation complete with examples

---

## Dependencies

- **Depends on**: C1 (Atom Enumeration) - need atom list for atoms.schema.json
- **Blocks**: C3 (Training Corpus) - training data must follow schema
- **Parallel**: Can start Phase 1 while C1 is in progress

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema too complex for AI | High | Keep flat where possible, add examples |
| Breaking changes needed | Medium | Version from start (1.0.0) |
| TypeScript/Python generation fails | Low | Write types manually if needed |
