# Testing Guide

## Overview

The Arteterapia application uses pytest for testing with a focus on API endpoint testing. Tests use session-scoped fixtures and optimized database handling for fast execution.

## Quick Start

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Specific test file
pytest tests/api/test_auth.py

# Specific test class
pytest tests/api/test_workshops.py::TestWorkshopCreate

# Specific test
pytest tests/api/test_auth.py::TestAuthLogin::test_login_success

# With coverage
pytest --cov=app --cov-report=html
```

## Test Organization

```
tests/
├── conftest.py              # Fixtures and configuration
├── models/                  # Model unit tests
│   ├── test_user.py        # User model tests
│   ├── test_role.py        # Role model tests
│   ├── test_workshop.py    # Workshop model tests
│   ├── test_participant.py # Participant model tests
│   ├── test_session.py     # Session model tests
│   ├── test_observation.py # ObservationalRecord model tests
│   └── test_user_invitation.py # UserInvitation model tests
├── api/                     # API endpoint tests
│   ├── test_auth.py        # Authentication API tests
│   ├── test_workshops.py   # Workshop API tests
│   └── test_participants.py # Participant API tests
├── routes/                  # Web route tests
│   ├── test_auth_routes.py        # Authentication route tests
│   ├── test_workshop_routes.py    # Workshop route tests
│   ├── test_participant_routes.py # Participant route tests
│   ├── test_session_routes.py     # Session route tests
│   └── test_observation_routes.py # Observation route tests
└── __init__.py
```

## Available Fixtures

### Application Fixtures
- `app` - Flask application instance
- `client` -Test client for requests
- `_db` - Database with test data

### Authentication Fixtures
- `admin_token` - JWT token for admin user
- `editor_token` - JWT token for editor user
- `admin_headers` - Authorization headers for admin
- `editor_headers` - Authorization headers for editor

### Test Data Fixtures
- `sample_workshop` - Pre-created workshop (returns ID)
- `sample_participant` - Pre-created participant (returns ID)
- `sample_session` - Pre-created session (returns ID)
- `sample_observation` - Pre-created observation (returns ID)

**Important**: Fixtures return IDs, not objects. Query objects when needed:
```python
def test_example(db, sample_workshop):
    workshop = Workshop.query.get(sample_workshop)  # Query object from ID
    assert workshop.name == 'Test Workshop'
```

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

## Writing Tests

### Example Test Structure

```python
import pytest

