#!/usr/bin/env python3
"""
SPECTROMETER V7 - GOLDEN REPOSITORY VALIDATOR
Teste completo nos 50 repositórios controle com gabarito conhecido
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from spectrometer_v7_haiku import SpectrometerV7
from datetime import datetime

class GoldenValidatorV7:
    """Validador para repositórios golden com Spectrometer V7"""

    def __init__(self):
        self.spectrometer = SpectrometerV7()
        self.results = {
            'total_repos': 0,
            'total_elements_expected': 0,
            'total_elements_detected': 0,
            'repo_results': [],
            'hadron_stats': {},
            'haiku_stats': {},
            'errors': [],
            'start_time': None,
            'end_time': None
        }

        # Gabarito dos 50 repositórios (baseado no controlled_validator)
        self.golden_repos_baseline = {
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
                'ImportStatement': 200,
                'AsyncFunction': 50
            }
        }

    def create_test_repositories(self) -> List[Path]:
        """Cria os 50 repositórios de teste com padrões conhecidos"""
        repos = []
        base_path = Path("/tmp/golden_repos_v7")

        # Limpa diretórios anteriores
        if base_path.exists():
            import shutil
            shutil.rmtree(base_path)
        base_path.mkdir(parents=True)

        print(f"🏗️  Criando 50 repositórios golden em {base_path}")

        # Tipos de repositórios baseados em padrões reais
        repo_templates = [
            ("microservice", 15),      # 15 microsserviços
            ("web_api", 10),           # 10 APIs REST
            ("data_pipeline", 5),      # 5 pipelines de dados
            ("ml_service", 5),         # 5 serviços de ML
            ("library", 8),            # 8 bibliotecas
            ("cli_tool", 7),           # 7 ferramentas CLI
        ]

        repo_count = 0
        for repo_type, count in repo_templates:
            for i in range(count):
                repo_count += 1
                repo_path = base_path / f"{repo_type}_{repo_count:02d}"

                # Cria estrutura do repositório
                self._create_repo_structure(repo_path, repo_type, i)
                repos.append(repo_path)

                if repo_count % 10 == 0:
                    print(f"  ✅ Criados {repo_count}/50 repositórios")

        print(f"✅ Total de {len(repos)} repositórios criados")
        return repos

    def _create_repo_structure(self, repo_path: Path, repo_type: str, index: int):
        """Cria estrutura específica para cada tipo de repositório"""
        repo_path.mkdir(parents=True)

        if repo_type == "microservice":
            self._create_microservice(repo_path, index)
        elif repo_type == "web_api":
            self._create_web_api(repo_path, index)
        elif repo_type == "data_pipeline":
            self._create_data_pipeline(repo_path, index)
        elif repo_type == "ml_service":
            self._create_ml_service(repo_path, index)
        elif repo_type == "library":
            self._create_library(repo_path, index)
        elif repo_type == "cli_tool":
            self._create_cli_tool(repo_path, index)

    def _create_microservice(self, path: Path, index: int):
        """Cria microsserviço com padrões conhecidos"""
        # src/models/entities.py
        (path / "src").mkdir()
        (path / "src" / "models").mkdir()
        (path / "src" / "repositories").mkdir()
        (path / "src" / "services").mkdir()
        (path / "src" / "controllers").mkdir()
        (path / "tests").mkdir()

        # Entidades
        entities_code = f'''"""
Entidades do microsserviço {index}
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User{index}:
    """Entidade de usuário"""
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    created_at: Optional[datetime] = None

@dataclass
class Order{index}:
    """Entidade de pedido"""
    id: Optional[int] = None
    user_id: int = 0
    total: float = 0.0
    status: str = "pending"
'''
        (path / "src" / "models" / "entities.py").write_text(entities_code)

        # DTOs
        dto_code = f'''"""
DTOs do microsserviço {index}
"""
from pydantic import BaseModel
from typing import Optional

class UserCreateDTO{index}(BaseModel):
    """DTO para criação de usuário"""
    name: str
    email: str

class UserResponseDTO{index}(BaseModel):
    """DTO para resposta de usuário"""
    id: int
    name: str
    email: str
'''
        (path / "src" / "models" / "dtos.py").write_text(dto_code)

        # Repositórios
        repo_code = f'''"""
Repositórios do microsserviço {index}
"""
from typing import List, Optional
from ..models.entities import User{index}, Order{index}

