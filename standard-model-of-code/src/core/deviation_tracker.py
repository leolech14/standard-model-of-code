"""
Deviation Tracker - Traces concordance deviations to their source.

PURPOSE: When code and docs diverge (discordance), identify:
  1. WHERE - Exact file:line of the deviation
  2. WHEN - Git commit that introduced the drift
  3. WHO - Author responsible
  4. WHY - Commit message (intent)

States tracked:
  - UNVOICED: Code exists without documentation
  - UNREALIZED: Documentation exists without code
  - DISCORDANT: Both exist but purposes conflict

Usage:
    tracker = DeviationTracker(repo_path)
    deviations = tracker.trace_all(symmetry_report)
    for dev in deviations:
        print(f"{dev.state} {dev.symbol} @ {dev.location}")
        print(f"  Introduced: {dev.commit_sha[:8]} by {dev.author}")
"""
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict
import json
import re


@dataclass
class SourceLocation:
    """Pinpoints a deviation in the codebase."""
    file_path: str
    line_number: int = 0
    column: int = 0
    context: str = ""  # Surrounding code/doc snippet

    def __str__(self) -> str:
        if self.line_number:
            return f"{self.file_path}:{self.line_number}"
        return self.file_path


@dataclass
class GitBlame:
    """Git attribution for a deviation."""
    commit_sha: str
    author: str
    author_email: str
    timestamp: datetime
    commit_message: str

    def to_dict(self) -> dict:
        return {
            "commit": self.commit_sha,
            "author": self.author,
            "email": self.author_email,
            "date": self.timestamp.isoformat(),
            "message": self.commit_message
        }


@dataclass
class MistakeEvidence:
    """Evidence supporting the diagnosis of a mistake."""
    diagnosis: str                    # What went wrong
    confidence: str                   # HIGH, MEDIUM, LOW
    evidence_type: str                # DIFF, HISTORY, INFERENCE
    details: str                      # Supporting evidence
    commit_added_code: bool = False   # Did this commit add the code?
    commit_touched_docs: bool = False # Did this commit touch docs?
    docs_existed_before: bool = False # Did docs exist before this commit?
    code_existed_before: bool = False # Did code exist before this commit?


def diagnose_mistake(state: str, blame: Optional["GitBlame"], symbol: str,
                     evidence: Optional[MistakeEvidence] = None) -> str:
    """
    Analyze the deviation and explain what went wrong.

    Returns a human-readable explanation of the mistake.
    """
    if evidence:
        # We have hard evidence from git analysis
        return f"{evidence.diagnosis} [{evidence.confidence} confidence, {evidence.evidence_type}]"

    if not blame:
        return f"Unknown origin - no git history available for {symbol}"

    # Fallback to commit message heuristics (LOW confidence)
    msg = blame.commit_message.lower()

    if state == "UNVOICED":
        # Code exists without documentation
        if any(kw in msg for kw in ["feat", "add", "implement", "create", "new"]):
            return f"[INFERRED] Feature added without docs. Commit '{blame.commit_message[:40]}' suggests new code."
        elif any(kw in msg for kw in ["refactor", "move", "rename", "reorganize"]):
            return f"[INFERRED] Refactoring may have broken doc links. Commit suggests restructuring."
        elif any(kw in msg for kw in ["fix", "bug", "patch", "hotfix"]):
            return f"[INFERRED] Bug fix may have added undocumented code."
        else:
            return f"[INFERRED] Code exists without docs. Cause unclear from commit message alone."

    elif state == "UNREALIZED":
        # Documentation exists without code
        if any(kw in msg for kw in ["doc", "readme", "spec", "plan"]):
            return f"[INFERRED] Docs written before implementation. Spec may never have been built."
        elif any(kw in msg for kw in ["delete", "remove", "deprecate", "drop"]):
            return f"[INFERRED] Code may have been removed without updating docs."
        else:
            return f"[INFERRED] Docs reference missing code. Either never built or removed."

    elif state == "DISCORDANT":
        return f"[INFERRED] Code and docs exist but may describe different purposes."

    return f"[INFERRED] Deviation detected but cause unclear from available evidence."


@dataclass
class Deviation:
    """A traced concordance deviation."""
    symbol: str                    # The symbol/reference name
    state: str                     # UNVOICED, UNREALIZED, DISCORDANT
    location: SourceLocation       # Where in the codebase
    blame: Optional[GitBlame]      # Who/when introduced it
    confidence: float = 1.0        # How certain we are
    suggested_action: str = ""     # What to do about it
    diagnosis: str = ""            # Explanation of what went wrong

    def __post_init__(self):
        if not self.diagnosis:
            self.diagnosis = diagnose_mistake(self.state, self.blame, self.symbol)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "state": self.state,
            "diagnosis": self.diagnosis,
            "location": str(self.location),
            "file": self.location.file_path,
            "line": self.location.line_number,
            "blame": self.blame.to_dict() if self.blame else None,
            "confidence": self.confidence,
            "action": self.suggested_action
        }


