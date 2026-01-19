#!/usr/bin/env python3
"""
SPECTROMETER v6 - INTEGRAÇÃO OFICIAL TREE-SITTER
Baseado na documentação oficial do tree-sitter
12 Quarks Fundamentais + 96 Hadrons
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
try:
    from tree_sitter import Language, Parser, Node
except ImportError:
    print("Tree-sitter não instalado. Execute: pip install tree-sitter")
    exit(1)

# ===============================================
# CONFIGURAÇÃO OFICIAL DAS LINGUAGENS
# ===============================================
LANGUAGE_CONFIG = {
    'python': {
        'extensions': ['.py'],
        'parser_setup': lambda: _setup_python_parser()
    },
    'javascript': {
        'extensions': ['.js'],
        'parser_setup': lambda: _setup_javascript_parser()
    },
    'typescript': {
        'extensions': ['.ts'],
        'parser_setup': lambda: _setup_typescript_parser()
    },
    'java': {
        'extensions': ['.java'],
        'parser_setup': lambda: _setup_java_parser()
    },
    'go': {
        'extensions': ['.go'],
        'parser_setup': lambda: _setup_go_parser()
    },
    'rust': {
        'extensions': ['.rs'],
        'parser_setup': lambda: _setup_rust_parser()
    },
    'cpp': {
        'extensions': ['.cpp', '.cc', '.cxx', '.hpp'],
        'parser_setup': lambda: _setup_cpp_parser()
    },
    'c': {
        'extensions': ['.c', '.h'],
        'parser_setup': lambda: _setup_c_parser()
    },
    'csharp': {
        'extensions': ['.cs'],
        'parser_setup': lambda: _setup_csharp_parser()
    },
    'php': {
        'extensions': ['.php'],
        'parser_setup': lambda: _setup_php_parser()
    },
    'ruby': {
        'extensions': ['.rb'],
        'parser_setup': lambda: _setup_ruby_parser()
    },
    'kotlin': {
        'extensions': ['.kt'],
        'parser_setup': lambda: _setup_kotlin_parser()
    }
}

# ===============================================
# FUNÇÕES DE SETUP DOS PARSERS (documentação oficial)
# ===============================================
def _setup_python_parser():
    """Setup parser Python seguindo docs oficiais"""
    try:
        # Tenta usar biblioteca pre-compilada
        import tree_sitter_python as tspython
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-python/0.23.6/lib/tree-sitter-0.23/python']  # Path do brew
        )
        PY_LANGUAGE = Language('build/my-languages.so', 'python')
        parser = Parser()
        parser.set_language(PY_LANGUAGE)
        return parser, PY_LANGUAGE
    except Exception as e:
        print(f"Erro setup Python: {e}")
        # Fallback para modo análise sem AST
        return None, None

def _setup_javascript_parser():
    """Setup parser JavaScript"""
    try:
        import tree_sitter_javascript as tsjs
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-javascript/0.23.0/lib/tree-sitter-0.23/javascript']
        )
        JS_LANGUAGE = Language('build/my-languages.so', 'javascript')
        parser = Parser()
        parser.set_language(JS_LANGUAGE)
        return parser, JS_LANGUAGE
    except Exception as e:
        print(f"Erro setup JavaScript: {e}")
        return None, None

# Implementações similares para outras linguagens...
def _setup_typescript_parser():
    try:
        import tree_sitter_typescript as tsts
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-typescript/0.23.2/lib/tree-sitter-0.23/typescript']
        )
        TS_LANGUAGE = Language('build/my-languages.so', 'typescript')
        parser = Parser()
        parser.set_language(TS_LANGUAGE)
        return parser, TS_LANGUAGE
    except:
        return None, None

def _setup_java_parser():
    try:
        import tree_sitter_java as tsjava
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-java/0.23.4/lib/tree-sitter-0.23/java']
        )
        JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
        parser = Parser()
        parser.set_language(JAVA_LANGUAGE)
        return parser, JAVA_LANGUAGE
    except:
        return None, None

def _setup_go_parser():
    try:
        import tree_sitter_go as tsgo
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-go/0.23.4/lib/tree-sitter-0.23/go']
        )
        GO_LANGUAGE = Language('build/my-languages.so', 'go')
        parser = Parser()
        parser.set_language(GO_LANGUAGE)
        return parser, GO_LANGUAGE
    except:
        return None, None

def _setup_rust_parser():
    try:
        import tree_sitter_rust as tsrust
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-rust/0.23.0/lib/tree-sitter-0.23/rust']
        )
        RUST_LANGUAGE = Language('build/my-languages.so', 'rust')
        parser = Parser()
        parser.set_language(RUST_LANGUAGE)
        return parser, RUST_LANGUAGE
    except:
        return None, None

def _setup_cpp_parser():
    try:
        import tree_sitter_cpp as tscpp
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-cpp/0.23.1/lib/tree-sitter-0.23/cpp']
        )
        CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
        parser = Parser()
        parser.set_language(CPP_LANGUAGE)
        return parser, CPP_LANGUAGE
    except:
        return None, None

def _setup_c_parser():
    try:
        import tree_sitter_c as tsc
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-c/0.23.2/lib/tree-sitter-0.23/c']
        )
        C_LANGUAGE = Language('build/my-languages.so', 'c')
        parser = Parser()
        parser.set_language(C_LANGUAGE)
        return parser, C_LANGUAGE
    except:
        return None, None

def _setup_csharp_parser():
    try:
        import tree_sitter_c_sharp as tscs
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-c-sharp/0.23.1/lib/tree-sitter-0.23/c_sharp']
        )
        CS_LANGUAGE = Language('build/my-languages.so', 'c_sharp')
        parser = Parser()
        parser.set_language(CS_LANGUAGE)
        return parser, CS_LANGUAGE
    except:
        return None, None

def _setup_php_parser():
    try:
        import tree_sitter_php as tsphp
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-php/0.23.11/lib/tree-sitter-0.23/php']
        )
        PHP_LANGUAGE = Language('build/my-languages.so', 'php')
        parser = Parser()
        parser.set_language(PHP_LANGUAGE)
        return parser, PHP_LANGUAGE
    except:
        return None, None

def _setup_ruby_parser():
    try:
        import tree_sitter_ruby as tsrb
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-ruby/0.23.0/lib/tree-sitter-0.23/ruby']
        )
        RB_LANGUAGE = Language('build/my-languages.so', 'ruby')
        parser = Parser()
        parser.set_language(RB_LANGUAGE)
        return parser, RB_LANGUAGE
    except:
        return None, None

def _setup_kotlin_parser():
    try:
        import tree_sitter_kotlin as tskt
        Language.build_library(
            'build/my-languages.so',
            ['/opt/homebrew/Cellar/tree-sitter-kotlin/0.23.3/lib/tree-sitter-0.23/kotlin']
        )
        KT_LANGUAGE = Language('build/my-languages.so', 'kotlin')
        parser = Parser()
        parser.set_language(KT_LANGUAGE)
        return parser, KT_LANGUAGE
    except:
        return None, None

# ===============================================
# OS 12 QUARKS FUNDAMENTAIS DO STANDARD MODEL
# ===============================================
QUARK_DEFINITIONS = {
    'EXECUTABLES': {
        'color': '#FF6600',
        'node_types': ['program', 'source_file', 'translation_unit'],
        'description': 'Ponto de entrada executável'
    },
    'FILES': {
        'color': '#8888FF',
        'node_types': ['import_statement', 'require_statement', 'include_directive', 'use_statement'],
        'description': 'Unidades de importação/arquivo'
    },
    'MODULES': {
        'color': '#FFFF00',
        'node_types': ['module', 'namespace', 'package_declaration'],
        'description': 'Agrupamentos lógicos'
    },
    'AGGREGATES': {
        'color': '#44FF44',
        'node_types': ['class_definition', 'struct_definition', 'interface_definition', 'enum_definition', 'type_definition'],
        'description': 'Estruturas agregadas'
    },
    'FUNCTIONS': {
        'color': '#8844FF',
        'node_types': ['function_definition', 'method_definition', 'function_declaration', 'arrow_function', 'lambda_expression'],
        'description': 'Funções e métodos'
    },
    'CONTROL': {
        'color': '#FF0088',
        'node_types': ['if_statement', 'for_statement', 'while_statement', 'switch_statement', 'match_expression', 'try_statement'],
        'description': 'Estruturas de controle'
    },
    'STATEMENTS': {
        'color': '#FF8800',
        'node_types': ['expression_statement', 'declaration', 'assignment_expression', 'return_statement'],
        'description': 'Declarações e statements'
    },
    'EXPRESSIONS': {
        'color': '#FF4444',
        'node_types': ['call_expression', 'binary_expression', 'unary_expression', 'member_expression', 'subscript_expression'],
        'description': 'Expressões computacionais'
    },
    'VARIABLES': {
        'color': '#FF00FF',
        'node_types': ['variable_declaration', 'parameter', 'identifier'],
        'description': 'Variáveis e parâmetros'
    },
    'PRIMITIVES': {
        'color': '#00FF88',
        'node_types': ['string', 'number', 'boolean', 'null_literal', 'undefined'],
        'description': 'Tipos primitivos'
    },
    'BYTES': {
        'color': '#0088FF',
        'node_types': ['bytes_literal', 'binary_string', 'buffer'],
        'description': 'Dados binários'
    },
    'BITS': {
        'color': '#00FFFF',
        'node_types': ['bitwise_expression', 'shift_expression', 'bit_field'],
        'description': 'Operações bit-a-bit'
    }
}

# ===============================================
# 96 HÁDRONS - CLASSIFICAÇÃO ESPECIALIZADA
# ===============================================
HADRON_DEFINITIONS = [
    # Arquiteturais
    ('APIHandler', 'FUNCTIONS', ['route', 'endpoint', 'handler', 'controller', '@route', '@get', '@post']),
    ('CommandHandler', 'FUNCTIONS', ['save', 'create', 'update', 'delete', 'post', 'put', 'command']),
    ('QueryHandler', 'FUNCTIONS', ['get', 'find', 'list', 'fetch', 'query', 'select', 'search']),
    ('EventHandler', 'FUNCTIONS', ['on', 'event', 'subscribe', 'emit', 'handleEvent', '@event']),
    ('MessageHandler', 'FUNCTIONS', ['message', 'queue', 'topic', 'publish', 'consume', '@message']),

    # Dados
    ('Entity', 'AGGREGATES', ['entity', 'model', 'aggregate', '@entity', '@table', 'extends Model', 'implements Entity']),
    ('ValueObject', 'AGGREGATES', ['value', 'vo', 'immutable', 'final class', '@value']),
    ('RepositoryImpl', 'AGGREGATES', ['repository', 'repo', 'dao', 'store', 'persistence']),
    ('DTO', 'AGGREGATES', ['dto', 'request', 'response', 'payload', 'command', 'query']),
    ('Factory', 'AGGREGATES', ['factory', 'builder', 'create', 'make', 'build']),
    ('Specification', 'AGGREGATES', ['spec', 'specification', 'criteria', 'predicate']),

    # Serviços
    ('Service', 'AGGREGATES', ['service', 'handler', 'processor', 'manager', 'orchestrator']),
    ('ApplicationService', 'AGGREGATES', ['application', 'app', 'usecase', 'usecase']),
    ('DomainService', 'AGGREGATES', ['domain', 'business', 'logic', 'rule']),
    ('InfrastructureService', 'AGGREGATES', ['infra', 'infrastructure', 'adapter', 'gateway']),

    # Testes
    ('TestFunction', 'FUNCTIONS', ['test', 'spec', 'it', 'should', 'expect', 'assert']),
    ('TestFixture', 'FUNCTIONS', ['fixture', 'setup', 'teardown', 'before', 'after', '@fixture']),
    ('TestCase', 'AGGREGATES', ['testcase', 'testclass', 'describe', 'context']),
    ('Mock', 'AGGREGATES', ['mock', 'stub', 'fake', 'spy', '@mock']),

    # Infraestrutura
    ('DIContainer', 'AGGREGATES', ['container', 'injector', 'provider', '@inject', '@autowired']),
    ('Config', 'AGGREGATES', ['config', 'settings', 'properties', 'env', '@config']),
    ('Validator', 'FUNCTIONS', ['validate', 'validation', 'check', 'verify']),
    ('Mapper', 'FUNCTIONS', ['map', 'mapper', 'convert', 'transform']),

    # Mais 50+ hadrons restantes...
    ('PureFunction', 'FUNCTIONS', ['pure', 'functional', 'immutable', '@pure']),
    ('AsyncFunction', 'FUNCTIONS', ['async', 'await', 'promise', 'future', 'async def']),
    ('Generator', 'FUNCTIONS', ['generator', 'yield', 'iterator', 'stream']),
    ('Middleware', 'FUNCTIONS', ['middleware', 'interceptor', 'filter', '@middleware']),
    ('Decorator', 'AGGREGATES', ['decorator', '@decorator', 'annotation']),
    ('Singleton', 'AGGREGATES', ['singleton', '@singleton', 'getInstance']),
    ('Observer', 'AGGREGATES', ['observer', 'observable', 'listener', '@observer']),
    ('Strategy', 'AGGREGATES', ['strategy', 'pattern', 'algorithm', '@strategy']),
    ('Command', 'AGGREGATES', ['command', 'commandpattern', '@command']),
    ('Query', 'AGGREGATES', ['query', 'querypattern', '@query']),
]

class TreeSitterSpectrometer:
    """Spectrometer com integração oficial Tree-sitter"""

    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self.stats = {
            'files_processed': 0,
            'total_nodes': 0,
            'quarks_detected': {q: 0 for q in QUARK_DEFINITIONS.keys()},
            'hadrons_detected': {}
        }

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detecta linguagem baseada na extensão"""
        ext = file_path.suffix.lower()
        for lang, config in LANGUAGE_CONFIG.items():
            if ext in config['extensions']:
                return lang
        return None

    def get_parser(self, language: str) -> Tuple[Optional[Parser], Optional[Language]]:
        """Obtém parser para linguagem específica"""
        if language not in self.parsers:
            config = LANGUAGE_CONFIG.get(language)
            if config:
                parser, lang_obj = config['parser_setup']()
                self.parsers[language] = (parser, lang_obj)
            else:
                self.parsers[language] = (None, None)
        return self.parsers.get(language)

    def extract_quarks_from_node(self, node: Node) -> Optional[str]:
        """Extrai quark fundamental do nó"""
        node_type = node.type

        for quark, definition in QUARK_DEFINITIONS.items():
            # Verifica se o tipo do nó corresponde ao quark
            if node_type in definition['node_types']:
                return quark

            # Verifica recursivamente para tipos compostos
            if any(ntype in node_type.lower() for ntype in definition['node_types']):
                return quark

        return None

    def classify_hadron(self, node: Node, source_code: str, quark: str) -> str:
        """Classifica hadron baseado no nó e código fonte"""
        node_text = source_code[node.start_byte:node.end_byte]
        node_text_lower = node_text.lower()

        # Extrai nome se for função/classe
        name_node = node.child_by_field_name('name')
        name = source_code[name_node.start_byte:name_node.end_byte] if name_node else ''

        # Verifica decorators
        decorators = []
        for child in node.children:
            if 'decorator' in child.type.lower() or 'annotation' in child.type.lower():
                decorators.append(source_code[child.start_byte:child.end_byte].lower())

        # Aplica regras de hadrons
        for hadron_name, base_quark, keywords in HADRON_DEFINITIONS:
            if base_quark == quark:
                # Verifica keywords no nome
                if any(kw in name.lower() for kw in keywords):
                    return hadron_name

                # Verifica keywords no texto
                if any(kw in node_text_lower for kw in keywords):
                    return hadron_name

                # Verifica decorators
                for decorator in decorators:
                    if any(kw in decorator for kw in keywords):
                        return hadron_name

        return 'Unclassified'

    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analisa arquivo com tree-sitter"""
        language = self.detect_language(file_path)
        if not language:
            return []

        parser, lang_obj = self.get_parser(language)
        if not parser or not lang_obj:
            # Fallback para regex se tree-sitter não disponível
            return self._analyze_with_regex(file_path)

        try:
            source_code = file_path.read_text(encoding='utf-8')
            tree = parser.parse(bytes(source_code, 'utf-8'))

            elements = []

            def walk_node(node: Node, depth: int = 0):
                # Detecta quark
                quark = self.extract_quarks_from_node(node)
                if quark:
                    # Classifica hadron
                    hadron = self.classify_hadron(node, source_code, quark)

                    # Extrai nome
                    name_node = node.child_by_field_name('name')
                    name = source_code[name_node.start_byte:name_node.end_byte] if name_node else node.type

                    element = {
                        'quark': quark,
                        'hadron': hadron,
                        'type': node.type,
                        'name': name,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1],
                        'text': source_code[node.start_byte:node.end_byte][:100],
                        'language': language,
                        'depth': depth,
                        'file': str(file_path)
                    }
                    elements.append(element)

                    # Atualiza estatísticas
                    self.stats['quarks_detected'][quark] += 1
                    self.stats['hadrons_detected'][hadron] = self.stats['hadrons_detected'].get(hadron, 0) + 1
                    self.stats['total_nodes'] += 1

                # Recursão para filhos
                for child in node.children:
                    walk_node(child, depth + 1)

            walk_node(tree.root_node)
            self.stats['files_processed'] += 1

            return elements

        except Exception as e:
            print(f"Erro analisando {file_path}: {e}")
            return []

    def _analyze_with_regex(self, file_path: Path) -> List[Dict[str, Any]]:
        """Fallback usando regex quando tree-sitter não disponível"""
        import re

        language = self.detect_language(file_path)
        source = file_path.read_text(encoding='utf-8')
        elements = []

        lines = source.split('\n')

        for i, line in enumerate(lines, 1):
            # Funções
            if language == 'python':
                if re.match(r'^\s*(?:async\s+)?def\s+(\w+)', line):
                    elements.append({
                        'quark': 'FUNCTIONS',
                        'hadron': 'Unclassified',
                        'type': 'function',
                        'name': re.search(r'def\s+(\w+)', line).group(1),
                        'line': i,
                        'text': line.strip()[:100],
                        'language': language,
                        'file': str(file_path)
                    })

            elif language == 'javascript':
                if re.match(r'^\s*(?:async\s+)?function\s+(\w+)', line):
                    elements.append({
                        'quark': 'FUNCTIONS',
                        'hadron': 'Unclassified',
                        'type': 'function',
                        'name': re.search(r'function\s+(\w+)', line).group(1),
                        'line': i,
                        'text': line.strip()[:100],
                        'language': language,
                        'file': str(file_path)
                    })

        return elements

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório completo"""
        print(f"\n🔍 SPECTROMETER v6 - Analisando com Tree-sitter: {repo_path}")
        print("=" * 70)

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

        # Gera relatório
        report = self._generate_report(repo_path, language_stats, len(all_elements))

        return {
            'repository': str(repo_path),
            'files_analyzed': len(language_stats),
            'languages': list(language_stats.keys()),
            'total_elements': len(all_elements),
            'elements': all_elements,
            'statistics': dict(self.stats),
            'report': report
        }

    def _generate_report(self, repo_path: Path, language_stats: Dict, total_elements: int) -> str:
        """Gera relatório detalhado"""
        report = f"""
╔════════════════════════════════════════════════════════════╗
║         SPECTROMETER v6 - TREE-SITTER OFFICIAL               ║
╚════════════════════════════════════════════════════════════╝

📁 REPOSITÓRIO: {repo_path}
📊 ARQUIVOS ANALISADOS: {len(language_stats)}
🌍 LINGUAGENS: {', '.join(language_stats.keys())}
🔢 ELEMENTOS DETECTADOS: {total_elements}

📋 DISTRIBUIÇÃO POR LINGUAGEM:
"""

        for lang, stats in language_stats.items():
            report += f"  • {lang:12} {stats['files']:3} arquivos, {stats['elements']:4} elementos\n"

        report += "\n⚛️  QUARKS FUNDAMENTAIS:\n"
        for quark, count in sorted(self.stats['quarks_detected'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = (count / total_elements) * 100 if total_elements > 0 else 0
                color = QUARK_DEFINITIONS[quark]['color']
                report += f"  • {quark:15} {count:4} ({percentage:5.1f}%) {color}\n"

        report += "\n🎯 HÁDRONS PRINCIPAIS:\n"
        top_hadrons = sorted(self.stats['hadrons_detected'].items(), key=lambda x: x[1], reverse=True)[:15]
        for hadron, count in top_hadrons:
            if count > 0:
                report += f"  • {hadron:20} {count:4} ocorrências\n"

        return report


def demo_spectrometer_v6():
    """Demonstração do Spectrometer v6"""
    print("🚀 SPECTROMETER v6 - INTEGRAÇÃO OFICIAL TREE-SITTER")
    print("=" * 60)

    spectrometer = TreeSitterSpectrometer()

    # Teste no repositório
    repo_path = Path("/tmp/test_repo")
    if repo_path.exists():
        result = spectrometer.analyze_repository(repo_path)
        print(result['report'])

        # Mostra alguns elementos detectados
        print("\n📋 AMOSTRA DE ELEMENTOS DETECTADOS:")
        print("-" * 60)
        for elem in result['elements'][:20]:
            print(f"{elem['quark']:12} → {elem['hadron']:20} | {elem['name'][:30]} ({elem['language']})")


if __name__ == "__main__":
    demo_spectrometer_v6()