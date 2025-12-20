# Backend Development Guide

## Overview

The Arteterapia backend is built with **Flask 3.0** using the **application factory pattern**. It provides both server-rendered Jinja2 templates for the web interface and a RESTful API for programmatic access.

**Primary Interface**: Jinja2 templates with AJAX interactions  
**Secondary Interface**: REST API (JWT-based)

## Architecture

### Application Structure

```
app/
├── __init__.py              # Flask factory, extensions init
├── admin_views.py           # Flask-Admin customization
├── routes/                  # Blueprint handlers (web interface)
│   ├── auth.py             # Authentication routes
│   ├── workshop.py         # Workshop CRUD
│   ├── participant.py      # Participant CRUD (AJAX)
│   ├── session.py          # Session CRUD (AJAX)
│   └── observation.py      # Observation workflow
├── api/                     # REST API endpoints (JWT)
│   ├── auth.py             # JWT authentication
│   ├── workshops.py        # Workshop API
│   ├── participants.py     # Participant API
│   ├── sessions.py         # Session API
│   └── observations.py     # Observation API
├── services/                # Business logic layer
│   ├── auth_service.py
│   ├── workshop_service.py
│   ├── participant_service.py
│   ├── session_service.py
│   └── observation_service.py
├── models/                  # SQLAlchemy ORM models
│   ├── user.py
│   ├── role.py
│   ├── workshop.py
│   ├── participant.py
│   ├── session.py
│   ├── observation.py
│   └── observation_questions.py  # CRITICAL: Question structure
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── workshop/
│   └── observation/
├── static/                  # Static assets
│   ├── css/custom.css
│   └── js/app.js
└── utils/
    └── email_utils.py
```

### Layer Responsibilities

**Routes (Blueprints)**
- Handle HTTP requests/responses
- Validate input data
- Call service layer for business logic
- Render templates or return JSON

**Services**
- Business logic and validation
- Permission checks
- Database operations
- Return data or error messages

**Models**
- Database schema definition
- Relationships between entities
- Helper methods for data access

## Core Concepts

### 1. Application Factory Pattern

The app is created using the factory pattern in `app/__init__.py`:

```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes import auth_bp, workshop_bp, ...
    app.register_blueprint(auth_bp)
    app.register_blueprint(workshop_bp, url_prefix='/workshop')
    
    return app
```

### 2. Blueprints Organization

**Web Interface Blueprints** (Jinja2 templates):
- `auth_bp` - No prefix, handles `/login`, `/register`, etc.
- `workshop_bp` - Prefix `/workshop`
- `participant_bp` - Prefix `/workshop` (AJAX endpoints)
- `session_bp` - Prefix `/workshop` (AJAX endpoints)
- `observation_bp` - Prefix `/session` and `/observation`

**API Blueprints** (JSON responses):
- `auth_api_bp` - Prefix `/api/v1/auth`
- `workshops_api_bp` - Prefix `/api/v1/workshops`
- `participants_api_bp` - Prefix `/api/v1/participants`
- `sessions_api_bp` - Prefix `/api/v1/sessions`
- `observations_api_bp` - Prefix `/api/v1/observations`

### 3. Service Layer Pattern

Services encapsulate business logic and return tuples of `(data, error)`:

```python
# Example from ObservationService
@staticmethod
def initialize_observation(session_id, participant_id, user_id):
    # Validate context
    session_obj, participant, error = ObservationService.validate_observation_context(
        session_id, participant_id, user_id
    )
    
    if error:
        return None, error
    
    # Business logic here...
    
    return observation_data, None
```

**Benefits:**
- Reusable across routes and API endpoints
- Centralized permission checks
- Easier to test
- Consistent error handling

### 4. Database Operations

**Always use the service layer for complex operations:**

