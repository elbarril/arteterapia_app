# API Documentation

## Overview

The Arteterapia application provides a RESTful JSON API alongside its traditional web interface. The API uses JWT (JSON Web Tokens) for authentication and follows RESTful conventions.

**Base URL**: `http://localhost:5000/api/v1`

**Version**: v1

**Authentication**: JWT Bearer tokens

---

## Authentication

### Login

Get JWT access and refresh tokens.

**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@arteterapia.local",
    "email_verified": true,
    "active": true,
    "roles": ["admin"],
    "created_at": "2025-12-10T18:47:48.269648"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account not active or email not verified

---

### Refresh Token

Get a new access token using a refresh token.

**Endpoint**: `POST /api/v1/auth/refresh`

**Headers**:
```
Authorization: Bearer <refresh_token>
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Get Current User

Get information about the currently authenticated user.

**Endpoint**: `GET /api/v1/auth/me`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@arteterapia.local",
  "email_verified": true,
  "active": true,
  "roles": ["admin"],
  "created_at": "2025-12-10T18:47:48.269648"
}
```

---

## Workshops

### List Workshops

Get all workshops accessible to the current user.

**Endpoint**: `GET /api/v1/workshops`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Workshop de Pintura",
    "objective": "Explorar emociones a través del color",
    "user_id": 1,
    "created_at": "2025-12-10T18:47:48.269648",
    "participant_count": 5,
    "session_count": 3
  }
]
```

**Permissions**:
- Admins see all workshops
- Regular users see only their own workshops

---

### Create Workshop

Create a new workshop.

**Endpoint**: `POST /api/v1/workshops`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "New Workshop",
  "objective": "Workshop objective (optional)"
}
```

**Response** (201 Created):
```json
{
  "id": 4,
  "name": "New Workshop",
  "objective": "Workshop objective",
  "user_id": 1,
  "created_at": "2025-12-17T03:00:00.000000",
  "participant_count": 0,
  "session_count": 0
}
```

**Error Responses**:
- `400 Bad Request`: Missing workshop name
- `401 Unauthorized`: Not authenticated

---

### Get Workshop Details

Get detailed information about a specific workshop, including participants and sessions.

**Endpoint**: `GET /api/v1/workshops/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Workshop de Pintura",
  "objective": "Explorar emociones",
  "user_id": 1,
  "created_at": "2025-12-10T18:47:48.269648",
  "participant_count": 2,
  "session_count": 1,
  "participants": [
    {
      "id": 1,
      "name": "Juan Pérez",
      "workshop_id": 1,
      "created_at": "2025-12-10T18:47:48.269648",
      "extra_data": {}
    }
  ],
  "sessions": [
    {
      "id": 1,
      "workshop_id": 1,
      "prompt": "Dibuja tu emoción favorita",
      "motivation": "Conectar con emociones positivas",
      "materials": ["lápices", "papel"],
      "created_at": "2025-12-10T18:47:48.269648",
      "observation_count": 2
    }
  ]
}
```

**Error Responses**:
- `404 Not Found`: Workshop not found or access denied

---

### Update Workshop

Update workshop details.

**Endpoint**: `PATCH /api/v1/workshops/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "name": "Updated Workshop Name",
  "objective": "Updated objective"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Updated Workshop Name",
  "objective": "Updated objective",
  "user_id": 1,
  "created_at": "2025-12-10T18:47:48.269648",
  "participant_count": 2,
  "session_count": 1
}
```

**Error Responses**:
- `400 Bad Request`: No data provided
- `404 Not Found`: Workshop not found or access denied

---

### Delete Workshop

Delete a workshop and all associated data.

**Endpoint**: `DELETE /api/v1/workshops/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Workshop deleted successfully"
}
```

**Error Responses**:
- `404 Not Found`: Workshop not found or access denied

---

## Participants

### List Workshop Participants

Get all participants for a specific workshop.

