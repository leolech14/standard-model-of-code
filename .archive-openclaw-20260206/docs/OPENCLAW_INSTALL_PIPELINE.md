# OpenClaw Installation Pipeline

**Purpose:** Receita completa para replicar sistema OpenClaw + Hostinger
**Audience:** Qualquer pessoa que queira instalar
**Time:** 45-60 minutos do zero ao funcionando

---

## Pré-requisitos

```
✅ VPS ou servidor Linux (4GB+ RAM recomendado)
✅ Número de telefone para WhatsApp (eSIM funciona)
✅ Conta Google (para GCS, opcional)
✅ Conta Anthropic ou usar Ollama only
```

---

## Parte 1: Infrastructure (20 min)

### 1.1 Provision VPS

**Hostinger (recomendado):**
```
1. Acesse: hostinger.com/vps
2. Escolha: KVM 4 ou superior (16GB+ RAM)
3. Template: Ubuntu 24.04 (ou OpenClaw se disponível)
4. Deploy
5. Anote: IP, senha root
```

**Ou Digital Ocean / Vultr / AWS:**
```
Ubuntu 24.04, 2+ vCPU, 8GB+ RAM, 50GB+ disk
```

### 1.2 SSH Access

```bash
# Generate SSH key (se não tiver)
ssh-keygen -t ed25519 -C "seu@email.com"

# Copy to VPS
ssh-copy-id root@SEU_VPS_IP

# Add to ~/.ssh/config
cat >> ~/.ssh/config << EOF
Host openclaw-vps
    HostName SEU_VPS_IP
    User root
    IdentityFile ~/.ssh/id_ed25519
EOF

# Test
ssh openclaw-vps "echo 'Connected!'"
```

---

## Parte 2: Install OpenClaw (15 min)

### 2.1 One-Line Install

```bash
# On VPS
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Ou manual:**
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | bash
apt-get install -y nodejs

# Install OpenClaw
npm install -g openclaw@latest

# Run onboarding
openclaw onboard
```

### 2.2 Configure During Wizard

```
1. Model/Auth Provider: Anthropic
2. Paste API key (de console.anthropic.com)
3. Default model: claude-sonnet-4-5
4. Channel: WhatsApp (QR link)
5. Skills: Select what you want
6. Done!
```

---

## Parte 3: WhatsApp Setup (10 min)

### 3.1 Get Phone Number

```
Option A: Buy eSIM (VIVO, TIM, Claro)
- vivo.com.br/esim
- R$10-20
- Ativa em 30 min

Option B: Physical SIM
- Compra em loja
- "Número novo" (importante!)
```

### 3.2 Link to OpenClaw

```bash
# On VPS
openclaw channels login --channel whatsapp

# Scan QR code with WhatsApp Business app
# Bot number now linked!
```

### 3.3 Test

```
From personal WhatsApp:
→ Message bot number
→ Should receive response
```

---

## Parte 4: Add Free Models (15 min, opcional)

### 4.1 Install Ollama

```bash
# On VPS
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull qwen2.5:32b     # General (19GB)
ollama pull codellama:34b   # Code (19GB)
```

### 4.2 Configure as Primary

```bash
openclaw models set ollama/qwen2.5:32b
openclaw models fallbacks add anthropic/claude-sonnet-4-5
```

### 4.3 Add Auth

```bash
# CRITICAL: Add Ollama to auth profiles
python3 << 'EOF'
import json

with open('/root/.openclaw/agents/main/agent/auth-profiles.json') as f:
    auth = json.load(f)

auth['profiles']['ollama:default'] = {
    "type": "local",
    "provider": "ollama",
    "baseUrl": "http://localhost:11434"
}

auth['lastGood']['ollama'] = 'ollama:default'

with open('/root/.openclaw/agents/main/agent/auth-profiles.json', 'w') as f:
    json.dump(auth, f, indent=2)

print("✓ Ollama auth added")
EOF

# Restart
systemctl --user restart openclaw-gateway
```

