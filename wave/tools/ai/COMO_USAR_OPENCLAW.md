# Como Usar OpenClaw - Guia Prático

**Para:** Você que construiu mas não sabe usar ainda
**Nível:** Zero to Hero

---

## 1️⃣ USO BÁSICO - WhatsApp

### Mandar Mensagem para o Bot

**Do seu telefone pessoal (+555499628402):**

```
Abrir WhatsApp
→ Nova conversa
→ Número: +55 54 99681-6430
→ Mensagem: "Oi, você está funcionando?"
→ Aguardar resposta
```

**O que acontece:**
```
Sua mensagem
    ↓
Rainmaker (bot) recebe
    ↓
Ollama Qwen processa (FREE)
    ↓ (Se Ollama falhar → Claude Opus fallback)
Resposta gerada
    ↓
Você recebe no WhatsApp
```

---

### Tipos de Mensagens que Funcionam

**Perguntas simples:**
```
"Qual a previsão do tempo hoje?"
"Explica o que é quantum computing"
"Traduza 'Hello' para português"
```

**Code help:**
```
"Explica esse erro: [paste error]"
"Como fazer um loop em Python?"
"Revisa esse código: [paste code]"
```

**Tarefas:**
```
"Me lembra de ligar pro João às 15h"
"Adiciona na minha lista: comprar leite"
"Qual meu próximo compromisso?"
```

**Pesquisa:**
```
"Pesquisa sobre [topic]"
"Resumo das notícias de hoje"
"O que é [conceito]?"
```

---

## 2️⃣ USO AVANÇADO - Dashboard

### Acessar Dashboard

```
1. Abrir: http://localhost:18789/?token=51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984

2. Se não abrir, SSH tunnel:
   ssh -f -N -L 18789:127.0.0.1:18789 hostinger

3. Então abrir URL
```

### O Que Fazer no Dashboard

**Chat direto:**
```
Dashboard → Chat
→ Digite mensagem
→ Teste AI sem WhatsApp
→ Vê thinking process
```

**Ver canais:**
```
Dashboard → Channels
→ WhatsApp status
→ Link/unlink
→ Ver QR code
```

**Configurar:**
```
Dashboard → Config
→ Mudar settings
→ Adjust permissions
→ Change models
```

**Ver logs:**
```
Dashboard → Logs
→ Debug issues
→ See message flow
→ Check errors
```

---

## 3️⃣ COMANDOS CLI (VPS)

### Status Geral

```bash
ssh hostinger
cd /root/openclaw
pnpm openclaw status
```

**Mostra:**
- Gateway online?
- WhatsApp linked?
- Sessions ativas
- Memory usage
- Security warnings

### Ver Mensagens/Sessions

```bash
pnpm openclaw sessions
# Lista conversas ativas

pnpm openclaw logs --follow
# Watch logs em tempo real
```

### Manage Cron Jobs

```bash
pnpm openclaw cron list
# Ver jobs agendados

pnpm openclaw cron add \
  --name "Daily Backup" \
  --cron "0 3 * * *" \
  --message "Backup important files to GCS"
# Adicionar novo job

pnpm openclaw cron run <id>
# Testar job manualmente
```

### Trocar Models

```bash
pnpm openclaw models set ollama/qwen2.5:32b
# Default = FREE Ollama

pnpm openclaw models set anthropic/claude-opus-4-5
# Default = Claude Opus (paid)

pnpm openclaw models fallbacks list
# Ver fallbacks configurados
```

---

## 4️⃣ SKILLS - Extender Capacidades

### Ver Skills Disponíveis

```bash
pnpm openclaw skills
# Lista o que tem instalado

npx clawhub search <termo>
# Busca skills na comunidade
```

### Instalar Nova Skill

```bash
npx clawhub install github
# Instala GitHub skill

pnpm openclaw skills
# Confirma instalação
```

### Usar Skill via WhatsApp

```
Mensagem: "/github list my repos"
Bot: [lista seus repos do GitHub]
```

---

## 5️⃣ TROUBLESHOOTING

### Bot não responde no WhatsApp

```bash
# 1. Check gateway
ssh hostinger "systemctl --user status openclaw-gateway"

# 2. Check WhatsApp linked
ssh hostinger "cd /root/openclaw && pnpm openclaw status"

# 3. Ver logs
ssh hostinger "tail -f /tmp/openclaw/openclaw-*.log"

# 4. Restart se necessário
ssh hostinger "systemctl --user restart openclaw-gateway"
```

### Dashboard não abre

```bash
# 1. Check SSH tunnel
ps aux | grep "ssh.*18789"

# 2. Recreate tunnel
ssh -f -N -L 18789:127.0.0.1:18789 hostinger

# 3. Open with token
open "http://localhost:18789/?token=51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984"
```

