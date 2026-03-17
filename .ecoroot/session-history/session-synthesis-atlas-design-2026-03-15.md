# Ecosystem Registry Architecture — Design Session Synthesis

> Consolidated from multi-agent design session (Claude Opus 4.6 + Gemini validation).
> Date: 2026-03-15 | Project: PROJECT_elements

---

## 1. Research Findings (15 Standards Surveyed)

Standards surveyed: Backstage, OpenAPI, AsyncAPI, MCP Registry, ODPS, SPDX 3.0, CycloneDX 1.6, W3C WoT, Schema.org, OCI, Helm, npm/PyPI/Cargo/Maven, Stripe/Shopify, App Stores, VS Code Marketplace.

### Finding 1: Nobody has solved both Identity and Connectivity in one document

| Standard    | Identity | Connectivity | Both?                                         |
|-------------|----------|--------------|-----------------------------------------------|
| Backstage   | Strong   | Strong       | Closest — but no protocol/auth/credential layer |
| SPDX 3.0    | Strong   | Strong       | Yes, but scoped to supply chain, not runtime  |
| CycloneDX   | Good     | Good         | Best for runtime, no commercial/maturity layer |
| W3C WoT     | Good     | Good         | Best protocol flexibility, IoT-scoped         |
| OpenAPI     | Single service | None   | Describes ONE service, not a topology         |
| Pkg registries | Strong | Deps only   | Half — no protocol/auth                       |

### Finding 2: Universal Minimum Viable Identity (8 fields)

```yaml
identifier:    string    # globally unique, URL-safe
name:          string    # human-readable display name
version:       string    # semver: MAJOR.MINOR.PATCH
description:   string    # 1-2 sentences, <250 chars
author:        string    # name, email, url
license:       string    # SPDX identifier or "proprietary"
source:        string    # URL to source/origin
keywords:      string[]  # discovery tags
```

**Caveat (Gemini validation):** These 8 fields are misleadingly universal. Version in semver ≠ version in ODPS. License for OSS ≠ license for SaaS. The UPS handles identity better through classification axes — don't flatten to lowest-common-denominator.

### Finding 3: Best-of-breed connectivity composite

| Take From   | What                                              | Why                                    |
|-------------|---------------------------------------------------|----------------------------------------|
| Backstage   | Bidirectional typed relations                     | Proven at Spotify scale, graph-first   |
| SPDX 3.0    | Edges as first-class elements with own IDs        | Connections deserve own identity        |
| CycloneDX   | Data flow direction, trust boundaries, auth       | Closest to runtime services            |
| W3C WoT     | Multi-protocol forms (HTTP + MCP + CLI)           | Tools ARE reachable via multiple protos |
| MCP Registry| Server card schema + capability declarations      | Native to the AI agent ecosystem       |

---

## 2. Two-Document Architecture

```
┌─────────────────────────────┐    ┌────────────────────────────────┐
│  UPS v4.1 (Product Identity)│    │  CONNECTIONS_REGISTRY v1       │
│                             │    │                                │
│  Layer A: Company           │    │  NODES: components, agents,    │
│  Layer B: Shared Platform   │◄──►│        external providers      │
│  Layer C: Stage Gates       │    │                                │
│  Layer D: Product Instance  │    │  EDGES: typed, bidirectional   │
│  Layer E: Conditional       │    │        connections with proto, │
│                             │    │        auth, risk, stage gate  │
│  WHAT things ARE            │    │  HOW things CONNECT            │
└─────────────────────────────┘    └────────────────────────────────┘
         │                                     │
         └────────── Shared vocabulary ────────┘
```

What the pair covers that NO existing standard does:
1. **Maturity-gated connections** — "this connection must exist before promotion to P4"
2. **Credential topology** — "this connection authenticates via doppler:ai-tools/prd/CEREBRAS_API_KEY"
3. **Agent-native connectivity** — MCP servers as first-class nodes

---

## 3. Final Taxonomy

