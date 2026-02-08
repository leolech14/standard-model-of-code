# 🦞 OpenClaw - START HERE

**Primeiro dia? Leia SÓ isto.**

---

## O QUE VOCÊ TEM

```
Bot WhatsApp: +55 54 99681-6430
Seu número: +5554999628402 (allowlist)
Dashboard: http://localhost:18789/?token=51c8c...
VPS: ssh hostinger
```

**Funcionando:**
- ✅ WhatsApp bot (manda msg, recebe resposta)
- ✅ Sonnet 4.5 1M (sua Max subscription)
- ✅ Dashboard (web interface)
- ✅ FREE fallback (Ollama)

---

## COMO USAR

**Via WhatsApp:**
```
Manda mensagem para: +55 54 99681-6430
Bot responde automaticamente
```

**Via Dashboard:**
```
1. ssh -f -N -L 18789:127.0.0.1:18789 hostinger
2. Abrir: http://localhost:18789/?token=51c8c0d43559c28bc7b5d79088bc788192dd617dcd5d5c2167d47d21b0eaa984
3. Chat direto com AI
```

---

## SE ALGO QUEBRAR

**Bot não responde:**
```bash
ssh hostinger "systemctl --user restart openclaw-gateway"
```

**Dashboard não abre:**
```bash
ssh -f -N -L 18789:127.0.0.1:18789 hostinger
```

**Ver o que está acontecendo:**
```bash
ssh hostinger "cd /root/openclaw && pnpm openclaw status"
```

---

## ONDE ESTÁ TUDO

```
Configs: /root/.openclaw/openclaw.json (VPS)
API Keys: Doppler (doppler secrets list)
Docs: ~/PROJECTS_all/PROJECT_elements/wave/tools/ai/
Dashboard: localhost:18789 (via tunnel)
```

---

## CUSTOS

```
VPS: R$165/mês
WhatsApp: R$10-30/mês
API: $0 (usando Max subscription)
TOTAL: ~R$185/mês
```

---

## PRÓXIMOS PASSOS

**Hoje:** USE o bot via WhatsApp alguns dias

**Depois:**
- Criar cron jobs úteis (OpenClaw já faz scheduling!)
- Instalar skills do ClawHub
- Configurar sync Mac↔VPS
- Mais customização

**NÃO build more antes de usar!**

---

## EMERGÊNCIA - PARAR TUDO

```bash
# Desligar bot
ssh hostinger "systemctl --user stop openclaw-gateway"

# Desligar VPS
# Via painel Hostinger
```

---

**SÓ ISSO QUE VOCÊ PRECISA SABER.**

**Outros 5 .md files:** Referência avançada (ignore por agora)

**Este arquivo:** Sua única fonte de verdade inicial

---

**TESTE AGORA:** Manda "Oi" pro bot no WhatsApp!
