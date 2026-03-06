#!/usr/bin/env python3
"""
API DRIFT ANALYZER - Backend/frontend API contract validation.

Compares backend API endpoint definitions against frontend API consumers to
detect mismatches (drift) in the contract between the two layers.

Part of the Collider analysis pipeline. Pure stdlib — no external dependencies.

Drift types detected:
    orphaned_endpoint  — Backend defines a route no frontend code calls
    missing_endpoint   — Frontend calls a URL the backend never defines
    method_mismatch    — Same path, different HTTP method
    path_drift         — Semantically similar paths with version/naming divergence
    shadow_endpoint    — Backend route present but unreachable (dead code flag)

Usage:
    from src.core.api_route_extractor import EndpointCatalog
    from src.core.frontend_api_detector import APIConsumerReport
    from src.core.api_drift_analyzer import analyze_api_drift

    report = analyze_api_drift(endpoint_catalog, consumer_report)
    print(report.summary())
"""

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# TYPE STUBS
# These mirror the real dataclasses from the sibling modules. When those
# modules exist the real imports below override these stubs, so all runtime
# behaviour is correct regardless of which modules are already present.
# ---------------------------------------------------------------------------

@dataclass
class _APIEndpointStub:
    route_path: str
    http_method: str
    handler_name: str = ""
    file_path: str = ""
    is_active: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class _EndpointCatalogStub:
    endpoints: List[_APIEndpointStub] = field(default_factory=list)
    file_path: str = ""


@dataclass
class _APICallSiteStub:
    url_pattern: str
    http_method: str
    caller_name: str = ""
    file_path: str = ""
    line: int = 0


@dataclass
class _APIConsumerReportStub:
    call_sites: List[_APICallSiteStub] = field(default_factory=list)
    file_path: str = ""


# Real imports — graceful fallback to stubs when modules are absent
try:
    from src.core.api_route_extractor import APIEndpoint, EndpointCatalog  # type: ignore
except ImportError:
    try:
        from api_route_extractor import APIEndpoint, EndpointCatalog  # type: ignore
    except ImportError:
        APIEndpoint = _APIEndpointStub          # type: ignore[misc,assignment]
        EndpointCatalog = _EndpointCatalogStub  # type: ignore[misc,assignment]

try:
    from src.core.frontend_api_detector import APICallSite, APIConsumerReport  # type: ignore
except ImportError:
    try:
        from frontend_api_detector import APICallSite, APIConsumerReport  # type: ignore
    except ImportError:
        APICallSite = _APICallSiteStub              # type: ignore[misc,assignment]
        APIConsumerReport = _APIConsumerReportStub  # type: ignore[misc,assignment]


# ---------------------------------------------------------------------------
# PATH NORMALIZATION
# ---------------------------------------------------------------------------

# Matches path parameter tokens in common framework styles:
#   Flask/FastAPI  → {id}  {user_id}
#   Express.js     → :id   :userId
#   Django         → <pk>  <int:pk>
_PARAM_RE = re.compile(
    r"\{[^}]+\}"       # {param}
    r"|:[a-zA-Z_][a-zA-Z0-9_]*"  # :param
    r"|<(?:[a-zA-Z_][a-zA-Z0-9_]*:)?[a-zA-Z_][a-zA-Z0-9_]*>"  # <type:param>
)

# Strip query strings and fragments before any further processing
_QUERY_RE = re.compile(r"[?#].*$")


def _normalize_path(raw: str) -> str:
    """Return a canonical form of *raw* for comparison purposes.

    Transformations applied in order:
    1. Strip query parameters and fragments
    2. Strip trailing slash (except bare root '/')
    3. Lowercase
    4. Replace all path-parameter tokens with the literal '{param}'
    """
    path = _QUERY_RE.sub("", raw).strip()
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    path = path.lower()
    path = _PARAM_RE.sub("{param}", path)
    return path


def _path_segments(normalized: str) -> List[str]:
    """Split a normalized path into non-empty segments."""
    return [s for s in normalized.split("/") if s]


# ---------------------------------------------------------------------------
# SIMILARITY HELPERS
# ---------------------------------------------------------------------------

