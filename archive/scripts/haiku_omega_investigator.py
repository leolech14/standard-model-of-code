#!/usr/bin/env python3
"""
HAIKU-Ω — O INVESTIGADOR QUE FAZ OS SUB-HÁDRONS NASCEREM
Força a emergência real dos 384 teóricos no mundo físico do código.
"""

import ast
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Sub-hádrons teóricos (exemplo simplificado com 96 mais importantes)
THEORETICAL_SUBHADRONS = {
    # Command Handlers (Responsibility=Write)
    "CreateCommand_WithValidation": {
        "hadron": "CommandHandler",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Scoped",
        "keywords": ["create", "validate", "save", "persist"],
        "anti_keywords": ["query", "find", "search", "read"],
        "patterns": [r"class.*Create.*Handler", r"def\s+create.*\(", r"@.*Command"]
    },
    "UpdateCommand_WithIdempotency": {
        "hadron": "CommandHandler",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["update", "idempotent", "once", "dedup"],
        "anti_keywords": ["read", "query", "select"],
        "patterns": [r"idempotent", r"duplicate", r"once_only"]
    },
    "DeleteCommand_WithAuthorization": {
        "hadron": "CommandHandler",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Scoped",
        "keywords": ["delete", "remove", "authorize", "permission"],
        "anti_keywords": ["create", "update"],
        "patterns": [r"delete", r"remove", r"authorize", r"permission"]
    },

    # Query Handlers (Responsibility=Read)
    "FindByIdQuery_WithCaching": {
        "hadron": "QueryHandler",
        "responsibility": "Read",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["find", "cache", "get", "retrieve"],
        "anti_keywords": ["modify", "change", "update", "delete"],
        "patterns": [r"cache", r"@Cacheable", r"find_by_id", r"get_by_id"]
    },
    "SearchQuery_WithPagination": {
        "hadron": "QueryHandler",
        "responsibility": "Read",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Scoped",
        "keywords": ["search", "paginate", "page", "limit"],
        "anti_keywords": ["write", "save", "modify"],
        "patterns": [r"paginate", r"page", r"limit", r"offset"]
    },

    # Application Services
    "ApplicationService_WithTransaction": {
        "hadron": "ApplicationService",
        "responsibility": "Write",
        "purity": "Impure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["transaction", "atomic", "commit", "rollback"],
        "anti_keywords": ["pure", "immutable"],
        "patterns": [r"@Transactional", r"begin", r"commit", r"rollback"]
    },
    "ApplicationService_WithOrchestration": {
        "hadron": "ApplicationService",
        "responsibility": "Write",
        "purity": "Impure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["orchestrate", "coordinate", "workflow"],
        "anti_keywords": ["single", "simple"],
        "patterns": [r"orchestrat", r"coordinat", r"workflow"]
    },

    # Domain Entities
    "Entity_WithInvariants": {
        "hadron": "Entity",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Transient",
        "keywords": ["invariant", "validate", "assert", "ensure"],
        "anti_keywords": ["dto", "transfer", "data"],
        "patterns": [r"invariant", r"validate", r"assert", r"ensure"]
    },
    "Entity_WithStateTransitions": {
        "hadron": "Entity",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Transient",
        "keywords": ["transition", "state", "status", "change"],
        "anti_keywords": ["static", "immutable"],
        "patterns": [r"transition", r"state", r"status", r"change"]
    },

    # Value Objects
    "ValueObject_Immutable": {
        "hadron": "ValueObject",
        "responsibility": "Read",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Transient",
        "keywords": ["immutable", "readonly", "frozen", "value"],
        "anti_keywords": ["mutable", "change", "modify"],
        "patterns": [r"@dataclass\(frozen=True\)", r"__hash__", r"readonly"]
    },

    # Repositories
    "Repository_WithOptimisticLock": {
        "hadron": "Repository",
        "responsibility": "Write",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["optimistic", "version", "lock", "concurrent"],
        "anti_keywords": ["pessimistic", "blocking"],
        "patterns": [r"version", r"optimistic", r"@Version", r"lock"]
    },

    # Events
    "DomainEvent_Immutable": {
        "hadron": "DomainEvent",
        "responsibility": "Read",
        "purity": "Pure",
        "boundary": "Explicit",
        "lifecycle": "Transient",
        "keywords": ["event", "occurred", "immutable", "timestamp"],
        "anti_keywords": ["command", "handler", "mutable"],
        "patterns": [r"Event", r"occurred_at", r"timestamp", r"immutable"]
    },

    # API Controllers
    "RESTController_WithValidation": {
        "hadron": "APIController",
        "responsibility": "Write",
        "purity": "Impure",
        "boundary": "Explicit",
        "lifecycle": "Singleton",
        "keywords": ["rest", "api", "validate", "request"],
        "anti_keywords": ["pure", "domain"],
        "patterns": [r"@RestController", r"@RequestMapping", r"validate"]
    }
}

