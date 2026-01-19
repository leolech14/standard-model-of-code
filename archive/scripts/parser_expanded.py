#!/usr/bin/env python3
"""
PARSER EXPANDIDO - Mais hadrons baseado no que aprendemos
"""

from parser_working import WorkingParser
import re
from pathlib import Path
from typing import List, Dict, Any

class ExpandedParser(WorkingParser):
    """Parser v3 - Mais hadrons e patterns detectados"""

    def __init__(self):
        super().__init__()

        # Adiciona mais patterns baseado nos testes reais
        self.patterns.update({
            # Test decorators
            'pytest_fixture': {
                'pattern': r'^\s*@pytest\.fixture',
                'type': 'decorator',
                'hadron': 'test_fixture'
            },

            # Type hints
            'type_hint': {
                'pattern': r':\s*(\w+)\s*->\s*\w+',
                'type': 'type_hint',
                'hadron': 'type_hint'
            },

            # SQLAlchemy patterns
            'column': {
                'pattern': r'(\w+)\s*=\s*Column\(',
                'type': 'column',
                'hadron': 'field'
            },

            # HTTP methods
            'http_method': {
                'pattern': r'\.(get|post|put|delete|patch)\s*\(',
                'type': 'http_method',
                'hadron': 'api_handler'
            },

            # Special methods
            'special_method': {
                'pattern': r'^\s*def\s+__(\w+)__\s*\(',
                'type': 'method',
                'hadron': 'lifecycle_method'
            }
        })

        # Hadron mapping expandido
        self.hadron_mapping.update({
            'test': {
                'test_case': 'test_case',
                'fixture': 'test_fixture',
                'assertion': 'assertion'
            },
            'lifecycle': {
                '__init__': 'constructor',
                '__str__': 'to_string',
                '__repr__': 'representation'
            },
            'data': {
                'column': 'field',
                'field': 'field',
                'attribute': 'field'
            }
        })

    def _classify_hadron(self, pattern_type: str, match, pattern_info: Dict) -> str:
        """Classificação expandida"""

        # Delega para o pai primeiro
        parent_hadron = super()._classify_hadron(pattern_type, match, pattern_info)
        if parent_hadron and parent_hadron != 'unknown':
            return parent_hadron

        # Nova classificação
        match_value = match.groups()[0] if match.groups() else ''

        if pattern_type == 'pytest_fixture':
            return 'test_fixture'

        elif pattern_type == 'special_method':
            special_methods = {
                '__init__': 'constructor',
                '__str__': 'to_string',
                '__repr__': 'representation',
                '__enter__': 'context_manager',
                '__exit__': 'context_manager',
                '__call__': 'callable'
            }
            return special_methods.get(match_value, 'lifecycle_method')

        elif pattern_type == 'column':
            return 'field'

        elif pattern_type == 'http_method':
            method = match.groups()[0]
            if method in ['get', 'list']:
                return 'query_handler'
            else:
                return 'command_handler'

        elif pattern_type == 'type_hint':
            return 'type_annotation'

        # Classificação por conteúdo
        content = match.string.lower()

        if pattern_type == 'function':
            func_name = match_value.lower()
            if 'test_' in func_name:
                return 'test_case'
            elif any(k in func_name for k in ['setup', 'teardown']):
                return 'test_lifecycle'
            elif any(k in func_name for k in ['assert_', 'expect']):
                return 'assertion'

        return 'unknown'


def test_expanded_parser():
    """Testa o parser expandido"""
    print("🚀 TESTANDO PARSER EXPANDIDO")
    print("="*50)

    parser = ExpandedParser()

    # Testes mais complexos
    advanced_tests = [
        ("Django com Type Hints", """
def get_user(request: HttpRequest) -> HttpResponse:
    return JsonResponse({})
        """),

        ("SQLAlchemy Models", """
class User(BaseModel):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
        """),

        ("Testes com Fixtures", """
@pytest.fixture
def repository():
    return UserRepository()
        """),

        ("Context Managers", """
class DatabaseManager:
    def __enter__(self):
        self.connection = connect()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        """),

        ("Async Operations", """
async def process_data(data: List[Dict]) -> List[Dict]:
    return [item for item in data if item['active']]
        """)
    ]

    print("\n🧪 TESTES AVANÇADOS:\n")

    for name, code in advanced_tests:
        print(f"\n🔍 {name}:")
        print("-" * 30)

        elements = parser._parse_content(code)

        if elements:
            for elem in elements:
                status = "✅"
                detail = f"→ {elem['hadron']}" if elem.get('hadron') != 'unknown' else f"({elem['type']})"
                print(f"  {status} {elem['content'][:50]} {detail}")
        else:
            print("  ❌ Nada detectado")

    # Teste no arquivo real
    print("\n📁 ANÁLISE DO REPOSITÓRIO COMPLETO:")
    print("-" * 50)

    parser = ExpandedParser()
    total_elements = []

    for file_path in ["/tmp/test_repo/src/user_service.py", "/tmp/test_repo/tests/test_user_service.py"]:
        path = Path(file_path)
        if path.exists():
            elems = parser.parse_file(path)
            total_elements.extend(elems)
            print(f"  📁 {path.name}: {len(elems)} elementos")

    print(f"\n📊 TOTAL: {len(total_elements)} elementos detectados")

    # Gera estatísticas por hadron
    hadrons = {}
    for elem in total_elements:
        if elem.get('hadron'):
            hadrons[elem['hadron']] = hadrons.get(elem['hadron'], 0) + 1

    print("\n🎯 DISTRIBUIÇÃO POR HÁDRON:")
    for hadron, count in sorted(hadrons.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {hadron:15} {count:3}")

    print("\n" + parser.generate_real_report())


if __name__ == "__main__":
    test_expanded_parser()