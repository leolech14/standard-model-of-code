# Manual de Arquitetura de Automação
## OpenClaw + n8n - Sistema Completo

**Versão:** 1.0
**Data:** 2026-02-04
**Propósito:** Guia definitivo de automação multi-camada

---

## Visão Geral

**Arquitetura:** 2-Layer Automation Stack
**Camada 1:** OpenClaw (Conversational AI + Simple Automation)
**Camada 2:** n8n (Complex Workflows + Integrations)
**Integração:** API webhooks bidirecionais

---

## CAMADA 1: OpenClaw (Agent Layer)

### O Que É

**OpenClaw** = Personal AI assistant framework
- Conversational interface (WhatsApp, Telegram, Discord, etc.)
- Autonomous agent com memória persistente
- Natural language task execution
- Built-in cron para tasks simples

### Capabilities

**1. Conversational Tasks:**
```
Você: "Qual a previsão do tempo?"
Rainmaker: [Usa weather skill] "Hoje: 25°C, ensolarado"
```

**2. Simple Cron:**
```bash
openclaw cron add \
  --name "Morning Reminder" \
  --cron "0 8 * * *" \
  --message "Bom dia! Seu dia começa em 30 min"
```

**3. Skills (14 ready, 36 available):**
- GitHub integration
- Weather
- Twitter/X
- Notion
- Image generation (DALL-E)
- Audio transcription (Whisper)
- Video processing
- E mais...

**4. Autonomous Agent:**
```
Você: "Monitora meu inbox e me avisa se algo urgente"
Rainmaker: [Monitora contínuo, decide o que é urgente, te avisa]
```

### Quando Usar OpenClaw

**✅ Use para:**
- Chat-driven tasks ("Faça X")
- Ad-hoc queries ("Quanto é X?")
- Personal assistant (lembretes, monitoring)
- Simple scheduling (1-2 step tasks)
- Anything needing AI reasoning

**❌ Não use para:**
- Complex workflows (5+ steps)
- Team collaboration
- Data pipelines
- Strict approval processes
- Tasks sem AI necessário

### OpenClaw Cron Limits

```
Bom para:
- Daily reminder
- Hourly check
- Simple notifications

Ruim para:
- ETL pipelines
- Multi-service orchestration
- Complex data transformations
- Conditional branching (if A then B else C)
```

---

## CAMADA 2: n8n (Workflow Layer)

### O Que É

**n8n** = Visual workflow automation platform
- 200+ pre-built integrations
- No-code visual editor
- Complex logic (branching, loops, error handling)
- Team collaboration

### Capabilities

**1. Visual Workflows:**
```
[Schedule Node: 6 AM daily]
    ↓
[GitHub: Get commits]
    ↓
[Filter: Only main branch]
    ↓
[AI: Summarize changes]
    ↓
[Slack: Post to #dev]
    ↓
[WhatsApp: Notify team lead]
```

**2. 200+ Integrations:**
- GitHub, GitLab, Bitbucket
- Notion, Airtable, Google Sheets
- Slack, Discord, Teams
- Gmail, Outlook
- AWS, GCP, Azure
- PostgreSQL, MySQL, MongoDB
- Stripe, PayPal
- E MUITO mais...

**3. Advanced Logic:**
```
IF (commit has "BREAKING")
  → Post to #urgent
  → Send email to team
  → Create Jira ticket
ELSE
  → Just log it
```

**4. Error Handling:**
```
TRY:
  API call
CATCH (error):
  Retry 3x
  If still fails → Alert admin
  Continue workflow
```

### Quando Usar n8n

**✅ Use para:**
- Scheduled workflows (complex)
- Multi-step processes
- API integrations (200+ services)
- Data pipelines
- Team workflows
- Anything com passos explícitos

**❌ Não use para:**
- Simple chat queries
- Ad-hoc tasks
- Anything melhor via conversa
- Single-step operations

---

## INTEGRAÇÃO: OpenClaw ↔ n8n

### Method 1: OpenClaw Triggers n8n

**Use case:** Chat command inicia workflow complexo

```
Você (WhatsApp): "Cria relatório completo do projeto X"
    ↓
OpenClaw: Detecta comando complexo
    ↓
OpenClaw Skill: Chama n8n webhook
    ↓
n8n Workflow:
    [GitHub: Get all data]
    [Notion: Get tasks]
    [GCS: Get docs]
    [AI: Analyze + summarize]
    [Generate: PDF report]
    [Upload: Google Drive]
    [Notify: WhatsApp com link]
    ↓
Você: Recebe link do relatório
```

**Implementação:**

```javascript
// OpenClaw skill: trigger-n8n.md
Quando usuário pede relatório:
1. POST http://localhost:5678/webhook/relatorio
2. Passa parâmetros (projeto, período)
3. n8n executa workflow
4. Retorna resultado
5. OpenClaw envia para usuário
```

