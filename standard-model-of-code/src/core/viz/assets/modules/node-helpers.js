/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NODE-HELPERS MODULE - Node classification and color functions
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Node color mode selection, data enrichment helpers, and tier grouping.
 * Depends on: COLOR (ColorOrchestrator), NODE (node-accessors), DM, Graph
 *
 * @module NODE_HELPERS
 * @version 1.0.0
 */

window.NODE_HELPERS = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // NODE COLOR BY MODE
    // ═══════════════════════════════════════════════════════════════════════

    function getNodeColorByMode(node) {
        // All colors come from ColorOrchestrator (aliased as Color)
        const Color = window.Color;
        const NODE_COLOR_MODE = window.NODE_COLOR_MODE;
        const DM = window.DM;

        if (NODE_COLOR_MODE === 'file') {
            const fileIdx = node.fileIdx ?? -1;
            if (fileIdx < 0) {
                return Color.get('tier', 'UNKNOWN');
            }
            const fileBoundaries = DM ? DM.getFileBoundaries() : [];
            const totalFiles = fileBoundaries.length;
            const fileInfo = fileBoundaries[fileIdx] || {};
            const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
            return window.getFileColor(fileIdx, totalFiles, fileLabel);
        }

        // =========================================================================
        // 33-DIMENSION COLOR SWITCH (The Mega-Switch)
        // =========================================================================

        // 1. ARCHITECTURE
        if (NODE_COLOR_MODE === 'tier') return Color.get('tier', window.getNodeTier(node));
        if (NODE_COLOR_MODE === 'layer') return Color.get('layer', (node.layer || node.dimensions?.D2_LAYER || 'UNKNOWN').toUpperCase());
        if (NODE_COLOR_MODE === 'subsystem') return Color.get('subsystem', getSubsystem(node));
        if (NODE_COLOR_MODE === 'boundary_score') return Color.getInterval('boundary_score', window.normalize(node.rpbl?.boundary ?? 1, 9));
        if (NODE_COLOR_MODE === 'phase') return Color.get('phase', getPhase(node));

        // 2. TAXONOMY
        if (NODE_COLOR_MODE === 'atom') return Color.get('atom', (node.kind || node.type || 'unknown').toLowerCase());
        if (NODE_COLOR_MODE === 'family') return Color.get('family', window.getNodeAtomFamily(node));
        if (NODE_COLOR_MODE === 'role') return Color.get('roleCategory', node.role_cat || 'Unknown');
        if (NODE_COLOR_MODE === 'roleCategory') return Color.get('roleCategory', node.role_cat || getRoleCategory(node));
        if (NODE_COLOR_MODE === 'fileType') return Color.get('fileType', getFileType(node));

        // 3. METRICS
        if (NODE_COLOR_MODE === 'complexity') return Color.getInterval('complexity', window.normalize(node.complexity || 0, 20));
        if (NODE_COLOR_MODE === 'loc') return Color.getInterval('loc', window.normalize(node.lines_of_code || 0, 500));
        if (NODE_COLOR_MODE === 'fan_in') return Color.getInterval('fan_in', window.normalize(node.in_degree || 0, 20));
        if (NODE_COLOR_MODE === 'fan_out') return Color.getInterval('fan_out', window.normalize(node.out_degree || 0, 20));
        if (NODE_COLOR_MODE === 'trust') return Color.getInterval('trust', node.trust || node.confidence || 0);

        // 4. RPBL DNA
        if (NODE_COLOR_MODE === 'responsibility') return Color.getInterval('responsibility', window.normalize(node.rpbl?.responsibility ?? 1, 9));
        if (NODE_COLOR_MODE === 'purity') return Color.getInterval('purity', window.normalize(node.rpbl?.purity ?? 1, 9));
        if (NODE_COLOR_MODE === 'lifecycle_score') return Color.getInterval('lifecycle_score', window.normalize(node.rpbl?.lifecycle ?? 1, 9));
        if (NODE_COLOR_MODE === 'state') return Color.get('state', (node.dimensions?.D5_STATE === 'Stateful') ? 'Stateful' : 'Stateless');
        if (NODE_COLOR_MODE === 'visibility') return Color.get('visibility', node.dimensions?.D4_BOUNDARY === 'External' ? 'Public' : 'Private');

        // 5. TOPOLOGY
        if (NODE_COLOR_MODE === 'centrality') return Color.getInterval('centrality', node.centrality || 0);
        if (NODE_COLOR_MODE === 'rank') return Color.getInterval('centrality', node.pagerank || 0);
        if (NODE_COLOR_MODE === 'ring') return Color.get('ring', window.getNodeRing(node));

        // 6. EVOLUTION (Placeholders / Simulated)
        if (NODE_COLOR_MODE === 'churn') return Color.getInterval('churn', Math.random() * 0.5);
        if (NODE_COLOR_MODE === 'age') return Color.getInterval('churn', 0.2);

        // DEFAULT FALLBACK
        return Color.get('tier', window.getNodeTier(node));
    }

    // ═══════════════════════════════════════════════════════════════════════
    // DATA ENRICHMENT HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getSubsystem(node) {
        if (!node.file_path) return 'Unknown';
        if (node.file_path.includes('/api/')) return 'Ingress';
        if (node.file_path.includes('/db/') || node.file_path.includes('repository')) return 'Persistence';
        if (node.file_path.includes('/core/') || node.file_path.includes('domain')) return 'Domain';
        if (node.file_path.includes('/ui/') || node.file_path.includes('frontend')) return 'Presentation';
        if (node.file_path.includes('config')) return 'Config';
        return 'Domain';
    }

    function getPhase(node) {
        const kind = (node.kind || '').toLowerCase();
        if (kind.includes('data') || kind.includes('entity') || kind.includes('schema')) return 'DATA';
        if (kind.includes('function') || kind.includes('logic')) return 'LOGIC';
        if (kind.includes('module') || kind.includes('package')) return 'ORGANIZATION';
        if (kind.includes('script') || kind.includes('main')) return 'EXECUTION';
        return 'LOGIC';
    }

    function getFileType(node) {
        const p = node.file_path || node.id || '';
        const ext = p.split('.').pop().toLowerCase();
        return ext || 'unknown';
    }

    function getRoleCategory(node) {
        const r = (node.role || '').toLowerCase();
        if (r.includes('service') || r.includes('manager')) return 'Orchestration';
        if (r.includes('repo') || r.includes('store')) return 'Storage';
        if (r.includes('controller') || r.includes('handler')) return 'Ingress';
        if (r.includes('util') || r.includes('helper')) return 'Utility';
        return 'Unknown';
    }

    // ═══════════════════════════════════════════════════════════════════════
    // NODE COLOR APPLICATION
    // ═══════════════════════════════════════════════════════════════════════

    function applyNodeColors(nodes) {
        const DM = window.DM;
        const fileBoundaries = DM ? DM.getFileBoundaries() : [];
        nodes.forEach(node => {
            if (node && node.isFileNode) {
                if (!node.color) {
                    const totalFiles = fileBoundaries.length;
                    const fileInfo = fileBoundaries[node.fileIdx] || {};
                    const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
                    node.color = window.getFileColor(node.fileIdx, totalFiles, fileLabel);
                }
                return;
            }
            if (window.fileMode) {
                return;
            }
            node.color = getNodeColorByMode(node);
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    // NODE SIZE MODE
    // ═══════════════════════════════════════════════════════════════════════

    function applyNodeSizeMode(mode) {
        const Graph = window.Graph;
        if (!Graph) return;
        const scale = window.APPEARANCE_STATE?.nodeScale || 1;
        switch (mode) {
            case 'uniform':
                Graph.nodeVal(() => 1 * scale);
                break;
            case 'degree':
                Graph.nodeVal(n => Math.max(1, ((n.in_degree || 0) + (n.out_degree || 0)) * 0.5) * scale);
                break;
            case 'fanout':
                Graph.nodeVal(n => (n.val || n.fanout || 1) * scale);
                break;
            case 'complexity':
                Graph.nodeVal(n => Math.max(1, (n.complexity || n.loc || 10) * 0.05) * scale);
                break;
            default:
                Graph.nodeVal(n => (n.val || 1) * scale);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TIER/DEPTH/SIMILARITY HELPERS
    // ═══════════════════════════════════════════════════════════════════════

    function getNodeTierValue(node) {
        if (!node) return 1;
        const tier = window.getNodeTier(node);
        if (tier === 'T0') return 0;
        if (tier === 'T1') return 1;
        if (tier === 'T2') return 2;
        return 1;
    }

    function getNodeDepth(node) {
        if (node && typeof node.y === 'number') {
            return Math.abs(node.y) / 500;
        }
        return 0.5;
    }

    function getSemanticSimilarity(srcNode, tgtNode) {
        if (!srcNode || !tgtNode) return 0.5;
        let score = 0;
        if (srcNode.type === tgtNode.type) score += 0.4;
        if (srcNode.fileIdx === tgtNode.fileIdx) score += 0.3;
        if (window.getNodeTier(srcNode) === window.getNodeTier(tgtNode)) score += 0.2;
        if (srcNode.ring === tgtNode.ring) score += 0.1;
        return score;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // TIER GROUPING
    // ═══════════════════════════════════════════════════════════════════════

    function groupNodesByTier(nodes) {
        const groups = { T0: [], T1: [], T2: [], UNKNOWN: [] };
        nodes.forEach(n => {
            const tier = window.getNodeTier(n);
            (groups[tier] || groups.UNKNOWN).push(n);
        });
        return groups;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        getColorByMode: getNodeColorByMode,
        getSubsystem: getSubsystem,
        getPhase: getPhase,
        getFileType: getFileType,
        getRoleCategory: getRoleCategory,
        applyColors: applyNodeColors,
        applySizeMode: applyNodeSizeMode,
        getTierValue: getNodeTierValue,
        getDepth: getNodeDepth,
        getSemanticSimilarity: getSemanticSimilarity,
        groupByTier: groupNodesByTier
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.getNodeColorByMode = NODE_HELPERS.getColorByMode;
window.getSubsystem = NODE_HELPERS.getSubsystem;
window.getPhase = NODE_HELPERS.getPhase;
window.getFileType = NODE_HELPERS.getFileType;
window.getRoleCategory = NODE_HELPERS.getRoleCategory;
window.applyNodeColors = NODE_HELPERS.applyColors;
window.applyNodeSizeMode = NODE_HELPERS.applySizeMode;
window.getNodeTierValue = NODE_HELPERS.getTierValue;
window.getNodeDepth = NODE_HELPERS.getDepth;
window.getSemanticSimilarity = NODE_HELPERS.getSemanticSimilarity;
window.groupNodesByTier = NODE_HELPERS.groupByTier;

console.log('[Module] NODE_HELPERS loaded - 11 functions');
