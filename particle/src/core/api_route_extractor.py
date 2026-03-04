#!/usr/bin/env python3
"""
API ROUTE EXTRACTOR
===================

Extracts API route definitions from backend source code nodes produced by
the Collider analysis pipeline.

Supported frameworks (auto-detected):
- FastAPI  : @app.get("/path"), @router.post("/path"), APIRouter prefix composition
- Flask    : @app.route("/path", methods=[...]), @bp.get("/path")
- Django   : path("route/", view), re_path(r"^pattern")
- Express  : app.get("/path", handler), router.post("/path", handler) (JS/TS)

Usage:
    from src.core.api_route_extractor import extract_api_routes

    catalog = extract_api_routes(nodes, edges, source_root="/path/to/repo")
    print(catalog.to_dict())
"""

import re
import ast
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class APIEndpoint:
    """A single extracted API endpoint."""

    route_path: str
    """Normalized route path, e.g. '/users/{id}' or '/api/items'."""

    http_method: str
    """HTTP verb in uppercase: 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', '*'."""

    handler_node_id: str
    """Node ID of the handler function as found in the nodes list."""

    handler_name: str
    """Function or method name that handles the route."""

    file_path: str
    """Absolute or repo-relative path to the source file."""

    framework: str
    """Detected framework: 'fastapi', 'flask', 'django', 'express', 'unknown'."""

    line_number: int = 0
    """Line where the route decorator or registration call appears."""

    parameters: List[str] = field(default_factory=list)
    """Path parameters extracted from route, e.g. ['id', 'slug']."""

    response_codes: List[int] = field(default_factory=list)
    """HTTP response codes detectable from source (e.g. status_code=404)."""

    confidence: float = 1.0
    """Extraction confidence: 1.0 = explicit decorator, 0.7 = heuristic match."""


@dataclass
class EndpointCatalog:
    """Complete catalog of API endpoints found in a codebase."""

    endpoints: List[APIEndpoint]
    """All extracted endpoints."""

    framework_detected: str
    """Primary framework, or 'unknown' when none is identifiable."""

    total_routes: int
    """Total number of unique endpoint definitions found."""

    by_method: Dict[str, int]
    """Aggregated count per HTTP method, e.g. {'GET': 5, 'POST': 3}."""

    by_file: Dict[str, int]
    """Aggregated count per source file path."""

    prefix_tree: Dict[str, Any]
    """Nested dict representing the route hierarchy by path segments."""

    def to_dict(self) -> dict:
        """Serialise the catalog to a plain dict (JSON-safe)."""
        return {
            "framework_detected": self.framework_detected,
            "total_routes": self.total_routes,
            "by_method": self.by_method,
            "by_file": self.by_file,
            "prefix_tree": self.prefix_tree,
            "endpoints": [
                {
                    "route_path": ep.route_path,
                    "http_method": ep.http_method,
                    "handler_node_id": ep.handler_node_id,
                    "handler_name": ep.handler_name,
                    "file_path": ep.file_path,
                    "framework": ep.framework,
                    "line_number": ep.line_number,
                    "parameters": ep.parameters,
                    "response_codes": ep.response_codes,
                    "confidence": ep.confidence,
                }
                for ep in self.endpoints
            ],
        }

    def find_by_path(self, path_pattern: str) -> List[APIEndpoint]:
        """Return endpoints whose route_path contains path_pattern as a substring."""
        return [ep for ep in self.endpoints if path_pattern in ep.route_path]

    def find_by_method(self, method: str) -> List[APIEndpoint]:
        """Return all endpoints matching the given HTTP method (case-insensitive)."""
        method_upper = method.upper()
        return [ep for ep in self.endpoints if ep.http_method == method_upper]


# =============================================================================
# REGEX PATTERNS
# =============================================================================

