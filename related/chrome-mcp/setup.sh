#!/bin/bash

echo "🚀 Setting up Chrome MCP Server..."

# Create directory structure
mkdir -p dist test-results

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Create Claude config helper
echo "📝 Creating Claude Desktop configuration helper..."

# Get absolute path
CHROME_MCP_PATH="$(pwd)/dist/index.js"

cat > claude-config.json << EOF
{
  "mcpServers": {
    "chrome": {
      "command": "node",
      "args": ["${CHROME_MCP_PATH}"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 To use Chrome MCP with Claude Desktop:"
echo "1. Copy the contents of 'claude-config.json'"
echo "2. Add to your Claude Desktop config file:"
echo "   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
echo "3. Restart Claude Desktop"
echo ""
echo "🧪 To test with MermaidFlow:"
echo "   npm test"
echo "   or"
echo "   node test-mermaidflow.js"
echo ""
echo "📁 Chrome MCP path: ${CHROME_MCP_PATH}"