---

## Parte 5: Mobile Access (10 min, opcional)

### 5.1 Install Tailscale

```bash
# On VPS
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
# Authenticate in browser

# Configure OpenClaw
openclaw config set gateway.tailscale.mode serve
openclaw config set gateway.bind loopback
systemctl --user restart openclaw-gateway
```

### 5.2 On Phone

```
1. Install Tailscale app
2. Login (same account)
3. Open: https://HOSTNAME.tailXXX.ts.net/?token=YOUR_TOKEN
4. Dashboard accessible from phone!
```

---

## Distribuir Pipeline

### Method 1: Git Repo

```
repo/
├─ README.md              ← Este documento
├─ install.sh             ← Script automatizado
├─ .env.example           ← Template de configs
├─ docker-compose.yml     ← Container setup
└─ docs/
    ├─ TROUBLESHOOTING.md
    └─ ARCHITECTURE.md
```

**Usuário:**
```bash
git clone seu-repo
./install.sh
# Responde perguntas
# Sistema instala sozinho
```

### Method 2: Docker Image

```dockerfile
FROM ubuntu:24.04

# Install tudo
RUN curl -fsSL https://openclaw.ai/install.sh | bash && \
    curl -fsSL https://ollama.ai/install.sh | sh

# Pre-pull models
RUN ollama pull qwen2.5:32b

# Configs
COPY configs/ /root/.openclaw/

EXPOSE 18789
CMD ["openclaw", "gateway", "run"]
```

**Usuário:**
```bash
docker pull seu/openclaw-setup
docker run -e ANTHROPIC_API_KEY=xxx seu/openclaw-setup
```

### Method 3: One-Line Install

```bash
# Hospeda script em GitHub
curl -fsSL https://raw.githubusercontent.com/you/openclaw-setup/main/install.sh | bash -s -- \
  --whatsapp-number=+5554XXXX \
  --anthropic-key=sk-ant-xxx \
  --enable-ollama
```

**Tudo automático.**

---

## TEMPLATE COMPLETO (Para Compartilhar)

**Criar repo com:**

```
openclaw-production-setup/
├─ README.md                  ← Como instalar (este pipeline)
├─ install-full.sh            ← Seu install-dependencies.sh melhorado
├─ docker-compose.yml         ← Para quem prefere Docker
├─ configs/
│   ├─ openclaw.json.template
│   ├─ auth-profiles.json.template
│   └─ .env.example
├─ docs/
│   ├─ ARCHITECTURE.md        ← Seu OPENCLAW_ARCHITECTURE.md
│   ├─ TROUBLESHOOTING.md     ← Seu DIAGNOSTICS.md
│   └─ USAGE.md               ← Seu COMO_USAR
└─ scripts/
    ├─ fix-common-issues.sh   ← OPENCLAW_FIX_IMMEDIATE.sh
    ├─ verify-setup.sh        ← Testa se funcionou
    └─ backup-config.sh
```

**Usuário faz:**
```bash
git clone https://github.com/leolech/openclaw-production-setup
cd openclaw-production-setup
./install-full.sh
# Responde: VPS IP, WhatsApp number, API key
# 20 minutos depois: Sistema funcionando
```

---

`★ Insight ─────────────────────────────────────`
**Best practices para compartilhar:**

1. **Script + Docs** (básico, funciona)
2. **Docker** (reproduzível, isolado)
3. **One-liner** (fastest, menos controle)
4. **Git template** (completo, versionado)

**Seu caso:**
- Tem install-dependencies.sh ✅
- Tem docs extensas ✅
- Falta: Docker option
- Falta: One-liner
- Falta: .env.example

**80% lá! Só precisa empacotar melhor.**
`─────────────────────────────────────────────────`

**Quer que eu crie o repo template completo?**

Ou primeiro fix o sistema, depois empacota pra compartilhar?
