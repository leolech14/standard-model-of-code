/**
 * ═══════════════════════════════════════════════════════════════════════════
 * SYNDROME DASHBOARD - Chemistry diagnosis panel
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Surfaces COLLIDER_DATA.chemistry.syndromes as severity cards with
 * clickable affected entities that highlight in the graph.
 *
 * Triggered by "Dx" dock button. Floating panel above the dock.
 *
 * @module SYNDROMES
 * @version 1.0.0
 */

let _panel = null;
let _visible = false;

// ═══════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════

function init() {
    const btn = document.getElementById('btn-dx');
    if (!btn) return;

    btn.addEventListener('click', toggle);
    console.log('[Module] SYNDROMES loaded - Diagnosis panel');
}

// ═══════════════════════════════════════════════════════════════════════
// PANEL MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════

function toggle() {
    if (_visible) {
        hide();
    } else {
        show();
    }
}

function show() {
    if (!_panel) _panel = _buildPanel();
    if (!_panel) return;
    _panel.style.display = 'block';
    _visible = true;
    const btn = document.getElementById('btn-dx');
    if (btn) btn.classList.add('active');
}

function hide() {
    if (_panel) _panel.style.display = 'none';
    _visible = false;
    const btn = document.getElementById('btn-dx');
    if (btn) btn.classList.remove('active');
}

// ═══════════════════════════════════════════════════════════════════════
// PANEL BUILDER
// ═══════════════════════════════════════════════════════════════════════

function _buildPanel() {
    const chemistry = window.COLLIDER_DATA?.chemistry || {};
    const syndromes = chemistry.syndromes || [];
    const contradictions = chemistry.contradictions || [];

    if (!syndromes.length && !contradictions.length) {
        if (typeof window.showToast === 'function') {
            window.showToast('No syndromes detected', 2000);
        }
        return null;
    }

    const panel = document.createElement('div');
    panel.className = 'syndrome-panel';
    panel.id = 'syndrome-panel';

    // Header
    const header = document.createElement('div');
    header.className = 'syndrome-header';

    const title = document.createElement('div');
    title.className = 'syndrome-title';
    title.textContent = 'DIAGNOSIS';

    const closeBtn = document.createElement('button');
    closeBtn.className = 'syndrome-close';
    closeBtn.textContent = '\u00D7';
    closeBtn.addEventListener('click', hide);

    header.appendChild(title);
    header.appendChild(closeBtn);
    panel.appendChild(header);

    // Compound severity bar
    if (chemistry.compound_severity != null) {
        const sev = document.createElement('div');
        sev.className = 'syndrome-compound';

        const barWrap = document.createElement('div');
        barWrap.className = 'syndrome-compound-bar';
        const barFill = document.createElement('div');
        barFill.className = 'syndrome-compound-fill';
        const pct = Math.min(chemistry.compound_severity, 1) * 100;
        barFill.style.width = pct + '%';
        const cls = chemistry.compound_severity < 0.3 ? 'signal-good' : chemistry.compound_severity < 0.6 ? 'signal-warn' : 'signal-bad';
        barFill.classList.add(cls);
        barWrap.appendChild(barFill);

        const label = document.createElement('span');
        label.className = 'syndrome-compound-label';
        label.textContent = `Compound Severity: ${chemistry.compound_severity.toFixed(2)}`;

        sev.appendChild(barWrap);
        sev.appendChild(label);
        panel.appendChild(sev);
    }

    // Syndrome cards
    const cardsWrap = document.createElement('div');
    cardsWrap.className = 'syndrome-cards';

    for (const syn of syndromes) {
        cardsWrap.appendChild(_buildSyndromeCard(syn));
    }

    panel.appendChild(cardsWrap);

    // Contradictions section
    if (contradictions.length > 0) {
        const cHeader = document.createElement('div');
        cHeader.className = 'syndrome-section-title';
        cHeader.textContent = `Contradictions (${contradictions.length})`;
        panel.appendChild(cHeader);

        const cWrap = document.createElement('div');
        cWrap.className = 'syndrome-contradictions';

        for (const c of contradictions) {
            const card = document.createElement('div');
            card.className = 'syndrome-contradiction';

            const dims = c.dimensions || c.dimension_pair || [];
            const dimText = Array.isArray(dims) ? dims.join(' \u2194 ') : String(dims);

            const line1 = document.createElement('div');
            line1.className = 'syndrome-contradiction-dims';
            line1.textContent = `${dimText}: ${c.severity != null ? c.severity.toFixed(2) : ''}`;

            card.appendChild(line1);

            if (c.description || c.explanation) {
                const line2 = document.createElement('div');
                line2.className = 'syndrome-contradiction-desc';
                line2.textContent = c.description || c.explanation;
                card.appendChild(line2);
            }

            cWrap.appendChild(card);
        }

        panel.appendChild(cWrap);
    }

    // Inject into Z4: left-float zone
    const zone = document.getElementById('zone-left-float') || document.getElementById('hud');
    if (zone) {
        zone.appendChild(panel);
    }

    return panel;
}

function _buildSyndromeCard(syn) {
    const card = document.createElement('div');
    card.className = 'syndrome-card';

    // Header row: name + severity
    const header = document.createElement('div');
    header.className = 'syndrome-card-header';

    const name = document.createElement('span');
    name.className = 'syndrome-card-name';
    name.textContent = (syn.name || 'Unknown Syndrome').toUpperCase();

    const sevBadge = document.createElement('span');
    sevBadge.className = 'syndrome-card-sev';
    const sev = syn.severity != null ? syn.severity : 0;
    sevBadge.textContent = sev.toFixed(2);
    const cls = sev < 0.3 ? 'signal-good' : sev < 0.6 ? 'signal-warn' : 'signal-bad';
    sevBadge.classList.add(cls);

    header.appendChild(name);
    header.appendChild(sevBadge);
    card.appendChild(header);

    // Description
    if (syn.description) {
        const desc = document.createElement('div');
        desc.className = 'syndrome-card-desc';
        desc.textContent = syn.description;
        card.appendChild(desc);
    }

    // Signals
    if (syn.signals && syn.signals.length) {
        const sigs = document.createElement('div');
        sigs.className = 'syndrome-card-signals';
        sigs.textContent = 'Signals: ' + syn.signals.join(', ');
        card.appendChild(sigs);
    }

    // Affected entities + Highlight button
    const affected = syn.affected_entities || syn.affected || [];
    if (affected.length > 0) {
        const footer = document.createElement('div');
        footer.className = 'syndrome-card-footer';

        const count = document.createElement('span');
        count.className = 'syndrome-card-count';
        count.textContent = `Affected: ${affected.length} nodes`;

        const hlBtn = document.createElement('button');
        hlBtn.className = 'syndrome-highlight-btn';
        hlBtn.textContent = 'Highlight';
        hlBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (typeof SELECT !== 'undefined' && SELECT.set) {
                SELECT.set(affected);
            } else if (typeof window.setSelection === 'function') {
                window.setSelection(affected);
            }
        });

        footer.appendChild(count);
        footer.appendChild(hlBtn);
        card.appendChild(footer);
    }

    return card;
}

// ═══════════════════════════════════════════════════════════════════════
// MODULE EXPORT
// ═══════════════════════════════════════════════════════════════════════

export { init, toggle, show, hide };

const SYNDROMES = { init, toggle, show, hide };
window.SYNDROMES = SYNDROMES;

console.log('[Module] SYNDROMES registered');
