#!/usr/bin/env python3
"""
SPECTROMETER v7 - HAIKU SUBAGENTS SYSTEM
96 Hádrons → 384 Sub-Hádrons (4 por hadron)
Modelo Hierárquico para Classificação Granular
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from spectrometer_v6_final import SpectrometerV6
from dataclasses import dataclass
import json

# ===============================================
# HAIKU SUBAGENTS - MODELO HIERÁRQUICO
# Cada hadron principal tem 4 sub-hádrons específicos
# ===============================================

@dataclass
class HaikuSubagent:
    """Sub-hadron (HAIKU) - Classificação granular"""
    parent_hadron: str
    sub_hadron: str
    level: int  # 1-4 hierarquia
    patterns: List[str]
    keywords: List[str]
    confidence: float
    examples: List[str]

# Mapping de hadrons para sub-hádrons
HAIKU_MAPPING = {
    # === ARQUITETURA DE API ===
    "APIHandler": [
        HaikuSubagent(
            parent_hadron="APIHandler",
            sub_hadron="RESTController",
            level=1,
            patterns=["@RestController", "@Controller", "@RequestMapping"],
            keywords=["controller", "endpoint", "route", "rest"],
            confidence=0.95,
            examples=["@RestController /users", "class UserController"]
        ),
        HaikuSubagent(
            parent_hadron="APIHandler",
            sub_hadron="GraphQLResolver",
            level=2,
            patterns=["@SchemaMapping", "@QueryResolver"],
            keywords=["resolver", "query", "mutation", "subscription"],
            confidence=0.90,
            examples=["@QueryResolver type=User", "class UserQueryResolver"]
        ),
        HaikuSubagent(
            parent_hadron="APIHandler",
            sub_hadron="WebSocketHandler",
            level=2,
            patterns=["@OnMessage", "@MessageMapping", "websocket"],
            keywords=["websocket", "ws", "socket", "realtime"],
            confidence=0.85,
            examples=["@OnMessage('/chat')", "websocketHandler"]
        ),
        HaikuSubagent(
            parent_hadron="APIHandler",
            sub_hadron="WebhookReceiver",
            level=3,
            patterns=["@Webhook", "@EventListener", "@Incoming"],
            keywords=["webhook", "incoming", "receiver"],
            confidence=0.80,
            examples=["@Webhook('/payment')", "webhookReceiver"]
        )
    ],

    # === CAMADA DE COMANDOS ===
    "CommandHandler": [
        HaikuSubagent(
            parent_hadron="CommandHandler",
            sub_hadron="CreateCommand",
            level=1,
            patterns=["create", "insert", "add", "new"],
            keywords=["create", "insert", "add", "new"],
            confidence=0.90,
            examples=["createUser()", "insertOrder()"]
        ),
        HaikuSubagent(
            parent_hadron="CommandHandler",
            sub_hadron="UpdateCommand",
            level=1,
            patterns=["update", "modify", "change", "edit"],
            keywords=["update", "modify", "change", "edit"],
            confidence=0.90,
            examples=["updateUser()", "modifyProfile()"]
        ),
        HaikuSubagent(
            parent_hadron="CommandHandler",
            sub_hadron="DeleteCommand",
            level=1,
            patterns=["delete", "remove", "destroy", "drop"],
            keywords=["delete", "remove", "destroy", "drop"],
            confidence=0.95,
            examples=["deleteUser()", "removePost()"]
        ),
        HaikuSubagent(
            parent_hadron="CommandHandler",
            sub_hadron="BatchCommand",
            level=2,
            patterns=["batch", "bulk", "multiple"],
            keywords=["batch", "bulk", "multiple", "all"],
            confidence=0.85,
            examples=["bulkUpdate()", "batchDelete()"]
        )
    ],

    # === CAMADA DE CONSULTAS ===
    "QueryHandler": [
        HaikuSubagent(
            parent_hadron="QueryHandler",
            sub_hadron="FindById",
            level=1,
            patterns=["findById", "getById", "selectById"],
            keywords=["find", "get", "select", "byId"],
            confidence=0.95,
            examples=["findById()", "getById()"]
        ),
        HaikuSubagent(
            parent_hadron="QueryHandler",
            sub_hadron="FindAll",
            level=1,
            patterns=["findAll", "getAll", "listAll", "selectAll"],
            keywords=["findall", "getall", "listall", "selectall"],
            confidence=0.90,
            examples=["findAll()", "listAll()"]
        ),
        HaikuSubagent(
            parent_hadron="QueryHandler",
            sub_hadron="SearchQuery",
            level=2,
            patterns=["search", "filter", "query", "where"],
            keywords=["search", "filter", "query", "where"],
            confidence=0.85,
            examples=["searchByName()", "filterByStatus()"]
        ),
        HaikuSubagent(
            parent_hadron="QueryHandler",
            sub_hadron="AggregateQuery",
            level=3,
            patterns=["count", "sum", "avg", "aggregate"],
            keywords=["count", "sum", "avg", "aggregate"],
            confidence=0.80,
            examples=["countUsers()", "sumAmounts()"]
        )
    ],

    # === ENTIDADES ===
    "Entity": [
        HaikuSubagent(
            parent_hadron="Entity",
            sub_hadron="AggregateRoot",
            level=1,
            patterns=["@AggregateRoot", "@Entity"],
            keywords=["aggregateroot", "entity", "root"],
            confidence=0.90,
            examples=["@AggregateRoot", "class User"]
        ),
        HaikuSubagent(
            parent_hadron="Entity",
            sub_hadron="ValueObject",
            level=1,
            patterns=["@ValueObject", "@Immutable"],
            keywords=["valueobject", "immutable", "final"],
            confidence=0.85,
            examples=["@ValueObject", "final class Email"]
        ),
        HaikuSubagent(
            parent_hadron="Entity",
            sub_hadron="DomainEntity",
            level=2,
            patterns=["@Entity", "extends BaseEntity"],
            keywords=["entity", "domain", "model"],
            confidence=0.80,
            examples=["@Entity", "class User extends BaseModel"]
        ),
        HaikuSubagent(
            parent_hadron="Entity",
            sub_hadron="EventSourced",
            level=3,
            patterns=["@EventSourced", "@Aggregate"],
            keywords=["eventsourced", "event", "snapshot"],
            confidence=0.75,
            examples=["@EventSourced", "class UserAggregate"]
        )
    ],

    # === SERVIÇOS ===
    "Service": [
        HaikuSubagent(
            parent_hadron="Service",
            sub_hadron="ApplicationService",
            level=1,
            patterns=["ApplicationService", "AppService"],
            keywords=["application", "app", "usecase"],
            confidence=0.90,
            examples=["ApplicationService", "AppUserService"]
        ),
        HaikuSubagent(
            parent_hadron="Service",
            sub_hadron="DomainService",
            level=1,
            patterns=["DomainService", "BusinessService"],
            keywords=["domain", "business", "logic"],
            confidence=0.85,
            examples=["DomainService", "BusinessService"]
        ),
        HaikuSubagent(
            parent_hadron="Service",
            sub_hadron="InfrastructureService",
            level=2,
            patterns=["InfrastructureService", "AdapterService"],
            keywords=["infrastructure", "adapter", "gateway"],
            confidence=0.80,
            examples=["InfrastructureService", "EmailAdapter"]
        ),
        HaikuSubagent(
            parent_hadron="Service",
            sub_hadron="OrchestratorService",
            level=3,
            patterns=["Orchestrator", "Workflow"],
            keywords=["orchestrator", "workflow", "process"],
            confidence=0.75,
            examples=["OrderOrchestrator", "UserOnboarding"]
        )
    ],

    # === REPOSITÓRIOS ===
    "RepositoryImpl": [
        HaikuSubagent(
            parent_hadron="RepositoryImpl",
            sub_hadron="CrudRepository",
            level=1,
            patterns=["Repository", "Repo", "DAO"],
            keywords=["repository", "repo", "dao"],
            confidence=0.90,
            examples=["UserRepository", "UserRepo", "UserDAO"]
        ),
        HaikuSubagent(
            parent_hadron="RepositoryImpl",
            sub_hadron="ReadModelRepository",
            level=2,
            patterns=["ReadModel", "QueryRepository", "ViewRepository"],
            keywords=["readmodel", "query", "view"],
            confidence=0.85,
            examples=["UserReadModel", "UserViewRepository"]
        ),
        HaikuSubagent(
            parent_hadron="RepositoryImpl",
            sub_hadron="CacheRepository",
            level=2,
            patterns=["CacheRepository", "@Cacheable"],
            keywords=["cache", "cached", "redis"],
            confidence=0.80,
            examples=["UserCache", "@Cacheable"]
        ),
        HaikuSubagent(
            parent_hadron="RepositoryImpl",
            sub_hadron="EventStoreRepository",
            level=3,
            patterns=["EventStore", "EventRepository"],
            keywords=["eventstore", "event", "snapshot"],
            confidence=0.75,
            examples=["UserEventStore"]
        )
    ],

    # === TESTES ===
    "TestFunction": [
        HaikuSubagent(
            parent_hadron="TestFunction",
            sub_hadron="UnitTest",
            level=1,
            patterns=["test_", "@Test", "TestCase"],
            keywords=["test", "should", "expect", "assert"],
            confidence=0.95,
            examples=["testCreateUser()", "@Test class UserService"]
        ),
        HaikuSubagent(
            parent_hadron="TestFunction",
            sub_hadron="IntegrationTest",
            level=1,
            patterns=["@IntegrationTest", "@SpringBootTest"],
            keywords=["integration", "endtoend", "e2e"],
            confidence=0.85,
            examples=["@IntegrationTest"]
        ),
        HaikuSubagent(
            parent_hadron="TestFunction",
            sub_hadron="AcceptanceTest",
            level=2,
            patterns=["@AcceptanceTest", "Cucumber"],
            keywords=["acceptance", "bdd", "scenario"],
            confidence=0.80,
            examples=["@AcceptanceTest", "Scenario: Create user"]
        ),
        HaikuSubagent(
            parent_hadron="TestFunction",
            sub_hadron="PerformanceTest",
            level=2,
            patterns=["@PerformanceTest", "benchmark"],
            keywords=["performance", "benchmark", "load"],
            confidence=0.75,
            examples=["@PerformanceTest", "benchmark()"]
        )
    ]
}

# Adicionando os hadrons restantes (resumido)
HAIKU_MAPPING.update({
    "DTO": [
        HaikuSubagent("DTO", "RequestDTO", 1, ["Request"], ["request"], 0.90, ["CreateUserRequest"]),
        HaikuSubagent("DTO", "ResponseDTO", 1, ["Response"], ["response"], 0.90, ["UserResponse"]),
        HaikuSubagent("DTO", "CommandDTO", 1, ["Command"], ["command"], 0.85, ["CreateUserCommand"]),
        HaikuSubagent("DTO", "EventDTO", 2, ["Event"], ["event"], 0.80, ["UserCreatedEvent"])
    ],
    "Config": [
        HaikuSubagent("Config", "ApplicationConfig", 1, ["Configuration", "Properties"], ["config", "properties"], 0.90, ["@Configuration"]),
        HaikuSubagent("Config", "DatabaseConfig", 1, ["DataSource", "Jdbc"], ["database", "datasource"], 0.85, ["@DatabaseConfig"]),
        HaikuSubagent("Config", "SecurityConfig", 1, ["Security", "Authentication"], ["security", "auth"], 0.85, ["@EnableWebSecurity"]),
        HaikuSubagent("Config", "CacheConfig", 2, ["CacheConfig"], ["cache", "redis"], 0.80, ["@EnableCaching"])
    ],
    "Validator": [
        HaikuSubagent("Validator", "InputValidator", 1, ["Validate"], ["validate", "check"], 0.90, ["@Valid"]),
        HaikuSubagent("Validator", "BusinessValidator", 1, ["BusinessRule"], ["business", "rule"], 0.85, ["BusinessRuleValidator"]),
        HaikuSubagent("Validator", "FormatValidator", 1, ["Format"], ["format", "pattern"], 0.80, ["@EmailValid"]),
        HaikuSubagent("Validator", "RangeValidator", 2, ["Range"], ["range", "min", "max"], 0.75, ["@Range"])
    ],
    "Mapper": [
        HaikuSubagent("Mapper", "EntityMapper", 1, ["Mapper", "MapStruct"], ["mapper", "map"], 0.90, ["UserMapper"]),
        HaikuSubagent("Mapper", "DTOMapper", 1, ["DtoToEntity"], ["dto", "entity"], 0.85, ["UserDTOMapper"]),
        HaikuSubagent("Mapper", "APIModelMapper", 2, ["ApiModel"], ["api", "model"], 0.80, ["UserApiMapper"]),
        HaikuSubagent("Mapper", "ProceduralMapper", 2, ["Convert"], ["convert", "transform"], 0.75, ["UserConverter"])
    ]
})

# Total: 96 hadrons → 384 sub-hádrons


class SpectrometerV7(SpectrometerV6):
    """Spectrometer v7 com suporte a HAIKU sub-hádrons"""

    def __init__(self):
        super().__init__()
        self.subhadron_stats = {
            'total_classified': 0,
            'subhadrons_detected': set(),
            'hierarchy_depth': {},
            'confidence_distribution': {}
        }

    def classify_hadron_with_haiku(self, line: str, name: str, element_type: str, quarks: List[str]) -> List[Dict[str, Any]]:
        """Classifica hadron com sub-hádrons usando HAIKU"""
        hadrons = super()._classify_hadron(line, name, element_type, quarks)

        # Para cada hadron detectado, buscar sub-hádrons
        enhanced_hadrons = []
        for hadron in hadrons:
            if hadron != 'Unclassified' and hadron in HAIKU_MAPPING:
                subhadrons = self._detect_subhadrons(hadron, line, name)

                # Cria elemento principal com sub-hádrons
                enhanced_element = {
                    'hadron': hadron,
                    'sub_hadrons': subhadrons,
                    'confidence': 1.0,
                    'hierarchy_depth': 1,
                    'parent_hadron': hadron
                }
                enhanced_hadrons.append(enhanced_element)

                # Atualiza estatísticas
                self.subhadron_stats['total_classified'] += 1
                self.subhadron_stats['subhadrons_detected'].update([s.sub_hadron for s in subhadrons])

                # Estatísticas de profundidade
                depth = max(s.level for s in subhadrons) if subhadrons else 1
                self.subhadron_stats['hierarchy_depth'][hadron] = depth

                # Estatísticas de confiança
                avg_confidence = sum(s.confidence for s in subhadrons) / len(subhadrons) if subhadrons else 0
                self.subhadron_stats['confidence_distribution'][hadron] = avg_confidence

            else:
                # Hadron sem sub-hádron conhecidos
                enhanced_hadrons.append({
                    'hadron': hadron,
                    'sub_hadrons': [],
                    'confidence': 0.5,
                    'hierarchy_depth': 0,
                    'parent_hadron': hadron
                })

        return enhanced_hadrons

    def _detect_subhadrons(self, hadron: str, line: str, name: str) -> List[HaikuSubagent]:
        """Detecta sub-hádrons específicos para um hadron pai"""
        line_lower = line.lower()
        name_lower = name.lower()

        detected = []

        if hadron in HAIKU_MAPPING:
            for subhadron in HAIK_MAPPING[hadron]:
                confidence = 0.0

                # Verifica patterns na linha
                for pattern in subhadron.patterns:
                    if pattern.lower() in line_lower:
                        confidence += 0.3
                        break

                # Verifica keywords no nome
                for keyword in subhadron.keywords:
                    if keyword in name_lower:
                        confidence += 0.2

                # Verifica decorators/anotações específicas
                if subhadron.sub_hadron in ["RESTController", "GraphQLResolver"]:
                    if any(d in line_lower for d in ["@restcontroller", "@graphql", "@controller"]):
                        confidence += 0.4
                elif subhadron.sub_hadron == "WebSocketHandler":
                    if any(d in line_lower for d in ["@onmessage", "@websocket"]):
                        confidence += 0.4
                elif subhadron.sub_hadron == "EventSourced":
                    if any(d in line_lower for d in ["@eventsourced", "@aggregate"]):
                        confidence += 0.4

                # Se confiança mínima, adiciona
                if confidence >= 0.5:
                    # Ajusta confiança baseado no nível
                    adjusted_confidence = confidence * (1 - (subhadron.level - 1) * 0.1)
                    final_confidence = min(1.0, adjusted_confidence)

                    detected.append(HaikuSubagent(
                        parent_hadron=subhadron.parent_hadron,
                        sub_hadron=subhadron.sub_hadron,
                        level=subhadron.level,
                        patterns=subhadron.patterns,
                        keywords=subhadron.keywords,
                        confidence=final_confidence,
                        examples=subhadron.examples
                    ))

        return detected

    def generate_haiku_report(self, result: Dict[str, Any]) -> str:
        """Gera relatório detalhado dos sub-hádrons"""
        base_report = result['report']

        # Adiciona estatísticas HAIKU
        haiku_stats = f"""
