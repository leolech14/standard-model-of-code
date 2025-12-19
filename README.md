# Standard Code Spectrometer

An experimental framework for classifying software constructs using a dimensional taxonomy.

## Background

This project explores whether a consistent ontology can describe code structures across programming languages. We propose:

- **167 atomic construct types** organized into 12 families across 4 phases
- **8 orthogonal dimensions** for semantic classification  
- A **hybrid heuristic + LLM pipeline** for automated classification

The taxonomy draws metaphorical inspiration from particle physics nomenclature, but the claims are empirical, not theoretical.

## Status

This is ongoing research. The taxonomy has been tested on ~35,000 code entities across 3 production codebases with 100% classification coverage, but it remains a hypothesis under active refinement.

We welcome critique and contributions.

---

## Quick Start

```bash
git clone https://github.com/leolech14/standard-model-for-computer-language.git
cd standard-model-for-computer-language
pip install -r requirements.txt

python cli.py analyze /path/to/any/repo
```

Results appear in `output/learning/COMPREHENSIVE_REPORT.md`

---

## The Taxonomy

### 4 Phases, 12 Families, 167 Atoms

| Phase | Families | Atoms | Description |
|-------|----------|------:|-------------|
| **DATA** | Bits, Bytes, Primitives, Variables | 26 | Data foundations |
| **LOGIC** | Expressions, Statements, Control, Functions | 61 | Behavioral constructs |
| **ORGANIZATION** | Aggregates, Services, Modules, Files | 45 | Structural patterns |
| **EXECUTION** | Handlers, Workers, Initializers, Probes | 35 | Runtime constructs |

### 8 Dimensions

Every classified construct is measured across 8 orthogonal dimensions:

| Dimension | Question | Example Values |
|-----------|----------|----------------|
| **WHAT** | What is it? | 167 atom types |
| **Layer** | Where in the architecture? | Interface, Core, Infrastructure |
| **Role** | What job does it perform? | Orchestrator, Data, Worker |
| **Boundary** | How does it connect? | Internal, Input, I/O, Output |
| **State** | Does it hold memory? | Stateful, Stateless |
| **Effect** | What side effects? | Pure, Read, Write, ReadModify |
| **Activation** | How is it triggered? | Direct, Event, Time |
| **Lifetime** | How long does it live? | Transient, Session, Global |

---

## Documentation

- [**STANDARD_MODEL_PAPER.md**](STANDARD_MODEL_PAPER.md) — Full theoretical framework
- [**ATOMS_REFERENCE.md**](ATOMS_REFERENCE.md) — Complete 167-atom taxonomy
- [**patterns/particle_defs.json**](patterns/particle_defs.json) — 22 high-level DDD patterns

---

## CLI Commands

```bash
# Analyze a repository
python cli.py analyze /path/to/repo

# System health check
python cli.py health

# Full audit (health + minimal analysis)
python cli.py audit /path/to/repo

# Graph analysis (on existing graph.json)
python cli.py graph output/analysis/graph.json
```

---

## Limitations

- Language support limited to Python, JavaScript, TypeScript
- LLM classification requires Ollama running locally
- Taxonomy is empirically derived, not mathematically proven
- Detection heuristics may misclassify edge cases

---

## Contributing

We welcome:
- Feedback on taxonomic choices
- Additional language support
- Alternative classification heuristics
- Empirical validation on new codebases

---

## Installation

```bash
pip install -r requirements.txt
```

Optional: Install [Ollama](https://ollama.ai) for hybrid LLM classification.

---

## License

MIT

---

*An exploratory project probing the structure of code.*
