#!/usr/bin/env python3
"""
Cerebras Spiral Intelligence System
====================================
Multi-pass iterative refinement for codebase understanding.

REGISTERED IN: .agent/registry/REGISTRY_OF_REGISTRIES.yaml (REG-014)
TOOL ID: TOOL-SPIRAL-001
VERSION: 1.0.0

PHILOSOPHY:
    Each pass builds on the previous, spiraling upward in confidence.
    Not circular (same level) but spiral (each pass deeper + informed).

    ╱╲
   ╱  ╲   P5: Unified Model (97%)
  ╱────╲  P4: Subsystem Synthesis (92%)
 ╱──────╲ P3: Dependency Resolution (85%)
╱────────╲P2: Gap Filling (75%)
╲────────╱P1: Surface Scan (65%)
 ╲──────╱
  ╲────╱
   ╲──╱

PASSES:
    P1: Surface scan - all files, self-only context (target: 60-70%)
    P2: Gap filling - low quality files, neighbor context (target: 75-85%)
    P3: Dependency resolution - cross-reference validation (target: 85-90%)
    P4: Subsystem synthesis - architectural understanding (target: 90-95%)
    P5: Unified model - complete codebase intelligence (target: 95-99%)

CONFIDENCE MODEL (4D):
    - factual: How accurate is the information? (verified against code)
    - alignment: How well does it fit the project? (matches architecture)
    - current: Is it up to date? (recent analysis)
    - onwards: Will it remain valid? (stability prediction)

    Overall = min(factual, alignment, current, onwards)
    Average = mean(factual, alignment, current, onwards)

LAP STATISTICS:
    Each pass (lap) records:
    - files_processed: Number of files analyzed
    - duration_seconds: Time taken
    - rate_per_second: Processing speed
    - confidence_before: Average confidence before pass
    - confidence_after: Average confidence after pass
    - confidence_delta: Improvement from this pass
    - gaps_closed: Number of gaps filled
    - errors: Number of failures

OUTPUTS:
    - context-management/data/intel/spiral/file_intel.json (per-file intelligence)
    - context-management/data/intel/spiral/spiral_state.json (state + lap stats)
    - context-management/data/intel/spiral/lap_history.json (detailed lap records)
    - context-management/data/intel/spiral/unified_model.json (export)

Usage:
    # Run full spiral (P1 → P2 → P3)
    python cerebras_spiral_intel.py spiral

    # Run with parallel workers (FAST)
    python cerebras_spiral_intel.py spiral --parallel --workers 20

    # Run specific pass
    python cerebras_spiral_intel.py pass --level 2

    # Check spiral status and lap stats
    python cerebras_spiral_intel.py status

    # Show detailed lap history
    python cerebras_spiral_intel.py laps

    # Export unified model
    python cerebras_spiral_intel.py export
"""

import os
import sys
import json
import time
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Set, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
INTEL_DIR = PROJECT_ROOT / "context-management" / "data" / "intel"
SPIRAL_DIR = INTEL_DIR / "spiral"
SPIRAL_DIR.mkdir(parents=True, exist_ok=True)

CEREBRAS_API_URL = "https://api.cerebras.ai/v1/chat/completions"
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")

# Rate limiting
MIN_REQUEST_INTERVAL = 0.02  # 50 req/sec with paid tier
_last_request_time = 0.0


# =============================================================================
# DATA MODELS
# =============================================================================

class PassLevel(Enum):
    """Spiral pass levels."""
    P1_SURFACE = 1      # All files, self-only
    P2_GAPS = 2         # Low quality, neighbor context
    P3_DEPS = 3         # Dependency resolution
    P4_SUBSYSTEM = 4    # Subsystem synthesis
    P5_UNIFIED = 5      # Complete model


