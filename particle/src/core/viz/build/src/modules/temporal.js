/**
 * ═══════════════════════════════════════════════════════════════════════════
 * TEMPORAL OVERLAY - Churn, age, bus factor, and hotspot visualization
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Surfaces COLLIDER_DATA.temporal_analysis as a toggle overlay:
 * - Node sizes scale by churn intensity
 * - Floating panel shows bus factor, age distribution, and hotspot list
 *
 * Triggered by "Time" dock button.
 *
 * @module TEMPORAL
 * @version 1.0.0
 */

let _panel = null;
let _active = false;
let _savedNodeVal = null;

// ═══════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════

function init() {
    const btn = document.getElementById('btn-temporal');
    if (!btn) return;

    btn.addEventListener('click', toggle);
    console.log('[Module] TEMPORAL loaded - Temporal overlay');
}

// ═══════════════════════════════════════════════════════════════════════
// TOGGLE
// ═══════════════════════════════════════════════════════════════════════

function toggle() {
    if (_active) {
        deactivate();
    } else {
        activate();
    }
}

function activate() {
    _active = true;
    const btn = document.getElementById('btn-temporal');
    if (btn) btn.classList.add('active');

    // Apply churn-based node sizing
    _applyChurnSizing();

    // Show panel
    if (!_panel) _panel = _buildPanel();
    if (_panel) _panel.style.display = 'block';
}

function deactivate() {
    _active = false;
    const btn = document.getElementById('btn-temporal');
    if (btn) btn.classList.remove('active');

    // Restore node sizing
    _restoreNodeSizing();

    // Hide panel
    if (_panel) _panel.style.display = 'none';
}

function isActive() {
    return _active;
}

// ═══════════════════════════════════════════════════════════════════════
// CHURN SIZING
// ═══════════════════════════════════════════════════════════════════════

function _applyChurnSizing() {
    const graph = window.FULL_GRAPH;
    if (!graph || typeof graph.nodeVal !== 'function') return;

    // Save current nodeVal function for restoration
    _savedNodeVal = graph.nodeVal();

    const nodes = window.COLLIDER_DATA?.nodes || [];
    let maxChurn = 0;
    for (const n of nodes) {
        const c = n.churn || 0;
        if (c > maxChurn) maxChurn = c;
    }

    if (maxChurn > 0) {
        graph.nodeVal(n => {
            const baseSize = n.val || 4;
            const churn = n.churn || 0;
            const multiplier = 1 + (churn / maxChurn) * 2; // Range [1, 3]
            return baseSize * multiplier;
        });
    }
}

function _restoreNodeSizing() {
    const graph = window.FULL_GRAPH;
    if (!graph || typeof graph.nodeVal !== 'function') return;

    if (_savedNodeVal && typeof _savedNodeVal === 'function') {
        graph.nodeVal(_savedNodeVal);
    } else {
        graph.nodeVal(n => n.val || 4);
    }
    _savedNodeVal = null;
}

// ═══════════════════════════════════════════════════════════════════════
// PANEL BUILDER
// ═══════════════════════════════════════════════════════════════════════

