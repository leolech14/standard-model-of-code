# Fresh Start Checklist - O que Deletar vs Manter

**Purpose:** Guia para reimplementação limpa do OpenClaw
**Preserva:** Identity, memory, sessions
**Reconstrói:** Installation, config

---

## 🗑️ SAFE TO DELETE (pode recriar)

### **OpenClaw Installation:**
```bash
/root/openclaw/                    ← Git clone (reinstala em 2 min)
├── Source code
├── node_modules/
├── dist/
└── ... (tudo pode ser git cloned de novo)

Comando:
rm -rf /root/openclaw
```

**Por quê deletar:**
- Reinstala via: `git clone https://github.com/openclaw/openclaw`
- Fresh start = latest version
- Sem config debt acumulado

---

### **Docker Artifacts:**
```bash
Docker containers              ← Recria com docker compose up
Docker images                  ← Rebuild com docker compose build
Docker volumes (se vazios)     ← Recria automaticamente

Comandos:
docker compose down            # Stop containers
docker rm openclaw-*           # Remove containers
docker rmi openclaw:local      # Remove image
docker volume prune            # Remove unused volumes
```

**Por quê deletar:**
- Fresh build = clean state
- Remove accumulated layers
- Latest base images

---

### **Generated Config (EXCEPT workspace!):**
```bash
/root/.openclaw/openclaw.json  ← Wizard regenera

Comando:
rm /root/.openclaw/openclaw.json
```

**Por quê deletar:**
- Wizard cria config correto
- Remove manual edits que quebraram
- Schema validado automaticamente

---

### **Temporary/Cache Files:**
```bash
/tmp/*                         ← Always safe
~/.cache/                      ← Rebuild caches
~/.npm/                        ← npm cache
/root/.openclaw/logs/          ← Old logs (opcional)

Comandos:
rm -rf /tmp/openclaw-*
rm -rf ~/.cache/openclaw
```

---

### **Failed Attempts:**
```bash
/root/openclaw-OLD-*           ← Backup old installs
/root/.openclaw-OLD-*          ← Backup old configs

Comandos:
rm -rf /root/openclaw-OLD-*
rm -rf /root/.openclaw-OLD-*
```

**Por quê deletar:**
- Já temos backups no Mac
- Ocupando 2GB+ de espaço
- Não vamos voltar para eles

---

## 🔒 MUST KEEP (irreplaceable!)

### **1. Tailscale Identity (CRITICAL)**
```bash
/var/lib/tailscale/
├── tailscaled.state           ← Device identity, keys
└── ...

Backup ANTES de qualquer wipe:
tar czf ~/tailscale-backup.tar.gz /var/lib/tailscale/

Restore:
tar xzf tailscale-backup.tar.gz -C /
systemctl restart tailscaled
```

**Por quê manter:**
- ❌ Se perder: Device removido da tailnet
- ❌ Precisa re-approve no admin
- ❌ New IP, breaks bookmarks/scripts
- ✅ Backup = keep identity

---

### **2. WhatsApp Session (CRITICAL)**
```bash
/root/.openclaw/credentials/whatsapp/
├── creds.json                 ← Auth tokens
├── pre-keys.json              ← Encryption keys
└── ...

Backup:
tar czf ~/whatsapp-session.tar.gz /root/.openclaw/credentials/whatsapp/

Restore:
tar xzf whatsapp-session.tar.gz -C /root/.openclaw/credentials/
```

**Por quê manter:**
- ❌ Se perder: WhatsApp desconecta
- ❌ Precisa re-scan QR code
- ❌ Novo número na lista de devices
- ❌ Conversas antigas perdidas
- ✅ Backup = keep connection

---

### **3. Workspace (Personality & Memory)**
```bash
/root/.openclaw/workspace/
├── SOUL.md                    ← Rainmaker personality
├── IDENTITY.md                ← Name, emoji, vibe
├── MEMORY.md                  ← Long-term learning
├── USER.md                    ← Info about you
├── AGENTS.md                  ← Operating instructions
├── inbox/                     ← Task history
├── outbox/                    ← Response history
└── memory/                    ← Daily logs

Backup:
tar czf ~/workspace.tar.gz /root/.openclaw/workspace/

Restore:
tar xzf workspace.tar.gz -C /root/.openclaw/
```

**Por quê manter:**
- ❌ Se perder: Rainmaker esquece tudo
- ❌ Personality resets (generic bot)
- ❌ Learning perdido
- ❌ History inacessível
- ✅ Backup = preserve identity

