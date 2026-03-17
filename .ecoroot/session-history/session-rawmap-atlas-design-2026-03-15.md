# RAW DOCUMENT MAP — CONTEXT-TO-CLEAN-CAUTIOUSLY.md

> Navigation index for AI agents. Use with the cleaned summary (`CONTEXT-CLEANED.md`).
> When the summary is insufficient, jump directly to the line ranges below for full detail.
>
> **File:** `CONTEXT-TO-CLEAN-CAUTIOUSLY.md` (4,164 lines)
> **Density legend:** ★★★ = essential raw detail | ★★ = useful context | ★ = low signal, mostly UI chrome

---

## SESSION 1: Research + Two-Document Architecture (Lines 1–390)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 1–14 | Claude Code header, version info | ★ | Skip — UI chrome only |
| 15–109 | **Research synthesis: 15 standards surveyed** — Universal MVI table, identity vs connectivity gap across npm/PyPI/OCI/Helm/MCP/Stripe/Backstage/ODPS/WoT | ★★★ | Full comparison table with per-standard field mapping. The cleaned doc summarizes; this has the raw data. |
| 110–160 | **Connectivity gap analysis** — What Backstage, W3C WoT, MCP Registry each contribute. What your ecosystem needs that none provide. | ★★★ | The hybrid schema rationale with specific field attributions per standard. |
| 161–199 | **Two-document architecture diagram** — UPS v4.1 (nodes) ↔ CONNECTIONS_REGISTRY (edges). ASCII art. | ★★ | The original diagram. Cleaned doc has it. |
| 200–220 | Source URLs for all research | ★★ | Backstage docs, MCP Registry, ODPS, etc. — reference links. |
| 221–388 | **Full research synthesis (Opus agents merged)** — Finding 1 (nobody solves both), Finding 2 (MVI 8-field core), Finding 3 (best-of-breed composite table), Answering "Do we have both documents?" | ★★★ | Longer version of research findings with CycloneDX, SPDX, WoT details. Lines 289–310 have the "Take From" table with three columns. |
| 389–390 | Session end timestamp | ★ | Skip |

---

## SESSION 2: Gemini Validation Critique (Lines 391–862)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 391–445 | Gemini session header + context reading | ★ | Skip — Gemini reading the transcript |
| 446–509 | **"What's genuinely strong"** — Gemini validates: core insight correct, UPS v4.1 complete, two-doc architecture right, Doppler-as-backend sound, feature rename correct. | ★★ | Positive validation with specific evidence. |
| 510–621 | **"What's shaky" (6 critiques)** — (1) Agent thrashing before productivity, (2) Audit incomplete (inventory not topology), (3) Approach C scanner dropped without justification, (4) B.1/B.2 boundary coherence problem, (5) Missing temporal health dimensions, (6) MVI misleadingly universal | ★★★ | **Critical.** These 6 concerns drove spec revisions. Lines 598–620 have the temporal health gap detail. Lines 570–590 have the B.1/B.2 noun-schema mismatch. |
| 622–678 | **"What's missing" (2 gaps)** — (1) No connection types taxonomy (protocol ≠ relationship type), (2) No direction beyond driving/driven — full direction taxonomy (push/pull/bidirectional_symmetric/bidirectional_asymmetric/event_driven) | ★★★ | The relationship type table (depends_on → delegation) originates here. Lines 660–676 define all 6 types. |
| 679–762 | **Direction taxonomy + cost model gap + Semantic Algebra link** — Gemini's critique of direction conflation, missing cost model on connections, missing formal link between CONNECTIONS_REGISTRY and Semantic Algebra | ★★★ | Lines 692–704: five direction types with examples. Lines 708–722: cost model argument (rate_limit, cost_model, monthly_budget). Lines 726–744: Semantic Algebra adaptation tokens fed by connection health. |
| 763–862 | **Gemini verdict + CONNECTIONS_REGISTRY prompt structure** — "UPS is production-grade", "CONNECTIONS_REGISTRY pre-specification". Then: 8-tier priority order, 5 deliverables, design principles. | ★★★ | Lines 828–862: Tier structure rationale ("Tiers 1-4 are schema, 5-8 are enrichment"). Line 856: "No AI inference, no LLM-assisted classification" — boring foundation principle. |

