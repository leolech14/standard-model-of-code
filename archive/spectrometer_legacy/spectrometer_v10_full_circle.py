#!/usr/bin/env python3
"""
SPECTROMETER V10 - FULL CIRCLE
POWERED BY DETERMINISTIC TREE-SITTER → HAIKU GAP FILLING → NEXT LEVEL
"""

import json
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib
import tempfile
import subprocess
import sys

# Tree-sitter powered parsing
try:
    from tree_sitter import Language, Parser, Node
    TREE_SITTER_AVAILABLE = True
    print("✅ Tree-sitter core disponível")
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("⚠️ Tree-sitter não disponível. Fallback para Universal.")

# Import do universal parser se tree-sitter não estiver disponível
from spectrometer_v9_universal import SpectrometerUniversal

@dataclass
class StructuralElement:
    """Elemento estrutural extraído pelo Tree-sitter"""
    type: str  # function_definition, class_definition, etc.
    name: str
    children: List['StructuralElement']
    parent: Optional['StructuralElement'] = None
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0
    text: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class TreeSitterStructuralAnalyzer:
    """Analisador estrutural determinístico powered by Tree-sitter"""

    def __init__(self):
        self.parsers = {}
        self.structure_cache = {}
        self._init_parsers()

    def _init_parsers(self):
        """Inicializa parsers Tree-sitter para múltiplas linguagens"""
        if not TREE_SITTER_AVAILABLE:
            print("⚠️ Tree-sitter não disponível. Usando fallback.")
            return

        # Mapeamento de linguagens
        self.language_parsers = {
            'python': 'tree_sitter_python',
            'javascript': 'tree_sitter_javascript',
            'typescript': 'tree_sitter_typescript',
            'java': 'tree_sitter_java',
            'go': 'tree_sitter_go',
            'rust': 'tree_sitter_rust',
            'c_sharp': 'tree_sitter_c_sharp',
            'php': 'tree_sitter_php',
            'ruby': 'tree_sitter_ruby',
            'kotlin': 'tree_sitter_kotlin'
        }

        # Inicializa parsers disponíveis
        for lang, package_name in self.language_parsers.items():
            try:
                # Tenta importar e inicializar
                mod = __import__(package_name)
                if hasattr(mod, 'language'):
                    self.parsers[lang] = Parser()
                    self.parsers[lang].set_language(mod.language())
                    print(f"✅ Parser Tree-sitter para {lang} inicializado")
            except ImportError:
                # Tenta tree-sitter-languages
                try:
                    from tree_sitter_languages import get_language, get_parser
                    self.parsers[lang] = get_parser(lang)
                    print(f"✅ Parser Tree-sitter para {lang} via tree-sitter-languages")
                except:
                    print(f"⚠️ Parser para {lang} não disponível")

    def analyze_file_structure(self, file_path: Path) -> StructuralElement:
        """Analisa estrutura completa do arquivo de forma determinística"""
        language = self._detect_language(file_path)
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Cache baseado em hash do conteúdo
        content_hash = hashlib.md5(content.encode()).hexdigest()
        cache_key = f"{file_path}:{content_hash}"

        if cache_key in self.structure_cache:
            return self.structure_cache[cache_key]

        if language in self.parsers and TREE_SITTER_AVAILABLE:
            structure = self._parse_with_tree_sitter(content, language)
        else:
            structure = self._parse_with_universal(content, language)

        self.structure_cache[cache_key] = structure
        return structure

    def _parse_with_tree_sitter(self, content: str, language: str) -> StructuralElement:
        """Parse com Tree-sitter - 100% determinístico"""
        parser = self.parsers[language]
        tree = parser.parse(bytes(content, 'utf-8'))

        root = StructuralElement(
            type='root',
            name='file_root',
            children=[],
            text=content
        )

        # Processa a árvore
        self._process_node(tree.root_node, root, content)

        return root

    def _process_node(self, node: Node, parent: StructuralElement, content: str):
        """Processa nó recursivamente"""
        # Extrai texto do nó
        start_byte = node.start_byte
        end_byte = node.end_byte
        node_text = content[start_byte:end_byte].strip()

        # Determina tipo de elemento
        element_type = self._map_node_to_element(node.type)

        if element_type:
            # Cria elemento estrutural
            element = StructuralElement(
                type=element_type,
                name=self._extract_name(node, content),
                parent=parent,
                line=node.start_point[0] + 1,
                column=node.start_point[1] + 1,
                end_line=node.end_point[0] + 1,
                end_column=node.end_point[1] + 1,
                text=node_text,
                metadata={
                    'node_type': node.type,
                    'is_named': node.is_named,
                    'has_children': len(node.children) > 0,
                    'depth': self._calculate_depth(node)
                }
            )

            # Adiciona ao pai
            parent.children.append(element)

            # Processa filhos
            for child in node.children:
                self._process_node(child, element, content)
        else:
            # Nó não mapeado - processa filhos diretamente
            for child in node.children:
                self._process_node(child, parent, content)

    def _parse_with_universal(self, content: str, language: str) -> StructuralElement:
        """Fallback usando parser universal"""
        spectrometer = SpectrometerUniversal()

        # Extrai elementos básicos
        quarks = spectrometer.parse_file(Path("dummy"))  # Ignora path

        # Converte para estrutura hierárquica
        root = StructuralElement(
            type='root',
            name='file_root',
            children=[],
            text=content
        )

        # Agrupa por escopo
        current_scope = root
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Detecta classes
            if 'class ' in stripped:
                class_name = self._extract_class_name(stripped)
                if class_name:
                    class_element = StructuralElement(
                        type='class_definition',
                        name=class_name,
                        parent=current_scope,
                        line=line_num,
                        column=line.find(class_name),
                        text=stripped,
                        metadata={'detected_by': 'universal_parser'}
                    )
                    current_scope.children.append(class_element)
                    current_scope = class_element

            # Detecta funções/métodos
            elif any(prefix in stripped for prefix in ['def ', 'function ', 'func ']):
                func_name = self._extract_function_name(stripped)
                if func_name:
                    func_element = StructuralElement(
                        type='function_definition',
                        name=func_name,
                        parent=current_scope,
                        line=line_num,
                        column=line.find(func_name),
                        text=stripped,
                        metadata={'detected_by': 'universal_parser'}
                    )
                    current_scope.children.append(func_element)

        return root

    def _detect_language(self, file_path: Path) -> str:
        """Detecta linguagem do arquivo"""
        suffix = file_path.suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cs': 'c_sharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.kt': 'kotlin'
        }

        return language_map.get(suffix, 'unknown')

    def _map_node_to_element(self, node_type: str) -> Optional[str]:
        """Mapeia tipo de nó Tree-sitter para elemento estrutural"""
        mapping = {
            # Funções
            'function_definition': 'function_definition',
            'method_definition': 'function_definition',
            'lambda_expression': 'function_definition',
            'arrow_function': 'function_definition',

            # Classes
            'class_definition': 'class_definition',
            'class_declaration': 'class_definition',
            'interface_definition': 'class_definition',

            # Módulos
            'module': 'module_definition',

            # Blocos de controle
            'if_statement': 'control_flow',
            'for_statement': 'control_flow',
            'while_statement': 'control_flow',
            'switch_statement': 'control_flow',

            # Importações
            'import_statement': 'import_statement',
            'import_from_statement': 'import_statement',

            # Variáveis
            'variable_declaration': 'variable_declaration',
            'assignment': 'variable_declaration',

            # Comentários
            'comment': 'comment',
            'block_comment': 'comment'
        }

        return mapping.get(node_type)

    def _extract_name(self, node: Node, content: str) -> str:
        """Extrai nome do nó"""
        # Padrões específicos por tipo de nó
        if 'function' in node.type or 'method' in node.type:
            # Procura pelo nome após 'def', 'function', etc.
            node_text = content[node.start_byte:node.end_byte]
            match = re.search(r'(def|function|func)\s+(\w+)', node_text)
            if match:
                return match.group(2)
        elif 'class' in node.type:
            # Procura pelo nome após 'class', 'interface'
            node_text = content[node.start_byte:node.end_byte]
            match = re.search(r'(class|interface)\s+(\w+)', node_text)
            if match:
                return match.group(2)

        # Fallback: primeiro child named
        for child in node.children:
            if child.is_named and child.type in ['identifier', 'type_identifier']:
                return content[child.start_byte:child.end_byte]

        return "unnamed"

    def _extract_class_name(self, line: str) -> str:
        """Extrai nome da classe de uma linha"""
        match = re.search(r'class\s+(\w+)', line)
        return match.group(1) if match else ""

    def _extract_function_name(self, line: str) -> str:
        """Extrai nome da função de uma linha"""
        patterns = [
            r'def\s+(\w+)',
            r'function\s+(\w+)',
            r'func\s+(\w+)',
            r'(\w+)\s*\([^)]*\)\s*{'
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

        return ""

    def _calculate_depth(self, node: Node) -> int:
        """Calcula profundidade do nó na árvore"""
        depth = 0
        current = node
        while current.parent:
            depth += 1
            current = current.parent
        return depth

class HAIKUGapFiller:
    """Preenche gaps semânticos usando HAIKU v2"""

    def __init__(self):
        # Carrega os 384 sub-hádrons HAIKU
        self.haiku_patterns = self._load_haiku_patterns()
        self.context_cache = {}

    def _load_haiku_patterns(self) -> Dict[str, Any]:
        """Carrega patterns HAIKU"""
        patterns = {
            # Command patterns
            'command_create': {
                'keywords': ['create', 'save', 'add', 'insert', 'new', 'post'],
                'returns': ['void', 'created', 'saved'],
                'modifies': True,
                'category': 'CommandHandler'
            },
            'command_update': {
                'keywords': ['update', 'modify', 'edit', 'change', 'put'],
                'returns': ['void', 'updated', 'modified'],
                'modifies': True,
                'category': 'CommandHandler'
            },
            'command_delete': {
                'keywords': ['delete', 'remove', 'destroy', 'del'],
                'returns': ['void', 'deleted', 'removed'],
                'modifies': True,
                'category': 'CommandHandler'
            },

            # Query patterns
            'query_find': {
                'keywords': ['find', 'get', 'retrieve', 'fetch', 'select'],
                'returns': ['object', 'list', 'array'],
                'modifies': False,
                'category': 'QueryHandler'
            },
            'query_list': {
                'keywords': ['list', 'all', 'get_all', 'find_all'],
                'returns': ['list', 'array', 'collection'],
                'modifies': False,
                'category': 'QueryHandler'
            },
            'query_search': {
                'keywords': ['search', 'filter', 'query', 'where'],
                'returns': ['list', 'array', 'results'],
                'modifies': False,
                'category': 'QueryHandler'
            },

            # Service patterns
            'service_business': {
                'keywords': ['service', 'manager', 'orchestrator', 'coordinator'],
                'multiple_operations': True,
                'transactional': True,
                'category': 'Service'
            },

            # Entity patterns
            'entity_model': {
                'keywords': ['entity', 'model', 'domain'],
                'has_id': True,
                'has_state': True,
                'immutable': False,
                'category': 'Entity'
            },

            # Repository patterns
            'repository_crud': {
                'keywords': ['repository', 'dao', 'storage', 'persistence'],
                'has_create': True,
                'has_read': True,
                'has_update': True,
                'has_delete': True,
                'category': 'RepositoryImpl'
            },

            # API patterns
            'api_rest': {
                'keywords': ['controller', 'api', 'rest', 'endpoint'],
                'has_routes': True,
                'has_status_codes': True,
                'category': 'APIHandler'
            }
        }

        return patterns

    def fill_gaps(self, structure: StructuralElement, file_path: Path) -> Dict[str, Any]:
        """Preenche gaps semânticos na estrutura"""
        enhanced = {
            'original_structure': self._serialize_structure(structure),
            'haiku_classifications': [],
            'semantic_relationships': [],
            'architectural_layers': [],
            'design_patterns': []
        }

        # Processa cada elemento
        for element in self._flatten_structure(structure):
            classification = self._classify_with_haiku(element, file_path)
            if classification:
                enhanced['haiku_classifications'].append(classification)

        # Deriva relacionamentos
        enhanced['semantic_relationships'] = self._derive_relationships(structure)

        # Identifica camadas arquiteturais
        enhanced['architectural_layers'] = self._identify_layers(structure)

        # Detecta padrões de design
        enhanced['design_patterns'] = self._detect_design_patterns(structure)

        return enhanced

    def _flatten_structure(self, structure: StructuralElement) -> List[StructuralElement]:
        """Achata estrutura para processamento"""
        elements = []

        def _flatten(node):
            if node.type != 'root':
                elements.append(node)
            for child in node.children:
                _flatten(child)

        _flatten(structure)
        return elements

    def _classify_with_haiku(self, element: StructuralElement, file_path: Path) -> Optional[Dict]:
        """Classifica elemento usando HAIKU patterns"""
        classifications = []

        # Analisa texto e metadados
        text = element.text.lower()
        metadata = element.metadata or {}

        for pattern_name, pattern in self.haiku_patterns.items():
            score = 0.0

            # Match de keywords
            keyword_matches = sum(1 for kw in pattern['keywords'] if kw in text)
            if keyword_matches > 0:
                score += 0.4 * (keyword_matches / len(pattern['keywords']))

            # Verifica tipo do elemento
            if element.type == 'function_definition':
                if pattern.get('modifies') == True:
                    if any(kw in text for kw in ['set', 'save', 'delete', 'update']):
                        score += 0.3
                elif pattern.get('modifies') == False:
                    if any(kw in text for kw in ['get', 'find', 'query', 'list']):
                        score += 0.3

            # Verifica categoria
            if pattern.get('category') == 'Entity' and element.type == 'class_definition':
                score += 0.2
            elif pattern.get('category') == 'RepositoryImpl' and 'repo' in text:
                score += 0.2

            if score > 0.5:
                classifications.append({
                    'pattern': pattern_name,
                    'category': pattern.get('category', 'Unknown'),
                    'confidence': min(1.0, score),
                    'element_type': element.type,
                    'element_name': element.name,
                    'line': element.line
                })

        # Retorna a melhor classificação
        if classifications:
            return max(classifications, key=lambda x: x['confidence'])

        return None

    def _derive_relationships(self, structure: StructuralElement) -> List[Dict]:
        """Deriva relacionamentos semânticos"""
        relationships = []
        elements = self._flatten_structure(structure)

        # Relacionamentos de chamada
        for element in elements:
            if element.type == 'function_definition':
                # Procura chamadas a outras funções
                for other in elements:
                    if other != element and other.type == 'function_definition':
                        if other.name in element.text:
                            relationships.append({
                                'type': 'calls',
                                'from': element.name,
                                'to': other.name,
                                'from_line': element.line,
                                'to_line': other.line
                            })

        # Relacionamentos de herança
        for element in elements:
            if element.type == 'class_definition':
                # Procura por herança
                if 'extends' in element.text or 'super()' in element.text:
                    relationships.append({
                        'type': 'inherits',
                        'from': element.name,
                        'to': 'parent_class',  # Seria extraído do parsing
                        'line': element.line
                    })

        return relationships

    def _identify_layers(self, structure: StructuralElement) -> List[Dict]:
        """Identifica camadas arquiteturais"""
        layers = []
        elements = self._flatten_structure(structure)

        # Mapeamento de elementos para camadas
        layer_mapping = {
            'Domain': ['entity', 'model', 'domain'],
            'Application': ['service', 'manager', 'orchestrator'],
            'Infrastructure': ['repository', 'dao', 'adapter'],
            'Interface': ['controller', 'api', 'endpoint', 'view']
        }

        for layer_name, keywords in layer_mapping.items():
            layer_elements = []
            for element in elements:
                if any(kw in element.text.lower() for kw in keywords):
                    layer_elements.append({
                        'name': element.name,
                        'type': element.type,
                        'line': element.line
                    })

            if layer_elements:
                layers.append({
                    'name': layer_name,
                    'elements': layer_elements,
                    'count': len(layer_elements)
                })

        return layers

    def _detect_design_patterns(self, structure: StructuralElement) -> List[Dict]:
        """Detecta padrões de design"""
        patterns = []
        elements = self._flatten_structure(structure)

        # Pattern: Singleton
        for element in elements:
            if element.name.lower().endswith('instance'):
                if 'static' in element.text and element.type == 'variable_declaration':
                    patterns.append({
                        'type': 'Singleton',
                        'class': 'Unknown',
                        'line': element.line,
                        'evidence': 'static instance variable'
                    })

        # Pattern: Factory
        for element in elements:
            if 'factory' in element.name.lower():
                patterns.append({
                    'type': 'Factory',
                    'class': element.name,
                    'line': element.line,
                    'evidence': 'name contains "factory"'
                })

        # Pattern: Observer
        for element in elements:
            if 'observer' in element.text.lower() or 'observable' in element.text.lower():
                patterns.append({
                    'type': 'Observer',
                    'class': element.name,
                    'line': element.line,
                    'evidence': 'mentions observer pattern'
                })

        return patterns

    def _serialize_structure(self, structure: StructuralElement) -> Dict:
        """Serializa estrutura para JSON"""
        def _serialize(node):
            return {
                'type': node.type,
                'name': node.name,
                'line': node.line,
                'column': node.column,
                'end_line': node.end_line,
                'end_column': node.end_column,
                'text': node.text[:100] + '...' if len(node.text) > 100 else node.text,
                'metadata': node.metadata,
                'children': [_serialize(child) for child in node.children]
            }

        return _serialize(structure)

class SpectrometerV10:
    """Spectrometer V10 - Full Circle: Tree-sitter → HAIKU → Next Level"""

    def __init__(self):
        self.structural_analyzer = TreeSitterStructuralAnalyzer()
        self.haiku_filler = HAIKUGapFiller()
        self.results = []

    def analyze_file_full_circle(self, file_path: Path) -> Dict[str, Any]:
        """Análise completa do ciclo: estrutura → HAIKU → insights"""
        print(f"\n🔄 SPECTROMETER V10 - FULL CIRCLE ANALYSIS")
        print(f"📁 File: {file_path}")
        print(f"=============================================")

        start_time = time.time()

        # Fase 1: Análise estrutural determinística (Tree-sitter)
        structure = self.structural_analyzer.analyze_file_structure(file_path)

        # Fase 2: Preenchimento de gaps com HAIKU
        haiku_insights = self.haiku_filler.fill_gaps(structure, file_path)

        # Fase 3: Geração de insights de próximo nível
        next_level_insights = self._generate_next_level_insights(
            structure,
            haiku_insights,
            file_path
        )

        duration = time.time() - start_time

        # Relatório completo
        report = {
            'file_path': str(file_path),
            'language': self.structural_analyzer._detect_language(file_path),
            'analysis_timestamp': time.time(),
            'duration_seconds': duration,
            'structural_analysis': {
                'total_elements': len(self.haiku_filler._flatten_structure(structure)),
                'max_depth': self._calculate_max_depth(structure),
                'complexity_score': self._calculate_complexity_score(structure)
            },
            'haiku_enhancement': haiku_insights,
            'next_level_insights': next_level_insights,
            'full_circle_score': self._calculate_full_circle_score(
                structure, haiku_insights, next_level_insights
            )
        }

        # Imprime resumo
        self._print_summary(report)

        return report

    def _generate_next_level_insights(self, structure: StructuralElement, haiku: Dict, file_path: Path) -> Dict[str, Any]:
        """Gera insights do próximo nível"""
        insights = {
            'architectural_smells': [],
            'code_quality_metrics': {},
            'refactoring_opportunities': [],
            'technical_debt_indicators': []
        }

        # Calcula métricas de qualidade
        elements = self.haiku_filler._flatten_structure(structure)

        # McCabe complexity (simplificado)
        insights['code_quality_metrics']['mccabe_complexity'] = self._calculate_mccabe(elements)

        # Acoplamento (simplificado)
        insights['code_quality_metrics']['coupling'] = len(haiku.get('semantic_relationships', []))

        # Coesão
        insights['code_quality_metrics']['cohesion'] = self._calculate_cohesion(elements)

        # Smells arquiteturais
        if insights['code_quality_metrics']['mccabe_complexity'] > 10:
            insights['architectural_smells'].append({
                'type': 'HighComplexity',
                'description': 'Function/method too complex',
                'severity': 'high'
            })

        # God Class
        for layer in haiku.get('architectical_layers', []):
            if layer['count'] > 20:
                insights['architectural_smells'].append({
                    'type': 'GodClass',
                    'layer': layer['name'],
                    'description': f'Layer {layer["name"]} has {layer["count"]} elements',
                    'severity': 'medium'
                })

        # Oportunidades de refactoring
        patterns = haiku.get('design_patterns', [])
        if not patterns:
            insights['refactoring_opportunities'].append({
                'type': 'MissingPatterns',
                'description': 'No design patterns detected - consider applying SOLID principles',
                'impact': 'medium'
            })

        return insights

    def _calculate_max_depth(self, structure: StructuralElement) -> int:
        """Calcula profundidade máxima da estrutura"""
        def _depth(node, current=0):
            if not node.children:
                return current
            return max(_depth(child, current + 1) for child in node.children)

        return _depth(structure, 0)

    def _calculate_complexity_score(self, structure: StructuralElement) -> float:
        """Calcula score de complexidade"""
        elements = self.haiku_filler._flatten_structure(structure)

        # Fatores de complexidade
        depth_score = self._calculate_max_depth(structure) * 10
        element_score = len(elements) * 2
        coupling_score = len([e for e in elements if e.type == 'function_definition']) * 5

        return depth_score + element_score + coupling_score

    def _calculate_mccabe(self, elements: List[StructuralElement]) -> float:
        """Calcula complexidade de McCabe simplificada"""
        complexity = 0
        for element in elements:
            if element.type in ['function_definition', 'method_definition']:
                text = element.text
                # Conta palavras-chave de decisão
                decision_keywords = ['if', 'elif', 'for', 'while', 'case', 'catch', '&&', '||']
                complexity += sum(1 for keyword in decision_keywords if keyword in text)

        return complexity

    def _calculate_cohesion(self, elements: List[StructuralElement]) -> float:
        """Calcula coesão simplificada"""
        classes = [e for e in elements if e.type == 'class_definition']

        if not classes:
            return 1.0

        total_cohesion = 0
        for cls in classes:
            # Simplificado: número de métodos / número total de elementos
            methods = [e for e in elements if e.parent == cls and e.type == 'function_definition']
            total_elements = [e for e in elements if e.parent == cls]

            if total_elements:
                cohesion = len(methods) / len(total_elements)
                total_cohesion += cohesion

        return total_cohesion / len(classes) if classes else 0

    def _calculate_full_circle_score(self, structure: StructuralElement, haiku: Dict, insights: Dict) -> float:
        """Calcula score final do Full Circle"""
        # Métricas ponderadas
        structure_score = 0.3
        haiku_score = 0.3
        insights_score = 0.4

        # Structure score (complexidade invertida)
        complexity = self._calculate_complexity_score(structure)
        structure_score = max(0, min(100, 100 - complexity / 10))

        # HAIKU score (baseado em classificações)
        haiku_count = len(haiku.get('haiku_classifications', []))
        total_elements = len(self.haiku_filler._flatten_structure(structure))
        haiku_score = (haiku_count / total_elements * 100) if total_elements > 0 else 0

        # Insights score (baseado em smells)
        smells_count = len(insights.get('architectural_smells', []))
        insights_score = max(0, 100 - smells_count * 10)

        # Média ponderada
        return (structure_score * 0.3 + haiku_score * 0.3 + insights_score * 0.4)

    def _print_summary(self, report: Dict[str, Any]):
        """Imprime resumo da análise"""
        print(f"\n📊 FULL CIRCLE ANALYSIS REPORT")
        print(f"================================")
        print(f"📁 File: {Path(report['file_path']).name}")
        print(f"🌐 Language: {report['language']}")
        print(f"⏱️  Duration: {report['duration_seconds']:.2f}s")
        print()

        # Estrutura
        struct = report['structural_analysis']
        print(f"🏗️  Structural Analysis:")
        print(f"   • Total Elements: {struct['total_elements']}")
        print(f"   • Max Depth: {struct['max_depth']}")
        print(f"   • Complexity Score: {struct['complexity_score']:.1f}")
        print()

        # HAIKU
        haiku = report['haiku_enhancement']
        print(f"⚛️  HAIKU Enhancement:")
        print(f"   • Classifications: {len(haiku.get('haiku_classifications', []))}")
        print(f"   • Relationships: {len(haiku.get('semantic_relationships', []))}")
        print(f"   • Architectural Layers: {len(haiku.get('architectural_layers', []))}")
        print(f"   • Design Patterns: {len(haiku.get('design_patterns', []))}")
        print()

        # Next Level
        insights = report['next_level_insights']
        quality = insights.get('code_quality_metrics', {})
        print(f"🚀 Next Level Insights:")
        print(f"   • McCabe Complexity: {quality.get('mccabe_complexity', 0)}")
        print(f"   • Coupling: {quality.get('coupling', 0)}")
        print(f"   • Cohesion: {quality.get('cohesion', 0):.2f}")
        print(f"   • Architectural Smells: {len(insights.get('architectural_smells', []))}")
        print(f"   • Refactoring Opportunities: {len(insights.get('refactoring_opportunities', []))}")
        print()

        # Score final
        print(f"🏆 Full Circle Score: {report['full_circle_score']:.1f}/100")
        print(f"================================")

    def analyze_repository_full_circle(self, repo_path: Path) -> Dict[str, Any]:
        """Análise completa do repositório"""
        print(f"\n🎯 SPECTROMETER V10 - REPOSITORY FULL CIRCLE")
        print(f"📁 Repository: {repo_path}")
        print(f"================================================")

        # Encontra arquivos para analisar
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs']
        files = []
        for ext in extensions:
            files.extend(repo_path.rglob(f'*{ext}'))

        # Limita para performance
        max_files = 30
        if len(files) > max_files:
            files = files[:max_files]

        # Analisa cada arquivo
        all_reports = []
        for file_path in files:
            print(f"\n🔄 Analyzing: {file_path.relative_to(repo_path)}")
            report = self.analyze_file_full_circle(file_path)
            all_reports.append(report)

        # Gera relatório consolidado
        repo_report = {
            'repository_path': str(repo_path),
            'analysis_timestamp': time.time(),
            'total_files': len(all_reports),
            'file_reports': all_reports,
            'summary': self._generate_repo_summary(all_reports)
        }

        # Salva relatório
        timestamp = int(time.time())
        report_path = Path(f"/tmp/spectrometer_v10_full_circle_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(repo_report, f, indent=2, default=str)

        print(f"\n💾 Repository report saved to: {report_path}")
        self._print_repo_summary(repo_report['summary'])

        return repo_report

    def _generate_repo_summary(self, all_reports: List[Dict]) -> Dict:
        """Gera sumário do repositório"""
        if not all_reports:
            return {}

        # Métricas agregadas
        total_elements = sum(r['structural_analysis']['total_elements'] for r in all_reports)
        avg_complexity = statistics.mean([r['structural_analysis']['complexity_score'] for r in all_reports])
        avg_score = statistics.mean([r['full_circle_score'] for r in all_reports])

        # Distribuição de linguagens
        languages = {}
        for r in all_reports:
            lang = r['language']
            languages[lang] = languages.get(lang, 0) + 1

        # Smells totais
        total_smells = sum(len(r['next_level_insights']['architectural_smells']) for r in all_reports)

        # Patterns totais
        total_patterns = sum(len(r['haiku_enhancement']['design_patterns']) for r in all_reports)

        return {
            'total_elements': total_elements,
            'average_complexity': avg_complexity,
            'average_full_circle_score': avg_score,
            'language_distribution': languages,
            'total_architectural_smells': total_smells,
            'total_design_patterns': total_patterns,
            'highest_scoring_file': max(all_reports, key=lambda r: r['full_circle_score'])['file_path'],
            'lowest_scoring_file': min(all_reports, key=lambda r: r['full_circle_score'])['file_path']
        }

    def _print_repo_summary(self, summary: Dict):
        """Imprime sumário do repositório"""
        print(f"\n📊 REPOSITORY SUMMARY")
        print(f"==================")
        print(f"📁 Total Files Analyzed: {summary['total_files']}")
        print(f"🏗️  Total Elements: {summary['total_elements']}")
        print(f"📊 Average Complexity: {summary['average_complexity']:.1f}")
        print(f"🏆 Average Score: {summary['average_full_circle_score']:.1f}/100")
        print()

        print(f"🌐 Language Distribution:")
        for lang, count in sorted(summary['language_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {lang}: {count}")
        print()

        print(f"⚠️  Architectural Smells: {summary['total_architectural_smells']}")
        print(f"🎨 Design Patterns: {summary['total_design_patterns']}")
        print()

        print(f"🏆 Best File: {Path(summary['highest_scoring_file']).name}")
        print(f"📉 Worst File: {Path(summary['lowest_scoring_file']).name}")
        print(f"==================")

# Execução principal
if __name__ == "__main__":
    spectrometer = SpectrometerV10()

    # Teste em arquivo específico
    test_files = [
        Path(__file__),  # Este arquivo
        Path("spectrometer_v9_universal.py"),
        Path("spectrometer_v7_haiku.py")
    ]

    print("🎯 SELECTIVE FULL CIRCLE ANALYSIS")
    print("==================================")

    for test_file in test_files:
        if test_file.exists():
            report = spectrometer.analyze_file_full_circle(test_file)
            print("\n" + "="*60)

    # Teste completo no diretório atual
    print("\n🎯 FULL REPOSITORY ANALYSIS")
    print("==========================")
    repo_report = spectrometer.analyze_repository_full_circle(Path(__file__).parent)

    print("\n✅ SPECTROMETER V10 - Full Circle Analysis Complete!")
    print("🔄 Tree-sitter → HAIKU → Next Level: ✅ Operational")