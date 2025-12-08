"""Test runner script for calvincTools.

This script provides convenient commands for running tests with various options.
"""
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print its output."""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("calvincTools Test Runner")
        print("\nUsage: python run_tests.py [command]")
        print("\nCommands:")
        print("  all          - Run all tests")
        print("  unit         - Run only unit tests")
        print("  integration  - Run only integration tests")
        print("  coverage     - Run tests with coverage report")
        print("  fast         - Run only fast tests (skip slow ones)")
        print("  verbose      - Run all tests with verbose output")
        print("  file <path>  - Run tests in specific file")
        print("  watch        - Run tests in watch mode (requires pytest-watch)")
        print("\nExamples:")
        print("  python run_tests.py all")
        print("  python run_tests.py coverage")
        print("  python run_tests.py file tests/test_utils_strings.py")
        return 0
    
    command = sys.argv[1].lower()
    
    # Base pytest command
    base_cmd = [sys.executable, "-m", "pytest"]
    
    if command == "all":
        return run_command(base_cmd, "All tests")
    
    elif command == "unit":
        return run_command(
            base_cmd + ["-m", "unit"],
            "Unit tests only"
        )
    
    elif command == "integration":
        return run_command(
            base_cmd + ["-m", "integration"],
            "Integration tests only"
        )
    
    elif command == "coverage":
        return run_command(
            base_cmd + [
                "--cov=calvincTools",
                "--cov-report=term-missing",
                "--cov-report=html"
            ],
            "Tests with coverage report"
        )
    
    elif command == "fast":
        return run_command(
            base_cmd + ["-m", "not slow"],
            "Fast tests only (excluding slow tests)"
        )
    
    elif command == "verbose":
        return run_command(
            base_cmd + ["-v", "-s"],
            "All tests with verbose output"
        )
    
    elif command == "file":
        if len(sys.argv) < 3:
            print("Error: Please specify a test file")
            print("Usage: python run_tests.py file <path>")
            return 1
        test_file = sys.argv[2]
        return run_command(
            base_cmd + [test_file],
            f"Tests in {test_file}"
        )
    
    elif command == "watch":
        try:
            return run_command(
                [sys.executable, "-m", "pytest_watch"],
                "Tests in watch mode"
            )
        except FileNotFoundError:
            print("Error: pytest-watch not installed")
            print("Install with: pip install pytest-watch")
            return 1
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python run_tests.py' for help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
