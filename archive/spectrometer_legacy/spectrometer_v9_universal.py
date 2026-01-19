#!/usr/bin/env python3
"""
SPECTROMETER V9 - UNIVERSAL VERSION
Funciona em QUALQUER versão Python (3.8+)
Prioridade: LibCST → AST → Regex (sem dependências externas problemáticas)
"""

import json
import time
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import statistics
import hashlib

# LibCST (Python-only, funciona em qualquer versão)
try:
    import libcst as cst
    LIBCST_AVAILABLE = True
except ImportError:
    LIBCST_AVAILABLE = False

@dataclass
class Quark:
    """Quark fundamental do Standard Model do Código"""
    type: str
    value: str
    line: int
    column: int
    confidence: float
    source: str  # libcst, ast, regex

@dataclass
class Hadron:
    """Hádron composto (padrão arquitetural)"""
    type: str
    name: str
    quarks: List[Quark]
    confidence: float
    haiku: Optional[str] = None
    valence_score: float = 1.0

class SpectrometerUniversal:
    """Parser universal sem dependências externas problemáticas"""

    def __init__(self):
        self.metrics = {
            'files_processed': 0,
            'total_quarks': 0,
            'total_hadrons': 0,
            'parser_usage': {'libcst': 0, 'ast': 0, 'regex': 0}
        }

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
        """Parseia arquivo com estratégia universal"""

        language = self.detect_language(file_path)
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Estratégia específica por linguagem
        if language == 'python':
            return self._parse_python(content)
        elif language in ['javascript', 'typescript']:
            return self._parse_javascript(content)
        elif language == 'java':
            return self._parse_java(content)
        else:
            return self._parse_generic(content, language)

    def _parse_python(self, content: str) -> List[Quark]:
        """Parse Python com múltiplas estratégias"""
        quarks = []

        # 1. Tenta LibCST (mais robusto, preserva formatting)
        if LIBCST_AVAILABLE:
            try:
                tree = cst.parse_module(content)

                class QuarkExtractor(cst.CSTVisitor):
                    def visit_FunctionDef(self, node):
                        quarks.append(Quark(
                            type='FUNCTIONS',
                            value=node.name.value,
                            line=node.position.start.line if node.position else 0,
                            column=node.position.start.column if node.position else 0,
                            confidence=0.95,
                            source='libcst'
                        ))

                    def visit_ClassDef(self, node):
                        quarks.append(Quark(
                            type='AGGREGATES',
                            value=node.name.value,
                            line=node.position.start.line if node.position else 0,
                            column=node.position.start.column if node.position else 0,
                            confidence=0.95,
                            source='libcst'
                        ))

                    def visit_Assign(self, node):
                        for target in node.targets:
                            if isinstance(target, cst.Name):
                                quarks.append(Quark(
                                    type='VARIABLES',
                                    value=target.value,
                                    line=target.position.start.line if target.position else 0,
                                    column=target.position.start.column if target.position else 0,
                                    confidence=0.90,
                                    source='libcst'
                                ))

                    def visit_Import(self, node):
                        for name_item in node.names:
                            if hasattr(name_item, 'name'):
                                quarks.append(Quark(
                                    type='MODULES',
                                    value=name_item.name.value,
                                    line=node.position.start.line if node.position else 0,
                                    column=node.position.start.column if node.position else 0,
                                    confidence=0.90,
                                    source='libcst'
                                ))

                    def visit_ImportFrom(self, node):
                        if node.module:
                            quarks.append(Quark(
                                type='MODULES',
                                value=node.module.value,
                                line=node.position.start.line if node.position else 0,
                                column=node.position.start.column if node.position else 0,
                                confidence=0.90,
                                source='libcst'
                            ))

                visitor = QuarkExtractor()
                tree.visit(visitor)

                self.metrics['parser_usage']['libcst'] += len([q for q in quarks if q.source == 'libcst'])

            except Exception:
                pass  # Fallback para AST

        # 2. Fallback para AST nativo (sempre funciona)
        if not quarks:
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

                self.metrics['parser_usage']['ast'] += len([q for q in quarks if q.source == 'ast'])

            except Exception:
                pass  # Fallback para regex

        # 3. Último recurso: Regex
        if not quarks:
            quarks = self._parse_regex_python(content)
            self.metrics['parser_usage']['regex'] += len(quarks)

        return quarks

    def _parse_javascript(self, content: str) -> List[Quark]:
        """Parse JavaScript/TypeScript"""
        quarks = []
        lines = content.split('\n')

        # Padrões JavaScript
        patterns = {
            'FUNCTIONS': [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\(',
                r'(\w+)\s*=>\s*{',
                r'async\s+function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*async\s*\('
            ],
            'AGGREGATES': [
                r'class\s+(\w+)',
                r'interface\s+(\w+)',
                r'type\s+(\w+)\s*=',
                r'export\s+class\s+(\w+)'
            ],
            'VARIABLES': [
                r'const\s+(\w+)\s*=',
                r'let\s+(\w+)\s*=',
                r'var\s+(\w+)\s='
            ],
            'MODULES': [
                r'import.*from\s+[\'"]([^\'"]+)[\'"]',
                r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
                r'export\s+default\s+(\w+)'
            ],
            'CONTROL': [
                r'if\s*\(',
                r'for\s*\(',
                r'while\s*\(',
                r'switch\s*\(',
                r'try\s*{'
            ]
        }

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            for quark_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        quarks.append(Quark(
                            type=quark_type,
                            value=value,
                            line=line_num,
                            column=line.find(value) + 1,
                            confidence=0.70,
                            source='regex'
                        ))

        return quarks

    def _parse_java(self, content: str) -> List[Quark]:
        """Parse Java"""
        quarks = []
        lines = content.split('\n')

        # Padrões Java
        patterns = {
            'FUNCTIONS': [
                r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
                r'void\s+(\w+)\s*\(',
                r'(?:public|private|protected)\s+class\s+(\w+)\s*\{',
                r'@\w+\s*(?:public|private|protected)?\s*\w+\s+(\w+)\s*\('
            ],
            'AGGREGATES': [
                r'(?:public\s+)?class\s+(\w+)',
                r'interface\s+(\w+)',
                r'enum\s+(\w+)'
            ],
            'VARIABLES': [
                r'(?:\w+\s+)+(\w+)\s*=',
                r'(?:\w+\s+)+(\w+)\s*;'
            ],
            'MODULES': [
                r'import\s+([^\s;]+);',
                r'package\s+([^;]+);'
            ]
        }

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            for quark_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        quarks.append(Quark(
                            type=quark_type,
                            value=value,
                            line=line_num,
                            column=line.find(value) + 1,
                            confidence=0.70,
                            source='regex'
                        ))

        return quarks

    def _parse_generic(self, content: str, language: str) -> List[Quark]:
        """Parse genérico para outras linguagens"""
        quarks = []
        lines = content.split('\n')

        # Padrões universais
        patterns = {
            'FUNCTIONS': [
                r'function\s+(\w+)\s*\(',
                r'def\s+(\w+)\s*\(',
                r'func\s+(\w+)\s*\(',
                r'(\w+)\s*\([^)]*\)\s*{'
            ],
            'AGGREGATES': [
                r'class\s+(\w+)',
                r'interface\s+(\w+)',
                r'struct\s+(\w+)'
            ],
            'VARIABLES': [
                r'(\w+)\s*=',
                r'var\s+(\w+)\s*=',
                r'let\s+(\w+)\s*=',
                r'const\s+(\w+)\s+='
            ],
            'CONTROL': [
                r'if\s*\(',
                r'for\s*\(',
                r'while\s*\(',
                r'switch\s*\('
            ]
        }

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            for quark_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        quarks.append(Quark(
                            type=quark_type,
                            value=value,
                            line=line_num,
                            column=line.find(value) + 1,
                            confidence=0.60,
                            source='regex'
                        ))

        return quarks

    def _parse_regex_python(self, content: str) -> List[Quark]:
        """Parse Python com regex (fallback final)"""
        quarks = []
        lines = content.split('\n')

        patterns = {
            'FUNCTIONS': [
                r'def\s+(\w+)\s*\(',
                r'async\s+def\s+(\w+)\s*\('
            ],
            'AGGREGATES': [
                r'class\s+(\w+)\s*:'
            ],
            'VARIABLES': [
                r'(\w+)\s*=',
                r'global\s+(\w+)'
            ],
            'MODULES': [
                r'import\s+(\w+)',
                r'from\s+(\w+)',
                r'from\s+\w+\s+import\s+(\w+)'
            ],
            'CONTROL': [
                r'if\s+.*:',
                r'for\s+\w+\s+in\s+.*:',
                r'while\s+.*:',
                r'try\s*:',
                r'except\s+.*:'
            ]
        }

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            for quark_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1) if match.groups() else match.group(0)
                        quarks.append(Quark(
                            type=quark_type,
                            value=value,
                            line=line_num,
                            column=line.find(value) + 1,
                            confidence=0.65,
                            source='regex'
                        ))

        return quarks

    def classify_hadrons(self, quarks: List[Quark]) -> List[Hadron]:
        """Classifica quarks em hádrons com regras otimizadas"""

        # Agrupa por elemento
        elements = {}
        for quark in quarks:
            if quark.type in ['FUNCTIONS', 'AGGREGATES']:
                key = quark.value
            else:
                key = f"{quark.line}_{quark.type}"

            if key not in elements:
                elements[key] = []
            elements[key].append(quark)

        hadrons = []

        for element_name, element_quarks in elements.items():
            # Determina tipo de hádron
            combined = ' '.join([q.value.lower() for q in element_quarks])

            # Regras de classificação refinadas
            if any(word in element_name.lower() for word in ['service', 'manager', 'controller']):
                hadron_type = 'Service'
            elif 'entity' in combined or 'model' in combined:
                hadron_type = 'Entity'
            elif any(word in combined for word in ['repository', 'dao']):
                hadron_type = 'RepositoryImpl'
            elif any(prefix in element_name.lower() for prefix in ['handle_', 'create_', 'save_', 'delete_']):
                hadron_type = 'CommandHandler'
            elif any(prefix in element_name.lower() for prefix in ['get_', 'find_', 'query_', 'list_']):
                hadron_type = 'QueryHandler'
            elif element_name.startswith('test_') or 'test' in combined:
                hadron_type = 'TestFunction'
            elif element_name in ['__init__', 'constructor']:
                hadron_type = 'Constructor'
            elif 'async' in combined or 'await' in combined:
                hadron_type = 'AsyncFunction'
            elif 'import' in combined or 'from' in combined:
                hadron_type = 'ImportStatement'
            elif any(word in combined for word in ['if', 'for', 'while', 'switch']):
                hadron_type = 'Control'
            else:
                hadron_type = 'PureFunction' if any(q.type == 'FUNCTIONS' for q in element_quarks) else 'Unclassified'

            # Calcula confiança
            confidence = statistics.mean([q.confidence for q in element_quarks]) if element_quarks else 0.5

            # Bonus para padrões claros
            if hadron_type in ['Service', 'Entity', 'RepositoryImpl', 'CommandHandler', 'QueryHandler']:
                confidence = min(0.95, confidence + 0.1)

            # Calcula valência
            valence = 1.0
            if hadron_type == 'Service' and not any(q.type == 'FUNCTIONS' for q in element_quarks):
                valence -= 0.3
            if hadron_type == 'TestFunction' and not any('assert' in q.value.lower() for q in element_quarks):
                valence -= 0.2

            hadrons.append(Hadron(
                type=hadron_type,
                name=element_name,
                quarks=element_quarks,
                confidence=confidence,
                valence_score=max(0.1, valence)
            ))

        return hadrons

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analisa um arquivo individual"""

        start_time = time.time()

        try:
            # 1. Parseia
            quarks = self.parse_file(file_path)

            # 2. Classifica
            hadrons = self.classify_hadrons(quarks)

            # 3. Métricas
            self.metrics['files_processed'] += 1
            self.metrics['total_quarks'] += len(quarks)
            self.metrics['total_hadrons'] += len(hadrons)

            duration = time.time() - start_time

            return {
                'file_path': str(file_path),
                'language': self.detect_language(file_path),
                'quarks': len(quarks),
                'hadrons': len(hadrons),
                'hadron_details': [{'type': h.type, 'name': h.name, 'confidence': h.confidence}
                                 for h in hadrons],
                'metrics': {
                    'avg_confidence': statistics.mean([h.confidence for h in hadrons]) if hadrons else 0,
                    'avg_valence': statistics.mean([h.valence_score for h in hadrons]) if hadrons else 1.0
                },
                'duration': duration,
                'timestamp': time.time()
            }

        except Exception as e:
            return {
                'file_path': str(file_path),
                'error': str(e),
                'quarks': 0,
                'hadrons': 0,
                'metrics': {'error': True}
            }

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório completo"""

        print(f"\n🔍 SPECTROMETER V9 - UNIVERSAL VERSION")
        print(f"📁 Analisando: {repo_path}")
        print(f"============================================================")

        # Encontra arquivos
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cs', '.php', '.rb', '.kt']
        files = []

        for ext in extensions:
            files.extend(repo_path.rglob(f'*{ext}'))

        # Limita para performance
        max_files = 50
        if len(files) > max_files:
            files = files[:max_files]
            print(f"  📊 Limitando a {max_files} arquivos")

        # Analisa cada arquivo
        results = []
        for file_path in files:
            print(f"  📄 {file_path.relative_to(repo_path)}")
            result = self.analyze_file(file_path)
            results.append(result)

        # Relatório final
        successful = [r for r in results if 'error' not in r]

        if successful:
            total_quarks = sum(r['quarks'] for r in successful)
            total_hadrons = sum(r['hadrons'] for r in successful)

            # Distribuição de hadrons
            hadron_types = {}
            for result in successful:
                for hadron in result['hadron_details']:
                    hadron_type = hadron['type']
                    hadron_types[hadron_type] = hadron_types.get(hadron_type, 0) + 1

            # Score V9
            avg_confidence = statistics.mean([r['metrics']['avg_confidence'] for r in successful])
            avg_valence = statistics.mean([r['metrics']['avg_valence'] for r in successful])
            hadron_diversity = len(hadron_types) / 10
            coverage = total_hadrons / max(total_quarks, 1)

            score_v9 = min(100, (hadron_diversity * 20 + avg_confidence * 30 +
                               avg_valence * 30 + coverage * 20))

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

            # Top hadrons
            print(f"\n🎯 Top Hadrons:")
            for hadron_type, count in sorted(hadron_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {hadron_type}: {count}")

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
            return {'error': 'No files analyzed successfully'}

# Teste
if __name__ == "__main__":
    spectrometer = SpectrometerUniversal()

    # Teste em arquivo exemplo
    test_repo = Path(__file__).parent
    result = spectrometer.analyze_repository(test_repo)

    print(f"\n✅ Análise concluída!")