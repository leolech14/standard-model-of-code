# Component C3: Annotated Training Corpus Roadmap

> **Goal**: Create an annotated corpus of real code labeled with Standard Model classifications for AI training
> **Priority**: ★★★★★ Critical Path
> **Estimated Duration**: Week 3-6

---

## Current State

| Metric | Current | Target |
|--------|---------|--------|
| Annotated particles | 0 | 10,000 |
| Human-verified samples | 0 | 1,000 |
| Repositories analyzed | 0 | 10+ |
| Classification accuracy | Unknown | >90% |
| Languages covered | 0 | 5 (Python, TS, Java, Go, Rust) |

---

## Phase 0: Pre-Development Research

### 0.1 Select Target Repositories (Day 1)

**Objective**: Choose diverse, well-maintained open-source codebases.

**Selection Criteria**:
- Active maintenance (commits in last 3 months)
- Good documentation and code quality
- Representative of enterprise patterns
- Permissive license (MIT, Apache, BSD)
- Significant size (>10,000 LOC)

**Proposed Repository List**:

| Repository | Language | Domain | Stars | Why |
|------------|----------|--------|-------|-----|
| `django/django` | Python | Web Framework | 75k+ | Clean architecture, REST patterns |
| `pallets/flask` | Python | Micro-framework | 65k+ | Simple, well-factored |
| `microsoft/vscode` | TypeScript | Desktop App | 150k+ | Large-scale TS |
| `facebook/react` | TypeScript/JS | UI Library | 200k+ | Component patterns |
| `vercel/next.js` | TypeScript | Full-stack | 115k+ | Modern full-stack |
| `kubernetes/kubernetes` | Go | Infrastructure | 100k+ | Systems programming |
| `gin-gonic/gin` | Go | Web Framework | 70k+ | Clean Go patterns |
| `spring-projects/spring-boot` | Java | Enterprise | 70k+ | DDD patterns |
| `rust-lang/rust` | Rust | Compiler | 85k+ | Low-level systems |
| `tokio-rs/tokio` | Rust | Async Runtime | 20k+ | Modern Rust |

**Deliverable**: `data/REPOSITORY_SELECTION.md` with final choices

---

### 0.2 Define Annotation Schema (Day 2)

**Objective**: Define how training samples are structured.

**Sample Structure**:
```yaml
# data/training/django_orm_query_001.yaml
sample_id: "django_orm_query_001"
source:
  repository: "django/django"
  commit: "abc123..."
  file: "django/db/models/query.py"
  function: "QuerySet.filter"
  lines: [245, 289]

code: |
  def filter(self, *args, **kwargs):
      """
      Return a new QuerySet instance with the args ANDed to the existing
      set.
      """
      self._not_support_combined_queries('filter')
      return self._filter_or_exclude(False, args, kwargs)

ground_truth:
  atom: "Fn_Method"
  dimensions:
    D1_WHAT: "Fn_Method"
    D2_LAYER: "Core"
    D3_ROLE: "Query"
    D4_BOUNDARY: "Internal"
    D5_STATE: "Stateless"
    D6_EFFECT: "Read"
    D7_LIFECYCLE: "Use"
    D8_TRUST: 95
  level: "L3"
  plane: "Semantic"
  tau: "τ(Method:Query:Core:Int:SL:R:U:95)"

collider_output:
  # Collider's automated classification (for comparison)
  atom: "Fn_Method"
  dimensions:
    D2_LAYER: "Core"
    D3_ROLE: "Query"
    # ... etc
  confidence: 0.87

verification:
  verified_by: "human"  # or "automated"
  verifier_id: "reviewer_001"
  verification_date: "2026-01-10"
  agreement: true  # Ground truth matches collider output?
  notes: "Clear query pattern, no side effects"
```

**Deliverable**: `data/ANNOTATION_SCHEMA.yaml`

---

### 0.3 Create Annotation Guidelines (Day 3)

