#!/bin/bash
# Atomic Task Claim Script
# Uses filesystem mv for race-condition-free task reservation

set -e

REGISTRY_DIR="$(dirname "$0")/../registry"
TASK_ID="${1:-}"
AGENT_ID="${2:-$(whoami)}"

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <TASK-ID> [AGENT-ID]"
    echo "Example: $0 TASK-001 claude-opus"
    exit 1
fi

TIMESTAMP=$(date +%s)
SOURCE="${REGISTRY_DIR}/active/${TASK_ID}.yaml"
TARGET="${REGISTRY_DIR}/claimed/${TIMESTAMP}_${AGENT_ID}_${TASK_ID}.yaml"

# Check if task exists
if [ ! -f "$SOURCE" ]; then
    echo "ERROR: Task ${TASK_ID} not found in active/"
    echo "Available tasks:"
    ls -1 "${REGISTRY_DIR}/active/"
    exit 1
fi

# Atomic claim attempt
if mv "$SOURCE" "$TARGET" 2>/dev/null; then
    echo "SUCCESS: Claimed ${TASK_ID}"
    echo "Claim file: ${TARGET}"
    echo "Timestamp: ${TIMESTAMP}"
    echo "Agent: ${AGENT_ID}"
else
    echo "FAILED: Task ${TASK_ID} already claimed or moved"
    exit 1
fi