```
ECOSYSTEM       — everything. The word "system" stays free/unbound.
  └── APPLICATION     — a coherent product (Rainmaker, Dashboard, AUDIO PRO, SecretScript)
       └── COMPONENT  — atomic, reusable unit of software. The microservice.
                        Passive. Deterministic. No judgment.
                        A component DELIVERS a capability. It's the machine, not the work.

AGENT           — software that crosses the governance threshold.
                  Active. Nondeterministic. Exercises judgment.
                  Operates on components AND other agents.
                  Separate category, not a subtype of component.

CONNECTION      — the data flow between any two nodes.
                  First-class entity with its own identity.
                  The nervous system made visible.
```

**Governance threshold** (component vs agent boundary):
- `human_operated` or `ai_assisted` → Component
- `ai_supervised` or `ai_autonomous` → Agent

**Key distinction:** A component is NOT a feature. A component is the thing that makes a feature possible. The feature is a property of the component (purpose + inputs/outputs). You sell the feature. You build, deploy, version, and govern the component.

**Entity identity kind enum:**
```yaml
kind: component | agent | connection
```

**Registries:**
- `COMPONENTS_REGISTRY.yaml` — what the ecosystem IS (software nodes)
- `AGENTS_REGISTRY.yaml` — who ACTS (software with governance requirements)
- `CONNECTIONS_REGISTRY.yaml` — how they REACH each other (interface edges)

---

## 4. The 4 Blocking Decisions (Final Answers)

| # | Question    | Old Answer     | Final Answer                  | Changed? |
|---|-------------|----------------|-------------------------------|----------|
| 1 | Granularity | Per-credential | **Per-component**             | Yes — components are atomic |
| 2 | Taxonomy    | All 7          | **All 7 relationship types**  | No |
| 3 | Orphans     | Quarantine     | **Quarantine in Doppler**     | No |
| 4 | Sequencing  | Tools first    | **All 3 registries simultaneously** | Yes — files are 90% done |

### Q1 rationale:
`cerebras_rapid_intel` and `cerebras_tagger` are separate components with separate blast radii, health profiles, and purposes — even though they share a credential. Credential failure cascade is modeled through Doppler's own connection entry (`blast_radius: [CON-001, CON-002, ...]`), not flattened into shared entries. Tradeoff: ~20-30 entries for Ring 1 instead of ~10, but each is independently queryable.

### Q4 rationale:
The 9 files in `ecosystem-REGISTRIES/` are 90% done. Work is:
1. Rename `feature` → `component`, `F-xxx` → `CMP-xxx` (mechanical)
2. Add `contains: []` and `part_of:` fields (small addition)
3. Add `authenticates_via` to relationship enum (7th type)
4. Move files to permanent repo location

---

## 5. Connection Schema (8-Tier Design)

### TIER 1 — The Atom

```yaml
connection:
  id:           CON-001                              # Globally unique
  source:       internal:CMP-055                     # Ref to COMPONENTS_REGISTRY
  target:       external:cerebras                    # Ref to external provider
  relationship: depends_on                           # From Tier 2 taxonomy
  description:  "Cerebras LLM inference for rapid intelligence sweeps"
```

**Ref format:**
- `internal:{component_id}` — references COMPONENTS_REGISTRY
- `external:{provider_name}` — references external providers (own node definitions)
- `infra:{resource_id}` — infrastructure resources (VPS, Syncthing, Tailscale)

**Design answer:** Two connections sharing same source+target are distinguished by `description` + `transport.protocol` combination.

### TIER 2 — Relationship Nature (closed taxonomy of 7)

| Type | Meaning | Structural implication |
|------|---------|----------------------|
| `depends_on` | Source cannot function without target | Failure propagates. Critical path. |
| `integrates_with` | Source enhanced by target but works without it | Graceful degradation possible. |
| `orchestrates` | Source triggers target in a workflow | Temporal coupling. Ordering matters. |
| `replicates` | Source and target maintain synchronized state | Bidirectional. Consistency requirements. |
| `delegates_to` | Source grants target authority to act on its behalf | Trust boundary. Governance applies. |
| `publishes_to` | Source emits events/data that target consumes | Decoupled. Async. |
| `authenticates_via` | Source authenticates through target | Credential dependency. |

