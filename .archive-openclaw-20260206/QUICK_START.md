# OpenClaw VPS - Guia Rápido

**Como usar seu OpenClaw no dia-a-dia.**

---

## 🚀 Acesso Básico

### Conectar ao VPS
```bash
ssh rainmaker
# ou
ssh hostinger
```

### Ver se está rodando
```bash
openclaw health
```

**Saída esperada:**
```
WhatsApp: linked (auth age Xm)
Web Channel: +555496816430
Agents: main (default)
```

---

## 💬 Usar via WhatsApp

### Seu Número
+555499628402 (único autorizado)

### Número do Bot
+555496816430

### Testar
1. Abra WhatsApp no celular
2. Envie mensagem para +555496816430
3. Digite: "oi"
4. Aguarde resposta automática

### Comandos no WhatsApp
```
# Perguntar algo
"Qual o clima em São Paulo?"

# Gerar imagem
"Gere uma imagem de um gato astronauta"

# Usar skill
"@github list my repos"

# Buscar na web
"Pesquise sobre Rust async"
```

---

## 🖥️ Comandos Úteis (SSH)

### Ver Logs em Tempo Real
```bash
ssh rainmaker "tail -f /tmp/openclaw/openclaw-\$(date +%Y-%m-%d).log"
```

### Ver Status do Gateway
```bash
ssh rainmaker "openclaw gateway status"
```

### Reiniciar Gateway
```bash
ssh rainmaker "openclaw gateway restart"
```

### Ver Skills Instaladas
```bash
ssh rainmaker "openclaw skills list"
```

### Instalar Nova Skill
```bash
ssh rainmaker "openclaw skills install slack"
# Outros: notion, github, tmux, weather, video-frames
```

### Ver Configuração
```bash
ssh rainmaker "cat /root/.openclaw/openclaw.json | jq '.agents.defaults.model'"
```

---

## 🔧 Troubleshooting Rápido

### WhatsApp não responde?

**1. Verificar se gateway está rodando:**
```bash
ssh rainmaker "systemctl --user status openclaw-gateway"
```

**Esperado:** `Active: active (running)`

**2. Se parado, reiniciar:**
```bash
ssh rainmaker "systemctl --user start openclaw-gateway"
```

**3. Verificar logs:**
```bash
ssh rainmaker "tail -50 /tmp/openclaw/openclaw-\$(date +%Y-%m-%d).log"
```

### SSH não conecta?

**1. Verificar se VPS está rodando:**
```bash
ping 82.25.77.221
```

**2. Verificar firewall:**
```bash
ssh rainmaker "ufw status"
```

**Deve mostrar:** `22/tcp ALLOW`

**3. VPS pode ter reiniciado, aguardar 2-3 minutos**

### "No API key found" errors?

**Normal!** Sistema usa fallback chain.
Se WhatsApp responde = tudo OK.

Modelos tentam:
1. MiniMax (primary)
2. ZAI GLM
3. Bedrock Claude
4. ... (27 fallbacks)

Um deles sempre funciona.

---

## 📦 Skills Recomendadas

### Já Instaladas ✅
- `bird` - Twitter/X
- `github` - GitHub CLI
- `coding-agent` - Run Claude Code remotamente!
- `notion` - Notion API
- `tmux` - Control tmux remotely
- `weather` - Previsão do tempo
- `video-frames` - Extrair frames de vídeo

### Para Instalar 🎯

**Produtividade:**
```bash
openclaw skills install slack
openclaw skills install trello
openclaw skills install obsidian
```

**Mídia:**
```bash
openclaw skills install spotify-player
openclaw skills install summarize  # YouTube transcription
```

**Casa:**
```bash
openclaw skills install openhue    # Philips Hue
openclaw skills install sonoscli   # Sonos speakers
```

---

## 🎨 Casos de Uso

### 1. Assistente Pessoal via WhatsApp
```
Você: "Me lembre de comprar leite amanhã às 10h"
Bot: [usa apple-reminders skill]

Você: "Qual minha agenda para hoje?"
Bot: [usa calendar skill se instalado]
```

