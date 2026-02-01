---
description: Global Discovery Experiment - 100 Repo Scale
---

# Global Discovery Experiment

This workflow defines the process for testing the Standard Model of Code against 100+ real-world repositories to validate coverage and discover new atoms.

## 1. Setup
- [ ] Create `experiments/global_discovery` directory
- [ ] Define `experiments/global_discovery/repos.json` (List of 100 target repos)
- [ ] Ensure `collider` CLI is available in path

## 2. Infrastructure
- [ ] Create `tools/batch_runner.py` to handle serial cloning and scanning
- [ ] Implement `tools/aggregator.py` to combine 100 JSON reports into one `global_matrix.json`

## 3. Execution (The Loop)
For each repo in `repos.json`:
1. **Clone**: Shallow clone to `temp_repos/<name>`
2. **Scan**: Run `collider full temp_repos/<name> --output experiments/outputs/<name>`
3. **Clean**: Delete `temp_repos/<name>` (Disk space management)
4. **Log**: Record success/failure and atom counts

## 4. Analysis
- [ ] Run `visualize_graph.py` on the aggregated `global_matrix.json`
- [ ] Generate "Global Coverage Report.md"
- [ ] Identify atoms with <5% coverage (Candidates for pruning)
- [ ] Identify frequent "Unknown" patterns (Candidates for new atoms)

## 5. Primitives to Target
Focus on diverse domains:
- **Systems**: Linux kernel, Redis, Nginx (C/C++)
- **Web**: React, Vue, Django, Rails (JS, Python, Ruby)
- **ML**: PyTorch, TensorFlow, HuggingFace (Python, C++)
- **Infra**: Kubernetes, Terraform, Docker (Go)
- **Enterprise**: Spring Boot, .NET Core (Java, C#)

## 6. Performance & Temporal Analysis (Advanced)
- [ ] For supported languages (e.g., Python), enable `trace_execution` flag if runtime data is available.
- [ ] Generate **Logic Gantt Charts**: Visualization of function dependency chains with estimated execution costs.
- [ ] Run **Shortest Path Algorithms** (Dijkstra/A*) on the graph to identify:
    - Critical Path latency (Theoretical minimum execution time).
    - Bottleneck nodes (High-latency hubs).
- [ ] Visualize "Hotspots" on the Standard Output graph (Red glow for slow paths).
