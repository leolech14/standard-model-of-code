#!/usr/bin/env python3
"""
SPECTROMETER VALIDATION FRAMEWORK
Validação rigorosa com ground-truth real e métricas científicas
Baseado em: Architecture Recovery papers, IEEE/ACM 2025
"""

import json
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
import shutil

@dataclass
class ValidationMetric:
    """Métrica de validação científica"""
    name: str
    precision: float  # TP / (TP + FP)
    recall: float      # TP / (TP + FN)
    f1_score: float   # 2 * (precision * recall) / (precision + recall)
    accuracy: float   # (TP + TN) / (TP + TN + FP + FN)
    false_positives: int
    false_negatives: int
    true_positives: int
    true_negatives: int

@dataclass
class GroundTruthElement:
    """Elemento com ground-truth verificado manualmente"""
    file_path: str
    line: int
    element_name: str
    element_type: str  # function, class, variable, etc
    ground_truth_hadron: str
    ground_truth_haiku: Optional[str]
    confidence: float = 1.0  # confiança manual na label
    reviewer: str = "expert"

class ValidationType(Enum):
    """Tipos de validação"""
    MANUAL_EXPERT = "manual_expert"
    PEER_REVIEWED = "peer_reviewed"
    PUBLISHED_DATASET = "published_dataset"
    SYNTHETIC_BUT_VERIFIED = "synthetic_verified"

