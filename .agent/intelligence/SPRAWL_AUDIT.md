# Sprawl Audit - O Que Ficou Para Trás
**Date:** 2026-01-27
**Status:** 184 uncommitted changes + 125 untracked files
**Action Required:** Cleanup ou commit

---

## CRITICAL FINDINGS

### 1. DASHBOARD DELETADO (Não Commitado!)

**Files deleted:**
```
dashboard/Dockerfile
dashboard/README.md
dashboard/deploy.sh
dashboard/main.py
dashboard/requirements.txt
dashboard/routers/*.py (6 files)
dashboard/static/*.html, *.js
```

**Status:** DELETADO mas não commitado
**Problema:** Dashboard backend que construímos (20 endpoints, 1,000+ linhas) foi DELETADO
**Por quem:** Outro agente (não nós)
**Ação:**
- Opção A: Commit deletion (aceitar que foi removido)
- Opção B: Restore do commit anterior
- Opção C: Reconstruir (temos o código em commits anteriores)

**RECOMENDAÇÃO:** Opção A (commit deletion) - dashboard não era crítico

---

### 2. ROOT DOCS DELETADOS

**Files deleted:**
```
CLAUDE.md
GEMINI.md
INDEX.md
README.md
PROJECT_MAP.md
THEORY_MAP.md
AGENTS.md
QUICK_START.md
```

**Status:** Deletados mas não commitados
**Problema:** Documentação raiz removida
**Por quem:** Outro agente (cleanup?)
**Motivo possível:** Consolidação em HANDOFF.md

**Ação:** Commit deletion (HANDOFF.md substitui)

---

### 3. ARCHITECTURE/EVOLUTION REPORTS DELETADOS

**Directories:**
```
architecture_report/
evolution_report/
experiments/
```

**Status:** Removidos (cleanup de outputs antigos?)
**Problema:** Reports históricos perdidos
**Ação:** Commit deletion (eram outputs temporários)

---

### 4. RELATED/CHROME-MCP DELETADO

**Directory:** `related/chrome-mcp/`
**Status:** Projeto TypeScript inteiro removido
**Problema:** MCP server deletado
**Ação:** Commit deletion (não relacionado ao core)

---

### 5. UNTRACKED FILES (125 novos não commitados)

**Preciso listar para ver o que são...**

---

## CATEGORIZAÇÃO DO SPRAWL

### Categoria A: DELETIONS (Cleanup)
**Total:** ~50 files deleted
**Tipos:**
- Root docs (CLAUDE.md, README.md, etc.)
- Dashboard backend (20 endpoints)
- Old reports (architecture, evolution)
- Chrome MCP (external project)

**Status:** Outro agente limpou
**Ação recomendada:** Commit deletions (aceitar cleanup)

### Categoria B: UNTRACKED (New files não adicionados)
**Total:** 125 files
**Tipos:** DESCONHECIDO (precisa listar)
**Ação:** Listar e categorizar

### Categoria C: MODIFIED (Mudanças não commitadas)
**Total:** ~10 files
**Tipos:**
- .agent/macros/trigger_state.yaml
- .agent/state/circuit_breakers.yaml
**Ação:** Commit (state files atualizados)

---

## AÇÕES NECESSÁRIAS

### 1. Commit Deletions (Aceitar Cleanup)
```bash
git add -u  # Stage all deletions
git commit -m "chore: Remove legacy docs and unused subsystems

Removed:
- Root documentation (consolidated in HANDOFF.md)
- Dashboard backend (not critical for core)
- Old reports (architecture, evolution)
- Chrome MCP (external project)

Cleanup by parallel agent, accepting changes.
"
```

### 2. Audit Untracked Files
```bash
git status --short | grep "^??" > /tmp/untracked.txt
# Review list
# Categorize: Keep vs Delete vs Archive
```

### 3. Commit State Updates
```bash
git add .agent/macros/ .agent/state/
git commit -m "chore: Update automation state (trigger + circuit breakers)"
```

---

## SPRAWL SCORE

**Committed:** 181,551 lines (8 commits)
**Uncommitted deletions:** ~50 files
**Uncommitted new:** 125 files
**Modified:** 10 files

**Sprawl ratio:** 184 / 181,551 = **0.1%** (LOW!)

**Assessment:** Minimal sprawl - maioria é cleanup de outro agente

---

## RECOMMENDATION

**Action A: Accept Cleanup** (5 min)
```bash
git add -u  # Stage deletions
git commit -m "chore: Accept cleanup from parallel agent"
```

**Action B: List Untracked** (2 min)
```bash
git status --short | grep "^??" | tee .agent/intelligence/UNTRACKED_FILES.txt
```

**Action C: Review Tomorrow**
- Assess 125 untracked files
- Decide: Keep, delete, or archive
- Clean commit

---

**DO ACTION A NOW?** (Accept deletions, clean slate)

Ou quer ver lista completa de untracked primeiro?

