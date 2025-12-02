"""Tests for calvincTools package."""
import pytest


def test_import():
    """Test that the package can be imported."""
    import calvincTools
    assert calvincTools.__version__ == "1.2.0"