class SpectrometerValidator:
    """Framework de validação rigorosa para Spectrometer V9"""

    def __init__(self):
        self.spectrometer = None  # Lazy loading
        self.results = []
        self.metrics_by_hadron = {}
        self.global_metrics = None

    def load_spectrometer(self):
        """Carrega Specterator V9 (lazy loading)"""
        if not self.spectrometer:
            from spectrometer_v9_raw_haiku import SpectrometerV9
            self.spectrometer = SpectrometerV9()

    def validate_against_ground_truth(
        self,
        repo_path: Path,
        ground_truth: List[GroundTruthElement],
        validation_type: ValidationType = ValidationType.MANUAL_EXPERT
    ) -> Dict[str, Any]:
        """
        Valida Spectrometer contra ground-truth conhecido

        Returns:
            Dicionário com métricas detalhadas e análise
        """
        print(f"\n🔍 VALIDAÇÃO RIGOROSA")
        print(f"📁 Repositório: {repo_path}")
        print(f"📊 Ground-truth: {len(ground_truth)} elementos")
        print(f"🔬 Tipo: {validation_type.value}")
        print("=" * 60)

        # Carrega Spectrometer
        self.load_spectrometer()

        # Executa análise
        start_time = time.time()
        analysis = self.spectrometer.analyze_repository(repo_path)
        duration = time.time() - start_time

        # Compara com ground-truth
        comparison = self._compare_with_ground_truth(analysis, ground_truth)

        # Calcula métricas
        metrics = self._calculate_metrics(comparison)

        # Análise de falhas
        failure_analysis = self._analyze_failures(comparison)

        # Salva resultados
        result = {
            "repository": str(repo_path),
            "validation_type": validation_type.value,
            "ground_truth_size": len(ground_truth),
            "spectrometer_size": len(analysis.get("classified_elements", [])),
            "duration_seconds": duration,
            "metrics": metrics,
            "comparison": comparison,
            "failure_analysis": failure_analysis,
            "validation_timestamp": time.time()
        }

        self.results.append(result)

        # Imprime relatório
        self._print_validation_report(result)

        return result

    def _compare_with_ground_truth(
        self, analysis: Dict, ground_truth: List[GroundTruthElement]
    ) -> Dict[str, Any]:
        """Compara resultados com ground-truth"""

        # Mapeia elementos do Spectrometer
        spectrometer_elements = {}
        for elem in analysis.get("classified_elements", []):
            key = f"{elem['line']}:{elem['name']}"
            spectrometer_elements[key] = elem

        # Mapeia ground-truth
        gt_elements = {}
        for gt in ground_truth:
            key = f"{gt.line}:{gt.element_name}"
            gt_elements[key] = gt

        # Comparações
        tp_hadrons = []  # True Positives (correto)
        fp_hadrons = []  # False Positives (errou)
        fn_hadrons = []  # False Negatives (perdeu)
        tn_hadrons = []  # True Negatives (correto negativo)

        # Hadrons
        for key, spec_elem in spectrometer_elements.items():
            if key in gt_elements:
                gt_elem = gt_elements[key]

                # Check hadron
                if spec_elem.get("hadron") == gt_elem.ground_truth_hadron:
                    tp_hadrons.append({
                        "key": key,
                        "predicted": spec_elem.get("hadron"),
                        "actual": gt_elem.ground_truth_hadron,
                        "confidence": spec_elem.get("confidence", 0)
                    })
                else:
                    fp_hadrons.append({
                        "key": key,
                        "predicted": spec_elem.get("hadron"),
                        "actual": gt_elem.ground_truth_hadron,
                        "confidence": spec_elem.get("confidence", 0)
                    })

        # False Negatives (ground-truth que não detectamos)
        for key, gt_elem in gt_elements.items():
            if key not in spectrometer_elements:
                fn_hadrons.append({
                    "key": key,
                    "predicted": None,
                    "actual": gt_elem.ground_truth_hadron,
                    "confidence": 0
                })

        # True Negatives (elementos que não existem em ambos - mais complexo)
        # Simplificado: elementos em áreas neutras
        total_possible = len(gt_elements) + len(spectrometer_elements)
        tn_hadrons_count = max(0, total_possible - len(tp_hadrons) - len(fp_hadrons) - len(fn_hadrons))

        return {
            "true_positives": tp_hadrons,
            "false_positives": fp_hadrons,
            "false_negatives": fn_hadrons,
            "true_negatives": tn_hadrons_count,
            "total_possible": total_possible
        }

    def _calculate_metrics(self, comparison: Dict) -> Dict[str, ValidationMetric]:
        """Calcula métricas científicas"""

        tp = len(comparison["true_positives"])
        fp = len(comparison["false_positives"])
        fn = len(comparison["false_negatives"])
        tn = comparison["true_negatives"]

        # Métricas globais
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0

        global_metric = ValidationMetric(
            name="Overall",
            precision=precision,
            recall=recall,
            f1_score=f1,
            accuracy=accuracy,
            false_positives=fp,
            false_negatives=fn,
            true_positives=tp,
            true_negatives=tn
        )

        # Métricas por hadron
        metrics_by_hadron = {"Overall": global_metric}

        # Agrupa por hadron previsto
        predicted_by_hadron = {}
        for fp in comparison["false_positives"]:
            hadron = fp["predicted"] or "Unclassified"
            if hadron not in predicted_by_hadron:
                predicted_by_hadron[hadron] = {"tp": 0, "fp": 0, "fn": 0}
            predicted_by_hadron[hadron]["fp"] += 1

        for tp in comparison["true_positives"]:
            hadron = tp["predicted"]
            if hadron not in predicted_by_hadron:
                predicted_by_hadron[hadron] = {"tp": 0, "fp": 0, "fn": 0}
            predicted_by_hadron[hadron]["tp"] += 1

        for fn in comparison["false_negatives"]:
            hadron = fn["actual"]
            if hadron not in predicted_by_hadron:
                predicted_by_hadron[hadron] = {"tp": 0, "fp": 0, "fn": 0}
            predicted_by_hadron[hadron]["fn"] += 1

        # Calcula métricas por hadron
        for hadron, counts in predicted_by_hadron.items():
            tp_h = counts["tp"]
            fp_h = counts["fp"]
            fn_h = counts["fn"]

            precision_h = tp_h / (tp_h + fp_h) if (tp_h + fp_h) > 0 else 0
            recall_h = tp_h / (tp_h + fn_h) if (tp_h + fn_h) > 0 else 0
            f1_h = 2 * (precision_h * recall_h) / (precision_h + recall_h) if (precision_h + recall_h) > 0 else 0

            metrics_by_hadron[hadron] = ValidationMetric(
                name=hadron,
                precision=precision_h,
                recall=recall_h,
                f1_score=f1_h,
                accuracy=0,  # Complexo calcular TN por hadron
                false_positives=fp_h,
                false_negatives=fn_h,
                true_positives=tp_h,
                true_negatives=0
            )

        self.metrics_by_hadron = metrics_by_hadron

        return metrics_by_hadron

    def _analyze_failures(self, comparison: Dict) -> Dict[str, Any]:
        """Análise detalhada das falhas"""

        analysis = {
            "false_positive_patterns": {},
            "false_negative_patterns": {},
            "confidence_distribution": {},
            "top_errors": []
        }

        # Analisa False Positives
        for fp in comparison["false_positives"]:
            hadron = fp["predicted"] or "Unclassified"

            if hadron not in analysis["false_positive_patterns"]:
                analysis["false_positive_patterns"][hadron] = []

            analysis["false_positive_patterns"][hadron].append({
                "line": fp["key"].split(":")[0],
                "name": fp["key"].split(":")[1],
                "predicted": hadron,
                "actual": fp["actual"],
                "confidence": fp["confidence"]
            })

        # Analisa False Negatives
        for fn in comparison["false_negatives"]:
            hadron = fn["actual"]

            if hadron not in analysis["false_negative_patterns"]:
                analysis["false_negative_patterns"][hadron] = []

            analysis["false_negative_patterns"][hadron].append({
                "line": fn["key"].split(":")[0],
                "name": fn["key"].split(":")[1],
                "missing": hadron
            })

        # Distribuição de confiança dos erros
        all_fps = comparison["false_positives"]
        if all_fps:
            confidences = [fp["confidence"] for fp in all_fps]
            analysis["confidence_distribution"] = {
                "min": min(confidences),
                "max": max(confidences),
                "avg": statistics.mean(confidences),
                "median": statistics.median(confidences)
            }

        # Top erros (mais frequentes)
        for hadron, fps in analysis["false_positive_patterns"].items():
            analysis["top_errors"].append({
                "type": "False Positive",
                "hadron": hadron,
                "count": len(fps),
                "examples": fps[:3]
            })

        return analysis

    def _print_validation_report(self, result: Dict):
        """Imprime relatório de validação"""

        metrics = result["metrics"]
        overall = metrics["Overall"]

        print("\n📊 RELATÓRIO DE VALIDAÇÃO")
        print("=" * 60)
        print(f"📁 Repositório: {Path(result['repository']).name}")
        print(f"📊 Ground-truth: {result['ground_truth_size']} elementos")
        print(f"🔍 Detectado: {result['spectrometer_size']} elementos")
        print(f"⏱️  Duração: {result['duration_seconds']:.2f}s")
        print(f"🎯 TIPO: {result['validation_type'].upper()}")
        print()

        # Métricas principais
        print("📈 MÉTRICAS PRINCIPAIS:")
        print(f"  • Precisão: {overall.precision:.1%}")
        print(f"  • Recall:    {overall.recall:.1%}")
        print(f"  • F1-Score:  {overall.f1_score:.1%}")
        print(f"  • Acurácia: {overall.accuracy:.1%}")
        print()

        # Status
        print("🎯 STATUS DA VALIDAÇÃO:")
        if overall.f1_score >= 0.95:
            print("  ✅ EXCELENTE (F1 ≥ 95%)")
        elif overall.f1_score >= 0.85:
            print("  ✅ BOM (F1 ≥ 85%)")
        elif overall.f1_score >= 0.70:
            print("  ⚠️  ACEITÁVEL (F1 ≥ 70%)")
        else:
            print("  ❌ PRECISA MELHORAR (F1 < 70%)")

        # Análise por hadron
        print(f"\n🔍 MÉTRICAS POR HÁDRON (Top 10):")
        sorted_hadrons = sorted(
            [(h, m) for h, m in metrics.items() if h != "Overall"],
            key=lambda x: x[1].f1_score,
            reverse=True
        )[:10]

        for hadron, metric in sorted_hadrons:
            status = "🟢" if metric.f1_score >= 0.9 else "🟡" if metric.f1_score >= 0.7 else "🔴"
            print(f"  {status} {hadron:20} P:{metric.precision:.2f} R:{metric.recall:.2f} F1:{metric.f1_score:.2f}")

        # Problemas
        failure_analysis = result.get("failure_analysis", {})
        if failure_analysis.get("false_positive_patterns"):
            print(f"\n⚠️  TOP FALSE POSITIVES:")
            for error in failure_analysis["top_errors"][:3]:
                print(f"  • {error['hadron']}: {error['count']} ocorrências")

        if failure_analysis.get("confidence_distribution"):
            conf = failure_analysis["confidence_distribution"]
            print(f"\n📊 CONFIANÇA DOS ERROS:")
            print(f"  • Média: {conf['avg']:.2f}")
            print(f"  • Mínimo: {conf['min']:.2f}")
            print(f"  • Máximo: {conf['max']:.2f}")

        print("=" * 60)

    def generate_full_report(self, output_path: Optional[Path] = None):
        """Gera relatório completo de todas as validações"""

        if not self.results:
            print("❌ Nenhuma validação realizada ainda")
            return

        # Métricas agregadas
        all_metrics = []
        for result in self.results:
            all_metrics.append(result["metrics"]["Overall"])

        # Calcula estatísticas globais
        precisions = [m.precision for m in all_metrics]
        recalls = [m.recall for m in all_metrics]
        f1_scores = [m.f1_score for m in all_metrics]

        self.global_metrics = {
            "repositories_validated": len(self.results),
            "avg_precision": statistics.mean(precisions),
            "avg_recall": statistics.mean(recalls),
            "avg_f1_score": statistics.mean(f1_scores),
            "min_f1_score": min(f1_scores),
            "max_f1_score": max(f1_scores),
            "std_f1_score": statistics.stdev(f1_scores) if len(f1_scores) > 1 else 0
        }

        # Relatório detalhado
        report = {
            "validation_timestamp": time.time(),
            "spectrometer_version": "v9",
            "summary": self.global_metrics,
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations()
        }

        # Salva relatório
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"💾 Relatório salvo em: {output_path}")

        return report

    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos resultados"""

        recommendations = []

        if not self.global_metrics:
            return ["Nenhuma validação realizada para gerar recomendações"]

        # Analisa F1-score
        if self.global_metrics["avg_f1_score"] < 0.80:
            recommendations.append(
                "🔧 F1-score baixo (<80%). Considerar: "
                "1) Refinar regras de hadrons com mais falsos positivos; "
                "2) Aumentar cobertura para reduzir falsos negativos"
            )
        elif self.global_metrics["avg_f1_score"] < 0.90:
            recommendations.append(
                "⚡ F1-score aceitável mas pode melhorar (80-90%). "
                "Focar nos hadrons com pior desempenho individual"
            )
        else:
            recommendations.append(
                "✅ Excelente desempenho (>90%). Manter monitoramento contínuo"
            )

        # Analisa precisão vs recall
        avg_precision = self.global_metrics["avg_precision"]
        avg_recall = self.global_metrics["avg_recall"]

        if avg_precision < 0.85:
            recommendations.append(
                "🎯 Baixa precisão (<85%). Muitos falsos positivos. "
                "Revisar regras que estão 'superclassificando'"
            )

        if avg_recall < 0.85:
            recommendations.append(
                "🔍 Baixo recall (<85%). Muitos falsos negativos. "
                "Expandir regras ou adicionar patterns ausentes"
            )

        # Consistência
        if self.global_metrics["std_f1_score"] > 0.15:
            recommendations.append(
                "📊 Alta variabilidade entre repositórios (std > 0.15). "
                "Investigar causas específicas por linguagem ou domínio"
            )

        return recommendations

# Exemplo de uso
if __name__ == "__main__":
    # Criar validador
    validator = SpectrometerValidator()

    # Exemplo: validar com ground-truth manual
    ground_truth = [
        GroundTruthElement(
            file_path="src/user_service.py",
            line=15,
            element_name="UserService",
            element_type="class",
            ground_truth_hadron="Service",
            ground_truth_haiku="ApplicationService"
        ),
        GroundTruthElement(
            file_path="src/user_repository.py",
            line=8,
            element_name="save",
            element_type="function",
            ground_truth_hadron="CommandHandler",
            ground_truth_haiku=None
        ),
        # ... mais elementos
    ]

    # Validar
    repo_path = Path("/tmp/test_repo")
    result = validator.validate_against_ground_truth(
        repo_path,
        ground_truth,
        ValidationType.MANUAL_EXPERT
    )

    # Gerar relatório completo
    report = validator.generate_full_report(
        Path("/tmp/spectrometer_validation_report.json")
    )