**Objective**: Write clear guidelines for human annotators.

**Guidelines Document Structure**:
1. **Introduction**: What is the Standard Model, why annotate?
2. **Dimension Definitions**: How to classify each D1-D8
3. **Role Cheat Sheet**: When to use each of the 33 roles
4. **Layer Decision Tree**: Flowchart for determining layer
5. **Common Patterns**: Examples for each category
6. **Edge Cases**: How to handle ambiguity
7. **Quality Checks**: Self-review checklist

**Key Decision Trees**:

```
D2 LAYER Decision Tree:
┌─────────────────────────────────────────────────────────────┐
│ Does it handle HTTP/UI/CLI directly?                        │
│   YES → INTERFACE                                           │
│   NO ↓                                                      │
│ Does it orchestrate use cases / application logic?          │
│   YES → APPLICATION                                         │
│   NO ↓                                                      │
│ Does it contain domain/business rules?                      │
│   YES → CORE                                                │
│   NO ↓                                                      │
│ Does it interact with external systems (DB, APIs, files)?   │
│   YES → INFRASTRUCTURE                                      │
│   NO ↓                                                      │
│ Is it a test?                                               │
│   YES → TEST                                                │
│   NO → CORE (default for utility)                           │
└─────────────────────────────────────────────────────────────┘
```

**Deliverable**: `data/ANNOTATION_GUIDELINES.md`

---

## Phase 1: Automated Labeling (Week 3-4)

### 1.1 Clone and Prepare Repositories (Day 4)

**Objective**: Set up local copies for analysis.

**Actions**:
```bash
mkdir -p data/repos
cd data/repos

# Clone selected repositories
git clone --depth 1 https://github.com/django/django
git clone --depth 1 https://github.com/pallets/flask
git clone --depth 1 https://github.com/microsoft/vscode
git clone --depth 1 https://github.com/facebook/react
git clone --depth 1 https://github.com/kubernetes/kubernetes
git clone --depth 1 https://github.com/spring-projects/spring-boot
git clone --depth 1 https://github.com/tokio-rs/tokio

# Note commit hashes for reproducibility
for dir in */; do
  echo "$dir: $(cd $dir && git rev-parse HEAD)" >> ../COMMIT_HASHES.txt
done
```

**Deliverable**: `data/repos/` with cloned repositories, `data/COMMIT_HASHES.txt`

---

### 1.2 Run Collider Analysis (Day 5-7)

**Objective**: Generate automated classifications for all repositories.

**Batch Processing Script**:
```bash
#!/bin/bash
# scripts/batch_analyze.sh

REPOS=(django flask vscode react kubernetes spring-boot tokio)

for repo in "${REPOS[@]}"; do
  echo "Analyzing $repo..."
  python -m collider analyze \
    --input "data/repos/$repo" \
    --output "data/analysis/$repo" \
    --format json \
    --include-source \
    --max-particles 5000
done
```

**Expected Output**:
```
data/analysis/
├── django/
│   ├── unified_analysis.json    # Full graph
│   ├── particles.jsonl          # One particle per line
│   └── statistics.json          # Summary stats
├── flask/
│   └── ...
└── ...
```

**Deliverable**: `data/analysis/` with Collider outputs for all repos

---

### 1.3 Generate Training Samples (Day 8-9)

**Objective**: Extract and format training samples.

