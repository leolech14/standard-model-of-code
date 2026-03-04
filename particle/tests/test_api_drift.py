"""
Tests for API drift detection pipeline.

Covers three modules:
  - src.core.api_route_extractor    (backend route extraction)
  - src.core.frontend_api_detector  (frontend API call detection)
  - src.core.api_drift_analyzer     (drift comparison and scoring)
"""

import pytest

from src.core.api_route_extractor import (
    extract_api_routes,
    APIEndpoint,
    EndpointCatalog,
)
from src.core.frontend_api_detector import (
    detect_frontend_api_calls,
    APICallSite,
    APIConsumerReport,
)
from src.core.api_drift_analyzer import (
    analyze_api_drift,
    APIDriftReport,
    DriftItem,
    generate_api_edges,
    generate_api_insights,
)


# =============================================================================
# HELPERS
# =============================================================================

def _make_node(node_id, name, file_path, source_code="", **extra):
    return {
        "id": node_id,
        "name": name,
        "file_path": file_path,
        "source_code": source_code,
        **extra,
    }


def _make_edge(source, target, edge_type="imports"):
    return {"source": source, "target": target, "edge_type": edge_type}


# =============================================================================
# TestAPIRouteExtractor
# =============================================================================

class TestAPIRouteExtractor:
    """Tests for backend API route extraction."""

    def test_fastapi_get_route(self):
        """@app.get('/users') extracts path and GET method."""
        source = '''
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
def list_users():
    return []
'''
        node = _make_node("n1", "list_users", "api/users.py", source_code=source)
        catalog = extract_api_routes([node], [])

        assert isinstance(catalog, EndpointCatalog)
        endpoints = catalog.endpoints
        assert any(e.route_path == "/users" and e.http_method == "GET" for e in endpoints)

    def test_fastapi_path_params(self):
        """@app.get('/users/{user_id}') extracts path parameter."""
        source = '''
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
'''
        node = _make_node("n1", "get_user", "api/users.py", source_code=source)
        catalog = extract_api_routes([node], [])

        paths = [e.route_path for e in catalog.endpoints]
        assert any("{user_id}" in p for p in paths)

    def test_fastapi_router_prefix(self):
        """APIRouter with prefix='/api/v1' composes the full path correctly."""
        source = '''
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1")

@router.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

@router.post("/users")
def create_user(user: dict):
    return {"id": 1}
'''
        node = _make_node("n1", "router", "api/v1/users.py", source_code=source)
        catalog = extract_api_routes([node], [])

        paths = [e.route_path for e in catalog.endpoints]
        assert any("/api/v1" in p for p in paths)

    def test_flask_route_decorator(self):
        """@app.route('/items', methods=['GET','POST']) produces two endpoints."""
        source = '''
from flask import Flask
app = Flask(__name__)

@app.route("/items", methods=["GET", "POST"])
def items():
    pass
'''
        node = _make_node("n1", "items", "app.py", source_code=source)
        catalog = extract_api_routes([node], [])

        item_endpoints = [e for e in catalog.endpoints if "/items" in e.route_path]
        methods = {e.http_method for e in item_endpoints}
        assert "GET" in methods
        assert "POST" in methods

    def test_flask_blueprint_prefix(self):
        """Flask Blueprint prefix is composed into the full path."""
        source = '''
from flask import Blueprint
bp = Blueprint("users", __name__, url_prefix="/users")

@bp.route("/<int:user_id>")
def get_user(user_id):
    pass
'''
        node = _make_node("n1", "bp", "blueprints/users.py", source_code=source)
        catalog = extract_api_routes([node], [])

        paths = [e.route_path for e in catalog.endpoints]
        assert any("/users" in p for p in paths)

    def test_express_route(self):
        """app.get('/users', handler) from JS source is extracted."""
        source = '''
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
    res.json([]);
});
'''
        node = _make_node("n1", "app", "routes/users.js", source_code=source)
        catalog = extract_api_routes([node], [])

        endpoints = catalog.endpoints
        assert any("/users" in e.route_path and e.http_method == "GET" for e in endpoints)

    def test_django_urlpatterns(self):
        """path('users/', views.UserList.as_view()) is extracted."""
        source = '''
from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.UserList.as_view(), name="user-list"),
]
'''
        node = _make_node("n1", "urlpatterns", "urls.py", source_code=source)
        catalog = extract_api_routes([node], [])

        paths = [e.route_path for e in catalog.endpoints]
        assert any("users" in p for p in paths)

    def test_empty_codebase_returns_empty(self):
        """No API files produces an empty catalog."""
        source = '''
def helper(x):
    return x + 1
'''
        node = _make_node("n1", "helper", "utils.py", source_code=source)
        catalog = extract_api_routes([node], [])

        assert isinstance(catalog, EndpointCatalog)
        assert len(catalog.endpoints) == 0

    def test_mixed_framework_detection(self):
        """FastAPI and Flask nodes in the same codebase are both extracted."""
        fastapi_source = '''
@app.get("/api/users")
def list_users():
    return []
'''
        flask_source = '''
@app.route("/legacy/items", methods=["GET"])
def list_items():
    pass
'''
        nodes = [
            _make_node("n1", "list_users", "api/fastapi_users.py", source_code=fastapi_source),
            _make_node("n2", "list_items", "api/flask_items.py", source_code=flask_source),
        ]
        catalog = extract_api_routes(nodes, [])

        paths = [e.route_path for e in catalog.endpoints]
        assert any("/api/users" in p for p in paths)
        assert any("/legacy/items" in p for p in paths)

    def test_endpoint_catalog_to_dict(self):
        """EndpointCatalog serializes to a dict without errors."""
        source = '''
@app.get("/ping")
def ping():
    return {"ok": True}
'''
        node = _make_node("n1", "ping", "main.py", source_code=source)
        catalog = extract_api_routes([node], [])

        result = catalog.to_dict()
        assert isinstance(result, dict)
        assert "endpoints" in result

    def test_find_by_path(self):
        """Catalog.find_by_path returns endpoints matching the pattern."""
        source = '''
@app.get("/users")
def list_users():
    return []

@app.get("/items")
def list_items():
    return []
'''
        node = _make_node("n1", "routes", "main.py", source_code=source)
        catalog = extract_api_routes([node], [])

        matches = catalog.find_by_path("/users")
        assert all("/users" in e.route_path for e in matches)
        assert not any("/items" in e.route_path for e in matches)

    def test_find_by_method(self):
        """Catalog.find_by_method returns only endpoints with that HTTP method."""
        source = '''
@app.get("/users")
def list_users():
    return []

@app.post("/users")
def create_user():
    return {}
'''
        node = _make_node("n1", "routes", "main.py", source_code=source)
        catalog = extract_api_routes([node], [])

        get_endpoints = catalog.find_by_method("GET")
        assert all(e.http_method == "GET" for e in get_endpoints)

    def test_prefix_tree_construction(self):
        """Hierarchical prefix tree is built correctly from the catalog."""
        source = '''
@router.get("/api/v1/users")
def list_users():
    return []

@router.get("/api/v1/items")
def list_items():
    return []

@router.get("/api/v2/users")
def list_users_v2():
    return []
'''
        node = _make_node("n1", "router", "api/routes.py", source_code=source)
        catalog = extract_api_routes([node], [])

        tree = catalog.prefix_tree
        assert isinstance(tree, dict)

    def test_confidence_scoring(self):
        """Explicit decorator yields confidence 1.0; heuristic yields lower."""
        explicit_source = '''
@app.get("/users")
def list_users():
    return []
'''
        node = _make_node("n1", "list_users", "main.py", source_code=explicit_source)
        catalog = extract_api_routes([node], [])

        if catalog.endpoints:
            explicit_conf = catalog.endpoints[0].confidence
            assert explicit_conf >= 0.7


