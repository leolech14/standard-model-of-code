#!/usr/bin/env python3
"""
SPECTROMETER V7 - FINAL TEST
Teste completo em repositórios recém-criados
"""

import json
import time
from pathlib import Path
from spectrometer_v7_haiku import SpectrometerV7
import tempfile
import shutil

def create_simple_golden_repos():
    """Cria 50 repositórios simples para teste"""
    print("🏗️  Criando 50 repositórios golden simples...")

    temp_dir = Path(tempfile.mkdtemp(prefix="spectrometer_v7_golden_"))
    print(f"📁 Diretório: {temp_dir}")

    # Template de repositório com padrões conhecidos
    repo_templates = [
        ("microservice", 15),
        ("api", 10),
        ("library", 10),
        ("cli", 8),
        ("webapp", 7)
    ]

    repo_count = 0
    for repo_type, count in repo_templates:
        for i in range(count):
            repo_count += 1
            repo_path = temp_dir / f"{repo_type}_{repo_count:02d}"
            repo_path.mkdir()

            # Cria arquivos baseado no tipo
            if repo_type == "microservice":
                create_microservice(repo_path, repo_count)
            elif repo_type == "api":
                create_api(repo_path, repo_count)
            elif repo_type == "library":
                create_library(repo_path, repo_count)
            elif repo_type == "cli":
                create_cli(repo_path, repo_count)
            elif repo_type == "webapp":
                create_webapp(repo_path, repo_count)

            if repo_count % 10 == 0:
                print(f"  ✅ {repo_count}/50 criados")

    return temp_dir

def create_microservice(path: Path, index: int):
    """Cria microsserviço"""
    (path / "src").mkdir()
    (path / "tests").mkdir()

    # Entidade
    (path / "src" / "entity.py").write_text(f'''
from dataclasses import dataclass

@dataclass
class User{index}:
    """Entidade de usuário"""
    id: int
    name: str
    email: str
''')

    # Repository
    (path / "src" / "repository.py").write_text(f'''
from typing import Optional, List
from .entity import User{index}

class UserRepository{index}:
    """Repositório de usuários"""

    def save(self, user: User{index}) -> User{index}:
        """Salva usuário"""
        return user

    def find_by_id(self, user_id: int) -> Optional[User{index}]:
        """Busca por ID"""
        return None

    def find_all(self) -> List[User{index}]:
        """Lista todos"""
        return []
''')

    # Service
    (path / "src" / "service.py").write_text(f'''
from typing import Optional
from .entity import User{index}
from .repository import UserRepository{index}

class UserService{index}:
    """Serviço de usuários"""

    def __init__(self):
        self.repository = UserRepository{index}()

    async def create_user(self, name: str, email: str) -> User{index}:
        """Cria usuário"""
        user = User{index}(id=1, name=name, email=email)
        return self.repository.save(user)

    def get_user(self, user_id: int) -> Optional[User{index}]:
        """Obtém usuário"""
        return self.repository.find_by_id(user_id)
''')

    # Controller/API Handler
    (path / "src" / "controller.py").write_text(f'''
from typing import List
from .service import UserService{index}
from .entity import User{index}

class UserController{index}:
    """Controller de usuários"""

    def __init__(self):
        self.service = UserService{index}()

    async def handle_create_user(self, name: str, email: str) -> dict:
        """Handler para criação"""
        user = await self.service.create_user(name, email)
        return {{"id": user.id, "name": user.name}}

    async def handle_get_user(self, user_id: int) -> dict:
        """Handler para busca"""
        user = self.service.get_user(user_id)
        return {{"id": user.id}} if user else {{}}
''')

    # Tests
    (path / "tests" / "test_service.py").write_text(f'''
import pytest
from unittest.mock import Mock
from src.service import UserService{index}
from src.entity import User{index}

class TestUserService{index}:
    """Testes do serviço"""

    def test_create_user(self):
        """Testa criação"""
        service = UserService{index}()
        user = service.create_user("Test", "test@email.com")
        assert user.name == "Test"
        assert user.email == "test@email.com"

    def test_get_user_not_found(self):
        """Testa busca não encontrada"""
        service = UserService{index}()
        user = service.get_user(999)
        assert user is None

    async def test_async_create(self):
        """Testa criação assíncrona"""
        service = UserService{index}()
        user = await service.create_user("Async", "async@email.com")
        assert user.name == "Async"
''')

