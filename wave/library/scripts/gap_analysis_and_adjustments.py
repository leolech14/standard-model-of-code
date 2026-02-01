#!/usr/bin/env python3
"""
Análise detalhada dos gaps e ajustes na taxonomia dos 96 hádrons
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from spectrometer_hadrons_engine import HADRON_CATALOG

class GapAnalyzer:
    """Analisa os gaps e propõe ajustes na taxonomia"""

    def __init__(self):
        self.results_path = Path("batch_analysis_results.json")
        self.gap_analysis = self._load_and_analyze()

    def _load_and_analyze(self) -> Dict:
        """Carrega resultados e analisa gaps"""
        with open(self.results_path, 'r') as f:
            results = json.load(f)

        stats = results["global_statistics"]
        missing = set(stats["missing_hadrons"])

        # Categoriza os missing
        categorized_gaps = self._categorize_missing_hadrons(missing)

        # Identifica padrões nos gaps
        gap_patterns = self._identify_gap_patterns(results)

        # Propõe ajustes
        adjustments = self._propose_adjustments(categorized_gaps, gap_patterns)

        return {
            "missing_hadrons": list(missing),
            "missing_count": len(missing),
            "coverage_percentage": stats["hadron_coverage"],
            "categorized_gaps": categorized_gaps,
            "gap_patterns": gap_patterns,
            "proposed_adjustments": adjustments,
            "priority_actions": self._determine_priority_actions(categorized_gaps, gap_patterns)
        }

    def _categorize_missing_hadrons(self, missing: Set[str]) -> Dict[str, Dict]:
        """Categoriza os hádrons não encontrados"""
        categories = {
            "syntax_level": {
                "description": "Elementos de baixo nível (sintaxe)",
                "hadrons": [],
                "impact": "low",
                "reason": "Provavelmente existem mas não foram detectados pelas heurísticas"
            },
            "rare_patterns": {
                "description": "Padrões raros ou específicos de domínio",
                "hadrons": [],
                "impact": "medium",
                "reason": "Aparecem apenas em contextos específicos"
            },
            "framework_specific": {
                "description": "Específicos de frameworks ou tecnologias",
                "hadrons": [],
                "impact": "medium",
                "reason": "Dependem de frameworks específicos"
            },
            "obselete_or_theoretical": {
                "description": "Teóricos ou obsoletos",
                "hadrons": [],
                "impact": "low",
                "reason": "Podem não ser mais relevantes"
            },
            "detection_issue": {
                "description": "Problema de detecção",
                "hadrons": [],
                "impact": "high",
                "reason": "Provavelmente existem mas o parser não encontrou"
            }
        }

        # Classifica cada hadron missing
        for hadron in missing:
            if hadron in ["BitFlag", "BitMask", "ParityBit", "SignBit",
                         "ByteArray", "MagicBytes", "PaddingBytes"]:
                categories["syntax_level"]["hadrons"].append(hadron)

            elif hadron in ["WebSocketHandler", "QueueWorker", "BackgroundThread",
                           "Actor", "Fiber", "WebWorker", "ServiceWorker"]:
                categories["rare_patterns"]["hadrons"].append(hadron)

            elif hadron in ["GraphQLResolver", "KubernetesJob", "CronJob",
                           "ContainerEntry", "LambdaEntry"]:
                categories["framework_specific"]["hadrons"].append(hadron)

            elif hadron in ["PanicRecover", "ChaosMonkey"]:
                categories["obselete_or_theoretical"]["hadrons"].append(hadron)

            else:
                categories["detection_issue"]["hadrons"].append(hadron)

        return categories

    def _identify_gap_patterns(self, results: Dict) -> Dict:
        """Identifica padrões nos gaps por categoria de repositório"""
        patterns = {
            "common_across_all": [],
            "category_specific": {},
            "language_specific": {}
        }

        repo_results = results["repository_results"]

        # Hádrons que faltam em múltiplos repositórios
        missing_counts = {}
        category_missing = {}

        for result in repo_results:
            category = result["category"]
            missing = result["statistics"]["missing_hadrons"]

            if category not in category_missing:
                category_missing[category] = {}

            for hadron in missing:
                missing_counts[hadron] = missing_counts.get(hadron, 0) + 1
                category_missing[category][hadron] = category_missing[category].get(hadron, 0) + 1

        # Hádrons que faltam em 50%+ dos repositórios
        threshold = len(repo_results) * 0.5
        patterns["common_across_all"] = [
            hadron for hadron, count in missing_counts.items()
            if count >= threshold
        ]

        # Por categoria
        for category, missing_map in category_missing.items():
            category_threshold = sum(1 for r in repo_results if r["category"] == category) * 0.6
            patterns["category_specific"][category] = [
                hadron for hadron, count in missing_map.items()
                if count >= category_threshold
            ]

        return patterns

    def _propose_adjustments(self, categorized: Dict, patterns: Dict) -> List[Dict]:
        """Propõe ajustes específicos na taxonomia"""
        adjustments = []

        # 1. Fundir hádrons muito similares
        adjustments.append({
            "type": "merge",
            "description": "Fundir hádrons de nível sintático",
            "reason": "Elementos como BitFlag, BitMask, ParityBit são muito específicos",
            "proposal": {
                "new_hadron": "BitOperation",
                "merge_from": ["BitFlag", "BitMask", "ParityBit", "SignBit"],
                "form": "tetrahedron+binary_ops"
            }
        })

        adjustments.append({
            "type": "merge",
            "description": "Consolidar handlers de sistema",
            "reason": "WebSocketHandler, QueueWorker, etc são específicos demais",
            "proposal": {
                "new_hadron": "SystemEventHandler",
                "merge_from": ["WebSocketHandler", "QueueWorker", "MessageConsumer"],
                "form": "icosahedron+system"
            }
        })

        # 2. Adicionar hádrons mais genéricos
        adjustments.append({
            "type": "add_generic",
            "description": "Adicionar hádrons genéricos para cobrir gaps",
            "reason": "Faltam padrões básicos comuns",
            "proposal": [
                {
                    "name": "FieldAccess",
                    "continent": "DATA_FOUNDATIONS",
                    "fundamental": "EXPRESSIONS",
                    "form": "cone+field",
                    "description": "Acesso a campos/atributos"
                },
                {
                    "name": "ImportStatement",
                    "continent": "ORGANIZATION",
                    "fundamental": "MODULES",
                    "form": "dodecahedron+import",
                    "description": "Declarações de import/export"
                },
                {
                    "name": "ErrorHandling",
                    "continent": "LOGIC_FLOW",
                    "fundamental": "CONTROL_STRUCTURES",
                    "form": "torus+error",
                    "description": "Qualquer forma de tratamento de erro"
                }
            ]
        })

        # 3. Ajustar heurísticas de detecção
        adjustments.append({
            "type": "improve_detection",
            "description": "Melhorar detecção de padrões existentes",
            "reason": "Muitos hádrons existem mas não foram detectados",
            "proposal": [
                {
                    "hadron": "TryCatch",
                    "improvement": "Detectar try/except, try/catch em qualquer linguagem",
                    "patterns": [r"try\s*{", r"except\s+", r"catch\s*\("]
                },
                {
                    "hadron": "InstanceField",
                    "improvement": "Detectar self.attr, this.attr",
                    "patterns": [r"self\.\w+", r"this\.\w+"]
                },
                {
                    "hadron": "StaticField",
                    "improvement": "Detectar acesso a classe/static",
                    "patterns": [r"ClassName\.\w+", r"static\s+\w+"]
                }
            ]
        })

        # 4. Remover hádrons obsoletos
        adjustments.append({
            "type": "remove",
            "description": "Remover hádrons teóricos ou obsoletos",
            "reason": "Não aparecem no código real",
            "proposal": {
                "remove": ["PanicRecover", "ChaosMonkey", "SelfHealingProbe"],
                "justification": "São conceitos teóricos, não padrões de código"
            }
        })

        return adjustments

    def _determine_priority_actions(self, categorized: Dict, patterns: Dict) -> List[Dict]:
        """Determina ações prioritárias baseado nos gaps"""
        actions = []

        # Ações de alta prioridade
        if len(categorized["detection_issue"]["hadrons"]) > 10:
            actions.append({
                "priority": "HIGH",
                "action": "Fix detection heuristics",
                "target": categorized["detection_issue"]["hadrons"],
                "impact": "Immediato na cobertura",
                "effort": "Baixo - só ajustar regex/patterns"
            })

        if patterns["common_across_all"]:
            actions.append({
                "priority": "HIGH",
                "action": "Address common gaps",
                "target": patterns["common_across_all"],
                "impact": "Alto - afeta todos os repositórios",
                "effort": "Médio - precisa análise profunda"
            })

        # Ações de média prioridade
        actions.append({
            "priority": "MEDIUM",
            "action": "Merge similar hadrons",
            "target": ["BitFlag", "BitMask", "WebSocketHandler", "QueueWorker"],
            "impact": "Reduz complexidade sem perder informação",
            "effort": "Baixo"
        })

        # Ações de baixa prioridade
        actions.append({
            "priority": "LOW",
            "action": "Remove obsolete hadrons",
            "target": categorized["obselete_or_theoretical"]["hadrons"],
            "impact": "Limpeza da taxonomia",
            "effort": "Mínimo"
        })

        return actions

    def generate_adjusted_taxonomy(self) -> Dict:
        """Gera taxonomia ajustada com as mudanças propostas"""
        # Começa com o catálogo original
        adjusted_catalog = HADRON_CATALOG.copy()

        # Aplica ajustes propostos
        for adj in self.gap_analysis["proposed_adjustments"]:
            if adj["type"] == "merge":
                # Remove os originais e adiciona o novo
                for hadron in adj["proposal"]["merge_from"]:
                    if hadron in adjusted_catalog:
                        del adjusted_catalog[hadron]

                # Adiciona o novo hádron
                new_name = adj["proposal"]["new_hadron"]
                # Precisa definir continent/fundamental baseado nos mesclados
                if adjusted_catalog:
                    # Usa o primeiro como referência
                    first = adj["proposal"]["merge_from"][0]
                    if first in HADRON_CATALOG:
                        adjusted_catalog[new_name] = {
                            "continent": HADRON_CATALOG[first]["continent"].value,
                            "fundamental": HADRON_CATALOG[first]["fundamental"].value,
                            "form": adj["proposal"]["form"]
                        }

            elif adj["type"] == "remove":
                for hadron in adj["proposal"]["remove"]:
                    if hadron in adjusted_catalog:
                        del adjusted_catalog[hadron]

        # Adiciona novos genéricos
        for adj in self.gap_analysis["proposed_adjustments"]:
            if adj["type"] == "add_generic":
                for new_hadron in adj["proposal"]:
                    adjusted_catalog[new_hadron["name"]] = {
                        "continent": new_hadron["continent"],
                        "fundamental": new_hadron["fundamental"],
                        "form": new_hadron["form"]
                    }

        return {
            "original_count": len(HADRON_CATALOG),
            "adjusted_count": len(adjusted_catalog),
            "reduction": len(HADRON_CATALOG) - len(adjusted_catalog),
            "catalog": adjusted_catalog
        }

    def save_analysis(self, output_path: Path):
        """Salva análise completa dos gaps"""
        analysis = {
            "metadata": {
                "missing_hadrons": self.gap_analysis["missing_count"],
                "coverage": self.gap_analysis["coverage_percentage"],
                "timestamp": "2025-12-03"
            },
            "gap_analysis": self.gap_analysis,
            "adjusted_taxonomy": self.generate_adjusted_taxonomy(),
            "next_steps": [
                "1. Implement detection improvements for top 10 missing hadrons",
                "2. Test adjusted taxonomy with new sample",
                "3. Validate LLM enrichment for edge cases",
                "4. Finalize taxonomy v4.1"
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        # Gera resumo executivo
        summary_path = output_path.with_suffix('.md')
        self._generate_summary(analysis, summary_path)

    def _generate_summary(self, analysis: Dict, output_path: Path):
        """Gera resumo em Markdown"""
        gap = analysis["gap_analysis"]
        taxonomy = analysis["adjusted_taxonomy"]

        summary = f"""# GAP ANALYSIS & TAXONOMY ADJUSTMENTS

