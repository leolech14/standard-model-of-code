# OpenClaw VPS - Estado Real (2026-02-06)

**FONTE ÚNICA DE VERDADE** - Todas outras docs são históricas/teóricas.

---

## 📌 Informações Básicas

| Item | Valor |
|------|-------|
| **Provider** | Hostinger VPS (KVM 8) |
| **IP** | 82.25.77.221 |
| **Hostname** | srv1325721.hstgr.cloud |
| **SSH Aliases** | `rainmaker` ou `hostinger` |
| **OS** | Ubuntu 24.04.3 LTS (kernel 6.8.0-94) |
| **Criado em** | 2026-02-02 (template oficial Hostinger) |
| **OpenClaw Version** | 2026.2.2-3 |
| **Uptime** | Reiniciado 2026-02-06 02:26 UTC |

---

## 🏗️ Arquitetura Instalada

### Tipo de Instalação
**SYSTEM-WIDE** (NÃO git clone manual!)

```
/usr/bin/openclaw → /usr/lib/node_modules/openclaw/openclaw.mjs
/root/.openclaw/  → Configuração e dados
```

**Instalado via:** Template "Ubuntu 24.04 with OpenClaw" do Hostinger
**Método:** NPM global package (`npm install -g openclaw`)

### Estrutura de Diretórios

```
/root/.openclaw/
├── agents/              # Configuração de agentes
│   └── main/
│       ├── agent/      # Memory, auth-profiles, prompts
│       └── sessions/   # Session store (2 entries)
├── credentials/        # WhatsApp session files
│   ├── whatsapp/
│   └── whatsapp-allowFrom.json
├── workspace/          # Workspace data (22M)
├── canvas/             # Canvas host files
├── cron/               # Scheduled tasks
├── devices/            # Device registry
├── extensions/         # Extensions
├── identity/           # Identity files
├── media/              # Media cache
├── memory/             # Memory storage
└── openclaw.json       # CONFIGURAÇÃO PRINCIPAL (7.4KB)
```

### Serviço Gateway

**Gerenciado por:** systemd (user service)
**Service file:** `~/.config/systemd/user/openclaw-gateway.service`
**PID:** 1083 (ao momento da captura)
**Status:** `active (running)`
**Memory:** 570.2M (peak: 1.3G)
**Logs:** `/tmp/openclaw/openclaw-YYYY-MM-DD.log`

---

## 🤖 Configuração de Modelos

### Primary Model
```
minimax-portal/MiniMax-M2.1
```

**NÃO Ollama, NÃO Anthropic local!**

### Fallback Chain (primeiros 10)
1. `zai/glm-4.7`
2. `amazon-bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0`
3. `xai/grok-4-1-fast`
4. `xai/grok-vision-beta`
5. `xai/grok-code-fast-1`
6. `xai/grok-beta`
7. `xai/grok-4-1-fast-non-reasoning`
8. `openai/gpt-5.2-pro`
9. `openai/gpt-5.2-codex`
10. `openai/gpt-5.2-chat-latest`

**Total de fallbacks:** 27 modelos
**Problema atual:** Alguns modelos sem API keys configuradas (minimax, zai, amazon-bedrock)

---

## 🔑 Autenticação Configurada

### Auth Profiles Ativos
```json
{
  "google-antigravity:leonardolech3@gmail.com": "OAuth",
  "google:default": "API Key",
  "minimax-portal:default": "OAuth",
  "minimax:default": "API Key",
  "openrouter:default": "API Key",
  "zai:default": "API Key"
}
```

**Localização:** `/root/.openclaw/agents/main/agent/auth-profiles.json`

---

## 📱 Canais Ativos

