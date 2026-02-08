#!/bin/bash
# OpenClaw Documentation Consolidation Script
# Executa o plano de limpeza automaticamente

set -e  # Exit on error

BASE_DIR="$HOME/PROJECTS_all/PROJECT_elements/openclaw-implementation"
cd "$BASE_DIR"

echo "========================================="
echo "OpenClaw Documentation Consolidation"
echo "========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função de confirmação
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Backup de segurança primeiro
echo -e "${YELLOW}[1/7] Criando backup de segurança...${NC}"
BACKUP_DIR="$BASE_DIR/.backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r archive docs scripts "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Backup criado em: $BACKUP_DIR${NC}"
echo ""

# Criar estrutura de diretórios
echo -e "${YELLOW}[2/7] Criando estrutura de diretórios...${NC}"
mkdir -p archive/2026-02-04
mkdir -p archive/research
mkdir -p reference
mkdir -p scripts
echo -e "${GREEN}✓ Estrutura criada${NC}"
echo ""

# Mover docs antigas para archive
echo -e "${YELLOW}[3/7] Movendo documentação antiga para archive...${NC}"
if [ -f "archive/OPENCLAW_NATIVE_FEATURES.md" ]; then
    mv archive/OPENCLAW_NATIVE_FEATURES.md archive/research/ 2>/dev/null || true
    echo "  → OPENCLAW_NATIVE_FEATURES.md"
fi
if [ -f "archive/N8N_VS_OPENCLAW.md" ]; then
    mv archive/N8N_VS_OPENCLAW.md archive/research/ 2>/dev/null || true
    echo "  → N8N_VS_OPENCLAW.md"
fi
if [ -f "archive/OPENCLAW_ARCHITECTURE.md" ]; then
    mv archive/OPENCLAW_ARCHITECTURE.md archive/research/ 2>/dev/null || true
    echo "  → OPENCLAW_ARCHITECTURE.md"
fi
if [ -f "docs/OPENCLAW_CRITICAL_AUDIT_20260204.md" ]; then
    mv docs/OPENCLAW_CRITICAL_AUDIT_20260204.md archive/2026-02-04/ 2>/dev/null || true
    echo "  → OPENCLAW_CRITICAL_AUDIT_20260204.md"
fi
if [ -f "docs/COMO_USAR_OPENCLAW.md" ]; then
    mv docs/COMO_USAR_OPENCLAW.md archive/2026-02-04/ 2>/dev/null || true
    echo "  → COMO_USAR_OPENCLAW.md"
fi
if [ -f "docs/OPENCLAW_INSTALL_PIPELINE.md" ]; then
    mv docs/OPENCLAW_INSTALL_PIPELINE.md archive/2026-02-04/ 2>/dev/null || true
    echo "  → OPENCLAW_INSTALL_PIPELINE.md"
fi
echo -e "${GREEN}✓ Docs antigas arquivadas${NC}"
echo ""

# Limpar ~/.claude
echo -e "${YELLOW}[4/7] Limpando ~/.claude...${NC}"
if [ -f "$HOME/.claude/openclaw-native-features-catalog.md" ]; then
    mv "$HOME/.claude/openclaw-native-features-catalog.md" reference/ 2>/dev/null || true
    echo "  → openclaw-native-features-catalog.md movido para reference/"
fi
if [ -f "$HOME/.claude/openclaw-implementation-study.md" ]; then
    if confirm "  Deletar ~/.claude/openclaw-implementation-study.md? (coberto pela REALIDADE)"; then
        rm "$HOME/.claude/openclaw-implementation-study.md"
        echo -e "${GREEN}  ✓ Deletado${NC}"
    else
        echo -e "${YELLOW}  ⊘ Mantido${NC}"
    fi
fi
echo ""

