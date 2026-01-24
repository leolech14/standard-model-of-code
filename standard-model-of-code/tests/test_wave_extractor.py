"""
Tests for Wave Extractor.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from src.core.wave_extractor import WaveExtractor, ReferenceKind, WaveNode


class TestWaveExtractor:
    """Test suite for WaveExtractor."""

    def test_extract_from_headers(self):
        """Test extraction from markdown headers."""
        md_content = '''
# API Reference

## validate()

Some description.

## UserService.create()

Another description.
'''
        extractor = WaveExtractor(Path("/tmp"))
        nodes = extractor._extract_from_headers(md_content, "test.md")
        ids = [n.id for n in nodes]

        assert "validate" in ids
        assert "UserService.create" in ids
        assert all(n.kind == ReferenceKind.HEADER for n in nodes)

    def test_extract_from_inline_code(self):
        """Test extraction from inline code blocks."""
        md_content = '''
Call `UserService.validate(input)` to validate.
The `create` method returns a new instance.
'''
        extractor = WaveExtractor(Path("/tmp"))
        nodes = extractor._extract_from_inline_code(md_content, "test.md")
        ids = [n.id for n in nodes]

        assert "UserService.validate" in ids
        assert "create" in ids
        assert all(n.kind == ReferenceKind.INLINE_CODE for n in nodes)

    def test_extract_from_code_blocks(self):
        """Test extraction from Python code blocks."""
        md_content = '''
Example usage:

```python
def example():
    service = UserService()
    service.validate(data)
```
'''
        extractor = WaveExtractor(Path("/tmp"))
        nodes = extractor._extract_from_code_blocks(md_content, "test.md")
        ids = [n.id for n in nodes]

        # Should find both the def and the call
        assert "example" in ids or any("validate" in i for i in ids)

        # Check that we have both kinds
        kinds = {n.kind for n in nodes}
        assert ReferenceKind.CODE_BLOCK_DEF in kinds or ReferenceKind.CODE_BLOCK_CALL in kinds

    def test_normalize_reference(self):
        """Test reference normalization."""
        extractor = WaveExtractor(Path("/tmp"))

        assert extractor._normalize_reference("validate()") == "validate"
        assert extractor._normalize_reference("UserService.validate(input)") == "UserService.validate"
        assert extractor._normalize_reference("`create`") == "create"
        assert extractor._normalize_reference("func[index]") == "func"
        assert extractor._normalize_reference("  method()  ") == "method"

    def test_extract_from_file(self):
        """Test extraction from a complete markdown file."""
        # Create a temporary directory and file
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "test.md"
            test_file.write_text('''
# API Documentation

## MyClass.method()

This is a method.

Use `MyClass.method()` like this:

```python
def example():
    obj = MyClass()
    obj.method()
```
''')

            extractor = WaveExtractor(Path(temp_dir))
            nodes = extractor.extract_from_file(test_file)

            # Should find references from headers, inline code, and code blocks
            assert len(nodes) > 0

            ids = [n.id for n in nodes]
            # Should have method from header
            assert "MyClass.method" in ids

            # Should have various kinds
            kinds = {n.kind for n in nodes}
            assert len(kinds) >= 2  # At least header and one other type

        finally:
            shutil.rmtree(temp_dir)

    def test_extract_all(self):
        """Test extraction from multiple markdown files."""
        # Create a temporary directory structure
        temp_dir = tempfile.mkdtemp()
        try:
            # Create multiple markdown files
            (Path(temp_dir) / "api.md").write_text("## function_a()")
            (Path(temp_dir) / "guide.md").write_text("Call `function_b()` here")

            # Create subdirectory
            subdir = Path(temp_dir) / "docs"
            subdir.mkdir()
            (subdir / "reference.md").write_text("## function_c()")

            extractor = WaveExtractor(Path(temp_dir))
            nodes = extractor.extract_all()

            # Should find references from all files
            assert len(nodes) >= 3

            ids = [n.id for n in nodes]
            assert "function_a" in ids
            assert "function_b" in ids
            assert "function_c" in ids

        finally:
            shutil.rmtree(temp_dir)

    def test_malformed_markdown(self):
        """Test that malformed markdown doesn't crash the extractor."""
        md_content = '''
## Incomplete header with code `

```python
# Incomplete code block
def broken(
'''
        extractor = WaveExtractor(Path("/tmp"))

        # Should not raise exceptions
        nodes = extractor._extract_from_headers(md_content, "test.md")
        assert isinstance(nodes, list)

        nodes = extractor._extract_from_inline_code(md_content, "test.md")
        assert isinstance(nodes, list)

        nodes = extractor._extract_from_code_blocks(md_content, "test.md")
        assert isinstance(nodes, list)

    def test_encoding_errors(self):
        """Test graceful handling of encoding errors."""
        # Create a file with non-UTF8 content
        temp_dir = tempfile.mkdtemp()
        try:
            test_file = Path(temp_dir) / "binary.md"
            # Write some binary data
            test_file.write_bytes(b'\x80\x81\x82## test()')

            extractor = WaveExtractor(Path(temp_dir))
            # Should not crash, should return empty or partial results
            nodes = extractor.extract_from_file(test_file)
            assert isinstance(nodes, list)

        finally:
            shutil.rmtree(temp_dir)

    def test_wave_node_structure(self):
        """Test that WaveNode has correct structure."""
        md_content = "## test_function()"
        extractor = WaveExtractor(Path("/tmp"))
        nodes = extractor._extract_from_headers(md_content, "test.md")

        assert len(nodes) == 1
        node = nodes[0]

        assert node.id == "test_function"
        assert node.kind == ReferenceKind.HEADER
        assert node.source_file == "test.md"
        assert node.line_number > 0
        assert node.raw_text == "test_function()"
        # Context may be None or a string
        assert node.context is None or isinstance(node.context, str)

    def test_complex_code_block_extraction(self):
        """Test extraction from complex code blocks with multiple calls."""
        md_content = '''
```python
class Service:
    def __init__(self):
        self.client = Client()

    def process(self, data):
        validated = self.validator.validate(data)
        result = self.client.send(validated)
        return self.formatter.format(result)
```
'''
        extractor = WaveExtractor(Path("/tmp"))
        nodes = extractor._extract_from_code_blocks(md_content, "test.md")

        ids = [n.id for n in nodes]

        # Should find method definitions
        # Should find attribute calls like self.validator.validate, self.client.send
        assert len(nodes) > 0

        # Check we have both defs and calls
        kinds = {n.kind for n in nodes}
        assert ReferenceKind.CODE_BLOCK_DEF in kinds or ReferenceKind.CODE_BLOCK_CALL in kinds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