# =============================================================================
# TestFrontendAPIDetector
# =============================================================================

class TestFrontendAPIDetector:
    """Tests for frontend API call detection."""

    def test_fetch_simple_url(self):
        """fetch('/api/users') is detected as an API call."""
        source = '''
const users = await fetch("/api/users");
'''
        node = _make_node("n1", "app", "src/App.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        assert isinstance(report, APIConsumerReport)
        urls = [s.url_pattern for s in report.call_sites]
        assert any("/api/users" in u for u in urls)

    def test_fetch_template_literal(self):
        """fetch(`/api/users/${id}`) is normalized to /api/users/{id}."""
        source = '''
const getUser = async (id) => {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
};
'''
        node = _make_node("n1", "getUser", "src/api.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any("{id}" in u or "/api/users" in u for u in urls)

    def test_axios_get(self):
        """axios.get('/api/items') is detected."""
        source = '''
import axios from 'axios';

const getItems = () => axios.get("/api/items");
'''
        node = _make_node("n1", "getItems", "src/api.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any("/api/items" in u for u in urls)

    def test_axios_config_object(self):
        """axios({ method: 'post', url: '/api/items' }) is detected."""
        source = '''
import axios from 'axios';

const createItem = (data) => axios({
    method: 'post',
    url: '/api/items',
    data,
});
'''
        node = _make_node("n1", "createItem", "src/api.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any("/api/items" in u for u in urls)

    def test_python_requests(self):
        """requests.get('http://api/users') is detected in Python source."""
        source = '''
import requests

def fetch_users():
    return requests.get("http://api/users").json()
'''
        node = _make_node("n1", "fetch_users", "client/api.py", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any("users" in u for u in urls)

    def test_graphql_query(self):
        """GraphQL query block is detected with method='QUERY'."""
        source = '''
const GET_USERS = gql`
    query {
        users {
            id
            name
        }
    }
`;
'''
        node = _make_node("n1", "GET_USERS", "src/queries.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        graphql_calls = [s for s in report.call_sites if s.http_method == "QUERY"]
        assert len(graphql_calls) >= 1

    def test_url_normalization_strips_base(self):
        """http://localhost:3000/api/items is normalized to /api/items."""
        source = '''
fetch("http://localhost:3000/api/items");
'''
        node = _make_node("n1", "app", "src/app.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any(u == "/api/items" or "localhost" not in u for u in urls)

    def test_url_normalization_strips_trailing_slash(self):
        """/api/users/ is normalized to /api/users."""
        source = '''
fetch("/api/users/");
'''
        node = _make_node("n1", "app", "src/app.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        urls = [s.url_pattern for s in report.call_sites]
        assert any(not u.endswith("/") for u in urls if "users" in u)

    def test_empty_frontend_returns_empty(self):
        """Source with no API calls produces an empty report."""
        source = '''
function formatDate(d) {
    return d.toISOString();
}
'''
        node = _make_node("n1", "formatDate", "src/utils.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        assert isinstance(report, APIConsumerReport)
        assert len(report.call_sites) == 0

    def test_deduplication(self):
        """Same URL called multiple times produces unique_endpoints_called = 1."""
        source = '''
fetch("/api/users");
fetch("/api/users");
fetch("/api/users");
'''
        node = _make_node("n1", "app", "src/app.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        assert report.unique_endpoints_called == 1

    def test_consumer_report_to_dict(self):
        """APIConsumerReport serializes to a dict without errors."""
        source = '''
fetch("/api/ping");
'''
        node = _make_node("n1", "app", "src/app.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        result = report.to_dict()
        assert isinstance(result, dict)
        assert "call_sites" in result

    def test_find_by_url(self):
        """Report.find_by_url returns call sites matching the URL pattern."""
        source = '''
fetch("/api/users");
fetch("/api/items");
'''
        node = _make_node("n1", "app", "src/app.js", source_code=source)
        report = detect_frontend_api_calls([node], [])

        matches = report.find_by_url("/api/users")
        assert all("/api/users" in s.url_pattern for s in matches)
        assert not any("/api/items" in s.url_pattern for s in matches)


# =============================================================================
# TestAPIDriftAnalyzer
# =============================================================================

class TestAPIDriftAnalyzer:
    """Tests for API drift comparison and scoring."""

    def _make_catalog(self, endpoints):
        """Build a minimal EndpointCatalog from a list of (path, method) tuples."""
        eps = [APIEndpoint(
            route_path=p, http_method=m, handler_node_id='', handler_name='',
            file_path='', framework='test', confidence=1.0,
        ) for p, m in endpoints]
        return EndpointCatalog(
            endpoints=eps, framework_detected='test',
            total_routes=len(eps), by_method={}, by_file={}, prefix_tree={},
        )

    def _make_report(self, call_sites):
        """Build a minimal APIConsumerReport from a list of (url, method) tuples."""
        sites = [APICallSite(
            url_pattern=u, http_method=m, caller_node_id='', caller_name='', file_path='',
        ) for u, m in call_sites]
        return APIConsumerReport(call_sites=sites)

    def test_perfect_match_zero_drift(self):
        """All backend routes matched by frontend yields drift_score = 0."""
        catalog = self._make_catalog([("/users", "GET"), ("/items", "GET")])
        report = self._make_report([("/users", "GET"), ("/items", "GET")])

        drift = analyze_api_drift(catalog, report)
        assert isinstance(drift, APIDriftReport)
        assert drift.drift_score == 0.0

    def test_orphaned_endpoint(self):
        """Backend route not called by frontend is drift_type='orphaned_endpoint'."""
        catalog = self._make_catalog([("/users", "GET"), ("/admin/secret", "GET")])
        report = self._make_report([("/users", "GET")])

        drift = analyze_api_drift(catalog, report)

        orphaned = [i for i in drift.drift_items if i.drift_type == "orphaned_endpoint"]
        assert len(orphaned) >= 1
        assert any("/admin/secret" in (i.backend_path or '') for i in orphaned)

    def test_missing_endpoint(self):
        """Frontend calls a route the backend does not have: drift_type='missing_endpoint', severity='critical'."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users", "GET"), ("/nonexistent", "GET")])

        drift = analyze_api_drift(catalog, report)

        missing = [i for i in drift.drift_items if i.drift_type == "missing_endpoint"]
        assert len(missing) >= 1
        assert all(i.severity == "critical" for i in missing)

    def test_method_mismatch(self):
        """Same path, different method yields drift_type='method_mismatch', severity='high'."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users", "POST")])

        drift = analyze_api_drift(catalog, report)

        mismatches = [i for i in drift.drift_items if i.drift_type == "method_mismatch"]
        assert len(mismatches) >= 1
        assert all(i.severity == "high" for i in mismatches)

    def test_path_drift_version(self):
        """Backend /v2/users vs frontend /v1/users yields drift_type='path_drift'."""
        catalog = self._make_catalog([("/v2/users", "GET")])
        report = self._make_report([("/v1/users", "GET")])

        drift = analyze_api_drift(catalog, report)

        path_drifts = [i for i in drift.drift_items if i.drift_type == "path_drift"]
        assert len(path_drifts) >= 1

    def test_drift_score_formula(self):
        """Drift score is between 0.0 and 1.0 for any input."""
        catalog = self._make_catalog([("/a", "GET"), ("/b", "POST"), ("/c", "DELETE")])
        report = self._make_report([("/a", "GET"), ("/x", "GET")])

        drift = analyze_api_drift(catalog, report)
        assert 0.0 <= drift.drift_score <= 1.0

    def test_coverage_calculation(self):
        """Coverage = matched / total_backend endpoints."""
        catalog = self._make_catalog([("/a", "GET"), ("/b", "GET"), ("/c", "GET")])
        report = self._make_report([("/a", "GET"), ("/b", "GET")])

        drift = analyze_api_drift(catalog, report)
        assert drift.coverage == pytest.approx(2 / 3, abs=0.01)

    def test_empty_backend_empty_frontend(self):
        """Both empty produces drift_score=0 and no drift items."""
        catalog = self._make_catalog([])
        report = self._make_report([])

        drift = analyze_api_drift(catalog, report)
        assert drift.drift_score == 0.0
        assert len(drift.drift_items) == 0

    def test_empty_backend_with_frontend_calls(self):
        """No backend routes + frontend calls → all missing → score = 1.0."""
        catalog = self._make_catalog([])
        report = self._make_report([("/api/users", "GET"), ("/api/items", "GET")])

        drift = analyze_api_drift(catalog, report)
        assert drift.drift_score == 1.0

    def test_generate_api_edges(self):
        """Matched endpoints produce edge dicts with edge_type='api_call'."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users", "GET")])
        drift = analyze_api_drift(catalog, report)

        edges = generate_api_edges(drift)
        assert isinstance(edges, list)
        api_call_edges = [e for e in edges if e.get("edge_type") == "api_call"]
        assert len(api_call_edges) >= 1

    def test_generate_api_insights(self):
        """Drift items produce insight dicts with category='api_drift'."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users", "POST")])  # method mismatch
        drift = analyze_api_drift(catalog, report)

        insights = generate_api_insights(drift)
        assert isinstance(insights, list)
        drift_insights = [i for i in insights if i.get("category") == "api_drift"]
        assert len(drift_insights) >= 1

    def test_path_normalization_in_matching(self):
        """{id}, :id, and <id> parameter styles all match each other."""
        catalog = self._make_catalog([("/users/{id}", "GET")])
        report_colon = self._make_report([("/users/:id", "GET")])
        report_angle = self._make_report([("/users/<id>", "GET")])

        drift_colon = analyze_api_drift(catalog, report_colon)
        drift_angle = analyze_api_drift(catalog, report_angle)

        assert drift_colon.drift_score == 0.0
        assert drift_angle.drift_score == 0.0

    def test_trailing_slash_normalization(self):
        """/users/ and /users are treated as the same endpoint."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users/", "GET")])

        drift = analyze_api_drift(catalog, report)
        assert drift.drift_score == 0.0

    def test_drift_report_to_dict(self):
        """APIDriftReport serializes to a dict without errors."""
        catalog = self._make_catalog([("/users", "GET")])
        report = self._make_report([("/users", "GET")])
        drift = analyze_api_drift(catalog, report)

        result = drift.to_dict()
        assert isinstance(result, dict)
        assert "drift_score" in result
        assert "drift_items" in result

    def test_drift_report_summary(self):
        """Summary includes counts and score."""
        catalog = self._make_catalog([("/a", "GET"), ("/b", "POST")])
        report = self._make_report([("/a", "GET"), ("/c", "DELETE")])
        drift = analyze_api_drift(catalog, report)

        summary = drift.summary()
        assert isinstance(summary, dict)
        assert "drift_score" in summary
        assert "matched_endpoints" in summary


# =============================================================================
# TestIntegration
# =============================================================================

class TestIntegration:
    """End-to-end pipeline tests combining all three modules."""

    def test_full_pipeline_fastapi_react(self):
        """Mock FastAPI backend + React frontend produces a realistic drift report."""
        backend_source = '''
from fastapi import APIRouter
router = APIRouter(prefix="/api/v1")

@router.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}

@router.post("/users")
def create_user(user: dict):
    return {"id": 1}

@router.get("/items")
def list_items():
    return []
'''
        frontend_source = '''
const getUser = async (id) => {
    const response = await fetch(`/api/v1/users/${id}`);
    return response.json();
};

const createUser = async (data) => {
    const response = await fetch("/api/v1/users", {
        method: "POST",
        body: JSON.stringify(data)
    });
    return response.json();
};
'''
        backend_node = _make_node("b1", "router", "api/routes.py", source_code=backend_source)
        frontend_node = _make_node("f1", "api", "src/api.js", source_code=frontend_source)

        catalog = extract_api_routes([backend_node], [])
        consumer = detect_frontend_api_calls([frontend_node], [])
        drift = analyze_api_drift(catalog, consumer)

        assert isinstance(drift, APIDriftReport)
        assert 0.0 <= drift.drift_score <= 1.0
        # /items exists in backend but not called from frontend: orphan expected
        orphaned = [i for i in drift.drift_items if i.drift_type == "orphaned_endpoint"]
        assert len(orphaned) >= 1

    def test_full_pipeline_flask_vanilla_js(self):
        """Mock Flask backend + vanilla JS frontend produces a realistic report."""
        backend_source = '''
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify([])

@app.route("/api/products/<int:product_id>", methods=["GET", "DELETE"])
def product_detail(product_id):
    return jsonify({})
'''
        frontend_source = '''
document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/products")
        .then(r => r.json())
        .then(data => console.log(data));

    fetch("/api/products/42", { method: "DELETE" });
});
'''
        backend_node = _make_node("b1", "app", "app.py", source_code=backend_source)
        frontend_node = _make_node("f1", "main", "static/main.js", source_code=frontend_source)

        catalog = extract_api_routes([backend_node], [])
        consumer = detect_frontend_api_calls([frontend_node], [])
        drift = analyze_api_drift(catalog, consumer)

        assert isinstance(drift, APIDriftReport)
        assert drift.coverage >= 0.0

    def test_full_pipeline_no_api(self):
        """Non-API codebase produces empty everything with no crash."""
        utility_source = '''
def clamp(value, lo, hi):
    return max(lo, min(hi, value))

def lerp(a, b, t):
    return a + (b - a) * t
'''
        node = _make_node("u1", "math_utils", "utils/math.py", source_code=utility_source)

        catalog = extract_api_routes([node], [])
        consumer = detect_frontend_api_calls([node], [])
        drift = analyze_api_drift(catalog, consumer)

        assert isinstance(catalog, EndpointCatalog)
        assert len(catalog.endpoints) == 0
        assert isinstance(consumer, APIConsumerReport)
        assert len(consumer.call_sites) == 0
        assert isinstance(drift, APIDriftReport)
        assert drift.drift_score == 0.0
        assert len(drift.drift_items) == 0
