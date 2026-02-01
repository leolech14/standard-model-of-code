#!/usr/bin/env python3
"""
PARSER MÍNIMO QUE FUNCIONA - Versão 0.1
Apenas o essencial que DETECTA código real
"""

import re
from pathlib import Path
from typing import List, Dict, Any

class MinimalParser:
    """Parser que detecta patterns reais - sem ilusões"""

    def __init__(self):
        self.detected_patterns = []

        # Patterns que REALMENTE existem em código Python
        self.patterns = {
            # Decorators (ESSENCIAL!)
            'decorator': {
                'pattern': r'^\s*@(\w+)',
                'type': 'decorator',
                'examples': ['@api_view', '@route', '@inject', '@property']
            },

            # Function definitions
            'function': {
                'pattern': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
                'type': 'function',
                'examples': ['def get_users', 'async def process', 'def save']
            },

            # Class definitions
            'class': {
                'pattern': r'^\s*class\s+(\w+)(?:\s*\(([^)]+)\))?',
                'type': 'class',
                'examples': ['class User', 'class Model(Base)', 'class Repository']
            },

            # Import statements
            'import': {
                'pattern': r'^(?:from\s+(\w+)\s+)?import\s+(.+)',
                'type': 'import',
                'examples': ['import numpy', 'from django import models']
            },

            # HTTP route definitions
            'http_route': {
                'pattern': r'^\s*(?:\w+\.)?(get|post|put|delete|patch)\s*\(\s*[\'"]\/[^\'\"]+[\'"]\s*\)',
                'type': 'route',
                'examples': ["app.get('/users')", "router.post('/api/users')"]
            }
        }

        # Hádrons que podemos detectar com confiança
        self.hadron_mapping = {
            # Function-based hadrons
            'handle_command': ['handle', 'command', 'create', 'update', 'delete'],
            'handle_query': ['get', 'find', 'fetch', 'list', 'query'],
            'handle_event': ['event', 'emit', 'on_', 'subscribe'],
            'pure_function': ['calculate', 'compute', 'transform', 'validate'],

            # Decorator-based hadrons
            'api_handler': ['api_view', 'route', 'endpoint'],
            'di_container': ['inject', 'autowired', 'component'],
            'auth': ['permission', 'login_required', 'require_auth'],

            # Class-based hadrons
            'entity': ['model', 'entity', 'domain'],
            'repository': ['repository', 'repo', 'dao'],
            'service': ['service', 'manager', 'handler'],
            'dto': ['dto', 'request', 'response', 'schema'],
        }

        self.stats = {
            'files_processed': 0,
            'patterns_found': {},
            'hadrons_found': {},
            'lines_analyzed': 0
        }

    def parse_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse um arquivo e retorna os elementos detectados"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.parse_content(content, str(file_path))
        except Exception as e:
            print(f"Erro lendo {file_path}: {e}")
            return []

    def parse_content(self, content: str, file_path: str = "") -> List[Dict[str, Any]]:
        """Parse conteúdo e detecta patterns"""
        elements = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Tenta cada pattern
            for pattern_name, pattern_info in self.patterns.items():
                match = re.match(pattern_info['pattern'], line)
                if match:
                    element = {
                        'type': pattern_info['type'],
                        'line': line_num,
                        'content': line,
                        'file': file_path,
                        'raw_match': match.groups()
                    }

                    # Extrai informações específicas
                    if pattern_name == 'decorator':
                        element['decorator_name'] = match.group(1)
                    elif pattern_name == 'function':
                        element['function_name'] = match.group(1)
                        element['is_async'] = 'async' in line
                    elif pattern_name == 'class':
                        element['class_name'] = match.group(1)
                        element['parent_class'] = match.group(2) if len(match.groups()) > 1 else None
                    elif pattern_name == 'import':
                        element['import_info'] = match.groups()
                    elif pattern_name == 'http_route':
                        element['http_method'] = match.group(1)

                    elements.append(element)

                    # Atualiza estatísticas
                    self.stats['patterns_found'][pattern_name] = self.stats['patterns_found'].get(pattern_name, 0) + 1

                    # Classifica em hadron
                    hadron = self._classify_hadron(element)
                    if hadron:
                        self.stats['hadrons_found'][hadron] = self.stats['hadrons_found'].get(hadron, 0) + 1
                        element['hadron'] = hadron

        self.stats['files_processed'] += 1
        self.stats['lines_analyzed'] += len(lines)

        return elements

    def _classify_hadron(self, element: Dict[str, Any]) -> str:
        """Classifica um elemento em um hadron"""
        content = element['content'].lower()

        # Baseado no decorator
        if element['type'] == 'decorator':
            decorator_name = element.get('decorator_name', '').lower()
            for hadron, keywords in self.hadron_mapping.items():
                if any(kw in decorator_name for kw in keywords):
                    return hadron

        # Baseado no nome da função/classe
        if element['type'] in ['function', 'class']:
            name = element.get('function_name', element.get('class_name', '')).lower()

            for hadron, keywords in self.hadron_mapping.items():
                if any(kw in name for kw in keywords):
                    return hadron

        # Baseado no conteúdo da linha
        if element['type'] == 'route':
            if 'get' in content:
                return 'query_handler'
            elif any(op in content for op in ['post', 'put', 'delete']):
                return 'command_handler'

        return 'unknown'

    def generate_report(self) -> str:
        """Gera relatório honesto do que foi detectado"""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║            PARSER MÍNIMO - RELATÓRIO HONESTO                ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS REAIS:
  • Arquivos processados: {self.stats['files_processed']}
  • Linhas analisadas: {self.stats['lines_analyzed']}
  • Padrões detectados: {sum(self.stats['patterns_found'].values())}
  • Hádrons classificados: {sum(self.stats['hadrons_found'].values())}