class TestMyFeature:
    """Tests for my feature."""
    
    def test_success_case(self, client, admin_headers):
        """Test successful operation."""
        response = client.get('/api/v1/endpoint', headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'expected_field' in data
    
    def test_error_case(self, client):
        """Test error handling."""
        response = client.get('/api/v1/endpoint')
        assert response.status_code == 401
```

### Testing Patterns

**Authentication Required:**
```python
def test_requires_auth(self, client):
    response = client.get('/api/v1/protected')
    assert response.status_code == 401
```

**Admin Only:**
```python
def test_admin_only(self, client, editor_headers):
    response = client.get('/api/v1/admin-endpoint', headers=editor_headers)
    assert response.status_code == 403
```

**CRUD Operations:**
```python
def test_create_resource(self, client, admin_headers):
    data = {'name': 'Test'}
    response = client.post('/api/v1/resources', 
                          json=data, 
                          headers=admin_headers)
    assert response.status_code == 201
    assert response.get_json()['name'] == 'Test'
```

## Performance Optimization

### Session-Scoped Fixtures

The test suite uses session-scoped database fixtures for optimal performance:

**Benefits:**
- Database created once per test session
- Cached JWT tokens (no repeated generation)
- Table truncation instead of full reset
- ~70% faster execution

**Implementation:**
```python
@pytest.fixture(scope='session')
def app():
    """Create application for testing session."""
    # App created once
    
@pytest.fixture(scope='session')
def _db(app):
    """Create database for testing session."""
    # Database created once
    
@pytest.fixture(scope='function', autouse=True)
def reset_db(_db):
    """Reset database state between tests."""
    # Truncate tables (fast)
```

### Test Isolation

Tests are isolated using table truncation:
- Preserves schema and roles
- Faster than full database drops
- Maintains foreign key relationships
- Automatic cleanup between tests

## Coverage

Generate coverage reports:
```bash
# HTML report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser

# Terminal report
pytest --cov=app --cov-report=term

# Missing lines report
pytest --cov=app --cov-report=term-missing
```

**Coverage Goals:**
- Overall: >80%
- Critical paths (auth, CRUD): >90%
- Models: >85%

## Continuous Integration

Add to CI/CD pipeline:

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
      - run: pytest --cov=app
```

## Common Patterns

### Testing JSON Responses
```python
def test_json_response(self, client, admin_headers):
    response = client.get('/api/v1/resource', headers=admin_headers)
    data = response.get_json()
    assert data['key'] == 'value'
```

### Testing Validation
```python
def test_missing_field(self, client, admin_headers):
    response = client.post('/api/v1/resource',
                          json={},
                          headers=admin_headers)
    assert response.status_code == 400
    assert 'error' in response.get_json()
```

### Testing Permissions
```python
def test_owner_only(self, client, editor_token):
    # Editor creates workshop
    workshop = create_workshop(client, editor_token)
    
    # Admin should not access
    response = client.get(f'/api/v1/workshops/{workshop["id"]}',
                         headers={'Authorization': f'Bearer {admin_token}'})
    # Depends on permission model
```

## Debugging Tests

### Run specific test with output
```bash
pytest tests/api/test_auth.py::test_login -v -s
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Show print statements
```bash
pytest -s
```

```

## Model Testing

### Overview

Model tests verify the core business logic, relationships, and data integrity of SQLAlchemy models. Located in `tests/models/`, these tests cover:

- Model creation and validation
- Computed properties and methods
- Relationships (one-to-many, many-to-many)
- Cascade deletes
- JSON field storage
- Token generation and validation
- Password hashing and verification
- Serialization (to_dict methods)

### Running Model Tests

```bash
# Run all model tests
pytest tests/models/

# Run specific model
pytest tests/models/test_user.py
pytest tests/models/test_workshop.py

# Run specific test class
pytest tests/models/test_user.py::TestUserPassword

# Run specific test
pytest tests/models/test_user.py::TestUserPassword::test_set_password

# With verbose output
pytest tests/models/ -v

# Stop on first failure (recommended for debugging)
pytest tests/models/ -x
```

### Model Test Coverage

| Model | Test File | Tests | Coverage |
|-------|-----------|-------|----------|
| User | `test_user.py` | 38 | Password hashing, email verification, password reset, roles, relationships |
| Role | `test_role.py` | 6 | CRUD operations, relationships |
| Workshop | `test_workshop.py` | 17 | Properties, relationships, cascade deletes |
| Participant | `test_participant.py` | 12 | JSON extra_data, relationships |
| Session | `test_session.py` | 20 | Properties, observation tracking methods |
| ObservationalRecord | `test_observation.py` | 27 | JSON answers, versioning system |
| UserInvitation | `test_user_invitation.py` | 22 | Token generation, expiry, validation |

**Total: 142 test cases**

### Writing Model Tests

**Basic Pattern:**
```python
import pytest
from app.models.workshop import Workshop

class TestWorkshopModel:
    """Tests for Workshop model basic functionality."""
    
    def test_create_workshop(self, db, admin_user):
        """Test creating a new workshop."""
        workshop = Workshop(
            name='Test Workshop',
            objective='Test objective',
            user_id=admin_user.id
        )
        db.session.add(workshop)
        db.session.commit()
        
        assert workshop.id is not None
        assert workshop.name == 'Test Workshop'
        assert workshop.user_id == admin_user.id
```

**Testing Relationships:**
```python
def test_workshop_owner_relationship(self, db, sample_workshop, admin_user):
    """Test workshop-owner relationship."""
    workshop = Workshop.query.get(sample_workshop)  # Query from ID
    assert workshop.owner == admin_user
```

**Testing Cascade Deletes:**
```python
def test_delete_workshop_cascades_to_participants(self, db, sample_workshop, sample_participant):
    """Test that deleting workshop deletes participants."""
    workshop = Workshop.query.get(sample_workshop)
    workshop_id = workshop.id
    participant_id = sample_participant
    
    db.session.delete(workshop)
    db.session.commit()
    
    assert Workshop.query.get(workshop_id) is None
    assert Participant.query.get(participant_id) is None
```

**Testing JSON Fields:**
```python
def test_participant_with_extra_data(self, db, sample_workshop):
    """Test creating participant with extra data."""
    extra = {'age': 25, 'notes': 'Test notes'}
    participant = Participant(
        name='Test Participant',
        workshop_id=sample_workshop,
        extra_data=extra
    )
    db.session.add(participant)
    db.session.commit()
    
    assert participant.extra_data == extra
    assert participant.extra_data['age'] == 25
```

**Testing Methods:**
```python
def test_user_check_password(self, db, admin_user):
    """Test password verification."""
    assert admin_user.check_password('admin123') is True
    assert admin_user.check_password('wrongpassword') is False
```

**Testing Computed Properties:**
```python
def test_workshop_participant_count(self, db, sample_workshop):
    """Test participant count property."""
    workshop = Workshop.query.get(sample_workshop)
    initial_count = workshop.participant_count
    
    # Add participant
    p = Participant(name='New Participant', workshop_id=workshop.id)
    db.session.add(p)
    db.session.commit()
    
    assert workshop.participant_count == initial_count + 1
```

### Skipped Tests (SQLite Limitations)

Some tests are skipped because SQLite doesn't enforce foreign key constraints in the test environment:

```python
@pytest.mark.skip(reason="SQLite doesn't enforce foreign key constraints in test environment")
def test_participant_invalid_workshop_id(self, db):
    """Test that participant requires valid workshop_id."""
    participant = Participant(name='Test', workshop_id=99999)
    db.session.add(participant)
    
    with pytest.raises(Exception):  # Would raise IntegrityError in PostgreSQL
        db.session.commit()
```

**Skipped tests:**
- `test_participant_invalid_workshop_id`
- `test_session_invalid_workshop_id`
- `test_observation_invalid_session_id`
- `test_observation_invalid_participant_id`
- `test_observation_requires_answers`
- `test_invitation_invalid_creator_id`

These constraints are enforced in production (PostgreSQL/MySQL).

### Common Model Testing Patterns

**Testing Unique Constraints:**
```python
def test_unique_username_constraint(self, db, admin_user):
    """Test that usernames must be unique."""
    user = User(
        username=admin_user.username,  # Duplicate
        email='different@example.com'
    )
    user.set_password('password')
    db.session.add(user)
    
    with pytest.raises(Exception):  # IntegrityError
        db.session.commit()
```

**Testing Token Generation:**
```python
def test_generate_verification_token(self, db, admin_user):
    """Test generating email verification token."""
    token = admin_user.generate_verification_token()
    
    assert token is not None
    assert len(token) > 20
    assert admin_user.verification_token == token
```

**Testing Serialization:**
```python
def test_to_dict_basic(self, db, admin_user):
    """Test converting user to dictionary."""
    data = admin_user.to_dict()
    
    assert data['id'] == admin_user.id
    assert data['username'] == admin_user.username
    assert 'password_hash' not in data  # Sensitive fields excluded
```

### Model Testing Best Practices

1. **Test one thing per test**: Focus on single behavior
2. **Use descriptive names**: `test_delete_workshop_cascades_to_participants`
3. **Query objects from fixture IDs**: `Workshop.query.get(sample_workshop)`
4. **Test both success and failure cases**: Valid and invalid data
5. **Verify database state**: Check that changes persisted
6. **Test edge cases**: Empty strings, null values, boundary conditions
7. **Document complex tests**: Use docstrings to explain what's being tested
8. **Group related tests**: Use test classes to organize

### Model Testing Checklist

When creating/modifying models, ensure tests cover:

- [ ] Model creation with required fields
- [ ] Model creation with optional fields
- [ ] Unique constraints
- [ ] Required field validation
- [ ] Computed properties
- [ ] Instance methods
- [ ] Static/class methods
- [ ] Relationships (forward and reverse)
- [ ] Cascade deletes
- [ ] JSON field storage and retrieval
- [ ] Serialization (to_dict)
- [ ] String representation (__repr__)

### Stop on first failure
```bash
pytest -x


## Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** (`test_user_cannot_delete_others_workshop`)
3. **Use fixtures** for setup/teardown
4. **Test edge cases** (empty strings, null values, max lengths)
5. **Test error paths** (not just happy paths)
6. **Avoid test interdependencies** (tests should run in any order)
7. **Use clear assertions** (`assert x == y`, not `assert x`)
8. **Document complex tests** with docstrings

## Performance Tips

- Use session-scoped fixtures for expensive operations
- Minimize database writes in tests
- Reuse test data when possible
- Avoid unnecessary API calls
- Use table truncation instead of full resets

## Troubleshooting

**Database locked error:**
- Ensure no Flask instances running
- Close database browser tools
- Check file permissions

**Import errors:**
- Verify virtual environment activated
- Install test dependencies: `pip install -r requirements.txt`

**Fixture not found:**
- Check `conftest.py` location
- Verify fixture scope
- Import needed fixtures

## Dynamic Testing Workflow

### Recommended Development Process

When creating or debugging tests, follow this efficient workflow:

1. **Run with Stop-on-Failure** (`-x` flag):
   ```bash
   pytest tests/routes/test_auth_routes.py -x -v --tb=short
   ```
   This stops at the first failure, allowing you to focus on one issue at a time.

2. **Identify the Failing Test**:
   - Read the error message carefully
   - Note the test name and line number
   - Check the assertion that failed

3. **Run Only the Failing Test**:
   ```bash
   pytest tests/routes/test_auth_routes.py::TestClass::test_method -vv --tb=long
   ```
   This provides detailed output for debugging.

4. **Fix the Issue**:
   - Update test code or application code as needed
   - Verify the fix addresses the root cause

5. **Verify the Fix**:
   ```bash
   pytest tests/routes/test_auth_routes.py::TestClass::test_method -vv
   ```
   Ensure the specific test now passes.

6. **Run Full Suite**:
   ```bash
   pytest tests/routes/test_auth_routes.py -v
   ```
   Only run the full suite after individual tests pass.

### Benefits of This Approach
- **Faster feedback**: Focus on one issue at a time
- **Clearer debugging**: Detailed output for specific test
- **Reduced noise**: Avoid overwhelming error messages
- **Efficient workflow**: Fix → Verify → Continue

## Common Testing Pitfalls

### 1. Database Session Issues

**Problem**: Objects become detached from session
```python
# ❌ Wrong - object queried in app context that exits
@pytest.fixture
def admin_user(app, db):
    with app.app_context():
        return User.query.filter_by(username='admin').first()  # Detached!

# ✅ Correct - object remains in session
@pytest.fixture
def admin_user(app, db):
    return User.query.filter_by(username='admin').first()  # Session maintained by db fixture
```

**Solution**: Let the `db` fixture manage the app context. Don't create nested contexts.

### 2. Timezone-Naive vs Timezone-Aware Datetimes

**Problem**: SQLite doesn't store timezone information
```python
# ❌ Wrong - comparison fails
if datetime.now(timezone.utc) > self.reset_token_expiry:  # May be naive from DB

# ✅ Correct - make naive datetime aware
expiry = self.reset_token_expiry.replace(tzinfo=timezone.utc) if self.reset_token_expiry.tzinfo is None else self.reset_token_expiry
if datetime.now(timezone.utc) > expiry:
```

**Solution**: Always handle timezone awareness when comparing datetimes loaded from SQLite.

### 3. UNIQUE Constraint Violations

**Problem**: Trying to create data that already exists
```python
# ❌ Wrong - fails if role exists
admin_role = Role(name='admin', description='Administrator')
db.session.add(admin_role)

# ✅ Correct - check existence first
admin_role = Role.query.filter_by(name='admin').first()
if not admin_role:
    admin_role = Role(name='admin', description='Administrator')
    db.session.add(admin_role)
```

**Solution**: Always check if data exists before creating, especially in session-scoped fixtures.

### 4. Database Configuration in Tests

**Problem**: Tests use production database instead of test database
```python
# ❌ Wrong - config set after app creation
app = create_app('default')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Too late!

# ✅ Correct - set environment variable before app creation
import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
app = create_app('default')
```

**Solution**: Set database configuration via environment variables before creating the app.

### 5. Token Generation Methods

**Problem**: Calling non-existent service methods
```python
# ❌ Wrong - method doesn't exist
token = AuthService.generate_email_verification_token(user.email)

# ✅ Correct - use User model method
token = user.generate_verification_token()
```

**Solution**: Check the actual implementation. Token generation is typically on the User model, not in services.

### 6. Missing Database Commits

**Problem**: Changes not persisted to database
```python
# ❌ Wrong - token generated but not saved
token = admin_user.generate_reset_token()
# Token exists on object but not in DB!

# ✅ Correct - commit after generation
token = admin_user.generate_reset_token()
db.session.commit()
```

**Solution**: Always commit after modifying database objects, especially in tests.

### 7. URL Prefix Confusion

**Problem**: Incorrect route paths in tests
```python
# ❌ Wrong - assuming blueprint has URL prefix
response = client.post('/auth/login', data={...})  # 404 if no prefix!

# ✅ Correct - check actual blueprint registration
response = client.post('/login', data={...})  # Matches actual route
```

**Solution**: Check `app/__init__.py` to see how blueprints are registered (with or without URL prefix).

## Code-to-Test Mapping

### Maintaining Test Coverage

When modifying application code, update corresponding tests. This table maps all application components to their test files:

#### Route Tests (Web Interface)

| Application File | Test File | Relationship |
|-----------------|-----------|--------------|
| `app/routes/auth.py` | `tests/routes/test_auth_routes.py` | 1:1 - Each route function should have multiple tests |
| `app/routes/workshop.py` | `tests/routes/test_workshop_routes.py` | 1:1 - Test all CRUD operations |
| `app/routes/participant.py` | `tests/routes/test_participant_routes.py` | 1:1 - Test all AJAX endpoints |
| `app/routes/session.py` | `tests/routes/test_session_routes.py` | 1:1 - Test all AJAX endpoints |
| `app/routes/observation.py` | `tests/routes/test_observation_routes.py` | 1:1 - Test workflow steps |

#### API Tests (REST Endpoints)

| Application File | Test File | Relationship |
|-----------------|-----------|--------------|
| `app/routes/auth.py` (API endpoints) | `tests/api/test_auth.py` | 1:1 - Test JWT authentication, token refresh, etc. |
| `app/routes/workshop.py` (API endpoints) | `tests/api/test_workshops.py` | 1:1 - Test workshop API CRUD operations |
| `app/routes/participant.py` (API endpoints) | `tests/api/test_participants.py` | 1:1 - Test participant API CRUD operations |

#### Service Tests (Business Logic)

| Application File | Test File | Relationship |
|-----------------|-----------|--------------|
| `app/services/auth_service.py` | `tests/services/test_auth_service.py` | 1:1 - Test authentication business logic |
| `app/services/workshop_service.py` | `tests/services/test_workshop_service.py` | 1:1 - Test workshop business logic |
| `app/services/session_service.py` | `tests/services/test_session_service.py` | 1:1 - Test session business logic |
| `app/services/observation_service.py` | `tests/services/test_observation_service.py` | 1:1 - Test observation business logic |
| `app/services/participant_service.py` | Tested via route/API tests | Indirect - Service tested through routes |

#### Model Tests (Database Layer)

| Application File | Test File | Relationship |
|-----------------|-----------|--------------|
| `app/models/user.py` | `tests/models/test_user.py` | 1:1 - Comprehensive unit tests for User model |
| `app/models/role.py` | `tests/models/test_role.py` | 1:1 - Unit tests for Role model |
| `app/models/workshop.py` | `tests/models/test_workshop.py` | 1:1 - Unit tests for Workshop model |
| `app/models/participant.py` | `tests/models/test_participant.py` | 1:1 - Unit tests for Participant model |
| `app/models/session.py` | `tests/models/test_session.py` | 1:1 - Unit tests for Session model |
| `app/models/observation.py` | `tests/models/test_observation.py` | 1:1 - Unit tests for ObservationalRecord model |
| `app/models/user_invitation.py` | `tests/models/test_user_invitation.py` | 1:1 - Unit tests for UserInvitation model |
| `app/models/observation_questions.py` | Validated via `test_observation.py` | Indirect - Question structure validated through observations |

**Note**: Models are also tested indirectly through route and API tests, but dedicated model tests provide focused unit testing of model logic, relationships, and constraints.

#### Infrastructure Tests

| Test File | Purpose |
|-----------|---------|
| `tests/test_basic_setup.py` | Basic application setup and configuration tests |
| `tests/conftest.py` | Test fixtures and configuration (not a test file itself) |

### When to Update Tests

**Add new tests when:**
- Adding a new route or endpoint
- Adding new validation rules
- Adding new permission checks
- Changing authentication requirements
- Modifying response formats

**Update existing tests when:**
- Changing route URLs or HTTP methods
- Modifying validation logic
- Changing error messages
- Updating response structure
- Changing permission requirements

**Don't update tests when:**
- Refactoring internal implementation (if behavior unchanged)
- Changing variable names (if interface unchanged)
- Optimizing queries (if results unchanged)

## Test Fixtures Reference

### Session-Scoped Fixtures (Created Once)
- `app`: Flask application with test configuration
- `_db`: Database with tables and base test users
- `admin_token`: JWT token for admin user (API tests)
- `editor_token`: JWT token for editor user (API tests)

### Function-Scoped Fixtures (Created Per Test)
- `db`: Database with table truncation for isolation
- `client`: Flask test client
- `admin_user`: Admin user instance
- `editor_user`: Editor user instance
- `sample_workshop`: Test workshop
- `sample_participant`: Test participant
- `sample_session`: Test session
- `sample_observation`: Test observation record

### Fixture Dependencies
```
app (session)
  └── _db (session)
        └── db (function)
              ├── admin_user (function)
              ├── editor_user (function)
              ├── sample_workshop (function)
              │     ├── sample_participant (function)
              │     └── sample_session (function)
              │           └── sample_observation (function)
              └── client (function)
```

## Critical Testing Knowledge

### Database Isolation Strategy

The test suite uses **table truncation** instead of full database recreation:

1. **Session Setup**: Create tables and base users once
2. **Test Setup**: Truncate tables (except users/roles) before each test
3. **Test Execution**: Test runs with clean slate
4. **Test Teardown**: Automatic via fixture cleanup
5. **Session Teardown**: Drop all tables after all tests

**Benefits:**
- Fast execution (~2.7s per test average)
- True isolation between tests
- Preserves base users for authentication
- No database recreation overhead

### Authentication in Tests

**Web Routes (Cookie-based):**
```python
# Login via form
client.post('/login', data={
    'username': 'admin',
    'password': 'admin123'
})
# Subsequent requests are authenticated via session cookie
```

**API Routes (Token-based):**
```python
# Use pre-generated token
headers = {'Authorization': f'Bearer {admin_token}'}
client.get('/api/v1/workshops', headers=headers)
```

### Test Naming Conventions

Follow this pattern for clarity:
```python
def test_<action>_<condition>_<expected_result>

# Examples:
def test_login_invalid_credentials_returns_error
def test_create_workshop_without_auth_redirects_to_login
def test_delete_participant_not_owner_permission_denied
```

### Assertion Best Practices

**Be specific:**
```python
# ❌ Vague
assert response.status_code != 500

# ✅ Specific
assert response.status_code == 200
```

**Check multiple aspects:**
```python
# ✅ Comprehensive
assert response.status_code == 200
data = response.get_json()
assert data['success'] is True
assert 'workshop' in data
assert data['workshop']['name'] == 'Test Workshop'

# Verify database state
workshop = Workshop.query.filter_by(name='Test Workshop').first()
assert workshop is not None
assert workshop.user_id == admin_user.id
```

### Error Debugging Tips

**1. Read the full traceback** - The error often occurs before the assertion
**2. Check fixture setup** - Many errors happen during fixture creation
**3. Verify database state** - Use `db.session.query()` to inspect
**4. Check app context** - Some operations require active app context
**5. Validate test data** - Ensure fixtures create valid data

For more information, see:
- Route tests: `tests/routes/`
- API tests: `tests/api/`
- Test fixtures: `tests/conftest.py`
- Routes reference: `.agent/topics/routes.md`
