#!/bin/bash
# DocsIntel Installation Script
# Level: L6 (PACKAGE)
# Purpose: Install and configure documentation intelligence MCP servers

set -e

echo "=================================="
echo "DocsIntel Installation"
echo "=================================="
echo ""

CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js not found. Please install Node.js first.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm not found. Please install npm first.${NC}"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}Warning: jq not found. Installing via brew...${NC}"
    brew install jq
fi

echo -e "${GREEN}Prerequisites OK${NC}"
echo ""

# =============================================================================
# LAYER 1: Install Pre-indexed MCP Servers
# =============================================================================

echo "=================================="
echo "Layer 1: Pre-indexed MCP Servers"
echo "=================================="
echo ""

# 1. Anthropic Docs MCP
echo "Installing anthropic-docs-mcp..."
if npm list -g @julianoczkowski/anthropic-docs-mcp-ts &> /dev/null; then
    echo -e "${GREEN}anthropic-docs-mcp already installed${NC}"
else
    npm install -g @julianoczkowski/anthropic-docs-mcp-ts
    echo -e "${GREEN}anthropic-docs-mcp installed${NC}"
fi

# Verify it works
if anthropic-docs-mcp --help &> /dev/null; then
    echo -e "${GREEN}anthropic-docs-mcp verified working${NC}"
else
    echo -e "${YELLOW}Warning: anthropic-docs-mcp may not be in PATH${NC}"
fi

echo ""

# =============================================================================
# LAYER 2: Verify Self-indexed Engine
# =============================================================================

echo "=================================="
echo "Layer 2: Self-indexed Engine"
echo "=================================="
echo ""

# Check if docs-mcp-server is configured
if [ -f "$CLAUDE_CONFIG" ]; then
    if jq -e '.mcpServers["docs-mcp-server"]' "$CLAUDE_CONFIG" > /dev/null 2>&1; then
        echo -e "${GREEN}docs-mcp-server already configured${NC}"
    else
        echo -e "${YELLOW}docs-mcp-server not in Claude config${NC}"
        echo "Add manually or run: docintel configure"
    fi
else
    echo -e "${RED}Claude Desktop config not found at: $CLAUDE_CONFIG${NC}"
fi

echo ""

# =============================================================================
# Generate MCP Config Snippet
# =============================================================================

echo "=================================="
echo "MCP Configuration Snippet"
echo "=================================="
echo ""
echo "Add these to your Claude Desktop config (mcpServers section):"
echo ""

cat << 'EOF'
{
  "anthropic-docs": {
    "command": "anthropic-docs-mcp",
    "args": ["--transport", "stdio"]
  },
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
EOF

echo ""
echo "=================================="
echo "Installation Complete"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Add the MCP config snippet above to Claude Desktop"
echo "2. Restart Claude Desktop"
echo "3. Test: 'Search Anthropic docs for Max subscription features'"
echo ""
echo -e "${YELLOW}Config location: $CLAUDE_CONFIG${NC}"
echo ""
