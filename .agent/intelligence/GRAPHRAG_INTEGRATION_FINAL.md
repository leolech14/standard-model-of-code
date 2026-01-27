# GraphRAG Integration Final + Arquivamento
**Data:** 2026-01-27
**Objetivo:** Finalizar Collider→GraphRAG + Arquivar código substituído

---

## I. O QUE GRAPHRAG SUBSTITUI

### ANTES (Text Search)

**Arquivo:** `context-management/tools/refinery/query_chunks.py`
**Método:** Brute-force text matching
```python
for chunk in all_chunks:
    if query.lower() in chunk['content'].lower():
        results.append(chunk)
```
**Limitações:**
- Não entende semântica (busca literal)
- Não conecta code → theory
- Não valida contra research
- O(n) complexity (slow em escala)

**Status:** MANTER para fallback, mas marcar como LEGACY

---

### DEPOIS (GraphRAG)

**Arquivos novos:**
- `.agent/tools/collider_to_neo4j.py` (import code graph)
- `.agent/tools/import_academic_foundations.py` (import papers)
- `.agent/tools/graphrag_query.py` (query interface - criar)

**Método:** Graph traversal + semantic embeddings
```python
# Find concept
concept = graph.find_concept(query)
# Traverse relationships
code = graph.traverse(concept → IMPLEMENTED_BY → CodeEntity)
theory = graph.traverse(concept → VALIDATED_BY → Paper)
# Return enriched answer
```

**Vantagens:**
- Entende semântica (embeddings)
- Conecta code ↔ theory ↔ research
- Valida claims (tem paper?)
- O(log n) com indexes

---

## II. INTEGRAÇÃO COLLIDER → GRAPHRAG

### A. Enriched Purpose Field

**Current (Collider):**
```python
# src/core/purpose_field.py
def compute_purpose(node, graph):
    # Heuristic based on centrality
    if betweenness > 0.5:
        return "coordinator"
    # etc.
```

**Enhanced (with GraphRAG):**
```python
# src/core/purpose_field_graphrag.py
def compute_purpose_enriched(node, graph, neo4j_conn):
    # Compute from metrics (existing)
    heuristic_purpose = compute_purpose(node, graph)

    # Validate via GraphRAG
    validation = neo4j_conn.run("""
        MATCH (code:CodeEntity {id: $node_id})
        MATCH (code)-[:SIMILAR_TO]->(similar)
        MATCH (similar)-[:IMPLEMENTS]->(concept)
        MATCH (paper)-[:VALIDATES]->(concept)
        RETURN concept.name, paper.title
    """, node_id=node.id)

    # Enriched purpose with grounding
    return {
        "computed": heuristic_purpose,
        "confidence": 0.75,
        "theory_grounding": validation.get("paper"),
        "validated": bool(validation)
    }
```

**Arquivo a criar:** `standard-model-of-code/src/core/purpose_field_graphrag.py`

---

### B. Brain Download Enhancement

**Current sections (11):**
```
1. Identity
2. Character
3. Architecture
4. Health
5. Improvements
6. Strategic Intelligence
7. Visual Reasoning
8. Domain Context
9. Performance
10. AI Insights
11. Quick Reference
```

**Nova seção 12:**
```
## THEORETICAL GROUNDING (GraphRAG)

This architecture exemplifies:
- [Collider queries GraphRAG for matching theories]

Validated by research:
- [GraphRAG lists papers supporting this architecture]

Theory gaps:
- [GraphRAG identifies concepts without validation]

Recommended reading:
- [GraphRAG suggests relevant papers]
```

**Arquivo a modificar:** `standard-model-of-code/src/core/brain_download.py`

---

## III. ARQUIVAMENTO (O Que Salvar)

### A. Código Legacy (Manter como Referência)

**Criar:** `standard-model-of-code/.archive/pre-graphrag/`

**Arquivar:**

1. **query_chunks.py** (text search original)
   - Razão: GraphRAG semantic search substitui
   - Manter: Como fallback se GraphRAG down
   - Status: LEGACY (funcional mas inferior)

2. **refinery_report.py** (activity reports)
   - Razão: GraphRAG pode gerar reports melhores
   - Manter: Útil para debugging
   - Status: LEGACY (mas ainda usado)

3. **Versões antigas:**
   - wire.py sem REFINERY stages
   - autopilot.py sem COMM_FABRIC
   - pe sem refinery commands

**NÃO arquivar:**
- Nada! Tudo ainda é usado ou vai ser usado

**Conclusão:** Nada precisa ser arquivado ainda - GraphRAG é ADIÇÃO, não substituição

---

### B. Documentação Histórica

**Criar:** `.agent/intelligence/sessions/2026-01-27/`

**Mover para lá:**
- MEGACHECKPOINT_20260127.md
- SESSION_FINAL_STATE.md
- PHASE_A_EXECUTION_LOG.md
- SESSION_COMPLETE_SUMMARY.md
- Todos os *_SYNTHESIS.md, *_ANALYSIS.md

**Razão:** Preservar histórico da sessão, não poluir intelligence/

**Manter em intelligence/:**
- ONTOLOGIA_SISTEMAS_FLUXO.md (teoria ativa)
- INTEGRATION_GAPS.md (work in progress)
- TEORIA_COMPLETA_SESSAO.md (referência ativa)

---

## IV. FINALIZAÇÃO DA INTEGRAÇÃO

### TASK A: Create GraphRAG Query Interface (2h)

**Arquivo:** `.agent/tools/graphrag_query.py`

