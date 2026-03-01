"""
Compartment Inferrer: Auto-infer architectural compartments from pipeline signals.

Solves the zero-config problem: boundary_validator.py requires an external YAML
file with compartment declarations. This module infers compartments automatically
from signals the pipeline already computes by Stage 6.8, so boundary validation
and group cohesion analysis always run — even without --boundaries.

Design:
  5 inference strategies vote on compartment assignment per node.
  A weighted synthesis merges votes into final assignments.
  Dependency inference observes actual cross-compartment edges.

Output is structurally identical to load_boundaries() so all downstream
consumers (assign_compartments, validate_boundaries, compute_group_cohesion)
work unchanged.

Extracted into dedicated module during Feature 5 implementation (2026-03-01).
"""

from collections import Counter, defaultdict
from pathlib import PurePosixPath
from typing import Dict, List, Any, Optional, Set, Tuple

# =============================================================================
# STRATEGY WEIGHTS
# =============================================================================

STRATEGY_WEIGHTS = {
    "directory": 0.35,
    "layer": 0.25,
    "community": 0.20,
    "naming": 0.15,
    "rpbl": 0.05,
}

# Minimum nodes for a group to survive as its own compartment
MIN_COMPARTMENT_SIZE = 3

# Minimum cross-compartment edges to infer a dependency
MIN_DEP_EDGE_COUNT = 2


# =============================================================================
# PUBLIC API
# =============================================================================

