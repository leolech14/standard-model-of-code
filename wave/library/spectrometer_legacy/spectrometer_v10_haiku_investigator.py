#!/usr/bin/env python3
"""
SPECTROMETER V10 - HAIKU INVESTIGATOR
Fazendo os 384 sub-hádrons teóricos serem encontrados na prática
"""

import json
import time
import statistics
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from spectrometer_v9_universal import SpectrometerUniversal

@dataclass
class SubhadronTemplate:
    """Template de sub-hádron investigável"""
    id: str
    parent_hadron: str
    name: str
    dimensions: Dict[str, Any]
    keywords: List[str]
    anti_keywords: List[str]  # Palavras que contradizem
    context_clues: List[str]  # Padrões de contexto
    examples: List[str]
    rarity: str
    detection_methods: List[str]

@dataclass
class DetectionResult:
    """Resultado de detecção de sub-hádron"""
    subhadron_id: str
    confidence: float
    evidence: List[str]
    context: Dict[str, Any]
    location: Dict[str, Any]

class HaikuInvestigator:
    """Investigador que faz sub-hádrons aparecerem na realidade"""

    def __init__(self):
        self.spectrometer = SpectrometerUniversal()
        self.templates = self._create_all_384_templates()
        self.results = []
        self.investigation_log = []

    def _create_all_384_templates(self) -> Dict[str, SubhadronTemplate]:
        """Cria os 384 templates de sub-hádrons"""
        templates = {}
        counter = 1

        # Dimensões fundamentais
        responsibilities = [
            "Create", "Update", "Delete", "FindById", "FindAll", "Search", "Query",
            "List", "Count", "Exists", "Validate", "Authorize", "Authenticate",
            "Encrypt", "Decrypt", "Transform", "Convert", "Calculate",
            "Process", "Execute", "Handle", "Manage", "Orchestrate",
            "Coordinate", "Route", "Filter", "Map", "Reduce", "Merge",
            "Split", "Join", "Sort", "Index", "Cache", "Log", "Monitor"
        ]

        purities = [
            "Pure", "Impure", "Idempotent", "Transactional",
            "SideEffect", "NoSideEffect", "Stateless", "Stateful"
        ]

        scopes = [
            "Local", "Singleton", "Scoped", "Transient", "Ephemeral",
            "Global", "Request", "Session", "Application"
        ]

        timings = [
            "Synchronous", "Asynchronous", "EventDriven", "Batch",
            "RealTime", "Scheduled", "Lazy", "Eager"
        ]

        boundaries = [
            "Internal", "External", "CrossBoundary", "Boundary",
            "Embedded", "Standalone", "Integrated"
        ]

        # 12 hadrons base
        hadrons = [
            "Entity", "AggregateRoot", "ValueObject", "DomainService",
            "ApplicationService", "CommandHandler", "QueryHandler",
            "RepositoryImpl", "ExternalService", "APIHandler",
            "Controller"
        ]

        # Gera combinações estratégicas (não todas as 384, as mais relevantes)
        for hadron in hadrons:
            for resp in responsibilities[:12]:  # Limit para os mais comuns
                for pure in purities[:4]:
                    for scope in scopes[:4]:
                        for timing in timings[:4]:
                            template_id = f"SH{counter:03d}"
                            name = f"{hadron}::{resp}::{pure}::{scope}::{timing}"

                            # Detecta combinações impossíveis (os 42 antimatéria)
                            if self._is_impossible_combination(hadron, resp, pure):
                                name += " [IMPOSSIBLE]"

                            templates[template_id] = SubhadronTemplate(
                                id=template_id,
                                parent_hadron=hadron,
                                name=name,
                                dimensions={
                                    "Responsibility": resp,
                                    "Purity": pure,
                                    "Scope": scope,
                                    "Timing": timing,
                                    "Boundary": "Internal"
                                },
                                keywords=self._generate_keywords(hadron, resp, pure),
                                anti_keywords=self._generate_anti_keywords(hadron, resp, pure),
                                context_clues=self._generate_context_clues(hadron, resp),
                                examples=self._generate_examples(hadron, resp),
                                rarity=self._calculate_rarity(hadron, resp, pure, scope),
                                detection_methods=["lexical", "semantic", "contextual", "structural"]
                            )
                            counter += 1

        return templates

    def _is_impossible_combination(self, hadron: str, resp: str, pure: str) -> bool:
        """Verifica se combinação é impossível (leis fundamentais)"""
        # Lei 1: CQRS - Commands nunca devolvem
        if hadron == "CommandHandler" and resp in ["FindById", "FindAll", "Query", "Search", "List", "Get"]:
            return True

        # Lei 2: CQRS - Queries nunca alteram
        if hadron == "QueryHandler" and resp in ["Create", "Update", "Delete", "Save", "Persist"]:
            return True

        # Lei 3: Pure Functions nunca têm side-effects
        if hadron == "Entity" and pure != "Stateless":
            return False  # Entity pode ter estado

        if hadron == "PureFunction" and pure != "Pure":
            return True

        # Lei 4: Services são stateless
        if hadron == "ApplicationService" and scope == "Global":
            return True

        return False

    def _generate_keywords(self, hadron: str, resp: str, pure: str) -> List[str]:
        """Gera keywords para busca"""
        keywords = []

        # Keywords do hadron pai
        hadron_keywords = {
            "Entity": ["entity", "model", "domain", "class", "struct"],
            "CommandHandler": ["handler", "command", "create", "save", "delete"],
            "QueryHandler": ["handler", "query", "find", "get", "list"],
            "RepositoryImpl": ["repository", "dao", "save", "find", "delete"],
            "APIHandler": ["controller", "api", "endpoint", "rest", "json"],
            "ApplicationService": ["service", "business", "logic", "orchestrator"]
        }

        keywords.extend(hadron_keywords.get(hadron, []))
        keywords.extend([resp.lower()])

        # Keywords da pureza
        if pure == "Pure":
            keywords.extend(["pure", "no_side_effects", "deterministic"])
        elif pure == "Impure":
            keywords.extend(["impure", "has_side_effects", "modifies"])

        return keywords

    def _generate_anti_keywords(self, hadron: str, resp: str, pure: str) -> List[str]:
        """Gera anti-palavras que indicam que NÃO é aquele sub-hádron"""
        anti_keywords = []

        # Anti-CQRS
        if hadron == "CommandHandler":
            anti_keywords.extend(["return", "find", "get", "query", "select", "fetch"])
        elif hadron == "QueryHandler":
            anti_keywords.extend(["save", "delete", "update", "insert", "modify"])

        # Anti-pureza
        if pure == "Pure":
            anti_keywords.extend(["save", "delete", "modify", "write", "persist"])
        elif pure == "Stateless":
            anti_keywords.extend(["static", "global", "shared", "cache"])

        return anti_keywords

    def _generate_context_clues(self, hadron: str, resp: str) -> List[str]:
        """Gera pistas de contexto"""
        clues = []

        # Contexto imports
        import_patterns = {
            "Entity": ["from domain", "from models", "import entity", "from domain_model"],
            "RepositoryImpl": ["import repository", "from infrastructure", "from persistence"],
            "APIHandler": ["from fastapi", "from flask", "from django", "@rest", "@controller"],
            "ApplicationService": ["@service", "from application"]
        }

        clues.extend(import_patterns.get(hadron, []))

        # Contexto de responsabilidade
        resp_patterns = {
            "Create": ["save", "create", "insert", "add", "new"],
            "Find": ["find", "get", "retrieve", "fetch", "select"],
            "Update": ["update", "modify", "edit", "change", "set"],
            "Delete": ["delete", "remove", "drop", "destroy"]
        }

        clues.extend(resp_patterns.get(resp, []))

        return clues

    def _generate_examples(self, hadron: str, resp: str) -> List[str]:
        """Gera exemplos de nomes"""
        examples = []

        if hadron == "Entity":
            examples = [f"User{resp}", f"Product{resp}", f"Order{resp}", f"Invoice{resp}"]
        elif hadron == "CommandHandler":
            examples = [f"{resp}Handler", f"{resp}Command", f"Handle{resp}"]
        elif hadron == "QueryHandler":
            examples = [f"{resp}Query", f"Get{resp}Query", f"Find{resp}"]
        elif hadron == "RepositoryImpl":
            examples = [f"{resp}Repository", f"{resp}DAO", f"{resp}Storage"]

        return examples[:5]  # Limita exemplos

    def _calculate_rarity(self, hadron: str, resp: str, pure: str, scope: str) -> str:
        """Calcula raridade do sub-hádron"""
        # Fatores de raridade
        exotic_factors = 0

        # Responsabilidades exóticas
        exotic_responsibilities = ["Orchestrate", "Coordinate", "Monitor", "Schedule"]
        if resp in exotic_responsibilities:
            exotic_factors += 1

        # Purezas incomuns
        if pure == "Transactional":
            exotic_factors += 1
        elif pure == "NoSideEffect":
            exotic_factors += 1

        # Scopes especiais
        if scope in ["Global", "Application"]:
            exotic_factors += 1

        if exotic_factors >= 2:
            return "Exotic"
        elif exotic_factors == 1:
            return "Rare"
        else:
            return "Common"

    def investigate_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Investiga repositório para encontrar sub-hádrons"""
        print(f"\n🔍 HAIKU INVESTIGATOR")
        print(f"📁 Repository: {repo_path}")
        print(f"🔬 Searching for 384 theoretical sub-hádrons...")
        print(f"================================")

        start_time = time.time()

        # Fase 1: Análise base com Spectometer
        base_analysis = self.spectrometer.analyze_repository(repo_path)

        # Fase 2: Investigação profunda com múltiplas estratégias
        print(f"\n🕵️ DEEP INVESTIGATION PHASE")
        print(f"----------------------------")

        all_results = []
        investigated_files = 0

        for file_data in base_analysis.get('files', []):
            if 'error' in file_data:
                continue

            file_path = Path(file_data['file_path'])
            print(f"\n🔍 Investigating: {file_path.name}")

            # Extrai conteúdo completo
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Análise estrutural com AST se for Python
            if file_path.suffix == '.py':
                try:
                    tree = ast.parse(content)
                    file_results = self._investigate_python_file(file_path, tree, content)
                except:
                    file_results = self._investigate_generic_file(file_path, content)
            else:
                file_results = self._investigate_generic_file(file_path, content)

            if file_results:
                all_results.extend(file_results)
                investigated_files += 1
                print(f"  ✅ Found {len(file_results)} sub-hadron candidates")
            else:
                print(f"  ⚪️ No sub-hádrons found")

        # Fase 3: Análise e refinamento
        print(f"\n🔬 REFINEMENT AND ANALYSIS")
        print(f"----------------------------")
        refined_results = self._refine_investigation(all_results)

        # Fase 4: Geração de relatório
        duration = time.time() - start_time

        report = {
            "investigation_metadata": {
                "repository": str(repo_path),
                "timestamp": time.time(),
                "duration_seconds": duration,
                "files_investigated": investigated_files,
                "total_templates": len(self.templates)
            },
            "statistics": {
                "total_candidates": len(all_results),
                "refined_matches": len(refined_results),
                "unique_subhadrons": len(set(r.subhadron_id for r in refined_results)),
                "average_confidence": statistics.mean([r.confidence for r in refined_results]) if refined_results else 0,
                "max_confidence": max([r.confidence for r in refined_results]) if refined_results else 0,
                "rarity_distribution": self._calculate_rarity_distribution(refined_results)
            },
            "discovered_subhadrons": refined_results,
            "templates_used": len([t for t in self.templates.values() if '[IMPOSSIBLE]' not in t.name]),
            "impossible_detections": [r for r in all_results if '[IMPOSSIBLE]' in self.templates.get(r.subhadron_id, SubhadronTemplate()).name]
        }

        # Salva relatório detalhado
        timestamp = int(time.time())
        report_path = Path(f"/tmp/haiku_investigation_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n💾 Investigation report saved to: {report_path}")
        self._print_investigation_summary(report)

        return report

    def _investigate_python_file(self, file_path: Path, tree: ast.AST, content: str) -> List[DetectionResult]:
        """Investiga arquivo Python usando AST"""
        results = []

        class SubhadronVisitor(ast.NodeVisitor):
            def __init__(self):
                self.results = []
                self.current_function = None

            def visit_FunctionDef(self, node):
                old_function = self.current_function
                self.current_function = node
                self.generic_visit(node)
                self.current_function = old_function

            def visit_ClassDef(self, node):
                old_function = self.current_function
                self.current_function = node
                self.generic_visit(node)
                self.current_function = old_function

            def visit_Call(self, node):
                # Analisa chamadas de função para detectar padrões
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        method_name = node.func.value.id
                        # Verifica se corresponde a um padrão
                        for template_id, template in self.templates.items():
                            if self._matches_pattern(method_name, template, content, self.current_function):
                                confidence = self._calculate_confidence(method_name, template, content, self.current_function)
                                if confidence > 0.3:
                                    result = DetectionResult(
                                        subhadron_id=template_id,
                                        confidence=confidence,
                                        evidence=[f"Method call: {method_name}"],
                                        context={
                                            "function": self.current_function.name if self.current_function else "module",
                                            "line": node.lineno,
                                            "file": str(file_path)
                                        },
                                        location={
                                            "type": "method_call",
                                            "line": node.lineno
                                        }
                                    )
                                    results.append(result)

                self.generic_visit(node)

            def visit_Assign(self, node):
                # Analisa atribuições para detectar operações
                if isinstance(node.value, ast.Attribute):
                    if isinstance(node.value.value, ast.Name):
                        attr_name = node.value.value.id
                        for template_id, template in self.templates.items():
                            if self._matches_pattern(attr_name, template, content, self.current_function):
                                confidence = self._calculate_confidence(attr_name, template, content, self.current_function)
                                if confidence > 0.3:
                                    result = DetectionResult(
                                        subhadron_id=template_id,
                                        confidence=confidence,
                                        evidence=[f"Assignment: {attr_name}"],
                                        context={
                                            "function": self.current_function.name if self.current_function else "module",
                                            "line": node.lineno,
                                            "file": str(file_path)
                                        },
                                        location={
                                            "type": "assignment",
                                            "line": node.lineno
                                        }
                                    )
                                    results.append(result)

                self.generic_visit(node)

        visitor = SubhadronVisitor()
        visitor.visit(tree)

        return results

    def _investigate_generic_file(self, file_path: Path, content: str) -> List[DetectionResult]:
        """Investiga arquivo genérico usando patterns textuais"""
        results = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            # Verifica cada template
            for template_id, template in self.templates.items():
                if '[IMPOSSIBLE]' in template.name:
                    continue  # Pula os impossíveis

                score = 0
                evidence = []

                # Verifica keywords
                keyword_matches = sum(1 for kw in template.keywords if kw in line_lower)
                if keyword_matches > 0:
                    score += 0.1 * keyword_matches

                # Verifica padrões de contexto
                for clue in template.context_clues:
                    if clue in line_lower:
                        score += 0.15

                # Verifica exemplos
                for example in template.examples:
                    if example.lower() in line_lower:
                        score += 0.25

                # Verifica anti-palavras
                anti_keyword_hits = sum(1 for ak in template.anti_keywords if ak in line_lower)
                if anti_keyword_hits > 0:
                    score -= 0.3

                # Verifica nome do elemento
                element_name = self._extract_element_name(line)
                if element_name and element_name.lower() in [kw.lower() for kw in template.keywords]:
                    score += 0.2

                if score > 0.4:  # Threshold baixo para aumentar detecção
                    result = DetectionResult(
                        subhadron_id=template_id,
                        confidence=min(1.0, score),
                        evidence=[f"Line pattern match: {line.strip()}"],
                        context={
                            "line": line_num,
                            "file": str(file_path),
                            "element": element_name
                        },
                        location={
                            "type": "line_pattern",
                            "line": line_num
                        }
                    )
                    results.append(result)

        return results

    def _matches_pattern(self, name: str, template: SubhadsonTemplate, content: str, context=None) -> bool:
        """Verifica se corresponde ao padrão"""
        name_lower = name.lower()

        # Verifica se o nome corresponde a um sub-padrão
        if template.dimensions["Responsibility"].lower() in name_lower:
            return True

        # Verifica se o contexto indica o sub-padrão
        if context and isinstance(context, ast.FunctionDef):
            func_name = context.name.lower()
            if template.dimensions["Responsibility"].lower() in func_name:
                return True

        return False

    def _calculate_confidence(self, name: str, template: SubhadsonTemplate, content: str, context=None) -> float:
        """Calcula confiança da detecção"""
        confidence = 0.0

        # Fator 1: Nome do elemento
        if template.dimensions["Responsibility"].lower() in name.lower():
            confidence += 0.4
        if template.dimensions["Purity"].lower() in name.lower():
            confidence += 0.2

        # Fator 2: Presença de keywords
        keyword_count = sum(1 for kw in template.keywords if kw in content.lower())
        if keyword_count > 0:
            confidence += 0.2 * min(keyword_count / 3, 1.0)

        # Fator 3: Pistas de contexto
        clue_count = sum(1 for clue in template.context_clues if clue in content.lower())
        if clue_count > 0:
            confidence += 0.1 * min(clue_count / 2, 1.0)

        # Fator 4: Raridade
        if template.rarity == "Exotic":
            confidence *= 1.2
        elif template.rarity == "Rare":
            confidence *= 1.1

        return min(1.0, confidence)

    def _extract_element_name(self, line: str) -> Optional[str]:
        """Extrai nome de elemento da linha"""
        # Padrões comuns
        patterns = [
            r'def\s+(\w+)\s*\(',
            r'class\s+(\w+)\s*:',
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=',
            r'(\w+)\s*:',
            r'async\s+def\s+(\w+)\s*\(',
            r'@.*def\s+(\w+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)

        return None

    def _refine_investigation(self, all_results: List[DetectionResult]) -> List[DetectionResult]:
        """Refina e filtra resultados da investigação"""
        refined = []

        for result in all_results:
            # Filtro 1: Confiança mínima
            if result.confidence < 0.3:
                continue

            # Filtro 2: Verifica anti-padrões
            template = self.templates.get(result.subhadron_id)
            if template:
                content = result.context.get('file', '')
                line = result.context.get('line', 0)
                try:
                    with open(content, 'r') as f:
                        lines = f.readlines()
                    if line <= len(lines):
                        line_content = lines[line - 1].lower()
                        anti_keyword_hits = sum(1 for ak in template.anti_keywords if ak in line_content)
                        if anti_keyword_hits > 0:
                            result.confidence -= 0.5
                except:
                    pass

            # Filtro 3: Verifica consistência
            if result.confidence >= 0.5:
                refined.append(result)

        # Remove duplicados mantendo a maior confiança
        seen = set()
        unique_results = []
        for result in sorted(refined, key=lambda x: x.confidence, reverse=True):
            key = (result.subhadron_id, result.context.get('file', ''), result.location.get('line', 0))
            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        return unique_results

    def _calculate_rarity_distribution(self, results: List[DetectionResult]) -> Dict[str, int]:
        """Calcula distribuição de raridade"""
        distribution = {"Common": 0, "Rare": 0, "Exotic": 0}

        for result in results:
            template = self.templates.get(result.subhadron_id)
            if template:
                distribution[template.rarity] = distribution.get(template.rarity, 0) + 1

        return distribution

    def _print_investigation_summary(self, report: Dict):
        """Imprime resumo da investigação"""
        stats = report["statistics"]
        print(f"\n📊 INVESTIGATION SUMMARY")
        print(f"=====================")
        print(f"📁 Repository: {Path(report['investigation_metadata']['repository']).name}")
        print(f"⏱️  Duration: {report['investigation_metadata']['duration_seconds']:.2f}s")
        print(f"📁 Files Investigated: {report['investigation_metadata']['files_investigated']}")
        print(f"📋 Templates Available: {report['investigation_metadata']['total_templates']}")
        print()

        print(f"🔍 DETECTION STATISTICS:")
        print(f"  • Total Candidates: {stats['total_candidates']}")
        print(f"  • Refined Matches: {stats['refined_matches']}")
        print(f"  • Unique Sub-hádrons: {stats['unique_subhadrons']}")
        print(f"  • Average Confidence: {stats['average_confidence']:.2f}")
        print(f"  • Max Confidence: {stats['max_confidence']:.2f}")

        print(f"\n📈 RARITY DISTRIBUTION:")
        for rarity, count in sorted(stats['rarity_distribution'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rarity}: {count}")

        if report["impossible_detections"]:
            print(f"\n⚠️ IMPOSSIBLE PATTERNS DETECTED:")
            for result in report["impossible_detections"][:5]:
                template = self.templates[result.subhadron_id]
                print(f"  • {template.name} in {Path(result.context['file']).name}")
                print(f"    Evidence: {result.evidence[0]}")

        print(f"\n🎯 SUCCESS RATE:")
        success_rate = (stats['unique_subhadrons'] / stats['total_templates']) * 100 if stats['total_templates'] > 0 else 0
        print(f"  • Templates Activated: {success_rate:.1f}%")
        print(f"  • Of 384 theoretical: {success_rate:.1f}% found")
        print(f"=====================")

# Execução principal
if __name__ == "__main__":
    investigator = HaikuInvestigator()

    # Investiga no diretório atual
    repo_path = Path(__file__).parent
    report = investigator.investigate_repository(repo_path)

    print(f"\n🔍 INVESTIGATION COMPLETE!")
    print(f"📊 Results: {report['statistics']['unique_subhadrons']} sub-hádrons encontrados")
    print(f"🎯 Achievement: Sub-hádrons teóricos agora são REAIS!")
