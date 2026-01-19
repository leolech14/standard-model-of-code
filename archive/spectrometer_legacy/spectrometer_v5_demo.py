#!/usr/bin/env python3
"""
SPECTROMETER v5 - DEMONSTRAÇÃO DO CONCEITO
Parser multi-linguagem universal sem dependências externas
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class CodeElement:
    """Representa um elemento de código universal"""
    type: str  # function, class, variable, etc
    language: str
    name: str
    text: str
    line: int
    confidence: float
    hadrons: List[str]

class UniversalLanguageDetector:
    """Detector universal de padrões multi-linguagem"""

    # Padrões universais que funcionam across-linguagem
    UNIVERSAL_PATTERNS = {
        # Funções/Métodos
        'function': {
            'python': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
            'javascript': r'^\s*(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)\s*=>|\([^)]*\)\s*\{))',
            'typescript': r'^\s*(?:function\s+(\w+)|(?:async\s+)?const\s+(\w+)\s*=\s*\([^)]*\)\s*=>)',
            'java': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{',
            'go': r'^\s*func\s+(?:\([^)]*\)\s+)?(\w+)\s*\([^)]*\)',
            'rust': r'^\s*(?:pub\s+)?(async\s+)?fn\s+(\w+)\s*\(',
            'c': r'^\s*(?:static\s+)?(?:inline\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*\{',
            'cpp': r'^\s*(?:virtual\s+)?(?:static\s+)?(?:inline\s+)?(?:\w+\s*::\s*)?(\w+)\s*\([^)]*\)',
            'csharp': r'^\s*(?:public|private|protected|internal)?\s*(?:static)?\s*(?:async)?\s*(?:\w+\s+)*(\w+)\s*\([^)]*)',
            'php': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*function\s+(\w+)\s*\(',
            'ruby': r'^\s*def\s+(\w+)',
            'kotlin': r'^\s*(?:fun\s+)(\w+)\s*\(',
        },

        # Classes/Estruturas
        'class': {
            'python': r'^\s*class\s+(\w+)',
            'javascript': r'^\s*class\s+(\w+)',
            'typescript': r'^\s*(?:abstract\s+)?class\s+(\w+)|(?:interface|type)\s+(\w+)',
            'java': r'^\s*(?:public\s+)?(?:abstract\s+)?class\s+(\w+)|(?:interface\s+(\w+))',
            'go': r'^\s*type\s+(\w+)\s+struct\s*\{',
            'rust': r'^\s*(?:pub\s+)?struct\s+(\w+)\s*\{|(?:pub\s+)?trait\s+(\w+)',
            'c': r'^\s*typedef\s+struct\s*\{[^}]*\}\s*(\w+);',
            'cpp': r'^\s*(?:class|struct)\s+(\w+)|(?:namespace\s+(\w+))',
            'csharp': r'^\s*(?:public|internal)?\s*(?:abstract\s+)?class\s+(\w+)|(?:interface\s+(\w+))',
            'php': r'^\s*(?:abstract\s+)?class\s+(\w+)|(?:interface\s+(\w+))',
            'kotlin': r'^\s*(?:sealed\s+)?(?:abstract\s+)?(?:open\s+)?class\s+(\w+)|(?:interface\s+(\w+))',
        },

        # Interfaces/Types
        'interface': {
            'typescript': r'^\s*interface\s+(\w+)',
            'java': r'^\s*interface\s+(\w+)',
            'csharp': r'^\s*interface\s+(\w+)',
            'go': r'^\s*type\s+(\w+)\s+interface\s*\{',
            'rust': r'^\s*trait\s+(\w+)',
            'kotlin': r'^\s*interface\s+(\w+)',
        },

        # Variáveis/Propriedades
        'variable': {
            'python': r'^\s*(\w+)\s*=',
            'javascript': r'^\s*(?:const|let|var)\s+(\w+)',
            'typescript': r'^\s*(?:const|let|var)\s+(\w+):',
            'java': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+\s+)+(\w+)(?:\s*=|\s*;)',
            'go': r'^\s*var\s+(\w+)|(?:\w+)\s*:=',
            'rust': r'^\s*let\s+(?:mut\s+)?(\w+)',
            'c': r'^\s*(?:static\s+)?(?:const\s+)?(?:\w+\s+)+(\w+)(?:\s*=|\s*;)',
            'cpp': r'^\s*(?:\w+\s*::\s*)?(\w+)(?:\s*=|\s*;)',
            'csharp': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:readonly)?\s*(?:\w+\s+)+(\w+)(?:\s*\{|\s*=|\s*;)',
            'php': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*\$(\w+)',
            'kotlin': r'^\s*(?:var|val)\s+(\w+)',
        },

        # Imports/Requires
        'import': {
            'python': r'^\s*import\s+(\w+)|from\s+(\w+)\s+import',
            'javascript': r'^\s*import\s+.*from\s+[\'"]([^\'"]+)|const\s+.*=\s*require\([\'"]([^\'"]+)',
            'typescript': r'^\s*import\s+.*from\s+[\'"]([^\'"]+)',
            'java': r'^\s*import\s+(?:static\s+)?([\w.]+)',
            'go': r'^\s*import\s+[\'"]([^\'"]+)[\'"]',
            'rust': r'^\s*use\s+([\w:]+)',
            'c': r'^\s*#include\s*[<"]([^>"]+)[>"]',
            'cpp': r'^\s*#include\s*[<"]([^>"]+)[>"]|^s*using\s+namespace\s+(\w+)',
            'csharp': r'^\s*using\s+([\w.]+)',
            'php': r'^\s*(?:use\s+|require_once\s+|include_once\s+)([^\s;]+)',
            'kotlin': r'^\s*import\s+([\w.]+)',
        },

        # Decorators/Annotations
        'decorator': {
            'python': r'^\s*@(\w+)',
            'javascript': r'^\s*@(\w+)',
            'typescript': r'^\s*@(\w+)',
            'java': r'^\s*@\w+(\([^)]*\))?',
            'csharp': r'^\s*\[\w+(\([^)]*\))?\]',
            'kotlin': r'^\s*@\w+',
        },

        # Comentários
        'comment': {
            'python': r'^\s*#.*',
            'javascript': r'^\s*//.*|^.*\*/.*',
            'typescript': r'^\s*//.*|^.*\*/.*',
            'java': r'^\s*//.*|^.*\*/.*',
            'go': r'^\s*//.*|^.*\*/.*',
            'rust': r'^\s*//.*|^.*\*/.*',
            'c': r'^\s*//.*|^.*\*/.*',
            'cpp': r'^\s*//.*|^.*\*/.*',
            'csharp': r'^\s*//.*|^.*\*/.*',
            'php': r'^\s*//.*|^.*\*/.*',
            'ruby': r'^\s*#.*',
            'kotlin': r'^\s*//.*|^.*\*/.*',
        }
    }

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detecta linguagem baseado na extensão"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
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

    def extract_elements(self, content: str, language: str) -> List[CodeElement]:
        """Extrai elementos do código usando padrões universais"""
        elements = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Para cada tipo de elemento
            for element_type, patterns in self.UNIVERSAL_PATTERNS.items():
                if language in patterns:
                    pattern = patterns[language]
                    match = re.search(pattern, line)

                    if match:
                        # Extrai nome do grupo de captura
                        name = ''
                        for group in match.groups():
                            if group:
                                name = group
                                break

                        # Classifica hadrons
                        hadrons = self._classify_hadrons(element_type, name, line, language)

                        element = CodeElement(
                            type=element_type,
                            language=language,
                            name=name or 'unnamed',
                            text=line[:100],
                            line=line_num,
                            confidence=0.9,
                            hadrons=hadrons
                        )
                        elements.append(element)
                        break  # Evita classificação múltipla

        return elements

    def _classify_hadrons(self, element_type: str, name: str, text: str, language: str) -> List[str]:
        """Classifica elemento em hadrons arquiteturais"""
        hadrons = []
        lower_name = name.lower()
        lower_text = text.lower()

        # Padrões universais cross-linguagem
        if element_type == 'function':
            # Command Handlers (escrita/mutação)
            if any(word in lower_name for word in ['save', 'create', 'update', 'delete', 'insert', 'post', 'put', 'remove', 'add']):
                hadrons.append('CommandHandler')

            # Query Handlers (leitura)
            elif any(word in lower_name for word in ['get', 'find', 'fetch', 'list', 'query', 'select', 'search', 'filter']):
                hadrons.append('QueryHandler')

            # Testes
            elif any(word in lower_name for word in ['test', 'spec', 'it_', 'should', 'describe', 'when']):
                hadrons.append('TestFunction')

            # Handlers genéricos
            elif any(word in lower_name for word in ['handle', 'process', 'execute', 'run', 'perform']):
                hadrons.append('Service')

            # Setup/Lifecycle
            elif any(word in lower_name for word in ['init', 'setup', 'start', 'stop', 'destroy', 'close']):
                hadrons.append('LifecycleHook')

        elif element_type == 'class' or element_type == 'interface':
            # Entidades/Models
            if any(word in lower_name for word in ['model', 'entity', 'domain', 'aggregate']):
                hadrons.append('Entity')

            # Repositories
            elif any(word in lower_name for word in ['repository', 'repo', 'dao', 'store']):
                hadrons.append('RepositoryImpl')

            # Services
            elif any(word in lower_name for word in ['service', 'handler', 'manager', 'processor']):
                hadrons.append('Service')

            # DTOs/Requests
            elif any(word in lower_name for word in ['dto', 'request', 'response', 'command', 'query', 'payload']):
                hadrons.append('DTO')

            # Controllers
            elif any(word in lower_name for word in ['controller', 'api', 'rest', 'resource']):
                hadrons.append('APIHandler')

            # Config
            elif any(word in lower_name for word in ['config', 'settings', 'options', 'properties']):
                hadrons.append('Config')

            # Testes
            elif any(word in lower_name for word in ['test', 'spec', 'mock', 'stub']):
                hadrons.append('TestCase')

        elif element_type == 'decorator':
            # API decorators
            if any(word in lower_text for word in ['route', 'endpoint', 'path', 'get', 'post', 'put', 'delete']):
                hadrons.append('APIHandler')

            # Test decorators
            elif any(word in lower_text for word in ['test', 'before', 'after', 'setup', 'teardown']):
                hadrons.append('TestFixture')

            # DI decorators
            elif any(word in lower_text for word in ['inject', 'autowired', 'component', 'service']):
                hadrons.append('DIContainer')

            # Data decorators
            elif any(word in lower_text for word in ['entity', 'table', 'column', 'field']):
                hadrons.append('Entity')

        elif element_type == 'variable':
            # Variáveis de configuração
            if any(word in lower_name for word in ['config', 'env', 'setting', 'option']):
                hadrons.append('Config')

            # Constantes
            if 'const' in lower_text or 'final' in lower_text or any(word in lower_name for word in ['max', 'min', 'default']):
                hadrons.append('Constant')

        return hadrons or ['Unknown']


class QuarkAnalyzer:
    """Analisador dos 12 Quarks Fundamentais"""

    # Mapeamento de elementos para quarks
    QUARK_MAPPING = {
        'EXECUTABLES': ['program', 'main', 'entry', 'app'],
        'FILES': ['import', 'require', 'include', 'use'],
        'MODULES': ['namespace', 'package', 'module'],
        'AGGREGATES': ['class', 'struct', 'interface', 'type'],
        'FUNCTIONS': ['function', 'method', 'fn', 'def'],
        'CONTROL': ['if', 'for', 'while', 'switch', 'match', 'try', 'catch'],
        'STATEMENTS': ['statement', 'declaration', 'assignment'],
        'EXPRESSIONS': ['expression', 'call', 'binary', 'unary'],
        'VARIABLES': ['variable', 'var', 'let', 'const', 'param'],
        'PRIMITIVES': ['string', 'number', 'boolean', 'null', 'undefined'],
        'BYTES': ['byte', 'bytes', 'binary', 'buffer'],
        'BITS': ['bit', 'bitwise', 'shift', 'and', 'or', 'xor']
    }

    def analyze_quarks(self, elements: List[CodeElement]) -> Dict[str, int]:
        """Analisa presença dos quarks fundamentais"""
        quark_counts = {quark: 0 for quark in self.QUARK_MAPPING.keys()}

        for element in elements:
            # Conta tipo base
            element_type = element.type.lower()
            element_name = element.name.lower()
            element_text = element.text.lower()

            # Mapeia para quarks
            for quark, keywords in self.QUARK_MAPPING.items():
                if any(keyword in element_type for keyword in keywords) or \
                   any(keyword in element_name for keyword in keywords) or \
                   any(keyword in element_text for keyword in keywords):
                    quark_counts[quark] += 1

        return quark_counts


class SpectrometerV5:
    """Motor principal do Spectrometer v5 - Multi-linguagem Universal"""

    def __init__(self):
        self.detector = UniversalLanguageDetector()
        self.quark_analyzer = QuarkAnalyzer()
        self.stats = {
            'files_processed': 0,
            'languages_detected': set(),
            'total_elements': 0,
            'hadron_counts': {},
            'quark_totals': {q: 0 for q in QuarkAnalyzer.QUARK_MAPPING.keys()}
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analisa um arquivo"""
        try:
            language = self.detector.detect_language(file_path)
            if not language:
                return None

            content = file_path.read_text(encoding='utf-8')
            elements = self.detector.extract_elements(content, language)

            # Analisa quarks
            quarks = self.quark_analyzer.analyze_quarks(elements)

            # Atualiza estatísticas
            self.stats['files_processed'] += 1
            self.stats['languages_detected'].add(language)
            self.stats['total_elements'] += len(elements)

            for hadron in ['Unknown'] + ['APIHandler', 'CommandHandler', 'QueryHandler', 'Entity', 'Service', 'RepositoryImpl', 'DTO', 'TestFunction']:
                count = sum(1 for e in elements if hadron in e.hadrons)
                if count > 0:
                    self.stats['hadron_counts'][hadron] = self.stats['hadron_counts'].get(hadron, 0) + count

            for quark, count in quarks.items():
                self.stats['quark_totals'][quark] += count

            return {
                'file_path': str(file_path),
                'language': language,
                'elements': elements,
                'quarks': quarks,
                'element_count': len(elements)
            }

        except Exception as e:
            print(f"Erro analisando {file_path}: {e}")
            return None

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório completo"""
        print(f"\n🔍 SPECTROMETER v5 - Analisando: {repo_path}")
        print("=" * 60)

        all_results = []
        language_stats = {}

        # Processa arquivos suportados
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and self.detector.detect_language(file_path):
                result = self.analyze_file(file_path)
                if result:
                    all_results.append(result)

                    # Estatísticas por linguagem
                    lang = result['language']
                    if lang not in language_stats:
                        language_stats[lang] = {'files': 0, 'elements': 0}
                    language_stats[lang]['files'] += 1
                    language_stats[lang]['elements'] += result['element_count']

        # Gera relatório
        report = self._generate_report(repo_path, language_stats)

        return {
            'repository': str(repo_path),
            'files_analyzed': len(all_results),
            'languages': list(self.stats['languages_detected']),
            'total_elements': self.stats['total_elements'],
            'language_stats': language_stats,
            'statistics': dict(self.stats),
            'report': report
        }

    def _generate_report(self, repo_path: Path, language_stats: Dict) -> str:
        """Gera relatório detalhado"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║         SPECTROMETER v5 - MULTI-LANGUAGE ANALYSIS         ║