**Direction model:** Unidirectional with computed reverse (Backstage pattern). Author one direction; reverse is derivable by graph traversal.

### TIER 3 — Protocol and Transport

```yaml
transport:
  protocol:    enum    # http_rest | http_graphql | grpc | mcp_stdio | mcp_sse |
                       # mcp_streamable_http | ssh | websocket | sync_bidirectional |
                       # webhook | event_bus | file_system | cli_subprocess
  endpoint:    string  # URL, host:port, path, or null for implicit
  direction:   enum    # push | pull | bidirectional_symmetric |
                       # request_response | fire_and_forget
```

### TIERS 4-8 — Enrichment layers

- **Tier 4:** Authentication (credential_ref to Doppler path, rotation policy)
- **Tier 5:** Health & temporal (status, last_verified, health_check command, failure_history)
- **Tier 6:** Risk overlay (data_sensitivity, consequence_if_broken, blast_radius)
- **Tier 7:** Stage gates (stage_required, aligns connection to product maturity P0-P7)
- **Tier 8:** Operational (cost_model, monthly_budget, rate_limits, SLA)

---

## 6. Design Principles

1. **Connections are first-class entities.** Own IDs, own lifecycle, own risk profile. Not properties of nodes.
2. **Closed taxonomies over open strings.** Every enum is finite and justified. "other" is never valid.
3. **Reference, don't duplicate.** Registry references Doppler secrets by path, components by ID, stages by code. Never copies content.
4. **Honest over optimistic.** `status: unknown` > `status: active` with no verification.
5. **Computable graph.** Parseable into directed graph. "What breaks if Y goes down?" answered by graph traversal.
6. **Minimal core, extensible edges.** Tiers 1–4 = schema. Tiers 5–8 = operational enrichment with defaults/nullable.
7. **Connection-specific, not universal identity.** `cost_model: per_token` on a connection ≠ pricing tiers on a product. Don't conflate.

---

## 7. Ecosystem Ground Truth (Validated Audit)

### Three concentric rings:
- **Ring 1** (8 services, ~90% traffic): Cerebras + Gemini + Perplexity + Doppler + Collider + ACI + OpenClaw + SQLite
- **Ring 2** (5 services, weekly): REH + Neo4j + HuggingFace + Decision Deck + Syncthing
- **Ring 3** (everything else): 9 MCP-only servers + 40 orphaned Doppler secrets + 8 unregistered Python tools

### Core dependency chain:
```
Doppler → [Cerebras, Gemini, Perplexity] → ACI → Collider/Refinery → Dashboard
            ↕ (MCP wrappers)                      ↕ (Neo4j, SQLite)
```

### Systemic gaps:
1. **Most-used tools are unregistered.** `cerebras_rapid_intel.py` has shell alias, MCP wrapper, 12 files depending on it — but no registry ID.
2. **MCP servers added ahead of code.** OpenAI, Replicate, ElevenLabs, Telegram configured but zero Python code uses them. Mark `status: dormant`.
3. **~40% Doppler secrets orphaned.** MARBLE, MESHY, META, TWILIO, BINANCE etc. — no code references. Scanner's first harvest.

### Implementation priority:
1. Register 8 unregistered tools in COMPONENTS_REGISTRY (give CMP-IDs)
2. Populate CONNECTIONS_REGISTRY with Ring 1 (~20 connections)
3. Build scanner to catch drift and orphaned secrets
4. Extend to Ring 2-3 as they gain real usage

---

## 8. Cognitive Compilation Principle

> **Core insight:** Schemas are crystallized cognition — the residue of intelligence compressed into deterministic structure. When a future AI agent loads the schema, it doesn't re-derive the reasoning. It inherits it.

```
Raw AI cognition:               ~1x   (reasoning from scratch every time)
AI + good documentation:        ~3x   (less guessing, fewer wrong turns)
AI + compiled cognitive schema: ~10x+ (inherits architectural reasoning,
                                       navigates deterministically,
                                       only uses inference for the novel parts)
```

