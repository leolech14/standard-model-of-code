#!/usr/bin/env python3
"""
Frontend API Call Detector
==========================
Detects API calls made by frontend and client-side code.
Part of the Collider analysis pipeline.

Supports:
  - fetch() / window.fetch()
  - axios (get, post, put, patch, delete, request, instance calls)
  - jQuery $.ajax / $.get / $.post
  - Python requests / httpx
  - GraphQL (query / mutation blocks)
  - Generic API client patterns (apiClient, this.http, etc.)

Pure Python, stdlib only. No external dependencies.

Extracted from the Collider analysis pipeline (particle hemisphere).
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class APICallSite:
    """A single detected API call in frontend code."""

    url_pattern: str        # "/api/users" or "/api/users/{id}" (normalized)
    http_method: str        # "GET", "POST", etc. or "QUERY"/"MUTATION" for GraphQL
    caller_node_id: str     # Node ID of the calling function/component
    caller_name: str        # Function/component name
    file_path: str          # Source file
    line_number: int = 0
    call_type: str = "rest"     # "rest", "graphql", "websocket"
    raw_url: str = ""           # Original URL string before normalization
    confidence: float = 1.0     # 1.0 = explicit URL, 0.5 = variable interpolation


@dataclass
class APIConsumerReport:
    """Complete report of API calls found in frontend code."""

    call_sites: List[APICallSite] = field(default_factory=list)
    total_calls: int = 0
    by_method: Dict[str, int] = field(default_factory=dict)
    by_file: Dict[str, int] = field(default_factory=dict)
    unique_endpoints_called: int = 0
    base_urls_detected: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to a plain dict (JSON-ready)."""
        return {
            "call_sites": [asdict(cs) for cs in self.call_sites],
            "total_calls": self.total_calls,
            "by_method": self.by_method,
            "by_file": self.by_file,
            "unique_endpoints_called": self.unique_endpoints_called,
            "base_urls_detected": self.base_urls_detected,
        }

    def find_by_url(self, url_pattern: str) -> List[APICallSite]:
        """Return all call sites whose normalized url_pattern matches."""
        return [cs for cs in self.call_sites if cs.url_pattern == url_pattern]


# ---------------------------------------------------------------------------
# Constants – frontend file extensions
# ---------------------------------------------------------------------------

_FRONTEND_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}

_PYTHON_CLIENT_IMPORTS = re.compile(
    r"\b(import\s+requests|import\s+httpx|from\s+requests|from\s+httpx)\b"
)

# Common base-URL patterns to strip during normalization
_BASE_URL_PATTERNS = [
    re.compile(r"https?://[^/\"'`\s]+"),   # absolute URLs (capture host portion)
    re.compile(r"\$\{[A-Z_][A-Z0-9_]*\}"), # ${BASE_URL} template vars (upper-case = env)
    re.compile(r"\$\{[a-zA-Z_]\w*Url\}"),  # ${apiUrl}, ${baseUrl}
    re.compile(r"['\"]?\s*\+\s*['\"]"),     # string concatenation artefact
]

# ---------------------------------------------------------------------------
# Regex patterns for each call type
# ---------------------------------------------------------------------------

# --- fetch() ---
# Matches: fetch("/api/foo"), fetch(`/api/${id}`), fetch(BASE_URL + "/foo")
_FETCH_RE = re.compile(
    r"""fetch\s*\(\s*(?:['"`])([^'"`]+)(?:['"`])"""     # fetch("/api/...")
    r"""|fetch\s*\(\s*`([^`]+)`"""                        # fetch(`/api/${id}`)
    r"""|fetch\s*\(\s*\w[\w.]*\s*\+\s*(?:['"`])([^'"`]+)(?:['"`])""",  # fetch(BASE + "/x")
    re.MULTILINE,
)

# --- axios method calls ---
# axios.get("/url"), axios.post("/url", data), axios.delete(url)
_AXIOS_METHOD_RE = re.compile(
    r"""axios\s*\.\s*(get|post|put|patch|delete|head|options)\s*\(\s*(?:['"`])([^'"`]+)(?:['"`])"""
    r"""|axios\s*\.\s*(get|post|put|patch|delete|head|options)\s*\(\s*`([^`]+)`""",
    re.IGNORECASE | re.MULTILINE,
)

# axios({ method: 'get', url: '/users' }) object form
_AXIOS_OBJECT_RE = re.compile(
    r"""axios\s*\(\s*\{[^}]*?method\s*:\s*['"`](\w+)['"`][^}]*?url\s*:\s*['"`]([^'"`]+)['"`]"""
    r"""|axios\s*\(\s*\{[^}]*?url\s*:\s*['"`]([^'"`]+)['"`][^}]*?method\s*:\s*['"`](\w+)['"`]""",
    re.IGNORECASE | re.DOTALL,
)

