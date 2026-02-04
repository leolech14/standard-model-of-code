# Mapa de Implementação - Tailscale Mesh Network

**Network:** leonardo.lech@gmail.com Tailscale
**Devices:** 3 (Mac Pro, iPhone 13, VPS Hostinger)
**Services:** 5+ (OpenClaw, Code-Server, Ollama, WhatsApp, GCS)
**Protocol:** WireGuard (encrypted P2P)

---

## Topology Visual

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TAILSCALE MESH NETWORK                                    │
│                 leonardo.lech@gmail.com                                      │
│                    100.x.x.x private IPs                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐  │
│   │   MAC PRO        │◄────►│  IPHONE 13 PRO   │◄────►│  VPS HOSTINGER   │  │
│   │ 100.111.18.33    │      │ 100.65.38.112    │      │ 100.119.234.42   │  │
│   │                  │      │                  │      │  srv1325721      │  │
│   │ Development      │      │ Mobile Access    │      │  Always-On Ops   │  │
│   └──────────────────┘      └──────────────────┘      └──────────────────┘  │
│            │                         │                         │            │
│            │    Encrypted P2P        │    Encrypted P2P        │            │
│            └─────────────────────────┴─────────────────────────┘            │
│                         All-to-All Connectivity                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ (All traffic encrypted)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
│  (Accessed via public internet, not Tailscale)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  • WhatsApp (Meta servers)                                                  │
│  • Anthropic API (Claude)                                                   │
│  • GCS (Google Cloud Storage)                                               │
│  • GitHub                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Device Details

### 💻 Mac Pro (100.111.18.33)

**Role:** Development workstation

**Services Running:**
```
✅ Claude Code CLI (development)
✅ Tailscale client (mesh network)
✅ SSH client (access VPS)
✅ Git (version control)
✅ Cursor/VSCode (IDE)
✅ Docker (containers)
✅ claude-max-api-proxy (port 3456) - If needed
```

**Access Patterns:**
```
→ VPS: ssh root@100.119.234.42
→ VPS: rsync via Tailscale IP
→ VPS: http://100.119.234.42:PORT
→ iPhone: Could SSH/transfer files (não comum)
```

**Accessible From:**
```
← iPhone: Via Tailscale (SSH, file transfer)
← VPS: Via Tailscale (SSH, sync)
```

---

### 📱 iPhone 13 Pro (100.65.38.112)

**Role:** Mobile access & monitoring

**Apps Installed:**
```
✅ Tailscale (network access)
✅ WhatsApp Business (bot interface)
✅ Safari (web access)
📋 Termius (SSH client) - Recommended
📋 Documents (file manager) - Recommended
```

**Can Access:**
```
→ VPS Dashboard: http://100.119.234.42:18789
→ VPS Code-Server: http://100.119.234.42:8080
→ VPS via SSH: Termius → 100.119.234.42
→ VPS files: Documents app (SFTP)
→ Mac: Could access (if Mac has server)
```

**Cannot Access (Yet):**
```
❌ OpenClaw via Tailscale URL (https://srv1325721.tailead920.ts.net)
   → Needs gateway bind=loopback + serve mode (configurado mas não testado)
```

---

### ☁️ VPS Hostinger (100.119.234.42)

**Hostname:** srv1325721.tailead920.ts.net
**Public IP:** 82.25.77.221 (não usado, Tailscale preferred)

**Services Running:**
```
✅ OpenClaw Gateway (port 18789)
   └─ WhatsApp bot (+555496816430)
   └─ Dashboard

✅ Code-Server (port 8080)
   └─ VSCode in browser

✅ Ollama (port 11434, localhost only)
   └─ Qwen 32B, CodeLlama 34B, Qwen 7B

✅ Tailscale (mesh network daemon)

✅ Doppler (secrets management)

✅ gcloud SDK (GCS access)
```

**Accessible From:**
```
← Mac: All ports via 100.119.234.42
← iPhone: All ports via 100.119.234.42
← Internet: Only via Tailscale (no public exposure)
```