---

## SESSION 2 cont.: The Full Prompt Spec (Lines 863–1527)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 863–1005 | **TIER 1 — The Atom** — Connection as first-class entity (from SPDX 3.0). YAML schema: id, source, target, description. Ref format: `internal:` / `external:` / `infra:`. Design question: what distinguishes two connections sharing same source+target? | ★★★ | The original YAML for the connection atom. Lines 972–984 have the raw schema. Lines 988–1002 have the ref format spec and design question. |
| 1006–1058 | **TIER 2 — Relationship Nature** — 6-type taxonomy table (depends_on, integrates_with, orchestrates, replicates, delegates_to, publishes_to). Design question: bidirectional vs unidirectional. | ★★★ | Lines 1016–1040: full type table with structural implications. |
| 1059–1107 | **TIER 3 — Protocol and Transport** — Full YAML schema: protocol enum (13 values), endpoint, direction enum (5 values). Design question: one transport or array (WoT forms)? | ★★★ | Lines 1076–1090: raw YAML with complete protocol and direction enums. |
| 1108–1148 | **TIER 4 — Authentication Binding** — YAML: method enum, credential_ref (Doppler path), rotation_policy, last_rotated. Design question: compound auth (OAuth = 3 secrets). | ★★★ | Lines 1120–1137: raw auth YAML. Lines 1142–1148: compound auth problem. |
| 1149–1186 | **TIER 5 — Health and Liveness** — YAML: status enum (6 values), last_verified, verification_method, failure_count_90d, mttr_avg. Design question: who updates health? | ★★★ | Lines 1162–1177: raw health YAML with all fields. |
| 1190–1225 | **TIER 6 — Risk and Governance** — YAML: data_sensitivity, data_flows, consequence_if_broken, blast_radius. Design question: manual vs computed blast_radius. | ★★★ | Lines 1200–1216: raw risk YAML. |
| 1228–1265 | **TIER 7 — Lifecycle and Stage Gates** — YAML: stage_required (P0-P7), created, deprecated, sunset, owner, successor. Design question: enforcement mechanism. | ★★★ | Lines 1240–1256: raw lifecycle YAML. |
| 1268–1327 | **TIER 8 — Operational Metadata** — YAML: rate_limit, cost_model, monthly_budget, sla, documentation_url. | ★★ | Lines 1278–1290: raw operational YAML. |
| 1328–1425 | **Deliverables spec** — (1) Schema definition, (2) 10 real example connections, (3) UPS cross-reference map (which B.1 nouns → which connections, which B.2 systems, which C stage gates, which D.4 governance rules), (4) Validator rules as pseudocode, (5) Scanner spec. | ★★★ | Lines 1352–1425: detailed requirements for cross-reference, validator rules, and scanner. The scanner spec (lines 1398–1425) describes parsing mcp.json, Doppler, SSH config, Python os.getenv. |
| 1428–1524 | **Design Principles (7) + Success Criteria (7 questions)** — Principles: first-class entities, closed taxonomies, reference don't duplicate, honest over optimistic, computable graph, minimal core, don't add fields that don't answer questions. | ★★★ | **Essential reference.** Lines 1440–1478: all 7 principles. Lines 1490–1524: all 7 success questions. |
| 1527 | Claude acknowledges Gemini validation, starts executing the prompt | ★ | Transition point. |

---

