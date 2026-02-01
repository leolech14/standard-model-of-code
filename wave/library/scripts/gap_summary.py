#!/usr/bin/env python3
"""
Resumo executivo da análise de gaps
"""

import json
from pathlib import Path

def main():
    # Carrega resultados
    with open("batch_analysis_results.json", 'r') as f:
        results = json.load(f)

    stats = results["global_statistics"]

    print("="*60)
    print("SPECTROMETER v4 - GAP ANALYSIS SUMMARY")
    print("="*60)

    print(f"\n📊 CURRENT STATUS:")
    print(f"  Repositórios analisados: {results['experiment_metadata']['sample_size']}")
    print(f"  Arquivos analisados: {stats['total_files_analyzed']:,}")
    print(f"  Elementos classificados: {stats['total_elements_classified']:,}")
    print(f"  Hádrons encontrados: {stats['unique_hadrons_found']}/96")
    print(f"  Cobertura: {stats['hadron_coverage']}%")
    print(f"  Confiança média: {stats['average_confidence']:.1%}")

    print(f"\n🔍 TOP 10 HÁDRONS MAIS COMUNS:")
    for hadron, count in stats["most_common_hadrons"]:
        print(f"  • {hadron}: {count:,} ocorrências")

    print(f"\n❌ HÁDRONS NÃO ENCONTRADOS (Top 20):")
    for hadron in stats["missing_hadrons"][:20]:
        print(f"  • {hadron}")

    print(f"\n💡 INSIGHTS PRINCIPAIS:")
    print("  1. COBERTURA BAIXA (52.3%) indica problema de detecção")
    print("  2. Hádrons de baixo nível (sintaxe) não foram detectados")
    print("  3. Padrões comuns como TryCatch, InstanceField estão faltando")
    print("  4. Concentração em LOGIC_FLOW (60.8%) vs EXECUTION (1.3%)")

    print(f"\n🎯 RECOMENDAÇÕES:")
    print("\nALTA PRIORIDADE:")
    print("  1. Melhorar heurísticas de detecção para os 20 hádrons mais comuns")
    print("  2. Adicionar suporte multi-linguagem (Java, Go, TypeScript)")
    print("  3. Implementar detecção de try/catch/except universal")

    print("\nMÉDIA PRIORIDADE:")
    print("  1. Fundir hádrons similares (BitFlag, BitMask → BitOperation)")
    print("  2. Remover hádrons teóricos (ChaosMonkey, SelfHealingProbe)")
    print("  3. Adicionar hádrons genéricos (FieldAccess, ImportStatement)")

    print("\nBAIXA PRIORIDADE:")
    print("  1. Expandir para 128 hádrons se novos padrões emergirem")
    print("  2. Implementar LLM para casos ambíguos")

    print("\n📈 PROJEÇÃO PÓS-AJUSTES:")
    print("  • Taxonomia ajustada: ~85 hádrons")
    print("  • Cobertura estimada: 75%+")
    print("  • Confiança estimada: 80%+")

    # Salva resumo
    summary = {
        "current_status": {
            "hadrons_found": stats["unique_hadrons_found"],
            "coverage": stats["hadron_coverage"],
            "confidence": stats["average_confidence"]
        },
        "top_missing": stats["missing_hadrons"][:15],
        "key_insights": [
            "Detection problem, not taxonomy problem",
            "Need multi-language support",
            "Missing common syntax patterns"
        ],
        "priority_fixes": [
            "Improve TryCatch detection",
            "Add InstanceField/StaticField patterns",
            "Support Java/Go/TypeScript"
        ],
        "projected_improvement": {
            "taxonomy_size": 85,
            "estimated_coverage": 75,
            "estimated_confidence": 80
        }
    }

    with open("gap_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n📁 Resumo salvo em: gap_summary.json")
    print("="*60)

if __name__ == "__main__":
    main()
