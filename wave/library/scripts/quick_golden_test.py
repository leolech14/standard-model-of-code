#!/usr/bin/env python3
"""
Quick Golden Test - Versão simplificada para testar Spectrometer V7
"""

import json
import time
from pathlib import Path
from spectrometer_v7_haiku import SpectrometerV7

def quick_test():
    """Teste rápido com 10 repositórios simples"""
    print("🚀 SPECTROMETER V7 - QUICK GOLDEN TEST")
    print("=" * 60)

    spectrometer = SpectrometerV7()
    test_path = Path("/tmp/quick_golden_test")

    # Limpa e cria diretório
    if test_path.exists():
        import shutil
        shutil.rmtree(test_path)
    test_path.mkdir()

    # Cria 10 repositórios simples
    repos = []
    for i in range(1, 11):
        repo_path = test_path / f"test_repo_{i:02d}"
        repo_path.mkdir()

        # Cria arquivos Python simples com padrões conhecidos
        (repo_path / "service.py").write_text(f'''
# Service {i}
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Entity{i}:
    """Entidade {i}"""
    id: int
    name: str

class Service{i}:
    """Serviço {i}"""

    def __init__(self):
        self.repository = None

    async def process_data(self, data: List[str]) -> Optional[Entity{i}]:
        """Processa dados"""
        entity = Entity{i}(id=1, name="test")
        return entity

    def sync_method(self) -> bool:
        """Método síncrono"""
        return True
''')

        (repo_path / "test_service.py").write_text(f'''
# Test Service {i}
import pytest
from service import Service{i}, Entity{i}

class TestService{i}:
    """Teste do serviço {i}"""

    def test_creation(self):
        """Testa criação"""
        service = Service{i}()
        assert service is not None

    def test_sync_method(self):
        """Testa método síncrono"""
        service = Service{i}()
        result = service.sync_method()
        assert result is True

    async def test_async_method(self):
        """Testa método assíncrono"""
        service = Service{i}()
        result = await service.process_data(["test"])
        assert result is not None
''')

        repos.append(repo_path)

    print(f"✅ Criados {len(repos)} repositórios de teste")

    # Executa análise
    print("\n🔍 Analisando repositórios...")
    total_elements = 0
    total_hadrons = {}
    haiku_classifications = 0
    start_time = time.time()

    for i, repo_path in enumerate(repos, 1):
        print(f"  📁 [{i:2d}/10] {repo_path.name}")

        try:
            result = spectrometer.analyze_repository_haiku(repo_path)
            elements = result.get('elements', [])
            total_elements += len(elements)

            # Conta hadrons
            for element in elements:
                hadrons = element.get('hadrons', [])
                for hadron in hadrons:
                    total_hadrons[hadron] = total_hadrons.get(hadron, 0) + 1

                # Conta HAIKU
                if 'enhanced_hadrons' in element:
                    for enhanced in element['enhanced_hadrons']:
                        if enhanced.get('sub_hadrons'):
                            haiku_classifications += 1

        except Exception as e:
            print(f"    ❌ Erro: {e}")

    duration = time.time() - start_time

    # Relatório
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DO QUICK TEST")
    print("=" * 60)
    print(f"⏱️  Duração: {duration:.2f} segundos")
    print(f"📁 Repositórios: {len(repos)}")
    print(f"🔢 Elementos detectados: {total_elements}")
    print(f"⚛️  Classificações HAIKU: {haiku_classifications}")
    print(f"🎯 Hadrons únicos: {len(total_hadrons)}")

    print(f"\n🎯 TOP 15 HÁDRONS:")
    for hadron, count in sorted(total_hadrons.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  • {hadron:20} {count:3} ocorrências")

    # Estatísticas HAIKU
    haiku_stats = spectrometer.get_haiku_summary()
    print(f"\n⚛️  ESTATÍSTICAS HAIKU:")
    print(f"  • Total classificado: {haiku_stats.get('total_classified', 0)}")
    print(f"  • Sub-hádrons detectados: {len(haiku_stats.get('subhadrons_detected', set()))}")
    print(f"  • Profundidade máxima: {max(haiku_stats.get('hierarchy_depth', {}).values() or [0])}")
    print(f"  • Confiança média: {haiku_stats.get('average_confidence', 0)*100:.1f}%")

    # Score final
    haiku_coverage = (haiku_classifications / max(total_elements, 1)) * 100
    hadron_diversity = (len(total_hadrons) / 96) * 100  # 96 hadrons totais
    final_score = (haiku_coverage * 0.5) + (hadron_diversity * 0.3) + (50 * 0.2)  # baseline fixo

    print(f"\n🏆 SCORE FINAL: {final_score:.1f}/100")
    print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}% (peso 50%)")
    print(f"  • Diversidade de Hadrons: {hadron_diversity:.1f}% (peso 30%)")
    print(f"  • Baseline: 50.0% (peso 20%)")

    # Salva resultado
    result_data = {
        'test_type': 'quick_golden_test',
        'repos_count': len(repos),
        'total_elements': total_elements,
        'haiku_classifications': haiku_classifications,
        'hadrons_detected': total_hadrons,
        'haiku_stats': haiku_stats,
        'duration': duration,
        'final_score': final_score
    }

    with open("/tmp/quick_golden_test_result.json", "w") as f:
        json.dump(result_data, f, indent=2)

    print(f"\n💾 Resultado salvo em: /tmp/quick_golden_test_result.json")
    print("=" * 60)

if __name__ == "__main__":
    quick_test()
