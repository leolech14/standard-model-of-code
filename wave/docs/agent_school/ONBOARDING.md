# ONBOARDING - Canonical Entry Point

> **Status:** ACTIVE
> **Purpose:** Progressive onboarding for AI agents. Start small, then drill deeper as needed.

## 0. Load the Kernel

Read `wave/docs/agent_school/AGENT_KERNEL.md` first. It is the minimal boot contract.

## 1. Boot and Check State

```bash
./pe status
./.agent/concierge_cli
./pe boot
```

If you need JSON output for tooling:

```bash
bash wave/tools/maintenance/boot.sh --json
```

## 2. Pick Work Safely

- Check certified moves: `./pe deck deal`
- Route intent: `./pe deck route "your intent"`
- If no card matches, define a small, atomic task and proceed via the micro-loop.

## 3. Where to Find Truth (SSoT)

These are the primary registries and truth anchors:

- `SUBSYSTEMS.yaml` — subsystem registry (active + maturity)
- `DOMAINS.yaml` — code↔context symmetry registry
- `.agent/registry/REGISTRY_OF_REGISTRIES.yaml` — discoverable index of registries
- `REPO_STRUCTURE.json` — declared repo structure and purpose
- `wave/docs/GLOSSARY.md` — canonical terminology

## 4. Core Concepts (Minimum Reading)

1. `wave/docs/PROJECTOME.md` — Projectome = Codome ⊔ Contextome
2. `wave/docs/CODOME.md` — Executable universe
3. `wave/docs/CONTEXTOME.md` — Non-executable universe
4. `wave/docs/CONCORDANCES.md` — Purpose alignment across code + docs
5. `particle/docs/MODEL.md` — Standard Model of Code

## 5. How to Query the Repo

Preferred tool entrypoints:

- `./pe ask "question"` — fast AI query
- `python3 wave/tools/ai/analyze.py "question" --set brain` — direct ACI
- `python3 wave/tools/ai/analyze.py --verify pipeline` — Socratic audit

## 6. Tutorials and Workflows

- `wave/docs/agent_school/TUTORIAL.md` — guided first task
- `wave/docs/agent_school/WORKFLOWS.md` — git and commit workflow
- `wave/docs/agent_school/CLI_GRAMMAR.md` — `./pe` command grammar
- `wave/docs/agent_school/DOD.md` — Definition of Done

## 7. If You Are Stuck

- Use `./pe status` to see current state.
- Use `./pe deck deal` to avoid improvisation when a certified card exists.
- Use `wave/docs/GLOSSARY.md` before inventing terms.

---

This onboarding is intentionally minimal. Use the Context Pack for a compact, always-safe memory anchor:

- `wave/docs/agent_school/CONTEXT_PACK.md`
- `wave/docs/agent_school/CONTEXT_PACK.json`
