# PROJECTOME OMNISCIENCE MODULE (POM)
# Complete Visibility Across the Entire Project Universe

> **Status:** SPECIFICATION
> **Created:** 2026-01-25
> **Purpose:** Universal inventory and purpose analysis for PROJECTOME
> **Grounded In:** Lawvere's Fixed-Point Theorem (P = C ⊔ X is necessary)

---

## Abstract

The **Projectome Omniscience Module (POM)** provides complete visibility into the entire PROJECTOME - the union of CODOME (executable code) and CONTEXTOME (non-executable content). It applies Purpose Field analysis across both universes to create a unified understanding of the project.

**Key Property:** POM includes itself in its inventory (Lawvere fixed point).

---

## 1. THE OMNISCIENCE PRINCIPLE

### 1.1 Definition

```
OMNISCIENCE = Complete knowledge of PROJECTOME at all levels

POM : PROJECTOME → MANIFEST
WHERE:
  - PROJECTOME = CODOME ⊔ CONTEXTOME
  - MANIFEST = Structured inventory with purpose annotations
  - POM ∈ CONTEXTOME (the module is part of what it inventories)
```

### 1.2 The Fixed Point Property

```
POM inventories PROJECTOME
POM ∈ PROJECTOME
∴ POM inventories itself

This is not a paradox - it's a FIXED POINT (Lawvere)
```

### 1.3 Levels of Omniscience

| Level | Scope | What It Sees |
|-------|-------|--------------|
| L0 | File | Individual files exist |
| L1 | Entity | Functions, classes, docs, configs |
| L2 | Relationship | Edges, references, links |
| L3 | Purpose | Role, intent, meaning |
| L4 | Field | Gradients, flows, patterns |
| L5 | Meta | The inventory itself |

---

## 2. ARCHITECTURE

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECTOME OMNISCIENCE MODULE                 │
│                                                                  │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │   CODOME SCANNER   │         │ CONTEXTOME SCANNER │         │
│  │                    │         │                    │         │
│  │  • Collider output │         │  • File walker     │         │
│  │  • unified.json    │         │  • Markdown parser │         │
│  │  • AST analysis    │         │  • YAML/JSON loader│         │
│  └─────────┬──────────┘         └─────────┬──────────┘         │
│            │                              │                     │
│            └──────────────┬───────────────┘                     │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │   MERGER    │                              │
│                    │             │                              │
│                    │  P = C ⊔ X  │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │   PURPOSE   │                              │
│                    │   ANALYZER  │                              │
│                    │             │                              │
│                    │  𝒫: P → ℝᵏ  │                              │
│                    └──────┬──────┘                              │
│                           │                                     │
│                    ┌──────▼──────┐                              │
│                    │  MANIFEST   │                              │
│                    │  GENERATOR  │                              │
│                    │             │                              │
│                    │ (includes   │                              │
│                    │  itself)    │                              │
│                    └─────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. SCAN CODOME
   └── Run Collider → unified_analysis.json
   └── Extract: nodes, edges, atoms, roles

2. SCAN CONTEXTOME
   └── Walk docs/, config/, .agent/
   └── Parse: .md, .yaml, .json
   └── Extract: sections, links, definitions

3. MERGE INTO PROJECTOME
   └── Verify: C ∩ X = ∅
   └── Combine: P = C ⊔ X
   └── Link: Cross-references between C and X

4. APPLY PURPOSE FIELD
   └── Compute: Purpose vectors for all entities
   └── Detect: Purpose gradients, orphans, phantoms
   └── Score: Symmetry states (SYMMETRIC, ORPHAN, PHANTOM, DRIFT)

5. GENERATE MANIFEST
   └── Include: All entities at all levels
   └── Include: Self-reference (POM entry)
   └── Output: projectome_manifest.yaml
```

---

## 3. DATA STRUCTURES

### 3.1 Unified Entity Schema

```yaml
# Every entity in PROJECTOME follows this schema
entity:
  id: string                    # Unique identifier
  universe: codome | contextome # Which universe
  type: string                  # Entity type (function, class, doc, config)
  path: string                  # File path
  location:                     # Position in file
    start_line: int
    end_line: int
    section: string             # For docs: heading

  # Purpose (Level 3)
  purpose:
    role: string                # Semantic role (33 canonical)
    intent: string              # Natural language purpose
    confidence: float           # 0.0 - 1.0
    layer: string               # Architectural layer

  # Relationships (Level 2)
  edges:
    - target: string            # Target entity ID
      type: string              # calls, imports, describes, references
      universe_crossing: bool   # Does it cross C↔X boundary?

  # Symmetry (Level 4)
  symmetry:
    state: symmetric | orphan | phantom | drift
    pair_id: string | null      # Matching entity in other universe
    drift_score: float          # 0.0 = aligned, 1.0 = fully drifted