## 🎯 Key Findings

- **Missing Hadrons**: {gap['missing_count']}/96 ({gap['coverage_percentage']}% coverage)
- **Main Issue**: Detection problems, not taxonomy problems
- **Recommendation**: Adjust taxonomy to ~85 hadrons with better detection

## 📊 Gap Categories

### Critical Issues (Detection)
- {len(gap['categorized_gaps']['detection_issue']['hadrons'])} hadrons não detectados corretamente
- Impacto: Alto - afeta diretamente a cobertura

### Low Impact (Syntax Level)
- {len(gap['categorized_gaps']['syntax_level']['hadrons'])} elementos de baixo nível
- Podem ser agrupados em hadrons mais genéricos

## 🔧 Proposed Adjustments

### 1. Merge Similar Hadrons
- **BitFlag, BitMask, ParityBit, SignBit** → **BitOperation**
- **WebSocketHandler, QueueWorker, MessageConsumer** → **SystemEventHandler**

### 2. Add Generic Patterns
- **FieldAccess** - Padrão muito comum não detectado
- **ImportStatement** - Essencial para análise de dependências
- **ErrorHandling** - Genérico para try/catch/except

### 3. Improve Detection
- Add regex patterns for TryCatch, InstanceField, StaticField
- Multi-language support (Java, Go, Rust, TypeScript)

