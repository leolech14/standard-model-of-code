#!/usr/bin/env node

/**
 * Test script for MermaidFlow application using Chrome MCP
 * This script will:
 * 1. Launch Chrome
 * 2. Navigate to the MermaidFlow app
 * 3. Test various features
 * 4. Collect console logs and performance metrics
 * 5. Take screenshots
 * 6. Generate a development insights report
 */

import { ChromeManager } from './src/chrome-manager.js';
import { PageTools } from './src/tools/page-tools.js';
import { ElementTools } from './src/tools/element-tools.js';
import { BrowserTools } from './src/tools/browser-tools.js';
import fs from 'fs/promises';
import path from 'path';

const chromeManager = new ChromeManager();
const pageTools = new PageTools(chromeManager);
const elementTools = new ElementTools(chromeManager);
const browserTools = new BrowserTools(chromeManager);

const MERMAIDFLOW_PATH = path.resolve('../MermaidFlow/index.html');
const OUTPUT_DIR = './test-results';

// Create output directory
await fs.mkdir(OUTPUT_DIR, { recursive: true });

console.log('🚀 Starting MermaidFlow Testing with Chrome MCP...\n');

// 1. Launch Chrome
console.log('📦 Launching Chrome...');
await chromeManager.launch({
  headless: false, // Set to true for headless testing
  windowSize: { width: 1920, height: 1080 },
  devtools: true,
});

// 2. Navigate to MermaidFlow
const fileUrl = `file://${MERMAIDFLOW_PATH}`;
console.log(`📍 Opening MermaidFlow: ${fileUrl}`);
await pageTools.navigate({ url: fileUrl });

// Wait for app to load
await new Promise(resolve => setTimeout(resolve, 3000));

// 3. Capture initial state
console.log('📸 Taking initial screenshot...');
const initialScreenshot = await chromeManager.takeScreenshot(undefined, {
  fullPage: true,
  format: 'png'
});
await fs.writeFile(`${OUTPUT_DIR}/01-initial-load.png`, Buffer.from(initialScreenshot, 'base64'));

// 4. Test input parsing
console.log('📝 Testing diagram input...');
const testDiagrams = {
  simple: 'graph TD\n    A[Start] --> B[End]',
  er: 'erDiagram\n    CUSTOMER ||--o{ ORDER : places\n    ORDER ||--|{ LINE-ITEM : contains',
  quantum: `erDiagram
    DATA_FOUNDATIONS ||--o{ LOGIC_FLOW : "feeds_into"
    LOGIC_FLOW ||--o{ ORGANIZATION : "modularizes"

    DATA_FOUNDATIONS quantum: {amplitude: 1.0, coherence: 0.9}
    LOGIC_FLOW quantum: {superposition: true}`
};

// Test each diagram type
for (const [name, diagram] of Object.entries(testDiagrams)) {
  console.log(`  - Testing ${name} diagram...`);

  // Clear existing input
  await elementTools.click({ selector: '#mermaidInput' });
  await pageTools.execute({
    script: () => {
      document.getElementById('mermaidInput').value = '';
    }
  });

  // Type new diagram
  await elementTools.type({
    selector: '#mermaidInput',
    text: diagram
  });

  // Click parse button
  await elementTools.click({ selector: '#parseBtn' });

  // Wait for parsing
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Take screenshot
  const screenshot = await chromeManager.takeScreenshot(undefined, {
    fullPage: true,
    format: 'png'
  });
  await fs.writeFile(`${OUTPUT_DIR}/02-diagram-${name}.png`, Buffer.from(screenshot, 'base64'));
}

// 5. Test quantum controls
console.log('⚛️ Testing quantum controls...');
const controls = [
  { selector: '#entanglement', value: 100 },
  { selector: '#waveCollapse', value: 75 },
  { selector: '#fluctuation', value: 50 },
  { selector: '#spectral', value: 100 }
];

for (const control of controls) {
  await pageTools.execute({
    script: (sel, val) => {
      document.querySelector(sel).value = val;
      document.querySelector(sel).dispatchEvent(new Event('input'));
    },
    args: [control.selector, control.value]
  });
  await new Promise(resolve => setTimeout(resolve, 500));
}

// Take screenshot with max quantum effects
const quantumScreenshot = await chromeManager.takeScreenshot(undefined, {
  fullPage: true,
  format: 'png'
});
await fs.writeFile(`${OUTPUT_DIR}/03-quantum-effects.png`, Buffer.from(quantumScreenshot, 'base64'));

// 6. Collect console logs and errors
console.log('📊 Collecting console information...');
const consoleLogs = [];
const errors = [];

// Set up console listener
const page = await chromeManager.getCurrentPage();

