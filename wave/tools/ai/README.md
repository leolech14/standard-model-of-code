# OpenClaw Documentation Index

**Status:** Documentação limpa e organizada em 2026-02-03

---

## 📖 DOCUMENTOS ATIVOS (LEIA ESTES)

### 0. **LESSONS_LEARNED.md** 🎓 ← **LEIA PRIMEIRO!**
   - **Para:** Você (Leo) antes de QUALQUER projeto novo
   - **O que é:** Por que falhamos (central-mcp) e como consertar
   - **Quando usar:** Antes de construir algo do zero
   - **Impacto:** Economiza 80-100 horas por projeto

### 1. **CLAUDE_OPENCLAW_HANDBOOK.md** 🤖 ← **PARA MIM (CLAUDE)**
   - **Para:** Claude agents trabalhando com OpenClaw
   - **O que é:** Tudo que Claude precisa saber
   - **Quando usar:** Configurar, debugar, ou colaborar com Rainmaker

### 2. **START_HERE.md** 🚀
   - **Para:** Primeiro dia (humano)
   - **O que é:** Guia minimalista (só o essencial)
   - **Quando usar:** Você instalou e quer começar AGORA

### 3. **COMO_USAR_OPENCLAW.md** 📚
   - **Para:** Uso diário (humano)
   - **O que é:** Guia prático completo
   - **Quando usar:** Precisa fazer algo específico (cron, skills, troubleshoot)

### 4. **ARQUITETURA_REAL.md** 🏗️
   - **Para:** Entender o sistema
   - **O que é:** Documento autoritativo do que está rodando
   - **Quando usar:** Quer saber exatamente o que tem no VPS

### 5. **CEREBRAS_TOOLS.md** ⚡
   - **Para:** Usar Cerebras API
   - **O que é:** Ferramentas específicas do Cerebras
   - **Quando usar:** Desenvolvimento com Cerebras

---

## 📦 ARQUIVOS ARQUIVADOS (_archive/)

**ATENÇÃO:** Estes docs são planejamento histórico, NÃO realidade atual!

| Arquivo | O que era | Por que arquivado |
|---------|-----------|-------------------|
| **N8N_VS_OPENCLAW.md** | Explicação n8n vs OpenClaw | n8n não foi implementado (OpenClaw já faz tudo) |
| **OPENCLAW_ARCHITECTURE.md** | Arquitetura 3-tier com n8n | Desatualizado (n8n não existe) |
| **EVOLUTION_AND_MAPPING.md** | Mapeamento de evolução | Planejamento antigo |
| **LEVERAGE_EXISTING_SUBSCRIPTIONS.md** | Estratégia de subscriptions | Referência |

**Use _archive/ para:**
- ✅ Entender decisões históricas
- ✅ Ver por que n8n foi descartado
- ✅ Referência de design original

**NÃO use _archive/ para:**
- ❌ Entender o que está rodando agora
- ❌ Seguir como guia de implementação

---

## 🗂️ ESTRUTURA DO DIRETÓRIO

```
wave/tools/ai/
├── README.md                         ← VOCÊ ESTÁ AQUI
│
├── 📖 DOCS ATIVOS (use estes)
│   ├── LESSONS_LEARNED.md            → 🎓 META-LIÇÃO (read first!)
│   ├── CLAUDE_OPENCLAW_HANDBOOK.md   → Para Claude agents 🤖
│   ├── START_HERE.md                 → Primeiro dia (humano)
│   ├── COMO_USAR_OPENCLAW.md         → Guia prático (humano)
│   ├── ARQUITETURA_REAL.md           → O que está rodando
│   └── CEREBRAS_TOOLS.md             → Ferramentas Cerebras
│
├── 📦 _archive/ (referência histórica)
│   ├── N8N_VS_OPENCLAW.md
│   ├── OPENCLAW_ARCHITECTURE.md
│   ├── EVOLUTION_AND_MAPPING.md
│   ├── LEVERAGE_EXISTING_SUBSCRIPTIONS.md
│   └── OPENCLAW_NATIVE_FEATURES.md
│
└── 🔧 SCRIPTS (tools Python/Bash)
    ├── analyze.py                 → Análise com Gemini
    ├── cerebras_*.py              → Ferramentas Cerebras
    ├── perplexity_research.py     → Pesquisa Perplexity
    └── ... (outros scripts)
```

