# Quick Reference

## Project Identity
- **Name**: Arteterapia
- **Type**: Flask Web Application
- **Purpose**: Art Therapy Workshop Management
- **Primary Language**: Spanish

## Technology Stack

```
Backend:  Flask 3.0 + SQLAlchemy + Flask-Migrate
Admin:    Flask-Admin (role-protected)
Auth:     Flask-Login (invitation-based)
Frontend: Bootstrap 5 + Vanilla JS
Database: SQLite (dev) / PostgreSQL/MySQL (prod)
Email:    Flask-Mail
```

## Core Models

### Application Models
1. **Workshop** - Workshops with objectives
2. **Participant** - Workshop participants
3. **Session** - Sessions with prompts, materials
4. **ObservationalRecord** - Observations (JSON storage, ~50 questions)
5. **ObservationQuestions** - Question structure (config file)

### Auth Models
6. **User** - System users with password auth
7. **Role** - User roles (Admin, Editor)
8. **UserInvitation** - Invitation tokens for registration

## Key Files

| File | Purpose |
|------|----------|
| `run.py` | Application entry point |
| `config.py` | Configuration (Dev/Prod) |
| `app/__init__.py` | Flask factory, blueprints, extensions |
| `app/models/observation_questions.py` | **CRITICAL**: Question structure (~50 questions) |
| `app/static/css/custom.css` | Minimalist design system |
| `setup_db.py` | Database initialization |
| `CHANGELOG.md` | **UPDATE REQUIRED**: Track all changes here |

## Topic Documentation

- **Backend**: `.agent/topics/backend.md` - Flask routes, services, models, Jinja2 templates
- **Frontend**: `.agent/topics/frontend.md` - Jinja2 templates (primary), SPA (secondary)
- **API**: `.agent/topics/api.md` - REST API endpoints and JWT authentication
- **Testing**: `.agent/topics/testing.md` - Test structure and coverage
- **Routes**: `.agent/topics/routes.md` - Complete route documentation

## Routes Map

**Note**: For comprehensive route documentation, see `.agent/topics/routes.md`

### Authentication Routes (No /auth prefix)
- `/login` - Login page (GET, POST)
- `/logout` - Logout (GET)
- `/register/<token>` - Registration via invitation (GET, POST)
- `/verify-email/<token>` - Email verification (GET)
- `/forgot-password` - Password reset request (GET, POST)
- `/reset-password/<token>` - Password reset (GET, POST)
- `/change-password` - Change password (GET, POST)

### Workshop Routes
- `/` - List workshops (GET)
- `/workshop/create` - Create workshop (POST)
- `/<workshop_id>` - Workshop detail (GET)
- `/<workshop_id>/objective` - Update objective (POST, JSON)
- `/<workshop_id>/delete` - Delete workshop (POST)

### Participant & Session Routes (AJAX/JSON)
- `/workshop/<workshop_id>/participant/create` - Create participant
- `/participant/<participant_id>/update` - Update participant
- `/participant/<participant_id>/delete` - Delete participant
- `/workshop/<workshop_id>/session/create` - Create session
- `/session/<session_id>/update` - Update session
- `/session/<session_id>/delete` - Delete session

### Observation Routes
- `/session/<session_id>/observe/<participant_id>` - Start observation
- `/observation/answer` - Process answer (POST, JSON)
- `/observation/complete` - Complete observation (POST, JSON)
- `/workshop/<workshop_id>/observations` - View observations

### Admin Only
- `/admin` - Flask-Admin panel

## Default Credentials

```
Username: admin
Password: admin123
```
**Change immediately after first login**

## Essential Commands

### Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# OR (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database with sample data
python setup_db.py --with-data

# Run application
python run.py
```

### Database
```bash
# Reset with sample data (venv activated)
python setup_db.py --reset --with-data

# OR without activating (Windows)
.\.venv\Scripts\python.exe setup_db.py --reset --with-data

# Create migration (venv activated)
flask --app run db migrate -m "Message"

# Apply migration (venv activated)
flask --app run db upgrade
```

### Top Flask CLI Commands

```bash
# Database management
flask --app run database stats
flask --app run database init --with-data
flask --app run database reset --yes

# User management
flask --app run users list
flask --app run users create
flask --app run users grant-role <username> admin

# Invitations
flask --app run invitations create --email user@example.com

# Admin utilities
flask --app run admin check-config
flask --app run admin generate-secret-key
```

### Testing
```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/models/          # Model tests
pytest tests/routes/          # Route tests
pytest tests/api/             # API tests

# Run with coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Test Coverage

### Model Tests (`tests/models/`)
- **142 test cases** covering all 7 models
- Tests: Creation, validation, relationships, cascade deletes, JSON fields, methods
- Files: `test_user.py`, `test_role.py`, `test_workshop.py`, `test_participant.py`, `test_session.py`, `test_observation.py`, `test_user_invitation.py`

### Route Tests (`tests/routes/`)
- Web interface routes (cookie-based auth)
- Files: `test_auth_routes.py`, `test_workshop_routes.py`, `test_participant_routes.py`, `test_session_routes.py`, `test_observation_routes.py`

