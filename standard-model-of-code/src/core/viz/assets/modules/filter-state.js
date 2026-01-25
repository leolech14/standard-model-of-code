/**
 * FILTER STATE MODULE
 *
 * Centralized filter state for the Collider visualization.
 * Manages search, tier filters, role filters, degree constraints, etc.
 *
 * @module FILTER_STATE
 *
 * Usage:
 *   FILTER_STATE.setSearch('UserService')
 *   FILTER_STATE.toggleTier('T2')
 *   FILTER_STATE.setMinDegree(3)
 *   FILTER_STATE.apply()  // Triggers graph filter
 */

window.FILTER_STATE = (function() {
    'use strict';

    // State object
    const _state = {
        // Text search
        search: '',

        // Categorical filters (Set = enabled, empty = show all)
        tiers: new Set(),
        families: new Set(),
        roles: new Set(),
        atoms: new Set(),
        edgeTypes: new Set(),

        // Boolean filters
        hideOrphans: false,
        hideDeadCode: false,
        hideExternal: false,

        // Numeric constraints
        minDegree: 0,
        maxDegree: Infinity,
        minComplexity: 0,
        maxComplexity: Infinity
    };

    let _debounceTimer = null;

    // ==========================================================================
    // STATE ACCESSORS
    // ==========================================================================

    function getState() {
        return {
            ..._state,
            tiers: [..._state.tiers],
            families: [..._state.families],
            roles: [..._state.roles],
            atoms: [..._state.atoms],
            edgeTypes: [..._state.edgeTypes]
        };
    }

    function setState(obj) {
        Object.keys(obj).forEach(k => {
            if (k in _state) {
                if (_state[k] instanceof Set) {
                    _state[k] = new Set(obj[k] || []);
                } else {
                    _state[k] = obj[k];
                }
            }
        });
    }

    // ==========================================================================
    // SEARCH
    // ==========================================================================

    function setSearch(term) {
        _state.search = (term || '').toLowerCase().trim();
        _debouncedApply();
    }

    function getSearch() {
        return _state.search;
    }

    // ==========================================================================
    // CATEGORICAL TOGGLES
    // ==========================================================================

    function toggleTier(tier) {
        if (_state.tiers.has(tier)) {
            _state.tiers.delete(tier);
        } else {
            _state.tiers.add(tier);
        }
        _debouncedApply();
    }

    function toggleFamily(family) {
        if (_state.families.has(family)) {
            _state.families.delete(family);
        } else {
            _state.families.add(family);
        }
        _debouncedApply();
    }

    function toggleRole(role) {
        if (_state.roles.has(role)) {
            _state.roles.delete(role);
        } else {
            _state.roles.add(role);
        }
        _debouncedApply();
    }

    function toggleEdgeType(type) {
        if (_state.edgeTypes.has(type)) {
            _state.edgeTypes.delete(type);
        } else {
            _state.edgeTypes.add(type);
        }
        _debouncedApply();
    }

    function clearCategory(category) {
        if (_state[category] instanceof Set) {
            _state[category].clear();
            _debouncedApply();
        }
    }

    // ==========================================================================
    // BOOLEAN FILTERS
    // ==========================================================================

    function setHideOrphans(hide) {
        _state.hideOrphans = !!hide;
        _debouncedApply();
    }

    function setHideDeadCode(hide) {
        _state.hideDeadCode = !!hide;
        _debouncedApply();
    }

    function setHideExternal(hide) {
        _state.hideExternal = !!hide;
        _debouncedApply();
    }

    // ==========================================================================
    // NUMERIC CONSTRAINTS
    // ==========================================================================

    function setMinDegree(val) {
        _state.minDegree = Math.max(0, parseInt(val) || 0);
        _debouncedApply();
    }

    function setMaxDegree(val) {
        _state.maxDegree = val === '' || val === null ? Infinity : Math.max(0, parseInt(val) || 0);
        _debouncedApply();
    }

    function setMinComplexity(val) {
        _state.minComplexity = Math.max(0, parseInt(val) || 0);
        _debouncedApply();
    }

    function setMaxComplexity(val) {
        _state.maxComplexity = val === '' || val === null ? Infinity : Math.max(0, parseInt(val) || 0);
        _debouncedApply();
    }

    // ==========================================================================
    // FILTER APPLICATION
    // ==========================================================================

    function _debouncedApply() {
        clearTimeout(_debounceTimer);
        _debounceTimer = setTimeout(apply, 50);
    }

    /**
     * Apply current filter state to the graph
     * Uses Graph.nodeVisibility() and EVENT_BUS
     */
    function apply() {
        if (typeof Graph === 'undefined' || !Graph) return;

        const filterFn = buildFilterFunction();

        // Apply to 3d-force-graph
        Graph.nodeVisibility(filterFn);

        // Emit event for other components
        if (typeof EVENT_BUS !== 'undefined') {
            EVENT_BUS.emit('filter:changed', getState());
        }

        // Trigger throttled refresh
        if (typeof REFRESH !== 'undefined' && REFRESH.throttled) {
            REFRESH.throttled();
        }

        // Update stats display
        _updateFilterStats();
    }

    /**
     * Build the filter function from current state
     */
    function buildFilterFunction() {
        return (node) => {
            // Search filter
            if (_state.search) {
                const searchable = (node.id + ' ' + (node.name || '') + ' ' + (node.file_path || '')).toLowerCase();
                if (!searchable.includes(_state.search)) return false;
            }

            // Tier filter
            if (_state.tiers.size > 0 && !_state.tiers.has(node.tier)) return false;

            // Family filter
            if (_state.families.size > 0 && !_state.families.has(node.family)) return false;

            // Role filter
            if (_state.roles.size > 0 && !_state.roles.has(node.role)) return false;

            // Orphan filter
            if (_state.hideOrphans) {
                const degree = (node.in_degree || 0) + (node.out_degree || 0);
                if (degree === 0) return false;
            }

            // Dead code filter (no incoming edges)
            if (_state.hideDeadCode && (node.in_degree || 0) === 0) return false;

            // External filter (boundary nodes)
            if (_state.hideExternal && node.id?.startsWith('__codome__')) return false;

            // Degree constraints
            const degree = (node.in_degree || 0) + (node.out_degree || 0);
            if (degree < _state.minDegree) return false;
            if (degree > _state.maxDegree) return false;

            // Complexity constraints
            if (node.complexity !== undefined) {
                if (node.complexity < _state.minComplexity) return false;
                if (node.complexity > _state.maxComplexity) return false;
            }

            return true;
        };
    }

    /**
     * Update filter stats display
     */
    function _updateFilterStats() {
        const statsEl = document.getElementById('filter-stats');
        if (!statsEl) return;

        let activeCount = 0;
        if (_state.search) activeCount++;
        if (_state.tiers.size > 0) activeCount++;
        if (_state.families.size > 0) activeCount++;
        if (_state.roles.size > 0) activeCount++;
        if (_state.hideOrphans) activeCount++;
        if (_state.hideDeadCode) activeCount++;
        if (_state.minDegree > 0) activeCount++;

        statsEl.textContent = activeCount > 0 ? `${activeCount} active` : '';
    }

    /**
     * Reset all filters to default
     */
    function reset() {
        _state.search = '';
        _state.tiers.clear();
        _state.families.clear();
        _state.roles.clear();
        _state.atoms.clear();
        _state.edgeTypes.clear();
        _state.hideOrphans = false;
        _state.hideDeadCode = false;
        _state.hideExternal = false;
        _state.minDegree = 0;
        _state.maxDegree = Infinity;
        _state.minComplexity = 0;
        _state.maxComplexity = Infinity;
        apply();
    }

    // ==========================================================================
    // PERSISTENCE
    // ==========================================================================

    const STORAGE_KEY = 'collider_filter_state_v1';

    function save() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(getState()));
        } catch (e) { /* ignore */ }
    }

    function load() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) setState(JSON.parse(saved));
        } catch (e) { /* ignore */ }
    }

    return {
        // State
        getState,
        setState,

        // Search
        setSearch,
        getSearch,

        // Categorical
        toggleTier,
        toggleFamily,
        toggleRole,
        toggleEdgeType,
        clearCategory,

        // Boolean
        setHideOrphans,
        setHideDeadCode,
        setHideExternal,

        // Numeric
        setMinDegree,
        setMaxDegree,
        setMinComplexity,
        setMaxComplexity,

        // Actions
        apply,
        reset,
        buildFilterFunction,

        // Persistence
        save,
        load
    };

})();

console.log('[Module] FILTER_STATE loaded');