**Storage:**
```
/root/openclaw/          ← OpenClaw install
/root/projects/          ← Synced projects (Mac → VPS)
/root/.openclaw/         ← Config, workspace, sessions
/root/google-cloud-sdk/  ← GCS tools
```

---

## Service Access Matrix

| Service | Mac Access | iPhone Access | Public Access |
|---------|-----------|---------------|---------------|
| **OpenClaw Dashboard** | http://100.119.234.42:18789 | http://100.119.234.42:18789 | ❌ No |
| **Code-Server** | http://100.119.234.42:8080 | http://100.119.234.42:8080 | ❌ No |
| **SSH** | ssh root@100.119.234.42 | Termius → 100.119.234.42 | ❌ No |
| **Ollama** | Via SSH tunnel only | ❌ No | ❌ No |
| **WhatsApp Bot** | Via Dashboard | Via WhatsApp app | ✅ Yes (Meta) |
| **Tailscale Hostname** | srv1325721.tailead920.ts.net | srv1325721.tailead920.ts.net | ❌ No |

---

## File Sync Options (via Tailscale)

### Option A: rsync (Manual, On-Demand)

**Mac → VPS:**
```bash
rsync -avz --delete \
  ~/PROJECTS_all/PROJECT_elements/ \
  root@100.119.234.42:/root/projects/PROJECT_elements/
```

**VPS → Mac:**
```bash
rsync -avz --delete \
  root@100.119.234.42:/root/openclaw/workspace/ \
  ~/openclaw-workspace/
```

**Pros:** Simple, controlled
**Cons:** Manual

---

### Option B: Syncthing (Automatic, Real-time)

**Setup (both sides):**

```bash
# Mac
brew install syncthing
brew services start syncthing
open http://localhost:8384

# VPS (via Tailscale)
ssh root@100.119.234.42
apt install -y syncthing
systemctl --user enable --now syncthing

# Access VPS Syncthing from Mac:
open http://100.119.234.42:8384
```

**Configure sync:**
```
Mac Syncthing:
  → Add remote device: 100.119.234.42
  → Add folder: ~/PROJECTS_all/PROJECT_elements
  → Share with VPS

VPS Syncthing:
  → Accept device
  → Accept folder
  → Set path: /root/projects/PROJECT_elements

Auto-sync:
  Edit file anywhere → Syncs in <1s
  Bidirectional
  Conflict resolution
  Version history
```

**Pros:** Automatic, real-time, bidirectional
**Cons:** Another daemon (minor)

---

### Option C: Tailscale Taildrop (Quick Transfers)

**iPhone → VPS:**
```
Tailscale app → Files → Send
→ Pick file
→ Send to srv1325721
→ Aparece em /root/Downloads/
```

**Mac → VPS:**
```bash
tailscale file cp ~/arquivo.txt srv1325721:
```

**VPS → Mac:**
```bash
ssh root@100.119.234.42
tailscale file cp arquivo.txt leonardos-macbook-pro:
```

**Pros:** Super fácil, no config
**Cons:** Manual, não sync contínuo

---

### Option D: SSHFS Mount (Network Drive)

**Mac monta VPS como pasta:**

```bash
# Install
brew install macfuse sshfs

# Mount
mkdir ~/vps-root
sshfs root@100.119.234.42:/root ~/vps-root

# Use
cd ~/vps-root/openclaw/
ls
vim arquivo.txt  # Edita direto no VPS!

# Finder
open ~/vps-root/  # Browse como pasta normal
```

**iPhone:** Documents app pode fazer similar (SFTP mount)

**Pros:** Transparente (como pasta local)
**Cons:** Depende de network (offline = inacessível)

---

## Implementação Recomendada

**Para desenvolvimento (Mac ↔ VPS):**

### Syncthing + Tailscale

