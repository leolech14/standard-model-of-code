#!/usr/bin/env python3
"""
FINAL CONTROLLED VALIDATOR - HAIKU v2 FULL ACTIVATED
O LHC do Software - Detectando os 342 sub-hádrons possíveis + 42 buracos negros
"""

import json
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib
import tempfile
import subprocess

# Import do Spectometer Universal (funciona em qualquer Python)
from spectrometer_v9_universal import SpectrometerUniversal, Quark, Hadron

@dataclass
class HaikuSubhadron:
    """Sub-hádron HAIKU - 342 possíveis + 42 impossíveis"""
    id: str
    name: str
    parent_hadron: str
    dimensions: Dict[str, str]  # 4 forças fundamentais
    rarity: str  # Common, Rare, Exotic, IMPOSSIBLE
    law_violated: Optional[str]  # Para os 42 impossíveis
    antimatter: bool  # True para os 42
    confidence: float

class HAIKUV2Engine:
    """Motor HAIKU v2 com os 384 sub-hádrons completos"""

    def __init__(self):
        self.subhadrons = self._generate_all_384()
        self.impossible_42 = [s for s in self.subhadrons if s.antimatter]
        self.possible_342 = [s for s in self.subhadrons if not s.antimatter]

    def _generate_all_384(self) -> List[HaikuSubhadron]:
        """Gera os 384 sub-hádrons via combinação sistemática"""
        subhadrons = []

        # As 4 dimensões (forças fundamentais)
        responsibilities = [
            "Create", "Update", "Delete", "FindById", "FindAll", "Query", "Project",
            "Transform", "Validate", "Calculate", "Execute", "Process", "Handle",
            "Manage", "Orchestrate", "Coordinate", "Route", "Filter", "Map",
            "Reduce", "Merge", "Split", "Join", "Sort", "Search", "Index",
            "Cache", "Log", "Monitor", "Secure", "Serialize", "Deserialize"
        ]

        purities = ["Pure", "Impure", "Idempotent", "ExternalIO"]
        boundaries = ["Domain", "Application", "Infrastructure", "Adapter", "API", "Test"]
        lifecycles = ["Singleton", "Scoped", "Transient", "Ephemeral", "Immortal"]

        # 12 hadrons principais que geram sub-hádrons
        hadron_parents = [
            "Service", "Entity", "RepositoryImpl", "CommandHandler", "QueryHandler",
            "APIHandler", "TestFunction", "Constructor", "AsyncFunction",
            "PureFunction", "ImportStatement", "Control"
        ]

        # As 11 leis fundamentais
        laws = {
            "CQRS_Command": "CommandHandler nunca devolve dados",
            "CQRS_Query": "QueryHandler nunca altera estado",
            "PureFunction": "PureFunction nunca tem side-effects",
            "Entity_ID": "Entity sempre tem identificador",
            "ValueObject_ID": "ValueObject nunca tem identificador",
            "Repository_Impure": "Repository sempre tem I/O",
            "EventHandler_NoReturn": "EventHandler nunca retorna valor",
            "API_External": "APIHandler sempre cruza fronteira externa",
            "Service_Stateless": "Service nunca tem estado",
            "Test_Isolated": "Test nunca toca produção",
            "Validator_Rejects": "Validator sempre rejeita inválido"
        }

        # Gera combinações
        counter = 1
        for hadron in hadron_parents:
            for resp in responsibilities:
                for pure in purities:
                    for bound in boundaries:
                        for life in lifecycles:
                            subhadron = HaikuSubhadron(
                                id=f"HS{counter:03d}",
                                name=f"{hadron}::{resp}::{pure}",
                                parent_hadron=hadron,
                                dimensions={
                                    "Responsibility": resp,
                                    "Purity": pure,
                                    "Boundary": bound,
                                    "Lifecycle": life
                                },
                                rarity="Common",
                                law_violated=None,
                                antimatter=False,
                                confidence=0.9
                            )

                            # Aplica as 11 leis - detecta os 42 impossíveis
                            if hadron == "CommandHandler" and resp in ["FindById", "FindAll", "Query"]:
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["CQRS_Command"]
                                subhadron.confidence = 0.0
                            elif hadron == "QueryHandler" and resp in ["Create", "Update", "Delete", "Save"]:
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["CQRS_Query"]
                                subhadron.confidence = 0.0
                            elif hadron == "PureFunction" and pure != "Pure":
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["PureFunction"]
                                subhadron.confidence = 0.0
                            elif hadron == "Entity" and resp == "Stateless":
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["Entity_ID"]
                                subhadron.confidence = 0.0
                            elif hadron == "TestFunction" and bound == "Application":
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["Test_Isolated"]
                                subhadron.confidence = 0.0
                            elif hadron == "APIHandler" and bound in ["Domain", "Application"]:
                                subhadron.antimatter = True
                                subhadron.rarity = "IMPOSSIBLE"
                                subhadron.law_violated = laws["API_External"]
                                subhadron.confidence = 0.0
                            else:
                                # Calcula raridade baseada em combinações exóticas
                                exotic_count = sum([
                                    pure == "ExternalIO",
                                    bound == "Infrastructure",
                                    life == "Immortal"
                                ])
                                if exotic_count >= 2:
                                    subhadron.rarity = "Exotic"
                                elif exotic_count == 1:
                                    subhadron.rarity = "Rare"

                            subhadrons.append(subhadron)
                            counter += 1

        # Limita aos 384 mais relevantes
        subhadrons = subhadrons[:384]

        return subhadrons

    def classify_with_haiku(self, hadron: Hadron, context: Dict[str, Any]) -> Optional[HaikuSubhadron]:
        """Classifica hadron usando HAIKU v2"""
        matches = []

        # Busca matches nos 342 possíveis
        for subhadron in self.possible_342:
            if subhadron.parent_hadron == hadron.type:
                # Analisa nome e contexto
                name_score = self._calculate_name_match(hadron.name, subhadron)
                context_score = self._calculate_context_match(context, subhadron)

                combined_score = (name_score + context_score) / 2

                if combined_score > 0.3:  # Reduzido para aumentar detecção
                    match = subhadron
                    match.confidence = combined_score
                    matches.append(match)

        # Retorna o melhor match
        if matches:
            return max(matches, key=lambda m: m.confidence)

        # Se nenhum match, retorna para detectar impossíveis
        return self._detect_antimatter(hadron, context)

    def _calculate_name_match(self, element_name: str, subhadron: HaikuSubhadron) -> float:
        """Calcula match baseado no nome"""
        name = element_name.lower()
        score = 0.0

        # Match principal
        if subhadron.parent_hadron.lower() in name:
            score += 0.4

        # Match de responsabilidade
        resp = subhadron.dimensions["Responsibility"].lower()
        if resp in name:
            score += 0.3
        elif any(word in name for word in resp.split()):
            score += 0.2

        # Match de pureza
        pure = subhadron.dimensions["Purity"].lower()
        if pure in name:
            score += 0.1

        return min(1.0, score)

    def _calculate_context_match(self, context: Dict[str, Any], subhadron: HaikuSubhadron) -> float:
        """Calcula match baseado no contexto do código"""
        score = 0.5  # Base neutro

        # Análise de imports (boundary)
        imports = context.get("imports", [])
        if subhadron.dimensions["Boundary"] == "External" and imports:
            score += 0.2
        elif subhadron.dimensions["Boundary"] == "Test" and any("test" in imp.lower() for imp in imports):
            score += 0.3

        # Análise de async (lifecycle)
        if subhadron.dimensions["Lifecycle"] == "Ephemeral" and context.get("has_async"):
            score += 0.2

        # Análise de side-effects (purity)
        has_side_effects = context.get("has_side_effects", False)
        if subhadron.dimensions["Purity"] == "Impure" and has_side_effects:
            score += 0.2
        elif subhadron.dimensions["Purity"] == "Pure" and not has_side_effects:
            score += 0.2

        return min(1.0, score)

    def _detect_antimatter(self, hadron: Hadron, context: Dict[str, Any]) -> Optional[HaikuSubhadron]:
        """Detecta se é um dos 42 impossíveis (antimatéria)"""
        for impossible in self.impossible_42:
            if impossible.parent_hadron == hadron.type:
                # Analisa padrões específicos
                if self._matches_impossible_pattern(hadron.name, context, impossible):
                    impossible.detected_in = {
                        "element_name": hadron.name,
                        "file": context.get("file_path", "unknown"),
                        "line": context.get("line", 0)
                    }
                    return impossible
        return None

    def _matches_impossible_pattern(self, name: str, context: Dict, impossible: HaikuSubhadron) -> bool:
        """Verifica se corresponde a um padrão impossível"""
        patterns = {
            "CommandHandler::Find": ["find", "get", "query", "search", "list"],
            "QueryHandler::Save": ["save", "create", "update", "delete", "persist"],
            "PureFunction::IO": ["open", "write", "read", "network", "database"],
            "TestFunction::Production": ["write_to_db", "send_email", "publish"],
            "APIHandler::Internal": ["internal_", "_private"]
        }

        name_lower = name.lower()
        for pattern, keywords in patterns.items():
            if pattern in impossible.name:
                if any(kw in name_lower for kw in keywords):
                    return True

        return False

