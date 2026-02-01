#!/usr/bin/env python3
"""
SPECTROMETER V10 - STRATEGIC DISCOVERY (SIMPLE)
Depth of Discovery: CONTINENTS → HÁDRONS → SUB-HÁDRONS
"""

import json
import time
import re
from pathlib import Path
from spectrometer_v9_universal import SpectrometerUniversal

class SimpleStrategicDiscovery:
    """Descoberta estratégica simplificada em 3 níveis"""

    def __init__(self):
        self.spectrometer = SpectrometerUniversal()
        self.discovered = {
            'continents': {},
            'hadrons': {},
            'subhadrons': {}
        }

    def discover_in_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Executa descoberta estratégica completa"""
        print(f"\n🎯 STRATEGIC DISCOVERY - Depth of Discovery")
        print(f"📁 Repository: {repo_path}")
        print(f"===========================================")

        start_time = time.time()

        # Analisa com Spectometer
        analysis = self.spectrometer.analyze_repository(repo_path)

        # Fase 1: Descoberta Continental (mapeamento dos hadrons)
        print("\n🌍 FASE 1: CONTINENTAL DISCOVERY")
        print("--------------------------------")
        self._map_to_continents(analysis)

        # Fase 2: Identificação Hadronic refinada
        print("\n⚛️  FASE 2: HADRONIC IDENTIFICATION")
        print("-----------------------------------")
        self._refine_hadrons()

        # Fase 3: Sub-hádrons táticos
        print("\n🔍 FASE 3: SUB-HADRONS STRATEGIC")
        print("--------------------------------")
        self._extract_subhadrons(analysis)

        duration = time.time() - start_time

        # Relatório final
        report = {
            "repository_path": str(repo_path),
            "timestamp": time.time(),
            "duration_seconds": duration,
            "discovery_levels": {
                "continents": len(self.discovered['continents']),
                "hadrons": len(self.discovered['hadrons']),
                "subhadrons": len(self.discovered['subhadrons'])
            },
            "strategic_map": self._generate_strategic_map(),
            "insights": self._generate_insights()
        }

        self._print_summary(report)

        return report

    def _map_to_continents(self, analysis: Dict):
        """Mapeia hadrons para continentes"""
        # Mapeamento continente
        continent_mapping = {
            'Domain': ['Entity', 'AggregateRoot', 'ValueObject', 'DomainService'],
            'Application': ['ApplicationService', 'CommandHandler', 'QueryHandler', 'UseCase'],
            'Infrastructure': ['RepositoryImpl', 'ExternalService', 'MessageBroker'],
            'Interface': ['APIHandler', 'Controller', 'Endpoint', 'View']
        }

        # Processa os hadrons detectados
        for file_data in analysis.get('files', []):
            if 'hadron_details' in file_data:
                for hadron in file_data['hadron_details']:
                    hadron_type = hadron['type']
                    confidence = hadron['confidence']

                    # Encontra o continente
                    continent = 'Unknown'
                    for cont_name, hadron_types in continent_mapping.items():
                        if hadron_type in hadron_types:
                            continent = cont_name
                            break

                    if continent != 'Unknown':
                        if continent not in self.discovered['continents']:
                            self.discovered['continents'][continent] = {
                                'count': 0,
                                'confidence_sum': 0,
                                'files': []
                            }

                        self.discovered['continents'][continent]['count'] += 1
                        self.discovered['continents'][continent]['confidence_sum'] += confidence
                        self.discovered['continents'][continent]['files'].append(file_data['file_path'])

        # Calcula confiança média
        for continent_data in self.discovered['continents'].values():
            continent_data['confidence'] = (
                continent_data['confidence_sum'] / continent_data['count']
                if continent_data['count'] > 0 else 0
            )

    def _refine_hadrons(self):
        """Refina identificação de hadrons com padrões táticos"""
        # Padrões específicos para refinar
        hadron_patterns = {
            'Entity': {
                'keywords': ['entity', 'model', 'domain', 'aggregate'],
                'structural': ['class', 'dataclass', 'type'],
                'behavioral': ['__init__', 'equals', 'hash']
            },
            'CommandHandler': {
                'keywords': ['command', 'create', 'save', 'delete', 'update', 'handle'],
                'behavioral': ['mutates', 'modifies', 'persistence'],
                'return_type': ['void', 'no_return', 'None']
            },
            'QueryHandler': {
                'keywords': ['query', 'find', 'get', 'search', 'list', 'retrieve'],
                'behavioral': ['returns', 'reads', 'select'],
                'side_effects': False
            },
            'Repository': {
                'keywords': ['repository', 'dao', 'storage', 'persistence'],
                'structural': ['interface', 'abstract'],
                'operations': ['save', 'find', 'delete', 'update']
            },
            'APIHandler': {
                'keywords': ['controller', 'api', 'endpoint', 'rest'],
                'structural': ['@', 'mapping', 'request', 'response'],
                'protocols': ['http', 'json', 'xml']
            },
            'TestFunction': {
                'keywords': ['test', 'spec', 'it', 'describe', 'assert'],
                'structural': ['def test_', '@test'],
                'isolated': ['mock', 'stub', 'fixture']
            }
        }

        # Aplica refinamento nos hadrons descobertos
        for continent_data in self.discovered['continents'].values():
            for file_path in continent_data['files']:
                try:
                    content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                    content_lower = content.lower()

                    for hadron_name, patterns in hadron_patterns.items():
                        # Verifica correspondência forte
                        score = 0
                        for keyword in patterns['keywords']:
                            if keyword in content_lower:
                                score += 0.3
                        for structural in patterns['structural']:
                            if structural in content_lower:
                                score += 0.2
                        for behavioral in patterns['behavioral']:
                            if behavioral in content_lower:
                                score += 0.1

                        if score > 0.5:
                            hadron_id = f"{hadron_name}_{len(self.discovered['hadrons'])}"
                            self.discovered['hadrons'][hadron_id] = {
                                'type': hadron_name,
                                'confidence': min(1.0, score),
                                'file': file_path,
                                'continent': None  # Seria calculado
                            }

                except:
                    continue

    def _extract_subhadrons(self, analysis: Dict):
        """Extrai sub-hádrons granulares"""
        subhadron_templates = {
            # Command handlers
            'CreateCommand': ['create', 'save', 'add', 'insert', 'new'],
            'UpdateCommand': ['update', 'modify', 'edit', 'change', 'put'],
            'DeleteCommand': ['delete', 'remove', 'destroy', 'del'],

            # Query handlers
            'FindById': ['find', 'get', 'retrieve', 'fetch'],
            'FindAll': ['all', 'list', 'find_all', 'get_all'],
            'SearchQuery': ['search', 'filter', 'query', 'where'],

            # Repositories
            'SaveOperation': ['save', 'persist', 'store'],
            'FindOperation': ['find', 'get', 'retrieve'],
            'DeleteOperation': ['delete', 'remove', 'purge'],

            # Services
            'BusinessLogic': ['calculate', 'process', 'validate', 'execute'],
            'Orchestration': ['orchestrate', 'coordinate', 'manage'],
            'Transformation': ['transform', 'convert', 'map', 'filter'],

            # API patterns
            'RESTEndpoint': ['get', 'post', 'put', 'delete', 'patch'],
            'GraphQLResolver': ['resolve', 'query', 'mutation'],
            'Serialization': ['serialize', 'deserialize', 'to_json']
        }

        # Analisa arquivos para encontrar sub-hádrons
        for file_data in analysis.get('files', []):
            if 'hadron_details' in file_data:
                content = Path(file_data['file_path']).read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                lines = content.split('\n')

                for hadron in file_data['hadron_details']:
                    hadron_type = hadron['type']
                    hadron_name = hadron['name']
                    line_content = ''

                    # Encontra a linha do hadron
                    for line_num, line in enumerate(lines, 1):
                        if hadron_name.lower() in line.lower():
                            line_content = line.lower()
                            break

                    # Verifica sub-padrões
                    for subhadron_name, keywords in subhadron_templates.items():
                        score = 0
                        for keyword in keywords:
                            if keyword in line_content:
                                score += 0.25

                        if score > 0.5:
                            subhadron_id = f"{hadron_type}_{subhadron_name}_{len(self.discovered['subhadrons'])}"
                            self.discovered['subhadrons'][subhadron_id] = {
                                'parent_hadron': hadron_type,
                                'sub_type': subhadron_name,
                                'confidence': min(1.0, score),
                                'file': file_data['file_path'],
                                'line': hadron_name
                            }

    def _generate_strategic_map(self) -> Dict:
        """Gera mapa estratégico da descoberta"""
        strategic_map = {
            'continents': {},
            'coverage': {
                'total_possible': 4,  # 4 continentes definidos
                'discovered': len(self.discovered['continents']),
                'percentage': (len(self.discovered['continents']) / 4) * 100
            },
            'hierarchy': {
                'levels': 3,
                'distribution': {
                    'continents': len(self.discovered['continents']),
                    'hadrons': len(self.discovered['hadrons']),
                    'subhadrons': len(self.discovered['subhadrons'])
                }
            }
        }

        # Detalhes dos continentes
        for continent_id, continent_data in self.discovered['continents'].items():
            strategic_map['continents'][continent_id] = {
                'elements': continent_data['count'],
                'avg_confidence': continent_data['confidence'],
                'file_count': len(set(continent_data['files'])),
                'diversity': len(set(Path(f).suffix for f in continent_data['files']))
            }

        return strategic_map

    def _generate_insights(self) -> List[Dict]:
        """Gera insights estratégicos"""
        insights = []

        # Cobertura continental
        coverage = self.discovered['continents']
        if len(coverage) < 2:
            insights.append({
                "type": "continental_gaps",
                "severity": "high",
                "message": f"Apenas {len(coverage)} continente(s) detectados",
                "recommendation": "Revisar arquitetura para melhor delimitação de domínios"
            })

        # Diversidade de hádrons
        hadron_types = set(h['type'] for h in self.discovered['hadrons'].values())
        if len(hadron_types) < 3:
            insights.append({
                "type": "low_diversity",
                "severity": "medium",
                "message": f"Pouca diversidade de hádrons ({len(hadron_types)} tipos)",
                "recommendation": "Considerar aplicar mais padrões arquiteturais"
            })

        # Granularidade
        if len(self.discovered['subhadrons']) > len(self.discovered['hadrons']) * 3:
            insights.append({
                "type": "high_granularity",
                "severity": "positive",
                "message": "Alta granularidade detectada (sub-hádrons > 3x hádrons)",
                "recommendation": "Bom nível de detalhe para análise"
            })

        return insights

    def _print_summary(self, report: Dict):
        """Imprime resumo da descoberta"""
        print(f"\n📊 STRATEGIC DISCOVERY SUMMARY")
        print(f"===============================")
        print(f"📁 Repository: {Path(report['repository_path']).name}")
        print(f"⏱️  Duration: {report['duration_seconds']:.2f}s")
        print()

        # Continents
        print(f"🌍 CONTINENTAL LEVEL:")
        coverage = report['discovery_levels']['continents']
        total = report['strategic_map']['coverage']['total_possible']
        print(f"  • Descobertos: {coverage}/{total} ({report['strategic_map']['coverage']['percentage']:.1f}%)")

        for continent_id, data in report['strategic_map']['continents'].items():
            print(f"    ◦ {continent_id}: {data['elements']} elementos, "
                  f"confiança {data['avg_confidence']:.1%}")

        # Hádrons
        print(f"\n⚛️  HADRONIC LEVEL:")
        hadron_level = report['discovery_levels']['hadrons']
        hadron_types = {}
        for h in self.discovered['hadrons'].values():
            hadron_types[h['type']] = hadron_types.get(h['type'], 0) + 1

        for hadron_type, count in sorted(hadron_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    ◦ {hadron_type}: {count}")

        # Sub-hádrons
        print(f"\n🔍 SUB-HADRONS STRATEGIC:")
        subhadron_level = report['discovery_levels']['subhadrons']
        sub_types = {}
        for s in self.discovered['subhadrons'].values():
            sub_types[s['sub_type']] = sub_types.get(s['sub_type'], 0) + 1

        for sub_type, count in sorted(sub_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    ◦ {sub_type}: {count}")

        # Insights
        print(f"\n💡 STRATEGIC INSIGHTS:")
        for insight in report['insights']:
            icon = "⚠️" if insight['severity'] == 'high' else "💡"
            print(f"  {icon} {insight['message']}")
            if insight.get('recommendation'):
                print(f"     → {insight['recommendation']}")

        print(f"\n🎯 HIERARCHY DISTRIBUTION:")
        hierarchy = report['strategic_map']['hierarchy']['distribution']
        print(f"  • Continents: {hierarchy['continents']}")
        print(f"  • Hadrons: {hierarchy['hadrons']}")
        print(f"  • Sub-hádrons: {hierarchy['subhadrons']}")

        print(f"\n✅ Discovery Complete!")
        print(f"🌍 → ⚛️  → 🔍 : Stratified analysis achieved")
        print(f"===============================")

# Execução principal
if __name__ == "__main__":
    discovery = SimpleStrategicDiscovery()

    # Descobre no diretório atual
    repo_path = Path(__file__).parent
    report = discovery.discover_in_repository(repo_path)

    # Salva relatório
    timestamp = int(time.time())
    report_path = Path(f"/tmp/strategic_discovery_{timestamp}.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n💾 Report saved to: {report_path}")
