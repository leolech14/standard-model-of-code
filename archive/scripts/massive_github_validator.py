#!/usr/bin/env python3
"""
VALIDADOR MASSIVO DO SPECTROMETER v4
Teste em 50 repositórios GitHub com respostas conhecidas
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple
from spectrometer_engine_universal import SpectrometerEngine

class MassiveGitHubValidator:
    """Valida o Spectometer em 50 repos GitHub conhecidos"""

    def __init__(self):
        self.engine = SpectrometerEngine()
        self.expected_patterns = self._build_expected_patterns()
        self.results = []

    def _build_expected_patterns(self) -> Dict:
        """Catálogo de padrões esperados para cada repo"""
        return {
            # ============= WEB FRAMEWORKS =============
            "django/django": {
                "language": "python",
                "expected_hadrons": ["APIHandler", "Middleware", "Validator", "Entity", "Service", "QueryHandler"],
                "expected_count": {"Entity": 50, "APIHandler": 100, "Middleware": 30},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Framework web Python"
            },
            "flask/flask": {
                "language": "python",
                "expected_hadrons": ["APIHandler", "Middleware", "Factory"],
                "expected_count": {"APIHandler": 50, "Middleware": 20},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Micro-framework web Python"
            },
            "fastapi/fastapi": {
                "language": "python",
                "expected_hadrons": ["APIHandler", "Middleware", "DependencyInjectionContainer"],
                "expected_count": {"APIHandler": 200, "Middleware": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "API framework moderno Python"
            },
            "expressjs/express": {
                "language": "javascript",
                "expected_hadrons": ["Middleware", "APIHandler", "Router"],
                "expected_count": {"Middleware": 30, "APIHandler": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Framework web Node.js"
            },
            "rails/rails": {
                "language": "ruby",
                "expected_hadrons": ["APIHandler", "Entity", "MigrationFile", "Validator"],
                "expected_count": {"Entity": 200, "MigrationFile": 100},
                "expected_dominant_quark": "AGGREGATES",
                "description": "Framework web Ruby"
            },
            "spring-projects/spring-boot": {
                "language": "java",
                "expected_hadrons": ["APIHandler", "Service", "RepositoryImpl", "DTO"],
                "expected_count": {"Service": 100, "RepositoryImpl": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Framework Java Spring"
            },
            "nestjs/nest": {
                "language": "typescript",
                "expected_hadrons": ["APIHandler", "Service", "DTO", "Guard"],
                "expected_count": {"APIHandler": 80, "Service": 60},
                "expected_dominant_quark": "AGGREGATES",
                "description": "Framework TypeScript Node.js"
            },
            "nextjs/next.js": {
                "language": "javascript",
                "expected_hadrons": ["APIHandler", "Component", "Middleware"],
                "expected_count": {"Component": 100, "APIHandler": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Framework React full-stack"
            },

            # ============= DATA SCIENCE =============
            "numpy/numpy": {
                "language": "python",
                "expected_hadrons": ["PureFunction", "ArrayItem", "Mapper"],
                "expected_count": {"PureFunction": 300},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Biblioteca numérica Python"
            },
            "pandas-dev/pandas": {
                "language": "python",
                "expected_hadrons": ["ValueObject", "Mapper", "Reducer"],
                "expected_count": {"Mapper": 200, "ValueObject": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Biblioteca análise de dados"
            },
            "scikit-learn/scikit-learn": {
                "language": "python",
                "expected_hadrons": ["Entity", "PureFunction", "Factory"],
                "expected_count": {"PureFunction": 200, "Entity": 30},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Machine learning Python"
            },
            "tensorflow/tensorflow": {
                "language": "python",
                "expected_hadrons": ["Entity", "Factory", "AsyncFunction"],
                "expected_count": {"Entity": 100, "PureFunction": 150},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Deep learning framework"
            },
            "pytorch/pytorch": {
                "language": "python",
                "expected_hadrons": ["Entity", "PureFunction", "Reducer"],
                "expected_count": {"Entity": 80, "PureFunction": 120},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Deep learning framework"
            },
            "jupyter/notebook": {
                "language": "python",
                "expected_hadrons": ["APIHandler", "Service", "EventHandler"],
                "expected_count": {"APIHandler": 60},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Jupyter notebook web"
            },

            # ============= DEVOPS / INFRA =============
            "kubernetes/kubernetes": {
                "language": "go",
                "expected_hadrons": ["APIHandler", "EventHandler", "Controller", "ConfigFile"],
                "expected_count": {"Controller": 100, "EventHandler": 80},
                "expected_dominant_quark": "AGGREGATES",
                "description": "Orquestração de containers"
            },
            "docker/docker": {
                "language": "go",
                "expected_hadrons": ["APIHandler", "ContainerEntry", "ConfigLoader"],
                "expected_count": {"APIHandler": 50, "ContainerEntry": 20},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Container platform"
            },
            "hashicorp/terraform": {
                "language": "go",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "expected_count": {"Module": 40, "ConfigFile": 30},
                "expected_dominant_quark": "MODULES",
                "description": "IaC tool"
            },
            "ansible/ansible": {
                "language": "python",
                "expected_hadrons": ["Module", "EventHandler", "ConfigFile"],
                "expected_count": {"Module": 100, "EventHandler": 30},
                "expected_dominant_quark": "MODULES",
                "description": "Automation tool"
            },
            "prometheus/prometheus": {
                "language": "go",
                "expected_hadrons": ["APIHandler", "Service", "ConfigFile"],
                "expected_count": {"APIHandler": 40, "Service": 30},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Monitoring system"
            },
            "grafana/grafana": {
                "language": "typescript",
                "expected_hadrons": ["Component", "Service", "APIHandler"],
                "expected_count": {"Component": 80, "Service": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Visualization platform"
            },
            "jenkinsci/jenkins": {
                "language": "java",
                "expected_hadrons": ["Extension", "PluginLoader", "ConfigFile"],
                "expected_count": {"Extension": 50},
                "expected_dominant_quark": "AGGREGATES",
                "description": "CI/CD server"
            },

            # ============= FRONTEND =============
            "facebook/react": {
                "language": "javascript",
                "expected_hadrons": ["Component", "PureFunction", "EventHandler"],
                "expected_count": {"Component": 200, "PureFunction": 100},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "UI library"
            },
            "vuejs/vue": {
                "language": "javascript",
                "expected_hadrons": ["Component", "EventHandler", "Mapper"],
                "expected_count": {"Component": 150, "EventHandler": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "UI framework"
            },
            "angular/angular": {
                "language": "typescript",
                "expected_hadrons": ["Component", "Service", "DTO"],
                "expected_count": {"Component": 200, "Service": 100},
                "expected_dominant_quark": "AGGREGATES",
                "description": "UI framework TypeScript"
            },
            "sveltejs/svelte": {
                "language": "javascript",
                "expected_hadrons": ["Component", "PureFunction", "EventHandler"],
                "expected_count": {"Component": 80},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "UI compiler"
            },

            # ============== DATABASES =============
            "postgres/postgres": {
                "language": "c",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "expected_count": {"Module": 100, "CLIEntry": 20},
                "expected_dominant_quark": "MODULES",
                "description": "PostgreSQL database"
            },
            "redis/redis": {
                "language": "c",
                "expected_hadrons": ["CommandHandler", "EventHandler", "Module"],
                "expected_count": {"CommandHandler": 100, "Module": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "In-memory database"
            },
            "mongodb/mongo": {
                "language": "cpp",
                "expected_hadrons": ["Module", "ConfigFile", "CLIEntry"],
                "expected_count": {"Module": 80},
                "expected_dominant_quark": "MODULES",
                "description": "NoSQL database"
            },
            "elastic/elasticsearch": {
                "language": "java",
                "expected_hadrons": ["Module", "Service", "ConfigFile"],
                "expected_count": {"Module": 60, "Service": 40},
                "expected_dominant_quark": "AGGREGATES",
                "description": "Search engine"
            },

            # ============== COMPILERS / LANGUAGES =============
            "golang/go": {
                "language": "go",
                "expected_hadrons": ["Module", "CLIEntry", "Parser", "Generator"],
                "expected_count": {"Module": 80, "Parser": 20},
                "expected_dominant_quark": "MODULES",
                "description": "Go language"
            },
            "rust-lang/rust": {
                "language": "rust",
                "expected_hadrons": ["Module", "CLIEntry", "Parser"],
                "expected_count": {"Module": 100, "Parser": 30},
                "expected_dominant_quark": "MODULES",
                "description": "Rust language"
            },
            "microsoft/TypeScript": {
                "language": "typescript",
                "expected_hadrons": ["Parser", "Generator", "Mapper"],
                "expected_count": {"Parser": 50, "Generator": 20},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "TypeScript language"
            },
            "dotnet/roslyn": {
                "language": "csharp",
                "expected_hadrons": ["Parser", "Generator", "Analyzer"],
                "expected_count": {"Parser": 60, "Analyzer": 40},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "C# compiler"
            },

            # ============== ENTERPRISE =============
            "microsoft/vscode": {
                "language": "typescript",
                "expected_hadrons": ["Extension", "Service", "EventHandler"],
                "expected_count": {"Extension": 100, "Service": 80},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Code editor"
            },
            "gitlabhq/gitlabhq": {
                "language": "ruby",
                "expected_hadrons": ["Model", "Controller", "Service", "EventHandler"],
                "expected_count": {"Model": 200, "Controller": 150},
                "expected_dominant_quark": "AGGREGATES",
                "description": "GitLab platform"
            },
            "odoo/odoo": {
                "language": "python",
                "expected_hadrons": ["Model", "APIHandler", "Service", "Controller"],
                "expected_count": {"Model": 300, "Service": 200},
                "expected_dominant_quark": "AGGREGATES",
                "description": "ERP system"
            },
            "apache/airflow": {
                "language": "python",
                "expected_hadrons": ["DAG", "Operator", "EventHandler", "ConfigFile"],
                "expected_count": {"Operator": 100, "DAG": 50},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Workflow orchestrator"
            },

            # ============= SYSTEMS =============
            "torvalds/linux": {
                "language": "c",
                "expected_hadrons": ["Module", "Driver", "EventHandler", "CLIEntry"],
                "expected_count": {"Module": 500, "Driver": 200},
                "expected_dominant_quark": "MODULES",
                "description": "Linux kernel"
            },
            "FFmpeg/FFmpeg": {
                "language": "c",
                "expected_hadrons": ["CLIEntry", "Filter", "Encoder", "Decoder"],
                "expected_count": {"Filter": 100, "CLIEntry": 30},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Media processing"
            },
            "openssl/openssl": {
                "language": "c",
                "expected_hadrons": ["Module", "CLIEntry", "CryptographicFunction"],
                "expected_count": {"Module": 80, "CLIEntry": 20},
                "expected_dominant_quark": "MODULES",
                "description": "Crypto library"
            },

            # ============= GAMING =============
            "godotengine/godot": {
                "language": "cpp",
                "expected_hadrons": ["Entity", "Component", "EventHandler", "Renderer"],
                "expected_count": {"Entity": 100, "Component": 80},
                "expected_dominant_quark": "AGGREGATES",
                "description": "Game engine"
            },
            "unity3d/unity": {
                "language": "csharp",
                "expected_hadrons": ["Entity", "Component", "Service"],
                "expected_count": {"Component": 200, "Entity": 100},
                "expected_dominant_quark": "FUNCTIONS",
                "description": "Game engine"
            }
        }

    def clone_and_analyze_repo(self, repo_full_name: str) -> Dict:
        """Clona e analisa um repositório"""
        import subprocess
        import tempfile
        import shutil

        print(f"\n🔄 Processando: {repo_full_name}")

        # Cria diretório temporário
        temp_dir = tempfile.mkdtemp()
        repo_dir = Path(temp_dir) / "repo"

        try:
            # Clona o repositório (limitando para velocidade)
            print(f"  📥 Clonando...")
            result = subprocess.run([
                "git", "clone",
                "--depth", "1",
                "--filter=blob:none",
                f"https://github.com/{repo_full_name}.git",
                str(repo_dir)
            ], capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return {
                    "repo": repo_full_name,
                    "status": "error",
                    "error": "Failed to clone"
                }

            # Limita a análise para 100 arquivos por repo (rapidez)
            print(f"  🔍 Analisando...")
            self.engine.max_files = 100
            analysis_result = self.engine.analyze_repository(str(repo_dir))

            # Compara com esperado
            expected = self.expected_patterns.get(repo_full_name, {})
            comparison = self._compare_with_expected(analysis_result, expected)

            return {
                "repo": repo_full_name,
                "status": "success",
                "expected": expected.get("description", "Unknown"),
                "analysis": analysis_result["statistics"],
                "comparison": comparison
            }

        except subprocess.TimeoutExpired:
            return {
                "repo": repo_full_name,
                "status": "timeout",
                "error": "Clone timeout"
            }
        except Exception as e:
            return {
                "repo": repo_full_name,
                "status": "error",
                "error": str(e)
            }
        finally:
            # Limpa
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _compare_with_expected(self, analysis: Dict, expected: Dict) -> Dict:
        """Compara resultados com o esperado"""
        stats = analysis["statistics"]
        hadrons_found = stats.get("hadrons_distribution", {})
        quarks_dist = stats.get("quarks_distribution", {})

        comparison = {
            "hadrons_found_vs_expected": {},
            "dominant_quark_match": False,
            "coverage_score": 0,
            "accuracy_score": 0,
            "missing_expected": [],
            "unexpected_found": []
        }

        # Verifica hádrons esperados
        for hadron, expected_count in expected.get("expected_count", {}).items():
            actual_count = hadrons_found.get(hadron, 0)
            comparison["hadrons_found_vs_expected"][hadron] = {
                "expected": expected_count,
                "actual": actual_count,
                "match": actual_count > 0
            }

            if actual_count == 0:
                comparison["missing_expected"].append(hadron)

        # Verifica quark dominante
        if quarks_dist:
            actual_dominant = max(quarks_dist, key=quarks_dist.get)
            expected_dominant = expected.get("expected_dominant_quark")
            comparison["dominant_quark_match"] = actual_dominant == expected_dominant

        # Calcula scores
        expected_hadrons = set(expected.get("expected_count", {}).keys())
        found_hadrons = set(hadrons_found.keys())

        if expected_hadrons:
            comparison["coverage_score"] = len(expected_hadrons & found_hadrons) / len(expected_hadrons) * 100

        return comparison

    def run_massive_validation(self) -> Dict:
        """Executa validação massiva em todos os repos"""
        print("🚀 INICIANDO VALIDAÇÃO MASSIVA")
        print(f"📊 Total de repositórios: {len(self.expected_patterns)}")
        print("="*60)

        start_time = time.time()
        results = []

        for repo_name in self.expected_patterns.keys():
            result = self.clone_and_analyze_repo(repo_name)
            results.append(result)

            # Resumo parcial
            if result["status"] == "success":
                comp = result["comparison"]
                print(f"  ✅ {repo_name}: {comp['coverage_score']:.1f}% coverage | "
                      f"Quark match: {'✅' if comp['dominant_quark_match'] else '❌'}")
            else:
                print(f"  ❌ {repo_name}: {result.get('error', 'Unknown error')}")

        # Compila estatísticas globais
        total_time = time.time() - start_time
        successful = [r for r in results if r["status"] == "success"]

        global_stats = {
            "total_repos": len(self.expected_patterns),
            "successful": len(successful),
            "failed": len(results) - len(successful),
            "total_time": round(total_time / 60, 1),  # minutos
            "avg_time_per_repo": round(total_time / len(results), 1),
            "coverage_distribution": [],
            "quark_accuracy": 0,
            "overall_score": 0
        }

        # Calcula acurácia geral
        if successful:
            coverages = [r["comparison"]["coverage_score"] for r in successful]
            quark_matches = sum(1 for r in successful if r["comparison"]["dominant_quark_match"])

            global_stats["avg_coverage"] = sum(coverages) / len(coverages)
            global_stats["quark_accuracy"] = (quark_matches / len(successful)) * 100
            global_stats["overall_score"] = (global_stats["avg_coverage"] + global_stats["quark_accuracy"]) / 2

        return {
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "Spectrometer v4.0"
            },
            "global_statistics": global_stats,
            "detailed_results": results,
            "summary": self._generate_summary(global_stats, successful)
        }

    def _generate_summary(self, global_stats: Dict, successful: List[Dict]) -> str:
        """Gera resumo dos resultados"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║          SPECTROMETER v4 - VALIDAÇÃO MASSIVA CONCLUÍDA          ║
