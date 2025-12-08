"""Tests for calvincTools.utils.misctools module."""
import pytest
from calvincTools.utils.misctools import show_fns, pretty_show_fns


class TestShowFns:
    """Test the show_fns function."""
    
    def test_show_fns_with_sample_file(self, sample_python_file):
        """Test show_fns extracts functions and classes correctly."""
        result = show_fns(sample_python_file)
        
        # Check structure
        assert 'classes' in result
        assert 'functions' in result
        assert isinstance(result['classes'], list)
        assert isinstance(result['functions'], list)
        
        # Check that we found the sample class
        class_items = [item for item in result['classes'] if 'SampleClass' in item]
        assert len(class_items) > 0
        
        # Check that we found the sample functions
        function_names = [item for item in result['functions']]
        assert any('sample_function' in fn for fn in function_names)
        assert any('another_function' in fn for fn in function_names)
    
    def test_show_fns_class_methods(self, sample_python_file):
        """Test that class methods are extracted."""
        result = show_fns(sample_python_file)
        
        # Check for class methods
        class_items = result['classes']
        assert any('method_one' in item for item in class_items)
        assert any('method_two' in item for item in class_items)
    
    def test_show_fns_line_numbers(self, sample_python_file):
        """Test that line numbers are included in output."""
        result = show_fns(sample_python_file)
        
        # All items should contain line number information
        all_items = result['classes'] + result['functions']
        assert all('lines' in item for item in all_items)
    
    def test_show_fns_function_signatures(self, sample_python_file):
        """Test that function signatures include parameters."""
        result = show_fns(sample_python_file)
        
        # Check that functions have parameter information
        sample_fn = [fn for fn in result['functions'] if 'sample_function' in fn]
        assert len(sample_fn) > 0
        # Should contain parameters x and y
        assert 'x' in sample_fn[0] or '(' in sample_fn[0]


class TestPrettyShowFns:
    """Test the pretty_show_fns function."""
    
    def test_pretty_show_fns_returns_string(self, sample_python_file):
        """Test pretty_show_fns returns a formatted string."""
        result = pretty_show_fns(sample_python_file)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_pretty_show_fns_contains_functions(self, sample_python_file):
        """Test pretty output contains function information."""
        result = pretty_show_fns(sample_python_file)
        assert 'sample_function' in result
        assert 'another_function' in result
    
    def test_pretty_show_fns_contains_classes(self, sample_python_file):
        """Test pretty output contains class information."""
        result = pretty_show_fns(sample_python_file)
        assert 'SampleClass' in result
    
    def test_pretty_show_fns_formatting(self, sample_python_file):
        """Test pretty output is formatted with sections."""
        result = pretty_show_fns(sample_python_file)
        # Should have separate sections or clear formatting
        assert 'Functions' in result or 'Classes' in result or '\n' in result


class TestShowFnsEdgeCases:
    """Test edge cases and error handling."""
    
    def test_show_fns_empty_file(self, temp_dir):
        """Test show_fns with an empty Python file."""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")
        
        result = show_fns(str(empty_file))
        assert result['classes'] == []
        assert result['functions'] == []
    
    def test_show_fns_only_imports(self, temp_dir):
        """Test show_fns with file containing only imports."""
        import_file = temp_dir / "imports.py"
        import_file.write_text("import os\nimport sys\nfrom pathlib import Path\n")
        
        result = show_fns(str(import_file))
        assert result['classes'] == []
        assert result['functions'] == []
    
    def test_show_fns_nested_classes(self, temp_dir):
        """Test show_fns with nested class definitions."""
        nested_file = temp_dir / "nested.py"
        content = '''
class OuterClass:
    def outer_method(self):
        pass
    
    class InnerClass:
        def inner_method(self):
            pass
'''
        nested_file.write_text(content)
        
        result = show_fns(str(nested_file))
        # Should find at least the outer class
        assert len(result['classes']) > 0
        assert any('OuterClass' in item for item in result['classes'])
    
    def test_show_fns_decorators(self, temp_dir):
        """Test show_fns with decorated functions."""
        decorated_file = temp_dir / "decorated.py"
        content = '''
def decorator(func):
    return func

@decorator
def decorated_function(x: int) -> int:
    return x * 2

class DecoratedClass:
    @staticmethod
    def static_method():
        pass
    
    @classmethod
    def class_method(cls):
        pass
'''
        decorated_file.write_text(content)
        
        result = show_fns(str(decorated_file))
        # Should find decorated function and class
        assert any('decorated_function' in item for item in result['functions'])
        assert any('DecoratedClass' in item for item in result['classes'])
    
    def test_show_fns_type_hints(self, temp_dir):
        """Test show_fns with complex type hints."""
        typed_file = temp_dir / "typed.py"
        content = '''
from typing import List, Dict, Optional, Union

def typed_function(
    items: List[str],
    mapping: Dict[str, int],
    optional: Optional[str] = None
) -> Union[str, None]:
    return optional

class TypedClass:
    def typed_method(self, value: int) -> bool:
        return value > 0
'''
        typed_file.write_text(content)
        
        result = show_fns(str(typed_file))
        assert any('typed_function' in item for item in result['functions'])
        assert any('TypedClass' in item for item in result['classes'])