## SESSION 3: Claude Executes the Spec (Lines 1527–2005)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 1527–1565 | **Tier 1 answer** — Connection atom with real example (CON-001, cerebras_rapid_intel → Cerebras). Ref format with three namespaces: `internal:`, `external:`, `infra:`. | ★★★ | Lines 1559–1574: the finalized atom YAML with ref format. |
| 1576–1642 | **Tier 2 answer** — Full 7-type taxonomy table with reverse names and ecosystem examples. Decision: unidirectional with computed reverse. `authenticates_via` added as 7th type. | ★★★ | Lines 1591–1618: the **definitive** relationship types table with computed reverse column. Lines 1620–1625: rationale for adding `authenticates_via`. |
| 1627–1656 | **Tier 3 answer** — One transport per connection (not array). Full protocol enum (12 values) and direction enum (5 values). | ★★★ | Lines 1644–1656: finalized transport YAML + direction taxonomy with examples. |
| 1658–1682 | **Tier 4 answer** — credential_refs is an ARRAY. Compound auth solved. No rotation_policy in registry (lives in Doppler). | ★★★ | Lines 1667–1682: finalized auth YAML with examples of single, compound, and file-based auth. |
| 1684–1702 | **Tier 5 answer** — Scanner is default health updater. Simplified from Gemini's proposal (failure_count computed, not stored). | ★★ | Lines 1690–1702: finalized health YAML. |
| 1704–1745 | **Tier 6-8 answers** — blast_radius: both manual + computed. Stage gate enforcement: validator rule (human decides). Operational: rate_limit, cost_model, monthly_budget, documentation_url. | ★★ | Lines 1712–1745: finalized Tiers 6-8 YAML. |
| 1748–1802 | **Spec written to file** — 826 lines to `2026-03-15-connections-registry-design.md`. Insight block on what Gemini caught + what research grounded. UPS v4.1 additions: B.1 noun "connection", B.2 system "Connectivity registry". | ★★ | Lines 1774–1797: summary of what Gemini caught and research grounded. |
| 1805–2005 | **Spec validation pass** — Code reviewer agent checks all 21 Gemini concerns. Scorecard: 18/21 addressed. Fixes: Design Principle 7 (MVI rebuttal), blast_radius traversal note, Semantic Algebra forward ref (§9.1), JSON Schema deliverable (§9.2). | ★★ | Lines 1957–1999: full scorecard table + insight on blast_radius traversal and Semantic Algebra link. |

---

## SESSION 4: Assumption Validation + Ecosystem Audit (Lines 2007–2502)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 2007–2067 | **Critical finding: example data is fiction.** Every `internal:T0xx` reference in the spec is wrong. Table mapping spec claims vs actual TOOLS_REGISTRY IDs. 8 unregistered Python tools. | ★★★ | Lines 2030–2060: the **wrong ID mapping table** and the **correct ID table**. This is the ground truth correction. |
| 2068–2200 | **Spec patches** — Diff hunks fixing CON-001 through CON-010 with correct T-IDs, `unregistered:` prefix, corrected credential paths, corrected blast_radius arrays. Added `unregistered:` ref format. | ★★ | Raw diff output. Visit only if you need the exact corrections made. |
| 2200–2447 | **Deep ecosystem audit** — File-by-file codebase scan. Which files reference which APIs. The 3-ring model (Ring 1: 8 services/90% traffic, Ring 2: 5 weekly, Ring 3: everything else). Core dependency chain. MCP-only gap. ~40 orphaned Doppler secrets listed. | ★★★ | Lines 2413–2437: **the key insight block** — 80/20 rule, MCP-only gap, orphaned secrets, real dependency chain diagram. Lines 2459–2496: **three rings definition** + implementation priority (register tools → populate Ring 1 → build scanner → extend). |
| 2500–2600 | **The 4 blocking questions as interactive prompts** — Q1 (granularity), Q2 (taxonomy), Q3 (orphans), Q4 (sequencing) with options. | ★★ | Lines 2508–2600: the decision options with tradeoff descriptions. |

---

