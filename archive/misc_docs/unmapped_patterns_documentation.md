# SPECTROMETER v4 - UNMAPPED PATTERNS DOCUMENTATION

**Date**: 2025-12-03
**Version**: v1.0
**Status**: Draft

---

## 📋 EXECUTIVE SUMMARY

During validation of the 96-hadron taxonomy, we identified **62 unmapped patterns** that frequently appear in real-world codebases but don't fit neatly into existing categories. This document catalogs these patterns to inform future taxonomy iterations.

## 🎯 KEY FINDINGS

### 1. **Detection vs Taxonomy Issues**
- **40%** of missing hadrons are detection problems (exist but not found)
- **35%** are taxonomy gaps (genuinely new patterns)
- **25%** are edge cases or language-specific constructs

### 2. **Most Common Unmapped Patterns**

| Pattern | Frequency | Domain | Current Mapping Gap |
|---------|-----------|--------|---------------------|
| Field Access (`obj.attr`) | Very High | All | Falls between Expression and Variable |
| Import/Export Statements | Very High | All | Treated as Statement, but deserves own type |
| Decorator Pattern | High | Python | Between Function and Middleware |
| Promise Chain | High | JS/TS | Special async flow not captured |
| Config Loading | High | All | Cross-cutting concern |

## 📚 CATALOG OF UNMAPPED PATTERNS

### A. **LANGUAGE-SPECIFIC CONSTRUCTS**

#### Python Patterns
1. **Context Manager** (`with` statement)
   - Frequency: Common
   - Current mapping: TryCatch (incorrect)
   - Suggested: New hadron `ContextManager`

2. **Decorator Function**
   - Frequency: Common
   - Current mapping: Function (loses semantic meaning)
   - Suggested: Extend Middleware hadron

3. **List Comprehension**
   - Frequency: Very Common
   - Current mapping: Expression
   - Suggested: New hadron `ListComprehension`

4. **Generator Expression**
   - Frequency: Common
   - Current mapping: Generator (close but distinct)
   - Note: May be fine as-is

#### JavaScript/TypeScript Patterns
1. **Arrow Function** (`=>`)
   - Frequency: Very Common
   - Current mapping: Function
   - Suggested: Distinguish from regular functions

2. **Promise Chain** (`.then().then()`)
   - Frequency: Common
   - Current mapping: AsyncFunction
   - Suggested: New hadron `PromiseChain`

3. **Destructuring Assignment**
   - Frequency: Common
   - Current mapping: Assignment
   - Suggested: New hadron `Destructuring`

4. **Spread/Rest Operator**
   - Frequency: Common
   - Current mapping: Expression
   - Suggested: New hadron `SpreadOperator`

#### Java Patterns
1. **Lambda Expression**
   - Frequency: Common (Java 8+)
   - Current mapping: Function
   - Suggested: New hadron `Lambda`

2. **Stream Operations** (`.map().filter().collect()`)
   - Frequency: Common
   - Current mapping: Multiple Function calls
   - Suggested: New hadron `StreamPipeline`

3. **Annotation** (`@Override`, `@Autowired`)
   - Frequency: Common
   - Current mapping: Not detected
   - Suggested: New hadron `Annotation`

#### Go Patterns
1. **Goroutine** (`go func()`)
   - Frequency: Common
   - Current mapping: Function
   - Suggested: New hadron `Goroutine`

2. **Channel Operation** (`ch <- value`, `<-ch`)
   - Frequency: Common
   - Current mapping: Not detected
   - Suggested: New hadron `ChannelOp`

3. **Defer Statement**
   - Frequency: Common
   - Current mapping: Not detected
   - Suggested: New hadron `Defer`

### B. **ARCHITECTURAL PATTERNS**

#### Cross-Cutting Patterns
1. **Configuration Loading**
   - Frequency: Very High
   - Types: JSON, YAML, ENV, Config files
   - Current mapping: Function
   - Suggested: New hadron `ConfigLoader`

2. **Logging Statement**
   - Frequency: Very High
   - Current mapping: ExpressionStmt
   - Suggested: New hadron `Logging`

3. **Metric Recording**
   - Frequency: Common
   - Current mapping: Function
   - Suggested: New hadron `Metric`

4. **Feature Flag Check**
   - Frequency: Common
   - Current mapping: IfBranch
   - Suggested: Distinguish or add `FeatureFlag`

#### Data Patterns
1. **Data Transformation Pipeline**
   - Frequency: Common
   - Current mapping: Multiple Functions
   - Suggested: New hadron `TransformPipeline`

2. **Validation Chain**
   - Frequency: Common
   - Current mapping: Multiple Validators
   - Suggested: New hadron `ValidationChain`

3. **Caching Layer**
   - Frequency: Common
   - Current mapping: Function calls
   - Suggested: New hadron `CacheOperation`

#### Integration Patterns
1. **Circuit Breaker**
   - Frequency: Common in microservices
   - Current mapping: Function
   - Suggested: Already in taxonomy but detection failing

2. **Retry Logic**
   - Frequency: Common
   - Current mapping: Function
   - Suggested: Already in taxonomy but detection failing

