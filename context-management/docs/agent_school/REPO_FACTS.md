# Repo Facts

> This file contains environment-specific facts about this repository.
> Update this file when project setup changes.

## Identity

| Fact | Value |
|------|-------|
| Repo Name | PROJECT_elements |
| Primary Language | Mixed (research/experimental) |
| Owner | Leonardo Lech |
| Contact | leonardo.lech@gmail.com |

---

## Commands

### Test
```bash
# TODO: Define test command for this repo
# Examples:
# npm test
# pytest
# go test ./...
# make test
```

### Lint
```bash
# TODO: Define lint command for this repo
# Examples:
# npm run lint
# ruff check .
# golangci-lint run
```

### Format
```bash
# TODO: Define format command for this repo
# Examples:
# npm run format
# black .
# gofmt -w .
```

### Build
```bash
# TODO: Define build command for this repo
# Examples:
# npm run build
# make build
# go build ./...
```

### Run
```bash
# TODO: Define run command for this repo
# Examples:
# npm start
# python main.py
# ./bin/app
```

---

## Directory Structure

```
PROJECT_elements/
├── AGENT_KERNEL.md          # Agent boot kernel (always loaded)
├── docs/
│   └── agent_school/        # Agent initiation docs
│       ├── INDEX.md
│       ├── WORKFLOWS.md
│       ├── REPO_FACTS.md    # (this file)
│       └── DOD.md
├── tools/
│   └── agent_boot.sh        # Automated boot script
├── standard-model-of-code/  # Subproject with own CLAUDE.md
└── archive/                 # Legacy/archived projects
```

---

## Environment

| Variable | Purpose | Where Defined |
|----------|---------|---------------|
| TBD | TBD | TBD |

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| TBD | TBD | TBD |

---

## Key Files

| File | Purpose |
|------|---------|
| `AGENT_KERNEL.md` | Tiny kernel loaded every session |
| `docs/agent_school/*` | Deep agent documentation |
| `standard-model-of-code/CLAUDE.md` | Subproject-specific rules |

---

## External Services

| Service | Purpose | Config Location |
|---------|---------|-----------------|
| GCP | Infrastructure | `~/gcp-infrastructure/CLAUDE.md` |
| Doppler | Secrets | `doppler -p gcloud-ops -c prd` |

---

## Notes

- This is a research/experimental repository
- Contains multiple subprojects with varying structures
- See subproject directories for specific commands
- GCP/infrastructure docs are NOT loaded globally (separate project)
