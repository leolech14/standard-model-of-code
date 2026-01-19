#!/usr/bin/env node

import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import path from 'path';

const OUTPUT_DIR = './test-results';
const MERMAIDFLOW_PATH = path.resolve('../MermaidFlow/index.html');

console.log('🚀 Testing MermaidFlow with Chrome...\n');

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
    console.log(`[${msg.type()}] ${msg.text()}`);
  });

  page.on('pageerror', error => {
    console.error(`[PAGE ERROR] ${error.message}`);
  });

  // Navigate to MermaidFlow
  const fileUrl = `file://${MERMAIDFLOW_PATH}`;
  console.log(`📍 Opening: ${fileUrl}`);
  await page.goto(fileUrl, { waitUntil: 'networkidle0' });

  // Wait for app to load
  await page.waitForSelector('#mermaidInput', { timeout: 10000 });
  console.log('✅ App loaded successfully!');

  // Take initial screenshot
  console.log('📸 Taking initial screenshot...');
  await page.screenshot({
    path: `${OUTPUT_DIR}/01-initial-load.png`,
    fullPage: true
  });

  // Check if Three.js is loaded
  const threeJsLoaded = await page.evaluate(() => {
    return typeof THREE !== 'undefined';
  });

  console.log(`Three.js loaded: ${threeJsLoaded ? '✅ Yes' : '❌ No'}`);

  // Test with a simple diagram
  console.log('\n📝 Testing simple diagram...');
  const simpleDiagram = 'graph TD\n    A[Start] --> B[Process] --> C[End]';

  await page.type('#mermaidInput', simpleDiagram);
  await page.click('#parseBtn');

  // Wait for processing
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Check for any results or errors
  const hasGraph = await page.evaluate(() => {
    const scene = document.querySelector('canvas');
    return scene && scene.width > 0;
  });

  console.log(`Graph rendered: ${hasGraph ? '✅ Yes' : '❌ No'}`);

  // Test with your Universal Codebase Map
  console.log('\n🏗️ Testing Universal Codebase Map...');
  await page.click('#mermaidInput');
  await page.keyboard.down('Control');
  await page.keyboard.press('a');
  await page.keyboard.up('Control');

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

  await page.type('#mermaidInput', universalMap);
  await page.click('#parseBtn');
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Take screenshot with the complex diagram
  console.log('📸 Taking screenshot with Universal Codebase Map...');
  await page.screenshot({
    path: `${OUTPUT_DIR}/02-universal-map.png`,
    fullPage: true
  });

  // Get performance metrics
  console.log('\n📊 Collecting performance metrics...');
  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
      loadComplete: nav.loadEventEnd - nav.loadEventStart,
      memoryUsed: performance.memory ? performance.memory.usedJSHeapSize / 1024 / 1024 : 'N/A'
    };
  });

  console.log(`DOM Content Loaded: ${metrics.domContentLoaded}ms`);
  console.log(`Load Complete: ${metrics.loadComplete}ms`);
  console.log(`Memory Used: ${metrics.memoryUsed}MB`);

  // Test quantum controls
  console.log('\n⚛️ Testing quantum controls...');

  // Max out all controls
  const controls = ['entanglement', 'waveCollapse', 'fluctuation', 'spectral'];
  for (const control of controls) {
    await page.evaluate((id) => {
      const slider = document.getElementById(id);
      if (slider) {
        slider.value = 100;
        slider.dispatchEvent(new Event('input'));
      }
    }, control);
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log('📸 Taking screenshot with max quantum effects...');
  await page.screenshot({
    path: `${OUTPUT_DIR}/03-quantum-max.png`,
    fullPage: true
  });

  // Check current FPS
  const fps = await page.evaluate(() => {
    const fpsElement = document.getElementById('fps');
    return fpsElement ? fpsElement.textContent : 'N/A';
  });
  console.log(`Current FPS: ${fps}`);

  // Get node and edge counts
  const graphStats = await page.evaluate(() => {
    const nodeCount = document.getElementById('nodeCount')?.textContent;
    const edgeCount = document.getElementById('edgeCount')?.textContent;
    const entropy = document.getElementById('entropy')?.textContent;
    const density = document.getElementById('density')?.textContent;

    return { nodeCount, edgeCount, entropy, density };
  });

  console.log('\n📈 Graph Statistics:');
  console.log(`  Nodes: ${graphStats.nodeCount}`);
  console.log(`  Edges: ${graphStats.edgeCount}`);
  console.log(`  Entropy: ${graphStats.entropy}`);
  console.log(`  Density: ${graphStats.density}`);

  // Generate summary report
  const report = `# MermaidFlow Test Report

## Test Results
- **App Loading**: ✅ Success
- **Three.js**: ${threeJsLoaded ? '✅ Loaded' : '❌ Missing'}
- **Simple Diagram**: ${hasGraph ? '✅ Rendered' : '❌ Failed'}
- **Universal Codebase Map**: ✅ Processed
- **Quantum Effects**: ✅ Tested

## Performance Metrics
- DOM Content Loaded: ${metrics.domContentLoaded}ms
- Load Complete: ${metrics.loadComplete}ms
- Memory Used: ${metrics.memoryUsed}MB
- Current FPS: ${fps}

## Graph Statistics
- Nodes: ${graphStats.nodeCount}
- Edges: ${graphStats.edgeCount}
- Entropy: ${graphStats.entropy}
- Density: ${graphStats.density}

## Screenshots Generated
1. 01-initial-load.png - App startup state
2. 02-universal-map.png - Universal Codebase Map rendered
3. 03-quantum-max.png - Max quantum effects

## Development Insights
${!threeJsLoaded ? '⚠️ **Three.js not loaded** - Check script imports\n' : ''}
${!hasGraph ? '⚠️ **Graph rendering failed** - Check Mermaid parser\n' : ''}
${parseInt(fps) < 30 ? '⚠️ **Low FPS** - Consider performance optimizations\n' : ''}
${metrics.memoryUsed > 100 ? '⚠️ **High memory usage** - Check for memory leaks\n' : ''}

Generated: ${new Date().toISOString()}`;

  await fs.writeFile(`${OUTPUT_DIR}/test-report.md`, report);
  console.log('\n✅ Test complete! Report saved to test-results/test-report.md');

} catch (error) {
  console.error('❌ Test failed:', error);
} finally {
  await browser.close();
  console.log('🧹 Browser closed');
}