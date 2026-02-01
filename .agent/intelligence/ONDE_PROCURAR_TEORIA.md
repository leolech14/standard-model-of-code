# Onde Procurar Teorias - Haikus de Localização
**Data:** 2026-01-27
**Método:** Memória de trabalho + conhecimento de estrutura

---

## OS 7 TEMPLOS DA TEORIA

### 1. 🏛️ O Templo Axiomático
```
particle/docs/theory/
├── THEORY_INDEX.md          ← COMEÇA AQUI (mapa de tudo)
├── L0_AXIOMS.md             ← 50+ axiomas formais
├── THEORY_AXIOMS.md         ← Validação Gemini (grupos A-H)
├── L2_LAWS.md               ← Leis dinâmicas
└── PROJECTOME_THEORY.md     ← Álgebra P = C ⊔ X
```
**Densidade:** MUITO ALTA (~100 teorias formais)
**Natureza:** Axiomas, provas matemáticas, fundamentação

---

### 2. 📚 A Biblioteca de Contexto
```
wave/docs/
├── deep/
│   ├── THEORY_AMENDMENT_2026-01.md    ← A1:Tools, A2:Dark Matter, A3:Confidence
│   ├── ONTOLOGICAL_FOUNDATIONS.md     ← Semiotics, Category Theory
│   ├── PURPOSE_EMERGENCE.md           ← Teleologia
│   └── BACKGROUND_AI_LAYER_MAP.md     ← BARE, AEP, HSL
├── theory/
│   ├── THEORY.md                      ← 171KB! Dump teórico massivo
│   ├── FOUNDATIONS_INTEGRATION.md     ← Proofs acadêmicas
│   └── FOUNDATIONAL_THEORIES.md       ← Koestler, Popper, Friston
└── GLOSSARY.md                        ← 400+ definições
```
**Densidade:** ALTA (~60 teorias + 400 termos)
**Natureza:** Extensões, aplicações, vocabulário

---

### 3. 🧪 O Laboratório da Sessão
```
.agent/intelligence/comm_analysis/
├── ONTOLOGIA_SISTEMAS_FLUXO.md        ← INTEGRAÇÃO COMPLETA (hoje)
├── MATEMATICA_DECOMPOSICAO.md         ← E(S|Φ) formalizado
├── ENERGIA_CONTEXTUAL.md              ← w(Φ) adaptativos
├── ARQUITETURA_UNIVERSAL.md           ← Framework universal
├── ENSAIO_DECOMPOSICAO_SUBSISTEMAS.md ← Estado relaxado
├── COMMUNICATION_FABRIC_RESEARCH_SYNTHESIS.md ← Fabric theory
├── PALACE_OF_BUTLERS.md               ← Multi-generational
└── [12 outros documentos desta sessão]
```
**Densidade:** MUITO ALTA (~50 teorias novas)
**Natureza:** Descobertas originais, integrações, sínteses

---

### 4. 🔬 O Arquivo de Pesquisa
```
particle/docs/research/
├── gemini/
│   ├── sessions/     243 JSON  ← Conversas completas
│   └── docs/         246 MD    ← Research reports
└── perplexity/
    ├── docs/         148 MD    ← Academic research (60+ fontes cada)
    └── raw/          144 JSON  ← Raw responses
```
**Densidade:** MASSIVA (1,068 arquivos)
**Natureza:** Validações externas, grounding acadêmico
**Atenção:** Cada Perplexity doc cita 20-60 teorias externas!

---

### 5. 📋 As Especificações Técnicas
```
particle/docs/specs/
├── VISUALIZATION_UI_SPEC.md           ← UI theory
├── TREE_SITTER_INTEGRATION_SPEC.md    ← Parser theory
├── CODOME_LANDSCAPE.md                ← Landscape theory
├── SEMANTIC_INDEXER_IMPLEMENTATION.md ← Indexing theory
└── [30+ outros specs]
```
**Densidade:** MÉDIA (~30 specs técnicos)
**Natureza:** Aplicações, implementações, protocolos

---

