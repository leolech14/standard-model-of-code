"""Tests for the Temporal Analysis module (REH integration)."""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from temporal_analysis import (
    NOISE_DIRS,
    NOISE_EXTENSIONS,
    CODE_EXTENSIONS,
    CAPABILITY_PATTERNS,
    LANG_BY_EXT,
    GrowthSnapshot,
    Hotspot,
    CapabilityDelta,
    ChangeCouplingPair,
    TemporalAnalysisResult,
    _is_noise,
    _is_code_file,
    _is_git_repo,
    _run_git,
    _analyze_growth,
    _analyze_hotspots,
    _analyze_capability_drift,
    _analyze_age_distribution,
    _analyze_change_coupling,
    _analyze_contributors,
    compute_temporal_analysis,
)


# ── Constants ────────────────────────────────────────────────────────────


class TestConstants:
    def test_noise_dirs_contains_standard(self):
        assert ".git" in NOISE_DIRS
        assert "node_modules" in NOISE_DIRS
        assert "__pycache__" in NOISE_DIRS

    def test_code_extensions(self):
        assert ".py" in CODE_EXTENSIONS
        assert ".ts" in CODE_EXTENSIONS
        assert ".go" in CODE_EXTENSIONS

    def test_lang_by_ext_mapping(self):
        assert LANG_BY_EXT[".py"] == "python"
        assert LANG_BY_EXT[".tsx"] == "javascript"
        assert LANG_BY_EXT[".go"] == "go"

    def test_capability_patterns_python(self):
        pat = CAPABILITY_PATTERNS["python"]
        assert pat.match("def hello():")
        assert pat.match("async def hello():")
        assert pat.match("class Foo:")
        assert pat.match("  def indented():")
        assert not pat.match("# def comment():")

    def test_capability_patterns_javascript(self):
        pat = CAPABILITY_PATTERNS["javascript"]
        assert pat.match("function hello() {")
        assert pat.match("export class Foo {")
        assert pat.match("const handler = async (")

    def test_capability_patterns_go(self):
        pat = CAPABILITY_PATTERNS["go"]
        assert pat.match("func main() {")
        assert pat.match("func (s *Server) Start() {")
        assert pat.match("type Config struct {")


# ── Noise/code file detection ────────────────────────────────────────────


class TestFiltering:
    def test_is_noise_git_dir(self):
        assert _is_noise(".git/config")

    def test_is_noise_node_modules(self):
        assert _is_noise("node_modules/express/index.js")

    def test_is_noise_pycache(self):
        assert _is_noise("src/__pycache__/foo.pyc")

    def test_is_noise_extension(self):
        assert _is_noise("image.png")
        assert _is_noise("binary.so")

    def test_not_noise_python(self):
        assert not _is_noise("src/core/analysis.py")

    def test_is_code_file_python(self):
        assert _is_code_file("main.py")

    def test_is_code_file_typescript(self):
        assert _is_code_file("app.tsx")

    def test_not_code_file_image(self):
        assert not _is_code_file("photo.png")

    def test_not_code_file_binary(self):
        assert not _is_code_file("libfoo.so")


# ── Dataclass tests ──────────────────────────────────────────────────────


class TestDataclasses:
    def test_growth_snapshot_defaults(self):
        gs = GrowthSnapshot(date="2026-01-01")
        assert gs.commits == 0
        assert gs.files_born == 0

    def test_hotspot(self):
        h = Hotspot(path="main.py", change_count=42, last_changed="2026-03-01")
        assert h.change_count == 42

    def test_capability_delta(self):
        cd = CapabilityDelta(kind="function", name="foo", file="a.py", action="added")
        assert cd.action == "added"

    def test_change_coupling_pair(self):
        cp = ChangeCouplingPair(file_a="a.py", file_b="b.py", co_change_count=7)
        assert cp.co_change_count == 7

    def test_result_default_unavailable(self):
        r = TemporalAnalysisResult()
        assert r.available is False
        assert r.total_commits == 0

    def test_result_to_dict(self):
        r = TemporalAnalysisResult(available=True, total_commits=100)
        d = r.to_dict()
        assert d['available'] is True
        assert d['total_commits'] == 100

    def test_result_to_dict_trims_long_timeline(self):
        timeline = [GrowthSnapshot(date=f"2026-01-{i:02d}") for i in range(1, 80)]
        r = TemporalAnalysisResult(growth_timeline=timeline)
        d = r.to_dict()
        assert len(d['growth_timeline']) == 60  # trimmed to 60


