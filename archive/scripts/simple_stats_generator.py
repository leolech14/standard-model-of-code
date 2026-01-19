#!/usr/bin/env python3
"""
📊 SPECTROMETER V12 - COMPREHENSIVE STATISTICS GENERATOR
Working version for immediate results with full tables
============================================
"""

import json
import os
import re
import time
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

class SpectrometerStatsGenerator:
    """Generate comprehensive statistics and particles table"""

    def __init__(self):
        self.results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': 'V12.1',
                'mode': 'comprehensive_statistics'
            },
            'summary_statistics': {},
            'comprehensive_statistics': {},
            'particles_table': [],
            'all_files_analyzed': []
        }

        # Particle definitions from HAIKU-384
        self.particle_types = {
            'Entity': {'responsibility': 9, 'purity': 3, 'boundary': 8, 'lifecycle': 9},
            'Service': {'responsibility': 7, 'purity': 4, 'boundary': 6, 'lifecycle': 5},
            'Repository': {'responsibility': 8, 'purity': 6, 'boundary': 7, 'lifecycle': 7},
            'Controller': {'responsibility': 6, 'purity': 2, 'boundary': 9, 'lifecycle': 4},
            'ValueObject': {'responsibility': 4, 'purity': 9, 'boundary': 5, 'lifecycle': 8},
            'AggregateRoot': {'responsibility': 10, 'purity': 5, 'boundary': 9, 'lifecycle': 10},
            'DomainService': {'responsibility': 8, 'purity': 7, 'boundary': 5, 'lifecycle': 6},
            'ApplicationService': {'responsibility': 7, 'purity': 3, 'boundary': 8, 'lifecycle': 5},
            'UseCase': {'responsibility': 6, 'purity': 5, 'boundary': 7, 'lifecycle': 4},
            'Factory': {'responsibility': 5, 'purity': 6, 'boundary': 4, 'lifecycle': 3},
            'Specification': {'responsibility': 4, 'purity': 8, 'boundary': 3, 'lifecycle': 7},
            'EventHandler': {'responsibility': 6, 'purity': 4, 'boundary': 6, 'lifecycle': 5},
            'Projection': {'responsibility': 5, 'purity': 7, 'boundary': 5, 'lifecycle': 6},
            'ReadModel': {'responsibility': 3, 'purity': 8, 'boundary': 4, 'lifecycle': 7},
            'Command': {'responsibility': 4, 'purity': 9, 'boundary': 3, 'lifecycle': 2},
            'Query': {'responsibility': 3, 'purity': 9, 'boundary': 3, 'lifecycle': 2},
            'Policy': {'responsibility': 5, 'purity': 8, 'boundary': 4, 'lifecycle': 8},
            'Strategy': {'responsibility': 6, 'purity': 7, 'boundary': 5, 'lifecycle': 6},
            'Observer': {'responsibility': 4, 'purity': 5, 'boundary': 6, 'lifecycle': 5},
            'Mediator': {'responsibility': 7, 'purity': 3, 'boundary': 8, 'lifecycle': 4}
        }

    def analyze_current_repository(self, repository_path: str):
        """Analyze current repository for patterns"""
        print(f"🔬 Analyzing repository: {repository_path}")

        # Collect all Python files
        python_files = []
        for root, dirs, files in os.walk(repository_path):
            # Skip virtual environment directories
            if 'spectrometer-env' in root or 'venv' in root or '__pycache__' in root:
                continue
            if '.git' in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)

        print(f"📁 Found {len(python_files)} Python files")

        # Process files and detect patterns
        all_particles = []
        files_with_particles = 0
        total_lines = 0
        total_chars = 0
        file_sizes = []

        start_time = time.time()

        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                lines = content.split('\n')
                line_count = len(lines)
                char_count = len(content)

                total_lines += line_count
                total_chars += char_count
                file_sizes.append(char_count)

                # Detect particles in this file
                file_particles = self._detect_particles_in_file(file_path, content, lines)

                if file_particles:
                    files_with_particles += 1
                    all_particles.extend(file_particles)

                self.results['all_files_analyzed'].append({
                    'file_path': file_path,
                    'lines': line_count,
                    'characters': char_count,
                    'particles_found': len(file_particles),
                    'particle_types': list(set(p['type'] for p in file_particles))
                })

            except Exception as e:
                print(f"⚠️ Error processing {file_path}: {e}")
                continue

        processing_time = time.time() - start_time

        # Calculate comprehensive statistics
        self._calculate_comprehensive_statistics(
            len(python_files), files_with_particles, total_lines,
            total_chars, file_sizes, processing_time, all_particles
        )

        # Calculate summary statistics
        self._calculate_summary_statistics(all_particles, python_files)

        # Build particles table
        self.results['particles_table'] = all_particles

        # Save results
        self._save_results()

        # Print tables
        self._print_all_tables()

    def _detect_particles_in_file(self, file_path: str, content: str, lines: list):
        """Detect architectural patterns in a file"""
        particles = []

        # Simple pattern detection based on keywords and structure
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Class detection
            if re.match(r'^\s*class\s+\w+', line):
                class_name = re.search(r'class\s+(\w+)', line).group(1)

                # Determine particle type based on naming and context
                particle_type = self._classify_particle(class_name, line_stripped, content)

                if particle_type:
                    confidence = self._calculate_confidence(class_name, line_stripped, content)

                    particle = {
                        'particle_id': f"{particle_type}_{len(particles)+1}",
                        'type': particle_type,
                        'name': class_name,
                        'file_path': file_path,
                        'line': i,
                        'confidence': confidence,
                        'responsibility': self.particle_types.get(particle_type, {}).get('responsibility', 5),
                        'purity': self.particle_types.get(particle_type, {}).get('purity', 5),
                        'boundary': self.particle_types.get(particle_type, {}).get('boundary', 5),
                        'lifecycle': self.particle_types.get(particle_type, {}).get('lifecycle', 5),
                        'evidence': line_stripped[:100]
                    }
                    particles.append(particle)

            # Function detection
            elif re.match(r'^\s*def\s+\w+', line):
                func_name = re.search(r'def\s+(\w+)', line).group(1)

                # Classify function
                particle_type = self._classify_function(func_name, line_stripped, content)

                if particle_type:
                    confidence = self._calculate_confidence(func_name, line_stripped, content)

                    particle = {
                        'particle_id': f"{particle_type}_{len(particles)+1}",
                        'type': particle_type,
                        'name': func_name,
                        'file_path': file_path,
                        'line': i,
                        'confidence': confidence,
                        'responsibility': self.particle_types.get(particle_type, {}).get('responsibility', 5),
                        'purity': self.particle_types.get(particle_type, {}).get('purity', 5),
                        'boundary': self.particle_types.get(particle_type, {}).get('boundary', 5),
                        'lifecycle': self.particle_types.get(particle_type, {}).get('lifecycle', 5),
                        'evidence': line_stripped[:100]
                    }
                    particles.append(particle)

        return particles

    def _classify_particle(self, name: str, line: str, content: str):
        """Classify particle type based on naming and context"""
        name_lower = name.lower()

        # Check for common DDD patterns
        if any(suffix in name_lower for suffix in ['entity', 'model', 'aggregate']):
            return 'Entity'
        elif any(suffix in name_lower for suffix in ['repository', 'repo']):
            return 'Repository'
        elif any(suffix in name_lower for suffix in ['controller', 'view', 'api']):
            return 'Controller'
        elif any(suffix in name_lower for suffix in ['service', 'handler']):
            return 'Service'
        elif any(suffix in name_lower for suffix in ['value', 'vo', 'val']):
            return 'ValueObject'
        elif any(suffix in name_lower for suffix in ['factory']):
            return 'Factory'
        elif any(suffix in name_lower for suffix in ['spec', 'specification']):
            return 'Specification'
        elif 'command' in name_lower:
            return 'Command'
        elif 'query' in name_lower or 'get' in name_lower:
            return 'Query'

        # Check content for patterns
        if 'class' in line and any(keyword in content for keyword in ['@dataclass', 'frozen=True', '__hash__']):
            return 'ValueObject'
        elif 'class' in line and any(keyword in content for keyword in ['@abstractmethod', 'ABC', 'interface']):
            return 'Service'

        return None

    def _classify_function(self, name: str, line: str, content: str):
        """Classify function type"""
        name_lower = name.lower()

        if name.startswith('handle_') or name.endswith('_handler'):
            return 'EventHandler'
        elif name.startswith('on_') or name.startswith('when_'):
            return 'Observer'
        elif name.startswith('create_') or name.startswith('make_'):
            return 'Factory'
        elif 'validate' in name_lower or 'check' in name_lower:
            return 'Specification'
        elif name.startswith('execute_') or name.startswith('run_'):
            return 'UseCase'
        elif 'apply' in name_lower:
            return 'Policy'
        elif name.startswith('process_'):
            return 'DomainService'

        return None

    def _calculate_confidence(self, name: str, line: str, content: str):
        """Calculate confidence score for particle detection"""
        confidence = 50  # Base confidence

        # Name-based confidence
        name_lower = name.lower()
        if any(pattern in name_lower for pattern in ['entity', 'repository', 'service', 'controller']):
            confidence += 20

        # Context-based confidence
        if any(keyword in content for keyword in ['@dataclass', 'frozen=True', 'immutable']):
            confidence += 15
        if any(keyword in content for keyword in ['abstractmethod', 'interface', 'protocol']):
            confidence += 15
        if any(keyword in content for keyword in ['database', 'db', 'sql', 'persistence']):
            confidence += 10

        return min(confidence, 100)

    def _calculate_comprehensive_statistics(self, total_files, files_with_particles,
                                          total_lines, total_chars, file_sizes, processing_time, all_particles):
        """Calculate comprehensive statistics"""
        # File analysis
        file_coverage = (files_with_particles / total_files * 100) if total_files > 0 else 0

        self.results['comprehensive_statistics'] = {
            'file_analysis': {
                'total_files_processed': total_files,
                'files_with_particles': files_with_particles,
                'files_without_particles': total_files - files_with_particles,
                'file_coverage_percentage': file_coverage,
                'largest_file_size': max(file_sizes) if file_sizes else 0,
                'smallest_file_size': min(file_sizes) if file_sizes else 0,
                'median_file_size': sorted(file_sizes)[len(file_sizes)//2] if file_sizes else 0
            },
            'particle_analysis': {
                'total_particles_detected': len(all_particles),
                'unique_particle_types': len(set(p['type'] for p in all_particles)),
                'average_particles_per_file': len(all_particles) / total_files if total_files > 0 else 0,
                'max_particles_in_file': max([len([p for p in all_particles if p['file_path'] == f]) for f in set(p['file_path'] for p in all_particles)], default=0),
                'average_confidence': sum(p['confidence'] for p in all_particles) / len(all_particles) if all_particles else 0
            },
            'performance': {
                'total_processing_time_seconds': processing_time,
                'files_per_second': total_files / processing_time if processing_time > 0 else 0,
                'lines_per_second': total_lines / processing_time if processing_time > 0 else 0,
                'characters_per_second': total_chars / processing_time if processing_time > 0 else 0,
                'success_rate': (files_with_particles / total_files * 100) if total_files > 0 else 0
            }
        }

    def _calculate_summary_statistics(self, all_particles, python_files):
        """Calculate summary statistics"""
        # Particle type distribution
        type_counts = Counter(p['type'] for p in all_particles)
        top_5_types = type_counts.most_common(5)

        # File distribution
        file_counts = Counter(p['file_path'] for p in all_particles)
        top_5_files = file_counts.most_common(5)

        # Confidence distribution
        confidence_ranges = {
            'High (80-100%)': len([p for p in all_particles if p['confidence'] >= 80]),
            'Medium (60-79%)': len([p for p in all_particles if 60 <= p['confidence'] < 80]),
            'Low (40-59%)': len([p for p in all_particles if 40 <= p['confidence'] < 60]),
            'Very Low (0-39%)': len([p for p in all_particles if p['confidence'] < 40])
        }

        self.results['summary_statistics'] = {
            'total_particles_found': len(all_particles),
            'unique_particle_types': len(type_counts),
            'top_5_particle_types': [(t, c, c/len(all_particles)*100) for t, c in top_5_types],
            'top_5_files_by_particles': [(f, c) for f, c in top_5_files],
            'confidence_distribution': confidence_ranges,
            'detection_density': len(all_particles) / len(python_files) if python_files else 0
        }

    def _save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'spectrometer_comprehensive_stats_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {filename}")

    def _print_all_tables(self):
        """Print all comprehensive tables"""
        print("\n" + "="*120)
        print("📊 SPECTROMETER V12 - COMPREHENSIVE STATISTICS AND PARTICLES TABLE")
        print("="*120)

        # EXECUTION METADATA
        print("\n📋 EXECUTION METADATA")
        print("-"*120)
        meta = self.results['metadata']
        print(f"{'Generated At':<30} | {meta['generated_at']:<50} | {'Timestamp'}")
        print(f"{'Generator Version':<30} | {meta['generator_version']:<50} | {'Engine version'}")
        print(f"{'Operating Mode':<30} | {meta['mode']:<50} | {'Analysis type'}")

        # SUMMARY STATISTICS
        print("\n🎯 SUMMARY STATISTICS")
        print("-"*120)
        summary = self.results['summary_statistics']
        print(f"{'Total Particles Found':<30} | {summary['total_particles_found']:<50} | {'All patterns detected'}")
        print(f"{'Unique Particle Types':<30} | {summary['unique_particle_types']:<50} | {'Different pattern types'}")
        print(f"{'Detection Density':<30} | {summary['detection_density']:.1f} | {'Particles per file'}")

        # COMPREHENSIVE STATISTICS
        print("\n📊 COMPREHENSIVE STATISTICS")
        print("-"*120)

        # File Analysis
        print(f"\n📁 FILE ANALYSIS")
        print("-"*120)
        file_stats = self.results['comprehensive_statistics']['file_analysis']
        print(f"{'Files Analyzed':<30} | {file_stats['total_files_processed']:<20} | {'Python files found'}")
        print(f"{'Files with Particles':<30} | {file_stats['files_with_particles']:<20} | {'Files containing patterns'}")
        print(f"{'Files without Particles':<30} | {file_stats['files_without_particles']:<20} | {'Clean/No DDD patterns'}")
        print(f"{'Coverage Percentage':<30} | {file_stats['file_coverage_percentage']:.1f}% | {'Percent analyzed'}")
        print(f"{'Largest File':<30} | {file_stats['largest_file_size']:,} | {'Characters'}")
        print(f"{'Smallest File':<30} | {file_stats['smallest_file_size']:,} | {'Characters'}")
        print(f"{'Median File Size':<30} | {file_stats['median_file_size']:,} | {'Characters'}")

        # PERFORMANCE STATISTICS
        print(f"\n⚡ PERFORMANCE STATISTICS")
        print("-"*120)
        perf = self.results['comprehensive_statistics']['performance']
        print(f"{'Files/Second':<30} | {perf['files_per_second']:.0f} | {'Processing throughput'}")
        print(f"{'Lines/Second':<30} | {perf['lines_per_second']:.0f} | {'Lines processed'}")
        print(f"{'Characters/Second':<30} | {perf['characters_per_second']:.0f} | {'Chars processed'}")
        print(f"{'Success Rate':<30} | {perf['success_rate']:.1f}% | {'Error-free operations'}")

        # PARTICLE ANALYSIS
        print(f"\n🔬 PARTICLE ANALYSIS")
        print("-"*120)
        particle_stats = self.results['comprehensive_statistics']['particle_analysis']
        print(f"{'Total Particles Detected':<30} | {particle_stats['total_particles_detected']:<20} | {'All patterns found'}")
        print(f"{'Unique Particle Types':<30} | {particle_stats['unique_particle_types']:<20} | {'Pattern variety'}")
        print(f"{'Average Particles Per File':<30} | {particle_stats['average_particles_per_file']:.1f} | {'Pattern density'}")
        print(f"{'Max Particles in File':<30} | {particle_stats['max_particles_in_file']:<20} | {'Highest concentration'}")
        print(f"{'Average Confidence':<30} | {particle_stats['average_confidence']:.1f}% | {'Detection confidence'}")

        # CONFIDENCE DISTRIBUTION
        print(f"\n📈 CONFIDENCE DISTRIBUTION")
        print("-"*120)
        conf_dist = self.results['summary_statistics']['confidence_distribution']
        for range_name, count in conf_dist.items():
            percentage = (count / self.results['summary_statistics']['total_particles_found'] * 100) if self.results['summary_statistics']['total_particles_found'] > 0 else 0
            print(f"{range_name:<30} | {count:<20} | {percentage:.1f}%")

        # TOP PARTICLE TYPES TABLE
        print(f"\n🏆 TOP 5 PARTICLE TYPES BY FREQUENCY")
        print("-"*120)
        print(f"{'#':<3} | {'Pattern Type':<20} | {'Count':<10} | {'Percentage':<12}")
        print("-"*120)

        for i, (ptype, count, pct) in enumerate(self.results['summary_statistics']['top_5_particle_types'], 1):
            print(f"{i:<3} | {ptype:<20} | {count:<10} | {pct:.1f}%")

        # TOP FILES BY PARTICLES TABLE
        print(f"\n📁 TOP 5 FILES BY PARTICLE COUNT")
        print("-"*120)
        print(f"{'#':<3} | {'File Name':<60} | {'Particles':<10}")
        print("-"*120)

        for i, (filename, count) in enumerate(self.results['summary_statistics']['top_5_files_by_particles'], 1):
            display_name = filename.split('/')[-1] if '/' in filename else filename
            print(f"{i:<3} | {display_name:<60} | {count:<10}")

        # DETAILED PARTICLES TABLE (TOP 25)
        print(f"\n🔬 DETAILED PARTICLES TABLE (TOP 25 BY CONFIDENCE)")
        print("-"*180)
        print(f"{'#':<3} | {'Particle ID':<20} | {'Type':<15} | {'Name':<25} | {'R':<2} | {'P':<2} | {'B':<2} | {'L':<2} | {'Conf':<6} | {'File':<40} | {'Line':<6}")
        print("-"*180)

        # Sort by confidence descending
        sorted_particles = sorted(
            self.results['particles_table'],
            key=lambda x: x['confidence'],
            reverse=True
        )

        for i, particle in enumerate(sorted_particles[:25], 1):
            file_name = particle['file_path'].split('/')[-1] if '/' in particle['file_path'] else particle['file_path']
            print(f"{i:<3} | {particle['particle_id']:<20} | {particle['type']:<15} | {particle['name']:<25} | "
                  f"{particle['responsibility']:<2} | {particle['purity']:<2} | {particle['boundary']:<2} | "
                  f"{particle['lifecycle']:<2} | {particle['confidence']:<6.1f}% | {file_name:<40} | {particle['line']:<6}")

        print("\n" + "="*180)
        print("🎯 ANALYSIS COMPLETE - All tables generated successfully!")
        print("="*180)

def main():
    """Main execution"""
    current_dir = "/Users/lech/PROJECTS_all/PROJECT_elements"

    generator = SpectrometerStatsGenerator()
    generator.analyze_current_repository(current_dir)

    # Print completion message
    print("\n✅ Comprehensive statistics and particles table generation complete!")

if __name__ == "__main__":
    main()