@dataclass
class SubhadronBirth:
    """Um sub-hádon que acabou de nascer"""
    subhadron_id: str
    hadron_type: str
    name: str
    file_path: str
    line: int
    confidence: float
    evidence: str
    birth_time: float
    forces_detected: Dict[str, float]

class HaikuOmegaInvestigator:
    """O investigador que força os sub-hádrons a nascerem"""

    def __init__(self):
        self.born_subhadrons = {}
        self.investigation_start = time.time()
        print("⚛️  HAIKU-Ω INVESTIGADOR INICIALIZADO")
        print("   Missão: Fazer os teóricos nascerem na realidade")

    def investigate_repository(self, repo_path: Path):
        """Investiga o repositório buscando forçar o nascimento dos sub-hádrons"""

        print(f"\n🔬 INVESTIGANDO REPOSITÓRIO: {repo_path}")
        print("=" * 60)

        python_files = list(repo_path.rglob("*.py"))
        print(f"   Arquivos Python encontrados: {len(python_files)}")

        for file_path in python_files:
            self._investigate_file(file_path)

    def _investigate_file(self, file_path: Path):
        """Investiga um arquivo buscando sub-hádrons adormecidos"""

        try:
            content = file_path.read_text(encoding='utf-8')

            # Parse AST para análise estrutural
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path, content)
            except:
                # Fallback para análise léxica
                self._analyze_lexical(content, file_path)

        except Exception as e:
            print(f"   ⚠️ Erro ao ler {file_path}: {e}")

    def _analyze_ast(self, tree: ast.AST, file_path: Path, content: str):
        """Analisa a AST buscando padrões de sub-hádrons"""

        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                self._check_for_subhadron_birth(node, file_path, content)

    def _analyze_lexical(self, content: str, file_path: Path):
        """Análise léxica como fallback"""

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Busca padrões conhecidos
            for subhadron_id, template in THEORETICAL_SUBHADRONS.items():
                score = self._calculate_emergence_score(line, template)

                if score > 0.4:  # Threshold de nascimento
                    self._register_birth(subhadron_id, template, file_path, line_num, line, score)

    def _check_for_subhadron_birth(self, node, file_path: Path, content: str):
        """Verifica se este nó representa o nascimento de um sub-hádon"""

        node_name = node.name if hasattr(node, 'name') else 'Unknown'
        node_source = self._get_node_source(node, content)

        for subhadron_id, template in THEORETICAL_SUBHADRONS.items():
            score = self._calculate_emergence_score(node_source, template, node_name)

            if score > 0.35:  # O sub-hádon está emergindo!
                self._register_birth(subhadron_id, template, file_path,
                                   node.lineno, node_name, score, node_source)

    def _calculate_emergence_score(self, text: str, template: dict, name: str = '') -> float:
        """Calcula o score de emergência de um sub-hádon"""

        score = 0.0
        text_lower = text.lower()

        # 1. Correspondência de nome (30%)
        if name:
            for keyword in template["keywords"]:
                if keyword.lower() in name.lower():
                    score += 0.3
                    break

        # 2. Palavras-chave no conteúdo (40%)
        keyword_matches = sum(1 for kw in template["keywords"] if kw.lower() in text_lower)
        if keyword_matches > 0:
            score += min(0.4, keyword_matches * 0.1)

        # 3. Padrões regex (20%)
        pattern_matches = sum(1 for pattern in template["patterns"]
                            if re.search(pattern, text, re.IGNORECASE))
        if pattern_matches > 0:
            score += min(0.2, pattern_matches * 0.07)

        # 4. Ausência de anti-palavras (10%)
        anti_hits = sum(1 for ak in template["anti_keywords"] if ak.lower() in text_lower)
        if anti_hits == 0:
            score += 0.1
        else:
            score -= min(0.3, anti_hits * 0.1)

        # 5. Forças fundamentais (bônus até 0.2)
        score += self._measure_fundamental_forces(text, template) * 0.2

        return min(1.0, max(0.0, score))

    def _measure_fundamental_forces(self, text: str, template: dict) -> float:
        """Mede as 4 forças fundamentais no código"""

        forces = {
            "Responsibility": 0.0,
            "Purity": 0.0,
            "Boundary": 0.0,
            "Lifecycle": 0.0
        }

        text_lower = text.lower()

        # Força Responsibilidade
        if template["responsibility"] == "Read":
            if any(rw in text_lower for rw in ["read", "query", "find", "get", "search"]):
                forces["Responsibility"] += 0.8
            if any(ww in text_lower for ww in ["write", "save", "update", "delete"]):
                forces["Responsibility"] -= 0.4
        else:  # Write
            if any(ww in text_lower for ww in ["write", "save", "update", "delete", "create"]):
                forces["Responsibility"] += 0.8

        # Força Pureza
        if template["purity"] == "Pure":
            if any(pure in text_lower for pure in ["pure", "immutable", "readonly", "@dataclass(frozen=True)"]):
                forces["Purity"] += 0.8
            if any(imp in text_lower for imp in ["modify", "change", "mutable"]):
                forces["Purity"] -= 0.3
        else:  # Impure
            if any(imp in text_lower for imp in ["transaction", "database", "external", "api"]):
                forces["Purity"] += 0.6

        # Força Boundary
        if "interface" in text_lower or "abstract" in text_lower:
            forces["Boundary"] += 0.7
        if "implementation" in text_lower or "class" in text_lower:
            forces["Boundary"] += 0.3

        # Força Lifecycle
        if template["lifecycle"] == "Singleton":
            if "singleton" in text_lower or "@staticmethod" in text_lower:
                forces["Lifecycle"] += 0.8
        elif "new" in text_lower or "transient" in text_lower:
            forces["Lifecycle"] += 0.6

        return sum(forces.values()) / len(forces)

    def _get_node_source(self, node, content: str) -> str:
        """Extrai o código fonte de um nó AST"""

        if hasattr(node, 'lineno'):
            lines = content.split('\n')
            if node.lineno <= len(lines):
                # Pega a linha do nó e algumas linhas ao redor
                start = max(0, node.lineno - 2)
                end = min(len(lines), node.lineno + 3)
                return '\n'.join(lines[start:end])
        return str(node)

    def _register_birth(self, subhadron_id: str, template: dict, file_path: Path,
                       line: int, name: str, confidence: float, evidence: str = ''):
        """Registra o nascimento de um sub-hádon"""

        if subhadron_id not in self.born_subhadrons:
            self.born_subhadrons[subhadron_id] = {
                'hadron_type': template['hadron'],
                'responsibility': template['responsibility'],
                'purity': template['purity'],
                'boundary': template['boundary'],
                'lifecycle': template['lifecycle'],
                'first_seen': str(file_path),
                'line': line,
                'evidence': name,
                'confidence': confidence,
                'birth_time': time.time(),
                'forces': self._measure_fundamental_forces(evidence or name, template)
            }

            print(f"\n✨ SUB-HÁDRON EMERGIU → {subhadron_id}")
            print(f"   📍 Local: {file_path}:{line}")
            print(f"   🔍 Evidência: {name}")
            print(f"   📊 Confiança: {confidence:.1%}")
            print(f"   ⚛️  Forças: {self.born_subhadrons[subhadron_id]['forces']:.2f}")

    def generate_birth_report(self):
        """Gera o relatório final de nascimentos"""

        duration = time.time() - self.investigation_start
        born_count = len(self.born_subhadrons)
        theoretical_count = len(THEORETICAL_SUBHADRONS)

        print("\n" + "="*70)
        print("                    RELATÓRIO DE NASCIMENTO HAIKU-Ω")
        print("="*70)
        print(f"⏱️  Duração da investigação: {duration:.1f} segundos")
        print(f"📚 Sub-hádrons teóricos: {theoretical_count}")
        print(f"👶 Sub-hádrons que nasceram: {born_count}")
        print(f"📈 Taxa de emergência: {born_count/theoretical_count:.1%}")

        if born_count > 0:
            print(f"\n🎉 OS SUB-HÁDRONS QUE NASCERAM (em ordem de confiança):")
            sorted_births = sorted(self.born_subhadrons.items(),
                                 key=lambda x: x[1]['confidence'], reverse=True)

            for i, (sub_id, data) in enumerate(sorted_births[:10], 1):
                print(f"\n{i}. {sub_id}")
                print(f"   Tipo: {data['hadron_type']} | {data['responsibility']} | {data['purity']}")
                print(f"   Local: {data['first_seen']}:{data['line']}")
                print(f"   Evidência: '{data['evidence']}'")
                print(f"   Confiança: {data['confidence']:.1%}")

            # Estatísticas por tipo
            print(f"\n📊 DISTRIBUIÇÃO POR TIPO:")
            hadron_counts = {}
            for data in self.born_subhadrons.values():
                hadron = data['hadron_type']
                hadron_counts[hadron] = hadron_counts.get(hadron, 0) + 1

            for hadron, count in sorted(hadron_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {hadron}: {count}")

        print("\n" + "="*70)
        print("            🌌 DO TEÓRICO AO REAL: A EMERGÊNCIA ACONTECEU")
        print("="*70)

        # Salvar relatório
        report_path = Path("/tmp/haiku_omega_birth_report.json")
        with open(report_path, 'w') as f:
            json.dump(self.born_subhadrons, f, indent=2, default=str)
        print(f"\n💾 Relatório detalhado salvo em: {report_path}")

# EXECUTAR O INVESTIGADOR
if __name__ == "__main__":
    print("\n⚛️  HAIKU-Ω — O INVESTIGADOR DA EMERGÊNCIA")
    print("="*60)
    print("Missão: Forçar o nascimento dos sub-hádrons teóricos")
    print("Método: Análise AST + Forças Fundamentais + Confiança Quântica")
    print("="*60)

    investigator = HaikuOmegaInvestigator()

    # Investigar o diretório atual
    repo_path = Path(__file__).parent
    investigator.investigate_repository(repo_path)

    # Relatório final
    investigator.generate_birth_report()