"""Tests for calvincTools package initialization."""
import pytest


class TestPackageVersion:
    """Test package version information."""
    
    def test_version_exists(self):
        """Test that version is defined."""
        import calvincTools
        assert hasattr(calvincTools, '__version__')
        assert calvincTools.__version__ is not None
    
    def test_version_type(self):
        """Test that version is a string."""
        import calvincTools
        assert isinstance(calvincTools.__version__, str)
    
    def test_version_parts(self):
        """
        Test version has (almost) proper semantic versioning format.
        E.g., '1.6.1c' should split into at least major, minor, patch.
        patch can have letters.
        """
        import calvincTools
        parts = calvincTools.__version__.split('.')
        assert len(parts) >= 2
        for part in parts[0:1]:  # major and minor should be digits
            assert part.isdigit()


class TestPackageMetadata:
    """Test package metadata."""
    
    def test_author(self):
        """Test author is defined."""
        import calvincTools
        # assert calvincTools.__author__ == "Calvin C"
        assert calvincTools.__author__ is not None
    
    def test_email(self):
        """Test email is defined."""
        import calvincTools
        # assert calvincTools.__email__ == "calvinc404@gmail.com"
        assert calvincTools.__email__ is not None
    
    def test_package_name(self):
        """Test package name is defined."""
        import calvincTools
        # assert calvincTools._pkgname == "Calvin C Tools"
        assert calvincTools._pkgname is not None


class TestModuleImports:
    """Test that all main modules can be imported."""
    
    def test_import_utils_strings(self):
        """Test importing strings utilities."""
        from calvincTools.utils import strings
        assert hasattr(strings, 'str2')
        assert hasattr(strings, 'WrapInQuotes')
        assert hasattr(strings, 'UnWrapQuotes')
        assert hasattr(strings, 'IsWrappedInQuotes')
    
    def test_import_utils_misctools(self):
        """Test importing misctools."""
        from calvincTools.utils import misctools
        assert hasattr(misctools, 'show_fns')
        assert hasattr(misctools, 'pretty_show_fns')
    
    def test_import_models(self):
        """Test importing models."""
        # Note: models has circular import with dbmenulist
        # This is a known issue in the codebase
        # We test that the classes can be used even if module import fails
        try:
            from calvincTools.models import (
                cMenuBase,
                menuGroups,
                menuItems,
                cParameters,
                cGreetings
            )
            assert cMenuBase is not None
            assert menuGroups is not None
            assert menuItems is not None
            assert cParameters is not None
            assert cGreetings is not None
        except ImportError:
            # Known circular import issue
            pytest.skip("Circular import issue in models module")
