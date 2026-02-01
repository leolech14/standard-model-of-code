# 🎯 Standard Model → DDD Architecture Linter: Pivot Roadmap

> **Vision Shift:** From "Universal Physics of Code" to "Practical DDD Constraint Enforcement"

---

## 1. What We Keep vs Kill

### ✅ KEEP (Proven Value)
| Asset | Why Keep | New Role |
|-------|----------|----------|
| **RPBL Dimensions** | Orthogonal, meaningful | Simplified to 3D: `Purity × Boundary × Lifecycle` |
| **11 Constraint Laws** | Actionable, enforceable | Core lint rules |
| **V12 Minimal Engine** | Working CLI pipeline | Refactor as rule executor |
| **Honest Assessment** | Credibility, focus | Marketing differentiator |

### ❌ KILL (Overengineered)
| Asset | Why Kill |
|-------|----------|
| 1440 coordinate space | Sparse, most cells invalid |
| 96 Hadrons taxonomy | 74 unused, causes drift |
| 384 subhadrons | Engineered numerology |
| 42 forbidden archetypes | Replace with ~10 high-confidence rules |
| "Standard Model" branding | Physics metaphor oversells |

---

## 2. New Scoped Product: **DDDLint**

### Core Value Proposition
> "Catch DDD/Clean Architecture violations in CI before they become tech debt"

### Target Users
- **Primary:** Teams adopting DDD/CQRS in Python, TypeScript, Java, Go
- **Secondary:** Tech leads enforcing architecture boundaries in monorepos
- **Tertiary:** Architecture consultants running health checks

### 10 Core Lint Rules (Ship First)

| ID | Rule | Detects | Severity |
|----|------|---------|----------|
| `DDD001` | Command returns data | CQRS violation | Error |
| `DDD002` | Query mutates state | CQRS violation | Error |
| `DDD003` | Pure function has I/O | Purity violation | Error |
| `DDD004` | Entity without ID field | Identity violation | Error |
| `DDD005` | ValueObject with identity | Identity violation | Warning |
| `DDD006` | Repository in domain layer | Boundary violation | Error |
| `DDD007` | Domain imports infrastructure | Dependency inversion | Error |
| `DDD008` | Aggregate spans bounded contexts | Boundary violation | Warning |
| `DDD009` | Test touches production data | Isolation violation | Error |
| `DDD010` | Service holds mutable state | Stateless violation | Warning |

---

## 3. Development Phases

### Phase 1: Foundation (Weeks 1-4)
**Goal:** 3 rules working on 3 fixtures

```
[ ] Refactor engine to tree-sitter AST (not regex)
[ ] Implement DDD001, DDD002, DDD003
[ ] Build fixtures: dddpy, nestjs-cqrs, go-clean-arch
[ ] Output: JSON + SARIF format
[ ] Benchmark: P/R/F1 per rule per fixture
```

**Success Metric:** F1 > 0.85 on all 3 rules

---

### Phase 2: Coverage (Weeks 5-8)
**Goal:** 10 rules, 10 fixtures, 4 languages

```
[ ] Add DDD004-DDD010
[ ] Fixtures: Python (3), TypeScript (3), Java (2), Go (2)
[ ] GitHub Action packaging
[ ] CLI flags: --fix suggestions, --ignore patterns
```

**Success Metric:** 80% of DDD practitioners say "this is useful" (5+ user interviews)

---

### Phase 3: Integration (Weeks 9-12)
**Goal:** Production-ready for OSS adoption

```
[ ] VSCode extension (inline warnings)
[ ] Pre-commit hook support
[ ] Documentation site
[ ] Public benchmark against ArchUnit/eslint-plugin-boundaries
```

**Success Metric:** 100+ GitHub stars, 3+ external contributors

---

## 4. Technical Refactoring Plan

### From V12 Minimal → DDDLint Core

```
spectrometer_v12_minimal/          →   dddlint/
├── core/                               ├── core/
│   ├── tree_sitter_engine.py          │   ├── parser.py        # AST extraction
│   ├── particle_classifier.py    →    │   ├── classifier.py    # Pattern → Rule
│   ├── dependency_analyzer.py         │   ├── graph.py         # Import graph
│   └── report_generator.py            │   └── reporter.py      # SARIF + JSON
├── patterns/                           ├── rules/
│   └── particle_defs.json        →    │   └── ddd_rules.yaml   # 10 rules config
└── validation/                         └── fixtures/
    └── dddpy_real/                         ├── python/
                                            ├── typescript/
                                            ├── java/
                                            └── go/
```

### Detection Strategy Upgrade

| Pattern | Old (Regex) | New (Semantic) |
|---------|-------------|----------------|
| CommandHandler | `*Command*` in name | Method returns void + takes `*Command` type |
| PureFunction | Heuristic | No I/O calls, no `self` mutation, no globals |
| Entity | `*Entity*` in name | Has `id`/`uuid`/`pk` field + mutable state |
| Repository | `*Repository*` in name | Implements `save`/`find`/`delete` + I/O |

---

## 5. Validation Strategy

### Ground Truth Fixtures (10 minimum)

| Repo | Lang | Architecture | Source |
|------|------|--------------|--------|
| dddpy | Python | Onion/DDD | Existing |
| python-clean-architecture | Python | Clean | GitHub |
| nestjs-cqrs | TypeScript | CQRS | GitHub |
| ts-clean-architecture | TypeScript | Clean | GitHub |
| go-clean-arch | Go | Clean | GitHub |
| go-ddd-example | Go | DDD | GitHub |
| axon-trader | Java | CQRS/ES | GitHub |
| ddd-java | Java | DDD | GitHub |
| eShopOnContainers | C# | Microservices | Reference |
| your-own-repo | Mixed | Monorepo | Internal |

### Metrics Per Rule
- **Precision:** % of flagged violations that are real
- **Recall:** % of real violations we catch
- **F1 Score:** Target > 0.85 for all shipped rules

---

## 6. What Stays from the "Standard Model"

### Conceptual Contributions Worth Publishing
1. **RPBL as Architecture DNA** — paper-worthy if validated
2. **Constraint-Driven Forbidden Patterns** — generalizable approach
3. **Purpose Map for LLM Context** — unique angle for AI-assisted architecture

### Future Expansion (Post-DDDLint)
- ML model trained on RPBL scores
- Architecture drift detection over time
- "Architecture as Code" spec format

---

## 7. Quick Wins (This Week)

```bash
# 1. Rename the project
mv spectrometer_v12_minimal dddlint

# 2. Implement one AST-based rule
# (Command returning data is easiest)

# 3. Run on 3 real repos, measure P/R/F1

# 4. Write 1-page README with honest positioning
```

---

## 8. Decision: Continue or Abandon?

| Factor | Score | Notes |
|--------|-------|-------|
| Technical feasibility | 8/10 | Core infra exists |
| Market need | 7/10 | DDD tooling gap is real |
| Competition | 6/10 | ArchUnit (Java-only), eslint-plugin-boundaries (basic) |
| Effort to MVP | 6/10 | 4-6 weeks to first 3 rules |
| Upside if successful | 8/10 | Could become standard DDD linter |

**Recommendation:** ✅ **Continue with scoped pivot**

---

> *"A useful tool with honest limitations beats a physics theory built on false claims."*
> — STANDARD_MODEL_OF_CODE_HONEST_GUIDE.md
