/**
 * ═══════════════════════════════════════════════════════════════════════════
 * HUD MODULE - Heads-up display management
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles HUD fade behavior and stats panel updates.
 * Depends on: DOM elements (stat-nodes, stat-edges, stat-entropy, etc.)
 *
 * @module HUD
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════
// HUD FADE BEHAVIOR
// ═══════════════════════════════════════════════════════════════════════

/**
 * Setup HUD auto-fade on idle
 * Fades HUD elements after period of inactivity
 */
function setupFade() {
    // Read idle delay from CSS token (--duration-toast), fallback to 3000ms
    const idleDelay = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue('--duration-toast') || '3000', 10
    );
    let timer = null;

    const activate = () => {
        document.body.classList.remove('hud-quiet');
        if (timer) {
            clearTimeout(timer);
        }
        timer = setTimeout(() => {
            document.body.classList.add('hud-quiet');
        }, idleDelay);
    };

    ['mousemove', 'mousedown', 'keydown', 'touchstart'].forEach((evt) => {
        window.addEventListener(evt, activate, { passive: true });
    });

    activate();
}

// ═══════════════════════════════════════════════════════════════════════
// STATS UPDATES
// ═══════════════════════════════════════════════════════════════════════

/**
 * Update all HUD stats elements
 * @param {Object} data - Graph data with nodes, links, meta
 */
function updateStats(data) {
    if (!data) return;

    // Stats panel: NODES, EDGES, ENTROPY
    const nodeCount = (data.nodes || []).length;
    const edgeCount = (data.links || []).length;

    const statNodes = document.getElementById('stat-nodes');
    const statEdges = document.getElementById('stat-edges');
    const statEntropy = document.getElementById('stat-entropy');

    if (statNodes) statNodes.textContent = nodeCount.toLocaleString();
    if (statEdges) statEdges.textContent = edgeCount.toLocaleString();
    if (statEntropy) {
        const entropy = data.meta?.entropy ?? data.entropy ?? '--';
        statEntropy.textContent = typeof entropy === 'number' ? entropy.toFixed(2) : entropy;
    }

    // Header panel: target name and timestamp
    const targetName = document.getElementById('target-name');
    const timestamp = document.getElementById('timestamp');

    if (targetName) {
        const target = data.meta?.target || data.target || 'Unknown';
        // Show just the last part of the path
        const shortTarget = target.split('/').pop() || target;
        targetName.textContent = shortTarget;
    }

    if (timestamp) {
        const ts = data.meta?.timestamp || data.timestamp || '';
        // Format: 2024-01-15T10:30:00 -> 2024-01-15 10:30
        const formatted = ts.replace('T', ' ').substring(0, 16);
        timestamp.textContent = formatted || 'Live';
    }

    // Health stat from incoherence data
    _updateHealth();
}

/**
 * Populate the Health stat in the HUD bar and build expandable incoherence breakdown.
 */
function _updateHealth() {
    const statHealth = document.getElementById('stat-health');
    const wrap = document.getElementById('stat-health-wrap');
    if (!statHealth || !wrap) return;

    const inc = window.COLLIDER_DATA?.incoherence || {};
    const health = inc.health_10;

    if (health == null) {
        statHealth.textContent = '--';
        return;
    }

    statHealth.textContent = typeof health === 'number' ? health.toFixed(1) : health;

    // Color-code based on health level
    const cls = health >= 7 ? 'signal-good' : health >= 4 ? 'signal-warn' : 'signal-bad';
    statHealth.className = 'stat-value stat-health-value ' + cls;

    // Build expandable breakdown panel (only once)
    if (wrap.querySelector('.incoherence-breakdown')) return;

    const terms = [
        { label: 'Structural', key: 'i_struct' },
        { label: 'Teleological', key: 'i_telic' },
        { label: 'Symmetry', key: 'i_sym' },
        { label: 'Boundary', key: 'i_bound' },
        { label: 'Flow', key: 'i_flow' },
    ];

    const hasTerms = terms.some(t => inc[t.key] != null);
    if (!hasTerms) return;

    const breakdown = document.createElement('div');
    breakdown.className = 'incoherence-breakdown';
    breakdown.style.display = 'none';

    const total = inc.incoherence_total || inc.i_total;
    if (total != null) {
        const header = document.createElement('div');
        header.className = 'inc-header';
        header.textContent = `INCOHERENCE (I=${typeof total === 'number' ? total.toFixed(2) : total})`;
        breakdown.appendChild(header);
    }

    for (const { label, key } of terms) {
        const val = inc[key];
        if (val == null) continue;

        const row = document.createElement('div');
        row.className = 'inc-row';

        const lbl = document.createElement('span');
        lbl.className = 'inc-label';
        lbl.textContent = label;

        const bar = document.createElement('div');
        bar.className = 'inc-bar-wrap';
        const fill = document.createElement('div');
        // Bars are inverted: lower = better
        const barCls = val < 0.15 ? 'signal-good' : val < 0.35 ? 'signal-warn' : 'signal-bad';
        fill.className = 'inc-bar-fill ' + barCls;
        fill.style.width = (Math.min(val, 1) * 100) + '%';
        bar.appendChild(fill);

        const valSpan = document.createElement('span');
        valSpan.className = 'inc-value';
        valSpan.textContent = typeof val === 'number' ? val.toFixed(2) : val;

        row.appendChild(lbl);
        row.appendChild(bar);
        row.appendChild(valSpan);
        breakdown.appendChild(row);
    }

    wrap.appendChild(breakdown);

    // Toggle on click
    wrap.style.cursor = 'pointer';
    wrap.addEventListener('click', () => {
        const visible = breakdown.style.display !== 'none';
        breakdown.style.display = visible ? 'none' : 'block';
    });
}

// ═══════════════════════════════════════════════════════════════════════
// MODULE EXPORT
// ═══════════════════════════════════════════════════════════════════════

export const HUD = {
    setupFade: setupFade,
    updateStats: updateStats
};

export {
    setupFade,
    updateStats
};

window.HUD = HUD;

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.setupHudFade = HUD.setupFade;
window.updateHudStats = HUD.updateStats;

console.log('[Module] HUD loaded - 2 functions');
