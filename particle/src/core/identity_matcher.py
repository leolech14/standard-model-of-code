"""
Identity Matcher for Wave-Particle Symmetry.
Matches documentation references to code symbols.
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class MatchResult:
    """Result of matching a wave node to particle nodes."""
    wave_id: str
    particle_id: Optional[str]
    confidence: float
    match_type: str  # "exact", "qualified", "fuzzy", "unresolved"
    rationale: str


@dataclass
class SymmetryResult:
    """Complete symmetry analysis result."""
    matched: List[MatchResult]
    undocumented: List[str]  # Particle nodes without Wave match
    orphan_docs: List[str]   # Wave nodes without Particle match

    @property
    def symmetry_score(self) -> float:
        """
        Compute symmetry score.

        Score = (high-confidence matches) / (total particle nodes)
        High confidence = >= 0.75
        """
        if not self.matched and not self.undocumented:
            return 1.0
        total = len(self.matched) + len(self.undocumented)
        return len([m for m in self.matched if m.confidence >= 0.75]) / total if total > 0 else 0.0


class IdentityMatcher:
    """Matches Wave (docs) to Particle (code) symbols."""

    def __init__(self, threshold: float = 0.75):
        """
        Initialize the identity matcher.

        Args:
            threshold: Minimum confidence score for fuzzy matches (default 0.75)
        """
        self.threshold = threshold

    def match(self, wave_ids: List[str], particle_ids: List[str]) -> SymmetryResult:
        """
        Match wave references to particle symbols.

        Args:
            wave_ids: List of symbol names from documentation
            particle_ids: List of symbol names from code

        Returns:
            SymmetryResult with matched, undocumented, and orphan lists
        """
        # Normalize inputs
        normalized_wave = [self._normalize(wid) for wid in wave_ids]
        normalized_particle = [self._normalize(pid) for pid in particle_ids]

        # Track which particles have been matched
        matched_particles = set()
        matched_results = []
        orphan_docs = []

        # Match each wave ID
        for wave_id, normalized_wave_id in zip(wave_ids, normalized_wave):
            match_result = self._match_single(
                normalized_wave_id,
                normalized_particle,
                particle_ids
            )

            if match_result.particle_id:
                matched_results.append(match_result)
                # Track the original particle ID
                matched_particles.add(match_result.particle_id)
            else:
                # No match found - orphan documentation
                orphan_docs.append(wave_id)

        # Find undocumented particles (particles without wave match)
        undocumented = [
            pid for pid in particle_ids
            if pid not in matched_particles
        ]

        return SymmetryResult(
            matched=matched_results,
            undocumented=undocumented,
            orphan_docs=orphan_docs
        )

    def _match_single(
        self,
        wave_id: str,
        normalized_particle_ids: List[str],
        original_particle_ids: List[str]
    ) -> MatchResult:
        """
        Match a single wave ID against all particles.

        Args:
            wave_id: Normalized wave identifier
            normalized_particle_ids: Normalized particle identifiers
            original_particle_ids: Original (non-normalized) particle identifiers

        Returns:
            MatchResult with best match found
        """
        # Layer 1: Exact match
        for normalized_pid, original_pid in zip(normalized_particle_ids, original_particle_ids):
            if wave_id == normalized_pid:
                return MatchResult(
                    wave_id=wave_id,
                    particle_id=original_pid,
                    confidence=1.0,
                    match_type="exact",
                    rationale="Exact match"
                )

        # Layer 2: Qualified name containment
        for normalized_pid, original_pid in zip(normalized_particle_ids, original_particle_ids):
            # Check if wave_id is contained in the qualified name
            # e.g., "validate" matches "UserService.validate"
            if wave_id in normalized_pid or normalized_pid.endswith(f".{wave_id}"):
                return MatchResult(
                    wave_id=wave_id,
                    particle_id=original_pid,
                    confidence=0.95,
                    match_type="qualified",
                    rationale=f"Contained in {original_pid}"
                )

        # Layer 3: Fuzzy match
        best_match, best_score = self._fuzzy_match(wave_id, normalized_particle_ids)

        if best_score >= self.threshold and best_match is not None:
            # Find the original particle ID
            best_index = normalized_particle_ids.index(best_match)
            original_pid = original_particle_ids[best_index]

            return MatchResult(
                wave_id=wave_id,
                particle_id=original_pid,
                confidence=best_score,
                match_type="fuzzy",
                rationale=f"Fuzzy match ({best_score:.2f})"
            )

        # No match found
        return MatchResult(
            wave_id=wave_id,
            particle_id=None,
            confidence=best_score,
            match_type="unresolved",
            rationale="No match found"
        )

    def _fuzzy_match(self, target: str, candidates: List[str]) -> Tuple[Optional[str], float]:
        """
        Find best fuzzy match using SequenceMatcher.

        Args:
            target: String to match
            candidates: List of candidate strings

        Returns:
            Tuple of (best_match, best_score)
        """
        best_match = None
        best_score = 0.0

        for candidate in candidates:
            # Use difflib's SequenceMatcher (stdlib, no deps)
            score = SequenceMatcher(None, target.lower(), candidate.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = candidate

        return best_match, best_score

    def _normalize(self, name: str) -> str:
        """
        Normalize symbol name for matching.

        Strips parentheses and whitespace while preserving qualified names.

        Args:
            name: Symbol name to normalize

        Returns:
            Normalized symbol name
        """
        # Strip parentheses, whitespace
        return name.replace("()", "").replace("(", "").replace(")", "").strip()
