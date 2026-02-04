# OpenClaw Native Features - Use These First!

**Purpose:** Evitar reinventar a roda - OpenClaw já tem muita coisa built-in
**Date:** 2026-02-03

---

## ✅ O QUE OPENCLAW JÁ TEM (Use isso!)

### Automation & Scheduling
```bash
openclaw cron add       # Scheduled tasks
openclaw cron list      # View jobs
openclaw cron run       # Test job
```

**Não precisa:**
- ❌ LaunchAgents externos
- ❌ System cron
- ❌ Sentinel para cron jobs

**Usa:**
- ✅ `openclaw cron` para tudo
- Gerencia via dashboard
- Logs integrados

---

### Skills & Capabilities
```bash
openclaw skills         # List available
npx clawhub            # Install from hub
```

**Não precisa:**
- ❌ Escrever scripts shell separados
- ❌ Criar ferramentas do zero

**Usa:**
- ✅ Install skill do ClawHub
- ✅ Ou cria skill (se não existir)
- Reutiliza comunidade

---

### Model Management
```bash
openclaw models set             # Change default
openclaw models fallbacks add   # Add fallback
openclaw models list            # See available
```

**Não precisa:**
- ❌ Configurar routing manualmente
- ❌ Criar proxy complexo (na maioria dos casos)

**Usa:**
- ✅ OpenClaw native model switching
- ✅ Fallbacks automáticos
- Config simples

---

### Channels (WhatsApp, Telegram, etc.)
```bash
openclaw channels login     # Link channel
openclaw channels status    # Check health
openclaw channels logout    # Disconnect
```

**Não precisa:**
- ❌ Baileys manual setup
- ❌ Custom webhook handlers

**Usa:**
- ✅ OpenClaw channel management
- Built-in para 15+ platforms

---

### Sessions & Context
```bash
openclaw sessions      # List conversations
/new                  # Reset context (in chat)
```

**Não precisa:**
- ❌ Database manual para context
- ❌ Custom session management

**Usa:**
- ✅ OpenClaw session system
- Automatic persistence

---

### Agents (Multiple Personalities)
```bash
openclaw agents        # Manage agents
```

**Não precisa:**
- ❌ Multiple OpenClaw instances
- ❌ Complex orchestration

**Usa:**
- ✅ Multiple agents in one gateway
- Isolated contexts

---

## ⚠️ O QUE AINDA PRECISA EXTERNO

### Development Sync (Mac ↔ VPS)
```
OpenClaw não synca arquivos entre machines
Precisa: rsync, lsyncd, ou git
```

### System Package Management
```
OpenClaw não instala software
Precisa: apt, brew, pip
Use: install-dependencies.sh
```

### GCS Operations
```
OpenClaw não tem GCS skill (ainda?)
Precisa: gsutil, gcloud SDK
```

### Secrets Management
```
OpenClaw pode usar env vars
Mas Doppler é melhor para manage
Use: Doppler + OpenClaw env integration
```

---

## 🎯 Decision Tree

**Quando precisar de algo, pergunta:**

```
┌─ Preciso de X
│
├─ OpenClaw tem skill/feature para isso?
│  │
│  ├─ SIM → Use OpenClaw native
│  │        Exemplo: Cron, channels, models
│  │
│  └─ NÃO → Implementação externa OK
│           Exemplo: File sync, GCS, system packages
│
└─ Checa antes de criar!
   npx clawhub search <feature>
   openclaw skills | grep <feature>
```

---

## 📚 O Que Ficou (Docs Úteis)

```
wave/tools/ai/
├─ OPENCLAW_ARCHITECTURE.md      ← System overview (keep)
├─ EVOLUTION_AND_MAPPING.md      ← Lessons learned (keep)
├─ N8N_VS_OPENCLAW.md            ← When to use what (keep)
├─ LEVERAGE_EXISTING_SUBSCRIPTIONS.md ← API strategy (keep)
└─ OPENCLAW_NATIVE_FEATURES.md   ← This file (keep)

Removidos:
├─ MASTER_CHECKLIST.md           ← Outdated phases
├─ IMPLEMENTATION_MAP.md         ← Implemented already
├─ STORAGE_BRIDGE_TRIANGULATION.md ← Incomplete
├─ OPENCLAW_DASHBOARD_GUIDE.md   ← Basic info
├─ OPENCLAW_UI_CUSTOMIZATION_PLAN.md ← UI já custom
└─ SUBSCRIPTION_LEVERAGE_STRATEGIES.md ← Consolidated
```

---

## ✅ SUMMARY

**Use OpenClaw para:**
- ✅ Cron jobs
- ✅ Skills/tools
- ✅ Model management
- ✅ Channels
- ✅ Sessions
- ✅ Agents

**Use ferramentas externas SOMENTE para:**
- File sync (rsync/lsyncd)
- System packages (apt/brew)
- GCS operations (gsutil)
- Secrets (Doppler)

**Regra de ouro:** Check OpenClaw first, external only if necessary!

---

**Última atualização:** 2026-02-03
**Status:** Cleaned up, consolidated, OpenClaw-first approach
