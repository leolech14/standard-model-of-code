# OpenClaw Community Docker Setups - Best Options 2026

**Strategy:** Use community-tested, don't reinvent
**Source:** GitHub, DigitalOcean, Community repos
**Date:** 2026-02-04

---

## 🏆 TOP 3 COMMUNITY-TESTED DOCKER SETUPS

### **Option 1: willbullen/openclaw-docker (Production-Hardened)**

**Best for:** Security-focused production deployment

**Features:**
- ✅ Production-ready security hardening
- ✅ Non-root user (UID 1000)
- ✅ Dropped capabilities
- ✅ Read-only root filesystem
- ✅ Healthchecks built-in
- ✅ MCP tool isolation

**Setup:**
```bash
# 1. Clone
git clone https://github.com/willbullen/openclaw-docker.git
cd openclaw-docker

# 2. Configure
cp .env.example .env
vim .env  # Add API keys

# 3. Onboard
./scripts/onboard.sh

# 4. Start
./scripts/up.sh

# 5. Access
http://127.0.0.1:18789
```

**Time:** 15-20 minutes
**Complexity:** Low (scripts handle everything)
**Security:** 10/10 (hardened by security expert)

**Link:** [GitHub - willbullen/openclaw-docker](https://github.com/willbullen/openclaw-docker)

---

### **Option 2: phioranex/openclaw-docker (Auto-Update)**

**Best for:** Always-latest version, minimal maintenance

**Features:**
- ✅ Pre-built images (no compilation)
- ✅ Auto-builds daily
- ✅ Checks for updates every 6 hours
- ✅ Simple docker-compose.yml
- ✅ Config in ~/.openclaw

**Setup:**
```bash
# 1. Create docker-compose.yml
curl -O https://raw.githubusercontent.com/phioranex/openclaw-docker/main/docker-compose.yml

# 2. Onboard
docker compose run --rm openclaw-cli onboard

# 3. Start
docker compose up -d openclaw-gateway

# 4. Access
http://127.0.0.1:18789
```

**Time:** 10-15 minutes
**Complexity:** Very Low (pre-built image)
**Updates:** Automatic (daily builds)

**Link:** [GitHub - phioranex/openclaw-docker](https://github.com/phioranex/openclaw-docker)

---

### **Option 3: Official OpenClaw Docker**

**Best for:** Standard deployment, official support

**Features:**
- ✅ Official from OpenClaw team
- ✅ docker-setup.sh automated script
- ✅ Wizard-driven configuration
- ✅ Docker Compose v2 based

**Setup:**
```bash
# 1. Clone official repo
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 2. Run setup script
./docker-setup.sh

# 3. Follow wizard
# (Selects AI provider, channels, skills)

# 4. Access
http://127.0.0.1:18789
```

**Time:** 20-30 minutes (includes wizard)
**Complexity:** Low (wizard guides you)
**Support:** Official (main repo issues)

**Link:** [OpenClaw Docker Setup](https://github.com/openclaw/openclaw/blob/main/docker-setup.sh)

---

## 🎯 MINHA RECOMENDAÇÃO:

### **Para VOCÊ (Leo):**

**Use: Option 1 (willbullen/openclaw-docker)**

**Por quê:**
1. ✅ Production-hardened (security expert built)
2. ✅ Scripts prontos (onboard.sh, up.sh)
3. ✅ Security default (non-root, capabilities dropped)
4. ✅ Funciona (community tested)
5. ✅ Podemos adicionar NOSSA camada em cima

**Pipeline:**
```
1. Desinstalar atual (backup first!)
2. git clone willbullen/openclaw-docker
3. ./scripts/onboard.sh
4. ./scripts/up.sh
5. TESTAR tudo (dashboard, WhatsApp, etc.)
6. SÓ ENTÃO adicionar:
   ├─ Ollama config
   ├─ Tailscale setup
   ├─ Max proxy (se quiser)
   └─ GCS integration
```

---

## 📂 OPENCLAW DIRECTORY STRUCTURE (Community Standard)

### **Que JÁ EXISTE (não recriar):**

```
/root/openclaw/                   ← Source code (oficial)
├─ dist/                          ← Compiled code
│  ├─ gateway/                    ← Gateway server
│  ├─ channels/                   ← WhatsApp, Telegram, etc.
│  ├─ agents/                     ← Agent logic
│  ├─ tools/                      ← Built-in tools
│  └─ ...
├─ docker-compose.yml             ← Docker config
├─ docker-setup.sh                ← Auto-setup script
├─ scripts/                       ← Helper scripts
└─ skills/                        ← Available skills

/root/.openclaw/                  ← User config/data
├─ openclaw.json                  ← Main config
├─ credentials/                   ← API keys, tokens
│  ├─ whatsapp/                   ← Session files
│  └─ ...
├─ agents/                        ← Agent workspaces
│  └─ main/                       ← Default agent
│     ├─ sessions/                ← Conversation sessions
│     └─ ...
├─ workspace/                     ← Agent files
│  ├─ SOUL.md                     ← Personality
│  ├─ MEMORY.md                   ← Long-term memory
│  ├─ memory/                     ← Daily logs
│  ├─ inbox/                      ← Tasks (custom)
│  └─ outbox/                     ← Responses (custom)
├─ cron/                          ← Cron jobs
├─ logs/                          ← Gateway logs
└─ ...
```

**Nosso custom:**
- ✅ inbox/outbox (não existe nativamente - é nosso)
- ✅ UI themes (custom)
- ✅ GCS sync scripts (custom)

**Nativo do OpenClaw:**
- workspace/SOUL.md, MEMORY.md ← USE
- cron/ system ← USE
- skills/ ← USE (ou build custom)
- channels/ ← USE

---

## 🚀 PLANO: FRESH START COM COMMUNITY SETUP

### **FASE 1: Backup & Cleanup (5 min)**

```bash
# Backup workspace (SOUL, MEMORY)
ssh hostinger "tar czf /tmp/openclaw-workspace-backup-$(date +%Y%m%d).tar.gz /root/.openclaw/workspace/"
scp hostinger:/tmp/openclaw-workspace-backup-*.tar.gz ~/backup/

# Stop current
ssh hostinger "systemctl --user stop openclaw-gateway"

# Move atual (não delete!)
ssh hostinger "mv /root/openclaw /root/openclaw-OLD-$(date +%Y%m%d)"
ssh hostinger "mv /root/.openclaw /root/.openclaw-OLD-$(date +%Y%m%d)"
```

---

### **FASE 2: Deploy Community Setup (15 min)**

```bash
# Option 1: willbullen (recommended)
ssh hostinger "git clone https://github.com/willbullen/openclaw-docker.git /root/openclaw-new && cd /root/openclaw-new"

# Configure
ssh hostinger "cd /root/openclaw-new && cp .env.example .env"

# Add Doppler secrets to .env
ssh hostinger "cd /root/openclaw-new && echo 'ANTHROPIC_API_KEY='$(doppler secrets get ANTHROPIC_API_KEY --plain) >> .env"

# Onboard
ssh hostinger "cd /root/openclaw-new && ./scripts/onboard.sh"

# Start
ssh hostinger "cd /root/openclaw-new && ./scripts/up.sh"
```

---

### **FASE 3: Restore Workspace (10 min)**

```bash
# Extract backup
ssh hostinger "cd /tmp && tar xzf openclaw-workspace-backup-*.tar.gz"

# Copy SOUL, MEMORY, inbox/outbox
ssh hostinger "cp -r /tmp/root/.openclaw-OLD-*/workspace/* /root/.openclaw/workspace/"

# Restart to load
ssh hostinger "cd /root/openclaw-new && docker compose restart"
```

---

### **FASE 4: Test EVERYTHING (30 min)**

```bash
# 1. Dashboard loads?
curl http://localhost:18789

# 2. WhatsApp link?
ssh hostinger "cd /root/openclaw-new && docker compose exec openclaw openclaw channels login"

# 3. Ollama config?
# (Add after testing base works)

# 4. Send test message via WhatsApp
# 5. Verify response
```

---

### **FASE 5: Add Custom Layers (30 min)**

**ONLY after base works 100%:**

```
1. Add Ollama (if not in base)
2. Configure Tailscale Serve
3. Setup GCS sync (optional)
4. Custom UI theme (optional)
```

---

## 🎯 ESTIMATED TIME:

```
Community setup: 40 minutes
Custom layers: 30 minutes
TOTAL: ~70 minutes

vs

Nossa tentativa: 14 horas
Status: Dashboard não funciona

ROI: 12x faster usando community setup!
```

---

## 📚 SOURCES:

- [willbullen/openclaw-docker - Production Hardened](https://github.com/willbullen/openclaw-docker)
- [phioranex/openclaw-docker - Auto-Update](https://github.com/phioranex/openclaw-docker)
- [Official Docker Setup](https://docs.openclaw.ai/install/docker)
- [DigitalOcean 1-Click](https://www.digitalocean.com/blog/moltbot-on-digitalocean)
- [Simon Willison's Guide](https://til.simonwillison.net/llms/openclaw-docker)

---

**Quer executar este plano? Fresh start com community-tested setup?**

**Tempo estimado: 1 hora para sistema FUNCIONANDO de verdade.**
**Vs continuar debug atual: ??? horas, resultado incerto.**
