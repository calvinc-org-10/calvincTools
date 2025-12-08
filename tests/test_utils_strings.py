"""Tests for calvincTools.utils.strings module."""
import pytest
from calvincTools.utils.strings import (
    str2,
    WrapInQuotes,
    UnWrapQuotes,
    IsWrappedInQuotes
)


class TestStr2:
    """Test the str2 function."""
    
    def test_str2_with_string(self):
        """Test str2 with a regular string."""
        assert str2("hello") == "hello"
    
    def test_str2_with_integer(self):
        """Test str2 with an integer."""
        assert str2(42) == "42"
    
    def test_str2_with_float(self):
        """Test str2 with a float."""
        assert str2(3.14) == "3.14"
    
    def test_str2_with_none_default(self):
        """Test str2 with None returns empty string by default."""
        assert str2(None) == ""
    
    def test_str2_with_custom_type_transform(self):
        """Test str2 with custom type transforms."""
        transforms = {int: lambda: "INTEGER"}
        assert str2(42, TypeTransforms=transforms) == "INTEGER"
    
    def test_str2_with_custom_value_transform(self):
        """Test str2 with custom value transforms."""
        transforms = {999: lambda: "SPECIAL"}
        assert str2(999, ValueTransforms=transforms) == "SPECIAL"
    
    def test_str2_with_boolean(self):
        """Test str2 with boolean values."""
        assert str2(True) == "True"
        assert str2(False) == "False"
    
    def test_str2_with_list(self):
        """Test str2 with a list."""
        assert str2([1, 2, 3]) == "[1, 2, 3]"


class TestWrapInQuotes:
    """Test the WrapInQuotes function."""
    
    def test_wrap_with_default_quotes(self):
        """Test wrapping with default double quotes."""
        assert WrapInQuotes("hello") == '"hello"'
    
    def test_wrap_with_single_quotes(self):
        """Test wrapping with single quotes."""
        assert WrapInQuotes("hello", "'", "'") == "'hello'"
    
    def test_wrap_with_different_open_close(self):
        """Test wrapping with different open and close characters."""
        assert WrapInQuotes("hello", "[", "]") == "[hello]"
    
    def test_wrap_empty_string(self):
        """Test wrapping an empty string."""
        assert WrapInQuotes("") == '""'
    
    def test_wrap_string_with_spaces(self):
        """Test wrapping a string containing spaces."""
        assert WrapInQuotes("hello world") == '"hello world"'


class TestUnWrapQuotes:
    """Test the UnWrapQuotes function."""
    
    def test_unwrap_double_quotes(self):
        """Test unwrapping double quotes."""
        assert UnWrapQuotes('"hello"') == "hello"
    
    def test_unwrap_single_quotes(self):
        """Test unwrapping single quotes."""
        assert UnWrapQuotes("'hello'", "'") == "hello"
    
    def test_unwrap_no_quotes(self):
        """Test unwrapping string without quotes returns original."""
        assert UnWrapQuotes("hello") == "hello"
    
    def test_unwrap_partial_quotes(self):
        """Test unwrapping with only one quote returns original."""
        assert UnWrapQuotes('"hello') == '"hello'
        assert UnWrapQuotes('hello"') == 'hello"'
    
    def test_unwrap_empty_quotes(self):
        """Test unwrapping empty quoted string."""
        assert UnWrapQuotes('""') == ""
    
    def test_unwrap_nested_quotes(self):
        """Test unwrapping removes only outer quotes."""
        assert UnWrapQuotes('""hello""') == '"hello"'


class TestIsWrappedInQuotes:
    """Test the IsWrappedInQuotes function."""
    
    def test_is_wrapped_true_double_quotes(self):
        """Test detection of double quoted strings."""
        assert IsWrappedInQuotes('"hello"') is True
    
    def test_is_wrapped_true_single_quotes(self):
        """Test detection of single quoted strings."""
        assert IsWrappedInQuotes("'hello'", "'") is True
    
    def test_is_wrapped_false_no_quotes(self):
        """Test detection returns False for unquoted strings."""
        assert IsWrappedInQuotes("hello") is False
    
    def test_is_wrapped_false_partial_quotes(self):
        """Test detection returns False for partially quoted strings."""
        assert IsWrappedInQuotes('"hello') is False
        assert IsWrappedInQuotes('hello"') is False
    
    def test_is_wrapped_empty_quotes(self):
        """Test detection of empty quoted string."""
        assert IsWrappedInQuotes('""') is True
    
    def test_is_wrapped_with_spaces(self):
        """Test detection of quoted strings with spaces."""
        assert IsWrappedInQuotes('"hello world"') is True