## SESSION 5: Cognitive Compilation + Agent Navigation (Lines 2600–3070)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 2600–2700 | More interactive decision prompts (sequencing, naming) | ★ | Skip — decisions captured in cleaned doc. |
| 2700–2967 | **Tier 0 — Agent Navigation Protocol.** `agent_interface` block spec. `context_priority` field rationale. The reframing: success criteria = "can the agent find it, understand it, and communicate it, without guessing?" not just "is the data there?" Also: convergence insight — one agent interface protocol across UPS + CONNECTIONS_REGISTRY + Semantic Algebra. | ★★★ | Lines 2900–2963: **Tier 0 full spec** — RESOLVE, TRAVERSE, ACT, EXPLAIN, TRIAGE. Lines 2944–2960: the subtle but critical reframing of success criteria. |
| 2968–3064 | **Cognitive Compilation Principle** — Leo's insight crystallized. Schemas as compiled cognition. The multiplier table (1x → 3x → 10x+). Maximum semantic density per token. What LLMs can/cannot infer. The foundational prompt reframe: "You are compiling architectural reasoning into deterministic structure." | ★★★ | **Philosophical core of the entire architecture.** Lines 2981–3012: the full cognitive compilation definition. Lines 3030–3047: the can-infer / cannot-infer split. Lines 3053–3061: the prompt rewrite instruction. |

---

## SESSION 6: Schema Construction + Examples (Lines 3066–3152)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 3066–3088 | Leo requests building all schemas directly. Identifies missing piece: AGENTS_REGISTRY. | ★★ | The trigger for building three registries + shared identity. |
| 3089–3152 | **Schema summary** — 8 files, 77KB. ENTITY_IDENTITY, FEATURES_REGISTRY, CONNECTIONS_REGISTRY, AGENTS_REGISTRY, ECOSYSTEM_GRAPH, + 3 example files. Description of each file's purpose and the agent block design. | ★★★ | Lines 3097–3134: concise description of all 8 files and the key design move (agent block = cognitive compilation). |

---

## SESSION 7: Progressive Requirements Model (Lines 3152–3500)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 3152–3200 | **Progressive disclosure model** — Schema grows with maturity. P0 = atom (7 fields), P5 = everything. Fields tagged with `required_at` stage. | ★★★ | Lines 3182–3200: the progressive_requirements YAML for P0 and start of P1. |
| 3200–3332 | **Full progressive requirements P1 through P7** — Every field categorized by stage, split by entity kind (feature/connection/agent). Agent governance enforced from P1. | ★★★ | **Critical reference for implementation.** Lines 3200–3250: P1-P2 fields. Lines 3252–3290: P3-P5 fields. |
| 3340–3427 | **Schema shape decision** — Option 1 (full skeleton with nulls) vs 2a (strict bottom-up) vs 2b (sparse, jump anywhere). Decision: 2b. Rationale: no nulls = max cognitive density for LLMs, stage is a ratchet not a ceiling. ENFORCED / FREE / LOCKED categories. | ★★★ | Lines 3355–3427: **essential design reasoning.** The argument against nulls (lines 3359–3368) is foundational. The ENFORCED/FREE/LOCKED model (lines 3465–3472) originates here. |
| 3429–3500 | **Hybrid enforcement model** — Enforce what code already contains, free everything else. LOCKED prevents premature promises. Token budget analysis: ~16.5K schemas, ~26.3K with examples, 2.6% of 1M context. Recommendation: always load everything. | ★★★ | Lines 3463–3496: hybrid model + always-load recommendation with math. |

---