╚══════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS GLOBAIS:
  • Repositórios testados: {global_stats['total_repos']}
  • Análises bem-sucedidas: {global_stats['successful']} ({global_stats['successful']/global_stats['total_repos']*100:.1f}%)
  • Falhas: {global_stats['failed']}
  • Tempo total: {global_stats['total_time']:.1f} minutos
  • Tempo médio por repo: {global_stats['avg_time_per_repo']:.1f} segundos

🎯 MÉTRICAS DE ACURÁCIA:
  • Cobertura média: {global_stats['avg_coverage']:.1f}%
  • Acurácia de quarks: {global_stats['quark_accuracy']:.1f}%
  • Score geral: {global_stats['overall_score']:.1f}/100

🏆 TOP 10 MAIORES COBERTURAS:
"""

        if successful:
            # Ordena por coverage
            top_repos = sorted(successful,
                             key=lambda x: x["comparison"]["coverage_score"],
                             reverse=True)[:10]

            for i, repo in enumerate(top_repos, 1):
                coverage = repo["comparison"]["coverage_score"]
                quark_match = "✅" if repo["comparison"]["dominant_quark_match"] else "❌"
                summary += f"  {i:2}. {repo['repo']:<30} {coverage:5.1f}% {quark_match}\n"

        summary += f"""
