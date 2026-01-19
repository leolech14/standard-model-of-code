"""
Spectrometer v2 - Preresolve Optimized Version
Fast architectural mapping by pre-resolving signals and batch processing.
"""

import ast
import json
import os
import re
import sys
import time
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional, Any
import argparse
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm

# ==================== CONFIGURATION ====================

# Default external dependencies to track
DEFAULT_EXTERNALS = {
    'db': {'postgres', 'postgresql', 'mysql', 'sqlite', 'pymongo', 'redis', 'elasticsearch'},
    'http': {'requests', 'httpx', 'urllib', 'aiohttp', 'fastapi', 'flask', 'django', 'tornado'},
    'queue': {'pika', 'kombu', 'kafka', 'celery', 'rq', 'beanstalk'},
    'storage': {'boto3', 'google.cloud', 'azure.storage', 'minio'},
    'config': {'pydantic_settings', 'python-dotenv', 'dynaconf', 'configparser'}
}

# Enhanced rule set with more heuristics
RULE_SET = {
    # Layer rules (order matters for specificity)
    'layer': [
        # Interface / UI Edge
        (r'@app\.|@router\.|@bp\.|Blueprint|@api\.|@\{.*\}|app\.get|app\.post|router\.get|router\.post', 'Interface'),
        (r'class.*View|class.*Controller|class.*Handler|request\.|Response|JsonResponse', 'Interface'),
        (r'Flask|FastAPI|Django|tornado|aiohttp', 'Interface'),
        (r'HttpResponse|render|redirect|get_object|filter\.all\(\)', 'Interface'),

        # Infrastructure
        (r'db\.|session\.|cursor\.|connection\.|execute\(|fetchall\(\)|commit\(\)', 'Infra'),
        (r'SQLAlchemy|django\.db|psycopg2|pymongo|redis|elasticsearch', 'Infra'),
        (r'boto3|google\.cloud|azure\.storage|minio', 'Infra'),
        (r'pika|kombu|kafka|celery|r', 'Infra'),

        # Core Business
        (r'class.*(Entity|Model|Domain|Service|Repository|Specification)', 'Core Biz'),
        (r'domain|entities?|models?|repository|specification|value.?object', 'Core Biz'),
        (r'business|rules?|validation|policies?', 'Core Biz'),

        # Tests
        (r'test_|def test_|assert_|mock_|fixture|setUp|tearDown', 'Tests'),
        (r'pytest|unittest|TestCase|@pytest\.|unittest\.mock', 'Tests'),
    ],

    # Role rules
    'role': [
        # Orchestrator
        (r'def.*(process|handle|execute|run|orchestrat|coordinat|manag|workflow|saga)', 'Orchestrator'),
        (r'class.*(Service|Application|UseCase|Interactor|Handler|Processor|Manager)', 'Orchestrator'),
        (r'facade|mediator|coordinator|orchestrator', 'Orchestrator'),

        # Worker
        (r'def.*(calculate|compute|transform|convert|format|parse|generate)', 'Worker'),
        (r'class.*(Worker|Calculator|Parser|Formatter|Transformer|Generator|Util)', 'Worker'),
        (r'helper|util|tool|algorithm|strategy', 'Worker'),

        # Data holder
        (r'class.*(Entity|Model|DTO|VO|ValueObject|Data|Record)', 'Data'),
        (r'dataclass|typeddict|namedtuple|attr\.|pydantic\.BaseModel', 'Data'),
    ],

    # State patterns
    'state': [
        (r'self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=|@property|@[a-zA-Z_][a-zA-Z0-9_]*\.setter', 'Stateful'),
        (r'global\s+[a-zA-Z_][a-zA-Z0-9_]*|^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*\{.*\}', 'Stateful'),
        (r'class.*:\s*$.*?self\.', 'Stateful'),  # Class with self assignments
    ],

    # Activation patterns
    'activation': [
        (r'def .*__call__|__invoke__|__execute__|@.*schedule|cron|periodic', 'Time'),
        (r'def .*on_|@.*event|listener|subscriber|observer|publish|emit', 'Event'),
        (r'def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):', 'Direct'),  # Regular method
    ],

    # I/O Effect patterns
    'effect': [
        (r'insert|update|delete|create|write|save|set|append|extend|send|publish', 'WRITE'),
        (r'execute|commit|transaction|mutate|modify', 'WRITE'),
        (r'select|find|get|fetch|query|search|load|read|open|read\(\)', 'READ'),
    ],

    # Lifetime patterns
    'lifetime': [
        (r'__init__.*self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=[^N]|@singleton|@.*\.\s*instance\(\)', 'Global'),
        (r'session|request\.|@.*scope|context|lifetime', 'Session'),
        (r'def [a-zA-Z_][a-zA-Z0-9_]*\([^)]*\):', 'Transient'),
    ],

    # Boundary patterns
    'boundary': [
        (r'request\.|headers|cookies|query|body|form|files|@.*route|@.*app\.route', 'In'),
        (r'Response|return|jsonify|render|redirect|HttpResponse|JsonResponse', 'Out'),
        (r'api|request|fetch|post|get|put|delete|patch|http|rest', 'In & Out'),
    ],
}