def _segment_similarity(a: str, b: str) -> float:
    """Compute a [0.0, 1.0] similarity between two normalized paths.

    Uses a segment-aware approach:
    - Exact segment matches score 1.0 per segment
    - Difflib ratio for the full string as a fallback tiebreaker
    """
    segs_a = _path_segments(a)
    segs_b = _path_segments(b)
    if not segs_a and not segs_b:
        return 1.0
    if not segs_a or not segs_b:
        return 0.0

    # Align from the right (tail of path) — API versioning lives at the left
    matched = sum(sa == sb for sa, sb in zip(reversed(segs_a), reversed(segs_b)))
    max_len = max(len(segs_a), len(segs_b))
    segment_score = matched / max_len

    # Blend with character-level similarity for robustness
    char_score = SequenceMatcher(None, a, b).ratio()
    return 0.7 * segment_score + 0.3 * char_score


# Threshold below which two paths are not considered "similar enough" to be
# flagged as path_drift (as opposed to truly unrelated routes).
_DRIFT_SIMILARITY_THRESHOLD = 0.40


# ---------------------------------------------------------------------------
# EXTERNAL / INFRASTRUCTURE EXCLUSION
# ---------------------------------------------------------------------------

# Patterns matching paths that should be excluded from drift analysis.
# These represent external service calls, infrastructure endpoints, and
# browser-generated requests that are NOT part of the internal API contract.
_EXTERNAL_EXCLUSION_PATTERNS: List[re.Pattern] = [
    # Absolute URLs — calls to external services (ElevenLabs, OpenAI, etc.)
    re.compile(r"^https?://", re.IGNORECASE),
    # WebSocket connections to external services
    re.compile(r"^wss?://", re.IGNORECASE),
    # Health and readiness probes (consumed by infra, not frontend)
    re.compile(r"/health(?:z|check)?$", re.IGNORECASE),
    re.compile(r"/ready$", re.IGNORECASE),
    # Prometheus-style metrics
    re.compile(r"/metrics$", re.IGNORECASE),
    # Static file serving
    re.compile(r"^/static/"),
    # Favicon and manifest (browser-generated, not app API)
    re.compile(r"^/favicon", re.IGNORECASE),
    re.compile(r"^/manifest\.json$", re.IGNORECASE),
    # API documentation endpoints (FastAPI/Swagger auto-generated)
    re.compile(r"^/docs$|^/redoc$|^/openapi", re.IGNORECASE),
]


def _is_excluded_path(raw_path: str, extra_patterns: Optional[List[re.Pattern]] = None) -> bool:
    """Return True if *raw_path* matches an exclusion pattern.

    Checks built-in ``_EXTERNAL_EXCLUSION_PATTERNS`` first, then any
    project-specific *extra_patterns* supplied by the caller.
    """
    for pat in _EXTERNAL_EXCLUSION_PATTERNS:
        if pat.search(raw_path):
            return True
    if extra_patterns:
        for pat in extra_patterns:
            if pat.search(raw_path):
                return True
    return False


# ---------------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class DriftItem:
    """A single drift finding produced by analyze_api_drift."""

    drift_type: str
    """One of: orphaned_endpoint, missing_endpoint, method_mismatch,
    path_drift, shadow_endpoint."""

    severity: str
    """One of: critical, high, medium, low."""

    description: str
    """Human-readable explanation of the drift."""

    backend_path: Optional[str]
    """Route path on the backend side; None when the backend has no entry."""

    frontend_path: Optional[str]
    """URL pattern on the frontend side; None when the frontend has no entry."""

    backend_method: Optional[str]
    frontend_method: Optional[str]

    backend_file: Optional[str]
    """Source file where the backend route is defined."""

    frontend_file: Optional[str]
    """Source file where the frontend call originates."""

    confidence: float = 1.0
    """How confident the matcher is that this finding is accurate (0–1)."""

    suggestion: str = ""
    """Recommended fix."""

    def to_dict(self) -> Dict:
        return {
            "drift_type": self.drift_type,
            "severity": self.severity,
            "description": self.description,
            "backend_path": self.backend_path,
            "frontend_path": self.frontend_path,
            "backend_method": self.backend_method,
            "frontend_method": self.frontend_method,
            "backend_file": self.backend_file,
            "frontend_file": self.frontend_file,
            "confidence": round(self.confidence, 3),
            "suggestion": self.suggestion,
        }