### API Tests (`tests/api/`)
- REST API endpoints (JWT token auth)
- Files: `test_auth.py`, `test_workshops.py`, `test_participants.py`

## Observation System

### 8 Question Categories (~50 total)
1. **Ingreso al Espacio** (Entry) - 4 questions
2. **Motivación** (Motivation) - 3 questions
3. **Consigna** (Instruction) - 5 questions
4. **Desarrollo** (Development) - 5 subcategories with ~20 questions
5. **Cierre** (Closure) - 6 questions
6. **Grupo** (Group) - 5 questions
7. **Clima Grupal** (Group Climate) - 4 questions

### Answer Options
- Sí (Yes)
- No (No)
- No está seguro/a (Not sure)
- No aplica (Not applicable)

### Storage
Answers stored as JSON in `ObservationalRecord.answers`:
```json
{
  "entry_on_time": "yes",
  "entry_resistance": "no",
  "motivation_interest": "yes"
}
```

## Design Principles

**UI/UX:**
- Minimalist - Clean, uncluttered interface
- Semantic - Button hierarchy by importance, not action
- Brand Colors - Borders, shadows, accents (not fills)
- Responsive - Mobile-first with Bootstrap 5
- Accessible - Focus states, keyboard navigation

**Code:**
- Application Factory - Modular Flask app creation
- Blueprints - Organized routes by domain
- Role-Based Access - Admin vs Editor permissions
- SQLAlchemy ORM - Database abstraction

## Security Checklist

- [ ] `SECRET_KEY` is 64-character random hex
- [ ] `.env` never committed (in `.gitignore`)
- [ ] Default admin password changed
- [ ] All protected routes use `@login_required`
- [ ] Admin routes check `current_user.is_admin()`
- [ ] Passwords hashed with Werkzeug
- [ ] Email verification required
- [ ] Tokens expire (reset: 24h, invitations: 7d)

## Common Pitfalls

**Don't:**
- Modify question IDs in `observation_questions.py` if data exists
- Commit `.env`, `*.db`, `*.mo` files
- Run `--reset` in production without backup
- Hardcode action colors (use semantic hierarchy)
- Skip `@login_required` on protected routes

**Do:**
- Create migrations after model changes
- Stop Flask before database reset
- Follow minimalist design principles
- Always activate virtual environment

## Development Workflow

1. **Plan** - Identify required changes
2. **Models** - Update/create models if needed
3. **Migrate** - Create and apply migrations
4. **Routes** - Add/modify route handlers
5. **Templates** - Update Jinja2 templates
6. **Test** - Manual browser testing
7. **Changelog** - Add entry to `CHANGELOG.md` under `[Unreleased]`
8. **Commit** - Granular, descriptive commits

## Workflow Shortcuts

- `/setup-environment` - Environment setup
- `/modify-models` - Database model changes
- `/reset-database` - Database reset

## Virtual Environment (⚠️ CRITICAL - READ FIRST)

**MANDATORY: ALL Python commands and scripts MUST be executed within the virtual environment.**

### Why This Is Critical

- ✅ Ensures correct Python version and dependencies
- ✅ Prevents compatibility issues (e.g., `datetime.UTC` requires Python 3.11+)
- ✅ Avoids conflicts with system Python packages
- ✅ Maintains consistent development environment

### How to Run Commands

**Windows PowerShell:**
```bash
# Direct execution (RECOMMENDED)
.\.venv\Scripts\python.exe script.py
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe setup_db.py --reset

# OR activate first
.\.venv\Scripts\Activate.ps1
python script.py
```

**Unix/macOS:**
```bash
# Direct execution (RECOMMENDED)
.venv/bin/python script.py
.venv/bin/python -m pytest
.venv/bin/python setup_db.py --reset

# OR activate first
source .venv/bin/activate
python script.py
```

### Examples: Right vs Wrong

❌ **WRONG:**
```bash
python setup_db.py --reset
pytest
flask --app run database init
```

✅ **CORRECT:**
```bash
.\.venv\Scripts\python.exe setup_db.py --reset
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\Activate.ps1; flask --app run database init
```

### Common Commands with venv

```bash
# Database setup
.\.venv\Scripts\python.exe setup_db.py --reset --with-data

# Run tests
.\.venv\Scripts\python.exe -m pytest

# Run application
.\.venv\Scripts\python.exe run.py

# Flask CLI (activate first)
.\.venv\Scripts\Activate.ps1
flask --app run database stats
flask --app run users list
```

## Configuration Flags

- `ENABLE_LANGUAGE_SWITCH` - Show/hide language switcher
- `BABEL_DEFAULT_LOCALE` - Default language
- `MAIL_SUPPRESS_SEND` - Log emails to console

## Support Resources

- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Bootstrap 5: https://getbootstrap.com/
- Flask-Admin: https://flask-admin.readthedocs.io/

---

*For comprehensive information, see [GUIDE.md](GUIDE.md).*