```

### 3.2 Projectome Manifest Schema

```yaml
# projectome_manifest.yaml
manifest:
  generated: datetime
  generator: POM v1.0
  self_reference: true          # Fixed point property

  universes:
    codome:
      count: int
      files: int
      nodes: int
      edges: int
    contextome:
      count: int
      files: int
      sections: int
      definitions: int

  totals:
    entities: int               # |P| = |C| + |X|
    relationships: int
    cross_universe_links: int

  symmetry:
    symmetric: int              # Paired entities
    orphan: int                 # Code without docs
    phantom: int                # Docs without code
    drift: int                  # Misaligned pairs

  purpose_field:
    coverage: float             # % entities with purpose
    coherence: float            # Average coherence score
    entropy: float              # Purpose field entropy

  entities: []                  # Full entity list (see 3.1)
```

---

## 4. CODOME SCANNER

### 4.1 Input: Collider Output

```python
def scan_codome(unified_analysis_path: str) -> List[Entity]:
    """
    Extract entities from Collider's unified_analysis.json
    """
    with open(unified_analysis_path) as f:
        data = json.load(f)

    entities = []
    for node in data['nodes']:
        entities.append(Entity(
            id=node['id'],
            universe='codome',
            type=node['kind'],
            path=node['file_path'],
            location=Location(
                start_line=node['start_line'],
                end_line=node['end_line']
            ),
            purpose=Purpose(
                role=node.get('semantic_role', 'unknown'),
                intent=node.get('docstring', ''),
                confidence=node.get('purpose_confidence', 0.0),
                layer=node.get('layer', 'unknown')
            ),
            edges=[
                Edge(target=e['target'], type=e['type'])
                for e in node.get('edges', [])
            ]
        ))

    return entities
```

### 4.2 Codome Entity Types

| Type | Description | Source |
|------|-------------|--------|
| `function` | Function/method | AST |
| `class` | Class definition | AST |
| `module` | Python module | File |
| `variable` | Module-level variable | AST |
| `import` | Import statement | AST |
| `constant` | Named constant | Pattern |

---

## 5. CONTEXTOME SCANNER

### 5.1 File Discovery

```python
def scan_contextome(root_path: str) -> List[Entity]:
    """
    Walk directories and parse non-executable files
    """
    entities = []

    # Documentation
    for md_file in glob(f"{root_path}/**/docs/**/*.md"):
        entities.extend(parse_markdown(md_file))

    # Configuration
    for yaml_file in glob(f"{root_path}/**/*.yaml"):
        if not is_code_adjacent(yaml_file):
            entities.extend(parse_yaml(yaml_file))

    for json_file in glob(f"{root_path}/**/config/**/*.json"):
        entities.extend(parse_json_config(json_file))

    # Agent artifacts
    for agent_file in glob(f"{root_path}/.agent/**/*"):
        entities.extend(parse_agent_artifact(agent_file))

    # Research outputs
    for research_file in glob(f"{root_path}/**/research/**/*"):
        entities.extend(parse_research(research_file))

    return entities
```

### 5.2 Markdown Parser

```python
def parse_markdown(file_path: str) -> List[Entity]:
    """
    Extract entities from Markdown documentation
    """
    with open(file_path) as f:
        content = f.read()

    entities = []

    # Document entity
    entities.append(Entity(
        id=f"doc::{file_path}",
        universe='contextome',
        type='document',
        path=file_path,
        purpose=Purpose(
            role='documentation',
            intent=extract_first_sentence(content)
        )
    ))

    # Section entities
    for heading in extract_headings(content):
        entities.append(Entity(
            id=f"section::{file_path}::{heading.slug}",
            universe='contextome',
            type='section',
            path=file_path,
            location=Location(
                start_line=heading.line,
                section=heading.text
            ),
            purpose=Purpose(
                role='section',
                intent=heading.text
            )
        ))

    # Definition entities (from tables, glossaries)
    for definition in extract_definitions(content):
        entities.append(Entity(
            id=f"def::{file_path}::{definition.term}",
            universe='contextome',
            type='definition',
            path=file_path,
            purpose=Purpose(
                role='definition',
                intent=definition.meaning
            )
        ))

    # Code references (links to CODOME)
    for ref in extract_code_references(content):
        entities[-1].edges.append(Edge(
            target=ref.target,
            type='describes',
            universe_crossing=True
        ))

    return entities