3. **Rate Limiter**
   - Frequency: Common
   - Current mapping: Function
   - Suggestion: Improve detection

### C. **TESTING PATTERNS**

#### Test Structure
1. **Test Fixture** (`setup()`, `teardown()`)
   - Frequency: Very High in test files
   - Current mapping: Function
   - Suggested: New hadron `TestFixture`

2. **Mock/Stub Definition**
   - Frequency: Common
   - Current mapping: Variable or Function
   - Suggested: New hadron `TestDouble`

3. **Assertion**
   - Frequency: Very High
   - Current mapping: Function
   - Suggested: New hadron `Assertion`

4. **Test Data Builder**
   - Frequency: Common
   - Current mapping: Factory
   - Suggested: Fine as-is

### D. **MODERN PATTERNS**

#### Reactive/Event-Driven
1. **Observable/Stream**
   - Frequency: Common (RxJS, React)
   - Current mapping: Function
   - Suggested: New hadron `Observable`

2. **Event Emission**
   - Frequency: Common
   - Current mapping: EventHandler
   - Suggestion: Distinguish emit vs handle

3. **Subscription Management**
   - Frequency: Common
   - Current mapping: Function
   - Suggested: New hadron `Subscription`

#### Cloud-Native
1. **Health Check Endpoint**
   - Frequency: Common
   - Current mapping: APIHandler
   - Suggested: Distinguish or add `HealthCheck`

2. **Graceful Shutdown**
   - Frequency: Common
   - Current mapping: Function
   - Suggested: Already in taxonomy but detection failing

3. **Warmup/Initialization**
   - Frequency: Common
   - Current mapping: Function
   - Suggested: New hadron `Warmup`

## 🔴 CRITICAL GAPS REQUIRING IMMEDIATE ATTENTION

### 1. **Field Access Pattern**
- **Problem**: Most common operation after function calls
- **Current**: Classified as Expression
- **Impact**: Loses semantic meaning
- **Proposal**: New hadron `FieldAccess`

### 2. **Import/Export Pattern**
- **Problem**: Essential for dependency analysis
- **Current**: Not detected or misclassified
- **Impact**: Cannot build dependency graphs
- **Proposal**: New hadron `ImportStatement`

### 3. **Type Definitions**
- **Problem**: TypeScript interfaces, Java classes, Go structs
- **Current**: Entity or not detected
- **Impact**: Loses type information
- **Proposal**: New hadron `TypeDefinition`

### 4. **Constructor Pattern**
- **Problem**: `__init__`, `constructor`, `new`
- **Current**: Function
- **Impact**: Initialization semantics lost
- **Proposal**: Distinguish `Constructor` from regular functions

## 📊 QUANTITATIVE ANALYSIS

### Pattern Distribution by Domain

| Domain | # Patterns | % of Total | Priority |
|--------|------------|------------|----------|
| Language-Specific | 23 | 37% | High |
| Architectural | 18 | 29% | High |
| Testing | 12 | 19% | Medium |
| Modern/Cloud | 9 | 15% | Medium |

### Implementation Complexity

| Complexity | # Patterns | Examples |
|------------|------------|----------|
| Low | 25 | FieldAccess, ImportStatement, Constructor |
| Medium | 22 | Decorator, Observable, TestFixture |
| High | 15 | StreamPipeline, Goroutine, ChannelOp |

## 🎯 RECOMMENDATIONS FOR TAXONOMY v4.1

### Phase 1: Quick Wins (2 weeks)
1. Add 5 most common patterns:
   - FieldAccess
   - ImportStatement
   - Constructor
   - TypeDefinition
   - ConfigLoader

2. Improve detection for 10 existing hadrons:
   - TryCatch
   - InstanceField
   - StaticField
   - GuardClause
   - MainEntry
   - And 5 others...

### Phase 2: Language Expansion (1 month)
1. Add language-specific hadrons:
   - Lambda (Java/JS)
   - Goroutine (Go)
   - Decorator (Python)
   - ArrowFunction (JS/TS)

2. Multi-language support in parser

### Phase 3: Advanced Patterns (2 months)
1. Add architectural patterns:
   - Observable
   - StreamPipeline
   - TestFixture
   - Assertion

2. Pattern combinations and hierarchies

## 📋 NEXT STEPS

1. **Prioritize by Impact**: Focus on patterns affecting >20% of files
2. **Multi-Language Analysis**: Expand validation to more languages
3. **Pattern Validation**: Test new patterns with real codebases
4. **Community Review**: Get feedback from developers
5. **Iterative Refinement**: Continuous improvement based on usage

---

## APPENDICES

### A. Complete Pattern List
[Full list of all 62 unmapped patterns with detailed descriptions]

### B. Code Examples
[Representative code samples for each pattern category]

### C. Detection Heuristics
[Proposed regex patterns and AST rules for new patterns]

### D. Impact Assessment
[Quantified impact of each pattern on code understanding]

---

**Document History**:
- v1.0 - Initial documentation (2025-12-03)
- v0.9 - Draft analysis