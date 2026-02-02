# AGENT_KERNEL - Minimal Boot Contract

> **Status:** ACTIVE
> **Purpose:** The minimum, high-signal rules and entrypoints every agent must load before acting.

## Start Here (2 minutes)

```bash
./pe status
./.agent/concierge_cli
./pe deck deal
./pe boot
```

If you need the machine-readable initiation report:

```bash
bash wave/tools/maintenance/boot.sh --json
```

## Non-Negotiables

1. Never leave the repo dirty. Commit changes or explain why you cannot.
2. Run tests before claiming done.
3. Every change needs a short rationale.
4. Search before creating new modules or docs.
5. Check the Decision Deck before complex actions: `./pe deck deal`.

## The Micro-Loop

```
SCAN → PLAN → EXECUTE → VALIDATE → COMMIT → REPEAT
```

## Canonical Commands

- Status: `./pe status`
- Boot: `./pe boot`
- Concierge view: `./.agent/concierge_cli`
- Decision Deck: `./pe deck deal`
- AI query: `./pe ask "question"`
- Verify (HSL): `./pe verify`
- Tests: `./pe test`
- Collider analysis: `./pe collider full <path> --output <dir>`

## Core Files (Read if unsure)

1. `wave/docs/PROJECTOME.md`
2. `wave/docs/CODOME.md`
3. `wave/docs/CONTEXTOME.md`
4. `wave/docs/CONCORDANCES.md`
5. `particle/docs/MODEL.md`
6. `particle/docs/COLLIDER.md`
7. `wave/docs/deep/AI_USER_GUIDE.md`

## Definition of Done

See `wave/docs/agent_school/DOD.md` for the full checklist and required completion format.