# --- jQuery ---
# $.ajax({ url: "/api/x" }), $.get("/api/x"), $.post("/api/x")
_JQUERY_AJAX_RE = re.compile(
    r"""\$\s*\.\s*ajax\s*\(\s*\{[^}]*?url\s*:\s*['"`]([^'"`]+)['"`]""",
    re.IGNORECASE | re.DOTALL,
)
_JQUERY_AJAX_METHOD_RE = re.compile(
    r"""\$\s*\.\s*(get|post|put|delete)\s*\(\s*(?:['"`])([^'"`]+)(?:['"`])""",
    re.IGNORECASE | re.MULTILINE,
)

# --- Python requests / httpx ---
_PY_HTTP_RE = re.compile(
    r"""(?:requests|httpx|session|client)\s*\.\s*(get|post|put|patch|delete|head|options)\s*\(\s*(?:f?['"`])([^'"`]+)(?:['"`])""",
    re.IGNORECASE | re.MULTILINE,
)
# f-string variant: requests.get(f"{BASE_URL}/users/{user_id}")
_PY_HTTP_FSTR_RE = re.compile(
    r"""(?:requests|httpx|session|client)\s*\.\s*(get|post|put|patch|delete|head|options)\s*\(\s*f['"`]([^'"`]+)['"`]""",
    re.IGNORECASE | re.MULTILINE,
)

# --- GraphQL ---
_GQL_QUERY_RE = re.compile(
    r"""\b(query|mutation)\s+\w*\s*[\({]""",
    re.MULTILINE,
)
# Also detect gql`` template tag and raw query strings
_GQL_TAG_RE = re.compile(
    r"""(?:gql|graphql)\s*`\s*(query|mutation)""",
    re.IGNORECASE | re.MULTILINE,
)

# --- Generic API client ---
# apiClient.get("/x"), this.http.post("/x"), api.delete("/x"), http.put("/x")
_GENERIC_CLIENT_RE = re.compile(
    r"""(?:apiClient|this\.http|this\.api|api|http|client|service)\s*\.\s*(get|post|put|patch|delete|head|options)\s*\(\s*(?:['"`])([^'"`]+)(?:['"`])""",
    re.MULTILINE,
)

# ---------------------------------------------------------------------------
# URL normalization helpers
# ---------------------------------------------------------------------------

# Replaces JS template literal ${expr} with {expr} placeholder
_JS_TEMPLATE_VAR_RE = re.compile(r"\$\{([^}]+)\}")

# Replaces Python f-string {var} / {obj.attr} / {func()} with {param}
_PY_FSTR_VAR_RE = re.compile(r"\{([^}]+)\}")

# Strip known base-URL prefixes (e.g. http://localhost:3000)
_ABS_HOST_RE = re.compile(r"^https?://[^/]+")


def _normalize_url(raw: str, is_template: bool = False, is_fstring: bool = False) -> Tuple[str, float]:
    """
    Normalize a raw URL string into a canonical path pattern.

    Returns (normalized_url, confidence).
      confidence = 1.0  if the URL was a plain string literal
      confidence = 0.7  if it contained a template expression (variable segment)
      confidence = 0.5  if it was heavily interpolated / concatenation artefact
    """
    url = raw.strip().strip("\"'` ")

    # Strip absolute host (http://localhost:3000/api/x -> /api/x)
    url = _ABS_HOST_RE.sub("", url)

    confidence = 1.0

    if is_template or "${" in url:
        # JS template literal: /api/users/${id} -> /api/users/{id}
        url = _JS_TEMPLATE_VAR_RE.sub(lambda m: "{" + _simplify_expr(m.group(1)) + "}", url)
        confidence = 0.7

    if is_fstring or (re.search(r"\{[^}]+\}", url) and not url.startswith("{")):
        # Python f-string: /users/{user_id} -> /users/{user_id} (already brace-wrapped)
        # Also handles concatenation residue
        url = _PY_FSTR_VAR_RE.sub(lambda m: "{" + _simplify_expr(m.group(1)) + "}", url)
        confidence = min(confidence, 0.7)

    # Concatenation artefact: "  + " -> nothing
    url = re.sub(r"\s*\+\s*", "", url)

    # Strip trailing query params for pattern matching (keep ?)
    # e.g. /api/users?active=true -> /api/users
    url = re.sub(r"\?.*$", "", url)

    # Collapse double slashes not at protocol boundary
    url = re.sub(r"(?<!:)//+", "/", url)

    # Strip trailing slash (except bare root "/")
    if url != "/" and url.endswith("/"):
        url = url.rstrip("/")

    # If the URL still looks heavily dynamic (mostly braces), lower confidence
    brace_ratio = url.count("{") / max(len(url.split("/")), 1)
    if brace_ratio > 0.5:
        confidence = min(confidence, 0.5)

    return url or "/", confidence


