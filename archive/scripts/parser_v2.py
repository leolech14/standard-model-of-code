#!/usr/bin/env python3
"""
PARSER V2 - Melhorias baseadas nos resultados reais
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from parser_minimo import MinimalParser

class EnhancedParser(MinimalParser):
    """Parser v2 com base nos resultados reais"""

    def __init__(self):
        super().__init__()

        # Melhorias baseadas no que vimos no user_service.py

        # Enhanced patterns
        self.patterns.update({
            # Dataclass decorator
            'dataclass': {
                'pattern': r'^\s*@dataclass',
                'type': 'decorator',
                'hadron': 'dto'
            },

            # Property decorator
            'property': {
                'pattern': r'^\s*@property',
                'type': 'decorator',
                'hadron': 'property'
            },

            # Type hints detection
            'type_hint': {
                'pattern': r':\s*(\w+\s*->\s*\w+|\w+\s*:\s*\w+)',
                'type': 'annotation'
            },

            # SQLAlchemy/ORM patterns
            'column_def': {
                'pattern': r'\b(\w+)\s*=\s*Column\(',
                'type': 'column',
                'hadron': 'field'
            },

            # Method definitions
            'method': {
                'pattern': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(\s*self',
                'type': 'method',
                'examples': ['def save(self', 'async def handle(self']
            }
        })

        # Enhanced hadron mapping
        self.hadron_mapping.update({
            'value_object': ['dataclass', 'dto', 'schema'],
            'field': ['column', 'property', 'attribute'],
            'crud_operation': ['save', 'create', 'update', 'delete'],
            'initializer': ['__init__', 'initialize', 'setup'],
        })

    def _classify_hadron(self, element: Dict[str, Any]) -> str:
        """Classificação melhorada baseada em resultados reais"""

        # Se o pattern já tem hadron definido
        if 'hadron' in element:
            return element['hadron']

        # Classificação original do pai
        hadron = super()._classify_hadron(element)

        if hadron != 'unknown':
            return hadron

        # Classificação adicional
        content = element['content'].lower()
        name = element.get('function_name', element.get('class_name', ''), '').lower()

        # Data patterns
        if 'model' in name or 'entity' in name:
            return 'entity'
        elif 'service' in name or 'handler' in name:
            return 'service'
        elif 'config' in name or 'settings' in name:
            return 'config'
        elif 'util' in name or 'helper' in name:
            return 'utility'

        # Operation patterns
        elif any(op in content for op in ['save', 'create', 'update', 'delete']):
            return 'crud_operation'
        elif any(op in content for op in ['get', 'find', 'fetch', 'list']):
            return 'query_operation'
        elif 'return' in content and 'request' in content:
            return 'api_handler'

        # Method patterns
        if element['type'] == 'method':
            if '__init__' in name:
                return 'initializer'
            elif 'save' in name:
                return 'crud_operation'
            elif name.startswith('get') or name.startswith('find'):
                return 'query_operation'
            elif name.startswith('set'):
                return 'setter'

        return 'unknown'

    def parse_file_enhanced(self, file_path: Path) -> List[Dict[str, Any]]:
        """Parse com análises adicionais"""
        elements = super().parse_file(file_path)

        # Adiciona contexto aos elementos
        context = {
            'has_async': False,
            'has_dataclass': False,
            'has_db_ops': False,
            'is_web_api': False
        }

        # Analisa o arquivo para contexto
        try:
            content = file_path.read_text()
            context['has_async'] = 'async def' in content
            context['has_dataclass'] = '@dataclass' in content
            context['has_db_ops'] = any(op in content for op in ['.save(', '.get(', '.all('])
            context['is_web_api'] = any(pattern in content for pattern in ['@api_view', '@route', 'request', 'response'])

            # Adiciona contexto aos elementos
            for elem in elements:
                elem['context'] = context

        except:
            pass

        return elements

    def generate_detailed_report(self) -> str:
        """Gera relatório detalhado com insights"""
        report = super().generate_report()

        # Análises adicionais
        if self.stats['files_processed'] > 0:
            report += "\n🔍 ANÁLISE CONTEXTUAL:\n"

            total_elements = sum(self.stats['hadrons_found'].values())
            unknown = self.stats['hadrons_found'].get('unknown', 0)

            report += f"  • Taxa de classificação: {((total_elements - unknown) / total_elements * 100):.1f}%\n"

            # Hadrons mais comuns
            sorted_hadrons = sorted(self.stats['hadrons_found'].items(),
                                   key=lambda x: x[1], reverse=True)[:5]
            if sorted_hadrons:
                report += "\n  Top 5 Hadrons:\n"
                for hadron, count in sorted_hadrons:
                    report += f"    • {hadron}: {count}\n"

            # Insights
            report += "\n💡 INSIGHTS:\n"
            if self.stats['patterns_found'].get('decorator', 0) > 0:
                report += "  ✅ Decorators detectados - Python moderno em uso\n"
            if self.stats['patterns_found'].get('function', 0) > 0:
                report += "  ✅ Funções detectadas - Lógica de negócio presente\n"
            if self.stats['patterns_found'].get('class', 0) > 0:
                report += "  ✅ Classes detectadas - OOP em uso\n"

        return report


def test_enhanced_parser():
    """Testa o parser v2 com o arquivo real"""
    print("🚀 TESTANDO PARSER V2 - MELHORADO")
    print("="*50)

    parser = EnhancedParser()

    # Teste no arquivo real que já analisamos
    elements = parser.parse_file_enhanced(Path("/tmp/test_repo/src/user_service.py"))

    print(f"\n📁 ARQUIVO: user_service.py")
    print(f"✅ Elementos detectados: {len(elements)}")

    # Análise por tipo
    types = {}
    hadrons = {}

    for elem in elements:
        elem_type = elem['type']
        hadron = elem.get('hadron', 'unknown')

        types[elem_type] = types.get(elem_type, 0) + 1
        hadrons[hadron] = hadrons.get(hadron, 0) + 1

    print("\n📊 DISTRIBUIÇÃO POR TIPO:")
    for elem_type, count in types.items():
        print(f"  • {elem_type}: {count}")

    print("\n🎯 DISTRIBUIÇÃO POR HÁDRON:")
    for hadron, count in hadrons.items():
        if count > 0:
            print(f"  • {hadron}: {count}")

    # Verifica melhorias
    improvements = [
        ("@dataclass detectado", "value_object"),
        ("Repository classificada", "repository"),
        ("save() como crud_operation", "crud_operation"),
        ("find_all() como query_operation", "query_operation"),
    ]

    print("\n🔧 MELHORIAS IMPLEMENTADAS:")
    for desc, hadron in improvements:
        found = hadrons.get(hadron, 0) > 0
        status = "✅" if found else "❌"
        print(f"  {status} {desc}")

    print("\n" + parser.generate_detailed_report())


if __name__ == "__main__":
    test_enhanced_parser()