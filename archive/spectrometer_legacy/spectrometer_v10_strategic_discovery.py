#!/usr/bin/env python3
"""
SPECTROMETER V10 - STRATEGIC DISCOVERY (DoD)
Depth of Discovery: CONTINENTS → HÁDRONS → SUB-HÁDRONS
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

from spectrometer_v9_universal import SpectrometerUniversal, Quark, Hadron

@dataclass
class DiscoveryPhase:
    """Fase de descoberta estratégica"""
    phase: int  # 1: Continentes, 2: Hádrons, 3: Sub-hádrons
    name: str
    description: str
    confidence_threshold: float
    discovery_methods: List[str]

@dataclass
class Continent:
    """Continente arquitetural (nível 1)"""
    id: str
    name: str
    hadrons: List[str]
    characteristics: Dict[str, Any]
    detected_in: List[str]  # files onde foi detectado
    confidence: float

@dataclass
class HadronV2:
    """Hádron refinado (nível 2)"""
    id: str
    name: str
    continent: str
    patterns: List[str]
    semantic_markers: Dict[str, Any]
    examples: List[str]
    confidence: float

@dataclass
class Subhadron:
    """Sub-hádron granular (nível 3)"""
    id: str
    name: str
    hadron: str
    dimensions: Dict[str, Any]  # 4 dimensões fundamentais
    tactical_patterns: List[str]
    rarity: str
    confidence: float

class StrategicDiscovery:
    """Sistema de descoberta estratégica em 3 níveis"""

    def __init__(self):
        self.phases = self._define_discovery_phases()
        self.continents = self._define_continents()
        self.hadrons = self._define_hadrons()
        self.subhadrons = self._define_subhadrons()
        self.discovered = {
            'continents': {},
            'hadrons': {},
            'subhadrons': {}
        }
        self.spectrometer = SpectrometerUniversal()

    def _define_discovery_phases(self) -> List[DiscoveryPhase]:
        """Define as 3 fases de descoberta"""
        return [
            DiscoveryPhase(
                phase=1,
                name="CONTINENTAL DISCOVERY",
                description="Identificar grandes continentes arquiteturais",
                confidence_threshold=0.7,
                discovery_methods=["structural_scan", "naming_patterns", "module_analysis"]
            ),
            DiscoveryPhase(
                phase=2,
                name="HADRONIC IDENTIFICATION",
                description="Detectar hádrons específicos dentro dos continentes",
                confidence_threshold=0.6,
                discovery_methods=["pattern_matching", "semantic_analysis", "context_inference"]
            ),
            DiscoveryPhase(
                phase=3,
                name="SUB-HADRONS EXCAVATION",
                description="Escavar sub-hádrons granulares dos hádrons detectados",
                confidence_threshold=0.5,
                discovery_methods=["dimensional_analysis", "tactical_patterns", "microsemantics"]
            )
        ]

    def _define_continents(self) -> Dict[str, Continent]:
        """Define os continentes arquiteturais"""
        return {
            "DOMAIN_CONTINENT": Continent(
                id="DC001",
                name="Domain Core",
                hadrons=["Entity", "AggregateRoot", "ValueObject", "DomainService"],
                characteristics={
                    "scope": "business_rules",
                    "persistence": "through_repositories",
                    "validation": "invariant_enforcement"
                },
                detected_in=[],
                confidence=0.0
            ),
            "APPLICATION_CONTINENT": Continent(
                id="AC001",
                name="Application Layer",
                hadrons=["ApplicationService", "UseCase", "CommandHandler", "QueryHandler"],
                characteristics={
                    "scope": "orchestration",
                    "coordination": "workflow",
                    "transaction_boundaries": True
                },
                detected_in=[],
                confidence=0.0
            ),
            "INFRASTRUCTURE_CONTINENT": Continent(
                id="IC001",
                name="Infrastructure",
                hadrons=["Repository", "ExternalService", "Cache", "MessageBroker"],
                characteristics={
                    "scope": "technical_concerns",
                    "external_systems": True,
                    "performance_focus": True
                },
                detected_in=[],
                confidence=0.0
            ),
            "INTERFACE_CONTINENT": Continent(
                id="IC002",
                name="Interface/Presentation",
                hadrons=["APIController", "GraphQLResolver", "RESTEndpoint", "View"],
                characteristics={
                    "scope": "external_boundary",
                    "protocol_translation": True,
                    "response_formatting": True
                },
                detected_in=[],
                confidence=0.0
            )
        }

    def _define_hadrons(self) -> Dict[str, HadronV2]:
        """Define os hádrons específicos"""
        hadrons = {}

        # Domain hadrons
        hadrons["Entity"] = HadronV2(
            id="H001",
            name="Entity",
            continent="DOMAIN_CONTINENT",
            patterns=["class.*Entity", "@Entity", "dataclass", "has_id"],
            semantic_markers={
                "has_identity": True,
                "immutable_partial": False,
                "behavioral_methods": False
            },
            examples=["UserEntity", "Product", "Order", "Invoice"],
            confidence=0.0
        )

        hadrons["AggregateRoot"] = HadronV2(
            id="H002",
            name="AggregateRoot",
            continent="DOMAIN_CONTINENT",
            patterns=["class.*Aggregate", "extends.*Entity.*Aggregate", "repository_pattern"],
            semantic_markers={
                "global_identity": True,
                "consistency_boundary": True,
                "domain_events": True
            },
            examples=["UserAggregate", "OrderAggregate", "ShoppingCart"],
            confidence=0.0
        )

        # Application hadrons
        hadrons["CommandHandler"] = HadronV2(
            id="H003",
            name="CommandHandler",
            continent="APPLICATION_CONTINENT",
            patterns=["handle.*Command", "@CommandHandler", "execute.*Create"],
            semantic_markers={
                "side_effects": True,
                "transactional": True,
                "no_return_value": True
            },
            examples=["CreateOrderHandler", "UpdateUserCommand", "DeleteProductHandler"],
            confidence=0.0
        )

        hadrons["QueryHandler"] = HadronV2(
            id="H004",
            name="QueryHandler",
            continent="APPLICATION_CONTINENT",
            patterns=["handle.*Query", "@QueryHandler", "find.*Query", "get.*Query"],
            semantic_markers={
                "read_only": True,
                "no_side_effects": True,
                "returns_data": True
            },
            examples=["FindUserQuery", "ListProductsQuery", "GetOrderDetails"],
            confidence=0.0
        )

        # Infrastructure hadrons
        hadrons["Repository"] = HadronV2(
            id="H005",
            name="Repository",
            continent="INFRASTRUCTURE_CONTINENT",
            patterns=["Repository", "DAO", "@Repository", "save.*find"],
            semantic_markers={
                "persistence": True,
                "crud_operations": True,
                "abstraction_layer": True
            },
            examples=["UserRepository", "OrderDAO", "ProductRepository"],
            confidence=0.0
        )

        # Interface hadrons
        hadrons["APIController"] = HadronV2(
            id="H006",
            name="APIController",
            continent="INTERFACE_CONTINENT",
            patterns=["@Controller", "@RestController", "@GetMapping", "post.*mapping"],
            semantic_markers={
                "http_protocol": True,
                "serialization": True,
                "status_codes": True
            },
            examples=["UserController", "ProductAPI", "OrderController"],
            confidence=0.0
        )

        return hadrons

    def _define_subhadrons(self) -> Dict[str, Subhadron]:
        """Define os sub-hádrons granulares"""
        subhadrons = {}

        # Dimensões fundamentais
        responsibilities = [
            "Create", "Update", "Delete", "FindById", "FindAll", "Search",
            "Validate", "Transform", "Calculate", "Execute", "Orchestrate"
        ]

        purities = ["Pure", "Impure", "Idempotent", "Transactional"]
        scopes = ["Local", "Distributed", "Singleton", "Scoped", "Transient"]
        timings = ["Synchronous", "Asynchronous", "EventDriven", "Batch"]

        # Gera combinações estratégicas
        counter = 1
        for hadron_name, hadron in self.hadrons.items():
            for resp in responsibilities[:5]:  # Limit para 384
                for pure in purities[:4]:
                    for scope in scopes[:4]:
                        if counter <= 384:
                            subhadron = Subhadron(
                                id=f"SH{counter:03d}",
                                name=f"{hadron_name}::{resp}::{pure}::{scope}",
                                hadron=hadron_name,
                                dimensions={
                                    "Responsibility": resp,
                                    "Purity": pure,
                                    "Scope": scope,
                                    "Timing": "Synchronous"
                                },
                                tactical_patterns=[resp.lower(), pure.lower()],
                                rarity="Common",
                                confidence=0.0
                            )

                            # Calcula raridade baseada na combinação
                            exotic_count = sum([
                                resp in ["Orchestrate", "Execute", "Transform"],
                                pure == "Transactional",
                                scope == "Distributed"
                            ])

                            if exotic_count >= 2:
                                subhadron.rarity = "Exotic"
                            elif exotic_count == 1:
                                subhadron.rarity = "Rare"

                            subhadrons[subhadron.id] = subhadron
                            counter += 1

        return subhadrons

    def discover_in_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Executa descoberta estratégica completa"""
        print(f"\n🎯 STRATEGIC DISCOVERY - Depth of Discovery")
        print(f"📁 Repository: {repo_path}")
        print(f"===========================================")

        start_time = time.time()

        # Fase 1: Descoberta Continental
        print("\n🌍 FASE 1: CONTINENTAL DISCOVERY")
        print("--------------------------------")
        self._discover_continents(repo_path)

        # Fase 2: Identificação Hadronic
        print("\n⚛️  FASE 2: HADRONIC IDENTIFICATION")
        print("-----------------------------------")
        self._discover_hadrons(repo_path)

        # Fase 3: Escavação Sub-Hadrons
        print("\n🔍 FASE 3: SUB-HADRONS EXCAVATION")
        print("---------------------------------")
        self._discover_subhadrons(repo_path)

        duration = time.time() - start_time

        # Relatório final
        report = {
            "repository_path": str(repo_path),
            "timestamp": time.time(),
            "duration_seconds": duration,
            "discovered_continents": len(self.discovered['continents']),
            "discovered_hadrons": len(self.discovered['hadrons']),
            "discovered_subhadrons": len(self.discovered['subhadrons']),
            "continents": self.discovered['continents'],
            "hadrons": self.discovered['hadrons'],
            "subhadrons": self.discovered['subhadrons'],
            "discovery_map": self._generate_discovery_map(),
            "strategic_insights": self._generate_strategic_insights()
        }

        # Imprime resumo
        self._print_discovery_summary(report)

        # Salva relatório
        timestamp = int(time.time())
        report_path = Path(f"/tmp/strategic_discovery_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n💾 Discovery report saved to: {report_path}")

        return report

    def _discover_continents(self, repo_path: Path):
        """Fase 1: Descoberta de continentes"""
        files = self._get_code_files(repo_path)
        phase = self.phases[0]

        for file_path in files:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            detected_continents = self._scan_for_continents(content, file_path)

            for continent_id, confidence in detected_continents.items():
                if confidence >= phase.confidence_threshold:
                    if continent_id not in self.discovered['continents']:
                        self.discovered['continents'][continent_id] = self.continents[continent_id]

                    self.discovered['continents'][continent_id].detected_in.append(str(file_path))
                    self.discovered['continents'][continent_id].confidence = max(
                        self.discovered['continents'][continent_id].confidence,
                        confidence
                    )

    def _scan_for_continents(self, content: str, file_path: Path) -> Dict[str, float]:
        """Escaneia arquivo em busca de continentes"""
        content_lower = content.lower()
        file_path_str = str(file_path).lower()

        scores = {}

        # Domain patterns
        if any(pattern in content_lower for pattern in ['entity', 'aggregate', 'domain']):
            scores['DOMAIN_CONTINENT'] = min(1.0, scores.get('DOMAIN_CONTINENT', 0) + 0.5)
        if 'domain' in file_path_str:
            scores['DOMAIN_CONTINENT'] += 0.3

        # Application patterns
        if any(pattern in content_lower for pattern in ['service', 'usecase', 'handler', 'command']):
            scores['APPLICATION_CONTINENT'] = min(1.0, scores.get('APPLICATION_CONTINENT', 0) + 0.5)
        if 'application' in file_path_str:
            scores['APPLICATION_CONTINENT'] += 0.3

        # Infrastructure patterns
        if any(pattern in content_lower for pattern in ['repository', 'dao', 'cache', 'message']):
            scores['INFRASTRUCTURE_CONTINENT'] = min(1.0, scores.get('INFRASTRUCTURE_CONTINENT', 0) + 0.5)
        if 'infra' in file_path_str:
            scores['INFRASTRUCTURE_CONTINENT'] += 0.3

        # Interface patterns
        if any(pattern in content_lower for pattern in ['controller', 'api', 'rest', 'graphql']):
            scores['INTERFACE_CONTINENT'] = min(1.0, scores.get('INTERFACE_CONTINENT', 0) + 0.5)
        if 'api' in file_path_str or 'controller' in file_path_str:
            scores['INTERFACE_CONTINENT'] += 0.3

        return scores

    def _discover_hadrons(self, repo_path: Path):
        """Fase 2: Identificação de hádrons"""
        files = self._get_code_files(repo_path)
        phase = self.phases[1]

        for file_path in files:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            detected_hadrons = self._scan_for_hadrons(content, file_path)

            for hadron_id, details in detected_hadrons.items():
                confidence = details['confidence']
                if confidence >= phase.confidence_threshold:
                    if hadron_id not in self.discovered['hadrons']:
                        hadron = self.hadrons[hadron_id]
                        self.discovered['hadrons'][hadron_id] = {
                            'hadron': hadron,
                            'detected_in': [],
                            'confidence': confidence,
                            'evidence': details.get('evidence', [])
                        }

                    self.discovered['hadrons'][hadron_id]['detected_in'].append(str(file_path))
                    self.discovered['hadrons'][hadron_id]['confidence'] = max(
                        self.discovered['hadrons'][hadron_id]['confidence'],
                        confidence
                    )

    def _scan_for_hadrons(self, content: str, file_path: Path) -> Dict[str, Dict]:
        """Escaneia arquivo em busca de hádrons"""
        content_lower = content.lower()
        lines = content.split('\n')

        detected = {}

        for hadron_id, hadron in self.hadrons.items():
            confidence = 0.0
            evidence = []

            # Match de patterns
            for pattern in hadron.patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    confidence += 0.3
                    evidence.append(f"Pattern match: {pattern}")

            # Match de semantic markers
            for marker, value in hadron.semantic_markers.items():
                if value and marker in content_lower:
                    confidence += 0.2
                    evidence.append(f"Semantic marker: {marker}")

            # Match de exemplos
            for example in hadron.examples:
                if example.lower() in content_lower:
                    confidence += 0.1

            if confidence > 0:
                detected[hadron_id] = {
                    'confidence': min(1.0, confidence),
                    'evidence': evidence
                }

        return detected

    def _discover_subhadrons(self, repo_path: Path):
        """Fase 3: Escavação de sub-hádrons"""
        phase = self.phases[2]

        # Só escava onde encontrou hádrons
        for hadron_id, hadron_data in self.discovered['hadrons'].items():
            for file_path_str in hadron_data['detected_in']:
                file_path = Path(file_path_str)
                content = file_path.read_text(encoding='utf-8', errors='ignore')

                detected_subhadrons = self._scan_for_subhadrons(
                    content,
                    file_path,
                    hadron_id
                )

                for subhadron_id, confidence in detected_subhadrons.items():
                    if confidence >= phase.confidence_threshold:
                        if subhadron_id not in self.discovered['subhadrons']:
                            self.discovered['subhadrons'][subhadron_id] = {
                                'subhadron': self.subhadrons[subhadron_id],
                                'detected_in': [],
                                'confidence': confidence
                            }

                        self.discovered['subhadrons'][subhadron_id]['detected_in'].append(file_path_str)
                        self.discovered['subhadrons'][subhadron_id]['confidence'] = max(
                            self.discovered['subhadrons'][subhadron_id]['confidence'],
                            confidence
                        )

    def _scan_for_subhadrons(self, content: str, file_path: Path, parent_hadron: str) -> Dict[str, float]:
        """Escaneia arquivo em busca de sub-hádrons específicos"""
        content_lower = content.lower()
        lines = content.split('\n')

        detected = {}

        # Filtra sub-hádrons do hadron pai
        relevant_subhadrons = {
            id: sub for id, sub in self.subhadrons.items()
            if sub.hadron == parent_hadron
        }

        for subhadron_id, subhadron in relevant_subhadrons.items():
            confidence = 0.0

            # Match de nome
            if subhadron.hadron.lower() in content_lower:
                confidence += 0.2

            # Match de dimensões
            for dim_name, dim_value in subhadron.dimensions.items():
                if dim_value.lower() in content_lower:
                    confidence += 0.15

            # Match de patterns táticos
            for pattern in subhadron.tactical_patterns:
                if pattern in content_lower:
                    confidence += 0.1

            # Ajuste baseado na raridade
            if subhadron.rarity == "Exotic":
                confidence *= 0.7  # Mais difícil de detectar
            elif subhadron.rarity == "Rare":
                confidence *= 0.85

            if confidence > 0.5:
                detected[subhadron_id] = min(1.0, confidence)

        return detected

    def _get_code_files(self, repo_path: Path) -> List[Path]:
        """Obtém arquivos de código do repositório"""
        extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cs', '.php', '.rb']
        files = []

        for ext in extensions:
            files.extend(repo_path.rglob(f'*{ext}'))

        # Limita para performance
        max_files = 100
        if len(files) > max_files:
            files = files[:max_files]

        return files

    def _generate_discovery_map(self) -> Dict:
        """Gera mapa visual da descoberta"""
        map_data = {
            "continents": {},
            "coverage": {
                "continents": len(self.discovered['continents']),
                "hadrons": len(self.discovered['hadrons']),
                "subhadrons": len(self.discovered['subhadrons']),
                "total_possible": len(self.continents) + len(self.hadrons) + len(self.subhadrons)
            }
        }

        for continent_id, continent in self.discovered['continents'].items():
            map_data["continents"][continent_id] = {
                "name": continent.name,
                "confidence": continent.confidence,
                "hadrons_count": len([
                    h for h in self.discovered['hadrons'].values()
                    if h['hadron'].continent == continent_id
                ]),
                "files": continent.detected_in
            }

        return map_data

    def _generate_strategic_insights(self) -> List[Dict]:
        """Gera insights estratégicos da descoberta"""
        insights = []

        # Cobertura continental
        continental_coverage = len(self.discovered['continents']) / len(self.continents) * 100
        if continental_coverage < 50:
            insights.append({
                "type": "low_coverage",
                "level": "continental",
                "message": f"Only {continental_coverage:.1f}% of continents discovered",
                "recommendation": "Consider reviewing domain boundaries"
            })

        # Distribuição de hádrons
        hadron_distribution = {}
        for hadron_data in self.discovered['hadrons'].values():
            continent = hadron_data['hadron'].continent
            hadron_distribution[continent] = hadron_distribution.get(continent, 0) + 1

        # Sub-hádrons por hádron
        subhadron_per_hadron = {}
        for subhadron_data in self.discovered['subhadrons'].values():
            hadron = subhadron_data['subhadron'].hadron
            subhadron_per_hadron[hadron] = subhadron_per_hadron.get(hadron, 0) + 1

        if subhadron_per_hadron:
            avg_subhadrons = statistics.mean(subhadron_per_hadron.values())
            insights.append({
                "type": "granularity_analysis",
                "message": f"Average {avg_subhadrons:.1f} sub-hadrons per hadron",
                "distribution": subhadron_per_hadron
            })

        return insights

    def _print_discovery_summary(self, report: Dict):
        """Imprime resumo da descoberta"""
        print(f"\n📊 STRATEGIC DISCOVERY SUMMARY")
        print(f"===============================")
        print(f"📁 Repository: {Path(report['repository_path']).name}")
        print(f"⏱️  Duration: {report['duration_seconds']:.2f}s")
        print()

        print(f"🌍 Continents Discovered: {report['discovered_continents']}/{len(self.continents)}")
        for continent_id, continent_data in report['continents'].items():
            print(f"  • {continent_data['name']}: {continent_data['confidence']:.1%} confidence")

        print(f"\n⚛️  Hadrons Identified: {report['discovered_hadrons']}")
        for hadron_id, hadron_data in report['hadrons'].items():
            print(f"  • {hadron_data['hadron'].name}: {hadron_data['confidence']:.1%}")

        print(f"\n🔍 Sub-Hadrons Excavated: {report['discovered_subhadrons']}")

        # Raridade distribution
        rarity_dist = {}
        for subhadron_data in report['subhadrons'].values():
            rarity = subhadron_data['subhadron'].rarity
            rarity_dist[rarity] = rarity_dist.get(rarity, 0) + 1

        for rarity, count in sorted(rarity_dist.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {rarity}: {count}")

        print(f"\n📈 Discovery Coverage: {report['discovery_map']['coverage']}")

        print(f"\n💡 Strategic Insights:")
        for insight in report['strategic_insights']:
            print(f"  • {insight['message']}")

        print(f"===============================")

# Execução principal
if __name__ == "__main__":
    discovery = StrategicDiscovery()

    # Descobre no diretório atual
    repo_path = Path(__file__).parent
    report = discovery.discover_in_repository(repo_path)

    print(f"\n✅ Strategic Discovery Complete!")
    print(f"🌍 → ⚛️  → 🔍 : {len(report['discovered_continents'])} → {len(report['discovered_hadrons'])} → {len(report['discovered_subhadrons'])}")