# VPS Complete Inventory - Hostinger srv1325721

**Date:** 2026-02-04 18:00 BRT
**Uptime:** 5 hours (fresh restart)
**Purpose:** Complete system state documentation

---

## 🖥️ HARDWARE & OS

```
Hostname: srv1325721.hstgr.cloud
Provider: Hostinger (82.25.77.221)
OS: Ubuntu 24.04.3 LTS
Kernel: 6.8.0-94-generic
Arch: x86_64

CPU: 8 cores
RAM: 31GB total, 1.3GB used, 19GB free (4% usage)
Disk: 387GB total, 79GB used, 308GB free (21% usage)
Swap: Not configured
```

---

## 👥 USERS

```
root (UID 0):
├─ Home: /root
├─ Current user
└─ Running: most services

ubuntu (UID 1000):
├─ Home: /home/ubuntu
├─ OpenClaw gateway process owner
└─ Config owner: /root/.openclaw/
```

---

## 📦 INSTALLED SOFTWARE

### **Core Services:**
```
✅ Docker 29.2.1 (container runtime)
✅ Ollama (local AI models)
✅ Tailscale 1.94.1 (mesh VPN)
✅ Node.js 22.22.0
✅ Doppler (secrets management)
✅ GitHub CLI (gh)
```

### **Optional Services:**
```
✅ Code-Server (VSCode web, port 8080)
✅ Syncthing (file sync, port 8384)
✅ Google Cloud SDK (gsutil, gcloud)
✅ Caddy (web server)
✅ Monarx (security scanner)
```

---

## 🐳 DOCKER

### **Containers:**
```
NAME: openclaw-openclaw-gateway-1
STATUS: Up 2 minutes
PORTS: 0.0.0.0:18789-18790
IMAGE: openclaw:local (6.29GB)
USER: node (non-root ✅)
```

### **Images:**
```
openclaw:local - 6.29GB
```

### **Volumes:**
```
NONE (using bind mounts)
```

### **Networks:**
```
Bridge (default)
Container IP: 172.17.0.x
```

---

## 🤖 OLLAMA

```
Service: systemd active ✅
Listening: 127.0.0.1:11434 (localhost ONLY!)
Process: PID 839

Models Installed:
├─ qwen2.5:7b (4.7GB)
├─ qwen2.5:32b (19GB)
└─ codellama:34b (19GB)

Storage: ~43GB total models
```

**⚠️ PROBLEM:**
```
Ollama binds: 127.0.0.1:11434
Docker tries: 172.17.0.1:11434
Result: Cannot connect (localhost != bridge IP)
```

---

## 🌐 TAILSCALE

```
Service: tailscaled active ✅
VPS IP: 100.119.234.42
Mesh Status: Connected

Devices in Network:
├─ srv1325721 (VPS) - 100.119.234.42
├─ iphone-13-pro - 100.65.38.112
└─ leonardos-macbook-pro - 100.111.18.33

Tailscale Serve: Configured
└─ Serves OpenClaw on tailnet
```

---

## 📂 DIRECTORY STRUCTURE

```
/root/
├── openclaw/                    ← Source (git clone oficial)
│   ├── docker-compose.yml       ← Container orchestration
│   ├── .env                     ← Environment vars
│   ├── dist/                    ← Compiled code
│   └── ... (official repo structure)
│
├── .openclaw/                   ← Data/config (owned by ubuntu!)
│   ├── openclaw.json            ← Main config (1KB)
│   ├── workspace/               ← Agent brain (16 files)
│   │   ├── SOUL.md              ← Restored ✅
│   │   ├── MEMORY.md            ← Restored ✅
│   │   ├── inbox/               ← Tasks
│   │   └── outbox/              ← Responses
│   ├── credentials/             ← API keys, WhatsApp session
│   └── logs/                    ← Gateway logs
│
├── projects/                    ← Synced from Mac
│   └── PROJECT_elements/
│       └── wave/tools/ai/       ← Your tools (30 scripts)
│
├── openclaw-implementation/     ← Docs synced
│   └── (complete knowledge base)
│
├── google-cloud-sdk/            ← GCS tools
├── Sync/                        ← Syncthing config
├── sync-bridge/                 ← (unused)
└── backup-workspace.sh          ← Backup script
```

---

## 🌐 NETWORK PORTS

