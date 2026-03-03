"""
Color Encoding Layer — maps data compartments to OKLCH channels.

Sits between data_chemistry (signal producer) and appearance_engine (renderer):

    data_chemistry.py ──→ color_encoding.py ──→ appearance_engine.py
                              ↑
                        color_science.py
                        (primitives)

The 3-channel model:
    H (hue)       = categorical identity  (tier, ring, file, level)
    L (lightness) = continuous metric A    (health, complexity, coherence)
    C (chroma)    = continuous metric B    (confidence, purity, coverage)

Pure Python, zero external dependencies beyond color_science (stdlib only).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.core.viz.color_science import (
    gamut_map_oklch,
    modulate_oklch,
    oklch_to_hex,
)


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass(frozen=True)
class ChannelMapping:
    """Rule for mapping a single data metric to one OKLCH channel."""
    metric: str                             # node/edge field name
    channel: str                            # 'lightness' | 'chroma' | 'hue'
    output_range: Tuple[float, float]       # target range in OKLCH units
    normalize: str = 'global'               # 'global' | 'per_group'
    group_by: Optional[str] = None          # field for per_group normalization
    invert: bool = False                    # high metric → low channel value


@dataclass(frozen=True)
class ViewSpec:
    """Complete encoding specification — which data maps to which channels."""
    name: str
    hue_source: str                         # 'tier' | 'ring' | 'file' | 'level' | 'topology_role'
    lightness: Optional[ChannelMapping] = None
    chroma: Optional[ChannelMapping] = None
    edge_mapping: Optional[ChannelMapping] = None


@dataclass
class EncodingReport:
    """Summary of what encode_all() did."""
    view_name: str
    nodes_encoded: int = 0
    edges_encoded: int = 0
    convergent_tagged: int = 0
    channels_used: List[str] = field(default_factory=list)
    missing_data: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# NEUTRAL DEFAULTS
# =============================================================================

# When a metric is missing, fall back to these perceptually neutral values.
NEUTRAL_L = 0.60
NEUTRAL_C = 0.08


# =============================================================================
# PRESET VIEWS
# =============================================================================

VIEW_DEFAULT = ViewSpec(
    name='default',
    hue_source='tier',
    # L and C are None → preserves current behavior (fixed per category)
)

VIEW_ARCHITECTURE = ViewSpec(
    name='architecture',
    hue_source='tier',
    lightness=ChannelMapping(
        metric='coherence_score',
        channel='lightness',
        output_range=(0.35, 0.85),
    ),
    chroma=ChannelMapping(
        metric='D6_pure_score',
        channel='chroma',
        output_range=(0.02, 0.20),
    ),
)

VIEW_HEALTH = ViewSpec(
    name='health',
    hue_source='tier',
    lightness=ChannelMapping(
        metric='cyclomatic_complexity',
        channel='lightness',
        output_range=(0.35, 0.85),
        invert=True,  # high complexity → low lightness (dark = bad)
    ),
    chroma=ChannelMapping(
        metric='coherence_score',
        channel='chroma',
        output_range=(0.02, 0.20),
    ),
)

VIEW_TOPOLOGY = ViewSpec(
    name='topology',
    hue_source='topology_role',
    lightness=ChannelMapping(
        metric='pagerank',
        channel='lightness',
        output_range=(0.35, 0.85),
    ),
    chroma=ChannelMapping(
        metric='betweenness_centrality',
        channel='chroma',
        output_range=(0.02, 0.20),
    ),
)

VIEW_FILES = ViewSpec(
    name='files',
    hue_source='file',
    lightness=ChannelMapping(
        metric='coherence_score',
        channel='lightness',
        output_range=(0.35, 0.85),
    ),
    chroma=ChannelMapping(
        metric='D6_pure_score',
        channel='chroma',
        output_range=(0.02, 0.20),
    ),
)

PRESET_VIEWS = {
    'default': VIEW_DEFAULT,
    'architecture': VIEW_ARCHITECTURE,
    'health': VIEW_HEALTH,
    'topology': VIEW_TOPOLOGY,
    'files': VIEW_FILES,
}


# =============================================================================
# BASE HUE TABLES
# =============================================================================

# Tier hues — matching appearance_engine's tier colors, expressed in OKLCH hue degrees.
_TIER_HUES: Dict[str, float] = {
    'CORE': 200.0,         # cyan / teal
    'ARCH': 280.0,         # purple
    'EXT.DISCOVERED': 60.0,  # warm yellow
    'EXT': 145.0,          # green
}

# Ring hues — Clean Architecture layers
_RING_HUES: Dict[str, float] = {
    'DOMAIN': 30.0,
    'APPLICATION': 60.0,
    'PRESENTATION': 145.0,
    'INTERFACE': 200.0,
    'INFRASTRUCTURE': 280.0,
    'CROSS_CUTTING': 330.0,
    'TEST': 100.0,
    'UNKNOWN': 0.0,
}

# Topology role hues
_TOPOLOGY_HUES: Dict[str, float] = {
    'hub': 30.0,
    'authority': 145.0,
    'bridge': 200.0,
    'leaf': 280.0,
    'isolate': 0.0,
}


def _resolve_base_hue(node: Dict[str, Any], hue_source: str) -> float:
    """Look up the base hue for a node given the hue source axis."""
    if hue_source == 'tier':
        atom = node.get('atom', '')
        for prefix, hue in _TIER_HUES.items():
            if atom.startswith(prefix):
                return hue
        return 0.0  # fallback for unrecognized atoms
    elif hue_source == 'ring':
        ring = node.get('ring', 'UNKNOWN').upper()
        return _RING_HUES.get(ring, 0.0)
    elif hue_source == 'file':
        # Golden-angle hue distribution per file index
        file_idx = node.get('fileIdx', 0)
        return (file_idx * 137.508) % 360.0
    elif hue_source == 'level':
        level = node.get('level', 0)
        # Map levels 0-15 across hue wheel
        return (level * 22.5) % 360.0
    elif hue_source == 'topology_role':
        role = node.get('topology_role', 'isolate')
        return _TOPOLOGY_HUES.get(role, 0.0)
    return 0.0


# =============================================================================
# NORMALIZATION
# =============================================================================

def _collect_metric_values(
    items: List[Dict[str, Any]],
    metric: str,
) -> List[float]:
    """Extract numeric values for a metric, skipping missing/non-numeric."""
    values = []
    for item in items:
        val = item.get(metric)
        if val is not None:
            try:
                values.append(float(val))
            except (TypeError, ValueError):
                pass
    return values


def _normalize_global(
    items: List[Dict[str, Any]],
    mapping: ChannelMapping,
) -> Dict[int, float]:
    """Normalize a metric globally across all items. Returns {index: normalized_value}."""
    values = _collect_metric_values(items, mapping.metric)
    if not values:
        return {}

    v_min = min(values)
    v_max = max(values)
    v_range = v_max - v_min

    lo, hi = mapping.output_range
    result: Dict[int, float] = {}
    for i, item in enumerate(items):
        val = item.get(mapping.metric)
        if val is None:
            continue
        try:
            fval = float(val)
        except (TypeError, ValueError):
            continue

        t = (fval - v_min) / v_range if v_range > 0 else 0.5
        if mapping.invert:
            t = 1.0 - t
        result[i] = lo + t * (hi - lo)

    return result


def _normalize_per_group(
    items: List[Dict[str, Any]],
    mapping: ChannelMapping,
) -> Dict[int, float]:
    """Normalize a metric per group. Returns {index: normalized_value}."""
    group_key = mapping.group_by or 'atom_family'

    # Partition into groups
    groups: Dict[str, List[Tuple[int, float]]] = {}
    for i, item in enumerate(items):
        val = item.get(mapping.metric)
        if val is None:
            continue
        try:
            fval = float(val)
        except (TypeError, ValueError):
            continue
        grp = str(item.get(group_key, '_ungrouped'))
        if grp not in groups:
            groups[grp] = []
        groups[grp].append((i, fval))

    lo, hi = mapping.output_range
    result: Dict[int, float] = {}
    for _grp_name, members in groups.items():
        vals = [v for _, v in members]
        v_min = min(vals)
        v_max = max(vals)
        v_range = v_max - v_min

        for idx, fval in members:
            t = (fval - v_min) / v_range if v_range > 0 else 0.5
            if mapping.invert:
                t = 1.0 - t
            result[idx] = lo + t * (hi - lo)

    return result


def _normalize(
    items: List[Dict[str, Any]],
    mapping: ChannelMapping,
) -> Dict[int, float]:
    """Dispatch to global or per-group normalization."""
    if mapping.normalize == 'per_group':
        return _normalize_per_group(items, mapping)
    return _normalize_global(items, mapping)


# =============================================================================
# CORE ENCODING FUNCTIONS
# =============================================================================

def tag_convergence(
    nodes: List[Dict[str, Any]],
    chemistry_result: Any,
) -> int:
    """Tag nodes with convergence data from chemistry analysis.

    For each convergent node found in the chemistry result, sets:
        node['convergence_severity']  = 'moderate' | 'high' | 'critical'
        node['convergence_signals']   = list of signal names
        node['convergence_count']     = number of converging signals

    Args:
        nodes: List of node dicts (mutated in place)
        chemistry_result: ChemistryResult (or dict with 'convergence' key)

    Returns:
        Number of nodes tagged
    """
    # Extract convergence data — handle both object and dict forms
    convergence = None
    if hasattr(chemistry_result, 'convergence'):
        convergence = chemistry_result.convergence
    elif isinstance(chemistry_result, dict):
        convergence = chemistry_result.get('convergence')

    if convergence is None:
        return 0

    # Build lookup: node_id → convergence info
    conv_nodes = []
    if hasattr(convergence, 'convergent_nodes'):
        conv_nodes = convergence.convergent_nodes
    elif isinstance(convergence, dict):
        conv_nodes = convergence.get('convergent_nodes', [])

    if not conv_nodes:
        return 0

    lookup: Dict[str, Any] = {}
    for cn in conv_nodes:
        if hasattr(cn, 'node_id'):
            lookup[cn.node_id] = cn
        elif isinstance(cn, dict):
            lookup[cn.get('node_id', '')] = cn

    # Tag matching nodes
    tagged = 0
    for node in nodes:
        node_id = node.get('id', '')
        if node_id in lookup:
            cn = lookup[node_id]
            if hasattr(cn, 'severity'):
                node['convergence_severity'] = cn.severity
                node['convergence_signals'] = list(cn.signals)
                node['convergence_count'] = cn.signal_count
            else:
                node['convergence_severity'] = cn.get('severity', 'moderate')
                node['convergence_signals'] = list(cn.get('signals', []))
                node['convergence_count'] = cn.get('signal_count', 0)
            tagged += 1

    return tagged


def encode_nodes(
    nodes: List[Dict[str, Any]],
    view: ViewSpec,
) -> Tuple[int, Dict[str, int]]:
    """Apply a ViewSpec to encode nodes with OKLCH colors.

    For each node:
        1. Resolve base hue from view.hue_source
        2. Normalize lightness metric → L channel (if mapped)
        3. Normalize chroma metric → C channel (if mapped)
        4. Gamut-map and write node['encoded_color'] as hex

    Args:
        nodes: List of node dicts (mutated in place)
        view: ViewSpec defining the encoding

    Returns:
        (nodes_encoded, missing_data) where missing_data maps metric → skip count
    """
    # Pre-compute normalized channel values
    l_values: Dict[int, float] = {}
    c_values: Dict[int, float] = {}
    missing: Dict[str, int] = {}

    if view.lightness:
        l_values = _normalize(nodes, view.lightness)
        missing[view.lightness.metric] = len(nodes) - len(l_values)

    if view.chroma:
        c_values = _normalize(nodes, view.chroma)
        missing[view.chroma.metric] = len(nodes) - len(c_values)

    encoded = 0
    for i, node in enumerate(nodes):
        H = _resolve_base_hue(node, view.hue_source)
        L = l_values.get(i, NEUTRAL_L)
        C = c_values.get(i, NEUTRAL_C)

        # Gamut-map and convert
        mL, mC, mH = gamut_map_oklch(L, C, H)
        node['encoded_color'] = oklch_to_hex(mL, mC, mH)
        encoded += 1

    return encoded, missing


def encode_edges(
    edges: List[Dict[str, Any]],
    mapping: Optional[ChannelMapping] = None,
) -> int:
    """Apply a ChannelMapping to encode edges with OKLCH colors.

    Default maps edge 'confidence' to a hue gradient (red → green).

    Args:
        edges: List of edge dicts (mutated in place)
        mapping: Optional ChannelMapping for the edge metric

    Returns:
        Number of edges encoded
    """
    if mapping is None:
        # Default: confidence → hue gradient
        mapping = ChannelMapping(
            metric='confidence',
            channel='hue',
            output_range=(30.0, 145.0),  # red-orange → green
        )

    values = _normalize_global(edges, mapping)
    if not values:
        return 0

    encoded = 0
    for i, edge in enumerate(edges):
        if i not in values:
            continue

        mapped_val = values[i]

        if mapping.channel == 'hue':
            L, C, H = 0.55, 0.12, mapped_val
        elif mapping.channel == 'lightness':
            H = 200.0  # default edge hue
            L, C = mapped_val, 0.10
        elif mapping.channel == 'chroma':
            H = 200.0
            L, C = 0.55, mapped_val
        else:
            continue

        mL, mC, mH = gamut_map_oklch(L, C, H)
        edge['encoded_color'] = oklch_to_hex(mL, mC, mH)
        encoded += 1

    return encoded


def encode_all(
    full_output: Dict[str, Any],
    view: Optional[ViewSpec] = None,
    chemistry: Any = None,
) -> EncodingReport:
    """Orchestrator: encode nodes + edges + convergence tagging in one call.

    Args:
        full_output: The full analysis output dict (contains 'nodes', 'edges')
        view: ViewSpec to apply (defaults to VIEW_DEFAULT)
        chemistry: ChemistryResult or dict (optional, for convergence tagging)

    Returns:
        EncodingReport summarizing what was done
    """
    if view is None:
        view = VIEW_DEFAULT

    report = EncodingReport(view_name=view.name)
    channels = []

    nodes = full_output.get('nodes', [])
    edges = full_output.get('edges', [])

    # 1. Tag convergence (before encoding, so nodes carry convergence metadata)
    if chemistry is not None:
        report.convergent_tagged = tag_convergence(nodes, chemistry)

    # 2. Encode nodes
    if nodes:
        report.nodes_encoded, report.missing_data = encode_nodes(nodes, view)
        channels.append('hue')
        if view.lightness:
            channels.append('lightness')
        if view.chroma:
            channels.append('chroma')

    # 3. Encode edges
    if edges:
        report.edges_encoded = encode_edges(edges, view.edge_mapping)

    report.channels_used = channels
    return report
