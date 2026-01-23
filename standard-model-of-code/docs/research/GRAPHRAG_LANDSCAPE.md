# GraphRAG Landscape Analysis

> Research on Graph Retrieval-Augmented Generation variations and benchmarks.
> Date: 2026-01-22

## Collider Alignment Score: 9/10

Collider is a near-perfect "Graph" component for a code-focused GraphRAG system.

| Pillar | Score | Implementation |
|--------|-------|----------------|
| Entity Extraction | 10/10 | `TreeSitterUniversalEngine` + classifiers |
| Edge Building | 10/10 | `edge_extractor.py` (calls, imports, inherits) |
| Community Detection | 10/10 | `graph_analyzer.py` (Leiden/Louvain) |
| Summarization | 8/10 | `ComponentCard` + optional AI insights |
| Multi-hop Reasoning | 9/10 | Knots, Markov, execution flow |

---

## GraphRAG Variations

| Variant | Creator | Key Differentiator |
|---------|---------|-------------------|
| **GraphRAG** | Microsoft | LLM-built knowledge graphs + community summarization |
| **LazyGraphRAG** | Microsoft | 1000x cheaper indexing, defers LLM to query time |
| **LightRAG** | HKBU | Dual-level retrieval (low/high) for scalability |
| **HiRAG** | Academic | Hierarchical multi-level abstraction |
| **GRAG** | Academic | Soft pruning + graph-aware prompt tuning |
| **MedGraphRAG** | Academic | Medical domain specialization |
| **MiniRAG** | HKUDS | Lightweight, resource-constrained |
| **DRIFT Search** | Microsoft | Global + local search combination |
| **G-Retriever** | Academic | Direct subgraph retrieval |

---

## Benchmarks

| Dataset | Type | Metrics |
|---------|------|---------|
| HotPotQA | Multi-hop QA | EM, F1 |
| WebQSP | KG QA | Hit@1, Hit@5 |
| GraphRAG-Bench | MS Standard | Comprehensiveness, Diversity |
| ExplaGraphs | Commonsense | Accuracy |
| PubMedQA | Medical | F1 |

### Evaluation Metrics
- **Hit@k** — Retrieval accuracy
- **BLEU/ROUGE** — Generation quality
- **BERTScore** — Semantic similarity
- **Faithfulness** — Hallucination detection
- **RAGAS** — Standard RAG evaluation framework

---

## Gap Analysis: Collider → Full GraphRAG

| Component | Status | Action Needed |
|-----------|--------|---------------|
| Entity extraction | ✓ Done | — |
| Edge building | ✓ Done | — |
| Community detection | ✓ Done | — |
| Community summarization | ⚠️ Partial | Add auto-summary per community |
| Query-time retrieval | ✗ Missing | Build subgraph retrieval API |
| LLM response generation | ✗ Missing | Add RAG runtime layer |

---

## References

- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
- [LazyGraphRAG](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/)
- [GraphRAG-Benchmark](https://github.com/GraphRAG-Bench/GraphRAG-Benchmark)
- [RAGAS Metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
