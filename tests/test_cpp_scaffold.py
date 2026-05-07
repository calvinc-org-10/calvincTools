"""Tests for initial C++ migration scaffold."""

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CPP_ROOT = REPO_ROOT / "calvincTools-cpp"


def test_cpp_scaffold_files_exist():
    assert (CPP_ROOT / "CMakeLists.txt").is_file()
    assert (CPP_ROOT / "include" / "calvinc_tools" / "version_config.hpp.in").is_file()
    assert (CPP_ROOT / "include" / "calvinc_tools" / "version.hpp").is_file()
    assert (CPP_ROOT / "src" / "version.cpp").is_file()


def test_cpp_version_matches_python_package_version():
    python_version_file = (REPO_ROOT / "calvincTools" / "__version__.py").read_text(encoding="utf-8")
    cmake_file = (CPP_ROOT / "CMakeLists.txt").read_text(encoding="utf-8")
    cpp_version_file = (CPP_ROOT / "src" / "version.cpp").read_text(encoding="utf-8")

    major = re.search(r"_base_ver_major\s*=\s*(\d+)", python_version_file)
    minor = re.search(r"_base_ver_minor\s*=\s*(\d+)", python_version_file)
    patch = re.search(r"_base_ver_patch\s*=\s*['\"]([^'\"]+)['\"]", python_version_file)
    cmake_version = re.search(r"project\(calvincToolsCpp VERSION ([0-9A-Za-z\.\-_]+) ", cmake_file)

    assert major and minor and patch and cmake_version
    assert "return CALVINC_TOOLS_VERSION;" in cpp_version_file
    assert cmake_version.group(1) == f"{major.group(1)}.{minor.group(1)}.{patch.group(1)}"