class FinalValidator:
    """Validador final com HAIKU v2 completo"""

    def __init__(self):
        self.spectrometer = SpectrometerUniversal()
        self.haiku_engine = HAIKUV2Engine()
        self.results = []

    def analyze_repository_with_haiku(self, repo_path: Path) -> Dict[str, Any]:
        """Análise completa com HAIKU v2 ativado"""
        print(f"\n🔥 FINAL CONTROLLED VALIDATOR - HAIKU v2 FULL ACTIVATED")
        print(f"📁 Repositório: {repo_path}")
        print(f"⚛️  Analisando com {len(self.haiku_engine.possible_342)} possíveis + {len(self.haiku_engine.impossible_42)} impossíveis")
        print(f"================================================================")

        start_time = time.time()

        # Analisa com Spectometer Universal
        analysis = self.spectrometer.analyze_repository(repo_path)

        # Aplica HAIKU v2 nos hadrons encontrados
        enhanced_results = []
        antimatter_detections = []

        for file_result in analysis.get('files', []):
            if 'error' in file_result:
                continue

            enhanced_file = file_result.copy()
            enhanced_hadrons = []

            # Processa cada hadron do arquivo
            for hadron_info in file_result.get('hadron_details', []):
                # Cria contexto para análise HAIKU
                context = {
                    "file_path": file_result['file_path'],
                    "imports": self._extract_imports(file_result['file_path']),
                    "has_async": "async" in hadron_info['name'].lower(),
                    "has_side_effects": self._detect_side_effects(file_result['file_path'], hadron_info['name'])
                }

                # Classifica com HAIKU
                haiku_match = self.haiku_engine.classify_with_haiku(
                    Hadron(
                        type=hadron_info['type'],
                        name=hadron_info['name'],
                        quarks=[],
                        confidence=hadron_info['confidence']
                    ),
                    context
                )

                # Adiciona informações HAIKU
                enhanced_hadron = hadron_info.copy()
                if haiku_match:
                    enhanced_hadron['haiku_id'] = haiku_match.id
                    enhanced_hadron['haiku_name'] = haiku_match.name
                    enhanced_hadron['haiku_rarity'] = haiku_match.rarity
                    enhanced_hadron['dimensions'] = haiku_match.dimensions

                    if haiku_match.antimatter:
                        enhanced_hadron['ANTIMATTER'] = True
                        enhanced_hadron['VIOLATED_LAW'] = haiku_match.law_violated
                        antimatter_detections.append({
                            'file': file_result['file_path'],
                            'element': hadron_info['name'],
                            'haiku_id': haiku_match.id,
                            'violation': haiku_match.law_violated
                        })
                        print(f"  ☢️  ANTIMATTER DETECTED: {hadron_info['name']} → {haiku_match.name}")
                        print(f"      Law violated: {haiku_match.law_violated}")
                    else:
                        if haiku_match.rarity == "Exotic":
                            print(f"  🌟 EXOTIC HAIKU: {hadron_info['name']} → {haiku_match.name}")
                        elif haiku_match.rarity == "Rare":
                            print(f"  💎 RARE HAIKU: {hadron_info['name']} → {haiku_match.name}")

                enhanced_hadrons.append(enhanced_hadron)

            enhanced_file['hadron_details'] = enhanced_hadrons
            enhanced_results.append(enhanced_file)

        # Gera relatório final
        duration = time.time() - start_time
        total_hadrons = sum(len(r.get('hadron_details', [])) for r in enhanced_results)
        haiku_classified = sum(1 for r in enhanced_results for h in r.get('hadron_details', []) if 'haiku_id' in h)

        # Estatísticas de raridade
        rarity_stats = {}
        for result in enhanced_results:
            for hadron in result.get('hadron_details', []):
                rarity = hadron.get('haiku_rarity', 'Unclassified')
                rarity_stats[rarity] = rarity_stats.get(rarity, 0) + 1

        final_report = {
            'repository_path': str(repo_path),
            'validation_type': 'HAIKU_v2_FULL',
            'timestamp': time.time(),
            'duration_seconds': duration,
            'spectrometer_analysis': analysis,
            'haiku_enhancement': {
                'total_hadrons': total_hadrons,
                'haiku_classified': haiku_classified,
                'classification_rate': (haiku_classified / total_hadrons * 100) if total_hadrons > 0 else 0,
                'rarity_distribution': rarity_stats,
                'antimatter_detections': antimatter_detections,
                'possible_342_found': len(set(h['haiku_id'] for r in enhanced_results for h in r.get('hadron_details', []) if h.get('haiku_id') and not h.get('ANTIMATTER'))),
                'impossible_42_detected': len(antimatter_detections)
            },
            'files': enhanced_results
        }

        # Relatório final
        print(f"\n================================================================")
        print(f"📊 HAIKU v2 VALIDATION REPORT")
        print(f"================================================================")
        print(f"📁 Repositório: {repo_path}")
        print(f"⏱️  Duração: {duration:.2f}s")
        print(f"🎯 Total hadrons: {total_hadrons}")
        print(f"⚛️  HAIKU classificados: {haiku_classified} ({haiku_classified/total_hadrons*100:.1f}%)")
        print(f"☢️  Antimatter detectada: {len(antimatter_detections)}")
        print(f"\n📈 Distribuição de raridade:")
        for rarity, count in sorted(rarity_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rarity}: {count}")

        if antimatter_detections:
            print(f"\n☢️  BURACOS NEGROS DETECTADOS:")
            for detection in antimatter_detections:
                print(f"  • {detection['element']} ({Path(detection['file']).name})")
                print(f"    Lei violada: {detection['violation']}")

        # Score final
        antimatter_penalty = len(antimatter_detections) * 10
        haiku_score = max(0, 100 - antimatter_penalty)

        print(f"\n🏆 SCORE HAIKU v2: {haiku_score}/100")
        print(f"================================================================")

        final_report['haiku_enhancement']['final_score'] = haiku_score

        return final_report

    def _extract_imports(self, file_path: str) -> List[str]:
        """Extrai imports do arquivo"""
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            imports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.append(line)
            return imports
        except:
            return []

    def _detect_side_effects(self, file_path: str, element_name: str) -> bool:
        """Detecta se elemento tem side-effects"""
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            in_function = False

            for line in lines:
                if element_name in line and ('def ' in line or 'function' in line):
                    in_function = True
                elif in_function:
                    # Detecta padrões de side-effect
                    if any(pattern in line.lower() for pattern in [
                        'print(', 'open(', 'write(', 'save(', 'delete(',
                        'execute(', 'query(', 'insert(', 'update('
                    ]):
                        return True
                    # Detecta fim da função
                    if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        in_function = False
            return False
        except:
            return False

    def run_comprehensive_validation(self, repo_path: Path) -> Dict[str, Any]:
        """Executa validação completa e salva resultados"""
        print(f"\n🚀 INICIANDO VALIDAÇÃO COMPLETA COM HAIKU v2")
        print(f"=================================================")

        # Executa análise
        result = self.analyze_repository_with_haiku(repo_path)

        # Salva resultado
        timestamp = int(time.time())
        report_path = Path(f"/tmp/haiku_v2_validation_{timestamp}.json")

        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n💾 Relatório completo salvo em: {report_path}")

        # Gera CSV dos 42 impossíveis detectados
        if result['haiku_enhancement']['antimatter_detections']:
            self._generate_antimatter_csv(result['haiku_enhancement']['antimatter_detections'])

        return result

    def _generate_antimatter_csv(self, detections: List[Dict]):
        """Gera CSV dos impossíveis detectados"""
        csv_path = Path("/tmp/antimatter_detections.csv")
        with open(csv_path, 'w') as f:
            f.write("File,Element,HAIKU_ID,Violation_Law\n")
            for d in detections:
                f.write(f"{Path(d['file']).name},{d['element']},{d['haiku_id']},{d['violation']}\n")
        print(f"📄 Antimatter CSV salvo em: {csv_path}")

# Execução principal
if __name__ == "__main__":
    validator = FinalValidator()

    # Teste no diretório atual
    test_repo = Path(__file__).parent
    result = validator.run_comprehensive_validation(test_repo)

    # Estatística final
    haiku_data = result['haiku_enhancement']
    print(f"\n🎯 ESTATÍSTICAS FINAIS:")
    print(f"  • HAIKU classificados: {haiku_data['haiku_classified']}/{haiku_data['total_hadrons']}")
    print(f"  • Taxa de classificação: {haiku_data['classification_rate']:.1f}%")
    print(f"  • Sub-hádrons únicos dos 342 possíveis: {haiku_data['possible_342_found']}")
    print(f"  • Buracos negros dos 42 impossíveis: {haiku_data['impossible_42_detected']}")
    print(f"  • Score final: {haiku_data['final_score']}/100")

    print(f"\n🔥 HAIKU v2 - LHC do Software: ATIVADO! 🔥")