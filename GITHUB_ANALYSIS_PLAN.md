# 🎯 GITHUB REPO ANALYSIS PLAN
**9 Top Repositories - Structured Analysis**
**Date**: 2025-12-27

---

## 📋 EXECUTION PLAN

### Phase 0: Pre-Flight Checks ✈️

**Goal**: Verify pipeline is production-ready

- [x] Pipeline works end-to-end (verified in END_TO_END_VERIFICATION.md)
- [ ] Test on small sample first
- [ ] Check available disk space (~5 GB needed)
- [ ] Verify Python dependencies
- [ ] Create directory structure
- [ ] Create automation scripts

**Estimated Time**: 30 minutes

---

### Phase 1: Setup & Infrastructure 🏗️

#### Task 1.1: Create Directory Structure

```bash
mkdir -p github_analysis/{repos,outputs,reports}
mkdir -p github_analysis/outputs/{django,fastapi,express,pandas,lodash,react,vue,requests,sqlalchemy}
```

#### Task 1.2: Clone Repositories

```bash
cd github_analysis/repos

# Python repos (our parser works best)
git clone --depth=1 https://github.com/django/django.git
git clone --depth=1 https://github.com/tiangolo/fastapi.git
git clone --depth=1 https://github.com/pandas-dev/pandas.git
git clone --depth=1 https://github.com/psf/requests.git
git clone --depth=1 https://github.com/sqlalchemy/sqlalchemy.git

# JavaScript repos (partial support)
git clone --depth=1 https://github.com/expressjs/express.git
git clone --depth=1 https://github.com/lodash/lodash.git
git clone --depth=1 https://github.com/facebook/react.git
git clone --depth=1 https://github.com/vuejs/core.git
```

**Estimated Time**: 10 minutes (depends on network)

#### Task 1.3: Create Automation Scripts

**Script 1: `analyze_repo.sh`**
```bash
#!/bin/bash
# Analyze a single repository

REPO_NAME=$1
REPO_PATH=$2
OUTPUT_DIR=$3

echo "🔬 Analyzing: $REPO_NAME"
echo "   Path: $REPO_PATH"
echo "   Output: $OUTPUT_DIR"

# Run Collider
python src/core/unified_analysis.py "$REPO_PATH" \
  --output "$OUTPUT_DIR/unified_analysis.json"

# Generate quick stats
cat "$OUTPUT_DIR/unified_analysis.json" | jq '{
  repo: "'$REPO_NAME'",
  nodes: .metadata.node_count,
  edges: .metadata.edge_count,
  analysis_time_ms: .metadata.analysis_time_ms,
  stateless_pct: ((.nodes | map(select(.dimensions.D5_STATE == "Stateless")) | length) / .metadata.node_count * 100),
  pure_pct: ((.nodes | map(select(.dimensions.D6_EFFECT == "Pure")) | length) / .metadata.node_count * 100),
  doc_coverage: .statistics.documentation_coverage
}' > "$OUTPUT_DIR/quick_stats.json"

echo "✅ Complete: $REPO_NAME"
```

**Script 2: `analyze_all.sh`**
```bash
#!/bin/bash
# Analyze all 9 repositories in sequence

REPOS=(
  "django:repos/django/django"
  "fastapi:repos/fastapi/fastapi"
  "express:repos/express/lib"
  "pandas:repos/pandas/pandas"
  "lodash:repos/lodash"
  "react:repos/react/packages/react/src"
  "vue:repos/core/packages/vue/src"
  "requests:repos/requests/requests"
  "sqlalchemy:repos/sqlalchemy/lib/sqlalchemy"
)

for repo_spec in "${REPOS[@]}"; do
  IFS=':' read -r name path <<< "$repo_spec"
  ./analyze_repo.sh "$name" "github_analysis/$path" "github_analysis/outputs/$name"
done

# Generate comparative report
python scripts/generate_comparative_report.py
```

