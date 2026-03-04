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
class SemanticSignature:
    """What question does this view answer? Human-readable metadata."""
    domain: str                             # 'architecture' | 'health' | 'topology' | etc.
    question: str                           # e.g. "Where are the high-complexity, low-coherence nodes?"
    reading: str                            # e.g. "Dark + gray = complex, incoherent code"


@dataclass(frozen=True)
class ViewSpec:
    """Complete encoding specification — which data maps to which channels."""
    name: str
    hue_source: str                         # 'tier' | 'ring' | 'file' | 'level' | 'topology_role'
    lightness: Optional[ChannelMapping] = None
    chroma: Optional[ChannelMapping] = None
    edge_mapping: Optional[ChannelMapping] = None
    signature: Optional[SemanticSignature] = None


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
    edge_mapping=ChannelMapping(
        metric='confidence',
        channel='hue',
        output_range=(30.0, 145.0),  # warm (low confidence) → green (high)
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
        normalize='per_group',
        group_by='file_path',  # complexity relative to file peers, not global
    ),
    chroma=ChannelMapping(
        metric='coherence_score',
        channel='chroma',
        output_range=(0.02, 0.20),
    ),
    edge_mapping=ChannelMapping(
        metric='confidence',
        channel='hue',
        output_range=(30.0, 145.0),  # warm (low confidence) → green (high)
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

# =============================================================================
# NEW VIEWS — Architecture domain
# =============================================================================

VIEW_LAYERS = ViewSpec(
    name='layers',
    hue_source='ring',
    lightness=ChannelMapping(metric='coherence_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='D6_pure_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='architecture',
        question='Which architectural layers have the most coherent code?',
        reading='Bright + vivid = coherent, pure code',
    ),
)

VIEW_BOUNDARIES = ViewSpec(
    name='boundaries',
    hue_source='boundary',
    lightness=ChannelMapping(metric='coherence_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='D6_pure_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='architecture',
        question='Are boundary components well-defined?',
        reading='Bright + vivid = clean boundary; dark + gray = leaky abstraction',
    ),
)

VIEW_SCALE = ViewSpec(
    name='scale',
    hue_source='level',
    lightness=ChannelMapping(metric='loc', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='out_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='architecture',
        question='Where does code concentrate at each scale level?',
        reading='Bright = large files; vivid = many outgoing dependencies',
    ),
)

# =============================================================================
# NEW VIEWS — Health domain
# =============================================================================

VIEW_COMPLEXITY = ViewSpec(
    name='complexity',
    hue_source='tier',
    lightness=ChannelMapping(
        metric='cyclomatic_complexity', channel='lightness',
        output_range=(0.35, 0.85), invert=True,
    ),
    chroma=ChannelMapping(metric='loc', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='health',
        question='Where are the large, complex components?',
        reading='Dark = high complexity; vivid = large codebase',
    ),
)

VIEW_QUALITY = ViewSpec(
    name='quality',
    hue_source='tier',
    lightness=ChannelMapping(metric='q_total', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='coherence_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='health',
        question='Which components have the best overall quality?',
        reading='Bright + vivid = high quality + coherent',
    ),
)

VIEW_CONVERGENCE = ViewSpec(
    name='convergence',
    hue_source='convergence_severity',
    lightness=ChannelMapping(metric='convergence_count', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(
        metric='cyclomatic_complexity', channel='chroma',
        output_range=(0.02, 0.20), invert=True,
    ),
    signature=SemanticSignature(
        domain='health',
        question='Where do multiple problems converge?',
        reading='Red-orange hue = critical; bright = many signals; vivid = complex',
    ),
)

# =============================================================================
# NEW VIEWS — Topology domain
# =============================================================================

VIEW_INFLUENCE = ViewSpec(
    name='influence',
    hue_source='topology_role',
    lightness=ChannelMapping(metric='in_degree', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='out_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='topology',
        question='Which nodes are most connected?',
        reading='Bright = many dependents; vivid = many dependencies',
    ),
)

VIEW_COUPLING = ViewSpec(
    name='coupling',
    hue_source='tier',
    lightness=ChannelMapping(metric='in_degree', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='out_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='topology',
        question='How tightly coupled are components by tier?',
        reading='Bright = high afferent coupling; vivid = high efferent coupling',
    ),
)

VIEW_CENTRALITY = ViewSpec(
    name='centrality',
    hue_source='topology_role',
    lightness=ChannelMapping(metric='betweenness_centrality', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='pagerank', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='topology',
        question='Which nodes control information flow?',
        reading='Bright = high betweenness; vivid = high PageRank',
    ),
)

# =============================================================================
# NEW VIEWS — Files domain
# =============================================================================

VIEW_FILE_SIZE = ViewSpec(
    name='file_size',
    hue_source='file',
    lightness=ChannelMapping(metric='loc', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(
        metric='cyclomatic_complexity', channel='chroma', output_range=(0.02, 0.20),
    ),
    signature=SemanticSignature(
        domain='files',
        question='Which files are biggest and most complex?',
        reading='Bright = large file; vivid = high complexity',
    ),
)

VIEW_FILE_QUALITY = ViewSpec(
    name='file_quality',
    hue_source='file',
    lightness=ChannelMapping(metric='q_total', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='coherence_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='files',
        question='Which files have the healthiest code?',
        reading='Bright + vivid = high quality + coherent file',
    ),
)

# =============================================================================
# NEW VIEWS — Behavior domain
# =============================================================================

VIEW_BEHAVIOR = ViewSpec(
    name='behavior',
    hue_source='behavior',
    lightness=ChannelMapping(metric='coherence_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='D6_pure_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='behavior',
        question='How do behavioral types compare in quality?',
        reading='Bright + vivid = coherent, pure behavior',
    ),
)

VIEW_INTENT = ViewSpec(
    name='intent',
    hue_source='atom_family',
    lightness=ChannelMapping(metric='coherence_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(
        metric='cyclomatic_complexity', channel='chroma',
        output_range=(0.02, 0.20), invert=True,
    ),
    signature=SemanticSignature(
        domain='behavior',
        question='Which atom families are cleanest?',
        reading='Bright = coherent; vivid = low complexity',
    ),
)

VIEW_ROLES = ViewSpec(
    name='roles',
    hue_source='atom',
    lightness=ChannelMapping(metric='loc', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='coherence_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='behavior',
        question='How do specific atom types distribute?',
        reading='Bright = large; vivid = coherent',
    ),
)

# =============================================================================
# NEW VIEWS — Purity domain
# =============================================================================

VIEW_PURITY = ViewSpec(
    name='purity',
    hue_source='tier',
    lightness=ChannelMapping(metric='D6_pure_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='coherence_score', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='purity',
        question='Which tiers have the purest implementations?',
        reading='Bright = high purity; vivid = coherent',
    ),
)

VIEW_PURITY_BY_LAYER = ViewSpec(
    name='purity_by_layer',
    hue_source='ring',
    lightness=ChannelMapping(metric='D6_pure_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(
        metric='cyclomatic_complexity', channel='chroma',
        output_range=(0.02, 0.20), invert=True,
    ),
    signature=SemanticSignature(
        domain='purity',
        question='Where is purity weakest?',
        reading='Dark = impure; vivid = low complexity (inverted)',
    ),
)

VIEW_ISOLATION = ViewSpec(
    name='isolation',
    hue_source='topology_role',
    lightness=ChannelMapping(metric='D6_pure_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='in_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='purity',
        question='Are isolated components more pure?',
        reading='Bright = pure; vivid = many incoming deps',
    ),
)

# =============================================================================
# NEW VIEWS — Risk domain
# =============================================================================

VIEW_RISK = ViewSpec(
    name='risk',
    hue_source='tier',
    lightness=ChannelMapping(metric='convergence_count', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='cyclomatic_complexity', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='risk',
        question='Where are the highest risk areas?',
        reading='Bright = many convergence signals; vivid = complex',
    ),
)

VIEW_DEBT = ViewSpec(
    name='debt',
    hue_source='tier',
    lightness=ChannelMapping(
        metric='q_total', channel='lightness',
        output_range=(0.35, 0.85), invert=True,
    ),
    chroma=ChannelMapping(metric='loc', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='risk',
        question='Where is technical debt accumulating?',
        reading='Dark = low quality (debt); vivid = large codebase',
    ),
)

VIEW_FRAGILITY = ViewSpec(
    name='fragility',
    hue_source='topology_role',
    lightness=ChannelMapping(metric='convergence_count', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='betweenness_centrality', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='risk',
        question='Which bridges are fragile?',
        reading='Bright = many problems; vivid = high betweenness (bridge)',
    ),
)

VIEW_GOD_CLASS = ViewSpec(
    name='god_class',
    hue_source='atom_family',
    lightness=ChannelMapping(metric='loc', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='out_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='risk',
        question='Are there god classes hiding in the codebase?',
        reading='Bright = large; vivid = many outgoing deps (god class signal)',
    ),
)

# =============================================================================
# NEW VIEWS — Confidence domain
# =============================================================================

VIEW_CONFIDENCE = ViewSpec(
    name='confidence',
    hue_source='tier',
    lightness=ChannelMapping(metric='coherence_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='out_degree', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='confidence',
        question='How confident are we in each component?',
        reading='Bright = coherent (confident); vivid = many deps',
    ),
)

VIEW_CLARITY = ViewSpec(
    name='clarity',
    hue_source='atom_family',
    lightness=ChannelMapping(metric='D6_pure_score', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='q_total', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='confidence',
        question='Which atom families are most self-documenting?',
        reading='Bright = pure; vivid = high quality score',
    ),
)

# =============================================================================
# NEW VIEWS — Convergence domain
# =============================================================================

VIEW_HOTSPOTS = ViewSpec(
    name='hotspots',
    hue_source='file',
    lightness=ChannelMapping(metric='convergence_count', channel='lightness', output_range=(0.35, 0.85)),
    chroma=ChannelMapping(metric='cyclomatic_complexity', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='convergence',
        question='Which files are the biggest problem hotspots?',
        reading='Bright = many convergence signals; vivid = complex',
    ),
)

VIEW_SIGNALS = ViewSpec(
    name='signals',
    hue_source='convergence_severity',
    lightness=ChannelMapping(
        metric='q_total', channel='lightness',
        output_range=(0.35, 0.85), invert=True,
    ),
    chroma=ChannelMapping(metric='loc', channel='chroma', output_range=(0.02, 0.20)),
    signature=SemanticSignature(
        domain='convergence',
        question='How do quality signals distribute by severity?',
        reading='Red-orange = critical severity; dark = low quality; vivid = large',
    ),
)


# =============================================================================
# PRESET VIEWS REGISTRY
# =============================================================================

PRESET_VIEWS = {
    # Original 5 (general domain)
    'default': VIEW_DEFAULT,
    'architecture': VIEW_ARCHITECTURE,
    'health': VIEW_HEALTH,
    'topology': VIEW_TOPOLOGY,
    'files': VIEW_FILES,
    # Architecture domain
    'layers': VIEW_LAYERS,
    'boundaries': VIEW_BOUNDARIES,
    'scale': VIEW_SCALE,
    # Health domain
    'complexity': VIEW_COMPLEXITY,
    'quality': VIEW_QUALITY,
    'convergence': VIEW_CONVERGENCE,
    # Topology domain
    'influence': VIEW_INFLUENCE,
    'coupling': VIEW_COUPLING,
    'centrality': VIEW_CENTRALITY,
    # Files domain
    'file_size': VIEW_FILE_SIZE,
    'file_quality': VIEW_FILE_QUALITY,
    # Behavior domain
    'behavior': VIEW_BEHAVIOR,
    'intent': VIEW_INTENT,
    'roles': VIEW_ROLES,
    # Purity domain
    'purity': VIEW_PURITY,
    'purity_by_layer': VIEW_PURITY_BY_LAYER,
    'isolation': VIEW_ISOLATION,
    # Risk domain
    'risk': VIEW_RISK,
    'debt': VIEW_DEBT,
    'fragility': VIEW_FRAGILITY,
    'god_class': VIEW_GOD_CLASS,
    # Confidence domain
    'confidence': VIEW_CONFIDENCE,
    'clarity': VIEW_CLARITY,
    # Convergence domain
    'hotspots': VIEW_HOTSPOTS,
    'signals': VIEW_SIGNALS,
}


# =============================================================================
# BASE HUE TABLES
# =============================================================================

# Tier hues — matching appearance_engine's tier colors, expressed in OKLCH hue degrees.
# Ordered longest-prefix-first so 'EXT.DISCOVERED' matches before 'EXT'.
_TIER_HUE_RULES: List[Tuple[str, float]] = [
    ('EXT.DISCOVERED', 60.0),   # warm yellow — must precede 'EXT'
    ('CORE', 200.0),            # cyan / teal
    ('ARCH', 280.0),            # purple
    ('EXT', 145.0),             # green
]

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


_ATOM_FAMILY_HUES: Dict[str, float] = {
    'structural': 200.0,    # cyan
    'behavioral': 30.0,     # orange
    'connective': 145.0,    # green
    'auxiliary': 280.0,     # purple
    'meta': 330.0,          # pink
}

_BOUNDARY_HUES: Dict[str, float] = {
    'INTERNAL': 200.0,
    'BOUNDARY': 60.0,
    'EXTERNAL': 30.0,
    'BRIDGE': 145.0,
    'UNKNOWN': 0.0,
}

_BEHAVIOR_HUES: Dict[str, float] = {
    'STATELESS': 200.0,
    'STATEFUL': 30.0,
    'REACTIVE': 145.0,
    'GENERATIVE': 280.0,
    'PASSIVE': 60.0,
    'UNKNOWN': 0.0,
}

_CONVERGENCE_HUES: Dict[str, float] = {
    'critical': 25.0,       # red-orange
    'high': 60.0,           # yellow
    'moderate': 145.0,      # green
}

_LAYER_HUES: Dict[str, float] = {
    'presentation': 30.0,
    'application': 60.0,
    'domain': 145.0,
    'infrastructure': 200.0,
    'cross_cutting': 280.0,
    'test': 100.0,
}

_CATEGORY_HUES: Dict[str, float] = {
    'class': 200.0,
    'function': 145.0,
    'module': 30.0,
    'interface': 280.0,
    'enum': 60.0,
    'type': 330.0,
}


def _resolve_metric(item: dict, metric: str) -> Any:
    """Resolve a dot-notation metric path. 'rpbl.responsibility' → item['rpbl']['responsibility']."""
    if '.' not in metric:
        return item.get(metric)
    parts = metric.split('.')
    current = item
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _resolve_base_hue(node: Dict[str, Any], hue_source: str) -> float:
    """Look up the base hue for a node given the hue source axis."""
    if hue_source == 'tier':
        atom = node.get('atom', '')
        for prefix, hue in _TIER_HUE_RULES:
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
    elif hue_source == 'atom_family':
        family = node.get('atom_family', 'structural')
        return _ATOM_FAMILY_HUES.get(family, 0.0)
    elif hue_source == 'boundary':
        boundary = _resolve_metric(node, 'dimensions.D4_BOUNDARY') or node.get('D4_BOUNDARY', 'UNKNOWN')
        return _BOUNDARY_HUES.get(str(boundary), 0.0)
    elif hue_source == 'behavior':
        behavior = _resolve_metric(node, 'dimensions.D5_BEHAVIOR') or node.get('D5_BEHAVIOR', 'UNKNOWN')
        return _BEHAVIOR_HUES.get(str(behavior), 0.0)
    elif hue_source == 'convergence_severity':
        severity = node.get('convergence_severity', 'moderate')
        return _CONVERGENCE_HUES.get(severity, 145.0)
    elif hue_source == 'layer':
        layer = node.get('layer', 'domain')
        return _LAYER_HUES.get(str(layer).lower(), 0.0)
    elif hue_source == 'category':
        cat = node.get('category', 'class')
        return _CATEGORY_HUES.get(str(cat).lower(), 0.0)
    elif hue_source == 'atom':
        atom = node.get('atom', '')
        return (hash(atom) * 137.508) % 360.0
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
        val = _resolve_metric(item, metric)
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
        val = _resolve_metric(item, mapping.metric)
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
        val = _resolve_metric(item, mapping.metric)
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
            nid = cn.node_id
        elif isinstance(cn, dict):
            nid = cn.get('node_id', '')
        else:
            continue
        if nid:  # skip empty/missing node_id to avoid false matches
            lookup[nid] = cn

    # Tag matching nodes
    tagged = 0
    for node in nodes:
        node_id = node.get('id', '')
        if not node_id or node_id not in lookup:
            continue
        cn = lookup[node_id]
        if hasattr(cn, 'severity'):
            node['convergence_severity'] = cn.severity
            node['convergence_signals'] = list(getattr(cn, 'signals', []))
            node['convergence_count'] = getattr(cn, 'signal_count', 0)
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
        4. Gamut-map and write node['encoded_color'] as OKLCH tuple (L, C, H)

    Args:
        nodes: List of node dicts (mutated in place)
        view: ViewSpec defining the encoding

    Returns:
        (nodes_encoded, missing_data) where missing_data maps metric → skip count
    """
    # If the view has no L or C mappings (e.g. VIEW_DEFAULT), skip encoding.
    # This preserves appearance_engine's color_mode switch (tier/ring/file).
    has_data_channels = view.lightness is not None or view.chroma is not None
    if not has_data_channels:
        return 0, {}

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

        # Gamut-map via modulate_oklch: take base hue, overlay data-driven L and C.
        # Store as OKLCH triple — hex conversion happens at the render boundary.
        mL, mC, mH = modulate_oklch(NEUTRAL_L, NEUTRAL_C, H,
                                     l_target=L, c_target=C)
        node['encoded_color'] = (mL, mC, mH)
        encoded += 1

    return encoded, missing


def encode_edges(
    edges: List[Dict[str, Any]],
    mapping: Optional[ChannelMapping] = None,
) -> Tuple[int, int]:
    """Apply a ChannelMapping to encode edges with OKLCH colors.

    Default maps edge 'confidence' to a hue gradient (red → green).

    Args:
        edges: List of edge dicts (mutated in place)
        mapping: Optional ChannelMapping for the edge metric

    Returns:
        (edges_encoded, edges_missing_metric)
    """
    if mapping is None:
        # Default: confidence → hue gradient
        mapping = ChannelMapping(
            metric='confidence',
            channel='hue',
            output_range=(30.0, 145.0),  # red-orange → green
        )

    values = _normalize_global(edges, mapping)
    edges_missing = len(edges) - len(values)
    if not values:
        return 0, edges_missing

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
        edge['encoded_color'] = (mL, mC, mH)
        encoded += 1

    return encoded, edges_missing


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

    # 2. Encode nodes (skipped for views with no L/C mapping like VIEW_DEFAULT)
    if nodes:
        report.nodes_encoded, report.missing_data = encode_nodes(nodes, view)
        if report.nodes_encoded > 0:
            channels.append('hue')
            if view.lightness:
                channels.append('lightness')
            if view.chroma:
                channels.append('chroma')

    # 3. Encode edges (only when the view provides an explicit edge mapping)
    if edges and view.edge_mapping is not None:
        report.edges_encoded, edges_missing = encode_edges(edges, view.edge_mapping)
        if edges_missing > 0:
            report.missing_data[f'edge:{view.edge_mapping.metric}'] = edges_missing

    report.channels_used = channels
    return report


def get_view_registry() -> Dict[str, Any]:
    """Export view metadata for JS consumption. Grouped by domain."""
    registry = {}
    for name, view in PRESET_VIEWS.items():
        sig = view.signature
        registry[name] = {
            'name': name,
            'domain': sig.domain if sig else 'general',
            'question': sig.question if sig else '',
            'reading': sig.reading if sig else '',
            'hue_source': view.hue_source,
            'lightness_metric': view.lightness.metric if view.lightness else None,
            'chroma_metric': view.chroma.metric if view.chroma else None,
        }
    return registry
