#!/usr/bin/env python3
"""
Test Spectrometer V7 nos 50 Golden Repositories existentes
"""

import json
import time
from pathlib import Path
from spectrometer_v7_haiku import SpectrometerV7

def test_existing_golden():
    """Testa nos 50 golden repositories que já existem"""
    print("🚀 SPECTROMETER V7 - 50 GOLDEN REPOSITORIES TEST")
    print("=" * 70)

    spectrometer = SpectrometerV7()

    # Diretório dos golden repositories existentes
    # Usa o caminho que foi mostrado na execução anterior
    import subprocess
    result = subprocess.run(['find', '/var/folders', '-name', 'spectrometer_final_*', '-type', 'd'],
                          capture_output=True, text=True)
    if result.stdout.strip():
        golden_path = Path(result.stdout.strip().split('\n')[0])
    else:
        # Fallback para tmp
        golden_path = Path("/tmp/controlled_repositories")

    if not golden_path.exists():
        print(f"❌ Diretório {golden_path} não existe!")
        print("Executando controlled_validator.py primeiro...")

        # Executa controlled_validator para criar os repos
        import subprocess
        result = subprocess.run(["python3", "final_controlled_validator.py"],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Erro ao criar repositórios: {result.stderr}")
            return

    # Lista todos os repositórios
    repos = [d for d in golden_path.iterdir() if d.is_dir()]
    repos = sorted(repos)[:50]  # Pega os primeiros 50

    if len(repos) == 0:
        print("❌ Nenhum repositório encontrado!")
        return

    print(f"✅ Encontrados {len(repos)} repositórios para testar")

    # Baseline do gabarito
    baseline = {
        'total_functions': 436,
        'total_classes': 124,
        'total_imports': 213,
        'total_elements': 5141,
        'expected_hadrons': {
            'TestFunction': 80,
            'Entity': 60,
            'DTO': 45,
            'RepositoryImpl': 35,
            'Service': 40,
            'CommandHandler': 30,
            'QueryHandler': 30,
            'APIHandler': 25,
            'Constructor': 100,
            'ImportStatement': 200
        }
    }

    print(f"📊 Baseline esperado:")
    print(f"  • Funções: {baseline['total_functions']}")
    print(f"  • Classes: {baseline['total_classes']}")
    print(f"  • Imports: {baseline['total_imports']}")
    print(f"  • Total: {baseline['total_elements']} elementos")

    # Executa análise
    print(f"\n🔍 Analisando {len(repos)} repositórios...")

    results = {
        'total_repos': len(repos),
        'total_elements': 0,
        'hadrons_detected': {},
        'haiku_classifications': 0,
        'repo_results': [],
        'errors': [],
        'start_time': time.time()
    }

    for i, repo_path in enumerate(repos, 1):
        print(f"  📁 [{i:2d}/{len(repos)}] {repo_path.name}", end="")

        try:
            # Analisa com Spectrometer V7
            result = spectrometer.analyze_repository_haiku(repo_path)
            elements = result.get('elements', [])

            repo_stats = {
                'repo_name': repo_path.name,
                'elements_count': len(elements),
                'hadrons': {},
                'haiku_count': 0,
                'success': True
            }

            # Conta elementos e hadrons
            for element in elements:
                # Conta hadrons
                hadrons = element.get('hadrons', [])
                for hadron in hadrons:
                    repo_stats['hadrons'][hadron] = repo_stats['hadrons'].get(hadron, 0) + 1
                    results['hadrons_detected'][hadron] = results['hadrons_detected'].get(hadron, 0) + 1

                # Conta HAIKU
                if 'enhanced_hadrons' in element:
                    for enhanced in element['enhanced_hadrons']:
                        if enhanced.get('sub_hadrons'):
                            repo_stats['haiku_count'] += 1
                            results['haiku_classifications'] += 1

            results['total_elements'] += len(elements)
            results['repo_results'].append(repo_stats)

            print(f" ✅ {len(elements)} elementos")

        except Exception as e:
            results['errors'].append({
                'repo': repo_path.name,
                'error': str(e)
            })
            print(f" ❌ Erro: {str(e)[:50]}")

    results['end_time'] = time.time()
    duration = results['end_time'] - results['start_time']

    # Relatório final
    print("\n" + "=" * 70)
    print("📊 SPECTROMETER V7 - GOLDEN REPOSITORIES REPORT")
    print("=" * 70)

    print(f"\n⏱️  Duração: {duration:.2f} segundos")
    print(f"📁 Repositórios analisados: {len(repos) - len(results['errors'])}/{len(repos)}")
    print(f"❌ Erros: {len(results['errors'])}")

    # Comparação com baseline
    print(f"\n📊 COMPARAÇÃO COM BASELINE:")
    print(f"  • Elementos esperados: {baseline['total_elements']}")
    print(f"  • Elementos detectados: {results['total_elements']}")

    accuracy = (results['total_elements'] / baseline['total_elements']) * 100
    print(f"  • PRECISÃO: {accuracy:.1f}%")

    # Top Hadrons
    print(f"\n🎯 TOP 20 HÁDRONS DETECTADOS:")
    for hadron, count in sorted(results['hadrons_detected'].items(),
                                key=lambda x: x[1], reverse=True)[:20]:
        expected = baseline['expected_hadrons'].get(hadron, 0)
        match_pct = (count / expected * 100) if expected > 0 else 0
        print(f"  • {hadron:20} {count:4} (esperado: {expected:3}) - {match_pct:5.1f}%")

    # Estatísticas HAIKU
    haiku_stats = spectrometer.get_haiku_summary()
    haiku_coverage = (results['haiku_classifications'] / max(results['total_elements'], 1)) * 100

    print(f"\n⚛️  ESTATÍSTICAS HAIKU:")
    print(f"  • Elementos classificados com HAIKU: {results['haiku_classifications']}")
    print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}%")
    print(f"  • Sub-hádrons únicos: {len(haiku_stats.get('subhadrons_detected', set()))}")
    print(f"  • Profundidade máxima: {max(haiku_stats.get('hierarchy_depth', {}).values() or [0])}")

    # Score final
    success_rate = (len(repos) - len(results['errors'])) / len(repos) * 100
    hadron_coverage = len(results['hadrons_detected']) / 96 * 100  # 96 hadrons totais

    final_score = (accuracy * 0.4) + (haiku_coverage * 0.3) + (hadron_coverage * 0.2) + (success_rate * 0.1)

    print(f"\n🏆 SCORE FINAL SPECTROMETER V7: {final_score:.1f}/100")
    print(f"  • Precisão vs Baseline: {accuracy:.1f}% (peso 40%)")
    print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}% (peso 30%)")
    print(f"  • Cobertura Hadrons: {hadron_coverage:.1f}% (peso 20%)")
    print(f"  • Taxa de Sucesso: {success_rate:.1f}% (peso 10%)")

    # Análise por tipo de hadron
    print(f"\n📈 ANÁLISE POR CATEGORIA:")

    categories = {
        'Testes': ['TestFunction', 'TestCase', 'TestFixture'],
        'Entidades': ['Entity', 'DTO', 'ValueObject'],
        'Serviços': ['Service', 'ApplicationService', 'DomainService'],
        'Controladores': ['APIHandler', 'CommandHandler', 'QueryHandler'],
        'Infraestrutura': ['RepositoryImpl', 'DatabaseConnection', 'CacheHandler']
    }

    for category, hadron_list in categories.items():
        total = sum(results['hadrons_detected'].get(h, 0) for h in hadron_list)
        print(f"  • {category:15} {total:4} elementos")

    # Salva relatório completo
    report_file = "/tmp/spectrometer_v7_golden_test_report.json"
    final_report = {
        'test_info': {
            'total_repos': len(repos),
            'baseline': baseline,
            'duration': duration,
            'timestamp': time.time()
        },
        'results': results,
        'haiku_stats': haiku_stats,
        'final_score': final_score,
        'analysis': {
            'accuracy': accuracy,
            'haiku_coverage': haiku_coverage,
            'hadron_coverage': hadron_coverage,
            'success_rate': success_rate
        }
    }

    # Converte sets para listas
    if 'subhadrons_detected' in final_report['haiku_stats']:
        final_report['haiku_stats']['subhadrons_detected'] = list(
            final_report['haiku_stats']['subhadrons_detected']
        )

    with open(report_file, 'w') as f:
        json.dump(final_report, f, indent=2)

    print(f"\n💾 Relatório completo salvo em: {report_file}")
    print("=" * 70)

if __name__ == "__main__":
    test_existing_golden()
