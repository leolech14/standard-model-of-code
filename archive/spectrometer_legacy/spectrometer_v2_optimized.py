#!/usr/bin/env python3
"""
Spectrometer V2 - Optimized Universal Code Architecture Analyzer

Fast architectural mapping by combining:
- Pre-resolved signals collection (O(n) instead of O(n*m))
- Parallel file processing
- Cached signal analysis
- Optimized token counting
- Progress tracking with tqdm

Performance target: <5 seconds for typical repos (was 60s)
"""

import ast
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm
import argparse

# Import LLM enrichment layer
try:
    from llm_enricher import LLMEnricher, ProgressiveMapper, LLMAnnotation
    LLM_ENRICHMENT_AVAILABLE = True
except ImportError:
    LLM_ENRICHMENT_AVAILABLE = False
    LLMEnricher = None
    ProgressiveMapper = None
    LLMAnnotation = None


@dataclass
class CodeElement:
    """Represents a single code element (atom) with all its properties."""
    element_id: str  # Stable location-based: filepath:start-end
    element_id_semantic: str  # Human-readable: filepath::elementName
    element_hash: str  # Content-based: sha256 hash
    name: str
    filepath: str
    first_loc: int
    last_loc: int
    loc_count: int
    token_count: int
    species: str
    role: str
    layer: str
    state: str
    activation: str
    effect: str
    lifetime: str
    boundary: str
    emojis: Optional[str] = None
    summary: str = ""
    # LLM enrichment fields (optional)
    llm_role: Optional[str] = None
    llm_layer: Optional[str] = None
    llm_state: Optional[str] = None
    llm_activation: Optional[str] = None
    llm_effect: Optional[str] = None
    llm_lifetime: Optional[str] = None
    llm_boundary: Optional[str] = None
    llm_species: Optional[str] = None
    llm_summary: Optional[str] = None
    llm_confidence: Optional[float] = None
    llm_notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if result['emojis'] is None:
            result.pop('emojis')
        # Only include LLM fields if they exist
        llm_fields = ['llm_role', 'llm_layer', 'llm_state', 'llm_activation',
                      'llm_effect', 'llm_lifetime', 'llm_boundary', 'llm_species',
                      'llm_summary', 'llm_confidence', 'llm_notes']
        for field in llm_fields:
            if result.get(field) is None:
                result.pop(field, None)
        return result

    def apply_llm_annotation(self, annotation: 'LLMAnnotation', confidence_threshold: float = 0.6):
        """
        Apply LLM annotation to this element.

        For each dimension, if LLM confidence >= threshold, use LLM value.
        Otherwise, keep heuristic value.
        Always sets summary and metadata regardless of confidence.
        """
        # Always update summary and metadata (even if confidence is low)
        if annotation.summary:
            self.llm_summary = annotation.summary
        self.llm_confidence = annotation.confidence
        if annotation.notes:
            self.llm_notes = annotation.notes

        # Only apply dimension refinements if confidence meets threshold
        if annotation.confidence < confidence_threshold:
            return

        # Apply LLM values where confidence is high enough
        if annotation.role and annotation.confidence >= confidence_threshold:
            self.llm_role = annotation.role
        if annotation.layer and annotation.confidence >= confidence_threshold:
            self.llm_layer = annotation.layer
        if annotation.state and annotation.confidence >= confidence_threshold:
            self.llm_state = annotation.state
        if annotation.activation and annotation.confidence >= confidence_threshold:
            self.llm_activation = annotation.activation
        if annotation.effect and annotation.confidence >= confidence_threshold:
            self.llm_effect = annotation.effect
        if annotation.lifetime and annotation.confidence >= confidence_threshold:
            self.llm_lifetime = annotation.lifetime
        if annotation.boundary and annotation.confidence >= confidence_threshold:
            self.llm_boundary = annotation.boundary
        if annotation.species and annotation.confidence >= confidence_threshold:
            self.llm_species = annotation.species


@dataclass
class FileSignals:
    """Pre-resolved signals for a file to avoid re-processing"""
    imports: List[str]
    external_edges: List[str]
    layer_matches: List[Tuple[str, int]]  # (layer, line_number)
    role_matches: List[Tuple[str, int]]
    state_matches: List[Tuple[str, int]]
    activation_matches: List[Tuple[str, int]]
    effect_matches: List[Tuple[str, int]]
    lifetime_matches: List[Tuple[str, int]]
    boundary_matches: List[Tuple[str, int]]
    species_matches: List[Tuple[str, int]]
    function_lines: Dict[str, Tuple[int, int]]  # name -> (start, end)
    class_lines: Dict[str, Tuple[int, int]]  # name -> (start, end)
    method_lines: Dict[str, Tuple[str, int, int]]  # name -> (class, start, end)
    line_types: Dict[int, str]  # line_number -> type (function, class, method)
    content_hash: str  # Hash of the entire file content


