"""
Wave Extractor for Wave-Particle Symmetry.
Extracts API references from markdown documentation.
"""
import ast
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class ReferenceKind(Enum):
    """Type of documentation reference."""
    HEADER = "header"
    INLINE_CODE = "inline_code"
    CODE_BLOCK_DEF = "code_block_def"
    CODE_BLOCK_CALL = "code_block_call"


@dataclass
class WaveNode:
    """A documentation reference to a code symbol."""
    id: str                    # The extracted symbol name
    kind: ReferenceKind
    source_file: str
    line_number: int
    raw_text: str              # Original text as found
    context: Optional[str]     # Surrounding context


class WaveExtractor:
    """Extracts API references from markdown files."""

    # Regex patterns for extraction
    HEADER_PATTERN = re.compile(r'^#{1,6}\s+([a-zA-Z_][a-zA-Z0-9_.]*(?:\([^)]*\))?)', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`([a-zA-Z_][a-zA-Z0-9_.]*(?:\([^)]*\))?)`')
    CODE_BLOCK_PATTERN = re.compile(r'```(?:python|py)?\n(.*?)```', re.DOTALL)

    def __init__(self, docs_path: Path):
        """
        Initialize the WaveExtractor.

        Args:
            docs_path: Path to directory containing markdown documentation
        """
        self.docs_path = Path(docs_path)

    def extract_all(self) -> List[WaveNode]:
        """
        Extract references from all markdown files.

        Returns:
            List of WaveNode objects representing all found references
        """
        nodes = []

        # Find all markdown files recursively
        markdown_files = list(self.docs_path.rglob("*.md"))

        for md_file in markdown_files:
            try:
                file_nodes = self.extract_from_file(md_file)
                nodes.extend(file_nodes)
            except Exception as e:
                # Log warning but continue processing other files
                print(f"Warning: Failed to process {md_file}: {e}")
                continue

        return nodes

    def extract_from_file(self, file_path: Path) -> List[WaveNode]:
        """
        Extract references from a single markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of WaveNode objects found in this file
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                content = file_path.read_text(encoding='latin-1')
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                return []
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return []

        nodes = []
        file_str = str(file_path)

        # Extract from different sources
        nodes.extend(self._extract_from_headers(content, file_str))
        nodes.extend(self._extract_from_inline_code(content, file_str))
        nodes.extend(self._extract_from_code_blocks(content, file_str))

        return nodes

    def _extract_from_headers(self, content: str, file_path: str) -> List[WaveNode]:
        """
        Extract from ## headers like '## function_name()' or '## ClassName.method()'.

        Args:
            content: Markdown file content
            file_path: Path to source file (for metadata)

        Returns:
            List of WaveNode objects from headers
        """
        nodes = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            match = self.HEADER_PATTERN.match(line)
            if match:
                raw_text = match.group(1)
                normalized = self._normalize_reference(raw_text)

                # Get context (next non-empty line)
                context = None
                for i in range(line_num, min(line_num + 5, len(lines))):
                    if i < len(lines) and lines[i].strip():
                        context = lines[i].strip()
                        break

                node = WaveNode(
                    id=normalized,
                    kind=ReferenceKind.HEADER,
                    source_file=file_path,
                    line_number=line_num,
                    raw_text=raw_text,
                    context=context
                )
                nodes.append(node)

        return nodes

    def _extract_from_inline_code(self, content: str, file_path: str) -> List[WaveNode]:
        """
        Extract from `backtick` inline code.

        Args:
            content: Markdown file content
            file_path: Path to source file (for metadata)

        Returns:
            List of WaveNode objects from inline code
        """
        nodes = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            matches = self.INLINE_CODE_PATTERN.finditer(line)
            for match in matches:
                raw_text = match.group(1)
                normalized = self._normalize_reference(raw_text)

                # Use the surrounding line as context
                context = line.strip()

                node = WaveNode(
                    id=normalized,
                    kind=ReferenceKind.INLINE_CODE,
                    source_file=file_path,
                    line_number=line_num,
                    raw_text=raw_text,
                    context=context
                )
                nodes.append(node)

        return nodes

    def _extract_from_code_blocks(self, content: str, file_path: str) -> List[WaveNode]:
        """
        Extract from ```python code blocks.

        Args:
            content: Markdown file content
            file_path: Path to source file (for metadata)

        Returns:
            List of WaveNode objects from code blocks
        """
        nodes = []

        # Find all code blocks
        matches = self.CODE_BLOCK_PATTERN.finditer(content)

        for match in matches:
            code_block = match.group(1)

            # Calculate line number of the code block start
            # Count newlines before this match
            line_num = content[:match.start()].count('\n') + 1

            # Parse with AST
            try:
                tree = ast.parse(code_block)
            except SyntaxError:
                # Invalid Python syntax, skip
                continue

            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    wave_node = WaveNode(
                        id=node.name,
                        kind=ReferenceKind.CODE_BLOCK_DEF,
                        source_file=file_path,
                        line_number=line_num + node.lineno,
                        raw_text=f"def {node.name}",
                        context=code_block.split('\n')[node.lineno - 1].strip() if node.lineno <= len(code_block.split('\n')) else None
                    )
                    nodes.append(wave_node)

                # Extract function calls (attribute access like obj.method())
                elif isinstance(node, ast.Call):
                    call_id = self._extract_call_name(node)
                    if call_id:
                        wave_node = WaveNode(
                            id=call_id,
                            kind=ReferenceKind.CODE_BLOCK_CALL,
                            source_file=file_path,
                            line_number=line_num + node.lineno,
                            raw_text=call_id,
                            context=code_block.split('\n')[node.lineno - 1].strip() if node.lineno <= len(code_block.split('\n')) else None
                        )
                        nodes.append(wave_node)

        return nodes

    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """
        Extract the name from a function call AST node.

        Args:
            call_node: AST Call node

        Returns:
            String representation of the call (e.g., "obj.method" or "function")
        """
        func = call_node.func

        if isinstance(func, ast.Name):
            # Simple function call: func()
            return func.id
        elif isinstance(func, ast.Attribute):
            # Method call: obj.method()
            parts = []
            current = func

            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value

            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
                return '.'.join(parts)

        return None

    def _normalize_reference(self, raw: str) -> str:
        """
        Normalize a reference: strip (), [], whitespace.

        Args:
            raw: Raw reference string

        Returns:
            Normalized reference
        """
        # Remove backticks
        normalized = raw.strip('`')

        # Remove parentheses and their contents
        normalized = re.sub(r'\([^)]*\)', '', normalized)

        # Remove brackets and their contents
        normalized = re.sub(r'\[[^\]]*\]', '', normalized)

        # Remove extra whitespace
        normalized = normalized.strip()

        return normalized