class UserRepository{index}:
    """Repositório de usuários"""

    def save(self, user: User{index}) -> User{index}:
        """Salva usuário"""
        pass

    def find_by_id(self, user_id: int) -> Optional[User{index}]:
        """Busca usuário por ID"""
        pass

    def find_all(self) -> List[User{index}]:
        """Lista todos usuários"""
        pass
'''
        (path / "src" / "repositories" / "user_repository.py").write_text(repo_code)

        # Serviços
        service_code = f'''"""
Serviços do microsserviço {index}
"""
from typing import List, Optional
from ..models.entities import User{index}
from ..repositories.user_repository import UserRepository{index}

class UserService{index}:
    """Serviço de usuários"""

    def __init__(self, repository: UserRepository{index}):
        self.repository = repository

    async def create_user(self, name: str, email: str) -> User{index}:
        """Cria novo usuário"""
        user = User{index}(name=name, email=email)
        return self.repository.save(user)

    async def get_user(self, user_id: int) -> Optional[User{index}]:
        """Obtém usuário por ID"""
        return self.repository.find_by_id(user_id)
'''
        (path / "src" / "services" / "user_service.py").write_text(service_code)

        # Controllers/API Handlers
        controller_code = f'''"""
Controllers do microsserviço {index}
"""
from fastapi import APIRouter, Depends
from typing import List
from ..services.user_service import UserService{index}
from ..models.dtos import UserCreateDTO{index}, UserResponseDTO{index}

router = APIRouter(prefix="/api/v1/users")

@router.post("/", response_model=UserResponseDTO{index})
async def create_user(
    user_data: UserCreateDTO{index},
    service: UserService{index} = Depends()
):
    """Cria novo usuário"""
    user = await service.create_user(user_data.name, user_data.email)
    return UserResponseDTO{index}(id=user.id, name=user.name, email=user.email)

@router.get("/{{user_id}}", response_model=UserResponseDTO{index})
async def get_user(
    user_id: int,
    service: UserService{index} = Depends()
):
    """Obtém usuário por ID"""
    user = await service.get_user(user_id)
    return UserResponseDTO{index}(id=user.id, name=user.name, email=user.email)
'''
        (path / "src" / "controllers" / "user_controller.py").write_text(controller_code)

        # Testes
        test_code = f'''"""
Testes do microsserviço {index}
"""
import pytest
from unittest.mock import Mock
from src.services.user_service import UserService{index}
from src.repositories.user_repository import UserRepository{index}
from src.models.entities import User{index}

class TestUserService{index}:
    """Testes do serviço de usuários"""

    def test_create_user_success(self):
        """Testa criação de usuário com sucesso"""
        repository = Mock(spec=UserRepository{index})
        service = UserService{index}(repository)

        user_data = User{index}(name="Test User", email="test@email.com")
        repository.save.return_value = user_data

        result = service.create_user("Test User", "test@email.com")

        assert result.name == "Test User"
        assert result.email == "test@email.com"
        repository.save.assert_called_once()

    def test_get_user_found(self):
        """Testa busca de usuário encontrado"""
        repository = Mock(spec=UserRepository{index})
        service = UserService{index}(repository)

        user = User{index}(id=1, name="Test", email="test@email.com")
        repository.find_by_id.return_value = user

        result = service.get_user(1)

        assert result is not None
        assert result.id == 1
        repository.find_by_id.assert_called_once_with(1)
'''
        (path / "tests" / "test_user_service.py").write_text(test_code)

        # Main/entry point
        main_code = f'''"""
Entry point do microsserviço {index}
"""
import asyncio
from src.controllers.user_controller import router

async def main():
    """Função principal"""
    print("Microsserviço {index} iniciado")

if __name__ == "__main__":
    asyncio.run(main())
'''
        (path / "main.py").write_text(main_code)

    def _create_web_api(self, path: Path, index: int):
        """Cria Web API com padrões REST"""
        (path / "app").mkdir()
        (path / "app" / "api").mkdir()
        (path / "app" / "models").mkdir()
        (path / "tests").mkdir()

        # Models
        models_code = f'''"""
Models da Web API {index}
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product{index}(Base):
    """Modelo de Produto"""
    __tablename__ = "products_{index}"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Integer)  # preço em centavos

    def calculate_discount(self, percentage: float) -> int:
        """Calcula desconto"""
        return int(self.price * (1 - percentage / 100))
'''
        (path / "app" / "models" / "product.py").write_text(models_code)

        # API Routes
        routes_code = f'''"""
API Routes {index}
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models.product import Product{index}