# Revisar wave/tools/ai/openclaw-implementation
echo -e "${YELLOW}[5/7] Revisando wave/tools/ai/openclaw-implementation...${NC}"
WAVE_OPENCLAW="$HOME/PROJECTS_all/PROJECT_elements/wave/tools/ai/openclaw-implementation"
if [ -f "$WAVE_OPENCLAW/openclaw.json" ]; then
    echo "  Comparando openclaw.json com VPS..."
    if ssh rainmaker "cat /root/.openclaw/openclaw.json" > /tmp/vps-openclaw.json 2>/dev/null; then
        if diff -q "$WAVE_OPENCLAW/openclaw.json" /tmp/vps-openclaw.json > /dev/null 2>&1; then
            echo -e "  ${YELLOW}→ Arquivos são IDÊNTICOS${NC}"
            if confirm "  Deletar wave/tools/ai/openclaw-implementation/openclaw.json?"; then
                rm "$WAVE_OPENCLAW/openclaw.json"
                echo -e "${GREEN}  ✓ Deletado${NC}"
            fi
        else
            echo -e "  ${YELLOW}→ Arquivos são DIFERENTES, mantendo ambos${NC}"
            echo "  Dica: revisar manualmente"
        fi
        rm /tmp/vps-openclaw.json
    else
        echo -e "  ${RED}⚠ Não foi possível conectar ao VPS para comparar${NC}"
    fi
fi
echo ""

# Criar README.md
echo -e "${YELLOW}[6/7] Criando README.md...${NC}"
cat > README.md << 'EOF'
# OpenClaw VPS Implementation

**Configuração e documentação do OpenClaw rodando em Hostinger VPS.**

---

## 📚 Documentação

| Arquivo | Propósito |
|---------|-----------|
| **[OPENCLAW_VPS_REALIDADE_2026-02-06.md](OPENCLAW_VPS_REALIDADE_2026-02-06.md)** | ⭐ **FONTE DA VERDADE** - Estado real do VPS |
| [QUICK_START.md](QUICK_START.md) | 🚀 Guia rápido de uso diário |
| [CLEANUP_PLAN.md](CLEANUP_PLAN.md) | 🧹 Plano de consolidação executado |

---

## 🎯 Começar Aqui

1. **Ver estado atual:** `OPENCLAW_VPS_REALIDADE_2026-02-06.md`
2. **Usar no dia-a-dia:** `QUICK_START.md`
3. **Problemas?** Ver seção Troubleshooting no QUICK_START.md

---

## 📂 Estrutura

```
openclaw-implementation/
├── OPENCLAW_VPS_REALIDADE_2026-02-06.md  ← VERDADE
├── QUICK_START.md                         ← Como usar
├── CLEANUP_PLAN.md                        ← Plano executado
├── README.md                              ← Este arquivo
│
├── reference/                             ← Recursos úteis
│   └── openclaw-native-features-catalog.md
│
├── archive/                               ← Histórico (read-only)
│   ├── 2026-02-04/                       ← Docs antigas
│   └── research/                          ← Research papers
│
└── scripts/                               ← Automação
    ├── consolidate.sh                     ← Script de consolidação
    └── backup-openclaw.sh                 ← (futuro)
```

---

## ⚙️ VPS Info

- **IP:** 82.25.77.221
- **SSH:** `ssh rainmaker` ou `ssh hostinger`
- **WhatsApp Bot:** +555496816430
- **Versão:** OpenClaw 2026.2.2-3
- **Provider:** Hostinger KVM 8

---

## 🔗 Links

- [OpenClaw Docs](https://docs.openclaw.ai)
- [ClawHub Skills](https://clawhub.com)
- [GitHub](https://github.com/OpenClaw/OpenClaw)

---

**Última atualização:** 2026-02-06
**Status:** ✅ Sistema funcional, WhatsApp ativo
EOF
echo -e "${GREEN}✓ README.md criado${NC}"
echo ""

# Resumo final
echo -e "${YELLOW}[7/7] Resumo da consolidação:${NC}"
echo ""
echo "✅ Estrutura criada:"
echo "   - archive/2026-02-04/"
echo "   - archive/research/"
echo "   - reference/"
echo "   - scripts/"
echo ""
echo "📦 Backup de segurança:"
echo "   $BACKUP_DIR"
echo ""
echo "📄 Documentos principais:"
echo "   1. OPENCLAW_VPS_REALIDADE_2026-02-06.md (VERDADE)"
echo "   2. QUICK_START.md (Guia rápido)"
echo "   3. CLEANUP_PLAN.md (Plano executado)"
echo "   4. README.md (Índice)"
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Consolidação concluída com sucesso!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Próximos passos recomendados:"
echo "1. Ler OPENCLAW_VPS_REALIDADE_2026-02-06.md"
echo "2. Testar com: ssh rainmaker 'openclaw health'"
echo "3. Enviar mensagem WhatsApp para +555496816430"
echo ""
