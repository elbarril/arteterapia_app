# Arteterapia Development Guide

Version: 2.0
Last Updated: December 2025
Project: Flask Web Application for Art Therapy Workshop Management

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Development Standards](#development-standards)
5. [Database and Models](#database-and-models)
6. [Authentication and Security](#authentication-and-security)
7. [Frontend Guidelines](#frontend-guidelines)
8. [Common Workflows](#common-workflows)

## Project Overview

### Purpose
Flask-based application for art therapists to manage workshops, sessions, participants, and therapeutic observations using a structured question-based approach (~50 questions across 8 categories).

### Key Features
- Workshop, participant, and session management
- Step-by-step therapeutic observation recording (JSON storage)
- Consolidated reporting and data visualization
- Role-based access (Admin/Editor) with invitation-based registration
- Flask-Admin interface for data management
- Minimalist, responsive UI design

### Target Users
- Art Therapists: Workshop and observation management
- Administrators: User management, system configuration

## Architecture

### Technology Stack

**Backend:**
- Flask 3.0 + SQLAlchemy 3.1.1 + Flask-Migrate 4.0.5
- Flask-Admin 1.6.1 + Flask-Login 0.6.3 + Flask-Mail 0.9.1

**Frontend:**
- Bootstrap 5 + Bootstrap-Flask 2.3.3
- Vanilla JavaScript + AJAX
- Jinja2 templating

**Database:**
- Development: SQLite
- Production: PostgreSQL/MySQL (SQLAlchemy compatible)

### Application Layers

```
┌─────────────────────────────────────┐
│  PRESENTATION (Templates + Static)  │
│  Bootstrap 5 + Vanilla JS           │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  ROUTES (Flask Blueprints)          │
│  auth, workshop, participant,       │
│  session, observation               │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  SERVICE (Flask-Login, Flask-Mail)  │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  MODEL (SQLAlchemy ORM)             │
│  User, Role, Workshop, Session,     │
│  Participant, ObservationalRecord   │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  DATA (SQLite/PostgreSQL/MySQL)     │
└─────────────────────────────────────┘
```

### Data Model Relationships

```
User ──┬─▶ Role (many-to-many via user_roles)
       └─▶ UserInvitation (one-to-many)

Workshop ──┬─▶ Session (one-to-many)
           └─▶ Participant (one-to-many)

Session + Participant ──▶ ObservationalRecord (many-to-one each)
```

## Project Structure

```
arteterapia_app/
├── app/
│   ├── __init__.py            # Flask factory, blueprint registration
│   ├── admin_views.py         # Flask-Admin customization
│   ├── routes/                # Blueprint handlers
│   │   ├── auth.py           
│   │   ├── observation.py    
│   │   ├── participant.py    
│   │   ├── session.py        
│   │   └── workshop.py       
│   ├── models/                # SQLAlchemy models
│   │   ├── observation.py     # ObservationalRecord (JSON storage)
│   │   ├── observation_questions.py  # CRITICAL: Question structure
│   │   ├── user.py            # User + auth methods
│   │   ├── role.py           
│   │   ├── workshop.py       
│   │   ├── session.py        
│   │   └── participant.py    
│   ├── static/
│   │   ├── css/custom.css     # Minimalist design system
│   │   └── js/app.js          # AJAX interactions
│   ├── templates/
│   │   ├── base.html          # Master template
│   │   ├── auth/             
│   │   ├── observation/      
│   │   └── workshop/         
│   └── utils/
│       └── email_utils.py     # Email sending
├── migrations/                # Alembic migrations
├── .env                       # Environment variables (gitignored)
├── config.py                  # Configuration classes
├── requirements.txt          
├── run.py                     # Application entry point
└── setup_db.py                # Database initialization
```

### Critical Files

| File | Purpose |
|------|---------|
| `run.py` | Application entry point |
| `config.py` | All configuration (Dev/Prod) |
| `app/__init__.py` | Factory pattern, extensions, blueprints |
| `app/models/observation_questions.py` | **CRITICAL**: Therapeutic question structure (~50 questions) |
| `app/static/css/custom.css` | Minimalist design system |
| `CHANGELOG.md` | **UPDATE REQUIRED**: Track all changes here |

## Development Standards

### Code Style
- Python: PEP 8 conventions
- Naming: Classes `PascalCase`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`
- Docstrings for all classes and non-trivial functions
- Comments explain "why", not "what"

### Flask Best Practices
1. Application factory pattern (already implemented)
2. Blueprints for modular routes (one per domain)
3. Environment-based configuration via `config.py`
4. Extension initialization: global init, then `init_app()` in factory
5. Database operations via `db.session`
6. Flash message categories: `success`, `info`, `warning`, `danger`

### Git Workflow
- Branch naming: `feature/name` or `fix/name`
- Granular, descriptive commits
- **ALWAYS** create new branch, **NEVER** commit directly to `master`
- Never commit: `.env`, `*.db`, `__pycache__`, `.venv`

### Command Execution (CRITICAL)
**ALWAYS** activate virtual environment before running Python commands:

Windows PowerShell:
```bash
.\.venv\Scripts\Activate.ps1; python script.py
# OR direct binary access
.\.venv\Scripts\python.exe script.py
```

Unix/macOS:
```bash
source .venv/bin/activate && python script.py
# OR direct binary access
.venv/bin/python script.py
```

### Error Handling
- Wrap database operations in try-except blocks
- Log errors appropriately  
- Use flash messages for user feedback
- Return meaningful HTTP status codes

## Database and Models

### Configuration
- Development: SQLite at `arteterapia.db` (gitignored)
- Connection: Via `DATABASE_URL` in `.env` or defaults to SQLite
- Migrations: Alembic via Flask-Migrate

### Core Models

**User**
- Authentication and authorization
- Methods: `set_password()`, `check_password()`, `is_admin()`
- Flask-Login integration (implements required methods)

**ObservationalRecord**
- Stores therapeutic observations with structured questions
- `answers` (JSON): All question responses as `{question_id: answer_value}`
- `notes` (Text): Freeform therapist notes
- Question IDs must match `observation_questions.py`

**Observation Questions Structure**
Located in `app/models/observation_questions.py`:

8 main categories (~50 total questions):
1. INGRESO AL ESPACIO (Entry) - 4 questions
2. MOTIVACIÓN (Motivation) - 3 questions
3. CONSIGNA (Instruction) - 5 questions
4. DESARROLLO (Development) - 5 subcategories with ~20 questions
5. CIERRE (Closure) - 6 questions
6. GRUPO (Group) - 5 questions
7. CLIMA GRUPAL (Group Climate) - 4 questions

Answer options: `yes`, `no`, `not_sure`, `not_applicable`

**WARNING**: Never change question IDs if observational data exists.

### Database Operations

**Create/Reset Database:**
```bash
# Initial setup with admin user only
python setup_db.py

# Setup with sample data (recommended for development)
python setup_db.py --with-data

# Reset database (WARNING: deletes all data)
python setup_db.py --reset --with-data
```

**Migrations:**
```bash
# Create migration after model changes
flask --app run db migrate -m "Description"

# Apply migrations
flask --app run db upgrade

# Rollback migration
flask --app run db downgrade
```

## Authentication and Security

### Authentication Flow

**Registration (Invitation-Based):**
1. Admin creates invitation via `/auth/create-invitation`
2. System generates token, sends email with registration link
3. User registers at `/auth/register/<token>`
4. System creates account, sends verification email
5. User verifies email, can now log in

**Login:**
1. User submits credentials at `/auth/login`
2. System verifies password hash
3. Flask-Login creates session
4. User redirected to workshop list

**Password Reset:**
1. User requests reset at `/auth/forgot-password`
2. System sends email with reset token
3. User sets new password at `/auth/reset-password/<token>`

### Security Best Practices

**CRITICAL: Always verify server-side**
- Never trust client-side checks
- Use `@login_required` on all protected routes
- Use `current_user.is_admin()` for admin-only features

**Password Security:**
- Hashing: Werkzeug's `generate_password_hash` (pbkdf2:sha256)
- Minimum length: 6 characters
- Never log password values

**Token Security:**
- Password reset: 24 hour expiry
- Email verification: 24 hour expiry
- Invitations: 7 day expiry
- Implementation: `itsdangerous.URLSafeTimedSerializer` with `SECRET_KEY`

**Environment Variables:**
```bash
# CRITICAL: Never commit .env file
SECRET_KEY=<64-character random hex>  # Generate: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=sqlite:///arteterapia.db
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=...
MAIL_PASSWORD=...  # Use app-specific passwords
```

### User Roles

**Admin:**
- Full access to all features
- Access to Flask-Admin panel (`/admin`)
- Can create user invitations

**Editor:**
- Manage workshops, participants, sessions, observations
- Cannot access Flask-Admin panel
- Cannot create user invitations

### Route Protection Example

```python
# Require login
@workshop_bp.route('/workshops')
@login_required
def list_workshops():
    # ...

# Require admin role
@auth_bp.route('/create-invitation')
@login_required
def create_invitation():
    if not current_user.is_admin():
        flash('No tienes permiso.', 'danger')
        return redirect(url_for('workshop_bp.list_workshops'))
    # ...
```

## Frontend Guidelines

### CSS Architecture

**Design System (`app/static/css/custom.css`):**
```css
:root {
    /* Brand colors - borders, icons, shadows */
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --accent-color: #3b82f6;
    --accent-shadow: rgba(37, 99, 235, 0.1);
    
    /* Neutral palette */
    --bg-light: #f8fafc;
    --border-light: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
}
```

**Design Principles:**
1. Semantic button hierarchy (not action-based)
2. Brand colors for borders, shadows, accents (not fills unless primary action)
3. Minimalist with generous whitespace
4. Subtle transitions for better UX

**Key Component Classes:**
- `.workshop-card`: Workshop cards with hover effects
- `.session-card`: Expandable session cards
- `.observation-card`: Observation interface
- `.answer-btn`: Answer buttons with visual feedback

### JavaScript Patterns

**AJAX Form Submission:**
```javascript
fetch('/workshop/1/update-objective', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({objective: newValue})
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Update UI
    } else {
        alert(data.error);
    }
});
```

**Dynamic Interactions:**
- Inline editing (workshop objectives)
- Session expansion (click to expand/collapse)
- Answer selection (visual feedback)

### Bootstrap 5 Guidelines
- Use utility classes: `mb-3`, `mt-4`, `d-flex`, `justify-content-between`
- Responsive breakpoints: `col-md-6`, `col-lg-4`
- Components: Cards, modals, badges, alerts, list groups
- **NEVER** use native `alert()`, `confirm()`, or `prompt()`
- Use `showModal` helper in `app.js` with Bootstrap modals

### Template Structure

All pages extend `base.html`:
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}
```

## Common Workflows

### Adding a New Feature

1. Plan: Identify models, routes, templates needed
2. Models: Update/create models in `app/models/`
3. Migration: `flask --app run db migrate -m "Add feature X"`
4. Apply: `flask --app run db upgrade`
5. Routes: Add routes to appropriate blueprint
6. Template: Create/update templates
7. Test: Manual testing in browser
8. Changelog: Add entry to `CHANGELOG.md` under `[Unreleased]` section
9. Commit: Granular commits with descriptive messages

### Modifying Observation Questions

Questions defined in `app/models/observation_questions.py`

To add/modify:
1. Edit `OBSERVATION_CATEGORIES` list
2. Existing observations continue to work (backward compatible)

**DO NOT** change question IDs if observations already exist.

### Changing UI Styles

1. Edit `app/static/css/custom.css`
2. Use CSS variables for brand colors
3. Maintain semantic button hierarchy
4. Test responsive behavior
5. Verify accessibility (focus states, contrast)

### Database Reset (Development)

```bash
# WARNING: Deletes all data
python setup_db.py --reset --with-data

# Restart Flask (Ctrl+C, then python run.py)
```

### Running the Application

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run development server
python run.py
```

Available at:
- Main app: `http://localhost:5000`
- Admin panel: `http://localhost:5000/admin`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`
- **Change immediately after first login**

### Common Issues

**Database Locked (SQLite):**
- Stop all Flask instances
- Close database browser tools
- Restart application

**404 on Routes:**
- Verify blueprint registered in `app/__init__.py`
- Check route definition matches URL
- Ensure `@login_required` applied if needed

**Flash Messages Not Appearing:**
- Check `base.html` includes flash message block
- Verify `flash()` called before `redirect()`
- Confirm correct category name

## Document Maintenance

**When to update:**
- Major architectural changes
- New models or significant model changes
- New authentication/security mechanisms
- Changes to development workflow
- Addition of new technologies

**How to update:**
1. Edit this file with clear, concise additions
2. Update "Last Updated" date at top
3. Ensure cross-references remain accurate
4. Commit: `docs: Update development guide - [description]`