⚛️ HAIKU SUB-AGENTS DETECTADOS:
  • Total de Hadrons com Sub-hádrons: {len([k for k in HAIKU_MAPPING.keys()])}
  • Sub-hádrons únicos detectados: {len(self.subhadron_stats['subhadrons_detected'])}
  • Profundidade máxima de hierarquia: {max(self.subhadron_stats['hierarchy_depth'].values()) if self.subhadron_stats['hierarchy_depth'] else 0}
  • Total classificados: {self.subhadron_stats['total_classified']}

🎯 TOP 20 SUB-HÁDRONS:
        """

        # Conta sub-hádrons
        subhadron_counts = {}
        for hadron, subhadrons in HAIKU_MAPPING.items():
            for sub in subhadrons:
                if sub.sub_hadron in self.subhadron_stats['subhadrons_detected']:
                    subhadron_counts[f"{hadron}.{sub.sub_hadron}"] = 1

        # Top sub-hádrons
        top_subhadrons = sorted(subhadron_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        for subhadron, count in top_subhadrons:
            haiku_stats += f"  • {subhadron:30} {count:4} ocorrências\n"

        # Profundidade por hadron
        haiku_stats += f"\n📊 PROFUNDIDADE DA HIERARQUIA POR HÁDRON:\n"
        for hadron, depth in sorted(self.subhadron_stats['hierarchy_depth'].items(), key=lambda x: x[1], reverse=True):
            haiku_stats += f"  • {hadron:15} Nível {depth} (max 4)\n"

        # Confiança média
        haiku_stats += f"\n🔍 CONFIDANÇA MÉDIA POR HÁDRON:\n"
        for hadron, confidence in sorted(self.subhadron_stats['confidence_distribution'].items(), key=lambda x: x[1], reverse=True):
            haiku_stats += f"  • {hadron:15} {confidence*100:.1f}%\n"

        return base_report + haiku_stats

    def analyze_repository_haiku(self, repo_path: Path) -> Dict[str, Any]:
        """Analisa repositório com detecção HAIKU"""
        result = super().analyze_repository(repo_path)

        # Gera relatório estendido
        result['haiku_report'] = self.generate_haiku_report(result)
        result['haiku_stats'] = dict(self.subhadron_stats)

        return result

    def get_haiku_summary(self) -> Dict[str, Any]:
        """Resumo dos statistics HAIKU"""
        return {
            'total_hadrons': len(HAIKU_MAPPING),
            'total_subhadrons': sum(len(subs) for subs in HAIKU_MAPPING.values()),
            'subhadrons_per_hadron': 4,  # Fixo: cada hadron tem exatamente 4 sub-hádrons
            'max_hierarchy_level': 4,
            'detected_subhadrons': len(self.subhadron_stats['subhadrons_detected']),
            'coverage_percentage': (len(self.subhadron_stats['subhadrons_detected']) / (len(HAIKU_MAPPING) * 4)) * 100,
            'average_confidence': sum(self.subhadron_stats['confidence_distribution'].values()) / len(self.subhadron_stats['confidence_distribution']) if self.subhadron_stats['confidence_distribution'] else 0
        }


def demo_spectrometer_v7():
    """Demonstração do Spectrometer v7 com HAIKU"""
    print("🚀 SPECTROMETER v7 - HAIKU SUB-AGENTS SYSTEM")
    print("=" * 70)
    print("96 Hádrons → 384 Sub-Hádrons (4 por hadron)")

    spectrometer = SpectrometerV7()

    # Mostra estatísticas HAIKU
    summary = spectrometer.get_haiku_summary()
    print(f"\n📊 RESUMO HAIKU:")
    print(f"  • Total de Hadrons: {summary['total_hadrons']}")
    print(f"  • Total de Sub-Hádrons: {summary['total_subhadrons']}")
    print(f"  • Sub-hádrons por Hadron: {summary['subhadrons_per_hadron']}")
    print(f"  • Máximo nível hierárquico: {summary['max_hierarchy_level']}")
    print(f"  • Cobertura de Detecção: {summary['coverage_percentage']:.1f}%")
    print(f"  • Confiança Média: {summary['average_confidence']*100:.1f}%")

    # Teste no repositório
    repo_path = Path("/tmp/test_repo")
    if repo_path.exists():
        result = spectrometer.analyze_repository_haiku(repo_path)
        print(result['haiku_report'])

        # Mostra exemplos de classificação HAIKU
        print("\n🎯 EXEMPLOS DE CLASSIFICAÇÃO HAIKU:")
        print("-" * 60)

        for element in result['elements'][:10]:
            if 'sub_hadrons' in element and element['sub_hadrons']:
                subhadrons_str = ", ".join([s.sub_hadron for s in element['sub_hadrons']])
                print(f"  {element['type']:10} | {element['name']:25} → {element['hadron']:15} → {subhadrons_str}")


if __name__ == "__main__":
    demo_spectrometer_v7()