def _simplify_expr(expr: str) -> str:
    """Simplify a JS/Python interpolation expression to a short placeholder name."""
    expr = expr.strip()
    # obj.prop -> prop
    if "." in expr:
        expr = expr.split(".")[-1]
    # func(args) -> func
    expr = re.sub(r"\(.*\)", "", expr)
    # camelCase -> keep as-is, just strip leading 'this'
    expr = re.sub(r"^this_?", "", expr)
    return expr or "param"


def _detect_base_urls(source: str) -> List[str]:
    """Extract base URL definitions from source (const BASE_URL = "...", etc.)."""
    found = []
    patterns = [
        re.compile(r"""(?:BASE_URL|baseUrl|API_URL|apiUrl|API_BASE|apiBase)\s*[=:]\s*['"`]([^'"`]+)['"`]"""),
        re.compile(r"""axios\.defaults\.baseURL\s*=\s*['"`]([^'"`]+)['"`]"""),
        re.compile(r"""baseURL\s*:\s*['"`]([^'"`]+)['"`]"""),
    ]
    for pat in patterns:
        for m in pat.finditer(source):
            url = m.group(1).strip()
            if url and url not in found:
                found.append(url)
    return found


# ---------------------------------------------------------------------------
# Per-call-type scanner functions
# ---------------------------------------------------------------------------

def _line_number(source: str, match_start: int) -> int:
    """Return 1-based line number for a character offset in source."""
    return source[:match_start].count("\n") + 1


