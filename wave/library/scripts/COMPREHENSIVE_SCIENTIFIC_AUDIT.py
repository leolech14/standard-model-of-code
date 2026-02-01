#!/usr/bin/env python3
"""
=================================================================
COMPREHENSIVE SCIENTIFIC AUDIT
Complete Evidence Analysis + Methodology Review
ALL DATA. ALL EVIDENCE. METHODOLOGY.
=================================================================
"""

import json
import statistics
import math
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import re

class ComprehensiveScientificAudit:
    """Auditoria Científica Completa dos Resultados do HAIKU-Ω"""

    def __init__(self):
        self.data_file = Path("/tmp/haiku_384_tuned_1764823831.json")
        self.audit_results = {}
        self.start_time = datetime.now()

        print("="*80)
        print("     COMPREHENSIVE SCIENTIFIC AUDIT")
        print("     Complete Evidence Analysis + Methodology Review")
        print("="*80)
        print(f"Início: {self.start_time}")
        print("="*80)

    def execute_complete_audit(self):
        """Executa auditoria completa"""

        # Carregar dados
        print("\n📁 CARREGANDO DADOS...")
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)

        # Análises
        self.audit_methodology()
        self.audit_evidence_quality()
        self.audit_detection_patterns()
        self.audit_statistical_validity()
        self.audit_file_coverage()
        self.audit_false_positive_analysis()
        self.audit_confidence_distribution()
        self.audit_high_confidence_cases()
        self.generate_final_audit_report()

    def audit_methodology(self):
        """Auditoria da Metodologia Usada"""

        print("\n🔬 AUDITORIA DE METODOLOGIA")
        print("-"*60)

        methodology = {
            "detector": "HAIKU-Ω v3.1",
            "approach": "Multi-factor Scoring System",
            "factors": [
                "Nome matching (30%)",
                "Keywords no texto (40%)",
                "Padrões regex (20%)",
                "Indicadores semânticos (10%)"
            ],
            "threshold": "0.25 (25%)",
            "parser": "Python AST + Lexical Fallback",
            "files_analyzed": 1970,
            "detection_time": "7.3 segundos"
        }

        print("📋 METODOLOGIA DETALHADA:")
        for key, value in methodology.items():
            if isinstance(value, list):
                print(f"   • {key}:")
                for item in value:
                    print(f"      - {item}")
            else:
                print(f"   • {key}: {value}")

        self.audit_results['methodology'] = methodology

    def audit_evidence_quality(self):
        """Auditoria da Qualidade das Evidências"""

        print("\n📊 AUDITORIA DE QUALIDADE DAS EVIDÊNCIAS")
        print("-"*60)

        detections = self.data['deteccoes']

        # Estatísticas básicas
        confidences = [d['confianca'] for d in detections]

        quality_metrics = {
            "total_detections": len(detections),
            "confidence_mean": statistics.mean(confidences),
            "confidence_median": statistics.median(confidences),
            "confidence_std": statistics.stdev(confidences) if len(confidences) > 1 else 0,
            "confidence_min": min(confidences),
            "confidence_max": max(confidences),
            "high_confidence_count": len([c for c in confidences if c >= 0.6]),
            "medium_confidence_count": len([c for c in confidences if 0.4 <= c < 0.6]),
            "low_confidence_count": len([c for c in confidences if c < 0.4])
        }

        print("📈 MÉTRICAS DE QUALIDADE:")
        print(f"   • Detecções totais: {quality_metrics['total_detections']:,}")
        print(f"   • Confiança média: {quality_metrics['confidence_mean']:.3f}")
        print(f"   • Confiança mediana: {quality_metrics['confidence_median']:.3f}")
        print(f"   • Desvio padrão: {quality_metrics['confidence_std']:.3f}")
        print(f"   • Intervalo: [{quality_metrics['confidence_min']:.3f}, {quality_metrics['confidence_max']:.3f}]")
        print(f"\n📊 DISTRIBUIÇÃO POR CONFIANÇA:")
        print(f"   • Alta (≥60%): {quality_metrics['high_confidence_count']} ({quality_metrics['high_confidence_count']/len(detections):.1%})")
        print(f"   • Média (40-59%): {quality_metrics['medium_confidence_count']} ({quality_metrics['medium_confidence_count']/len(detections):.1%})")
        print(f"   • Baixa (<40%): {quality_metrics['low_confidence_count']} ({quality_metrics['low_confidence_count']/len(detections):.1%})")

        self.audit_results['evidence_quality'] = quality_metrics

    def audit_detection_patterns(self):
        """Auditoria dos Padrões de Detecção"""

        print("\n🔍 AUDITORIA DE PADRÕES DE DETECÇÃO")
        print("-"*60)

        detections = self.data['deteccoes']

        # Análise por arquivo
        files_with_detections = defaultdict(list)
        for det in detections:
            file_path = det['arquivo']
            files_with_detections[file_path].append(det)

        # Top 20 arquivos com mais detecções
        top_files = sorted(files_with_detections.items(),
                          key=lambda x: len(x[1]), reverse=True)[:20]

        print("📁 TOP 20 ARQUIVOS COM MAIS DETECÇÕES:")
        for i, (file_path, dets) in enumerate(top_files, 1):
            avg_conf = statistics.mean([d['confianca'] for d in dets])
            print(f"   {i:2d}. {Path(file_path).name}")
            print(f"       Detecções: {len(dets)} | Confiança média: {avg_conf:.3f}")

        # Análise por tipo de sub-hádon
        subhadron_types = Counter(d['hadron'] for d in detections)
        print("\n⚛️  DETECÇÕES POR TIPO DE SUB-HÁDRON:")
        for hadron, count in subhadron_types.most_common():
            print(f"   • {hadron}: {count} ({count/len(detections):.1%})")

        # Análise por responsibility
        resp_types = Counter(d['responsibility'] for d in detections)
        print("\n🎯 DETECÇÕES POR RESPONSIBILITY:")
        for resp, count in resp_types.most_common():
            print(f"   • {resp}: {count} ({count/len(detections):.1%})")

        self.audit_results['detection_patterns'] = {
            'top_files': top_files[:10],
            'by_hadron': dict(subhadron_types),
            'by_responsibility': dict(resp_types)
        }

    def audit_statistical_validity(self):
        """Auditoria da Validade Estatística"""

        print("\n📈 AUDITORIA DE VALIDADE ESTATÍSTICA")
        print("-"*60)

        detections = self.data['deteccoes']
        confidences = [d['confianca'] for d in detections]

        # Testes estatísticos
        statistical_tests = {
            "sample_size": len(detections),
            "coefficient_of_variation": statistics.stdev(confidences) / statistics.mean(confidences) if statistics.mean(confidences) > 0 else 0,
            "skewness": self._calculate_skewness(confidences),
            "kurtosis": self._calculate_kurtosis(confidences),
            "outliers_count": len([c for c in confidences if abs(c - statistics.mean(confidences)) > 2 * statistics.stdev(confidences)])
        }

        print("🧪 TESTES ESTATÍSTICOS:")
        print(f"   • Tamanho da amostra: {statistical_tests['sample_size']:,}")
        print(f"   • Coeficiente de variação: {statistical_tests['coefficient_of_variation']:.3f}")
        print(f"   • Skewness (assimetria): {statistical_tests['skewness']:.3f}")
        print(f"   • Kurtosis: {statistical_tests['kurtosis']:.3f}")
        print(f"   • Outliers (2σ): {statistical_tests['outliers_count']}")

        # Interpretação
        cv = statistical_tests['coefficient_of_variation']
        if cv < 0.1:
            cv_interpret = "MUITO BAIXA (extremamente consistente)"
        elif cv < 0.2:
            cv_interpret = "BAIXA (muito consistente)"
        elif cv < 0.3:
            cv_interpret = "MODERADA (razoavelmente consistente)"
        else:
            cv_interpret = "ALTA (inconsistente)"

        print(f"\n📝 INTERPRETAÇÃO:")
        print(f"   • Variabilidade: {cv_interpret}")

        self.audit_results['statistical_validity'] = statistical_tests

    def audit_file_coverage(self):
        """Auditoria da Cobertura de Arquivos"""

        print("\n📂 AUDITORIA DE COBERTURA DE ARQUIVOS")
        print("-"*60)

        total_files = self.data['metricas']['arquivos_analisados']
        files_with_detection = self.data['metricas']['arquivos_com_deteccao']

        coverage_analysis = {
            "total_files": total_files,
            "files_with_detection": files_with_detection,
            "coverage_percentage": files_with_detection / total_files,
            "files_without_detection": total_files - files_with_detection,
            "detections_per_file_ratio": self.data['metricas']['detectados'] / files_with_detection if files_with_detection > 0 else 0
        }

        print("📊 ANÁLISE DE COBERTURA:")
        print(f"   • Arquivos totais: {coverage_analysis['total_files']:,}")
        print(f"   • Arquivos com detecção: {coverage_analysis['files_with_detection']:,}")
        print(f"   • Arquivos sem detecção: {coverage_analysis['files_without_detection']:,}")
        print(f"   • Percentual de cobertura: {coverage_analysis['coverage_percentage']:.1%}")
        print(f"   • Média de detecções/arquivo: {coverage_analysis['detections_per_file_ratio']:.1f}")

        self.audit_results['file_coverage'] = coverage_analysis

    def audit_false_positive_analysis(self):
        """Auditoria de Possíveis Falsos Positivos"""

        print("\n⚠️  AUDITORIA DE FALSOS POSITIVOS")
        print("-"*60)

        detections = self.data['deteccoes']

        # Padrões suspeitos
        suspicious_patterns = [
            r"from typing import",
            r"print\(",
            r"#.*",
            r"'.*'",
            r'".*"',
            r"def \w+\(",
            r"class \w+\(",
            r"import \w+",
            r"=\s*\{",
            r"=\s*\["
        ]

        false_positive_indicators = {
            "import_statements": 0,
            "print_statements": 0,
            "comments": 0,
            "string_literals": 0,
            "function_definitions": 0,
            "class_definitions": 0,
            "dictionary_assignments": 0,
            "list_assignments": 0
        }

        high_risk_detections = []

        for det in detections:
            evidence = det['evidencia']
            risk_score = 0

            # Verificar padrões suspeitos
            if re.search(r"from typing import", evidence):
                false_positive_indicators['import_statements'] += 1
                risk_score += 0.3
            elif re.search(r"print\(", evidence):
                false_positive_indicators['print_statements'] += 1
                risk_score += 0.4
            elif evidence.startswith("#") or evidence.startswith("'") or evidence.startswith('"'):
                false_positive_indicators['comments'] += 1
                risk_score += 0.5
            elif re.search(r"def \w+\(", evidence):
                false_positive_indicators['function_definitions'] += 1
                risk_score += 0.2
            elif re.search(r"class \w+\(", evidence):
                false_positive_indicators['class_definitions'] += 1
                risk_score += 0.1
            elif re.search(r"=\s*\{", evidence):
                false_positive_indicators['dictionary_assignments'] += 1
                risk_score += 0.3
            elif re.search(r"=\s*\[", evidence):
                false_positive_indicators['list_assignments'] += 1
                risk_score += 0.3

            if risk_score >= 0.3:
                high_risk_detections.append({
                    'id': det['id'],
                    'evidence': evidence,
                    'confidence': det['confianca'],
                    'risk_score': risk_score,
                    'file': Path(det['arquivo']).name,
                    'line': det['linha']
                })

        print("🚨 INDICADORES DE FALSOS POSITIVOS:")
        for indicator, count in false_positive_indicators.items():
            if count > 0:
                print(f"   • {indicator}: {count} ocorrências")

        print(f"\n⚠️  DETECÇÕES DE ALTO RISCO: {len(high_risk_detections)}")

        # Top 10 suspeitas
        print("\n🔍 TOP 10 DETECÇÕES MAIS SUSPEITAS:")
        sorted_suspects = sorted(high_risk_detections, key=lambda x: x['risk_score'], reverse=True)[:10]

        for i, suspect in enumerate(sorted_suspects, 1):
            print(f"   {i}. {suspect['id']}")
            print(f"      Arquivo: {suspect['file']}:{suspect['line']}")
            print(f"      Evidência: '{suspect['evidence'][:50]}...'")
            print(f"      Confiança: {suspect['confidence']:.1%} | Risco: {suspect['risk_score']:.1f}")

        self.audit_results['false_positive_analysis'] = {
            'indicators': false_positive_indicators,
            'high_risk_count': len(high_risk_detections),
            'high_risk_percentage': len(high_risk_detections) / len(detections),
            'top_suspects': sorted_suspects[:20]
        }

    def audit_confidence_distribution(self):
        """Auditoria da Distribuição de Confiança"""

        print("\n📊 AUDITORIA DA DISTRIBUIÇÃO DE CONFIANÇA")
        print("-"*60)

        detections = self.data['deteccoes']
        confidences = [d['confianca'] for d in detections]

        # Histograma
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        histogram = [0] * (len(bins) - 1)

        for conf in confidences:
            for i in range(len(bins) - 1):
                if bins[i] <= conf < bins[i + 1]:
                    histogram[i] += 1
                    break

        print("📈 HISTOGRAMA DE CONFIANÇA:")
        for i in range(len(bins) - 1):
            bar_length = int(histogram[i] / max(histogram) * 50) if max(histogram) > 0 else 0
            bar = "█" * bar_length
            print(f"   {bins[i]:.1f}-{bins[i+1]:.1f}: {bar} {histogram[i]:,}")

        # Quartis
        sorted_conf = sorted(confidences)
        n = len(sorted_conf)
        q1 = sorted_conf[n // 4]
        q2 = sorted_conf[n // 2]
        q3 = sorted_conf[3 * n // 4]

        print(f"\n📊 ANÁLISE QUARTIL:")
        print(f"   • Q1 (25%): {q1:.3f}")
        print(f"   • Q2 (50%/mediana): {q2:.3f}")
        print(f"   • Q3 (75%): {q3:.3f}")
        print(f"   • IQR: {q3 - q1:.3f}")

        self.audit_results['confidence_distribution'] = {
            'histogram': list(zip(bins[:-1], bins[1:], histogram)),
            'quartiles': {'q1': q1, 'q2': q2, 'q3': q3, 'iqr': q3 - q1}
        }

    def audit_high_confidence_cases(self):
        """Auditoria Detalhada dos Casos de Alta Confiança"""

        print("\n🏆 AUDITORIA DETALHADA - ALTA CONFIANÇA (≥70%)")
        print("-"*60)

        detections = self.data['deteccoes']
        high_confidence = [d for d in detections if d['confianca'] >= 0.70]

        print(f"📊 CASOS DE ALTA CONFIANÇA: {len(high_confidence)}")

        # Top 20 de maior confiança
        top_confidence = sorted(high_confidence, key=lambda x: x['confianca'], reverse=True)[:20]

        print("\n🥇 TOP 20 MAIORES CONFIANÇAS:")
        for i, det in enumerate(top_confidence, 1):
            print(f"\n{i:2d}. {det['id']}")
            print(f"     📊 Confiança: {det['confianca']:.1%}")
            print(f"     📍 Arquivo: {Path(det['arquivo']).name}:{det['linha']}")
            print(f"     🔍 Evidência: '{det['evidencia'][:80]}...'")
            print(f"     ⚛️  Tipo: {det['hadron']} | {det['responsibility']} | {det['purity']}")

        # Análise dos melhores casos
        print(f"\n📈 ANÁLISE DOS MELHORES CASOS:")
        best_cases = top_confidence[:5]
        for case in best_cases:
            print(f"\n🔬 CASO EXCELENTE: {case['id']}")
            print(f"   Por que é excelente:")
            print(f"   • Confiança: {case['confianca']:.1%}")

            # Verificar arquivo real
            try:
                file_path = Path(case['arquivo'])
                if file_path.exists():
                    lines = file_path.read_text(encoding='utf-8').split('\n')
                    if case['linha'] <= len(lines):
                        context_start = max(0, case['linha'] - 3)
                        context_end = min(len(lines), case['linha'] + 2)
                        print(f"   • Contexto do código:")
                        for line_num in range(context_start, context_end):
                            marker = ">>> " if line_num + 1 == case['linha'] else "    "
                            print(f"   {marker}{line_num + 1:3d}: {lines[line_num]}")
            except:
                print(f"   • Não foi possível ler o arquivo")

        self.audit_results['high_confidence_cases'] = {
            'count': len(high_confidence),
            'top_20': top_confidence,
            'best_5': best_cases
        }

    def generate_final_audit_report(self):
        """Gera Relatório Final da Auditoria"""

        print("\n" + "="*80)
        print("              RELATÓRIO FINAL DE AUDITORIA CIENTÍFICA")
        print("="*80)

        # Resumo Executivo
        print("\n📋 RESUMO EXECUTIVO DA AUDITORIA")
        print("-"*60)

        total_detections = self.audit_results['evidence_quality']['total_detections']
        avg_confidence = self.audit_results['evidence_quality']['confidence_mean']
        high_conf_pct = self.audit_results['evidence_quality']['high_confidence_count'] / total_detections
        false_positive_risk = self.audit_results['false_positive_analysis']['high_risk_percentage']

        print(f"• Detecções totais analisadas: {total_detections:,}")
        print(f"• Confiança média: {avg_confidence:.1%}")
        print(f"• Detecções de alta qualidade: {high_conf_pct:.1%}")
        print(f"• Risco de falso positivo: {false_positive_risk:.1%}")

        # Avaliação Final
        print(f"\n🎯 AVALIAÇÃO FINAL DA METODOLOGIA")
        print("-"*60)

        # Pontos fortes
        print("✅ PONTOS FORTES:")
        if avg_confidence >= 0.4:
            print("   • Boa confiança média nas detecções")
        if self.audit_results['file_coverage']['coverage_percentage'] >= 0.3:
            print("   • Cobertura significativa dos arquivos")
        if high_conf_pct >= 0.05:
            print("   • Presença de detecções de alta qualidade")
        if self.audit_results['statistical_validity']['coefficient_of_variation'] < 0.5:
            print("   • Consistência estatística razoável")

        # Pontos fracos
        print("\n⚠️  PONTOS DE ATENÇÃO:")
        if false_positive_risk > 0.1:
            print("   • Alta taxa de possíveis falsos positivos")
        if avg_confidence < 0.5:
            print("   • Confiança média poderia ser maior")
        if self.audit_results['evidence_quality']['low_confidence_count'] > total_detections * 0.5:
            print("   • Muitas detecções de baixa confiança")

        # Recomendações
        print("\n💡 RECOMENDAÇÕES:")
        print("   1. Aumentar threshold para 0.35-0.4 para reduzir falsos positivos")
        print("   2. Implementar validação de contexto para evitar imports/comments")
        print("   3. Refinar pesos do scoring system")
        print("   4. Adicionar filtros de exclusão para padrões conhecidos")

        # Salvar auditoria completa
        audit_file = Path(f"/tmp/COMPREHENSIVE_AUDIT_{int(self.start_time.timestamp())}.json")

        with open(audit_file, 'w') as f:
            json.dump({
                'audit_metadata': {
                    'timestamp': self.start_time.isoformat(),
                    'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                    'data_source': str(self.data_file),
                    'total_detections_analyzed': total_detections
                },
                'audit_results': self.audit_results
            }, f, indent=2, default=str)

        print(f"\n💾 Auditoria completa salva em: {audit_file}")
        print("="*80)

    def _calculate_skewness(self, data):
        """Calcula skewness"""
        n = len(data)
        if n < 3:
            return 0
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0:
            return 0
        return sum((x - mean) ** 3 for x in data) / (n * std ** 3)

    def _calculate_kurtosis(self, data):
        """Calcula kurtosis"""
        n = len(data)
        if n < 4:
            return 0
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0:
            return 0
        return sum((x - mean) ** 4 for x in data) / (n * std ** 4) - 3

# EXECUTAR AUDITORIA COMPLETA
if __name__ == "__main__":
    print("\n" + "="*80)
    print("     INICIANDO AUDITORIA CIENTÍFICA COMPLETA")
    print("     ALL DATA. ALL EVIDENCE. METHODOLOGY.")
    print("="*80)

    auditor = ComprehensiveScientificAudit()
    auditor.execute_complete_audit()
