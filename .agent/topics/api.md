# API Development Guide

## Overview

The Arteterapia application provides a RESTful JSON API for external integrations and frontend applications. The API uses JWT authentication and follows RESTful conventions.

**Base URL**: `http://localhost:5000/api/v1`
**Authentication**: JWT Bearer tokens
**Version**: v1

## Authentication

### Login
Get JWT access and refresh tokens.

`POST /api/v1/auth/login`

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@arteterapia.local",
    "roles": ["admin"]
  }
}
```

**Errors:**
- `400`: Missing username/password
- `401`: Invalid credentials
- `403`: Account inactive or email not verified

### Refresh Token
`POST /api/v1/auth/refresh`

**Headers**: `Authorization: Bearer <refresh_token>`

**Response (200):**
```json
{
  "access_token": "eyJhbGci..."
}
```

### Get Current User
`GET /api/v1/auth/me`

**Headers**: `Authorization: Bearer <access_token>`

## Workshops

### List Workshops
`GET /api/v1/workshops`

Returns all workshops. Admins see all workshops, regular users see only their own.

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Workshop de Pintura",
    "objective": "Explorar emociones",
    "user_id": 1,
    "created_at": "2025-12-10T18:47:48",
    "participant_count": 5,
    "session_count": 3
  }
]
```

### Create Workshop
`POST /api/v1/workshops`

**Request:**
```json
{
  "name": "New Workshop",
  "objective": "Optional objective"
}
```

**Response (201):** Workshop object

### Get Workshop Details
`GET /api/v1/workshops/{id}`

Includes participants and sessions.

**Response (200):**
```json
{
  "id": 1,
  "name": "Workshop de Pintura",
  "participants": [...],
  "sessions": [...]
}
```

### Update Workshop
`PATCH /api/v1/workshops/{id}`

**Request (all fields optional):**
```json
{
  "name": "Updated name",
  "objective": "Updated objective"
}
```

### Delete Workshop
`DELETE /api/v1/workshops/{id}`

**Response (200):**
```json
{
  "message": "Workshop deleted successfully"
}
```

## Participants

### List Workshop Participants
`GET /api/v1/participants/workshop/{workshop_id}`

### Create Participant
`POST /api/v1/participants`

**Request:**
```json
{
  "workshop_id": 1,
  "name": "María García",
  "extra_data": {
    "age": 30,
    "notes": "Custom notes"
  }
}
```

### Get Participant
`GET /api/v1/participants/{id}`

### Update Participant
`PATCH /api/v1/participants/{id}`

**Request (all optional):**
```json
{
  "name": "Updated name",
  "extra_data": { ...}
}
```

### Delete Participant
`DELETE /api/v1/participants/{id}`

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error type",
  "message": "Detailed message"
}
```

**Common Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Auth required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: JWT validation error

## CORS Configuration

CORS enabled for all `/api/v1/*` endpoints. Configure in `.env`:

```bash
# Development
CORS_ORIGINS=*

# Production
CORS_ORIGINS=https://yourdomain.com
```

## Testing

Run API tests:
```bash
# All API tests
pytest tests/api/ -v

# Specific test file
pytest tests/api/test_auth.py -v

# With coverage
pytest tests/api/ --cov=app --cov-report=html
```

## Example Workflow

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Create workshop
curl -s -X POST http://localhost:5000/api/v1/workshops \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Workshop"}'

# 3. List workshops
curl -s http://localhost:5000/api/v1/workshops \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Implementation Details

### JWT Configuration

Tokens configured in `config.py`:
- Access token: 15 minute expiry
- Refresh token: 30 day expiry
- Algorithm: HS256

### Security Best Practices

- Always use HTTPS in production
- Implement rate limiting (Flask-Limiter)
- Add Content Security Policy headers
- Validate all input data
- Use environment variables for secrets

### API Versioning

API versioned via URL path (`/api/v1/`). Future versions can coexist:
- `/api/v1/` - Current version
- `/api/v2/` - Future version

## Future Endpoints

Planned for future releases:
- Session management endpoints
- Observation recording endpoints
- Batch operations
- Search and filtering
- Export functionality

For detailed implementation, see `app/api/` directory in the codebase.