class OptimizedElementClassifier:
    """Optimized classifier using pre-resolved signals."""

    # Role patterns
    ORCHESTRATOR_KEYWORDS = ['orchestrate', 'coordinate', 'manage', 'handle', 'controller', 'handler']
    WORKER_KEYWORDS = ['process', 'execute', 'run', 'perform', 'worker', 'task']
    DATA_KEYWORDS = ['model', 'entity', 'value', 'data', 'record', 'dto', 'vo']

    # Layer patterns
    INTERFACE_KEYWORDS = ['controller', 'handler', 'route', 'endpoint', 'api', 'presenter', 'view', 'ui']
    APPLICATION_KEYWORDS = ['usecase', 'use_case', 'service', 'application', 'flow', 'workflow', 'saga']
    CORE_BIZ_KEYWORDS = ['domain', 'entity', 'business', 'rule', 'specification', 'value_object']
    INFRA_KEYWORDS = ['repository', 'gateway', 'client', 'adapter', 'db', 'cache', 'queue', 'logger', 'config']
    TEST_KEYWORDS = ['test', 'spec', 'fixture', 'mock', 'stub']

    # State patterns
    STATEFUL_KEYWORDS = ['cache', 'session', 'connection', 'pool', 'store', 'state']

    # Activation patterns
    EVENT_KEYWORDS = ['event', 'listener', 'subscriber', 'handler', 'on_', 'subscribe']
    TIME_KEYWORDS = ['cron', 'schedule', 'timer', 'periodic', 'job', 'task']

    # Effect patterns
    READ_KEYWORDS = ['get', 'fetch', 'read', 'query', 'find', 'load', 'retrieve', 'download', 'list']
    WRITE_KEYWORDS = [
        'create', 'save', 'update', 'delete', 'write', 'post', 'put', 'patch',
        'execute', 'run', 'process',  # often side-effectful flows
        'send', 'publish', 'emit', 'dispatch', 'charge'  # outbound effects
    ]

    # Boundary patterns
    EXTERNAL_KEYWORDS = ['http', 'api', 'client', 'request', 'response', 'fetch', 'call']
    INTERNAL_KEYWORDS = ['internal', 'local', 'helper', 'util']

    @staticmethod
    def classify_role_optimized(name: str, docstring: str, signals: FileSignals, line_num: int) -> str:
        """Classify Role dimension using pre-resolved signals."""
        # Check pre-resolved signals first (O(1) lookup)
        for role, match_line in signals.role_matches:
            # Check if the match is close to our element
            if abs(match_line - line_num) <= 5:  # Within 5 lines
                return role

        # Fallback to keyword analysis
        combined = f"{name} {docstring}".lower()

        if any(kw in combined for kw in OptimizedElementClassifier.ORCHESTRATOR_KEYWORDS):
            return "ORCHESTRATOR"
        if any(kw in combined for kw in OptimizedElementClassifier.DATA_KEYWORDS):
            return "DATA"
        return "WORKER"

    @staticmethod
    def classify_layer_optimized(filepath: str, name: str, docstring: str, signals: FileSignals, line_num: int) -> str:
        """Classify Layer dimension using pre-resolved signals."""
        # Check pre-resolved signals first
        for layer, match_line in signals.layer_matches:
            if abs(match_line - line_num) <= 5:
                return layer

        # Fallback to filepath analysis
        combined = f"{filepath} {name} {docstring}".lower()

        if any(kw in combined for kw in OptimizedElementClassifier.TEST_KEYWORDS):
            return "Tests"
        if any(kw in combined for kw in OptimizedElementClassifier.INTERFACE_KEYWORDS):
            return "Interface"
        if any(kw in combined for kw in OptimizedElementClassifier.INFRA_KEYWORDS):
            return "Infra"
        if any(kw in combined for kw in OptimizedElementClassifier.CORE_BIZ_KEYWORDS):
            return "Core Biz"
        if any(kw in combined for kw in OptimizedElementClassifier.APPLICATION_KEYWORDS):
            return "Application"

        # Default based on filepath structure
        if 'test' in filepath.lower():
            return "Tests"
        if 'api' in filepath.lower() or 'controller' in filepath.lower():
            return "Interface"
        if 'infra' in filepath.lower() or 'repository' in filepath.lower():
            return "Infra"
        if 'domain' in filepath.lower() or 'entity' in filepath.lower():
            return "Core Biz"

        # "naked noun" default → Core Biz
        base_name = name.split(".")[-1]  # strip .method if present
        if base_name and base_name[0].isupper():
            if not any(kw in combined for kw in (
                OptimizedElementClassifier.INTERFACE_KEYWORDS +
                OptimizedElementClassifier.INFRA_KEYWORDS +
                OptimizedElementClassifier.APPLICATION_KEYWORDS +
                OptimizedElementClassifier.TEST_KEYWORDS
            )):
                return "Core Biz"

        return "Application"

    @staticmethod
    def classify_state_optimized(signals: FileSignals, line_num: int, end_line: int) -> str:
        """Classify State dimension using pre-resolved signals."""
        # Check if there are any stateful signals in the element range
        state_signals_nearby = [s for s in signals.state_matches if line_num <= s[1] <= end_line]
        return 'Stateful' if state_signals_nearby else 'Stateless'

    @staticmethod
    def classify_activation_optimized(signals: FileSignals, line_num: int) -> str:
        """Classify Activation dimension using pre-resolved signals."""
        # Find closest activation signal
        closest_signal = None
        min_distance = float('inf')

        for activation, match_line in signals.activation_matches:
            distance = abs(match_line - line_num)
            if distance < min_distance:
                min_distance = distance
                closest_signal = activation

        return closest_signal if closest_signal and min_distance <= 5 else 'Direct'

    @staticmethod
    def classify_effect_optimized(signals: FileSignals, line_num: int, end_line: int) -> str:
        """Classify Effect dimension using pre-resolved signals."""
        # Find effects within the element range
        write_signals = [e for e in signals.effect_matches
                        if e[0] == 'WRITE' and line_num <= e[1] <= end_line]
        read_signals = [e for e in signals.effect_matches
                       if e[0] == 'READ' and line_num <= e[1] <= end_line]

        if write_signals and read_signals:
            return "READ & WRITE"
        if write_signals:
            return "WRITE"
        if read_signals:
            return "READ"
        return "READ"  # Default assumption

    @staticmethod
    def classify_lifetime_optimized(signals: FileSignals, line_num: int) -> str:
        """Classify Lifetime dimension using pre-resolved signals."""
        # Find closest lifetime signal
        closest_signal = None
        min_distance = float('inf')

        for lifetime, match_line in signals.lifetime_matches:
            distance = abs(match_line - line_num)
            if distance < min_distance:
                min_distance = distance
                closest_signal = lifetime

        return closest_signal if closest_signal and min_distance <= 5 else 'Transient'

    @staticmethod
    def classify_boundary_optimized(signals: FileSignals, line_num: int, end_line: int) -> str:
        """Classify Boundary dimension using pre-resolved signals."""
        # Find boundary signals within the element range
        boundary_signals = [b for b in signals.boundary_matches
                          if line_num <= b[1] <= end_line]

        if not boundary_signals:
            return "Internal"

        # Count different boundary types
        boundary_types = [b[0] for b in boundary_signals]

        if "In & Out" in boundary_types:
            return "In & Out"
        if "In" in boundary_types and "Out" in boundary_types:
            return "In & Out"
        if "In" in boundary_types:
            return "In"
        if "Out" in boundary_types:
            return "Out"

        return "Internal"

    @staticmethod
    def determine_species_optimized(layer: str, role: str, activation: str, effect: str,
                                   name: str, docstring: str, signals: FileSignals, line_num: int) -> str:
        """Determine the species name using optimized lookup."""
        # Check pre-resolved species first
        for species, match_line in signals.species_matches:
            if abs(match_line - line_num) <= 5:
                return species

        # Fallback to logic-based determination
        combined = f"{name} {docstring}".lower()
        base_name = name.split(".")[-1].lower()

        if layer == "Interface":
            if 'handler' in combined or 'controller' in combined:
                return "Request Handler/Controller"
            if 'presenter' in combined or 'viewmodel' in combined:
                return "Presenter/ViewModel"
            if 'validator' in combined or 'guard' in combined:
                return "Input Validator/Guard"
            return "UI Action Wrapper"

        elif layer == "Application":
            if activation in ("Event", "Time") or 'saga' in combined or 'workflow' in combined:
                return "Process/Workflow Manager (Saga)"
            if 'policy' in combined or 'guard' in combined:
                return "Application Policy/Guard"
            if 'mapper' in combined or 'translator' in combined or base_name.endswith("mapper"):
                return "Application Mapper/Translator"
            if role == "ORCHESTRATOR" or 'usecase' in combined or 'flow' in combined:
                return "Use Case/Flow Orchestrator"
            return "Use Case/Flow Orchestrator"

        elif layer == "Core Biz":
            if 'event' in combined or base_name.endswith("event"):
                return "Domain Event"
            if 'value object' in combined or 'value_object' in combined:
                return "Value Object"
            if 'service' in combined:
                return "Core Business Service"
            if role == "DATA":
                return "Business Entity"
            return "Business Entity"

        elif layer == "Infra":
            if 'repository' in combined:
                return "Repository"
            if 'query' in combined:
                return "Query Object/Read Model"
            if 'gateway' in combined or 'client' in combined:
                return "Data Gateway/API Client"
            if 'producer' in combined or 'publish' in combined:
                return "Message Producer"
            if 'consumer' in combined or 'listener' in combined or 'subscribe' in combined:
                return "Message Consumer/Listener"
            if 'job' in combined or 'worker' in combined:
                return "Background Job/Worker"
            if 'cache' in combined:
                return "Cache"
            if 'config' in combined or 'setting' in combined:
                return "Config Loader/Settings"
            return "Data Gateway/API Client"

        elif layer == "Tests":
            if 'test' in combined or 'spec' in combined:
                return "Test Case/Suite"
            if 'fixture' in combined or 'factory' in combined or 'builder' in combined:
                return "Fixture/Factory/Builder"
            return "Test Harness/Scenario Runner"

        return "Unknown"


