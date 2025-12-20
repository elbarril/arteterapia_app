# Application Routes Reference

## Overview
This document provides a comprehensive reference of all application routes, their purposes, authentication requirements, and HTTP methods.

## Route Organization

Routes are organized into blueprints by functional area:
- **Auth Blueprint** (`auth_bp`): Authentication and user management
- **Workshop Blueprint** (`workshop_bp`): Workshop management
- **Participant Routes**: Participant management within workshops
- **Session Routes**: Session management within workshops
- **Observation Routes**: Observation workflow

## Authentication Routes (`app/routes/auth.py`)

### Login
- **URL**: `/login`
- **Methods**: `GET`, `POST`
- **Auth Required**: No
- **Purpose**: User authentication
- **Redirects**: 
  - Authenticated users → `/` (workshop list)
  - Successful login → `/` or `next` parameter
  - Users requiring password change → `/change-password`

### Logout
- **URL**: `/logout`
- **Methods**: `GET`
- **Auth Required**: Yes
- **Purpose**: End user session
- **Redirects**: `/login`

### Registration
- **URL**: `/register/<token>`
- **Methods**: `GET`, `POST`
- **Auth Required**: No
- **Purpose**: New user registration via invitation token
- **Validation**: 
  - Token must be valid and not expired
  - Username must be unique
  - Passwords must match
- **Redirects**: `/login` on success

### Email Verification
- **URL**: `/verify-email/<token>`
- **Methods**: `GET`
- **Auth Required**: No
- **Purpose**: Verify user email address
- **Redirects**: `/login`

### Forgot Password
- **URL**: `/forgot-password`
- **Methods**: `GET`, `POST`
- **Auth Required**: No
- **Purpose**: Request password reset
- **Security**: Prevents email enumeration
- **Redirects**: `/login` after submission

### Reset Password
- **URL**: `/reset-password/<token>`
- **Methods**: `GET`, `POST`
- **Auth Required**: No
- **Purpose**: Reset password with token
- **Validation**: 
  - Token must be valid and not expired
  - Passwords must match
- **Redirects**: 
  - Invalid token → `/forgot-password`
  - Success → `/login`

### Change Password
- **URL**: `/change-password`
- **Methods**: `GET`, `POST`
- **Auth Required**: Yes
- **Purpose**: Change password for authenticated user
- **Validation**: 
  - Current password must be correct
  - New passwords must match
- **Redirects**: `/` on success

## Workshop Routes (`app/routes/workshop.py`)

### List Workshops
- **URL**: `/`
- **Methods**: `GET`
- **Auth Required**: Yes
- **Purpose**: Display all workshops
- **Permissions**: 
  - Admins see all workshops
  - Regular users see only their own

### Create Workshop
- **URL**: `/workshop/create`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Create new workshop
- **Validation**: Name is required
- **Redirects**: `/<workshop_id>` on success

### Workshop Detail
- **URL**: `/<workshop_id>`
- **Methods**: `GET`
- **Auth Required**: Yes
- **Purpose**: View workshop details, participants, sessions
- **Permissions**: Owner or admin only
- **Redirects**: `/` if permission denied

### Update Objective
- **URL**: `/<workshop_id>/objective`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Update workshop objective
- **Content-Type**: `application/json`
- **Permissions**: Owner or admin only
- **Response**: JSON with success status

### Delete Workshop
- **URL**: `/<workshop_id>/delete`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Delete workshop
- **Permissions**: Owner or admin only
- **Redirects**: `/` on success

## Participant Routes (`app/routes/participant.py`)

### Create Participant
- **URL**: `/workshop/<workshop_id>/participant/create`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Add participant to workshop
- **Content-Type**: `application/json`
- **Validation**: Name is required
- **Permissions**: Workshop owner or admin
- **Response**: JSON with participant data

### Update Participant
- **URL**: `/participant/<participant_id>/update`
- **Methods**: `POST`, `PUT`
- **Auth Required**: Yes
- **Purpose**: Update participant information
- **Content-Type**: `application/json`
- **Validation**: Name is required
- **Permissions**: Workshop owner or admin
- **Response**: JSON with updated participant data

### Delete Participant
- **URL**: `/participant/<participant_id>/delete`
- **Methods**: `POST`, `DELETE`
- **Auth Required**: Yes
- **Purpose**: Remove participant from workshop
- **Permissions**: Workshop owner or admin
- **Response**: JSON with success status

## Session Routes (`app/routes/session.py`)

### Create Session
- **URL**: `/workshop/<workshop_id>/session/create`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Create new session in workshop
- **Content-Type**: `application/json`
- **Validation**: Prompt is required
- **Permissions**: Workshop owner or admin
- **Response**: JSON with session data

### Update Session
- **URL**: `/session/<session_id>/update`
- **Methods**: `POST`, `PUT`
- **Auth Required**: Yes
- **Purpose**: Update session information
- **Content-Type**: `application/json`
- **Validation**: Prompt is required
- **Permissions**: Workshop owner or admin
- **Response**: JSON with updated session data

