# Invocation Manifestation Analysis: Φ-Space Theory vs Current Standard Model

**Date:** 2026-01-28
**Purpose:** Compare newly discovered Φ-space theory against existing Standard Model
**Status:** PRE-VALIDATION (requires Perplexity research + peer review)

---

## Executive Summary

**Discovery:** Service/Tool/Library are not discrete categories but **manifestations of code in different invocation contexts (Φ)**.

**Key Insight:** Same code can manifest as Service, Tool, OR Library depending on invocation context - like wave-particle duality in physics.

**Current Theory Status:** Standard Model HAS pieces (D7 Activation, D8 Lifetime) but LACKS unified Φ-space framework.

---

## Part 1: What We Discovered (2026-01-28 Session)

### The Φ-Space Framework

**Core Proposition:**
```
Manifestation = f(Code, Φ)

Where:
- Code ∈ C (code space - what Collider sees)
- Φ ∈ Φ (invocation context space)
- Manifestation ∈ {Service, Tool, Library, Daemon, ...}
```

**Key Dimensions of Φ:**

| Dimension | Range | Examples |
|-----------|-------|----------|
| **Network Accessibility** | [0.0, 1.0] | 0.0=local, 1.0=networked |
| **Process Boundary** | {embedded, isolated, distributed} | Library=embedded, Service=isolated |
| **Lifecycle** | {ephemeral, scheduled, persistent, reactive} | Tool=ephemeral, Service=persistent |
| **Consumer Pattern** | {single, multiple, broadcast} | Tool=single, Service=multiple |
| **State Model** | {stateless, stateful, transactional} | Service=often stateless |
| **Invocation Mechanism** | {CLI, import, network, schedule, event} | Tool=CLI, Service=network |

**Named Manifestations** (landmarks in Φ-space):

1. **SERVICE**
   - Φ = {network: 0.9, process: isolated, lifecycle: persistent, consumers: multiple}
   - Example: GraphRAG (Neo4j), AWS S3, PaymentService

2. **TOOL**
   - Φ = {network: 0.0, process: isolated, lifecycle: ephemeral, consumers: single}
   - Example: aws cli, migrate-database, collider

3. **LIBRARY**
   - Φ = {network: N/A, process: embedded, lifecycle: N/A, consumers: single}
   - Example: numpy, lodash, standard library

4. **DAEMON**
   - Φ = {network: 0.0, process: isolated, lifecycle: persistent, consumers: single}
   - Example: filesystem_watcher, systemd services

5. **SERVERLESS FUNCTION**
   - Φ = {network: 0.7, process: distributed, lifecycle: ephemeral, consumers: multiple}
   - Example: AWS Lambda, Cloud Functions

6. **MESSAGE HANDLER**
   - Φ = {network: 0.5, process: isolated, lifecycle: reactive, consumers: multiple}
   - Example: Kafka consumer, RabbitMQ handler

**Critical Properties:**

1. **NOT mutually exclusive** - Same code can occupy multiple manifestations simultaneously
2. **Continuous space** - Φ-space is multi-dimensional and continuous (not discrete categories)
3. **Context-dependent** - Manifestation emerges from invocation context, not code properties alone

### Example: scanner.py in Dual Space

```python
# scanner.py - SAME CODE, three manifestations

def scan_files(path):
    """Core scanning logic"""
    return files

# Manifestation 1: As TOOL (CLI invocation)
if __name__ == "__main__":
    result = scan_files(sys.argv[1])  # Φ_tool
    print(result)

# Manifestation 2: As LIBRARY (import)
from scanner import scan_files  # Φ_library

# Manifestation 3: As SERVICE (wrapped in FastAPI)
@app.get("/scan")
def scan_endpoint(path: str):
    return scan_files(path)  # Φ_service
```

**Same code. Different Φ. Different manifestation.**

---

## Part 2: What Current Standard Model Says

### Evidence from analyze.py Query (2026-01-28)

**Source:** RAG search over `collider-docs` store
**Model:** gemini-3-pro-preview

**Findings:**

#### ✅ EXISTING: Related Dimensions

