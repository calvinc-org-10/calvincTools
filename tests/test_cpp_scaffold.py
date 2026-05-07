"""Tests for initial C++ migration scaffold."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CPP_ROOT = REPO_ROOT / "calvincTools-cpp"


def test_cpp_scaffold_files_exist():
    assert (CPP_ROOT / "CMakeLists.txt").is_file()
    assert (CPP_ROOT / "include" / "calvinc_tools" / "version.hpp").is_file()
    assert (CPP_ROOT / "src" / "version.cpp").is_file()


def test_cpp_version_matches_python_package_version():
    python_version_file = (REPO_ROOT / "calvincTools" / "__version__.py").read_text(encoding="utf-8")
    cpp_version_file = (CPP_ROOT / "src" / "version.cpp").read_text(encoding="utf-8")

    assert '__version__ = _base_ver' in python_version_file
    assert 'return "2.2.0";' in cpp_version_file