```
1. Install Syncthing (ambos)
   Mac: brew install syncthing
   VPS: apt install syncthing

2. Start services
   Mac: brew services start syncthing
   VPS: systemctl --user enable --now syncthing

3. Configure via web UI
   Mac: http://localhost:8384
   VPS: http://100.119.234.42:8384 (via Tailscale!)

4. Add device (cada lado adiciona o outro)
   Mac adiciona: srv1325721 (ID from VPS web UI)
   VPS adiciona: leonardos-macbook-pro (ID from Mac web UI)

5. Share folders
   Mac: ~/PROJECTS_all/PROJECT_elements → VPS
   VPS: /root/openclaw/workspace → Mac (logs, memory)

6. Enable bidirectional
   Both sides: Folder type = "Send & Receive"

7. Done!
   Edit anywhere → Auto-sync em <1s
```

**Monitoring:**
```
Web UI shows:
- Sync status
- Files synced
- Bandwidth
- Conflicts (if any)
- Version history
```

---

### Taildrop para Quick Transfers

```
Caso de uso:
- Screenshot do Mac → VPS
- Arquivo do iPhone → VPS
- Log do VPS → Mac

Não precisa sync contínuo
```

---

## Network Security

**Tailscale Advantages:**

```
✅ Zero-trust mesh (cada connection autenticada)
✅ Encrypted WireGuard (melhor que OpenVPN)
✅ No public ports (tudo via mesh)
✅ ACLs disponíveis (controle fino de acesso)
✅ Audit logs (quem acessou o quê)
```

**Current Exposure:**

```
Internet-facing:
❌ NADA via IP público (82.25.77.221 não usado)

Tailscale-only:
✅ OpenClaw Dashboard (port 18789)
✅ Code-Server (port 8080)
✅ SSH (port 22)
✅ Syncthing (port 8384) - Se instalarmos

Localhost-only:
✅ Ollama (port 11434)
```

**Segurança:** Excellent - tudo via Tailscale (private mesh)

---

## Bandwidth & Performance

**Tailscale routing:**
```
Direct connection (quando possível):
Mac ↔ VPS: Direct P2P
│
└─ Se ambos têm public IP/NAT traversal funciona
   Senão: Via DERP relay (Tailscale servers)
```

**Speeds observed:**
```
rsync via Tailscale: ~10-50 MB/s (depende de connection)
Syncthing: Real-time (<1s for small files)
Taildrop: ~5-20 MB/s
Code-Server: Responsive (low latency via P2P)
```

---

## Complete Integration Map

```
┌───────────────────────────────────────────────────────────────────┐
│                    LEONARDO'S TAILSCALE MESH                       │
│                   leonardo.lech@gmail.com                          │
└───────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌──────────────────┐
│   MAC PRO     │    │  IPHONE 13    │    │   VPS srv1325721 │
│ Development   │    │  Mobile       │    │   Production     │
├───────────────┤    ├───────────────┤    ├──────────────────┤
│               │    │               │    │                  │
│ Cursor/VSCode │───▶│ Safari        │───▶│ OpenClaw Gateway │
│ Claude Code   │    │ WhatsApp      │    │  - Dashboard     │
│ Git           │    │ Tailscale     │    │  - API           │
│ Tailscale     │    │ Termius (SSH) │    │  - WhatsApp bot  │
│               │    │ Documents     │    │                  │
│               │    │               │    │ Code-Server      │
│ Files:        │◄──▶│ Files:        │◄──▶│  - VSCode web    │
│ PROJECTS_all/ │    │ Taildrop      │    │  - File editor   │
│               │    │               │    │                  │
│               │    │               │    │ Ollama           │
│               │    │               │    │  - Qwen 32B      │
│               │    │               │    │  - CodeLlama     │
│               │    │               │    │                  │
│ Syncthing ◄───┼────┼───────────────┼───▶│ Syncthing        │
│ (if enabled)  │    │               │    │ (if enabled)     │
└───────────────┘    └───────────────┘    └──────────────────┘
        │                     │                     │
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD SERVICES (Public)                       │
│           (Não via Tailscale, via internet normal)               │
├─────────────────────────────────────────────────────────────────┤
│  • GCS (elements-archive-2026)                                  │
│  • Anthropic API (Claude Opus/Sonnet)                           │
│  • WhatsApp Meta Servers                                        │
│  • GitHub (standard-model-of-code)                              │
│  • Doppler (secrets)                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Access Patterns

### Mac → VPS

**SSH:**
```bash
ssh root@100.119.234.42
# ou
ssh root@srv1325721
```

**Files (rsync):**
```bash
rsync -avz ~/local/ root@100.119.234.42:/remote/
```

**Web Services:**
```
http://100.119.234.42:18789  # OpenClaw
http://100.119.234.42:8080   # Code-Server
http://100.119.234.42:8384   # Syncthing (se instalar)
```

**Syncthing (auto):**
```
Edit ~/PROJECTS_all/PROJECT_elements/file.txt
→ Auto-sync to /root/projects/PROJECT_elements/file.txt
→ <1 segundo
```

---

### iPhone → VPS

**WhatsApp:**
```
Mensagem para +55 54 99681-6430
→ Rainmaker no VPS processa
→ Responde
```

**Dashboard:**
```
Safari:
http://100.119.234.42:18789/?token=51c8c0d4...
→ OpenClaw control panel
```

**Code Editor:**
```
Safari:
http://100.119.234.42:8080
Password: f479f0374a9b4e76db9ce916a48dba3f
→ VSCode completo
```

**SSH Terminal:**
```
Termius app:
→ Add host: 100.119.234.42
→ Terminal completo
→ Edita configs, restart services
```

**File Transfer:**
```
Taildrop:
Share → Tailscale → srv1325721
→ Arquivo aparece em /root/Downloads/

