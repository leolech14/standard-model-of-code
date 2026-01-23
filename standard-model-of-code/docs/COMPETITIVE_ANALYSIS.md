# COMPETITIVE ANALYSIS & MODULE ROADMAP

> Collider's market position and extensibility roadmap.
>
> **Created:** 2026-01-22
> **Status:** Living document

---

## CURRENT STATE (v1.0)

### What Collider Does Uniquely

| Capability | Status | Competitors |
|------------|--------|-------------|
| 8-Dimensional Classification | ✓ Implemented | None |
| Standard Model Theory (200 atoms, 33 roles) | ✓ Implemented | None |
| 3D Force-Directed Graph Visualization | ✓ Implemented | None |
| Purity Scoring (D6:EFFECT) | ✓ Implemented | None |
| RPBL Character Analysis | ✓ Implemented | None |
| Graph Centrality (PageRank, Betweenness) | ✓ Implemented | None |
| Topology Role Detection | ✓ Implemented | None |
| UPB Visual Property Binding | ✓ Implemented | None |
| Tree-sitter AST Analysis | ✓ Implemented | Partial (Semgrep) |

### Current Metrics (Self-Analysis)

```
Nodes analyzed:        2,107
Edges extracted:       5,860
Files processed:       173
Processing time:       18.1s
Dimension coverage:    99.7%
Tree-sitter coverage:  82.6%
Languages supported:   5 (Python, JS/TS, Go, Rust)
```

---

## MARKET OVERVIEW (2025-2026)

### Market Size and Growth

| Metric | Value | Source |
|--------|-------|--------|
| Global SAST Market (2025) | $554 million | Mordor Intelligence |
| Projected Market (2030) | $1.548 billion | Mordor Intelligence |
| CAGR | 22.82% | Mordor Intelligence |
| Cloud SAST Growth Rate | 20.4% CAGR | Industry reports |
| IDE Plugin Growth Rate | 21.1% CAGR | Industry reports |

### Key Market Trends

1. **Shift-Left Security** - IDE plugins growing fastest (21.1% CAGR) as security moves to code authoring
2. **AI-Generated Code** - 60% more false positives from legacy scanners on AI-written code
3. **Platform Consolidation** - 70% of triage time lost to duplicate alerts across isolated tools
4. **Supply Chain Security** - 45% of orgs will experience supply chain attacks by 2025 (Gartner)
5. **Developer-First Tools** - Emphasis on low false positives and seamless workflow integration

---

## COMPETITIVE LANDSCAPE

### Detailed Competitor Profiles

#### SonarQube / SonarCloud

