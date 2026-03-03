# Git Hooks

Git hooks for PROJECT_elements. Source of truth lives here in `.agent/hooks/`;
`.git/hooks/` gets symlinks pointing back.

## Installation

```bash
make hooks          # Recommended: installs all hooks via symlinks
make setup          # Full setup (also installs hooks)
```

Manual alternative:
```bash
pre-commit install --hook-type commit-msg --hook-type pre-commit
ln -sf ../../.agent/hooks/pre-push .git/hooks/pre-push
ln -sf ../../.agent/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/pre-push .git/hooks/post-commit
```

## Hooks

### pre-push (COLLIDER GATE)

Runs Collider architectural health checks before allowing a push.

- Executes `particle/src/scripts/collider_pre_push.py` via `uv run`
- 120-second timeout (graceful: allows push on timeout, CI validates)
- Worktree-safe (unsets VIRTUAL_ENV for correct venv resolution)

### post-commit (AUTOPILOT)

Runs after every commit via the **Autopilot** orchestrator:

1. **TDJ** - Updates Timestamp Daily Journal (temporal index)
2. **Trigger Engine** - Checks and executes macro triggers
3. **Circuit Breakers** - Graceful degradation if systems fail

**Features:**
- Lightweight execution (~100ms)
- Circuit breakers prevent cascade failures
- Graceful degradation (4 levels: FULL -> PARTIAL -> MANUAL -> EMERGENCY)
- Idempotent (safe to run multiple times)

**Commands:**
```bash
.agent/tools/autopilot.py status    # Show all systems status
.agent/tools/autopilot.py disable   # Disable automation
.agent/tools/autopilot.py enable    # Re-enable automation
.agent/tools/autopilot.py health    # Deep health check
.agent/tools/autopilot.py recover   # Reset after failures
.agent/tools/autopilot.py run       # Manual full cycle
```

**Legacy Fallback:** If autopilot is unavailable, falls back to GCS mirror only.

### pre-commit (via pre-commit framework)

Managed by `.pre-commit-config.yaml`, not stored here. Includes:
- commitlint (Conventional Commits)
- YAML/JSON/TOML validation
- Trailing whitespace, EOF fixer
- Large file detection (500KB limit)
- Merge conflict markers, private key detection
- Python AST check

## Adding New Hooks

1. Create the hook script in `.agent/hooks/`
2. Document it in this README
3. Add a symlink line in `scripts/setup.sh` and `Makefile` `hooks` target
4. Run `make hooks` to install