**Extraction Script**:
```python
# scripts/extract_training_samples.py

import json
from pathlib import Path

def extract_samples(analysis_dir: Path, output_dir: Path, sample_size: int = 1000):
    """Extract diverse training samples from Collider output."""
    
    # Load analysis
    with open(analysis_dir / "unified_analysis.json") as f:
        graph = json.load(f)
    
    particles = graph["particles"]
    
    # Stratified sampling to ensure diversity
    samples_by_layer = defaultdict(list)
    for p in particles:
        layer = p["dimensions"].get("D2_LAYER", "Unknown")
        samples_by_layer[layer].append(p)
    
    # Take proportional samples from each layer
    selected = []
    per_layer = sample_size // len(samples_by_layer)
    for layer, layer_particles in samples_by_layer.items():
        selected.extend(random.sample(layer_particles, min(per_layer, len(layer_particles))))
    
    # Write training samples
    for i, particle in enumerate(selected):
        sample = create_training_sample(particle)
        output_file = output_dir / f"{analysis_dir.name}_{i:04d}.yaml"
        write_yaml(sample, output_file)
    
    return len(selected)
```

**Deliverable**: `data/training/` with ~5000 auto-labeled samples

---

### 1.4 Quality Filtering (Day 10)

**Objective**: Remove low-confidence samples.

**Filters**:
1. **Confidence threshold**: Remove samples with D8_TRUST < 70%
2. **Edge count**: Remove orphan particles (no edges)
3. **Code quality**: Remove too-short (<3 lines) or too-long (>100 lines) samples
4. **Duplicate removal**: No duplicate particles across samples

**Deliverable**: Filtered `data/training/` with ~4000 high-quality samples

---

## Phase 2: Human Verification (Week 4-5)

### 2.1 Select Verification Sample (Day 11)

**Objective**: Choose 1000 samples for human review.

**Selection Strategy**:
- 200 samples per layer (Interface, Application, Core, Infrastructure, Test)
- 50 samples per role (top 10 most common roles)
- 100 edge cases (lowest confidence)
- 100 random stratified

**Deliverable**: `data/verification_queue/` with 1000 samples

---

### 2.2 Create Verification Interface (Day 12)

**Objective**: Build simple UI for verification.

**Options**:
1. **Spreadsheet approach**: Export to Google Sheets with dropdown validation
2. **CLI tool**: Interactive terminal reviewer
3. **Simple web app**: Local Flask app with forms

**Proposed CLI Tool**:
```python
# tools/verify_sample.py

def verify_sample(sample_path: Path):
    """Interactive verification of a single sample."""
    sample = load_yaml(sample_path)
    
    print(f"\n{'='*60}")
    print(f"Sample: {sample['sample_id']}")
    print(f"File: {sample['source']['file']}")
    print(f"{'='*60}")
    print(sample['code'])
    print(f"{'='*60}")
    
    print(f"\nCollider classified as:")
    print(f"  Atom: {sample['collider_output']['atom']}")
    print(f"  Layer: {sample['collider_output']['dimensions']['D2_LAYER']}")
    print(f"  Role: {sample['collider_output']['dimensions']['D3_ROLE']}")
    
    print("\nIs this correct? (y/n/edit)")
    response = input("> ")
    
    if response == 'y':
        sample['verification']['agreement'] = True
        # Copy collider output to ground truth
    elif response == 'edit':
        # Interactive edit of each dimension
        sample['ground_truth'] = edit_dimensions(sample)
    else:
        sample['verification']['agreement'] = False
        sample['ground_truth'] = edit_dimensions(sample)
    
    sample['verification']['verified_by'] = 'human'
    sample['verification']['verification_date'] = date.today().isoformat()
    save_yaml(sample, sample_path)
```

**Deliverable**: `tools/verify_sample.py`

---

### 2.3 Conduct Human Verification (Days 13-18)

**Objective**: Complete human review of 1000 samples.

**Workflow**:
1. Distribute samples among reviewers (if multiple)
2. Each reviewer processes ~50-100 samples/day
3. Track progress in `data/VERIFICATION_LOG.md`
4. Weekly sync to discuss edge cases

**Quality Metrics to Track**:
- Agreement rate (Collider vs Human)
- Disagreement patterns (which dimensions are most wrong?)
- Inter-annotator agreement (if multiple reviewers)

**Deliverable**: 1000 human-verified samples in `data/ground_truth/`

---