function _buildPanel() {
    const temporal = window.COLLIDER_DATA?.temporal_analysis || {};
    const hotspots = temporal.hotspots || [];
    const busFactor = temporal.bus_factor;
    const churnRate = temporal.churn_rate;
    const ageQuartiles = temporal.age_quartiles || {};

    if (!hotspots.length && busFactor == null && !Object.keys(ageQuartiles).length) {
        if (typeof window.showToast === 'function') {
            window.showToast('No temporal data available', 2000);
        }
        return null;
    }

    const panel = document.createElement('div');
    panel.className = 'temporal-panel';
    panel.id = 'temporal-panel';

    // Header
    const header = document.createElement('div');
    header.className = 'temporal-header';

    const title = document.createElement('div');
    title.className = 'temporal-title';
    title.textContent = 'TEMPORAL';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'temporal-close';
    closeBtn.textContent = '\u00D7';
    closeBtn.addEventListener('click', deactivate);

    header.appendChild(title);
    header.appendChild(closeBtn);
    panel.appendChild(header);

    // Key stats row
    const stats = document.createElement('div');
    stats.className = 'temporal-stats';

    if (busFactor != null) {
        const bfEl = document.createElement('div');
        bfEl.className = 'temporal-stat';
        const bfCls = busFactor <= 1 ? 'signal-bad' : busFactor <= 2 ? 'signal-warn' : 'signal-good';
        bfEl.innerHTML = `<span class="temporal-stat-label">Bus Factor</span><span class="temporal-stat-value ${bfCls}">${busFactor}</span>`;
        stats.appendChild(bfEl);
    }

    if (churnRate != null) {
        const crEl = document.createElement('div');
        crEl.className = 'temporal-stat';
        crEl.innerHTML = `<span class="temporal-stat-label">Churn Rate</span><span class="temporal-stat-value">${typeof churnRate === 'number' ? churnRate.toFixed(2) : churnRate}</span>`;
        stats.appendChild(crEl);
    }

    panel.appendChild(stats);

    // Age distribution
    if (Object.keys(ageQuartiles).length > 0) {
        const ageSection = document.createElement('div');
        ageSection.className = 'temporal-age-section';

        const ageTitle = document.createElement('div');
        ageTitle.className = 'temporal-section-title';
        ageTitle.textContent = 'Age Distribution';
        ageSection.appendChild(ageTitle);

        const ageGrid = document.createElement('div');
        ageGrid.className = 'temporal-age-grid';

        // Find max for bar scaling
        const values = Object.values(ageQuartiles).map(Number).filter(n => !isNaN(n));
        const maxVal = Math.max(...values, 1);

        for (const [label, count] of Object.entries(ageQuartiles)) {
            const item = document.createElement('div');
            item.className = 'temporal-age-item';

            const lbl = document.createElement('span');
            lbl.className = 'temporal-age-label';
            lbl.textContent = label;

            const bar = document.createElement('div');
            bar.className = 'temporal-age-bar';
            const fill = document.createElement('div');
            fill.className = 'temporal-age-fill';
            fill.style.width = ((count / maxVal) * 100) + '%';
            bar.appendChild(fill);

            const val = document.createElement('span');
            val.className = 'temporal-age-count';
            val.textContent = count;

            item.appendChild(lbl);
            item.appendChild(bar);
            item.appendChild(val);
            ageGrid.appendChild(item);
        }

        ageSection.appendChild(ageGrid);
        panel.appendChild(ageSection);
    }

    // Hotspots
    if (hotspots.length > 0) {
        const hsSection = document.createElement('div');
        hsSection.className = 'temporal-hotspots-section';

        const hsTitle = document.createElement('div');
        hsTitle.className = 'temporal-section-title';
        hsTitle.textContent = 'Hotspots';
        hsSection.appendChild(hsTitle);

        const hsList = document.createElement('div');
        hsList.className = 'temporal-hotspot-list';

        const top20 = hotspots.slice(0, 20);
        for (let i = 0; i < top20.length; i++) {
            const hs = top20[i];
            const row = document.createElement('div');
            row.className = 'temporal-hotspot-row';

            const rank = document.createElement('span');
            rank.className = 'temporal-hotspot-rank';
            rank.textContent = (i + 1) + '.';

            const path = document.createElement('span');
            path.className = 'temporal-hotspot-path';
            const filePath = hs.path || hs.file || hs.name || 'Unknown';
            path.textContent = filePath.length > 40 ? '...' + filePath.slice(-37) : filePath;
            path.title = filePath;

            const count = document.createElement('span');
            count.className = 'temporal-hotspot-count';
            count.textContent = `(${hs.change_count || hs.changes || hs.churn || 0})`;

            row.appendChild(rank);
            row.appendChild(path);
            row.appendChild(count);
            hsList.appendChild(row);
        }

        hsSection.appendChild(hsList);
        panel.appendChild(hsSection);
    }

    // Inject into Z4: left-float zone
    const zone = document.getElementById('zone-left-float') || document.getElementById('hud');
    if (zone) {
        zone.appendChild(panel);
    }

    return panel;
}

// ═══════════════════════════════════════════════════════════════════════
// MODULE EXPORT
// ═══════════════════════════════════════════════════════════════════════

export { init, toggle, activate, deactivate, isActive };

const TEMPORAL = { init, toggle, activate, deactivate, isActive };
window.TEMPORAL = TEMPORAL;

console.log('[Module] TEMPORAL registered');