╚════════════════════════════════════════════════════════════╝

📁 REPOSITÓRIO: {repo_path}
📊 ARQUIVOS ANALISADOS: {self.stats['files_processed']}
🌍 LINGUAGENS: {', '.join(self.stats['languages_detected'])}
🔢 ELEMENTOS TOTAIS: {self.stats['total_elements']}

📋 DISTRIBUIÇÃO POR LINGUAGEM:
"""

        for lang, stats in language_stats.items():
            report += f"  • {lang:12} {stats['files']:4} arquivos, {stats['elements']:5} elementos\n"

        report += "\n⚛️  QUARKS FUNDAMENTAIS DETECTADOS:\n"
        for quark, count in sorted(self.stats['quark_totals'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / self.stats['total_elements']) * 100 if self.stats['total_elements'] > 0 else 0
                report += f"  • {quark:15} {count:6} ({percentage:5.1f}%)\n"

        report += "\n🎯 PRINCIPAIS HÁDRONS:\n"
        top_hadrons = sorted(self.stats['hadron_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
        for hadron, count in top_hadrons:
            if count > 0:
                report += f"  • {hadron:20} {count:4} ocorrências\n"

        # Insights
        report += "\n💡 INSIGHTS:\n"

        multi_lang = len(self.stats['languages_detected']) > 1
        if multi_lang:
            report += f"  ✅ Repositório multi-linguagem ({len(self.stats['languages_detected'])} linguagens)\n"

        if self.stats['quark_totals']['FUNCTIONS'] > 0:
            report += f"  ✅ {self.stats['quark_totals']['FUNCTIONS']} funções/métodos detectados\n"

        if self.stats['quark_totals']['AGGREGATES'] > 0:
            report += f"  ✅ {self.stats['quark_totals']['AGGREGATES']} classes/estruturas detectadas\n"

        # Análise arquitetural
        api_handlers = self.stats['hadron_counts'].get('APIHandler', 0)
        services = self.stats['hadron_counts'].get('Service', 0)
        repositories = self.stats['hadron_counts'].get('RepositoryImpl', 0)
        entities = self.stats['hadron_counts'].get('Entity', 0)

        if api_handlers > 0 and services > 0:
            report += f"  ✅ Padrão de API/Services detectado\n"
        if repositories > 0 and entities > 0:
            report += f"  ✅ Padrão Repository/Entity detectado\n"

        tests = sum(v for k, v in self.stats['hadron_counts'].items() if 'test' in k.lower())
        if tests > 0:
            report += f"  ✅ {tests} elementos de teste detectados\n"

        # Score
        hadron_variety = len([h for h, c in self.stats['hadron_counts'].items() if c > 0 and h != 'Unknown'])
        score = min(100, (hadron_variety * 5) + (multi_lang * 10) + (len(self.stats['languages_detected']) * 5))

        report += f"\n📈 SCORE FINAL: {score}/100\n"

        return report


def demo_spectrometer_v5():
    """Demonstração do Spectrometer v5"""
    print("🚀 SPECTROMETER v5 - MULTI-LANGUAGE UNIVERSAL")
    print("=" * 60)

    engine = SpectrometerV5()

    # Teste no repositório
    repo_path = Path("/tmp/test_repo")
    if repo_path.exists():
        result = engine.analyze_repository(repo_path)
        print(result['report'])

    # Teste em arquivo JavaScript
    js_test = Path("/tmp/test.js")
    if js_test.exists():
        print(f"\n📄 Testando arquivo JavaScript: {js_test.name}")
        result = engine.analyze_file(js_test)
        if result:
            print(f"   Linguagem: {result['language']}")
            print(f"   Elementos: {result['element_count']}")
            print(f"   Quarks: {sum(result['quarks'].values())}")

            # Mostra alguns elementos
            for elem in result['elements'][:5]:
                hadrons_str = ', '.join(elem.hadrons) if elem.hadrons else 'None'
                print(f"     • {elem.type:10} {elem.name:20} → {hadrons_str}")


if __name__ == "__main__":
    demo_spectrometer_v5()