### 2.4 Compute Accuracy Metrics (Day 19)

**Objective**: Calculate Collider's baseline accuracy.

**Metrics Script**:
```python
# scripts/compute_accuracy.py

def compute_accuracy(ground_truth_dir: Path):
    """Compute per-dimension accuracy."""
    
    results = {
        'overall': {'correct': 0, 'total': 0},
        'per_dimension': {f'D{i}': {'correct': 0, 'total': 0} for i in range(1, 9)},
        'per_layer': {},
        'per_role': {},
        'confusion_matrices': {}
    }
    
    for sample_file in ground_truth_dir.glob("*.yaml"):
        sample = load_yaml(sample_file)
        gt = sample['ground_truth']['dimensions']
        pred = sample['collider_output']['dimensions']
        
        for dim in ['D2_LAYER', 'D3_ROLE', 'D4_BOUNDARY', 'D5_STATE', 'D6_EFFECT']:
            results['per_dimension'][dim]['total'] += 1
            if gt.get(dim) == pred.get(dim):
                results['per_dimension'][dim]['correct'] += 1
    
    # Compute percentages
    for dim, data in results['per_dimension'].items():
        data['accuracy'] = data['correct'] / data['total'] if data['total'] > 0 else 0
    
    return results
```

**Expected Output**:
```json
{
  "overall_accuracy": 0.847,
  "per_dimension": {
    "D1_WHAT": {"accuracy": 0.98, "note": "AST-based, very reliable"},
    "D2_LAYER": {"accuracy": 0.82, "note": "Hardest to infer"},
    "D3_ROLE": {"accuracy": 0.78, "note": "Pattern matching good but not perfect"},
    "D4_BOUNDARY": {"accuracy": 0.91, "note": "I-O detection reliable"},
    "D5_STATE": {"accuracy": 0.94, "note": "self/this detection good"},
    "D6_EFFECT": {"accuracy": 0.87, "note": "Side effect detection improving"},
    "D7_LIFECYCLE": {"accuracy": 0.89, "note": "init/del patterns clear"},
    "D8_TRUST": "N/A"
  },
  "biggest_confusion": {
    "D2_LAYER": "Application vs Core (45% of errors)",
    "D3_ROLE": "Service vs Utility (30% of errors)"
  }
}
```

**Deliverable**: `benchmarks/accuracy.json`

---

## Phase 3: Dataset Finalization (Week 5-6)

### 3.1 Error Analysis (Day 20)

**Objective**: Understand and document error patterns.

**Analysis Report**:
```markdown
# Error Analysis Report

## Summary
- 1000 samples verified
- 847 correct (84.7%)
- 153 errors (15.3%)

## Error Distribution by Dimension
| Dimension | Error Rate | Most Common Error |
|-----------|------------|-------------------|
| D2_LAYER | 18% | Application↔Core confusion |
| D3_ROLE | 22% | Service↔Utility confusion |
| D4_BOUNDARY | 9% | Missing I-O detection |
| D5_STATE | 6% | Closure state missed |
| D6_EFFECT | 13% | Indirect write missed |

## Top Error Patterns

### 1. Application vs Core Confusion (45% of D2 errors)
**Pattern**: Methods that orchestrate domain logic but also contain business rules
**Example**: `UserService.create_user()` - Is it Application (orchestration) or Core (business rule)?
**Root Cause**: Clean Architecture boundary is contextual

### 2. Service vs Utility Confusion (30% of D3 errors)
**Pattern**: Stateless helpers that could be either
**Example**: `format_date()` - Is it a Service (has purpose) or Utility (generic)?
**Root Cause**: Naming convention missing, context needed

## Recommendations for Collider Improvement
1. Add file path heuristics for layer detection
2. Look for DDD naming patterns (Repository, Factory, etc.)
3. Check for external dependencies to infer I-O boundary
```

**Deliverable**: `benchmarks/ERROR_ANALYSIS.md`

