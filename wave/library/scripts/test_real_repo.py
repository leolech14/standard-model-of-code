#!/usr/bin/env python3
"""
Teste o parser no arquivo real do repositório
"""

from parser_working import WorkingParser
from pathlib import Path

def test_real_repo():
    print("🔍 TESTANDO EM REPOSITÓRIO REAL")
    print("="*50)

    parser = WorkingParser()

    # Lista de arquivos para testar
    test_files = [
        "/tmp/test_repo/src/user_service.py",
        "/tmp/test_repo/tests/test_user_service.py",
        "/tmp/test_repo/config.json"  # Para ver se lida (deve ser ignorado)
    ]

    total_elements = []
    all_hadrons = {}

    for file_path in test_files:
        path = Path(file_path)
        print(f"\n📁 Analisando: {path.name}")

        if path.exists():
            elements = parser.parse_file(path)
            total_elements.extend(elements)

            print(f"  ✅ Detectados: {len(elements)} elementos")

            # Mostra alguns exemplos
            for elem in elements[:5]:
                hadron_info = f"→ {elem['hadron']}" if elem.get('hadron') else ""
                print(f"     • {elem['type']:12} {elem['content'][:40]} {hadron_info}")

            # Conta hadrons
            for elem in elements:
                if elem.get('hadron'):
                    all_hadrons[elem['hadron']] = all_hadrons.get(elem['hadron'], 0) + 1
        else:
            print(f"  ❌ Arquivo não encontrado")

    print("\n" + "="*50)
    print("📊 RESUMO FINAL")
    print(f"• Total de elementos: {len(total_elements)}")
    print(f"• Hádrons únicos: {len(all_hadrons)}")
    print(f"• Hádrons detectados:")

    for hadron, count in sorted(all_hadrons.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {hadron}: {count}")

    # Gera relatório completo
    print("\n" + parser.generate_real_report())

    return total_elements

if __name__ == "__main__":
    test_real_repo()