---

### **4. API Keys & Credentials (If not using Doppler)**
```bash
/root/.openclaw/credentials/
└── (other than whatsapp/)

Backup:
# If using Doppler: SKIP (already external)
# If NOT: Backup manually with encryption

gpg -c credentials.tar.gz
```

**Por quê manter:**
- Se não usa Doppler: Única cópia de keys
- ✅ Doppler = não precisa backup (already external)

---

### **5. Custom Scripts & Tools**
```bash
/root/projects/PROJECT_elements/wave/tools/ai/
├── perplexity_research.py
├── analyze.py
├── cerebras_*.py
└── ... (30 scripts)

Backup:
# Already on Mac (synced)
# No backup needed from VPS
```

**Por quê manter:**
- Custom tooling única
- Rainmaker usa esses scripts
- ✅ Already on Mac (primary copy)

---

### **6. Documentation**
```bash
/root/openclaw-implementation/    ← Knowledge base
/root/projects/PROJECT_elements/  ← Synced docs

Backup:
# Already on Mac + committed to git
# No backup needed from VPS
```

---

## 📦 BACKUP PROCEDURE (Before Fresh Start)

### **Pre-Wipe Checklist:**

```bash
# 1. Tailscale identity ✅ (DONE)
tar czf ~/backup/tailscale-$(date +%Y%m%d).tar.gz /var/lib/tailscale/

# 2. WhatsApp session ⚠️ (DO THIS!)
tar czf ~/backup/whatsapp-$(date +%Y%m%d).tar.gz /root/.openclaw/credentials/whatsapp/

# 3. Workspace ✅ (DONE)
tar czf ~/backup/workspace-$(date +%Y%m%d).tar.gz /root/.openclaw/workspace/

# 4. Copy all to Mac
scp hostinger:~/backup/*.tar.gz ~/backup/

# 5. Verify backups
ls -lh ~/backup/*.tar.gz
# Should show: tailscale, whatsapp, workspace
```

---

## 🗑️ WIPE PROCEDURE

### **Safe Destruction:**

```bash
# 1. Stop services
docker compose down
systemctl --user stop openclaw-gateway
systemctl stop code-server

# 2. Remove OpenClaw
rm -rf /root/openclaw
rm -rf /root/.openclaw

# 3. Remove old backups (already on Mac)
rm -rf /root/openclaw-OLD-*
rm -rf /root/.openclaw-OLD-*

# 4. Clean Docker
docker system prune -af
docker volume prune -f

# 5. Keep:
# - /var/lib/tailscale/ (DON'T TOUCH!)
# - /root/projects/ (synced docs)
# - Doppler (external, safe)
```

---

## ✅ RESTORE PROCEDURE (After Fresh Install)

### **Post-Install Restoration:**

```bash
# 1. Fresh install OpenClaw (wizard ou docker)
cd /root
git clone https://github.com/openclaw/openclaw
cd openclaw
./docker-setup.sh
# Complete wizard (creates base config)

# 2. Restore Tailscale (if wiped)
tar xzf ~/backup/tailscale-*.tar.gz -C /
systemctl restart tailscaled

# 3. Restore WhatsApp session
tar xzf ~/backup/whatsapp-*.tar.gz -C /root/.openclaw/credentials/

# 4. Restore Workspace
tar xzf ~/backup/workspace-*.tar.gz -C /root/.openclaw/

# 5. Restart
docker compose restart

# 6. Test
openclaw status
# WhatsApp should reconnect automatically
# Rainmaker should remember everything
```

---

## 🎯 SUMMARY

### **DELETE (Regenerable):**
```
✅ /root/openclaw/ (source)
✅ Docker containers/images
✅ /root/.openclaw/openclaw.json (config)
✅ Logs, caches, temps
✅ Old backups (*-OLD-*)
```

### **KEEP (Irreplaceable):**
```
🔒 /var/lib/tailscale/ (identity)
🔒 /root/.openclaw/credentials/whatsapp/ (session)
🔒 /root/.openclaw/workspace/ (SOUL, MEMORY)
✅ /root/projects/ (docs, scripts)
✅ Doppler (external, always safe)
```

### **Backup Before Wipe:**
```
Priority 1: WhatsApp session ⚠️ (DO NOW if not done!)
Priority 2: Workspace ✅ (already backed up)
Priority 3: Tailscale ✅ (already backed up)
```

---

**Backups ready for fresh start?**
**Or want to fix current Ollama issue first?** 🦞
