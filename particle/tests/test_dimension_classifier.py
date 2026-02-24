"""Unit tests for dimension_classifier."""

from types import SimpleNamespace

from src.core import dimension_classifier as dc


def test_regex_boundary_classification():
    classifier = dc.RegexDimensionClassifier()

    assert classifier.classify_boundary("data = open(path).read()") == dc.BoundaryType.INPUT
    assert classifier.classify_boundary("print('ok'); json.dump(obj, f)") == dc.BoundaryType.OUTPUT
    assert classifier.classify_boundary("x = open(path).read(); print(x)") == dc.BoundaryType.IO
    assert classifier.classify_boundary("value = a + b") == dc.BoundaryType.INTERNAL


def test_regex_state_classification():
    classifier = dc.RegexDimensionClassifier()

    assert classifier.classify_state("anything", kind="class") == dc.StateType.STATEFUL
    assert classifier.classify_state("self.count += 1") == dc.StateType.STATEFUL
    assert classifier.classify_state("x = y + z") == dc.StateType.STATELESS


def test_regex_lifecycle_classification():
    classifier = dc.RegexDimensionClassifier()

    assert classifier.classify_lifecycle("__init__") == dc.LifecyclePhase.CREATE
    assert classifier.classify_lifecycle("cleanup") == dc.LifecyclePhase.DESTROY
    assert classifier.classify_lifecycle("process_order") == dc.LifecyclePhase.USE


def test_regex_layer_classification_priority_and_fallbacks():
    classifier = dc.RegexDimensionClassifier()

    # Name-based priority: test beats everything.
    assert (
        classifier.classify_layer("requests.get(url)", "test_service_handler")
        == dc.LayerType.TEST
    )
    assert (
        classifier.classify_layer("@app.get('/x')\npass", "RouteHandler")
        == dc.LayerType.INTERFACE
    )
    assert (
        classifier.classify_layer("obj.execute(sql)", "Repository")
        == dc.LayerType.INFRASTRUCTURE
    )
    assert (
        classifier.classify_layer("...", "Thing", "/my/app/services/use_case.py")
        == dc.LayerType.APPLICATION
    )
    assert (
        classifier.classify_layer("...", "Entity", "/my/app/domain/model.py")
        == dc.LayerType.CORE
    )
    assert classifier.classify_layer("...", "UnknownThing", "/tmp/other.py") == dc.LayerType.UNKNOWN


def test_dimension_classifier_prefers_tree_sitter_then_falls_back(monkeypatch):
    classifier = dc.DimensionClassifier()

    node = {
        "name": "__init__",
        "kind": "function",
        "body_source": "print('x')",
        "file_path": "app.py",
    }

    # Tree-sitter path: explicit values from ts classifier
    monkeypatch.setattr(
        classifier._ts_classifier,
        "classify_boundary",
        lambda source, language: dc.BoundaryType.OUTPUT,
    )
    monkeypatch.setattr(
        classifier._ts_classifier,
        "classify_state",
        lambda source, language: dc.StateType.STATEFUL,
    )
    monkeypatch.setattr(
        classifier._ts_classifier,
        "classify_lifecycle",
        lambda source, name, language: dc.LifecyclePhase.CREATE,
    )
    monkeypatch.setattr(
        classifier._ts_classifier,
        "classify_layer",
        lambda source, language: dc.LayerType.INTERFACE,
    )

    assert classifier.classify_boundary(node) == dc.BoundaryType.OUTPUT
    assert classifier.classify_state(node) == dc.StateType.STATEFUL
    assert classifier.classify_lifecycle(node) == dc.LifecyclePhase.CREATE
    assert classifier.classify_layer(node) == dc.LayerType.INTERFACE

    # Fallback path: ts returns None.
    monkeypatch.setattr(classifier._ts_classifier, "classify_boundary", lambda source, language: None)
    monkeypatch.setattr(classifier._ts_classifier, "classify_state", lambda source, language: None)
    monkeypatch.setattr(
        classifier._ts_classifier,
        "classify_lifecycle",
        lambda source, name, language: None,
    )
    monkeypatch.setattr(classifier._ts_classifier, "classify_layer", lambda source, language: None)

    assert classifier.classify_boundary({"body_source": "open(path).read()", "file_path": "x.py"}) == dc.BoundaryType.INPUT
    assert classifier.classify_state({"body_source": "x = y + z", "kind": "function"}) == dc.StateType.STATELESS
    assert classifier.classify_lifecycle({"name": "cleanup", "body_source": "..."}) == dc.LifecyclePhase.DESTROY
    assert classifier.classify_layer({"name": "Repository", "body_source": "..."}) == dc.LayerType.INFRASTRUCTURE