def _scan_fetch(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    results = []
    for m in _FETCH_RE.finditer(source):
        # Group 1: plain string, Group 2: template literal, Group 3: concat trailing segment
        raw = m.group(1) or m.group(2) or m.group(3) or ""
        if not raw:
            continue
        is_tpl = m.group(2) is not None
        is_concat = m.group(3) is not None
        url, conf = _normalize_url(raw, is_template=is_tpl)
        if is_concat:
            conf = min(conf, 0.5)
        results.append(APICallSite(
            url_pattern=url,
            http_method="GET",      # fetch() defaults to GET; OPTIONS/POST need body detection
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))
    return results


def _scan_axios(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    results = []

    # Method shorthand: axios.get("/url")
    for m in _AXIOS_METHOD_RE.finditer(source):
        method = (m.group(1) or m.group(3) or "GET").upper()
        raw = m.group(2) or m.group(4) or ""
        is_tpl = m.group(4) is not None
        if not raw:
            continue
        url, conf = _normalize_url(raw, is_template=is_tpl)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    # Object form: axios({ method: 'post', url: '/x' })
    for m in _AXIOS_OBJECT_RE.finditer(source):
        if m.group(1):  # method then url
            method = m.group(1).upper()
            raw = m.group(2)
        else:           # url then method
            raw = m.group(3)
            method = m.group(4).upper()
        url, conf = _normalize_url(raw)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    return results


def _scan_jquery(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    results = []

    # $.ajax({ url: "/x" }) — method defaults to GET unless specified
    for m in _JQUERY_AJAX_RE.finditer(source):
        raw = m.group(1)
        # Try to find method in the same ajax block
        block = source[m.start(): m.start() + 300]
        method_m = re.search(r"""type\s*:\s*['"`](\w+)['"`]""", block, re.IGNORECASE)
        method = method_m.group(1).upper() if method_m else "GET"
        url, conf = _normalize_url(raw)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    # $.get("/x"), $.post("/x")
    for m in _JQUERY_AJAX_METHOD_RE.finditer(source):
        method = m.group(1).upper()
        raw = m.group(2)
        url, conf = _normalize_url(raw)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    return results


def _scan_python_http(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    results = []

    for m in _PY_HTTP_RE.finditer(source):
        method = m.group(1).upper()
        raw = m.group(2)
        url, conf = _normalize_url(raw)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    # f-string variant
    for m in _PY_HTTP_FSTR_RE.finditer(source):
        method = m.group(1).upper()
        raw = m.group(2)
        url, conf = _normalize_url(raw, is_fstring=True)
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=conf,
        ))

    return results


def _scan_graphql(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    results = []
    seen_lines: set = set()

    def _add(m: re.Match, op_type: str) -> None:
        ln = _line_number(source, m.start())
        if ln in seen_lines:
            return
        seen_lines.add(ln)
        method = "QUERY" if op_type.lower() == "query" else "MUTATION"
        results.append(APICallSite(
            url_pattern="/graphql",
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=ln,
            call_type="graphql",
            raw_url="",
            confidence=0.9,
        ))

    for m in _GQL_QUERY_RE.finditer(source):
        _add(m, m.group(1))

    for m in _GQL_TAG_RE.finditer(source):
        _add(m, m.group(1))

    return results


def _scan_generic_client(source: str, node_id: str, node_name: str, file_path: str) -> List[APICallSite]:
    """Catch-all for apiClient.get(), this.http.post(), etc."""
    results = []
    for m in _GENERIC_CLIENT_RE.finditer(source):
        method = m.group(1).upper()
        raw = m.group(2)
        url, conf = _normalize_url(raw)
        # Slightly lower confidence — could be a non-HTTP client
        results.append(APICallSite(
            url_pattern=url,
            http_method=method,
            caller_node_id=node_id,
            caller_name=node_name,
            file_path=file_path,
            line_number=_line_number(source, m.start()),
            call_type="rest",
            raw_url=raw,
            confidence=min(conf, 0.8),
        ))
    return results


# ---------------------------------------------------------------------------
# File classification helpers
# ---------------------------------------------------------------------------

def _is_frontend_file(file_path: str) -> bool:
    """True for JS/TS/Vue/Svelte files."""
    return Path(file_path).suffix.lower() in _FRONTEND_EXTENSIONS


def _is_python_client_file(source: str) -> bool:
    """True for Python files that import requests or httpx."""
    return bool(_PYTHON_CLIENT_IMPORTS.search(source))


def _get_source(node: dict, source_root: str) -> Optional[str]:
    """
    Retrieve source code for a node.
    Priority: node['source_code'] -> read file_path.
    Returns None if unavailable.
    """
    src = node.get("source_code")
    if src:
        return src

    fpath = node.get("file_path", "")
    if not fpath:
        return None

    candidates = [Path(fpath)]
    if source_root:
        candidates.append(Path(source_root) / fpath)

    for p in candidates:
        try:
            if p.exists():
                return p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_frontend_api_calls(
    nodes: list,
    edges: list,
    source_root: str = "",
) -> APIConsumerReport:
    """
    Detect API calls in frontend/client code.

    Strategy:
      1. Identify frontend files (*.js, *.ts, *.jsx, *.tsx, *.vue, *.svelte, or
         Python files that import requests/httpx).
      2. Scan source code with regex patterns for each call type.
      3. Normalize URLs: strip base URL, resolve template literals, extract path
         pattern.
      4. Deduplicate by normalized URL + method for the unique-endpoint count.

    Args:
        nodes:       List of node dicts with keys: 'id', 'file_path', 'name',
                     optionally 'source_code'.
        edges:       List of edge dicts (currently unused; reserved for future
                     cross-node correlation).
        source_root: Optional filesystem prefix prepended when reading files by
                     path (useful when file_path is relative).

    Returns:
        APIConsumerReport with all discovered call sites and aggregated stats.
    """
    all_sites: List[APICallSite] = []
    base_urls: List[str] = []

    # Group nodes by file so we read each file at most once
    file_to_nodes: Dict[str, List[dict]] = defaultdict(list)
    for node in nodes:
        fp = node.get("file_path", "")
        if fp:
            file_to_nodes[fp].append(node)

    # Also handle nodes without file_path (source_code inline, no file)
    orphan_nodes = [n for n in nodes if not n.get("file_path")]
    for node in orphan_nodes:
        src = node.get("source_code", "")
        if not src:
            continue
        # Determine if this looks like frontend/client code
        if _is_python_client_file(src):
            _process_node(node, src, all_sites)
        elif _looks_like_js_source(src):
            _process_node(node, src, all_sites)

    for file_path, fnodes in file_to_nodes.items():
        # Read source once per file using the first node that can provide it
        source: Optional[str] = None
        for n in fnodes:
            source = _get_source(n, source_root)
            if source is not None:
                break

        if source is None:
            continue

        is_frontend = _is_frontend_file(file_path)
        is_py_client = (not is_frontend) and _is_python_client_file(source)

        if not (is_frontend or is_py_client):
            continue

        # Collect base URLs declared in this file
        for bu in _detect_base_urls(source):
            if bu not in base_urls:
                base_urls.append(bu)

        # For each node in the file, scan using its identity
        for node in fnodes:
            _process_node(node, source, all_sites)

    return _build_report(all_sites, base_urls)


def _looks_like_js_source(src: str) -> bool:
    """Heuristic: does this source resemble JavaScript/TypeScript?"""
    js_markers = ["const ", "let ", "var ", "=>", "function ", "import ", "export "]
    hits = sum(1 for m in js_markers if m in src)
    return hits >= 2


def _process_node(node: dict, source: str, sink: List[APICallSite]) -> None:
    """Run all scanners against a single node's source code, append to sink."""
    node_id = node.get("id", node.get("file_path", "unknown"))
    node_name = node.get("name", "unknown")
    file_path = node.get("file_path", "")

    scanners = [
        _scan_fetch,
        _scan_axios,
        _scan_jquery,
        _scan_python_http,
        _scan_graphql,
        _scan_generic_client,
    ]
    for scanner in scanners:
        try:
            results = scanner(source, node_id, node_name, file_path)
            sink.extend(results)
        except Exception:
            # Individual scanner failure must not abort the whole pipeline
            continue


def _build_report(sites: List[APICallSite], base_urls: List[str]) -> APIConsumerReport:
    """Aggregate raw call sites into the final report structure."""
    by_method: Dict[str, int] = defaultdict(int)
    by_file: Dict[str, int] = defaultdict(int)
    unique_endpoints: set = set()

    for cs in sites:
        by_method[cs.http_method] += 1
        if cs.file_path:
            by_file[cs.file_path] += 1
        unique_endpoints.add((cs.url_pattern, cs.http_method))

    return APIConsumerReport(
        call_sites=sites,
        total_calls=len(sites),
        by_method=dict(by_method),
        by_file=dict(by_file),
        unique_endpoints_called=len(unique_endpoints),
        base_urls_detected=base_urls,
    )


# ---------------------------------------------------------------------------
# CLI demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # --- Demo: inline synthetic nodes (no files needed) ---
    demo_nodes = [
        {
            "id": "node::UserService",
            "name": "UserService",
            "file_path": "src/services/UserService.ts",
            "source_code": """
import axios from 'axios';

const BASE_URL = 'http://localhost:3000';

export async function fetchUsers() {
    return axios.get('/api/users');
}

export async function createUser(data) {
    return axios.post('/api/users', data);
}

export async function deleteUser(id) {
    return axios.delete(`/api/users/${id}`);
}
""",
        },
        {
            "id": "node::ProductPage",
            "name": "ProductPage",
            "file_path": "src/pages/ProductPage.jsx",
            "source_code": """
import React, { useEffect } from 'react';

function ProductPage({ productId }) {
    useEffect(() => {
        fetch(`/api/products/${productId}`)
            .then(r => r.json())
            .then(setProduct);

        fetch('/api/categories')
            .then(r => r.json())
            .then(setCategories);
    }, [productId]);
}
""",
        },
        {
            "id": "node::LegacyWidget",
            "name": "LegacyWidget",
            "file_path": "src/legacy/widget.js",
            "source_code": """
$.ajax({ url: '/api/legacy/data', type: 'GET' });
$.post('/api/legacy/submit', { name: 'foo' });
""",
        },
        {
            "id": "node::GQLClient",
            "name": "GQLClient",
            "file_path": "src/graphql/client.ts",
            "source_code": """
import { gql } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

const CREATE_USER = gql`
  mutation CreateUser($input: UserInput!) {
    createUser(input: $input) {
      id
    }
  }
`;
""",
        },
        {
            "id": "node::PythonClient",
            "name": "fetch_data",
            "file_path": "scripts/fetch_data.py",
            "source_code": """
import requests

BASE_URL = 'http://api.example.com'

def fetch_users():
    return requests.get(f'{BASE_URL}/users')

def create_item(payload):
    return requests.post(f'{BASE_URL}/items', json=payload)
""",
        },
    ]

    report = detect_frontend_api_calls(demo_nodes, edges=[], source_root="")

    print("=== Frontend API Detector Demo ===\n")
    print(f"Total call sites detected : {report.total_calls}")
    print(f"Unique endpoints          : {report.unique_endpoints_called}")
    print(f"By HTTP method            : {report.by_method}")
    print(f"By file                   : {json.dumps(report.by_file, indent=2)}")
    print(f"Base URLs detected        : {report.base_urls_detected}")
    print("\n--- Call Sites ---")
    for cs in report.call_sites:
        print(
            f"  [{cs.http_method:8s}] {cs.url_pattern:<35s} "
            f"conf={cs.confidence:.1f}  {Path(cs.file_path).name}:{cs.line_number}"
        )

    if "--json" in sys.argv:
        print("\n--- Full JSON ---")
        print(json.dumps(report.to_dict(), indent=2))