---

## 🎯 QUICK START

### Se é seu primeiro dia:
```bash
1. Ler: START_HERE.md (5 minutos)
2. Testar: Mandar msg WhatsApp pro bot
3. Explorar: Dashboard web UI
```

### Se precisa fazer algo específico:
```bash
1. Consultar: COMO_USAR_OPENCLAW.md
2. Seção específica: Ctrl+F [sua dúvida]
3. Executar comando
```

### Se quer entender a arquitetura:
```bash
1. Ler: ARQUITETURA_REAL.md
2. Ver: Diagramas e componentes
3. Comparar com _archive/ (o que era vs o que é)
```

---

## 🔍 DECISÕES DE DESIGN

### Por que n8n não foi implementado?

**Planejado:**
- n8n para workflows
- n8n para cron jobs
- n8n para integrações

**Realidade:**
- OpenClaw já tem cron jobs nativo ✅
- OpenClaw já tem webhooks ✅
- OpenClaw skills fazem integrações ✅

**Conclusão:** n8n seria duplicação desnecessária.

**Docs sobre isso:**
- `_archive/N8N_VS_OPENCLAW.md` - Explicação completa
- `ARQUITETURA_REAL.md` - O que está rodando sem n8n

---

## 📊 MAPA MENTAL

```
OpenClaw Implementation
│
├─ 🎯 OBJETIVO
│  └─ AI assistant pessoal via WhatsApp
│
├─ 🏗️ COMPONENTES
│  ├─ OpenClaw Gateway (core)
│  ├─ Ollama (models locais FREE)
│  ├─ Doppler (secrets)
│  └─ WhatsApp (interface)
│
├─ ❌ NÃO IMPLEMENTADO
│  ├─ n8n (desnecessário)
│  ├─ Sync bridge (não prioritário)
│  └─ Multiple agents (um basta)
│
└─ 📚 DOCS
   ├─ Ativos (use)
   │  ├─ START_HERE.md
   │  ├─ COMO_USAR_OPENCLAW.md
   │  └─ ARQUITETURA_REAL.md
   │
   └─ Arquivados (referência)
      └─ _archive/*.md
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

### Qual doc ler?

| Problema | Doc | Seção |
|----------|-----|-------|
| Bot não responde | COMO_USAR_OPENCLAW.md | § 5 Troubleshooting |
| Dashboard não abre | START_HERE.md | § Se algo quebrar |
| Criar cron job | COMO_USAR_OPENCLAW.md | § 3 Comandos CLI |
| Entender arquitetura | ARQUITETURA_REAL.md | Todo o doc |
| Por que não tem n8n? | _archive/N8N_VS_OPENCLAW.md | Todo o doc |

---

## ✅ CHECKLIST DE QUALIDADE DOS DOCS

- [x] Sem duplicação (um tópico = um lugar)
- [x] Arquivados claramente separados
- [x] START_HERE minimalista (<60 linhas)
- [x] COMO_USAR prático (copy-paste ready)
- [x] ARQUITETURA autoritativa (único source of truth)
- [x] _archive preservado (referência histórica)
- [x] n8n referências removidas dos docs ativos
- [x] README índice mestre criado

---

## 🔄 MANUTENÇÃO

### Quando atualizar docs:

**START_HERE.md:**
- Mudou algo essencial do primeiro dia

**COMO_USAR_OPENCLAW.md:**
- Novo comando útil descoberto
- Nova skill instalada frequentemente usada
- Troubleshooting comum não documentado

**ARQUITETURA_REAL.md:**
- Componente novo adicionado
- Decisão arquitetural mudou
- Custos mudaram significativamente

**_archive/:**
- Nunca! (é referência histórica)

---

## 📞 SUPORTE

**Tem dúvida?**
1. Procurar no doc apropriado (use índice acima)
2. Perguntar pro Rainmaker (via WhatsApp!)
3. Consultar _archive/ (design decisions)

**Doc está errado?**
- Atualizar e commitar
- Manter este README.md atualizado

---

**Última atualização:** 2026-02-03 23:50 BRT
**Mantido por:** Claude Code

**Este README é o mapa da documentação. Mantenha-o atualizado!**