**Script 3: `generate_comparative_report.py`**
```python
#!/usr/bin/env python3
"""Generate comparative analysis report from all 9 repos."""

import json
from pathlib import Path
from typing import List, Dict

def load_analysis(repo_name: str) -> Dict:
    """Load analysis for a repo."""
    path = Path(f"github_analysis/outputs/{repo_name}/unified_analysis.json")
    with open(path) as f:
        return json.load(f)

def calculate_metrics(data: Dict) -> Dict:
    """Calculate key metrics."""
    nodes = data['nodes']
    total = len(nodes)

    if total == 0:
        return {}

    return {
        'total_nodes': total,
        'total_edges': len(data.get('edges', [])),
        'stateless_pct': len([n for n in nodes if n.get('dimensions', {}).get('D5_STATE') == 'Stateless']) / total * 100,
        'pure_pct': len([n for n in nodes if n.get('dimensions', {}).get('D6_EFFECT') == 'Pure']) / total * 100,
        'internal_pct': len([n for n in nodes if n.get('dimensions', {}).get('D4_BOUNDARY') == 'Internal']) / total * 100,
        'high_confidence_pct': len([n for n in nodes if n.get('lenses', {}).get('R8_EPISTEMOLOGY', {}).get('confidence', 0) > 70]) / total * 100,
        'cacheable_count': len([n for n in nodes if
            n.get('dimensions', {}).get('D5_STATE') == 'Stateless' and
            n.get('dimensions', {}).get('D6_EFFECT') == 'Pure'
        ]),
        'security_critical_count': len([n for n in nodes if
            n.get('dimensions', {}).get('D4_BOUNDARY') in ['Output', 'I-O'] and
            n.get('dimensions', {}).get('D6_EFFECT') in ['Write', 'ReadModify']
        ])
    }

def main():
    repos = ['django', 'fastapi', 'express', 'pandas', 'lodash', 'react', 'vue', 'requests', 'sqlalchemy']

    results = []
    for repo in repos:
        try:
            data = load_analysis(repo)
            metrics = calculate_metrics(data)
            metrics['repo'] = repo
            results.append(metrics)
        except Exception as e:
            print(f"Error processing {repo}: {e}")

    # Generate markdown report
    report = generate_markdown_report(results)

    with open('github_analysis/reports/COMPARATIVE_ANALYSIS.md', 'w') as f:
        f.write(report)

    print("✅ Comparative report generated: github_analysis/reports/COMPARATIVE_ANALYSIS.md")

def generate_markdown_report(results: List[Dict]) -> str:
    """Generate markdown report."""
    md = "# 🔬 COMPARATIVE ANALYSIS - 9 GitHub Repositories\n\n"
    md += "**Date**: 2025-12-27\n"
    md += "**Analyzed with**: Collider v3.0.0 (8D + 8L)\n\n"
    md += "---\n\n"

    # Summary table
    md += "## 📊 SUMMARY TABLE\n\n"
    md += "| Repo | Nodes | Edges | Stateless% | Pure% | Internal% | High Confidence% |\n"
    md += "|------|-------|-------|------------|-------|-----------|------------------|\n"

    for r in results:
        md += f"| **{r['repo']}** | {r['total_nodes']:,} | {r['total_edges']:,} | "
        md += f"{r['stateless_pct']:.1f}% | {r['pure_pct']:.1f}% | "
        md += f"{r['internal_pct']:.1f}% | {r['high_confidence_pct']:.1f}% |\n"

    md += "\n---\n\n"

    # Rankings
    md += "## 🏆 RANKINGS\n\n"

    # Purity ranking
    md += "### Most Pure (D6 Effect)\n\n"
    sorted_pure = sorted(results, key=lambda x: x['pure_pct'], reverse=True)
    for i, r in enumerate(sorted_pure[:5], 1):
        md += f"{i}. **{r['repo']}**: {r['pure_pct']:.1f}% pure functions\n"

    md += "\n### Most Stateless (D5 State)\n\n"
    sorted_stateless = sorted(results, key=lambda x: x['stateless_pct'], reverse=True)
    for i, r in enumerate(sorted_stateless[:5], 1):
        md += f"{i}. **{r['repo']}**: {r['stateless_pct']:.1f}% stateless\n"

    md += "\n### Most Cacheable Functions\n\n"
    sorted_cacheable = sorted(results, key=lambda x: x['cacheable_count'], reverse=True)
    for i, r in enumerate(sorted_cacheable[:5], 1):
        md += f"{i}. **{r['repo']}**: {r['cacheable_count']:,} cacheable functions\n"

    md += "\n### Most Security-Critical\n\n"
    sorted_security = sorted(results, key=lambda x: x['security_critical_count'], reverse=True)
    for i, r in enumerate(sorted_security[:5], 1):
        md += f"{i}. **{r['repo']}**: {r['security_critical_count']:,} I/O write operations\n"

    return md

if __name__ == '__main__':
    main()
```

**Estimated Time**: 15 minutes

---

### Phase 2: Pre-Flight Test 🧪

**Test on small sample before big runs**

```bash
# Test pipeline on test_sample.py (we know this works)
python src/core/unified_analysis.py test_sample.py

# Check output
cat collider_output/unified_analysis.json | jq '.metadata'
```

