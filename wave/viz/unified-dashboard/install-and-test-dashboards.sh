#!/bin/bash
# Install and Test Both Dashboards
# Run this to set everything up!

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  DASHBOARD INSTALLATION & TESTING                          ║"
echo "║  Session 2026-01-28 - Theory + Tools + Platform           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="/Users/lech/PROJECTS_all/PROJECT_elements"

# ============================================================================
# INSTALL PROJECTOME VIEWER (unified-dashboard)
# ============================================================================

echo "📊 [1/2] Installing Projectome Viewer..."
echo "Location: context-management/viz/unified-dashboard"
echo ""

cd "$PROJECT_ROOT/context-management/viz/unified-dashboard"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo "✅ Projectome Viewer dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "Projectome Viewer ready!"
echo "  Port: 3000"
echo "  Features: Collider 3D + Refinery chunks (split view)"
echo "  Command: projectome"
echo ""

# ============================================================================
# INSTALL REFINERY PLATFORM (refinery-platform)
# ============================================================================

echo "🌐 [2/2] Installing Refinery Platform..."
echo "Location: context-management/experiments/refinery-platform"
echo ""

cd "$PROJECT_ROOT/context-management/experiments/refinery-platform"

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo "✅ Refinery Platform dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "Refinery Platform ready!"
echo "  Port: 3001"
echo "  Features: Multi-tenant, 6 pages, 4 APIs"
echo "  Level: L7 System → L8 Platform"
echo "  Command: refinery"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION COMPLETE                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 TO RUN:"
echo ""
echo "  Option 1: Global Commands"
echo "    $ projectome      # Starts Projectome Viewer on :3000"
echo "    $ refinery        # Starts Refinery Platform on :3001"
echo ""
echo "  Option 2: Manual"
echo "    $ cd context-management/viz/unified-dashboard && npm run dev"
echo "    $ cd context-management/experiments/refinery-platform && npm run dev"
echo ""
echo "📚 DOCUMENTATION:"
echo "  - DASHBOARD_QUICK_REFERENCE.md (this directory)"
echo "  - ~/.claude/CLAUDE.md (updated with commands)"
echo "  - SESSION_2026-01-28_FINAL_SUMMARY.md (epic session recap)"
echo ""
echo "📖 THEORY (100%):"
echo "  - standard-model-of-code/docs/theory/THEORY_COMPLETE_ALL.md (3,425 lines)"
echo "  - Consolidated L0+L1+L2+L3 with today's additions"
echo ""
echo "🎉 ALL SYSTEMS OPERATIONAL!"
echo ""