# ── Git helper tests ─────────────────────────────────────────────────────


class TestRunGit:
    def test_run_git_nonexistent_dir(self):
        ok, msg = _run_git("/nonexistent/path/xyz", ["status"])
        assert not ok

    @patch("temporal_analysis.subprocess.run")
    def test_run_git_timeout(self, mock_run):
        import subprocess as sp
        mock_run.side_effect = sp.TimeoutExpired(cmd="git", timeout=30)
        ok, msg = _run_git("/tmp", ["log"])
        assert not ok
        assert "timed out" in msg.lower()

    @patch("temporal_analysis.subprocess.run")
    def test_run_git_success(self, mock_run):
        mock_run.return_value = type("R", (), {
            "returncode": 0,
            "stdout": "hello world",
        })()
        ok, output = _run_git("/tmp", ["status"])
        assert ok
        assert output == "hello world"

    @patch("temporal_analysis.subprocess.run")
    def test_run_git_output_capped(self, mock_run):
        mock_run.return_value = type("R", (), {
            "returncode": 0,
            "stdout": "x" * 1000,
        })()
        ok, output = _run_git("/tmp", ["log"], max_output=100)
        assert ok
        assert len(output) == 100


class TestIsGitRepo:
    @patch("temporal_analysis.os.path.isdir")
    def test_with_git_dir(self, mock_isdir):
        mock_isdir.return_value = True
        assert _is_git_repo("/some/repo")

    @patch("temporal_analysis._run_git")
    @patch("temporal_analysis.os.path.isdir")
    def test_worktree_fallback(self, mock_isdir, mock_git):
        mock_isdir.return_value = False
        mock_git.return_value = (True, ".git")
        assert _is_git_repo("/some/worktree")

    @patch("temporal_analysis._run_git")
    @patch("temporal_analysis.os.path.isdir")
    def test_not_a_repo(self, mock_isdir, mock_git):
        mock_isdir.return_value = False
        mock_git.return_value = (False, "fatal")
        assert not _is_git_repo("/not/a/repo")


# ── Growth analysis ──────────────────────────────────────────────────────


class TestAnalyzeGrowth:
    @patch("temporal_analysis._run_git")
    def test_basic_growth(self, mock_git):
        def side_effect(repo, args, **kwargs):
            if "--diff-filter=A" in args:
                return True, (
                    "2026-01-01\n"
                    "src/main.py\n"
                    "\n"
                    "2026-01-02\n"
                    "src/utils.py\n"
                )
            else:
                return True, (
                    "2026-01-01\n"
                    "2026-01-01\n"
                    "2026-01-01\n"
                    "2026-01-02\n"
                    "2026-01-02\n"
                )
        mock_git.side_effect = side_effect

        timeline, total_c, total_b, first, last = _analyze_growth("/repo")
        assert total_c == 5
        assert total_b == 2
        assert first == "2026-01-01"
        assert last == "2026-01-02"
        assert len(timeline) == 2
        assert timeline[0].commits == 3
        assert timeline[1].files_born == 1

    @patch("temporal_analysis._run_git")
    def test_empty_repo(self, mock_git):
        mock_git.return_value = (True, "")
        timeline, total_c, total_b, first, last = _analyze_growth("/repo")
        assert timeline == []
        assert total_c == 0

    @patch("temporal_analysis._run_git")
    def test_git_failure(self, mock_git):
        mock_git.return_value = (False, "error")
        timeline, total_c, total_b, first, last = _analyze_growth("/repo")
        assert timeline == []

    @patch("temporal_analysis._run_git")
    def test_noise_filtered(self, mock_git):
        def side_effect(repo, args, **kwargs):
            if "--diff-filter=A" in args:
                return True, (
                    "2026-01-01\n"
                    "node_modules/express/index.js\n"
                    "src/main.py\n"
                    "__pycache__/foo.pyc\n"
                )
            else:
                return True, "2026-01-01\n"
        mock_git.side_effect = side_effect

        timeline, _, total_b, _, _ = _analyze_growth("/repo")
        assert total_b == 1  # only src/main.py counts