@dataclass
class APIDriftReport:
    """Complete API drift analysis between one backend catalog and one frontend
    consumer report."""

    drift_items: List[DriftItem] = field(default_factory=list)
    matched_endpoints: int = 0
    total_backend_routes: int = 0
    total_frontend_calls: int = 0
    drift_score: float = 0.0
    coverage: float = 0.0

    orphaned_count: int = 0
    missing_count: int = 0
    mismatch_count: int = 0
    excluded_backend: int = 0
    excluded_frontend: int = 0

    # Collider graph edges generated from matched endpoints
    _edges: List[Dict] = field(default_factory=list, repr=False)

    def to_dict(self) -> Dict:
        return {
            "matched_endpoints": self.matched_endpoints,
            "total_backend_routes": self.total_backend_routes,
            "total_frontend_calls": self.total_frontend_calls,
            "drift_score": round(self.drift_score, 4),
            "coverage": round(self.coverage, 4),
            "orphaned_count": self.orphaned_count,
            "missing_count": self.missing_count,
            "mismatch_count": self.mismatch_count,
            "excluded_backend": self.excluded_backend,
            "excluded_frontend": self.excluded_frontend,
            "drift_items": [d.to_dict() for d in self.drift_items],
        }

    def summary(self) -> Dict:
        """Return a compact summary dict suitable for pipeline logging."""
        severity_counts: Dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for item in self.drift_items:
            severity_counts[item.severity] = severity_counts.get(item.severity, 0) + 1
        return {
            "drift_score": round(self.drift_score, 4),
            "coverage": round(self.coverage, 4),
            "matched_endpoints": self.matched_endpoints,
            "total_drift_items": len(self.drift_items),
            "by_severity": severity_counts,
            "by_type": {
                "orphaned_endpoint": self.orphaned_count,
                "missing_endpoint": self.missing_count,
                "method_mismatch": self.mismatch_count,
                "path_drift": sum(1 for d in self.drift_items if d.drift_type == "path_drift"),
                "shadow_endpoint": sum(1 for d in self.drift_items if d.drift_type == "shadow_endpoint"),
            },
            "excluded": {
                "backend": self.excluded_backend,
                "frontend": self.excluded_frontend,
                "total": self.excluded_backend + self.excluded_frontend,
            },
        }

    def get_edges(self) -> List[Dict]:
        """Return Collider-compatible edge dicts for matched and drifted routes.

        Edge types emitted:
            api_call  — frontend caller successfully matches a backend handler
            api_drift — a drift item links the two sides (confidence < 1.0)
        """
        return list(self._edges)


# ---------------------------------------------------------------------------
# CORE ANALYSIS
# ---------------------------------------------------------------------------

