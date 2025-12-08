# Testing Guide for calvincTools

## Quick Start

### Install Development Dependencies
```bash
pip install -e ".[dev]"
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=calvincTools --cov-report=html

# Run specific test file
pytest tests/test_utils_strings.py

# Run with verbose output
pytest -v
```

## Test Organization

### Test Files
- `test_calvincTools.py` - Package-level tests
- `test_package.py` - Package initialization and metadata
- `test_utils_strings.py` - String utility functions
- `test_utils_calvindate.py` - Date utility functions and calvindate class
- `test_utils_misctools.py` - Miscellaneous tools (AST parsing)
- `test_models.py` - Database models (SQLAlchemy)
- `test_integration.py` - Integration tests across modules

### Test Categories

#### Unit Tests
Test individual functions and methods in isolation.

```python
def test_str2_with_string():
    """Test str2 with a regular string."""
    assert str2("hello") == "hello"
```

#### Integration Tests
Test interaction between multiple components.

```python
@pytest.mark.integration
def test_complete_workflow(test_session):
    """Test a complete workflow using multiple components."""
    # Create related objects and test their interaction
```

## Running Tests

### Using pytest directly
```bash
# All tests
pytest

# Specific file
pytest tests/test_utils_strings.py

# Specific class
pytest tests/test_utils_strings.py::TestStr2

# Specific test
pytest tests/test_utils_strings.py::TestStr2::test_str2_with_string

# With markers
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
pytest -m unit        # Only unit tests

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Using the test runner script
```bash
# Run all tests
python run_tests.py all

# Run with coverage
python run_tests.py coverage

# Run only fast tests
python run_tests.py fast

# Run specific file
python run_tests.py file tests/test_utils_strings.py

# Run with verbose output
python run_tests.py verbose
```

## Test Coverage

### Generate Coverage Report
```bash
pytest --cov=calvincTools --cov-report=html
```

View the report:
```bash
# Opens in default browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals
- Overall coverage: > 80%
- Critical modules: > 90%
- Utility functions: 100%

### Checking Coverage
```bash
# Terminal report with missing lines
pytest --cov=calvincTools --cov-report=term-missing

# Generate both HTML and terminal report
pytest --cov=calvincTools --cov-report=html --cov-report=term-missing
```

## Writing Tests

### Test Function Naming
```python
def test_<what_is_being_tested>():
    """Brief description of what is tested."""
    pass
```

### Test Class Organization
```python
class TestFeatureName:
    """Test suite for FeatureName."""
    
    def test_basic_case(self):
        """Test basic functionality."""
        pass
    
    def test_edge_case(self):
        """Test edge case."""
        pass
    
    def test_error_handling(self):
        """Test error handling."""
        pass
```

### Using Fixtures
```python
def test_with_database(test_session):
    """Test using database fixture."""
    obj = MyModel(field="value")
    test_session.add(obj)
    test_session.commit()
    
    result = test_session.query(MyModel).first()
    assert result.field == "value"
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_inputs(input, expected):
    """Test with multiple input cases."""
    assert my_function(input) == expected
```

### Testing Exceptions
```python
def test_raises_error():
    """Test that function raises expected error."""
    with pytest.raises(ValueError):
        my_function(invalid_input)

def test_error_message():
    """Test error message content."""
    with pytest.raises(ValueError) as exc_info:
        my_function(invalid_input)
    assert "expected message" in str(exc_info.value)
```

## Fixtures Reference

### Available Fixtures (conftest.py)

#### `temp_dir`
Provides a temporary directory for test files.
```python
def test_with_temp_dir(temp_dir):
    file_path = temp_dir / "test.txt"
    file_path.write_text("content")
    assert file_path.exists()
```

#### `sample_python_file`
Provides a sample Python file for testing AST parsing.
```python
def test_parse_file(sample_python_file):
    result = show_fns(sample_python_file)
    assert len(result['functions']) > 0
```

#### `in_memory_db`
Provides an in-memory database with tables created.
```python
def test_with_db(in_memory_db):
    obj = MyModel(field="value")
    in_memory_db.add(obj)
    in_memory_db.commit()
```

#### `test_engine`
Provides a SQLAlchemy engine for testing.
```python
def test_with_engine(test_engine):
    # Use engine for operations
    pass
```

#### `test_session`
Provides a SQLAlchemy session for testing.
```python
def test_with_session(test_session):
    obj = MyModel(field="value")
    test_session.add(obj)
    test_session.commit()
```

## Best Practices

### 1. Test Independence
Each test should be independent and not rely on other tests.

```python
# Good
def test_create_item(test_session):
    item = MyModel(name="test")
    test_session.add(item)
    test_session.commit()
    assert item.id is not None

# Bad - depends on previous test
def test_update_item(test_session):
    item = test_session.query(MyModel).first()  # Assumes item exists
    item.name = "updated"
```

### 2. Clear Assertions
Use specific assertions that clearly indicate what's being tested.

```python
# Good
assert user.name == "John"
assert len(items) == 3
assert result is not None

# Less clear
assert user
assert items
assert result
```

### 3. Descriptive Test Names
Test names should describe what they test.

```python
# Good
def test_str2_converts_none_to_empty_string():
    assert str2(None) == ""

# Less descriptive
def test_str2():
    assert str2(None) == ""
```

### 4. One Concept Per Test
Each test should verify one specific behavior.

```python
# Good - focused test
def test_user_creation():
    user = User(name="John")
    assert user.name == "John"

def test_user_validation():
    with pytest.raises(ValueError):
        User(name="")

# Bad - testing multiple concepts
def test_user():
    user = User(name="John")
    assert user.name == "John"
    user.name = ""
    with pytest.raises(ValueError):
        user.validate()
```

### 5. Use Fixtures for Setup
Extract common setup into fixtures.

```python
# Good
@pytest.fixture
def user():
    return User(name="John", email="john@example.com")

def test_user_name(user):
    assert user.name == "John"

def test_user_email(user):
    assert user.email == "john@example.com"

# Less maintainable
def test_user_name():
    user = User(name="John", email="john@example.com")
    assert user.name == "John"

def test_user_email():
    user = User(name="John", email="john@example.com")
    assert user.email == "john@example.com"
```

## Continuous Integration

### GitHub Actions
Tests run automatically on push and pull requests. See `.github/workflows/tests.yml`.

### Local Pre-commit Checks
Before committing, run:
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=calvincTools --cov-report=term-missing

# Run linting (if configured)
flake8 calvincTools tests
black --check calvincTools tests
mypy calvincTools
```

## Troubleshooting

### Import Errors
```bash
# Install package in development mode
pip install -e .
```

### Fixture Not Found
Ensure `conftest.py` is in the tests directory and pytest can discover it.

### Database Errors
Tests use in-memory databases. If you encounter errors:
1. Check that fixtures are used correctly
2. Ensure test isolation (each test gets fresh database)
3. Verify that test_session fixture is being used

### Slow Tests
Mark slow tests appropriately:
```python
@pytest.mark.slow
def test_slow_operation():
    # Long-running test
    pass
```

Run without slow tests:
```bash
pytest -m "not slow"
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