@dataclass
class DeviationReport:
    """Complete deviation analysis with source tracing."""
    timestamp: str
    total_deviations: int
    by_state: Dict[str, int]
    by_author: Dict[str, int]
    deviations: List[Deviation]
    oldest_deviation: Optional[Deviation] = None
    newest_deviation: Optional[Deviation] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total": self.total_deviations,
                "by_state": self.by_state,
                "by_author": self.by_author
            },
            "oldest": self.oldest_deviation.to_dict() if self.oldest_deviation else None,
            "newest": self.newest_deviation.to_dict() if self.newest_deviation else None,
            "deviations": [d.to_dict() for d in self.deviations]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


class DeviationTracker:
    """Traces concordance deviations to their git source."""

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self._git_available = self._check_git()

    def _check_git(self) -> bool:
        """Check if git is available and repo is valid."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _git_blame_line(self, file_path: str, line_number: int) -> Optional[GitBlame]:
        """Get git blame for a specific line."""
        if not self._git_available or line_number <= 0:
            return None

        try:
            # Use porcelain format for parsing
            result = subprocess.run(
                ["git", "blame", "-L", f"{line_number},{line_number}",
                 "--porcelain", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            lines = result.stdout.strip().split('\n')
            if not lines:
                return None

            # Parse porcelain output
            commit_sha = lines[0].split()[0]
            author = ""
            author_email = ""
            timestamp = datetime.now()

            for line in lines[1:]:
                if line.startswith("author "):
                    author = line[7:]
                elif line.startswith("author-mail "):
                    author_email = line[12:].strip("<>")
                elif line.startswith("author-time "):
                    ts = int(line[12:])
                    timestamp = datetime.fromtimestamp(ts)

            # Get commit message
            msg_result = subprocess.run(
                ["git", "log", "-1", "--format=%s", commit_sha],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            commit_message = msg_result.stdout.strip() if msg_result.returncode == 0 else ""

            return GitBlame(
                commit_sha=commit_sha,
                author=author,
                author_email=author_email,
                timestamp=timestamp,
                commit_message=commit_message
            )

        except Exception:
            return None

    def _analyze_commit_evidence(self, commit_sha: str, file_path: str,
                                   symbol: str, state: str) -> Optional[MistakeEvidence]:
        """
        Analyze git diff to get HARD EVIDENCE of what happened.

        This looks at the actual commit to determine:
        1. Did this commit ADD the code/docs?
        2. Did this commit touch BOTH code and docs?
        3. What files were changed?
        """
        if not self._git_available:
            return None

        try:
            # Get list of files changed in this commit
            result = subprocess.run(
                ["git", "show", "--name-status", "--format=", commit_sha],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            changed_files = result.stdout.strip().split('\n')

            code_files_changed = []
            doc_files_changed = []

            for line in changed_files:
                if not line.strip():
                    continue
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                status, filepath = parts[0], parts[1]

                if filepath.endswith(('.py', '.js', '.ts', '.go', '.rs')):
                    code_files_changed.append((status, filepath))
                elif filepath.endswith(('.md', '.rst', '.txt')) or 'doc' in filepath.lower():
                    doc_files_changed.append((status, filepath))

            # Analyze the evidence
            commit_added_code = any(s in ('A', 'M') for s, _ in code_files_changed)
            commit_touched_docs = len(doc_files_changed) > 0

            # Determine diagnosis based on EVIDENCE
            if state == "UNVOICED":
                if commit_added_code and not commit_touched_docs:
                    return MistakeEvidence(
                        diagnosis=f"Code added in {commit_sha[:8]} without documentation update",
                        confidence="HIGH",
                        evidence_type="DIFF",
                        details=f"Commit modified {len(code_files_changed)} code files, 0 doc files",
                        commit_added_code=True,
                        commit_touched_docs=False
                    )
                elif commit_added_code and commit_touched_docs:
                    return MistakeEvidence(
                        diagnosis=f"Code and docs both changed, but symbol not documented",
                        confidence="MEDIUM",
                        evidence_type="DIFF",
                        details=f"Commit touched docs but missed this symbol",
                        commit_added_code=True,
                        commit_touched_docs=True
                    )

            elif state == "UNREALIZED":
                if commit_touched_docs and not commit_added_code:
                    return MistakeEvidence(
                        diagnosis=f"Documentation added in {commit_sha[:8]} without corresponding code",
                        confidence="HIGH",
                        evidence_type="DIFF",
                        details=f"Commit modified {len(doc_files_changed)} doc files, 0 code files",
                        commit_added_code=False,
                        commit_touched_docs=True
                    )

            return None

        except Exception:
            return None

    def _git_log_file(self, file_path: str) -> Optional[GitBlame]:
        """Get the last modification info for a file."""
        if not self._git_available:
            return None

        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ae|%at|%s", "--", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0 or not result.stdout.strip():
                return None

            parts = result.stdout.strip().split("|", 4)
            if len(parts) < 5:
                return None

            return GitBlame(
                commit_sha=parts[0],
                author=parts[1],
                author_email=parts[2],
                timestamp=datetime.fromtimestamp(int(parts[3])),
                commit_message=parts[4]
            )

        except Exception:
            return None

    def _find_symbol_location(self, symbol: str, search_code: bool = True) -> Optional[SourceLocation]:
        """Find where a symbol is defined/referenced."""
        # Extract the simple name from qualified path
        parts = symbol.split(".")
        simple_name = parts[-1]

        # Determine search path based on symbol structure
        if search_code:
            # Search in Python files
            search_patterns = ["*.py"]
            search_dir = self.repo_path / "src"
            if not search_dir.exists():
                search_dir = self.repo_path
        else:
            # Search in documentation
            search_patterns = ["*.md"]
            search_dir = self.repo_path / "docs"
            if not search_dir.exists():
                search_dir = self.repo_path

        for pattern in search_patterns:
            for file_path in search_dir.rglob(pattern):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')

                    for i, line in enumerate(lines, 1):
                        # Look for definition patterns
                        if search_code:
                            # Python: def func, class Cls, CONST =
                            if re.search(rf'\b(def|class)\s+{re.escape(simple_name)}\b', line):
                                return SourceLocation(
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=i,
                                    context=line.strip()[:100]
                                )
                            if re.match(rf'^{re.escape(simple_name)}\s*=', line):
                                return SourceLocation(
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=i,
                                    context=line.strip()[:100]
                                )
                        else:
                            # Markdown: mentions in code blocks or headers
                            if simple_name in line:
                                return SourceLocation(
                                    file_path=str(file_path.relative_to(self.repo_path)),
                                    line_number=i,
                                    context=line.strip()[:100]
                                )
                except Exception:
                    continue

        return None

    def trace_unvoiced(self, symbol: str) -> Deviation:
        """Trace an UNVOICED deviation (code without docs)."""
        location = self._find_symbol_location(symbol, search_code=True)

        if not location:
            location = SourceLocation(file_path="unknown", context=f"Symbol: {symbol}")

        blame = None
        evidence = None

        if location.line_number > 0:
            blame = self._git_blame_line(location.file_path, location.line_number)
        elif location.file_path != "unknown":
            blame = self._git_log_file(location.file_path)

        # Get HARD EVIDENCE from git diff
        if blame:
            evidence = self._analyze_commit_evidence(
                blame.commit_sha, location.file_path, symbol, "UNVOICED"
            )

        diagnosis = diagnose_mistake("UNVOICED", blame, symbol, evidence)

        return Deviation(
            symbol=symbol,
            state="UNVOICED",
            location=location,
            blame=blame,
            suggested_action=f"Add documentation for {symbol} in docs/",
            diagnosis=diagnosis
        )

    def trace_unrealized(self, symbol: str) -> Deviation:
        """Trace an UNREALIZED deviation (docs without code)."""
        location = self._find_symbol_location(symbol, search_code=False)

        if not location:
            location = SourceLocation(file_path="unknown", context=f"Reference: {symbol}")

        blame = None
        evidence = None

        if location.line_number > 0:
            blame = self._git_blame_line(location.file_path, location.line_number)
        elif location.file_path != "unknown":
            blame = self._git_log_file(location.file_path)

        # Get HARD EVIDENCE from git diff
        if blame:
            evidence = self._analyze_commit_evidence(
                blame.commit_sha, location.file_path, symbol, "UNREALIZED"
            )

        diagnosis = diagnose_mistake("UNREALIZED", blame, symbol, evidence)

        return Deviation(
            symbol=symbol,
            state="UNREALIZED",
            location=location,
            blame=blame,
            suggested_action=f"Implement {symbol} or remove from documentation",
            diagnosis=diagnosis
        )

    def trace_from_symmetry_report(self, report_dict: dict) -> DeviationReport:
        """
        Trace all deviations from a SymmetryReport.

        Args:
            report_dict: Output from SymmetryReport.to_dict()
        """
        deviations = []

        # Trace undocumented (UNVOICED)
        undocumented = report_dict.get("top_offenders", {}).get("undocumented", [])
        for symbol in undocumented:
            dev = self.trace_unvoiced(symbol)
            deviations.append(dev)

        # Trace orphan docs (UNREALIZED)
        orphan_docs = report_dict.get("top_offenders", {}).get("orphan_docs", [])
        for symbol in orphan_docs:
            dev = self.trace_unrealized(symbol)
            deviations.append(dev)

        # Count by state
        by_state = {}
        for dev in deviations:
            by_state[dev.state] = by_state.get(dev.state, 0) + 1

        # Count by author
        by_author = {}
        for dev in deviations:
            if dev.blame:
                author = dev.blame.author
                by_author[author] = by_author.get(author, 0) + 1

        # Find oldest and newest
        dated = [d for d in deviations if d.blame]
        oldest = min(dated, key=lambda d: d.blame.timestamp) if dated else None
        newest = max(dated, key=lambda d: d.blame.timestamp) if dated else None

        return DeviationReport(
            timestamp=datetime.now().isoformat(),
            total_deviations=len(deviations),
            by_state=by_state,
            by_author=by_author,
            deviations=deviations,
            oldest_deviation=oldest,
            newest_deviation=newest
        )

    def trace_directory(self, code_dir: Path, docs_dir: Path) -> DeviationReport:
        """
        Quick trace without full symmetry analysis.
        Compares code definitions with doc mentions.
        """
        from .visibility_analyzer import VisibilityAnalyzer
        from .wave_extractor import WaveExtractor
        from .identity_matcher import IdentityMatcher

        # Extract code symbols
        code_symbols = []
        for py_file in code_dir.rglob("*.py"):
            if "test" in str(py_file) or ".venv" in str(py_file):
                continue
            try:
                source = py_file.read_text(encoding='utf-8')
                module = str(py_file.relative_to(code_dir)).replace("/", ".").replace(".py", "")
                analyzer = VisibilityAnalyzer(source, module)
                for name in analyzer.get_public_exports():
                    code_symbols.append(f"{module}.{name}" if "." not in name else name)
            except Exception:
                continue

        # Extract doc references
        extractor = WaveExtractor(docs_dir)
        doc_nodes = extractor.extract_all()
        doc_symbols = list(set(node.id for node in doc_nodes))

        # Match
        matcher = IdentityMatcher(threshold=0.75)
        result = matcher.match(doc_symbols, code_symbols)

        # Build report dict matching SymmetryReport structure
        report_dict = {
            "top_offenders": {
                "undocumented": result.undocumented[:20],
                "orphan_docs": result.orphan_docs[:20]
            }
        }

        return self.trace_from_symmetry_report(report_dict)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Trace concordance deviations to source")
    parser.add_argument("repo_path", type=Path, help="Repository root")
    parser.add_argument("--code-dir", type=Path, help="Code directory (default: src/)")
    parser.add_argument("--docs-dir", type=Path, help="Docs directory (default: docs/)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--limit", type=int, default=20, help="Max deviations to trace")

    args = parser.parse_args()

    tracker = DeviationTracker(args.repo_path)

    code_dir = args.code_dir or (args.repo_path / "src")
    docs_dir = args.docs_dir or (args.repo_path / "docs")

    report = tracker.trace_directory(code_dir, docs_dir)

    if args.json:
        print(report.to_json())
    else:
        print(f"\n{'='*60}")
        print(f"DEVIATION TRACKER REPORT")
        print(f"{'='*60}")
        print(f"Total deviations: {report.total_deviations}")
        print(f"By state: {report.by_state}")
        print(f"By author: {report.by_author}")

        if report.oldest_deviation and report.oldest_deviation.blame:
            old = report.oldest_deviation
            blame = old.blame
            print(f"\nOldest drift: {old.symbol}")
            print(f"  Introduced: {blame.timestamp.date()} by {blame.author}")
            print(f"  Commit: {blame.commit_sha[:8]} - {blame.commit_message[:50]}")

        print(f"\n{'='*60}")
        print("TOP DEVIATIONS:")
        print(f"{'='*60}")

        for dev in report.deviations[:args.limit]:
            print(f"\n[{dev.state}] {dev.symbol}")
            print(f"  Location: {dev.location}")
            if dev.blame:
                print(f"  Author: {dev.blame.author} ({dev.blame.timestamp.date()})")
                print(f"  Commit: {dev.blame.commit_sha[:8]}")
            print(f"  Action: {dev.suggested_action}")


if __name__ == "__main__":
    main()