def analyze_api_drift(
    endpoint_catalog,   # EndpointCatalog from api_route_extractor
    consumer_report,    # APIConsumerReport from frontend_api_detector
    *,
    exclusion_patterns: Optional[List[re.Pattern]] = None,
) -> APIDriftReport:
    """Compare backend endpoints against frontend API calls and return drift report.

    Matching strategy (applied in order):
        0. Pre-filter: remove endpoints/calls matching exclusion patterns
        1. Normalize both sides: strip trailing slashes, lowercase, parameterize
        2. Exact match: normalized path + HTTP method (case-insensitive)
        3. Fuzzy match on path: path matches but method differs → method_mismatch
        4. Similarity search among unmatched pairs → path_drift when score >=
           _DRIFT_SIMILARITY_THRESHOLD
        5. Inactive backend routes in unmatched set → shadow_endpoint
        6. Remaining unmatched backend routes → orphaned_endpoint
        7. Remaining unmatched frontend calls → missing_endpoint

    Severity rules:
        missing_endpoint  → critical  (frontend will receive HTTP 404)
        method_mismatch   → high      (frontend will receive HTTP 405)
        path_drift        → high      (likely a version mismatch)
        orphaned_endpoint → medium    (dead API surface, maintenance burden)
        shadow_endpoint   → low       (informational; route unreachable)

    Args:
        exclusion_patterns: Optional list of compiled regex patterns for
            project-specific paths to exclude from analysis (in addition to
            the built-in ``_EXTERNAL_EXCLUSION_PATTERNS``).
    """
    raw_endpoints = getattr(endpoint_catalog, "endpoints", []) or []
    raw_call_sites = getattr(consumer_report, "call_sites", []) or []

    # ------------------------------------------------------------------ #
    # Pre-filter: exclude external / infrastructure paths
    # ------------------------------------------------------------------ #
    endpoints = []
    excluded_be = 0
    for ep in raw_endpoints:
        raw = getattr(ep, "route_path", "")
        if _is_excluded_path(raw, exclusion_patterns):
            excluded_be += 1
        else:
            endpoints.append(ep)

    call_sites = []
    excluded_fe = 0
    for cs in raw_call_sites:
        raw = getattr(cs, "url_pattern", "")
        if _is_excluded_path(raw, exclusion_patterns):
            excluded_fe += 1
        else:
            call_sites.append(cs)

    report = APIDriftReport(
        total_backend_routes=len(endpoints),
        total_frontend_calls=len(call_sites),
        excluded_backend=excluded_be,
        excluded_frontend=excluded_fe,
    )

    if not endpoints and not call_sites:
        return report

    # ------------------------------------------------------------------ #
    # Build normalized lookup tables
    # key = (normalized_path, METHOD_UPPER)
    # ------------------------------------------------------------------ #

    # backend: (norm_path, method) -> endpoint object
    backend_map: Dict[Tuple[str, str], object] = {}
    for ep in endpoints:
        key = (_normalize_path(getattr(ep, "route_path", "")), getattr(ep, "http_method", "GET").upper())
        backend_map[key] = ep

    # frontend: (norm_path, method) -> list[call_site] (multiple callers OK)
    frontend_map: Dict[Tuple[str, str], List] = {}
    for cs in call_sites:
        key = (_normalize_path(getattr(cs, "url_pattern", "")), getattr(cs, "http_method", "GET").upper())
        frontend_map.setdefault(key, []).append(cs)

    unmatched_backend: Dict[Tuple[str, str], object] = dict(backend_map)
    unmatched_frontend: Dict[Tuple[str, str], List] = dict(frontend_map)
    edges: List[Dict] = []

    # ------------------------------------------------------------------ #
    # Pass 1 — Exact match (path + method)
    # ------------------------------------------------------------------ #
    for key in list(frontend_map.keys()):
        if key in unmatched_backend:
            ep = unmatched_backend.pop(key)
            callers = unmatched_frontend.pop(key, [])
            report.matched_endpoints += 1

            norm_path, method = key
            for cs in callers:
                edges.append({
                    "source": _caller_id(cs),
                    "target": _handler_id(ep),
                    "edge_type": "api_call",
                    "confidence": 1.0,
                    "route": norm_path,
                    "method": method,
                })

    # ------------------------------------------------------------------ #
    # Pass 2 — Method mismatch (path matches, method does not)
    # ------------------------------------------------------------------ #
    backend_by_path: Dict[str, List[Tuple[str, object]]] = {}
    for (np, method), ep in list(unmatched_backend.items()):
        backend_by_path.setdefault(np, []).append((method, ep))

    frontend_by_path: Dict[str, List[Tuple[str, List]]] = {}
    for (np, method), callers in list(unmatched_frontend.items()):
        frontend_by_path.setdefault(np, []).append((method, callers))

    for norm_path, fe_entries in list(frontend_by_path.items()):
        if norm_path not in backend_by_path:
            continue
        be_entries = backend_by_path[norm_path]
        for fe_method, callers in fe_entries:
            for be_method, ep in be_entries:
                if fe_method != be_method:
                    item = DriftItem(
                        drift_type="method_mismatch",
                        severity="high",
                        description=(
                            f"Frontend calls {fe_method} {norm_path} "
                            f"but backend defines {be_method} {norm_path}."
                        ),
                        backend_path=getattr(ep, "route_path", norm_path),
                        frontend_path=_raw_pattern(callers[0]),
                        backend_method=be_method,
                        frontend_method=fe_method,
                        backend_file=getattr(ep, "file_path", None),
                        frontend_file=getattr(callers[0], "file_path", None),
                        confidence=1.0,
                        suggestion=(
                            f"Change the frontend call to use {be_method}, "
                            f"or update the backend route to accept {fe_method}."
                        ),
                    )
                    report.drift_items.append(item)
                    report.mismatch_count += 1
                    edges.append({
                        "source": _caller_id(callers[0]),
                        "target": _handler_id(ep),
                        "edge_type": "api_drift",
                        "drift_type": "method_mismatch",
                        "confidence": 0.7,
                        "route": norm_path,
                    })
                    # Remove these from unmatched pools
                    _pop_backend_key(unmatched_backend, (norm_path, be_method))
                    _pop_frontend_key(unmatched_frontend, (norm_path, fe_method))

    # ------------------------------------------------------------------ #
    # Pass 3 — Path drift (segment similarity across remaining unmatched)
    # ------------------------------------------------------------------ #
    remaining_be = list(unmatched_backend.items())   # [(key, ep), ...]
    remaining_fe = list(unmatched_frontend.items())  # [(key, callers), ...]

    used_be: set = set()
    used_fe: set = set()

    for fe_key, callers in remaining_fe:
        fe_norm, fe_method = fe_key
        best_score = _DRIFT_SIMILARITY_THRESHOLD
        best_be_key = None
        best_ep = None

        for be_key, ep in remaining_be:
            if be_key in used_be:
                continue
            be_norm, _ = be_key
            score = _segment_similarity(fe_norm, be_norm)
            if score > best_score:
                best_score = score
                best_be_key = be_key
                best_ep = ep

        if best_be_key is not None and best_ep is not None:
            be_norm, be_method = best_be_key
            item = DriftItem(
                drift_type="path_drift",
                severity="high",
                description=(
                    f"Frontend calls '{fe_norm}' but the closest backend route "
                    f"is '{be_norm}' (similarity {best_score:.0%}). "
                    f"Possible API version mismatch or rename."
                ),
                backend_path=getattr(best_ep, "path", be_norm),
                frontend_path=_raw_pattern(callers[0]),
                backend_method=be_method,
                frontend_method=fe_method,
                backend_file=getattr(best_ep, "source_file", None),
                frontend_file=getattr(callers[0], "file_path", None),
                confidence=round(best_score, 3),
                suggestion=(
                    f"Update the frontend to call '{be_norm}' "
                    f"(or migrate the backend route to '{fe_norm}')."
                ),
            )
            report.drift_items.append(item)
            edges.append({
                "source": _caller_id(callers[0]),
                "target": _handler_id(best_ep),
                "edge_type": "api_drift",
                "drift_type": "path_drift",
                "confidence": round(best_score, 3),
                "route": fe_norm,
            })
            used_be.add(best_be_key)
            used_fe.add(fe_key)

    # ------------------------------------------------------------------ #
    # Pass 4 — Shadow endpoints (inactive backend routes in unmatched set)
    # ------------------------------------------------------------------ #
    for be_key, ep in remaining_be:
        if be_key in used_be:
            continue
        is_active = getattr(ep, "is_active", True)
        if not is_active:
            be_norm, be_method = be_key
            item = DriftItem(
                drift_type="shadow_endpoint",
                severity="low",
                description=(
                    f"Backend route {be_method} {be_norm} is marked inactive "
                    f"(dead code / disabled route) and has no frontend consumer."
                ),
                backend_path=getattr(ep, "route_path", be_norm),
                frontend_path=None,
                backend_method=be_method,
                frontend_method=None,
                backend_file=getattr(ep, "file_path", None),
                frontend_file=None,
                confidence=1.0,
                suggestion="Remove the disabled route or re-enable it if still needed.",
            )
            report.drift_items.append(item)
            used_be.add(be_key)

    # ------------------------------------------------------------------ #
    # Pass 5 — Orphaned endpoints (active backend routes with no consumer)
    # ------------------------------------------------------------------ #
    for be_key, ep in remaining_be:
        if be_key in used_be:
            continue
        be_norm, be_method = be_key
        item = DriftItem(
            drift_type="orphaned_endpoint",
            severity="medium",
            description=(
                f"Backend defines {be_method} {be_norm} "
                f"but no frontend code calls it."
            ),
            backend_path=getattr(ep, "route_path", be_norm),
            frontend_path=None,
            backend_method=be_method,
            frontend_method=None,
            backend_file=getattr(ep, "file_path", None),
            frontend_file=None,
            confidence=1.0,
            suggestion=(
                "Add a frontend consumer or deprecate and remove this route. "
                "Could also be called by an external client not tracked here."
            ),
        )
        report.drift_items.append(item)
        report.orphaned_count += 1

    # ------------------------------------------------------------------ #
    # Pass 6 — Missing endpoints (frontend calls with no backend match)
    # ------------------------------------------------------------------ #
    for fe_key, callers in remaining_fe:
        if fe_key in used_fe:
            continue
        fe_norm, fe_method = fe_key
        item = DriftItem(
            drift_type="missing_endpoint",
            severity="critical",
            description=(
                f"Frontend calls {fe_method} {fe_norm} "
                f"but no backend route handles it. Runtime 404 expected."
            ),
            backend_path=None,
            frontend_path=_raw_pattern(callers[0]),
            backend_method=None,
            frontend_method=fe_method,
            backend_file=None,
            frontend_file=getattr(callers[0], "file_path", None),
            confidence=1.0,
            suggestion=(
                f"Implement {fe_method} {fe_norm} on the backend, "
                f"or correct the URL in the frontend caller."
            ),
        )
        report.drift_items.append(item)
        report.missing_count += 1

    # ------------------------------------------------------------------ #
    # Compute aggregate metrics
    # ------------------------------------------------------------------ #
    total = report.total_backend_routes + report.total_frontend_calls
    drift_numerator = report.orphaned_count + report.missing_count + report.mismatch_count
    report.drift_score = drift_numerator / max(1, total)

    if report.total_backend_routes > 0:
        report.coverage = report.matched_endpoints / report.total_backend_routes
    else:
        report.coverage = 0.0

    report._edges = edges
    return report