### WhatsApp ✅
- **Status:** Linked (auth age atual varia)
- **Web Channel:** +555496816430
- **JID:** 555496816430:1@s.whatsapp.net
- **Allowed From:** +555499628402 (Leo's phone)
- **Last Message:** Auto-reply funcionando
- **Plugin:** `whatsapp` (enabled)

### Outros Canais
- **Telegram:** Não configurado
- **Discord:** Não configurado
- **Slack:** Skill disponível, não configurado

---

## 🛠️ Skills Instaladas

**Status:** 15/50 ready (30% utilização)

### ✅ Ready (15 skills)
1. 🐦 **bird** - X/Twitter CLI
2. 📦 **bluebubbles** - iMessage integration
3. 📦 **clawhub** - Skill marketplace
4. 🧩 **coding-agent** - Claude Code/Codex runner
5. 🐙 **github** - GitHub CLI (`gh`)
6. 📦 **healthcheck** - Security hardening
7. 📦 **mcporter** - MCP server management
8. 📝 **notion** - Notion API
9. 🖼️ **openai-image-gen** - DALL-E
10. ☁️ **openai-whisper-api** - Audio transcription
11. 🧿 **oracle** - Prompt bundling
12. 📦 **skill-creator** - Build custom skills
13. 🧵 **tmux** - Remote tmux control
14. 🎞️ **video-frames** - Video processing
15. 🌤️ **weather** - Weather forecasts

### ❌ Missing (35 skills)
Apple Notes, Apple Reminders, Bear Notes, 1Password, Gmail/Calendar, Obsidian, Slack, Spotify, Things 3, Trello, Voice Call, etc.

---

## 🌐 Network & Firewall

### Portas Abertas (UFW)
```
22/tcp    → SSH ✅
80/tcp    → HTTP (Caddy redirect) ✅
443/tcp   → HTTPS (Caddy) ✅
41641/udp → Tailscale ✅
```

### Serviços Escutando
```
127.0.0.1:18789  → OpenClaw Gateway (localhost only)
0.0.0.0:8080     → ? (unknown service)
0.0.0.0:22       → SSH
0.0.0.0:80       → Caddy
0.0.0.0:443      → Caddy
```

### Gateway Mode
**Bind:** `loopback` (127.0.0.1)
**Port:** 18789
**Access:** Localhost only (não acessível externamente)
**Dashboard:** http://127.0.0.1:18789/
**Auth:** Token-based (`16977b348d8f1a139cf9d63eb5613ff459c7266b0712535f`)

**Tailscale serve:** Habilitado (`resetOnExit: true`)

---

## 🐳 Docker Services

```
portainer   → 0.0.0.0:9000, 9443
authelia    → 0.0.0.0:9091
grafana     → 0.0.0.0:3000
loki        → 0.0.0.0:3100
promtail    → (no ports exposed)
```

**Observability stack ativo!**

---

## 💾 Recursos

### Disk
- **Total:** 387GB
- **Usado:** 160GB (42%)
- **Livre:** 227GB
- `.openclaw`: 22M
- `openclaw-custom`: 2.2G

### Memory
- **Total:** 31GB
- **Usado:** 1.8GB (6%)
- **Livre:** 27GB
- **Swap:** 0B (desabilitado)

### CPU
- **Cores:** 8
- **Load average:** 0.43, 1.03, 0.86

---

## ⚠️ Problemas Conhecidos

### 1. API Keys Faltando
```
FailoverError: No API key found for provider "minimax"
FailoverError: No API key found for provider "zai"
FailoverError: No API key found for amazon-bedrock
```

**Impacto:** Fallback cascade em caso de falha do MiniMax
**Status:** Sistema funciona com minimax-portal OAuth

### 2. Plugin Warnings
```
[plugins] intelligence missing register/activate export
[plugins] model-footer missing register/activate export
```

**Impacto:** Cosmético, não afeta operação
**Ação:** Nenhuma necessária

### 3. `openclaw models status` Crash
```
TypeError: Cannot read properties of undefined (reading 'trim')
```

**Impacto:** Comando CLI quebrado, mas modelos funcionam
**Workaround:** Ler `openclaw.json` diretamente
**Status:** Bug upstream

---

## 🔐 Segurança

### Firewall: ✅ Configurado
- UFW ativo com regras SSH/HTTP/HTTPS
- Tailscale port aberto

### SSH Hardening: ⚠️ PENDENTE
**Recomendações:**
1. OOMScoreAdjust=-1000 para sshd
2. Verificar que SSH escuta em 0.0.0.0:22 ✅
3. Considerar fail2ban
4. Considerar rate limiting

### Backup: ✅ Existe
**Localização local (Mac):**
- `~/backup/openclaw-workspace-COMPLETE-20260204-020801.tar.gz`
- `~/backup/whatsapp-session-backup.tar.gz`

**Última restauração:** 2026-02-04

---

## 📖 Operações Comuns

### Conectar ao VPS
```bash
ssh rainmaker
# ou
ssh hostinger
```

### Ver Status
```bash
openclaw health
openclaw gateway status
systemctl --user status openclaw-gateway
```

### Ver Logs
```bash
# Real-time
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# Histórico
ls -lh /tmp/openclaw/
```

### Reiniciar Gateway
```bash
openclaw gateway restart
# ou
systemctl --user restart openclaw-gateway
```

### Testar WhatsApp
Enviar mensagem de +555499628402 para o bot
Esperar auto-reply

### Ver Configuração
```bash
cat /root/.openclaw/openclaw.json | jq .
```

### Instalar Skill
```bash
openclaw skills install <nome>
# Exemplo:
openclaw skills install slack
```

---

## 🎯 Diferenças vs Documentação Antiga

| Aspecto | Docs Antigas | Realidade |
|---------|--------------|-----------|
| **Instalação** | Git clone `/root/openclaw` | NPM global `/usr/bin/openclaw` |
| **Primary Model** | `ollama/qwen2.5:14b` | `minimax-portal/MiniMax-M2.1` |
| **Fallback** | Anthropic Sonnet | 27 modelos diversos |
| **Data criação** | 2026-02-04 | 2026-02-02 |
| **Método install** | Manual clone | Template Hostinger |
| **Gateway** | Descrito como público | Localhost only |
| **Docker** | OpenClaw containers | Observability stack |

---

## 🔗 Recursos

### Hostinger API
- **VM ID:** 1325721
- **Firewall ID:** 191571
- **Datacenter:** 14
- **Plan:** KVM 8

### GitHub
- **Repo oficial:** https://github.com/OpenClaw/OpenClaw
- **Versão instalada:** v2026.2.2-3

### Docs Oficiais
- https://docs.openclaw.ai
- https://clawhub.com (skills)

### Backups Locais
- `~/backup/` (workspace + WhatsApp credentials)

---

## ✅ Checklist de Saúde

**Data:** 2026-02-06 02:39 UTC

- [x] VPS acessível via SSH
- [x] Firewall configurado (SSH/HTTP/HTTPS)
- [x] Gateway rodando (systemd active)
- [x] WhatsApp conectado e respondendo
- [x] Logs sendo gerados
- [x] Disk space OK (42% uso)
- [x] Memory OK (6% uso)
- [x] Docker services rodando
- [x] Backups existem
- [ ] API keys completas (minimax, zai, bedrock faltando)
- [ ] SSH hardening completo

---

## 📝 Notas Importantes

1. **OpenClaw FUNCIONA** - Sistema em produção, WhatsApp respondendo
2. **Configuração diferente da docs** - Template Hostinger != instalação manual
3. **Gateway localhost-only** - Use Tailscale para acesso remoto
4. **Modelo primário MiniMax** - Via OAuth portal (grátis?)
5. **Fallbacks não todos configurados** - Mas sistema funcional
6. **Observability ativa** - Grafana/Loki/Promtail rodando
7. **Disk space abundante** - 227GB livres
8. **Memory subutilizada** - 27GB livres de 31GB

---

**ESTA É A VERDADE. TODAS AS OUTRAS DOCS SÃO HISTÓRICAS.**

Última atualização: 2026-02-06 02:40 UTC
Auditado por: Claude Opus 4.6
Método: SSH direto + Hostinger API