### Delete Session
- **URL**: `/session/<session_id>/delete`
- **Methods**: `POST`, `DELETE`
- **Auth Required**: Yes
- **Purpose**: Remove session from workshop
- **Permissions**: Workshop owner or admin
- **Response**: JSON with success status

## Observation Routes (`app/routes/observation.py`)

### Start Observation
- **URL**: `/session/<session_id>/observe/<participant_id>`
- **Methods**: `GET`
- **Auth Required**: Yes
- **Purpose**: Begin observation workflow for participant in session
- **Permissions**: Workshop owner or admin
- **Session Data**: Stores observation state in Flask session
- **Response**: Renders observation form

### Process Answer
- **URL**: `/observation/answer`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Process answer to observation question
- **Content-Type**: `application/json`
- **Session Data**: Requires active observation in Flask session
- **Response**: JSON with next question or completion status

### Complete Observation
- **URL**: `/observation/complete`
- **Methods**: `POST`
- **Auth Required**: Yes
- **Purpose**: Save completed observation to database
- **Content-Type**: `application/json`
- **Session Data**: Requires completed observation in Flask session
- **Response**: JSON with success status and observation ID

### View Observations
- **URL**: `/workshop/<workshop_id>/observations`
- **Methods**: `GET`
- **Auth Required**: Yes
- **Purpose**: View all observations for workshop
- **Permissions**: Workshop owner or admin
- **Response**: Renders observations table

## Route Patterns and Conventions

### URL Structure
- **Resource-based**: URLs represent resources (workshops, participants, sessions)
- **Hierarchical**: Child resources nested under parents (`/workshop/<id>/participant/create`)
- **RESTful**: Uses appropriate HTTP methods (GET, POST, PUT, DELETE)

### Authentication
- All routes except auth routes require `@login_required` decorator
- Permission checks verify ownership or admin status
- Unauthorized access redirects to login or workshop list

### Response Types
- **HTML Routes**: Return rendered templates or redirects
- **AJAX Routes**: Return JSON responses with `success` field
- **Error Handling**: 404 for not found, 403 for forbidden, 400 for validation errors

### Permission Model
- **Admin Users**: Full access to all resources
- **Regular Users**: Access only to their own workshops and related resources
- **Ownership**: Checked via `workshop.user_id == current_user.id`

### Data Flow
1. **Request** → Route handler
2. **Authentication** → `@login_required` decorator
3. **Permission Check** → Verify ownership or admin status
4. **Service Layer** → Business logic in service classes
5. **Database** → Model operations
6. **Response** → Template render or JSON

## Testing Considerations

### Route Testing Requirements
- Test authentication requirement for all protected routes
- Test permission checks for owner-only routes
- Test validation for all input fields
- Test not found scenarios (404)
- Test both success and error paths
- Test all supported HTTP methods

### Test Fixtures Needed
- `client`: Flask test client
- `admin_user`: Admin user for permission testing
- `editor_user`: Regular user for permission testing
- `sample_workshop`: Test workshop data
- `sample_participant`: Test participant data
- `sample_session`: Test session data

### Common Test Patterns
```python
# Authentication test
def test_route_requires_login(client):
    response = client.get('/protected-route', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location

# Permission test
def test_route_permission_denied(client, editor_user, admin_workshop):
    client.post('/login', data={'username': 'editor', 'password': 'editor123'})
    response = client.get(f'/{admin_workshop}', follow_redirects=False)
    assert response.status_code == 302

# Success test
def test_route_success(client, admin_user):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'})
    response = client.get('/route')
    assert response.status_code == 200
```

## Route-to-Test Mapping

| Route File | Test File | Coverage |
|------------|-----------|----------|
| `app/routes/auth.py` | `tests/routes/test_auth_routes.py` | 29 tests |
| `app/routes/workshop.py` | `tests/routes/test_workshop_routes.py` | 16 tests |
| `app/routes/participant.py` | `tests/routes/test_participant_routes.py` | 13 tests |
| `app/routes/session.py` | `tests/routes/test_session_routes.py` | 14 tests |
| `app/routes/observation.py` | `tests/routes/test_observation_routes.py` | 12 tests |

## Security Considerations

### CSRF Protection
- Disabled for AJAX routes (`WTF_CSRF_ENABLED = False` in tests)
- Enabled for form-based routes in production

### SQL Injection Prevention
- All queries use SQLAlchemy ORM
- No raw SQL queries with user input

### XSS Prevention
- Jinja2 auto-escaping enabled
- User input sanitized before rendering

### Authentication Security
- Passwords hashed with bcrypt
- Session cookies are HTTP-only
- Password reset tokens expire after 24 hours
- Email verification tokens expire after 7 days

## Performance Considerations

### Database Queries
- Eager loading for related data (`workshop.participants.all()`)
- Indexed fields: `username`, `email`, `reset_token`
- Session-scoped test fixtures for performance

### Caching
- No caching implemented (future enhancement)
- Consider caching for workshop lists and observations

### Optimization Opportunities
- Pagination for large workshop lists
- Lazy loading for observation data
- Database query optimization with `select_related`