**Compression principle:** Maximum semantic density per token. Every field is measured by: *does it reduce the cognitive work an AI agent must do at runtime?*

**What LLMs CAN infer** (don't spell out): data types, validation rules, naming conventions, hierarchical nesting.

**What LLMs CANNOT infer** (must be explicitly compiled): why things connect, what breaks on failure, when connections are required relative to maturity, who can modify, how to explain to humans.

### Tier 0 — Agent Navigation Protocol

Every entity carries an `agent_interface` block enabling AI agents to:
1. RESOLVE natural language to schema entities without inference
2. TRAVERSE the graph with explicit reasoning about why each edge matters
3. ACT on entities within declared permission boundaries
4. EXPLAIN entities to humans using pre-authored description templates
5. TRIAGE what to load into context when full registry is too large

### Token budget:
- Schemas only: ~16,500 tokens
- Schemas + examples: ~26,300 tokens
- At 1M context window: **2.6%** — recommendation is always-load everything

---

## 9. Progressive Requirements (Hybrid Model)

Three categories:
- **ENFORCED** — must be present at this stage (fields the code already contains)
- **FREE** — welcome anytime, never required (early knowledge is rewarded)
- **LOCKED** — cannot appear below a certain stage (prevents premature promises)

**Rationale:** P0 fields are things the source code already contains (endpoint URL, `os.getenv` call, input params, auth pattern). P1 adds what you must know before other humans depend on it (data sensitivity, AI autonomy level). P2 adds what you must know before the system depends on it (health checks, blast radius). Progression follows actual risk curve.

**Agent governance exception:** `governance.delegation.cannot` (prohibitions) and `governance.escalation` (when to stop and ask) are ENFORCED from P1 — earlier than most fields. Cost of unauthorized agent action is always high.

---

## 10. Gemini Validation — Critical Catches

1. **Scanner from Approach C is NOT optional.** A registry without validation is documentation. Documentation rots.
2. **Missing connection types taxonomy.** Protocol (HOW bits travel) ≠ relationship type (WHY things connect). Both needed.
3. **Missing temporal health.** `status: active` without `last_verified` is a lie.
4. **B.1/B.2 boundary problem.** Shared nouns flow through multiple systems with undefined per-system schemas.
5. **MVI misleadingly universal.** Don't flatten UPS identity to lowest-common-denominator 8-field template.
6. **Connection direction beyond driving/driven.** Needs push | pull | bidirectional | request_response | fire_and_forget.

---

## 11. Agent Registry Rationale

Agents are a **distinct operational category** requiring dedicated governance, identity, and coordination primitives — not because they are non-software, but because the consequences of their operation demand a higher standard of accountability than passive components.

**Key architectural insight:** The boundary between component and agent is a governance threshold, not an ontological wall. Systems that start as components can gain agency as they mature.

**Agent-specific concerns with no component equivalent:**
- Composability is *social* not mechanical (context transfer, trust delegation, judgment)
- Regulatory trajectory demands separate treatment (EU AI Act, Brazil PL 2338/2023)
- MCP authentication primitives treat agents as callers with identity, not just token bearers

**Grounding:** Agents are not autonomous. They simulate autonomy. Governance is industrial safety engineering (preventing high-speed mistakes), not employment law (managing autonomous actors). Design for momentum, not intentions.

---

## 12. Success Criteria

When the schema is complete, these questions become answerable from registry files:

- "What connects to Cerebras?" → All connections with `target: external:cerebras`
- "What breaks if Cerebras goes down?" → Transitive closure of `blast_radius`
- "Is the Telegram connection healthy?" → `health.status` + `health.last_verified`
- "What credentials need rotation?" → `auth.last_rotated` vs `auth.rotation_policy`
- "What connections must exist before promoting to P4?" → `stage_required <= P4`
- "What undocumented connections exist?" → Scanner diff between registry and config
- "What is monthly API spend exposure?" → Sum `operational.monthly_budget` across active connections

**Design constraint:** Do not add any field that doesn't help answer at least one of these questions.
