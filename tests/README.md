# calvincTools Test Suite

This directory contains the comprehensive test suite for the calvincTools package.

## Test Structure

```
tests/
├── conftest.py                  # Pytest configuration and shared fixtures
├── test_calvincTools.py         # Main package tests
├── test_package.py              # Package initialization and metadata tests
├── test_utils_strings.py        # Tests for string utilities
├── test_utils_calvindate.py     # Tests for date utilities
├── test_utils_misctools.py      # Tests for miscellaneous tools
├── test_models.py               # Tests for database models
└── test_integration.py          # Integration tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=calvincTools --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_utils_strings.py
```

### Run specific test class
```bash
pytest tests/test_utils_strings.py::TestStr2
```

### Run specific test
```bash
pytest tests/test_utils_strings.py::TestStr2::test_str2_with_string
```

### Run tests with verbose output
```bash
pytest -v
```

### Run only fast tests (skip slow tests)
```bash
pytest -m "not slow"
```

### Run only integration tests
```bash
pytest -m integration
```

### Run only unit tests
```bash
pytest -m unit
```

## Test Coverage

The test suite aims for comprehensive coverage of:

1. **String Utilities** (`calvincTools.utils.strings`)
   - `str2()` - String conversion with custom transforms
   - `WrapInQuotes()` - Quote wrapping
   - `UnWrapQuotes()` - Quote unwrapping
   - `IsWrappedInQuotes()` - Quote detection

2. **Date Utilities** (`calvincTools.utils.calvindate`)
   - `calvindate` class - Enhanced datetime with multiple construction formats
   - Date arithmetic methods (`daysfrom`, `tomorrow`, `yesterday`)
   - Workday calculation (`nextWorkdayAfter`)
   - `IsDateString()` - Date string validation

3. **Miscellaneous Tools** (`calvincTools.utils.misctools`)
   - `show_fns()` - Python file AST analysis
   - `pretty_show_fns()` - Formatted function/class display

4. **Database Models** (`calvincTools.models`)
   - `cMenuBase` - Base model with setValue/getValue
   - `menuGroups` - Menu group management
   - `menuItems` - Menu item management with foreign keys
   - `cParameters` - System parameters storage
   - `cGreetings` - Greetings storage

5. **Integration Tests**
   - Cross-module functionality
   - End-to-end workflows
   - Real-world usage scenarios

## Fixtures

The test suite provides several fixtures in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `sample_python_file` - Sample Python file for AST testing
- `in_memory_db` - In-memory SQLite database
- `sample_menu_data` - Sample data for menu testing
- `test_engine` - SQLAlchemy test engine
- `test_session` - SQLAlchemy test session

## Writing New Tests

### Unit Test Example
```python
def test_my_feature():
    """Test description."""
    result = my_function("input")
    assert result == "expected"
```

### Integration Test Example
```python
@pytest.mark.integration
def test_workflow(test_session):
    """Test complete workflow."""
    # Setup
    obj = MyModel(field="value")
    test_session.add(obj)
    test_session.commit()
    
    # Test
    result = test_session.query(MyModel).first()
    assert result.field == "value"
```

### Parametrized Test Example
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_multiple_cases(input, expected):
    """Test multiple cases."""
    assert my_function(input) == expected
```

## Test Markers

- `@pytest.mark.slow` - For tests that take significant time
- `@pytest.mark.integration` - For integration tests
- `@pytest.mark.unit` - For unit tests

## Dependencies

Required testing packages (install with `pip install -e ".[dev]"`):
- pytest >= 7.0
- pytest-cov >= 3.0
- black >= 22.0
- flake8 >= 4.0
- mypy >= 0.950

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
# Open htmlcov/index.html in your browser
```

## Continuous Integration

Tests should pass in CI/CD pipelines. Ensure all tests pass before committing:
```bash
pytest --cov=calvincTools --cov-report=term-missing
```

## Troubleshooting

### Import errors
If you get import errors, ensure the package is installed in development mode:
```bash
pip install -e .
```

### Database errors in tests
Tests use in-memory SQLite databases that are created fresh for each test. If you encounter database errors, ensure your test is using the provided fixtures.

### Fixture not found
Make sure `conftest.py` is in the tests directory and pytest can discover it.

## Best Practices

1. **One test, one assertion** - Each test should verify one specific behavior
2. **Descriptive names** - Test names should describe what they test
3. **Use fixtures** - Leverage fixtures for common setup
4. **Clean up** - Tests should not leave side effects
5. **Independent tests** - Tests should not depend on each other
6. **Fast tests** - Keep tests fast; mark slow tests appropriately