```

### 5.3 Contextome Entity Types

| Type | Description | Source |
|------|-------------|--------|
| `document` | Markdown file | File |
| `section` | Heading + content | Parser |
| `definition` | Term definition | Tables/glossaries |
| `config` | Configuration item | YAML/JSON |
| `task` | Task registry entry | .agent/registry |
| `research` | AI output | research/ |
| `schema` | JSON schema | schema/ |

---

## 6. SYMMETRY DETECTION

### 6.1 Cross-Universe Linking

```python
def detect_symmetry(codome: List[Entity], contextome: List[Entity]) -> SymmetryReport:
    """
    Find pairs and classify symmetry states
    """
    pairs = []
    orphans = []
    phantoms = []
    drifted = []

    # Build lookup maps
    code_by_name = {e.name: e for e in codome}
    doc_refs = extract_all_references(contextome)

    for code_entity in codome:
        # Look for documentation that references this code
        matching_docs = find_docs_for_code(code_entity, contextome)

        if not matching_docs:
            orphans.append(code_entity)
        else:
            # Check alignment
            for doc in matching_docs:
                drift = compute_drift(code_entity, doc)
                if drift > DRIFT_THRESHOLD:
                    drifted.append((code_entity, doc, drift))
                else:
                    pairs.append((code_entity, doc))

    # Find phantoms (docs without code)
    documented_ids = {pair[0].id for pair in pairs}
    for doc_entity in contextome:
        if doc_entity.references_code:
            referenced = doc_entity.get_code_references()
            if not any(ref in code_by_name for ref in referenced):
                phantoms.append(doc_entity)

    return SymmetryReport(
        symmetric=len(pairs),
        orphan=len(orphans),
        phantom=len(phantoms),
        drift=len(drifted),
        pairs=pairs,
        orphan_list=orphans,
        phantom_list=phantoms,
        drift_list=drifted
    )
```

### 6.2 Symmetry States

| State | Code | Docs | Meaning |
|-------|------|------|---------|
| **SYMMETRIC** | Exists | Exists & Matches | Healthy |
| **ORPHAN** | Exists | Missing | Undocumented code |
| **PHANTOM** | Missing | Exists | Spec without implementation |
| **DRIFT** | Exists | Exists but Mismatched | Out of sync |

### 6.3 Drift Computation

```python
def compute_drift(code: Entity, doc: Entity) -> float:
    """
    Compute semantic drift between code and its documentation

    Returns: 0.0 (perfectly aligned) to 1.0 (completely different)
    """
    # Compare signatures
    if code.type == 'function':
        sig_match = compare_signatures(code.signature, doc.documented_signature)
    else:
        sig_match = 1.0

    # Compare purpose descriptions
    purpose_match = semantic_similarity(
        code.purpose.intent,
        doc.purpose.intent
    )

    # Compare parameter documentation
    param_match = compare_parameters(code.params, doc.params)

    # Weight and combine
    drift = 1.0 - (0.3 * sig_match + 0.5 * purpose_match + 0.2 * param_match)

    return drift
```

---

## 7. PURPOSE FIELD APPLICATION

### 7.1 Unified Purpose Analysis

```python
def apply_purpose_field(projectome: List[Entity]) -> PurposeFieldResult:
    """
    Apply Purpose Field analysis across entire PROJECTOME
    """
    # Level 1: Atomic Purpose (already in entities)

    # Level 2: Composite Purpose
    composites = group_by_container(projectome)
    for container, children in composites.items():
        container.purpose = compute_composite_purpose(children)

    # Level 3: Layer Purpose
    layers = group_by_layer(projectome)
    layer_purposes = {
        layer: compute_layer_purpose(entities)
        for layer, entities in layers.items()
    }

    # Level 4: Purpose Gradients
    gradients = compute_purpose_gradients(projectome)

    # Level 5: Field Metrics
    field_entropy = compute_field_entropy(projectome)
    field_coherence = compute_field_coherence(projectome)

    return PurposeFieldResult(
        entities=projectome,
        layer_purposes=layer_purposes,
        gradients=gradients,
        entropy=field_entropy,
        coherence=field_coherence
    )
```

### 7.2 Cross-Universe Purpose Flow

```
PURPOSE FLOW:

  CONTEXTOME (Meaning)          CODOME (Implementation)
  ─────────────────────         ──────────────────────

  THEORY.md                     purpose_field.py
      │                              │
      │ defines                      │ implements
      ▼                              ▼
  "Purpose Field                def compute_purpose():
   is a vector                      ...
   field 𝒫: N → ℝᵏ"
      │                              │
      │ specifies                    │ realizes
      ▼                              ▼
  GLOSSARY.md                   PurposeNode class
  (definitions)                 (data structure)

