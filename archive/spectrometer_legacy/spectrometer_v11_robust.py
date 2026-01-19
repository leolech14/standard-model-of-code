#!/usr/bin/env python3
"""
SPECTROMETER V11 - ROBUST EDITION
Production-ready LHC of Software
Priority 1: Error Handling & Robustness Implementation
"""

import ast
import json
import logging
import re
import traceback
import warnings
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Iterator
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/spectrometer_v11.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SpectrometerV11')

# Suppress warnings in production
warnings.filterwarnings('ignore', category=SyntaxWarning)

@dataclass
class RobustnessMetrics:
    """Metrics for robustness monitoring"""
    total_files_processed: int = 0
    successful_parses: int = 0
    ast_successes: int = 0
    libcst_successes: int = 0
    regex_successes: int = 0
    errors_handled: int = 0
    error_types: Dict[str, int] = None

    def __post_init__(self):
        if self.error_types is None:
            self.error_types = {}

    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_files_processed == 0:
            return 0.0
        return (self.successful_parses / self.total_files_processed) * 100

    def get_fallback_usage(self) -> Dict[str, float]:
        """Calculate fallback usage percentages"""
        total = self.ast_successes + self.libcst_successes + self.regex_successes
        if total == 0:
            return {'ast': 0, 'libcst': 0, 'regex': 0}
        return {
            'ast': (self.ast_successes / total) * 100,
            'libcst': (self.libcst_successes / total) * 100,
            'regex': (self.regex_successes / total) * 100
        }

class ErrorHandler:
    """Centralized error handling and recovery"""

    def __init__(self):
        self.error_counts = defaultdict(int)
        self.recovery_strategies = {
            'SyntaxError': self._handle_syntax_error,
            'UnicodeDecodeError': self._handle_encoding_error,
            'MemoryError': self._handle_memory_error,
            'PermissionError': self._handle_permission_error,
            'ImportError': self._handle_import_error,
            'AttributeError': self._handle_attribute_error,
            'IndexError': self._handle_index_error,
            'KeyError': self._handle_key_error,
            'ValueError': self._handle_value_error,
            'TypeError': self._handle_type_error
        }

    @contextmanager
    def handle_errors(self, context: str = "Unknown"):
        """Context manager for error handling"""
        try:
            yield
        except Exception as e:
            error_type = type(e).__name__
            self.error_counts[error_type] += 1
            logger.warning(f"Error in {context}: {error_type}: {str(e)}")

            # Try recovery strategy if exists
            if error_type in self.recovery_strategies:
                return self.recovery_strategies[error_type](e, context)
            else:
                return self._handle_generic_error(e, context)

    def _handle_syntax_error(self, error: SyntaxError, context: str):
        """Handle syntax errors"""
        logger.info(f"Syntax error in {context}, will try regex fallback")
        return {'fallback': 'regex', 'reason': 'syntax_error'}

    def _handle_encoding_error(self, error: UnicodeDecodeError, context: str):
        """Handle encoding errors"""
        logger.info(f"Encoding error in {context}, trying different encodings")
        return {'fallback': 'encoding_retry', 'encodings': ['utf-8', 'latin-1', 'cp1252']}

    def _handle_memory_error(self, error: MemoryError, context: str):
        """Handle memory errors"""
        logger.error(f"Memory error in {context}: {str(error)}")
        return {'fallback': 'skip', 'reason': 'memory_error'}

    def _handle_permission_error(self, error: PermissionError, context: str):
        """Handle permission errors"""
        logger.warning(f"Permission denied in {context}")
        return {'fallback': 'skip', 'reason': 'permission_denied'}

    def _handle_import_error(self, error: ImportError, context: str):
        """Handle import errors"""
        logger.info(f"Import error in {context}: {str(error)}")
        return {'fallback': 'builtin_only', 'reason': 'missing_dependency'}

    def _handle_attribute_error(self, error: AttributeError, context: str):
        """Handle attribute errors"""
        logger.debug(f"Attribute error in {context}: {str(error)}")
        return {'fallback': 'safe_access', 'reason': 'missing_attribute'}

    def _handle_index_error(self, error: IndexError, context: str):
        """Handle index errors"""
        logger.debug(f"Index error in {context}: {str(error)}")
        return {'fallback': 'bounds_check', 'reason': 'out_of_bounds'}

    def _handle_key_error(self, error: KeyError, context: str):
        """Handle key errors"""
        logger.debug(f"Key error in {context}: {str(error)}")
        return {'fallback': 'default_value', 'reason': 'missing_key'}

    def _handle_value_error(self, error: ValueError, context: str):
        """Handle value errors"""
        logger.debug(f"Value error in {context}: {str(error)}")
        return {'fallback': 'validation', 'reason': 'invalid_value'}

    def _handle_type_error(self, error: TypeError, context: str):
        """Handle type errors"""
        logger.debug(f"Type error in {context}: {str(error)}")
        return {'fallback': 'type_check', 'reason': 'wrong_type'}

    def _handle_generic_error(self, error: Exception, context: str):
        """Handle generic errors"""
        logger.error(f"Unhandled error in {context}: {type(error).__name__}: {str(error)}")
        return {'fallback': 'skip', 'reason': 'unknown_error'}