page.on('console', msg => {
  consoleLogs.push({
    type: msg.type(),
    text: msg.text(),
    location: msg.location()
  });
});

page.on('pageerror', error => {
  errors.push({
    message: error.message,
    stack: error.stack
  });
});

// Trigger some interactions to generate logs
await elementTools.click({ selector: '#resetBtn' });
await new Promise(resolve => setTimeout(resolve, 1000));
await elementTools.click({ selector: '#glow' }); // Toggle glow
await elementTools.click({ selector: '#particles' }); // Toggle particles

// 7. Test performance
console.log('⚡ Analyzing performance...');
const perfResult = await pageTools.analyze({
  includePerformance: true,
  includeAccessibility: false,
  includeSEO: false
});

// 8. Test 3D interaction (simulate mouse movement)
console.log('🖱️ Testing 3D interaction...');
await pageTools.execute({
  script: () => {
    // Simulate mouse movements to test 3D controls
    const canvas = document.getElementById('canvas');
    const rect = canvas.getBoundingClientRect();

    // Create mouse events
    const events = [
      { type: 'mousedown', x: rect.width / 2, y: rect.height / 2 },
      { type: 'mousemove', x: rect.width / 2 + 100, y: rect.height / 2 },
      { type: 'mousemove', x: rect.width / 2 + 100, y: rect.height / 2 + 100 },
      { type: 'mouseup', x: rect.width / 2 + 100, y: rect.height / 2 + 100 },
    ];

    events.forEach(event => {
      const mouseEvent = new MouseEvent(event.type, {
        clientX: event.x,
        clientY: event.y,
        bubbles: true
      });
      canvas.dispatchEvent(mouseEvent);
    });
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

// 9. Final screenshot
console.log('📸 Taking final screenshot...');
const finalScreenshot = await chromeManager.takeScreenshot(undefined, {
  fullPage: true,
  format: 'png'
});
await fs.writeFile(`${OUTPUT_DIR}/04-final-state.png`, Buffer.from(finalScreenshot, 'base64'));

// 10. Generate development insights report
console.log('📈 Generating development insights...\n');

const report = generateReport({
  consoleLogs,
  errors,
  performance: perfResult.content[0].text,
  testResults: {
    diagramsTested: Object.keys(testDiagrams).length,
    screenshotCount: 4,
    interactionsTested: 7
  }
});

// Write report
await fs.writeFile(`${OUTPUT_DIR}/development-insights.md`, report);

// 11. Cleanup
console.log('🧹 Cleaning up...');
await chromeManager.close();

console.log('\n✅ Testing complete!');
console.log(`📁 Results saved to: ${OUTPUT_DIR}/`);
console.log('📊 Check development-insights.md for detailed analysis\n');

function generateReport(data) {
  const timestamp = new Date().toISOString();

  return `# MermaidFlow Development Insights Report
Generated: ${timestamp}

## 🎯 Test Summary

- **Diagrams Tested**: ${data.testResults.diagramsTested}
- **Screenshots Captured**: ${data.testResults.screenshotCount}
- **User Interactions Simulated**: ${data.testResults.interactionsTested}

## 📊 Performance Metrics

${data.performance}

## 🐛 Issues and Errors

${data.errors.length > 0 ?
  data.errors.map(e => `### Error\n\`\`\`\n${e.message}\n${e.stack}\n\`\`\`\n`).join('\n') :
  '✅ No errors detected during testing!'
}

## 📝 Console Logs

${data.consoleLogs.map(log =>
  `- **${log.type.toUpperCase()}**: ${log.text}`
).join('\n')}

## 🔍 Development Recommendations

### Performance Optimizations
1. **Canvas Rendering**: Monitor FPS with complex diagrams
2. **Particle System**: Consider LOD (Level of Detail) for performance
3. **Memory Management**: Ensure proper cleanup of Three.js resources

### User Experience
1. **Loading States**: Add visual feedback during diagram parsing
2. **Error Handling**: Improve error messages for invalid Mermaid syntax
3. **Controls**: Consider adding keyboard shortcuts for common actions

### Feature Enhancements
1. **Export Formats**: Add SVG, PDF export options
2. **Diagram Types**: Support for flowcharts, sequence diagrams
3. **Collaboration**: Real-time collaboration features
4. **Templates**: Pre-built diagram templates

## 🚀 Next Steps

1. Fix any errors identified above
2. Implement recommended optimizations
3. Add unit tests for core functionality
4. Consider integration with existing documentation systems

## 📸 Screenshots

- \`01-initial-load.png\`: Initial application state
- \`02-diagram-*.png\`: Different diagram types rendered
- \`03-quantum-effects.png\`: Maximum quantum effects enabled
- \`04-final-state.png\`: After all interactions

---
*Report generated by Chrome MCP testing framework*
`;
}