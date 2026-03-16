"""
Tier -1: Atlas — Instant knowledge from the Ecosystem Atlas.

Before any LLM call, check if the query can be answered from ATLAS.yaml.
This is the cheapest possible tier: a YAML file read + string matching.
Zero API cost, <50ms latency.

If the atlas answers the query:
  → Return entity.agent.explanation with atlas citations
  → Skip all other tiers

If the atlas partially matches:
  → Scope the downstream tier to the matched component's source files
  → Pass atlas context as system prompt enrichment

If no atlas match:
  → Fall through to normal ACI routing (RAG → Long Context → etc.)

Standard Model Classification:
  D1: SVC.FNC.S (Service Function, Singleton)
  D2: Application (tier execution)
  D3: Provider (provides atlas knowledge)
  D4: Internal (reads local YAML only)
  D6: Pure (deterministic lookup)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None


# Atlas location relative to project root
ATLAS_PATHS = [
    "atlas/ATLAS.yaml",
    "../atlas/ATLAS.yaml",
]


def _load_atlas(project_root: str) -> Optional[Dict]:
    """Load ATLAS.yaml from the project root."""
    if yaml is None:
        return None
    for rel in ATLAS_PATHS:
        path = Path(project_root) / rel
        if path.exists():
            try:
                return yaml.safe_load(path.read_text())
            except Exception:
                continue
    return None


def _all_entities(atlas: Dict) -> List[Dict]:
    """Flatten all entities from all sections."""
    entities = []
    for section in ("components", "agents", "connections", "resources", "externals"):
        entities.extend(atlas.get(section, []))
    return entities


def _match_score(query: str, entity: Dict) -> float:
    """Score how well a query matches an entity. Higher = better match."""
    query_lower = query.lower()
    score = 0.0

    # Entities WITH agent.explanation are worth more (they can answer questions)
    has_explanation = bool(entity.get("agent", {}).get("explanation"))

    # Name match (strongest signal)
    name = (entity.get("name") or "").lower()
    display = (entity.get("display_name") or "").lower()
    if name and name in query_lower:
        score += 10.0 if has_explanation else 3.0
    elif name and name.replace("-", " ") in query_lower:
        score += 10.0 if has_explanation else 3.0
    if display and display in query_lower:
        score += 8.0 if has_explanation else 2.0
    elif display and display.split(" (")[0].lower() in query_lower:
        score += 8.0 if has_explanation else 2.0

    # Alias match
    for alias in entity.get("aliases", []):
        if alias.lower() in query_lower:
            score += 7.0
            break

    # ID match (exact)
    eid = (entity.get("id") or "").upper()
    if eid and eid in query.upper():
        score += 15.0

    # Connection target matching — "what connects to X?" should find connections TO X
    target = (entity.get("target") or "").lower()
    source = (entity.get("source") or "").lower()
    resolved_target = entity.get("_resolved_target_name", "")
    if target:
        # Extract the provider name from "external:EXT-001" style refs
        target_name = target.split(":")[-1].lower().replace("-", " ")
        if target_name in query_lower:
            score += 12.0 if has_explanation else 5.0
        # Also check resolved name (EXT-001 → "cerebras")
        if resolved_target and resolved_target in query_lower:
            score += 12.0 if has_explanation else 5.0
    if source:
        source_name = source.split(":")[-1].lower().replace("-", " ")
        if source_name in query_lower:
            score += 5.0

    # Purpose keyword overlap
    purpose = (entity.get("purpose") or "").lower()
    query_words = set(re.findall(r'\w+', query_lower))
    purpose_words = set(re.findall(r'\w+', purpose))
    overlap = query_words & purpose_words - {"the", "a", "an", "is", "of", "to", "and", "in", "for", "what", "how", "does"}
    if overlap:
        score += len(overlap) * 1.5

    # Tag match
    for tag in entity.get("tags", []):
        tag_parts = tag.lower().replace(":", " ").split()
        if any(tp in query_lower for tp in tag_parts):
            score += 2.0

    return score


def _build_ext_name_map(atlas: Dict) -> Dict[str, str]:
    """Map EXT-xxx IDs to provider names for cross-referencing."""
    mapping = {}
    for ext in atlas.get("externals", []):
        eid = ext.get("id", "")
        name = ext.get("name", "")
        if eid and name:
            mapping[eid.lower()] = name.lower()
            mapping[f"external:{eid}".lower()] = name.lower()
    return mapping


def atlas_lookup(
    query: str,
    project_root: str,
    threshold: float = 5.0,
    max_results: int = 5,
) -> Optional[Dict[str, Any]]:
    """Look up a query against ATLAS.yaml.

    Returns:
        None if no match above threshold.
        Dict with:
            matched: list of (entity, score) tuples
            answer: pre-authored explanation from best match
            context: atlas metadata for downstream tier enrichment
            source_files: list of file paths from matched components (for context scoping)
    """
    atlas = _load_atlas(project_root)
    if not atlas:
        return None

    entities = _all_entities(atlas)
    ext_names = _build_ext_name_map(atlas)

    # For connections, resolve target EXT-xxx to provider name for matching
    for e in entities:
        target = (e.get("target") or "").lower()
        if target in ext_names:
            e["_resolved_target_name"] = ext_names[target]

    scored = [(e, _match_score(query, e)) for e in entities]
    scored = [(e, s) for e, s in scored if s >= threshold]
    scored.sort(key=lambda x: -x[1])

    if not scored:
        return None

    best_entity, best_score = scored[0]
    top_matches = scored[:max_results]

    # Extract pre-authored explanation
    agent_block = best_entity.get("agent", {})
    explanation = agent_block.get("explanation", best_entity.get("purpose", ""))

    # Extract source files for context scoping
    source_files = []
    for entity, _ in top_matches:
        invoke = entity.get("invoke", {})
        if isinstance(invoke, dict):
            method = invoke.get("method", "")
            # Extract file paths from invoke methods
            for token in method.split():
                if token.endswith(".py") or "/" in token:
                    source_files.append(token)

    # Build blast radius context
    blast_radius = []
    for entity, _ in top_matches:
        impact = entity.get("impact", {})
        if isinstance(impact, dict):
            blast_radius.extend(impact.get("blast_radius", []))

    # Build connection context
    connections = []
    for entity, _ in top_matches:
        conns = entity.get("requires_connections", [])
        connections.extend(conns)

    return {
        "matched": [(e.get("id", "?"), e.get("name", "?"), s) for e, s in top_matches],
        "best_match": {
            "id": best_entity.get("id"),
            "name": best_entity.get("name"),
            "kind": best_entity.get("kind"),
            "stage": best_entity.get("stage"),
            "status": best_entity.get("status"),
            "score": best_score,
        },
        "answer": explanation,
        "purpose": best_entity.get("purpose", ""),
        "context": {
            "connections": connections,
            "blast_radius": blast_radius,
            "feeds_into": best_entity.get("feeds_into", []),
            "fed_by": best_entity.get("fed_by", []),
        },
        "source_files": source_files,
        "health": best_entity.get("health", {}),
        "recovery_action": best_entity.get("impact", {}).get("recovery_action", ""),
    }


def atlas_context_prompt(lookup_result: Dict) -> str:
    """Build a system prompt fragment from atlas lookup results.

    This gets injected into the LLM prompt when a downstream tier
    handles the query, giving it atlas awareness.
    """
    if not lookup_result:
        return ""

    best = lookup_result["best_match"]
    lines = [
        f"[Atlas Context] Query matched {best['kind']} {best['id']} ({best['name']}), stage {best['stage']}.",
        f"Purpose: {lookup_result['purpose']}",
    ]

    if lookup_result["context"]["connections"]:
        lines.append(f"Connections: {', '.join(lookup_result['context']['connections'])}")
    if lookup_result["context"]["blast_radius"]:
        lines.append(f"Blast radius: {', '.join(lookup_result['context']['blast_radius'])}")
    if lookup_result["health"]:
        status = lookup_result["health"].get("status", "unknown")
        lines.append(f"Health: {status}")
    if lookup_result["recovery_action"]:
        lines.append(f"Recovery: {lookup_result['recovery_action']}")

    return "\n".join(lines)


# Quick test
if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) or "what connects to Cerebras?"
    root = str(Path(__file__).resolve().parents[5])  # wave/tools/ai/analyze/tiers → project root
    result = atlas_lookup(query, root)
    if result:
        print(f"Match: {result['best_match']['id']} ({result['best_match']['name']}) score={result['best_match']['score']}")
        print(f"Answer: {result['answer']}")
        print(f"Source files: {result['source_files']}")
        print(f"Context: {atlas_context_prompt(result)}")
    else:
        print("No atlas match.")
