#!/usr/bin/env python3
"""
Dataset diversificado para validação dos 96 hádrons
50+ repositórios representativos do ecossistema de software
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple

class ValidationDataset:
    """Dataset curado para validação do Spectrometer v4"""

    def __init__(self):
        self.repositories = self._build_repository_catalog()

    def _build_repository_catalog(self) -> List[Dict]:
        """Constrói catálogo de repositórios para teste"""
        repos = []

        # ========================
        # CATEGORIA: Web Frameworks
        # ========================
        repos.extend([
            {
                "name": "Django",
                "url": "https://github.com/django/django",
                "language": "python",
                "category": "web_framework",
                "size": "large",
                "expected_hadrons": ["APIHandler", "Middleware", "Validator", "Entity", "Service", "QueryHandler"],
                "complexity": "high"
            },
            {
                "name": "Flask",
                "url": "https://github.com/pallets/flask",
                "language": "python",
                "category": "web_framework",
                "size": "medium",
                "expected_hadrons": ["APIHandler", "Middleware", "Factory"],
                "complexity": "medium"
            },
            {
                "name": "FastAPI",
                "url": "https://github.com/fastapi/fastapi",
                "language": "python",
                "category": "web_framework",
                "size": "medium",
                "expected_hadrons": ["APIHandler", "Middleware", "DependencyInjectionContainer"],
                "complexity": "high"
            },
            {
                "name": "Express.js",
                "url": "https://github.com/expressjs/express",
                "language": "javascript",
                "category": "web_framework",
                "size": "medium",
                "expected_hadrons": ["Middleware", "APIHandler", "Router"],
                "complexity": "medium"
            },
            {
                "name": "Rails",
                "url": "https://github.com/rails/rails",
                "language": "ruby",
                "category": "web_framework",
                "size": "large",
                "expected_hadrons": ["APIHandler", "Entity", "MigrationFile", "Validator"],
                "complexity": "high"
            },
            {
                "name": "Spring Boot",
                "url": "https://github.com/spring-projects/spring-boot",
                "language": "java",
                "category": "web_framework",
                "size": "large",
                "expected_hadrons": ["APIHandler", "Service", "RepositoryImpl", "DTO"],
                "complexity": "high"
            }
        ])

        # ========================
        # CATEGORIA: Data Science / ML
        # ========================
        repos.extend([
            {
                "name": "NumPy",
                "url": "https://github.com/numpy/numpy",
                "language": "python",
                "category": "data_science",
                "size": "large",
                "expected_hadrons": ["PureFunction", "ArrayItem", "Mapper"],
                "complexity": "high"
            },
            {
                "name": "Pandas",
                "url": "https://github.com/pandas-dev/pandas",
                "language": "python",
                "category": "data_science",
                "size": "large",
                "expected_hadrons": ["ValueObject", "Mapper", "Reducer"],
                "complexity": "high"
            },
            {
                "name": "Scikit-learn",
                "url": "https://github.com/scikit-learn/scikit-learn",
                "language": "python",
                "category": "machine_learning",
                "size": "large",
                "expected_hadrons": ["Entity", "PureFunction", "Factory"],
                "complexity": "high"
            },
            {
                "name": "TensorFlow",
                "url": "https://github.com/tensorflow/tensorflow",
                "language": "python",
                "size": "large",
                "category": "machine_learning",
                "expected_hadrons": ["Entity", "Factory", "AsyncFunction"],
                "complexity": "very_high"
            },
            {
                "name": "PyTorch",
                "url": "https://github.com/pytorch/pytorch",
                "language": "python",
                "category": "machine_learning",
                "size": "large",
                "expected_hadrons": ["Entity", "PureFunction", "Reducer"],
                "complexity": "very_high"
            }
        ])

        # ========================
        # CATEGORIA: DevOps / Infrastructure
        # ========================
        repos.extend([
            {
                "name": "Kubernetes",
                "url": "https://github.com/kubernetes/kubernetes",
                "language": "go",
                "category": "infrastructure",
                "size": "very_large",
                "expected_hadrons": ["APIHandler", "EventHandler", "Controller", "ConfigFile"],
                "complexity": "very_high"
            },
            {
                "name": "Docker",
                "url": "https://github.com/docker/docker",
                "language": "go",
                "category": "infrastructure",
                "size": "very_large",
                "expected_hadrons": ["APIHandler", "ContainerEntry", "ConfigLoader"],
                "complexity": "very_high"
            },
            {
                "name": "Ansible",
                "url": "https://github.com/ansible/ansible",
                "language": "python",
                "category": "infrastructure",
                "size": "large",
                "expected_hadrons": ["Module", "EventHandler", "ConfigFile"],
                "complexity": "high"
            },
            {
                "name": "Terraform",
                "url": "https://github.com/hashicorp/terraform",
                "language": "go",
                "category": "infrastructure",
                "size": "large",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "complexity": "high"
            },
            {
                "name": "Jenkins",
                "url": "https://github.com/jenkinsci/jenkins",
                "language": "java",
                "category": "infrastructure",
                "size": "large",
                "expected_hadrons": ["Extension", "PluginLoader", "ConfigFile"],
                "complexity": "high"
            }
        ])

        # ========================
        # CATEGORIA: Frontend (JS/TS)
        # ========================
        repos.extend([
            {
                "name": "React",
                "url": "https://github.com/facebook/react",
                "language": "javascript",
                "category": "frontend",
                "size": "large",
                "expected_hadrons": ["Component", "PureFunction", "EventHandler"],
                "complexity": "high"
            },
            {
                "name": "Vue.js",
                "url": "https://github.com/vuejs/vue",
                "language": "javascript",
                "category": "frontend",
                "size": "large",
                "expected_hadrons": ["Component", "EventHandler", "Mapper"],
                "complexity": "high"
            },
            {
                "name": "Angular",
                "url": "https://github.com/angular/angular",
                "language": "typescript",
                "category": "frontend",
                "size": "large",
                "expected_hadrons": ["Component", "Service", "DTO"],
                "complexity": "high"
            },
            {
                "name": "Next.js",
                "url": "https://github.com/vercel/next.js",
                "language": "typescript",
                "category": "frontend",
                "size": "large",
                "expected_hadrons": ["APIHandler", "Component", "Middleware"],
                "complexity": "high"
            },
            {
                "name": "Svelte",
                "url": "https://github.com/sveltejs/svelte",
                "language": "javascript",
                "category": "frontend",
                "size": "medium",
                "expected_hadrons": ["Component", "PureFunction", "EventHandler"],
                "complexity": "medium"
            }
        ])

        # ========================
        # CATEGORIA: Databases
        # ========================
        repos.extend([
            {
                "name": "PostgreSQL",
                "url": "https://github.com/postgres/postgres",
                "language": "c",
                "category": "database",
                "size": "very_large",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "complexity": "very_high"
            },
            {
                "name": "Redis",
                "url": "https://github.com/redis/redis",
                "language": "c",
                "category": "database",
                "size": "large",
                "expected_hadrons": ["CommandHandler", "EventHandler", "Module"],
                "complexity": "high"
            },
            {
                "name": "MongoDB",
                "url": "https://github.com/mongodb/mongo",
                "language": "cpp",
                "category": "database",
                "size": "very_large",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "complexity": "very_high"
            },
            {
                "name": "Elasticsearch",
                "url": "https://github.com/elastic/elasticsearch",
                "language": "java",
                "category": "database",
                "size": "very_large",
                "expected_hadrons": ["Module", "Service", "ConfigFile"],
                "complexity": "very_high"
            }
        ])

        # ========================
        # CATEGORIA: Enterprise / Business
        # ========================
        repos.extend([
            {
                "name": "Odoo",
                "url": "https://github.com/odoo/odoo",
                "language": "python",
                "category": "enterprise",
                "size": "very_large",
                "expected_hadrons": ["Model", "APIHandler", "Service", "Controller"],
                "complexity": "very_high"
            },
            {
                "name": "Apache Airflow",
                "url": "https://github.com/apache/airflow",
                "language": "python",
                "category": "enterprise",
                "size": "large",
                "expected_hadrons": ["DAG", "Operator", "EventHandler", "ConfigFile"],
                "complexity": "high"
            },
            {
                "name": "GitLab",
                "url": "https://github.com/gitlabhq/gitlabhq",
                "language": "ruby",
                "category": "enterprise",
                "size": "very_large",
                "expected_hadrons": ["Model", "Controller", "Service", "EventHandler"],
                "complexity": "very_high"
            },
            {
                "name": "Metabase",
                "url": "https://github.com/metabase/metabase",
                "language": "clojure",
                "category": "enterprise",
                "size": "large",
                "expected_hadrons": ["Entity", "QueryHandler", "APIHandler", "Mapper"],
                "complexity": "high"
            }
        ])

        # ========================
        # CATEGORIA: Compilers / Tooling
        # ========================
        repos.extend([
            {
                "name": "Rust",
                "url": "https://github.com/rust-lang/rust",
                "language": "rust",
                "category": "compiler",
                "size": "very_large",
                "expected_hadrons": ["Module", "CLIEntry", "Parser"],
                "complexity": "very_high"
            },
            {
                "name": "Go",
                "url": "https://github.com/golang/go",
                "language": "go",
                "category": "compiler",
                "size": "very_large",
                "expected_hadrons": ["Module", "CLIEntry", "Parser", "Generator"],
                "complexity": "very_high"
            },
            {
                "name": "TypeScript",
                "url": "https://github.com/microsoft/TypeScript",
                "language": "typescript",
                "category": "compiler",
                "size": "very_large",
                "expected_hadrons": ["Parser", "Generator", "Mapper"],
                "complexity": "very_high"
            },
            {
                "name": "Babel",
                "url": "https://github.com/babel/babel",
                "language": "javascript",
                "category": "compiler",
                "size": "large",
                "expected_hadrons": ["Parser", "Generator", "Transformer"],
                "complexity": "high"
            }
        ])

        # ========================
        # CATEGORIA: Gaming / Graphics
        # ========================
        repos.extend([
            {
                "name": "Godot",
                "url": "https://github.com/godotengine/godot",
                "language": "cpp",
                "category": "gaming",
                "size": "very_large",
                "expected_hadrons": ["Entity", "Component", "EventHandler", "Renderer"],
                "complexity": "very_high"
            },
            {
                "name": "Three.js",
                "url": "https://github.com/mrdoob/three.js",
                "language": "javascript",
                "category": "gaming",
                "size": "large",
                "expected_hadrons": ["Entity", "PureFunction", "Renderer"],
                "complexity": "high"
            }
        ])

        # ========================
        # CATEGORIA: Legacy / Systems
        # ========================
        repos.extend([
            {
                "name": "Linux Kernel",
                "url": "https://github.com/torvalds/linux",
                "language": "c",
                "category": "system",
                "size": "very_large",
                "expected_hadrons": ["Module", "Driver", "EventHandler", "CLIEntry"],
                "complexity": "very_high"
            },
            {
                "name": "FFmpeg",
                "url": "https://github.com/FFmpeg/FFmpeg",
                "language": "c",
                "category": "system",
                "size": "very_large",
                "expected_hadrons": ["CLIEntry", "Filter", "Encoder", "Decoder"],
                "complexity": "very_high"
            },
            {
                "name": "OpenSSL",
                "url": "https://github.com/openssl/openssl",
                "language": "c",
                "category": "system",
                "size": "large",
                "expected_hadrons": ["Module", "CLIEntry", "CryptographicFunction"],
                "complexity": "high"
            }
        ])

        return repos

    def get_repos_by_language(self, language: str) -> List[Dict]:
        """Filtra repositórios por linguagem"""
        return [r for r in self.repositories if r["language"] == language]

    def get_repos_by_category(self, category: str) -> List[Dict]:
        """Filtra repositórios por categoria"""
        return [r for r in self.repositories if r["category"] == category]

    def get_sample_by_complexity(self, complexity: str, count: int = 5) -> List[Dict]:
        """Amostra repositórios por complexidade"""
        filtered = [r for r in self.repositories if r["complexity"] == complexity]
        return filtered[:count]

    def get_balanced_sample(self, count_per_category: int = 2) -> List[Dict]:
        """Amostra balanceada entre categorias"""
        categories = set(r["category"] for r in self.repositories)
        sample = []

        for category in categories:
            repos = self.get_repos_by_category(category)
            sample.extend(repos[:count_per_category])

        return sample

    def save_dataset(self, output_path: Path):
        """Salva dataset em JSON"""
        dataset = {
            "metadata": {
                "total_repositories": len(self.repositories),
                "languages": list(set(r["language"] for r in self.repositories)),
                "categories": list(set(r["category"] for r in self.repositories)),
                "size_distribution": {
                    size: len([r for r in self.repositories if r["size"] == size])
                    for size in set(r["size"] for r in self.repositories)
                }
            },
            "repositories": self.repositories
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)

    def generate_test_plan(self) -> Dict:
        """Gera plano de teste sistemático"""
        plan = {
            "phases": [
                {
                    "name": "Phase 1 - Web Frameworks",
                    "description": "Testar frameworks web mais populares",
                    "repositories": self.get_repos_by_category("web_framework")[:5],
                    "success_criteria": {
                        "coverage": "> 80%",
                        "confidence": "> 0.7"
                    }
                },
                {
                    "name": "Phase 2 - Data Science",
                    "description": "Validar em repositórios de ML/Data Science",
                    "repositories": self.get_repos_by_category("data_science")[:3],
                    "success_criteria": {
                        "coverage": "> 75%",
                        "confidence": "> 0.6"
                    }
                },
                {
                    "name": "Phase 3 - Infrastructure",
                    "description": "Testar ferramentas de DevOps",
                    "repositories": self.get_repos_by_category("infrastructure")[:3],
                    "success_criteria": {
                        "coverage": "> 70%",
                        "confidence": "> 0.6"
                    }
                },
                {
                    "name": "Phase 4 - Frontend",
                    "description": "Analisar frameworks JavaScript/TypeScript",
                    "repositories": self.get_repos_by_category("frontend")[:3],
                    "success_criteria": {
                        "coverage": "> 75%",
                        "confidence": "> 0.7"
                    }
                },
                {
                    "name": "Phase 5 - Enterprise",
                    "description": "Validar em sistemas corporativos",
                    "repositories": self.get_repos_by_category("enterprise")[:3],
                    "success_criteria": {
                        "coverage": "> 70%",
                        "confidence": "> 0.6"
                    }
                },
                {
                    "name": "Phase 6 - Random Sample",
                    "description": "Amostra aleatória do restante",
                    "repositories": self.repositories[20:30],
                    "success_criteria": {
                        "coverage": "> 60%",
                        "confidence": "> 0.5"
                    }
                }
            ],
            "overall_success_criteria": {
                "total_coverage": "> 75%",
                "avg_confidence": "> 0.65",
                "max_missing_hadrons": 20
            }
        }

        return plan

# ========================
# EXECUÇÃO DO DATASET
# ========================

if __name__ == "__main__":
    dataset = ValidationDataset()

    # Salva dataset completo
    dataset_path = Path("validation_dataset.json")
    dataset.save_dataset(dataset_path)
    print(f"Dataset salvo em: {dataset_path}")

    # Gera plano de teste
    test_plan = dataset.generate_test_plan()
    plan_path = Path("validation_test_plan.json")
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(test_plan, f, indent=2)
    print(f"Plano de teste salvo em: {plan_path}")

    # Print resumo
    print("\n" + "="*60)
    print("VALIDATION DATASET SUMMARY")
    print("="*60)
    print(f"Total de repositórios: {len(dataset.repositories)}")
    print(f"Linguagens: {len(set(r['language'] for r in dataset.repositories))}")
    print(f"Categorias: {len(set(r['category'] for r in dataset.repositories))}")
    print("\nDistribuição por categoria:")
    for category in set(r['category'] for r in dataset.repositories):
        count = len(dataset.get_repos_by_category(category))
        print(f"  - {category}: {count} repositórios")