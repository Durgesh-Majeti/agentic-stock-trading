# Testing Guide

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_validators.py
pytest tests/test_helpers.py
pytest tests/test_database_session.py
pytest tests/test_repositories.py
pytest tests/test_config.py
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Class

```bash
pytest tests/test_validators.py::TestPriceValidation
```

### Run Specific Test Function

```bash
pytest tests/test_validators.py::TestPriceValidation::test_valid_price
```

## Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_validators.py` - Validator function tests
- `tests/test_helpers.py` - Helper function tests
- `tests/test_database_session.py` - Database session tests
- `tests/test_repositories.py` - Repository tests
- `tests/test_config.py` - Configuration tests
- `tests/test_scripts.py` - Script tests

## Test Coverage

Current coverage focuses on Phase 1 components:
- ✅ Validators (100% coverage)
- ✅ Helpers (100% coverage)
- ✅ Database session (basic tests)
- ✅ Repositories (basic tests)
- ✅ Configuration (basic tests)

## Adding New Tests

1. Create test file: `tests/test_<module>.py`
2. Import pytest and required modules
3. Use fixtures from `conftest.py`
4. Follow naming convention: `test_<function_name>`
5. Run tests to verify
