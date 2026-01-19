#!/usr/bin/env python3
"""
SPECTROMETER V12 - COMPREHENSIVE STATISTICS & PARTICLES TABLE
Complete Output with All Numbers and Mapped Particles
Full Statistics + Individual Particle Details + Universal Mapping
"""

import json
import time
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict, Counter
import re

class ComprehensiveStatisticsGenerator:
    """Generates complete statistics and particles table"""

    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "execution_metadata": {
                "timestamp": None,
                "duration_seconds": None,
                "spectrometer_version": "V12.0",
                "total_files_processed": 0,
                "total_lines_of_code": 0,
                "total_characters": 0,
                "average_file_size": 0
            },
            "comprehensive_statistics": {
                "particle_detection": {
                    "total_particles_detected": 0,
                    "unique_particle_types": 0,
                    "average_confidence": 0.0,
                    "confidence_distribution": {},
                    "particles_per_file": {},
                    "detection_rate": 0.0
                },
                "pattern_recognition": {
                    "universal_patterns_detected": 0,
                    "language_specific_patterns": 0,
                    "touchpoints_found": {},
                    "cross_language_equivalents": {},
                    "pattern_distribution": {},
                    "touchpoint_coverage": {}
                },
                "file_analysis": {
                    "files_with_particles": 0,
                    "files_without_particles": 0,
                    "file_coverage_percentage": 0.0,
                    "largest_file_size": 0,
                    "smallest_file_size": 0,
                    "median_file_size": 0
                },
                "performance": {
                    "files_per_second": 0.0,
                    "lines_per_second": 0.0,
                    "characters_per_second": 0.0,
                    "error_rate": 0.0,
                    "success_rate": 100.0
                }
            },
            "particles_table": [],
            "summary_statistics": {}
        }

        # Load previous results for comprehensive analysis
        self.load_previous_results()

    def load_previous_results(self):
        """Load data from previous Spectrometer runs"""
        result_files = [
            "/tmp/haiku_384_tuned_1764823831.json",
            "/tmp/spectrometer_v11_report_1764825009.json",
            "/tmp/spectrometer_v11_validation_20251204_021013.json"
        ]

        for result_file in result_files:
            if Path(result_file).exists():
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)

                        # Extract particle data
                        if 'deteccoes' in data:
                            self._process_particles(data['deteccoes'])

                        # Update file counts
                        if 'file_results' in data:
                            self.results['comprehensive_statistics']['file_analysis']['total_files_processed'] += len(data['file_results'])

                except Exception as e:
                    print(f"Warning: Could not process {result_file}: {e}")

    def _process_particles(self, detections: List[Dict]):
        """Process particle detections from previous runs"""
        for detection in detections:
            self.results['comprehensive_statistics']['particle_detection']['total_particles_detected'] += 1

            # Count unique particle types
            particle_type = detection.get('id', 'Unknown')
            self.results['particles_table'].append({
                'particle_id': particle_type,
                'particle_type': detection.get('hadron_type', 'Unknown'),
                'responsibility': detection.get('responsibility', 'Unknown'),
                'purity': detection.get('purity', 'Unknown'),
                'boundary': detection.get('boundary', 'Unknown'),
                'lifecycle': detection.get('lifecycle', 'Unknown'),
                'file_path': detection.get('arquivo', 'Unknown'),
                'line': detection.get('linha', 0),
                'confidence': detection.get('confianca', 0.0),
                'timestamp': detection.get('timestamp', None),
                'evidence': detection.get('evidencia', '')
            })

    def analyze_current_repository(self, repo_path: Path):
        """Analyze the current repository for real-time statistics"""
        print(f"\n🔬 Analyzing repository: {repo_path}")
        print("Collecting comprehensive statistics...")

        # Find all Python files
        python_files = list(repo_path.rglob("*.py"))
        self.results['execution_metadata']['total_files_processed'] = len(python_files)

        # Process each file
        files_with_particles = 0
        total_lines = 0
        total_chars = 0
        file_sizes = []

        for file_path in python_files:
            try:
                # File statistics
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = len(content.split('\n'))
                chars = len(content)

                total_lines += lines
                total_chars += chars
                file_sizes.append(chars)

                # Detect patterns in file
                particles = self._detect_particles_in_file(file_path, content)
                if particles:
                    files_with_particles += 1
                    self.results['particles_table'].extend(particles)

            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")

        # Calculate final statistics
        self._calculate_final_statistics(
            python_files, files_with_particles, total_lines, total_chars, file_sizes
        )

    def _detect_particles_in_file(self, file_path: Path, content: str) -> List[Dict]:
        """Detect particles (sub-hádrons) in a file"""
        particles = []
        lines = content.split('\n')

        # Pattern definitions for detection
        patterns = {
            'Entity': [
                r'class\s+\w*[Ee]ntity',
                r'class\s+\w*[Mm]odel',
                r'@entity',
                r'dataclass.*class',
                r'class.*Table',
                r'struct.*Entity'
            ],
            'Repository': [
                r'class\s+\w*[Rr]epository',
                r'interface\s+\w*[Rr]epository',
                r'extends.*Repository',
                r'implements.*Repository',
                r'def\s+(save|find|delete|update)'
            ],
            'Service': [
                r'class\s+\w*[Ss]ervice',
                r'class\s+\w*[Aa]pplication',
                r'@Service',
                r'class\s+\w*[Uu]secase',
                r'def\s+(execute|handle|process)'
            ],
            'Controller': [
                r'class\s+\w*[Cc]ontroller',
                r'@RestController',
                r'@Controller',
                r'@app\.route',
                r'@GetMapping',
                r'router\.get'
            ],
            'ValueObject': [
                r'@dataclass\(frozen=True\)',
                r'class\s+\w*[Vv]alueObject',
                r'dataclass.*class.*ValueObject',
                r'frozenset',
                r'@value',
                r'final class'
            ],
            'Factory': [
                r'class\s+\w*[Ff]actory',
                r'def\s+(create|build|make)',
                r'Factory\s*\(',
                r'Builder\s*\(',
                r'Creator\s*\('
            ],
            'Specification': [
                r'class\s+\w*[Ss]pecification',
                r'interface\s+\w*[Ss]pecification',
                r'def\s+(is_satisfied|validate)',
                r'Predicate\s*(',
                r'Rule\s*\('
            ]
        }

        # Detect patterns
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, line_lower):
                        particles.append({
                            'particle_id': f"{pattern_type}_{line_num}_{len(particles)+1}",
                            'particle_type': pattern_type,
                            'responsibility': self._infer_responsibility(pattern_type),
                            'purity': self._infer_purity(pattern_type, line),
                            'boundary': self._infer_boundary(pattern_type),
                            'lifecycle': self._infer_lifecycle(pattern_type),
                            'file_path': str(file_path),
                            'line': line_num,
                            'confidence': 0.7,  # Base confidence for regex detection
                            'timestamp': time.time(),
                            'evidence': line.strip()[:100],
                            'pattern_matched': pattern
                        })

        return particles

    def _infer_responsibility(self, pattern_type: str) -> str:
        """ infer responsibility from pattern type"""
        responsibility_map = {
            'Entity': 'Write',
            'Repository': 'Both',
            'Service': 'Write',
            'Controller': 'Both',
            'ValueObject': 'Read',
            'Factory': 'Create',
            'Specification': 'Read'
        }
        return responsibility_map.get(pattern_type, 'Unknown')

    def _infer_purity(self, pattern_type: str, line: str) -> str:
        """infer purity from pattern and context"""
        if pattern_type in ['ValueObject', 'Specification']:
            return 'Pure'
        elif pattern_type in ['Entity', 'Repository']:
            if 'interface' in line.lower() or 'abstract' in line.lower():
                return 'Pure'
            else:
                return 'Impure'
        elif pattern_type in ['Service', 'Controller']:
            return 'Impure'
        elif pattern_type == 'Factory':
            return 'Pure'
        return 'Unknown'

    def _infer_boundary(self, pattern_type: str) -> str:
        """infer boundary from pattern type"""
        if pattern_type in ['Entity', 'ValueObject', 'Repository']:
            return 'Explicit'
        elif pattern_type in ['Service', 'Controller']:
            return 'Explicit'
        return 'Implicit'

    def _infer_lifecycle(self, pattern_type: str) -> str:
        """infer lifecycle from pattern type"""
        if pattern_type in ['ValueObject', 'Specification']:
            return 'Transient'
        elif pattern_type in ['Entity']:
            return 'Transient'
        elif pattern_type in ['Repository', 'Service', 'Controller']:
            return 'Singleton'
        elif pattern_type == 'Factory':
            return 'Transient'
        return 'Unknown'

    def _calculate_final_statistics(self, files: List[Path], files_with_particles: int,
                                     total_lines: int, total_chars: int, file_sizes: List[int]):
        """Calculate final comprehensive statistics"""

        # Update execution metadata
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        self.results['execution_metadata'].update({
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'total_lines_of_code': total_lines,
            'total_characters': total_chars,
            'average_file_size': sum(file_sizes) / len(file_sizes) if file_sizes else 0
        })

        # Update particle detection statistics
        self._calculate_particle_statistics()

        # Update file analysis statistics
        self._calculate_file_statistics(files, files_with_particles, file_sizes)

        # Update performance statistics
        self.results['comprehensive_statistics']['performance'].update({
            'files_per_second': len(files) / duration if duration > 0 else 0,
            'lines_per_second': total_lines / duration if duration > 0 else 0,
            'characters_per_second': total_chars / duration if duration > 0 else 0
        })

        # Calculate summary statistics
        self._calculate_summary_statistics()

    def _calculate_particle_statistics(self):
        """Calculate particle detection statistics"""
        particles = self.results['particles_table']

        if particles:
            confidences = [p['confidence'] for p in particles]
            particle_types = [p['particle_type'] for p in particles]
            files_with_particles = len(set(p['file_path'] for p in particles))

            files_total = self.results['execution_metadata']['total_files_processed']

            # Confidence distribution
            confidence_ranges = [(0, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.0)]
            for min_conf, max_conf in confidence_ranges:
                count = sum(1 for c in confidences if min_conf <= c < max_conf)
                self.results['comprehensive_statistics']['particle_detection']['confidence_distribution'][
                    f"{min_conf*100}-{max_conf*100}%"
                ] = count

            # Unique particle types
            unique_types = set(particle_types)
            self.results['comprehensive_statistics']['particle_detection']['unique_particle_types'] = len(unique_types)

            # Average confidence
            self.results['comprehensive_statistics']['particle_detection']['average_confidence'] = statistics.mean(confidences) if confidences else 0

            # Particles per file
            particles_per_file = {}
            for particle in particles:
                file_path = particle['file_path']
                particles_per_file[file_path] = particles_per_file.get(file_path, 0) + 1

            self.results['comprehensive_statistics']['particle_detection']['particles_per_file'] = particles_per_file

            # Detection rate
            self.results['comprehensive_statistics']['particle_detection']['detection_rate'] = (
                files_with_particles / files_total * 100 if files_total > 0 else 0
            )

    def _calculate_file_statistics(self, files: List[Path], files_with_particles: int, file_sizes: List[int]):
        """Calculate file analysis statistics"""
        total_files = len(files)

        self.results['comprehensive_statistics']['file_analysis'].update({
            'files_with_particles': files_with_particles,
            'files_without_particles': total_files - files_with_particles,
            'file_coverage_percentage': (files_with_particles / total_files * 100) if total_files > 0 else 0,
            'largest_file_size': max(file_sizes) if file_sizes else 0,
            'smallest_file_size': min(file_sizes) if file_sizes else 0,
            'median_file_size': statistics.median(file_sizes) if file_sizes else 0
        })

    def _calculate_summary_statistics(self):
        """Calculate summary statistics for quick overview"""
        metrics = self.results['comprehensive_statistics']

        # Top statistics
        self.results['summary_statistics'] = {
            'top_5_particle_types': self._get_top_5_particle_types(),
            'top_5_files_by_particles': self._get_top_5_files_by_particles(),
            'key_metrics': {
                'total_particles': metrics['particle_detection']['total_particles_detected'],
                'unique_types': metrics['particle_detection']['unique_particle_types'],
                'average_confidence': f"{metrics['particle_detection']['average_confidence']:.2%}",
                'file_coverage': f"{metrics['file_analysis']['file_coverage_percentage']:.1f}%"
            },
            'performance_summary': {
                'files_per_sec': f"{metrics['performance']['files_per_second']:.1f}",
                'lines_per_sec': f"{metrics['performance']['lines_per_sec']:.0f}",
                'duration_sec': f"{self.results['execution_metadata']['duration_seconds']:.1f}"
            }
        }

    def _get_top_5_particle_types(self) -> List[Tuple[str, int, float]]:
        """Get top 5 particle types by count"""
        particle_counts = Counter(p['particle_type'] for p in self.results['particles_table'])
        total_particles = len(self.results['particles_table'])

        top_5 = particle_counts.most_common(5)
        return [(ptype, count, count/total_particles*100) for ptype, count in top_5]

    def _get_top_5_files_by_particles(self) -> List[Tuple[str, int]]:
        """Get top 5 files by particle count"""
        file_counts = Counter(p['file_path'] for p in self.results['particles_table'])

        return [(Path(fp).name, count) for fp, count in file_counts.most_common(5)]

    def generate_comprehensive_output(self):
        """Generate comprehensive statistics and tables output"""

        print("\n" + "="*100)
        print("                   COMPREHENSIVE STATISTICS AND PARTICLES TABLE")
        print("                          Spectrometer V12.0 - Complete Analysis")
        print("="*100)
        print(f"Generated: {self.results['execution_metadata']['timestamp']}")
        print(f"Duration: {self.results['execution_metadata']['duration_seconds']:.2f} seconds")
        print("="*100)

        # EXECUTION METADATA TABLE
        print("\n📊 EXECUTION METADATA TABLE")
        print("-"*100)
        print(f"{'Metric':<30} | {'Value':<20} | {'Details':<50}")
        print("-"*100)
        print(f"{'Total Files Processed':<30} | {self.results['execution_metadata']['total_files_processed']:<20} | {'All Python files'}")
        print(f"{'Total Lines of Code':<30} | {self.results['execution_metadata']['total_lines_of_commence']:,<20} | {'Lines analyzed'}")
        print(f"{'Total Characters':<30} | {self.results['execution_metadata']['total_characters']:,<20} | {'Characters analyzed'}")
        print(f"{'Average File Size':<30} | {self.results['execution_metadata']['average_file_size']:<20} | {'Characters per file'}")

        # PARTICLE DETECTION STATISTICS TABLE
        print(f"\n🎯 PARTICLE DETECTION STATISTICS TABLE")
        print("-"*100)
        print(f"{'Metric':<30} | {'Value':<20} | {'Details':<50}")
        print("-"*100)
        particle_stats = self.results['comprehensive_statistics']['particle_detection']
        print(f"{'Total Particles Detected':<30} | {particle_stats['total_particles_detected']:<20} | {'All particles across all files'}")
        print(f"{'Unique Particle Types':<30} | {particle_stats['unique_particle_types']:<20} | {'Different pattern types'}")
        print(f"{'Average Confidence':<30} | {particle_stats['average_confidence']:<20} | {'Mean detection confidence'}")
        file_coverage = particle_stats['detection_rate']
        print(f"{'Files with Particles':<30} | {particle_stats['detection_rate']:<20} | {'Percentage of files'}")

        # CONFIDENCE DISTRIBUTION
        print(f"\n📊 CONFIDENCE DISTRIBUTION")
        print("-"*50)
        for range_min, range_max, count in [
            (0, 0.5, particle_stats['confidence_distribution'].get('0-50%', 0)),
            (0.5, 0.7, particle_stats['confidence_distribution'].get('50-70%', 0)),
            (0.7, 0.9, particle_stats['confidence_distribution'].get('70-90%', 0)),
            (0.9, 1.0, particle_stats['confidence_distribution'].get('90-100%', 0))
        ]:
            bar_length = int(count / max(1, max(
                particle_stats['confidence_distribution'].values()
            )) * 30)
            bar = "█" * bar_length
            print(f"{range_min*3:3d}-{range_max*3:3d}%: {bar} {count} particles ({count/particle_stats['total_particles_detected']*100:.1f}%)")

        # FILE ANALYSIS STATISTICS
        print(f"\n📁 FILE ANALYSIS STATISTICS")
        print("-"*100)
        file_stats = self.results['comprehensive_statistics']['file_analysis']
        print(f"{'Files Analyzed':<30} | {file_stats['total_files_processed']:<20} | {'Python files found'}")
        print(f"{'Files with Particles':<30} | {file_stats['files_with_particles']:<20} | {'Files containing patterns'}")
        print(f"{'Files without Particles':<30} | {file_stats['files_without_particles']:<20} | {'Clean/No DDD patterns'}")
        print(f"{'Coverage Percentage':<30} | {file_stats['file_coverage_percentage']:.1f}% | {'Percent analyzed'}")
        print(f"{'Largest File':<30} | {file_stats['largest_file_size']:,<20} | {'Characters'}")
        print(f"{'Smallest File':<30} | {file_stats['smallest_file_size']:<20} | {'Characters'}")
        print(f"{'Median File Size':<30} | {file_stats['median_file_size']:<20} | {'Characters'}")

        # PERFORMANCE STATISTICS
        print(f"\n⚡ PERFORMANCE STATISTICS")
        print("-"*100)
        perf = self.results['comprehensive_statistics']['performance']
        print(f"{'Files/Second':<30} | {perf['files_per_second']:.0f} | {'Processing throughput'}")
        print(f"{'Lines/Second':<30} | {perf['lines_per_second']:.0f} | {'Lines processed'}")
        print(f"{'Characters/Second':<30} | {perf['characters_per_second']:.0f} | {'Chars processed'}")
        print(f"{'Success Rate':<30} | {perf['success_rate']:.1f}% | {'Error-free operations'}")

        # TOP PARTICLE TYPES TABLE
        print(f"\n🏆 TOP 5 PARTICLE TYPES BY FREQUENCY")
        print("-"*100)
        print(f"{'#':<3} | {'Pattern Type':<20} | {'Count':<10} | {'Percentage':<12}")
        print("-"*100)

        for i, (ptype, count, pct) in enumerate(self.results['summary_statistics']['top_5_particle_types'], 1):
            print(f"{i:<3} | {ptype:<20} | {count:<10} | {pct:.1f}%")

        # TOP FILES BY PARTICLES TABLE
        print(f"\n📁 TOP 5 FILES BY PARTICLE COUNT")
        print("-"*100)
        print(f"{'#':<3} | {'File Name':<40} | {'Particles':<10} | {'Location'}")
        print("-"*100)

        for i, (filename, count) in enumerate(self.results['summary_statistics']['top_5_files_by_particles'], 1):
            file_parts = filename.rsplit('/', 1)
            location = file_parts[0] if len(file_parts) > 1 else "root"
            print(f"{i:<3} | {filename:<40} | {count:<10} | {location}")

        # DETAILED PARTICLES TABLE (Top 20)
        print(f"\n🔬 DETAILED PARTICLES TABLE (TOP 20)")
        print("-"*100)
        print(f"{'#':<3} | {'Particle ID':<25} | {'Type':<15} | {'Responsibility':<12} | {'Purity':<8} | {'File':<30} | {'Line':<6} | {'Conf':<7} | {'Evidence':<60}")
        print("-"*100)

        # Sort by confidence descending
        sorted_particles = sorted(
            self.results['particles_table'],
            key=lambda x: (x['confidence'], x['line'], x['file_path']),
            reverse=True
        )

        for i, particle in enumerate(sorted_particles[:20], 1):
            evidence = particle['evidence']
            if len(evidence) > 60:
                evidence = evidence[:57] + "..."

            print(f"{i:<3} | {particle['particle_id']:<25} | {particle['particle_type']:<15} | "
                  f"{particle['responsibility']:<12} | {particle['purity']:<8} | "
                  f"{Path(particle['file_path']).name:<30} | {particle['line']:<6} | "
                  f"{particle['confidence']:.1%} | {evidence}")

        if len(sorted_particles) > 20:
            remaining = len(sorted_particles) - 20
            print(f"... and {remaining} more particles")

        # SUMMARY STATISTICS
        print(f"\n📋 SUMMARY STATISTICS")
        print("-"*100)
        summary = self.results['summary_statistics']

        print(f"\n🎯 Key Metrics:")
        for metric, value in summary['key_metrics'].items():
            print(f"   • {metric}: {value}")

        print(f"\n⚡ Performance:")
        for metric, value in summary['performance_summary'].items():
            print(f"   • {metric}: {value}")

        # Save detailed results to JSON
        self.save_comprehensive_results()

    def save_comprehensive_results(self):
        """Save comprehensive results to JSON file"""
        timestamp = int(datetime.now().timestamp())
        output_path = Path(f"/tmp/comprehensive_stats_and_particles_{timestamp}.json")

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n💾 Comprehensive results saved to: {output_path}")
        print(f"   Total particles: {len(self.results['particles_table'])}")
        print(f"   File size: {output_path.stat().st_size:,} bytes")

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("   COMPREHENSIVE STATISTICS GENERATOR")
    print("   Full Stats + Particles Table + Universal Mapping")
    print("="*80)

    generator = ComprehensiveStatisticsGenerator()

    # Analyze current repository
    current_dir = Path(__file__).parent
    generator.analyze_current_repository(current_dir)

    # Generate output
    generator.generate_comprehensive_output()

    print("\n" + "="*80)
    print("           ANALYSIS COMPLETE")
    print("="*80)
    print("   All particles mapped and statistics generated")
    print("   Ready for universal architecture analysis")
    print("="*80)

if __name__ == "__main__":
    main()