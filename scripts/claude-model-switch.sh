#!/bin/bash
# Claude Code Model Switcher
# Switches between different inference providers
#
# Usage:
#   source scripts/claude-model-switch.sh anthropic   # Default Anthropic
#   source scripts/claude-model-switch.sh openrouter  # OpenRouter (346+ models)
#   source scripts/claude-model-switch.sh zai         # Z.ai GLM (use alias instead)
#   source scripts/claude-model-switch.sh litellm     # LiteLLM proxy (for Cerebras/Groq)
#
# After sourcing, run: claude --model <model-name> "your prompt"
#
# IMPORTANT: OpenRouter and Docker Model Runner support Anthropic API natively.
#            Cerebras/Groq/Together require LiteLLM proxy (OpenAI format only).

set -e

# Load secrets from Doppler
eval "$(doppler secrets download --no-file --format env 2>/dev/null)" || true

show_help() {
    echo "Claude Code Model Switcher"
    echo ""
    echo "Usage: source $0 <provider>"
    echo ""
    echo "NATIVE ANTHROPIC API SUPPORT (works directly):"
    echo "  anthropic   - Anthropic API (default)"
    echo "  openrouter  - OpenRouter (346+ models, Anthropic-native)"
    echo "  local       - Docker Model Runner (localhost:12434)"
    echo ""
    echo "REQUIRES LITELLM PROXY (OpenAI format only):"
    echo "  litellm     - LiteLLM proxy at localhost:4000"
    echo "                Supports: Cerebras, Groq, Together, etc."
    echo ""
    echo "ALTERNATIVES (use aliases instead):"
    echo "  zai         - Use 'zai' alias directly (Z.ai GLM)"
    echo "  claude-1m   - Use 'claude-1m' alias (1M context)"
    echo ""
    echo "After sourcing, run:"
    echo "  claude --model <model> \"prompt\""
    echo ""
    echo "Model examples:"
    echo "  openrouter:  qwen/qwen-2.5-coder-32b-instruct"
    echo "  openrouter:  deepseek/deepseek-coder-v2"
    echo "  openrouter:  anthropic/claude-3.5-sonnet"
    echo "  litellm:     cerebras/llama-3.3-70b"
    echo "  local:       qwen2.5-coder:32b"
}

case "${1:-help}" in
    anthropic|default)
        unset ANTHROPIC_BASE_URL
        unset ANTHROPIC_AUTH_TOKEN
        export ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY}"
        echo "✓ Switched to: Anthropic (default)"
        echo "  Models: claude-sonnet-4-5-20250929, etc."
        ;;

    openrouter|or)
        if [ -z "$OPENROUTER_API_KEY" ]; then
            echo "ERROR: OPENROUTER_API_KEY not set"
            echo "Run: doppler secrets set OPENROUTER_API_KEY <key>"
            return 1 2>/dev/null || exit 1
        fi
        export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
        export ANTHROPIC_AUTH_TOKEN="${OPENROUTER_API_KEY}"
        export ANTHROPIC_API_KEY=""  # MUST be empty for token auth!
        echo "✓ Switched to: OpenRouter (Anthropic-native)"
        echo "  Base URL: https://openrouter.ai/api"
        echo "  Models: qwen/qwen-2.5-coder-32b-instruct, deepseek/deepseek-coder-v2, etc."
        echo ""
        echo "  Browse: https://openrouter.ai/models"
        ;;

    local|docker)
        export ANTHROPIC_BASE_URL="http://localhost:12434"
        unset ANTHROPIC_AUTH_TOKEN
        unset ANTHROPIC_API_KEY
        echo "✓ Switched to: Local Docker Model Runner"
        echo "  Base URL: http://localhost:12434"
        echo ""
        echo "  Make sure Docker Model Runner is running:"
        echo "    docker desktop enable model-runner --tcp"
        echo "  List models: docker model list"
        ;;

    litellm|proxy)
        export ANTHROPIC_BASE_URL="http://localhost:4000"
        unset ANTHROPIC_AUTH_TOKEN
        unset ANTHROPIC_API_KEY
        echo "✓ Switched to: LiteLLM Proxy"
        echo "  Base URL: http://localhost:4000"
        echo ""
        echo "  Make sure LiteLLM is running with your provider:"
        echo "    CEREBRAS_API_KEY=\$CEREBRAS_API_KEY litellm --model cerebras/llama-3.3-70b --port 4000"
        echo "    GROQ_API_KEY=\$GROQ_API_KEY litellm --model groq/llama-3.3-70b-versatile --port 4000"
        echo ""
        echo "  Or use LiteLLM config file for multiple models."
        ;;

    zai)
        echo "Use the 'zai' alias instead:"
        echo "  zai \"your prompt\""
        echo ""
        echo "This uses ~/.claude/settings-zai.json with Z.ai endpoint."
        return 0 2>/dev/null || exit 0
        ;;

    cerebras|groq|together)
        echo "ERROR: $1 uses OpenAI format, not Anthropic."
        echo ""
        echo "Claude Code requires Anthropic Messages API."
        echo "$1 only supports OpenAI format."
        echo ""
        echo "Solution: Use LiteLLM as a proxy:"
        echo "  1. pip install litellm"
        echo "  2. Start proxy:"
        if [ "$1" = "cerebras" ]; then
            echo "     CEREBRAS_API_KEY=\$(doppler secrets get CEREBRAS_API_KEY --plain) \\"
            echo "       litellm --model cerebras/llama-3.3-70b --port 4000"
        elif [ "$1" = "groq" ]; then
            echo "     GROQ_API_KEY=\$(doppler secrets get GROQ_API_KEY --plain) \\"
            echo "       litellm --model groq/llama-3.3-70b-versatile --port 4000"
        else
            echo "     TOGETHER_API_KEY=\$(doppler secrets get TOGETHER_API_KEY --plain) \\"
            echo "       litellm --model together/Qwen/Qwen3-Coder-480B-A35B-Instruct --port 4000"
        fi
        echo "  3. source scripts/claude-model-switch.sh litellm"
        echo "  4. claude \"your prompt\""
        return 1 2>/dev/null || exit 1
        ;;

    help|--help|-h)
        show_help
        return 0 2>/dev/null || exit 0
        ;;

    *)
        echo "Unknown provider: $1"
        echo ""
        show_help
        return 1 2>/dev/null || exit 1
        ;;
esac

echo ""
echo "Current config:"
echo "  ANTHROPIC_BASE_URL:   ${ANTHROPIC_BASE_URL:-<default Anthropic>}"
echo "  ANTHROPIC_AUTH_TOKEN: ${ANTHROPIC_AUTH_TOKEN:+set (hidden)}"
echo "  ANTHROPIC_API_KEY:    ${ANTHROPIC_API_KEY:-<not set>}"