def create_api(path: Path, index: int):
    """Cria API REST"""
    (path / "app.py").write_text(f'''
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel

class ItemDTO{index}(BaseModel):
    """DTO de Item"""
    name: str
    price: float

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint"""
    return {{"message": "API {index}"}}

@app.get("/items/{{item_id}}")
async def get_item(item_id: int):
    """Obtém item"""
    if item_id <= 0:
        raise HTTPException(status_code=400)
    return {{"id": item_id, "name": "Item {index}"}}

@app.post("/items")
async def create_item(item: ItemDTO{index}):
    """Cria item"""
    return {{"id": 1, "name": item.name, "price": item.price}}
''')

    (path / "test_app.py").write_text(f'''
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root():
    """Testa root"""
    response = client.get("/")
    assert response.status_code == 200
    assert "API {index}" in response.json()["message"]

def test_get_item():
    """Testa get item"""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_item():
    """Testa create item"""
    response = client.post("/items", json={{"name": "Test", "price": 10.0}})
    assert response.status_code == 200
''')

def create_library(path: Path, index: int):
    """Cria biblioteca"""
    (path / f"lib{index}").mkdir()

    (path / f"lib{index}" / "__init__.py").write_text(f'''
"""
Biblioteca {index}
"""

from .core import Utils{index}
from .validators import Validator{index}

__version__ = "1.0.{index}"
__all__ = ["Utils{index}", "Validator{index}"]
''')

    (path / f"lib{index}" / "core.py").write_text(f'''
import hashlib
from typing import Any, List

class Utils{index}:
    """Utilitários diversos"""

    @staticmethod
    def hash_string(text: str) -> str:
        """Gera hash MD5"""
        return hashlib.md5(text.encode()).hexdigest()

    def process_list(self, items: List[Any]) -> List[Any]:
        """Processa lista"""
        return [item for item in items if item is not None]

    def calculate_sum(self, numbers: List[float]) -> float:
        """Calcula soma"""
        return sum(numbers)
''')

    (path / f"lib{index}" / "validators.py").write_text(f'''
from typing import Dict, List
import re

class Validator{index}:
    """Validador de dados"""

    def validate_email(self, email: str) -> bool:
        """Valida email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_required_fields(self, data: Dict, required: List[str]) -> bool:
        """Valida campos obrigatórios"""
        return all(field in data for field in required)

    def validate_positive_number(self, value: float) -> bool:
        """Valida número positivo"""
        return value > 0
''')

def create_cli(path: Path, index: int):
    """Cria CLI tool"""
    (path / "cli.py").write_text(f'''
import argparse
import sys

class CLI{index}:
    """Ferramenta CLI {index}"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=f"CLI Tool {index}")
        self.setup_commands()

    def setup_commands(self):
        """Configura comandos"""
        subparsers = self.parser.add_subparsers(dest='command')

        # Comando process
        process_parser = subparsers.add_parser('process')
        process_parser.add_argument('--input', required=True)
        process_parser.add_argument('--output', required=False)

        # Comando validate
        validate_parser = subparsers.add_parser('validate')
        validate_parser.add_argument('file', help='Arquivo para validar')

    def run(self, args=None):
        """Executa CLI"""
        parsed = self.parser.parse_args(args)

        if parsed.command == 'process':
            self.handle_process(parsed)
        elif parsed.command == 'validate':
            self.handle_validate(parsed)
        else:
            self.parser.print_help()

    def handle_process(self, args):
        """Processa dados"""
        print(f"Processando {{args.input}}")

    def handle_validate(self, args):
        """Valida arquivo"""
        print(f"Validando {{args.file}}")

def main():
    """Main"""
    cli = CLI{index}()
    cli.run()

if __name__ == "__main__":
    main()
''')