---

### Method 2: n8n Triggers OpenClaw

**Use case:** Workflow scheduled precisa AI decision

```
n8n Schedule (6 AM):
    [GitHub: Get yesterday commits]
    [Filter: >100 lines changed]
    [Send to OpenClaw API]
    ↓
OpenClaw Agent:
    [AI analyzes code changes]
    [Decides if needs review]
    [Generates summary]
    ↓
n8n recebe resposta:
    [If needs review → Create PR comment]
    [Else → Just log]
```

**Implementação:**

```javascript
// n8n HTTP Request node
POST http://localhost:18789/api/agent
Headers: { Authorization: "Bearer openclaw-token" }
Body: {
  message: "Analyze these commits: [data]",
  model: "ollama/qwen2.5:32b"
}
```

---

### Method 3: Hybrid (Ideal)

**Use case:** Best of both worlds

```
FRONTEND (você):
    WhatsApp, Dashboard, Voice
        ↓
    OpenClaw (entende natural language)
        ↓ [decide]
        ├─ Simple? → OpenClaw executa direto
        │
        └─ Complex? → Triggers n8n
                         ↓
                     n8n workflow
                         ↓
                     Resultado → OpenClaw
                         ↓
                     Você (via chat)
```

**Exemplo híbrido:**

```
Você: "Backup meus projetos importantes"

OpenClaw decide:
- Quais projetos? → Pergunta
- Você: "Elements, Atman, Sentinel"
- OpenClaw: OK, triggering backup workflow

n8n workflow:
    [Compress: PROJECT_elements]
    [Upload: GCS]
    [Verify: Upload OK]
    [Compress: PROJECT_atman]
    [Upload: GCS]
    [Verify: Upload OK]
    [Send webhook: Done]

OpenClaw recebe done:
- Você (WhatsApp): "✅ Backup completo: 3 projects, 25GB, GCS"
```

---

## Hostinger + n8n Integration

### Opção A: n8n VPS Template (Novo VPS)

```
Criar segundo VPS:
├─ Template: "Ubuntu 24.04 with n8n"
├─ Size: KVM 2 (8GB RAM suficiente)
├─ Cost: +R$90/mês
├─ Dedicated n8n server
└─ OpenClaw VPS chama via API
```

**Prós:** Isolamento, dedicated resources
**Contras:** Custo dobrado

---

### Opção B: Docker no VPS Atual (Recomendado)

```bash
# No seu VPS (srv1325721)
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v n8n-data:/home/node/.n8n \
  -e WEBHOOK_URL=https://srv1325721.tailead920.ts.net \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=$(openssl rand -hex 16) \
  n8nio/n8n

# Access: https://srv1325721.tailead920.ts.net:5678
```

**Prós:** Um VPS, custo zero adicional
**Contras:** Compartilha RAM com OpenClaw (32GB suficiente)

