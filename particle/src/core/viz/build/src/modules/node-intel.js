/**
 * ═══════════════════════════════════════════════════════════════════════════
 * NODE INTELLIGENCE CARD - Rich detail panel for single node selection
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Replaces the 5-field selection card with a 6-section collapsible card
 * exposing all properties the Collider pipeline computes for each node.
 *
 * Sections: Identity, Metrics, DNA (RPBL), Topology, Evolution, Source
 *
 * @module NODE_INTEL
 * @version 1.0.0
 */

// ═══════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════

/**
 * Get a node property using accessor functions if available, else direct access.
 */
function _get(node, key, fallback) {
    const val = node[key];
    return val != null ? val : fallback;
}

/**
 * Format a number for display (2 decimal places for floats, locale for ints).
 */
function _fmt(val) {
    if (val == null || val === '') return '--';
    if (typeof val === 'number') {
        return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
    }
    return String(val);
}

/**
 * Create a collapsible section with header and body.
 */
function _section(title, open) {
    const sec = document.createElement('div');
    sec.className = 'ni-section';

    const header = document.createElement('div');
    header.className = 'ni-section-header' + (open ? '' : ' collapsed');
    header.innerHTML = `<span class="ni-collapse-icon">&#9662;</span> ${title}`;
    header.addEventListener('click', () => {
        header.classList.toggle('collapsed');
        body.classList.toggle('collapsed');
    });

    const body = document.createElement('div');
    body.className = 'ni-section-body' + (open ? '' : ' collapsed');

    sec.appendChild(header);
    sec.appendChild(body);
    return { sec, body };
}

/**
 * Create a key-value row.
 */
function _kv(label, value) {
    const row = document.createElement('div');
    row.className = 'ni-kv';
    row.innerHTML = `<span class="ni-kv-label">${label}</span><span class="ni-kv-value">${_fmt(value)}</span>`;
    return row;
}

/**
 * Create a pill tag styling using the Rainmaker rc-comp-chip component.
 */
function _tag(text, styleClass) {
    const span = document.createElement('span');
    span.className = 'rc-comp-chip';
    span.innerHTML = `<span class="pip h-neutral"></span>${text}`;
    return span;
}

/**
 * Create a horizontal bar (0-max scale).
 */
function _bar(value, max, colorClass) {
    const wrap = document.createElement('div');
    wrap.className = 'ni-bar-wrap';

    const fill = document.createElement('div');
    fill.className = 'ni-bar-fill ' + colorClass;
    const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
    fill.style.width = pct + '%';

    wrap.appendChild(fill);
    return wrap;
}

/**
 * Get color class for a 0-10 scale value.
 */
function _signalClass(val) {
    if (val == null) return 'signal-neutral';
    if (val >= 7) return 'signal-good';
    if (val >= 4) return 'signal-warn';
    return 'signal-bad';
}

/**
 * Get color class for a 0-1 metric bar (relative, higher = better).
 */
function _relativeBarClass(val, max) {
    if (val == null || max == null || max === 0) return 'signal-neutral';
    const ratio = val / max;
    if (ratio >= 0.6) return 'signal-good';
    if (ratio >= 0.3) return 'signal-warn';
    return 'signal-bad';
}

/**
 * Compute max values from the full dataset for relative bars.
 */
function _getDatasetMaxes() {
    const nodes = window.COLLIDER_DATA?.nodes || [];
    const maxes = { in_degree: 0, out_degree: 0, complexity: 0, loc: 0, churn: 0 };
    for (const n of nodes) {
        if (n.in_degree > maxes.in_degree) maxes.in_degree = n.in_degree;
        if (n.out_degree > maxes.out_degree) maxes.out_degree = n.out_degree;
        const cx = n.cyclomatic_complexity || n.complexity || 0;
        if (cx > maxes.complexity) maxes.complexity = cx;
        const lc = n.loc || n.lines_of_code || 0;
        if (lc > maxes.loc) maxes.loc = lc;
        if ((n.churn || 0) > maxes.churn) maxes.churn = n.churn;
    }
    return maxes;
}

// ═══════════════════════════════════════════════════════════════════════
// MAIN RENDER FUNCTION
// ═══════════════════════════════════════════════════════════════════════

/**
 * Render a rich intelligence card for a single node into the given container.
 * @param {Object} node - The graph node object with all Collider properties
 * @param {HTMLElement} container - DOM element to append the card into
 */