PURPOSE FLOWS: X → C (specs → code)
VERIFICATION FLOWS: C → X (code → docs)
```

---

## 8. MANIFEST GENERATION

### 8.1 Self-Referential Entry

```python
def generate_manifest(projectome: List[Entity], output_path: str):
    """
    Generate manifest INCLUDING ITSELF (fixed point)
    """
    # Create manifest entity
    manifest_entity = Entity(
        id="pom::manifest",
        universe='contextome',
        type='manifest',
        path=output_path,
        purpose=Purpose(
            role='meta-inventory',
            intent='Complete inventory of PROJECTOME including itself'
        ),
        edges=[
            Edge(target=e.id, type='inventories')
            for e in projectome
        ]
    )

    # Add manifest to projectome (fixed point!)
    projectome.append(manifest_entity)

    # Also add this spec document
    spec_entity = Entity(
        id="pom::spec",
        universe='contextome',
        type='specification',
        path="docs/specs/PROJECTOME_OMNISCIENCE_MODULE.md",
        purpose=Purpose(
            role='specification',
            intent='Specification of the Projectome Omniscience Module'
        )
    )
    projectome.append(spec_entity)

    # Generate YAML
    manifest = {
        'manifest': {
            'generated': datetime.now().isoformat(),
            'generator': 'POM v1.0',
            'self_reference': True,
            'fixed_point_proof': 'Lawvere 1969',
            # ... rest of manifest
        }
    }

    with open(output_path, 'w') as f:
        yaml.dump(manifest, f)
```

### 8.2 Output Files

| File | Content |
|------|---------|
| `projectome_manifest.yaml` | Complete inventory |
| `symmetry_report.yaml` | Symmetry analysis |
| `purpose_field.yaml` | Purpose vectors |
| `orphan_list.md` | Undocumented code |
| `phantom_list.md` | Unimplemented specs |

---

## 9. INTEGRATION WITH EXISTING TOOLS

### 9.1 Integration Points

| Tool | Integration | Data Flow |
|------|-------------|-----------|
| **Collider** | Input | unified_analysis.json → POM |
| **ACI** | Query | POM manifest → analyze.py context |
| **HSL** | Validation | POM → drift detection |
| **ROR** | Registry | POM → Registry of Registries |

### 9.2 CLI Interface

```bash
# Full scan
pom scan --output projectome_manifest.yaml

# Codome only
pom scan --codome-only

# Symmetry check
pom symmetry --threshold 0.3

# Purpose field
pom purpose --show-gradients

# Self-check (run on own codebase)
pom scan . --self-reference
```

---

## 10. IMPLEMENTATION PHASES

### Phase 1: Core Scanner
- [ ] Codome scanner (wraps Collider)
- [ ] Basic Contextome scanner (Markdown, YAML)
- [ ] Merger (verify disjoint, combine)

### Phase 2: Symmetry Detection
- [ ] Cross-universe reference extraction
- [ ] Pair matching algorithm
- [ ] Drift computation
- [ ] Symmetry report generation

### Phase 3: Purpose Integration
- [ ] Import from purpose_field.py
- [ ] Extend to Contextome entities
- [ ] Cross-universe purpose flow

### Phase 4: Manifest Generation
- [ ] YAML output
- [ ] Self-reference (fixed point)
- [ ] ROR integration

### Phase 5: CLI & Integration
- [ ] Command-line interface
- [ ] ACI context provider
- [ ] Dashboard/visualization

---

## 11. THEORETICAL GROUNDING

### 11.1 Why POM Is Necessary

By Lawvere's Fixed-Point Theorem:
- CODOME cannot fully specify its own meaning
- Meaning requires external CONTEXTOME
- Complete understanding requires BOTH

**Therefore:** A tool that sees ONLY code (Collider) or ONLY docs (ACI) is incomplete. POM sees BOTH.

### 11.2 The Omniscience Property

```
OMNISCIENCE = ∀e ∈ P : visible(e, POM)

For every entity in PROJECTOME, POM can see it.
Including POM itself (fixed point).
```

### 11.3 Relationship to ROR

```
ROR = Registry of all registries (categories)
POM = Inventory of all entities (instances)

ROR answers: "What KINDS of things exist?"
POM answers: "What SPECIFIC things exist?"

ROR : Categories → Count
POM : PROJECTOME → Manifest
```

---

## 12. SOURCES

- `FOUNDATIONS_INTEGRATION.md` - Proof that P = C ⊔ X is necessary
- `purpose_field.py` - Purpose Field implementation
- `PURPOSE_ONTOLOGY.md` - Purpose theory
- `CODESPACE_ALGEBRA.md` - Mathematical foundations
- `REGISTRY_OF_REGISTRIES.md` - Category enumeration

---

*Created: 2026-01-25*
*Part of Standard Model of Code*
*This document is self-referential: it specifies a system that inventories itself*
