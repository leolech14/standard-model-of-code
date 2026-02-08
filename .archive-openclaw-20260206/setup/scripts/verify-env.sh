#!/bin/bash
# Environment Verification - Check Mac & VPS match
# Run daily via cron to detect drift

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VPS_HOST="hostinger"

echo "Environment Verification Report"
echo "Date: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check function
check_tool() {
    local tool=$1
    local version_cmd=$2

    # Local check
    if command -v $tool &> /dev/null; then
        local_version=$($version_cmd 2>&1 | head -1)
        local_status="${GREEN}✓${NC}"
    else
        local_version="NOT INSTALLED"
        local_status="${RED}✗${NC}"
    fi

    # Remote check
    if ssh $VPS_HOST "command -v $tool" &> /dev/null; then
        remote_version=$(ssh $VPS_HOST "$version_cmd" 2>&1 | head -1)
        remote_status="${GREEN}✓${NC}"
    else
        remote_version="NOT INSTALLED"
        remote_status="${RED}✗${NC}"
    fi

    # Compare
    if [ "$local_version" = "$remote_version" ]; then
        match="${GREEN}✓ MATCH${NC}"
    else
        match="${YELLOW}⚠ DIFF${NC}"
    fi

    printf "%-20s %b %-30s %b %-30s %b\n" \
        "$tool" "$local_status" "$local_version" \
        "$remote_status" "$remote_version" "$match"
}

echo "Tool                 Mac                            VPS                            Status"
echo "──────────────────── ────────────────────────────── ────────────────────────────── ──────"

check_tool "node" "node --version"
check_tool "pnpm" "pnpm --version"
check_tool "python3" "python3 --version"
check_tool "doppler" "doppler --version"
check_tool "gcloud" "gcloud version | head -1"
check_tool "litellm" "litellm --version"
check_tool "ollama" "ollama --version"
check_tool "fswatch" "fswatch --version | head -1"
check_tool "lsyncd" "lsyncd --version"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "End of report"