### 6. 🗂️ Os Registros Canônicos
```
particle/schema/fixed/
├── atoms.json           ← 3,525 atoms definidos
├── roles.json           ← 33 roles canônicos
├── dimensions.json      ← 8 dimensões
└── [outros schemas]

.agent/intelligence/
├── LOL.yaml             ← 2,469 entities
├── LOL_FORMAL_DEFINITION.md  ← Matemática do LOL
└── subsystem registries
```
**Densidade:** ESTRUTURADA (definições precisas)
**Natureza:** Enumerações completas, schemas

---

### 7. 🌊 O Oceano de Referências
```
wave/docs/theory/references/
├── md/          ← 150+ papers em markdown
│   ├── PEIRCE_*.md
│   ├── FRISTON_*.md
│   ├── KOESTLER_*.md
│   └── [147+ outros]
├── txt/         ← Textos completos (7.9MB PEIRCE alone!)
└── metadata/    ← JSON metadata
```
**Densidade:** OCEANICA (150+ teorias externas completas)
**Natureza:** Fundamentação acadêmica

---

## ESTRATÉGIA DE PROCURA (Priorizada)

### Fase 1: Núcleo Formal (1 hora)
1. `particle/docs/theory/THEORY_INDEX.md` - LER PRIMEIRO
2. `L0_AXIOMS.md` - Extrair todos os axiomas A-H
3. `THEORY_AXIOMS.md` - Validação + grupos
4. `.agent/intelligence/ONTOLOGIA_SISTEMAS_FLUXO.md` - Integração completa

**Output:** ~150 teorias formais

### Fase 2: Extensões (2 horas)
5. `wave/docs/deep/THEORY_AMENDMENT_2026-01.md`
6. `wave/docs/theory/THEORY.md` (171KB - ler seções principais)
7. `.agent/intelligence/comm_analysis/*.md` (15 arquivos desta sessão)

**Output:** +60 teorias

### Fase 3: Especializações (1 hora)
8. Scan `particle/docs/specs/*.md` (30+ specs)
9. Scan `.agent/specs/*.md` (automação, dashboard)
10. Schemas `*.json` (atoms, roles, dimensions)

**Output:** +40 frameworks

### Fase 4: Research (opcional - 2 horas)
11. Sample 20 Perplexity docs (de 148 total)
12. Extract citações principais
13. Mapear teorias externas únicas

**Output:** +50 teorias externas

---

## MÉTODO DE EXTRAÇÃO (Por Tipo)

### Axiomas
**Buscar:**
```bash
grep -r "^###.*Axiom [A-H][0-9]" particle/docs/theory/
grep -r "^\*\*Axiom" .agent/intelligence/
```

### Teoremas
```bash
grep -r "^### Theorem" particle/docs/theory/
grep -r "^### T[0-9]" .agent/intelligence/
```

### Leis
```bash
grep -r "Law" particle/docs/theory/*.md | grep "^###"
grep -r "Lei Construtal\|Law" .agent/intelligence/*.md
```

### Frameworks
```bash
grep -r "Framework" particle/docs/ wave/docs/
grep -r "^## .*Theory$" **/*.md
```

---

## RESULTADO ESPERADO

**Se executarmos catalogação completa (6 horas):**

- **Teorias formais:** ~150 (axiomas, teoremas, leis)
- **Frameworks/padrões:** ~80 (aplicações)
- **Definições/termos:** ~400 (glossário)
- **Referências externas:** ~150 (papers integrados)
- **TOTAL:** ~780 entradas teóricas únicas

**Mas com cross-references e derivações:**
- **Teorias únicas:** ~300
- **Citações/aplicações:** ~480
- **TOTAL integrado:** ~780 nodes no grafo teórico

---

## HAIKUS DE ORIENTAÇÃO

```
Theory lives in three:
Standard Model (bedrock deep)
Comm Analysis (new growth)
References (vast ocean)

Start at INDEX.md
Follow L0 to L3 layers down
Then dive comm_analysis

Each .md file a world
Each axiom births theorems
Graph grows recursive
```

---

**PRÓXIMO:** Executar scan automatizado com teoria_cataloger.py melhorado OU catalogação manual via estes haikus?