**Success Criteria**:
- ✅ No errors
- ✅ 5 nodes extracted
- ✅ 3 edges extracted
- ✅ All 8 lenses present
- ✅ Output is valid JSON

**Estimated Time**: 2 minutes

---

### Phase 3: Analyze Python Repos 🐍

**Priority 1: Python repos (our parser works best here)**

#### Repo 1: Django (Largest - 300K LOC)

```bash
./analyze_repo.sh django github_analysis/repos/django/django github_analysis/outputs/django
```

**Expected**:
- Nodes: ~50,000 - 100,000
- Time: 3-10 minutes
- Insights: Layer distribution (Models, Views, Templates), DTO patterns

#### Repo 2: FastAPI (Medium - 30K LOC)

```bash
./analyze_repo.sh fastapi github_analysis/repos/fastapi/fastapi github_analysis/outputs/fastapi
```

**Expected**:
- Nodes: ~5,000 - 10,000
- Time: 30-60 seconds
- Insights: High purity, async patterns, type hints

#### Repo 4: Pandas (Largest - 400K LOC)

```bash
./analyze_repo.sh pandas github_analysis/repos/pandas/pandas github_analysis/outputs/pandas
```

**Expected**:
- Nodes: ~80,000 - 150,000
- Time: 5-15 minutes
- Insights: Pure transformations, stateless operations

#### Repo 8: Requests (Small - 20K LOC)

```bash
./analyze_repo.sh requests github_analysis/repos/requests/requests github_analysis/outputs/requests
```

**Expected**:
- Nodes: ~2,000 - 5,000
- Time: 20-40 seconds
- Insights: 100% boundary crossing (HTTP client)

#### Repo 9: SQLAlchemy (Large - 300K LOC)

```bash
./analyze_repo.sh sqlalchemy github_analysis/repos/sqlalchemy/lib/sqlalchemy github_analysis/outputs/sqlalchemy
```

**Expected**:
- Nodes: ~50,000 - 100,000
- Time: 3-10 minutes
- Insights: Stateful ORM, complex effects

**Estimated Time**: 20-45 minutes total

---

### Phase 4: Analyze JavaScript Repos 📜

**Priority 2: JavaScript repos (partial parser support)**

**Note**: Our tree-sitter parser has basic JS support. Results may be less complete than Python.

#### Repo 3: Express.js (10K LOC)

```bash
./analyze_repo.sh express github_analysis/repos/express/lib github_analysis/outputs/express
```

#### Repo 5: Lodash (15K LOC)

```bash
./analyze_repo.sh lodash github_analysis/repos/lodash github_analysis/outputs/lodash
```

**Expected**: 100% pure functions (the ideal codebase!)

#### Repo 6: React (200K LOC)

```bash
./analyze_repo.sh react github_analysis/repos/react/packages/react/src github_analysis/outputs/react
```

#### Repo 7: Vue.js (100K LOC)

```bash
./analyze_repo.sh vue github_analysis/repos/core/packages/vue/src github_analysis/outputs/vue
```

**Estimated Time**: 15-30 minutes total

---

### Phase 5: Generate Reports 📊

#### Task 5.1: Run Comparative Analysis

```bash
python scripts/generate_comparative_report.py
```

**Output**: `github_analysis/reports/COMPARATIVE_ANALYSIS.md`

#### Task 5.2: Generate Per-Repo Insights

For each repo, generate:
- Top 10 cacheable functions
- Security-critical operations
- Code quality metrics
- Architectural patterns

```bash
for repo in django fastapi express pandas lodash react vue requests sqlalchemy; do
  python scripts/generate_repo_insights.py "$repo"
done
```

**Estimated Time**: 10 minutes

---

## 📊 EXPECTED OUTPUTS

### Directory Structure After Completion

```
github_analysis/
├── repos/
│   ├── django/
│   ├── fastapi/
│   ├── express/
│   ├── pandas/
│   ├── lodash/
│   ├── react/
│   ├── vue/
│   ├── requests/
│   └── sqlalchemy/
├── outputs/
│   ├── django/
│   │   ├── unified_analysis.json
│   │   └── quick_stats.json
│   ├── fastapi/
│   │   ├── unified_analysis.json
│   │   └── quick_stats.json
│   └── ... (same for all 9)
└── reports/
    ├── COMPARATIVE_ANALYSIS.md
    ├── django_insights.md
    ├── fastapi_insights.md
    └── ... (9 total)
```

### Report Contents

