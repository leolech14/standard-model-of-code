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


def test_ensure_local_ignore_registers_feedback_pattern(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)

    feedback_dir = repo / ".collider" / "feedback"
    hub._ensure_local_ignore(repo, feedback_dir)

    exclude_text = (repo / ".git" / "info" / "exclude").read_text(encoding="utf-8")
    assert ".collider/feedback/" in exclude_text
    assert (feedback_dir / ".gitignore").exists()


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


def test_generate_feedback_bundle_writes_latest_feedback_artifacts(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)
    output_dir = repo / ".collider"
    feedback_dir = repo / ".collider" / "feedback"

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

    monkeypatch.setattr(hub, "_CENTRAL_FEEDBACK_ROOT", tmp_path / "central_feedback")

    result = hub._generate_feedback_bundle(
        repo=repo,
        output_dir=output_dir,
        feedback_dir=feedback_dir,
        run_mode="feedback-only",
        llm_model="qwen2.5:7b-instruct",
        llm_timeout_sec=1,
        skip_llm=True,
    )

    assert Path(result["latest_auto_feedback_json"]).exists()
    assert Path(result["latest_ai_user_audit_md"]).exists()
    assert Path(result["latest_feedback_report_json"]).exists()
    assert result["llm_meta"]["provider"] == "deterministic"


def test_feedback_sync_targets_single_project_elements_folder(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo_layout(repo)
    output_dir = repo / ".collider"
    feedback_dir = repo / ".collider" / "feedback"

    _write_output_bundle(
        output_dir=output_dir,
        unified={"nodes": [{"id": "a"}], "edges": [{"source": "a", "target": "b"}]},
        insights={"grade": "B", "health_score": 8.0, "findings_by_severity": {}},
    )

    central = tmp_path / "project_elements_feedback_single"
    monkeypatch.setattr(hub, "_CENTRAL_FEEDBACK_ROOT", central)

    result = hub._generate_feedback_bundle(
        repo=repo,
        output_dir=output_dir,
        feedback_dir=feedback_dir,
        run_mode="feedback-only",
        llm_model="qwen2.5:7b-instruct",
        llm_timeout_sec=1,
        skip_llm=True,
    )

    synced = result.get("synced", {})
    central_paths = synced.get("central", [])
    assert len(central_paths) == 3
    assert all(str(path).startswith(str(central)) for path in central_paths)


def test_build_full_cmd_ecosystem_profile_excludes_repo_archives(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    output_dir = tmp_path / "analysis"

    cmd = hub._build_full_cmd(
        collider_bin="collider",
        repo=repo,
        output_dir=output_dir,
        profile="ecosystem",
        no_default_excludes=False,
        extra_excludes=[],
        passthrough=[],
        html=False,
        no_timing=False,
    )

    excludes = [
        cmd[idx + 1]
        for idx, token in enumerate(cmd[:-1])
        if token == "--exclude"
    ]

    assert ".claude/worktrees" in excludes
    assert ".agent/intelligence" in excludes
    assert "research/gemini" in excludes
    assert "research/perplexity" in excludes
    assert "wave/intelligence" in excludes
