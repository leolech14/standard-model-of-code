# Research Papers Library

Master index of academic papers supporting the Standard Model of Code research.

**Last Updated:** 2026-02-02

---

## Directory Structure

```
particle/docs/research/
├── similar_papers/           # Papers similar to SMC (code representation, taxonomies)
│   ├── INDEX.md
│   └── 9 PDFs (~14 MB)
├── foundational_ai_ml/       # Core AI/ML papers (transformers, LLMs)
│   ├── INDEX.md
│   └── 5 PDFs (~14 MB)
├── gemini/                   # Gemini research outputs
├── perplexity/               # Perplexity research outputs
└── notebooklm/               # NotebookLM research outputs
```

---

## Paper Collections

### Similar Papers (Code Analysis & Taxonomies)
Location: `similar_papers/`

| Category | Count | Key Papers |
|----------|-------|------------|
| Code Representation | 3 | SemanticFlowGraph (FSE'23), ASTNN, S-AST |
| Taxonomies | 3 | CPC (ICSE'20), Seven Kingdoms, Bottom-Up |
| Surveys | 3 | DL+Code, GNN Review, LLM+KG |

**Most Important:** `SemanticFlowGraph_FSE2023` - closest to SMC approach

### Foundational AI/ML
Location: `foundational_ai_ml/`

| Category | Count | Key Papers |
|----------|-------|------------|
| Transformers | 3 | Attention Is All You Need, BERT, GPT |
| Surveys | 2 | Foundation Models, LLM Survey 2024 |

**Most Important:** `Attention_Is_All_You_Need_Transformer_2017.pdf` - THE foundation

---

## Quick Reference: Papers to Cite

### For Related Work
```
@inproceedings{zhang2019astnn,
  title={A Novel Neural Source Code Representation based on AST},
  author={Zhang et al.},
  booktitle={ICSE},
  year={2019}
}

@inproceedings{du2023sfg,
  title={Pre-training Code Representation with Semantic Flow Graph},
  author={Du et al.},
  booktitle={FSE},
  year={2023}
}

@inproceedings{huang2020cpc,
  title={CPC: Automatically Classifying and Propagating Natural Language Comments},
  author={Huang et al.},
  booktitle={ICSE},
  year={2020}
}
```

### For Background
```
@article{vaswani2017attention,
  title={Attention Is All You Need},
  author={Vaswani et al.},
  journal={NeurIPS},
  year={2017}
}

@article{devlin2018bert,
  title={BERT: Pre-training of Deep Bidirectional Transformers},
  author={Devlin et al.},
  journal={arXiv},
  year={2018}
}
```

---

## Total Library Stats

| Collection | Papers | Size |
|------------|--------|------|
| Similar Papers | 9 | ~14 MB |
| Foundational AI/ML | 5 | ~14 MB |
| **Total** | **14** | **~28 MB** |

---

## Usage Notes

1. **For Writing Paper:** Start with `similar_papers/INDEX.md` for positioning
2. **For Understanding AI Context:** Read `foundational_ai_ml/INDEX.md`
3. **For Citation:** Use BibTeX entries above

## Missing Papers (TODO)

- [ ] ISO/IEC 25010 standard document
- [ ] SWEBOK v4 (already in archive/downloads_2026/)
- [ ] Graph ML for Static Analysis systematic mapping (2025)
- [ ] More recent code LLM papers (CodeBERT, GraphCodeBERT, etc.)
