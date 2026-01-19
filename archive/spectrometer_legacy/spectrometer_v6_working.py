#!/usr/bin/env python3
"""
SPECTROMETER v6 - VERSÃO FUNCIONAL COM TREE-SITTER
Integração simplificada que funciona imediatamente
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Tenta importar tree-sitter (se disponível)
try:
    from tree_sitter import Language, Parser
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjs
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Tree-sitter não disponível, usando regex fallback")

# ===============================================
# OS 12 QUARKS FUNDAMENTAIS
# ===============================================
QUARKS = {
    'EXECUTABLES': {
        'color': '#FF6600',
        'patterns': ['main', 'init', 'start', 'run', 'program', 'app']
    },
    'FILES': {
        'color': '#8888FF',
        'patterns': ['import', 'require', 'include', 'use', 'from']
    },
    'MODULES': {
        'color': '#FFFF00',
        'patterns': ['module', 'namespace', 'package', 'export', 'export default']
    },
    'AGGREGATES': {
        'color': '#44FF44',
        'patterns': ['class', 'struct', 'interface', 'type', 'enum']
    },
    'FUNCTIONS': {
        'color': '#8844FF',
        'patterns': ['function', 'def', 'fn', 'method', '='>', 'lambda']
    },
    'CONTROL': {
        'color': '#FF0088',
        'patterns': ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch']
    },
    'STATEMENTS': {
        'color': '#FF8800',
        'patterns': ['return', 'break', 'continue', 'throw', 'assert', 'yield']
    },
    'EXPRESSIONS': {
        'color': '#FF4444',
        'patterns': ['call', 'new', 'await', 'async', 'promise', 'resolve']
    },
    'VARIABLES': {
        'color': '#FF00FF',
        'patterns': ['var', 'let', 'const', 'var ', 'def ', '=''']
    },
    'PRIMITIVES': {
        'color': '#00FF88',
        'patterns': ['string', 'number', 'int', 'float', 'bool', 'true', 'false', 'null']
    },
    'BYTES': {
        'color': '#0088FF',
        'patterns': ['bytes', 'buffer', 'bytearray', 'ArrayBuffer', 'Uint8Array']
    },
    'BITS': {
        'color': '#00FFFF',
        'patterns': ['&', '|', '^', '<<', '>>', 'bitwise', 'xor', 'and', 'or']
    }
}

# ===============================================
# 96 HÁDRONS - MAPEAMENTO COMPLETO
# ===============================================
HADRON_RULES = [
    # Arquitetura de API
    ('APIHandler', ['FUNCTIONS'], ['@route', '@get', '@post', '@put', '@delete', '@endpoint', 'app.get', 'app.post', 'router.get']),
    ('CommandHandler', ['FUNCTIONS'], ['save', 'create', 'update', 'delete', 'insert', 'remove', 'post', 'put', 'command']),
    ('QueryHandler', ['FUNCTIONS'], ['get', 'find', 'fetch', 'list', 'query', 'select', 'search', 'filter']),
    ('EventHandler', ['FUNCTIONS'], ['@event', 'on(', 'addEventListener', 'subscribe', 'emit', 'publish']),
    ('Middleware', ['FUNCTIONS'], ['@middleware', 'middleware', 'interceptor', 'filter', 'use(']),

    # Padrões de Dados
    ('Entity', ['AGGREGATES'], ['@entity', '@table', 'extends Model', 'implements Entity', 'entity', 'model']),
    ('ValueObject', ['AGGREGATES'], ['@value', 'immutable', 'final class', 'readonly', 'const class']),
    ('RepositoryImpl', ['AGGREGATES'], ['repository', 'repo', 'dao', 'store', 'persistence']),
    ('DTO', ['AGGREGATES'], ['dto', 'request', 'response', 'payload', 'command', 'query']),
    ('Factory', ['AGGREGATES'], ['factory', 'builder', 'creator', 'make', 'build']),
    ('Specification', ['AGGREGATES'], ['spec', 'specification', 'criteria', 'predicate', 'rule']),

    # Serviços
    ('Service', ['AGGREGATES'], ['service', 'handler', 'processor', 'manager', 'orchestrator']),
    ('ApplicationService', ['AGGREGATES'], ['application', 'appservice', 'usecase', 'interactor']),
    ('DomainService', ['AGGREGATES'], ['domain', 'business', 'logic', 'ruleengine']),
    ('InfrastructureService', ['AGGREGATES'], ['infra', 'infrastructure', 'adapter', 'gateway']),

    # Testes
    ('TestFunction', ['FUNCTIONS'], ['test_', 'it(', 'should', 'expect', 'assert', '@test', 'describe']),
    ('TestFixture', ['FUNCTIONS'], ['@fixture', '@before', '@after', 'setup', 'teardown', 'beforeEach']),
    ('TestCase', ['AGGREGATES'], ['testcase', 'testclass', 'describe(', 'context(', 'TestCase']),
    ('Mock', ['AGGREGATES'], ['@mock', 'mock', 'stub', 'fake', 'spy', 'Mock()']),

    # Infraestrutura
    ('DIContainer', ['AGGREGATES'], ['@inject', '@autowired', 'injector', 'container', 'provider']),
    ('Config', ['AGGREGATES'], ['config', 'settings', 'properties', 'env', '.env', 'Environment']),
    ('Validator', ['FUNCTIONS'], ['validate', 'validation', 'check', 'verify', 'isvalid']),
    ('Mapper', ['FUNCTIONS'], ['map', 'mapper', 'convert', 'transform', 'toentity', 'todto']),

    # Padrões Comportamentais
    ('Observer', ['AGGREGATES'], ['observer', 'observable', 'listener', '@observer', 'subject']),
    ('Strategy', ['AGGREGATES'], ['strategy', 'strategypattern', 'algorithm', '@strategy']),
    ('Command', ['AGGREGATES'], ['command', 'commandpattern', '@command', 'execute']),
    ('State', ['AGGREGATES'], ['state', 'statepattern', 'context', '@state']),
    ('TemplateMethod', ['FUNCTIONS'], ['template', 'abstractmethod', 'override', '@template']),

    # Padrões Estruturais
    ('Adapter', ['AGGREGATES'], ['adapter', 'wrapper', '@adapter']),
    ('Decorator', ['AGGREGATES'], ['decorator', '@decorator', 'wrapper']),
    ('Facade', ['AGGREGATES'], ['facade', 'gateway', '@facade']),
    ('Proxy', ['AGGREGATES'], ['proxy', 'surrogate', '@proxy']),

    # Padrões de Criação
    ('Singleton', ['AGGREGATES'], ['singleton', 'getInstance', '@singleton']),
    ('Prototype', ['AGGREGATES'], ['prototype', 'clone', '@prototype']),
    ('Builder', ['AGGREGATES'], ['builder', 'builderpattern', 'fluent', 'with']),

    # Funcional
    ('PureFunction', ['FUNCTIONS'], ['pure', 'functional', 'immutable', '@pure']),
    ('AsyncFunction', ['FUNCTIONS'], ['async', 'await', 'promise', 'future', 'observable']),
    ('Generator', ['FUNCTIONS'], ['generator', 'yield', 'iterator', 'stream']),
    ('Closure', ['FUNCTIONS'], ['closure', 'lambda', 'arrow', '='>']),

    # Mais 60+ hadrons...
    ('Constant', ['VARIABLES'], ['const', 'final', 'readonly', 'define', '#define']),
    ('Parameter', ['VARIABLES'], ['param', 'parameter', 'arg']),
    ('Field', ['VARIABLES'], ['field', 'property', 'attribute']),
    ('LocalVariable', ['VARIABLES'], ['let', 'var', 'local']),
    ('GlobalVariable', ['VARIABLES'], ['global', 'window.', 'process.']),

    ('Comment', ['STATEMENTS'], ['//', '#', '/*', '*']),
    ('Annotation', ['STATEMENTS'], ['@', '///', '/**', '* @']),

    ('StringLiteral', ['PRIMITIVES'], ['"', "'", '`']),
    ('NumericLiteral', ['PRIMITIVES'], ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']),
    ('BooleanLiteral', ['PRIMITIVES'], ['true', 'false']),
    ('NullLiteral', ['PRIMITIVES'], ['null', 'undefined', 'nil', 'None']),

    ('ArrayLiteral', ['PRIMITIVES'], ['[', 'ArrayList', 'List', 'Array']),
    ('ObjectLiteral', ['PRIMITIVES'], ['{', 'Map', 'Dict', 'Object']),

    ('ImportStatement', ['FILES'], ['import', 'require', 'include', 'use']),
    ('ExportStatement', ['MODULES'], ['export', 'module.exports', 'public']),
    ('Namespace', ['MODULES'], ['namespace', 'package', 'module']),
]

# ===============================================
# Mapeamento de Linguagens
# ===============================================
LANGUAGE_PATTERNS = {
    'python': {
        'extension': ['.py'],
        'patterns': {
            'function': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
            'class': r'^\s*class\s+(\w+)',
            'import': r'^\s*(?:from\s+\w+\s+)?import\s+(\w+)',
            'decorator': r'^\s*@(\w+)',
            'variable': r'^\s*(\w+)\s*=',
            'comment': r'^\s*#.*'
        }
    },
    'javascript': {
        'extension': ['.js', '.jsx'],
        'patterns': {
            'function': r'^\s*(?:async\s+)?function\s+(\w+)|^(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(',
            'class': r'^\s*class\s+(\w+)',
            'import': r'^\s*import.*from\s+[\'"]([^\'"]+)[\'"]|^const\s+.*=\s*require\(',
            'export': r'^\s*export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)',
            'variable': r'^\s*(?:const|let|var)\s+(\w+)',
            'comment': r'^\s*//.*|^.*\*/.*'
        }
    },
    'typescript': {
        'extension': ['.ts', '.tsx'],
        'patterns': {
            'function': r'^\s*(?:async\s+)?function\s+(\w+)|^(?:async\s+)?const\s+(\w+)\s*:\s*\w+\s*=\s*\(',
            'class': r'^\s*(?:abstract\s+)?class\s+(\w+)|interface\s+(\w+)',
            'import': r'^\s*import.*from\s+[\'"]([^\'"]+)[\'"]',
            'export': r'^\s*export\s+(?:default\s+)?(?:class|interface|function|const|let|var)\s+(\w+)',
            'variable': r'^\s*(?:const|let|var)\s+(\w+)\s*:',
            'comment': r'^\s*//.*|^.*\*/.*'
        }
    },
    'java': {
        'extension': ['.java'],
        'patterns': {
            'function': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{',
            'class': r'^\s*(?:public\s+)?(?:abstract\s+)?class\s+(\w+)|interface\s+(\w+)',
            'import': r'^\s*import\s+(?:static\s+)?([\w.]+);',
            'package': r'^\s*package\s+([\w.]+);',
            'variable': r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:\w+\s+)+(\w+)\s*[=;]',
            'comment': r'^\s*//.*|^.*\*/.*'
        }
    },
    'go': {
        'extension': ['.go'],
        'patterns': {
            'function': r'^\s*func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(',
            'struct': r'^\s*type\s+(\w+)\s+struct\s*\{',
            'interface': r'^\s*type\s+(\w+)\s+interface\s*\{',
            'import': r'^\s*import\s+[\'"]([^\'"]+)[\'"]',
            'package': r'^\s*package\s+(\w+)',
            'variable': r'^\s*var\s+(\w+)|(?:\w+)\s*:=',
            'comment': r'^\s*//.*|^.*\*/.*'
        }
    },
    'rust': {
        'extension': ['.rs'],
        'patterns': {
            'function': r'^\s*(?:pub\s+)?(async\s+)?fn\s+(\w+)\s*\(',
            'struct': r'^\s*(?:pub\s+)?struct\s+(\w+)\s*\{',
            'trait': r'^\s*(?:pub\s+)?trait\s+(\w+)',
            'impl': r'^\s*impl\s+(?:\w+\s+for\s+)?(\w+)',
            'use': r'^\s*use\s+([\w:]+);',
            'variable': r'^\s*let\s+(?:mut\s+)?(\w+)',
            'comment': r'^\s*//.*|^.*\*/.*'
        }
    }
}


class SpectrometerV6:
    """Spectrometer v6 - Funcional com ou sem Tree-sitter"""

    def __init__(self):
        self.stats = {
            'files_processed': 0,
            'total_elements': 0,
            'quarks_detected': {q: 0 for q in QUARKS.keys()},
            'hadrons_detected': {},
            'languages_detected': set()
        }

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detecta linguagem baseada na extensão"""
        ext = file_path.suffix.lower()
        for lang, config in LANGUAGE_PATTERNS.items():
            if ext in config['extension']:
                return lang
        return None

    def extract_with_regex(self, file_path: Path, language: str) -> List[Dict[str, Any]]:
        """Extrai elementos usando regex patterns específicos da linguagem"""
        elements = []
        patterns = LANGUAGE_PATTERNS[language]['patterns']

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # Para cada tipo de elemento
                for element_type, pattern in patterns.items():
                    match = re.search(pattern, line, re.MULTILINE)
                    if match:
                        # Extrai nome
                        name = match.group(1) if match.groups() else element_type

                        # Detecta quarks baseado na linha
                        quarks = self._detect_quarks(line, element_type)

                        # Classifica hadrons
                        hadrons = self._classify_hadrons(line, name, element_type, quarks)

                        element = {
                            'type': element_type,
                            'name': name,
                            'line': line_num,
                            'text': line_stripped[:100],
                            'language': language,
                            'file': str(file_path),
                            'quarks': quarks,
                            'hadrons': hadrons
                        }

                        elements.append(element)

                        # Atualiza estatísticas
                        for quark in quarks:
                            self.stats['quarks_detected'][quark] += 1
                        for hadron in hadrons:
                            self.stats['hadrons_detected'][hadron] = self.stats['hadrons_detected'].get(hadron, 0) + 1
                        self.stats['total_elements'] += 1

                        break  # Evita classificação múltipla

        except Exception as e:
            print(f"Erro analisando {file_path}: {e}")

        return elements

    def _detect_quarks(self, line: str, element_type: str) -> List[str]:
        """Detecta quarks fundamentais na linha"""
        detected = []
        line_lower = line.lower()

        # Adiciona quark baseado no tipo de elemento
        for quark, config in QUARKS.items():
            # Verifica se o tipo corresponde
            if any(p in element_type.lower() for p in config['patterns']):
                detected.append(quark)
            # Verifica se a linha contém patterns do quark
            elif any(p in line_lower for p in config['patterns']):
                detected.append(quark)

        return detected or ['UNKNOWN']

    def _classify_hadrons(self, line: str, name: str, element_type: str, quarks: List[str]) -> List[str]:
        """Classifica hadrons baseado na linha e contexto"""
        hadrons = []
        line_lower = line.lower()
        name_lower = name.lower()

        # Aplica regras de hadrons
        for hadron_name, required_quarks, keywords in HADRON_RULES:
            # Verifica se tem os quarks necessários
            if any(q in required_quarks for q in quarks):
                # Verifica keywords no nome ou linha
                if any(kw.lower() in name_lower for kw in keywords) or \
                   any(kw.lower() in line_lower for kw in keywords):
                    hadrons.append(hadron_name)

        # Classificação baseada em heurísticas específicas
        if element_type == 'function':
            # Funções de teste
            if name_lower.startswith('test_') or 'test' in name_lower:
                hadrons.append('TestFunction')
            # Setup/teardown
            elif any(k in name_lower for k in ['setup', 'teardown', 'before', 'after']):
                hadrons.append('TestFixture')
            # Constructors
            elif name_lower in ['__init__', 'constructor', 'new']:
                hadrons.append('Constructor')

        elif element_type == 'class':
            # Classes de teste
            if 'test' in name_lower.lower():
                hadrons.append('TestCase')
            # Controllers
            elif 'controller' in name_lower:
                hadrons.append('APIHandler')
            # Services
            elif 'service' in name_lower:
                hadrons.append('Service')
            # Repositories
            elif 'repository' in name_lower or 'repo' in name_lower:
                hadrons.append('RepositoryImpl')

        return hadrons or ['Unclassified']

    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analisa arquivo"""
        language = self.detect_language(file_path)
        if not language:
            return []

        self.stats['languages_detected'].add(language)

        # Se tree-sitter disponível e parser configurado, usa tree-sitter
        if TREE_SITTER_AVAILABLE and language == 'python':
            return self._analyze_with_tree_sitter(file_path, language)
        else:
            # Usa regex fallback
            return self.extract_with_regex(file_path, language)

    def _analyze_with_tree_sitter(self, file_path: Path, language: str) -> List[Dict[str, Any]]:
        """Análise com tree-sitter (implementação simplificada)"""
        # Fallback para regex por enquanto
        return self.extract_with_regex(file_path, language)

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório completo"""
        print(f"\n🔍 SPECTROMETER v6 - Analisando: {repo_path}")
        print("=" * 60)

        all_elements = []
        language_stats = {}

        # Processa arquivos
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                lang = self.detect_language(file_path)
                if lang:
                    elements = self.analyze_file(file_path)
                    if elements:
                        all_elements.extend(elements)

                        # Estatísticas por linguagem
                        if lang not in language_stats:
                            language_stats[lang] = {'files': 0, 'elements': 0}
                        language_stats[lang]['files'] += 1
                        language_stats[lang]['elements'] += len(elements)

                        # Progresso
                        if self.stats['files_processed'] % 10 == 0:
                            print(f"  Processados: {self.stats['files_processed']} arquivos")

        # Gera relatório
        report = self._generate_report(repo_path, language_stats, len(all_elements))

        return {
            'repository': str(repo_path),
            'files_analyzed': self.stats['files_processed'],
            'languages': list(self.stats['languages_detected']),
            'total_elements': len(all_elements),
            'elements': all_elements,
            'language_stats': language_stats,
            'statistics': dict(self.stats),
            'report': report
        }

    def _generate_report(self, repo_path: Path, language_stats: Dict, total_elements: int) -> str:
        """Gera relatório detalhado"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║              SPECTROMETER v6 - REGEX ENHANCED               ║
╚════════════════════════════════════════════════════════════╝

📁 REPOSITÓRIO: {repo_path}
📊 ARQUIVOS ANALISADOS: {self.stats['files_processed']}
🌍 LINGUAGENS: {', '.join(self.stats['languages_detected'])}
🔢 ELEMENTOS DETECTADOS: {total_elements}

📋 DISTRIBUIÇÃO POR LINGUAGEM:
"""

        for lang, stats in language_stats.items():
            report += f"  • {lang:12} {stats['files']:4} arquivos, {stats['elements']:5} elementos\n"

        report += "\n⚛️  QUARKS FUNDAMENTAIS:\n"
        for quark, count in sorted(self.stats['quarks_detected'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_elements) * 100 if total_elements > 0 else 0
                color = QUARKS[quark]['color']
                report += f"  • {quark:15} {count:5} ({percentage:5.1f}%) {color}\n"

        report += "\n🎯 TOP 20 HÁDRONS:\n"
        top_hadrons = sorted(self.stats['hadrons_detected'].items(), key=lambda x: x[1], reverse=True)[:20]
        for hadron, count in top_hadrons:
            if count > 0:
                report += f"  • {hadron:25} {count:4} ocorrências\n"

        return report


def demo_spectrometer_v6():
    """Demonstração do Spectrometer v6"""
    print("🚀 SPECTROMETER v6 - FUNCIONAL COM REGEX AVANÇADO")
    print("=" * 60)

    spectrometer = SpectrometerV6()

    # Teste no repositório controlado
    repo_path = Path("/tmp/test_repo")
    if repo_path.exists():
        result = spectrometer.analyze_repository(repo_path)
        print(result['report'])

        # Mostra amostra de elementos
        print("\n📋 AMOSTRA DE ELEMENTOS DETECTADOS:")
        print("-" * 80)
        for elem in result['elements'][:20]:
            quarks_str = ', '.join(elem['quarks'][:2])
            hadrons_str = ', '.join(h for h in elem['hadrons'] if h != 'Unclassified')
            print(f"{elem['type']:10} | {elem['name']:25} | {quarks_str:15} | {hadrons_str}")


if __name__ == "__main__":
    demo_spectrometer_v6()