#!/bin/bash
# OpenClaw Environment Setup - Mac & VPS
# Run on both machines to get identical environments
#
# Usage: ./install-dependencies.sh

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  OpenClaw Environment Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo -e "${GREEN}✓ Detected: macOS${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}✓ Detected: Linux${NC}"
else
    echo -e "${RED}✗ Unsupported OS: $OSTYPE${NC}"
    exit 1
fi

echo ""

# ============================================================================
# UNIVERSAL DEPENDENCIES (Both Mac & Linux)
# ============================================================================

echo -e "${BLUE}[1/8] Installing Universal Dependencies...${NC}"

# Node.js check
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    if [[ "$OS" == "mac" ]]; then
        brew install node@22
    else
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
else
    echo -e "${GREEN}✓ Node.js already installed: $(node --version)${NC}"
fi

# pnpm check
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
else
    echo -e "${GREEN}✓ pnpm already installed: $(pnpm --version)${NC}"
fi

echo ""

# ============================================================================
# PYTHON DEPENDENCIES
# ============================================================================

echo -e "${BLUE}[2/8] Installing Python Dependencies...${NC}"

# Python 3 check
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    if [[ "$OS" == "mac" ]]; then
        brew install python@3.12
    else
        sudo apt-get install -y python3 python3-pip
    fi
else
    echo -e "${GREEN}✓ Python 3 already installed: $(python3 --version)${NC}"
fi

# pipx check (Mac only, Linux uses pip)
if [[ "$OS" == "mac" ]]; then
    if ! command -v pipx &> /dev/null; then
        echo "Installing pipx..."
        brew install pipx
    else
        echo -e "${GREEN}✓ pipx already installed${NC}"
    fi
fi

echo ""

# ============================================================================
# LITELLM (for Claude subscription proxy)
# ============================================================================

echo -e "${BLUE}[3/8] Installing LiteLLM...${NC}"

if [[ "$OS" == "mac" ]]; then
    pipx install 'litellm[proxy]' 2>&1 | tail -3
else
    pip3 install 'litellm[proxy]' --break-system-packages 2>&1 | tail -3
fi

echo -e "${GREEN}✓ LiteLLM installed${NC}"
echo ""

# ============================================================================
# DOPPLER (secrets management)
# ============================================================================

echo -e "${BLUE}[4/8] Installing Doppler...${NC}"

if ! command -v doppler &> /dev/null; then
    echo "Installing Doppler..."
    if [[ "$OS" == "mac" ]]; then
        brew install doppler
    else
        curl -sLf https://cli.doppler.com/install.sh | sh
    fi
else
    echo -e "${GREEN}✓ Doppler already installed: $(doppler --version)${NC}"
fi

echo ""

# ============================================================================
# FILE SYNC TOOLS
# ============================================================================

echo -e "${BLUE}[5/8] Installing Sync Tools...${NC}"

if [[ "$OS" == "mac" ]]; then
    # fswatch for file watching
    if ! command -v fswatch &> /dev/null; then
        echo "Installing fswatch..."
        brew install fswatch
    else
        echo -e "${GREEN}✓ fswatch already installed${NC}"
    fi
else
    # lsyncd + inotify for Linux
    if ! command -v lsyncd &> /dev/null; then
        echo "Installing lsyncd..."
        sudo apt-get install -y lsyncd inotify-tools
    else
        echo -e "${GREEN}✓ lsyncd already installed${NC}"
    fi
fi

echo ""

# ============================================================================
# GCLOUD SDK
# ============================================================================

echo -e "${BLUE}[6/8] Installing Google Cloud SDK...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo "Installing gcloud SDK..."
    curl https://sdk.cloud.google.com | bash

    # Add to PATH
    if [[ "$OS" == "mac" ]]; then
        echo 'source ~/google-cloud-sdk/path.bash.inc' >> ~/.zshrc
        echo 'source ~/google-cloud-sdk/completion.zsh.inc' >> ~/.zshrc
    else
        # Create symlinks for Linux
        sudo ln -sf /root/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud
        sudo ln -sf /root/google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil
    fi

    echo -e "${YELLOW}⚠ gcloud installed - restart shell or run: source ~/.zshrc${NC}"
else
    echo -e "${GREEN}✓ gcloud already installed: $(gcloud version | head -1)${NC}"
fi

echo ""

# ============================================================================
# OLLAMA (local models - VPS only)
# ============================================================================

echo -e "${BLUE}[7/8] Installing Ollama...${NC}"

if [[ "$OS" == "linux" ]]; then
    if ! command -v ollama &> /dev/null; then
        echo "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh

        # Pull models
        echo "Pulling Ollama models (this takes time)..."
        ollama pull qwen2.5:32b &
        ollama pull codellama:34b &
        wait
    else
        echo -e "${GREEN}✓ Ollama already installed${NC}"
        echo "Models available:"
        ollama list
    fi
else
    echo -e "${YELLOW}⚠ Ollama skipped (VPS only)${NC}"
fi

echo ""

# ============================================================================
# OPENCLAW (if on VPS)
# ============================================================================

echo -e "${BLUE}[8/8] Checking OpenClaw...${NC}"

if [[ "$OS" == "linux" ]]; then
    if [ ! -d "/root/openclaw" ]; then
        echo "OpenClaw not found - install manually or via Hostinger template"
    else
        echo -e "${GREEN}✓ OpenClaw found at /root/openclaw${NC}"
        cd /root/openclaw && pnpm install 2>&1 | tail -3
    fi
else
    echo -e "${YELLOW}⚠ OpenClaw check skipped (VPS only)${NC}"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Installed:"
echo "  ✓ Node.js & pnpm"
echo "  ✓ Python 3"
echo "  ✓ LiteLLM (Claude proxy)"
echo "  ✓ Doppler (secrets)"
echo "  ✓ Sync tools (fswatch/lsyncd)"
echo "  ✓ gcloud SDK"
if [[ "$OS" == "linux" ]]; then
    echo "  ✓ Ollama + models"
fi
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Configure Doppler: doppler login"
echo "  2. Authenticate gcloud: gcloud auth login"
if [[ "$OS" == "linux" ]]; then
    echo "  3. Configure OpenClaw: cd /root/openclaw && pnpm openclaw onboard"
fi
echo ""
echo -e "${YELLOW}Configs synced via: ~/PROJECTS_all/PROJECT_elements/configs/${NC}"
echo ""