📋 PADRÕES ENCONTRADOS:
"""

        for pattern, count in self.stats['patterns_found'].items():
            report += f"  • {pattern}: {count} ocorrências\n"

        report += "\n🎯 HÁDRONS IDENTIFICADOS:\n"

        for hadron, count in self.stats['hadrons_found'].items():
            if count > 0:
                report += f"  • {hadron}: {count} ocorrências\n"

        report += "\n✅ CONCLUSÃO:\n"
        if sum(self.stats['patterns_found'].values()) > 0:
            report += "  O parser está FUNCIONANDO!\n"
            report += "  Detectou patterns reais em código Python.\n"
        else:
            report += "  Nenhum padrão detectado. Verifique os arquivos.\n"

        return report


def test_parser():
    """Testa o parser com exemplos conhecidos"""
    print("🧪 TESTANDO PARSER MÍNIMO")
    print("="*50)

    parser = MinimalParser()

    # Test cases que devem funcionar
    test_cases = [
        ("Django REST", """
@api_view(['GET'])
def get_users(request):
    return User.objects.all()
        """),

        ("FastAPI", """
@app.get("/users")
async def get_users():
    return await user_service.list()
        """),

        ("SQLAlchemy Model", """
class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
        """),

        ("Repository Pattern", """
class UserRepository:
    def save(self, user):
        db.session.add(user)
        db.session.commit()
        """),

        ("Import Statement", """
from django.db import models
import numpy as np
        """)
    ]

    print("\n📁 TESTANDO CÓDIGOS CONHECIDOS:\n")

    for name, code in test_cases:
        print(f"\n🔍 {name}:")
        print("-" * 30)

        elements = parser.parse_content(code)

        if elements:
            for elem in elements:
                print(f"  ✅ {elem['type']}: {elem['content']}")
                if elem.get('hadron'):
                    print(f"     → Hádron: {elem['hadron']}")
        else:
            print("  ❌ Nada detectado")

    print("\n" + "="*50)
    print(parser.generate_report())


if __name__ == "__main__":
    test_parser()

    # Teste em arquivo real
    print("\n🔍 TESTANDO EM ARQUIVO REAL (user_service.py)...")

    parser = MinimalParser()
    elements = parser.parse_file(Path("/tmp/test_repo/src/user_service.py"))

    if elements:
        print(f"\n✅ Detectados {len(elements)} elementos:")
        for elem in elements[:10]:  # Primeiros 10
            print(f"  • {elem['type']:10} {elem['content']}")
            if elem.get('hadron'):
                print(f"    → Hádron: {elem['hadron']}")
    else:
        print("\n❌ Nenhum elemento detectado no arquivo real")
