# Research: Given the CUTTING audit results, propose the MINIMAL VIABLE META-REGISTRY. Requirements:

1. SINGLE ...

> **Date:** 2026-01-23 07:01:10
> **Source:** gemini
> **Model:** gemini-2.5-pro
> **Checksum:** `sha256:e45fce79e1e0579a9f8f7b53821b18e31fe4d023e5b856805bfee4d8f1277ee6`
> **Raw JSON:** `raw/20260123_070110_given_the_cutting_audit_results__propose_the_minim.json`

---

## Query

Given the CUTTING audit results, propose the MINIMAL VIABLE META-REGISTRY. Requirements:

1. SINGLE FILE only (.agent/META_REGISTRY.yaml)
2. MAXIMUM 50 lines for the whole file
3. NO health checks, NO checksums, NO complex metadata
4. Just: path, type, purpose (one line each)
5. Can be MANUALLY maintained (no automation needed initially)
6. Replaces the need for INDEX.md tables

Output the EXACT file content that should be created, following YAML best practices.

---

## Response

Based on my analysis of the project's structure and the requirements for a minimal, manually maintained meta-registry, here is the proposed content for `.agent/META_REGISTRY.yaml`.

This file acts as a single, machine-readable source of truth for locating the key registries and strategic documents within the repository, satisfying all your constraints.

```yaml
# A minimal, manually maintained index of key project registries and documents.
# Replaces markdown tables in INDEX.md for machine parsing and agent discovery.

registries:
  - path: .agent/KERNEL.md
    type: Bootstrap Protocol
    purpose: Agent boot protocol and core project principles.

  - path: .agent/manifest.yaml
    type: Project Manifest
    purpose: Machine-readable project metadata and capabilities.

  - path: .agent/SUBSYSTEM_INTEGRATION.md
    type: Integration Map
    purpose: Visual and descriptive map of subsystem connections.

  - path: .agent/OPEN_CONCERNS.md
    type: Design Document
    purpose: Design for the sprint system and other open problems.

  - path: .agent/roadmap/ROADMAP_REGISTRY.yaml
    type: Strategic Roadmap
    purpose: Registry of strategic goals and long-term vision.

  - path: .agent/sprints/
    type: Sprint Registry
    purpose: Sprint definitions, tracking work in major cycles.

  - path: .agent/registry/INDEX.md
    type: Task Dashboard
    purpose: Human-readable dashboard for all tracked tasks.

  - path: .agent/registry/inbox/
    type: Discovery Inbox
    purpose: Triage inbox for new, un-scoped opportunities.

  - path: .agent/runs/
    type: Run Records
    purpose: Log of all agent work sessions (RUN records).

  - path: .agent/intelligence/insights/
    type: Research Insights
    purpose: Actionable insights from the Research Refinery.

  - path: .agent/intelligence/truths/
    type: BARE Truths
    purpose: Canonical truths about the codebase (BARE output).
```

---

## Citations

_No citations provided_
