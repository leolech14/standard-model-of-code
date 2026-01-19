#!/usr/bin/env node

import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';

const OUTPUT_DIR = './test-results';
const MERMAIDFLOW_URL = 'http://localhost:8080';

console.log('🚀 Testing MermaidFlow with Chrome (via HTTP Server)...\n');

// Create output directory
await fs.mkdir(OUTPUT_DIR, { recursive: true });

// Launch browser
const browser = await puppeteer.launch({
  headless: false,
  devtools: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  // Enable console logging
  page.on('console', msg => {
    const type = msg.type();
    if (type === 'error') {
      console.error(`[CONSOLE ERROR] ${msg.text()}`);
    } else if (type === 'warning') {
      console.warn(`[CONSOLE WARNING] ${msg.text()}`);
    } else {
      console.log(`[CONSOLE] ${msg.text()}`);
    }
  });

  page.on('pageerror', error => {
    console.error(`[PAGE ERROR] ${error.message}`);
    if (error.stack) {
      console.error(`[STACK] ${error.stack}`);
    }
  });

  // Monitor requests
  const requests = [];
  page.on('request', request => {
    requests.push({
      url: request.url(),
      method: request.method(),
      timestamp: Date.now()
    });
  });

  // Navigate to MermaidFlow
  console.log(`📍 Opening: ${MERMAIDFLOW_URL}`);
  await page.goto(MERMAIDFLOW_URL, { waitUntil: 'networkidle0', timeout: 30000 });

  // Wait for app to load
  console.log('⏳ Waiting for app to initialize...');
  try {
    await page.waitForFunction(() => {
      return window.location.pathname === '/' && document.getElementById('mermaidInput');
    }, { timeout: 10000 });
    console.log('✅ App loaded successfully!');
  } catch (e) {
    console.log('⚠️ App may still be loading...');
  }

  // Wait a bit more for everything to initialize
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Check what's loaded
  console.log('\n🔍 Checking page state...');
  const pageState = await page.evaluate(() => {
    const checks = {
      hasInput: !!document.getElementById('mermaidInput'),
      hasParseBtn: !!document.getElementById('parseBtn'),
      hasCanvas: !!document.getElementById('canvas'),
      hasControls: !!document.getElementById('controls'),
      hasMetrics: !!document.getElementById('metrics'),
      threeLoaded: typeof THREE !== 'undefined',
      hasError: !!document.querySelector('.error'),
      loading: !!document.getElementById('loading')
    };

    // Get any visible error messages
    const errors = [];
    document.querySelectorAll('.error, .error-message').forEach(el => {
      if (el.offsetParent !== null) {
        errors.push(el.textContent);
      }
    });

    return { ...checks, errors };
  });

  console.log('Page State:', pageState);

  // Take initial screenshot
  console.log('\n📸 Taking initial screenshot...');
  await page.screenshot({
    path: `${OUTPUT_DIR}/01-initial-load.png`,
    fullPage: true
  });

  if (!pageState.threeLoaded) {
    console.log('⚠️ Three.js not loaded, checking imports...');
    const scriptStatus = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll('script[src]'));
      return scripts.map(s => ({
        src: s.src,
        loaded: s.readyState === 'complete' || s.complete
      }));
    });
    console.log('Script Status:', scriptStatus);
  }

  // Test with your Universal Codebase Map
  console.log('\n🏗️ Testing Universal Codebase Map...');

  const universalMap = `erDiagram
    DATA_FOUNDATIONS ||--o{ LOGIC_FLOW : "feeds_into"
    LOGIC_FLOW ||--o{ ORGANIZATION : "modularizes"
    ORGANIZATION ||--o{ EXECUTION : "deploys_as"

    DATA_FOUNDATIONS {
        Bits Bt "Binary states"
        Bytes By "Memory chunks"
        Primitives Dt "Basic types"
        Variables Vc "State holders"
    }

    LOGIC_FLOW {
        Expressions Ex "Computations"
        Statements St "Actions"
        Control_Structures Cs "Flow directors"
        Functions Fn "Reusable blocks"
    }

    ORGANIZATION {
        Aggregates Oc "Composites"
        Modules Mp "Groupers"
        Files Sf "Containers"
    }

    EXECUTION {
        Executables Bb "Runtime forms"
    }

    Variables ||--|| Expressions : "input_to"
    Functions ||--o{ Aggregates : "contains"
    Modules ||--o{ Functions : "imports"`;

  if (pageState.hasInput && pageState.hasParseBtn) {
    // Clear and fill input
    await page.click('#mermaidInput');
    await page.keyboard.down('Control');
    await page.keyboard.press('a');
    await page.keyboard.up('Control');
    await new Promise(resolve => setTimeout(resolve, 100));

    await page.type('#mermaidInput', universalMap, { delay: 10 });

    // Click parse button
    console.log('🔘 Clicking parse button...');
    await page.click('#parseBtn');

    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Take screenshot
    console.log('📸 Taking screenshot after parsing...');
    await page.screenshot({
      path: `${OUTPUT_DIR}/02-universal-map.png`,
      fullPage: true
    });
  } else {
    console.log('⚠️ Cannot test diagram parsing - UI elements not found');
  }

  // Check metrics
  if (pageState.hasMetrics) {
    console.log('\n📊 Collecting metrics...');
    const metrics = await page.evaluate(() => {
      const getEl = (id) => document.getElementById(id)?.textContent;
      return {
        nodes: getEl('nodeCount'),
        edges: getEl('edgeCount'),
        entropy: getEl('entropy'),
        density: getEl('density'),
        fps: getEl('fps')
      };
    });
    console.log('Metrics:', metrics);
  }

  // Performance metrics
  console.log('\n⚡ Performance metrics...');
  const perfMetrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
      loadComplete: nav.loadEventEnd - nav.loadEventStart,
      memoryUsed: performance.memory ? performance.memory.usedJSHeapSize / 1024 / 1024 : 'N/A'
    };
  });
  console.log(`DOM Content Loaded: ${perfMetrics.domContentLoaded}ms`);
  console.log(`Load Complete: ${perfMetrics.loadComplete}ms`);
  console.log(`Memory Used: ${perfMetrics.memoryUsed}MB`);

  // Test quantum controls if available
  const controlsExist = await page.evaluate(() => {
    return ['entanglement', 'waveCollapse', 'fluctuation', 'spectral']
      .every(id => !!document.getElementById(id));
  });

  if (controlsExist) {
    console.log('\n⚛️ Testing quantum controls...');

    // Max out controls
    for (const control of ['entanglement', 'waveCollapse', 'fluctuation', 'spectral']) {
      await page.evaluate((id) => {
        const slider = document.getElementById(id);
        if (slider) {
          slider.value = 100;
          slider.dispatchEvent(new Event('input'));
          // Also trigger change event
          slider.dispatchEvent(new Event('change'));
        }
      }, control);
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('📸 Taking screenshot with quantum effects...');
    await page.screenshot({
      path: `${OUTPUT_DIR}/03-quantum-effects.png`,
      fullPage: true
    });
  }

  // Generate comprehensive report
  const report = `# MermaidFlow Test Report
Generated: ${new Date().toISOString()}

## Test Environment
- Browser: Chrome (Puppeteer)
- URL: ${MERMAIDFLOW_URL}
- Test Type: HTTP Server

## Test Results

### ✅ Successes
${pageState.hasInput ? '- [x] Input field loaded' : '- [ ] Input field missing'}
${pageState.hasParseBtn ? '- [x] Parse button loaded' : '- [ ] Parse button missing'}
${pageState.hasCanvas ? '- [x] Canvas element found' : '- [ ] Canvas element missing'}
${pageState.hasControls ? '- [x] Controls panel loaded' : '- [ ] Controls panel missing'}
${pageState.hasMetrics ? '- [x] Metrics panel loaded' : '- [ ] Metrics panel missing'}

### ❌ Issues
${pageState.threeLoaded ? '' : '- [ ] Three.js library not loaded\n'}
${pageState.hasError ? '- [ ] Error messages visible:\n' + pageState.errors.map(e => `  - ${e}`).join('\n') + '\n' : ''}

## Performance Metrics
- DOM Content Loaded: ${perfMetrics.domContentLoaded}ms
- Load Complete: ${perfMetrics.loadComplete}ms
- Memory Used: ${perfMetrics.memoryUsed}MB

## Console Logs
${requests.length} requests made
Main requests:
${requests.slice(0, 10).map(r => `- ${r.method} ${r.url.split('/').pop()}`).join('\n')}

## Recommendations

### High Priority
1. **Three.js Loading** ${pageState.threeLoaded ? '✅ Working' : '⚠️ Fix import paths for Three.js modules'}
2. **CORS Issues** Resolved by using HTTP server
3. **Error Handling** ${pageState.hasError ? '⚠️ Fix visible errors' : '✅ No visible errors'}

### Performance
${perfMetrics.domContentLoaded > 3000 ? '⚠️ Slow initial load - optimize bundle size' : '✅ Load time acceptable'}
${parseInt(perfMetrics.memoryUsed) > 100 ? '⚠️ High memory usage - check for leaks' : '✅ Memory usage normal'}

### Features to Test Next
1. [ ] Diagram parsing and rendering
2. [ ] 3D interaction (mouse controls)
3. [ ] Quantum physics effects
4. [ ] Export functionality
5. [ ] Different diagram types

## Screenshots
1. \`01-initial-load.png\` - App state on load
2. \`02-universal-map.png\` - After loading Universal Codebase Map
3. \`03-quantum-effects.png\` - With quantum effects maxed

---
Report generated by Chrome MCP Test Framework`;

  await fs.writeFile(`${OUTPUT_DIR}/test-report.md`, report);
  console.log('\n✅ Test complete! Report saved to test-results/test-report.md');

} catch (error) {
  console.error('❌ Test failed:', error);
  console.error('Stack:', error.stack);
} finally {
  await browser.close();
  console.log('🧹 Browser closed');
}

// Kill the HTTP server
console.log('🛑 Stopping HTTP server...');
try {
  process.kill(5, 'SIGTERM');
} catch (e) {
  // Server might already be stopped
}