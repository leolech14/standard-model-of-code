#!/usr/bin/env python3
"""
Spectrometer v4 - Hadron Classification Engine
Implementation dos 96 hádrons do Standard Model do Código
"""

import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================
# ENUMERAÇÕES FUNDAMENTAIS
# ======================

class Continent(Enum):
    """Os 12 continentes (partículas fundamentais)"""
    DATA_FOUNDATIONS = "#00FFFF"  # Ciano
    LOGIC_FLOW = "#FF4444"        # Vermelho
    ORGANIZATION = "#44FF44"      # Verde
    EXECUTION = "#FF6600"         # Âmbar

class Fundamental(Enum):
    """As 12 partículas fundamentais"""
    BITS = "Bits"
    BYTES = "Bytes"
    PRIMITIVES = "Primitives"
    VARIABLES = "Variables"
    EXPRESSIONS = "Expressions"
    STATEMENTS = "Statements"
    CONTROL_STRUCTURES = "Control Structures"
    FUNCTIONS = "Functions"
    AGGREGATES = "Aggregates"
    MODULES = "Modules"
    FILES = "Files"
    EXECUTABLES = "Executables"

# ======================
# CATÁLOGO COMPLETO DOS 96 HÁDRONS
# ======================

HADRON_CATALOG = {
    # Data Foundations (Ciano)
    "BitFlag": {"id": 1, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BITS, "form": "tetrahedron+glow"},
    "BitMask": {"id": 2, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BITS, "form": "tetrahedron+mask"},
    "ParityBit": {"id": 3, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BITS, "form": "tetrahedron+pulse"},
    "SignBit": {"id": 4, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BITS, "form": "tetrahedron+negative"},

    "ByteArray": {"id": 5, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BYTES, "form": "cube+grid"},
    "MagicBytes": {"id": 6, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BYTES, "form": "cube+emissive"},
    "PaddingBytes": {"id": 7, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.BYTES, "form": "cube+transparent"},

    "Boolean": {"id": 8, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.PRIMITIVES, "form": "icosahedron+binary"},
    "Integer": {"id": 9, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.PRIMITIVES, "form": "icosahedron+metallic"},
    "Float": {"id": 10, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.PRIMITIVES, "form": "icosahedron+soft"},
    "StringLiteral": {"id": 11, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.PRIMITIVES, "form": "icosahedron+text"},
    "EnumValue": {"id": 12, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.PRIMITIVES, "form": "icosahedron+ring"},

    "LocalVar": {"id": 13, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.VARIABLES, "form": "cylinder+short"},
    "Parameter": {"id": 14, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.VARIABLES, "form": "cylinder+arrow"},
    "InstanceField": {"id": 15, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.VARIABLES, "form": "cylinder+medium"},
    "StaticField": {"id": 16, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.VARIABLES, "form": "cylinder+tall"},
    "GlobalVar": {"id": 17, "continent": Continent.DATA_FOUNDATIONS, "fundamental": Fundamental.VARIABLES, "form": "cylinder+glowing"},

    # Logic & Flow (Vermelho / Magenta)
    "ArithmeticExpr": {"id": 18, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.EXPRESSIONS, "form": "cone+orange"},
    "CallExpr": {"id": 19, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.EXPRESSIONS, "form": "cone+arrow"},
    "LiteralExpr": {"id": 20, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.EXPRESSIONS, "form": "cone+solid"},

    "Assignment": {"id": 21, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.STATEMENTS, "form": "cube+arrow_in"},
    "ReturnStmt": {"id": 22, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.STATEMENTS, "form": "cube+arrow_up"},
    "ExpressionStmt": {"id": 23, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.STATEMENTS, "form": "cube+neutral"},

    "IfBranch": {"id": 24, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+split"},
    "LoopFor": {"id": 25, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+rotating"},
    "LoopWhile": {"id": 26, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+pulsing"},
    "SwitchCase": {"id": 27, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+multi"},
    "TryCatch": {"id": 28, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+shield"},
    "GuardClause": {"id": 29, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.CONTROL_STRUCTURES, "form": "torus+barrier"},

    "PureFunction": {"id": 30, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+smooth"},
    "ImpureFunction": {"id": 31, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+rough"},
    "AsyncFunction": {"id": 32, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+orbit"},
    "Generator": {"id": 33, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+spiral"},
    "Closure": {"id": 34, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+glow"},

    "CommandHandler": {"id": 35, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+gold"},
    "QueryHandler": {"id": 36, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+blue"},
    "EventHandler": {"id": 37, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+pulse"},
    "SagaStep": {"id": 38, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+chain"},
    "Middleware": {"id": 39, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+layered"},
    "Validator": {"id": 40, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+shield"},
    "Mapper": {"id": 41, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+arrows"},
    "Reducer": {"id": 42, "continent": Continent.LOGIC_FLOW, "fundamental": Fundamental.FUNCTIONS, "form": "octahedron+fold"},

    # Organization (Verde)
    "ValueObject": {"id": 43, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+crystal"},
    "Entity": {"id": 44, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+core"},
    "AggregateRoot": {"id": 45, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+crown"},
    "ReadModel": {"id": 46, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+transparent"},
    "Projection": {"id": 47, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+projector"},
    "DTO": {"id": 48, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+flat"},
    "Factory": {"id": 49, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.AGGREGATES, "form": "sphere+spark"},

    "BoundedContext": {"id": 50, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.MODULES, "form": "dodecahedron+thick"},
    "FeatureModule": {"id": 51, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.MODULES, "form": "dodecahedron+colored"},
    "InfrastructureAdapter": {"id": 52, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.MODULES, "form": "dodecahedron+plug"},
    "DomainPort": {"id": 53, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.MODULES, "form": "dodecahedron+socket"},
    "ApplicationPort": {"id": 54, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.MODULES, "form": "dodecahedron+arrow"},

    "SourceFile": {"id": 55, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.FILES, "form": "cube+language"},
    "ConfigFile": {"id": 56, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.FILES, "form": "cube+gear"},
    "MigrationFile": {"id": 57, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.FILES, "form": "cube+arrow_up"},
    "TestFile": {"id": 58, "continent": Continent.ORGANIZATION, "fundamental": Fundamental.FILES, "form": "cube+check"},

    # Execution (Âmbar)
    "MainEntry": {"id": 59, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+crown"},
    "CLIEntry": {"id": 60, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+terminal"},
    "LambdaEntry": {"id": 61, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+cloud"},
    "WorkerEntry": {"id": 62, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+gear"},
    "APIHandler": {"id": 63, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+globe"},
    "GraphQLResolver": {"id": 64, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+graph"},
    "WebSocketHandler": {"id": 65, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+wave"},

    "ContainerEntry": {"id": 66, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+docker"},
    "KubernetesJob": {"id": 67, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+helm"},
    "CronJob": {"id": 68, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+clock"},
    "MessageConsumer": {"id": 69, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+queue"},
    "QueueWorker": {"id": 70, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+worker"},
    "BackgroundThread": {"id": 71, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+twist"},
    "Actor": {"id": 72, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+envelope"},
    "Coroutine": {"id": 73, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+wave"},
    "Fiber": {"id": 74, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+fiber"},
    "WebWorker": {"id": 75, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+browser"},
    "ServiceWorker": {"id": 76, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+shield"},
    "ServerlessColdStart": {"id": 77, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+ice"},
    "HealthCheck": {"id": 78, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+heart"},
    "MetricsExporter": {"id": 79, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+graph"},
    "TracerProvider": {"id": 80, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+trace"},
    "LoggerInit": {"id": 81, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+log"},
    "ConfigLoader": {"id": 82, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+config"},
    "DependencyInjectionContainer": {"id": 83, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+syringe"},
    "PluginLoader": {"id": 84, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+plug"},
    "MigrationRunner": {"id": 85, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+db_up"},
    "SeedData": {"id": 86, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+seed"},
    "GracefulShutdown": {"id": 87, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+fade"},
    "PanicRecover": {"id": 88, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+parachute"},
    "CircuitBreakerInit": {"id": 89, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+broken"},
    "RateLimiter": {"id": 90, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+sand"},
    "CacheWarmer": {"id": 91, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+fire"},
    "FeatureFlagCheck": {"id": 92, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+toggle"},
    "ABTestRouter": {"id": 93, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+split"},
    "CanaryDeployTrigger": {"id": 94, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+bird"},
    "ChaosMonkey": {"id": 95, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+monkey"},
    "SelfHealingProbe": {"id": 96, "continent": Continent.EXECUTION, "fundamental": Fundamental.EXECUTABLES, "form": "icosahedron+heal"},
}

# ======================
# ESTRUTURAS DE DADOS
# ======================

@dataclass
class CodeSignal:
    """Sinais detectados no código"""
    has_io: bool = False
    has_state: bool = False
    is_async: bool = False
    is_generator: bool = False
    is_pure: bool = False
    handles_events: bool = False
    handles_commands: bool = False
    handles_queries: bool = False
    has_decorator: bool = False
    is_test: bool = False
    is_entry_point: bool = False
    database_access: bool = False
    http_access: bool = False
    file_access: bool = False
    queue_access: bool = False

@dataclass
class HadronClassification:
    """Resultado da classificação de um elemento de código"""
    element_id: str
    element_type: str  # function, class, variable, etc
    name: str
    file_path: str
    line_start: int
    line_end: int
    signals: CodeSignal
    hadron_type: Optional[str] = None
    fundamental: Optional[Fundamental] = None
    continent: Optional[Continent] = None
    confidence: float = 0.0
    reason: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['fundamental'] = self.fundamental.value if self.fundamental else None
        d['continent'] = self.continent.value if self.continent else None
        return d

# ======================
# MOTOR DE CLASSIFICAÇÃO
# ======================

class HadronClassifier:
    """Motor principal de classificação dos 96 hádrons"""

    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compila padrões regex para classificação rápida"""
        patterns = {
            'command_handler': [
                re.compile(r'.*handle.*[Cc]ommand.*'),
                re.compile(r'.*process.*[Cc]ommand.*'),
                re.compile(r'.*execute.*[Cc]ommand.*'),
            ],
            'query_handler': [
                re.compile(r'.*handle.*[Qq]uery.*'),
                re.compile(r'.*get.*[Bb]y.*'),
                re.compile(r'.*find.*[Bb]y.*'),
                re.compile(r'.*fetch.*'),
            ],
            'event_handler': [
                re.compile(r'.*on.*'),
                re.compile(r'.*handle.*[Ee]vent.*'),
                re.compile(r'.*@.*[Ee]vent.*'),
                re.compile(r'.*@Subscribe'),
                re.compile(r'.*@EventListener'),
            ],
            'middleware': [
                re.compile(r'.*[Mm]iddleware.*'),
                re.compile(r'.*interceptor.*'),
                re.compile(r'.*filter.*'),
            ],
            'validator': [
                re.compile(r'.*validate.*'),
                re.compile(r'.*check.*'),
                re.compile(r'.*verify.*'),
            ],
            'mapper': [
                re.compile(r'.*to.*Dto.*'),
                re.compile(r'.*from.*Dto.*'),
                re.compile(r'.*map.*'),
                re.compile(r'.*convert.*'),
            ],
            'reducer': [
                re.compile(r'.*reduce.*'),
                re.compile(r'.*combine.*'),
                re.compile(r'.*merge.*'),
            ],
            'entity': [
                re.compile(r'.*Entity.*'),
                re.compile(r'.*Model.*'),
            ],
            'value_object': [
                re.compile(r'.*Value.*'),
                re.compile(r'.*VO$'),
            ],
            'aggregate_root': [
                re.compile(r'.*Aggregate.*'),
                re.compile(r'.*Root.*'),
            ],
            'dto': [
                re.compile(r'.*Dto.*'),
                re.compile(r'.*Request.*'),
                re.compile(r'.*Response.*'),
            ],
            'factory': [
                re.compile(r'.*Factory.*'),
                re.compile(r'.*Builder.*'),
            ],
            'repository': [
                re.compile(r'.*Repository.*'),
                re.compile(r'.*Repo.*'),
            ],
            'service': [
                re.compile(r'.*Service.*'),
            ],
        }
        return patterns

    def analyze_function(self, node: ast.FunctionDef, signals: CodeSignal) -> HadronClassification:
        """Analisa uma função e determina seu hádron"""
        # Extrai sinais do AST
        self._extract_function_signals(node, signals)

        # Aplica regras de classificação
        hadron_type, confidence, reason = self._classify_function(node.name, signals)

        # Mapeia para partícula fundamental e continente
        if hadron_type in HADRON_CATALOG:
            catalog = HADRON_CATALOG[hadron_type]
            fundamental = catalog["fundamental"]
            continent = catalog["continent"]
        else:
            fundamental = Fundamental.FUNCTIONS
            continent = Continent.LOGIC_FLOW

        return HadronClassification(
            element_id=f"{node.name}:{node.lineno}",
            element_type="function",
            name=node.name,
            file_path="",  # Preenchido pelo caller
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            signals=signals,
            hadron_type=hadron_type,
            fundamental=fundamental,
            continent=continent,
            confidence=confidence,
            reason=reason
        )

    def _extract_function_signals(self, node: ast.FunctionDef, signals: CodeSignal):
        """Extrai sinais do AST da função"""
        # Detecta decorators
        if node.decorator_list:
            signals.has_decorator = True
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    if dec.id in ['app', 'router']:
                        signals.http_access = True
                    elif 'event' in dec.id.lower():
                        signals.handles_events = True

        # Detecta async
        if isinstance(node, ast.AsyncFunctionDef):
            signals.is_async = True

        # Detecta generator (yield)
        for child in ast.walk(node):
            if isinstance(child, ast.Yield) or isinstance(child, ast.YieldFrom):
                signals.is_generator = True

        # Detecta I/O operations
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    # Database operations
                    if child.func.attr in ['execute', 'fetchone', 'fetchall', 'commit', 'query']:
                        signals.database_access = True
                        signals.has_io = True
                    # File operations
                    elif child.func.attr in ['open', 'read', 'write', 'close']:
                        signals.file_access = True
                        signals.has_io = True
                    # HTTP operations
                    elif child.func.attr in ['get', 'post', 'put', 'delete', 'request']:
                        signals.http_access = True
                        signals.has_io = True

    def _classify_function(self, name: str, signals: CodeSignal) -> Tuple[str, float, str]:
        """Classifica o tipo de hádron baseado no nome e sinais"""

        # Regras específicas - maior prioridade
        if self._matches_patterns(name, self.patterns['command_handler']):
            return "CommandHandler", 0.9, f"Nome '{name}' corresponde a padrão de Command Handler"

        if self._matches_patterns(name, self.patterns['query_handler']):
            return "QueryHandler", 0.9, f"Nome '{name}' corresponde a padrão de Query Handler"

        if signals.handles_events or self._matches_patterns(name, self.patterns['event_handler']):
            return "EventHandler", 0.9, f"Detectado manipulador de eventos"

        if signals.is_generator:
            return "Generator", 0.95, f"Função usa yield/async generator"

        if signals.is_async:
            if not signals.has_io:
                return "AsyncFunction", 0.8, f"Função async sem I/O detectado"

        if self._matches_patterns(name, self.patterns['middleware']):
            return "Middleware", 0.85, f"Nome corresponde a padrão de Middleware"

        if self._matches_patterns(name, self.patterns['validator']):
            return "Validator", 0.85, f"Nome corresponde a padrão de Validator"

        if self._matches_patterns(name, self.patterns['mapper']):
            return "Mapper", 0.85, f"Nome corresponde a padrão de Mapper"

        if self._matches_patterns(name, self.patterns['reducer']):
            return "Reducer", 0.85, f"Nome corresponde a padrão de Reducer"

        # Regras genéricas - menor prioridade
        if signals.has_io:
            return "ImpureFunction", 0.7, f"Função tem operações de I/O"
        else:
            return "PureFunction", 0.6, f"Função não tem operações de I/O detectadas"

    def _matches_patterns(self, name: str, patterns: List[re.Pattern]) -> bool:
        """Verifica se o nome corresponde a algum padrão regex"""
        return any(pattern.match(name) for pattern in patterns)

    def analyze_class(self, node: ast.ClassDef, signals: CodeSignal) -> HadronClassification:
        """Analisa uma classe e determina seu hádron"""
        self._extract_class_signals(node, signals)

        hadron_type, confidence, reason = self._classify_class(node.name, signals)

        if hadron_type in HADRON_CATALOG:
            catalog = HADRON_CATALOG[hadron_type]
            fundamental = catalog["fundamental"]
            continent = catalog["continent"]
        else:
            fundamental = Fundamental.AGGREGATES
            continent = Continent.ORGANIZATION

        return HadronClassification(
            element_id=f"{node.name}:{node.lineno}",
            element_type="class",
            name=node.name,
            file_path="",
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            signals=signals,
            hadron_type=hadron_type,
            fundamental=fundamental,
            continent=continent,
            confidence=confidence,
            reason=reason
        )

    def _extract_class_signals(self, node: ast.ClassDef, signals: CodeSignal):
        """Extrai sinais do AST da classe"""
        # Detecta padrões de DDD
        signals.is_test = 'test' in node.name.lower() or 'spec' in node.name.lower()

        # Analisa métodos
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == '__init__':
                    # Verifica se tem ID (entidade)
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute):
                                    if 'id' in target.attr.lower():
                                        signals.has_state = True

        # Detecta herança
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in ['Entity', 'Model']:
                    signals.has_state = True

    def _classify_class(self, name: str, signals: CodeSignal) -> Tuple[str, float, str]:
        """Classifica o tipo de hádron para classes"""

        # Padrões específicos
        if self._matches_patterns(name, self.patterns['entity']):
            return "Entity", 0.9, f"Classe '{name}' corresponde a padrão de Entity"

        if self._matches_patterns(name, self.patterns['value_object']):
            return "ValueObject", 0.9, f"Classe '{name}' corresponde a padrão de Value Object"

        if self._matches_patterns(name, self.patterns['aggregate_root']):
            return "AggregateRoot", 0.9, f"Classe '{name}' corresponde a padrão de Aggregate Root"

        if self._matches_patterns(name, self.patterns['dto']):
            return "DTO", 0.85, f"Classe '{name}' corresponde a padrão de DTO"

        if self._matches_patterns(name, self.patterns['factory']):
            return "Factory", 0.85, f"Classe '{name}' corresponde a padrão de Factory"

        if self._matches_patterns(name, self.patterns['repository']):
            return "RepositoryImpl", 0.9, f"Classe '{name}' corresponde a padrão de Repository"

        if self._matches_patterns(name, self.patterns['service']):
            return "Service", 0.7, f"Classe '{name}' corresponde a padrão de Service"

        # Heurística base
        if signals.has_state:
            return "Entity", 0.6, f"Classe tem estado (atributos ID)"

        return "ValueObject", 0.5, f"Classe sem padrão específico detectado"

# ======================
# PIPELINE DE ANÁLISE
# ======================

class SpectrometerAnalyzer:
    """Pipeline principal de análise do Spectrometer v4"""

    def __init__(self):
        self.classifier = HadronClassifier()
        self.results: List[HadronClassification] = []

    def analyze_file(self, file_path: Path) -> List[HadronClassification]:
        """Analisa um arquivo Python e retorna os hádrons encontrados"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            file_results = []

            # Analisa funções e classes no nível superior
            for node in ast.walk(tree):
                signals = CodeSignal()

                if isinstance(node, ast.FunctionDef) and self._is_top_level(tree, node):
                    result = self.classifier.analyze_function(node, signals)
                    result.file_path = str(file_path)
                    file_results.append(result)

                elif isinstance(node, ast.ClassDef):
                    result = self.classifier.analyze_class(node, signals)
                    result.file_path = str(file_path)
                    file_results.append(result)

            return file_results

        except Exception as e:
            logger.error(f"Erro ao analisar arquivo {file_path}: {e}")
            return []

    def _is_top_level(self, tree: ast.AST, node: ast.AST) -> bool:
        """Verifica se o nó está no nível superior do módulo"""
        for child in ast.iter_child_nodes(tree):
            if child is node:
                return True
        return False

    def analyze_repository(self, repo_path: Path) -> Dict:
        """Analisa um repositório completo"""
        logger.info(f"Analisando repositório: {repo_path}")

        all_results = []
        file_count = 0

        # Busca arquivos Python
        for py_file in repo_path.rglob("*.py"):
            # Ignora diretórios comuns
            if any(part.startswith(('.', '__')) for part in py_file.parts):
                continue

            results = self.analyze_file(py_file)
            all_results.extend(results)
            file_count += 1

            if file_count % 50 == 0:
                logger.info(f"Analisados {file_count} arquivos...")

        # Compila estatísticas
        stats = self._compute_statistics(all_results)

        return {
            "repository": str(repo_path),
            "files_analyzed": file_count,
            "total_elements": len(all_results),
            "hadrons_found": len(set(r.hadron_type for r in all_results if r.hadron_type)),
            "coverage": self._compute_coverage(all_results),
            "statistics": stats,
            "elements": [r.to_dict() for r in all_results]
        }

    def _compute_statistics(self, results: List[HadronClassification]) -> Dict:
        """Computa estatísticas da análise"""
        stats = {
            "by_continent": {},
            "by_fundamental": {},
            "by_hadron": {},
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
            "unclassified": 0
        }

        for result in results:
            # Por continente
            if result.continent:
                continent = result.continent.name
                stats["by_continent"][continent] = stats["by_continent"].get(continent, 0) + 1

            # Por partícula fundamental
            if result.fundamental:
                fundamental = result.fundamental.value
                stats["by_fundamental"][fundamental] = stats["by_fundamental"].get(fundamental, 0) + 1

            # Por hádron
            if result.hadron_type:
                hadron = result.hadron_type
                stats["by_hadron"][hadron] = stats["by_hadron"].get(hadron, 0) + 1
            else:
                stats["unclassified"] += 1

            # Distribuição de confiança
            if result.confidence >= 0.8:
                stats["confidence_distribution"]["high"] += 1
            elif result.confidence >= 0.6:
                stats["confidence_distribution"]["medium"] += 1
            else:
                stats["confidence_distribution"]["low"] += 1

        return stats

    def _compute_coverage(self, results: List[HadronClassification]) -> float:
        """Computa cobertura dos 96 hádrons"""
        unique_hadrons = set(r.hadron_type for r in results if r.hadron_type)
        return (len(unique_hadrons) / len(HADRON_CATALOG)) * 100

# ======================
# VALIDATION EXPERIMENT
# ======================

class ValidationExperiment:
    """Experimento de validação dos 96 hádrons"""

    def __init__(self):
        self.analyzer = SpectrometerAnalyzer()
        self.test_repos = self._define_test_repositories()

    def _define_test_repositories(self) -> List[str]:
        """Define repositórios para teste diversificado"""
        # TODO: Expandir com 50+ repositórios reais
        return [
            # Micro-frameworks
            "https://github.com/pallets/flask",
            "https://github.com/django/django",
            "https://github.com/fastapi/fastapi",

            # Data Science
            "https://github.com/numpy/numpy",
            "https://github.com/pandas-dev/pandas",
            "https://github.com/scikit-learn/scikit-learn",

            # DevOps
            "https://github.com/ansible/ansible",
            "https://github.com/kubernetes/kubernetes",

            # Frontend (Python-based)
            "https://github.com/streamlit/streamlit",

            # Enterprise
            "https://github.com/apache/airflow",
            "https://github.com/odoo/odoo",
        ]

    def run_validation(self) -> Dict:
        """Executa experimento de validação completo"""
        logger.info("Iniciando experimento de validação dos 96 hádrons")

        results = {
            "experiment_id": f"validation_{int(time.time())}",
            "hadrons_catalog": len(HADRON_CATALOG),
            "repositories_tested": len(self.test_repos),
            "results": []
        }

        for repo_url in self.test_repos:
            logger.info(f"Validando repositório: {repo_url}")

            # Clone e análise (simplificado para exemplo)
            repo_name = repo_url.split('/')[-1]
            repo_path = Path(f"/tmp/{repo_name}")

            if not repo_path.exists():
                logger.warning(f"Repositório {repo_path} não encontrado. Pulando.")
                continue

            repo_results = self.analyzer.analyze_repository(repo_path)
            repo_results["url"] = repo_url
            results["results"].append(repo_results)

        # Compila estatísticas globais
        results["global_statistics"] = self._compile_global_stats(results["results"])

        # Identifica gaps
        results["gaps"] = self._identify_gaps(results["global_statistics"])

        return results

    def _compile_global_stats(self, repo_results: List[Dict]) -> Dict:
        """Compila estatísticas globais do experimento"""
        global_stats = {
            "total_files": 0,
            "total_elements": 0,
            "hadron_frequency": {},
            "missing_hadrons": set(),
            "avg_confidence": 0,
            "high_confidence_ratio": 0
        }

        total_confidence = 0
        high_conf_count = 0
        element_count = 0

        for repo in repo_results:
            global_stats["total_files"] += repo["files_analyzed"]
            global_stats["total_elements"] += repo["total_elements"]

            # Agrega frequência de hádrons
            for hadron, count in repo["statistics"]["by_hadron"].items():
                global_stats["hadron_frequency"][hadron] = global_stats["hadron_frequency"].get(hadron, 0) + count

            # Agrega confiança
            for elem in repo["elements"]:
                if elem["confidence"]:
                    total_confidence += elem["confidence"]
                    element_count += 1
                    if elem["confidence"] >= 0.8:
                        high_conf_count += 1

        global_stats["avg_confidence"] = total_confidence / element_count if element_count > 0 else 0
        global_stats["high_confidence_ratio"] = high_conf_count / element_count if element_count > 0 else 0

        # Identifica hádrons não encontrados
        all_found = set(global_stats["hadron_frequency"].keys())
        global_stats["missing_hadrons"] = set(HADRON_CATALOG.keys()) - all_found

        global_stats["coverage"] = len(all_found) / len(HADRON_CATALOG) * 100

        return global_stats

    def _identify_gaps(self, global_stats: Dict) -> List[Dict]:
        """Identifica gaps na taxonomia dos 96 hádrons"""
        gaps = []

        # Hádrons não encontrados
        if global_stats["missing_hadrons"]:
            gaps.append({
                "type": "missing_hadrons",
                "severity": "high",
                "description": f"Hádrons não encontrados em nenhum repositório: {len(global_stats['missing_hadrons'])}",
                "items": list(global_stats["missing_hadrons"])
            })

        # Hádrons raramente encontrados
        rare_hadrons = [h for h, c in global_stats["hadron_frequency"].items() if c < 5]
        if rare_hadrons:
            gaps.append({
                "type": "rare_hadrons",
                "severity": "medium",
                "description": f"Hádrons encontrados em menos de 5 ocorrências: {len(rare_hadrons)}",
                "items": rare_hadrons
            })

        # Baixa confiança geral
        if global_stats["avg_confidence"] < 0.7:
            gaps.append({
                "type": "low_confidence",
                "severity": "high",
                "description": f"Confiança média baixa: {global_stats['avg_confidence']:.2%}"
            })

        # Cobertura baixa
        if global_stats["coverage"] < 80:
            gaps.append({
                "type": "low_coverage",
                "severity": "high",
                "description": f"Cobertura baixa dos 96 hádrons: {global_stats['coverage']:.1f}%"
            })

        return gaps

    def save_results(self, results: Dict, output_path: Path):
        """Salva resultados do experimento"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Resultados salvos em: {output_path}")

# ======================
# EXECUÇÃO PRINCIPAL
# ======================

if __name__ == "__main__":
    import time

    # Executa experimento de validação
    experiment = ValidationExperiment()
    results = experiment.run_validation()

    # Salva resultados
    output_file = Path("spectrometer_validation_results.json")
    experiment.save_results(results, output_file)

    # Print resumo
    print("\n" + "="*60)
    print("SPECTROMETER v4 - VALIDATION RESULTS")
    print("="*60)
    print(f"Repositórios testados: {results['repositories_tested']}")
    print(f"Arquivos analisados: {results['global_statistics']['total_files']}")
    print(f"Elementos classificados: {results['global_statistics']['total_elements']}")
    print(f"Cobertura dos 96 hádrons: {results['global_statistics']['coverage']:.1f}%")
    print(f"Confiança média: {results['global_statistics']['avg_confidence']:.1%}")
    print(f"Hádrons não encontrados: {len(results['global_statistics']['missing_hadrons'])}")

    if results['gaps']:
        print("\nGAPS IDENTIFICADOS:")
        for gap in results['gaps']:
            print(f"  - {gap['description']}")

    print("\nResultados completos salvos em:", output_file)