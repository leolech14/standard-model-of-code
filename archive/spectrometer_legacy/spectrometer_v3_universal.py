#!/usr/bin/env python3
"""
Spectrometer V3 - Universal Architecture Analyzer

Features:
- Optimized pre-resolved signals
- Universal language support
- Enhanced React/TypeScript heuristics
- Improved state mutation detection
- Better boundary classification
- Parallel processing
- Smart LLM enrichment with progressive mapping

Target: <5 seconds for large repos
Accuracy: >90% classification precision
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
    from llm_enricher import LLMEnricher
    LLM_ENRICHMENT_AVAILABLE = True
except ImportError:
    LLM_ENRICHMENT_AVAILABLE = False
    LLMEnricher = None


@dataclass
class CodeElement:
    """Universal code element representation."""
    element_id: str  # Stable location-based: filepath:start-end
    element_id_semantic: str  # Human-readable: filepath::elementName
    element_hash: str  # Content-based: sha256 hash
    name: str
    filepath: str
    first_loc: int
    last_loc: int
    loc_count: int
    token_count: int
    language: str = 'Unknown'
    species: str = 'Unknown'
    role: str = 'Unknown'
    layer: str = 'Unknown'
    state: str = 'Unknown'
    activation: str = 'Unknown'
    effect: str = 'Unknown'
    lifetime: str = 'Unknown'
    boundary: str = 'Unknown'
    emojis: Optional[str] = None
    summary: str = ""
    # LLM enrichment fields
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
    # Valence Engine
    valence: Optional[Dict[str, Any]] = None

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
        """Apply LLM annotation to this element."""
        # Always update summary and metadata (even if confidence is low)
        if annotation.summary:
            self.llm_summary = annotation.summary
        self.llm_confidence = annotation.confidence
        if annotation.notes:
            self.llm_notes = annotation.notes

        # Only apply dimension refinements if confidence meets threshold
        if annotation.confidence >= confidence_threshold:
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
    """Pre-resolved signals for ultra-fast classification."""
    imports: List[str]
    external_edges: List[str]
    language: str = 'Unknown'
    framework: str = 'Unknown'
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
    # Enhanced signals
    react_components: List[Tuple[str, int]]  # (name, line)
    react_hooks: List[Tuple[str, int]]  # (hook, line)
    state_mutations: List[Tuple[str, int]]  # (stateVar, line)
    event_listeners: List[Tuple[str, int]]  # (event, line)
    api_calls: List[Tuple[str, str, int]]  # (api, method, line)
    dom_manipulations: List[Tuple[str, int]]  # (domMethod, line)
    framework_patterns: Dict[str, int]  # (pattern, count)


class UniversalElementClassifier:
    """Enhanced classifier with universal language support."""

    # Enhanced patterns for different languages/frameworks
    LANGUAGE_PATTERNS = {
        'Python': {
            'extensions': ['.py'],
            'comments': ['#'],
            'strings': ["'''", '"""', '"', "'"],
            'function_def': r'^\s*def\s+(\w+)\s*\(',
            'class_def': r'^\s*class\s+(\w+)',
            'method_def': r'^\s*def\s+(\w+)\s*\(',
            'import_statement': r'^(from\s+\S+\s+import|import\s+)',
            'self_assignment': r'self\.\w+\s*=',
            'global_statement': r'^\s*global\s+',
            'decorator': r'^\s*@\w+',
        },
        'TypeScript/JavaScript': {
            'extensions': ['.ts', '.tsx', '.js', '.jsx'],
            'comments': ['//', '/*', '*'],
            'strings': ['"', "'", '`'],
            'function_def': r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\)\s*=>|class\s+\w+\s*\{)',
            'class_def': r'(?:export\s+)?class\s+(\w+)',
            'method_def': r'(\w+)\s*\(',
            'import_statement': r'^\s*(?:import\s+.*from|const\s+.*=)',
            'this_assignment': r'this\.\w+\s*=',
            'interface_def': r'^interface\s+(\w+)',
            'type_def': r'^type\s+(\w+)',
        },
        'Java': {
            'extensions': ['.java'],
            'comments': ['//', '/*', '*'],
            'strings': ['"', "'"],
            'function_def': r'(?:public|private|protected|static)?\s+.*\s+(\w+)\s*\([^)]*\)',
            'class_def': r'(?:public|private|protected|static)?\s+class\s+(\w+)',
            'method_def': r'(?:public|private|protected|static)?\s+.*\s+(\w+)\s*\([^)]*\)',
            'import_statement': r'^import\s+',
            'this_assignment': r'this\.\w+\s*=',
        },
        'Go': {
            'extensions': ['.go'],
            'comments': ['//', '/*', '*'],
            'strings': ['"', '`'],
            'function_def': r'func\s+(\w+)\s*\([^)]*)',
            'struct_def': r'type\s+(\w+)\s+struct',
            'method_def': r'func\s+\([^)]*\s+\(\w+)\s*\([^)]*)',
            'import_statement': r'^import\s+',
        },
        'C/C++': {
            'extensions': ['.c', '.cpp', '.cc', '.h', '.hpp'],
            'comments': ['//', '/*', '*'],
            'strings': ['"', "'"],
            'function_def': r'\w+\s+(\w+)\s*\([^)]*)\s*{',
            'struct_def': r'typedef\s+struct\s+(\w+)|struct\s+(\w+)\s*{',
        },
        'Rust': {
            'extensions': ['.rs'],
            'comments': ['//', '/*', '*'],
            'strings': ['"', "'"],
            'function_def': r'fn\s+(\w+)\s*\([^)]*)',
            'struct_def': r'struct\s+(\w+)\s*{',
            'impl_def': r'impl\s+(\w+)\s+for\s+(\w+)',
            'use_statement': r'^use\s+',
        },
    }

    # Framework-specific patterns
    FRAMEWORK_PATTERNS = {
        'React': {
            'indicators': ['React', 'useState', 'useEffect', 'useRef', 'import React', '@gmail/genai'],
            'layer': 'Interface',
            'role_patterns': {
                r'useState|useEffect|useRef|useContext|useReducer': 'Stateful',
                r'createRoot|render.*App|\.jsx?\.': 'Interface',
            },
        },
        'Angular': {
            'indicators': ['@Component', '@Injectable', '@NgModule', '@Input', '@Output'],
            'layer': 'Application',
        },
        'Vue': {
            'indicators': ['ref', 'reactive', 'computed', 'watch', 'emits'],
            'layer': 'Interface',
        },
        'Express': {
            'indicators': ['express\(\)', 'app\.get|app\.post|app\.put|router\.', 'res\.|req\.'],
            'layer': 'Interface',
        },
        'Flask': {
            'indicators': ['Flask\(', '@app\.route|request\.', 'response\.'],
            'layer': 'Interface',
        },
        'Django': {
            'indicators': ['from django', 'models\.Model', 'HttpResponse'],
            'layer': 'Interface',
        },
        'FastAPI': {
            'indicators': ['from fastapi', '@app\.', 'Request', 'Response'],
            'layer': 'Interface',
        },
        'Spring': {
            'indicators': ['@RestController', '@Service', '@Repository', '@Autowired'],
            'layer': 'Application',
        },
    }

    # Enhanced role patterns
    ROLE_PATTERNS = {
        'ORCHESTRATOR': [
            # Orchestrator keywords
            r'(?:orchestrat|coordinat|manag|workflow|saga|process|control|supervis)',
            r'(?:handle|execute|run|direct|perform|operate|init|start)',
            r'(?:class.*(?:Service|Controller|Handler|Manager|Orchestrator|Processor|Director))',
            # Event patterns
            r'(?:dispatch|emit|publish|trigger|fire|invoke)',
        ],
        'WORKER': [
            # Worker keywords
            r'(?:process|execut|calculat|comput|transform|convert|pars|generat|build|creat|download|upload)',
            r'(?:class.*(?:Worker|Processor|Generator|Builder|Factory|Calculator|Parser|Formatter))',
            r'(?:function.*(?:process|execute|run|perform|work|do))',
        ],
        'DATA': [
            # Data keywords
            r'(?:class.*(?:Entity|Model|DTO|VO|ValueObject|Record|Data|Struct))',
            r'(?:interface|type|struct).*\{.*\}',
            r'(?:const|let|var)\s+\w+\s*=\s*\{.*\}',
            # Container patterns
            r'(?:Array|List|Map|Set|Dict|Collection|Queue)',
            r'(?:Repository|Store|Cache)',
        ],
    }

    # Enhanced layer patterns with framework context
    LAYER_PATTERNS = {
        'Interface': [
            # UI/Frontend patterns
            r'(?:render|component|template|jsx|tsx|html|vue\.js|angular\.)',
            r'(?:React\.|Vue\.|Angular\.|document\.|window\.|ReactDOM)',
            r'(?:express\.|fastapi\.|flask\.|router\.|@app\.)',
            r'(?:http|https?://|api|rest|graphql|websocket)',
            r'(?:Request|Response|req|res|ctx|next\()',
            r'(?:EventHandler|Listener|Observer|Publisher|Subscriber)',
        ],
        'Application': [
            # Service/Business logic
            r'(?:Service|UseCase|Interactor|Application|Business|Domain)',
            r'(?:class.*(?:Service|Application|UseCase|Orchestrator|Processor|Manager))',
            r'(?:interface|abstract|protocol).*\{.*\}',
            r'(?:Factory|Builder|Adapter|Mapper|Converter|Transformer)',
            r'(?:validate|verify|check|ensure|assert|require)',
        ],
        'Core Biz': [
            # Domain/Entity patterns
            r'(?:Entity|Model|Domain|Business|Aggregate|Root|ValueObject)',
            r'(?:class.*(?:Entity|Model|Domain|Business))',
            r'(?:interface.*Entity|Model|Domain|Business)',
            r'(?:Repository|Specification|Rule|Policy)',
            r'(?:Invariant|Guard|Assertion)',
        ],
        'Infra': [
            # Infrastructure patterns
            r'(?:Database|DB|SQL|NoSQL|Cache|Queue|Message|Email|Storage|File|Network)',
            r'(?:class.*(?:Repository|Gateway|Client|Adapter|Driver|Connector|Provider))',
            r'(?:import.*(?:sql|pg|mysql|redis|kafka|aws|azure|google))',
            r'(?:sequelize|typeorm|mongoose|prisma|drizzle)',
            r'(?:http|https|ftp|s3|gcs|blob|download|upload)',
        ],
        'Tests': [
            # Test patterns
            r'(?:test|spec|it|describe|beforeEach|afterEach|expect|assert)',
            r'(?:Test|TestCase|Suite|TestFixture|Mock|Stub|Fake)',
            r'(?:jest|mocha|chai|sinon|jasmine|rspec)',
        ],
    }

    # State detection patterns
    STATE_PATTERNS = {
        'Stateful': [
            # React hooks
            r'useState|useRef|useContext|useReducer|useCustom|atom|selector',
            # Instance variables
            r'self\.[a-zA-Z_][a-zA-Z0-9_]*\s*=',
            r'this\.[a-zA-Z_][a-zA-Z0-9_]*\s*=',
            r'(?:class|struct).*\{.*\}',
            # Static/global variables
            r'^\s*(?:static\s+)?(?:const|let|var)\s+\w+\s*=.*[^;]',
            r'^\s*global\s+\w+',
            # Caches
            r'(?:Cache|Store|memory|buffer|pool)',
        ],
        'Stateless': [
            # Pure functions
            r'^(?:const|let|var)\s+\w+\s*=\s*\([^)]*\s*=>',
            r'^\s*function\s+\w+\s*\([^)]*\s*\{',
        ],
    }

    # Activation patterns
    ACTIVATION_PATTERNS = {
        'Event': [
            # Event handlers
            r'(?:on[A-Z]|addEventListener|on\w+|handle\w+|subscribe|listen|observe)',
            r'(?:useEffect|useLayoutEffect|useInsertionEffect)',
            r'(?:EventEmitter|EventBus|PubSub|Observer)',
            r'@.*Event|@.*Listener|@.*Handler',
            r'dispatch|emit|publish|trigger|fire|invoke',
        ],
        'Time': [
            # Scheduled/cron jobs
            r'(?:cron|schedule|timer|interval|timeout|setInterval|setTimeout)',
            r'(?:setTimeout|setInterval|cronJob|scheduledTask)',
            r'@.*Schedule|@.*Timer|@.*Cron',
        ],
        'Direct': [
            # Direct calls
            r'^(?:const|let|var)\s+\w+\s*=\s*\w+',
            r'^\s*function\s+\w+\s*\(',
            r'(?:\.call\(|\.apply\(|\.invoke\()',
        ],
    }

    # Effect patterns
    EFFECT_PATTERNS = {
        'READ': [
            # Read operations
            r'(?:get|fetch|find|load|read|query|select|retrieve|download)',
            r'(?:console\.log|console\.info|print|debug|trace)',
            r'(?:return|output|yield)',
        ],
        'WRITE': [
            # Write/mutation operations
            r'(?:set|write|save|store|put|post|patch|delete|create|insert|update)',
            r'(?:\.push|\.pop|\.shift|\.unshift|\.splice)',
            r'(?:\.assign|\.merge|\.extend|\.clear|\.remove)',
            r'(?:Math\.random|Date\.now|new\s+\w+)',
            r'(?:setState|setLoading|setError|setData)',
            r'(?:dispatch|emit|publish|trigger|fire)',
            r'(?:alert|prompt|confirm)',
            r'(?:document\.createElement|appendChild|removeChild)',
        ],
        'READ & WRITE': [
            # Mixed operations
            r'(?:map|filter|reduce|forEach|transform|process)',
            r'(?:sort|reverse|slice|splice)',
            r'(?:JSON\.(?:parse|stringify))',
            r'(?:localStorage|sessionStorage)',
        ],
    }

    # Lifetime patterns
    LIFETIME_PATTERNS = {
        'Transient': [
            # Request/function-scoped
            r'(?:function\s*\([^)]*\s*\{.*\})',
            r'(?:const|let)\s+\w+\s*=\s*\([^)]*\s*=>',
        ],
        'Session': [
            # Session/user-scoped
            r'(?:session|Session)',
            r'(?:user|User)',
            r'(?:request|Request)',
        ],
        'Global': [
            # Application-level
            r'(?:global|window\.|document\.|process\.env)',
            r'(?:module\.exports|exports\.|__init__|main)',
            r'(?:singleton|static\s+)',
        ],
    }

    # Boundary patterns
    BOUNDARY_PATTERNS = {
        'Internal': [
            # Pure internal operations
            r'(?:calculate|compute|format|parse|validate|transform)',
            r'(?:private|protected|internal)',
            r'(?:this\.[^.]|self\.[^.])',
            r'(?:\.map\(|\.filter\(|\.reduce\()',
            r'(?:Array\.from|Object\.keys|Object\.values)',
        ],
        'In': [
            # Receiving data
            r'(?:req\.|request\.|Request\()',
            r'(?:params|query|body|input|formData)',
            r'(?:event\.|evt\.|Event\()',
            r'(?:args|arguments)',
            r'(?:input|file|upload)',
        ],
        'Out': [
            # Sending data
            r'(?:res\.|response\.|Response\()',
            r'(?:return|return\(|yield)',
            r'(?:dispatch|emit|publish|send|post|put|patch)',
            r'(?:alert|prompt|confirm|log)',
            r'(?:console\.|\.log|\.info|\.error|\.warn)',
            r'(?:window\.open|location\.|history\.)',
            r'(?:document\.write|\.createElement)',
            r'(?:XMLHttpRequest|fetch|axios|http)',
        ],
        'In & Out': [
            # Bidirectional
            r'(?:router|Router|middleware)',
            r'(?:proxy|adapter|gateway|client)',
            r'(?:websocket|ws|socket\.io)',
            r'(?:http\.|https\://)',
        ],
    }

    @staticmethod
    def detect_language(filepath: Path) -> str:
        """Detect programming language from file extension."""
        ext = filepath.suffix.lower()

        for lang, patterns in UniversalElementClassifier.LANGUAGE_PATTERNS.items():
            if ext in patterns['extensions']:
                return lang

        # Default fallback based on common patterns
        if ext in {'.h', '.hpp', '.c', '.cpp', '.cc'}:
            return 'C/C++'
        elif ext in {'.rb', '.rbw'}:
            return 'Ruby'
        elif ext in {'.php', '.php5', '.phtml'}:
            return 'PHP'
        elif ext in {'.scala', '.sc'}:
            return 'Scala'
        elif ext in {'.kt', '.kts'}:
            return 'Kotlin'
        elif ext in {'.rs', '.rslib'}:
            return 'Rust'
        elif ext in {'.dart'}:
            return 'Dart'
        elif ext in {'.go'}:
            return 'Go'
        elif ext in {'.cs', '.csx'}:
            return 'C#'
        elif ext in {'.java', '.class', '.jar'}:
            return 'Java'
        elif ext in {'.swift'}:
            return 'Swift'
        elif ext in {'.m', '.mm', '.h', '.hpp'}:
            return 'Objective-C'
        elif ext in {'.sh', '.bash', '.zsh', '.fish', '.ps1'}:
            return 'Shell'
        elif ext in {'.sql', '.ddl', '.dml'}:
            return 'SQL'
        elif ext in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}:
            return 'Config'
        elif ext in {'.md', '.txt', '.rst', '.adoc'}:
            return 'Documentation'

        return 'Unknown'

    @staticmethod
    def detect_framework(lines: List[str], language: str) -> str:
        """Detect framework from code patterns."""
        text = '\n'.join(lines[:50])  # Check first 50 lines for efficiency

        for framework, config in UniversalElementClassifier.FRAMEWORK_PATTERNS.items():
            for indicator in config['indicators']:
                if any(re.search(pattern, text, re.IGNORECASE) for pattern in config.get('patterns', [])):
                    return framework

        return 'Unknown'

    @staticmethod
    def classify_role_enhanced(name: str, code: str, signals: FileSignals, line_num: int) -> str:
        """Enhanced role classification with better patterns."""
        combined = f"{name} {code}".lower()

        # Check LLM enrichment first if available
        if signals.role_matches:
            # Find closest match
            closest_role = None
            min_distance = float('inf')
            for role, match_line in signals.role_matches:
                distance = abs(match_line - line_num)
                if distance < min_distance:
                    min_distance = distance
                    closest_role = role
            if closest_role and min_distance <= 5:
                return closest_role

        # Use enhanced patterns
        score = {'ORCHESTRATOR': 0, 'WORKER': 0, 'DATA': 0}

        for role, patterns in UniversalElementClassifier.ROLE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    score[role] += 2  # Weight patterns by importance

        # Special framework-based role inference
        if signals.framework in ['React', 'Vue', 'Angular', 'Svelte']:
            score['WORKER'] += 1

        # Choose highest scoring role
        return max(score.items(), key=lambda x: x[1])[0] if any(score.values()) else 'Unknown'

    @staticmethod
    def classify_layer_enhanced(filepath: str, name: str, code: str, signals: FileSignal, line_num: int) -> str:
        """Enhanced layer classification with framework awareness."""
        combined = f"{filepath} {name} {code}".lower()

        # Check LLM enrichment first
        if signals.layer_matches:
            closest_layer = None
            min_distance = float('inf')
            for layer, match_line in signals.layer_matches:
                distance = abs(match_line - line_num)
                if distance < min_distance:
                    min_distance = distance
                    closest_layer = layer
            if closest_layer and min_distance <= 5:
                return closest_layer

        score = {
            'Interface': 0, 'Application': 0, 'Core Biz': 0,
            'Infra': 0, 'Tests': 0
        }

        # Framework-aware classification
        if signals.framework in ['React', 'Vue', 'Angular', 'Svelte', 'Express', 'Flask', 'Django', 'FastAPI']:
            score['Interface'] += 3

        elif signals.framework in ['Spring', 'NestJS', 'Laravel']:
            score['Application'] += 3

        elif signals.framework in ['Django REST', 'FastAPI', 'GraphQL', 'PostgREST']:
            score['Application'] += 2

        # Check enhanced patterns
        for layer, patterns in UniversalElementClassifier.LAYER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    score[layer] += 2

        # Special cases
        if 'test' in combined or 'spec' in combined:
            score['Tests'] += 5

        # "naked noun" default - check if it's a domain concept
        base_name = name.split('.')[-1]
        if base_name and base_name[0].isupper():
            # Check if it has common interface or infra terms
            if not any(keyword in combined for keywords in
                      ['api', 'request', 'response', 'database', 'cache', 'queue', 'config']):
                if not any(keyword in combined for keyword in
                          ['interface', 'service', 'controller', 'handler', 'client', 'provider']):
                    score['Core Biz'] += 1

        return max(score.items(), key=lambda x: x[1])[0] if any(score.values()) else 'Application'

    @staticmethod
    def classify_state_enhanced(code: str, signals: FileSignals, line_num: int, end_line: int) -> str:
        """Enhanced state detection with React hooks awareness."""
        # Check for React hooks or state mutations in element range
        state_mutations_in_range = [
            (s[0], s[1]) for s in signals.state_mutations
            if line_num <= s[1] <= end_line
        ]

        # Check for hooks in element range
        hooks_in_range = [
            (h[0], h[1]) for h in signals.react_hooks
            if line_num <= h[1] <= end_line
        ]

        if state_mutations_in_range or hooks_in_range:
            return 'Stateful'

        # Check for this/self assignments in element range
        for i in range(max(0, line_num - 1), min(len(code.split('\n'), end_line)):
            line = code.split('\n')[i]
            if re.search(r'\bself\.[a-zA-Z_][a-zA-Z0-9_]*\s*=', line) or \
               re.search(r'\bthis\.[a-zA-Z_][a-zA-Z0-9_]*\s*=', line):
                return 'Stateful'

        # Check for persistent patterns
        if any(keyword in code for keyword in
                  ['singleton', 'static.*instance', 'global.', 'persist']):
            return 'Stateful'

        return 'Stateless'

    @staticmethod
    def classify_activation_enhanced(code: str, signals: FileSignals, line_num: int) -> str:
        """Enhanced activation detection."""
        # Check for event listeners in element range
        events_in_range = [
            (e[0], e[1]) for e in signals.event_listeners
            if line_num <= e[1] <= line_num + 10  # Check near the line
        ]

        if events_in_range:
            return 'Event'

        # Check for hooks in element range
        hooks_in_range = [
            (h[0], h[1]) for h in signals.react_hooks
            if line_num <= h[1] <= line_num + 10
        ]

        # useEffect with dependency array suggests event-based
        if 'useEffect' in code and 'dependency array' in code.lower():
            return 'Event'

        # Direct function calls
        return 'Direct'

    @staticmethod
    def classify_effect_enhanced(code: str, signals: FileSignals, line_num: int, end_line: int) -> str:
        """Enhanced effect detection with mutation awareness."""
        # Count different effect types in element range
        write_count = 0
        read_count = 0

        # Check state mutations
        for mutation, mutation_line in signals.state_mutations:
            if line_num <= mutation_line <= end_line:
                write_count += 1

        # Check API calls
        for api, method, api_line in signals.api_calls:
            if line_num <= api_line <= end_line:
                if method in ['post', 'put', 'delete', 'patch', 'upload', 'send']:
                    write_count += 1
                else:
                    read_count += 1

        # Check DOM manipulations
        for dom_method, dom_line in signals.dom_manipulations:
            if line_num <= dom_line <= end_line:
                write_count += 1

        # Check patterns in code
        for pattern, effect_type in UniversalElementClassifier.EFFECT_PATTERNS.items():
            if effect_type == 'READ & WRITE':
                if re.search(pattern, code, re.IGNORECASE):
                    return 'READ & WRITE'
            elif effect_type == 'WRITE':
                write_count += 1
            elif effect_type == 'READ':
                read_count += 1

        # Decide based on counts
        if write_count > 0 and read_count > 0:
            return 'READ & WRITE'
        elif write_count > 0:
            return 'WRITE'
        else:
            return 'READ'

    @staticmethod
    def classify_lifetime_enhanced(code: str, signals: FileSignals, line_num: int) -> str:
        """Enhanced lifetime detection."""
        # Check for persistent/global patterns
        if line_num == 0 or 'main(' in code[:100]:
            return 'Global'

        # Check for singleton or static
        if 'singleton' in code.lower() or 'static.*instance' in code.lower():
            return 'Global'

        # React hooks suggest component lifetime
        if signals.react_hooks:
            return 'Transient'  # Components remount

        # Function patterns suggest transient
        if re.search(r'^\s*(?:const|let|var)\s+\w+\s*=', code):
            return 'Transient'

        return 'Transient'

    @staticmethod
    def classify_boundary_enhanced(code: str, signals: FileSignals, line_num: int, end_line: int) -> str:
        """Enhanced boundary classification with external API detection."""
        # Count boundary types in element range
        inbound_count = 0
        outbound_count = 0

        # Check API calls
        for api, method, api_line in signals.api_calls:
            if line_num <= api_line <= end_line:
                if method in ['get', 'fetch', 'read', 'query']:
                    inbound_count += 1
                else:
                    outbound_count += 1

        # Check event listeners
        for event, event_line in signals.event_listeners:
            if line_num <= event_line <= end_line + 10:
                inbound_count += 1

        # Check DOM manipulations
        for dom_method, dom_line in signals.dom_manipulations:
            if line_num <= dom_line <= end_line:
                outbound_count += 1

        # Check patterns in code
        for pattern, boundary_type in UniversalElement.BOUNDARY_PATTERNS.items():
            if boundary_type == 'In & Out':
                if re.search(pattern, code, re.IGNORECASE):
                    return 'In & Out'
            elif boundary_type == 'In':
                inbound_count += 1
            elif boundary_type == 'Out':
                outbound_count += 1

        # Decide based on counts
        if inbound_count > 0 and outbound_count > 0:
            return 'In & Out'
        elif outbound_count > 0:
            return 'Out'
        elif inbound_count > 0:
            return 'In'
        else:
            return 'Internal'

    @staticmethod
    def determine_species_enhanced(layer: str, role: str, activation: str, effect: str,
                                   name: str, code: str, signals: FileSignals, line_num: int) -> str:
        """Enhanced species determination with framework awareness."""
        # Framework-specific species
        if signals.framework == 'React':
            if 'Component' in name or 'render' in name:
                return 'React Component'
            elif 'Hook' in name:
                return 'React Hook'

        elif signals.framework == 'Express':
            if 'router.' in code or 'app\.' in code:
                return 'Route Handler'
            elif 'middleware' in code:
                return 'Middleware'

        elif signals.framework in ['Flask', 'Django', 'FastAPI']:
            if 'view' in name or 'route' in name:
                return 'View Function'
            elif 'middleware' in code:
                return 'Middleware'

        # Layer-based species
        if layer == 'Interface':
            if role == 'ORCHESTRATOR':
                if 'Handler' in name or 'Controller' in name:
                    return 'Request Handler/Controller'
                return 'UI Orchestrator'
            elif role == 'WORKER':
                if 'render' in name or 'display' in name:
                    return 'UI Renderer'
                return 'UI Worker'
            else:
                return 'UI Component'

        elif layer == 'Application':
            if role == 'ORCHESTRATOR':
                if activation == 'Event':
                    return 'Process/Workflow Manager (Saga)'
                return 'Use Case/Flow Orchestrator'
            elif role == 'DATA':
                return 'Application Data Holder'
            else:
                return 'Application Function'

        elif layer == 'Core Biz':
            if role == 'DATA':
                if 'Entity' in name or 'Model' in name:
                    return 'Domain Entity'
                elif 'Value' in name:
                    return 'Value Object'
                return 'Data Object'
            elif role == 'WORKER':
                if 'Service' in name:
                    return 'Core Business Service'
                elif 'Rule' in name:
                    return 'Business Rule Engine'
                return 'Core Worker'

        elif layer == 'Infra':
            if 'Repository' in name or 'Repo' in name:
                return 'Repository'
            elif 'Gateway' in name or 'Client' in name or 'Adapter' in name:
                return 'Gateway/Adapter'
            elif 'Cache' in name:
                return 'Cache'
            elif 'Queue' in name:
                return 'Message Queue'
            elif 'Job' in name or 'Worker' in name:
                return 'Background Job'
            elif 'Config' in name:
                return 'Configuration'
            return 'Infrastructure Component'

        return 'Unknown'


class ValenceEngine:
    """Enhanced validation engine for architectural consistency."""

    def __init__(self):
        self.rules = [
            # Consistency rules (hard failures)
            {
                'id': 'boundary_internal_has_external',
                'type': 'consistency',
                'severity': 'invalid',
                'check': lambda elem: (
                    elem['boundary'] == 'Internal' and
                    len(elem.get('external_dependencies', [])) == 0
                ),
                'message': 'Boundary marked Internal but has external dependencies'
            },
            {
                'id': 'effect_read_with_writes',
                'type': 'consistency',
                'severity': 'invalid',
                'check': lambda elem: elem['effect'] == 'READ' and not elem.get('has_writes', False),
                'message': 'Effect marked READ but element performs writes'
            },
            {
                'id': 'state_stateless_with_stateful',
                'type': 'consistency',
                'severity': 'invalid',
                'check': lambda elem: (
                    elem['state'] == 'Stateless' and
                    elem.get('has_state_assignments', False) == False
                ),
                'message': 'State marked Stateless but has state assignments'
            },

            # Architecture rules (soft warnings)
            {
                'id': 'core_biz_with_boundary',
                'type': 'architecture',
                'severity': 'warn',
                'score': -4,
                'check': lambda elem: (
                    elem['layer'] == 'Core Biz' and
                    elem['boundary'] != 'Internal'
                ),
                'infra_without_external',
                'message': 'Core Biz layer should not have external boundary'
            },
            {
                'id': 'interface_time_activation',
                'type': 'architecture',
                'severity': 'info',
                'score': -1,
                'check': lambda elem: (
                    elem['layer'] == 'Interface' and
                    elem['activation'] == 'Time'
                ),
                'message': 'Interface with Time activation is unusual (polling/timer UI)'
            },
            {
                'id': 'orchestrator_in_infra',
                'type': 'architecture',
                'severity': 'info',
                'score': -1,
                'check': lambda elem: (
                    elem['role'] == 'ORCHESTRATOR' and
                    elem['layer'] == 'Infra'
                ),
                'message': 'Orchestration in Infra may indicate layer violation'
            },
            {
                'id': 'data_write_only',
                'type': 'architecture',
                'severity': 'warn',
                'score': -2,
                'check': lambda elem: (
                    elem['role'] == 'DATA' and
                    elem['effect'] in ['WRITE', 'READ & WRITE']
                ),
                'message': 'Data holder that only writes may be anemic'
            },

            # Risk patterns (high severity)
            {
                'id': 'stateful_global',
                'type': 'risk',
                'severity': 'warn',
                'score': -3,
                'check': lambda elem: (
                    elem['state'] == 'Stateful' and
                    elem['lifetime'] == 'Global'
                ),
                'message': 'Stateful + Global lifetime is risky (concurrency/testing)'
            },
            {
                'id': 'large_component',
                'type': 'complexity',
                'severity': 'info',
                'score': -1,
                'score': -2,
                'check': lambda elem: elem['loc_count'] > 200,
                'message': 'Large component (>{200 LOC) may benefit from decomposition'
            },

            # Rarity patterns
            {
                'id': 'rare_species',
                'type': 'rarity',
                'severity': 'info',
                'score': -2,
                'check': lambda elem: (
                    elem['species'] in ['Unknown', 'Generic'] or
                    elem['species'] not in [
                        'Component', 'Function', 'Class', 'Service', 'Repository',
                        'Controller', 'Handler', 'Manager', 'Worker', 'Entity', 'Model'
                    ]
                ),
                'message': 'Uncommon species type may need clarification'
            },
        ]

    def validate_element(self, element: Dict) -> Dict[str, Any]:
        """Validate a single element and return valence info."""
        valence = {
            'grade': '✅',
            'score': 0,
            'reasons': []
        }

        failures = []
        warnings = []

        # Add signals for LLM to check
        element['has_writes'] = bool(re.search(r'(?:set[A-Z]|this\.[a-zA-Z_]|\breturn\s*[^{]*)', element.get('content', '')))
        element['has_state_assignments'] = bool(re.search(r'(?:const|let|var)\s+\w+\s*=', element.get('content', '')))

        # Apply all rules
        for rule in self.rules:
            try:
                if not rule['check'](element):
                    if rule['type'] == 'consistency':
                        failures.append(rule['id'])
                        valence['grade'] = '❌'
                        valence['score'] -= 10
                    elif rule['type'] == 'architecture':
                        warnings.append(rule['id'])
                        valence['score'] += rule.get('score', 0)
                    elif rule['type'] == 'risk':
                        warnings.append(rule['id'])
                        valence['score'] += rule.get('score', 0)
                    elif rule['type'] == 'complexity':
                        valence['score'] += rule.get('score', 0)
                    elif rule['type'] == 'rarity':
                        warnings.append(rule['id'])
                        valence['score'] += rule.get('score', 0)
            except Exception as e:
                print(f"Error applying rule {rule['id']}: {e}")

        # Format reasons
        all_issues = failures + warnings
        if all_issues:
            valence['reasons'] = [
                self.rules[r['id']]['message']
                for r in all_issues
                if r['id'] in self.rules
            ]

        return valence

    def get_statistics(self, elements: List[Dict]) -> Dict[str, Any]:
        """Generate valence statistics for a collection of elements."""
        stats = {
            'total_elements': len(elements),
            'elements_by_grade': {'✅': 0, '⚠️': 0, '❌': 0, '☢️': 0},
            'total_score': 0,
            'rule_violations': defaultdict(int),
            'most_common_issues': [],
            'health_score': 0
        }

        total_score = 0
        for element in elements:
            valence = element.get('valence')
            if valence:
                stats['elements_by_grade'][valence['grade']] += 1
                stats['total_score'] += valence.get('score', 0)
                stats['rule_violations'][valence.get('reasons', [])] += 1

        # Calculate health score
        max_possible = len(elements) * 10  # Max -10 per element
        if stats['total_score'] < 0:
            stats['health_score'] = 0
        else:
            stats['health_score'] = 100 - (abs(stats['total_score) / max_possible * 100)

        return stats


class UniversalSpectrometer:
    """Universal architecture analyzer with enhanced classification."""

    def __init__(self, repo_path: str, output_path: str = None,
                 enable_llm: bool = False, llm_cache_dir: Optional[str] = None,
                 max_workers: int = None, verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.output_path = output_path or f"{self.repo_path.name}_elements_v3.json"
        self.enable_llm = enable_llm and LLM_ENRICHMENT_AVAILABLE
        self.max_workers = max_workers or min(32, os.cpu_count() or 8)
        self.verbose = verbose
        self.element_map: Dict[str, CodeElement] = {}

        # Initialize components
        self.valence_engine = ValenceEngine()
        self.classifier = UniversalElementClassifier()

        # Performance tracking
        self.start_time = None
        self.scan_time = 0
        self.process_time = 0
        self.dependency_time = 0

        # Cache for file signals
        self.file_signals_cache: Dict[str, FileSignals] = {}

        # Improved ignore patterns
        self.ignored_patterns = [
            '**/node_modules/**', '**/vendor/**', '**/__pycache__/**',
            '**/.git/**', '**/dist/**', '**/build/**', '**/target/**',
            '**/*.pyc', '**/*.pyo', '**/.venv/**', '**/env/**',
            '**/*.min.js', '**/*.map', '**/*.d\.ts', '**/.*\.lock',
            '**/coverage/**', '**/.pytest_cache/**', '**/.nyc/**',
            '**/site-packages/**', '**/.vscode/**', '**/.idea/**',
        ]

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

    def scan_files(self) -> List[Path]:
        """Scan repository for relevant files."""
        self._log(f"Scanning for files...")

        files = []
        for root, dirs, filenames in os.walk(self.repo_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and
                      d not in ['node_modules', '__pycache__', 'venv', 'env',
                                'target', 'build', 'dist', '.git']]

            for filename in filenames:
                filepath = Path(root) / filename

                # Include all source files for universal analysis
                if not self.should_ignore(filepath):
                    files.append(filepath)

        self._log(f"Found {len(files)} files to analyze")
        return files

    def pre_resolve_signals_optimized(self, filepath: Path) -> FileSignals:
        """Ultra-fast signal resolution with enhanced detection."""
        file_path_str = str(filepath)

        # Check cache first
        if file_path_str in self.file_signals_cache:
            return self.file_signals_cache[file_path_str]

        # Initialize signals
        signals = FileSignals([], [], 'Unknown', 'Unknown', [], [], [], [], [], [], [], [], {}, {}, {}, {})

        # Skip empty files quickly
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            return signals

        if not lines:
            return signals

        content = ''.join(lines)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        signals.content_hash = content_hash

        # Detect language
        signals.language = UniversalElementClassifier.detect_language(filepath)

        # Detect framework
        signals.framework = UniversalElementClassifier.detect_framework(lines, signals.language)

        # Enhanced React/TypeScript patterns
        if signals.framework in ['React', 'Vue', 'Angular', 'Svelte']:
            # Find React components
            component_pattern = r'(?:const|function|class)\s+(\w+).*?(?:extends\s+\w+)?\s*(?:implements|\w+\s*{))'
            for line_num, line in enumerate(lines, 1):
                match = re.search(component_pattern, line)
                if match:
                    signals.react_components.append((match.group(1), line_num))

            # Find React hooks
            hook_patterns = [
                r'(useEffect|useState|useRef|useContext|useReducer|useCustom|useDebugValue|useImperativeHandle)',
                r'useLayoutEffect|useImperativeHandle',
            ]
            for line_num, line in enumerate(lines, 1):
                for pattern in hook_patterns:
                    if pattern in line:
                        signals.react_hooks.append((pattern, line_num))
                        break

            # Find state mutations (setXXX patterns)
            state_pattern = r'(setSelected[A-Z]\w*)'
            for line_num, line in enumerate(lines, 1):
                if re.search(state_pattern, line):
                    signals.state_mutations.append((line.split('=')[0].strip(), line_num))

            # Find event listeners
            event_patterns = [
                r'addEventListener\(|addEventListener\(',
                r'on[A-Z][a-z]*Event',
                r'\.on[A-Z][a-z]*\(.*\)',
            ]
            for line_num, line in enumerate(lines, 1):
                for pattern in event_patterns:
                    if pattern in line:
                        signals.event_listeners.append((line.split('(')[0].strip(), line_num))

            # Find API calls
            api_patterns = [
                (r'(fetch\s*\(|axios\.(?:get|post|put|patch|delete)|http\.|https?://|aws\.|gcp\.)', 'fetch'),
                (r'(\.get|\.post|\.put|\.patch|\.delete)', 'method'),
                (r'(GoogleGenAI|axios|fetch)', 'class'),
            ]
            for line_num, line in enumerate(lines, 1):
                for api, method in api_patterns:
                    if api in line:
                        signals.api_calls.append((api, method, line_num))
                        break

            # Find DOM manipulations
            dom_patterns = [
                (r'(createElement|appendChild|removeChild|createElementNS|getElementById|querySelector)', 'method'),
            ]
            for line_num, line in enumerate(lines, 1):
                for dom_method, pattern in dom_patterns:
                    if pattern in line:
                        signals.dom_manipulations.append((dom_method, line_num))
                        break

        # Universal language parsing for unsupported languages
        if signals.language == 'Unknown':
            # Fallback patterns
            universal_patterns = {
                'function': [
                    r'function\s+(\w+)\s*\(',
                    r'def\s+(\w+)\s*\(',
                    r'(?:const|let|var)\s+(\w+)\s*=\s*(?:function|\([^)]*\s*=>)',
                    r'(?:\w+)\s*:\s*function\s*\(',
                ],
                'class': [
                    r'class\s+(\w+)(?:\s*extends\s+\w+)?\s*{',
                    r'(?:interface|type|struct)\s+(\w+)\s*{',
                ],
                'import': [
                    r'import\s+.*\s+from\s+[\'"'][^\'"]+[\'"]',
                    r'from\s+[\'"'][^\'"]+[\'"]\s+import',
                ],
            }

            # Try to extract from unknown language
            for category, patterns in universal_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if category == 'function':
                        for match in matches:
                            signals.function_lines[match] = (line_num, line_num + 10)
                    elif category == 'class':
                        for match in matches:
                            signals.class_lines[match] = (line_num, line_num + 20)
                    elif category == 'import':
                        signals.imports.extend(matches)

        # Store in cache
        self.file_signals_cache[file_path_str] = signals
        return signals

    def process_file_ultra_fast(self, filepath: Path) -> List[CodeElement]:
        """Ultra-fast file processing with pre-resolved signals."""
        elements = []

        # Pre-resolve all signals in one pass
        signals = self.pre_resolve_signals_optimized(filepath)

        # Skip if no structure found
        if not signals.function_lines and not signals.class_lines:
            return elements

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except:
            return elements

        content = ''.join(lines)

        # Process classes
        for class_name, (start, end) in signals.class_lines.items():
            class_content = content[start-1:end]
            docstring = self._extract_docstring_enhanced(lines, start)

            element = CodeElement(
                element_id=f"{filepath.relative_to(self.repo_path)}:{start}-{end}",
                element_id_semantic=f"{filepath.relative_to(self.repo_path)}::class.{class_name}",
                element_hash=hashlib.sha256(class_content.encode()).hexdigest()[:16],
                name=f"class.{class_name}",
                filepath=str(filepath.relative_to(self.repo_path)),
                first_loc=start,
                last_loc=end,
                loc_count=end - start + 1,
                token_count=len(class_content) // 4,
                language=signals.language,
                framework=signals.framework,
                content=class_content
            )

            # Enhanced classification
            self.classify_element_ultra_fast(element, signals, start)

            elements.append(element)

            # Process methods within this class
            for method_name, (class_match, method_start, method_end) in signals.method_lines.items():
                if class_match == class_name:
                    method_content = content[method_start-1:method_end]
                    method_docstring = self._extract_docstring_enhanced(lines, method_start)

                    method_element = CodeElement(
                        element_id=f"{filepath.relative_to(self.repo_path)}:{method_start}-{method_end}",
                        element_id_semantic=f"{filepath.relative_to(self.repo_path)}::class.{class_name}.{method_name}",
                        element_hash=hashlib.sha256(method_content.encode()).hexdigest()[:16],
                        name=f"{class_name}.{method_name}",
                        filepath=str(filepath.relative_to(self.repo_path)),
                        first_loc=method_start,
                        last_loc=method_end,
                        loc_count=method_end - method_start + 1,
                        token_count=len(method_content) // 4,
                        language=signals.language,
                        framework=signals.framework,
                        content=method_content
                    )

                    self.classify_element_ultra_fast(method_element, signals, method_start)
                    elements.append(method_element)

        # Process standalone functions
        for func_name, (start, end) in signals.function_lines.items():
            # Skip if it's actually a method we already processed
            if any(func_name.split('.')[-1] in m.split('.') for m in signals.method_lines):
                continue

            func_content = content[start-1:end]
            docstring = self._extract_docstring_enhanced(lines, start)

            element = CodeElement(
                element_id=f"{filepath.relative_to(self.repo_path)}:{start}-{end}",
                element_id_semantic=f"{filepath.relative_to(self.repo_path)}::{func_name}",
                element_hash=hashlib.sha256(func_content.encode()).hexdigest()[:16],
                name=func_name,
                filepath=str(filepath.relative_to(self.repo_path)),
                first_loc=start,
                last_loc=end,
                loc_count=end - start + 1,
                token_count=len(func_content) // 4,
                language=signals.language,
                framework=signals.framework,
                content=func_content
            )

            self.classify_element_ultra_fast(element, signals, start)
            elements.append(element)

        return elements

    def _extract_docstring_enhanced(self, lines: List[str], start_line: int) -> str:
        """Enhanced docstring extraction."""
        if start_line <= len(lines):
            # Look for docstring in the first few lines
            for i in range(start_line - 1, min(start_line + 5, len(lines))):
                line = lines[i].strip()
                if line.startswith('"""') or line.startswith("'''"):
                    # Found docstring start
                    quote_char = '"""' if line.startswith('"""') else "'''"
                    if line.count(quote_char) >= 2:
                        # Single line docstring
                        return line.strip(quote_char).strip()
                    # Multi-line docstring
                    return 'Docstring extraction not implemented'
        return ""

    def classify_element_ultra_fast(self, element: CodeElement, signals: FileSignals, line_num: int):
        """Ultra-fast classification using pre-resolved signals."""
        # Use the enhanced classifier
        element.role = UniversalElementClassifier.classify_role_enhanced(
            element.name, element.content, signals, line_num
        )
        element.layer = UniversalElementClassifier.classify_layer_enhanced(
            element.filepath, element.name, element.content, signals, line_num
        )
        element.state = UniversalElementClassifier.classify_state_enhanced(
            element.content, signals, line_num, element.last_loc
        )
        element.activation = UniversalElementClassifier.classify_activation_enhanced(
            element.content, signals, line_num
        )
        element.effect = UniversalElementClassifier.classify_effect_enhanced(
            element.content, signals, line_num, element.last_loc
        )
        element.lifetime = UniversalElementClassifier.classify_lifetime_enhanced(
            element.content, signals, line_num
        )
        element.boundary = UniversalElementClassifier.classify_boundary_enhanced(
            element.content, signals, line_num, element.last_loc
        )
        element.species = UniversalElementClassifier.determine_species_enhanced(
            element.layer, element.role, element.activation, element.effect,
            element.name, element.content, signals, line_num
        )

        # Add language and framework info
        element.language = signals.language
        element.framework = signals.framework

        # Generate summary
        if not element.summary:
            element.summary = f"{element.role} {element.species} in {element.layer}"

        # Apply valence validation
        element.valence = self.valence_engine.validate_element(element.to_dict())

    def analyze_repository_parallel(self) -> Dict[str, Any]:
        """Analyze repository with ultra-fast parallel processing."""
        self.start_time = time.time()

        print(f"\n🔍 Analyzing repository: {self.repo_path}")
        print(f"   Output will be saved to: {self.output_path}")

        # Step 1: Scan files
        scan_start = time.time()
        files = self.scan_files()
        scan_time = time.time() - scan_start
        self._log(f"File scan completed in {scan_time:.2f}s")

        # Step 2: Process files in parallel
        process_start = time.time()
        all_elements = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self.process_file_ultra_fast, file_path)
                for file_path in files
            }

            # Process with progress bar
            for future in tqdm.tqdm(as_completed(future_to_file),
                                   total=len(files),
                                   desc="Analyzing files"):
                try:
                    elements = future.result()
                    all_elements.extend(elements)
                except Exception as e:
                    file_path = future_to_file[future]
                    self._log(f"Error processing {file_path}: {e}")

        process_time = time.time() - process_start
        self._log(f"File processing completed in {process_time:.2f}s")

        # Step 3: Build dependencies
        dep_start = time.time()
        self._build_dependencies_universal(all_elements)
        dep_time = time.time() - dep_start
        self._log(f"Dependency analysis completed in {dep_time:.2f}s")

        # Step 4: Compute statistics
        stats = self.calculate_statistics_enhanced(all_elements)

        # Add valence statistics
        valence_stats = self.valence_engine.get_statistics(all_elements)
        stats.update({'valence': valence_stats})

        # Step 5: LLM enrichment (if enabled)
        if self.enable_llm and self.llm_enricher:
            self._log("Starting LLM enrichment...")
            self.enrich_with_llm_ultra_fast(all_elements)

        # Step 6: Prepare output
        output_data = {
            'specVersion': 'nonperiodic-v3-universal',
            'repoId': self.repo_path.name,
            'metadata': {
                'root_path': str(self.repo_path),
                'spectrometer_version': 'v3_universal',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_runtime_seconds': round(time.time() - self.start_time, 2),
                'scan_time_seconds': round(scan_time, 2),
                'processing_time_seconds': round(process_time, 2),
                'dependency_time_seconds': round(dep_time, 2),
                'file_count': len(files),
                'element_count': len(all_elements),
                'loc_analyzed': stats['total_loc'],
                'tokens_analyzed': stats['total_tokens'],
                'languages_detected': self._get_language_stats(all_elements),
                'frameworks_detected': self._get_framework_stats(all_elements),
            },
            'elements': [elem.to_dict() for elem in all_elements],
            'statistics': stats,
            'dependencies': self.dependencies,
            'externals': self.externals,
            'externalEdges': self.external_edges,
        }

        # Step 7: Save output
        save_start = time.time()
        self._save_output(output_data)
        save_time = time.time() - save_start

        total_time = time.time() - self.start_time

        # Final report
        print(f"\n✅ Analysis complete!")
        print(f"   ⏱️  Total time: {total_time:.2f}s")
        if total_time < 5:
            print(f"   🚀 Performance target achieved!")
        else:
            print(f"   ⚠️ Above 5s target, but much improved")

        print(f"   📁 Processed {len(files)} files")
        print(f"   🧩 Found {len(all_elements)} elements")
        print(f"   📊 Results saved to: {self.output_path}")

        return output_data

    def _get_language_stats(self, elements: List[CodeElement]) -> Dict[str, int]:
        """Count elements by language."""
        lang_stats = defaultdict(int)
        for elem in elements:
            lang_stats[elem.language] += 1
        return dict(lang_stats)

    def _get_framework_stats(self, elements: List[CodeElement]) -> Dict[str, int]:
        """Count elements by framework."""
        framework_stats = defaultdict(int)
        for elem in elements:
            if elem.framework != 'Unknown':
                framework_stats[elem.framework] += 1
        return dict(framework_stats)

    def build_dependencies_universal(self, elements: List[CodeElement]):
        """Build dependency graph with universal analysis."""
        # Create quick lookup
        element_names = {elem.name: elem for elem in elements}

        # Simple dependency detection based on name matching
        for elem in elements:
            # Check for function calls in code
            if elem.content:
                for other_name in element_names:
                    if other_name != elem.name and re.search(r'\b' + re.escape(other_name) + r'\(', elem.content)):
                        elem.dependencies.append(other_name)

                # Check imports/exports
                for imp in elem.imports:
                    elem.dependencies.append(imp)

    def calculate_statistics_enhanced(self, elements: List[CodeElement]) -> Dict[str, Any]:
        """Enhanced statistics calculation."""
        if not elements:
            return {
                'total_elements': 0, 'total_loc': 0, 'total_tokens': 0,
                'average_loc': 0, 'average_tokens': 0,
                'files_analyzed': 0, 'files_with_elements': 0,
                'by_language': {}, 'by_framework': {},
                'by_layer': {}, 'by_role': {}, 'by_state': {},
                'by_activation': {}, 'by_effect': {}, 'by_lifetime': {},
                'by_boundary': {}, 'by_species': {}
            }

        stats = {
            'total_elements': len(elements),
            'total_loc': sum(elem.loc_count for elem in elements),
            'total_tokens': sum(elem.token_count for elem in elements),
            'average_loc': round(sum(elem.loc_count for elem in elements) / len(elements), 2),
            'average_tokens': round(sum(elem.token_count for elem in elements) / len(elements), 2),
            'files_analyzed': len(set(elem.filepath for elem in elements)),
            'files_with_elements': len(set(elem.filepath for elem in elements)),
        }

        # Enhanced dimension counts
        dimension_fields = [
            'by_layer', 'by_role', 'by_state', 'activation',
            'by_effect', 'lifetime', 'boundary', 'species'
        ]
        for field in dimension_fields:
            counter = defaultdict(int)
            for elem in elements:
                value = getattr(elem, field)
                if value != 'Unknown':
                    counter[value] += 1
            stats[field] = dict(sorted(counter.items(), key=lambda x: x[1], reverse=True))

        # Language and framework stats
        stats['by_language'] = self._get_language_stats(elements)
        stats['by_framework'] = self._get_framework_stats(elements)

        return stats

    def enrich_with_llm_ultra_fast(self, elements: List[CodeElement]):
        """Ultra-fast LLM enrichment."""
        if not self.llm_enricher:
            return

        # Enrich only high-priority elements
        priority_elements = [
            elem for elem in elements
            if elem.loc_count > 50 or elem.token_count > 500 or
            elem.layer in ['Core Biz', 'Interface'] or
            elem.role == 'ORCHESTRATOR'
        ][:4]  # Limit to top elements

        self._log(f"Enriching {len(priority_elements)} high-priority elements with LLM...")

        # Batch process
        batch = [e for e in priority_elements if not hasattr(e, 'llm_summary')]
        if batch:
            results = self.llm_enricher.batch_enrich(batch)

            # Apply results
            for element, annotation in zip(batch, results):
                element.apply_llm_annotation(annotation)

        self._log(f"Enriched {len(priority_elements)} elements with LLM annotations")

    def _save_output(self, output_data: Dict):
        """Save analysis results."""
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

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
    """Main entry point for universal spectrometer."""
    parser = argparse.ArgumentParser(
        description="Spectrometer V3: Universal Architecture Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python spectrometer_v3_universal.py ~/myproject
  python spectrometer_v3_universal.py ~/myproject -o custom_output.json
  python spectrometer_v3_universal.py ~/myproject --enable-llm --max-workers 16
        ""
    )

    parser.add_argument("repo_path", help="Path to repository to analyze")
    parser.add_argument("output", nargs="?", default=None,
                       help="Output JSON file path (default: repo_name_elements_v3.json)")
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
        print(f"❌ Error: Path '{args.repo_path}' does not exist.")
        sys.exit(1)

    # Create and run spectrometer
    spectrometer = UniversalSpectrometer(
        args.repo_path,
        output_path=args.output,
        enable_llm=args.enable_llm,
        llm_cache_dir=args.llm_cache_dir,
        max_workers=args.max_workers,
        verbose=args.verbose
    )

    try:
        spectrometer.analyze_repository_parallel()
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()