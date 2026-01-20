/**
 * ═══════════════════════════════════════════════════════════════════════════
 * HOVER MODULE - Node hover and click interactions
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Node hover panel updates, click handling, and interaction management.
 * Depends on: HOVERED_NODE, VIS_FILTERS, GRAPH_MODE, DM, Graph
 *
 * @module HOVER
 * @version 1.0.0
 */

window.HOVER = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // UPDATE HOVER PANEL
    // ═══════════════════════════════════════════════════════════════════════

    function updateHoverPanel(node) {
        const hoverPanel = document.getElementById('hover-panel');
        const placeholder = document.getElementById('hover-placeholder');
        if (!hoverPanel) return;

        if (!node) {
            hoverPanel.classList.remove('has-node');
            if (placeholder) placeholder.style.display = '';
            return;
        }

        hoverPanel.classList.add('has-node');
        if (placeholder) placeholder.style.display = 'none';

        // Helper to set element text safely
        const setEl = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val ?? '--';
        };

        // Basic info
        setEl('hover-name', node.label || node.id || 'Unknown');
        setEl('hover-type', node.type || node.kind || '--');
        setEl('hover-file', node.file_path || '--');

        // Tier/Ring/Family
        setEl('hover-tier', window.getNodeTier ? window.getNodeTier(node) : (node.tier || '--'));
        setEl('hover-ring', window.getNodeRing ? window.getNodeRing(node) : (node.ring || '--'));
        setEl('hover-family', window.getNodeAtomFamily ? window.getNodeAtomFamily(node) : (node.atom_family || '--'));

        // Metrics
        setEl('hover-complexity', node.complexity ?? '--');
        setEl('hover-loc', node.lines_of_code ?? node.loc ?? '--');
        setEl('hover-fanin', node.in_degree ?? '--');
        setEl('hover-fanout', node.out_degree ?? '--');

        // Role
        setEl('hover-role', node.role || '--');

        // Code preview (if available)
        const codeEl = document.getElementById('hover-code');
        if (codeEl) {
            const code = node.body_source || node.body || '';
            codeEl.textContent = code ? code.substring(0, 500) : '// no source';
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // HANDLE NODE HOVER
    // ═══════════════════════════════════════════════════════════════════════

    function handleNodeHover(node, data) {
        const filePanel = document.getElementById('file-panel');
        window.HOVERED_NODE = node || null;

        // Always update hover panel
        updateHoverPanel(node);

        // Guard: file-panel may not exist
        if (!filePanel) return;

        const VIS_FILTERS = window.VIS_FILTERS;
        if (!VIS_FILTERS.metadata.showFilePanel) {
            filePanel.classList.remove('visible');
            return;
        }

        if (!node) {
            setTimeout(() => {
                if (!window.fileMode) filePanel.classList.remove('visible');
            }, 300);
            return;
        }

        // Get file info from boundaries
        const boundaries = data.file_boundaries || [];
        const fileIdx = node.fileIdx;

        if (fileIdx < 0 || fileIdx >= boundaries.length) {
            return;
        }

        const fileInfo = boundaries[fileIdx];

        // Update panel content
        const setEl = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        setEl('file-name', fileInfo.file_name || 'unknown');
        setEl('file-cohesion', `Cohesion: ${(fileInfo.cohesion * 100).toFixed(0)}%`);
        setEl('file-purpose', fileInfo.purpose || '--');
        setEl('file-atom-count', fileInfo.atom_count || 0);
        setEl('file-lines', fileInfo.line_range ? `${fileInfo.line_range[0]}-${fileInfo.line_range[1]}` : '--');
        setEl('file-classes', (fileInfo.classes || []).join(', ') || 'none');
        setEl('file-functions', 'Functions: ' + ((fileInfo.functions || []).slice(0, 8).join(', ') || 'none'));

        // Code preview from node body
        const code = node.body || '// no source available';
        setEl('file-code', code);

        // Show panel
        filePanel.classList.add('visible');
        if (typeof LAYOUT !== 'undefined') LAYOUT.reflow();
    }

    // ═══════════════════════════════════════════════════════════════════════
    // HANDLE NODE CLICK
    // ═══════════════════════════════════════════════════════════════════════

    function handleNodeClick(node, event) {
        if (!node) return;
        const additive = event && event.shiftKey;
        if (additive) {
            window.toggleSelection(node);
            return;
        }
        if (node.id) {
            window.setSelection([node.id]);
        }
        const GRAPH_MODE = window.GRAPH_MODE;
        if ((GRAPH_MODE === 'files' || GRAPH_MODE === 'hybrid') && node.isFileNode) {
            window.toggleFileExpand(node.fileIdx);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        updatePanel: updateHoverPanel,
        onNodeHover: handleNodeHover,
        onNodeClick: handleNodeClick
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.updateHoverPanel = HOVER.updatePanel;
window.handleNodeHover = HOVER.onNodeHover;
window.handleNodeClick = HOVER.onNodeClick;

console.log('[Module] HOVER loaded - 3 functions');
