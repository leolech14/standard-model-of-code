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

// ═══════════════════════════════════════════════════════════════════════
// OKLCH → HEX CONVERTER (render boundary)
// ═══════════════════════════════════════════════════════════════════════

/**
 * Convert OKLCH [L, C, H] triple to hex string.
 * Port of color_science.py's oklch_to_hex — same matrices, same gamut mapping.
 */
function oklchToHex(L, C, H) {
    // Gamut map: binary-search chroma reduction
    L = Math.max(0, Math.min(1, L));
    if (L <= 0) return '#000000';
    if (L >= 1) return '#ffffff';

    let lo = 0, hi = C;
    for (let i = 0; i < 24 && hi - lo > 0.001; i++) {
        const mid = (lo + hi) / 2;
        const [r, g, b] = _oklchToSrgb(L, mid, H);
        if (r >= -0.001 && r <= 1.001 && g >= -0.001 && g <= 1.001 && b >= -0.001 && b <= 1.001) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    C = lo;

    const [r, g, b] = _oklchToSrgb(L, C, H);
    const clamp = v => Math.max(0, Math.min(255, Math.round(v * 255)));
    return '#' + [r, g, b].map(v => clamp(v).toString(16).padStart(2, '0')).join('');
}

function _oklchToSrgb(L, C, H) {
    const hRad = H * Math.PI / 180;
    const a = C * Math.cos(hRad);
    const b = C * Math.sin(hRad);

    // OKLab → LMS (cube-root)
    const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    const s_ = L - 0.0894841775 * a - 1.2914855480 * b;

    const l = l_ * l_ * l_;
    const m = m_ * m_ * m_;
    const s = s_ * s_ * s_;

    // LMS → linear sRGB
    const rLin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
    const gLin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
    const bLin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;

    // Linear → sRGB gamma
    const gamma = v => v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055;
    return [gamma(rLin), gamma(gLin), gamma(bLin)];
}

// Expose for other modules
window.oklchToHex = oklchToHex;

// ═══════════════════════════════════════════════════════════════════════
// NODE COLOR BY MODE
// ═══════════════════════════════════════════════════════════════════════

// =========================================================================
// MODE_ACCESSORS: Declarative map replacing the mega-switch
// Each mode maps to a function: (node, Color) => colorString
// =========================================================================

const MODE_ACCESSORS = {
    // 1. ARCHITECTURE
    tier: (n, C) => C.get('tier', window.getNodeTier(n)),
    layer: (n, C) => C.get('layer', (n.layer || n.dimensions?.D2_LAYER || 'UNKNOWN').toUpperCase()),
    subsystem: (n, C) => C.get('subsystem', getSubsystem(n)),
    boundary_score: (n, C) => C.getInterval('boundary_score', window.normalize(n.rpbl?.boundary ?? 1, 9)),
    phase: (n, C) => C.get('phase', getPhase(n)),

    // 2. TAXONOMY
    atom: (n, C) => C.get('atom', (n.kind || n.type || 'unknown').toLowerCase()),
    family: (n, C) => C.get('family', window.getNodeAtomFamily(n)),
    role: (n, C) => C.get('roleCategory', n.role_cat || 'Unknown'),
    roleCategory: (n, C) => C.get('roleCategory', n.role_cat || getRoleCategory(n)),
    fileType: (n, C) => C.get('fileType', getFileType(n)),

    // 3. METRICS
    complexity: (n, C) => C.getInterval('complexity', window.normalize(n.complexity || 0, 20)),
    loc: (n, C) => C.getInterval('loc', window.normalize(n.lines_of_code || 0, 500)),
    fan_in: (n, C) => C.getInterval('fan_in', window.normalize(n.in_degree || 0, 20)),
    fan_out: (n, C) => C.getInterval('fan_out', window.normalize(n.out_degree || 0, 20)),
    trust: (n, C) => C.getInterval('trust', n.trust || n.confidence || 0),

    // 4. RPBL DNA
    responsibility: (n, C) => C.getInterval('responsibility', window.normalize(n.rpbl?.responsibility ?? 1, 9)),
    purity: (n, C) => C.getInterval('purity', window.normalize(n.rpbl?.purity ?? 1, 9)),
    lifecycle_score: (n, C) => C.getInterval('lifecycle_score', window.normalize(n.rpbl?.lifecycle ?? 1, 9)),
    state: (n, C) => C.get('state', (n.dimensions?.D5_STATE === 'Stateful') ? 'Stateful' : 'Stateless'),
    visibility: (n, C) => C.get('visibility', n.dimensions?.D4_BOUNDARY === 'External' ? 'Public' : 'Private'),

    // 5. TOPOLOGY
    centrality: (n, C) => C.getInterval('centrality', n.centrality || 0),
    rank: (n, C) => C.getInterval('centrality', n.pagerank || 0),
    ring: (n, C) => C.get('ring', window.getNodeRing(n)),

    // 6. SEMANTIC PURPOSE (Stage 6.7 - PURPOSE = f(edges))
    semanticRole: (n, C) => C.get('semanticRole', n.semantic_role || 'unknown'),

    // 7. HOLARCHY SCALE (Stage 2.6 - 16-level classification)
    scale: (n, C) => C.get('scale', n.level || 'L3'),
    levelZone: (n, C) => C.get('levelZone', n.level_zone || 'SEMANTIC'),

    // 8. EVOLUTION (Placeholders)
    churn: (n, C) => C.getInterval('churn', Math.random() * 0.5),
    age: (n, C) => C.getInterval('churn', 0.2)
};

function getNodeColorByMode(node) {
    const Color = window.Color;
    const NODE_COLOR_MODE = window.NODE_COLOR_MODE;
    const DM = window.DM;

    // Encoding view override: pre-computed OKLCH triples from Python.
    // Convert [L, C, H] → hex at this render boundary.
    const activeView = window.ENCODING_VIEW || 'default';
    if (activeView !== 'default' && node.encoded_colors && node.encoded_colors[activeView]) {
        const oklch = node.encoded_colors[activeView];
        return Array.isArray(oklch) ? oklchToHex(oklch[0], oklch[1], oklch[2]) : oklch;
    }

    // Special case: CODOME boundary nodes (external callers)
    // Always use their explicit color_hint, regardless of color mode
    if (node.is_codome_boundary || node.kind === 'boundary') {
        if (node.color_hint) {
            return node.color_hint;
        }
        // Fallback color mapping by codome_source
        const CODOME_COLORS = {
            'test_entry': '#4CAF50',      // Green
            'entry_point': '#2196F3',     // Blue
            'framework_managed': '#9C27B0', // Purple
            'cross_language': '#FF9800',  // Orange
            'external_boundary': '#00BCD4', // Cyan
            'dynamic_target': '#E91E63'   // Pink
        };
        return CODOME_COLORS[node.codome_source] || '#FF9800';
    }

    // Special case: file coloring needs extra context
    if (NODE_COLOR_MODE === 'file') {
        const fileIdx = node.fileIdx ?? -1;
        if (fileIdx < 0) return Color.get('tier', 'UNKNOWN');
        const fileBoundaries = DM ? DM.getFileBoundaries() : [];
        const totalFiles = fileBoundaries.length;
        const fileInfo = fileBoundaries[fileIdx] || {};
        const fileLabel = fileInfo.file || fileInfo.file_name || fileIdx;
        return window.getFileColor(fileIdx, totalFiles, fileLabel);
    }

    // Use MODE_ACCESSORS map - O(1) lookup instead of if-chain
    const accessor = MODE_ACCESSORS[NODE_COLOR_MODE];
    if (accessor) return accessor(node, Color);

    // Default fallback
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
    const totalFiles = fileBoundaries.length;

    nodes.forEach(node => {
        // PRE-COMPUTE file_color for UPB/Property Query resolution
        // This ensures Q.node(n, 'color') works when colorBy='file'
        if (node.fileIdx !== undefined && node.fileIdx >= 0 && totalFiles > 0) {
            const fileInfo = fileBoundaries[node.fileIdx] || {};
            const fileLabel = fileInfo.file || fileInfo.file_name || node.fileIdx;
            node.file_color = window.getFileColor(node.fileIdx, totalFiles, fileLabel);
        }

        if (node && node.isFileNode) {
            if (!node.color) {
                node.color = node.file_color || window.getFileColor(node.fileIdx, totalFiles, '');
            }
            return;
        }
        if (window.fileMode) {
            return;
        }
        // For boundary nodes, always apply their specific color
        if (node.is_codome_boundary || node.kind === 'boundary') {
            node.color = getNodeColorByMode(node);
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
    const BOUNDARY_NODE_SIZE_MULTIPLIER = 1.5; // Boundary nodes 1.5x larger

    const isBoundaryNode = (n) => n.is_codome_boundary || n.kind === 'boundary';
    const sizeWithBoundaryCheck = (baseSize) =>
        isBoundaryNode({ is_codome_boundary: arguments[0]?.is_codome_boundary, kind: arguments[0]?.kind })
            ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER
            : baseSize;

    switch (mode) {
        case 'uniform':
            Graph.nodeVal(n => (isBoundaryNode(n) ? 1.5 : 1) * scale);
            break;
        case 'degree':
            Graph.nodeVal(n => {
                const baseSize = Math.max(1, ((n.in_degree || 0) + (n.out_degree || 0)) * 0.5);
                return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
            });
            break;
        case 'fanout':
            Graph.nodeVal(n => {
                const baseSize = n.val || n.fanout || 1;
                return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
            });
            break;
        case 'complexity':
            Graph.nodeVal(n => {
                const baseSize = Math.max(1, (n.complexity || n.loc || 10) * 0.05);
                return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
            });
            break;
        default:
            Graph.nodeVal(n => {
                const baseSize = n.val || 1;
                return (isBoundaryNode(n) ? baseSize * BOUNDARY_NODE_SIZE_MULTIPLIER : baseSize) * scale;
            });
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

export {
    getNodeColorByMode,
    getSubsystem,
    getPhase,
    getFileType,
    getRoleCategory,
    applyNodeColors,
    applyNodeSizeMode,
    getNodeTierValue,
    getNodeDepth,
    getSemanticSimilarity,
    groupNodesByTier
};
export const NODE_HELPERS = {
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
window.NODE_HELPERS = NODE_HELPERS;

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.getNodeColorByMode = window.NODE_HELPERS.getColorByMode;
window.getSubsystem = window.NODE_HELPERS.getSubsystem;
window.getPhase = window.NODE_HELPERS.getPhase;
window.getFileType = window.NODE_HELPERS.getFileType;
window.getRoleCategory = window.NODE_HELPERS.getRoleCategory;
window.applyNodeColors = window.NODE_HELPERS.applyColors;
window.applyNodeSizeMode = window.NODE_HELPERS.applySizeMode;
window.getNodeTierValue = window.NODE_HELPERS.getTierValue;
window.getNodeDepth = window.NODE_HELPERS.getDepth;
window.getSemanticSimilarity = window.NODE_HELPERS.getSemanticSimilarity;
window.groupNodesByTier = window.NODE_HELPERS.groupByTier;

console.log('[Module] NODE_HELPERS loaded - 11 functions');
