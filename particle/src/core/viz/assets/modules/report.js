/**
 * ═══════════════════════════════════════════════════════════════════════════
 * REPORT MODULE - Report panel, AI insights, and metrics display
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Handles the brain download report, AI insights panel, and metrics/KPI display.
 * Depends on: escapeHtml (from utils.js), DOM elements
 *
 * @module REPORT
 * @version 1.0.0
 */

window.REPORT = (function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // BRAIN DOWNLOAD REPORT
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Setup the brain download report panel
     * @param {Object} data - Data object with brain_download field
     */
    function setupReport(data) {
        const panel = document.getElementById('report-panel');
        const content = document.getElementById('report-content');
        // Guard: elements may not exist in minimal template
        if (!content) return;
        const report = (data && data.brain_download) ? data.brain_download : '';
        content.textContent = report || 'No report available.';
    }

    // ═══════════════════════════════════════════════════════════════════════
    // AI INSIGHTS PANEL
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Setup the AI insights panel
     * @param {Object} data - Data object with ai_insights field
     */
    function setupAIInsights(data) {
        const escapeHtml = window.escapeHtml || ((s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c])));

        const panel = document.getElementById('insights-panel');
        const content = document.getElementById('insights-content');
        const btn = document.getElementById('btn-insights');

        const insights = (data && data.ai_insights) ? data.ai_insights : null;

        if (!insights) {
            // Hide the button if no insights available
            if (btn) btn.style.display = 'none';
            return;
        }

        // Show the button
        if (btn) btn.style.display = 'inline-flex';

        // Render insights
        let html = '';

        // Executive Summary
        if (insights.executive_summary) {
            html += `<div class="insights-section">
                <div class="insights-section-title">Executive Summary</div>
                <div class="insights-summary">${escapeHtml(insights.executive_summary)}</div>
            </div>`;
        }

        // Patterns Detected
        if (insights.patterns_detected && insights.patterns_detected.length > 0) {
            html += `<div class="insights-section">
                <div class="insights-section-title">Patterns Detected</div>`;
            for (const pattern of insights.patterns_detected) {
                const confidencePercent = Math.round((pattern.confidence || 0) * 100);
                html += `<div class="insights-pattern">
                    <div class="insights-pattern-header">
                        <span class="insights-pattern-name">${escapeHtml(pattern.pattern_name || 'Unknown')}</span>
                        <span class="insights-pattern-type ${pattern.pattern_type || ''}">${escapeHtml(pattern.pattern_type || '')}</span>
                    </div>
                    <div class="insights-confidence">
                        <div class="insights-confidence-bar">
                            <div class="insights-confidence-fill" style="width: ${confidencePercent}%"></div>
                        </div>
                        <span>${confidencePercent}%</span>
                    </div>
                    ${pattern.evidence ? `<div class="insights-pattern-evidence">${escapeHtml(pattern.evidence)}</div>` : ''}
                    ${pattern.recommendation ? `<div class="insights-pattern-evidence" style="color: var(--color-accent-secondary);">Tip: ${escapeHtml(pattern.recommendation)}</div>` : ''}
                </div>`;
            }
            html += '</div>';
        }

        // Refactoring Opportunities
        if (insights.refactoring_opportunities && insights.refactoring_opportunities.length > 0) {
            html += `<div class="insights-section">
                <div class="insights-section-title">Refactoring Opportunities</div>`;
            for (const refactor of insights.refactoring_opportunities) {
                html += `<div class="insights-refactor">
                    <div class="insights-refactor-title">
                        ${escapeHtml(refactor.title || 'Untitled')}
                        <span class="insights-refactor-priority ${refactor.priority || 'LOW'}">${refactor.priority || 'LOW'}</span>
                    </div>
                    ${refactor.description ? `<div class="insights-refactor-desc">${escapeHtml(refactor.description)}</div>` : ''}
                    ${refactor.affected_files && refactor.affected_files.length > 0 ?
                        `<div class="insights-refactor-desc" style="margin-top: 4px; color: var(--color-text-muted);">Files: ${refactor.affected_files.slice(0, 3).map(f => escapeHtml(f)).join(', ')}${refactor.affected_files.length > 3 ? '...' : ''}</div>` : ''}
                </div>`;
            }
            html += '</div>';
        }

        // Topology Analysis
        if (insights.topology_analysis) {
            const topo = insights.topology_analysis;
            html += `<div class="insights-section">
                <div class="insights-section-title">Topology Analysis</div>
                ${topo.shape_interpretation ? `<div class="insights-summary">${escapeHtml(topo.shape_interpretation)}</div>` : ''}
                ${topo.health_assessment ? `<div class="insights-pattern-evidence">Health: ${escapeHtml(topo.health_assessment)}</div>` : ''}
                ${topo.coupling_analysis ? `<div class="insights-pattern-evidence">Coupling: ${escapeHtml(topo.coupling_analysis)}</div>` : ''}
            </div>`;
        }

        // Risk Areas
        if (insights.risk_areas && insights.risk_areas.length > 0) {
            html += `<div class="insights-section">
                <div class="insights-section-title">Risk Areas</div>`;
            for (const risk of insights.risk_areas) {
                html += `<div class="insights-risk">
                    <span class="insights-risk-level ${risk.risk_level || 'LOW'}">${risk.risk_level || 'LOW'}</span>
                    <div class="insights-risk-content">
                        <div class="insights-risk-area">${escapeHtml(risk.area || 'Unknown')}</div>
                        ${risk.description ? `<div class="insights-risk-desc">${escapeHtml(risk.description)}</div>` : ''}
                        ${risk.mitigation ? `<div class="insights-risk-desc" style="color: var(--color-accent-secondary); margin-top: 4px;">Tip: ${escapeHtml(risk.mitigation)}</div>` : ''}
                    </div>
                </div>`;
            }
            html += '</div>';
        }

        // Meta information
        if (insights.meta) {
            const meta = insights.meta;
            html += `<div class="insights-meta">
                Generated: ${meta.generated_at ? new Date(meta.generated_at).toLocaleString() : 'Unknown'}
                | Model: ${escapeHtml(meta.model || 'Unknown')}
                ${meta.confidence ? ` | Confidence: ${Math.round(meta.confidence * 100)}%` : ''}
            </div>`;
        }

        content.innerHTML = html || '<div class="insights-placeholder">No insights data available.</div>';
    }

    // ═══════════════════════════════════════════════════════════════════════
    // METRICS / KPI DISPLAY
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * Setup metrics and health indicators
     * @param {Object} data - Data object with kpis field
     */
    function setupMetrics(data) {
        const kpis = (data && data.kpis) ? data.kpis : {};

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.textContent = value;
        };

        const asNumber = (val) => {
            const num = Number(val);
            return Number.isFinite(num) ? num : null;
        };

        const formatPercent = (val) => {
            const num = asNumber(val);
            return num === null ? '--' : `${num.toFixed(1)}%`;
        };

        const formatCount = (val) => {
            const num = asNumber(val);
            return num === null ? '--' : `${Math.round(num)}`;
        };

        const formatScore = (val) => {
            const num = asNumber(val);
            return num === null ? '--' : `${num.toFixed(1)}/10`;
        };

        // Set metric values
        setText('metric-edge-resolution', formatPercent(kpis.edge_resolution_percent));
        setText('metric-call-ratio', formatPercent(kpis.call_ratio_percent));
        setText('metric-reachability', formatPercent(kpis.reachability_percent));
        setText('metric-dead-code', formatPercent(kpis.dead_code_percent));
        setText('metric-knot-score', formatScore(kpis.knot_score));
        setText('metric-topology', kpis.topology_shape || 'UNKNOWN');
        setText('metric-orphans', formatCount(kpis.orphan_count));
        setText('metric-top-hubs', formatCount(kpis.top_hub_count));

        // Set health indicators (traffic light bars)
        const setHealth = (id, level) => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('good', 'medium', 'bad', 'neutral');
                el.classList.add(level);
            }
        };

        // Edge Resolution: >90% good, 70-90% medium, <70% bad
        const edgeRes = asNumber(kpis.edge_resolution_percent);
        setHealth('health-edge-resolution', edgeRes === null ? 'neutral' : edgeRes >= 90 ? 'good' : edgeRes >= 70 ? 'medium' : 'bad');

        // Call Ratio: >60% good, 40-60% medium, <40% bad
        const callRatio = asNumber(kpis.call_ratio_percent);
        setHealth('health-call-ratio', callRatio === null ? 'neutral' : callRatio >= 60 ? 'good' : callRatio >= 40 ? 'medium' : 'bad');

        // Reachability: >90% good, 70-90% medium, <70% bad
        const reach = asNumber(kpis.reachability_percent);
        setHealth('health-reachability', reach === null ? 'neutral' : reach >= 90 ? 'good' : reach >= 70 ? 'medium' : 'bad');

        // Dead Code: <5% good, 5-15% medium, >15% bad (INVERTED - lower is better)
        const dead = asNumber(kpis.dead_code_percent);
        setHealth('health-dead-code', dead === null ? 'neutral' : dead <= 5 ? 'good' : dead <= 15 ? 'medium' : 'bad');

        // Knot Score: <3 good, 3-6 medium, >6 bad (INVERTED - lower is better)
        const knot = asNumber(kpis.knot_score);
        setHealth('health-knot-score', knot === null ? 'neutral' : knot <= 3 ? 'good' : knot <= 6 ? 'medium' : 'bad');

        // Topology: neutral (informational only)
        setHealth('health-topology', 'neutral');

        // Orphans: <10 good, 10-50 medium, >50 bad (INVERTED - lower is better)
        const orphans = asNumber(kpis.orphan_count);
        setHealth('health-orphans', orphans === null ? 'neutral' : orphans <= 10 ? 'good' : orphans <= 50 ? 'medium' : 'bad');

        // Top Hubs: neutral (informational only)
        setHealth('health-top-hubs', 'neutral');
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MODULE EXPORT
    // ═══════════════════════════════════════════════════════════════════════

    return {
        setupReport: setupReport,
        setupAIInsights: setupAIInsights,
        setupMetrics: setupMetrics
    };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BACKWARD COMPATIBILITY SHIMS
// ═══════════════════════════════════════════════════════════════════════════

window.setupReport = REPORT.setupReport;
window.setupAIInsights = REPORT.setupAIInsights;
window.setupMetrics = REPORT.setupMetrics;

console.log('[Module] REPORT loaded - 3 functions');
