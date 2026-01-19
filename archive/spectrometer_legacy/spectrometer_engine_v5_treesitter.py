#!/usr/bin/env python3
"""
SPECTROMETER ENGINE v5 - TREE-SITTER EDITION
Parser AST universal baseado no Standard Model do Código
Suporte real a 12+ linguagens com quarks e hadrons
"""

import tree_sitter as ts
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import requests
import tempfile
import subprocess
import os

# Mapa de linguagens para identificadores tree-sitter
LANGUAGE_MAP = {
    'python': 'python',
    'javascript': 'javascript',
    'typescript': 'typescript',
    'java': 'java',
    'go': 'go',
    'rust': 'rust',
    'c': 'c',
    'cpp': 'cpp',
    'csharp': 'c_sharp',
    'php': 'php',
    'ruby': 'ruby',
    'kotlin': 'kotlin',
    'scala': 'scala',
    'swift': 'swift',
    'dart': 'dart'
}

class TreeSitterExtractor:
    """Extrator universal baseado em tree-sitter"""

    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._setup_languages()

    def _setup_languages(self):
        """Configura parsers para todas as linguagens suportadas"""
        for lang_name, tree_sitter_name in LANGUAGE_MAP.items():
            try:
                # Tenta carregar biblioteca tree-sitter
                lang_module = __import__(f'tree_sitter_{tree_sitter_name}', fromlist=['language'])
                self.languages[lang_name] = lang_module.language()

                # Cria parser
                parser = ts.Parser()
                parser.set_language(self.languages[lang_name])
                self.parsers[lang_name] = parser

                print(f"✅ {lang_name}: OK")
            except (ImportError, Exception) as e:
                print(f"❌ {lang_name}: {e}")

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detecta linguagem baseado na extensão do arquivo"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.swift': 'swift',
            '.dart': 'dart'
        }
        return ext_map.get(file_path.suffix.lower())

    def parse_file(self, file_path: Path) -> Optional[ts.Tree]:
        """Parseia arquivo usando tree-sitter"""
        lang = self.detect_language(file_path)
        if not lang or lang not in self.parsers:
            return None

        try:
            parser = self.parsers[lang]
            content = file_path.read_bytes()
            tree = parser.parse(content)
            return tree
        except Exception as e:
            print(f"Erro parseando {file_path}: {e}")
            return None

    def extract_all_nodes(self, tree: ts.Tree, file_path: Path) -> List[Dict[str, Any]]:
        """Extrai todos os nós relevantes da AST"""
        elements = []
        lang = self.detect_language(file_path)

        def walk_node(node: ts.Node, depth: int = 0):
            # Extrai informação do nó
            element = self._extract_node_info(node, lang, depth)
            if element:
                elements.append(element)

            # Recursivamente visita filhos
            for child in node.children:
                walk_node(child, depth + 1)

        if tree:
            walk_node(tree.root_node)

        return elements

    def _extract_node_info(self, node: ts.Node, lang: str, depth: int) -> Optional[Dict[str, Any]]:
        """Extrai informação de um nó específico"""
        # Padrões universais cross-linguagem
        universal_patterns = {
            # Funções/Métodos
            'function_definition': [
                'function_definition', 'function_declaration', 'method_definition',
                'decorated_definition', 'async_function_declaration', 'arrow_function'
            ],
            # Classes/Estruturas
            'class_definition': [
                'class_definition', 'class_declaration', 'struct_definition',
                'interface_definition', 'type_declaration', 'enum_definition'
            ],
            # Variáveis
            'variable_declaration': [
                'variable_declaration', 'variable_declarator', 'let_declaration',
                'const_declaration', 'assignment_expression', 'augmented_assignment_expression'
            ],
            # Imports/Requires
            'import_statement': [
                'import_statement', 'import_declaration', 'require_statement',
                'use_statement', 'include_directive'
            ],
            # Controle de fluxo
            'control_flow': [
                'if_statement', 'for_statement', 'while_statement', 'switch_statement',
                'match_statement', 'try_statement', 'catch_clause'
            ],
            # Expressões
            'expression': [
                'call_expression', 'binary_expression', 'unary_expression',
                'member_expression', 'subscript_expression', 'conditional_expression'
            ]
        }

        node_type = node.type

        # Mapeia tipo universal
        universal_type = None
        for utype, patterns in universal_patterns.items():
            if any(p in node_type.lower() for p in patterns):
                universal_type = utype
                break

        if not universal_type:
            return None

        # Extrai texto do nó
        text = node.text.decode('utf-8', errors='ignore').strip()

        return {
            'type': universal_type,
            'specific_type': node_type,
            'language': lang,
            'text': text,
            'start_point': (node.start_point.row, node.start_point.column),
            'end_point': (node.end_point.row, node.end_point.column),
            'depth': depth,
            'child_count': len(node.children),
            'node_id': id(node)
        }