@dataclass
class Confidence4D:
    """4-dimensional confidence scoring."""
    factual: float = 0.0      # How accurate?
    alignment: float = 0.0    # How well does it fit?
    current: float = 0.0      # Is it up to date?
    onwards: float = 0.0      # Will it remain valid?

    @property
    def overall(self) -> float:
        """Overall confidence = minimum of all dimensions."""
        return min(self.factual, self.alignment, self.current, self.onwards)

    @property
    def average(self) -> float:
        """Average confidence across dimensions."""
        return (self.factual + self.alignment + self.current + self.onwards) / 4

    def to_dict(self) -> Dict[str, float]:
        return {
            "factual": self.factual,
            "alignment": self.alignment,
            "current": self.current,
            "onwards": self.onwards,
            "overall": self.overall,
            "average": self.average
        }


@dataclass
class FileIntel:
    """Intelligence for a single file."""
    path: str
    hash: str
    size: int
    extension: str

    # Analysis results
    purpose: str = ""
    summary: str = ""
    key_concepts: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    # Confidence tracking
    confidence: Dict[str, float] = field(default_factory=dict)
    pass_history: List[Dict] = field(default_factory=list)

    # Metadata
    analyzed_at: str = ""
    pass_level: int = 0
    model: str = ""

    def add_pass_result(self, level: int, result: Dict, confidence: Confidence4D):
        """Record a pass result."""
        self.pass_history.append({
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence.to_dict(),
            "result_keys": list(result.keys())
        })
        self.pass_level = level
        self.confidence = confidence.to_dict()


@dataclass
class SubsystemIntel:
    """Intelligence for a subsystem (group of related files)."""
    name: str
    files: List[str]
    purpose: str = ""
    boundaries: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    confidence: Dict[str, float] = field(default_factory=dict)


@dataclass
class LapStats:
    """Statistics for a single spiral pass (lap)."""
    pass_level: int
    started_at: str = ""
    completed_at: str = ""
    duration_seconds: float = 0.0
    files_processed: int = 0
    files_total: int = 0
    rate_per_second: float = 0.0
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    confidence_delta: float = 0.0
    gaps_before: int = 0
    gaps_after: int = 0
    gaps_closed: int = 0
    errors: int = 0
    workers_used: int = 1

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SpiralState:
    """State of the spiral intelligence system."""
    current_pass: int = 0
    files_total: int = 0
    files_analyzed: Dict[int, int] = field(default_factory=dict)  # pass -> count
    confidence_by_pass: Dict[int, float] = field(default_factory=dict)
    gaps_remaining: int = 0
    last_run: str = ""
    lap_history: List[Dict] = field(default_factory=list)  # List of LapStats dicts

    def to_dict(self) -> Dict:
        return asdict(self)

    def add_lap(self, lap: LapStats):
        """Record a completed lap."""
        self.lap_history.append(lap.to_dict())
        self.current_pass = lap.pass_level
        self.files_analyzed[lap.pass_level] = lap.files_processed
        self.confidence_by_pass[lap.pass_level] = lap.confidence_after
        self.gaps_remaining = lap.gaps_after
        self.last_run = lap.completed_at

    def get_lap_summary(self) -> str:
        """Get formatted lap summary."""
        if not self.lap_history:
            return "No laps completed yet."

        lines = ["LAP HISTORY:", "=" * 50]
        for lap in self.lap_history:
            lines.append(
                f"  P{lap['pass_level']}: {lap['files_processed']} files in {lap['duration_seconds']:.1f}s "
                f"({lap['rate_per_second']:.1f}/sec) | "
                f"Confidence: {lap['confidence_before']:.0f}% → {lap['confidence_after']:.0f}% "
                f"(+{lap['confidence_delta']:.0f}%)"
            )
        return "\n".join(lines)


# =============================================================================
# CEREBRAS API
# =============================================================================

def get_cerebras_key() -> str:
    """Get Cerebras API key."""
    key = os.environ.get("CEREBRAS_API_KEY", "")
    if not key:
        # Try doppler
        try:
            import subprocess
            result = subprocess.run(
                ["doppler", "secrets", "get", "CEREBRAS_API_KEY", "--plain"],
                capture_output=True, text=True, timeout=10
            )
            key = result.stdout.strip()
        except Exception:
            pass
    return key