class RobustParser:
    """Robust parser with multiple fallback strategies"""

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.metrics = RobustnessMetrics()

        # Pre-compile regex patterns for performance
        self.patterns = {
            'class_definition': re.compile(r'^\s*class\s+(\w+)', re.MULTILINE),
            'function_definition': re.compile(r'^\s*def\s+(\w+)', re.MULTILINE),
            'import_statement': re.compile(r'^\s*(?:from\s+\S+\s+)?import\s+', re.MULTILINE),
            'decorator': re.compile(r'^\s*@\w+', re.MULTILINE),
            'async_def': re.compile(r'^\s*async\s+def\s+(\w+)', re.MULTILINE)
        }

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse file with robust error handling and fallbacks"""
        self.metrics.total_files_processed += 1

        result = {
            'file_path': str(file_path),
            'success': False,
            'parser_used': 'none',
            'nodes': [],
            'errors': [],
            'metadata': {}
        }

        # Try multiple parsing strategies in order
        for strategy in ['ast', 'libcst', 'regex']:
            with self.error_handler.handle_errors(f"{strategy}_parse_{file_path.name}"):
                if strategy == 'ast':
                    parsed = self._parse_with_ast(file_path)
                elif strategy == 'libcst':
                    parsed = self._parse_with_libcst(file_path)
                else:  # regex
                    parsed = self._parse_with_regex(file_path)

                if parsed['success']:
                    result.update(parsed)
                    result['parser_used'] = strategy
                    self.metrics.successful_parses += 1

                    # Update strategy-specific metrics
                    if strategy == 'ast':
                        self.metrics.ast_successes += 1
                    elif strategy == 'libcst':
                        self.metrics.libcst_successes += 1
                    else:
                        self.metrics.regex_successes += 1

                    return result

        # All strategies failed
        self.metrics.errors_handled += 1
        logger.warning(f"All parsing strategies failed for {file_path}")
        return result

    def _parse_with_ast(self, file_path: Path) -> Dict[str, Any]:
        """Parse with Python AST (primary strategy)"""
        try:
            # Try multiple encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    content = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise UnicodeDecodeError("unknown", b"", 0, 0, "No valid encoding found")

            tree = ast.parse(content)
            nodes = []

            for node in ast.walk(tree):
                node_info = self._extract_ast_node_info(node)
                if node_info:
                    nodes.append(node_info)

            return {
                'success': True,
                'nodes': nodes,
                'metadata': {
                    'encoding_used': encoding,
                    'node_count': len(nodes),
                    'tree_depth': self._calculate_ast_depth(tree)
                }
            }

        except Exception as e:
            raise e

    def _parse_with_libcst(self, file_path: Path) -> Dict[str, Any]:
        """Parse with LibCST (secondary strategy)"""
        try:
            # Try to import libcst
            import libcst as cst

            content = file_path.read_text(encoding='utf-8', errors='ignore')
            module = cst.parse_module(content)

            nodes = []
            for node in module.walk(cst.Module):
                if isinstance(node, (cst.ClassDef, cst.FunctionDef)):
                    nodes.append({
                        'type': 'class' if isinstance(node, cst.ClassDef) else 'function',
                        'name': node.name.value if hasattr(node.name, 'value') else str(node.name),
                        'line': node.position.start.line if node.position else 0,
                        'column': node.position.start.column if node.position else 0
                    })

            return {
                'success': True,
                'nodes': nodes,
                'metadata': {
                    'parser': 'libcst',
                    'node_count': len(nodes)
                }
            }

        except ImportError:
            # LibCST not available, skip to next strategy
            raise ImportError("LibCST not available")
        except Exception as e:
            raise e

    def _parse_with_regex(self, file_path: Path) -> Dict[str, Any]:
        """Parse with regex (last resort)"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            nodes = []

            # Find classes
            for match in self.patterns['class_definition'].finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                nodes.append({
                    'type': 'class',
                    'name': match.group(1),
                    'line': line_num,
                    'column': match.start() - content.rfind('\n', 0, match.start()) - 1
                })

            # Find functions
            for match in self.patterns['function_definition'].finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                nodes.append({
                    'type': 'function',
                    'name': match.group(1),
                    'line': line_num,
                    'column': match.start() - content.rfind('\n', 0, match.start()) - 1
                })

            # Find async functions
            for match in self.patterns['async_def'].finditer(content):
                line_num = content[:match.start()].count('\n') + 1
                nodes.append({
                    'type': 'async_function',
                    'name': match.group(1),
                    'line': line_num,
                    'column': match.start() - content.rfind('\n', 0, match.start()) - 1
                })

            return {
                'success': True,
                'nodes': nodes,
                'metadata': {
                    'parser': 'regex',
                    'node_count': len(nodes),
                    'line_count': len(lines)
                }
            }

        except Exception as e:
            raise e

    def _extract_ast_node_info(self, node) -> Optional[Dict[str, Any]]:
        """Extract information from AST node"""
        try:
            if isinstance(node, ast.ClassDef):
                return {
                    'type': 'class',
                    'name': node.name,
                    'line': node.lineno,
                    'column': node.col_offset,
                    'bases': [base.id if hasattr(base, 'id') else str(base) for base in node.bases],
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                    'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                }
            elif isinstance(node, ast.FunctionDef):
                return {
                    'type': 'function',
                    'name': node.name,
                    'line': node.lineno,
                    'column': node.col_offset,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                    'returns': ast.unparse(node.returns) if hasattr(node, 'returns') and node.returns else None
                }
            elif isinstance(node, ast.AsyncFunctionDef):
                return {
                    'type': 'async_function',
                    'name': node.name,
                    'line': node.lineno,
                    'column': node.col_offset,
                    'args': [arg.arg for arg in node.args.args],
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                }
        except:
            pass
        return None

    def _calculate_ast_depth(self, node, depth=0) -> int:
        """Calculate maximum depth of AST tree"""
        if not hasattr(node, 'body') or not isinstance(node.body, list):
            return depth

        max_child_depth = depth
        for child in node.body:
            if isinstance(child, ast.AST):
                child_depth = self._calculate_ast_depth(child, depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

class SpectrometerV11:
    """Spectrometer V11 - Robust Production Edition"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.error_handler = ErrorHandler()
        self.parser = RobustParser(self.error_handler)
        self.start_time = datetime.now()

        # Setup additional logging
        self.setup_detailed_logging()

        logger.info("="*80)
        logger.info("SPECTROMETER V11 - ROBUST EDITION INITIALIZED")
        logger.info(f"Start time: {self.start_time}")
        logger.info("="*80)

    def setup_detailed_logging(self):
        """Setup detailed error tracking"""
        self.error_log = []
        self.success_log = []

    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository with comprehensive error handling"""
        logger.info(f"Starting analysis of repository: {repo_path}")

        # Validate input
        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return {'error': 'Repository not found', 'path': str(repo_path)}

        # Get all Python files
        python_files = list(repo_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files to analyze")

        # Process files with progress tracking
        results = {
            'repository_path': str(repo_path),
            'start_time': self.start_time.isoformat(),
            'total_files': len(python_files),
            'file_results': [],
            'robustness_metrics': {},
            'error_summary': {},
            'success_summary': {}
        }

        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                logger.info(f"Processing {i}/{len(python_files)} files... ({i/len(python_files)*100:.1f}%)")

            # Analyze file with robust parsing
            file_result = self.parser.parse_file(file_path)
            file_result['file_index'] = i
            results['file_results'].append(file_result)

            # Track success/failure
            if file_result['success']:
                self.success_log.append(file_result)
            else:
                self.error_log.append(file_result)

        # Calculate final metrics
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        results.update({
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'robustness_metrics': asdict(self.parser.metrics),
            'error_summary': {
                'total_errors': len(self.error_log),
                'error_types': dict(self.error_handler.error_counts),
                'files_with_errors': [r['file_path'] for r in self.error_log if not r['success']]
            },
            'success_summary': {
                'total_successes': len(self.success_log),
                'success_rate': self.parser.metrics.get_success_rate(),
                'fallback_usage': self.parser.metrics.get_fallback_usage(),
                'files_per_second': len(python_files) / duration if duration > 0 else 0
            }
        })

        # Log final summary
        self.log_final_summary(results)

        # Save detailed report
        self.save_report(results)

        return results

    def log_final_summary(self, results: Dict[str, Any]):
        """Log final analysis summary"""
        logger.info("="*80)
        logger.info("ANALYSIS COMPLETE - FINAL SUMMARY")
        logger.info("="*80)

        metrics = results['robustness_metrics']
        success = results['success_summary']

        logger.info(f"✅ Files processed: {metrics['total_files_processed']:,}")
        logger.info(f"✅ Successful parses: {metrics['successful_parses']:,}")
        logger.info(f"✅ Success rate: {success['success_rate']:.1f}%")
        logger.info(f"✅ Duration: {results['duration_seconds']:.1f} seconds")
        logger.info(f"✅ Throughput: {success['files_per_second']:.0f} files/second")

        logger.info("\n📊 Parser usage:")
        for parser, pct in success['fallback_usage'].items():
            logger.info(f"   • {parser.upper()}: {pct:.1f}%")

        if results['error_summary']['total_errors'] > 0:
            logger.info(f"\n⚠️  Errors handled: {results['error_summary']['total_errors']}")
            for error_type, count in results['error_summary']['error_types'].items():
                logger.info(f"   • {error_type}: {count}")

        logger.info("="*80)

    def save_report(self, results: Dict[str, Any]):
        """Save detailed analysis report"""
        timestamp = int(self.start_time.timestamp())
        report_path = Path(f"/tmp/spectrometer_v11_report_{timestamp}.json")

        try:
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"\n💾 Detailed report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

# Main execution
if __name__ == "__main__":
    # Configuration
    config = {
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'timeout_seconds': 30,
        'enable_libcst': True,
        'parallel_processing': False  # Disabled for robustness
    }

    # Initialize spectrometer
    spectrometer = SpectrometerV11(config)

    # Analyze current repository
    repo_path = Path(__file__).parent
    results = spectrometer.analyze_repository(repo_path)

    # Print key metrics
    print("\n🎯 KEY METRICS:")
    print(f"   Success Rate: {results['success_summary']['success_rate']:.1f}%")
    print(f"   Files/Second: {results['success_summary']['files_per_second']:.0f}")
    print(f"   Error Rate: {results['error_summary']['total_errors']/results['total_files']*100:.1f}%")

    # Determine if success criteria met
    success_criteria_met = (
        results['success_summary']['success_rate'] >= 95 and
        results['error_summary']['total_errors'] == 0
    )

    print(f"\n{'✅ SUCCESS CRITERIA MET' if success_criteria_met else '⚠️  NEEDS IMPROVEMENT'}")