**Endpoint**: `GET /api/v1/participants/workshop/{workshop_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Juan Pérez",
    "workshop_id": 1,
    "created_at": "2025-12-10T18:47:48.269648",
    "extra_data": {
      "age": 25,
      "notes": "First time participant"
    }
  }
]
```

**Error Responses**:
- `404 Not Found`: Workshop not found or access denied

---

### Create Participant

Add a new participant to a workshop.

**Endpoint**: `POST /api/v1/participants`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "workshop_id": 1,
  "name": "María García",
  "extra_data": {
    "age": 30,
    "notes": "Interested in painting"
  }
}
```

**Response** (201 Created):
```json
{
  "id": 2,
  "name": "María García",
  "workshop_id": 1,
  "created_at": "2025-12-17T03:00:00.000000",
  "extra_data": {
    "age": 30,
    "notes": "Interested in painting"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing workshop_id or name
- `404 Not Found`: Workshop not found or access denied

---

### Get Participant Details

Get information about a specific participant.

**Endpoint**: `GET /api/v1/participants/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "workshop_id": 1,
  "created_at": "2025-12-10T18:47:48.269648",
  "extra_data": {}
}
```

**Error Responses**:
- `404 Not Found`: Participant not found or access denied

---

### Update Participant

Update participant information.

**Endpoint**: `PATCH /api/v1/participants/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "name": "Juan Pérez Updated",
  "extra_data": {
    "age": 26,
    "notes": "Updated notes"
  }
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Juan Pérez Updated",
  "workshop_id": 1,
  "created_at": "2025-12-10T18:47:48.269648",
  "extra_data": {
    "age": 26,
    "notes": "Updated notes"
  }
}
```

**Error Responses**:
- `400 Bad Request`: No data provided
- `404 Not Found`: Participant not found or access denied

---

### Delete Participant

Remove a participant from a workshop.

**Endpoint**: `DELETE /api/v1/participants/{id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "message": "Participant deleted successfully"
}
```

**Error Responses**:
- `404 Not Found`: Participant not found or access denied

---

## Error Handling

All API endpoints return consistent error responses:

**Format**:
```json
{
  "error": "Error type",
  "message": "Detailed error message (optional)"
}
```

**Common HTTP Status Codes**:
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: JWT validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, there are no rate limits enforced. For production deployment, consider implementing rate limiting using Flask-Limiter.

---

## CORS

CORS is enabled for all `/api/v1/*` endpoints. Configure allowed origins in `.env`:

```bash
# Development (allow all)
CORS_ORIGINS=*

# Production (specific origins)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## Testing

See `.agent/docs/TESTING.md` for comprehensive API testing documentation.

**Quick Test**:
```bash
# Run all API tests
pytest tests/api/ -v

# Run with coverage
pytest tests/api/ --cov=app --cov-report=html
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Create workshop
WORKSHOP_ID=$(curl -s -X POST http://localhost:5000/api/v1/workshops \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"API Workshop","objective":"Testing API"}' \
  | jq -r '.id')

# 3. Add participant
PARTICIPANT_ID=$(curl -s -X POST http://localhost:5000/api/v1/participants \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"workshop_id\":$WORKSHOP_ID,\"name\":\"Test Participant\"}" \
  | jq -r '.id')

# 4. Get workshop details
curl -s http://localhost:5000/api/v1/workshops/$WORKSHOP_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Update participant
curl -s -X PATCH http://localhost:5000/api/v1/participants/$PARTICIPANT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"extra_data":{"age":25}}' | jq
```

---

## Future Endpoints

The following endpoints are planned for future releases:

- `GET /api/v1/sessions/workshop/{id}` - List workshop sessions
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions/{id}` - Get session details
- `PATCH /api/v1/sessions/{id}` - Update session
- `DELETE /api/v1/sessions/{id}` - Delete session
- `GET /api/v1/observations/session/{id}` - List session observations
- `POST /api/v1/observations` - Create observation
- `GET /api/v1/observations/{id}` - Get observation details
- `PATCH /api/v1/observations/{id}` - Update observation
- `DELETE /api/v1/observations/{id}` - Delete observation