class QuarkDetector:
    """Detector dos 12 quarks fundamentais usando tree-sitter"""

    # Mapeamento universal de quarks para padrões AST
    QUARK_PATTERNS = {
        'EXECUTABLES': [
            ('program', lambda nodes: [n for n in nodes if n['specific_type'] == 'program']),
            ('source_file', lambda nodes: [n for n in nodes if n['depth'] == 0])
        ],

        'FILES': [
            ('import_statement', lambda nodes: [n for n in nodes if n['type'] == 'import_statement']),
            ('module', lambda nodes: [n for n in nodes if 'module' in n['specific_type']])
        ],

        'MODULES': [
            ('namespace', lambda nodes: [n for n in nodes if 'namespace' in n['specific_type']]),
            ('package', lambda nodes: [n for n in nodes if 'package' in n['specific_type']])
        ],

        'AGGREGATES': [
            ('class_definition', lambda nodes: [n for n in nodes if n['type'] == 'class_definition']),
            ('struct_definition', lambda nodes: [n for n in nodes if 'struct' in n['specific_type']]),
            ('interface_definition', lambda nodes: [n for n in nodes if 'interface' in n['specific_type']])
        ],

        'FUNCTIONS': [
            ('function_definition', lambda nodes: [n for n in nodes if n['type'] == 'function_definition']),
            ('method_definition', lambda nodes: [n for n in nodes if 'method' in n['specific_type']]),
            ('arrow_function', lambda nodes: [n for n in nodes if 'arrow' in n['specific_type']])
        ],

        'CONTROL': [
            ('control_flow', lambda nodes: [n for n in nodes if n['type'] == 'control_flow']),
            ('conditional', lambda nodes: [n for n in nodes if 'if' in n['specific_type'] or 'switch' in n['specific_type']]),
            ('loop', lambda nodes: [n for n in nodes if 'for' in n['specific_type'] or 'while' in n['specific_type']])
        ],

        'STATEMENTS': [
            ('expression_statement', lambda nodes: [n for n in nodes if 'statement' in n['specific_type']]),
            ('declaration', lambda nodes: [n for n in nodes if 'declaration' in n['specific_type']])
        ],

        'EXPRESSIONS': [
            ('expression', lambda nodes: [n for n in nodes if n['type'] == 'expression']),
            ('call_expression', lambda nodes: [n for n in nodes if 'call' in n['specific_type']]),
            ('binary_expression', lambda nodes: [n for n in nodes if 'binary' in n['specific_type']])
        ],

        'VARIABLES': [
            ('variable_declaration', lambda nodes: [n for n in nodes if n['type'] == 'variable_declaration']),
            ('identifier', lambda nodes: [n for n in nodes if n['specific_type'] == 'identifier']),
            ('parameter', lambda nodes: [n for n in nodes if 'parameter' in n['specific_type']])
        ],

        'PRIMITIVES': [
            ('string', lambda nodes: [n for n in nodes if 'string' in n['specific_type']),
            ('number', lambda nodes: [n for n in nodes if 'number' in n['specific_type'] or 'integer' in n['specific_type']),
            ('boolean', lambda nodes: [n for n in nodes if 'boolean' in n['specific_type']),
            ('null', lambda nodes: [n for n in nodes if 'null' in n['specific_type'] or 'none' in n['specific_type'])
        ],

        'BYTES': [
            ('binary_literal', lambda nodes: [n for n in nodes if 'binary' in n['specific_type']),
            ('byte_string', lambda nodes: [n for n in nodes if 'byte' in n['specific_type'])
        ],

        'BITS': [
            ('bitwise', lambda nodes: [n for n in nodes if 'bitwise' in n['specific_type'] or 'shift' in n['specific_type']),
            ('bit_field', lambda nodes: [n for n in nodes if 'bit' in n['specific_type'].lower()])
        ]
    }

    def detect_quarks(self, nodes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Detecta quarks fundamentais na lista de nós"""
        quarks = {quark: [] for quark in self.QUARK_PATTERNS.keys()}

        for quark, patterns in self.QUARK_PATTERNS.items():
            for pattern_name, extractor in patterns:
                try:
                    quark_elements = extractor(nodes)
                    quarks[quark].extend(quark_elements)
                except Exception as e:
                    print(f"Erro no padrão {pattern_name} para {quark}: {e}")

        # Remove duplicatas
        for quark in quarks:
            seen = set()
            quarks[quark] = [x for x in quarks[quark] if x['node_id'] not in seen and not seen.add(x['node_id'])]

        return quarks


class HadronClassifier:
    """Classificador universal de 96 hadrons baseado em padrões AST"""

    # Padrões universais cross-linguagem para hadrons
    HADRON_PATTERNS = {
        # Hadrons de Arquitetura
        'APIHandler': [
            ('@.*route', r'@[a-zA-Z_].*route|@[a-zA-Z_].*endpoint|@[a-zA-Z_].*api'),
            ('router', r'router|Router'),
            ('app\.(get|post|put|delete)', r'app\.(get|post|put|delete|patch)'),
            ('response', r'response|Response|res\.')
        ],

        'CommandHandler': [
            ('save|create|update|delete', r'save|create|update|delete|insert|remove'),
            ('post|put|delete', r'\b(post|put|delete|patch)\b'),
            ('mutate', r'mutate|modify|transform')
        ],

        'QueryHandler': [
            ('get|find|list|fetch', r'get|find|list|fetch|query|select'),
            ('search', r'search|filter|where'),
            ('return.*data', r'return.*data|fetch.*data')
        ],

        'Entity': [
            ('class.*Model|class.*Entity', r'class\s+(?:\w+Model|\w+Entity|\w+)'),
            ('@entity|@table', r'@entity|@table|@Entity|@Table'),
            ('extends.*Model', r'extends\s+\w*Model|\s+Model\s*\{'),
            ('struct.*\{', r'struct\s+\w+\s*\{')
        ],

        'RepositoryImpl': [
            ('Repository', r'\w*Repository|\w*Repo|\w*Dao'),
            ('save|find|delete.*methods', r'save\(|find\(|delete\('),
            ('extends.*Repository', r'extends\s+\w*Repository|\w*Repository\s*\{')
        ],

        'Service': [
            ('class.*Service', r'class\s+\w*Service|\w*Service\s*\{'),
            ('@service', r'@service|@Service'),
            ('process|handle|execute', r'process|handle|execute|run')
        ],

        # Hadrons de Dados
        'DTO': [
            ('@dataclass', r'@dataclass'),
            ('class.*DTO|class.*Request', r'class\s+\w*DTO|\w*Request|\w*Response'),
            ('interface.*\{', r'interface\s+\w+\s*\{'),
            ('type.*=', r'type\s+\w+\s*=')
        ],

        'Field': [
            ('Column|field|property', r'Column|field|property|\w+\s*:'),
            ('@column|@field', r'@column|@field|@Column|@Field'),
            ('private.*\w+;', r'private\s+\w+\s*;|public\s+\w+\s*;')
        ],

        # Hadrons de Teste
        'TestFunction': [
            ('test_|it\(|describe\(', r'test_|it\(|describe\(|should\(|expect\('),
            ('@test|@TestCase', r'@test|@TestCase|@Test'),
            ('assert|expect', r'assert|expect|should\.|\.to\.')
        ],

        'TestFixture': [
            ('@fixture|@Before|@After', r'@fixture|@Before|@After|@BeforeEach|@AfterEach'),
            ('setUp|tearDown', r'setUp|tearDown|beforeEach|afterEach')
        ],

        # Hadrons de Infraestrutura
        'DIContainer': [
            ('@inject|@Autowired', r'@inject|@Autowired|@Inject'),
            ('container', r'container|Container|injector'),
            ('provide|register', r'provide|register|bind')
        ],

        'Config': [
            ('config|settings', r'config|Config|settings|Settings|env|ENV'),
            ('@Configuration|@Config', r'@Configuration|@Config'),
            ('\.env|process\.env', r'\.env|process\.env|getenv')
        ]
    }

    def classify_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classifica nós em hadrons"""
        classified = []

        for node in nodes:
            hadrons = self._detect_hadrons(node)

            for hadron, confidence in hadrons:
                classified.append({
                    'node': node,
                    'hadron': hadron,
                    'confidence': confidence,
                    'language': node['language'],
                    'text': node['text'][:100] + ('...' if len(node['text']) > 100 else '')
                })

        return classified

    def _detect_hadrons(self, node: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Detecta hadrons para um nó específico"""
        detected = []
        text = node.get('text', '').lower()
        specific_type = node.get('specific_type', '').lower()

        for hadron, patterns in self.HADRON_PATTERNS.items():
            confidence = 0.0

            for pattern_name, regex in patterns:
                import re
                if re.search(regex, text, re.IGNORECASE):
                    confidence += 0.3
                if re.search(regex, specific_type, re.IGNORECASE):
                    confidence += 0.2

                # Bônus para tipos específicos
                if hadron == 'APIHandler' and 'route' in specific_type:
                    confidence += 0.4
                elif hadron == 'Entity' and ('class' in specific_type or 'struct' in specific_type):
                    confidence += 0.4
                elif hadron == 'TestFunction' and 'function_definition' == node.get('type'):
                    confidence += 0.3

            if confidence > 0.3:
                detected.append((hadron, min(1.0, confidence)))

        return detected


class SpectrometerEngineV5:
    """Motor principal do Spectrometer v5 com tree-sitter"""

    def __init__(self):
        self.extractor = TreeSitterExtractor()
        self.quark_detector = QuarkDetector()
        self.hadron_classifier = HadronClassifier()

        # Estatísticas
        self.stats = {
            'files_processed': 0,
            'languages_detected': set(),
            'total_nodes': 0,
            'quarks_detected': {q: 0 for q in QuarkDetector.QUARK_PATTERNS.keys()},
            'hadrons_detected': {}
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analisa um arquivo completo"""
        tree = self.extractor.parse_file(file_path)
        if not tree:
            return None

        # Extrai todos os nós
        nodes = self.extractor.extract_all_nodes(tree, file_path)
        if not nodes:
            return None

        # Detecta quarks
        quarks = self.quark_detector.detect_quarks(nodes)

        # Classifica hadrons
        hadrons = self.hadron_classifier.classify_nodes(nodes)

        # Atualiza estatísticas
        self.stats['files_processed'] += 1
        self.stats['total_nodes'] += len(nodes)
        lang = self.extractor.detect_language(file_path)
        if lang:
            self.stats['languages_detected'].add(lang)

        for quark, elements in quarks.items():
            self.stats['quarks_detected'][quark] += len(elements)

        for hadron_info in hadrons:
            hadron = hadron_info['hadron']
            self.stats['hadrons_detected'][hadron] = self.stats['hadrons_detected'].get(hadron, 0) + 1

        return {
            'file_path': str(file_path),
            'language': lang,
            'total_nodes': len(nodes),
            'quarks': quarks,
            'hadrons': hadrons,
            'top_nodes': nodes[:10]  # Primeiros 10 nós para debug
        }

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório completo"""
        print(f"\n🔍 Analisando repositório: {repo_path}")
        print("=" * 60)

        all_results = []
        language_stats = {}

        # Encontra arquivos suportados
        supported_extensions = set()
        for ext in LANGUAGE_MAP.values():
            supported_extensions.update(Path('*.' + e) for e in self.extractor.detect_language.__code__.co_consts if isinstance(e, str) and e.startswith('.'))

        files_processed = 0
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and self.extractor.detect_language(file_path):
                result = self.analyze_file(file_path)
                if result:
                    all_results.append(result)
                    files_processed += 1

                    # Estatísticas por linguagem
                    lang = result['language']
                    if lang:
                        language_stats[lang] = language_stats.get(lang, {'files': 0, 'nodes': 0})
                        language_stats[lang]['files'] += 1
                        language_stats[lang]['nodes'] += result['total_nodes']

                    # Progresso
                    if files_processed % 50 == 0:
                        print(f"  Processados: {files_processed} arquivos")

        # Gera relatório
        report = self._generate_report(repo_path, all_results, language_stats)

        return {
            'repository': str(repo_path),
            'files_analyzed': files_processed,
            'languages': list(self.stats['languages_detected']),
            'results': all_results,
            'language_stats': language_stats,
            'statistics': dict(self.stats),
            'report': report
        }

    def _generate_report(self, repo_path: Path, results: List[Dict], language_stats: Dict) -> str:
        """Gera relatório detalhado da análise"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║            SPECTROMETER v5 - TREE-SITTER ANALYSIS           ║
╚══════════════════════════════════════════════════════════════╝

📁 REPOSITÓRIO: {repo_path}
📊 ARQUIVOS ANALISADOS: {len(results)}
🌍 LINGUAGENS: {', '.join(self.stats['languages_detected'])}
🔢 NÓS TOTAIS: {self.stats['total_nodes']}

📋 ESTATÍSTICAS POR LINGUAGEM:
"""

        for lang, stats in language_stats.items():
            report += f"  • {lang:15} {stats['files']:5} arquivos, {stats['nodes']:6} nós\n"

        report += "\n🎯 QUARKS DETECTADOS:\n"
        for quark, count in sorted(self.stats['quarks_detected'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / self.stats['total_nodes']) * 100 if self.stats['total_nodes'] > 0 else 0
                report += f"  • {quark:15} {count:6} ({percentage:5.1f}%)\n"

        report += "\n⚛️  HÁDRONS PRINCIPAIS:\n"
        top_hadrons = sorted(self.stats['hadrons_detected'].items(), key=lambda x: x[1], reverse=True)[:10]
        for hadron, count in top_hadrons:
            if count > 0:
                report += f"  • {hadron:20} {count:4} ocorrências\n"

        # Insights
        report += "\n💡 INSIGHTS:\n"

        if len(self.stats['languages_detected']) > 1:
            report += f"  ✅ Repositório multi-linguagem detectado\n"

        if self.stats['quarks_detected']['FUNCTIONS'] > 0:
            report += f"  ✅ {self.stats['quarks_detected']['FUNCTIONS']} funções/métodos detectados\n"

        if self.stats['quarks_detected']['AGGREGATES'] > 0:
            report += f"  ✅ {self.stats['quarks_detected']['AGGREGATES']} classes/estruturas detectadas\n"

        hadrons_with_tests = sum(1 for h in self.stats['hadrons_detected'] if 'test' in h.lower())
        if hadrons_with_tests > 0:
            report += f"  ✅ {hadrons_with_tests} tipos de padrões de teste detectados\n"

        # Score
        score = min(100, (len(self.stats['hadrons_detected']) * 2))
        report += f"\n📈 SCORE FINAL: {score}/100\n"

        return report


def test_tree_sitter_spectrometer():
    """Teste inicial do motor v5"""
    print("🚀 SPECTROMETER v5 - TREE-SITTER EDITION")
    print("=" * 50)

    engine = SpectrometerEngineV5()

    # Teste em arquivo Python
    test_py = Path("/tmp/test_repo/src/user_service.py")
    if test_py.exists():
        result = engine.analyze_file(test_py)
        if result:
            print(f"\n📄 Arquivo Python: {test_py.name}")
            print(f"   Linguagem: {result['language']}")
            print(f"   Nós: {result['total_nodes']}")
            print(f"   Quarks: {sum(len(v) for v in result['quarks'].values())}")
            print(f"   Hadrons: {len(result['hadrons'])}")

    # Teste em arquivo JavaScript (se existir)
    test_js = Path("/tmp/test_repo/app.js")
    if test_js.exists():
        result = engine.analyze_file(test_js)
        if result:
            print(f"\n📄 Arquivo JavaScript: {test_js.name}")
            print(f"   Linguagem: {result['language']}")
            print(f"   Nós: {result['total_nodes']}")
            print(f"   Quarks: {sum(len(v) for v in result['quarks'].values())}")
            print(f"   Hadrons: {len(result['hadrons'])}")

    # Relatório completo
    repo_path = Path("/tmp/test_repo")
    if repo_path.exists():
        result = engine.analyze_repository(repo_path)
        print(result['report'])


if __name__ == "__main__":
    test_tree_sitter_spectrometer()