# ── Hotspot analysis ─────────────────────────────────────────────────────


class TestAnalyzeHotspots:
    @patch("temporal_analysis._run_git")
    def test_basic_hotspots(self, mock_git):
        call_count = [0]
        def side_effect(repo, args, **kwargs):
            if args[0] == "log" and "--name-only" in args:
                return True, (
                    "src/main.py\n"
                    "src/main.py\n"
                    "src/main.py\n"
                    "src/utils.py\n"
                    "src/utils.py\n"
                )
            elif args[0] == "log" and "-1" in args:
                return True, "2026-03-01"
            return True, ""
        mock_git.side_effect = side_effect

        hotspots = _analyze_hotspots("/repo", top_n=5)
        assert len(hotspots) == 2
        assert hotspots[0].path == "src/main.py"
        assert hotspots[0].change_count == 3

    @patch("temporal_analysis._run_git")
    def test_noise_filtered(self, mock_git):
        def side_effect(repo, args, **kwargs):
            if "--name-only" in args:
                return True, "node_modules/x.js\nsrc/a.py\n"
            return True, "2026-01-01"
        mock_git.side_effect = side_effect

        hotspots = _analyze_hotspots("/repo")
        assert len(hotspots) == 1
        assert hotspots[0].path == "src/a.py"


# ── Capability drift ─────────────────────────────────────────────────────


class TestAnalyzeCapabilityDrift:
    @patch("temporal_analysis._run_git")
    def test_added_function(self, mock_git):
        mock_git.return_value = (True, (
            "diff --git a/x.py b/x.py\n"
            "+def new_function():\n"
            "+    pass\n"
        ))
        added, removed, modified = _analyze_capability_drift("/repo")
        assert len(added) == 1
        assert added[0].name == "new_function"
        assert added[0].action == "added"
        assert len(removed) == 0

    @patch("temporal_analysis._run_git")
    def test_removed_class(self, mock_git):
        mock_git.return_value = (True, (
            "diff --git a/x.py b/x.py\n"
            "-class OldService:\n"
            "-    pass\n"
        ))
        added, removed, modified = _analyze_capability_drift("/repo")
        assert len(removed) == 1
        assert removed[0].name == "OldService"
        assert removed[0].kind == "class"

    @patch("temporal_analysis._run_git")
    def test_modified_function(self, mock_git):
        mock_git.return_value = (True, (
            "diff --git a/x.py b/x.py\n"
            "-def handler():\n"
            "+def handler():\n"
        ))
        added, removed, modified = _analyze_capability_drift("/repo")
        # Same name added AND removed = modified
        assert len(added) == 0
        assert len(removed) == 0
        assert modified == 1

    @patch("temporal_analysis._run_git")
    def test_fallback_on_shallow_clone(self, mock_git):
        calls = []
        def side_effect(repo, args, **kwargs):
            calls.append(args)
            if "HEAD~10..HEAD" in " ".join(args):
                return False, "fatal: bad revision"
            return True, "+def fallback():\n"
        mock_git.side_effect = side_effect

        added, removed, modified = _analyze_capability_drift("/repo")
        # Should have retried with smaller ref
        assert len(calls) > 1

    @patch("temporal_analysis._run_git")
    def test_javascript_detection(self, mock_git):
        mock_git.return_value = (True, (
            "diff --git a/app.ts b/app.ts\n"
            "+export class AppController {\n"
        ))
        added, _, _ = _analyze_capability_drift("/repo")
        assert len(added) == 1
        assert added[0].name == "AppController"


