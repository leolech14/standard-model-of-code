#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { ChromeManager } from './chrome-manager.js';
import { BrowserTools } from './tools/browser-tools.js';
import { PageTools } from './tools/page-tools.js';
import { NetworkTools } from './tools/network-tools.js';
import { ElementTools } from './tools/element-tools.js';

const server = new Server(
  {
    name: 'chrome-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize Chrome manager
const chromeManager = new ChromeManager();

// Register tool handlers
const browserTools = new BrowserTools(chromeManager);
const pageTools = new PageTools(chromeManager);
const networkTools = new NetworkTools(chromeManager);
const elementTools = new ElementTools(chromeManager);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // Browser management tools
      {
        name: 'chrome_launch',
        description: 'Launch Chrome browser instance',
        inputSchema: {
          type: 'object',
          properties: {
            headless: {
              type: 'boolean',
              description: 'Run Chrome in headless mode',
              default: false,
            },
            userDataDir: {
              type: 'string',
              description: 'Path to user data directory',
            },
            windowSize: {
              type: 'object',
              properties: {
                width: { type: 'number', default: 1920 },
                height: { type: 'number', default: 1080 },
              },
            },
          },
        },
      },
      {
        name: 'chrome_close',
        description: 'Close Chrome browser instance',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'chrome_new_tab',
        description: 'Open a new tab',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL to navigate to',
            },
            active: {
              type: 'boolean',
              description: 'Make tab active',
              default: true,
            },
          },
        },
      },

      // Page navigation tools
      {
        name: 'page_navigate',
        description: 'Navigate to a URL',
        inputSchema: {
          type: 'object',
          properties: {
            url: {
              type: 'string',
              description: 'URL to navigate to',
            },
            waitUntil: {
              type: 'string',
              enum: ['load', 'domcontentloaded', 'networkidle0', 'networkidle2'],
              default: 'load',
            },
            timeout: {
              type: 'number',
              default: 30000,
            },
          },
          required: ['url'],
        },
      },
      {
        name: 'page_screenshot',
        description: 'Take a screenshot of the current page',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['png', 'jpeg'],
              default: 'png',
            },
            fullPage: {
              type: 'boolean',
              default: true,
            },
            selector: {
              type: 'string',
              description: 'CSS selector to capture specific element',
            },
            quality: {
              type: 'number',
              minimum: 0,
              maximum: 100,
              description: 'JPEG quality (0-100)',
            },
          },
        },
      },
      {
        name: 'page_content',
        description: 'Get page content (HTML, text, or markdown)',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['html', 'text', 'markdown'],
              default: 'text',
            },
            selector: {
              type: 'string',
              description: 'CSS selector to get content from specific element',
            },
          },
        },
      },
      {
        name: 'page_execute',
        description: 'Execute JavaScript in the page context',
        inputSchema: {
          type: 'object',
          properties: {
            script: {
              type: 'string',
              description: 'JavaScript code to execute',
            },
            args: {
              type: 'array',
              items: { type: 'string' },
              description: 'Arguments to pass to the script',
            },
            waitForResult: {
              type: 'boolean',
              default: true,
            },
          },
          required: ['script'],
        },
      },

      // Element interaction tools
      {
        name: 'element_click',
        description: 'Click an element',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector of element to click',
            },
            waitForSelector: {
              type: 'boolean',
              default: true,
            },
            timeout: {
              type: 'number',
              default: 5000,
            },
          },
          required: ['selector'],
        },
      },
      {
        name: 'element_type',
        description: 'Type text into an input field',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector of input field',
            },
            text: {
              type: 'string',
              description: 'Text to type',
            },
            clear: {
              type: 'boolean',
              default: true,
            },
            delay: {
              type: 'number',
              default: 10,
            },
          },
          required: ['selector', 'text'],
        },
      },
      {
        name: 'element_select',
        description: 'Select an option from a dropdown',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector of select element',
            },
            value: {
              type: 'string',
              description: 'Value of option to select',
            },
          },
          required: ['selector', 'value'],
        },
      },

      // Network monitoring tools
      {
        name: 'network_requests',
        description: 'Get network request log',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              default: 50,
            },
            filter: {
              type: 'object',
              properties: {
                url: { type: 'string' },
                method: { type: 'string' },
                status: { type: 'number' },
              },
            },
          },
        },
      },
      {
        name: 'network_block',
        description: 'Block network requests',
        inputSchema: {
          type: 'object',
          properties: {
            patterns: {
              type: 'array',
              items: { type: 'string' },
              description: 'URL patterns to block (glob patterns)',
            },
          },
          required: ['patterns'],
        },
      },

      // Page analysis tools
      {
        name: 'page_analyze',
        description: 'Analyze page structure and performance',
        inputSchema: {
          type: 'object',
          properties: {
            includePerformance: {
              type: 'boolean',
              default: true,
            },
            includeAccessibility: {
              type: 'boolean',
              default: true,
            },
            includeSEO: {
              type: 'boolean',
              default: true,
            },
          },
        },
      },
      {
        name: 'page_links',
        description: 'Extract all links from the page',
        inputSchema: {
          type: 'object',
          properties: {
            selector: {
              type: 'string',
              description: 'CSS selector to limit search to specific area',
            },
            externalOnly: {
              type: 'boolean',
              default: false,
            },
          },
        },
      },
      {
        name: 'page_forms',
        description: 'Extract all forms from the page',
        inputSchema: {
          type: 'object',
          properties: {
            includeInputs: {
              type: 'boolean',
              default: true,
            },
          },
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      // Browser management
      case 'chrome_launch':
        return await browserTools.launch(args);
      case 'chrome_close':
        return await browserTools.close(args);
      case 'chrome_new_tab':
        return await browserTools.newTab(args);

      // Page navigation
      case 'page_navigate':
        return await pageTools.navigate(args);
      case 'page_screenshot':
        return await pageTools.screenshot(args);
      case 'page_content':
        return await pageTools.getContent(args);
      case 'page_execute':
        return await pageTools.execute(args);

      // Element interaction
      case 'element_click':
        return await elementTools.click(args);
      case 'element_type':
        return await elementTools.type(args);
      case 'element_select':
        return await elementTools.select(args);

      // Network monitoring
      case 'network_requests':
        return await networkTools.getRequests(args);
      case 'network_block':
        return await networkTools.blockRequests(args);

      // Page analysis
      case 'page_analyze':
        return await pageTools.analyze(args);
      case 'page_links':
        return await pageTools.getLinks(args);
      case 'page_forms':
        return await pageTools.getForms(args);

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${name}`
        );
    }
  } catch (error) {
    console.error(`Error executing ${name}:`, error);
    throw new McpError(
      ErrorCode.InternalError,
      `Tool execution failed: ${error.message}`
    );
  }
});

// Cleanup on exit
process.on('SIGINT', async () => {
  console.log('\nShutting down Chrome MCP server...');
  await chromeManager.cleanup();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('\nShutting down Chrome MCP server...');
  await chromeManager.cleanup();
  process.exit(0);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Chrome MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});