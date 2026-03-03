"""Tests for Contextome Intelligence (Stage 0.8)."""

import os
import sys
from pathlib import Path

import pytest

# Add core to path (matches existing test pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'core'))

from contextome_intel import (
    DOC_EXTENSIONS,
    HOT_SKIP,
    MAX_DOC_SIZE,
    DocInventoryItem,
    DeclaredPurpose,
    SymmetrySeed,
    ContextomeIntelligence,
    LLMAdapter,
    _discover_docs,
    _extract_sections,
    _extract_declared_purpose,
    _detect_framework_signals_from_config,
    _seed_symmetry,
    _compute_purpose_priors,
    _enrich_with_llm,
    run_contextome_intelligence,
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _write_file(path: Path, content: str) -> None:
    """Create a file with content, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


class MockLLMAdapter:
    """A mock LLM adapter for testing Layer 2 enrichment."""

    provider_name = 'mock'

    def __init__(self, responses: dict | None = None):
        self.responses = responses or {}
        self.calls = []

    def extract_purpose(self, content: str, path: str) -> dict | None:
        self.calls.append((path, len(content)))
        if path in self.responses:
            return self.responses[path]
        return {
            'semantic_purpose': f'Mock purpose for {path}',
            'architecture_hints': ['layer:mock'],
            'constraints': [],
        }


class FailingLLMAdapter:
    """An LLM adapter that always raises exceptions."""

    provider_name = 'failing'

    def extract_purpose(self, content: str, path: str) -> dict | None:
        raise RuntimeError('LLM is down')


# ── Section Extraction ───────────────────────────────────────────────────


class TestExtractSections:
    def test_markdown_headings(self):
        content = '# Title\n\n## Section 1\n\nText.\n\n### Sub-section\n'
        sections = _extract_sections(content, '.md')
        assert len(sections) == 3
        assert sections[0] == {'level': 1, 'title': 'Title'}
        assert sections[1] == {'level': 2, 'title': 'Section 1'}
        assert sections[2] == {'level': 3, 'title': 'Sub-section'}

    def test_markdown_with_trailing_hashes(self):
        content = '# Title #\n## Section ##\n'
        sections = _extract_sections(content, '.md')
        assert sections[0]['title'] == 'Title'
        assert sections[1]['title'] == 'Section'

    def test_rst_headings(self):
        content = 'Title\n=====\n\nSome text.\n\nSection\n-------\n'
        sections = _extract_sections(content, '.rst')
        assert len(sections) == 2
        assert sections[0]['title'] == 'Title'
        assert sections[1]['title'] == 'Section'

    def test_org_headings(self):
        content = '* Top Level\n** Second Level\n*** Third Level\n'
        sections = _extract_sections(content, '.org')
        assert len(sections) == 3
        assert sections[0] == {'level': 1, 'title': 'Top Level'}
        assert sections[1] == {'level': 2, 'title': 'Second Level'}
        assert sections[2] == {'level': 3, 'title': 'Third Level'}

    def test_adoc_uses_markdown_pattern(self):
        content = '# AsciiDoc Title\n## Section\n'
        sections = _extract_sections(content, '.adoc')
        assert len(sections) == 2

    def test_txt_returns_empty(self):
        content = 'Just plain text with no headings.\n'
        sections = _extract_sections(content, '.txt')
        assert sections == []

    def test_empty_content(self):
        assert _extract_sections('', '.md') == []


# ── Declared Purpose Extraction ──────────────────────────────────────────


class TestExtractDeclaredPurpose:
    def test_title_from_h1(self):
        content = '# Authentication Service\n\n## Overview\n\nHandles auth.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/auth.md', content, sections)
        assert dp.title_purpose == 'Authentication Service'

    def test_title_from_filename_when_no_h1(self):
        content = '## Just sub-headings\n\nNo top-level heading.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/user_service.md', content, sections)
        assert dp.title_purpose == 'User Service'

    def test_no_title_for_readme(self):
        """README/INDEX filenames should not become the title."""
        content = '## Setup\n\nJust setup instructions.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('README.md', content, sections)
        assert dp.title_purpose is None

    def test_keywords_extraction(self):
        content = '# API\n\nUses Django and PostgreSQL with Redis caching.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/api.md', content, sections)
        assert 'Django' in dp.keywords
        assert 'PostgreSQL' in dp.keywords
        assert 'Redis' in dp.keywords

    def test_code_refs_backtick(self):
        content = '# API\n\nSee `src/services/user.py` for details.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/api.md', content, sections)
        assert 'src/services/user.py' in dp.code_refs

    def test_code_refs_path(self):
        content = '# API\n\nThe handler is in src/api/routes.ts and tests/api_test.py.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/api.md', content, sections)
        assert any('src/api/routes.ts' in ref for ref in dp.code_refs)

    def test_sub_sections(self):
        content = '# Service\n\n## Authentication\n\n## Authorization\n\n### RBAC\n'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/service.md', content, sections)
        assert 'Authentication' in dp.sections
        assert 'Authorization' in dp.sections
        assert 'RBAC' in dp.sections

    def test_framework_signals(self):
        content = '# App\n\nBuilt with React and Express.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/app.md', content, sections)
        assert 'React' in dp.framework_signals
        assert 'Express' in dp.framework_signals

    def test_constraint_extraction(self):
        content = '# API\n\nAll endpoints MUST validate input. Responses SHOULD include timestamps.'
        sections = _extract_sections(content, '.md')
        dp = _extract_declared_purpose('docs/api.md', content, sections)
        assert len(dp.constraints) >= 1
        assert any('MUST' in c for c in dp.constraints)

    def test_empty_content(self):
        dp = _extract_declared_purpose('docs/empty.md', '', [])
        assert dp.file == 'docs/empty.md'
        assert dp.keywords == []
        assert dp.code_refs == []

    def test_to_dict_basic(self):
        dp = DeclaredPurpose(
            file='test.md',
            title_purpose='Test',
            keywords=['Python'],
            code_refs=['src/main.py'],
            sections=['Overview'],
            framework_signals=['Flask'],
            constraints=['MUST validate'],
        )
        d = dp.to_dict()
        assert d['file'] == 'test.md'
        assert d['title_purpose'] == 'Test'
        assert 'semantic_purpose' not in d  # None by default

    def test_to_dict_with_llm_fields(self):
        dp = DeclaredPurpose(
            file='test.md',
            title_purpose='Test',
            keywords=[],
            code_refs=[],
            sections=[],
            framework_signals=[],
            constraints=[],
            semantic_purpose='A testing module',
            architecture_hints=['layer:test'],
            enrichment_source='gemini',
        )
        d = dp.to_dict()
        assert d['semantic_purpose'] == 'A testing module'
        assert d['enrichment_source'] == 'gemini'


# ── Doc Discovery ────────────────────────────────────────────────────────


class TestDiscoverDocs:
    def test_finds_markdown_files(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n\nDescription.')
        _write_file(tmp_path / 'docs' / 'guide.md', '# Guide\n')

        inventory = _discover_docs(tmp_path)
        paths = [item.path for item in inventory]
        assert 'README.md' in paths
        assert os.path.join('docs', 'guide.md') in paths

    def test_finds_all_doc_extensions(self, tmp_path):
        for ext in DOC_EXTENSIONS:
            _write_file(tmp_path / f'doc{ext}', f'Content for {ext}')

        inventory = _discover_docs(tmp_path)
        found_exts = {item.extension for item in inventory}
        assert found_exts == DOC_EXTENSIONS

    def test_skips_hot_skip_dirs(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root\n')
        _write_file(tmp_path / 'node_modules' / 'pkg' / 'README.md', '# Pkg\n')
        _write_file(tmp_path / '.git' / 'README.md', '# Git\n')

        inventory = _discover_docs(tmp_path)
        paths = [item.path for item in inventory]
        assert 'README.md' in paths
        assert len(paths) == 1  # only root README

    def test_skips_exclude_paths(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root\n')
        _write_file(tmp_path / 'vendor' / 'lib.md', '# Vendor\n')

        inventory = _discover_docs(tmp_path, exclude_paths=['vendor'])
        paths = [item.path for item in inventory]
        assert 'README.md' in paths
        assert len(paths) == 1

    def test_skips_empty_files(self, tmp_path):
        _write_file(tmp_path / 'empty.md', '')
        _write_file(tmp_path / 'real.md', '# Content\n')

        inventory = _discover_docs(tmp_path)
        paths = [item.path for item in inventory]
        assert 'real.md' in paths
        assert 'empty.md' not in paths

    def test_skips_oversized_files(self, tmp_path):
        _write_file(tmp_path / 'huge.md', 'x' * (MAX_DOC_SIZE + 1))
        _write_file(tmp_path / 'normal.md', '# Normal\n')

        inventory = _discover_docs(tmp_path)
        paths = [item.path for item in inventory]
        assert 'normal.md' in paths
        assert 'huge.md' not in paths

    def test_ignores_non_doc_files(self, tmp_path):
        _write_file(tmp_path / 'code.py', 'print("hello")')
        _write_file(tmp_path / 'data.json', '{}')
        _write_file(tmp_path / 'README.md', '# Project\n')

        inventory = _discover_docs(tmp_path)
        assert len(inventory) == 1
        assert inventory[0].path == 'README.md'

    def test_extracts_sections_and_line_count(self, tmp_path):
        content = '# Title\n\n## Section 1\n\n## Section 2\n'
        _write_file(tmp_path / 'doc.md', content)

        inventory = _discover_docs(tmp_path)
        assert len(inventory) == 1
        item = inventory[0]
        assert len(item.sections) == 3
        assert item.line_count > 0

    def test_empty_directory(self, tmp_path):
        inventory = _discover_docs(tmp_path)
        assert inventory == []

    def test_to_dict(self, tmp_path):
        _write_file(tmp_path / 'doc.md', '# Title\n')
        inventory = _discover_docs(tmp_path)
        d = inventory[0].to_dict()
        assert 'path' in d
        assert 'extension' in d
        assert 'size_bytes' in d
        assert 'sections' in d
        assert 'line_count' in d


# ── Framework Signal Detection ───────────────────────────────────────────


class TestFrameworkSignalDetection:
    def test_requirements_txt(self, tmp_path):
        _write_file(tmp_path / 'requirements.txt', 'django>=4.0\nflask\n')
        signals = _detect_framework_signals_from_config(tmp_path)
        assert 'Django' in signals
        assert 'Flask' in signals

    def test_package_json(self, tmp_path):
        _write_file(tmp_path / 'package.json', '{"dependencies": {"react": "^18.0", "express": "^4.0"}}')
        signals = _detect_framework_signals_from_config(tmp_path)
        assert 'React' in signals
        assert 'Express' in signals

    def test_go_mod(self, tmp_path):
        _write_file(tmp_path / 'go.mod', 'require github.com/gin-gonic/gin v1.9\n')
        signals = _detect_framework_signals_from_config(tmp_path)
        assert 'Gin' in signals

    def test_cargo_toml(self, tmp_path):
        _write_file(tmp_path / 'Cargo.toml', '[dependencies]\nactix-web = "4"\n')
        signals = _detect_framework_signals_from_config(tmp_path)
        assert 'Actix' in signals

    def test_no_config_files(self, tmp_path):
        signals = _detect_framework_signals_from_config(tmp_path)
        assert signals == []

    def test_deduplication(self, tmp_path):
        _write_file(tmp_path / 'requirements.txt', 'django\ndjango-rest\n')
        signals = _detect_framework_signals_from_config(tmp_path)
        assert signals.count('Django') == 1


# ── Symmetry Seeding ─────────────────────────────────────────────────────


class TestSymmetrySeeding:
    def test_root_readme(self, tmp_path):
        inventory = [DocInventoryItem(
            path='README.md', extension='.md',
            size_bytes=100, sections=[{'level': 1, 'title': 'Project'}],
            line_count=10,
        )]
        purposes = [DeclaredPurpose(
            file='README.md', title_purpose='Project',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        seeds = _seed_symmetry(inventory, purposes, tmp_path)
        assert len(seeds) == 1
        assert './' in seeds[0].code_targets
        assert seeds[0].confidence >= 0.9
        assert seeds[0].relationship == 'describes'

    def test_subdir_readme(self, tmp_path):
        (tmp_path / 'src' / 'auth').mkdir(parents=True)
        inventory = [DocInventoryItem(
            path='src/auth/README.md', extension='.md',
            size_bytes=50, sections=[], line_count=5,
        )]
        purposes = [DeclaredPurpose(
            file='src/auth/README.md', title_purpose='Auth Module',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        seeds = _seed_symmetry(inventory, purposes, tmp_path)
        assert len(seeds) == 1
        assert 'src/auth/' in seeds[0].code_targets

    def test_named_doc_matches_code_dir(self, tmp_path):
        (tmp_path / 'src' / 'auth').mkdir(parents=True)
        inventory = [DocInventoryItem(
            path='docs/auth.md', extension='.md',
            size_bytes=100, sections=[], line_count=10,
        )]
        purposes = [DeclaredPurpose(
            file='docs/auth.md', title_purpose='Authentication',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        seeds = _seed_symmetry(inventory, purposes, tmp_path)
        assert any('src/auth/' in s.code_targets for s in seeds)

    def test_code_refs_create_seeds(self, tmp_path):
        inventory = [DocInventoryItem(
            path='docs/api.md', extension='.md',
            size_bytes=100, sections=[], line_count=10,
        )]
        purposes = [DeclaredPurpose(
            file='docs/api.md', title_purpose='API Guide',
            keywords=[], code_refs=['src/api/routes.py', 'src/api/models.py'],
            sections=[], framework_signals=[], constraints=[],
        )]
        seeds = _seed_symmetry(inventory, purposes, tmp_path)
        assert len(seeds) >= 1
        all_targets = [t for s in seeds for t in s.code_targets]
        assert 'src/api/routes.py' in all_targets

    def test_empty_inputs(self, tmp_path):
        seeds = _seed_symmetry([], [], tmp_path)
        assert seeds == []

    def test_symmetry_seed_to_dict(self):
        seed = SymmetrySeed(
            doc_path='README.md',
            code_targets=['src/'],
            relationship='covers',
            confidence=0.8,
        )
        d = seed.to_dict()
        assert d['doc_path'] == 'README.md'
        assert d['confidence'] == 0.8


# ── Purpose Priors ───────────────────────────────────────────────────────


class TestPurposePriors:
    def test_basic_prior_computation(self):
        purposes = [DeclaredPurpose(
            file='docs/auth.md', title_purpose='Authentication Service',
            keywords=['OAuth'], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        seeds = [SymmetrySeed(
            doc_path='docs/auth.md',
            code_targets=['src/auth/'],
            relationship='covers',
            confidence=0.7,
        )]
        priors = _compute_purpose_priors(purposes, seeds)
        assert 'src/auth/**' in priors
        assert priors['src/auth/**']['purpose'] == 'Authentication Service'
        assert priors['src/auth/**']['confidence'] == 0.7

    def test_llm_semantic_purpose_preferred(self):
        purposes = [DeclaredPurpose(
            file='docs/api.md', title_purpose='API Docs',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
            semantic_purpose='REST API gateway for user management',
        )]
        seeds = [SymmetrySeed(
            doc_path='docs/api.md',
            code_targets=['src/api/'],
            relationship='covers',
            confidence=0.8,
        )]
        priors = _compute_purpose_priors(purposes, seeds)
        assert priors['src/api/**']['purpose'] == 'REST API gateway for user management'

    def test_no_seeds_no_priors(self):
        purposes = [DeclaredPurpose(
            file='docs/api.md', title_purpose='API',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        priors = _compute_purpose_priors(purposes, [])
        assert priors == {}

    def test_no_title_no_prior(self):
        purposes = [DeclaredPurpose(
            file='README.md', title_purpose=None,
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        seeds = [SymmetrySeed(
            doc_path='README.md', code_targets=['./'],
            relationship='describes', confidence=0.9,
        )]
        priors = _compute_purpose_priors(purposes, seeds)
        assert priors == {}


# ── LLM Enrichment ──────────────────────────────────────────────────────


class TestLLMEnrichment:
    def test_enriches_declared_purposes(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n\nA great project.')
        inventory = [DocInventoryItem(
            path='README.md', extension='.md',
            size_bytes=30, sections=[{'level': 1, 'title': 'Project'}],
            line_count=3,
        )]
        purposes = [DeclaredPurpose(
            file='README.md', title_purpose='Project',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        adapter = MockLLMAdapter()
        count = _enrich_with_llm(inventory, purposes, tmp_path, adapter)
        assert count > 0
        assert purposes[0].semantic_purpose is not None
        assert purposes[0].enrichment_source == 'mock'
        assert len(adapter.calls) == 1

    def test_failing_adapter_degrades_gracefully(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n')
        inventory = [DocInventoryItem(
            path='README.md', extension='.md',
            size_bytes=10, sections=[], line_count=1,
        )]
        purposes = [DeclaredPurpose(
            file='README.md', title_purpose='Project',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        adapter = FailingLLMAdapter()
        count = _enrich_with_llm(inventory, purposes, tmp_path, adapter)
        assert count == 0
        assert purposes[0].semantic_purpose is None

    def test_none_return_skipped(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Skipped\n')
        inventory = [DocInventoryItem(
            path='README.md', extension='.md',
            size_bytes=10, sections=[], line_count=1,
        )]
        purposes = [DeclaredPurpose(
            file='README.md', title_purpose='Skipped',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=[],
        )]
        adapter = MockLLMAdapter(responses={'README.md': None})
        count = _enrich_with_llm(inventory, purposes, tmp_path, adapter)
        assert count == 0

    def test_constraint_merge(self, tmp_path):
        _write_file(tmp_path / 'doc.md', '# API\n')
        inventory = [DocInventoryItem(
            path='doc.md', extension='.md',
            size_bytes=10, sections=[], line_count=1,
        )]
        purposes = [DeclaredPurpose(
            file='doc.md', title_purpose='API',
            keywords=[], code_refs=[], sections=[],
            framework_signals=[], constraints=['MUST validate input'],
        )]
        adapter = MockLLMAdapter(responses={
            'doc.md': {
                'semantic_purpose': 'API gateway',
                'constraints': ['MUST validate input', 'SHOULD log errors'],
            },
        })
        _enrich_with_llm(inventory, purposes, tmp_path, adapter)
        # Original constraint + new constraint (no duplicate)
        assert 'MUST validate input' in purposes[0].constraints
        assert 'SHOULD log errors' in purposes[0].constraints
        assert purposes[0].constraints.count('MUST validate input') == 1


# ── LLMAdapter Protocol ─────────────────────────────────────────────────


class TestLLMAdapterProtocol:
    def test_mock_adapter_implements_protocol(self):
        adapter = MockLLMAdapter()
        assert isinstance(adapter, LLMAdapter)

    def test_failing_adapter_implements_protocol(self):
        adapter = FailingLLMAdapter()
        assert isinstance(adapter, LLMAdapter)


# ── Integration: run_contextome_intelligence ─────────────────────────────


class TestRunContextomeIntelligence:
    def test_empty_directory(self, tmp_path):
        result = run_contextome_intelligence(str(tmp_path))
        assert isinstance(result, ContextomeIntelligence)
        assert result.doc_count == 0
        assert result.inventory == []
        assert result.declared_purposes == []
        assert result.symmetry_seeds == []
        assert result.purpose_priors == {}
        assert result.llm_used is False

    def test_basic_repo(self, tmp_path):
        _write_file(tmp_path / 'README.md',
                     '# My Project\n\n## Installation\n\n## Usage\n')
        _write_file(tmp_path / 'docs' / 'api.md',
                     '# API Reference\n\nUses FastAPI and PostgreSQL.\n')
        _write_file(tmp_path / 'src' / 'main.py', 'print("hello")')

        result = run_contextome_intelligence(str(tmp_path))
        assert result.doc_count == 2
        assert len(result.inventory) == 2
        assert len(result.declared_purposes) == 2
        assert result.purpose_coverage > 0
        assert result.deterministic_signals > 0

    def test_with_config_file_signals(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# App\n')
        _write_file(tmp_path / 'requirements.txt', 'fastapi\nsqlalchemy\n')

        result = run_contextome_intelligence(str(tmp_path))
        # Config signals should be injected into root-level docs
        root_dp = next(dp for dp in result.declared_purposes if dp.file == 'README.md')
        assert 'FastAPI' in root_dp.framework_signals

    def test_symmetry_seeds_generated(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root Project\n')
        (tmp_path / 'src' / 'auth').mkdir(parents=True)
        _write_file(tmp_path / 'docs' / 'auth.md',
                     '# Authentication\n\nSee `src/auth/handler.py`.\n')

        result = run_contextome_intelligence(str(tmp_path))
        assert len(result.symmetry_seeds) >= 1

    def test_purpose_priors_generated(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root\n')
        (tmp_path / 'src' / 'auth').mkdir(parents=True)
        _write_file(tmp_path / 'docs' / 'auth.md', '# Authentication Service\n')

        result = run_contextome_intelligence(str(tmp_path))
        assert len(result.purpose_priors) >= 1

    def test_with_llm_adapter(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n\nA project.')
        adapter = MockLLMAdapter()

        result = run_contextome_intelligence(str(tmp_path), llm_adapter=adapter)
        assert result.llm_used is True
        assert result.enriched_signals > 0
        assert len(adapter.calls) >= 1

    def test_with_failing_llm(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n')
        adapter = FailingLLMAdapter()

        result = run_contextome_intelligence(str(tmp_path), llm_adapter=adapter)
        assert result.llm_used is True
        assert result.enriched_signals == 0

    def test_exclude_paths(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root\n')
        _write_file(tmp_path / 'vendor' / 'lib.md', '# Vendor Lib\n')

        result = run_contextome_intelligence(str(tmp_path), exclude_paths=['vendor'])
        paths = [item.path for item in result.inventory]
        assert 'README.md' in paths
        assert not any('vendor' in p for p in paths)

    def test_to_dict_serialization(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Project\n\nUses Django.')

        result = run_contextome_intelligence(str(tmp_path))
        d = result.to_dict()
        assert isinstance(d, dict)
        assert 'inventory' in d
        assert 'declared_purposes' in d
        assert 'symmetry_seeds' in d
        assert 'purpose_priors' in d
        assert 'doc_count' in d
        assert 'purpose_coverage' in d
        assert 'deterministic_signals' in d
        assert 'enriched_signals' in d
        assert 'llm_used' in d

    def test_purpose_coverage_calculation(self, tmp_path):
        # 2 docs with purpose, 1 without
        _write_file(tmp_path / 'README.md', '## No H1 heading here\n')
        _write_file(tmp_path / 'docs' / 'api.md', '# API Guide\n')
        _write_file(tmp_path / 'docs' / 'setup.md', '# Setup Guide\n')

        result = run_contextome_intelligence(str(tmp_path))
        # README has no H1 and is excluded from title fallback
        # api.md and setup.md have H1 headings
        assert result.doc_count == 3
        assert 0.0 < result.purpose_coverage <= 1.0

    def test_hot_skip_dirs_excluded(self, tmp_path):
        _write_file(tmp_path / 'README.md', '# Root\n')
        _write_file(tmp_path / 'node_modules' / 'pkg' / 'README.md', '# Pkg\n')
        _write_file(tmp_path / '.venv' / 'doc.md', '# Venv doc\n')

        result = run_contextome_intelligence(str(tmp_path))
        assert result.doc_count == 1

    def test_with_real_collider_output(self):
        """Test against actual repo if available."""
        import json

        output_file = Path('/tmp/collider_self_test6/unified_analysis.json')
        if not output_file.exists():
            pytest.skip('No real Collider output available')

        with open(output_file) as f:
            data = json.load(f)

        ctx = data.get('contextome')
        if ctx is None:
            pytest.skip('Collider output has no contextome')

        assert isinstance(ctx, dict)
        assert 'doc_count' in ctx
        assert 'inventory' in ctx
        assert 'declared_purposes' in ctx


# ── Data Contract Tests ──────────────────────────────────────────────────


class TestDataContracts:
    def test_doc_inventory_item_to_dict(self):
        item = DocInventoryItem(
            path='docs/api.md',
            extension='.md',
            size_bytes=1024,
            sections=[{'level': 1, 'title': 'API'}],
            line_count=50,
        )
        d = item.to_dict()
        assert d == {
            'path': 'docs/api.md',
            'extension': '.md',
            'size_bytes': 1024,
            'sections': [{'level': 1, 'title': 'API'}],
            'line_count': 50,
        }

    def test_contextome_intelligence_to_dict_roundtrip(self):
        ci = ContextomeIntelligence(
            inventory=[],
            declared_purposes=[],
            symmetry_seeds=[],
            purpose_priors={},
            llm_used=False,
            doc_count=0,
            purpose_coverage=0.0,
            deterministic_signals=0,
            enriched_signals=0,
        )
        d = ci.to_dict()
        assert d['doc_count'] == 0
        assert d['llm_used'] is False
        assert d['inventory'] == []