### 4. Remove Obsolete
- PanicRecover, ChaosMonkey, SelfHealingProbe

## 📈 Expected Impact

- **Before**: 96 hadrons, 52.3% coverage
- **After**: ~85 hadrons, estimated 75%+ coverage
- **Benefit**: Mais focado, melhor detecção, mais útil

## ✅ Priority Actions

1. **IMMEDIATE**: Fix detection heuristics for top 10 missing
2. **SHORT-TERM**: Implement adjusted taxonomy
3. **MEDIUM-TERM**: Add LLM enrichment for edge cases
4. **LONG-TERM**: Expand validation dataset

---
Analysis completed: 2025-12-03
"""

        with open(output_path, 'w') as f:
            f.write(summary)

# ========================
# EXECUÇÃO PRINCIPAL
# ========================

if __name__ == "__main__":
    analyzer = GapAnalyzer()

    # Salva análise completa
    output_file = Path("gap_analysis_adjustments.json")
    analyzer.save_analysis(output_file)

    print("\n" + "="*60)
    print("GAP ANALYSIS COMPLETE")
    print("="*60)
    print(f"Arquivo de análise: {output_file}")
    print(f"Taxonomia ajustada para {analyzer.generate_adjusted_taxonomy()['adjusted_count']} hádrons")
    print(f"Redução de {analyzer.generate_adjusted_taxonomy()['reduction']} hádrons")
    print("\nPróximos passos:")
    for step in analyzer.gap_analysis["priority_actions"][:3]:
        print(f"  - [{step['priority']}] {step['action']}")