```python
# ❌ DON'T: Direct DB operations in routes
@workshop_bp.route('/create', methods=['POST'])
def create_workshop():
    workshop = Workshop(name=request.form['name'])
    db.session.add(workshop)
    db.session.commit()

# ✅ DO: Use service layer
@workshop_bp.route('/create', methods=['POST'])
def create_workshop():
    workshop, error = WorkshopService.create_workshop(
        name=request.form['name'],
        user_id=current_user.id
    )
    if error:
        flash(error, 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
```

### 5. AJAX Patterns

Many routes return JSON for AJAX interactions:

```python
@participant_bp.route('/workshop/<int:workshop_id>/participant/create', methods=['POST'])
@login_required
def create_participant(workshop_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'El nombre es obligatorio'
        }), 400
    
    # Create participant...
    
    return jsonify({
        'success': True,
        'message': 'Participante agregado',
        'participant': {
            'id': participant.id,
            'name': participant.name
        }
    })
```

## Key Features Implementation

### Observation System

The observation system is the core feature of the application:

**1. Pending Observations**
When a participant is created, pending observation records are automatically created for all existing sessions:

```python
# In participant.py create_participant()
participant = Participant(name=name, workshop_id=workshop_id)
db.session.add(participant)
db.session.flush()  # Get participant.id

# Create pending observations
sessions = Session.query.filter_by(workshop_id=workshop_id).all()
for session in sessions:
    observation = ObservationalRecord(
        session_id=session.id,
        participant_id=participant.id,
        answers={},  # Empty = pending
        version=1
    )
    db.session.add(observation)
```

**2. Observation Workflow**
- User clicks observation button for a participant-session combination
- System initializes observation (pre-fills if redo, empty if pending)
- User answers ~50 questions across 8 categories
- Answers stored in session during workflow
- On completion, answers saved to database

**3. Versioning**
- Each participant-session combination can have multiple observations
- Version number increments for redos
- Pending observations (empty answers) are updated, not versioned

### Authentication & Authorization

**Flask-Login** for session-based auth:

```python
@login_required
def protected_route():
    # current_user is available
    if not current_user.is_admin():
        flash('No tienes permiso', 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
```

**Permission Checks:**
- Admin users: Full access to all workshops
- Regular users: Only their own workshops
- Service layer validates permissions

### Email System

**Flask-Mail** for email notifications:

```python
from app.utils.email_utils import send_email

send_email(
    to=user.email,
    subject='Verificación de cuenta',
    template='auth/verify_email',
    user=user,
    token=token
)
```

## Development Workflow

### Adding a New Feature

1. **Plan the feature**
   - Identify required models, routes, templates
   - Determine if it needs API endpoints

2. **Update models** (if needed)
   ```bash
   # After modifying models
   flask --app run db migrate -m "Add new field"
   flask --app run db upgrade
   ```

3. **Create service methods**
   - Add business logic to appropriate service
   - Include permission checks
   - Return (data, error) tuples

4. **Add routes**
   - Web routes in `app/routes/`
   - API routes in `app/api/`
   - Use service layer for logic

5. **Create templates**
   - Extend `base.html`
   - Use Bootstrap 5 components
   - Add AJAX interactions if needed

6. **Test manually**
   - Run app: `python run.py`
   - Test all scenarios
   - Check error handling

### Common Patterns

**Creating a new route:**

```python
@workshop_bp.route('/<int:workshop_id>')
@login_required
def detail(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    
    # Permission check
    if not current_user.is_admin() and workshop.user_id != current_user.id:
        flash('No tienes permiso', 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
    
    return render_template('workshop/detail.html', workshop=workshop)
```

**AJAX endpoint:**

```python
@session_bp.route('/session/<int:session_id>/update', methods=['POST'])
@login_required
def update_session(session_id):
    session = Session.query.get_or_404(session_id)
    data = request.get_json()
    
    # Update logic...
    
    return jsonify({'success': True, 'message': 'Sesión actualizada'})
```

**Template rendering:**

