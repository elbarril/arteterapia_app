# Running Tests

## Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/api/test_auth.py

# Run specific test class
pytest tests/api/test_workshops.py::TestWorkshopCreate

# Run specific test
pytest tests/api/test_auth.py::TestAuthLogin::test_login_success_with_username

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## Test Organization

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── api/                     # API endpoint tests
│   ├── test_auth.py        # Authentication API tests
│   └── test_workshops.py   # Workshop API tests
└── __init__.py
```

## Available Fixtures

### Application Fixtures
- `app` - Flask application instance
- `client` - Test client for making requests
- `_db` - Database instance with test data

### Authentication Fixtures
- `admin_token` - JWT token for admin user
- `editor_token` - JWT token for editor user
- `admin_headers` - Authorization headers for admin
- `editor_headers` - Authorization headers for editor

### Test Data Fixtures
- `sample_workshop` - Pre-created workshop
- `sample_participant` - Pre-created participant
- `sample_session` - Pre-created session

## Test Users

**Admin User:**
- Username: `admin`
- Email: `admin@test.com`
- Password: `admin123`
- Roles: `admin`

**Editor User:**
- Username: `editor`
- Email: `editor@test.com`
- Password: `editor123`
- Roles: `editor`

## Writing New Tests

Example test structure:

```python
import pytest

class TestMyFeature:
    """Tests for my feature."""
    
    def test_success_case(self, client, admin_headers):
        """Test successful operation."""
        response = client.get('/api/v1/endpoint', headers=admin_headers)
        assert response.status_code == 200
    
    def test_error_case(self, client):
        """Test error handling."""
        response = client.get('/api/v1/endpoint')
        assert response.status_code == 401
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest
```
