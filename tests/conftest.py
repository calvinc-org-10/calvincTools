"""Pytest configuration and fixtures for calvincTools tests."""
import pytest
import tempfile
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing misctools."""
    file_path = temp_dir / "sample.py"
    content = '''
class SampleClass:
    """A sample class for testing."""
    
    def method_one(self, arg1: str) -> str:
        return arg1
    
    def method_two(self, arg1: int, arg2: int) -> int:
        return arg1 + arg2

def sample_function(x: int, y: int) -> int:
    """A sample function for testing."""
    return x * y

def another_function(name: str) -> str:
    return f"Hello, {name}"
'''
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    from calvincTools.models import cMenuBase
    
    engine = create_engine("sqlite:///:memory:", echo=False)
    cMenuBase.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_menu_data():
    """Provide sample menu data for testing."""
    return {
        'group_name': 'TestGroup',
        'group_info': 'Test group information',
        'menu_name': 'TestMenu',
        'menu_info': 'Test menu information'
    }