---

### 3.2 Update Collider Based on Findings (Day 21-22)

**Objective**: Improve Collider using error analysis.

**Improvements to Implement**:
1. Better layer detection from file paths
2. Role detection from naming patterns
3. Improved boundary detection
4. Edge case handling

**Deliverable**: Updated Collider with improvements

---

### 3.3 Re-run Analysis (Day 23)

**Objective**: Re-analyze with improved Collider.

**Actions**:
1. Re-run Collider on all repositories
2. Re-compute accuracy metrics
3. Verify improvement

**Target**: Improve from 84.7% to >90% accuracy

**Deliverable**: Updated `benchmarks/accuracy_v2.json`

---

### 3.4 Package Final Dataset (Day 24-25)

**Objective**: Create the final training corpus release.

**Final Dataset Structure**:
```
data/
├── README.md                    # Dataset documentation
├── LICENSE                      # CC-BY-4.0 or similar
├── METADATA.json                # Version, stats, provenance
├── training/
│   ├── all_samples.jsonl        # 10,000 particles (one per line)
│   ├── by_layer/                # Split by layer
│   ├── by_language/             # Split by language
│   └── by_role/                 # Split by role
├── ground_truth/
│   ├── verified_1000.jsonl      # Human-verified subset
│   └── annotations.json         # Raw annotation data
├── benchmarks/
│   ├── accuracy.json            # Accuracy metrics
│   ├── confusion_matrices/      # Per-dimension confusion
│   └── ERROR_ANALYSIS.md        # Detailed error analysis
└── analysis/
    └── [per-repo outputs]       # Full Collider outputs
```

**Deliverable**: Complete `data/` directory ready for release

---

## Deliverables Summary

| Deliverable | Path | Description |
|-------------|------|-------------|
| Repository Selection | `data/REPOSITORY_SELECTION.md` | 10 chosen repos |
| Annotation Schema | `data/ANNOTATION_SCHEMA.yaml` | Sample structure |
| Annotation Guidelines | `data/ANNOTATION_GUIDELINES.md` | Human reviewer guide |
| Cloned Repositories | `data/repos/` | Local copies |
| Collider Analysis | `data/analysis/` | Raw outputs |
| Training Samples | `data/training/` | 10,000 auto-labeled |
| Ground Truth | `data/ground_truth/` | 1,000 human-verified |
| Accuracy Metrics | `benchmarks/accuracy.json` | Classification accuracy |
| Error Analysis | `benchmarks/ERROR_ANALYSIS.md` | Error patterns |
| Final Dataset | `data/` | Packaged for release |

---

## Success Criteria

- [ ] 10+ repositories analyzed
- [ ] 10,000+ training samples generated
- [ ] 1,000 human-verified samples
- [ ] Classification accuracy >90%
- [ ] Error analysis complete
- [ ] Dataset packaged and documented
- [ ] Reproducible (commit hashes, scripts)

---

## Dependencies

- **Depends on**: 
  - C1 (Atom Enumeration) - need complete atom list
  - C2 (JSON Schema) - samples must follow schema
- **Blocks**: Nothing - this is the final component
- **Parallel**: Can begin repository cloning immediately

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low Collider accuracy | High | Iterate on improvements before human verification |
| Human verification slow | Medium | Parallelize with multiple reviewers |
| Repository license issues | Low | Check licenses before cloning |
| Too diverse/noisy data | Medium | Focus on high-quality repos only |
| Annotation disagreement | Medium | Create decision trees, regular syncs |

---

## Budget (if applicable)

| Item | Estimated Cost | Notes |
|------|----------------|-------|
| Human annotation (1000 samples) | $500-1000 | If outsourced (~$0.50-1/sample) |
| Compute for Collider | Minimal | Local or small cloud instance |
| Storage | Minimal | <10GB total |
| **Total** | ~$500-1000 | Most work can be done internally |