1. **D7 ACTIVATION** - How component is invoked
   - Direct (function call)
   - Event-Driven (message trigger)
   - Scheduled (cron)
   - **Maps to:** Invocation Mechanism in Φ-space

2. **D8 LIFETIME** - Deployment/lifetime scope
   - Transient (per-request)
   - Singleton (application lifetime)
   - Deployable (unit of shipping)
   - **Maps to:** Lifecycle in Φ-space

3. **D3 ROLE** - Purpose/responsibility
   - Service is one of 33 canonical roles
   - Under "Orchestration" category
   - **Maps to:** Partially overlaps with manifestation

4. **L6 PACKAGE** - Library as structural level
   - Library = Level 6 in 16-level scale
   - Corresponds to Module/Folder
   - **Maps to:** Package structure, not manifestation

5. **ATOM TYPES** - Tool mentioned as execution family
   - Worker, Probe, Utility atoms
   - **Maps to:** Atom classification, not manifestation

#### ❌ MISSING: Φ-Space Concepts

1. **No unified invocation context framework** (Φ-space)
2. **No network accessibility as fundamental dimension**
3. **No process boundary as ontological property**
4. **No manifestation duality/multiplicity concept**
5. **No continuous Φ-space (only discrete dimensions)**
6. **No explicit Service vs Tool vs Library as manifestations**

#### 🟡 PARTIAL: Situation Formula

**Existing:**
```
Situation = Role (33) × Layer (4) × Lifecycle (3) × RPBL (6,561) × Domain (∞)
```

**What it captures:**
- Role (D3) - includes "Service" role
- Lifecycle - partial overlap with D8 Lifetime
- Layer (D2) - architectural layer (Clean Architecture)

**What it misses:**
- Invocation mechanism (CLI vs network vs import)
- Process boundary (embedded vs isolated)
- Consumer pattern (single vs multiple)
- **These are NOT the same as existing dimensions**

---

## Part 3: Gap Analysis

### What Standard Model Has

| Concept | Standard Model | Φ-Space Theory | Overlap? |
|---------|----------------|----------------|----------|
| Invocation trigger | D7 Activation (3 types) | Invocation Mechanism (6+ types) | ⚠️ Partial |
| Deployment lifetime | D8 Lifetime | Lifecycle dimension | ⚠️ Partial |
| Service concept | D3 Role = Service | Service manifestation | ⚠️ Different semantics |
| Library concept | L6 Package level | Library manifestation | ❌ No - different concepts |
| Tool concept | Atom type (Worker) | Tool manifestation | ❌ No - different concepts |
| Process boundary | ❌ Not modeled | Process dimension | ❌ Missing |
| Network accessibility | ❌ Not modeled | Network dimension | ❌ Missing |
| Consumer pattern | ❌ Not modeled | Consumer dimension | ❌ Missing |
| Context space | Situation formula | Φ-space | ⚠️ Overlaps but different |
| Manifestation duality | ❌ Not modeled | Core concept | ❌ Missing |

### Key Differences in Semantics

#### 1. "Service" Means Different Things

**Standard Model D3 ROLE:**
- Service = one of 33 roles (Orchestrator category)
- **What it does** (coordinates other atoms)
- Mutually exclusive with other roles

**Φ-Space Manifestation:**
- Service = network-accessible, persistent, multi-consumer
- **How it's invoked** (deployment model)
- NOT mutually exclusive (same code can be Service AND Tool)

#### 2. "Tool" Means Different Things

**Standard Model Atom Type:**
- Tool = execution family atom (Worker, Probe, Utility)
- **What it IS** (structural classification)
- Source code level

**Φ-Space Manifestation:**
- Tool = CLI-invoked, ephemeral, single-consumer
- **How it's deployed** (invocation pattern)
- Runtime level

#### 3. "Library" Means Different Things

**Standard Model L6 Level:**
- Library = Package/Module level in 16-level hierarchy
- **Structural scale** (between File and System)
- Static structure

**Φ-Space Manifestation:**
- Library = embedded, no process boundary
- **Deployment model** (linked into host)
- Runtime behavior

### What's Actually Missing

