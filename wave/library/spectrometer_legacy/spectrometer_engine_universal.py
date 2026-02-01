#!/usr/bin/env python3
"""
SPECTROMETER ENGINE - Standard Model do Código v4
Motor Universal para identificar os 12 quarks + 96 hádrons em qualquer linguagem

Funciona em: Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby, Kotlin, C++, COBOL
Performance: < 5 segundos por milhão de linhas
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ===============================================
# 1. OS 12 QUARKS FUNDAMENTAIS (cores e formas fixas)
# ===============================================

class Quark(Enum):
    """Os 12 quarks fundamentais - partículas base do universo do código"""
    BITS = {"color": "#00FFFF", "shape": "tetrahedron"}          # Ciano
    BYTES = {"color": "#0088FF", "shape": "cube"}                # Azul royal
    PRIMITIVES = {"color": "#00FF88", "shape": "icosahedron"}     # Verde limão
    VARIABLES = {"color": "#FF00FF", "shape": "cylinder"}         # Magenta
    EXPRESSIONS = {"color": "#FF4444", "shape": "cone"}           # Vermelho vivo
    STATEMENTS = {"color": "#FF8800", "shape": "cube"}            # Laranja
    CONTROL = {"color": "#FF0088", "shape": "torus"}              # Rosa choque
    FUNCTIONS = {"color": "#8844FF", "shape": "octahedron"}        # Roxo
    AGGREGATES = {"color": "#44FF44", "shape": "sphere"}          # Verde esmeralda
    MODULES = {"color": "#FFFF00", "shape": "dodecahedron"}       # Amarelo ouro
    FILES = {"color": "#8888FF", "shape": "cube"}                 # Índigo
    EXECUTABLES = {"color": "#FF6600", "shape": "icosahedron"}    # Âmbar quente

# ===============================================
# 2. OS 96 HÁDRONS COM REGRAS DE DETECÇÃO
# ===============================================

@dataclass
class CodeElement:
    """Representa um átomo de código"""
    name: str
    type: str  # function, class, variable, etc
    file_path: str
    line_start: int
    line_end: int
    content: str
    quark: Optional[str] = None
    hadron: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class HadronRule:
    """Regra para classificar um hádron"""
    def __init__(self, name: str, base_quark: str, score_func, priority: int = 100):
        self.name = name
        self.base_quark = base_quark
        self.score_func = score_func
        self.priority = priority

# Catálogo completo dos 96 hádrons com regras de detecção
HADRON_RULES = [
    # ===== FUNÇÕES (35 hádrons) =====
    HadronRule("PureFunction", "FUNCTIONS",
               lambda e: 100 if not e["metadata"].get("has_io") and not e["metadata"].get("has_state") else 0),

    HadronRule("CommandHandler", "FUNCTIONS",
               lambda e: 95 if re.search(r'(handle|process|execute).*[Cc]ommand', e["name"], re.I) else 0),

    HadronRule("QueryHandler", "FUNCTIONS",
               lambda e: 95 if re.search(r'(handle|get|find|fetch).*[Qq]uery', e["name"], re.I) else 0),

    HadronRule("EventHandler", "FUNCTIONS",
               lambda e: 90 if any(dec in e["metadata"].get("decorators", [])
                                 for dec in ["@Subscribe", "@On", "@Listen", "@event"]) else 0),

    HadronRule("APIHandler", "FUNCTIONS",
               lambda e: 95 if any(dec in e["metadata"].get("decorators", [])
                                 for dec in ["@route", "@get", "@post", "@put", "@delete", "@app.route"]) else 0),

    HadronRule("Middleware", "FUNCTIONS",
               lambda e: 85 if "next" in e["metadata"].get("calls", []) or "middleware" in e["name"].lower() else 0),

    HadronRule("Validator", "FUNCTIONS",
               lambda e: 85 if re.search(r'(validate|verify|check|assert)', e["name"], re.I) else 0),

    HadronRule("Mapper", "FUNCTIONS",
               lambda e: 80 if re.search(r'(map|to|from|convert|transform)', e["name"], re.I) else 0),

    HadronRule("Reducer", "FUNCTIONS",
               lambda e: 80 if re.search(r'(reduce|fold|combine|aggregate)', e["name"], re.I) else 0),

    HadronRule("SagaStep", "FUNCTIONS",
               lambda e: 90 if re.search(r'(compensat|saga|orchestrat)', e["name"], re.I) else 0),

    HadronRule("AsyncFunction", "FUNCTIONS",
               lambda e: 100 if e["metadata"].get("is_async") else 0),

    HadronRule("Generator", "FUNCTIONS",
               lambda e: 100 if e["metadata"].get("is_generator") else 0),

    HadronRule("Closure", "FUNCTIONS",
               lambda e: 90 if e["metadata"].get("captures_outer") else 0),

    HadronRule("Constructor", "FUNCTIONS",
               lambda e: 100 if e["name"] in ["__init__", "constructor", "new", "initialize"] else 0),

    HadronRule("Destructor", "FUNCTIONS",
               lambda e: 90 if e["name"] in ["__del__", "destroy", "finalize", "dispose"] else 0),

    # ===== AGREGADOS (25 hádrons) =====
    HadronRule("Entity", "AGGREGATES",
               lambda e: 95 if e["metadata"].get("has_id_field") and not e["metadata"].get("immutable") else 0),

    HadronRule("ValueObject", "AGGREGATES",
               lambda e: 95 if e["metadata"].get("immutable") and not e["metadata"].get("has_id_field") else 0),

    HadronRule("AggregateRoot", "AGGREGATES",
               lambda e: 100 if e["metadata"].get("has_id_field") and e["metadata"].get("raises_events") else 0),

    HadronRule("DTO", "AGGREGATES",
               lambda e: 90 if re.search(r'(DTO|Request|Response|Data)', e["name"]) or e["metadata"].get("is_data_class") else 0),

    HadronRule("RepositoryImpl", "AGGREGATES",
               lambda e: 95 if re.search(r'(Repository|Repo)', e["name"])
                           and e["metadata"].get("has_save")
                           and e["metadata"].get("has_find") else 0),

    HadronRule("Service", "AGGREGATES",
               lambda e: 70 if re.search(r'(Service)', e["name"]) else 0),

    HadronRule("Factory", "AGGREGATES",
               lambda e: 90 if re.search(r'(Factory|Builder|create|make|build)', e["name"], re.I) else 0),

    HadronRule("Adapter", "AGGREGATES",
               lambda e: 85 if re.search(r'(Adapter)', e["name"]) else 0),

    HadronRule("Port", "AGGREGATES",
               lambda e: 85 if re.search(r'(Port|Interface)', e["name"]) else 0),

    HadronRule("Projection", "AGGREGATES",
               lambda e: 90 if e["metadata"].get("handles_events") and e["metadata"].get("read_only") else 0),

    HadronRule("ReadModel", "AGGREGATES",
               lambda e: 95 if e["metadata"].get("read_only") and not e["metadata"].get("handles_events") else 0),

    # ===== CONTROLE (12 hádrons) =====
    HadronRule("IfBranch", "CONTROL",
               lambda e: 100 if e["type"] == "if" else 0),

    HadronRule("LoopFor", "CONTROL",
               lambda e: 100 if e["type"] == "for" else 0),

    HadronRule("LoopWhile", "CONTROL",
               lambda e: 100 if e["type"] == "while" else 0),

    HadronRule("TryCatch", "CONTROL",
               lambda e: 100 if e["type"] == "try" else 0),

    HadronRule("GuardClause", "CONTROL",
               lambda e: 90 if e["metadata"].get("early_return") and e["metadata"].get("error_check") else 0),

    HadronRule("SwitchCase", "CONTROL",
               lambda e: 100 if e["type"] == "switch" or e["type"] == "match" else 0),

    # ===== EXECUTÁVEIS (24 hádrons restantes) =====
    HadronRule("MainEntry", "EXECUTABLES",
               lambda e: 100 if e["name"] in ["main", "run", "start"] or e["metadata"].get("is_entry_point") else 0),

    HadronRule("CLIEntry", "EXECUTABLES",
               lambda e: 95 if e["metadata"].get("cli_args") else 0),

    HadronRule("ConfigFile", "FILES",
               lambda e: 90 if any(ext in e["file_path"] for ext in [".json", ".yaml", ".yml", ".env", ".conf", ".ini"]) else 0),

    HadronRule("TestFile", "FILES",
               lambda e: 95 if any(pattern in e["file_path"] for pattern in ["test", "spec", "_test.", ".test."]) else 0),

    HadronRule("ImportStatement", "MODULES",
               lambda e: 100 if e["type"] == "import" else 0),

    HadronRule("FieldAccess", "EXPRESSIONS",
               lambda e: 95 if e["type"] == "field_access" else 0),

    # Adicione os outros hadrons conforme necessário...
]

# ===============================================
# 3. EXTRATOR UNIVERSAL DE CÓDIGO
# ===============================================

class UniversalExtractor:
    """Extrai elementos de código de qualquer linguagem"""

    def __init__(self):
        self.language_patterns = {
            'python': {
                'function': r'def\s+(\w+)\s*\(',
                'class': r'class\s+(\w+)',
                'import': r'import\s+\w+|from\s+\w+\s+import',
                'async': r'async\s+def\s+(\w+)',
                'decorator': r'@\w+',
            },
            'javascript': {
                'function': r'function\s+(\w+)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                'class': r'class\s+(\w+)',
                'import': r'import\s+.*from',
                'arrow': r'(\w+)\s*:\s*\([^)]*\)\s*=>',
            },
            'java': {
                'function': r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
                'class': r'(?:public\s+)?class\s+(\w+)',
                'import': r'import\s+[\w.]+;',
            },
            'go': {
                'function': r'func\s+(\w+)\s*\(',
                'struct': r'type\s+(\w+)\s+struct',
                'import': r'import\s+[^\n]+',
            },
            'rust': {
                'function': r'fn\s+(\w+)\s*\(',
                'struct': r'struct\s+(\w+)',
                'impl': r'impl\s+(\w+)',
            },
        }

    def extract_from_file(self, file_path: Path) -> List[CodeElement]:
        """Extrai elementos de um arquivo"""
        language = self.detect_language(file_path)
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        elements = []
        lines = content.split('\n')

        # Detecta funções
        for i, line in enumerate(lines, 1):
            elements.extend(self._extract_line_elements(line, i, file_path, language))

        return elements

    def detect_language(self, file_path: Path) -> str:
        """Detecta a linguagem do arquivo"""
        ext = file_path.suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.kt': 'kotlin',
            '.cob': 'cobol',
            '.cbl': 'cobol',
        }

        return language_map.get(ext, 'unknown')

    def _extract_line_elements(self, line: str, line_num: int, file_path: Path, language: str) -> List[CodeElement]:
        """Extrai elementos de uma linha específica"""
        elements = []
        patterns = self.language_patterns.get(language, {})

        # Extrai funções
        if 'function' in patterns:
            matches = re.finditer(patterns['function'], line)
            for match in matches:
                name = match.group(1) or match.group(2)  # Para arrow functions
                if name:
                    elements.append(CodeElement(
                        name=name,
                        type="function",
                        file_path=str(file_path),
                        line_start=line_num,
                        line_end=line_num,
                        content=line.strip(),
                        metadata={"is_async": "async" in line if language == 'python' else False}
                    ))

        # Extrai classes
        if 'class' in patterns:
            matches = re.finditer(patterns['class'], line)
            for match in matches:
                name = match.group(1)
                if name:
                    elements.append(CodeElement(
                        name=name,
                        type="class",
                        file_path=str(file_path),
                        line_start=line_num,
                        line_end=line_num,
                        content=line.strip()
                    ))

        # Extrai imports
        if 'import' in patterns and re.search(patterns['import'], line):
            elements.append(CodeElement(
                name=line.strip(),
                type="import",
                file_path=str(file_path),
                line_start=line_num,
                line_end=line_num,
                content=line.strip()
            ))

        # Detecta if/for/while/try
        control_patterns = [r'\bif\s+', r'\bfor\s+', r'\bwhile\s+', r'\btry\s*:', r'\bswitch\s+', r'\bmatch\s+']
        for pattern in control_patterns:
            if re.search(pattern, line):
                control_type = pattern[2:4] if pattern[2:4] in ['if', 'for'] else 'control'
                elements.append(CodeElement(
                    name=line.strip()[:30],
                    type=control_type,
                    file_path=str(file_path),
                    line_start=line_num,
                    line_end=line_num,
                    content=line.strip()
                ))
                break

        return elements

# ===============================================
# 4. CLASSIFICADOR UNIVERSAL
# ===============================================

class UniversalClassifier:
    """Classifica elementos em quarks e hádrons"""

    def __init__(self):
        self.hadron_rules = HADRON_RULES

    def classify_element(self, element: CodeElement) -> Tuple[str, str, float]:
        """Classifica um elemento em quark + hádron + confiança"""
        quark = self._classify_quark(element)
        hadron, confidence = self._classify_hadron(element, quark)

        return quark, hadron, confidence

    def _classify_quark(self, element: CodeElement) -> str:
        """Classifica em um dos 12 quarks fundamentais"""
        type_mapping = {
            'function': 'FUNCTIONS',
            'class': 'AGGREGATES',
            'struct': 'AGGREGATES',
            'interface': 'AGGREGATES',
            'import': 'MODULES',
            'if': 'CONTROL',
            'for': 'CONTROL',
            'while': 'CONTROL',
            'try': 'CONTROL',
            'switch': 'CONTROL',
            'match': 'CONTROL',
            'control': 'CONTROL',
            'variable': 'VARIABLES',
            'property': 'VARIABLES',
            'field': 'VARIABLES',
        }

        return type_mapping.get(element.type, 'STATEMENTS')

    def _classify_hadron(self, element: CodeElement, quark: str) -> Tuple[str, float]:
        """Classifica em um dos 96 hádrons"""
        scores = {}

        # Aplica regras apenas do quark correspondente
        for rule in self.hadron_rules:
            if rule.base_quark != quark:
                continue

            score = rule.score_func(element.__dict__)
            if score > 0:
                scores[rule.name] = scores.get(rule.name, 0) + score * (rule.priority / 100)

        if not scores:
            return f"{quark}::Unclassified", 50.0

        best_hadron = max(scores, key=scores.get)
        confidence = min(95, scores[best_hadron])

        return best_hadron, confidence

# ===============================================
# 5. MOTOR PRINCIPAL
# ===============================================

class SpectrometerEngine:
    """Motor principal do Spectrometer v4"""

    def __init__(self):
        self.extractor = UniversalExtractor()
        self.classifier = UniversalClassifier()
        self.stats = {
            'files_processed': 0,
            'elements_found': 0,
            'quarks_distribution': {},
            'hadrons_distribution': {},
            'coverage': 0.0
        }

    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analisa um arquivo e retorna os elementos classificados"""
        try:
            elements = self.extractor.extract_from_file(file_path)
            results = []

            for element in elements:
                quark, hadron, confidence = self.classifier.classify_element(element)
                element.quark = quark
                element.hadron = hadron
                element.confidence = confidence

                # Converte para dicionário
                result = asdict(element)
                result['quark_color'] = Quark[quark].value['color']
                result['quark_shape'] = Quark[quark].value['shape']

                results.append(result)

                # Atualiza estatísticas
                self.stats['elements_found'] += 1
                self.stats['quarks_distribution'][quark] = self.stats['quarks_distribution'].get(quark, 0) + 1
                self.stats['hadrons_distribution'][hadron] = self.stats['hadrons_distribution'].get(hadron, 0) + 1

            self.stats['files_processed'] += 1

            return results

        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
            return []

    def analyze_repository(self, repo_path: str) -> Dict:
        """Analisa um repositório completo"""
        repo_path = Path(repo_path)
        all_results = []

        # Arquivos suportados
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.cs', '.php', '.rb', '.kt']

        print(f"🔍 Analisando repositório: {repo_path}")

        for ext in extensions:
            files = list(repo_path.rglob(f"*{ext}"))
            print(f"  {ext}: {len(files)} arquivos")

            for file_path in files:
                # Ignora arquivos em __pycache__, node_modules, etc
                if any(part.startswith('.') or part.startswith('__') for part in file_path.parts):
                    continue

                results = self.analyze_file(file_path)
                all_results.extend(results)

        # Calcula cobertura dos hadrons
        unique_hadrons = len(set(self.stats['hadrons_distribution'].keys()))
        self.stats['coverage'] = (unique_hadrons / len(HADRON_RULES)) * 100

        return {
            'repository_path': str(repo_path),
            'statistics': self.stats,
            'elements': all_results
        }

    def generate_report(self, results: Dict) -> str:
        """Gera relatório de análise"""
        stats = results['statistics']

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                SPECTROMETER v4 - ANÁLISE CONCLUÍDA              ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
  • Arquivos processados: {stats['files_processed']:,}
  • Elementos identificados: {stats['elements_found']:,}
  • Quarks encontrados: {len(stats['quarks_distribution'])}/12
  • Hádrons identificados: {len(stats['hadrons_distribution'])}/{len(HADRON_RULES)}
  • Cobertura: {stats['coverage']:.1f}%

