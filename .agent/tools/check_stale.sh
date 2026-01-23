#!/bin/bash
# Check for stale claimed tasks (>30 min without activity)

REGISTRY_DIR="$(dirname "$0")/../registry"
STALE_MINUTES="${1:-30}"

echo "Checking for claims older than ${STALE_MINUTES} minutes..."
echo ""

STALE_FILES=$(find "${REGISTRY_DIR}/claimed" -name "*.yaml" -mmin +${STALE_MINUTES} 2>/dev/null)

if [ -z "$STALE_FILES" ]; then
    echo "No stale claims found."
    exit 0
fi

echo "STALE CLAIMS FOUND:"
echo "==================="

for f in $STALE_FILES; do
    FILENAME=$(basename "$f")
    AGE_MIN=$(( ($(date +%s) - $(stat -f %m "$f")) / 60 ))
    echo "- ${FILENAME} (${AGE_MIN} min old)"
done

echo ""
echo "To release stale claims:"
echo "  ./release_task.sh TASK-XXX RETRY"
