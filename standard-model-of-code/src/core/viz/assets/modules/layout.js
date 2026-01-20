/**
 * ═══════════════════════════════════════════════════════════════════════════
 * LAYOUT MODULE - Unified UI Layout Engine
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * MIGRATED FROM: app.js HudLayoutManager (390 lines)
 * This is the SINGLE SOURCE OF TRUTH for UI layout intelligence.
 *
 * Features:
 *   - Panel placement with collision avoidance (from HudLayoutManager)
 *   - Component registration system (NEW)
 *   - Toast/control-bar collision detection (NEW)
 *   - Min-width graph validation (NEW)
 *   - Debug overlay with Ctrl+Shift+L (NEW)
 *
 * @module LAYOUT
 * @version 2.0.0
 * @confidence 94%
 */

window.LAYOUT = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // CONFIGURATION (from HudLayoutManager)
    // ═══════════════════════════════════════════════════════════════════════

    const CONFIG = {
        MARGIN: 16,
        MIN_GRAPH_WIDTH: 320,
        REFLOW_THROTTLE_MS: 50,
        DEBUG_COLORS: {
            dock: 'rgba(100, 150, 255, 0.3)',
            overlay: 'rgba(255, 150, 100, 0.3)',
            floating: 'rgba(100, 255, 150, 0.3)',
            fixed: 'rgba(150, 150, 150, 0.3)'
        }
    };

    // Panels by priority (higher = more important, won't be moved)
    // MIGRATED from HudLayoutManager
    const FIXED_PANELS = ['top-left-header', 'stats-panel', 'metrics-panel', 'bottom-dock', 'report-panel', 'side-dock'];
    const DYNAMIC_PANELS = ['hover-panel', 'file-panel', 'selection-panel'];

    // ═══════════════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════════════

    // Throttle state (from HudLayoutManager)
    let _rafPending = false;
    let _lastReflow = 0;

    // Mouse position for hover-panel placement (from HudLayoutManager)
    let _mouseX = 0;
    let _mouseY = 0;

    // Component registry (NEW)
    const _registry = new Map();

    // Debug overlay state (NEW)
    let _debugEnabled = false;
    let _debugOverlay = null;

    // ═══════════════════════════════════════════════════════════════════════
    // VIEWPORT & RECT UTILITIES (from HudLayoutManager)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Get viewport rectangle with margins
     */
    function getViewport() {
        return {
            left: CONFIG.MARGIN,
            top: CONFIG.MARGIN,
            right: window.innerWidth - CONFIG.MARGIN,
            bottom: window.innerHeight - CONFIG.MARGIN,
            width: window.innerWidth - 2 * CONFIG.MARGIN,
            height: window.innerHeight - 2 * CONFIG.MARGIN
        };
    }

    /**
     * Check if sidebar is effectively "open" (occupying space)
     */
    function isSidebarOpen() {
        const sideDock = document.getElementById('side-dock');
        if (!sideDock) return false;
        const state = window.SIDEBAR_STATE;
        return (state && (state.locked || state.open)) ||
            sideDock.classList.contains('locked') ||
            sideDock.classList.contains('expanded') ||
            sideDock.matches(':hover');
    }

    /**
     * Get rectangle for an element (returns null if hidden/missing)
     */
    function getRect(el) {
        if (!el) return null;
        if (typeof el === 'string') {
            el = document.getElementById(el) || document.querySelector(el);
        }
        if (!el) return null;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return null;
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) return null;
        return { left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height };
    }

    /**
     * Get sidebar occupied region (full expanded width when open)
     */
    function getSidebarRect() {
        const sideDock = document.getElementById('side-dock');
        if (!sideDock || !isSidebarOpen()) return null;
        const sideWidth = parseInt(getComputedStyle(sideDock).getPropertyValue('--side-width')) || 260;
        return {
            left: 0,
            top: 0,
            right: 16 + sideWidth + 20,
            bottom: window.innerHeight,
            width: 16 + sideWidth + 20,
            height: window.innerHeight
        };
    }

    /**
     * Get all occupied rectangles (fixed panels + sidebar when open)
     */
    function getOccupiedRects() {
        const rects = [];

        // Sidebar takes priority when open
        const sidebarRect = getSidebarRect();
        if (sidebarRect) rects.push(sidebarRect);

        // Fixed panels
        FIXED_PANELS.forEach(id => {
            if (id === 'side-dock') return;
            const el = document.getElementById(id) || document.querySelector('.' + id);
            const rect = getRect(el);
            if (rect) rects.push(rect);
        });

        // Top-left header (special case - class-based)
        const topLeft = document.querySelector('.top-left');
        const topLeftRect = getRect(topLeft);
        if (topLeftRect) rects.push(topLeftRect);

        return rects;
    }

    /**
     * Calculate overlap area between two rectangles
     */
    function overlapArea(r1, r2) {
        if (!r1 || !r2) return 0;
        const xOverlap = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
        const yOverlap = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
        return xOverlap * yOverlap;
    }

    /**
     * Check if rect is fully inside viewport
     */
    function isInsideViewport(rect, viewport) {
        return rect.left >= viewport.left &&
            rect.top >= viewport.top &&
            rect.right <= viewport.right &&
            rect.bottom <= viewport.bottom;
    }

    /**
     * Clamp position to keep panel inside viewport
     */
    function clampToViewport(pos, panelWidth, panelHeight, viewport) {
        return {
            left: Math.max(viewport.left, Math.min(pos.left, viewport.right - panelWidth)),
            top: Math.max(viewport.top, Math.min(pos.top, viewport.bottom - panelHeight))
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CANDIDATE GENERATION (from HudLayoutManager)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Generate candidate positions for file panel
     */
    function getFilePanelCandidates(panelWidth, panelHeight) {
        const vp = getViewport();
        const margin = 20;
        const sidebarOpen = isSidebarOpen();
        const sidebarWidth = sidebarOpen ? 300 : 0;

        return sidebarOpen ? [
            { left: vp.right - panelWidth - margin, top: vp.top + margin },
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin },
            { left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin },
            { left: sidebarWidth + margin, top: vp.top + margin }
        ] : [
            { left: vp.left + margin, top: vp.bottom - panelHeight - margin },
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin },
            { left: vp.right - panelWidth - margin, top: vp.top + margin },
            { left: vp.left + margin, top: vp.top + margin }
        ];
    }

    /**
     * Generate candidate positions for selection panel
     */
    function getSelectionPanelCandidates(panelWidth, panelHeight) {
        const vp = getViewport();
        const margin = 20;
        const sidebarOpen = isSidebarOpen();
        const sidebarWidth = sidebarOpen ? 300 : 0;

        return sidebarOpen ? [
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin },
            { left: vp.right - panelWidth - margin, top: vp.top + margin },
            { left: sidebarWidth + margin, top: vp.bottom - panelHeight - margin },
            { left: sidebarWidth + margin, top: vp.top + margin }
        ] : [
            { left: vp.right - panelWidth - margin, top: vp.bottom - panelHeight - margin },
            { left: vp.right - panelWidth - margin, top: vp.top + margin },
            { left: vp.left + margin, top: vp.bottom - panelHeight - margin },
            { left: vp.left + margin, top: vp.top + margin }
        ];
    }

    /**
     * Get screen centroid of selected nodes
     */
    function getSelectionCentroid() {
        const Graph = window.Graph;
        const selectedIds = window.SELECTED_NODE_IDS;
        if (!Graph || !Graph.graphData || !selectedIds || selectedIds.size === 0) return null;

        const nodes = Graph.graphData().nodes || [];
        const selectedNodes = nodes.filter(n => selectedIds.has(n.id));
        if (selectedNodes.length === 0) return null;

        let sumX = 0, sumY = 0, sumZ = 0;
        selectedNodes.forEach(n => {
            sumX += n.x || 0;
            sumY += n.y || 0;
            sumZ += n.z || 0;
        });
        const centroid3D = {
            x: sumX / selectedNodes.length,
            y: sumY / selectedNodes.length,
            z: sumZ / selectedNodes.length
        };

        const camera = Graph.camera();
        if (!camera || !window.THREE) return null;
        const vector = new window.THREE.Vector3(centroid3D.x, centroid3D.y, centroid3D.z);
        vector.project(camera);
        return {
            x: (vector.x * 0.5 + 0.5) * window.innerWidth,
            y: (-vector.y * 0.5 + 0.5) * window.innerHeight
        };
    }

    /**
     * Generate candidate positions for hover panel
     */
    function getHoverPanelCandidates(mouseX, mouseY, panelWidth, panelHeight) {
        const vp = getViewport();
        const offset = 16;

        let anchorX = mouseX;
        let anchorY = mouseY;

        const hoveredNode = window.HOVERED_NODE;
        const selectedIds = window.SELECTED_NODE_IDS;
        if (hoveredNode && selectedIds && selectedIds.has(hoveredNode.id)) {
            const centroid = getSelectionCentroid();
            if (centroid) {
                anchorX = mouseX * 0.3 + centroid.x * 0.7;
                anchorY = mouseY * 0.3 + centroid.y * 0.7;
            }
        }

        const sidebarOpen = isSidebarOpen();
        const sidebarRect = sidebarOpen ? getSidebarRect() : null;
        const minLeft = sidebarRect ? sidebarRect.right + offset : vp.left;

        let candidates = [
            { left: anchorX + offset, top: anchorY - panelHeight - offset },
            { left: anchorX + offset, top: anchorY + offset },
            { left: anchorX - panelWidth - offset, top: anchorY + offset },
            { left: anchorX - panelWidth - offset, top: anchorY - panelHeight - offset }
        ];

        if (sidebarRect) {
            candidates = candidates.map(c => ({
                left: Math.max(c.left, minLeft),
                top: c.top
            }));
        }

        return candidates;
    }

    /**
     * Update mouse position
     */
    function updateMousePosition(x, y) {
        _mouseX = x;
        _mouseY = y;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // PANEL PLACEMENT (from HudLayoutManager)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Place a panel at the best position (least overlap)
     */
    function placePanel(panelEl, candidates, occupiedRects) {
        if (!panelEl) return null;

        const rect = panelEl.getBoundingClientRect();
        const panelWidth = rect.width || 400;
        const panelHeight = rect.height || 350;
        const viewport = getViewport();

        let bestPos = candidates[0];
        let bestOverlap = Infinity;

        for (const pos of candidates) {
            const clampedPos = clampToViewport(pos, panelWidth, panelHeight, viewport);
            const panelRect = {
                left: clampedPos.left,
                top: clampedPos.top,
                right: clampedPos.left + panelWidth,
                bottom: clampedPos.top + panelHeight
            };

            let totalOverlap = 0;
            for (const occRect of occupiedRects) {
                totalOverlap += overlapArea(panelRect, occRect);
            }

            if (!isInsideViewport(panelRect, viewport)) {
                totalOverlap += 10000;
            }

            if (totalOverlap < bestOverlap) {
                bestOverlap = totalOverlap;
                bestPos = clampedPos;
                if (totalOverlap === 0) break;
            }
        }

        return bestPos;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TOAST/CONTROL-BAR COLLISION (NEW)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Check and resolve toast/control-bar collision
     * Returns offset to apply to toast if collision detected
     */
    function resolveToastCollision() {
        const toast = document.getElementById('toast') ||
                      document.getElementById('hud-toast') ||
                      document.getElementById('mode-toast');
        const controlBar = document.querySelector('.control-bar');

        if (!toast || !controlBar) return 0;

        const toastRect = getRect(toast);
        const barRect = getRect(controlBar);

        if (!toastRect || !barRect) return 0;

        const overlap = overlapArea(toastRect, barRect);
        if (overlap > 0) {
            // Move toast above control bar
            const offset = barRect.height + CONFIG.MARGIN;
            console.log(`[LAYOUT] Toast/control-bar collision: ${overlap}px², offset: -${offset}px`);
            return -offset;
        }
        return 0;
    }

    /**
     * Apply toast offset if needed
     */
    function applyToastOffset() {
        const offset = resolveToastCollision();
        if (offset !== 0) {
            const toast = document.getElementById('toast') ||
                          document.getElementById('hud-toast');
            if (toast) {
                toast.style.transform = `translateX(-50%) translateY(${offset}px)`;
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MIN-WIDTH VALIDATOR (NEW)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Validate graph has minimum width, adjust sidebars if needed
     */
    function validateGraphWidth() {
        const leftSidebar = document.getElementById('left-sidebar');
        const rightSidebar = document.getElementById('right-sidebar');
        const viewport = getViewport();

        const leftWidth = leftSidebar ? (getRect(leftSidebar)?.width || 0) : 0;
        const rightWidth = rightSidebar ? (getRect(rightSidebar)?.width || 0) : 0;
        const graphWidth = viewport.width - leftWidth - rightWidth;

        if (graphWidth < CONFIG.MIN_GRAPH_WIDTH) {
            const deficit = CONFIG.MIN_GRAPH_WIDTH - graphWidth;
            console.warn(`[LAYOUT] Graph width ${graphWidth}px < ${CONFIG.MIN_GRAPH_WIDTH}px minimum`);

            // Try to reduce right sidebar
            if (rightSidebar && rightWidth > 200) {
                const newWidth = Math.max(200, rightWidth - deficit);
                document.documentElement.style.setProperty('--right-panel-width', newWidth + 'px');
                return { adjusted: true, component: 'right-sidebar', newWidth };
            }
        }
        return { adjusted: false };
    }

    // ═══════════════════════════════════════════════════════════════════════
    // REFLOW (from HudLayoutManager, enhanced)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Reflow all dynamic panels
     */
    function reflow() {
        const now = Date.now();
        if (now - _lastReflow < CONFIG.REFLOW_THROTTLE_MS) {
            if (!_rafPending) {
                _rafPending = true;
                requestAnimationFrame(() => {
                    _rafPending = false;
                    reflow();
                });
            }
            return;
        }
        _lastReflow = now;

        const occupiedRects = getOccupiedRects();

        // Place hover panel first (higher priority)
        const hoverPanel = document.getElementById('hover-panel');
        let hoverPanelRect = null;
        if (hoverPanel && hoverPanel.classList.contains('visible')) {
            const hoverWidth = hoverPanel.offsetWidth || 280;
            const hoverHeight = hoverPanel.offsetHeight || 200;
            const candidates = getHoverPanelCandidates(_mouseX, _mouseY, hoverWidth, hoverHeight);
            const pos = placePanel(hoverPanel, candidates, occupiedRects);
            if (pos) {
                hoverPanel.style.left = pos.left + 'px';
                hoverPanel.style.top = pos.top + 'px';
                hoverPanel.style.right = 'auto';
                hoverPanelRect = {
                    left: pos.left, top: pos.top,
                    right: pos.left + hoverWidth, bottom: pos.top + hoverHeight
                };
            }
        }

        const filePanelOccupied = [...occupiedRects];
        if (hoverPanelRect) filePanelOccupied.push(hoverPanelRect);

        // Place selection panel
        const selectionPanel = document.getElementById('selection-panel');
        if (selectionPanel && selectionPanel.classList.contains('visible')) {
            const candidates = getSelectionPanelCandidates(
                selectionPanel.offsetWidth || 320,
                selectionPanel.offsetHeight || 280
            );
            const pos = placePanel(selectionPanel, candidates, filePanelOccupied);
            if (pos) {
                selectionPanel.style.left = pos.left + 'px';
                selectionPanel.style.top = pos.top + 'px';
                selectionPanel.style.right = 'auto';
                filePanelOccupied.push({
                    left: pos.left, top: pos.top,
                    right: pos.left + (selectionPanel.offsetWidth || 320),
                    bottom: pos.top + (selectionPanel.offsetHeight || 280)
                });
            }
        }

        // Place file panel
        const filePanel = document.getElementById('file-panel');
        if (filePanel && filePanel.classList.contains('visible')) {
            const candidates = getFilePanelCandidates(
                filePanel.offsetWidth || 400,
                filePanel.offsetHeight || 350
            );
            const pos = placePanel(filePanel, candidates, filePanelOccupied);
            if (pos) {
                filePanel.style.left = pos.left + 'px';
                filePanel.style.top = pos.top + 'px';
                filePanel.style.bottom = 'auto';
            }
        }

        // NEW: Check toast/control-bar collision
        applyToastOffset();

        // NEW: Validate graph width
        validateGraphWidth();

        // NEW: Update debug overlay
        if (_debugEnabled) updateDebugOverlay();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DEBUG OVERLAY (NEW)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Toggle debug overlay
     */
    function toggleDebugOverlay() {
        _debugEnabled = !_debugEnabled;

        if (_debugEnabled) {
            if (!_debugOverlay) {
                _debugOverlay = document.createElement('div');
                _debugOverlay.id = 'layout-debug-overlay';
                _debugOverlay.style.cssText = `
                    position: fixed; top: 0; left: 0;
                    width: 100%; height: 100%;
                    pointer-events: none; z-index: 10001;
                `;
                document.body.appendChild(_debugOverlay);
            }
            updateDebugOverlay();
            console.log('[LAYOUT] Debug overlay ON (Ctrl+Shift+L)');
        } else {
            if (_debugOverlay) {
                _debugOverlay.remove();
                _debugOverlay = null;
            }
            console.log('[LAYOUT] Debug overlay OFF');
        }
    }

    /**
     * Update debug overlay with current component bounds
     */
    function updateDebugOverlay() {
        if (!_debugOverlay) return;

        let html = '';
        const allPanels = [...FIXED_PANELS, ...DYNAMIC_PANELS, 'toast', 'control-bar', 'left-sidebar', 'right-sidebar'];

        allPanels.forEach(id => {
            const el = document.getElementById(id) || document.querySelector('.' + id);
            const rect = getRect(el);
            if (!rect) return;

            const kind = FIXED_PANELS.includes(id) ? 'fixed' :
                         DYNAMIC_PANELS.includes(id) ? 'floating' : 'overlay';
            const color = CONFIG.DEBUG_COLORS[kind] || 'rgba(128,128,128,0.3)';

            html += `
                <div style="
                    position: fixed;
                    left: ${rect.left}px; top: ${rect.top}px;
                    width: ${rect.width}px; height: ${rect.height}px;
                    background: ${color};
                    border: 1px solid ${color.replace('0.3', '0.8')};
                    font-size: 10px; color: white; text-shadow: 0 0 2px black;
                    padding: 2px 4px; box-sizing: border-box; overflow: hidden;
                ">${id}</div>
            `;
        });

        _debugOverlay.innerHTML = html;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // COMPONENT REGISTRATION (NEW - for future explicit constraints)
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Register a component (for explicit constraint tracking)
     */
    function register(descriptor) {
        const { id, selector, kind = 'dock' } = descriptor;
        if (!id) return null;

        let element = typeof selector === 'string' ?
            (document.getElementById(selector.replace('#', '')) || document.querySelector(selector)) :
            selector;

        _registry.set(id, { ...descriptor, element });
        console.log(`[LAYOUT] Registered: ${id} (${kind})`);
        return _registry.get(id);
    }

    /**
     * Get registered component
     */
    function get(id) {
        return _registry.get(id) || null;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Initialize layout system
     */
    function init() {
        // Window resize
        window.addEventListener('resize', () => reflow());

        // Track mouse position
        window.addEventListener('mousemove', (e) => {
            updateMousePosition(e.clientX, e.clientY);
        }, { passive: true });

        // Sidebar state changes
        const sideDock = document.getElementById('side-dock');
        if (sideDock) {
            sideDock.addEventListener('mouseenter', () => reflow());
            sideDock.addEventListener('mouseleave', () => {
                setTimeout(() => reflow(), 200);
            });
        }

        // Debug overlay shortcut (Ctrl+Shift+L)
        window.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                e.preventDefault();
                toggleDebugOverlay();
            }
        });

        console.log('[LAYOUT] Initialized (replaces HudLayoutManager)');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        // Core utilities
        getViewport,
        getRect,
        overlapArea,
        isInsideViewport,
        clampToViewport,

        // Panel placement (backward compatible with HudLayoutManager)
        getOccupiedRects,
        placePanel,
        getFilePanelCandidates,
        getSelectionPanelCandidates,
        getHoverPanelCandidates,
        getSelectionCentroid,
        updateMousePosition,

        // Main entry points
        reflow,
        init,

        // NEW: Validation
        validateGraphWidth,
        resolveToastCollision,

        // NEW: Debug
        toggleDebugOverlay,

        // NEW: Registration
        register,
        get,

        // Config (read-only)
        CONFIG: Object.freeze({ ...CONFIG })
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY: HudLayoutManager alias
// ═══════════════════════════════════════════════════════════════════════════

window.HudLayoutManager = LAYOUT;
window.Layout = LAYOUT;

console.log('[Module] LAYOUT loaded - Unified Layout Engine v2.0.0');
