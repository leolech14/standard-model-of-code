"""
Tests for identity_matcher module.
"""
import pytest
from src.core.identity_matcher import IdentityMatcher, MatchResult, SymmetryResult


def test_exact_match():
    """Test exact matching of wave to particle IDs."""
    matcher = IdentityMatcher()
    wave_ids = ["validate", "create"]
    particle_ids = ["validate", "create", "delete"]

    result = matcher.match(wave_ids, particle_ids)

    # Both should match exactly
    exact_matches = [m for m in result.matched if m.match_type == "exact"]
    assert len(exact_matches) == 2
    assert all(m.confidence == 1.0 for m in exact_matches)


def test_qualified_name_match():
    """Test matching when wave ID is contained in qualified particle name."""
    matcher = IdentityMatcher()
    wave_ids = ["validate"]  # Doc just says "validate"
    particle_ids = ["UserService.validate", "OtherService.process"]

    result = matcher.match(wave_ids, particle_ids)

    assert len(result.matched) == 1
    assert result.matched[0].match_type == "qualified"
    assert result.matched[0].confidence == 0.95
    assert result.matched[0].particle_id == "UserService.validate"


def test_fuzzy_match():
    """Test fuzzy matching with similarity threshold."""
    matcher = IdentityMatcher(threshold=0.75)
    wave_ids = ["validate_input"]
    particle_ids = ["validate_user_input", "process_data"]

    result = matcher.match(wave_ids, particle_ids)

    assert len(result.matched) == 1
    assert result.matched[0].match_type == "fuzzy"
    assert result.matched[0].confidence >= 0.75


def test_unresolved_match():
    """Test detection of orphan documentation (no particle match)."""
    matcher = IdentityMatcher(threshold=0.75)
    wave_ids = ["completely_different"]
    particle_ids = ["validate", "create"]

    result = matcher.match(wave_ids, particle_ids)

    assert len(result.orphan_docs) == 1
    assert "completely_different" in result.orphan_docs


def test_undocumented_detection():
    """Test detection of undocumented particles (no wave match)."""
    matcher = IdentityMatcher()
    wave_ids = ["validate"]
    particle_ids = ["validate", "create", "delete"]

    result = matcher.match(wave_ids, particle_ids)

    # "create" and "delete" are undocumented
    assert "create" in result.undocumented
    assert "delete" in result.undocumented
    assert len(result.undocumented) == 2


def test_symmetry_score():
    """Test symmetry score calculation."""
    matcher = IdentityMatcher()
    wave_ids = ["validate", "create"]
    particle_ids = ["validate", "create", "delete"]

    result = matcher.match(wave_ids, particle_ids)

    # 2 matched out of 3 total particle = 0.67
    assert 0.6 <= result.symmetry_score <= 0.7


def test_empty_inputs():
    """Test handling of empty input lists."""
    matcher = IdentityMatcher()

    # Both empty
    result = matcher.match([], [])
    assert result.symmetry_score == 1.0
    assert len(result.matched) == 0
    assert len(result.undocumented) == 0
    assert len(result.orphan_docs) == 0

    # Only wave empty
    result = matcher.match([], ["validate"])
    assert len(result.undocumented) == 1
    assert result.symmetry_score == 0.0

    # Only particle empty (orphan docs don't affect score - it's particle-centric)
    result = matcher.match(["validate"], [])
    assert len(result.orphan_docs) == 1
    # Score is 1.0 because there are no particles to document
    assert result.symmetry_score == 1.0


def test_normalization():
    """Test symbol name normalization."""
    matcher = IdentityMatcher()
    wave_ids = ["validate()"]
    particle_ids = ["validate", "create"]

    result = matcher.match(wave_ids, particle_ids)

    # Should strip parentheses and match
    assert len(result.matched) == 1
    assert result.matched[0].match_type == "exact"


def test_case_insensitive_fuzzy():
    """Test that fuzzy matching is case-insensitive."""
    matcher = IdentityMatcher(threshold=0.75)
    wave_ids = ["ValidateInput"]
    particle_ids = ["validate_input", "process_data"]

    result = matcher.match(wave_ids, particle_ids)

    # Should fuzzy match despite case difference
    assert len(result.matched) == 1
    assert result.matched[0].confidence >= 0.75


def test_multiple_qualified_matches():
    """Test that qualified matching picks the first match."""
    matcher = IdentityMatcher()
    wave_ids = ["validate"]
    particle_ids = ["UserService.validate", "AdminService.validate"]

    result = matcher.match(wave_ids, particle_ids)

    # Should match the first qualified name
    assert len(result.matched) == 1
    assert result.matched[0].match_type == "qualified"
    assert result.matched[0].particle_id == "UserService.validate"