**Resources:**
- [Hostinger n8n Docker guide](https://www.hostinger.com/tutorials/how-to-self-host-n8n-with-docker)
- [n8n hosting docs](https://docs.n8n.io/hosting/)

---

### Opção C: Hostinger Managed n8n (Mais Fácil)

```
Hostinger n8n Hosting Plan:
├─ Start: $5.99/mo (primeiro mês)
├─ Renew: $9.99/mo
├─ Pre-configured
├─ 1-click install
└─ Suporte incluído
```

**Link:** [Hostinger n8n hosting](https://www.hostinger.com/self-hosted-n8n)

**Prós:** Zero setup
**Contras:** Custo mensal, menos controle

---

## Decision Matrix

| Requirement | OpenClaw Cron | n8n Workflow | Both |
|-------------|---------------|--------------|------|
| Chat-initiated | ✅ | ❌ | ✅ |
| Scheduled (simple) | ✅ | ✅ | Either |
| Scheduled (complex) | ❌ | ✅ | n8n |
| Multi-service | ❌ | ✅ | n8n |
| AI reasoning needed | ✅ | ⚠️ | OpenClaw |
| Team collaboration | ❌ | ✅ | n8n |
| Visual editor | ❌ | ✅ | n8n |
| Natural language | ✅ | ❌ | OpenClaw |
| Strict control | ❌ | ✅ | n8n |
| Cost | FREE | FREE (self-host) | Both FREE |

---

## Casos de Uso Específicos

### Caso 1: Daily Brief (Híbrido)

```
OpenClaw cron (6 AM):
  Message: "Cria meu daily brief"
    ↓
  OpenClaw skill: trigger-n8n-brief
    ↓
n8n workflow "daily-brief":
    [GitHub: Yesterday commits]
    [Google Calendar: Today events]
    [Gmail: Unread important]
    [Weather: Today forecast]
    [AI Node: Summarize all]
    [Format: Markdown]
    [Return: JSON to OpenClaw]
    ↓
OpenClaw recebe:
  Formata bonito
  Envia WhatsApp
```

**Benefício:** OpenClaw scheduling + n8n power + AI summary

---

### Caso 2: Inbox Monitor (OpenClaw Only)

```
OpenClaw cron (hourly):
  Check Gmail
  If urgent (AI decides):
    → Notify WhatsApp
    → Mark as important
  Else:
    → Just log
```

**Benefício:** Simple, todo AI reasoning, sem n8n overhead

---

### Caso 3: Backup Pipeline (n8n Only)

```
n8n cron (daily 3 AM):
  [Compress: /important-files]
  [Upload: GCS primary]
  [Upload: AWS S3 backup]
  [Verify: Both uploads]
  [Cleanup: Local compressed]
  [Log: Success/fail]
  [If fail: Alert admin]
```

**Benefício:** Confiável, sem AI, steps explícitos

---

## Implementação Recomendada (Sua Situação)

**Fase Atual:**
```
✅ OpenClaw funcionando
✅ Ollama ready (pending fix)
✅ WhatsApp connected
✅ Dashboard accessible
```

**Próxima Fase:**
```
1. Fix OpenClaw (15 min)
   → Ollama auth
   → Model priority
   → Verify bot responds

2. Use OpenClaw só (1 semana)
   → Descobre o que precisa
   → Identifica tasks complexas
   → Lista workflows desejados

3. Add n8n (1-2 horas)
   → Docker install
   → Create 2-3 workflows úteis
   → Integrate with OpenClaw

4. Optimize (contínuo)
   → Mais workflows
   → Refine integration
   → Add monitoring
```

---

## Integração Técnica

### OpenClaw → n8n

**Criar skill em OpenClaw:**

```markdown
---
name: trigger-n8n
description: Triggers n8n workflow
---

# trigger-n8n

Triggers an n8n workflow via webhook.

Usage:
/trigger-n8n <workflow-name> [params]

Example:
/trigger-n8n daily-report project=elements

Implementation:
- POST to http://localhost:5678/webhook/<workflow-name>
- Pass params as JSON
- Return result to user
```

**n8n Webhook:**
```
[Webhook Trigger]
    ↓
[Process data]
    ↓
[Return JSON response]
```

---

### n8n → OpenClaw

**n8n HTTP Request Node:**
```json
{
  "method": "POST",
  "url": "http://localhost:18789/api/message/send",
  "headers": {
    "Authorization": "Bearer {{$env.OPENCLAW_TOKEN}}"
  },
  "body": {
    "channel": "whatsapp",
    "to": "+555499628402",
    "message": "Workflow completed: {{$json.result}}"
  }
}
```

---

## Monitoramento

**OpenClaw monitora n8n:**
```bash
# Cron job verifica n8n health
openclaw cron add \
  --name "n8n Health Check" \
  --every "1h" \
  --message "Check if n8n is responding at localhost:5678"
```

**n8n monitora OpenClaw:**
```
n8n workflow "openclaw-health":
  [HTTP: GET localhost:18789/api/health]
  [If down: Alert via WhatsApp]
```

**Ambos se monitoram!**

---

## Custos

### OpenClaw Only
```
VPS: R$165/mo
WhatsApp: R$10-30/mo
APIs (Ollama FREE): $0-10/mo
TOTAL: R$185-210/mo
```

### OpenClaw + n8n (Docker)
```
VPS: R$165/mo (mesmo VPS)
WhatsApp: R$10-30/mo
APIs: $0-10/mo
n8n: $0 (self-hosted Docker)
TOTAL: R$185-210/mo (SEM CUSTO ADICIONAL!)
```

### OpenClaw + n8n (Managed)
```
VPS OpenClaw: R$165/mo
n8n Hosted: $10/mo
WhatsApp: R$10-30/mo
APIs: $0-10/mo
TOTAL: R$235-260/mo (+$10 n8n)
```

**Recomendação:** Docker no mesmo VPS (zero custo adicional)

---

## Instalação n8n (Quando Pronto)

### Via Docker (10 min)

```bash
# 1. On VPS
ssh hostinger

# 2. Install Docker (se não tiver)
curl -fsSL https://get.docker.com | sh

# 3. Run n8n
docker run -d \
  --name n8n \
  --restart unless-stopped \
  -p 5678:5678 \
  -v /root/n8n-data:/home/node/.n8n \
  -e WEBHOOK_URL=https://srv1325721.tailead920.ts.net \
  -e N8N_ENCRYPTION_KEY=$(openssl rand -hex 16) \
  -e N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -hex 16) \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=secure_password_here \
  -e GENERIC_TIMEZONE=America/Sao_Paulo \
  n8nio/n8n:latest

# 4. Access
# Via Tailscale: https://srv1325721.tailead920.ts.net:5678
# Login: admin / secure_password_here

# 5. Create workflow
# [Visual editor opens]
```

---

## Exemplo Completo: Daily Report

### Setup

**OpenClaw Cron (initiator):**
```bash
openclaw cron add \
  --name "Trigger Daily Report" \
  --cron "0 6 * * *" \
  --tz "America/Sao_Paulo" \
  --message "Trigger n8n workflow: daily-report"
```

**n8n Workflow (executor):**
```
Name: daily-report
Trigger: Webhook (/webhook/daily-report)

Nodes:
1. [Webhook] Receive trigger
2. [GitHub] Get commits (last 24h)
3. [Notion] Get completed tasks
4. [Google Calendar] Get today events
5. [HTTP] Weather API
6. [Function] Combine all data
7. [OpenAI] Summarize (use Claude via proxy)
8. [HTTP] Send to OpenClaw
9. End

OpenClaw receives summary:
  Formats as markdown
  Sends via WhatsApp
```

---

## Workflows Úteis (Templates)

### 1. Backup Automation

```
n8n daily 3 AM:
  Compress important dirs
  → Upload GCS
  → Upload S3 (backup)
  → Verify both
  → Cleanup
  → Notify success/fail
```

### 2. Code Review Assistant

```
GitHub webhook (PR opened):
  → Get changed files
  → Send to Claude (via OpenClaw)
  → Generate review comments
  → Post to PR
  → Notify in Slack
```

### 3. Invoice Processing

```
Gmail watch (new invoice):
  → Download PDF
  → OCR (Tesseract)
  → Extract data (AI)
  → Update Google Sheets
  → Create Notion entry
  → Alert if >$1000
```

### 4. Social Media Monitoring

```
Every 1 hour:
  → Twitter search mentions
  → Sentiment analysis (AI)
  → If negative → Alert team
  → If question → Draft response (AI)
  → Save all to database
```

---

## Roadmap de Adoption

### Week 1: OpenClaw Solo
```
- Use via WhatsApp
- Explore skills
- Create 2-3 simple cron jobs
- Learn capabilities
```

### Week 2: Identify n8n Needs
```
- List tasks too complex for OpenClaw
- Design 3-5 workflows on paper
- Decide: Docker ou Managed?
```

### Week 3: Install n8n
```
- Docker setup (10 min)
- Create first workflow (1h)
- Test OpenClaw ↔ n8n integration
```

### Week 4+: Expand
```
- More workflows
- Optimize integration
- Add monitoring
- Team collaboration (se aplicável)
```

---

## Troubleshooting Integration

**OpenClaw can't reach n8n:**
```bash
# Check n8n running
docker ps | grep n8n

# Check port
ss -tlnp | grep 5678

# Test direct
curl http://localhost:5678/webhook/test
```

**n8n can't reach OpenClaw:**
```bash
# Check gateway
systemctl --user status openclaw-gateway

# Test API
curl http://localhost:18789/api/health
```

**Both running but not connecting:**
```
- Check firewall (both on localhost = should work)
- Verify webhook URLs
- Check auth tokens
- Review logs (openclaw + docker logs n8n)
```

---

## Decisão Final

**Para você:**

```
AGORA:
├─ OpenClaw funcionando (pending fixes)
├─ Skills nativas (14)
├─ Seus custom tools (30)
└─ Automation básica via OpenClaw cron

DEPOIS (quando OpenClaw estável):
├─ Add n8n (Docker, 10 min)
├─ Create 3-5 workflows essenciais
├─ Integrate OpenClaw ↔ n8n
└─ Sistema completo de automação

NÃO AGORA:
├─ n8n antes OpenClaw funcionar
├─ Workflows antes saber o que precisa
└─ Complexidade sem necessidade
```

---

**SUMMARY:**

- **OpenClaw:** Agent conversational (você tem)
- **n8n:** Workflow orchestrator (você vai adicionar)
- **Juntos:** Sistema completo
- **Separados:** Cada um tem valor
- **Hostinger:** Suporta ambos

**Implementa:** OpenClaw primeiro, n8n depois

**Sources:**
- [Hostinger n8n template](https://www.hostinger.com/support/10473267-how-to-use-the-n8n-vps-template-at-hostinger/)
- [n8n Docker self-host](https://www.hostinger.com/tutorials/how-to-self-host-n8n-with-docker)
- [OpenClaw vs n8n comparison](https://sourceforge.net/software/compare/OpenClaw-vs-n8n/)

---

**Last Updated:** 2026-02-04 01:45 UTC
**Status:** Manual completo - referência para futuro
**Next:** Fix OpenClaw, use 1 semana, depois add n8n
