#!/usr/bin/env bash
# Verify MANIFEST.sha256 seal
# Usage: ./tools/research/verify_manifest.sh artifacts/atom-research/2026-01-22/
#
# This script is location-independent: it always operates from PROJECT_ROOT.
# Manifest entries are project-root-relative paths.

set -e

PACK_DIR="${1:?Usage: verify_manifest.sh <pack_dir>}"

# Project root = standard-model-of-code/ (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Always operate from PROJECT_ROOT (manifest paths are relative to it)
cd "$PROJECT_ROOT"

# Handle absolute vs relative pack paths
if [[ "$PACK_DIR" = /* ]]; then
    # Absolute path - must be inside PROJECT_ROOT, convert to relative
    if [[ "$PACK_DIR" == "$PROJECT_ROOT"* ]]; then
        PACK_DIR="${PACK_DIR#$PROJECT_ROOT/}"
    else
        echo "ERROR: Absolute PACK_DIR must be inside PROJECT_ROOT"
        echo "  PACK_DIR: $PACK_DIR"
        echo "  PROJECT_ROOT: $PROJECT_ROOT"
        exit 1
    fi
fi

MANIFEST="$PACK_DIR/MANIFEST.sha256"

if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: MANIFEST.sha256 not found at $MANIFEST"
    echo "  Working directory: $(pwd)"
    exit 1
fi

# Cross-platform SHA256 function (macOS uses shasum, Linux uses sha256sum)
sha256_hash() {
    if command -v sha256sum &> /dev/null; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum &> /dev/null; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        echo "ERROR: No sha256 tool found" >&2
        exit 1
    fi
}

echo "Verifying manifest: $MANIFEST"
echo "Working directory: $(pwd)"
echo "=========================================="

# Extract just the hash lines (skip comments and empty lines)
ERRORS=0
VERIFIED=0

while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ -z "$line" ]] && continue

    EXPECTED_HASH=$(echo "$line" | awk '{print $1}')
    FILE_PATH=$(echo "$line" | awk '{print $2}')

    if [ ! -f "$FILE_PATH" ]; then
        echo "MISSING: $FILE_PATH"
        ERRORS=$((ERRORS + 1))
        continue
    fi

    ACTUAL_HASH=$(sha256_hash "$FILE_PATH")

    if [ "$EXPECTED_HASH" = "$ACTUAL_HASH" ]; then
        echo "OK: $FILE_PATH"
        VERIFIED=$((VERIFIED + 1))
    else
        echo "MISMATCH: $FILE_PATH"
        echo "  Expected: $EXPECTED_HASH"
        echo "  Actual:   $ACTUAL_HASH"
        ERRORS=$((ERRORS + 1))
    fi
done < "$MANIFEST"

echo "=========================================="
echo "Verified: $VERIFIED files"

if [ $ERRORS -eq 0 ]; then
    echo "[PASS] All files match manifest"
    exit 0
else
    echo "[FAIL] $ERRORS file(s) failed verification"
    exit 1
fi