### Ollama não está sendo usado

```bash
# Ver model atual
ssh hostinger "cd /root/openclaw && pnpm openclaw models status"

# Forçar Ollama
ssh hostinger "cd /root/openclaw && pnpm openclaw models set ollama/qwen2.5:32b"

# Restart gateway
ssh hostinger "systemctl --user restart openclaw-gateway"
```

---

## 6️⃣ TAREFAS COMUNS

### Adicionar Pessoa ao Allowlist

```bash
ssh hostinger "cd /root/openclaw && \
python3 << 'EOF'
import json
with open('/root/.openclaw/openclaw.json') as f:
    config = json.load(f)
config['channels']['whatsapp']['allowFrom'].append('+5554999999999')
with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
EOF
"

# Restart
ssh hostinger "systemctl --user restart openclaw-gateway"
```

### Mudar Tema do Dashboard

```bash
# Edit CSS no VPS
ssh hostinger "vim /root/openclaw/ui/src/styles/base.css"

# Rebuild
ssh hostinger "cd /root/openclaw && pnpm ui:build"

# Refresh browser (Cmd+Shift+R)
```

### Backup Manual para GCS

```bash
# Backup workspace
gsutil -m rsync -r /root/.openclaw/workspace \
  gs://elements-archive-2026/backups/openclaw/$(date +%Y%m%d)/
```

### Ver Custos de API

```bash
# Check Anthropic usage
open https://console.anthropic.com/settings/usage

# Ollama é FREE, sempre
```

---

## 7️⃣ TESTING - Aprenda Usando

### Test 1: Pergunta Simples

```
WhatsApp para bot:
"What is 2+2?"

Deve responder rápido (Ollama)
```

### Test 2: Código

```
WhatsApp para bot:
"Write a Python function to reverse a string"

Deve usar CodeLlama fallback (se configurado)
```

### Test 3: Complexo

```
WhatsApp para bot:
"Explain the architecture of a microservices system with examples"

Pode usar Claude se Ollama não conseguir
```

### Test 4: Dashboard Chat

```
Dashboard → Chat
Mensagem: "List all available skills"

Vê resposta formatada, com tool calls visíveis
```

### Test 5: Cron Job

```
ssh hostinger "cd /root/openclaw && \
pnpm openclaw cron add \
  --name 'Test Job' \
  --at '+1m' \
  --message 'This is a test cron job' && \
pnpm openclaw cron list"

Aguarda 1 minuto, verifica se rodou
```

---

## 8️⃣ DAILY USAGE

**Manhã:**
```
- Check WhatsApp: Alguma mensagem do bot?
- Dashboard Overview: System healthy?
```

**Durante o dia:**
```
- Manda perguntas via WhatsApp quando precisar
- Bot responde (seu AI assistant pessoal)
```

**Noite:**
```
- Check logs se teve algum erro
- Ver cron jobs rodaram
```

**Semanal:**
```
- Review usage/costs
- Adjust model settings se necessário
- Update OpenClaw: pnpm openclaw update
```

---

## 9️⃣ ATALHOS ÚTEIS

```bash
# Status rápido
alias oc-status='ssh hostinger "cd /root/openclaw && pnpm openclaw status"'

# Logs live
alias oc-logs='ssh hostinger "tail -f /tmp/openclaw/openclaw-*.log"'

# Restart
alias oc-restart='ssh hostinger "systemctl --user restart openclaw-gateway"'

# Dashboard
alias oc-dash='open "http://localhost:18789/?token=51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984"'
```

**Adiciona ao ~/.zshrc:**
```bash
# OpenClaw shortcuts
source ~/PROJECTS_all/PROJECT_elements/wave/tools/ai/openclaw-aliases.sh
```

---

## 🎓 LEARNING PATH

**Semana 1: Basics**
- Enviar 10+ mensagens WhatsApp
- Explorar dashboard
- Testar diferentes tipos de perguntas

**Semana 2: Advanced**
- Criar 2-3 cron jobs úteis (OpenClaw nativo!)
- Instalar 2-3 skills do ClawHub
- Customizar SOUL.md e IDENTITY.md
- Configurar heartbeat monitoring

**Semana 3: Integration**
- Build custom skills
- Configurar webhooks para serviços externos
- Integrar com GitHub, Google Calendar, etc.

**Mês 2+: Master**
- Multiple agents
- Complex automations
- Full dev workflow com sync

---

**COMECE AGORA:** Mande uma mensagem pro bot via WhatsApp!

**Quando tiver dúvida:** Consulte este guia ou pergunte pro próprio Rainmaker 😄