function renderNodeCard(node, container) {
    const card = document.createElement('div');
    card.className = 'node-intel';

    const maxes = _getDatasetMaxes();

    // ── Section 1: Identity (always open) ──
    const s1 = _section('IDENTITY', true);

    const nameEl = document.createElement('div');
    nameEl.className = 'ni-name';
    nameEl.textContent = node.name || node.id || 'Unknown';
    s1.body.appendChild(nameEl);

    const badges = document.createElement('div');
    badges.className = 'ni-badges';

    const atomType = node.atom_type || node.type || '';
    if (atomType) badges.appendChild(_tag(atomType, 'ni-tag-type'));

    const tier = typeof getNodeTier === 'function' ? getNodeTier(node) : (node.tier || '');
    if (tier) badges.appendChild(_tag(tier, 'ni-tag-tier'));

    s1.body.appendChild(badges);

    const tags = document.createElement('div');
    tags.className = 'ni-tags';

    const ring = typeof getNodeRing === 'function' ? getNodeRing(node) : (node.ring || '');
    if (ring) tags.appendChild(_tag('Ring: ' + ring));

    const layer = node.layer || '';
    if (layer) tags.appendChild(_tag('Layer: ' + layer));

    const role = node.role || '';
    if (role) tags.appendChild(_tag('Role: ' + role));

    const family = typeof getNodeAtomFamily === 'function' ? getNodeAtomFamily(node) : (node.atom_family || '');
    if (family) tags.appendChild(_tag('Family: ' + family));

    s1.body.appendChild(tags);

    const filePath = node.file_path || node.file || '';
    if (filePath) {
        const fileEl = document.createElement('div');
        fileEl.className = 'ni-file';
        fileEl.textContent = filePath.length > 60 ? '...' + filePath.slice(-57) : filePath;
        fileEl.title = filePath;
        s1.body.appendChild(fileEl);
    }

    card.appendChild(s1.sec);

    // ── Section 2: Metrics (open by default) ──
    const s2 = _section('METRICS', true);

    const complexity = node.cyclomatic_complexity || node.complexity || null;
    const loc = node.loc || node.lines_of_code || null;
    const fanIn = node.fan_in || node.in_degree || null;
    const fanOut = node.fan_out || node.out_degree || null;
    const trust = node.trust || node.trust_score || null;

    const metricsGrid = document.createElement('div');
    metricsGrid.className = 'ni-metrics-grid';

    if (complexity != null) metricsGrid.appendChild(_kv('Complexity', complexity));
    if (loc != null) metricsGrid.appendChild(_kv('LOC', loc));
    if (fanIn != null) metricsGrid.appendChild(_kv('Fan-in', fanIn));
    if (fanOut != null) metricsGrid.appendChild(_kv('Fan-out', fanOut));
    if (trust != null) metricsGrid.appendChild(_kv('Trust', trust));

    const tokens = node.tokens || null;
    if (tokens != null) metricsGrid.appendChild(_kv('Tokens', tokens));

    const coherence = node.coherence_score || null;
    if (coherence != null) metricsGrid.appendChild(_kv('Coherence', coherence));

    const purity = node.D6_pure_score || node.purity || null;
    if (purity != null) metricsGrid.appendChild(_kv('Purity', purity));

    s2.body.appendChild(metricsGrid);

    // Relative bars for in/out degree
    if (node.in_degree != null || node.out_degree != null) {
        const barSection = document.createElement('div');
        barSection.className = 'ni-degree-bars';

        if (node.in_degree != null) {
            const row = document.createElement('div');
            row.className = 'ni-bar-row';
            row.innerHTML = `<span class="ni-bar-label">In-degree</span><span class="ni-bar-value">${node.in_degree}</span>`;
            row.appendChild(_bar(node.in_degree, maxes.in_degree, _relativeBarClass(node.in_degree, maxes.in_degree)));
            barSection.appendChild(row);
        }
        if (node.out_degree != null) {
            const row = document.createElement('div');
            row.className = 'ni-bar-row';
            row.innerHTML = `<span class="ni-bar-label">Out-degree</span><span class="ni-bar-value">${node.out_degree}</span>`;
            row.appendChild(_bar(node.out_degree, maxes.out_degree, _relativeBarClass(node.out_degree, maxes.out_degree)));
            barSection.appendChild(row);
        }

        s2.body.appendChild(barSection);
    }

    card.appendChild(s2.sec);

    // ── Section 3: DNA / RPBL (open by default) ──
    const resp = _get(node, 'responsibility', null);
    const pure = _get(node, 'purity', null) ?? _get(node, 'D6_pure_score', null);
    const bound = _get(node, 'boundary_score', null);
    const life = _get(node, 'lifecycle_score', null);
    const hasDNA = resp != null || pure != null || bound != null || life != null;

    if (hasDNA) {
        const s3 = _section('DNA (RPBL)', true);

        const dnaEntries = [
            { label: 'Responsibility', value: resp },
            { label: 'Purity', value: pure },
            { label: 'Boundary', value: bound },
            { label: 'Lifecycle', value: life },
        ];

        for (const { label, value } of dnaEntries) {
            if (value == null) continue;
            const row = document.createElement('div');
            row.className = 'ni-dna-row';

            const lbl = document.createElement('span');
            lbl.className = 'ni-dna-label';
            lbl.textContent = label;

            const val = document.createElement('span');
            val.className = 'ni-dna-value';
            val.textContent = typeof value === 'number' ? value.toFixed(1) : value;

            row.appendChild(lbl);
            row.appendChild(_bar(value, 10, _signalClass(value)));
            row.appendChild(val);

            s3.body.appendChild(row);
        }

        card.appendChild(s3.sec);
    }

    // ── Section 4: Topology (collapsed by default) ──
    const s4 = _section('TOPOLOGY', false);

    const topoFields = [
        ['PageRank', node.pagerank],
        ['Centrality', node.betweenness_centrality || node.centrality],
        ['Depth', node.depth],
        ['Boundary', node.boundary],
        ['State', node.state || node.statefulness],
        ['Lifecycle', node.lifecycle],
        ['Convergence', node.convergence_count],
    ];

    for (const [label, value] of topoFields) {
        if (value != null) s4.body.appendChild(_kv(label, value));
    }

    if (s4.body.childElementCount > 0) card.appendChild(s4.sec);

    // ── Section 5: Evolution (collapsed by default) ──
    const churn = _get(node, 'churn', null);
    const age = _get(node, 'age', null);
    const hasEvolution = churn != null || age != null;

    if (hasEvolution) {
        const s5 = _section('EVOLUTION', false);

        if (churn != null) {
            const row = _kv('Churn (commits)', churn);
            // Hot badge if churn > 75th percentile
            if (maxes.churn > 0 && churn > maxes.churn * 0.75) {
                const hot = document.createElement('span');
                hot.className = 'ni-tag signal-bad';
                hot.textContent = 'HOT';
                hot.style.marginLeft = '8px';
                row.appendChild(hot);
            }
            s5.body.appendChild(row);
        }
        if (age != null) s5.body.appendChild(_kv('Age (days)', age));

        card.appendChild(s5.sec);
    }

    // ── Section 6: Source (collapsed by default) ──
    const bodyText = node.body || node.source || '';
    const s6 = _section('SOURCE', false);

    if (bodyText) {
        const pre = document.createElement('pre');
        pre.className = 'ni-code';
        pre.textContent = bodyText.length > 500 ? bodyText.slice(0, 500) + '\n...' : bodyText;
        s6.body.appendChild(pre);
    } else {
        const noSrc = document.createElement('div');
        noSrc.className = 'ni-no-source';
        noSrc.textContent = '// source not available';
        s6.body.appendChild(noSrc);
    }
    card.appendChild(s6.sec);

    // Add to container and activate intel mode
    container.appendChild(card);

    const panel = container.closest('.selection-panel');
    if (panel) panel.classList.add('intel-active');
}

/**
 * Clean up intel-active state from the selection panel.
 */
function clearIntelState() {
    const panel = document.querySelector('.selection-panel.intel-active');
    if (panel) panel.classList.remove('intel-active');
}

// ═══════════════════════════════════════════════════════════════════════
// MODULE EXPORT
// ═══════════════════════════════════════════════════════════════════════

export { renderNodeCard, clearIntelState };

const NODE_INTEL = { renderNodeCard, clearIntelState };
window.NODE_INTEL = NODE_INTEL;

console.log('[Module] NODE_INTEL loaded - Node Intelligence Card');
