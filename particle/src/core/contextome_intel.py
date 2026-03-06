# Theory: L1_DEFINITIONS.md SS3.2 (Contextome Definition)
# Theory: CONTEXTOME.md (Formal Contextome specification)
"""
CONTEXTOME INTELLIGENCE (Stage 0.8)
====================================

Sibling discovery system to Survey (Stage 0).

Survey defines the CODOME -- what code exists and how it should be analyzed.
Contextome Intelligence defines the CONTEXTOME -- what documentation exists
and what it DECLARES about the system.

"Code implements purpose. Documentation declares purpose.
 The truth is where they agree."

Architecture: Dual-Layer
  - Layer 1 (Deterministic): Always runs, zero dependencies, structural extraction
  - Layer 2 (LLM Enrichment): Optional, provider-agnostic adapter, deepens signals

Output: ContextomeIntelligence -- inventory, declared purposes, symmetry seeds,
        purpose priors. Same contract whether LLM is present or not.

Integration:
  - Stage 0.8 runs between Survey (Stage 0) and Incremental Detection (Stage 0.5)
  - Feeds into Purpose Field (Stage 3.7) as purpose priors
  - Feeds into InsightsCompiler (Stage 11.95) for declared-vs-inferred comparison
  - Feeds into Incoherence (Stage 11.96) for I_sym term

Phase: 10 (Adaptive Intelligence Layer)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

# ---------------------------------------------------------------------------
# Constants -- sibling to survey.py's DOC_EXTENSIONS
# ---------------------------------------------------------------------------

DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.adoc', '.org'}

# Same walk-skip pattern as survey.py HOT_SKIP
HOT_SKIP = {
    ".git", "node_modules", "archive", "experiments",
    ".collider", ".venv", "venv", "__pycache__",
}

# Heading hierarchy patterns per doc type
_MD_HEADING = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*#*\s*)?$', re.MULTILINE)
_RST_HEADING_UNDERLINE = re.compile(r'^([=\-~^`"+:.\'#*!]{3,})\s*$')

# Keyword extraction -- capitalized technical terms, framework names
_KEYWORD_PATTERN = re.compile(
    r'\b('
    r'Django|Flask|FastAPI|Express|React|Vue|Angular|Svelte|Next\.?js|Nuxt|'
    r'Spring|Rails|Laravel|Gin|Echo|Fiber|Actix|Rocket|'
    r'PostgreSQL|MySQL|MongoDB|Redis|SQLite|Cassandra|DynamoDB|'
    r'GraphQL|REST|gRPC|WebSocket|MQTT|'
    r'Docker|Kubernetes|Terraform|AWS|GCP|Azure|Heroku|Vercel|'
    r'OAuth|JWT|SAML|OIDC|HTTPS|TLS|SSL|'
    r'TypeScript|JavaScript|Python|Go|Rust|Java|Kotlin|Swift|Ruby|PHP|'
    r'CI/CD|GitHub\s*Actions|Jenkins|CircleCI|GitLab\s*CI|'
    r'Webpack|Vite|Rollup|esbuild|Babel|'
    r'pytest|Jest|Mocha|RSpec|JUnit|'
    r'Celery|RabbitMQ|Kafka|SQS|NATS|'
    r'Nginx|Apache|Caddy|Traefik'
    r')\b',
    re.IGNORECASE
)

# Code reference patterns in documentation
_CODE_REF_BACKTICK = re.compile(r'`([^`]+(?:\.\w{1,5}|::\w+|\(\)))`')
_CODE_REF_PATH = re.compile(
    r'(?:^|\s)((?:src|lib|app|pkg|internal|cmd|api|tests?|spec|config)/'
    r'[\w/\-]+\.[\w]+)',
    re.MULTILINE
)
_CODE_REF_CLASS = re.compile(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b')

# Constraint patterns (RFC 2119 language)
_CONSTRAINT_PATTERN = re.compile(
    r'(?:^|\.\s+)([^.]*?\b(?:MUST|MUST\s+NOT|SHALL|SHALL\s+NOT|SHOULD|'
    r'SHOULD\s+NOT|REQUIRED|RECOMMENDED)\b[^.]*\.)',
    re.MULTILINE | re.IGNORECASE
)

# Framework signals in config files
_FRAMEWORK_CONFIG_SIGNALS = {
    'requirements.txt': [
        (r'\bdjango\b', 'Django'),
        (r'\bflask\b', 'Flask'),
        (r'\bfastapi\b', 'FastAPI'),
        (r'\bcelery\b', 'Celery'),
        (r'\bsqlalchemy\b', 'SQLAlchemy'),
    ],
    'package.json': [
        (r'"react"', 'React'),
        (r'"vue"', 'Vue'),
        (r'"angular', 'Angular'),
        (r'"svelte"', 'Svelte'),
        (r'"next"', 'Next.js'),
        (r'"nuxt"', 'Nuxt'),
        (r'"express"', 'Express'),
        (r'"fastify"', 'Fastify'),
    ],
    'go.mod': [
        (r'gin-gonic/gin', 'Gin'),
        (r'labstack/echo', 'Echo'),
        (r'gofiber/fiber', 'Fiber'),
    ],
    'Cargo.toml': [
        (r'actix-web', 'Actix'),
        (r'rocket', 'Rocket'),
        (r'axum', 'Axum'),
    ],
    'Gemfile': [
        (r'\brails\b', 'Rails'),
        (r'\bsinatra\b', 'Sinatra'),
    ],
    'composer.json': [
        (r'laravel', 'Laravel'),
        (r'symfony', 'Symfony'),
    ],
}

# Max file size to read (256KB -- skip giant docs)
MAX_DOC_SIZE = 256 * 1024


# ---------------------------------------------------------------------------
# Data Contracts
# ---------------------------------------------------------------------------

@dataclass
class DocInventoryItem:
    """A single doc file in the contextome."""
    path: str               # relative path from root
    extension: str           # .md, .rst, etc.
    size_bytes: int
    sections: list[dict]     # [{level, title}]
    line_count: int

    def to_dict(self) -> dict:
        return {
            'path': self.path,
            'extension': self.extension,
            'size_bytes': self.size_bytes,
            'sections': self.sections,
            'line_count': self.line_count,
        }


@dataclass
class DeclaredPurpose:
    """Purpose extracted from a single document."""
    file: str                    # relative path
    title_purpose: str | None    # first H1 heading
    keywords: list[str]          # technical terms found
    code_refs: list[str]         # code paths/classes referenced
    sections: list[str]          # sub-headings as sub-purposes
    framework_signals: list[str] # framework names detected
    constraints: list[str]       # MUST/SHALL statements
    # LLM-enriched fields (None when LLM not used)
    semantic_purpose: str | None = None
    architecture_hints: list[str] | None = None
    enrichment_source: str | None = None  # "gemini", "openai", etc.

    def to_dict(self) -> dict:
        d = {
            'file': self.file,
            'title_purpose': self.title_purpose,
            'keywords': self.keywords,
            'code_refs': self.code_refs,
            'sections': self.sections,
            'framework_signals': self.framework_signals,
            'constraints': self.constraints,
        }
        if self.semantic_purpose is not None:
            d['semantic_purpose'] = self.semantic_purpose
        if self.architecture_hints is not None:
            d['architecture_hints'] = self.architecture_hints
        if self.enrichment_source is not None:
            d['enrichment_source'] = self.enrichment_source
        return d


@dataclass
class SymmetrySeed:
    """A doc-code relationship seed for symmetry analysis."""
    doc_path: str            # doc file
    code_targets: list[str]  # code paths this doc likely covers
    relationship: str        # "covers", "describes", "references"
    confidence: float        # 0.0-1.0

    def to_dict(self) -> dict:
        return {
            'doc_path': self.doc_path,
            'code_targets': self.code_targets,
            'relationship': self.relationship,
            'confidence': self.confidence,
        }


@dataclass
class ContextomeIntelligence:
    """Stage 0.8 output -- same contract whether LLM is present or not."""

    # 0.8.1: What docs exist (deterministic)
    inventory: list[DocInventoryItem]

    # 0.8.2 + 0.8.5: What the docs declare
    declared_purposes: list[DeclaredPurpose]

    # 0.8.3: Doc-code mapping seeds (deterministic)
    symmetry_seeds: list[SymmetrySeed]

    # 0.8.4: Purpose priors for codome analysis
    purpose_priors: dict  # {glob_pattern: {purpose, confidence, source}}

    # Metadata
    llm_used: bool = False
    doc_count: int = 0
    purpose_coverage: float = 0.0
    deterministic_signals: int = 0
    enriched_signals: int = 0

    def to_dict(self) -> dict:
        return {
            'inventory': [item.to_dict() for item in self.inventory],
            'declared_purposes': [dp.to_dict() for dp in self.declared_purposes],
            'symmetry_seeds': [s.to_dict() for s in self.symmetry_seeds],
            'purpose_priors': self.purpose_priors,
            'llm_used': self.llm_used,
            'doc_count': self.doc_count,
            'purpose_coverage': self.purpose_coverage,
            'deterministic_signals': self.deterministic_signals,
            'enriched_signals': self.enriched_signals,
        }


# ---------------------------------------------------------------------------
# LLM Adapter Protocol (Layer 2)
# ---------------------------------------------------------------------------

@runtime_checkable
class LLMAdapter(Protocol):
    """Provider-agnostic LLM interface for contextome enrichment.

    Any LLM provider (Gemini, OpenAI, Cerebras, Ollama) can implement this.
    When provided to run_contextome_intelligence(), it deepens the
    deterministic signals with semantic analysis.
    """

    def extract_purpose(self, content: str, path: str) -> dict | None:
        """Extract semantic purpose from document content.

        Args:
            content: Truncated document text (max ~4K tokens)
            path: Relative file path for context

        Returns:
            dict with keys: semantic_purpose, architecture_hints,
            constraints, relationships. Or None if extraction fails.
        """
        ...


# ---------------------------------------------------------------------------
# Layer 1: Deterministic Core
# ---------------------------------------------------------------------------

def _discover_docs(
    root: Path,
    exclude_paths: list[str] | None = None,
) -> list[DocInventoryItem]:
    """Stage 0.8.1: Doc Discovery.

    Walk the filesystem to find all documentation files,
    extract heading structure from each.
    """
    exclude_paths = exclude_paths or []
    inventory = []
    root_str = str(root)

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune HOT_SKIP directories in-place
        dirnames[:] = [d for d in dirnames if d not in HOT_SKIP]

        rel_dir = os.path.relpath(dirpath, root_str)
        if rel_dir == '.':
            rel_dir = ''

        # Check exclude_paths
        skip = False
        for exc in exclude_paths:
            exc_clean = exc.rstrip('/')
            if rel_dir == exc_clean or rel_dir.startswith(exc_clean + '/'):
                skip = True
                dirnames.clear()
                break
        if skip:
            continue

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in DOC_EXTENSIONS:
                continue

            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.join(rel_dir, filename) if rel_dir else filename

            try:
                stat = os.stat(full_path)
                if stat.st_size > MAX_DOC_SIZE:
                    continue
                if stat.st_size == 0:
                    continue

                # Read and extract structure
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                sections = _extract_sections(content, ext)
                line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)

                inventory.append(DocInventoryItem(
                    path=rel_path,
                    extension=ext,
                    size_bytes=stat.st_size,
                    sections=sections,
                    line_count=line_count,
                ))
            except (OSError, UnicodeDecodeError):
                continue

    return inventory


def _extract_sections(content: str, ext: str) -> list[dict]:
    """Extract heading hierarchy from document content."""
    sections = []

    if ext in ('.md', '.adoc'):
        for match in _MD_HEADING.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            sections.append({'level': level, 'title': title})

    elif ext == '.rst':
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i + 1 < len(lines) and _RST_HEADING_UNDERLINE.match(lines[i + 1]):
                title = line.strip()
                if title and not _RST_HEADING_UNDERLINE.match(title):
                    # RST heading level is determined by underline character
                    # but we don't know order until we see them all
                    sections.append({'level': 1, 'title': title})

    elif ext == '.org':
        for line in content.split('\n'):
            if line.startswith('*'):
                stars = len(line) - len(line.lstrip('*'))
                title = line[stars:].strip()
                if title:
                    sections.append({'level': stars, 'title': title})

    return sections


def _extract_declared_purpose(
    rel_path: str,
    content: str,
    sections: list[dict],
) -> DeclaredPurpose:
    """Stage 0.8.2: Structural Purpose Extraction from a single doc.

    Deterministic extraction of 6 signal types:
    1. Title purpose (first H1)
    2. Keywords (framework/tech terms)
    3. Code references (paths, classes, functions)
    4. Section structure (sub-headings as sub-purposes)
    5. Framework signals (pattern matching)
    6. Constraints (RFC 2119 language)
    """
    # 1. Title purpose: first H1 heading
    title_purpose = None
    for sec in sections:
        if sec['level'] == 1:
            title_purpose = sec['title']
            break

    # If no H1 in sections, try the filename
    if title_purpose is None:
        basename = os.path.splitext(os.path.basename(rel_path))[0]
        if basename.upper() not in ('README', 'INDEX', 'CHANGELOG', 'LICENSE'):
            # Convert filename to purpose: SOME_THING -> Some Thing
            title_purpose = basename.replace('_', ' ').replace('-', ' ').title()

    # 2. Keywords: technical terms
    keywords = sorted(set(
        m.group(0) for m in _KEYWORD_PATTERN.finditer(content)
    ))

    # 3. Code references
    code_refs = set()
    for m in _CODE_REF_BACKTICK.finditer(content):
        ref = m.group(1)
        # Filter: must look like code (has dots, slashes, parens, or colons)
        if any(c in ref for c in './:()') and len(ref) < 200:
            code_refs.add(ref)
    for m in _CODE_REF_PATH.finditer(content):
        code_refs.add(m.group(1))
    code_refs = sorted(code_refs)[:50]  # cap at 50

    # 4. Sub-purposes from section headings
    sub_sections = [
        sec['title'] for sec in sections
        if sec['level'] in (2, 3)
    ][:30]  # cap at 30

    # 5. Framework signals from content
    framework_signals = sorted(set(
        m.group(0) for m in _KEYWORD_PATTERN.finditer(content)
        if m.group(0).lower() in {
            'django', 'flask', 'fastapi', 'express', 'react', 'vue', 'angular',
            'svelte', 'next.js', 'nuxt', 'spring', 'rails', 'laravel',
            'gin', 'echo', 'fiber', 'actix', 'rocket',
        }
    ))

    # 6. Constraints
    constraints = [
        m.group(1).strip()
        for m in _CONSTRAINT_PATTERN.finditer(content)
    ][:20]  # cap at 20

    return DeclaredPurpose(
        file=rel_path,
        title_purpose=title_purpose,
        keywords=keywords,
        code_refs=code_refs,
        sections=sub_sections,
        framework_signals=framework_signals,
        constraints=constraints,
    )


def _detect_framework_signals_from_config(root: Path) -> list[str]:
    """Detect framework signals from config files (requirements.txt, package.json, etc.)."""
    signals = []

    for config_file, patterns in _FRAMEWORK_CONFIG_SIGNALS.items():
        config_path = root / config_file
        if not config_path.exists():
            continue
        try:
            content = config_path.read_text(encoding='utf-8', errors='replace')
            for pattern, framework in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    signals.append(framework)
        except OSError:
            continue

    return sorted(set(signals))


def _seed_symmetry(
    inventory: list[DocInventoryItem],
    declared_purposes: list[DeclaredPurpose],
    root: Path,
) -> list[SymmetrySeed]:
    """Stage 0.8.3: Symmetry Seeding.

    Map docs to code using deterministic heuristics:
    1. Name matching: README.md in src/auth/ → covers src/auth/
    2. Code refs: doc mentions `src/services/user.py` → covers that file
    3. Sibling detection: doc next to code directory → covers that directory
    4. Explicit naming: ARCHITECTURE.md → covers entire project
    """
    seeds = []

    for doc_item in inventory:
        doc_path = doc_item.path
        doc_dir = os.path.dirname(doc_path)
        doc_name = os.path.splitext(os.path.basename(doc_path))[0].lower()

        code_targets = []
        relationship = 'covers'
        confidence = 0.5

        # Heuristic 1: README/INDEX in a code directory → covers that directory
        if doc_name in ('readme', 'index'):
            if doc_dir:
                # README in a subdirectory → covers that subdirectory
                code_targets.append(doc_dir + '/')
                confidence = 0.8
            else:
                # Root README → covers the whole project
                code_targets.append('./')
                confidence = 0.9
                relationship = 'describes'

        # Heuristic 2: Named doc matches code structure
        # e.g., auth.md → covers src/auth/, lib/auth/, etc.
        elif doc_name not in ('changelog', 'license', 'contributing', 'code_of_conduct'):
            # Look for matching directories in the project
            target_name = doc_name.replace('-', '_')
            for candidate in ('src', 'lib', 'app', 'pkg', 'internal', 'cmd'):
                candidate_dir = os.path.join(candidate, target_name)
                if (root / candidate_dir).is_dir():
                    code_targets.append(candidate_dir + '/')
                    confidence = 0.7
                    break

        # Heuristic 3: Code references in the document
        dp = next((p for p in declared_purposes if p.file == doc_path), None)
        if dp and dp.code_refs:
            for ref in dp.code_refs[:10]:
                if '/' in ref and not ref.startswith('http'):
                    code_targets.append(ref)
                    relationship = 'references'
                    confidence = max(confidence, 0.6)

        # Heuristic 4: Sibling directories
        if doc_dir:
            # Check if doc is next to code directories
            dir_path = root / doc_dir
            if dir_path.is_dir():
                try:
                    siblings = [
                        d for d in os.listdir(dir_path)
                        if (dir_path / d).is_dir() and d not in HOT_SKIP
                    ]
                    code_siblings = [
                        s for s in siblings
                        if s.lower() in ('src', 'lib', 'app', 'tests', 'test', 'spec')
                    ]
                    for sib in code_siblings:
                        target = os.path.join(doc_dir, sib) + '/'
                        if target not in code_targets:
                            code_targets.append(target)
                            confidence = max(confidence, 0.5)
                except OSError:
                    pass

        if code_targets:
            seeds.append(SymmetrySeed(
                doc_path=doc_path,
                code_targets=sorted(set(code_targets)),
                relationship=relationship,
                confidence=confidence,
            ))

    return seeds


def _compute_purpose_priors(
    declared_purposes: list[DeclaredPurpose],
    symmetry_seeds: list[SymmetrySeed],
) -> dict:
    """Stage 0.8.4: Purpose Priors.

    Map heading-derived purposes to code path patterns.
    These become initial purpose suggestions for the Purpose Field.
    """
    priors = {}

    for seed in symmetry_seeds:
        # Find the declared purpose for this doc
        dp = next(
            (p for p in declared_purposes if p.file == seed.doc_path),
            None,
        )
        if dp is None or dp.title_purpose is None:
            continue

        # Map each code target to a purpose prior
        for code_target in seed.code_targets:
            # Normalize to glob pattern
            if code_target.endswith('/'):
                glob_pattern = code_target + '**'
            else:
                glob_pattern = code_target

            purpose_text = dp.title_purpose

            # Use semantic_purpose if LLM enriched it
            if dp.semantic_purpose:
                purpose_text = dp.semantic_purpose

            priors[glob_pattern] = {
                'purpose': purpose_text,
                'confidence': seed.confidence,
                'source': dp.file,
                'keywords': dp.keywords[:5] if dp.keywords else [],
            }

    return priors


# ---------------------------------------------------------------------------
# Layer 2: LLM Enrichment
# ---------------------------------------------------------------------------

def _enrich_with_llm(
    inventory: list[DocInventoryItem],
    declared_purposes: list[DeclaredPurpose],
    root: Path,
    adapter: LLMAdapter,
    max_docs: int = 50,
) -> int:
    """Stage 0.8.5 + 0.8.6: LLM enrichment + merge.

    Reads doc contents, sends to LLM adapter for semantic extraction,
    merges results into existing declared_purposes (mutates in place).

    Returns count of enriched signals.
    """
    enriched_count = 0

    # Prioritize: README first, then by size (smaller = more focused)
    sorted_items = sorted(
        inventory[:max_docs],
        key=lambda item: (
            0 if 'readme' in item.path.lower() else 1,
            item.size_bytes,
        ),
    )

    for item in sorted_items:
        # Find corresponding declared purpose
        dp = next(
            (p for p in declared_purposes if p.file == item.path),
            None,
        )
        if dp is None:
            continue

        # Read content (truncated for LLM)
        try:
            full_path = root / item.path
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(16_000)  # ~4K tokens
        except OSError:
            continue

        # Call LLM adapter
        try:
            result = adapter.extract_purpose(content, item.path)
        except Exception:
            continue

        if result is None:
            continue

        # 0.8.6: Merge enrichment into deterministic base
        if 'semantic_purpose' in result and result['semantic_purpose']:
            dp.semantic_purpose = result['semantic_purpose']
            enriched_count += 1

        if 'architecture_hints' in result and result['architecture_hints']:
            dp.architecture_hints = result['architecture_hints']
            enriched_count += 1

        if 'constraints' in result and result['constraints']:
            # Merge LLM constraints with deterministic ones
            for c in result['constraints']:
                if c not in dp.constraints:
                    dp.constraints.append(c)
            enriched_count += 1

        dp.enrichment_source = getattr(adapter, 'provider_name', 'unknown')

    return enriched_count


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_contextome_intelligence(
    root_path: str,
    exclude_paths: list[str] | None = None,
    llm_adapter: LLMAdapter | None = None,
) -> ContextomeIntelligence:
    """Run Stage 0.8: Contextome Intelligence.

    Dual-layer architecture:
      - Layer 1 (deterministic): Always runs. Discovers docs, extracts
        structural purpose, seeds symmetry, computes purpose priors.
      - Layer 2 (LLM enrichment): Runs only if llm_adapter is provided.
        Deepens declared purposes with semantic analysis.

    Args:
        root_path: Path to repository root
        exclude_paths: Paths to exclude from doc discovery
        llm_adapter: Optional LLM adapter for semantic enrichment

    Returns:
        ContextomeIntelligence with full inventory and analysis
    """
    root = Path(root_path)

    # ── Layer 1: Deterministic Core ──────────────────────────────────────

    # 0.8.1: Doc Discovery
    inventory = _discover_docs(root, exclude_paths)

    # 0.8.2: Structural Purpose Extraction
    declared_purposes = []
    for item in inventory:
        try:
            full_path = root / item.path
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            dp = _extract_declared_purpose(item.path, content, item.sections)
            declared_purposes.append(dp)
        except OSError:
            continue

    # Detect framework signals from config files
    config_signals = _detect_framework_signals_from_config(root)
    # Inject config signals into root-level docs
    for dp in declared_purposes:
        if os.path.dirname(dp.file) == '':
            for sig in config_signals:
                if sig not in dp.framework_signals:
                    dp.framework_signals.append(sig)

    # 0.8.3: Symmetry Seeding
    symmetry_seeds = _seed_symmetry(inventory, declared_purposes, root)

    # 0.8.4: Purpose Priors
    purpose_priors = _compute_purpose_priors(declared_purposes, symmetry_seeds)

    # Count deterministic signals
    det_signals = 0
    for dp in declared_purposes:
        if dp.title_purpose:
            det_signals += 1
        det_signals += len(dp.keywords)
        det_signals += len(dp.code_refs)
        det_signals += len(dp.framework_signals)
        det_signals += len(dp.constraints)

    # ── Layer 2: LLM Enrichment (optional) ───────────────────────────────

    enriched_signals = 0
    llm_used = False

    if llm_adapter is not None:
        llm_used = True
        enriched_signals = _enrich_with_llm(
            inventory, declared_purposes, root, llm_adapter,
        )
        # Recompute purpose priors with enriched data
        purpose_priors = _compute_purpose_priors(declared_purposes, symmetry_seeds)

    # ── Assemble output ──────────────────────────────────────────────────

    docs_with_purpose = sum(
        1 for dp in declared_purposes
        if dp.title_purpose or dp.semantic_purpose
    )
    purpose_coverage = docs_with_purpose / len(declared_purposes) if declared_purposes else 0.0

    return ContextomeIntelligence(
        inventory=inventory,
        declared_purposes=declared_purposes,
        symmetry_seeds=symmetry_seeds,
        purpose_priors=purpose_priors,
        llm_used=llm_used,
        doc_count=len(inventory),
        purpose_coverage=purpose_coverage,
        deterministic_signals=det_signals,
        enriched_signals=enriched_signals,
    )