## SESSION 8: Taxonomy Naming Debate (Lines 3500–3900)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 3570–3685 | **Naming candidates** — Capability, Skill, Operation, Service, Feature, Function. Pros/cons of each. Recommendation: Capability → then overridden by "Component." | ★★ | Lines 3603–3683: full analysis of each candidate with four-perspective test (agent/product/system/economic). |
| 3687–3752 | **"Component" wins** — Leo says "system of systems." The taxonomy dissolves. Component in the systems engineering sense. Hierarchy: Ecosystem → System → Component → Action → Artifact. Contains/part_of recursion. Rename chain: TOOLS → FEATURES → CAPABILITIES → COMPONENTS. | ★★★ | Lines 3697–3752: the definitive taxonomy with recursion model and rename chain. Lines 3756–3761: formal graph definition `G = (Components ∪ Agents, Connections)`. |
| 3762–3900 | **Agent separation debate** — Should agents be subtypes of components or separate? Leo argues for separate category (AI as more than software). Claude pushes back with precision: agents are not autonomous, they simulate autonomy. Governance = industrial safety (momentum), not employment law (intentions). The governance threshold: `ai_supervised` / `ai_autonomous` → Agent. | ★★★ | **The best philosophical passage.** Lines 3838–3851: agents are powerful tools, not autonomous beings. Lines 3866–3895: the governance threshold definition + spectrum not wall. |

---

## SESSION 9: Final Taxonomy Lock (Lines 3900–4055)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 3900–3948 | Leo clarifies: "CPF" = registration number, not personhood. Refocuses on naming/schemas. Final taxonomy locked: Ecosystem → Application → Component + Agent + Connection. | ★★★ | Lines 3914–3946: **the final taxonomy** with registry names and kind enum. |
| 3950–4015 | **Leo's voice transcript** — Raw reasoning on applications, components, microservices, data flow. Key insight: "if we can manage to have a data flow map from day one, we are eons ahead." | ★★ | Lines 3977–3980: the data flow insight. Lines 4002–4009: the component/feature distinction. |
| 4016–4055 | Claude's response (interrupted) — Updating schemas with final naming. Confirms agent operates on components AND other agents. | ★★ | Lines 4023–4030: multi-agent correction. |

---

## SESSION 10: Files Read + 4 Decisions Reconsidered (Lines 4055–4164)

| Lines | Content | Density | Why visit |
|-------|---------|---------|-----------|
| 4055–4075 | Reading 9 ecosystem-REGISTRIES files. Current state: pre-rename (kind: feature, F-xxx IDs). | ★★ | |
| 4077–4154 | **The 4 Blocking Decisions, reconsidered against new architecture** — Q1: Per-component (not per-credential). Q2: Keep all 7. Q3: Quarantine. Q4: All 3 registries simultaneously. Summary table. Work plan (7 mechanical steps). | ★★★ | Lines 4082–4149: **the definitive decision table** with rationale for each change. This is a duplicate of the same content from earlier, but with updated `component` framing. |
| 4155–4164 | Session end / prompt | ★ | Skip |

---

## QUICK REFERENCE: Where to find specific things

| Need | Go to lines |
|------|------------|
| Raw standard-by-standard comparison table | 84–109 |
| Gemini's 6 "what's shaky" critiques | 510–621 |
| Full 8-tier YAML schemas (Gemini's prompt version) | 968–1290 |
| Full 8-tier YAML schemas (Claude's executed version) | 1545–1745 |
| 7 relationship types table with reverse names | 1591–1618 |
| Validator rules (pseudocode requirements) | 1370–1395 |
| Scanner spec (what to parse and how) | 1398–1425 |
| Wrong ID corrections (spec vs reality) | 2030–2060 |
| 3-ring ecosystem model + dependency chain | 2459–2496 |
| Tier 0 Agent Navigation Protocol | 2900–2963 |
| Cognitive Compilation Principle (full) | 2968–3064 |
| Progressive requirements P0–P7 (all fields) | 3182–3332 |
| Sparse vs skeleton decision (no nulls rationale) | 3355–3427 |
| ENFORCED / FREE / LOCKED model | 3463–3496 |
| Naming debate (capability vs component vs...) | 3570–3752 |
| Agent vs component philosophical debate | 3762–3900 |
| Final taxonomy + registry names | 3914–3946 |
| 4 decisions final summary table | 4137–4149 |