def create_webapp(path: Path, index: int):
    """Cria web app"""
    (path / "app.py").write_text(f'''
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    """Página inicial"""
    return "<h1>Web App {index}</h1><p>Bem-vindo!</p>"

@app.route("/api/data", methods=["GET"])
def get_data():
    """API endpoint"""
    data = [
        {{"id": 1, "name": "Item {index}-1"}},
        {{"id": 2, "name": "Item {index}-2"}}
    ]
    return jsonify(data)

@app.route("/api/data", methods=["POST"])
def create_data():
    """Cria dados"""
    data = request.json
    return jsonify({{"success": True, "data": data}})
''')

    (path / "config.py").write_text(f'''
"""
Configuração do Web App {index}
"""
import os

class Config:
    """Configuração base"""
    SECRET_KEY = "secret-{index}"
    DEBUG = True

class DevelopmentConfig(Config):
    """Config de desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Config de produção"""
    DEBUG = False

config = {{
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}}
''')

def run_final_test():
    """Executa teste final do Spectrometer V7"""
    print("\n" + "="*80)
    print("🚀 SPECTROMETER V7 - FINAL TEST ON 50 GOLDEN REPOSITORIES")
    print("="*80)

    # Cria repositórios
    repos_path = create_simple_golden_repos()
    repos = [d for d in repos_path.iterdir() if d.is_dir()]

    print(f"\n✅ Criados {len(repos)} repositórios em {repos_path}")

    # Inicializa Spectrometer V7
    spectrometer = SpectrometerV7()

    # Baseline esperado baseado nos templates
    baseline = {
        'total_elements_per_repo': 20,  # média esperada
        'expected_hadrons': {
            'Entity': 50,         # 1 por repo
            'RepositoryImpl': 50, # 1 por repo
            'Service': 50,       # 1 por repo
            'APIHandler': 75,    # 1.5 por repo (média)
            'TestFunction': 100, # 2 por repo
            'DTO': 25,           # 0.5 por repo
            'Constructor': 150,  # 3 por repo
            'AsyncFunction': 75, # 1.5 por repo
            'ImportStatement': 100, # 2 por repo
        }
    }

    print(f"\n📊 Baseline estimado:")
    total_expected = sum(baseline['expected_hadrons'].values())
    print(f"  • Total hadrons esperados: {total_expected}")
    print(f"  • Média por repo: {total_expected / len(repos):.1f}")

    # Executa análise
    print(f"\n🔍 Analisando repositórios com Spectrometer V7...")

    results = {
        'total_repos': len(repos),
        'total_elements': 0,
        'hadrons_detected': {},
        'haiku_classifications': 0,
        'repo_details': [],
        'start_time': time.time()
    }

    for i, repo_path in enumerate(repos, 1):
        print(f"  📁 [{i:2d}/{len(repos)}] {repo_path.name}", end="")

        try:
            # Analisa com V7 + HAIKU
            result = spectrometer.analyze_repository_haiku(repo_path)
            elements = result.get('elements', [])

            repo_detail = {
                'name': repo_path.name,
                'elements': len(elements),
                'hadrons': {},
                'haiku_count': 0
            }

            # Processa elementos
            for element in elements:
                # Conta hadrons
                hadrons = element.get('hadrons', [])
                for hadron in hadrons:
                    repo_detail['hadrons'][hadron] = repo_detail['hadrons'].get(hadron, 0) + 1
                    results['hadrons_detected'][hadron] = results['hadrons_detected'].get(hadron, 0) + 1

                # Conta HAIKU
                if 'enhanced_hadrons' in element:
                    for enhanced in element['enhanced_hadrons']:
                        if enhanced.get('sub_hadrons'):
                            repo_detail['haiku_count'] += 1
                            results['haiku_classifications'] += 1

            results['total_elements'] += len(elements)
            results['repo_details'].append(repo_detail)

            print(f" ✅ {len(elements)} elems | {repo_detail['haiku_count']} HAIKU")

        except Exception as e:
            print(f" ❌ Erro: {str(e)[:50]}")

    results['end_time'] = time.time()
    duration = results['end_time'] - results['start_time']

    # Relatório final
    print("\n" + "="*80)
    print("📊 SPECTROMETER V7 - FINAL RESULTS")
    print("="*80)

    print(f"\n⏱️  Duração total: {duration:.2f} segundos")
    print(f"📁 Repositórios analisados: {len(repos)}")
    print(f"🔢 Total de elementos detectados: {results['total_elements']}")
    print(f"⚛️  Classificações HAIKU: {results['haiku_classifications']}")

    # Comparação com baseline
    print(f"\n📊 COMPARAÇÃO COM BASELINE:")
    print(f"  • Hadrons esperados: {total_expected}")
    print(f"  • Hadrons detectados: {sum(results['hadrons_detected'].values())}")

    detection_rate = (sum(results['hadrons_detected'].values()) / total_expected) * 100
    print(f"  • Taxa de detecção: {detection_rate:.1f}%")

    # Top hadrons detectados
    print(f"\n🎯 TOP 15 HÁDRONS DETECTADOS:")
    for hadron, count in sorted(results['hadrons_detected'].items(),
                                key=lambda x: x[1], reverse=True)[:15]:
        expected = baseline['expected_hadrons'].get(hadron, 0)
        pct = (count / expected * 100) if expected > 0 else 0
        print(f"  • {hadron:20} {count:4} (esperado: {expected:3}) - {pct:5.1f}%")

    # Estatísticas HAIKU
    haiku_stats = spectrometer.get_haiku_summary()
    haiku_coverage = (results['haiku_classifications'] / max(results['total_elements'], 1)) * 100

    print(f"\n⚛️  HAIKU SUB-AGENTS PERFORMANCE:")
    print(f"  • Elementos com sub-hádrons: {results['haiku_classifications']}")
    print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}%")
    print(f"  • Sub-hádrons únicos: {len(haiku_stats.get('subhadrons_detected', set()))}")
    print(f"  • Profundidade máxima: {max(haiku_stats.get('hierarchy_depth', {}).values() or [0])}")
    print(f"  • Confiança média: {haiku_stats.get('average_confidence', 0)*100:.1f}%")

    # Score final
    hadron_diversity = len(results['hadrons_detected']) / 96 * 100
    haiku_score = haiku_coverage * 0.4 + hadron_diversity * 0.3 + detection_rate * 0.3

    print(f"\n🏆 SCORE FINAL SPECTROMETER V7: {haiku_score:.1f}/100")
    print(f"  • Detecção de Hadrons: {detection_rate:.1f}% (peso 30%)")
    print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}% (peso 40%)")
    print(f"  • Diversidade de Hadrons: {hadron_diversity:.1f}% (peso 30%)")

    # Análise qualitativa
    print(f"\n📈 ANÁLISE POR TIPO DE REPOSITÓRIO:")
    repo_types = {}
    for repo in results['repo_details']:
        repo_type = repo['name'].split('_')[0]
        if repo_type not in repo_types:
            repo_types[repo_type] = {'count': 0, 'elements': 0, 'haiku': 0}
        repo_types[repo_type]['count'] += 1
        repo_types[repo_type]['elements'] += repo['elements']
        repo_types[repo_type]['haiku'] += repo['haiku_count']

    for repo_type, stats in repo_types.items():
        avg_elements = stats['elements'] / stats['count']
        avg_haiku = stats['haiku'] / stats['count']
        print(f"  • {repo_type:12} {stats['count']:2} repos | "
              f"{avg_elements:.1f} elems/repo | {avg_haiku:.1f} HAIKU/repo")

    # Salva relatório completo
    report_path = "/tmp/spectrometer_v7_final_report.json"
    final_report = {
        'test_info': {
            'total_repos': len(repos),
            'duration': duration,
            'timestamp': time.time(),
            'baseline': baseline
        },
        'results': results,
        'haiku_stats': haiku_stats,
        'scores': {
            'detection_rate': detection_rate,
            'haiku_coverage': haiku_coverage,
            'hadron_diversity': hadron_diversity,
            'final_score': haiku_score
        }
    }

    # Converte sets para listas
    if 'subhadrons_detected' in final_report['haiku_stats']:
        final_report['haiku_stats']['subhadrons_detected'] = list(
            final_report['haiku_stats']['subhadrons_detected']
        )

    with open(report_path, 'w') as f:
        json.dump(final_report, f, indent=2)

    print(f"\n💾 Relatório completo salvo em: {report_path}")

    # Cleanup
    print(f"\n🧹 Limpando diretório temporário...")
    shutil.rmtree(repos_path)
    print(f"✅ Teste concluído com sucesso!")
    print("="*80)

if __name__ == "__main__":
    run_final_test()