```jinja2
{% extends "base.html" %}

{% block title %}{{ workshop.name }} - Arteterapia{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ workshop.name }}</h1>
    
    {% for participant in participants %}
    <div class="participant-item">
        {{ participant.name }}
    </div>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script>
    const workshopId = {{ workshop.id }};
    // AJAX interactions here
</script>
{% endblock %}
```

## Database Models

### Core Models

**Workshop**
- `name`: Workshop name
- `objective`: Workshop objective (optional)
- `user_id`: Owner (creator)
- Relationships: participants, sessions

**Participant**
- `name`: Participant name
- `workshop_id`: Foreign key to workshop
- `extra_data`: JSON field for custom data
- Relationships: observations

**Session**
- `prompt`: Session instruction/prompt
- `motivation`: Session motivation (optional)
- `materials`: JSON array of materials
- `workshop_id`: Foreign key to workshop
- Relationships: observations

**ObservationalRecord**
- `session_id`: Foreign key to session
- `participant_id`: Foreign key to participant
- `version`: Version number (1, 2, 3...)
- `answers`: JSON dict {question_id: answer}
- `freeform_notes`: Optional text notes
- `created_at`: Timestamp

### Model Methods

**Workshop:**
```python
@property
def participant_count(self):
    return len(self.participants)

@property
def session_count(self):
    return len(self.sessions)
```

**Session:**
```python
def has_observation_for(self, participant_id):
    return ObservationalRecord.has_observation(self.id, participant_id)

def get_observation_count_for(self, participant_id):
    return ObservationalRecord.query.filter_by(
        session_id=self.id,
        participant_id=participant_id
    ).count()
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/models/test_workshop.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

### Test Structure

```
tests/
├── conftest.py              # Fixtures
├── models/                  # Model tests
│   ├── test_user.py
│   ├── test_workshop.py
│   └── ...
├── routes/                  # Route tests (web interface)
│   ├── test_auth_routes.py
│   ├── test_workshop_routes.py
│   └── ...
└── api/                     # API tests (JWT)
    ├── test_auth.py
    ├── test_workshops.py
    └── ...
```

## Best Practices

### Security

1. **Always validate user input**
   ```python
   name = data.get('name', '').strip()
   if not name:
       return jsonify({'error': 'Name required'}), 400
   ```

2. **Check permissions in services**
   ```python
   if not user.is_admin() and workshop.user_id != user_id:
       return None, 'No tienes permiso'
   ```

3. **Use parameterized queries** (SQLAlchemy handles this)

4. **Hash passwords** (Werkzeug's generate_password_hash)

5. **Validate tokens** (itsdangerous for email verification)

### Performance

1. **Use eager loading for relationships**
   ```python
   workshops = Workshop.query.options(
       db.joinedload(Workshop.participants)
   ).all()
   ```

2. **Limit query results**
   ```python
   recent = Observation.query.order_by(
       Observation.created_at.desc()
   ).limit(10).all()
   ```

3. **Use database indexes** (defined in models)

### Code Organization

1. **Keep routes thin** - delegate to services
2. **Services return (data, error)** - consistent pattern
3. **Use type hints** where helpful
4. **Document complex logic** with comments
5. **Follow PEP 8** naming conventions

## Troubleshooting

### Common Issues

**Database locked (SQLite)**
- Stop all Flask instances
- Close DB browser tools
- Restart application

**Migration conflicts**
```bash
# Reset migrations (development only!)
rm -rf migrations/
flask --app run db init
flask --app run db migrate -m "Initial migration"
flask --app run db upgrade
```

**Import errors**
- Ensure virtual environment is activated
- Check circular imports
- Verify blueprint registration

**Template not found**
- Check template path matches route
- Verify template extends base.html
- Check for typos in template name

## Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://www.sqlalchemy.org/
- Jinja2 Documentation: https://jinja.palletsprojects.com/
- Flask-Login: https://flask-login.readthedocs.io/
- Flask-Admin: https://flask-admin.readthedocs.io/
