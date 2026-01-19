#!/usr/bin/env python3
"""
SPECTROMETER V11.1 - EXTERNAL VALIDATION EDITION
Structured JSON Output with Third-Party Repo Validation
Validates against real-world open-source repositories
"""

import json
import requests
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import sys
import hashlib

# Import our robust parser
from spectrometer_v11_robust import SpectrometerV11

class ExternalValidator:
    """Validates Spectrometer against external repositories"""

    def __init__(self):
        self.results = {
            "validation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "spectrometer_version": "V11.1",
                "validation_type": "external_third_party",
                "standards": ["MIT", "Apache-2.0", "BSD", "GPL-3.0"]
            },
            "repositories_tested": [],
            "cross_validation_metrics": {},
            "structured_output": {},
            "validation_summary": {}
        }

        # Known valid repositories with different architectures
        self.validation_repos = [
            {
                "name": "django",
                "url": "https://github.com/django/django/archive/refs/tags/4.2.7.zip",
                "architecture": "MVT (Model-View-Template)",
                "language": "Python",
                "size": "Large (>500k LOC)",
                "expected_patterns": ["ORM", "Views", "Models", "Forms"],
                "license": "BSD-3-Clause"
            },
            {
                "name": "flask",
                "url": "https://github.com/pallets/flask/archive/refs/tags/2.3.2.zip",
                "architecture": "Microframework",
                "language": "Python",
                "size": "Medium (~50k LOC)",
                "expected_patterns": ["Request Handlers", "Context", "Routing"],
                "license": "BSD-3-Clause"
            },
            {
                "name": "fastapi",
                "url": "https://github.com/tiangolo/fastapi/archive/refs/tags/0.104.1.zip",
                "architecture": "Modern API Framework",
                "language": "Python",
                "size": "Medium (~100k LOC)",
                "expected_patterns": ["APIRouter", "Pydantic", "DependencyInjection"],
                "license": "MIT"
            },
            {
                "name": "requests",
                "url": "https://github.com/psf/requests/archive/refs/tags/v2.31.0.zip",
                "architecture": "HTTP Client Library",
                "language": "Python",
                "size": "Small (~10k LOC)",
                "expected_patterns": ["Session", "Adapter", "Response"],
                "license": "Apache-2.0"
            }
        ]

    def download_and_extract_repo(self, repo_info: Dict[str, Any]) -> Optional[Path]:
        """Download and extract a repository for validation"""
        print(f"\n📥 Downloading {repo_info['name']}...")

        try:
            # Download
            response = requests.get(repo_info['url'], stream=True)
            response.raise_for_status()

            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="spectrometer_val_"))
            zip_path = temp_dir / f"{repo_info['name']}.zip"

            # Save zip
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find extracted directory
            extracted_dir = None
            for item in temp_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    extracted_dir = item
                    break

            if extracted_dir:
                print(f"✅ Extracted to: {extracted_dir}")
                return extracted_dir
            else:
                print(f"❌ Could not find extracted directory")
                return None

        except Exception as e:
            print(f"❌ Failed to download/extract {repo_info['name']}: {e}")
            return None

    def validate_repository(self, repo_info: Dict[str, Any], repo_path: Path) -> Dict[str, Any]:
        """Validate a single repository with Spectrometer"""
        print(f"\n🔬 Validating {repo_info['name']}...")

        # Initialize Spectrometer
        spectrometer = SpectrometerV11({
            'external_validation': True,
            'repo_metadata': repo_info
        })

        # Analyze repository
        analysis_results = spectrometer.analyze_repository(repo_path)

        # Structure the validation results
        validation_result = {
            "repository": {
                "name": repo_info['name'],
                "url": repo_info['url'],
                "architecture": repo_info['architecture'],
                "language": repo_info['language'],
                "size": repo_info['size'],
                "license": repo_info['license'],
                "extracted_path": str(repo_path)
            },
            "spectrometer_analysis": analysis_results,
            "cross_validation": {
                "expected_patterns_found": [],
                "unexpected_patterns": [],
                "pattern_coverage": 0.0,
                "architecture_compliance": 0.0
            },
            "metrics": {
                "files_analyzed": len(analysis_results.get('file_results', [])),
                "detection_rate": 0.0,
                "confidence_distribution": {},
                "subhadron_distribution": {}
            },
            "validation_status": "pending"
        }

        # Calculate cross-validation metrics
        self._calculate_cross_validation(validation_result, repo_info)

        # Add to results
        self.results["repositories_tested"].append(validation_result)

        return validation_result

    def _calculate_cross_validation(self, validation_result: Dict, repo_info: Dict):
        """Calculate cross-validation metrics"""
        expected_patterns = repo_info.get('expected_patterns', [])
        found_patterns = set()

        # Analyze detection results
        all_detections = []
        for file_result in validation_result['spectrometer_analysis'].get('file_results', []):
            if file_result.get('success'):
                for node in file_result.get('nodes', []):
                    # Determine pattern type
                    pattern = self._classify_node_pattern(node)
                    if pattern:
                        found_patterns.add(pattern)
                        all_detections.append({
                            'file': file_result['file_path'],
                            'pattern': pattern,
                            'confidence': 0.8,  # Placeholder
                            'line': node.get('line', 0)
                        })

        # Calculate metrics
        expected_found = [p for p in expected_patterns if p in found_patterns]
        validation_result['cross_validation']['expected_patterns_found'] = expected_found
        validation_result['cross_validation']['pattern_coverage'] = len(expected_found) / len(expected_patterns) if expected_patterns else 0
        validation_result['cross_validation']['architecture_compliance'] = min(1.0, len(expected_found) / max(1, len(expected_patterns) * 0.7))

        # Store structured output
        validation_result['metrics']['detection_rate'] = len(all_detections) / max(1, validation_result['metrics']['files_analyzed'])
        validation_result['structured_output'] = {
            "pattern_matches": all_detections,
            "file_level_analysis": self._generate_file_level_analysis(validation_result['spectrometer_analysis'].get('file_results', []))
        }

        # Determine validation status
        if validation_result['cross_validation']['architecture_compliance'] >= 0.7:
            validation_result['validation_status'] = "passed"
        elif validation_result['cross_validation']['architecture_compliance'] >= 0.5:
            validation_result['validation_status'] = "partial"
        else:
            validation_result['validation_status'] = "failed"

    def _classify_node_pattern(self, node: Dict) -> Optional[str]:
        """Classify a node into an architecture pattern"""
        node_name = node.get('name', '').lower()
        node_type = node.get('type', '')

        # Pattern classification rules
        if 'model' in node_name or node_type == 'class':
            if any(keyword in node_name for keyword in ['model', 'entity', 'table']):
                return "Model/Entity"

        if 'view' in node_name or 'controller' in node_name:
            return "View/Controller"

        if 'form' in node_name:
            return "Form"

        if 'request' in node_name or 'response' in node_name:
            return "HTTP Handler"

        if 'router' in node_name or 'route' in node_name:
            return "Routing"

        if 'session' in node_name:
            return "Session"

        if 'adapter' in node_name:
            return "Adapter"

        if 'response' in node_name:
            return "Response"

        return None

    def _generate_file_level_analysis(self, file_results: List[Dict]) -> Dict:
        """Generate file-level structured analysis"""
        file_analysis = {}

        for file_result in file_results:
            if file_result.get('success'):
                file_path = file_result['file_path']
                file_analysis[file_path] = {
                    "parser_used": file_result.get('parser_used', 'unknown'),
                    "node_count": len(file_result.get('nodes', [])),
                    "nodes": file_result.get('nodes', []),
                    "complexity_metrics": {
                        "depth": self._calculate_file_complexity(file_result.get('nodes', [])),
                        "coupling": self._estimate_coupling(file_result.get('nodes', [])),
                        "cohesion": self._estimate_cohesion(file_result.get('nodes', []))
                    }
                }

        return file_analysis

    def _calculate_file_complexity(self, nodes: List[Dict]) -> int:
        """Calculate complexity score for a file"""
        complexity = 0
        for node in nodes:
            if node.get('type') == 'class':
                complexity += len(node.get('methods', [])) * 2
            elif node.get('type') in ['function', 'async_function']:
                complexity += len(node.get('args', []))
        return complexity

    def _estimate_coupling(self, nodes: List[Dict]) -> int:
        """Estimate coupling level"""
        imports = 0
        for node in nodes:
            if 'import' in node.get('name', '').lower():
                imports += 1
        return min(10, imports)  # Cap at 10

    def _estimate_cohesion(self, nodes: List[Dict]) -> float:
        """Estimate cohesion level (0-1)"""
        if not nodes:
            return 0.0

        # Simple heuristic: more related nodes = higher cohesion
        class_count = sum(1 for n in nodes if n.get('type') == 'class')
        func_count = sum(1 for n in nodes if n.get('type') in ['function', 'async_function'])

        if class_count > 0:
            return min(1.0, class_count / (class_count + func_count))
        return 0.5

    def run_validation_suite(self) -> Dict[str, Any]:
        """Run full validation suite on all repositories"""
        print("🔬 SPECTROMETER V11.1 - EXTERNAL VALIDATION SUITE")
        print("="*80)

        validation_summary = {
            "total_repos": len(self.validation_repos),
            "passed": 0,
            "failed": 0,
            "partial": 0,
            "overall_score": 0.0
        }

        # Test each repository
        for repo_info in self.validation_repos[:2]:  # Test first 2 for demo
            repo_path = self.download_and_extract_repo(repo_info)

            if repo_path:
                validation_result = self.validate_repository(repo_info, repo_path)

                # Update summary
                status = validation_result['validation_status']
                validation_summary[status] += 1

                print(f"\n📊 {repo_info['name']} Validation: {status.upper()}")
                print(f"   Pattern Coverage: {validation_result['cross_validation']['pattern_coverage']:.1%}")
                print(f"   Architecture Compliance: {validation_result['cross_validation']['architecture_compliance']:.1%}")
            else:
                validation_summary['failed'] += 1
                print(f"\n❌ {repo_info['name']} Validation: FAILED (download error)")

        # Calculate overall score
        total = validation_summary['passed'] + validation_summary['partial']
        if total > 0:
            validation_summary['overall_score'] = (
                (validation_summary['passed'] * 1.0 + validation_summary['partial'] * 0.5) /
                len(self.validation_repos)
            )

        self.results['validation_summary'] = validation_summary

        # Generate final structured output
        self._generate_final_structured_output()

        return self.results

    def _generate_final_structured_output(self):
        """Generate final structured JSON output"""

        # Calculate aggregate metrics
        all_files = 0
        all_detections = 0
        all_patterns = set()

        for repo in self.results['repositories_tested']:
            metrics = repo.get('metrics', {})
            all_files += metrics.get('files_analyzed', 0)
            all_detections += len(repo.get('structured_output', {}).get('pattern_matches', []))

            # Collect all patterns
            for match in repo.get('structured_output', {}).get('pattern_matches', []):
                all_patterns.add(match['pattern'])

        # Structure the final output
        self.results['structured_output'] = {
            "validation_timestamp": datetime.now().isoformat(),
            "spectrometer_performance": {
                "total_files_analyzed": all_files,
                "total_detections": all_detections,
                "detection_rate": all_detections / max(1, all_files),
                "patterns_discovered": list(all_patterns),
                "unique_pattern_count": len(all_patterns)
            },
            "cross_validation_metrics": {
                "average_pattern_coverage": sum(
                    r['cross_validation']['pattern_coverage']
                    for r in self.results['repositories_tested']
                ) / max(1, len(self.results['repositories_tested'])),
                "average_architecture_compliance": sum(
                    r['cross_validation']['architecture_compliance']
                    for r in self.results['repositories_tested']
                ) / max(1, len(self.results['repositories_tested'])),
                "validation_success_rate": self.results['validation_summary']['overall_score']
            },
            "repository_breakdown": [
                {
                    "name": repo['repository']['name'],
                    "architecture": repo['repository']['architecture'],
                    "status": repo['validation_status'],
                    "metrics": repo['metrics'],
                    "cross_validation": repo['cross_validation']
                }
                for repo in self.results['repositories_tested']
            ]
        }

    def save_validation_results(self, output_path: Optional[str] = None) -> str:
        """Save validation results to structured JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/spectrometer_v11_validation_{timestamp}.json"

        # Create structured output
        structured_output = {
            "$schema": "https://github.com/leonardolech/spectrometer/validation-schema-v1.json",
            "metadata": self.results["validation_metadata"],
            "summary": self.results["validation_summary"],
            "performance": self.results["structured_output"]["spectrometer_performance"],
            "cross_validation": self.results["structured_output"]["cross_validation_metrics"],
            "repositories": self.results["structured_output"]["repository_breakdown"],
            "detailed_results": self.results["repositories_tested"]
        }

        # Save with proper formatting
        with open(output_path, 'w') as f:
            json.dump(structured_output, f, indent=2, ensure_ascii=False)

        # Generate SHA256 for integrity
        sha256_hash = hashlib.sha256()
        with open(output_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        print(f"\n💾 Structured JSON saved to: {output_path}")
        print(f"🔐 SHA256: {sha256_hash.hexdigest()}")

        return output_path

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("   SPECTROMETER V11.1 - EXTERNAL VALIDATION")
    print("   Structured JSON Output with Third-Party Validation")
    print("="*80)

    # Run validation
    validator = ExternalValidator()
    results = validator.run_validation_suite()

    # Save results
    output_path = validator.save_validation_results()

    # Print summary
    print("\n" + "="*80)
    print("               VALIDATION SUMMARY")
    print("="*80)
    summary = results['validation_summary']
    print(f"Total Repositories: {summary['total_repos']}")
    print(f"Passed: {summary['passed']}")
    print(f"Partial: {summary['partial']}")
    print(f"Failed: {summary['failed']}")
    print(f"Overall Score: {summary['overall_score']:.1%}")

    # Performance metrics
    perf = results['structured_output']['spectrometer_performance']
    print(f"\nPerformance Metrics:")
    print(f"  Files Analyzed: {perf['total_files_analyzed']:,}")
    print(f"  Detections: {perf['total_detections']:,}")
    print(f"  Detection Rate: {perf['detection_rate']:.2%}")
    print(f"  Unique Patterns: {perf['unique_pattern_count']}")

    print("="*80)
    print(f"✅ Structured JSON output ready at: {output_path}")

if __name__ == "__main__":
    main()