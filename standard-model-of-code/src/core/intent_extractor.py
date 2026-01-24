"""Multi-modal intent extraction from code, commits, docs.

Research finding: "Developer intent is not fully captured by code alone"
(WSDM 2025). Must extract from multiple sources:

1. Docstrings - Explicit developer intent
2. Commit messages - Evolution intent (why changes were made)
3. README/docs - High-level purpose
4. Issue references - Problem context

This module extracts intent signals that graph analysis alone cannot capture.
"""
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


def extract_readme_intent(repo_path: Path) -> Optional[str]:
    """Extract high-level purpose from README.

    README typically describes:
    - What the project does
    - Why it exists
    - How to use it

    Returns first 2000 chars of README content.
    """
    readme_patterns = [
        'README.md', 'README.rst', 'README.txt', 'README',
        'readme.md', 'Readme.md'
    ]

    for pattern in readme_patterns:
        readme_path = repo_path / pattern
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8')
                return content[:2000]  # First 2K chars
            except Exception:
                continue
    return None


def extract_commit_intents(
    repo_path: Path,
    file_path: str,
    num_commits: int = 10
) -> List[Dict[str, str]]:
    """Extract intent from commits affecting a specific file.

    Commit messages express:
    - problem discovery ("fix bug in...")
    - solution proposal ("implement X to solve Y")
    - architectural intent ("refactor for better...")
    - feature requests ("add support for...")

    Args:
        repo_path: Root of git repository
        file_path: Relative path to file
        num_commits: Max commits to retrieve

    Returns:
        List of {hash, message, intent_type} dicts
    """
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-n', str(num_commits), '--', file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    message = parts[1]
                    commits.append({
                        'hash': parts[0],
                        'message': message,
                        'intent_type': classify_commit_intent(message)
                    })
        return commits
    except Exception:
        return []


def extract_docstring_intent(source_code: str) -> Optional[str]:
    """Extract docstring from function/class source.

    Docstrings represent explicit developer intent -
    what they intended the code to do.
    """
    # Match triple-quoted docstrings (double quotes)
    match = re.search(r'"""(.*?)"""', source_code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Match triple-quoted docstrings (single quotes)
    match = re.search(r"'''(.*?)'''", source_code, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Match single-line comments at start (for languages without docstrings)
    lines = source_code.split('\n')
    comments = []
    for line in lines[:5]:  # Check first 5 lines
        stripped = line.strip()
        if stripped.startswith('#'):
            comments.append(stripped[1:].strip())
        elif stripped.startswith('//'):
            comments.append(stripped[2:].strip())
    if comments:
        return ' '.join(comments)

    return None


def classify_commit_intent(message: str) -> str:
    """Classify commit message intent category.

    Categories based on research:
    - fix: Problem resolution
    - feature: New functionality
    - refactor: Architectural change
    - docs: Documentation
    - test: Test coverage
    - perf: Performance improvement
    - chore: Maintenance

    Args:
        message: Commit message text

    Returns:
        Intent category string
    """
    message_lower = message.lower()

    # Fix patterns
    if any(p in message_lower for p in ['fix', 'bug', 'issue', 'error', 'crash', 'resolve']):
        return 'fix'

    # Feature patterns
    if any(p in message_lower for p in ['add', 'feat', 'implement', 'new', 'create', 'support']):
        return 'feature'

    # Refactor patterns
    if any(p in message_lower for p in ['refactor', 'restructure', 'reorganize', 'simplify', 'clean']):
        return 'refactor'

    # Performance patterns
    if any(p in message_lower for p in ['perf', 'optim', 'speed', 'fast', 'cache']):
        return 'perf'

    # Docs patterns
    if any(p in message_lower for p in ['doc', 'readme', 'comment', 'typo']):
        return 'docs'

    # Test patterns
    if any(p in message_lower for p in ['test', 'spec', 'coverage', 'mock']):
        return 'test'

    return 'chore'


def extract_issue_references(commit_message: str) -> List[str]:
    """Extract issue/PR references from commit message.

    Patterns:
    - #123
    - fixes #123
    - closes #123
    - GH-123
    """
    patterns = [
        r'#(\d+)',
        r'GH-(\d+)',
        r'(?:fixes|closes|resolves)\s+#(\d+)',
    ]

    references = []
    for pattern in patterns:
        matches = re.findall(pattern, commit_message, re.IGNORECASE)
        references.extend(matches)

    return list(set(references))


def build_node_intent_profile(
    node_id: str,
    file_path: str,
    source_code: Optional[str],
    repo_path: Path
) -> Dict[str, Any]:
    """Build comprehensive intent profile for a node.

    Combines multiple intent sources:
    - Docstring (explicit developer intent)
    - Commit history (evolution intent)
    - Issue references (problem context)

    Args:
        node_id: Unique node identifier
        file_path: Path to source file
        source_code: Source code of the node (if available)
        repo_path: Root of git repository

    Returns:
        Intent profile dict
    """
    profile: Dict[str, Any] = {
        'node_id': node_id,
        'file_path': file_path,
        'has_docstring': False,
        'has_commits': False,
        'has_issues': False
    }

    # Docstring intent
    if source_code:
        docstring = extract_docstring_intent(source_code)
        if docstring:
            profile['docstring'] = docstring[:500]  # Truncate
            profile['has_docstring'] = True

    # Commit intent
    commits = extract_commit_intents(repo_path, file_path, num_commits=5)
    if commits:
        profile['recent_commits'] = commits
        profile['commit_intents'] = [c['intent_type'] for c in commits]
        profile['has_commits'] = True

        # Extract issue references from commits
        all_issues = []
        for commit in commits:
            issues = extract_issue_references(commit['message'])
            all_issues.extend(issues)
        if all_issues:
            profile['issue_references'] = list(set(all_issues))
            profile['has_issues'] = True

    # Compute intent richness score
    richness = sum([
        profile['has_docstring'],
        profile['has_commits'],
        profile['has_issues']
    ])
    profile['intent_richness'] = richness / 3.0

    return profile


def analyze_intent_coverage(
    nodes: List[Dict],
    repo_path: Path
) -> Dict[str, Any]:
    """Analyze intent coverage across all nodes.

    Returns statistics about how much intent information
    is available in the codebase.
    """
    total = len(nodes)
    with_docstring = 0
    with_commits = 0

    for node in nodes:
        source = node.get('body_source', '')
        if source and extract_docstring_intent(source):
            with_docstring += 1

        file_path = node.get('file_path', '')
        if file_path:
            commits = extract_commit_intents(repo_path, file_path, num_commits=1)
            if commits:
                with_commits += 1

    return {
        'total_nodes': total,
        'with_docstring': with_docstring,
        'with_commits': with_commits,
        'docstring_coverage': with_docstring / max(1, total),
        'commit_coverage': with_commits / max(1, total)
    }