router = APIRouter(prefix="/products")

@router.get("/")
async def list_products() -> List[dict]:
    """Lista todos produtos"""
    return [
        {{"id": 1, "name": "Product {index}-1", "price": 1000}},
        {{"id": 2, "name": "Product {index}-2", "price": 2000}}
    ]

@router.get("/{{product_id}}")
async def get_product(product_id: int):
    """Obtém produto por ID"""
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    return {{"id": product_id, "name": "Product {index}", "price": 1500}}
'''
        (path / "app" / "api" / "products.py").write_text(routes_code)

        # Tests
        test_code = f'''"""
Testes da API {index}
"""
import pytest
from fastapi.testclient import TestClient
from app.api.products import router

client = TestClient(router)

def test_list_products():
    """Testa listagem de produtos"""
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_product():
    """Testa busca de produto"""
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_product_invalid():
    """Testa busca com ID inválido"""
    response = client.get("/products/0")
    assert response.status_code == 400
'''
        (path / "tests" / "test_products.py").write_text(test_code)

    def _create_data_pipeline(self, path: Path, index: int):
        """Cria pipeline de dados"""
        (path / "pipeline").mkdir()
        (path / "pipeline" / "extractors").mkdir()
        (path / "pipeline" / "transformers").mkdir()
        (path / "pipeline" / "loaders").mkdir()

        # Extractor
        extractor_code = f'''"""
Extractor {index}
"""
import pandas as pd
from typing import Iterator, Dict, Any

class DataExtractor{index}:
    """Extrator de dados"""

    def __init__(self, source_path: str):
        self.source_path = source_path

    def extract_csv(self) -> Iterator[pd.DataFrame]:
        """Extrai dados de CSV"""
        for file_path in Path(self.source_path).glob("*.csv"):
            yield pd.read_csv(file_path)

    def extract_from_api(self, url: str) -> Dict[str, Any]:
        """Extrai dados de API"""
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
'''
        (path / "pipeline" / "extractors" / "csv_extractor.py").write_text(extractor_code)

        # Transformer
        transformer_code = f'''"""
Transformer {index}
"""
import pandas as pd
from typing import List, Dict

class DataTransformer{index}:
    """Transformador de dados"""

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa dados"""
        return df.dropna().drop_duplicates()

    def aggregate_metrics(self, df: pd.DataFrame) -> Dict:
        """Agrega métricas"""
        return {{
            "total_rows": len(df),
            "unique_values": df.nunique().to_dict(),
            "null_counts": df.isnull().sum().to_dict()
        }}
'''
        (path / "pipeline" / "transformers" / "data_transformer.py").write_text(transformer_code)

    def _create_ml_service(self, path: Path, index: int):
        """Cria serviço de Machine Learning"""
        (path / "ml").mkdir()
        (path / "ml" / "models").mkdir()
        (path / "ml" / "preprocessors").mkdir()

        # ML Model
        model_code = f'''"""
ML Model {index}
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import Tuple, List

class MLPredictor{index}:
    """Preditor ML"""

    def __init__(self, n_estimators: int = 100):
        self.model = RandomForestClassifier(n_estimators=n_estimators)
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray) -> float:
        """Treina modelo"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        return self.model.score(X_test, y_test)

    def predict(self, X: np.ndarray) -> List[int]:
        """Faz predições"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict(X).tolist()
'''
        (path / "ml" / "models" / "predictor.py").write_text(model_code)

    def _create_library(self, path: Path, index: int):
        """Cria biblioteca reutilizável"""
        (path / f"library{index}").mkdir()

        # Library core
        lib_code = f'''"""
Library {index} - Utilitários diversos
"""
from typing import Any, List, Dict
import hashlib
import json

class StringUtils{index}:
    """Utilitários de strings"""

    @staticmethod
    def slugify(text: str) -> str:
        """Converte texto para slug"""
        return text.lower().replace(" ", "-")

    @staticmethod
    def hash_md5(text: str) -> str:
        """Gera hash MD5"""
        return hashlib.md5(text.encode()).hexdigest()

class DataValidator{index}:
    """Validador de dados"""

    def validate_email(self, email: str) -> bool:
        """Valida email"""
        return "@" in email and "." in email

    def validate_required_fields(self, data: Dict, required: List[str]) -> bool:
        """Valida campos obrigatórios"""
        return all(field in data for field in required)
