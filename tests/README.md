# FastAPI Backend Tests

This directory contains comprehensive tests for the FastAPI backend using the AAA (Arrange-Act-Assert) testing pattern.

## Test Structure

### `conftest.py`
- Shared fixtures for TestClient and sample data
- Reusable test setup across all test files

### `test_api.py`
- API endpoint tests (GET, POST, DELETE operations)
- Error handling and edge cases
- HTTP status code validation

### `test_data.py`
- Data validation and business logic tests
- Structure and integrity checks
- Format validation

### `test_integration.py`
- End-to-end workflow tests
- Complete user journey validation
- Cross-operation testing

## AAA Testing Pattern

All tests follow the **Arrange-Act-Assert** pattern:

```python
def test_example(self, client):
    # Arrange - Set up test preconditions
    test_data = setup_test_data()

    # Act - Execute the operation being tested
    response = client.post("/endpoint", json=test_data)

    # Assert - Verify expected outcomes
    assert response.status_code == 200
    assert response.json()["expected_field"] == "expected_value"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestActivitiesAPI::test_get_activities_success

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

## Test Coverage

The test suite covers:
- ✅ API endpoints (GET, POST, DELETE)
- ✅ Error handling (404, 400 responses)
- ✅ Data validation and integrity
- ✅ Business logic constraints
- ✅ End-to-end workflows
- ✅ Edge cases and boundary conditions

## Adding New Tests

1. Choose the appropriate test file based on the test focus:
   - `test_api.py` for API endpoint testing
   - `test_data.py` for data validation
   - `test_integration.py` for workflows

2. Follow the AAA pattern in each test method

3. Use descriptive test method names: `test_<operation>_<scenario>_<expected_result>`

4. Add docstrings explaining what each test validates

## Dependencies

- `pytest` - Test framework
- `fastapi` - Web framework
- `httpx` - HTTP client for testing

Install test dependencies:
```bash
pip install pytest httpx
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide fast feedback on code changes.