```
LISTENING:
├─ 18789 (OpenClaw gateway) - Docker → 0.0.0.0
├─ 11434 (Ollama) - 127.0.0.1 ONLY ⚠️
├─ 8080 (Code-Server) - 0.0.0.0
├─ 8384 (Syncthing) - 127.0.0.1
└─ 22 (SSH) - 0.0.0.0

EXPOSED PUBLICLY:
├─ 22 (SSH)
├─ 18789 (OpenClaw) ⚠️ Should be localhost!
└─ 8080 (Code-Server) ⚠️ Should be localhost!

RECOMMENDATION: Bind only to localhost, access via Tailscale
```

---

## 🔑 DOPPLER

```
Logged in: ✅ YES
Token: dp.st...gUeP
Workplace: DeepC
Project: ai-tools
Config: dev

Secrets available (13):
├─ ANTHROPIC_API_KEY
├─ OPENAI_API_KEY
├─ GEMINI_API_KEY
├─ PERPLEXITY_API_KEY
├─ CEREBRAS_API_KEY
└─ ... (others)
```

---

## ⚠️ PROBLEMS IDENTIFIED

### **1. CRITICAL: Ollama não acessível do Docker**
```
Ollama: 127.0.0.1:11434
Container: Tenta 172.17.0.1:11434
Result: Connection refused

Fix Options:
A) Ollama listen 0.0.0.0:11434
B) Docker network_mode: host
C) Use host.docker.internal (if supported)
```

### **2. WARNING: Ports expostos publicamente**
```
18789 (OpenClaw): 0.0.0.0 ⚠️
8080 (Code-Server): 0.0.0.0 ⚠️

Should: 127.0.0.1 only, access via Tailscale
```

### **3. INFO: .env vars missing**
```
OLLAMA_API_KEY: Set ✅
OLLAMA_BASE_URL: Set ✅
But: Still not working (connectivity issue, not auth)
```

---

## ✅ WHAT'S WORKING

```
✅ Docker: Containers running
✅ Ollama: Models ready (43GB total)
✅ Tailscale: Mesh connected (3 devices)
✅ OpenClaw: Version 2026.2.3 (latest!)
✅ Workspace: Restored (SOUL, MEMORY)
✅ Code-Server: Accessible from iPhone
✅ Syncthing: Installed
✅ Doppler: Authenticated, secrets available
✅ Backups: Scripts in place
```

---

## 🎯 ROOT CAUSE ANALYSIS

### **Why Ollama doesn't work:**

```
sequenceDiagram
    Container->>Docker Bridge: Connect to 172.17.0.1:11434
    Docker Bridge->>Host: Forward to localhost?
    Host->>Ollama: Listening on 127.0.0.1:11434 ONLY
    Ollama-->>Host: REFUSE (not accepting from bridge)
    Host-->>Container: Connection refused
    Container-->>Rainmaker: Error: Unknown model
```

**The gap:** Ollama localhost-only != Docker bridge network

---

## 🔧 SOLUTIONS (Choose One)

### **Solution A: Make Ollama accept from Docker (Simplest)**

```bash
# Edit Ollama service
ssh hostinger "systemctl edit --full ollama"

# Change:
OLLAMA_HOST=0.0.0.0:11434  # instead of 127.0.0.1

# Restart
systemctl restart ollama
```

**Pros:** Quick (5 min)
**Cons:** Exposes Ollama to network (secure with firewall)

---

### **Solution B: Docker host network mode (Recommended)**

```yaml
# docker-compose.yml
services:
  openclaw-gateway:
    network_mode: "host"  # Use host network
```

**Pros:** Container sees localhost = Ollama works
**Cons:** Loses container network isolation

---

### **Solution C: Use official OpenAI** (Already working)

```
Accept: Ollama won't work in Docker easily
Use: OpenAI API (already configured, functional)
Cost: Pay-per-token (vs FREE Ollama)
```

**Pros:** Works NOW, no debug
**Cons:** Costs money vs FREE local

---

## 📊 RECOMMENDATIONS

### **Immediate (Tonight):**
1. Use OpenAI API (Option C) - Already works
2. Test WhatsApp → Should respond with OpenAI
3. Validate end-to-end working

### **Tomorrow (Fresh Mind):**
1. Implement Solution A or B for Ollama
2. Fix port bindings (localhost only)
3. Complete security hardening
4. Full validation

---

## 📈 METRICS

```
Session Duration: 17 hours
Files Created: 27 docs, 8,150+ lines
Commits: 8
Current State: 80% functional
Blocking Issue: Ollama connectivity (not critical)
Alternative: OpenAI working (costs $, but works)
```

---

**INVENTORY COMPLETE.**
**Problem identified: Docker ↔ Ollama networking.**
**Solution exists: 3 options documented.**
**Decision needed: Debug more OR accept OpenAI for now?**