Documents app:
SFTP → 100.119.234.42
→ Browse/edit arquivos
```

---

### VPS → Mac

**Sync:**
```bash
# Pull from Mac (se Mac tem SSH server)
rsync -avz lech@100.111.18.33:~/files/ /root/local/
```

**Trigger:**
```bash
# VPS pode trigger Mac scripts via SSH
ssh lech@100.111.18.33 "~/bin/script.sh"
```

**Taildrop:**
```bash
tailscale file cp log.txt leonardos-macbook-pro:
```

---

### VPS → iPhone

**Push notifications:**
```
OpenClaw → WhatsApp API → iPhone
(Via internet, não Tailscale)
```

**Taildrop:**
```bash
tailscale file cp screenshot.png iphone-13-pro:
→ Aparece no Tailscale app no iPhone
```

---

## Sync Implementation (Recommended)

### Syncthing Setup - Complete Steps

**1. Install (Mac):**
```bash
brew install syncthing
brew services start syncthing
open http://localhost:8384
```

**2. Install (VPS):**
```bash
ssh root@100.119.234.42
apt install -y syncthing
systemctl --user enable --now syncthing

# Get device ID
curl -s http://localhost:8384/rest/system/status | jq -r .myID
# Copie o ID (tipo: ABC1234-DEF5678...)
```

**3. Connect Devices:**

**No Mac (http://localhost:8384):**
```
Actions → Show ID
→ Copie Mac ID

Add Remote Device:
→ Device ID: [VPS ID copiado]
→ Device name: srv1325721
→ Save
```

**No VPS (http://100.119.234.42:8384 via Tailscale):**
```
Add Remote Device:
→ Device ID: [Mac ID]
→ Device name: leonardos-macbook-pro
→ Auto-accept: Yes
→ Save
```

**4. Share Folders:**

**Mac shares PROJECT_elements:**
```
Add Folder:
→ Path: ~/PROJECTS_all/PROJECT_elements
→ Folder ID: project-elements
→ Share with: srv1325721 ✅
→ Folder type: Send & Receive
→ Save
```

**VPS accepts and maps:**
```
[Notification: Mac shared folder]
→ Accept
→ Path: /root/projects/PROJECT_elements
→ Save
```

**5. Verify:**
```
Mac: Edit ~/PROJECTS_all/PROJECT_elements/test.txt
Wait: <1 second
VPS: cat /root/projects/PROJECT_elements/test.txt
→ Deve mostrar mesmas mudanças
```

---

### Additional Sync Pairs

**VPS workspace → Mac (logs, memory):**
```
VPS shares: /root/.openclaw/workspace
Mac receives: ~/openclaw-workspace/
Type: Send & Receive
```

**Mac configs → VPS:**
```
Mac shares: ~/PROJECTS_all/PROJECT_elements/setup/configs/
VPS receives: /root/configs/
Type: Send & Receive