# ---------------------------------------------------------------------------
# INTEGRATION HELPERS
# ---------------------------------------------------------------------------

def generate_api_edges(drift_report: APIDriftReport) -> List[Dict]:
    """Convert matched endpoints into Collider edge dicts.

    Each edge represents a verified (or drifted) caller-to-handler relationship
    ready for ingestion by the Collider graph builder.

    Example output:
        {
            'source': 'frontend::UserService.fetchUser',
            'target': 'backend::UsersController.get_user',
            'edge_type': 'api_call',
            'confidence': 1.0,
            'route': '/api/users/{param}',
            'method': 'GET'
        }
    """
    return drift_report.get_edges()


def generate_api_insights(drift_report: APIDriftReport) -> List[Dict]:
    """Generate insight dicts compatible with the insights_compiler.

    Each dict matches the shape expected by CompiledInsight and can be
    passed directly into a findings list.

    Example output:
        {
            'category': 'api_drift',
            'severity': 'critical',
            'title': 'Frontend calls non-existent endpoint',
            'description': '...',
            'recommendation': '...',
            'effort': 'medium'
        }
    """
    _EFFORT: Dict[str, str] = {
        "critical": "high",
        "high": "medium",
        "medium": "low",
        "low": "low",
    }
    _TITLES: Dict[str, str] = {
        "missing_endpoint":  "Frontend calls non-existent endpoint",
        "method_mismatch":   "HTTP method mismatch on shared path",
        "path_drift":        "Frontend/backend path version divergence",
        "orphaned_endpoint": "Backend route has no frontend consumer",
        "shadow_endpoint":   "Inactive backend route detected",
    }

    insights: List[Dict] = []
    for item in drift_report.drift_items:
        insights.append({
            "category": "api_drift",
            "severity": item.severity,
            "title": _TITLES.get(item.drift_type, item.drift_type),
            "description": item.description,
            "recommendation": item.suggestion,
            "effort": _EFFORT.get(item.severity, "medium"),
            "evidence": {
                "drift_type": item.drift_type,
                "backend_path": item.backend_path,
                "frontend_path": item.frontend_path,
                "backend_method": item.backend_method,
                "frontend_method": item.frontend_method,
                "backend_file": item.backend_file,
                "frontend_file": item.frontend_file,
                "confidence": item.confidence,
            },
        })
    return insights