# FastAPI / Starlette decorator: @app.get("/path") or @router.post("/path", ...)
_FASTAPI_DECORATOR = re.compile(
    r'@\w+\.(get|post|put|delete|patch|head|options|trace)\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# Flask @app.route("/path", methods=[...]) or @bp.route(...)
_FLASK_ROUTE = re.compile(
    r'@\w+\.route\s*\(\s*["\']([^"\']+)["\'](?:[^)]*methods\s*=\s*\[([^\]]*)\])?',
    re.IGNORECASE,
)

# Flask shorthand: @bp.get("/path"), @bp.post("/path")
_FLASK_SHORTHAND = re.compile(
    r'@\w+\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# Django path/re_path in urlpatterns: path("users/", view_fn)
_DJANGO_PATH = re.compile(
    r'(?:re_)?path\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# FastAPI include_router with prefix: app.include_router(router, prefix="/api/v1")
_INCLUDE_ROUTER = re.compile(
    r'include_router\s*\(\s*(\w+)\s*(?:,|\))(?:[^)]*prefix\s*=\s*["\']([^"\']*)["\'])?',
    re.IGNORECASE,
)

# FastAPI APIRouter constructor: router = APIRouter(prefix="/api/v1")
_APIROUTER_CTOR = re.compile(
    r'(\w+)\s*=\s*APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']*)["\']',
    re.IGNORECASE,
)

# Flask register_blueprint: app.register_blueprint(bp, url_prefix="/api")
_REGISTER_BLUEPRINT = re.compile(
    r'register_blueprint\s*\(\s*(\w+)\s*(?:,|\))(?:[^)]*url_prefix\s*=\s*["\']([^"\']*)["\'])?',
    re.IGNORECASE,
)

# Flask Blueprint constructor: bp = Blueprint("name", __name__, url_prefix="/users")
_BLUEPRINT_CTOR = re.compile(
    r'(\w+)\s*=\s*Blueprint\s*\([^)]*url_prefix\s*=\s*["\']([^"\']*)["\']',
    re.IGNORECASE,
)

# Express.js: app.get("/path", ...) or router.post("/path", ...)
_EXPRESS_ROUTE = re.compile(
    r"\b(?:app|router|server)\.(get|post|put|delete|patch|all|use)\s*\(\s*[\"'`]([^\"'`]+)[\"'`]",
    re.IGNORECASE,
)

# Path parameters in various styles
_FASTAPI_PARAM = re.compile(r'\{(\w+)\}')
_FLASK_PARAM = re.compile(r'<(?:[^:>]+:)?(\w+)>')
_EXPRESS_PARAM = re.compile(r':(\w+)')

# Status codes referenced inline: status_code=404, HTTPStatus.OK
_STATUS_CODE = re.compile(r'status_code\s*=\s*(\d{3})')

# Django HTTP method decorators: @require_http_methods(["GET"])
_DJANGO_METHODS = re.compile(
    r'require_http_methods\s*\(\s*\[([^\]]+)\]',
    re.IGNORECASE,
)

# Function definition line immediately following a decorator block
_FUNC_DEF = re.compile(r'^(?:async\s+)?def\s+(\w+)', re.MULTILINE)
_JS_FUNC_NAME = re.compile(r',\s*(?:async\s+)?(?:function\s+)?(\w+)\s*[,\)]')

# =============================================================================
# FRAMEWORK DETECTION
# =============================================================================

_FRAMEWORK_SIGNALS: Dict[str, List[str]] = {
    "fastapi": ["fastapi", "starlette"],
    "flask": ["flask"],
    "django": ["django"],
    "express": ["express", "koa", "hapi"],
}


def _detect_framework(nodes: list, edges: list) -> str:
    """Infer the primary web framework from import edges and node names.

    Scans edges with edge_type='imports' for framework package names, then
    falls back to scanning node names and file paths for framework signals.

    Returns the framework name or 'unknown'.
    """
    # Score each framework based on evidence weight
    scores: Dict[str, int] = {fw: 0 for fw in _FRAMEWORK_SIGNALS}

    # Primary signal: import edges referencing framework packages
    for edge in edges:
        if edge.get("edge_type") not in ("imports", "import", "requires"):
            continue
        target = (edge.get("target") or edge.get("to") or "").lower()
        for framework, signals in _FRAMEWORK_SIGNALS.items():
            if any(sig in target for sig in signals):
                scores[framework] += 3

    # Secondary signal: node names and file paths
    for node in nodes:
        text = " ".join([
            (node.get("name") or "").lower(),
            (node.get("file_path") or "").lower(),
            (node.get("source_code") or "")[:500].lower(),
        ])
        for framework, signals in _FRAMEWORK_SIGNALS.items():
            if any(sig in text for sig in signals):
                scores[framework] += 1

    best = max(scores, key=lambda fw: scores[fw])
    return best if scores[best] > 0 else "unknown"


# =============================================================================
# PATH PARAMETER EXTRACTION
# =============================================================================

def _extract_path_params(route_path: str, framework: str) -> List[str]:
    """Extract path parameter names from a route path string.

    Handles:
    - FastAPI / Django : {param}
    - Flask            : <type:param> or <param>
    - Express          : :param
    """
    if framework in ("fastapi", "django", "unknown"):
        params = _FASTAPI_PARAM.findall(route_path)
        if params:
            return params
    if framework == "flask":
        return _FLASK_PARAM.findall(route_path)
    if framework == "express":
        return _EXPRESS_PARAM.findall(route_path)
    # Try all patterns as fallback
    return (
        _FASTAPI_PARAM.findall(route_path)
        or _FLASK_PARAM.findall(route_path)
        or _EXPRESS_PARAM.findall(route_path)
    )


def _normalize_flask_path(path: str) -> str:
    """Convert Flask <type:param> syntax to canonical {param} form."""
    return re.sub(r'<(?:[^:>]+:)?(\w+)>', r'{\1}', path)


def _normalize_express_path(path: str) -> str:
    """Convert Express :param syntax to canonical {param} form."""
    return re.sub(r':(\w+)', r'{\1}', path)


# =============================================================================
# ROUTER / BLUEPRINT PREFIX RESOLUTION
# =============================================================================

def _collect_prefixes(source: str, framework: str) -> Dict[str, str]:
    """Return a mapping of {variable_name: prefix} found in the source.

    Handles both constructor-level prefixes (APIRouter(prefix=...), Blueprint(url_prefix=...))
    and mount-level prefixes (include_router, register_blueprint).
    Mount-level prefixes take priority over constructor-level ones.
    """
    prefixes: Dict[str, str] = {}
    if framework in ("fastapi", "unknown"):
        # Constructor: router = APIRouter(prefix="/api/v1")
        for m in _APIROUTER_CTOR.finditer(source):
            var_name, prefix = m.group(1), m.group(2) or ""
            prefixes[var_name] = prefix.rstrip("/")
        # Mount: app.include_router(router, prefix="/api/v1") — overrides constructor
        for m in _INCLUDE_ROUTER.finditer(source):
            var_name, prefix = m.group(1), m.group(2) or ""
            prefixes[var_name] = prefix.rstrip("/")
    if framework in ("flask", "unknown"):
        # Constructor: bp = Blueprint("name", __name__, url_prefix="/users")
        for m in _BLUEPRINT_CTOR.finditer(source):
            var_name, prefix = m.group(1), m.group(2) or ""
            prefixes[var_name] = prefix.rstrip("/")
        # Mount: app.register_blueprint(bp, url_prefix="/api") — overrides constructor
        for m in _REGISTER_BLUEPRINT.finditer(source):
            var_name, prefix = m.group(1), m.group(2) or ""
            prefixes[var_name] = prefix.rstrip("/")
    return prefixes


# =============================================================================
# RESPONSE CODE EXTRACTION
# =============================================================================

def _extract_response_codes(source: str) -> List[int]:
    """Find explicit HTTP status codes referenced in the source snippet."""
    found = _STATUS_CODE.findall(source)
    codes = sorted({int(c) for c in found if 100 <= int(c) <= 599})
    return codes


# =============================================================================
# PER-FRAMEWORK ROUTE EXTRACTION
# =============================================================================

def _extract_fastapi(source: str, node: dict, prefix: str = "") -> List[APIEndpoint]:
    """Extract FastAPI route decorators from a source snippet."""
    endpoints: List[APIEndpoint] = []
    file_path = node.get("file_path", "")
    node_id = node.get("id") or node.get("node_id") or node.get("name", "")
    lines = source.splitlines()

    for i, line in enumerate(lines, start=1):
        m = _FASTAPI_DECORATOR.search(line)
        if not m:
            continue
        method = m.group(1).upper()
        raw_path = m.group(2)
        full_path = (prefix.rstrip("/") + "/" + raw_path.lstrip("/")) if prefix else raw_path

        # Find the handler function defined after this decorator block
        handler_name = _find_handler_after(lines, i - 1)
        response_codes = _extract_response_codes(source)

        endpoints.append(APIEndpoint(
            route_path=full_path,
            http_method=method,
            handler_node_id=node_id,
            handler_name=handler_name,
            file_path=file_path,
            framework="fastapi",
            line_number=i,
            parameters=_extract_path_params(full_path, "fastapi"),
            response_codes=response_codes,
            confidence=1.0,
        ))
    return endpoints


def _extract_flask(source: str, node: dict, prefix: str = "") -> List[APIEndpoint]:
    """Extract Flask route decorators from a source snippet."""
    endpoints: List[APIEndpoint] = []
    file_path = node.get("file_path", "")
    node_id = node.get("id") or node.get("node_id") or node.get("name", "")
    lines = source.splitlines()

    for i, line in enumerate(lines, start=1):
        # @app.route("/path", methods=[...])
        m_route = _FLASK_ROUTE.search(line)
        if m_route:
            raw_path = m_route.group(1)
            methods_raw = m_route.group(2) or ""
            methods = [
                w.strip().strip("\"'").upper()
                for w in methods_raw.split(",")
                if w.strip().strip("\"'")
            ] or ["GET"]
            handler_name = _find_handler_after(lines, i - 1)
            norm_path = _normalize_flask_path(raw_path)
            full_path = (prefix.rstrip("/") + "/" + norm_path.lstrip("/")) if prefix else norm_path
            for method in methods:
                endpoints.append(APIEndpoint(
                    route_path=full_path,
                    http_method=method,
                    handler_node_id=node_id,
                    handler_name=handler_name,
                    file_path=file_path,
                    framework="flask",
                    line_number=i,
                    parameters=_extract_path_params(full_path, "flask"),
                    response_codes=_extract_response_codes(source),
                    confidence=1.0,
                ))
            continue

        # @bp.get("/path") shorthand
        m_short = _FLASK_SHORTHAND.search(line)
        if m_short:
            method = m_short.group(1).upper()
            raw_path = m_short.group(2)
            norm_path = _normalize_flask_path(raw_path)
            full_path = (prefix.rstrip("/") + "/" + norm_path.lstrip("/")) if prefix else norm_path
            handler_name = _find_handler_after(lines, i - 1)
            endpoints.append(APIEndpoint(
                route_path=full_path,
                http_method=method,
                handler_node_id=node_id,
                handler_name=handler_name,
                file_path=file_path,
                framework="flask",
                line_number=i,
                parameters=_extract_path_params(full_path, "flask"),
                response_codes=_extract_response_codes(source),
                confidence=1.0,
            ))

    return endpoints


def _extract_django(source: str, node: dict) -> List[APIEndpoint]:
    """Extract Django urlpatterns route definitions from a source snippet."""
    endpoints: List[APIEndpoint] = []
    file_path = node.get("file_path", "")
    node_id = node.get("id") or node.get("node_id") or node.get("name", "")

    lines = source.splitlines()
    for i, line in enumerate(lines, start=1):
        m = _DJANGO_PATH.search(line)
        if not m:
            continue
        raw_path = m.group(1)

        # Attempt to pull the view name from the same line
        view_match = re.search(r',\s*(?:views\.)?(\w+)', line)
        handler_name = view_match.group(1) if view_match else "unknown"

        # Method detection via @require_http_methods on a nearby preceding line
        methods = _find_django_methods(lines, i - 1)

        norm_path = "/" + raw_path.lstrip("^").rstrip("$").lstrip("/")
        for method in methods:
            endpoints.append(APIEndpoint(
                route_path=norm_path,
                http_method=method,
                handler_node_id=node_id,
                handler_name=handler_name,
                file_path=file_path,
                framework="django",
                line_number=i,
                parameters=_extract_path_params(norm_path, "django"),
                response_codes=_extract_response_codes(source),
                confidence=0.9,
            ))
    return endpoints


def _extract_express(source: str, node: dict) -> List[APIEndpoint]:
    """Extract Express.js route registrations from a JS/TS source snippet."""
    endpoints: List[APIEndpoint] = []
    file_path = node.get("file_path", "")
    node_id = node.get("id") or node.get("node_id") or node.get("name", "")
    lines = source.splitlines()

    for i, line in enumerate(lines, start=1):
        m = _EXPRESS_ROUTE.search(line)
        if not m:
            continue
        raw_method = m.group(1).upper()
        method = "*" if raw_method in ("ALL", "USE") else raw_method
        raw_path = m.group(2)
        norm_path = _normalize_express_path(raw_path)

        # Handler name: look for a function reference after the path argument
        handler_match = _JS_FUNC_NAME.search(line)
        handler_name = handler_match.group(1) if handler_match else "anonymous"

        endpoints.append(APIEndpoint(
            route_path=norm_path,
            http_method=method,
            handler_node_id=node_id,
            handler_name=handler_name,
            file_path=file_path,
            framework="express",
            line_number=i,
            parameters=_extract_path_params(norm_path, "express"),
            response_codes=_extract_response_codes(source),
            confidence=1.0,
        ))
    return endpoints


# =============================================================================
# HELPER UTILITIES
# =============================================================================

def _find_handler_after(lines: List[str], decorator_idx: int) -> str:
    """Scan forward from a decorator line to find the 'def' that follows.

    Skips blank lines and additional decorators (@...) between the matched
    decorator and the function definition.
    """
    for j in range(decorator_idx + 1, min(decorator_idx + 10, len(lines))):
        m = _FUNC_DEF.match(lines[j].lstrip())
        if m:
            return m.group(1)
    return "unknown"


def _find_django_methods(lines: List[str], route_idx: int) -> List[str]:
    """Look backward from a Django path() call for method restriction decorators."""
    for j in range(route_idx - 1, max(route_idx - 5, -1), -1):
        m = _DJANGO_METHODS.search(lines[j])
        if m:
            raw = m.group(1)
            return [w.strip().strip("\"'").upper() for w in raw.split(",") if w.strip().strip("\"'")]
    return ["*"]


def _read_source(node: dict, source_root: str) -> str:
    """Return the source code for a node.

    Priority:
    1. 'source_code' field on the node (already loaded by Collider)
    2. Read 'file_path' from disk (relative paths resolved against source_root)
    """
    source = node.get("source_code") or ""
    if source:
        return source

    file_path = node.get("file_path", "")
    if not file_path:
        return ""

    path = Path(file_path)
    if not path.is_absolute() and source_root:
        path = Path(source_root) / file_path

    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# =============================================================================
# PREFIX TREE BUILDER
# =============================================================================

def _build_prefix_tree(endpoints: List[APIEndpoint]) -> Dict[str, Any]:
    """Build a nested dict from route path segments for hierarchical navigation.

    Example:
        /api/v1/users/{id} -> {"api": {"v1": {"users": {"{id}": {"__endpoints__": [...]}}}}}
    """
    tree: Dict[str, Any] = {}
    for ep in endpoints:
        parts = [p for p in ep.route_path.strip("/").split("/") if p]
        node: Dict[str, Any] = tree
        for part in parts:
            node = node.setdefault(part, {})
        leaf: list = node.setdefault("__endpoints__", [])
        leaf.append(f"{ep.http_method} {ep.route_path}")
    return tree


# =============================================================================
# PUBLIC ENTRY POINT
# =============================================================================

def extract_api_routes(
    nodes: list,
    edges: list,
    source_root: str = "",
) -> EndpointCatalog:
    """Extract API route definitions from analyzed codebase nodes.

    Strategy:
    1. Detect the primary framework from import edges and node metadata.
    2. For each node that plausibly contains route definitions, read its source.
    3. Apply framework-specific regex extraction to find route decorators /
       registration calls.
    4. Resolve APIRouter prefixes (FastAPI) and Blueprint prefixes (Flask) using
       include_router / register_blueprint patterns found in the same source.
    5. Aggregate into an EndpointCatalog with statistics and a prefix tree.

    Args:
        nodes:       List of node dicts from the Collider parse output.
                     Expected fields: 'file_path', 'name', 'id' (optional),
                     'source_code' (optional), 'decorators' (optional).
        edges:       List of edge dicts (used for framework detection via
                     import relationships).
        source_root: Filesystem root to resolve relative file_path values.
                     Pass the repo root when node file_path values are relative.

    Returns:
        EndpointCatalog with all discovered endpoints and aggregated statistics.
        Returns an empty catalog (total_routes=0) when no routes are found.
    """
    framework = _detect_framework(nodes, edges)

    # Collect prefix maps from all files (prefix composition pass)
    # Maps variable_name -> prefix string for the whole project
    global_prefixes: Dict[str, str] = {}
    for node in nodes:
        source = _read_source(node, source_root)
        if source:
            global_prefixes.update(_collect_prefixes(source, framework))

    endpoints: List[APIEndpoint] = []

    # File-level deduplication: read each file once even if multiple nodes
    # reference it (e.g. multiple functions in the same module)
    seen_files: Dict[str, str] = {}

    for node in nodes:
        file_path = node.get("file_path", "")
        if not file_path:
            continue

        # Determine framework from file extension for mixed codebases
        ext = Path(file_path).suffix.lower()
        is_js = ext in (".js", ".ts", ".mjs", ".cjs")
        effective_framework = "express" if is_js and framework in ("express", "unknown") else framework

        if file_path not in seen_files:
            seen_files[file_path] = _read_source(node, source_root)
        source = seen_files[file_path]

        if not source:
            continue

        # Determine applicable prefix for this node's router/blueprint variable
        node_name = node.get("name", "")
        prefix = global_prefixes.get(node_name, "")

        # Try the primary framework first
        node_endpoints: List[APIEndpoint] = []
        if effective_framework == "fastapi":
            node_endpoints = _extract_fastapi(source, node, prefix)
        elif effective_framework == "flask":
            node_endpoints = _extract_flask(source, node, prefix)
        elif effective_framework == "django":
            node_endpoints = _extract_django(source, node)
        elif effective_framework == "express":
            node_endpoints = _extract_express(source, node)

        # Fallback: if the primary framework yielded nothing, try all extractors
        # This handles mixed-framework codebases (e.g. FastAPI + Flask)
        if not node_endpoints and effective_framework != "unknown":
            node_endpoints = []
            node_endpoints.extend(_extract_fastapi(source, node, prefix))
            node_endpoints.extend(_extract_flask(source, node, prefix))
            node_endpoints.extend(_extract_django(source, node))
            if is_js:
                node_endpoints.extend(_extract_express(source, node))
            for ep in node_endpoints:
                ep.confidence = min(ep.confidence, 0.8)

        if effective_framework == "unknown" and not node_endpoints:
            node_endpoints = []
            node_endpoints.extend(_extract_fastapi(source, node))
            node_endpoints.extend(_extract_flask(source, node))
            node_endpoints.extend(_extract_django(source, node))
            if is_js:
                node_endpoints.extend(_extract_express(source, node))
            for ep in node_endpoints:
                ep.confidence = 0.7

        endpoints.extend(node_endpoints)

    # Deduplicate by (file_path, line_number, method) — multiple nodes per file
    seen_keys: set = set()
    unique_endpoints: List[APIEndpoint] = []
    for ep in endpoints:
        key = (ep.file_path, ep.line_number, ep.http_method, ep.route_path)
        if key not in seen_keys:
            seen_keys.add(key)
            unique_endpoints.append(ep)

    # Aggregate statistics
    by_method: Dict[str, int] = {}
    by_file: Dict[str, int] = {}
    for ep in unique_endpoints:
        by_method[ep.http_method] = by_method.get(ep.http_method, 0) + 1
        by_file[ep.file_path] = by_file.get(ep.file_path, 0) + 1

    return EndpointCatalog(
        endpoints=unique_endpoints,
        framework_detected=framework,
        total_routes=len(unique_endpoints),
        by_method=by_method,
        by_file=by_file,
        prefix_tree=_build_prefix_tree(unique_endpoints),
    )


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    import json

    # Minimal synthetic node list covering FastAPI, Flask, Django, and Express

    _FASTAPI_SOURCE = """\
from fastapi import APIRouter
router = APIRouter()

@router.get("/users")
async def list_users():
    return []

@router.post("/users")
async def create_user():
    return {}

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return {}

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int):
    pass
"""

    _FLASK_SOURCE = """\
from flask import Blueprint
bp = Blueprint("items", __name__)

@bp.route("/items", methods=["GET", "POST"])
def item_list():
    pass

@bp.get("/items/<int:item_id>")
def item_detail(item_id):
    pass
"""

    _DJANGO_SOURCE = """\
from django.urls import path, re_path
from . import views

urlpatterns = [
    path("orders/", views.OrderList),
    path("orders/<int:pk>/", views.OrderDetail),
    re_path(r"^legacy/.*", views.LegacyHandler),
]
"""

    _EXPRESS_SOURCE = """\
const express = require('express');
const router = express.Router();

router.get('/products', listProducts);
router.post('/products', createProduct);
router.get('/products/:id', getProduct);
router.put('/products/:id', updateProduct);
"""

    demo_nodes = [
        {
            "id": "node-fastapi-1",
            "name": "router",
            "file_path": "app/users.py",
            "source_code": _FASTAPI_SOURCE,
        },
        {
            "id": "node-flask-1",
            "name": "bp",
            "file_path": "app/items.py",
            "source_code": _FLASK_SOURCE,
        },
        {
            "id": "node-django-1",
            "name": "urlpatterns",
            "file_path": "app/urls.py",
            "source_code": _DJANGO_SOURCE,
        },
        {
            "id": "node-express-1",
            "name": "router",
            "file_path": "src/routes/products.js",
            "source_code": _EXPRESS_SOURCE,
        },
    ]

    demo_edges = [
        {"edge_type": "imports", "source": "node-fastapi-1", "target": "fastapi"},
        {"edge_type": "imports", "source": "node-flask-1", "target": "flask"},
        {"edge_type": "imports", "source": "node-django-1", "target": "django"},
        {"edge_type": "imports", "source": "node-express-1", "target": "express"},
    ]

    catalog = extract_api_routes(demo_nodes, demo_edges)

    print(f"Framework detected : {catalog.framework_detected}")
    print(f"Total routes       : {catalog.total_routes}")
    print(f"By method          : {catalog.by_method}")
    print(f"By file            : {catalog.by_file}")
    print()
    for ep in catalog.endpoints:
        print(f"  [{ep.http_method:<7}] {ep.route_path:<35} {ep.handler_name} ({ep.framework})")
    print()
    print("Prefix tree (JSON):")
    print(json.dumps(catalog.prefix_tree, indent=2))