# ── Age distribution ─────────────────────────────────────────────────────


class TestAnalyzeAgeDistribution:
    @patch("temporal_analysis._run_git")
    def test_basic_age(self, mock_git):
        now = time.time()
        three_days_ago = str(int(now - 3 * 86400))
        thirty_days_ago = str(int(now - 30 * 86400))
        year_ago = str(int(now - 400 * 86400))

        mock_git.return_value = (True, (
            f"{three_days_ago}\nsrc/new.py\n\n"
            f"{thirty_days_ago}\nsrc/mid.py\n\n"
            f"{year_ago}\nsrc/old.py\n"
        ))

        buckets, median = _analyze_age_distribution("/repo")
        assert buckets["< 7 days"] == 1
        assert buckets["30-90 days"] == 1
        assert buckets["> 365 days"] == 1
        assert median > 0

    @patch("temporal_analysis._run_git")
    def test_empty(self, mock_git):
        mock_git.return_value = (True, "")
        buckets, median = _analyze_age_distribution("/repo")
        assert buckets == {}
        assert median == 0.0


# ── Change coupling ──────────────────────────────────────────────────────


class TestAnalyzeChangeCoupling:
    @patch("temporal_analysis._run_git")
    def test_basic_coupling(self, mock_git):
        mock_git.return_value = (True, (
            "COMMIT_SEP\n"
            "src/a.py\n"
            "src/b.py\n"
            "COMMIT_SEP\n"
            "src/a.py\n"
            "src/b.py\n"
            "COMMIT_SEP\n"
            "src/a.py\n"
            "src/b.py\n"
            "COMMIT_SEP\n"
            "src/a.py\n"
            "src/c.py\n"
        ))
        pairs = _analyze_change_coupling("/repo", min_co_changes=3)
        assert len(pairs) == 1
        assert pairs[0].file_a == "src/a.py"
        assert pairs[0].file_b == "src/b.py"
        assert pairs[0].co_change_count == 3

    @patch("temporal_analysis._run_git")
    def test_merge_bomb_filtered(self, mock_git):
        """Commits with >15 files are ignored (likely merges)."""
        files = "\n".join([f"src/f{i}.py" for i in range(20)])
        mock_git.return_value = (True, f"COMMIT_SEP\n{files}\n")
        pairs = _analyze_change_coupling("/repo", min_co_changes=1)
        assert len(pairs) == 0

    @patch("temporal_analysis._run_git")
    def test_noise_excluded(self, mock_git):
        mock_git.return_value = (True, (
            "COMMIT_SEP\n"
            "node_modules/x.js\n"
            "src/a.py\n"
            "COMMIT_SEP\n"
            "node_modules/x.js\n"
            "src/a.py\n"
            "COMMIT_SEP\n"
            "node_modules/x.js\n"
            "src/a.py\n"
        ))
        pairs = _analyze_change_coupling("/repo", min_co_changes=1)
        # Only 1 code file per commit after filtering, no pairs
        assert len(pairs) == 0


# ── Contributors ─────────────────────────────────────────────────────────


class TestAnalyzeContributors:
    @patch("temporal_analysis._run_git")
    def test_basic_contributors(self, mock_git):
        mock_git.return_value = (True, (
            "   150\tAlice\n"
            "    50\tBob\n"
            "    10\tCharlie\n"
        ))
        bus, contribs = _analyze_contributors("/repo")
        assert bus == 3
        assert len(contribs) == 3
        assert contribs[0]["name"] == "Alice"
        assert contribs[0]["commits"] == 150

    @patch("temporal_analysis._run_git")
    def test_single_contributor(self, mock_git):
        mock_git.return_value = (True, "   200\tSolo Dev\n")
        bus, contribs = _analyze_contributors("/repo")
        assert bus == 1


# ── Main entry point ─────────────────────────────────────────────────────