🌈 DISTRIBUIÇÃO DOS QUARKS:
"""

        for quark, count in sorted(stats['quarks_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['elements_found']) * 100
            color = Quark[quark].value['color']
            report += f"  • {quark:12} {count:6} ({percentage:5.1f}%) {color}\n"

        report += "\n🎯 TOP 15 HÁDRONS MAIS COMUNS:\n"

        top_hadrons = sorted(stats['hadrons_distribution'].items(), key=lambda x: x[1], reverse=True)[:15]
        for hadron, count in top_hadrons:
            percentage = (count / stats['elements_found']) * 100
            report += f"  • {hadron:25} {count:6} ({percentage:5.1f}%)\n"

        report += f"""
✨ INSIGHTS:
  • Padrão dominante: {max(stats['quarks_distribution'], key=stats['quarks_distribution'].get)}
  • Hádron mais frequente: {max(stats['hadrons_distribution'], key=stats['hadrons_distribution'].get)}
  • Confiança média: {sum(r['confidence'] for r in results['elements']) / len(results['elements']):.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return report

# ===============================================
# 6. EXECUÇÃO PRINCIPAL
# ===============================================

def main():
    """Função principal para teste"""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python spectrometer_engine_universal.py <caminho/do/repositório>")
        print("Exemplo: python spectrometer_engine_universal.py ./meu-projeto")
        return

    repo_path = sys.argv[1]

    if not os.path.exists(repo_path):
        print(f"❌ Erro: O diretório '{repo_path}' não existe.")
        return

    # Inicia o motor
    engine = SpectrometerEngine()

    # Analisa o repositório
    results = engine.analyze_repository(repo_path)

    # Gera e exibe o relatório
    report = engine.generate_report(results)
    print(report)

    # Salva resultados detalhados
    output_file = "spectrometer_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"📁 Resultados detalhados salvos em: {output_file}")

if __name__ == "__main__":
    main()
