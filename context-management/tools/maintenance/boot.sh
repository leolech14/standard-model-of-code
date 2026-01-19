#!/bin/bash
# Agent Boot Script
# Generates INITIATION_REPORT for agent sessions
# Usage: ./tools/agent_boot.sh

set -e

echo "=== AGENT BOOT SEQUENCE ==="
echo ""

# Update timestamps CSV
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/update_timestamps.sh" ]; then
    echo "Updating file timestamps..."
    "$SCRIPT_DIR/update_timestamps.sh" --quiet
    echo "Timestamps updated."
    echo ""
fi

# Get repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
echo "Repo Root: $REPO_ROOT"

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "not_a_git_repo")
echo "Branch: $BRANCH"

# Get git status
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    STATUS="clean"
else
    STATUS="dirty"
fi
echo "Status: $STATUS"

# Detect commands (look for common patterns)
detect_command() {
    local type=$1

    case $type in
        test)
            if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
                echo "npm test"
            elif [ -f "pytest.ini" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
                echo "pytest"
            elif [ -f "Makefile" ] && grep -q '^test:' Makefile 2>/dev/null; then
                echo "make test"
            elif [ -f "go.mod" ]; then
                echo "go test ./..."
            else
                echo "not_found"
            fi
            ;;
        lint)
            if [ -f "package.json" ] && grep -q '"lint"' package.json 2>/dev/null; then
                echo "npm run lint"
            elif [ -f "pyproject.toml" ] && grep -q 'ruff' pyproject.toml 2>/dev/null; then
                echo "ruff check ."
            elif [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ]; then
                echo "eslint ."
            else
                echo "not_found"
            fi
            ;;
        format)
            if [ -f "package.json" ] && grep -q '"format"' package.json 2>/dev/null; then
                echo "npm run format"
            elif [ -f "pyproject.toml" ] && grep -q 'black' pyproject.toml 2>/dev/null; then
                echo "black ."
            elif [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ]; then
                echo "prettier --write ."
            else
                echo "not_found"
            fi
            ;;
        build)
            if [ -f "package.json" ] && grep -q '"build"' package.json 2>/dev/null; then
                echo "npm run build"
            elif [ -f "Makefile" ] && grep -q '^build:' Makefile 2>/dev/null; then
                echo "make build"
            elif [ -f "go.mod" ]; then
                echo "go build ./..."
            else
                echo "not_found"
            fi
            ;;
        run)
            if [ -f "package.json" ] && grep -q '"start"' package.json 2>/dev/null; then
                echo "npm start"
            elif [ -f "main.py" ]; then
                echo "python main.py"
            elif [ -f "Makefile" ] && grep -q '^run:' Makefile 2>/dev/null; then
                echo "make run"
            else
                echo "not_found"
            fi
            ;;
    esac
}

TEST_CMD=$(detect_command test)
LINT_CMD=$(detect_command lint)
FORMAT_CMD=$(detect_command format)
BUILD_CMD=$(detect_command build)
RUN_CMD=$(detect_command run)

echo ""
echo "Commands detected:"
echo "  test:   $TEST_CMD"
echo "  lint:   $LINT_CMD"
echo "  format: $FORMAT_CMD"
echo "  build:  $BUILD_CMD"
echo "  run:    $RUN_CMD"

# Generate timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo ""
echo "=== INITIATION_REPORT ==="
echo ""

# Output JSON
cat <<EOF
{
  "initiated": true,
  "timestamp": "$TIMESTAMP",
  "repo_root": "$REPO_ROOT",
  "branch": "$BRANCH",
  "status": "$STATUS",
  "commands": {
    "test": "$TEST_CMD",
    "lint": "$LINT_CMD",
    "format": "$FORMAT_CMD",
    "build": "$BUILD_CMD",
    "run": "$RUN_CMD"
  },
  "policies_acknowledged": {
    "commit_discipline": true,
    "no_dirty_end": true,
    "test_before_done": true,
    "summary_required": true
  },
  "notes": []
}
EOF

echo ""
echo "=== BOOT COMPLETE ==="
echo ""
echo "Next steps:"
echo "1. Review docs/agent_school/WORKFLOWS.md for commit discipline"
echo "2. Review docs/agent_school/DOD.md for definition of done"
echo "3. Begin your task using the micro-loop: SCAN → PLAN → EXECUTE → VALIDATE → COMMIT"
