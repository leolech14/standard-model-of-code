#!/bin/bash
# Release a claimed task (success or failure)

set -e

REGISTRY_DIR="$(dirname "$0")/../registry"
TASK_ID="${1:-}"
STATUS="${2:-COMPLETE}"  # COMPLETE, FAILED, or RETRY

if [ -z "$TASK_ID" ]; then
    echo "Usage: $0 <TASK-ID> [STATUS]"
    echo "STATUS: COMPLETE (default), FAILED, or RETRY"
    exit 1
fi

# Find the claimed file
CLAIMED_FILE=$(ls "${REGISTRY_DIR}/claimed/"*"_${TASK_ID}.yaml" 2>/dev/null | head -1)

if [ -z "$CLAIMED_FILE" ] || [ ! -f "$CLAIMED_FILE" ]; then
    echo "ERROR: No claimed file found for ${TASK_ID}"
    echo "Claimed tasks:"
    ls -1 "${REGISTRY_DIR}/claimed/" 2>/dev/null || echo "(none)"
    exit 1
fi

case "$STATUS" in
    COMPLETE|FAILED)
        # Move to archive
        TARGET="${REGISTRY_DIR}/archive/${STATUS}_${TASK_ID}.yaml"
        mv "$CLAIMED_FILE" "$TARGET"
        echo "SUCCESS: Task ${TASK_ID} archived as ${STATUS}"
        echo "Archive file: ${TARGET}"
        ;;
    RETRY)
        # Move back to active for retry
        TARGET="${REGISTRY_DIR}/active/${TASK_ID}.yaml"
        mv "$CLAIMED_FILE" "$TARGET"
        echo "SUCCESS: Task ${TASK_ID} returned to active for retry"
        ;;
    *)
        echo "ERROR: Unknown status '${STATUS}'"
        echo "Valid: COMPLETE, FAILED, RETRY"
        exit 1
        ;;
esac