# Species mapping rules
SPECIES_RULES = [
    # Controllers
    (r'class.*Controller|class.*Handler|@.*route|app\.(get|post|put|delete)', 'Controller'),

    # Services
    (r'class.*Service|class.*ApplicationService|class.*UseCase', 'Application Service'),

    # Domain objects
    (r'class.*Entity|class.*Aggregate|class.*Model', 'Domain Entity'),
    (r'class.*VO|class.*ValueObject|class.*DTO', 'Value Object'),

    # Infrastructure
    (r'class.*Repository|class.*Gateway|class.*Adapter', 'Repository/Gateway'),
    (r'.*(Database|DB|Storage|Cache).*', 'Infrastructure'),

    # Tests
    (r'class.*Test|def test_|TestCase', 'Test'),
]

# Language-agnostic patterns for fallback detection
FALLBACK_PATTERNS = {
    'function': [
        r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*function\s*\(',
        r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{',
        r'export\s+(default\s+)?function\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'export\s+(const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\(',
    ],
    'class': [
        r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{',  # JS constructor
        r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*class\s+',
        r'type\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*struct\s*',
    ],
    'import': [
        r'import\s+.*\s+from\s+[\'"][^\'"]+[\'"]',
        r'from\s+[\'"][^\'"]+[\'"]\s+import',
        r'require\s*\([\'"][^\'"]+[\'"]\)',
        r'#include\s*[<"][^>"]+[">]',
        r'using\s+[a-zA-Z_][a-zA-Z0-9_]*;',
        r'import\s+\{.*\}\s*from\s+[\'"][^\'"]+[\'"]',
    ],
}

# ==================== DATA STRUCTURES ====================

@dataclass
class CodeElement:
    """Represents a code element (function, class, method) with metadata."""
    name: str
    element_type: str  # 'function', 'class', 'method'
    file_path: str
    start_line: int
    end_line: int
    loc: int
    layer: str = 'Unknown'
    role: str = 'Unknown'
    state: str = 'Unknown'
    activation: str = 'Unknown'
    effect: str = 'Unknown'
    lifetime: str = 'Unknown'
    boundary: str = 'Unknown'
    species: str = 'Unknown'
    imports: List[str] = None
    dependencies: List[str] = None
    external_dependencies: List[str] = None
    content: str = None
    content_hash: str = ''
    tokens: int = 0

    def __post_init__(self):
        if self.imports is None:
            self.imports = []
        if self.dependencies is None:
            self.dependencies = []
        if self.external_dependencies is None:
            self.external_dependencies = []

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

# ==================== CORE ENGINE ====================

class SpectrometerV2:
    """Optimized version of Spectrometer with pre-resolution and parallel processing."""

    def __init__(self,
                 root_path: str,
                 output_path: str = None,
                 externals: Dict[str, Set[str]] = None,
                 file_pattern: str = None,
                 verbose: bool = False):
        self.root_path = Path(root_path)
        self.output_path = output_path or f"{self.root_path.name}_elements.json"
        self.externals = externals or DEFAULT_EXTERNALS
        self.file_pattern = file_pattern or r'\.(py|js|ts|jsx|tsx)$'
        self.verbose = verbose

        # Initialize counters
        self.file_count = 0
        self.element_count = 0
        self.token_count = 0
        self.import_count = 0
        self.external_count = 0

        # Cache for file signals
        self.file_signals_cache: Dict[str, FileSignals] = {}

    def _log(self, message: str, force: bool = False):
        """Log only if verbose or forced."""
        if self.verbose or force:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return any(test_marker in file_path.parts for test_marker in ['test', 'tests', 'spec'])

    def _scan_files(self) -> List[Path]:
        """Scan repository for relevant files using parallel processing."""
        self._log(f"Scanning for files matching: {self.file_pattern}")

        files = []
        pattern = re.compile(self.file_pattern)

        for root, dirs, filenames in os.walk(self.root_path):
            # Skip hidden directories and common build/cache dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and
                      d not in ['node_modules', '__pycache__', 'venv', 'env',
                                'target', 'build', 'dist', '.git']]

            for filename in filenames:
                if pattern.search(filename):
                    file_path = Path(root) / filename
                    # Additional filtering
                    if self._should_include_file(file_path):
                        files.append(file_path)

        self._log(f"Found {len(files)} files to analyze")
        return files

    def _should_include_file(self, file_path: Path) -> bool:
        """Filter files: exclude test files and migrations unless explicitly asked."""
        # Include tests in main analysis (they're architectural too)
        return True

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def _count_tokens_fast(self, file_path: Path, lines: List[str]) -> Tuple[int, int]:
        """Fast token counting without actually parsing."""
        # Simple heuristic: average Python token is ~4 characters
        # This is MUCH faster than actual tokenization
        char_count = sum(len(line) for line in lines)
        estimated_tokens = char_count // 4
        loc = len(lines)
        return loc, estimated_tokens

    def _pre_resolve_file_signals(self, file_path: Path) -> FileSignals:
        """Pre-resolve all signals in a file in a single pass."""
        if file_path.suffix not in {'.py', '.js', '.ts', '.jsx', '.tsx'}:
            return FileSignals([], [], [], [], [], [], [], [], [], [], {}, {}, {}, {})

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            self._log(f"Could not read {file_path}: {e}")
            return FileSignals([], [], [], [], [], [], [], [], [], [], {}, {}, {}, {})

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

        content = ''.join(lines)

        # Detect imports
        for category, keywords in self.externals.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    external_edges.append(f"{category}:{keyword}")

        # Detect actual imports
        if file_path.suffix == '.py':
            imports.extend(self._extract_python_imports(content))
        else:
            for pattern in FALLBACK_PATTERNS['import']:
                imports.extend(re.findall(pattern, content))

        # Pre-resolve all patterns in a single pass
        for idx, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check each category of patterns
            for pattern, value in RULE_SET['layer']:
                if re.search(pattern, line, re.IGNORECASE):
                    layer_matches.append((value, idx))

            for pattern, value in RULE_SET['role']:
                if re.search(pattern, line, re.IGNORECASE):
                    role_matches.append((value, idx))

            # State patterns (multiline aware)
            for pattern, value in RULE_SET['state']:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's not just a comment
                    if not line_stripped.startswith('#'):
                        state_matches.append((value, idx))

            for pattern, value in RULE_SET['activation']:
                if re.search(pattern, line, re.IGNORECASE):
                    activation_matches.append((value, idx))

            for pattern, value in RULE_SET['effect']:
                if re.search(pattern, line, re.IGNORECASE):
                    effect_matches.append((value, idx))

            for pattern, value in RULE_SET['lifetime']:
                if re.search(pattern, line, re.IGNORECASE):
                    lifetime_matches.append((value, idx))

            for pattern, value in RULE_SET['boundary']:
                if re.search(pattern, line, re.IGNORECASE):
                    boundary_matches.append((value, idx))

            for pattern, value in SPECIES_RULES:
                if re.search(pattern, line, re.IGNORECASE):
                    species_matches.append((value, idx))

            # Detect function and class definitions
            if file_path.suffix == '.py':
                # Python functions
                func_match = re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
                if func_match:
                    indent = len(func_match.group(1))
                    name = func_match.group(2)
                    function_lines[name] = (idx, idx + 10)  # Rough estimate
                    line_types[idx] = 'function'
                    continue

                # Python classes
                class_match = re.match(r'^(\s*)class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if class_match:
                    indent = len(class_match.group(1))
                    name = class_match.group(2)
                    class_lines[name] = (idx, idx + 20)  # Rough estimate
                    line_types[idx] = 'class'
                    continue
            else:
                # JavaScript/TypeScript functions
                for pattern in FALLBACK_PATTERNS['function']:
                    match = re.search(pattern, line)
                    if match:
                        name = match.groups()[-1]
                        function_lines[name] = (idx, idx + 10)
                        line_types[idx] = 'function'
                        break

                # JavaScript/TypeScript classes
                for pattern in FALLBACK_PATTERNS['class']:
                    match = re.search(pattern, line)
                    if match:
                        name = match.groups()[-1]
                        class_lines[name] = (idx, idx + 20)
                        line_types[idx] = 'class'
                        break

        # Refine boundaries for classes and functions
        if file_path.suffix == '.py' and (function_lines or class_lines):
            try:
                tree = ast.parse(content)
                self._refine_boundaries_with_ast(tree, function_lines, class_lines, method_lines)
            except:
                pass  # Fall back to estimates

        return FileSignals(
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
            line_types=line_types
        )

    def _refine_boundaries_with_ast(self, tree, function_lines, class_lines, method_lines):
        """Use AST to refine function/class boundaries more accurately."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name in function_lines:
                    function_lines[node.name] = (node.lineno, node.end_lineno or node.lineno + 10)

                # Check if it's a method
                if hasattr(node, 'parent'):  # Would need ASTVisitor to set parent
                    method_name = f"{getattr(node.parent, 'name', 'Unknown')}.{node.name}"
                    method_lines[method_name] = (getattr(node.parent, 'name', 'Unknown'),
                                                 node.lineno, node.end_lineno or node.lineno + 5)

            elif isinstance(node, ast.ClassDef):
                if node.name in class_lines:
                    class_lines[node.name] = (node.lineno, node.end_lineno or node.lineno + 20)

    def _process_file_optimized(self, file_path: Path) -> List[CodeElement]:
        """Process a single file using pre-resolved signals."""
        elements = []

        # Get file extension once
        ext = file_path.suffix

        # Skip unsupported files
        if ext not in {'.py', '.js', '.ts', '.jsx', '.tsx'}:
            return elements

        # Pre-resolve signals for this file
        signals = self._pre_resolve_file_signals(file_path)
        self.file_signals_cache[str(file_path)] = signals

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            self._log(f"Could not read {file_path}: {e}")
            return elements

        loc, tokens = self._count_tokens_fast(file_path, lines)
        content = ''.join(lines)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        # Process classes
        for class_name, (start, end) in signals.class_lines.items():
            class_content = content[start-1:end]
            element = CodeElement(
                name=class_name,
                element_type='class',
                file_path=str(file_path.relative_to(self.root_path)),
                start_line=start,
                end_line=end,
                loc=end - start + 1,
                content=class_content,
                content_hash=content_hash,
                tokens=tokens // max(1, len(signals.class_lines) + len(signals.function_lines))
            )

            # Classify using pre-resolved signals
            self._classify_element_optimized(element, signals, start)

            # Add imports and externals
            element.imports = list(set(signals.imports))
            element.external_dependencies = list(set(signals.external_edges))

            elements.append(element)

            # Process methods within this class
            for method_name, (class_name_match, method_start, method_end) in signals.method_lines.items():
                if class_name_match == class_name:
                    method_content = content[method_start-1:method_end]
                    method_element = CodeElement(
                        name=f"{class_name}.{method_name}",
                        element_type='method',
                        file_path=str(file_path.relative_to(self.root_path)),
                        start_line=method_start,
                        end_line=method_end,
                        loc=method_end - method_start + 1,
                        content=method_content,
                        content_hash=content_hash,
                        tokens=tokens // max(1, len(signals.function_lines) + len(signals.class_lines) + len(signals.method_lines))
                    )

                    self._classify_element_optimized(method_element, signals, method_start)
                    method_element.imports = list(set(signals.imports))
                    method_element.external_dependencies = list(set(signals.external_edges))

                    elements.append(method_element)

        # Process standalone functions
        for func_name, (start, end) in signals.function_lines.items():
            # Skip if it's actually a method we already processed
            if any(func_name in m for m in signals.method_lines):
                continue

            func_content = content[start-1:end]
            element = CodeElement(
                name=func_name,
                element_type='function',
                file_path=str(file_path.relative_to(self.root_path)),
                start_line=start,
                end_line=end,
                loc=end - start + 1,
                content=func_content,
                content_hash=content_hash,
                tokens=tokens // max(1, len(signals.function_lines) + len(signals.class_lines))
            )

            self._classify_element_optimized(element, signals, start)
            element.imports = list(set(signals.imports))
            element.external_dependencies = list(set(signals.external_edges))

            elements.append(element)

        return elements

    def _classify_element_optimized(self, element: CodeElement, signals: FileSignals, line_number: int):
        """Classify an element using pre-resolved signals (O(1) instead of O(n))."""

        # Helper to find the closest match to the line number
        def find_closest_match(matches: List[Tuple[str, int]]) -> Optional[str]:
            if not matches:
                return None
            # Find the match closest to our line number
            closest = min(matches, key=lambda x: abs(x[1] - line_number))
            return closest[0]

        # Classify each dimension using pre-resolved signals
        element.layer = find_closest_match(signals.layer_matches) or 'Unknown'
        element.role = find_closest_match(signals.role_matches) or 'Unknown'

        # For state, check if there are any stateful signals before the end of the element
        state_signals_nearby = [s for s in signals.state_matches if s[1] <= element.end_line]
        element.state = 'Stateful' if state_signals_nearby else 'Stateless'

        element.activation = find_closest_match(signals.activation_matches) or 'Direct'

        # For effect, prioritize writes over reads
        write_signals = [e for e in signals.effect_matches if e[0] == 'WRITE' and e[1] <= element.end_line]
        read_signals = [e for e in signals.effect_matches if e[0] == 'READ' and e[1] <= element.end_line]

        if write_signals and read_signals:
            element.effect = 'READ & WRITE'
        elif write_signals:
            element.effect = 'WRITE'
        elif read_signals:
            element.effect = 'READ'
        else:
            element.effect = 'READ'  # Default assumption

        element.lifetime = find_closest_match(signals.lifetime_matches) or 'Transient'
        element.boundary = find_closest_match(signals.boundary_matches) or 'Internal'
        element.species = find_closest_match(signals.species_matches) or 'Class'

        # Adjust based on element type
        if element.element_type == 'class':
            if element.species == 'Class':
                element.species = 'Entity'

        elif element.element_type == 'function':
            if element.species == 'Entity':
                element.species = 'Function'

        elif element.element_type == 'method':
            if element.species == 'Function':
                element.species = 'Method'

        # Special handling for test files
        if 'test' in element.file_path.lower():
            element.layer = 'Tests'
            if element.species == 'Entity':
                element.species = 'Test'

    def _extract_python_imports(self, content: str) -> List[str]:
        """Fast extraction of imports from Python code."""
        imports = []

        # Simple regex patterns (faster than AST for this use case)
        patterns = [
            r'^from\s+([^\s]+)\s+import',
            r'^import\s+([^\s]+)',
        ]

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('import', 'from')):
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.append(match.group(1))
                        break

        return imports

    def analyze(self) -> Dict[str, Any]:
        """Main analysis method with parallel processing."""
        start_time = time.time()

        print(f"\n🔍 Analyzing repository: {self.root_path}")
        print(f"   Output will be saved to: {self.output_path}")

        # Step 1: Scan files
        scan_start = time.time()
        files = self._scan_files()
        scan_time = time.time() - scan_start
        print(f"   File scan completed in {scan_time:.2f}s")

        # Step 2: Process files in parallel
        process_start = time.time()
        all_elements = []

        # Use ThreadPoolExecutor for I/O-bound operations
        with ThreadPoolExecutor(max_workers=min(32, os.cpu_count() or 8)) as executor:
            # Submit all files
            future_to_file = {executor.submit(self._process_file_optimized, file_path): file_path
                            for file_path in files}

            # Process as they complete with progress bar
            for future in tqdm.tqdm(as_completed(future_to_file), total=len(files), desc="Analyzing files"):
                try:
                    elements = future.result()
                    all_elements.extend(elements)
                except Exception as e:
                    file_path = future_to_file[future]
                    self._log(f"Error processing {file_path}: {e}")

        process_time = time.time() - process_start
        print(f"   File processing completed in {process_time:.2f}s")

        # Step 3: Build dependencies
        dep_start = time.time()
        self._build_dependencies_fast(all_elements)
        dep_time = time.time() - dep_start
        print(f"   Dependency analysis completed in {dep_time:.2f}s")

        # Step 4: Compute statistics
        stats = self._compute_statistics(all_elements)

        # Step 5: Prepare output
        output_data = {
            'metadata': {
                'root_path': str(self.root_path),
                'spectrometer_version': 'v2_preresolve',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_runtime_seconds': round(time.time() - start_time, 2),
                'file_count': len(files),
                'element_count': len(all_elements),
                'loc_analyzed': stats['total_loc'],
                'tokens_analyzed': stats['total_tokens']
            },
            'elements': [asdict(element) for element in all_elements],
            'statistics': stats,
            'performance': {
                'scan_time_seconds': round(scan_time, 2),
                'processing_time_seconds': round(process_time, 2),
                'dependency_time_seconds': round(dep_time, 2),
                'files_processed_per_second': round(len(files) / process_time, 2),
                'elements_processed_per_second': round(len(all_elements) / process_time, 2)
            }
        }

        # Step 6: Save output
        save_start = time.time()
        self._save_output(output_data)
        save_time = time.time() - save_start

        total_time = time.time() - start_time

        # Final report
        print(f"\n✅ Analysis complete!")
        print(f"   ⏱️  Total time: {total_time:.2f}s (target: <5s)")
        if total_time > 5:
            print(f"   ⚠️  Still above target. Further optimizations needed.")
        else:
            print(f"   🚀 Performance target achieved!")

        print(f"   📁 Processed {len(files)} files")
        print(f"   🧩 Found {len(all_elements)} elements")
        print(f"   📊 Results saved to: {self.output_path}")

        return output_data

    def _build_dependencies_fast(self, elements: List[CodeElement]):
        """Build dependency graph using the file signals cache."""
        # Create a quick lookup of element names to their dependencies
        element_names = {elem.name: elem for elem in elements}

        # Build import mapping from file signals
        all_imports = {}
        for elem in elements:
            file_path = elem.file_path
            if file_path in self.file_signals_cache:
                signals = self.file_signals_cache[file_path]
                all_imports[elem.name] = signals.imports

        # Simple dependency detection based on name matching
        for elem in elements:
            # Check if element calls other elements
            if elem.content:
                # Simple heuristic: look for other element names in the content
                for other_name in element_names:
                    if other_name != elem.name and re.search(r'\b' + re.escape(other_name) + r'\(', elem.content):
                        elem.dependencies.append(other_name)

            # Add import-based dependencies
            if elem.name in all_imports:
                for imp in all_imports[elem.name]:
                    elem.dependencies.append(imp)

    def _compute_statistics(self, elements: List[CodeElement]) -> Dict[str, Any]:
        """Compute summary statistics."""
        stats = {
            'elements_by_type': Counter(),
            'elements_by_layer': Counter(),
            'elements_by_role': Counter(),
            'elements_by_species': Counter(),
            'external_dependencies': Counter(),
            'total_loc': 0,
            'total_tokens': 0,
            'total_files': 0
        }

        files_seen = set()

        for element in elements:
            stats['elements_by_type'][element.element_type] += 1
            stats['elements_by_layer'][element.layer] += 1
            stats['elements_by_role'][element.role] += 1
            stats['elements_by_species'][element.species] += 1

            for ext_dep in element.external_dependencies:
                stats['external_dependencies'][ext_dep.split(':')[0]] += 1

            stats['total_loc'] += element.loc
            stats['total_tokens'] += element.tokens
            files_seen.add(element.file_path)

        stats['total_files'] = len(files_seen)

        return stats

    def _save_output(self, output_data: Dict[str, Any]):
        """Save analysis results to JSON file."""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

# ==================== MAIN EXECUTION ====================

def main():
    parser = argparse.ArgumentParser(
        description='Spectrometer v2 - Fast Architectural Mapping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spectrometer_v2_preresolve.py ~/myproject
  python spectrometer_v2_preresolve.py ~/myproject -o custom_output.json
  python spectrometer_v2_preresolve.py ~/myproject -v
        """
    )

    parser.add_argument('root_path', help='Root directory of the codebase to analyze')
    parser.add_argument('-o', '--output', help='Output JSON file (default: <repo>_elements.json)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.root_path):
        print(f"❌ Error: Path '{args.root_path}' does not exist.")
        sys.exit(1)

    # Run analysis
    spectrometer = SpectrometerV2(
        root_path=args.root_path,
        output_path=args.output,
        verbose=args.verbose
    )

    try:
        spectrometer.analyze()
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()