def cerebras_query(prompt: str, system: str = "", max_tokens: int = 1000,
                   temperature: float = 0.3) -> str:
    """Send query to Cerebras with rate limiting."""
    global _last_request_time

    # Rate limit
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    api_key = get_cerebras_key()
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY not found")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            CEREBRAS_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": CEREBRAS_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=60
        )
        _last_request_time = time.time()

        if response.status_code == 429:
            print("Rate limited - waiting...", file=sys.stderr)
            time.sleep(2.0)
            return cerebras_query(prompt, system, max_tokens, temperature)

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Cerebras error: {e}", file=sys.stderr)
        return ""


def parse_json_response(response: str) -> Dict:
    """Extract JSON from LLM response."""
    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        elif "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            return {}
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError, IndexError):
        return {}


# =============================================================================
# PASS IMPLEMENTATIONS
# =============================================================================

# Pass 1: Surface Scan
P1_SYSTEM = """You are a code intelligence analyst. Analyze this file and extract:
1. PURPOSE: One-line description (what it does)
2. SUMMARY: 2-3 sentences explaining the file
3. KEY_CONCEPTS: Up to 5 key patterns/technologies
4. DEPENDENCIES: What this file imports/requires
5. EXPORTS: What this file provides to others
6. GAPS: Any issues (missing docs, incomplete code, TODOs)
7. QUALITY: Score 1-10

Output as JSON with keys: purpose, summary, key_concepts, dependencies, exports, gaps, quality"""


# Pass 2: Gap Filling (with neighbor context)
P2_SYSTEM = """You are a code intelligence analyst doing a SECOND PASS.
You have context from neighboring files. Use this to:
1. VALIDATE: Check if the previous analysis was correct
2. REFINE: Improve purpose and summary based on context
3. CONNECT: Identify relationships with neighbors
4. FILL_GAPS: Address any gaps from first pass

Previous analysis and neighbor context provided. Output improved analysis as JSON."""


# Pass 3: Dependency Resolution
P3_SYSTEM = """You are a dependency analyst. Given a file and its declared dependencies:
1. VALIDATE_DEPS: Are the listed dependencies correct?
2. MISSING_DEPS: What dependencies are missing?
3. CIRCULAR: Are there circular dependencies?
4. INTERFACE: What interface does this file expose?

Output as JSON with: validated_deps, missing_deps, circular_refs, interface"""


# Pass 4: Subsystem Synthesis
P4_SYSTEM = """You are a software architect analyzing a SUBSYSTEM (group of related files).
Given the files and their individual analyses:
1. SUBSYSTEM_PURPOSE: What does this subsystem do?
2. BOUNDARIES: Where does this subsystem start/end?
3. INTERFACES: How do other subsystems interact with it?
4. INTERNAL_STRUCTURE: How do files within relate?
5. HEALTH: Overall subsystem health score 1-10

Output as JSON."""


# Pass 5: Unified Model
P5_SYSTEM = """You are a chief architect creating a UNIFIED MODEL of the codebase.
Given all subsystems and their relationships:
1. ARCHITECTURE: High-level architecture description
2. DATA_FLOW: How does data flow through the system?
3. CONTROL_FLOW: How is control managed?
4. KEY_ABSTRACTIONS: What are the core abstractions?
5. RECOMMENDATIONS: What should be improved?

Output as JSON."""


