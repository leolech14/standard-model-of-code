"""
Test suite for VisibilityAnalyzer.

Validates visibility classification according to Python conventions:
- __all__ precedence
- Underscore conventions
- Class method visibility
- Public exports
"""
import pytest
from src.core.visibility_analyzer import VisibilityAnalyzer, Visibility


def test_all_declaration_takes_precedence():
    """Test that __all__ overrides naming conventions."""
    code = '''
__all__ = ["public_func"]
def public_func(): pass
def other_func(): pass  # Not in __all__, should be private
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["public_func"].visibility == Visibility.PUBLIC
    assert result["other_func"].visibility == Visibility.PRIVATE


def test_underscore_conventions():
    """Test naming convention visibility rules."""
    code = '''
def public(): pass
def _protected(): pass
def __private(): pass
def __dunder__(): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["public"].visibility == Visibility.PUBLIC
    assert result["_protected"].visibility == Visibility.PROTECTED
    assert result["__private"].visibility == Visibility.PRIVATE
    assert result["__dunder__"].visibility == Visibility.SPECIAL


def test_class_methods():
    """Test visibility of methods within classes."""
    code = '''
class MyClass:
    def public_method(self): pass
    def _protected_method(self): pass
    def __private_method(self): pass
    def __init__(self): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["MyClass.public_method"].visibility == Visibility.PUBLIC
    assert result["MyClass._protected_method"].visibility == Visibility.PROTECTED
    assert result["MyClass.__private_method"].visibility == Visibility.PRIVATE
    assert result["MyClass.__init__"].visibility == Visibility.SPECIAL


def test_get_public_exports():
    """Test extraction of public API symbols."""
    code = '''
__all__ = ["func_a", "ClassB"]
def func_a(): pass
def func_b(): pass
class ClassB: pass
'''
    analyzer = VisibilityAnalyzer(code)
    exports = analyzer.get_public_exports()
    assert "func_a" in exports
    assert "ClassB" in exports
    assert "func_b" not in exports


def test_syntax_error_handling():
    """Test graceful handling of unparseable code."""
    code = "def broken syntax here"
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result == {}


def test_no_all_declaration():
    """Test default visibility when __all__ is not defined."""
    code = '''
def public_func(): pass
def _protected_func(): pass
class PublicClass: pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["public_func"].visibility == Visibility.PUBLIC
    assert result["_protected_func"].visibility == Visibility.PROTECTED
    assert result["PublicClass"].visibility == Visibility.PUBLIC


def test_qualified_names():
    """Test that qualified names include class context."""
    code = '''
class Outer:
    class Inner:
        def method(self): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert "Outer" in result
    assert "Outer.Inner" in result
    assert "Outer.Inner.method" in result


def test_async_functions():
    """Test visibility of async function definitions."""
    code = '''
async def public_async(): pass
async def _protected_async(): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["public_async"].visibility == Visibility.PUBLIC
    assert result["_protected_async"].visibility == Visibility.PROTECTED


def test_module_variables():
    """Test visibility of module-level variable assignments."""
    code = '''
PUBLIC_VAR = 42
_protected_var = "hidden"
__private_var = True
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["PUBLIC_VAR"].visibility == Visibility.PUBLIC
    assert result["_protected_var"].visibility == Visibility.PROTECTED
    assert result["__private_var"].visibility == Visibility.PRIVATE


def test_is_in_all_flag():
    """Test that is_in_all flag is set correctly."""
    code = '''
__all__ = ["exported"]
def exported(): pass
def not_exported(): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["exported"].is_in_all is True
    assert result["not_exported"].is_in_all is False


def test_line_numbers():
    """Test that line numbers are captured correctly."""
    code = '''
def func1(): pass
def func2(): pass

class MyClass:
    def method(self): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    assert result["func1"].line_number == 2
    assert result["func2"].line_number == 3
    assert result["MyClass"].line_number == 5
    assert result["MyClass.method"].line_number == 6


def test_empty_source():
    """Test handling of empty source code."""
    analyzer = VisibilityAnalyzer("")
    result = analyzer.analyze()
    assert result == {}


def test_all_with_non_strings():
    """Test that __all__ with non-string elements is handled gracefully."""
    code = '''
__all__ = ["valid", 123, None]
def valid(): pass
'''
    analyzer = VisibilityAnalyzer(code)
    result = analyzer.analyze()
    # Should only extract the string "valid"
    exports = analyzer.get_public_exports()
    assert "valid" in exports
    assert len(exports) == 1