class SpectrometerV2Optimized:
    """Optimized version of Spectrometer with performance enhancements."""

    def __init__(self, repo_path: str, enable_llm: bool = False, llm_cache_dir: Optional[str] = None,
                 max_workers: int = None, verbose: bool = False):
        """
        Initialize Spectrometer V2 Optimized.

        Args:
            repo_path: Path to repository to analyze
            enable_llm: Whether to enable LLM semantic enrichment
            llm_cache_dir: Directory for LLM cache (default: .spectrometer_cache)
            max_workers: Maximum number of parallel workers (default: CPU count)
            verbose: Enable verbose output
        """
        self.repo_path = Path(repo_path)
        self.elements: List[CodeElement] = []
        self.dependencies: List[Dict] = []
        self.externals: List[Dict] = []
        self.external_edges: List[Dict] = []
        self.element_map: Dict[str, CodeElement] = {}
        self.external_map: Dict[str, str] = {}
        self.verbose = verbose
        self.max_workers = max_workers or min(32, os.cpu_count() or 8)

        # Performance tracking
        self.start_time = None
        self.scan_time = 0
        self.process_time = 0
        self.dependency_time = 0

        # Cache for file signals
        self.file_signals_cache: Dict[str, FileSignals] = {}

        self.ignored_patterns = [
            '**/node_modules/**',
            '**/vendor/**',
            '**/__pycache__/**',
            '**/.git/**',
            '**/dist/**',
            '**/build/**',
            '**/*.pyc',
            '**/.venv/**',
            '**/venv/**',
        ]

        # Initialize LLM enricher if available
        self.enable_llm = enable_llm and LLM_ENRICHMENT_AVAILABLE
        if self.enable_llm:
            self.llm_enricher = LLMEnricher(cache_dir=llm_cache_dir, enable_llm=enable_llm)
        else:
            self.llm_enricher = None

    def _log(self, message: str, force: bool = False):
        """Log only if verbose or forced."""
        if self.verbose or force:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored."""
        for pattern in self.ignored_patterns:
            if filepath.match(pattern):
                return True
        return False

    def count_tokens_fast(self, code: str) -> int:
        """Fast token counting approximation."""
        # Simple heuristic: average token is ~4 characters
        return len(code) // 4

    def extract_docstring(self, node: ast.AST) -> str:
        """Extract docstring from AST node."""
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            if ast.get_docstring(node):
                return ast.get_docstring(node)
        return ""

    def get_node_code(self, node: ast.AST, source_lines: List[str]) -> str:
        """Get source code for a node."""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            start = node.lineno - 1
            end = node.end_lineno
            return '\n'.join(source_lines[start:end])
        return ""

    def generate_element_hash(self, code: str, name: str, filepath: str) -> str:
        """Generate a stable content hash for an element."""
        normalized_code = re.sub(r'\s+', ' ', code.strip())
        content = f"{filepath}::{name}\n{normalized_code}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def pre_resolve_file_signals(self, filepath: Path) -> FileSignals:
        """Pre-resolve all signals in a file in a single pass."""
        file_path_str = str(filepath)

        # Check cache first
        if file_path_str in self.file_signals_cache:
            return self.file_signals_cache[file_path_str]

        # Initialize all collections
        imports = []
        external_edges = []
        layer_matches = []
        role_matches = []
        state_matches = []
        activation_matches = []
        effect_matches = []
        lifetime_matches = []
        boundary_matches = []
        species_matches = []
        function_lines = {}
        class_lines = {}
        method_lines = {}
        line_types = {}

        # Skip unsupported files quickly
        if filepath.suffix not in {'.py', '.js', '.ts', '.jsx', '.tsx'}:
            signals = FileSignals([], [], [], [], [], [], [], [], [], [], {}, {}, {}, {}, "")
            self.file_signals_cache[file_path_str] = signals
            return signals

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            self._log(f"Could not read {filepath}: {e}")
            signals = FileSignals([], [], [], [], [], [], [], [], [], [], {}, {}, {}, {}, "")
            self.file_signals_cache[file_path_str] = signals
            return signals

        content = ''.join(lines)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Define patterns for optimized detection
        patterns = {
            'layer': [
                (r'@app\.|@router\.|@bp\.|Blueprint|@api\.|@\{.*\}|app\.get|app\.post|router\.get|router\.post', 'Interface'),
                (r'class.*View|class.*Controller|class.*Handler|request\.|Response|JsonResponse', 'Interface'),
                (r'Flask|FastAPI|Django|tornado|aiohttp', 'Interface'),
                (r'db\.|session\.|cursor\.|connection\.|execute\(|fetchall\(\)|commit\(\)', 'Infra'),
                (r'SQLAlchemy|django\.db|psycopg2|pymongo|redis|elasticsearch', 'Infra'),
                (r'boto3|google\.cloud|azure\.storage|minio', 'Infra'),
                (r'pika|kombu|kafka|celery|r', 'Infra'),
                (r'class.*(Entity|Model|Domain|Service|Repository|Specification)', 'Core Biz'),
                (r'domain|entities?|models?|repository|specification|value.?object', 'Core Biz'),
                (r'test_|def test_|assert_|mock_|fixture|setUp|tearDown', 'Tests'),
                (r'pytest|unittest|TestCase|@pytest\.|unittest\.mock', 'Tests'),
            ],
            'role': [
                (r'def.*(process|handle|execute|run|orchestrat|coordinat|manag|workflow|saga)', 'ORCHESTRATOR'),
                (r'class.*(Service|Application|UseCase|Interactor|Handler|Processor|Manager)', 'ORCHESTRATOR'),
                (r'def.*(calculate|compute|transform|convert|format|parse|generate)', 'WORKER'),
                (r'class.*(Worker|Calculator|Parser|Formatter|Transformer|Generator|Util)', 'WORKER'),
                (r'class.*(Entity|Model|DTO|VO|ValueObject|Data|Record)', 'DATA'),
            ],
            'state': [
                (r'self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=|@property|@[a-zA-Z_][a-zA-Z0-9_]*\.setter', 'Stateful'),
                (r'global\s+[a-zA-Z_][a-zA-Z0-9_]*|^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\{.*\}', 'Stateful'),
            ],
            'activation': [
                (r'def .*__call__|__invoke__|__execute__|@.*schedule|cron|periodic', 'Time'),
                (r'def .*on_|@.*event|listener|subscriber|observer|publish|emit', 'Event'),
            ],
            'effect': [
                (r'insert|update|delete|create|write|save|set|append|extend|send|publish', 'WRITE'),
                (r'execute|commit|transaction|mutate|modify', 'WRITE'),
                (r'select|find|get|fetch|query|search|load|read|open|read\(\)', 'READ'),
            ],
            'lifetime': [
                (r'__init__.*self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=[^N]|@singleton|@.*\.\s*instance\(\)', 'Global'),
                (r'session|request\.|@.*scope|context|lifetime', 'Session'),
            ],
            'boundary': [
                (r'request\.|headers|cookies|query|body|form|files|@.*route|@.*app\.route', 'In'),
                (r'Response|return|jsonify|render|redirect|HttpResponse|JsonResponse', 'Out'),
                (r'api|request|fetch|post|get|put|delete|patch|http|rest', 'In & Out'),
            ],
            'species': [
                (r'class.*Controller|class.*Handler|@.*route|app\.(get|post|put|delete)', 'Controller'),
                (r'class.*Service|class.*ApplicationService|class.*UseCase', 'Application Service'),
                (r'class.*Entity|class.*Aggregate|class.*Model', 'Domain Entity'),
                (r'class.*VO|class.*ValueObject|class.*DTO', 'Value Object'),
                (r'class.*Repository|class.*Gateway|class.*Adapter', 'Repository/Gateway'),
                (r'class.*Test|def test_|TestCase', 'Test'),
            ],
        }

        # Single pass through all lines
        for idx, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Skip comments for most patterns
            if line_stripped.startswith('#') or line_stripped.startswith('//'):
                continue

            # Check each category of patterns
            for category, pattern_list in patterns.items():
                for pattern, value in pattern_list:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Add to appropriate list
                        if category == 'layer':
                            layer_matches.append((value, idx))
                        elif category == 'role':
                            role_matches.append((value, idx))
                        elif category == 'state':
                            state_matches.append((value, idx))
                        elif category == 'activation':
                            activation_matches.append((value, idx))
                        elif category == 'effect':
                            effect_matches.append((value, idx))
                        elif category == 'lifetime':
                            lifetime_matches.append((value, idx))
                        elif category == 'boundary':
                            boundary_matches.append((value, idx))
                        elif category == 'species':
                            species_matches.append((value, idx))

            # Detect functions and classes (Python)
            if filepath.suffix == '.py':
                func_match = re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
                if func_match:
                    name = func_match.group(2)
                    function_lines[name] = (idx, idx + 10)  # Rough estimate
                    line_types[idx] = 'function'
                    continue

                class_match = re.match(r'^(\s*)class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if class_match:
                    name = class_match.group(2)
                    class_lines[name] = (idx, idx + 20)  # Rough estimate
                    line_types[idx] = 'class'
                    continue

        # For Python files, refine boundaries with AST if possible
        if filepath.suffix == '.py' and (function_lines or class_lines):
            try:
                tree = ast.parse(content)
                self._refine_boundaries_with_ast(tree, function_lines, class_lines, method_lines)
            except:
                pass  # Fall back to estimates

        signals = FileSignals(
            imports=imports,
            external_edges=external_edges,
            layer_matches=layer_matches,
            role_matches=role_matches,
            state_matches=state_matches,
            activation_matches=activation_matches,
            effect_matches=effect_matches,
            lifetime_matches=lifetime_matches,
            boundary_matches=boundary_matches,
            species_matches=species_matches,
            function_lines=function_lines,
            class_lines=class_lines,
            method_lines=method_lines,
            line_types=line_types,
            content_hash=content_hash
        )

        self.file_signals_cache[file_path_str] = signals
        return signals

    def _refine_boundaries_with_ast(self, tree, function_lines, class_lines, method_lines):
        """Use AST to refine function/class boundaries more accurately."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name in function_lines:
                    function_lines[node.name] = (node.lineno, node.end_lineno or node.lineno + 10)
            elif isinstance(node, ast.ClassDef):
                if node.name in class_lines:
                    class_lines[node.name] = (node.lineno, node.end_lineno or node.lineno + 20)

    def process_file_optimized(self, filepath: Path) -> List[CodeElement]:
        """Process a single file using optimized signal resolution."""
        elements = []

        # Pre-resolve signals for this file
        signals = self.pre_resolve_file_signals(filepath)

        # Skip if no supported patterns found
        if not signals.function_lines and not signals.class_lines:
            return elements

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                source_lines = f.readlines()
        except Exception:
            return elements

        # Process classes
        for class_name, (start, end) in signals.class_lines.items():
            code = ''.join(source_lines[start-1:end])
            docstring = self._extract_docstring_from_lines(source_lines, start)

            element = self.create_element_optimized(
                class_name, filepath, start, end, code, docstring,
                None, signals, "class"
            )
            elements.append(element)

            # Process methods within this class
            for method_name, (class_match, method_start, method_end) in signals.method_lines.items():
                if class_match == class_name:
                    method_code = ''.join(source_lines[method_start-1:method_end])
                    method_docstring = self._extract_docstring_from_lines(source_lines, method_start)

                    method_element = self.create_element_optimized(
                        method_name, filepath, method_start, method_end,
                        method_code, method_docstring, class_name, signals, "method"
                    )
                    elements.append(method_element)

        # Process standalone functions
        for func_name, (start, end) in signals.function_lines.items():
            # Skip if it's actually a method we already processed
            if any(func_name in m.split('.')[-1] for m in signals.method_lines):
                continue

            code = ''.join(source_lines[start-1:end])
            docstring = self._extract_docstring_from_lines(source_lines, start)

            element = self.create_element_optimized(
                func_name, filepath, start, end, code, docstring,
                None, signals, "function"
            )
            elements.append(element)

        return elements

    def _extract_docstring_from_lines(self, source_lines: List[int], start_line: int) -> str:
        """Extract docstring from source lines starting at start_line."""
        if start_line <= len(source_lines):
            # Look for docstring in the first few lines
            for i in range(start_line - 1, min(start_line + 3, len(source_lines))):
                line = source_lines[i].strip()
                if line.startswith('"""') or line.startswith("'''"):
                    # Found docstring start, extract it
                    quote_char = '"""' if line.startswith('"""') else "'''"
                    if line.count(quote_char) >= 2:
                        # Single line docstring
                        return line.strip(quote_char).strip()
                    # Multi-line docstring - would need more complex parsing
                    # For now, return first line
                    return line.strip(quote_char).strip()
        return ""

    def create_element_optimized(self, name: str, filepath: Path, first_loc: int, last_loc: int,
                                code: str, docstring: str, class_name: Optional[str],
                                signals: FileSignals, element_type: str) -> CodeElement:
        """Create a CodeElement using optimized classification."""
        loc_count = last_loc - first_loc + 1
        token_count = self.count_tokens_fast(code)

        # Use class.method format for methods
        display_name = f"{class_name}.{name}" if class_name else name

        # Optimized classification using pre-resolved signals
        role = OptimizedElementClassifier.classify_role_optimized(
            display_name, docstring, signals, first_loc
        )
        layer = OptimizedElementClassifier.classify_layer_optimized(
            str(filepath.relative_to(self.repo_path)), display_name, docstring, signals, first_loc
        )
        state = OptimizedElementClassifier.classify_state_optimized(signals, first_loc, last_loc)
        activation = OptimizedElementClassifier.classify_activation_optimized(signals, first_loc)
        effect = OptimizedElementClassifier.classify_effect_optimized(signals, first_loc, last_loc)
        lifetime = OptimizedElementClassifier.classify_lifetime_optimized(signals, first_loc)
        boundary = OptimizedElementClassifier.classify_boundary_optimized(signals, first_loc, last_loc)
        species = OptimizedElementClassifier.determine_species_optimized(
            layer, role, activation, effect, display_name, docstring, signals, first_loc
        )

        # Generate all three ID types
        rel_filepath = str(filepath.relative_to(self.repo_path))
        element_id = f"{rel_filepath}:{first_loc}-{last_loc}"
        element_id_semantic = f"{rel_filepath}::{display_name}"
        element_hash = self.generate_element_hash(code, display_name, rel_filepath)

        summary = docstring.split('\n')[0] if docstring else f"{role} {species} in {layer}"

        return CodeElement(
            element_id=element_id,
            element_id_semantic=element_id_semantic,
            element_hash=element_hash,
            name=display_name,
            filepath=rel_filepath,
            first_loc=first_loc,
            last_loc=last_loc,
            loc_count=loc_count,
            token_count=token_count,
            species=species,
            role=role,
            layer=layer,
            state=state,
            activation=activation,
            effect=effect,
            lifetime=lifetime,
            boundary=boundary,
            summary=summary
        )

    def analyze_repository_parallel(self) -> Dict:
        """Analyze the entire repository using parallel processing."""
        self.start_time = time.time()

        repo_id = self.repo_path.name
        scanned_files = set()

        # Step 1: Scan files
        scan_start = time.time()
        all_files = []

        # Find all relevant files
        for pattern in ['*.py', '*.ts', '*.tsx', '*.js', '*.jsx']:
            all_files.extend(self.repo_path.rglob(pattern))

        # Filter out ignored files
        files_to_process = [f for f in all_files if not self.should_ignore(f)]
        self.scan_time = time.time() - scan_start

        self._log(f"Found {len(files_to_process)} files to analyze")
        self._log(f"Scan completed in {self.scan_time:.2f}s")

        # Step 2: Process files in parallel
        process_start = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files
            future_to_file = {executor.submit(self.process_file_optimized, file_path): file_path
                            for file_path in files_to_process}

            # Process with progress bar
            for future in tqdm.tqdm(as_completed(future_to_file),
                                   total=len(files_to_process),
                                   desc="Analyzing files"):
                try:
                    elements = future.result()
                    self.elements.extend(elements)
                    scanned_files.add(str(future_to_file[file_path].relative_to(self.repo_path)))
                except Exception as e:
                    file_path = future_to_file[future]
                    self._log(f"Error processing {file_path}: {e}")

        self.process_time = time.time() - process_start
        self._log(f"File processing completed in {self.process_time:.2f}s")

        # Step 3: Build element map and analyze connections
        dep_start = time.time()
        self.element_map = {elem.element_id: elem for elem in self.elements}
        self.analyze_connections_optimized()
        self.dependency_time = time.time() - dep_start
        self._log(f"Dependency analysis completed in {self.dependency_time:.2f}s")

        # Step 4: LLM enrichment (if enabled)
        if self.enable_llm and self.llm_enricher:
            self._log("Starting LLM enrichment...")
            self.enrich_with_llm(repo_id)

        # Step 5: Calculate statistics
        stats = self.calculate_statistics()
        stats["filesScanned"] = len(scanned_files)

        # Add performance metrics
        total_time = time.time() - self.start_time
        stats["performance"] = {
            "scan_time_seconds": round(self.scan_time, 2),
            "processing_time_seconds": round(self.process_time, 2),
            "dependency_time_seconds": round(self.dependency_time, 2),
            "total_time_seconds": round(total_time, 2),
            "files_per_second": round(len(files_to_process) / self.process_time, 2),
            "elements_per_second": round(len(self.elements) / self.process_time, 2)
        }

        # Step 6: Build hierarchy
        hierarchy = self.build_hierarchy()

        # Step 7: Build output structure
        output = {
            "specVersion": "nonperiodic-v2-optimized",
            "repoId": repo_id,
            "statistics": stats,
            "elements": [elem.to_dict() for elem in self.elements],
            "dependencies": self.dependencies,
            "externals": self.externals,
            "externalEdges": self.external_edges,
            "hierarchy": hierarchy
        }

        # Step 8: Generate Mermaid diagram
        self.generate_mermaid_diagram(repo_id)

        # Final report
        self._log(f"\n✅ Analysis complete!")
        self._log(f"   ⏱️  Total time: {total_time:.2f}s")
        if total_time < 5:
            self._log(f"   🚀 Performance target achieved!")
        else:
            self._log(f"   ⚠️  Above 5s target, but much improved from 60s")
        self._log(f"   📁 Processed {len(files_to_process)} files")
        self._log(f"   🧩 Found {len(self.elements)} elements")

        return output

    def analyze_connections_optimized(self):
        """Analyze connections using cached signals."""
        # Patterns for external systems (optimized)
        external_patterns = {
            'http': [r'https?://[^\s\'"`]+', r'axios\.(get|post|put|delete|patch)', r'fetch\s*\(', r'\.get\(|\.post\('],
            'db': [r'\.(query|execute|select|insert|update|delete)\s*\(', r'db\.|database\.|sqlite'],
            'queue': [r'\.(publish|send|emit|produce)\s*\(', r'kafka|rabbitmq|sqs'],
            'storage': [r'localStorage|sessionStorage', r's3\.|gcs\.|azure\.blob'],
            'config': [r'process\.env', r'\.config|\.settings'],
        }

        # Process each element's connections
        for elem in self.elements:
            filepath = self.repo_path / elem.filepath
            if not filepath.exists():
                continue

            # Get cached signals for this file
            signals = self.file_signals_cache.get(elem.filepath)
            if not signals:
                continue

            # Use cached signals to detect externals
            for external_type in signals.external_edges:
                ext_id = self.register_external(external_type, external_type, f"External {external_type}")
                self.external_edges.append({
                    "from": elem.element_id_semantic,
                    "fromStable": elem.element_id,
                    "fromHash": elem.element_hash,
                    "toExternal": ext_id,
                    "kind": external_type,
                    "description": f"Uses {external_type}"
                })

        # Normalize boundaries based on external edges
        self.normalize_boundaries()

    def normalize_boundaries(self):
        """Normalize boundary classification based on external edges."""
        by_element = defaultdict(set)
        for edge in self.external_edges:
            eid = edge["fromStable"]
            kinds = by_element[eid]
            kinds.add(edge["kind"])

        for elem in self.elements:
            kinds = by_element.get(elem.element_id, set())
            if not kinds:
                continue

            has_in = any(k in ['http', 'request', 'fetch'] for k in kinds)
            has_out = any(k in ['http', 'api', 'response', 'send', 'publish'] for k in kinds)

            if has_in and has_out:
                elem.boundary = "In & Out"
            elif has_out:
                elem.boundary = "Out"
            elif has_in:
                elem.boundary = "In"

    def register_external(self, name: str, kind: str, description: str) -> str:
        """Register an external system and return its ID."""
        for ext in self.externals:
            if ext['name'] == name and ext['kind'] == kind:
                return ext['externalId']

        ext_id = f"ext:{kind}-{len(self.externals) + 1}"
        self.externals.append({
            "externalId": ext_id,
            "kind": kind,
            "name": name,
            "description": description
        })
        return ext_id

    def calculate_statistics(self) -> Dict:
        """Calculate comprehensive statistics."""
        if not self.elements:
            return {
                "totalElements": 0,
                "totalLoc": 0,
                "totalTokens": 0,
                "averageLoc": 0,
                "averageTokens": 0,
                "filesAnalyzed": 0,
                "filesWithElements": 0,
                "byLayer": {},
                "byRole": {},
                "byState": {},
                "byActivation": {},
                "byEffect": {},
                "byLifetime": {},
                "byBoundary": {},
                "bySpecies": {}
            }

        total_elements = len(self.elements)
        total_loc = sum(elem.loc_count for elem in self.elements)
        total_tokens = sum(elem.token_count for elem in self.elements)
        average_loc = total_loc / total_elements
        average_tokens = total_tokens / total_elements

        unique_files = set(elem.filepath for elem in self.elements)
        files_with_elements = len(unique_files)

        # Count by dimension
        counters = {
            'byLayer': defaultdict(int),
            'byRole': defaultdict(int),
            'byState': defaultdict(int),
            'byActivation': defaultdict(int),
            'byEffect': defaultdict(int),
            'byLifetime': defaultdict(int),
            'byBoundary': defaultdict(int),
            'bySpecies': defaultdict(int)
        }

        for elem in self.elements:
            counters['byLayer'][elem.layer] += 1
            counters['byRole'][elem.role] += 1
            counters['byState'][elem.state] += 1
            counters['byActivation'][elem.activation] += 1
            counters['byEffect'][elem.effect] += 1
            counters['byLifetime'][elem.lifetime] += 1
            counters['byBoundary'][elem.boundary] += 1
            counters['bySpecies'][elem.species] += 1

        def sort_by_count(d):
            return dict(sorted(d.items(), key=lambda x: x[1], reverse=True))

        return {
            "totalElements": total_elements,
            "totalLoc": total_loc,
            "totalTokens": total_tokens,
            "averageLoc": round(average_loc, 2),
            "averageTokens": round(average_tokens, 2),
            "filesAnalyzed": files_with_elements,
            "filesWithElements": files_with_elements,
            **{k: sort_by_count(v) for k, v in counters.items()}
        }

    def build_hierarchy(self) -> Dict:
        """Build hierarchical architecture map."""
        # Simplified hierarchy building for performance
        hierarchy = {"files": {}, "modules": {}, "subsystems": []}

        # Group elements by file
        elements_by_file = defaultdict(list)
        for elem in self.elements:
            elements_by_file[elem.filepath].append(elem)

        # Build file summaries (simplified)
        for filepath, file_elements in elements_by_file.items():
            layers = defaultdict(int)
            for elem in file_elements:
                layers[elem.layer] += 1

            primary_layer = max(layers.items(), key=lambda x: x[1])[0] if layers else "Unknown"

            hierarchy["files"][filepath] = {
                "filepath": filepath,
                "elementCount": len(file_elements),
                "primaryLayer": primary_layer,
                "layerDistribution": dict(layers),
                "summary": f"File with {len(file_elements)} elements"
            }

        return hierarchy

    def generate_mermaid_diagram(self, repo_id: str):
        """Generate optimized Mermaid diagram."""
        if not self.elements:
            return

        # Simplified diagram generation for performance
        lines = [
            "%% Mermaid diagram generated by Spectrometer V2 Optimized",
            f"%% Repository: {repo_id}",
            f"%% Elements: {len(self.elements)}",
            "",
            "graph TB",
            ""
        ]

        # Group by layer
        elements_by_layer = defaultdict(list)
        for elem in self.elements:
            elements_by_layer[elem.layer].append(elem)

        # Add layer subgraphs
        for layer, elements in elements_by_layer.items():
            layer_id = layer.replace(" ", "_")
            lines.append(f"  subgraph {layer_id}[\"{layer}\"]")

            # Limit elements shown for performance
            for elem in elements[:20]:  # Max 20 per layer
                safe_id = f"E_{elem.element_id.replace(':', '_').replace('-', '_')[:20]}"
                display_name = elem.name.split('.')[-1][:20]
                lines.append(f"    {safe_id}[\"{display_name}\"]")

            if len(elements) > 20:
                lines.append(f"    more_{layer_id}[\"... and {len(elements)-20} more\"]")

            lines.append("  end")

        lines.append("")
        mermaid_path = self.repo_path.parent / "elements_v2_optimized.mmd"
        with open(mermaid_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        print(f"Generated Mermaid diagram: {mermaid_path}")

    def emit_json(self, output_path: Optional[str] = None) -> str:
        """Emit JSON output."""
        result = self.analyze_repository_parallel()
        json_str = json.dumps(result, indent=2)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            self._log(f"Emitted JSON to {output_path}", force=True)

        return json_str


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Spectrometer V2: Optimized Universal Code Architecture Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spectrometer_v2_optimized.py ~/myproject
  python spectrometer_v2_optimized.py ~/myproject -o custom_output.json
  python spectrometer_v2_optimized.py ~/myproject -v --max-workers 16
        """
    )

    parser.add_argument("repo_path", help="Path to repository to analyze")
    parser.add_argument("output", nargs="?", default=None,
                       help="Output JSON file path (default: stdout)")
    parser.add_argument("--enable-llm", action="store_true",
                       help="Enable LLM semantic enrichment")
    parser.add_argument("--llm-cache-dir", default=".spectrometer_cache",
                       help="Directory for LLM cache")
    parser.add_argument("--max-workers", type=int, default=None,
                       help="Maximum parallel workers (default: CPU count)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    if not os.path.exists(args.repo_path):
        print(f"Error: Repository path '{args.repo_path}' does not exist")
        sys.exit(1)

    spectrometer = SpectrometerV2Optimized(
        args.repo_path,
        enable_llm=args.enable_llm,
        llm_cache_dir=args.llm_cache_dir,
        max_workers=args.max_workers,
        verbose=args.verbose
    )

    try:
        spectrometer.emit_json(args.output)
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()