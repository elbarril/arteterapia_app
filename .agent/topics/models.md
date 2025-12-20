# Models Documentation

## Overview

The Arteterapia application uses SQLAlchemy ORM for database models. All models are located in `app/models/` and follow a consistent pattern for relationships, validation, and serialization.

## Core Principles

1. **Timezone-aware datetimes**: All datetime fields use `datetime.now(timezone.utc)`
2. **Cascade deletes**: Parent-child relationships use `cascade='all, delete-orphan'`
3. **JSON storage**: Complex data stored as JSON fields (answers, materials, extra_data)
4. **Token security**: URL-safe tokens with expiry for authentication flows
5. **Password hashing**: Werkzeug's `pbkdf2:sha256` for password security

## Model Reference

### User Model (`app/models/user.py`)

**Purpose**: Authentication and authorization

**Key Fields**:
- `username` (String, unique, indexed) - User login name
- `email` (String, unique, indexed) - User email address
- `password_hash` (String) - Hashed password (never store plaintext)
- `active` (Boolean, default=True) - Account active status
- `email_verified` (Boolean, default=False) - Email verification status
- `verification_token` (String, unique, nullable) - Email verification token
- `reset_token` (String, unique, nullable) - Password reset token
- `reset_token_expiry` (DateTime, nullable) - Reset token expiration
- `must_change_password` (Boolean, default=False) - Force password change flag

**Relationships**:
- `roles` (many-to-many via `user_roles` table) - User roles
- `invitations_created` (one-to-many) - Invitations created by this user
- `workshops` (one-to-many, cascade delete) - Workshops owned by user

**Key Methods**:

```python
# Password management
user.set_password(password)              # Hash and set password
user.check_password(password) -> bool    # Verify password

# Email verification
token = user.generate_verification_token()  # Generate unique token
user.verify_email()                         # Mark email as verified

# Password reset
token = user.generate_reset_token(expiry_hours=24)  # Generate reset token
user.verify_reset_token(token) -> bool              # Verify token validity
user.clear_reset_token()                            # Clear token after use

# Role management
user.has_role(role_name) -> bool         # Check if user has specific role
user.is_admin() -> bool                  # Check if user has admin role

# Serialization
user.to_dict() -> dict                   # Convert to dictionary (excludes passwords/tokens)
```

**Important Notes**:
- Passwords are NEVER stored in plaintext
- Tokens are URL-safe and cryptographically secure
- Reset tokens expire after 24 hours by default
- Verification tokens don't expire but are single-use
- `to_dict()` excludes sensitive fields (password_hash, tokens)

---

### Role Model (`app/models/role.py`)

**Purpose**: Role-based access control

**Key Fields**:
- `name` (String, unique, indexed) - Role name (e.g., 'admin', 'editor')
- `description` (String, nullable) - Role description

**Relationships**:
- `users` (many-to-many via `user_roles` table) - Users with this role

**Usage**:
```python
# Check role
admin_role = Role.query.filter_by(name='admin').first()
if user in admin_role.users.all():
    # User is admin
```

---

### Workshop Model (`app/models/workshop.py`)

**Purpose**: Central entity for art therapy workshops

**Key Fields**:
- `name` (String, required, indexed) - Workshop name
- `objective` (Text, nullable) - Workshop objective/description
- `user_id` (Integer, foreign key, required, indexed) - Owner user ID

**Relationships**:
- `owner` (many-to-one) - User who owns the workshop
- `participants` (one-to-many, cascade delete) - Workshop participants
- `sessions` (one-to-many, cascade delete) - Workshop sessions

**Computed Properties**:
```python
workshop.participant_count -> int  # Number of participants
workshop.session_count -> int      # Number of sessions
workshop.has_observations -> bool  # Whether workshop has any observations
```

**Key Methods**:
```python
workshop.to_dict(include_relations=False) -> dict
# include_relations=True includes participants and sessions arrays
```

**Important Notes**:
- Deleting a workshop cascades to all participants and sessions
- Participants and sessions are deleted when workshop is deleted
- Use `include_relations=True` carefully (can be expensive for large workshops)

---

### Participant Model (`app/models/participant.py`)

