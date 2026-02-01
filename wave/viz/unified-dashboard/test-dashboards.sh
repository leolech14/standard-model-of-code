#!/bin/bash
# Test Both Dashboards - Run this script to test everything!

set -e

echo "🧪 TESTING DASHBOARDS"
echo "===================="
echo ""

# Test 1: Projectome Viewer (unified-dashboard)
echo "📊 TEST 1: Projectome Viewer (unified-dashboard)"
echo "Location: context-management/viz/unified-dashboard"
echo "Port: 3000"
echo ""

cd /Users/lech/PROJECTS_all/PROJECT_elements/context-management/viz/unified-dashboard

echo "Installing dependencies..."
npm install

echo ""
echo "✅ unified-dashboard ready!"
echo "Start with: npm run dev"
echo "Or use command: projectome"
echo ""
echo "Press ENTER to test Refinery Platform next..."
read

# Test 2: Refinery Platform
echo ""
echo "🌐 TEST 2: Refinery Platform (refinery-platform)"
echo "Location: context-management/experiments/refinery-platform"
echo "Port: 3001"
echo ""

cd /Users/lech/PROJECTS_all/PROJECT_elements/context-management/experiments/refinery-platform

echo "Installing dependencies..."
npm install

echo ""
echo "✅ refinery-platform ready!"
echo "Start with: npm run dev"
echo "Or use command: refinery"
echo ""

echo "===================="
echo "🎉 BOTH DASHBOARDS INSTALLED!"
echo ""
echo "To run:"
echo "  projectome  # Opens :3000 (Projectome Viewer)"
echo "  refinery    # Opens :3001 (Multi-Tenant Platform)"
echo ""
echo "Or manually:"
echo "  cd context-management/viz/unified-dashboard && npm run dev"
echo "  cd context-management/experiments/refinery-platform && npm run dev"