| Attribute | Value |
|-----------|-------|
| **Focus** | Code Quality + Security |
| **Languages** | 30+ (Java, Python, JS/TS, C/C++, C#, Go, Ruby, PHP, etc.) |
| **Pricing** | Cloud: €30/mo (100K LOC), Free tier (50K LOC), Enterprise: Annual license |
| **Deployment** | Cloud (SonarCloud) + Self-managed (SonarQube Server) |
| **Key Feature** | Quality Gates - enforce thresholds before merge |
| **Certifications** | SOC 2 Type II (Feb 2025), ISO 27001:2022 |
| **IDE Plugins** | JetBrains, VS Code |
| **CI/CD** | Jenkins, GitHub Actions, Azure DevOps, GitLab CI, Bitbucket |

#### Semgrep

| Attribute | Value |
|-----------|-------|
| **Focus** | Custom Rules + Security (SAST/SCA/Secrets) |
| **Languages** | 20+ (C, C++, C#, Go, Java, JS, Kotlin, PHP, Python, Ruby, Rust, etc.) |
| **Pricing** | Free (10 contributors), Teams: $40/dev/mo (Code), $40/dev/mo (SCA), $20/dev/mo (Secrets) |
| **Deployment** | Cloud + Self-managed |
| **Key Feature** | Rule-based pattern matching, Semgrep Assistant (GPT-4 powered) |
| **Recent** | MCP Server for LLM integration, 85% false positive auto-detection |
| **IDE Plugins** | Limited |
| **CI/CD** | GitHub, GitLab, Bitbucket, Azure DevOps |

#### Snyk Code

| Attribute | Value |
|-----------|-------|
| **Focus** | Developer-First Security (SAST/SCA/DAST/Container) |
| **Languages** | Java, Python, JS/TS, C#, Go, Ruby, PHP |
| **Pricing** | From $25/mo, Ignite: $1,260/dev/yr, Enterprise: Contact |
| **Deployment** | Cloud-native |
| **Key Feature** | AI-powered semantic analysis, lowest false-positive rates |
| **Recent** | Acquired Probely (DAST) Nov 2024, 300+ new customers in 2024 |
| **IDE Plugins** | VS Code, JetBrains |
| **CI/CD** | Jenkins, CircleCI, GitHub Actions, AWS CodePipeline, Azure, Bitbucket |

#### CodeQL (GitHub Advanced Security)

| Attribute | Value |
|-----------|-------|
| **Focus** | Semantic Analysis / Vulnerability Research |
| **Languages** | 9 GA (JS/TS, Python, Java, C/C++, C#, Ruby, Go, Kotlin), Swift (beta) |
| **Pricing** | Free (open source), GHAS: $29/active committer/mo |
| **Deployment** | Cloud (GitHub) + Enterprise Server |
| **Key Feature** | Queryable code database, 432 security queries, 100% CWE Top 25 |
| **Recent** | 318 default queries (+27% YoY) |
| **IDE Plugins** | VS Code (CodeQL extension) |
| **CI/CD** | Native GitHub Actions |

#### Veracode

| Attribute | Value |
|-----------|-------|
| **Focus** | Enterprise Compliance (SAST/DAST/SCA/IaC) |
| **Languages** | 100+ languages, 350+ frameworks |
| **Pricing** | SAST: ~$15K/yr (100 apps), SCA: ~$12K/yr, DAST: ~$20-25K/yr, Full suite: $100K+ |
| **Deployment** | Cloud + Hybrid |
| **Key Feature** | Whole-program analysis, AI-powered Veracode Fix |
| **Recent** | 420 trillion LOC scanned, 204M flaws found, EASM (May 2025), Package Firewall (Jun 2025) |
| **IDE Plugins** | VS Code, JetBrains, Eclipse, Visual Studio |
| **CI/CD** | Jenkins, Azure DevOps, GitLab, GitHub Actions |

#### Checkmarx One

| Attribute | Value |
|-----------|-------|
| **Focus** | Enterprise AppSec Platform (SAST/DAST/SCA/API) |
| **Languages** | 30+ (Apex, Groovy, Java, JS, JSP, Kotlin, PHP, Python, Ruby, etc.) |
| **Pricing** | $5K-$35K+/yr (50 devs), Enterprise: Contact |
| **Deployment** | Cloud |
| **Key Feature** | Agentic AI for instant fix recommendations, unified dashboard |
| **Recent** | Acquired Dustico (2021) for malicious code detection |
| **IDE Plugins** | Yes (multiple) |
| **CI/CD** | Major platforms supported |

#### Coverity (Black Duck/Synopsys)

| Attribute | Value |
|-----------|-------|
| **Focus** | Enterprise Security + Code Quality |
| **Languages** | 22 languages, 200+ frameworks |
| **Pricing** | Enterprise (contact sales) |
| **Deployment** | Cloud + On-prem |
| **Key Feature** | Multi-file defect detection, Code Sight IDE plugin |
| **Compliance** | OWASP Top 10, CWE Top 25, MISRA, CERT |
| **IDE Plugins** | Code Sight (real-time) |
| **CI/CD** | Popular IDE, SCM, CI systems |

### Comprehensive Feature Matrix

| Feature | Collider | SonarQube | Semgrep | Snyk | CodeQL | Veracode | Checkmarx |
|---------|----------|-----------|---------|------|--------|----------|-----------|
| **SAST** | Partial | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **SCA** | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **DAST** | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| **Secrets** | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **IaC** | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **Container** | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| **API Security** | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| **Quality Gates** | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| **AI Remediation** | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **8D Classification** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **3D Visualization** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Architecture Intel** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Purity Analysis** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Graph Centrality** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

### Pricing Comparison

| Tool | Free Tier | Entry Price | Enterprise |
|------|-----------|-------------|------------|
| **Collider** | ✓ Open source | Free | N/A |
| **SonarQube** | 50K LOC | €30/mo (100K LOC) | Annual license |
| **Semgrep** | 10 contributors | $40/dev/mo | Contact |
| **Snyk** | Limited | $25/mo | $1,260/dev/yr |
| **CodeQL** | Open source repos | $29/committer/mo | GHAS |
| **Veracode** | ✗ | ~$15K/yr | $100K+ |
| **Checkmarx** | ✗ | ~$5K/yr | $35K+ |
| **Coverity** | ✗ | Enterprise | Enterprise |

### Emerging Competitors

| Tool | Focus | Key Differentiator |
|------|-------|-------------------|
| **Aikido Security** | AI-powered SAST + compliance | Acquired Trag AI (2025), SOC 2/GDPR automation |
| **DeepSource** | DevSecOps platform | Noise reduction, auto-remediation |
| **CodeRabbit** | AI code review | Learns from developer corrections |

### Collider's Unique Position

```
Collider creates a NEW CATEGORY: Code Architecture Intelligence

┌─────────────────────────────────────────────────────────────────┐
│                    THE SECURITY QUESTION                        │
│                                                                 │
│   SonarQube:  "Is this code clean?"                            │
│   Snyk:       "Is this code secure?"                           │
│   Semgrep:    "Does this match a vulnerability pattern?"       │
│   Veracode:   "Does this pass compliance?"                     │
│                                                                 │
│   Collider:   "What IS this code?"                             │
│               "What role does it play in the system?"          │
│               "How does it connect to everything else?"        │
│               "What is its architectural character?"           │
└─────────────────────────────────────────────────────────────────┘

Unique capabilities NO competitor offers:
• 8-Dimensional Classification (D1-D8)
• 200 Atoms / 33 Roles taxonomy
• 3D Force-Directed Graph Visualization
• Purity Scoring (D6:EFFECT)
• RPBL Character Analysis
• Graph Centrality (PageRank, Betweenness)
• Universal Property Binding (data → visual mapping)
```

---

## FUTURE MODULE ROADMAP

### Architecture: Pluggable Modules

Collider's pipeline architecture supports pluggable modules at multiple extension points:

```
┌─────────────────────────────────────────────────────────────┐
│                    COLLIDER CORE                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │ Parser  │→ │Analyzer │→ │Classifier│→ │ Visualizer │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘    │
│       │            │            │               │           │
│       ▼            ▼            ▼               ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EXTENSION POINTS                        │   │
│  │  • Language Modules    • Analysis Modules            │   │
│  │  • Security Modules    • Visualization Modules       │   │
│  │  • Integration Modules • Export Modules              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

### Module Opportunities

#### M1: Language Modules (Expand Coverage)

| Language | Priority | Effort | Tree-sitter Support |
|----------|----------|--------|---------------------|
| Java | HIGH | Medium | ✓ Available |
| C/C++ | HIGH | Medium | ✓ Available |
| C# | MEDIUM | Medium | ✓ Available |
| Ruby | MEDIUM | Low | ✓ Available |
| PHP | MEDIUM | Low | ✓ Available |
| Kotlin | MEDIUM | Low | ✓ Available |
| Swift | LOW | Low | ✓ Available |
| Scala | LOW | Medium | ✓ Available |

**Implementation Pattern:**
```
src/core/queries/{language}/
├── symbols.scm      # Required: function/class extraction
├── locals.scm       # Optional: scope analysis
├── patterns.scm     # Optional: atom detection
└── data_flow.scm    # Optional: purity analysis
```

---

#### M2: Security Modules (Address Gap)

| Module | Priority | Competitors | Integration Point |
|--------|----------|-------------|-------------------|
| **SAST Scanner** | HIGH | Semgrep, Snyk | Post-parse analysis |
| **Dependency Check** | HIGH | Snyk, OWASP | Import analysis |
| **Secret Detection** | MEDIUM | GitLeaks, Aikido | Pattern matching |
| **Taint Analysis** | MEDIUM | CodeQL | Data flow extension |
| **OWASP Top 10** | MEDIUM | All | Rule-based detection |

**Proposed Architecture:**
```python
# src/core/security/__init__.py
class SecurityModule:
    def analyze(self, nodes: List[Node], edges: List[Edge]) -> SecurityReport:
        """Run security checks on analyzed code."""
        pass

# Plugs into Stage 2.12 of pipeline
```

---

#### M3: Integration Modules (Enterprise Readiness)

| Integration | Priority | Effort | Value |
|-------------|----------|--------|-------|
| **GitHub Actions** | HIGH | Low | CI/CD automation |
| **GitLab CI** | HIGH | Low | CI/CD automation |
| **Jenkins Plugin** | MEDIUM | Medium | Enterprise CI |
| **VS Code Extension** | HIGH | Medium | Developer experience |
| **JetBrains Plugin** | MEDIUM | Medium | Developer experience |
| **Slack/Teams Alerts** | LOW | Low | Notifications |
| **Jira Integration** | LOW | Medium | Issue tracking |

**GitHub Action Example:**
```yaml
# .github/workflows/collider.yml
- name: Run Collider Analysis
  uses: collider/action@v1
  with:
    output: collider-report
    fail-on: critical-violations
```

---

#### M4: Export Modules (Interoperability)

| Format | Priority | Use Case |
|--------|----------|----------|
| **SARIF** | HIGH | GitHub Security, IDE integration |
| **SPDX** | MEDIUM | License compliance |
| **CycloneDX** | MEDIUM | SBOM generation |
| **GraphML** | LOW | Graph tool import |
| **DOT** | LOW | Graphviz visualization |

---

#### M5: Analysis Modules (Extend Theory)

| Module | Priority | Theory Link | Description |
|--------|----------|-------------|-------------|
| **Coupling Analyzer** | HIGH | Architecture | Afferent/efferent coupling |
| **Cohesion Analyzer** | HIGH | Architecture | LCOM metrics |
| **Change Risk** | MEDIUM | D7:LIFECYCLE | Churn + complexity hotspots |
| **Test Coverage Map** | MEDIUM | D8:TRUST | Coverage → graph overlay |
| **Performance Predictor** | LOW | Theory expansion | Complexity → runtime |
| **Refactoring Suggester** | LOW | All dimensions | AI-powered recommendations |

---

#### M6: Visualization Modules (Enhance UX)

| Module | Priority | Description |
|--------|----------|-------------|
| **Diff Visualization** | HIGH | Compare two analyses |
| **Time-lapse Mode** | MEDIUM | Animate codebase evolution |
| **AR/VR Export** | LOW | Spatial computing readiness |
| **Dependency Matrix** | MEDIUM | DSM (Design Structure Matrix) |
| **Treemap View** | LOW | Alternative to 3D graph |

---

#### M7: Compliance Modules (Enterprise Requirement)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **OWASP Top 10** | HIGH | All major tools | Security vulnerability rules |
| **PCI-DSS Rules** | MEDIUM | Veracode, Checkmarx | Payment card compliance |
| **GDPR Data Flow** | MEDIUM | Snyk, SonarQube | Privacy compliance tracking |
| **Code Smell Rules** | HIGH | SonarQube, CodeClimate | Maintainability rules |
| **False Positive Tuning** | HIGH | All tools | Suppress/configure rules |

**Why needed:** Enterprise customers require compliance certifications. Without OWASP/PCI-DSS rules, Collider cannot be adopted in regulated industries.

---

#### M8: Cloud/SaaS Modules (Deployment Options)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Hosted SaaS** | HIGH | All major tools | Cloud-hosted analysis |
| **Multi-tenant** | MEDIUM | SonarCloud, Snyk | Organization support |
| **Multi-repo Support** | MEDIUM | All major tools | Monorepo + multi-repo |
| **Self-hosted Docker** | HIGH | SonarQube | On-prem deployment |

**Why needed:** Currently Collider is CLI-only. Teams need shared dashboards and centralized analysis.

---

#### M9: Collaboration Modules (Team Features)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **PR Comments** | HIGH | All CI tools | Auto-comment on PRs |
| **Issue Assignment** | MEDIUM | SonarQube, Snyk | Assign findings to devs |
| **Team Dashboards** | MEDIUM | CodeClimate | Aggregate team metrics |
| **Annotations API** | LOW | GitHub | In-file annotations |

**Why needed:** Individual analysis is useful; team-wide visibility drives adoption.

---

#### M10: Historical/Trends Modules (Time-Series)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Trend Charts** | HIGH | CodeClimate, SonarQube | Metrics over time |
| **Regression Detection** | HIGH | All CI tools | Alert on degradation |
| **Technical Debt Tracker** | MEDIUM | SonarQube | Debt accumulation |
| **Custom Dashboards** | LOW | Enterprise tools | Build custom reports |

**Why needed:** Point-in-time analysis is insufficient. Teams need to see improvement/degradation trends.

---

#### M11: Quality Gates Modules (CI Blocking)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Pass/Fail Thresholds** | HIGH | All CI tools | Block merge on violations |
| **Custom Gate Rules** | MEDIUM | SonarQube | Define custom criteria |
| **Baseline Comparison** | MEDIUM | Snyk | Compare to baseline |
| **Branch Policies** | LOW | GitHub/GitLab | Enforce on specific branches |

**Why needed:** Without quality gates, Collider is advisory-only. Teams need enforcement.

---

#### M12: Incremental Analysis Modules (Performance)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Diff-only Analysis** | HIGH | Semgrep, SonarQube | Analyze only changed files |
| **Result Caching** | MEDIUM | All tools | Cache unchanged results |
| **Parallel Processing** | MEDIUM | Built-in potential | Multi-core analysis |
| **Streaming Results** | LOW | Large codebase need | Progressive output |

**Why needed:** Full analysis on every PR is slow. Incremental mode enables CI adoption.

---

#### M13: API/SDK Modules (Programmatic Access)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **REST API** | HIGH | All SaaS tools | Programmatic access |
| **GraphQL API** | LOW | Modern tools | Flexible queries |
| **Webhooks** | MEDIUM | All CI tools | Event notifications |
| **Python SDK** | MEDIUM | Snyk, Semgrep | Native integration |

**Why needed:** Enables custom tooling, dashboards, and integration with internal systems.

---

#### M14: Duplicate Detection Modules (Code Quality)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Clone Detection** | MEDIUM | SonarQube, PMD | Find copy-pasted code |
| **Near-duplicate** | LOW | Advanced tools | Similar but not identical |
| **Cross-repo Clones** | LOW | Enterprise need | Duplicates across repos |

**Why needed:** DRY violations are a common code smell. Most competitors detect them.

---

#### M15: Test Coverage Modules (Quality Metrics)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Coverage Import** | HIGH | CodeClimate | Import lcov/cobertura |
| **Coverage Overlay** | MEDIUM | Unique to Collider | Show coverage on 3D graph |
| **Uncovered Complexity** | HIGH | Unique | High complexity + low coverage |
| **Test Gap Analysis** | MEDIUM | SonarQube | Identify untested areas |

**Why needed:** Coverage data combined with complexity creates powerful insights unique to Collider.

---

## COMPLETE GAP COVERAGE MATRIX

| Gap | Module | Priority |
|-----|--------|----------|
| Languages (5 → 15+) | M1 | HIGH |
| SAST/Security Rules | M2 | HIGH |
| CI/CD Integration | M3 | HIGH |
| IDE Plugins | M3 | HIGH |
| Export Formats (SARIF) | M4 | HIGH |
| Coupling/Cohesion | M5 | HIGH |
| Diff Visualization | M6 | HIGH |
| OWASP/PCI-DSS Compliance | M7 | HIGH |
| Code Smell Rules | M7 | HIGH |
| Cloud/SaaS Deployment | M8 | HIGH |
| PR Comments | M9 | HIGH |
| Team Dashboards | M9 | MEDIUM |
| Trend Charts | M10 | HIGH |
| Regression Detection | M10 | HIGH |
| Quality Gates | M11 | HIGH |
| Incremental Analysis | M12 | HIGH |
| REST API | M13 | HIGH |
| Clone Detection | M14 | MEDIUM |
| Test Coverage Import | M15 | HIGH |
| Coverage Overlay | M15 | MEDIUM |

**Total Gaps Identified:** 24
**Gaps Covered by M1-M15:** 24 (100%)

---

## IMPLEMENTATION PRIORITY MATRIX

```
                           HIGH VALUE
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      │  M3: GitHub CI    ★    │   ★   M1: Languages    │
      │  M4: SARIF             │       M3: VS Code      │
      │  M11: Quality Gates    │       M8: Docker       │
      │  M12: Incremental      │       M2: SAST         │
      │                        │                        │
 LOW ─┼────────────────────────┼────────────────────────┼─ HIGH
EFFORT                         │                        EFFORT
      │                        │                        │
      │  M6: Diff View         │       M7: Compliance   │
      │  M15: Coverage Import  │       M8: SaaS         │
      │  M9: PR Comments       │       M10: Dashboards  │
      │                        │       M13: REST API    │
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               │
                           LOW VALUE
```

**Recommended Implementation Phases:**

### Phase 1: CI Adoption (M3, M4, M11, M12)
Quick wins that enable CI/CD integration:
1. **M3: GitHub Actions** - Low effort, high visibility
2. **M4: SARIF Export** - Enables GitHub Security tab
3. **M11: Quality Gates** - Pass/fail thresholds
4. **M12: Incremental** - Fast re-analysis for PRs

### Phase 2: Developer Experience (M1, M3-IDE, M6)
Expand reach and usability:
5. **M1: Java/C++ Support** - Largest language gaps
6. **M3: VS Code Extension** - IDE integration
7. **M6: Diff Visualization** - Compare analyses

### Phase 3: Security & Compliance (M2, M7)
Enterprise requirements:
8. **M2: SAST Scanner** - Security rules
9. **M7: OWASP/PCI-DSS** - Compliance certification

### Phase 4: Platform Features (M8, M9, M10, M13)
Team and enterprise scale:
10. **M8: Cloud/SaaS** - Hosted deployment
11. **M9: Collaboration** - PR comments, team dashboards
12. **M10: Historical Trends** - Time-series analysis
13. **M13: REST API** - Programmatic access

### Phase 5: Advanced Features (M5, M14, M15)
Differentiation and depth:
14. **M5: Coupling/Cohesion** - Architecture metrics
15. **M14: Clone Detection** - DRY violations
16. **M15: Test Coverage** - Coverage overlay on 3D graph

---

## SUCCESS METRICS

### Current Baseline

| Metric | Current | Target (6mo) | Target (12mo) | Target (24mo) |
|--------|---------|--------------|---------------|---------------|
| Languages | 5 | 10 | 15 | 20 |
| CI/CD Integrations | 0 | 2 | 4 | 4 |
| IDE Plugins | 0 | 1 | 2 | 3 |
| Security Rules | 0 | 50 | 200 | 500 |
| Export Formats | 2 (JSON, HTML) | 4 | 6 | 8 |
| Modules Implemented | 0/15 | 4/15 | 8/15 | 15/15 |
| API Endpoints | 0 | 0 | 10 | 50 |
| Team Features | 0 | 0 | 3 | 10 |

### Module Implementation Tracking

| Module | Status | Target |
|--------|--------|--------|
| M1: Languages | 5/20 | 6mo: 10, 12mo: 15 |
| M2: Security | 0% | 6mo: SAST basics |
| M3: Integrations | 0% | 6mo: GitHub Actions + SARIF |
| M4: Export | 33% | 6mo: SARIF |
| M5: Analysis | 0% | 12mo: Coupling |
| M6: Visualization | 0% | 6mo: Diff view |
| M7: Compliance | 0% | 12mo: OWASP Top 10 |
| M8: Cloud/SaaS | 0% | 12mo: Docker |
| M9: Collaboration | 0% | 12mo: PR comments |
| M10: Trends | 0% | 18mo: Basic charts |
| M11: Quality Gates | 0% | 6mo: Pass/fail |
| M12: Incremental | 0% | 6mo: Diff-only |
| M13: API/SDK | 0% | 12mo: REST API |
| M14: Duplicates | 0% | 18mo: Clone detection |
| M15: Coverage | 0% | 12mo: Import |

### Competitive Parity Checklist

**Phase 1 (CI Adoption):**
- [ ] GitHub Actions integration (M3)
- [ ] SARIF export for GitHub Security (M4)
- [ ] Quality gates - pass/fail thresholds (M11)
- [ ] Incremental analysis for PRs (M12)

**Phase 2 (Developer Experience):**
- [ ] Language coverage ≥ 15 (M1)
- [ ] VS Code extension (M3)
- [ ] Diff visualization (M6)

**Phase 3 (Security & Compliance):**
- [ ] Basic SAST rules - OWASP Top 10 (M2)
- [ ] Compliance rules - PCI-DSS basics (M7)
- [ ] False positive tuning (M7)

**Phase 4 (Platform Features):**
- [ ] Docker self-hosted deployment (M8)
- [ ] PR auto-comments (M9)
- [ ] Historical trend charts (M10)
- [ ] REST API (M13)

**Phase 5 (Advanced Features):**
- [ ] Coupling/cohesion metrics (M5)
- [ ] Clone detection (M14)
- [ ] Test coverage overlay (M15)

---

## STRATEGIC POSITIONING

### Don't Compete, Complement

Collider should NOT try to replace SonarQube/Snyk. Instead:

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                        │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Snyk    │    │ SonarQube│    │ Collider │              │
│  │ Security │    │ Quality  │    │ Architect│              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  "Is it secure?"  "Is it clean?" "What IS it?"             │
│                                   "How does it work?"       │
│                                   "What's the architecture?"│
└─────────────────────────────────────────────────────────────┘
```

### Unique Value Proposition

> **Collider is the only tool that treats code as a physical system with measurable properties across 8 dimensions, visualized in 3D, grounded in theory.**

This is NOT something SonarQube, Semgrep, or any competitor offers.

---

## DOCUMENT HISTORY

| Date | Change |
|------|--------|
| 2026-01-22 | Initial creation with competitive analysis and 6-module roadmap |
| 2026-01-22 | Expanded to 15 modules (M1-M15) covering all 24 identified gaps |
| 2026-01-22 | Added market research: $554M market size, detailed competitor profiles, pricing, feature matrices |