**Purpose**: People who attend workshops

**Key Fields**:
- `name` (String, required) - Participant name
- `workshop_id` (Integer, foreign key, required) - Associated workshop
- `extra_data` (JSON, nullable) - Flexible field for additional data

**Relationships**:
- `workshop` (many-to-one) - Associated workshop
- `observations` (one-to-many, cascade delete) - Observational records

**Key Methods**:
```python
participant.to_dict() -> dict
# extra_data defaults to {} if None
```

**Extra Data Usage**:
```python
# Store flexible data
participant.extra_data = {
    'age': 25,
    'contact': 'email@example.com',
    'notes': 'Special considerations'
}
```

**Important Notes**:
- `extra_data` is stored as JSON in database
- Deleting participant cascades to all observations
- `to_dict()` returns empty dict for `extra_data` if None

---

### Session Model (`app/models/session.py`)

**Purpose**: Therapeutic sessions within workshops

**Key Fields**:
- `workshop_id` (Integer, foreign key, required) - Associated workshop
- `prompt` (Text, required) - Session prompt/instruction
- `motivation` (Text, nullable) - Session motivation
- `materials` (JSON, nullable) - Array of material names

**Relationships**:
- `workshop` (many-to-one) - Associated workshop
- `observations` (one-to-many, cascade delete) - Observational records

**Computed Properties**:
```python
session.has_observations -> bool      # Whether session has any observations
session.observation_count -> int      # Total number of observations
```

**Key Methods**:
```python
session.has_observation_for(participant_id) -> bool
# Check if observation exists for specific participant

session.get_observation_count_for(participant_id) -> int
# Get number of observation versions for participant

session.to_dict() -> dict
# materials defaults to [] if None
```

**Materials Usage**:
```python
session.materials = ['paint', 'brushes', 'canvas', 'paper']
```

**Important Notes**:
- Materials stored as JSON array
- Deleting session cascades to all observations
- Multiple observations can exist per participant (versioning)

---

### ObservationalRecord Model (`app/models/observation.py`)

**Purpose**: Therapeutic observations with structured questions

**Key Fields**:
- `session_id` (Integer, foreign key, required) - Associated session
- `participant_id` (Integer, foreign key, required) - Associated participant
- `version` (Integer, default=1) - Version number for tracking history
- `answers` (JSON, required, default=dict) - Question ID → answer mappings
- `freeform_notes` (Text, nullable) - Additional therapist notes

**Relationships**:
- `session` (many-to-one) - Associated session
- `participant` (many-to-one) - Associated participant

**Key Methods**:
```python
observation.get_answer(question_id) -> str | None
# Get answer for specific question

# Static methods
ObservationalRecord.get_latest_version(session_id, participant_id) -> int
# Returns 0 if no observations exist

ObservationalRecord.has_observation(session_id, participant_id) -> bool
# Check if observation exists
```

**Answers Structure**:
```python
observation.answers = {
    'entry_on_time': 'yes',
    'entry_resistance': 'no',
    'motivation_interest': 'yes',
    'development_focus': 'not_sure',
    'closure_satisfaction': 'not_applicable'
}
```

**Answer Options**:
- `'yes'` - Affirmative
- `'no'` - Negative
- `'not_sure'` - Uncertain
- `'not_applicable'` - Not applicable

**Versioning System**:
```python
# Multiple observations for same participant-session
obs1 = ObservationalRecord(session_id=1, participant_id=1, version=1, ...)
obs2 = ObservationalRecord(session_id=1, participant_id=1, version=2, ...)

# Get latest version
latest = ObservationalRecord.get_latest_version(session_id=1, participant_id=1)
# Returns 2
```

**Important Notes**:
- Answers stored as JSON dictionary
- Question IDs must match `observation_questions.py`
- Versioning allows tracking observation changes over time
- Each participant can have multiple observation versions per session

---

### UserInvitation Model (`app/models/user_invitation.py`)

**Purpose**: Invitation-based user registration

