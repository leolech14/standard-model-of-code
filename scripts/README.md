# Scripts Index

> **Purpose:** Central index of executable scripts across PROJECT_elements.
> Updated: 2026-01-31

## Quick Reference

### Active Scripts (Use These)

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/claude-model-switch.sh` | Switch Claude model provider | `./scripts/claude-model-switch.sh` |
| `scripts/start-litellm-cerebras.sh` | Start LiteLLM proxy for Cerebras | `./scripts/start-litellm-cerebras.sh` |

### Agent Task Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `.agent/tools/claim_task.sh` | Claim a task for execution | Used by KERNEL.md |
| `.agent/tools/release_task.sh` | Release a claimed task | Used by KERNEL.md |
| `.agent/tools/check_stale.sh` | Check for stale tasks | Used by autopilot |
| `.agent/tools/promote_opportunity.sh` | Promote OPP to TASK | Manual |

### Maintenance Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `context-management/tools/maintenance/boot.sh` | Agent boot sequence | `./boot.sh` |
| `context-management/tools/maintenance/offload_legacy.sh` | Archive old files | Manual |
| `context-management/tools/maintenance/update_timestamps.sh` | Update file timestamps | Manual |

### Cloud/Deployment Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `.agent/tools/cloud/deploy.sh` | Deploy to cloud | Manual |
| `.agent/tools/cloud/check_status.sh` | Check cloud status | Manual |
| `context-management/tools/ops/sync_to_cloud.sh` | Sync to GCS | Manual |
| `standard-model-of-code/ops/cloud-run-deploy.sh` | Deploy Collider to Cloud Run | CI/CD |
| `standard-model-of-code/ops/cloud-entrypoint.sh` | Cloud Run entrypoint | Docker |

### Dashboard Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `context-management/viz/unified-dashboard/install-and-test-dashboards.sh` | Install dashboards | One-time |
| `context-management/viz/unified-dashboard/test-dashboards.sh` | Test dashboards | CI |

### Tool-Specific Scripts
| Script | Purpose | Usage |
|--------|---------|-------|
| `context-management/tools/docsintel/install.sh` | Install DocsIntel MCP | One-time |
| `context-management/tools/ai/setup_agent_builder.sh` | Setup agent builder | One-time |
| `standard-model-of-code/tools/batch_grade/deploy.sh` | Deploy batch grader | Manual |
| `standard-model-of-code/tools/batch_grade/runpod_setup.sh` | Setup RunPod | One-time |

## Archived/Legacy Scripts (Don't Use)

| Script | Status | Notes |
|--------|--------|-------|
| `.agent/tools/graphrag_phase1.sh` | Dormant | GraphRAG experiment |
| `.agent/tools/execute_cutting_phase1.sh` | Dormant | Old refactoring |
| `context-management/docs/research/scripts/research_phase1.sh` | Dormant | Old research automation |
| `context-management/library/*/deploy.sh` | Dead | Legacy dashboards |
| `standard-model-of-code/archive/**/*.sh` | Dead | Archived experiments |

## Python CLI Tools (Prefer These)

For most tasks, use Python tools instead of shell scripts:

```bash
# Analysis
python3 context-management/tools/ai/analyze.py "query"

# Spiral Intel
python3 context-management/tools/ai/cerebras_spiral_intel.py status

# Collider
./collider full . --output /tmp/analysis
```

## Adding New Scripts

1. Place in appropriate directory:
   - `scripts/` - General utilities
   - `.agent/tools/` - Agent automation
   - `*/ops/` - Deployment/cloud
   - `*/tools/` - Tool-specific

2. Add to this README with purpose and usage

3. Include shebang and usage comment:
   ```bash
   #!/bin/bash
   # Usage: ./script.sh [args]
   # Purpose: What it does
   ```