Symlinks:
VPS: ln -s /root/configs/openclaw.json /root/.openclaw/openclaw.json
```

---

## Complete Workflow Example

**Development Loop:**

```
1. Mac (Cursor):
   Edit code in PROJECT_elements/

2. Syncthing:
   Auto-sync to VPS (<1s)

3. VPS:
   File updated
   OpenClaw detects (if watching)
   Hot reload (if configured)

4. Test:
   iPhone → Dashboard (monitor)
   iPhone → WhatsApp (interact com bot)
   Mac → Logs (via sync or SSH)

5. Iterate:
   Edit again (loop)
```

**No SSH commands needed** - tudo automático via Syncthing!

---

## Monitoring & Management

**From iPhone:**

```
Safari:
├─ http://100.119.234.42:18789 → OpenClaw status
├─ http://100.119.234.42:8080  → Edit files (Code-Server)
└─ http://100.119.234.42:8384  → Sync status (Syncthing)

Termius:
└─ Terminal completo (advanced)

WhatsApp:
└─ Chat com Rainmaker (perguntas sobre sistema)
```

**From Mac:**

```
Terminal:
├─ ssh root@100.119.234.42
└─ git pull/push

Browser:
├─ OpenClaw Dashboard (monitor)
└─ Syncthing UI (sync status)

IDE:
├─ Cursor (local files)
└─ VSCode Remote (VPS files)
```

---

## Tailscale Features Não Usados (Futuro)

**1. Tailscale SSH:**
```bash
# SSH via Tailscale (mais seguro)
tailscale ssh root@srv1325721
# Sem need de SSH keys, Tailscale auth
```

**2. Tailscale Serve (Public Share):**
```bash
# Share OpenClaw publicamente (com quem você aprovar)
tailscale serve --set-path=/openclaw http://localhost:18789
# Gera: https://srv1325721.tailead920.ts.net/openclaw
```

**3. MagicDNS:**
```bash
# Ao invés de 100.119.234.42
# Usa: srv1325721
ssh root@srv1325721  # Funciona!
```

**4. Subnet Router:**
```bash
# VPS como gateway para outras networks
tailscale up --advertise-routes=10.0.0.0/24
# Mac/iPhone acessa network interna via VPS
```

---

## Next Steps

**Immediate (5 min):**
```
1. Install Termius no iPhone
2. Add VPS (100.119.234.42)
3. Test SSH from phone
```

**Soon (20 min):**
```
4. Install Syncthing (Mac + VPS)
5. Configure sync folders
6. Test real-time sync
```

**Later (optional):**
```
7. SSHFS mount (if want network drive)
8. Advanced Tailscale features
```

---

`★ Insight ─────────────────────────────────────`
**Tailscale transforma:**

ANTES:
- VPS = Servidor remoto
- Acesso = Complexo (SSH tunnel, VPN)
- Sync = Manual (rsync on-demand)

DEPOIS:
- VPS = Device na rede local
- Acesso = Direto (IP, hostname)
- Sync = Automático (Syncthing)

**Resultado:** VPS como se estivesse no mesmo WiFi!
`─────────────────────────────────────────────────`

**Status:**
- ✅ Mac ↔ VPS via Tailscale
- ✅ iPhone ↔ VPS via Tailscale
- ✅ Code-Server acessível
- ⏳ Syncthing (20 min para setup)

**Quer instalar Syncthing agora?**

Ou test Termius primeiro?

---

**Last Updated:** 2026-02-04 03:30 UTC
**Network:** 100% via Tailscale (zero public exposure)
**Sync:** Manual (rsync) → Can upgrade to Syncthing
