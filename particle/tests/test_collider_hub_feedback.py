import json
from pathlib import Path

import src.core.collider_hub as hub


def _init_git_repo_layout(repo: Path) -> None:
    (repo / ".git" / "info").mkdir(parents=True, exist_ok=True)


def _write_output_bundle(output_dir: Path, unified: dict, insights: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "unified_analysis.json").write_text(json.dumps(unified), encoding="utf-8")
    (output_dir / "collider_insights.json").write_text(json.dumps(insights), encoding="utf-8")
    (output_dir / "collider.db").write_bytes(b"db")


def test_ensure_local_ignore_registers_reh_pattern(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)

    reh_dir = repo / ".reh"
    hub._ensure_local_ignore(repo, reh_dir)

    exclude_text = (repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert ".reh/" in exclude_text
    assert (reh_dir / ".gitignore").exists()


def test_build_auto_feedback_flags_negative_performance_signals(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)
    output_dir = repo / ".collider"

    _write_output_bundle(
        output_dir=output_dir,
        unified={
            "nodes": [{"id": "a"}],
            "edges": [{"source": "a", "target": "b"}],
            "performance": {"total_estimated_cost": -123, "time_by_type": {"tau_compute": -2}},
        },
        insights={
            "grade": "C",
            "health_score": 6.3,
            "findings_by_severity": {"critical": 1},
            "findings": [{"severity": "critical", "title": "Invalid performance totals"}],
            "mission_matrix": {"performance": {"status": "fail", "notes": ["negative totals"]}},
        },
    )

    feedback = hub._build_auto_feedback(repo=repo, output_dir=output_dir, run_mode="full")
    issue_titles = [issue.get("title", "") for issue in feedback["issues"]]

    assert feedback["issue_count"] > 0
    assert any("Negative performance values" in title for title in issue_titles)


def test_generate_feedback_bundle_writes_latest_reh_artifacts(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)
    output_dir = repo / ".collider"
    reh_dir = repo / ".reh"

    _write_output_bundle(
        output_dir=output_dir,
        unified={
            "nodes": [{"id": "a"}],
            "edges": [{"source": "a", "target": "b"}],
            "performance": {"total_estimated_cost": 10},
        },
        insights={
            "grade": "B",
            "health_score": 8.0,
            "findings_by_severity": {"critical": 0, "high": 1},
            "findings": [{"severity": "high", "title": "Example finding"}],
        },
    )

    monkeypatch.setattr(hub, "_resolve_ecoroot", lambda _repo: None)
    monkeypatch.setattr(hub, "_INNER_FEEDBACK_ROOT", tmp_path / "inner_feedback")

    result = hub._generate_feedback_bundle(
        repo=repo,
        output_dir=output_dir,
        reh_dir=reh_dir,
        run_mode="feedback-only",
        llm_model="qwen2.5:7b-instruct",
        llm_timeout_sec=1,
        skip_llm=True,
    )

    assert Path(result["latest_auto_feedback_json"]).exists()
    assert Path(result["latest_ai_user_audit_md"]).exists()
    assert Path(result["latest_rehport_json"]).exists()
    assert result["llm_meta"]["provider"] == "deterministic"
