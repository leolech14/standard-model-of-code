# Oracle-Based Benchmark System

Validates Spectrometer's architectural layer predictions against GitHub repos with **documented, enforceable architecture**.

## Why "Oracle"?

Instead of hand-labeling components, we use repos where the "correct answer" comes from:
- **Canonical directory structure** (e.g., `src/domain/` → domain layer)
- **Book/documentation references** (Architecture Patterns with Python)
- **CI-enforced constraints** (Import Linter, ArchUnit) [planned]

This gives us:
- Complete symbol coverage (every file → layer)
- Citable ground truth for papers
- Reproducible metrics with pinned commits

## Quick Start

```bash
# Run all benchmarks
python run_oracle_bench.py

# Run single repo
python run_oracle_bench.py --repo cosmicpython_code

# List available repos
python run_oracle_bench.py --list

# Extract oracle only (no Spectrometer)
python run_oracle_bench.py --extract-only
```

## Current Results

| Repo | Accuracy | Coverage | Validated Source |
|------|----------|----------|-----------------|
| cosmicpython | 23.4% | 48.4% | O'Reilly book (2020) |
| dddpy | 47.5% | 65.9% | README Onion Architecture |

## Adding New Repos

1. Add entry to `manifest.yaml`:
```yaml
- id: my_repo
  name: "My DDD Repo"
  url: https://github.com/user/repo.git
  commit: "abc1234"  # PIN THIS!
  language: python
  
  oracle_type: canonical_paths
  oracle_config:
    layers:
      domain: ["src/domain/**/*.py"]
      application: ["src/service/**/*.py"]
  
  mapping_file: mappings/my_mapping.yaml
  validated_source: "README.md documents layer structure"
```

2. Create translation mapping in `mappings/`:
```yaml
name: my_mapping
oracle_to_layer:
  domain: Core
  application: Application
```

3. Run: `python run_oracle_bench.py --repo my_repo`

## Oracle Types

| Type | Status | How it works |
|------|--------|--------------|
| `canonical_paths` | ✅ Done | Glob patterns → layer |
| `import_linter` | 🔲 Planned | Parse `.importlinter` config |
| `archunit` | 🔲 Planned | Parse ArchUnit test files |

## Metrics Explained

- **Accuracy**: % of oracle-labeled symbols where Spectrometer's inferred layer matches
- **Coverage**: % of all symbols that have oracle labels
- **Precision/Recall**: Per-layer breakdown
- **Confusion Matrix**: Where layers get mis-classified

## Directory Structure

```
oracle_bench/
├── manifest.yaml         # Repo definitions
├── run_oracle_bench.py   # Main runner
├── oracles/
│   ├── base.py           # Abstract interface
│   └── canonical_paths.py
├── mappings/             # oracle→spectrometer translations
├── repos/                # Cloned benchmark repos
└── reports/              # Generated JSON reports
```
