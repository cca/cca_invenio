# InvenioRDM Test Suite

This directory contains tests for the CCA InvenioRDM instance.

## Prerequisites

> [!CAUTION]
> These tests run against the **live development instance**. They are integration tests that interact with the actual database and search indices. Misconfigured tests are likely to leave leftover data.

Using actual tests reflects real-world behavior better, but is slow and can mess up a local instance.

```sh
# to test, the instance & its backing services must be running
docker desktop start
invenio-cli run
```

## Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_cli.py`** - Tests for CLI utilities in `site/cca/scripts/`
- **`test_custom_fields.py`** - Tests for custom fields configuration
- **`test_groups_sync.py`** - Tests for groups synchronization utility (existing)
- **`test_records.py`** - Tests for creating, updating, and managing records
- **`test_search.py`** - Tests for search functionality including filters and pagination
- **`test_views.py`** - Tests for custom views and API endpoints

## Running Tests

**Prerequisites**: InvenioRDM services and application must be running (see above).

```fish
# Activate virtual environment
source .venv/bin/activate.fish
pytest tests/ -v # Run all tests, verbose
pytest tests/test_records.py # Specific test file
pytest tests/ -k "search" # Tests matching a pattern
# Run only unit tests (services not required)
pytest tests/ -m unit
# Run only integration tests (require running services)
pytest tests/ -m integration
# Skip slow tests (e.g., search tests that wait for indexing)
pytest tests/ -m "not slow"
```

## Adding New Tests

When adding new functionality to CCA InvenioRDM:

1. Add corresponding tests to the appropriate test file
2. Use existing fixtures from `conftest.py` when possible
3. Clean up any created resources (records, users, etc.) after tests
4. Use descriptive test names that explain what is being tested
5. Add docstrings to test functions explaining the test purpose

Generally, tests should have a `@pytest.mark` annotation of either `unit` (services not required) or `integration`.

## Alternative: Isolated Unit Tests (Future Work)

To create truly isolated unit tests that don't require services:

1. Install `pytest-invenio` package
2. Configure test database (SQLite)
3. Mock external services
4. Use InvenioRDM's test fixtures

This would require significant refactoring but would allow:

- Tests without running services
- Faster execution
- Isolation from local instance
- CI/CD without full infrastructure

## Additional Notes

- Many tests create and delete records, so they may take time to run due to indexing
- Tests use the `system_identity` to bypass permissions