```python
#!/usr/bin/env python3
"""GraphRAG Query Interface - Semantic queries over knowledge graph"""

from neo4j import GraphDatabase
import sys

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "elements2026"

def query_graphrag(question):
    """Execute GraphRAG query."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        # Intent classification (simple)
        if "validate" in question.lower():
            # What validates X?
            concept = extract_concept(question)
            result = session.run("""
                MATCH (c:SmocConcept)
                WHERE c.name CONTAINS $concept
                MATCH (pc)-[:VALIDATES]->(c)
                MATCH (p)-[:DEFINES]->(pc)
                RETURN p.title, p.author, c.name
            """, concept=concept)

        elif "implement" in question.lower():
            # What code implements X?
            concept = extract_concept(question)
            result = session.run("""
                MATCH (c:SmocConcept)
                WHERE c.name CONTAINS $concept
                MATCH (code:CodeEntity)
                WHERE code.purpose CONTAINS c.name
                RETURN code.id, code.file_path, c.name
            """, concept=concept)

        else:
            # General semantic search
            result = session.run("""
                MATCH (n)
                WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $query)
                RETURN n
                LIMIT 10
            """, query=question)

        # Format results
        for record in result:
            print(record)

    driver.close()

if __name__ == "__main__":
    query_graphrag(sys.argv[1] if len(sys.argv) > 1 else "test")
```

---

### TASK B: Integrate com ./pe (30min)

**Adicionar ao pe script:**
```bash
graphrag)
    shift
    case "${1:-help}" in
        query)
            shift
            .tools_venv/bin/python .agent/tools/graphrag_query.py "$@"
            ;;
        status)
            cypher-shell -u neo4j -p elements2026 \
              "MATCH (n) RETURN labels(n)[0], count(n);"
            ;;
        viz)
            open http://localhost:7474
            ;;
        *)
            echo "Usage: ./pe graphrag <command>"
            echo ""
            echo "Commands:"
            echo "  query 'question'   Query knowledge graph"
            echo "  status             Show graph statistics"
            echo "  viz                Open Neo4j Browser"
            ;;
    esac
    ;;
```

---

### TASK C: Add to Collider Brain Download (1h)

**Modificar:** `standard-model-of-code/src/core/brain_download.py`

**Adicionar após seção 11:**

```python
def generate_theoretical_grounding(graph, neo4j_conn):
    """Section 12: Theoretical Grounding (GraphRAG)."""

    if not neo4j_conn:
        return "Neo4j not available - skipping theoretical grounding"

    # Query: What theories apply to this codebase?
    theories = neo4j_conn.run("""
        MATCH (code:CodeEntity)-[:IMPLEMENTS]->(concept:SmocConcept)
        MATCH (paper:AcademicPaper)-[:VALIDATES]->(concept)
        RETURN DISTINCT paper.title, paper.author, concept.name
        LIMIT 10
    """)

    # Query: What are theory gaps?
    gaps = neo4j_conn.run("""
        MATCH (concept:SmocConcept)
        WHERE NOT (concept)<-[:VALIDATES]-()
        RETURN concept.name
    """)

    output = """
## THEORETICAL GROUNDING

This codebase exemplifies:
"""
    for theory in theories:
        output += f"- {theory['paper.title']} ({theory['paper.author']})\n"
        output += f"  Concept: {theory['concept.name']}\n"

    output += "\nTheory gaps (need validation):\n"
    for gap in gaps:
        output += f"- {gap['concept.name']}\n"

    return output
```

---

## V. PLANO DE EXECUÇÃO

### Hoje (2 horas):

**1. Limpar duplicatas (15min)**
```cypher
// Delete duplicate nodes (keep first occurrence)
MATCH (n)
WITH labels(n)[0] as label, n.id as id, collect(n) as nodes
WHERE size(nodes) > 1
FOREACH (n in tail(nodes) | DETACH DELETE n)
```

**2. Criar graphrag_query.py (1h)**
- Implement query interface
- Test com 5 queries
- Validate results

**3. Integrar ./pe graphrag (30min)**
- Add commands
- Test via CLI
- Document usage

**4. Arquivar documentação sessão (15min)**
```bash
mkdir -p .agent/intelligence/sessions/2026-01-27
mv .agent/intelligence/*CHECKPOINT*.md sessions/2026-01-27/
mv .agent/intelligence/*SUMMARY*.md sessions/2026-01-27/
```

---

### Amanhã (4 horas):

**5. Enhance Collider (3h)**
- Add purpose_field_graphrag.py
- Modify brain_download.py (section 12)
- Test enriched output

**6. Validate Accuracy (1h)**
- 20 test queries
- Compare: text search vs GraphRAG
- Measure: precision, recall
- Document: Results

---

## VI. CÓDIGO PARA ARQUIVAR (Preservação Histórica)

**NADA por enquanto!**

**Razão:**
- Text search (query_chunks.py) → Ainda útil como fallback
- Refinery reports → Ainda usados
- Todos os butlers → Ainda funcionando

**GraphRAG é ADIÇÃO (não substituição)**

**Quando arquivar:**
- Se/quando GraphRAG provar 100% superior
- Se/quando desativarmos text search
- Então: Mover para `.archive/pre-graphrag-{date}/`

---

## VII. PRÓXIMOS PASSOS IMEDIATOS

**Passo 1: Limpar duplicatas (agora - 5min)**

**Passo 2: Testar query real**
```bash
# Em Neo4j Browser:
MATCH (p:AcademicPaper {id: 'REF-040'})
MATCH (p)-[:DEFINES]->(pc)-[:VALIDATES]->(c:SmocConcept)
RETURN p.title, c.name
```

**Passo 3: Criar query interface (1h)**

**Passo 4: Integrar Collider (amanhã - 3h)**

---

**COMEÇAR COM LIMPEZA DE DUPLICATAS?**

Ou prefere manter duplicatas e só testar queries primeiro?