**Gap 1: Network Accessibility** (fundamental dimension)
- Not in D1-D8
- Critical for Service vs Tool distinction
- Martin Fowler: "Service = out-of-process component"

**Gap 2: Process Boundary** (ontological property)
- Not in D1-D8
- Determines embedded vs isolated
- Library (embedded) vs Service/Tool (isolated)

**Gap 3: Consumer Pattern** (architectural property)
- Not in D1-D8
- Single consumer vs multiple consumers
- Critical for service design

**Gap 4: Manifestation Framework** (meta-theory)
- No concept that same code manifests differently in different contexts
- No Φ-space (invocation context space)
- No wave-particle duality analog

**Gap 5: Continuous vs Discrete**
- Current: Discrete dimensions with fixed domains
- Φ-space: Continuous dimensions (network: 0.0-1.0, not binary)
- Allows gray areas (AWS Lambda = hybrid Service-Tool)

---

## Part 4: Integration Proposal

### Option A: Extend Existing Dimensions

Add 3 new dimensions to D1-D8:

```
D9 NETWORK_ACCESSIBILITY: [0.0, 1.0]
  - 0.0 = local-only (Tool, Daemon)
  - 0.5 = hybrid (Lambda, edge functions)
  - 1.0 = fully networked (Service, API)

D10 PROCESS_BOUNDARY: {embedded, isolated, distributed}
  - embedded = Library (no process boundary)
  - isolated = Service/Tool (separate process)
  - distributed = Microservice (multi-node)

D11 CONSUMER_PATTERN: {single, multiple, broadcast}
  - single = Tool (one user)
  - multiple = Service (many consumers)
  - broadcast = Pub/sub (all subscribers)
```

**Pro:** Extends existing framework cleanly
**Con:** Doesn't capture manifestation duality concept

### Option B: Add New Layer - Φ-Space Axioms

Create new axiom group in L0_AXIOMS.md:

```
A9: INVOCATION CONTEXT (Φ-Space)

A9.1: Code exists in potential state
A9.2: Manifestation = f(Code, Φ) where Φ ∈ Φ-space
A9.3: Φ-space has dimensions {network, process, lifecycle, consumers, ...}
A9.4: Same code can manifest in multiple contexts (non-exclusive)
A9.5: Named manifestations are landmarks in continuous Φ-space

Definitions:
- Service: High network, isolated process, persistent, multi-consumer
- Tool: No network, isolated process, ephemeral, single-consumer
- Library: Embedded process (no boundary), lifecycle coupled to host
```

**Pro:** Captures duality/multiplicity concept
**Con:** Major theoretical addition (needs validation)

### Option C: Reinterpret Existing (Minimal)

Clarify that D7/D8 already capture this:

```
D7 ACTIVATION + D8 LIFETIME = invocation context

Service = {D7: Network-triggered, D8: Persistent}
Tool = {D7: Direct-call, D8: Transient}
Library = {Special case: embedded, no D7/D8 apply}
```

**Pro:** No new theory needed
**Con:** Doesn't explain manifestation duality or continuous space

### Option D: Hybrid - Add Manifestation as Meta-Property

Don't add dimensions, add MANIFESTATION as emergent property:

```
Manifestation emerges from (D7, D8, D3) combination

M: (D7 × D8 × D3) → {Service, Tool, Library, ...}

Where:
- Service = {Activation: network, Lifetime: persistent, Role: orchestrator}
- Tool = {Activation: direct, Lifetime: transient, Role: worker}
- Library = {Special: embedded context}
```

**Pro:** Explains emergence, uses existing dimensions
**Con:** Doesn't explain why same code can be both simultaneously

---

## Part 5: Validation Questions for Perplexity

### Research Needed

1. **Is invocation context a recognized concept in CS literature?**
   - Search: "invocation context", "execution context", "deployment context"
   - Verify: Do authoritative sources distinguish invocation from structure?

2. **Is Service/Tool duality documented?**
   - Search: "service vs tool architecture", "deployment duality"
   - Verify: Does AWS CLI wrapping S3 have a name for this pattern?

3. **Is Φ-space continuous or discrete?**
   - Search: "continuous architectural space", "gradients in deployment models"
   - Verify: Is AWS Lambda considered hybrid or discrete category?