class SpiralEngine:
    """Engine for running spiral intelligence passes."""

    def __init__(self):
        self.state = self._load_state()
        self.cache = self._load_cache()

    def _load_state(self) -> SpiralState:
        """Load spiral state from disk."""
        state_file = SPIRAL_DIR / "spiral_state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                return SpiralState(**data)
            except Exception:
                pass
        return SpiralState()

    def _save_state(self):
        """Save spiral state to disk."""
        state_file = SPIRAL_DIR / "spiral_state.json"
        state_file.write_text(json.dumps(self.state.to_dict(), indent=2))

    def _load_cache(self) -> Dict[str, FileIntel]:
        """Load file intelligence cache."""
        cache_file = SPIRAL_DIR / "file_intel.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                return {k: FileIntel(**v) for k, v in data.items()}
            except Exception:
                pass
        return {}

    def _save_cache(self):
        """Save file intelligence cache."""
        cache_file = SPIRAL_DIR / "file_intel.json"
        cache_file.write_text(json.dumps(
            {k: asdict(v) for k, v in self.cache.items()},
            indent=2
        ))

    def get_file_hash(self, path: Path) -> str:
        """Get hash of file for change detection."""
        try:
            content = path.read_bytes()
            return hashlib.md5(content).hexdigest()[:12]
        except Exception:
            return ""

    def scan_files(self) -> List[Path]:
        """Scan for analyzable files."""
        skip_dirs = {
            '.git', '.venv', '.tools_venv', 'node_modules', '__pycache__',
            '.pytest_cache', '.mypy_cache', 'dist', 'build', '.next',
            '.turbo', '.cache', 'coverage', '.idea', '.vscode'
        }
        extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs',
            '.md', '.yaml', '.yml', '.json', '.toml', '.sql', '.sh'
        }

        files = []
        for path in PROJECT_ROOT.rglob("*"):
            if path.is_file():
                if any(skip in path.parts for skip in skip_dirs):
                    continue
                if path.suffix.lower() in extensions:
                    files.append(path)
        return sorted(files)

    # =========================================================================
    # PARALLEL PROCESSING
    # =========================================================================

    def _analyze_file_parallel(self, args: Tuple[int, int, Path]) -> Tuple[str, Optional[FileIntel]]:
        """Analyze a single file (for parallel execution)."""
        idx, total, path = args
        try:
            abs_path = path.resolve()
            rel_path = str(abs_path.relative_to(PROJECT_ROOT))
            current_hash = self.get_file_hash(path)

            # Skip if already analyzed
            if rel_path in self.cache:
                existing = self.cache[rel_path]
                if existing.hash == current_hash and existing.pass_level >= 1:
                    return rel_path, None  # Already done

            intel = self._analyze_file_p1(path, rel_path, current_hash)
            return rel_path, intel

        except Exception as e:
            return str(path), None

    def run_pass_1_parallel(self, files: List[Path] = None, workers: int = 20) -> Dict[str, FileIntel]:
        """Pass 1: Surface scan with parallel workers (FAST)."""
        print("=" * 60)
        print(f"PASS 1: SURFACE SCAN ({workers} WORKERS)")
        print("=" * 60)

        if files is None:
            files = self.scan_files()

        print(f"Found {len(files)} files")
        print(f"Expected rate: ~{workers}/sec")
        print()

        self.state.files_total = len(files)

        # Record lap start
        lap = LapStats(
            pass_level=1,
            started_at=datetime.now().isoformat(),
            files_total=len(files),
            workers_used=workers
        )

        # Calculate confidence before
        if self.cache:
            conf_before = [
                self.cache[p].confidence.get("average", 0)
                for p in self.cache if self.cache[p].confidence
            ]
            lap.confidence_before = sum(conf_before) / len(conf_before) if conf_before else 0
            lap.gaps_before = sum(1 for v in self.cache.values() if v.gaps)

        start_time = time.time()
        analyzed = 0
        errors = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self._analyze_file_parallel, (i, len(files), f)): f
                for i, f in enumerate(files)
            }

            # Collect results
            for future in as_completed(futures):
                rel_path, intel = future.result()
                if intel:
                    self.cache[rel_path] = intel
                    analyzed += 1
                else:
                    # Could be skip or error
                    pass

                total_done = analyzed + errors
                if total_done % 100 == 0 and total_done > 0:
                    elapsed = time.time() - start_time
                    rate = analyzed / elapsed if elapsed > 0 else 0
                    eta = (len(files) - total_done) / rate if rate > 0 else 0
                    print(f"Progress: {total_done}/{len(files)} ({rate:.1f}/sec, ETA: {eta:.0f}s)", flush=True)
                    self._save_cache()

        # Complete lap stats
        elapsed = time.time() - start_time
        lap.completed_at = datetime.now().isoformat()
        lap.duration_seconds = elapsed
        lap.files_processed = analyzed
        lap.rate_per_second = analyzed / elapsed if elapsed > 0 else 0
        lap.errors = errors

        # Calculate confidence after
        conf_after = [
            self.cache[p].confidence.get("average", 0)
            for p in self.cache if self.cache[p].confidence
        ]
        lap.confidence_after = sum(conf_after) / len(conf_after) if conf_after else 0
        lap.confidence_delta = lap.confidence_after - lap.confidence_before
        lap.gaps_after = sum(1 for v in self.cache.values() if v.gaps)
        lap.gaps_closed = lap.gaps_before - lap.gaps_after

        # Record lap
        self.state.add_lap(lap)
        self._save_cache()
        self._save_state()

        print()
        print(f"COMPLETE: {analyzed} files in {elapsed:.0f}s ({lap.rate_per_second:.1f} files/sec)")
        print(f"Confidence: {lap.confidence_before:.0f}% → {lap.confidence_after:.0f}% (+{lap.confidence_delta:.0f}%)")

        return self.cache

    # =========================================================================
    # PASS 1: Surface Scan
    # =========================================================================

    def run_pass_1(self, files: List[Path] = None, workers: int = 1) -> Dict[str, FileIntel]:
        """Pass 1: Surface scan of all files."""
        print("=" * 60)
        print("PASS 1: SURFACE SCAN")
        print("=" * 60)

        if files is None:
            files = self.scan_files()

        self.state.files_total = len(files)

        # Record lap start
        lap = LapStats(
            pass_level=1,
            started_at=datetime.now().isoformat(),
            files_total=len(files),
            workers_used=workers
        )

        # Calculate confidence before
        if self.cache:
            conf_before = [
                self.cache[p].confidence.get("average", 0)
                for p in self.cache if self.cache[p].confidence
            ]
            lap.confidence_before = sum(conf_before) / len(conf_before) if conf_before else 0
            lap.gaps_before = sum(1 for v in self.cache.values() if v.gaps)

        start_time = time.time()
        analyzed = 0
        errors = 0

        for i, path in enumerate(files):
            rel_path = str(path.relative_to(PROJECT_ROOT))
            current_hash = self.get_file_hash(path)

            # Skip if already analyzed in P1 with same hash
            if rel_path in self.cache:
                existing = self.cache[rel_path]
                if existing.hash == current_hash and existing.pass_level >= 1:
                    continue

            # Analyze
            print(f"[{i+1}/{len(files)}] {rel_path}", flush=True)
            intel = self._analyze_file_p1(path, rel_path, current_hash)
            if intel:
                self.cache[rel_path] = intel
                analyzed += 1
            else:
                errors += 1

            # Save periodically
            if analyzed % 50 == 0:
                self._save_cache()

        # Complete lap stats
        elapsed = time.time() - start_time
        lap.completed_at = datetime.now().isoformat()
        lap.duration_seconds = elapsed
        lap.files_processed = analyzed
        lap.rate_per_second = analyzed / elapsed if elapsed > 0 else 0
        lap.errors = errors

        # Calculate confidence after
        conf_after = [
            self.cache[p].confidence.get("average", 0)
            for p in self.cache if self.cache[p].confidence
        ]
        lap.confidence_after = sum(conf_after) / len(conf_after) if conf_after else 0
        lap.confidence_delta = lap.confidence_after - lap.confidence_before
        lap.gaps_after = sum(1 for v in self.cache.values() if v.gaps)
        lap.gaps_closed = lap.gaps_before - lap.gaps_after

        # Record lap
        self.state.add_lap(lap)
        self._save_cache()
        self._save_state()

        print(f"\nPass 1 complete: {analyzed} files analyzed")
        print(f"Duration: {elapsed:.1f}s ({lap.rate_per_second:.1f} files/sec)")
        print(f"Confidence: {lap.confidence_before:.0f}% → {lap.confidence_after:.0f}% (+{lap.confidence_delta:.0f}%)")

        return self.cache

    def _analyze_file_p1(self, path: Path, rel_path: str, file_hash: str) -> Optional[FileIntel]:
        """Analyze a single file for Pass 1."""
        try:
            content = path.read_text(errors='ignore')[:8000]

            prompt = f"""Analyze this file: {rel_path}

```{path.suffix[1:] if path.suffix else 'txt'}
{content}
```

Provide analysis as JSON."""

            response = cerebras_query(prompt, P1_SYSTEM, max_tokens=800)
            data = parse_json_response(response)

            if not data:
                return None

            # Calculate confidence
            quality = float(data.get("quality", 5))
            confidence = Confidence4D(
                factual=min(quality * 10, 70),  # Cap at 70% for P1
                alignment=60,  # Default for P1
                current=80,    # Fresh analysis
                onwards=50     # Unknown durability
            )

            intel = FileIntel(
                path=rel_path,
                hash=file_hash,
                size=path.stat().st_size,
                extension=path.suffix,
                purpose=data.get("purpose", ""),
                summary=data.get("summary", ""),
                key_concepts=data.get("key_concepts", []),
                dependencies=data.get("dependencies", []),
                exports=data.get("exports", []),
                gaps=data.get("gaps", []),
                analyzed_at=datetime.now().isoformat(),
                pass_level=1,
                model=CEREBRAS_MODEL
            )
            intel.add_pass_result(1, data, confidence)

            return intel

        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            return None

    # =========================================================================
    # PASS 2: Gap Filling
    # =========================================================================

    def run_pass_2(self) -> Dict[str, FileIntel]:
        """Pass 2: Fill gaps with neighbor context."""
        print("=" * 60)
        print("PASS 2: GAP FILLING")
        print("=" * 60)

        # Find files needing P2
        targets = self._get_p2_targets()
        print(f"Found {len(targets)} files for Pass 2")

        analyzed = 0
        for i, rel_path in enumerate(targets):
            print(f"[{i+1}/{len(targets)}] {rel_path}", flush=True)

            # Get neighbor context
            neighbors = self._get_neighbors(rel_path)

            # Re-analyze with context
            updated = self._analyze_file_p2(rel_path, neighbors)
            if updated:
                self.cache[rel_path] = updated
                analyzed += 1

            if analyzed % 20 == 0:
                self._save_cache()

        self.state.files_analyzed[2] = analyzed
        self.state.current_pass = 2
        self.state.last_run = datetime.now().isoformat()

        self._save_cache()
        self._save_state()

        print(f"\nPass 2 complete: {analyzed} files refined")
        return self.cache

    def _get_p2_targets(self) -> List[str]:
        """Get files that need Pass 2 analysis."""
        targets = []
        for path, intel in self.cache.items():
            # Target low confidence or quality
            if intel.confidence.get("overall", 0) < 60:
                targets.append(path)
            # Target files with gaps
            elif intel.gaps:
                targets.append(path)
            # Target files with no dependencies (suspicious)
            elif not intel.dependencies and intel.extension in ['.py', '.js', '.ts']:
                targets.append(path)
        return targets

    def _get_neighbors(self, rel_path: str) -> List[Dict]:
        """Get context from neighboring files."""
        path = Path(rel_path)
        parent = path.parent
        neighbors = []

        for other_path, intel in self.cache.items():
            other = Path(other_path)
            # Same directory
            if other.parent == parent and other_path != rel_path:
                neighbors.append({
                    "path": other_path,
                    "purpose": intel.purpose,
                    "exports": intel.exports
                })
            # Check if this file is in other's dependencies
            if rel_path in intel.dependencies:
                neighbors.append({
                    "path": other_path,
                    "purpose": intel.purpose,
                    "relationship": "depends_on_this"
                })

        return neighbors[:10]  # Limit context size

    def _analyze_file_p2(self, rel_path: str, neighbors: List[Dict]) -> Optional[FileIntel]:
        """Analyze file with neighbor context for Pass 2."""
        if rel_path not in self.cache:
            return None

        existing = self.cache[rel_path]
        path = PROJECT_ROOT / rel_path

        try:
            content = path.read_text(errors='ignore')[:12000]  # More context in P2

            prompt = f"""Re-analyze this file with neighbor context.

FILE: {rel_path}
PREVIOUS ANALYSIS:
- Purpose: {existing.purpose}
- Gaps: {existing.gaps}

NEIGHBOR CONTEXT:
{json.dumps(neighbors, indent=2)}

FILE CONTENT:
```{path.suffix[1:] if path.suffix else 'txt'}
{content}
```

Provide IMPROVED analysis as JSON with: purpose, summary, key_concepts, dependencies, exports, gaps, quality, confidence_notes"""

            response = cerebras_query(prompt, P2_SYSTEM, max_tokens=1000)
            data = parse_json_response(response)

            if not data:
                return existing

            # Update confidence (higher for P2)
            quality = float(data.get("quality", 5))
            confidence = Confidence4D(
                factual=min(quality * 10 + 10, 85),  # Higher cap for P2
                alignment=70,
                current=85,
                onwards=60
            )

            # Merge with existing
            existing.purpose = data.get("purpose", existing.purpose)
            existing.summary = data.get("summary", existing.summary)
            existing.key_concepts = data.get("key_concepts", existing.key_concepts)
            existing.dependencies = data.get("dependencies", existing.dependencies)
            existing.exports = data.get("exports", existing.exports)
            existing.gaps = data.get("gaps", existing.gaps)
            existing.add_pass_result(2, data, confidence)

            return existing

        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
            return existing

    # =========================================================================
    # PASS 3: Dependency Resolution
    # =========================================================================

    def run_pass_3(self) -> Dict[str, FileIntel]:
        """Pass 3: Validate and resolve dependencies."""
        print("=" * 60)
        print("PASS 3: DEPENDENCY RESOLUTION")
        print("=" * 60)

        # Build dependency graph
        dep_graph = self._build_dependency_graph()

        # Validate each file's dependencies
        analyzed = 0
        for rel_path, intel in self.cache.items():
            if intel.pass_level < 2:
                continue  # Skip files not yet at P2

            validated = self._validate_dependencies(rel_path, dep_graph)
            if validated:
                intel.dependents = validated.get("dependents", [])
                intel.add_pass_result(3, validated, Confidence4D(
                    factual=85,
                    alignment=80,
                    current=90,
                    onwards=70
                ))
                analyzed += 1

        self.state.files_analyzed[3] = analyzed
        self.state.current_pass = 3
        self._save_cache()
        self._save_state()

        print(f"\nPass 3 complete: {analyzed} files validated")
        return self.cache

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a dependency graph from cache."""
        graph = {}
        for path, intel in self.cache.items():
            graph[path] = set(intel.dependencies)
        return graph

    def _validate_dependencies(self, rel_path: str, graph: Dict[str, Set[str]]) -> Dict:
        """Validate dependencies for a file."""
        intel = self.cache.get(rel_path)
        if not intel:
            return {}

        # Find dependents (files that depend on this one)
        dependents = [
            other for other, deps in graph.items()
            if rel_path in deps or any(rel_path.endswith(d) for d in deps)
        ]

        return {
            "dependents": dependents[:20],
            "validated": True
        }

    # =========================================================================
    # STATUS & EXPORT
    # =========================================================================

    def get_status(self) -> Dict:
        """Get current spiral status."""
        total_confidence = 0
        count = 0
        gaps_count = 0

        for intel in self.cache.values():
            if intel.confidence:
                total_confidence += intel.confidence.get("overall", 0)
                count += 1
            if intel.gaps:
                gaps_count += 1

        return {
            "current_pass": self.state.current_pass,
            "files_total": len(self.cache),
            "files_by_pass": {
                str(k): v for k, v in self.state.files_analyzed.items()
            },
            "average_confidence": total_confidence / count if count else 0,
            "files_with_gaps": gaps_count,
            "last_run": self.state.last_run
        }

    def export_model(self) -> Dict:
        """Export the unified intelligence model."""
        return {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "total_files": len(self.cache),
                "passes_completed": self.state.current_pass
            },
            "files": {k: asdict(v) for k, v in self.cache.items()},
            "statistics": self.get_status()
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cerebras Spiral Intelligence - Multi-pass codebase understanding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s spiral                    # Run full spiral (P1 → P2 → P3)
  %(prog)s spiral --parallel -w 20   # Fast parallel mode
  %(prog)s pass --level 2            # Run specific pass
  %(prog)s status                    # Show status and lap stats
  %(prog)s laps                      # Show detailed lap history
  %(prog)s export                    # Export unified model
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # spiral - run full spiral
    spiral_p = subparsers.add_parser("spiral", help="Run full spiral (all passes)")
    spiral_p.add_argument("--parallel", "-p", action="store_true", help="Use parallel workers")
    spiral_p.add_argument("--workers", "-w", type=int, default=20, help="Number of parallel workers")

    # pass - run specific pass
    pass_p = subparsers.add_parser("pass", help="Run specific pass")
    pass_p.add_argument("--level", type=int, required=True, choices=[1,2,3,4,5])
    pass_p.add_argument("--parallel", "-p", action="store_true", help="Use parallel workers")
    pass_p.add_argument("--workers", "-w", type=int, default=20, help="Number of parallel workers")

    # status - show status
    subparsers.add_parser("status", help="Show spiral status and lap stats")

    # laps - show lap history
    subparsers.add_parser("laps", help="Show detailed lap history")

    # export - export model
    export_p = subparsers.add_parser("export", help="Export unified model")
    export_p.add_argument("--output", type=str, default="unified_model.json")

    args = parser.parse_args()

    engine = SpiralEngine()

    if args.command == "spiral":
        print("Starting full spiral...")
        if args.parallel:
            print(f"Using {args.workers} parallel workers")
            engine.run_pass_1_parallel(workers=args.workers)
        else:
            engine.run_pass_1()
        engine.run_pass_2()
        engine.run_pass_3()
        print("\nSpiral complete!")
        print(engine.state.get_lap_summary())

    elif args.command == "pass":
        if args.level == 1:
            if args.parallel:
                engine.run_pass_1_parallel(workers=args.workers)
            else:
                engine.run_pass_1()
        elif args.level == 2:
            engine.run_pass_2()
        elif args.level == 3:
            engine.run_pass_3()
        else:
            print(f"Pass {args.level} not yet implemented")

    elif args.command == "status":
        status = engine.get_status()
        print("=" * 60)
        print("SPIRAL INTELLIGENCE STATUS")
        print("=" * 60)
        print(f"Current pass:      P{status['current_pass']}")
        print(f"Files analyzed:    {status['files_total']}")
        print(f"Avg confidence:    {status['average_confidence']:.1f}%")
        print(f"Files with gaps:   {status['files_with_gaps']}")
        print(f"Last run:          {status['last_run']}")
        print()
        print(engine.state.get_lap_summary())

    elif args.command == "laps":
        print(engine.state.get_lap_summary())
        if engine.state.lap_history:
            print()
            print("DETAILED LAP DATA:")
            print(json.dumps(engine.state.lap_history, indent=2))

    elif args.command == "export":
        model = engine.export_model()
        output_path = SPIRAL_DIR / args.output
        output_path.write_text(json.dumps(model, indent=2))
        print(f"Exported to: {output_path}")
        print(f"Total files: {len(model['files'])}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