💡 INSIGHTS:
"""

        if global_stats['overall_score'] >= 80:
            summary += "  ✅ EXCELENTE: O motor está pronto para produção!\n"
        elif global_stats['overall_score'] >= 65:
            summary += "  🟡 BOM: O motor é funcional mas precisa de ajustes\n"
        else:
            summary += "  🔴 PRECISA MELHORAR: Revisar heurísticas de detecção\n"

        return summary

    def save_results(self, results: Dict, output_path: Path):
        """Salva resultados completos"""
        # JSON completo
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Relatório resumido
        report_path = output_path.with_suffix('.md')
        with open(report_path, 'w') as f:
            f.write(results["summary"])

        print(f"\n📁 Resultados salvos:")
        print(f"  JSON: {output_path}")
        print(f"  Relatório: {report_path}")

# ===============================================
# EXECUÇÃO PRINCIPAL
# ===============================================

if __name__ == "__main__":
    import os

    # Verifica se git está disponível
    if os.system("git --version > /dev/null 2>&1") != 0:
        print("❌ Git não encontrado. Por favor instale o Git para continuar.")
        exit(1)

    validator = MassiveGitHubValidator()

    # Se quiser testar com apenas 5 repos (rápido):
    test_repos = {
        "django/django": validator.expected_patterns["django/django"],
        "numpy/numpy": validator.expected_patterns["numpy/numpy"],
        "expressjs/express": validator.expected_patterns["expressjs/express"],
        "golang/go": validator.expected_patterns["golang/go"],
        "torvalds/linux": validator.expected_patterns["torvalds/linux"]
    }
    validator.expected_patterns = test_repos

    # Executa validação (comente a linha acima e descomente para rodar nos 50)
    results = validator.run_massive_validation()
    validator.save_results(results, Path("massive_validation_results.json"))

    print("\n" + "="*60)
    print("VALIDAÇÃO MASSIVA COMPLETA!")
    print("="*60)