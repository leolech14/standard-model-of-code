from src.core.performance_predictor import predict_performance


def test_predictor_clamps_negative_loc_and_complexity():
    nodes = [
        {
            "id": "svc:bad",
            "name": "bad_service",
            "role": "Service",
            "lines_of_code": -42,
            "complexity": -9,
        }
    ]

    profile = predict_performance(nodes)
    node = profile.nodes["svc:bad"]

    assert node.lines_of_code == 1
    assert node.complexity == 1
    assert node.estimated_cost >= 0
    assert profile.total_estimated_cost >= 0


def test_predictor_handles_non_numeric_metrics_without_negative_totals():
    nodes = [
        {
            "id": "api:handler",
            "name": "http_handler",
            "role": "API",
            "lines_of_code": "not-a-number",
            "complexity": None,
        },
        {
            "id": "repo:query",
            "name": "query_store",
            "role": "Repository",
            "lines_of_code": "-12",
            "complexity": "7",
        },
    ]

    profile = predict_performance(nodes)

    assert profile.total_estimated_cost >= 0
    assert all(node.estimated_cost >= 0 for node in profile.nodes.values())