4. **Do existing frameworks model manifestation?**
   - Search: "same code different contexts", "code manifestation patterns"
   - Verify: CORBA, DCOM, RMI - did they formalize this?

5. **Is network accessibility a fundamental dimension?**
   - Search: "network boundary software architecture", "Martin Fowler process boundary"
   - Verify: Is "out-of-process" considered ontological or practical?

6. **How do academics classify software components?**
   - Search: "software component taxonomy", "architectural classification schemes"
   - Verify: Do IEEE, ACM, ISO standards address this?

7. **Is there precedent for wave-particle duality analog?**
   - Search: "duality in software engineering", "complementary views code"
   - Verify: Has anyone proposed physics analogs for deployment?

8. **What about emerging categories?**
   - Search: "serverless architecture classification", "edge computing taxonomy"
   - Verify: How are Lambda, edge functions, smart contracts classified?

---

## Part 6: Next Steps

### Immediate (Pre-Validation)

1. ✅ Document discovery (this file)
2. ⏳ Create comprehensive Perplexity research query
3. ⏳ Execute research ($60-80 cost, 8+ sources needed)
4. ⏳ Analyze research results against Φ-space theory

### Post-Validation (If Confirmed)

1. **Update L0_AXIOMS.md** - Add A9: Invocation Context
2. **Update L1_DEFINITIONS.md** - Define Φ-space, manifestations
3. **Extend atom classification** - Add manifestation metadata
4. **Update Collider** - Detect manifestation from code structure + deployment hints
5. **Create visualization** - Φ-space as 3D projection in dashboard

### Post-Validation (If Refuted/Modified)

1. Identify which parts are valid
2. Integrate valid parts into existing D7/D8
3. Document why full Φ-space theory didn't hold
4. Update this analysis with corrections

---

## Part 7: Confidence Assessment

| Claim | Confidence | Evidence |
|-------|-----------|----------|
| Service/Tool ARE different | 95% | Perplexity research (60+ sources) |
| Difference is invocation context | 85% | Martin Fowler, AWS architecture |
| Same code can be both | 90% | scanner.py example, AWS CLI pattern |
| Φ-space is continuous | 70% | Intuition, needs validation |
| Current theory missing this | 90% | analyze.py search + THEORY_INDEX read |
| Should add to Standard Model | 75% | Needs peer review + Perplexity validation |
| Wave-particle analog valid | 60% | Metaphor, not physics |
| 18+ categories exist | 80% | Empirically observed (Lambda, webhook, etc.) |
| Network accessibility fundamental | 85% | Core to Service definition (Fowler) |
| Process boundary ontological | 90% | Library vs Service is about boundaries |

**Overall Assessment:** 80% confidence this is valid and should be added to theory.

**Blocking Risk:** If Perplexity research finds that invocation context is NOT recognized in literature, may need to reframe as "deployment model" or "execution mode" instead.

---

## Part 8: References

### Session Context
- Date: 2026-01-28
- Conversation: GraphRAG architectural decision (service vs tool)
- Perplexity Query 1: "Service vs Tool distinction" (60+ sources)
- analyze.py Query: Current Standard Model content

### Standard Model Documents
- `standard-model-of-code/docs/theory/THEORY_INDEX.md` (v2.0.0)
- `standard-model-of-code/docs/theory/L0_AXIOMS.md`
- `standard-model-of-code/docs/theory/L1_DEFINITIONS.md`
- Current dimensions: D1-D8 defined in L1

### External Sources (From Perplexity Research)
- Martin Fowler: "Microservices" (2014) - Service = out-of-process component
- AWS Architecture patterns
- SOA literature (60+ citations)

### Next Research
- ⏳ Comprehensive Perplexity query (to be executed)
- ⏳ Academic CS literature search
- ⏳ Industry framework analysis (Spring, .NET, etc.)

---

**END OF ANALYSIS**

**Status:** Pre-validation
**Next Action:** Execute comprehensive Perplexity research query
**Decision Point:** Integrate into Standard Model if research validates (>80% confidence)
