#!/usr/bin/env python3
"""
SPECTROMETER V9 - FIXED VERSION
Parser híbrido robusto com fallback automático
Tree-sitter → LibCST → AST
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import statistics

# Imports principais
try:
    from tree_sitter import Language, Parser, Node
    from tree_sitter_languages import get_language, get_parser
    TREE_SITTER_AVAILABLE = True
    print("✅ Tree-sitter e tree-sitter-languages disponíveis")
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("⚠️ Tree-sitter não disponível. Usando fallbacks.")

try:
    import libcst as cst
    LIBCST_AVAILABLE = True
except ImportError:
    LIBCST_AVAILABLE = False
    print("⚠️ LibCST não disponível. Usando AST fallback.")

import ast
import hashlib

# Configurações
QUARK_TYPES = [
    "BITS", "BYTES", "PRIMITIVES", "VARIABLES",
    "EXPRESSIONS", "STATEMENTS", "CONTROL", "FUNCTIONS",
    "AGGREGATES", "MODULES", "FILES", "EXECUTABLES"
]

@dataclass
class Quark:
    """Quark fundamental do Standard Model do Código"""
    type: str
    value: str
    line: int
    column: int
    confidence: float
    source: str  # tree-sitter, libcst, ast, regex

@dataclass
class Hadron:
    """Hádron composto (padrão arquitetural)"""
    type: str
    name: str
    quarks: List[Quark]
    confidence: float
    haiku: Optional[str] = None
    valence_score: float = 1.0

class ParserEngine(Enum):
    """Motores de parsing disponíveis"""
    TREE_SITTER = "tree_sitter"
    LIBCST = "libcst"
    AST = "ast"
    REGEX = "regex"

class UniversalCodeParser:
    """Parser universal com fallback automático"""

    def __init__(self):
        self.engine_preferences = [
            ParserEngine.TREE_SITTER,
            ParserEngine.LIBCST,
            ParserEngine.AST,
            ParserEngine.REGEX
        ]
        self.parsers = {}
        self._init_parsers()

    def _init_parsers(self):
        """Inicializa os parsers disponíveis"""

        # Tree-sitter parsers
        if TREE_SITTER_AVAILABLE:
            try:
                self.parsers[ParserEngine.TREE_SITTER] = {
                    'python': get_parser('python'),
                    'javascript': get_parser('javascript'),
                    'typescript': get_parser('typescript'),
                    'java': get_parser('java'),
                    'go': get_parser('go'),
                    'rust': get_parser('rust'),
                    'c_sharp': get_parser('c_sharp'),
                    'php': get_parser('php'),
                    'ruby': get_parser('ruby'),
                    'kotlin': get_parser('kotlin')
                }
                print("✅ Tree-sitter parsers inicializados")
            except Exception as e:
                print(f"⚠️ Erro Tree-sitter: {e}")

        # LibCST
        if LIBCST_AVAILABLE:
            print("✅ LibCST disponível")

    def detect_language(self, file_path: Path) -> str:
        """Detecta linguagem do arquivo"""
        suffix = file_path.suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cs': 'c_sharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.swift': 'swift',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }

        return language_map.get(suffix, 'unknown')

    def parse_file(self, file_path: Path) -> List[Quark]:
        """Parseia arquivo com fallback automático"""

        language = self.detect_language(file_path)
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Tenta cada motor em ordem de preferência
        for engine in self.engine_preferences:
            try:
                if engine == ParserEngine.TREE_SITTER and TREE_SITTER_AVAILABLE:
                    if language in self.parsers.get(ParserEngine.TREE_SITTER, {}):
                        return self._parse_tree_sitter(content, language)

                elif engine == ParserEngine.LIBCST and LIBCST_AVAILABLE:
                    if language == 'python':
                        return self._parse_libcst(content)

                elif engine == ParserEngine.AST:
                    if language == 'python':
                        return self._parse_ast(content)

                elif engine == ParserEngine.REGEX:
                    return self._parse_regex(content, language)

            except Exception as e:
                print(f"⚠️ Falha motor {engine.value}: {e}")
                continue

        # Se tudo falhar, usa regex básico
        return self._parse_regex(content, language)

    def _parse_tree_sitter(self, content: str, language: str) -> List[Quark]:
        """Parse com Tree-sitter"""
        quarks = []
        parser = self.parsers[ParserEngine.TREE_SITTER][language]
        tree = parser.parse(bytes(content, 'utf-8'))

        # Extrai nós da árvore
        def extract_nodes(node: Node, depth: int = 0):
            if depth > 50:  # Prevenir recursão infinita
                return

            # Mapeia tipos de nó para quarks
            quark_type = self._map_node_to_quark(node.type)
            if quark_type:
                # Extrai valor do nó
                start_pos = node.start_point
                value = content[node.start_byte:node.end_byte].strip()

                if value:
                    quarks.append(Quark(
                        type=quark_type,
                        value=value,
                        line=start_pos[0] + 1,
                        column=start_pos[1] + 1,
                        confidence=0.95,
                        source='tree-sitter'
                    ))

            # Recursão para filhos
            for child in node.children:
                extract_nodes(child, depth + 1)

        extract_nodes(tree.root_node)
        return quarks

    def _parse_libcst(self, content: str) -> List[Quark]:
        """Parse com LibCST (Python only)"""
        quarks = []

        try:
            tree = cst.parse_module(content)

            class QuarkExtractor(cst.CSTVisitor):
                def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
                    quarks.append(Quark(
                        type='FUNCTIONS',
                        value=node.name.value,
                        line=node.position.start.line if node.position else 0,
                        column=node.position.start.column if node.position else 0,
                        confidence=0.90,
                        source='libcst'
                    ))
                    # Não chama generic_visit para evitar duplicatas

                def visit_ClassDef(self, node: cst.ClassDef) -> None:
                    quarks.append(Quark(
                        type='AGGREGATES',
                        value=node.name.value,
                        line=node.position.start.line if node.position else 0,
                        column=node.position.start.column if node.position else 0,
                        confidence=0.90,
                        source='libcst'
                    ))

                def visit_Assign(self, node: cst.Assign) -> None:
                    for target in node.targets:
                        if isinstance(target, cst.Name):
                            quarks.append(Quark(
                                type='VARIABLES',
                                value=target.value,
                                line=target.position.start.line if target.position else 0,
                                column=target.position.start.column if target.position else 0,
                                confidence=0.85,
                                source='libcst'
                            ))

            visitor = QuarkExtractor()
            tree.visit(visitor)

        except Exception as e:
            print(f"⚠️ Erro LibCST: {e}")

        return quarks

    def _parse_ast(self, content: str) -> List[Quark]:
        """Parse com AST nativo (Python)"""
        quarks = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    quarks.append(Quark(
                        type='FUNCTIONS',
                        value=node.name,
                        line=node.lineno,
                        column=node.col_offset or 0,
                        confidence=0.85,
                        source='ast'
                    ))

                elif isinstance(node, ast.ClassDef):
                    quarks.append(Quark(
                        type='AGGREGATES',
                        value=node.name,
                        line=node.lineno,
                        column=node.col_offset or 0,
                        confidence=0.85,
                        source='ast'
                    ))

                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    quarks.append(Quark(
                        type='VARIABLES',
                        value=node.id,
                        line=node.lineno,
                        column=node.col_offset or 0,
                        confidence=0.80,
                        source='ast'
                    ))

        except Exception as e:
            print(f"⚠️ Erro AST: {e}")

        return quarks

    def _parse_regex(self, content: str, language: str) -> List[Quark]:
        """Parse com regex (fallback universal)"""
        quarks = []
        lines = content.split('\n')

        # Padrões por linguagem
        patterns = {
            'python': {
                'FUNCTIONS': [r'def\s+(\w+)\s*\(', r'async\s+def\s+(\w+)\s*\('],
                'AGGREGATES': [r'class\s+(\w+)\s*:'],
                'VARIABLES': [r'(\w+)\s*='],
                'MODULES': [r'import\s+(\w+)', r'from\s+(\w+)', r'from\s+\w+\s+import\s+(\w+)'],
                'CONTROL': [r'if\s+.*:', r'for\s+\w+\s+in\s+.*:', r'while\s+.*:', r'try\s*:'],
                'STATEMENTS': [r'return\s+', r'yield\s+', r'raise\s+', r'break\b', r'continue\b']
            },
            'javascript': {
                'FUNCTIONS': [r'function\s+(\w+)\s*\(', r'const\s+(\w+)\s*=\s*\(', r'(\w+)\s*=>\s*{'],
                'AGGREGATES': [r'class\s+(\w+)\s*{'],
                'VARIABLES': [r'(?:const|let|var)\s+(\w+)\s*='],
                'CONTROL': [r'if\s*\(', r'for\s*\(', r'while\s*\(', r'switch\s*\(']
            },
            'java': {
                'FUNCTIONS': [r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', r'void\s+(\w+)\s*\('],
                'AGGREGATES': [r'(?:public\s+)?class\s+(\w+)', r'interface\s+(\w+)'],
                'VARIABLES': [r'(?:\w+\s+)+(\w+)\s*='],
                'CONTROL': [r'if\s*\(', r'for\s*\(', r'while\s*\(', r'switch\s*\(']
            }
        }

        # Padrão genérico se linguagem não encontrada
        generic_patterns = {
            'FUNCTIONS': [r'(?:function|def|func)\s+(\w+)\s*\(', r'(\w+)\s*\([^)]*\)\s*{'],
            'AGGREGATES': [r'(?:class|interface|struct)\s+(\w+)'],
            'VARIABLES': [r'(\w+)\s*='],
            'CONTROL': [r'if\s*\(', r'for\s*\(', r'while\s*\(', r'switch\s*\(']
        }

        lang_patterns = patterns.get(language, generic_patterns)

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            for quark_type, pattern_list in lang_patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        quarks.append(Quark(
                            type=quark_type,
                            value=value,
                            line=line_num,
                            column=line.find(value) + 1,
                            confidence=0.60,  # Menor confiança para regex
                            source='regex'
                        ))

        return quarks

    def _map_node_to_quark(self, node_type: str) -> Optional[str]:
        """Mapeia tipo de nó Tree-sitter para quark"""
        mapping = {
            # Funções
            'function_definition': 'FUNCTIONS',
            'function_declaration': 'FUNCTIONS',
            'method_definition': 'FUNCTIONS',
            'lambda_expression': 'FUNCTIONS',
            'arrow_function': 'FUNCTIONS',

            # Classes/Structs
            'class_definition': 'AGGREGATES',
            'class_declaration': 'AGGREGATES',
            'struct_definition': 'AGGREGATES',
            'interface_definition': 'AGGREGATES',

            # Variáveis
            'variable_declaration': 'VARIABLES',
            'assignment': 'VARIABLES',
            'identifier': 'VARIABLES',

            # Controle
            'if_statement': 'CONTROL',
            'for_statement': 'CONTROL',
            'while_statement': 'CONTROL',
            'switch_statement': 'CONTROL',
            'try_statement': 'CONTROL',

            # Módulos/Imports
            'import_statement': 'MODULES',
            'import_from_statement': 'MODULES',
            'module': 'MODULES',

            # Expressões
            'binary_expression': 'EXPRESSIONS',
            'unary_expression': 'EXPRESSIONS',
            'call_expression': 'EXPRESSIONS',
            'member_expression': 'EXPRESSIONS',

            # Statements
            'return_statement': 'STATEMENTS',
            'break_statement': 'STATEMENTS',
            'continue_statement': 'STATEMENTS',
            'throw_statement': 'STATEMENTS',
            'expression_statement': 'STATEMENTS'
        }

        return mapping.get(node_type)

class HadronClassifier:
    """Classificador de hádrons com regras refinadas"""

    def __init__(self):
        # Regras refinadas baseadas nos testes
        self.rules = {
            'Service': [
                r'(\w*Service\w*)',
                r'(\w*Manager\w*)',
                r'(\w*Handler\w*)',
                r'(\w*Controller\w*)',
                r'(\w*Orchestrator\w*)',
                r'class.*Service.*:',
                r'@Service',
                r'@Component'
            ],
            'Entity': [
                r'class\s+(\w+Entity\w*)',
                r'class\s+(\w+Model\w*)',
                r'@Entity',
                r'@Table',
                r'dataclass.*\w+',
                r'class.*\{.*id:.*\}'
            ],
            'RepositoryImpl': [
                r'(\w*Repository\w*)',
                r'(\w*DAO\w*)',
                r'interface\s+(\w*Repository\w*)',
                r'@Repository'
            ],
            'CommandHandler': [
                r'(handle\w*)',
                r'(create\w*)',
                r'(save\w*)',
                r'(delete\w*)',
                r'(update\w*)',
                r'(post\w*)',
                r'(process\w*)',
                r'(execute\w*)'
            ],
            'QueryHandler': [
                r'(get\w*)',
                r'(find\w*)',
                r'(query\w*)',
                r'(search\w*)',
                r'(list\w*)',
                r'(fetch\w*)',
                r'(retrieve\w*)',
                r'load\w*'
            ],
            'APIHandler': [
                r'@.*Mapping',
                r'@.*Route',
                r'@.*Endpoint',
                r'app\.(get|post|put|delete)',
                r'router\.(get|post|put|delete)',
                r'(@\w*(?:Request|Response))'
            ],
            'TestFunction': [
                r'(test\w*)',
                r'(spec\w*)',
                r'(it\w*)',
                r'describe\s*\(',
                r'it\s*\(',
                r'def test_',
                r'async\s+def test_',
                r'@test',
                r'@Test',
                r'@TestCase'
            ],
            'Constructor': [
                r'__init__',
                r'constructor\s*\(',
                r'def __init__',
                r'initialize\s*\('
            ],
            'AsyncFunction': [
                r'async\s+def\s+(\w+)',
                r'async\s+function\s+(\w+)',
                r'(\w+)\.then\(',
                r'await\s+',
                r'Promise\.'
            ],
            'ImportStatement': [
                r'^import\s+',
                r'^from\s+',
                r'^require\s*\(',
                r'^#include\s+',
                r'use\s+\w+;'
            ]
        }

    def classify_quarks(self, quarks: List[Quark]) -> List[Hadron]:
        """Classifica quarks em hádrons"""
        hadrons = []

        # Agrupa quarks por elemento
        elements = self._group_quarks_by_element(quarks)

        for element_name, element_quarks in elements.items():
            # Determina tipo de hádron
            hadron_type = self._determine_hadron_type(element_quarks)

            # Calcula confiança
            confidence = self._calculate_confidence(element_quarks, hadron_type)

            # Aplica regras de valência
            valence_score = self._calculate_valence(element_quarks, hadron_type)

            hadrons.append(Hadron(
                type=hadron_type,
                name=element_name,
                quarks=element_quarks,
                confidence=confidence,
                valence_score=valence_score
            ))

        return hadrons

    def _group_quarks_by_element(self, quarks: List[Quark]) -> Dict[str, List[Quark]]:
        """Agrupa quarks por elemento (função, classe, etc.)"""
        elements = {}

        for quark in quarks:
            # Extrai nome base do elemento
            if quark.type == 'FUNCTIONS':
                # Para funções, usa o nome como chave
                key = quark.value
            elif quark.type == 'AGGREGATES':
                # Para classes, usa o nome
                key = quark.value
            else:
                # Para outros, agrupa por linha
                key = f"{quark.line}_{quark.type}"

            if key not in elements:
                elements[key] = []
            elements[key].append(quark)

        return elements

    def _determine_hadron_type(self, quarks: List[Quark]) -> str:
        """Determina o tipo de hádron baseado nos quarks"""

        # Concatena valores dos quarks para análise
        combined_values = ' '.join([q.value for q in quarks]).lower()

        # Verifica regras em ordem de especificidade
        for hadron_type, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, combined_values, re.IGNORECASE):
                    # Evita falsos positivos comuns
                    if self._validate_classification(hadron_type, combined_values):
                        return hadron_type

        # Default baseado no tipo principal
        main_quark = max(quarks, key=lambda q: q.confidence)

        if main_quark.type == 'FUNCTIONS':
            if 'test' in main_quark.value.lower():
                return 'TestFunction'
            elif 'async' in combined_values or 'await' in combined_values:
                return 'AsyncFunction'
            elif any(word in combined_values for word in ['get', 'find', 'query']):
                return 'QueryHandler'
            elif any(word in combined_values for word in ['save', 'create', 'delete', 'update']):
                return 'CommandHandler'
            else:
                return 'PureFunction'
        elif main_quark.type == 'AGGREGATES':
            if any(word in combined_values for word in ['entity', 'model', 'table']):
                return 'Entity'
            elif any(word in combined_values for word in ['service', 'manager', 'controller']):
                return 'Service'
            elif any(word in combined_values for word in ['repository', 'dao']):
                return 'RepositoryImpl'
            else:
                return 'Aggregate'
        elif main_quark.type == 'MODULES':
            return 'ImportStatement'
        else:
            return 'Unclassified'

    def _validate_classification(self, hadron_type: str, combined_values: str) -> bool:
        """Valida para evitar falsos positivos"""

        # Regras de exclusão
        if hadron_type == 'Service':
            # Evita classificar getters/setters como Service
            if any(word in combined_values for word in ['get_', 'set_', 'is_', 'has_']):
                return False
            # Evita variáveis com 'service' no nome
            if 'service.' in combined_values and len(combined_values.split()) < 3:
                return False

        elif hadron_type == 'QueryHandler':
            # Evita variáveis com 'get' no nome
            if combined_values.count('=') > 0 and len(combined_values.split()) < 3:
                return False

        elif hadron_type == 'TestFunction':
            # Deve ter padrões de teste
            if not any(word in combined_values for word in ['assert', 'expect', 'should', 'test', 'spec']):
                return False

        return True

    def _calculate_confidence(self, quarks: List[Quark], hadron_type: str) -> float:
        """Calcula confiança da classificação"""

        # Média ponderada das confianças dos quarks
        weights = {'FUNCTIONS': 0.4, 'AGGREGATES': 0.4, 'MODULES': 0.2}

        weighted_sum = 0
        total_weight = 0

        for quark in quarks:
            weight = weights.get(quark.type, 0.1)
            weighted_sum += quark.confidence * weight
            total_weight += weight

        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0

        # Ajuste baseado no tipo de hadron
        if hadron_type in ['Service', 'Entity', 'RepositoryImpl']:
            return min(0.95, base_confidence + 0.1)
        elif hadron_type == 'Unclassified':
            return max(0.1, base_confidence - 0.2)

        return base_confidence

    def _calculate_valence(self, quarks: List[Quark], hadron_type: str) -> float:
        """Calcula score de valência (coerência)"""

        score = 1.0

        # Penalizações por inconsistências
        if hadron_type == 'Service':
            # Service sem métodos
            func_count = sum(1 for q in quarks if q.type == 'FUNCTIONS')
            if func_count == 0:
                score -= 0.3

        elif hadron_type == 'Entity':
            # Entity sem atributos
            if not any('id' in q.value.lower() for q in quarks):
                score -= 0.2

        elif hadron_type == 'TestFunction':
            # Test sem asserts
            if not any('assert' in q.value.lower() or 'expect' in q.value.lower()
                      for q in quarks):
                score -= 0.2

        return max(0.1, score)

class SpectrometerV9:
    """Spectrometer V9 - Versão corrigida com parser híbrido"""

    def __init__(self):
        self.parser = UniversalCodeParser()
        self.classifier = HadronClassifier()
        self.metrics = {
            'files_processed': 0,
            'total_quarks': 0,
            'total_hadrons': 0,
            'parser_usage': {engine.value: 0 for engine in ParserEngine}
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analisa um arquivo individual"""

        start_time = time.time()

        try:
            # 1. Parseia o arquivo
            quarks = self.parser.parse_file(file_path)

            # Atualiza métricas
            self.metrics['files_processed'] += 1
            self.metrics['total_quarks'] += len(quarks)

            # 2. Classifica em hádrons
            hadrons = self.classifier.classify_quarks(quarks)
            self.metrics['total_hadrons'] += len(hadrons)

            # 3. Atualiza uso do parser
            if quarks:
                parser_used = quarks[0].source
                if parser_used in self.metrics['parser_usage']:
                    self.metrics['parser_usage'][parser_used] += 1

            # 4. Gera hash do conteúdo para cache
            content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()

            duration = time.time() - start_time

            return {
                'file_path': str(file_path),
                'language': self.parser.detect_language(file_path),
                'quarks': [{'type': q.type, 'value': q.value, 'line': q.line,
                           'column': q.column, 'confidence': q.confidence, 'source': q.source}
                          for q in quarks],
                'hadrons': [{'type': h.type, 'name': h.name, 'confidence': h.confidence,
                            'valence_score': h.valence_score, 'quark_count': len(h.quarks)}
                           for h in hadrons],
                'metrics': {
                    'quark_count': len(quarks),
                    'hadron_count': len(hadrons),
                    'avg_confidence': statistics.mean([h.confidence for h in hadrons]) if hadrons else 0,
                    'avg_valence': statistics.mean([h.valence_score for h in hadrons]) if hadrons else 1.0
                },
                'duration': duration,
                'content_hash': content_hash,
                'timestamp': time.time()
            }

        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'quarks': [],
                'hadrons': [],
                'metrics': {'error': True}
            }

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa um repositório completo"""

        print(f"\n🔍 SPECTROMETER V9 - FIXED VERSION")
        print(f"📁 Analisando: {repo_path}")
        print(f"============================================================")

        results = []

        # Encontra arquivos para analisar
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cs', '.php', '.rb', '.kt']
        files = []

        for ext in extensions:
            files.extend(repo_path.rglob(f'*{ext}'))

        # Limita para não sobrecarregar
        max_files = 100
        if len(files) > max_files:
            files = files[:max_files]
            print(f"  📊 Limitando a {max_files} arquivos")

        # Analisa cada arquivo
        for file_path in files:
            print(f"  📄 {file_path.relative_to(repo_path)}")
            result = self.analyze_file(file_path)
            results.append(result)

        # Gera relatório final
        successful = [r for r in results if 'error' not in r]

        if successful:
            total_quarks = sum(r['metrics']['quark_count'] for r in successful)
            total_hadrons = sum(r['metrics']['hadron_count'] for r in successful)
            avg_confidence = statistics.mean([r['metrics'].get('avg_confidence', 0) for r in successful])
            avg_valence = statistics.mean([r['metrics'].get('avg_valence', 1.0) for r in successful])

            # Conta hadrons por tipo
            hadron_types = {}
            for result in successful:
                for hadron in result['hadrons']:
                    hadron_type = hadron['type']
                    hadron_types[hadron_type] = hadron_types.get(hadron_type, 0) + 1

            # Calcula score V9
            hadron_diversity = len(hadron_types) / 10  # Normalizado para 10 tipos
            confidence_score = avg_confidence
            valence_score = avg_valence
            coverage = total_hadrons / max(total_quarks, 1)

            score_v9 = min(100, (hadron_diversity * 20 + confidence_score * 30 +
                               valence_score * 30 + coverage * 20))

            print(f"\n============================================================")
            print(f"📊 SPECTROMETER V9 - REPORT")
            print(f"============================================================")
            print(f"📁 Repositório: {repo_path}")
            print(f"📄 Arquivos analisados: {len(successful)}")
            print(f"⚛️  Quarks brutos: {total_quarks}")
            print(f"🎯 Elementos classificados: {total_hadrons}")
            print(f"📈 Parser usage: {self.metrics['parser_usage']}")
            print(f"🎯 Confiança média: {avg_confidence:.1%}")
            print(f"⚖️  Valência média: {avg_valence:.2f}")
            print(f"🏆 SCORE V9: {score_v9:.1f}/100")
            print(f"============================================================")

            return {
                'repository_path': str(repo_path),
                'classified_elements': total_hadrons,
                'hadron_distribution': hadron_types,
                'score_v9': score_v9,
                'metrics': {
                    'files_analyzed': len(successful),
                    'total_quarks': total_quarks,
                    'total_hadrons': total_hadrons,
                    'avg_confidence': avg_confidence,
                    'avg_valence': avg_valence,
                    'parser_usage': self.metrics['parser_usage']
                },
                'files': results
            }
        else:
            print("\n❌ Nenhum arquivo analisado com sucesso")
            return {
                'repository_path': str(repo_path),
                'error': 'No files analyzed successfully',
                'files': results
            }

# Teste rápido
if __name__ == "__main__":
    spectrometer = SpectrometerV9()

    # Cria arquivo de teste
    test_file = Path("/tmp/test_spectrometer.py")
    test_file.write_text("""
class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, user_data):
        return self.repository.save(user_data)

    def get_user(self, user_id):
        return self.repository.find_by_id(user_id)

class UserRepository:
    def save(self, user):
        print(f"Saving {user}")
        return user

    def find_by_id(self, user_id):
        return {"id": user_id}

def test_user_creation():
    service = UserService()
    user = service.create_user({"name": "John"})
    assert user["name"] == "John"
""")

    # Analisa
    result = spectrometer.analyze_repository(Path("/tmp"))

    # Mostra resultados
    print("\n🎯 Hadrons encontrados:")
    for hadron in result.get('files', [{}])[0].get('hadrons', []):
        print(f"  - {hadron['type']}: {hadron['name']} (conf: {hadron['confidence']:.2f})")

    # Limpa
    test_file.unlink()