# ---------------------------------------------------------------------------
# PRIVATE UTILITIES
# ---------------------------------------------------------------------------

def _caller_id(call_site) -> str:
    """Produce a stable node ID string for a frontend call site."""
    src = getattr(call_site, "file_path", "") or getattr(call_site, "source_file", "") or ""
    caller = getattr(call_site, "caller_name", "") or getattr(call_site, "caller_node_id", "") or ""
    return f"frontend::{src}::{caller}" if caller else f"frontend::{src}"


def _handler_id(endpoint) -> str:
    """Produce a stable node ID string for a backend endpoint handler."""
    src = getattr(endpoint, "file_path", "") or getattr(endpoint, "source_file", "") or ""
    handler = getattr(endpoint, "handler_name", "") or getattr(endpoint, "handler_node_id", "") or ""
    return f"backend::{src}::{handler}" if handler else f"backend::{src}"


def _raw_pattern(call_site) -> Optional[str]:
    """Return the raw url_pattern from a call site object."""
    return getattr(call_site, "url_pattern", None)


def _pop_backend_key(mapping: Dict, key: Tuple) -> None:
    mapping.pop(key, None)


def _pop_frontend_key(mapping: Dict, key: Tuple) -> None:
    mapping.pop(key, None)


# ---------------------------------------------------------------------------
# DEMO / SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # ------------------------------------------------------------------
    # Build mock data that exercises all five drift types
    # ------------------------------------------------------------------

    @dataclass
    class MockEndpoint:
        route_path: str
        http_method: str
        handler_name: str = ""
        file_path: str = ""
        is_active: bool = True

    @dataclass
    class MockCatalog:
        endpoints: List

    @dataclass
    class MockCallSite:
        url_pattern: str
        http_method: str
        caller_name: str = ""
        file_path: str = ""

    @dataclass
    class MockConsumerReport:
        call_sites: List

    catalog = MockCatalog(endpoints=[
        # Will be matched exactly by frontend
        MockEndpoint("/api/users/{id}", "GET", "UsersController.get", "routes/users.py"),
        # Frontend calls with wrong method  → method_mismatch
        MockEndpoint("/api/items", "POST", "ItemsController.create", "routes/items.py"),
        # No frontend consumer at all       → orphaned_endpoint
        MockEndpoint("/api/reports/export", "GET", "ReportsController.export", "routes/reports.py"),
        # Inactive route                    → shadow_endpoint
        MockEndpoint("/api/legacy/data", "GET", "LegacyController.data", "routes/legacy.py", is_active=False),
        # Will be matched via path_drift to /api/v1/settings from frontend
        MockEndpoint("/api/v2/settings", "GET", "SettingsController.get", "routes/settings.py"),
    ])

    consumer = MockConsumerReport(call_sites=[
        # Exact match for /api/users/{id}
        MockCallSite("/api/users/123", "GET", "UserService.fetchUser", "services/UserService.ts"),
        # Method mismatch: frontend uses PUT, backend defines POST
        MockCallSite("/api/items", "PUT", "ItemService.updateItem", "services/ItemService.ts"),
        # Frontend calls non-existent endpoint → missing_endpoint
        MockCallSite("/api/settings/preferences", "GET", "SettingsPage.load", "pages/SettingsPage.tsx"),
        # Path drift: frontend uses v1, backend defines v2
        MockCallSite("/api/v1/settings", "GET", "LegacySettingsService.fetch", "services/LegacySettings.ts"),
    ])

    report = analyze_api_drift(catalog, consumer)

    print("=" * 60)
    print("API DRIFT ANALYSIS DEMO")
    print("=" * 60)
    print(json.dumps(report.summary(), indent=2))
    print()
    print("--- Drift items ---")
    for item in report.drift_items:
        print(f"  [{item.severity.upper():8}] {item.drift_type}")
        print(f"           {item.description}")
        print(f"           Suggestion: {item.suggestion}")
        print()

    print("--- Collider edges ---")
    for edge in generate_api_edges(report):
        print(f"  {edge['edge_type']:10} | {edge.get('route', '')} | confidence={edge['confidence']}")

    print()
    print("--- Insights ---")
    for insight in generate_api_insights(report):
        print(f"  [{insight['severity'].upper():8}] {insight['title']}")