**COMPARATIVE_ANALYSIS.md**:
- Summary table (all 9 repos)
- Rankings (purity, statefulness, cacheability, security)
- Architectural pattern comparison
- Best practices identified

**{repo}_insights.md** (per repo):
- Executive summary
- Top 10 cacheable functions
- Security-critical operations
- Code quality metrics (R8)
- Dimensional distribution (D1-D8)
- Actionable recommendations

---

## ⚙️ RESOURCE REQUIREMENTS

### Disk Space

| Repo | Clone Size | Output Size | Total |
|------|-----------|-------------|-------|
| Django | ~100 MB | ~50 MB | 150 MB |
| FastAPI | ~5 MB | ~5 MB | 10 MB |
| Express | ~3 MB | ~2 MB | 5 MB |
| Pandas | ~150 MB | ~100 MB | 250 MB |
| Lodash | ~10 MB | ~3 MB | 13 MB |
| React | ~50 MB | ~20 MB | 70 MB |
| Vue | ~30 MB | ~15 MB | 45 MB |
| Requests | ~5 MB | ~3 MB | 8 MB |
| SQLAlchemy | ~80 MB | ~50 MB | 130 MB |

**Total**: ~700 MB

### Time Estimates

| Phase | Time |
|-------|------|
| Setup | 30 min |
| Python repos | 20-45 min |
| JS repos | 15-30 min |
| Reports | 10 min |
| **Total** | **75-115 minutes** |

### CPU/Memory

- CPU: Standard (1 core per analysis)
- Memory: ~500 MB - 2 GB per analysis
- Parallelization: Can run multiple in parallel if desired

---

## 🚨 PRE-FLIGHT CHECKLIST

Before starting, verify:

- [ ] **Pipeline verified**: test_sample.py works ✅
- [ ] **Disk space**: 5+ GB available
- [ ] **Dependencies**: Python 3.8+, jq installed
- [ ] **Network**: Stable connection for cloning
- [ ] **Time**: 2+ hours available for full analysis
- [ ] **Directory**: Created github_analysis/ structure
- [ ] **Scripts**: Created automation scripts
- [ ] **Backup**: Current collider_output/ backed up

---

## 🎯 SUCCESS CRITERIA

**Analysis Complete When**:
- ✅ All 9 repos analyzed without errors
- ✅ All outputs generated (18 JSON files minimum)
- ✅ Comparative report created
- ✅ Per-repo insights generated
- ✅ No crashes, no data loss

**Quality Metrics**:
- All analyses have > 0 nodes
- All JSON files valid
- All 8 lenses present in outputs
- Edge extraction working

---

## 🔄 ROLLBACK PLAN

**If something fails**:

1. **Single repo fails**: Skip and continue with others
2. **Parser crashes**: Use fallback AST parser
3. **Out of memory**: Analyze smaller subset of files
4. **Out of disk**: Clean up intermediate files
5. **Out of time**: Prioritize Python repos (1, 2, 4, 8, 9)

---

## 📋 EXECUTION ORDER

**Recommended sequence**:

1. ✅ Setup & Scripts (30 min)
2. ✅ Pre-flight test (2 min)
3. 🐍 FastAPI (fastest, validates setup) - 1 min
4. 🐍 Requests (small, clean) - 1 min
5. 🐍 Django (large, tests scale) - 5-10 min
6. 🐍 Pandas (largest, stress test) - 10-15 min
7. 🐍 SQLAlchemy (complex patterns) - 5-10 min
8. 📜 Lodash (ideal baseline) - 2 min
9. 📜 Express (middleware patterns) - 3 min
10. 📜 React (component patterns) - 5-10 min
11. 📜 Vue (reactive patterns) - 5-10 min
12. 📊 Generate reports (10 min)

**Total**: ~60-90 minutes

---

## 🎉 DELIVERABLES

**When complete, you'll have**:

1. **9 complete codebase analyses** (8D + 8L for each)
2. **Comparative report** showing architectural patterns across ecosystems
3. **Per-repo insights** with actionable recommendations
4. **Rankings** (most pure, most cacheable, most secure, etc.)
5. **Evidence** that Theory v2 works on world-class codebases
6. **Benchmark data** for Collider performance at scale

**This will prove**:
- ✅ 8D + 8L works on production code
- ✅ Insights scale from 571 nodes → 100K+ nodes
- ✅ Cross-language analysis possible
- ✅ Comparative architecture analysis unlocked
- ✅ Automatic task generation works at scale

---

**Ready to execute?** Say "GO" and I'll start with Phase 0! 🚀
