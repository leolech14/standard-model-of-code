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
cd standard-model-of-code && pytest tests/ -q
```

### Lint
```bash
cd standard-model-of-code && ruff check src/
```

### Format
```bash
cd standard-model-of-code && black src/ --check
```

### Build
```bash
cd standard-model-of-code && pip install -e .
```

### Run
```bash
./collider full <path> --output <dir>
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
| `GEMINI_API_KEY` | AI analysis (File Search RAG) | Doppler: `ai-tools/dev` |
| `ANTHROPIC_API_KEY` | Claude API (optional) | Doppler: `ai-tools/dev` |

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| tree-sitter | latest | AST parsing |
| networkx | latest | Graph analysis |
| pytest | latest | Testing |
| ruff | latest | Linting |
| black | latest | Formatting |

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