### 2. Code Review Remoto
```bash
# No Mac, commit code
git commit -m "Add feature X"

# WhatsApp
Você: "@github create pr for feature-x"
Bot: [cria PR usando gh CLI]
```

### 3. Media Control
```bash
# Instalar skills primeiro
ssh rainmaker "openclaw skills install spotify-player"
ssh rainmaker "openclaw skills install sonoscli"

# WhatsApp
Você: "Tocar jazz no Sonos"
Bot: [controla Sonos]
```

### 4. Monitoring
```bash
# WhatsApp
Você: "Status do VPS"
Bot: [executa openclaw health + system stats]
```

---

## 🔐 Segurança

### Números Autorizados
Apenas `+555499628402` (seu número) pode usar o bot.

Para adicionar outro número:
```bash
ssh rainmaker
nano /root/.openclaw/openclaw.json

# Editar:
"allowFrom": ["+555499628402", "+5511999999999"]

# Salvar e reiniciar
openclaw gateway restart
```

### Token do Dashboard
```
Token: 16977b348d8f1a139cf9d63eb5613ff459c7266b0712535f
```

**Não compartilhar!**

### Acesso Remoto ao Dashboard
Dashboard está em `localhost:18789` (não acessível da internet).

**Para acessar:**
1. Use Tailscale (já configurado no VPS)
2. Ou SSH tunnel:
```bash
ssh -L 18789:localhost:18789 rainmaker
# Depois abrir: http://localhost:18789
```

---

## 💾 Backup

### Última Backup
- **Data:** 2026-02-04
- **Local:** `~/backup/`
- **Arquivos:**
  - `openclaw-workspace-COMPLETE-20260204-020801.tar.gz`
  - `whatsapp-session-backup.tar.gz`

### Fazer Novo Backup
```bash
# Workspace
ssh rainmaker "tar czf /tmp/openclaw-workspace-\$(date +%Y%m%d).tar.gz /root/.openclaw/workspace"
scp rainmaker:/tmp/openclaw-workspace-*.tar.gz ~/backup/

# WhatsApp credentials
ssh rainmaker "tar czf /tmp/whatsapp-backup-\$(date +%Y%m%d).tar.gz /root/.openclaw/credentials"
scp rainmaker:/tmp/whatsapp-backup-*.tar.gz ~/backup/
```

### Restaurar (se necessário)
```bash
# Copiar para VPS
scp ~/backup/openclaw-workspace-*.tar.gz rainmaker:/tmp/

# Extrair
ssh rainmaker "tar xzf /tmp/openclaw-workspace-*.tar.gz -C /"
ssh rainmaker "openclaw gateway restart"
```

---

## 📊 Monitoramento

### Dashboards Disponíveis

**Grafana:** http://82.25.77.221:3000
**Portainer:** http://82.25.77.221:9000
**Authelia:** http://82.25.77.221:9091

**Nota:** Podem estar protegidos por firewall, use Tailscale.

### Ver Uso de Recursos
```bash
ssh rainmaker "htop"
# ou
ssh rainmaker "docker stats"
```

---

## 🆘 Suporte

### Logs
```bash
# Hoje
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# Ontem
tail -f /tmp/openclaw/openclaw-$(date -d yesterday +%Y-%m-%d).log
```

### Documentação Oficial
- https://docs.openclaw.ai
- https://clawhub.com

### Estado Real do VPS
Arquivo: `OPENCLAW_VPS_REALIDADE_2026-02-06.md` (mesma pasta)

---

## 🎯 Próximos Passos

1. **Testar WhatsApp** - Enviar "oi" e receber resposta
2. **Instalar skills** - Escolher 2-3 do seu interesse
3. **Configurar backup automático** - Cron job semanal
4. **Explorar skills marketplace** - https://clawhub.com
5. **Criar custom skill** - Use `skill-creator` skill

---

**Dica:** OpenClaw é uma plataforma, não só chatbot. Pense em automações que você quer e procure skills no ClawHub!

Última atualização: 2026-02-06