def infer_compartments(
    nodes: List[Dict],
    edges: List[Dict],
    G_full: Optional[Any] = None,
    survey_result: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Auto-infer architectural compartments from pipeline signals.

    Returns same structure as load_boundaries() so downstream consumers
    (assign_compartments, validate_boundaries, compute_group_cohesion)
    work unchanged:
    {
        "compartments": {
            "compartment_name": {
                "globs": ["pattern/**"],
                "allowed_deps": ["other_compartment", ...],
            }, ...
        },
        "inference_metadata": {
            "strategy_contributions": {...},
            "confidence_per_compartment": {...},
            "total_nodes_assigned": int,
        }
    }

    Args:
        nodes: Enriched node dicts from pipeline (need file_path, dimensions, rpbl_boundary)
        edges: Edge dicts (need source, target)
        G_full: Optional NetworkX DiGraph from Stage 6.5
        survey_result: Optional survey output with identity/archetype info
    """
    if not nodes:
        return {"compartments": {}, "inference_metadata": {"total_nodes_assigned": 0}}

    # Build node ID index for fast lookup
    node_by_id = {n.get("id", n.get("name", "")): n for n in nodes}

    # Run all strategies
    strategy_results: List[Tuple[Dict[str, str], float, str]] = []

    # Strategy 1: Directory Clustering (weight 0.35)
    dir_assignments = _strategy_directory_clustering(nodes)
    if dir_assignments:
        strategy_results.append((dir_assignments, STRATEGY_WEIGHTS["directory"], "directory"))

    # Strategy 2: D2_LAYER Agreement (weight 0.25)
    layer_assignments = _strategy_layer_agreement(nodes, dir_assignments)
    if layer_assignments:
        strategy_results.append((layer_assignments, STRATEGY_WEIGHTS["layer"], "layer"))

    # Strategy 3: Community Detection (weight 0.20)
    community_assignments = _strategy_community_detection(nodes, G_full)
    if community_assignments:
        strategy_results.append((community_assignments, STRATEGY_WEIGHTS["community"], "community"))

    # Strategy 4: Naming Convention (weight 0.15)
    naming_assignments = _strategy_naming_convention(nodes, survey_result)
    if naming_assignments:
        strategy_results.append((naming_assignments, STRATEGY_WEIGHTS["naming"], "naming"))

    # Strategy 5: RPBL Boundary (weight 0.05) — amplifier only
    rpbl_assignments = _strategy_rpbl_boundary(nodes, dir_assignments)
    if rpbl_assignments:
        strategy_results.append((rpbl_assignments, STRATEGY_WEIGHTS["rpbl"], "rpbl"))

    # Synthesize via weighted voting
    final_assignments, confidence_map = _synthesize_votes(
        [(a, w) for a, w, _ in strategy_results],
        nodes,
    )

    if not final_assignments:
        return {"compartments": {}, "inference_metadata": {"total_nodes_assigned": 0}}

    # Infer allowed_deps from observed edges
    allowed_deps = _infer_allowed_deps(final_assignments, edges)

    # Build globs from actual file paths per compartment
    compartment_globs = _build_compartment_globs(final_assignments, node_by_id)

    # Assemble output in load_boundaries()-compatible format
    compartments: Dict[str, Dict[str, Any]] = {}
    for comp_name in sorted(set(final_assignments.values())):
        compartments[comp_name] = {
            "globs": compartment_globs.get(comp_name, []),
            "allowed_deps": sorted(allowed_deps.get(comp_name, [])),
        }

    # Per-compartment confidence (average confidence of member nodes)
    confidence_per_comp: Dict[str, float] = {}
    for comp_name in compartments:
        member_confidences = [
            confidence_map[nid]
            for nid, c in final_assignments.items()
            if c == comp_name and nid in confidence_map
        ]
        if member_confidences:
            confidence_per_comp[comp_name] = round(
                sum(member_confidences) / len(member_confidences), 3
            )

    # Strategy contribution tracking
    strategy_contributions = {
        name: len(assignments)
        for assignments, _, name in strategy_results
    }

    return {
        "compartments": compartments,
        "inference_metadata": {
            "strategy_contributions": strategy_contributions,
            "confidence_per_compartment": confidence_per_comp,
            "total_nodes_assigned": len(final_assignments),
            "source": "inferred",
        },
    }


# =============================================================================
# STRATEGY 1: DIRECTORY CLUSTERING
# =============================================================================

def _strategy_directory_clustering(nodes: List[Dict]) -> Dict[str, str]:
    """Group nodes by top-level directory path.

    Logic:
    - Extract top-level project directory from file_path
    - e.g., 'src/api/routes/users.py' -> 'src/api'
    - Merge tiny groups (<MIN_COMPARTMENT_SIZE nodes) into nearest neighbor
    """
    # Group nodes by directory prefix
    dir_groups: Dict[str, List[str]] = defaultdict(list)
    node_dirs: Dict[str, str] = {}

    for node in nodes:
        file_path = node.get("file_path", "")
        node_id = node.get("id", node.get("name", ""))

        if not file_path or not node_id:
            continue

        # Skip synthetic nodes (codome boundaries, etc.)
        if file_path.startswith("__"):
            continue

        prefix = _extract_directory_prefix(file_path)
        dir_groups[prefix].append(node_id)
        node_dirs[node_id] = prefix

    if not dir_groups:
        return {}

    # Merge tiny groups into nearest neighbor
    _merge_tiny_groups(dir_groups, min_size=MIN_COMPARTMENT_SIZE)

    # Convert to node_id -> compartment_name
    assignments: Dict[str, str] = {}
    # Rebuild reverse map after merges
    for comp_name, member_ids in dir_groups.items():
        label = _sanitize_compartment_name(comp_name)
        for nid in member_ids:
            assignments[nid] = label

    return assignments


def _extract_directory_prefix(file_path: str) -> str:
    """Extract a meaningful directory prefix from a file path.

    Heuristic: use the first two path components if they exist,
    otherwise the first component. For root-level files, use '_root'.

    Examples:
        'src/api/routes/users.py'   -> 'src/api'
        'src/core/engine.py'        -> 'src/core'
        'tests/test_api.py'         -> 'tests'
        'setup.py'                  -> '_root'
    """
    parts = PurePosixPath(file_path).parts
    if len(parts) <= 1:
        return "_root"
    if len(parts) == 2:
        return parts[0]
    # Use first two meaningful components
    return f"{parts[0]}/{parts[1]}"


def _merge_tiny_groups(
    groups: Dict[str, List[str]],
    min_size: int = MIN_COMPARTMENT_SIZE,
) -> None:
    """Merge groups smaller than min_size into the largest group (in-place).

    Simple heuristic: tiny groups get absorbed by the biggest group.
    This prevents single-file compartments from polluting the output.
    """
    if not groups:
        return

    # Find largest group
    largest_name = max(groups, key=lambda k: len(groups[k]))

    tiny_keys = [k for k, v in groups.items() if len(v) < min_size and k != largest_name]
    for key in tiny_keys:
        groups[largest_name].extend(groups[key])
        del groups[key]


def _sanitize_compartment_name(raw: str) -> str:
    """Convert a directory prefix to a clean compartment name.

    'src/api' -> 'api'
    'src/core' -> 'core'
    'tests' -> 'tests'
    '_root' -> 'root'
    """
    # Remove common prefixes that don't add info
    for strip_prefix in ("src/", "lib/", "app/", "pkg/"):
        if raw.startswith(strip_prefix):
            raw = raw[len(strip_prefix):]

    # Clean up
    name = raw.replace("/", "_").replace("-", "_").strip("_")
    return name or "root"


# =============================================================================
# STRATEGY 2: D2_LAYER AGREEMENT
# =============================================================================

def _strategy_layer_agreement(
    nodes: List[Dict],
    dir_assignments: Dict[str, str],
) -> Dict[str, str]:
    """Within each directory group, sub-cluster by D2_LAYER.

    If a directory contains mixed layers, split into sub-compartments.
    Pure directories stay as-is.
    """
    if not dir_assignments:
        return {}

    # Group nodes by their directory compartment
    comp_layers: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    for node in nodes:
        node_id = node.get("id", node.get("name", ""))
        if node_id not in dir_assignments:
            continue

        dir_comp = dir_assignments[node_id]
        layer = node.get("dimensions", {}).get("D2_LAYER", "")
        if not layer or layer in ("Unknown", ""):
            layer = "general"

        comp_layers[dir_comp][layer.lower()].append(node_id)

    # Decide: split mixed directories, keep pure ones
    assignments: Dict[str, str] = {}
    for dir_comp, layer_groups in comp_layers.items():
        if len(layer_groups) <= 1:
            # Pure directory — use directory name as-is
            for layer, nids in layer_groups.items():
                for nid in nids:
                    assignments[nid] = dir_comp
        else:
            # Mixed — check if dominant layer covers >80%
            total = sum(len(nids) for nids in layer_groups.values())
            dominant_layer = max(layer_groups, key=lambda k: len(layer_groups[k]))
            dominant_count = len(layer_groups[dominant_layer])

            if dominant_count / total >= 0.8:
                # One layer dominates — don't split
                for layer, nids in layer_groups.items():
                    for nid in nids:
                        assignments[nid] = dir_comp
            else:
                # Genuinely mixed — split into sub-compartments
                for layer, nids in layer_groups.items():
                    sub_comp = f"{dir_comp}_{layer}"
                    for nid in nids:
                        assignments[nid] = sub_comp

    return assignments


# =============================================================================
# STRATEGY 3: COMMUNITY DETECTION
# =============================================================================

def _strategy_community_detection(
    nodes: List[Dict],
    G_full: Optional[Any],
) -> Dict[str, str]:
    """Use Louvain community detection from graph_metrics.detect_clusters().

    Each community becomes a candidate compartment, labeled by the
    dominant directory of its member nodes.
    """
    if G_full is None:
        return {}

    try:
        from src.core.graph_metrics import detect_clusters
    except ImportError:
        return {}

    clusters = detect_clusters(G_full)
    if not clusters:
        return {}

    # Build node -> file_path lookup
    node_files: Dict[str, str] = {}
    for node in nodes:
        nid = node.get("id", node.get("name", ""))
        fp = node.get("file_path", "")
        if nid and fp:
            node_files[nid] = fp

    assignments: Dict[str, str] = {}
    for cluster in clusters:
        if not cluster:
            continue

        # Label cluster by dominant directory
        dir_counts: Counter = Counter()
        for nid in cluster:
            fp = node_files.get(nid, "")
            if fp and not fp.startswith("__"):
                prefix = _extract_directory_prefix(fp)
                label = _sanitize_compartment_name(prefix)
                dir_counts[label] += 1

        if dir_counts:
            cluster_label = dir_counts.most_common(1)[0][0]
        else:
            cluster_label = "cluster"

        for nid in cluster:
            assignments[nid] = cluster_label

    return assignments


# =============================================================================
# STRATEGY 4: NAMING CONVENTION DETECTION
# =============================================================================

# Framework-specific naming patterns: pattern -> role label
_NAMING_PATTERNS = {
    # Python patterns
    "views": "interface",
    "controllers": "interface",
    "handlers": "interface",
    "routes": "interface",
    "endpoints": "interface",
    "api": "interface",
    "services": "application",
    "use_cases": "application",
    "usecases": "application",
    "models": "domain",
    "entities": "domain",
    "schemas": "domain",
    "serializers": "boundary",
    "adapters": "boundary",
    "repositories": "infrastructure",
    "persistence": "infrastructure",
    "database": "infrastructure",
    "db": "infrastructure",
    "migrations": "infrastructure",
    "utils": "utility",
    "utilities": "utility",
    "helpers": "utility",
    "common": "utility",
    "shared": "utility",
    "tests": "test",
    "test": "test",
    "spec": "test",
    "specs": "test",
    "__tests__": "test",
    "config": "config",
    "settings": "config",
    "configuration": "config",
}


def _strategy_naming_convention(
    nodes: List[Dict],
    survey_result: Optional[Dict],
) -> Dict[str, str]:
    """Detect framework-specific naming patterns in file paths.

    Matches directory names and file name suffixes against known patterns.
    """
    assignments: Dict[str, str] = {}

    for node in nodes:
        node_id = node.get("id", node.get("name", ""))
        file_path = node.get("file_path", "")

        if not file_path or not node_id:
            continue
        if file_path.startswith("__"):
            continue

        label = _match_naming_pattern(file_path)
        if label:
            assignments[node_id] = label

    return assignments


def _match_naming_pattern(file_path: str) -> Optional[str]:
    """Match a file path against known naming patterns.

    Checks both directory names and file name suffixes.
    """
    parts = PurePosixPath(file_path).parts
    stem = PurePosixPath(file_path).stem.lower()

    # Check directory names
    for part in parts[:-1]:  # exclude filename
        part_lower = part.lower()
        if part_lower in _NAMING_PATTERNS:
            return _NAMING_PATTERNS[part_lower]

    # Check file name suffixes: e.g., 'user_controller.py' -> 'controller'
    for pattern, label in _NAMING_PATTERNS.items():
        if stem.endswith(f"_{pattern}") or stem.endswith(f"_{pattern.rstrip('s')}"):
            return label

    return None


# =============================================================================
# STRATEGY 5: RPBL BOUNDARY AMPLIFICATION
# =============================================================================

def _strategy_rpbl_boundary(
    nodes: List[Dict],
    dir_assignments: Dict[str, str],
) -> Dict[str, str]:
    """Use RPBL boundary scores as a signal amplifier.

    High boundary scores (>0.7) indicate architectural seams.
    This strategy reinforces directory assignments for nodes with
    clear boundary characteristics — it doesn't reassign.
    """
    if not dir_assignments:
        return {}

    assignments: Dict[str, str] = {}

    for node in nodes:
        node_id = node.get("id", node.get("name", ""))
        if not node_id or node_id not in dir_assignments:
            continue

        rpbl = node.get("rpbl_boundary", 0.0)
        if isinstance(rpbl, (int, float)) and rpbl > 0.7:
            # High boundary score — reinforce existing assignment
            assignments[node_id] = dir_assignments[node_id]

    return assignments


# =============================================================================
# SYNTHESIS: WEIGHTED VOTING
# =============================================================================

def _synthesize_votes(
    strategy_results: List[Tuple[Dict[str, str], float]],
    nodes: List[Dict],
) -> Tuple[Dict[str, str], Dict[str, float]]:
    """Merge strategy proposals via weighted voting.

    For each node, collect votes from all strategies.
    Final assignment = label with highest cumulative weight.
    Confidence = winning_weight / total_weight_cast.

    Returns:
        (final_assignments, confidence_map)
    """
    if not strategy_results:
        return {}, {}

    # Collect all node IDs that got at least one vote
    all_node_ids: Set[str] = set()
    for assignments, _ in strategy_results:
        all_node_ids.update(assignments.keys())

    final_assignments: Dict[str, str] = {}
    confidence_map: Dict[str, float] = {}

    for node_id in all_node_ids:
        # Tally votes: label -> cumulative weight
        votes: Dict[str, float] = defaultdict(float)
        total_weight = 0.0

        for assignments, weight in strategy_results:
            if node_id in assignments:
                label = assignments[node_id]
                votes[label] += weight
                total_weight += weight

        if not votes:
            continue

        # Winner = highest cumulative weight
        winner = max(votes, key=lambda k: votes[k])
        final_assignments[node_id] = winner
        confidence_map[node_id] = round(votes[winner] / total_weight, 3) if total_weight > 0 else 0.0

    return final_assignments, confidence_map


# =============================================================================
# DEPENDENCY INFERENCE
# =============================================================================

def _infer_allowed_deps(
    assignments: Dict[str, str],
    edges: List[Dict],
) -> Dict[str, List[str]]:
    """Observe actual cross-compartment edges, declare them as allowed_deps.

    If >=MIN_DEP_EDGE_COUNT edges go from compartment A to compartment B,
    add B to A's allowed_deps.

    This describes what the code ACTUALLY does, not what someone wishes it did.
    """
    # Count cross-compartment edges: (source_comp, target_comp) -> count
    cross_counts: Dict[Tuple[str, str], int] = defaultdict(int)

    for edge in edges:
        source_id = edge.get("source", "")
        target_id = edge.get("target", "")

        source_comp = assignments.get(source_id)
        target_comp = assignments.get(target_id)

        if source_comp and target_comp and source_comp != target_comp:
            cross_counts[(source_comp, target_comp)] += 1

    # Build allowed_deps with threshold
    all_comps = set(assignments.values())
    allowed: Dict[str, List[str]] = {comp: [] for comp in all_comps}

    for (src_comp, tgt_comp), count in cross_counts.items():
        if count >= MIN_DEP_EDGE_COUNT:
            if tgt_comp not in allowed.get(src_comp, []):
                allowed.setdefault(src_comp, []).append(tgt_comp)

    return allowed


# =============================================================================
# GLOB GENERATION
# =============================================================================

def _build_compartment_globs(
    assignments: Dict[str, str],
    node_by_id: Dict[str, Dict],
) -> Dict[str, List[str]]:
    """Build glob patterns for each compartment from actual file paths.

    Groups files by compartment, finds common directory prefixes,
    generates glob patterns that would match those files.
    """
    # Collect file paths per compartment
    comp_files: Dict[str, Set[str]] = defaultdict(set)
    for node_id, comp_name in assignments.items():
        node = node_by_id.get(node_id, {})
        fp = node.get("file_path", "")
        if fp and not fp.startswith("__"):
            comp_files[comp_name].add(fp)

    globs: Dict[str, List[str]] = {}
    for comp_name, files in comp_files.items():
        # Find common directory prefixes
        dir_prefixes: Counter = Counter()
        for fp in files:
            prefix = _extract_directory_prefix(fp)
            dir_prefixes[prefix] += 1

        # Generate globs from most common prefixes
        patterns = []
        for prefix, _ in dir_prefixes.most_common():
            pattern = f"{prefix}/**"
            # Avoid duplicate/redundant patterns
            if pattern not in patterns:
                patterns.append(pattern)

        globs[comp_name] = patterns if patterns else [f"{comp_name}/**"]

    return globs
