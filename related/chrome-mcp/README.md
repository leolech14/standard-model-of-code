# Chrome MCP - Browser Automation via Model Context Protocol

A powerful MCP (Model Context Protocol) server that provides comprehensive browser automation capabilities through Chrome DevTools Protocol and Puppeteer.

## 🚀 Features

### Core Capabilities
- **Browser Management**: Launch, configure, and manage Chrome instances
- **Page Navigation**: Navigate to URLs, wait for loads, handle redirects
- **Element Interaction**: Click, type, select, hover over elements
- **Content Extraction**: Get HTML, text, or markdown content
- **Screenshot Capture**: Full page or element-specific screenshots
- **JavaScript Execution**: Run scripts in page context
- **Network Monitoring**: Track requests, responses, and network conditions
- **Page Analysis**: SEO, performance, and accessibility metrics

### Advanced Features
- **Request Interception**: Block or modify network requests
- **Console Monitoring**: Capture console logs and errors
- **Form Automation**: Extract and fill forms
- **Link Analysis**: Extract internal and external links
- **Multi-tab Management**: Work with multiple browser tabs
- **Headless Support**: Run in headless or headed mode

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd chrome-mcp

# Install dependencies
npm install

# Build the project
npm run build

# Or run in development mode
npm run dev
```

## 🔧 Setup

### 1. Install Chrome/Chromium
Ensure Chrome or Chromium is installed on your system:
- macOS: `brew install --cask google-chrome`
- Ubuntu: `sudo apt-get install google-chrome-stable`
- Windows: Download from https://chrome.google.com

### 2. Configure Claude Desktop to use Chrome MCP

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "chrome": {
      "command": "node",
      "args": ["/path/to/chrome-mcp/dist/index.js"],
      "env": {
        "PUPPETEER_EXECUTABLE_PATH": "/path/to/chrome"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

## 📚 Available Tools

### Browser Management
- `chrome_launch`: Launch Chrome browser
- `chrome_close`: Close Chrome browser
- `chrome_new_tab`: Open new tab
- `chrome_list_tabs`: List all open tabs

### Page Operations
- `page_navigate`: Navigate to URL
- `page_screenshot`: Take screenshot
- `page_content`: Get page content
- `page_execute`: Execute JavaScript
- `page_analyze`: Analyze page metrics
- `page_links`: Extract links
- `page_forms`: Extract forms

### Element Interaction
- `element_click`: Click element
- `element_type`: Type text into input
- `element_select`: Select dropdown option
- `element_hover`: Hover over element
- `element_scroll`: Scroll to element
- `element_waitFor`: Wait for element

### Network Tools
- `network_requests`: Get request log
- `network_block`: Block requests
- `network_clearLogs`: Clear network logs

## 🎯 Usage Examples

### Basic Web Scraping
```
1. Launch Chrome
2. Navigate to target URL
3. Extract content or take screenshot
4. Close browser
```

### Form Automation
```
1. Navigate to form URL
2. Extract form fields
3. Fill in required fields
4. Submit form
5. Verify results
```

### Performance Testing
```
1. Navigate to page
2. Analyze performance metrics
3. Monitor network requests
4. Take screenshots
5. Generate report
```

## 🔍 Testing MermaidFlow

Use the provided test script to test the MermaidFlow application:

```bash
node test-mermaidflow.js
```

This will:
- Launch Chrome
- Load MermaidFlow application
- Test various features
- Collect performance metrics
- Generate development insights

## 🛠️ Development

### Project Structure
```
chrome-mcp/
├── src/
│   ├── index.ts          # Main MCP server
│   ├── chrome-manager.ts # Chrome instance management
│   └── tools/            # Tool implementations
│       ├── browser-tools.ts
│       ├── page-tools.ts
│       ├── element-tools.ts
│       └── network-tools.ts
├── test-mermaidflow.js  # Test script for MermaidFlow
└── dist/                 # Compiled JavaScript
```

### Building
```bash
npm run build
```

### Running in Development
```bash
npm run dev
```

### Testing
```bash
npm test
```

## ⚙️ Configuration

### Chrome Options
- `headless`: Run without UI
- `userDataDir`: Custom user data directory
- `windowSize`: Browser window dimensions
- `devtools`: Open DevTools on launch
- `args`: Additional Chrome arguments

### Page Configuration
- `viewport`: Page viewport dimensions
- `userAgent`: Custom user agent
- `locale`: Browser locale
- `timezoneId`: Timezone identifier

## 🔐 Security Considerations

- Always sanitize user input when executing JavaScript
- Use headless mode for automated tasks
- Clear sensitive data before closing
- Monitor network requests for sensitive information
- Use request interception to block unwanted resources

## 🚨 Troubleshooting

### Common Issues

1. **Chrome not found**
   - Ensure Chrome/Chromium is installed
   - Set `PUPPETEER_EXECUTABLE_PATH` environment variable

2. **Permission denied**
   - Check file permissions
   - Run with appropriate user permissions

3. **Timeout errors**
   - Increase timeout values
   - Check network connectivity

4. **Memory leaks**
   - Ensure proper cleanup
   - Close pages when done

### Debug Mode
Enable debug logging:
```bash
DEBUG=puppeteer:* node dist/index.js
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 🔗 Related Projects

- [Puppeteer](https://pptr.dev/) - Headless Chrome Node.js API
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Model Context Protocol](https://modelcontextprotocol.io/)