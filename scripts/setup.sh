#!/usr/bin/env bash
# PROJECT_elements -- plug-and-play setup
# Usage: ./scripts/setup.sh [--full]
set -euo pipefail

FULL=false
[[ "${1:-}" == "--full" ]] && FULL=true

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# ── Colors ──────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { printf "${GREEN}[ok]${NC}  %s\n" "$1"; }
warn() { printf "${YELLOW}[!!]${NC}  %s\n" "$1"; }
fail() { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }
step() { printf "\n${BLUE}── %s ──${NC}\n" "$1"; }

# ── 1. Check dependencies ──────────────────────────────────────
step "Checking dependencies"
MISSING=0

check_cmd() {
    if command -v "$1" >/dev/null 2>&1; then
        ok "$1 $(command -v "$1")"
    else
        fail "$1 not found -- $2"
        MISSING=1
    fi
}

check_cmd python3      "brew install python3"
check_cmd uv           "curl -LsSf https://astral.sh/uv/install.sh | sh"
check_cmd git          "xcode-select --install"
check_cmd pre-commit   "brew install pre-commit  OR  uv tool install pre-commit"

# node is optional -- only needed for commitlint hook
if command -v node >/dev/null 2>&1; then
    ok "node $(node --version)"
else
    warn "node not found (optional -- needed for commitlint hook)"
fi

if [[ "$FULL" == true ]]; then
    check_cmd doppler "brew install dopplerhq/cli/doppler"
fi

if [[ "$MISSING" -eq 1 ]]; then
    fail "Install missing dependencies above and re-run."
    exit 1
fi

# ── 2. Collider venv (particle/) ───────────────────────────────
step "Setting up Collider venv (particle/)"
(cd particle && uv sync)
ok "particle/.venv ready"

# ── 3. Git hooks ───────────────────────────────────────────────
step "Installing git hooks"

# Clear core.hooksPath if set (conflicts with pre-commit install)
if git config --get core.hooksPath >/dev/null 2>&1; then
    git config --unset core.hooksPath
    ok "cleared redundant core.hooksPath"
fi

# pre-commit hooks (commitlint, yaml checks, etc.)
pre-commit install --hook-type commit-msg --hook-type pre-commit
ok "pre-commit hooks installed"

# Symlink tracked hooks into .git/hooks/
mkdir -p .git/hooks

for hook in .agent/hooks/pre-push .agent/hooks/post-commit; do
    name="$(basename "$hook")"
    target="../../${hook}"
    if [[ -f "$hook" ]]; then
        ln -sf "$target" ".git/hooks/$name"
        chmod +x ".git/hooks/$name"
        ok "symlinked $name"
    fi
done

# ── 4. Tools venv (.tools_venv) ───────────────────────────────
step "Setting up tools venv (.tools_venv)"
if [[ -f requirements-tools.txt ]]; then
    uv venv .tools_venv --python python3 2>/dev/null || true
    .tools_venv/bin/pip install -q -r requirements-tools.txt
    ok ".tools_venv ready"
else
    warn "requirements-tools.txt not found -- skipping .tools_venv"
fi

# ── 5. Full mode: Wave AI tools ───────────────────────────────
if [[ "$FULL" == true ]]; then
    step "Setting up Wave AI tools (Doppler)"
    if [[ -f requirements.txt ]]; then
        uv venv .venv --python python3 2>/dev/null || true
        .venv/bin/pip install -q -r requirements.txt
        ok ".venv ready (Wave AI)"
    fi
    if doppler whoami >/dev/null 2>&1; then
        ok "Doppler authenticated"
    else
        warn "Run 'doppler login' then 'doppler setup' to configure secrets"
    fi
fi

# ── 6. Verify ─────────────────────────────────────────────────
step "Verifying installation"
VERIFY_OK=true

# Collider import test
if (cd particle && uv run python -c "from core.collider import Collider; print('Collider import OK')" 2>/dev/null); then
    ok "Collider importable"
else
    # Fallback: try the package itself
    if (cd particle && uv run python -c "import cli; print('cli import OK')" 2>/dev/null); then
        ok "Collider CLI importable"
    else
        warn "Collider import check failed (may need: cd particle && uv sync --all-extras)"
        VERIFY_OK=false
    fi
fi

# pre-commit dry run (fast subset)
if pre-commit run check-yaml --all-files >/dev/null 2>&1; then
    ok "pre-commit operational"
else
    warn "pre-commit dry run had issues (run 'make lint' to see details)"
    VERIFY_OK=false
fi

# ── 7. Quick start ────────────────────────────────────────────
step "Setup complete"

if [[ "$VERIFY_OK" == true ]]; then
    printf "${GREEN}All checks passed.${NC}\n"
else
    printf "${YELLOW}Setup finished with warnings -- see above.${NC}\n"
fi

cat <<'QUICKSTART'

Quick start:
  ./pe status              # System health
  make test                # Run 406+ Collider tests
  make lint                # Pre-commit checks on all files
  ./collider full .        # Full Collider analysis

QUICKSTART