def test_intent_and_language_dimension_classification():
    classifier = dc.DimensionClassifier()

    assert (
        classifier.classify_intent({"name": "get_user", "docstring": "Get user by id"})
        == dc.IntentType.DOCUMENTED
    )
    assert (
        classifier.classify_intent({"name": "delete_user", "docstring": "Get user by id"})
        == dc.IntentType.CONTRADICTORY
    )
    assert classifier.classify_intent({"name": "x", "docstring": ""}) == dc.IntentType.AMBIGUOUS
    assert classifier.classify_intent({"name": "calculate_total"}) == dc.IntentType.IMPLICIT

    assert classifier.classify_language_dimension({"file_path": "a.py"}) == "Python"
    assert classifier.classify_language_dimension({"file_path": "component.tsx"}) == "TypeScriptReact"
    assert classifier.classify_language_dimension({"file_path": "README.abc"}) == "Abc"
    assert classifier.classify_language_dimension({}) == "Unknown"


def test_classify_all_dimensions_writes_flat_and_nested_fields(monkeypatch):
    monkeypatch.setattr(dc.DimensionClassifier, "classify_all", lambda self, node: {
        "boundary": "io",
        "state": "stateful",
        "lifecycle": "use",
        "intent": "Documented",
        "language": "Python",
    })

    nodes = [
        {"id": "a::f", "name": "f", "dimensions": {}},
        {"id": "a::g", "name": "g"},
    ]
    count = dc.classify_all_dimensions(nodes)

    assert count == 2
    for node in nodes:
        assert node["boundary"] == "io"
        assert node["state"] == "stateful"
        assert node["lifecycle"] == "use"
        assert node["intent"] == "Documented"
        assert node["language_dim"] == "Python"
        assert node["dimensions"]["D4_BOUNDARY"] == "io"
        assert node["dimensions"]["D5_STATE"] == "stateful"
        assert node["dimensions"]["D7_LIFECYCLE"] == "use"
        assert node["dimensions"]["D9_INTENT"] == "Documented"
        assert node["dimensions"]["D10_LANGUAGE"] == "Python"


def test_tree_sitter_role_and_layer_classification_with_mocked_captures(monkeypatch):
    ts = dc.TreeSitterDimensionClassifier()

    monkeypatch.setattr(ts, "_ensure_initialized", lambda language="python": True)
    ts._queries = {"roles": object(), "layer": object()}
    ts._parser = SimpleNamespace(parse=lambda _: SimpleNamespace(root_node=object()))

    monkeypatch.setattr(
        ts,
        "_run_query_with_details",
        lambda query_type, root_node, source: {
            "role.utility.function": ["utility_fn"],
            "role.repository.class": ["UserRepository"],
        },
    )
    role = ts.classify_role("class UserRepository: pass", language="python")
    assert role is not None
    # Repository should win by priority over utility.
    assert role["role"] == "Repository"
    assert role["confidence"] == dc.ROLE_CONFIDENCE["repository"]
    assert set(role["all_detected"]) == {"utility", "repository"}

    monkeypatch.setattr(
        ts,
        "_run_query",
        lambda query_type, root_node: {"layer.core.class", "layer.interface.route"},
    )
    layer = ts.classify_layer("@app.get('/x')\ndef x(): pass", language="python")
    assert layer == dc.LayerType.INTERFACE