'''
        (path / f"library{index}" / "__init__.py").write_text(lib_code)

    def _create_cli_tool(self, path: Path, index: int):
        """Cria ferramenta CLI"""
        (path / "cli").mkdir()

        # CLI commands
        cli_code = f'''"""
CLI Tool {index}
"""
import argparse
import sys
from typing import Optional

class CLITool{index}:
    """Ferramenta de linha de comando"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=f"Ferramenta CLI {index}",
            prog=f"tool{index}"
        )
        self._setup_commands()

    def _setup_commands(self):
        """Configura comandos"""
        subparsers = self.parser.add_subparsers(dest='command')

        # Comando process
        process_parser = subparsers.add_parser('process')
        process_parser.add_argument('--input', required=True)
        process_parser.add_argument('--output', required=False)
        process_parser.add_argument('--verbose', action='store_true')

        # Comando validate
        validate_parser = subparsers.add_parser('validate')
        validate_parser.add_argument('file', help='Arquivo para validar')

    def run(self, args: Optional[list] = None):
        """Executa CLI"""
        parsed = self.parser.parse_args(args)

        if parsed.command == 'process':
            self._handle_process(parsed)
        elif parsed.command == 'validate':
            self._handle_validate(parsed)
        else:
            self.parser.print_help()

    def _handle_process(self, args):
        """Lida com comando process"""
        print(f"Processando {{args.input}}")
        if args.verbose:
            print("Modo verboso ativado")

    def _handle_validate(self, args):
        """Lida com comando validate"""
        print(f"Validando arquivo: {{args.file}}")

def main():
    """Ponto de entrada"""
    tool = CLITool{index}()
    tool.run()

if __name__ == "__main__":
    main()
'''
        (path / "cli" / "main.py").write_text(cli_code)
        (path / f"tool{index}.py").write_text(f'from cli.main import main; main()')

    def run_validation(self) -> Dict[str, Any]:
        """Executa validação completa nos golden repositories"""
        print("\n" + "="*80)
        print("🚀 SPECTROMETER V7 - GOLDEN REPOSITORY VALIDATION")
        print("="*80)

        self.results['start_time'] = datetime.now()

        # Cria repositórios de teste
        repos = self.create_test_repositories()
        self.results['total_repos'] = len(repos)

        print(f"\n🔍 Iniciando análise de {len(repos)} repositórios...")
        print(f"📊 Baseline esperado: {self.golden_repos_baseline['total_elements']} elementos")
        print("-" * 80)

        # Analisa cada repositório
        for i, repo_path in enumerate(repos, 1):
            print(f"\n📁 [{i:2d}/50] Analisando: {repo_path.name}")

            try:
                # Analisa com Spectrometer V7
                result = self.spectrometer.analyze_repository_haiku(repo_path)

                # Extrai métricas
                total_elements = len(result.get('elements', []))
                hadrons_count = {}
                haiku_classifications = 0

                for element in result.get('elements', []):
                    # Conta hadrons
                    hadrons = element.get('hadrons', [])
                    for hadron in hadrons:
                        hadrons_count[hadron] = hadrons_count.get(hadron, 0) + 1

                    # Conta classificações HAIKU
                    if 'enhanced_hadrons' in element:
                        for enhanced in element['enhanced_hadrons']:
                            if enhanced.get('sub_hadrons'):
                                haiku_classifications += 1

                repo_result = {
                    'repo_name': repo_path.name,
                    'total_elements': total_elements,
                    'hadrons_detected': hadrons_count,
                    'haiku_classifications': haiku_classifications,
                    'unique_hadrons': len(hadrons_count),
                    'top_hadrons': sorted(hadrons_count.items(), key=lambda x: x[1], reverse=True)[:5],
                    'processing_time': result.get('processing_time', 0),
                    'success': True
                }

                self.results['repo_results'].append(repo_result)
                self.results['total_elements_detected'] += total_elements

                # Atualiza estatísticas de hadrons
                for hadron, count in hadrons_count.items():
                    self.results['hadron_stats'][hadron] = self.results['hadron_stats'].get(hadron, 0) + count

                # Progresso
                if i % 10 == 0:
                    avg_elements = self.results['total_elements_detected'] / i
                    print(f"  📊 Progresso: {i}/50 repos | Média: {avg_elements:.1f} elementos/repo")

            except Exception as e:
                error_info = {
                    'repo_name': repo_path.name,
                    'error': str(e),
                    'success': False
                }
                self.results['repo_results'].append(error_info)
                self.results['errors'].append(error_info)
                print(f"  ❌ Erro: {e}")

        self.results['end_time'] = datetime.now()

        # Calcula estatísticas HAIKU
        self.results['haiku_stats'] = self.spectrometer.get_haiku_summary()

        # Gera relatório final
        self._generate_final_report()

        return self.results

    def _generate_final_report(self):
        """Gera relatório final da validação"""
        print("\n" + "="*80)
        print("📊 SPECTROMETER V7 - VALIDATION REPORT")
        print("="*80)

        # Estatísticas gerais
        duration = self.results['end_time'] - self.results['start_time']
        success_repos = sum(1 for r in self.results['repo_results'] if r.get('success', False))

        print(f"\n⏱️  DURAÇÃO: {duration.total_seconds():.2f} segundos")
        print(f"📁 REPOSITÓRIOS: {success_repos}/{self.results['total_repos']} analisados com sucesso")
        print(f"❌ ERROS: {len(self.results['errors'])}")

        # Comparação com baseline
        print(f"\n📊 COMPARAÇÃO COM BASELINE:")
        print(f"  • Elementos esperados: {self.golden_repos_baseline['total_elements']}")
        print(f"  • Elementos detectados: {self.results['total_elements_detected']}")

        if self.golden_repos_baseline['total_elements'] > 0:
            accuracy = (self.results['total_elements_detected'] / self.golden_repos_baseline['total_elements']) * 100
            print(f"  • PRECISÃO: {accuracy:.1f}%")

        # Top Hadrons detectados
        print(f"\n🎯 TOP 20 HÁDRONS DETECTADOS:")
        for hadron, count in sorted(self.results['hadron_stats'].items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  • {hadron:20} {count:5} ocorrências")

        # Estatísticas HAIKU
        haiku_stats = self.results['haiku_stats']
        print(f"\n⚛️  ESTATÍSTICAS HAIKU:")
        print(f"  • Total classificado: {haiku_stats.get('total_classified', 0)}")
        print(f"  • Sub-hádrons detectados: {len(haiku_stats.get('subhadrons_detected', set()))}")
        print(f"  • Profundidade máxima: {max(haiku_stats.get('hierarchy_depth', {}).values() or [0])}")
        print(f"  • Confiança média: {haiku_stats.get('average_confidence', 0)*100:.1f}%")

        # Repositórios com melhor classificação
        print(f"\n🏆 TOP 10 REPOSITÓRIOS (MAIOR CLASSIFICAÇÃO HAIKU):")
        sorted_repos = sorted(
            [r for r in self.results['repo_results'] if r.get('success')],
            key=lambda x: x.get('haiku_classifications', 0),
            reverse=True
        )[:10]

        for i, repo in enumerate(sorted_repos, 1):
            print(f"  {i:2d}. {repo['repo_name']:25} - {repo['haiku_classifications']:3} classificações")

        # Salva relatório detalhado
        report_path = Path("/tmp/spectrometer_v7_golden_report.json")
        with open(report_path, 'w') as f:
            # Converte objetos Path para string para JSON
            serializable_results = {}
            for key, value in self.results.items():
                if key == 'start_time' or key == 'end_time':
                    serializable_results[key] = value.isoformat() if value else None
                elif key == 'haiku_stats':
                    serializable_results[key] = value.copy()
                    if 'subhadrons_detected' in serializable_results[key]:
                        serializable_results[key]['subhadrons_detected'] = list(
                            serializable_results[key]['subhadrons_detected']
                        )
                else:
                    serializable_results[key] = value

            json.dump(serializable_results, f, indent=2)

        print(f"\n💾 RELATÓRIO COMPLETO SALVO EM: {report_path}")

        # Score final
        success_rate = (success_repos / self.results['total_repos']) * 100
        haiku_coverage = (haiku_stats.get('total_classified', 0) / max(self.results['total_elements_detected'], 1)) * 100

        final_score = (success_rate * 0.4) + (haiku_coverage * 0.3) + (accuracy * 0.3)

        print(f"\n🏆 SCORE FINAL SPECTROMETER V7: {final_score:.1f}/100")
        print(f"  • Taxa de Sucesso: {success_rate:.1f}% (peso 40%)")
        print(f"  • Cobertura HAIKU: {haiku_coverage:.1f}% (peso 30%)")
        print(f"  • Precisão vs Baseline: {accuracy:.1f}% (peso 30%)")

        print("="*80)

# Executa validação
if __name__ == "__main__":
    validator = GoldenValidatorV7()
    results = validator.run_validation()