class TestComputeTemporalAnalysis:
    def test_no_repo_path(self):
        result = compute_temporal_analysis({})
        assert result.available is False
        assert "no repo path" in result.error

    def test_repo_path_from_metadata(self):
        with patch("temporal_analysis._is_git_repo", return_value=False):
            result = compute_temporal_analysis({
                "metadata": {"target_path": "/some/non/repo"}
            })
            assert result.available is False
            assert "not a git repository" in result.error

    def test_explicit_repo_path(self):
        with patch("temporal_analysis._is_git_repo", return_value=False):
            result = compute_temporal_analysis({}, repo_path="/not/a/repo")
            assert result.available is False

    @patch("temporal_analysis._analyze_contributors")
    @patch("temporal_analysis._analyze_change_coupling")
    @patch("temporal_analysis._analyze_age_distribution")
    @patch("temporal_analysis._analyze_capability_drift")
    @patch("temporal_analysis._analyze_hotspots")
    @patch("temporal_analysis._analyze_growth")
    @patch("temporal_analysis._is_git_repo")
    def test_full_pipeline(
        self, mock_is_git, mock_growth, mock_hotspots,
        mock_drift, mock_age, mock_coupling, mock_contribs,
    ):
        mock_is_git.return_value = True
        mock_growth.return_value = (
            [GrowthSnapshot("2026-01-01", 5, 2)],
            100, 50, "2025-01-01", "2026-01-01",
        )
        mock_hotspots.return_value = [
            Hotspot("main.py", 42, "2026-01-01"),
        ]
        mock_drift.return_value = (
            [CapabilityDelta("function", "new_fn", "a.py", "added")],
            [CapabilityDelta("class", "OldClass", "b.py", "removed")],
            3,
        )
        mock_age.return_value = ({"< 7 days": 5, "> 365 days": 10}, 120.5)
        mock_coupling.return_value = [
            ChangeCouplingPair("a.py", "b.py", 8),
        ]
        mock_contribs.return_value = (2, [
            {"name": "Alice", "commits": 70},
            {"name": "Bob", "commits": 30},
        ])

        full_output = {"node_count": 50, "metadata": {"target_path": "/repo"}}
        result = compute_temporal_analysis(full_output, repo_path="/repo")

        assert result.available is True
        assert result.total_commits == 100
        assert result.total_files_born == 50
        assert result.active_days == 1
        assert len(result.hotspots) == 1
        assert len(result.capabilities_added) == 1
        assert len(result.capabilities_removed) == 1
        assert result.capabilities_modified == 3
        assert result.median_age_days == 120.5
        assert len(result.change_coupling) == 1
        assert result.bus_factor == 2
        assert result.churn_rate > 0  # 42 changes / 50 files

    @patch("temporal_analysis._analyze_contributors")
    @patch("temporal_analysis._analyze_change_coupling")
    @patch("temporal_analysis._analyze_age_distribution")
    @patch("temporal_analysis._analyze_capability_drift")
    @patch("temporal_analysis._analyze_hotspots")
    @patch("temporal_analysis._analyze_growth")
    @patch("temporal_analysis._is_git_repo")
    def test_churn_rate_zero_files(
        self, mock_is_git, mock_growth, mock_hotspots,
        mock_drift, mock_age, mock_coupling, mock_contribs,
    ):
        mock_is_git.return_value = True
        mock_growth.return_value = ([], 0, 0, "", "")
        mock_hotspots.return_value = []
        mock_drift.return_value = ([], [], 0)
        mock_age.return_value = ({}, 0.0)
        mock_coupling.return_value = []
        mock_contribs.return_value = (0, [])

        result = compute_temporal_analysis(
            {"node_count": 0}, repo_path="/repo"
        )
        assert result.available is True
        assert result.churn_rate == 0.0

    def test_to_dict_serializable(self):
        """Verify the full result is JSON-serializable."""
        import json
        r = TemporalAnalysisResult(
            available=True,
            total_commits=10,
            hotspots=[Hotspot("a.py", 5, "2026-01-01")],
            change_coupling=[ChangeCouplingPair("a.py", "b.py", 3)],
        )
        d = r.to_dict()
        serialized = json.dumps(d)
        assert '"available": true' in serialized