**Key Fields**:
- `email` (String, required, indexed) - Invitee email
- `token` (String, unique, required, indexed) - Auto-generated secure token
- `created_by_user_id` (Integer, foreign key, required) - Creator user ID
- `created_at` (DateTime, auto) - Creation timestamp
- `expires_at` (DateTime, required) - Expiration timestamp
- `used_at` (DateTime, nullable) - When invitation was used

**Relationships**:
- `creator` (many-to-one) - User who created the invitation

**Key Methods**:
```python
# Initialization auto-generates token and expiry
invitation = UserInvitation(
    email='user@example.com',
    created_by_user_id=admin_user.id,
    expiry_days=7  # Optional, defaults to 7
)

invitation.is_valid() -> bool      # Check if valid (not used, not expired)
invitation.mark_as_used()          # Mark as used (sets used_at)
```

**Status Property**:
```python
invitation.status -> str
# Returns: 'pending', 'used', or 'expired'
```

**Important Notes**:
- Token is auto-generated (URL-safe, 32 bytes)
- Default expiry is 7 days
- Tokens are single-use
- Status is computed from `used_at` and `expires_at`

---

## Common Patterns

### Creating Related Objects

```python
# Create workshop with participants and sessions
workshop = Workshop(name='Art Therapy 101', user_id=user.id)
db.session.add(workshop)
db.session.commit()

participant = Participant(name='John Doe', workshop_id=workshop.id)
session = Session(workshop_id=workshop.id, prompt='Draw your feelings')
db.session.add_all([participant, session])
db.session.commit()

# Create observation
observation = ObservationalRecord(
    session_id=session.id,
    participant_id=participant.id,
    answers={'entry_on_time': 'yes'},
    version=1
)
db.session.add(observation)
db.session.commit()
```

### Cascade Deletes

```python
# Deleting workshop deletes all related data
db.session.delete(workshop)
db.session.commit()
# Automatically deletes:
# - All participants in workshop
# - All sessions in workshop
# - All observations in those sessions
```

### Querying with Relationships

```python
# Get all workshops for a user
user.workshops.all()

# Get all participants in a workshop
workshop.participants.all()

# Get all observations for a session
session.observations.all()

# Filter observations by participant
session.observations.filter_by(participant_id=participant.id).all()
```

### JSON Field Usage

```python
# Participant extra_data
participant.extra_data = {'age': 30, 'notes': 'Left-handed'}
db.session.commit()

# Session materials
session.materials = ['paint', 'canvas', 'brushes']
db.session.commit()

# Observation answers
observation.answers = {
    'entry_on_time': 'yes',
    'motivation_interest': 'yes'
}
db.session.commit()
```

## Database Migrations

When modifying models:

```bash
# Create migration
flask --app run db migrate -m "Description of changes"

# Review migration file in migrations/versions/

# Apply migration
flask --app run db upgrade

# Rollback if needed
flask --app run db downgrade
```

## Testing Models

Model tests are located in `tests/models/`. See [Testing Documentation](testing.md) for details.

```bash
# Run all model tests
pytest tests/models/

# Run specific model tests
pytest tests/models/test_user.py
pytest tests/models/test_workshop.py
```

## Best Practices

1. **Always use timezone-aware datetimes**: `datetime.now(timezone.utc)`
2. **Commit after modifications**: Don't forget `db.session.commit()`
3. **Handle cascade deletes carefully**: Understand what gets deleted
4. **Validate before saving**: Check required fields and constraints
5. **Use transactions for complex operations**: Wrap in try-except with rollback
6. **Don't modify question IDs**: If observations exist, changing question IDs breaks data
7. **Test model changes**: Update model tests when modifying models

## Common Pitfalls

❌ **Don't**:
- Store passwords in plaintext
- Modify question IDs in `observation_questions.py` if data exists
- Forget to commit after modifications
- Use naive datetimes (without timezone)
- Delete parent objects without understanding cascade effects

✅ **Do**:
- Use `set_password()` for password hashing
- Use `to_dict()` for API responses
- Handle timezone awareness when comparing datetimes
- Test cascade deletes before using in production
- Validate foreign key relationships

## Related Documentation

- [Testing Guide](testing.md) - Model testing patterns
- [API Documentation](api.md) - API endpoints using models
- [Development Guide](../GUIDE.md) - General development patterns
