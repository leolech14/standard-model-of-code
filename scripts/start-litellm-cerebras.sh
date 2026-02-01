#!/bin/bash
# Start LiteLLM proxy for Cerebras
# This translates Anthropic Messages API → Cerebras (OpenAI format)
#
# Usage:
#   ./scripts/start-litellm-cerebras.sh
#   # Then in another terminal:
#   source scripts/claude-model-switch.sh litellm
#   claude --model cerebras/llama-3.3-70b "your prompt"

set -e

# Load Cerebras key from Doppler
export CEREBRAS_API_KEY=$(doppler secrets get CEREBRAS_API_KEY --plain --project ai-tools --config dev 2>/dev/null)

if [ -z "$CEREBRAS_API_KEY" ]; then
    echo "ERROR: CEREBRAS_API_KEY not found in Doppler"
    exit 1
fi

echo "Starting LiteLLM proxy for Cerebras..."
echo "  Port: 4000"
echo "  Model: cerebras/llama-3.3-70b"
echo ""
echo "To use with Claude Code:"
echo "  source scripts/claude-model-switch.sh litellm"
echo "  claude \"your prompt\""
echo ""
echo "Press Ctrl+C to stop"
echo "---"

litellm --model cerebras/llama-3.3-70b --port 4000
