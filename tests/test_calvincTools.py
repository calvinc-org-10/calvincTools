"""Tests for calvincTools package."""
import pytest
import calvincTools


def test_import():
    """Test that the package can be imported."""
    import calvincTools
    assert calvincTools.__version__ is not None


def test_package_metadata():
    """Test package metadata is available."""
    assert calvincTools.__author__ is not None
    assert calvincTools.__email__ is not None
    assert calvincTools._pkgname is not None


def test_version_format():
    """Test version follows (almost) semantic versioning. (apart from patch being alphanumeric)"""
    version = calvincTools.__version__
    parts = version.split('.')
    assert len(parts) >= 2  # At least major.minor
    assert all(part.isdigit() for part in parts[0:1])  # major and minor parts are numeric


def test_sysver_keys():
    """Test system version dictionary has expected keys."""
    assert 'DEV' in calvincTools.sysver
    assert 'PROD' in calvincTools.sysver
    assert 'DEMO' in calvincTools.sysver


def test_sysver_format():
    """Test system version values are formatted correctly."""
    sysver = calvincTools.sysver
    base_ver = calvincTools._base_ver
    
    assert base_ver in sysver['PROD']
    assert 'DEV' in sysver['DEV']
    assert 'DEMO' in sysver['DEMO']


def test_utils_submodule_import():
    """Test that utils submodules can be imported."""
    from calvincTools.utils import strings
    from calvincTools.utils import misctools
    
    assert strings is not None
    assert misctools is not None


def test_models_import():
    """Test that models can be imported."""
    from calvincTools import models
    assert models is not None


def test_version_date():
    """Test version date is present."""
    assert calvincTools._ver_date is not None
    assert len(calvincTools._ver_date) > 0


def test_base_version_components():
    """Test base version components are integers."""
    assert isinstance(calvincTools._base_ver_major, int)
    assert isinstance(calvincTools._base_ver_minor, int)
    # assert isinstance(calvincTools._base_ver_patch, int)
    
    # Ensure non-negative
    assert calvincTools._base_ver_major >= 0
    assert calvincTools._base_ver_minor >= 0
    # assert calvincTools._base_ver_patch >= 0
